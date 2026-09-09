import hashlib,json,pathlib,subprocess,sys,time,datetime
root=pathlib.Path.cwd(); base=root/'.cache/v1-investigations-20260908/systems'; d=base/'d2-large-reuse24';d.mkdir(exist_ok=False)
archive=root/'.cache/packaged-v1-platform-20260908-04/lean-model-lab.pyz'
sha=hashlib.sha256(archive.read_bytes()).hexdigest();assert sha=='5f1aabf84635e33dd166ee656d5bcb5830f25a5f4f5d68433e2fd3e4498fb986'
cli=[sys.executable,'-I',str(archive)]
def run(name,args):
 command=cli+list(map(str,args));start=time.monotonic_ns();r=subprocess.run(command,capture_output=True,text=True)
 (d/(name+'.stdout')).write_text(r.stdout);(d/(name+'.stderr')).write_text(r.stderr)
 (d/(name+'.command.json')).write_text(json.dumps(dict(command=command,started_ns=start,finished_ns=time.monotonic_ns(),returncode=r.returncode,archive_sha256=sha),indent=2)+'\n')
 if r.returncode:print(r.stderr);raise SystemExit(r.returncode)
 print(name,'PASS',flush=True)
run('propose',['research','propose','--mechanism','slice-versus-full-cache-v1','--output',d/'proposal.json'])
run('protocol-template',['research','protocol','--proposal',d/'proposal.json','--output',d/'protocol-template.json'])
protocol=json.loads((base/'d1-small-reuse24/protocol.json').read_text());template=json.loads((d/'protocol-template.json').read_text());protocol['proposal_sha256']=template['proposal_sha256']
protocol['development_evidence']='D1 original record-reuse/context24/seed940101: 0.5B full-cache baseline 1/8 correct and sliced-cache candidate 4/8 correct in each of two repetitions. Both failed 95%. The predeclared single 14B alternative uses identical original grammar, table and queries. The unrelated single explicit-language chain diagnostic was adverse; no wording search is performed.'
protocol['selection_rule']='Require BOTH full-context and sliced arms to reach at least 95% exact task accuracy in EACH attempt, requiring 8/8 here, plus no pair-level aggregate accuracy loss. Any failure stops model and wording search. Root coordination and a new finite pre-confirmation freeze are required before any held-out matrix.'
protocol['stopping_rule']='Execute this single fixed 14B development case once: original record-reuse, context24, seed940101, 8 requests per attempt, two balanced AB/BA pairs, C1, six threads, slice-versus-full-cache-v1. Preserve every failed or interrupted attempt. No further model/wording/seed search after quality failure; any subsequent frozen held-out failure/system-cost challenge requires separate root coordination. Investigator total <=3000 new offered requests and <=5400 seconds native execution; original deadline310468865220540 cannot change.'
(d/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
run('freeze',['research','freeze',d/'proposal.json','--output',d/'proposal-bundle'])
run('verify-proposal',['research','verify',d/'proposal-bundle'])
run('study-create',['research','study-create','--proposal',d/'proposal.json','--protocol',d/'protocol.json','--allocation',root/'.cache/allocation-0.4-20260908.json','--model-profile','qwen2.5-14b-instruct-fp16-v1','--family','record-reuse','--context-records','24','--split','development','--purpose','DEVELOPMENT','--requests','8','--seed','940101','--concurrency','1','--pairs','2','--threads','6','--output',d/'recipe.json'])
run('recipe-validate',['recipe','validate',d/'recipe.json'])
(d/'preexecution-freeze.json').write_text(json.dumps(dict(frozen_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),frozen_ns=time.monotonic_ns(),archive_sha256=sha,protocol_file_sha256=hashlib.sha256((d/'protocol.json').read_bytes()).hexdigest(),recipe_file_sha256=hashlib.sha256((d/'recipe.json').read_bytes()).hexdigest(),new_offered_requests=32,prior_investigator_offered_requests=32,prior_queue_execution_seconds=29.500493033,original_deadline_ns=310468865220540,stage='single predeclared 14B feasibility alternative; no confirmation'),indent=2)+'\n')
print('FROZEN',d)
