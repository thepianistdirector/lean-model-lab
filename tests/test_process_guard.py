"""Real inert process trees exercise Linux preparation supervision.

No compilation, model, network or external package is involved. All test files
live under the project's TMPDIR. Cleanup uses owned Popen handles and pidfds
where supported; inert descendants also have finite lifetimes on older kernels.
"""
import contextlib
import errno
import fcntl
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest
import zipfile
from pathlib import Path

from lean_model_lab import process_guard
from lean_model_lab.process_guard import start_guarded_process
from lean_model_lab.runner import _group_members, stop_owned_process
from lean_model_lab.resources import heavy_job

ROOT = Path(__file__).resolve().parents[1]

GRANDCHILD = r'''
import json, os, signal, sys, time
from pathlib import Path
if sys.argv[2] == '1':
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
fields = Path('/proc/self/stat').read_text().rsplit(')', 1)[1].split()
Path(sys.argv[1], 'grandchild.json').write_text(json.dumps(
    {'pid': os.getpid(), 'start_ticks': fields[19], 'group': os.getpgrp()}))
deadline = time.monotonic() + 15
while time.monotonic() < deadline:
    time.sleep(.05)
'''

COMMAND = r'''
import json, os, subprocess, sys, time
from pathlib import Path
root = Path(sys.argv[1])
child = subprocess.Popen([sys.executable, '-I', '-c', sys.argv[2], str(root), sys.argv[3]])
while not (root / 'grandchild.json').exists():
    time.sleep(.005)
fields = Path('/proc/self/stat').read_text().rsplit(')', 1)[1].split()
(root / 'command-ready.json').write_text(json.dumps(
    {'pid': os.getpid(), 'start_ticks': fields[19], 'group': os.getpgrp()}))
if sys.argv[4] == '1':
    raise SystemExit(17)
deadline = time.monotonic() + 15
while time.monotonic() < deadline:
    time.sleep(.05)
'''

COORDINATOR = r'''
import json, os, subprocess, sys
from contextlib import nullcontext
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from lean_model_lab.process_guard import start_guarded_process
from lean_model_lab.resources import heavy_job
root = Path(sys.argv[2])
argv = json.loads((root / 'command-argv.json').read_text())
lease_mode = sys.argv[3]
with (heavy_job(root) if lease_mode != 'none' else nullcontext(None)) as lease_fd:
    guard = start_guarded_process(argv, cwd=root, env=None, stdin=subprocess.DEVNULL,
                                   stdout=None, stderr=None,
                                   lease_fd=lease_fd if lease_mode == 'inherit' else None)
    fields = Path('/proc/' + str(guard.pid) + '/stat').read_text().rsplit(')', 1)[1].split()
    (root / 'guardian.json').write_text(json.dumps(
        {'pid': guard.pid, 'start_ticks': fields[19], 'group': os.getpgid(guard.pid)}))
    code = guard.wait()
raise SystemExit(code if code >= 0 else 128 - code)
'''


