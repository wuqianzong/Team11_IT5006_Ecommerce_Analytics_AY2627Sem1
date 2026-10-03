# ML dataset guideline

Status: implementation specification v1.1, revised 2026-10-04.

Read this document together with the [feature contract](feature_contract.md),
[proposal](../../../docs/milestone2_proposal.md), and
[data architecture](../../../docs/data_architecture.md). The architecture owns
directory/lineage rules; this guideline and the feature contract own detailed ML
rules. The processing-plan PDFs and Feature Baseline v1.0 PDF are discussion inputs;
this revised contract incorporates their review and teammate geography feedback.

## Locked v1.1 implementation decisions

- Only `distance_km_max` is a baseline distance predictor. Do not export primary
  or mean seller distance. The maximum is a geographic-difficulty proxy, not proof
  that the farthest parcel is last to arrive. No correlation >0.99 is assumed.
- Filter points against the pinned IBGE Brazil polygon before computing coordinate
  medians by five-digit ZIP prefix and state. A bounding box is insufficient.
  Median reduces outlier influence; it does not guarantee a true location.
- Null distance when any required seller/customer location is unresolved. Retain
  the order and record missingness; never use a smaller partial maximum.
- Physical totals require all item measurements; otherwise null them and retain
  missingness fractions. Zero-price orders remain, with a null freight ratio.
- Keep customer and primary-seller state and interstate_share. Section 4 of the
  contract freezes the exact predictor allowlist and PDF-name mapping.
- Require a valid score for classification and positive fractional-day duration
  for regression. IDs, status, outcomes and eligibility flags are audit/target
  columns, never predictors.
- Listing features are secondary. Seller outcome histories and stacking remain
  deferred until their stricter contracts are implemented.

## 1. Lineage and scope

`data/preprocessed/*.csv -> src/features/ -> data/business/ml/`

The notebook `notebooks/04_ml_feature_engineering.ipynb` explains and calls reusable
code. ML must not read `data/raw/` or `data/business/dashboard/`. Do not import
dashboard-specific date clipping, review collapsing, or order exclusions implicitly.

Build one row per source order. Keep deterministic checkout aggregates reusable
across tasks, but fit task-specific models on task-specific eligible rows.
Preserve source files and existing dashboard behavior.

The sole additional reference is the pinned IBGE country polygon specified in
the contract's Geography lookup section. Stage it and `boundary_manifest.json`
under `docs/references/geography/`; the archive is not supplied by this revision.
Record the actual source URL, edition, SHA-256, CRS and geometry transformation.
This is a documented, label-independent geographic quality-control exception to
the preprocessed-only rule. Do not alter raw Olist inputs or import other external
predictors.

Build with cached local geometry. A missing reference, missing CRS, invalid
geometry or checksum mismatch must fail clearly; no silent bounding-box fallback
or runtime downloads. Boundary-inclusive coverage, retained islands, zero buffer,
coordinate-median revalidation and coverage-loss reporting are mandatory.
The contract defines exact steps and the historical-boundary limitation.

## 2. Artifacts and column roles

| Artifact | Contract |
| --- | --- |
| `orders_ml_features.csv` | Shared order-level base; identifiers, deterministic predictors, targets and eligibility/audit columns have explicit roles. No scaled values, seller outcome histories or model predictions. |
| `feature_schema.json` | Versioned columns, roles, types, units, formulas, availability assumptions, missingness rules and task feature allowlists. |
| `dataset_manifest.json` | Input hashes, target/feature versions, configuration, row counts, exclusions and deterministic content checksum. Separate volatile run timestamps from content identity. |
| `split_assignments.csv` | One row per order: customer group, split version, and development/holdout/excluded assignment with reason. |
| `cv_assignments.csv` | One row per task and eligible development order: validation fold and split version. |
| `quality_report.json` | Contract checks, missingness, join cardinalities and cohort counts. Required failures stop publication. |
| `zip_centroids.csv` | Versioned ZIP/state median lookup after country filtering, with coordinate counts, status and boundary version; unresolved keys retained. Not a model-input table. |

Optional `train.csv` and `test.csv` are derived exports, never independent sources of
split membership. Fold-specific history or prediction caches require task, fold,
model/configuration version and source-partition provenance.

Training must use explicit feature allowlists. Never infer predictors with
`drop(target)` or “all numeric columns.” Quarantine both targets, all review scores,
eligibility flags, IDs, split labels, raw timestamps and outcome-derived measures.
IDs remain available for joins, grouping, and audit only.

