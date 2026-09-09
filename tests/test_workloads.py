"""Controls for v2 recipe identity and offered arrival semantics."""
import copy
import json
import math
import unittest
from collections import Counter

from lean_model_lab.contracts import ContractError, canonical_bytes, make_workload, validate_workload
from lean_model_lab.workloads import MAX_DEADLINE_NS, MAX_NS, make_workload_v2, validate_workload_v2


class WorkloadV2Tests(unittest.TestCase):
    def test_default_reproduces_original_population_without_changing_v1(self):
        old = make_workload()
        new = make_workload_v2()
        self.assertEqual(new['requests'], old['requests'])
        self.assertEqual(new['quality'], old['quality'])
        self.assertEqual(new['sampling'], old['sampling'])
        self.assertEqual(new['generator']['max_queue_requests'], 128)
        self.assertIs(validate_workload(old), old)
        self.assertIs(validate_workload_v2(new), new)

    def test_recipe_json_roundtrip_and_seed_reproduction(self):
        original = make_workload_v2(request_count=20, seed=17, max_output_tokens=64,
                                    max_queue_requests=3, request_deadline_ns=900,
                                    concurrency_modes=(1, 2, 4, 8))
        restored = json.loads(canonical_bytes(original))
        self.assertEqual(canonical_bytes(make_workload_v2(**restored['generator'])), canonical_bytes(original))
        self.assertIs(validate_workload_v2(restored), restored)
        self.assertNotEqual(original['requests'], make_workload_v2(request_count=20, seed=18)['requests'])

    def test_population_boundaries_and_balanced_strata(self):
        for count in (4, 12, 128, 1024):
            with self.subTest(count=count):
                value = make_workload_v2(request_count=count, max_output_tokens=128, seed=2**32-1)
                validate_workload_v2(value)
                self.assertEqual(len(value['requests']), count)
                self.assertEqual(len({r['request_id'] for r in value['requests']}), count)
                self.assertEqual(Counter(r['stratum'] for r in value['requests']),
                                 {n: count//4 for n in (16, 64, 128, 256)})
                self.assertTrue(all(r['arrival_offset_ns'] == 0 for r in value['requests']))
                self.assertEqual(value['max_queue_requests'], count)

    def test_paced_and_burst_arrivals_are_relative(self):
        for mode, burst, expected in (
            ('paced', 8, [0, 7, 14, 21, 28, 35, 42, 49]),
            ('burst', 3, [0, 0, 0, 7, 7, 7, 14, 14]),
            ('burst', 1, [0, 7, 14, 21, 28, 35, 42, 49]),
            ('burst', 8, [0]*8),
        ):
            with self.subTest(mode=mode, burst=burst):
                value = make_workload_v2(request_count=8, arrival_mode=mode, interval_ns=7,
                                         burst_size=burst, request_deadline_ns=MAX_DEADLINE_NS)
                self.assertEqual([r['arrival_offset_ns'] for r in value['requests']], expected)
                self.assertIs(validate_workload_v2(value), value)

    def test_numeric_parameters_reject_bool_float_nonfinite_and_wrong_types(self):
        parameters = ('request_count', 'seed', 'max_output_tokens', 'interval_ns',
                      'burst_size', 'max_queue_requests', 'request_deadline_ns')
        for field in parameters:
            for bad in (True, False, 1.0, math.nan, math.inf, -math.inf, '1', [], {}):
                with self.subTest(field=field, value=repr(bad)):
                    with self.assertRaises(ContractError):
                        make_workload_v2(**{field: bad})

    def test_concurrency_modes_require_bounded_sorted_unique_integers(self):
        for modes in ((1,), [8], (1, 2, 4, 8)):
            with self.subTest(modes=modes):
                value = make_workload_v2(concurrency_modes=modes)
                self.assertEqual(value['concurrency_modes'], list(modes))
                self.assertEqual(value['generator']['concurrency_modes'], list(modes))
                self.assertIsNot(value['generator']['concurrency_modes'], value['concurrency_modes'])
                validate_workload_v2(value)
        for modes in (None, 1, '1', {}, set(), [], [1, 2, 3, 4, 5], [1, 1], [4, 1],
                      [0], [9], [-1], [True], [1.0], [math.nan], [math.inf], ['1'], [[]]):
            with self.subTest(modes=repr(modes)), self.assertRaises(ContractError):
                make_workload_v2(concurrency_modes=modes)

    def test_numeric_bounds_and_arrival_overflow(self):
        bad_recipes = [
            {'request_count': n} for n in (0, 3, 5, 1025, 1028)
        ] + [
            {field: n} for field, values in (
                ('seed', (0, -1, 2**32)), ('max_output_tokens', (0, 31, 129)),
                ('interval_ns', (-1, MAX_NS+1)), ('burst_size', (0, -1, 1025)),
                ('max_queue_requests', (0, -1, 129)),
                ('request_deadline_ns', (0, -1, MAX_DEADLINE_NS+1)),
            ) for n in values
        ] + [
            {'arrival_mode': 'simultaneous', 'interval_ns': 1},
            {'arrival_mode': 'paced'}, {'arrival_mode': 'burst'},
            {'arrival_mode': 'burst', 'interval_ns': 1, 'burst_size': 129},
            {'arrival_mode': 'paced', 'interval_ns': MAX_NS},
            {'arrival_mode': 'burst', 'interval_ns': MAX_NS, 'burst_size': 8},
        ]
        for recipe in bad_recipes:
            with self.subTest(recipe=recipe), self.assertRaises(ContractError):
                make_workload_v2(**recipe)
        value = make_workload_v2(request_count=4, arrival_mode='paced', interval_ns=MAX_NS//3)
        validate_workload_v2(value)

    def test_bad_modes_and_required_numeric_none(self):
        for mode in ('', 'finite_batch_all_at_zero', 'PACED', 0, True, [], {}, None):
            with self.subTest(mode=mode), self.assertRaises(ContractError):
                make_workload_v2(arrival_mode=mode)
        for field in ('request_count', 'seed', 'max_output_tokens', 'interval_ns', 'burst_size'):
            with self.subTest(field=field), self.assertRaises(ContractError):
                make_workload_v2(**{field: None})

    def test_mutated_population_controls_and_structure_fail_closed(self):
        mutations = [
            lambda w: w.update(schema_version=True),
            lambda w: w.update(workload_id='synthetic-key-copy-v1'),
            lambda w: w.update(extra='unexpected'),
            lambda w: w['generator'].update(extra=1),
            lambda w: w['generator'].pop('seed'),
            lambda w: w['generator'].update(max_queue_requests=None),
            lambda w: w['generator'].update(seed=False),
            lambda w: w['generator'].update(concurrency_modes=(1, 4)),
            lambda w: w['generator'].update(request_count=4),
            lambda w: w['requests'].pop(),
            lambda w: w['requests'].reverse(),
            lambda w: w['requests'][0].update(extra=1),
            lambda w: w['requests'][0].update(prompt='private replacement'),
            lambda w: w['requests'][0].update(expected='XXXXX'),
            lambda w: w['requests'][0].update(arrival_offset_ns=1),
            lambda w: w['requests'][0].update(arrival_offset_ns=False),
            lambda w: w['requests'][0].update(stratum=64),
            lambda w: w['requests'][1].update(request_id='r000'),
            lambda w: w['quality'].update(minimum_accuracy=0.5),
            lambda w: w['quality'].update(minimum_accuracy=math.nan),
            lambda w: w['quality'].update(require_token_parity=False),
            lambda w: w['sampling'].update(allow_eos=False),
            lambda w: w['sampling'].update(stop=['stop']),
            lambda w: w['sampling'].update(stop=()),
            lambda w: w['sampling'].update(temperature=True),
            lambda w: w.update(max_output_tokens=64),
            lambda w: w.update(max_queue_requests=1),
            lambda w: w.update(request_deadline_ns=1),
            lambda w: w.update(concurrency_modes=(1, 4)),
            lambda w: w.update(concurrency_modes=[1]),
            lambda w: w.update(requests=tuple(w['requests'])),
        ]
        for mutate in mutations:
            value = copy.deepcopy(make_workload_v2())
            mutate(value)
            with self.subTest(value=str(value)[:100]), self.assertRaises(ContractError):
                validate_workload_v2(value)
        for bad in (None, [], {}, True, 'workload'):
            with self.subTest(value=bad), self.assertRaises(ContractError):
                validate_workload_v2(bad)


if __name__ == '__main__':
    unittest.main()
