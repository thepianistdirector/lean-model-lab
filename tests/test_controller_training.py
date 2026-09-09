"""Training-admission tests use explicit fixtures; no native research claims."""
import copy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from lean_model_lab.contracts import ContractError,digest,read_json
from lean_model_lab.controller_training import (make_training_protocol,collect_native_labels,
    train_native_controller,validate_training_protocol)
from lean_model_lab.recipes_v3 import prompt_intervention,validate_recipe_v3
from test_research_v3 import fixture_v3,make_campaign_v3
from test_acceptance_controller import resign


class ControllerTrainingTests(unittest.TestCase):
    def data(self,family='reference-chain'):
        work,config=fixture_v3(family=family,purpose='DEVELOPMENT',split='development',request_count=8)
        recipe=config['recipe']
        other=copy.deepcopy(recipe)
        from lean_model_lab.structured_workloads import make_workload_v3
        from lean_model_lab.recipes_v3 import make_recipe_v3
        other_work=make_workload_v3(**{**work['generator'],'seed':99})
        other=make_recipe_v3(model_profile_id=recipe['model_profile_id'],workload=other_work,
            allocation=recipe['allocation'],mechanism_id=recipe['mechanism_id'],
            protocol=recipe['research_protocol'],proposal=recipe['research_proposal'],purpose='DEVELOPMENT')
        protocol=make_training_protocol([recipe],[other])
        protocol['frozen_ns']=1
        config['evidence_class']='MEASURED' # deliberately mocked native evidence below
        attempts=make_campaign_v3(work,config,changed_output=False)
        inventory={'config':config,'config_sha256':digest(config),'workload':work,
            'workload_sha256':digest(work),'inventory_complete':True,'attempts':attempts}
        return protocol,inventory

    def collect(self,protocol,inventory):
        session=MagicMock();session.__enter__.return_value.inspect.return_value=inventory
        with patch('lean_model_lab.controller_training.Session.open',return_value=session), patch(
            'lean_model_lab.controller_training.verify_native_inventory',return_value={'status':'TEST_FIXTURE'}):
            return collect_native_labels([Path('fixture')],protocol,'fit')

    def test_protocol_rejects_overlap_and_confirmatory_labels(self):
        protocol,inventory=self.data();recipe=inventory['config']['recipe']
        with self.assertRaisesRegex(ContractError,'disjoint'):
            make_training_protocol([recipe],[recipe])
        _,confirmation=fixture_v3()
        with self.assertRaisesRegex(ContractError,'development'):
            make_training_protocol([recipe],[confirmation['recipe']])
        weakened=copy.deepcopy(protocol);weakened['selection_rule']='allow 20% harm'
        with self.assertRaises(ContractError):validate_training_protocol(weakened)

    def test_all_repetition_labels_keep_harm_and_all_table_queries_share_group(self):
        protocol,inventory=self.data('record-reuse')
        candidate=next(a for a in inventory['attempts'] if a['arm']=='candidate')
        candidate['requests'][0]['output_text']='WRONG'
        value=self.collect(protocol,inventory)
        self.assertEqual(len(value['rows']),8)
        self.assertEqual(len({r['group_id'] for r in value['rows']}),1)
        self.assertEqual(sum(not r['slice_correct'] for r in value['rows']),1)
        self.assertTrue(all(r['full_correct'] for r in value['rows']))

    def test_protocol_postdating_labels_missing_population_and_failed_cells_refused(self):
        for mutation in ('late','missing','failed','wrong_recipe'):
            protocol,inventory=self.data()
            if mutation=='late':protocol['frozen_ns']=10**15
            if mutation=='missing':inventory['attempts'].pop()
            if mutation=='failed':inventory['attempts'][0]['status']='INTERRUPTED'
            if mutation=='wrong_recipe':protocol['fit_recipe_sha256s']=['f'*64]
            with self.subTest(mutation=mutation),self.assertRaises(ContractError):
                self.collect(protocol,inventory)

    def test_native_integrity_check_is_required(self):
        protocol,inventory=self.data()
        session=MagicMock();session.__enter__.return_value.inspect.return_value=inventory
        with patch('lean_model_lab.controller_training.Session.open',return_value=session), patch(
            'lean_model_lab.controller_training.verify_native_inventory',side_effect=ValueError('raw mismatch')):
            with self.assertRaisesRegex(ValueError,'raw mismatch'):
                collect_native_labels([Path('fixture')],protocol,'fit')

    def test_model_template_binding_and_runtime_gate(self):
        work,config=fixture_v3(mechanism_id='learned-gated-slice-v1')
        recipe=config['recipe'];self.assertEqual(validate_recipe_v3(recipe),recipe)
        for key in ('model_profile_sha256','template_sha256'):
            changed=copy.deepcopy(recipe);changed['controller']['metadata'][key]='f'*64
            resign(changed['controller'])
            with self.assertRaisesRegex(ContractError,'model or template'):
                validate_recipe_v3(changed)
        prompt=work['requests'][0]['prompt']
        baseline=prompt_intervention(prompt,recipe['mechanism_id'],'baseline',recipe['controller'])
        self.assertEqual(baseline['prompt'],prompt)
        candidate=prompt_intervention(prompt,recipe['mechanism_id'],'candidate',recipe['controller'])
        self.assertIn('controller_prediction',candidate)
        self.assertFalse(candidate['controller_prediction']['formal_guarantee'])
        simple=prompt_intervention(prompt,'simple-gated-slice-v1','candidate')
        self.assertEqual(simple['prompt'],prompt) # reference chain is excluded by simple gate


if __name__=='__main__':unittest.main()
