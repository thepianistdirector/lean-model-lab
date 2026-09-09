"""Recompute descriptive tables and standalone figures from retained native evidence.

Pass an explicit evidence manifest and a NEW output directory. No inference, simulation, private workspace constants or source editing is required.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
import os
import statistics
import time

import argparse
parser = argparse.ArgumentParser(description="Reanalyse exported Lean Model Lab quality evidence without model loading or source edits.")
parser.add_argument('--evidence-manifest', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True, help='New output directory; existing paths are refused.')
args = parser.parse_args()
MANIFEST_PATH = args.evidence_manifest.resolve()
MANIFEST = json.loads(MANIFEST_PATH.read_text())
if MANIFEST.get('schema_version') != 1:
    raise ValueError('evidence manifest schema_version must be 1')
ENTRIES = {entry['id']:entry for entry in MANIFEST['studies']}
if len(ENTRIES) != len(MANIFEST['studies']):
    raise ValueError('study IDs must be unique')
required = {'14b','legacy-comparison','legacy-protocol-failure','development'}
if not required.issubset(ENTRIES):
    raise ValueError('manifest must include the four retained quality benchmark roles')
if set(ENTRIES) - (required | {'confirmation-14b'}):
    raise ValueError('unrecognized study role; supply known roles with configurable paths')
def resolve_entry(value):
    path = Path(value)
    return path.resolve() if path.is_absolute() else (MANIFEST_PATH.parent/path).resolve()
STUDIES = {name:resolve_entry(entry['study']) for name,entry in ENTRIES.items()}
REPORTS = {name:resolve_entry(entry['report']) for name,entry in ENTRIES.items()}
AUDITS = {name:resolve_entry(entry['raw_audit']) for name,entry in ENTRIES.items()}
for name in ENTRIES:
    for path in [STUDIES[name]/'config.json', STUDIES[name]/'workload.json', REPORTS[name], AUDITS[name]]:
        if not path.is_file():
            raise ValueError(f'missing manifest source: {name}: {path}')
OUT = args.output.resolve()
if any(OUT.is_relative_to(source) for source in STUDIES.values()):
    raise ValueError('output cannot be inside an input evidence study')
if OUT.exists():
    raise ValueError('output directory must be new; retained results cannot be overwritten')
OUT.mkdir(parents=True,exist_ok=False)
CACHE = OUT/'.runtime'
CACHE.mkdir()
REANALYSIS_STARTED_NS = time.monotonic_ns()



def read(path):
    return json.loads(Path(path).read_text())


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def csvwrite(name, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with (OUT / name).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in row.items()})


def correct(request, expected):
    return (request.get('status') == 'SUCCEEDED'
            and request.get('finish_reason') != 'length'
            and request.get('output_text', '').strip() == expected)


def quantiles(values):
    values = sorted(values)
    return {name: values[max(0, math.ceil(p * len(values)) - 1)] if values else None
            for name, p in [('p50', .5), ('p95', .95), ('p99', .99)]}


attempts, requests, pairs, differences, costs, inventories = [], [], [], [], [], []
summaries = {}
for name, source in STUDIES.items():
    report = read(REPORTS[name])
    audit = read(AUDITS[name])
    config = read(source / 'config.json')
    canonical_config = hashlib.sha256(json.dumps(config,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')).hexdigest()
    assert report['config_sha256'] == canonical_config, ('report config binding',name)
    assert audit['config_sha256'] == canonical_config, ('raw-audit config binding',name)
    for field,path in [('report_sha256',REPORTS[name]),('raw_audit_sha256',AUDITS[name])]:
        if ENTRIES[name].get(field):
            assert digest(path)==ENTRIES[name][field], ('manifest hash',name,field)
    if ENTRIES[name].get('producer_archive'):
        producer = resolve_entry(ENTRIES[name]['producer_archive'])
        assert digest(producer)==ENTRIES[name]['producer_archive_sha256'], ('producer archive hash',name)
    workload = read(source / 'workload.json')
    expected = {r['request_id']: r for r in workload['requests']}
    raw = {a['attempt_id']: a for a in (read(p) for p in (source / 'attempts').glob('*.json'))}
    metrics = {a['attempt_id']: a for a in report['attempts']}
    native = {a['attempt_id']: a for a in audit['attempts']}
    for aid, a in raw.items():
        m = metrics[aid]
        observed_correct = sum(correct(r, expected[r['request_id']]['expected']) for r in a['requests'])
        assert observed_correct == m['quality_correct'], (name, aid, observed_correct, m['quality_correct'])
        row = dict(study=name, attempt_id=aid, concurrency=a['concurrency'], pair_index=a['pair_index'],
                   arm=a['arm'], status=a['status'], observed=len(a['requests']), offered=len(expected),
                   correct=observed_correct, accuracy=observed_correct/len(expected),
                   service_s=m['service_ns']/1e9, full_attempt_s=m['full_wall_ns']/1e9,
                   throughput_requests_s=m['successful_requests_per_second'],
                   output_tokens_s=m['successful_output_tokens_per_second'],
                   server_hwm_bytes=a['environment']['memory']['value'],
                   load_averages=a['environment']['load']['value'],
                   newly_evaluated_input_tokens=native[aid]['new_input_tokens'],
                   reused_input_tokens=native[aid]['reused_input_tokens'],
                   generated_tokens=native[aid]['generated_tokens'], eligible=m['eligible'],
                   ineligibility=m['ineligibility_reasons'],
                   slo_qualified=m.get('serving', {}).get('slo_qualified_requests'))
        resource_path = source / 'raw' / aid / 'resource-observations.json'
        resource = read(resource_path) if resource_path.exists() else {}
        row['sampled_server_plus_coordinator_peak_bytes'] = resource.get('maximum_observed_aggregate_rss_bytes')
        row['cpu_time_s'] = None  # These retained schemas expose no CPU-time counter.
        for key, ns in m['overhead_ns'].items():
            row[key + '_s'] = ns/1e9
        for metric, qs in m['latency'].items():
            for q in ['p50', 'p95', 'p99']:
                row[metric.replace('_ns', '') + '_' + q + '_s'] = qs[q]/1e9 if qs[q] is not None else None
        for r in a['requests']:
            wr = expected[r['request_id']]
            rr = dict(study=name, attempt_id=aid, concurrency=a['concurrency'], pair_index=a['pair_index'],
                      arm=a['arm'], request_id=r['request_id'], stratum=wr['stratum'], expected=wr['expected'],
                      status=r['status'], finish_reason=r.get('finish_reason'), output_text=r.get('output_text'),
                      output_token_ids=r.get('output_token_ids'), correct=correct(r, wr['expected']),
                      prompt_tokens=r.get('prompt_tokens'), generated_tokens=r.get('generated_tokens'))
            for label, end, start in [('arrival_to_completion_s','completed_ns','arrival_ns'),
                                      ('arrival_to_first_token_s','first_token_ns','arrival_ns'),
                                      ('dispatch_to_completion_s','completed_ns','dispatch_ns'),
                                      ('queue_s','admitted_ns','arrival_ns')]:
                rr[label] = (r[end]-r[start])/1e9 if r.get(end) is not None and r.get(start) is not None else None
            requests.append(rr)
        dispatch = [r['dispatch_to_completion_s'] for r in requests if r['attempt_id'] == aid and r['dispatch_to_completion_s'] is not None]
        row.update({'dispatch_to_completion_'+q+'_s': v for q, v in quantiles(dispatch).items()})
        attempts.append(row)
    for c, group in report['concurrency_groups'].items():
        for p in group['pairs']:
            ba, ca = raw[p['baseline_attempt_id']], raw[p['candidate_attempt_id']]
            br = {r['request_id']: r for r in ba['requests']}
            cr = {r['request_id']: r for r in ca['requests']}
            transitions = {'correct_correct': 0, 'correct_wrong': 0, 'wrong_correct': 0, 'wrong_wrong': 0}
            mismatch = []
            for rid in expected:
                b, c_req = br.get(rid, {}), cr.get(rid, {})
                bc, cc = correct(b, expected[rid]['expected']), correct(c_req, expected[rid]['expected'])
                transition = ('correct' if bc else 'wrong') + '_' + ('correct' if cc else 'wrong')
                transitions[transition] += 1
                if b.get('output_token_ids') != c_req.get('output_token_ids'):
                    mismatch.append(rid)
                    differences.append(dict(study=name, concurrency=int(c), pair_index=p['pair_index'],request_id=rid,
                                            expected=expected[rid]['expected'], transition=transition,
                                            baseline_output=b.get('output_text'), candidate_output=c_req.get('output_text'),
                                            baseline_tokens=b.get('output_token_ids'), candidate_tokens=c_req.get('output_token_ids')))
            assert mismatch == p['token_mismatch_request_ids'], (name, mismatch, p['token_mismatch_request_ids'])
            bm, cm = metrics[ba['attempt_id']], metrics[ca['attempt_id']]
            eligible = report['eligible'] and p['eligible']
            pairs.append(dict(study=name, concurrency=int(c), pair_index=p['pair_index'],
                              order='AB' if ba['started_ns'] < ca['started_ns'] else 'BA', eligible=eligible,
                              baseline_attempt_id=ba['attempt_id'],candidate_attempt_id=ca['attempt_id'],
                              **transitions, token_mismatches=len(mismatch), token_mismatch_ids=mismatch,
                              service_throughput_ratio=p['throughput_candidate_over_baseline'],
                              full_attempt_efficiency_ratio=bm['full_wall_ns']/cm['full_wall_ns'] if eligible else None,
                              e2e_p95_ratio=p['end_to_end_tail_candidate_over_baseline']['p95'],
                              e2e_p99_ratio=p['end_to_end_tail_candidate_over_baseline']['p99'],
                              ttft_p95_ratio=p['ttft_tail_candidate_over_baseline']['p95'],
                              ttft_p99_ratio=p['ttft_tail_candidate_over_baseline']['p99']))
    setup = report['accounting']['setup_acquisition_build_costs']
    for i, rec in enumerate(setup.get('records', [])):
        costs.append(dict(study=name, kind='inherited_or_current_setup', record_index=i,
                          phase=rec['phase'], status=rec['status'], clock_boot_id=config['clock']['boot_id'], start_ns=rec['started_ns'],
                          finish_ns=rec['finished_ns'], duration_s=(rec['finished_ns']-rec['started_ns'])/1e9,
                          bytes_acquired=rec.get('bytes_acquired'), details=rec.get('details')))
    for a in raw.values():
        costs.append(dict(study=name,kind='native_attempt',record_index=a['attempt_id'],phase='attempt',
                          status=a['status'],clock_boot_id=config['clock']['boot_id'],start_ns=a['started_ns'],finish_ns=a['finished_ns'],
                          duration_s=(a['finished_ns']-a['started_ns'])/1e9,details=a['arm']))
    summaries[name] = dict(source=ENTRIES[name]['study'], config=config, audit_status=audit['status'],
                           auditor_sha256=audit['auditor_sha256'], eligible=report['eligible'],
                           ineligibility=report['ineligibility_reasons'], accounting=report['accounting'],
                           correct=sum(a['quality_correct'] for a in metrics.values()),
                           offered=sum(a['expected_requests'] for a in metrics.values()),
                           observations=sum(len(a['requests']) for a in raw.values()))
    for path in sorted(source.rglob('*')):
        if path.is_file():
            inventories.append(dict(study=name,path=os.path.relpath(path,MANIFEST_PATH.parent),bytes=path.stat().st_size,sha256=digest(path)))

attempts.sort(key=lambda r:(r['study'],r['concurrency'],r['pair_index'],r['arm'],r['attempt_id']))
requests.sort(key=lambda r:(r['study'],r['concurrency'],r['pair_index'],r['arm'],r['request_id'],r['attempt_id']))
pairs.sort(key=lambda r:(r['study'],r['concurrency'],r['pair_index']))
differences.sort(key=lambda r:(r['study'],r['concurrency'],r['pair_index'],r['request_id']))
costs.sort(key=lambda r:(r['clock_boot_id'],r['start_ns'],r['finish_ns'],r['study'],str(r['record_index'])))
inventories.sort(key=lambda r:(r['study'],r['path']))
dedup = {}
for row in costs:
    # A predecessor attempt can appear as a setup record in a later study.
    key = (row['clock_boot_id'], row['start_ns'], row['finish_ns'])
    dedup.setdefault(key, {'clock_boot_id':key[0], 'start_ns':key[1], 'finish_ns':key[2], 'duration_s':row['duration_s'], 'views':[]})['views'].append(row)
intervals = sorted((key[1],key[2]) for key in dedup)
union = []
for start, end in intervals:
    if union and start <= union[-1][1]:
        union[-1][1] = max(union[-1][1], end)
    else:
        union.append([start,end])
producer_boots={s['config']['clock']['boot_id'] for s in summaries.values()}
cost_context = dict(reanalysis_started_monotonic_ns=REANALYSIS_STARTED_NS,
                    reanalysis_elapsed_s=(time.monotonic_ns()-REANALYSIS_STARTED_NS)/1e9,
                    producer_accounting={name:s['accounting']['full_cost_accounting'] for name,s in summaries.items()},
                    scope='Producer clock cutoffs remain frozen. Current reanalysis-host monotonic time never extends a historical allocation. No all-allocation savings ratio.',
                    unique_supplied_interval_union_s=sum(e-s for s,e in union)/1e9 if len(producer_boots)==1 else None,
                    union_scope='Union of supplied intervals only on one recorded boot; unavailable across distinct boot clocks; not complete campaign total.',
                    producer_boot_count=len(producer_boots), energy='UNAVAILABLE; no sensor', money='UNAVAILABLE; no monetary probe')
if 'confirmation-14b' in STUDIES:
    original_workload=read(STUDIES['14b']/'workload.json')
    new_workload=read(STUDIES['confirmation-14b']/'workload.json')
    old_prompts={r['prompt'] for r in original_workload['requests']}
    new_prompts={r['prompt'] for r in new_workload['requests']}
    write('split-audit.json', {'historical_seed':original_workload['generator_seed'], 'confirmation_seed':new_workload['generator_seed'], 'exact_full_prompt_overlap_count':len(old_prompts & new_prompts), 'confirmation_unique_full_prompt_count':len(new_prompts), 'scope':'Full prompt identity versus historical128-request measurement population; fixed shared filler prefixes and grammar remain intentional. No overlap-driven resampling.'})
write('summary.json', summaries)
write('tables.json', dict(attempts=attempts,pairs=pairs,output_differences=differences,cost_context=cost_context))
if 'confirmation-14b' in STUDIES:
    confirmation_pairs=[p for p in pairs if p['study']=='confirmation-14b']
    confirmation_gate={'status':'PASS' if len(confirmation_pairs)==2 and all(p['eligible'] and p['service_throughput_ratio']>=1.05 and p['full_attempt_efficiency_ratio']>=1.05 and all(p[m] is not None and p[m]<=1.10 for m in ['e2e_p95_ratio','e2e_p99_ratio','ttft_p95_ratio','ttft_p99_ratio']) for p in confirmation_pairs) else 'FAIL_OR_INCOMPLETE', 'native_v2_eligible':summaries['confirmation-14b']['eligible'], 'full_attempt_gate':'Prospectively declared external protocol requirement in addition to native v2 service criterion.', 'required_pairs':2, 'observed_pairs':len(confirmation_pairs), 'observed_requests':summaries['confirmation-14b']['observations'], 'offered_requests':summaries['confirmation-14b']['offered'], 'service_practical_threshold_ratio':1.05,'full_attempt_practical_threshold_ratio':1.05,'maximum_tail_ratio':1.10,'slo_goodput_separate':True}
    write('confirmation-gate.json',confirmation_gate)
write('source-inventory.json', inventories)
write('deduplicated-cost-ledger.json', list(dedup.values()))
for name, rows in [('attempts.csv',attempts),('requests.csv',requests),('pairs.csv',pairs),
                   ('output-differences.csv',differences),('cost-ledger.csv',costs)]:
    csvwrite(name,rows)
write('cost-context.json',cost_context)

os.environ['MPLCONFIGDIR'] = str((CACHE/'mpl').resolve())
os.environ['TMPDIR'] = str((CACHE/'tmp').resolve())
(CACHE/'mpl').mkdir(exist_ok=True)
(CACHE/'tmp').mkdir(exist_ok=True)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                     'axes.spines.right':False,'axes.titleweight':'bold','figure.facecolor':'white',
                     'svg.hashsalt':'lean-model-lab-quality-heldout14b-20260908'})
BLUE, GOLD, INK = '#2563a6', '#bf861a', '#303640'
figdir=OUT/'figures';figdir.mkdir(exist_ok=True)
def save(fig,name):
    fig.savefig(figdir/(name+'.png'),dpi=180,bbox_inches='tight')
    fig.savefig(figdir/(name+'.svg'),bbox_inches='tight',metadata={'Date':None})
    fig.savefig(figdir/(name+'.pdf'),bbox_inches='tight',metadata={'CreationDate':None,'ModDate':None})
    plt.close(fig)

fig, ax = plt.subplots(figsize=(9,5.6),layout='constrained')
groups=[('Historical 0.5B · C1','legacy-comparison',1),('Historical 0.5B · C4','legacy-comparison',4),
        ('Historical 14B · C1','14b',1),('Historical 14B · C4','14b',4),('New 0.5B development · C1','development',1),('Held-out 14B · C4','confirmation-14b',4)]
groups=[g for g in groups if g[1] in STUDIES]
for i,(label, study,c) in enumerate(groups):
    rows=[a for a in attempts if a['study']==study and a['concurrency']==c]
    for j,arm in enumerate(['baseline','candidate']):
        arm_rows=[a for a in rows if a['arm']==arm]
        if not arm_rows:
            continue
        val=min(a['accuracy'] for a in arm_rows)*100
        ax.barh(i+(j-.5)*.30,val,height=.27,color=BLUE if j==0 else 'white',edgecolor=BLUE,hatch=None if j==0 else '///',label=arm if i==0 else None)
    ax.text(min(val+1,101),i,f'{val:.2f}%',va='center',color=INK)
ax.axvline(95,color=INK,linestyle='--',label='Frozen 95% quality gate')
ax.set(yticks=range(len(groups)),yticklabels=[g[0] for g in groups],xlim=(0,112),xlabel='Minimum arm accuracy across repetitions (%)')
ax.invert_yaxis();ax.legend(loc='upper center',bbox_to_anchor=(.5,-.15),ncols=3,fontsize=8)
fig.suptitle('Minimum arm quality by retained study and concurrency',x=.02,ha='left')
ax.set_title('128 requests per historical/confirmation arm; 8 per development arm. Settings differ across studies.',fontsize=9,loc='left',fontweight='normal')
save(fig,'quality-gates')

panels=[item for item in [('14b',1,'Retained main · C1'),('14b',4,'Retained main · C4'),('confirmation-14b',4,'New held-out · C4')] if item[0] in STUDIES]
fig, axes=plt.subplots(1,len(panels),figsize=(4*len(panels),4),layout='constrained',sharey=True)
for ax,(study,c,title) in zip(axes,panels):
    ps=[p for p in pairs if p['study']==study and p['concurrency']==c]
    service_pairs=[p for p in ps if p['service_throughput_ratio'] is not None]
    ax.scatter([p['pair_index']+1-.055 for p in service_pairs],[p['service_throughput_ratio'] for p in service_pairs],color=BLUE,marker='o',label='Service throughput',s=42)
    full_pairs=[p for p in ps if p['full_attempt_efficiency_ratio'] is not None]
    ax.scatter([p['pair_index']+1+.055 for p in full_pairs],[p['full_attempt_efficiency_ratio'] for p in full_pairs],color=GOLD,marker='s',label='Full-attempt efficiency',s=40)
    if not service_pairs:
        ax.text(.5,.65,'Unavailable: ineligible or incomplete',ha='center',transform=ax.transAxes,fontsize=8)
    ax.axhline(1.05,color=INK,linestyle=':',label='5% practical threshold')
    ax.set(title=title,xlabel='Pair number and execution order',xticks=[p['pair_index']+1 for p in ps],ylim=(0,max(4.5,max(((p['service_throughput_ratio'] or 0) for p in pairs if p['study'] in ['14b','confirmation-14b']), default=0)+.5)))
    ax.set_xticklabels([str(p['pair_index']+1)+'\n'+p['order'] for p in ps])
    ax.grid(axis='y',alpha=.2)
axes[0].set_ylabel('Candidate / baseline (×)')
axes[0].legend(fontsize=8)
fig.suptitle('14B paired service and full-attempt effects\n128 requests per arm; full attempt includes repeated verification and load',fontsize=12)
save(fig,'paired-effects')

fig,axes=plt.subplots(1,len(panels),figsize=(4*len(panels),4.5),layout='constrained')
for ax,(study,c,title) in zip(axes,panels):
    for arm,col,linestyle in [('baseline',BLUE,'-'),('candidate',GOLD,'--')]:
        vals=sorted(r['arrival_to_completion_s'] for r in requests if r['study']==study and r['concurrency']==c and r['arm']==arm)
        ax.plot(vals,[(i+1)/len(vals) for i in range(len(vals))],color=col,linestyle=linestyle,label=arm)
    ax.axvline(30,color=INK,linestyle=':',label='30 s end-to-end SLO')
    ax.set(title=title,xlabel='Arrival to completion (seconds)',ylabel='Empirical fraction',ylim=(0,1),xlim=(0,1300))
    ax.grid(alpha=.15)
axes[0].legend(fontsize=8)
fig.suptitle('14B request latency distributions\nHistorical: 512 observations/arm; held-out: 256/arm. Correlated within simultaneous batches.',fontsize=12)
save(fig,'latency-distributions')

figure_sources={'quality-gates':'attempts.csv','paired-effects':'pairs.csv','latency-distributions':'requests.csv'}
figure_files=[]
for figure_path in sorted(figdir.iterdir()):
    if figure_path.suffix in {'.png','.svg','.pdf'}:
        csv_path=OUT/figure_sources[figure_path.stem]
        figure_files.append({'path':figure_path.relative_to(OUT).as_posix(),'bytes':figure_path.stat().st_size,'sha256':digest(figure_path),'source_csv':csv_path.relative_to(OUT).as_posix(),'source_csv_sha256':digest(csv_path)})
write('figure-source-manifest.json',{'schema_version':1,'relative_path_base':'Analysis output directory containing this manifest.','renderer_script':Path(__file__).name,'renderer_script_sha256':digest(Path(__file__)),'evidence_manifest_sha256':digest(MANIFEST_PATH),'visual_review':'PENDING_SEPARATE_REVIEW_OF_EXPORTED_FILES','files':figure_files})
write('reanalysis-receipt.json', {'status':'COMPLETED_LOCAL_HASH_CONSISTENCY_CHECKS', 'evidence_manifest_sha256':digest(MANIFEST_PATH),'script_sha256':digest(Path(__file__)),'scope':'Checks retained bytes, evaluator agreement and optional producer archive hashes; not producer authentication, external execution or independent human validation.','new_native_requests':0})
print(json.dumps({'attempts':len(attempts),'requests':len(requests),'pairs':len(pairs),'token_differences':differences,'cost_context':cost_context},indent=2))
