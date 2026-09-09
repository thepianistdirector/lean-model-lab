"""Recipe-bound CPU evidence, including explicit decisions without dispatch.

Malformed observations raise EvidenceError. Well-formed adverse observations
remain in every applicable denominator and invalidate comparative claims. No
attempt-only result establishes complete inventory, costs or authenticity.
"""
from __future__ import annotations

import re
import statistics
from collections import Counter
from typing import Any

from .config import validate_config_v2
from .contracts import ContractError, digest
from .evidence import (ATTEMPT_KEYS, OVERHEAD_KEYS, REQUEST_KEYS, EvidenceError,
                       _check, _choice, _distribution, _integer, _keys, _text,
                       _tokens, _unavailable, _validate_environment)
from .recipes import schedule
from .workloads import validate_workload_v2


def _validate_inputs(workload: Any, config: Any, config_sha256: str,
                     workload_sha256: str) -> None:
    try:
        validate_workload_v2(workload)
        validate_config_v2(config)
    except (ContractError, KeyError, TypeError) as exc:
        raise EvidenceError(f'invalid frozen v2 inputs: {exc}') from exc
    for name, value in (('config_sha256', config_sha256), ('workload_sha256', workload_sha256)):
        _check(type(value) is str and re.fullmatch(r'[0-9a-f]{64}', value) is not None,
               f'invalid expected {name}')
    _check(digest(config) == config_sha256, 'configuration digest does not match frozen input')
    _check(digest(workload) == workload_sha256, 'workload digest does not match frozen input')
    _check(config['workload_sha256'] == workload_sha256,
           'workload is not bound to the frozen recipe configuration')


