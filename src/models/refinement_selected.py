"""Reproduce frozen refined choices, fit bundles, and score without private docs."""
import argparse
import importlib.metadata
import json
from pathlib import Path
import sys
import warnings
import joblib
import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from src.common.loaders import sha256_file
from .data import ROOT, TARGETS
from .evaluate import metrics
from .io import write_json, ids_digest
from .pipelines import positive_probability
from .policy import select_cost_threshold, threshold_curve, apply_threshold
from .refinement_temporal import chronological_data
from .refinement_inputs import SelectedInputs, selected_pipeline
from .score import checked_manifest

CONFIG = Path(__file__).with_name('configs') / 'refinement_selected_v3.json'


def probabilities(task, pipe, X):
    return pipe.predict(X) if task == 'regression' else positive_probability(pipe, X)


def fit_checked(pipe, X, y):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        pipe.fit(X, y)
    notices = [{'category': w.category.__name__, 'message': str(w.message)} for w in caught]
    if any(issubclass(w.category, ConvergenceWarning) for w in caught):
        raise RuntimeError('Unconverged fit; stop without changing parameters')
    return notices


def build(output, config_path=CONFIG):
    if output.exists():
        raise FileExistsError('Use a new versioned output; do not overwrite accepted runs')
    config = json.loads(config_path.read_text())
    if config['terminal_evaluation_allowed']:
        raise ValueError('Fit configuration must prohibit terminal selection')
    data = chronological_data(ROOT, config)
    output.mkdir(parents=True)
    write_json(config, output / 'configuration.json')
    paths = list((ROOT / 'src/models').glob('*.py')) + list((ROOT / 'src/features').glob('*.py')) + list((ROOT / 'src/common').glob('*.py')) + [config_path]
    source_hashes = {str(p.relative_to(ROOT)): sha256_file(p) for p in paths}
    write_json({'source_hashes': source_hashes, 'input_hashes': data['input_hashes'],
                'review_source_sha256': sha256_file(ROOT / 'data/preprocessed/olist_order_reviews_dataset.csv'),
                'python': sys.version, 'packages': {p: importlib.metadata.version(p) for p in ['numpy', 'pandas', 'scikit-learn', 'scipy', 'joblib', 'matplotlib']},
                'chronological_terminal_used_for_selection': False}, output / 'build_freeze.json')
    data['membership'].to_csv(output / 'chronological_fold_membership.csv', index=False)
    data['exclusions'].to_csv(output / 'chronological_exclusions.csv', index=False)
    records, attempts, oof = [], [], {}
    try:
        for task in TARGETS:
            cols, candidate = config['predictors_by_task'][task], config['selected'][task]
            collected = []
            for fold in range(5):
                train, val = data['folds'][task, fold]
                job = output / 'development' / task / f'fold{fold}'
                job.mkdir(parents=True)
                pipe = selected_pipeline(task, candidate, config['baseline_config'], cols)
                attempts.append({'task': task, 'phase': 'development_confirmation', 'fold': fold, 'status': 'started'})
                write_json(attempts, output / 'fit_attempts.json')
                notices = fit_checked(pipe, train[cols], train[TARGETS[task]])
                write_json(notices, job / 'fit_warnings.json')
                for partition, frame in [('training_resubstitution', train), ('validation', val)]:
                    values = probabilities(task, pipe, frame[cols])
                    records.append({'task': task, 'fold': fold, 'partition': partition, **metrics(task, frame[TARGETS[task]], values)})
                    if partition == 'validation':
                        pred = frame[['order_id', 'customer_unique_id', 'prediction_timestamp', 'customer_state', 'n_items']].copy()
                        pred['target'], pred['prediction'] = frame[TARGETS[task]].to_numpy(), values
                        pred.to_csv(job / 'validation_predictions.csv', index=False)
                        collected.append(pred)
                joblib.dump(pipe, job / 'pipeline.joblib', compress=3)
                train[['order_id']].to_csv(job / 'training_ids.csv', index=False)
                attempts[-1]['status'] = 'completed'
                print('Confirmed', task, fold, flush=True)
            oof[task] = pd.concat(collected, ignore_index=True)
            if oof[task].order_id.duplicated().any():
                raise ValueError('Repeated validation order')
            metric = 'mae' if task == 'regression' else 'average_precision'
            mean = np.mean([r[metric] for r in records if r['task'] == task and r['partition'] == 'validation'])
            if not np.isclose(mean, config['expected_validation_primary'][task], rtol=1e-10, atol=1e-10):
                raise ValueError('Production subset differs from frozen development choice')
            oof[task].to_csv(output / f'{task}_development_oof.csv', index=False)
        pd.DataFrame(records).to_csv(output / 'development_fold_metrics.csv', index=False)
        cls = oof['classification']
        cutoff, policy_metrics = select_cost_threshold(cls.target, cls.prediction, config['policy_cost_ratio'])
        policy = {'kind': 'fixed_threshold', 'positive_class': 1, 'comparison': '>=', 'threshold': cutoff,
                  'cost_ratio_fn_to_fp': config['policy_cost_ratio'], 'cost_assumption': 'illustrative, not measured business loss',
                  'selection_population': 'Previously explored preterminal chronological OOF after model choice; not independent',
                  'tie_break': 'highest threshold among equal integer costs', 'OOF_report': policy_metrics}
        write_json(policy, output / 'frozen_decision_policy.json')
        threshold_curve(cls.target, cls.prediction).to_csv(output / 'policy_threshold_curve.csv', index=False)
        pd.DataFrame([{'ratio': ratio, 'threshold': select_cost_threshold(cls.target, cls.prediction, ratio)[0],
                       **select_cost_threshold(cls.target, cls.prediction, ratio)[1]} for ratio in [1, 2, 5, 10]]).to_csv(output / 'policy_scenarios.csv', index=False)
        for task in TARGETS:
            training, cols = data['final_training'][task], config['predictors_by_task'][task]
            training[['order_id', 'customer_unique_id', 'prediction_timestamp']].to_csv(output / f'{task}_training_ids.csv', index=False)
            candidates = [('selected', config['selected'][task]), ('dummy', {'id': 'baseline_dummy', 'family': 'dummy', 'baseline_model': 'dummy'}),
                          ('linear', {'id': 'baseline_linear', 'family': 'linear', 'baseline_model': 'linear'}), ('forest', config['forest_reference'])]
            if task == 'classification':
                candidates.append(('tree', {'id': 'baseline_tree', 'family': 'tree', 'baseline_model': 'tree'}))
            for role, candidate in candidates:
                job = output / 'bundles' / task / role
                job.mkdir(parents=True)
                pipe = selected_pipeline(task, candidate, config['baseline_config'], cols)
                attempts.append({'task': task, 'phase': 'final_fit', 'role': role, 'status': 'started'})
                write_json(attempts, output / 'fit_attempts.json')
                notices = fit_checked(pipe, training[cols], training[TARGETS[task]])
                joblib.dump(pipe, job / 'pipeline.joblib', compress=3)
                write_json({'version': config['version'], 'task': task, 'predictor_allowlist': cols,
                            'input_units': 'original units; see unchanged base feature schema', 'missing_columns': 'reject', 'null_cells': 'allow'}, job / 'feature_schema.json')
                write_json({'task': task, 'role': role, 'model_version': config['version'], 'training_n': len(training),
                            'training_ids_sha256': ids_digest(training.order_id), 'terminal_cutoff': config['terminal_cutoff'],
                            'limitations': config['limitations']}, job / 'metadata.json')
                write_json({'candidate': candidate, 'baseline_config': config['baseline_config']}, job / 'configuration.json')
                normalized = pipe.named_steps['inputs'].transform(training[cols])
                write_json({c: {'missing_n': int(training[c].isna().sum()), 'normalized_counts': normalized[c].value_counts().to_dict()}
                            if normalized[c].dtype == object else {'missing_n': int(training[c].isna().sum()), 'median': normalized[c].median(), 'mean': normalized[c].mean(), 'std': normalized[c].std()} for c in cols}, job / 'feature_stats.json')
                write_json(notices, job / 'fit_warnings.json')
                names = pipe[:-1].get_feature_names_out().tolist()
                write_json({'transformed_feature_names': names, 'raw_predictors': cols, 'encoded_dimension': len(names)}, job / 'pipeline_state.json')
                if task == 'classification':
                    write_json(policy if role == 'selected' else {**policy, 'threshold': .5, 'selection_population': 'fixed descriptive baseline policy'}, job / 'decision_policy.json')
                sample = training.iloc[:64][cols]
                if not np.allclose(probabilities(task, pipe, sample), probabilities(task, joblib.load(job / 'pipeline.joblib'), sample), rtol=1e-12, atol=1e-12):
                    raise ValueError('Saved pipeline parity failed')
                write_json({'output_hashes': {p.name: sha256_file(p) for p in job.iterdir() if p.is_file()}}, job / 'bundle_manifest.json')
                attempts[-1]['status'] = 'completed'
                print('Final fitted', task, role, len(training), flush=True)
        assert len(attempts) == config['application_fit_ceiling'] == 19
        write_json(attempts, output / 'fit_attempts.json')
        write_json({'status': 'built_pending_independent_verification', 'new_fits': len(attempts), 'terminal_scoring_calls': 0,
                    'cycle_total_fits': 263 + 100 + 50 + len(attempts), 'validation_matches_frozen_choices': True}, output / 'build_completion.json')
    except Exception as error:
        write_json({'error_type': type(error).__name__, 'error': str(error), 'attempted_fits': len(attempts)}, output / 'build_failure.json')
        raise


