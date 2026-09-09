"""Read-only, offline study comparison. Hash consistency is not authentication.

Catalog source references are bundle-relative file names plus JSON pointers. They
are evidence locators, never URLs. No source files are created or repaired here.
"""
from __future__ import annotations

import copy
import html
import json
import re
from collections import Counter
from pathlib import Path

from . import __version__
from .artifacts import read_journal
from .contracts import canonical_bytes, digest, parse_json, read_json
from .llama_adapter import BACKEND_COMMIT, BACKEND_PATCH_SHA256, normalize_response
from .session import Session
from .study_report import evaluate_inventory
from .native_evidence import native_evidence as _native_evidence, NativeEvidenceError


class WorkbenchError(ValueError):
    """A source cannot enter the comparison catalog without explicit reconciliation."""


def _label(path: Path) -> str:
    return re.sub(r'[^A-Za-z0-9_. -]', '_', path.name).strip(' .')[:80] or 'study'


def _disambiguate_labels(studies: list[dict]) -> None:
    """Retain neutral basenames while making same-named sources selectable."""
    counts = Counter(study['label'] for study in studies)
    occupied = {study['label'] for study in studies if counts[study['label']] == 1}
    for study in studies:
        if counts[study['label']] > 1:
            base = f"{study['label']} [{study['id']}]"
            label = base
            suffix = 2
            while label in occupied:
                label = f'{base} ({suffix})'
                suffix += 1
            study['label'] = label
            occupied.add(label)


def _ref(document: str, pointer: str = '') -> dict:
    return {'document': document, 'pointer': pointer}


def _unavailable(reason: str) -> dict:
    return {'status': 'UNAVAILABLE', 'value': None, 'reason': reason}


def _identity(config: dict) -> dict:
    # Deliberately strict: future fields also separate groups until reviewed.
    return {key: copy.deepcopy(value) for key, value in config.items()
            if key not in ('study_id', 'clock')}




def _suppress_ratios(result: dict) -> None:
    """Do not let healthy subgroups advertise ratios from an ineligible campaign."""
    for group in result['concurrency_groups'].values():
        if not result['eligible'] or not group['eligible']:
            group['throughput_ratio_median'] = None
            group['throughput_ratio_range'] = None
            if 'full_wall_efficiency_ratio_median' in group:
                group['full_wall_efficiency_ratio_median'] = None
                group['full_wall_efficiency_ratio_range'] = None
            for pair in group['pairs']:
                pair['throughput_candidate_over_baseline'] = None
                if 'full_wall_efficiency_candidate_over_baseline' in pair:
                    pair['full_wall_efficiency_candidate_over_baseline'] = None
                for metric in ('end_to_end_tail_candidate_over_baseline', 'ttft_tail_candidate_over_baseline'):
                    pair[metric] = {key: None for key in pair[metric]}


