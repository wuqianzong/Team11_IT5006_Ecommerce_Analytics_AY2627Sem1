# SmartCommerce — IT5006 Group 11 (Olist E-Commerce Analytics)

Interactive Streamlit Executive Dashboard and Data Analytics Pipeline for the **Olist Brazilian E-Commerce** dataset (2016–2018), built for **IT5006: Fundamentals of Data Analytics (AY 2026/27 Semester 1)**.

---

## 📁 Repository Structure

The repository strictly follows the official course specification (**Page 7 of the Project Description**):

```text
.
├── data/
│   ├── raw/                  # 9 original, untouched Olist CSV files
│   ├── preprocessed/         # 9 cleaned & typed baseline CSVs (lossless type standardization)
│   ├── reference/geography/  # Pinned IBGE boundary and provenance for distance features
│   └── business/
│       ├── dashboard/        # 9 processed CSVs + smartcommerce_consolidated.csv (ready for Streamlit)
│       └── ml/               # Checkout-proxy features, targets, frozen splits and contracts
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb                         # Stage 1: raw -> preprocessed (types, zip codes, GPS dedup)
│   ├── 02_dashboard_preprocessing.ipynb               # Stage 2: preprocessed -> business/dashboard (filtering & metrics)
│   ├── 03_business_dashboard_data_preprocessing.ipynb # Stage 3: data preview, table consolidation & KPI validation
│   ├── 04_ml_feature_engineering.ipynb                # Stage 4: deterministic ML features and split manifests
│   ├── 05_model_training_and_evaluation.ipynb        # Historical Baseline (Stage 5A): 27-feature random-group fits
│   ├── 06_model_tuning_and_selection.ipynb           # Historical Baseline (Stage 5B): bounded development selection
│   ├── 07_final_evaluation_and_scoring.ipynb         # Historical Baseline (Stage 5C): frozen random holdout scoring
│   ├── 08_refined_models_and_evidence.ipynb         # Refinement Cycle 1: leak-free chronological split (v3: tree/logistic)
│   └── 09_refinement_cycle2_migration.ipynb          # Refinement Cycle 2: current champion models (v4: tuned RF + log1p)
│
├── deployment/               # Official directory for the dashboard application
│   └── app.py                # Executive Operations Master Dashboard (Streamlit application)
│
├── src/                      # Reusable Python source code and shared utilities
│   ├── common/               # Shared schemas, loaders, and utilities
│   ├── features/             # Feature engineering encoders and transformers
│   └── models/               # Model training, hyperparameter tuning, and evaluation
│
├── experiments/              # Systematic experimentation, ablation studies, and trial protocols
│   ├── refinement_cycle1/    # Whole-cycle orchestration and initial diagnostics
│   ├── feature_selection_v3/ # Feature blocks, combinations and model comparisons
│   └── experiment_3/         # Comprehensive 6-phase refinement study (reproducible champion research)
│
├── artifacts/                # Serialized model pipelines and evaluation metrics
│   ├── models/               # .joblib / .pkl model artifacts
│   └── metrics/              # Evaluation reports, confusion matrices, and benchmark bundles
│       ├── refinement-selected-v3/  # Refinement Cycle 1 accepted bundles & evidence
│       └── refinement-selected-v4/  # Refinement Cycle 2 (Current Champion) bundles & evidence
│
├── app.py                    # Root entrypoint launcher (delegates execution to deployment/app.py)
├── requirements.txt          # Python dependencies for local run and Streamlit Cloud
└── README.md
```

---

## 🔄 Data Architecture & Lineage

The data is organized into three clean layers under `data/`:

* **Dashboard Track**: $\text{data/raw/} \xrightarrow{\textbf{Stage 1}} \text{data/preprocessed/} \xrightarrow{\textbf{Stage 2}} \text{data/business/dashboard/} \xrightarrow{\textbf{Stage 3}} \text{smartcommerce\_consolidated.csv}$
* **Machine Learning Track**: $\text{data/raw/} \xrightarrow{\textbf{Stage 1}} \text{data/preprocessed/} \xrightarrow{\textbf{Stage 4}} \text{data/business/ml/orders\_ml\_features.csv} \xrightarrow{\textbf{Models}} \text{artifacts/metrics/}$

