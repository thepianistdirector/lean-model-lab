"""Synthetic evaluator controls; no model execution or measured claims."""
import copy
import math
import unittest

from lean_model_lab.allocation import MAXIMUM
from lean_model_lab.config import make_config_v2
from lean_model_lab.contracts import ContractError, digest
from lean_model_lab.evidence import EvidenceError, OVERHEAD_KEYS
from lean_model_lab.evidence_v2 import (evaluate_campaign_v2, summarize_attempt_v2,
                                        validate_attempt_v2)
from lean_model_lab.recipes import make_recipe, schedule
from lean_model_lab.workloads import make_workload_v2


def fixture(*, count=128, modes=(1, 4), pairs=2, purpose='MEASUREMENT',
            ttft_slo_ns=1_000_000, end_to_end_slo_ns=2_000_000, **workload_args):
    workload = make_workload_v2(request_count=count, concurrency_modes=modes, **workload_args)
    allocation = {
        'schema_version': 2, 'allocation_id': 'evaluator-unit-test', 'approved': True,
        'approval_reference': 'synthetic test fixture; no inference authorization',
        'observed_utc': '2026-09-08', 'boot_id': 'TEST_FIXTURE', 'started_ns': 1,
        'deadline_ns': 1 + MAXIMUM['full_wall_seconds'] * 10**9,
        'limits': dict(MAXIMUM), 'scope': 'model-free evaluator fixture only',
    }
    recipe = make_recipe(model_profile_id='qwen2.5-0.5b-instruct-fp16-v1', workload=workload,
                         allocation=allocation, pair_count=pairs, purpose=purpose,
                         ttft_slo_ns=ttft_slo_ns, end_to_end_slo_ns=end_to_end_slo_ns)
    config = make_config_v2(recipe=recipe, server_sha256='a' * 64, evidence_class='TEST_FIXTURE',
                            hardware={'platform': 'fixture', 'cpu': 'fixture'},
                            implementation_sha256='b' * 64)
    return workload, config


def identity(config, workload):
    return {'config': config, 'config_sha256': digest(config), 'workload_sha256': digest(workload)}


def make_attempt(workload, config, *, arm='baseline', concurrency=None, pair_index=0,
                 started_ns=1000, duration_ns=100):
    if concurrency is None:
        concurrency = config['evaluation']['concurrency_modes'][0]
    service_start = started_ns + 1000
    lanes = [service_start] * concurrency
    records = []
    for index, request in enumerate(workload['requests']):
        lane = index % concurrency
        arrival = service_start + request['arrival_offset_ns']
        admitted = max(arrival, lanes[lane])
        first = admitted + duration_ns // 2
        tokens = [ord(letter) for letter in request['expected']]
        completion = admitted + duration_ns
        lanes[lane] = completion
        records.append({
            'request_id': request['request_id'], 'arrival_ns': arrival, 'admitted_ns': admitted,
            'dispatch_ns': admitted + 1, 'first_token_ns': first, 'completed_ns': completion,
            'token_events': [{'observed_ns': first, 'token_ids': tokens[:2]},
                             {'observed_ns': first + 1, 'token_ids': tokens[2:]}],
            'output_token_ids': tokens, 'output_text': request['expected'], 'finish_reason': 'eos',
            'status': 'SUCCEEDED', 'prompt_tokens': request['stratum'] + 30,
            'generated_tokens': len(tokens), 'engine_start_ns': None,
        })
    service_ns = max(row['completed_ns'] for row in records) - service_start
    overhead = {key: 0 for key in OVERHEAD_KEYS}
    overhead.update(startup=100, verification=200, load=300, warmup=400,
                    service=service_ns, evaluation=50, reporting=50)
    unavailable = {'status': 'UNAVAILABLE', 'scope': 'no probe in synthetic fixture',
                   'value': None, 'unit': 'unavailable'}
    return {
        'schema_version': 2, 'evidence_class': 'TEST_FIXTURE',
        'attempt_id': f'fixture-{concurrency}-{pair_index}-{arm}-{started_ns}',
        'config_sha256': digest(config), 'workload_sha256': digest(workload),
        'arm': arm, 'concurrency': concurrency, 'pair_index': pair_index, 'started_ns': started_ns,
        'service_started_ns': service_start, 'finished_ns': service_start + service_ns + 100,
        'status': 'COMPLETED', 'requests': records, 'overhead_ns': overhead,
        'environment': {'observer': 'unittest', 'version': '0.4.0-dev', 'platform': 'fixture',
                        'cpu': 'fixture', **{key: dict(unavailable) for key in ('load', 'thermal', 'memory', 'energy')}},
    }


