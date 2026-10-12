"""Verify the submitted Milestone 2 evidence using frozen models; never fit.

The recorded terminal cohort has already been inspected. This reproduces its
published results, not a new independent test or a new model-selection run.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from src.common.loaders import sha256_file
from .data import ROOT, TARGETS, load_development
from .finalize import report_metrics
from .io import ids_digest, write_json
from .refinement_terminal import terminal_cohorts
from .refinement_selected_v4 import SelectedScorerV4

CANONICAL_RUN = ROOT / 'artifacts/metrics/refinement-selected-v4'


def output_location(run: Path, destination: Path | None) -> Path:
    """Never overwrite canonical inputs or a previous verification receipt."""
    output = (destination or ROOT / 'artifacts/reproduction' /
              ('milestone2-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))).resolve()
    for protected in [run.resolve(), ROOT / 'data', ROOT / 'src', ROOT / 'docs']:
        if output.is_relative_to(protected.resolve()) or protected.resolve().is_relative_to(output):
            raise ValueError('Verification output must be outside source/evidence directories')
    if output.exists():
        raise FileExistsError('Verification output already exists; choose a new directory')
    return output


def compare_tables(actual: pd.DataFrame, expected: pd.DataFrame,
                   keys: list[str], tolerance: float = 1e-9) -> pd.DataFrame:
    """Compare keyed metric tables, including row coverage and missing values."""
    if actual.duplicated(keys).any() or expected.duplicated(keys).any():
        raise ValueError('Duplicate metric keys')
    a, e = actual.set_index(keys), expected.set_index(keys)
    if set(a.index) != set(e.index):
        raise ValueError('Reproduced and published metric rows differ')
    a = a.reindex(e.index)
    rows = []
    for column in e.columns:
        if column not in a:
            raise ValueError('Missing reproduced column: ' + column)
        left = pd.to_numeric(a[column], errors='coerce').astype(float)
        right = pd.to_numeric(e[column], errors='coerce').astype(float)
        if not right.notna().any():
            continue
        valid = np.isclose(left, right, rtol=0, atol=tolerance, equal_nan=True)
        rows.append({'column': column, 'entries': len(e),
                     'max_absolute_difference': float((left-right).abs().max()),
                     'passed': bool(valid.all())})
    if not rows:
        raise ValueError('No numeric metrics compared')
    return pd.DataFrame(rows)


def verify(run_dir: Path = CANONICAL_RUN, output_dir: Path | None = None):
    from .refinement_selected_v4_terminal import (
        build_train_val_test_comparison, compute_subgroups,
        plot_classification_diagnostics, plot_regression_diagnostics,
    )
    run = Path(run_dir).resolve()
    output = output_location(run, output_dir)
    frozen = json.loads((run / 'build_freeze.json').read_text())
    versions = {p: importlib.metadata.version(p) for p in frozen['packages']}
    if versions != frozen['packages']:
        raise ValueError('Use requirements-milestone2.txt: numerical package versions differ from the frozen run')
    evaluation = json.loads((run / 'terminal/evaluation_freeze.json').read_text())
    config = json.loads((run / 'configuration.json').read_text())
    policy = json.loads((run / 'frozen_decision_policy.json').read_text())
    for relative, digest in evaluation['bundle_hashes'].items():
        if sha256_file(run / relative) != digest:
            raise ValueError('Frozen bundle differs from published evaluation: ' + relative)
    if sha256_file(run / 'frozen_decision_policy.json') != evaluation['policy_sha256']:
        raise ValueError('Frozen decision policy differs from published evaluation')
    for name, digest in frozen['input_hashes'].items():
        if sha256_file(ROOT / 'data/business/ml' / name) != digest:
            raise ValueError('Frozen dataset input changed: ' + name)

    required = ['configuration.json', 'build_freeze.json', 'frozen_decision_policy.json',
                'development_fold_metrics.csv', 'regression_training_ids.csv',
                'classification_training_ids.csv', 'classification_development_oof.csv',
                'terminal/evaluation_freeze.json', 'terminal/metrics.csv',
                'terminal/subgroups.csv', 'terminal/train_val_test_comparison.csv',
                'terminal/regression_selected_predictions.csv',
                'terminal/classification_selected_predictions.csv']
    inputs = {name: sha256_file(run / name) for name in required}
    inputs.update({name: sha256_file(run / name) for name in evaluation['bundle_hashes']})
    dev, _, _ = load_development(ROOT)
    reviews = pd.read_csv(ROOT / 'data/preprocessed/olist_order_reviews_dataset.csv',
                          usecols=['order_id', 'review_score', 'review_answer_timestamp'],
                          dtype={'order_id': 'string'})
    _, frames, _ = terminal_cohorts(dev, reviews, config['terminal_cutoff'])
    output.mkdir(parents=True)
    records, subgroup_rows, prediction_checks, target_rows, basket_rows = [], [], [], [], []
    for task in TARGETS:
        frame = frames[task]
        training_ids = pd.read_csv(run / f'{task}_training_ids.csv', dtype={'order_id': 'string'})
        if training_ids.order_id.isna().any() or training_ids.order_id.duplicated().any():
            raise ValueError('Invalid training IDs: ' + task)
        if set(training_ids.order_id) & set(frame.order_id):
            raise ValueError('Training/terminal IDs overlap: ' + task)
        training = dev.loc[dev.order_id.isin(training_ids.order_id)]
        if len(training) != len(training_ids):
            raise ValueError('Training IDs do not match saved development data: ' + task)
        for partition, cohort in [('training', training), ('terminal', frame)]:
            target = cohort[TARGETS[task]]
            target_rows.append({'task': task, 'partition': partition, 'n': len(cohort),
                                'target_mean': float(target.mean()), 'target_median': float(target.median()),
                                'positive_n': int(target.sum()) if task == 'classification' else None})
            if task == 'regression':
                for label, mask in [('1 item', cohort.n_items.eq(1)),
                                    ('2–3 items', cohort.n_items.between(2, 3)),
                                    ('4+ items', cohort.n_items.ge(4))]:
                    basket_rows.append({'partition': partition, 'basket': label,
                                        'n': int(mask.sum()), 'cohort_n': len(cohort),
                                        'share': float(mask.mean())})
        for bundle in sorted((run / 'bundles' / task).iterdir()):
            if not bundle.is_dir():
                continue
            scorer = SelectedScorerV4(bundle)
            if ids_digest(training_ids.order_id) != scorer.metadata['training_ids_sha256']:
                raise ValueError('Training-ID digest mismatch: ' + task + '/' + bundle.name)
            scored = scorer.score(frame[['order_id'] + config['predictors_by_task'][task]])
            prediction_col = 'lead_days_prediction' if task == 'regression' else 'probability_1'
            values = scored[prediction_col].to_numpy()
            threshold = scorer.policy['threshold'] if task == 'classification' else 0.5
            records.append({'task': task, 'role': bundle.name,
                            **report_metrics(task, frame[TARGETS[task]], values, threshold)})
            scored['target'] = frame[TARGETS[task]].to_numpy()
            scored['customer_unique_id'] = frame.customer_unique_id.to_numpy()
            scored.to_csv(output / f'{task}_{bundle.name}_predictions.csv', index=False)
            if bundle.name == 'selected':
                published = pd.read_csv(run / f'terminal/{task}_selected_predictions.csv',
                                        dtype={'order_id': 'string'})
                aligned = scored.merge(published, on='order_id', how='outer',
                                       suffixes=('_new', '_published'), indicator=True,
                                       validate='one_to_one')
                if not aligned['_merge'].eq('both').all():
                    raise ValueError('Terminal prediction cohort mismatch: ' + task)
                for col in [prediction_col, 'target']:
                    passed = np.allclose(aligned[col+'_new'], aligned[col+'_published'],
                                         rtol=0, atol=1e-10)
                    prediction_checks.append({'task': task, 'column': col, 'passed': bool(passed),
                                              'max_absolute_difference': float(np.max(np.abs(
                                                  aligned[col+'_new']-aligned[col+'_published'])))})
                subgroup_rows.extend(compute_subgroups(task, frame, values, threshold))
                if task == 'regression':
                    plot_regression_diagnostics(output, frame[TARGETS[task]].to_numpy(), values, frame)
                else:
                    if threshold != policy['threshold']:
                        raise ValueError('Selected threshold differs from frozen policy')
                    plot_classification_diagnostics(output, frame[TARGETS[task]].to_numpy(), values, threshold)

    metrics = pd.DataFrame(records)
    metrics.to_csv(output / 'metrics.csv', index=False)
    pd.DataFrame(target_rows).to_csv(output / 'table_f4_target_statistics.csv', index=False)
    pd.DataFrame(basket_rows).to_csv(output / 'table_f3_basket_counts.csv', index=False)
    subgroup = pd.DataFrame(subgroup_rows)
    subgroup['ranking_support_sufficient'] = (
        subgroup.n.ge(100) & subgroup.get('positives', pd.Series(100, index=subgroup.index)).ge(20))
    subgroup.to_csv(output / 'subgroups.csv', index=False)
    comparisons = []
    for name, actual, keys in [('metrics', metrics, ['task', 'role']),
                                ('subgroups', subgroup, ['task', 'dimension', 'subgroup'])]:
        result = compare_tables(actual, pd.read_csv(run / f'terminal/{name}.csv'), keys)
        comparisons.append(result.assign(table=name))
    build_train_val_test_comparison(run, output)
    comparisons.append(compare_tables(pd.read_csv(output / 'train_val_test_comparison.csv'),
                                      pd.read_csv(run / 'terminal/train_val_test_comparison.csv'),
                                      ['task', 'metric']).assign(table='train_val_test_comparison'))
    comparison = pd.concat(comparisons, ignore_index=True)
    comparison.to_csv(output / 'metric_comparison.csv', index=False)

    # Preserve exact saved probabilities at a recorded threshold boundary.
    oof = pd.read_csv(run / 'classification_development_oof.csv', float_precision='round_trip')
    fixed = report_metrics('classification', oof.target, oof.prediction, policy['threshold'])
    recorded_optimum = report_metrics('classification', oof.target, oof.prediction,
                                      policy['empirical_optimal_threshold'])
    if recorded_optimum['illustrative_cost_5_to_1'] != policy['OOF_report']['illustrative_cost']:
        raise ValueError('Stored OOF optimum cost cannot be reproduced')
    write_json({'frozen_threshold': policy['threshold'], 'frozen_policy_metrics': fixed,
                'recorded_empirical_threshold': policy['empirical_optimal_threshold'],
                'recorded_threshold_metrics': recorded_optimum,
                'threshold_reselected': False}, output / 'oof_policy_verification.json')
    unchanged = all(sha256_file(run / name) == digest for name, digest in inputs.items())
    passed = bool(comparison.passed.all() and all(c['passed'] for c in prediction_checks) and unchanged)
    receipt = {'passed': passed, 'new_fits': 0, 'new_threshold_searches': 0,
               'independent_new_test': False, 'canonical_evidence_unchanged': unchanged,
               'cohort_n': {task: len(frame) for task, frame in frames.items()},
               'model_rows': len(metrics), 'subgroup_rows': len(subgroup),
               'prediction_checks': prediction_checks,
               'python': platform.python_version(), 'packages': versions,
               'source_sha256': {str(p.relative_to(ROOT)): sha256_file(p) for p in
                                 [Path(__file__), ROOT / 'src/models/refinement_selected_v4.py',
                                  ROOT / 'src/models/refinement_selected_v4_terminal.py']},
               'evidence_sha256': inputs,
               'meaning': 'Reproduction of previously inspected submitted results, with frozen models and policy.'}
    write_json(receipt, output / 'verification.json')
    if not passed:
        raise ValueError('Reproduction differs from published evidence; inspect ' + str(output))
    print(f'PASS: {len(metrics)} model rows, {len(subgroup)} subgroup rows; no training or policy search.\nOutputs: {output}')
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, default=CANONICAL_RUN)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    verify(args.run, args.output)


if __name__ == '__main__':
    main()
