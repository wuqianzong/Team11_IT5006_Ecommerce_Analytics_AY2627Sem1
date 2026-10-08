"""Independent saved-prediction checks; never fits or scores terminal outcomes."""
import argparse
import json
from pathlib import Path
import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import average_precision_score, roc_auc_score, brier_score_loss

from src.common.loaders import sha256_file
from src.features.contract import PREDICTOR_ALLOWLIST
from src.models.data import TARGETS
from src.models.io import ids_digest, write_json
from src.models.refinement_core import CORE_FEATURES
from src.models.refinement_temporal import chronological_data
from experiments.feature_selection_v3.runner import canonical_membership, score, SubsetInputContract
from experiments.feature_selection_v3.inputs import load_trial
# Screen invoked with -m serialized the contract under __main__. Exposing the
# exact same class permits local verification without rewriting fitted binaries.
# Before publishing/reusing models, use a stable-module contract and explicit
# compatibility loader; this screen is evidence, not a deployment artifact.

ROOT = Path(__file__).resolve().parents[2]


def close(a, b):
    assert np.allclose(a, b, rtol=1e-10, atol=1e-10, equal_nan=True), (a, b)


def primary(task, y, p):
    return mean_absolute_error(y, p) if task == 'regression' else average_precision_score(y, p)