def build_catalog(studies: list[Path]) -> dict:
    """Validate all sources atomically; reject duplicates and unreconciled evidence.

    Finalized means every recorded reservation has a reconciled terminal artifact,
    not that every cell in the planned comparison was executed. A copy of the same
    source session is rejected even under another basename. Independent sessions
    with identical configurations are retained separately, without pooled ratios.
    """
    if type(studies) is not list or not studies:
        raise WorkbenchError('provide at least one finalized study directory')
    catalog = {'schema_version': 1, 'workbench_version': __version__, 'studies': [],
               'compatibility_groups': [], 'cross_study_ratios': None,
               'scope': 'Read-only local evidence comparison; no pooled or cross-study speed claim.',
               'integrity_limit': 'Hashes establish internal consistency, not authentication, independent execution, or proof that no evidence was omitted.',
               'unavailable': {'energy': _unavailable('no energy probe'),
                               'engine_latency': _unavailable('client receipts do not establish engine execution or token emission times')}}
    seen_sessions, seen_paths = set(), set()
    groups = {}
    for number, supplied in enumerate(studies, 1):
        root = Path(supplied)
        label = _label(root)
        if root.resolve() in seen_paths:
            raise WorkbenchError(f'duplicate study input: {label}')
        seen_paths.add(root.resolve())
        try:
            with Session.open(root) as session:
                inventory = session.inspect()
                if not inventory['inventory_complete']:
                    raise WorkbenchError('finalized, reconciled terminal inventory required')
                if inventory['session_id'] in seen_sessions:
                    raise WorkbenchError('duplicate source session (including copied or relabelled bundles)')
                seen_sessions.add(inventory['session_id'])
                result = evaluate_inventory(inventory, study_root=root)
                _suppress_ratios(result)
                config = inventory['config']
                identity = _identity(config)
                compatibility = digest(identity)
                study_key = f'study-{number}'
                groups.setdefault(compatibility, []).append(study_key)
                expected = inventory['workload']['requests']
                source_attempts = {a['attempt_id']: a for a in inventory['attempts']}
                attempts = []
                input_identities = {}
                for summary_index, summary in enumerate(result['attempts']):
                    attempt = source_attempts[summary['attempt_id']]
                    native = _native_evidence(root, inventory, attempt)
                    for identifier, observation in native.items():
                        token_identity = digest(observation['input_token_ids'])
                        identity_key = (attempt['arm'], identifier) if config['schema_version'] == 3 and not config['evaluation']['output_token_parity'] else identifier
                        if identity_key in input_identities and input_identities[identity_key] != token_identity:
                            raise WorkbenchError('actual tokenizer input IDs drifted between attempts')
                        input_identities[identity_key] = token_identity
                    records = {row['request_id']: (i, row) for i, row in enumerate(attempt['requests'])}
                    peers = [a for a in inventory['attempts'] if a['concurrency'] == attempt['concurrency'] and
                             a['pair_index'] == attempt['pair_index'] and a['arm'] != attempt['arm']]
                    unambiguous = len(peers) == 1 and sum(a['concurrency'] == attempt['concurrency'] and
                        a['pair_index'] == attempt['pair_index'] and a['arm'] == attempt['arm']
                        for a in inventory['attempts']) == 1
                    peer_records = {r['request_id']: r for r in peers[0]['requests']} if unambiguous else {}
                    requests = []
                    for expected_index, prompt in enumerate(expected):
                        identifier = prompt['request_id']
                        entry = records.get(identifier)
                        request = entry[1] if entry else None
                        peer = peer_records.get(identifier)
                        parity = {'status': 'UNAVAILABLE', 'output_token_ids_equal': None,
                                  'generated_tokens_equal': None, 'output_text_equal': None,
                                  'prompt_token_count_equal': None}
                        if request is not None and peer is not None:
                            for output, field in (('output_token_ids_equal', 'output_token_ids'),
                                ('generated_tokens_equal', 'generated_tokens'), ('output_text_equal', 'output_text'),
                                ('prompt_token_count_equal', 'prompt_tokens')):
                                parity[output] = request[field] == peer[field]
                            parity['status'] = 'PASS' if all(parity[k] for k in (
                                'output_token_ids_equal', 'generated_tokens_equal', 'prompt_token_count_equal')) else 'FAIL'
                            parity['peer_source'] = _ref(f"attempts/{peers[0]['attempt_id']}.json",
                                f"/requests/{next(i for i, r in enumerate(peers[0]['requests']) if r['request_id'] == identifier)}")
                        elif unambiguous:
                            parity['status'] = 'MISSING'
                        evidence = native.get(identifier, {'input_token_ids': None,
                            'cache': _unavailable('no supported, reconciled native response evidence')})
                        requests.append({'request_id': identifier, 'stratum': prompt['stratum'],
                            'expected_answer': prompt['expected'], 'expected_source': _ref('workload.json', f'/requests/{expected_index}/expected'),
                            'observed': request is not None, 'status': request['status'] if request else 'MISSING',
                            'quality_correct': bool(request and request['status'] == 'SUCCEEDED' and request['output_text'].strip() == prompt['expected']),
                            'source': _ref(f"attempts/{attempt['attempt_id']}.json", f'/requests/{entry[0]}') if entry else None,
                            'normalized': copy.deepcopy(request), 'native': evidence, 'parity': parity})
                    attempts.append({'metrics': {key: copy.deepcopy(value) for key, value in summary.items() if key != 'environment'},
                        'metrics_source': _ref('evaluate_inventory', f'/attempts/{summary_index}'), 'requests': requests})
                # Operational free-text setup details can contain local paths; only
                # typed cost fields enter this portable catalog. Raw output stays exact.
                accounting = copy.deepcopy(result['accounting'])
                for key in ('setup_acquisition_build_costs',):
                    if isinstance(accounting.get(key), dict):
                        for record in accounting[key].get('records', []):
                            record.pop('details', None)
                for record in accounting.get('prior_runtime_protocol_failures', []):
                    record.pop('details', None)
                # Recheck after native replay to refuse concurrent out-of-band mutation.
                if canonical_bytes(session.inspect()) != canonical_bytes(inventory):
                    raise WorkbenchError('source changed during catalog construction')
                catalog['studies'].append({'id': study_key, 'label': label, 'session_id': inventory['session_id'],
                    'config_sha256': inventory['config_sha256'], 'workload_sha256': inventory['workload_sha256'],
                    'compatibility_key': compatibility, 'identity': identity,
                    'workload_family': inventory['workload'].get('family', inventory['workload']['workload_id']),
                    'evidence_class': result['evidence_class'], 'finding': result['finding'],
                    'eligible': result['eligible'], 'measured_claim_eligible': result['measured_claim_eligible'],
                    'ineligibility_reasons': result['ineligibility_reasons'],
                    'inventory_integrity': result['inventory_integrity'], 'finalized_inventory': True,
                    'accounting': accounting, 'accounting_source': _ref('evaluate_inventory', '/accounting'),
                    'quality': {'correct': sum(a['metrics']['quality_correct'] for a in attempts),
                                'denominator': sum(a['metrics']['quality_denominator'] for a in attempts),
                                'failed_attempts': sum(not a['metrics']['quality_pass'] for a in attempts)},
                    'concurrency_groups': result['concurrency_groups'], 'attempts': attempts,
                    'limitations': result['limitations']})
        except (ValueError, OSError, KeyError, TypeError, IndexError) as exc:
            # Do not expose private source locations through exception strings.
            if isinstance(exc, (WorkbenchError, NativeEvidenceError)):
                raise WorkbenchError(f'{label}: {exc}') from exc
            raise WorkbenchError(f'{label}: source validation failed ({type(exc).__name__}); inspect the source locally') from exc
    _disambiguate_labels(catalog['studies'])
    catalog['compatibility_groups'] = [{'key': key, 'study_ids': ids,
        'scope': 'Identical frozen identities except study label and clock; grouping does not authorize pooled comparisons.'}
        for key, ids in groups.items()]
    catalog['summary'] = {'study_count': len(catalog['studies']),
        'eligible_studies': sum(s['eligible'] for s in catalog['studies']),
        'measured_claim_eligible_studies': sum(s['measured_claim_eligible'] for s in catalog['studies']),
        'compatibility_group_count': len(groups),
        'finding': 'Independent studies; inspect eligibility and quality before interpreting within-study observations.'}
    return catalog


