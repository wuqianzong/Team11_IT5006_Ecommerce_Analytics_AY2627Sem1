# Feature set suggestion and implementation contract

Status: recommended baseline v1, specified for teammate/agent implementation.
Updated: 2026-10-02. This document specifies intended behavior; no feature builder
or evaluation result is implied to exist.

Read the [ML guideline](README.md) and
[proposal](../../../docs/milestone2_proposal.md). Preserve the current
`raw -> preprocessed -> business` architecture. Input tables below always refer
to files under `data/preprocessed/`.

## 1. Current problems and required resolution

| Current problem | Resolution |
| --- | --- |
| Task 2 alternates between reviewed and delivered-and-reviewed orders. | Baseline classification uses all valid reviewed orders; regression uses valid delivered orders. Export separate eligibility flags. |
| 12.85% and 6.78 are treated as universal prevalence/weight. | They describe the earlier delivered-reviewed population. Compute class proportions per cohort and any weights per training fold. |
| Multiple items/sellers are compressed without exact rules. | Aggregate before joins; define primary item, distinct-seller geography, and counts below. |
| Minimum review is justified by dashboard consistency. | Define the target as any recorded negative review, independently of dashboard logic. Report review-selection sensitivity. |
| State features are reduced to is_SP without evidence. | Keep state categories in v1; compare state/region simplifications on development folds only. |
| Freight is dropped as allegedly linearly collinear with price and ratio. | Retain all as candidates; inspect stability and ablation performance. The relationship is multiplicative. |
| Approval delay is renamed dispatch delay. | Preserve distinct event definitions. Do not use either current-order duration at checkout. |
| Global seller histories are assumed safe after a time filter. | Outcome-derived histories must also respect fold membership and label/event availability. Exclude from baseline. |
| One OOF regression column is assumed safe for any classifier CV. | Rebuild the regression stage within outer classifier folds. Exclude from baseline. |
| Median/scale/category preprocessing is incompletely specified. | Fit learned transforms inside folds; preserve raw-unit deterministic features and missingness in exports. |
| GroupKFold is described as the final test and as time-safe. | Maintain an outer holdout manifest and separate inner fold manifest. Temporal evaluation is a distinct protocol. |
| Pipeline/model artifacts omit the operating threshold. | Serialize threshold, positive class, feature schema and data/split versions with the pipeline. |
| Business effects and PASS labels are stated before validation. | Report hypotheses, assumptions and actual checks; no invented scores, ROI or leakage guarantees. |

Audit context, before final eligibility filtering: 99,441 orders; 9,803 multi-item
orders; 1,278 multi-seller orders; 547 orders with multiple reviews. Recompute and
record these during implementation rather than hardcoding acceptance counts.

## 2. Grain, population and deterministic joins

Start from orders, not order items. Preserve exactly one row per source
`order_id`, including orders with missing items/reviews. Require a unique non-null
order key; fail on ambiguous source duplicates rather than silently dropping them.

Join customer records many-to-one on `customer_id`; retain
`customer_unique_id` for grouping. Validate uniqueness of product, seller and
translation keys before joins. An unmatched dimension creates missing features
and a quality flag, not an inner-join deletion.

Items are unique on (`order_id`, `order_item_id`). Join products and sellers
many-to-one, then aggregate items to orders before adding reviews/payments.
Collapse reviews and payments independently to order grain. No item × payment ×
review Cartesian multiplication is allowed.

Primary item: sort within order by price descending (missing last), then numeric
`order_item_id` ascending. Use its category and seller state. For an order with
items but all prices missing, choose the lowest item ID and flag price missing.
No items means missing primary attributes.

Sort exported rows by `order_id` with a fixed column order and fixed null/date
serialization. Preserve IDs and five-digit postal prefixes as strings.

## 3. Column roles and target contract

| Column | Role and rule |
| --- | --- |
| `order_id`, `customer_id`, `customer_unique_id` | Identifier/audit only; never predictors. |
| `prediction_timestamp` | Purchase timestamp; audit/splitting only. Do not encode raw timestamp or IDs as numeric predictors. |
| `lead_days` | Nullable float target: elapsed seconds from purchase to customer delivery / 86400; delivered status and strictly positive interval required. |
| `review_score_min` | Nullable integer target source: minimum valid score 1–5 across supplied reviews. Not a feature for either task. |
| `is_detractor` | Nullable integer target: 1 for minimum score <=2; 0 for minimum score >=3; null if no valid score. |
| `eligible_regression` | Delivered status, valid positive lead_days, valid prediction time and resolved customer group. Not a predictor. |
| `eligible_classification` | Valid review target, valid prediction time and resolved customer group. Delivery status is not an eligibility requirement. |
| `regression_exclusion_reason`, `classification_exclusion_reason` | Deterministically ordered reason codes, not predictors. Preserve multiple reasons if applicable. |
| `regression_label_available_at` | Customer delivery timestamp for valid regression outcomes; audit only. |
| `review_latest_observed_at` | Maximum valid answer timestamp across contributing valid reviews; audit proxy, not proof that no future review can arrive. |
| `review_count`, final status and outcome timestamps | Audit only. Never current-order predictors. |

