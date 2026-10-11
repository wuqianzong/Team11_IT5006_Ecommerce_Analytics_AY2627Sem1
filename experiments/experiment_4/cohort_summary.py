"""Reproduce raw cohort summaries for the report from accepted membership IDs; no fits."""
from pathlib import Path
import argparse
import hashlib
import json
import pandas as pd
from src.models.data import ROOT


def summarize(run, output):
    if output.exists():
        raise FileExistsError('Use a fresh output directory; preserve previous summaries')
    feature_file = ROOT / 'data/business/ml/orders_ml_features.csv'
    hashes = json.loads((run / 'input_hashes.json').read_text())
    if hashlib.sha256(feature_file.read_bytes()).hexdigest() != hashes['orders_ml_features.csv']:
        raise ValueError('Feature input differs from the accepted run')
    base = pd.read_csv(feature_file, dtype={'order_id': 'string'}).set_index('order_id', verify_integrity=True)
    selected = json.loads((run / 'selection_freeze.json').read_text())['selected']
    cohorts = {}
    for task in ['regression', 'classification']:
        training = pd.read_csv(run / f'{task}_final_training_ids.csv', dtype={'order_id': 'string'})
        terminal = pd.read_csv(run / 'terminal' / f'{task}_{selected[task]["id"]}_predictions.csv', dtype={'order_id': 'string'})
        for partition, frame in [('training', training), ('terminal', terminal)]:
            if frame.order_id.isna().any() or frame.order_id.duplicated().any():
                raise ValueError('Invalid membership identifiers')
            cohorts[task, partition] = base.loc[frame.order_id].copy()
        if set(training.order_id) & set(terminal.order_id):
            raise ValueError('Training and terminal memberships overlap')
    numeric, states, baskets, sellers, targets = [], [], [], [], []
    features = ['total_price', 'total_freight', 'freight_ratio', 'n_items', 'purchase_hour', 'distance_km_max']
    for partition in ['training', 'terminal']:
        regression = cohorts['regression', partition]
        for feature in features:
            values = regression[feature]
            numeric.append({'partition': partition, 'feature': feature, 'n': len(values), 'missing_pct': 100*values.isna().mean(), 'mean': values.mean(), 'median': values.median(), 'sd': values.std(ddof=1), 'min': values.min(), 'max': values.max(), 'skew': values.skew(), 'mode': values.mode().iloc[0] if values.notna().any() else None})
        for state, n in regression.customer_state.value_counts(dropna=False).items():
            states.append({'partition': partition, 'state': state, 'n': int(n), 'share_pct': 100*n/len(regression)})
        basket = pd.cut(regression.n_items, [0, 1, 3, float('inf')], labels=['1 item', '2-3 items', '4+ items'])
        for label, n in basket.value_counts(sort=False).items():
            baskets.append({'partition': partition, 'basket': label, 'n': int(n), 'share_pct': 100*n/len(regression)})
        sellers.append({'partition': partition, 'n': len(regression), 'primary_seller_SP_share_pct': 100*regression.primary_seller_state.eq('SP').mean(), 'mean_interstate_share_pct': 100*regression.interstate_share.mean()})
        lead = regression.lead_days
        targets.append({'partition': partition, 'task': 'regression', 'n': len(lead), 'mean': lead.mean(), 'median': lead.median(), 'sd': lead.std(ddof=1), 'min': lead.min(), 'max': lead.max(), 'skew': lead.skew()})
        detractor = cohorts['classification', partition].is_detractor
        targets.append({'partition': partition, 'task': 'classification', 'n': len(detractor), 'positives': int(detractor.sum()), 'prevalence_pct': 100*detractor.mean()})
    output.mkdir(parents=True)
    for name, records in [('numeric_stats', numeric), ('state_shares', states), ('basket_shares', baskets), ('seller_stats', sellers), ('target_stats', targets)]:
        pd.DataFrame(records).to_csv(output / f'{name}.csv', index=False)
    (output / 'verification.json').write_text(json.dumps({'status': 'passed', 'feature_input_sha256': hashes['orders_ml_features.csv'], 'cohort_counts': {task: {partition: len(cohorts[task, partition]) for partition in ['training', 'terminal']} for task in ['regression', 'classification']}, 'no_new_fits': True}, indent=2))
    print(f'Raw cohort summaries saved to {output}; no models fitted')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    summarize(args.run.resolve(), args.output.resolve())
