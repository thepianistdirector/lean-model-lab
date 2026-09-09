"""Frozen configuration for the single admitted model, adapter and policy family."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .contracts import ContractError, canonical_bytes, digest, keys, make_workload
from .llama_adapter import BACKEND_COMMIT, BACKEND_PATCH_SHA256, MODEL_COMMIT, MODEL_SHA256, render_prompt

ENGINE = {'compute_threads':2, 'http_threads':4, 'context_per_slot':2048,
          'cache_ram_mib':0, 'cache_idle_slots':False, 'kv_unified':False,
          'cache_reuse':0, 'context_shift':False, 'gpu_layers':0, 'device':'none',
          'continuous_batching':True, 'warmup':False}
EVALUATION = {'accuracy_minimum':0.95, 'practical_throughput_gain':0.05,
              'maximum_tail_regression':0.10, 'pairs_per_concurrency':3,
              'pair_order':['AB','BA','AB'], 'concurrency_modes':[1,4],
              'uncertainty':'descriptive_pair_range', 'output_token_parity':True}
LIMITS = {'full_wall_seconds':7200, 'disk_bytes':5*1024**3, 'memory_bytes':4*1024**3,
          'max_heavy_jobs':1, 'request_timeout_seconds':120, 'startup_timeout_seconds':180}


def _sha(value: Any, label: str) -> None:
    if type(value) is not str or not re.fullmatch('[0-9a-f]{64}',value):
        raise ContractError(f'{label} must be an exact SHA-256 digest')


def make_config(*, server_sha256: str, evidence_class: str, hardware: dict,
                implementation_sha256: str = '0'*64) -> dict:
    return {'schema_version':1, 'study_id':'qwen05-fp16-prefix-cache-v1',
            'evidence_class':evidence_class,
            'clock':{'kind':'monotonic_ns','boot_id':(Path('/proc/sys/kernel/random/boot_id').read_text().strip()
                      if evidence_class=='MEASURED' else 'TEST_FIXTURE')},
            'model':{'repository':'Qwen/Qwen2.5-0.5B-Instruct-GGUF','revision':MODEL_COMMIT,
                     'gguf_sha256':MODEL_SHA256,'precision':'FP16','license':'Apache-2.0'},
            'tokenizer':{'gguf_sha256':MODEL_SHA256,
                         'template_sha256':digest(render_prompt('{PROMPT}'))},
            'backend':{'repository':'ggml-org/llama.cpp','revision':BACKEND_COMMIT,
                       'version':'v0.2.0','server_sha256':server_sha256,
                       'source_patch_sha256':BACKEND_PATCH_SHA256},
            'implementation_sha256':implementation_sha256,
            'hardware':dict(hardware), 'workload_sha256':digest(make_workload()),
            'engine':dict(ENGINE),
            'sampling':{'samplers':['temperature'],'temperature':0,'seed':20260907,
                        'max_output_tokens':32,'allow_eos':True,'stop':[]},
            'candidate':{'field':'cache_prompt','baseline':False,'candidate':True},
            'evaluation':dict(EVALUATION), 'limits':dict(LIMITS)}


def validate_config(value: Any) -> dict:
    if type(value) is dict and type(value.get("schema_version")) is int and value["schema_version"] in (2, 3):
        return validate_config_v2(value)
    keys(value, {'schema_version','study_id','evidence_class','clock','model','tokenizer','backend',
                 'implementation_sha256','hardware','workload_sha256','engine','sampling',
                 'candidate','evaluation','limits'},'configuration')
    if value['evidence_class'] not in ('TEST_FIXTURE','MEASURED'):
        raise ContractError('configuration evidence class must be explicit')
    keys(value['backend'],{'repository','revision','version','server_sha256','source_patch_sha256'},'backend')
    keys(value['hardware'],{'platform','cpu'},'hardware')
    for key in ('platform','cpu'):
        if type(value['hardware'][key]) is not str or not value['hardware'][key].strip():
            raise ContractError(f'hardware.{key} must be a nonempty string')
    if value['evidence_class']=='MEASURED' and value['hardware']['platform']!='Linux-x86_64':
        raise ContractError('only the reviewed Linux CPU environment can be admitted')
    _sha(value['backend']['server_sha256'],'server_sha256')
    _sha(value['implementation_sha256'],'implementation_sha256')
    if value['evidence_class']=='MEASURED' and value['implementation_sha256']=='0'*64:
        raise ContractError('measured evidence requires implementation identity')
    expected=make_config(server_sha256=value['backend']['server_sha256'],
                         evidence_class=value['evidence_class'],hardware=value['hardware'],
                         implementation_sha256=value['implementation_sha256'])
    keys(value['clock'],{'kind','boot_id'},'clock')
    if value['evidence_class']=='MEASURED':
        if type(value['clock']['boot_id']) is not str or not re.fullmatch('[0-9a-f-]{36}',value['clock']['boot_id']):
            raise ContractError('measured clock requires Linux boot identity')
        expected['clock']['boot_id']=value['clock']['boot_id']
    if canonical_bytes(value)!=canonical_bytes(expected):
        raise ContractError('configuration differs from the fixed model/tokenizer/backend/cache/quality contract')
    return value


def make_config_v2(*,recipe: dict,server_sha256: str,evidence_class: str,hardware: dict,
                   implementation_sha256: str) -> dict:
    from .recipes import validate_recipe
    from .profiles import get_model_profile
    from .allocation import runtime_limits
    import copy
    validate_recipe(recipe);profile=get_model_profile(recipe['model_profile_id'])
    first=profile['files'][0]
    config=make_config(server_sha256=server_sha256,evidence_class=evidence_class,hardware=hardware,
                       implementation_sha256=implementation_sha256)
    config.update(schema_version=recipe['schema_version'],study_id='recipe-'+digest(recipe)[:16],recipe=copy.deepcopy(recipe),
        recipe_sha256=digest(recipe),model={'repository':profile['repository'],'revision':profile['revision'],
            'gguf_sha256':first['sha256'],'precision':profile['precision'],'license':profile['license'],
            'profile_id':profile['profile_id'],'profile_sha256':digest(profile),'artifacts':copy.deepcopy(profile['files'])},
        tokenizer={'gguf_sha256':first['sha256'],'model_profile_sha256':digest(profile),
            'template_sha256':profile['template_sha256']},workload_sha256=recipe['workload_sha256'],
        engine=copy.deepcopy(recipe['engine']),evaluation=copy.deepcopy(recipe['evaluation']),
        limits=runtime_limits(recipe['allocation']))
    config['sampling']['max_output_tokens']=recipe['workload_generator']['max_output_tokens']
    config['sampling']['seed']=recipe['workload_generator']['seed']
    if recipe['schema_version'] == 3:
        config['candidate'] = {'mechanism_id': recipe['mechanism_id'], 'baseline': 'full-context-v1',
            'scope': 'registered prompt intervention; task quality is independently evaluated'}
    if evidence_class=='MEASURED':config['clock']['boot_id']=recipe['allocation']['boot_id']
    return config


def validate_config_v2(value: Any) -> dict:
    from .recipes import validate_recipe
    required=set(make_config(server_sha256='0'*64,evidence_class='TEST_FIXTURE',hardware={'platform':'fixture','cpu':'fixture'}))|{'recipe','recipe_sha256'}
    keys(value,required,'configuration v2')
    validate_recipe(value['recipe'])
    if value['evidence_class'] not in ('TEST_FIXTURE','MEASURED'):raise ContractError('configuration evidence class must be explicit')
    keys(value['backend'],{'repository','revision','version','server_sha256','source_patch_sha256'},'backend')
    keys(value['hardware'],{'platform','cpu'},'hardware')
    for key in ('platform','cpu'):
        if type(value['hardware'][key]) is not str or not value['hardware'][key].strip():raise ContractError('invalid hardware identity')
    if value['evidence_class']=='MEASURED' and value['hardware']['platform']!='Linux-x86_64':raise ContractError('only reviewed Linux CPU execution is admitted')
    _sha(value['backend']['server_sha256'],'server_sha256');_sha(value['implementation_sha256'],'implementation_sha256')
    if value['evidence_class']=='MEASURED' and (value['implementation_sha256']=='0'*64 or value['recipe']['allocation']['boot_id']=='TEST_FIXTURE'):
        raise ContractError('measured configuration requires actual implementation and allocation clock')
    expected=make_config_v2(recipe=value['recipe'],server_sha256=value['backend']['server_sha256'],
        evidence_class=value['evidence_class'],hardware=value['hardware'],implementation_sha256=value['implementation_sha256'])
    if canonical_bytes(value)!=canonical_bytes(expected):raise ContractError('configuration differs from its frozen recipe or reviewed artifacts')
    return value
