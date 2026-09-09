"""Inert integration controls for the actual profile-preparation lifecycle.

Only the source-clone command argv is substituted. Real allocation validation,
the preparation signal wrapper, phase receipts, guardian and heavy-job lease run
in a project-local temporary fixture. Native executables and network operations
are rejected by the isolated harness; no retrieval, build or inference occurs.
"""
import contextlib
import fcntl
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from lean_model_lab.runner import _group_members
import test_process_guard as _inert

ROOT = Path(__file__).resolve().parents[1]

WRAPPER = r'''
import json, os, subprocess, sys, time
from pathlib import Path
from types import SimpleNamespace
repository = Path(sys.argv[1])
fixture = Path(sys.argv[2])
sys.path.insert(0, str(repository / 'src'))
sys.path.insert(0, str(repository / 'tools'))
import prepare_profile as prepare
from lean_model_lab.runner import _group_members

# The real project may currently have an admitted heavy job. This fixture uses
# the identical lease implementation under its own temporary project root.
prepare.ROOT = fixture
real_guard = prepare.start_guarded_process
real_stop = prepare.stop_owned_process
real_popen = subprocess.Popen
command = json.loads((fixture / 'inert-command.json').read_text())

def only_python(argv, *args, **kwargs):
    if not isinstance(argv, (list, tuple)) or not argv or argv[0] != sys.executable or kwargs.get('shell'):
        raise AssertionError('inert preparation control forbids native command execution')
    return real_popen(argv, *args, **kwargs)

def forbid(*args, **kwargs):
    raise AssertionError('inert preparation control forbids retrieval/build follow-up')

def guarded(argv, **kwargs):
    if argv[:4] != ['git', '-c', 'credential.helper=', 'clone']:
        raise AssertionError('unexpected preparation command; refusing execution')
    (fixture / 'requested-command.json').write_text(json.dumps(argv))
    process = real_guard(command, **kwargs)
    fields = Path('/proc/' + str(process.pid) + '/stat').read_text().rsplit(')', 1)[1].split()
    (fixture / 'guardian.json').write_text(json.dumps({'pid': process.pid, 'start_ticks': fields[19],
        'group': os.getpgid(process.pid), 'lease_fd_received': kwargs.get('lease_fd')}))
    return process

def stopped(process):
    (fixture / 'stop-started.json').write_text(json.dumps({'observed_ns': time.monotonic_ns(),
        'live_members': _group_members(process.pid)}))
    real_stop(process)
    (fixture / 'stop-finished.json').write_text(json.dumps({'observed_ns': time.monotonic_ns(),
        'live_members': _group_members(process.pid), 'returncode': process.returncode}))

subprocess.Popen = only_python
subprocess.check_output = forbid
prepare.urllib.request.build_opener = forbid
prepare.start_guarded_process = guarded
prepare.stop_owned_process = stopped
def audit(event, args):
    if event in ('socket.connect', 'socket.getaddrinfo'):
        raise AssertionError('network is forbidden in this inert control')
sys.addaudithook(audit)
args = SimpleNamespace(allocation=fixture / 'approved-inert-allocation.json',
    profile='qwen2.5-0.5b-instruct-fp16-v1', output=fixture / 'prepared')
raise SystemExit(prepare.prepare(args))
'''


