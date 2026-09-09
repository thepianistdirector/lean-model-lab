#!/usr/bin/env python3
"""Publication artifacts from the final retained descriptive CSV tables."""
import argparse,csv,pathlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=argparse.ArgumentParser();p.add_argument('--analysis',type=pathlib.Path,required=True);p.add_argument('--manifest',type=pathlib.Path,required=True);p.add_argument('--evidence-root',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();manifest=json.loads(a.manifest.read_text());base=(a.evidence_root or a.manifest.parent).resolve();out=a.output
if out.exists():raise SystemExit('Choose a new figure output directory')
out.mkdir(parents=True)
def rows(name):return list(csv.DictReader((a.analysis/name).open()))
def save(fig,name):
 for suffix in ['png','svg','pdf']:fig.savefig(out/(name+'.'+suffix),dpi=220,bbox_inches='tight')
 plt.close(fig)
def style(ax):
 ax.spines[['top','right']].set_visible(False);ax.tick_params(labelsize=8)
attempts=rows('attempts.csv');oracles=rows('oracle-strata.csv')
policies=[(r['id'],r['label']) for r in manifest.get('confirmation_policies',[])]
keys=[(study,label,pair) for study,label in policies for pair in [0,1]]
if len(policies)==3 and all(any(r['study']==study for r in attempts) for study,_,_ in keys):
 fig,axs=plt.subplots(2,1,figsize=(10,7),layout='constrained')
 for arm,label,color,offset in [('baseline','Native full context','#4c6585',-.24),('candidate','Native candidate','#b86939',0)]:
  selected=[next(r for r in attempts if r['study']==study and r['pair_index']==str(pair) and r['arm']==arm) for study,_,pair in keys]
  bars=axs[0].bar([i+offset for i in range(6)],[float(r['accuracy'])*100 for r in selected],width=.22,label=label,facecolor='white' if arm=='candidate' else color,edgecolor=color,hatch='///' if arm=='candidate' else None,linewidth=.9)
  axs[0].bar_label(bars,labels=[r['correct'] for r in selected],padding=2,fontsize=7)
  wall=axs[1].bar([i+(offset+.12) for i in range(6)],[float(r['full_wall_s']) for r in selected],width=.22,label=label,facecolor='white' if arm=='candidate' else color,edgecolor=color,hatch='///' if arm=='candidate' else None,linewidth=.9)
  axs[1].bar_label(wall,labels=[f"{float(r['full_wall_s']):.0f}" for r in selected],padding=2,fontsize=7)
 union=[next(r for r in oracles if r['study']==study and r['repeat_scope']==f'pair_{pair}' and r['dimension']=='all') for study,_,pair in keys]
 bars=axs[0].bar([i+.24 for i in range(6)],[float(r['oracle_accuracy'])*100 for r in union],width=.22,color='#b6b9bf',edgecolor='#565d66',hatch='..',label='Observed full/candidate union')
 axs[0].bar_label(bars,labels=[r['oracle_correct'] for r in union],padding=2,fontsize=7)
 axs[0].axhline(95,color='#34383c',linestyle='--',linewidth=1.1,label='95% required')
 axs[0].set_ylim(0,110);axs[0].set_ylabel('Exact accuracy (%)');axs[0].set_title('Counts above bars divide by all 128 offered questions per arm')
 axs[0].legend(ncol=2,frameon=False,fontsize=8,loc='upper left',bbox_to_anchor=(0,1.25))
 axs[1].set_ylim(0,max(float(r['full_wall_s']) for r in attempts if r['phase']=='MEASUREMENT')*1.2);axs[1].set_ylabel('Full attempt wall (seconds)');axs[1].set_title('Descriptive deployment cost; quality gates determine eligibility')
 for ax in axs:
  ax.set_xticks(range(6),[label+'\n'+('AB' if pair==0 else 'BA') for _,label,pair in keys]);style(ax)
 fig.suptitle('Fixed mixed-record confirmation · 0.5B · 24 records · concurrency one',fontsize=13)
 save(fig,'confirmation-quality-and-cost')
 classes=[('both_correct','Both correct','#4c6585',''),('full_only_correct','Full only: candidate harm','#d58b53','xxx'),('candidate_only_correct','Candidate only: benefit','#a6bad1','///'),('both_wrong','Both wrong','#dedfe2','...')]
 fig,ax=plt.subplots(figsize=(10,4),layout='constrained');bottom=[0]*6
 for field,label,color,hatch in classes:
  values=[int(r[field]) for r in union];bars=ax.bar(range(6),values,bottom=bottom,label=label,color=color,edgecolor='#424851',linewidth=.5,hatch=hatch,width=.6)
  for i,(b,v) in enumerate(zip(bottom,values)):
   if v>=4:ax.text(i,b+v/2,str(v),ha='center',va='center',fontsize=8,color='white' if field=='both_correct' else '#202428')
  bottom=[b+v for b,v in zip(bottom,values)]
 ax.set_xticks(range(6),[label+'\n'+('AB' if pair==0 else 'BA') for _,label,pair in keys]);ax.set_ylabel('Questions per pair (all 128 retained)');ax.set_ylim(0,134);style(ax);ax.legend(ncol=2,frameon=False,fontsize=8,bbox_to_anchor=(.5,1.01),loc='lower center');ax.set_title('Aggregate correctness retains both harmed and jointly wrong questions',pad=48)
 save(fig,'confirmation-four-outcomes')
 fig,ax=plt.subplots(figsize=(9,4),layout='constrained');families=['record-lookup','reference-chain','record-updates'];family_rows=[next(r for r in oracles if r['study']==manifest['relationships']['slice_confirmation'] and r['repeat_scope']==f'pair_{pair}' and r['dimension']=='family' and r['stratum']==family) for family in families for pair in [0,1]];bottom=[0]*6
 for field,label,color,hatch in classes:
  values=[int(r[field]) for r in family_rows];ax.bar(range(6),values,bottom=bottom,label=label,color=color,edgecolor='#424851',linewidth=.5,hatch=hatch,width=.6)
  for i,(b,v) in enumerate(zip(bottom,values)):
   if v>=2:ax.text(i,b+v/2,str(v),ha='center',va='center',fontsize=8,color='white' if field=='both_correct' else '#202428')
  bottom=[b+v for b,v in zip(bottom,values)]
 ax.set_xticks(range(6),[f"{family.replace('record-','')}\n{'AB' if pair==0 else 'BA'} · n={family_rows[i]['offered']}" for i,(family,pair) in enumerate((f,p) for f in families for p in [0,1])]);ax.set_ylabel('Questions per family and pair');ax.set_ylim(0,47);style(ax);ax.legend(ncol=2,frameon=False,fontsize=8,bbox_to_anchor=(.5,1.01),loc='lower center');ax.set_title('Dependency-slice outcome classes across the fixed mixed population',pad=48)
 save(fig,'slice-family-outcomes')
fit=manifest.get('relationships',{}).get('fit');budget=manifest.get('relationships',{}).get('matched_budget_control')
if all(any(r['study']==study for r in attempts) for study in [fit,budget]):
 fig,ax=plt.subplots(figsize=(8,4),layout='constrained')
 configs=[(fit,'baseline','Full in fit','#4c6585',-.27),(fit,'candidate','Dependency slice','#b86939',-.09),(budget,'baseline','Full in control','#93a3b8',.09),(budget,'candidate','Matched record budget','#b86939',.27)]
 for study,arm,label,color,offset in configs:
  selected=[next(r for r in attempts if r['study']==study and r['arm']==arm and r['pair_index']==str(pair)) for pair in [0,1]];bars=ax.bar([pair+offset for pair in [0,1]],[int(r['correct']) for r in selected],width=.17,label=label,facecolor='white' if arm=='candidate' else color,edgecolor=color,hatch=('xxx' if study==budget else '///') if arm=='candidate' else None,linewidth=.9);ax.bar_label(bars,labels=[r['correct']+'/32' for r in selected],fontsize=8,padding=3)
 ax.set_xticks([0,1],['AB repetition','BA repetition']);ax.set_ylim(0,36);ax.set_ylabel('Exact correct among the same 32 tables');style(ax);ax.legend(ncol=2,frameon=False,fontsize=8,loc='upper left');ax.set_title('Development control: dependency selection at matched record counts',pad=16)
 save(fig,'matched-budget-development-control')
controller_reference=manifest.get('controller',{}).get('path')
controller_path=(base/controller_reference).resolve() if controller_reference else None
if controller_path and controller_path.exists():
 controller=json.loads(controller_path.read_text());cal=controller['calibration'];trace=cal['trace'];n=cal['row_count'];fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained');x=range(len(trace));labels=[str(r['threshold']) for r in trace]
 bars=axs[0].bar(x,[100*r['routed_correct']/n for r in trace],color='#4c6585');axs[0].bar_label(bars,labels=[str(r['routed_correct'])+'/'+str(n) for r in trace],padding=3,fontsize=8);axs[0].axhline(95,color='#34383c',linestyle='--',label='95% required');axs[0].set_ylim(0,110);axs[0].set_ylabel('Routed calibration accuracy (%)');axs[0].legend(frameon=False,fontsize=8)
 for offset,key,label,color in [(-.18,'accepted','Accepted cases','#a6bad1'),(.18,None,'Accepted harmful cases','#b86939')]:
  values=[r[key] if key else r['accepted_outcomes']['full_only_correct'] for r in trace];bars=axs[1].bar([i+offset for i in x],values,width=.34,facecolor=color if key else 'white',edgecolor=color,hatch=None if key else 'xxx',linewidth=.9,label=label);axs[1].bar_label(bars,padding=2,fontsize=8)
 axs[1].set_ylim(0,n*1.18);axs[1].set_ylabel('Calibration questions');axs[1].legend(frameon=False,fontsize=8,loc='upper left',bbox_to_anchor=(0,1.23))
 for ax in axs:ax.set_xticks(list(x),labels);ax.set_xlabel('Frozen harmful-omission score threshold');style(ax)
 fig.suptitle('Actual calibration artifact: '+controller['parameters']['mode']+' · no population guarantee',fontsize=12)
 save(fig,'controller-calibration')
for spec in manifest.get('closed_figures',[]):
 study=spec['id'];local=[r for r in attempts if r['study']==study]
 if not local:continue
 fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained')
 for arm,label,color,offset in [('baseline','Original full v1','#4c6585',-.18),('candidate',spec['candidate_label'],'#b86939',.18)]:
  selected=sorted([r for r in local if r['arm']==arm],key=lambda r:r['pair_index'])
  for i,key in enumerate(['accuracy','full_wall_s']):
   bars=axs[i].bar([j+offset for j in range(2)],[float(r[key])*(100 if i==0 else 1) for r in selected],width=.34,label=label,facecolor='white' if arm=='candidate' else color,edgecolor=color,hatch='///' if arm=='candidate' else None,linewidth=.9);axs[i].bar_label(bars,labels=[r['correct']+'/'+r['offered'] if i==0 else f"{float(r[key]):.1f}" for r in selected],padding=3,fontsize=8)
 axs[0].axhline(95,color='#34383c',linestyle='--',label='95% required');axs[0].set_ylim(0,110);axs[0].set_ylabel('Exact task accuracy (%)');axs[0].legend(frameon=False,fontsize=8,loc='upper left',bbox_to_anchor=(0,.82));axs[0].set_title('Closed development advance branch')
 axs[1].set_ylim(0,max(float(r['full_wall_s']) for r in local)*1.2);axs[1].set_ylabel('Full attempt wall (seconds)');axs[1].set_title('Descriptive cost; no eligible speedup')
 for ax in axs:ax.set_xticks([0,1],['AB repetition','BA repetition']);style(ax)
 fig.suptitle(spec['title'],fontsize=12);save(fig,spec['figure_name'])
print(out)