Use one vocabulary: `lead_days`, `is_detractor`, `review_score_min`; do not mix
`detractor` and `is_detractor`. Valid scores remain available for snapshot labels
when their response date is missing, but such rows cannot supply history or support
a temporal-label claim without a documented availability rule.

Quarantine malformed scores and impossible dates in quality reporting. Do not
copy the dashboard's blanket timestamp exclusions; a carrier/approval inconsistency
does not automatically invalidate the purchase-to-delivery target. Report it
separately. Missing predictors normally use pipeline imputation, not row deletion.

Snapshot minimum-review target: “any recorded negative review in this data copy.”
Its observation window varies and eventual non-review is unknown.

For an optional temporal experiment, define a new target version with a fixed
follow-up horizon H days and a documented observation cutoff. Use reviews answered
after purchase and within H days. A negative becomes observed at its first qualifying
negative response; conservatively treat all training labels as mature only after
purchase + H, with that maturity before the model-fit cutoff. A zero requires at
least one valid in-window review and completion of the horizon; no review stays
unknown. Report excluded/unmatured orders. Do not pretend the largest timestamp in
a file establishes complete follow-up. If the observation cutoff cannot be justified,
report that temporal classification is not validated.

Regression temporal training also requires delivery before the fit cutoff.
Never label an unobserved delivery as zero duration or discard long deliveries
just to improve error metrics.

## 4. Baseline feature contract

All features below are candidates for both tasks unless stated otherwise. Store
untransformed values. The schema must record a role, dtype, unit, source columns,
formula, aggregation grain, missingness rule, availability assumption, and phase
(base, pipeline-fitted, or fold-specific) for every column.

| Feature(s) | Exact derivation and unit | Missing/invalid handling |
| --- | --- | --- |
| `n_items` | Count item rows per order. Each source item row is one unit; do not multiply by order_item_id. | Zero if no item rows; add `has_items`. |
| `n_products`, `n_sellers` | Distinct non-null product/seller IDs among items. | Zero if none; flag unresolved identifiers. |
| `n_categories` | Distinct resolved translated categories, excluding Unknown. | Zero if none; retain category-missing fraction. |
| `total_price`, `total_freight` | Sum item price / freight_value in BRL, each item once. | Negative/nonfinite values invalid. Null total if no items or any required component is invalid/missing; report invalid fractions. |
| `freight_ratio` | total_freight / total_price. | Null if denominator <=0 or either total missing; add `freight_ratio_missing`. Never fill infinity with zero. |
| `total_weight_g` | Sum item product_weight_g, counting repeated products once per item row. | Nonpositive/nonfinite weights invalid; null total if any item weight missing/invalid or no items. |
| `total_volume_cm3` | Sum per-item product_length_cm × product_height_cm × product_width_cm. | All three dimensions must be positive/finite; null total if any item volume unknown or no items. |
| `weight_missing_fraction`, `volume_missing_fraction` | Number of invalid/unknown item measurements / n_items. | Null for no items; has_items distinguishes absence. |
| `primary_category` | English category of deterministic primary item. | Explicit Unknown for missing/untranslated categories, with quality count. |
| `category_missing_fraction` | Fraction of items lacking resolved category. | Null for no items. |
| `customer_state` | Customer table state. | Normalize whitespace/case; invalid state -> Unknown plus quality flag. |
| `primary_seller_state` | Seller state of deterministic primary item. | Unknown for absent/unresolved state. |
| `distance_km_mean`, `distance_km_max` | Mean/max Haversine distance from customer to each distinct seller, equal weight per seller, km. | Null aggregate if any required seller/customer coordinate unresolved. Retain distance_missing_fraction. |
| `distance_missing_fraction` | Distinct sellers with unresolved distance / n_sellers. | Null if no sellers. |
| `interstate_share` | Fraction of distinct sellers whose state differs from customer state. | Null if customer or any seller state unresolved, or no sellers. Do not treat unknown as intrastate. |
| `purchase_month`, `purchase_dayofweek`, `purchase_hour` | Purchase timestamp components: 1–12, 0–6 (Monday=0), 0–23. Treat as categorical in v1. | Null if timestamp invalid. Preserve source clock convention; do not invent timezone conversions. |
| `primary_payment_type` | Sum valid payment_value by normalized type; choose largest total, ties lexicographically by type. | Unknown if no usable payment. Payment snapshot availability is an assumption. |
| `payment_installments_max` | Maximum positive recorded instalments across usable payment rows. | Zero/nonfinite/missing -> null; flag. Do not interpret zero as a legitimate no-instalment observation without evidence. |
| `n_payment_methods` | Distinct usable payment types. | Zero if no usable payment; retain payment_missing indicator. |

