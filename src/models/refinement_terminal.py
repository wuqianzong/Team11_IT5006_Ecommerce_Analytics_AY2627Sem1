"""Freeze, then evaluate saved chronological core bundles once; never fits/selects."""
from __future__ import annotations

import argparse
import json
import platform
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score

from src.common.loaders import sha256_file
from .data import ROOT, TARGETS, load_development
from .evaluate import metrics
from .finalize import report_metrics, per_class_report, subgroup_tables
from .io import write_json, write_csv_lf, ids_digest
from .refinement_core import CORE_FEATURES
from .refinement_score import CoreScorer

ROLES = ['selected', 'dummy', 'linear', 'tree']
RECIPE = {
    'version': 'chronological-terminal-v2', 'authorization': 'User: ok, proceed',
    'scope': 'Original development only; original holdout excluded',
    'terminal_start': '2018-05-25T00:00:00', 'terminal_end': 'Available source end; no tail trimming',
    'eligibility': 'Existing task eligibility plus valid contributing outcome timestamps',
    'regression_timestamp': 'Recorded delivery strictly after purchase',
    'classification_timestamp': 'Every valid contributing review answer timestamp present and >= purchase',
    'evaluation_observation_horizon': 'All recorded outcomes; no invented complete follow-up date',
    'roles': ROLES, 'primary_metrics': {'regression': 'mae', 'classification': 'average_precision'},
    'thresholds': 'Selected frozen preterminal OOF policy; references fixed 0.5; selected 0.5 diagnostic also shown',
    'subgroups': ['customer_state', 'basket_size', 'observed_duration_days (regression only)', 'purchase_month'],
    'subgroup_reliability': 'n>=100; classification ranking also requires >=20 positives and negatives',
    'diagnostic_plots': 'Actual-minus-predicted residuals; ROC/PR; fixed-width 0.1 probability reliability bins; no recalibration',
    'uncertainty': {'method': 'Paired customer-cluster percentile bootstrap', 'replicates': 1000,
                    'seed': 42, 'coverage': 0.95,
                    'meaning': 'Conditional sampling variability; not adjustment for prior exposure, selection or temporal drift'},
    'no_fits_or_search': True,
    'limitations': ['Previously inspected data, not untouched independent test',
                    'Assumed reconstruction of transaction inputs, not event-time certification',
                    'Conditional recorded delivery/review populations; unknown complete follow-up horizon'],
}


def freeze(root, bundles, freeze_path, verification_path):
    if freeze_path.exists():
        raise FileExistsError('Freeze already exists; never replace')
    checked = json.loads(verification_path.read_text())
    if not all(checked['checks'].values()) or checked['cycle_predictive_fits'] != 263:
        raise ValueError('Implementation gate failed')
    for name, digest in checked['source_sha256'].items():
        if sha256_file(root/name) != digest:
            raise ValueError('Verified implementation changed: '+name)
    for name, digest in checked['preterminal_artifact_sha256'].items():
        if sha256_file(bundles/name) != digest:
            raise ValueError('Verified prefit artifact changed: '+name)
    paths = list((root/'src').rglob('*.py')) + list((root/'src/models/configs').glob('*.json'))
    paths += [root/'requirements.txt', verification_path]
    paths += [p for p in bundles.rglob('*') if p.is_file()]
    source = root/'data/business/ml'
    paths += [p for p in source.iterdir() if p.is_file() and p.suffix in {'.csv', '.json'}]
    paths += [p for p in (root/'data/preprocessed').iterdir() if p.is_file() and p.suffix=='.csv']
    freeze_path.parent.mkdir(parents=True, exist_ok=True)
    write_json({'recorded_utc': datetime.now(timezone.utc).isoformat(), 'recipe': RECIPE,
                'python': platform.python_version(), 'bundles': str(bundles.relative_to(root)),
                'hashes': {str(p.relative_to(root)): sha256_file(p) for p in sorted(set(paths))},
                'new_predictive_fits': 0, 'terminal_scoring_started': False}, freeze_path)


