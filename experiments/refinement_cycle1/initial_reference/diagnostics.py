"""Original 255-fit diagnostic design with portable paths; no terminal scoring."""
from __future__ import annotations
import argparse
import hashlib
import importlib.metadata
import json
import platform
import sys
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.compose import ColumnTransformer
from sklearn.exceptions import ConvergenceWarning
from src.features.contract import PREDICTOR_ALLOWLIST, UNKNOWN
from src.models.data import load_development, TARGETS
from src.models.evaluate import metrics
from src.models.io import write_json, ids_digest
from src.models.pipelines import positive_probability
from src.models.tuned_pipelines import make_tuned_pipeline

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PROTOCOL = HERE / 'protocol.json'
LOG = None

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()

def event(kind, action, outcome, experiment='STEP5', **extra):
    prior = [json.loads(x) for x in LOG.read_text().splitlines()] if LOG.exists() else []
    ident = 'S5-' + str(sum(x['event_id'].startswith('S5-') for x in prior)+1).zfill(4)
    data = dict(event_id=ident, timestamp_utc=datetime.now(timezone.utc).isoformat(),
                actor='assistant', event_type=kind, experiment_id=experiment,
                rubric_sections=[1,2,3,4,5,6], action=action, outcome=outcome,
                evidence_paths=[], limitations=['Reused development; retrospective input assumptions; no terminal scoring.'],
                next_action='Continue frozen diagnostic protocol or stop on invalid evidence.',
                previous_event_id=prior[-1]['event_id'] if prior else None, **extra)
    with LOG.open('a') as f:
        f.write(json.dumps(data, default=str) + '\n')

class RareState(TransformerMixin, BaseEstimator):
    def fit(self, X, y=None):
        values = X.customer_state
        if values.eq('__REFINEMENT_RARE__').any():
            raise ValueError('Reserved rare token collision')
        counts = values[values.ne(UNKNOWN)].value_counts()
        counts = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        kept, total = [], 0
        for token, count in counts:
            kept.append(token); total += count
            if total >= .8 * sum(c for _, c in counts):
                break
        self.keep_ = kept
        self.seen_ = sorted(values.unique())
        self.feature_names_in_ = np.array(X.columns)
        return self
    def transform(self, X):
        X = X.copy()
        rare = ~X.customer_state.isin(self.keep_ + [UNKNOWN])
        X.loc[rare, 'customer_state'] = '__REFINEMENT_RARE__'
        return X
    def get_feature_names_out(self, input_features=None):
        return self.feature_names_in_

if __name__ == '__main__':
    # Stable identity for new bundles, unlike the original local CLI alias.
    sys.modules['experiments.refinement_cycle1.initial_reference.diagnostics'] = sys.modules[__name__]
    RareState.__module__ = 'experiments.refinement_cycle1.initial_reference.diagnostics'

def pipeline(task, candidate, config, columns, rare=False):
    pipe = make_tuned_pipeline(task, candidate, config)
    transforms = [(name, clone(est), [c for c in cols if c in columns])
                  for name, est, cols in pipe.named_steps['preprocess'].transformers]
    pipe.set_params(preprocess=ColumnTransformer(transforms, remainder='drop', sparse_threshold=1., verbose_feature_names_out=True))
    if rare:
        pipe.steps.insert(1, ('rare', RareState()))
    return pipe

