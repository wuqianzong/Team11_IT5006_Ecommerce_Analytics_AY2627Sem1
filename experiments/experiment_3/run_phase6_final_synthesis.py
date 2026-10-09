#!/usr/bin/env python3
"""Experiment 3 — Phase 6: Final Master Synthesis & Unified Train-Validation-Holdout Benchmark.

Evaluates the complete model progression from Baseline (27 features) to Tuned Architectures
(13/14 features + Log1p scaling + GridSearchCV optimization) across all three data partitions:
  1. Train Resubstitution (Development Training Set)
  2. 5-Fold Cross-Validation (Mean ± SD across 5 temporal validation folds)
  3. Terminal Holdout Evaluation (Locked 20% unseen test set)

Computes:
  - Full metrics for Regression: MAE, RMSE, R²
  - Full metrics for Classification: Average Precision (AP), ROC-AUC, Brier Score,
    and thresholded metrics (Precision, Recall, F1, 1:5 Business Cost) at default tau=0.50
    and optimal business operating threshold tau*=0.17.
  - Generalization Gap = Holdout - Val Mean
  - Overfitting diagnosis

Outputs saved strictly to:
  artifacts/metrics/experiment-3/final_synthesis/
"""

import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, FunctionTransformer
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import average_precision_score, roc_auc_score, brier_score_loss
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score
from sklearn.base import clone

# Add repo root to import path
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.models.data import load_development, task_rows, fold_indices, PREDICTOR_ALLOWLIST
from src.features.contract import CATEGORICAL_COLUMNS
from src.models.refinement_core import CORE_FEATURES

OUTPUT_DIR = REPO_ROOT / "artifacts" / "metrics" / "experiment-3" / "final_synthesis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Feature subsets
REG_13_FEATURES = CORE_FEATURES + ["distance_km_max", "distance_missing_fraction"]
CLF_14_FEATURES = CORE_FEATURES + ["n_sellers", "primary_seller_state", "interstate_share"]
SKEWED_NUMERIC_COLS = ["total_price", "total_freight", "distance_km_max"]


def load_holdout_data():
    """Load the locked holdout test set completely independent of development."""
    ml_dir = REPO_ROOT / "data" / "business" / "ml"
    base = pd.read_csv(ml_dir / "orders_ml_features.csv", dtype={"order_id": "string", "customer_unique_id": "string"})
    splits = pd.read_csv(ml_dir / "split_assignments.csv", dtype="string")
    selected_ids = splits.loc[splits["split_assignment"].eq("holdout"), "order_id"]
    holdout = base.loc[base["order_id"].isin(selected_ids)].sort_values("order_id").reset_index(drop=True)

    df_holdout_reg = holdout.loc[holdout["eligible_regression"].eq(1)].copy().reset_index(drop=True)
    df_holdout_clf = holdout.loc[holdout["eligible_classification"].eq(1)].copy().reset_index(drop=True)
    return df_holdout_reg, df_holdout_clf


def build_preprocessor(feature_names, apply_log1p_num=False):
    """Build ColumnTransformer."""
    num_cols = [c for c in feature_names if c not in CATEGORICAL_COLUMNS]
    cat_cols = [c for c in feature_names if c in CATEGORICAL_COLUMNS]

    skewed_in_subset = [c for c in SKEWED_NUMERIC_COLS if c in num_cols]
    normal_num_in_subset = [c for c in num_cols if c not in skewed_in_subset]

    transformers = []
    if apply_log1p_num and skewed_in_subset:
        skewed_pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("log1p", FunctionTransformer(np.log1p, validate=False)),
            ("scaler", StandardScaler())
        ])
        transformers.append(("skewed_num", skewed_pipe, skewed_in_subset))

    regular_num_cols = normal_num_in_subset if apply_log1p_num else num_cols
    if regular_num_cols:
        reg_num_pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ])
        transformers.append(("reg_num", reg_num_pipe, regular_num_cols))

    if cat_cols:
        cat_pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
            ("ohe", OneHotEncoder(drop="first", handle_unknown="ignore", sparse_output=False))
        ])
        transformers.append(("cat", cat_pipe, cat_cols))

    return ColumnTransformer(transformers=transformers, remainder="drop")