def terminal_cohorts(development, reviews, cutoff):
    """No score-based filters. Return both inclusion and explicit exclusion evidence."""
    terminal = development.loc[pd.to_datetime(development.prediction_timestamp).ge(pd.Timestamp(cutoff))].copy()
    terminal['prediction_timestamp'] = pd.to_datetime(terminal.prediction_timestamp)
    scores = pd.to_numeric(reviews.review_score, errors='coerce')
    valid = scores.notna() & np.isfinite(scores) & scores.mod(1).eq(0) & scores.between(1,5)
    contributing = reviews.loc[valid & reviews.order_id.isin(terminal.order_id)].copy()
    contributing['_date'] = pd.to_datetime(contributing.review_answer_timestamp, errors='coerce')
    contributing['_missing'] = contributing._date.isna()
    contributing['_score'] = scores.loc[contributing.index]
    agg = contributing.groupby('order_id').agg(min_answer=('_date','min'), max_answer=('_date','max'),
                                               missing_answers=('_missing','sum'), min_score=('_score','min'))
    terminal = terminal.merge(agg, on='order_id', how='left', validate='one_to_one')
    cls = terminal.eligible_classification.eq(1)
    if not terminal.loc[cls,'review_score_min'].eq(terminal.loc[cls,'min_score']).all():
        raise ValueError('Terminal classification target differs from contributing reviews')
    if not terminal.loc[cls,'is_detractor'].eq(terminal.loc[cls,'min_score'].le(2).astype(int)).all():
        raise ValueError('Binary target inconsistent')
    delivered = pd.to_datetime(terminal.regression_label_available_at, errors='coerce')
    valid_time = {
        'regression': delivered.notna() & delivered.gt(terminal.prediction_timestamp),
        'classification': terminal.min_answer.notna() & terminal.max_answer.notna() &
            terminal.missing_answers.eq(0) & terminal.min_answer.ge(terminal.prediction_timestamp),
    }
    frames, eligibility = {}, []
    for task, target in TARGETS.items():
        eligible = terminal['eligible_'+task].eq(1)
        mask = eligible & valid_time[task]
        frames[task] = terminal.loc[mask].sort_values('order_id').reset_index(drop=True)
        if frames[task].empty or frames[task][target].isna().any():
            raise ValueError('Empty cohort or missing eligible target')
        if task == 'regression':
            expected = (delivered.loc[mask]-terminal.loc[mask,'prediction_timestamp']).dt.total_seconds()/86400
            if not np.allclose(expected, terminal.loc[mask,'lead_days'], rtol=1e-12, atol=1e-12):
                raise ValueError('Terminal duration formula differs')
        for i, row in terminal.iterrows():
            eligibility.append({'order_id': row.order_id, 'task': task, 'purchase_month': str(row.prediction_timestamp.to_period('M')),
                                'included': bool(mask.loc[i]), 'existing_eligible': bool(eligible.loc[i]),
                                'reason': 'included' if mask.loc[i] else ('existing_task_ineligible' if not eligible.loc[i]
                                             else 'contributing_label_timestamp_missing_or_inconsistent')})
    return terminal, frames, pd.DataFrame(eligibility)


def paired_intervals(task, y, selected, reference, groups, replicates=1000, seed=42):
    y, selected, reference = map(np.asarray, (y, selected, reference))
    groups = np.asarray(groups)
    unique, inverse = np.unique(groups, return_inverse=True)
    rng = np.random.default_rng(seed)
    values=[]
    def delta(weights):
        if task=='regression':
            return float(np.average(np.abs(y-selected)-np.abs(y-reference),weights=weights))
        if len(np.unique(y[weights>0]))<2:
            return None
        return float(average_precision_score(y,selected,sample_weight=weights)-average_precision_score(y,reference,sample_weight=weights))
    for _ in range(replicates):
        group_counts=np.bincount(rng.integers(0,len(unique),len(unique)),minlength=len(unique))
        value=delta(group_counts[inverse])
        if value is not None: values.append(value)
    if not values: raise ValueError('No valid bootstrap samples')
    return {'task': task, 'metric': 'mae' if task=='regression' else 'average_precision',
            'difference_selected_minus_reference': delta(np.ones(len(y))),
            'lower_95': float(np.quantile(values,.025)), 'upper_95': float(np.quantile(values,.975)),
            'replicates_requested': replicates, 'replicates_valid': len(values), 'seed': seed,
            'customers': len(unique), 'interpretation': 'Negative favours selected for MAE; positive for AP. Conditional sampling only.'}


