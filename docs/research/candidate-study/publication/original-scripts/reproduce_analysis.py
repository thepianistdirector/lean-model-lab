#!/usr/bin/env python3
"""Reproduce read-only scientific tables in a NEW output directory.

This command never executes a model, trains a replacement, or regenerates tasks.
"""
import argparse,pathlib,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();own=pathlib.Path(__file__).resolve().parent;root=own.parents[2]
if a.output.exists():raise SystemExit('Choose a new analysis output directory')
a.output.mkdir(parents=True)
args=[sys.executable,str(own/'analyze_negative.py')]
for name in ['negative-fit-study04','negative-calibration-study04','negative-budget-control-study04','negative-confirm-slice-study04','negative-confirm-simple-study04','negative-confirm-learned-study04']:
 study=own/name
 if not (study.with_name(study.name+'.queue')/'receipt.json').exists():raise SystemExit('All frozen negative studies must be complete before final analysis reproduction: '+name)
 args+=['--study',str(study)]
args+=['--output',str(a.output.resolve())]
subprocess.run(args,cwd=root,check=True)
