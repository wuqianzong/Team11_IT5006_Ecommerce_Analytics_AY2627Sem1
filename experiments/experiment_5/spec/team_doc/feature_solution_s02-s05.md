# Feature solution — stages s02 to s05 (frozen)

Oct 17, 2026 · @B

**Frozen on 17 Oct 2026** for implementation. s02–s05 are approved and committed as AGREED blueprints in `experiments/experiment_5/spec/blueprints/`; any further change goes through a CHANGELOG change request. The one decision left open by design (the 95% or 99% threshold, plus the collinearity drops) is made at the human gate after s03.

This is the full solution from raw data to cross-validation folds, merged from the team's feature solution doc, the frozen design and the pipeline audit. Walk it top to bottom: every row has a decision ID from the decision log and a Review cell to mark Approved or Change.

## How to review

- Each stage is a table of steps in run order. **Review** cell: Approved, or Change plus a comment on the row.
- Decision IDs (G-xx) point to `spec/blueprints/decision_log.md` in the repo, which records why each choice was made.
- No Milestone 2 result or metric is used: every count, threshold, cutoff and score is recomputed in Experiment 5, and every decision rests on those new numbers (G-29). Milestone 2 code may be reused as logic, never its outputs.
- When every row of a stage is Approved, its tag in the Pipeline v2 chart moves from IN REVIEW to APPROVED. The stage's blueprint file is then written and committed as AGREED.

## s02 — Data preprocessing (one table for both tasks)

Output: one row per order, with IDs for audit, the 24 contract predictors (e5lib/contract.py, G-61), both targets with their label-available times, and every exclusion counted. Nothing is learned from data except the outlier threshold, which uses pre-cutoff orders only.

| # | Step | Solution | Basis | Review |
| --- | --- | --- | --- | --- |
| 2.1 | Load | Canvas copy of the 9 Olist tables; sha256 of each file in `data_hashes.json` | Brief: use the Canvas copy | Approved |
| 2.2 | Clean | Declared types; ZIP prefixes kept as strings (leading zeros); categorical domain checks logged, rows kept; geolocation exact duplicates dropped (counts recomputed and logged). No imputation | Milestone 2 cleaning notebook | Approved |
| 2.3 | Geography | ZIP centroids = median lat/lng per ZIP prefix and state, after the IBGE Brazil boundary filter (archive hash recorded) | `docs/references/geography` | Approved |
| 2.4 | Join | Orders ← customers (many-to-one on `customer_id`); items, payments and reviews aggregated to `order_id` first, then left-joined one-to-one; key-uniqueness and merge-cardinality checks; output rows = orders | Milestone 2 `aggregation.py`, `geography.py`; Milestone 1 TA (joins) | Approved |
| 2.5 | Predictors | The 24 predictors of e5lib/contract.py (G-61; has\_items, freight\_ratio\_missing and payment\_missing are not in the contract and are not built): basket (items, products, sellers, categories), price and freight, physical totals and missing fractions, primary category and seller state, distance, interstate share, calendar, payment | Milestone 2 feature formulas; contract written for Experiment 5 (G-61) | Approved |
| 2.6 | Targets | `lead_days` = delivery − purchase in fractional days (delivered, valid, > 0), available at delivery. `is_detractor` = minimum valid review score ≤ 2, available at the last review answer; first-review label kept for a sensitivity check | Design s01; Milestone 1 TA (label bias) | Approved |
| 2.7 | Leakage audit | Every column tagged known / not known at checkout. Delivery dates, `order_status` and review fields are never predictors; `order_estimated_delivery_date` is known at checkout but is never a predictor: in production the promised date would come from the task 1 prediction (G-35). It is used only to describe late-vs-promised trends in s03. Also never predictors, because they are only known after purchase: order\_approved\_at, shipping\_limit\_date, has\_items and freight\_ratio\_missing (post-purchase leakage: both encode a later cancellation). payment\_missing is known at checkout but excluded as constant, because 2.11 removes every order without a usable payment (G-42, G-51). Date-order audit on every order: purchase ≤ approval ≤ carrier ≤ delivery, estimated date > purchase, review answer > purchase; violations are logged, and an order whose delivery is not after purchase leaves regression (2.6). Payment fields carry no timestamp, so "chosen at checkout" is a stated assumption. Final order\_status is used only to define populations (2.8), never as an input (G-30) | Brief leakage warning; audit #11 | Approved |
| 2.8 | Populations | Zero-item orders out of both tasks. Regression: delivered orders with a valid lead time. Classification: orders not cancelled or unavailable, with a valid review; targets never imputed. Stated as a scope limit in the report | G-20 | Approved |
| 2.9 | Outliers | Removed as suspected data-entry errors, in development and test alike: `lead_days` > max(100, mean + 12 × SD of pre-cutoff orders); `distance_km_max` > 4,397.53 km. Threshold and removal counts computed in s02 and logged. The lead-time rule removes orders from regression only, the distance rule from both tasks (G-66) | G-21 (team instruction) | Approved |
| 2.10 | Missing installments | Orders with missing `payment_installments_max` removed (count logged); the app rejects the same input | G-20 | Approved |
| 2.11 | Missing payment | Orders without a usable payment (no payment rows, or only the not\_defined payment type) removed from both tasks (count logged); the app rejects the same input. payment\_missing is then always 0 and is excluded as constant | G-51 (audit 3) | Approved (team, audit 3) |
| 2.12 | Data documentation | Generated by the s02 code, following the NIBRS model the teacher shared. data\_dictionary.csv: one row per column of the 9 raw tables and of records.csv.gz, with type, nullable, grain, source, meaning of a missing value (missing / zero / unknown / not applicable), known at checkout, eligibility and a comment. figures/data\_structure.png: the tables, their keys and one-to-many links, and the aggregate-first join to one row per order. Used by the report, the s04 feature dictionary and the s10 app input checks | G-58; docs/references/NIBRS; Milestone 1 TA (joins) | Approved (team, CR-023) |
| 2.13 | Negative values | Orders with a negative value in a log1p candidate (total\_price, total\_freight, total\_weight\_g, total\_volume\_cm3, distance\_km\_max) removed from both tasks; zero kept, missing values stay missing. Every s02 removal rule writes exclusions.csv rows with step, reason\_code and reason\_description, one description per code pre-registered in protocol.yaml (G-63) | G-62, G-63 (s01 review) | Approved (team, s01 review) |

