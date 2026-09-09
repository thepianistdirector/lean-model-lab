#!/usr/bin/env python3
"""Verify the locally built zipapp with synthetic evidence; never execute inference."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'tests')]
from build_archive import build
from lean_model_lab.artifacts import write_json_new
from lean_model_lab.contracts import file_digest, make_workload
from lean_model_lab.runner import implementation_digest
from test_evidence import CONFIG, make_campaign
from test_study_report import fixture_study


def verify(root: Path) -> dict:
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=False)
    archive = root / 'lean-model-lab.pyz'
    receipt = build(archive)
    rebuilt = root / 'repeat-build.pyz'
    build(rebuilt)
    if archive.read_bytes() != rebuilt.read_bytes():
        raise RuntimeError('identical source did not produce identical archives')
    with zipfile.ZipFile(archive) as bundle:
        manifest = json.loads(bundle.read('BUILD-MANIFEST.json'))
        if set(bundle.namelist()) != set(manifest['files']) | {'BUILD-MANIFEST.json'}:
            raise RuntimeError('archive inventory differs from manifest')
        for name, expected in manifest['files'].items():
            if hashlib.sha256(bundle.read(name)).hexdigest() != expected:
                raise RuntimeError(f'archive manifest mismatch: {name}')
    work = root / 'isolated-cwd'
    work.mkdir()
    environment = {k: v for k, v in os.environ.items() if not k.startswith('PYTHON')}
    checks = []

    def command(label, *args, expected=0):
        process = subprocess.run([sys.executable, '-I', str(archive), *map(str, args)],
                                 cwd=work, env=environment, text=True, capture_output=True,
                                 timeout=30, check=False)
        if process.returncode != expected:
            raise RuntimeError(f'{label}: exit {process.returncode}: {process.stderr}')
        checks.append({'check': label, 'status': 'PASS', 'exit_code': process.returncode})
        return json.loads(process.stdout) if process.stdout.strip() else None

    probe = subprocess.run([sys.executable, '-I', '-c',
        'import sys; sys.path.insert(0, sys.argv[1]); '
        'from lean_model_lab.runner import implementation_digest; print(implementation_digest())',
        str(archive)], cwd=work, env=environment, text=True, capture_output=True,
        timeout=30, check=True)
    if probe.stdout.strip() != implementation_digest():
        raise RuntimeError('source and archive implementation identities differ')
    checks.append({'check': 'deterministic_manifest_and_implementation_identity', 'status': 'PASS'})
    trace = work / 'trace.json'
    command('create_trace', 'trace', 'create', '--output', trace)
    command('validate_trace', 'trace', 'validate', trace)
    before = file_digest(trace)
    command('refuse_trace_overwrite', 'trace', 'create', '--output', trace, expected=2)
    if file_digest(trace) != before:
        raise RuntimeError('refused overwrite changed trace')
    write_json_new(work / 'config.json', CONFIG)
    attempts = work / 'attempts'
    attempts.mkdir()
    for index, attempt in enumerate(make_campaign()):
        write_json_new(attempts / f'{index:02}.json', attempt)
    result = command('evaluate_fixtures', 'evaluate', '--workload', trace,
        '--config', work / 'config.json', '--attempts', attempts,
        '--output', work / 'evaluation.json', '--html', work / 'evaluation.html')
    if result['measured_claim_eligible'] or result['attempt_count'] != 12:
        raise RuntimeError('synthetic evaluator result mislabeled or incomplete')
    damaged = make_workload()
    damaged['requests'].pop()
    write_json_new(work / 'damaged-trace.json', damaged)
    command('reject_missing_request', 'trace', 'validate', work / 'damaged-trace.json', expected=2)
    study = work / 'study'
    fixture_study(study)
    inventory = command('inspect_complete_inventory', 'inspect', study)
    if not inventory['inventory_complete'] or inventory['terminal_attempt_count'] != 12:
        raise RuntimeError('packaged inventory lost fixture attempts')
    hashes = {str(p.relative_to(study)): file_digest(p) for p in study.rglob('*') if p.is_file()}
    result = command('report_complete_inventory', 'report', study,
        '--output', work / 'report.json', '--html', work / 'report.html')
    if result['measured_claim_eligible']:
        raise RuntimeError('synthetic study report became measured evidence')
    if hashes != {str(p.relative_to(study)): file_digest(p) for p in study.rglob('*') if p.is_file()}:
        raise RuntimeError('rendering changed producer inventory')
    journal = study / 'journal.jsonl'
    journal.write_bytes(journal.read_bytes() + b'{"schema_version":')
    damaged_hash = file_digest(journal)
    inventory = command('detect_torn_journal', 'inspect', study)
    if not inventory['journal_recovery_required']:
        raise RuntimeError('torn journal was not detected')
    command('reject_unreconciled_report', 'report', study,
        '--output', work / 'invalid-report.json', expected=2)
    command('recover_journal', 'recover-journal', study)
    if not any(file_digest(p) == damaged_hash for p in study.rglob('*') if p.is_file()):
        raise RuntimeError('journal repair failed to retain original damaged bytes')
    inventory = command('inspect_recovered_inventory', 'inspect', study)
    if inventory['journal_recovery_required'] or inventory['terminal_attempt_count'] != 12:
        raise RuntimeError('journal repair lost inventory or remained unreconciled')
    result = {'schema_version': 1, 'evidence_class': 'TEST_FIXTURE',
              'scope': 'locally built package on the development host; no model inference or external reproduction',
              'artifact': receipt, 'implementation_sha256': implementation_digest(),
              'python': sys.version.split()[0], 'checks': checks,
              'measured_claim_eligible': False}
    write_json_new(root / 'verification.json', result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    print(json.dumps(verify(parser.parse_args().output), indent=2))
