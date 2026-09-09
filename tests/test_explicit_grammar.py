"""Fixed wording diagnostic: same task records/answers, separately versioned text."""
import copy
import inspect
import unittest
from lean_model_lab.contracts import ContractError,digest
from lean_model_lab.context_slice import RULES_V2,OUTPUT_V2,transform_prompt
from lean_model_lab.explicit_grammar import restate_prompt
from lean_model_lab.structured_workloads import EXPLICIT_FAMILIES,make_workload_v3,validate_workload_v3
from lean_model_lab.recipes_v3 import cache_enabled,prompt_intervention
from test_context_slice import reference_interpret
from test_research_v3 import fixture_v3
import test_controller_training as training_tests


class ExplicitGrammarTests(unittest.TestCase):
    def test_new_families_preserve_exact_old_records_queries_answers_and_arrivals(self):
        for family,base in EXPLICIT_FAMILIES.items():
            for size in (8,24,64):
                for split in ('development','confirmation'):
                    old=make_workload_v3(family=base,request_count=8,seed=51,context_records=size,split=split)
                    new=make_workload_v3(family=family,request_count=8,seed=51,context_records=size,split=split)
                    self.assertEqual(validate_workload_v3(new),new)
                    for a,b in zip(old['requests'],new['requests']):
                        self.assertEqual(a['prompt'].split('\n')[4:],b['prompt'].split('\n')[4:])
                        self.assertEqual(a['expected'],b['expected'])
                        self.assertEqual(a['arrival_offset_ns'],b['arrival_offset_ns'])
                        self.assertEqual(reference_interpret(b['prompt']),b['expected'])
                        self.assertLessEqual(len(b['prompt'].encode('ascii')),1600)
                        sliced=transform_prompt(b['prompt'],'dependency-slice-v1')
                        self.assertEqual(sliced['decision'],'CERTIFIED_SLICE')
                        self.assertEqual(reference_interpret(sliced['prompt']),b['expected'])

    def test_registered_diagnosis_changes_only_three_header_lines_and_no_cache(self):
        work,config=fixture_v3(mechanism_id='explicit-grammar-v2',purpose='DEVELOPMENT',split='development',request_count=8)
        source=work['requests'][0]['prompt']
        self.assertEqual(prompt_intervention(source,'explicit-grammar-v2','baseline')['prompt'],source)
        result=prompt_intervention(source,'explicit-grammar-v2','candidate')
        self.assertEqual(result['certificate']['rewritten_line_indices'],[0,2,3])
        self.assertEqual([i for i,(a,b) in enumerate(zip(source.split('\n'),result['prompt'].split('\n'))) if a!=b],[0,2,3])
        self.assertEqual(result['certificate']['retained_record_count'],8)
        self.assertEqual(result['certificate']['scope'],'SYNTAX_PRESERVING_INSTRUCTION_RESTATEMENT_ONLY')
        self.assertEqual(reference_interpret(result['prompt']),work['requests'][0]['expected'])
        self.assertEqual(list(inspect.signature(restate_prompt).parameters),['prompt'])
        self.assertFalse(cache_enabled(config['recipe'],'baseline'))
        self.assertFalse(cache_enabled(config['recipe'],'candidate'))

    def test_malformed_or_mixed_header_never_acquires_a_certificate(self):
        work=make_workload_v3(family='reference-chain-explicit-v2',request_count=4)
        prompt=work['requests'][0]['prompt'].replace(RULES_V2,'RULES Let the model guess')
        self.assertEqual(restate_prompt(prompt)['prompt'],prompt)
        self.assertEqual(restate_prompt(prompt)['decision'],'FALLBACK_FULL_CONTEXT')
        self.assertEqual(transform_prompt(prompt,'dependency-slice-v1')['decision'],'FALLBACK_FULL_CONTEXT')

    def test_training_table_groups_do_not_change_when_only_instructions_change(self):
        helper=training_tests.ControllerTrainingTests()
        p1,i1=helper.data('reference-chain');p2,i2=helper.data('reference-chain-explicit-v2')
        old=helper.collect(p1,i1);new=helper.collect(p2,i2)
        self.assertEqual({r['group_id'] for r in old['rows']},{r['group_id'] for r in new['rows']})
        self.assertTrue({r['source_id'] for r in old['rows']}.isdisjoint(r['source_id'] for r in new['rows']))


if __name__=='__main__':unittest.main()
