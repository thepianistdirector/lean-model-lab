"""Deterministic controller controls; labels and request costs are TEST_FIXTURE."""
import copy
import inspect
import json
import unittest
from unittest.mock import patch

from lean_model_lab.acceptance_controller import (extract_features, fit_controller,
                                                predict, validate_controller)
from lean_model_lab.context_slice import prompt_lines, transform_prompt
from lean_model_lab.contracts import ContractError, canonical_bytes, digest


METADATA = {'model_profile_id': 'fixture-model-v1', 'model_profile_sha256': 'a'*64,
            'template_sha256': 'b'*64, 'source_build_sha256': 'c'*64,
            'fit_source_sha256': 'd'*64, 'calibration_source_sha256': 'e'*64}


def prompt(closure=1):
    keys = ['AAAAA', 'BBBBB', 'CCCCC', 'DDDDD', 'EEEEE', 'FFFFF', 'GGGGG', 'HHHHH']
    rows = [f'REF {keys[i]} {keys[i+1]}' if i < closure-1 else f'VALUE {keys[i]} APPLE'
            for i in range(8)]
    return '\n'.join(prompt_lines('reference-chain', rows, keys[0]))


def row(identity, *, closure=1, full=True, sliced=True, full_ns=1000, slice_ns=500):
    return {'source_id': digest('source-'+identity), 'group_id': digest('group-'+identity),
            'features': extract_features(prompt(closure)), 'full_correct': full,
            'slice_correct': sliced, 'full_request_ns': full_ns, 'slice_request_ns': slice_ns}


def populations():
    fit = [row('fit-safe-'+str(i)) for i in range(8)] + [
        row('fit-harm-'+str(i), closure=2, sliced=False) for i in range(8)]
    calibration = [row('cal-safe-'+str(i)) for i in range(8)] + [
        row('cal-harm-'+str(i), closure=2, sliced=False) for i in range(8)]
    return fit, calibration


def resign(value):
    value['controller_sha256'] = digest({k:v for k,v in value.items() if k!='controller_sha256'})
    return value


