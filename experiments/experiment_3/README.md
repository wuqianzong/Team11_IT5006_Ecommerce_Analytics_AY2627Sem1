# Experiment 3: Comprehensive Model Refinement & Evaluation

This directory contains the complete, self-contained implementation, documentation, and reproduction scripts for **Experiment 3**.

Experiment 3 addresses the core structural deficiencies identified in early project baselines:
1. **Multicollinearity & Design Matrix Singularity:** Resolving rank deficiency (9) and infinite condition number ($\kappa = \infty$) in the original 27-feature set.
2. **Extreme Distribution Skewness & Tail Outliers:** Addressing severe right-skew on target delivery lead time ($g_1 = 3.70$, $g_2 = 37.17$) and continuous financial/distance features.
3. **Hyperparameter Invalidation:** Eliminating default hyperparameter bias by performing formal `GridSearchCV` hyperparameter tuning across all candidate model families.
4. **Asymmetric Business Decision Costs:** Overcoming the failure of the default $\tau = 0.50$ threshold on imbalanced customer detractor classification ($14.7\%$ minority rate).

All methods deployed strictly adhere to the techniques taught in the NUS IT5006 lab curriculum (**Weeks 01–08: Tutorials 5, 6, 7, and 8**).

---

## 📁 Directory Structure & File Manifest

```
experiments/experiment_3/
├── README.md                                 # This reproduction guide
├── PLAN.md                                   # Comprehensive 6-phase experimental plan
├── TO_TEST_LIST.md                           # Master hypothesis and decision backlog
├── SUMMARY_REPORT.md                         # Academic master synthesis report
├── run_eda_outliers.py                       # Phase 1: Distribution tail audit & outlier ablation
├── run_collinearity_reduction.py             # Phase 2: Correlation matrices & 27 -> 11 feature reduction
├── run_feature_expansion_importance.py       # Phase 3: Base-to-complex hierarchy & task-specific expansion
├── run_phase4_transforms_and_tuning.py       # Phase 4: Target log1p & GridSearchCV hyperparameter tuning
├── run_phase5_threshold_calibration.py       # Phase 5: Probability calibration & cost-curve optimization
├── run_phase6_final_synthesis.py             # Phase 6: Unified Train vs. 5-Fold CV vs. Holdout benchmark
└── run_all.py                                # End-to-end master runner script

artifacts/metrics/experiment-3/
├── eda/                                      # Phase 1 plots (boxplots, Cook's distance) & skewness CSVs
├── feature_selection/                        # Phase 2 correlation matrices (27 & 11) & rank audits
├── feature_importance/                       # Phase 3 feature importances & expansion comparisons
├── transforms_and_tuning/                    # Phase 4 tuning comparisons & ablation tables
├── threshold_calibration/                    # Phase 5 calibration curves & 4-panel cost plots
└── final_synthesis/                          # Phase 6 unified benchmark tables & comparison plots
```

---

## 🚀 Quick Reproduction Guide

All experiments are fully deterministic (`seed=42`) and execute strictly from the repository root using the existing project conda environment.

### Prerequisites

Ensure the conda environment is active and project dependencies are available:
```bash
conda activate QuantBrain
# Verify that scikit-learn, pandas, numpy, matplotlib, and seaborn are available
python -c "import sklearn, pandas, numpy, matplotlib, seaborn; print('Environment ready!')"
```

### Option A: Run Full End-to-End Reproduction (All 6 Phases)

To execute the entire 6-phase experiment sequentially and reproduce all tables and figures:
```bash
python experiments/experiment_3/run_all.py
```

### Option B: Execute Phase-by-Phase

You can run individual phases independently:

#### Phase 1: Tail Audit & Outlier Treatment
```bash
python experiments/experiment_3/run_eda_outliers.py
```
* **Outputs:** `artifacts/metrics/experiment-3/eda/`
* **Verification Checkpoint:** Confirms right-skewness on `lead_days` ($g_1=3.70$, $g_2=37.17$). 5-fold CV demonstrates that Winsorization (clipping at 60d) achieves MAE **$5.235$d** vs. raw baseline $5.263$d ($\Delta = -0.028$d).

