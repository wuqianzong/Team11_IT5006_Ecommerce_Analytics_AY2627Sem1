"""Independent numerical and membership audit of a completed fixed-catalog study."""
from pathlib import Path
import argparse,json,hashlib
import pandas as pd,numpy as np,joblib
from sklearn.metrics import mean_absolute_error,mean_squared_error,r2_score,average_precision_score,roc_auc_score,brier_score_loss
from src.models.data import ROOT,TARGETS
from src.models.refinement_temporal import chronological_data
from src.models.experiment4_pipeline import predict
from src.models.io import ids_digest

def verify(run):
    p=json.loads((run/'protocol.json').read_text());frozen=json.loads((run/'freeze.json').read_text());data=chronological_data(ROOT,p);fm=pd.read_csv(run/'fold_metrics.csv');summary=pd.read_csv(run/'summary.csv');selection=json.loads((run/'selection_freeze.json').read_text());assert json.loads((run/'completion.json').read_text())['status']=='passed'
    for name,h in frozen['source_hashes'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    keys=['task','fold','role','order_id'];old=pd.read_csv(run/'fold_membership.csv',dtype={'order_id':'string'});assert old.sort_values(keys).reset_index(drop=True).equals(data['membership'].astype({'order_id':'string'}).sort_values(keys).reset_index(drop=True))
    checked=0;largest=0
    for task,candidates in p['candidates'].items():
      for c in candidates:
        vals=[]
        for fold in range(5):
          tr,va=data['folds'][task,fold];folder=run/'development'/task/c['id']/f'fold{fold}';meta=json.loads((folder/'membership.json').read_text());assert meta['training_ids_sha256']==ids_digest(tr.order_id);assert meta['validation_ids_sha256']==ids_digest(va.order_id)
          assert set(tr.customer_unique_id).isdisjoint(va.customer_unique_id);pipe=joblib.load(folder/'pipeline.joblib');preds=predict(task,pipe,va[c['features']]);saved=pd.read_csv(folder/'predictions.csv',dtype={'order_id':'string'});assert saved.order_id.tolist()==va.order_id.tolist();assert np.allclose(preds,saved.prediction,rtol=1e-12,atol=1e-12)
          y=va[TARGETS[task]];m={'mae':mean_absolute_error(y,preds),'rmse':np.sqrt(mean_squared_error(y,preds)),'r2':r2_score(y,preds)} if task=='regression' else {'average_precision':average_precision_score(y,preds),'roc_auc':roc_auc_score(y,preds),'brier':brier_score_loss(y,preds)}
          row=fm.loc[(fm.task==task)&(fm.candidate==c['id'])&(fm.fold==fold)&(fm.partition=='validation')].iloc[0]
          for k,v in m.items():largest=max(largest,abs(v-row[k]));assert np.isclose(v,row[k],rtol=1e-10,atol=1e-10)
          vals.append(m['mae' if task=='regression' else 'average_precision']);checked+=1
        primary='mae' if task=='regression' else 'average_precision';sr=summary.loc[(summary.task==task)&(summary.candidate==c['id'])].iloc[0];assert np.isclose(np.mean(vals),sr['validation_'+primary+'_mean'],rtol=1e-10,atol=1e-10);assert np.isclose(np.std(vals,ddof=1),sr['validation_'+primary+'_sd'],rtol=1e-10,atol=1e-10)
        b=run/'bundles'/task/c['id'];manifest=json.loads((b/'manifest.json').read_text())['sha256'];assert all(hashlib.sha256((b/n).read_bytes()).hexdigest()==h for n,h in manifest.items())
      part=summary.loc[summary.task==task];primary='validation_mae_mean' if task=='regression' else 'validation_average_precision_mean';best=part[primary].min() if task=='regression' else part[primary].max();assert np.isclose(selection['selection_scores'][task]['validation_mean'],best,rtol=1e-10,atol=1e-10)
    assert not selection['terminal_used_for_selection']
    selected=selection['selected']['classification']['id'];oof=pd.read_csv(run/f'classification_{selected}_oof.csv',float_precision='round_trip');policy=json.loads((run/'decision_policy.json').read_text());threshold=policy['threshold'];cost=int(((oof.prediction>=threshold)&(oof.target==0)).sum()+5*((oof.prediction<threshold)&(oof.target==1)).sum());curve=pd.read_csv(run/'threshold_curve.csv',float_precision='round_trip');loss=curve.fp+5*curve.fn;assert cost==loss.min();assert np.isclose(threshold,curve.loc[loss==loss.min(),'threshold'].max())
    # Recompute terminal metrics solely from saved results, after fixed selection.
    tm=pd.read_csv(run/'terminal_metrics.csv');terminal_checks=0
    for _,row in tm.iterrows():
      df=pd.read_csv(run/'terminal'/f'{row.task}_{row.candidate}_predictions.csv');y=df.target;pred=df.prediction
      value=mean_absolute_error(y,pred) if row.task=='regression' else average_precision_score(y,pred);key='mae' if row.task=='regression' else 'average_precision';assert np.isclose(value,row[key],rtol=1e-10,atol=1e-10);terminal_checks+=1
    report={'status':'passed','checked_validation_folds':checked,'terminal_prediction_files_checked':terminal_checks,'maximum_validation_metric_difference':largest,'memberships_match':True,'selection_matches_development_rule':True,'threshold_matches_development_cost_minimum':True,'no_new_fits':True};(run/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--run',type=Path,required=True);args=a.parse_args();verify(args.run.resolve())