def _e(value) -> str:
    return html.escape(str(value), quote=True)


def _json(value) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def _seconds(value) -> str:
    return 'Unavailable' if value is None else f'{value / 1e9:.6f} s'


def _td(value) -> str:
    status = value in ('SUCCEEDED', 'COMPLETED', 'FAILED', 'INTERRUPTED', 'CANCELLED', 'MISSING')
    return ('<td class="status-cell">' if status else '<td>') + _e(value) + '</td>'


def _table(headers: list[str], rows: list[str], caption: str) -> str:
    return ('<div class="table-scroll" tabindex="0" role="region" aria-label="' + _e(caption) + '"><table>'
        '<caption>' + _e(caption) + '</caption><thead><tr>' + ''.join('<th scope="col">' + _e(h) + '</th>' for h in headers) +
        '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>')


def _cost_details(study: dict) -> str:
    accounting = study['accounting']
    full = accounting['full_cost_accounting']
    setup = accounting['setup_acquisition_build_costs']
    records = setup.get('records', [])
    adverse = sum(record['status'] != 'COMPLETED' for record in records)
    facts = [('Registered full wall', full.get('registered_full_wall_ns')),
             ('Attributed setup and attempts', full.get('attributed_setup_and_attempt_ns')),
             ('Coordinator or idle wall', full.get('unattributed_coordinator_or_idle_ns')),
             ('All retained attempt envelopes', accounting['full_wall_ns'])]
    rows = ['<tr>' + ''.join(_td(value) for value in (
        record['phase'], record['status'], _seconds(record['finished_ns'] - record['started_ns']),
        'Unavailable' if record['bytes_acquired'] is None else record['bytes_acquired'])) + '</tr>' for record in records]
    ancestor_html=''
    for ancestor in accounting.get('historical_preparation_ancestors', []):
        ancestor_html += '<p>Earlier preparation: '+_seconds(ancestor['attributed_setup_ns'])+' across '+str(ancestor['phase_count'])+' phases, including '+str(ancestor['failed_phases'])+' failed and '+str(ancestor['interrupted_phases'])+' interrupted. '+_e(ancestor['scope'])+'</p>'
    return ('<details class="cost-details"><summary>Cost breakdown and setup history (' + str(adverse) +
        ' adverse phases)</summary><dl>' + ''.join('<dt>' + _e(label) + '</dt><dd>' + _seconds(value) + '</dd>'
        for label, value in facts) + '</dl><p>These are overlapping views of one ledger; do not add the totals. '
        'Setup history includes failed phases and inherited predecessor costs.</p>' + ancestor_html +
        (_table(['Phase', 'Status', 'Wall', 'Bytes acquired'], rows, study['label'] + ' · retained setup history')
         if rows else '<p>Setup history is unavailable.</p>') + '</details>')


