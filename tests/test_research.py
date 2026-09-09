"""Model-free research contract controls; TEST_FIXTURE recipes never execute."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from lean_model_lab import research
from lean_model_lab.contracts import ContractError, canonical_bytes, digest, read_json
from lean_model_lab.research_proposals import PROPOSALS
from test_evidence_v2 import fixture


ROOT = Path(__file__).resolve().parents[1]
TEMP_ROOT = ROOT / '.cache' / 'tmp'


class ResearchTests(unittest.TestCase):
    def setUp(self):
        TEMP_ROOT.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix='research-test-', dir=TEMP_ROOT)
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.control = research.template('prefix-cache-control')

    def freeze(self, name='frozen'):
        root = self.root / name
        research.freeze_proposal(self.control, root)
        return root

    def rewrite(self, path, mutate):
        value = read_json(path)
        mutate(value)
        path.write_text(json.dumps(value), encoding='utf-8')

    def cli(self, *args, expected=0):
        env = dict(os.environ, PYTHONPATH=str(ROOT/'src')+os.pathsep+str(ROOT/'tests'),
                   TMPDIR=str(TEMP_ROOT), PYTHONDONTWRITEBYTECODE='1')
        completed = subprocess.run([sys.executable, '-m', 'lean_model_lab', 'research',
                                    *map(str, args)], cwd=ROOT, env=env,
                                   capture_output=True, text=True, timeout=30)
        self.assertEqual(completed.returncode, expected, completed.stderr)
        if expected:
            self.assertEqual(completed.stdout, '')
            return completed.stderr
        self.assertEqual(completed.stderr, '')
        return json.loads(completed.stdout)

    def test_catalog_inventory_and_document_projections_are_exact(self):
        catalog = research.catalog()
        self.assertEqual(len(catalog['techniques']), 40)
        self.assertEqual(len(catalog['sources']), 72)
        self.assertEqual(catalog['coverage']['inference_families'], 20)
        self.assertEqual(catalog['coverage']['training_families'], 20)
        self.assertFalse(catalog['coverage']['exhaustive'])
        self.assertEqual(catalog, read_json(ROOT/'docs/research/technique-catalog.json'))
        self.assertEqual(PROPOSALS, read_json(ROOT/'docs/research/proposals.json'))
        catalog['sources'][0]['title'] = 'Changed caller copy'
        self.assertNotEqual(catalog, research.catalog())

    def test_all_templates_validate_but_only_registered_control_has_compiler(self):
        rows = research.template_list()
        self.assertEqual(len(rows), 9)
        for row in rows:
            with self.subTest(template=row['id']):
                proposal = research.template(row['id'])
                self.assertEqual(research.validate_proposal(proposal), proposal)
                result = research.readiness(proposal)
                self.assertEqual(result['supported_recipe_compiler'], row['id']=='prefix-cache-control')
                self.assertIs(result['execution_authorized'], False)
                self.assertIs(result['execution_performed'], False)
                self.assertNotEqual(result['novelty_status'], 'CONFIRMED')
        with self.assertRaisesRegex(ContractError, 'unknown research template'):
            research.template('invented-template')

    def test_catalog_support_and_composition_do_not_grant_paper_capabilities(self):
        available = research.catalog_view(available_only=True)
        self.assertEqual([r['id'] for r in available['techniques']], ['prefix-cache'])
        self.assertEqual(research.catalog_view('training', True)['techniques'], [])
        for domain in ('inference', 'training'):
            self.assertEqual(len(research.catalog_view(domain)['techniques']), 20)
        other = next(r['id'] for r in research.catalog()['techniques'] if r['id']!='prefix-cache')
        composed = research.composition(['prefix-cache', other])
        self.assertFalse(composed['composition_verified'])
        self.assertFalse(composed['supported_recipe_compiler'])
        self.assertFalse(composed['execution_authorized'])
        with self.assertRaises(ContractError):
            research.catalog_view(technique_id='invented-technique')

    def test_proposals_reject_bad_prior_art_capabilities_resources_and_novelty(self):
        mutations = {
            'malformed source id': lambda p: p['prior_art'][0].update(source_id=['bad']),
            'unknown source id': lambda p: p['prior_art'][0].update(source_id='src-absent'),
            'duplicate prior art': lambda p: p['prior_art'].append(copy.deepcopy(p['prior_art'][0])),
            'unknown capability': lambda p: p['required_capabilities'].append('invented-runtime'),
            'unknown technique': lambda p: p['technique_ids'].append('invented-technique'),
            'manufactured novelty': lambda p: p['novelty'].update(status='CONFIRMED'),
            'hidden training requirement': lambda p: p.update(domain='training'),
            'unprotected confirmation': lambda p: p.update(stage='protected_confirmation'),
        }
        for field in ('cpu_threads', 'memory_bytes', 'disk_bytes', 'wall_seconds'):
            mutations['boolean '+field] = lambda p, field=field: p['resources'].update({field: True})
        for name, mutate in mutations.items():
            with self.subTest(mutation=name):
                proposal = copy.deepcopy(self.control)
                mutate(proposal)
                with self.assertRaises(ContractError):
                    research.validate_proposal(proposal)

    def test_catalog_rejects_bad_urls_duplicate_sources_and_unknown_caution_refs(self):
        mutations = {
            'HTTP': lambda c: c['sources'][0].update(url='http://example.org/paper'),
            'credentials': lambda c: c['sources'][0].update(url='https://user:secret@example.org/paper'),
            'no host': lambda c: c['sources'][0].update(url='https:///paper'),
            'duplicate id': lambda c: c['sources'][1].update(id=c['sources'][0]['id']),
            'duplicate URL': lambda c: c['sources'][1].update(url=c['sources'][0]['url']),
            'unknown caution': lambda c: c['evaluation_cautions'][0].update(source_ids=['src-absent']),
            'manufactured replication': lambda c: c['sources'][0].update(independent_replication=True),
        }
        for name, mutate in mutations.items():
            with self.subTest(mutation=name):
                catalog = research.catalog()
                mutate(catalog)
                with self.assertRaises(ContractError):
                    research.validate_catalog(catalog)

    def test_frozen_bundle_retains_catalog_and_verifies_without_live_catalog(self):
        frozen = self.freeze()
        retained = read_json(frozen/'catalog.json')
        self.assertEqual(retained, research.catalog())
        with patch.object(research, 'catalog', side_effect=AssertionError('live catalog consulted')):
            result = research.verify_frozen(frozen)
        self.assertEqual(result['catalog_sha256'], digest(retained))
        self.assertEqual(result['proposal_sha256'], digest(self.control))
        self.assertFalse(result['execution_authorized'])

    def test_frozen_bundle_rejects_proposal_catalog_and_manifest_tampering(self):
        mutations = [
            ('proposal.json', lambda p: p.update(prediction='Tampered prediction')),
            ('catalog.json', lambda c: c['sources'][0].update(title='Tampered source')),
            ('RESEARCH-MANIFEST.json', lambda m: m.update(schema_version=True)),
            ('RESEARCH-MANIFEST.json', lambda m: m.update(execution_authorized=True)),
            ('RESEARCH-MANIFEST.json', lambda m: m.update(execution_performed=True)),
            ('RESEARCH-MANIFEST.json', lambda m: m.update(supported_recipe_compiler=1)),
            ('RESEARCH-MANIFEST.json', lambda m: m.update(missing_capabilities={'training-runtime':'IMPLEMENTED'})),
            ('RESEARCH-MANIFEST.json', lambda m: m.update(remaining_gates=['No further gates'])),
            ('RESEARCH-MANIFEST.json', lambda m: m.update(novelty_status='CONFIRMED')),
            ('RESEARCH-MANIFEST.json', lambda m: m.update(integrity_limit='Authentic executed result')),
            ('RESEARCH-MANIFEST.json', lambda m: m['files'].update({'catalog.json':'0'*64})),
        ]
        for index, (filename, mutate) in enumerate(mutations):
            with self.subTest(file=filename, mutation=index):
                frozen = self.freeze('tampered-'+str(index))
                self.rewrite(frozen/filename, mutate)
                with self.assertRaises(ContractError):
                    research.verify_frozen(frozen)

    def test_frozen_bundle_rejects_inventory_changes_and_symlinks(self):
        for name in ('extra', 'missing', 'member-link', 'root-link'):
            with self.subTest(case=name):
                frozen = self.freeze(name)
                if name=='extra':
                    (frozen/'unexpected.json').write_text('{}')
                elif name=='missing':
                    (frozen/'catalog.json').unlink()
                elif name=='member-link':
                    target = self.root/'retained-catalog.json'
                    (frozen/'catalog.json').rename(target)
                    (frozen/'catalog.json').symlink_to(target)
                else:
                    link = self.root/'bundle-link'
                    link.symlink_to(frozen, target_is_directory=True)
                    frozen = link
                with self.assertRaises(ContractError):
                    research.verify_frozen(frozen)

    def test_freeze_and_compile_never_overwrite_existing_or_dangling_targets(self):
        _, config = fixture()
        for operation in ('freeze', 'compile'):
            for kind in ('directory', 'dangling-symlink'):
                with self.subTest(operation=operation, kind=kind):
                    output = self.root/(operation+'-'+kind)
                    if kind=='directory':
                        output.mkdir()
                        (output/'sentinel').write_text('preserve')
                    else:
                        output.symlink_to(self.root/'absent')
                    with self.assertRaises(FileExistsError):
                        if operation=='freeze': research.freeze_proposal(self.control, output)
                        else: research.compile_control(self.control, config['recipe'], output)
                    if kind=='directory': self.assertEqual((output/'sentinel').read_text(), 'preserve')
                    else: self.assertTrue(output.is_symlink())

    def test_compile_preserves_canonical_recipe_and_never_authorizes_execution(self):
        _, config = fixture()
        self.assertEqual(config['evidence_class'], 'TEST_FIXTURE')
        recipe = config['recipe']
        before = canonical_bytes(recipe)
        proposal = copy.deepcopy(self.control)
        proposal['id'] = 'renamed-control'
        output = self.root/'compiled'
        result = research.compile_control(proposal, recipe, output)
        self.assertEqual(canonical_bytes(read_json(output/'recipe.json')), before)
        self.assertEqual(canonical_bytes(recipe), before)
        self.assertEqual(result['recipe_sha256'], digest(recipe))
        self.assertEqual(result['candidate_delta'], {'cache_prompt': {'baseline':False, 'candidate':True}})
        self.assertFalse(result['execution_authorized'])
        self.assertFalse(result['execution_performed'])
        self.assertIn('canonical content unchanged', result['scope'])

    def test_compile_refuses_unsupported_or_semantically_mutated_proposals(self):
        _, config = fixture()
        proposals = [research.template(row['id']) for row in research.template_list()
                     if row['id']!='prefix-cache-control']
        for field in ('candidate_delta', 'prediction', 'claim_limit'):
            proposal = copy.deepcopy(self.control)
            proposal[field] += ' Changed research semantics.'
            proposals.append(proposal)
        for index, proposal in enumerate(proposals):
            with self.subTest(proposal=proposal['id'], case=index):
                research.validate_proposal(proposal)
                self.assertFalse(research.readiness(proposal)['supported_recipe_compiler'])
                output = self.root/('refused-'+str(index))
                with self.assertRaisesRegex(ContractError, 'exact registered prefix-cache control'):
                    research.compile_control(proposal, config['recipe'], output)
                self.assertFalse(output.exists())

    def test_cli_fixture_roundtrip_and_refusal_preserve_input_content(self):
        proposal = self.root/'proposal.json'
        result = self.cli('propose', '--template', 'prefix-cache-control', '--output', proposal)
        self.assertTrue(result['supported_recipe_compiler'])
        self.assertFalse(result['execution_authorized'])
        frozen = self.root/'frozen-cli'
        self.cli('freeze', proposal, '--output', frozen)
        verified = self.cli('verify', frozen)
        self.assertEqual(verified['proposal_sha256'], digest(read_json(proposal)))
        _, config = fixture()
        recipe = self.root/'input-recipe.json'
        recipe.write_text(json.dumps(config['recipe'], indent=4)+'\n')
        raw_before = recipe.read_bytes()
        compiled = self.root/'compiled-cli'
        result = self.cli('compile', '--proposal', proposal, '--recipe', recipe, '--output', compiled)
        self.assertFalse(result['execution_performed'])
        self.assertEqual(recipe.read_bytes(), raw_before)
        self.assertNotEqual((compiled/'recipe.json').read_bytes(), raw_before)
        self.assertEqual(canonical_bytes(read_json(compiled/'recipe.json')), canonical_bytes(config['recipe']))
        self.cli('propose', '--template', 'prefix-cache-control', '--output', proposal, expected=2)
        self.rewrite(proposal, lambda p: p.update(candidate_delta='Use an unregistered operator.'))
        refused = self.root/'refused-cli'
        error = self.cli('compile', '--proposal', proposal, '--recipe', recipe,
                         '--output', refused, expected=2)
        self.assertIn('exact registered prefix-cache control', error)
        self.assertFalse(refused.exists())


if __name__ == '__main__':
    unittest.main()
