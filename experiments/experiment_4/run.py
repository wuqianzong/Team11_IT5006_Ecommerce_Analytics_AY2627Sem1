"""Fixed-catalog development study; terminal outcomes are accessed only after selection freeze."""
from pathlib import Path
import argparse,json,hashlib,time,warnings,sys,importlib.metadata
import pandas as pd,numpy as np,joblib
from sklearn.exceptions import ConvergenceWarning
from src.models.data import ROOT,TARGETS,load_development
from src.models.refinement_temporal import chronological_data
from src.models.experiment4_pipeline import build,predict
from src.models.evaluate import metrics
from src.models.policy import select_cost_threshold,threshold_curve
from src.models.io import ids_digest

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj):p.write_text(json.dumps(obj,indent=2,default=lambda x:x.item() if hasattr(x,'item') else str(x)))
def fit(pipe,frame,task,candidate):
    y=frame[TARGETS[task]].to_numpy()
    if candidate.get('clip'):y=np.minimum(y,candidate['clip'])
    with warnings.catch_warnings(record=True) as ws:
        warnings.simplefilter('always');pipe.fit(frame[candidate['features']],y)
    notes=[{'category':w.category.__name__,'message':str(w.message)} for w in ws]
    if any(issubclass(w.category,ConvergenceWarning) for w in ws):raise RuntimeError('Unconverged fit; retain failed run')
    return notes

