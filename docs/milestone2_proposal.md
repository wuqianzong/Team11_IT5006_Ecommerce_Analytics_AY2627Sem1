# Milestone 2 Proposal: Delivery Lead Time and Low-Review Risk at Checkout

Status: revised implementation proposal, 2026-10-02. Results remain to be established.

Milestone 2: 11 October 2026, 23:59; 40%; technical report of 6–8 pages excluding
cover, references, and appendices. Verify deadline changes on Canvas.

## 1. Scope and business questions

We address two related prediction problems, using the same order-level checkout
features and two reusable model families. This meets the brief's requirement for
both regression and classification; connecting the models through stacking is
optional, not a prerequisite.

| Task | Question and target | Population and stakeholder |
| --- | --- | --- |
| Delivery regression | Predict elapsed calendar days from purchase to customer delivery: `lead_days = total_seconds(delivered_customer_date - purchase_timestamp) / 86400`. | Delivered orders with valid dates; fulfillment/customer service. Predictions describe duration conditional on eventual delivery. |
| Low-review classification | Predict whether an order has any recorded review of 1–2 stars: `is_detractor = int(review_score_min <= 2)`. | Orders with a valid recorded review, including non-delivered orders; customer experience/seller operations. Predictions are evaluated among reviewed orders, not all possible customer experiences. |

Prediction time is immediately after checkout, represented by
`order_purchase_timestamp`. The data does not timestamp every checkout field or
provide historical product snapshots. Treat availability of recorded prices,
seller allocation, payment information, and product attributes as documented
assumptions, not proven historical facts.

No review means an unknown classification target, not a satisfied customer.
Regression eligibility must not require a review. Classification eligibility must
not require eventual delivery. Eligibility flags and exclusions are task-specific.

The intended actions are delivery-time decision support and prioritizing orders
for customer-service attention. Predictive accuracy does not establish that an
intervention prevents a bad review, increases conversion, or improves profit.
The dataset has neither pre-purchase conversion denominators nor randomized
interventions. Any economic scenario must identify assumed costs and effectiveness.

## 2. Data and feature architecture

Source: the nine typed tables in `data/preprocessed/`. Do not use dashboard
tables or copy dashboard date/review filters into ML implicitly.

One shared table, `data/business/ml/orders_ml_features.csv`, preserves one row
per source order. It contains clearly separated identifier/audit, feature, target,
and eligibility columns. Each training script selects an explicit feature
allowlist. Targets, IDs, timestamps used to construct outcomes, and eligibility
flags must never enter predictors.

Read the [ML guideline](../data/business/ml/README.md) and
[feature contract](../data/business/ml/feature_contract.md) before implementation.
The contract defines exact aggregation, missing-value, split, and validation rules.

Initial feature groups:

- Geography: customer state, primary seller state, mean/maximum seller distance,
  interstate share, and seller count.
- Basket and financial: item/product/category counts, total price, total freight,
  and freight-to-price ratio.
- Product properties: complete-case item weight/volume totals with missingness
  fractions; deterministic primary product category.
- Purchase context: month, weekday, hour, and documented payment summaries.
- Secondary experiment: primary-item description length and photo count.

Retain state categories initially. Do not remove freight solely because a ratio
uses it. Haversine distance is a straight-line geographic proxy, not road distance.
Product volume sums are not measured package volume.

Learn imputation, category grouping, scaling, feature selection, and any clipping
thresholds inside development folds. Keep deterministic sums and ratios in the
shared base table. Never pre-scale the exported feature table.

Historical seller outcomes and regression predictions are excluded from baseline
version 1. They require fold-specific construction and separate provenance.

## 3. Cohort evidence and target definition

A read-only audit on 2026-10-02 found:

| Check | Count |
| --- | ---: |
| Source orders | 99,441 |
| Orders with multiple items | 9,803 |
| Orders with multiple sellers | 1,278 |
| Orders with multiple review records | 547 |
| Reviewed orders, minimum-score rule | 98,673 |
| Negative orders among those reviewed | 14,533 |
| Delivered-and-reviewed orders, minimum-score rule | 95,832 |
| Negative delivered-and-reviewed orders | 12,311 |

These are snapshot checks before the final eligibility validations, not fixed
training sizes or expected test results. The old 12.85% prevalence applies to the
delivered-and-reviewed cohort only. Recompute all cohort counts, class proportions,
and baselines from the implemented target version.

