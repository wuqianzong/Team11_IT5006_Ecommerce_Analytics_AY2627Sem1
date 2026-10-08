"""Read-only diagnostic evidence synthesis; does not fit predictive models."""
import importlib
import json
import subprocess
import sys
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from scipy import sparse
from . import diagnostics
from .diagnostics import ROOT, HERE, PROTOCOL, prepare, event, digest
from experiments.refinement_cycle1.paths import run_root
from src.models.evaluate import metrics
from src.models.io import write_json
from src.features.contract import PREDICTOR_ALLOWLIST

OUT=run_root()/'initial_reference/results'
AUDIT=run_root()/'initial_reference/audit'
def main():
    diagnostics.LOG = OUT/'process_log.jsonl'
    done=json.loads((OUT/'run_completion.json').read_text())
    if done['new_predictive_fits']!=255 or done['terminal_evaluated']:
        raise ValueError('Incomplete/incorrect diagnostic run')
    AUDIT.mkdir(exist_ok=False)
    protocol=json.loads(PROTOCOL.read_text())
    records=pd.read_csv(OUT/'fold_metrics.csv')
    val=records.loc[records.partition.eq('validation')]
    for _, group in val.groupby(['experiment','task','candidate']):
        if set(group.fold)!={0,1,2,3,4}:raise ValueError('Incomplete fold scores')
    summary=val.groupby(['experiment','task','candidate','family'])[['mae','rmse','r2','average_precision','roc_auc','brier']].agg(['mean','std']).reset_index()
    summary.columns=['_'.join(c).strip('_') if isinstance(c,tuple) else c for c in summary.columns]
    summary.to_csv(AUDIT/'comparison_summary.csv',index=False)
    selection=json.loads((OUT/'development_selection.json').read_text())
    paired=[];subgroups=[];coverage=[];pooled=[]
    controls={'E02':'E01','E03':'E01','E04':'E01','E05':'E04','E06':'E05','E07':'E01','E08':'E05'}
    for (exp,task,candidate),group in val.groupby(['experiment','task','candidate']):
        predictions=[]
        for fold in range(5):
            path=OUT/'jobs'/f'{exp}-{task}-{candidate}-fold{fold}'
            pred=pd.read_csv(path/'validation_predictions.csv',dtype={'order_id':'string'})
            pred['fold']=fold;predictions.append(pred)
            for groupname,mask in [('multi_item',pred.n_items.gt(1)),('single_item',pred.n_items.eq(1)),
                                   ('incomplete_record',~pred.complete_record),('complete_record',pred.complete_record)]:
                if mask.any():
                    part=pred.loc[mask]
                    values=metrics(task,part.target,part.prediction)
                    reliable=task=='regression' or (len(part)>=100 and values['positives']>=20 and values['negatives']>=20)
                    subgroups.append(dict(experiment=exp,task=task,candidate=candidate,fold=fold,subgroup=groupname,
                                          AP_stable_enough_for_planned_rule=reliable,**values))
            for state,part in pred.groupby('customer_state'):
                values=metrics(task,part.target,part.prediction)
                subgroups.append(dict(experiment=exp,task=task,candidate=candidate,fold=fold,subgroup='customer_state:'+state,
                    AP_stable_enough_for_planned_rule=task=='regression' or (len(part)>=100 and values['positives']>=20 and values['negatives']>=20),**values))
            if task=='regression' and pred.target.gt(30).any():
                part=pred.loc[pred.target.gt(30)]
                subgroups.append(dict(experiment=exp,task=task,candidate=candidate,fold=fold,subgroup='observed_over_30_days',
                    AP_stable_enough_for_planned_rule=True,**metrics(task,part.target,part.prediction)))
            if exp in controls:
                ref=controls[exp]
                rp=pd.read_csv(OUT/'jobs'/f'{ref}-{task}-{candidate}-fold{fold}'/'validation_predictions.csv',dtype={'order_id':'string'})
                if not pred.order_id.equals(rp.order_id) or not pred.target.equals(rp.target):
                    raise ValueError('Comparison populations/targets mismatch')
                key='mae' if task=='regression' else 'average_precision'
                now=metrics(task,pred.target,pred.prediction)[key];before=metrics(task,rp.target,rp.prediction)[key]
                paired.append(dict(experiment=exp,reference=ref,task=task,candidate=candidate,fold=fold,
                                   metric=key,reference_score=before,candidate_score=now,
                                   degradation=now-before if task=='regression' else before-now))
            # Inspect actual trained mappings and quantify unseen inputs per fold.
            config=json.loads((path/'configuration.json').read_text())
            coverage.append(dict(experiment=exp,task=task,candidate=candidate,fold=fold,training_n=config['training_n'],
                                 excluded_training_n=config['original_training_n']-config['training_n'],validation_n=len(pred)))
        all_pred=pd.concat(predictions,ignore_index=True)
        if all_pred.order_id.duplicated().any():raise ValueError('Repeated OOF order within candidate')
        pooled.append(dict(experiment=exp,task=task,candidate=candidate,**metrics(task,all_pred.target,all_pred.prediction)))
    pd.DataFrame(paired).to_csv(AUDIT/'paired_fold_differences.csv',index=False)
    pd.DataFrame(subgroups).to_csv(AUDIT/'subgroup_metrics.csv',index=False)
    pd.DataFrame(coverage).to_csv(AUDIT/'coverage.csv',index=False)
    pd.DataFrame(pooled).to_csv(AUDIT/'pooled_oof_metrics.csv',index=False)
    # Reconstruct the supplemental paired/family tables from the same saved
    # scores. These are descriptive diagnostics, not extra predictive trials.
    sg=pd.DataFrame(subgroups)
    indexed=sg.set_index(['experiment','task','candidate','fold','subgroup'])
    paired_groups=[]
    for r in sg.itertuples():
        if r.experiment not in controls:continue
        ref=controls[r.experiment]
        before=indexed.loc[(ref,r.task,r.candidate,r.fold,r.subgroup)]
        key='mae' if r.task=='regression' else 'average_precision'
        old=before[key];new=getattr(r,key)
        delta=new-old if r.task=='regression' else old-new
        reliable=bool(r.AP_stable_enough_for_planned_rule and before.AP_stable_enough_for_planned_rule)
        threshold=.5 if r.task=='regression' else .02
        paired_groups.append(dict(experiment=r.experiment,reference=ref,task=r.task,candidate=r.candidate,fold=r.fold,
                                  subgroup=r.subgroup,n=r.n,metric=key,reference_score=old,candidate_score=new,
                                  degradation=delta,threshold=threshold,material_warning=bool(reliable and delta>threshold),
                                  AP_reliable_for_rule=reliable,small_regression_group=bool(r.task=='regression' and r.n<100)))
    pd.DataFrame(paired_groups).to_csv(AUDIT/'paired_subgroup_warnings.csv',index=False)
    family=[]
    for (task,candidate),group in val[val.experiment=='E01'].groupby(['task','candidate']):
        spec=next(c for c in protocol['candidates'][task] if c['id']==candidate)
        if 'baseline_model' in spec:continue
        reference='baseline_linear' if spec['family'] in {'ridge','logistic','linear'} else 'baseline_tree'
        key='mae' if task=='regression' else 'average_precision'
        for r in group.itertuples():
            old=val[(val.experiment=='E01')&(val.task==task)&(val.candidate==reference)&(val.fold==r.fold)].iloc[0][key]
            new=getattr(r,key)
            family.append(dict(task=task,candidate=candidate,reference=reference,fold=r.fold,metric=key,
                               improvement=old-new if task=='regression' else new-old))
    pd.DataFrame(family).to_csv(AUDIT/'within_family_baseline_differences.csv',index=False)
    # Independent fresh cohort reconstruction validates count/ID lineage again.
    folds,_=prepare(make_reconstruction_dir(),protocol)
    reload_checks=[]
    for path in sorted((OUT/'jobs').iterdir()):
        completion=json.loads((path/'completion.json').read_text())
        if digest(path/'pipeline.joblib')!=completion['pipeline_sha256']:
            raise ValueError('Saved pipeline checksum mismatch')
        config=json.loads((path/'configuration.json').read_text())
        if config['fold']!=0:continue
        model=joblib.load(path/'pipeline.joblib')
        va=folds[config['task'],0][1]
        values=model.predict(va[PREDICTOR_ALLOWLIST]) if config['task']=='regression' else model.predict_proba(va[PREDICTOR_ALLOWLIST])[:,list(model.named_steps['model'].classes_).index(1)]
        saved=pd.read_csv(path/'validation_predictions.csv')
        if not np.allclose(values,saved.prediction,rtol=1e-12,atol=1e-12):
            raise ValueError('Reload predictions mismatch')
        reload_checks.append({'job':path.name,'rows':len(va),'predictions_match':True})
    write_json(reload_checks,AUDIT/'reload_verification.json')
    design=[];encoding=[]
    for task in ['regression','classification']:
        linear=next(c for c in selection['sensitivity_representatives'][task] if c['family'] in {'linear','ridge','logistic'})
        for exp in ['E01','E02','E03','E04','E05','E06','E07']:
            for fold in range(5):
                tr,va=folds[task,fold]
                path=OUT/'jobs'/f'{exp}-{task}-{linear["id"]}-fold{fold}'
                model=joblib.load(path/'pipeline.joblib')
                normalized=model.named_steps['inputs'].transform(va[PREDICTOR_ALLOWLIST])
                if 'rare' in model.named_steps:normalized=model.named_steps['rare'].transform(normalized)
                pre=model.named_steps['preprocess']
                cat=pre.named_transformers_['categorical'];cols=next(c for n,_,c in pre.transformers_ if n=='categorical')
                for i,col in enumerate(cols):
                    encoding.append(dict(experiment=exp,task=task,fold=fold,column=col,validation_n=len(va),
                                         unseen_n=int((~normalized[col].isin(cat.categories_[i])).sum())))
                if exp not in ['E01','E05','E06']:continue
                X=model[:-1].transform(tr[PREDICTOR_ALLOWLIST]);X=X.toarray() if sparse.issparse(X) else np.asarray(X)
                names=model[:-1].get_feature_names_out()
                sd=X.std(axis=0);constant=sd<=1e-12
                Z=(X[:,~constant]-X[:,~constant].mean(axis=0))/sd[~constant]
                # VIF with intercept: centred normalized predictor Gram matrix.
                corr=(Z.T@Z)/len(Z);eigen,vectors=np.linalg.eigh(corr)
                tol=max(corr.shape)*np.finfo(float).eps*max(float(eigen.max()),1.)*100
                rank=int((eigen>tol).sum());null=vectors[:,eigen<=tol]
                inverse=(vectors[:,eigen>tol]/eigen[eigen>tol])@vectors[:,eigen>tol].T
                null_loading=np.sum(null**2,axis=1) if null.size else np.zeros(len(corr))
                vifs={name:('infinite_rank_deficiency' if null_loading[i]>1e-8 else float(inverse[i,i])) for i,name in enumerate(names[~constant])}
                result=dict(experiment=exp,task=task,fold=fold,training_n=len(tr),
                            transformed_columns=len(names),nonconstant_columns=int((~constant).sum()),rank=rank,
                            constants=names[constant].tolist(),intercept='Included implicitly by centering; constants excluded from VIF',
                            reference_coding='drop_first',condition_number='infinite' if rank<len(corr) else float(np.sqrt(eigen.max()/eigen.min())),VIF=vifs)
                design.append(result)
    write_json(design,AUDIT/'linear_design_diagnostics.json')
    pd.DataFrame(encoding).to_csv(AUDIT/'linear_unseen_category_counts.csv',index=False)
    # Audit preterminal original regression extremes, including explicitly excluded rows.
    from src.models.data import load_development
    dev,_,_=load_development(ROOT)
    cutoff=pd.Timestamp(protocol['terminal_cutoff'])
    sample=dev.loc[pd.to_datetime(dev.prediction_timestamp).lt(cutoff)&dev.eligible_regression.eq(1)&dev.lead_days.gt(100)].copy()
    orders=pd.read_csv(ROOT/'data/preprocessed/olist_orders_dataset.csv',dtype={'order_id':'string'})
    raw=sample[['order_id','lead_days','prediction_timestamp']].merge(orders,on='order_id',validate='one_to_one')
    for col in ['order_purchase_timestamp','order_approved_at','order_delivered_carrier_date','order_delivered_customer_date']:
        raw[col]=pd.to_datetime(raw[col],errors='coerce')
    raw['reconstructed_lead_days']=(raw.order_delivered_customer_date-raw.order_purchase_timestamp).dt.total_seconds()/86400
    raw['target_formula_matches']=np.isclose(raw.lead_days,raw.reconstructed_lead_days)
    raw['approval_before_purchase']=raw.order_approved_at.lt(raw.order_purchase_timestamp)
    raw['carrier_before_approval']=raw.order_delivered_carrier_date.lt(raw.order_approved_at)
    raw['delivery_before_carrier']=raw.order_delivered_customer_date.lt(raw.order_delivered_carrier_date)
    raw.to_csv(AUDIT/'extreme_source_audit.csv',index=False)
    test_command=[sys.executable,'-m','experiments.refinement_cycle1.initial_reference.test_diagnostics']
    test=subprocess.run(test_command,cwd=ROOT,capture_output=True,text=True)
    (AUDIT/'structural_test_stdout.txt').write_text(test.stdout)
    (AUDIT/'structural_test_stderr.txt').write_text(test.stderr)
    if test.returncode:raise ValueError('Structural tests failed')
    checks={'255_jobs_complete':len(list((OUT/'jobs').glob('*/completion.json')))==255,
            'all_comparisons_same_population':True,'structural_tests_passed':True,'terminal_scoring_not_performed':True,
            'all_255_pipeline_checksums_verified':True,'all_51_first_fold_pipelines_reload_and_match':len(reload_checks)==51}
    if not all(checks.values()):raise ValueError(str(checks))
    write_json({'status':'diagnostic_evidence_ready_for_review_not_adoption','checks':checks,'new_predictive_fits':255,
                'portability_note':'Private report-preservation/worktree checks are not scientific reconstruction dependencies.',
                'auxiliary_method':'Eigenanalysis of actual fold-training standardized correlation matrices; no extra predictive fits.',
                'prediction_warning_policy':'Unknown-category warnings retained in stderr; unseen counts quantified from actual encoders. No refit on validation.',
                'terminal_evaluation':False,'holdout_evaluation':False,'report_or_contract_changes':False},AUDIT/'verification.json')
    event('completion','Validate diagnostic evidence, subgroup/paired scores and actual linear designs.','Checks passed; results ready for human decision and impact analysis; no adoption.',evidence_paths_override=[str(AUDIT/'verification.json')])
    print('Diagnostic evidence verification passed.')

def make_reconstruction_dir():
    p=AUDIT/'cohort_reconstruction';p.mkdir();return p

if __name__=='__main__':main()
