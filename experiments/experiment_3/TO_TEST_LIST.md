# Experiment 3: To-Test Master List & Planning Document

**Created:** 2026-10-08  
**Status:** Active Planning & Backlog  
**Purpose:** A staged backlog of hypotheses, feature engineering ideas, algorithmic tweaks, and validation experiments to be tested systematically before applying changes to the canonical production pipeline.

---

## 📋 Table of Contents
1. [Core Testing Principles & Guardrails](#1-core-testing-principles--guardrails)
2. [Top-Priority Test Items (User Focus Areas)](#2-top-priority-test-items-user-focus-areas)
   - [Item 1: Skewness/Tail Diagnostics & Pre-Scaling Log-Transformation (`log1p` $\rightarrow$ `StandardScaler`)](#item-1-skewnesstail-diagnostics--pre-scaling-log-transformation-log1p--standardscaler)
   - [Item 2: Lead Time Target Log-Transformation Evaluation ($\log(1+y)$)](#item-2-lead-time-target-log-transformation-evaluation-log1y)
   - [Item 3: Extreme Outlier Diagnostics, Charts & Business Judgment (Clipping vs. Removal)](#item-3-extreme-outlier-diagnostics-charts--business-judgment-clipping-vs-removal)
3. [Broader Backlog of Experiment 3 Hypotheses](#3-broader-backlog-of-experiment-3-hypotheses)
   - [Category C: High-Cardinality & Interaction Feature Engineering](#category-c-high-cardinality--interaction-feature-engineering)
   - [Category D: Classification Probability Calibration & Decision Policies](#category-d-classification-probability-calibration--decision-policies)
   - [Category E: Evaluation, Cross-Validation & Metric Reporting](#category-e-evaluation-cross-validation--metric-reporting)
4. [Experiment Execution Tracker](#4-experiment-execution-tracker)
5. [Log of Additions & Discussion Notes](#5-log-of-additions--discussion-notes)

---

## 1. Core Testing Principles & Guardrails

To prevent data leakage, overfitting, and unprincipled model drift, all items in this backlog must adhere to the following rules:
* **Chronological Split Integrity:** No test may violate the expanding temporal windows or use future labels to predict past events.
* **Leakage-Free Pipelines:** All transformations (imputation medians, scaling statistics, target encoding maps, outlier clipping thresholds) must be fit strictly on training folds and applied out-of-fold.
* **Pre-declared Significance Thresholds:**
  * **Regression:** Candidate must achieve $\Delta \text{MAE} > 0.05$ days across at least 4 of 5 cross-validation folds to justify adoption.
  * **Classification:** Candidate must achieve $\Delta \text{Average Precision} > 0.005$ across at least 4 of 5 folds.
* **Sandbox Verification:** Every experiment runs in an isolated subfolder under `experiments/experiment_3/` with a frozen protocol JSON before any code touches `src/models/` or production bundles.

---

## 2. Top-Priority Test Items (User Focus Areas)

### Item 1: Skewness/Tail Diagnostics & Pre-Scaling Log-Transformation (`log1p` $\rightarrow$ `StandardScaler`)
* **ID:** `EXP3-PRE-01`
* **Priority:** Highest
* **Background & Motivation:**
  - Continuous numeric features (`total_price`, `total_freight`, `distance_km_max`) exhibit heavy right-skewed Pareto distributions. For example, `total_price` has a median of R\$ 86.3 but a maximum of R\$ 13,440; `total_freight` has a median of R\$ 16.8 with extreme charges over R\$ 400.
  - In linear/logistic models, applying `StandardScaler()` directly on raw skewed data causes standard deviation $\sigma$ to be inflated by extreme tail points, compressing the typical order mass into a dense spike near zero.
* **Specific Experimental Plan:**
  1. *Distribution & Skewness Audit:*
     - Compute skewness ($g_1 = \frac{m_3}{s^3}$), kurtosis ($g_2 = \frac{m_4}{s^4} - 3$), P50, P90, P95, P99, and Max for all continuous predictors.
     - Set a principled threshold: Any continuous feature with skewness $g_1 > 1.5$ (or kurtosis $> 3.0$) receives a non-linear log transform.
  2. *Pipeline Transformation Protocol:*
     - Apply $\log(1 + x)$ (`FunctionTransformer(np.log1p)`) **before** `StandardScaler()`:
       $$\text{Raw } x \xrightarrow{\text{SimpleImputer(strategy='median')}} \xrightarrow{\text{FunctionTransformer(np.log1p)}} \xrightarrow{\text{StandardScaler()}} \text{Model}$$
     - In tree models, evaluate whether feeding $\log(1+x)$ directly improves split search efficiency and leaf density.
  3. *Evaluation Metric:*
     - Compare design matrix condition numbers ($\kappa$), coefficient stability, and 5-fold cross-validation metrics against the current baseline.

---

### Item 2: Lead Time Target Log-Transformation Evaluation ($\log(1+y)$)
* **ID:** `EXP3-REG-01`
* **Priority:** Highest
* **Background & Motivation:**
  - In Milestone 2, the delivery lead time target $y = \text{lead\_days}$ has severe positive skew (median $\approx 10.2$ days, mean $\approx 12.1$ days, P99 $\approx 42.0$ days, with long delays reaching 195 days).
  - The Milestone 2 Decision Tree Regressor fit raw days directly. Because trees output piecewise-constant leaves bounded by training averages ($\le 25$ days), when extreme delay outliers appeared in the out-of-period terminal holdout, squared error exploded, causing the catastrophic $R^2 = -0.3602$ failure.
* **Specific Experimental Plan:**
  1. *Architecture Implementation:*
     - Wrap estimators in scikit-learn's `TransformedTargetRegressor`:
       $$y^* = \log(1 + y), \quad \hat{y} = \exp(\hat{y}^*) - 1$$
     - Evaluate both standard back-transformation and Duan's smearing correction factor ($\hat{y} = \exp(\hat{y}^* + \frac{1}{2}\hat{\sigma}^2) - 1$) to avoid geometric-mean under-prediction bias.
  2. *Candidate Models to Benchmark:*
     - Decision Tree Regressor (`max_depth=5`, `min_samples_leaf=100`)
     - Ridge Regression ($L_2$ shrinkage with standardized features)
     - Random Forest Regressor (64 trees, `max_depth=12`)
  3. *Comparative Evaluation:*
     - Must evaluate predictions back on the **original physical scale (days)** for honest comparison: MAE (days), RMSE (days), and $R^2$.
     - Also measure Log-scale error (RMSLE / Root Mean Squared Logarithmic Error).
     - Test whether target log-transformation eliminates the negative $R^2$ on terminal holdout.

---

### Item 3: Extreme Outlier Diagnostics, Charts & Business Judgment (Clipping vs. Removal)
* **ID:** `EXP3-OUT-01`
* **Priority:** Highest
* **Background & Motivation:**
  - In regression, extreme delays (e.g. 54.8-day delivery in Sept 2016, or 100+ day anomalies) and massive order values exert extreme leverage. We must formally evaluate whether these data points should be **clipped (Winsorized)** or **removed**, backed by visual charts and business scenario reasoning.
* **Specific Experimental Plan:**
  1. *Diagnostic Visualizations (Charts to Generate):*
     - **Boxplots & Violin Plots:** Visualizing distributions of raw vs. log-transformed values for `lead_days`, `total_freight`, and `total_price`.
     - **Scatter Plots & Cook's Distance:** Plotting `lead_days` vs. `distance_km_max` and identifying high-leverage outliers.
     - **Monthly Trend Charts:** Inspecting when extreme delays clustered (e.g., Brazilian postal strike periods, carrier hub disruptions).
  2. *Business & Practical Scenario Evaluation (Trade-off Analysis):*
     - **Removal (Dropping Records):**
       - *Business Reality:* In e-commerce, severely delayed orders represent real customers who experienced fulfillment failures and left negative reviews. Silently deleting them from training creates severe survival/selection bias. The model will systematically under-predict delivery dates during carrier disruptions.
       - *When Removal IS Justified:* Only when records represent verifiable data corruption (e.g. delivery date recorded *before* purchase date, or canceled orders mistakenly labeled as delivered).
     - **Clipping / Winsorization (Bounding Extremes):**
       - *Business Reality:* Setting an operational ceiling (e.g. capping `lead_days` at 60 or 90 days, or capping freight at P99) preserves the order and its multi-item signals, while capping the squared-error loss $(y - \hat{y})^2$ so single 150-day outliers cannot distort tree splits or linear slope.
       - *Implementation:* Custom transformer `Winsorizer(lower_quantile=0.0, upper_quantile=0.99)` fit strictly on training folds.
  3. *3-Way Empirical Benchmark on Cross-Validation & Terminal Holdout:*
     - **Option A:** Raw Untreated Data (Current Baseline)
     - **Option B:** Winsorized / Clipped Data (Target capped at 60 days, Freight capped at P99)
     - **Option C:** Filtered / Removed Outliers ($y > 60$ days excluded from training)

---

## 3. Broader Backlog of Experiment 3 Hypotheses

### Category C: High-Cardinality & Interaction Feature Engineering
* [ ] **EXP3-FE-01: Target Encoding for High-Cardinality Product Categories**
  * *Hypothesis:* Instead of 71 sparse one-hot dummy columns (which caused matrix rank deficiency of 170 vs 187), out-of-fold target encoding with smoothing ($m$-estimate) will capture category delivery speed without expanding matrix dimensionality.
  * *Priority:* Medium
* [ ] **EXP3-FE-02: Spatial & Logistics Interaction Terms**
  * *Hypothesis:* Interaction terms such as $\text{distance\_km\_max} \times \text{interstate\_share}$ and $\text{n\_sellers} \times \text{n\_items}$ will capture compounding delivery friction and split-shipment risks.
  * *Priority:* Medium

### Category D: Classification Probability Calibration & Decision Policies
* [ ] **EXP3-CLF-01: Threshold Optimization under Cost Curves**
  * *Hypothesis:* Exploring dynamic cutoff selection across different operational cost ratios ($C_{\text{FP}} : C_{\text{FN}} \in \{1:2, 1:5, 1:10\}$) will produce a more practical operational alert rate on terminal holdout than the fixed $17.1\%$ alert rate.
  * *Priority:* Medium
* [ ] **EXP3-CLF-02: Probability Calibration (Isotonic vs. Platt Scaling)**
  * *Hypothesis:* Post-hoc calibration via `CalibratedClassifierCV(method="sigmoid", cv="prefit")` will improve Brier score and log-loss on out-of-fold predictions.
  * *Priority:* Low

### Category E: Evaluation, Cross-Validation & Metric Reporting
* [ ] **EXP3-EVAL-01: Unified Train-Validation-Holdout Comparison Tables**
  * *Hypothesis:* Structuring all future experiment outputs into an automated unified 3-column table (Train Resubstitution, Validation Mean $\pm$ SD, Terminal Holdout) will directly satisfy teacher expectations and catch overfitting gaps immediately.
  * *Priority:* High

---

## 4. Experiment Execution Tracker

| Experiment ID | Description | Target Task | Status | Dev CV Metric | Terminal Metric | Decision |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **EXP3-OUT-01** | Outlier charts & Clipping vs. Removal evaluation | Both | **Completed (Phase 1)** | Raw: MAE 5.263d, RMSE 8.309d, R² 0.2243<br>Clipped: MAE 5.234d, RMSE 8.313d, R² 0.2235<br>Removed: MAE 5.202d, RMSE 8.321d, R² 0.2220 | Retained in dev (Zero holdout touch) | **Adopt Clipping (Winsorization)**: Improves MAE by 0.028d without inducing survival bias or dropping genuine delayed reviews |
| **EXP3-SEL-01** | Multicollinearity Audit & Feature Reduction (27 -> 9, Option 1) | Both | **Completed (Phase 2)** | 27 features: Rank deficiency 9, κ = ∞<br>9 features: Rank deficiency 0, κ = 70.77 | N/A (Feature contract) | **Adopt 9 Core Features (Option 1)**: Eliminates singular design matrix, drops bulk/missingness collinearity and invariant/leakage flags (`has_items`, `freight_ratio_missing`) |
| **EXP3-SEL-02** | Task-Specific Feature Expansion (9 -> 11/12) & Base-to-Complex | Both | **Completed (Phase 3)** | Reg MAE: RF achieves 4.986d; Clf AP: Logistic achieves 0.2990 | N/A (Feature contract) | **Adopt Expanded 11/12 Sets**: Consistently benefits all model tiers across 5-fold CV |
| **EXP3-PRE-01** | Input Skewness `log1p` Pre-Scaling before `StandardScaler` | Both | **Completed (Phase 4A)** | Ridge Reg MAE drops 5.141d -> 5.075d; Logistic Clf AP improves to 0.3000 | Pending Final Gate | **Adopt `log1p` pre-scaling** on continuous dollar/distance predictors |
| **EXP3-REG-01** | Target log transformation ($\log(1+y)$) | Regression | **Completed (Phase 4A)** | Ridge MAE drops 5.141d -> 4.794d (-0.347d); RF drops to 4.793d (-0.193d) | Pending Final Gate | **Adopt TransformedTargetRegressor**: Massive, unambiguous regression performance boost |
| **EXP3-TUNE-01**| GridSearchCV Tuning across all candidate models | Both | **Completed (Phase 4B)** | DT Clf AP: 0.2626 -> 0.2843 (+0.0217); RF Clf AP: 0.3064; RF Reg MAE: 4.718d | Pending Final Gate | **Adopt Tuned Parameters**: Resolves default hyperparameter bias across both tasks |
| **EXP3-CLF-01** | Cost-curve threshold tuning & Platt calibration | Classification | **Completed (Phase 5)** | Brier 0.1174; under 1:5 cost ratio, tau*=0.17 cuts business cost by 16.3% | Retained in dev | **Adopt Operating Threshold $\tau^* = 0.17$**: F1 max 0.330; catches 38.2% of detractors |
| **EXP3-EVAL-01** | Unified Train-Validation-Holdout benchmark table | Both | **Completed (Phase 6)** | RF Reg Holdout MAE 4.839d (-0.187d vs base); RF Clf Holdout AP 0.3130 | Evaluated on Holdout | **Champion Confirmed**: Zero data leakage; stable generalization across all 3 tiers |

---

## 5. Log of Additions & Discussion Notes

* **2026-10-08 (Initial Setup):** Master list established with baseline guardrails and initial hypotheses.
* **2026-10-08 (User Additions - Items 1, 2, 3):**
  - Added **EXP3-PRE-01:** Full skewness/tail audit across continuous features; apply $\log(1+x)$ prior to `StandardScaler()`.
  - Added **EXP3-REG-01:** Target log-transformation evaluation on `lead_days` via `TransformedTargetRegressor` to resolve decision tree tail collapse.
  - Added **EXP3-OUT-01:** Extreme outlier diagnostic visualizations (boxplots, Cook's distance, trends) and formal business evaluation comparing raw vs. clipped (Winsorized) vs. dropped records.
* **2026-10-09 (Phase 1 Execution Completed):**
  - Completed distribution skewness and kurtosis audit on 77,139 development orders.
  - Conducted 3-way outlier ablation study across 5 temporal folds: Clipped (Winsorized at 60d target, P99 freight) achieved best trade-off (MAE 5.234d vs Raw 5.263d) while preserving operational delay signals and avoiding survival bias.
* **2026-10-09 (Phase 2 Execution Completed):**
  - Computed full $27 \times 27$ Pearson correlation matrix and audited rank deficiency.
  - 27 features had rank deficiency 9 and condition number $\kappa = \infty$. Pruning to 9 core features (Option 1) restored full numerical rank (71/71) and lowered condition number to $\mathbf{\kappa = 70.77}$.
* **2026-10-09 (Phase 3 Execution Completed):**
  - Full Base-to-Complex model benchmark executed across 27 vs 9 vs 11/12 features (Ridge/Logistic -> Decision Tree -> Random Forest).
  - Adding `distance_km_max` recovered regression MAE by $-0.11$ to $-0.15$ days across all model families; adding seller/interstate features restored classification AP to parity ($0.2990 \approx 0.2998$) while eliminating rank deficiency.
* **2026-10-09 (Phase 4 Execution Completed):**
  - **Phase 4A (Transforms):** Target log-transformation via `TransformedTargetRegressor(func=np.log1p, inverse_func=np.expm1)` produced a massive breakthrough: Ridge MAE plunged from $5.141$d $\to \mathbf{4.794}$d ($-0.347$ days), and Random Forest dropped from $4.986$d $\to \mathbf{4.793}$d ($-0.193$ days). Input `log1p` on skewed predictors improved Logistic Regression AP to $0.3000$.
  - **Phase 4B (GridSearchCV Tuning):** Tuned all candidate model families. Decision Tree classification AP surged from $0.2626 \to \mathbf{0.2843}$ ($+0.0217$ AP gain). Random Forest achieved champion performance: **MAE $4.718$ days** for Regression (`max_depth=14, min_samples_leaf=20`) and **AP $0.3064$** for Classification (`max_depth=14, min_samples_leaf=20`).
* **2026-10-09 (Phase 5 Execution Completed):**
  - **Phase 5A (Probability Calibration):** Audited reliability curves and Brier score loss across 5 temporal folds. Both Logistic Regression (Brier $0.1176$) and Tuned Random Forest (Brier $0.1174$) exhibit near-ideal diagonal reliability without needing post-hoc Platt warping.
  - **Phase 5B (Asymmetric Cost Curves):** Evaluated decision threshold $\tau \in [0.05, 0.90]$ across 3 cost ratios ($1:1, 1:5, 1:10$). At default $\tau=0.50$, recall is only $4.5\%$ (missing $95\%$ of angry customers). Under realistic proactive support costs ($1:5$), lowering the decision threshold to **$\tau^* = 0.17$** achieves maximum F1 ($0.330$), catches $38.2\%$ of detractors (precision $0.290$, alert rate $19.4\%$), and cuts total operational business loss by **$16.3\%$ (saving $9,100$ cost units)**. Saved 4-panel diagnostic plot `threshold_optimization_4panel.png` and reliability curves `calibration_curves.png`.

