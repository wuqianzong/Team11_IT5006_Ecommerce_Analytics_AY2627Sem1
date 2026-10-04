# Feature set suggestion and implementation contract

Status: implementation contract v1.2, incorporating tutorial-aligned implementation
and acceptance requirements. Updated: 2026-10-04.
The v1.1 builder and split implementation exist but have outstanding review findings.
This revision is a specification, not certification that those findings are fixed.
The 27-column base feature definitions remain v1.1; record contract_version=v1.2
separately. Version changed data, lookup or split artifacts explicitly and regenerate
their dependent manifests; do not silently relabel existing outputs as verified.

Read the [ML guideline](README.md) and
[proposal](../../../docs/milestone2_proposal.md). Preserve the current
`raw -> preprocessed -> business` architecture. Input tables below always refer
to files under `data/preprocessed/`. The only additional input is the pinned,
label-independent Brazil boundary reference specified below. This is a documented
geographic quality-control exception, not an additional transactional data source.

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
| Mean ZIP coordinates can be distorted by erroneous locations. | Filter coordinates against a pinned Brazil country polygon before computing ZIP/state coordinate medians. Audit exclusions and lost coverage. |
| Three seller distances duplicate single-seller information. | Keep only `distance_km_max` as the baseline distance predictor. |
| The baseline PDF leaves zero-price rows “dropped or imputed.” | Retain the order, null the ratio and impute within folds. Missing predictors alone do not cause task exclusion. |
| The baseline PDF proposes partial physical sums. | Use complete totals plus missingness fractions; a partial sum must not masquerade as a total. |
| The baseline PDF permits a review record without a valid score. | Require at least one valid integer score in 1–5; otherwise the label remains null. |

Audit context, before final eligibility filtering: 99,441 orders; 9,803 multi-item
orders; 1,278 multi-seller orders; 547 orders with multiple reviews. Recompute and
record these during implementation rather than hardcoding acceptance counts.
The prior audit found 98,666 orders with items, of which 1,278 were multi-seller:
approximately 98.7% of item-bearing orders were single-seller. Recompute the
denominator explicitly. Primary, mean and maximum distances coincide for complete
single-seller orders, but this does not establish full-sample correlation >0.99.

Maximum distance is a parsimonious geographic-difficulty proxy. The farthest seller
need not dispatch or deliver last. Carrier choice, processing and routes also
matter; an order-level delivery timestamp does not establish the responsible
parcel. Mean distance is a valid summary, not a truck route. Its omission is a
simplicity decision, not proof that it is meaningless.

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
Use UTF-8 and explicit LF line endings for generated CSVs. Hash the actual canonical
files distributed with the repository, not a pre-Git CRLF representation. Record
the byte-hash algorithm and newline convention; verify hashes after a clean checkout.

Serialized floats keep full float64 precision without rounding. Content hashes are
byte-exact for integer/string/categorical/date columns. Floating-point columns
(Haversine `arcsin`/`sqrt`, coordinate medians) can differ at the ~1e-12 level
across platforms and math backends, so verify float equality with a documented
numerical tolerance — `atol=1e-9` and `rtol=1e-9` in each column's native unit
(km, g, cm³, BRL, days, fractions) — instead of demanding bit-identical bytes.