| Layer | Folder Path | Purpose & Rules |
| :--- | :--- | :--- |
| **1. Raw** | `data/raw/` | Exact, immutable copies of the 9 original Olist CSV files downloaded from Canvas. Never edit or overwrite manually. |
| **2. Preprocessed** | `data/preprocessed/` | **Lossless baseline**: Parses ISO datetimes (`pd.to_datetime`), preserves 5-digit zip codes as strings (`01037`), checks categorical enums, and removes 261,831 exact duplicate GPS rows. Keeps 100% of transaction rows across all other tables. |
| **3A. Business (Dashboard)** | `data/business/dashboard/` | **Dashboard-ready tables**: Applies business rules for executive presentation: removes timestamp sequence errors, filters orders to the stable operating period (**2017-01 to 2018-08**), collapses multi-reviews to lowest score, and pre-calculates `delivery_days`, `is_on_time`, and `item_revenue`. Houses `smartcommerce_consolidated.csv`. |
| **3B. Business (ML)** | `data/business/ml/` | **Predictive modelling features & targets**: 27 checkout-proxy predictors plus separate outcomes/eligibility in `orders_ml_features.csv`. All features are strictly restricted to information available at the point of checkout. |

---

## 🚀 How to Run the Dashboard

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch Streamlit
You can run the dashboard from either the root launcher or directly from `deployment/`:
```bash
streamlit run app.py
# or
streamlit run deployment/app.py
```
Open the printed local URL (usually `http://localhost:8501`) in your browser.

> [!TIP]
> The dashboard application includes an automatic in-memory fallback. If `smartcommerce_consolidated.csv` is not pre-generated on disk, the app dynamically constructs it from the base dashboard CSVs in `data/business/dashboard/` on first load and caches it in memory.

---

## Milestone 2 reproduction and report evidence

Start here to verify the submitted Milestone 2 results. The submitted report is
unchanged. Repository documentation below clarifies its reproduction instructions
and records evidence corrections separately.

### 1. Install the frozen modelling environment

Use a separate environment for the model bundles. The original build used Python
3.10.19; its five numerical/model package versions are recorded in
`artifacts/metrics/refinement-selected-v4/build_freeze.json`.

```bash
python3 -m venv .venv-milestone2
source .venv-milestone2/bin/activate
python -m pip install -r requirements-milestone2.txt
```

Python 3.13.5 with these same numerical versions was also checked for no-fit
reproduction. This is a model-verification environment; dashboard dependencies
remain in `requirements.txt`, whose numerical pins now agree with the frozen run.

### 2. Run the command printed in the submitted report

```bash
python -m src.models.refinement_selected_v4_terminal
```

The bare command now verifies the frozen evidence. It checks bundle and dataset
checksums, scores all nine saved model/reference bundles, checks both selected
models against published per-order predictions, compares all terminal metrics,
79 subgroup rows and the train–validate–test matrix, and checks the recorded OOF
policy costs. It performs **no model fitting or threshold selection**.

Outputs go to a new directory under `artifacts/reproduction/`, never to the
published evidence directory. Specify another unused directory if desired:

```bash
python -m src.models.refinement_selected_v4_terminal --output /tmp/milestone2-check
```

A successful run prints `PASS` and writes `verification.json`,
`metric_comparison.csv`, predictions, diagnostic charts and cohort statistics.
The holdout has already been inspected: this is reproduction of the reported
results, not a new independent test. Frozen threshold 0.17 is a deployment policy;
the recorded chronological OOF empirical threshold is about 0.1822.

An archived receipt from the checked reproduction is in
[`artifacts/metrics/milestone2-reproduction-receipt/`](artifacts/metrics/milestone2-reproduction-receipt/).

### 3. Inspect the executable notebook

Open [`notebooks/09_refinement_cycle2_migration.ipynb`](notebooks/09_refinement_cycle2_migration.ipynb).
Select the Python interpreter from `.venv-milestone2` as its kernel. If using a
separate Jupyter installation, register that environment first:

```bash
python -m ipykernel install --user --name it5006-milestone2 --display-name "IT5006 Milestone 2"
```

It shows the report's nine-feature screening, 11/12-feature tuning, chronological
confirmation, frozen terminal verification and example scoring. It explicitly
inspects existing fits rather than retraining. The optional training recipe is
listed below. Notebook 08 is an earlier architecture, **not** the report's
nine-feature Cycle 1 benchmark.

### Evidence for the two cycles