Usable payment rows: recognized source payment type and finite positive
payment_value. Flag excluded payment records rather than silently rewriting raw
data. Do not count payment totals as item revenue. Check source payment key
(`order_id`, `payment_sequential`) and fail/report duplicates.

Do not claim payments are proven known at order_purchase_timestamp: the payments
table lacks event timestamps. Define the baseline as the checkout-complete
simulation and include this assumption in both report and inference schema.
Compare a no-payment feature variant if its operational availability is uncertain.

### Geography lookup

Use the preprocessed geolocation reference, independent of labels. Keep valid
finite coordinates within latitude [-90, 90] and longitude [-180, 180]; flag
additional plausible-country checks separately. Build median latitude/longitude
per zero-padded ZIP prefix and normalized state; use that composite key for customer
and seller lookup. Missing matches stay missing; no invented coordinates.

Record the reference hash and acknowledge static geography as an assumption.
With radius 6371 km, apply Haversine in radians and clip its floating-point
intermediate to [0,1]. Unit checks must distinguish degrees, radians and kilometers.
Do not claim this is route distance or a historically versioned geolocation service.

## 5. Secondary feature experiments

Implement only after baseline validation; compare on the same folds.

| Candidate | Contract / reason to defer |
| --- | --- |
| Primary photo count | `product_photos_qty` of primary item; nonnegative count; null if missing. No synthetic zero. |
| Primary description length | `product_description_lenght` of primary item; nonnegative character-count proxy. No review text. |
| Region pair | Explicit Brazilian region lookup covering North, Northeast, Central-West, Southeast and South. Compare against states; do not automatically replace states with is_SP. |
| Density | total_weight_g / total_volume_cm3 only with complete, valid totals. Collinearity/interpretability check required. |
| Top-category grouping | Learn frequency ranking inside training folds; retain other categories as Other and missing as Unknown. No global top-10 selection. |
| Seller history | Fold-specific definitions below. Not exported in baseline table. |
| Predicted lead time | Fold/model-specific `T_pred`, not a physical observation. Nested construction below. |

Do not create a “high-defect category” flag from full-data negative-review rates.
Outcome-derived category encodings require the same fold and availability controls
as seller histories. Hand-defined fragility groupings are hypotheses and must have
a documented mapping and validation, not a claim of observed defects.

Catalogue attributes have no historical versions. Acknowledge this limitation
rather than certifying all recorded descriptions/photos as known at checkout.

## 6. Fold-specific seller history (optional)

Build order–seller pairs once so one multi-item order does not count repeatedly for
the same seller. An order-level review is an order experience, not a seller-specific
rating; attributing it to each participating seller is an explicit assumption.

For a scored order at time t, permitted sources must:
- belong to the current training partition (never validation/holdout);
- be a different order from the scored order;
- have purchase time < t;
- have the relevant outcome event observed strictly before t; and
- for frozen temporal scoring, also have the event before the fit cutoff.

For training-row histories, exclude the current order and use earlier observable
training records only. For validation rows, freeze the permitted source partition;
do not update it using validation outcomes. Rebuild this process for every CV fold.
Any global prior used for cold starts must respect both fold and time availability.

Recommended initial history:
- `seller_hist_review_count`: distinct prior reviewed orders per seller.
- `seller_hist_review_mean`: mean of each prior order's minimum review score
  among responses available by t, not its eventual minimum.
- Aggregate across distinct sellers using equal-weight mean, with
  `seller_history_missing_share`. Unknown means remain null; counts are zero.
  Pipeline imputation may supply a fallback; never treat zero stars as “no history.”

Optional approval latency is approval minus purchase, available at approval.
Optional dispatch latency is carrier handover minus purchase, available at handover.
Use separate accurate names. Negative/missing intervals are excluded with counts.
Do not rename approval latency to dispatch latency or invent a dispatch SLA.

A portable history transformer/cache must retain training-source identifiers,
timestamps, fold version and source hashes. Verify that no held-out outcome appears
in its lineage.

## 7. Split manifest and training contract

Baseline outer assignment:
1. Resolve customer_unique_id for all orders. Missing groups receive excluded
   assignment and reason; never fill them with one shared dummy customer.
