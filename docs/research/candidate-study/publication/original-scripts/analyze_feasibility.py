#!/usr/bin/env python3
"""Read retained product evidence only; never run models or recompute reports."""
import argparse,csv,hashlib,json,math,pathlib,time
p=argparse.ArgumentParser();p.add_argument('--study',type=pathlib.Path,required=True);p.add_argument('--report',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(p.read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
workload=read(a.study/'workload.json'); report=read(a.report)
expected={r['request_id']:r['expected'] for r in workload['requests']}
raw=[read(p) for p in sorted((a.study/'attempts').glob('*.json'))]
reported={x['attempt_id']:x for x in report['attempts']}
requests=[];attempts=[];pairs=[]
for attempt in raw:
 rr=reported[attempt['attempt_id']]; lookup={r['request_id']:r for r in attempt['requests']}
 for rid,ans in expected.items():
  r=lookup.get(rid,{});out=r.get('output_text','');ok=r.get('status')=='SUCCEEDED' and out.strip()==ans
  requests.append({'attempt_id':attempt['attempt_id'],'pair_index':attempt['pair_index'],'arm':attempt['arm'],'request_id':rid,'expected':ans,'output':out,'correct':ok,'status':r.get('status','MISSING'),'finish_reason':r.get('finish_reason'),'prompt_tokens':r.get('prompt_tokens'),'generated_tokens':r.get('generated_tokens'),'dispatch_completion_s':(r['completed_ns']-r['dispatch_ns'])/1e9 if r.get('completed_ns') is not None and r.get('dispatch_ns') is not None else None})
 n=sum(r['correct'] for r in requests if r['attempt_id']==attempt['attempt_id'])
 assert n==rr['quality_correct'],(n,rr['quality_correct'])
 attempts.append({'attempt_id':attempt['attempt_id'],'pair_index':attempt['pair_index'],'arm':attempt['arm'],'offered':len(expected),'correct':n,'accuracy':n/len(expected),'quality_pass':rr['quality_pass'],'full_wall_s':rr['full_wall_ns']/1e9,'service_s':rr['service_ns']/1e9,'end_to_end_p95_s':rr['latency']['client_end_to_end_ns']['p95']/1e9,'ttft_p95_s':rr['latency']['client_ttft_ns']['p95']/1e9,'prompt_tokens':rr['prompt_tokens_observed'],'generated_tokens':rr['generated_tokens_reported'],'limit_completions':rr['truncated_requests'],'eligible':rr['eligible']})
for pi in sorted({x['pair_index'] for x in raw}):
 arm={arm:{r['request_id']:r for r in requests if r['pair_index']==pi and r['arm']==arm} for arm in ('baseline','candidate')}
 classes={'both_correct':0,'full_correct_candidate_wrong':0,'full_wrong_candidate_correct':0,'both_wrong':0}
 for rid in expected:
  b,c=arm['baseline'][rid]['correct'],arm['candidate'][rid]['correct'];classes['both_correct' if b and c else 'full_correct_candidate_wrong' if b else 'full_wrong_candidate_correct' if c else 'both_wrong']+=1
 ar={x['arm']:x for x in attempts if x['pair_index']==pi}
 pairs.append({'pair_index':pi,'denominator':len(expected),**classes,'candidate_minus_baseline_correct':ar['candidate']['correct']-ar['baseline']['correct'],'descriptive_candidate_over_full_wall':ar['candidate']['full_wall_s']/ar['baseline']['full_wall_s'],'efficiency_claim_eligible':False})
for name,rows in [('requests',requests),('attempts',attempts),('pairs',pairs)]:
 with (a.output/(name+'.csv')).open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
account=report['accounting'];queue=read(pathlib.Path(str(a.study)+'.queue')/'receipt.json')
summary={'schema_version':1,'scope':'Development feasibility only; descriptive costs do not imply an eligible efficiency claim. Repetitions share eight unique questions.','inputs':{'study':str(a.study),'report':str(a.report),'report_sha256':digest(a.report),'workload_sha256':digest(a.study/'workload.json'),'analysis_sha256':digest(pathlib.Path(__file__))},'created_monotonic_ns':time.monotonic_ns(),'attempts':attempts,'pairs':pairs,'budget':{'native_offered':len(raw)*len(expected),'unique_questions':len(expected),'attempt_full_wall_s':account['full_wall_ns']/1e9,'queue_execution_wall_s':(queue['finished_ns']-queue['execution_started_ns'])/1e9,'setup_accounting':account['setup_acquisition_build_costs'],'original_allocation_accounting':account['full_cost_accounting'],'warning':'Original allocation accounting already includes setup and prior work: never add overlapping totals. Monetary cost, thermal and energy remain unavailable.'},'eligible':report['eligible']}
(a.output/'analysis.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'attempts':attempts,'pairs':pairs,'native_offered':summary['budget']['native_offered'],'output':str(a.output)},indent=2))
