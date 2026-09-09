"""Local inert archive fixtures exercise candidate identity and exclusion gates."""
import copy
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from lean_model_lab.contracts import canonical_bytes, digest, make_workload
from lean_model_lab.llama_adapter import MODEL_FILENAME
from lean_model_lab.session import Session
from lean_model_lab.workbench import build_catalog, render_workbench
from test_evidence import CONFIG, make_attempt

PROJECT = Path(__file__).resolve().parents[1]


def load_tool(name):
    spec = importlib.util.spec_from_file_location(name, PROJECT / 'tools' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


bundler = load_tool('build_recipe_review_bundle')
exporter = load_tool('export_study')


class RecipeBundleTests(unittest.TestCase):
    def setUp(self):
        scratch = PROJECT / '.cache' / 'tmp'
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.root_patch = patch.object(bundler, 'ROOT', self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        for name in bundler.SOURCE_FILES:
            (self.root / name).write_text('{}\n' if name.endswith('.json') else 'local fixture\n')
        for name in bundler.SOURCE_DIRS:
            (self.root / name).mkdir()
        runtime = self.root / 'src' / 'lean_model_lab'
        runtime.mkdir()
        self.current = b'raise RuntimeError("archive must never execute")\n'
        self.old = b'raise RuntimeError("older producer must never execute")\n'
        (runtime / '__init__.py').write_bytes(self.current)
        self.final = self.root / 'final.pyz'
        self.producer = self.root / 'frozen.pyz'
        self.write_archive(self.final, self.current)
        self.write_archive(self.producer, self.old)
        self.export = self.make_export('one', self.old)
        self.studies = [('first-study', self.export)]
        self.catalog = self.root / 'catalog.json'
        self.html = self.root / 'catalog.html'
        self.write_workbench()

    def write_archive(self, path, runtime, extra=None):
        files = {'lean_model_lab/__init__.py': runtime,
                 '__main__.py': b'from lean_model_lab.cli import main\nraise SystemExit(main())\n', 'LICENSE': b'fixture\n'}
        files.update(extra or {})
        files['BUILD-MANIFEST.json'] = canonical_bytes({'version': '0.4.0.fixture',
            'artifact_class': 'LOCAL_DEVELOPMENT_CANDIDATE', 'runtime': 'inert fixture',
            'files': {name: bundler.sha(data) for name, data in files.items()}})
        with zipfile.ZipFile(path, 'w') as archive:
            for name, data in files.items():
                archive.writestr(name, data)

    def make_export(self, name, runtime):
        config = copy.deepcopy(CONFIG)
        config['implementation_sha256'] = digest({'__init__.py': bundler.sha(runtime)})
        source = self.root / ('original-' + name)
        Session.create(source, config, make_workload(), [])
        with Session.open(source) as session:
            attempt = make_attempt()
            reservation = session.reserve('baseline', 1, 0, attempt['started_ns'])
            attempt['attempt_id'] = reservation['attempt_id']
            attempt['config_sha256'] = digest(config)
            (reservation['raw_dir'] / 'server.log').write_text(
                "srv load_model: loading model '/private-fixture/" + MODEL_FILENAME + "'\n")
            session.publish(attempt)
        output = self.root / ('export-' + name)
        exporter.export(source, output, '/private-fixture/' + MODEL_FILENAME)
        return output

    def write_workbench(self):
        catalog = build_catalog([path / 'study' for _, path in self.studies])
        for index, study in enumerate(catalog['studies']):
            study['label'] = 'Portable label ' + str(index)
        self.catalog.write_bytes(canonical_bytes(catalog) + b'\n')
        self.html.write_text(render_workbench(catalog))

    def build(self, **overrides):
        arguments = {'output': self.root / 'candidate', 'archive': self.final,
                     'producers': [self.producer], 'studies': self.studies,
                     'workbench_json': self.catalog, 'workbench_html': self.html}
        arguments.update(overrides)
        return bundler.build(**arguments)

    def test_multiple_producers_source_identity_inventory_and_determinism(self):
        newer = self.make_export('two', self.current)
        self.studies.append(('second-study', newer))
        self.write_workbench()
        result = self.build()
        repeated = self.build(output=self.root / 'candidate-repeat')
        self.assertEqual(result, repeated)
        self.assertTrue(result['source_runtime_matches_final_cli'])
        self.assertTrue(result['workbench_matches_included_exports'])
        first = result['studies']['first-study']
        self.assertTrue(first['producer_artifacts'][0].startswith('producer-'))
        self.assertEqual(result['studies']['second-study']['producer_artifacts'], ['lean-model-lab.pyz'])
        self.assertEqual(first['evidence_class'], 'TEST_FIXTURE')
        provenance = json.loads((self.export / 'study/EXPORT-PROVENANCE.json').read_bytes())
        self.assertEqual(len(provenance['changed_raw_files']), 1)
        for name, metadata in result['artifacts'].items():
            self.assertEqual(bundler.sha((self.root / 'candidate' / name).read_bytes()), metadata['sha256'])
        with zipfile.ZipFile(self.root / 'candidate/lean-model-lab-source.zip') as archive:
            self.assertIn('lean-model-lab-source/WORKSPACE.json', archive.namelist())
        with zipfile.ZipFile(self.root / 'candidate/lean-model-lab-evidence.zip') as archive:
            self.assertIn('evidence/first-study/study/.lock', archive.namelist())
            inventory = json.loads(archive.read('FILE-MANIFEST.json'))
            self.assertTrue(inventory['directories'])
            for name, metadata in inventory['files'].items():
                self.assertEqual(bundler.sha(archive.read(name)), metadata['sha256'])
        with self.assertRaisesRegex(ValueError, 'already exists'):
            self.build()

    def test_missing_actual_producer_is_rejected(self):
        self.write_archive(self.producer, b'pass\n')
        with self.assertRaisesRegex(ValueError, 'no included producer'):
            self.build()
        self.assertFalse((self.root / 'candidate').exists())

    def test_source_cli_drift_is_rejected(self):
        (self.root / 'src/lean_model_lab/__init__.py').write_text('pass\n')
        with self.assertRaisesRegex(ValueError, 'source runtime differs'):
            self.build()

    def test_rehashed_archive_traversal_and_blob_are_rejected(self):
        for name in ('../escape.py', 'lean_model_lab/../escape.py', 'model.gguf', 'browser/chrome'):
            with self.subTest(name=name):
                self.write_archive(self.producer, self.old, {name: b'blob'})
                with self.assertRaisesRegex(ValueError, 'unsafe|unreviewed'):
                    self.build()

    def test_archive_tampering_and_duplicate_entries_are_rejected(self):
        with zipfile.ZipFile(self.producer) as archive:
            files = {name: archive.read(name) for name in archive.namelist()}
        files['lean_model_lab/__init__.py'] = b'pass\n'
        with zipfile.ZipFile(self.producer, 'w') as archive:
            for name, data in files.items():
                archive.writestr(name, data)
        with self.assertRaisesRegex(ValueError, 'manifest'):
            self.build()
        self.write_archive(self.producer, self.old, {'LICENSE': b'fixture', 'license': b'collision'})
        with self.assertRaisesRegex(ValueError, 'duplicate archive'):
            self.build()

    def test_report_tampering_even_with_rebound_ready_hash_is_rejected(self):
        report_path = self.export / 'report.json'
        report = json.loads(report_path.read_bytes())
        report['finding'] = 'unsubstantiated change'
        report_path.write_bytes(canonical_bytes(report))
        provenance_path = self.export / 'study/EXPORT-PROVENANCE.json'
        provenance = json.loads(provenance_path.read_bytes())
        provenance['report_unchanged_sha256'] = digest(report)
        provenance_path.write_bytes(canonical_bytes(provenance))
        ready_path = self.export / 'EXPORT-READY.json'
        ready = json.loads(ready_path.read_bytes())
        ready.update(report_sha256=bundler.sha(report_path.read_bytes()),
                     provenance_sha256=bundler.sha(provenance_path.read_bytes()))
        ready_path.write_bytes(canonical_bytes(ready))
        with self.assertRaisesRegex(ValueError, 'Session inventory'):
            self.build()

    def test_original_provenance_tampering_is_rejected(self):
        (self.export / 'original-provenance/config.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'original provenance bytes'):
            self.build()

    def test_ready_and_redacted_raw_tampering_are_rejected(self):
        ready_path = self.export / 'EXPORT-READY.json'
        original_ready = ready_path.read_bytes()
        ready = json.loads(original_ready)
        ready['provenance_sha256'] = '0' * 64
        ready_path.write_bytes(canonical_bytes(ready))
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            self.build()
        ready_path.write_bytes(original_ready)
        next((self.export / 'study/raw').rglob('server.log')).write_text('altered raw log\n')
        with self.assertRaises(ValueError):
            self.build()

    def test_stale_workbench_and_html_are_rejected(self):
        catalog = json.loads(self.catalog.read_bytes())
        catalog['studies'][0]['quality']['correct'] += 1
        self.catalog.write_bytes(canonical_bytes(catalog))
        self.html.write_text(render_workbench(catalog))
        with self.assertRaisesRegex(ValueError, 'workbench differs'):
            self.build()
        self.write_workbench()
        self.html.write_text(self.html.read_text() + '<p>extra</p>')
        with self.assertRaisesRegex(ValueError, 'workbench differs'):
            self.build()

    def test_paths_names_symlinks_and_overlaps_are_rejected(self):
        for names in ([('../escape', self.export)], [('A', self.export), ('a', self.root / 'missing')]):
            with self.assertRaisesRegex(ValueError, 'safe unique|collision'):
                self.build(studies=names)
        for output in (self.export / 'nested', self.root / 'src' / 'out', self.root / '..' / 'escape'):
            with self.assertRaisesRegex(ValueError, 'overlap|traversal'):
                self.build(output=output)
        link = self.root / 'link'
        link.symlink_to(self.export, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            self.build(studies=[('linked', link)])
        with self.assertRaisesRegex(ValueError, 'overlap'):
            self.build(producers=[self.final])

    def test_source_blob_exclusion_and_evidence_blob_refusal(self):
        for name in ('model.gguf', 'llama-server', 'chrome', 'compiled.so'):
            (self.root / 'src' / name).write_bytes(b'\x00blob')
        self.build()
        with zipfile.ZipFile(self.root / 'candidate/lean-model-lab-source.zip') as archive:
            self.assertFalse(any(name.endswith(('.gguf', '.so', '/chrome', '/llama-server')) for name in archive.namelist()))
        (self.export / 'study/raw/model.gguf').write_bytes(b'blob')
        with self.assertRaisesRegex(ValueError, 'unreviewed evidence'):
            self.build(output=self.root / 'refused')

    def test_private_path_and_binary_disguised_as_text_are_rejected(self):
        for data in (('/' + 'home/private-account/model').encode(), b'\x00binary'):
            with self.subTest(data=data):
                (self.root / 'docs/review.md').write_bytes(data)
                with self.assertRaisesRegex(ValueError, 'private path|binary'):
                    self.build()

    def test_workbench_has_separate_bounded_text_allowance(self):
        path = self.root / 'bounded.json'
        with patch.object(bundler, 'MAX_FILE_BYTES', 8), patch.object(bundler, 'MAX_WORKBENCH_BYTES', 16):
            path.write_bytes(b'a' * 12)
            with self.assertRaisesRegex(ValueError, 'oversized'):
                bundler.read_text(path, 'workbench.json')
            self.assertEqual(bundler.read_text(path, 'workbench.json', workbench=True), b'a' * 12)
            path.write_bytes(b'a' * 17)
            with self.assertRaisesRegex(ValueError, 'oversized'):
                bundler.read_text(path, 'workbench.json', workbench=True)
            with self.assertRaisesRegex(ValueError, 'oversized'):
                bundler.check_text('workbench.json', b'a' * 17, workbench=True)
            path.write_bytes(b'\x00' + b'a' * 11)
            with self.assertRaisesRegex(ValueError, 'binary'):
                bundler.read_text(path, 'workbench.json', workbench=True)


if __name__ == '__main__':
    unittest.main()
