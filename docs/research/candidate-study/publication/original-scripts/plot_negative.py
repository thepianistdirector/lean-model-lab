#!/usr/bin/env python3
"""Publication artifacts from the final retained descriptive CSV tables."""
import argparse,csv,pathlib,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
p=argparse.ArgumentParser();p.add_argument('--analysis',type=pathlib.Path,required=True);a=p.parse_args();out=a.analysis/'figures';out.mkdir(exist_ok=True)
def rows(name):return list(csv.DictReader((a.analysis/name).open()))
def save(fig,name):
 for suffix in ['png','svg','pdf']:fig.savefig(out/(name+'.'+suffix),dpi=220,bbox_inches='tight')
 plt.close(fig)
def style(ax):
 ax.spines[['top','right']].set_visible(False);ax.tick_params(labelsize=8)
attempts=rows('attempts.csv');oracles=rows('oracle-strata.csv')
policies=[('negative-confirm-slice-study04','Dependency slice'),('negative-confirm-simple-study04','Simple gate'),('negative-confirm-learned-study04','Trained gate')]
keys=[(study,label,pair) for study,label in policies for pair in [0,1]]
if all(any(r['study']==study for r in attempts) for study,_,_ in keys):
 fig,axs=plt.subplots(2,1,figsize=(10,7),layout='constrained')
 for arm,label,color,offset in [('baseline','Native full context','#4c6585',-.24),('candidate','Native candidate','#b86939',0)]:
  selected=[next(r for r in attempts if r['study']==study and r['pair_index']==str(pair) and r['arm']==arm) for study,_,pair in keys]
  bars=axs[0].bar([i+offset for i in range(6)],[float(r['accuracy'])*100 for r in selected],width=.22,label=label,color=color)
  axs[0].bar_label(bars,labels=[r['correct'] for r in selected],padding=2,fontsize=7)
  wall=axs[1].bar([i+(offset+.12) for i in range(6)],[float(r['full_wall_s']) for r in selected],width=.22,label=label,color=color)
  axs[1].bar_label(wall,labels=[f"{float(r['full_wall_s']):.0f}" for r in selected],padding=2,fontsize=7)
 union=[next(r for r in oracles if r['study']==study and r['repeat_scope']==f'pair_{pair}' and r['dimension']=='all') for study,_,pair in keys]
 bars=axs[0].bar([i+.24 for i in range(6)],[float(r['oracle_accuracy'])*100 for r in union],width=.22,color='#7f9175',label='Observed full/candidate union')
 axs[0].bar_label(bars,labels=[r['oracle_correct'] for r in union],padding=2,fontsize=7)
 axs[0].axhline(95,color='#a12828',linestyle='--',linewidth=1.1,label='95% required')
 axs[0].set_ylim(0,110);axs[0].set_ylabel('Exact accuracy (%)');axs[0].set_title('Counts above bars divide by all 128 offered questions per arm')
 axs[0].legend(ncol=2,frameon=False,fontsize=8,loc='upper left',bbox_to_anchor=(0,1.25))
 axs[1].set_ylim(0,max(float(r['full_wall_s']) for r in attempts if r['phase']=='MEASUREMENT')*1.2);axs[1].set_ylabel('Full attempt wall (seconds)');axs[1].set_title('Descriptive deployment cost; quality gates determine eligibility')
 for ax in axs:
  ax.set_xticks(range(6),[label+'\n'+('AB' if pair==0 else 'BA') for _,label,pair in keys]);style(ax)
 fig.suptitle('Fixed mixed-record confirmation · 0.5B · 24 records · concurrency one',fontsize=13)
 save(fig,'confirmation-quality-and-cost')
 classes=[('both_correct','Both correct','#4e846b'),('full_only_correct','Full only: candidate harm','#b75143'),('candidate_only_correct','Candidate only: benefit','#5f87ac'),('both_wrong','Both wrong','#c7c9cc')]
 fig,ax=plt.subplots(figsize=(10,4),layout='constrained');bottom=[0]*6
 for field,label,color in classes:
  values=[int(r[field]) for r in union];bars=ax.bar(range(6),values,bottom=bottom,label=label,color=color,width=.6)
  for i,(b,v) in enumerate(zip(bottom,values)):
   if v>=4:ax.text(i,b+v/2,str(v),ha='center',va='center',fontsize=8)
  bottom=[b+v for b,v in zip(bottom,values)]
 ax.set_xticks(range(6),[label+'\n'+('AB' if pair==0 else 'BA') for _,label,pair in keys]);ax.set_ylabel('Questions per pair (all 128 retained)');ax.set_ylim(0,134);style(ax);ax.legend(ncol=2,frameon=False,fontsize=8,bbox_to_anchor=(0,1.23),loc='upper left');ax.set_title('Aggregate correctness retains both harmed and jointly wrong questions',pad=45)
 save(fig,'confirmation-four-outcomes')
 fig,ax=plt.subplots(figsize=(9,4),layout='constrained');families=['record-lookup','reference-chain','record-updates'];family_rows=[next(r for r in oracles if r['study']=='negative-confirm-slice-study04' and r['repeat_scope']==f'pair_{pair}' and r['dimension']=='family' and r['stratum']==family) for family in families for pair in [0,1]];bottom=[0]*6
 for field,label,color in classes:
  values=[int(r[field]) for r in family_rows];ax.bar(range(6),values,bottom=bottom,label=label,color=color,width=.6)
  for i,(b,v) in enumerate(zip(bottom,values)):
   if v>=2:ax.text(i,b+v/2,str(v),ha='center',va='center',fontsize=8)
  bottom=[b+v for b,v in zip(bottom,values)]
 ax.set_xticks(range(6),[f"{family.replace('record-','')}\n{'AB' if pair==0 else 'BA'} · n={family_rows[i]['offered']}" for i,(family,pair) in enumerate((f,p) for f in families for p in [0,1])]);ax.set_ylabel('Questions per family and pair');ax.set_ylim(0,47);style(ax);ax.legend(ncol=2,frameon=False,fontsize=8,bbox_to_anchor=(0,1.23),loc='upper left');ax.set_title('Dependency-slice outcome classes across the fixed mixed population',pad=45)
 save(fig,'slice-family-outcomes')