def evaluate_regression_models(df_dev, df_holdout, seed=42):
    """Benchmark regression models across Train, 5-Fold CV, and Holdout."""
    print("\n" + "=" * 80)
    print("EVALUATING REGRESSION BENCHMARK: TRAIN vs 5-FOLD CV vs TERMINAL HOLDOUT")
    print("=" * 80)

    # 1. Define model pipelines
    # Baseline 27 features (Untuned Random Forest baseline)
    prep_27 = build_preprocessor(PREDICTOR_ALLOWLIST, apply_log1p_num=False)
    pipe_baseline_27 = Pipeline([
        ("preprocess", prep_27),
        ("model", RandomForestRegressor(n_estimators=50, max_depth=10, min_samples_leaf=50, random_state=seed, n_jobs=-1))
    ])

    # 13 Features Preprocessor (with log1p pre-scaling)
    prep_13 = build_preprocessor(REG_13_FEATURES, apply_log1p_num=True)

    # Tuned Ridge (alpha=1.0 + Target Log1p)
    pipe_ridge_inner = Pipeline([("preprocess", prep_13), ("model", Ridge(alpha=1.0, random_state=seed))])
    pipe_ridge = TransformedTargetRegressor(regressor=pipe_ridge_inner, func=np.log1p, inverse_func=np.expm1)

    # Tuned Decision Tree (depth=10, leaf=100 + Target Log1p)
    pipe_dt_inner = Pipeline([("preprocess", prep_13), ("model", DecisionTreeRegressor(max_depth=10, min_samples_leaf=100, random_state=seed))])
    pipe_dt = TransformedTargetRegressor(regressor=pipe_dt_inner, func=np.log1p, inverse_func=np.expm1)

    # Tuned Random Forest Champion (depth=14, leaf=20 + Target Log1p)
    pipe_rf_inner = Pipeline([("preprocess", prep_13), ("model", RandomForestRegressor(n_estimators=50, max_depth=14, min_samples_leaf=20, random_state=seed, n_jobs=-1))])
    pipe_rf = TransformedTargetRegressor(regressor=pipe_rf_inner, func=np.log1p, inverse_func=np.expm1)

    models = [
        ("Baseline (27 Features Untuned)", PREDICTOR_ALLOWLIST, pipe_baseline_27, "Original Baseline"),
        ("Ridge Linear (Tuned, 13 Feat + Log1p)", REG_13_FEATURES, pipe_ridge, "Linear Parametric"),
        ("Decision Tree (Tuned, 13 Feat + Log1p)", REG_13_FEATURES, pipe_dt, "Non-Linear Tree"),
        ("Random Forest (Champion, 13 Feat + Log1p)", REG_13_FEATURES, pipe_rf, "Complex Ensemble Champion")
    ]

    records = []
    y_dev = df_dev["lead_days"].values
    y_holdout = df_holdout["lead_days"].values

    for model_name, feat_cols, pipe, archetype in models:
        print(f"\nRunning benchmark for: {model_name}...")

        # 1. 5-Fold Cross Validation
        cv_maes, cv_rmses, cv_r2s = [], [], []
        for fold, train_idx, val_idx in fold_indices(df_dev):
            tr_df = df_dev.iloc[train_idx]
            va_df = df_dev.iloc[val_idx]

            fold_est = clone(pipe)
            fold_est.fit(tr_df[feat_cols], tr_df["lead_days"])
            val_preds = np.clip(fold_est.predict(va_df[feat_cols]), 0.0, None)
            y_val = va_df["lead_days"].values

            cv_maes.append(mean_absolute_error(y_val, val_preds))
            cv_rmses.append(np.sqrt(mean_squared_error(y_val, val_preds)))
            cv_r2s.append(r2_score(y_val, val_preds))

        cv_mae_mean, cv_mae_std = np.mean(cv_maes), np.std(cv_maes)
        cv_rmse_mean, cv_rmse_std = np.mean(cv_rmses), np.std(cv_rmses)
        cv_r2_mean, cv_r2_std = np.mean(cv_r2s), np.std(cv_r2s)

        # 2. Fit on Entire Development Set
        full_est = clone(pipe)
        full_est.fit(df_dev[feat_cols], y_dev)

        # 3. Train Resubstitution
        train_preds = np.clip(full_est.predict(df_dev[feat_cols]), 0.0, None)
        train_mae = mean_absolute_error(y_dev, train_preds)
        train_rmse = np.sqrt(mean_squared_error(y_dev, train_preds))
        train_r2 = r2_score(y_dev, train_preds)

        # 4. Terminal Holdout Evaluation
        holdout_preds = np.clip(full_est.predict(df_holdout[feat_cols]), 0.0, None)
        holdout_mae = mean_absolute_error(y_holdout, holdout_preds)
        holdout_rmse = np.sqrt(mean_squared_error(y_holdout, holdout_preds))
        holdout_r2 = r2_score(y_holdout, holdout_preds)

        # Generalization gap (Holdout - CV Mean)
        gen_gap_mae = holdout_mae - cv_mae_mean

        records.append({
            "task": "Regression (Lead Time)",
            "model_architecture": model_name,
            "archetype": archetype,
            "feature_count": len(feat_cols),
            "train_mae": train_mae,
            "cv_mae_mean": cv_mae_mean,
            "cv_mae_std": cv_mae_std,
            "holdout_mae": holdout_mae,
            "generalization_gap_mae": gen_gap_mae,
            "train_rmse": train_rmse,
            "cv_rmse_mean": cv_rmse_mean,
            "cv_rmse_std": cv_rmse_std,
            "holdout_rmse": holdout_rmse,
            "train_r2": train_r2,
            "cv_r2_mean": cv_r2_mean,
            "cv_r2_std": cv_r2_std,
            "holdout_r2": holdout_r2
        })

        print(f"  Train MAE: {train_mae:.3f}d | 5-Fold CV MAE: {cv_mae_mean:.3f}±{cv_mae_std:.3f}d | Holdout MAE: {holdout_mae:.3f}d (Gap: {gen_gap_mae:+.3f}d)")

    return pd.DataFrame(records)