Minimum score defines “any recorded negative review,” rather than first experience
or final satisfaction. Use first answered review as an optional label sensitivity
analysis on development data. All-review snapshot labels have variable follow-up;
report this limitation. A temporal experiment additionally needs a fixed observation
window and label-maturity rules, as defined in the feature contract.

## 4. Models and scope control

| Level | Regression | Classification |
| --- | --- | --- |
| Reference | Median DummyRegressor | Prior/majority DummyClassifier |
| Family A: linear baseline | LinearRegression | LogisticRegression, initially unweighted |
| Family B: tree baseline | DecisionTreeRegressor | DecisionTreeClassifier |
| First complexity increase | RandomForestRegressor | RandomForestClassifier |
| Optional, evidence-dependent | Ridge or XGBoostRegressor | Class weights or XGBoostClassifier |
| Optional third family | Ensemble only if justified | Soft voting or regression-to-classification stacking |

Reference dummy predictors are comparison controls. Use two substantive families
initially; do not require every optional algorithm. Every added complexity must
be compared against its simpler baseline on the same evaluation population.

For linear models, use median numeric imputation with missingness indicators,
selected nonnegative `log1p` transforms, and StandardScaler. Use categorical
imputation and OneHotEncoder with documented reference/unknown handling.
Tree pipelines need imputation and categorical handling but not scaling.
Choose transformations using development CV, not the final test.

Tune a small predeclared search space: for example tree depth/minimum leaf size,
forest depth/minimum leaf size/max features, and logistic regularization strength.
Record candidate settings, scoring, folds, seeds, and compute budget. Report CV
mean and standard deviation; fold variability is not a confidence interval.

## 5. Evaluation protocol

### Primary course comparison

1. Create a deterministic customer-group split manifest before fitting anything.
   Reserve approximately 20% as a protected holdout, approximately stratified for
   review labels; the contract defines how unlabeled orders share this assignment.
2. Use only development data for model selection. Classification uses five-fold
   StratifiedGroupKFold; regression uses five-fold GroupKFold. All groups use
   `customer_unique_id`, not `customer_id`.
3. Fit the entire preprocessing/model pipeline inside each fold. Compare candidates
   on the same task-specific rows and folds.
4. Choose the final configuration and generate development OOF probabilities for
   threshold selection. These support development decisions, not an unbiased
   performance claim after tuning. The protected holdout provides that assessment.
5. Freeze model choice, feature list, threshold, and any calibration. Refit on all
   eligible development rows and evaluate once on the holdout.

This evaluates held-out customers in the historical snapshot. It does not prove
performance on future orders. Save assignments rather than regenerating different
partitions in each script.

### Metrics and success criteria

- Regression: primary MAE in days, plus RMSE, R², residual plots, and errors by
  state, basket size, and duration band. Compare against median and linear baselines.
- Classification: primary average precision (AP; explicitly identify this PR summary),
  ROC-AUC, precision, recall, F1, confusion matrix, and precision/recall at a
  predeclared review capacity. Accuracy is supplementary, not forbidden.
- Report classification prevalence and constant-score AP baseline on each population.
- Select additional complexity only if development evidence improves the chosen
  metric/operating trade-off enough to justify its cost. If it fails, retain the
  simpler model and report the negative result.
- If probabilities drive decisions, inspect reliability plots and Brier score.
  Class weighting is an experiment, not a guarantee of calibrated probabilities.
  Compute any negative/positive weighting ratio within each training fold.
- Select the operational threshold using development OOF predictions. A 5:1
  false-negative/false-positive cost ratio is an illustrative assumption. Compare
  1:1, 2:1, 5:1, and 10:1 or use a documented review-capacity constraint.
  Save the chosen threshold with the model; never tune it on holdout outcomes.

### Optional temporal robustness check

Specify calendar windows before evaluating performance. July–August 2018 is a
candidate, not an approved fixed window. Training requires outcome availability
before the training cutoff, not merely purchase before cutoff. In the audit,
1,705 orders purchased before July were delivered in July or later.

Use a documented label-follow-up horizon, snapshot cutoff, and customer-overlap
policy. Under the current disjoint-customer contract, exclude overlapping customers
from temporal evaluation and report how this changes its population. Do not call
the result representative of returning customers. Calendar validation is not
stratified; retain the stratified primary comparison for the brief and report
temporal prevalence separately.

