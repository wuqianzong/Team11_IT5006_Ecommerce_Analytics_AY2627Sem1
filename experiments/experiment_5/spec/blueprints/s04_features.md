# s04_features — blueprint

| Field | Value |
| --- | --- |
| Stage | s04_features (`../pipeline_design.md` → s04) |
| Nodes | regression, classification |
| Status | AGREED |
| Owner | TBD |
| Last agreed | 2026-10-18 (4.5 deleted, CR-015; audit 2, CR-021); first agreed 2026-10-17 (team walkthrough, doc tab "Feature solution (s02–s05)") |
| Discussion | Claude Doc "Milestone 3 pipeline stages", tab "Feature solution (s02–s05)", section s04 |

## 1. Goal and gate
Goal: define, without fitting, each task's feature list, transforms and pipeline recipe.
The threshold and collinearity drops come from the team via `spec/human_decisions.yaml` (G-31).
Gate: features and recipes defined without fitting or using test data (`../stages.json`).

## 2. Inputs
- `stages/s02_data/common/outputs/records.csv.gz` (pre-cutoff, task-eligible rows only).
- `stages/s03_eda/<task>/outputs/importance_ranking.csv` (regression; it covers exactly the pool) and, for
  classification, `candidate_ranking_extended.csv` (24 predictors + 12 screening candidates), plus the raw
  collinearity tables. The ranking s04 walks is the task's pool, `e5lib.contract.pool(task)`: the rows of
  the extended ranking whose feature is in the pool, with the shares re-normalised to sum to 1 (each
  feature's mutual information is computed on its own, so filtering is exact; CR-042, audit H-02).
- `spec/protocol.yaml`: skewness trigger (1.0), collinearity cut-offs (|r| > 0.9, VIF > 10).
- `spec/human_decisions.yaml` (G-31): the team's cumulative-importance threshold (95% or 99%) and
  the feature dropped from each flagged collinear group, with rationale, recorded after reviewing
  `eda_review_pack.md`. s04 stops if these are missing.

## 3. Method
1. **Baseline (4.1).** The 24 predictors of `e5lib/contract.py` (G-61; `has_items`,
   `freight_ratio_missing` and `payment_missing` are not in the contract: G-30, G-42, G-51); `purchase_month`, `purchase_dayofweek`,
   `purchase_hour` numeric (G-22). The classification adds the three candidates adopted at the s03 gate (G-70): product_photos_qty, product_description_lenght, seller_prior_review_mean.
2. **Transforms (4.2).** log1p only for the contract's candidates `total_price`, `total_freight`,
   `total_weight_g`, `total_volume_cm3`, `distance_km_max`, each when its pre-cutoff skewness > 1;
   for classification also `product_description_lenght` (same skewness rule; pre-cutoff skewness 2.04 in s03 3.10); `product_photos_qty` (a count) and `seller_prior_review_mean` (a 1–5 rating) are never logged (G-70);
   `freight_ratio`, counts, calendar fields, 0/1 indicators and 0–1 shares are never logged
   (G-47, G-62); missing values stay missing through log1p and are imputed afterwards; the final list is in `feature_dictionary.csv`;
   log1p regression target (`TransformedTargetRegressor`, inverse expm1). No target cap (G-25).
3. **Reduction (4.3).** Drop constant and duplicate columns automatically. Flag features with
   |correlation| > 0.9 or VIF > 10; the team decides which of each flagged group to drop and
   records the decision and rationale in `reduction_rationale.csv` (G-26). Report the encoded
   design-matrix rank and condition number per recipe. The duplicate rule also applies to the
   encoded columns inside each training fold (factory step `dedupe`; G-73), e.g. the identical
   missing indicators of fields that are always missing together.
4. **Selection (4.4).** Walk the pool ranking (section 2) and keep features until the cumulative share reaches the
   team's threshold (G-19, declared exception: computed once on pre-cutoff data; CV scores of the
   chosen set are optimistic and the report says so).
5. **Extra candidate (4.5): deleted** (G-35, CR-015). `order_estimated_delivery_date` is neither a
   feature nor a reference model: in production the promised date would be set from the task 1
   prediction itself, which differs in nature from Olist's own estimate.