Fixed order-local sums, ratios and date components may be computed before splitting.
Determinism alone is not a leakage guarantee: a globally fitted median imputer or
category ranking is deterministic but still forbidden. ZIP medians are a separate
frozen reference lookup, not order-local features; see the reference assumption in §4.

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
| `distance_km_max` | Maximum Haversine distance from customer to each distinct seller, km; the only baseline distance predictor. | Null if no sellers, an item seller ID is missing, or any required seller/customer coordinate is unresolved. Never take a partial maximum. |
| `distance_missing_fraction` | Distinct sellers with unresolved distance / n_sellers. | Null if no sellers. |
| `interstate_share` | Fraction of distinct sellers whose state differs from customer state. | Null if customer or any seller state unresolved, or no sellers. Do not treat unknown as intrastate. |
| `purchase_month`, `purchase_dayofweek`, `purchase_hour` | Purchase timestamp components: 1–12, 0–6 (Monday=0), 0–23. Treat as categorical in v1. | Null if timestamp invalid. Preserve source clock convention; do not invent timezone conversions. |
| `primary_payment_type` | Sum valid payment_value by normalized type; choose largest total, ties lexicographically by type. | Unknown if no usable payment. Payment snapshot availability is an assumption. |
| `payment_installments_max` | Maximum positive recorded instalments across usable payment rows. | Zero/nonfinite/missing -> null; flag. Do not interpret zero as a legitimate no-instalment observation without evidence. |
| `n_payment_methods` | Distinct usable payment types. | Zero if no usable payment; retain payment_missing indicator. |

Usable payment types are `credit_card`, `boleto`, `voucher`, and `debit_card`,
normalized to lowercase after trimming. Other types, including `not_defined`,
are unusable and counted. Usable payment rows require finite positive
payment_value. Flag excluded payment records rather than silently rewriting raw
data. Do not count payment totals as item revenue. Check source payment key
(`order_id`, `payment_sequential`) and fail/report duplicates.

Do not claim payments are proven known at order_purchase_timestamp: the payments
table lacks event timestamps. Define the baseline as the checkout-complete
simulation and include this assumption in both report and inference schema.
Compare a no-payment feature variant if its operational availability is uncertain.

### Geography lookup: required algorithm

1. Read preprocessed geolocation; source tables stay unchanged. Filtering applies
   only to the ML lookup.
2. Normalize state to uppercase and ZIP prefix to a five-digit string. Accept
   integer-valued numeric prefixes or digit strings of length 1–5, zero-pad them,
   and reject other forms. Never create a ZIP for missing data.
   Valid states: AC, AL, AP, AM, BA, CE, DF, ES, GO, MA, MT, MS, MG, PA, PB, PR,
   PE, PI, RJ, RN, RS, RO, RR, SC, SP, SE, TO.
3. Reject invalid keys, then nonnumeric/nonfinite coordinates, then latitude
   outside [-90,90] or longitude outside [-180,180]. Record mutually exclusive
   first-failure reasons in this order.
4. Apply the country polygon below using longitude as x and latitude as y. Keep
   points inside or on its boundary. A rectangular coordinate range is insufficient:
   it also covers neighboring countries and ocean.
5. Group surviving rows by (ZIP prefix, state). Compute latitude median and
   longitude median independently, with equal weight per surviving preprocessed
   row. Do not deduplicate further or weight by order frequency.
6. Check the median point against the same polygon. Coordinate-wise medians can
   fall outside nonconvex polygons; mark such lookups unresolved. Do not silently
   snap to a coast, substitute a mean, or invent a nearest ZIP.
7. Left-join customers/sellers by the composite lookup key. A ZIP with no surviving
   coordinates stays unresolved. No city/state-centroid fallback in v1.1.
8. Build distinct (order_id, seller_id) pairs and calculate their customer distances.
   Repeated seller items do not multiply distances. Publish the maximum only if
   all seller IDs and required coordinates resolve. Otherwise null it and retain
   the order for pipeline imputation.

Median is robust to a minority of extreme values; it neither identifies every bad
point nor guarantees the true neighborhood center. Country filtering cannot remove
wrong coordinates that still lie within Brazil.

### Boundary reference and provenance

Use the country polygon from the pinned
[IBGE BR_Pais_2024.zip](https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2024/Brasil/BR_Pais_2024.zip).
The [official directory](https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2024/Brasil/)
identifies this national product. It is specified, not bundled by this documentation
change. The implementing agent must stage the original archive and provenance under
`docs/references/geography/`, leaving the nine raw Olist tables untouched.

