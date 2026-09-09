#!/usr/bin/env python3
"""Independent read-only resolution of a retained native counterexample."""
import hashlib,json,pathlib
p=pathlib.Path(__file__).parent
study=p/'feasibility-14b-study03'
def load(p): return json.loads(p.read_text())
def solve(prompt):
 lines=prompt.splitlines();begin=lines.index('BEGIN');end=lines.index('END');table={}
 for line in lines[begin+1:end]:
  op,key,value=line.split();assert op in ('VALUE','REF');table[key]=(op,value)
 query=lines[end+1].split();assert query[0]=='ASK';key=query[1];seen=set();chain=[]
 while True:
  assert key not in seen;seen.add(key);op,value=table[key];chain.append([op,key,value])
  if op=='VALUE':return value,chain
  key=value
rid='r007';w=load(study/'workload.json');original=next(r for r in w['requests'] if r['request_id']==rid)
records=[]
for ap in sorted((study/'attempts').glob('*.json')):
 a=load(ap);r=next(r for r in a['requests'] if r['request_id']==rid)
 if a['arm']=='candidate':
  tracepath=study/'raw'/a['attempt_id']/'prompt-interventions.json';trace=next(r for r in load(tracepath)['requests'] if r['request_id']==rid)['result'];prompt=trace['prompt'];certificate=trace['certificate']
  assert certificate['dependency_closure_preserved'] is True
 else:prompt=original['prompt'];certificate=None
 value,chain=solve(prompt);assert value==original['expected']
 records.append({'attempt_id':a['attempt_id'],'attempt_sha256':hashlib.sha256(ap.read_bytes()).hexdigest(),'pair_index':a['pair_index'],'arm':a['arm'],'prompt':prompt,'independently_resolved':value,'resolution_chain':chain,'native_output':r['output_text'],'native_token_ids':r['output_token_ids'],'native_finish_reason':r['finish_reason'],'correct':r['output_text'].strip()==value,'certificate':certificate})
result={'scope':'One exact retained native counterexample, read-only semantic re-resolution without product imports. The semantic certificate itself never claimed model equivalence.','request_id':rid,'expected':original['expected'],'records':records,'status':'PASS_SEMANTIC_PRESERVATION_WITH_REPEATED_NATIVE_HARM'}
(p/'feasibility-14b-analysis03/counterexample-r007.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
