"""Observe the queued confirmation and inspect terminal evidence once.

No model invocation or retry is implemented here. Run from the source root.
"""
from pathlib import Path
import collections
import json
import os
import subprocess
import time

BASE = Path('.cache/v1-investigations-20260908/quality/confirmation-14b')
STUDY = BASE / 'study'
ARCHIVE = '.cache/packaged-v1-platform-20260908-04/lean-model-lab.pyz'
QUEUE_RECEIPT = BASE / 'study.queue' / 'receipt.json'
progress = BASE / 'progress-observations.jsonl'
while not QUEUE_RECEIPT.exists():
    kinds = collections.Counter()
    for path in (STUDY / 'events').glob('*.json'):
        try:
            kinds[json.loads(path.read_text())['kind']] += 1
        except (OSError, json.JSONDecodeError):
            continue
    value = dict(monotonic_ns=time.monotonic_ns(), event_counts=dict(kinds),
                 host_load=list(os.getloadavg()),
                 scope='Operational progress only; no expected answers or output quality inspected.')
    with progress.open('a') as stream:
        stream.write(json.dumps(value) + '\n')
    print(json.dumps(value), flush=True)
    time.sleep(45)

commands = [
    ('inspect', ['python3', ARCHIVE, 'inspect', str(STUDY)]),
    ('report', ['python3', ARCHIVE, 'report', str(STUDY), '--output', str(BASE/'result.json'), '--html', str(BASE/'report.html')]),
    ('workbench', ['python3', ARCHIVE, 'workbench', '--study', str(STUDY), '--output', str(BASE/'workbench.json'), '--html', str(BASE/'workbench.html')]),
    ('raw-audit', ['python3', 'tools/audit_raw_study.py', str(STUDY), '--output', str(BASE/'raw-audit.json')]),
]
results = []
for name, command in commands:
    start = time.monotonic_ns()
    result = subprocess.run(command, capture_output=True, text=True)
    (BASE/(name+'.stdout')).write_text(result.stdout)
    (BASE/(name+'.stderr')).write_text(result.stderr)
    receipt = dict(command=command,start_ns=start,finish_ns=time.monotonic_ns(),returncode=result.returncode)
    (BASE/(name+'.receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n')
    results.append(receipt)
    print(json.dumps(dict(phase=name,returncode=result.returncode)),flush=True)

if (BASE/'result.json').exists() and (BASE/'raw-audit.json').exists():
    for name, command in [
        ('export', ['python3','tools/export_study.py',str(STUDY),'--output',str(BASE/'export'),
                    '--model-path',str(Path('.cache/prepared-14b-20260908-01/qwen2.5-14b-instruct-fp16-00001-of-00008.gguf').resolve())]),
        ('derive', ['.cache/research-plot-env/bin/python','docs/research/quality-study/confirmation-14b/derive.py']),
    ]:
        start=time.monotonic_ns()
        result=subprocess.run(command,capture_output=True,text=True)
        (BASE/(name+'.stdout')).write_text(result.stdout)
        (BASE/(name+'.stderr')).write_text(result.stderr)
        receipt=dict(command=command,start_ns=start,finish_ns=time.monotonic_ns(),returncode=result.returncode)
        (BASE/(name+'.receipt.json')).write_text(json.dumps(receipt,indent=2)+'\n')
        results.append(receipt)
        print(json.dumps(dict(phase=name,returncode=result.returncode,error=result.stderr[-1000:])),flush=True)

(BASE/'analysis-operations.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(dict(status='TERMINAL_ANALYSIS_OPERATIONS_RETAINED',queue_receipt=json.loads(QUEUE_RECEIPT.read_text()))),flush=True)
