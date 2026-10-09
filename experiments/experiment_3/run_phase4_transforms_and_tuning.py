#!/usr/bin/env python3
"""Experiment 3 — Phase 4: Pre-Scaling, Target Log-Transformations & GridSearchCV Model Tuning.

Evaluates:
- Phase 4A: Transformations & Scaling
  * Input log1p pre-scaling on skewed continuous features (total_price, total_freight, distance_km_max) before StandardScaler.
  * Target log-transformation on lead_days via TransformedTargetRegressor(func=np.log1p, inverse_func=np.expm1).
- Phase 4B: Full GridSearchCV Hyperparameter Tuning across All Candidate Model Families:
  * Regression: Ridge, Decision Tree, Random Forest
  * Classification: Logistic Regression, Decision Tree, Random Forest
- Evaluates Default vs. Tuned models to identify the true optimal architecture without default hyperparameter bias.

Outputs saved strictly to:
artifacts/metrics/experiment-3/transforms_and_tuning/
"""

import sys
import json
import time
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, FunctionTransformer
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import average_precision_score, roc_auc_score, brier_score_loss, accuracy_score

# Add repo root to import path
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from src.models.data import load_development, task_rows, fold_indices
from src.features.contract import CATEGORICAL_COLUMNS
from src.models.refinement_core import CORE_FEATURES

OUTPUT_DIR = REPO_ROOT / "artifacts" / "metrics" / "experiment-3" / "transforms_and_tuning"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Final Selected Feature Subsets
REG_13_FEATURES = CORE_FEATURES + ["distance_km_max", "distance_missing_fraction"]
CLF_14_FEATURES = CORE_FEATURES + ["n_sellers", "primary_seller_state", "interstate_share"]

# Continuous features requiring log1p pre-scaling (skewness > 2.0 audited in Phase 1)
SKEWED_NUMERIC_COLS = ["total_price", "total_freight", "distance_km_max"]


def build_preprocessor(feature_names, apply_log1p_num=False):
    """Build a ColumnTransformer with optional log1p pre-scaling on skewed continuous predictors."""
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


