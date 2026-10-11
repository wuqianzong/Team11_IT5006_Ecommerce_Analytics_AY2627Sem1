"""Derive self-contained report evidence from the accepted run without model fits.

All tables use the fixed memberships and original, unclipped evaluation targets.
Permutation diagnostics use each selected saved fold model on its full validation
fold, three shuffles per raw input, seed 42. They do not change model selection.
"""
from pathlib import Path
import argparse
import hashlib
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, average_precision_score, roc_auc_score, brier_score_loss, confusion_matrix
from src.models.data import ROOT
from src.models.experiment4_pipeline import predict
from experiments.experiment_4.cohort_summary import summarize as cohort_summary


def generate(run, output):
    if output.exists():
        raise FileExistsError('Use a fresh output directory')
    hashes = json.loads((run / 'input_hashes.json').read_text())
    source = ROOT / 'data/business/ml/orders_ml_features.csv'
    assert hashlib.sha256(source.read_bytes()).hexdigest() == hashes['orders_ml_features.csv']
    base = pd.read_csv(source, dtype={'order_id': 'string'}, float_precision='round_trip').set_index('order_id', verify_integrity=True)
    protocol = json.loads((run / 'protocol.json').read_text())
    selected = json.loads((run / 'selection_freeze.json').read_text())['selected']
    policy = json.loads((run / 'decision_policy.json').read_text())
    threshold = policy['threshold']
    summary = pd.read_csv(run / 'summary.csv', float_precision='round_trip')
    folds = pd.read_csv(run / 'fold_metrics.csv', float_precision='round_trip')
    terminal_metrics = pd.read_csv(run / 'terminal_metrics.csv', float_precision='round_trip')
    output.mkdir(parents=True)
    cohort_summary(run, output / 'cohorts')
    figures = output / 'figures'; figures.mkdir()
    catalogue, importance, fold_support, checked = [], [], [], []
    for task in ['regression', 'classification']:
        primary = 'mae' if task == 'regression' else 'average_precision'
        measures = ['mae', 'rmse', 'r2'] if task == 'regression' else ['average_precision', 'roc_auc', 'brier']
        for i, candidate in enumerate(protocol['candidates'][task], 1):
            name = candidate['id']; label = ('R' if task == 'regression' else 'C') + f'{i:02d}'
            s = summary[(summary.task == task) & (summary.candidate == name)].iloc[0]
            t = terminal_metrics[(terminal_metrics.task == task) & (terminal_metrics.candidate == name)].iloc[0]
            record = dict(task=task, label=label, candidate=name, cycle=candidate['cycle'], family=candidate['family'], n_features=len(candidate['features']), input_log=candidate.get('input_log', False), target_log=candidate.get('target_log', False), cap=candidate.get('clip', ''), selected=name == selected[task]['id'])
            record.update(s.drop(['task', 'candidate', 'cycle', 'family']).to_dict())
            record.update({'terminal_' + metric: t[metric] for metric in measures})
            catalogue.append(record)
            oof = pd.read_csv(run / f'{task}_{name}_oof.csv', float_precision='round_trip')
            terminal = pd.read_csv(run / 'terminal' / f'{task}_{name}_predictions.csv', float_precision='round_trip')
            assert not oof.order_id.duplicated().any() and not terminal.order_id.duplicated().any()
            def metrics(frame):
                y, p = frame.target, frame.prediction
                if task == 'regression':
                    return dict(mae=mean_absolute_error(y,p), rmse=np.sqrt(mean_squared_error(y,p)), r2=r2_score(y,p))
                return dict(average_precision=average_precision_score(y,p), roc_auc=roc_auc_score(y,p), brier=brier_score_loss(y,p))
            for metric, value in metrics(terminal).items():
                assert np.isclose(value, t[metric], rtol=1e-11, atol=1e-12)
            for fold in range(5):
                frame = oof[oof.fold == fold]
                saved = folds[(folds.task == task) & (folds.candidate == name) & (folds.fold == fold) & (folds.partition == 'validation')].iloc[0]
                for metric, value in metrics(frame).items():
                    assert np.isclose(value, saved[metric], rtol=1e-11, atol=1e-12)
            checked.append({'task': task, 'candidate': name, 'validated_terminal_and_folds': True})
        name = selected[task]['id']; config = next(c for c in protocol['candidates'][task] if c['id'] == name)
        oof = pd.read_csv(run / f'{task}_{name}_oof.csv', dtype={'order_id': 'string'}, float_precision='round_trip')
        for fold in range(5):
            frame = oof[oof.fold == fold]
            # Counts and boundary audit are taken from the task-wide split audit.
            a = pd.read_csv(run / 'split_audit.csv'); a = a[(a.task == task) & (a.fold == fold)]
            tr, va = a[a.role == 'training'].iloc[0], a[a.role == 'validation'].iloc[0]
            fold_support.append(dict(task=task, fold=fold+1, training_n=int(tr.n), validation_n=int(va.n), training_customers=int(tr.customers), validation_customers=int(va.customers), validation_target_mean=va.target_mean, validation_positives=int(frame.target.sum()) if task == 'classification' else None))
            pipe = joblib.load(run / 'development' / task / name / f'fold{fold}' / 'pipeline.joblib')
            X = base.loc[frame.order_id, config['features']].copy()
            prediction = predict(task, pipe, X)
            assert np.allclose(prediction, frame.prediction, rtol=1e-10, atol=1e-10)
            score = mean_absolute_error(frame.target, prediction) if task == 'regression' else average_precision_score(frame.target, prediction)
            for index, feature in enumerate(config['features']):
                for repeat in range(3):
                    rng = np.random.default_rng(42 + fold*1000 + index*10 + repeat)
                    shuffled = X.copy(); shuffled[feature] = rng.permutation(X[feature].to_numpy())
                    p = predict(task, pipe, shuffled)
                    changed = mean_absolute_error(frame.target, p) if task == 'regression' else average_precision_score(frame.target, p)
                    importance.append(dict(task=task, fold=fold+1, feature=feature, repeat=repeat+1, importance=changed-score if task == 'regression' else score-changed))
    pd.DataFrame(catalogue).to_csv(output / 'catalogue.csv', index=False)
    pd.DataFrame(fold_support).to_csv(output / 'fold_support.csv', index=False)
    imp = pd.DataFrame(importance); imp.to_csv(output / 'permutation_details.csv', index=False)
    fi = imp.groupby(['task','feature','fold'], sort=False).importance.mean().reset_index()
    si = fi.groupby(['task','feature'], sort=False).importance.agg(['mean','std']).reset_index()
    si.to_csv(output / 'permutation_summary.csv', index=False)
    fig, axes = plt.subplots(1,2, figsize=(12,5))
    for task, ax in zip(['regression','classification'], axes):
        d=si[si.task == task].sort_values('mean')
        ax.barh(d.feature, d['mean'], xerr=d['std'], color='#357a9e', capsize=2)
        ax.axvline(0, color='black', linewidth=.7)
        ax.set_title(task.capitalize() + ' selected model')
        ax.set_xlabel('Increase in MAE (days)' if task == 'regression' else 'Decrease in AP')
    fig.tight_layout();fig.savefig(figures/'permutation.png', dpi=180);plt.close(fig)
    policy_rows, calibration, errors = [], [], []
    for partition in ['OOF','terminal']:
        path = run / 'classification_expanded_inputlog_regularized_oof.csv' if partition == 'OOF' else run / 'terminal/classification_expanded_inputlog_regularized_predictions.csv'
        d = pd.read_csv(path, float_precision='round_trip'); y=d.target.to_numpy(); p=d.prediction.to_numpy()
        for label, predicted in [('No alerts', np.zeros(len(d), dtype=int)), ('Threshold 0.5', (p >= .5).astype(int)), ('Frozen threshold', (p >= threshold).astype(int)), ('All alerts', np.ones(len(d), dtype=int))]:
            tn,fp,fn,tp=confusion_matrix(y,predicted,labels=[0,1]).ravel()
            policy_rows.append(dict(partition=partition, policy=label, n=len(d), tn=int(tn), fp=int(fp), fn=int(fn), tp=int(tp), alerts=int(tp+fp), precision=tp/(tp+fp) if tp+fp else np.nan, recall=tp/(tp+fn), f1=2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else np.nan, accuracy=(tp+tn)/len(d), alert_pct=100*(tp+fp)/len(d), loss=int(fp+5*fn)))
        bins = np.minimum((p*10).astype(int),9)
        for b in range(10):
            mask=bins==b
            calibration.append(dict(partition=partition, bin=f'{b/10:.1f}–{(b+1)/10:.1f}', n=int(mask.sum()), positives=int(y[mask].sum()), mean_probability=float(p[mask].mean()) if mask.any() else np.nan, observed_rate=float(y[mask].mean()) if mask.any() else np.nan))
    pd.DataFrame(policy_rows).to_csv(output/'policy_comparison.csv',index=False)
    cal=pd.DataFrame(calibration);cal.to_csv(output/'calibration.csv',index=False)
    curve=pd.read_csv(run/'threshold_curve.csv',float_precision='round_trip')
    fig,axes=plt.subplots(1,2,figsize=(10.5,4))
    axes[0].plot(curve.threshold,curve.fp+5*curve.fn,color='#357a9e')
    axes[0].axhline(40250, color='gray',linestyle='--',label='No alerts')
    axes[0].scatter([threshold],[35446],color='#b64c39',label='Frozen minimum')
    axes[0].set(xlim=(0,1),xlabel='Threshold',ylabel='OOF illustrative loss FP + 5 FN',title='Development policy selection');axes[0].legend(fontsize=8)
    for part in ['OOF','terminal']:
        d=cal[(cal.partition==part)&(cal.n>0)]
        axes[1].plot(d.mean_probability,d.observed_rate,'o-',label=part)
    axes[1].plot([0,1],[0,1],'--',color='gray');axes[1].set(xlim=(0,1),ylim=(0,1),xlabel='Mean predicted probability',ylabel='Observed detractor share',title='Fixed 0.1 width reliability bins');axes[1].legend()
    fig.tight_layout();fig.savefig(figures/'policy_calibration.png',dpi=180);plt.close(fig)
    for part in ['OOF','terminal']:
        path=run/'regression_expanded_log_forest_leaf50_oof.csv' if part=='OOF' else run/'terminal/regression_expanded_log_forest_leaf50_predictions.csv'
        d=pd.read_csv(path,float_precision='round_trip');error=d.prediction-d.target;ae=error.abs()
        errors.append(dict(partition=part,n=len(d),bias=error.mean(),mae=ae.mean(),median_absolute_error=ae.median(),p90_absolute_error=ae.quantile(.9),p95_absolute_error=ae.quantile(.95),p99_absolute_error=ae.quantile(.99),max_absolute_error=ae.max(),negative_predictions=int((d.prediction<0).sum()),actual_over_60=int((d.target>60).sum()),actual_over_60_mae=ae[d.target>60].mean()))
    pd.DataFrame(errors).to_csv(output/'regression_errors.csv',index=False)
    exclusions=pd.read_csv(run/'exclusions.csv')
    exclusions.groupby(['task','fold','role','reasons'],dropna=False).size().rename('n').reset_index().to_csv(output/'exclusion_counts.csv',index=False)
    eligibility=pd.read_csv(run/'terminal_eligibility.csv')
    eligibility.groupby(['task','included','reason']).size().rename('n').reset_index().to_csv(output/'terminal_eligibility_counts.csv',index=False)
    # Additional slices supplement the existing selected-subgroup table.
    extra=[]
    for task in ['regression','classification']:
        name=selected[task]['id'];d=pd.read_csv(run/'terminal'/f'{task}_{name}_predictions.csv',dtype={'order_id':'string'},float_precision='round_trip')
        x=base.loc[d.order_id].reset_index(drop=True);d=d.reset_index(drop=True)
        groups={'basket':pd.cut(x.n_items,[0,1,3,np.inf],labels=['1 item','2-3 items','4+ items'])}
        if task=='regression':
            groups['distance']=pd.cut(x.distance_km_max,[-np.inf,250,1000,np.inf],labels=['≤250 km','250–1000 km','>1000 km']).astype('object').fillna('Missing distance')
        for dimension,group in groups.items():
            for label in group.unique():
                mask=group==label;y=d.target[mask];p=d.prediction[mask]
                rec=dict(task=task,dimension=dimension,subgroup=label,n=len(y))
                if task=='regression':rec.update(mae=mean_absolute_error(y,p),rmse=np.sqrt(mean_squared_error(y,p)),r2=r2_score(y,p))
                else:
                    tn,fp,fn,tp=confusion_matrix(y,p>=threshold,labels=[0,1]).ravel()
                    rec.update(positives=int(y.sum()),average_precision=average_precision_score(y,p) if y.nunique()==2 else np.nan,precision_1=tp/(tp+fp) if tp+fp else np.nan,recall_1=tp/(tp+fn) if tp+fn else np.nan,illustrative_cost_5_to_1=int(fp+5*fn))
                extra.append(rec)
    pd.DataFrame(extra).to_csv(output/'extra_subgroups.csv',index=False)
    # Raw skewness and target-tail charts: training IDs, no outcome filtering.
    ids=pd.read_csv(run/'regression_final_training_ids.csv',dtype={'order_id':'string'})
    train=base.loc[ids.order_id]
    fig,axes=plt.subplots(2,3,figsize=(11,6))
    for ax,feature in zip(axes.flat,['total_price','total_freight','distance_km_max']):
        v=train[feature].dropna();cut=v.quantile(.99);ax.hist(v[v<=cut],bins=40,color='#357a9e');ax.set_title(feature+' raw ≤99th pct');ax.set_ylabel('Orders')
    for ax,feature in zip(axes.flat[3:],['total_price','total_freight','distance_km_max']):
        ax.hist(np.log1p(train[feature].dropna()),bins=40,color='#b64c39');ax.set_title(feature+' log1p all observed');ax.set_ylabel('Orders')
    fig.tight_layout();fig.savefig(figures/'input_skewness.png',dpi=180);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,3.7))
    for ax,feature in zip(axes,['lead_days','lead_days']):
        v=train.lead_days if ax==axes[0] else np.log1p(train.lead_days)
        ax.hist(v,bins=70,color='#357a9e');ax.set(xlabel='Days' if ax==axes[0] else 'log1p(days)',ylabel='Orders')
    axes[0].axvline(60,color='#b64c39',linestyle='--',label='Training cap candidate');axes[0].legend(fontsize=8)
    fig.tight_layout();fig.savefig(figures/'target_tail.png',dpi=180);plt.close(fig)
    counts={'raw_inputs':{},'training_labels_over_60':int((train.lead_days>60).sum())}
    for feature in ['total_price','total_freight','distance_km_max']:
        v=train[feature].dropna();counts['raw_inputs'][feature]={'observed':len(v),'missing':int(train[feature].isna().sum()),'raw_skew':v.skew(),'log1p_skew':np.log1p(v).skew(),'raw_chart_p99':v.quantile(.99),'hidden_from_raw_chart':int((v>v.quantile(.99)).sum())}
    (output/'chart_statistics.json').write_text(json.dumps(counts,indent=2))
    supplement(run, output)
    manifest={str(p.relative_to(output)):hashlib.sha256(p.read_bytes()).hexdigest() for p in output.rglob('*') if p.is_file()}
    (output/'verification.json').write_text(json.dumps(dict(status='passed',no_new_fits=True,feature_input_sha256=hashes['orders_ml_features.csv'],verified_candidates=checked,permutation={'folds':5,'repeats':3,'full_validation_rows':True,'seed_rule':'42 + zero-based fold*1000 + feature_index*10 + repeat'},output_sha256=manifest),indent=2))
    print(f'Self-contained report tables and charts saved to {output}; all 26 candidates independently checked; no models fitted')


