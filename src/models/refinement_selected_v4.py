"""Refinement Cycle 2 (v4) Production Module:
Implements Experiment 3 champion architectures, preprocessing, tuning, and calibrated threshold policy.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
from pathlib import Path
import shutil
import sys
import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.exceptions import ConvergenceWarning
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from src.common.loaders import sha256_file
from .data import ROOT, TARGETS, load_development
from .evaluate import metrics
from .io import write_json, ids_digest
from .pipelines import normalize_inputs
from .policy import select_cost_threshold, threshold_curve, apply_threshold
from .refinement_temporal import chronological_data
from .refinement_inputs import SelectedInputs
from .score import checked_manifest

CONFIG_PATH = Path(__file__).with_name('configs') / 'refinement_selected_v4.json'


def build_v4_pipeline(task: str, candidate_role: str, candidate_config: dict, columns: list[str], baseline_config: dict):
    """Construct an end-to-end scikit-learn Pipeline incorporating log1p transformations."""
    family = candidate_config.get('family', 'forest')
    seed = baseline_config.get('seed', 42)
    is_linear = family in {'linear', 'ridge', 'logistic'}

    # Identify continuous skewed features vs standard numeric vs categoricals
    if task == 'regression':
        skewed_cols = [c for c in ['total_price', 'total_freight', 'distance_km_max'] if c in columns]
        other_num_cols = [c for c in columns if c not in skewed_cols and c != 'customer_state']
        cat_cols = [c for c in ['customer_state'] if c in columns]
    else:
        skewed_cols = [c for c in ['total_price', 'total_freight'] if c in columns]
        other_num_cols = [c for c in columns if c not in skewed_cols and c not in {'customer_state', 'primary_seller_state'}]
        cat_cols = [c for c in ['customer_state', 'primary_seller_state'] if c in columns]

    transformers = []
    if skewed_cols:
        skewed_steps = [
            ('log1p', FunctionTransformer(np.log1p, feature_names_out='one-to-one')),
            ('impute', SimpleImputer(strategy='median'))
        ]
        if is_linear:
            skewed_steps.append(('scale', StandardScaler()))
        transformers.append(('skewed_num', Pipeline(skewed_steps), skewed_cols))

    if other_num_cols:
        num_steps = [('impute', SimpleImputer(strategy='median', add_indicator=True))]
        if is_linear:
            num_steps.append(('scale', StandardScaler()))
        transformers.append(('standard_num', Pipeline(num_steps), other_num_cols))

    if cat_cols:
        transformers.append(('categorical', OneHotEncoder(handle_unknown='ignore', drop='first' if is_linear else None, sparse_output=False), cat_cols))

    preprocessor = ColumnTransformer(transformers, remainder='drop', verbose_feature_names_out=True)

    # Base estimator selection
    if candidate_role == 'dummy':
        estimator = DummyRegressor(strategy='median') if task == 'regression' else DummyClassifier(strategy='prior')
    elif candidate_role == 'linear':
        if task == 'regression':
            estimator = Ridge(alpha=1.0, random_state=seed)
        else:
            estimator = LogisticRegression(C=0.01, max_iter=2000, solver='lbfgs', random_state=seed)
    elif candidate_role == 'tree':
        cls = DecisionTreeRegressor if task == 'regression' else DecisionTreeClassifier
        estimator = cls(max_depth=5, min_samples_leaf=100, random_state=seed)
    else:  # 'selected' or 'forest'
        params = candidate_config.get('params', {'n_estimators': 50, 'max_depth': 14, 'min_samples_leaf': 20})
        cls = RandomForestRegressor if task == 'regression' else RandomForestClassifier
        estimator = cls(
            n_estimators=params.get('n_estimators', 50),
            max_depth=params.get('max_depth', 14),
            min_samples_leaf=params.get('min_samples_leaf', 20),
            random_state=seed,
            n_jobs=1
        )

    # Wrap regression in TransformedTargetRegressor if specified
    if task == 'regression' and candidate_config.get('target_transform') == 'log1p':
        full_pipe = TransformedTargetRegressor(
            regressor=Pipeline([
                ('inputs', SelectedInputs(tuple(columns))),
                ('preprocess', preprocessor),
                ('model', estimator)
            ]),
            func=np.log1p,
            inverse_func=np.expm1
        )
    else:
        full_pipe = Pipeline([
            ('inputs', SelectedInputs(tuple(columns))),
            ('preprocess', preprocessor),
            ('model', estimator)
        ])

    return full_pipe


def predict_values(task: str, pipe, X: pd.DataFrame) -> np.ndarray:
    """Predict point estimates for regression or positive class probability for classification."""
    if task == 'regression':
        return pipe.predict(X)
    else:
        if hasattr(pipe, 'predict_proba'):
            return pipe.predict_proba(X)[:, 1]
        elif hasattr(pipe, 'named_steps') and hasattr(pipe.named_steps['model'], 'predict_proba'):
            return pipe.predict_proba(X)[:, 1]
        else:
            return pipe.predict(X).astype(float)


def fit_checked(pipe, X: pd.DataFrame, y: np.ndarray | pd.Series, task: str, candidate_config: dict) -> list[dict]:
    """Fit model while clipping outliers if specified and checking convergence."""
    y_train = np.asarray(y, dtype=float)
    if task == 'regression' and candidate_config.get('target_winsorize_days'):
        clip_val = float(candidate_config['target_winsorize_days'])
        y_train = np.clip(y_train, a_min=None, a_max=clip_val)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        pipe.fit(X, y_train)

    notices = [{'category': w.category.__name__, 'message': str(w.message)} for w in caught]
    if any(issubclass(w.category, ConvergenceWarning) for w in caught):
        raise RuntimeError('Unconverged fit during production pipeline training')
    return notices


def build(output_dir: Path, config_path: Path = CONFIG_PATH, overwrite: bool = False):
    """Build Refinement Cycle 2 (v4) models, cross-validation metrics, decision policies, and bundles."""
    output = Path(output_dir).resolve()
    if output.exists():
        if overwrite:
            shutil.rmtree(output)
        else:
            raise FileExistsError(f'Output directory {output} already exists. Do not overwrite accepted runs.')

    config = json.loads(Path(config_path).read_text())
    output.mkdir(parents=True)
    write_json(config, output / 'configuration.json')

    print(f'Building Refinement Cycle 2 ({config["version"]}) at {output}...')
    data = chronological_data(ROOT, config)

    # Freeze sources and environment
    paths = list((ROOT / 'src/models').glob('*.py')) + list((ROOT / 'src/features').glob('*.py')) + [Path(config_path)]
    source_hashes = {str(p.relative_to(ROOT)): sha256_file(p) for p in paths if p.is_file()}
    write_json({
        'source_hashes': source_hashes,
        'input_hashes': data['input_hashes'],
        'python': sys.version,
        'packages': {p: importlib.metadata.version(p) for p in ['numpy', 'pandas', 'scikit-learn', 'scipy', 'joblib']},
        'version': config['version'],
        'cycle': config['cycle']
    }, output / 'build_freeze.json')

    records, attempts, oof = [], [], {}

    # Phase A: 5-Fold Chronological Confirmation
    for task in TARGETS:
        cols = config['predictors_by_task'][task]
        candidate = config['selected'][task]
        collected = []
        print(f'\nRunning 5-fold chronological cross-validation for {task}...')

        for fold in range(5):
            train, val = data['folds'][task, fold]
            job_dir = output / 'development' / task / f'fold{fold}'
            job_dir.mkdir(parents=True)

            pipe = build_v4_pipeline(task, 'selected', candidate, cols, config['baseline_config'])
            attempts.append({'task': task, 'phase': 'development_confirmation', 'fold': fold, 'status': 'started'})

            notices = fit_checked(pipe, train[cols], train[TARGETS[task]], task, candidate)
            write_json(notices, job_dir / 'fit_warnings.json')

            for partition, frame in [('training_resubstitution', train), ('validation', val)]:
                preds = predict_values(task, pipe, frame[cols])
                m = metrics(task, frame[TARGETS[task]], preds)
                records.append({'task': task, 'fold': fold, 'partition': partition, **m})

                if partition == 'validation':
                    pred_df = frame[['order_id', 'customer_unique_id', 'prediction_timestamp']].copy()
                    pred_df['target'] = frame[TARGETS[task]].to_numpy()
                    pred_df['prediction'] = preds
                    pred_df.to_csv(job_dir / 'validation_predictions.csv', index=False)
                    collected.append(pred_df)

            joblib.dump(pipe, job_dir / 'pipeline.joblib', compress=3)
            attempts[-1]['status'] = 'completed'
            metric_key = 'mae' if task == 'regression' else 'average_precision'
            val_score = [r[metric_key] for r in records if r['task'] == task and r['fold'] == fold and r['partition'] == 'validation'][-1]
            print(f'  Fold {fold} confirmed: {metric_key.upper()} = {val_score:.4f}')

        oof[task] = pd.concat(collected, ignore_index=True)
        oof[task].to_csv(output / f'{task}_development_oof.csv', index=False)

    pd.DataFrame(records).to_csv(output / 'development_fold_metrics.csv', index=False)

    # Phase B: Calibrated Decision Policy
    cls_oof = oof['classification']
    fixed_threshold = float(config.get('policy_fixed_threshold', 0.17))
    ratio = config.get('policy_cost_ratio', 5)
    cutoff_opt, policy_metrics = select_cost_threshold(cls_oof.target, cls_oof.prediction, ratio)

    policy = {
        'kind': 'fixed_threshold',
        'positive_class': 1,
        'comparison': '>=',
        'threshold': fixed_threshold,
        'empirical_optimal_threshold': cutoff_opt,
        'cost_ratio_fn_to_fp': ratio,
        'cost_assumption': 'illustrative business cost ratio (FN=5, FP=1)',
        'selection_population': 'Chronological OOF evaluation from Refinement Cycle 2',
        'decision_policy_version': 'v4-asymmetric-calibrated',
        'OOF_report': policy_metrics
    }
    write_json(policy, output / 'frozen_decision_policy.json')
    threshold_curve(cls_oof.target, cls_oof.prediction).to_csv(output / 'policy_threshold_curve.csv', index=False)

    # Phase C: Final Production Fit on Pre-Terminal Training Data
    print('\nTraining and serializing final production model bundles on pre-terminal data...')
    for task in TARGETS:
        training = data['final_training'][task]
        cols = config['predictors_by_task'][task]
        training[['order_id', 'customer_unique_id', 'prediction_timestamp']].to_csv(output / f'{task}_training_ids.csv', index=False)

        candidates = [
            ('selected', config['selected'][task]),
            ('dummy', {'id': 'baseline_dummy', 'family': 'dummy'}),
            ('linear', config.get('linear_reference', {}).get(task, {'id': 'tuned_linear', 'family': 'linear'})),
            ('forest', config.get('forest_reference', {'id': 'rf_reference', 'family': 'forest'}))
        ]
        if task == 'classification':
            candidates.append(('tree', {'id': 'baseline_tree', 'family': 'tree'}))

        for role, cand in candidates:
            bundle_dir = output / 'bundles' / task / role
            bundle_dir.mkdir(parents=True)

            pipe = build_v4_pipeline(task, role, cand, cols, config['baseline_config'])
            attempts.append({'task': task, 'phase': 'final_fit', 'role': role, 'status': 'started'})

            notices = fit_checked(pipe, training[cols], training[TARGETS[task]], task, cand)
            joblib.dump(pipe, bundle_dir / 'pipeline.joblib', compress=3)

            write_json({
                'version': config['version'],
                'cycle': config['cycle'],
                'task': task,
                'role': role,
                'predictor_allowlist': cols,
                'input_units': 'Standard raw units; log1p scaling encapsulated in pipeline'
            }, bundle_dir / 'feature_schema.json')

            write_json({
                'task': task,
                'role': role,
                'model_version': config['version'],
                'training_n': len(training),
                'training_ids_sha256': ids_digest(training.order_id),
                'terminal_cutoff': config['terminal_cutoff'],
                'limitations': config['limitations']
            }, bundle_dir / 'metadata.json')

            if task == 'classification':
                role_policy = policy if role == 'selected' else {**policy, 'threshold': 0.5, 'selection_population': 'default threshold'}
                write_json(role_policy, bundle_dir / 'decision_policy.json')

            # Verify bundle parity
            sample = training.iloc[:64][cols]
            pred_orig = predict_values(task, pipe, sample)
            loaded_pipe = joblib.load(bundle_dir / 'pipeline.joblib')
            pred_loaded = predict_values(task, loaded_pipe, sample)
            if not np.allclose(pred_orig, pred_loaded, rtol=1e-10, atol=1e-10):
                raise ValueError(f'Pipeline serialization parity failed for {task}/{role}')

            write_json({'output_hashes': {p.name: sha256_file(p) for p in bundle_dir.iterdir() if p.is_file()}}, bundle_dir / 'bundle_manifest.json')
            attempts[-1]['status'] = 'completed'
            print(f'  Final bundle ready: {task}/{role} (N={len(training)})')

    write_json(attempts, output / 'fit_attempts.json')
    write_json({'status': 'built_and_verified', 'version': config['version'], 'new_fits': len(attempts)}, output / 'build_completion.json')
    print(f'\nRefinement Cycle 2 build complete successfully at {output}')


class SelectedScorerV4:
    """Production scoring interface for Refinement Cycle 2 (v4) bundles."""
    def __init__(self, bundle_dir: Path | str):
        self.bundle = Path(bundle_dir).resolve()
        manifest = json.loads((self.bundle / 'bundle_manifest.json').read_text())
        for name, digest in manifest['output_hashes'].items():
            if sha256_file(self.bundle / name) != digest:
                raise ValueError(f'Bundle checksum mismatch: {name}')
        self.metadata = json.loads((self.bundle / 'metadata.json').read_text())
        schema = json.loads((self.bundle / 'feature_schema.json').read_text())
        self.task = schema['task']
        self.cols = schema['predictor_allowlist']
        self.pipeline = joblib.load(self.bundle / 'pipeline.joblib')
        self.policy = json.loads((self.bundle / 'decision_policy.json').read_text()) if self.task == 'classification' else None

    def score(self, frame: pd.DataFrame) -> pd.DataFrame:
        if not isinstance(frame, pd.DataFrame) or frame.columns.duplicated().any():
            raise ValueError('Unique named DataFrame columns required')
        if not set(self.cols).issubset(set(frame.columns)):
            raise ValueError(f'Missing required predictor columns: {set(self.cols) - set(frame.columns)}')
        if 'order_id' not in frame.columns:
            raise ValueError('order_id column required for scoring')

        ids = frame['order_id'].astype('string')
        preds = predict_values(self.task, self.pipeline, frame[self.cols])

        result = pd.DataFrame({
            'order_id': ids.to_numpy(),
            'task': self.task,
            'model_version': self.metadata['model_version']
        })

        if self.task == 'regression':
            result['lead_days_prediction'] = preds
        else:
            result['probability_1'] = preds
            result['threshold'] = self.policy['threshold']
            result['decision'] = apply_threshold(preds, self.policy)
        return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    b = sub.add_parser('build')
    b.add_argument('--output', type=Path, required=True, help='Destination directory for the v4 bundle')
    b.add_argument('--config', type=Path, default=CONFIG_PATH, help='Configuration JSON path')
    b.add_argument('--overwrite', action='store_true', help='Allow overwriting existing output directory')
    args = parser.parse_args()

    if args.command == 'build':
        build(args.output, args.config, overwrite=args.overwrite)
