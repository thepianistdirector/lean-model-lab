"""Project-scoped single-heavy-job lease. No shared host configuration is changed."""
from contextlib import contextmanager
from contextvars import ContextVar
import fcntl
from pathlib import Path


_ACTIVE_LEASE=ContextVar('lean_model_lab_heavy_lease_fd',default=None)


def active_heavy_lease_fd():
    return _ACTIVE_LEASE.get()


def heavy_lease_fds():
    fd=active_heavy_lease_fd()
    return () if fd is None else (fd,)


@contextmanager
def heavy_job(project_root: Path):
    cache=project_root.resolve()/'.cache'
    cache.mkdir(parents=True,exist_ok=True)
    lock=cache/'lean-model-lab-heavy.lock'
    if lock.is_symlink():raise ValueError('heavy-job lock must not be a symlink')
    with lock.open('a+b') as handle:
        try:fcntl.flock(handle.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError('another Lean Model Lab acquisition/build/study holds the heavy-job lease') from exc
        token=_ACTIVE_LEASE.set(handle.fileno())
        try:yield handle.fileno()
        finally:
            _ACTIVE_LEASE.reset(token)
            # Closing, rather than LOCK_UN, keeps an inherited guardian/server
            # descriptor authoritative until the last owned process exits.


def require_workspace_root(*paths: Path) -> Path:
    """Use the supplied source workspace for one lease and full disk accounting."""
    import json
    from .contracts import ContractError
    cwd=Path.cwd().resolve()
    roots=[]
    for candidate in (cwd,*cwd.parents):
        marker=candidate/'WORKSPACE.json'
        if marker.is_file():
            if marker.is_symlink():raise ContractError('workspace marker must not be symlinked')
            try: value=json.loads(marker.read_text())
            except (OSError,ValueError) as exc:raise ContractError('invalid workspace marker') from exc
            if value=={'project':'lean-model-lab','schema_version':1}:roots.append(candidate)
    if not roots:raise ContractError('run/resume require the supplied source workspace root containing WORKSPACE.json')
    root=roots[-1]
    if cwd!=root:raise ContractError('run/resume must start at the outermost Lean Model Lab workspace root; nested working directories are refused')
    for path in paths:
        if not path.resolve().is_relative_to(root):raise ContractError('study and inference artifacts must remain within the same workspace disk/lease scope')
    return root
