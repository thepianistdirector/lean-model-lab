"""One fixed instruction-restatement diagnostic, with all task records retained.

This is an existing prompting technique, not a new model or efficiency claim.
The fixed unrelated example never contains the generated D/C task identifiers.
"""
from .contracts import ContractError
from .context_slice import (_parse, _certificate, LANGUAGE_V2, RULES_V2, OUTPUT_V2,
                            transform_prompt, _sha)


def restate_prompt(prompt):
    if type(prompt) is not str:raise ContractError('restatement input must be prompt text')
    try:parsed=_parse(prompt)
    except ContractError:
        result=transform_prompt(prompt,'full-context-v1')
        result['decision']='FALLBACK_FULL_CONTEXT'
        result['certificate']['fallback_reason']='unsupported_instruction_restatement_input'
        return result
    lines=parsed['lines'][:]
    lines[0]=LANGUAGE_V2;lines[2]=RULES_V2;lines[3]=OUTPUT_V2
    result='\n'.join(lines)
    certificate=_certificate(prompt,'explicit-grammar-v2')
    certificate.update(scope='SYNTAX_PRESERVING_INSTRUCTION_RESTATEMENT_ONLY',
        output_prompt_sha256=_sha(result),input_syntax_valid=True,
        dependency_closure_preserved=True,input_record_count=len(parsed['records']),
        retained_record_count=len(parsed['records']),closure_record_count=len(parsed['closure']),
        query_key=parsed['query'],closure_line_indices=sorted(r['line_index'] for r in parsed['closure']),
        selected_record_line_indices=[r['line_index'] for r in parsed['records']],
        rewritten_line_indices=[0,2,3],
        fixed_example_scope='Unrelated AAAAA/BBBBB/APPLE example; no task answer or external labels read.')
    return {'prompt':result,'decision':'EXPLICIT_GRAMMAR_RESTATEMENT',
        'selected_line_indices':list(range(len(lines))),'certificate':certificate}