6. **Rationale (4.6).** For each kept feature: formula, grain, checkout availability,
   missingness, hypothesised signal, verified citation. Citations only from sources checked in
   this experiment, never from earlier experiments; a signal without one is stated as an
   unmeasured mechanism (G-76).
7. **Selected set (4.7).** One per task, used by every model family (G-49). The classification pool is the 24 contract predictors plus the screening candidates adopted at the s03 gate (G-68, G-70): product_photos_qty (scaled, never logged), product_description_lenght (log1p if pre-cutoff skewness > 1) and seller_prior_review_mean (the seller rating customers see at checkout; scaled, missing for sellers without an earlier review, imputed in folds with a missing indicator); regression stays at the 24. Thresholds: 99% for both tasks (human_decisions.yaml). s04 reads the pool only through `e5lib.contract.pool(task)`, never a hand-written list. est_delivery_days was screened (G-69) and not adopted (G-70), so G-35 holds and classification s06 does not depend on regression s06.
8. **Pipeline recipe (4.8).** Per family:
   - numeric: median imputation with missing indicators; `distance_km_max` instead takes the route
     median (customer_state × primary_seller_state, fallback customer_state, then global), after
     log1p, via a custom transformer fitted inside each training fold (G-27);
   - categorical: one-hot with `handle_unknown='ignore'`, drop-first for linear/logistic only;
   - scaling (`StandardScaler`) for linear/logistic only;
   - everything fitted later inside folds (s06–s08), never here.

## 4. Decisions
| ID | Question | Answer | Basis | Status |
| --- | --- | --- | --- | --- |
| s04-D1 | Calendar type | Numeric | G-22 | Agreed |
| s04-D2 | Skew trigger | log1p if skewness > 1, for the five contract candidates and, for classification, product_description_lenght (G-70) | G-22, G-47, G-62 | Agreed |
| s04-D3 | Target cap | None | G-25 | Agreed |
| s04-D4 | Collinearity drops | Flagged by cut-offs, decided by the team, recorded | G-26 | Agreed |
| s04-D5 | Selection | EDA ranking, cumulative threshold fixed before fitting | G-19 | Agreed (threshold value pending s03 output) |
| s04-D6 | Promised lead days | Not used (deleted 2026-10-18) | G-35 (supersedes G-17) | Agreed |
| s04-D7 | Missing distance | Route median in folds | G-27 | Agreed |

## 5. Outputs (per task, under `stages/s04_features/<task>/outputs/`)
- `feature_dictionary.csv`: feature, formula, grain, availability, missingness, transform, kept,
  reason, citation; it extends the s02 `data_dictionary.csv` for the model features (G-58).
- `reduction_rationale.csv`: feature, flagged by (r / VIF / constant / duplicate), paired with,
  team decision, rationale, decided by, date.
- `selected_features.json`: the task's selected feature list, used by every family (G-49).
- `recipes.json`: family → imputation, encoding, scaling, transforms.

## 6. Checks
- Every computation reads only pre-cutoff rows (assert on purchase timestamps).
- No fitted object is saved in this stage's outputs.
- Every feature dropped for collinearity has a row in `reduction_rationale.csv`.
- The cumulative threshold is recorded in `protocol.yaml` before s06 has any output.
- The ranked feature set equals `e5lib.contract.pool(task)` exactly, and its shares sum to 1 (CR-042, audits H-02, M-03).
- `feature_dictionary.csv` is the authoritative description of every pool feature, adopted candidates
  included; the s02 data dictionary describes them as screening columns only (CR-042, audit M-02).

## 7. Milestone 2 reuse
`src/models/refinement_selected_v4.py` (log1p + median imputation pattern) and
`src/models/pipelines.py` (ColumnTransformer layout), copied into `e5lib/factory.py` with
provenance. Fix when copying: calendar fields numeric throughout (remove the string conversion in
`normalize_inputs()`); add the route-median transformer.

## 8. Report hooks
Feature engineering section: feature dictionary, reduction rationale table, selection threshold
and its stated limitation. Appendix (Henry, s04 review): the pipeline recipe table per family
(recipes.json) and the derived features with their formulas (missing indicators: 1 if the parent is
missing, else 0; distance_km_max_missing from the route-median step), from feature_dictionary.csv.

## 9. Open questions
- Cumulative-importance threshold (95% or 99%): set by the team once the s03 ranking exists.
