import copy
import unittest
from lean_model_lab.admission import proposal,validate_admission
from lean_model_lab.contracts import ContractError


class AdmissionTests(unittest.TestCase):
    def test_pending_is_not_permission_and_approval_cannot_expand_envelope(self):
        record=proposal()
        with self.assertRaises(ContractError):validate_admission(record)
        record.update(approved=True,approval_reference='test fixture operator decision; no model execution')
        validate_admission(record)
        for mutate in (lambda r:r['limits'].update(memory_bytes=99999999999),
                       lambda r:r.update(model_sha256='b'*64),lambda r:r.update(approved=1)):
            bad=copy.deepcopy(record);mutate(bad)
            with self.assertRaises(ContractError):validate_admission(bad)


if __name__=='__main__':unittest.main()