Files: `records.csv.gz`, `exclusions.csv` (one row per removed order and reason, with step, reason\_code and reason\_description; G-63), `data_hashes.json`, `audit.json`.

## s03 — EDA (per task, pre-cutoff orders only)

EDA uses only orders purchased before the task's test cutoff (computed in s02), so no choice sees test outcomes. Every figure has a sidecar data file, and everything is saved under `stages/s03_eda/<task>/outputs/` (never `artifacts/`).

| # | Analysis | Solution | Output | Review |
| --- | --- | --- | --- | --- |
| 3.1 | Regression target | `lead_days` KDE; count, mean, SD, min, 1/5/25/50/75/95/99%, max, skewness, kurtosis | `target_regression_lead_days.csv` | Approved |
| 3.2 | Classification target | `is_detractor` bar chart; counts, share of low reviews (≤ 2) and normal reviews (≥ 3) | `target_classification_is_detractor.csv` | Approved |
| 3.3 | Trends over time | By purchase month: median lead time, late-vs-promised rate, detractor rate, with counts (not volume only) | `outcome_trends.csv` | Approved |
| 3.4 | Numeric features vs `lead_days` | Scatter plot per feature; Pearson **and** Spearman (skewed features); full percentile profile; sorted by absolute correlation | `numeric_feature_target_lead_days.csv` | Approved |
| 3.5 | Categorical features vs `lead_days` | Violin plots (median, IQR, outliers); one-hot (drop-first) correlations; calendar fields treated as categorical for plots only | `categorical_feature_target_lead_days.csv` | Approved |
| 3.6 | Numeric features vs `is_detractor` | KDE per class with overlap coefficient (0% = perfect separation, 100% = no signal) and per-feature ROC-AUC on the same rows | `numeric_feature_target_is_detractor.csv` | Approved |
| 3.7 | Categorical features vs `is_detractor` | Mutual information (`mutual_info_classif`, discrete, seed 42) | `categorical_feature_target_is_detractor.csv` | Approved |
| 3.8 | Importance ranking | One ranking per task feeding s04 selection, over all 24 contract predictors (the ranking file has exactly 24 rows; G-42, G-61): absolute Spearman for regression, mutual information for classification (one measure per task, so cumulative shares are meaningful). Missingness, outliers and correlation/VIF among raw numeric features also reported here | `importance_ranking.csv`, `eda_summary.json`, `candidate_rationale.csv` | Approved |

Human gate (G-31): implementation stops after s03. All EDA results are presented to the team, and s04 runs only after the team records its decisions (threshold, collinearity drops). The ranking measure in 3.8 is my recommendation: the team doc listed several measures, but only one per task can be summed to a 95% or 99% share.

## s04 — Features (per task, defined, not fitted)

s04 writes recipes and feature lists; nothing is fitted here. Steps 4.3 and 4.4 are the two declared exceptions to fold-fitting (design rule 2), both on pre-cutoff orders only.

