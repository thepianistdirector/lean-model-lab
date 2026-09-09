"""Bounded symbolic record slicing; never a certificate of model equivalence.

This is classic dependency slicing applied to a deliberately small synthetic
language, not a new model architecture. The transformer receives no answer,
request object, seed or external record store. It emits only original input
lines. Certificates establish syntax and query-dependency closure only: they
do not establish logits, token distributions or LLM answer correctness.
"""
from __future__ import annotations

import hashlib
import re

from .contracts import ContractError

LANGUAGE = 'RECORD-LANGUAGE v1'
LANGUAGE_V2 = 'RECORD-LANGUAGE v2'
FAMILIES = ('record-lookup', 'reference-chain', 'record-updates')
RULES = 'RULES Last assignment wins. REF follows the final assignment of its target.'
OUTPUT = 'OUTPUT Resolve ASK to a VALUE. Reply with that alphabetic value only.'
RULES_V2 = ('RULES VALUE k v means key k has value v. REF k t means key k uses target t\'s final value. '
            'Last write to a key wins. Follow REF targets until VALUE. '
            'Example: VALUE AAAAA APPLE; REF BBBBB AAAAA; ASK BBBBB => APPLE.')
OUTPUT_V2 = ('OUTPUT Return the complete five-letter VALUE value for ASK, exactly as written. '
             'Do not return a key, shorten the value, explain, or add other text.')
MECHANISMS = ('full-context-v1', 'lexical-slice-v1', 'dependency-slice-v1', 'matched-budget-slice-v1')
MAX_RECORDS = 64
MAX_PROMPT_CHARS = 4096
MAX_DEPENDENCY_STEPS = 64
RECORD = re.compile(r'(VALUE|REF) ([A-Z]{5}) ([A-Z]{5})\Z')
QUERY = re.compile(r'ASK ([A-Z]{5})\Z')


def prompt_lines(family: str, records: list[str], query: str) -> list[str]:
    """The exact grammar shared with the deterministic workload author."""
    return [LANGUAGE, 'TASK ' + family, RULES, OUTPUT, 'BEGIN', *records, 'END',
            'ASK ' + query, 'ANSWER:']


def _sha(prompt: str) -> str:
    return hashlib.sha256(prompt.encode('utf-8')).hexdigest()


def _parse(prompt: str) -> dict:
    if len(prompt) > MAX_PROMPT_CHARS:
        raise ContractError('prompt_character_budget')
    if not prompt.isascii() or '\r' in prompt:
        raise ContractError('unknown_language')
    lines = prompt.split('\n')
    if len(lines) < 9 or len(lines) > MAX_RECORDS + 8:
        raise ContractError('record_count_budget')
    family = lines[1].removeprefix('TASK ')
    language,rules,output=(LANGUAGE_V2,RULES_V2,OUTPUT_V2) if lines[0]==LANGUAGE_V2 else (LANGUAGE,RULES,OUTPUT)
    if (lines[:5] != [language, 'TASK ' + family, rules, output, 'BEGIN'] or
            family not in FAMILIES or lines[-3] != 'END' or lines[-1] != 'ANSWER:'):
        raise ContractError('unknown_language')
    query = QUERY.fullmatch(lines[-2])
    if query is None:
        raise ContractError('malformed_query')
    records = []
    final = {}
    for line_index in range(5, len(lines) - 3):
        match = RECORD.fullmatch(lines[line_index])
        if match is None:
            raise ContractError('malformed_record')
        kind, key, rhs = match.groups()
        if family == 'record-lookup' and kind != 'VALUE':
            raise ContractError('lookup_reference')
        if family != 'record-updates' and key in final:
            raise ContractError('duplicate_key')
        record = {'kind': kind, 'key': key, 'rhs': rhs, 'line_index': line_index}
        records.append(record)
        final[key] = record
    if query[1] not in final:
        raise ContractError('unknown_query_key')
    # Validate the final graph globally, including branches unrelated to ASK.
    # Earlier writes are intentionally superseded under last-write semantics.
    for key in final:
        visited = set()
        current = key
        for _ in range(MAX_DEPENDENCY_STEPS):
            if current in visited:
                raise ContractError('reference_cycle')
            if current not in final:
                raise ContractError('dangling_reference')
            visited.add(current)
            record = final[current]
            if record['kind'] == 'VALUE':
                break
            current = record['rhs']
        else:
            raise ContractError('dependency_step_budget')
    closure = []
    current = query[1]
    for _ in range(MAX_DEPENDENCY_STEPS):
        record = final[current]
        closure.append(record)
        if record['kind'] == 'VALUE':
            break
        current = record['rhs']
    else:
        raise ContractError('dependency_step_budget')
    return {'lines': lines, 'family': family, 'records': records, 'final': final,
            'query': query[1], 'closure': closure}


