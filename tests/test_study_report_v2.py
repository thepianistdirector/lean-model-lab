"""Prior measurement history must survive a fresh successful study inventory."""
import copy
import json
import unittest
from lean_model_lab.contracts import digest
from lean_model_lab.study_report import evaluate_inventory
from test_evidence_v2 import fixture,make_campaign


def inventory():
    workload,config=fixture(modes=(1,))
    attempts=make_campaign(workload,config)
    records=[{'phase':name,'status':'COMPLETED','started_ns':1+i*100,'finished_ns':50+i*100,
              'bytes_acquired':0,'details':'synthetic setup'}
             for i,name in enumerate(('source-acquisition','model-acquisition','build'))]
    return {'inventory_complete':True,'config':config,'workload':workload,
            'config_sha256':digest(config),'workload_sha256':digest(workload),
            'attempts':attempts,'reservation_count':len(attempts),'event_count':20,
            'setup_accounting':{'records':records}}


def predecessor(value,*,purpose='MEASUREMENT',status='FAILED',recipe_hash=None):
    details={'purpose':purpose,'source_recipe_sha256':recipe_hash or digest(value['config']['recipe']),
             'source_config_sha256':'c'*64,'source_session_id':'old-fixture',
             'source_attempt_id':'old-attempt','source_attempt_sha256':'d'*64}
    return {'phase':'predecessor-study-attempt','status':status,'started_ns':300,'finished_ns':500,
            'bytes_acquired':0,'details':json.dumps(details)}


class PriorMeasurementTests(unittest.TestCase):
    def test_same_recipe_retry_cannot_reset_any_prior_outcome(self):
        for status in ('FAILED','INTERRUPTED','COMPLETED'):
            with self.subTest(status=status):
                value=inventory();self.assertTrue(evaluate_inventory(value)['eligible'])
                value['setup_accounting']['records'].append(predecessor(value,status=status))
                result=evaluate_inventory(value)
                self.assertFalse(result['eligible']);self.assertFalse(result['measured_claim_eligible'])
                self.assertIn('retained_prior_same_recipe_measurement',result['ineligibility_reasons'])
                for group in result['concurrency_groups'].values():
                    self.assertIsNone(group['throughput_ratio_median'])
                    for pair in group['pairs']:
                        self.assertIsNone(pair['throughput_candidate_over_baseline'])
                        self.assertTrue(all(v is None for v in pair['ttft_tail_candidate_over_baseline'].values()))

    def test_development_and_distinct_recipe_remain_charged_separate_trials(self):
        for kwargs in ({'purpose':'DEVELOPMENT'},{'recipe_hash':'e'*64}):
            value=inventory();value['setup_accounting']['records'].append(predecessor(value,**kwargs))
            result=evaluate_inventory(value);self.assertTrue(result['eligible'])
            self.assertEqual(len(result['accounting']['setup_acquisition_build_costs']['records']),4)

    def test_old_measurement_receipt_without_recipe_identity_is_conservative(self):
        value=inventory();row=predecessor(value);details=json.loads(row['details'])
        del details['source_recipe_sha256'];row['details']=json.dumps(details)
        value['setup_accounting']['records'].append(row)
        self.assertFalse(evaluate_inventory(value)['eligible'])

if __name__=='__main__':unittest.main()
