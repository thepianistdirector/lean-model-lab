"""Recipe-driven real CPU execution with bounded offered-arrival replay."""
from __future__ import annotations
import concurrent.futures
import os
import signal
import subprocess
import threading
import time
import urllib.error
from pathlib import Path
from .resources import heavy_lease_fds
from .allocation import validate_allocation
from .artifacts import append_event,write_json_new
from .config import make_config_v2,validate_config
from .contracts import ContractError,canonical_bytes,digest,file_digest,read_json
from .evidence import OVERHEAD_KEYS
from .llama_adapter import BACKEND_COMMIT,completion_payload,render_prompt
from .profiles import verify_model_files
from .recipes import validate_recipe,workload_from_recipe,schedule
from .replay import LaneReplay
from .runner import (RunStopped,_free_port,_json_request,_limits,_rss,_stream,directory_bytes,
                     environment,hardware,implementation_digest,server_arguments,stop_owned_process)


def execute_attempt_v2(session,*,server,model,config,workload,concurrency,pair_index,arm,deadline_ns,project_root):
    validate_config(config)
    if (concurrency,pair_index,arm) not in schedule(config):raise ContractError('attempt cell is outside frozen recipe')
    allocation=config['recipe']['allocation'];limits=config['limits'];engine=config['engine'];sampling=config['sampling']
    if deadline_ns!=allocation['deadline_ns']:raise ContractError('attempt cannot change original allocation deadline')
    if config['evidence_class']=='MEASURED':validate_allocation(allocation,active=True)
    started=time.monotonic_ns();reservation=session.reserve(arm,concurrency,pair_index,started)
    identifier=reservation['attempt_id'];raw=reservation['raw_dir'];overhead={k:0 for k in OVERHEAD_KEYS}
    process=None;cancel=threading.Event();completed=[];status='FAILED';error=None;peak=None;aggregate_peak=0
    service_started=started;previous_signals={};port=_free_port();base=f'http://127.0.0.1:{port}'
    def on_signal(signum,frame):cancel.set()
    for sig in (signal.SIGINT,signal.SIGTERM):previous_signals[sig]=signal.signal(sig,on_signal)
    def resources():
        nonlocal peak,aggregate_peak
        server_rss=_rss(process.pid) if process else 0
        observed=_rss(process.pid,'VmHWM') if process else None
        if observed is not None:peak=max(peak or 0,observed)
        used=(server_rss or 0)+(_rss(os.getpid()) or 0);aggregate_peak=max(aggregate_peak,used)
        if used>limits['memory_bytes']:raise RunStopped('aggregate RSS allocation exhausted')
        if time.monotonic_ns()>=deadline_ns:raise RunStopped('original full-wall allocation exhausted')
        if cancel.is_set():raise RunStopped('cancelled by operator')
    def payload(index,slot):
        from .recipes_v3 import cache_enabled
        cache = cache_enabled(config['recipe'], arm)
        return completion_payload(tokenized[index],slot,cache,seed=sampling['seed'],
            max_output_tokens=sampling['max_output_tokens'],context_per_slot=engine['context_per_slot'],slot_count=concurrency)
    def checkpoint(result):
        completed.append(result);session.checkpoint(identifier,result,time.monotonic_ns())
    load=list(os.getloadavg())
    try:
        t=time.monotonic_ns()
        verification=verify_model_files(model,config['model']['profile_id'],check=resources)
        if file_digest(server,check=resources)!=config['backend']['server_sha256']:raise ContractError('compiled backend bytes changed after admission')
        resources()
        version=subprocess.run([str(server),'--version'],capture_output=True,text=True,timeout=min(10,max(.001,(deadline_ns-time.monotonic_ns())/1e9)),
            env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},check=False)
        resources()
        if version.returncode or BACKEND_COMMIT[:7] not in version.stdout+version.stderr:
            raise ContractError('backend version differs from pinned source')
        write_json_new(raw/'backend-version.json',{'stdout':version.stdout,'stderr':version.stderr,'exit_code':version.returncode})
        write_json_new(raw/'model-verification.json',verification)
        overhead['verification']=time.monotonic_ns()-t;resources()
        t=time.monotonic_ns();argv=server_arguments(server,model,concurrency,port,config)
        env={'PATH':os.environ.get('PATH','/usr/bin:/bin'),'LANG':'C.UTF-8','LC_ALL':'C.UTF-8',
             'TMPDIR':str(raw),'LLAMA_CACHE':str(raw/'cache')}
        parent_pid=os.getpid()
        with (raw/'server.log').open('xb') as log:
            process=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,
                env=env,start_new_session=True,pass_fds=heavy_lease_fds(),preexec_fn=lambda:_limits(parent_pid,limits,engine['compute_threads'],True))
        affinity=sorted(os.sched_getaffinity(process.pid))
        if len(affinity)!=engine['compute_threads']:raise ContractError('backend CPU affinity differs from recipe policy')
        write_json_new(raw/'process.json',{'pid':process.pid,'started_ns':time.monotonic_ns(),
            'boot_id':allocation['boot_id'],'cpu_affinity':affinity,
            'proc_start_ticks':Path(f'/proc/{process.pid}/stat').read_text().rsplit(')',1)[1].split()[19]})
        ready=min(deadline_ns,t+limits['startup_timeout_seconds']*10**9)
        while time.monotonic_ns()<ready:
            resources()
            if process.poll() is not None:raise RunStopped('backend exited during model load; see retained log')
            try:
                if _json_request(base,'/health').get('status')=='ok':break
            except (OSError,ValueError,urllib.error.URLError):pass
            time.sleep(.1)
        else:raise RunStopped('backend startup deadline exceeded')
        overhead['load']=time.monotonic_ns()-t
        slots=_json_request(base,'/slots')
        if (not isinstance(slots,list) or len(slots)!=concurrency or
            sorted(r.get('id',-1) for r in slots)!=list(range(concurrency)) or
            any(r.get('n_ctx')!=engine['context_per_slot'] or r.get('is_processing') is not False for r in slots)):
            raise ContractError('native slots/context differ from recipe')
        write_json_new(raw/'slots.json',slots)
        t=time.monotonic_ns();tokenized=[];interventions=[]
        for request in workload['requests']:
            resources()
            prompt = request['prompt']
            if config['schema_version'] == 3:
                from .recipes_v3 import prompt_intervention
                intervention_started = time.monotonic_ns()
                intervention = prompt_intervention(prompt, config['recipe']['mechanism_id'], arm, config['recipe'].get('controller'))
                interventions.append({'request_id': request['request_id'], 'input_prompt_sha256': digest(prompt),
                    'result': intervention, 'duration_ns': time.monotonic_ns() - intervention_started})
                prompt = intervention['prompt']
            value=_json_request(base,'/tokenize',{'content':render_prompt(prompt),'add_special':True,'parse_special':True})
            tokens=value.get('tokens')
            completion_payload(tokens,0,False,seed=sampling['seed'],max_output_tokens=sampling['max_output_tokens'],
                context_per_slot=engine['context_per_slot'],slot_count=concurrency)
            tokenized.append(tokens)
        if config['schema_version'] == 3:
            write_json_new(raw/'prompt-interventions.json', {'schema_version': 1,
                'preparation_started_ns': t, 'preparation_finished_ns': time.monotonic_ns(), 'mechanism_id': config['recipe']['mechanism_id'],
                'arm': arm, 'scope': 'syntax/dependency checks only; no LLM output guarantee; preparation precedes offered arrivals and is charged in full wall',
                'requests': interventions})
        write_json_new(raw/'tokenized-inputs.json',{'workload_sha256':digest(workload),'tokens':tokenized})
        overhead['cache_preparation']=time.monotonic_ns()-t
        service_started=time.monotonic_ns()
        write_json_new(raw/'service-epoch.json',{'observed_ns':service_started,'workload_sha256':digest(workload)})
        replay=LaneReplay(workload,concurrency,service_started);futures={};last_disk=0
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
            try:
                while not replay.done:
                    now=time.monotonic_ns()
                    # Complete prior invocations before observing the next scheduler tick.
                    for slot,(index,future) in list(futures.items()):
                        if future.done():
                            result=future.result();checkpoint(result)
                            replay.complete(slot,index,time.monotonic_ns());del futures[slot]
                    try:
                        resources()
                        if now-last_disk>10**9:
                            if directory_bytes(project_root)>limits['disk_bytes']:raise RunStopped('project disk allocation exhausted')
                            last_disk=now
                    except RunStopped as exc:error=str(exc);cancel.set()
                    if cancel.is_set():
                        stop_owned_process(process)
                        for slot,(index,future) in list(futures.items()):
                            checkpoint(future.result());replay.complete(slot,index,time.monotonic_ns());del futures[slot]
                        break  # Unoffered/queued work remains explicitly missing, not silently retried.
                    for event in replay.advance(time.monotonic_ns()):
                        index=event['index'];slot=event['slot'];request=workload['requests'][index]
                        arrival=service_started+request['arrival_offset_ns']
                        append_event(raw/'scheduler.jsonl',{'request_id':request['request_id'],**event,
                            'arrival_ns':arrival,'pending_count_at_batch_end':replay.pending_count})
                        if event['kind']=='dispatch':
                            future=pool.submit(_stream,base,payload(index,slot),raw/(request['request_id']+'.jsonl'),cancel,
                                request_id=request['request_id'],arrival_ns=arrival,admitted_ns=event['observed_ns'],
                                prompt_count=len(tokenized[index]),limits=limits,seed=sampling['seed'],max_output_tokens=sampling['max_output_tokens'])
                            futures[slot]=(index,future)
                        else:
                            result={'request_id':request['request_id'],'arrival_ns':arrival,'admitted_ns':None,'dispatch_ns':None,
                                'first_token_ns':None,'completed_ns':event['observed_ns'],'token_events':[],
                                'output_token_ids':[],'output_text':'','generated_tokens':0,'engine_start_ns':None,
                                'prompt_tokens':len(tokenized[index]),'status':'REJECTED' if event['kind']=='queue_full' else 'EXPIRED',
                                'finish_reason':event['kind']}
                            append_event(raw/(request['request_id']+'.jsonl'),{'observed_ns':event['observed_ns'],
                                'scheduler_outcome':event['kind'],'engine_dispatched':False,'slot':slot})
                            checkpoint(result)
                    if not replay.done:
                        # Only local receipt/scheduler latency is measured; no engine clock is inferred.
                        next_arrival=replay.next_arrival_ns
                        sleep=.005 if next_arrival is None else min(.005,max(0,(next_arrival-time.monotonic_ns())/1e9))
                        if sleep:time.sleep(sleep)
            except BaseException:
                # Stop the backend before executor shutdown waits for active I/O.
                cancel.set()
                stop_owned_process(process)
                raise
        overhead['service']=time.monotonic_ns()-service_started
        status='INTERRUPTED' if cancel.is_set() else 'COMPLETED'
    except (OSError,ValueError,RunStopped,subprocess.SubprocessError,urllib.error.URLError) as exc:
        error=type(exc).__name__+': '+str(exc);status='INTERRUPTED' if cancel.is_set() else 'FAILED'
    finally:
        before=time.monotonic_ns()
        if process is not None:
            observed=_rss(process.pid,'VmHWM')
            if observed is not None:peak=max(peak or 0,observed)
            stop_owned_process(process)
        overhead['recovery']+=time.monotonic_ns()-before
        for sig,handler in previous_signals.items():signal.signal(sig,handler)
    finished=time.monotonic_ns()
    if service_started==started and not completed:service_started=finished
    if completed:overhead['service']=max(overhead['service'],max(r['completed_ns'] for r in completed)-service_started)
    if error:write_json_new(raw/'failure.json',{'error':error,'observed_ns':finished})
    write_json_new(raw/'resource-observations.json',{'maximum_observed_aggregate_rss_bytes':aggregate_peak,
        'server_vmhwm_bytes':peak,'scope':'sampled owned server plus coordinator RSS; not a continuous or allocation-wide aggregate peak'})
    attempt={'schema_version':config['schema_version'],'evidence_class':config['evidence_class'],'attempt_id':identifier,
        'config_sha256':digest(config),'workload_sha256':digest(workload),'arm':arm,'concurrency':concurrency,
        'pair_index':pair_index,'started_ns':started,'service_started_ns':service_started,'finished_ns':finished,
        'status':status,'requests':completed,'overhead_ns':overhead,'environment':environment(load+list(os.getloadavg()),peak)}
    session.publish(attempt)
    session.record_setup({'phase':'artifact-finalization','status':'COMPLETED','started_ns':finished,
        'finished_ns':time.monotonic_ns(),'bytes_acquired':0,'details':'raw hashing and immutable recipe-attempt publication'})
    return attempt


