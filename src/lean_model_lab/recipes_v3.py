"""Explicit registered prompt interventions; legacy recipe meanings stay frozen."""
from __future__ import annotations
import copy
from .contracts import ContractError, canonical_bytes, digest, keys
from .recipes import make_recipe, RECIPE_KEYS

MECHANISMS = ('prefix-cache-v1', 'full-context-v1', 'lexical-slice-v1',
              'dependency-slice-v1', 'matched-budget-slice-v1',
              'dependency-slice-cache-v1', 'slice-versus-full-cache-v1',
              'simple-gated-slice-v1', 'learned-gated-slice-v1','explicit-grammar-v2')
PROTOCOL_KEYS = {'question', 'hypothesis', 'primary_sources', 'baseline', 'ablations',
                 'selection_rule', 'uncertainty', 'stopping_rule', 'claim_limit',
                 'development_evidence', 'confirmation_isolation', 'proposal_sha256'}


def validate_protocol(value):
    from .research import text, texts
    from .config import _sha
    from urllib.parse import urlsplit
    keys(value, PROTOCOL_KEYS, 'v3 study protocol')
    for field in PROTOCOL_KEYS - {'primary_sources', 'ablations', 'proposal_sha256'}:
        text(value[field], 'protocol ' + field)
    texts(value['ablations'], 'protocol ablations')
    texts(value['primary_sources'], 'protocol primary sources')
    for url in value['primary_sources']:
        parts = urlsplit(url)
        if parts.scheme != 'https' or not parts.hostname or parts.username or parts.password:
            raise ContractError('protocol sources require unauthenticated HTTPS')
    _sha(value['proposal_sha256'], 'proposal identity')
    return value


def make_recipe_v3(*, model_profile_id, workload, allocation, mechanism_id, protocol, proposal,
                   compute_threads=None, pair_count=2, purpose='MEASUREMENT',
                   ttft_slo_ns=15_000_000_000, end_to_end_slo_ns=30_000_000_000,
                   controller=None):
    from .structured_workloads import validate_workload_v3
    from .workloads import make_workload_v2, GENERATOR_KEYS
    from .research import validate_proposal, CAPABILITIES
    validate_workload_v3(workload); validate_protocol(protocol); validate_proposal(proposal)
    if protocol['proposal_sha256'] != digest(proposal):
        raise ContractError('study protocol does not bind the supplied proposal')
    if proposal['mechanism_id'] != mechanism_id:
        raise ContractError('proposal mechanism differs from the registered intervention')
    if proposal['domain'] != 'inference' or proposal['stage'] != 'llm_development':
        raise ContractError('this registered inference lane has no training or protected-confirmation execution')
    if any(CAPABILITIES[c] != 'IMPLEMENTED' for c in proposal['required_capabilities']):
        raise ContractError('proposal requires capabilities absent from this runtime')
    from .research_studies import build_proposal
    registered = build_proposal(mechanism_id)
    for field in ('quality_contract', 'metrics', 'baseline', 'candidate_delta'):
        if canonical_bytes(proposal[field]) != canonical_bytes(registered[field]):
            raise ContractError('proposal '+field+' differs from registered experiment semantics')
    if mechanism_id not in MECHANISMS:
        raise ContractError('unregistered prompt mechanism; candidate code is not imported')
    if purpose == 'MEASUREMENT' and workload['generator']['split'] != 'confirmation':
        raise ContractError('v3 measurement requires a prospectively declared confirmation split')
    base = make_workload_v2(**{k: v for k, v in workload['generator'].items() if k in GENERATOR_KEYS})
    recipe = make_recipe(model_profile_id=model_profile_id, workload=base, allocation=allocation,
        compute_threads=compute_threads, pair_count=pair_count, purpose=purpose,
        ttft_slo_ns=ttft_slo_ns, end_to_end_slo_ns=end_to_end_slo_ns)
    requested=proposal['resources'];limits=allocation['limits']
    if recipe['engine']['compute_threads'] > requested['cpu_threads'] or any(
        limits[a] > requested[b] for a,b in [('memory_bytes','memory_bytes'),('disk_bytes','disk_bytes'),('full_wall_seconds','wall_seconds')]):
        raise ContractError('recipe resource envelope exceeds the proposal ceiling')
    recipe.update(schema_version=3, workload_generator=copy.deepcopy(workload['generator']),
                  workload_sha256=digest(workload), mechanism_id=mechanism_id,
                  research_protocol=copy.deepcopy(protocol), research_proposal=copy.deepcopy(proposal))
    if mechanism_id=='learned-gated-slice-v1':
        from .acceptance_controller import validate_controller
        from .profiles import get_model_profile
        validate_controller(controller)
        metadata=controller['metadata'];profile=get_model_profile(model_profile_id)
        if (metadata['model_profile_id']!=model_profile_id or
            metadata['model_profile_sha256']!=digest(profile) or
            metadata['template_sha256']!=profile['template_sha256']):
            raise ContractError('controller model or template identity differs from recipe')
        recipe['controller']=copy.deepcopy(controller)
    elif controller is not None:
        raise ContractError('controller artifact only accepted for registered learned gate')
    recipe['evaluation'].update(output_token_parity=mechanism_id in ('prefix-cache-v1', 'full-context-v1'),
        comparison_semantics='same_input_token_parity' if mechanism_id in ('prefix-cache-v1', 'full-context-v1')
            else 'changed_input_exact_task_quality_no_loss',
        quality_noninferiority_margin=0, cost_primary='attempt_full_wall_including_prompt_preparation',
        uncertainty='descriptive_pair_range; request-level paired quality differences, no independence claim')
    return recipe