def _validate_attempt(attempt: Any, workload: dict, config: dict,
                      config_sha256: str, workload_sha256: str) -> None:
    _keys(attempt, ATTEMPT_KEYS, 'attempt')
    _integer(attempt['schema_version'], 'schema_version', 2, 2)
    _choice(attempt['evidence_class'], ('MEASURED', 'TEST_FIXTURE'), 'evidence_class')
    _check(attempt['evidence_class'] == config['evidence_class'], 'configuration evidence class mismatch')
    _text(attempt['attempt_id'], 'attempt_id')
    _check(attempt['config_sha256'] == config_sha256, 'configuration identity mismatch')
    _check(attempt['workload_sha256'] == workload_sha256, 'workload identity mismatch')
    _choice(attempt['arm'], ('baseline', 'candidate'), 'arm')
    _integer(attempt['concurrency'], 'concurrency', 1, 8)
    _integer(attempt['pair_index'], 'pair_index', 0, config['evaluation']['pairs_per_concurrency'] - 1)
    _check((attempt['concurrency'], attempt['pair_index'], attempt['arm']) in schedule(config),
           'attempt cell is not in the frozen schedule')
    _choice(attempt['status'], ('COMPLETED', 'INTERRUPTED', 'FAILED'), 'attempt.status')
    for field in ('started_ns', 'service_started_ns', 'finished_ns'):
        _integer(attempt[field], field)
    _check(attempt['started_ns'] <= attempt['service_started_ns'] <= attempt['finished_ns'],
           'invalid attempt clock order')
    _check(attempt['finished_ns'] > attempt['started_ns'], 'attempt duration must be positive')
    _keys(attempt['overhead_ns'], OVERHEAD_KEYS, 'overhead_ns')
    for field, value in attempt['overhead_ns'].items():
        _integer(value, f'overhead_ns.{field}')
    _check(sum(attempt['overhead_ns'].values()) <= attempt['finished_ns'] - attempt['started_ns'],
           'overhead phases overlap or exceed full wall')
    _check(attempt['overhead_ns']['service'] <= attempt['finished_ns'] - attempt['service_started_ns'],
           'service exceeds remaining attempt duration')
    _validate_environment(attempt['environment'])
    for field in ('platform', 'cpu'):
        _check(attempt['environment'][field] == config['hardware'][field],
               'hardware identity differs from frozen configuration')

    expected = {row['request_id']: row for row in workload['requests']}
    _check(type(attempt['requests']) is list, 'requests must be a list')
    seen = set()
    for request in attempt['requests']:
        _keys(request, REQUEST_KEYS, 'request')
        identifier = request['request_id']
        _text(identifier, 'request_id')
        _check(identifier in expected, 'unexpected request ID')
        _check(identifier not in seen, 'duplicate request ID')
        seen.add(identifier)
        for field in ('arrival_ns', 'completed_ns'):
            _integer(request[field], field)
        _check(request['arrival_ns'] == attempt['service_started_ns'] + expected[identifier]['arrival_offset_ns'],
               'arrival differs from the frozen trace')
        _check(request['arrival_ns'] <= request['completed_ns'] <= attempt['finished_ns'],
               'invalid request clock order')
        _check(request['completed_ns'] - attempt['service_started_ns'] <= attempt['overhead_ns']['service'],
               'service accounting excludes request time')
        _integer(request['prompt_tokens'], 'prompt_tokens', 1, 2**31 - 1)
        _tokens(request['output_token_ids'], 'output_token_ids')
        if request['generated_tokens'] is not None:
            _integer(request['generated_tokens'], 'generated_tokens', 0, 4096)
            _check(request['generated_tokens'] >= len(request['output_token_ids']),
                   'generated token count is smaller than observed output IDs')
        _text(request['output_text'], 'output_text', empty=True)
        _choice(request['status'], ('SUCCEEDED', 'FAILED', 'CANCELLED', 'REJECTED', 'EXPIRED'), 'request.status')
        _choice(request['finish_reason'], ('eos', 'limit', 'error', 'cancelled', 'queue_full', 'deadline'),
                'finish_reason')
        reasons = {'SUCCEEDED': ('eos', 'limit'), 'FAILED': ('error',), 'CANCELLED': ('cancelled',),
                   'REJECTED': ('queue_full',), 'EXPIRED': ('deadline',)}
        _check(request['finish_reason'] in reasons[request['status']], 'status/finish reason mismatch')
        _check(type(request['token_events']) is list, 'token_events must be a list')
        _check(request['engine_start_ns'] is None,
               'engine_start_ns must be null: the admitted adapter has no engine-start probe')
        if request['status'] in ('REJECTED', 'EXPIRED'):
            _check(all(request[field] is None for field in ('admitted_ns', 'dispatch_ns', 'first_token_ns')),
                   'local queue decisions cannot contain admission or dispatch timestamps')
            _check(request['output_text'] == '' and request['output_token_ids'] == [] and
                   request['token_events'] == [] and type(request['generated_tokens']) is int and
                   request['generated_tokens'] == 0,
                   'local queue decisions require empty output and a proved zero generated count')
            if request['status'] == 'EXPIRED':
                deadline = workload['request_deadline_ns']
                _check(deadline is not None, 'EXPIRED requires a declared request deadline')
                _check(request['completed_ns'] >= request['arrival_ns'] + deadline,
                       'expiration decision predates the offered-arrival deadline')
            continue

        for field in ('admitted_ns', 'dispatch_ns'):
            _integer(request[field], field)
        _check(request['arrival_ns'] <= request['admitted_ns'] <= request['dispatch_ns'] <= request['completed_ns'],
               'invalid admitted request clock order')
        _check(request['status'] != 'SUCCEEDED' or request['generated_tokens'] is not None,
               'successful request requires the actual generated token counter')
        _check(not (request['status'] == 'SUCCEEDED' and request['output_text'] and
                    not request['output_token_ids']), 'successful nonempty text has no observed output tokens')
        observed_tokens = []
        first_observed = None
        previous = request['dispatch_ns']
        for event in request['token_events']:
            _keys(event, {'observed_ns', 'token_ids'}, 'token event')
            _integer(event['observed_ns'], 'token event observed_ns')
            _tokens(event['token_ids'], 'token event token_ids')
            _check(previous <= event['observed_ns'] <= request['completed_ns'], 'invalid chunk clock order')
            previous = event['observed_ns']
            if event['token_ids'] and first_observed is None:
                first_observed = event['observed_ns']
            observed_tokens.extend(event['token_ids'])
        _check(observed_tokens == request['output_token_ids'], 'chunk tokens differ from final tokens')
        if request['first_token_ns'] is not None:
            _integer(request['first_token_ns'], 'first_token_ns')
        _check(request['first_token_ns'] == first_observed,
               'first token must equal first nonempty token chunk')

    if attempt['status'] == 'COMPLETED':
        _check(seen == set(expected), 'completed attempt has missing requests')
    admitted = [row for row in attempt['requests'] if row['admitted_ns'] is not None]
    boundaries = []
    for request in admitted:
        if request['admitted_ns'] < request['completed_ns']:
            boundaries.extend(((request['admitted_ns'], 1), (request['completed_ns'], -1)))
    active = 0
    for _, change in sorted(boundaries):
        active += change
        _check(active <= attempt['concurrency'], 'observed in-flight count exceeds declared concurrency')
    by_id = {row['request_id']: row for row in admitted}
    for lane in range(attempt['concurrency']):
        previous_completion = attempt['service_started_ns']
        for expected_request in workload['requests'][lane::attempt['concurrency']]:
            request = by_id.get(expected_request['request_id'])
            if request is not None:
                _check(request['admitted_ns'] >= previous_completion,
                       'request order violates the frozen deterministic lane assignment')
                previous_completion = request['completed_ns']


