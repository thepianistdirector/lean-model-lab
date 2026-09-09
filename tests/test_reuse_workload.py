"""Table trajectories and cache-policy controls, without synthetic speed claims."""
import unittest
from lean_model_lab.structured_workloads import make_workload_v3, validate_workload_v3
from lean_model_lab.recipes_v3 import cache_enabled, prompt_intervention
from test_research_v3 import fixture_v3


class ReuseWorkloadTests(unittest.TestCase):
    def test_complete_table_trajectories_include_cold_primers(self):
        for count in (8,24,64):
            work=make_workload_v3(family='record-reuse',context_records=count,request_count=24,
                                  concurrency_modes=(1,),split='confirmation',seed=999)
            self.assertEqual(validate_workload_v3(work),work)
            tables=[]
            for start in range(0,24,8):
                rows=work['requests'][start:start+8]
                table=rows[0]['prompt'].split('\n')[5:-3]
                tables.append(table)
                self.assertEqual(len(table),count)
                self.assertEqual(len({r['prompt'].split('\n')[-2] for r in rows}),8)
                for row in rows:
                    lines=row['prompt'].split('\n')
                    self.assertEqual(lines[5:-3],table)
                    mapping={line.split()[1]:line.split()[2] for line in table}
                    self.assertEqual(mapping[lines[-2].split()[1]],row['expected'])
            self.assertEqual(len({tuple(t) for t in tables}),3)
            self.assertEqual(len(work['requests']),24)

    def test_development_confirmation_tables_are_disjoint(self):
        works=[make_workload_v3(family='record-reuse',request_count=16,split=s,seed=123)
               for s in ('development','confirmation')]
        self.assertTrue({r['prompt'] for r in works[0]['requests']}.isdisjoint(
                        {r['prompt'] for r in works[1]['requests']}))
        self.assertTrue({r['expected'] for r in works[0]['requests']}.isdisjoint(
                        {r['expected'] for r in works[1]['requests']}))

    def test_strong_cache_baseline_and_candidate_use_explicit_policy(self):
        for mechanism,policies in [('prefix-cache-v1',(False,True)),
            ('dependency-slice-v1',(False,False)),('dependency-slice-cache-v1',(False,True)),
            ('slice-versus-full-cache-v1',(True,True))]:
            work,config=fixture_v3(mechanism_id=mechanism,family='record-reuse',request_count=8,
                                  purpose='DEVELOPMENT',split='development')
            recipe=config['recipe'];prompt=work['requests'][0]['prompt']
            self.assertEqual(tuple(cache_enabled(recipe,a) for a in ('baseline','candidate')),policies)
            self.assertEqual(prompt_intervention(prompt,mechanism,'baseline')['prompt'],prompt)
            changed=prompt_intervention(prompt,mechanism,'candidate')['prompt']!=prompt
            self.assertEqual(changed,mechanism!='prefix-cache-v1')


if __name__=='__main__':unittest.main()
