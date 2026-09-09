"""Inert research contracts and explicit capability boundaries; never execute proposals."""
from __future__ import annotations

import copy
import re
from pathlib import Path
from urllib.parse import urlsplit

from .contracts import ContractError, canonical_bytes, digest, integer, keys, read_json
from .artifacts import write_json_new

ID = re.compile(r'[a-z][a-z0-9-]{2,95}\Z')
PROPOSAL_FIELDS = {'schema_version', 'id', 'title', 'domain', 'kind', 'objective',
    'mechanism_id', 'mechanism', 'prediction', 'prior_art', 'technique_ids', 'baseline',
    'candidate_delta', 'invariants', 'quality_contract', 'metrics', 'ablations',
    'falsifiers', 'required_capabilities', 'resources', 'stop_rules', 'evaluation',
    'novelty', 'stage', 'claim_limit'}
CAPABILITIES = {
    'reviewed-cpu-prefix-cache-v2': 'IMPLEMENTED',
    'immutable-recipe-and-recovery': 'IMPLEMENTED',
    'synthetic-key-copy-evaluator': 'IMPLEMENTED',
    'offline-evidence-workbench': 'IMPLEMENTED',
    'registered-context-slice-v3': 'IMPLEMENTED',
    'structured-record-evaluator-v3': 'IMPLEMENTED',
    'training-runtime': 'NOT_IMPLEMENTED',
    'custom-attention-operator': 'NOT_IMPLEMENTED',
    'custom-model-training': 'NOT_IMPLEMENTED',
    'general-quality-evaluator': 'NOT_IMPLEMENTED',
    'protected-confirmation-isolation': 'NOT_IMPLEMENTED',
    'gpu-runtime': 'NOT_ADMITTED',
    'untrusted-candidate-isolation': 'NOT_IMPLEMENTED',
}


def text(value, label, maximum=6000):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ContractError(label + ' must be nonempty bounded text')
    return value


def identifier(value, label):
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise ContractError(label + ' must be a stable lowercase identifier')


def texts(value, label, *, minimum=1, maximum=32):
    if type(value) is not list or not minimum <= len(value) <= maximum:
        raise ContractError(label + ' has an invalid population')
    for item in value:
        text(item, label)
    if len(value) != len(set(value)):
        raise ContractError(label + ' contains duplicates')


def catalog():
    from .research_catalog import CATALOG
    return validate_catalog(copy.deepcopy(CATALOG))