def make_campaign(workload, config, candidate_duration_ns=80):
    result = []
    started = 1000
    for concurrency, pair, arm in schedule(config):
        attempt = make_attempt(workload, config, arm=arm, concurrency=concurrency, pair_index=pair,
                               started_ns=started, duration_ns=candidate_duration_ns if arm == 'candidate' else 100)
        result.append(attempt)
        started = attempt['finished_ns'] + 100
    return result


def local_decision(request, *, status, deadline_ns=None):
    request.update(status=status, finish_reason='queue_full' if status == 'REJECTED' else 'deadline',
                   admitted_ns=None, dispatch_ns=None, first_token_ns=None, output_text='',
                   output_token_ids=[], token_events=[], generated_tokens=0, engine_start_ns=None,
                   completed_ns=request['arrival_ns'] + (deadline_ns if status == 'EXPIRED' else 0))


class EvidenceV2Tests(unittest.TestCase):
    def setUp(self):
        self.workload, self.config = fixture()
        self.attempt = make_attempt(self.workload, self.config)

    def validate(self, attempt=None, workload=None, config=None):
        workload = self.workload if workload is None else workload
        config = self.config if config is None else config
        return validate_attempt_v2(self.attempt if attempt is None else attempt, workload,
                                    **identity(config, workload))

    def summary(self, attempt=None, workload=None, config=None):
        workload = self.workload if workload is None else workload
        config = self.config if config is None else config
        return summarize_attempt_v2(self.attempt if attempt is None else attempt, workload,
                                     **identity(config, workload))

    def evaluate(self, attempts=None, workload=None, config=None):
        workload = self.workload if workload is None else workload
        config = self.config if config is None else config
        return evaluate_campaign_v2(make_campaign(workload, config) if attempts is None else attempts,
                                      workload, **identity(config, workload))

    def assert_all_ratios_null(self, result):
        self.assertFalse(result['eligible'])
        for group in result['concurrency_groups'].values():
            self.assertFalse(group['eligible'])
            self.assertEqual(group['finding'], 'INELIGIBLE')
            self.assertEqual(group['pair_count'], 0)
            self.assertIsNone(group['throughput_ratio_median'])
            self.assertIsNone(group['throughput_ratio_range'])
            for pair in group['pairs']:
                self.assertFalse(pair['eligible'])
                self.assertIsNone(pair['throughput_candidate_over_baseline'])
                for field in ('end_to_end_tail_candidate_over_baseline', 'ttft_tail_candidate_over_baseline'):
                    self.assertEqual(pair[field], {'p95': None, 'p99': None})

    def test_balanced_fixture_calculates_descriptive_ratios_without_measured_claim(self):
        result = self.evaluate()
        self.assertTrue(result['eligible'])
        self.assertFalse(result['measured_claim_eligible'])
        self.assertEqual(result['finding'], 'TEST_FIXTURE_ONLY')
        self.assertEqual(result['evaluator_version'], '0.4.0-dev')
        self.assertEqual(result['accounting']['attempt_count'], 8)
        self.assertEqual(result['accounting']['expected_requests_across_attempts'], 1024)
        for group in result['concurrency_groups'].values():
            self.assertEqual(group['pair_count'], 2)
            self.assertEqual(group['throughput_ratio_range'], [1.25, 1.25])
            self.assertEqual(group['finding'], 'PRACTICAL_GAIN_IN_ALL_PAIRS')

    def test_population_output_and_schedule_bounds_are_recipe_driven(self):
        for count, modes, pairs in ((132, (2,), 4), (1024, (8,), 2), (128, (1, 2, 4, 8), 8)):
            with self.subTest(count=count, modes=modes, pairs=pairs):
                workload, config = fixture(count=count, modes=modes, pairs=pairs, max_output_tokens=128)
                result = self.evaluate(workload=workload, config=config)
                self.assertTrue(result['eligible'])
                self.assertEqual(result['accounting']['expected_requests_across_attempts'], count * len(modes) * pairs * 2)
                self.assertEqual(set(result['concurrency_groups']), {str(mode) for mode in modes})
                for group in result['concurrency_groups'].values(): self.assertEqual(group['pair_count'], pairs)
                self.assertEqual(result['attempts'][0]['strata']['16']['expected_count'], count // 4)

    def test_odd_unbound_and_changed_quality_recipes_fail_closed(self):
        with self.assertRaises(ContractError): fixture(pairs=3)
        with self.assertRaises(ContractError): fixture(count=4)
        for mutate in (
            lambda c: c['recipe']['evaluation'].update(pairs_per_concurrency=3, pair_order=['AB', 'BA', 'AB']),
            lambda c: c['evaluation'].update(accuracy_minimum=0.5),
            lambda c: c['recipe']['evaluation'].update(output_token_parity=False),
            lambda c: c.update(recipe_sha256='c' * 64),
            lambda c: c['recipe']['workload_generator'].update(seed=19),
            lambda c: c['model'].update(profile_sha256='c' * 64),
        ):
            config = copy.deepcopy(self.config)
            mutate(config)
            with self.subTest(config=str(config)[:50]), self.assertRaises(EvidenceError):
                self.evaluate(config=config)
        workload = copy.deepcopy(self.workload)
        workload['quality']['minimum_accuracy'] = 0.5
        with self.assertRaises(EvidenceError): self.validate(workload=workload)
        other_workload = make_workload_v2(seed=19)
        with self.assertRaisesRegex(EvidenceError, 'not bound'): self.validate(workload=other_workload)

    def test_attempt_identity_schema_fields_and_probes_are_strict(self):
        mutations = [
            lambda a: a.update(schema_version=1), lambda a: a.update(schema_version=True),
            lambda a: a.update(concurrency=True), lambda a: a.update(concurrency=2),
            lambda a: a.update(pair_index=2), lambda a: a.update(extra=1),
            lambda a: a.update(evidence_class='MEASURED'),
            lambda a: a.update(config_sha256='c' * 64), lambda a: a.update(workload_sha256='c' * 64),
            lambda a: a['environment'].update(cpu='other'),
            lambda a: a['environment']['energy'].update(value=10),
            lambda a: a['environment']['memory'].update(status='MEASURED', value=math.nan),
            lambda a: a['requests'][0].update(extra=1), lambda a: a['requests'][0].pop('engine_start_ns'),
            lambda a: a['requests'][0].update(engine_start_ns=a['service_started_ns']),
            lambda a: a['overhead_ns'].update(service=1),
            lambda a: a['overhead_ns'].update(load=a['finished_ns']),
        ]
        for mutate in mutations:
            attempt = copy.deepcopy(self.attempt)
            mutate(attempt)
            with self.subTest(mutate=mutate), self.assertRaises(EvidenceError): self.validate(attempt)

    def test_numeric_timestamps_and_tokens_reject_bool_nonfinite_and_bad_order(self):
        for bad in (None, True, -1, 2.0, '2', math.nan, math.inf):
            attempt = copy.deepcopy(self.attempt)
            attempt['requests'][0]['dispatch_ns'] = bad
            with self.subTest(value=bad), self.assertRaises(EvidenceError): self.validate(attempt)
        for mutate in (
            lambda r: r.update(arrival_ns=r['arrival_ns'] + 1),
            lambda r: r.update(first_token_ns=r['first_token_ns'] - 1),
            lambda r: r.update(generated_tokens=None),
            lambda r: r.update(generated_tokens=0),
            lambda r: r.update(output_token_ids=[1]*4097),
            lambda r: r['token_events'][0].update(token_ids=[True]),
            lambda r: r['token_events'].reverse(),
            lambda r: r.update(status='FAILED'),
        ):
            attempt = copy.deepcopy(self.attempt)
            mutate(attempt['requests'][0])
            with self.subTest(mutate=mutate), self.assertRaises(EvidenceError): self.validate(attempt)

    def test_duplicate_missing_unknown_requests_and_concurrency_lanes(self):
        for mutate in (
            lambda a: a['requests'].append(copy.deepcopy(a['requests'][0])),
            lambda a: a['requests'].pop(),
            lambda a: a['requests'][0].update(request_id='foreign'),
        ):
            attempt = copy.deepcopy(self.attempt)
            mutate(attempt)
            with self.subTest(mutate=mutate), self.assertRaises(EvidenceError): self.validate(attempt)
        attempt = make_attempt(self.workload, self.config, concurrency=4)
        attempt['concurrency'] = 1
        with self.assertRaisesRegex(EvidenceError, 'in-flight'): self.validate(attempt)
        attempt = make_attempt(self.workload, self.config, concurrency=4)
        first, fifth = attempt['requests'][0], attempt['requests'][4]
        first['request_id'], fifth['request_id'] = fifth['request_id'], first['request_id']
        with self.assertRaisesRegex(EvidenceError, 'lane assignment'): self.validate(attempt)

    def test_incomplete_or_retried_campaign_never_leaks_healthy_subgroup_ratios(self):
        attempts = make_campaign(self.workload, self.config)
        self.assert_all_ratios_null(self.evaluate(attempts[:-1]))
        retry = make_attempt(self.workload, self.config, started_ns=attempts[-1]['finished_ns']+100)
        result = self.evaluate(attempts + [retry])
        self.assert_all_ratios_null(result)
        self.assertEqual(result['accounting']['attempt_count'], 9)
        self.assertEqual(result['accounting']['observed_requests'], 9*128)
        attempts[0]['status'] = 'INTERRUPTED'
        attempts[0]['requests'] = attempts[0]['requests'][:64]
        result = self.evaluate(attempts)
        self.assert_all_ratios_null(result)
        self.assertEqual(result['accounting']['missing_requests'], 64)
        self.assertEqual(result['attempts'][0]['quality_denominator'], 128)
        self.assertEqual(result['attempts'][0]['quality_accuracy'], 0.5)

    def test_attempt_duplicates_and_overlap_fail_but_array_order_is_irrelevant(self):
        attempts = make_campaign(self.workload, self.config)
        attempts.reverse()
        self.assertTrue(self.evaluate(attempts)['eligible'])
        attempts[1]['attempt_id'] = attempts[0]['attempt_id']
        with self.assertRaisesRegex(EvidenceError, 'duplicate attempt ID'): self.evaluate(attempts)
        attempts = make_campaign(self.workload, self.config)
        attempts[1] = make_attempt(self.workload, self.config, arm='candidate', started_ns=attempts[0]['started_ns'])
        with self.assertRaisesRegex(EvidenceError, 'overlap'): self.evaluate(attempts)

    def test_global_schedule_order_is_checked_across_concurrency_groups(self):
        attempts = make_campaign(self.workload, self.config)
        # Each concurrency retains its own AB/BA order, but the registered groups are reversed.
        starts = 1000
        reordered = []
        for a in attempts[4:] + attempts[:4]:
            b = make_attempt(self.workload, self.config, arm=a['arm'], concurrency=a['concurrency'],
                             pair_index=a['pair_index'], started_ns=starts)
            reordered.append(b); starts = b['finished_ns'] + 100
        result = self.evaluate(reordered)
        self.assertIn('registered_schedule_order_invalid', result['ineligibility_reasons'])
        self.assert_all_ratios_null(result)

    def test_token_and_prompt_count_parity_gate_entire_campaign(self):
        for kind in ('token', 'generated', 'prompt', 'matching_pair_prompt'):
            attempts = make_campaign(self.workload, self.config)
            request = attempts[1]['requests'][0]
            if kind == 'token':
                request['output_token_ids'][0] = 999
                request['token_events'][0]['token_ids'][0] = 999
            elif kind == 'generated': request['generated_tokens'] += 1
            elif kind == 'prompt': request['prompt_tokens'] += 1
            else:
                for a in attempts[:2]: a['requests'][0]['prompt_tokens'] += 1
            result = self.evaluate(attempts)
            with self.subTest(kind=kind):
                self.assertTrue(result['attempts'][1]['quality_pass'])
                self.assert_all_ratios_null(result)

    def test_exact_quality_failures_limits_and_output_budget_are_adverse(self):
        workload, config = fixture(max_output_tokens=64)
        for kind in ('wrong', 'FAILED', 'CANCELLED', 'limit', 'over_budget'):
            attempts = make_campaign(workload, config)
            if kind == 'wrong':
                for row in attempts[-1]['requests'][:7]: row['output_text'] = 'wrong'
            else:
                row = attempts[-1]['requests'][0]
                if kind in ('FAILED', 'CANCELLED'):
                    row.update(status=kind, finish_reason='error' if kind == 'FAILED' else 'cancelled', generated_tokens=None)
                elif kind == 'limit': row.update(finish_reason='limit', generated_tokens=64)
                else: row['generated_tokens'] = 65
            result = self.evaluate(attempts, workload, config)
            with self.subTest(kind=kind): self.assert_all_ratios_null(result)
        attempts = make_campaign(workload, config)
        for a in attempts:
            a['requests'][0]['generated_tokens'] = 64  # Counter may exceed visible IDs and is within this recipe.
        self.assertTrue(self.evaluate(attempts, workload, config)['eligible'])

    def test_local_queue_decisions_have_zero_engine_work_and_full_denominators(self):
        workload, config = fixture(count=4, modes=(1,), purpose='DEVELOPMENT', request_deadline_ns=100,
                                   ttft_slo_ns=400, end_to_end_slo_ns=400)
        attempt = make_attempt(workload, config)
        local_decision(attempt['requests'][0], status='REJECTED')
        local_decision(attempt['requests'][1], status='EXPIRED', deadline_ns=100)
        attempt['requests'][3].update(status='FAILED', finish_reason='error', generated_tokens=None)
        self.validate(attempt, workload, config)
        result = self.summary(attempt, workload, config)
        serving = result['serving']
        for field, expected in {'offered_requests':4, 'observed_requests':4, 'admitted_requests':2,
                                'completed_requests':1, 'rejected_requests':1, 'expired_requests':1,
                                'failed_requests':1, 'slo_qualified_requests':1,
                                'generated_tokens_unknown_requests':1}.items():
            self.assertEqual(serving[field], expected, field)
        self.assertEqual(serving['slo_qualified_fraction'], 0.25)
        self.assertEqual(serving['goodput_per_second'], 1e9 / 400)
        self.assertEqual(result['quality_denominator'], 4)
        self.assertEqual(result['latency']['client_queue_ns']['count'], 2)
        self.assertEqual(result['latency']['client_end_to_end_ns']['count'], 4)
        self.assertIsNone(serving['offered_requests_per_second'])
        attempt['status'] = 'INTERRUPTED'; attempt['requests'].pop()
        result = self.summary(attempt, workload, config)
        self.assertEqual(result['serving']['missing_requests'], 1)
        self.assertEqual(result['serving']['slo_qualified_fraction'], 0.25)

    def test_rejected_or_expired_request_invalidates_otherwise_complete_measurement(self):
        workload, config = fixture(request_deadline_ns=100)
        for status in ('REJECTED', 'EXPIRED'):
            attempts = make_campaign(workload, config)
            local_decision(attempts[-1]['requests'][0], status=status, deadline_ns=100)
            result = self.evaluate(attempts, workload, config)
            with self.subTest(status=status):
                self.assertEqual(result['accounting']['observed_requests'], 8*128)
                self.assert_all_ratios_null(result)

    def test_local_decisions_reject_fabricated_dispatch_output_and_deadlines(self):
        workload, config = fixture(request_deadline_ns=100)
        valid = make_attempt(workload, config)
        local_decision(valid['requests'][0], status='EXPIRED', deadline_ns=100)
        mutations = [
            lambda r: r.update(admitted_ns=r['arrival_ns']),
            lambda r: r.update(dispatch_ns=r['arrival_ns']),
            lambda r: r.update(first_token_ns=r['arrival_ns']),
            lambda r: r.update(generated_tokens=None), lambda r: r.update(generated_tokens=False),
            lambda r: r.update(generated_tokens=1), lambda r: r.update(output_text='x'),
            lambda r: r.update(output_token_ids=[0]), lambda r: r.update(token_events=[{}]),
            lambda r: r.update(completed_ns=r['arrival_ns']+99),
            lambda r: r.update(engine_start_ns=r['arrival_ns']),
            lambda r: r.update(finish_reason='queue_full'), lambda r: r.update(prompt_tokens=0),
        ]
        for mutate in mutations:
            attempt = copy.deepcopy(valid); mutate(attempt['requests'][0])
            with self.subTest(mutate=mutate), self.assertRaises(EvidenceError):
                self.validate(attempt, workload, config)
        without_deadline = make_attempt(self.workload, self.config)
        local_decision(without_deadline['requests'][0], status='EXPIRED', deadline_ns=100)
        with self.assertRaisesRegex(EvidenceError, 'declared request deadline'): self.validate(without_deadline)

    def test_goodput_requires_both_slos_quality_and_observed_ttft(self):
        workload, config = fixture(modes=(1,), ttft_slo_ns=50, end_to_end_slo_ns=100)
        attempt = make_attempt(workload, config)
        result = self.summary(attempt, workload, config)
        self.assertEqual(result['quality_accuracy'], 1)
        self.assertEqual(result['serving']['slo_qualified_requests'], 1)
        self.assertEqual(result['serving']['slo_qualified_fraction'], 1/128)
        attempt['requests'][0]['output_text'] = 'wrong'
        self.assertEqual(self.summary(attempt, workload, config)['serving']['slo_qualified_requests'], 0)
        attempt['requests'][0].update(output_token_ids=[], token_events=[], output_text='',
                                      generated_tokens=0, first_token_ns=None)
        result = self.summary(attempt, workload, config)
        self.assertEqual(result['serving']['ttft_unobserved_admitted_requests'], 1)
        self.assertEqual(result['serving']['slo_qualified_requests'], 0)

    def test_paced_offered_rate_uses_declared_span_and_service_rates_keep_idle(self):
        workload, config = fixture(arrival_mode='paced', interval_ns=200, ttft_slo_ns=50, end_to_end_slo_ns=100)
        attempt = make_attempt(workload, config)
        result = self.summary(attempt, workload, config)
        serving = result['serving']
        self.assertEqual(serving['offered_arrival_span_ns'], 127*200)
        self.assertEqual(serving['offered_requests_per_second'], 128*1e9/(127*200))
        self.assertEqual(serving['service_envelope_ns'], 127*200+100)
        self.assertEqual(serving['completed_requests_per_second'], 128*1e9/(127*200+100))
        self.assertEqual(serving['slo_qualified_requests'], 128)

    def test_development_population_never_becomes_an_efficiency_claim(self):
        for count in (4, 128):
            workload, config = fixture(count=count, purpose='DEVELOPMENT')
            result = self.evaluate(workload=workload, config=config)
            with self.subTest(count=count):
                self.assert_all_ratios_null(result)
                self.assertFalse(result['measured_claim_eligible'])
                self.assertIn('development_recipe_not_measurement', result['ineligibility_reasons'])
                self.assertEqual(result['attempts'][0]['quality_denominator'], count)

    def test_zero_output_and_unavailable_telemetry_are_not_invented(self):
        for row in self.attempt['requests']:
            row.update(output_token_ids=[], token_events=[], output_text='', first_token_ns=None, generated_tokens=0)
        result = self.summary()
        self.assertEqual(result['latency']['client_ttft_ns']['count'], 0)
        self.assertIsNone(result['latency']['client_ttft_ns']['p99'])
        self.assertEqual(result['serving']['goodput_per_second'], 0)
        self.assertEqual(result['serving']['ttft_unobserved_admitted_requests'], 128)
        for field in ('inter_token_latency_ns', 'dispatch_to_engine_start_ns', 'accelerator_memory_bytes'):
            self.assertEqual(result[field]['status'], 'UNAVAILABLE')

    def test_equal_and_slower_candidates_keep_non_gain_findings(self):
        for duration, finding in ((100, 'NO_DEMONSTRATED_PRACTICAL_GAIN'), (120, 'TAIL_REGRESSION')):
            result = self.evaluate(make_campaign(self.workload, self.config, candidate_duration_ns=duration))
            with self.subTest(duration=duration):
                for group in result['concurrency_groups'].values(): self.assertEqual(group['finding'], finding)

    def test_outside_allocation_retains_cost_but_invalidates_claim(self):
        attempt = make_attempt(self.workload, self.config,
                               started_ns=self.config['recipe']['allocation']['deadline_ns']+1)
        result = self.summary(attempt)
        self.assertFalse(result['eligible'])
        self.assertIn('attempt_outside_registered_allocation', result['ineligibility_reasons'])
        self.assertGreater(result['full_wall_ns'], 0)


if __name__ == '__main__':
    unittest.main()
