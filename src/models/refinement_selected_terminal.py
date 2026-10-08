"""Previously inspected terminal diagnostic: freeze first, never fit or select."""
import argparse
import json
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
from src.common.loaders import sha256_file
from .data import ROOT, TARGETS, load_development
from .io import write_json
from .refinement_selected import SelectedScorer
from .refinement_terminal import terminal_cohorts, paired_intervals
from .refinement_diagnostics import plots
from .finalize import report_metrics, per_class_report, subgroup_tables


def evaluate(run, acknowledge=False):
    if not acknowledge:
        raise ValueError('Explicit --acknowledge-previously-inspected-terminal required')
    output = run / 'terminal'
    if output.exists():
        raise FileExistsError('This run already reserved terminal access; preserve it')
    verification = json.loads((run / 'verification.json').read_text())
    assert verification['status'] == 'passed'
    for rel, digest in verification['artifact_hashes'].items():
        if sha256_file(run / rel) != digest:
            raise ValueError('Verified artifact modified: ' + rel)
    freeze = json.loads((run / 'build_freeze.json').read_text())
    for rel, digest in freeze['source_hashes'].items():
        assert sha256_file(ROOT / rel) == digest, rel
    config = json.loads((run / 'configuration.json').read_text())
    output.mkdir()
    bundle_paths = [p for p in (run / 'bundles').rglob('*') if p.is_file()]
    write_json({'recipe': 'Same chronology/eligibility as core-v2; original20% holdout excluded; all recorded consistent terminal labels; no score-based exclusions.',
                'prior_exposure_acknowledged': True, 'models_features_thresholds_already_frozen': True,
                'terminal_cutoff': config['terminal_cutoff'], 'no_fits_or_selection': True,
                'bundle_hashes': {str(p.relative_to(run)): sha256_file(p) for p in bundle_paths},
                'policy_sha256': sha256_file(run / 'frozen_decision_policy.json'),
                'evaluation_code_sha256': sha256_file(Path(__file__)),
                'plot_code_sha256': sha256_file(Path(__file__).with_name('refinement_diagnostics.py'))}, output / 'evaluation_freeze.json')
    try:
        dev, _, _ = load_development(ROOT)
        reviews = pd.read_csv(ROOT / 'data/preprocessed/olist_order_reviews_dataset.csv', usecols=['order_id', 'review_score', 'review_answer_timestamp'], dtype={'order_id': 'string'})
        _, frames, eligibility = terminal_cohorts(dev, reviews, config['terminal_cutoff'])
        eligibility.to_csv(output / 'eligibility.csv', index=False)
        records, subgroups, selected_scores, selected_frames, intervals, warnings_log = [], [], {}, {}, [], []
        for task in TARGETS:
            frame = frames[task]
            cols = config['predictors_by_task'][task]
            earlier = pd.read_csv(run / f'{task}_training_ids.csv', dtype={'customer_unique_id': 'string'})
            if set(earlier.customer_unique_id) & set(frame.customer_unique_id):
                raise ValueError('Terminal customer in final training')
            predictions = {}
            for bundle in sorted((run / 'bundles' / task).iterdir()):
                role = bundle.name
                scorer = SelectedScorer(bundle)
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter('always')
                    scored = scorer.score(frame[['order_id'] + cols])
                warnings_log += [{'task': task, 'role': role, 'category': w.category.__name__, 'message': str(w.message)} for w in caught]
                values = scored.lead_days_prediction.to_numpy() if task == 'regression' else scored.probability_1.to_numpy()
                predictions[role] = values
                threshold = scorer.policy['threshold'] if task == 'classification' else .5
                scored['target'] = frame[TARGETS[task]].to_numpy()
                scored['customer_unique_id'] = frame.customer_unique_id.to_numpy()
                scored.to_csv(output / f'{task}_{role}_predictions.csv', index=False)
                m = report_metrics(task, frame[TARGETS[task]], values, threshold)
                records.append({'task': task, 'role': role, **m})
                if role == 'selected':
                    selected_scores[task], selected_frames[task] = values, frame
                    subgroups.extend(subgroup_tables(task, frame, values, threshold))
                    months = frame.prediction_timestamp.dt.to_period('M').astype(str)
                    for month in sorted(months.unique()):
                        mask = months.eq(month)
                        subgroups.append({'task': task, 'dimension': 'purchase_month', 'subgroup': month,
                                          'small_support_flag': int(mask.sum()) < 100,
                                          **report_metrics(task, frame.loc[mask, TARGETS[task]], values[mask], threshold)})
                    if task == 'classification':
                        pd.DataFrame(per_class_report(frame.is_detractor, values, threshold)).to_csv(output / 'classification_per_class.csv', index=False)
                        write_json({'frozen_policy': m, 'fixed_05_diagnostic': report_metrics(task, frame.is_detractor, values, .5),
                                    'no_alert_cost': int(5*frame.is_detractor.sum()), 'terminal_does_not_change_policy': True}, output / 'classification_policy_comparison.json')
            for role in predictions:
                if role != 'selected':
                    intervals.append({'reference': role, **paired_intervals(task, frame[TARGETS[task]], predictions['selected'], predictions[role], frame.customer_unique_id, replicates=1000, seed=42)})
        pd.DataFrame(records).to_csv(output / 'metrics.csv', index=False)
        group_table = pd.DataFrame(subgroups)
        group_table['ranking_support_sufficient'] = (group_table.n.ge(100) & group_table.positives.ge(20) & group_table.negatives.ge(20))
        group_table.to_csv(output / 'subgroups.csv', index=False)
        pd.DataFrame(intervals).to_csv(output / 'paired_intervals.csv', index=False)
        write_json(warnings_log, output / 'scoring_warnings.json')
        plots(output, selected_frames, selected_scores, 'Previously inspected chronological terminal diagnostic')
        for p in bundle_paths:
            assert sha256_file(p) == json.loads((output / 'evaluation_freeze.json').read_text())['bundle_hashes'][str(p.relative_to(run))]
        write_json({'status': 'complete_pending_independent_verification', 'new_fits': 0, 'terminal_scoring_passes': 1,
                    'previously_inspected_diagnostic_only': True, 'selection_changed': False,
                    'cohort_n': {task: len(f) for task, f in frames.items()}}, output / 'completion.json')
    except Exception as error:
        write_json({'error_type': type(error).__name__, 'error': str(error), 'no_automatic_retry': True}, output / 'failure.json')
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--acknowledge-previously-inspected-terminal', action='store_true')
    args = parser.parse_args()
    evaluate(args.run.resolve(), args.acknowledge_previously_inspected_terminal)
