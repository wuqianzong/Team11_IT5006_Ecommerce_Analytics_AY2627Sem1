"""Terminal evaluation for Refinement Cycle 2 (v4) production run.
Applies frozen production models to out-of-sample terminal evaluation cohorts.
Computes comprehensive diagnostics, subgroup breakdowns (state, basket, month),
and Train-Validate-Test generalization comparisons.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import warnings

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import precision_recall_curve, roc_curve

from src.common.loaders import sha256_file
from .data import ROOT, TARGETS, load_development
from .io import write_json
from .refinement_selected_v4 import SelectedScorerV4
from .refinement_terminal import terminal_cohorts
from .finalize import report_metrics, per_class_report, subgroup_tables


def compute_subgroups(task: str, frame: pd.DataFrame, values: np.ndarray, threshold: float) -> list[dict]:
    """Compute detailed subgroup breakdowns across customer state, basket size, purchase month, and distance."""
    subgroups = list(subgroup_tables(task, frame, values, threshold))

    # Temporal month breakdown
    months = frame['prediction_timestamp'].dt.to_period('M').astype(str)
    for month in sorted(months.unique()):
        mask = months.eq(month).to_numpy()
        subgroups.append({
            'task': task,
            'dimension': 'purchase_month',
            'subgroup': str(month),
            'small_support_flag': int(mask.sum()) < 100,
            **report_metrics(task, frame.loc[mask, TARGETS[task]], values[mask], threshold)
        })

    # Distance band breakdown for regression
    if task == 'regression' and 'distance_km_max' in frame.columns:
        dist_bins = pd.cut(
            frame['distance_km_max'].fillna(-1),
            bins=[-np.inf, 0, 250, 500, 1000, np.inf],
            labels=['Missing', '0-250km', '250-500km', '500-1000km', '1000km+']
        )
        for band in ['Missing', '0-250km', '250-500km', '500-1000km', '1000km+']:
            mask = dist_bins.eq(band).to_numpy()
            if mask.sum() > 0:
                subgroups.append({
                    'task': task,
                    'dimension': 'distance_band',
                    'subgroup': band,
                    'small_support_flag': int(mask.sum()) < 100,
                    **report_metrics(task, frame.loc[mask, TARGETS[task]], values[mask], threshold)
                })

    return subgroups


def plot_regression_diagnostics(output_dir: Path, y_true: np.ndarray, y_pred: np.ndarray, frame: pd.DataFrame):
    """Plot 4-panel regression diagnostics: scatter, residuals, distribution, and top states."""
    residuals = y_true - y_pred
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))

    # 1. Observed vs Predicted
    axes[0, 0].scatter(y_true, y_pred, alpha=0.15, s=6, color='#1f77b4')
    max_val = max(np.percentile(y_true, 99.5), np.percentile(y_pred, 99.5))
    axes[0, 0].plot([0, max_val], [0, max_val], 'k--', lw=1.5, label='Ideal 1:1')
    axes[0, 0].set_xlim(0, max_val)
    axes[0, 0].set_ylim(0, max_val)
    axes[0, 0].set_title('Observed vs. Predicted Delivery Lead Days', fontsize=11, fontweight='bold')
    axes[0, 0].set_xlabel('Observed Lead Days')
    axes[0, 0].set_ylabel('Predicted Lead Days')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # 2. Residuals vs Predicted
    axes[0, 1].scatter(y_pred, residuals, alpha=0.15, s=6, color='#ff7f0e')
    axes[0, 1].axhline(0, color='k', linestyle='--', lw=1.5)
    axes[0, 1].set_xlim(0, max_val)
    axes[0, 1].set_ylim(-25, 25)
    axes[0, 1].set_title('Residuals vs. Predicted Lead Days', fontsize=11, fontweight='bold')
    axes[0, 1].set_xlabel('Predicted Lead Days')
    axes[0, 1].set_ylabel('Residual (Observed - Predicted) [days]')
    axes[0, 1].grid(True, alpha=0.3)

    # 3. Residual Error Distribution
    axes[1, 0].hist(residuals, bins=70, range=(-20, 20), color='#2ca02c', edgecolor='black', alpha=0.7)
    axes[1, 0].axvline(0, color='red', linestyle='--', lw=1.5, label='Zero Error')
    axes[1, 0].axvline(np.mean(residuals), color='black', linestyle=':', lw=1.5, label=f'Mean: {np.mean(residuals):.2f}d')
    axes[1, 0].set_title('Residual Error Distribution (days)', fontsize=11, fontweight='bold')
    axes[1, 0].set_xlabel('Residual (days)')
    axes[1, 0].set_ylabel('Order Count')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # 4. State Subgroup MAE (Top 8 States)
    top_states = frame['customer_state'].value_counts().head(8).index.tolist()
    state_maes = []
    for st in top_states:
        mask = frame['customer_state'].eq(st).to_numpy()
        state_maes.append(float(np.mean(np.abs(y_true[mask] - y_pred[mask]))))

    bars = axes[1, 1].bar(top_states, state_maes, color='#9467bd', edgecolor='black', alpha=0.8)
    axes[1, 1].axhline(float(np.mean(np.abs(residuals))), color='red', linestyle='--', lw=1.5, label=f'Global MAE ({np.mean(np.abs(residuals)):.2f}d)')
    axes[1, 1].set_title('Holdout MAE by Top Customer States', fontsize=11, fontweight='bold')
    axes[1, 1].set_xlabel('Customer State')
    axes[1, 1].set_ylabel('MAE (days)')
    axes[1, 1].legend()
    axes[1, 1].grid(axis='y', alpha=0.3)
    for bar in bars:
        h = bar.get_height()
        axes[1, 1].text(bar.get_x() + bar.get_width()/2., h + 0.08, f'{h:.2f}', ha='center', va='bottom', fontsize=9)

    plt.suptitle('Refinement Cycle 2: Delivery Duration Terminal Diagnostics (RF Champion)', fontsize=13, fontweight='bold', y=0.995)
    plt.tight_layout()
    fig.savefig(output_dir / 'regression_diagnostics.png', dpi=150)
    plt.close(fig)


def plot_classification_diagnostics(output_dir: Path, y_true: np.ndarray, y_prob: np.ndarray, threshold: float):
    """Plot 4-panel classification diagnostics: PR curve, ROC curve, Calibration curve, and Cost curve."""
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    prevalence = float(np.mean(y_true))

    # 1. Precision-Recall Curve
    precision, recall, _ = precision_recall_curve(y_true, y_prob)
    axes[0, 0].plot(recall, precision, color='#1f77b4', lw=2, label='Champion RF')
    axes[0, 0].axhline(prevalence, color='grey', linestyle='--', label=f'No-skill ({prevalence:.1%})')
    # Mark operating point
    y_pred_thresh = (y_prob >= threshold).astype(int)
    tp = np.sum((y_pred_thresh == 1) & (y_true == 1))
    fp = np.sum((y_pred_thresh == 1) & (y_true == 0))
    fn = np.sum((y_pred_thresh == 0) & (y_true == 1))
    p_star = tp / (tp + fp) if (tp + fp) > 0 else 0
    r_star = tp / (tp + fn) if (tp + fn) > 0 else 0
    axes[0, 0].scatter([r_star], [p_star], color='red', s=80, zorder=5, label=f'Policy τ*={threshold:.2f} (P={p_star:.2f}, R={r_star:.2f})')
    axes[0, 0].set_title('Precision-Recall Curve', fontsize=11, fontweight='bold')
    axes[0, 0].set_xlabel('Recall (Detractor Catch Rate)')
    axes[0, 0].set_ylabel('Precision')
    axes[0, 0].set_xlim(0, 1.02)
    axes[0, 0].set_ylim(0, 1.02)
    axes[0, 0].legend(loc='upper right')
    axes[0, 0].grid(True, alpha=0.3)

    # 2. ROC Curve
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    axes[0, 1].plot(fpr, tpr, color='#ff7f0e', lw=2, label='Champion RF')
    axes[0, 1].plot([0, 1], [0, 1], 'k--', lw=1.5, label='Random Guess')
    axes[0, 1].set_title('Receiver Operating Characteristic (ROC)', fontsize=11, fontweight='bold')
    axes[0, 1].set_xlabel('False Positive Rate')
    axes[0, 1].set_ylabel('True Positive Rate (Recall)')
    axes[0, 1].legend(loc='lower right')
    axes[0, 1].grid(True, alpha=0.3)

    # 3. Calibration Curve / Reliability Diagram
    prob_true, prob_pred = calibration_curve(y_true, y_prob, n_bins=8, strategy='quantile')
    axes[1, 0].plot(prob_pred, prob_true, 's-', color='#2ca02c', lw=2, label='Champion RF')
    axes[1, 0].plot([0, 1], [0, 1], 'k--', label='Perfect Calibration')
    axes[1, 0].set_title('Reliability Diagram (Calibration)', fontsize=11, fontweight='bold')
    axes[1, 0].set_xlabel('Mean Predicted Probability')
    axes[1, 0].set_ylabel('Empirical Detractor Fraction')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # 4. Illustrative Cost Curve vs Threshold (1:5 Error Cost Ratio)
    thresholds = np.linspace(0.05, 0.60, 50)
    costs = []
    for t in thresholds:
        yp = (y_prob >= t).astype(int)
        c_fn = 5 * np.sum((yp == 0) & (y_true == 1))
        c_fp = 1 * np.sum((yp == 1) & (y_true == 0))
        costs.append(c_fn + c_fp)

    axes[1, 1].plot(thresholds, costs, color='#d62728', lw=2, label='Loss = 5·FN + 1·FP')
    axes[1, 1].axvline(threshold, color='black', linestyle='--', label=f'Optimal τ*={threshold:.2f}')
    axes[1, 1].scatter([threshold], [min(costs)], color='black', s=80, zorder=5)
    axes[1, 1].set_title('Asymmetric Cost Curve (1:5 FN:FP Ratio)', fontsize=11, fontweight='bold')
    axes[1, 1].set_xlabel('Decision Threshold (τ)')
    axes[1, 1].set_ylabel('Total Evaluated Business Loss')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    plt.suptitle('Refinement Cycle 2: Review Detractor Terminal Diagnostics (RF Champion)', fontsize=13, fontweight='bold', y=0.995)
    plt.tight_layout()
    fig.savefig(output_dir / 'classification_diagnostics.png', dpi=150)
    plt.close(fig)


def build_train_val_test_comparison(run_dir: Path, output_dir: Path):
    """Compile side-by-side Train vs. Validate vs. Test generalization comparison table."""
    cv_df = pd.read_csv(run_dir / 'development_fold_metrics.csv')
    test_df = pd.read_csv(output_dir / 'metrics.csv')

    rows = []

    # Regression comparison
    reg_train = cv_df[(cv_df['task'] == 'regression') & (cv_df['partition'] == 'training_resubstitution')]
    reg_val = cv_df[(cv_df['task'] == 'regression') & (cv_df['partition'] == 'validation')]
    reg_test = test_df[(test_df['task'] == 'regression') & (test_df['role'] == 'selected')].iloc[0]

    for metric in ['mae', 'rmse', 'r2']:
        t_mean, t_sd = reg_train[metric].mean(), reg_train[metric].std()
        v_mean, v_sd = reg_val[metric].mean(), reg_val[metric].std()
        test_val = reg_test[metric]
        rows.append({
            'task': 'regression',
            'metric': metric,
            'train_mean': round(t_mean, 4),
            'train_sd': round(t_sd, 4),
            'val_mean': round(v_mean, 4),
            'val_sd': round(v_sd, 4),
            'test_holdout': round(test_val, 4)
        })

    # Classification comparison
    clf_train = cv_df[(cv_df['task'] == 'classification') & (cv_df['partition'] == 'training_resubstitution')]
    clf_val = cv_df[(cv_df['task'] == 'classification') & (cv_df['partition'] == 'validation')]
    clf_test = test_df[(test_df['task'] == 'classification') & (test_df['role'] == 'selected')].iloc[0]

    for metric in ['average_precision', 'roc_auc', 'brier', 'f1_1']:
        t_mean, t_sd = clf_train[metric].mean(), clf_train[metric].std()
        v_mean, v_sd = clf_val[metric].mean(), clf_val[metric].std()
        test_val = clf_test[metric]
        rows.append({
            'task': 'classification',
            'metric': metric,
            'train_mean': round(t_mean, 4),
            'train_sd': round(t_sd, 4),
            'val_mean': round(v_mean, 4),
            'val_sd': round(v_sd, 4),
            'test_holdout': round(test_val, 4)
        })

    comp_df = pd.DataFrame(rows)
    comp_df.to_csv(output_dir / 'train_val_test_comparison.csv', index=False)
    print("\n=== Train vs. Validate vs. Test Generalization Comparison ===")
    print(comp_df.to_string(index=False))


def evaluate(run_dir: Path, acknowledge: bool = False, overwrite: bool = False):
    if not acknowledge:
        raise ValueError('Explicit --acknowledge-previously-inspected-terminal required')

    run = Path(run_dir).resolve()
    output = run / 'terminal'
    if output.exists():
        if overwrite:
            print(f'Overwriting existing terminal evaluation in {output}...')
        else:
            raise FileExistsError(f'{output} already exists. Use --overwrite to re-evaluate.')
    else:
        output.mkdir(parents=True)

    config = json.loads((run / 'configuration.json').read_text())

    bundle_paths = [p for p in (run / 'bundles').rglob('*') if p.is_file()]
    write_json({
        'version': config['version'],
        'cycle': config['cycle'],
        'terminal_cutoff': config['terminal_cutoff'],
        'bundle_hashes': {str(p.relative_to(run)): sha256_file(p) for p in bundle_paths},
        'policy_sha256': sha256_file(run / 'frozen_decision_policy.json')
    }, output / 'evaluation_freeze.json')

    print(f'Evaluating terminal out-of-sample cohorts for {config["version"]}...')
    dev, _, _ = load_development(ROOT)
    reviews = pd.read_csv(
        ROOT / 'data/preprocessed/olist_order_reviews_dataset.csv',
        usecols=['order_id', 'review_score', 'review_answer_timestamp'],
        dtype={'order_id': 'string'}
    )
    _, frames, eligibility = terminal_cohorts(dev, reviews, config['terminal_cutoff'])
    eligibility.to_csv(output / 'eligibility.csv', index=False)

    records = []
    subgroups = []

    for task in TARGETS:
        frame = frames[task]
        cols = config['predictors_by_task'][task]
        print(f'\nScoring terminal cohort for {task} (N={len(frame)})...')

        for bundle in sorted((run / 'bundles' / task).iterdir()):
            if not bundle.is_dir():
                continue
            role = bundle.name
            scorer = SelectedScorerV4(bundle)

            scored = scorer.score(frame[['order_id'] + cols])
            values = scored['lead_days_prediction'].to_numpy() if task == 'regression' else scored['probability_1'].to_numpy()
            threshold = scorer.policy['threshold'] if task == 'classification' else 0.5

            scored['target'] = frame[TARGETS[task]].to_numpy()
            scored['customer_unique_id'] = frame['customer_unique_id'].to_numpy()
            scored.to_csv(output / f'{task}_{role}_predictions.csv', index=False)

            m = report_metrics(task, frame[TARGETS[task]], values, threshold)
            records.append({'task': task, 'role': role, **m})

            if role == 'selected':
                print(f'  [Champion] {role:10s} -> Computing subgroups and diagnostic figures...')
                subgroups.extend(compute_subgroups(task, frame, values, threshold))

                if task == 'regression':
                    plot_regression_diagnostics(output, frame[TARGETS[task]].to_numpy(), values, frame)
                else:
                    plot_classification_diagnostics(output, frame[TARGETS[task]].to_numpy(), values, threshold)
                    pd.DataFrame(per_class_report(frame.is_detractor, values, threshold)).to_csv(output / 'classification_per_class.csv', index=False)
                    write_json({
                        'frozen_policy': m,
                        'fixed_05_diagnostic': report_metrics(task, frame.is_detractor, values, 0.5),
                        'no_alert_cost': int(5 * frame.is_detractor.sum()),
                        'terminal_does_not_change_policy': True
                    }, output / 'classification_policy_comparison.json')

            if task == 'regression':
                print(f'  {role:10s} -> MAE: {m["mae"]:.4f} days | RMSE: {m["rmse"]:.4f} | R2: {m.get("r2", float("nan")):.4f}')
            else:
                print(f'  {role:10s} -> AP: {m["average_precision"]:.4f} | ROC-AUC: {m["roc_auc"]:.4f} | F1: {m.get("f1_1", 0.0):.4f} | Cost: {m.get("illustrative_cost_5_to_1", 0):.0f}')

    # Save metrics
    metrics_df = pd.DataFrame(records)
    metrics_df.to_csv(output / 'metrics.csv', index=False)

    # Save subgroups
    subgroup_df = pd.DataFrame(subgroups)
    subgroup_df['ranking_support_sufficient'] = (
        subgroup_df['n'].ge(100) & subgroup_df.get('positives', pd.Series(100, index=subgroup_df.index)).ge(20)
    )
    subgroup_df.to_csv(output / 'subgroups.csv', index=False)
    print(f'Saved subgroup analysis ({len(subgroup_df)} entries) to {output / "subgroups.csv"}')

    # Build Train vs Validate vs Test comparison
    build_train_val_test_comparison(run, output)

    write_json({'status': 'completed', 'cohort_n': {task: len(f) for task, f in frames.items()}}, output / 'completion.json')
    print(f'\nTerminal evaluation complete. All artifacts saved to {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True, help='Path to run directory')
    parser.add_argument('--acknowledge-previously-inspected-terminal', action='store_true', required=True)
    parser.add_argument('--overwrite', action='store_true', help='Allow overwriting existing terminal evaluation')
    args = parser.parse_args()
    evaluate(args.run, args.acknowledge_previously_inspected_terminal, args.overwrite)