def prepare(out, protocol):
    dev, _, hashes = load_development(ROOT)
    dev['prediction_timestamp'] = pd.to_datetime(dev.prediction_timestamp)
    cutoff = pd.Timestamp(protocol['terminal_cutoff'])
    terminal_ids = dev.loc[dev.prediction_timestamp.ge(cutoff), ['order_id','customer_unique_id','prediction_timestamp']].copy()
    terminal_ids.to_csv(out / 'terminal_identity_manifest.csv', index=False)
    groups = set(terminal_ids.customer_unique_id)
    earlier = dev.loc[dev.prediction_timestamp.lt(cutoff)].copy()
    terminal_purge = earlier.customer_unique_id.isin(groups)
    earlier.loc[terminal_purge,['order_id','customer_unique_id']].to_csv(out / 'terminal_group_training_purge.csv', index=False)
    earlier = earlier.loc[~terminal_purge].copy().reset_index(drop=True)
    # No terminal targets reach downstream fitting/scoring functions.
    dev = None
    reviews = pd.read_csv(ROOT/'data/preprocessed/olist_order_reviews_dataset.csv',
                          usecols=['order_id','review_score','review_answer_timestamp'], dtype={'order_id':'string'})
    reviews = reviews.loc[reviews.order_id.isin(earlier.order_id)].copy()
    scores = pd.to_numeric(reviews.review_score, errors='coerce')
    valid = scores.notna() & np.isfinite(scores) & scores.mod(1).eq(0) & scores.between(1,5)
    reviews = reviews.loc[valid].copy()
    reviews['_score'] = scores.loc[valid]
    reviews['_answer'] = pd.to_datetime(reviews.review_answer_timestamp, errors='coerce')
    reviews['_missing'] = reviews._answer.isna()
    agg = reviews.groupby('order_id').agg(review_time_min=('_answer','min'), review_time_max=('_answer','max'),
                        review_time_missing=('_missing','sum'), source_min_score=('_score','min'))
    earlier = earlier.merge(agg, on='order_id', how='left', validate='one_to_one')
    eligible_cls = earlier.eligible_classification.eq(1)
    if not earlier.loc[eligible_cls, 'review_score_min'].eq(earlier.loc[eligible_cls,'source_min_score']).all():
        raise ValueError('Recorded review target does not match source minimum')
    earlier['regression_label_available_at'] = pd.to_datetime(earlier.regression_label_available_at, errors='coerce')
    validity = {
        'regression': earlier.regression_label_available_at.notna() & earlier.regression_label_available_at.gt(earlier.prediction_timestamp),
        'classification': earlier.review_time_min.notna() & earlier.review_time_max.notna() & earlier.review_time_missing.eq(0) & earlier.review_time_min.ge(earlier.prediction_timestamp)
    }
    availability = {'regression': earlier.regression_label_available_at, 'classification': earlier.review_time_max}
    boundaries = [pd.Timestamp(x) for x in protocol['inner_calendar_boundaries']]
    folds, membership, exclusions, qa = {}, [], [], []
    for fold, (lo, hi) in enumerate(zip(boundaries[:-1], boundaries[1:])):
        val_window = earlier.prediction_timestamp.ge(lo) & earlier.prediction_timestamp.lt(hi)
        val_groups = set(earlier.loc[val_window,'customer_unique_id'])
        for task in TARGETS:
            eligible = earlier['eligible_'+task].eq(1)
            train_window = earlier.prediction_timestamp.lt(lo) & eligible
            group_purge = earlier.customer_unique_id.isin(val_groups)
            train = train_window & ~group_purge & validity[task] & availability[task].lt(lo)
            val = val_window & eligible & validity[task] & availability[task].lt(cutoff)
            tr, va = earlier.loc[train].copy(), earlier.loc[val].copy()
            if tr.empty or va.empty or set(tr.customer_unique_id) & set(va.customer_unique_id):
                raise ValueError('Empty/overlapping chronological fold')
            if task == 'classification' and (set(tr.is_detractor) != {0,1} or set(va.is_detractor) != {0,1}):
                raise ValueError('Chronological classification fold lacks a class')
            assert tr.prediction_timestamp.lt(lo).all() and availability[task].loc[train].lt(lo).all()
            assert va.prediction_timestamp.ge(lo).all() and va.prediction_timestamp.lt(hi).all()
            assert not set(tr.customer_unique_id) & groups and not set(va.customer_unique_id) & groups
            for role, frame in [('training',tr), ('validation',va)]:
                for oid in frame.order_id:
                    membership.append(dict(order_id=oid,task=task,fold=fold,role=role))
            for role, window, available_cutoff in [('training',train_window,lo),('validation',val_window & eligible,cutoff)]:
                for idx in earlier.index[window]:
                    reasons = []
                    if role == 'training' and group_purge.loc[idx]: reasons.append('validation_customer_purge')
                    if not validity[task].loc[idx]: reasons.append('label_timestamp_missing_or_inconsistent')
                    elif not availability[task].loc[idx] < available_cutoff: reasons.append('label_not_observable_by_cutoff')
                    if reasons: exclusions.append(dict(order_id=earlier.loc[idx,'order_id'],task=task,fold=fold,role=role,reasons=';'.join(reasons)))
            folds[task,fold] = (tr,va)
            qa.append(dict(task=task,fold=fold,training_n=len(tr),validation_n=len(va),training_cutoff=str(lo),validation_end=str(hi),
                           training_ids_sha256=ids_digest(tr.order_id),validation_ids_sha256=ids_digest(va.order_id),
                           zero_customer_overlap=True,all_training_labels_mature=True,terminal_targets_returned=False))
    pd.DataFrame(membership).to_csv(out/'chronological_fold_membership.csv', index=False)
    pd.DataFrame(exclusions).to_csv(out/'chronological_exclusions.csv', index=False)
    write_json({'folds':qa,'input_hashes':hashes,'terminal_identities':len(terminal_ids),
                'terminal_targets_returned':False,'new_model_fits':0},out/'cohort_verification.json')
    return folds, hashes

