"""Source-grounded starting protocols for the bounded implemented inference lane."""
from __future__ import annotations
import copy
from .contracts import ContractError, digest
from .research import catalog, template, validate_proposal
from .recipes_v3 import MECHANISMS, validate_protocol

SOURCES = ['https://arxiv.org/abs/2310.04408', 'https://arxiv.org/abs/2403.12968',
           'https://arxiv.org/abs/2605.17304', 'https://arxiv.org/abs/2509.17338']


def build_proposal(mechanism_id):
    if mechanism_id not in MECHANISMS:
        raise ContractError('unknown registered study mechanism')
    value = template('prefix-cache-control')
    value.update(id='study-'+mechanism_id, mechanism_id=mechanism_id, domain='inference',
        stage='llm_development', objective='efficiency_at_quality')
    known = mechanism_id in ('prefix-cache-v1', 'full-context-v1','explicit-grammar-v2')
    value['kind'] = 'known_method_control' if known else 'new_combination'
    value['novelty'] = {'status': 'KNOWN_METHOD' if known else 'OVERLAP_IDENTIFIED',
        'search_scope': 'Primary RECOMP, LLMLingua-2, Context Codec and SLICET5 pages reviewed 2026-09-08; classical dependency slicing is existing work. This bounded test does not establish priority.',
        'unresolved_questions': ['Whether a syntax/dependency certificate predicts model task accuracy or cost advantage on the declared structured-record population.']}
    descriptions = {
        'explicit-grammar-v2': 'Keep every original record, key, value, query and order, but replace the compact instruction header with one fixed explicit operand definition, unrelated example and complete-five-letter output instruction. No slicing or cache change.',
        'simple-gated-slice-v1': 'Use dependency slicing only for one-record query closures with no overwritten writes; otherwise send full context. This gate is predeclared without learned parameters.',
        'learned-gated-slice-v1': 'Fit a depth-two empirical harmful-omission tree on actual paired native outcomes, select a threshold on separate table-group calibration data, then route frozen confirmation prompts using graph features only. No feasible calibration point falls back to full context.',
        'dependency-slice-cache-v1': 'Apply verified dependency slicing and enable same-slot prefix reuse in the candidate; compare with uncached full context, with both constituent controls required.',
        'slice-versus-full-cache-v1': 'Compare verified dependency slices with full context while both arms enable identical same-slot prefix reuse; retain all cold primers and new-table transitions.',
        'prefix-cache-v1': 'Toggle native same-slot prefix reuse for identical structured-record prompts.',
        'full-context-v1': 'Repeat identical full-context no-cache inference as a measurement control.',
        'lexical-slice-v1': 'Retain only lexical target matches without recursive dependency closure; deliberately incomplete causal ablation.',
        'dependency-slice-v1': 'Compute final-assignment dependency closure, retain source records in original order, attach a bounded syntactic certificate, and fall back to full context when verification fails.',
        'matched-budget-slice-v1': 'Select a deterministic subset with the same record-count budget as dependency closure, without dependency-based selection; records are not a token-count budget.',
    }
    value.update(title='Structured-context investigation: '+mechanism_id,
        mechanism=descriptions[mechanism_id],
        prediction='Dependency-complete omission may reduce native prompt work while preserving exact task quality; a syntax-level certificate alone may fail to preserve actual model answers.',
        baseline='The same checkpoint, offered requests and inference settings on complete original contexts with cache disabled.',
        candidate_delta=descriptions[mechanism_id],
        technique_ids=[],
        invariants=['Same admitted model, tokenizer/template, output ceiling, sampling, offered task population and paired order.',
                    'Candidate consumes prompt text only. Expected answers are independently evaluated after inference.',
                    'Every failed, interrupted and missing request remains charged and in the offered denominator.'],
        required_capabilities=['immutable-recipe-and-recovery', 'offline-evidence-workbench',
                               'registered-context-slice-v3', 'structured-record-evaluator-v3'])
    source_map = {s['url']:s for s in catalog()['sources']}
    value['prior_art'] = [{'source_id':source_map[url]['id'], 'overlap':source_map[url]['supported_claim'],
        'proposed_difference': 'A small registered record-language closure/certificate/fallback implementation and its real-model causal ablations; no priority claim and no replication of the paper benchmark.'} for url in SOURCES]
    value['quality_contract'] = {'metric':'exact_record_answer_after_outer_whitespace_strip',
        'direction':'higher', 'decision_rule':'Both arms at least 95% correct on every offered request, with no observed pairwise task-quality loss. Same-input controls additionally require exact token parity.',
        'evaluation_revision':'v3-prompt-task-quality-1; exact implementation archive retained',
        'population':'Complete prospectively frozen structured workload, model profile, split, seed and offered arrivals in the compiled recipe.',
        'semantic_equivalence':'Task-answer equivalence for changed-input interventions; output differences remain visible. Syntax/dependency preservation does not imply unchanged logits or general language quality.'}
    value['metrics'] = [
        {'name':'full_attempt_wall', 'unit':'nanoseconds', 'direction':'lower', 'decision_rule':'At least 5% improvement in every balanced pair, with quality gates and at most 10% p95/p99 tail regression; descriptive ranges, not significance.'},
        {'name':'all_allocation_cost', 'unit':'nanoseconds', 'direction':'lower', 'decision_rule':'Include setup, development/search, failed attempts, preprocessing and retries; shared ancestry is counted once.'},
        {'name':'task_accuracy', 'unit':'fraction_of_offered_requests', 'direction':'higher', 'decision_rule':'95% absolute minimum and zero allowed observed pairwise quality regression.'},
    ]
    value['ablations'] = ['Full original context with cache disabled.', 'Lexical target-only selection without transitive closure.',
        'Dependency closure with certificate and conservative fallback.', 'Same record-count budget without dependency-based selection; report actual token budget differences.',
        'A symbolic task interpreter is a non-LLM floor for this restricted grammar, not a general-language competitor.']
    value['falsifiers'] = ['Any retained task semantics lost by the closure certificate refutes its restricted preservation claim.',
        'Actual model accuracy loss despite a valid certificate refutes certificate-to-model-output equivalence.',
        'Startup, analysis, tokenization or retries erasing service savings defeats full-cost improvement.',
        'If a symbolic interpreter suffices, do not frame this task as requiring an LLM or claim broad inference advances.']
    value['evaluation'] = {'development':'Use the development split for implementation and feasibility; retain its complete costs and outputs.',
        'confirmation':'Use a separately seeded confirmation split only after protocol and candidate freeze. Same Unix identity: workflow separation, not malicious-writer isolation.',
        'selection_rule':'One predeclared candidate and causal ablations, equal populations/repetitions/model settings. Do not tune or replace a failed confirmation.'}
    value['claim_limit']='Candidate combination/engineering investigation of structured-context omission; broad novelty, arbitrary natural-language guarantees, training advances and general speedups are unestablished.'
    if mechanism_id in ('dependency-slice-cache-v1','slice-versus-full-cache-v1'):
        value['novelty']['search_scope'] += ' Direct cache/compression overlap: CAPC https://arxiv.org/abs/2607.15516 (2026-07-17); this is a CPU systems challenge, not a priority claim.'
        value['ablations'] = ['Full context without cache.', 'Full context with cache.', 'Dependency slice without cache.', 'Dependency slice with cache.', 'Include first-use and table-change requests in all costs and denominators.']
        value['prediction']='On repeated-table traffic, a shorter query-dependent slice can destroy useful prefix reuse; native CPU full-wall savings may disappear against full context with caching.'
        value['claim_limit']='Known-mechanism CPU interaction/transfer investigation. No cache-aware compression novelty, API-price equivalence, universal gain or training claim.'
    if mechanism_id=='slice-versus-full-cache-v1':
        value['baseline']='The same checkpoint, offered requests and inference settings on complete original contexts with same-slot prefix cache enabled.'
    if mechanism_id in ('simple-gated-slice-v1','learned-gated-slice-v1'):
        value['novelty']['search_scope'] += ' Related selective prediction and routing: Learn then Test https://arxiv.org/abs/2110.01052; Conformal Risk Control https://arxiv.org/abs/2208.02814; RouteLLM https://arxiv.org/abs/2406.18665. This empirical procedure has no conformal or population-risk guarantee.'
        value['prediction']='Model-bound empirical acceptance may avoid harmful omissions while retaining useful slicing savings, but calibration failure, distribution shift and full training/setup cost may erase the benefit.'
        value['ablations']=['Always full context.','Always dependency slice.','Predeclared one-record closure with no overwritten writes gate.','Depth-two learned gate with separate calibration; all four paired outcome classes remain recorded.']
        value['claim_limit']='Bounded learned acceptance-controller investigation; actual small-tree training, no training or fine-tuning of the underlying LLM. Novel architecture, formal risk guarantees and broad natural-language savings are unestablished.'
    if mechanism_id=='explicit-grammar-v2':
        value['prediction']='A fixed clarification of operand roles and output format may improve model comprehension of the same records; failure would rule out this single wording alternative, not every possible prompt.'
        value['ablations']=['Unchanged compact v1 full-context instructions.','Fixed explicit v2 instructions with all original full-context task records retained.']
        value['novelty']['search_scope']='Known instruction and in-context-example technique; Brown et al. https://arxiv.org/abs/2005.14165 reviewed 2026-09-08. This is a bounded development diagnosis, not novelty or model training.'
        value['claim_limit']='One fixed development wording diagnosis on identical task records. No prompt search, architecture novelty, LLM training or universal comprehension/efficiency claim. Failed original results remain retained.'
    return validate_proposal(value)


