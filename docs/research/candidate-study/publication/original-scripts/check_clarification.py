#!/usr/bin/env python3
"""Check the completed diagnosis retained every record and changed only fixed instructions."""
import hashlib,json,pathlib
p=pathlib.Path(__file__).parent;s=p/'clarification-0.5b-study04'
def load(p):return json.loads(p.read_text())
old=load(p/'feasibility-14b-study03/workload.json');new=load(s/'workload.json')
assert old['requests']==new['requests'],'Questions, records or answers changed'
expected={r['request_id']:r for r in new['requests']};instructions=load(p/'fixed-explicit-grammar-v2.json')['instructions'];checks=[]
for path in sorted((s/'attempts').glob('*.json')):
 a=load(path)
 if a['arm']!='candidate':continue
 tpath=s/'raw'/a['attempt_id']/'prompt-interventions.json';trace=load(tpath)
 for r in trace['requests']:
  before=expected[r['request_id']]['prompt'].splitlines();after=r['result']['prompt'].splitlines();desired=before[:]
  for i,key in [(0,'language'),(2,'rules'),(3,'output')]:desired[i]=instructions[key]
  assert after==desired,'A non-frozen line was changed'
  cert=r['result']['certificate'];assert cert['retained_record_count']==cert['input_record_count']==8
  assert cert['rewritten_line_indices']==[0,2,3]
  checks.append({'attempt_id':a['attempt_id'],'request_id':r['request_id'],'all_original_records_query_order_preserved':True,'exact_fixed_header_only':True,'trace_sha256':hashlib.sha256(tpath.read_bytes()).hexdigest()})
assert len(checks)==16
result={'status':'PASS','scope':'Independent retained-data check, no model execution. Every candidate request has exactly the original records/query and the three frozen instruction lines. Both-model study questions and expected answers are byte-identical.','candidate_requests_checked':len(checks),'checks':checks}
(p/'clarification-0.5b-analysis04/instruction-invariance.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'])
