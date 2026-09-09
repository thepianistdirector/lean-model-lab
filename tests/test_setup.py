import copy
import time
import unittest
from lean_model_lab.contracts import ContractError
from lean_model_lab.llama_adapter import BACKEND_COMMIT,BACKEND_PATCH_SHA256,MODEL_SHA256
from lean_model_lab.setup import validate_receipt


class SetupTests(unittest.TestCase):
    def make(self):
        return {'schema_version':1,'boot_id':'fixture-boot','records':[
            {'phase':phase,'status':'COMPLETED','started_ns':i*100+1,'finished_ns':i*100+99,
             'bytes_acquired':10,'details':'synthetic receipt validator fixture'}
            for i,phase in enumerate(('source-acquisition','model-acquisition','build'))],
            'artifacts':{'backend_revision':BACKEND_COMMIT,'backend_patch_sha256':BACKEND_PATCH_SHA256,
                         'model_sha256':MODEL_SHA256,'server_sha256':'a'*64}}

    def test_source_model_binary_clock_and_cost_receipt(self):
        receipt=self.make();validate_receipt(receipt,boot_id='fixture-boot')
        mutations=[lambda r:r.update(boot_id='other'),lambda r:r['artifacts'].update(backend_revision='latest'),
                   lambda r:r['artifacts'].update(backend_patch_sha256='0'*64),
                   lambda r:r['artifacts'].update(model_sha256='b'*64),lambda r:r['records'].pop(),
                   lambda r:r['records'][0].update(finished_ns=-1),
                   lambda r:r['records'][1].update(started_ns=1),
                   lambda r:r['records'][1].update(bytes_acquired=True),
                   lambda r:r['records'][2].update(finished_ns=time.monotonic_ns()+10**12)]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                bad=copy.deepcopy(receipt);mutate(bad)
                with self.assertRaises(ContractError):validate_receipt(bad,boot_id='fixture-boot')


if __name__=='__main__':unittest.main()