def priority(c):
    family = c['family']
    rank = {'dummy':0,'linear':1,'ridge':2,'logistic':2,'tree':3,'forest':4}[family]
    params = c.get('params', {})
    return rank, params.get('max_depth', 5), -params.get('min_samples_leaf',100), c['id']

def choose(records, task, candidates):
    key = 'mae' if task=='regression' else 'average_precision'
    scores = {c['id']: np.array([r[key] for r in records if r['task']==task and r['candidate']==c['id'] and r['partition']=='validation' and r['experiment']=='E01']) for c in candidates}
    if any(len(x)!=5 or not np.isfinite(x).all() for x in scores.values()):
        raise ValueError('Incomplete candidate comparison')
    sign = 1 if task=='regression' else -1
    best = min(candidates,key=lambda c:sign * scores[c['id']].mean())
    tol = .05 if task=='regression' else .005
    comparable = [c for c in candidates if (sign*(scores[c['id']]-scores[best['id']])).mean() <= tol+1e-12 and (sign*(scores[c['id']]-scores[best['id']]) <= tol+1e-12).sum() >=4]
    return min(comparable,key=priority)

def complete_mask(frame):
    mask = frame.has_items.eq(1) & frame.payment_missing.eq(0)
    for c in ['weight_missing_fraction','volume_missing_fraction','category_missing_fraction','distance_missing_fraction']:
        mask &= frame[c].eq(0)
    return mask

def state(pipe, X):
    names = pipe[:-1].get_feature_names_out().tolist()
    pre = pipe.named_steps['preprocess']
    info = {'transformed_names':names,'dimension':len(names)}
    if 'rare' in pipe.named_steps:
        info['rare_mapping'] = {'retained':pipe.named_steps['rare'].keep_, 'seen':pipe.named_steps['rare'].seen_}
    for name, transform, cols in pre.transformers_:
        if name=='remainder' or not len(cols): continue
        if name=='numeric':
            info['imputer_statistics'] = dict(zip(cols,transform.named_steps['impute'].statistics_.tolist()))
            if 'scale' in transform.named_steps:
                info['scaler_mean'] = transform.named_steps['scale'].mean_.tolist()
                info['scaler_scale'] = transform.named_steps['scale'].scale_.tolist()
        else:
            info['encoding'] = {c:transform.categories_[i].tolist() for i,c in enumerate(cols)}
            info['reference_coding'] = transform.drop
    model = pipe.named_steps['model']
    if hasattr(model,'coef_'):
        info['coefficients'] = dict(zip(names,np.ravel(model.coef_).tolist()))
        info['intercept'] = np.ravel(model.intercept_).tolist()
    return info

