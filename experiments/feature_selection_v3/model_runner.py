"""Frozen taught-family model comparison; preterminal rows only."""
import argparse
import json
from pathlib import Path
import time
import warnings
import joblib
import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from . import runner as screen
from .inputs import SubsetInputContract
from src.common.loaders import sha256_file
from src.features.contract import PREDICTOR_ALLOWLIST
from src.models.data import TARGETS
from src.models.io import ids_digest, write_json
from src.models.refinement_core import CORE_FEATURES
from src.models.evaluate import metrics

ROOT = screen.ROOT
PROTOCOL = Path(__file__).with_name('model_protocol.json')


def design():
    old, config = screen.read_design()
    protocol = screen.binding(json.loads(PROTOCOL.read_text()))
    blocks = {b['id']: b for b in old['blocks']}
    for b in protocol['blocks']:
        additions = protocol['feature_sets'][b['feature_set']]
        b['columns'] = [c for c in PREDICTOR_ALLOWLIST if any(c in blocks[k]['columns'] for k in additions)]
        b['availability_assumptions'] = {k: blocks[k]['availability_assumption'] for k in additions}
    assert len(protocol['blocks']) * 5 == protocol['new_model_fit_ceiling'] == 50
    assert len({b['id'] for b in protocol['blocks']}) == 10
    assert not protocol['terminal_evaluation_allowed']
    assert protocol['feature_selection_attempts_already_consumed'] == 100
    previous = ROOT / protocol['screen_evidence']
    assert json.loads((previous / 'verification/verification.json').read_text())['status'] == 'passed'
    assert json.loads((previous / 'run_completion.json').read_text())['total_feature_study_attempts'] == 100
    return protocol, config


