import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CLITests(unittest.TestCase):
    def invoke(self, *arguments):
        return subprocess.run([sys.executable, '-m', 'lean_model_lab', *map(str, arguments)],
                              text=True, capture_output=True, check=False)

    def test_create_validate_and_no_clobber(self):
        with tempfile.TemporaryDirectory() as raw:
            target=Path(raw)/'trace.json'
            created=self.invoke('trace','create','--output',target)
            self.assertEqual(0,created.returncode,created.stderr)
            self.assertEqual('MODEL_FREE_CONTRACT',json.loads(created.stdout)['evidence'])
            original=target.read_bytes()
            self.assertEqual(0,self.invoke('trace','validate',target).returncode)
            self.assertEqual(2,self.invoke('trace','create','--output',target).returncode)
            self.assertEqual(original,target.read_bytes())
            data=json.loads(original);data['quality']['minimum_accuracy']=0
            target.write_text(json.dumps(data))
            rejected=self.invoke('trace','validate',target)
            self.assertEqual(2,rejected.returncode)
            self.assertIn('frozen',rejected.stderr)


    def test_evaluator_rejects_changed_model_even_with_consistent_hashes(self):
        import copy
        from test_evidence import CONFIG, make_campaign
        from lean_model_lab.contracts import digest, make_workload
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);(root/'attempts').mkdir()
            config=copy.deepcopy(CONFIG)
            config['model']['repository']='unreviewed/other'
            (root/'config.json').write_text(json.dumps(config))
            (root/'workload.json').write_text(json.dumps(make_workload()))
            for index,attempt in enumerate(make_campaign()):
                attempt['config_sha256']=digest(config)
                (root/'attempts'/f'{index}.json').write_text(json.dumps(attempt))
            result=self.invoke('evaluate','--workload',root/'workload.json','--config',root/'config.json',
                               '--attempts',root/'attempts','--output',root/'result.json')
            self.assertEqual(2,result.returncode,result.stdout)
            self.assertIn('fixed model',result.stderr)
            self.assertFalse((root/'result.json').exists())


if __name__=='__main__': unittest.main()