def validate_attempt_v2(attempt: Any, workload: Any, *, config: Any,
                        config_sha256: str, workload_sha256: str) -> None:
    _validate_inputs(workload, config, config_sha256, workload_sha256)
    _validate_attempt(attempt, workload, config, config_sha256, workload_sha256)


def _summarize(attempt: dict, workload: dict, config: dict) -> dict:
    records = attempt['requests']
    expected = {row['request_id']: row for row in workload['requests']}
    missing_ids = sorted(set(expected) - {row['request_id'] for row in records})
    statuses = Counter(row['status'] for row in records)
    admitted = [row for row in records if row['admitted_ns'] is not None]
    correct_rows = [row for row in records if row['status'] == 'SUCCEEDED' and
                    row['output_text'].strip() == expected[row['request_id']]['expected']]
    correct = len(correct_rows)
    truncated = sum(row['finish_reason'] == 'limit' for row in records)
    budget = workload['max_output_tokens']
    over_budget = sum((row['generated_tokens'] is not None and row['generated_tokens'] > budget) or
                      len(row['output_token_ids']) > budget for row in records)
    quality = correct / len(expected)
    tokens = sum(len(row['output_token_ids']) for row in records)
    successful_tokens = sum(len(row['output_token_ids']) for row in records if row['status'] == 'SUCCEEDED')
    service_ns = attempt['overhead_ns']['service']
    full_wall_ns = attempt['finished_ns'] - attempt['started_ns']
    evaluation = config['evaluation']
    reasons = []
    if attempt['status'] != 'COMPLETED': reasons.append('attempt_not_completed')
    if missing_ids: reasons.append('missing_requests')
    if statuses['SUCCEEDED'] != len(expected): reasons.append('not_all_requests_succeeded')
    if truncated: reasons.append('length_limit_completion')
    if over_budget: reasons.append('generated_token_budget_exceeded')
    if quality < evaluation['accuracy_minimum']: reasons.append('absolute_quality_below_0.95')
    if not service_ns: reasons.append('zero_service_duration')
    if config['recipe']['purpose'] != 'MEASUREMENT': reasons.append('development_recipe_not_measurement')
    allocation = config['recipe']['allocation']
    if not allocation['started_ns'] <= attempt['started_ns'] < attempt['finished_ns'] <= allocation['deadline_ns']:
        reasons.append('attempt_outside_registered_allocation')
    latency = {
        'client_queue_ns': _distribution([row['admitted_ns'] - row['arrival_ns'] for row in admitted]),
        'admission_to_dispatch_ns': _distribution([row['dispatch_ns'] - row['admitted_ns'] for row in admitted]),
        'client_ttft_ns': _distribution([row['first_token_ns'] - row['arrival_ns'] for row in records
                                         if row['first_token_ns'] is not None]),
        'client_end_to_end_ns': _distribution([row['completed_ns'] - row['arrival_ns'] for row in records]),
        'client_chunk_gap_ns': _distribution([second - first for row in records
            for times in [[event['observed_ns'] for event in row['token_events'] if event['token_ids']]]
            for first, second in zip(times, times[1:])]),
    }
    strata = {}
    for stratum in sorted({row['stratum'] for row in expected.values()}):
        ids = {key for key, row in expected.items() if row['stratum'] == stratum}
        present = [row for row in records if row['request_id'] in ids]
        stratum_correct = sum(row['request_id'] in ids for row in correct_rows)
        strata[str(stratum)] = {'expected_count': len(ids), 'observed_count': len(present),
                               'quality_accuracy': stratum_correct / len(ids),
                               'client_end_to_end_ns': _distribution([
                                   row['completed_ns'] - row['arrival_ns'] for row in present])}
    offsets = [row['arrival_offset_ns'] for row in workload['requests']]
    offered_span = max(offsets) - min(offsets)
    qualified = sum(row['first_token_ns'] is not None and
                    row['first_token_ns'] - row['arrival_ns'] <= evaluation['ttft_slo_ns'] and
                    row['completed_ns'] - row['arrival_ns'] <= evaluation['end_to_end_slo_ns']
                    for row in correct_rows)
    serving = {
        'arrival_mode': workload['arrival_mode'], 'offered_requests': len(expected),
        'observed_requests': len(records), 'admitted_requests': len(admitted),
        'completed_requests': statuses['SUCCEEDED'], 'rejected_requests': statuses['REJECTED'],
        'expired_requests': statuses['EXPIRED'], 'failed_requests': statuses['FAILED'],
        'cancelled_requests': statuses['CANCELLED'], 'missing_requests': len(missing_ids),
        'offered_arrival_span_ns': offered_span,
        'offered_requests_per_second': len(expected) * 1e9 / offered_span if offered_span else None,
        'service_envelope_ns': service_ns,
        'admitted_requests_per_second': len(admitted) * 1e9 / service_ns if service_ns else None,
        'completed_requests_per_second': statuses['SUCCEEDED'] * 1e9 / service_ns if service_ns else None,
        'ttft_slo_ns': evaluation['ttft_slo_ns'], 'end_to_end_slo_ns': evaluation['end_to_end_slo_ns'],
        'slo_qualified_requests': qualified, 'slo_qualified_fraction': qualified / len(expected),
        'goodput_per_second': qualified * 1e9 / service_ns if service_ns else None,
        'ttft_unobserved_admitted_requests': sum(row['first_token_ns'] is None for row in admitted),
        'generated_tokens_unknown_requests': sum(row['generated_tokens'] is None for row in records),
        'denominator_notes': 'Offered rate is all declared arrivals divided by last-minus-first arrival offset; '
            'zero-span batches have no offered rate. Admitted/completed rates and goodput use the full service '
            'envelope. Qualified means SUCCEEDED with an exact answer and observed TTFT/end-to-end within both '
            'declared SLOs. The qualified fraction divides by every offered request, including missing and local '
            'rejection/expiry decisions. Descriptive goodput does not override campaign validity gates.',
    }
    return {
        'attempt_id': attempt['attempt_id'], 'evidence_class': attempt['evidence_class'],
        'arm': attempt['arm'], 'concurrency': attempt['concurrency'], 'pair_index': attempt['pair_index'],
        'status': attempt['status'], 'eligible': not reasons, 'ineligibility_reasons': reasons,
        'expected_requests': len(expected), 'observed_requests': len(records), 'missing_request_ids': missing_ids,
        'succeeded_requests': statuses['SUCCEEDED'], 'failed_requests': statuses['FAILED'],
        'cancelled_requests': statuses['CANCELLED'], 'rejected_requests': statuses['REJECTED'],
        'expired_requests': statuses['EXPIRED'], 'truncated_requests': truncated,
        'over_token_budget_requests': over_budget,
        'quality_correct': correct, 'quality_denominator': len(expected), 'quality_accuracy': quality,
        'quality_pass': quality >= evaluation['accuracy_minimum'], 'output_tokens_observed': tokens,
        'generated_tokens_reported': sum(row['generated_tokens'] for row in records if row['generated_tokens'] is not None),
        'generated_tokens_unknown_requests': sum(row['generated_tokens'] is None for row in records),
        'generated_minus_visible_tokens': sum(row['generated_tokens'] - len(row['output_token_ids'])
                                               for row in records if row['generated_tokens'] is not None),
        'prompt_tokens_observed': sum(row['prompt_tokens'] for row in records),
        'successful_requests_per_second': statuses['SUCCEEDED'] * 1e9 / service_ns if service_ns else None,
        'successful_output_tokens_per_second': successful_tokens * 1e9 / service_ns if service_ns else None,
        'service_ns': service_ns, 'full_wall_ns': full_wall_ns, 'overhead_ns': dict(attempt['overhead_ns']),
        'unattributed_wall_ns': full_wall_ns - sum(attempt['overhead_ns'].values()),
        'latency': latency, 'strata': strata, 'serving': serving, 'environment': attempt['environment'],
        'dispatch_to_engine_start_ns': _unavailable('the admitted adapter has no engine-start probe'),
        'inter_token_latency_ns': _unavailable('stream chunks do not establish individual engine token emission times'),
        'accelerator_memory_bytes': _unavailable('CPU adapter has no accelerator probe'),
        'denominator_notes': f'Quality uses all {len(expected)} offered requests. End-to-end latency includes '
            'every retained terminal request or local decision. Queue/dispatch latency includes admitted '
            'requests only; TTFT requires an observed nonempty token chunk. Missing counts remain explicit.',
    }