class SelectedScorer:
    """Trusted bundle scoring; checksum is integrity, not protection from malicious pickle."""
    def __init__(self, bundle):
        self.bundle = Path(bundle)
        checked_manifest(self.bundle)
        self.metadata = json.loads((self.bundle / 'metadata.json').read_text())
        schema = json.loads((self.bundle / 'feature_schema.json').read_text())
        self.task, self.cols = schema['task'], schema['predictor_allowlist']
        if self.task != self.metadata['task'] or schema['version'] != 'refinement-selected-v3':
            raise ValueError('Wrong task/version')
        self.pipeline = joblib.load(self.bundle / 'pipeline.joblib')
        if list(self.pipeline.named_steps['inputs'].columns) != self.cols:
            raise ValueError('Pipeline/schema disagreement')
        self.policy = json.loads((self.bundle / 'decision_policy.json').read_text()) if self.task == 'classification' else None

    def score(self, frame):
        if not isinstance(frame, pd.DataFrame) or frame.columns.duplicated().any() or set(frame.columns) != {'order_id', *self.cols}:
            raise ValueError('order_id plus exactly task predictors required')
        ids = frame.order_id.astype('string')
        if ids.isna().any() or ids.str.strip().eq('').any() or ids.duplicated().any():
            raise ValueError('Missing/blank/duplicate order ID')
        values = probabilities(self.task, self.pipeline, frame[self.cols])
        if not np.isfinite(values).all():
            raise ValueError('Nonfinite predictions')
        result = pd.DataFrame({'order_id': ids.to_numpy(), 'task': self.task, 'model_version': self.metadata['model_version']})
        if self.policy:
            result['probability_1'], result['decision'], result['threshold'] = values, apply_threshold(values, self.policy), self.policy['threshold']
        else:
            result['lead_days_prediction'] = values
        return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    b = sub.add_parser('build'); b.add_argument('--output', type=Path, required=True)
    s = sub.add_parser('score'); s.add_argument('--bundle', type=Path, required=True); s.add_argument('--input', type=Path, required=True); s.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'build':
        build(args.output.resolve())
    else:
        if args.output.exists():
            raise FileExistsError('Scoring output exists')
        SelectedScorer(args.bundle).score(pd.read_csv(args.input, dtype={'order_id': 'string'})).to_csv(args.output, index=False)
