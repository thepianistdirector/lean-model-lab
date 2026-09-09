"""Linux supervision for reviewed preparation commands and their process group.

The returned Popen owns a fresh session/group whose leader remains alive until
the command and its descendants finish or are stopped. Parent death requests
the same cleanup as explicit cancellation. This is a lifecycle guard, not a
sandbox for commands that deliberately escape their process group.

The supervisor is embedded Python source passed directly to this interpreter.
It needs neither a temporary script nor an importable filesystem module, so the
same launcher works when this module is loaded from a packaged zipapp.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


_SUPERVISOR_SOURCE = r'''
import ctypes
import os
import signal
import subprocess
import sys
import time

GRACE_SECONDS = 1.0
POLL_SECONDS = 0.02
PR_SET_PDEATHSIG = 1
PR_SET_CHILD_SUBREAPER = 36
group = os.getpgrp()
own_pid = os.getpid()
requested_signal = None


def note(message):
    try:
        os.write(2, ('[process_guard] ' + message + '\n').encode('utf-8'))
    except OSError:
        pass


def on_signal(signum, frame):
    global requested_signal
    if requested_signal is None:
        requested_signal = signum


def process_fields(pid):
    try:
        with open('/proc/' + str(pid) + '/stat', 'r') as stream:
            return stream.read().rsplit(')', 1)[1].split()
    except (OSError, IndexError):
        return None


def live_group_members():
    result = []
    # The leader is still this process; this numeric PGID cannot be reused by
    # a foreign session during inspection or either group signal.
    with os.scandir('/proc') as entries:
        for entry in entries:
            if not entry.name.isdecimal() or int(entry.name) == own_pid:
                continue
            fields = process_fields(entry.name)
            if fields and int(fields[2]) == group and fields[0] not in ('Z', 'X'):
                result.append(int(entry.name))
    return result


def children_remain():
    # Called only after normal command status has been captured, or during
    # cancellation when the supervising signal is the reported exit reason.
    # Subreaping prevents an orphan/fork race from looking like an empty group
    # merely because /proc enumeration missed a newly reparented grandchild.
    while True:
        try:
            pid, status = os.waitpid(-1, os.WNOHANG)
        except ChildProcessError:
            return False
        if pid == 0:
            return True


def stop_group():
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    os.killpg(group, signal.SIGTERM)
    # The ignored broadcast is discarded; subsequent external cancellation
    # still records its signal while this bounded cleanup continues.
    signal.signal(signal.SIGTERM, on_signal)
    deadline = time.monotonic() + GRACE_SECONDS
    while children_remain() or live_group_members():
        if time.monotonic() >= deadline:
            note('grace expired; SIGKILL for the owned process group')
            # Includes this supervisor. A -SIGKILL return code explicitly
            # records escalation; no foreign numeric PID is selected.
            os.killpg(group, signal.SIGKILL)
            os._exit(128 + signal.SIGKILL)
        time.sleep(POLL_SECONDS)


def finish(code):
    if code < 0:
        signum = -code
        if signum not in (signal.SIGKILL, signal.SIGSTOP):
            signal.signal(signum, signal.SIG_DFL)
        os.kill(own_pid, signum)
        os._exit(128 + signum)
    os._exit(code)


def main():
    global requested_signal
    if group != own_pid or os.getsid(0) != own_pid:
        note('refusing to launch outside a fresh owned session/group')
        return 125
    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)
    try:
        parent_pid = int(sys.argv[1])
        parent_start_ticks = sys.argv[2]
        command_argv = sys.argv[3:]
        if parent_pid <= 0 or not parent_start_ticks.isdecimal() or not command_argv:
            raise ValueError('invalid supervisor arguments')
        libc = ctypes.CDLL(None, use_errno=True)
        if libc.prctl(PR_SET_PDEATHSIG, signal.SIGTERM, 0, 0, 0) != 0:
            raise OSError(ctypes.get_errno(), 'cannot install parent-death signal')
        if libc.prctl(PR_SET_CHILD_SUBREAPER, 1, 0, 0, 0) != 0:
            raise OSError(ctypes.get_errno(), 'cannot establish local descendant reaping')
        fields = process_fields(parent_pid)
        if os.getppid() != parent_pid or fields is None or fields[19] != parent_start_ticks:
            requested_signal = requested_signal or signal.SIGTERM
        if requested_signal is not None:
            note('parent changed before launch; command not started')
            stop_group()
            finish(-requested_signal)
        # Inherit this supervisor's descriptors and process group. Do not call
        # setsid/start_new_session or pass a new environment to the command.
        command = subprocess.Popen(command_argv, close_fds=True)
        while True:
            code = command.poll()
            if requested_signal is not None:
                note('cancellation or parent death; stopping owned process group')
                stop_group()
                finish(-requested_signal)
            if code is not None:
                if children_remain() or live_group_members():
                    note('command exited with descendants; stopping owned process group')
                    stop_group()
                # A signal can arrive during descendant cleanup. Preserve
                # explicit cancellation instead of reporting an unrelated 0.
                finish(-requested_signal if requested_signal is not None else code)
            time.sleep(POLL_SECONDS)
    except BaseException as exc:
        note('supervisor failure: ' + type(exc).__name__)
        # Any exceptional path after command creation must still stop the
        # owned group. If cleanup itself fails, the group is killed together.
        try:
            stop_group()
        except BaseException:
            os.killpg(group, signal.SIGKILL)
        return 125


finish(main())
'''


def start_guarded_process(argv, *, cwd, env, stdin, stdout, stderr,
                          lease_fd: int | None = None) -> subprocess.Popen:
    """Launch reviewed argv with cancellation and coordinator-death cleanup.

Normal command exit codes (including signal termination) are preserved after
descendants are gone. Cancellation normally returns the negative signal; forced
group cleanup returns -SIGKILL. The returned handle supports poll/wait/communicate
    and the existing stop_owned_process/group_rss helpers. The caller must keep
    commands in this group; deliberate daemonization is outside the reviewed scope.
    An optional open flock descriptor is retained by the supervisor until cleanup;
    the actual command receives no copy. Its owner must close, rather than explicitly
    unlock, its copy so coordinator death cannot release the shared lease early.
    """
    if sys.platform != 'linux':
        raise RuntimeError('guarded preparation requires Linux parent-death supervision')
    if type(argv) not in (list, tuple) or not argv:
        raise ValueError('argv must be a nonempty argument sequence, not shell text')
    arguments = [os.fspath(value) for value in argv]
    if any(type(value) is not str or '\x00' in value for value in arguments):
        raise ValueError('guarded argv requires text arguments without NUL bytes')
    if lease_fd is not None:
        if type(lease_fd) is not int or lease_fd < 3:
            raise ValueError('lease_fd must be an open descriptor distinct from standard streams')
        os.fstat(lease_fd)  # Reject a closed descriptor before starting any process.
    parent_pid = os.getpid()
    fields = Path(f'/proc/{parent_pid}/stat').read_text().rsplit(')', 1)[1].split()
    parent_start_ticks = fields[19]
    return subprocess.Popen(
        [sys.executable, '-I', '-c', _SUPERVISOR_SOURCE, str(parent_pid), parent_start_ticks, *arguments],
        cwd=cwd, env=env, stdin=stdin, stdout=stdout, stderr=stderr,
        start_new_session=True, close_fds=True, pass_fds=() if lease_fd is None else (lease_fd,),
    )
