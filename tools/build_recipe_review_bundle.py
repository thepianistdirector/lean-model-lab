#!/usr/bin/env python3
"""Build a verified, local-only 0.4 review candidate from frozen producers and exports."""
from __future__ import annotations

import argparse
import copy
import io
import json
import re
import stat
import subprocess
import sys
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(ROOT / 'tools'))
from build_review_bundle import SOURCE_DIRS, SOURCE_FILES, SUFFIXES, sha, write_zip
from lean_model_lab.contracts import canonical_bytes, digest, parse_json
from lean_model_lab.report import render_report
from lean_model_lab.session import Session
from lean_model_lab.study_report import evaluate_inventory
from lean_model_lab.workbench import build_catalog, render_workbench

MAX_FILE_BYTES = 32 * 1024 * 1024
MAX_WORKBENCH_BYTES = 64 * 1024 * 1024
MAX_ARCHIVE_BYTES = 128 * 1024 * 1024
NAME = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}\Z')


def checked_path(path: Path) -> Path:
    path = Path(path).absolute()
    if '..' in path.parts or not path.is_relative_to(ROOT):
        raise ValueError('inputs and output must be project-scoped without traversal')
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('refusing symlink path')
    return path


def safe_member(name: str) -> None:
    if (not isinstance(name, str) or not name or '\\' in name or '\x00' in name or
            PurePosixPath(name).is_absolute() or any(p in ('', '.', '..') for p in name.split('/')) or
            any(ord(c) < 32 or ord(c) == 127 for c in name)):
        raise ValueError('unsafe archive member')


def check_text(name: str, data: bytes, *, source=False, workbench=False) -> None:
    limit = MAX_WORKBENCH_BYTES if workbench else MAX_FILE_BYTES
    if len(data) > limit or b'\x00' in data:
        raise ValueError('binary or oversized file refused: ' + name)
    text = data.decode('utf-8')
    # Only the pre-existing literal redaction fixtures are admitted in source.
    fixture = source and name.endswith(('tests/test_export.py', 'tools/build_review_bundle.py'))
    paths = re.findall(r'/(?:home|Users|tmp)/[^\s\"\'<>]+', text)
    sentinels = tuple('/' + 'home/' + who + '/' for who in ('fixture', 'other'))
    historical = source and name == 'plan/lineage/821c6364/TASKS.md'
    if any(not ((fixture and p.startswith(sentinels)) or
                (historical and p == '/' + 'tmp/lean-model-lab-pycache')) for p in paths):
        raise ValueError('unreviewed private path in ' + name)
    if re.search(r'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----', text):
        raise ValueError('credential-like content in ' + name)


def read_text(path: Path, name: str, *, source=False, workbench=False) -> bytes:
    limit = MAX_WORKBENCH_BYTES if workbench else MAX_FILE_BYTES
    if not path.is_file() or path.is_symlink() or path.stat().st_size > limit:
        raise ValueError('nonregular or oversized file: ' + name)
    data = path.read_bytes()
    check_text(name, data, source=source, workbench=workbench)
    return data


def collect(root: Path, *, source=False) -> tuple[dict, list]:
    files, directories = {}, []
    for path in sorted(root.rglob('*')):
        if path.is_symlink():
            raise ValueError('refusing symlink entry')
        relative = path.relative_to(root).as_posix()
        safe_member(relative)
        if source and '__pycache__' in path.parts:
            continue
        if path.is_dir():
            directories.append(relative + '/')
        elif path.is_file():
            if source and path.suffix not in SUFFIXES:
                continue
            if not source and path.suffix not in {'.json', '.jsonl', '.html', '.log', '.txt'} and path.name != '.lock':
                raise ValueError('unreviewed evidence file type: ' + relative)
            files[relative] = read_text(path, root.name + '/' + relative if source else relative, source=source)
        else:
            raise ValueError('refusing nonregular entry')
    if len({name.casefold() for name in files}) != len(files):
        raise ValueError('case-colliding file inventory')
    return files, directories