## 3. Tasks and label scope

- Regression: delivered orders with valid purchase/delivery timestamps and strictly
  positive elapsed duration. No review requirement. Output `lead_days`.
- Classification: any order with a valid review score in 1–5, irrespective of
  eventual delivery. Output `is_detractor` using the minimum valid score.
  Missing reviews have a null target, never zero.
- Both tasks additionally require a valid purchase time and resolved customer group
  for evaluation. Preserve ineligible rows and exclusion reasons in the base table.
- Minimum-score labels mean “any recorded negative review.” They do not mean first
  or final review. Record observation-window limitations and label availability.
- Do not make shared features depend on delivery/review eligibility.

Detailed rules, including temporal-label restrictions, are in the feature contract.

## 4. Time and preprocessing constraints

Prediction cutoff: `order_purchase_timestamp`. Checkout payment/seller allocation
and catalogue attributes have unverified snapshot-availability assumptions; record
them and provide a no-payment sensitivity run if needed.

Current-order approval, shipping/handover and customer-delivery timestamps,
shipping-limit dates, review text/timestamps/scores, final order status, delivery
duration and late/on-time flags are not baseline predictors. Estimated-delivery
promises are excluded from version 1; adding them needs a named availability and
business-use experiment.

Export deterministic values in original units. Imputers, encoders, top-category
selection, scalers, data-driven clipping and feature selection must be fitted inside
each training fold. Numeric missingness must not silently become zero in aggregates.
Unknown categories must be handled and logged.

## 5. Split and evaluation contract

Use a shared customer-group development/holdout manifest, approximately stratified
by review class, before model fitting. The feature contract specifies the handling
of unknown labels. Every order belonging to one `customer_unique_id` receives the
same outer assignment.

Within development: five-fold StratifiedGroupKFold for classification and GroupKFold
for regression. Reuse task folds across model comparisons. Fail clearly if the
population cannot support the requested folds or both classification classes.

Holdout outcomes must not drive transformation choices, model selection, calibration,
or threshold tuning. Publish final holdout scores after choices are locked.
Development OOF scores used for selection are not an independent final estimate.

Temporal evaluation is optional and separate. It requires chronological and
label-maturity checks; GroupKFold alone is not temporal validation. Maintain the
current disjoint-customer requirement and report any overlap exclusions.

## 6. Optional extensions

Historical seller outcomes require event availability before the scored purchase
AND permitted training-source membership. Build them per fold, never globally.
Specify cold-start counts/fallbacks. A scaler pipeline does not protect a
precomputed history feature.

`T_pred` belongs to training outputs, not the base table. Classifier outer folds
must enclose regression fitting and inner OOF construction. Compare with and without
it on identical rows. Detailed requirements are in the feature contract.

Class weighting, XGBoost, temporal validation, voting and stacking are optional.
Begin with simple linear/logistic and tree baselines. Do not hardcode class weights.

## 7. Handoff and artifact requirements

Implementation order:

1. Read contract sections 2–4; stage/check the boundary reference and provenance.
2. Implement portable reusable modules under `src/features/` for geometry lookup,
   item/payment/review aggregation, targets and base export. Explain execution in
   `notebooks/04_ml_feature_engineering.ipynb`.
3. Export the base table, lookup, schema, manifest and quality report. Apply the
   exact common predictor allowlist; secondary features require versioned variants.
4. Build shared outer and task-specific inner split manifests per contract section 7.
5. Run contract section 9 checks, including country filtering, incomplete distances,
   missing physical totals, review eligibility and multiplication-safe joins.
6. Hand off commands, input requirements, dependency versions, actual output counts,
   missingness/coverage, exclusions and test results to both model teams.

The implementation should expose a repository-root CLI such as
`python -m src.features.build_features` followed by
`python -m src.features.create_splits`; document actual arguments, boundary setup
and validation commands when implemented. Pin compatible GIS dependencies if used.
Do not claim these entrypoints already exist. Training can proceed only once
required dataset checks pass. No model fitting is required merely to build features.

Before training, pass every required check in the feature contract. Save pipelines
with feature names/order, positive class, threshold, target/cohort version, split
version, dependency versions, configuration and metrics. Reload and verify
predictions and threshold decisions.

Generated datasets and models are implementation outputs, not deliverables of this
documentation revision. Do not claim a plan has passed leakage checks before the
implementation and its assertions exist. Keep implementation changes uncommitted
unless explicitly instructed to commit.
