"""Schema-3 integration controls using synthetic observations, never native inference.

Prompt counts below are fixture counters, not native tokenizer receipts. Actual
input-ID stability is a separate raw-evidence gate owned by the workbench audit.
"""
import copy
from pathlib import Path
import tempfile
import unittest

from lean_model_lab.config import make_config_v2, validate_config
from lean_model_lab.contracts import ContractError, canonical_bytes, digest, validate_workload
from lean_model_lab.evidence import EvidenceError, evaluate_campaign, summarize_attempt, validate_attempt
from lean_model_lab.recipes import schedule, validate_recipe
from lean_model_lab.recipes_v3 import MECHANISMS, make_recipe_v3, validate_recipe_v3
from lean_model_lab.research_studies import build_proposal, default_protocol
from lean_model_lab.session import Session, SessionError
from lean_model_lab.structured_workloads import make_workload_v3
from test_evidence import CONFIG as CONFIG_V1, make_campaign as campaign_v1
from test_evidence_v2 import fixture as fixture_v2, make_attempt as attempt_v2, make_campaign as campaign_v2


ROOT = Path(__file__).resolve().parents[1]
TEMP_ROOT = ROOT/'.cache/tmp'


def fixture_v3(*, mechanism_id='dependency-slice-v1', family='reference-chain',
               context_records=8, split='confirmation', purpose='MEASUREMENT',
               request_count=128, concurrency_modes=(1,), pair_count=2):
    workload = make_workload_v3(family=family, context_records=context_records, split=split,
                                request_count=request_count, concurrency_modes=concurrency_modes)
    _, base_config = fixture_v2()
    proposal = build_proposal(mechanism_id)
    protocol = default_protocol(proposal)
    controller=None
    if mechanism_id=='learned-gated-slice-v1':
        from test_acceptance_controller import populations, METADATA
        from lean_model_lab.acceptance_controller import fit_controller
        from lean_model_lab.profiles import get_model_profile
        profile=get_model_profile('qwen2.5-0.5b-instruct-fp16-v1')
        controller=fit_controller(*populations(),metadata={**METADATA,
            'model_profile_id':profile['profile_id'],'model_profile_sha256':digest(profile),
            'template_sha256':profile['template_sha256']})
    recipe = make_recipe_v3(model_profile_id='qwen2.5-0.5b-instruct-fp16-v1', workload=workload,
                            allocation=base_config['recipe']['allocation'], mechanism_id=mechanism_id,
                            proposal=proposal, protocol=protocol, pair_count=pair_count, purpose=purpose,
                            ttft_slo_ns=1_000_000, end_to_end_slo_ns=2_000_000,controller=controller)
    config = make_config_v2(recipe=recipe, server_sha256='a'*64, evidence_class='TEST_FIXTURE',
                            hardware={'platform':'fixture', 'cpu':'fixture'}, implementation_sha256='b'*64)
    return workload, config


def identity(workload, config):
    return {'config':config, 'config_sha256':digest(config), 'workload_sha256':digest(workload)}


def alternative_output(request):
    """A whitespace-prefixed fixture answer differs in tokens but passes exact strip."""
    request['output_text'] = ' '+request['output_text']
    request['output_token_ids'].insert(0, 32)
    request['token_events'][0]['token_ids'].insert(0, 32)
    request['generated_tokens'] += 1


def make_attempt_v3(workload, config, *, arm='baseline', concurrency=1, pair_index=0,
                    started_ns=1000, duration_ns=100, preparation_ns=0, changed_output=False):
    attempt = attempt_v2(workload, config, arm=arm, concurrency=concurrency, pair_index=pair_index,
                         started_ns=started_ns, duration_ns=duration_ns)
    attempt['schema_version'] = 3
    changed_input = not config['evaluation']['output_token_parity']
    for request in attempt['requests']:
        # Declared fixture counters differ across arms only for schema-3 interventions.
        request['prompt_tokens'] = 60 if arm=='candidate' and changed_input else 100
        if arm=='candidate' and changed_output:
            alternative_output(request)
    if preparation_ns:
        attempt['service_started_ns'] += preparation_ns
        attempt['finished_ns'] += preparation_ns
        attempt['overhead_ns']['verification'] += preparation_ns
        for request in attempt['requests']:
            for field in ('arrival_ns', 'admitted_ns', 'dispatch_ns', 'first_token_ns', 'completed_ns'):
                if request[field] is not None:
                    request[field] += preparation_ns
            for event in request['token_events']:
                event['observed_ns'] += preparation_ns
    return attempt