def run(out, prepare_only=False):
    global LOG
    if out.exists(): raise FileExistsError('Never overwrite a diagnostic run')
    out.mkdir(parents=True)
    LOG = out / 'process_log.jsonl'
    protocol = json.loads(PROTOCOL.read_text())
    environment = {'python':sys.version,'platform':platform.platform(),
                   'packages':{p:importlib.metadata.version(p) for p in ['numpy','pandas','scikit-learn','scipy','joblib']}}
    identity = {'protocol_sha256':digest(PROTOCOL),'runner_sha256':digest(__file__),'environment':environment,
                'dependency_sha256':{str(p.relative_to(ROOT)):digest(p) for p in [ROOT/'src/models/tuned_pipelines.py',ROOT/'src/models/pipelines.py',ROOT/'src/models/data.py',ROOT/'src/models/evaluate.py']}}
    write_json(identity,out/'identity.json')
    event('start','Build separate chronological manifests and verify cohort gates.','Started; no production data changes.',code_hash=identity['runner_sha256'],config_hash=identity['protocol_sha256'])
    folds, hashes = prepare(out,protocol)
    expected = json.loads((HERE/'feasibility.json').read_text())['folds']
    for row in expected:
        tr, va = folds[row['task'],row['fold']]
        if len(tr)!=row['usable_training'] or len(va)!=row['usable_validation']:
            raise ValueError('Independent preflight counts disagree')
    write_json({'status':'passed','independent_preflight_count_match':True,'folds':10,'new_model_fits':0},out/'preflight.json')
    event('completion','Verify chronological manifests against independent preflight.','All ten task/fold training/validation counts match; zero group/time leakage.',evidence_paths_override=[str(out/'preflight.json')])
    if prepare_only: return
    records, count = [], 0
    (out/'jobs').mkdir()
    def fit_job(experiment, task, candidate, fold, columns, rare=False, complete=False):
        nonlocal count
        if count >=255: raise RuntimeError('Selection fit ceiling exhausted')
        tr,va=folds[task,fold]
        original_n=len(tr)
        if complete: tr=tr.loc[complete_mask(tr)].copy()
        if tr.empty or (task=='classification' and set(tr.is_detractor)!={0,1}):
            raise ValueError('Complete-case filter produced unusable training')
        pipe=pipeline(task,candidate,protocol['baseline_config'],columns,rare)
        job_id=f'{experiment}-{task}-{candidate["id"]}-fold{fold}'
        target=out/'jobs'/job_id;target.mkdir()
        count+=1
        params={'experiment':experiment,'task':task,'candidate':candidate,'fold':fold,'columns':columns,'rare':rare,'complete_training':complete,
                'training_n':len(tr),'original_training_n':original_n,'validation_n':len(va),
                'train_ids_sha256':ids_digest(tr.order_id),'validation_ids_sha256':ids_digest(va.order_id)}
        write_json(params,target/'configuration.json')
        tr[['order_id']].to_csv(target/'training_ids.csv',index=False)
        if complete:
            omitted=folds[task,fold][0].loc[~complete_mask(folds[task,fold][0])]
            omitted[['order_id']].to_csv(target/'excluded_training_ids.csv',index=False)
        event('start',f'Fit {job_id}','Predictive attempt started.',experiment,attempt_id=count,hypothesis=experiment,
              input_hashes=hashes,config_hash=digest(target/'configuration.json'),code_hash=identity['runner_sha256'],
              command=[sys.executable,*sys.argv],environment=environment,stdout_path=str(out.parent/'stdout.log'),stderr_path=str(out.parent/'stderr.log'),warnings=[],metrics_paths=[])
        start=time.monotonic()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always');pipe.fit(tr[PREDICTOR_ALLOWLIST],tr[TARGETS[task]])
        warning_list=[{'category':w.category.__name__,'message':str(w.message)} for w in caught]
        write_json(warning_list,target/'warnings.json')
        if any(issubclass(w.category,ConvergenceWarning) for w in caught):
            raise RuntimeError('Convergence warning; stopped without candidate selection')
        seconds=time.monotonic()-start
        for partition,frame in [('training_resubstitution',tr),('validation',va)]:
            score=pipe.predict(frame[PREDICTOR_ALLOWLIST]) if task=='regression' else positive_probability(pipe,frame[PREDICTOR_ALLOWLIST])
            m=metrics(task,frame[TARGETS[task]],score)
            row=dict(experiment=experiment,task=task,candidate=candidate['id'],family=candidate['family'],fold=fold,partition=partition,fit_seconds=seconds,**m)
            records.append(row)
            if partition=='validation':
                pd.DataFrame({'order_id':frame.order_id.to_numpy(),'customer_unique_id':frame.customer_unique_id.to_numpy(),
                   'prediction_timestamp':frame.prediction_timestamp.to_numpy(),'n_items':frame.n_items.to_numpy(),'customer_state':frame.customer_state.to_numpy(),
                   'complete_record':complete_mask(frame).to_numpy(),'target':frame[TARGETS[task]].to_numpy(),'prediction':score}).to_csv(target/'validation_predictions.csv',index=False)
        write_json(state(pipe,tr[PREDICTOR_ALLOWLIST]),target/'pipeline_state.json')
        joblib.dump(pipe,target/'pipeline.joblib',compress=3)
        write_json({'status':'complete','predictive_attempt':count,'fit_seconds':seconds,'warnings':warning_list,'pipeline_sha256':digest(target/'pipeline.joblib')},target/'completion.json')
        pd.DataFrame(records).to_csv(out/'fold_metrics.csv',index=False)
        event('completion',f'Complete {job_id}','Valid training/validation metrics and provenance saved.',experiment,attempt_id=count,warnings=warning_list,metrics_paths=[str(target/'validation_predictions.csv')])
        print(f'{count}/255 {job_id} {seconds:.2f}s',flush=True)
    for task in TARGETS:
        for c in protocol['candidates'][task]:
            for fold in range(5):fit_job('E01',task,c,fold,protocol['primary_features'])
    selected={};representatives={}
    for task in TARGETS:
        candidates=protocol['candidates'][task]
        selected[task]=choose(records,task,candidates)
        representatives[task]=[choose(records,task,[c for c in candidates if c['family'] in {'linear','ridge','logistic'}]),
                              choose(records,task,[c for c in candidates if c['family']=='forest'])]
    write_json({'core_finalist_candidates':selected,'sensitivity_representatives':representatives,'selected_from':'preterminal chronological folds only','not_adopted':True},out/'development_selection.json')
    core=protocol['primary_features'];full=protocol['retrospective_full_features']
    for exp in ['E02','E03','E04','E05','E06','E07','E08']:
        columns={'E02':[x for x in core if x!='n_products'],'E03':protocol['calendar_features'],
                 'E04':protocol['retrospective_no_payment_features'],'E05':full,
                 'E06':[x for x in full if x not in {'n_products','n_sellers','n_categories'}],'E07':core,'E08':full}[exp]
        for task in TARGETS:
            for c in representatives[task]:
                if exp=='E08' and c['family']!='forest':continue
                for fold in range(5):fit_job(exp,task,c,fold,columns,rare=exp=='E07',complete=exp=='E08')
    if count!=255:raise ValueError('Fit accounting mismatch')
    write_json({'status':'predictive_diagnostics_complete_auxiliary_and_evidence_review_pending','new_predictive_fits':count,
                'terminal_evaluated':False,'original_holdout_evaluated':False,'final_adoption':False},out/'run_completion.json')
    event('completion','Finish frozen predictive diagnostics.','255 fits complete; terminal/holdout untouched by this run; evidence review and auxiliary audits remain.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--prepare-only',action='store_true');args=p.parse_args()
    try:run(args.out,args.prepare_only)
    except Exception as error:
        event('failure','Chronological runner stopped.',repr(error),error_type=type(error).__name__)
        raise
