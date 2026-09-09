"""Recompute the registered prompt-only transformation from retained study inputs.

This is consistency verification with the frozen implementation, not an
independent algorithm or proof of unchanged model behavior.
"""
from .contracts import ContractError, canonical_bytes, digest, keys, read_json
from .recipes_v3 import prompt_intervention


def verify_interventions(root, inventory, attempt):
    config = inventory['config']
    if config['schema_version'] != 3:
        return None
    path = root/'raw'/attempt['attempt_id']/'prompt-interventions.json'
    if not path.exists() and not attempt['requests']:
        return {'status':'NOT_REACHED', 'scope':'attempt ended before complete prompt preparation'}
    if path.is_symlink() or not path.is_file():
        raise ContractError('v3 native outputs require retained prompt intervention evidence')
    value = read_json(path)
    keys(value, {'schema_version', 'mechanism_id', 'arm', 'scope', 'requests', 'preparation_started_ns', 'preparation_finished_ns'}, 'prompt intervention evidence')
    if (type(value['schema_version']) is not int or value['schema_version'] != 1 or
        value['mechanism_id'] != config['recipe']['mechanism_id'] or value['arm'] != attempt['arm'] or
        value['scope'] != 'syntax/dependency checks only; no LLM output guarantee; preparation precedes offered arrivals and is charged in full wall'):
        raise ContractError('intervention evidence scope or mechanism differs')
    workload = inventory['workload']
    if type(value['requests']) is not list or len(value['requests']) != len(workload['requests']):
        raise ContractError('intervention evidence requires the complete frozen population')
    start=value['preparation_started_ns'];finish=value['preparation_finished_ns']
    if (type(start) is not int or type(finish) is not int or
        not attempt['started_ns'] <= start <= finish <= attempt['service_started_ns']):
        raise ContractError('invalid retained preparation envelope')
    total = 0
    for source, row in zip(workload['requests'], value['requests']):
        keys(row, {'request_id','input_prompt_sha256','result','duration_ns'}, 'prompt intervention record')
        if row['request_id'] != source['request_id'] or row['input_prompt_sha256'] != digest(source['prompt']):
            raise ContractError('intervention source identity differs')
        if type(row['duration_ns']) is not int or row['duration_ns'] < 0:
            raise ContractError('invalid observed intervention duration')
        expected = prompt_intervention(source['prompt'], config['recipe']['mechanism_id'], attempt['arm'], config['recipe'].get('controller'))
        if canonical_bytes(row['result']) != canonical_bytes(expected):
            raise ContractError('retained transformation differs from registered prompt-only implementation')
        total += row['duration_ns']
    if total > finish-start or total > attempt['overhead_ns']['cache_preparation']:
        raise ContractError('prompt intervention cost exceeds its preparation phase')
    return {'status':'CONSISTENT', 'total_intervention_ns':total,
            'scope':'Recomputed prompt-only transformation; no independent authenticity or output guarantee.',
            'requests':value['requests']}