def discover_predecessors(project_root,allocation,explicit=()):
    """Find locally present same-allocation producers; explicit paths cannot hide one.

    This is a local admission guard, not authentication of deleted/external trials.
    Redacted derivatives never replace their producer. If only a derivative remains,
    admission is refused until the original producer history is restored.
    """
    from .session import Session
    project_root=Path(project_root).resolve()
    paths={Path(p).resolve() for p in explicit};derivative_ids=set();producers={}
    if any(not p.is_relative_to(project_root) for p in paths):raise ContractError('predecessor must be retained inside the same workspace')
    candidates={p.parent for pattern in ('session.json','config.json') for p in project_root.rglob(pattern)}
    for parent in sorted(candidates):
        manifest=parent/'session.json';config_path=parent/'config.json'
        if not config_path.is_file():
            value=read_json(manifest)
            if type(value) is dict and {'session_id','config_sha256','workload_sha256','setup_sha256'}<=set(value):
                raise ContractError('local producer manifest has lost its configuration; restore its history before new admission')
            continue
        config=read_json(config_path)
        if type(config) is not dict or config.get('schema_version') not in (2,3):continue
        recipe=config.get('recipe')
        if type(recipe) is not dict or type(recipe.get('allocation')) is not dict:
            raise ContractError('malformed local v2 study provenance')
        if recipe['allocation'].get('allocation_id')!=allocation['allocation_id']:continue
        if canonical_bytes(recipe.get('allocation'))!=canonical_bytes(allocation):
            raise ContractError('locally retained allocation identity has conflicting bounds or clock')
        # Only positively linked export sidecars may lack a producer layout.
        exported=parent.parent/'study'/'EXPORT-PROVENANCE.json'
        if parent.name=='original-provenance' and exported.is_file():
            provenance=read_json(exported)
            if (not manifest.is_file() or file_digest(manifest)!=provenance.get('source_session_sha256') or
                digest(config)!=read_json(manifest)['config_sha256']):
                raise ContractError('export provenance sidecars do not match their source identity')
            derivative_ids.add(read_json(manifest)['session_id'])
            continue
        if (parent/'EXPORT-PROVENANCE.json').exists():
            derivative_ids.add(read_json(manifest)['session_id']);continue
        paths.add(parent.resolve())
    for path in sorted(paths):
        with Session.open(path) as session:inventory=session.inspect()
        config=inventory['config']
        if config['schema_version'] not in (2,3) or canonical_bytes(config['recipe']['allocation'])!=canonical_bytes(allocation):
            raise ContractError('predecessor is outside this original allocation')
        if not inventory['inventory_complete']:raise ContractError('reconcile every local predecessor before another study')
        if (path/'EXPORT-PROVENANCE.json').exists():raise ContractError('predecessor must be an original producer, not a redacted derivative')
        identity=inventory['session_id']
        fingerprint=digest({'config':config,'workload':inventory['workload'],
            'attempts':inventory['attempts'],'setup':inventory['setup_accounting']['records'],
            'journal_sha256':file_digest(path/'journal.jsonl')})
        if identity in producers:
            if producers[identity][0]!=fingerprint:raise ContractError('conflicting local copies of a predecessor study')
        else:producers[identity]=(fingerprint,path)
    if derivative_ids-set(producers):raise ContractError('local derivative lacks its original predecessor producer')
    return [value[1] for key,value in sorted(producers.items())]