Record URL, product year, retrieval time, actual archive SHA-256, original CRS,
geometry-selection rule, library versions, transformation and derived geometry hash
in `boundary_manifest.json`. Honor source attribution/redistribution terms. Never
invent a checksum or silently upgrade the edition.

Read the declared CRS and fail if absent. Transform the country geometry to
EPSG:4326, union all country parts, and retain supplied islands. Validate nonempty,
valid geometry; invalid geometry requires an explicit documented repair. Use
boundary-inclusive coverage, e.g. Shapely `covers`; do not silently simplify or
buffer. The initial policy has zero buffer. Resolution/GPS error can exclude
legitimate coastal/border points, so report coverage loss.

Suggested tools: GeoPandas for file/CRS handling, Shapely for vectorized coverage;
record compatible versions in requirements. Build against the cached local
reference; no implicit runtime download. Missing/unreadable reference or hash
mismatch must fail, not fall back to a bounding box. Another source, buffer or
edition requires a new feature version and rationale.

The 2024 country polygon is a static plausibility reference for 2016–2018 orders,
not a historical administrative reconstruction. Disclose this external-reference
assumption in the report. Do not assert every rejected point is proven erroneous.
The ZIP lookup also assumes the supplied geolocation reference is available to the
simulated system. It is aggregated reference data, not a training-fitted imputer and
not proof of historical availability. Freeze and hash it independently of task splits;
never use holdout outcomes to select its policy. A stricter historical lookup requires
a separately versioned experiment with an evidenced reference-availability rule.
On every build, including cached-geometry paths, verify actual reference hashes,
declared CRS and geometry validity before use. A hardcoded expected hash is not
evidence that the supplied file matches it.

### Haversine and audit outputs

Use radius 6371 km and convert degrees to radians:
`a = sin²(delta_lat/2) + cos(lat_customer)*cos(lat_seller)*sin²(delta_lon/2)`.
Clip a to [0,1], then `distance = 2*6371*arcsin(sqrt(a))`.
Require finite nonnegative results; do not round intermediate calculations.
These are straight-line distances, not observed travel times or road distances.

Save `zip_centroids.csv` under `data/business/ml/` with ZIP, state, accepted
coordinate count, median lat/lon, resolution status and boundary version. Include
every valid source key, even if all its coordinates were rejected (null coordinates
and zero accepted count). Sort by ZIP/state. Hash the lookup and boundary inputs.
The quality report must include:

- reference counts before/after each filter and first-failure reason;
- keys with zero survivors or out-of-country median points;
- customer/seller coverage before and after filtering, using the same valid-key
  denominator (before = key with at least one globally valid coordinate);
- zero/one/multiple-seller order counts and their denominators;
- order distance completeness, and missingness rates by state and task eligibility;
- boundary edition/CRS and implementation library versions.

Do not use holdout outcomes to select geographic filtering policies.

### Exact predictor allowlist and baseline-PDF migration

Use this shared list for both tasks initially; task-specific removals need a named
development ablation:

```text
n_items, has_items, n_products, n_sellers, n_categories,
total_price, total_freight, freight_ratio, freight_ratio_missing,
total_weight_g, total_volume_cm3, weight_missing_fraction,
volume_missing_fraction, primary_category, category_missing_fraction,
customer_state, primary_seller_state, distance_km_max,
distance_missing_fraction, interstate_share,
purchase_month, purchase_dayofweek, purchase_hour,
primary_payment_type, payment_installments_max, n_payment_methods, payment_missing
```

`has_items = int(n_items > 0)`;
`freight_ratio_missing = int(freight_ratio is null)`;
`payment_missing = int(no usable payment rows)`.
Counts are nonnegative integers; flags are 0/1; continuous values/fractions are
nullable floats; states/category/payment are categorical strings; time components
are nullable integers encoded as categories. Unlisted quality flags are audit-only.
Primary photo count and description length remain optional secondary features.

