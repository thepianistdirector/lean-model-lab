"""Offline comparison integrity and renderer checks. No model or browser required."""
import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

from lean_model_lab.artifacts import write_json_new, append_event
from lean_model_lab.contracts import digest, file_digest, make_workload
from lean_model_lab.session import Session
from lean_model_lab.workbench import WorkbenchError, build_catalog, render_workbench
from test_evidence import CONFIG, make_campaign
from test_study_report import setup_records


def create_study(root, attempts=None, config=None, native=None):
    config = copy.deepcopy(CONFIG if config is None else config)
    Session.create(root, config, make_workload(), setup_records())
    with Session.open(root) as session:
        for attempt in copy.deepcopy(make_campaign() if attempts is None else attempts):
            attempt['config_sha256'] = digest(config)
            reservation = session.reserve(attempt['arm'], attempt['concurrency'], attempt['pair_index'], attempt['started_ns'])
            attempt['attempt_id'] = reservation['attempt_id']
            if native:
                native(reservation['raw_dir'], attempt)
            session.publish(attempt)
    return root


def hashes(root):
    return {str(p.relative_to(root)): file_digest(p) for p in root.rglob('*') if p.is_file()}


def native_files(directory, attempt, corrupt=False):
    """Retain native receipts for a single interrupted fixture request."""
    request = attempt['requests'][0]
    count = request['prompt_tokens']
    tokens = [[7] * (r['stratum'] + 30) for r in make_workload()['requests']]
    write_json_new(directory / 'tokenized-inputs.json', {'workload_sha256': attempt['workload_sha256'], 'tokens': tokens})
    records = [(request['dispatch_ns'], {'stop': False, 'id_slot': -1, 'tokens': [0], 'content': '',
        'tokens_predicted': 0, 'tokens_evaluated': count,
        'prompt_progress': {'total': count, 'cache': 0, 'processed': count, 'time_ms': 0}})]
    for i, event in enumerate(request['token_events']):
        records.append((event['observed_ns'], {'stop': False, 'id_slot': -1, 'tokens': event['token_ids'],
            'content': request['output_text'][:2] if i == 0 else request['output_text'][2:]}))
    records.append((request['completed_ns'], {'stop': True, 'id_slot': 0, 'tokens': [], 'content': '',
        'tokens_predicted': request['generated_tokens'], 'tokens_evaluated': count, 'truncated': False,
        'stop_type': 'eos', 'stopping_word': '', 'generation_settings': {'samplers': ['temperature'],
            'temperature': 0, 'seed': 20260907, 'n_predict': 32, 'ignore_eos': False, 'stop': [],
            'stream': True, 'grammar': '', 'lora': [], 'backend_sampling': False},
        'timings': {'cache_n': 1 if corrupt else 0, 'prompt_n': count, 'predicted_n': request['generated_tokens']}}))
    for timestamp, payload in records:
        append_event(directory / (request['request_id'] + '.jsonl'), {'observed_ns': timestamp, 'data_utf8': json.dumps(payload)})


class Structure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.ids = []
        self.labels = []
        self.scripts = []
        self.in_catalog = False
        self.catalog = ''

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'label':
            self.labels.append(attrs.get('for'))
        if tag == 'script':
            self.scripts.append(attrs)
            self.in_catalog = attrs.get('id') == 'workbench-catalog'

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_catalog = False

    def handle_data(self, text):
        if self.in_catalog:
            self.catalog += text


class WorkbenchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_catalog_preserves_all_attempts_source_bytes_and_metric_references(self):
        study = create_study(self.root / 'study')
        before = hashes(study)
        catalog = build_catalog([study])
        page = render_workbench(catalog)
        self.assertEqual(before, hashes(study))
        result = catalog['studies'][0]
        self.assertEqual(12, len(result['attempts']))
        self.assertEqual(1536, sum(len(a['requests']) for a in result['attempts']))
        self.assertEqual(1536, result['quality']['denominator'])
        self.assertFalse(result['measured_claim_eligible'])
        self.assertEqual('TEST_FIXTURE', result['evidence_class'])
        self.assertNotIn(str(self.root), json.dumps(catalog))
        self.assertNotIn(str(self.root), page)
        request = result['attempts'][0]['requests'][0]
        pointer = request['source']
        document = json.loads((study / pointer['document']).read_text())
        self.assertEqual(document['requests'][0], request['normalized'])
        self.assertEqual('/requests/0', pointer['pointer'])
        self.assertEqual('UNAVAILABLE', request['native']['cache']['status'])
        self.assertIsNone(catalog['cross_study_ratios'])

    def test_partial_schedule_retains_costs_missing_rows_and_null_ratios(self):
        attempts = make_campaign()[:7]
        attempts[-1]['status'] = 'INTERRUPTED'
        attempts[-1]['requests'] = attempts[-1]['requests'][:5]
        result = build_catalog([create_study(self.root / 'recovery', attempts)])['studies'][0]
        self.assertFalse(result['eligible'])
        self.assertTrue(result['finalized_inventory'])
        self.assertEqual(123, result['accounting']['missing_requests'])
        self.assertEqual(7, result['accounting']['attempt_count'])
        self.assertEqual(5, sum(r['observed'] for r in result['attempts'][-1]['requests']))
        self.assertEqual('MISSING', result['attempts'][-1]['requests'][-1]['status'])
        self.assertGreater(result['accounting']['full_cost_accounting']['registered_full_wall_ns'], 0)
        for group in result['concurrency_groups'].values():
            self.assertIsNone(group['throughput_ratio_range'])
            for pair in group['pairs']:
                self.assertIsNone(pair['throughput_candidate_over_baseline'])

    def test_unresolved_or_torn_journal_is_rejected_without_repair(self):
        study = create_study(self.root / 'unresolved', [])
        with Session.open(study) as session:
            session.reserve('baseline', 1, 0, 1000)
        before = hashes(study)
        with self.assertRaisesRegex(WorkbenchError, 'finalized'):
            build_catalog([study])
        self.assertEqual(before, hashes(study))
        study = create_study(self.root / 'torn', make_campaign()[:1])
        with (study / 'journal.jsonl').open('ab') as stream:
            stream.write(b'{')
        before = hashes(study)
        with self.assertRaises(WorkbenchError):
            build_catalog([study])
        self.assertEqual(before, hashes(study))

    def test_tampered_normalized_raw_and_configuration_are_rejected(self):
        for kind in ('normalized', 'raw', 'config'):
            with self.subTest(kind=kind):
                study = create_study(self.root / kind, make_campaign()[:1])
                if kind == 'normalized':
                    path = next((study / 'attempts').glob('*.json'))
                    document = json.loads(path.read_text())
                    document['requests'][0]['output_text'] = 'changed'
                    path.write_text(json.dumps(document))
                elif kind == 'raw':
                    directory = next((study / 'raw').iterdir())
                    (directory / 'extra.json').write_text('{}')
                else:
                    path = study / 'config.json'
                    document = json.loads(path.read_text())
                    document['backend']['server_sha256'] = 'b' * 64
                    path.write_text(json.dumps(document))
                before = hashes(study)
                with self.assertRaises(WorkbenchError):
                    build_catalog([study])
                self.assertEqual(before, hashes(study))

    def test_same_path_and_copied_session_rejected_independent_repeat_retained(self):
        first = create_study(self.root / 'first', make_campaign()[:1])
        with self.assertRaisesRegex(WorkbenchError, 'duplicate'):
            build_catalog([first, first])
        second = self.root / 'copy'
        shutil.copytree(first, second)
        with self.assertRaisesRegex(WorkbenchError, 'duplicate source session'):
            build_catalog([first, second])
        third = create_study(self.root / 'independent', make_campaign()[:1])
        result = build_catalog([first, third])
        self.assertEqual(2, result['summary']['study_count'])
        self.assertEqual(1, len(result['compatibility_groups']))

    def test_backend_binary_and_implementation_separate_compatibility(self):
        first = create_study(self.root / 'first', make_campaign()[:1])
        config = copy.deepcopy(CONFIG)
        config['backend']['server_sha256'] = 'b' * 64
        second = create_study(self.root / 'different-binary', make_campaign()[:1], config)
        config = copy.deepcopy(CONFIG)
        config['implementation_sha256'] = 'c' * 64
        third = create_study(self.root / 'different-implementation', make_campaign()[:1], config)
        result = build_catalog([first, second, third])
        self.assertEqual(3, len(result['compatibility_groups']))
        self.assertIsNone(result['cross_study_ratios'])

    def test_quality_and_text_parity_are_separate_from_token_parity(self):
        attempts = make_campaign()
        attempts[1]['requests'][0]['output_text'] = 'wrong'
        candidate = attempts[1]['requests'][1]
        candidate['output_token_ids'][0] = 999
        candidate['token_events'][0]['token_ids'][0] = 999
        result = build_catalog([create_study(self.root / 'mismatch', attempts)])['studies'][0]
        requests = result['attempts'][1]['requests']
        self.assertFalse(requests[0]['quality_correct'])
        self.assertEqual('PASS', requests[0]['parity']['status'])
        self.assertFalse(requests[0]['parity']['output_text_equal'])
        self.assertEqual('FAIL', requests[1]['parity']['status'])
        self.assertTrue(requests[1]['quality_correct'])
        self.assertFalse(result['eligible'])

    def test_duplicate_cell_keeps_all_attempts_but_parity_is_ambiguous(self):
        attempts = make_campaign()
        extra = copy.deepcopy(attempts[0])
        offset = attempts[-1]['finished_ns'] + 1000
        for key in ('started_ns', 'service_started_ns', 'finished_ns'):
            extra[key] += offset
        for row in extra['requests']:
            for key in ('arrival_ns', 'admitted_ns', 'dispatch_ns', 'first_token_ns', 'completed_ns'):
                row[key] += offset
            for event in row['token_events']:
                event['observed_ns'] += offset
        result = build_catalog([create_study(self.root / 'retry', attempts + [extra])])['studies'][0]
        self.assertEqual(13, len(result['attempts']))
        self.assertEqual('UNAVAILABLE', result['attempts'][0]['requests'][0]['parity']['status'])
        self.assertFalse(result['eligible'])

    def test_hostile_output_is_escaped_in_markup_and_embedded_json(self):
        attempts = make_campaign()[:1]
        hostile = '</script><img src=x onerror=alert(1)>\u2028&'
        attempts[0]['requests'][0]['output_text'] = hostile
        result = build_catalog([create_study(self.root / '<odd> study', attempts)])
        page = render_workbench(result)
        self.assertNotIn('<img', page)
        self.assertNotIn(hostile, page)
        self.assertIn('&lt;/script&gt;', page)
        parsed = Structure()
        parsed.feed(page)
        self.assertEqual(2, len(parsed.scripts))
        self.assertEqual(result, json.loads(parsed.catalog))
        self.assertEqual('_odd_ study', result['studies'][0]['label'])

    def test_accessibility_structure_and_offline_contract(self):
        catalog = build_catalog([create_study(self.root / 'study', make_campaign()[:1])])
        page = render_workbench(catalog)
        parser = Structure()
        parser.feed(page)
        self.assertEqual(len(parser.ids), len(set(parser.ids)))
        controls = [a for tag, a in parser.tags if tag == 'select']
        self.assertEqual(7, len(controls))
        self.assertTrue(all(c['id'] in parser.labels for c in controls))
        self.assertTrue(all('disabled' in c for c in controls))
        self.assertTrue(all(a.get('scope') == 'col' for tag, a in parser.tags if tag == 'th'))
        self.assertTrue(all('src' not in a for a in parser.scripts))
        self.assertNotIn('fetch(', page)
        self.assertNotIn('innerHTML', page)
        self.assertIn(':focus-visible', page)
        self.assertIn('aria-live="polite"', page)
        self.assertIn('<noscript>', page)
        self.assertIn('No request evidence matches', page)
        self.assertIn("connect-src 'none'", page)

    def test_supported_native_cache_replay_and_malformed_accounting(self):
        attempts = make_campaign()[:1]
        attempts[0]['status'] = 'INTERRUPTED'
        attempts[0]['requests'] = attempts[0]['requests'][:1]
        study = create_study(self.root / 'native', attempts, native=native_files)
        native = build_catalog([study])['studies'][0]['attempts'][0]['requests'][0]['native']
        self.assertEqual('RECONCILED_NATIVE', native['cache']['status'])
        self.assertEqual(0, native['cache']['reused_input_tokens'])
        self.assertEqual('PASS', native['normalized_replay']['status'])
        malformed = create_study(self.root / 'malformed', attempts,
            native=lambda directory, attempt: native_files(directory, attempt, corrupt=True))
        with self.assertRaisesRegex(WorkbenchError, 'cache accounting'):
            build_catalog([malformed])

    @unittest.skipUnless(shutil.which('node'), 'Node is unavailable; browser checks remain manual')
    def test_filter_script_combines_controls_empty_state_and_reset(self):
        catalog = build_catalog([create_study(self.root / 'study', make_campaign()[:1])])
        page = render_workbench(catalog)
        script = page.rsplit('<script>', 1)[1].split('</script>', 1)[0]
        harness = r"""
const assert = require('assert');
function control(key){return {dataset:{filter:key},value:'',disabled:true,events:{},addEventListener(k,f){this.events[k]=f;}};}
const keys=['study','family','concurrency','pair','arm','quality','parity'];
const controls=keys.map(control);
const rows=[
{dataset:{study:'study-1',family:'family-1',concurrency:'1',pair:'0',arm:'baseline',quality:'fail',parity:'FAIL'}},
{dataset:{study:'study-2',family:'family-2',concurrency:'4',pair:'1',arm:'candidate',quality:'pass',parity:'PASS'}}];
const reset=control('reset'); const status={}; const empty={hidden:true};
global.document={querySelectorAll:s=>s==='[data-filter]'?controls:rows,getElementById:id=>id==='reset-filters'?reset:id==='filter-count'?status:empty};
""" + script + r"""
assert(controls.every(c=>!c.disabled));assert(!reset.disabled);
for(const [index,key] of keys.entries()){
controls[index].value=rows[0].dataset[key];controls[index].events.change();
assert.strictEqual(rows[0].hidden,false);assert.strictEqual(rows[1].hidden,true);
reset.events.click();assert(rows.every(r=>!r.hidden));
}
controls[0].value='study-1';controls[2].value='4';controls[0].events.change();
assert(rows.every(r=>r.hidden));assert.strictEqual(empty.hidden,false);assert.strictEqual(status.textContent,'0 of 2 request rows shown.');
reset.events.click();assert(rows.every(r=>!r.hidden));assert.strictEqual(empty.hidden,true);
"""
        completed = subprocess.run(['node', '-e', harness], capture_output=True, text=True, check=False)
        self.assertEqual(0, completed.returncode, completed.stderr)

    def test_native_semantic_mismatch_and_missing_tokenizer_are_rejected(self):
        attempts = make_campaign()[:1]
        attempts[0]['status'] = 'INTERRUPTED'
        attempts[0]['requests'] = attempts[0]['requests'][:1]
        def different_output(directory, attempt):
            native_files(directory, attempt)
            attempt['requests'][0]['output_text'] = 'changed after native capture'
        study = create_study(self.root / 'native-mismatch', attempts, native=different_output)
        with self.assertRaisesRegex(WorkbenchError, 'normalized request'):
            build_catalog([study])
        def missing_tokenizer(directory, attempt):
            native_files(directory, attempt)
            (directory / 'tokenized-inputs.json').unlink()
        study = create_study(self.root / 'no-tokenizer', attempts, native=missing_tokenizer)
        with self.assertRaisesRegex(WorkbenchError, 'tokenizer evidence'):
            build_catalog([study])

    def test_same_basename_studies_get_distinct_portable_labels_without_changing_sources(self):
        (self.root / 'one').mkdir()
        (self.root / 'two').mkdir()
        first = create_study(self.root / 'one' / 'study', make_campaign()[:1])
        second = create_study(self.root / 'two' / 'study', make_campaign()[:1])
        before = (hashes(first), hashes(second))
        catalog = build_catalog([first, second])
        self.assertEqual(['study [study-1]', 'study [study-2]'], [s['label'] for s in catalog['studies']])
        frozen = copy.deepcopy(catalog)
        page = render_workbench(catalog)
        self.assertEqual(frozen, catalog)
        self.assertEqual(before, (hashes(first), hashes(second)))
        self.assertIn('study [study-1]', page)
        self.assertNotIn(str(self.root), page)

    def test_family_filter_and_readable_cost_and_request_evidence_keep_json(self):
        catalog = build_catalog([create_study(self.root / 'study', make_campaign()[:1])])
        page = render_workbench(catalog)
        self.assertIn('id="filter-family"', page)
        self.assertIn('data-family="synthetic-key-copy-v1"', page)
        self.assertIn('Cost breakdown and setup history', page)
        self.assertIn('Coordinator or idle wall', page)
        self.assertIn('Paired output token IDs', page)
        self.assertIn('Generated token count', page)
        self.assertIn('Normalized record and source references', page)
        parsed = Structure()
        parsed.feed(page)
        self.assertEqual(catalog, json.loads(parsed.catalog))

    def test_empty_input_rejected(self):
        with self.assertRaises(WorkbenchError):
            build_catalog([])


if __name__ == '__main__':
    unittest.main()
