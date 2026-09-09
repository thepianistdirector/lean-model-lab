"""Retain a prospective budget check; never runs models or changes frozen inputs."""
import hashlib,json,pathlib,sys,time
base=pathlib.Path('.cache/v1-investigations-20260908/systems');target=sys.argv[1]
assert target in {'h2-small-reuse64','h3-large-reuse24'}
manifest=json.loads((base/'heldout-matrix-freeze.json').read_text())
for case in manifest['cases']:
 for name in ('protocol','recipe'):
  assert hashlib.sha256((base/case['id']/(name+'.json')).read_bytes()).hexdigest()==case[name+'_file_sha256']
used=0.;completed=[]
for cid in ['d1-small-reuse24','d2-large-reuse24','h1-small-reuse24','h2-small-reuse64']:
 receipt=base/cid/'study.queue/receipt.json'
 if receipt.exists():
  r=json.loads(receipt.read_text());elapsed=(r['finished_ns']-r['execution_started_ns'])/1e9 if r['execution_started_ns'] else 0
  used+=elapsed;completed.append({'id':cid,'execution_seconds':elapsed,'queue_status':r['status']})
assert any(c['id']=='h1-small-reuse24' for c in completed)
h1=[json.loads(p.read_text()) for p in (base/'h1-small-reuse24/study/attempts').glob('*.json')]
assert len(h1)==4 and all(a['status']=='COMPLETED' for a in h1), 'H1 incomplete; do not auto-continue'
h1_service=sum(a['overhead_ns']['service'] for a in h1)/1e9
h1_full=sum(a['finished_ns']-a['started_ns'] for a in h1)/1e9
h1_execution=next(c['execution_seconds'] for c in completed if c['id']=='h1-small-reuse24')
if target=='h2-small-reuse64':
 projection=2*h1_service+(h1_execution-h1_service)
 method='Twice observed H1 service for prospective context64, plus its measured non-service/product admission envelope; then independent1.5x safety.'
else:
 assert any(c['id']=='h2-small-reuse64' for c in completed)
 h2=[json.loads(p.read_text()) for p in (base/'h2-small-reuse64/study/attempts').glob('*.json')]
 assert len(h2)==4 and all(a['status']=='COMPLETED' for a in h2), 'H2 incomplete; do not auto-continue'
 correction=max(1.,h1_service/(19.118863105*16))
 projection=manifest['forecast']['cell_execution_seconds'][2]*correction
 method='Original matched14B sixteen-table service forecast multiplied by max(1, actualH1service / originally projectedH1service), then independent1.5x safety. This is a prospective resource estimate, not a timing-performance claim.'
remaining=5400-used;global_remaining=(310468865220540-time.monotonic_ns())/1e9
record=dict(checked_ns=time.monotonic_ns(),case_id=target,matrix_freeze_sha256=hashlib.sha256((base/'heldout-matrix-freeze.json').read_bytes()).hexdigest(),all_three_recipe_and_protocol_hashes_verified=True,prior_completed=completed,prior_execution_seconds=used,h1_actual_service_seconds=h1_service,h1_actual_native_full_seconds=h1_full,h1_actual_execution_seconds=h1_execution,estimated_execution_seconds=projection,projection_method=method,safety_factor=1.5,required_safety_seconds=1.5*projection,remaining_investigator_execution_seconds=remaining,remaining_original_allocation_seconds=global_remaining,decision='ADMIT_FIXED_CELL_ONCE' if 1.5*projection<min(remaining,global_remaining) else 'STOP_RESOURCE_BUDGET_NO_POPULATION_CHANGE')
path=base/target/'budget-admission.json';assert not path.exists(),'Retain previous budget admission; do not overwrite'
path.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
if record['decision']!='ADMIT_FIXED_CELL_ONCE':raise SystemExit(2)