Missing item seller IDs mean the complete seller set is unknown: set maximum
distance, distance_missing_fraction and interstate_share to null and record
`seller_id_missing` as an audit flag. Otherwise distance_missing_fraction is the
unresolved distinct-seller count / n_sellers; missing customer coordinates make all
seller distances unresolved. With no sellers, distance and fraction are null.

| Baseline PDF name | Canonical implementation / action |
| --- | --- |
| `order_purchase_timestamp` | `prediction_timestamp` in export; preserve source name in lineage. |
| `is_task1_eligible`, `is_task2_eligible` | `eligible_regression`, `eligible_classification`. |
| `detractor` | `is_detractor`; retain `review_score_min` as target-source metadata. |
| `seller_state` | `primary_seller_state`. |
| `distance_max_km` | `distance_km_max`, the only distance predictor. |
| `distance_km`, `distance_mean_km` | Omit; also omit old repo `distance_km_mean`. |
| `is_interstate` | `interstate_share`; this changes meaning, not merely naming. |
| `n_distinct_products` | `n_products`. |
| `sum_weight_g`, `sum_volume_cm3` | `total_weight_g`, `total_volume_cm3` with complete-total semantics. |
| `weight_missing`, `volume_missing` | Missingness fractions, not binary-any-missing flags. |
| `payment_method_primary`, `max_installments` | `primary_payment_type`, `payment_installments_max`. |
| `purchase_weekday` | `purchase_dayofweek`, Monday=0. |
| `description_length`, `photos_count` | Optional `primary_description_length`, `primary_photos_count`. |

Do not export duplicate aliases. Normalize once and give both model teams the same
schema and manifests. Highest-price primary-item ties use smallest numeric item ID.
Payment-type total ties use lexicographic type, not an undefined aggregate sequence.

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

Tutorial 3 demonstrates binning and polynomial interactions; Tutorial 5 demonstrates
nonlinear regression and residual-led transformations. These are options, not a
requirement to enlarge the baseline. No binning, polynomial expansion, PCA or
row-wise normalization in the first baseline. A named experiment may use selected
nonnegative log1p predictors, selected numeric interactions or learned bins if
development evidence motivates it. Fit learned parameters within training folds;
compare identical task rows and folds, record configuration and negative results,
and obtain team approval before changing the baseline. Do not expand all one-hot
columns into polynomials or automatically remove correlated predictors.

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
2. For orders with resolved groups, use three per-order split-only strata: negative
   review, nonnegative review, and unknown review. Unknown is not a model class.
   Sort by order_id before splitting; pass order rows and their strata with
   groups=customer_unique_id. Do not collapse customers to one row or use an
   "any negative review wins" customer-level stratum.
3. Use StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42) on this
   population; preselect fold 0 as the approximate 20% holdout. Assign all remaining
   groups to development. Do not choose a fold based on model scores.
4. Persist one outer assignment per order, then apply task eligibility. Report
   resulting sizes, class balance, and group disjointness for each task.
5. Within development eligible rows, create task-specific five-fold manifests:
   StratifiedGroupKFold for classification, GroupKFold for regression. Use stable
   order_id sorting; record library versions and seed where applicable.

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

Default preprocessing for the first reproducible baseline:
- Categorical columns are customer_state, primary_seller_state, primary_category,
  primary_payment_type, purchase_month, purchase_dayofweek and purchase_hour.
  Convert time codes to consistent category strings; use an explicit Unknown
  missing token and OneHotEncoder(handle_unknown='ignore'). For the linear
  baseline use drop='first' and record reference categories and the fact that an
  unseen value can encode like the reference. Record unknown-category counts.
- All other allowlisted columns are numeric. Use training-fold median imputation
  with missingness indicators and keep_empty_features=True; a wholly missing
  training column therefore retains its position with the imputer's documented
  zero fallback and indicator, never a claimed observed value. Version/persist
  transformed feature names. Scale numeric columns for linear/logistic models;
  use unscaled imputed numbers for trees.