def evaluate_classification_models(df_dev, df_holdout, seed=42):
    """Benchmark classification models across Train, 5-Fold CV, and Holdout."""
    print("\n" + "=" * 80)
    print("EVALUATING CLASSIFICATION BENCHMARK: TRAIN vs 5-FOLD CV vs TERMINAL HOLDOUT")
    print("=" * 80)

    # 1. Define model pipelines
    # Baseline 27 features (Untuned Random Forest baseline)
    prep_27 = build_preprocessor(PREDICTOR_ALLOWLIST, apply_log1p_num=False)
    pipe_baseline_27 = Pipeline([
        ("preprocess", prep_27),
        ("model", RandomForestClassifier(n_estimators=50, max_depth=10, min_samples_leaf=50, random_state=seed, n_jobs=-1))
    ])

    # 14 Features Preprocessor (with log1p pre-scaling)
    prep_14 = build_preprocessor(CLF_14_FEATURES, apply_log1p_num=True)

    # Tuned Logistic Regression (C=0.01 + Log1p Input)
    pipe_log = Pipeline([
        ("preprocess", prep_14),
        ("model", LogisticRegression(C=0.01, solver="lbfgs", max_iter=2000, random_state=seed))
    ])

    # Tuned Decision Tree (depth=10, leaf=200 + Log1p Input)
    pipe_dt = Pipeline([
        ("preprocess", prep_14),
        ("model", DecisionTreeClassifier(max_depth=10, min_samples_leaf=200, random_state=seed))
    ])

    # Tuned Random Forest Champion (depth=14, leaf=20 + Log1p Input)
    pipe_rf = Pipeline([
        ("preprocess", prep_14),
        ("model", RandomForestClassifier(n_estimators=50, max_depth=14, min_samples_leaf=20, random_state=seed, n_jobs=-1))
    ])

    models = [
        ("Baseline (27 Features Untuned)", PREDICTOR_ALLOWLIST, pipe_baseline_27, "Original Baseline"),
        ("Logistic Regression (Tuned, 14 Feat + Log1p)", CLF_14_FEATURES, pipe_log, "Linear Parametric"),
        ("Decision Tree (Tuned, 14 Feat + Log1p)", CLF_14_FEATURES, pipe_dt, "Non-Linear Tree"),
        ("Random Forest (Champion, 14 Feat + Log1p)", CLF_14_FEATURES, pipe_rf, "Complex Ensemble Champion")
    ]

    records = []
    y_dev = df_dev["is_detractor"].values
    y_holdout = df_holdout["is_detractor"].values

    for model_name, feat_cols, pipe, archetype in models:
        print(f"\nRunning benchmark for: {model_name}...")

        # 1. 5-Fold Cross Validation
        cv_aps, cv_aucs, cv_briers = [], [], []
        cv_f1_050, cv_cost_050 = [], []
        cv_f1_opt, cv_cost_opt = [], []

        for fold, train_idx, val_idx in fold_indices(df_dev):
            tr_df = df_dev.iloc[train_idx]
            va_df = df_dev.iloc[val_idx]

            fold_est = clone(pipe)
            fold_est.fit(tr_df[feat_cols], tr_df["is_detractor"])
            val_probs = fold_est.predict_proba(va_df[feat_cols])[:, 1]
            y_val = va_df["is_detractor"].values

            cv_aps.append(average_precision_score(y_val, val_probs))
            cv_aucs.append(roc_auc_score(y_val, val_probs))
            cv_briers.append(brier_score_loss(y_val, val_probs))

            # Default tau = 0.50
            pred_050 = (val_probs >= 0.50).astype(int)
            tn, fp, fn, tp = confusion_matrix(y_val, pred_050).ravel()
            cv_f1_050.append(f1_score(y_val, pred_050, zero_division=0))
            cv_cost_050.append(fp + 5 * fn)

            # Optimal business tau = 0.17
            pred_opt = (val_probs >= 0.17).astype(int)
            tn, fp, fn, tp = confusion_matrix(y_val, pred_opt).ravel()
            cv_f1_opt.append(f1_score(y_val, pred_opt, zero_division=0))
            cv_cost_opt.append(fp + 5 * fn)

        cv_ap_mean, cv_ap_std = np.mean(cv_aps), np.std(cv_aps)
        cv_auc_mean, cv_auc_std = np.mean(cv_aucs), np.std(cv_aucs)
        cv_brier_mean, cv_brier_std = np.mean(cv_briers), np.std(cv_briers)
        cv_f1_050_mean = np.mean(cv_f1_050)
        cv_f1_opt_mean = np.mean(cv_f1_opt)

        # 2. Fit on Entire Development Set
        full_est = clone(pipe)
        full_est.fit(df_dev[feat_cols], y_dev)

        # 3. Train Resubstitution
        train_probs = full_est.predict_proba(df_dev[feat_cols])[:, 1]
        train_ap = average_precision_score(y_dev, train_probs)
        train_auc = roc_auc_score(y_dev, train_probs)
        train_brier = brier_score_loss(y_dev, train_probs)

        # 4. Terminal Holdout Evaluation
        holdout_probs = full_est.predict_proba(df_holdout[feat_cols])[:, 1]
        holdout_ap = average_precision_score(y_holdout, holdout_probs)
        holdout_auc = roc_auc_score(y_holdout, holdout_probs)
        holdout_brier = brier_score_loss(y_holdout, holdout_probs)

        # Holdout metrics at tau = 0.50
        h_pred_050 = (holdout_probs >= 0.50).astype(int)
        h_tn5, h_fp5, h_fn5, h_tp5 = confusion_matrix(y_holdout, h_pred_050).ravel()
        h_prec_050 = precision_score(y_holdout, h_pred_050, zero_division=0)
        h_rec_050 = recall_score(y_holdout, h_pred_050, zero_division=0)
        h_f1_050 = f1_score(y_holdout, h_pred_050, zero_division=0)
        h_cost_050 = h_fp5 + 5 * h_fn5

        # Holdout metrics at optimal tau = 0.17
        h_pred_opt = (holdout_probs >= 0.17).astype(int)
        h_tn_opt, h_fp_opt, h_fn_opt, h_tp_opt = confusion_matrix(y_holdout, h_pred_opt).ravel()
        h_prec_opt = precision_score(y_holdout, h_pred_opt, zero_division=0)
        h_rec_opt = recall_score(y_holdout, h_pred_opt, zero_division=0)
        h_f1_opt = f1_score(y_holdout, h_pred_opt, zero_division=0)
        h_cost_opt = h_fp_opt + 5 * h_fn_opt

        gen_gap_ap = holdout_ap - cv_ap_mean

        records.append({
            "task": "Classification (Detractor)",
            "model_architecture": model_name,
            "archetype": archetype,
            "feature_count": len(feat_cols),
            "train_ap": train_ap,
            "cv_ap_mean": cv_ap_mean,
            "cv_ap_std": cv_ap_std,
            "holdout_ap": holdout_ap,
            "generalization_gap_ap": gen_gap_ap,
            "train_auc": train_auc,
            "cv_auc_mean": cv_auc_mean,
            "cv_auc_std": cv_auc_std,
            "holdout_auc": holdout_auc,
            "train_brier": train_brier,
            "cv_brier_mean": cv_brier_mean,
            "cv_brier_std": cv_brier_std,
            "holdout_brier": holdout_brier,
            "holdout_f1_default_050": h_f1_050,
            "holdout_cost_default_050": h_cost_050,
            "holdout_f1_optimal_017": h_f1_opt,
            "holdout_cost_optimal_017": h_cost_opt,
            "holdout_cost_savings_pct": (h_cost_050 - h_cost_opt) / h_cost_050 * 100.0
        })

        print(f"  Train AP: {train_ap:.4f} | 5-Fold CV AP: {cv_ap_mean:.4f}±{cv_ap_std:.4f} | Holdout AP: {holdout_ap:.4f} (Gap: {gen_gap_ap:+.4f})")
        print(f"  Holdout Cost (1:5): Default tau=0.50: {h_cost_050:,} | Optimal tau=0.17: {h_cost_opt:,} (Saved: {(h_cost_050 - h_cost_opt) / h_cost_050 * 100.0:.1f}%)")

    return pd.DataFrame(records)


