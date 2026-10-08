"""Bounded preterminal feature-block screen; no terminal API or final adoption."""
from __future__ import annotations
import argparse
import copy
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

from src.common.loaders import sha256_file
from src.features.contract import PREDICTOR_ALLOWLIST
from src.models.data import TARGETS
from src.models.evaluate import metrics
from src.models.io import ids_digest, write_json
from src.models.pipelines import normalize_inputs, positive_probability
from src.models.refinement_core import CORE_FEATURES
from src.models.refinement_temporal import chronological_data
from src.models.tuned_pipelines import make_tuned_pipeline
from experiments.refinement_cycle1.paths import binding

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = Path(__file__).with_name('protocol.json')

class SubsetInputContract(TransformerMixin, BaseEstimator):
    """Validate exactly the declared predictors using existing base semantics."""
    def __init__(self, columns):
        self.columns = columns

    def transform(self, X):
        if not isinstance(X, pd.DataFrame) or X.columns.duplicated().any():
            raise ValueError('Unique named dataframe required')
        if len(set(self.columns)) != len(self.columns) or not set(self.columns) <= set(PREDICTOR_ALLOWLIST):
            raise ValueError('Unknown/duplicate predictor specification')
        if set(X.columns) != set(self.columns):
            raise ValueError('Expected exactly declared predictor columns; outcomes/IDs prohibited')
        # Padding is schema validation only. Unselected columns never enter the
        # preprocessor/model and their values are neither required nor learned.
        padded = X.reindex(columns=PREDICTOR_ALLOWLIST)
        normalized, _ = normalize_inputs(padded)
        return normalized[list(self.columns)]

    def fit(self, X, y=None):
        self.transform(X)
        self.feature_names_in_ = np.array(self.columns, dtype=object)
        self.n_features_in_ = len(self.columns)
        return self

    def get_feature_names_out(self, input_features=None):
        return np.array(self.columns, dtype=object)

def make_pipeline(task, candidate, baseline_config, columns):
    pipe = make_tuned_pipeline(task, candidate, baseline_config)
    transforms = [(name, clone(est), [c for c in cols if c in columns])
                  for name, est, cols in pipe.named_steps['preprocess'].transformers]
    pipe.set_params(inputs=SubsetInputContract(tuple(columns)),
                    preprocess=ColumnTransformer(transforms, remainder='drop', sparse_threshold=1., verbose_feature_names_out=True))
    return pipe

def screen_flag(task, gains, protocol):
    a = np.asarray(gains, dtype=float)
    if len(a) != 5 or not np.isfinite(a).all():
        raise ValueError('Five finite paired window gains required')
    return bool(a.mean() > protocol['practical_gain'][task]
                and (a > 0).sum() >= protocol['required_improving_folds'])

def score(task, pipe, X):
    return pipe.predict(X) if task == 'regression' else positive_probability(pipe, X)

def canonical_membership(frame):
    keys = ['task', 'fold', 'role', 'order_id']
    if frame[keys].isna().any().any() or frame.duplicated(keys).any():
        raise ValueError('Missing/duplicate chronological membership key')
    canonical = frame[keys].astype({'task': 'string', 'role': 'string', 'order_id': 'string', 'fold': 'int64'})
    return canonical.sort_values(keys).reset_index(drop=True)

def read_design(root=ROOT):
    protocol = binding(json.loads(PROTOCOL.read_text()))
    config = json.loads((root / protocol['source_config']).read_text())
    if protocol['terminal_evaluation_allowed'] or config['terminal_evaluation_allowed']:
        raise ValueError('Terminal evaluation prohibited')
    if config['predictors'] != CORE_FEATURES:
        raise ValueError('Accepted core changed')
    added = [c for b in protocol['blocks'] for c in b['columns']]
    if len(set(added)) != 16 or len(added) != 16 or set(added) & set(CORE_FEATURES):
        raise ValueError('Blocks must partition the 16 non-core base predictors')
    if set(added) | set(CORE_FEATURES) != set(PREDICTOR_ALLOWLIST):
        raise ValueError('Block coverage differs from the preserved base')
    if len(protocol['blocks']) * 2 * 5 != protocol['stage_fit_ceiling']:
        raise ValueError('Invalid screen budget')
    return protocol, config