- No log transform, top-10 grouping or clipping in the first baseline. These are
  named development experiments rather than per-agent choices. No precomputed
  medians/scales or encoded dummy columns in orders_ml_features.csv.

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
- Geography fixtures reject a European point and an ocean/foreign point inside the
  bounding rectangle but outside the polygon; accept a covered boundary point.
  A mixed-validity ZIP uses only accepted coordinates; an all-rejected ZIP remains
  unresolved. Verify CRS, coordinate order and post-median coverage.
- Distance fixtures: coincident points give zero; one seller gives its distance;
  multiple sellers give the maximum; duplicated seller items do not change it;
  missing required coordinates yield null, not a smaller partial maximum.
  Assert primary/mean distance columns are absent from exports and allowlists.
- Physical fixtures: two items with one missing measurement give null total and
  missingness fraction 0.5; all-missing/no-item cases never yield misleading zero
  totals. A zero price preserves the row and yields a null ratio.
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

## 11. Tutorial-aligned implementation and evidence contract

### 11.1 Stage boundaries and tutorial interpretation

The sequence is: define contract -> build fixed base features -> create approved
outer/inner manifests -> optionally construct fold/time-safe histories -> fit the
complete preprocessing/model pipeline within each training fold. Histories are
optional: the baseline proceeds directly from manifests to pipeline fitting.

Tutorial 3 explicitly uses the whole dataset for a preprocessing-only demonstration.
Do not copy that fitting scope into supervised evaluation. Tutorial 4's train-only
fit/reused transform rule and Tutorial 7's reference/agentic workflow govern training.
Keep customer-group isolation rather than copying the labs' ordinary row splits.
Do not adopt review-text features from the spam exercise: they are unavailable at
checkout. Tutorial synthetic datasets and results are teaching examples, never
project inputs or evidence.

### 11.2 Required feature audit (after split approval)

The feature notebook must import reusable modules, not maintain embedded copies of
their full implementation. Add a development-only audit, separately for the two
eligible task populations, containing:

- column roles, dtypes and units; missing counts and percentages with denominators;
- numeric count, mean, standard deviation, min, quartiles and max; constant columns;
- category frequencies and class counts/proportions;
- distributions of key price, weight, volume, distance and duration variables;
- numeric predictor correlations and selected feature/target relationships;
- written observations identifying possible skew, redundancy and coverage problems,
  with evidence and proposed experiments, not automatic feature deletion.

Full-population integrity, eligibility and split-balance checks remain permissible.
Do not use holdout feature/target relationships to choose features or transformations.
These audits do not impute, scale, clip or drop rows in the base CSV. A quality
report with row counts alone does not satisfy the exploratory evidence requirement.

### 11.3 Reusable training interface (later training phase)

Implement preprocessing/model factories under src/models/ and explain their use in
notebooks/05_model_training_and_evaluation.ipynb. Select X by the explicit task
allowlist and select y/groups/manifests separately, joined by order_id. Build a
name-based ColumnTransformer with remainder='drop', then the estimator as the last
step of a single Pipeline. Apply §7's categorical and numeric defaults. For trees,
use one-hot encoding with drop=None; no numeric scaling. For linear/logistic models,
retain drop='first' and save the reference categories. Use sparse encoding when
practical; dense conversion requires a documented memory check, not a lab copy-paste.

The categorical missing token is Unknown, not the tutorial's most-frequent fill:
this is an intentional project choice preserving missing-category meaning. Normalize
calendar codes consistently (e.g. integer 1 and 1.0 must not become distinct levels).
Retain all 27 input columns, including constant or wholly missing training columns;
any approved removal is a named variant. Missingness-indicator output columns may
differ between folds, but each fitted pipeline must have stable transform dimensions
and persisted feature names. Do not compare coefficients across folds by position.

CV and hyperparameter search receive the entire pipeline and original-unit X, never
a matrix transformed before CV. Convert saved validation-fold assignments to index
pairs using the aligned task rows; do not silently recreate random folds. A fresh
pipeline is fitted per fold. Validation and holdout receive transform/predict only.
Neither a scaler nor a Pipeline makes a globally precomputed seller history safe.

