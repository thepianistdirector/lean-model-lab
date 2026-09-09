"""Combine validated attempt metrics with the authoritative session and setup costs."""
from __future__ import annotations

import json
from .contracts import digest
from .evidence import EvidenceError,evaluate_campaign


def evaluate_inventory(inventory: dict, *, study_root=None) -> dict:
    if not inventory['inventory_complete']:
        raise EvidenceError('unfinished or unreconciled inventory: inspect and recover before reporting a comparison')
    result=evaluate_campaign(inventory['attempts'],inventory['workload'],config=inventory['config'],
        config_sha256=inventory['config_sha256'],workload_sha256=inventory['workload_sha256'])
    if inventory['config']['schema_version'] == 3 and inventory['config']['evidence_class'] == 'MEASURED':
        if study_root is None:
            raise EvidenceError('measured v3 reporting requires the raw producer directory')
        from .native_evidence import verify_native_inventory
        result['native_evidence_integrity']=verify_native_inventory(study_root,inventory)
    setup=inventory['setup_accounting']
    if inventory['config'].get('recipe',{}).get('mechanism_id')=='learned-gated-slice-v1':
        controller=inventory['config']['recipe']['controller']
        result['controller_training_provenance']={
            'controller_sha256':controller['controller_sha256'],'metadata':controller['metadata'],
            'mode':controller['parameters']['mode'],'formal_guarantee':False,
            'training_costs_status':'RETAINED_SEPARATELY_IN_NATIVE_TRAINING_PACKAGE',
            'scope':'Per-attempt comparisons include deployed controller preparation. Inspect the separately hashed label-source studies and training receipt before claiming amortized total-cost savings. The allocation span includes preceding work on that clock but is not a per-mechanism attribution.'}
    accounting=result['accounting'];accounting['setup_acquisition_build_costs']=setup
    from .ancestor_costs import preparation_ancestors
    ancestors=preparation_ancestors(setup['records'])
    if ancestors:accounting['historical_preparation_ancestors']=ancestors
    records=setup['records'];attempts=inventory['attempts']
    intervals=sorted([(r['started_ns'],r['finished_ns']) for r in records]+
                     [(a['started_ns'],a['finished_ns']) for a in attempts])
    if any(a[1]>b[0] for a,b in zip(intervals,intervals[1:])):
        raise EvidenceError('setup and attempt intervals overlap: refusing double-counted full costs')
    required={'source-acquisition','model-acquisition','build'}
    known=bool(records) and required<={r['phase'] for r in records if r['status']=='COMPLETED'}
    if known:
        result['measured_claim_eligible']=result['eligible'] and result['evidence_class']=='MEASURED'
        cutoff=intervals[-1][1]
        if cutoff<intervals[-1][1]:raise EvidenceError('report clock predates retained evidence')
        start=intervals[0][0]
        if inventory['config']['schema_version'] in (2,3):
            start=inventory['config']['recipe']['allocation']['started_ns']
            if any(a<start for a,b in intervals):raise EvidenceError('v2 retained cost predates its declared allocation')
        span=cutoff-start;attributed=sum(end-start for start,end in intervals)
        accounting['full_cost_accounting']={'status':'RECORDED','registered_full_wall_ns':span,
            'attributed_setup_and_attempt_ns':attributed,'unattributed_coordinator_or_idle_ns':span-attributed,
            'cutoff_ns':cutoff,'scope':'first retained setup phase through last retained producer observation; includes intervening idle/coordinator work',
            'current_report_publication':'separate report receipt in the rendering environment; never extends the producer clock'}
        if inventory['config']['schema_version'] in (2,3):
            accounting['full_cost_accounting']['scope']='original allocation start through last retained producer observation; all intervening development/idle/prior work remains charged'
            accounting['full_cost_accounting']['allocation_id']=inventory['config']['recipe']['allocation']['allocation_id']
    else:
        accounting['full_cost_accounting']={'status':'UNAVAILABLE','scope':'required acquisition/build receipt phases missing'}
        result['measured_claim_eligible']=False
        result['limitations'].append('Full setup costs are unverified; no complete study claim is eligible.')
    if known and accounting['full_cost_accounting']['registered_full_wall_ns']>inventory['config']['limits']['full_wall_seconds']*10**9:
        result['eligible']=False;result['measured_claim_eligible']=False
        result['finding']='INELIGIBLE'
        result['ineligibility_reasons'].append('registered_full_wall_allocation_exceeded')
        for group in result['concurrency_groups'].values():
            group['eligible']=False;group['finding']='INELIGIBLE'
    prior_protocol_failures=[r for r in records if r['phase']=='runtime-protocol-validation' and r['status']!='COMPLETED']
    if prior_protocol_failures:
        result['eligible']=False;result['measured_claim_eligible']=False;result['finding']='INELIGIBLE'
        result['ineligibility_reasons'].append('retained_prior_runtime_protocol_failure')
        result['limitations'].append('Earlier model requests failed protocol validation under a prior client implementation. '
            'Their original inventories and costs remain retained; corrected paired measurements are descriptive, '
            'not an eligible efficiency claim for this allocation.')
        accounting['prior_runtime_protocol_failures']=prior_protocol_failures
        for group in result['concurrency_groups'].values():
            group['eligible']=False;group['finding']='INELIGIBLE'
    if inventory['config']['schema_version'] in (2,3):
        prior_measurements=[]
        for row in records:
            if row['phase']!='predecessor-study-attempt':continue
            try: details=json.loads(row['details'])
            except (ValueError,TypeError) as exc:raise EvidenceError('invalid predecessor provenance') from exc
            if not isinstance(details,dict) or details.get('purpose') not in ('DEVELOPMENT','MEASUREMENT'):
                raise EvidenceError('missing predecessor purpose')
            if details['purpose']=='MEASUREMENT':
                # Older receipts lacking recipe identity cannot prove a distinct trial.
                if (details.get('source_recipe_sha256') in (None,digest(inventory['config']['recipe'])) or
                    details.get('source_config_sha256')==inventory['config_sha256']):
                    prior_measurements.append(row)
        if prior_measurements:
            result['eligible']=False;result['measured_claim_eligible']=False;result['finding']='INELIGIBLE'
            result['ineligibility_reasons'].append('retained_prior_same_recipe_measurement')
            result['limitations'].append('A prior measurement of this recipe is retained. Starting a new study cannot replace its adverse or successful outcome with a fresh eligible campaign.')
            accounting['prior_same_recipe_measurements']=prior_measurements
        if not known:
            result['eligible']=False;result['measured_claim_eligible']=False;result['finding']='INELIGIBLE'
            result['ineligibility_reasons'].append('required_setup_costs_unverified')
        if not result['eligible']:
            for group in result['concurrency_groups'].values():
                group['eligible']=False;group['finding']='INELIGIBLE'
                group['throughput_ratio_median']=None;group['throughput_ratio_range']=None
                group['pair_count']=0
                if 'full_wall_efficiency_ratio_median' in group:
                    group['full_wall_efficiency_ratio_median']=None;group['full_wall_efficiency_ratio_range']=None
                for pair in group['pairs']:
                    pair['eligible']=False;pair['throughput_candidate_over_baseline']=None
                    if 'full_wall_efficiency_candidate_over_baseline' in pair:pair['full_wall_efficiency_candidate_over_baseline']=None
                    for metric in ('end_to_end_tail_candidate_over_baseline','ttft_tail_candidate_over_baseline'):
                        pair[metric]={k:None for k in pair[metric]}
    result['inventory_integrity']={'reservation_count':inventory['reservation_count'],
        'event_count':inventory['event_count'],'complete':True,'scope':'immutable local events, normalized attempts and raw-file hashes'}
    return result
