"""Mixed-population semantics and offered subgroup denominators; fixture outputs."""
from collections import Counter
import copy
import unittest
from lean_model_lab.contracts import ContractError,digest
from lean_model_lab.context_slice import transform_prompt
from lean_model_lab.structured_workloads import make_workload_v3,validate_workload_v3
from lean_model_lab.report import render_report
from lean_model_lab.evidence import evaluate_campaign
from test_context_slice import reference_interpret
from test_research_v3 import fixture_v3,make_campaign_v3
import test_controller_training as training_tests


class MixedWorkloadTests(unittest.TestCase):
    def test_frozen_balanced_cycles_and_independent_symbolic_answers(self):
        for n,counts in [(32,(11,11,10)),(128,(43,43,42))]:
            for split in ('development','confirmation'):
                work=make_workload_v3(family='record-mixed-v1',request_count=n,split=split,
                                      context_records=24,seed=717)
                self.assertEqual(validate_workload_v3(work),work)
                observed=Counter(r['prompt'].split('\n')[1][5:] for r in work['requests'])
                self.assertEqual(tuple(observed[f] for f in ('record-lookup','reference-chain','record-updates')),counts)
                for row in work['requests']:
                    self.assertEqual(reference_interpret(row['prompt']),row['expected'])
                    sliced=transform_prompt(row['prompt'],'dependency-slice-v1')
                    self.assertEqual(reference_interpret(sliced['prompt']),row['expected'])

    def test_split_and_seed_keep_actual_prompt_table_groups_disjoint(self):
        works=[make_workload_v3(family='record-mixed-v1',request_count=32,split=split,seed=seed)
               for split,seed in [('development',10),('development',11),('confirmation',10)]]
        groups=[{digest(r['prompt'].split('\n')[:-2]) for r in w['requests']} for w in works]
        for i in range(3):
            self.assertEqual(len(groups[i]),32)
            for j in range(i):self.assertTrue(groups[i].isdisjoint(groups[j]))
        damaged=copy.deepcopy(works[0]);damaged['requests'][0]['expected']='WRONG'
        with self.assertRaises(ContractError):validate_workload_v3(damaged)

    def test_report_subgroups_count_wrong_answers_without_conditioning(self):
        work,config=fixture_v3(family='record-mixed-v1')
        attempts=make_campaign_v3(work,config)
        candidate=next(a for a in attempts if a['arm']=='candidate')
        candidate['requests'][1]['output_text']='WRONG'
        result=evaluate_campaign(attempts,work,config=config,config_sha256=digest(config),workload_sha256=digest(work))
        row=next(a for a in result['attempts'] if a['attempt_id']==candidate['attempt_id'])
        self.assertFalse(result['eligible'])
        self.assertEqual(row['task_families']['reference-chain']['quality_correct'],42)
        self.assertEqual(row['task_families']['reference-chain']['expected_count'],43)
        self.assertEqual(sum(x['expected_count'] for x in row['task_families'].values()),128)
        html=render_report(result)
        self.assertIn('Mixed workload component results',html)
        self.assertIn('42 / 43',html)

    def test_registered_native_label_collector_accepts_mixed_population(self):
        helper=training_tests.ControllerTrainingTests()
        protocol,inventory=helper.data('record-mixed-v1')
        labels=helper.collect(protocol,inventory)
        self.assertEqual(len(labels['rows']),8)
        self.assertEqual(len({r['group_id'] for r in labels['rows']}),8)
        self.assertGreater(len({r['features']['closure_records'] for r in labels['rows']}),1)


if __name__=='__main__':unittest.main()