def validate_catalog(value):
    keys(value, {'schema_version', 'catalog_id', 'reviewed_date', 'coverage', 'sources',
                 'techniques', 'composition_rules', 'evaluation_cautions'}, 'research catalog')
    integer(value['schema_version'], 1, 1, 'catalog schema')
    identifier(value['catalog_id'], 'catalog id'); text(value['reviewed_date'], 'catalog review date')
    keys(value['coverage'], {'inference_families', 'training_families', 'exhaustive', 'scope',
                            'gaps', 'adoption_rule'}, 'catalog coverage')
    if value['coverage']['exhaustive'] is not False:
        raise ContractError('this bounded catalog cannot claim exhaustive coverage')
    texts(value['coverage']['gaps'], 'catalog gaps')
    for field in ('scope', 'adoption_rule'):
        text(value['coverage'][field], 'coverage ' + field)
    if type(value['sources']) is not list or not 1 <= len(value['sources']) <= 1024:
        raise ContractError('invalid source inventory')
    source_ids = set(); source_urls = set()
    for source in value['sources']:
        keys(source, {'id', 'title', 'date', 'date_basis', 'url', 'supported_claim',
                      'evidence_type', 'verification_scope', 'independent_replication'}, 'catalog source')
        identifier(source['id'], 'source id')
        for field in ('title', 'date', 'date_basis', 'url', 'supported_claim', 'evidence_type', 'verification_scope'):
            text(source[field], 'source ' + field)
        url = urlsplit(source['url'])
        if url.scheme != 'https' or not url.hostname or url.username or url.password:
            raise ContractError('source must use an unauthenticated HTTPS reference')
        if source['id'] in source_ids or source['url'] in source_urls:
            raise ContractError('duplicate source identity or URL')
        if source['independent_replication'] is not False:
            raise ContractError('source catalog cannot manufacture independent replication')
        source_ids.add(source['id']); source_urls.add(source['url'])
    if type(value['techniques']) is not list or not 1 <= len(value['techniques']) <= 512:
        raise ContractError('invalid technique inventory')
    seen = set(); counts = {'inference': 0, 'training': 0}
    for row in value['techniques']:
        keys(row, {'id', 'name', 'domains', 'family', 'mechanism', 'source_ids', 'semantic_effect',
                   'model_changes', 'applicability', 'prerequisites', 'required_capabilities',
                   'interaction_risks', 'limitations', 'local_scope_note'}, 'technique')
        identifier(row['id'], 'technique id')
        if row['id'] in seen:
            raise ContractError('duplicate technique identity')
        seen.add(row['id'])
        for field in ('name', 'family', 'mechanism', 'semantic_effect', 'model_changes', 'local_scope_note'):
            text(row[field], 'technique ' + field)
        for field in ('domains', 'source_ids', 'applicability', 'prerequisites', 'required_capabilities',
                      'interaction_risks', 'limitations'):
            texts(row[field], 'technique ' + field)
        if set(row['domains']) - counts.keys() or set(row['source_ids']) - source_ids:
            raise ContractError('unknown technique domain or source')
        for domain in row['domains']:
            counts[domain] += 1
    for domain, count in counts.items():
        integer(value['coverage'][domain+'_families'], 0, 512, 'family count')
        if value['coverage'][domain+'_families'] != count:
            raise ContractError('declared catalog coverage differs from inventory')
    texts(value['composition_rules'], 'composition rules')
    if type(value['evaluation_cautions']) is not list or len(value['evaluation_cautions']) > 32:
        raise ContractError('invalid evaluator caution inventory')
    for caution in value['evaluation_cautions']:
        keys(caution, {'source_ids', 'finding', 'implication'}, 'evaluation caution')
        texts(caution['source_ids'], 'caution sources')
        if set(caution['source_ids']) - source_ids:
            raise ContractError('unknown evaluation caution source')
        text(caution['finding'], 'caution finding'); text(caution['implication'], 'caution implication')
    canonical_bytes(value)
    return value


def technique_support(technique_id):
    # Catalog descriptions never grant a capability or authorize execution.
    if technique_id == 'prefix-cache':
        return {'state': 'IMPLEMENTED_REVIEWED_CPU_CONTROL',
                'adapter': 'reviewed-cpu-prefix-cache-v2',
                'scope': 'Same-slot prefix cache toggle only, through validated v2 recipes; admission still required.'}
    return {'state': 'CATALOG_ONLY', 'adapter': None,
            'scope': 'Published mechanism, not an executable local integration.'}


def catalog_view(domain=None, available_only=False, technique_id=None):
    value = catalog()
    selected = []
    for row in value['techniques']:
        if domain and domain not in row['domains']:
            continue
        if technique_id and row['id'] != technique_id:
            continue
        row['local_support'] = technique_support(row['id'])
        if available_only and row['local_support']['adapter'] is None:
            continue
        selected.append(row)
    if technique_id and not selected:
        raise ContractError('technique is absent from the selected catalog/domain')
    return {'schema_version': 1, 'catalog_id': value['catalog_id'],
            'catalog_sha256': digest(value), 'coverage': value['coverage'],
            'techniques': selected, 'sources': value['sources'],
            'execution_performed': False,
            'scope': 'Source-backed discovery catalog; support is an explicit code binding, not a paper claim.'}


def template(template_id, *, frozen_catalog=None):
    from .research_proposals import PROPOSALS
    if template_id not in PROPOSALS:
        raise ContractError('unknown research template')
    return validate_proposal(copy.deepcopy(PROPOSALS[template_id]), frozen_catalog=frozen_catalog)


