#!/usr/bin/env python3
"""Prepare an explicitly redacted derivative of a finalized study; never publish it."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import shutil
import sys
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from lean_model_lab.artifacts import write_json_new,write_new
from lean_model_lab.contracts import canonical_bytes,digest,file_digest,parse_json,read_json
from lean_model_lab.llama_adapter import MODEL_FILENAME
from lean_model_lab.profiles import get_model_profile
from lean_model_lab.session import Session,SessionError
from lean_model_lab.study_report import evaluate_inventory


def inventory_files(root: Path) -> dict:
    result={}
    for p in sorted(root.rglob('*')):
        if p.is_symlink():raise ValueError('export refuses symlinks')
        if p.is_file():
            result[p.relative_to(root).as_posix()]={'sha256':file_digest(p),'size_bytes':p.stat().st_size}
        elif not p.is_dir():raise ValueError('export refuses nonregular entries')
    return result


def redact_raw(path: Path, model_path: str, replacements=None) -> tuple[bytes,list]:
    original=path.read_bytes()
    if len(original)>16*1024*1024:raise ValueError('raw file exceeds reviewed export bound')
    changes=[]
    replacements=replacements or {model_path:MODEL_FILENAME}
    if path.name=='server.log':
        lines=original.decode('utf-8').splitlines(keepends=True)
        for i,line in enumerate(lines):
            for private,replacement in replacements.items():
                if private in lines[i]:
                    if not any(marker in line for marker in ('load_model','llama_model_loader','llama_model_load')):
                        raise ValueError('model path occurs outside reviewed loader log metadata')
                    lines[i]=lines[i].replace(private,replacement)
                    changes.append({'line':i+1,'kind':'operational-log-redaction','replacement':replacement})
        return ''.join(lines).encode(),changes
    if re.fullmatch(r'r[0-9]{3,4}\.jsonl',path.name):
        lines=original.splitlines(keepends=True)
        for i,line in enumerate(lines):
            receipt=parse_json(line)
            if 'data_utf8' not in receipt or receipt['data_utf8']=='[DONE]':continue
            event=parse_json(receipt['data_utf8'])
            if type(event) is not dict or event.get('model') not in replacements:continue
            if event.get('stop') is not True:raise ValueError('model path occurs outside terminal response metadata')
            revised=copy.deepcopy(event);revised['model']=replacements[event['model']]
            # Only /model may change. All scientific values remain exactly equal.
            if canonical_bytes({k:v for k,v in event.items() if k!='model'})!=canonical_bytes({k:v for k,v in revised.items() if k!='model'}):
                raise ValueError('redaction changed scientific payload')
            modified=dict(receipt);modified['data_utf8']=json.dumps(revised,ensure_ascii=False,separators=(',',':'))
            lines[i]=canonical_bytes(modified)+b'\n'
            changes.append({'line':i+1,'kind':'raw-response-metadata-redaction',
                'pointer':'/data_utf8 (decoded JSON) /model','replacement':revised['model'],
                'unchanged_payload_without_model_sha256':digest({k:v for k,v in event.items() if k!='model'})})
        return b''.join(lines),changes
    return original,changes


def export(source: Path, output: Path, model_path: str) -> dict:
    source=source.resolve();output=output.resolve()
    if output.is_relative_to(source) or source.is_relative_to(output):
        raise ValueError('source and derivative output must be separate directory trees')
    if not Path(model_path).is_absolute():
        raise ValueError('supply the exact original absolute model path for reviewed metadata redaction')
    if (source/'EXPORT-PROVENANCE.json').exists():raise ValueError('export the original producer, not an existing derivative')
    started=time.monotonic_ns()
    with Session.open(source) as session:
        original_inventory=session.inspect()
        config=original_inventory['config']
        profile=get_model_profile(config['model']['profile_id'] if config['schema_version'] in (2,3) else 'qwen2.5-0.5b-instruct-fp16-v1')
        if Path(model_path).name!=profile['entrypoint']:raise ValueError('original model path does not match the admitted entrypoint')
        replacements={str(Path(model_path).parent/f['filename']):f['filename'] for f in profile['files']}
        if not original_inventory['inventory_complete']:
            raise SessionError('export requires a finalized, reconciled source inventory')
        original_report=evaluate_inventory(original_inventory,study_root=source)
        original_catalog=inventory_files(source)
        output.mkdir(parents=True,exist_ok=False)
        destination=output/'study'
        shutil.copytree(source,destination)
        provenance=output/'original-provenance';provenance.mkdir()
        for name in ('session.json','config.json','workload.json','setup.json','journal.jsonl'):
            shutil.copyfile(source/name,provenance/name)
        shutil.copytree(source/'events',provenance/'events')
        changes=[]
        for path in sorted((destination/'raw').rglob('*')):
            if not path.is_file():continue
            data,edits=redact_raw(path,model_path,replacements)
            if edits:
                relative=path.relative_to(destination).as_posix()
                before=original_catalog[relative]
                path.write_bytes(data)  # Only the new, unpublished derivative is mutable here.
                changes.append({'path':relative,'original':before,
                    'exported':{'sha256':file_digest(path),'size_bytes':len(data)},'changes':edits})
        # Rebind only the terminal raw inventory and its downstream hash chain.
        previous=digest(read_json(destination/'session.json'));events=[]
        for event_file in sorted((destination/'events').iterdir()):
            event=read_json(event_file)
            event['previous_sha256']=previous
            if event['kind']=='terminal':
                raw=destination/'raw'/event['payload']['attempt_id']
                event['payload']['raw_files']=[{'path':name,**meta} for name,meta in inventory_files(raw).items()]
            event_file.write_bytes(canonical_bytes(event)+b'\n')
            previous=digest(event);events.append(event)
        (destination/'journal.jsonl').write_bytes(b''.join(canonical_bytes(event)+b'\n' for event in events))
        with Session.open(destination) as derivative:
            derived_inventory=derivative.inspect()
            derived_report=evaluate_inventory(derived_inventory,study_root=destination)
        if canonical_bytes(original_report)!=canonical_bytes(derived_report):
            raise ValueError('derivative changed computed report outcomes')
        # The original opaque hashes and event chain are retained without its private raw paths.
        write_json_new(provenance/'file-catalog.json',original_catalog)
        manifest={'schema_version':1,'export_class':'REDACTED_DERIVATIVE_NOT_ORIGINAL_RAW',
            'scope':'Exact model-path replacement in operational logs and terminal SSE /model metadata; '
                    'request/token/timing/quality/configuration data and normalized attempts unchanged.',
            'source_session_sha256':file_digest(source/'session.json'),
            'source_journal_sha256':file_digest(source/'journal.jsonl'),
            'source_event_chain_head_sha256':digest(read_json(sorted((source/'events').iterdir())[-1])) if events else digest(read_json(source/'session.json')),
            'exported_event_chain_head_sha256':previous,'changed_raw_files':changes,
            'report_unchanged_sha256':digest(original_report),
            'original_raw_bytes':'retained privately by producer; only original hashes are supplied here',
            'integrity_limit':'Hashes establish local consistency, not independent authentication of the producer or redaction attestation.',
            'started_ns':started,'finished_ns':time.monotonic_ns(),
            'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip()}
        write_json_new(destination/'EXPORT-PROVENANCE.json',manifest)
        write_json_new(output/'report.json',derived_report)
        from lean_model_lab.report import render_report
        write_new(output/'report.html',render_report(derived_report).encode())
        # Fail closed on any remaining absolute home/temp path, including unexpected fields.
        # This is a scoped path check, not a universal secret detector or publication approval.
        for p in output.rglob('*'):
            if p.is_file() and (model_path.encode() in p.read_bytes() or
                re.search(rb'/(?:home|Users|tmp)/',p.read_bytes())):
                raise ValueError('unreviewed filesystem path remains in export; output is incomplete')
        if inventory_files(source)!=original_catalog:raise ValueError('source changed during export')
        ready={'status':'LOCAL_REDACTED_EXPORT_VERIFIED_NOT_PUBLISHED',
               'provenance_sha256':file_digest(destination/'EXPORT-PROVENANCE.json'),
               'report_sha256':file_digest(output/'report.json'),
               'changed_raw_file_count':len(changes),
               'expected_requests':sum(len(original_inventory['workload']['requests']) for _ in original_inventory['attempts']),
               'observed_requests':sum(len(a['requests']) for a in original_inventory['attempts'])}
        write_json_new(output/'EXPORT-READY.json',ready)
        return ready


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--model-path',required=True)
    args=parser.parse_args()
    try:print(json.dumps(export(args.source,args.output,args.model_path)))
    except (OSError,ValueError) as exc:
        print('lean-model-lab export: '+str(exc),file=sys.stderr);raise SystemExit(2)
