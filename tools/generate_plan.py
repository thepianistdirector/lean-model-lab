#!/usr/bin/env python3
"""Generate human and publication projections from the canonical task ledger."""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def render(plan: dict) -> dict[str, str]:
    tasks, waves = plan['tasks'], plan['waves']
    counts = dict(sorted(Counter(t['targetRelease'] for t in tasks).items()))
    by_id = {t['id']: t for t in tasks}
    intro = ('Generated from [plan/tasks.json](plan/tasks.json); edit the canonical ledger, then run '
             '`python3 tools/generate_plan.py`. Task states and evidence live in that ledger; '
             '[STATUS.md](STATUS.md) summarizes the root execution evidence. Native publication is separate.\n\n')
    task_lines = ['# Lean Model Lab contributor tasks\n', intro,
                  f'{len(tasks)} active outcomes in {len(waves)} waves. Release horizons: '+', '.join(f'{k}: {v}' for k,v in counts.items())+'.\n',
                  'The three historical foundation outcomes remain DONE. New planning rows do not establish implementation, automated pass, runtime proof, user validation or release. Full original contracts and history remain in [immutable lineage](plan/lineage/821c6364/plan/tasks.json). Historical source contracts are not additional active outcomes.\n',
                  'Before executing a new packet, the root records owned files, actual commands, falsifiers, resource/permission bounds and exit evidence. Model-free checks are preparation; 0.1 requires real inference and quality evaluation.\n']
    for wave in waves:
        task_lines += [f"## Wave {wave['id']}: {wave['name']}\n", f"Horizon: {wave['targetRelease']}. Exit evidence: {wave['exitEvidence']}\n"]
        for key in wave['taskIds']:
            t=by_id[key]
            task_lines += [f"### {t['id']} — {t['title']}\n", f"- Project key: `{t['key']}`; feature area: {t['featureArea']}; target: {t['targetRelease']}; status: **{t['status']}**; evidence: **{t['evidenceLevel']}**.\n",
             f"- Outcome: {t['outcome']}\n",f"- Dependencies: {', '.join(t['dependsOn']) or 'none'}.\n",f"- Acceptance: {t['acceptance']}\n",f"- Origin: {t['requirementClass']}; references: {', '.join(t['sourceRefs'])}.\n",f"- Risk/evidence needs: {t['riskEvidenceNeeds']}\n"]
            if t['evidence']:
                task_lines.append('- Recorded evidence: '+'; '.join(e['reference']+' ('+e['scope']+')' for e in t['evidence'])+'.\n')
    task_lines += ['## Source mapping and history\n','Each row preserves original identity, frozen revision, acceptance, predecessors and history in the canonical mapping; platform IDs remain null until supported creation returns them.\n', '| Original source | Treatment | Successors |\n| --- | --- | --- |\n']
    for m in plan['sourceMappings']:
        task_lines.append(f"| {m['sourceId']} | {m['treatment']} | {', '.join(m['successorIds'])} |\n")
    road = ['# Lean Model Lab outcome roadmap\n',intro,
            plan['objective']+'\n\n',f"{len(tasks)} active task outcomes; {len(waves)} waves; "+str(sum(len(t['dependsOn']) for t in tasks))+' explicit prerequisite edges.\n',
            'The original 27 task records, 71 edges, original Waves 0–8 and eight scientific gates are preserved verbatim in [historical roadmap](plan/lineage/821c6364/ROADMAP.md). The new narrow inference path does not mark training or analytical predecessors complete.\n',
            '## Evidence and scope\n']
    for fact in plan['facts']: road.append(f"- **{fact['kind']}**: {fact['text']}\n")
    for w in waves:
        road += [f"\n## Wave {w['id']}: {w['name']}\n",f"- Horizon: {w['targetRelease']}.\n",f"- Outcome: {w['outcome']}\n",f"- Entry dependencies: {', '.join(w['entryDependencies']) or 'none'}.\n",f"- Exit evidence: {w['exitEvidence']}\n",f"- Assigned tasks ({len(w['taskIds'])}): {', '.join(w['taskIds'])}.\n"]
        for k in w['taskIds']:
            t=by_id[k];road.append(f"  - {k}: {t['title']} — {t['status']} / {t['evidenceLevel']}.\n")
    road += ['\n## Publication and access\n',f"Native publication status: **{plan['publication']['status']}**. {plan['publication']['accessInstructions']}\n",'\nRequired destinations: [public roadmap](https://tanduna.com/projects/lean-model-lab/roadmap), [native tasks](https://tanduna.com/p/lean-model-lab/tasks). A prepared export or DISCUSSION proposal is not published or accepted work.\n']
    export={'schemaVersion':1,'kind':'publication-ready canonical export; not a submitted native payload','project':plan['project'],'publication':plan['publication'],'objective':plan['objective'],'counts':{'tasks':len(tasks),'waves':len(waves),'dependencyEdges':sum(len(t['dependsOn']) for t in tasks),'releaseHorizons':counts},'waves':waves,'tasks':tasks,'sourceMappings':plan['sourceMappings'],'workflow':{'identity':'Resolve existing records and reconcile returned IDs before retries. Canonical keys are not native task IDs.','creation':'Create authorized native tasks with full outcome/acceptance/source/evidence fields using supported tools; save returned platformId into the canonical ledger.','draft':'Resolve every task/dependency key to returned native IDs before constructing task_plans.save_draft arguments from current documented schema.','submission':'Explicit agreement, passing review and approved exact poll option remain required; DISCUSSION is not acceptance.','verification':'Read public waves, counts, ordering, prerequisites, status and actual versioned access instructions; reconcile partial failures idempotently.'}}
    return {'TASKS.md':'\n'.join(task_lines),'ROADMAP.md':'\n'.join(road),'plan/tanduna-export.json':json.dumps(export,indent=2,ensure_ascii=False)+'\n'}


def generate(root: Path, check: bool=False) -> int:
    plan=json.loads((root/'plan/tasks.json').read_text())
    errors=[]
    for name, content in render(plan).items():
        path=root/name
        if check:
            if not path.exists() or path.read_text()!=content: errors.append(name)
        else: path.write_text(content)
    if errors:
        print('FAIL: generated projection drift: '+', '.join(errors));return 1
    print('PASS: generated projections current' if check else 'Generated TASKS.md, ROADMAP.md and plan/tanduna-export.json')
    return 0


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--check',action='store_true')
    a=p.parse_args();return generate(a.root.resolve(),a.check)

if __name__=='__main__': raise SystemExit(main())
