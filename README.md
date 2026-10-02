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
│   └── business/
│       ├── dashboard/        # 9 processed CSVs + smartcommerce_consolidated.csv (ready for Streamlit)
│       └── ml/               # Point-in-time features, targets (orders_ml_features.csv) & splits
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb                    # Stage 1: raw -> preprocessed (types, zip codes, GPS dedup)
│   ├── 02_dashboard_preprocessing.ipynb          # Stage 2: preprocessed -> business/dashboard (filtering & metrics)
│   ├── 03_business_dashboard_data_preprocessing.ipynb # Stage 3: data preview, table consolidation & KPI validation
│   └── 04_ml_feature_engineering.ipynb           # Stage 4: preprocessed -> business/ml (point-in-time features)
│
├── deployment/               # Official directory for the dashboard application
│   └── app.py                # Executive Operations Master Dashboard (Streamlit application)
│
├── src/                      # Reusable Python source code and shared utilities
│   ├── common/               # Shared schemas, loaders, and utilities
│   ├── features/             # Feature engineering encoders and transformers
│   └── models/               # Model training, hyperparameter tuning, and evaluation
│
├── docs/
│   ├── references/           # Course project description & 6 curated literature review PDFs
│   ├── data_architecture.md  # Architectural specification and data contracts
│   └── milestone2_proposal.md# Milestone 2 proposal and modeling blueprint
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
| **3B. Business (ML)** | `data/business/ml/` | **Predictive modeling features & targets**: Point-in-time features frozen at `order_purchase_timestamp` (`orders_ml_features.csv`). Strictly isolates training data from dashboard date clipping and prevents post-purchase target leakage. Splitting strictly grouped by `customer_unique_id`. |

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

---

## ⚠️ Important Course Guidelines & Data Gotchas

* **`customer_id` vs. `customer_unique_id`**:
  * `customer_id`: a 1-time session key generated per transaction.
  * `customer_unique_id`: the persistent identifier of the actual human customer.
  * *Always use `customer_unique_id` for repeat-purchase analysis, customer retention, or customer-level features.*
* **Data Leakage Warnings (Literature: Kapoor & Narayanan, 2023)**:
  * Columns like `order_delivered_customer_date`, `delivery_days`, and `is_on_time` are **outcomes**, not predictors.
  * They are included in the dashboard tables purely for historical performance reporting. For Phase 2 predictive models, features must strictly use information known at or before checkout.
