"""Real process/HTTP recipe integration with an inert synthetic server, not a model."""
import json
import subprocess
import threading
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from lean_model_lab.config import make_config_v2
from lean_model_lab.contracts import digest,file_digest
from lean_model_lab.recipes import make_recipe
from lean_model_lab.runner import execute_attempt,hardware
from lean_model_lab.session import Session
from lean_model_lab.workloads import make_workload_v2
from lean_model_lab.evidence import summarize_attempt


def inputs(root,*,modes=(1,),**kwargs):
    server=root/'fixture-server';model=root/'fixture-model'
    source=Path(__file__).parent/'fixtures/native_server.py'
    server.write_text('#!'+sys.executable+'\n'+source.read_text());server.chmod(0o700)
    model.write_bytes(b'INERT TEST INPUT; NO WEIGHTS')
    workload=make_workload_v2(request_count=8,concurrency_modes=modes,**kwargs)
    now=time.monotonic_ns()
    allocation={'schema_version':2,'allocation_id':'coordinator-fixture','approved':True,
        'approval_reference':'unit-test fixture, no inference authority','observed_utc':'2026-09-08',
        'boot_id':'TEST_FIXTURE','started_ns':now,'deadline_ns':now+60*10**9,
        'limits':{'full_wall_seconds':60,'disk_bytes':2000000000,'memory_bytes':4000000000,'compute_threads':2,'max_heavy_jobs':1},
        'scope':'inert local process and HTTP fixture'}
    recipe=make_recipe(model_profile_id='qwen2.5-0.5b-instruct-fp16-v1',workload=workload,
        allocation=allocation,compute_threads=2,pair_count=2,purpose='DEVELOPMENT')
    config=make_config_v2(recipe=recipe,server_sha256=file_digest(server),evidence_class='TEST_FIXTURE',
        hardware=hardware(),implementation_sha256='a'*64)
    return workload,config,server,model


