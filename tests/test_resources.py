import tempfile
import os
from unittest.mock import patch
import unittest
from pathlib import Path
from lean_model_lab.resources import heavy_job,require_workspace_root
from lean_model_lab.contracts import ContractError


class ResourceTests(unittest.TestCase):
    def test_nested_cwd_and_outside_artifacts_cannot_change_lease_or_disk_scope(self):
        root=Path(__file__).resolve().parents[1]
        temporary_root=root/'.cache/tmp';temporary_root.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=temporary_root) as raw:
            nested=Path(raw)/'nested';nested.mkdir()
            with patch('pathlib.Path.cwd',return_value=root):
                self.assertEqual(require_workspace_root(nested/'new-study'),root)
                with self.assertRaises(ContractError):require_workspace_root(root.parent/'outside')
            with patch('pathlib.Path.cwd',return_value=nested):
                with self.assertRaisesRegex(ContractError,'outermost'):require_workspace_root()
                # A copied nested marker cannot create another lease namespace.
                (nested/'WORKSPACE.json').write_bytes((root/'WORKSPACE.json').read_bytes())
                with self.assertRaisesRegex(ContractError,'outermost'):require_workspace_root()
            with patch('pathlib.Path.cwd',return_value=root.parent):
                with self.assertRaisesRegex(ContractError,'supplied source'):require_workspace_root()

    def test_distinct_studies_cannot_share_one_project_heavy_slot(self):
        with tempfile.TemporaryDirectory() as raw:
            root=Path(raw)
            with heavy_job(root):
                with self.assertRaises(RuntimeError):
                    with heavy_job(root):self.fail('second heavy job admitted')
            with heavy_job(root):pass


if __name__=='__main__':unittest.main()
