import copy
import unittest
from lean_model_lab.contracts import ContractError
from lean_model_lab.llama_adapter import completion_payload, normalize_response


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.records=[(20,{'stop':False,'tokens':[10,11],'content':'KEY','id_slot':0}),
                      (30,{'stop':True,'tokens':[],'content':'','id_slot':0,
                           'tokens_predicted':3,'tokens_evaluated':6,'truncated':False,
                           'stop_type':'eos','stopping_word':'','generation_settings':
                           {'samplers':['temperature'],'temperature':0,'seed':20260907,'n_predict':32,
                            'ignore_eos':False,'stop':[],'stream':True,'grammar':'','lora':[],
                            'backend_sampling':False}})]
        self.args=dict(request_id='r000',arrival_ns=1,admitted_ns=2,dispatch_ns=3,
                       completed_ns=40,prompt_tokens=6,slot=0)

    def test_only_policy_changes_and_eos_is_not_fabricated(self):
        before=completion_payload([1,2,3],0,False)
        after=completion_payload([1,2,3],0,True)
        self.assertEqual(['cache_prompt'],[k for k in before if before[k]!=after[k]])
        request=normalize_response(self.records,**self.args)
        self.assertEqual([10,11],request['output_token_ids'])
        self.assertEqual(3,request['generated_tokens'])
        self.assertEqual('KEY',request['output_text'])
        self.assertEqual([{'observed_ns':20,'token_ids':[10,11]}],request['token_events'])
        self.assertIsNone(request['engine_start_ns'])

    def test_mutated_stream_semantics_fail(self):
        mutations=[lambda r:r.pop(),lambda r:r[1][1].update(content='KEY'),
                   lambda r:r[1][1].update(tokens=[10,11]),
                   lambda r:r[0][1].update(id_slot=1),lambda r:r[1][1].update(tokens_predicted=1),
                   lambda r:r[1][1].update(id_slot=-1),
                   lambda r:r[1][1].update(tokens_evaluated=5),lambda r:r[1][1].update(truncated=True),
                   lambda r:r[1][1].update(stop_type='word'),lambda r:r.reverse(),
                   lambda r:r[1][1]['generation_settings'].update(temperature=1),
                   lambda r:r[1][1]['generation_settings'].update(grammar='root ::= \"X\"')]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                records=copy.deepcopy(self.records);mutate(records)
                with self.assertRaises(ContractError): normalize_response(records,**self.args)

    def test_actual_native_progress_sentinel_and_emitted_eos_are_distinct(self):
        progress={'stop':False,'tokens':[0],'content':'','id_slot':-1,
                  'tokens_predicted':0,'tokens_evaluated':6,
                  'prompt_progress':{'total':6,'cache':4,'processed':6,'time_ms':2}}
        records=[(10,progress),(20,{'stop':False,'tokens':[12987],'content':'water','id_slot':-1}),
                 (21,{'stop':False,'tokens':[151645],'content':'','id_slot':-1}),
                 copy.deepcopy(self.records[-1])]
        records[-1][1]['tokens_predicted']=2
        result=normalize_response(records,**self.args)
        self.assertEqual([12987,151645],result['output_token_ids'])
        self.assertEqual('water',result['output_text'])
        self.assertEqual(20,result['first_token_ns'])
        self.assertEqual(2,result['generated_tokens'])
        self.assertEqual(2,len(result['token_events']))
        for field,value in (('tokens_predicted',1),('content','hidden output'),('tokens',[77])):
            bad=copy.deepcopy(records);bad[0][1][field]=value
            with self.subTest(field=field),self.assertRaises(ContractError):normalize_response(bad,**self.args)
        bad=copy.deepcopy(records);bad[0][1]['prompt_progress']['processed']=3
        with self.assertRaises(ContractError):normalize_response(bad,**self.args)

    def test_output_limit_and_overshoot_are_retained(self):
        self.records[1][1].update(stop_type='limit',tokens_predicted=33)
        result=normalize_response(self.records,**self.args)
        self.assertEqual(33,result['generated_tokens'])
        self.assertEqual('limit',result['finish_reason'])


if __name__=='__main__':unittest.main()
