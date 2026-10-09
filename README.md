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

## 🧭 Machine Learning Modeling: Three-Stage Evolution (Guide for Reviewers)

To ensure instructors and reviewers can easily navigate the project history without confusion, the modeling work progresses through three distinct, documented generations:

```
[Generation 1: Historical Baseline]    ===>    [Generation 2: Refinement Cycle 1]    ===>    [Generation 3: Refinement Cycle 2 (Champion)]
Notebooks 04–07 (Milestone 1)                  Notebook 08 (refinement-selected-v3)          Notebook 09 & Exp 3 (refinement-selected-v4)
• 27 raw features (collinear, κ = ∞)           • 13/14 pruned features                       • Full-rank features (κ = 70.8)
• Random-grouped split by customer             • Chronological forward-chaining split        • Chronological forward-chaining split
• ⚠️ Severe temporal inversion leakage         • Customer purges + label maturity            • Customer purges + label maturity
• Untuned baselines                            • Baseline tree & unweighted logistic         • Tuned RF + log1p transforms + τ* = 0.17
                                               • Regression MAE: 5.540 days                  • Regression MAE: 3.719 days (-32.9% error)
                                               • R² = -0.360 (unreliable)                    • R² = +0.187 (strong generalization)
```

### Comparative Lifecycle Summary

| Feature / Dimension | Generation 1: Historical Baseline | Generation 2: Refinement Cycle 1 (`v3`) | Generation 3: Refinement Cycle 2 (`v4`, **Champion**) |
| :--- | :--- | :--- | :--- |
| **Notebook Reference** | [`notebooks/04` to `07`](notebooks/) | [`notebooks/08_refined_models_and_evidence.ipynb`](notebooks/08_refined_models_and_evidence.ipynb) | [`notebooks/09_refinement_cycle2_migration.ipynb`](notebooks/09_refinement_cycle2_migration.ipynb) |
| **Configuration File** | `src/models/configs/stage3_baseline.json` | `src/models/configs/refinement_selected_v3.json` | `src/models/configs/refinement_selected_v4.json` |
| **Artifact Location** | `artifacts/metrics/stage3-baseline-v1/` | `artifacts/metrics/refinement-selected-v3/` | `artifacts/metrics/refinement-selected-v4/` |
| **Feature Set** | 27 raw predictors (collinear) | 13 (regression) / 14 (classification) | 13 (regression) / 14 (classification), full-rank |
| **Matrix Conditioning** | Condition number $\kappa = \infty$ (rank deficient 9) | Not analyzed | Condition number $\kappa = 70.77$ (full rank 71/71) |
| **Validation Splitting** | Random Grouped 80/20 by `customer_unique_id` | 5-Fold Chronological Forward-Chaining | 5-Fold Chronological Forward-Chaining |
| **Leakage Controls** | ❌ **Temporal Inversion Leakage**: future 2018 orders leaked into 2017 training | ✅ **Leak-Free**: Training strictly precedes validation; validation customers purged | ✅ **Leak-Free**: Strict temporal arrow of time + customer purge + label maturity check |
| **Preprocessing** | Standard scaling & imputation only | Pipeline-encapsulated scaling & OHE | **Log1p scaling** on continuous inputs (`total_price`, `freight`, `distance`) |
| **Target Handling** | Raw continuous lead days (right-skewed) | Raw continuous lead days | **Target Log1p + 60d Winsorization** via `TransformedTargetRegressor` |
| **Regression Model** | Linear Regression & Untuned Tree | Decision Tree ($d=5$) | **Tuned Random Forest Regressor** ($N=50, d=14, L=20$) |
| **Classification Model** | Logistic Regression | Unweighted Logistic Regression ($C=0.01$) | **Tuned Random Forest Classifier** ($N=50, d=14, L=20$) |
| **Decision Policy** | Arbitrary default $\tau = 0.50$ | Default $\tau = 0.50$ | **Cost-Calibrated Optimal Threshold $\tau^* = 0.17$** ($1:5$ error cost ratio) |
| **Holdout Regression MAE** | 7.34 days (distorted) | 5.540 days | **3.719 days** (**$-1.822$ days, $-32.9\%$ error reduction**) |
| **Holdout Regression $R^2$** | Highly negative | $-0.3601$ | **$+0.1871$** (**swung strongly positive**) |
| **Holdout Detractor Recall**| $4.5\%$ | $27.4\%$ | **$38.2\%$** (True Positives jumped from $42 \to 517$) |
| **Holdout Business Error Cost** | Not optimized | $8,532$ cost units | **$8,205$ cost units** (**lowest total business loss**) |

