"""Native protocol consistency checks shared by reports and the workbench."""
from pathlib import Path
from .artifacts import read_journal
from .contracts import canonical_bytes, digest, parse_json, read_json
from .llama_adapter import BACKEND_COMMIT, BACKEND_PATCH_SHA256, normalize_response

class NativeEvidenceError(ValueError):
    pass

def _ref(document: str, pointer: str = '') -> dict:
    return {'document': document, 'pointer': pointer}


def _unavailable(reason: str) -> dict:
    return {'status': 'UNAVAILABLE', 'value': None, 'reason': reason}


def native_evidence(root: Path, inventory: dict, attempt: dict) -> dict:
    """Replay only the supported native protocol; never infer cache from the arm."""
    backend = inventory['config']['backend']
    if (backend.get('repository') != 'ggml-org/llama.cpp' or
            backend.get('revision') != BACKEND_COMMIT or
            backend.get('source_patch_sha256') != BACKEND_PATCH_SHA256):
        return {}
    directory = root / 'raw' / attempt['attempt_id']
    intervention_by_id = {}
    if inventory['config']['schema_version'] == 3:
        from .intervention_evidence import verify_interventions
        verified = verify_interventions(root, inventory, attempt)
        intervention_by_id = {row['request_id']: row for row in verified.get('requests', [])}
    token_path = directory / 'tokenized-inputs.json'
    indices = {r['request_id']: i for i, r in enumerate(inventory['workload']['requests'])}
    has_streams = any((directory / (identifier + '.jsonl')).exists() for identifier in indices)
    if not token_path.exists() and not has_streams:
        return {}
    if not token_path.exists():
        raise NativeEvidenceError('native streams lack retained tokenizer evidence')
    tokens = read_json(token_path)
    if (type(tokens) is not dict or set(tokens) != {'workload_sha256', 'tokens'} or
            tokens['workload_sha256'] != inventory['workload_sha256'] or
            type(tokens['tokens']) is not list or len(tokens['tokens']) != len(indices) or
            any(type(row) is not list or not row or any(type(t) is not int or t < 0 for t in row)
                for row in tokens['tokens'])):
        raise NativeEvidenceError('native tokenizer evidence differs from workload')
    result = {}
    for request in attempt['requests']:
        identifier = request['request_id']
        index = indices[identifier]
        source = f"raw/{attempt['attempt_id']}/{identifier}.jsonl"
        item = {'input_token_ids': tokens['tokens'][index],
                'input_tokens_source': _ref(f"raw/{attempt['attempt_id']}/tokenized-inputs.json", f'/tokens/{index}'),
                'cache': _unavailable('failed or cancelled response has no reconciled terminal cache accounting')}
        if identifier in intervention_by_id:
            item['prompt_intervention'] = intervention_by_id[identifier]
        result[identifier] = item
        if request['status'] != 'SUCCEEDED':
            continue
        path = directory / (identifier + '.jsonl')
        if not path.is_file():
            raise NativeEvidenceError('successful native request lacks retained response')
        receipts, torn = read_journal(path)
        if torn or any('error' in row for row in receipts):
            raise NativeEvidenceError('successful native response is torn or contains an error')
        records = [(row['observed_ns'], parse_json(row['data_utf8'])) for row in receipts
                   if 'data_utf8' in row and row['data_utf8'] != '[DONE]']
        normalized = normalize_response(records, request_id=identifier,
            arrival_ns=request['arrival_ns'], admitted_ns=request['admitted_ns'],
            dispatch_ns=request['dispatch_ns'], completed_ns=request['completed_ns'],
            prompt_tokens=len(tokens['tokens'][index]), slot=index % attempt['concurrency'],
            **({'seed': inventory['config']['sampling']['seed'],
                'max_output_tokens': inventory['config']['sampling']['max_output_tokens']}
               if inventory['config']['schema_version'] >= 2 else {}))
        if canonical_bytes(normalized) != canonical_bytes(request):
            raise NativeEvidenceError('native response differs from normalized request')
        timings = records[-1][1].get('timings', {})
        if type(timings) is not dict or any(type(timings.get(key)) is not int or timings[key] < 0
               for key in ('cache_n', 'prompt_n', 'predicted_n')):
            raise NativeEvidenceError('native cache accounting is missing or malformed')
        progress = [row['prompt_progress'] for _, row in records if 'prompt_progress' in row]
        if inventory['config']['schema_version'] == 3:
            from .recipes_v3 import cache_enabled
            cache_allowed=cache_enabled(inventory['config']['recipe'],attempt['arm'])
        else:cache_allowed=attempt['arm']=='candidate'
        if (timings['cache_n'] + timings['prompt_n'] != request['prompt_tokens'] or
                timings['predicted_n'] != request['generated_tokens'] or
                (not cache_allowed and timings['cache_n'] != 0) or
                not progress or any(p['cache'] != timings['cache_n'] for p in progress)):
            raise NativeEvidenceError('native cache accounting does not reconcile')
        item['cache'] = {'status': 'RECONCILED_NATIVE', 'reused_input_tokens': timings['cache_n'],
                         'new_input_tokens': timings['prompt_n'], 'source': _ref(source),
                         'scope': 'native terminal timings reconciled with progress and normalized response'}
        item['normalized_replay'] = {'status': 'PASS', 'source': _ref(source)}
    return result


def verify_native_inventory(root, inventory):
    root=Path(root)
    identities={};reconciled=0
    config=inventory['config']
    changed_inputs=config['schema_version']==3 and not config['evaluation']['output_token_parity']
    for attempt in inventory['attempts']:
        observations=native_evidence(root,inventory,attempt)
        successful={r['request_id'] for r in attempt['requests'] if r['status']=='SUCCEEDED'}
        if not successful <= set(observations):
            raise NativeEvidenceError('successful measured requests lack raw native evidence')
        for identifier,observation in observations.items():
            key=(attempt['arm'],identifier) if changed_inputs else identifier
            identity=digest(observation['input_token_ids'])
            if key in identities and identities[key]!=identity:
                raise NativeEvidenceError('native input token identities drifted within the declared comparison semantics')
            identities[key]=identity
            if identifier in successful:
                if observation.get('normalized_replay',{}).get('status')!='PASS':
                    raise NativeEvidenceError('successful request lacks normalized raw replay')
                reconciled+=1
    return {'status':'CONSISTENT','successful_requests_reconciled':reconciled,
            'scope':'Raw/native/transformation consistency; local hashes do not establish independent authenticity.'}
