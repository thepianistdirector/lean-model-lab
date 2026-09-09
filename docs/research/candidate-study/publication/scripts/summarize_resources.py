"""Summarize retained native memory and queue/process timing; no inference."""
import argparse,hashlib,json,pathlib
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--manifest',type=pathlib.Path,required=True);p.add_argument('--evidence-root',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
assert not a.output.exists(),'Choose a new output path'
m=read(a.manifest);base=a.evidence_root;attempts=[];timings=[];groups={}
for s in m['studies']:
 report_path=base/s['report'];config_path=base/s['study']/'config.json';queue_path=base/s['queue_receipt']
 assert sha(report_path)==s['expected']['report_sha256'] and sha(config_path)==s['expected']['config_sha256'] and sha(queue_path)==s['expected']['queue_sha256']
 report=read(report_path);config=read(config_path);queue=read(queue_path);profile=config['model']['profile_id'];limit=config['limits']['memory_bytes']
 for at in report['attempts']:
  path=base/s['study']/'raw'/at['attempt_id']/'resource-observations.json';resource=read(path);memory=at['environment']['memory'];assert memory['status']=='MEASURED' and memory['unit']=='bytes' and memory['value']==resource['server_vmhwm_bytes']
  row={'study':s['id'],'model_profile_id':profile,'attempt_id':at['attempt_id'],'arm':at['arm'],'pair_index':at['pair_index'],'server_vmhwm_bytes':resource['server_vmhwm_bytes'],'sampled_server_plus_coordinator_rss_bytes':resource['maximum_observed_aggregate_rss_bytes'],'configured_memory_limit_bytes':limit,'source_resource':path.relative_to(base).as_posix(),'source_resource_sha256':sha(path),'source_report':s['report'],'source_report_sha256':sha(report_path),'source_config':config_path.relative_to(base).as_posix(),'source_config_sha256':sha(config_path)}
  assert 0<row['server_vmhwm_bytes']<=limit and 0<row['sampled_server_plus_coordinator_rss_bytes']<=limit
  attempts.append(row);groups.setdefault(profile,[]).append(row)
 assert queue['started_ns']<=queue['execution_started_ns']<=queue['finished_ns']
 timings.append({'study':s['id'],'archive_process_execution_ns':queue['finished_ns']-queue['execution_started_ns'],'queue_wait_ns':queue['execution_started_ns']-queue['started_ns'],'source_queue_receipt':s['queue_receipt'],'source_queue_sha256':sha(queue_path)})
summary=[]
for profile,rows in sorted(groups.items()):
 item={'model_profile_id':profile,'attempts':len(rows),'studies':len({x['study'] for x in rows}),'configured_memory_limits_bytes':sorted({x['configured_memory_limit_bytes'] for x in rows})}
 for key in ['server_vmhwm_bytes','sampled_server_plus_coordinator_rss_bytes']:
  item[key]={'min':min(x[key] for x in rows),'max':max(x[key] for x in rows),'min_decimal_GB':min(x[key] for x in rows)/1e9,'max_decimal_GB':max(x[key] for x in rows)/1e9}
 summary.append(item)
result={'status':'PASS','manifest_sha256':sha(a.manifest),'script_sha256':sha(pathlib.Path(__file__)),'memory_scope':'Server VmHWM is the maximum observed owned-server /proc high-water mark before shutdown, excluding coordinator. Aggregate RSS is sampled owned server plus coordinator, not a continuous or allocation-wide peak. Neither is whole-host memory or evidence that transient peaks did not occur. Decimal GB equals 1,000,000,000 bytes. No accelerator memory probe is available.','timing_scope':'Archive-process execution is finished_ns minus execution_started_ns; it EXCLUDES queue waiting. Queue waiting is execution_started_ns minus started_ns and remains charged inside original-allocation elapsed time. Legacy queue_execution_s in final analysis/cost-scopes denotes archive-process execution, not queue wait. Attempt, process and original-allocation scopes overlap and must not be added.','per_model':summary,'attempts':attempts,'study_timings':timings,'total_archive_process_execution_ns':sum(x['archive_process_execution_ns'] for x in timings),'total_queue_wait_ns':sum(x['queue_wait_ns'] for x in timings),'native_execution':False}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','per_model':summary,'total_archive_process_execution_ns':result['total_archive_process_execution_ns'],'total_queue_wait_ns':result['total_queue_wait_ns']}))