### 11.4 Input-validation contract and acceptance fixtures

Validate both base exports and incoming model features. Required predictor columns
must be present, but an allowed null cell is not a missing column. Reorder columns
by name; exclude non-allowlisted metadata from X. Preserve source files.

At the model-input boundary, fail clearly on missing columns, malformed numeric
values, infinities, fractional counts and invalid ranges. At base-source ingestion,
retain the existing per-field missing/quarantine rules and report rejected values;
do not turn every malformed source value into an unreported zero. Valid numeric
nulls continue to the fold-fitted imputer. Enforce:

- counts: nonnegative integers; flags: 0/1;
- price/freight/distance/ratio: nonnegative finite values when present;
- complete weight/volume and known installments: strictly positive when present;
- missingness fractions and interstate_share: [0,1];
- month 1–12, weekday 0–6, hour 0–23; identifiers and targets never in X.

Malformed state/payment tokens follow §4's normalization to Unknown with a quality
flag/count. A valid category unseen in training is different from a malformed value:
allow it through the configured encoder, count it and disclose the possible all-zero
encoding/reference collision. Domain vocabularies come from the contract; fitted
category vocabularies come only from training, not a full-data reference dataframe.

Add executable tests for missing required columns, reordered columns, wrong types,
infinities, negative counts/prices, out-of-range fractions/calendar codes, legitimate
nulls, unseen categories and a wholly missing training column. Verify that changing
validation values or labels cannot change training-fitted imputation statistics,
scaler parameters or encoder categories. Assert identical reordered-column predictions,
finite transformed numeric values, stable per-pipeline feature names/dimensions and
equality of predictions/threshold decisions after artifact reload.

Base/split tests gate base/split publication now. Pipeline and scoring fixtures gate
training artifacts later; report them as deferred, not passed, until implemented.
Build outputs in staging, run required checks, and publish only on success. A failed
build must leave the previous published dataset/manifests intact. Test that behavior.
Exercise the actual production geography function on a boundary point. Test Cartesian
join safety with the two-item/two-payment/two-review fixture, not a hardcoded pass.
A review with no valid score must have a null label even if review_count is positive.

### 11.5 Model diagnostics, decisions and persistence (later training phase)

Start logistic regression with class_weight=None and no resampling. Weighted models
remain separate development experiments, not automatic imbalance fixes. Follow the
Tutorial 7 reference/agentic approach where T07_Main differs on weighting or uses
test predictions for a threshold sweep. Retain the proposal's primary AP metric,
ROC-AUC, majority-baseline accuracy and threshold-dependent precision/recall/F1;
regression retains MAE, RMSE, R² and development OOF residual plots. Accuracy is
supplementary, and beating it is not the sole definition of business usefulness.

Choose thresholds using development OOF probabilities; freeze feature/model choices,
any calibration and the threshold before final holdout scoring. Mean predicted
probability versus prevalence is only a preliminary calibration check: also report
reliability plots and Brier score when interpreting probabilities. Any fitted
calibrator must use development-only, group-respecting validation. State positive
class is_detractor=1 and retrieve that class's probability explicitly.

Retrieve transformed names from the fitted pipeline and assert alignment with
coefficients. Explain standardized numeric coefficients separately from categorical
reference comparisons; report associations, not causal effects. Before claiming a
feature matters, inspect correlations and a same-fold ablation or stability analysis.
Perform all feature refinement before opening the final holdout. Business costs,
capacity constraints and the operational threshold require a team decision; do not
borrow the tutorial's banking costs or claim measured intervention benefits.

Save pipeline, threshold, validation policy, feature names/references, positive class,
task/contract/feature/split versions, dependency versions, seeds and selection evidence.
Reload without fit and reproduce predictions and decisions. Keep a decision record
of target/feature/metric/threshold choices, rationale, evidence and team approval;
agents must not silently change these choices.
