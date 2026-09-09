"""Native llama.cpp SSE normalization for the one reviewed CPU cache policy.

This module does not start a backend or retrieve artifacts. Raw records remain
separate from normalized evidence. Tests use explicit fabricated API fixtures.
"""
from __future__ import annotations

import math

from .contracts import ContractError, SEED, integer

BACKEND_COMMIT = 'bb4caa7540188872173c44d161602d9271386413'
BACKEND_PATCH_FILENAME = 'llama-cpp-v0.2.0-gcc8-ctad.patch'
BACKEND_PATCH_SHA256 = '598d10a911e4d9c33926bd2dfd75735d143b84db14ad644a7502f35bec8e0f1c'
MODEL_COMMIT = '9217f5db79a29953eb74d5343926648285ec7e67'
MODEL_SHA256 = '8e0ae26000627ed62de0e78e41860af70094558b9d2913385c842a6aa06cf3fc'
MODEL_FILENAME = 'qwen2.5-0.5b-instruct-fp16.gguf'


def render_prompt(prompt: str) -> str:
    return ('<|im_start|>system\nYou are Qwen, created by Alibaba Cloud. '
            'You are a helpful assistant.<|im_end|>\n<|im_start|>user\n'+prompt+
            '<|im_end|>\n<|im_start|>assistant\n')


def completion_payload(prompt_tokens: list[int], slot: int, cache: bool, *, seed: int=SEED,
                       max_output_tokens: int=32, context_per_slot: int=2048, slot_count: int=4) -> dict:
    integer(seed,1,2**32-1,'seed');integer(max_output_tokens,32,128,'max_output_tokens')
    integer(context_per_slot,2048,2048,'context_per_slot');integer(slot_count,1,8,'slot_count')
    if type(slot) is not int or not 0 <= slot < slot_count or type(cache) is not bool:
        raise ContractError('invalid fixed slot/cache policy')
    if type(prompt_tokens) is not list or not prompt_tokens or any(type(token) is not int or token < 0 for token in prompt_tokens):
        raise ContractError('prompt tokens must be nonempty nonnegative IDs')
    if len(prompt_tokens) + max_output_tokens > context_per_slot:
        raise ContractError('prompt plus output exceeds admitted per-slot context')
    return {'prompt':prompt_tokens, 'id_slot':slot, 'cache_prompt':cache,
            'stream':True, 'return_tokens':True, 'n_predict':max_output_tokens, 'temperature':0,
            'seed':seed, 'ignore_eos':False, 'stop':[], 'samplers':['temperature'],
            'timings_per_token':True, 'return_progress':True}


def is_prompt_progress(payload: dict, prompt_tokens: int) -> bool:
    """Pinned progress events carry a placeholder token, not generated output."""
    if 'prompt_progress' not in payload:
        return False
    progress=payload['prompt_progress']
    if (payload.get('stop') is not False or payload.get('content')!='' or
        payload.get('tokens')!=[0] or type(payload.get('tokens_predicted')) is not int or
        payload['tokens_predicted']!=0 or payload.get('tokens_evaluated')!=prompt_tokens or
        type(progress) is not dict or set(progress)!={'total','cache','processed','time_ms'}):
        raise ContractError('malformed native prompt-progress event')
    if (any(type(progress[key]) is not int for key in ('total','cache','processed')) or
        progress['total']!=prompt_tokens or
        not 0<=progress['cache']<=progress['processed']<=progress['total'] or
        type(progress['time_ms']) not in (int,float) or
        not math.isfinite(progress['time_ms']) or progress['time_ms']<0):
        raise ContractError('invalid native prompt-progress accounting')
    return True


def normalize_response(records: list[tuple[int, dict]], *, request_id: str,
                       arrival_ns: int, admitted_ns: int, dispatch_ns: int,
                       completed_ns: int, prompt_tokens: int, slot: int,
                       seed: int=SEED,max_output_tokens: int=32) -> dict:
    """Normalize observed chunks, never synthesize an engine timestamp or EOS ID."""
    integer(seed,1,2**32-1,'seed');integer(max_output_tokens,32,128,'max_output_tokens')
    token_events=[]; text=[]; tokens=[]; terminal=None; previous=dispatch_ns
    for observed_ns, payload in records:
        if type(observed_ns) is not int or not previous <= observed_ns <= completed_ns:
            raise ContractError('stream timestamps out of order')
        previous=observed_ns
        if type(payload) is not dict or type(payload.get('stop')) is not bool:
            raise ContractError('native stream record missing stop flag')
        # This pinned backend leaves the partial result's slot at its -1 sentinel.
        # Only the terminal result attests the actual slot; never invent it earlier.
        allowed_slots=(slot,) if payload['stop'] else (-1,slot)
        if type(payload.get('id_slot')) is not int or payload['id_slot'] not in allowed_slots:
            raise ContractError('backend used an unexpected slot')
        if terminal is not None:
            raise ContractError('stream contains data after terminal record')
        if is_prompt_progress(payload,prompt_tokens):
            if tokens:raise ContractError('prompt progress appeared after generated tokens')
            continue
        ids=payload.get('tokens',[]);content=payload.get('content','')
        if type(ids) is not list or any(type(t) is not int or t < 0 for t in ids):
            raise ContractError('invalid streamed token IDs')
        if type(content) is not str:
            raise ContractError('invalid streamed content')
        if payload['stop']:
            # Pinned native stream final records contain no output; they are accounting.
            if ids or content:
                raise ContractError('unexpected terminal output: refusing to duplicate stream')
            terminal=payload
        else:
            text.append(content);tokens.extend(ids)
            if ids: token_events.append({'observed_ns':observed_ns,'token_ids':ids})
    if terminal is None:
        raise ContractError('stream ended without terminal accounting')
    settings=terminal.get('generation_settings')
    if type(settings) is not dict:
        raise ContractError('missing actual generation settings')
    expected={'samplers':['temperature'],'temperature':0,'seed':seed,'n_predict':max_output_tokens,
              'ignore_eos':False,'stop':[],'stream':True,'grammar':'','lora':[],
              'backend_sampling':False}
    for key,value in expected.items():
        actual=settings.get(key)
        if actual != value or (isinstance(actual,bool) != isinstance(value,bool)):
            raise ContractError(f'backend changed frozen generation setting: {key}')
    generated=terminal.get('tokens_predicted')
    if type(generated) is not int or generated < len(tokens):
        raise ContractError('generated-token accounting missing or below visible token count')
    if terminal.get('tokens_evaluated') != prompt_tokens:
        raise ContractError('backend prompt-token count differs from admitted input')
    if terminal.get('truncated') is not False:
        raise ContractError('backend context truncation or missing truncation flag')
    reason=terminal.get('stop_type')
    if reason not in ('eos','limit'):
        raise ContractError('unexpected stop condition')
    if terminal.get('stopping_word',''):
        raise ContractError('unexpected custom stopping word')
    return {'request_id':request_id, 'arrival_ns':arrival_ns, 'admitted_ns':admitted_ns,
            'dispatch_ns':dispatch_ns, 'completed_ns':completed_ns,
            'first_token_ns':token_events[0]['observed_ns'] if token_events else None,
            'token_events':token_events, 'output_token_ids':tokens, 'generated_tokens':generated,
            'output_text':''.join(text), 'finish_reason':reason, 'status':'SUCCEEDED',
            'prompt_tokens':prompt_tokens, 'engine_start_ns':None}
