"""Prospective, native-evidence-backed training of the small acceptance controller.

Local hashes and clocks enforce accidental-mixup checks, not authentication
against another process with the same filesystem identity. No LLM is trained.
"""
from __future__ import annotations
import time
from pathlib import Path
from .contracts import ContractError, canonical_bytes, digest, keys, read_json
from .artifacts import write_json_new
from .recipes import validate_recipe, schedule
from .session import Session
from .native_evidence import verify_native_inventory
from .acceptance_controller import extract_features, fit_controller

PROTOCOL_KEYS={'schema_version','kind','frozen_ns','fit_recipe_sha256s',
    'calibration_recipe_sha256s','label_rule','selection_rule','scope'}
LABEL_RULE='All repetitions must be correct per arm; sum dispatch-to-completion request costs per arm; retain all four outcome classes.'
SELECTION_RULE='Depth-two binary harmful-omission Gini; fixed grid 0,.05,.1,.25,.5,1; at least 8 accepted, zero observed calibration harm, >=95% routed calibration accuracy, positive request saving; maximum saving then lowest threshold; otherwise ALWAYS_FULL.'
SCOPE='Actual small-controller training only; workflow isolation, no LLM training, population-risk, novelty or full-cost guarantee.'


def _development_recipe(recipe):
    validate_recipe(recipe)
    if (recipe['schema_version']!=3 or recipe['purpose']!='DEVELOPMENT' or
        recipe['mechanism_id']!='dependency-slice-v1' or
        recipe['workload_generator']['split']!='development' or
        recipe['evaluation']['concurrency_modes']!=[1]):
        raise ContractError('controller labels require development dependency-slice v3 recipes at concurrency one')


def make_training_protocol(fit_recipes, calibration_recipes):
    if not fit_recipes or not calibration_recipes:
        raise ContractError('training requires nonempty fit and calibration recipe populations')
    for recipe in fit_recipes+calibration_recipes:_development_recipe(recipe)
    identities=[digest(r) for r in fit_recipes+calibration_recipes]
    if len(set(identities))!=len(identities):
        raise ContractError('fit and calibration recipes must be unique and disjoint')
    # Prompt/table groups are also checked using actual workloads at fitting time.
    return validate_training_protocol({'schema_version':1,'kind':'NATIVE_CONTROLLER_TRAINING_PROTOCOL',
        'frozen_ns':time.monotonic_ns(),'fit_recipe_sha256s':sorted(digest(r) for r in fit_recipes),
        'calibration_recipe_sha256s':sorted(digest(r) for r in calibration_recipes),
        'label_rule':LABEL_RULE,'selection_rule':SELECTION_RULE,'scope':SCOPE})


def validate_training_protocol(value):
    from .config import _sha
    keys(value,PROTOCOL_KEYS,'controller training protocol')
    if (type(value['schema_version']) is not int or value['schema_version']!=1 or
        value['kind']!='NATIVE_CONTROLLER_TRAINING_PROTOCOL' or
        type(value['frozen_ns']) is not int or value['frozen_ns']<=0 or
        value['label_rule']!=LABEL_RULE or value['selection_rule']!=SELECTION_RULE or value['scope']!=SCOPE):
        raise ContractError('controller training protocol differs from registered semantics')
    all_ids=[]
    for name in ('fit_recipe_sha256s','calibration_recipe_sha256s'):
        ids=value[name]
        if type(ids) is not list or not ids or len(ids)>64 or ids!=sorted(ids):
            raise ContractError('training recipe identities must be nonempty bounded sorted lists')
        for identity in ids:_sha(identity,'training recipe')
        all_ids+=ids
    if len(all_ids)!=len(set(all_ids)):
        raise ContractError('training recipes overlap')
    return value


