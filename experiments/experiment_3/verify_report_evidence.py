"""Recalculate report audit tables from frozen data, without fitting models.

Run from the repository root:
    python experiments/experiment_3/verify_report_evidence.py
Outputs are written to artifacts/metrics/report-evidence-exp3/.
"""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'artifacts/metrics/report-evidence-exp3')
    args = parser.parse_args()
    paths = {
        'features': ROOT / 'data/business/ml/orders_ml_features.csv',
        'splits': ROOT / 'data/business/ml/split_assignments.csv',
        'training_ids': ROOT / 'artifacts/metrics/refinement-selected-v4/regression_training_ids.csv',
        'terminal_predictions': ROOT / 'artifacts/metrics/refinement-selected-v4/terminal/regression_selected_predictions.csv',
    }
    frames = {name: pd.read_csv(path, dtype={'order_id': 'string'}) for name, path in paths.items()}
    for name, frame in frames.items():
        if frame.order_id.isna().any() or frame.order_id.duplicated().any():
            raise ValueError(f'{name}: order IDs must be unique and nonmissing')
    base = frames['features'].merge(frames['splits'][['order_id', 'split_assignment']],
                                  on='order_id', validate='one_to_one')
    if len(base) != len(frames['features']) or len(base) != len(frames['splits']):
        raise ValueError('Feature and split ID sets differ')
    train_ids = frames['training_ids'].order_id
    test_ids = frames['terminal_predictions'].order_id
    if set(train_ids) & set(test_ids):
        raise ValueError('Training and terminal cohorts overlap')
    cohorts = {}
    for name, ids in [('train', train_ids), ('terminal', test_ids)]:
        subset = base[base.order_id.isin(ids)].copy()
        if len(subset) != len(ids) or not subset.eligible_regression.eq(1).all():
            raise ValueError(f'{name}: unmatched or ineligible orders')
        cohorts[name] = subset
    development = base.loc[base.split_assignment.eq('development') & base.eligible_regression.eq(1), 'lead_days']
    lead_summary = {
        'cohort': 'eligible regression in saved outer development split; raw target',
        'n': int(len(development)), 'mean': float(development.mean()),
        'minimum': float(development.min()), 'maximum': float(development.max()),
        'skewness': float(development.skew()), 'excess_kurtosis': float(development.kurt()),
        'estimator': 'pandas bias-corrected sample skewness and excess kurtosis',
        'training_cap_days': 60,
    }
    features = ['total_price', 'total_freight', 'freight_ratio', 'n_items', 'purchase_hour', 'distance_km_max']
    rows = []
    for feature in features:
        for statistic in ['mean', 'median', 'std', 'missing_pct']:
            values = []
            for name in ['train', 'terminal']:
                col = cohorts[name][feature]
                values.append(float(col.isna().mean() * 100 if statistic == 'missing_pct' else getattr(col, statistic)()))
            tr, te = values
            rows.append({'feature': feature, 'statistic': statistic, 'train_n': len(train_ids),
                         'terminal_n': len(test_ids), 'train_value': tr, 'terminal_value': te,
                         'drift': te-tr if statistic == 'missing_pct' else (100*(te/tr-1) if tr != 0 else None),
                         'drift_unit': 'percentage points' if statistic == 'missing_pct' else 'percent'})
    zero = base.loc[base.n_items.eq(0)].copy()
    before = pd.to_datetime(zero.prediction_timestamp, utc=True) < pd.Timestamp('2018-05-25', tz='UTC')
    groups = {
        'development': zero.split_assignment.eq('development'),
        'holdout_before_terminal': zero.split_assignment.eq('holdout') & before,
        'terminal_holdout': zero.split_assignment.eq('holdout') & ~before,
    }
    zero_rows = []
    for name, mask in groups.items():
        zero_rows.append({'partition': name, 'all_zero_item_orders': int(mask.sum()),
                          'eligible_classification_orders': int((mask & zero.eligible_classification.eq(1)).sum())})
    if sum(x['all_zero_item_orders'] for x in zero_rows) != len(zero):
        raise ValueError('Zero-item partition decomposition is incomplete')
    labelled = zero.loc[zero.eligible_classification.eq(1)]
    ratio = base.freight_ratio
    valid = base.total_price.gt(0) & base.total_price.notna() & base.total_freight.notna()
    if not np.allclose(ratio[valid], base.loc[valid, 'total_freight']/base.loc[valid, 'total_price']):
        raise ValueError('freight_ratio does not match its contract')
    summary = {
        'lead_days': lead_summary,
        'zero_item': {'all_n': len(zero), 'eligible_n': len(labelled),
                      'detractor_n': int(labelled.is_detractor.sum()),
                      'detractor_rate': float(labelled.is_detractor.mean())},
        'freight_ratio': {'formula': 'total_freight / total_price', 'maximum': float(ratio.max()),
                          'observed_n': int(ratio.notna().sum()), 'above_one_n': int(ratio.gt(1).sum())},
        'cohort_targets': {name: {'n': len(frame), 'lead_mean': float(frame.lead_days.mean()),
                                  'lead_median': float(frame.lead_days.median())} for name, frame in cohorts.items()},
        'input_sha256': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths.values()},
    }
    args.output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output/'table_f1_statistics.csv', index=False)
    pd.DataFrame(zero_rows).to_csv(args.output/'zero_item_counts.csv', index=False)
    (args.output/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(f'No-fit report evidence verified; outputs: {args.output}')


if __name__ == '__main__':
    main()
