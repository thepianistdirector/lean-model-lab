"""Finite operator allocations shared across preparation, execution and recovery.

Approval metadata is an operator record, not a signature or isolation boundary.
"""
from __future__ import annotations
import re
import time
from pathlib import Path
from .contracts import ContractError,integer,keys

MAXIMUM={'full_wall_seconds':43200,'disk_bytes':200_000_000_000,
         'memory_bytes':60_000_000_000,'compute_threads':12,'max_heavy_jobs':1}


def validate_allocation(value, *, active=False, fixture=False):
    keys(value,{'schema_version','allocation_id','approved','approval_reference','observed_utc',
                'boot_id','started_ns','deadline_ns','limits','scope'},'allocation')
    integer(value['schema_version'],2,2,'allocation.schema_version')
    if value['approved'] is not True:raise ContractError('allocation is not operator-approved')
    if type(value['allocation_id']) is not str or not re.fullmatch('[A-Za-z0-9._-]{1,80}',value['allocation_id']):
        raise ContractError('allocation ID must be a bounded identifier, not a path')
    for key in ('approval_reference','observed_utc','scope'):
        if type(value[key]) is not str or not value[key].strip() or value[key].startswith('PENDING'):
            raise ContractError('allocation needs actual '+key)
    boot=value['boot_id']
    if not (fixture and boot=='TEST_FIXTURE') and (type(boot) is not str or not re.fullmatch('[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',boot)):
        raise ContractError('allocation requires exact Linux boot identity')
    keys(value['limits'],set(MAXIMUM),'allocation.limits')
    for name,ceiling in MAXIMUM.items():integer(value['limits'][name],1,ceiling,'allocation.limits.'+name)
    integer(value['started_ns'],1,2**63-1,'allocation.started_ns')
    integer(value['deadline_ns'],1,2**63-1,'allocation.deadline_ns')
    if value['deadline_ns']!=value['started_ns']+value['limits']['full_wall_seconds']*10**9:
        raise ContractError('allocation deadline differs from its original start and duration')
    if active:
        if fixture:raise ContractError('fixture allocation cannot execute inference')
        if boot!=Path('/proc/sys/kernel/random/boot_id').read_text().strip():
            raise ContractError('allocation belongs to another boot')
        if not value['started_ns']<=time.monotonic_ns()<value['deadline_ns']:
            raise ContractError('original allocation is not active; no automatic restart or extension')
    return value


def runtime_limits(allocation):
    value=validate_allocation(allocation,fixture=type(allocation) is dict and allocation.get('boot_id')=='TEST_FIXTURE')
    return {k:v for k,v in value['limits'].items() if k!='compute_threads'} | {
        'request_timeout_seconds':300,'startup_timeout_seconds':600}


def make_allocation(*,full_wall_seconds,disk_bytes,memory_bytes,compute_threads,approval_reference):
    """Record an explicit local operator assertion; does not authenticate an owner."""
    import datetime
    import uuid
    started=time.monotonic_ns()
    value={'schema_version':2,'allocation_id':'allocation-'+uuid.uuid4().hex,'approved':True,
        'approval_reference':approval_reference,'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'started_ns':started,
        'deadline_ns':started+full_wall_seconds*10**9,
        'limits':{'full_wall_seconds':full_wall_seconds,'disk_bytes':disk_bytes,'memory_bytes':memory_bytes,
                  'compute_threads':compute_threads,'max_heavy_jobs':1},
        'scope':'Operator-declared local allocation; preparation, execution, failure, recovery and intervening wall count. No automatic reset, paid cloud/GPU or publication authority.'}
    return validate_allocation(value,active=True)