def _request_details(request: dict, metric: dict, metric_source: dict) -> str:
    normalized = request['normalized']
    parity = request['parity']
    cache = request['native']['cache']
    comparison = lambda key: 'Unavailable' if parity[key] is None else ('Match' if parity[key] else 'Mismatch')
    values = [('Expected answer', request['expected_answer']),
              ('Observed text', normalized['output_text'] if normalized else 'Missing observation'),
              ('Output token IDs', _json(normalized['output_token_ids']) if normalized else 'Unavailable'),
              ('Generated token count', normalized['generated_tokens'] if normalized and normalized['generated_tokens'] is not None else 'Unavailable'),
              ('Prompt token count', normalized['prompt_tokens'] if normalized else 'Unavailable'),
              ('Paired output token IDs', comparison('output_token_ids_equal')),
              ('Paired generated counts', comparison('generated_tokens_equal')),
              ('Paired text', comparison('output_text_equal')),
              ('Paired prompt counts', comparison('prompt_token_count_equal')),
              ('Reused input tokens', cache['reused_input_tokens'] if cache['status'] == 'RECONCILED_NATIVE' else 'Unavailable'),
              ('New input tokens', cache['new_input_tokens'] if cache['status'] == 'RECONCILED_NATIVE' else 'Unavailable')]
    intervention = request['native'].get('prompt_intervention')
    if intervention:
        values.extend([('Context decision', intervention['result']['decision']),
            ('Observed context analysis', _seconds(intervention['duration_ns'])),
            ('Transformed prompt sent for tokenization', intervention['result']['prompt']),
            ('Certificate scope', intervention['result']['certificate']['scope'])])
        prediction=intervention['result'].get('controller_prediction')
        if prediction:
            values.extend([('Acceptance controller decision',prediction['decision']),
                ('Decision reason',prediction['reason']),('Prompt graph features',_json(prediction['features'])),
                ('Population-risk guarantee','None; empirical development/calibration only')])
    detail = {'request_evidence': request, 'attempt_id': metric['attempt_id'], 'attempt_metric_source': metric_source}
    return ('<details class="request-details"><summary>Evidence for ' + _e(request['request_id']) +
            '</summary><dl>' + ''.join('<dt>' + _e(label) + '</dt><dd>' + _e(value) + '</dd>' for label, value in values) +
            '</dl><details><summary>Normalized record and source references</summary><pre tabindex="0">' +
            _e(_json(detail)) + '</pre></details></details>')


