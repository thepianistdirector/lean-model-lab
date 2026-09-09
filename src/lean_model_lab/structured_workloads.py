"""Deterministic v3 synthetic records authored for this AGPL project.

No external dataset is imported. Development and confirmation use disjoint key
and answer namespaces plus separately derived random streams. The seed is a
reproducibility control, not a hidden-answer protection boundary. Context record
count is a real task-size axis, independent of the v1/v2 filler-word STRATA.
"""
from __future__ import annotations

import hashlib
import random
import string
from typing import Any

from .contracts import ContractError, QUALITY, canonical_bytes, integer
from .context_slice import FAMILIES as RECORD_FAMILIES, prompt_lines

BASE_FAMILIES = RECORD_FAMILIES + ('record-reuse','record-mixed-v1')
EXPLICIT_FAMILIES = {family.removesuffix('-v1')+'-explicit-v2':family for family in BASE_FAMILIES}
FAMILIES = BASE_FAMILIES + tuple(EXPLICIT_FAMILIES)
from .workloads import GENERATOR_KEYS as V2_GENERATOR_KEYS, REQUEST_KEYS, WORKLOAD_KEYS, _object, make_workload_v2

GENERATOR_KEYS = V2_GENERATOR_KEYS | {'family', 'context_records', 'split'}
CONTEXT_RECORD_COUNTS = (8, 24, 64)
SPLITS = ('development', 'confirmation')
# For this ASCII language, even one token per prompt byte plus a conservative
# fixed chat-template envelope and the largest output budget fits 2048 slots.
# Runtime admission must still tokenize and check the actual complete template.
MAX_GENERATED_PROMPT_BYTES = 1600
CHAT_TEMPLATE_BYTE_ALLOWANCE = 256


def _word(rng: random.Random, namespace: str) -> str:
    return namespace + ''.join(rng.choice(string.ascii_uppercase) for _ in range(4))


def _unique_words(rng: random.Random, namespace: str, count: int) -> list[str]:
    words = []
    occupied = set()
    while len(words) < count:
        word = _word(rng, namespace)
        if word not in occupied:
            words.append(word)
            occupied.add(word)
    return words


def _near_key(key: str, occupied: set[str]) -> str:
    for letter in string.ascii_uppercase:
        candidate = key[:-1] + letter
        if candidate not in occupied:
            return candidate
    # At most 64 randomly chosen keys are used. Do not silently rely on chance
    # if a future fixture occupies every last-character neighbor.
    for letter in string.ascii_uppercase:
        candidate = key[:3] + letter + key[4]
        if candidate not in occupied:
            return candidate
    raise ContractError('near-key namespace exhausted')


def _request(rng: random.Random, family: str, context_records: int, namespace: str) -> tuple[str, str]:
    keys = _unique_words(rng, namespace, context_records)
    values = _unique_words(rng, namespace, context_records + 4)
    root = keys[0]
    keys[-1] = _near_key(root, set(keys))
    if family == 'record-lookup':
        rows = [f'VALUE {key} {value}' for key, value in zip(keys, values)]
        rng.shuffle(rows)
        expected = values[0]
    elif family == 'reference-chain':
        depth = {8: 2, 24: 3, 64: 4}[context_records]
        rows = [f'REF {keys[i]} {keys[i + 1]}' for i in range(depth)]
        rows.extend(f'VALUE {keys[i]} {values[i]}' for i in range(depth, context_records))
        rng.shuffle(rows)
        expected = values[depth]
    else:
        # Six ordered writes create three stale values followed by a two-edge
        # reference path and its new terminal value. Fillers occupy random gaps.
        writes = [f'VALUE {root} {values[0]}', f'VALUE {keys[1]} {values[1]}',
                  f'VALUE {keys[2]} {values[2]}', f'REF {root} {keys[1]}',
                  f'REF {keys[1]} {keys[2]}', f'VALUE {keys[2]} {values[3]}']
        filler_keys = keys[3:context_records - 1]
        filler_keys = filler_keys[:context_records - 7] + [keys[-1]]
        fillers = [f'VALUE {key} {values[i + 4]}' for i, key in enumerate(filler_keys)]
        rng.shuffle(fillers)
        positions = set(rng.sample(range(context_records), len(writes)))
        rows = []
        for i in range(context_records):
            rows.append(writes.pop(0) if i in positions else fillers.pop(0))
        expected = values[3]
    prompt = '\n'.join(prompt_lines(family, rows, root))
    if len(prompt.encode('ascii')) > MAX_GENERATED_PROMPT_BYTES:
        raise ContractError('generated prompt exceeds conservative context envelope')
    return prompt, expected


