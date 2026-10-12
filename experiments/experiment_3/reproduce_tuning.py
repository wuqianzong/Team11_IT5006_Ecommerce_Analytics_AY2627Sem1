#!/usr/bin/env python3
"""Reproduce pre/post leakage-remediation tuning without changing accepted evidence."""
from __future__ import annotations
import argparse
import importlib.metadata
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import pandas as pd
from src.common.loaders import sha256_file
from src.models.io import ids_digest
from src.models.refinement_selected_v4_verify import verify, CANONICAL_RUN
from experiments.experiment_3 import run_phase4_transforms_and_tuning as tuning

HISTORICAL_CLASSIFICATION_FEATURES = [
    'n_items', 'has_items', 'n_products', 'total_price', 'total_freight',
    'freight_ratio', 'freight_ratio_missing', 'customer_state', 'purchase_month',
    'purchase_dayofweek', 'purchase_hour', 'n_sellers', 'primary_seller_state',
    'interstate_share',
]


def comparison_tables(output):
    current = pd.read_csv(output / 'current/phase4b_tuning_results.csv')
    old = pd.read_csv(output / 'historical/phase4b_tuning_results.csv')
    report = pd.read_csv(ROOT / 'artifacts/metrics/experiment-3/transforms_and_tuning/phase4b_tuning_results.csv')
    comparison = current.merge(old, on=['task', 'model_family'], suffixes=('_current', '_historical'), validate='one_to_one')
    comparison = comparison.merge(report[['task', 'model_family', 'best_cv_score']], on=['task', 'model_family'], validate='one_to_one')
    comparison = comparison.rename(columns={'best_cv_score': 'reported_score'})
    comparison['same_parameters'] = comparison.best_hyperparameters_current.eq(comparison.best_hyperparameters_historical)
    comparison['current_minus_historical'] = comparison.best_cv_score_current - comparison.best_cv_score_historical
    comparison['historical_minus_reported'] = comparison.best_cv_score_historical - comparison.reported_score
    comparison.to_csv(output / 'classification_before_after.csv', index=False)
    winner_rows = []
    for regime, frame in [('current', current), ('historical', old)]:
        for task, group in frame.groupby('task'):
            ascending = task.startswith('Regression')
            ordered = group.sort_values('best_cv_score', ascending=ascending)
            winner, runner_up = ordered.iloc[0], ordered.iloc[1]
            winner_rows.append({'regime': regime, 'task': task, 'winner': winner.model_family,
                                'parameters': winner.best_hyperparameters, 'score': winner.best_cv_score,
                                'runner_up': runner_up.model_family,
                                'winning_margin': abs(winner.best_cv_score-runner_up.best_cv_score)})
    pd.DataFrame(winner_rows).to_csv(output / 'model_selection.csv', index=False)
    frames = []
    for regime in ['current', 'historical']:
        for path in sorted((output / regime).glob('*_grid.csv')):
            frame = pd.read_csv(path)
            frame.insert(0, 'regime', regime)
            frames.append(frame)
    pd.concat(frames, ignore_index=True).to_csv(output / 'all_grid_candidates.csv', index=False)
    return comparison


def reproduce(output):
    output = Path(output).resolve()
    allowed = (ROOT / 'artifacts/reproduction').resolve()
    if not output.is_relative_to(allowed) or output == allowed:
        raise ValueError('Choose a new subdirectory of artifacts/reproduction')
    if output.exists():
        raise FileExistsError('Output exists; choose an unused directory')
    versions = {p: importlib.metadata.version(p) for p in ['numpy', 'pandas', 'scipy', 'scikit-learn', 'joblib']}
    expected = json.loads((CANONICAL_RUN / 'build_freeze.json').read_text())['packages']
    if versions != expected:
        raise ValueError('Install requirements-milestone2.txt before reproducing tuning')
    f, cv, hashes = tuning.load_development()
    regression = tuning.task_rows(f, cv, 'regression')
    eligible = tuning.task_rows(f, cv, 'classification')
    clean = eligible.loc[eligible.has_items.eq(1)].copy().reset_index(drop=True)
    output.mkdir(parents=True)
    provenance = {'created_utc': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(),
                  'packages': versions, 'seed': 42, 'cv': 'saved five-fold customer-grouped development assignments',
                  'data_hashes': hashes, 'source_hashes': {str(p.relative_to(ROOT)): sha256_file(p) for p in [Path(__file__), Path(tuning.__file__)]},
                  'regression_features': tuning.REG_11_FEATURES,
                  'current_classification_features': tuning.CLF_12_FEATURES,
                  'historical_classification_features': HISTORICAL_CLASSIFICATION_FEATURES,
                  'regression_rows': len(regression), 'current_classification_rows': len(clean),
                  'historical_classification_rows': len(eligible), 'excluded_zero_item_rows': len(eligible)-len(clean),
                  'order_id_digests': {'regression': ids_digest(regression.order_id), 'current': ids_digest(clean.order_id), 'historical': ids_digest(eligible.order_id)},
                  'interpretation': 'Post-submission reruns of two grouped-CV classification setups: historical (14 predictors, 78,938 eligible orders including zero-item orders) and current (12 predictors, 78,334 orders with has_items == 1). Both cohort and feature list differ; final chronological and terminal evaluation are separate stages.'}
    (output / 'provenance.json').write_text(json.dumps(provenance, indent=2))
    tuning.run_phase4b_gridsearch_tuning(regression, clean, output_dir=output / 'current')
    tuning.run_phase4b_gridsearch_tuning(regression, eligible, output_dir=output / 'historical',
                                      clf_features=HISTORICAL_CLASSIFICATION_FEATURES, classification_only=True)
    comparison = comparison_tables(output)
    # Independently verify accepted terminal evidence; never fit or select on terminal labels.
    verify(output_dir=output / 'frozen_final_verification')
    receipt = {'current_configurations': 55, 'historical_classification_configurations': 27,
               'same_classification_parameters': bool(comparison.same_parameters.all()),
               'historical_classification_reproduces_report': bool(comparison.historical_minus_reported.abs().le(1e-10).all()),
               'final_evidence': 'Frozen-model no-fit verification; not a new independent test.',
               'classification_setups_differ_in_cohort_and_features': True}
    (output / 'completion.json').write_text(json.dumps(receipt, indent=2))
    print(json.dumps(receipt, indent=2))
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    reproduce(args.output)


if __name__ == '__main__':
    main()
