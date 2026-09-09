import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from lean_model_lab.artifacts import write_json_new,write_new
from lean_model_lab.contracts import canonical_bytes,make_workload,read_json
from lean_model_lab.llama_adapter import MODEL_FILENAME
from lean_model_lab.session import Session,SessionError
from lean_model_lab.study_report import evaluate_inventory
from test_evidence import CONFIG,make_attempt

spec=importlib.util.spec_from_file_location('export_study',Path(__file__).resolve().parents[1]/'tools/export_study.py')
exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)


class ExportTests(unittest.TestCase):
    def make_source(self,root,*,extra_path=False,unfinished=False):
        Session.create(root,CONFIG,make_workload(),[])
        with Session.open(root) as session:
            attempt=make_attempt();r=session.reserve('baseline',1,0,attempt['started_ns'])
            attempt['attempt_id']=r['attempt_id']
            model='/home/fixture/private/'+MODEL_FILENAME
            write_new(r['raw_dir']/'server.log',f"srv load_model: loading model '{model}'\n".encode())
            payload={'stop':True,'model':model,'tokens':[11,12],'timings':{'prompt_n':74,'cache_n':0},'content':''}
            write_new(r['raw_dir']/'r000.jsonl',canonical_bytes({'observed_ns':22,'data_utf8':json.dumps(payload)})+b'\n')
            if extra_path:write_json_new(r['raw_dir']/'unexpected.json',{'unreviewed':'/home/other/private'})
            if not unfinished:session.publish(attempt)
        return model,r['attempt_id']

    def test_redaction_rebinds_inventory_without_changing_producer_or_report(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);source=root/'source';output=root/'export'
            model,attempt=self.make_source(source)
            before=exporter.inventory_files(source)
            with Session.open(source) as session:original_report=evaluate_inventory(session.inspect())
            result=exporter.export(source,output,model)
            self.assertEqual(2,result['changed_raw_file_count'])
            self.assertEqual(before,exporter.inventory_files(source))
            with Session.open(output/'study') as session:self.assertEqual(original_report,evaluate_inventory(session.inspect()))
            event=read_json(output/'study/raw'/attempt/'r000.jsonl')
            payload=json.loads(event['data_utf8'])
            self.assertEqual(MODEL_FILENAME,payload['model'])
            self.assertEqual([11,12],payload['tokens'])
            self.assertEqual(22,event['observed_ns'])
            self.assertEqual((source/'journal.jsonl').read_bytes(),(output/'original-provenance/journal.jsonl').read_bytes())
            self.assertNotEqual((source/'journal.jsonl').read_bytes(),(output/'study/journal.jsonl').read_bytes())

    def test_sharded_profile_paths_and_four_digit_request_keep_payload_values(self):
        from lean_model_lab.profiles import get_model_profile
        profile=get_model_profile('qwen2.5-14b-instruct-fp16-v1')
        replacements={'/home/fixture/private/'+f['filename']:f['filename'] for f in profile['files']}
        entry='/home/fixture/private/'+profile['entrypoint']
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);path=root/'r1000.jsonl'
            event={'stop':True,'model':entry,'tokens':[151645],'timings':{'predicted_n':1},'content':''}
            path.write_bytes(canonical_bytes({'observed_ns':123,'data_utf8':json.dumps(event)})+b'\n')
            revised,changes=exporter.redact_raw(path,entry,replacements)
            receipt=json.loads(revised);payload=json.loads(receipt['data_utf8'])
            self.assertEqual(receipt['observed_ns'],123);self.assertEqual(payload.pop('model'),profile['entrypoint'])
            self.assertEqual(payload,{k:v for k,v in event.items() if k!='model'});self.assertEqual(len(changes),1)
            log=root/'server.log';log.write_text(''.join('llama_model_loader: loading '+p+'\n' for p in replacements))
            revised,changes=exporter.redact_raw(log,entry,replacements)
            self.assertEqual(len(changes),8);self.assertNotIn(b'/home/',revised)
            self.assertTrue(all(f['filename'].encode() in revised for f in profile['files']))

    def test_unknown_path_refuses_ready_marker_and_never_changes_source(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);source=root/'source';output=root/'export'
            model,_=self.make_source(source,extra_path=True);before=exporter.inventory_files(source)
            with self.assertRaisesRegex(ValueError,'unreviewed filesystem path'):
                exporter.export(source,output,model)
            self.assertFalse((output/'EXPORT-READY.json').exists())
            self.assertEqual(before,exporter.inventory_files(source))

    def test_unfinished_inventory_cannot_be_exported_as_finalized(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);source=root/'source';output=root/'export'
            model,_=self.make_source(source,unfinished=True)
            with self.assertRaisesRegex(SessionError,'finalized'):
                exporter.export(source,output,model)
            self.assertFalse(output.exists())


if __name__=='__main__':unittest.main()