def inherited_setup(records,predecessors,allocation):
    """Retain declared prior study costs once, including adverse development trials."""
    from .session import Session,validate_setup_records
    merged={digest(r):r for r in records};seen=set()
    for path in predecessors:
        with Session.open(path) as session:inventory=session.inspect()
        if not inventory['inventory_complete']:raise ContractError('reconcile predecessor inventory before another study')
        config=inventory['config']
        if config['schema_version'] not in (2,3) or canonical_bytes(config['recipe']['allocation'])!=canonical_bytes(allocation):
            raise ContractError('predecessor is outside this original allocation')
        if inventory['session_id'] in seen:raise ContractError('duplicate predecessor study')
        seen.add(inventory['session_id'])
        for record in inventory['setup_accounting']['records']:merged[digest(record)]=record
        for a in inventory['attempts']:
            row={'phase':'predecessor-study-attempt','status':a['status'],'started_ns':a['started_ns'],
                'finished_ns':a['finished_ns'],'bytes_acquired':0,'details':json_details({
                    'source_session_id':inventory['session_id'],'source_config_sha256':inventory['config_sha256'],
                    'source_recipe_sha256':digest(config['recipe']),'source_attempt_id':a['attempt_id'],'source_attempt_sha256':digest(a),
                    'purpose':config['recipe']['purpose'],'expected_requests':len(inventory['workload']['requests']),
                    'observed_requests':len(a['requests']),'scope':'prior recipe trial retained, not a cell in this recipe'})}
            merged[digest(row)]=row
    result=sorted(merged.values(),key=lambda r:(r['started_ns'],r['finished_ns']))
    validate_setup_records(result)
    return result


