#!/usr/bin/env python3
"""Catalogue completed evidence without modifying any study or native artifact."""
import hashlib,json,pathlib,time
own=pathlib.Path(__file__).resolve().parent;root=own.parents[2];docs=root/'docs/research/candidate-study';target=own/'candidate-delivery-manifest04.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def item(p):return {'path':str(p.relative_to(root)),'sha256':sha(p),'bytes':p.stat().st_size}
stems=['feasibility-14b03','clarification-0.5b04','negative-fit04','negative-calibration04','negative-budget-control04','negative-confirm-slice04','negative-confirm-simple04','negative-confirm-learned04'];studies=[];missing=[]
for stem in stems:
 label,version=stem[:-2],stem[-2:];study=own/(label+'-study'+version);queue=pathlib.Path(str(study)+'.queue')/'receipt.json'
 if not queue.exists():missing.append(str(study.relative_to(root)));continue
 receipt=read(queue);attempt_files=sorted((study/'attempts').glob('*.json'));attempts=[read(p) for p in attempt_files];workload=read(study/'workload.json');entry={'name':stem,'study':str(study.relative_to(root)),'queue_receipt':item(queue),'queue_status':receipt['status'],'actual_attempt_count':len(attempts),'offered_native':len(attempts)*len(workload['requests']),'unique_questions':len(workload['requests']),'execution_s':(receipt['finished_ns']-receipt['execution_started_ns'])/1e9 if receipt['execution_started_ns'] is not None else 0,'exports':{},'attempts':[item(p) for p in attempt_files]}
 for kind,suffix in [('report','.json'),('workbench','.json'),('workbench','.html'),('raw-audit','.json')]:
  p=own/(label+'-'+kind+version+suffix)
  if p.exists():entry['exports'][kind+suffix]=item(p)
  else:missing.append(str(p.relative_to(root)))
 export=own/(label+'-export'+version);entry['export_directory']=str(export.relative_to(root))
 if not (export/'EXPORT-READY.json').exists():missing.append(str(export.relative_to(root)))
 studies.append(entry)
producers=[]
for version in ['03','04']:
 p=root/'.cache'/('packaged-v1-platform-20260908-'+version)/'lean-model-lab.pyz';producers.append(item(p))
files=[]
for base in [own,docs]:
 for p in sorted(base.rglob('*')):
  if p.is_file() and p!=target and not any(part in ('mpl-cache','__pycache__') for part in p.relative_to(base).parts):files.append(item(p))
training=own/'negative-controller04';controller=training/'controller.json';training_info={'directory':str(training.relative_to(root)),'exists':controller.exists()}
if controller.exists():training_info.update(controller=item(controller),mode=read(controller)['parameters']['mode'],receipt=item(training/'training-receipt.json'))
else:missing.append(str(controller.relative_to(root)))
result={'schema_version':1,'created_monotonic_ns':time.monotonic_ns(),'status':'COMPLETE_INVENTORY' if not missing else 'INCOMPLETE_INVENTORY','missing':missing,'producers':producers,'studies':studies,'training':training_info,'native_offered':sum(s['offered_native'] for s in studies),'native_execution_s':sum(s['execution_s'] for s in studies),'maximum_native_offered':2000,'maximum_native_execution_s':10800,'original_deadline_ns':310468865220540,'visual_reviews_path':str((own/'visual-review04.json').relative_to(root)),'files':files,'scope':'Integrity inventory only; not scientific eligibility or publication acceptance. Existing failed feasibility branches remain closed. Queue/attempt/allocation cost scopes overlap and are not summed together.'}
target.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'path':str(target.relative_to(root)),'status':result['status'],'native_offered':result['native_offered'],'native_execution_s':result['native_execution_s'],'files':len(files)}))