def _latency_qualified_summary(study: dict) -> str:
    totals = {'baseline': [0, 0], 'candidate': [0, 0]}
    seen = set()
    for attempt in study['attempts']:
        metric = attempt['metrics']
        serving = metric.get('serving') or {}
        if not {'slo_qualified_requests', 'offered_requests'} <= serving.keys():
            return 'Unavailable in this study format'
        arm = metric['arm']
        seen.add(arm)
        totals[arm][0] += serving['slo_qualified_requests']
        totals[arm][1] += serving['offered_requests']
    return ' · '.join(f"{arm.title()}: {totals[arm][0]} / {totals[arm][1]}" if arm in seen
                      else f'{arm.title()}: no retained attempts'
                      for arm in ('baseline', 'candidate'))


def render_workbench(catalog: dict) -> str:
    """Render a build_catalog result. All external text is escaped, including JSON."""
    catalog = copy.deepcopy(catalog)
    studies = catalog['studies']
    _disambiguate_labels(studies)
    options = {'study': [(s['id'], s['label']) for s in studies],
        'family': [(family, family) for family in sorted({s['workload_family'] for s in studies})],
        'concurrency': [(str(c), str(c)) for c in sorted({a['metrics']['concurrency'] for s in studies for a in s['attempts']})],
        'pair': [(str(p), str(p + 1)) for p in sorted({a['metrics']['pair_index'] for s in studies for a in s['attempts']})],
        'arm': [('baseline', 'Baseline'), ('candidate', 'Candidate')],
        'quality': [('fail', 'Incorrect / missing'), ('pass', 'Correct requests')],
        'parity': [('FAIL', 'Token parity mismatch'), ('PASS', 'Token parity matches'), ('MISSING', 'Missing paired observation'), ('UNAVAILABLE', 'Unavailable / ambiguous pair')]}
    controls = ''.join('<label for="filter-' + key + '">' + label + '<select disabled id="filter-' + key + '" data-filter="' + key + '"><option value="">All</option>' +
        ''.join('<option value="' + _e(value) + '">' + _e(text) + '</option>' for value, text in options[key]) + '</select></label>'
        for key, label in (('study', 'Study'), ('family', 'Workload family'), ('concurrency', 'Concurrency'), ('pair', 'Pair'), ('arm', 'Arm'), ('quality', 'Request quality'), ('parity', 'Paired token evidence')))
    summaries, attempt_rows, request_rows, pair_rows = [], [], [], []
    for study in studies:
        sid = study['id']
        accounting = study['accounting']
        full = accounting['full_cost_accounting']
        evaluation = study['identity']['evaluation']
        targets = (_seconds(evaluation['ttft_slo_ns']) + ' TTFT · ' +
                   _seconds(evaluation['end_to_end_slo_ns']) + ' completion'
                   if {'ttft_slo_ns', 'end_to_end_slo_ns'} <= evaluation.keys() else 'Unavailable')
        from .report import render_task_families
        family_details=render_task_families([a['metrics'] for a in study['attempts']])
        summaries.append('<article><h3>' + _e(study['label']) + '</h3><p class="badge">' + _e(study['evidence_class']) + '</p><p><strong>' +
            _e(study['finding']) + '</strong></p><dl><dt>Model</dt><dd>' + _e(study['identity']['model']['repository']) + '</dd><dt>Workload</dt><dd>' +
            _e(study['workload_family']) + '</dd><dt>Correct / expected across retained attempts</dt><dd>' + _e(f"{study['quality']['correct']} / {study['quality']['denominator']}") +
            '</dd><dt>Correct and within both latency targets / offered</dt><dd>' + _e(_latency_qualified_summary(study)) +
            '</dd><dt>Frozen latency targets</dt><dd>' + _e(targets) +
            '</dd><dt>Retained attempts</dt><dd>' + _e(accounting['attempt_count']) +
            '</dd><dt>Observed / missing requests</dt><dd>' + _e(f"{accounting['observed_requests']} / {accounting['missing_requests']}") + '</dd><dt>Registered full wall</dt><dd>' +
            _seconds(full.get('registered_full_wall_ns')) + '</dd><dt>Measured claim eligible</dt><dd>' + ('Yes' if study['measured_claim_eligible'] else 'No') + '</dd></dl><p>' +
            _e('; '.join(study['ineligibility_reasons']) or 'No campaign eligibility failures. Fixture data remains non-measured.') + '</p>' + _cost_details(study) + family_details + '<details><summary>Frozen identity and cost source references</summary><pre tabindex="0">' +
            _e(_json({key: study[key] for key in ('config_sha256', 'workload_sha256', 'compatibility_key', 'identity', 'accounting', 'accounting_source', 'inventory_integrity')})) + '</pre></details></article>')
        for concurrency, group in study['concurrency_groups'].items():
            for pair in group['pairs']:
                ratio = pair['throughput_candidate_over_baseline'] if study['eligible'] and group['eligible'] and pair['eligible'] else None
                pair_rows.append('<tr>' + ''.join(_td(value) for value in (study['label'], concurrency, pair['pair_index'] + 1,
                    'Match' if pair['token_parity'] else 'Different', 'Unavailable' if ratio is None else f'{ratio:.6f}',
                    'Unavailable' if pair.get('full_wall_efficiency_candidate_over_baseline') is None else f"{pair['full_wall_efficiency_candidate_over_baseline']:.6f}",
                    ', '.join(pair['token_mismatch_request_ids']) or 'None')) + '</tr>')
        for attempt in study['attempts']:
            metric = attempt['metrics']
            serving = metric.get('serving') or {}
            qualified = (f"{serving['slo_qualified_requests']} / {serving['offered_requests']}"
                         if 'slo_qualified_requests' in serving else 'Unavailable')
            goodput = serving.get('goodput_per_second')
            attempt_rows.append('<tr>' + ''.join(_td(value) for value in (study['label'], metric['attempt_id'], metric['arm'], metric['concurrency'],
                metric['pair_index'] + 1, metric['status'], f"{metric['quality_correct']} / {metric['quality_denominator']}",
                f"{metric['observed_requests']} / {metric['expected_requests']}",
                qualified, 'Unavailable' if goodput is None else f'{goodput:.6f}',
                'Unavailable' if metric['successful_requests_per_second'] is None else f"{metric['successful_requests_per_second']:.6f}",
                _seconds(metric['latency']['client_ttft_ns']['p95']),
                _seconds(metric['latency']['client_end_to_end_ns']['p95']),
                _seconds(metric['full_wall_ns']))) + '<td><details><summary>Attempt metrics</summary><pre>' +
                _e(_json({'metrics': metric, 'source': attempt['metrics_source']})) + '</pre></details></td></tr>')
            for request in attempt['requests']:
                normalized = request['normalized']
                attributes = {'study': sid, 'family': study['workload_family'], 'concurrency': metric['concurrency'], 'pair': metric['pair_index'], 'arm': metric['arm'],
                    'quality': 'pass' if request['quality_correct'] else 'fail', 'parity': request['parity']['status']}
                attrs = ' '.join('data-' + key + '="' + _e(value) + '"' for key, value in attributes.items())
                cache = request['native']['cache']
                cache_text = str(cache['reused_input_tokens']) if cache['status'] == 'RECONCILED_NATIVE' else 'Unavailable'
                request_rows.append('<tr data-request ' + attrs + '>' + ''.join(_td(value) for value in (
                    study['label'], f"{metric['concurrency']} / {metric['pair_index'] + 1} / {metric['arm']}", request['request_id'], request['status'],
                    'Correct' if request['quality_correct'] else 'Incorrect / missing', request['parity']['status'], request['expected_answer'],
                    normalized['output_text'] if normalized else 'Missing observation', cache_text)) +
                    '<td>' + _request_details(request, metric, attempt['metrics_source']) + '</td></tr>')
    source_json = _json(catalog).replace('&', '\\u0026').replace('<', '\\u003c').replace('>', '\\u003e').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'none'; img-src 'none'; base-uri 'none'; form-action 'none'">