---

## 🔬 How to Reconstruct the Entire Modeling Pipeline

Instructors and reviewers can reproduce and verify any part of the project using the methods below:

### Method 1: The Recommended Interactive Walkthrough (Jupyter Notebooks)

1. **Inspect Historical Baseline (Milestone 1)**:
   * Run [`notebooks/04_ml_feature_engineering.ipynb`](notebooks/04_ml_feature_engineering.ipynb) to [`notebooks/07_final_evaluation_and_scoring.ipynb`](notebooks/07_final_evaluation_and_scoring.ipynb).
   * Note the initial 27-feature baseline results and random-group split.
2. **Inspect Refinement Cycle 1 (Leakage Fix & Chronological Baseline)**:
   * Run [`notebooks/08_refined_models_and_evidence.ipynb`](notebooks/08_refined_models_and_evidence.ipynb).
   * Verifies the 5 chronological expansion folds and baseline decision tree / logistic regression models (`refinement-selected-v3`).
3. **Inspect Refinement Cycle 2 (Current Production Champion)**:
   * Run [`notebooks/09_refinement_cycle2_migration.ipynb`](notebooks/09_refinement_cycle2_migration.ipynb).
   * Directly loads the `refinement-selected-v4` models, executes live head-to-head comparisons, displays cost curves, and performs zero-fit production scoring on sample checkout orders.

---

### Method 2: Command-Line One-Step Reproduction (Cycle 2 / v4 Champion)

You can re-train, verify, and score the champion models directly from the command line:

```bash
# 1. Set environment variables for reproducibility
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1

# 2. Build the Refinement Cycle 2 bundle (5-fold chronological confirmation + final pre-terminal fits)
python -m src.models.refinement_selected_v4 build --output artifacts/metrics/refinement-selected-v4-reproduced

# 3. Evaluate the frozen production models on the unseen terminal holdout cohort
python -m src.models.refinement_selected_v4_terminal --run artifacts/metrics/refinement-selected-v4-reproduced --acknowledge-previously-inspected-terminal
```

---

### Method 3: Live No-Fit Production Batch Scoring

To score new, unseen checkout transactions using the frozen production model bundles without retraining:

```bash
# Score Regression (Delivery Lead Time Prediction in days):
python -m src.models.refinement_selected_v4 score \
  --bundle artifacts/metrics/refinement-selected-v4/bundles/regression/selected \
  --input data/business/ml/sample_test_orders.csv \
  --output artifacts/metrics/lead_days_predictions.csv

# Score Classification (Detractor Risk & Calibrated Alert Decision):
python -m src.models.refinement_selected_v4 score \
  --bundle artifacts/metrics/refinement-selected-v4/bundles/classification/selected \
  --input data/business/ml/sample_test_orders.csv \
  --output artifacts/metrics/detractor_risk_predictions.csv
```

---

### Method 4: Comprehensive Experiment 3 Research Audit

The exhaustive 6-phase research study that generated the champion configuration is completely documented and reproducible:
* **Study Report**: [`experiments/experiment_3/SUMMARY_REPORT.md`](experiments/experiment_3/SUMMARY_REPORT.md)
* **Reproduction Guide**: [`experiments/experiment_3/README.md`](experiments/experiment_3/README.md)
* **Master One-Command Runner**:
  ```bash
  python experiments/experiment_3/run_all.py
  ```

---

## ⚠️ Methodological Notes & Literature Integrity

* **Entities: `customer_id` vs. `customer_unique_id`**:
  * `customer_id`: single-use 1-time session transaction token.
  * `customer_unique_id`: persistent unique identifier of the real individual customer.
  * Over **$97\%$** of buyers on Olist are single-order customers. Models predict cold-start lead time and detractor risk for new buyers at checkout.
* **Leakage Avoidance (Kapoor & Narayanan, 2023; Arpogaus et al., 2024)**:
  * Downstream event columns (`order_delivered_customer_date`, `delivery_days`, `review_score`, `is_on_time`) are strictly excluded from predictors.
  * In Refinement Cycles 1 and 2, chronological forward-chaining cross-validation guarantees that models only train on past transactions to predict future ones.
  * Validation customer purging guarantees zero customer identity overlap between training and testing sets.
