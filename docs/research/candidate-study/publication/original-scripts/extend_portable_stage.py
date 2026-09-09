#!/usr/bin/env python3
"""Stage actual completed exports in the exact final release layout.

This adds no native runs, recipes, observations or inferred results.
"""
import argparse,pathlib,json,hashlib,shutil
p=argparse.ArgumentParser();p.add_argument('--stage',required=True);p.add_argument('--study',action='append',default=[]);p.add_argument('--final',action='store_true');a=p.parse_args()
own=pathlib.Path(__file__).resolve().parent;root=own.parents[2];pub=root/'docs/research/candidate-study/publication';stage=own/'portable-export-test04'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
m=read(pub/'evidence-manifest-development-stage3.json');known={e['id'] for e in m['studies']}
for sid in a.study:
 assert sid in ['negative-confirm-slice-study04','negative-confirm-simple-study04','negative-confirm-learned-study04'] and sid not in known
 export=own/sid.replace('-study','-export');assert (export/'EXPORT-READY.json').exists(),'Actual export not ready'
 q=pub/'artifacts'/sid/'queue-receipt.json';assert q.exists(),'Refresh publication queue provenance first';receipt=read(q);assert receipt['status']=='COMPLETED' and receipt['exit_code']==0,'Native study has not completed'
 dest=stage/'evidence'/sid
 if not dest.exists():shutil.copytree(export,dest)
 else:assert sha(dest/'EXPORT-READY.json')==sha(export/'EXPORT-READY.json'),'Previously staged export differs'
 m['studies'].append({'id':sid,'study':f'evidence/{sid}/study','report':f'evidence/{sid}/report.json','queue_receipt':'lean-model-lab-source/'+q.relative_to(root).as_posix(),'expected':{'config_sha256':sha(dest/'study/config.json'),'workload_sha256':sha(dest/'study/workload.json'),'report_sha256':sha(dest/'report.json'),'queue_sha256':sha(q)}});known.add(sid)
ordered=[('negative-confirm-slice-study04','Dependency slice'),('negative-confirm-simple-study04','Simple gate'),('negative-confirm-learned-study04','Fitted: all full')]
m['relationships']['confirmation']=[sid for sid,_ in ordered if sid in known]
if 'negative-confirm-slice-study04' in known:m['relationships']['slice_confirmation']='negative-confirm-slice-study04'
m['confirmation_policies']=[{'id':sid,'label':label} for sid,label in ordered if sid in known]
rule=pub/'artifacts/protocols/04-confirmation-illustration-selection04.json';m['illustration_selection']={'path':'lean-model-lab-source/'+rule.relative_to(root).as_posix(),'sha256':sha(rule)}
if a.final:assert len(m['studies'])==8 and len(m['relationships']['confirmation'])==3,'The final manifest requires all eight actual exports'
name='evidence-manifest-final.json' if a.final else 'evidence-manifest-'+a.stage+'.json';target=pub/name
assert not target.exists(),'Choose a new stage rather than replace an evidence manifest';target.write_text(json.dumps(m,indent=2)+'\n')
shutil.copytree(pub,stage/'lean-model-lab-source'/pub.relative_to(root),dirs_exist_ok=True)
print(json.dumps({'manifest':str(target.relative_to(root)),'manifest_sha256':sha(target),'studies':len(m['studies']),'stage':str(stage.relative_to(root))}))
