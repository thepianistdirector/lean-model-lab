import copy
import json
import tempfile
import unittest
from pathlib import Path

from lean_model_lab.contracts import ContractError, digest, make_workload, read_json, validate_workload


class WorkloadTests(unittest.TestCase):
    def test_reproducible_population_and_answers(self):
        first = make_workload()
        self.assertEqual(digest(first), digest(make_workload()))
        validate_workload(first)
        self.assertEqual(128, len({r['request_id'] for r in first['requests']}))
        for r in first['requests']:
            self.assertIn('KEY: '+r['expected']+'\n', r['prompt'])
            filler = r['prompt'].split('FILLER: ')[1].split('\n')[0]
            self.assertEqual(r['stratum'], len(filler.split()))

    def test_comparison_semantics_cannot_drift(self):
        mutations = [
            lambda w: w['requests'].pop(),
            lambda w: w['requests'].append(copy.deepcopy(w['requests'][0])),
            lambda w: w['requests'][0].update(expected='OTHER'),
            lambda w: w['requests'][0].update(prompt='shortened'),
            lambda w: w['requests'][0].update(arrival_offset_ns=-1),
            lambda w: w['quality'].update(minimum_accuracy=0.5),
            lambda w: w['sampling'].update(temperature=1),
            lambda w: w.update(concurrency_modes=[1]),
            lambda w: w.update(schema_version=True),
            lambda w: w.update(max_output_tokens=8),
            lambda w: w.update(unknown=True),
        ]
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                w = make_workload(); mutate(w)
                with self.assertRaises(ContractError): validate_workload(w)

    def test_duplicate_keys_and_nonfinite_json_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw)/'input.json'
            for text in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
                path.write_text(text)
                with self.assertRaises(ContractError): read_json(path)
            path.write_text('{"x":1}')
            with self.assertRaises(ContractError): read_json(path,max_bytes=2)


if __name__ == '__main__': unittest.main()