| # | Step | Solution | Basis | Review |
| --- | --- | --- | --- | --- |
| 4.1 | Baseline | The 24 predictors of e5lib/contract.py (G-61; has\_items, freight\_ratio\_missing and payment\_missing are not in the contract: the first two leak a later cancellation, payment\_missing is constant after 2.11; G-30, G-42, G-51); `purchase_month`, `purchase_dayofweek`, `purchase_hour` numeric | G-02, G-22 (fixes the Milestone 2 string/numeric bug) | Approved |
| 4.2 | Transforms | log1p only for the five contract candidates total\_price, total\_freight, total\_weight\_g, total\_volume\_cm3, distance\_km\_max, each with pre-cutoff skewness > 1; freight\_ratio, counts, calendar fields, 0/1 indicators and 0–1 shares never logged; missing values stay missing through log1p and are imputed afterwards (G-47, G-62); log1p regression target. No target cap: extreme values are handled by the s02 outlier removal and the log target | G-22, G-25 | Approved |
| 4.3 | Reduction (label-free) | Drop constant and duplicate features automatically. Highly collinear features are only flagged, by cut-offs pre-registered in `protocol.yaml` (\|correlation\| > 0.9 or VIF > 10); for each flagged group the team decides which feature to drop, and the decision and its rationale are recorded in reduction\_rationale.csv and written into the report. Then report the encoded design-matrix rank and condition number per recipe | G-11, G-26, audit #4 and #6 | Approved |
| 4.4 | Selection (EDA ranking) | Keep features in s03 ranking order until the cumulative share reaches the team's threshold (95% or 99%), fixed before any model is fitted. CV scores of the chosen set will be somewhat optimistic; the report says so | G-19 (team choice) | Approved |
| 4.6 | Rationale | Each kept feature: formula, grain, checkout availability, missingness, hypothesised signal, verified citation | Teacher note §3; Milestone 1 TA | Approved |
| 4.7 | Selected set | One selected set per task, used by every model family (G-49) | G-02 | Approved |
| 4.8 | Pipeline recipe | Per family: median imputation + missing indicators, except distance\_km\_max, which takes the route median (customer\_state × primary\_seller\_state; fallback customer\_state, then global; after log1p) learned in each training fold; one-hot with unknown handling (drop-first for linear/logistic only); scaling for linear/logistic only; fitted later inside folds | T3–T4, T7 §5 | Approved |

4.5 (promised lead days) was removed on 18 Oct (G-35). Rows 4.6–4.8 keep their numbers so existing references stay valid.

Files: `feature_dictionary.csv`, `selected_features.json`, `recipes.json`.

## s05 — Partition (per task; needs only s02)

The test cohort is held out by time, no test customer is ever seen in training, and the five folds respect time, customers and label timing.

| # | Step | Solution | Basis | Review |
| --- | --- | --- | --- | --- |
| 5.1 | Order | Sort each task's eligible orders by purchase timestamp, earliest first | Team doc | Approved |
| 5.2 | Test cohort | Newest 20% per task, computed fresh: the cutoff is the purchase timestamp at the 80% position of that task's eligible orders (after the s02 row-local population rules, before the outlier rule; G-67). It is computed in s02, recorded in protocol.yaml (data-dependent layer), and the exact IDs are frozen in `test_manifest.csv`. The cohort is defined only by this experiment's data and rules and is a new held-out test (G-38) | G-23 | Approved |
| 5.3 | Test-side purge | Remove test orders whose `customer_unique_id` also appears in development (count logged). The test cohort is then new customers only, named a "new-customer time-ordered holdout" and always stated with its actual share of eligible orders after the purge and the share the purge removed (G-48) | G-18 (team choice) | Approved |
| 5.4 | Test checks | Per task (G-46): regression test keeps at least 15% of eligible delivered orders; classification test keeps at least 15% of eligible reviewed orders and at least 15% of all eligible detractors; train–test prevalence gap reported. On failure: alert the team and stop, never a random split | G-23; teacher pitfall | Approved |
| 5.5 | CV folds | Five time-ordered expanding folds on development (`TimeSeriesSplit` style, equal-sized validation blocks); boundary dates recorded in `protocol.yaml` (data-dependent layer). Anti-temporal-leakage rule: in every fold, training holds only orders purchased before the validation block starts, never later ones; asserted per fold (max training purchase time < min validation purchase time) | G-23 (expanding chosen by team), G-14 | Approved |
| 5.6 | Fold customer purge | In each fold, training orders whose customer\_unique\_id appears in that validation block are removed, so no customer is on both sides, as at the test boundary; asserted per fold (no shared customer\_unique\_id between training and validation, counts logged) | Teacher note §2; Milestone 2 | Approved |
| 5.7 | Label maturity | A label counts only from the moment it was observable: lead\_days at the delivery timestamp, is\_detractor at the last review answer. Training rows: keep an order only if its label was observable before its fold's validation block starts. Validation rows: keep an order only if its label was observable before the task's test cutoff. Rows dropped by this rule are counted per fold | Label-timing leakage rule; audit #2 | Approved |
| 5.8 | Class support | Both tasks: every fold's training part holds at least the minimum number of rows pre-registered in protocol.yaml (G-53). Classification also: positives and prevalence per fold, training and validation; minimum count pre-registered in `protocol.yaml`; a boundary may move only before s06 runs, logged in CHANGELOG | G-14 | Approved |