def make_workload_v3(*, request_count: int = 128, seed: int = 20260907,
                     max_output_tokens: int = 32, arrival_mode: str = 'simultaneous',
                     interval_ns: int = 0, burst_size: int = 8,
                     max_queue_requests: int | None = None,
                     request_deadline_ns: int | None = None,
                     concurrency_modes: tuple[int, ...] | list[int] = (1, 4),
                     family: str = 'record-lookup', context_records: int = 24,
                     split: str = 'development') -> dict:
    """Generate exact v2-shaped outer/request objects with a v3 generator."""
    if type(family) is not str or family not in FAMILIES:
        raise ContractError('unknown structured workload family')
    integer(context_records, min(CONTEXT_RECORD_COUNTS), max(CONTEXT_RECORD_COUNTS), 'context_records')
    if context_records not in CONTEXT_RECORD_COUNTS:
        raise ContractError('context_records must be 8, 24 or 64')
    if type(split) is not str or split not in SPLITS:
        raise ContractError('split must be development or confirmation')
    base = make_workload_v2(request_count=request_count, seed=seed, max_output_tokens=max_output_tokens,
        arrival_mode=arrival_mode, interval_ns=interval_ns, burst_size=burst_size,
        max_queue_requests=max_queue_requests, request_deadline_ns=request_deadline_ns,
        concurrency_modes=concurrency_modes)
    generator = {**base['generator'], 'family': family, 'context_records': context_records, 'split': split}
    source_family=EXPLICIT_FAMILIES.get(family,family)
    derived = hashlib.sha256(canonical_bytes({'generator_version': 3, 'seed': seed,
                                            'family': source_family, 'split': split})).digest()
    rng = random.Random(int.from_bytes(derived, 'big'))
    namespace = 'D' if split == 'development' else 'C'
    requests = []
    for index, previous in enumerate(base['requests']):
        if source_family == 'record-reuse':
            # Eight queries share one complete table in their original order.
            # No warm-up request is omitted; new tables reset useful reuse.
            if index % 8 == 0:
                table_keys=_unique_words(rng,namespace,context_records)
                table_values=_unique_words(rng,namespace,context_records)
                table_rows=[f'VALUE {k} {v}' for k,v in zip(table_keys,table_values)]
                rng.shuffle(table_rows)
                queries=rng.sample(range(context_records),8)
            selected=queries[index % 8]
            prompt='\n'.join(prompt_lines('record-lookup',table_rows,table_keys[selected]))
            expected=table_values[selected]
            if len(prompt.encode('ascii')) > MAX_GENERATED_PROMPT_BYTES:
                raise ContractError('generated reused table exceeds context envelope')
        elif source_family=='record-mixed-v1':
            # Prospective balanced cycling, not outcome-dependent selection.
            # TASK preserves each constituent grammar; the declaration binds
            # one joint population with explicit, separately reported subgroups.
            constituent=RECORD_FAMILIES[index % len(RECORD_FAMILIES)]
            prompt,expected=_request(rng,constituent,context_records,namespace)
        else:
            prompt, expected = _request(rng, source_family, context_records, namespace)
        if family in EXPLICIT_FAMILIES:
            from .explicit_grammar import restate_prompt
            prompt=restate_prompt(prompt)['prompt']
            if len(prompt.encode('ascii'))>MAX_GENERATED_PROMPT_BYTES:
                raise ContractError('explicit-language prompt exceeds conservative context envelope')
        requests.append({'request_id': previous['request_id'], 'stratum': context_records,
                         'prompt': prompt, 'expected': expected,
                         'arrival_offset_ns': previous['arrival_offset_ns']})
    base.update(schema_version=3, workload_id='synthetic-' + family + '-v3', generator=generator,
                stratum_unit='context_records', requests=requests)
    return base


def validate_workload_v3(value: Any) -> dict:
    """Reject any change to the regenerated prompt population or its controls."""
    _object(value, WORKLOAD_KEYS, 'v3 workload')
    _object(value['generator'], GENERATOR_KEYS, 'v3 generator')
    if value['generator']['max_queue_requests'] is None:
        raise ContractError('stored generator requires a resolved queue capacity')
    if type(value['generator']['concurrency_modes']) is not list:
        raise ContractError('stored generator concurrency_modes must be a JSON array')
    expected = make_workload_v3(**value['generator'])
    if type(value['requests']) is not list or len(value['requests']) != len(expected['requests']):
        raise ContractError('requests must contain the complete generated population')
    for request in value['requests']:
        _object(request, REQUEST_KEYS, 'v3 request')
    _object(value['quality'], set(QUALITY), 'quality')
    _object(value['sampling'], {'temperature', 'seed', 'stop', 'allow_eos'}, 'sampling')
    if type(value['concurrency_modes']) is not list or type(value['sampling']['stop']) is not list:
        raise ContractError('concurrency modes and stop controls must be JSON arrays')
    if canonical_bytes(value) != canonical_bytes(expected):
        raise ContractError('workload differs from its frozen structured v3 generator recipe')
    return value
