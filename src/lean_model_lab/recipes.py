"""Versioned, immutable experiment recipes for reviewed CPU model profiles."""
from __future__ import annotations
import copy
from .allocation import validate_allocation
from .contracts import ContractError,canonical_bytes,digest,integer,keys,validate_workload
from .config import ENGINE,EVALUATION
from .profiles import get_model_profile
from .workloads import make_workload_v2

RECIPE_KEYS={'schema_version','model_profile_id','model_profile_sha256','workload_generator',
             'workload_sha256','engine','evaluation','allocation','purpose'}


def make_recipe(*,model_profile_id,workload,allocation,compute_threads=None,pair_count=4,
                purpose='MEASUREMENT',ttft_slo_ns=15_000_000_000,end_to_end_slo_ns=30_000_000_000):
    validate_workload(workload)
    if workload['schema_version']!=2:raise ContractError('recipe requires v2 workload; legacy workload remains a separate immutable contract')
    validate_allocation(allocation,fixture=type(allocation) is dict and allocation.get('boot_id')=='TEST_FIXTURE')
    profile=get_model_profile(model_profile_id)
    if compute_threads is None:compute_threads=allocation['limits']['compute_threads']
    integer(compute_threads,1,allocation['limits']['compute_threads'],'compute_threads')
    integer(pair_count,2,8,'pair_count')
    if pair_count%2:raise ContractError('v2 paired order requires an even number of AB/BA pairs')
    if purpose not in ('DEVELOPMENT','MEASUREMENT'):raise ContractError('recipe purpose must distinguish development from measurement')
    if purpose=='MEASUREMENT' and len(workload['requests'])<128:
        raise ContractError('measurement recipes require at least128requests; smaller populations are development controls')
    for name,value in [('ttft_slo_ns',ttft_slo_ns),('end_to_end_slo_ns',end_to_end_slo_ns)]:
        integer(value,1,3600*10**9,name)
    if ttft_slo_ns>end_to_end_slo_ns:raise ContractError('TTFT SLO cannot exceed end-to-end SLO')
    if workload['requests'][-1]['arrival_offset_ns']>=allocation['limits']['full_wall_seconds']*10**9:
        raise ContractError('arrival trace alone exceeds the full allocation')
    if sum(f['bytes'] for f in profile['files'])>=allocation['limits']['memory_bytes']:
        raise ContractError('reviewed model weights leave no memory headroom')
    engine=copy.deepcopy(ENGINE);engine['compute_threads']=compute_threads
    engine['http_threads']=max(4,max(workload['concurrency_modes']))
    engine['cpu_affinity_policy']='first_available_compute_thread_count'
    evaluation=copy.deepcopy(EVALUATION)
    evaluation.update(pairs_per_concurrency=pair_count,pair_order=['AB' if p%2==0 else 'BA' for p in range(pair_count)],
        concurrency_modes=list(workload['concurrency_modes']),ttft_slo_ns=ttft_slo_ns,end_to_end_slo_ns=end_to_end_slo_ns,
        scheduler='deterministic_lane_affinity',queue_policy='bounded_drop_tail',
        deadline_policy='expire_before_dispatch; in-flight completion lateness retained and evaluated against SLOs')
    return {'schema_version':2,'model_profile_id':model_profile_id,'model_profile_sha256':digest(profile),
        'workload_generator':copy.deepcopy(workload['generator']),'workload_sha256':digest(workload),
        'engine':engine,'evaluation':evaluation,'allocation':copy.deepcopy(allocation),'purpose':purpose}


def workload_from_recipe(recipe):
    if recipe.get('schema_version') == 3:
        from .recipes_v3 import workload_from_recipe_v3
        return workload_from_recipe_v3(recipe)
    return make_workload_v2(**recipe['workload_generator'])


def validate_recipe(value):
    if type(value) is dict and type(value.get('schema_version')) is int and value['schema_version'] == 3:
        from .recipes_v3 import validate_recipe_v3
        return validate_recipe_v3(value)
    keys(value,RECIPE_KEYS,'recipe')
    if type(value['schema_version']) is not int or value['schema_version']!=2:raise ContractError('unsupported recipe version')
    if type(value['engine']) is not dict or type(value['evaluation']) is not dict:raise ContractError('recipe engine/evaluation must be objects')
    try:
        expected=make_recipe(model_profile_id=value['model_profile_id'],workload=workload_from_recipe(value),
            allocation=value['allocation'],compute_threads=value['engine']['compute_threads'],
            pair_count=value['evaluation']['pairs_per_concurrency'],purpose=value['purpose'],
            ttft_slo_ns=value['evaluation']['ttft_slo_ns'],end_to_end_slo_ns=value['evaluation']['end_to_end_slo_ns'])
    except (KeyError,TypeError) as exc:raise ContractError('incomplete or malformed recipe') from exc
    if canonical_bytes(value)!=canonical_bytes(expected):raise ContractError('recipe differs from reviewed model/workload/runtime/evaluation controls')
    return value


def schedule(config):
    """Single authority for every registered cell, used by runner/recovery/evaluator."""
    evaluation=config['evaluation']
    return [(c,p,arm) for c in evaluation['concurrency_modes']
        for p,order in enumerate(evaluation['pair_order'])
        for arm in (('baseline','candidate') if order=='AB' else ('candidate','baseline'))]