Files: `folds.csv`, `test_manifest.csv`, `counts.json`, `checks.json`. Seed 42 is recorded with them.

## What later stages inherit

These parts of the feature solution land outside s02–s05. They are recorded now and will be reviewed with those stages.

| Stage | Inherits | Decision |
| --- | --- | --- |
| s06 Training | The feature set, input logs and log target are fixed here from EDA and used by every model (log1p on the five contract candidates with skewness > 1, G-47, G-62, and on the regression target); they are not tested on the folds | G-19, G-25, G-36 |
| s08 Selection | Test metrics: regression MAE, RMSE, R², share within ±3 days; classification AP (= PR-AUC, reported once), ROC-AUC, Brier, confusion matrix, precision/recall/F1 at the threshold, illustrative cost, prevalence baseline. Bundle stores the training-data profile (numeric distributions, category shares) for drift checks | G-24 |
| s10 Release | App input checks reject what s02 removes (no items, missing installments, impossible distance) and warn when inputs drift from the training profile | G-20, G-24 |

## Open items for the team

Each item has my recommended answer; tick it when agreed, or comment.

- [ ] **Cumulative-importance threshold (4.4):** pick 95% or 99% once the s03 ranking exists, before any model is fitted. Implementation stops after s03: every EDA table and figure is shown to the team, which decides this threshold and the collinearity drops (4.3) before s04 runs (G-31). Recommended: 95%, with 99% only if 95% drops a feature the EDA shows to be clearly useful.
- [x] **Ranking measure (3.8):** absolute Spearman for regression, mutual information for classification.
- [x] **Pre-registered cut-offs (4.2, 4.3):** log1p if skewness > 1 (the five contract candidates only, G-47, G-62); flag a feature if |correlation| > 0.9 with another feature or VIF > 10; the team decides what to drop (G-26).
- [x] **Classification population (2.8):** orders not cancelled or unavailable with a valid review, stated as a scope limit.
- [x] **Validation-label timing (5.7):** validation labels available before the task's test cutoff.
- [x] **Fold boundaries (5.5):** equal-sized validation blocks by order count (`TimeSeriesSplit`), not Milestone 2's equal calendar windows; dates recorded in `protocol.yaml`.

## Decision IDs used in this tab

Full entries, with who raised each and why, are in `experiments/experiment_5/spec/blueprints/decision_log.md`.

| ID | Decision |
| --- | --- |
| G-02 | Start from the 24-predictor contract (G-61), reduce, then select one set per task by the EDA ranking (G-19), used by every model; one cycle instead of Milestone 2's 9 → 11/12 |
| G-11 | 24 contract predictors (G-61) → core reduction is a label-free rule on pre-cutoff orders (declared exception to fit-in-folds) |
| G-13 | s03 checks collinearity on raw features; encoded design-matrix rank checked in s04 and s06 |
| G-14 | `protocol.yaml` has two layers: pre-registered (s01) and data-dependent (owned by s04 and s05) |
| G-36 | Log transforms always on, from EDA (inputs with skewness > 1 and the regression target); s06 compares model families only |
| G-35 | `order_estimated_delivery_date` (promised lead days) is never a feature or a reference model; it only describes late-vs-promised trends in s03 |
| G-18 | Repeat customers removed from the test set, not from development |
| G-19 | Feature selection by one EDA importance ranking per task, threshold fixed before fitting |
| G-20 | Populations: no zero-item orders; classification = not cancelled/unavailable with a review; missing installments removed |
| G-21 | Outlier removal: `lead_days` > max(100, mean + 12 SD), distance > 4,397.53 km |
| G-22 | Calendar fields numeric; log1p when skewness > 1, for the five contract candidates only (G-47, G-62) |
| G-23 | Test = newest 20% (cutoff computed fresh in s02, G-28), per-task 15% checks (G-46), no random fallback, five expanding folds |
| G-24 | Test metric list and training profile for drift checks |
| G-25 | No target cap: extreme lead times are handled by the s02 outlier removal and the log target (supersedes G-03) |
| G-26 | Collinear features are flagged by pre-registered cut-offs; the team decides which to drop, with the rationale recorded and reported |
| G-27 | Missing distance filled with the route median (customer × seller state), fitted inside training folds, with the missing indicator kept |
| G-28 | Test cutoff recomputed per task by the 80/20 rule in s02 (not assumed from Milestone 2) |
| G-29 | No Milestone 2 result or metric is reused; all numbers are recomputed in Experiment 5 (code logic may be reused) |