def diagnostic_plots(output, frames, predictions):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from sklearn.metrics import roc_curve, precision_recall_curve
    y=frames['regression'].lead_days.to_numpy();score=predictions['regression','selected']
    fig,axes=plt.subplots(1,3,figsize=(13,4))
    axes[0].scatter(y,score,s=4,alpha=.15);axes[0].plot([0,y.max()],[0,y.max()],'k--')
    axes[0].set(xlabel='Actual delivery days',ylabel='Predicted delivery days')
    axes[1].scatter(score,y-score,s=4,alpha=.15);axes[1].axhline(0,color='black',ls='--')
    axes[1].set(xlabel='Predicted delivery days',ylabel='Actual minus predicted (days)')
    axes[2].hist(y-score,bins=60);axes[2].set(xlabel='Actual minus predicted (days)',ylabel='Orders')
    fig.suptitle('Chronological terminal evaluation: frozen core random forest')
    fig.tight_layout();fig.savefig(output/'regression_terminal_diagnostics.png',dpi=150);plt.close(fig)
    y=frames['classification'].is_detractor.to_numpy();score=predictions['classification','selected']
    records=[];bins=np.minimum((score*10).astype(int),9)
    for b in range(10):
        mask=bins==b
        records.append({'bin':b,'lower_inclusive':b/10,'upper':(b+1)/10,'n':int(mask.sum()),
                        'mean_probability':float(score[mask].mean()) if mask.any() else None,
                        'observed_negative_fraction':float(y[mask].mean()) if mask.any() else None})
    table=pd.DataFrame(records);write_csv_lf(table,output/'classification_reliability.csv')
    fig,axes=plt.subplots(1,3,figsize=(13,4))
    if len(np.unique(y))==2:
        fpr,tpr,_=roc_curve(y,score);precision,recall,_=precision_recall_curve(y,score)
        axes[0].plot(fpr,tpr);axes[1].plot(recall,precision)
    axes[0].plot([0,1],[0,1],'k--');axes[0].set(xlabel='False-positive rate',ylabel='Recall',title='ROC')
    axes[1].axhline(y.mean(),color='grey',ls='--');axes[1].set(xlabel='Recall',ylabel='Precision',title='PR (dashed: prevalence)')
    axes[2].plot(table.mean_probability,table.observed_negative_fraction,'o-')
    axes[2].plot([0,1],[0,1],'k--');axes[2].set(xlabel='Mean predicted probability',ylabel='Observed negative fraction',title='Reliability (fixed bins)')
    fig.suptitle('Chronological terminal evaluation: frozen core logistic regression')
    fig.tight_layout();fig.savefig(output/'classification_terminal_diagnostics.png',dpi=150);plt.close(fig)


