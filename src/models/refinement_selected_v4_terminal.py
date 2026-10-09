"""Terminal evaluation for Refinement Cycle 2 (v4) production run.
Applies frozen production models to out-of-sample terminal evaluation cohorts.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import warnings

import numpy as np
import pandas as pd

from src.common.loaders import sha256_file
from .data import ROOT, TARGETS, load_development
from .io import write_json
from .refinement_selected_v4 import SelectedScorerV4
from .refinement_terminal import terminal_cohorts, paired_intervals
from .finalize import report_metrics, per_class_report, subgroup_tables


def evaluate(run_dir: Path, acknowledge: bool = False):
    if not acknowledge:
        raise ValueError('Explicit --acknowledge-previously-inspected-terminal required')

    run = Path(run_dir).resolve()
    output = run / 'terminal'
    if output.exists():
        raise FileExistsError(f'{output} already exists. Preserve existing terminal evaluation.')

    config = json.loads((run / 'configuration.json').read_text())
    output.mkdir(parents=True)

    bundle_paths = [p for p in (run / 'bundles').rglob('*') if p.is_file()]
    write_json({
        'version': config['version'],
        'cycle': config['cycle'],
        'terminal_cutoff': config['terminal_cutoff'],
        'bundle_hashes': {str(p.relative_to(run)): sha256_file(p) for p in bundle_paths},
        'policy_sha256': sha256_file(run / 'frozen_decision_policy.json')
    }, output / 'evaluation_freeze.json')

    print(f'Evaluating terminal out-of-sample cohorts for {config["version"]}...')
    dev, _, _ = load_development(ROOT)
    reviews = pd.read_csv(
        ROOT / 'data/preprocessed/olist_order_reviews_dataset.csv',
        usecols=['order_id', 'review_score', 'review_answer_timestamp'],
        dtype={'order_id': 'string'}
    )
    _, frames, eligibility = terminal_cohorts(dev, reviews, config['terminal_cutoff'])
    eligibility.to_csv(output / 'eligibility.csv', index=False)

    records = []
    for task in TARGETS:
        frame = frames[task]
        cols = config['predictors_by_task'][task]
        print(f'\nScoring terminal cohort for {task} (N={len(frame)})...')

        for bundle in sorted((run / 'bundles' / task).iterdir()):
            if not bundle.is_dir():
                continue
            role = bundle.name
            scorer = SelectedScorerV4(bundle)

            scored = scorer.score(frame[['order_id'] + cols])
            values = scored['lead_days_prediction'].to_numpy() if task == 'regression' else scored['probability_1'].to_numpy()
            threshold = scorer.policy['threshold'] if task == 'classification' else 0.5

            scored['target'] = frame[TARGETS[task]].to_numpy()
            scored['customer_unique_id'] = frame['customer_unique_id'].to_numpy()
            scored.to_csv(output / f'{task}_{role}_predictions.csv', index=False)

            m = report_metrics(task, frame[TARGETS[task]], values, threshold)
            records.append({'task': task, 'role': role, **m})

            if task == 'regression':
                print(f'  {role:10s} -> MAE: {m["mae"]:.4f} days | RMSE: {m["rmse"]:.4f} | R2: {m.get("r2", float("nan")):.4f}')
            else:
                print(f'  {role:10s} -> AP: {m["average_precision"]:.4f} | ROC-AUC: {m["roc_auc"]:.4f} | F1: {m.get("f1_1", 0.0):.4f} | Cost: {m.get("illustrative_cost_5_to_1", 0):.0f}')

    metrics_df = pd.DataFrame(records)
    metrics_df.to_csv(output / 'metrics.csv', index=False)
    write_json({'status': 'completed', 'cohort_n': {task: len(f) for task, f in frames.items()}}, output / 'completion.json')
    print(f'\nTerminal evaluation complete. Metrics saved to {output / "metrics.csv"}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True, help='Path to run directory')
    parser.add_argument('--acknowledge-previously-inspected-terminal', action='store_true', required=True)
    args = parser.parse_args()
    evaluate(args.run, args.acknowledge_previously_inspected_terminal)