@unittest.skipUnless(sys.platform == 'linux', 'Linux procfs/prctl controls required')
class ProcessGuardTests(unittest.TestCase):
    def setUp(self):
        temporary_root = Path(os.environ.get('TMPDIR', ROOT / '.cache' / 'tmp')).resolve()
        if not temporary_root.is_relative_to(ROOT):
            temporary_root = ROOT / '.cache' / 'tmp'
        temporary_root.mkdir(parents=True, exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(prefix='process-guard-', dir=temporary_root)
        self.root = Path(self.temporary.name)
        self.env = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'TMPDIR': str(self.root)}
        self.handles = []
        self.pidfds = []
        self.records = []
        self.logs = []

    def tearDown(self):
        # Kill only identity-bound handles. Guardian termination requests normal
        # tree cleanup first; pidfds provide a safe last resort for test failure.
        for process in self.handles:
            if process.poll() is None:
                process.terminate()
        deadline = time.monotonic() + 3
        for process in self.handles:
            with contextlib.suppress(subprocess.TimeoutExpired):
                process.wait(timeout=max(.01, deadline - time.monotonic()))
        for fd in self.pidfds:
            with contextlib.suppress(ProcessLookupError):
                signal.pidfd_send_signal(fd, signal.SIGKILL)
            os.close(fd)
        for process in self.handles:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=5)
            for stream in (process.stdin, process.stdout, process.stderr):
                if stream is not None:
                    stream.close()
        # On older kernels pidfd_open can be exposed by Python but return
        # ENOSYS. Do not fall back to signaling a possibly reused numeric PID.
        # Reviewed inert descendants self-exit within fifteen seconds even if
        # the very guardian under test is broken.
        deadline = time.monotonic() + 16
        while any(self.running(record) for record in self.records) and time.monotonic() < deadline:
            time.sleep(.02)
        self.assertFalse(any(self.running(record) for record in self.records),
                         'an inert test descendant exceeded its bounded lifetime')
        for stream in self.logs:
            stream.close()
        self.temporary.cleanup()

    def wait_for(self, predicate, *, timeout=6):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            result = predicate()
            if result:
                return result
            time.sleep(.01)
        self.fail('process supervision observation timed out')

    def record(self, filename):
        def read():
            try:
                return json.loads((self.root / filename).read_text())
            except (FileNotFoundError, ValueError):
                return None
        record = self.wait_for(read)
        self.records.append(record)
        if not hasattr(os, 'pidfd_open') or not hasattr(signal, 'pidfd_send_signal'):
            return record
        try:
            fd = os.pidfd_open(record['pid'])
        except ProcessLookupError:
            return record
        except OSError as exc:
            if exc.errno in (errno.ENOSYS, errno.EPERM):
                return record
            raise
        # Check the receipt before retaining the pidfd, since command exit may
        # have raced receipt loading. An unrelated reused PID is never killed.
        if self.running(record):
            self.pidfds.append(fd)
        else:
            os.close(fd)
        return record

    @staticmethod
    def running(record):
        try:
            fields = Path(f"/proc/{record['pid']}/stat").read_text().rsplit(')', 1)[1].split()
        except FileNotFoundError:
            return False
        return fields[19] == record['start_ticks'] and fields[0] not in ('Z', 'X')

    def tree_argv(self, *, stubborn=False, command_exits=False):
        return [sys.executable, '-I', '-c', COMMAND, str(self.root), GRANDCHILD,
                '1' if stubborn else '0', '1' if command_exits else '0']

    def log(self):
        stream = (self.root / 'shared.log').open('ab')
        self.logs.append(stream)
        return stream

    def launch_guard(self, argv, *, pipe=False):
        process = start_guarded_process(argv, cwd=self.root, env=self.env,
            stdin=subprocess.PIPE if pipe else subprocess.DEVNULL,
            stdout=subprocess.PIPE if pipe else self.log(), stderr=subprocess.PIPE if pipe else subprocess.STDOUT)
        self.handles.append(process)
        return process

    def launch_coordinator(self, *, stubborn=False, lease_mode='none'):
        (self.root / 'command-argv.json').write_text(json.dumps(self.tree_argv(stubborn=stubborn)))
        process = subprocess.Popen([sys.executable, '-I', '-c', COORDINATOR,
            str(ROOT / 'src'), str(self.root), lease_mode], cwd=self.root, env=self.env,
            stdin=subprocess.DEVNULL, stdout=self.log(), stderr=subprocess.STDOUT, start_new_session=True)
        self.handles.append(process)
        guardian = self.record('guardian.json')
        command = self.record('command-ready.json')
        grandchild = self.record('grandchild.json')
        for record in (guardian, command, grandchild):
            self.assertEqual(record['group'], guardian['pid'])
            self.assertTrue(self.running(record))
        return process, guardian, command, grandchild

    def lease_available(self):
        with (self.root / '.cache' / 'lean-model-lab-heavy.lock').open('r+b') as lease:
            try:
                fcntl.flock(lease.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return False
        return True

    def test_normal_exit_and_shared_standard_streams(self):
        process = self.launch_guard([sys.executable, '-I', '-c',
            "import sys; print('command:' + sys.stdin.read(), flush=True); print('diagnostic', file=sys.stderr); sys.exit(23)"], pipe=True)
        output, error = process.communicate(b'input', timeout=5)
        self.assertEqual(process.returncode, 23)
        self.assertEqual(output, b'command:input\n')
        self.assertEqual(error, b'diagnostic\n')
        self.assertEqual(_group_members(process.pid), [])

    def test_normal_command_signal_is_preserved(self):
        process = self.launch_guard([sys.executable, '-I', '-c',
            'import os,signal; os.kill(os.getpid(),signal.SIGTERM)'])
        self.assertEqual(process.wait(timeout=5), -signal.SIGTERM)
        self.assertEqual(_group_members(process.pid), [])

    def test_normal_command_exit_does_not_leave_an_orphan_grandchild(self):
        process = self.launch_guard(self.tree_argv(command_exits=True))
        grandchild = self.record('grandchild.json')
        self.assertEqual(process.wait(timeout=5), 17)
        self.wait_for(lambda: not self.running(grandchild))
        self.assertEqual(_group_members(process.pid), [])
        self.assertIn('command exited with descendants', (self.root / 'shared.log').read_text())

    def test_sigterm_coordinator_stops_command_and_grandchild(self):
        coordinator, guardian, command, grandchild = self.launch_coordinator()
        coordinator.send_signal(signal.SIGTERM)
        self.assertEqual(coordinator.wait(timeout=5), -signal.SIGTERM)
        self.wait_for(lambda: all(not self.running(r) for r in (guardian, command, grandchild)))
        self.assertEqual(_group_members(guardian['pid']), [])
        self.assertIn('parent death', (self.root / 'shared.log').read_text())

    def test_sigkill_coordinator_still_stops_command_and_grandchild(self):
        coordinator, guardian, command, grandchild = self.launch_coordinator()
        coordinator.kill()
        self.assertEqual(coordinator.wait(timeout=5), -signal.SIGKILL)
        self.wait_for(lambda: all(not self.running(r) for r in (guardian, command, grandchild)))
        self.assertEqual(_group_members(guardian['pid']), [])

    def test_parent_death_escalates_stubborn_grandchild(self):
        coordinator, guardian, command, grandchild = self.launch_coordinator(stubborn=True)
        started = time.monotonic()
        coordinator.kill(); coordinator.wait(timeout=5)
        self.wait_for(lambda: all(not self.running(r) for r in (guardian, command, grandchild)))
        self.assertLess(time.monotonic() - started, 4)
        self.assertEqual(_group_members(guardian['pid']), [])
        self.assertIn('grace expired; SIGKILL', (self.root / 'shared.log').read_text())

    def test_negative_control_detects_uninherited_lease_gap(self):
        coordinator, guardian, command, grandchild = self.launch_coordinator(
            stubborn=True, lease_mode='omit')
        self.assertFalse(self.lease_available())
        coordinator.kill(); coordinator.wait(timeout=5)
        self.assertTrue(self.running(grandchild))
        self.assertTrue(self.lease_available())
        self.wait_for(lambda: all(not self.running(r) for r in (guardian, command, grandchild)))

    def test_inherited_lease_survives_coordinator_sigkill_until_cleanup(self):
        coordinator, guardian, command, grandchild = self.launch_coordinator(
            stubborn=True, lease_mode='inherit')
        self.assertFalse(self.lease_available())
        coordinator.kill(); coordinator.wait(timeout=5)
        self.assertTrue(self.running(grandchild))
        self.assertFalse(self.lease_available())
        self.wait_for(lambda: all(not self.running(r) for r in (guardian, command, grandchild)))
        self.assertTrue(self.lease_available())

    def test_actual_command_does_not_inherit_the_guardians_lease(self):
        with heavy_job(self.root) as lease_fd:
            lease_identity = os.fstat(lease_fd)
            code = (
                'import os,sys\n'
                'try:\n'
                ' s=os.fstat(int(sys.argv[1]))\n'
                'except OSError:\n'
                ' raise SystemExit(0)\n'
                'raise SystemExit(21 if (s.st_dev,s.st_ino)==(int(sys.argv[2]),int(sys.argv[3])) else 0)\n'
            )
            process = start_guarded_process([sys.executable, '-I', '-c', code, str(lease_fd),
                str(lease_identity.st_dev), str(lease_identity.st_ino)], cwd=self.root, env=self.env,
                stdin=subprocess.DEVNULL, stdout=self.log(), stderr=subprocess.STDOUT, lease_fd=lease_fd)
            self.handles.append(process)
            self.assertEqual(process.wait(timeout=5), 0)

    def test_direct_cancellation_has_explicit_signal_status(self):
        process = self.launch_guard(self.tree_argv(stubborn=True))
        grandchild = self.record('grandchild.json')
        self.record('command-ready.json')
        process.send_signal(signal.SIGTERM)
        self.assertEqual(process.wait(timeout=5), -signal.SIGKILL)
        self.wait_for(lambda: not self.running(grandchild))

    def test_legacy_stop_owned_process_keeps_unrelated_group_alive(self):
        unrelated = subprocess.Popen([sys.executable, '-I', '-c', 'import time; time.sleep(30)'],
                                      stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                                      stderr=subprocess.DEVNULL, start_new_session=True)
        self.handles.append(unrelated)
        process = self.launch_guard(self.tree_argv())
        command = self.record('command-ready.json')
        grandchild = self.record('grandchild.json')
        self.assertEqual(os.getsid(process.pid), process.pid)
        self.assertEqual(os.getpgid(process.pid), process.pid)
        self.assertIn(command['pid'], _group_members(process.pid))
        self.assertIn(grandchild['pid'], _group_members(process.pid))
        stop_owned_process(process)
        self.assertEqual(process.returncode, -signal.SIGTERM)
        self.assertEqual(_group_members(process.pid), [])
        self.assertIsNone(unrelated.poll())
        stop_owned_process(process)  # Existing caller idempotence is preserved.

    def test_parent_identity_race_refuses_command_before_launch(self):
        marker = self.root / 'must-not-run'
        process = subprocess.Popen([sys.executable, '-I', '-c', process_guard._SUPERVISOR_SOURCE,
            '1', '0', sys.executable, '-I', '-c',
            'from pathlib import Path; Path(' + repr(str(marker)) + ').write_text("ran")'],
            cwd=self.root, env=self.env, stdin=subprocess.DEVNULL, stdout=self.log(),
            stderr=subprocess.STDOUT, start_new_session=True)
        self.handles.append(process)
        self.assertEqual(process.wait(timeout=5), -signal.SIGTERM)
        self.assertFalse(marker.exists())

    def test_launcher_works_from_isolated_zipapp(self):
        archive = self.root / 'guard-test.pyz'
        main = (
            'import subprocess,sys\n'
            'from lean_model_lab.process_guard import start_guarded_process\n'
            'p=start_guarded_process([sys.executable,"-I","-c","print(42);raise SystemExit(19)"],'
            'cwd=".",env=None,stdin=subprocess.DEVNULL,stdout=None,stderr=None)\n'
            'raise SystemExit(p.wait())\n'
        )
        with zipfile.ZipFile(archive, 'w') as bundle:
            bundle.writestr('__main__.py', main)
            bundle.writestr('lean_model_lab/__init__.py', '')
            bundle.writestr('lean_model_lab/process_guard.py', Path(process_guard.__file__).read_bytes())
        process = subprocess.Popen([sys.executable, '-I', str(archive)], cwd=self.root, env=self.env,
                                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.handles.append(process)
        output, error = process.communicate(timeout=5)
        self.assertEqual(process.returncode, 19, error)
        self.assertEqual(output, b'42\n')


if __name__ == '__main__':
    unittest.main()
