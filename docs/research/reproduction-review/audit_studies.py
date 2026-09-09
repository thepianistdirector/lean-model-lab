import json,hashlib,collections,time
from pathlib import Path
import argparse
parser=argparse.ArgumentParser(description='Independently audit retained package request streams and exact record semantics; no model execution.')
parser.add_argument('--package',action='append',required=True,help='Unique NAME=extracted-package-path')
parser.add_argument('--output',type=Path,required=True)
args=parser.parse_args();packages=dict(item.split('=',1) for item in args.package)
assert len(packages)==len(args.package),'Package names must be unique'
assert not args.output.exists(),'Output must be new'
checks=[];errors=[]
def load(p):return json.loads(p.read_text())
def solve(prompt):
 lines=prompt.splitlines();a=lines.index('BEGIN');b=lines.index('END');mapping={}
 for row in lines[a+1:b]:
  kind,key,value=row.split();assert kind in ['VALUE','REF'];mapping[key]=(kind,value)
 key=next(row.split()[1] for row in lines[b+1:] if row.startswith('ASK '));visited=set()
 while key in mapping and key not in visited:
  visited.add(key);kind,value=mapping[key]
  if kind=='VALUE':return value
  key=value
 return None
for package,package_path in packages.items():
 base=Path(package_path);meta=load(base/'RESEARCH-PACKAGE.json')
 for name in meta['studies']:
  study=base/'evidence'/name/'study';w=load(study/'workload.json');sources={r['request_id']:r for r in w['requests']};ats=[load(x) for x in (study/'attempts').glob('*.json')];rows=[];pairclasses={};raw_count=0
  for a in sorted(ats,key=lambda x:(x['concurrency'],x['pair_index'],x['arm'])):
   offered=len(sources);counts=collections.Counter();prompt_tokens=generated_tokens=cache_tokens=new_tokens=0;trace=study/'raw'/a['attempt_id']/'prompt-interventions.json';trace={r['request_id']:r['result'] for r in load(trace)['requests']} if trace.exists() else {};symbolic_total=symbolic_preserved=0
   for r in a['requests']:
    rid=r['request_id'];s=sources[rid];ok=r['status']=='SUCCEEDED' and r['output_text'].strip()==s['expected'];counts['correct']+=ok;counts[r['status']]+=1;prompt_tokens+=r.get('prompt_tokens') or 0;generated_tokens+=r.get('generated_tokens') or 0
    if s['prompt'].startswith('RECORD-LANGUAGE'):
     assert solve(s['prompt'])==s['expected'];trans=trace.get(rid,{}).get('prompt',s['prompt']);symbolic_total+=1;symbolic_preserved+=solve(trans)==s['expected']
    stream=study/'raw'/a['attempt_id']/(rid+'.jsonl')
    if not stream.exists():continue
    raw_count+=1;events=[]
    for line in stream.read_text().splitlines():
     row=json.loads(line)
     if row.get('data_utf8') and row['data_utf8']!='[DONE]':events.append(json.loads(row['data_utf8']))
    generated=[e for e in events if not e.get('stop') and 'prompt_progress' not in e];content=''.join(e.get('content','') for e in generated);tokens=[t for e in generated for t in e.get('tokens',[])];finals=[e for e in events if e.get('stop')]
    if content!=r['output_text']:errors.append([package,name,a['attempt_id'],rid,'content mismatch'])
    if tokens!=r['output_token_ids']:errors.append([package,name,a['attempt_id'],rid,'tokens mismatch'])
    if r['status']=='SUCCEEDED':
     assert len(finals)==1;f=finals[0];assert f['tokens_predicted']==r['generated_tokens'];assert f['tokens_evaluated']==r['prompt_tokens'];cache_tokens+=f['timings'].get('cache_n',0);new_tokens+=f['timings']['prompt_n']
   rows.append({'attempt_id':a['attempt_id'],'arm':a['arm'],'concurrency':a['concurrency'],'pair':a['pair_index'],'status':a['status'],'offered':offered,'observed':len(a['requests']),'missing':offered-len(a['requests']),'counts':dict(counts),'prompt_tokens':prompt_tokens,'generated_tokens':generated_tokens,'cache_tokens':cache_tokens,'new_tokens':new_tokens,'symbolic_checked':symbolic_total,'symbolic_preserved':symbolic_preserved,'full_attempt_seconds':(a['finished_ns']-a['started_ns'])/1e9})
  for concurrency,pair in sorted(set((a['concurrency'],a['pair_index']) for a in ats)):
   arms={a['arm']:{r['request_id']:r for r in a['requests']} for a in ats if a['concurrency']==concurrency and a['pair_index']==pair};cc=collections.Counter();mismatches=[]
   for rid,s in sources.items():
    ba=arms.get('baseline',{}).get(rid);ca=arms.get('candidate',{}).get(rid);bc=ba and ba['status']=='SUCCEEDED' and ba['output_text'].strip()==s['expected'];qc=ca and ca['status']=='SUCCEEDED' and ca['output_text'].strip()==s['expected'];cc['both_correct' if bc and qc else 'baseline_only' if bc else 'candidate_only' if qc else 'both_wrong_or_missing']+=1
    if ba and ca and ba['output_token_ids']!=ca['output_token_ids']:mismatches.append(rid)
   pairclasses[f'c{concurrency}-p{pair}']={'complete_arms':set(arms)=={'baseline','candidate'},'classes':dict(cc),'token_mismatch_requests':mismatches}
  checks.append({'package':package,'study':name,'raw_streams_reconstructed':raw_count,'attempts':rows,'pairs':pairclasses})
result={'status':'PASS' if not errors else 'DISCREPANCIES','method':'Reviewer-authored independent final-write REF interpreter and native SSE reconstruction; no package analysis imports. All offered requests retained including missing arms/requests. Legacy incomplete outcomes are not completed comparisons.','studies':checks,'errors':errors,'created_ns':time.monotonic_ns()};args.output.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],'studies',len(checks),'streams',sum(s['raw_streams_reconstructed'] for s in checks),'errors',errors[:10])