def template_list():
    from .research_proposals import PROPOSALS
    return [{'id': k, 'title': v['title'], 'domain': v['domain'],
             'kind': v['kind'], 'objective': v['objective'], 'novelty': v['novelty']['status']}
            for k, v in PROPOSALS.items()]


def validate_proposal(value, *, frozen_catalog=None):
    keys(value, PROPOSAL_FIELDS, 'research proposal')
    integer(value['schema_version'], 1, 1, 'research schema')
    identifier(value['id'], 'proposal id')
    identifier(value['mechanism_id'], 'mechanism id')
    for field in ('title', 'mechanism', 'prediction', 'baseline', 'candidate_delta', 'claim_limit'):
        text(value[field], field)
    if value['domain'] not in ('inference', 'training', 'joint'):
        raise ContractError('unknown research domain')
    if value['kind'] not in ('known_method_control', 'new_combination', 'mechanism_hypothesis'):
        raise ContractError('unknown research kind')
    if value['objective'] not in ('efficiency_at_quality', 'quality_at_budget', 'frontier_shift'):
        raise ContractError('unknown research objective')
    if value['stage'] not in ('synthetic_falsifier', 'operator_prototype', 'tiny_model',
                              'llm_development', 'protected_confirmation'):
        raise ContractError('unknown research stage')
    for field in ('invariants', 'ablations', 'falsifiers', 'required_capabilities', 'stop_rules'):
        texts(value[field], field)
    unknown = set(value['required_capabilities']) - CAPABILITIES.keys()
    if unknown:
        raise ContractError('unknown required capabilities: ' + ', '.join(sorted(unknown)))
    known = catalog() if frozen_catalog is None else validate_catalog(frozen_catalog)
    technique_ids = {t['id'] for t in known['techniques']}
    texts(value['technique_ids'], 'technique_ids', minimum=0)
    if set(value['technique_ids']) - technique_ids:
        raise ContractError('proposal refers to an unknown technique')
    source_ids = {s['id'] for s in known['sources']}
    if type(value['prior_art']) is not list or not 1 <= len(value['prior_art']) <= 32:
        raise ContractError('prior art must name bounded source comparisons')
    seen = set()
    for item in value['prior_art']:
        keys(item, {'source_id', 'overlap', 'proposed_difference'}, 'prior art comparison')
        identifier(item['source_id'], 'prior art source id')
        if item['source_id'] not in source_ids or item['source_id'] in seen:
            raise ContractError('unknown or duplicate prior art source')
        seen.add(item['source_id'])
        text(item['overlap'], 'prior art overlap'); text(item['proposed_difference'], 'proposed difference')
    keys(value['quality_contract'], {'metric', 'direction', 'decision_rule', 'evaluation_revision',
                                     'population', 'semantic_equivalence'}, 'quality contract')
    for field, item in value['quality_contract'].items():
        text(item, 'quality ' + field)
    if value['quality_contract']['direction'] not in ('higher', 'lower'):
        raise ContractError('quality direction must be explicit')
    if type(value['metrics']) is not list or not 1 <= len(value['metrics']) <= 16:
        raise ContractError('metrics must contain bounded explicit definitions')
    metric_names = set()
    for item in value['metrics']:
        keys(item, {'name', 'unit', 'direction', 'decision_rule'}, 'metric')
        for field, entry in item.items():
            text(entry, 'metric ' + field)
        if item['direction'] not in ('higher', 'lower') or item['name'] in metric_names:
            raise ContractError('invalid metric direction or duplicate metric')
        metric_names.add(item['name'])
    keys(value['resources'], {'cpu_threads', 'memory_bytes', 'disk_bytes', 'wall_seconds',
                              'gpu_requirement'}, 'proposed resource needs')
    for field, upper in [('cpu_threads', 4096), ('memory_bytes', 10**16),
                         ('disk_bytes', 10**18), ('wall_seconds', 365*24*3600)]:
        integer(value['resources'][field], 1, upper, field)
    text(value['resources']['gpu_requirement'], 'gpu_requirement')
    keys(value['evaluation'], {'development', 'confirmation', 'selection_rule'}, 'evaluation plan')
    for field, item in value['evaluation'].items():
        text(item, 'evaluation ' + field)
    keys(value['novelty'], {'status', 'search_scope', 'unresolved_questions'}, 'novelty assessment')
    if value['novelty']['status'] not in ('KNOWN_METHOD', 'UNVERIFIED', 'OVERLAP_IDENTIFIED'):
        raise ContractError('this research plane cannot certify novelty')
    if (value['kind'] == 'known_method_control') != (value['novelty']['status'] == 'KNOWN_METHOD'):
        raise ContractError('known controls and speculative novelty must remain distinct')
    text(value['novelty']['search_scope'], 'novelty search scope')
    texts(value['novelty']['unresolved_questions'], 'novelty unresolved questions')
    if value['domain'] in ('training', 'joint') and not any(
            c in value['required_capabilities'] for c in ('training-runtime', 'custom-model-training')):
        raise ContractError('training proposals must declare the missing training capability')
    if value['stage'] == 'protected_confirmation' and 'protected-confirmation-isolation' not in value['required_capabilities']:
        raise ContractError('confirmation requires protected evaluator isolation')
    canonical_bytes(value)
    return value


