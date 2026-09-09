import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from lean_model_lab.contracts import file_digest,make_workload
from lean_model_lab.session import Session
from lean_model_lab.study_report import evaluate_inventory
from test_evidence import CONFIG,make_campaign


def setup_records():
    return [{'phase':name,'status':'COMPLETED','started_ns':i*100+1,'finished_ns':i*100+50,
             'bytes_acquired':0,'details':'model-free receipt fixture'}
            for i,name in enumerate(('source-acquisition','model-acquisition','build'))]


def fixture_study(root):
    Session.create(root,CONFIG,make_workload(),setup_records())
    with Session.open(root) as session:
        for attempt in make_campaign():
            reservation=session.reserve(attempt['arm'],attempt['concurrency'],attempt['pair_index'],attempt['started_ns'])
            attempt['attempt_id']=reservation['attempt_id'];session.publish(attempt)
        return session.inspect()


class StudyReportTests(unittest.TestCase):
    def test_earlier_protocol_failure_cannot_disappear_after_client_correction(self):
        with tempfile.TemporaryDirectory() as raw:
            inventory=fixture_study(Path(raw)/'study')
            inventory['setup_accounting']['records'].append({'phase':'runtime-protocol-validation',
                'status':'FAILED','started_ns':251,'finished_ns':900,'bytes_acquired':0,
                'details':'retained earlier model attempt; separate immutable inventory'})
            result=evaluate_inventory(inventory)
            self.assertFalse(result['eligible'])
            self.assertFalse(result['measured_claim_eligible'])
            self.assertIn('retained_prior_runtime_protocol_failure',result['ineligibility_reasons'])
            self.assertEqual(1,len(result['accounting']['prior_runtime_protocol_failures']))
            self.assertTrue(all(not g['eligible'] for g in result['concurrency_groups'].values()))

    def test_export_leaves_producer_evidence_unchanged_and_records_renderer_separately(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);study=root/'study';fixture_study(study)
            before={str(p.relative_to(study)):file_digest(p) for p in study.rglob('*') if p.is_file()}
            output=root/'report.json'
            result=subprocess.run([sys.executable,'-m','lean_model_lab','report',str(study),'--output',str(output)],
                                   text=True,capture_output=True,check=False)
            self.assertEqual(0,result.returncode,result.stderr)
            after={str(p.relative_to(study)):file_digest(p) for p in study.rglob('*') if p.is_file()}
            self.assertEqual(before,after)
            self.assertTrue(output.with_suffix('.json.receipt.json').exists())
            with Session.open(study) as session:self.assertEqual(3,session.inspect()['setup_accounting']['record_count'])

    def test_full_wall_budget_remains_a_gate_even_when_request_pairs_pass(self):
        with tempfile.TemporaryDirectory() as raw:
            inventory=fixture_study(Path(raw)/'study')
            # A long retained producer-side finalization cannot disappear from costs.
            last=inventory['attempts'][-1]['finished_ns']
            inventory['setup_accounting']['records'].append({'phase':'artifact-finalization','status':'COMPLETED',
                'started_ns':last+1,'finished_ns':last+7201*10**9,'bytes_acquired':0,'details':'synthetic over-budget fixture'})
            result=evaluate_inventory(inventory)
            self.assertFalse(result['eligible'])
            self.assertFalse(result['measured_claim_eligible'])
            self.assertIn('registered_full_wall_allocation_exceeded',result['ineligibility_reasons'])
            self.assertTrue(all(not g['eligible'] for g in result['concurrency_groups'].values()))


if __name__=='__main__':unittest.main()