The report compares **two families**: linear (Ridge/logistic) and tree-based
(single tree/random forest), with separate dummy references.

| Evidence | Protocol and source |
| --- | --- |
| Cycle 1, 9-feature comparison | Grouped CV: `artifacts/metrics/experiment-3/feature_importance/feature_dimension_score_comparison.csv` |
| Cycle 2 candidate tuning, Table C.2 | Grouped CV: `artifacts/metrics/experiment-3/transforms_and_tuning/phase4b_tuning_results.csv` |
| Default versus tuned candidates, Figure C.1 | `artifacts/metrics/experiment-3/transforms_and_tuning/phase4_default_vs_tuned_comparison.csv` |
| Selected-model chronological confirmation, Table C.1 | `artifacts/metrics/refinement-selected-v4/development_fold_metrics.csv` |
| Common terminal comparison, Table E.2 | `artifacts/metrics/refinement-selected-v4/terminal/metrics.csv`; all saved reference bundles are included |
| Train–validate–test, Tables E.1/F.5 | `artifacts/metrics/refinement-selected-v4/terminal/train_val_test_comparison.csv` |
| Permutation importance, Figures D.1/D.2 | Published tree-regressor and logistic-classifier CSV/PNG files in the feature-importance directory; these do not measure final-forest importance |
| Frozen policy and recorded OOF cost | `frozen_decision_policy.json` and `classification_development_oof.csv` in the v4 directory |
| Cohort and target statistics, Tables A.1/F.1 | `artifacts/metrics/report-evidence-exp3/`; both final training-ID files are included |

The selected terminal regression scores are MAE **3.7185 days**, RMSE **5.3085**
and R² **0.1871**. Classification AP is **0.1823**, ROC-AUC **0.5864** and Brier
**0.0949** on 15,769 orders. Frozen threshold 0.17 yields TP=456, FP=1,859,
FN=1,251, precision=19.70%, recall=26.71%, F1=0.2268 and illustrative loss=8,114
for FN=5, FP=1. The regression cohort has 15,615 orders.

Grouped screening scores and chronological confirmation scores use different
protocols. They are not a matched temporal estimate of improvement between the
two cycles. The forest reference and selected classifier have identical ranking
scores; applying the frozen policy changes decisions and illustrative loss, not AP.
Condition number 70.77/rank 71 applies to the encoded **nine-feature core**, not
all expanded-model matrices. The 27-feature matrix is singular.

### 4. Verify descriptive report statistics without loading models

Use an unused output directory to preserve the published audit files:

```bash
python experiments/experiment_3/verify_report_evidence.py --output /tmp/milestone2-statistics
```

This reproduces raw development target moments, Table F.1 statistics/drift and the
zero-item decomposition. See the separate evidence notes for the submitted report's
basket-count and classification-prevalence corrections:
[`docs/milestone2_reproduction_notes.md`](docs/milestone2_reproduction_notes.md).

### 5. Score a historical checkout example without fitting

```bash
python -m src.models.refinement_selected_v4 score \
  --bundle artifacts/metrics/refinement-selected-v4/bundles/regression/selected \
  --input examples/milestone2_checkout_orders.csv \
  --output /tmp/milestone2-lead-days.csv

python -m src.models.refinement_selected_v4 score \
  --bundle artifacts/metrics/refinement-selected-v4/bundles/classification/selected \
  --input examples/milestone2_checkout_orders.csv \
  --output /tmp/milestone2-detractor-risk.csv
```

The example includes predictor columns only, sampled from the saved development
data. It demonstrates scoring historical records, not a live integration.
Existing scoring output files are refused.

### Optional: rebuild the frozen model recipe

This retrains the recorded configuration and can take considerably longer than
verification. It performs no new hyperparameter search, recomputes OOF diagnostics
and retains deployment threshold 0.17. It does not alter the submitted bundles.

```bash
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
python -m src.models.refinement_selected_v4 build --output artifacts/reproduction/v4-rebuilt
python -m src.models.refinement_selected_v4_terminal \
  --run artifacts/reproduction/v4-rebuilt --acknowledge-previously-inspected-terminal
```

For research-stage grouped comparisons and tuning, see
[`experiments/experiment_3/README.md`](experiments/experiment_3/README.md).
Their outputs are exploratory screening evidence, separate from the chronological
confirmation and final terminal metrics. No new training is needed to verify the
submitted scores.