class AcceptanceControllerTests(unittest.TestCase):
    def test_actual_graph_features_include_superseded_writes_and_record_positions(self):
        text = '\n'.join(prompt_lines('record-updates', [
            'VALUE AAAAA APPLE', 'VALUE BBBBB PEACH', 'REF AAAAA BBBBB',
            'VALUE CCCCC GRAPE', 'VALUE BBBBB LEMON', 'VALUE DDDDD BERRY',
            'VALUE EEEEE MANGO', 'VALUE FFFFF MELON'], 'AAAAA'))
        self.assertEqual(extract_features(text), {'total_records':8, 'closure_records':2,
            'overwritten_writes':2, 'min_retained_position_permille':285,
            'max_retained_position_permille':571})
        single = '\n'.join(prompt_lines('record-lookup', ['VALUE AAAAA APPLE'], 'AAAAA'))
        self.assertEqual(extract_features(single), {'total_records':1, 'closure_records':1,
            'overwritten_writes':0, 'min_retained_position_permille':0,
            'max_retained_position_permille':0})

    def test_fit_signal_and_separate_safe_calibration_select_useful_gate(self):
        fit, calibration = populations()
        controller = fit_controller(fit, calibration, metadata=METADATA)
        parameters = controller['parameters']
        self.assertEqual(parameters['mode'], 'LEARNED_GATE')
        self.assertEqual(parameters['threshold_index'], 0)
        self.assertFalse(parameters['formal_guarantee'])
        self.assertFalse(controller['formal_guarantee'])
        tree = parameters['tree']
        self.assertEqual((tree['feature'], tree['threshold']), ('closure_records', 1))
        self.assertEqual(tree['harm_count'], 8)
        self.assertEqual(controller['calibration']['trace'][0]['accepted'], 8)
        self.assertEqual(controller['calibration']['trace'][0]['routed_correct'], 16)
        self.assertEqual(controller['calibration']['trace'][0]['request_saving_ns'], 4000)
        self.assertEqual(predict(parameters, prompt(1))['decision'], 'DEPENDENCY_SLICE')
        self.assertEqual(predict(parameters, prompt(2))['decision'], 'FULL')

    def test_depth_two_and_split_trace_use_deterministic_gini_ties(self):
        fit, calibration = populations()
        fit += [row('fit-safe-three-'+str(i), closure=3) for i in range(8)]
        controller = fit_controller(fit, calibration, metadata=METADATA)
        trace = controller['training']['trace']
        self.assertEqual([r['node_id'] for r in trace], [0,1,2,5,6])
        self.assertEqual(controller['parameters']['tree']['threshold'], 1)
        self.assertEqual(controller['parameters']['tree']['right']['threshold'], 2)
        self.assertEqual(len(trace), 5)
        self.assertTrue(all(r['stop_reason']=='MAX_DEPTH' for r in trace if r['node_id'] in (5,6)))
        root = trace[0]
        self.assertGreater(len(root['candidate_splits']), 1)
        self.assertEqual(root['selected'], {'feature':'closure_records', 'threshold':1})
        self.assertEqual(validate_controller(json.loads(json.dumps(controller))), controller)

    def test_harmful_calibration_refuses_slicing_without_retraining_fit_tree(self):
        fit, calibration = populations()
        original = fit_controller(fit, calibration, metadata=METADATA)
        calibration[0]['slice_correct'] = False  # Same fit-safe graph; actual omission harms.
        refused = fit_controller(fit, calibration, metadata=METADATA)
        self.assertEqual(refused['parameters']['tree'], original['parameters']['tree'])
        self.assertEqual(refused['parameters']['mode'], 'ALWAYS_FULL')
        self.assertEqual(refused['calibration']['refusal_reason'], 'NO_FEASIBLE_CALIBRATION_THRESHOLD')
        self.assertTrue(all(not r['eligible'] for r in refused['calibration']['trace']))
        prediction = predict(refused['parameters'], prompt())
        self.assertEqual(prediction['prompt'], prompt())
        self.assertEqual(prediction['decision'], 'FULL')
        self.assertEqual(prediction['reason'], 'CALIBRATION_REFUSED')

    def test_full_model_failures_remain_in_all_four_outcomes_and_quality_denominator(self):
        fit, _ = populations()
        fit += [row('fit-both-wrong', full=False, sliced=False),
                row('fit-slice-only', full=False, sliced=True)]
        calibration = [row('cal-good-'+str(i)) for i in range(15)] + [
            row('cal-both-wrong', full=False, sliced=False)]
        controller = fit_controller(fit, calibration, metadata=METADATA)
        self.assertEqual(controller['training']['outcomes'], {'both_correct':8,
            'full_only_correct':8, 'slice_only_correct':1, 'both_wrong':1})
        self.assertEqual(controller['calibration']['row_count'], 16)
        self.assertEqual(controller['calibration']['outcomes']['both_wrong'], 1)
        self.assertEqual(controller['calibration']['trace'][0]['routed_correct'], 15)
        self.assertEqual(controller['parameters']['mode'], 'ALWAYS_FULL')

    def test_finite_grid_selects_lowest_tied_feasible_threshold(self):
        fit = [row('fit-mixed-'+str(i), sliced=i!=0) for i in range(8)]
        calibration = [row('cal-good-'+str(i)) for i in range(8)]
        controller = fit_controller(fit, calibration, metadata=METADATA)
        self.assertEqual(controller['parameters']['tree']['kind'], 'leaf')
        self.assertEqual(controller['parameters']['threshold_index'], 3)  # 0.25 >= 1/8.
        self.assertEqual(controller['calibration']['grid'], [0, .05, .1, .25, .5, 1])
        self.assertEqual([r['eligible'] for r in controller['calibration']['trace']],
                         [False,False,False,True,True,True])

    def test_insufficient_accepted_rows_or_nonpositive_native_saving_refuses(self):
        fit, _ = populations()
        for label, count, cost in [('too-few',7,500), ('equal-cost',8,1000), ('slower',8,1500)]:
            with self.subTest(case=label):
                calibration = [row(label+str(i), slice_ns=cost) for i in range(count)]
                controller = fit_controller(fit, calibration, metadata=METADATA)
                self.assertEqual(controller['parameters']['mode'], 'ALWAYS_FULL')
                self.assertFalse(controller['formal_guarantee'])

    def test_calibration_maximizes_request_saving_before_threshold_tie_break(self):
        fit = [row('fit-zero-'+str(i)) for i in range(8)] + [
            row('fit-low-risk-'+str(i), closure=2, sliced=i!=0) for i in range(8)]
        calibration = [row('cal-small-saving-'+str(i), slice_ns=900) for i in range(8)] + [
            row('cal-larger-saving-'+str(i), closure=2, slice_ns=500) for i in range(8)]
        controller = fit_controller(fit, calibration, metadata=METADATA)
        self.assertTrue(controller['calibration']['trace'][0]['eligible'])
        self.assertEqual(controller['calibration']['trace'][0]['request_saving_ns'], 800)
        self.assertEqual(controller['calibration']['trace'][3]['request_saving_ns'], 4800)
        self.assertEqual(controller['parameters']['threshold_index'], 3)

    def test_combined_row_budget_rejects_oversize_without_training(self):
        base = row('budget-row')
        fit = []
        for index in range(4096):
            value = copy.deepcopy(base)
            value.update(source_id=digest('large-fit-source-'+str(index)),
                         group_id=digest('large-fit-group-'+str(index)))
            fit.append(value)
        with patch('lean_model_lab.acceptance_controller._fit', side_effect=AssertionError('oversized fit started')):
            with self.assertRaisesRegex(ContractError, 'combined 4096-row budget'):
                fit_controller(fit, [row('separate-cal')], metadata=METADATA)

    def test_deterministic_roundtrip_and_input_order_invariance(self):
        fit, calibration = populations()
        before = canonical_bytes([fit, calibration, METADATA])
        left = fit_controller(fit, calibration, metadata=METADATA)
        right = fit_controller(list(reversed(fit)), list(reversed(calibration)), metadata=METADATA)
        self.assertEqual(canonical_bytes(left), canonical_bytes(right))
        self.assertEqual(canonical_bytes([fit, calibration, METADATA]), before)
        restored = json.loads(json.dumps(left))
        self.assertEqual(validate_controller(restored), left)
        self.assertEqual(predict(restored['parameters'], prompt()), predict(left['parameters'], prompt()))

    def test_fit_and_calibration_source_and_group_overlap_are_rejected(self):
        for field in ('source_id', 'group_id'):
            with self.subTest(identity=field):
                fit, calibration = populations()
                calibration[0][field] = fit[0][field]
                with self.assertRaisesRegex(ContractError, 'overlap'):
                    fit_controller(fit, calibration, metadata=METADATA)
        fit, calibration = populations(); fit.append(copy.deepcopy(fit[0]))
        with self.assertRaisesRegex(ContractError, 'duplicate'):
            fit_controller(fit, calibration, metadata=METADATA)

    def test_strict_rows_reject_unknown_features_labels_boolean_numbers_and_ranges(self):
        mutations = {
            'answer oracle': lambda r: r['features'].update(expected_answer=1),
            'seed oracle': lambda r: r['features'].update(seed=123),
            'row extra': lambda r: r.update(confirmation=True),
            'bool feature': lambda r: r['features'].update(total_records=True),
            'bool request cost': lambda r: r.update(full_request_ns=True),
            'numeric outcome': lambda r: r.update(full_correct=1),
            'zero cost': lambda r: r.update(slice_request_ns=0),
            'impossible closure': lambda r: r['features'].update(closure_records=64),
            'off-grid position': lambda r: r['features'].update(min_retained_position_permille=101),
            'invalid hash': lambda r: r.update(group_id='not-an-identity'),
        }
        for name, mutate in mutations.items():
            with self.subTest(mutation=name):
                fit, calibration = populations(); mutate(fit[0])
                with self.assertRaises(ContractError):
                    fit_controller(fit, calibration, metadata=METADATA)
        fit, calibration = populations(); bad = dict(METADATA, arbitrary_code='never')
        with self.assertRaises(ContractError):
            fit_controller(fit, calibration, metadata=bad)

    def test_strict_tree_trace_and_calibration_reject_resigned_mutations(self):
        fit, calibration = populations(); controller = fit_controller(fit, calibration, metadata=METADATA)
        mutations = {
            'unknown tree feature': lambda c: c['parameters']['tree'].update(feature='expected_answer'),
            'bool threshold': lambda c: c['parameters']['tree'].update(threshold=True),
            'bool threshold index': lambda c: c['parameters'].update(threshold_index=False),
            'bad tree depth': lambda c: c['parameters']['tree']['left'].update(depth=3),
            'bad child population': lambda c: c['parameters']['tree']['left'].update(samples=9),
            'extra tree field': lambda c: c['parameters']['tree'].update(eval='anything'),
            'fake guarantee': lambda c: c.update(formal_guarantee=True),
            'changed Gini': lambda c: c['training']['trace'][0]['candidate_splits'][0].update(weighted_gini_numerator=99),
            'missing node trace': lambda c: c['training']['trace'].pop(),
            'manufactured saving': lambda c: c['calibration']['trace'][0].update(request_saving_ns=99999),
            'hidden failures': lambda c: c['calibration']['trace'][0].update(routed_correct=15),
            'arbitrary threshold': lambda c: c['parameters'].update(threshold_index=6),
            'forged feasibility': lambda c: c['calibration']['trace'][-1].update(eligible=True),
        }
        for name, mutate in mutations.items():
            with self.subTest(mutation=name):
                changed = copy.deepcopy(controller); mutate(changed); resign(changed)
                with self.assertRaises(ContractError):
                    validate_controller(changed)

    def test_prediction_has_no_labels_or_identity_oracle_and_emits_original_lines(self):
        fit, calibration = populations(); controller = fit_controller(fit, calibration, metadata=METADATA)
        parameters = controller['parameters']
        self.assertEqual(list(inspect.signature(predict).parameters), ['parameters', 'prompt'])
        heldout = prompt().replace('AAAAA', 'ZZZZZ').replace('APPLE', 'PEACH')
        self.assertEqual(extract_features(heldout), extract_features(prompt()))
        with (patch('lean_model_lab.acceptance_controller._counts', side_effect=AssertionError('labels accessed')),
              patch('lean_model_lab.acceptance_controller.validate_controller', side_effect=AssertionError('artifact trace accessed'))):
            result = predict(parameters, heldout)
        self.assertEqual(result['decision'], 'DEPENDENCY_SLICE')
        self.assertEqual(result['prompt'], transform_prompt(heldout, 'dependency-slice-v1')['prompt'])
        self.assertTrue(all(line in heldout.splitlines() for line in result['prompt'].splitlines()))
        self.assertNotEqual(result['prompt'], 'PEACH')
        with self.assertRaises(TypeError):
            predict(parameters, heldout, expected_answer='PEACH')
        with self.assertRaises(ContractError):
            predict(controller, heldout)

    def test_parameter_tree_rejects_split_outside_ancestor_feature_range(self):
        fit, calibration = populations()
        parameters = fit_controller(fit, calibration, metadata=METADATA)['parameters']
        child = parameters['tree']['left']
        left = copy.deepcopy(child); right = copy.deepcopy(child)
        for leaf, node_id in ((left,3), (right,4)):
            leaf.update(node_id=node_id, depth=2, samples=4)
            leaf['outcomes']['both_correct'] = 4
        child.update(kind='split', feature='closure_records', threshold=2, left=left, right=right)
        # Root's left branch already requires closure_records <= 1.
        with self.assertRaises(ContractError):
            predict(parameters, prompt())

    def test_malformed_prompt_falls_back_to_unchanged_full_context(self):
        fit, calibration = populations(); parameters = fit_controller(fit, calibration, metadata=METADATA)['parameters']
        for text in ('unknown syntax', prompt().replace('VALUE AAAAA APPLE','REF AAAAA AAAAA'), 'x'*4097):
            with self.subTest(prompt=text[:24]):
                result = predict(parameters, text)
                self.assertEqual(result['decision'], 'FULL')
                self.assertEqual(result['prompt'], text)
                self.assertEqual(result['reason'], 'MALFORMED_PROMPT')
                self.assertIsNone(result['features'])
        with self.assertRaises(ContractError):
            predict(parameters, {'prompt':prompt(), 'expected':'APPLE'})


if __name__ == '__main__':
    unittest.main()
