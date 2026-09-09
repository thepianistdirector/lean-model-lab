"""Bounded Linux coordinator for the exact reviewed local llama.cpp artifact.

No acquisition, shell execution, remote endpoint, untrusted policy or production
server is supported. The caller supplies lawful artifacts and an approved setup
ledger. Process limits are not a security sandbox.
"""
from __future__ import annotations

import concurrent.futures
import ctypes
import contextlib
import json
import os
import platform
import resource
import signal
import socket
import subprocess
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

from .resources import heavy_lease_fds
from . import __version__
from .artifacts import append_event, write_json_new
from .config import LIMITS, make_config, validate_config
from .contracts import ContractError, canonical_bytes, digest, file_digest, make_workload, parse_json
from .evidence import OVERHEAD_KEYS
from .llama_adapter import (BACKEND_COMMIT, MODEL_SHA256, completion_payload,
                            normalize_response, render_prompt)


class RunStopped(RuntimeError):
    pass


def hardware() -> dict:
    cpu='unknown CPU'
    try:
        for line in Path('/proc/cpuinfo').read_text().splitlines():
            if line.startswith('model name'):
                cpu=line.split(':',1)[1].strip();break
    except OSError: pass
    return {'platform':platform.system()+'-'+platform.machine(), 'cpu':cpu}


def implementation_digest() -> str:
    # Enumerate all package source, including future modules, in source and zipapp form.
    import hashlib
    from importlib.resources import files
    return digest({entry.name:hashlib.sha256(entry.read_bytes()).hexdigest()
                   for entry in sorted(files('lean_model_lab').iterdir(),key=lambda e:e.name)
                   if entry.is_file() and entry.name.endswith('.py')})


def _probe(status='UNAVAILABLE', *, scope, value=None, unit='unavailable') -> dict:
    return {'status':status,'scope':scope,'value':value,'unit':unit}


def environment(load: list[float], peak_server_bytes: int | None) -> dict:
    return {'observer':'Lean Model Lab native SSE client', 'version':__version__, **hardware(),
            'load':_probe('MEASURED',scope='host load averages before/after attempt (1,5,15 minutes)',
                          value=load,unit='runnable_or_uninterruptible_tasks'),
            'memory':_probe('MEASURED' if peak_server_bytes is not None else 'UNAVAILABLE',
                            scope='maximum observed /proc owned-server VmHWM before shutdown; excludes coordinator',
                            value=peak_server_bytes,unit='bytes'),
            'thermal':_probe(scope='no admitted thermal sensor'),
            'energy':_probe(scope='no admitted energy sensor; no TDP estimate')}


def directory_bytes(path: Path) -> int:
    total=0
    for entry in path.rglob('*'):
        if entry.is_file() and not entry.is_symlink():
            try:total+=entry.stat().st_size
            except FileNotFoundError:pass
    return total


def _rss(pid: int, field='VmRSS') -> int | None:
    try:
        for line in Path(f'/proc/{pid}/status').read_text().splitlines():
            if line.startswith(field+':'):return int(line.split()[1])*1024
    except (OSError,ValueError):pass
    return None


def _free_port() -> int:
    with socket.socket() as listener:
        listener.bind(('127.0.0.1',0));return listener.getsockname()[1]