def make_campaign_v3(workload, config, *, preparation_ns=0, changed_output=True):
    attempts = []
    started = 1000
    for concurrency, pair, arm in schedule(config):
        attempt = make_attempt_v3(workload, config, arm=arm, concurrency=concurrency,
            pair_index=pair, started_ns=started, duration_ns=80 if arm=='candidate' else 100,
            preparation_ns=preparation_ns if arm=='candidate' else 0, changed_output=changed_output)
        attempts.append(attempt)
        started = attempt['finished_ns']+100
    return attempts


class ResearchV3Tests(unittest.TestCase):
    def setUp(self):
        TEMP_ROOT.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix='research-v3-test-', dir=TEMP_ROOT)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def evaluate(self, attempts, workload, config):
        return evaluate_campaign(attempts, workload, **identity(workload, config))

    def assert_no_comparative_ratios(self, result):
        self.assertFalse(result['eligible'])
        self.assertFalse(result['measured_claim_eligible'])
        for group in result['concurrency_groups'].values():
            self.assertFalse(group['eligible'])
            self.assertIsNone(group['throughput_ratio_median'])
            self.assertIsNone(group.get('full_wall_efficiency_ratio_median'))
            for pair in group['pairs']:
                self.assertFalse(pair['eligible'])
                self.assertIsNone(pair['throughput_candidate_over_baseline'])
                self.assertIsNone(pair['full_wall_efficiency_candidate_over_baseline'])

    def test_compound_contract_routes_all_workload_families_through_schema_three(self):
        for family in ('record-lookup', 'reference-chain', 'record-updates'):
            with self.subTest(family=family):
                workload, config = fixture_v3(family=family, purpose='DEVELOPMENT',
                                             split='development', request_count=4)
                recipe = config['recipe']
                self.assertEqual((workload['schema_version'], recipe['schema_version'], config['schema_version']), (3,3,3))
                self.assertEqual(validate_workload(workload), workload)
                self.assertEqual(validate_recipe(recipe), recipe)
                self.assertEqual(validate_config(config), config)
                self.assertEqual(recipe['workload_sha256'], digest(workload))
                self.assertEqual(recipe['research_protocol']['proposal_sha256'], digest(recipe['research_proposal']))
                self.assertFalse(recipe['evaluation']['output_token_parity'])
                self.assertEqual(recipe['evaluation']['comparison_semantics'], 'changed_input_exact_task_quality_no_loss')
                self.assertEqual(recipe['evaluation']['quality_noninferiority_margin'], 0)
                self.assertEqual(recipe['evaluation']['cost_primary'], 'attempt_full_wall_including_prompt_preparation')

    def test_all_registered_mechanisms_have_explicit_comparison_semantics(self):
        for mechanism in MECHANISMS:
            with self.subTest(mechanism=mechanism):
                _, config = fixture_v3(mechanism_id=mechanism, purpose='DEVELOPMENT',
                                      split='development', request_count=4)
                self.assertEqual(validate_recipe_v3(config['recipe']), config['recipe'])
                same_input = mechanism in ('prefix-cache-v1', 'full-context-v1')
                self.assertIs(config['evaluation']['output_token_parity'], same_input)

    def test_mutated_proposal_protocol_mechanism_or_weakened_evaluation_is_rejected(self):
        _, config = fixture_v3()
        mutations = {
            'proposal hash': lambda r: r['research_protocol'].update(proposal_sha256='0'*64),
            'proposal contents': lambda r: r['research_proposal'].update(prediction='Changed after protocol freeze'),
            'unknown mechanism': lambda r: r.update(mechanism_id='unregistered-code-v1'),
            'mechanism mismatch': lambda r: r['research_proposal'].update(mechanism_id='full-context-v1'),
            'quality weakened': lambda r: r['evaluation'].update(accuracy_minimum=0.50),
            'noninferiority weakened': lambda r: r['evaluation'].update(quality_noninferiority_margin=0.05),
            'service-only claim': lambda r: r['evaluation'].update(cost_primary='service_wall_only'),
            'parity relabel': lambda r: r['evaluation'].update(output_token_parity=True),
            'workload digest': lambda r: r.update(workload_sha256='0'*64),
        }
        for name, mutate in mutations.items():
            with self.subTest(mutation=name):
                recipe = copy.deepcopy(config['recipe'])
                mutate(recipe)
                with self.assertRaises(ContractError):
                    validate_recipe(recipe)
        changed_config = copy.deepcopy(config)
        changed_config['evaluation']['quality_noninferiority_margin'] = 1
        with self.assertRaises(ContractError):
            validate_config(changed_config)
        with self.assertRaisesRegex(ContractError, 'unknown registered study mechanism'):
            build_proposal('unregistered-code-v1')

    def test_measurement_cannot_relabel_development_split(self):
        with self.assertRaisesRegex(ContractError, 'confirmation split'):
            fixture_v3(split='development', purpose='MEASUREMENT')
        workload, config = fixture_v3(split='development', purpose='DEVELOPMENT', request_count=4)
        result = self.evaluate(make_campaign_v3(workload, config), workload, config)
        self.assert_no_comparative_ratios(result)
        self.assertIn('development_recipe_not_measurement', result['ineligibility_reasons'])

    def test_changed_input_and_output_tokens_pass_only_explicit_task_quality_contract(self):
        workload, config = fixture_v3()
        attempts = make_campaign_v3(workload, config)
        for attempt in attempts:
            validate_attempt(attempt, workload, **identity(workload, config))
        result = self.evaluate(attempts, workload, config)
        self.assertTrue(result['eligible'])
        self.assertEqual(result['schema_version'], 3)
        self.assertEqual(result['finding'], 'TEST_FIXTURE_ONLY')
        self.assertFalse(result['measured_claim_eligible'])
        group = result['concurrency_groups']['1']
        self.assertEqual(group['finding'], 'PRACTICAL_GAIN_IN_ALL_PAIRS')
        for pair in group['pairs']:
            self.assertEqual(pair['quality_difference_candidate_minus_baseline'], 0)
            self.assertFalse(pair['token_parity'])
            self.assertEqual(len(pair['prompt_token_mismatch_request_ids']), len(workload['requests']))
            self.assertGreater(pair['full_wall_efficiency_candidate_over_baseline'], 1.05)

    def test_same_input_schema_three_controls_still_require_token_parity(self):
        for mechanism in ('prefix-cache-v1', 'full-context-v1'):
            with self.subTest(mechanism=mechanism):
                workload, config = fixture_v3(mechanism_id=mechanism)
                result = self.evaluate(make_campaign_v3(workload, config), workload, config)
                self.assert_no_comparative_ratios(result)
                self.assertTrue(any('token_identity_or_parity_failed' in r for r in result['ineligibility_reasons']))

    def test_quality_regression_blocks_gain_even_above_absolute_threshold(self):
        workload, config = fixture_v3()
        attempts = make_campaign_v3(workload, config)
        candidate = next(a for a in attempts if a['arm']=='candidate')
        candidate['requests'][0]['output_text'] = 'WRONG'
        result = self.evaluate(attempts, workload, config)
        self.assertGreater(next(a for a in result['attempts'] if a['attempt_id']==candidate['attempt_id'])['quality_accuracy'], .95)
        self.assert_no_comparative_ratios(result)
        self.assertTrue(any('task_quality_regression' in r for r in result['ineligibility_reasons']))
        self.assertEqual(result['accounting']['observed_requests'], 4*128)

    def test_equal_low_quality_cannot_pass_noninferiority_alone(self):
        workload, config = fixture_v3()
        attempts = make_campaign_v3(workload, config)
        for attempt in attempts:
            for request in attempt['requests'][:7]:
                request['output_text'] = 'WRONG'
        result = self.evaluate(attempts, workload, config)
        self.assert_no_comparative_ratios(result)
        self.assertTrue(all(a['quality_accuracy'] < .95 for a in result['attempts']))
        self.assertTrue(all('absolute_quality_below_0.95' in a['ineligibility_reasons'] for a in result['attempts']))

    def test_prompt_count_drift_within_an_arm_invalidates_normalized_comparison(self):
        workload, config = fixture_v3()
        attempts = make_campaign_v3(workload, config)
        next(a for a in attempts if a['arm']=='candidate')['requests'][0]['prompt_tokens'] += 1
        result = self.evaluate(attempts, workload, config)
        self.assert_no_comparative_ratios(result)
        self.assertIn('prompt_token_counts_changed_across_attempts', result['ineligibility_reasons'])

    def test_expensive_preparation_erases_gain_while_service_improves(self):
        workload, config = fixture_v3()
        attempts = make_campaign_v3(workload, config, preparation_ns=10_000)
        result = self.evaluate(attempts, workload, config)
        self.assertTrue(result['eligible'])
        group = result['concurrency_groups']['1']
        self.assertGreater(group['throughput_ratio_median'], 1.05)
        self.assertLess(group['full_wall_efficiency_ratio_median'], 1)
        self.assertEqual(group['finding'], 'NO_DEMONSTRATED_PRACTICAL_GAIN')
        self.assertEqual(result['accounting']['full_wall_ns'], sum(a['finished_ns']-a['started_ns'] for a in attempts))
        self.assertEqual(result['accounting']['overhead_ns']['verification'], 4*200+2*10_000)

    def test_session_roundtrip_preserves_schema_three_lineage_and_checkpoints(self):
        workload, config = fixture_v3(purpose='DEVELOPMENT', split='development', request_count=4)
        root = self.root/'session'
        Session.create(root, config, workload, [])
        attempt = make_attempt_v3(workload, config)
        with Session.open(root) as session:
            reservation = session.reserve(attempt['arm'], attempt['concurrency'], attempt['pair_index'], attempt['started_ns'])
            attempt['attempt_id'] = reservation['attempt_id']
            (reservation['raw_dir']/'fixture.txt').write_text('TEST_FIXTURE: synthetic counters; no native inference\n')
            request = attempt['requests'][0]
            session.checkpoint(attempt['attempt_id'], request, request['completed_ns'])
            mutated = copy.deepcopy(attempt)
            mutated['requests'][0]['output_text'] = 'Rewritten checkpoint'
            with self.assertRaisesRegex(SessionError, 'omits or changes'):
                session.publish(mutated)
            session.publish(attempt)
        with Session.open(root) as session:
            inventory = session.inspect()
        self.assertTrue(inventory['inventory_complete'])
        self.assertEqual(inventory['attempts'], [attempt])
        self.assertEqual(canonical_bytes(inventory['config']), canonical_bytes(config))
        self.assertEqual(inventory['workload_sha256'], digest(workload))
        summary = summarize_attempt(attempt, workload, **identity(workload, config))
        self.assertEqual(summary['quality_denominator'], 4)
        self.assertEqual(summary['quality_accuracy'], 1)
        self.assertFalse(summary['eligible'])

    def test_schema_one_and_two_keep_existing_same_input_parity_rules(self):
        from lean_model_lab.contracts import make_workload
        work_v1 = make_workload()
        work_v2, config_v2 = fixture_v2()
        for version, workload, config, attempts in (
            (1, work_v1, CONFIG_V1, campaign_v1()),
            (2, work_v2, config_v2, campaign_v2(work_v2, config_v2)),
        ):
            with self.subTest(schema=version):
                original = canonical_bytes(config)
                self.assertTrue(self.evaluate(attempts, workload, config)['eligible'])
                for attempt in attempts:
                    if attempt['arm']=='candidate':
                        alternative_output(attempt['requests'][0])
                result = self.evaluate(attempts, workload, config)
                self.assertFalse(result['eligible'])
                self.assertFalse(result['measured_claim_eligible'])
                self.assertEqual(canonical_bytes(validate_config(config)), original)
                self.assertEqual(config['schema_version'], version)


if __name__ == '__main__':
    unittest.main()
