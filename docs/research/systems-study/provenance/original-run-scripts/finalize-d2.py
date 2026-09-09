import json,pathlib,subprocess,sys,time,hashlib
root=pathlib.Path.cwd();d=root/'.cache/v1-investigations-20260908/systems/d2-large-reuse24';archive=root/'.cache/packaged-v1-platform-20260908-04/lean-model-lab.pyz';sha=hashlib.sha256(archive.read_bytes()).hexdigest();assert sha=='5f1aabf84635e33dd166ee656d5bcb5830f25a5f4f5d68433e2fd3e4498fb986'
assert (d/'study.queue/receipt.json').exists(),'Native queue has not finalized'
cli=[sys.executable,'-I',str(archive)]
def run(name,command):
 command=list(map(str,command));start=time.monotonic_ns();r=subprocess.run(command,capture_output=True,text=True)
 (d/(name+'.stdout')).write_text(r.stdout);(d/(name+'.stderr')).write_text(r.stderr)
 (d/(name+'.command.json')).write_text(json.dumps(dict(command=command,started_ns=start,finished_ns=time.monotonic_ns(),returncode=r.returncode,archive_sha256=sha),indent=2)+'\n')
 if r.returncode:print(r.stdout,r.stderr);raise SystemExit(r.returncode)
 print(name,'PASS',flush=True)
 if name=='inspect':(d/'inspect.json').write_text(r.stdout)
run('inspect',cli+['inspect',d/'study'])
run('report',cli+['report',d/'study','--output',d/'result.json','--html',d/'report.html'])
run('workbench',cli+['workbench','--study',d/'study','--output',d/'workbench.json','--html',d/'workbench.html'])
run('raw-audit',[sys.executable,'tools/audit_raw_study.py',d/'study','--output',d/'raw-audit.json'])
run('export',[sys.executable,'tools/export_study.py',d/'study','--output',d/'export','--model-path',root/'.cache/prepared-14b-20260908-01/qwen2.5-14b-instruct-fp16-00001-of-00008.gguf'])
