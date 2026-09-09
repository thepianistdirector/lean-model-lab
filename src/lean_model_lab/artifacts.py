"""Exclusive immutable files and durable append-only attempt journals."""
from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any

from .contracts import canonical_bytes, parse_json


def write_new(path: Path, data: bytes) -> None:
    """Publish complete bytes without replacing an existing artifact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.parent / ('.'+path.name+'.'+uuid.uuid4().hex+'.partial')
    try:
        with temporary.open('xb') as output:
            output.write(data); output.flush(); os.fsync(output.fileno())
        os.link(temporary, path)  # Atomic no-clobber publication on same filesystem.
        directory = os.open(path.parent, os.O_RDONLY)
        try: os.fsync(directory)
        finally: os.close(directory)
    finally:
        temporary.unlink(missing_ok=True)


def write_json_new(path: Path, value: Any) -> None:
    write_new(path, canonical_bytes(value)+b'\n')


def append_event(path: Path, value: dict) -> None:
    """One coordinator owns each journal; readers tolerate only a torn final line."""
    with path.open('ab') as output:
        output.write(canonical_bytes(value)+b'\n'); output.flush(); os.fsync(output.fileno())


def read_journal(path: Path) -> tuple[list[dict], bool]:
    raw = path.read_bytes()
    lines = raw.splitlines(keepends=True)
    torn = bool(lines and not lines[-1].endswith(b'\n'))
    if torn: lines.pop()
    values = [parse_json(line) for line in lines]
    if any(not isinstance(value, dict) for value in values):
        raise ValueError('journal records must be objects')
    return values, torn
