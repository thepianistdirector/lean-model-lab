"""Deterministic v2 synthetic workloads; no execution or private prompt inputs.

Arrival offsets are relative to the service epoch. A request deadline, when set,
is a duration from its offered arrival, not a new admission-time allowance.
The resolved generator recipe is authoritative; validation regenerates the full
population and rejects changes to any prompt, answer, control or arrival.
"""
from __future__ import annotations

import random
import string
from typing import Any

from .contracts import ContractError, QUALITY, STRATA, canonical_bytes, integer

MAX_NS = 2**63 - 1
MAX_DEADLINE_NS = 3600 * 10**9
GENERATOR_KEYS = {
    'request_count', 'seed', 'max_output_tokens', 'arrival_mode', 'interval_ns',
    'burst_size', 'max_queue_requests', 'request_deadline_ns',
    'concurrency_modes',
}
WORKLOAD_KEYS = {
    'schema_version', 'workload_id', 'generator', 'generator_seed', 'stratum_unit',
    'concurrency_modes', 'max_output_tokens', 'sampling', 'arrival_mode', 'quality',
    'max_queue_requests', 'request_deadline_ns', 'requests',
}
REQUEST_KEYS = {'request_id', 'stratum', 'prompt', 'expected', 'arrival_offset_ns'}


def _object(value: Any, fields: set[str], label: str) -> None:
    if type(value) is not dict or set(value) != fields:
        raise ContractError(f'{label} must contain exactly the declared fields')


def make_workload_v2(*, request_count: int = 128, seed: int = 20260907,
                     max_output_tokens: int = 32, arrival_mode: str = 'simultaneous',
                     interval_ns: int = 0, burst_size: int = 8,
                     max_queue_requests: int | None = None,
                     request_deadline_ns: int | None = None,
                     concurrency_modes: tuple[int, ...] | list[int] = (1, 4)) -> dict:
    """Create a complete recipe; omitted queue capacity resolves to population size.

Paced request i arrives at i * interval_ns. Burst request i arrives at
(i // burst_size) * interval_ns. Simultaneous arrivals are all zero.
Burst size is retained in every recipe but only controls burst-mode arrivals.
    """
    integer(request_count, 4, 1024, 'request_count')
    if request_count % 4:
        raise ContractError('request_count must be a multiple of four')
    integer(seed, 1, 2**32 - 1, 'seed')
    integer(max_output_tokens, 32, 128, 'max_output_tokens')
    if type(concurrency_modes) not in (tuple, list) or not 1 <= len(concurrency_modes) <= 4:
        raise ContractError('concurrency_modes must contain one to four modes')
    modes = list(concurrency_modes)
    for mode in modes:
        integer(mode, 1, 8, 'concurrency mode')
    if modes != sorted(set(modes)):
        raise ContractError('concurrency_modes must be sorted and unique')
    if type(arrival_mode) is not str or arrival_mode not in ('simultaneous', 'paced', 'burst'):
        raise ContractError('arrival_mode must be simultaneous, paced or burst')
    integer(interval_ns, 0, MAX_NS, 'interval_ns')
    if arrival_mode == 'simultaneous' and interval_ns != 0:
        raise ContractError('simultaneous arrivals require interval_ns=0')
    if arrival_mode != 'simultaneous' and interval_ns == 0:
        raise ContractError('paced and burst arrivals require positive interval_ns')
    integer(burst_size, 1, request_count if arrival_mode == 'burst' else 1024, 'burst_size')
    if max_queue_requests is None:
        max_queue_requests = request_count
    integer(max_queue_requests, 1, request_count, 'max_queue_requests')
    if request_deadline_ns is not None:
        integer(request_deadline_ns, 1, MAX_DEADLINE_NS, 'request_deadline_ns')
    last_index = ((request_count - 1) // burst_size if arrival_mode == 'burst'
                  else request_count - 1 if arrival_mode == 'paced' else 0)
    if last_index * interval_ns > MAX_NS:
        raise ContractError('arrival offsets exceed signed 64-bit nanoseconds')

    generator = {
        'request_count': request_count, 'seed': seed, 'max_output_tokens': max_output_tokens,
        'arrival_mode': arrival_mode, 'interval_ns': interval_ns, 'burst_size': burst_size,
        'max_queue_requests': max_queue_requests, 'request_deadline_ns': request_deadline_ns,
        'concurrency_modes': list(modes),
    }
    rng = random.Random(seed)
    vocabulary = ('river', 'stone', 'cloud', 'field', 'tree', 'path', 'light', 'water')
    filler = {size: ' '.join(vocabulary[i % len(vocabulary)] for i in range(size))
              for size in STRATA}
    requests = []
    for index in range(request_count):
        size = STRATA[index % len(STRATA)]
        answer = ''.join(rng.choice(string.ascii_uppercase) for _ in range(5))
        prompt = ('Read the record below. Reply with the value of KEY only, without explanation.\n'
                  f'FILLER: {filler[size]}\nKEY: {answer}\nAnswer:')
        arrival = (index * interval_ns if arrival_mode == 'paced' else
                   (index // burst_size) * interval_ns if arrival_mode == 'burst' else 0)
        requests.append({'request_id': f'r{index:03d}', 'stratum': size,
                         'prompt': prompt, 'expected': answer, 'arrival_offset_ns': arrival})
    return {
        'schema_version': 2, 'workload_id': 'synthetic-key-copy-v2', 'generator': generator,
        'generator_seed': seed, 'stratum_unit': 'filler_words', 'concurrency_modes': list(modes),
        'max_output_tokens': max_output_tokens,
        'sampling': {'temperature': 0, 'seed': seed, 'stop': [], 'allow_eos': True},
        'arrival_mode': arrival_mode, 'quality': dict(QUALITY),
        'max_queue_requests': max_queue_requests, 'request_deadline_ns': request_deadline_ns,
        'requests': requests,
    }


def validate_workload_v2(value: Any) -> dict:
    """Validate the exact generated JSON contract and return the supplied object."""
    _object(value, WORKLOAD_KEYS, 'v2 workload')
    _object(value['generator'], GENERATOR_KEYS, 'generator')
    # None is an API convenience only: persisted recipes bind a concrete capacity.
    if value['generator']['max_queue_requests'] is None:
        raise ContractError('stored generator requires a resolved queue capacity')
    if type(value['generator']['concurrency_modes']) is not list:
        raise ContractError('stored generator concurrency_modes must be a JSON array')
    expected = make_workload_v2(**value['generator'])
    if type(value['requests']) is not list or len(value['requests']) != len(expected['requests']):
        raise ContractError('requests must contain the complete generated population')
    for request in value['requests']:
        _object(request, REQUEST_KEYS, 'request')
    _object(value['quality'], set(QUALITY), 'quality')
    _object(value['sampling'], {'temperature', 'seed', 'stop', 'allow_eos'}, 'sampling')
    if type(value['concurrency_modes']) is not list or type(value['sampling']['stop']) is not list:
        raise ContractError('concurrency modes and stop controls must be JSON arrays')
    if canonical_bytes(value) != canonical_bytes(expected):
        raise ContractError('workload differs from its frozen synthetic-key-copy-v2 generator recipe')
    return value
