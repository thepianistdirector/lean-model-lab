#!/usr/bin/env python3
"""Acquire/build only the approved pinned graph, locally, with retained setup costs.

This script is inert without a valid operator admission record. It never installs
system packages, downloads remote executables, loads model code, or runs inference.
"""
from __future__ import annotations

import argparse
import contextlib
import os
import signal
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from lean_model_lab.admission import validate_admission
from lean_model_lab.process_guard import start_guarded_process
from lean_model_lab.resources import active_heavy_lease_fd
from lean_model_lab.artifacts import append_event,write_json_new
from lean_model_lab.config import LIMITS
from lean_model_lab.contracts import ContractError,file_digest,read_json
from lean_model_lab.llama_adapter import (BACKEND_COMMIT,BACKEND_PATCH_FILENAME,BACKEND_PATCH_SHA256,
                                        MODEL_COMMIT,MODEL_FILENAME,MODEL_SHA256)
from lean_model_lab.runner import directory_bytes,stop_owned_process,_rss

CMAKE_OPTIONS={
 'CMAKE_BUILD_TYPE':'Release','BUILD_SHARED_LIBS':'OFF','LLAMA_BUILD_COMMON':'ON',
 'LLAMA_BUILD_TOOLS':'ON','LLAMA_BUILD_SERVER':'ON','GGML_CPU':'ON',
 'LLAMA_BUILD_APP':'OFF','LLAMA_BUILD_EXAMPLES':'OFF','LLAMA_BUILD_TESTS':'OFF',
 'LLAMA_BUILD_UI':'OFF','LLAMA_USE_PREBUILT_UI':'OFF','LLAMA_OPENSSL':'OFF',
 'LLAMA_BUILD_BORINGSSL':'OFF','LLAMA_BUILD_LIBRESSL':'OFF','LLAMA_SUBPROCESS':'OFF',
 'LLAMA_LLGUIDANCE':'OFF','MTMD_VIDEO':'OFF','GGML_OPENMP':'OFF','GGML_OPENMP_FETCH':'OFF',
 'GGML_BLAS':'OFF','GGML_CPU_KLEIDIAI':'OFF','GGML_RPC':'OFF','GGML_CCACHE':'OFF',
 'GGML_CUDA':'OFF','GGML_METAL':'OFF','GGML_VULKAN':'OFF','GGML_SYCL':'OFF',
 'GGML_HIP':'OFF','GGML_BACKEND_DL':'OFF','LLAMA_BUILD_IS_DEV':'OFF','GGML_NATIVE':'ON'}


def native_build_options(env):
    """GCC 8 ships C++17 filesystem in its existing separate standard archive."""
    options=dict(CMAKE_OPTIONS)
    version=subprocess.check_output(['c++','-dumpfullversion'],env=env,text=True,timeout=10).strip()
    if version.split('.')[0]=='8':
        library=subprocess.check_output(['c++','-print-file-name=libstdc++fs.a'],
                                        env=env,text=True,timeout=10).strip()
        if not Path(library).is_file():
            raise ContractError('GCC 8 filesystem standard library is unavailable; no toolchain installation allowed')
        options['CMAKE_CXX_STANDARD_LIBRARIES']='-lstdc++fs'
    return options


def reviewed_model_url(url):
    parsed=urllib.parse.urlsplit(url)
    allowed=('huggingface.co','hf.co','xethub.hf.co')
    if (parsed.scheme!='https' or parsed.username or parsed.password or parsed.port not in (None,443) or
        not parsed.hostname or not any(parsed.hostname==h or parsed.hostname.endswith('.'+h) for h in allowed)):
        raise ContractError('unreviewed model CDN redirect; refusing the request')
    return url


class ReviewedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        reviewed_model_url(urllib.parse.urljoin(req.full_url,newurl))
        return super().redirect_request(req,fp,code,msg,headers,newurl)


def group_rss(group: int) -> int:
    total=0
    for path in Path('/proc').iterdir():
        if not path.name.isdecimal():continue
        try:
            fields=(path/'stat').read_text().rsplit(')',1)[1].split()
            if int(fields[2])==group:total+=_rss(int(path.name)) or 0
        except (OSError,ValueError,IndexError):pass
    return total


