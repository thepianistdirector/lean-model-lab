#!/usr/bin/env python3
"""Copy original research provenance, with explicit operational path derivatives.

Native evidence, frozen recipes and fitted-controller scientific fields are never
rewritten. This only maintains the separately reviewable publication sources.
"""
import pathlib,json,hashlib,shutil
own=pathlib.Path(__file__).resolve().parent;root=own.parents[2];pub=root/'docs/research/candidate-study/publication';rows=[];frozen=[]
def sha(data):return hashlib.sha256(data).hexdigest()
def portable_copy(src,dest,operational):
 raw=src.read_bytes();count=raw.count(str(root).encode());data=raw.replace(str(root).encode(),b'$PROJECT_ROOT') if operational else raw
 if not operational and count:raise ValueError('Frozen artifact requires explicit review of private path: '+src.name)
 if any(prefix in data for prefix in [(b'/'+part+b'/') for part in (b'home',b'Users',b'tmp')]):raise ValueError('Unresolved private path in '+src.name)
 dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 entry={'original_relative_path':src.relative_to(root).as_posix(),'original_filename':src.name,'publication_path':dest.relative_to(root).as_posix(),'original_sha256':sha(raw),'derived_sha256':sha(data),'original_bytes':len(raw),'derived_bytes':len(data),'replacement_counts':{'PROJECT_ROOT':count if operational else 0},'operation':'Operational metadata derivative: literal workspace root replaced by named path token; stream suffix normalized to .txt. No scientific values changed.' if operational else 'Byte-exact original scientific artifact; filename extension mapping only when documented.'}
 (rows if operational else frozen).append(entry)
for src in sorted((own/'commands').iterdir()):
 if src.is_file():portable_copy(src,pub/'artifacts/commands'/(src.name+'.txt' if src.suffix in ('.stdout','.stderr','.log') else src.name),True)
selected=set()
for pattern in ['*-recipe*.json','*-proposal*.json','*-protocol*.json','[0-9][0-9]-*.json']:
 selected.update(own.glob(pattern))
for src in sorted(selected):portable_copy(src,pub/'artifacts/protocols'/src.name,False)
log=own/'03-confirmation-access-log04.jsonl'
if log.exists():portable_copy(log,pub/'artifacts/protocols'/(log.name+'.txt'),False)
for src in sorted((own/'negative-controller04').glob('*.json')):portable_copy(src,pub/'artifacts/training'/src.name,False)
for queue in sorted(own.glob('*-study*.queue')):
 for filename,target in [('registration.json','queue-registration.json'),('receipt.json','queue-receipt.json'),('product.log','queue-product.log.txt')]:
  src=queue/filename
  if src.exists():portable_copy(src,pub/'artifacts'/queue.name.removesuffix('.queue')/target,True)
for src in sorted(own.glob('*.py')):portable_copy(src,pub/'original-scripts'/src.name,True)
(pub/'operational-derivatives.json').write_text(json.dumps({'schema_version':1,'path_tokens':{'$PROJECT_ROOT':'Original producer workspace root, a documentary token rather than an executable native recipe setting.'},'files':rows},indent=2)+'\n')
(pub/'original-scientific-artifacts.json').write_text(json.dumps({'schema_version':1,'scope':'Exact original bytes and explicitly documented filename normalization; all seeds, rules, recipes, scientific fields and training artifacts unchanged.','files':frozen},indent=2)+'\n')
print(json.dumps({'operational_files':len(rows),'exact_scientific_files':len(frozen)}))
