import tempfile
import unittest
from pathlib import Path
from lean_model_lab.artifacts import append_event, read_journal, write_json_new


class ArtifactTests(unittest.TestCase):
    def test_no_overwrite_and_no_partial_artifact_left(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw);target=root/'result.json'
            write_json_new(target, {'status':'FAILED','consumed_ns':14})
            original=target.read_bytes()
            with self.assertRaises(FileExistsError):
                write_json_new(target, {'status':'SUCCEEDED','consumed_ns':0})
            self.assertEqual(original,target.read_bytes())
            self.assertEqual([target],list(root.iterdir()))

    def test_recovery_preserves_cost_before_torn_final_record(self):
        with tempfile.TemporaryDirectory() as raw:
            path=Path(raw)/'events.jsonl'
            append_event(path,{'kind':'started','attempt_id':'first'})
            append_event(path,{'kind':'usage','elapsed_ns':500})
            with path.open('ab') as output: output.write(b'{"kind":"terminal"')
            original=path.read_bytes()
            records,torn=read_journal(path)
            self.assertTrue(torn)
            self.assertEqual(500,records[1]['elapsed_ns'])
            self.assertEqual(original,path.read_bytes())

    def test_conflicting_and_nonfinite_usage_are_not_recovered(self):
        with tempfile.TemporaryDirectory() as raw:
            path=Path(raw)/'events.jsonl'
            for payload in (b'{"kind":"usage","elapsed_ns":500,"elapsed_ns":0}\n',
                            b'{"kind":"usage","elapsed_ns":NaN}\n'):
                path.write_bytes(payload)
                with self.assertRaises(ValueError):read_journal(path)

    def test_interior_corruption_is_not_hidden(self):
        with tempfile.TemporaryDirectory() as raw:
            path=Path(raw)/'events.jsonl'
            path.write_bytes(b'{broken}\n{"kind":"usage","elapsed_ns":10}\n')
            with self.assertRaises(ValueError): read_journal(path)


if __name__=='__main__': unittest.main()
