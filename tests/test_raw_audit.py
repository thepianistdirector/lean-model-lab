import copy
import importlib.util
import unittest
from pathlib import Path

from lean_model_lab.llama_adapter import normalize_response

spec=importlib.util.spec_from_file_location('audit_raw_study',Path(__file__).resolve().parents[1]/'tools/audit_raw_study.py')
auditor=importlib.util.module_from_spec(spec);spec.loader.exec_module(auditor)


class RawAuditTests(unittest.TestCase):
    def test_corrupt_tokens_and_unexpected_baseline_cache_cannot_pass(self):
        records=[(10,{'stop':False,'id_slot':-1,'tokens':[0],'content':'','tokens_predicted':0,'tokens_evaluated':3,
            'prompt_progress':{'total':3,'cache':0,'processed':3,'time_ms':0}}),
            (20,{'stop':False,'id_slot':-1,'tokens':[10,11],'content':'KEY'}),
            (30,{'stop':True,'id_slot':0,'tokens':[],'content':'','tokens_predicted':3,'tokens_evaluated':3,
                'truncated':False,'stop_type':'eos','stopping_word':'',
                'generation_settings':{'samplers':['temperature'],'temperature':0,'seed':20260907,'n_predict':32,
                    'ignore_eos':False,'stop':[],'stream':True,'grammar':'','lora':[],'backend_sampling':False},
                'timings':{'cache_n':0,'prompt_n':3,'predicted_n':3}})]
        request=normalize_response(records,request_id='r000',arrival_ns=1,admitted_ns=2,dispatch_ns=3,
                                   completed_ns=40,prompt_tokens=3,slot=0)
        self.assertEqual(0,auditor.audit_request(request,records,3,0,'baseline')['reused_input_tokens'])
        bad=copy.deepcopy(records);bad[1][1]['tokens'][0]=99
        with self.assertRaisesRegex(ValueError,'normalized request'):auditor.audit_request(request,bad,3,0,'baseline')
        bad=copy.deepcopy(records);bad[-1][1]['timings'].update(cache_n=1,prompt_n=2)
        bad[0][1]['prompt_progress']['cache']=1
        with self.assertRaisesRegex(ValueError,'baseline unexpectedly'):auditor.audit_request(request,bad,3,0,'baseline')
        self.assertEqual(1,auditor.audit_request(request,bad,3,0,'candidate')['reused_input_tokens'])
        bad[0][1]['prompt_progress']['cache']=0
        with self.assertRaisesRegex(ValueError,'reused-prefix counts differ'):auditor.audit_request(request,bad,3,0,'candidate')


if __name__=='__main__':unittest.main()