def server_arguments(server: Path, model: Path, concurrency: int, port: int,config: dict | None=None) -> list[str]:
    if config is not None and config['schema_version'] in (2,3):
        if type(concurrency) is not int or concurrency not in config['evaluation']['concurrency_modes']:raise ContractError('unsupported recipe concurrency')
        engine=config['engine']
        return [str(server),'--model',str(model),'--host','127.0.0.1','--port',str(port),
            '--parallel',str(concurrency),'--ctx-size',str(engine['context_per_slot']*concurrency),
            '--threads',str(engine['compute_threads']),'--threads-batch',str(engine['compute_threads']),
            '--threads-http',str(engine['http_threads']),'--device','none','--gpu-layers','0',
            '--no-context-shift','--no-ui','--no-agent','--cache-ram','0','--no-cache-idle-slots',
            '--no-kv-unified','--cache-reuse','0','--no-warmup','--offline','--no-mmproj','--log-colors','off']
    if concurrency not in (1,4):raise ContractError('unsupported concurrency')
    return [str(server), '--model',str(model),'--host','127.0.0.1','--port',str(port),
            '--parallel',str(concurrency),'--ctx-size',str(2048*concurrency),
            '--threads','2','--threads-batch','2','--threads-http','4',
            '--device','none','--gpu-layers','0','--no-context-shift','--no-ui','--no-agent',
            '--cache-ram','0','--no-cache-idle-slots','--no-kv-unified','--cache-reuse','0',
            '--no-warmup','--offline','--no-mmproj','--log-colors','off']


def _limits(parent_pid: int | None = None,limits: dict | None=None,compute_threads: int=2,bind_cpus: bool=False) -> None:
    limits=LIMITS if limits is None else limits
    if parent_pid is not None:
        libc=ctypes.CDLL(None,use_errno=True)
        if libc.prctl(1,signal.SIGTERM,0,0,0)!=0:
            raise OSError(ctypes.get_errno(),"cannot establish parent-death signal")
        if os.getppid()!=parent_pid:os._exit(125)
    resource.setrlimit(resource.RLIMIT_AS,(limits['memory_bytes'],limits['memory_bytes']))
    resource.setrlimit(resource.RLIMIT_CPU,(limits['full_wall_seconds']*compute_threads,)*2)
    if bind_cpus:
        allowed=sorted(os.sched_getaffinity(0))
        if len(allowed)<compute_threads:raise ContractError('fewer CPUs available than frozen recipe threads')
        os.sched_setaffinity(0,set(allowed[:compute_threads]))
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    os.nice(10)


def _group_members(group: int) -> list[int]:
    members=[]
    for path in Path('/proc').iterdir():
        if not path.name.isdecimal():continue
        try:
            fields=(path/'stat').read_text().rsplit(')',1)[1].split()
            if int(fields[2])==group and int(fields[3])==group and fields[0]!='Z':
                members.append(int(path.name))
        except (OSError,ValueError,IndexError):pass
    return members


def stop_owned_process(process: subprocess.Popen) -> None:
    """Close the fresh process group, including children after its leader exits.

    Call only for Popen(start_new_session=True) objects created by this process.
    A completed cleanup is remembered so later calls never target a reused ID.
    """
    if getattr(process,'_lml_group_stopped',False):return
    group=process.pid
    # A still-existing leader must be the session/group created for this handle.
    try:
        if os.getpgid(group)!=group or os.getsid(group)!=group:
            raise RunStopped('owned process lost its expected session/group identity')
    except ProcessLookupError:pass
    with contextlib.suppress(ProcessLookupError):os.killpg(group,signal.SIGTERM)
    deadline=time.monotonic()+3
    while _group_members(group) and time.monotonic()<deadline:time.sleep(.05)
    if _group_members(group):
        with contextlib.suppress(ProcessLookupError):os.killpg(group,signal.SIGKILL)
        deadline=time.monotonic()+3
        while _group_members(group) and time.monotonic()<deadline:time.sleep(.05)
    if _group_members(group):raise RunStopped('owned process group did not stop; retain its inventory')
    process.wait(timeout=3)
    process._lml_group_stopped=True


def _opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _json_request(base: str, path: str, payload=None, timeout=2):
    data=canonical_bytes(payload) if payload is not None else None
    req=urllib.request.Request(base+path,data=data,headers={'Content-Type':'application/json'})
    with _opener().open(req,timeout=timeout) as response:
        raw=response.read(4*1024*1024+1)
    if len(raw)>4*1024*1024:raise ContractError('backend response exceeds bounded JSON size')
    return parse_json(raw)