def run_phase4a_transforms_ablation(df_reg, df_clf, seed=42):
    """Phase 4A: Ablation study of input log1p pre-scaling and target log-transformation."""
    print("\n" + "=" * 80)
    print("PHASE 4A: PRE-SCALING & TARGET LOG-TRANSFORMATION ABLATION")
    print("=" * 80)

    results = []

    # 1. Regression Target Transformation & Input Scaling Ablation
    # We test 3 configurations:
    # A: Standard Baseline (No input log, Raw Target)
    # B: Input log1p on skewed predictors, Raw Target
    # C: Input log1p on skewed predictors, Target log1p (TransformedTargetRegressor)
    reg_configs = [
        ("Raw Input + Raw Target (Baseline)", False, False),
        ("Log1p Input + Raw Target", True, False),
        ("Log1p Input + Log1p Target (TransformedTargetRegressor)", True, True)
    ]

    reg_models = [
        ("Ridge Linear", Ridge(alpha=1.0, random_state=seed)),
        ("Decision Tree", DecisionTreeRegressor(max_depth=5, min_samples_leaf=100, random_state=seed)),
        ("Random Forest", RandomForestRegressor(n_estimators=50, max_depth=10, min_samples_leaf=50, random_state=seed, n_jobs=-1))
    ]

    for config_name, apply_in_log, apply_tgt_log in reg_configs:
        print(f"\nEvaluating Regression: {config_name}...")
        for model_name, model_inst in reg_models:
            fold_metrics = []
            for fold, train_idx, val_idx in fold_indices(df_reg):
                train_df = df_reg.iloc[train_idx]
                val_df = df_reg.iloc[val_idx]

                preprocessor = build_preprocessor(REG_13_FEATURES, apply_log1p_num=apply_in_log)
                pipe = Pipeline([("preprocess", preprocessor), ("model", model_inst)])

                if apply_tgt_log:
                    full_est = TransformedTargetRegressor(
                        regressor=pipe, func=np.log1p, inverse_func=np.expm1
                    )
                else:
                    full_est = pipe

                full_est.fit(train_df[REG_13_FEATURES], train_df["lead_days"])
                preds = full_est.predict(val_df[REG_13_FEATURES])
                y_true = val_df["lead_days"].values

                # Clip negative predictions if any
                preds = np.clip(preds, 0.0, None)

                mae = mean_absolute_error(y_true, preds)
                rmse = np.sqrt(mean_squared_error(y_true, preds))
                r2 = r2_score(y_true, preds)
                fold_metrics.append({"mae": mae, "rmse": rmse, "r2": r2})

            df_f = pd.DataFrame(fold_metrics)
            results.append({
                "task": "Regression (Lead Time)",
                "configuration": config_name,
                "model": model_name,
                "metric_primary": "MAE (Days)",
                "primary_mean": df_f["mae"].mean(),
                "primary_std": df_f["mae"].std(),
                "metric_secondary": "RMSE (Days)",
                "secondary_mean": df_f["rmse"].mean(),
                "secondary_std": df_f["rmse"].std(),
                "r2_mean": df_f["r2"].mean(),
                "r2_std": df_f["r2"].std()
            })
            print(f"  [{model_name}] MAE: {df_f['mae'].mean():.4f} ± {df_f['mae'].std():.4f} d | RMSE: {df_f['rmse'].mean():.4f} | R²: {df_f['r2'].mean():.4f}")

    # 2. Classification Input Scaling Ablation
    # A: Standard Baseline (Raw input)
    # B: Log1p Input on skewed predictors
    clf_configs = [
        ("Raw Input (Baseline)", False),
        ("Log1p Input on Skewed Predictors", True)
    ]
    clf_models = [
        ("Logistic Regression", LogisticRegression(C=0.01, solver="lbfgs", max_iter=2000, random_state=seed)),
        ("Decision Tree", DecisionTreeClassifier(max_depth=5, min_samples_leaf=100, random_state=seed)),
        ("Random Forest", RandomForestClassifier(n_estimators=50, max_depth=10, min_samples_leaf=50, random_state=seed, n_jobs=-1))
    ]

    for config_name, apply_in_log in clf_configs:
        print(f"\nEvaluating Classification: {config_name}...")
        for model_name, model_inst in clf_models:
            fold_metrics = []
            for fold, train_idx, val_idx in fold_indices(df_clf):
                train_df = df_clf.iloc[train_idx]
                val_df = df_clf.iloc[val_idx]

                preprocessor = build_preprocessor(CLF_14_FEATURES, apply_log1p_num=apply_in_log)
                pipe = Pipeline([("preprocess", preprocessor), ("model", model_inst)])
                pipe.fit(train_df[CLF_14_FEATURES], train_df["is_detractor"])

                probs = pipe.predict_proba(val_df[CLF_14_FEATURES])[:, 1]
                y_true = val_df["is_detractor"].values

                ap = average_precision_score(y_true, probs)
                roc = roc_auc_score(y_true, probs)
                brier = brier_score_loss(y_true, probs)
                fold_metrics.append({"ap": ap, "roc_auc": roc, "brier": brier})

            df_f = pd.DataFrame(fold_metrics)
            results.append({
                "task": "Classification (Detractor)",
                "configuration": config_name,
                "model": model_name,
                "metric_primary": "Average Precision (AP)",
                "primary_mean": df_f["ap"].mean(),
                "primary_std": df_f["ap"].std(),
                "metric_secondary": "ROC-AUC",
                "secondary_mean": df_f["roc_auc"].mean(),
                "secondary_std": df_f["roc_auc"].std(),
                "brier_mean": df_f["brier"].mean(),
                "brier_std": df_f["brier"].std()
            })
            print(f"  [{model_name}] AP: {df_f['ap'].mean():.4f} ± {df_f['ap'].std():.4f} | ROC-AUC: {df_f['roc_auc'].mean():.4f} | Brier: {df_f['brier'].mean():.4f}")

    df_ablation = pd.DataFrame(results)
    ablation_csv_path = OUTPUT_DIR / "phase4a_transforms_ablation.csv"
    df_ablation.to_csv(ablation_csv_path, index=False)
    print(f"\nSaved Phase 4A ablation results to: {ablation_csv_path}")
    return df_ablation