### Optional history and stacking

Seller outcome histories need both event-time availability and fold isolation.
The baseline feature builder must not export globally computed target-derived
histories. A checkout-time filter alone cannot protect random CV.

For stacking, each outer classifier-training partition must generate its own inner
OOF regression predictions. Refit the regressor only on eligible outer-training
orders to predict the outer validation partition. Do not reuse one global OOF
column across classifier CV. Compare with/without `T_pred` on identical rows.
All reviewed classification orders may need predictions even if they lack a
regression target; document the resulting extrapolation risk.

## 6. Connection to taught material

Paths below are relative to the supplied course/tutorial folders, not dependencies
required to clone or execute this repository.

| Material | Application |
| --- | --- |
| Tutorial 3, `T03.ipynb` | SimpleImputer, scaling, nominal encoding, Pipeline and ColumnTransformer. |
| Tutorial 4, `T04.ipynb` / filled notebook | Train/test separation and reusing fitted preprocessing. Review text remains excluded because it is unavailable at checkout. |
| Tutorial 5, `T05.ipynb` | Linear/multiple regression, residuals, heteroscedasticity and R². |
| Course W6, `ML-deployement-necessary_files/Model/L6.1_Fraud_Detection_Training.ipynb` | Haversine engineering, RF/XGBoost pipelines, optional voting, model serialization and metadata. |
| Course W6, `L6_Model_Deployment_Slides.md` and bulk-scoring lab | Reusable inference contract and saved feature schema; deployment itself is primarily Milestone 3. |
| Tutorial 7, `Logistic_Regression_Standard_Solution_non_agentic.ipynb` | Protected holdout, whole-pipeline CV, OOF threshold choice, coefficient interpretation, pipeline plus threshold artifact. |
| Course W7, `Classification_01_Updated.pdf` | Logistic probabilities/odds, classification metrics and cost-dependent decisions. |

Adapt teaching examples to Olist's groups, observation times, and missing outcomes.
The fraud lab's weighting is not mandatory for review classification. Tutorial 7
provides an unweighted probability-model starting point. A matching mean predicted
probability and prevalence alone is not sufficient evidence of calibration.

## 7. Interpretation and literature

Use linear coefficients with units/reference categories and stability caveats,
plus validation-set permutation importance for selected models. SHAP is optional.
Feature importance is predictive association, not proof of causation.

The [project brief](references/IT5006%20Project%20Description%20-%20AY%202026_27%20Semester%201.pdf)
is the requirements source. The six papers in `docs/references/` motivate delivery,
reviews, tabular models, and leakage/calibration checks; they do not validate our
unbuilt pipeline.

Corrected interpretation: Deshpande and Pendem estimate a 13.3% increase in average
daily seller sales in a specific Tmall scenario reducing three-day deliveries to
two days. This is not a universal 13.3% sales loss per day of delay. Do not transfer
that number, or Cui et al.'s setting-specific effects, directly into an Olist ROI
claim. The imbalance paper evaluates resampling methods and does not establish
that weighted losses preserve calibration.

Delivery point estimates do not justify promised delivery windows without separate
coverage/interval validation. Do not describe purchase-to-delivery time as pure
seller-to-customer transit; it also includes pre-dispatch processing.

## 8. Deliverables and implementation order

1. Feature contract, reproducible base table, eligibility report and split manifest.
2. Notebook `notebooks/04_ml_feature_engineering.ipynb`, delegating reusable code
   to `src/features/build_features.py` and `src/features/create_splits.py`.
3. Training/evaluation scripts in `src/models/` and
   `notebooks/05_model_training_and_evaluation.ipynb`.
4. Baseline and tuned model comparisons, errors, calibration/threshold analysis,
   interpretation, and limitations.
5. Optional extensions only after the baseline workflow passes validation.
6. Complete pipeline/threshold artifacts under `artifacts/models/`; metrics under
   `artifacts/metrics/`; schemas, feature lists, input hashes, environment versions,
   fold assignments, random seeds and configuration recorded alongside them.

Suggested 6–8 page allocation: problem/stakeholder and scope (1 page), data and
features (1–2), models and validation (1–2), results/interpretation (2), limitations
and recommendations (1). Include GitHub link, reproducible code, figure/table labels,
and AI-use declaration. Do not fill result tables with projected performance.
