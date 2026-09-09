#!/usr/bin/env python3
"""Prepare the admitted sharded model and pinned CPU backend under one allocation."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from lean_model_lab.allocation import validate_allocation
from lean_model_lab.artifacts import append_event,write_json_new
from lean_model_lab.contracts import ContractError,digest,file_digest,read_json
from lean_model_lab.llama_adapter import BACKEND_COMMIT,BACKEND_PATCH_FILENAME,BACKEND_PATCH_SHA256
from lean_model_lab.profiles import get_model_profile
from lean_model_lab.resources import heavy_job
from lean_model_lab.process_guard import start_guarded_process
from lean_model_lab.resources import active_heavy_lease_fd
from lean_model_lab.runner import directory_bytes,stop_owned_process,_rss
from prepare_backend import native_build_options,ReviewedRedirect,reviewed_model_url,group_rss


def _prepare(args):
    allocation=validate_allocation(read_json(args.allocation),active=True)
    profile=get_model_profile(args.profile)
    limits=allocation['limits'];deadline=allocation['deadline_ns']
    if sum(a['bytes'] for a in profile['files'])>=limits['memory_bytes']:
        raise ContractError('model weights leave no admitted resident-memory allowance')
    output=args.output.resolve()
    if not output.is_relative_to(ROOT):raise ContractError('preparation must remain in this project')
    with heavy_job(ROOT):
        output.mkdir(parents=True,exist_ok=False)
        write_json_new(output/'allocation.json',allocation);write_json_new(output/'model-profile.json',profile)
        journal=output/'setup-events.jsonl';records=[];peak=0
        env={k:v for k,v in os.environ.items() if k in ('PATH','LANG','LC_ALL')}
        env.update(TMPDIR=str(output),GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_SYSTEM='/dev/null',
                   GIT_TERMINAL_PROMPT='0',CMAKE_BUILD_PARALLEL_LEVEL=str(limits['compute_threads']))
        def budget(process=None):
            nonlocal peak
            if time.monotonic_ns()>=deadline:raise TimeoutError('original autonomous allocation exhausted')
            if directory_bytes(ROOT)>limits['disk_bytes']:raise RuntimeError('project disk allocation exhausted')
            used=(_rss(os.getpid()) or 0)+(group_rss(process.pid) if process else 0);peak=max(peak,used)
            if used>limits['memory_bytes']:raise MemoryError('aggregate preparation RSS allocation exhausted')
        def command(argv,label):
            with (output/(label+'.log')).open('xb') as f:
                process=start_guarded_process(argv,cwd=output,env=env,stdin=subprocess.DEVNULL,
                    stdout=f,stderr=subprocess.STDOUT,lease_fd=active_heavy_lease_fd())
            try:
                while process.poll() is None:budget(process);time.sleep(.25)
                if process.returncode:raise RuntimeError(label+' failed; original log retained')
            finally:stop_owned_process(process)
        def phase(name,fn):
            before=time.monotonic_ns();initial=directory_bytes(output);status='COMPLETED';error=None
            append_event(journal,{'phase':name,'event':'STARTED','observed_ns':before})
            try:fn()
            except BaseException as exc:status='INTERRUPTED' if isinstance(exc,KeyboardInterrupt) else 'FAILED';error=exc
            record={'phase':name,'status':status,'started_ns':before,'finished_ns':time.monotonic_ns(),
                'bytes_acquired':max(0,directory_bytes(output)-initial),'details':name+'; exact source/model profile; all logs retained'}
            records.append(record);append_event(journal,{'event':'TERMINAL','record':record})
            write_json_new(output/(name+'-receipt.json'),record)
            if error:raise error
        source=output/'llama.cpp';build=output/'build'
        def source_fetch():
            command(['git','-c','credential.helper=','clone','--depth','1','--branch','v0.2.0',
                     'https://github.com/ggml-org/llama.cpp.git',str(source)],'source-clone')
            revision=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],env=env,text=True).strip()
            if revision!=BACKEND_COMMIT:raise ContractError('upstream source revision drift')
        def model_fetch():
            opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),ReviewedRedirect())
            for index,artifact in enumerate(profile['files']):
                budget();name=artifact['filename'];part=output/(name+'.partial');h=hashlib.sha256();count=0
                url=f"https://huggingface.co/{profile['repository']}/resolve/{profile['revision']}/{name}"
                req=urllib.request.Request(url,headers={'User-Agent':'Lean-Model-Lab/0.4-reviewed-model-retrieval'})
                t=time.monotonic_ns();last=t
                print(f"Downloading reviewed shard {index+1}/{len(profile['files'])}: {name}",flush=True)
                with opener.open(req,timeout=30) as response,part.open('xb') as stream:
                    reviewed_model_url(response.url)
                    while True:
                        chunk=response.read(4*1024*1024)
                        if not chunk:break
                        count+=len(chunk)
                        if count>artifact['bytes']:raise ContractError('shard exceeds exact reviewed byte size')
                        h.update(chunk);stream.write(chunk)
                        if time.monotonic_ns()-last>10**9:budget();last=time.monotonic_ns()
                    stream.flush();os.fsync(stream.fileno())
                if count!=artifact['bytes'] or h.hexdigest()!=artifact['sha256']:
                    raise ContractError('shard byte count/SHA mismatch; partial retained')
                os.link(part,output/name);part.unlink()
                append_event(journal,{'event':'VERIFIED_SHARD','filename':name,'bytes':count,
                    'sha256':h.hexdigest(),'started_ns':t,'finished_ns':time.monotonic_ns()})
                print(f'Verified shard {index+1}/{len(profile["files"])} ({count} bytes)',flush=True)
        def compile_backend():
            patch=ROOT/'patches'/BACKEND_PATCH_FILENAME
            if file_digest(patch)!=BACKEND_PATCH_SHA256:raise ContractError('reviewed GCC8 patch drift')
            command(['git','-C',str(source),'apply','--check',str(patch)],'patch-check')
            command(['git','-C',str(source),'apply',str(patch)],'patch-apply')
            options=native_build_options(env);write_json_new(output/'build-options.json',options)
            command(['cmake','-S',str(source),'-B',str(build),*[f'-D{k}={v}' for k,v in options.items()]],'cmake-configure')
            command(['cmake','--build',str(build),'--target','llama-server','--parallel',str(limits['compute_threads'])],'cmake-build')
            command(['ldd',str(build/'bin/llama-server')],'linked-system-libraries')
        try:
            phase('source-acquisition',source_fetch);phase('model-acquisition',model_fetch);phase('build',compile_backend)
            budget()
            receipt={'schema_version':2,'boot_id':allocation['boot_id'],'allocation':allocation,
                'records':records,'artifacts':{'backend_revision':BACKEND_COMMIT,'backend_patch_sha256':BACKEND_PATCH_SHA256,
                    'server_sha256':file_digest(build/'bin/llama-server'),'model_profile_id':args.profile,
                    'model_profile_sha256':digest(profile)},
                'resource_observations':{'maximum_observed_aggregate_rss_bytes':peak,
                    'scope':'sampled preparation process plus owned build group; not continuous allocation-wide peak'}}
            write_json_new(output/'setup.json',receipt)
            print('Prepared exact profile and backend; no inference performed.',flush=True)
            return 0
        except BaseException as exc:
            write_json_new(output/'setup-failure.json',{'schema_version':2,'allocation':allocation,'model_profile':profile,
                'records':records,'error':type(exc).__name__+': '+str(exc),'failed_observation_ns':time.monotonic_ns(),
                'maximum_observed_aggregate_rss_bytes':peak})
            print('Preparation failed; all observed costs and partials retained: '+str(exc),file=sys.stderr);return 2

def prepare(args):
    previous={}
    def stop(signum,frame):raise KeyboardInterrupt('preparation cancelled by operator')
    for sig in (signal.SIGINT,signal.SIGTERM):previous[sig]=signal.signal(sig,stop)
    try:return _prepare(args)
    finally:
        for sig,handler in previous.items():signal.signal(sig,handler)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--allocation',type=Path,required=True)
    p.add_argument('--profile',required=True);p.add_argument('--output',type=Path,required=True)
    try:raise SystemExit(prepare(p.parse_args()))
    except (OSError,ValueError) as exc:print('lean-model-lab prepare: '+str(exc),file=sys.stderr);raise SystemExit(2)
