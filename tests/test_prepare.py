import importlib.util
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from lean_model_lab.contracts import ContractError

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('prepare_backend',ROOT/'tools/prepare_backend.py')
prepare=importlib.util.module_from_spec(spec);spec.loader.exec_module(prepare)


class PreparationTests(unittest.TestCase):
    def test_gcc8_requires_existing_filesystem_library_and_other_versions_do_not_add_it(self):
        with patch.object(prepare.subprocess,'check_output',side_effect=['8.5.0','/missing/libstdc++fs.a']):
            with self.assertRaisesRegex(ContractError,'unavailable'):
                prepare.native_build_options({})
        with patch.object(prepare.subprocess,'check_output',return_value='12.1.0') as calls:
            self.assertNotIn('CMAKE_CXX_STANDARD_LIBRARIES',prepare.native_build_options({}))
            self.assertEqual(1,calls.call_count)

    def test_pending_admission_creates_no_download_or_build(self):
        with tempfile.TemporaryDirectory() as raw:
            output=Path(raw)/'unapproved'
            result=subprocess.run([sys.executable,str(ROOT/'tools/prepare_backend.py'),'--admission',
                str(ROOT/'docs/decisions/admission-proposal.json'),'--output',str(output)],capture_output=True,text=True)
            self.assertEqual(2,result.returncode,result.stdout)
            self.assertIn('admission is pending',result.stderr)
            self.assertFalse(output.exists())

    def test_unknown_redirect_is_rejected_before_following_it(self):
        for url in ('http://huggingface.co/model','https://127.0.0.1/private','https://evil.example/model',
                    'https://huggingface.co.evil.example/model','https://user:pass@hf.co/model','https://hf.co:8443/model'):
            with self.subTest(url=url),self.assertRaises(ContractError):prepare.reviewed_model_url(url)
        self.assertEqual('https://cas-bridge.xethub.hf.co/model',prepare.reviewed_model_url('https://cas-bridge.xethub.hf.co/model'))


if __name__=='__main__':unittest.main()