def _stream(base: str, payload: dict, raw_path: Path, cancel: threading.Event,
            *, request_id: str, arrival_ns: int, admitted_ns: int, prompt_count: int,
            limits: dict | None=None,seed: int=20260907,max_output_tokens: int=32) -> dict:
    limits=LIMITS if limits is None else limits
    dispatch=time.monotonic_ns();records=[];error=None
    try:
        request=urllib.request.Request(base+'/completion',data=canonical_bytes(payload),
                                        headers={'Content-Type':'application/json','Accept':'text/event-stream'})
        with _opener().open(request,timeout=limits['request_timeout_seconds']) as response:
            data=[];total=0;record_size=0
            for line in response:
                if cancel.is_set():raise RunStopped('attempt cancelled')
                now=time.monotonic_ns();total+=len(line);record_size+=len(line)
                if total>2*1024*1024 or record_size>128*1024:
                    raise ContractError('backend stream exceeds admitted evidence byte bound')
                if line.strip()==b'':
                    if not data:continue
                    encoded=b'\n'.join(data);data=[];record_size=0
                    # Receipt timestamp belongs to this whole SSE event, not its individual tokens.
                    append_event(raw_path,{'observed_ns':now,'data_utf8':encoded.decode('utf-8')})
                    if encoded==b'[DONE]':break
                    event=parse_json(encoded);records.append((now,event))
                    if event.get('stop') is True:break
                elif line.startswith(b'data:'):
                    data.append(line[5:].lstrip(b' ').rstrip(b'\r\n'))
            if data:raise ContractError('unterminated final SSE record')
        return normalize_response(records,request_id=request_id,arrival_ns=arrival_ns,
            admitted_ns=admitted_ns,dispatch_ns=dispatch,completed_ns=time.monotonic_ns(),
            prompt_tokens=prompt_count,slot=payload['id_slot'],seed=seed,max_output_tokens=max_output_tokens)
    except (OSError,ValueError,RunStopped,subprocess.SubprocessError,urllib.error.URLError) as exc:
        error=type(exc).__name__+': '+str(exc)
        append_event(raw_path,{'observed_ns':time.monotonic_ns(),'error':error})
        # Keep actual observed partial output and unknown final generated count.
        events=[];text=[];ids=[]
        for observed,event in records:
            if isinstance(event,dict) and event.get('stop') is False and 'prompt_progress' not in event:
                tokens=event.get('tokens',[])
                if isinstance(tokens,list) and all(type(t) is int and t>=0 for t in tokens):
                    ids.extend(tokens)
                    if tokens:events.append({'observed_ns':observed,'token_ids':tokens})
                if isinstance(event.get('content'),str):text.append(event['content'])
        cancelled=cancel.is_set()
        return {'request_id':request_id,'arrival_ns':arrival_ns,'admitted_ns':admitted_ns,
                'dispatch_ns':dispatch,'first_token_ns':events[0]['observed_ns'] if events else None,
                'completed_ns':time.monotonic_ns(),'token_events':events,'output_token_ids':ids,
                'generated_tokens':None,'output_text':''.join(text),'prompt_tokens':prompt_count,
                'engine_start_ns':None,'status':'CANCELLED' if cancelled else 'FAILED',
                'finish_reason':'cancelled' if cancelled else 'error'}


