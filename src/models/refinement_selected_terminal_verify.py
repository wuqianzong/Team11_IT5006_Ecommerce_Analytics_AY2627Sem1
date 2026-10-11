"""Recompute terminal metrics/eligibility from saved predictions; no fits/scores."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from src.common.loaders import sha256_file
from .data import ROOT, TARGETS, load_development
from .evaluate import metrics
from .io import write_json
from .refinement_terminal import terminal_cohorts
from .policy import apply_threshold


def verify(run):
    folder = run / 'terminal'
    destination = folder / 'verification.json'
    if destination.exists():
        raise FileExistsError('Preserve recorded verification')
    freeze = json.loads((folder / 'evaluation_freeze.json').read_text())
    for rel, digest in freeze['bundle_hashes'].items():
        assert sha256_file(run / rel) == digest, rel
    assert sha256_file(run / 'frozen_decision_policy.json') == freeze['policy_sha256']
    config = json.loads((run / 'configuration.json').read_text())
    dev, _, _ = load_development(ROOT)
    reviews = pd.read_csv(ROOT / 'data/preprocessed/olist_order_reviews_dataset.csv', usecols=['order_id', 'review_score', 'review_answer_timestamp'], dtype={'order_id': 'string'})
    _, frames, eligibility = terminal_cohorts(dev, reviews, config['terminal_cutoff'])
    saved = pd.read_csv(folder / 'eligibility.csv', dtype={'order_id': 'string'})
    assert saved[['task', 'order_id', 'included', 'reason']].astype(str).equals(eligibility[['task', 'order_id', 'included', 'reason']].astype(str))
    table = pd.read_csv(folder / 'metrics.csv')
    assert len(table) == 9
    checked = []
    for row in table.itertuples():
        frame = frames[row.task]
        pred = pd.read_csv(folder / f'{row.task}_{row.role}_predictions.csv', dtype={'order_id': 'string'})
        assert pred.order_id.tolist() == frame.order_id.tolist()
        assert not pred.order_id.duplicated().any()
        np.testing.assert_array_equal(pred.target, frame[TARGETS[row.task]])
        values = pred.lead_days_prediction if row.task == 'regression' else pred.probability_1
        threshold = .5 if row.task == 'regression' else float(pred.threshold.iloc[0])
        actual = metrics(row.task, pred.target, values, threshold)
        keys = ['mae', 'rmse', 'r2', 'negative_predictions'] if row.task == 'regression' else ['average_precision', 'roc_auc', 'brier', 'tp', 'fp', 'tn', 'fn']
        for key in keys:
            assert np.isclose(getattr(row, key), actual[key], rtol=1e-10, atol=1e-10), (row.task, row.role, key)
        if row.task == 'classification':
            np.testing.assert_array_equal(pred.decision, apply_threshold(values, {'kind': 'fixed_threshold', 'positive_class': 1, 'threshold': threshold}))
        checked.append({'task': row.task, 'role': row.role, 'n': len(pred), 'metrics_and_decisions_recomputed': True})
    assert len(frames['regression']) == 15615 and len(frames['classification']) == 15807
    groups = pd.read_csv(folder / 'subgroups.csv', dtype={'subgroup': 'string'})
    for task, frame in frames.items():
        p = pd.read_csv(folder / f'{task}_selected_predictions.csv')
        values = p.lead_days_prediction.to_numpy() if task == 'regression' else p.probability_1.to_numpy()
        threshold = .5 if task == 'regression' else p.threshold.iloc[0]
        basket = np.select([frame.n_items.eq(0), frame.n_items.eq(1), frame.n_items.between(2, 3)], ['0', '1', '2-3'], default='4+')
        dimensions = {'customer_state': frame.customer_state.fillna('unknown').astype(str), 'basket_size': pd.Series(basket),
                      'purchase_month': frame.prediction_timestamp.dt.to_period('M').astype(str)}
        if task == 'regression':
            dimensions['observed_duration_days'] = pd.cut(frame.lead_days, [0, 7, 14, 30, np.inf], labels=['0-7', '7-14', '14-30', '30+']).astype(str)
        for r in groups[groups.task == task].itertuples():
            mask = dimensions[r.dimension].eq(r.subgroup).to_numpy()
            assert r.n == mask.sum()
            if mask.any():
                expected = metrics(task, frame.loc[mask, TARGETS[task]], values[mask], threshold)
                key = 'mae' if task == 'regression' else 'average_precision'
                if expected[key] is not None:
                    assert np.isclose(getattr(r, key), expected[key], rtol=1e-10, atol=1e-10)
    write_json({'status': 'passed', 'checked': checked, 'subgroup_rows_checked': len(groups), 'new_fits': 0,
                'model_scoring_calls': 0, 'previously_inspected_diagnostic_only': True, 'selection_or_policy_changed': False,
                'code_sha256': sha256_file(Path(__file__)),
                'artifact_hashes': {str(p.relative_to(folder)): sha256_file(p) for p in folder.rglob('*') if p.is_file()}}, destination)
    print('PASS:9 terminal models, exact eligibility/cohorts, policy decisions and selected subgroups; zero fits')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    verify(parser.parse_args().run.resolve())