def verify_archive(path: Path) -> dict:
    if not path.is_file() or path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ValueError('archive is missing or oversized')
    data = path.read_bytes()
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        entries = archive.infolist()
        names = [entry.filename for entry in entries]
        if len({name.casefold() for name in names}) != len(names):
            raise ValueError('duplicate archive inventory')
        if sum(entry.file_size for entry in entries) > MAX_ARCHIVE_BYTES:
            raise ValueError('archive expanded size exceeds bound')
        files = {}
        for entry in entries:
            safe_member(entry.filename)
            mode = entry.external_attr >> 16
            if (entry.is_dir() or stat.S_IFMT(mode) not in (0, stat.S_IFREG) or
                    entry.file_size > MAX_FILE_BYTES or entry.flag_bits & 1):
                raise ValueError('unsafe archive entry')
            name = entry.filename
            if not (name in ('BUILD-MANIFEST.json', '__main__.py', 'LICENSE', 'THIRD_PARTY_NOTICES.md') or
                    re.fullmatch(r'lean_model_lab/[A-Za-z_][A-Za-z0-9_]*\.py', name) or
                    re.fullmatch(r'patches/[A-Za-z0-9_.-]+\.patch', name)):
                raise ValueError('unreviewed archive member')
            files[name] = archive.read(entry)
            check_text(name, files[name])
    manifest = parse_json(files.pop('BUILD-MANIFEST.json'))
    if (set(manifest) != {'version', 'artifact_class', 'runtime', 'files'} or
            manifest.get('artifact_class') != 'LOCAL_DEVELOPMENT_CANDIDATE' or
            manifest.get('files') != {name: sha(value) for name, value in files.items()}):
        raise ValueError('CLI manifest inventory or content mismatch')
    runtime = {name: value for name, value in files.items() if name.startswith('lean_model_lab/')}
    if not runtime or files.get('__main__.py') != b'from lean_model_lab.cli import main\nraise SystemExit(main())\n':
        raise ValueError('CLI runtime missing')
    return {'data': data, 'sha256': sha(data), 'bytes': len(data), 'version': manifest['version'],
            'runtime': runtime, 'implementation_sha256': digest({PurePosixPath(k).name: sha(v) for k, v in runtime.items()})}


def verify_export(root: Path, implementations: dict) -> tuple[dict, dict, list]:
    files, directories = collect(root)
    if set(p.name for p in root.iterdir()) != {'EXPORT-READY.json', 'report.json', 'report.html', 'study', 'original-provenance'}:
        raise ValueError('unexpected export root inventory')
    ready = parse_json(files['EXPORT-READY.json'])
    provenance = parse_json(files['study/EXPORT-PROVENANCE.json'])
    report = parse_json(files['report.json'])
    if (ready.get('status') != 'LOCAL_REDACTED_EXPORT_VERIFIED_NOT_PUBLISHED' or
            ready.get('provenance_sha256') != sha(files['study/EXPORT-PROVENANCE.json']) or
            ready.get('report_sha256') != sha(files['report.json']) or
            provenance.get('export_class') != 'REDACTED_DERIVATIVE_NOT_ORIGINAL_RAW' or
            provenance.get('report_unchanged_sha256') != digest(report)):
        raise ValueError('export ready, provenance or report hash mismatch')
    with Session.open(root / 'study') as session:
        inventory = session.inspect()
    if not inventory['inventory_complete'] or canonical_bytes(evaluate_inventory(inventory,study_root=root / 'study')) != canonical_bytes(report):
        raise ValueError('export report differs from finalized Session inventory')
    if files['report.html'] != render_report(report).encode():
        raise ValueError('export HTML differs from report')
    implementation = inventory['config']['implementation_sha256']
    if implementation not in implementations:
        raise ValueError('study implementation has no included producer archive')
    if (ready.get('expected_requests') != len(inventory['workload']['requests']) * len(inventory['attempts']) or
            ready.get('observed_requests') != sum(len(a['requests']) for a in inventory['attempts'])):
        raise ValueError('export request counts differ')
    original = parse_json(files['original-provenance/file-catalog.json'])
    for name, metadata in original.items():
        safe_member(name)
        if not isinstance(metadata, dict) or set(metadata) != {'sha256', 'size_bytes'}:
            raise ValueError('malformed original file catalog')
    changes = provenance['changed_raw_files']
    if ready.get('changed_raw_file_count') != len(changes) or len({c['path'] for c in changes}) != len(changes):
        raise ValueError('export change inventory differs')
    changed = {change['path']: change for change in changes}
    for name, change in changed.items():
        safe_member(name)
        value = files.get('study/' + name)
        if (not name.startswith('raw/') or value is None or change['original'] != original.get(name) or
                change['exported'] != {'sha256': sha(value), 'size_bytes': len(value)}):
            raise ValueError('redaction provenance differs from exported bytes')
    # Bind all unchanged bytes, including normalized attempts, to the retained original catalog.
    derivative = {name[6:]: data for name, data in files.items() if name.startswith('study/') and name != 'study/EXPORT-PROVENANCE.json'}
    if set(derivative) != set(original):
        raise ValueError('original and exported file inventories differ')
    for name, value in derivative.items():
        if name not in changed and name != 'journal.jsonl' and not name.startswith('events/'):
            if original[name] != {'sha256': sha(value), 'size_bytes': len(value)}:
                raise ValueError('unchanged export bytes differ from original catalog')
    for prefix, head_key in (('original-provenance/', 'source_event_chain_head_sha256'), ('study/', 'exported_event_chain_head_sha256')):
        session_data = files[prefix + 'session.json']
        previous = digest(parse_json(session_data))
        events = []
        for name in sorted(n for n in files if n.startswith(prefix + 'events/')):
            event = parse_json(files[name])
            if event['previous_sha256'] != previous:
                raise ValueError('provenance event chain differs')
            previous = digest(event)
            events.append(event)
        journal = files[prefix + 'journal.jsonl']
        if journal != b''.join(canonical_bytes(event) + b'\n' for event in events) or previous != provenance[head_key]:
            raise ValueError('provenance journal or chain head differs')
        if prefix == 'original-provenance/':
            if sha(session_data) != provenance['source_session_sha256'] or sha(journal) != provenance['source_journal_sha256']:
                raise ValueError('original provenance hash differs')
            for name, value in files.items():
                if name.startswith(prefix) and name != prefix + 'file-catalog.json':
                    relative = name[len(prefix):]
                    if original.get(relative) != {'sha256': sha(value), 'size_bytes': len(value)}:
                        raise ValueError('original provenance bytes differ from catalog')
    original_events = [parse_json(files[name]) for name in sorted(files) if name.startswith('original-provenance/events/')]
    exported_events = [parse_json(files[name]) for name in sorted(files) if name.startswith('study/events/')]
    if len(original_events) != len(exported_events):
        raise ValueError('original and exported event counts differ')
    for before, after in zip(original_events, exported_events):
        before.pop('previous_sha256')
        after.pop('previous_sha256')
        if before['kind'] == 'terminal':
            raw_prefix = 'raw/' + before['payload']['attempt_id'] + '/'
            expected_before = [{'path': name[len(raw_prefix):], **metadata}
                               for name, metadata in sorted(original.items()) if name.startswith(raw_prefix)]
            if before['payload']['raw_files'] != expected_before:
                raise ValueError('original terminal raw inventory differs from catalog')
            before['payload']['raw_files'] = [{'path': row['path'], **changed[raw_prefix + row['path']]['exported']}
                if raw_prefix + row['path'] in changed else row for row in expected_before]
        if canonical_bytes(before) != canonical_bytes(after):
            raise ValueError('export altered non-redaction event content')
    if collect(root) != (files, directories):
        raise ValueError('export changed during verification')
    summary = {'session_id': inventory['session_id'], 'implementation_sha256': implementation,
               'producer_artifacts': implementations[implementation], 'evidence_class': report['evidence_class'],
               'finding': report['finding'], 'eligible': report['eligible'],
               'measured_claim_eligible': report['measured_claim_eligible'],
               'report_sha256': sha(files['report.json']), 'provenance_sha256': ready['provenance_sha256']}
    return summary, files, directories


