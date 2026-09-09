#!/usr/bin/env python3
"""Validate canonical plan, immutable source lineage and generated projections.

Standard-library planning checks only; no inference, network or scientific claim.
Self-test fixtures are created exclusively in the selected project's .cache.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
import re
import shutil
import tempfile
from collections import Counter
from pathlib import Path
from generate_plan import render

ROOT=Path(__file__).resolve().parents[1]
PREFIX='lean-model-lab:'
FOUNDATION={'LM-F01','LM-F02','LM-F03'}
STATUSES={'PLANNED','IN PROGRESS','IMPLEMENTED','AUTOMATED PASS','RUNTIME VERIFIED','USER VALIDATED','RELEASE VERIFIED','BLOCKED','FAILED','NOT TESTED','DONE'}
LEVELS=STATUSES-{'PLANNED','IN PROGRESS','BLOCKED'}
HORIZONS={'foundation':0,'0.1':1,'0.2':2,'0.3':3,'0.4':4,
          'later 0.x':5,'1.0':6,'long-term':7,'exploratory':8}
OWNER_REFERENCES={'owner-launch:2026-09-07:section-5','owner-scope:2026-09-08:0.4',
                  'owner-mission:2026-09-08:research',
                  'owner-v1:2026-09-08:tanduna-v1-research-20260908-lean-model-lab'}
LINEAGE_HASHES={
'plan/lineage/821c6364/plan/tasks.json':'54104c7ff63e39fa48ce25f40b5c328ea5bbbf37e8feaca7ce14910468b203d2',
'plan/lineage/821c6364/ROADMAP.md':'977e4eedfb516cbd4a11c9f99d77be310cace35c6e81c3a3641c0b1542ff8319',
'plan/lineage/821c6364/TASKS.md':'86c3eac0ac2d00c13f76a76068b366c024a06d748976693b99cfe78d053908cb',
'plan/lineage/821c6364/STATUS.md':'2d7d2af19a700defae461e43f949d17a71877086a572ad41f3807f7582fbe2f0',
'plan/lineage/821c6364/tools/validate_plan.py':'af55569acbcf971eb72f1c69efe807bfe4b3f5a535aea24213a4f1a1fe1d37ad'}


def text(value): return isinstance(value,str) and bool(value.strip())
def strings(value): return isinstance(value,list) and all(text(v) for v in value)
def normalize(value): return re.sub(r'\W+',' ',value.lower()).strip()


def validate_plan(plan: object, original: dict) -> list[str]:
    errors=[]
    if not isinstance(plan,dict): return ['plan top level must be an object']
    if plan.get('project')!='lean-model-lab':errors.append('project must be lean-model-lab')
    if plan.get('schemaVersion')!=3:errors.append('schemaVersion must be 3')
    if plan.get('stateAuthority')!='plan/tasks.json':errors.append('canonical state authority must be plan/tasks.json')
    tasks=plan.get('tasks');waves=plan.get('waves');mappings=plan.get('sourceMappings')
    if not isinstance(tasks,list) or not all(isinstance(t,dict) for t in tasks):return errors+['tasks must be a list of objects']
    if not 200<=len(tasks)<=400:errors.append('active task count must be 200–400')
    if not isinstance(waves,list) or not all(isinstance(w,dict) for w in waves):return errors+['waves must be a list of objects']
    if not 20<=len(waves)<=32:errors.append('wave count must be 20–32 for native publication')
    if not isinstance(mappings,list) or not all(isinstance(m,dict) for m in mappings):return errors+['sourceMappings must be a list of objects']
    malformed=False
    for i,t in enumerate(tasks):
        name=t.get('id',f'tasks[{i}]')
        for field in ['id','key','title','outcome','featureArea','targetRelease','acceptance','requirementClass','riskEvidenceNeeds','status','evidenceLevel']:
            if not text(t.get(field)):errors.append(f'{name}.{field} must be a non-empty string');malformed=True
        if type(t.get('wave')) is not int or t['wave']<0:errors.append(f'{name}.wave must be a non-negative integer, not boolean');malformed=True
        for field in ['dependsOn','sourceRefs','ownedPaths']:
            if not strings(t.get(field)):errors.append(f'{name}.{field} must be a string list');malformed=True
        if not isinstance(t.get('prerequisiteCoverage'),dict):errors.append(f'{name}.prerequisiteCoverage must be an object');malformed=True
        if 'boundedSuccessorOf' in t:
            if not strings(t['boundedSuccessorOf']) or not t['boundedSuccessorOf']:errors.append(f'{name}.boundedSuccessorOf must be a non-empty string list');malformed=True
            if not text(t.get('scopeBoundary')):errors.append(f'{name}.scopeBoundary must explain the bounded successor');malformed=True
        if not isinstance(t.get('evidence'),list) or not all(isinstance(e,dict) and all(text(e.get(f)) for f in ['level','reference','scope']) for e in t['evidence']):errors.append(f'{name}.evidence must contain level/reference/scope records');malformed=True
    for w in waves:
        if type(w.get('id')) is not int or w['id']<0:errors.append('wave id must be a non-negative integer');malformed=True
        for f in ['name','outcome','exitEvidence','targetRelease']:
            if not text(w.get(f)):errors.append(f'wave {f} must be non-empty');malformed=True
        for f in ['entryDependencies','taskIds']:
            if not strings(w.get(f)):errors.append(f'wave {f} must be a string list');malformed=True
    for m in mappings:
        if not text(m.get('sourceId')):errors.append('mapping sourceId must be a non-empty string');malformed=True
        if not strings(m.get('successorIds')):errors.append('mapping successorIds must be a string list');malformed=True
    if malformed:return errors
    ids=[t['id'] for t in tasks];byid={t['id']:t for t in tasks};position={k:i for i,k in enumerate(ids)}
    for field in ['id','key','title','outcome']:
        repeated=[k for k,v in Counter(normalize(t[field]) for t in tasks).items() if v>1]
        if repeated:errors.append('duplicate '+field+': '+', '.join(repeated))
    for t in tasks:
        k=t['id']
        if t['key']!=PREFIX+k:errors.append(k+': invalid project-scoped key')
        if t['status'] not in STATUSES:errors.append(k+': unsupported status')
        if t['evidenceLevel'] not in LEVELS:errors.append(k+': unsupported evidence level')
        if t['targetRelease'] not in HORIZONS:errors.append(k+': unsupported release horizon')
        if not t['sourceRefs']:errors.append(k+': orphan task without source references')
        if len(set(t['dependsOn']))!=len(t['dependsOn']):errors.append(k+': duplicate prerequisite')
        if set(t['prerequisiteCoverage'])!=set(t['dependsOn']) or not all(text(v) for v in t['prerequisiteCoverage'].values()):errors.append(k+': missing prerequisite outcome coverage')
        if t['status'] not in {'PLANNED','IN PROGRESS','BLOCKED','NOT TESTED','FAILED'} and not t['evidence']:errors.append(k+': completion status requires evidence')
        if t['evidenceLevel'] not in {'NOT TESTED','FAILED'} and not any(e['level']==t['evidenceLevel'] for e in t['evidence']):errors.append(k+': claimed evidence level lacks matching evidence')
        if t['status']=='DONE' and k not in FOUNDATION:errors.append(k+': new work must use specific evidence levels, not historical DONE')
        if t['targetRelease']=='exploratory' and t['requirementClass']!='exploratory proposal':errors.append(k+': exploratory scope must be labeled proposal')
        if t.get('platformId') is not None and (not text(t.get('platformId')) or not text(t.get('platformEvidence'))):errors.append(k+': native platform ID requires read-back evidence')
        for predecessor in t.get('boundedSuccessorOf',[]):
            if predecessor not in byid:errors.append(k+': unknown bounded-scope predecessor '+predecessor)
            elif predecessor==k:errors.append(k+': bounded successor cannot refer to itself')
        for d in t['dependsOn']:
            if d not in byid:errors.append(k+': unknown dependency '+d);continue
            p=byid[d]
            if position[d]>=position[k]:errors.append(k+': prerequisite ordering violation '+d)
            if p['wave']>t['wave']:errors.append(k+': later-wave dependency '+d)
            if HORIZONS.get(p['targetRelease'],99)>HORIZONS.get(t['targetRelease'],99):errors.append(k+': later-release dependency '+d)
    visiting=set();visited=set()
    def visit(k):
        if k in visiting:errors.append('dependency cycle at '+k);return
        if k in visited:return
        visiting.add(k)
        for d in byid[k]['dependsOn']:
            if d in byid:visit(d)
        visiting.remove(k);visited.add(k)
    for k in byid:visit(k)
    reachable=set(FOUNDATION)
    for t in tasks:
        if any(d in reachable for d in t['dependsOn']):reachable.add(t['id'])
    for t in tasks:
        if t['id'] not in reachable:errors.append(t['id']+': orphan task disconnected from foundation')
    if [w['id'] for w in waves]!=sorted(set(w['id'] for w in waves)):errors.append('wave IDs must be unique and ordered')
    assigned=[]
    for w in waves:
        if len(w['name'])>80:errors.append('native wave name exceeds 80 characters')
        if not w['taskIds']:errors.append('orphan empty wave')
        assigned.extend(w['taskIds'])
        for k in w['taskIds']:
            if k not in byid:errors.append('wave has unknown task '+k);continue
            if byid[k]['wave']!=w['id']:errors.append(k+': wave assignment mismatch')
            if byid[k]['targetRelease']!=w['targetRelease']:errors.append(k+': wave release mismatch')
        for d in w['entryDependencies']:
            if d not in byid:errors.append('unknown wave entry dependency '+d)
            elif byid[d]['wave']>=w['id']:errors.append('wave entry requires prior-wave outcome')
        roots=[byid[k] for k in w['taskIds'] if k in byid and not any(d in w['taskIds'] for d in byid[k]['dependsOn'])]
        for t in roots:
            if not set(w['entryDependencies'])<=set(t['dependsOn']):errors.append(t['id']+': wave entry prerequisite coverage missing')
    if Counter(assigned)!=Counter(ids):errors.append('orphan or multiply assigned tasks in waves')
    originals={t['id']:t for t in original['tasks']}
    if Counter(m.get('sourceId') for m in mappings)!=Counter(originals.keys()):errors.append('source mapping coverage must preserve all 27 unique originals')
    for m in mappings:
        sid=m.get('sourceId');old=originals.get(sid)
        if old is None:continue
        expected={'sourceKey':PREFIX+sid,'sourceStatus':old['status'],'sourceAcceptance':old['acceptance'],'structuredPrerequisites':old['dependsOn'],'textualPrerequisites':[],'sourceRevision':original['contractVersion'],'sourcePlatformId':None,'frozenPredecessor':None}
        for field,value in expected.items():
            if m.get(field)!=value:errors.append(sid+': source mapping changed immutable '+field)
        if not text(m.get('reason')) or m.get('treatment') not in {'retained','expanded','split','merged','deferred','superseded','split and expanded','deferred and expanded'}:errors.append(sid+': mapping needs explicit treatment and reason')
        successors=m.get('successorIds')
        if not strings(successors) or not successors:errors.append(sid+': missing successor mappings');continue
        if len(successors)!=len(set(successors)):errors.append(sid+': duplicate successor mapping')
        for k in successors:
            if k not in byid:errors.append(sid+': unknown successor '+k)
            elif PREFIX+sid not in byid[k]['sourceRefs']:errors.append(sid+': successor lacks source reference '+k)
    mapping_byid={m.get('sourceId'):m for m in mappings}
    for t in tasks:
        for ref in t['sourceRefs']:
            if ref.startswith(PREFIX):
                sid=ref[len(PREFIX):]
                if sid not in mapping_byid or t['id'] not in mapping_byid[sid].get('successorIds',[]):errors.append(t['id']+': source reference lacks reciprocal mapping')
            elif ref not in OWNER_REFERENCES:errors.append(t['id']+': unknown source reference '+ref)
    for fid in FOUNDATION:
        t=byid.get(fid)
        if t is None:errors.append('missing retained foundation '+fid);continue
        for field,value in originals[fid].items():
            if t.get(field)!=value:errors.append(fid+': accepted foundation changed '+field)
    pub=plan.get('publication')
    if not isinstance(pub,dict):errors.append('publication metadata required')
    elif pub.get('status')=='RELEASE VERIFIED':
        if not pub.get('nativePlanId') or not pub.get('readbackEvidence'):errors.append('native publication completion requires read-back evidence')
    delivery=plan.get('v1Delivery')
    if delivery is not None:
        dispatch='tanduna-v1-research-20260908-lean-model-lab'
        if not isinstance(delivery,dict) or delivery.get('dispatchIdentifier')!=dispatch:
            errors.append('v1 delivery must name the exact owner dispatch')
        packets=plan.get('executionPackets',[])
        if not isinstance(packets,list) or sum(isinstance(p,dict) and p.get('id')==dispatch for p in packets)!=1:
            errors.append('v1 owner dispatch must have exactly one execution packet')
        snapshots=plan.get('supersededScopes',[])
        if not isinstance(snapshots,list):errors.append('superseded scopes must be a list')
        else:
            for snapshot in snapshots:
                if not isinstance(snapshot,dict):errors.append('superseded scope must be an object');continue
                objects=snapshot.get('taskObjects')
                if not isinstance(objects,list):errors.append('superseded task objects must be a list');continue
                digest=hashlib.sha256(json.dumps(objects,sort_keys=True,separators=(',',':')).encode()).hexdigest()
                if digest!=snapshot.get('taskObjectsSha256'):errors.append('superseded task object digest mismatch')
    return errors


def validate_repository(root: Path) -> list[str]:
    errors=[]
    for name,digest in LINEAGE_HASHES.items():
        try:
            if hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest:errors.append('immutable lineage digest mismatch: '+name)
        except OSError:errors.append('missing immutable lineage: '+name)
    # Never interpret a modified source snapshot as the historical authority.
    if errors:return errors
    try:
        original=json.loads((root/'plan/lineage/821c6364/plan/tasks.json').read_text())
        plan=json.loads((root/'plan/tasks.json').read_text())
    except (OSError,ValueError) as e:return errors+['cannot parse plan: '+str(e)]
    if len(original['tasks'])!=27 or sum(len(t['dependsOn']) for t in original['tasks'])!=71:errors.append('immutable lineage must retain 27 objects and 71 edges')
    errors.extend(validate_plan(plan,original))
    if isinstance(plan,dict):
        if plan.get('lineage',{}).get('files')!=LINEAGE_HASHES:errors.append('canonical lineage digest registry changed')
        try:
            projections=render(plan)
        except (KeyError,TypeError,ValueError,AttributeError):projections={}
        for name,expected in projections.items():
            try:
                if (root/name).read_text()!=expected:errors.append('generated projection drift: '+name)
            except OSError:errors.append('missing generated projection: '+name)
        if isinstance(plan.get('tasks'),list):
            readme=root/'README.md'
            if readme.exists():
                count=re.search(r'\[(\d+) contributor tasks\]\(TASKS.md\)',readme.read_text())
                if count and int(count.group(1))!=len(plan['tasks']):errors.append('README contributor-task count differs from canonical plan')
    return errors


def run_self_test(root: Path) -> int:
    baseline=validate_repository(root)
    if baseline:
        print('SELF-TEST FAIL: invalid baseline');print('\n'.join(baseline));return 1
    plan=json.loads((root/'plan/tasks.json').read_text());original=json.loads((root/'plan/lineage/821c6364/plan/tasks.json').read_text())
    cases=[]
    def case(name,mutate,expected):cases.append((name,mutate,expected))
    case('wrong project',lambda p:p.update(project='sibling'),'project must')
    case('boolean wave',lambda p:p['tasks'][3].update(wave=True),'not boolean')
    case('malformed dependency',lambda p:p['tasks'][3].update(dependsOn=[9]),'string list')
    case('duplicate outcome',lambda p:p['tasks'][4].update(outcome=p['tasks'][3]['outcome']),'duplicate outcome')
    case('dangling dependency',lambda p:p['tasks'][3]['dependsOn'].append('LM-MISSING'),'unknown dependency')
    case('cycle',lambda p:p['tasks'][3]['dependsOn'].append(p['tasks'][4]['id']),'dependency cycle')
    case('later horizon',lambda p:p['tasks'][3]['dependsOn'].append('LM-W27-T08'),'later-release dependency')
    case('dependency coverage',lambda p:p['tasks'][3].update(prerequisiteCoverage={}),'prerequisite outcome coverage')
    case('missing mapping',lambda p:p['sourceMappings'].pop(),'source mapping coverage')
    case('malformed mapping',lambda p:p['sourceMappings'][0].update(sourceId=[]),'mapping sourceId')
    case('changed original acceptance',lambda p:p['sourceMappings'][3].update(sourceAcceptance='weakened'),'immutable sourceAcceptance')
    case('changed historical edge',lambda p:p['sourceMappings'][9].update(structuredPrerequisites=[]),'immutable structuredPrerequisites')
    case('missing source backlink',lambda p:p['tasks'][3].update(sourceRefs=[]),'successor lacks source reference')
    case('unrecognized owner directive',lambda p:p['tasks'][3]['sourceRefs'].append('owner-mission:unverified'),'unknown source reference')
    if plan.get('v1Delivery'):
        case('changed v1 dispatch',lambda p:p['v1Delivery'].update(dispatchIdentifier='unverified'),'exact owner dispatch')
        case('duplicate v1 dispatch',lambda p:p['executionPackets'].append(copy.deepcopy(p['executionPackets'][-1])),'exactly one execution packet')
        case('changed superseded scope',lambda p:p['supersededScopes'][0]['taskObjects'][0].update(acceptance='weakened'),'superseded task object digest mismatch')
    case('orphan task',lambda p:p['tasks'][3].update(dependsOn=[]),'disconnected from foundation')
    case('orphan wave assignment',lambda p:p['waves'][1]['taskIds'].pop(),'orphan or multiply assigned')
    case('release scope mismatch',lambda p:p['waves'][1].update(targetRelease='long-term'),'wave release mismatch')
    case('false runtime proof',lambda p:p['tasks'][3].update(status='RUNTIME VERIFIED',evidenceLevel='RUNTIME VERIFIED',evidence=[]),'completion status requires evidence')
    case('fake native ID',lambda p:p['tasks'][3].update(platformId='invented'),'native platform ID requires')
    case('reopen accepted foundation',lambda p:p['tasks'][0].update(status='PLANNED'),'accepted foundation changed status')
    case('oversized native wave',lambda p:p['waves'][1].update(name='x'*81),'exceeds 80')
    case('unsupported explicit horizon',lambda p:p['tasks'][3].update(targetRelease='0.5'),'unsupported release horizon')
    # Exercise explicit horizons without assuming a fixed expanded task count.
    def earlier_successor_with_later_dependency(p):
        successor=next(t for t in p['tasks'] if t['id'] not in FOUNDATION)
        prerequisite=next(t for t in reversed(p['tasks']) if t['id']!=successor['id'])
        successor['targetRelease']='0.2';prerequisite['targetRelease']='0.4'
        successor['dependsOn'].append(prerequisite['id'])
    case('explicit 0.4 prerequisite of 0.2',earlier_successor_with_later_dependency,'later-release dependency')
    case('undersized task population',lambda p:p.update(tasks=p['tasks'][:199]),'active task count must')
    case('oversized task population',lambda p:p.update(tasks=p['tasks']+[copy.deepcopy(p['tasks'][-1]) for _ in range(401-len(p['tasks']))]),'active task count must')
    failures=[]
    for name,mutate,expected in cases:
        candidate=copy.deepcopy(plan);mutate(candidate);found=validate_plan(candidate,original)
        if not any(expected in e for e in found):failures.append(name+': missing '+expected)
    negative_controls=len(cases)
    if validate_plan([],original)!=['plan top level must be an object']:failures.append('non-object plan')
    negative_controls+=1
    # Exercise file-level drift and immutable-byte tampering in project-scoped fixtures.
    cache=root/'.cache';cache.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='plan-selftest-',dir=cache) as raw:
        fixture=Path(raw)
        for name in [*LINEAGE_HASHES,'plan/tasks.json','TASKS.md','ROADMAP.md','plan/tanduna-export.json']:
            target=fixture/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(root/name,target)
        for name in ['TASKS.md','ROADMAP.md','plan/tanduna-export.json']:
            path=fixture/name;before=path.read_text();path.write_text(before+'\nDRIFT\n')
            if 'generated projection drift: '+name not in validate_repository(fixture):failures.append('projection drift '+name)
            negative_controls+=1
            path.write_text(before)
        path=fixture/'plan/lineage/821c6364/ROADMAP.md';path.write_text(path.read_text()+'\nchanged\n')
        if not any('immutable lineage digest mismatch' in e for e in validate_repository(fixture)):failures.append('immutable byte tampering')
        negative_controls+=1
    if failures:print('SELF-TEST FAIL: '+'; '.join(failures));return 1
    print(f'SELF-TEST PASS: {negative_controls} negative controls; accepted DONE baseline preserved; fixtures project-scoped')
    return 0


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=ROOT);parser.add_argument('--self-test',action='store_true')
    args=parser.parse_args();root=args.root.resolve()
    if args.self_test:return run_self_test(root)
    errors=validate_repository(root)
    if errors:print(f'FAIL: {len(errors)} errors\n'+'\n'.join('- '+e for e in errors));return 1
    p=json.loads((root/'plan/tasks.json').read_text())
    print(f"PASS: {len(p['tasks'])} tasks, {len(p['waves'])} waves, {sum(len(t['dependsOn']) for t in p['tasks'])} dependency edges; 27/71 immutable lineage; generated views/export consistent")
    return 0

if __name__=='__main__':raise SystemExit(main())
