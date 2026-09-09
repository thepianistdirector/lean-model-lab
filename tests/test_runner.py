"""Transport and process-control fixtures; no model/backend is executed."""
import json
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from lean_model_lab.artifacts import read_journal
from lean_model_lab.llama_adapter import completion_payload
from lean_model_lab.runner import _stream, server_arguments, stop_owned_process


class Handler(BaseHTTPRequestHandler):
    records=[]
    def log_message(self,*args):pass
    def do_POST(self):
        self.rfile.read(int(self.headers['Content-Length']))
        self.send_response(200);self.send_header('Content-Type','text/event-stream');self.end_headers()
        for record in self.records:
            self.wfile.write(b'data: '+json.dumps(record).encode()+b'\n\n')
            self.wfile.flush()


class RunnerTests(unittest.TestCase):
    def test_native_stream_keeps_raw_accounting_and_partial_failure(self):
        progress={'stop':False,'tokens':[0],'content':'','id_slot':-1,'tokens_predicted':0,'tokens_evaluated':3,
                  'prompt_progress':{'total':3,'cache':0,'processed':3,'time_ms':0}}
        partial={'stop':False,'tokens':[10,11],'content':'KEY','id_slot':-1}
        final={'stop':True,'tokens':[],'content':'','id_slot':0,'tokens_predicted':3,
               'tokens_evaluated':3,'truncated':False,'stop_type':'eos','stopping_word':'',
               'generation_settings':{'samplers':['temperature'],'temperature':0,'seed':20260907,
               'n_predict':32,'ignore_eos':False,'stop':[],'stream':True,'grammar':'','lora':[],
               'backend_sampling':False}}
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
        try:
            with tempfile.TemporaryDirectory() as raw:
                for index,records in enumerate(([progress,partial,final],[progress,partial],[progress])):
                    Handler.records=records
                    path=Path(raw)/f'{index}.jsonl'
                    result=_stream(f'http://127.0.0.1:{server.server_port}',completion_payload([1,2,3],0,False),
                        path,threading.Event(),request_id='r000',arrival_ns=1,admitted_ns=2,prompt_count=3)
                    self.assertEqual([10,11] if index<2 else [],result['output_token_ids'])
                    self.assertEqual('KEY' if index<2 else '',result['output_text'])
                    if index<2:self.assertGreater(result['first_token_ns'],result['dispatch_ns'])
                    else:self.assertIsNone(result['first_token_ns'])
                    self.assertEqual('SUCCEEDED' if index==0 else 'FAILED',result['status'])
                    self.assertEqual(3 if index==0 else None,result['generated_tokens'])
                    events,torn=read_journal(path)
                    self.assertFalse(torn);self.assertGreaterEqual(len(events),2)
        finally:
            server.shutdown();server.server_close();worker.join()

    def test_both_arms_use_identical_bounded_engine_arguments(self):
        args=server_arguments(Path('/reviewed/server'),Path('/reviewed/model'),4,40001)
        self.assertEqual('127.0.0.1',args[args.index('--host')+1])
        self.assertEqual('2',args[args.index('--threads')+1])
        self.assertEqual('0',args[args.index('--cache-ram')+1])
        self.assertIn('--no-cache-idle-slots',args)
        self.assertIn('--no-kv-unified',args)
        self.assertIn('--no-warmup',args)
        self.assertIn('--offline',args)

    def test_stop_only_owned_process_group(self):
        child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(300)'],start_new_session=True)
        try:
            stop_owned_process(child)
            self.assertIsNotNone(child.poll())
            stop_owned_process(child)  # Idempotent; no PID reuse targeting after reap.
        finally:
            if child.poll() is None:child.kill();child.wait()


if __name__=='__main__':unittest.main()

class ProcessDescendantTests(unittest.TestCase):
    def test_cleanup_after_group_leader_exits(self):
        import os,time
        from lean_model_lab.runner import _group_members
        child=subprocess.Popen([sys.executable,'-c',
            'import os,time;pid=os.fork();time.sleep(30) if pid==0 else None'],
            start_new_session=True)
        try:
            child.wait(timeout=3)
            self.assertTrue(_group_members(child.pid))
            stop_owned_process(child)
            self.assertFalse(_group_members(child.pid))
        finally:
            stop_owned_process(child)
