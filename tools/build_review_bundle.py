#!/usr/bin/env python3
"""Build a local review-only source/CLI/redacted-evidence bundle; never publish."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE_FILES=('.gitignore','ARCHITECTURE.md','CONTRIBUTING.md','EXPERIMENTS.md','LICENSE',
    'README.md','WORKSPACE.json','ROADMAP.md','SOURCES.md','STATUS.md','TASKS.md','THIRD_PARTY_NOTICES.md')
SOURCE_DIRS=('docs','patches','plan','src','tests','tools','workloads')
SUFFIXES={'.py','.md','.json','.html','.txt','.patch'}
STUDIES=('comparison','protocol-failure','recovery-control')


def sha(data):return hashlib.sha256(data).hexdigest()

def check_text(name,data):
    text=data.decode('utf-8')
    # Known actual developer paths are forbidden. Fixture sentinels deliberately
    # test redaction and contain no actual account, directory or credential.
    paths=re.findall(r'/(?:home|Users)/[^\s\"\'<>]+',text)
    allowed=name.endswith(('tests/test_export.py','tools/build_review_bundle.py'))
    if any(not (allowed and p.startswith(('/home/fixture/','/home/other/'))) for p in paths):
        raise ValueError('unreviewed private path in '+name)
    if re.search(r'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',text):
        raise ValueError('credential-like content in '+name)


def collect(directory,prefix,source=False):
    result={}
    for p in sorted(directory.rglob('*')):
        if p.is_symlink():raise ValueError('refusing symlink')
        if not p.is_file():continue
        if source and ('__pycache__' in p.parts or p.suffix not in SUFFIXES):continue
        relative=p.relative_to(directory).as_posix()
        name=prefix+'/'+relative
        data=p.read_bytes()
        check_text(name,data)
        result[name]=data
    return result


def write_zip(path,files,directories=()):
    directories=sorted(set(directories))
    manifest={'schema_version':1,'status':'LOCAL_REVIEW_CANDIDATE_NOT_PUBLISHED','directories':directories,
        'files':{k:{'sha256':sha(v),'bytes':len(v)} for k,v in sorted(files.items())}}
    contents=dict(files);contents['FILE-MANIFEST.json']=(json.dumps(manifest,sort_keys=True,indent=2)+'\n').encode()
    with zipfile.ZipFile(path,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for name in directories:
            if not name.endswith('/') or name.startswith('/') or '..' in Path(name).parts:raise ValueError('unsafe directory entry')
            info=zipfile.ZipInfo(name,(2026,9,8,0,0,0));info.external_attr=(0o40755<<16)|0x10
            z.writestr(info,b'')
        for name,data in sorted(contents.items()):
            if name.startswith('/') or '..' in Path(name).parts:raise ValueError('unsafe archive entry')
            info=zipfile.ZipInfo(name,(2026,9,8,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
            z.writestr(info,data)
    with zipfile.ZipFile(path) as z:
        if len(z.namelist())!=len(set(z.namelist())) or set(z.namelist())!=set(contents)|set(directories):raise ValueError('archive inventory differs')
        for name,data in contents.items():
            if z.read(name)!=data:raise ValueError('archive readback differs')
    return {'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size,'file_count':len(contents),'directory_count':len(directories)}


def build(output,archive,producer,evidence):
    output=output.resolve()
    if not output.is_relative_to(ROOT):raise ValueError('output must be project-scoped')
    if any(output==p.resolve() or output in p.resolve().parents for p in (archive,producer,evidence)):
        raise ValueError('output overlaps inputs')
    output.mkdir(parents=True,exist_ok=False)
    source={}
    for name in SOURCE_FILES:
        p=ROOT/name
        if p.is_symlink():raise ValueError('refusing source symlink')
        data=p.read_bytes();check_text(name,data);source['lean-model-lab-source/'+name]=data
    for name in SOURCE_DIRS:source.update(collect(ROOT/name,'lean-model-lab-source/'+name,source=True))
    base=subprocess.run(['git','rev-parse','HEAD'],cwd=ROOT,text=True,capture_output=True,check=True).stdout.strip()
    source['lean-model-lab-source/BASE-REVISION.txt']=(base+'\nUncommitted source snapshot; FILE-MANIFEST.json is its exact inventory.\n').encode()
    artifacts={'lean-model-lab-source.zip':write_zip(output/'lean-model-lab-source.zip',source)}
    raw={};directories=[]
    for study in STUDIES:
        ready=json.loads((evidence/study/'EXPORT-READY.json').read_text())
        if ready['status']!='LOCAL_REDACTED_EXPORT_VERIFIED_NOT_PUBLISHED':raise ValueError('unverified export')
        if sha((evidence/study/'report.json').read_bytes())!=ready['report_sha256']:raise ValueError('export report drift')
        if sha((evidence/study/'study'/'EXPORT-PROVENANCE.json').read_bytes())!=ready['provenance_sha256']:raise ValueError('export provenance drift')
        raw.update(collect(evidence/study,'evidence/'+study))
        directories.extend('evidence/'+study+'/'+d.relative_to(evidence/study).as_posix()+'/' for d in sorted((evidence/study).rglob('*')) if d.is_dir())
    artifacts['lean-model-lab-evidence.zip']=write_zip(output/'lean-model-lab-evidence.zip',raw,directories)
    implementations=[]
    for src,name in [(archive,'lean-model-lab.pyz'),(producer,'measured-producer.pyz')]:
        with zipfile.ZipFile(src) as z:
            m=json.loads(z.read('BUILD-MANIFEST.json'))
            if set(z.namelist())!=set(m['files'])|{'BUILD-MANIFEST.json'}:raise ValueError('CLI manifest inventory mismatch')
            for entry,digest in m['files'].items():
                data=z.read(entry)
                if sha(data)!=digest:raise ValueError('CLI manifest content mismatch')
                check_text(entry,data)
            implementations.append({k:v for k,v in m['files'].items() if k.startswith('lean_model_lab/')})
        shutil.copyfile(src,output/name)
        artifacts[name]={'sha256':sha(src.read_bytes()),'bytes':src.stat().st_size}
    if implementations[0]!=implementations[1]:raise ValueError('review CLI runtime differs from measured producer')
    result={'schema_version':1,'status':'LOCAL_REVIEW_CANDIDATE_NOT_PUBLISHED','version':'0.1.0.dev0',
        'source_base_revision':base,'artifacts':artifacts,'runtime_source_matches_measured_producer':True,
        'cli_difference':'Updated dependency notice distinguishes synthetic fixture reports from real model reports; Python runtime source is identical.',
        'privacy_scope':'Explicit source/evidence allowlist, UTF-8 paths/credential-pattern scan and hash readback; no weights, backend binary, account configuration, cache or original private raw directory included. This scan is not an independent security attestation.',
        'missing_release_gates':['public authorization/publication and author identity','supported authenticated native Tanduna publication and actual review/decision','public-artifact external execution/recovery','qualified researcher observations','browser accessibility runtime checks']}
    (output/'CANDIDATE-MANIFEST.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--archive',type=Path,required=True)
    p.add_argument('--producer',type=Path,required=True);p.add_argument('--evidence',type=Path,required=True)
    a=p.parse_args();print(json.dumps(build(a.output,a.archive,a.producer,a.evidence),indent=2))
