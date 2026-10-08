"""Paired incremental comparisons against smaller tested feature sets."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, mean_absolute_error
from .runner import ROOT
from src.models.io import write_json
from src.common.loaders import sha256_file

PAIRS = {
    'regression': [('seller_distance', 'seller'), ('seller_distance', 'distance'),
                   ('seller_distance_physical', 'seller_distance'), ('seller_distance_category', 'seller_distance'),
                   ('all_nonpayment', 'seller_distance_physical'), ('all_nonpayment', 'seller_distance_category'),
                   ('seller_distance_payment', 'seller_distance'), ('full27', 'all_nonpayment')],
    'classification': [('seller_category', 'seller'), ('seller_distance', 'seller'),
                       ('seller_category_distance', 'seller_category'), ('seller_category_distance', 'seller_distance'),
                       ('all_nonpayment', 'seller_category_distance')]
}


def measure(task, y, p):
    return mean_absolute_error(y, p) if task == 'regression' else average_precision_score(y, p)


def compare(folder):
    assert json.loads((folder / 'verification/verification.json').read_text())['status'] == 'passed'
    destination = folder / 'incremental_comparisons'
    if destination.exists():
        raise FileExistsError('Preserve earlier comparisons')
    protocol = json.loads((folder / 'study_freeze.json').read_text())['protocol']
    screen = ROOT / protocol['screen_evidence']
    rows, subgroups, sources = [], [], {}
    for task, pairs in PAIRS.items():
        for added, smaller in pairs:
            for fold in range(5):
                a = folder / 'jobs' / f'{added}-{task}-fold{fold}' / 'validation_predictions.csv'
                reference_root = screen if smaller in {'seller', 'distance'} else folder
                b = reference_root / 'jobs' / f'{smaller}-{task}-fold{fold}' / 'validation_predictions.csv'
                sources[str(a.relative_to(ROOT))] = sha256_file(a)
                sources[str(b.relative_to(ROOT))] = sha256_file(b)
                x, y = [pd.read_csv(p, dtype={'order_id': 'string'}) for p in (a, b)]
                assert not x.order_id.duplicated().any() and not y.order_id.duplicated().any()
                assert set(x.order_id) == set(y.order_id)
                y = y.set_index('order_id').loc[x.order_id].reset_index()
                assert np.array_equal(x.target, y.target)
                base, candidate = measure(task, x.target, y.prediction), measure(task, x.target, x.prediction)
                gain = base-candidate if task == 'regression' else candidate-base
                rows.append({'task': task, 'candidate': added, 'comparator': smaller, 'fold': fold,
                             'n': len(x), 'base_metric': base, 'candidate_metric': candidate, 'paired_gain': gain})
                basket = np.select([x.n_items.eq(0), x.n_items.eq(1), x.n_items.between(2, 3)], ['0', '1', '2-3'], default='4+')
                for dimension, values in {'customer_state': x.customer_state.fillna('Unknown').to_numpy(), 'basket_size': basket}.items():
                    for label in sorted(set(values)):
                        mask = values == label
                        target = x.target.to_numpy()[mask]
                        positive, negative = int((target == 1).sum()), int((target == 0).sum())
                        defined = task == 'regression' or min(positive, negative) > 0
                        supported = int(mask.sum()) >= protocol['minimum_subgroup_n'] and (task == 'regression' or min(positive, negative) >= protocol['minimum_subgroup_class_n'])
                        harm = None
                        if defined:
                            c, r = measure(task, target, x.prediction.to_numpy()[mask]), measure(task, target, y.prediction.to_numpy()[mask])
                            harm = c-r if task == 'regression' else r-c
                        subgroups.append({'task': task, 'candidate': added, 'comparator': smaller, 'fold': fold,
                                          'dimension': dimension, 'subgroup': label, 'n': int(mask.sum()),
                                          'support_sufficient': supported, 'metric_defined': defined, 'harm': harm,
                                          'substantial_harm_flag': bool(defined and supported and harm > protocol['subgroup_harm'][task])})
    frame, groups = pd.DataFrame(rows), pd.DataFrame(subgroups)
    summaries = []
    for (task, candidate, comparator), values in frame.groupby(['task', 'candidate', 'comparator']):
        gain = values.paired_gain
        harms = groups[(groups.task == task) & (groups.candidate == candidate) & (groups.comparator == comparator)]
        summaries.append({'task': task, 'candidate': candidate, 'comparator': comparator, 'paired_gain_mean': gain.mean(),
                          'improving_folds': int(gain.gt(0).sum()),
                          'incremental_practical_flag': bool(gain.mean() > protocol['practical_gain'][task] and gain.gt(0).sum() >= 4),
                          'subgroup_harm_flags': int(harms.substantial_harm_flag.sum()), 'adopted': False})
    destination.mkdir()
    frame.to_csv(destination / 'fold_comparisons.csv', index=False)
    groups.to_csv(destination / 'subgroup_comparisons.csv', index=False)
    pd.DataFrame(summaries).to_csv(destination / 'summary.csv', index=False)
    write_json({'status': 'complete', 'matched_fold_pairs': len(frame), 'new_fits': 0,
                'terminal_scoring_calls': 0, 'input_hashes': sources, 'code_sha256': sha256_file(Path(__file__))}, destination / 'completion.json')
    print(pd.DataFrame(summaries).to_string(index=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    compare(parser.parse_args().input.resolve())
