"""Accessible standalone report derived from validated evidence, with no remote assets."""
from __future__ import annotations

import html
import json


def _escape(value) -> str:
    return html.escape(str(value), quote=True)


def _seconds(value) -> str:
    return 'Unavailable' if value is None else f'{value / 1_000_000_000:.3f} s'


def _number(value, places=3) -> str:
    return 'Unavailable' if value is None else f'{value:.{places}f}'


def render_task_families(attempts):
    rows=[]
    for attempt in attempts:
        for family,value in attempt.get('task_families',{}).items():
            rows.append('<tr>'+''.join('<td>'+_escape(v)+'</td>' for v in (
                attempt['attempt_id'],attempt['arm'],family,
                f"{value['quality_correct']} / {value['expected_count']}",
                f"{value['observed_count']} / {value['expected_count']}",
                _seconds(value['client_end_to_end_ns']['p95'])))+'</tr>')
    if not rows:return ''
    return ('<details><summary>Mixed workload component results</summary><p>These are constituent subgroups of one frozen mixed population. '
        'The full 128-request minimum applies to the combined population; smaller subgroups are descriptive.</p>'
        '<div class="table-scroll" tabindex="0" role="region" aria-label="Mixed workload component results"><table>'
        '<caption>Offered denominators and observed task quality by component</caption><thead><tr>'+
        ''.join('<th scope="col">'+v+'</th>' for v in ('Attempt','Arm','Component','Correct / offered','Observed / offered','End-to-end p95'))+
        '</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div></details>')


