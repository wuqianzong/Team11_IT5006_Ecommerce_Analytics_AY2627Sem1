"""Audit reused scores and matched model-family comparisons; no fitting."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, average_precision_score
from .runner import ROOT
from .inputs import load_trial
from src.common.loaders import sha256_file
from src.models.io import write_json


def primary(task, y, p):
    return mean_absolute_error(y, p) if task == 'regression' else average_precision_score(y, p)


def compare(folder):
    assert json.loads((folder / 'verification/verification.json').read_text())['status'] == 'passed'
    output = folder / 'model_comparisons'
    if output.exists():
        raise FileExistsError('Existing comparisons must be preserved')
    freeze = json.loads((folder / 'study_freeze.json').read_text())
    protocol = freeze['protocol']
    for path, expected in freeze['reused_job_hashes'].items():
        assert sha256_file(ROOT / path) == expected, path
    entries = [(b['id'], b['tasks'][0], b['feature_set'], folder, b['id'], False) for b in protocol['blocks']]
    entries += [(r['id'], r['task'], r['feature_set'], ROOT / r['source'], r['block'], True) for r in protocol['reuse']]
    all_rows, predictions, source_hashes, reused_checks = [], {}, {}, []
    fresh_metrics = pd.read_csv(folder / 'fold_metrics.csv')
    for identity, task, feature_set, source, block, reused in entries:
        source_metrics = fresh_metrics if not reused else pd.read_csv(source / 'fold_metrics.csv')
        for fold in range(5):
            job = source / 'jobs' / f'{block}-{task}-fold{fold}'
            config = json.loads((job / 'configuration.json').read_text())
            pred_path = job / 'validation_predictions.csv'
            pred = pd.read_csv(pred_path, dtype={'order_id': 'string'})
            source_hashes[str(pred_path.relative_to(ROOT))] = sha256_file(pred_path)
            assert not pred.order_id.duplicated().any()
            # Every reused cohort must equal the newly verified cohort, not just
            # a row count. Targets and training digests were checked pre-fit.
            anchor_id = next(b['id'] for b in protocol['blocks'] if b['tasks'][0] == task)
            anchor = pd.read_csv(folder / 'jobs' / f'{anchor_id}-{task}-fold{fold}' / 'validation_predictions.csv', dtype={'order_id': 'string'})
            assert pred.order_id.tolist() == anchor.order_id.tolist()
            assert np.array_equal(pred.target, anchor.target)
            metric = 'mae' if task == 'regression' else 'average_precision'
            vals = source_metrics[(source_metrics.block == block) & (source_metrics.task == task) & (source_metrics.fold == fold)]
            assert set(vals.partition) == {'validation', 'training_resubstitution'} and len(vals) == 2
            recorded = vals[vals.partition == 'validation'].iloc[0][metric]
            assert np.isclose(recorded, primary(task, pred.target, pred.prediction), rtol=1e-10, atol=1e-10)
            if reused:
                pipe = load_trial(job / 'pipeline.joblib')
                assert list(pipe.named_steps['inputs'].columns) == config['columns']
                assert len(config['columns']) == {'r13': 13, 'r19': 19, 'c14': 14}[feature_set]
                reused_checks.append({'id': identity, 'fold': fold, 'source': str(job.relative_to(ROOT)), 'metric_recomputed': True})
            predictions[identity, fold] = pred
            for _, row in vals.iterrows():
                all_rows.append({**row.to_dict(), 'id': identity, 'feature_set': feature_set, 'reused': reused})
    metrics = pd.DataFrame(all_rows)
    summaries = []
    for identity, task, feature_set, source, block, reused in entries:
        frame = metrics[metrics.id == identity]
        v, t = frame[frame.partition == 'validation'], frame[frame.partition == 'training_resubstitution']
        metric = 'mae' if task == 'regression' else 'average_precision'
        summaries.append({'id': identity, 'task': task, 'feature_set': feature_set, 'reused': reused,
                          'primary_metric': metric, 'training_mean': t[metric].mean(),
                          'validation_mean': v[metric].mean(), 'validation_sd': v[metric].std(ddof=1),
                          'rmse_mean': v.rmse.mean(), 'r2_mean': v.r2.mean(),
                          'roc_auc_mean': v.roc_auc.mean(), 'brier_mean': v.brier.mean(),
                          'training_validation_gap': v[metric].mean()-t[metric].mean() if task == 'regression' else t[metric].mean()-v[metric].mean()})
    pairs = []
    for fs in ['r13', 'r19']:
        pairs += [(fs+'_ols', fs+'_dummy'), (fs+'_tree', fs+'_dummy'), (fs+'_forest', fs+'_tree'), (fs+'_forest', fs+'_ols')]
    pairs += [('r19_'+m, 'r13_'+m) for m in ['dummy', 'ols', 'tree', 'forest']]
    pairs += [('c14_plain_logistic', 'c14_dummy'), ('c14_regularized_logistic', 'c14_plain_logistic'),
              ('c14_tree', 'c14_dummy'), ('c14_forest', 'c14_tree'), ('c14_forest', 'c14_regularized_logistic')]
    pair_rows, subgroup_rows = [], []
    for candidate, base in pairs:
        task = 'classification' if candidate.startswith('c') else 'regression'
        for fold in range(5):
            x, y = predictions[candidate, fold], predictions[base, fold]
            assert x.order_id.tolist() == y.order_id.tolist() and np.array_equal(x.target, y.target)
            c, b = primary(task, x.target, x.prediction), primary(task, x.target, y.prediction)
            gain = b-c if task == 'regression' else c-b
            pair_rows.append({'task': task, 'candidate': candidate, 'comparator': base, 'fold': fold, 'paired_gain': gain})
            basket = np.select([x.n_items.eq(0), x.n_items.eq(1), x.n_items.between(2, 3)], ['0', '1', '2-3'], default='4+')
            for dimension, values in {'customer_state': x.customer_state.fillna('Unknown').to_numpy(), 'basket_size': basket}.items():
                for label in sorted(set(values)):
                    mask = values == label
                    target = x.target.to_numpy()[mask]
                    defined = task == 'regression' or len(set(target)) == 2
                    supported = mask.sum() >= protocol['minimum_subgroup_n'] and (task == 'regression' or min(int((target == 1).sum()), int((target == 0).sum())) >= protocol['minimum_subgroup_class_n'])
                    harm = None
                    if defined:
                        cv, bv = primary(task, target, x.prediction.to_numpy()[mask]), primary(task, target, y.prediction.to_numpy()[mask])
                        harm = cv-bv if task == 'regression' else bv-cv
                    subgroup_rows.append({'task': task, 'candidate': candidate, 'comparator': base, 'fold': fold,
                                          'dimension': dimension, 'subgroup': label, 'n': int(mask.sum()),
                                          'support_sufficient': bool(supported), 'metric_defined': defined, 'harm': harm,
                                          'substantial_harm_flag': bool(defined and supported and harm > protocol['subgroup_harm'][task])})
    pair_frame, group_frame = pd.DataFrame(pair_rows), pd.DataFrame(subgroup_rows)
    pair_summary = []
    for (task, candidate, base), f in pair_frame.groupby(['task', 'candidate', 'comparator']):
        groups = group_frame[(group_frame.candidate == candidate) & (group_frame.comparator == base)]
        pair_summary.append({'task': task, 'candidate': candidate, 'comparator': base, 'gain_mean': f.paired_gain.mean(),
                             'improving_windows': int(f.paired_gain.gt(0).sum()), 'practical_flag': bool(f.paired_gain.mean() > protocol['practical_gain'][task] and f.paired_gain.gt(0).sum() >= 4),
                             'subgroup_harm_flags': int(groups.substantial_harm_flag.sum())})
    assert len(all_rows) == 130 and len(reused_checks) == 15 and len(pair_rows) == 85
    output.mkdir()
    metrics.to_csv(output / 'all_fold_metrics.csv', index=False)
    pd.DataFrame(summaries).to_csv(output / 'model_summary.csv', index=False)
    pair_frame.to_csv(output / 'paired_folds.csv', index=False)
    group_frame.to_csv(output / 'subgroup_comparisons.csv', index=False)
    pd.DataFrame(pair_summary).to_csv(output / 'paired_summary.csv', index=False)
    write_json({'status': 'passed', 'new_fits': 0, 'new_model_fits_in_run': 50, 'reused_fold_results_checked': reused_checks,
                'matched_pairs': 85, 'terminal_scoring_calls': 0, 'source_prediction_hashes': source_hashes,
                'code_sha256': sha256_file(Path(__file__))}, output / 'completion.json')
    print(pd.DataFrame(summaries).to_string(index=False))
    print(pd.DataFrame(pair_summary).to_string(index=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    compare(parser.parse_args().input.resolve())