def readiness(value, *, frozen_catalog=None):
    known = catalog() if frozen_catalog is None else frozen_catalog
    validate_proposal(value, frozen_catalog=known)
    missing = {c: CAPABILITIES[c] for c in value['required_capabilities'] if CAPABILITIES[c] != 'IMPLEMENTED'}
    required = template('prefix-cache-control', frozen_catalog=known); required['id'] = value['id']
    from .recipes_v3 import MECHANISMS
    compiles = canonical_bytes(value) == canonical_bytes(required) or (
        value['domain'] == 'inference' and value['mechanism_id'] in MECHANISMS and
        value['stage'] == 'llm_development')
    return {'proposal_sha256': digest(value), 'catalog_sha256': digest(known),
            'status': 'RESEARCH_PROPOSAL_ONLY', 'missing_capabilities': missing,
            'supported_recipe_compiler': compiles and not missing,
            'execution_authorized': False, 'execution_performed': False,
            'remaining_gates': ['exact immutable implementation/data/evaluator and resource admission',
                                'stage-specific observed evidence; proposal validation proves structure only'],
            'novelty_status': value['novelty']['status']}


def composition(technique_ids):
    texts(technique_ids, 'composition techniques')
    known = {t['id']: t for t in catalog()['techniques']}
    if set(technique_ids) - known.keys():
        raise ContractError('unknown composition technique')
    rows = [{'id': t, 'local_support': technique_support(t),
             'interaction_risks': known[t]['interaction_risks']} for t in technique_ids]
    only_supported = technique_ids == ['prefix-cache']
    return {'techniques': rows, 'composition_verified': only_supported,
            'supported_recipe_compiler': only_supported, 'execution_authorized': False,
            'status': 'SUPPORTED_SINGLE_CONTROL' if only_supported else 'INTEGRATION_AND_INTERACTION_TESTS_REQUIRED',
            'scope': 'Benefits do not multiply automatically; each combination needs matched ablations and admission.'}


def freeze_proposal(value, output):
    validate_proposal(value)
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise FileExistsError('choose a new immutable research bundle')
    frozen_catalog = catalog()
    result = readiness(value)
    result.update(schema_version=1, status='FROZEN_RESEARCH_PROPOSAL_NOT_EXECUTED',
                  files={'proposal.json': digest(value), 'catalog.json': digest(frozen_catalog)},
                  integrity_limit='Local immutable hashes are not independent authenticity or novelty evidence.')
    output.mkdir(parents=True, exist_ok=False)
    write_json_new(output/'proposal.json', value)
    write_json_new(output/'catalog.json', frozen_catalog)
    write_json_new(output/'RESEARCH-MANIFEST.json', result)
    return result


