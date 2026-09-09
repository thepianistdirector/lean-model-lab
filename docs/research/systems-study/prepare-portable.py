#!/usr/bin/env python3
"""Copy exact study specifications and verify exports for portable reanalysis."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys
import time

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--workspace-root',type=Path,default=Path.cwd())
parser.add_argument('--cases',nargs='+',required=True)
args=parser.parse_args();root=args.workspace_root.resolve();docs=root/'docs/research/systems-study'
base=root/'.cache/v1-investigations-20260908/systems';dest=docs/'provenance';dest.mkdir(exist_ok=True)
portable_prefix=Path('lean-model-lab-source/docs/research/systems-study/provenance')
allowed={'d1-small-reuse24','d2-large-reuse24','h1-small-reuse24','h2-small-reuse64','h3-large-reuse24'}
assert set(args.cases)<=allowed
for name in ['stage-plan.json','heldout-matrix-freeze.json','stage-status-after-d1.json','stage-status-after-d2.json','final-campaign-status.json']:
 if (base/name).exists():shutil.copyfile(base/name,dest/name)
script_dest=dest/'original-run-scripts';script_dest.mkdir(exist_ok=True)
for name in ['prepare-d2.py','prepare-heldout.py','finalize-d2.py','finalize-case.py','admit-next.py']:
 if (base/name).exists():shutil.copyfile(base/name,script_dest/name)
public_cases=[];test_cases=[];catalog=[]
for cid in args.cases:
 source=base/cid;target=dest/cid;target.mkdir(exist_ok=True)
 assert (source/'export/EXPORT-READY.json').exists(), 'Only completed verified exports can enter this manifest'
 previous_ready=target/'EXPORT-READY.json'
 already_verified=previous_ready.exists() and (target/'inspect-export.json').exists() and (target/'raw-audit-export.json').exists()
 if already_verified:
  assert previous_ready.read_bytes()==(source/'export/EXPORT-READY.json').read_bytes(), 'Export changed after retained verification'
 for name in ['proposal.json','protocol.json','protocol-template.json','recipe.json','preexecution-freeze.json','budget-admission.json','matched-population-check.json','native-queue-command.json']:
  if (source/name).exists():shutil.copyfile(source/name,target/name)
 for pattern in ['*.command.json','*.stdout','*.stderr']:
  for path in source.glob(pattern):
   filename=path.name+'.txt' if path.suffix in {'.stdout','.stderr'} else path.name
   shutil.copyfile(path,target/filename)
 if (source/'proposal-bundle').exists():shutil.copytree(source/'proposal-bundle',target/'proposal-bundle',dirs_exist_ok=True)
 for name in ['registration.json','receipt.json','product.log']:
  shutil.copyfile(source/'study.queue'/name,target/('queue-'+name+('.txt' if name.endswith('.log') else '')))
 shutil.copyfile(source/'export/report.json',target/'report.json')
 shutil.copyfile(source/'export/EXPORT-READY.json',target/'EXPORT-READY.json')
 archive_dir='packaged-v1-platform-20260908-03' if cid.startswith('d1-') else 'packaged-v1-platform-20260908-04'
 archive=root/'.cache'/archive_dir/'lean-model-lab.pyz';archive_sha=hashlib.sha256(archive.read_bytes()).hexdigest()
 small='small' in cid
 backend=root/('.cache/prepared-20260908-01/build/bin/llama-server' if small else '.cache/prepared-14b-20260908-01/build/bin/llama-server')
 model=root/('.cache/prepared-20260908-01/qwen2.5-0.5b-instruct-fp16.gguf' if small else '.cache/prepared-14b-20260908-01/qwen2.5-14b-instruct-fp16-00001-of-00008.gguf')
 setup=root/('.cache/adopted-0.5b-current-02/setup.json' if small else '.cache/prepared-14b-20260908-01/setup.json')
 command=['python3','tools/run_queued_recipe.py','--archive',str(archive.relative_to(root)),'--recipe',str((source/'recipe.json').relative_to(root)),'--server',str(backend.relative_to(root)),'--model',str(model.relative_to(root)),'--setup',str(setup.relative_to(root)),'--output',str((source/'study').relative_to(root))]
 (target/'queue-command.json').write_text(json.dumps({'command':command,'environment':{'PYTHONDONTWRITEBYTECODE':'1','TMPDIR':'.cache/tmp'},'archive_sha256':archive_sha,'recipe_file_sha256':hashlib.sha256((source/'recipe.json').read_bytes()).hexdigest(),'scope':'Documentary transcription of the original queue invocation, assembled during publication preparation. Original queue registration and receipt separately retain execution timestamps and producer hashes; this file is not a new contemporaneous process attestation.'},indent=2)+'\n')
 for name,command in [('inspect-export',[sys.executable,'-I',str(archive),'inspect',str(source/'export/study')]),('raw-audit-export',[sys.executable,str(root/'tools/audit_raw_study.py'),str(source/'export/study'),'--output',str(target/'raw-audit-export.json')])]:
  if already_verified:
   continue
  start=time.monotonic_ns();run=subprocess.run(command,capture_output=True,text=True,cwd=root)
  (target/(name+'.stdout.txt')).write_text(run.stdout);(target/(name+'.stderr.txt')).write_text(run.stderr)
  (target/(name+'.command.json')).write_text(json.dumps({'command':command,'started_ns':start,'finished_ns':time.monotonic_ns(),'returncode':run.returncode,'archive_sha256':archive_sha},indent=2)+'\n')
  if run.returncode:print(run.stdout,run.stderr);raise SystemExit(run.returncode)
  if name=='inspect-export':(target/'inspect-export.json').write_text(run.stdout)
 p=portable_prefix/cid
 record={'id':cid,'study':f'evidence/systems-{cid}/study','report':str(p/'report.json'),'inspect':str(p/'inspect-export.json'),'raw_audit':str(p/'raw-audit-export.json'),'queue_receipt':str(p/'queue-receipt.json')}
 public_cases.append(record)
 test_cases.append({**record,'study':str(source/'export/study'),'report':str(target/'report.json'),'inspect':str(target/'inspect-export.json'),'raw_audit':str(target/'raw-audit-export.json'),'queue_receipt':str(target/'queue-receipt.json')})
 print(cid,'export inspection/raw audit PASS',flush=True)
private_store=base/'publication-unredacted';private_store.mkdir(exist_ok=True)
ledger_path=docs/'provenance-redactions.json'
previous=json.loads(ledger_path.read_text())['files'] if ledger_path.exists() else []
redactions={row['path']:row for row in previous}
private_pattern=re.compile(r'/(?:home|Users|tmp)/[^\s\"\'<>]+')
for path in sorted([*dest.rglob('*'),docs/'portable-relocation-check.json']):
 if not path.is_file():continue
 relative=str(path.relative_to(docs));original=path.read_bytes();text=original.decode('utf-8');changes=[]
 for old,new,kind in [(str(root),'${WORKSPACE_ROOT}','workspace-prefix'),(sys.executable,'python3','interpreter-executable')]:
  count=text.count(old)
  if count:
   text=text.replace(old,new);changes.append({'kind':kind,'replacement':new,'count':count})
 for old in sorted(set(private_pattern.findall(text))):
  if re.fullmatch(r'python(?:3(?:\.\d+)?)?',Path(old).name):
   count=text.count(old);text=text.replace(old,'python3')
   changes.append({'kind':'historical-interpreter-executable','replacement':'python3','count':count})
 assert not private_pattern.search(text), 'Unreviewed remaining private path in '+relative
 if changes:
  assert path.name not in {'protocol.json','recipe.json','proposal.json','heldout-matrix-freeze.json','stage-plan.json'}, 'Scientific specification must remain byte-exact'
  saved=private_store/path.relative_to(docs);saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(original)
  derivative=text.encode();path.write_bytes(derivative)
  redactions[relative]={'path':relative,'original_sha256':hashlib.sha256(original).hexdigest(),'derived_sha256':hashlib.sha256(derivative).hexdigest(),'redaction_count':sum(c['count'] for c in changes),'changes':changes}
 current=path.read_bytes();record={'path':relative,'original_filename':path.name[:-4] if path.name.endswith(('.stdout.txt','.stderr.txt','.log.txt')) else path.name,'bytes':len(current),'sha256':hashlib.sha256(current).hexdigest(),'operational_metadata_derivative':relative in redactions}
 if relative in redactions:record['original_sha256']=redactions[relative]['original_sha256']
 catalog.append(record)
(docs/'provenance-redactions.json').write_text(json.dumps({'scope':'Operational path metadata only. Exact originals remain privately retained. Recipe, protocol, proposal, freeze, cost and token fields are unchanged. Named workspace/interpreter replacements are documentation tokens, not new contemporaneous execution attestations.','files':list(redactions.values())},indent=2)+'\n')
(docs/'provenance-catalog.json').write_text(json.dumps({'scope':'Byte-exact scientific specifications and documented operational metadata derivatives, with original/derived hashes and original filenames.','files':catalog},indent=2)+'\n')
manifest={'schema_version':2,'evidence_root':'.','scope':'Use --evidence-root for the extracted self-contained investigation root; analysis output can be any new directory.','cases':public_cases}
(docs/'evidence-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(base/'export-analysis-manifest.json').write_text(json.dumps({**manifest,'cases':test_cases},indent=2)+'\n')