def supplement(run, output):
    """Readable single-task figures and full selected-input cohort metadata."""
    base=pd.read_csv(ROOT/'data/business/ml/orders_ml_features.csv',dtype={'order_id':'string'},float_precision='round_trip').set_index('order_id')
    selected=json.loads((run/'selection_freeze.json').read_text())['selected']
    protocol=json.loads((run/'protocol.json').read_text())
    catalogue=pd.read_csv(output/'catalogue.csv')
    importance=pd.read_csv(output/'permutation_summary.csv')
    numeric,categorical=[],[]
    for task in ['regression','classification']:
        config=next(c for c in protocol['candidates'][task] if c['id']==selected[task]['id'])
        for partition in ['training','terminal']:
            path=run/f'{task}_final_training_ids.csv' if partition=='training' else run/'terminal'/f'{task}_{selected[task]["id"]}_predictions.csv'
            ids=pd.read_csv(path,dtype={'order_id':'string'});x=base.loc[ids.order_id]
            for feature in config['features']:
                v=x[feature]
                if feature.endswith('state'):
                    for label,n in v.value_counts(dropna=False).items():
                        categorical.append(dict(task=task,partition=partition,feature=feature,value=label,n=int(n),share_pct=100*n/len(v)))
                else:
                    numeric.append(dict(task=task,partition=partition,feature=feature,n=len(v),mean=v.mean(),median=v.median(),sd=v.std(ddof=1),min=v.min(),max=v.max(),skew=v.skew(),missing_pct=100*v.isna().mean()))
        d=catalogue[catalogue.task==task];metric='mae' if task=='regression' else 'average_precision'
        fig,ax=plt.subplots(figsize=(7.5,5.3))
        colors=['#28754a' if bool(s) else '#357a9e' if c==1 else '#c18035' for s,c in zip(d.selected,d.cycle)]
        ax.barh(d.label,d['validation_'+metric+'_mean'],xerr=d['validation_'+metric+'_sd'],color=colors,capsize=3)
        ax.invert_yaxis();ax.set_xlabel('MAE in days — lower is better' if task=='regression' else 'Average Precision — higher is better');ax.set_title(task.capitalize()+' development mean ± sample SD')
        ax.grid(axis='x',alpha=.2);fig.tight_layout();fig.savefig(output/'figures'/f'{task}_comparison.png',dpi=180);plt.close(fig)
        d=importance[importance.task==task].sort_values('mean')
        fig,ax=plt.subplots(figsize=(7.5,4.5))
        ax.barh(d.feature,d['mean'],xerr=d['std'],color='#357a9e',capsize=3);ax.axvline(0,color='black',linewidth=.7)
        ax.set_xlabel('Increase in MAE (days)' if task=='regression' else 'Decrease in Average Precision');ax.set_title(task.capitalize()+' validation permutation importance')
        fig.tight_layout();fig.savefig(output/'figures'/f'{task}_permutation.png',dpi=180);plt.close(fig)
    pd.DataFrame(numeric).to_csv(output/'all_input_numeric.csv',index=False)
    pd.DataFrame(categorical).to_csv(output/'all_input_categorical.csv',index=False)
    # Make population accounting and monthly diagnostics explicit in the report.
    split_path=ROOT/'data/business/ml/split_assignments.csv'
    assert hashlib.sha256(split_path.read_bytes()).hexdigest()==json.loads((run/'input_hashes.json').read_text())['split_assignments.csv']
    assignments=pd.read_csv(split_path,dtype={'order_id':'string'}).set_index('order_id')
    d=base.join(assignments[['split_assignment']])
    development=d[d.split_assignment=='development'];cutoff=protocol['terminal_cutoff'][:10]
    terminal=development[development.prediction_timestamp>=cutoff]
    pre=development[development.prediction_timestamp<cutoff]
    purge=pre[pre.customer_unique_id.isin(terminal.customer_unique_id)]
    pre=pre[~pre.customer_unique_id.isin(terminal.customer_unique_id)]
    flow=[dict(stage='All raw orders',n=len(base)),dict(stage='Customer-reserved orders outside this study',n=int((d.split_assignment=='holdout').sum())),dict(stage='Starting modelling population',n=len(development)),dict(stage='Preterminal before terminal-customer purge',n=len(pre)+len(purge)),dict(stage='Preterminal orders purged for terminal customers',n=len(purge)),dict(stage='Preterminal after terminal-customer purge',n=len(pre)),dict(stage='Terminal before task eligibility',n=len(terminal))]
    for task in ['regression','classification']:
        flow.append(dict(stage=task.capitalize()+' preterminal existing target eligibility',n=int(pre['eligible_'+task].sum())))
        flow.append(dict(stage=task.capitalize()+' final training',n=len(pd.read_csv(run/f'{task}_final_training_ids.csv'))))
        flow.append(dict(stage=task.capitalize()+' terminal included',n=len(pd.read_csv(run/'terminal'/f'{task}_{selected[task]["id"]}_predictions.csv'))))
    pd.DataFrame(flow).to_csv(output/'population_flow.csv',index=False)
    monthly=[]
    for task in ['regression','classification']:
        name=selected[task]['id'];d=pd.read_csv(run/'terminal'/f'{task}_{name}_predictions.csv',float_precision='round_trip')
        for month,frame in d.groupby(pd.to_datetime(d.prediction_timestamp).dt.strftime('%Y-%m')):
            y,p=frame.target,frame.prediction;rec=dict(task=task,dimension='purchase_month',subgroup=month,n=len(frame))
            if task=='regression':rec.update(mae=mean_absolute_error(y,p),rmse=np.sqrt(mean_squared_error(y,p)),r2=r2_score(y,p))
            else:
                cut=json.loads((run/'decision_policy.json').read_text())['threshold'];tn,fp,fn,tp=confusion_matrix(y,p>=cut,labels=[0,1]).ravel()
                rec.update(positives=int(y.sum()),average_precision=average_precision_score(y,p),roc_auc=roc_auc_score(y,p),precision_1=tp/(tp+fp) if tp+fp else np.nan,recall_1=tp/(tp+fn) if tp+fn else np.nan,illustrative_cost_5_to_1=int(fp+5*fn))
            monthly.append(rec)
    pd.DataFrame(monthly).to_csv(output/'monthly_subgroups.csv',index=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();generate(args.run.resolve(),args.output.resolve())