def _prepare(args):
    validate_admission(read_json(args.admission))
    output=args.output.resolve()
    if not output.is_relative_to(ROOT):raise ContractError('setup output must remain inside this project')
    output.mkdir(parents=True,exist_ok=False)
    started=time.monotonic_ns();deadline=started+LIMITS['full_wall_seconds']*10**9
    write_json_new(output/'allocation.json',{'schema_version':1,
        'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
        'started_ns':started,'deadline_ns':deadline,'limits':LIMITS})
    journal=output/'setup-events.jsonl';records=[]
    env={key:value for key,value in os.environ.items() if key in ('PATH','LANG','LC_ALL')}
    env.update(TMPDIR=str(output),GIT_CONFIG_GLOBAL='/dev/null',GIT_CONFIG_SYSTEM='/dev/null',
               GIT_TERMINAL_PROMPT='0',CMAKE_BUILD_PARALLEL_LEVEL='2')
    def budget(process=None):
        if time.monotonic_ns()>=deadline:raise TimeoutError('two-hour full-wall allocation exhausted')
        if directory_bytes(output)>LIMITS['disk_bytes']:raise RuntimeError('5 GiB setup disk allocation exhausted')
        if process and group_rss(process.pid)+(_rss(os.getpid()) or 0)>LIMITS['memory_bytes']:
            raise MemoryError('4 GiB aggregate setup RSS allocation exhausted')
    def command(arguments,label):
        with (output/(label+'.log')).open('xb') as log:
            process=start_guarded_process(arguments,cwd=output,env=env,stdin=subprocess.DEVNULL,
                stdout=log,stderr=subprocess.STDOUT,lease_fd=active_heavy_lease_fd())
        try:
            while process.poll() is None:
                budget(process);time.sleep(.25)
            if process.returncode:raise RuntimeError(f'{label} failed with exit {process.returncode}; retained log')
        finally:stop_owned_process(process)
    def phase(name,function):
        phase_start=time.monotonic_ns();before=directory_bytes(output)
        append_event(journal,{'phase':name,'event':'STARTED','observed_ns':phase_start})
        status='COMPLETED';failure=None
        try:function()
        except BaseException as exc:
            status='INTERRUPTED' if isinstance(exc,KeyboardInterrupt) else 'FAILED';failure=exc
        record={'phase':name,'status':status,'started_ns':phase_start,'finished_ns':time.monotonic_ns(),
            'bytes_acquired':max(0,directory_bytes(output)-before),'details':name+'; retained local logs and artifacts'}
        records.append(record);append_event(journal,{'event':'TERMINAL','record':record})
        write_json_new(output/(name+'-receipt.json'),record)
        if failure:raise failure
    source=output/'llama.cpp';build=output/'build';model=output/MODEL_FILENAME
    def fetch_source():
        command(['git','-c','credential.helper=','clone','--depth','1','--branch','v0.2.0',
                 'https://github.com/ggml-org/llama.cpp.git',str(source)],'source-clone')
        actual=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],env=env,text=True).strip()
        if actual!=BACKEND_COMMIT:raise ContractError('upstream source tag does not match pinned commit')
    def fetch_model():
        url=f'https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/{MODEL_COMMIT}/{MODEL_FILENAME}'
        part=output/(MODEL_FILENAME+'.partial')
        request=urllib.request.Request(url,headers={'User-Agent':'Lean-Model-Lab/0.1-artifact-retrieval'})
        opener=urllib.request.build_opener(urllib.request.ProxyHandler({}),ReviewedRedirect())
        with opener.open(request,timeout=30) as response,part.open('xb') as stream:
            reviewed_model_url(response.url)
            total=0;last_check=0
            while True:
                chunk=response.read(1024*1024)
                if not chunk:break
                total+=len(chunk)
                if total>1_400_000_000:raise ContractError('model exceeds reviewed download size')
                stream.write(chunk)
                if time.monotonic_ns()-last_check>10**9:budget();last_check=time.monotonic_ns()
            stream.flush();os.fsync(stream.fileno())
        if file_digest(part)!=MODEL_SHA256:raise ContractError('downloaded model checksum mismatch; partial retained')
        os.link(part,model);part.unlink()
    def compile_backend():
        patch=ROOT/'patches'/BACKEND_PATCH_FILENAME
        if file_digest(patch)!=BACKEND_PATCH_SHA256:
            raise ContractError('reviewed compiler-compatibility patch changed')
        command(['git','-C',str(source),'apply','--check',str(patch)],'compatibility-patch-check')
        command(['git','-C',str(source),'apply',str(patch)],'compatibility-patch-apply')
        options=native_build_options(env)
        write_json_new(output/'build-options.json',options)
        command(['cmake','-S',str(source),'-B',str(build),
                 *[f'-D{key}={value}' for key,value in options.items()]],'cmake-configure')
        command(['cmake','--build',str(build),'--target','llama-server','--parallel','2'],'cmake-build')
        command(['ldd',str(build/'bin'/'llama-server')],'linked-system-libraries')
    try:
        phase('source-acquisition',fetch_source)
        phase('model-acquisition',fetch_model)
        phase('build',compile_backend)
        receipt={'schema_version':1,'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
                 'records':records,'artifacts':{'backend_revision':BACKEND_COMMIT,
                 'backend_patch_sha256':BACKEND_PATCH_SHA256,
                 'server_sha256':file_digest(build/'bin'/'llama-server'),'model_sha256':MODEL_SHA256}}
        write_json_new(output/'setup.json',receipt)
        print('Prepared exact local artifacts; no inference performed. Receipt: '+str((output/'setup.json').relative_to(ROOT)))
        return 0
    except BaseException as exc:
        write_json_new(output/'setup-failure.json',{'records':records,'error':type(exc).__name__+': '+str(exc),
                       'full_wall_elapsed_ns':time.monotonic_ns()-started})
        print('Setup failed; artifacts and all costs retained: '+str(exc),file=sys.stderr)
        return 2


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--admission',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args(argv)
    from lean_model_lab.resources import heavy_job
    validate_admission(read_json(args.admission))
    previous={}
    def stop(signum,frame):raise KeyboardInterrupt('preparation cancelled by operator')
    for sig in (signal.SIGINT,signal.SIGTERM):previous[sig]=signal.signal(sig,stop)
    try:
        with heavy_job(ROOT):return _prepare(args)
    finally:
        for sig,handler in previous.items():signal.signal(sig,handler)


if __name__=='__main__':
    try:raise SystemExit(main())
    except (OSError,ValueError) as exc:
        print('lean-model-lab setup: '+str(exc),file=sys.stderr);raise SystemExit(2)