def verify(folder):
    destination = folder / 'verification'
    if destination.exists():
        raise FileExistsError('Preserve previous verification')
    freeze = json.loads((folder / 'study_freeze.json').read_text())
    protocol, config = freeze['protocol'], freeze['fixed_model_config']
    for category in ['source_hashes', 'core_reference_hashes', 'protected_hashes']:
        for path, expected in freeze[category].items():
            assert sha256_file(ROOT / path) == expected, path
    for filename, expected in freeze['input_hashes'].items():
        assert sha256_file(ROOT / 'data/business/ml' / filename) == expected, filename
    for path, expected in freeze.get('screen_evidence_hashes', {}).items():
        assert sha256_file(ROOT / path) == expected, path
    for path, expected in freeze.get('reused_job_hashes', {}).items():
        assert sha256_file(ROOT / path) == expected, path
    data = chronological_data(ROOT, config)
    membership = pd.read_csv(folder / 'chronological_fold_membership.csv', dtype={'order_id': 'string'})
    assert canonical_membership(membership).equals(canonical_membership(data['membership']))
    fm = pd.read_csv(folder / 'fold_metrics.csv')
    sg = pd.read_csv(folder / 'subgroup_comparisons.csv', dtype={'subgroup': 'string'})
    summary = pd.read_csv(folder / 'block_summary.csv')
    assert len(fm) == 100 and len(summary) == 10
    logs = [json.loads(x) for x in (folder / 'process_log.jsonl').read_text().splitlines()]
    assert sum(x['kind'] == 'fit_started' for x in logs) == 50
    assert sum(x['kind'] == 'fit_completed' for x in logs) == 50
    assert not any(x['kind'] == 'failure' for x in logs)
    checked, gains, warning_counts, checked_subgroups = [], {}, {}, 0
    for block in protocol['blocks']:
        cols = CORE_FEATURES + [c for c in PREDICTOR_ALLOWLIST if c in block['columns']]
        for task in block.get('tasks', list(TARGETS)):
            gains[task, block['id']] = []
            for fold in range(5):
                training, validation = data['folds'][task, fold]
                job = folder / 'jobs' / f'{block["id"]}-{task}-fold{fold}'
                jc = json.loads((job / 'configuration.json').read_text())
                model_spec = block.get('candidate', config['selected'][task])
                assert jc['columns'] == cols and jc['candidate'] == model_spec
                assert jc['training_ids_sha256'] == ids_digest(training.order_id)
                assert jc['validation_ids_sha256'] == ids_digest(validation.order_id)
                train_ids = pd.read_csv(job / 'training_ids.csv', dtype={'order_id': 'string'})
                assert train_ids.order_id.tolist() == training.order_id.tolist()
                pred = pd.read_csv(job / 'validation_predictions.csv', dtype={'order_id': 'string'})
                assert pred.order_id.tolist() == validation.order_id.tolist()
                assert not pred.order_id.duplicated().any()
                close(pred.target, validation[TARGETS[task]])
                assert pd.to_datetime(pred.prediction_timestamp).lt(pd.Timestamp(config['terminal_cutoff'])).all()
                assert not set(training.customer_unique_id) & set(validation.customer_unique_id)
                ref_folder = ROOT / protocol['baseline_evidence'] / 'jobs' / f'E01-{task}-{config["selected"][task]["id"]}-fold{fold}'
                ref = pd.read_csv(ref_folder / 'validation_predictions.csv', dtype={'order_id': 'string'}).set_index('order_id')
                close(pred.core_reference_prediction, ref.loc[pred.order_id, 'prediction'])
                y, p, core = pred.target.to_numpy(), pred.prediction.to_numpy(), pred.core_reference_prediction.to_numpy()
                row = fm[(fm.block == block['id']) & (fm.task == task) & (fm.fold == fold) & (fm.partition == 'validation')]
                assert len(row) == 1
                row = row.iloc[0]
                independently = ({'mae': mean_absolute_error(y, p), 'rmse': np.sqrt(mean_squared_error(y, p)), 'r2': r2_score(y, p)}
                                 if task == 'regression' else {'average_precision': average_precision_score(y, p), 'roc_auc': roc_auc_score(y, p), 'brier': brier_score_loss(y, p)})
                for key, value in independently.items():
                    close(row[key], value)
                baseline = primary(task, y, core)
                gain = baseline - primary(task, y, p) if task == 'regression' else primary(task, y, p) - baseline
                close(row.core_metric, baseline)
                close(row.paired_gain, gain)
                gains[task, block['id']].append(gain)
                baskets = np.select([pred.n_items.eq(0), pred.n_items.eq(1), pred.n_items.between(2, 3)], ['0', '1', '2-3'], default='4+')
                group_rows = sg[(sg.block == block['id']) & (sg.task == task) & (sg.fold == fold)]
                for dimension, values in {'customer_state': pred.customer_state.fillna('Unknown').to_numpy(), 'basket_size': baskets}.items():
                    for label in sorted(set(values)):
                        mask = values == label
                        record = group_rows[(group_rows.dimension == dimension) & (group_rows.subgroup == label)]
                        assert len(record) == 1
                        r = record.iloc[0]
                        positive = int((y[mask] == 1).sum())
                        negative = int(mask.sum()) - positive
                        defined = task == 'regression' or min(positive, negative) > 0
                        support = int(mask.sum()) >= protocol['minimum_subgroup_n'] and (task == 'regression' or min(positive, negative) >= protocol['minimum_subgroup_class_n'])
                        assert r.n == int(mask.sum()) and bool(r.metric_defined) == defined and bool(r.support_sufficient) == support
                        if defined:
                            base, candidate = primary(task, y[mask], core[mask]), primary(task, y[mask], p[mask])
                            harm = candidate - base if task == 'regression' else base - candidate
                            close(r.core_metric, base); close(r.candidate_metric, candidate); close(r.harm, harm)
                            assert bool(r.substantial_harm_flag) == bool(support and harm > protocol['subgroup_harm'][task])
                        else:
                            assert pd.isna(r.harm) and not r.substantial_harm_flag
                        checked_subgroups += 1
                completion = json.loads((job / 'completion.json').read_text())
                assert completion['status'] == 'valid_completed' and not completion['adopted']
                assert sha256_file(job / 'pipeline.joblib') == completion['pipeline_sha256']
                notices = json.loads((job / 'warnings.json').read_text())
                assert not any(w['category'] == 'ConvergenceWarning' for w in notices)
                for w in notices:
                    warning_counts[w['message']] = warning_counts.get(w['message'], 0) + 1
                pipe = load_trial(job / 'pipeline.joblib')
                assert list(pipe.named_steps['inputs'].columns) == cols
                active = [c for _, _, columns in pipe.named_steps['preprocess'].transformers_ for c in columns]
                assert set(active) == set(cols)
                normalized = pipe.named_steps['inputs'].transform(training[cols])
                pre = pipe.named_steps['preprocess']
                numeric_cols = pre.transformers_[0][2]
                categorical_cols = pre.transformers_[1][2]
                numeric = pre.named_transformers_['numeric']
                imputer = numeric.named_steps['impute']
                expected_medians = normalized[numeric_cols].median().fillna(0).to_numpy()
                close(imputer.statistics_, expected_medians)
                assert np.array_equal(imputer.indicator_.features_, np.flatnonzero(normalized[numeric_cols].isna().any().to_numpy()))
                if 'scale' in numeric.named_steps:
                    imputed_training = imputer.transform(normalized[numeric_cols])
                    close(numeric.named_steps['scale'].mean_, imputed_training.mean(axis=0))
                    close(numeric.named_steps['scale'].var_, imputed_training.var(axis=0))
                encoder = pre.named_transformers_['categorical']
                for col, categories in zip(categorical_cols, encoder.categories_):
                    assert list(categories) == sorted(normalized[col].unique().tolist())
                params = pipe.named_steps['model'].get_params()
                if 'baseline_model' in model_spec:
                    base_model = model_spec['baseline_model']
                    expected_params = ({'strategy': 'median' if task == 'regression' else 'prior'} if base_model == 'dummy'
                                       else config['baseline_config']['tree'] if base_model == 'tree'
                                       else config['baseline_config']['linear'] if task == 'regression'
                                       else {**config['baseline_config']['logistic'], 'C': np.inf})
                else:
                    expected_params = model_spec['params']
                for key, value in expected_params.items():
                    assert params[key] == value, (key, params[key], value)
                state = json.loads((job / 'pipeline_state.json').read_text())
                assert pipe[:-1].get_feature_names_out().tolist() == state['transformed_feature_names']
                # Disallow even an accidental top-level refit during saved-model parity.
                pipe.fit = lambda *a, **k: (_ for _ in ()).throw(AssertionError('Verification must not fit'))
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', UserWarning)
                    close(score(task, pipe, validation.iloc[:32][cols]), p[:32])
                checked.append({'job': job.name, 'validation_n': len(pred), 'saved_model_parity_n': 32})
    assert checked_subgroups == len(sg)
    for r in summary.itertuples():
        a = np.array(gains[r.task, r.block])
        vals = fm[(fm.task == r.task) & (fm.block == r.block) & (fm.partition == 'validation')]
        close(r.paired_gain_mean, a.mean()); close(r.candidate_mean, vals[r.metric].mean())
        close(r.candidate_sd, vals[r.metric].std(ddof=1)); close(r.core_mean, vals.core_metric.mean())
        assert r.improving_folds == (a > 0).sum()
        assert r.promising_screen_flag == bool(a.mean() > protocol['practical_gain'][r.task] and (a > 0).sum() >= protocol['required_improving_folds'])
        assert r.subgroup_harm_flags == sg[(sg.task == r.task) & (sg.block == r.block)].substantial_harm_flag.sum()
        assert not r.adopted and not r.availability_certified
    completion = json.loads((folder / 'run_completion.json').read_text())
    assert completion['new_predictive_attempts'] == 50 and completion['terminal_scoring_calls'] == 0 and not completion['adopted']
    destination.mkdir()
    write_json({'status': 'passed', 'jobs_checked': checked, 'subgroups_checked': checked_subgroups,
                'source_reference_input_and_accepted_hashes_unchanged': True,
                'saved_predictions_and_paired_summaries_recomputed': True,
                'training_only_imputer_encoder_scaler_statistics_checked': True,
                'saved_pipeline_parity_rows_per_job': 32, 'captured_warnings': warning_counts,
                'verification_fits': 0, 'terminal_scoring_calls': 0,
                'verifier_sha256': sha256_file(Path(__file__)),
                'trial_inventory': {str(p.relative_to(folder)): sha256_file(p) for p in folder.rglob('*') if p.is_file() and destination not in p.parents}},
               destination / 'verification.json')
    print(f'PASS: {len(checked)} jobs, {checked_subgroups} subgroup comparisons, zero fits/terminal scoring')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    verify(parser.parse_args().input.resolve())
