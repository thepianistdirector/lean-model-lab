#!/usr/bin/env python3
"""Verify retained table grouping, development separation and matched model populations."""
import argparse
import hashlib
import json
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('manifest',type=Path)
parser.add_argument('--evidence-root',type=Path)
parser.add_argument('--output',required=True,type=Path)
args=parser.parse_args();manifest=json.loads(args.manifest.read_text())
root=Path(args.evidence_root or manifest.get('workspace_root') or manifest.get('evidence_root','.')).resolve()
records=[];workloads={};groups={};by_split={}
for case in manifest['cases']:
 study=root/case['study'] if 'study' in case else root/case['directory']/'study'
 path=study/'workload.json';workload=json.loads(path.read_text());workloads[case['id']]=workload
 table_queries={}
 for row in workload['requests']:
  table,query=row['prompt'].split('\nEND\n',1)
  table_id=hashlib.sha256(table.encode()).hexdigest();table_queries.setdefault(table_id,[]).append(query)
 groups[case['id']]=set(table_queries);by_split.setdefault(workload['generator']['split'],set()).update(table_queries)
 counts=[len(v) for v in table_queries.values()];distinct=[len(set(v)) for v in table_queries.values()]
 records.append({'case_id':case['id'],'split':workload['generator']['split'],'seed':workload['generator']['seed'],
  'context_records':workload['generator']['context_records'],'offered_tasks':len(workload['requests']),
  'distinct_tables':len(table_queries),'queries_per_table':counts,'distinct_queries_per_table':distinct,
  'eight_distinct_queries_per_table':all(n==8 for n in counts+distinct),
  'workload_file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'table_sha256':list(table_queries)})
comparisons=[]
for left,right in [('d1-small-reuse24','d2-large-reuse24'),('h1-small-reuse24','h3-large-reuse24')]:
 if left in workloads and right in workloads:
  comparisons.append({'cases':[left,right],'all_generated_request_records_identical':workloads[left]['requests']==workloads[right]['requests']})
overlap=sorted(by_split.get('development',set()) & by_split.get('confirmation',set()))
passing=all(r['eight_distinct_queries_per_table'] for r in records) and not overlap and all(c['all_generated_request_records_identical'] for c in comparisons)
result={'status':'PASS' if passing else 'POPULATION_CHECK_FAILED','cases':records,'matched_model_comparisons':comparisons,
 'development_confirmation_table_overlap':overlap,'distinct_table_prefixes_across_cases':len(set().union(*groups.values())),
 'scope':'Exact retained original table/query identity; deterministic repetitions and matched-model reuse do not become independent observations. This does not establish adversarial split isolation or a statistical population guarantee.'}
args.output.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],result['distinct_table_prefixes_across_cases'],'distinct retained tables')
if not passing:raise SystemExit(1)