def json_details(value):
    return canonical_bytes(value).decode('utf-8')


def run_recipe(*,server,model,output,setup_receipt,recipe,predecessors):
    from .setup import validate_receipt
    from .session import Session
    validate_recipe(recipe);allocation=validate_allocation(recipe['allocation'],active=True)
    validate_receipt(setup_receipt,recipe=recipe)
    if output.exists():raise FileExistsError('study output exists; inspect/resume or choose a new path')
    if hardware()['platform']!='Linux-x86_64':raise ContractError('only reviewed Linux x86_64 execution is admitted')
    if len(os.sched_getaffinity(0))<recipe['engine']['compute_threads']:raise ContractError('insufficient available CPU affinity')
    server=server.resolve(strict=True);model=model.resolve(strict=True);start=time.monotonic_ns()
    if not output.resolve().is_relative_to(Path.cwd().resolve()):raise ContractError('study output must remain in the project')
    # Expected identities come from the reviewed build receipt. Each reserved
    # attempt verifies actual bytes/version before loading; failures retain costs.
    config=make_config_v2(recipe=recipe,server_sha256=setup_receipt['artifacts']['server_sha256'],evidence_class='MEASURED',hardware=hardware(),
                         implementation_sha256=implementation_digest())
    validate_config(config)
    predecessors=discover_predecessors(Path.cwd(),allocation,predecessors)
    records=inherited_setup(setup_receipt['records'],predecessors,allocation)
    records.append({'phase':'runtime-admission','status':'COMPLETED','started_ns':start,
        'finished_ns':time.monotonic_ns(),'bytes_acquired':0,'details':'recipe/setup/hardware/prior-cost admission; actual shard and binary verification occurs inside each retained attempt'})
    workload=workload_from_recipe(recipe);Session.create(output,config,workload,records)
    with Session.open(output) as session:
        for concurrency,pair,arm in schedule(config):
            if time.monotonic_ns()>=allocation['deadline_ns']:return session.inspect()
            print(f'Running recipe pair {pair+1}, concurrency {concurrency}, {arm}',flush=True)
            attempt=execute_attempt_v2(session,server=server,model=model,config=config,workload=workload,
                concurrency=concurrency,pair_index=pair,arm=arm,deadline_ns=allocation['deadline_ns'],project_root=Path.cwd())
            print(f"Retained {attempt['status']}: {len(attempt['requests'])}/{len(workload['requests'])} offered request records",flush=True)
            if attempt['status']!='COMPLETED':return session.inspect()
        return session.inspect()
