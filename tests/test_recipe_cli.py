"""Freeze/revalidate user recipes without downloading or executing a model."""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from lean_model_lab.config import validate_config
from lean_model_lab.contracts import ContractError
from test_evidence_v2 import fixture


class RecipeCLITests(unittest.TestCase):
    def invoke(self,*args):
        return subprocess.run([sys.executable,'-m','lean_model_lab',*map(str,args)],capture_output=True,text=True)

    def test_roundtrip_and_refused_overwrite_with_nondefault_arrivals(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);_,config=fixture();allocation=root/'allocation.json';recipe=root/'recipe.json'
            allocation.write_text(json.dumps(config['recipe']['allocation']))
            args=['recipe','create','--allocation',allocation,'--model-profile','qwen2.5-14b-instruct-fp16-v1',
                  '--output',recipe,'--arrival','burst','--interval-ms','100','--burst-size','4',
                  '--concurrency','1','4','--pairs','4','--queue-capacity','16','--seed','45','--max-output-tokens','64']
            created=self.invoke(*args);self.assertEqual(created.returncode,0,created.stderr)
            self.assertFalse(json.loads(created.stdout)['inference_performed']);before=recipe.read_bytes()
            validated=self.invoke('recipe','validate',recipe);self.assertEqual(validated.returncode,0,validated.stderr)
            self.assertEqual(json.loads(created.stdout),json.loads(validated.stdout))
            self.assertEqual(self.invoke(*args).returncode,2);self.assertEqual(before,recipe.read_bytes())
            value=json.loads(before);value['evaluation']['minimum_accuracy']=0
            recipe.write_text(json.dumps(value));self.assertEqual(self.invoke('recipe','validate',recipe).returncode,2)

    def test_config_rejects_changed_shard_clock_sampling_or_recipe_even_with_new_hash(self):
        _,config=fixture()
        edits=[lambda c:c['model']['artifacts'][0].update(sha256='f'*64),
               lambda c:c['clock'].update(boot_id='foreign'),
               lambda c:c['sampling'].update(max_output_tokens=64),
               lambda c:c['engine'].update(compute_threads=13),
               lambda c:c['recipe'].update(purpose='DEVELOPMENT')]
        for edit in edits:
            value=copy.deepcopy(config);edit(value)
            with self.assertRaises(ContractError):validate_config(value)

if __name__=='__main__':unittest.main()