def execute_attempt(session, *, server: Path, model: Path, config: dict, workload: dict,
                    concurrency: int, pair_index: int, arm: str, deadline_ns: int,
                    project_root: Path) -> dict:
    if config['schema_version'] in (2,3):
        from .runner_recipe import execute_attempt_v2
        return execute_attempt_v2(session,server=server,model=model,config=config,workload=workload,
            concurrency=concurrency,pair_index=pair_index,arm=arm,deadline_ns=deadline_ns,project_root=project_root)
    started=time.monotonic_ns(); reservation=session.reserve(arm,concurrency,pair_index,started)
    attempt_id=reservation['attempt_id'];raw_dir=reservation['raw_dir'];raw_dir.mkdir(exist_ok=True,parents=True)
    overhead={key:0 for key in OVERHEAD_KEYS};process=None;requests=[];service_started=started
    cancel=threading.Event();completed_requests=[];peak=None;load=list(os.getloadavg());status='FAILED'
    error=None;port=_free_port();base=f'http://127.0.0.1:{port}';interrupted=False
    previous_signals={}
    def on_signal(signum,frame):cancel.set()
    for signum in (signal.SIGINT,signal.SIGTERM):
        previous_signals[signum]=signal.signal(signum,on_signal)
    try:
        t=time.monotonic_ns()
        if file_digest(model)!=MODEL_SHA256 or file_digest(server)!=config['backend']['server_sha256']:
            raise ContractError('local model/backend bytes changed after admission')
        overhead['verification']=time.monotonic_ns()-t
        if time.monotonic_ns()>=deadline_ns:raise RunStopped('full-wall allocation exhausted')
        t=time.monotonic_ns()
        argv=server_arguments(server,model,concurrency,port)
        clean_env={'PATH':os.environ.get('PATH','/usr/bin:/bin'),'LANG':'C.UTF-8','LC_ALL':'C.UTF-8',
                   'TMPDIR':str(raw_dir),'LLAMA_CACHE':str(raw_dir/'cache')}
        parent_pid=os.getpid()
        with (raw_dir/'server.log').open('xb') as log:
            process=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,
                env=clean_env,start_new_session=True,pass_fds=heavy_lease_fds(),preexec_fn=lambda:_limits(parent_pid))
        write_json_new(raw_dir/'process.json',{'pid':process.pid,'started_ns':time.monotonic_ns(),
            'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
            'proc_start_ticks':Path(f'/proc/{process.pid}/stat').read_text().rsplit(')',1)[1].split()[19]})
        ready_deadline=min(deadline_ns,t+LIMITS['startup_timeout_seconds']*10**9)
        while time.monotonic_ns()<ready_deadline:
            if cancel.is_set():raise RunStopped('cancelled during model load')
            if (_rss(process.pid) or 0)+(_rss(os.getpid()) or 0)>LIMITS['memory_bytes']:
                raise RunStopped('aggregate RSS allocation exhausted during load')
            if process.poll() is not None:raise RunStopped('backend exited during load; inspect retained server.log')
            try:
                if _json_request(base,'/health').get('status')=='ok':break
            except (OSError,ValueError,urllib.error.URLError):pass
            time.sleep(.1)
        else:raise RunStopped('backend readiness deadline exhausted')
        overhead['load']=time.monotonic_ns()-t
        # Load includes process initialization; no fabricated split of internal startup.
        slots=_json_request(base,'/slots')
        if (not isinstance(slots,list) or len(slots)!=concurrency or
            sorted(row.get('id',-1) for row in slots)!=list(range(concurrency)) or
            any(row.get('n_ctx')!=2048 or row.get('is_processing') is not False for row in slots)):
            raise ContractError('backend slot/context inventory differs from fixed concurrency')
        write_json_new(raw_dir/'slots.json',slots)
        t=time.monotonic_ns();tokenized=[]
        for request in workload['requests']:
            if cancel.is_set() or time.monotonic_ns()>=deadline_ns:raise RunStopped('stopped during tokenization')
            if (_rss(process.pid) or 0)+(_rss(os.getpid()) or 0)>LIMITS['memory_bytes']:
                raise RunStopped('aggregate RSS allocation exhausted during tokenization')
            value=_json_request(base,'/tokenize',{'content':render_prompt(request['prompt']),
                                               'add_special':True,'parse_special':True})
            tokens=value.get('tokens')
            completion_payload(tokens,0,False)  # Reject malformed or over-context input before service.
            tokenized.append(tokens)
        write_json_new(raw_dir/'tokenized-inputs.json',{'workload_sha256':digest(workload),'tokens':tokenized})
        overhead['cache_preparation']=time.monotonic_ns()-t
        service_started=time.monotonic_ns();checkpoint_lock=threading.Lock()
        def lane(slot):
            outputs=[]
            for index in range(slot,len(workload['requests']),concurrency):
                if cancel.is_set():break
                request=workload['requests'][index];admitted=time.monotonic_ns()
                result=_stream(base,completion_payload(tokenized[index],slot,arm=='candidate'),
                    raw_dir/(request['request_id']+'.jsonl'),cancel,request_id=request['request_id'],
                    arrival_ns=service_started,admitted_ns=admitted,prompt_count=len(tokenized[index]))
                outputs.append(result)
                with checkpoint_lock:
                    completed_requests.append(result)
                    session.checkpoint(attempt_id,result,time.monotonic_ns())
            return outputs
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as workers:
            try:
                futures=[workers.submit(lane,slot) for slot in range(concurrency)]
                remaining=set(futures);last_disk_check=0
                while remaining:
                    _,remaining=concurrent.futures.wait(remaining,timeout=.1)
                    observed=_rss(process.pid,'VmHWM')
                    if observed is not None:peak=max(peak or 0,observed)
                    now=time.monotonic_ns()
                    aggregate=(_rss(process.pid) or 0)+(_rss(os.getpid()) or 0)
                    if now>=deadline_ns or aggregate>LIMITS['memory_bytes']:
                        error='full-wall or aggregate RSS allocation exhausted';cancel.set()
                    if now-last_disk_check>10**9:
                        if directory_bytes(project_root)>LIMITS['disk_bytes']:
                            error='project artifact disk allocation exhausted';cancel.set()
                        last_disk_check=now
                    if cancel.is_set():stop_owned_process(process)
                for future in futures:requests.extend(future.result())
            except BaseException:
                # Stop the backend before executor shutdown waits for active I/O.
                cancel.set()
                stop_owned_process(process)
                raise
        overhead['service']=time.monotonic_ns()-service_started
        status='INTERRUPTED' if cancel.is_set() else 'COMPLETED'
    except (OSError,ValueError,RunStopped,subprocess.SubprocessError,urllib.error.URLError) as exc:
        error=type(exc).__name__+': '+str(exc)
        status='INTERRUPTED' if cancel.is_set() else 'FAILED'
    finally:
        before_stop=time.monotonic_ns()
        if process is not None:
            observed=_rss(process.pid,'VmHWM')
            if observed is not None:peak=max(peak or 0,observed)
            stop_owned_process(process)
        overhead['recovery']+=time.monotonic_ns()-before_stop
        for signum,handler in previous_signals.items():signal.signal(signum,handler)
    requests=completed_requests
    finished=time.monotonic_ns()
    if not requests and service_started==started:
        service_started=finished
    if requests:
        overhead['service']=max(overhead['service'],max(r['completed_ns'] for r in requests)-service_started)
    if error:write_json_new(raw_dir/'failure.json',{'error':error,'observed_ns':finished})
    attempt={'schema_version':1,'evidence_class':config['evidence_class'],'attempt_id':attempt_id,
        'config_sha256':digest(config),'workload_sha256':digest(workload),'arm':arm,
        'concurrency':concurrency,'pair_index':pair_index,'started_ns':started,
        'service_started_ns':service_started,'finished_ns':finished,'status':status,
        'requests':requests,'overhead_ns':overhead,'environment':environment(load+list(os.getloadavg()),peak)}
    session.publish(attempt)
    finalized=time.monotonic_ns()
    session.record_setup({'phase':'artifact-finalization','status':'COMPLETED',
        'started_ns':finished,'finished_ns':finalized,'bytes_acquired':0,
        'details':'raw evidence hashing, immutable attempt publication and inventory reconciliation'})
    return attempt


