"""Selected-model development diagnostics and interpretation; never fits."""
import argparse
import json
from pathlib import Path
import warnings
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import roc_curve, precision_recall_curve, average_precision_score, mean_absolute_error
from sklearn.tree import plot_tree
from src.common.loaders import sha256_file
from .data import ROOT, TARGETS
from .io import write_json
from .refinement_selected import probabilities
from .refinement_temporal import chronological_data
from .finalize import subgroup_tables


def plots(folder, frames, scores, title):
    folder.mkdir(parents=True, exist_ok=True)
    y, p = frames['regression'].lead_days.to_numpy(), scores['regression']
    residual = y-p
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    axes[0].scatter(p, residual, s=3, alpha=.12); axes[0].axhline(0, color='black', ls='--')
    axes[0].set(xlabel='Predicted delivery days', ylabel='Actual minus predicted days')
    axes[1].hist(residual, bins=60); axes[1].set(xlabel='Residual days', ylabel='Orders')
    stats.probplot(residual, plot=axes[2]); axes[2].set(title='Normal Q-Q: diagnostic, not an assumption test')
    fig.suptitle(title + ': selected decision-tree regression'); fig.tight_layout()
    fig.savefig(folder / 'regression_diagnostics.png', dpi=130); plt.close(fig)
    y, p = frames['classification'].is_detractor.to_numpy(), scores['classification']
    fpr, tpr, _ = roc_curve(y, p); precision, recall, _ = precision_recall_curve(y, p)
    records = []
    bins = np.minimum((p*10).astype(int), 9)
    for b in range(10):
        mask = bins == b
        records.append({'bin': b, 'n': int(mask.sum()), 'mean_probability': p[mask].mean() if mask.any() else None,
                        'observed_fraction': y[mask].mean() if mask.any() else None})
    reliability = pd.DataFrame(records); reliability.to_csv(folder / 'classification_reliability.csv', index=False)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    axes[0].plot(fpr, tpr); axes[0].plot([0, 1], [0, 1], 'k--'); axes[0].set(xlabel='False-positive rate', ylabel='Recall', title='ROC')
    axes[1].plot(recall, precision); axes[1].axhline(y.mean(), color='grey', ls='--'); axes[1].set(xlabel='Recall', ylabel='Precision', title='PR; dashed reference is prevalence')
    axes[2].plot(reliability.mean_probability, reliability.observed_fraction, 'o-'); axes[2].plot([0, 1], [0, 1], 'k--')
    axes[2].set(xlabel='Mean predicted probability', ylabel='Observed fraction', title='Reliability; bin counts saved')
    fig.suptitle(title + ': selected regularised logistic classification'); fig.tight_layout()
    fig.savefig(folder / 'classification_diagnostics.png', dpi=130); plt.close(fig)


def development(run):
    output = run / 'development_diagnostics'
    if output.exists():
        raise FileExistsError('Preserve existing diagnostics')
    assert json.loads((run / 'verification.json').read_text())['status'] == 'passed'
    config = json.loads((run / 'configuration.json').read_text())
    data = chronological_data(ROOT, config)
    output.mkdir()
    frames, scores, subgroups, importance = {}, {}, [], []
    threshold = json.loads((run / 'frozen_decision_policy.json').read_text())['threshold']
    for task in TARGETS:
        frame = pd.read_csv(run / f'{task}_development_oof.csv', dtype={'order_id': 'string'})
        frame[TARGETS[task]] = frame.target
        frames[task], scores[task] = frame, frame.prediction.to_numpy()
        subgroups.extend(subgroup_tables(task, frame, scores[task], threshold))
        for fold in range(5):
            _, validation = data['folds'][task, fold]
            cols = config['predictors_by_task'][task]
            pipe = joblib.load(run / 'development' / task / f'fold{fold}' / 'pipeline.joblib')
            y = validation[TARGETS[task]]
            metric = mean_absolute_error if task == 'regression' else average_precision_score
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                baseline = metric(y, probabilities(task, pipe, validation[cols]))
                for index, col in enumerate(cols):
                    for repeat in range(3):
                        rng = np.random.default_rng(42 + 1000*fold + 10*index + repeat)
                        x = validation[cols].copy()
                        x[col] = rng.permutation(x[col].to_numpy())
                        disturbed = metric(y, probabilities(task, pipe, x))
                        importance.append({'task': task, 'fold': fold, 'feature': col, 'repeat': repeat,
                                           'performance_loss': disturbed-baseline if task == 'regression' else baseline-disturbed})
    plots(output, frames, scores, 'Preterminal out-of-fold development')
    pd.DataFrame(subgroups).to_csv(output / 'subgroups.csv', index=False)
    imp = pd.DataFrame(importance); imp.to_csv(output / 'permutation_importance.csv', index=False)
    imp.groupby(['task', 'feature']).performance_loss.agg(['mean', 'std']).reset_index().to_csv(output / 'permutation_summary.csv', index=False)
    for task in TARGETS:
        pipe = joblib.load(run / 'bundles' / task / 'selected' / 'pipeline.joblib')
        names = pipe[:-1].get_feature_names_out()
        if task == 'regression':
            pd.DataFrame({'transformed_feature': names, 'impurity_importance': pipe.named_steps['model'].feature_importances_}).to_csv(output / 'tree_importance.csv', index=False)
            fig, ax = plt.subplots(figsize=(16, 7))
            plot_tree(pipe.named_steps['model'], feature_names=names, max_depth=2, filled=True, rounded=True, fontsize=7, ax=ax)
            ax.set_title('Final selected tree: top two split levels only, not the complete depth-5 tree')
            fig.tight_layout(); fig.savefig(output / 'selected_tree_top.png', dpi=140); plt.close(fig)
        else:
            coef = pipe.named_steps['model'].coef_[0]
            pd.DataFrame({'transformed_feature': names, 'coefficient': coef, 'odds_ratio': np.exp(coef)}).to_csv(output / 'logistic_coefficients.csv', index=False)
    write_json({'status': 'complete', 'new_fits': 0, 'terminal_scoring_calls': 0, 'permutation_seed': 42,
                'repeats_per_feature_fold': 3, 'code_sha256': sha256_file(Path(__file__)),
                'limitations': ['Post-selection reused development evidence, not independent confirmation.',
                                'Permutation can disrupt correlated inputs; importance is predictive association, not causal.',
                                'OOF policy/calibration summaries are descriptive after selection; no calibration fit.']}, output / 'completion.json')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    development(parser.parse_args().run.resolve())
