"""Publish paired fold comparisons and report-ready figures from fixed saved evidence."""
from pathlib import Path
import json
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve,roc_curve,confusion_matrix
from src.models.data import ROOT,TARGETS,load_development
from src.models.refinement_temporal import chronological_data
from src.models.refinement_terminal import terminal_cohorts
from src.models.finalize import subgroup_tables

def summarize(run):
 p=json.loads((run/'protocol.json').read_text());s=pd.read_csv(run/'summary.csv');fm=pd.read_csv(run/'fold_metrics.csv');sel=json.loads((run/'selection_freeze.json').read_text());tm=pd.read_csv(run/'terminal_metrics.csv');policy=json.loads((run/'decision_policy.json').read_text());data=chronological_data(ROOT,p)
 pairs=[]
 for task in TARGETS:
  primary='mae' if task=='regression' else 'average_precision'
  links=[('core_plain','expanded_raw_plain','feature expansion, plain'),('core_tree','expanded_raw_tree','feature expansion, tree'),('core_forest','expanded_raw_forest','feature expansion, forest'),('expanded_raw_plain','expanded_inputlog_plain','input log1p, plain')]
  if task=='regression':links += [('expanded_raw_forest','expanded_inputlog_forest','input log1p, forest'),('expanded_inputlog_plain','expanded_log_plain','target log1p, plain'),('expanded_inputlog_forest','expanded_log_forest','target log1p, forest'),('expanded_log_plain','expanded_log_regularized','L2 regularization'),('expanded_log_tree','expanded_log_forest','tree to ensemble'),('expanded_log_forest','expanded_log_forest_leaf50','larger leaves'),('expanded_log_forest','expanded_log_forest_clip60','60-day training cap')]
  else:links += [('expanded_raw_forest','expanded_inputlog_forest','input log1p, forest'),('expanded_inputlog_plain','expanded_inputlog_regularized','L2 regularization'),('expanded_inputlog_tree','expanded_inputlog_forest','tree to ensemble')]
  for a,b,label in links:
   x=fm.loc[(fm.task==task)&(fm.candidate==a)&(fm.partition=='validation')].sort_values('fold')[primary].to_numpy();y=fm.loc[(fm.task==task)&(fm.candidate==b)&(fm.partition=='validation')].sort_values('fold')[primary].to_numpy();delta=(x-y) if task=='regression' else (y-x)
   pairs.append({'task':task,'comparison':label,'from':a,'to':b,'baseline_mean':x.mean(),'candidate_mean':y.mean(),'improvement_mean':delta.mean(),'improvement_sd':delta.std(ddof=1),'improved_folds':int((delta>0).sum()),'fold_differences':json.dumps(delta.tolist())})
 pd.DataFrame(pairs).to_csv(run/'paired_comparisons.csv',index=False)
 # Split stage descriptive evidence, no selection rule consumes these summaries.
 split=[]
 for task in TARGETS:
  for f in range(5):
   tr,va=data['folds'][task,f]
   for role,frame in [('training',tr),('validation',va)]:split.append({'task':task,'fold':f,'role':role,'n':len(frame),'customers':frame.customer_unique_id.nunique(),'timestamp_min':str(frame.prediction_timestamp.min()),'timestamp_max':str(frame.prediction_timestamp.max()),'target_mean':frame[TARGETS[task]].mean(),'target_median':frame[TARGETS[task]].median()})
 pd.DataFrame(split).to_csv(run/'split_audit.csv',index=False)
 figures=run/'figures';figures.mkdir(exist_ok=True)
 labels={'core_dummy':'Core dummy','core_plain':'Core plain linear','core_tree':'Core single tree','core_forest':'Core forest','expanded_raw_plain':'Expanded plain linear','expanded_raw_tree':'Expanded tree','expanded_raw_forest':'Expanded forest','expanded_inputlog_plain':'Input log, plain','expanded_inputlog_forest':'Input log, forest','expanded_inputlog_regularized':'Input log, regularized','expanded_inputlog_tree':'Input log, tree','expanded_log_plain':'Input/target log, plain','expanded_log_regularized':'Input/target log, Ridge','expanded_log_tree':'Input/target log, tree','expanded_log_forest':'Input/target log, forest','expanded_log_forest_leaf50':'Log forest, leaf 50','expanded_log_forest_clip60':'Log forest, cap 60'}
 fig,axes=plt.subplots(1,2,figsize=(14,8))
 for ax,task in zip(axes,TARGETS):
  sub=s.loc[s.task==task];m='mae' if task=='regression' else 'average_precision';v=sub['validation_'+m+'_mean'];sd=sub['validation_'+m+'_sd'];colors=['#146b45' if c==sel['selected'][task]['id'] else '#326ca3' if cycle==1 else '#d17d28' for c,cycle in zip(sub.candidate,sub.cycle)]
  ax.barh(np.arange(len(sub)),v,xerr=sd,color=colors,alpha=.85,capsize=2);ax.set_yticks(np.arange(len(sub)),[labels.get(c,c) for c in sub.candidate],fontsize=8);ax.invert_yaxis();ax.set_xlabel('Validation MAE (days); lower is better' if task=='regression' else 'Validation average precision; higher is better');ax.set_title(task.capitalize());ax.grid(axis='x',alpha=.2)
 fig.suptitle('Two-cycle chronological comparison\nMean ± sample SD across five folds; green is selected');fig.tight_layout();fig.savefig(figures/'two_cycle_comparison.png',dpi=160);plt.close(fig)
 dev,_,_=load_development(ROOT);reviews=pd.read_csv(ROOT/'data/preprocessed/olist_order_reviews_dataset.csv',usecols=['order_id','review_score','review_answer_timestamp'],dtype={'order_id':'string'});_,frames,_=terminal_cohorts(dev,reviews,p['terminal_cutoff']);subgroups=[];comp=[]
 for task in TARGETS:
  c=sel['selected'][task]['id'];df=pd.read_csv(run/'terminal'/f'{task}_{c}_predictions.csv',dtype={'order_id':'string'});frame=frames[task];assert frame.order_id.tolist()==df.order_id.tolist();subgroups.extend(subgroup_tables(task,frame,df.prediction.to_numpy(),policy['threshold']))
  ss=s.loc[(s.task==task)&(s.candidate==c)].iloc[0];ts=tm.loc[(tm.task==task)&(tm.candidate==c)].iloc[0];tr=pd.read_csv(run/'final_training_metrics.csv');tr=tr.loc[(tr.task==task)&(tr.candidate==c)].iloc[0]
  for metric in (['mae','rmse','r2'] if task=='regression' else ['average_precision','roc_auc','brier']):comp.append({'task':task,'candidate':c,'metric':metric,'fold_training_mean':ss['training_'+metric+'_mean'],'fold_training_sd':ss['training_'+metric+'_sd'],'validation_mean':ss['validation_'+metric+'_mean'],'validation_sd':ss['validation_'+metric+'_sd'],'final_refit_training':tr[metric],'terminal':ts[metric]})
  if task=='regression':
   y=df.target.to_numpy();pred=df.prediction.to_numpy();res=y-pred;fig,ax=plt.subplots(1,3,figsize=(13,4));ax[0].scatter(y,pred,s=3,alpha=.12);lim=np.quantile(np.r_[y,pred],.995);ax[0].plot([0,lim],[0,lim],'k--');ax[0].set(xlabel='Actual days',ylabel='Predicted days',xlim=(0,lim),ylim=(0,lim),title='Axes limited to pooled 99.5th percentile');ax[1].scatter(pred,res,s=3,alpha=.12);ax[1].axhline(0,color='k',ls='--');ax[1].set(xlabel='Predicted days',ylabel='Actual minus predicted days');ax[2].hist(res,bins=70);ax[2].set(xlabel='Residual days',ylabel='Orders');fig.suptitle('Selected regression terminal diagnostics');fig.tight_layout();fig.savefig(figures/'regression_diagnostics.png',dpi=160);plt.close(fig)
  else:
   y=df.target.to_numpy();pred=df.prediction.to_numpy();precision,recall,_=precision_recall_curve(y,pred);fpr,tpr,_=roc_curve(y,pred);fig,ax=plt.subplots(1,3,figsize=(13,4));ax[0].plot(recall,precision);ax[0].axhline(y.mean(),ls='--',color='grey');ax[0].set(xlabel='Recall',ylabel='Precision',title=f'AP={ts.average_precision:.4f}; prevalence={y.mean():.4f}');ax[1].plot(fpr,tpr);ax[1].plot([0,1],[0,1],'k--');ax[1].set(xlabel='False positive rate',ylabel='Recall',title=f'ROC AUC={ts.roc_auc:.4f}');cm=confusion_matrix(y,pred>=policy['threshold']);ax[2].imshow(cm,cmap='Blues');ax[2].set(xticks=[0,1],yticks=[0,1],xlabel='Predicted class',ylabel='Actual class',title=f'Frozen threshold={policy["threshold"]:.5f}')
   for i in range(2):
    for j in range(2):ax[2].text(j,i,str(cm[i,j]),ha='center',va='center',color='white' if cm[i,j]>cm.max()/2 else 'black')
   fig.suptitle('Selected classification terminal diagnostics');fig.tight_layout();fig.savefig(figures/'classification_diagnostics.png',dpi=160);plt.close(fig)
 pd.DataFrame(subgroups).to_csv(run/'selected_subgroups.csv',index=False);pd.DataFrame(comp).to_csv(run/'train_validation_terminal.csv',index=False)
 print(s[['task','candidate','validation_mae_mean','validation_average_precision_mean']].to_string(index=False));print(tm.loc[tm.selected==True].to_string(index=False))
if __name__=='__main__':
 import argparse
 a=argparse.ArgumentParser();a.add_argument('--run',type=Path,required=True);args=a.parse_args();summarize(args.run.resolve())
