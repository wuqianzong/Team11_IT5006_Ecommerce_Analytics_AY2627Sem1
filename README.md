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
│       └── dashboard/        # 9 processed CSVs + smartcommerce_consolidated.csv (ready for Streamlit)
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb                    # Stage 1: raw -> preprocessed (types, zip codes, GPS dedup)
│   ├── 02_dashboard_preprocessing.ipynb          # Stage 2: preprocessed -> business/dashboard (filtering & metrics)
│   └── 03_business_dashboard_data_preprocessing.ipynb # Stage 3: data preview, table consolidation & KPI validation
│
├── deployment/               # Official directory for the dashboard application
│   └── app.py                # Executive Operations Master Dashboard (Streamlit application)
│
├── src/                      # Reusable Python source code and shared utilities
│   └── common/               # Shared schemas and utilities
│
├── docs/
│   ├── references/           # Course project description & 6 curated literature review PDFs
│   └── data_architecture.md  # Architectural specification and data contracts
│
├── app.py                    # Root entrypoint launcher (delegates execution to deployment/app.py)
├── requirements.txt          # Python dependencies for local run and Streamlit Cloud
└── README.md
```

---

## 🔄 Data Architecture & Lineage

The data is organized into three clean layers under `data/`:

$$\text{data/raw/} \xrightarrow[\text{01\_data\_cleaning.ipynb}]{\textbf{Stage 1: Clean}} \text{data/preprocessed/} \xrightarrow[\text{02\_dashboard\_preprocessing.ipynb}]{\textbf{Stage 2: Process}} \text{data/business/dashboard/} \xrightarrow[\text{03\_business\_dashboard\_data\_preprocessing.ipynb}]{\textbf{Stage 3: Consolidate}} \text{smartcommerce\_consolidated.csv}$$

| Layer | Folder Path | Purpose & Rules |
| :--- | :--- | :--- |
| **1. Raw** | `data/raw/` | Exact, immutable copies of the 9 original Olist CSV files downloaded from Canvas. Never edit or overwrite manually. |
| **2. Preprocessed** | `data/preprocessed/` | **Lossless baseline**: Parses ISO datetimes (`pd.to_datetime`), preserves 5-digit zip codes as strings (`01037`), checks categorical enums, and removes 261,831 exact duplicate GPS rows. Keeps 100% of transaction rows across all other tables. |
| **3. Business** | `data/business/dashboard/` | **Dashboard-ready tables**: Applies business rules for executive presentation: removes timestamp sequence errors, filters orders to the stable operating period (**2017-01 to 2018-08**), collapses multi-reviews to the lowest review score, and pre-calculates `delivery_days`, `is_on_time`, and `item_revenue`. Also houses the master merged table `smartcommerce_consolidated.csv`. |

> *Note for Phase 2 Modeling*: Future feature sets, target vectors, and train/test splits for machine learning will live under a dedicated `data/business/ml/` folder to prevent data leakage and avoid mixing modeling data with dashboard-specific date filters.

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
