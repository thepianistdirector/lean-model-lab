#!/usr/bin/env python3
"""Retain one actual product/helper invocation without adding scientific behavior."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

PROJECT = Path(__file__).resolve().parents[3]
OWN = Path(__file__).resolve().parent


def record(label, command, timeout=120):
    if not label or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-_' for c in label):
        raise ValueError('unsafe command label')
    directory = OWN / 'commands'
    directory.mkdir(exist_ok=True)
    record_path = directory / (label + '.json')
    if record_path.exists():
        raise ValueError('command receipt already exists')
    started = time.monotonic_ns()
    with (directory / (label + '.stdout')).open('xb') as stdout, (directory / (label + '.stderr')).open('xb') as stderr:
        result = subprocess.run(command, cwd=PROJECT, stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, timeout=timeout)
    receipt = {'label': label, 'command': command, 'started_ns': started,
               'finished_ns': time.monotonic_ns(), 'exit_code': result.returncode,
               'scope': 'Command receipt only; no assertion of quality or scientific eligibility.'}
    for name in ('stdout', 'stderr'):
        data = (directory / (label + '.' + name)).read_bytes()
        receipt[name] = {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}
    with record_path.open('x') as stream:
        stream.write(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
    print(json.dumps(receipt))
    return result.returncode


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('label')
    parser.add_argument('--timeout', type=int, default=120)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    raise SystemExit(record(args.label, command, args.timeout))
