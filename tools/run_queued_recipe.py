#!/usr/bin/env python3
"""Serialize finite native recipes without extending their original allocation.

This source-workspace convenience command invokes the exact supplied product
archive once. It neither edits a recipe nor retries a failed study.
"""
import argparse
import fcntl
import json
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from lean_model_lab.contracts import ContractError,read_json,file_digest
from lean_model_lab.artifacts import write_json_new
from lean_model_lab.recipes import validate_recipe
from lean_model_lab.allocation import validate_allocation


def execute(args):
    if Path.cwd().resolve()!=ROOT:raise ContractError('run from the supplied project workspace')
    output=args.output.resolve()
    if not output.is_relative_to(ROOT):raise ContractError('queued output must stay in this workspace')
    if output.exists():raise ContractError('queued output must be new')
    directory=output.with_name(output.name+'.queue')
    directory.mkdir(parents=True,exist_ok=False)
    recipe=validate_recipe(read_json(args.recipe));allocation=recipe['allocation']
    validate_allocation(allocation,active=True)
    deadline=allocation['deadline_ns'];started=time.monotonic_ns();child=None
    archive_sha=file_digest(args.archive)
    command=[sys.executable,'-I',str(args.archive.resolve()),'run','--recipe',str(args.recipe.resolve()),
        '--server',str(args.server.resolve()),'--model',str(args.model.resolve()),
        '--setup',str(args.setup.resolve()),'--output',str(output)]
    write_json_new(directory/'registration.json',{'started_ns':started,'deadline_ns':deadline,
        'archive_sha256':archive_sha,'recipe_file_sha256':file_digest(args.recipe),
        'scope':'Queued one-time product execution; same allocation, no automatic retries.'})
    def stop(sig,frame):
        if child is not None and child.poll() is None:child.send_signal(signal.SIGINT)
        raise KeyboardInterrupt('queued study cancelled')
    for sig in (signal.SIGINT,signal.SIGTERM):signal.signal(sig,stop)
    code=None;error=None;execution_started=None
    try:
        with (ROOT/'.cache/research-queue.lock').open('a+b') as queue:
            while True:
                if time.monotonic_ns()>=deadline:raise TimeoutError('original allocation exhausted while queued')
                try:
                    fcntl.flock(queue,fcntl.LOCK_EX|fcntl.LOCK_NB)
                    break
                except BlockingIOError:time.sleep(min(45,max(.001,(deadline-time.monotonic_ns())/1e9)))
            with (ROOT/'.cache/lean-model-lab-heavy.lock').open('a+b') as heavy:
                while True:
                    if time.monotonic_ns()>=deadline:raise TimeoutError('original allocation exhausted waiting for active backend')
                    try:
                        fcntl.flock(heavy,fcntl.LOCK_EX|fcntl.LOCK_NB)
                        fcntl.flock(heavy,fcntl.LOCK_UN)
                        break
                    except BlockingIOError:time.sleep(min(45,max(.001,(deadline-time.monotonic_ns())/1e9)))
            if file_digest(args.archive)!=archive_sha:raise ContractError('queued archive changed')
            execution_started=time.monotonic_ns()
            with (directory/'product.log').open('xb') as log:
                child=subprocess.Popen(command,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
                code=child.wait(timeout=max(.001,(deadline-time.monotonic_ns())/1e9))
    except BaseException as exc:
        error=type(exc).__name__+': '+str(exc)
    finally:
        if child is not None and child.poll() is None:
            child.send_signal(signal.SIGINT)
            try:child.wait(timeout=20)
            except subprocess.TimeoutExpired:child.kill();child.wait(timeout=5)
        receipt={'status':'COMPLETED' if code==0 and error is None else 'FAILED_OR_CANCELLED',
            'started_ns':started,'execution_started_ns':execution_started,'finished_ns':time.monotonic_ns(),
            'deadline_ns':deadline,'archive_sha256':archive_sha,'exit_code':code,'error':error,
            'scope':'Queue/process receipt; successful process exit alone does not establish quality or efficiency.'}
        write_json_new(directory/'receipt.json',receipt)
    print(json.dumps(receipt))
    return 0 if code==0 and error is None else 2


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('archive','recipe','server','model','setup','output'):
        parser.add_argument('--'+name,type=Path,required=True)
    raise SystemExit(execute(parser.parse_args()))
