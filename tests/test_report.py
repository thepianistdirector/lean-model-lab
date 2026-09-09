import copy
import unittest
from lean_model_lab.contracts import digest, make_workload
from lean_model_lab.evidence import evaluate_campaign
from lean_model_lab.report import render_report
from test_evidence import CONFIG, CONFIG_SHA256, make_campaign


class ReportTests(unittest.TestCase):
    def test_fixture_labels_full_attempts_and_escaped_content(self):
        workload=make_workload()
        attempts=make_campaign()
        attempts[0]['attempt_id']='<script>alert(1)</script>'
        result=evaluate_campaign(attempts,workload,config=CONFIG,config_sha256=CONFIG_SHA256,workload_sha256=digest(workload))
        html=render_report(result)
        self.assertIn('NO MODEL INFERENCE',html)
        self.assertNotIn('<script>',html)
        self.assertIn('&lt;script&gt;',html)
        self.assertIn('scope="col"',html)
        self.assertIn('tabindex="0"',html)
        self.assertEqual(13,html.count('<tr>'))
        self.assertIn('separate setup ledger',html)
        self.assertIn('TEST_FIXTURE_ONLY',html)
        self.assertNotIn('https://',html)


if __name__=='__main__': unittest.main()
