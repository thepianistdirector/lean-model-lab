#!/usr/bin/env python3
"""Verify and reuse prepared model/backend bytes under an existing allocation.

No download, build, server execution or subprocess is performed. Historical
setup costs stay in an explicit ancestor scope, outside the new setup ledger.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import stat
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))

from lean_model_lab.allocation import validate_allocation
from lean_model_lab.artifacts import append_event, write_json_new, write_new
from lean_model_lab.contracts import ContractError, digest, file_digest, parse_json, read_json
from lean_model_lab.llama_adapter import BACKEND_COMMIT, BACKEND_PATCH_FILENAME, BACKEND_PATCH_SHA256
from lean_model_lab.profiles import LEGACY_PROFILE, SMALL_PROFILE, get_model_profile, model_files, verify_model_files
from lean_model_lab.resources import heavy_job, require_workspace_root
from lean_model_lab.runner import _rss
from lean_model_lab.setup import validate_receipt

MAX_RECEIPT_BYTES = 2 * 1024 * 1024


def workspace_path(path: Path, root: Path, *, existing=True, directory=False) -> Path:
    """Refuse symlink components and lexical escapes, including output parents."""
    if '..' in path.parts:
        raise ContractError('parent traversal is not allowed in adoption paths')
    path = path.absolute()
    if not path.is_relative_to(root) or path == root:
        raise ContractError('adoption artifacts must remain inside the same workspace')
    parts = path.relative_to(root).parts
    current = root
    for index, part in enumerate(parts):
        current = current / part
        final = index == len(parts) - 1
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            if final and not existing:
                return path
            raise ContractError('adoption path or parent does not exist') from None
        if stat.S_ISLNK(mode):
            raise ContractError('adoption paths must not contain symlinks')
        if not final or directory:
            if not stat.S_ISDIR(mode):
                raise ContractError('adoption parent must be a directory')
        elif not stat.S_ISREG(mode):
            raise ContractError('adoption input must be a regular file')
    if not existing:
        raise ContractError('adoption output already exists; refusing overwrite')
    return path


def fingerprint(path: Path) -> tuple:
    value = path.stat(follow_symlinks=False)
    return (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)


class Budget:
    """Check time/RSS per hash chunk; scan workspace disk at bounded intervals."""
    def __init__(self, root, allocation):
        self.root = root
        self.allocation = allocation
        self.peak = 0
        self.last_disk_ns = 0
        self.disk_bytes = 0

    def quick(self):
        if time.monotonic_ns() >= self.allocation['deadline_ns']:
            raise TimeoutError('current allocation deadline exhausted; no extension')
        used = _rss(os.getpid())
        if used is None:
            raise ContractError('cannot observe adoption process RSS')
        self.peak = max(self.peak, used)
        if used > self.allocation['limits']['memory_bytes']:
            raise MemoryError('adoption process RSS exceeds current allocation')

    def __call__(self, *, force_disk=False):
        self.quick()
        now = time.monotonic_ns()
        if force_disk or now - self.last_disk_ns >= 10**9:
            total = 0
            stack = [self.root]
            visited = 0
            while stack:
                with os.scandir(stack.pop()) as entries:
                    for entry in entries:
                        visited += 1
                        if visited % 128 == 0:
                            self.quick()
                        if entry.is_symlink():
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(Path(entry.path))
                        elif entry.is_file(follow_symlinks=False):
                            try:
                                total += entry.stat(follow_symlinks=False).st_size
                            except FileNotFoundError:
                                continue
                            if total > self.allocation['limits']['disk_bytes']:
                                raise OSError('workspace disk exceeds current allocation')
            self.disk_bytes = total
            self.last_disk_ns = time.monotonic_ns()
            self.quick()


def ancestor_costs(source):
    records = source['records']
    start = min(r['started_ns'] for r in records)
    end = max(r['finished_ns'] for r in records)
    attributed = sum(r['finished_ns'] - r['started_ns'] for r in records)
    return {
        'scope': 'Historical source setup only; never charged as current-allocation intervals. '
                 'Full source records, including failures, are retained verbatim. '
                 'Nested ancestor scopes, if present, remain separate rather than being summed twice.',
        'started_ns': start, 'finished_ns': end,
        'attributed_phase_ns': attributed, 'setup_span_ns': end - start,
        'unattributed_gap_ns': end - start - attributed,
        'recorded_bytes_acquired': sum(r['bytes_acquired'] for r in records),
        'terminal_counts': {status: sum(r['status'] == status for r in records)
                            for status in ('COMPLETED', 'FAILED', 'INTERRUPTED')},
        'allocation_identity': source.get('allocation'),
        'allocation_scope': 'Exact source allocation retained' if 'allocation' in source else
                            'Legacy schema 1 has no allocation object; no ID, closure proof '
                            'or complete allocation-wide wall total is invented.',
    }


def _adopt(args):
    root = require_workspace_root(args.allocation, args.source_setup, args.server, args.model, args.output)
    allocation_path = workspace_path(args.allocation, root)
    allocation = validate_allocation(read_json(allocation_path), active=True)
    output = workspace_path(args.output, root, existing=False, directory=True)
    # Guard the lease directory itself: heavy_job rejects a symlinked lock file.
    if (root / '.cache').exists() or (root / '.cache').is_symlink():
        workspace_path(root / '.cache', root, directory=True)
    with heavy_job(root):
        validate_allocation(allocation, active=True)
        output.mkdir(mode=0o700, exist_ok=False)
        journal = output / 'setup-events.jsonl'
        records = []
        budget = Budget(root, allocation)
        source = profile = ancestry = model_evidence = None
        source_raw = None
        source_sha = None
        server_sha = None
        input_stamps = {}

        def checked_path(path):
            result = workspace_path(path, root)
            input_stamps[result] = fingerprint(result)
            return result

        def stable_inputs():
            for path, before in input_stamps.items():
                workspace_path(path, root)
                if fingerprint(path) != before:
                    raise ContractError('adoption input changed during verification')

        def phase(name, fn, explanation):
            before = time.monotonic_ns()
            append_event(journal, {'event': 'STARTED', 'phase': name, 'observed_ns': before})
            error = None
            status = 'COMPLETED'
            try:
                budget(force_disk=True)
                fn()
                budget()
                stable_inputs()
            except BaseException as exc:
                status = 'INTERRUPTED' if isinstance(exc, KeyboardInterrupt) else 'FAILED'
                error = exc
            detail = {'operation': 'reuse-and-verification', 'newly_acquired_artifact_bytes': 0,
                      'explanation': explanation,
                      'ancestor_receipt_sha256': source_sha,
                      'ancestor_receipt_file': 'source-setup.json',
                      'cost_boundary': 'This interval measures current verification only. '
                                       'Historical acquisition/build/failure costs remain a separate ancestor scope.'}
            if name == 'source-acquisition' and ancestry is not None:
                # Runtime/export preserve setup records. Carry the exact source text
                # here as well as in the sidecar so ancestry cannot silently vanish.
                detail['ancestor'] = ancestry
            record = {'phase': name, 'status': status, 'started_ns': before,
                      'finished_ns': time.monotonic_ns(), 'bytes_acquired': 0,
                      'details': json.dumps(detail, sort_keys=True, separators=(',', ':'))}
            records.append(record)
            append_event(journal, {'event': 'TERMINAL', 'record': record})
            write_json_new(output / (name + '-receipt.json'), record)
            if error is not None:
                raise error

        def verify_source():
            nonlocal source, profile, source_raw, source_sha, ancestry
            source_path = checked_path(args.source_setup)
            if source_path.stat().st_size > MAX_RECEIPT_BYTES:
                raise ContractError('source setup receipt exceeds the bounded metadata size')
            with source_path.open('rb') as stream:
                source_raw = stream.read(MAX_RECEIPT_BYTES + 1)
            if len(source_raw) > MAX_RECEIPT_BYTES:
                raise ContractError('source setup receipt grew beyond the metadata size limit')
            source_sha = hashlib.sha256(source_raw).hexdigest()
            write_new(output / 'source-setup.json', source_raw)
            source = validate_receipt(parse_json(source_raw), boot_id=allocation['boot_id'])
            if max(r['finished_ns'] for r in source['records']) > allocation['started_ns']:
                raise ContractError('source setup must precede the current allocation; do not merge allocation scopes')
            if source.get('allocation', {}).get('allocation_id') == allocation['allocation_id']:
                raise ContractError('source and current allocation must have distinct identities')
            profile = get_model_profile(args.profile)
            artifacts = source['artifacts']
            if source['schema_version'] == 1:
                if (profile['profile_id'] not in (LEGACY_PROFILE['profile_id'],SMALL_PROFILE['profile_id']) or
                    len(profile['files']) != 1 or
                    artifacts['model_sha256'] != profile['files'][0]['sha256']):
                    raise ContractError('legacy source receipt admits only its exact reviewed 0.5B profile')
            elif (artifacts['model_profile_id'] != args.profile or
                  artifacts['model_profile_sha256'] != digest(profile)):
                raise ContractError('source receipt and requested model profile differ')
            patch = checked_path(root / 'patches' / BACKEND_PATCH_FILENAME)
            if file_digest(patch, check=budget) != BACKEND_PATCH_SHA256:
                raise ContractError('workspace reviewed backend patch differs from its pin')
            ancestry = {'schema_version': 1, 'source_receipt_sha256': source_sha,
                        'source_receipt_raw_utf8': source_raw.decode('utf-8'),
                        'source_receipt_path': str(source_path.relative_to(root)),
                        'historical_costs': ancestor_costs(source),
                        'source_revision': artifacts['backend_revision'],
                        'source_patch_sha256': artifacts['backend_patch_sha256'],
                        'attestation_boundary': 'Original receipt and pinned artifact bytes are verified; '
                                                'this operation does not rebuild, run git, certify an '
                                                'unchanged source checkout or authenticate the receipt author.'}
            write_json_new(output / 'ancestor-costs.json', ancestry)
            write_json_new(output / 'allocation.json', allocation)
            write_json_new(output / 'model-profile.json', profile)

        def verify_model():
            nonlocal model_evidence
            model = checked_path(args.model)
            for path in model_files(model, args.profile):
                checked_path(path)
            model_evidence = verify_model_files(model, args.profile, check=budget)
            write_json_new(output / 'model-verification.json', model_evidence)

        def verify_backend():
            nonlocal server_sha
            server = checked_path(args.server)
            if not os.access(server, os.X_OK):
                raise ContractError('prepared server is not executable by the current user')
            server_sha = file_digest(server, check=budget)
            if server_sha != source['artifacts']['server_sha256']:
                raise ContractError('prepared server SHA-256 differs from source receipt')
            write_json_new(output / 'backend-verification.json', {
                'backend_revision': BACKEND_COMMIT, 'backend_patch_sha256': BACKEND_PATCH_SHA256,
                'server_sha256': server_sha, 'server_bytes': server.stat().st_size,
                'operation': 'Existing prepared binary hash verification; no build or server invocation',
            })

        try:
            phase('source-acquisition', verify_source,
                  'Reuse and verify historical receipt, admitted profile and pinned source/patch identity; '
                  'no source acquisition. Exact ancestor bytes and all historical cost records retained.')
            phase('model-acquisition', verify_model,
                  'Reuse and stream-verify every already present reviewed model shard; no download or model copy.')
            phase('build', verify_backend,
                  'Reuse and verify exact already compiled server bytes against the ancestor; no build, '
                  'server execution or new backend qualification.')
            budget(force_disk=True)
            stable_inputs()
            receipt = {'schema_version': 2, 'boot_id': allocation['boot_id'], 'allocation': allocation,
                       'records': records,
                       'artifacts': {'backend_revision': BACKEND_COMMIT,
                                     'backend_patch_sha256': BACKEND_PATCH_SHA256,
                                     'server_sha256': server_sha, 'model_profile_id': args.profile,
                                     'model_profile_sha256': digest(profile)},
                       'resource_observations': {
                           'maximum_observed_aggregate_rss_bytes': budget.peak,
                           'scope': 'Sampled adoption coordinator RSS during bounded verification; '
                                    'no child processes. Not a continuous whole-allocation or host peak.'}}
            validate_receipt(receipt)
            write_json_new(output / 'adoption.json', {
                'schema_version': 1, 'operation': 'reuse-and-verification', 'status': 'VERIFICATION_COMPLETED',
                'current_allocation_id': allocation['allocation_id'],
                'source_receipt_sha256': source_sha, 'ancestor_costs_file': 'ancestor-costs.json',
                'source_receipt_file': 'source-setup.json', 'setup_receipt_sha256': digest(receipt),
                'artifact_paths': {'server': str(Path(args.server).absolute().relative_to(root)),
                                   'model': str(Path(args.model).absolute().relative_to(root))},
                'newly_acquired_artifact_bytes': 0,
                'current_verification_phase_ns': sum(r['finished_ns'] - r['started_ns'] for r in records),
                'workspace_bytes_last_observed': budget.disk_bytes,
                'cost_boundary': 'Verification consumes current allocation time/RSS/disk. '
                                 'Metadata output bytes are not downloaded/model/build artifact bytes. '
                                 'Ancestor source text and costs are also embedded in the first setup record '
                                 'so ordinary runtime/evidence exports retain historical scope. '
                                 'Historical costs are not zero and are not merged into current intervals. '
                                 'A valid setup.json is the final success marker; this manifest alone is insufficient.',
            })
            write_json_new(output / 'setup.json', receipt)
            print('Adopted verified existing profile; new setup.json retains separate ancestor costs. '
                  'No acquisition, build or inference performed.', flush=True)
            return 0
        except BaseException as exc:
            write_json_new(output / 'setup-failure.json', {
                'schema_version': 1, 'operation': 'reuse-and-verification',
                'status': 'INTERRUPTED' if isinstance(exc, KeyboardInterrupt) else 'FAILED',
                'allocation': allocation, 'requested_profile_id': args.profile,
                'source_receipt_sha256': source_sha, 'records': records,
                'error': type(exc).__name__ + ': ' + str(exc),
                'failed_observation_ns': time.monotonic_ns(),
                'maximum_observed_aggregate_rss_bytes': budget.peak,
                'cost_boundary': 'Partial current verification retained; no valid new setup receipt. '
                                 'Original source artifacts and historical costs are unchanged.'})
            print('Adoption failed; verification receipts retained: ' + str(exc), file=sys.stderr)
            return 2


def adopt(args):
    previous = {}
    def stop(signum, frame):
        raise KeyboardInterrupt('adoption cancelled by operator')
    for sig in (signal.SIGINT, signal.SIGTERM):
        previous[sig] = signal.signal(sig, stop)
    try:
        return _adopt(args)
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('allocation', 'source-setup', 'server', 'model', 'output'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--profile', required=True)
    try:
        return adopt(parser.parse_args())
    except (OSError, ValueError, RuntimeError) as exc:
        print('lean-model-lab adopt: ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