def run(out):
    assert not out.exists(),'Preserve existing runs';out.mkdir(parents=True)
    proto_path=ROOT/'experiments/experiment_4/protocol.json';p=json.loads(proto_path.read_text());write(out/'protocol.json',p)
    paths=[Path(__file__),ROOT/'src/models/experiment4_pipeline.py',ROOT/'src/models/refinement_temporal.py',proto_path]
    write(out/'freeze.json',{'protocol_sha256':sha(proto_path),'source_hashes':{str(x.relative_to(ROOT)):sha(x) for x in paths},'packages':{x:importlib.metadata.version(x) for x in ['numpy','pandas','scikit-learn','scipy','joblib']},'started_at':pd.Timestamp.now(tz='Asia/Shanghai').isoformat()})
    data=chronological_data(ROOT,p);data['membership'].to_csv(out/'fold_membership.csv',index=False);data['exclusions'].to_csv(out/'exclusions.csv',index=False)
    write(out/'input_hashes.json',data['input_hashes']);data['terminal_identities'].to_csv(out/'terminal_identities.csv',index=False)
    records=[];attempts=[];oofs={};start=time.time()
    try:
      for task,candidates in p['candidates'].items():
        for c in candidates:
          frames=[]
          for f in range(5):
            tr,va=data['folds'][task,f];job=out/'development'/task/c['id']/f'fold{f}';job.mkdir(parents=True)
            pipe=build(task,c);entry={'task':task,'candidate':c['id'],'fold':f,'status':'started'};attempts.append(entry);write(out/'fit_attempts.json',attempts)
            notes=fit(pipe,tr,task,c);write(job/'warnings.json',notes)
            for partition,frame in [('training',tr),('validation',va)]:
              values=predict(task,pipe,frame[c['features']]);m=metrics(task,frame[TARGETS[task]],values)
              records.append({'task':task,'candidate':c['id'],'cycle':c['cycle'],'fold':f,'partition':partition,**m})
              if partition=='validation':
                df=frame[['order_id','customer_unique_id','prediction_timestamp']].copy();df['target']=frame[TARGETS[task]].to_numpy();df['prediction']=values;df['fold']=f;frames.append(df);df.to_csv(job/'predictions.csv',index=False)
            joblib.dump(pipe,job/'pipeline.joblib',compress=3)
            write(job/'membership.json',{'training_n':len(tr),'validation_n':len(va),'training_ids_sha256':ids_digest(tr.order_id),'validation_ids_sha256':ids_digest(va.order_id)})
            entry['status']='completed';pd.DataFrame(records).to_csv(out/'fold_metrics.csv',index=False)
          oof=pd.concat(frames,ignore_index=True);assert not oof.order_id.duplicated().any();oof.to_csv(out/f'{task}_{c["id"]}_oof.csv',index=False);oofs[task,c['id']]=oof
          print(task,c['id'],'completed',round(time.time()-start,1),'seconds',flush=True)
      fm=pd.DataFrame(records);summaries=[];chosen={};selection={}
      for task,candidates in p['candidates'].items():
        primary='mae' if task=='regression' else 'average_precision';scores=[]
        for c in candidates:
          row={'task':task,'candidate':c['id'],'cycle':c['cycle'],'family':c['family']}
          for part in ['training','validation']:
            rows=fm.loc[(fm.task==task)&(fm.candidate==c['id'])&(fm.partition==part)]
            for m in (['mae','rmse','r2'] if task=='regression' else ['average_precision','roc_auc','brier']):row[part+'_'+m+'_mean']=rows[m].mean();row[part+'_'+m+'_sd']=rows[m].std(ddof=1)
          summaries.append(row);scores.append(row['validation_'+primary+'_mean'])
        best=min(scores) if task=='regression' else max(scores);idx=next(i for i,s in enumerate(scores) if abs(s-best)<=1e-10);chosen[task]=candidates[idx];selection[task]={'candidate':chosen[task]['id'],'primary':primary,'validation_mean':scores[idx]}
      summary=pd.DataFrame(summaries);summary.to_csv(out/'summary.csv',index=False)
      # All decisions freeze before any terminal target reading.
      cls=oofs['classification',chosen['classification']['id']];tau,report=select_cost_threshold(cls.target,cls.prediction,5)
      policy={'kind':'fixed_threshold','positive_class':1,'comparison':'>=','threshold':tau,'cost_ratio_fn_to_fp':5,'OOF_report':report,'selection_population':'selected Experiment 4 chronological OOF; reused development evidence'}
      write(out/'decision_policy.json',policy);threshold_curve(cls.target,cls.prediction).to_csv(out/'threshold_curve.csv',index=False)
      write(out/'selection_freeze.json',{'selected':chosen,'selection_scores':selection,'threshold':tau,'terminal_used_for_selection':False,'summary_sha256':sha(out/'summary.csv')})
      # Fit all fixed references once for train/validation/terminal tables; no terminal-based replacement.
      trainmetrics=[]
      for task,candidates in p['candidates'].items():
        tr=data['final_training'][task];tr[['order_id','customer_unique_id','prediction_timestamp']].to_csv(out/f'{task}_final_training_ids.csv',index=False)
        for c in candidates:
          pipe=build(task,c);notes=fit(pipe,tr,task,c);b=out/'bundles'/task/c['id'];b.mkdir(parents=True);joblib.dump(pipe,b/'pipeline.joblib',compress=3)
          write(b/'feature_schema.json',{'task':task,'predictor_allowlist':c['features'],'version':'experiment-4-v1'});write(b/'configuration.json',c);write(b/'warnings.json',notes)
          write(b/'metadata.json',{'training_n':len(tr),'training_ids_sha256':ids_digest(tr.order_id),'terminal_cutoff':p['terminal_cutoff'],'selected':c['id']==chosen[task]['id']})
          if task=='classification':write(b/'decision_policy.json',policy if c['id']==chosen[task]['id'] else {**policy,'threshold':.5,'selection_population':'default comparison threshold'})
          values=predict(task,pipe,tr[c['features']]);trainmetrics.append({'task':task,'candidate':c['id'],**metrics(task,tr[TARGETS[task]],values,tau if task=='classification' and c['id']==chosen[task]['id'] else .5)})
          assert np.allclose(values[:64],predict(task,joblib.load(b/'pipeline.joblib'),tr[c['features']].iloc[:64]),rtol=1e-12,atol=1e-12)
          write(b/'manifest.json',{'sha256':{f.name:sha(f) for f in b.iterdir() if f.is_file()}})
      pd.DataFrame(trainmetrics).to_csv(out/'final_training_metrics.csv',index=False)
      from src.models.refinement_terminal import terminal_cohorts
      dev,_,_=load_development(ROOT);reviews=pd.read_csv(ROOT/'data/preprocessed/olist_order_reviews_dataset.csv',usecols=['order_id','review_score','review_answer_timestamp'],dtype={'order_id':'string'})
      _,terminal,eligibility=terminal_cohorts(dev,reviews,p['terminal_cutoff']);eligibility.to_csv(out/'terminal_eligibility.csv',index=False);tm=[]
      (out/'terminal').mkdir()
      for task,candidates in p['candidates'].items():
        frame=terminal[task]
        for c in candidates:
          pipe=joblib.load(out/'bundles'/task/c['id']/'pipeline.joblib');values=predict(task,pipe,frame[c['features']]);threshold=tau if task=='classification' and c['id']==chosen[task]['id'] else .5
          m=metrics(task,frame[TARGETS[task]],values,threshold);tm.append({'task':task,'candidate':c['id'],'selected':c['id']==chosen[task]['id'],**m})
          df=frame[['order_id','customer_unique_id','prediction_timestamp']].copy();df['target']=frame[TARGETS[task]].to_numpy();df['prediction']=values;df.to_csv(out/'terminal'/f'{task}_{c["id"]}_predictions.csv',index=False)
      pd.DataFrame(tm).to_csv(out/'terminal_metrics.csv',index=False);write(out/'fit_attempts.json',attempts)
      write(out/'completion.json',{'status':'passed','fold_fits':len(attempts),'final_fits':sum(len(x) for x in p['candidates'].values()),'selected':selection,'threshold':tau,'elapsed_seconds':time.time()-start,'terminal_is_previously_inspected':True,'terminal_used_for_selection':False})
      print(json.dumps(selection),flush=True)
    except Exception as e:
      write(out/'failure.json',{'error':repr(e),'attempts':attempts,'elapsed_seconds':time.time()-start});raise
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);args=a.parse_args();run(args.output.resolve())
