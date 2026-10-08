"""Descriptive baseline failure diagnostics on saved validation records only."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from .inputs import load_trial
from src.common.loaders import sha256_file
from src.models.io import write_json
from src.models.refinement_temporal import chronological_data
from .runner import ROOT


def inspect(folder, output=None):
    assert json.loads((folder / 'verification/verification.json').read_text())['status'] == 'passed'
    output = output or folder / 'baseline_diagnostics'
    if output.exists():
        raise FileExistsError('Existing diagnostic must be preserved')
    rows, coefficients, sources, month_support = [], [], {}, []
    freeze = json.loads((folder / 'study_freeze.json').read_text())
    folds = chronological_data(ROOT, freeze['fixed_model_config'])['folds']
    for identity in ['r13_ols', 'r19_ols']:
        for fold in range(5):
            job = folder / 'jobs' / f'{identity}-regression-fold{fold}'
            pipe = load_trial(job / 'pipeline.joblib')
            training = folds['regression', fold][0]
            for (year, month), group in training.groupby([training.prediction_timestamp.dt.year, training.prediction_timestamp.dt.month]):
                month_support.append({'id': identity, 'fold': fold, 'training_year': int(year), 'training_month': int(month),
                                      'n': len(group), 'mean_observed_lead_days': group.lead_days.mean(),
                                      'median_observed_lead_days': group.lead_days.median()})
            p = pd.read_csv(job / 'validation_predictions.csv')
            sources[str(job / 'validation_predictions.csv')] = sha256_file(job / 'validation_predictions.csv')
            categorical_cols = pipe.named_steps['preprocess'].transformers_[1][2]
            encoder = pipe.named_steps['preprocess'].named_transformers_['categorical']
            months = encoder.categories_[categorical_cols.index('purchase_month')]
            seen = pd.to_datetime(p.prediction_timestamp).dt.month.astype(str).isin(months)
            errors = p.target-p.prediction
            for label, mask in [('all', np.ones(len(p), dtype=bool)), ('month_seen_in_training', seen), ('month_unseen_in_training', ~seen)]:
                if not np.any(mask):
                    continue
                rows.append({'id': identity, 'fold': fold, 'group': label, 'n': int(np.sum(mask)),
                             'mae': np.abs(errors[mask]).mean(), 'mean_actual': p.target[mask].mean(),
                             'mean_prediction': p.prediction[mask].mean(), 'mean_residual_actual_minus_predicted': errors[mask].mean(),
                             'prediction_min': p.prediction[mask].min(), 'prediction_max': p.prediction[mask].max(),
                             'negative_predictions': int(p.prediction[mask].lt(0).sum())})
            names = pipe[:-1].get_feature_names_out()
            coef = pipe.named_steps['model'].coef_
            for i in np.argsort(np.abs(coef))[-8:][::-1]:
                coefficients.append({'id': identity, 'fold': fold, 'transformed_feature': names[i], 'coefficient': coef[i],
                                     'units_note': 'Numeric coefficients use fold-standardized units; categorical coefficients use reference coding. Not causal importance.'})
    output.mkdir()
    pd.DataFrame(rows).to_csv(output / 'ols_month_coverage.csv', index=False)
    pd.DataFrame(coefficients).to_csv(output / 'ols_largest_coefficients.csv', index=False)
    pd.DataFrame(month_support).to_csv(output / 'training_calendar_support.csv', index=False)
    write_json({'status': 'descriptive_postfit_diagnostic', 'new_fits': 0, 'terminal_scoring_calls': 0,
                'diagnostic_not_used_to_add_or_remove_features': True, 'source_prediction_hashes': sources,
                'code_sha256': sha256_file(Path(__file__)),
                'limitations': ['Seen/unseen month cohorts differ; not a controlled cause of error.',
                                'Sparse sklearn LinearRegression solver termination/rank is not audited here; no convergence certificate.',
                                'Coefficient magnitudes do not establish importance under correlated or reference-coded predictors.']}, output / 'completion.json')
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    inspect(args.input.resolve(), args.output.resolve() if args.output else None)
