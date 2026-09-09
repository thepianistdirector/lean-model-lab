"""Explicit same-boot reconciliation and restart; interrupted attempts stay retained."""
from __future__ import annotations

import time
import uuid
from pathlib import Path

from . import __version__
from .artifacts import write_json_new
from .contracts import ContractError,digest,read_json
from .evidence import OVERHEAD_KEYS
from .runner import _group_members,execute_attempt,hardware,implementation_digest


def current_boot() -> str:
    return Path('/proc/sys/kernel/random/boot_id').read_text().strip()


def reconcile_unfinished(session) -> list[str]:
    inventory=session.inspect();config=inventory['config']
    if inventory['journal_recovery_required']:session.recover_journal();inventory=session.inspect()
    if not inventory['unresolved_attempts']:return []
    if config['clock']['boot_id']!=current_boot():
        raise ContractError('reboot changed the monotonic clock; preserve unfinished observations for explicit cross-boot review')
    if config['evidence_class']=='MEASURED' and config['hardware']!=hardware():
        raise ContractError('recovery hardware differs from the frozen study')
    recovered=[]
    for row in inventory['unresolved_attempts']:
        raw=session.root/'raw'/row['attempt_id'];process_file=raw/'process.json'
        if process_file.exists():
            process=read_json(process_file)
            if process['boot_id']==current_boot():
                stat=Path(f"/proc/{process['pid']}/stat")
                try:fields=stat.read_text().rsplit(')',1)[1].split()
                except FileNotFoundError:fields=None
                if fields and fields[19]==str(process['proc_start_ticks']) and fields[0]!='Z':
                    raise ContractError('recorded backend is still running; no recovery mutation or restart performed')
                if fields is None and _group_members(process['pid']):
                    raise ContractError('recorded process group has surviving members; original cleanup must finish first')
        if row['state']=='PENDING_PUBLICATION':
            attempt=row['pending_attempt'];cutoff=attempt['finished_ns']
        else:
            cutoff=time.monotonic_ns();requests=[c['request'] for c in row['checkpoints']]
            expected={r['request_id']:r for r in inventory['workload']['requests']}
            service_start=(requests[0]['arrival_ns']-expected[requests[0]['request_id']]['arrival_offset_ns']) if requests else cutoff
            overhead={key:0 for key in OVERHEAD_KEYS}
            overhead['service']=max((r['completed_ns']-service_start for r in requests),default=0)
            if config['schema_version'] == 3 and (raw/'prompt-interventions.json').is_file():
                preparation=read_json(raw/'prompt-interventions.json')
                start=preparation.get('preparation_started_ns');finish=preparation.get('preparation_finished_ns')
                if type(start) is not int or type(finish) is not int or not row['started_ns'] <= start <= finish <= service_start:
                    raise ContractError('retained preparation envelope is invalid')
                overhead['cache_preparation']=finish-start
            unavailable={'status':'UNAVAILABLE','scope':'not observed across interrupted coordinator interval',
                         'value':None,'unit':'unavailable'}
            attempt={'schema_version':config['schema_version'],'evidence_class':config['evidence_class'],'attempt_id':row['attempt_id'],
                'config_sha256':digest(config),'workload_sha256':inventory['workload_sha256'],
                'arm':row['arm'],'concurrency':row['concurrency'],'pair_index':row['pair_index'],
                'started_ns':row['started_ns'],'service_started_ns':service_start,'finished_ns':cutoff,
                'status':'INTERRUPTED','requests':requests,'overhead_ns':overhead,
                'environment':{'observer':'same-boot recovery coordinator; no new engine observations',
                    'version':__version__,**config['hardware'],
                    **{key:dict(unavailable) for key in ('load','thermal','memory','energy')}}}
            write_json_new(raw/('reconciliation-'+uuid.uuid4().hex+'.json'),{'closed_at_ns':cutoff,
                'known_observed_until_ns':row['observed_until_ns'],
                'wall_scope':'reservation through explicit closure, including unavailable/idle interval',
                'service_scope':'retained completed requests only; unobserved work remains unattributed',
                **({'preparation_scope':'retained timed transformation/tokenization envelope only; subsequent receipt write and other unknown phases remain unattributed'} if config['schema_version']==3 else {}),
                'missing_request_ids':row['unaccounted_request_ids'],'inference_restarted':False})
        session.publish(attempt)
        session.record_setup({'phase':'recovery-reconciliation','status':'COMPLETED',
            'started_ns':cutoff,'finished_ns':time.monotonic_ns(),'bytes_acquired':0,
            'details':'retained interrupted/publication attempt; recovery wait, raw hashing and finalization'})
        recovered.append(row['attempt_id'])
    return recovered


def resume_study(*, study: Path, server: Path, model: Path, admission: dict | None=None,recipe: dict | None=None) -> dict:
    from .admission import validate_admission
    from .config import LIMITS
    from .resources import heavy_job,require_workspace_root
    from .session import Session
    if recipe is None:validate_admission(admission)
    else:
        from .recipes import validate_recipe
        from .allocation import validate_allocation
        validate_recipe(recipe);validate_allocation(recipe['allocation'],active=True)
    root=require_workspace_root(study,server,model)
    with heavy_job(root),Session.open(study) as session:
        inventory=session.inspect();config=inventory['config']
        if config['evidence_class']!='MEASURED':raise ContractError('CLI resume only admits the real reviewed backend')
        if config['clock']['boot_id']!=current_boot():raise ContractError('cannot resume across a reboot with the old clock/allocation')
        if config['implementation_sha256']!=implementation_digest():
            raise ContractError('use the original frozen implementation to resume this study')
        records=inventory['setup_accounting']['records']
        if not records:raise ContractError('setup allocation is unknown')
        deadline=min(r['started_ns'] for r in records)+LIMITS['full_wall_seconds']*10**9
        if config['schema_version'] in (2,3):
            if recipe is None or digest(recipe)!=config['recipe_sha256']:raise ContractError('resume requires the original frozen recipe')
            deadline=config['recipe']['allocation']['deadline_ns']
        elif recipe is not None:raise ContractError('legacy resume requires legacy admission')
        if time.monotonic_ns()>=deadline:raise ContractError('original full-wall allocation exhausted; no automatic extension')
        reconcile_unfinished(session);inventory=session.inspect()
        completed={(a['concurrency'],a['pair_index'],a['arm']) for a in inventory['attempts'] if a['status']=='COMPLETED'}
        from .recipes import schedule
        for concurrency,pair,arm in schedule(config):
            if (concurrency,pair,arm) in completed:continue
            attempt=execute_attempt(session,server=server.resolve(strict=True),model=model.resolve(strict=True),
                config=config,workload=inventory['workload'],concurrency=concurrency,pair_index=pair,
                arm=arm,deadline_ns=deadline,project_root=root)
            if attempt['status']!='COMPLETED':return session.inspect()
        return session.inspect()
