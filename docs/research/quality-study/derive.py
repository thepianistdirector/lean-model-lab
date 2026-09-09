"""Recompute descriptive tables and standalone figures from retained native evidence.

Run from the Lean Model Lab source root. No inference, simulation or source mutation.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
import os
import statistics
import time

OUT = Path('docs/research/quality-study')
CACHE = Path('.cache/v1-investigations-20260908/quality')
STUDIES = {
    '14b': Path('.cache/study-14b-main-20260908-01'),
    'legacy-comparison': Path('.cache/public-evidence-0.4-20260908/legacy-comparison/study'),
    'legacy-protocol-failure': Path('.cache/public-evidence-0.4-20260908/legacy-protocol-failure/study'),
    'development': CACHE / 'development-study',
}


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
    report = read(CACHE / name / 'result.json')
    audit = read(CACHE / name / 'raw-audit.json')
    config = read(source / 'config.json')
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
                              e2e_p99_ratio=p['end_to_end_tail_candidate_over_baseline']['p99']))
    setup = report['accounting']['setup_acquisition_build_costs']
    for i, rec in enumerate(setup.get('records', [])):
        costs.append(dict(study=name, kind='inherited_or_current_setup', record_index=i,
                          phase=rec['phase'], status=rec['status'], start_ns=rec['started_ns'],
                          finish_ns=rec['finished_ns'], duration_s=(rec['finished_ns']-rec['started_ns'])/1e9,
                          bytes_acquired=rec.get('bytes_acquired'), details=rec.get('details')))
    for a in raw.values():
        costs.append(dict(study=name,kind='native_attempt',record_index=a['attempt_id'],phase='attempt',
                          status=a['status'],start_ns=a['started_ns'],finish_ns=a['finished_ns'],
                          duration_s=(a['finished_ns']-a['started_ns'])/1e9,details=a['arm']))
    summaries[name] = dict(source=str(source), config=config, audit_status=audit['status'],
                           auditor_sha256=audit['auditor_sha256'], eligible=report['eligible'],
                           ineligibility=report['ineligibility_reasons'], accounting=report['accounting'],
                           correct=sum(a['quality_correct'] for a in metrics.values()),
                           offered=sum(a['expected_requests'] for a in metrics.values()),
                           observations=sum(len(a['requests']) for a in raw.values()))
    for path in sorted(source.rglob('*')):
        if path.is_file():
            inventories.append(dict(study=name,path=str(path),bytes=path.stat().st_size,sha256=digest(path)))

dedup = {}
for row in costs:
    # A predecessor attempt can appear as a setup record in a later study.
    key = (row['start_ns'], row['finish_ns'])
    dedup.setdefault(key, {'start_ns':key[0], 'finish_ns':key[1], 'duration_s':row['duration_s'], 'views':[]})['views'].append(row)
intervals = sorted(dedup)
union = []
for start, end in intervals:
    if union and start <= union[-1][1]:
        union[-1][1] = max(union[-1][1], end)
    else:
        union.append([start,end])
now = time.monotonic_ns()
cost_context = dict(snapshot_monotonic_ns=now, original_allocation_start_ns=267268865220540,
                    original_allocation_deadline_ns=310468865220540,
                    current_allocation_elapsed_s=(now-267268865220540)/1e9,
                    current_allocation_remaining_s=(310468865220540-now)/1e9,
                    scope='Current all-clock includes all investigators/coordinator/idle, not attributable to this finding alone. Historical producer cutoffs remain frozen. Historical pre-allocation0.1 costs are separate and not added to current elapsed.',
                    unique_supplied_interval_union_s=sum(e-s for s,e in union)/1e9,
                    union_scope='Union of supplied ledgers only across both historical and current clocks on this same boot; not complete campaign total.',
                    energy='UNAVAILABLE; no sensor', money='UNAVAILABLE; no monetary probe')
write('summary.json', summaries)
write('tables.json', dict(attempts=attempts,pairs=pairs,output_differences=differences,cost_context=cost_context))
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
                     'axes.spines.right':False,'axes.titleweight':'bold','figure.facecolor':'white'})
BLUE, GOLD, INK = '#2563a6', '#bf861a', '#303640'
figdir=OUT/'figures';figdir.mkdir(exist_ok=True)
def save(fig,name):
    fig.savefig(figdir/(name+'.png'),dpi=180,bbox_inches='tight')
    fig.savefig(figdir/(name+'.svg'),bbox_inches='tight')
    plt.close(fig)

fig, ax = plt.subplots(figsize=(9,4.8),layout='constrained')
groups=[('Historical 0.5B · C1','legacy-comparison',1),('Historical 0.5B · C4','legacy-comparison',4),
        ('Historical 14B · C1','14b',1),('Historical 14B · C4','14b',4),('New 0.5B development · C1','development',1)]
for i,(label, study,c) in enumerate(groups):
    rows=[a for a in attempts if a['study']==study and a['concurrency']==c]
    for j,arm in enumerate(['baseline','candidate']):
        val=statistics.mean(a['accuracy'] for a in rows if a['arm']==arm)*100
        ax.barh(i+(j-.5)*.30,val,height=.27,color=BLUE if j==0 else 'white',edgecolor=BLUE,hatch=None if j==0 else '///',label=arm if i==0 else None)
    ax.text(min(val+1,101),i,f'{val:.2f}%',va='center',color=INK)
ax.axvline(95,color=INK,linestyle='--',label='Frozen 95% quality gate')
ax.set(yticks=range(len(groups)),yticklabels=[g[0] for g in groups],xlim=(0,112),xlabel='Exact answers / all offered requests (%)')
ax.invert_yaxis();ax.legend(loc='upper center',bbox_to_anchor=(.5,-.15),ncols=3,fontsize=8)
fig.suptitle('Exact task quality by retained study and concurrency',x=.02,ha='left')
ax.set_title('128 requests per historical arm; 8 per development arm. Different tasks/settings across studies.',fontsize=9,loc='left',fontweight='normal')
save(fig,'quality-gates')

fig, axes=plt.subplots(1,2,figsize=(10,4),layout='constrained',sharey=True)
for ax,c in zip(axes,[1,4]):
    ps=[p for p in pairs if p['study']=='14b' and p['concurrency']==c]
    ax.plot([p['pair_index']+1 for p in ps],[p['service_throughput_ratio'] for p in ps],color=BLUE,marker='o',label='Service throughput')
    ax.plot([p['pair_index']+1 for p in ps],[p['full_attempt_efficiency_ratio'] for p in ps],color=GOLD,marker='s',linestyle='--',label='Full-attempt efficiency')
    ax.axhline(1.05,color=INK,linestyle=':',label='5% practical threshold')
    ax.set(title=f'Concurrency {c}',xlabel='Pair (AB, BA, AB, BA)',xticks=[1,2,3,4],ylim=(0,4.5))
    ax.grid(axis='y',alpha=.2)
axes[0].set_ylabel('Candidate / baseline (×)')
axes[0].legend(fontsize=8)
fig.suptitle('14B paired service and full-attempt effects\n128 requests per arm; full attempt includes repeated verification and load',fontsize=12)
save(fig,'paired-effects')

fig,axes=plt.subplots(1,2,figsize=(10,4.5),layout='constrained')
for ax,c in zip(axes,[1,4]):
    for arm,col,linestyle in [('baseline',BLUE,'-'),('candidate',GOLD,'--')]:
        vals=sorted(r['arrival_to_completion_s'] for r in requests if r['study']=='14b' and r['concurrency']==c and r['arm']==arm)
        ax.plot(vals,[(i+1)/len(vals) for i in range(len(vals))],color=col,linestyle=linestyle,label=arm)
    ax.axvline(30,color=INK,linestyle=':',label='30 s end-to-end SLO')
    ax.set(title=f'Concurrency {c}',xlabel='Arrival to completion (seconds)',ylabel='Empirical fraction',ylim=(0,1),xlim=(0,1300))
    ax.grid(alpha=.15)
axes[0].legend(fontsize=8)
fig.suptitle('14B request latency distributions\n512 observations per arm/concurrency, correlated within four simultaneous batches',fontsize=12)
save(fig,'latency-distributions')

print(json.dumps({'attempts':len(attempts),'requests':len(requests),'pairs':len(pairs),'token_differences':differences,'cost_context':cost_context},indent=2))
