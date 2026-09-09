"""End-to-end coordinator fixture: actual HTTP/processes, no model or performance claim."""
import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from lean_model_lab.config import make_config
from lean_model_lab.contracts import file_digest,make_workload
from lean_model_lab.runner import execute_attempt,hardware
from lean_model_lab.session import Session


class CoordinatorTests(unittest.TestCase):
    def test_completed_and_interrupted_fixture_keep_attempts_and_costs(self):
        import lean_model_lab.runner as runner
        for interrupt in (False,True):
            with self.subTest(interrupt=interrupt),tempfile.TemporaryDirectory() as raw:
                root=Path(raw);server=root/'fixture-server';model=root/'fixture-model'
                source=Path(__file__).parent/'fixtures'/'native_server.py'
                server.write_text('#!'+sys.executable+'\n'+source.read_text());server.chmod(0o700)
                model.write_bytes(b'INERT TEST FIXTURE: NO WEIGHTS')
                config=make_config(server_sha256=file_digest(server),evidence_class='TEST_FIXTURE',hardware=hardware())
                study=root/'study';workload=make_workload();Session.create(study,config,workload,[])
                original=runner._stream
                def stop_after_first(*args,**kwargs):
                    result=original(*args,**kwargs);args[3].set();return result
                with Session.open(study) as session,patch.object(runner,'MODEL_SHA256',file_digest(model)):
                    with patch.object(runner,'_stream',stop_after_first if interrupt else original):
                        result=execute_attempt(session,server=server,model=model,config=config,workload=workload,
                            concurrency=1 if interrupt else 4,pair_index=0,arm='baseline',
                            deadline_ns=time.monotonic_ns()+30*10**9,project_root=root)
                    self.assertEqual('INTERRUPTED' if interrupt else 'COMPLETED',result['status'])
                    self.assertEqual(1 if interrupt else 128,len(result['requests']))
                    self.assertEqual('TEST_FIXTURE',result['evidence_class'])
                    inventory=session.inspect()
                    self.assertTrue(inventory['inventory_complete'])
                    self.assertEqual(1,len(inventory['attempts']))
                    self.assertGreater(inventory['setup_accounting']['full_wall_ns'],0)
                    for request in result['requests']:
                        self.assertEqual(6,request['generated_tokens'])
                        self.assertEqual(5,len(request['output_token_ids']))
                        self.assertNotIn(0,request['output_token_ids'])
                        self.assertIsNone(request['engine_start_ns'])


if __name__=='__main__':unittest.main()
