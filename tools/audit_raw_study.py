#!/usr/bin/env python3
"""Reconcile finalized raw native responses against normalized measured requests."""
from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from lean_model_lab.artifacts import read_journal,write_json_new
from lean_model_lab.contracts import canonical_bytes,digest,file_digest,parse_json,read_json
from lean_model_lab.llama_adapter import normalize_response
from lean_model_lab.session import Session


def audit_request(request, records, prompt_count, slot, arm, **sampling):
    normalized=normalize_response(records,request_id=request['request_id'],arrival_ns=request['arrival_ns'],
        admitted_ns=request['admitted_ns'],dispatch_ns=request['dispatch_ns'],completed_ns=request['completed_ns'],
        prompt_tokens=prompt_count,slot=slot,**sampling)
    if canonical_bytes(normalized)!=canonical_bytes(request):
        raise ValueError('raw stream differs from normalized request')
    final=records[-1][1];timings=final.get('timings',{})
    for field in ('cache_n','prompt_n','predicted_n'):
        if type(timings.get(field)) is not int or timings[field]<0:
            raise ValueError('native timing token accounting missing or malformed')
    if timings['cache_n']+timings['prompt_n']!=prompt_count:
        raise ValueError('native cached plus newly processed input differs from admitted prompt')
    if timings['predicted_n']!=request['generated_tokens']:
        raise ValueError('native timing generated count differs from terminal accounting')
    if arm=='baseline' and timings['cache_n']!=0:
        raise ValueError('baseline unexpectedly reused a prompt prefix')
    progress=[p['prompt_progress'] for _,p in records if 'prompt_progress' in p]
    if not progress or any(p['cache']!=timings['cache_n'] for p in progress):
        raise ValueError('progress and terminal reused-prefix counts differ')
    return {'reused_input_tokens':timings['cache_n'],'new_input_tokens':timings['prompt_n'],
            'generated_tokens':timings['predicted_n'], 'progress_events':len(progress)}


def audit(root: Path) -> dict:
    started=time.monotonic_ns();reference_tokens=None;references_by_arm={};attempts=[]
    with Session.open(root) as session:
        inventory=session.inspect()
        if not inventory['inventory_complete']:raise ValueError('raw audit requires reconciled inventory')
        if inventory['config']['evidence_class']!='MEASURED':raise ValueError('this command audits measured studies, not fixtures')
        config=inventory['config']
        sampling={k:config['sampling'][k] for k in ('seed','max_output_tokens')} if config['schema_version'] in (2,3) else {}
        workload=inventory['workload'];indices={r['request_id']:i for i,r in enumerate(workload['requests'])}
        for attempt in inventory['attempts']:
            directory=root/'raw'/attempt['attempt_id']
            tokens=read_json(directory/'tokenized-inputs.json')
            if (set(tokens)!={'workload_sha256','tokens'} or tokens['workload_sha256']!=inventory['workload_sha256'] or
                type(tokens['tokens']) is not list or len(tokens['tokens'])!=len(workload['requests'])):
                raise ValueError('tokenized input inventory differs from workload')
            if config['schema_version'] == 3:
                from lean_model_lab.intervention_evidence import verify_interventions
                verify_interventions(root, inventory, attempt)
                prior = references_by_arm.setdefault(attempt['arm'], tokens)
                if canonical_bytes(prior) != canonical_bytes(tokens):
                    raise ValueError('actual tokenizer input IDs drifted within a registered arm')
                reference_tokens = references_by_arm
            elif reference_tokens is None:reference_tokens=tokens
            elif canonical_bytes(reference_tokens)!=canonical_bytes(tokens):
                raise ValueError('actual tokenizer input IDs drifted between attempts')
            request_ids={r['request_id'] for r in attempt['requests']}
            raw_ids={p.stem for p in directory.glob('r*.jsonl') if re.fullmatch(r'r[0-9]{3,4}',p.stem)}
            if not request_ids<=raw_ids or not raw_ids<=set(indices):
                raise ValueError('raw request files omit checkpoints or contain foreign request identities')
            if attempt['status']=='COMPLETED' and raw_ids!=request_ids:
                raise ValueError('completed attempt has uncheckpointed raw request files')
            counts={'request_count':len(request_ids),'successful_raw_reconciliations':0,
                    'failed_or_cancelled_requests':0,'local_non_dispatch_reconciliations':0,'missing_requests':len(indices)-len(request_ids),
                    'uncheckpointed_raw_requests':len(raw_ids-request_ids),
                    'reused_input_tokens':0,'new_input_tokens':0,'generated_tokens':0,'progress_events':0}
            for request in attempt['requests']:
                path=directory/(request['request_id']+'.jsonl');receipts,torn=read_journal(path)
                if torn:raise ValueError('torn raw stream receipt')
                if request['status'] in ('REJECTED','EXPIRED'):
                    expected_kind='queue_full' if request['status']=='REJECTED' else 'deadline'
                    if (len(receipts)!=1 or receipts[0].get('scheduler_outcome')!=expected_kind or
                        receipts[0].get('engine_dispatched') is not False or receipts[0].get('observed_ns')!=request['completed_ns']):
                        raise ValueError('local no-dispatch receipt differs from terminal outcome')
                    counts['local_non_dispatch_reconciliations']+=1;continue
                if request['status']!='SUCCEEDED':
                    counts['failed_or_cancelled_requests']+=1;continue
                if any('error' in r for r in receipts):raise ValueError('successful request retains an unaccounted stream error')
                records=[(r['observed_ns'],parse_json(r['data_utf8'])) for r in receipts
                         if 'data_utf8' in r and r['data_utf8']!='[DONE]']
                index=indices[request['request_id']]
                if config['schema_version'] == 3:
                    from lean_model_lab.recipes_v3 import cache_enabled
                    cache_allowed=cache_enabled(config['recipe'],attempt['arm'])
                else:cache_allowed=attempt['arm']=='candidate'
                metrics=audit_request(request,records,len(tokens['tokens'][index]),index%attempt['concurrency'],
                    'candidate' if cache_allowed else 'baseline',**sampling)
                counts['successful_raw_reconciliations']+=1
                for key,value in metrics.items():counts[key]+=value
            attempts.append({'attempt_id':attempt['attempt_id'],'arm':attempt['arm'],
                'concurrency':attempt['concurrency'],'pair_index':attempt['pair_index'],'status':attempt['status'],**counts})
        result={'schema_version':1,'status':'PASS' if all(a['status']=='COMPLETED' and not a['failed_or_cancelled_requests']
                 and not a['missing_requests'] for a in attempts) and attempts else 'INCOMPLETE_OR_FAILED',
                'scope':'Raw/normalized/actual-tokenizer/cache-accounting consistency; not independent execution, quality approval or external authentication.',
                'config_sha256':inventory['config_sha256'],'tokenized_inputs_sha256':digest(reference_tokens) if reference_tokens else None,
                'attempts':attempts,'candidate_reuse_observed':any(a['arm']=='candidate' and a['reused_input_tokens']>0 for a in attempts),
                'auditor_sha256':file_digest(Path(__file__)),'started_ns':started,'finished_ns':time.monotonic_ns()}
        return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study',type=Path);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    try:
        result=audit(args.study);write_json_new(args.output,result)
        print(result['status']+': '+str(sum(a['successful_raw_reconciliations'] for a in result['attempts']))+' raw requests reconciled')
    except (OSError,ValueError) as exc:
        print('lean-model-lab raw audit: '+str(exc),file=sys.stderr);raise SystemExit(2)