<title>Evidence workbench · Lean Model Lab</title><style>
:root{color-scheme:light;--ink:#192b32;--muted:#41585f;--line:#c8d3d5;--paper:#f7f9f8;--accent:#09655b}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}header,main,footer{max-width:1440px;margin:auto;padding:2rem 1.5rem}header,footer{border-bottom:1px solid var(--line)}h1{font-size:clamp(2rem,5vw,3.5rem);line-height:1.1;letter-spacing:-.03em}h2{margin-top:0}section{margin-bottom:2.5rem}p{max-width:85ch}.badge{color:var(--accent);font-size:.85rem;font-weight:700}a{color:var(--accent)}a:focus-visible,summary:focus-visible,select:focus-visible,button:focus-visible,[tabindex]:focus-visible{outline:3px solid #9d4a00;outline-offset:4px}.skip{position:absolute;top:-8rem;left:1rem;background:white;padding:1rem}.skip:focus{top:1rem}.notice{border-left:4px solid #9d4a00;padding:.5rem 1rem;background:#fff5e8}.studies{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:1.25rem}article{background:white;border:1px solid var(--line);padding:1.25rem;min-width:0}dt{color:var(--muted)}dd{margin:.15rem 0 .7rem;font-weight:600;overflow-wrap:anywhere}fieldset{border:1px solid var(--line);padding:1rem;display:flex;flex-wrap:wrap;gap:1rem}legend{font-weight:650}label{display:flex;flex-direction:column;gap:.3rem;flex:1 1 220px}select,button{font:inherit;min-height:44px;padding:.5rem;background:white;color:var(--ink);border:1px solid var(--muted);border-radius:3px}button{cursor:pointer;align-self:end}.table-scroll{overflow:auto;max-width:100%;border:1px solid var(--line);background:white}table{border-collapse:collapse;width:100%;font-size:.875rem}caption{text-align:left;padding:1rem;font-weight:650}th,td{text-align:left;vertical-align:top;padding:.75rem;border-bottom:1px solid var(--line)}th{background:#eaf0ed}td{max-width:35rem;overflow-wrap:anywhere}summary{cursor:pointer;padding:.5rem 0;font-weight:600;min-height:44px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:.8rem;max-height:32rem;overflow:auto;border:1px solid var(--line);padding:.8rem}details{min-width:12rem}article details{min-width:0}[hidden]{display:none!important}.muted{color:var(--muted)}@media(max-width:480px){header,main,footer{padding:1.5rem 1rem}fieldset{padding:.75rem}}@media print{fieldset,.skip{display:none}.table-scroll{overflow:visible}table{font-size:9px}}
p,li{overflow-wrap:anywhere}fieldset,label{min-width:0}select{min-width:0;width:100%}.status-cell{white-space:nowrap}.cost-details .table-scroll{margin:1rem 0}.request-details{min-width:18rem;max-width:30rem}.request-details dd{font-size:.875rem;white-space:pre-wrap}.section-nav{display:flex;flex-wrap:wrap;gap:.5rem 1.25rem;margin-top:1rem}.section-nav a{display:inline-block;min-height:44px;padding:.5rem 0}
</style></head><body><a class="skip" href="#main">Skip to evidence</a>
<header><p class="badge">LEAN MODEL LAB / OFFLINE WORKBENCH</p><h1>Compare evidence, with its limits in view.</h1><p>''' + _e(catalog['summary']['finding']) + '''</p>
<p class="notice">''' + _e(f"{len(studies)} {'study' if len(studies) == 1 else 'studies'} · {catalog['summary']['eligible_studies']} campaign-eligible · {catalog['summary']['measured_claim_eligible_studies']} measured-claim-eligible · {len(catalog['compatibility_groups'])} strict identity {'group' if len(catalog['compatibility_groups']) == 1 else 'groups'}.") + ''' No cross-study speed ranking or pooled estimate is computed.</p><nav class="section-nav" aria-label="Evidence sections"><a href="#requests-heading">Filter requests</a><a href="#pairs-heading">Paired results</a><a href="#attempts-heading">All attempts</a><a href="#studies-heading">Costs and findings</a></nav></header>
<main id="main" tabindex="-1"><section aria-labelledby="studies-heading"><h2 id="studies-heading">Study findings and complete costs</h2><p>Each card retains all attempts, including failure and recovery history. Full wall spans overlap between related studies and must not be added across studies. Finalized inventory means all recorded reservations reconcile; a planned schedule may still be incomplete.</p><div class="studies">''' + ''.join(summaries) + '''</div></section>
<section aria-labelledby="pairs-heading"><h2 id="pairs-heading">Within-study paired evidence</h2><p>Service ratios are candidate / baseline request throughput. Full-wall efficiency is baseline / candidate attempt duration, including context analysis, tokenization, verification, load and shutdown; it is the primary cost comparison for v3. Ratios are unavailable when campaign eligibility fails. Changed-input v3 interventions are gated on task quality, while token differences remain descriptive. TEST_FIXTURE values exercise calculations and are not measured results. Identity groups include model, tokenizer, workload, implementation, backend revision, patch and binary, engine, sampling, evaluation, hardware, and all other frozen fields except study ID and clock.</p>''' + _table(['Study', 'Concurrency', 'Pair', 'Observed token parity', 'Service throughput ratio', 'Full-wall efficiency ratio', 'Token mismatch request IDs'], pair_rows, 'Paired observations; no cross-study ratios') + '''</section>
<section aria-labelledby="attempts-heading"><h2 id="attempts-heading">Every retained attempt</h2><p>Latency-qualified responses must have an exact correct answer and meet both frozen TTFT and completion targets. Goodput divides that count by the complete service envelope; every offered request remains in its quality denominator. Throughput and client latency are descriptive observations, including ineligible runs. TTFT covers observed nonempty token chunks only; other denominators remain in the metric evidence.</p>''' + _table(['Study', 'Attempt', 'Arm', 'Concurrency', 'Pair', 'Status', 'Correct / expected', 'Observed / expected', 'Latency-qualified / offered', 'Goodput / s', 'Observed requests / s', 'Client TTFT p95', 'Client end-to-end p95', 'Full attempt wall', 'Metric evidence'], attempt_rows, 'Complete attempt inventory, unaffected by request filters') + '''</section>
<section aria-labelledby="requests-heading"><h2 id="requests-heading">Request evidence drilldown</h2><p id="filter-help">Filters combine and affect only request rows. Study totals and attempts always remain complete. Pair numbers start at 1 here; source pair_index starts at 0. Token parity checks IDs, generated counts and prompt counts; exact text equality is reported separately in each evidence disclosure. Scroll tables horizontally on narrow screens.</p>
<noscript><p class="notice">JavaScript is disabled. All evidence remains readable; request filters are unavailable.</p></noscript><fieldset aria-describedby="filter-help"><legend>Filter request evidence</legend>''' + controls + '''<button id="reset-filters" type="button" disabled>Reset filters</button></fieldset><p id="filter-count" role="status" aria-live="polite">''' + str(len(request_rows)) + ''' request rows shown.</p><p id="empty-state" hidden>No request evidence matches these filters. Reset filters to inspect every retained observation.</p>''' + _table(['Study', 'Concurrency / pair / arm', 'Request', 'Status', 'Exact quality', 'Token parity', 'Expected answer', 'Observed text', 'Reused input tokens', 'Retained evidence'], request_rows, 'Expected requests across all retained attempts, including missing observations') + '''</section>
<section aria-labelledby="scope-heading"><h2 id="scope-heading">Evidence boundaries</h2><p>Energy, engine execution-start latency, and engine inter-token emission timing are unavailable. Client receipts cannot establish these quantities. Input token IDs and cache counts are shown only for the supported retained native protocol; absent evidence is never treated as zero.</p><p>''' + _e(catalog['integrity_limit']) + '''</p><p>Machine-readable source references identify bundle-relative documents and JSON pointers. Operational setup descriptions are omitted from this portable view; original files are unchanged. The embedded catalog uses the same schema as the JSON export.</p></section>
</main><footer>This local page uses no remote assets, network requests, telemetry, or model execution. It does not establish publication, external reproduction, human review, or accessibility certification.</footer>
<script id="workbench-catalog" type="application/json">''' + source_json + '''</script><script>
(function(){'use strict';
const controls=Array.from(document.querySelectorAll('[data-filter]'));
const rows=Array.from(document.querySelectorAll('[data-request]'));
const reset=document.getElementById('reset-filters');
function apply(){let visible=0;for(const row of rows){const show=controls.every(control=>!control.value||row.dataset[control.dataset.filter]===control.value);row.hidden=!show;if(show)visible++;}document.getElementById('filter-count').textContent=visible+' of '+rows.length+' request rows shown.';document.getElementById('empty-state').hidden=visible!==0;}
for(const control of controls){control.disabled=false;control.addEventListener('change',apply);}reset.disabled=false;reset.addEventListener('click',function(){for(const control of controls)control.value='';apply();});apply();
})();
</script></body></html>'''
