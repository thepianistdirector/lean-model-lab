#!/usr/bin/env python3
"""Validate a retained native-trained controller against exported label studies.

No new tree is fitted, threshold tuned, model executed, or artifact replaced.
Original source hashes can differ from redacted export hashes; the manifest
binds both the copied native training artifacts and the actual exported data.
"""
import argparse,hashlib,json,pathlib,time
from fractions import Fraction
from reanalyze import parse,canonical

def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def classify(row):return 'both_correct' if row['full_correct'] and row['slice_correct'] else 'full_only_correct' if row['full_correct'] else 'slice_only_correct' if row['slice_correct'] else 'both_wrong'
def count(rows):return {key:sum(classify(r)==key for r in rows) for key in ['both_correct','full_only_correct','slice_only_correct','both_wrong']}
def leaf(tree,features):
 node=tree
 while node['kind']=='split':node=node['left'] if features[node['feature']]<=node['threshold'] else node['right']
 return node

def main():
 p=argparse.ArgumentParser();p.add_argument('--manifest',type=pathlib.Path,required=True);p.add_argument('--evidence-root',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
 if a.output.exists():raise SystemExit('Output must be new')
 m=read(a.manifest);base=(a.evidence_root or a.manifest.parent).resolve();training=m['training'];directory=base/training['directory'];entries={r['id']:r for r in m['studies']}
 for filename,digest in training['expected'].items():assert sha(directory/filename)==digest,'Training file hash mismatch: '+filename
 controller=read(directory/'controller.json');protocol=read(directory/'training-protocol.json');receipt=read(directory/'training-receipt.json');assert receipt['status']=='COMPLETED';copy=dict(controller);stored=copy.pop('controller_sha256');assert canonical(copy)==stored,'Controller identity mismatch'
 populations={};native_checks=[]
 for split,relationship in [('fit','fit'),('calibration','calibration')]:
  entry=entries[m['relationships'][relationship]];study=base/entry['study'];w=read(study/'workload.json');attempts=[read(p) for p in sorted((study/'attempts').glob('*.json'))];labels=read(directory/(split+'-labels.json'));label_map={r['source_id']:r for r in labels['rows']};assert len(label_map)==len(w['requests']);assert min(r['started_ns'] for r in attempts)>=protocol['frozen_ns']
  for src in w['requests']:
   semantic=parse(src['prompt']);source_id=canonical(src['prompt']);assert semantic['expected']==src['expected'];expected={'source_id':source_id,'group_id':semantic['group_id'],'features':semantic['features']}
   for arm,prefix in [('baseline','full'),('candidate','slice')]:
    obs=[next(r for r in attempt['requests'] if r['request_id']==src['request_id']) for attempt in attempts if attempt['arm']==arm];assert len(obs)==2 and all(r['status']=='SUCCEEDED' for r in obs)
    expected[prefix+'_correct']=all(r['output_text'].strip()==src['expected'] for r in obs);expected[prefix+'_request_ns']=sum(r['completed_ns']-r['dispatch_ns'] for r in obs)
   assert label_map[source_id]==expected,'Copied native label differs from exported actual outputs/features/costs'
  populations[split]=labels['rows'];native_checks.append({'split':split,'rows':len(labels['rows']),'all_native_rows_reconciled':True})
 assert {r['group_id'] for r in populations['fit']}.isdisjoint({r['group_id'] for r in populations['calibration']}),'Fit/calibration groups overlap'
 tree=controller['parameters']['tree']
 def check_node(node,rows):
  assert node['samples']==len(rows) and node['outcomes']==count(rows) and node['harm_count']==count(rows)['full_only_correct']
  assert node['depth']<=2
  if node['kind']=='split':
   check_node(node['left'],[r for r in rows if r['features'][node['feature']]<=node['threshold']]);check_node(node['right'],[r for r in rows if r['features'][node['feature']]>node['threshold']])
 check_node(tree,populations['fit']);cal=populations['calibration'];grid=[]
 for index,value in enumerate(controller['calibration']['grid']):
  threshold=Fraction(str(value));accepted=[]
  for row in cal:
   node=leaf(tree,row['features'])
   if node['harm_count']*threshold.denominator<=node['samples']*threshold.numerator:accepted.append(row)
  c=count(accepted);full_ns=sum(r['full_request_ns'] for r in accepted);slice_ns=sum(r['slice_request_ns'] for r in accepted);routed=sum(r['full_correct'] for r in cal)-c['full_only_correct']+c['slice_only_correct'];expected={'threshold_index':index,'threshold':value,'accepted':len(accepted),'accepted_outcomes':c,'routed_correct':routed,'accepted_full_request_ns':full_ns,'accepted_slice_request_ns':slice_ns,'request_saving_ns':full_ns-slice_ns,'eligible':len(accepted)>=8 and c['full_only_correct']==0 and routed*100>=95*len(cal) and full_ns>slice_ns};assert controller['calibration']['trace'][index]==expected;grid.append(expected)
 eligible=[r for r in grid if r['eligible']];selected=min(eligible,key=lambda r:(-r['request_saving_ns'],r['threshold_index']))['threshold_index'] if eligible else None;assert selected==controller['parameters']['threshold_index'];assert controller['parameters']['mode']==('ALWAYS_FULL' if selected is None else 'LEARNED_GATE');assert controller['formal_guarantee'] is False
 result={'status':'PASS','created_monotonic_ns':time.monotonic_ns(),'manifest_sha256':sha(a.manifest),'validator_sha256':sha(pathlib.Path(__file__)),'native_checks':native_checks,'training_mode':controller['parameters']['mode'],'selected_threshold_index':selected,'fitted_node_counts_reconciled':True,'all_fixed_calibration_grid_rows_reconciled':True,'scope':'Independent retained-artifact validation using actual redacted export outputs. No replacement tree or threshold was fitted; no native or population-risk claim.'};a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
