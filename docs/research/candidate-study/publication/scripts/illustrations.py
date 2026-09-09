#!/usr/bin/env python3
"""Select descriptive native illustrations under the prospectively fixed rule.

This script reads complete retained evidence and never runs a language model.
All selected cases accompany, and never replace, complete population tables.
"""
import argparse,json,pathlib
from reanalyze import parse,sha,read

p=argparse.ArgumentParser();p.add_argument('--manifest',type=pathlib.Path,required=True);p.add_argument('--evidence-root',type=pathlib.Path,required=True);p.add_argument('--analysis',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
if a.output.exists():raise SystemExit('Choose a new illustration output directory')
a.output.mkdir(parents=True)
manifest=read(a.manifest);analysis=read(a.analysis/'analysis.json');assert analysis['status']=='PASS' and analysis['manifest_sha256']==sha(a.manifest),'Run complete portable reanalysis first'
base=a.evidence_root.resolve();sid=manifest['relationships']['slice_confirmation'];entry=next(e for e in manifest['studies'] if e['id']==sid);study=base/entry['study'];sources={r['request_id']:r for r in read(study/'workload.json')['requests']}
assert sha(study/'workload.json')==entry['expected']['workload_sha256']
rule_reference=manifest['illustration_selection'];rule_path=base/rule_reference['path'];assert sha(rule_path)==rule_reference['sha256'],'Illustration rule hash mismatch'
rule=read(rule_path);queue=read(base/entry['queue_receipt']);assert rule['study']==sid and rule['recorded_ns']<queue['execution_started_ns'],'Illustration rule was not frozen before native execution'
attempts={};prompts={}
for path in sorted((study/'attempts').glob('*.json')):
 attempt=read(path);key=(attempt['pair_index'],attempt['arm']);assert key not in attempts;attempts[key]={'raw':attempt,'path':path,'requests':{r['request_id']:r for r in attempt['requests']}}
 trace_path=study/'raw'/attempt['attempt_id']/'prompt-interventions.json'
 if trace_path.exists():prompts[key]={'path':trace_path,'rows':{r['request_id']:r['result'] for r in read(trace_path)['requests']}}
pairs=sorted({key[0] for key in attempts});assert pairs==[0,1] and len(attempts)==4

def correct(r,expected):return r['status']=='SUCCEEDED' and r['output_text'].strip()==expected

def qualifies(rid,kind):
 expected=sources[rid]['expected']
 return all((correct(attempts[(pair,'baseline')]['requests'][rid],expected) and not correct(attempts[(pair,'candidate')]['requests'][rid],expected)) if kind=='harmful' else (not correct(attempts[(pair,'baseline')]['requests'][rid],expected) and correct(attempts[(pair,'candidate')]['requests'][rid],expected)) for pair in pairs)

def native_summary(attempt_id,rid,request):
 stream_path=study/'raw'/attempt_id/(rid+'.jsonl');events=[]
 for line in stream_path.read_text().splitlines():
  record=json.loads(line);data=record.get('data_utf8')
  if data is not None and data!='[DONE]':events.append(json.loads(data))
 progress=[event for event in events if 'prompt_progress' in event]
 assert all(event.get('tokens_predicted')==0 and event.get('content','')=='' for event in progress),'Unexpected generated content in a prompt-progress event'
 chunks=[event for event in events if not event.get('stop') and 'prompt_progress' not in event]
 content=''.join(event.get('content','') for event in chunks);tokens=[token for event in chunks for token in event.get('tokens',[])]
 assert content==request.get('output_text',''),'Native SSE content differs from the retained output'
 assert tokens==request.get('output_token_ids',[]),'Native SSE token IDs differ from the retained output'
 terminal=[event for event in events if event.get('stop')]
 if request['status']=='SUCCEEDED':assert len(terminal)==1,'Successful selected request lacks one native final event'
 final=terminal[-1] if terminal else {};settings=final.get('generation_settings',{})
 return {'exported_stream_path':stream_path.relative_to(base).as_posix(),'exported_stream_sha256':sha(stream_path),'native_content_reconstruction':content,'native_token_ids':tokens,'excluded_prompt_progress_events':len(progress),'progress_scope':'Native prompt-progress events report zero predicted tokens; their sentinel token field is not a generated output token.','terminal_event_count':len(terminal),'native_stop_type':final.get('stop_type'),'native_truncated':final.get('truncated'),'native_tokens_predicted':final.get('tokens_predicted'),'native_tokens_evaluated':final.get('tokens_evaluated'),'native_prompt_cache_reused':final.get('timings',{}).get('cache_n'),'native_max_tokens':settings.get('max_tokens'),'native_temperature':settings.get('temperature')}

selections=[]
for kind in ['harmful','beneficial']:
 candidates=sorted(rid for rid in sources if qualifies(rid,kind));lookup=[rid for rid in candidates if parse(sources[rid]['prompt'])['family']=='record-lookup']
 selected=(lookup if kind=='harmful' and lookup else candidates)
 if not selected:
  selections.append({'kind':kind,'status':'NO_QUALIFYING_REPEATED_CASE'});continue
 rid=selected[0];src=sources[rid];parsed=parse(src['prompt']);rows=[]
 assert parsed['expected']==src['expected']
 for pair in pairs:
  for arm in ['baseline','candidate']:
   info=attempts[(pair,arm)];r=info['requests'][rid];trace=prompts.get((pair,arm));intervention=trace['rows'][rid] if trace else None;prompt=intervention['prompt'] if intervention else src['prompt'];assert parse(prompt)['expected']==src['expected']
   rows.append({'pair_index':pair,'order':'AB' if pair==0 else 'BA','arm':arm,'attempt_id':info['raw']['attempt_id'],'exported_attempt_sha256':sha(info['path']),'exported_trace_sha256':sha(trace['path']) if trace else None,'prompt':prompt,'output_text':r.get('output_text',''),'output_token_ids':r.get('output_token_ids'),'finish_reason':r.get('finish_reason'),'status':r['status'],'correct':correct(r,src['expected']),'prompt_tokens':r.get('prompt_tokens'),'generated_tokens':r.get('generated_tokens'),'certificate':intervention['certificate'] if intervention else None,'native_sse':native_summary(info['raw']['attempt_id'],rid,r)})
 artifact={'study':sid,'kind':kind,'request_id':rid,'family':parsed['family'],'expected':src['expected'],'original_prompt':src['prompt'],'source_group_id':parsed['group_id'],'features':parsed['features'],'qualifying_repeated_case_count':len(candidates),'qualifying_repeated_lookup_count':len(lookup),'native_rows':rows,'independent_symbolic_answer_check':'PASS for original and every selected prompt','scope':'Descriptive selected illustration, with original and all selected native prompts and outputs. Hashes identify actual exported evidence derivatives. Complete population tables determine reported frequencies.'}
 name=f'{kind}-{rid}';(a.output/(name+'.json')).write_text(json.dumps(artifact,indent=2)+'\n')
 candidate_prompt=next(r['prompt'] for r in rows if r['arm']=='candidate')
 md=[f'# Fresh confirmation {kind} illustration: {rid}','',f'Study `{sid}`; family `{parsed["family"]}`; expected answer `{src["expected"]}`. This is the prospectively selected descriptive illustration. Complete population outcomes remain in the accompanying request and paired tables.','',f'There are {len(candidates)} qualifying repeated {kind} cases, including {len(lookup)} direct lookups. Original and selected prompts independently resolve to the same answer.','', '## Complete original prompt','','```text',src['prompt'],'```','','## Complete selected prompt','','```text',candidate_prompt,'```','','## Every native repetition','','| Order | Arm | Native output | Correct | Finish |','| --- | --- | --- | --- | --- |']
 for row in rows:md.append('| '+row['order']+' | '+row['arm']+' | '+json.dumps(row['output_text']).replace('|','\\|')+' | '+str(row['correct'])+' | '+str(row['finish_reason'])+' |')
 md+=['',f'The companion `{name}.json` retains token IDs reconstructed independently from the native SSE stream, native termination/cache/budget fields, all certificates, prompt counts and exported raw-file hashes. This case illustrates a mechanism; it is not a frequency estimate or an additional evaluation cohort.',''];(a.output/(name+'.md')).write_text('\n'.join(md))
 selections.append({'kind':kind,'status':'SELECTED','request_id':rid,'artifact':name+'.json','qualifying_repeated_cases':len(candidates),'qualifying_repeated_lookup_cases':len(lookup)})
summary={'status':'PASS','study':sid,'manifest_sha256':sha(a.manifest),'analysis_sha256':sha(a.analysis/'analysis.json'),'selection_rule_sha256':sha(rule_path),'selection_script_sha256':sha(pathlib.Path(__file__)),'selections':selections,'native_execution':False}
(a.output/'selection-receipt.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