@unittest.skipUnless(sys.platform == 'linux', 'Linux preparation lifecycle required')
class PrepareLifecycleTests(unittest.TestCase):
    def setUp(self):
        temporary_root = Path(os.environ.get('TMPDIR', ROOT / '.cache' / 'tmp')).resolve()
        if not temporary_root.is_relative_to(ROOT): temporary_root = ROOT / '.cache' / 'tmp'
        temporary_root.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix='prepare-lifecycle-', dir=temporary_root)
        self.root = Path(self.temporary.name)
        self.process = None
        self.records = []
        self.log = (self.root / 'coordinator.log').open('ab')
        started = time.monotonic_ns()
        self.allocation = {
            'schema_version': 2, 'allocation_id': 'inert-preparation-lifecycle', 'approved': True,
            'approval_reference': 'Owner-requested inert supervision test; no download, build or inference',
            'observed_utc': '2026-09-08',
            'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
            'started_ns': started, 'deadline_ns': started + 60 * 10**9,
            'limits': {'full_wall_seconds': 60, 'disk_bytes': 128 * 1024**2,
                       'memory_bytes': 2_000_000_000, 'compute_threads': 1, 'max_heavy_jobs': 1},
            'scope': 'Project TMP fixture and inert Python tree only; original allocation is unchanged',
        }
        (self.root / 'approved-inert-allocation.json').write_text(json.dumps(self.allocation))
        argv = [sys.executable, '-I', '-c', _inert.COMMAND, str(self.root / 'prepared'),
                _inert.GRANDCHILD, '1', '0']
        (self.root / 'inert-command.json').write_text(json.dumps(argv))

    def tearDown(self):
        if self.process is not None:
            if self.process.poll() is None:
                self.process.terminate()
                try: self.process.wait(timeout=5)
                except subprocess.TimeoutExpired: self.process.kill()
            self.process.wait(timeout=5)
        # The shared inert fixtures also self-exit within fifteen seconds. Never
        # signal an orphan by an unpinned numeric PID in a failed test cleanup.
        deadline = time.monotonic() + 16
        while any(self.running(r) for r in self.records) and time.monotonic() < deadline:
            time.sleep(.02)
        live = [r['pid'] for r in self.records if self.running(r)]
        self.log.close()
        self.temporary.cleanup()
        self.assertEqual(live, [], 'inert descendants exceeded their bounded lifetimes')

    @staticmethod
    def running(record):
        return _inert.ProcessGuardTests.running(record)

    def wait_for(self, predicate, timeout=7):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            result = predicate()
            if result: return result
            time.sleep(.01)
        diagnostic = (self.root / 'coordinator.log').read_text()
        self.fail('preparation observation timed out: ' + diagnostic)

    def read_when_ready(self, relative):
        def read():
            try: return json.loads((self.root / relative).read_text())
            except (FileNotFoundError, ValueError): return None
        return self.wait_for(read)

    def lease_available(self):
        with (self.root / '.cache' / 'lean-model-lab-heavy.lock').open('r+b') as lease:
            try: fcntl.flock(lease.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError: return False
        return True

    def launch(self):
        self.process = subprocess.Popen([sys.executable, '-I', '-c', WRAPPER, str(ROOT), str(self.root)],
            cwd=self.root, env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'TMPDIR': str(self.root)},
            stdin=subprocess.DEVNULL, stdout=self.log, stderr=subprocess.STDOUT, start_new_session=True)
        guardian = self.read_when_ready('guardian.json')
        command = self.read_when_ready('prepared/command-ready.json')
        grandchild = self.read_when_ready('prepared/grandchild.json')
        self.records = [guardian, command, grandchild]
        self.assertIsInstance(guardian['lease_fd_received'], int)
        self.assertGreaterEqual(guardian['lease_fd_received'], 3)
        for record in self.records:
            self.assertTrue(self.running(record))
            self.assertEqual(record['group'], guardian['pid'])
        self.assertFalse(self.lease_available())
        events = [json.loads(line) for line in (self.root / 'prepared/setup-events.jsonl').read_text().splitlines()]
        self.assertEqual(len(events), 1)
        self.assertEqual((events[0]['phase'], events[0]['event']), ('source-acquisition', 'STARTED'))
        return guardian, command, grandchild

    def test_sigterm_preserves_interrupted_phase_and_releases_lease_after_cleanup(self):
        guardian, command, grandchild = self.launch()
        self.process.send_signal(signal.SIGTERM)
        self.read_when_ready('stop-started.json')
        self.assertTrue(self.running(grandchild))  # Its ignored TERM exercises the cleanup interval.
        self.assertFalse(self.lease_available())
        self.assertEqual(self.process.wait(timeout=7), 2)
        self.wait_for(lambda: all(not self.running(r) for r in self.records))
        self.assertEqual(_group_members(guardian['pid']), [])
        cleanup = self.read_when_ready('stop-finished.json')
        receipt = self.read_when_ready('prepared/source-acquisition-receipt.json')
        failure = self.read_when_ready('prepared/setup-failure.json')
        self.assertEqual(cleanup['live_members'], [])
        self.assertEqual(cleanup['returncode'], -signal.SIGKILL)
        self.assertEqual(receipt['status'], 'INTERRUPTED')
        self.assertEqual(receipt['phase'], 'source-acquisition')
        self.assertGreater(receipt['finished_ns'], receipt['started_ns'])
        self.assertGreaterEqual(receipt['finished_ns'], cleanup['observed_ns'])
        self.assertGreaterEqual(failure['failed_observation_ns'], receipt['finished_ns'])
        self.assertEqual(failure['records'], [receipt])
        self.assertEqual(failure['allocation'], self.allocation)
        self.assertTrue(failure['error'].startswith('KeyboardInterrupt:'))
        self.assertTrue(self.lease_available())
        events = [json.loads(line) for line in (self.root / 'prepared/setup-events.jsonl').read_text().splitlines()]
        self.assertEqual([event['event'] for event in events], ['STARTED', 'TERMINAL'])
        self.assertEqual(events[-1]['record'], receipt)
        self.assertFalse((self.root / 'prepared/setup.json').exists())
        self.assertFalse((self.root / 'prepared/model-acquisition-receipt.json').exists())
        self.assertFalse((self.root / 'prepared/llama.cpp').exists())

    def test_sigkill_retains_started_evidence_and_guardian_holds_lease_through_cleanup(self):
        guardian, command, grandchild = self.launch()
        self.process.kill()
        self.assertEqual(self.process.wait(timeout=5), -signal.SIGKILL)
        self.assertTrue(self.running(grandchild))
        self.assertFalse(self.lease_available())
        self.wait_for(lambda: all(not self.running(r) for r in self.records))
        self.assertEqual(_group_members(guardian['pid']), [])
        self.assertTrue(self.lease_available())
        self.assertFalse((self.root / 'prepared/setup-failure.json').exists())
        self.assertFalse((self.root / 'prepared/source-acquisition-receipt.json').exists())
        self.assertFalse((self.root / 'prepared/setup.json').exists())
        events = [json.loads(line) for line in (self.root / 'prepared/setup-events.jsonl').read_text().splitlines()]
        self.assertEqual([event['event'] for event in events], ['STARTED'])
        self.assertIn('grace expired; SIGKILL', (self.root / 'prepared/source-clone.log').read_text())


if __name__ == '__main__':
    unittest.main()