def generate_benchmark_figures(df_reg_bench, df_clf_bench):
    """Generate professional visual summary figures for Milestone 2."""
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), dpi=150)

    # 1. Regression Benchmark
    models_reg = ["Baseline (27 Feat)", "Ridge Linear", "Decision Tree", "Random Forest (Champion)"]
    x = np.arange(len(models_reg))
    width = 0.28

    tr_mae = df_reg_bench["train_mae"].values
    cv_mae = df_reg_bench["cv_mae_mean"].values
    cv_err = df_reg_bench["cv_mae_std"].values
    ho_mae = df_reg_bench["holdout_mae"].values

    b1 = ax1.bar(x - width, tr_mae, width, label="Train Resubstitution", color="#bdc3c7", edgecolor="black")
    b2 = ax1.bar(x, cv_mae, width, yerr=cv_err, label="5-Fold CV Validation", color="#2980b9", edgecolor="black", capsize=4)
    b3 = ax1.bar(x + width, ho_mae, width, label="Terminal Holdout", color="#27ae60", edgecolor="black")

    ax1.set_xticks(x)
    ax1.set_xticklabels(models_reg, fontweight="bold", fontsize=10, rotation=10)
    ax1.set_ylabel("Mean Absolute Error in Days (Lower is Better)", fontweight="bold", fontsize=11)
    ax1.set_title("Regression: Train vs. 5-Fold CV vs. Terminal Holdout", fontweight="bold", fontsize=12)
    ax1.set_ylim(3.5, 5.7)
    ax1.legend(frameon=True)

    for bar in b3:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.03, f"{yval:.2f}d", ha="center", va="bottom", fontsize=9, fontweight="bold")

    # 2. Classification Benchmark
    models_clf = ["Baseline (27 Feat)", "Logistic Reg", "Decision Tree", "Random Forest (Champion)"]
    x2 = np.arange(len(models_clf))

    tr_ap = df_clf_bench["train_ap"].values
    cv_ap = df_clf_bench["cv_ap_mean"].values
    cv_ap_err = df_clf_bench["cv_ap_std"].values
    ho_ap = df_clf_bench["holdout_ap"].values

    b4 = ax2.bar(x2 - width, tr_ap, width, label="Train Resubstitution", color="#bdc3c7", edgecolor="black")
    b5 = ax2.bar(x2, cv_ap, width, yerr=cv_ap_err, label="5-Fold CV Validation", color="#2980b9", edgecolor="black", capsize=4)
    b6 = ax2.bar(x2 + width, ho_ap, width, label="Terminal Holdout", color="#27ae60", edgecolor="black")

    ax2.set_xticks(x2)
    ax2.set_xticklabels(models_clf, fontweight="bold", fontsize=10, rotation=10)
    ax2.set_ylabel("Average Precision / PR-AUC (Higher is Better)", fontweight="bold", fontsize=11)
    ax2.set_title("Classification: Train vs. 5-Fold CV vs. Terminal Holdout", fontweight="bold", fontsize=12)
    ax2.set_ylim(0.20, 0.45)
    ax2.legend(frameon=True)

    for bar in b6:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.003, f"{yval:.4f}", ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.tight_layout()
    fig_path = OUTPUT_DIR / "unified_benchmark_table.png"
    plt.savefig(fig_path, dpi=150)
    plt.close()
    print(f"\nSaved Unified Benchmark Figure to: {fig_path}")


