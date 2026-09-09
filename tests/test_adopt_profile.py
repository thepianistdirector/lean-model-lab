"""Inert adoption fixtures: tiny bytes, no native process or real model hashing."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from contextlib import ExitStack
from unittest.mock import patch

from lean_model_lab.contracts import ContractError, digest, read_json
from lean_model_lab.llama_adapter import BACKEND_COMMIT, BACKEND_PATCH_FILENAME
from lean_model_lab.resources import heavy_job
from lean_model_lab.setup import validate_receipt

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('adopt_prepared_profile_test_tool', ROOT / 'tools/adopt_prepared_profile.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
PROFILE = 'qwen2.5-0.5b-instruct-fp16-v1'


class AdoptProfileTests(unittest.TestCase):
    def setUp(self):
        cache = ROOT / '.cache'
        cache.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix='adopt-fixture-', dir=cache)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / 'WORKSPACE.json').write_text('{"project":"lean-model-lab","schema_version":1}')
        (self.root / '.cache').mkdir()
        (self.root / 'patches').mkdir()
        self.patch_bytes = b'inert reviewed patch fixture\n'
        (self.root / 'patches' / BACKEND_PATCH_FILENAME).write_bytes(self.patch_bytes)
        self.patch_sha = hashlib.sha256(self.patch_bytes).hexdigest()
        self.model = self.root / 'fixture-model.gguf'
        self.model.write_bytes(b'inert model bytes; never executed\n')
        self.model_sha = hashlib.sha256(self.model.read_bytes()).hexdigest()
        self.server = self.root / 'fixture-server'
        self.server.write_bytes(b'inert non-program server bytes; never executed\n')
        self.server.chmod(0o700)
        self.profile = {'profile_id': PROFILE, 'repository': 'inert/local-fixture', 'revision': 'fixture',
                        'entrypoint': self.model.name,
                        'files': [{'filename': self.model.name, 'bytes': self.model.stat().st_size,
                                   'sha256': self.model_sha}]}
        boot = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        now = time.monotonic_ns()
        self.allocation = {
            'schema_version': 2, 'allocation_id': 'adopt-inert-current', 'approved': True,
            'approval_reference': 'Inert fixture only; no real model/build execution',
            'observed_utc': '2026-09-08T00:00:00Z', 'boot_id': boot,
            'started_ns': now - 10**9, 'deadline_ns': now - 10**9 + 600 * 10**9,
            'limits': {'full_wall_seconds': 600, 'disk_bytes': 10**8,
                       'memory_bytes': 10**9, 'compute_threads': 1, 'max_heavy_jobs': 1},
            'scope': 'Project-local inert test fixture; no downloaded model/backend is accessed'}
        self.source = {'schema_version': 1, 'boot_id': boot,
                       'artifacts': {'backend_revision': BACKEND_COMMIT,
                                     'backend_patch_sha256': self.patch_sha,
                                     'server_sha256': hashlib.sha256(self.server.read_bytes()).hexdigest(),
                                     'model_sha256': self.model_sha},
                       'records': [
                           {'phase': name, 'status': status,
                            'started_ns': now - 10**10 + index * 10**6,
                            'finished_ns': now - 10**10 + index * 10**6 + 500000,
                            'bytes_acquired': 100 + index, 'details': 'inert historical cost fixture'}
                           for index, (name, status) in enumerate([
                               ('source-acquisition', 'COMPLETED'), ('model-acquisition', 'COMPLETED'),
                               ('build', 'FAILED'), ('build', 'COMPLETED')])]}
        self.args = argparse.Namespace(allocation=self.root / 'current.json', source_setup=self.root / 'original.json',
                                       server=self.server, model=self.model, profile=PROFILE,
                                       output=self.root / 'adopted')
        self.write_inputs()
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.workspace = self.stack.enter_context(patch.object(tool, 'require_workspace_root', return_value=self.root))
        def get_profile(name):
            if name != PROFILE:
                raise ContractError('unknown inert fixture profile')
            return copy.deepcopy(self.profile)
        self.stack.enter_context(patch.object(tool, 'get_model_profile', side_effect=get_profile))
        self.stack.enter_context(patch('lean_model_lab.profiles.get_model_profile', side_effect=get_profile))
        self.stack.enter_context(patch.object(tool, 'BACKEND_PATCH_SHA256', self.patch_sha))
        self.stack.enter_context(patch('lean_model_lab.setup.BACKEND_PATCH_SHA256', self.patch_sha))
        self.stack.enter_context(patch('lean_model_lab.setup.MODEL_SHA256', self.model_sha))
        # A direct subprocess would make the implementation fail even on tiny inputs.
        self.popen = self.stack.enter_context(patch('subprocess.Popen', side_effect=AssertionError('adoption must not launch a process')))

    def write_inputs(self):
        self.args.allocation.write_text(json.dumps(self.allocation))
        self.args.source_setup.write_text(json.dumps(self.source, indent=3) + '\n\n')

    def test_legacy_adoption_retains_exact_ancestor_and_disjoint_current_costs(self):
        original = self.args.source_setup.read_bytes()
        before_model = self.model.read_bytes()
        self.assertEqual(tool.adopt(self.args), 0)
        receipt = read_json(self.args.output / 'setup.json')
        validate_receipt(receipt)
        self.assertEqual(receipt['allocation'], self.allocation)
        self.assertEqual([r['phase'] for r in receipt['records']], ['source-acquisition', 'model-acquisition', 'build'])
        self.assertTrue(all(r['bytes_acquired'] == 0 and r['status'] == 'COMPLETED' for r in receipt['records']))
        self.assertTrue(all(r['started_ns'] >= self.allocation['started_ns'] for r in receipt['records']))
        ancestor = json.loads(receipt['records'][0]['details'])['ancestor']
        self.assertEqual(ancestor['source_receipt_raw_utf8'].encode(), original)
        self.assertEqual((self.args.output / 'source-setup.json').read_bytes(), original)
        self.assertEqual(ancestor['source_receipt_sha256'], hashlib.sha256(original).hexdigest())
        self.assertEqual(ancestor['historical_costs']['recorded_bytes_acquired'], 406)
        self.assertEqual(ancestor['historical_costs']['attributed_phase_ns'], 2000000)
        self.assertEqual(ancestor['historical_costs']['terminal_counts']['FAILED'], 1)
        self.assertIsNone(ancestor['historical_costs']['allocation_identity'])
        self.assertEqual(self.model.read_bytes(), before_model)
        self.assertEqual(self.args.source_setup.read_bytes(), original)
        manifest = read_json(self.args.output / 'adoption.json')
        self.assertEqual(manifest['setup_receipt_sha256'], digest(receipt))
        self.assertEqual(manifest['newly_acquired_artifact_bytes'], 0)
        self.popen.assert_not_called()
        self.workspace.assert_called_once()

    def test_v2_source_allocation_is_preserved_without_merging_intervals(self):
        old = copy.deepcopy(self.allocation)
        old['allocation_id'] = 'adopt-inert-prior'
        old['started_ns'] -= 1000 * 10**9
        old['deadline_ns'] = old['started_ns'] + old['limits']['full_wall_seconds'] * 10**9
        for index, record in enumerate(self.source['records']):
            record['started_ns'] = old['started_ns'] + (index + 1) * 10**9
            record['finished_ns'] = record['started_ns'] + 500000
        self.source.update(schema_version=2, allocation=old,
                           resource_observations={'maximum_observed_aggregate_rss_bytes': 1,
                                                  'scope': 'inert historical fixture'})
        self.source['artifacts'].pop('model_sha256')
        self.source['artifacts'].update(model_profile_id=PROFILE, model_profile_sha256=digest(self.profile))
        self.write_inputs()
        self.assertEqual(tool.adopt(self.args), 0)
        ancestor = read_json(self.args.output / 'ancestor-costs.json')
        self.assertEqual(ancestor['historical_costs']['allocation_identity'], old)
        self.assertEqual(read_json(self.args.output / 'setup.json')['allocation'], self.allocation)

    def assert_failed(self, expected):
        self.assertEqual(tool.adopt(self.args), 2)
        failure = read_json(self.args.output / 'setup-failure.json')
        self.assertIn(expected, failure['error'])
        self.assertFalse((self.args.output / 'setup.json').exists())
        self.assertTrue((self.args.output / 'setup-events.jsonl').exists())
        return failure

    def test_wrong_source_backend_identity_is_retained_as_failure(self):
        self.source['artifacts']['backend_revision'] = 'unreviewed'
        self.write_inputs()
        self.assert_failed('approved model/backend')
        self.assertEqual((self.args.output / 'source-setup.json').read_bytes(), self.args.source_setup.read_bytes())

    def test_unknown_profile_refused(self):
        self.args.profile = 'unreviewed-profile'
        self.assert_failed('unknown inert fixture profile')

    def test_legacy_receipt_cannot_admit_a_different_profile(self):
        other = copy.deepcopy(self.profile)
        other['profile_id'] = 'qwen2.5-14b-instruct-fp16-v1'
        self.args.profile = other['profile_id']
        with patch.object(tool, 'get_model_profile', return_value=other):
            self.assert_failed('only its exact reviewed 0.5B profile')

    def test_malformed_source_is_retained_without_a_valid_setup(self):
        raw = b'{"schema_version":1,"schema_version":2}\n'
        self.args.source_setup.write_bytes(raw)
        self.assert_failed('duplicate JSON key')
        self.assertEqual((self.args.output / 'source-setup.json').read_bytes(), raw)

    def test_model_corruption_preserves_failure_cost(self):
        self.model.write_bytes(b'X' * self.model.stat().st_size)
        failure = self.assert_failed('SHA-256 differs')
        self.assertEqual(failure['records'][-1]['phase'], 'model-acquisition')
        self.assertEqual(failure['records'][-1]['status'], 'FAILED')

    def test_server_corruption_preserves_completed_model_verification(self):
        self.server.write_bytes(b'X' * self.server.stat().st_size)
        failure = self.assert_failed('server SHA-256 differs')
        self.assertEqual([r['status'] for r in failure['records']], ['COMPLETED', 'COMPLETED', 'FAILED'])

    def test_expired_or_unapproved_allocation_cannot_create_output(self):
        for expired in (True, False):
            with self.subTest(expired=expired):
                invalid = copy.deepcopy(self.allocation)
                if expired:
                    invalid['started_ns'] -= 1000 * 10**9
                    invalid['deadline_ns'] -= 1000 * 10**9
                else:
                    invalid['approved'] = False
                self.args.allocation.write_text(json.dumps(invalid))
                with self.assertRaises(ContractError):
                    tool.adopt(self.args)
                self.assertFalse(self.args.output.exists())

    def test_source_intervals_cannot_be_relabelled_as_current_setup(self):
        self.source['records'][-1]['finished_ns'] = time.monotonic_ns()
        self.write_inputs()
        self.assert_failed('must precede the current allocation')

    def test_existing_output_is_not_modified(self):
        self.args.output.mkdir()
        marker = self.args.output / 'keep'
        marker.write_bytes(b'original')
        with self.assertRaisesRegex(ContractError, 'overwrite'):
            tool.adopt(self.args)
        self.assertEqual(list(self.args.output.iterdir()), [marker])
        self.assertEqual(marker.read_bytes(), b'original')

    def test_symlink_input_parent_and_output_escape_are_refused(self):
        parent = self.root / 'linked'
        parent.symlink_to(self.root, target_is_directory=True)
        self.args.model = parent / self.model.name
        self.assert_failed('symlinks')
        self.args.output = parent / 'not-created'
        with self.assertRaisesRegex(ContractError, 'symlinks'):
            tool.adopt(self.args)
        self.assertFalse((self.root / 'not-created').exists())
        with self.assertRaisesRegex(ContractError, 'same workspace'):
            tool.workspace_path(self.root.parent / 'outside-fixture', self.root, existing=False)

    def test_active_heavy_lease_prevents_verification_or_output(self):
        with heavy_job(self.root):
            with self.assertRaisesRegex(RuntimeError, 'heavy-job lease'):
                tool.adopt(self.args)
        self.assertFalse(self.args.output.exists())

    def test_chunk_cancellation_is_retained_and_releases_lease(self):
        original = tool.verify_model_files
        def interrupted(entrypoint, profile, *, check):
            check()
            raise KeyboardInterrupt('fixture cancellation between hash chunks')
        with patch.object(tool, 'verify_model_files', side_effect=interrupted):
            failure = self.assert_failed('fixture cancellation')
        self.assertEqual(failure['status'], 'INTERRUPTED')
        self.assertEqual(failure['records'][-1]['status'], 'INTERRUPTED')
        with heavy_job(self.root):
            pass
        self.assertIs(tool.verify_model_files, original)

    def test_input_mutation_after_hash_is_refused(self):
        original = tool.verify_model_files
        def changed(entrypoint, profile, *, check):
            result = original(entrypoint, profile, check=check)
            entrypoint.write_bytes(b'X' * entrypoint.stat().st_size)
            return result
        with patch.object(tool, 'verify_model_files', side_effect=changed):
            self.assert_failed('input changed during verification')

    def test_budget_deadline_memory_disk_checks(self):
        allocation = copy.deepcopy(self.allocation)
        budget = tool.Budget(self.root, allocation)
        allocation['deadline_ns'] = 1
        with self.assertRaises(TimeoutError):
            budget()
        allocation['deadline_ns'] = self.allocation['deadline_ns']
        with patch.object(tool, '_rss', return_value=allocation['limits']['memory_bytes'] + 1):
            with self.assertRaises(MemoryError):
                budget()
        allocation['limits']['disk_bytes'] = 1
        with self.assertRaisesRegex(OSError, 'workspace disk'):
            budget(force_disk=True)


if __name__ == '__main__':
    unittest.main()