def run_phase4b_gridsearch_tuning(df_reg, df_clf, seed=42):
    """Phase 4B: Full GridSearchCV Hyperparameter Tuning across All Candidate Models."""
    print("\n" + "=" * 80)
    print("PHASE 4B: FULL GRIDSEARCHCV HYPERPARAMETER TUNING ACROSS ALL CANDIDATE MODELS")
    print("=" * 80)

    # Convert folds into (train_idx, val_idx) list for GridSearchCV cv parameter
    reg_cv_splits = [(train_idx, val_idx) for _, train_idx, val_idx in fold_indices(df_reg)]
    clf_cv_splits = [(train_idx, val_idx) for _, train_idx, val_idx in fold_indices(df_clf)]

    tuning_summary = []

    # 1. Regression Tuning
    print("\n--- Tuning Regression Models on 13 Features (with Log1p Input + Log1p Target) ---")
    reg_preprocessor = build_preprocessor(REG_13_FEATURES, apply_log1p_num=True)

    # 1A. Ridge Regression Tuning
    print("  [1/3] Tuning Ridge Linear Regression (alpha search)...")
    pipe_ridge = Pipeline([("preprocess", reg_preprocessor), ("model", Ridge(random_state=seed))])
    tgt_ridge = TransformedTargetRegressor(regressor=pipe_ridge, func=np.log1p, inverse_func=np.expm1)
    param_grid_ridge = {
        "regressor__model__alpha": [0.01, 0.1, 1.0, 10.0, 100.0, 500.0]
    }
    gs_ridge = GridSearchCV(
        tgt_ridge, param_grid_ridge, cv=reg_cv_splits,
        scoring="neg_mean_absolute_error", n_jobs=-1, return_train_score=True
    )
    t0 = time.time()
    gs_ridge.fit(df_reg[REG_13_FEATURES], df_reg["lead_days"])
    ridge_time = time.time() - t0
    best_ridge_alpha = gs_ridge.best_params_["regressor__model__alpha"]
    best_ridge_mae = -gs_ridge.best_score_
    print(f"    Optimal alpha: {best_ridge_alpha} | Best Val MAE: {best_ridge_mae:.4f} d (fit in {ridge_time:.1f}s)")
    tuning_summary.append({
        "task": "Regression (Lead Time)",
        "model_family": "Ridge Linear",
        "best_hyperparameters": f"alpha={best_ridge_alpha}",
        "best_cv_score": best_ridge_mae,
        "scoring_metric": "neg_mean_absolute_error",
        "tuning_time_s": ridge_time
    })

    # 1B. Decision Tree Regression Tuning
    print("  [2/3] Tuning Decision Tree Regressor (max_depth, min_samples_leaf)...")
    pipe_dt = Pipeline([("preprocess", reg_preprocessor), ("model", DecisionTreeRegressor(random_state=seed))])
    tgt_dt = TransformedTargetRegressor(regressor=pipe_dt, func=np.log1p, inverse_func=np.expm1)
    param_grid_dt = {
        "regressor__model__max_depth": [4, 6, 8, 10],
        "regressor__model__min_samples_leaf": [20, 50, 100, 200]
    }
    gs_dt = GridSearchCV(
        tgt_dt, param_grid_dt, cv=reg_cv_splits,
        scoring="neg_mean_absolute_error", n_jobs=-1, return_train_score=True
    )
    t0 = time.time()
    gs_dt.fit(df_reg[REG_13_FEATURES], df_reg["lead_days"])
    dt_time = time.time() - t0
    best_dt_params = gs_dt.best_params_
    best_dt_mae = -gs_dt.best_score_
    print(f"    Optimal params: {best_dt_params} | Best Val MAE: {best_dt_mae:.4f} d (fit in {dt_time:.1f}s)")
    tuning_summary.append({
        "task": "Regression (Lead Time)",
        "model_family": "Decision Tree",
        "best_hyperparameters": str(best_dt_params),
        "best_cv_score": best_dt_mae,
        "scoring_metric": "neg_mean_absolute_error",
        "tuning_time_s": dt_time
    })

    # 1C. Random Forest Regression Tuning
    print("  [3/3] Tuning Random Forest Regressor (max_depth, min_samples_leaf)...")
    pipe_rf = Pipeline([("preprocess", reg_preprocessor), ("model", RandomForestRegressor(n_estimators=50, random_state=seed, n_jobs=-1))])
    tgt_rf = TransformedTargetRegressor(regressor=pipe_rf, func=np.log1p, inverse_func=np.expm1)
    param_grid_rf = {
        "regressor__model__max_depth": [6, 10, 14],
        "regressor__model__min_samples_leaf": [20, 50]
    }
    gs_rf = GridSearchCV(
        tgt_rf, param_grid_rf, cv=reg_cv_splits,
        scoring="neg_mean_absolute_error", n_jobs=-1, return_train_score=True
    )
    t0 = time.time()
    gs_rf.fit(df_reg[REG_13_FEATURES], df_reg["lead_days"])
    rf_time = time.time() - t0
    best_rf_params = gs_rf.best_params_
    best_rf_mae = -gs_rf.best_score_
    print(f"    Optimal params: {best_rf_params} | Best Val MAE: {best_rf_mae:.4f} d (fit in {rf_time:.1f}s)")
    tuning_summary.append({
        "task": "Regression (Lead Time)",
        "model_family": "Random Forest",
        "best_hyperparameters": str(best_rf_params),
        "best_cv_score": best_rf_mae,
        "scoring_metric": "neg_mean_absolute_error",
        "tuning_time_s": rf_time
    })

    # 2. Classification Tuning
    print("\n--- Tuning Classification Models on 14 Features (with Log1p Input) ---")
    clf_preprocessor = build_preprocessor(CLF_14_FEATURES, apply_log1p_num=True)

    # 2A. Logistic Regression Tuning
    print("  [1/3] Tuning Logistic Regression (C regularization search)...")
    pipe_logistic = Pipeline([("preprocess", clf_preprocessor), ("model", LogisticRegression(solver="lbfgs", max_iter=2000, random_state=seed))])
    param_grid_log = {
        "model__C": [0.001, 0.01, 0.1, 1.0, 10.0]
    }
    gs_log = GridSearchCV(
        pipe_logistic, param_grid_log, cv=clf_cv_splits,
        scoring="average_precision", n_jobs=-1, return_train_score=True
    )
    t0 = time.time()
    gs_log.fit(df_clf[CLF_14_FEATURES], df_clf["is_detractor"])
    log_time = time.time() - t0
    best_log_C = gs_log.best_params_["model__C"]
    best_log_ap = gs_log.best_score_
    print(f"    Optimal C: {best_log_C} | Best Val AP: {best_log_ap:.4f} (fit in {log_time:.1f}s)")
    tuning_summary.append({
        "task": "Classification (Detractor)",
        "model_family": "Logistic Regression",
        "best_hyperparameters": f"C={best_log_C}",
        "best_cv_score": best_log_ap,
        "scoring_metric": "average_precision",
        "tuning_time_s": log_time
    })

    # 2B. Decision Tree Classification Tuning
    print("  [2/3] Tuning Decision Tree Classifier (max_depth, min_samples_leaf)...")
    pipe_dtc = Pipeline([("preprocess", clf_preprocessor), ("model", DecisionTreeClassifier(random_state=seed))])
    param_grid_dtc = {
        "model__max_depth": [4, 6, 8, 10],
        "model__min_samples_leaf": [20, 50, 100, 200]
    }
    gs_dtc = GridSearchCV(
        pipe_dtc, param_grid_dtc, cv=clf_cv_splits,
        scoring="average_precision", n_jobs=-1, return_train_score=True
    )
    t0 = time.time()
    gs_dtc.fit(df_clf[CLF_14_FEATURES], df_clf["is_detractor"])
    dtc_time = time.time() - t0
    best_dtc_params = gs_dtc.best_params_
    best_dtc_ap = gs_dtc.best_score_
    print(f"    Optimal params: {best_dtc_params} | Best Val AP: {best_dtc_ap:.4f} (fit in {dtc_time:.1f}s)")
    tuning_summary.append({
        "task": "Classification (Detractor)",
        "model_family": "Decision Tree",
        "best_hyperparameters": str(best_dtc_params),
        "best_cv_score": best_dtc_ap,
        "scoring_metric": "average_precision",
        "tuning_time_s": dtc_time
    })

    # 2C. Random Forest Classification Tuning
    print("  [3/3] Tuning Random Forest Classifier (max_depth, min_samples_leaf)...")
    pipe_rfc = Pipeline([("preprocess", clf_preprocessor), ("model", RandomForestClassifier(n_estimators=50, random_state=seed, n_jobs=-1))])
    param_grid_rfc = {
        "model__max_depth": [6, 10, 14],
        "model__min_samples_leaf": [20, 50]
    }
    gs_rfc = GridSearchCV(
        pipe_rfc, param_grid_rfc, cv=clf_cv_splits,
        scoring="average_precision", n_jobs=-1, return_train_score=True
    )
    t0 = time.time()
    gs_rfc.fit(df_clf[CLF_14_FEATURES], df_clf["is_detractor"])
    rfc_time = time.time() - t0
    best_rfc_params = gs_rfc.best_params_
    best_rfc_ap = gs_rfc.best_score_
    print(f"    Optimal params: {best_rfc_params} | Best Val AP: {best_rfc_ap:.4f} (fit in {rfc_time:.1f}s)")
    tuning_summary.append({
        "task": "Classification (Detractor)",
        "model_family": "Random Forest",
        "best_hyperparameters": str(best_rfc_params),
        "best_cv_score": best_rfc_ap,
        "scoring_metric": "average_precision",
        "tuning_time_s": rfc_time
    })

    df_tuning = pd.DataFrame(tuning_summary)
    tuning_csv_path = OUTPUT_DIR / "phase4b_tuning_results.csv"
    df_tuning.to_csv(tuning_csv_path, index=False)
    print(f"\nSaved Phase 4B tuning results to: {tuning_csv_path}")

    # Return fitted grid search models for detailed fold evaluation
    return {
        "reg_ridge": gs_ridge.best_estimator_,
        "reg_dt": gs_dt.best_estimator_,
        "reg_rf": gs_rf.best_estimator_,
        "clf_log": gs_log.best_estimator_,
        "clf_dt": gs_dtc.best_estimator_,
        "clf_rf": gs_rfc.best_estimator_
    }, df_tuning


