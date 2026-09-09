#!/usr/bin/env python3
"""Recompute descriptive systems tables from retained producer artifacts.

This analysis does not execute models, regenerate confirmation tasks, or create
an alternative evaluator. Packaged report/native-audit gates remain authoritative.
No comparative efficiency ratio is emitted for an ineligible campaign.
"""
import argparse
import csv
import hashlib
import json
import math
from decimal import Decimal
from pathlib import Path


def read(path):
    return json.loads(path.read_text())


def checksum(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False).encode()).hexdigest()


def raw_terminal(path):
    terminal = None
    if not path.exists():
        return None
    for line in path.read_text().splitlines():
        receipt = json.loads(line)
        if 'data_utf8' not in receipt or receipt['data_utf8'] == '[DONE]':
            continue
        payload = json.loads(receipt['data_utf8'])
        if payload.get('stop') is True:
            terminal = payload
    return terminal


def write_csv(path, rows):
    if not rows:
        path.write_text('')
        return
    with path.open('w', newline='') as output:
        writer = csv.DictWriter(output, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def union_length(intervals):
    total = 0; end = None
    for start, finish in sorted(set(intervals)):
        if finish < start:
            raise ValueError('negative producer interval')
        if end is None or start >= end:
            total += finish-start
        elif finish > end:
            total += finish-end
        end = finish if end is None else max(end, finish)
    return total


def nearest_rank(values, quantile):
    """Descriptive empirical quantile; eight-request p95 is the maximum."""
    ordered = sorted(value for value in values if value is not None)
    return ordered[max(0, math.ceil(quantile*len(ordered))-1)] if ordered else None


def analyze(manifest_path, output, evidence_root=None):
    manifest = read(manifest_path)
    root = Path(evidence_root or manifest.get('workspace_root') or manifest.get('evidence_root', '.')).resolve()
    request_rows = []; pair_rows = []; attempt_rows = []; case_rows = []
    sessions = set(); identities = {}; all_intervals = []; current_intervals = []
    allocations = {}; provenance = []; queue_seconds = 0; queue_wait_seconds = 0
    for case in manifest['cases']:
        directory = root/case.get('directory', '.')
        study = root/case['study'] if 'study' in case else directory/'study'
        inventory_path = root/case['inspect'] if 'inspect' in case else directory/'inspect.json'
        report_path = root/case['report'] if 'report' in case else directory/'result.json'
        audit_path = root/case['raw_audit'] if 'raw_audit' in case else directory/'raw-audit.json'
        queue_path = root/case['queue_receipt'] if 'queue_receipt' in case else directory/'study.queue/receipt.json'
        inventory = read(inventory_path)
        config = read(study/'config.json'); workload = read(study/'workload.json')
        result = read(report_path); audit = read(audit_path)
        session = read(study/'session.json')
        if session['session_id'] in sessions:
            raise ValueError('same producer supplied twice')
        sessions.add(session['session_id'])
        if result['config_sha256'] != checksum(config) or result['workload_sha256'] != checksum(workload):
            raise ValueError('report does not bind producer inputs')
        if audit['config_sha256'] != result['config_sha256']:
            raise ValueError('raw audit belongs to another producer')
        if not inventory['inventory_complete']:
            raise ValueError('unreconciled producer cannot be finalized')
        generator = workload['generator']; recipe = config['recipe']
        allocation = recipe['allocation']; allocations[allocation['allocation_id']] = allocation
        attempts = sorted((read(p) for p in (study/'attempts').glob('*.json')),
                          key=lambda attempt: attempt['started_ns'])
        expected = {row['request_id']: row for row in workload['requests']}
        tables = {}; positions = {}; table_ids = {}
        for index, row in enumerate(workload['requests']):
            table = row['prompt'].split('\nEND\n', 1)[0]
            table_id = hashlib.sha256(table.encode()).hexdigest()
            table_ids[row['request_id']] = table_id
            positions[row['request_id']] = tables.get(table_id, 0)
            tables[table_id] = positions[row['request_id']]+1
        arm_requests = {}; cells = {}
        for attempt in attempts:
            aid = attempt['attempt_id']; raw = study/'raw'/aid
            tokenized = read(raw/'tokenized-inputs.json') if (raw/'tokenized-inputs.json').exists() else None
            interventions = read(raw/'prompt-interventions.json') if (raw/'prompt-interventions.json').exists() else {'requests':[]}
            by_intervention = {row['request_id']:row for row in interventions['requests']}
            indices = {row['request_id']:i for i,row in enumerate(workload['requests'])}
            resource = read(raw/'resource-observations.json') if (raw/'resource-observations.json').exists() else {}
            current_intervals.append((attempt['started_ns'], attempt['finished_ns']))
            all_intervals.append((attempt['started_ns'], attempt['finished_ns']))
            correct = 0; reused = 0; new = 0; predicted = 0
            observed_e2e = []; observed_ttft = []; observed_queue = []
            native_prompt_ms = []; native_generation_ms = []
            request_map = {row['request_id']:row for row in attempt['requests']}
            cells[(attempt['concurrency'],attempt['pair_index'],attempt['arm'])] = request_map
            for identifier, original in expected.items():
                row = request_map.get(identifier)
                success = bool(row and row['status']=='SUCCEEDED')
                quality = bool(success and row['output_text'].strip()==original['expected'])
                correct += quality
                terminal = raw_terminal(raw/(identifier+'.jsonl')) if row else None
                timing = terminal.get('timings', {}) if terminal else {}
                intervention = by_intervention.get(identifier, {})
                transformed = intervention.get('result', {})
                ids = tokenized['tokens'][indices[identifier]] if tokenized else None
                if success and (not timing or ids is None or timing['cache_n']+timing['prompt_n'] != len(ids)):
                    raise ValueError('successful raw input accounting unavailable or inconsistent')
                reused += timing.get('cache_n', 0); new += timing.get('prompt_n', 0)
                predicted += timing.get('predicted_n', 0)
                native_prompt_ms.append(timing.get('prompt_ms')); native_generation_ms.append(timing.get('predicted_ms'))
                e2e = row['completed_ns']-row['arrival_ns'] if row else None
                ttft = row['first_token_ns']-row['arrival_ns'] if row and row['first_token_ns'] is not None else None
                queue_wait = row['dispatch_ns']-row['arrival_ns'] if row and row['dispatch_ns'] is not None else None
                observed_e2e.append(e2e); observed_ttft.append(ttft); observed_queue.append(queue_wait)
                request_rows.append({'case_id':case['id'], 'model_profile':config['model']['profile_id'],
                    'mechanism':recipe['mechanism_id'], 'family':generator['family'],
                    'context_records':generator['context_records'], 'seed':generator['seed'],
                    'split':generator['split'], 'purpose':recipe['purpose'], 'attempt_id':aid,
                    'arm':attempt['arm'], 'pair_index':attempt['pair_index'], 'concurrency':attempt['concurrency'],
                    'request_id':identifier, 'table_sha256':table_ids[identifier],
                    'table_index':list(tables).index(table_ids[identifier]), 'within_table_position':positions[identifier],
                    'first_query_of_table':positions[identifier]==0, 'observed':row is not None,
                    'status':row['status'] if row else 'MISSING', 'correct':quality,
                    'expected':original['expected'], 'output':row['output_text'] if row else None,
                    'output_token_ids':json.dumps(row['output_token_ids']) if row else None,
                    'input_token_ids_sha256':checksum(ids) if ids is not None else None,
                    'input_tokens':len(ids) if ids is not None else None,
                    'native_reused_tokens':timing.get('cache_n'), 'native_new_tokens':timing.get('prompt_n'),
                    'native_prompt_ms':timing.get('prompt_ms'), 'native_generation_ms':timing.get('predicted_ms'),
                    'generated_tokens':row['generated_tokens'] if row else None,
                    'client_end_to_end_ns':e2e, 'client_queue_before_dispatch_ns':queue_wait,
                    'native_request_proxy_ns':row['completed_ns']-row['dispatch_ns'] if row and row['dispatch_ns'] is not None else None,
                    'client_ttft_ns':ttft,
                    'original_prompt_characters':len(original['prompt']),
                    'original_prompt_sha256':hashlib.sha256(original['prompt'].encode()).hexdigest(),
                    'transformed_prompt_characters':len(transformed['prompt']) if 'prompt' in transformed else None,
                    'intervention_duration_ns':intervention.get('duration_ns'),
                    'intervention_decision':transformed.get('decision')})
            phases = attempt['overhead_ns']
            dispatched = sorted((r for r in request_map.values() if r['dispatch_ns'] is not None),
                                key=lambda r:r['dispatch_ns'])
            intervals = [(r['dispatch_ns'],r['completed_ns']) for r in dispatched]
            client_in_flight = union_length(intervals)
            outside_in_flight = phases['service']-client_in_flight
            if outside_in_flight < 0:
                raise ValueError('client in-flight interval union exceeds recorded service envelope')
            between_requests = None
            if attempt['concurrency']==1:
                between_requests = sum(dispatched[i]['dispatch_ns']-dispatched[i-1]['completed_ns']
                                       for i in range(1,len(dispatched)))
                if any(dispatched[i]['dispatch_ns']<dispatched[i-1]['completed_ns'] for i in range(1,len(dispatched))):
                    raise ValueError('single-slot client requests overlap')
            record = {'case_id':case['id'], 'model_profile':config['model']['profile_id'],
                'mechanism':recipe['mechanism_id'], 'family':generator['family'],
                'context_records':generator['context_records'], 'purpose':recipe['purpose'],
                'attempt_id':aid, 'arm':attempt['arm'], 'pair_index':attempt['pair_index'],
                'status':attempt['status'], 'expected_requests':len(expected),
                'observed_requests':len(request_map), 'correct':correct, 'accuracy':correct/len(expected),
                'full_wall_ns':attempt['finished_ns']-attempt['started_ns'], 'service_ns':phases['service'],
                'preparation_ns':phases['cache_preparation'], 'verification_ns':phases['verification'],
                'load_ns':phases['load'], 'recovery_ns':phases['recovery'],
                'native_reused_tokens':reused, 'native_new_tokens':new, 'generated_tokens':predicted,
                'native_timing_request_count':sum(v is not None for v in native_prompt_ms),
                'native_prompt_ms_sum':float(sum(Decimal(str(v)) for v in native_prompt_ms)) if all(v is not None for v in native_prompt_ms) else None,
                'native_generation_ms_sum':float(sum(Decimal(str(v)) for v in native_generation_ms)) if all(v is not None for v in native_generation_ms) else None,
                'client_in_flight_interval_union_ns':client_in_flight,
                'service_outside_client_in_flight_intervals_ns':outside_in_flight,
                'between_request_completion_and_next_dispatch_ns':between_requests,
                'e2e_p50_ns':nearest_rank(observed_e2e, .5), 'e2e_p95_ns':nearest_rank(observed_e2e, .95),
                'e2e_max_ns':nearest_rank(observed_e2e, 1), 'ttft_p95_ns':nearest_rank(observed_ttft, .95),
                'client_queue_p95_ns':nearest_rank(observed_queue, .95),
                'non_success_requests':len(expected)-sum(row['status']=='SUCCEEDED' for row in request_map.values()),
                'host_load_before_after':json.dumps(attempt['environment'].get('load',{}).get('value')),
                'host_load_unit':attempt['environment'].get('load',{}).get('unit'),
                'sampled_aggregate_rss_bytes':resource.get('maximum_observed_aggregate_rss_bytes'),
                'server_vmhwm_bytes':resource.get('server_vmhwm_bytes')}
            attempt_rows.append(record); arm_requests.setdefault(attempt['arm'], []).append(record)
        for concurrency, pair, arm in sorted(cells):
            if arm != 'baseline': continue
            baseline = cells[(concurrency,pair,'baseline')]
            candidate = cells.get((concurrency,pair,'candidate'), {})
            classes = dict.fromkeys(['both_correct','baseline_only_correct','candidate_only_correct','both_wrong'], 0)
            token_changes = 0
            for identifier, original in expected.items():
                b = baseline.get(identifier); c = candidate.get(identifier)
                bc = bool(b and b['status']=='SUCCEEDED' and b['output_text'].strip()==original['expected'])
                cc = bool(c and c['status']=='SUCCEEDED' and c['output_text'].strip()==original['expected'])
                classes['both_correct' if bc and cc else 'baseline_only_correct' if bc else 'candidate_only_correct' if cc else 'both_wrong'] += 1
                token_changes += bool(b and c and b['output_token_ids'] != c['output_token_ids'])
            pair_rows.append({'case_id':case['id'], 'pair_index':pair, 'concurrency':concurrency,
                'offered_tasks':len(expected), **classes,
                'observed_either_answer_correct':len(expected)-classes['both_wrong'],
                'changed_output_token_sequences':token_changes,
                'official_campaign_eligible':result['eligible']})
        case_rows.append({'case_id':case['id'], 'model_profile':config['model']['profile_id'],
            'mechanism':recipe['mechanism_id'], 'family':generator['family'],
            'context_records':generator['context_records'], 'purpose':recipe['purpose'],
            'unique_tables':len(tables),
            'native_attempts':len(attempts), 'offered_requests':len(expected)*len(attempts),
            'observed_requests':sum(len(a['requests']) for a in attempts),
            'baseline_correct':sum(r['correct'] for r in arm_requests.get('baseline', [])),
            'baseline_denominator':sum(r['expected_requests'] for r in arm_requests.get('baseline', [])),
            'candidate_correct':sum(r['correct'] for r in arm_requests.get('candidate', [])),
            'candidate_denominator':sum(r['expected_requests'] for r in arm_requests.get('candidate', [])),
            'official_eligible':result['eligible'], 'measured_claim_eligible':result['measured_claim_eligible'],
            'official_reasons':json.dumps(result['ineligibility_reasons']), 'raw_audit_status':audit['status']})
        for setup in inventory['setup_accounting']['records']:
            identities.setdefault(checksum(setup), setup)
            all_intervals.append((setup['started_ns'], setup['finished_ns']))
        queue = read(queue_path)
        if queue['execution_started_ns'] is not None:
            queue_seconds += (queue['finished_ns']-queue['execution_started_ns'])/1e9
            queue_wait_seconds += (queue['execution_started_ns']-queue['started_ns'])/1e9
        provenance.append({'case_id':case['id'], 'session_id':session['session_id'],
            'config_sha256':checksum(config), 'workload_sha256':checksum(workload),
            'recipe_sha256':checksum(recipe), 'implementation_sha256':config['implementation_sha256'],
            'archive_sha256':queue['archive_sha256'], 'server_sha256':config['backend']['server_sha256'],
            'model_profile_sha256':config['model']['profile_sha256'],
            'template_sha256':config['tokenizer']['template_sha256'],
            'report_sha256':hashlib.sha256(report_path.read_bytes()).hexdigest()})
    if len(allocations) != 1:
        raise ValueError('systems package must retain one original allocation')
    table_cells = {}
    for row in request_rows:
        key = (row['case_id'], row['pair_index'], row['concurrency'], row['table_index'], row['table_sha256'])
        table_cells.setdefault(key, {}).setdefault(row['arm'], {})[row['request_id']] = row
    table_rows = []
    for key, arms in sorted(table_cells.items()):
        case_id, pair, concurrency, index, table_sha = key
        baseline = arms.get('baseline', {}); candidate = arms.get('candidate', {})
        identifiers = set(baseline) | set(candidate)
        record = dict(case_id=case_id, pair_index=pair, concurrency=concurrency,
                      table_index=index, table_sha256=table_sha, offered_tasks=len(identifiers))
        classes = dict.fromkeys(['both_correct','baseline_only_correct','candidate_only_correct','both_wrong'], 0)
        changes = 0
        for identifier in identifiers:
            b = baseline.get(identifier, {}); c = candidate.get(identifier, {})
            bc = b.get('correct', False); cc = c.get('correct', False)
            classes['both_correct' if bc and cc else 'baseline_only_correct' if bc else 'candidate_only_correct' if cc else 'both_wrong'] += 1
            changes += bool(b.get('observed') and c.get('observed') and b['output_token_ids'] != c['output_token_ids'])
        record.update(classes)
        record['observed_either_answer_correct'] = len(identifiers)-classes['both_wrong']
        record['changed_output_token_sequences'] = changes
        for arm, data in [('baseline', baseline), ('candidate', candidate)]:
            available = list(data.values())
            record[arm+'_observed_requests'] = sum(row['observed'] for row in available)
            record[arm+'_correct'] = sum(row['correct'] for row in available)
            for state, selected in [('first_use', [r for r in available if r['first_query_of_table']]),
                                    ('subsequent', [r for r in available if not r['first_query_of_table']]),
                                    ('all', available)]:
                values = [r['native_new_tokens'] for r in selected]
                record[arm+'_'+state+'_native_new_tokens'] = sum(values) if values and all(v is not None for v in values) else None
            values = [r['generated_tokens'] for r in available]
            record[arm+'_generated_tokens'] = sum(values) if values and all(v is not None for v in values) else None
        table_rows.append(record)
    allocation = next(iter(allocations.values()))
    cutoff = max(end for _,end in all_intervals)
    current = union_length(current_intervals); attributed = union_length(all_intervals)
    summary = {'classification':'Bounded CPU systems interaction study; no novelty or generalization guarantee',
        'cases':case_rows, 'provenance':provenance,
        'populations':{'distinct_original_table_prefixes_across_all_cases':len({r['table_sha256'] for r in request_rows}),
            'distinct_original_query_prompts_across_all_cases':len({r['original_prompt_sha256'] for r in request_rows}),
            'offered_native_request_records':len(request_rows),
            'scope':'Exact original table-prefix identity deduplicates matched-model populations; repeated queries and balanced pairs are not independent tables.'},
        'costs':{'original_allocation_id':allocation['allocation_id'],
            'original_deadline_ns':allocation['deadline_ns'], 'current_investigation_native_attempt_wall_ns':current,
            'all_retained_attributed_interval_union_ns':attributed,
            'historical_setup_prior_work_and_finalization_interval_union_ns':attributed-current,
            'full_allocation_span_through_last_retained_observation_ns':cutoff-allocation['started_ns'],
            'unattributed_original_allocation_interval_ns':cutoff-allocation['started_ns']-attributed,
            'queue_execution_elapsed_seconds_including_product_admission':queue_seconds,
            'queue_wait_seconds_before_product_execution':queue_wait_seconds,
            'unique_setup_records':len(identities),
            'scope':'Interval union deduplicates inherited ancestors and current attempts; per-study allocation spans are never summed. Unattributed intervals may include coordination, idle time or other work absent from retained setup records; they are not a measured idle-time quantity.'},
        'limits':{'energy':'NOT_MEASURED', 'thermal':'NOT_MEASURED',
            'cpu_time':'No per-phase CPU-time counters are retained by this runner; host load averages are not CPU utilization or energy.',
            'rss':'Sampled coordinator/server aggregate and server VmHWM, not a continuous host peak',
            'uncertainty':'Shared-table queries are dependent; pair ranges are descriptive, not confidence intervals',
            'tail_definition':'Nearest-rank empirical quantiles over observed requests; p95 equals the maximum for eight requests. Missing requests remain counted as non-success, without fabricated timings.',
            'either_answer_correct':'Observed paired-output upper bound only; it consumes knowledge of both outputs and ground truth, and is not a deployable oracle, measured controller, or free inference policy.',
            'timing_decomposition':'Native prompt/generation durations, client dispatch-to-completion interval union, and remaining service-envelope time are distinct measurements. Outside-in-flight time includes coordination/monitoring/checkpoint gaps and does not identify their individual causes. These are wall intervals, not CPU or energy measurements.',
            'comparison_ratios':'Only official quality-qualified campaign outputs may support efficiency ratios; this table emits none'}}
    output.mkdir(parents=True, exist_ok=True)
    for name, rows in [('requests',request_rows),('pairs',pair_rows),('attempts',attempt_rows),('cases',case_rows),('tables',table_rows)]:
        write_csv(output/(name+'.csv'), rows)
    (output/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path); parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--evidence-root', type=Path,
                        help='Root for explicit manifest paths; supports relocated exported investigation packages')
    args = parser.parse_args()
    print(json.dumps(analyze(args.manifest, args.output, args.evidence_root), indent=2))