def collect_native_labels(roots, protocol, split):
    validate_training_protocol(protocol)
    if split not in ('fit','calibration'):raise ContractError('invalid training split')
    rows=[];sources=[];binding=None
    for root in sorted(map(Path,roots),key=str):
        with Session.open(root) as session:inventory=session.inspect()
        config=inventory['config'];recipe=config['recipe'];_development_recipe(recipe)
        if config['evidence_class']!='MEASURED' or not inventory['inventory_complete']:
            raise ContractError('controller training requires reconciled actual native measured outputs')
        attempts=inventory['attempts']
        expected=set(schedule(config))
        cells=[(a['concurrency'],a['pair_index'],a['arm']) for a in attempts]
        if len(cells)!=len(expected) or set(cells)!=expected or any(a['status']!='COMPLETED' for a in attempts):
            raise ContractError('controller labels require all prospective paired arms once, with no failed or replacement cells')
        if min(a['started_ns'] for a in attempts)<protocol['frozen_ns']:
            raise ContractError('controller training protocol must predate native label collection')
        observed_binding={'model_profile_id':recipe['model_profile_id'],
            'model_profile_sha256':recipe['model_profile_sha256'],
            'template_sha256':config['tokenizer']['template_sha256'],
            'source_build_sha256':config['implementation_sha256']}
        if binding is None:binding=observed_binding
        if binding!=observed_binding:raise ContractError('controller label sources differ in model, template or producer implementation')
        native=verify_native_inventory(root,inventory)
        by_arm={arm:[{r['request_id']:r for r in a['requests']} for a in attempts if a['arm']==arm]
                for arm in ('baseline','candidate')}
        for source in inventory['workload']['requests']:
            features=extract_features(source['prompt'])
            if features is None:raise ContractError('training population contains unsupported grammar')
            row={'source_id':digest(source['prompt']),
                # All queries sharing an exact table are one unit, irrespective of ASK.
                'group_id':digest(source['prompt'].split('\n')[5:-3]),'features':features}
            for arm,prefix in [('baseline','full'),('candidate','slice')]:
                observations=[]
                for attempt_rows in by_arm[arm]:
                    if source['request_id'] not in attempt_rows:raise ContractError('training arm omitted offered request')
                    observations.append(attempt_rows[source['request_id']])
                if any(r['status']!='SUCCEEDED' for r in observations):
                    raise ContractError('failed native labels remain evidence but cannot become fitted success data')
                row[prefix+'_correct']=all(r['output_text'].strip()==source['expected'] for r in observations)
                row[prefix+'_request_ns']=sum(r['completed_ns']-r['dispatch_ns'] for r in observations)
            rows.append(row)
        sources.append({'study_name':root.name,'recipe_sha256':digest(recipe),
            'config_sha256':inventory['config_sha256'],'workload_sha256':inventory['workload_sha256'],
            'attempts_sha256':digest(attempts),'native_integrity':native,
            'attempt_full_wall_ns':sum(a['finished_ns']-a['started_ns'] for a in attempts),
            'offered_native_requests':sum(len(inventory['workload']['requests']) for a in attempts)})
    actual=sorted(s['recipe_sha256'] for s in sources)
    if actual!=protocol[split+'_recipe_sha256s']:
        raise ContractError('actual native label population differs from frozen training protocol')
    rows.sort(key=lambda r:r['source_id'])
    return {'schema_version':1,'kind':'NATIVE_CONTROLLER_LABELS','split':split,
        'training_protocol_sha256':digest(protocol),'binding':binding,'sources':sources,'rows':rows,
        'scope':'Raw-audited actual development model responses; paired all-repetition correctness, dispatch-to-completion cost proxy, no independence or full-cost claim.'}


def train_native_controller(*, fit_studies, calibration_studies, protocol, output):
    output=Path(output)
    if output.exists():raise ContractError('controller output must be new; training attempts are never replaced')
    output.mkdir(parents=True)
    started=time.monotonic_ns()
    write_json_new(output/'training-protocol.json',validate_training_protocol(protocol))
    try:
        fit=collect_native_labels(fit_studies,protocol,'fit')
        write_json_new(output/'fit-labels.json',fit)
        calibration=collect_native_labels(calibration_studies,protocol,'calibration')
        write_json_new(output/'calibration-labels.json',calibration)
        if fit['binding']!=calibration['binding']:
            raise ContractError('fit and calibration model/build identities differ')
        metadata={**fit['binding'],'fit_source_sha256':digest(fit),'calibration_source_sha256':digest(calibration)}
        training_started=time.monotonic_ns()
        controller=fit_controller(fit['rows'],calibration['rows'],metadata=metadata)
        training_finished=time.monotonic_ns()
        write_json_new(output/'controller.json',controller)
        receipt={'status':'COMPLETED','controller_sha256':digest(controller),
            'protocol_sha256':digest(protocol),'started_ns':started,'finished_ns':time.monotonic_ns(),
            'fit_and_calibration_ns':training_finished-training_started,
            'label_collection_attempt_wall_ns':sum(s['attempt_full_wall_ns'] for d in (fit,calibration) for s in d['sources']),
            'scope':'Current training/validation process costs plus separate source attempt durations; original allocation span and shared acquisition costs remain separate, never added per study.'}
    except Exception as exc:
        write_json_new(output/'training-receipt.json',{'status':'FAILED','started_ns':started,
            'finished_ns':time.monotonic_ns(),'error':str(exc),'scope':SCOPE})
        raise
    write_json_new(output/'training-receipt.json',receipt)
    return receipt