2. For resolved groups, use three split-only strata: negative review, nonnegative
   review, and unknown review. Unknown is not a model class.
3. Use StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42) on this
   population; preselect fold 0 as the approximate 20% holdout. Assign all remaining
   groups to development. Do not choose a fold based on model scores.
4. Persist one outer assignment per order, then apply task eligibility. Report
   resulting sizes, class balance, and group disjointness for each task.
5. Within development eligible rows, create task-specific five-fold manifests:
   StratifiedGroupKFold for classification, GroupKFold for regression. Use stable
   order sorting; record library versions and seed where applicable.

Group constraints make exact 80/20 proportions and exact class ratios impossible
in general. Check both classification classes in each partition and validation
fold. If unsupported, stop and document a reduced-fold configuration; do not
silently fall back to random rows.

Immutable holdout assignment applies to both models. No task may use holdout
customers' alternative outcomes to train the other task.

Use train-fitted numeric imputation and categorical handling. In the linear
baseline, StandardScaler follows imputation and any selected log1p transform.
Validate nonnegative inputs before logs. Select nominal encodings explicitly;
arbitrary numeric state codes must not imply a ranking. Report unseen categories.
Feature selection/ablation, transformations and clipping all remain development
decisions.

Predictions and target arrays join by order_id, not by incidental row position.
Never impute labels. Never cap or remove true long-duration test labels to make
the regression score better.

## 8. Cascaded prediction contract (optional)

Within each outer classification development fold:
1. Restrict all regression training sources to outer-training customer groups.
2. Generate inner OOF regression predictions for eligible regression-training
   orders. For classification-training orders with no regression label, generate
   predictions from models excluding their customer group and all outer-validation
   groups. Record this extrapolation population explicitly.
3. Train the classifier using only outer-training features and these predictions.
4. Refit regression on eligible outer-training orders, predict outer-validation
   orders, and evaluate the classifier there.
5. Any preprocessing, history construction or hyperparameter search follows
   the same nested boundary.

Before final holdout scoring, create development-only OOF inputs for final classifier
training and fit the final regressor on eligible development data. Both exclude all
holdout groups. Persist base-regressor version, fold IDs and predictions. A global
OOF column reused across outer classifier folds fails this contract.

Compare against a classifier without T_pred on identical classification rows.
Do not quietly restrict the cascade to delivered orders. If that scope is chosen,
version the cohort and rerun its baseline explicitly.

## 9. Acceptance checks and agent handoff

Implement reusable logic in `src/features/`, explained by
`notebooks/04_ml_feature_engineering.ipynb`. Resolve repository paths portably.
Use these checks before publishing outputs:

- Source hashes and source/output row counts recorded; one output row per source
  order, unique non-null order_id, stable content on rerun.
- Keys and join cardinalities asserted; two items × two payments × two reviews
  still produce one order row with correct item totals.
- Fixture for multi-seller geography verifies distinct-seller weighting and max.
- Primary-item and payment ties produce the documented deterministic result.
- Null/invalid dimensions, zero price, absent payments/items, unmatched ZIPs and
  unknown categories produce the documented missing values/flags.
- Missing review stays null; reviewed non-delivered orders remain classification
  candidates; delivered unreviewed orders remain regression candidates.
- Feature allowlists have empty intersection with targets, identifiers, outcome
  fields, eligibility/audit metadata and split columns.
- Outer/inner customer groups do not overlap; both classification classes present;
  task rows use their intended manifest and no holdout fits occur.
- Pipeline fit learns imputation/encoding/scaling only from the fold's training data.
- Optional history fixture: an earlier purchase with a later review cannot enter
  history before that review; validation-source reviews never enter training history.
- Optional temporal fixture: pre-cutoff purchase with post-cutoff delivery is not
  an available regression training label at cutoff.
- Optional cascade fixture records regression source groups and checks their
  disjointness from the outer validation groups.
- Reloaded final pipeline and saved threshold reproduce predictions and decisions.

Deliver base builder, schema/manifest generation, split builder, meaningful small
fixtures/checks, and an execution README. Summarize exclusions and assumptions.
Do not fabricate data, performance results or timestamps. Do not edit raw/baseline
source tables, change dashboard behavior, add unnecessary model families, or commit
without the user's instruction.

## 10. Implementation priority

1. Deterministic baseline features, task labels, schema and quality report.
2. Shared holdout and task-specific CV manifests.
3. Dummy, linear/logistic and decision-tree pipelines; then Random Forest.
4. Development metrics, interpretation, threshold selection and saved artifacts.
5. Optional listing attributes, weighting or XGBoost through controlled comparisons.
6. History, temporal robustness and stacking only after their stricter contracts
   can be implemented and verified within the remaining project time.
