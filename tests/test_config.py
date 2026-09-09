import copy
import unittest
from lean_model_lab.config import make_config, validate_config
from lean_model_lab.contracts import ContractError


class ConfigTests(unittest.TestCase):
    def setUp(self):
        self.config=make_config(server_sha256='a'*64,evidence_class='TEST_FIXTURE',
                                hardware={'platform':'fixture','cpu':'fixture'})

    def test_exact_supported_family_validates(self):
        validate_config(self.config)

    def test_mutations_cannot_hide_behind_new_digest(self):
        mutations=[lambda c:c['model'].update(repository='other/model'),
                   lambda c:c['model'].update(gguf_sha256='b'*64),
                   lambda c:c['tokenizer'].update(gguf_sha256='b'*64),
                   lambda c:c['sampling'].update(temperature=0.9),
                   lambda c:c['candidate'].update(field='temperature'),
                   lambda c:c['engine'].update(cache_ram_mib=1024),
                   lambda c:c['evaluation'].update(accuracy_minimum=0.1),
                   lambda c:c['backend'].update(revision='latest'),
                   lambda c:c['backend'].update(source_patch_sha256='0'*64),
                   lambda c:c['limits'].update(full_wall_seconds=999999),
                   lambda c:c.update(schema_version=True)]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                config=copy.deepcopy(self.config);mutate(config)
                with self.assertRaises(ContractError):validate_config(config)

    def test_measured_configuration_needs_runtime_and_code_identity(self):
        self.config['evidence_class']='MEASURED'
        with self.assertRaises(ContractError):validate_config(self.config)
        self.config['hardware']['platform']='Linux-x86_64'
        with self.assertRaises(ContractError):validate_config(self.config)
        self.config['implementation_sha256']='c'*64
        self.config['clock']['boot_id']='00000000-0000-0000-0000-000000000001'
        validate_config(self.config)


if __name__=='__main__':unittest.main()
