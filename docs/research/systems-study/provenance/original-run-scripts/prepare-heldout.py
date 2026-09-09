import hashlib,json,pathlib,subprocess,sys,time,datetime
root=pathlib.Path.cwd();base=root/'.cache/v1-investigations-20260908/systems';archive=root/'.cache/packaged-v1-platform-20260908-04/lean-model-lab.pyz';sha=hashlib.sha256(archive.read_bytes()).hexdigest();assert sha=='5f1aabf84635e33dd166ee656d5bcb5830f25a5f4f5d68433e2fd3e4498fb986'
cli=[sys.executable,'-I',str(archive)];cases=[('h1-small-reuse24','qwen2.5-0.5b-instruct-fp16-v2',24,940129,2),('h2-small-reuse64','qwen2.5-0.5b-instruct-fp16-v2',64,940193,2),('h3-large-reuse24','qwen2.5-14b-instruct-fp16-v1',24,940129,6)]
hypotheses=[
'H1: Across the frozen new tables, dependency slicing reduces first-use newly processed input tokens while the full-context cached baseline may require fewer new tokens on subsequent changing queries. Report cold, warm and all-query counters separately per table and attempt; no counterfactual extension past eight queries.',
'H2: Lower input-token work or shorter service/full wall cannot establish an efficiency gain when original quality gates fail. Report native generated-token counts, exact outputs and all charged cache preparation so output-length changes remain an explicit timing confound.',
'H3: Enumerate both-correct, baseline-only-correct, candidate-only-correct and both-wrong classes for each table and pair across the two context sizes and admitted model configurations. The joint correctness classes describe observed paired answers; they are not a deployable two-output oracle or a controller.',
'H4: Compare descriptive directions across 0.5B context24 versus64 and matched 0.5B versus14B context24 populations. Preserve model/runtime/thread differences and all failed states; no novel method, general language-quality, energy, API-price or population-risk claim.'
]
freezes=[]
for cid,profile,context,seed,threads in cases:
 d=base/cid;d.mkdir(exist_ok=False)
 def run(name,args):
  command=cli+list(map(str,args));start=time.monotonic_ns();r=subprocess.run(command,capture_output=True,text=True)
  (d/(name+'.stdout')).write_text(r.stdout);(d/(name+'.stderr')).write_text(r.stderr)
  (d/(name+'.command.json')).write_text(json.dumps(dict(command=command,started_ns=start,finished_ns=time.monotonic_ns(),returncode=r.returncode,archive_sha256=sha),indent=2)+'\n')
  if r.returncode:print(r.stdout,r.stderr);raise SystemExit(r.returncode)
 run('propose',['research','propose','--mechanism','slice-versus-full-cache-v1','--output',d/'proposal.json'])
 run('protocol-template',['research','protocol','--proposal',d/'proposal.json','--output',d/'protocol-template.json'])
 protocol=json.loads((base/'d2-large-reuse24/protocol.json').read_text());template=json.loads((d/'protocol-template.json').read_text());protocol['proposal_sha256']=template['proposal_sha256']
 protocol['hypothesis']='\n'.join(hypotheses)
 protocol['development_evidence']='Preserved D1 and D2 matched original record-reuse/context24/seed940101 development results: 0.5B full1/8 versus slice4/8; 14B full3/8 versus slice1/8 in each repetition. Neither passed quality. This is a frozen held-out negative/system-cost challenge, not reopened model/wording/seed search or positive-advance confirmation.'
 protocol['selection_rule']='Run the three jointly frozen held-out cells once in declared order, subject only to resource/time feasibility. Preserve the unchanged platform gate: each arm >=95% exact task accuracy, no observed aggregate pair-level candidate loss. An ineligible case remains ineligible; no efficiency ratios after failed quality. No cell is selected, discarded, repeated or replaced based on its quality outcome.'
 protocol['stopping_rule']='Exactly h1-small-reuse24 seed940129, h2-small-reuse64 seed940193, h3-large-reuse24 seed940129; each original record-reuse, BOTH cached, confirmation128 requests, two AB/BA pairs, C1, threads2/2/6. All three protocols and recipes frozen before first native request. Before each queue launch require 1.5 times the then-current prospective execution estimate to fit remaining investigator5400-second execution budget and original deadline310468865220540. Total investigator offered requests <=1600 including64 development. Use actual first held-out case timing to update later projections, without altering populations, gates, settings or hypotheses. No failed-quality efficiency ratios or subsequent wording/model/seed search. Preserve all failures/interruptions and costs; no automatic retries.'
 protocol['claim_limit']='Instrumented held-out negative CPU cache/compression and model/context-transfer challenge with substantial known prior-art overlap; no novelty or quality-qualified efficiency claim if gates fail. No energy measurement, API-price equivalence, natural-language generalization or formal risk guarantee.'
 protocol['uncertainty']='Sixteen independently generated tables per cell, eight dependent ordered queries per table, two balanced repetitions. Report per-table and paired descriptive distributions/ranges; no request-IID confidence interval or significance claim. The model transfer uses matched generated requests but distinct model/thread/server configurations.'
 (d/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
 run('freeze',['research','freeze',d/'proposal.json','--output',d/'proposal-bundle']);run('verify-proposal',['research','verify',d/'proposal-bundle'])
 run('study-create',['research','study-create','--proposal',d/'proposal.json','--protocol',d/'protocol.json','--allocation',root/'.cache/allocation-0.4-20260908.json','--model-profile',profile,'--family','record-reuse','--context-records',context,'--split','confirmation','--purpose','MEASUREMENT','--requests','128','--seed',seed,'--concurrency','1','--pairs','2','--threads',threads,'--output',d/'recipe.json'])
 run('recipe-validate',['recipe','validate',d/'recipe.json'])
 freezes.append(dict(id=cid,profile=profile,context_records=context,seed=seed,threads=threads,requests_per_attempt=128,attempts=4,protocol_file_sha256=hashlib.sha256((d/'protocol.json').read_bytes()).hexdigest(),recipe_file_sha256=hashlib.sha256((d/'recipe.json').read_bytes()).hexdigest()))
 print(cid,'FROZEN',flush=True)
small_service=19.118863105;small_other=25.028197536-small_service
large_service=143.19881433;large_other=213.724989432-large_service
projections=[small_service*16+small_other,small_service*16*2+small_other,large_service*16+large_other]
record=dict(frozen_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),frozen_ns=time.monotonic_ns(),archive_sha256=sha,implementation_sha256='18c28e8075ebc9e5651bf4e0a66c2fca332480b4834a7342fc49d43775a9ab32',classification='HELD_OUT_NEGATIVE_SYSTEM_COST_CHALLENGE_NOT_POSITIVE_ADVANCE',hypotheses=hypotheses,cases=freezes,prior_offered_requests=64,maximum_total_offered_requests=1600,prior_execution_seconds=248.081342296,maximum_native_execution_seconds=5400,original_deadline_ns=310468865220540,forecast=dict(cell_execution_seconds=projections,safety_factor=1.5,safety_total_seconds=sum(projections)*1.5,remaining_execution_budget_seconds=5400-248.081342296,method='Scale per-case development service for sixteen tables while retaining four attempt non-service envelopes; context64 small-model service multiplier2 is prospective, uncertain, and must be replaced by available held-out timing evidence before admission. Add 1.5x safety per case; no additional populations if resource check fails. Native request service and full execution remain separately charged.'))
assert sum(projections)*1.5 < 5400-248.081342296
(base/'heldout-matrix-freeze.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record['forecast'],indent=2))