def summarize_attempt_v2(attempt: Any, workload: Any, *, config: Any,
                         config_sha256: str, workload_sha256: str) -> dict:
    validate_attempt_v2(attempt, workload, config=config, config_sha256=config_sha256,
                         workload_sha256=workload_sha256)
    return _summarize(attempt, workload, config)


def evaluate_campaign_v2(attempts: Any, workload: Any, *, config: Any,
                         config_sha256: str, workload_sha256: str) -> dict:
    """Evaluate the complete registered schedule; global gates precede all ratios."""
    _validate_inputs(workload, config, config_sha256, workload_sha256)
    _check(type(attempts) is list and bool(attempts), 'campaign requires at least one attempt')
    for attempt in attempts:
        _validate_attempt(attempt, workload, config, config_sha256, workload_sha256)
    _check(len({a['attempt_id'] for a in attempts}) == len(attempts), 'duplicate attempt ID')
    ordered = sorted(attempts, key=lambda a: a['started_ns'])
    _check(all(a['finished_ns'] <= b['started_ns'] for a, b in zip(ordered, ordered[1:])),
           'attempts overlap; sequential study costs cannot be summed')
    summaries = [_summarize(a, workload, config) for a in ordered]
    summary_by_id = {a['attempt_id']: a for a in summaries}
    declared = schedule(config)
    actual = [(a['concurrency'], a['pair_index'], a['arm']) for a in ordered]
    evaluation = config['evaluation']
    pair_count = evaluation['pairs_per_concurrency']
    reasons = []
    if len(attempts) != len(declared): reasons.append(f'fixed_design_requires_exactly_{len(declared)}_attempts')
    if any(not row['eligible'] for row in summaries): reasons.append('one_or_more_attempts_ineligible')
    if config['recipe']['purpose'] != 'MEASUREMENT': reasons.append('development_recipe_not_measurement')
    if actual != declared: reasons.append('registered_schedule_order_invalid')
    cells = {}
    prompt_counts = {}
    for attempt in ordered:
        cells.setdefault((attempt['concurrency'], attempt['pair_index'], attempt['arm']), []).append(attempt)
        for request in attempt['requests']:
            prompt_counts.setdefault(request['request_id'], set()).add(request['prompt_tokens'])
    drift_ids = {identifier for identifier, counts in prompt_counts.items() if len(counts) != 1}
    if drift_ids: reasons.append('prompt_token_counts_changed_across_attempts')
    if set(cells) != set(declared) or any(len(value) != 1 for value in cells.values()):
        reasons.append('missing_or_duplicate_comparison_cells')
    groups = {}
    for concurrency in evaluation['concurrency_modes']:
        order_ok = [cell for cell in actual if cell[0] == concurrency] == [cell for cell in declared if cell[0] == concurrency]
        if not order_ok: reasons.append(f'concurrency_{concurrency}_counterbalanced_order_invalid')
        pairs = []
        for pair in range(pair_count):
            left, right = cells.get((concurrency, pair, 'baseline'), []), cells.get((concurrency, pair, 'candidate'), [])
            if len(left) != 1 or len(right) != 1:
                continue
            baseline, candidate = left[0], right[0]
            left_requests = {r['request_id']: r for r in baseline['requests']}
            right_requests = {r['request_id']: r for r in candidate['requests']}
            identifiers = set(left_requests) | set(right_requests)
            mismatches = sorted(identifier for identifier in identifiers
                if identifier not in left_requests or identifier not in right_requests or
                left_requests[identifier]['output_token_ids'] != right_requests[identifier]['output_token_ids'] or
                left_requests[identifier]['generated_tokens'] != right_requests[identifier]['generated_tokens'])
            prompt_mismatches = sorted(identifier for identifier in set(left_requests) & set(right_requests)
                if left_requests[identifier]['prompt_tokens'] != right_requests[identifier]['prompt_tokens'])
            parity = not mismatches and len(left_requests) == len(right_requests) == len(workload['requests'])
            if not parity or prompt_mismatches:
                reasons.append(f'concurrency_{concurrency}_pair_{pair}_token_identity_or_parity_failed')
            pairs.append({'pair_index': pair, 'baseline_attempt_id': baseline['attempt_id'],
                          'candidate_attempt_id': candidate['attempt_id'], 'eligible': False,
                          'token_parity': parity, 'token_mismatch_request_ids': mismatches,
                          'prompt_token_mismatch_request_ids': prompt_mismatches,
                          'campaign_prompt_identity_drift_request_ids': sorted(drift_ids & identifiers),
                          'throughput_candidate_over_baseline': None,
                          'end_to_end_tail_candidate_over_baseline': {'p95': None, 'p99': None},
                          'ttft_tail_candidate_over_baseline': {'p95': None, 'p99': None}})
        groups[str(concurrency)] = {'pairs': pairs, 'counterbalanced_order_valid': order_ok,
                                    'pair_count': 0, 'throughput_ratio_median': None,
                                    'throughput_ratio_range': None, 'finding': 'INELIGIBLE', 'eligible': False}
    eligible = not reasons
    # Never emit a favorable pair or group ratio from an otherwise invalid campaign.
    for group in groups.values():
        if not eligible:
            group['ineligibility_reasons'] = sorted(set(reasons))
            continue
        for pair in group['pairs']:
            base = summary_by_id[pair['baseline_attempt_id']]
            cand = summary_by_id[pair['candidate_attempt_id']]
            pair['eligible'] = True
            pair['throughput_candidate_over_baseline'] = cand['successful_requests_per_second'] / base['successful_requests_per_second']
            for field, metric in (('end_to_end_tail_candidate_over_baseline', 'client_end_to_end_ns'),
                                  ('ttft_tail_candidate_over_baseline', 'client_ttft_ns')):
                for percentile in ('p95', 'p99'):
                    before, after = base['latency'][metric][percentile], cand['latency'][metric][percentile]
                    pair[field][percentile] = after / before if before and after is not None else None
        ratios = [pair['throughput_candidate_over_baseline'] for pair in group['pairs']]
        tails = [value for pair in group['pairs']
                 for metric in ('end_to_end_tail_candidate_over_baseline', 'ttft_tail_candidate_over_baseline')
                 for value in pair[metric].values() if value is not None]
        finding = ('TAIL_REGRESSION' if any(v > 1 + evaluation['maximum_tail_regression'] for v in tails) else
                   'PRACTICAL_GAIN_IN_ALL_PAIRS' if min(ratios) >= 1 + evaluation['practical_throughput_gain'] else
                   'NO_DEMONSTRATED_PRACTICAL_GAIN')
        group.update(eligible=True, finding=finding, pair_count=len(ratios),
                     throughput_ratio_median=statistics.median(ratios), throughput_ratio_range=[min(ratios), max(ratios)])
    evidence_class = config['evidence_class']
    return {
        'schema_version': 2, 'evaluator_version': '0.4.0-dev', 'evidence_class': evidence_class,
        'config_sha256': config_sha256, 'workload_sha256': workload_sha256,
        'recipe_context': {'recipe_sha256':digest(config['recipe']), 'purpose':config['recipe']['purpose'],
            'model_profile_id':config['model']['profile_id'],'engine':config['engine'],
            'evaluation':config['evaluation'],'workload_generator':workload['generator']},
        'eligible': eligible, 'measured_claim_eligible': False,
        'finding': 'TEST_FIXTURE_ONLY' if evidence_class == 'TEST_FIXTURE' else
                   ('PAIRED_DEVICE_SPECIFIC_RESULT' if eligible else 'INELIGIBLE'),
        'ineligibility_reasons': sorted(set(reasons)), 'attempts': summaries, 'concurrency_groups': groups,
        'accounting': {
            'attempt_count': len(attempts), 'expected_requests_across_attempts': len(workload['requests']) * len(attempts),
            'observed_requests': sum(row['observed_requests'] for row in summaries),
            'missing_requests': sum(len(row['missing_request_ids']) for row in summaries),
            'visible_output_tokens_observed': sum(row['output_tokens_observed'] for row in summaries),
            'generated_tokens_reported': sum(row['generated_tokens_reported'] for row in summaries),
            'generated_tokens_unknown_requests': sum(row['generated_tokens_unknown_requests'] for row in summaries),
            'full_wall_ns': sum(row['full_wall_ns'] for row in summaries),
            'elapsed_span_ns': ordered[-1]['finished_ns'] - ordered[0]['started_ns'],
            'overhead_ns': {key: sum(row['overhead_ns'][key] for row in summaries) for key in sorted(OVERHEAD_KEYS)},
            'unattributed_wall_ns': sum(row['unattributed_wall_ns'] for row in summaries),
            'setup_acquisition_build_costs': _unavailable('not included in attempt documents; require separate retained setup ledger'),
            'monetary_cost': _unavailable('no monetary-cost probe or estimate'),
        },
        'thresholds': {'absolute_accuracy': evaluation['accuracy_minimum'],
                       'practical_throughput_gain': evaluation['practical_throughput_gain'],
                       'maximum_tail_regression': evaluation['maximum_tail_regression']},
        'limitations': [
            f'{pair_count} paired runs per concurrency with balanced AB/BA order; ranges are descriptive, not confidence intervals or significance tests.',
            f'{len(workload["requests"])}-request p95/p99 estimates and smaller stratum tails have limited resolution; correlated requests are not independent replicate runs.',
            'Client chunk receipts do not establish individual token emission times or engine-internal latency.',
            'Synthetic key copying does not establish general language-model competence or protected confirmation.',
            'All supplied attempts are retained; this file alone cannot prove omitted attempts do not exist.',
            'Digest consistency does not authenticate externally supplied observations.',
            'Attempt-only evaluation does not verify complete inventory or acquisition/build costs.',
            'Offered arrivals and local queue decisions remain in the quality and SLO-fraction denominator; missing requests cannot improve goodput.',
            'Results apply to the declared arrival trace and device; finite batches do not imply online serving, energy or cross-device superiority.',
        ],
    }
