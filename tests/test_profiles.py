from __future__ import annotations
import copy
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch
from lean_model_lab.allocation import validate_allocation
from lean_model_lab.contracts import ContractError,digest
from lean_model_lab.profiles import get_model_profile,profile_sha256,verify_model_files

PROFILE='qwen2.5-14b-instruct-fp16-v1'

class ProfileTests(unittest.TestCase):
    def test_corrected_small_profile_matches_independent_pinned_file_evidence(self):
        import json
        root=Path(__file__).resolve().parents[1]
        source=json.loads((root/'docs/evidence/0.5b-profile-size-source-20260908.json').read_text())['entry']
        metadata=json.loads((root/'docs/evidence/gguf-metadata-inventory.json').read_text())
        old=get_model_profile('qwen2.5-0.5b-instruct-fp16-v1')
        new=get_model_profile('qwen2.5-0.5b-instruct-fp16-v2')
        self.assertEqual(new['files'][0]['bytes'],source['size'])
        self.assertEqual(new['files'][0]['bytes'],metadata['file_bytes'])
        self.assertEqual(new['files'][0]['sha256'],source['lfs']['oid'])
        self.assertEqual(new['files'][0]['sha256'],metadata['model_sha256'])
        self.assertEqual(old['files'][0]['sha256'],new['files'][0]['sha256'])
        self.assertEqual(old['files'][0]['bytes']-new['files'][0]['bytes'],78)
        self.assertNotEqual(digest(old),digest(new))

    def test_exact_complete_large_profile_and_copy_isolation(self):
        p=get_model_profile(PROFILE)
        self.assertEqual(len(p['files']),8)
        self.assertEqual(sum(f['bytes'] for f in p['files']),29547716864)
        self.assertEqual(p['entrypoint'],p['files'][0]['filename'])
        before=profile_sha256(PROFILE);p['files'][1]['sha256']='0'*64
        self.assertEqual(profile_sha256(PROFILE),before)
        with self.assertRaises(ContractError):get_model_profile('unreviewed/model')

    def test_every_shard_is_verified_and_missing_or_changed_secondary_refused(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);parts=[{'filename':f'model-{i}.gguf','bytes':1,'sha256':str(i)*64} for i in range(3)]
            fixture={'profile_id':'fixture','entrypoint':'model-0.gguf','files':parts}
            for part in parts:(root/part['filename']).write_bytes(b'a')
            with patch('lean_model_lab.profiles.get_model_profile',return_value=fixture),patch('lean_model_lab.profiles.file_digest',side_effect=['0'*64,'1'*64,'2'*64]) as hashes:
                self.assertEqual(verify_model_files(root/'model-0.gguf','fixture')['total_bytes'],3)
                self.assertEqual(hashes.call_count,3)
            (root/'model-1.gguf').unlink()
            with patch('lean_model_lab.profiles.get_model_profile',return_value=fixture),self.assertRaises(ContractError):verify_model_files(root/'model-0.gguf','fixture')
            (root/'model-1.gguf').write_bytes(b'b')
            with patch('lean_model_lab.profiles.get_model_profile',return_value=fixture),patch('lean_model_lab.profiles.file_digest',side_effect=['0'*64,'f'*64]),self.assertRaises(ContractError):verify_model_files(root/'model-0.gguf','fixture')

    def test_hash_checks_cancellation_between_chunks(self):
        from lean_model_lab.contracts import file_digest
        with tempfile.TemporaryDirectory() as raw:
            model=Path(raw)/'fixture';model.write_bytes(b'x'*(4*1024*1024))
            calls=[]
            def check():
                calls.append(True)
                if len(calls)==4:raise RuntimeError('cancelled fixture')
            with self.assertRaisesRegex(RuntimeError,'cancelled fixture'):file_digest(model,check=check)
            self.assertEqual(len(calls),4)

    def test_allocation_is_bounded_clock_bound_and_never_restarted(self):
        started=time.monotonic_ns()-1000000
        value={'schema_version':2,'allocation_id':'fixture-allocation','approved':True,'approval_reference':'test operator record',
            'observed_utc':'2026-09-08T00:00:00+00:00','boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
            'started_ns':started,'deadline_ns':started+43200*10**9,'limits':{'full_wall_seconds':43200,'disk_bytes':200000000000,'memory_bytes':60000000000,'compute_threads':12,'max_heavy_jobs':1},'scope':'test fixture; no inference'}
        self.assertIs(validate_allocation(value,active=True),value)
        for field,bad in [('compute_threads',13),('memory_bytes',60000000001),('disk_bytes',200000000001),('full_wall_seconds',43201),('max_heavy_jobs',2),('compute_threads',True)]:
            mutated=copy.deepcopy(value);mutated['limits'][field]=bad
            with self.subTest(field=field,bad=bad),self.assertRaises(ContractError):validate_allocation(mutated)
        for field,bad in [('approved',False),('deadline_ns',value['deadline_ns']+1),('boot_id','unbound')]:
            mutated=copy.deepcopy(value);mutated[field]=bad
            with self.subTest(field=field),self.assertRaises(ContractError):validate_allocation(mutated,active=True)
        expired=copy.deepcopy(value);expired['started_ns']=1;expired['deadline_ns']=1+43200*10**9
        with self.assertRaises(ContractError):validate_allocation(expired,active=True)
        validate_allocation(expired)  # Historical receipt remains statically inspectable.

if __name__=='__main__':unittest.main()
