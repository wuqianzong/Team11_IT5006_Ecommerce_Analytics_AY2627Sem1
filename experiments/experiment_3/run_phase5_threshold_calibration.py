#!/usr/bin/env python3
"""Experiment 3 — Phase 5: Classification Probability Calibration & Decision Cost-Curve Optimization.

Directly implements methodology taught in IT5006 Tutorial 7 (T07_Main.ipynb Cells 35-36)
and Tutorial 8 (T08_Classficiation_Models.ipynb):
1. Probability Calibration:
   - Evaluates calibration curves and Brier score loss for Logistic Regression and Random Forest.
   - Tests Platt Scaling (CalibratedClassifierCV, method='sigmoid').
2. Asymmetric Business Cost-Curve Threshold Optimization:
   - False Positive (FP): Proactive support outreach sent to a satisfied customer (Cost = $1).
   - False Negative (FN): Missed detractor customer leads to churn and public 1-star review.
   - Tests 3 operational cost ratios:
     * Scenario A: Balanced/Cost-neutral (C_FP = 1, C_FN = 1)
     * Scenario B: Moderate Proactive Support (C_FP = 1, C_FN = 5) [Standard baseline]
     * Scenario C: High Customer Retention (C_FP = 1, C_FN = 10)
   - Evaluates thresholds tau in [0.05, 0.90] with step 0.02.
   - Computes 4-panel diagnostic plot:
     * Panel 1: Precision, Recall, and F1 vs. Threshold
     * Panel 2: Total Business Cost Curves vs. Threshold across Scenarios (Finding tau*)
     * Panel 3: Confusion Matrix Stackplot (TP, FP, FN, TN)
     * Panel 4: Positive Intervention / Alert Rate (%) vs. Threshold

Outputs saved strictly to:
artifacts/metrics/experiment-3/threshold_calibration/
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, FunctionTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import calibration_curve, CalibratedClassifierCV
from sklearn.metrics import confusion_matrix, brier_score_loss, average_precision_score, roc_auc_score
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.base import clone

# Add repo root to import path
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.models.data import load_development, task_rows, fold_indices
from src.features.contract import CATEGORICAL_COLUMNS
from src.models.refinement_core import CORE_FEATURES

OUTPUT_DIR = REPO_ROOT / "artifacts" / "metrics" / "experiment-3" / "threshold_calibration"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 14 Features for Classification (Phase 3 winning set)
CLF_14_FEATURES = CORE_FEATURES + ["n_sellers", "primary_seller_state", "interstate_share"]
SKEWED_NUMERIC_COLS = ["total_price", "total_freight", "distance_km_max"]


def build_preprocessor(feature_names):
    """Build ColumnTransformer with log1p pre-scaling on skewed continuous predictors."""
    num_cols = [c for c in feature_names if c not in CATEGORICAL_COLUMNS]
    cat_cols = [c for c in feature_names if c in CATEGORICAL_COLUMNS]

    skewed_in_subset = [c for c in SKEWED_NUMERIC_COLS if c in num_cols]
    normal_num_in_subset = [c for c in num_cols if c not in skewed_in_subset]

    transformers = []
    if skewed_in_subset:
        skewed_pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("log1p", FunctionTransformer(np.log1p, validate=False)),
            ("scaler", StandardScaler())
        ])
        transformers.append(("skewed_num", skewed_pipe, skewed_in_subset))

    if normal_num_in_subset:
        reg_num_pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ])
        transformers.append(("reg_num", reg_num_pipe, normal_num_in_subset))

    if cat_cols:
        cat_pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
            ("ohe", OneHotEncoder(drop="first", handle_unknown="ignore", sparse_output=False))
        ])
        transformers.append(("cat", cat_pipe, cat_cols))

    return ColumnTransformer(transformers=transformers, remainder="drop")


def run_probability_calibration_audit(df_clf, seed=42):
    """Audit probability calibration and Brier score before and after Platt scaling."""
    print("\n" + "=" * 80)
    print("PHASE 5A: PROBABILITY CALIBRATION & BRIER SCORE AUDIT")
    print("=" * 80)

    preprocessor = build_preprocessor(CLF_14_FEATURES)

    # Models from Phase 4B optimal configuration
    base_models = {
        "Logistic Regression (C=0.01)": Pipeline([
            ("preprocess", preprocessor),
            ("model", LogisticRegression(C=0.01, solver="lbfgs", max_iter=2000, random_state=seed))
        ]),
        "Random Forest (Tuned)": Pipeline([
            ("preprocess", preprocessor),
            ("model", RandomForestClassifier(n_estimators=50, max_depth=14, min_samples_leaf=20, random_state=seed, n_jobs=-1))
        ])
    }

    # Collect out-of-fold probability predictions across 5 temporal folds
    oof_predictions = {name: {"y_true": [], "y_prob": [], "y_prob_cal": []} for name in base_models}

    for fold, train_idx, val_idx in fold_indices(df_clf):
        train_df = df_clf.iloc[train_idx]
        val_df = df_clf.iloc[val_idx]

        for name, pipe in base_models.items():
            # 1. Fit uncalibrated pipeline
            pipe_uncal = clone(pipe)
            pipe_uncal.fit(train_df[CLF_14_FEATURES], train_df["is_detractor"])
            probs_uncal = pipe_uncal.predict_proba(val_df[CLF_14_FEATURES])[:, 1]

            # 2. Fit Platt calibrated pipeline (method='sigmoid')
            # CalibratedClassifierCV wraps the unfitted pipeline using cv=3 inside the training fold
            pipe_cal = CalibratedClassifierCV(clone(pipe), method="sigmoid", cv=3)
            pipe_cal.fit(train_df[CLF_14_FEATURES], train_df["is_detractor"])
            probs_cal = pipe_cal.predict_proba(val_df[CLF_14_FEATURES])[:, 1]

            oof_predictions[name]["y_true"].extend(val_df["is_detractor"].values)
            oof_predictions[name]["y_prob"].extend(probs_uncal)
            oof_predictions[name]["y_prob_cal"].extend(probs_cal)

    cal_results = []
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=150)

    for idx, (name, data) in enumerate(oof_predictions.items()):
        y_true = np.array(data["y_true"])
        y_prob = np.array(data["y_prob"])
        y_prob_cal = np.array(data["y_prob_cal"])

        brier_raw = brier_score_loss(y_true, y_prob)
        brier_cal = brier_score_loss(y_true, y_prob_cal)
        ap_raw = average_precision_score(y_true, y_prob)
        ap_cal = average_precision_score(y_true, y_prob_cal)

        cal_results.append({
            "model": name,
            "calibration_status": "Uncalibrated",
            "brier_score": brier_raw,
            "average_precision": ap_raw
        })
        cal_results.append({
            "model": name,
            "calibration_status": "Platt Calibrated (Sigmoid)",
            "brier_score": brier_cal,
            "average_precision": ap_cal
        })

        print(f"\n[{name}]")
        print(f"  Uncalibrated      -> Brier: {brier_raw:.5f} | AP: {ap_raw:.4f}")
        print(f"  Platt Calibrated  -> Brier: {brier_cal:.5f} | AP: {ap_cal:.4f}")

        # Calibration Curves
        prob_true_raw, prob_pred_raw = calibration_curve(y_true, y_prob, n_bins=10)
        prob_true_cal, prob_pred_cal = calibration_curve(y_true, y_prob_cal, n_bins=10)

        ax = ax1 if idx == 0 else ax2
        ax.plot([0, 1], [0, 1], "k--", label="Perfect Calibration", lw=1.5)
        ax.plot(prob_pred_raw, prob_true_raw, "s-", color="#e74c3c", lw=2, label=f"Uncalibrated (Brier={brier_raw:.4f})")
        ax.plot(prob_pred_cal, prob_true_cal, "o-", color="#27ae60", lw=2, label=f"Platt Calibrated (Brier={brier_cal:.4f})")
        ax.set_xlabel("Mean Predicted Probability", fontweight="bold", fontsize=11)
        ax.set_ylabel("Fraction of Positives (Detractors)", fontweight="bold", fontsize=11)
        ax.set_title(f"Reliability Curve: {name}", fontweight="bold", fontsize=12)
        ax.legend(frameon=True, loc="upper left")
        ax.set_xlim(-0.02, 1.02)
        ax.set_ylim(-0.02, 1.02)

    plt.tight_layout()
    cal_plot_path = OUTPUT_DIR / "calibration_curves.png"
    plt.savefig(cal_plot_path, dpi=150)
    plt.close()
    print(f"Saved Calibration Curves plot to: {cal_plot_path}")

    df_cal = pd.DataFrame(cal_results)
    df_cal.to_csv(OUTPUT_DIR / "calibration_metrics.csv", index=False)

    return oof_predictions


def run_threshold_cost_optimization(oof_predictions):
    """Phase 5B: Asymmetric Cost-Curve Threshold Optimization across 3 Business Scenarios."""
    print("\n" + "=" * 80)
    print("PHASE 5B: ASYMMETRIC COST-CURVE THRESHOLD OPTIMIZATION")
    print("=" * 80)

    # Use Random Forest (Tuned) as the primary champion model
    rf_data = oof_predictions["Random Forest (Tuned)"]
    y_true = np.array(rf_data["y_true"])
    y_prob = np.array(rf_data["y_prob"])
    n_samples = len(y_true)

    # Cost scenarios: (Scenario Name, Cost FP, Cost FN)
    cost_scenarios = [
        ("Scenario A: Balanced / Cost-Neutral (1:1)", 1.0, 1.0),
        ("Scenario B: Moderate Proactive Support (1:5)", 1.0, 5.0),
        ("Scenario C: Aggressive Customer Retention (1:10)", 1.0, 10.0)
    ]

    thresholds = np.arange(0.05, 0.91, 0.02)
    curve_data = []

    for tau in thresholds:
        y_pred = (y_prob >= tau).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

        prec = precision_score(y_true, y_pred, zero_division=0)
        rec = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        alert_rate = (tp + fp) / n_samples

        row = {
            "threshold": round(tau, 3),
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": prec, "recall": rec, "f1": f1,
            "alert_rate": alert_rate
        }

        # Calculate cost under each scenario
        for sc_name, c_fp, c_fn in cost_scenarios:
            total_cost = (fp * c_fp) + (fn * c_fn)
            norm_cost = total_cost / n_samples
            row[f"cost_{c_fp}_{c_fn}"] = total_cost
            row[f"norm_cost_{c_fp}_{c_fn}"] = norm_cost

        curve_data.append(row)

    df_curves = pd.DataFrame(curve_data)
    df_curves.to_csv(OUTPUT_DIR / "cost_curve_optimization.csv", index=False)
    print(f"Saved threshold cost curves to: {OUTPUT_DIR / 'cost_curve_optimization.csv'}")

    # Identify optimal thresholds for each scenario
    optimal_summary = []
    for sc_name, c_fp, c_fn in cost_scenarios:
        cost_col = f"cost_{c_fp}_{c_fn}"
        best_idx = df_curves[cost_col].idxmin()
        best_row = df_curves.loc[best_idx]

        # Contrast with default threshold 0.50
        idx_050 = (df_curves["threshold"] - 0.50).abs().idxmin()
        row_050 = df_curves.loc[idx_050]

        cost_saving = row_050[cost_col] - best_row[cost_col]
        pct_saving = (cost_saving / row_050[cost_col]) * 100.0

        optimal_summary.append({
            "scenario": sc_name,
            "cost_ratio_fp_fn": f"{int(c_fp)}:{int(c_fn)}",
            "optimal_threshold": best_row["threshold"],
            "optimal_total_cost": best_row[cost_col],
            "optimal_precision": best_row["precision"],
            "optimal_recall": best_row["recall"],
            "optimal_f1": best_row["f1"],
            "optimal_alert_rate": best_row["alert_rate"],
            "default_050_cost": row_050[cost_col],
            "cost_reduction_amount": cost_saving,
            "cost_reduction_pct": pct_saving
        })

        print(f"\n{sc_name}:")
        print(f"  * Optimal Threshold (tau*): {best_row['threshold']:.2f}")
        print(f"  * Precision: {best_row['precision']:.3f} | Recall: {best_row['recall']:.3f} | F1: {best_row['f1']:.3f}")
        print(f"  * Alert Rate: {best_row['alert_rate']*100:.1f}%")
        print(f"  * Total Cost: {best_row[cost_col]:,.0f} vs Default 0.50: {row_050[cost_col]:,.0f} (Saved: {pct_saving:.1f}%)")

    df_opt = pd.DataFrame(optimal_summary)
    df_opt.to_csv(OUTPUT_DIR / "threshold_metrics_summary.csv", index=False)
    print(f"Saved optimal threshold summary to: {OUTPUT_DIR / 'threshold_metrics_summary.csv'}")

    # Generate 4-Panel Visualization Plot (Matching T07 Cell 36)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, axes = plt.subplots(2, 2, figsize=(15, 11), dpi=150)

    # Panel 1: Precision, Recall, F1 vs Threshold
    ax1 = axes[0, 0]
    ax1.plot(df_curves["threshold"], df_curves["precision"], "o-", label="Precision", color="#3498db", lw=2, markersize=4)
    ax1.plot(df_curves["threshold"], df_curves["recall"], "s-", label="Recall", color="#e74c3c", lw=2, markersize=4)
    ax1.plot(df_curves["threshold"], df_curves["f1"], "^-", label="F1 Score", color="#2ecc71", lw=2, markersize=4)
    ax1.axvline(x=0.50, color="gray", linestyle="--", alpha=0.8, label="Default (0.50)")
    tau_opt_5 = df_opt.loc[df_opt["cost_ratio_fp_fn"] == "1:5", "optimal_threshold"].values[0]
    ax1.axvline(x=tau_opt_5, color="#f39c12", linestyle="--", lw=2, label=f"Optimal 1:5 ({tau_opt_5:.2f})")
    ax1.set_xlabel("Classification Decision Threshold", fontweight="bold", fontsize=11)
    ax1.set_ylabel("Metric Score", fontweight="bold", fontsize=11)
    ax1.set_title("Classification Metrics vs. Decision Threshold", fontweight="bold", fontsize=12)
    ax1.legend(frameon=True, loc="center right")
    ax1.set_xlim(0.05, 0.90)
    ax1.set_ylim(-0.02, 1.02)

    # Panel 2: Total Business Cost Curves across 3 Scenarios
    ax2 = axes[0, 1]
    colors = ["#2980b9", "#f39c12", "#c0392b"]
    for i, (sc_name, c_fp, c_fn) in enumerate(cost_scenarios):
        norm_cost = df_curves[f"norm_cost_{c_fp}_{c_fn}"]
        opt_t = df_opt.loc[df_opt["cost_ratio_fp_fn"] == f"{int(c_fp)}:{int(c_fn)}", "optimal_threshold"].values[0]
        min_c = df_curves.loc[df_curves["threshold"] == opt_t, f"norm_cost_{c_fp}_{c_fn}"].values[0]
        ax2.plot(df_curves["threshold"], norm_cost, lw=2.5, color=colors[i], label=f"{int(c_fp)}:{int(c_fn)} Cost Ratio (Min @ {opt_t:.2f})")
        ax2.scatter([opt_t], [min_c], s=120, color=colors[i], zorder=5)

    ax2.axvline(x=0.50, color="gray", linestyle="--", alpha=0.8, label="Default (0.50)")
    ax2.set_xlabel("Classification Decision Threshold", fontweight="bold", fontsize=11)
    ax2.set_ylabel("Normalized Expected Cost per Order ($)", fontweight="bold", fontsize=11)
    ax2.set_title("Normalized Business Cost vs. Decision Threshold", fontweight="bold", fontsize=12)
    ax2.legend(frameon=True, loc="upper right")
    ax2.set_xlim(0.05, 0.90)

    # Panel 3: Confusion Matrix Stackplot (TP, FP, FN, TN)
    ax3 = axes[1, 0]
    ax3.stackplot(
        df_curves["threshold"],
        df_curves["tp"], df_curves["fp"], df_curves["fn"], df_curves["tn"],
        labels=["True Positive (Intervened Detractor)", "False Positive (Unneeded Contact)",
                "False Negative (Missed Detractor)", "True Negative (Correctly Left Alone)"],
        colors=["#27ae60", "#e74c3c", "#f39c12", "#3498db"],
        alpha=0.85
    )
    ax3.axvline(x=tau_opt_5, color="black", linestyle="--", lw=2, label=f"Optimal 1:5 ({tau_opt_5:.2f})")
    ax3.set_xlabel("Classification Decision Threshold", fontweight="bold", fontsize=11)
    ax3.set_ylabel("Order Count across 5-Fold Validation", fontweight="bold", fontsize=11)
    ax3.set_title("Confusion Matrix Breakdown vs. Decision Threshold", fontweight="bold", fontsize=12)
    ax3.legend(frameon=True, loc="center right", fontsize=9)
    ax3.set_xlim(0.05, 0.90)

    # Panel 4: Alert Rate (%) vs Threshold
    ax4 = axes[1, 1]
    ax4.plot(df_curves["threshold"], df_curves["alert_rate"] * 100.0, "o-", color="#8e44ad", lw=2, markersize=4)
    base_rate = (y_true.sum() / n_samples) * 100.0
    ax4.axhline(y=base_rate, color="gray", linestyle=":", alpha=0.9, label=f"True Detractor Rate ({base_rate:.1f}%)")
    opt_rate = df_opt.loc[df_opt["cost_ratio_fp_fn"] == "1:5", "optimal_alert_rate"].values[0] * 100.0
    ax4.axvline(x=tau_opt_5, color="#f39c12", linestyle="--", lw=2, label=f"Optimal 1:5 Alert Rate ({opt_rate:.1f}%)")
    ax4.set_xlabel("Classification Decision Threshold", fontweight="bold", fontsize=11)
    ax4.set_ylabel("Orders Flagged for Intervention (%)", fontweight="bold", fontsize=11)
    ax4.set_title("Customer Intervention Capacity vs. Threshold", fontweight="bold", fontsize=12)
    ax4.legend(frameon=True, loc="upper right")
    ax4.set_xlim(0.05, 0.90)

    plt.tight_layout()
    plot_path = OUTPUT_DIR / "threshold_optimization_4panel.png"
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"Saved 4-Panel Threshold Optimization Plot to: {plot_path}")


def main():
    print("=" * 80)
    print("EXPERIMENT 3 — PHASE 5: PROBABILITY CALIBRATION & THRESHOLD OPTIMIZATION")
    print("=" * 80)

    f, cv, hashes = load_development()
    df_clf = task_rows(f, cv, "classification").copy()
    print(f"Loaded {len(df_clf):,} classification orders for Phase 5 evaluation.")

    # 1. Run Calibration Audit
    oof_predictions = run_probability_calibration_audit(df_clf)

    # 2. Run Asymmetric Cost-Curve Threshold Optimization
    run_threshold_cost_optimization(oof_predictions)

    print("\n" + "=" * 80)
    print("PHASE 5 CALIBRATION & THRESHOLD OPTIMIZATION COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()