#### Phase 2: Multicollinearity Audit & Feature Reduction
```bash
python experiments/experiment_3/run_collinearity_reduction.py
```
* **Outputs:** `artifacts/metrics/experiment-3/feature_selection/`
* **Verification Checkpoint:** Confirms 27 baseline features have rank deficiency 9 and condition number $\kappa = \infty$. Pruning to 11 core features restores full numerical rank (**71/71**) and slashes condition number to $\mathbf{\kappa = 70.77}$.

#### Phase 3: Base-to-Complex Hierarchy & Task-Specific Expansion
```bash
python experiments/experiment_3/run_feature_expansion_importance.py
```
* **Outputs:** `artifacts/metrics/experiment-3/feature_importance/`
* **Verification Checkpoint:** Confirms expanding to 13 features for regression (adding `distance_km_max`) improves Random Forest MAE from $5.098$d $\to \mathbf{4.986}$d. Expanding to 14 features for classification (adding seller/interstate variables) restores Logistic AP to $0.2990$ and Random Forest to $0.2991$.

#### Phase 4: Pre-Scaling, Target Log-Transformations & GridSearchCV Tuning
```bash
python experiments/experiment_3/run_phase4_transforms_and_tuning.py
```
* **Outputs:** `artifacts/metrics/experiment-3/transforms_and_tuning/`
* **Verification Checkpoint:** Confirms target log-transformation $\log(1+y)$ via `TransformedTargetRegressor` drops Ridge MAE from $5.141$d $\to \mathbf{4.794}$d ($-0.35$d) and Random Forest to **$4.718$d**. Decision Tree classification AP jumps from $0.2626 \to \mathbf{0.2843}$ ($+0.0217$).

#### Phase 5: Probability Calibration & Business Cost-Curve Threshold Optimization
```bash
python experiments/experiment_3/run_phase5_threshold_calibration.py
```
* **Outputs:** `artifacts/metrics/experiment-3/threshold_calibration/`
* **Verification Checkpoint:** Confirms empirical probability calibration (Brier score loss: $0.1174$). Under $1:5$ error cost ratio, shifting decision threshold from $\tau = 0.50 \to \mathbf{\tau^* = 0.17}$ increases detractor recall from $4.5\% \to \mathbf{38.2\%}$ and saves **$16.3\%$ in operational error costs** ($9,100$ cost units saved).

#### Phase 6: Unified Benchmark (Train vs. 5-Fold CV vs. Terminal Holdout)
```bash
python experiments/experiment_3/run_phase6_final_synthesis.py
```
* **Outputs:** `artifacts/metrics/experiment-3/final_synthesis/`
* **Verification Checkpoint:** Evaluates the complete model hierarchy across 77k development orders and 19k locked holdout test orders. Confirms tuned Random Forest beats baseline by **$-0.187$d MAE on holdout** ($4.839$d vs $5.026$d) and delivers a **$15.0\%$ cost reduction** on holdout test data.

---

## 📊 Summary of Master Holdout Results

| Task | Champion Model Architecture | Features | 5-Fold CV Validation | Terminal Holdout Test | Baseline Holdout | Absolute Gain on Holdout |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Regression** | Random Forest (`depth=14, leaf=20`) + Target Log1p | 13 | **$4.718 \pm 0.059$d** MAE | **$4.839$d** MAE | 5.026d MAE | **$-0.187$ days** ($-3.7\%$ error) |
| **Classification** | Random Forest (`depth=14, leaf=20`) + Log1p Pre-scale | 14 | **$0.3064 \pm 0.0011$** AP | **$0.3130$** AP | 0.3077 AP | **$+0.0053$ AP** |
| **Policy Cost** | Optimal Decision Threshold ($\tau^* = 0.17$) | 14 | $46,812$ Cost | **$11,802$** Cost | 13,885 Cost ($\tau=0.50$) | **$-15.0\%$ Cost Reduction** |

---

## 🔒 Containment & Scientific Governance

* **Zero Leakage:** All transformations (target log-transformation, input scaling, imputation, one-hot encoding) are encapsulated within `sklearn.pipeline.Pipeline` and fit strictly on training folds.
* **Locked Input Hashes:** Input datasets (`data/business/ml/orders_ml_features.csv` and `data/business/ml/split_assignments.csv`) are validated against canonical SHA-256 digests.
* **Read-Only Working Directory:** Production source code (`src/`), notebooks (`notebooks/`), and frozen baseline bundle directories remain untouched during all phases of Experiment 3.
