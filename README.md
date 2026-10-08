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
│   ├── 01_data_cleaning.ipynb                    # Stage 1: raw -> preprocessed (types, zip codes, GPS dedup)
│   ├── 02_dashboard_preprocessing.ipynb          # Stage 2: preprocessed -> business/dashboard (filtering & metrics)
│   ├── 03_business_dashboard_data_preprocessing.ipynb # Stage 3: data preview, table consolidation & KPI validation
│   ├── 04_ml_feature_engineering.ipynb           # Deterministic ML features and split manifests
│   ├── 05_model_training_and_evaluation.ipynb   # Task evidence and development baselines
│   ├── 06_model_tuning_and_selection.ipynb      # Bounded development selection and policy
│   ├── 07_final_evaluation_and_scoring.ipynb    # Historical frozen holdout results and no-fit scoring
│   └── 08_refined_models_and_evidence.ipynb    # Current refined-model evidence and scoring
│
├── deployment/               # Official directory for the dashboard application
│   └── app.py                # Executive Operations Master Dashboard (Streamlit application)
│
├── src/                      # Reusable Python source code and shared utilities
│   ├── common/               # Shared schemas, loaders, and utilities
│   ├── features/             # Feature engineering encoders and transformers
│   └── models/               # Model training, hyperparameter tuning, and evaluation
│
├── experiments/              # Frozen trial protocols, runners and reproduction instructions
│   ├── refinement_cycle1/    # Whole-cycle orchestration and initial diagnostics
│   └── feature_selection_v3/ # Feature blocks, combinations and model comparisons
│
├── artifacts/                # Serialized model pipelines and evaluation metrics
│   ├── models/               # .joblib / .pkl model artifacts
│   └── metrics/              # Evaluation reports and confusion matrices
│
├── app.py                    # Root entrypoint launcher (delegates execution to deployment/app.py)
├── requirements.txt          # Python dependencies for local run and Streamlit Cloud
└── README.md
```

---

## 🔄 Data Architecture & Lineage

The data is organized into three clean layers under `data/`:

* **Dashboard Track**: $\text{data/raw/} \xrightarrow{\textbf{Stage 1}} \text{data/preprocessed/} \xrightarrow{\textbf{Stage 2}} \text{data/business/dashboard/} \xrightarrow{\textbf{Stage 3}} \text{smartcommerce\_consolidated.csv}$
* **Machine Learning Track**: $\text{data/raw/} \xrightarrow{\textbf{Stage 1}} \text{data/preprocessed/} \xrightarrow{\textbf{Stage 4}} \text{data/business/ml/orders\_ml\_features.csv} \xrightarrow{\textbf{Models}} \text{artifacts/models/}$

| Layer | Folder Path | Purpose & Rules |
| :--- | :--- | :--- |
| **1. Raw** | `data/raw/` | Exact, immutable copies of the 9 original Olist CSV files downloaded from Canvas. Never edit or overwrite manually. |
| **2. Preprocessed** | `data/preprocessed/` | **Lossless baseline**: Parses ISO datetimes (`pd.to_datetime`), preserves 5-digit zip codes as strings (`01037`), checks categorical enums, and removes 261,831 exact duplicate GPS rows. Keeps 100% of transaction rows across all other tables. |
| **3A. Business (Dashboard)** | `data/business/dashboard/` | **Dashboard-ready tables**: Applies business rules for executive presentation: removes timestamp sequence errors, filters orders to the stable operating period (**2017-01 to 2018-08**), collapses multi-reviews to lowest score, and pre-calculates `delivery_days`, `is_on_time`, and `item_revenue`. Houses `smartcommerce_consolidated.csv`. |
| **3B. Business (ML)** | `data/business/ml/` | **Predictive modelling features & targets**: 27 checkout-proxy predictors plus separate outcomes/eligibility in `orders_ml_features.csv`. Payment/catalogue/seller-allocation availability is an explicit snapshot assumption, not proven event-time access. Models exclude post-outcome columns and dashboard date clipping; splits group `customer_unique_id`. |

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

## 📓 How to Reproduce the Data Pipeline

To regenerate all datasets from scratch starting from the raw CSVs, run the notebooks in order:

1. Open and run **`notebooks/01_data_cleaning.ipynb`**:
   * Reads from: `data/raw/`
   * Writes to: `data/preprocessed/`
2. Open and run **`notebooks/02_dashboard_preprocessing.ipynb`**:
   * Reads from: `data/preprocessed/`
   * Writes to: `data/business/dashboard/`
3. Open and run **`notebooks/03_business_dashboard_data_preprocessing.ipynb`**:
   * Reads from: `data/business/dashboard/`
   * Performs data validation and generates `data/business/dashboard/smartcommerce_consolidated.csv`.

All notebooks resolve project paths dynamically, meaning they can be executed from within VS Code, JupyterLab, or the command line without modifying directory paths.

## Milestone 2 modelling and review

Current applied configuration: `refinement-selected-v3`, part of **one refinement
cycle with successive phases**. Delivery uses a depth-5 decision tree with 13 raw
predictors; recorded 1–2-star review risk uses unweighted L2 logistic regression
(`C=0.01`) with 14. The reusable deterministic base still contains all 27 predictors.
Neither model is deployment-certified; later-period evaluation is previously
inspected diagnostic evidence, not an untouched new test. The cost ratio is assumed.

| Phase | Evidence/code | Meaning |
| --- | --- | --- |
| Initial conservative reference | `experiments/refinement_cycle1/initial_reference/`, `refinement_core*.py`; compressed evidence | 11-input chronology, review-driven diagnostics and initial terminal assessment |
| Incremental feature tests | `experiments/feature_selection_v3/{protocol,combination_protocol}.json` and runners; `feature-selection-v3-screen`, `-combinations` results | 50 standalone-block +50 combination fits; all unsuccessful cases retained |
| Model-family gate | `model_protocol.json`, `model_runner.py`, `compare_models.py`; `feature-selection-v3-model-gate` results | 50 simple-baseline fits +15 reused results; simpler regression tree selected |
| Applied final state | `src/models/configs/refinement_selected_v3.json`, modules below; `refinement-selected-v3` results | 10 selected-fold confirmation refits +9 final/reference fits; frozen policy and one final diagnostic pass |

The expansion was introduced after reviewing the initial version; the entire
cycle was **not** preplanned. Each subsequent catalogue was frozen before its own
fits. There are 432 predictive fits in this logical cycle (263+100+50+19), and
two terminal assessments across its initial and final versions. Neither later
assessment is claimed to restore test independence. Do not compare chronology
scores directly with the historical random-group 80/20 scores.

### Reproduce the applied models (no private documents required)

Use Python 3.13.9 and the pinned dependencies. Run commands from the repo root:

```bash
python -m pip install -r requirements.txt -r src/models/requirements-stage3.txt
python -m unittest src.models.tests.test_refinement_selected
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MPLCONFIGDIR=artifacts/generated/mpl-cache
python -m src.models.refinement_selected build --output artifacts/metrics/refinement-selected-v3-check
python -m src.models.refinement_selected_verify --run artifacts/metrics/refinement-selected-v3-check
python -m src.models.refinement_diagnostics --run artifacts/metrics/refinement-selected-v3-check
```

Choose a **new** output name each time; never delete or overwrite accepted outputs
to make a command succeed. Build uses the supplied `data/business/ml/*.csv/json`
and `data/preprocessed/*.csv`; it does not require teaching/review/report folders,
internet downloads or experiment model files. It reconstructs customer-purged
chronological folds and mature labels, confirms frozen development scores, and
writes complete trusted bundles under `bundles/{task}/{role}`. References are fitted
on the same task-specific inputs, not the historical 27-field interface. Recorded
hashes and environment identify inputs; exact serialized bytes are not promised
across platforms. Missing input/version/hash mismatches must stop, not be patched
by weakening checks. This path reproduces fixed choices; it does not rerun selection.

Terminal evaluation is a separate explicit command, **after verification**:

```bash
python -m src.models.refinement_selected_terminal --run artifacts/metrics/refinement-selected-v3-check --acknowledge-previously-inspected-terminal
python -m src.models.refinement_selected_terminal_verify --run artifacts/metrics/refinement-selected-v3-check
```

It excludes the original20% holdout, scores the previously inspected chronological
terminal once per new run, and refuses a reserved output even after a failure.
Do not change features/models/policy from these outcomes. It never fits. Verify
recomputes saved metrics and eligibility; bootstrap intervals are conditional
sampling diagnostics, not corrections for prior exposure or time dependence.

### No-fit batch scoring

```bash
python -m src.models.refinement_selected score --bundle artifacts/metrics/refinement-selected-v3/bundles/regression/selected --input YOUR_BATCH.csv --output NEW_PREDICTIONS.csv
```

Use `classification/selected` for review risk. Each batch must have `order_id`
and exactly that bundle's `feature_schema.json` predictor list, in original units.
Missing columns, extra outcomes and duplicate/blank IDs fail; null cells are allowed.
Load only trusted joblib files: checksum verification detects corruption, not a
malicious pickle. Scoring never fits. Models are retrospective placement proxies,
not a guarantee the features existed in a live checkout system.

### Historical trials and reports

Notebooks04–07 and `stage3-*`, `stage4-*`, `stage5-*` artifacts are the historical
27-feature grouped-random baseline, not the current model. Notebook08 is the
current command entry point. The [refinement reproduction guide](experiments/refinement_cycle1/README.md)
distinguishes all trial phases from the applied state. It documents lossless
accepted-evidence inspection, the full 432-fit reconstruction, and report checks.

```bash
python -m experiments.refinement_cycle1.evidence unpack --output artifacts/generated/accepted-evidence
python -m experiments.refinement_cycle1.report_evidence --run artifacts/generated/accepted-evidence/final --verify
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m experiments.refinement_cycle1.reproduce --output artifacts/generated/full-check-01 --acknowledge-previously-inspected-terminal
```

No private report, review, tutorial or course folder is required. All unsuccessful
trial outcomes remain in the compressed archives under
`artifacts/metrics/refinement-cycle1-evidence/`; intermediate models are regenerated.
Final tables/charts and selected bundles are directly visible under
`artifacts/metrics/refinement-selected-v3/`. The report is shared separately;
`report_evidence.json` maps sections and numerical claims to committed evidence.
Human interpretation and report-layout review remain necessary.

---

## ⚠️ Important Course Guidelines & Data Gotchas

* **`customer_id` vs. `customer_unique_id`**:
  * `customer_id`: a 1-time session key generated per transaction.
  * `customer_unique_id`: the persistent identifier of the actual human customer.
  * *Always use `customer_unique_id` for repeat-purchase analysis, customer retention, or customer-level features.*
* **Data Leakage Warnings (Literature: Kapoor & Narayanan, 2023)**:
  * Columns like `order_delivered_customer_date`, `delivery_days`, and `is_on_time` are **outcomes**, not predictors.
  * They are included in dashboard tables for historical reporting. Current Phase 2 models use reconstructed order-placement inputs with explicit snapshot-availability assumptions; outcomes are never predictors. A live system would need to establish actual event-time availability.