def generate_default_vs_tuned_comparison(df_reg, df_clf, tuned_models, seed=42):
    """Generate final comparison between Default Baseline and Tuned Models."""
    print("\n" + "=" * 80)
    print("GENERATING DEFAULT VS TUNED BENCHMARK COMPARISON")
    print("=" * 80)
    from sklearn.base import clone

    rows = []

    # Default Regression Pipelines (Untuned)
    reg_prep_raw = build_preprocessor(REG_13_FEATURES, apply_log1p_num=False)
    default_reg_models = {
        "Ridge Linear": Pipeline([("preprocess", reg_prep_raw), ("model", Ridge(alpha=1.0, random_state=seed))]),
        "Decision Tree": Pipeline([("preprocess", reg_prep_raw), ("model", DecisionTreeRegressor(max_depth=5, min_samples_leaf=100, random_state=seed))]),
        "Random Forest": Pipeline([("preprocess", reg_prep_raw), ("model", RandomForestRegressor(n_estimators=50, max_depth=10, min_samples_leaf=50, random_state=seed, n_jobs=-1))])
    }

    # Regression Comparison
    for model_name, default_pipe in default_reg_models.items():
        # 1. Default (Phase 3 Baseline)
        fold_metrics_def = []
        for fold, train_idx, val_idx in fold_indices(df_reg):
            train_df = df_reg.iloc[train_idx]
            val_df = df_reg.iloc[val_idx]
            est = clone(default_pipe)
            est.fit(train_df[REG_13_FEATURES], train_df["lead_days"])
            preds = np.clip(est.predict(val_df[REG_13_FEATURES]), 0.0, None)
            y_true = val_df["lead_days"].values
            fold_metrics_def.append({
                "mae": mean_absolute_error(y_true, preds),
                "rmse": np.sqrt(mean_squared_error(y_true, preds)),
                "r2": r2_score(y_true, preds)
            })
        df_def = pd.DataFrame(fold_metrics_def)
        rows.append({
            "task": "Regression (Lead Time)",
            "model_family": model_name,
            "status": "Default (Untuned Baseline)",
            "primary_metric": "MAE (Days)",
            "primary_mean": df_def["mae"].mean(),
            "primary_std": df_def["mae"].std(),
            "secondary_metric": "RMSE (Days)",
            "secondary_mean": df_def["rmse"].mean(),
            "secondary_std": df_def["rmse"].std(),
            "r2_mean": df_def["r2"].mean(),
            "r2_std": df_def["r2"].std()
        })

        # 2. Tuned Model
        tuned_key = "reg_ridge" if "Ridge" in model_name else ("reg_dt" if "Tree" in model_name else "reg_rf")
        tuned_est = tuned_models[tuned_key]
        fold_metrics_tuned = []
        for fold, train_idx, val_idx in fold_indices(df_reg):
            train_df = df_reg.iloc[train_idx]
            val_df = df_reg.iloc[val_idx]
            est = clone(tuned_est)
            est.fit(train_df[REG_13_FEATURES], train_df["lead_days"])
            preds = np.clip(est.predict(val_df[REG_13_FEATURES]), 0.0, None)
            y_true = val_df["lead_days"].values
            fold_metrics_tuned.append({
                "mae": mean_absolute_error(y_true, preds),
                "rmse": np.sqrt(mean_squared_error(y_true, preds)),
                "r2": r2_score(y_true, preds)
            })
        df_tun = pd.DataFrame(fold_metrics_tuned)
        rows.append({
            "task": "Regression (Lead Time)",
            "model_family": model_name,
            "status": "Tuned (Phase 4B + Log1p)",
            "primary_metric": "MAE (Days)",
            "primary_mean": df_tun["mae"].mean(),
            "primary_std": df_tun["mae"].std(),
            "secondary_metric": "RMSE (Days)",
            "secondary_mean": df_tun["rmse"].mean(),
            "secondary_std": df_tun["rmse"].std(),
            "r2_mean": df_tun["r2"].mean(),
            "r2_std": df_tun["r2"].std()
        })

    # Default Classification Pipelines (Untuned)
    clf_prep_raw = build_preprocessor(CLF_14_FEATURES, apply_log1p_num=False)
    default_clf_models = {
        "Logistic Regression": Pipeline([("preprocess", clf_prep_raw), ("model", LogisticRegression(C=0.01, solver="lbfgs", max_iter=2000, random_state=seed))]),
        "Decision Tree": Pipeline([("preprocess", clf_prep_raw), ("model", DecisionTreeClassifier(max_depth=5, min_samples_leaf=100, random_state=seed))]),
        "Random Forest": Pipeline([("preprocess", clf_prep_raw), ("model", RandomForestClassifier(n_estimators=50, max_depth=10, min_samples_leaf=50, random_state=seed, n_jobs=-1))])
    }

    # Classification Comparison
    for model_name, default_pipe in default_clf_models.items():
        # 1. Default (Phase 3 Baseline)
        fold_metrics_def = []
        for fold, train_idx, val_idx in fold_indices(df_clf):
            train_df = df_clf.iloc[train_idx]
            val_df = df_clf.iloc[val_idx]
            est = clone(default_pipe)
            est.fit(train_df[CLF_14_FEATURES], train_df["is_detractor"])
            probs = est.predict_proba(val_df[CLF_14_FEATURES])[:, 1]
            y_true = val_df["is_detractor"].values
            fold_metrics_def.append({
                "ap": average_precision_score(y_true, probs),
                "roc_auc": roc_auc_score(y_true, probs),
                "brier": brier_score_loss(y_true, probs)
            })
        df_def = pd.DataFrame(fold_metrics_def)
        rows.append({
            "task": "Classification (Detractor)",
            "model_family": model_name,
            "status": "Default (Untuned Baseline)",
            "primary_metric": "Average Precision (AP)",
            "primary_mean": df_def["ap"].mean(),
            "primary_std": df_def["ap"].std(),
            "secondary_metric": "ROC-AUC",
            "secondary_mean": df_def["roc_auc"].mean(),
            "secondary_std": df_def["roc_auc"].std(),
            "brier_mean": df_def["brier"].mean(),
            "brier_std": df_def["brier"].std()
        })

        # 2. Tuned Model
        tuned_key = "clf_log" if "Logistic" in model_name else ("clf_dt" if "Tree" in model_name else "clf_rf")
        tuned_est = tuned_models[tuned_key]
        fold_metrics_tuned = []
        for fold, train_idx, val_idx in fold_indices(df_clf):
            train_df = df_clf.iloc[train_idx]
            val_df = df_clf.iloc[val_idx]
            est = clone(tuned_est)
            est.fit(train_df[CLF_14_FEATURES], train_df["is_detractor"])
            probs = est.predict_proba(val_df[CLF_14_FEATURES])[:, 1]
            y_true = val_df["is_detractor"].values
            fold_metrics_tuned.append({
                "ap": average_precision_score(y_true, probs),
                "roc_auc": roc_auc_score(y_true, probs),
                "brier": brier_score_loss(y_true, probs)
            })
        df_tun = pd.DataFrame(fold_metrics_tuned)
        rows.append({
            "task": "Classification (Detractor)",
            "model_family": model_name,
            "status": "Tuned (Phase 4B + Log1p)",
            "primary_metric": "Average Precision (AP)",
            "primary_mean": df_tun["ap"].mean(),
            "primary_std": df_tun["ap"].std(),
            "secondary_metric": "ROC-AUC",
            "secondary_mean": df_tun["roc_auc"].mean(),
            "secondary_std": df_tun["roc_auc"].std(),
            "brier_mean": df_tun["brier"].mean(),
            "brier_std": df_tun["brier"].std()
        })

    df_comp = pd.DataFrame(rows)
    comp_csv_path = OUTPUT_DIR / "phase4_default_vs_tuned_comparison.csv"
    df_comp.to_csv(comp_csv_path, index=False)
    print(f"\nSaved Default vs Tuned comparison to: {comp_csv_path}")

    # Plot Grouped Default vs Tuned Comparison
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6), dpi=150)

    # 1. Regression MAE Grouped
    reg_df = df_comp[df_comp["task"].str.startswith("Regression")]
    models = ["Ridge Linear", "Decision Tree", "Random Forest"]
    x = np.arange(len(models))
    width = 0.35

    def_mae = [reg_df[(reg_df["model_family"] == m) & (reg_df["status"].str.startswith("Default"))]["primary_mean"].values[0] for m in models]
    def_std = [reg_df[(reg_df["model_family"] == m) & (reg_df["status"].str.startswith("Default"))]["primary_std"].values[0] for m in models]
    tun_mae = [reg_df[(reg_df["model_family"] == m) & (reg_df["status"].str.startswith("Tuned"))]["primary_mean"].values[0] for m in models]
    tun_std = [reg_df[(reg_df["model_family"] == m) & (reg_df["status"].str.startswith("Tuned"))]["primary_std"].values[0] for m in models]

    b1 = ax1.bar(x - width/2, def_mae, width, yerr=def_std, label="Default (Untuned)", color="#95a5a6", edgecolor="black", capsize=4)
    b2 = ax1.bar(x + width/2, tun_mae, width, yerr=tun_std, label="Tuned (Phase 4B + Log1p)", color="#2980b9", edgecolor="black", capsize=4)
    ax1.set_xticks(x)
    ax1.set_xticklabels(models, fontweight="bold", fontsize=10)
    ax1.set_ylabel("Validation MAE in Days (Lower is Better)", fontweight="bold", fontsize=11)
    ax1.set_title("Regression: Impact of Pre-scaling & Hyperparameter Tuning", fontweight="bold", fontsize=12)
    ax1.set_ylim(4.5, 5.6)
    ax1.legend(frameon=True)
    for bar in b1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.02, f"{yval:.2f}d", ha="center", va="bottom", fontsize=9)
    for bar in b2:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 0.02, f"{yval:.2f}d", ha="center", va="bottom", fontsize=9, fontweight="bold")

    # 2. Classification AP Grouped
    clf_df = df_comp[df_comp["task"].str.startswith("Classification")]
    clf_models = ["Logistic Regression", "Decision Tree", "Random Forest"]
    x2 = np.arange(len(clf_models))

    def_ap = [clf_df[(clf_df["model_family"] == m) & (clf_df["status"].str.startswith("Default"))]["primary_mean"].values[0] for m in clf_models]
    def_ap_std = [clf_df[(clf_df["model_family"] == m) & (clf_df["status"].str.startswith("Default"))]["primary_std"].values[0] for m in clf_models]
    tun_ap = [clf_df[(clf_df["model_family"] == m) & (clf_df["status"].str.startswith("Tuned"))]["primary_mean"].values[0] for m in clf_models]
    tun_ap_std = [clf_df[(clf_df["model_family"] == m) & (clf_df["status"].str.startswith("Tuned"))]["primary_std"].values[0] for m in clf_models]

    b3 = ax2.bar(x2 - width/2, def_ap, width, yerr=def_ap_std, label="Default (Untuned)", color="#95a5a6", edgecolor="black", capsize=4)
    b4 = ax2.bar(x2 + width/2, tun_ap, width, yerr=tun_ap_std, label="Tuned (Phase 4B + Log1p)", color="#27ae60", edgecolor="black", capsize=4)
    ax2.set_xticks(x2)
    ax2.set_xticklabels(clf_models, fontweight="bold", fontsize=10)
    ax2.set_ylabel("Validation Average Precision (Higher is Better)", fontweight="bold", fontsize=11)
    ax2.set_title("Classification: Impact of Pre-scaling & Hyperparameter Tuning", fontweight="bold", fontsize=12)
    ax2.set_ylim(0.24, 0.32)
    ax2.legend(frameon=True)
    for bar in b3:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.0015, f"{yval:.4f}", ha="center", va="bottom", fontsize=9)
    for bar in b4:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.0015, f"{yval:.4f}", ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.tight_layout()
    plot_path = OUTPUT_DIR / "phase4_default_vs_tuned_comparison.png"
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f"Saved Phase 4 comparison plot to: {plot_path}")


def main():
    print("=" * 80)
    print("EXPERIMENT 3 — PHASE 4: TRANSFORMS & GRIDSEARCHCV MODEL TUNING")
    print("=" * 80)

    f, cv, hashes = load_development()
    df_reg = task_rows(f, cv, "regression").copy()
    df_clf = task_rows(f, cv, "classification").copy()
    print(f"Loaded {len(df_reg):,} regression orders and {len(df_clf):,} classification orders.")

    # 1. Run Phase 4A: Pre-scaling and Target log-transform ablation
    df_ablation = run_phase4a_transforms_ablation(df_reg, df_clf)

    # 2. Run Phase 4B: Full GridSearchCV Hyperparameter Tuning
    tuned_models, df_tuning = run_phase4b_gridsearch_tuning(df_reg, df_clf)

    # 3. Generate Default vs. Tuned Benchmark Comparison
    generate_default_vs_tuned_comparison(df_reg, df_clf, tuned_models)

    print("\n" + "=" * 80)
    print("PHASE 4 TRANSFORMS & TUNING COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()