def render_report(result: dict) -> str:
    """Call only with evaluate_campaign output; content is still HTML-escaped."""
    v3=result.get('schema_version')==3
    v2=result.get('schema_version') in (2,3)
    context=result.get('recipe_context',{})
    fixture = result['evidence_class'] == 'TEST_FIXTURE'
    title = 'Evaluator test fixture' if fixture else ('Structured-context study' if v3 else 'CPU prefix-cache study')
    comparison_description = ('Baseline versus '+context['mechanism_id']+', with task quality, output differences and total costs.' if v3 else 'Baseline versus one prompt-prefix cache policy, with quality and complete request accounting.')
    quality_description = ('Both arms require at least 95% exact task answers and no observed pairwise quality loss. Token parity is required only for same-input controls; changed-input differences are retained. Primary cost includes prompt analysis, startup and shutdown.' if v3 else 'Absolute quality: at least 95% exact synthetic keys in every arm. Token parity is an additional check.')
    badge = 'TEST DATA · NO MODEL INFERENCE' if fixture else 'DEVICE-SPECIFIC MEASUREMENTS'
    finding = result['finding'].replace('_',' ').capitalize()
    rows = []
    for attempt in result['attempts']:
        latency = attempt['latency']['client_end_to_end_ns']
        rows.append('<tr>'+''.join('<td>'+_escape(value)+'</td>' for value in (
            attempt['attempt_id'], attempt['arm'], attempt['concurrency'], attempt['pair_index']+1,
            attempt['status'], f"{attempt['quality_correct']}/{attempt['quality_denominator']}",
            f"{attempt['observed_requests']}/{attempt['expected_requests']}",
            _number(attempt['successful_requests_per_second']), _seconds(latency['p95']),
            _seconds(attempt['full_wall_ns'])))+'</tr>')
    group_sections = []
    for concurrency, group in result['concurrency_groups'].items():
        pairs = []
        for pair in group['pairs']:
            ratio=pair['throughput_candidate_over_baseline']
            ratio_text='Comparison unavailable' if ratio is None else _number(ratio)+'× request throughput'
            if v3:
                full_ratio=pair.get('full_wall_efficiency_candidate_over_baseline')
                ratio_text += '; full-wall efficiency '+('unavailable' if full_ratio is None else _number(full_ratio)+'×')
                ratio_text += '; task accuracy difference '+_number(pair['quality_difference_candidate_minus_baseline'])
            parity_text = ('observed '+('matched' if pair['token_parity'] else 'different')) if v3 else ('passed' if pair['token_parity'] else 'failed')
            pairs.append('<li>Pair '+str(pair['pair_index']+1)+': '+_escape(ratio_text)+
                         '; token parity '+parity_text+'.</li>')
        group_sections.append('<section><h3>Concurrency '+_escape(concurrency)+'</h3><p>'+_escape(
            group['finding'].replace('_',' ').capitalize())+'</p><ul>'+''.join(pairs)+'</ul></section>')
    reasons=''.join('<li>'+_escape(x.replace('_',' '))+'</li>' for x in result['ineligibility_reasons'])
    limits=''.join('<li>'+_escape(x)+'</li>' for x in result['limitations'])
    accounting=result['accounting']
    pair_title='Three pairs, two concurrency modes'
    pair_description='AB / BA / AB order is fixed before execution. Ratios below are descriptive; three pairs do not support a precise confidence interval.'
    serving_html=''
    if v2:
        evaluation=context['evaluation'];generator=context['workload_generator']
        pair_title=f"{evaluation['pairs_per_concurrency']} pairs per concurrency"
        pair_description=' / '.join(evaluation['pair_order'])+' order is frozen before execution. Ratios are descriptive; failed campaign gates suppress every comparison ratio.'
        serving_rows=[]
        for attempt in result['attempts']:
            serving=attempt['serving']
            values=(attempt['attempt_id'],serving['arrival_mode'],serving['offered_requests'],serving['admitted_requests'],
                serving['rejected_requests'],serving['expired_requests'],serving['slo_qualified_requests'],
                _number(serving['goodput_per_second']),_number(serving['offered_requests_per_second']))
            serving_rows.append('<tr>'+''.join('<td>'+_escape(v)+'</td>' for v in values)+'</tr>')
        serving_html='<section><h2>Arrival replay and qualified requests</h2><p>Recipe purpose: <strong>'+_escape(context['purpose'])+'</strong>. Model: '+_escape(context['model_profile_id'])+'.</p>'
        serving_html+='<p>Qualified requests have an exact answer, observed time to first token within '+_seconds(evaluation['ttft_slo_ns'])+' and end-to-end completion within '+_seconds(evaluation['end_to_end_slo_ns'])+' of the offered arrival. Goodput divides this count by the entire service envelope; every offered request stays in the quality denominator.</p>'
        serving_html+='<p>Offered rate uses the first-to-last arrival span; simultaneous batches have no offered rate. Queue limits and pre-dispatch deadlines remain in the frozen recipe. These descriptive counts cannot override a failed comparison gate.</p>'
        serving_html+='<div class="table-scroll" tabindex="0" role="region" aria-label="Serving results"><table><caption>Declared arrivals and observed outcomes</caption><thead><tr>'+''.join('<th scope="col">'+x+'</th>' for x in ['Attempt','Arrival mode','Offered','Admitted','Rejected','Expired','Qualified','Goodput / s','Offered / s'])+'</tr></thead><tbody>'+''.join(serving_rows)+'</tbody></table></div></section>'
    full=accounting.get('full_cost_accounting',{})
    full_cost='Full allocation wall time: '+_seconds(full.get('registered_full_wall_ns'))+'. '+str(full.get('scope','Required setup ledger is unavailable.'))
    for ancestor in accounting.get('historical_preparation_ancestors',[]):
        full_cost += ' Separate earlier preparation: '+_seconds(ancestor['attributed_setup_ns'])+'. '+ancestor['scope']
    raw = _escape(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>{_escape(title)} · Lean Model Lab</title>
<style>
:root{{color-scheme:light;--ink:#192b32;--muted:#41585f;--line:#c8d3d5;--paper:#f7f9f8;--accent:#09655b}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.55 system-ui,sans-serif}}
a{{color:var(--accent)}}a:focus-visible,summary:focus-visible,[tabindex]:focus-visible{{outline:3px solid #9d4a00;outline-offset:4px}}
.skip{{position:absolute;left:1rem;top:-6rem;background:white;padding:1rem}}.skip:focus{{top:1rem}}
header,main,footer{{max-width:1120px;margin:auto;padding:2rem 1.5rem}}header{{border-bottom:1px solid var(--line)}}
.wordmark{{font-weight:750;letter-spacing:.025em;margin:0 0 2rem}}.badge{{font-size:.8rem;font-weight:750;color:var(--accent);letter-spacing:.06em}}
h1{{font-size:clamp(2rem,5vw,3.4rem);line-height:1.08;letter-spacing:-.035em;max-width:20ch;margin:.8rem 0 1.4rem}}
h2{{font-size:1.4rem;margin:0 0 1rem}}h3{{font-size:1.05rem}}p{{max-width:78ch}}.lede{{font-size:1.15rem;color:var(--muted)}}
section{{margin-bottom:2.5rem}}.facts{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:1rem;margin:1.5rem 0}}
.facts div{{border-top:2px solid var(--line);padding-top:.7rem}}dt{{color:var(--muted)}}dd{{font-size:1.5rem;font-weight:650;margin:.4rem 0}}
.notice{{border-left:4px solid #9d4a00;padding:.1rem 1rem;background:#fff5e8}}.groups{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:2rem}}
.table-scroll{{overflow:auto;border:1px solid var(--line);background:white}}table{{border-collapse:collapse;width:100%;font-size:.875rem}}
caption{{text-align:left;padding:1rem;font-weight:600}}th,td{{padding:.75rem;text-align:left;vertical-align:top;border-bottom:1px solid var(--line)}}th{{white-space:nowrap;background:#eaf0ed}}td:first-child{{overflow-wrap:anywhere;min-width:10rem}}
summary{{cursor:pointer;font-weight:650;padding:.8rem 0}}pre{{white-space:pre-wrap;overflow-wrap:anywhere;padding:1rem;background:white;border:1px solid var(--line);font-size:.8rem}}
footer{{border-top:1px solid var(--line);font-size:.875rem;color:var(--muted)}}li{{margin:.4rem 0}}code{{overflow-wrap:anywhere}}
@media(max-width:480px){{header,main,footer{{padding:1.5rem 1rem}}.wordmark{{margin-bottom:1.5rem}}}}
@media print{{header,main,footer{{max-width:none;padding:1rem}}.table-scroll{{overflow:visible}}table{{font-size:9px}}details{{display:none}}}}
</style></head><body><a class="skip" href="#main">Skip to evidence</a>
<header><p class="wordmark">Lean Model Lab / {'1.0' if v3 else '0.4' if v2 else '0.1'} development</p><p class="badge">{badge}</p>
<h1>{_escape(title)}</h1><p class="lede">{_escape(finding)}. {_escape(comparison_description)}</p>
{'<div class="notice"><p>This report exercises the evaluator with fabricated test inputs. It contains no measured model result or speedup claim.</p></div>' if fixture else ''}
</header><main id="main">
<section aria-labelledby="accounting"><h2 id="accounting">Every attempt stays in view</h2>
<dl class="facts"><div><dt>Retained attempts</dt><dd>{accounting['attempt_count']}</dd></div>
<div><dt>Observed requests</dt><dd>{accounting['observed_requests']}</dd></div>
<div><dt>Missing requests</dt><dd>{accounting['missing_requests']}</dd></div>
<div><dt>Attempt wall time</dt><dd>{_seconds(accounting['full_wall_ns'])}</dd></div></dl>
<p>Attempt wall time includes retained attempt overhead. Acquisition and build costs require the separate setup ledger; this view does not silently count them as zero.</p>
<p>{_escape(full_cost)}</p>
<p>{_escape(quality_description)} Energy and engine-internal token emission times are unavailable.</p>
{'<div class="notice"><p>Comparison is ineligible:</p><ul>'+reasons+'</ul></div>' if reasons else ''}</section>
<section aria-labelledby="paired"><h2 id="paired">{_escape(pair_title)}</h2>
<p>{_escape(pair_description)}</p>
<div class="groups">{''.join(group_sections)}</div></section>
<section aria-labelledby="attempts"><h2 id="attempts">Complete attempt results</h2><p id="table-help">Scroll the table horizontally on narrow screens. Quality and observed-request counts retain all expected requests in their denominators.</p>
<div class="table-scroll" tabindex="0" role="region" aria-label="Attempt results table" aria-describedby="table-help"><table>
<caption>All retained attempts, in execution order</caption><thead><tr>{''.join('<th scope="col">'+x+'</th>' for x in ['Attempt','Arm','Concurrency','Pair','Status','Correct / expected','Observed / expected','Requests / s','End-to-end p95','Full wall'])}</tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>
{serving_html}{render_task_families(result['attempts'])}
<section aria-labelledby="limits"><h2 id="limits">What this evidence can support</h2><ul>{limits}</ul>
<p>Configuration SHA-256: <code>{_escape(result['config_sha256'])}</code><br>Workload SHA-256: <code>{_escape(result['workload_sha256'])}</code></p></section>
<details><summary>Inspect the complete derived JSON</summary><pre>{raw}</pre></details>
</main><footer>Generated from validated raw evidence. Local development artifact; this page does not establish public release, external reproduction or human review. No remote scripts, fonts or telemetry.</footer></body></html>'''