def verify_frozen(root):
    root = Path(root)
    names = {'proposal.json', 'catalog.json', 'RESEARCH-MANIFEST.json'}
    if root.is_symlink() or not root.is_dir() or {p.name for p in root.iterdir()} != names:
        raise ContractError('research bundle inventory is incomplete or unexpected')
    for name in names:
        path = root/name
        if path.is_symlink() or not path.is_file():
            raise ContractError('research bundle members must be regular files')
    frozen_catalog = validate_catalog(read_json(root/'catalog.json', max_bytes=4*1024*1024))
    proposal = validate_proposal(read_json(root/'proposal.json', max_bytes=256*1024), frozen_catalog=frozen_catalog)
    manifest = read_json(root/'RESEARCH-MANIFEST.json', max_bytes=256*1024)
    keys(manifest, {'schema_version', 'proposal_sha256', 'catalog_sha256', 'status',
                   'missing_capabilities', 'supported_recipe_compiler', 'execution_authorized',
                   'execution_performed', 'remaining_gates', 'novelty_status', 'files',
                   'integrity_limit'}, 'research manifest')
    if (type(manifest['schema_version']) is not int or manifest['schema_version'] != 1 or
            manifest['status'] != 'FROZEN_RESEARCH_PROPOSAL_NOT_EXECUTED' or
            manifest['execution_authorized'] is not False or manifest['execution_performed'] is not False or
            manifest['proposal_sha256'] != digest(proposal) or manifest['catalog_sha256'] != digest(frozen_catalog) or
            manifest['files'] != {'proposal.json': digest(proposal), 'catalog.json': digest(frozen_catalog)} or
            manifest['novelty_status'] != proposal['novelty']['status']):
        raise ContractError('research bundle hashes, scope or novelty state differ')
    expected = readiness(proposal, frozen_catalog=frozen_catalog)
    for field in ('missing_capabilities', 'supported_recipe_compiler', 'remaining_gates'):
        if canonical_bytes(manifest[field]) != canonical_bytes(expected[field]):
            raise ContractError('research readiness metadata differs from registered capability rules')
    if manifest['integrity_limit'] != 'Local immutable hashes are not independent authenticity or novelty evidence.':
        raise ContractError('research integrity scope differs')
    return {'status': 'FROZEN_PROPOSAL_BYTES_VERIFIED', 'proposal_sha256': digest(proposal),
            'catalog_sha256': digest(frozen_catalog), 'execution_authorized': False,
            'scope': 'Retained catalog interpretation; hashes do not establish authenticity, novelty or executed results.'}


def compile_control(value, recipe, output):
    from .recipes import validate_recipe
    validate_proposal(value); validate_recipe(recipe)
    required = template('prefix-cache-control')
    observed = copy.deepcopy(value); required['id'] = observed['id']
    if canonical_bytes(observed) != canonical_bytes(required):
        raise ContractError('only the exact registered prefix-cache control can compile to the current adapter')
    limits = recipe['allocation']['limits']; requested = value['resources']
    if recipe['engine']['compute_threads'] > requested['cpu_threads'] or any(
            limits[a] > requested[b] for a, b in [('memory_bytes', 'memory_bytes'),
            ('disk_bytes', 'disk_bytes'), ('full_wall_seconds', 'wall_seconds')]):
        raise ContractError('recipe envelope exceeds the frozen research control ceiling')
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise FileExistsError('choose a new compiled research directory')
    result = {'schema_version': 1, 'status': 'COMPILED_KNOWN_CONTROL_NEEDS_RUN_ADMISSION',
              'proposal_sha256': digest(value), 'recipe_sha256': digest(recipe),
              'catalog_sha256': digest(catalog()), 'technique_id': 'prefix-cache',
              'candidate_delta': {'cache_prompt': {'baseline': False, 'candidate': True}},
              'execution_authorized': False, 'execution_performed': False,
              'scope': 'Recipe canonical content unchanged; ordinary run admission and all quality/cost rules still apply. No novelty claim.'}
    output.mkdir(parents=True, exist_ok=False)
    write_json_new(output/'proposal.json', value); write_json_new(output/'recipe.json', recipe)
    write_json_new(output/'EXPERIMENT-LINK.json', result)
    return result