def run(output):
    if output.exists():
        raise FileExistsError('Existing outputs must be preserved')
    protocol, config = design()
    output.mkdir(parents=True)
    attempts = 0
    screen.event(output, 'initialization', 'Freeze taught-family baselines and reuse catalogue before model comparison fits.', new_predictive_attempts=0)
    try:
        folds, refs, identity = screen.prepare(output, protocol, config)
        identity['reused_job_hashes'] = {}
        for reuse in protocol['reuse']:
            additions = protocol['feature_sets'][reuse['feature_set']]
            screen_blocks = {b['id']: b for b in screen.read_design()[0]['blocks']}
            cols = CORE_FEATURES + [c for c in PREDICTOR_ALLOWLIST if any(c in screen_blocks[k]['columns'] for k in additions)]
            source = ROOT / reuse['source']
            assert json.loads((source / 'verification/verification.json').read_text())['status'] == 'passed'
            for fold in range(5):
                train, val = folds[reuse['task'], fold]
                job = source / 'jobs' / f'{reuse["block"]}-{reuse["task"]}-fold{fold}'
                jc = json.loads((job / 'configuration.json').read_text())
                assert jc['columns'] == cols and jc['candidate'] == config['selected'][reuse['task']]
                assert jc['training_ids_sha256'] == ids_digest(train.order_id)
                pred = pd.read_csv(job / 'validation_predictions.csv', dtype={'order_id': 'string'})
                assert pred.order_id.tolist() == val.order_id.tolist()
                assert np.array_equal(pred.target, val[TARGETS[reuse['task']]])
                for path in job.iterdir():
                    if path.is_file():
                        identity['reused_job_hashes'][str(path.relative_to(ROOT))] = sha256_file(path)
            for path in [source / 'verification/verification.json', source / 'fold_metrics.csv']:
                identity['reused_job_hashes'][str(path.relative_to(ROOT))] = sha256_file(path)
        for path in [PROTOCOL, Path(__file__), Path(__file__).with_name('inputs.py')]:
            identity['source_hashes'][str(path.relative_to(ROOT))] = sha256_file(path)
        previous = ROOT / protocol['screen_evidence']
        identity['screen_evidence_hashes'] = {str(p.relative_to(ROOT)): sha256_file(p) for p in previous.rglob('*') if p.is_file()}
        write_json(identity, output / 'study_freeze.json')
        records, subgroups = [], []
        for block in protocol['blocks']:
            columns = CORE_FEATURES + block['columns']
            for task in block['tasks']:
                for fold in range(5):
                    assert attempts < 50
                    train, val = folds[task, fold]
                    job = output / 'jobs' / f'{block["id"]}-{task}-fold{fold}'
                    job.mkdir(parents=True)
                    candidate = block['candidate']
                    write_json({'block': block, 'task': task, 'fold': fold, 'columns': columns, 'candidate': candidate,
                                'training_n': len(train), 'validation_n': len(val), 'training_ids_sha256': ids_digest(train.order_id),
                                'validation_ids_sha256': ids_digest(val.order_id)}, job / 'configuration.json')
                    train[['order_id']].to_csv(job / 'training_ids.csv', index=False)
                    pd.DataFrame([{'role': role, 'column': c, 'n': len(f), 'missing_n': int(f[c].isna().sum())}
                                  for role, f in [('training', train), ('validation', val)] for c in columns]).to_csv(job / 'coverage.csv', index=False)
                    pipe = screen.make_pipeline(task, candidate, config['baseline_config'], columns)
                    pipe.set_params(inputs=SubsetInputContract(tuple(columns)))
                    attempts += 1
                    screen.event(output, 'fit_started', 'Fit fixed model-family baseline on shortlisted features.', job=str(job.relative_to(output)), attempt=attempts)
                    started = time.monotonic()
                    caught = []
                    try:
                        with warnings.catch_warnings(record=True) as caught:
                            warnings.simplefilter('always')
                            pipe.fit(train[columns], train[TARGETS[task]])
                            scores = {role: screen.score(task, pipe, f[columns]) for role, f in [('training_resubstitution', train), ('validation', val)]}
                        if any(issubclass(w.category, ConvergenceWarning) for w in caught):
                            raise RuntimeError('Convergence warning invalidates trial')
                        seconds = time.monotonic() - started
                        for role, f in [('training_resubstitution', train), ('validation', val)]:
                            m = metrics(task, f[TARGETS[task]], scores[role])
                            row = {'block': block['id'], 'task': task, 'fold': fold, 'partition': role, 'candidate': candidate['id'], 'fit_seconds': seconds, **m}
                            if role == 'validation':
                                metric = 'mae' if task == 'regression' else 'average_precision'
                                core = metrics(task, f[TARGETS[task]], refs[task, fold])[metric]
                                row.update(core_metric=core, paired_gain=core-m[metric] if task == 'regression' else m[metric]-core)
                            records.append(row)
                        predictions = val[['order_id', 'customer_unique_id', 'prediction_timestamp', 'n_items', 'customer_state']].copy()
                        predictions['target'] = val[TARGETS[task]].to_numpy()
                        predictions['prediction'] = scores['validation']
                        predictions['core_reference_prediction'] = refs[task, fold]
                        predictions.to_csv(job / 'validation_predictions.csv', index=False)
                        subgroups.extend(screen.subgroup_rows(task, fold, block['id'], val, scores['validation'], refs[task, fold], protocol))
                        names = pipe[:-1].get_feature_names_out().tolist()
                        write_json({'transformed_feature_names': names, 'encoded_dimension': len(names), 'raw_predictors': columns, 'fitted_only_on': 'fold_training'}, job / 'pipeline_state.json')
                        joblib.dump(pipe, job / 'pipeline.joblib', compress=3)
                        write_json({'status': 'valid_completed', 'attempt': attempts, 'fit_seconds': seconds, 'pipeline_sha256': sha256_file(job / 'pipeline.joblib'), 'adopted': False}, job / 'completion.json')
                    except Exception as error:
                        write_json({'status': 'failed_execution_not_valid_evidence', 'attempt': attempts, 'error': str(error)}, job / 'failure.json')
                        raise
                    finally:
                        write_json([{'category': w.category.__name__, 'message': str(w.message)} for w in caught], job / 'warnings.json')
                    pd.DataFrame(records).to_csv(output / 'fold_metrics.csv', index=False)
                    pd.DataFrame(subgroups).to_csv(output / 'subgroup_comparisons.csv', index=False)
                    # The screen summarizer expects unique block IDs; shared task
                    # IDs are collapsed only for iteration, not trial evidence.
                    unique = dict(protocol, blocks=list({b['id']: b for b in protocol['blocks']}.values()))
                    screen.summarize(records, subgroups, unique, output)
                    screen.event(output, 'fit_completed', 'Preserve comparison regardless of gain.', job=str(job.relative_to(output)), attempt=attempts)
                    print(f'{attempts}/50 {job.name}', flush=True)
        assert attempts == 50
        for key in ['source_hashes', 'protected_hashes', 'core_reference_hashes', 'screen_evidence_hashes', 'reused_job_hashes']:
            screen.assert_unchanged(ROOT, identity[key])
        write_json({'status': 'model_gate_complete_pending_verification_and_decisions', 'new_predictive_attempts': attempts,
                    'new_model_comparison_attempts': attempts, 'prior_feature_study_attempts': 100, 'terminal_scoring_calls': 0,
                    'old_holdout_scoring_calls': 0, 'adopted': False, 'protected_files_unchanged': True}, output / 'run_completion.json')
        screen.event(output, 'model_gate_completed', 'Model comparison budget exhausted; verify baselines and reuse before decisions.')
    except Exception as error:
        write_json({'status': 'failed_preserved', 'new_predictive_attempts': attempts, 'error': str(error)}, output / 'run_failure.json')
        screen.event(output, 'failure', 'Stop; preserve failed attempt and budget consumed.', attempts=attempts, error=str(error))
        raise


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    # Keep directory creation inside run while ensuring job parents exist.
    run(args.output.resolve())