def protected_hashes(root):
    # Protect public inputs; private reports and original worktree guards are
    # provenance, not dependencies of a portable scientific reproduction.
    paths = list((root / 'data/business/ml').glob('*.csv'))
    paths += list((root / 'data/business/ml').glob('*.json'))
    paths += list((root / 'data/preprocessed').glob('*.csv'))
    return {str(p.relative_to(root)): sha256_file(p) for p in paths}

def assert_unchanged(root, expected):
    for rel, digest in expected.items():
        if sha256_file(root / rel) != digest:
            raise ValueError('Protected file modified: ' + rel)

def event(output, kind, action, **details):
    path = output / 'process_log.jsonl'
    prior = [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []
    record = {'event_id': f'FS3-{len(prior)+1:04d}', 'timestamp_utc': datetime.now(timezone.utc).isoformat(),
              'previous_event_id': prior[-1]['event_id'] if prior else None,
              'kind': kind, 'action': action, **details}
    with path.open('a') as f:
        f.write(json.dumps(record) + '\n')

def subgroup_rows(task, fold, block, frame, predictions, reference, protocol):
    result = []
    basket = np.select([frame.n_items.eq(0), frame.n_items.eq(1), frame.n_items.between(2, 3)],
                       ['0', '1', '2-3'], default='4+')
    dimensions = {'customer_state': frame.customer_state.fillna('Unknown').to_numpy(), 'basket_size': basket}
    metric = 'mae' if task == 'regression' else 'average_precision'
    for dimension, values in dimensions.items():
        for group in sorted(set(values)):
            mask = values == group
            y = frame.loc[mask, TARGETS[task]].to_numpy()
            n = len(y)
            positive = int((y == 1).sum()) if task == 'classification' else None
            negative = n - positive if positive is not None else None
            support = n >= protocol['minimum_subgroup_n']
            if task == 'classification':
                support &= min(positive, negative) >= protocol['minimum_subgroup_class_n']
                defined = positive > 0 and negative > 0
            else:
                defined = True
            candidate_value = metrics(task, y, predictions[mask])[metric] if defined else None
            core_value = metrics(task, y, reference[mask])[metric] if defined else None
            harm = (candidate_value - core_value if task == 'regression' else core_value - candidate_value) if defined else None
            result.append({'task': task, 'fold': fold, 'block': block, 'dimension': dimension,
                           'subgroup': group, 'n': n, 'positives': positive, 'negatives': negative,
                           'support_sufficient': bool(support), 'metric_defined': defined,
                           'core_metric': core_value, 'candidate_metric': candidate_value, 'harm': harm,
                           'substantial_harm_flag': bool(support and defined and harm > protocol['subgroup_harm'][task])})
    return result

def prepare(output, protocol, config):
    protected = protected_hashes(ROOT)
    data = chronological_data(ROOT, config)
    expected = pd.read_csv(ROOT / protocol['baseline_membership'], dtype={'order_id': 'string'})
    if not canonical_membership(data['membership']).equals(canonical_membership(expected)):
        raise ValueError('Accepted chronological memberships differ')
    data['membership'].to_csv(output / 'chronological_fold_membership.csv', index=False)
    data['exclusions'].to_csv(output / 'chronological_exclusions.csv', index=False)
    references, checks, evidence_hashes = {}, [], {}
    base = ROOT / protocol['baseline_evidence']
    for (task, fold), (training, validation) in data['folds'].items():
        cutoff = pd.Timestamp(config['terminal_cutoff'])
        if not training.prediction_timestamp.lt(cutoff).all() or not validation.prediction_timestamp.lt(cutoff).all():
            raise ValueError('Terminal purchases reached a trial')
        if set(training.customer_unique_id) & set(validation.customer_unique_id):
            raise ValueError('Customer overlap')
        candidate = config['selected'][task]
        folder = base / 'jobs' / f'E01-{task}-{candidate["id"]}-fold{fold}'
        pred_path = folder / 'validation_predictions.csv'
        reference = pd.read_csv(pred_path, dtype={'order_id': 'string'})
        if reference.order_id.duplicated().any() or set(reference.order_id) != set(validation.order_id):
            raise ValueError('Reference validation IDs differ')
        aligned = reference.set_index('order_id').loc[validation.order_id]
        if not np.array_equal(aligned.target.to_numpy(), validation[TARGETS[task]].to_numpy()):
            raise ValueError('Reference targets differ')
        job_config = json.loads((folder / 'configuration.json').read_text())
        if job_config['candidate'] != candidate or job_config['columns'] != CORE_FEATURES:
            raise ValueError('Reference candidate/features differ')
        if job_config['train_ids_sha256'] != ids_digest(training.order_id):
            raise ValueError('Reference training IDs differ')
        # Check the exact new subset input semantics against saved preterminal
        # models/predictions. No estimator fitting and no terminal scoring.
        sample = validation.iloc[:128]
        model = joblib.load(folder / 'pipeline.joblib')
        old = score(task, model, sample[PREDICTOR_ALLOWLIST])
        saved = aligned.prediction.to_numpy()[:len(sample)]
        replacement = copy.deepcopy(model)
        replacement.set_params(inputs=SubsetInputContract(tuple(CORE_FEATURES)))
        newer = score(task, replacement, sample[CORE_FEATURES])
        if not np.allclose(old, saved, rtol=1e-12, atol=1e-12) or not np.allclose(newer, saved, rtol=1e-12, atol=1e-12):
            raise ValueError('New subset interface does not reproduce core reference')
        references[task, fold] = aligned.prediction.to_numpy()
        checks.append({'task': task, 'fold': fold, 'training_n': len(training), 'validation_n': len(validation),
                       'same_ids_targets_training': True, 'subset_core_parity_128_rows': True,
                       'no_terminal_rows': True})
        for path in [pred_path, folder / 'configuration.json', folder / 'pipeline.joblib']:
            evidence_hashes[str(path.relative_to(ROOT))] = sha256_file(path)
    sources = [Path(__file__), PROTOCOL, ROOT / protocol['source_config'],
               ROOT / 'src/models/refinement_temporal.py', ROOT / 'src/models/tuned_pipelines.py',
               ROOT / 'src/models/pipelines.py', ROOT / 'src/models/data.py', ROOT / 'src/models/evaluate.py',
               ROOT / 'src/features/contract.py', ROOT / 'src/common/loaders.py']
    identity = {'source_hashes': {str(p.relative_to(ROOT)): sha256_file(p) for p in sources},
                'core_reference_hashes': evidence_hashes, 'protected_hashes': protected,
                'input_hashes': data['input_hashes'], 'protocol': protocol, 'fixed_model_config': config,
                'environment': {'python': sys.version, 'platform': platform.platform(),
                                'packages': {p: importlib.metadata.version(p) for p in ['numpy', 'pandas', 'scikit-learn', 'scipy', 'joblib']}}}
    write_json(identity, output / 'study_freeze.json')
    write_json({'status': 'passed', 'fold_checks': checks, 'same_chronological_membership': True,
                'new_predictive_fits': 0, 'terminal_scoring_calls': 0}, output / 'preflight.json')
    assert_unchanged(ROOT, protected)
    return data['folds'], references, identity

def summarize(records, subgroup_records, protocol, output):
    rows = []
    for task in TARGETS:
        for block in protocol['blocks']:
            vals = [r for r in records if r['task'] == task and r['block'] == block['id'] and r['partition'] == 'validation']
            if len(vals) != 5:
                continue
            metric = 'mae' if task == 'regression' else 'average_precision'
            warnings_n = sum(r['substantial_harm_flag'] for r in subgroup_records if r['task'] == task and r['block'] == block['id'])
            gains = [v['paired_gain'] for v in vals]
            promising = screen_flag(task, gains, protocol)
            rows.append({'task': task, 'block': block['id'], 'metric': metric,
                         'core_mean': np.mean([v['core_metric'] for v in vals]),
                         'candidate_mean': np.mean([v[metric] for v in vals]),
                         'candidate_sd': np.std([v[metric] for v in vals], ddof=1),
                         'paired_gain_mean': np.mean(gains), 'improving_folds': sum(g > 0 for g in gains),
                         'promising_screen_flag': promising, 'subgroup_harm_flags': warnings_n,
                         'status': 'promising_needs_review' if promising else 'no_consistent_practical_gain_in_screen',
                         'adopted': False, 'availability_certified': False})
    pd.DataFrame(rows).to_csv(output / 'block_summary.csv', index=False)
    return rows

def run(output, prepare_only=False):
    if output.exists():
        raise FileExistsError('Existing trial output refused; preserve previous attempts')
    output.mkdir(parents=True)
    protocol, config = read_design()
    event(output, 'initialization', 'Freeze a new exploratory preterminal block screen; preserve accepted runs.',
          new_predictive_attempts=0, terminal_evaluation_allowed=False)
    attempts = 0
    try:
        folds, references, identity = prepare(output, protocol, config)
        event(output, 'verification', 'Same memberships, training IDs, targets and core normalization verified for ten task/folds.',
              evidence='preflight.json', new_predictive_attempts=0)
        if prepare_only:
            write_json({'status': 'prepared_not_fitted', 'new_predictive_attempts': 0,
                        'terminal_scoring_calls': 0, 'adopted': False}, output / 'run_completion.json')
            return
        records, subgroup_records = [], []
        for block in protocol['blocks']:
            columns = CORE_FEATURES + [c for c in PREDICTOR_ALLOWLIST if c in block['columns']]
            for task in TARGETS:
                for fold in range(5):
                    if attempts >= protocol['stage_fit_ceiling']:
                        raise RuntimeError('Frozen predictive attempt ceiling reached')
                    training, validation = folds[task, fold]
                    job = output / 'jobs' / f'{block["id"]}-{task}-fold{fold}'
                    job.mkdir(parents=True)
                    candidate = config['selected'][task]
                    write_json({'block': block, 'task': task, 'fold': fold, 'columns': columns,
                                'candidate': candidate, 'training_n': len(training), 'validation_n': len(validation),
                                'training_ids_sha256': ids_digest(training.order_id),
                                'validation_ids_sha256': ids_digest(validation.order_id)}, job / 'configuration.json')
                    training[['order_id']].to_csv(job / 'training_ids.csv', index=False)
                    coverage = [{'role': role, 'column': col, 'n': len(frame), 'missing_n': int(frame[col].isna().sum())}
                                for role, frame in [('training', training), ('validation', validation)] for col in columns]
                    pd.DataFrame(coverage).to_csv(job / 'coverage.csv', index=False)
                    pipe = make_pipeline(task, candidate, config['baseline_config'], columns)
                    attempts += 1
                    event(output, 'fit_started', 'Fit fixed candidate with one added block.',
                          job=str(job.relative_to(output)), attempt=attempts)
                    notices = []
                    started = time.monotonic()
                    try:
                        with warnings.catch_warnings(record=True) as caught:
                            warnings.simplefilter('always')
                            pipe.fit(training[columns], training[TARGETS[task]])
                            if any(issubclass(w.category, ConvergenceWarning) for w in caught):
                                raise RuntimeError('Convergence warning; invalid trial stopped')
                            scores = {role: score(task, pipe, frame[columns])
                                      for role, frame in [('training_resubstitution', training), ('validation', validation)]}
                        notices = [{'category': w.category.__name__, 'message': str(w.message)} for w in caught]
                        seconds = time.monotonic() - started
                        reference = references[task, fold]
                        for partition, frame in [('training_resubstitution', training), ('validation', validation)]:
                            m = metrics(task, frame[TARGETS[task]], scores[partition])
                            row = {'block': block['id'], 'task': task, 'fold': fold, 'partition': partition,
                                   'candidate': candidate['id'], 'fit_seconds': seconds, **m}
                            if partition == 'validation':
                                key = 'mae' if task == 'regression' else 'average_precision'
                                core = metrics(task, frame[TARGETS[task]], reference)[key]
                                row.update(core_metric=core, paired_gain=core-m[key] if task == 'regression' else m[key]-core)
                            records.append(row)
                        predictions = validation[['order_id', 'customer_unique_id', 'prediction_timestamp', 'n_items', 'customer_state']].copy()
                        predictions['target'] = validation[TARGETS[task]].to_numpy()
                        predictions['prediction'] = scores['validation']
                        predictions['core_reference_prediction'] = reference
                        predictions.to_csv(job / 'validation_predictions.csv', index=False)
                        subgroup_records.extend(subgroup_rows(task, fold, block['id'], validation, scores['validation'], reference, protocol))
                        names = pipe[:-1].get_feature_names_out().tolist()
                        write_json({'transformed_feature_names': names, 'encoded_dimension': len(names),
                                    'raw_predictors': columns, 'fitted_only_on': 'fold_training'}, job / 'pipeline_state.json')
                        joblib.dump(pipe, job / 'pipeline.joblib', compress=3)
                        write_json({'status': 'valid_completed', 'attempt': attempts, 'fit_seconds': seconds,
                                    'pipeline_sha256': sha256_file(job / 'pipeline.joblib'), 'adopted': False}, job / 'completion.json')
                    except Exception as error:
                        if 'caught' in locals():
                            notices = [{'category': w.category.__name__, 'message': str(w.message)} for w in caught]
                        write_json({'status': 'failed_execution_not_valid_evidence', 'attempt': attempts,
                                    'error_type': type(error).__name__, 'error': str(error)}, job / 'failure.json')
                        raise
                    finally:
                        write_json(notices, job / 'warnings.json')
                    pd.DataFrame(records).to_csv(output / 'fold_metrics.csv', index=False)
                    pd.DataFrame(subgroup_records).to_csv(output / 'subgroup_comparisons.csv', index=False)
                    summarize(records, subgroup_records, protocol, output)
                    event(output, 'fit_completed', 'Retain valid comparison whether gain is positive or negative.',
                          attempt=attempts, job=str(job.relative_to(output)), warnings=len(notices))
                    print(f'{attempts}/50 {block["id"]} {task} fold{fold} {seconds:.2f}s', flush=True)
        if attempts != 50:
            raise ValueError('Unexpected fit accounting')
        assert_unchanged(ROOT, identity['protected_hashes'])
        assert_unchanged(ROOT, identity['source_hashes'])
        assert_unchanged(ROOT, identity['core_reference_hashes'])
        write_json({'status': 'screen_complete_pending_independent_verification_and_decisions',
                    'new_predictive_attempts': attempts, 'terminal_scoring_calls': 0,
                    'old_holdout_scoring_calls': 0, 'adopted': False, 'protected_files_unchanged': True}, output / 'run_completion.json')
        event(output, 'screen_completed', '50 block-screen fits complete; no feature adoption or terminal evaluation.',
              next_action='Verify evidence and review task-specific combinations before any followup fits.')
    except Exception as error:
        write_json({'status': 'failed_preserved', 'new_predictive_attempts': attempts,
                    'error_type': type(error).__name__, 'error': str(error), 'adopted': False}, output / 'run_failure.json')
        event(output, 'failure', 'Stop and retain failed attempt; do not hide or overwrite.', error=str(error), attempts=attempts)
        raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    run(args.output.resolve(), args.prepare_only)