def workload_from_recipe_v3(value):
    from .structured_workloads import make_workload_v3
    return make_workload_v3(**value['workload_generator'])


def validate_recipe_v3(value):
    extra={'controller'} if value.get('mechanism_id')=='learned-gated-slice-v1' else set()
    keys(value, RECIPE_KEYS | {'mechanism_id', 'research_protocol', 'research_proposal'} | extra, 'recipe v3')
    if type(value['schema_version']) is not int or value['schema_version'] != 3:
        raise ContractError('unsupported research recipe schema')
    try:
        expected = make_recipe_v3(model_profile_id=value['model_profile_id'],
            workload=workload_from_recipe_v3(value), allocation=value['allocation'],
            mechanism_id=value['mechanism_id'], protocol=value['research_protocol'], proposal=value['research_proposal'],
            compute_threads=value['engine']['compute_threads'], pair_count=value['evaluation']['pairs_per_concurrency'],
            purpose=value['purpose'], ttft_slo_ns=value['evaluation']['ttft_slo_ns'],
            end_to_end_slo_ns=value['evaluation']['end_to_end_slo_ns'],controller=value.get('controller'))
    except (KeyError, TypeError) as exc:
        raise ContractError('malformed research recipe') from exc
    if canonical_bytes(value) != canonical_bytes(expected):
        raise ContractError('research recipe differs from registered mechanism, quality or workload rules')
    return value


def prompt_intervention(prompt, mechanism_id, arm, controller=None):
    from .context_slice import transform_prompt
    if arm not in ('baseline', 'candidate'):
        raise ContractError('unsupported comparison arm')
    selected = 'full-context-v1' if arm == 'baseline' or mechanism_id == 'prefix-cache-v1' else mechanism_id
    if selected=='explicit-grammar-v2':
        from .explicit_grammar import restate_prompt
        return restate_prompt(prompt)
    if selected in ('simple-gated-slice-v1','learned-gated-slice-v1'):
        from .acceptance_controller import extract_features, predict
        if selected=='learned-gated-slice-v1':
            if controller is None:
                raise ContractError('learned inference requires frozen controller')
            prediction=predict(controller['parameters'],prompt)
        else:
            features=extract_features(prompt)
            accept=features is not None and features['closure_records']==1 and features['overwritten_writes']==0
            prediction={'decision':'DEPENDENCY_SLICE' if accept else 'FULL',
                'features':features,'reason':'predeclared_single_value_no_overwrite_gate',
                'formal_guarantee':False}
        selected='dependency-slice-v1' if prediction['decision']=='DEPENDENCY_SLICE' else 'full-context-v1'
        result=transform_prompt(prompt,selected)
        result['controller_prediction']={k:v for k,v in prediction.items() if k!='prompt'}
        return result
    if selected in ('dependency-slice-cache-v1', 'slice-versus-full-cache-v1'):
        selected='dependency-slice-v1'
    return transform_prompt(prompt, selected)


def cache_enabled(recipe, arm):
    if arm not in ('baseline','candidate'):
        raise ContractError('invalid cache-policy arm')
    if recipe['schema_version']==2:
        return arm=='candidate'
    mechanism=recipe['mechanism_id']
    if mechanism=='slice-versus-full-cache-v1':
        return True
    return arm=='candidate' and mechanism in ('prefix-cache-v1','dependency-slice-cache-v1')