def main():
    print("=" * 80)
    print("EXPERIMENT 3 — PHASE 6: FINAL MASTER SYNTHESIS & UNIFIED BENCHMARK")
    print("=" * 80)

    f, cv, hashes = load_development()
    df_dev_reg = task_rows(f, cv, "regression").copy()
    df_dev_clf = task_rows(f, cv, "classification").copy()

    df_holdout_reg, df_holdout_clf = load_holdout_data()

    print(f"Loaded Development: {len(df_dev_reg):,} Reg | {len(df_dev_clf):,} Clf")
    print(f"Loaded Holdout:     {len(df_holdout_reg):,} Reg | {len(df_holdout_clf):,} Clf")

    # 1. Evaluate Regression
    df_reg_bench = evaluate_regression_models(df_dev_reg, df_holdout_reg)

    # 2. Evaluate Classification
    df_clf_bench = evaluate_classification_models(df_dev_clf, df_holdout_clf)

    # Combine into unified master table
    df_reg_bench.to_csv(OUTPUT_DIR / "unified_regression_benchmark.csv", index=False)
    df_clf_bench.to_csv(OUTPUT_DIR / "unified_classification_benchmark.csv", index=False)
    print(f"\nSaved Regression Benchmark to: {OUTPUT_DIR / 'unified_regression_benchmark.csv'}")
    print(f"Saved Classification Benchmark to: {OUTPUT_DIR / 'unified_classification_benchmark.csv'}")

    # Generate figures
    generate_benchmark_figures(df_reg_bench, df_clf_bench)

    print("\n" + "=" * 80)
    print("PHASE 6 MASTER BENCHMARK COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()
