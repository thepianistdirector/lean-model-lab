import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from lean_model_lab.contracts import ContractError,make_workload
from lean_model_lab.recovery import reconcile_unfinished
from lean_model_lab.session import Session
from test_evidence import CONFIG,make_attempt


class RecoveryTests(unittest.TestCase):
    def test_orphan_closure_keeps_checkpoint_and_real_wall_gap(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw)/'study';Session.create(root,CONFIG,make_workload(),[])
            with Session.open(root) as session:
                attempt=make_attempt();reservation=session.reserve('baseline',1,0,attempt['started_ns'])
                request=attempt['requests'][0];session.checkpoint(reservation['attempt_id'],request,request['completed_ns']+1)
            with Session.open(root) as session,patch('lean_model_lab.recovery.current_boot',return_value='TEST_FIXTURE'):
                before=time.monotonic_ns();ids=reconcile_unfinished(session)
                inventory=session.inspect();closed=inventory['attempts'][0]
                self.assertEqual([reservation['attempt_id']],ids)
                self.assertEqual('INTERRUPTED',closed['status'])
                self.assertEqual([request],closed['requests'])
                self.assertGreaterEqual(closed['finished_ns'],before)
                self.assertTrue(inventory['inventory_complete'])
                next_attempt=session.reserve('baseline',1,0,time.monotonic_ns())
                self.assertNotEqual(reservation['attempt_id'],next_attempt['attempt_id'])

    def test_cross_boot_recovery_refuses_to_invent_elapsed_time(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw)/'study';Session.create(root,CONFIG,make_workload(),[])
            with Session.open(root) as session:
                session.reserve('baseline',1,0,1)
                with self.assertRaises(ContractError):reconcile_unfinished(session)
                self.assertEqual([],session.inspect()['attempts'])


if __name__=='__main__':unittest.main()
