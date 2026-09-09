#!/usr/bin/env python3
"""Exercise one real crash/reconcile/restart path inside the original allocation.

This intentional recovery control is not an additional completed comparison.
It stops after the first restarted arm completes and retains every extra attempt.
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from lean_model_lab.artifacts import write_json_new
from lean_model_lab.recipes import schedule,validate_recipe
from lean_model_lab.allocation import validate_allocation
from lean_model_lab.contracts import canonical_bytes,digest,file_digest,read_json
from lean_model_lab.runner import _group_members
from lean_model_lab.session import Session
from lean_model_lab.resources import require_workspace_root


def verify(args):
    fields=('output','archive','parent_study','server','model','setup','recipe')
    for field in fields:setattr(args,field,getattr(args,field).resolve())
    workspace=require_workspace_root(*(getattr(args,field) for field in fields))
    if workspace!=ROOT:raise ValueError('recovery harness must run in its own source workspace')
    root=args.output;root.mkdir(parents=True,exist_ok=False)
    study=root/'study';archive=args.archive.resolve();started=time.monotonic_ns()
    with Session.open(args.parent_study) as parent:
        source=parent.inspect()
    recipe=validate_recipe(read_json(args.recipe));allocation=validate_allocation(recipe['allocation'],active=True)
    if source['config']['schema_version'] not in (2,3) or source['config']['recipe_sha256']!=digest(recipe):
        raise ValueError('recovery requires the original versioned parent recipe')
    if recipe['purpose']!='DEVELOPMENT':raise ValueError('intentional recovery control uses a development recipe')
    expected_cells=schedule(source['config'])
    if (not source['inventory_complete'] or len(source['attempts'])!=len(expected_cells) or
        any(a['status']!='COMPLETED' for a in source['attempts'])):
        raise ValueError('parent development trial must retain its complete schedule before this recovery control')
    first_concurrency,first_pair,first_arm=expected_cells[0]
    parent_first=source['attempts'][0]
    def successful_native_rows(attempt):
        return bool(attempt['requests']) and all(r['status']=='SUCCEEDED' and r['dispatch_ns'] is not None and
            type(r['generated_tokens']) is int and r['generated_tokens']>0 for r in attempt['requests'])
    if not successful_native_rows(parent_first):raise ValueError('parent first cell must contain successful actual native inference')
    expected_requests=len(source['workload']['requests'])
    if expected_requests<4:raise ValueError('recovery control needs at least four requests')
    allocation_start=allocation['started_ns'];deadline=allocation['deadline_ns']
    if deadline-started<1200*10**9:raise ValueError('less than twenty minutes remain; recovery control not started')
    setup=args.setup
    logs=[];children=[]
    env={k:v for k,v in os.environ.items() if not k.startswith('PYTHON')}
    base=[sys.executable,'-I',str(archive)]
    probe=subprocess.run([sys.executable,'-I','-c',
        'import sys; sys.path.insert(0,sys.argv[1]); from lean_model_lab.runner import implementation_digest; print(implementation_digest())',
        str(archive)],cwd=ROOT,env=env,capture_output=True,text=True,timeout=10,check=True)
    if probe.stdout.strip()!=source['config']['implementation_sha256']:
        raise ValueError('recovery archive differs from the main campaign implementation')

    def command(label,*arguments):
        before=time.monotonic_ns()
        result=subprocess.run([*base,*map(str,arguments)],cwd=ROOT,env=env,capture_output=True,text=True,timeout=30)
        write_json_new(root/(label+'.json'),{'started_ns':before,'finished_ns':time.monotonic_ns(),
            'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
        if result.returncode:raise RuntimeError(label+' failed; retained command receipt')
        return json.loads(result.stdout)

    def launch(label,*arguments):
        log=(root/(label+'.log')).open('xb');logs.append(log)
        p=subprocess.Popen([*base,*map(str,arguments)],cwd=ROOT,env=env,stdin=subprocess.DEVNULL,
                           stdout=log,stderr=subprocess.STDOUT)
        children.append(p);return p

    def events():
        return [read_json(p) for p in sorted((study/'events').glob('*.json'))] if (study/'events').exists() else []

    def wait_until(p,predicate,seconds=240):
        cutoff=min(deadline,time.monotonic_ns()+seconds*10**9)
        while time.monotonic_ns()<cutoff:
            value=predicate()
            if value:return value
            if p.poll() is not None:raise RuntimeError('recovery control process exited before required observation')
            time.sleep(.05)
        raise TimeoutError('recovery-control observation or original allocation deadline exhausted')

    try:
        p=launch('initial-run','run','--server',args.server,'--model',args.model,'--setup',setup,
                 '--recipe',args.recipe,'--predecessor',args.parent_study,'--output',study)
        checkpoints=wait_until(p,lambda:[e for e in events() if e['kind']=='checkpoint']
                               if sum(e['kind']=='checkpoint' for e in events())>=2 else None,seconds=600)
        if canonical_bytes(read_json(study/'config.json'))!=canonical_bytes(source['config']):
            raise ValueError('recovery model/backend/workload/hardware/implementation identity differs from parent')
        original_id=checkpoints[0]['payload']['attempt_id']
        process=read_json(study/'raw'/original_id/'process.json')
        os.kill(p.pid,signal.SIGKILL);p.wait(timeout=10)
        cleanup_deadline=time.monotonic()+10
        while _group_members(process['pid']) and time.monotonic()<cleanup_deadline:time.sleep(.05)
        if _group_members(process['pid']):
            raise RuntimeError('owned backend survived parent death; recovery not safe to continue')
        print('Observed parent-death cleanup; completed request checkpoints retained.',flush=True)
        before=command('inspect-after-crash','inspect',study)
        if before['inventory_complete'] or before['terminal_attempt_count']:
            raise RuntimeError('crash did not produce the intended unfinished first attempt')
        journal=study/'journal.jsonl';original_journal_sha=file_digest(journal)
        with journal.open('ab') as stream:
            stream.write(b'{"schema_version":');stream.flush();os.fsync(stream.fileno())
        damaged_journal_sha=file_digest(journal)
        repaired=command('recover-journal','recover-journal',study)
        if not repaired['journal_rebuilt'] or not any(file_digest(f)==damaged_journal_sha for f in (study/'recovery').glob('journal-*.jsonl')):
            raise RuntimeError('journal repair did not retain exact damaged bytes')
        command('reconcile-first-attempt','reconcile',study)
        with Session.open(study) as session:first_inventory=session.inspect()
        first=first_inventory['attempts'][0];first_digest=digest(first)
        observed_before={e['payload']['request']['request_id']:e['payload']['request'] for e in checkpoints}
        retained={r['request_id']:r for r in first['requests']}
        if first['status']!='INTERRUPTED' or any(canonical_bytes(retained[k])!=canonical_bytes(v) for k,v in observed_before.items()):
            raise RuntimeError('reconciliation lost or changed observed checkpoints')
        print('Journal repair and reconciliation retained the interrupted attempt; starting its replacement.',flush=True)
        p=launch('resume-run','resume',study,'--server',args.server,'--model',args.model,'--recipe',args.recipe)
        def restarted_terminal():
            for e in events():
                if e['kind']=='terminal' and e['payload']['attempt_id']!=original_id:
                    a=read_json(study/'attempts'/(e['payload']['attempt_id']+'.json'))
                    if a['status']=='COMPLETED':return a
            return None
        replacement=wait_until(p,restarted_terminal,seconds=1200)
        if replacement['arm']!=first_arm or replacement['concurrency']!=first_concurrency or replacement['pair_index']!=first_pair or len(replacement['requests'])!=expected_requests:
            raise RuntimeError('resume did not complete the expected replacement cell')
        if not successful_native_rows(replacement):
            raise RuntimeError('replacement terminal accounting contains rejected, expired or unsuccessful inference; recovery control did not pass')
        # The full design may have started its next cell; retain its graceful interruption too.
        if p.poll() is None:os.kill(p.pid,signal.SIGINT)
        p.wait(timeout=15)
        if p.returncode not in (0,-signal.SIGINT,128+signal.SIGINT):
            raise RuntimeError('resume exited unexpectedly during controlled stop')
        command('final-reconcile','reconcile',study)
        with Session.open(study) as session:final=session.inspect()
        if not final['inventory_complete'] or digest(next(a for a in final['attempts'] if a['attempt_id']==original_id))!=first_digest:
            raise RuntimeError('resume changed original failed attempt or left unresolved inventory')
        ids=[a['attempt_id'] for a in final['attempts']]
        if len(ids)!=len(set(ids)):raise RuntimeError('duplicate terminal attempt IDs')
        finished=time.monotonic_ns()
        result={'schema_version':2,'status':'PASS','evidence_class':'MEASURED_RECOVERY_CONTROL',
            'scope':'Intentional crash, torn-journal repair, same-boot reconciliation and first-cell restart using the real packaged CLI/model; not a completed extra comparison.',
            'study_schema_version':recipe['schema_version'],'recipe_sha256':digest(recipe),'allocation_id':allocation['allocation_id'],'archive_sha256':file_digest(archive),'original_attempt_id':original_id,'replacement_attempt_id':replacement['attempt_id'],
            'observed_requests_before_crash':len(first['requests']),'replacement_requests':len(replacement['requests']),'successful_replacement_native_requests':sum(r['status']=='SUCCEEDED' for r in replacement['requests']),
            'retained_attempt_count':len(ids),'retained_observed_requests':sum(len(a['requests']) for a in final['attempts']),
            'original_journal_sha256':original_journal_sha,'damaged_journal_sha256':damaged_journal_sha,
            'backend_stopped_on_parent_death':True,'original_attempt_unchanged':True,'unique_terminal_ids':True,
            'resume_exit_code':p.returncode,'stop_semantics':'SIGINT after first replacement terminal; graceful cancellation or KeyboardInterrupt accepted only after final inventory reconciliation',
            'started_ns':started,'finished_ns':finished,'allocation_started_ns':allocation_start,
            'allocation_elapsed_ns':finished-allocation_start,'within_original_allocation':finished<deadline}
        if not result['within_original_allocation']:raise RuntimeError('recovery completed beyond original allocation')
        write_json_new(root/'verification.json',result)
        print(json.dumps(result),flush=True)
        return result
    except BaseException as exc:
        write_json_new(root/'verification-failure.json',{'status':'FAILED','error':type(exc).__name__+': '+str(exc),
            'started_ns':started,'failed_observation_ns':time.monotonic_ns(),'allocation_id':allocation['allocation_id'],
            'scope':'all raw attempts and interrupted work remain retained for reconciliation'})
        raise
    finally:
        for p in children:
            if p.poll() is None:
                p.send_signal(signal.SIGINT)
                try:p.wait(timeout=15)
                except subprocess.TimeoutExpired:p.kill();p.wait(timeout=5)
        # Failure cleanup is limited to backend groups attested by this new study.
        # A different process start time or boot is never a target.
        for path in (study/'raw').glob('*/process.json'):
            record=read_json(path);pid=record['pid']
            if record['boot_id']!=Path('/proc/sys/kernel/random/boot_id').read_text().strip():continue
            try:fields=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()
            except FileNotFoundError:fields=None
            if fields and (fields[19]!=str(record['proc_start_ticks']) or int(fields[2])!=pid or int(fields[3])!=pid):continue
            if _group_members(pid):
                try:os.killpg(pid,signal.SIGTERM)
                except ProcessLookupError:pass
                cutoff=time.monotonic()+3
                while _group_members(pid) and time.monotonic()<cutoff:time.sleep(.05)
                if _group_members(pid):
                    try:os.killpg(pid,signal.SIGKILL)
                    except ProcessLookupError:pass
        for log in logs:log.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('parent-study','archive','server','model','setup','recipe','output'):
        parser.add_argument('--'+name,required=True,type=Path)
    args=parser.parse_args()
    try:verify(args)
    except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as exc:
        print('lean-model-lab recovery control: '+str(exc),file=sys.stderr);raise SystemExit(2)
