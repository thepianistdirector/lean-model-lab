#!/usr/bin/env python3
"""Standalone development figures from retained analysis CSVs."""
import csv,pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
base=pathlib.Path(__file__).parent
for folder,title,candidate in [('feasibility-14b-analysis03','14B dependency-slice feasibility','Dependency slice'),('clarification-0.5b-analysis04','0.5B fixed instruction diagnosis','Explicit full v2')]:
 p=base/folder;rows=list(csv.DictReader((p/'attempts.csv').open()))
 fig,ax=plt.subplots(1,2,figsize=(10,4),layout='constrained')
 for arm,label,color,offset in [('baseline','Original full v1','#4c6585',-.18),('candidate',candidate,'#b86939',.18)]:
  r=sorted([x for x in rows if x['arm']==arm],key=lambda x:x['pair_index'])
  for i,key in enumerate(['accuracy','full_wall_s']):
   bars=ax[i].bar([j+offset for j in range(2)],[float(x[key])*(100 if i==0 else 1) for x in r],width=.34,label=label,color=color)
   ax[i].bar_label(bars,labels=[f"{int(x['correct'])}/8" if i==0 else f"{float(x[key]):.1f}" for x in r],padding=3)
 ax[0].axhline(95,color='#a12828',linestyle='--',linewidth=1.2,label='95% required')
 ax[0].set_ylim(0,110);ax[0].set_ylabel('Exact task accuracy (%)');ax[0].set_title('All four arms fail the absolute gate')
 ax[1].set_ylim(0,max(float(x['full_wall_s']) for x in rows)*1.2);ax[1].set_ylabel('Full attempt wall (seconds)');ax[1].set_title('Descriptive costs; no eligible speedup')
 for a in ax:
  a.set_xticks([0,1],['Pair 1 · AB','Pair 2 · BA']);a.spines[['top','right']].set_visible(False)
 ax[0].legend(loc='upper left',bbox_to_anchor=(0,.8),frameon=False,fontsize=8)
 fig.suptitle(title+' · eight unique reference-chain questions',fontsize=12)
 for suffix in ['png','svg','pdf']:fig.savefig(p/('feasibility.'+suffix),dpi=200)
 plt.close(fig)