def build(output: Path, archive: Path, producers: list[Path], studies: list[tuple[str, Path]],
          workbench_json: Path, workbench_html: Path) -> dict:
    output, archive, workbench_json, workbench_html = map(checked_path, (output, archive, workbench_json, workbench_html))
    producers = [checked_path(p) for p in producers]
    studies = [(name, checked_path(path)) for name, path in studies]
    if not producers or not studies or any(not NAME.fullmatch(name) for name, _ in studies):
        raise ValueError('provide producers and studies with safe unique names')
    if len({name.casefold() for name, _ in studies}) != len(studies):
        raise ValueError('study name collision')
    inputs = [archive, *producers, *(p for _, p in studies), workbench_json, workbench_html]
    for index, path in enumerate([output, *inputs]):
        if any(path.is_relative_to(other) or other.is_relative_to(path) for other in [output, *inputs][index + 1:]):
            raise ValueError('output or input paths overlap')
    if output.exists():
        raise ValueError('output already exists; no overwrite')
    if any(output.is_relative_to(ROOT / name) for name in SOURCE_DIRS):
        raise ValueError('output overlaps source allowlist')
    final = verify_archive(archive)
    payloads = {'lean-model-lab.pyz': final['data']}
    implementations = {final['implementation_sha256']: ['lean-model-lab.pyz']}
    producer_records = []
    for path in producers:
        producer = verify_archive(path)
        name = 'producer-' + producer['sha256'] + '.pyz'
        if name in payloads:
            raise ValueError('duplicate producer archive')
        payloads[name] = producer['data']
        implementations.setdefault(producer['implementation_sha256'], []).append(name)
        producer_records.append({key: producer[key] for key in ('sha256', 'bytes', 'version', 'implementation_sha256')} | {'artifact': name})
    source = {}
    for name in SOURCE_FILES:
        source['lean-model-lab-source/' + name] = read_text(ROOT / name, name, source=True)
    for name in SOURCE_DIRS:
        directory = checked_path(ROOT / name)
        entries, _ = collect(directory, source=True)
        for relative, data in entries.items():
            source['lean-model-lab-source/' + name + '/' + relative] = data
    runtime_prefix = 'lean-model-lab-source/src/'
    runtime = {name[len(runtime_prefix):]: data for name, data in source.items()
               if name.startswith(runtime_prefix + 'lean_model_lab/') and name.endswith('.py')}
    if runtime != final['runtime']:
        raise ValueError('source runtime differs from final CLI')
    base = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True, capture_output=True, check=True).stdout.strip()
    source['lean-model-lab-source/BASE-REVISION.txt'] = (base + '\nUncommitted source snapshot; FILE-MANIFEST.json is its exact inventory.\n').encode()
    evidence, directories, summaries = {}, [], {}
    for name, path in studies:
        summary, files, dirs = verify_export(path, implementations)
        summaries[name] = summary
        evidence.update({'evidence/' + name + '/' + key: value for key, value in files.items()})
        directories.extend('evidence/' + name + '/' + entry for entry in dirs)
    json_data = read_text(workbench_json, 'workbench.json', workbench=True)
    html_data = read_text(workbench_html, 'workbench.html', workbench=True)
    supplied = parse_json(json_data)
    expected = build_catalog([path / 'study' for _, path in studies])
    # Basename labels are presentation only: private originals and redacted copies differ.
    normalized = copy.deepcopy(supplied)
    if len(normalized.get('studies', [])) != len(expected['studies']):
        raise ValueError('workbench study inventory differs')
    for actual, required in zip(normalized['studies'], expected['studies']):
        if not isinstance(actual.get('label'), str) or not actual['label'] or len(actual['label']) > 120:
            raise ValueError('invalid workbench label')
        actual['label'] = required['label']
    if canonical_bytes(normalized) != canonical_bytes(expected) or html_data != render_workbench(supplied).encode():
        raise ValueError('workbench differs from included exports or renderer')
    payloads.update({'workbench.json': json_data, 'workbench.html': html_data})
    # Snapshot all inputs before creating output. No incomplete candidate manifest on failure.
    output.mkdir(parents=True, exist_ok=False)
    artifacts = {'lean-model-lab-source.zip': write_zip(output / 'lean-model-lab-source.zip', source),
                 'lean-model-lab-evidence.zip': write_zip(output / 'lean-model-lab-evidence.zip', evidence, directories)}
    for name, data in sorted(payloads.items()):
        with (output / name).open('xb') as stream:
            stream.write(data)
        if (output / name).read_bytes() != data:
            raise ValueError('artifact readback differs')
        artifacts[name] = {'sha256': sha(data), 'bytes': len(data)}
    result = {'schema_version': 1, 'status': 'LOCAL_REVIEW_CANDIDATE_NOT_PUBLISHED', 'version': final['version'],
              'source_base_revision': base, 'source_snapshot': 'Exact uncommitted allowlisted bytes in source ZIP FILE-MANIFEST.json',
              'artifacts': artifacts, 'final_cli_implementation_sha256': final['implementation_sha256'],
              'source_runtime_matches_final_cli': True, 'producer_archives': producer_records, 'studies': summaries,
              'workbench_matches_included_exports': True,
              'integrity_limit': 'Local hash consistency is not producer authentication, independent execution, or proof against omitted evidence.',
              'privacy_scope': 'Allowlisted UTF-8 source and evidence, scoped path and credential pattern checks; no model weights, native backend, browser binaries, or private original raw bytes.',
              'missing_release_gates': ['public authorization, publication and author identity',
                  'supported authenticated native Tanduna publication and actual review/decision',
                  'external execution and recovery from the public artifact', 'qualified researcher observations',
                  'independent browser accessibility review']}
    with (output / 'CANDIDATE-MANIFEST.json').open('x') as stream:
        stream.write(json.dumps(result, sort_keys=True, indent=2) + '\n')
    return result


def study_argument(value: str) -> tuple[str, Path]:
    name, separator, path = value.partition('=')
    if not separator or not path or not NAME.fullmatch(name):
        raise argparse.ArgumentTypeError('study must be SAFE_NAME=EXPORT_DIRECTORY')
    return name, Path(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--archive', type=Path, required=True)
    parser.add_argument('--producer', type=Path, action='append', required=True)
    parser.add_argument('--study', type=study_argument, action='append', required=True)
    parser.add_argument('--workbench-json', type=Path, required=True)
    parser.add_argument('--workbench-html', type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(build(args.output, args.archive, args.producer, args.study, args.workbench_json, args.workbench_html), indent=2))
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        print('review candidate refused: ' + str(exc), file=sys.stderr)
        raise SystemExit(2)