def evaluate(root, freeze_path, output):
    if output.exists(): raise FileExistsError('Terminal attempt exists; do not overwrite or silently repeat')
    frozen=json.loads(freeze_path.read_text())
    if frozen['recipe']!=RECIPE: raise ValueError('Recipe changed after freeze')
    for name,digest in frozen['hashes'].items():
        if sha256_file(root/name)!=digest: raise ValueError('Frozen dependency changed: '+name)
    output.mkdir(parents=True)
    write_json({'status':'started', 'recorded_utc':datetime.now(timezone.utc).isoformat(),
                'freeze_sha256':sha256_file(freeze_path),'new_predictive_fits':0},output/'attempt.json')
    bundles=root/frozen['bundles']
    dev,_,_=load_development(root)
    reviews=pd.read_csv(root/'data/preprocessed/olist_order_reviews_dataset.csv',
                        usecols=['order_id','review_score','review_answer_timestamp'],dtype={'order_id':'string'})
    terminal,frames,eligibility=terminal_cohorts(dev,reviews,RECIPE['terminal_start'])
    saved=pd.read_csv(bundles/'terminal_identity_manifest.csv',dtype={'order_id':'string','customer_unique_id':'string'})
    if set(saved.order_id)!=set(terminal.order_id): raise ValueError('Terminal identities differ from reservation')
    identity=terminal[['order_id','customer_unique_id']].sort_values('order_id').reset_index(drop=True)
    if not identity.equals(saved[['order_id','customer_unique_id']].sort_values('order_id').reset_index(drop=True)):
        raise ValueError('Reserved terminal customer identity differs')
    for task in TARGETS:
        train=pd.read_csv(bundles/f'{task}_preterminal_training_ids.csv',dtype='string')
        if set(train.customer_unique_id)&set(terminal.customer_unique_id): raise ValueError('Training/terminal customer overlap')
        if not pd.to_datetime(train.prediction_timestamp).lt(pd.Timestamp(RECIPE['terminal_start'])).all():
            raise ValueError('Future training row')
    write_csv_lf(eligibility,output/'terminal_eligibility.csv')
    coverage=eligibility.groupby(['task','purchase_month','reason']).size().rename('n').reset_index()
    write_csv_lf(coverage,output/'coverage_by_month.csv')
    results=[];subgroups=[];classes=[];monthly=[];intervals=[];predictions={};notices=[]
    for task,rows in frames.items():
        y=rows[TARGETS[task]].to_numpy()
        for role in ROLES:
            scorer=CoreScorer(bundles/task/role)
            def forbidden_fit(*args,**kwargs): raise AssertionError('Terminal evaluation cannot fit')
            scorer.pipeline.fit=forbidden_fit
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always');scored=scorer.score(rows[['order_id',*CORE_FEATURES]])
            notices.extend({'task':task,'role':role,'category':w.category.__name__,'message':str(w.message)} for w in caught)
            score=scored['lead_days_prediction' if task=='regression' else 'probability_1'].to_numpy()
            cut=float(scorer.policy['threshold']) if task=='classification' else .5
            predictions[task,role]=score
            table=rows[['order_id','customer_unique_id','prediction_timestamp',TARGETS[task]]].rename(columns={TARGETS[task]:'target'})
            table=table.merge(scored,on='order_id',validate='one_to_one')
            if task=='regression':table['residual_actual_minus_predicted']=y-score
            write_csv_lf(table,output/f'{task}_{role}_terminal_predictions.csv')
            results.append({'task':task,'role':role,'operating_policy':'frozen' if role=='selected' else 'reference_default',**report_metrics(task,y,score,cut)})
            if task=='classification':
                classes.extend({'role':role,**r} for r in per_class_report(y,score,cut))
                if role=='selected': results.append({'task':task,'role':role,'operating_policy':'fixed_0.5_diagnostic_not_selected',**report_metrics(task,y,score,.5)})
            subgroups.extend({'role':role,**r} for r in subgroup_tables(task,rows,score,cut))
            for month,indices in rows.groupby(rows.prediction_timestamp.dt.to_period('M')).groups.items():
                ix=np.asarray(list(indices),dtype=int)
                monthly.append({'task':task,'role':role,'purchase_month':str(month),**report_metrics(task,y[ix],score[ix],cut)})
            print('Scored',task,role,len(rows),flush=True)
        for role in ROLES[1:]:
            interval=paired_intervals(task,y,predictions[task,'selected'],predictions[task,role],rows.customer_unique_id.to_numpy())
            intervals.append({'reference_role':role,**interval});print('Interval',task,role,flush=True)
    groups=pd.DataFrame(subgroups)
    groups['ranking_reliable_flag']=groups.n.ge(100)&((groups.task=='regression')|(groups.positives.ge(20)&groups.negatives.ge(20)))
    write_csv_lf(groups,output/'terminal_subgroups.csv')
    write_csv_lf(pd.DataFrame(results),output/'terminal_metrics.csv')
    write_csv_lf(pd.DataFrame(classes),output/'classification_per_class.csv')
    write_csv_lf(pd.DataFrame(monthly),output/'terminal_monthly_metrics.csv')
    write_csv_lf(pd.DataFrame(intervals),output/'paired_cluster_bootstrap.csv')
    write_json(notices,output/'scoring_warnings.json')
    diagnostic_plots(output,frames,predictions)
    for name,digest in frozen['hashes'].items():
        if sha256_file(root/name)!=digest:raise ValueError('Dependency mutated during evaluation: '+name)
    write_json({'status':'completed_one_declared_terminal_evaluation','freeze_sha256':sha256_file(freeze_path),
                'terminal_identity_n':len(terminal),'evaluated_n':{t:len(r) for t,r in frames.items()},
                'terminal_order_ids_sha256':ids_digest(terminal.order_id),'new_predictive_fits':0,
                'cycle_predictive_fits':263,'frozen_inputs_unchanged':True,'selection_changed':False,
                'limitations':RECIPE['limitations'],'output_hashes':{p.name:sha256_file(p) for p in output.iterdir() if p.is_file() and p.name!='completion.json'}},output/'completion.json')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze',type=Path,required=True)
    parser.add_argument('--create-freeze',action='store_true')
    parser.add_argument('--bundles',type=Path)
    parser.add_argument('--verification',type=Path)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    if args.create_freeze:
        if args.bundles is None or args.verification is None:parser.error('Freeze requires bundles and verification')
        freeze(ROOT,args.bundles,args.freeze,args.verification)
    else:
        if args.output is None:parser.error('Evaluation requires output')
        evaluate(ROOT,args.freeze,args.output)
