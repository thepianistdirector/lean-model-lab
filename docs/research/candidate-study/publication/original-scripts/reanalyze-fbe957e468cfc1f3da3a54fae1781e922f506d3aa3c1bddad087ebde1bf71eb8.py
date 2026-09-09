#!/usr/bin/env python3
"""Independent descriptive analysis of retained product studies, with no inference.

The per-pair oracle chooses only between that pair's observed full/slice outputs.
The conservative oracle selects an arm correct in every retained repetition.
Neither object is a model or an executable serving policy.
"""
import argparse,collections,csv,hashlib,json,pathlib,time

def read(path): return json.loads(path.read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def parse(prompt):
 lines=prompt.splitlines();start=lines.index('BEGIN');end=lines.index('END');body=lines[start+1:end];final={}
 for pos,line in enumerate(body):
  op,key,value=line.split();assert op in ('VALUE','REF');final[key]=(op,value,pos)
 ask=lines[end+1].split();assert ask[0]=='ASK';key=ask[1];seen=set();positions=[]
 while True:
  if key in seen or key not in final:raise ValueError('missing or cyclic dependency')
  seen.add(key);op,value,pos=final[key];positions.append(pos)
  if op=='VALUE':break
  key=value
 total=len(body)
 return {'family':lines[1].split()[1],'expected':value,'body':body,'group_id':canonical(body),'features':{'closure_records':len(positions),'max_retained_position_permille':max(positions)*1000//max(total-1,1),'min_retained_position_permille':min(positions)*1000//max(total-1,1),'overwritten_writes':total-len(final),'total_records':total}}
def csv_write(path,rows):
 if not rows:return
 with path.open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
def outcomes(rows):
 counter=collections.Counter(r['outcome'] for r in rows)
 return {key:counter[key] for key in ['both_correct','full_only_correct','candidate_only_correct','both_wrong']}
def strata(r):
 f=r['features']
 def position(x):return '0-333' if x<=333 else '334-666' if x<=666 else '667-1000'
 return [('all','all'),('family',r['family']),('closure_records',str(f['closure_records']) if f['closure_records']<3 else '3+'),('overwritten_writes','0' if f['overwritten_writes']==0 else '1+'),('min_retained_position_permille',position(f['min_retained_position_permille'])),('max_retained_position_permille',position(f['max_retained_position_permille']))]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--manifest',type=pathlib.Path,required=True);ap.add_argument('--evidence-root',type=pathlib.Path);ap.add_argument('--output',type=pathlib.Path,required=True);args=ap.parse_args();manifest=read(args.manifest);base=(args.evidence_root or args.manifest.parent).resolve()
 if args.output.exists():raise SystemExit('Output must be a new directory')
 args.output.mkdir(parents=True)
 assert manifest['schema_version']==1 and isinstance(manifest['studies'],list),'Unsupported evidence manifest'
 assert len({e['id'] for e in manifest['studies']})==len(manifest['studies']),'Duplicate logical study IDs'
 def resolve(value):return (base/value).resolve()
 requests=[];attempts=[];paired=[];oracles=[];checks=[];costs=[];inventory=[];tables={};all_pair_rows={};workload_rows={};stability=[]
 for entry in manifest['studies']:
  study=resolve(entry['study']);study_id=entry['id'];report_path=resolve(entry['report']);queue_path=resolve(entry['queue_receipt'])
  for key,path in [('config_sha256',study/'config.json'),('workload_sha256',study/'workload.json'),('report_sha256',report_path),('queue_sha256',queue_path)]:assert sha(path)==entry['expected'][key],'Manifest hash mismatch: '+study_id+' '+key
  workload=read(study/'workload.json');config=read(study/'config.json');recipe=config['recipe'];mechanism=recipe['mechanism_id'];phase=recipe['purpose'];report=read(report_path)
  workload_rows[study_id]=workload['requests'];source={r['request_id']:r for r in workload['requests']};parsed={rid:parse(r['prompt']) for rid,r in source.items()};tables[study_id]={rid:r['group_id'] for rid,r in parsed.items()}
  for rid,r in parsed.items():assert r['expected']==source[rid]['expected'],'Independent full-context answer mismatch'
  ra=[read(f) for f in sorted((study/'attempts').glob('*.json'))];rr={a['attempt_id']:a for a in report['attempts']};by_pair={}
  cells=[(a['pair_index'],a['arm']) for a in ra];assert len(cells)==len(set(cells)),'Duplicate attempts cannot be silently replaced'
  for a in ra:
   ar=rr[a['attempt_id']];lookup={r['request_id']:r for r in a['requests']};trace_path=study/'raw'/a['attempt_id']/'prompt-interventions.json';trace=read(trace_path) if trace_path.exists() else None;trace_rows={r['request_id']:r['result'] for r in trace.get('requests',[])} if trace else {}
   count=0
   for rid,src in source.items():
    r=lookup.get(rid,{});correct=r.get('status')=='SUCCEEDED' and r.get('output_text','').strip()==src['expected'];count+=correct;t=trace_rows.get(rid);actual_prompt=t['prompt'] if t else src['prompt'];same_semantics=None
    if mechanism=='explicit-grammar-v2' and a['arm']=='candidate':
     instructions=read(resolve(manifest['instruction_bindings'][study_id]))['instructions'];desired=src['prompt'].splitlines()
     for index,key in [(0,'language'),(2,'rules'),(3,'output')]:desired[index]=instructions[key]
     assert actual_prompt.splitlines()==desired,'Explicit diagnosis changed more than the fixed instructions'
    try: same_semantics=parse(actual_prompt)['expected']==src['expected']
    except ValueError: same_semantics=False
    if a['arm']=='baseline' or mechanism in ('dependency-slice-v1','simple-gated-slice-v1','learned-gated-slice-v1'):assert same_semantics,'Semantics-preserving policy changed interpreter answer'
    row={'study':study_id,'phase':phase,'mechanism':mechanism,'attempt_id':a['attempt_id'],'pair_index':a['pair_index'],'arm':a['arm'],'request_id':rid,'group_id':parsed[rid]['group_id'],'family':parsed[rid]['family'],'expected':src['expected'],'output':r.get('output_text',''),'correct':correct,'status':r.get('status','MISSING'),'finish_reason':r.get('finish_reason'),'prompt_tokens':r.get('prompt_tokens'),'generated_tokens':r.get('generated_tokens'),'dispatch_completion_s':(r['completed_ns']-r['dispatch_ns'])/1e9 if r.get('completed_ns') is not None and r.get('dispatch_ns') is not None else None,'decision':t['decision'] if t else 'BASELINE_FULL','retained_records':t['certificate']['retained_record_count'] if t else parsed[rid]['features']['total_records'],'symbolic_answer_preserved':same_semantics,**parsed[rid]['features']};requests.append(row);by_pair.setdefault(a['pair_index'],{}).setdefault(a['arm'],{})[rid]=row
   assert count==ar['quality_correct'],'Independent quality differs from product'
   attempts.append({'study':study_id,'phase':phase,'mechanism':mechanism,'attempt_id':a['attempt_id'],'pair_index':a['pair_index'],'arm':a['arm'],'offered':len(source),'correct':count,'accuracy':count/len(source),'full_wall_s':ar['full_wall_ns']/1e9,'service_s':ar['service_ns']/1e9,'end_to_end_p95_s':ar['latency']['client_end_to_end_ns']['p95']/1e9,'ttft_p95_s':ar['latency']['client_ttft_ns']['p95']/1e9,'prompt_tokens':ar['prompt_tokens_observed'],'generated_tokens':ar['generated_tokens_reported'],'quality_pass':ar['quality_pass'],'eligible':ar['eligible'],'status':a['status']})
  local_pairs=[]
  for pi,arms in sorted(by_pair.items()):
   assert set(arms)=={'baseline','candidate'}
   for rid in source:
    b,c=arms['baseline'][rid],arms['candidate'][rid];outcome='both_correct' if b['correct'] and c['correct'] else 'full_only_correct' if b['correct'] else 'candidate_only_correct' if c['correct'] else 'both_wrong'
    row={'study':study_id,'phase':phase,'mechanism':mechanism,'pair_index':pi,'request_id':rid,'family':parsed[rid]['family'],'full_correct':b['correct'],'candidate_correct':c['correct'],'outcome':outcome,'oracle_correct':b['correct'] or c['correct'],'features':parsed[rid]['features']};local_pairs.append(row);paired.append({k:v for k,v in row.items() if k!='features'})
  all_pair_rows[study_id]=local_pairs
  for pi in sorted(by_pair):
   groups=collections.defaultdict(list)
   for r in local_pairs:
    if r['pair_index']==pi:
     for group in strata(r):groups[group].append(r)
   for (dimension,value),rows in sorted(groups.items()):
    counts=outcomes(rows);n=len(rows);oracle=sum(r['oracle_correct'] for r in rows)
    oracles.append({'study':study_id,'phase':phase,'mechanism':mechanism,'repeat_scope':f'pair_{pi}','dimension':dimension,'stratum':value,'offered':n,**counts,'full_correct':counts['both_correct']+counts['full_only_correct'],'candidate_correct':counts['both_correct']+counts['candidate_only_correct'],'oracle_correct':oracle,'oracle_accuracy':oracle/n,'oracle_at_least_95pct':oracle*100>=n*95,'interpretation':'Conditional observed-output ceiling; no inter-repeat mixing or population guarantee.'})
  conservative=[]
  for rid in source:
   arm_rows={arm:[by_pair[pi][arm][rid] for pi in sorted(by_pair)] for arm in ['baseline','candidate']}
   full=all(r['correct'] for r in arm_rows['baseline']);candidate=all(r['correct'] for r in arm_rows['candidate'])
   stability.append({'study':study_id,'request_id':rid,'family':parsed[rid]['family'],'full_correct_sequence':''.join('1' if r['correct'] else '0' for r in arm_rows['baseline']),'candidate_correct_sequence':''.join('1' if r['correct'] else '0' for r in arm_rows['candidate']),'full_unique_outputs':len({r['output'] for r in arm_rows['baseline']}),'candidate_unique_outputs':len({r['output'] for r in arm_rows['candidate']}),'per_pair_union_sequence':''.join('1' if by_pair[pi]['baseline'][rid]['correct'] or by_pair[pi]['candidate'][rid]['correct'] else '0' for pi in sorted(by_pair)),'conservative_oracle_correct':full or candidate})
   r={'request_id':rid,'family':parsed[rid]['family'],'features':parsed[rid]['features'],'oracle_correct':full or candidate,'outcome':'both_correct' if full and candidate else 'full_only_correct' if full else 'candidate_only_correct' if candidate else 'both_wrong'};conservative.append(r)
  groups=collections.defaultdict(list)
  for r in conservative:
   for group in strata(r):groups[group].append(r)
  for (dimension,value),rows in sorted(groups.items()):
   counts=outcomes(rows);n=len(rows);oracle=sum(r['oracle_correct'] for r in rows)
   oracles.append({'study':study_id,'phase':phase,'mechanism':mechanism,'repeat_scope':'one_arm_correct_in_all_repeats','dimension':dimension,'stratum':value,'offered':n,**counts,'full_correct':counts['both_correct']+counts['full_only_correct'],'candidate_correct':counts['both_correct']+counts['candidate_only_correct'],'oracle_correct':oracle,'oracle_accuracy':oracle/n,'oracle_at_least_95pct':oracle*100>=n*95,'interpretation':'Choose one observed arm per request that is correct in every repeat; no opportunistic mixing.'})
  queue=read(queue_path);costs.append({'study':study_id,'native_offered':len(source)*len(ra),'unique_tables':len(set(tables[study_id].values())),'queue_execution_s':(queue['finished_ns']-queue['execution_started_ns'])/1e9,'attempt_full_wall_s':report['accounting']['full_wall_ns']/1e9,'enclosing_study_span_s':report['accounting']['elapsed_span_ns']/1e9,'original_allocation_full_wall_ns':report['accounting']['full_cost_accounting'].get('registered_full_wall_ns'),'scope':'Queue, attempt and allocation scopes overlap; never add them. Only disjoint queue executions are summed across studies.'})
  inventory.append({'study':str(study),'config_sha256':sha(study/'config.json'),'workload_sha256':sha(study/'workload.json'),'report_sha256':sha(report_path),'queue_sha256':sha(queue_path),'native_attempts':len(ra),'offered_each':len(source),'families':dict(collections.Counter(r['family'] for r in parsed.values()))})
  checks.append({'study':study_id,'status':'PASS','checks':['All offered native outputs scored against independent record interpreter','Independent correct counts equal packaged report','All relevant candidate prompts preserve symbolic answers','All four paired outcome classes retained','Per-pair and conservative oracle denominators kept separate']})
 relationships=manifest.get('relationships',{});fit=relationships.get('fit');cal=relationships.get('calibration');control=relationships.get('matched_budget_control');confirm=relationships.get('confirmation',[])
 assert all(name in tables for name in confirm),'Missing declared confirmation study'
 if fit in tables and cal in tables:
  assert set(tables[fit].values()).isdisjoint(tables[cal].values()),'Fit/calibration table overlap'
  checks.append({'study':'fit versus calibration','status':'PASS','checks':['Independent exact-body group disjointness']})
 if confirm:
  reference=workload_rows[confirm[0]]
  for name in confirm:
   assert workload_rows[name]==reference,'Confirmation policy populations differ'
   for earlier in [fit,cal]:
    if earlier in tables:assert set(tables[name].values()).isdisjoint(tables[earlier].values()),'Confirmation overlaps development tables'
  checks.append({'study':'all available confirmation policies','status':'PASS','checks':['Byte-identical offered request records/answers across policies','Independent table-body disjointness from development']})
 if fit in tables and control in tables:
  assert workload_rows[fit]==workload_rows[control],'Shortening control changed source tables'
  candidates={(r['study'],r['pair_index'],r['request_id']):r for r in requests if r['arm']=='candidate'}
  for (study,pi,rid),row in candidates.items():
   if study==control:assert row['retained_records']==candidates[(fit,pi,rid)]['retained_records'],'Control record budget mismatch'
  checks.append({'study':'matched-budget development control','status':'PASS','checks':['Exact same source tables and expected answers','Equal retained record counts per request and pair','Actual prompt token counts remain separately observed']})
 route_counts=[]
 for study in tables:
  for pi in sorted({r['pair_index'] for r in requests if r['study']==study}):
   count=collections.Counter(r['decision'] for r in requests if r['study']==study and r['pair_index']==pi and r['arm']=='candidate')
   for decision,n in sorted(count.items()):route_counts.append({'study':study,'pair_index':pi,'decision':decision,'offered':n})
 for name,rows in [('requests',requests),('attempts',attempts),('paired',paired),('oracle-strata',oracles),('cost-scopes',costs),('route-counts',route_counts),('repetition-stability',stability)]:csv_write(args.output/(name+'.csv'),rows)
 result={'status':'PASS','created_monotonic_ns':time.monotonic_ns(),'analysis_script_sha256':sha(pathlib.Path(__file__)),'manifest_sha256':sha(args.manifest),'evidence_root':str(base),'inventory':inventory,'checks':checks,'costs':costs,'native_offered':sum(r['native_offered'] for r in costs),'native_execution_s':sum(r['queue_execution_s'] for r in costs),'scope':'Descriptive bounded native evidence. No eligible positive efficiency claim is inferred. All study reports remain authoritative for gates.','oracle_summary':[r for r in oracles if r['dimension'] in ('all','family')]}
 (args.output/'analysis.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'studies':len(inventory),'native_offered':result['native_offered'],'output':str(args.output)}))
if __name__=='__main__':main()