fit='negative-fit-study04';budget='negative-budget-control-study04'
if all(any(r['study']==study for r in attempts) for study in [fit,budget]):
 fig,ax=plt.subplots(figsize=(8,4),layout='constrained')
 configs=[(fit,'baseline','Full in fit','#4c6585',-.27),(fit,'candidate','Dependency slice','#b86939',-.09),(budget,'baseline','Full in control','#93a3b8',.09),(budget,'candidate','Matched record budget','#827397',.27)]
 for study,arm,label,color,offset in configs:
  selected=[next(r for r in attempts if r['study']==study and r['arm']==arm and r['pair_index']==str(pair)) for pair in [0,1]];bars=ax.bar([pair+offset for pair in [0,1]],[int(r['correct']) for r in selected],width=.17,label=label,color=color);ax.bar_label(bars,labels=[r['correct']+'/32' for r in selected],fontsize=8,padding=3)
 ax.set_xticks([0,1],['AB repetition','BA repetition']);ax.set_ylim(0,36);ax.set_ylabel('Exact correct among the same 32 tables');style(ax);ax.legend(ncol=2,frameon=False,fontsize=8,loc='upper left',bbox_to_anchor=(0,1.22));ax.set_title('Development causal control: semantic selection versus record shortening',pad=40)
 save(fig,'matched-budget-development-control')
controller_path=pathlib.Path(__file__).resolve().parent/'negative-controller04/controller.json'
if controller_path.exists():
 controller=json.loads(controller_path.read_text());cal=controller['calibration'];trace=cal['trace'];n=cal['row_count'];fig,axs=plt.subplots(1,2,figsize=(10,4),layout='constrained');x=range(len(trace));labels=[str(r['threshold']) for r in trace]
 bars=axs[0].bar(x,[100*r['routed_correct']/n for r in trace],color='#4c6585');axs[0].bar_label(bars,labels=[str(r['routed_correct'])+'/'+str(n) for r in trace],padding=3,fontsize=8);axs[0].axhline(95,color='#a12828',linestyle='--',label='95% required');axs[0].set_ylim(0,110);axs[0].set_ylabel('Routed calibration accuracy (%)');axs[0].legend(frameon=False,fontsize=8)
 for offset,key,label,color in [(-.18,'accepted','Accepted cases','#7f9175'),(.18,None,'Accepted harmful cases','#b75143')]:
  values=[r[key] if key else r['accepted_outcomes']['full_only_correct'] for r in trace];bars=axs[1].bar([i+offset for i in x],values,width=.34,color=color,label=label);axs[1].bar_label(bars,padding=2,fontsize=8)
 axs[1].set_ylim(0,n*1.18);axs[1].set_ylabel('Calibration questions');axs[1].legend(frameon=False,fontsize=8,loc='upper left',bbox_to_anchor=(0,1.23))
 for ax in axs:ax.set_xticks(list(x),labels);ax.set_xlabel('Frozen harmful-omission score threshold');style(ax)
 fig.suptitle('Actual calibration artifact: '+controller['parameters']['mode']+' · no population guarantee',fontsize=12)
 save(fig,'controller-calibration')
print(out)