def _certificate(prompt: str, mechanism_id: str) -> dict:
    prompt_sha256 = _sha(prompt)
    return {'schema_version': 1, 'scope': 'SYNTAX_DEPENDENCY_CLOSURE_ONLY',
            'limitation': 'No claim about logits, token distributions, model answer equivalence or LLM correctness.',
            'mechanism_id': mechanism_id, 'input_prompt_sha256': prompt_sha256,
            'output_prompt_sha256': prompt_sha256, 'input_syntax_valid': None,
            'dependency_closure_preserved': None, 'input_record_count': None,
            'retained_record_count': None, 'closure_record_count': None,
            'query_key': None, 'closure_line_indices': [],
            'selected_record_line_indices': [], 'budget_unit': 'record_lines',
            'budget_matched_to_dependency': mechanism_id == 'matched-budget-slice-v1',
            'selection_indices_complete': True, 'fallback_reason': None}


def transform_prompt(prompt: str, mechanism_id: str) -> dict:
    """Return a prompt-only transformation and an explicitly limited certificate.

Indices are zero-based original lines, in original order, including the retained
header/footer. For oversized input, unchanged fallback avoids enumerating an
unbounded number of lines; indices are empty and their completeness is false.
The matched-budget ablation keeps the first N record lines, where N is the
dependency slice's record count. It does not claim a matched tokenizer budget.
Lexical ablation keeps records mentioning ASK's exact key, without following
references. Neither ablation asserts dependency closure unless it actually
retains every last-write record in the full query path.
    """
    if type(prompt) is not str:
        raise ContractError('prompt must be a string')
    if type(mechanism_id) is not str or mechanism_id not in MECHANISMS:
        raise ContractError('unknown context-slice mechanism')
    certificate = _certificate(prompt, mechanism_id)
    # The full-cost reference must not pay for candidate parsing or closure.
    # Hashing and line-index provenance are the only identity bookkeeping here.
    if mechanism_id == 'full-context-v1':
        complete = len(prompt) <= MAX_PROMPT_CHARS
        certificate.update(scope='IDENTITY_ONLY', selection_indices_complete=complete)
        return {'prompt': prompt, 'decision': 'IDENTITY',
                'selected_line_indices': list(range(prompt.count('\n') + 1)) if complete else [],
                'certificate': certificate}
    if len(prompt) > MAX_PROMPT_CHARS:
        certificate.update(fallback_reason='prompt_character_budget', selection_indices_complete=False)
        return {'prompt': prompt, 'decision': 'FALLBACK_FULL_CONTEXT',
                'selected_line_indices': [], 'certificate': certificate}
    all_indices = list(range(prompt.count('\n') + 1))
    try:
        parsed = _parse(prompt)
    except ContractError as exc:
        certificate['fallback_reason'] = str(exc)
        certificate['input_syntax_valid'] = False
        return {'prompt': prompt, 'decision': 'FALLBACK_FULL_CONTEXT',
                'selected_line_indices': all_indices, 'certificate': certificate}
    records = parsed['records']
    closure_indices = {record['line_index'] for record in parsed['closure']}
    if mechanism_id == 'dependency-slice-v1':
        selected = closure_indices
        decision = 'CERTIFIED_SLICE'
    elif mechanism_id == 'lexical-slice-v1':
        selected = {record['line_index'] for record in records
                    if record['key'] == parsed['query'] or
                    (record['kind'] == 'REF' and record['rhs'] == parsed['query'])}
        decision = 'ABLATION_SLICE'
    else:
        selected = {record['line_index'] for record in records[:len(closure_indices)]}
        decision = 'ABLATION_SLICE'
    retained = [i for i in all_indices if i < 5 or i >= len(parsed['lines']) - 3 or i in selected]
    transformed = '\n'.join(parsed['lines'][i] for i in retained)
    # Keeping every final write in the full query path preserves its symbolic
    # result. Older writes cannot override them because order is unchanged.
    certificate.update(output_prompt_sha256=_sha(transformed), input_syntax_valid=True,
        dependency_closure_preserved=closure_indices.issubset(selected),
        input_record_count=len(records), retained_record_count=len(selected),
        closure_record_count=len(closure_indices), query_key=parsed['query'],
        closure_line_indices=sorted(closure_indices), selected_record_line_indices=sorted(selected))
    return {'prompt': transformed, 'decision': decision,
            'selected_line_indices': retained, 'certificate': certificate}