class CoordinatorV2Tests(unittest.TestCase):
    def run_fixture(self,**kwargs):
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup);root=Path(temporary.name)
        workload,config,server,model=inputs(root,**kwargs)
        study=root/'study';Session.create(study,config,workload,[])
        with Session.open(study) as session,patch('lean_model_lab.runner_recipe.verify_model_files',return_value={'scope':'INERT FIXTURE'}):
            attempt=execute_attempt(session,server=server,model=model,config=config,workload=workload,
                concurrency=1,pair_index=0,arm='baseline',deadline_ns=config['recipe']['allocation']['deadline_ns'],project_root=root)
            inventory=session.inspect()
        self.assertTrue(inventory['inventory_complete']);self.assertEqual(attempt['schema_version'],2)
        summary=summarize_attempt(attempt,workload,config=config,config_sha256=digest(config),workload_sha256=digest(workload))
        return attempt,summary,workload,config,study

    def test_checkpoint_failure_cancels_other_worker_before_pool_shutdown(self):
        from lean_model_lab.runner_recipe import _stream as actual_stream
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);workload,config,server,model=inputs(root,modes=(2,))
            Session.create(root/'study',config,workload,[])
            blocked=threading.Event();cancel_seen=threading.Event()
            def stream(base,payload,path,cancel,**kwargs):
                if payload['id_slot']==1:
                    blocked.set()
                    if cancel.wait(4):cancel_seen.set()
                else:self.assertTrue(blocked.wait(2))
                return actual_stream(base,payload,path,cancel,**kwargs)
            with Session.open(root/'study') as session, patch('lean_model_lab.runner_recipe.verify_model_files',return_value={}), patch('lean_model_lab.runner_recipe._stream',side_effect=stream), patch.object(session,'checkpoint',side_effect=OSError('injected checkpoint write failure')):
                start=time.monotonic()
                attempt=execute_attempt(session,server=server,model=model,config=config,workload=workload,
                    concurrency=2,pair_index=0,arm='baseline',deadline_ns=config['recipe']['allocation']['deadline_ns'],project_root=root)
                self.assertLess(time.monotonic()-start,3)
                self.assertTrue(cancel_seen.is_set());self.assertEqual(attempt['status'],'INTERRUPTED')
                self.assertTrue(session.inspect()['inventory_complete'])

    def test_version_timeout_closes_reserved_attempt(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);workload,config,server,model=inputs(root)
            Session.create(root/'study',config,workload,[])
            with Session.open(root/'study') as session, patch('lean_model_lab.runner_recipe.verify_model_files',return_value={}), patch('lean_model_lab.runner_recipe.subprocess.run',side_effect=subprocess.TimeoutExpired('fixture --version',.01)):
                attempt=execute_attempt(session,server=server,model=model,config=config,workload=workload,
                    concurrency=1,pair_index=0,arm='baseline',deadline_ns=config['recipe']['allocation']['deadline_ns'],project_root=root)
                self.assertEqual(attempt['status'],'FAILED');self.assertEqual(attempt['requests'],[])
                self.assertTrue(session.inspect()['inventory_complete'])

    def test_cancelled_hashing_never_invokes_backend_version(self):
        import os,signal
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);workload,config,server,model=inputs(root)
            Session.create(root/'study',config,workload,[])
            def verify(*args,check):
                os.kill(os.getpid(),signal.SIGTERM);check()
            with Session.open(root/'study') as session, patch('lean_model_lab.runner_recipe.verify_model_files',side_effect=verify), patch('lean_model_lab.runner_recipe.subprocess.run') as version:
                attempt=execute_attempt(session,server=server,model=model,config=config,workload=workload,
                    concurrency=1,pair_index=0,arm='baseline',deadline_ns=config['recipe']['allocation']['deadline_ns'],project_root=root)
                version.assert_not_called();self.assertEqual(attempt['status'],'INTERRUPTED')
                self.assertTrue(session.inspect()['inventory_complete'])

    def test_paced_native_requests_use_frozen_seed_budget_and_actual_arrivals(self):
        attempt,summary,workload,_,_=self.run_fixture(arrival_mode='paced',interval_ns=10000000,seed=45,max_output_tokens=64)
        self.assertEqual(attempt['status'],'COMPLETED');self.assertEqual(summary['succeeded_requests'],8)
        by_id={r['request_id']:r for r in attempt['requests']}
        for expected in workload['requests']:
            row=by_id[expected['request_id']]
            self.assertEqual(row['arrival_ns'],attempt['service_started_ns']+expected['arrival_offset_ns'])
            self.assertGreaterEqual(row['admitted_ns'],row['arrival_ns'])
            self.assertEqual(row['output_text'],expected['expected'])
        self.assertFalse(summary['eligible'])  # Development population, never a measurement claim.

    def test_overflow_retains_unadmitted_requests_and_full_denominator(self):
        attempt,summary,workload,_,_=self.run_fixture(max_queue_requests=1)
        self.assertEqual(attempt['status'],'COMPLETED');self.assertEqual(len(attempt['requests']),8)
        rejected=[r for r in attempt['requests'] if r['status']=='REJECTED']
        self.assertEqual(len(rejected),6);self.assertEqual(summary['quality_denominator'],8)
        self.assertEqual(summary['quality_correct'],2)
        for r in rejected:self.assertIsNone(r['admitted_ns']);self.assertIsNone(r['dispatch_ns']);self.assertEqual(r['generated_tokens'],0)
        self.assertEqual(summary['serving']['rejected_requests'],6)

    def test_expired_before_dispatch_has_no_engine_or_fabricated_tokens(self):
        attempt,summary,_,_,study=self.run_fixture(request_deadline_ns=1)
        self.assertEqual(attempt['status'],'COMPLETED');self.assertEqual(summary['serving']['expired_requests'],8)
        self.assertEqual(summary['serving']['admitted_requests'],0)
        for r in attempt['requests']:
            self.assertEqual(r['status'],'EXPIRED');self.assertEqual(r['token_events'],[])
            self.assertIsNone(r['dispatch_ns']);self.assertIsNone(r['first_token_ns'])
        raw=study/'raw'/attempt['attempt_id']
        self.assertTrue(all('engine_dispatched' in json.loads((raw/(r['request_id']+'.jsonl')).read_text()) for r in attempt['requests']))

if __name__=='__main__':unittest.main()
