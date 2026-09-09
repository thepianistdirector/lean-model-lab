"""Split distribution integrity and reviewed analytical-asset boundaries."""
import json
import unittest
import zipfile
from unittest.mock import patch

import test_recipe_bundle as fixture_module

bundler = fixture_module.load_tool('build_v1_release_bundle')


class V1BundleTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixture_module.RecipeBundleTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root
        for module in (bundler, bundler.verified):
            patcher = patch.object(module, 'ROOT', self.root)
            patcher.start()
            self.addCleanup(patcher.stop)

    def build(self, **overrides):
        arguments = {'output': self.root / 'v1', 'archive': self.fixture.final,
                     'producers': [self.fixture.producer], 'studies': self.fixture.studies}
        arguments.update(overrides)
        return bundler.build(**arguments)

    def test_split_studies_exact_source_and_hash_readback(self):
        self.fixture.studies.append(('second', self.fixture.make_export('two', self.fixture.current)))
        csv = self.root / 'docs/results.csv'
        csv.write_text('arm,correct\nbaseline,0\n')
        result = self.build()
        repeated = self.build(output=self.root / 'repeat')
        self.assertEqual(result, repeated)
        self.assertTrue(result['source_runtime_matches_final_cli'])
        self.assertEqual(len(result['studies']), 2)
        self.assertIn('first-study-evidence.zip', result['artifacts'])
        self.assertIn('second-evidence.zip', result['artifacts'])
        self.assertLess((self.root / 'v1/index.html').stat().st_size, 10000)
        self.assertNotIn('lean-model-lab-evidence.zip', result['artifacts'])
        for name, metadata in result['artifacts'].items():
            self.assertEqual(bundler.sha((self.root / 'v1' / name).read_bytes()), metadata['sha256'])
        with zipfile.ZipFile(self.root / 'v1/lean-model-lab-source.zip') as archive:
            self.assertEqual(archive.read('lean-model-lab-source/docs/results.csv'), csv.read_bytes())
        with zipfile.ZipFile(self.root / 'v1/second-evidence.zip') as archive:
            self.assertTrue(all(name.startswith('evidence/second/') or name == 'FILE-MANIFEST.json'
                                for name in archive.namelist()))
        with self.assertRaisesRegex(ValueError, 'already exists'):
            self.build()

    def test_missing_producer_never_creates_ready_manifest(self):
        with self.assertRaisesRegex(ValueError, 'no included producer'):
            self.build(producers=[])
        self.assertFalse((self.root / 'v1/CANDIDATE-MANIFEST.json').exists())

    def test_study_cannot_overwrite_index_or_ready_manifest(self):
        for name in ('index', 'INDEX', 'CANDIDATE-MANIFEST', 'candidate-manifest'):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'reserved'):
                self.build(studies=[(name, self.fixture.export)])
        self.assertFalse((self.root / 'v1').exists())

    def test_investigation_zip_contains_source_exact_producers_and_flattened_evidence(self):
        folder = self.root / 'docs/research/quality'
        folder.mkdir(parents=True)
        (folder / 'manuscript.md').write_text('Explicit inert fixture; no model claim.\n')
        (folder / 'audit.json').write_text('{"status":"TEST_FIXTURE"}\n')
        specification = self.root / 'quality-package.json'
        document = {'title': 'Quality benchmark fixture', 'classification': 'BENCHMARK',
                    'source_directory': 'docs/research/quality', 'studies': ['first-study'],
                    'entrypoint': 'docs/research/quality/manuscript.md',
                    'supplementary_files': {'audits/first.json': 'docs/research/quality/audit.json'}}
        specification.write_text(json.dumps(document))
        result = self.build(research_packages=[('quality', specification)])
        self.assertIn('quality-research.zip', result['artifacts'])
        with zipfile.ZipFile(self.root / 'v1/quality-research.zip') as archive:
            names = archive.namelist()
            self.assertIn('lean-model-lab-source/src/lean_model_lab/__init__.py', names)
            self.assertIn('lean-model-lab-source/docs/research/quality/manuscript.md', names)
            self.assertIn('evidence/first-study/study/config.json', names)
            self.assertIn('manifests/first-study-evidence.json', names)
            self.assertIn('first-study.html', names)
            self.assertIn('lean-model-lab.pyz', names)
            self.assertEqual(archive.read('audits/first.json'), (folder / 'audit.json').read_bytes())
            self.assertTrue(any(name.startswith('producer-') and name.endswith('.pyz') for name in names))
            record = json.loads(archive.read('RESEARCH-PACKAGE.json'))
            self.assertEqual(record['study_evidence']['first-study']['evidence_class'], 'TEST_FIXTURE')
            self.assertIn(b'evidence/first-study/EXPORT-READY.json', archive.read('index.html'))
            self.assertIn(b'lean-model-lab-source/docs/research/quality/manuscript.md', archive.read('index.html'))
            inventory = json.loads(archive.read('FILE-MANIFEST.json'))
            for name, metadata in inventory['files'].items():
                self.assertEqual(bundler.sha(archive.read(name)), metadata['sha256'])
        document['supplementary_files'] = {'index.html': 'docs/research/quality/audit.json'}
        specification.write_text(json.dumps(document))
        with self.assertRaisesRegex(ValueError, 'collides with package'):
            self.build(output=self.root / 'collision-group', research_packages=[('quality', specification)])
        document['studies'] = ['missing']
        specification.write_text(json.dumps(document))
        with self.assertRaisesRegex(ValueError, 'missing or duplicate studies'):
            self.build(output=self.root / 'invalid-group', research_packages=[('quality', specification)])

    def test_figure_must_be_reviewed_and_unchanged(self):
        folder = self.root / 'docs/research/example/figures'
        folder.mkdir(parents=True)
        figure = folder / 'chart.pdf'
        figure.write_bytes(b'%PDF-1.4\n%%EOF\n')
        relative = figure.relative_to(self.root).as_posix()
        with self.assertRaisesRegex(ValueError, 'lacks reviewed digest'):
            self.build()
        manifest = self.root / 'reviewed-assets.json'
        manifest.write_text(json.dumps({relative: bundler.sha(figure.read_bytes())}))
        self.build(asset_manifest=manifest)
        figure.write_bytes(b'%PDF-1.4\nchanged\n%%EOF\n')
        with self.assertRaisesRegex(ValueError, 'digest differs'):
            self.build(output=self.root / 'changed', asset_manifest=manifest)

    def test_active_figures_and_unreviewed_location_are_refused(self):
        for name, data in [('docs/research/a/figures/a.pdf', b'%PDF-1.4\n/JavaScript 1\n%%EOF'),
                           ('docs/research/a/figures/a.png', b'bad PNG'),
                           ('docs/blob.pdf', b'%PDF-1.4\n%%EOF')]:
            with self.subTest(name=name), self.assertRaises(ValueError):
                bundler.validate_figure(name, data)
        for svg in (b'<svg><script/></svg>', b'<svg><use href="https://example.org/x"/></svg>',
                    b'<svg onload="x()"/>', b'<html/>'):
            with self.subTest(svg=svg), self.assertRaises(ValueError):
                bundler.validate_svg(svg)
        bundler.validate_svg(b'<svg><defs><path id="a"/></defs><use href="#a"/></svg>')

    def test_private_csv_and_source_runtime_drift_are_refused(self):
        path = self.root / 'docs/results.csv'
        path.write_text('/' + 'home/private-account/result\n')
        with self.assertRaisesRegex(ValueError, 'private path'):
            self.build()
        path.unlink()
        (self.root / 'src/lean_model_lab/__init__.py').write_text('pass\n')
        with self.assertRaisesRegex(ValueError, 'source runtime differs'):
            self.build()

    def test_research_metadata_cannot_be_silently_omitted(self):
        folder = self.root / 'docs/research/example/dependency'
        folder.mkdir(parents=True)
        metadata = folder / 'METADATA'
        metadata.write_text('Name: retained-dependency\n')
        with self.assertRaisesRegex(ValueError, 'unsupported research file would be omitted'):
            self.build()
        metadata.rename(folder / 'METADATA.txt')
        self.build()
        with zipfile.ZipFile(self.root / 'v1/lean-model-lab-source.zip') as archive:
            self.assertEqual(archive.read('lean-model-lab-source/docs/research/example/dependency/METADATA.txt'),
                             b'Name: retained-dependency\n')


if __name__ == '__main__':
    unittest.main()
