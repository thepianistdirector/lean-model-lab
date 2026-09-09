#!/usr/bin/env python3
"""Retain exact product inspection/report/workbench plus independent audit/export.

No native execution or retry occurs here. All destination names must be new.
"""
import argparse,pathlib,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--study',type=pathlib.Path,required=True);p.add_argument('--archive',type=pathlib.Path,required=True);p.add_argument('--label',required=True);p.add_argument('--model',type=pathlib.Path,required=True);a=p.parse_args()
root=pathlib.Path(__file__).resolve().parents[3];own=pathlib.Path(__file__).resolve().parent;stem=a.study.name.replace('-study','');base=a.study.parent
commands=[('inspect',['python3','-I',str(a.archive),'inspect',str(a.study)]),('report',['python3','-I',str(a.archive),'report',str(a.study),'--output',str(base/(stem[:-2]+'-report'+stem[-2:]+'.json')),'--html',str(base/(stem[:-2]+'-report'+stem[-2:]+'.html'))]),('workbench',['python3','-I',str(a.archive),'workbench','--study',str(a.study),'--output',str(base/(stem[:-2]+'-workbench'+stem[-2:]+'.json')),'--html',str(base/(stem[:-2]+'-workbench'+stem[-2:]+'.html'))]),('raw-audit',['python3','tools/audit_raw_study.py',str(a.study),'--output',str(base/(stem[:-2]+'-raw-audit'+stem[-2:]+'.json'))]),('export',['python3','tools/export_study.py',str(a.study),'--output',str(base/(stem[:-2]+'-export'+stem[-2:])),'--model-path',str(a.model.resolve())])]
for suffix,command in commands:
 subprocess.run([sys.executable,str(own/'record_command.py'),a.label+'-'+suffix,'--']+command,cwd=root,check=True)
