#!/usr/bin/env python3
"""Standalone manuscript figures from retained systems-study CSV tables."""
import argparse
import csv
from pathlib import Path
import statistics

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BLUE = '#3478B8'
GOLD = '#C99024'
INK = '#26323B'
GREY = '#E3E6E8'
COLORS = {'baseline': BLUE, 'candidate': GOLD}
LABELS = {'baseline': 'Full context + cache', 'candidate': 'Dependency slice + cache'}


def rows(path):
    with path.open() as source:
        return list(csv.DictReader(source))


def finish(fig, output, name):
    for extension in ('png', 'svg', 'pdf'):
        fig.savefig(output/(name+'.'+extension), dpi=180, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def axes_style(ax):
    ax.spines[['top', 'right']].set_visible(False)
    ax.spines[['left', 'bottom']].set_color('#8A949B')
    ax.grid(axis='y', color=GREY, linewidth=.6)
    ax.set_axisbelow(True)
    ax.tick_params(colors=INK)


def plot(tables, output):
    output.mkdir(parents=True, exist_ok=True)
    cases = rows(tables/'cases.csv'); attempts = rows(tables/'attempts.csv')
    requests = rows(tables/'requests.csv'); table_rows = rows(tables/'tables.csv')
    plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':10, 'text.color':INK,
        'axes.labelcolor':INK, 'axes.titlecolor':INK, 'axes.titlesize':12,
        'svg.fonttype':'none', 'pdf.fonttype':42})
    fig, ax = plt.subplots(figsize=(max(8, len(cases)*3), 5.5))
    fig.subplots_adjust(top=.74, bottom=.23, left=.12, right=.97)
    for i, case in enumerate(cases):
        for offset, arm in ((-.18,'baseline'),(.18,'candidate')):
            count = int(case[arm+'_correct']); total = int(case[arm+'_denominator'])
            value = 100*count/total if total else 0
            ax.bar(i+offset, value, width=.32, color=COLORS[arm], edgecolor=INK, linewidth=.6,
                   hatch='//' if arm=='candidate' else None,
                   label=LABELS[arm] if i==0 else None)
            ax.text(i+offset, value+2.2, f'{count}/{total}\n({value:.1f}%)', ha='center', fontsize=9)
    ax.axhline(95, color=INK, linestyle='--', linewidth=1)
    ax.text(.99, 96.5, '95% gate', transform=ax.get_yaxis_transform(), ha='right', fontsize=9)
    labels = [case['case_id'].split('-')[0].upper()+' · '+
              ('0.5B' if '0.5b' in case['model_profile'] else '14B')+'\n'+
              case['context_records']+' records · '+case['purpose'].lower() for case in cases]
    ax.set_xticks(range(len(cases)), labels)
    ax.set_ylim(0, 112); ax.set_yticks([0,25,50,75,100]); ax.set_ylabel('Exact task accuracy (%)')
    fig.suptitle('Task accuracy by study and arm', x=.12, y=.98, ha='left', fontsize=14)
    handles, names = ax.get_legend_handles_labels()
    fig.legend(handles, names, frameon=False, loc='upper left', bbox_to_anchor=(.11,.925), ncol=2)
    fig.text(.12,.825,'Correct / all offered outputs; counts include both balanced repetitions.', fontsize=9)
    axes_style(ax)
    fig.text(.12,.05,'All offered requests remain in each denominator. Shared-table queries and repetitions are dependent.\nThe unchanged quality and paired task gates govern efficiency eligibility.', fontsize=8.5)
    finish(fig, output, 'quality')
    for case in cases:
        case_id = case['case_id']; data = [r for r in requests if r['case_id']==case_id]
        case_attempts = [a for a in attempts if a['case_id']==case_id]
        fig, axs = plt.subplots(1,3,figsize=(12,4.4))
        for panel, (title, field) in enumerate((('First use: mean per table','cold'),
                ('Remaining queries: mean','warm'),('All queries: total per attempt','total'))):
            ax = axs[panel]; values = []
            for arm in ('baseline','candidate'):
                selected = [r for r in data if r['arm']==arm and r['native_new_tokens']]
                subset = [float(r['native_new_tokens']) for r in selected
                          if (r['first_query_of_table']=='True') == (field=='cold')] if field!='total' else []
                if field=='total':
                    values.append(statistics.mean(float(a['native_new_tokens']) for a in case_attempts if a['arm']==arm))
                else:
                    values.append(statistics.mean(subset) if subset else 0)
            bars = ax.bar([0,1], values, width=.62, color=[BLUE,GOLD], edgecolor=INK, linewidth=.6)
            bars[1].set_hatch('//')
            for x,value in enumerate(values):
                ax.text(x, value+max(values)*.035, f'{value:.1f}' if field in {'cold','warm'} else f'{value:,.0f}', ha='center')
            ax.set_xticks([0,1], ['Full + cache','Slice + cache']); ax.set_ylim(0,max(values)*1.22 or 1)
            ax.set_title(title,loc='left',fontsize=11); ax.set_ylabel('Native newly processed input tokens')
            axes_style(ax)
        fig.suptitle(f'Native input work across cache states — {case_id}',x=.06,ha='left',fontsize=14,y=1.05)
        fig.text(.06,-.12,'Each table contributes 1 first-use and 7 subsequent queries; tables repeat across balanced pairs.\nLater first-use requests can reuse a common instruction prefix. Panels use different y scales.\nToken work is not latency or an API-price estimate; quality gates still apply.',fontsize=9)
        fig.tight_layout(w_pad=2)
        finish(fig,output,case_id+'-cache')
        fig,ax = plt.subplots(figsize=(10,4.8))
        ordered = sorted(case_attempts,key=lambda a:(int(a['pair_index']),a['arm']!='baseline'))
        labels = []
        for i,attempt in enumerate(ordered):
            arm = attempt['arm']; service=float(attempt['service_ns'])/1e9
            full=float(attempt['full_wall_ns'])/1e9; remainder=full-service
            ax.bar(i,service,color=COLORS[arm],edgecolor=INK,linewidth=.6,
                   hatch='//' if arm=='candidate' else None)
            ax.bar(i,remainder,bottom=service,color='white',edgecolor=INK,linewidth=.7,
                   hatch='...',label='Other charged attempt work' if i==0 else None)
            ax.text(i,full+.035*max(float(a['full_wall_ns'])/1e9 for a in ordered),f'{full:.3f}s',ha='center')
            ax.text(i,service/2,f'{service:.3f}s\nservice',ha='center',va='center',color=INK,fontsize=9,
                    bbox={'facecolor':'white','edgecolor':'none','pad':3})
            labels.append(f'Pair {int(attempt["pair_index"])+1}\n'+('Full + cache' if arm=='baseline' else 'Slice + cache'))
        ax.set_xticks(range(len(ordered)),labels); ax.set_ylabel('Wall time per attempt (seconds)')
        ax.set_ylim(0,max(float(a['full_wall_ns'])/1e9 for a in ordered)*1.22)
        ax.set_title(f'Service and full attempt costs — {case_id}',loc='left',pad=18)
        ax.legend(frameon=False,loc='upper left',bbox_to_anchor=(0,1.02)); axes_style(ax)
        qualification = 'Study ineligible: descriptive costs only.' if case['official_eligible']=='False' else 'See the retained report for all eligibility gates.'
        fig.text(.08,-.13,'Producer order is A–B then B–A; bars are grouped by pair for comparison.\nService includes native requests and client/coordinator gaps; their decomposition is retained in the tables.\nOther work includes preparation, verification, load and shutdown. Historical setup is reported separately.\n'+qualification,fontsize=9)
        finish(fig,output,case_id+'-cost')
        if case['purpose'] != 'MEASUREMENT':
            continue
        grouped = [r for r in table_rows if r['case_id']==case_id]
        table_indices = sorted({int(r['table_index']) for r in grouped})
        pair_indices = sorted({int(r['pair_index']) for r in grouped})
        fig, axs = plt.subplots(1,2,figsize=(13,5.6))
        fig.subplots_adjust(top=.75,bottom=.25,wspace=.3,left=.07,right=.98)
        changes = []; positive_tables = set(table_indices)
        for pair in pair_indices:
            selected = sorted((r for r in grouped if int(r['pair_index'])==pair),key=lambda r:int(r['table_index']))
            offset=(pair_indices.index(pair)-(len(pair_indices)-1)/2)*.34
            x=[int(r['table_index'])+1+offset for r in selected]
            delta=[int(r['candidate_subsequent_native_new_tokens'])-int(r['baseline_subsequent_native_new_tokens']) for r in selected]
            changes.extend(delta)
            positive_tables &= {int(r['table_index']) for r,difference in zip(selected,delta) if difference>0}
            axs[0].bar(x,delta,width=.31,color=GOLD,edgecolor=INK,linewidth=.4,hatch='//')
            bottom=[0]*len(selected)
            for field,label,color,hatch in [
                    ('both_correct','Both correct',GREY,None),
                    ('baseline_only_correct','Full only: harm from slicing',BLUE,None),
                    ('candidate_only_correct','Slice only: benefit from slicing',GOLD,'//'),
                    ('both_wrong','Both wrong','white','...')]:
                values=[int(r[field]) for r in selected]
                axs[1].bar(x,values,bottom=bottom,width=.31,color=color,edgecolor=INK,linewidth=.4,hatch=hatch,
                           label=label if pair==pair_indices[0] else None)
                bottom=[b+v for b,v in zip(bottom,values)]
        for ax in axs:
            ax.set_xticks([i+1 for i in table_indices]);ax.tick_params(axis='x',labelsize=8)
            ax.set_xlabel('Retained table index');axes_style(ax)
        axs[0].axhline(0,color=INK,linewidth=.9)
        axs[0].set_ylim(min(0,min(changes))*1.2,max(1,max(changes))*1.22)
        axs[0].set_ylabel('New tokens: slice minus full, seven subsequent queries')
        axs[0].set_title('Warm input work for each table',loc='left',fontsize=12,pad=14)
        axs[0].text(.02,.95,f'{len(positive_tables)}/{len(table_indices)} tables: more slice work in both repeats',
                    transform=axs[0].transAxes,va='top',fontsize=9,
                    bbox={'facecolor':'white','edgecolor':'none','pad':2})
        axs[1].set_ylim(0,8);axs[1].set_yticks([0,2,4,6,8])
        axs[1].set_ylabel('All eight offered queries, by correctness class')
        axs[1].set_title('Harmful, beneficial and shared outcomes',loc='left',fontsize=12,pad=14)
        handles,names=axs[1].get_legend_handles_labels()
        fig.legend(handles,names,frameon=False,ncol=2,loc='upper left',bbox_to_anchor=(.065,.94),fontsize=9)
        fig.suptitle(f'Paired evidence across new tables — {case_id}',x=.07,y=1.01,ha='left',fontsize=14)
        eligibility_note='The study is ineligible.' if case['official_eligible']=='False' else 'Eligibility is reported separately.'
        fig.text(.07,.065,'Each table shows both balanced repetitions: pair 1 on the left, pair 2 on the right. Queries within a table are dependent.\nThe warm-work panel isolates subsequent queries; first-use requests and complete costs remain in the study.\nPositive token differences indicate more work for slicing. Correctness classes retain every offered task. '+eligibility_note,fontsize=9)
        finish(fig,output,case_id+'-table-effects')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tables',required=True,type=Path);parser.add_argument('--output',required=True,type=Path)
    arguments = parser.parse_args();plot(arguments.tables,arguments.output)
