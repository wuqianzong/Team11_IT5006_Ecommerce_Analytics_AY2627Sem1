# Notebooks Directory Guide — IT5006 Group 11

This directory contains the complete sequence of Jupyter notebooks documenting the data processing, historical modeling baselines, and applied refinement cycles for the Olist E-Commerce dataset.

---

## 📚 Notebook Directory Roadmap

| # | Notebook Name | Stage / Role | Description & Inputs/Outputs |
| :--- | :--- | :--- | :--- |
| **01** | [`01_data_cleaning.ipynb`](01_data_cleaning.ipynb) | **Stage 1 (Data Cleaning)** | Reads `data/raw/`, cleans zip codes, parses datetimes, removes duplicate GPS entries, and saves lossless typed CSVs to `data/preprocessed/`. |
| **02** | [`02_dashboard_preprocessing.ipynb`](02_dashboard_preprocessing.ipynb) | **Stage 2 (Dashboard Prep)** | Filters out timestamp sequence anomalies, restricts to the 2017–2018 operating period, collapses multi-reviews, and computes initial dashboard metrics. |
| **03** | [`03_business_dashboard_data_preprocessing.ipynb`](03_business_dashboard_data_preprocessing.ipynb) | **Stage 3 (Consolidation)** | Consolidates dashboard tables into `smartcommerce_consolidated.csv` and validates executive KPIs. |
| **04** | [`04_ml_feature_engineering.ipynb`](04_ml_feature_engineering.ipynb) | **Stage 4 (ML Features)** | Generates deterministic 27-feature checkout-proxy dataset (`orders_ml_features.csv`) and manifests. |
| **05** | [`05_model_training_and_evaluation.ipynb`](05_model_training_and_evaluation.ipynb) | **Stage 5A (Historical Baseline)** | Historical baseline models evaluated using 27 features and random-grouped 80/20 train/test splitting. |
| **06** | [`06_model_tuning_and_selection.ipynb`](06_model_tuning_and_selection.ipynb) | **Stage 5B (Historical Selection)** | Hyperparameter search and bounded selection under the random-group protocol. |
| **07** | [`07_final_evaluation_and_scoring.ipynb`](07_final_evaluation_and_scoring.ipynb) | **Stage 5C (Historical Final Holdout)** | Frozen evaluation on the random holdout partition. |
| **08** | [`08_refined_models_and_evidence.ipynb`](08_refined_models_and_evidence.ipynb) | **Refinement Cycle 1 (`v3`)** | Replaced flawed random-group splits with **leak-free chronological forward-chaining evaluation** (customer purges + label maturity gating). Evaluates Decision Tree ($d=5$) and Logistic Regression ($C=0.01$) over pruned 13/14 features. |
| **09** | [`09_refinement_cycle2_migration.ipynb`](09_refinement_cycle2_migration.ipynb) | **Refinement Cycle 2 (`v4`, Champion)** | **Current Production Champion**: Migrates winning Experiment 3 architectures: Non-linear Random Forests ($N=50, d=14$), Target & Input Log1p transformations, and cost-calibrated threshold policy ($\tau^* = 0.17$). Slashes holdout MAE by $32.9\%$ and minimizes total business cost. |

---

## 🎯 Quick Guide for Reviewers & Instructors

* **If you want to inspect the current production models and live inference immediately**:
  * Open and run **[`09_refinement_cycle2_migration.ipynb`](09_refinement_cycle2_migration.ipynb)**. It directly loads the serialized bundles from `artifacts/metrics/refinement-selected-v4/` and demonstrates zero-fit batch scoring and head-to-head comparison against Cycle 1.
* **If you want to understand the temporal leakage discovery**:
  * Compare **`05_model_training_and_evaluation.ipynb`** (which used random `GroupKFold` and suffered temporal inversion) against **`08_refined_models_and_evidence.ipynb`** (which introduced chronological expansion splits with customer purges).
* **If you want to view the experimental research behind the champion**:
  * Consult [`experiments/experiment_3/SUMMARY_REPORT.md`](../experiments/experiment_3/SUMMARY_REPORT.md).