def default_protocol(proposal):
    validate_proposal(proposal)
    value = {'question':'Can dependency-complete context omission preserve model task accuracy and lower full inference cost on the frozen structured-record workload?',
        'hypothesis':proposal['prediction'], 'primary_sources':list(SOURCES), 'baseline':proposal['baseline'],
        'ablations':copy.deepcopy(proposal['ablations']),
        'selection_rule':'Registered candidate chosen before confirmation. Equal offered work, model, sampling, repetitions and maximum resource envelope; no tuning on confirmation.',
        'uncertainty':'Balanced AB/BA paired effects and descriptive pair ranges; per-request paired correctness differences. No IID request assumption, significance claim or generalization beyond covered scenarios.',
        'stopping_rule':'Execute exactly the frozen cells once; stop on original allocation exhaustion, cancellation, invalid identity/protocol, or failed/interrupted arm. Retain all outputs; no successful replacement of failed confirmation.',
        'claim_limit':proposal['claim_limit'],
        'development_evidence':'No development evidence supplied in this starting protocol; investigator must cite retained feasibility artifacts before confirmation or explicitly predeclare a zero-tuning design.',
        'confirmation_isolation':'Separate modules, candidate receives prompt only, regenerated fixed answers, distinct seeded split, frozen implementation hashes. Shared Unix identity: workflow convention, not an adversarial security boundary.',
        'proposal_sha256':digest(proposal)}
    if proposal['mechanism_id'] in ('dependency-slice-cache-v1','slice-versus-full-cache-v1'):
        value['primary_sources'].append('https://arxiv.org/abs/2607.15516')
        value['question']='When does context omission lose its CPU cost advantage because full-context prefix reuse saves more work?'
    if proposal['mechanism_id'] in ('simple-gated-slice-v1','learned-gated-slice-v1'):
        value['primary_sources'].extend(['https://arxiv.org/abs/2110.01052','https://arxiv.org/abs/2208.02814','https://arxiv.org/abs/2406.18665'])
        value['question']='Can a fitted model-bound harmful-omission gate outperform always-full, always-slice and a predeclared simple gate after calibration, untouched confirmation and training costs?'
    if proposal['mechanism_id']=='explicit-grammar-v2':
        value['primary_sources']=['https://arxiv.org/abs/2005.14165']
        value['question']='Does one fixed explicit definition of operand roles and output format improve comprehension of identical full-context record tasks?'
    return validate_protocol(value)
