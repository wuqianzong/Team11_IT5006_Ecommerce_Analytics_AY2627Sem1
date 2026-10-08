"""Verify regenerated eight core bundles and initial terminal metrics; no fits."""
import json
import joblib
import numpy as np
import pandas as pd
from src.common.loaders import sha256_file
from src.models.data import ROOT, TARGETS, load_development
from src.models.io import write_json, ids_digest
from src.models.refinement_core import CORE_FEATURES
from src.models.refinement_temporal import chronological_data
from src.models.refinement_score import CoreScorer
from src.models.refinement_terminal import terminal_cohorts
from src.models.refinement_selected_verify import training_state
from src.models.evaluate import metrics
from src.models.policy import select_cost_threshold


def verify_core(folder):
    config = json.loads((ROOT/'src/models/configs/refinement_core_v2.json').read_text())
    data = chronological_data(ROOT, config)
    policy = json.loads((folder/'frozen_decision_policy.json').read_text())
    from .paths import run_root
    source = run_root()/'initial_reference/results'
    cls = pd.concat([pd.read_csv(source/'jobs'/f'E01-classification-{config["selected"]["classification"]["id"]}-fold{f}'/'validation_predictions.csv') for f in range(5)])
    threshold, _ = select_cost_threshold(cls.target, cls.prediction, config['policy_cost_ratio'])
    assert policy['threshold'] == threshold
    for task in TARGETS:
        train = data['final_training'][task]
        for role in ['selected', 'dummy', 'linear', 'tree']:
            job = folder/task/role
            scorer = CoreScorer(job)
            assert scorer.metadata['training_ids_sha256'] == ids_digest(train.order_id)
            training_state(scorer.pipeline, train, CORE_FEATURES)
            assert len(scorer.score(train.iloc[:64][['order_id']+CORE_FEATURES])) == 64
    sources = list((ROOT/'src').rglob('*.py'))
    write_json({'checks': {'eight_bundles_verified': True, 'training_only_preprocessing': True, 'OOF_policy_verified': True},
                'cycle_predictive_fits': 263,
                'source_sha256': {str(p.relative_to(ROOT)): sha256_file(p) for p in sources},
                'preterminal_artifact_sha256': {str(p.relative_to(folder)): sha256_file(p) for p in folder.rglob('*') if p.is_file()},
                'verification_fits': 0}, folder/'verification.json')


def verify_terminal(folder, core):
    dev, _, _ = load_development(ROOT)
    reviews = pd.read_csv(ROOT/'data/preprocessed/olist_order_reviews_dataset.csv', dtype={'order_id': 'string'})
    _, frames, eligibility = terminal_cohorts(dev, reviews, '2018-05-25')
    table = pd.read_csv(folder/'terminal_metrics.csv')
    for task in TARGETS:
        for role in ['selected', 'dummy', 'linear', 'tree']:
            pred = pd.read_csv(folder/f'{task}_{role}_terminal_predictions.csv', dtype={'order_id': 'string'})
            assert pred.order_id.tolist() == frames[task].order_id.tolist()
            np.testing.assert_array_equal(pred.target, frames[task][TARGETS[task]])
            p = pred.lead_days_prediction if task == 'regression' else pred.probability_1
            threshold = .5 if task == 'regression' else json.loads((core/task/role/'decision_policy.json').read_text())['threshold']
            values = metrics(task, pred.target, p, threshold)
            row = table[(table.task == task) & (table.role == role) & ~table.operating_policy.str.contains('diagnostic_not_selected')].iloc[0]
            keys = ['mae','rmse','r2'] if task == 'regression' else ['average_precision','roc_auc','brier','tp','fp','tn','fn']
            for key in keys:
                assert np.isclose(row[key], values[key], rtol=1e-10, atol=1e-10), (task, role, key)
    saved = pd.read_csv(folder/'terminal_eligibility.csv', dtype={'order_id':'string'})
    assert saved[['task','order_id','included']].astype(str).equals(eligibility[['task','order_id','included']].astype(str))
    write_json({'status':'passed','all_eight_models_checked':True,'exact_eligibility':True,'new_fits':0}, folder/'portable_verification.json')
