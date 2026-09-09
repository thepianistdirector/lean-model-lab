"""Setup receipt validation; artifacts cannot be executed before receipt checks."""
from __future__ import annotations

import re
import time
from pathlib import Path

from .contracts import ContractError, keys
from .llama_adapter import BACKEND_COMMIT, BACKEND_PATCH_SHA256, MODEL_SHA256


def validate_receipt(receipt: dict, *, boot_id: str | None = None,recipe: dict | None=None) -> dict:
    if type(receipt) is dict and type(receipt.get('schema_version')) is int and receipt['schema_version']==2:
        return validate_receipt_v2(receipt,boot_id=boot_id,recipe=recipe)
    keys(receipt,{'schema_version','boot_id','records','artifacts'},'setup receipt')
    if type(receipt['schema_version']) is not int or receipt['schema_version']!=1:
        raise ContractError('unsupported setup receipt version')
    if boot_id is None:boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    if receipt['boot_id']!=boot_id:
        raise ContractError('setup monotonic clock belongs to another boot; resource reconciliation required')
    artifacts=receipt['artifacts']
    keys(artifacts,{'backend_revision','backend_patch_sha256','server_sha256','model_sha256'},'setup artifacts')
    if (artifacts['backend_revision']!=BACKEND_COMMIT or artifacts['model_sha256']!=MODEL_SHA256 or
        artifacts['backend_patch_sha256']!=BACKEND_PATCH_SHA256):
        raise ContractError('setup artifacts differ from approved model/backend')
    if type(artifacts['server_sha256']) is not str or not re.fullmatch('[0-9a-f]{64}',artifacts['server_sha256']):
        raise ContractError('setup receipt must bind exact compiled server bytes')
    records=receipt['records']
    if type(records) is not list or not records:raise ContractError('setup accounting is required')
    previous=0;now=time.monotonic_ns()
    for record in records:
        keys(record,{'phase','status','started_ns','finished_ns','bytes_acquired','details'},'setup record')
        if record['status'] not in ('COMPLETED','FAILED','INTERRUPTED'):
            raise ContractError('invalid setup terminal status')
        for name in ('phase','details'):
            if type(record[name]) is not str or not record[name].strip():raise ContractError('missing setup '+name)
        for name in ('started_ns','finished_ns','bytes_acquired'):
            if type(record[name]) is not int or record[name]<0:raise ContractError('invalid setup '+name)
        if not previous<=record['started_ns']<record['finished_ns']<=now:
            raise ContractError('setup records overlap, run backwards or claim future time')
        previous=record['finished_ns']
    required={'source-acquisition','model-acquisition','build'}
    if not required<={r['phase'] for r in records if r['status']=='COMPLETED'}:
        raise ContractError('setup receipt lacks completed source/model/build phases')
    return receipt


def validate_receipt_v2(receipt,*,boot_id=None,recipe=None):
    from .allocation import validate_allocation
    from .profiles import get_model_profile
    from .recipes import validate_recipe
    from .contracts import canonical_bytes,digest,integer
    from .session import validate_setup_records
    keys(receipt,{'schema_version','boot_id','allocation','records','artifacts','resource_observations'},'v2 setup receipt')
    integer(receipt['schema_version'],2,2,'setup.schema_version')
    validate_allocation(receipt['allocation'])
    if boot_id is None:boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip()
    if receipt['boot_id']!=boot_id or receipt['allocation']['boot_id']!=boot_id:raise ContractError('setup belongs to another boot/allocation clock')
    artifacts=receipt['artifacts']
    keys(artifacts,{'backend_revision','backend_patch_sha256','server_sha256','model_profile_id','model_profile_sha256'},'v2 setup artifacts')
    profile=get_model_profile(artifacts['model_profile_id'])
    if artifacts['model_profile_sha256']!=digest(profile) or artifacts['backend_revision']!=BACKEND_COMMIT or artifacts['backend_patch_sha256']!=BACKEND_PATCH_SHA256:
        raise ContractError('setup artifact profile differs from reviewed pins')
    if type(artifacts['server_sha256']) is not str or not re.fullmatch('[0-9a-f]{64}',artifacts['server_sha256']):raise ContractError('setup lacks exact compiled binary identity')
    records=validate_setup_records(receipt['records']);now=time.monotonic_ns()
    if not records or min(r['started_ns'] for r in records)<receipt['allocation']['started_ns'] or max(r['finished_ns'] for r in records)>min(now,receipt['allocation']['deadline_ns']):
        raise ContractError('setup intervals escape original allocation or claim future observations')
    required={'source-acquisition','model-acquisition','build'}
    if not required<={r['phase'] for r in records if r['status']=='COMPLETED'}:raise ContractError('setup lacks completed source/model/build phases')
    observation=receipt['resource_observations'];keys(observation,{'maximum_observed_aggregate_rss_bytes','scope'},'setup resources')
    integer(observation['maximum_observed_aggregate_rss_bytes'],1,receipt['allocation']['limits']['memory_bytes'],'setup peak RSS')
    if type(observation['scope']) is not str or not observation['scope'].strip():raise ContractError('setup resource scope missing')
    if recipe is not None:
        validate_recipe(recipe)
        if (recipe['model_profile_id']!=profile['profile_id'] or recipe['model_profile_sha256']!=digest(profile) or
            canonical_bytes(recipe['allocation'])!=canonical_bytes(receipt['allocation'])):
            raise ContractError('recipe differs from prepared model or original allocation')
    return receipt