def _run_study(*, server: Path, model: Path, output: Path, setup_receipt: dict,
              admission: dict | None=None,recipe: dict | None=None,predecessors: list[Path] | None=None) -> dict:
    """Execute the registered study after explicit local artifact admission."""
    if recipe is not None:
        from .runner_recipe import run_recipe
        return run_recipe(server=server,model=model,output=output,setup_receipt=setup_receipt,
            recipe=recipe,predecessors=predecessors or [])
    from .admission import validate_admission
    from .session import Session
    from .setup import validate_receipt
    validate_admission(admission)
    if output.exists():raise FileExistsError('study directory already exists; inspect it or choose a new study')
    validate_receipt(setup_receipt)
    setup_records=setup_receipt['records']
    if platform.system()!='Linux' or platform.machine()!='x86_64':
        raise ContractError('this candidate is reviewed for Linux x86_64 only')
    if not setup_records:
        raise ContractError('actual setup/acquisition/build ledger is required; unknown costs cannot be zero')
    wanted={'source-acquisition','model-acquisition','build'}
    if not wanted<={r.get('phase') for r in setup_records if r.get('status')=='COMPLETED'}:
        raise ContractError('setup ledger lacks completed source/model/build phases')
    first=min(r['started_ns'] for r in setup_records)
    deadline=first+LIMITS['full_wall_seconds']*10**9
    if time.monotonic_ns()>=deadline:raise RunStopped('full-wall setup/study allocation exhausted')
    server=server.resolve(strict=True);model=model.resolve(strict=True)
    before_version=time.monotonic_ns()
    if file_digest(model)!=MODEL_SHA256:raise ContractError('model bytes differ from approved SHA-256')
    server_sha256=file_digest(server)
    if server_sha256!=setup_receipt['artifacts']['server_sha256']:
        raise ContractError('server bytes differ from reviewed build receipt; refusing execution')
    version=subprocess.run([str(server),'--version'],capture_output=True,text=True,timeout=10,
                           env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},check=False)
    if version.returncode or BACKEND_COMMIT[:7] not in version.stdout+version.stderr:
        raise ContractError('backend version does not attest the pinned source commit')
    config=make_config(server_sha256=server_sha256,evidence_class='MEASURED',hardware=hardware(),
                       implementation_sha256=implementation_digest())
    validate_config(config)
    setup_records=list(setup_records)+[{'phase':'runtime-verification','status':'COMPLETED',
        'started_ns':before_version,'finished_ns':time.monotonic_ns(),'bytes_acquired':0,
        'details':'local binary version and model/backend SHA-256 verification'}]
    workload=make_workload();Session.create(output,config,workload,setup_records)
    with Session.open(output) as session:
        for concurrency in (1,4):
            for pair in range(3):
                order=('baseline','candidate') if pair!=1 else ('candidate','baseline')
                for arm in order:
                    if time.monotonic_ns()>=deadline:
                        return session.inspect()
                    print(f'Running pair {pair+1}, concurrency {concurrency}, {arm}',flush=True)
                    attempt=execute_attempt(session,server=server,model=model,config=config,workload=workload,
                        concurrency=concurrency,pair_index=pair,arm=arm,deadline_ns=deadline,project_root=Path.cwd())
                    print(f"Retained {attempt['status']}: {len(attempt['requests'])}/128 request records",flush=True)
                    if attempt['status']!='COMPLETED':return session.inspect()
        return session.inspect()


def run_study(**arguments) -> dict:
    from .admission import validate_admission
    from .resources import heavy_job,require_workspace_root
    if arguments.get('recipe') is not None:
        from .recipes import validate_recipe
        from .allocation import validate_allocation
        validate_recipe(arguments['recipe']);validate_allocation(arguments['recipe']['allocation'],active=True)
    else:validate_admission(arguments['admission'])
    root=require_workspace_root(arguments['server'],arguments['model'],arguments['output'])
    with heavy_job(root):
        return _run_study(**arguments)
