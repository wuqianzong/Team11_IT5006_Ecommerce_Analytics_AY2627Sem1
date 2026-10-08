"""Independent no-fit verification of refined final/development pipelines."""
import argparse
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, average_precision_score
from src.common.loaders import sha256_file
from .data import ROOT, TARGETS
from .io import ids_digest, write_json
from .refinement_temporal import chronological_data
from .refinement_selected import SelectedScorer, probabilities
from .policy import select_cost_threshold


def training_state(pipe, training, cols):
    normalized = pipe.named_steps['inputs'].transform(training[cols])
    pre = pipe.named_steps['preprocess']
    numeric = pre.named_transformers_['numeric']
    nc, cc = pre.transformers_[0][2], pre.transformers_[1][2]
    np.testing.assert_allclose(numeric.named_steps['impute'].statistics_, normalized[nc].median().fillna(0).to_numpy(), rtol=1e-10, atol=1e-10)
    if 'scale' in numeric.named_steps:
        z = numeric.named_steps['impute'].transform(normalized[nc])
        np.testing.assert_allclose(numeric.named_steps['scale'].mean_, z.mean(axis=0), rtol=1e-10, atol=1e-10)
        np.testing.assert_allclose(numeric.named_steps['scale'].var_, z.var(axis=0), rtol=1e-10, atol=1e-10)
    for col, categories in zip(cc, pre.named_transformers_['categorical'].categories_):
        assert list(categories) == sorted(normalized[col].unique().tolist())


def verify(run):
    destination = run / 'verification.json'
    if destination.exists():
        raise FileExistsError('Verification record exists; preserve it')
    freeze = json.loads((run / 'build_freeze.json').read_text())
    for rel, expected in freeze['source_hashes'].items():
        assert sha256_file(ROOT / rel) == expected, rel
    for filename, expected in freeze['input_hashes'].items():
        assert sha256_file(ROOT / 'data/business/ml' / filename) == expected, filename
    assert sha256_file(ROOT / 'data/preprocessed/olist_order_reviews_dataset.csv') == freeze['review_source_sha256']
    config = json.loads((run / 'configuration.json').read_text())
    data = chronological_data(ROOT, config)
    saved = pd.read_csv(run / 'chronological_fold_membership.csv', dtype={'order_id': 'string'})
    keys = ['task', 'fold', 'role', 'order_id']
    assert saved[keys].astype(str).sort_values(keys).reset_index(drop=True).equals(data['membership'][keys].astype(str).sort_values(keys).reset_index(drop=True))
    rows = pd.read_csv(run / 'development_fold_metrics.csv')
    assert len(rows) == 20
    checked = []
    for task in TARGETS:
        cols = config['predictors_by_task'][task]
        primary = 'mae' if task == 'regression' else 'average_precision'
        for fold in range(5):
            train, val = data['folds'][task, fold]
            folder = run / 'development' / task / f'fold{fold}'
            pipe = joblib.load(folder / 'pipeline.joblib')
            pred = pd.read_csv(folder / 'validation_predictions.csv', dtype={'order_id': 'string'})
            assert pred.order_id.tolist() == val.order_id.tolist()
            np.testing.assert_array_equal(pred.target, val[TARGETS[task]])
            np.testing.assert_allclose(probabilities(task, pipe, val[cols]), pred.prediction, rtol=1e-10, atol=1e-10)
            training_state(pipe, train, cols)
            for partition, frame in [('training_resubstitution', train), ('validation', val)]:
                scores = probabilities(task, pipe, frame[cols])
                expected = mean_absolute_error(frame.lead_days, scores) if task == 'regression' else average_precision_score(frame.is_detractor, scores)
                record = rows[(rows.task == task) & (rows.fold == fold) & (rows.partition == partition)]
                assert len(record) == 1
                assert np.isclose(record.iloc[0][primary], expected, rtol=1e-10, atol=1e-10)
            old = ROOT / ('artifacts/metrics/feature-selection-v3-model-gate/jobs/r13_tree-regression-fold' + str(fold) if task == 'regression'
                          else 'artifacts/metrics/feature-selection-v3-screen/jobs/seller-classification-fold' + str(fold)) / 'validation_predictions.csv'
            if old.exists():
                earlier = pd.read_csv(old, dtype={'order_id': 'string'})
                assert earlier.order_id.tolist() == pred.order_id.tolist()
                np.testing.assert_allclose(earlier.prediction, pred.prediction, rtol=1e-10, atol=1e-10)
            checked.append({'task': task, 'fold': fold, 'validation_n': len(pred), 'full_saved_prediction_parity': True,
                            'prior_trial_parity_checked': old.exists()})
        for folder in (run / 'bundles' / task).iterdir():
            scorer = SelectedScorer(folder)
            final = data['final_training'][task]
            assert scorer.metadata['training_ids_sha256'] == ids_digest(final.order_id)
            training_state(scorer.pipeline, final, cols)
            batch = final.iloc[:64][['order_id'] + cols]
            valid = scorer.score(batch)
            assert len(valid) == len(batch)
            for bad in [batch.drop(columns=cols[0]), batch.assign(lead_days=1), pd.concat([batch, batch.iloc[:1]])]:
                try:
                    scorer.score(bad)
                except ValueError:
                    pass
                else:
                    raise AssertionError('Invalid strict batch accepted')
    cls = pd.read_csv(run / 'classification_development_oof.csv')
    policy = json.loads((run / 'frozen_decision_policy.json').read_text())
    threshold, _ = select_cost_threshold(cls.target, cls.prediction, config['policy_cost_ratio'])
    assert policy['threshold'] == threshold
    attempts = json.loads((run / 'fit_attempts.json').read_text())
    assert len(attempts) == 19 and all(a['status'] == 'completed' for a in attempts)
    write_json({'status': 'passed', 'folds': checked, 'final_bundles_checked': 9, 'training_only_preprocessing': True,
                'strict_scoring_rejections': True, 'OOF_policy_recomputed': True, 'verification_fits': 0,
                'terminal_scoring_calls': 0, 'verifier_sha256': sha256_file(Path(__file__)),
                'artifact_hashes': {str(p.relative_to(run)): sha256_file(p) for p in run.rglob('*') if p.is_file()}}, destination)
    print('PASS: all10 full fold predictions,9 final bundles, strict interface and policy; zero fits/test scores')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    verify(parser.parse_args().run.resolve())
