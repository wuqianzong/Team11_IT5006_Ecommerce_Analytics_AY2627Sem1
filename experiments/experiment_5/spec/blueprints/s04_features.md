# s04_features — blueprint

| Field | Value |
| --- | --- |
| Stage | s04_features (`../pipeline_design.md` → s04) |
| Nodes | regression, classification |
| Status | AGREED |
| Owner | TBD |
| Last agreed | 2026-10-17 (team walkthrough, doc tab "Feature solution (s02–s05)") |
| Discussion | Claude Doc "Milestone 3 pipeline stages", tab "Feature solution (s02–s05)", section s04 |

## 1. Goal and gate
Goal: define, without fitting, each task's feature list, transforms and pipeline recipe.
The threshold and collinearity drops come from the team via `spec/human_decisions.yaml` (G-31).
Gate: features and recipes defined without fitting or using test data (`../stages.json`).

## 2. Inputs
- `stages/s02_data/common/outputs/records.csv.gz` (pre-cutoff, task-eligible rows only).
- `stages/s03_eda/<task>/outputs/importance_ranking.csv` and the raw collinearity tables.
- `spec/protocol.yaml`: skewness trigger (1.0), collinearity cut-offs (|r| > 0.9, VIF > 10).
- `spec/human_decisions.yaml` (G-31): the team's cumulative-importance threshold (95% or 99%) and
  the feature dropped from each flagged collinear group, with rationale, recorded after reviewing
  `eda_review_pack.md`. s04 stops if these are missing.

## 3. Method
1. **Baseline (4.1).** The 27 contract predictors minus `has_items` and `freight_ratio_missing`
   (post-purchase leakage, G-30), so 25 candidates; `purchase_month`, `purchase_dayofweek`,
   `purchase_hour` numeric (G-22).
2. **Transforms (4.2).** log1p for every non-negative numeric feature with pre-cutoff skewness > 1;
   log1p regression target (`TransformedTargetRegressor`, inverse expm1). No target cap (G-25).
3. **Reduction (4.3).** Drop constant and duplicate columns automatically. Flag features with
   |correlation| > 0.9 or VIF > 10; the team decides which of each flagged group to drop and
   records the decision and rationale in `reduction_rationale.csv` (G-26). Report the encoded
   design-matrix rank and condition number per recipe.
4. **Selection (4.4).** Walk the s03 ranking and keep features until the cumulative share reaches the
   team's threshold (G-19, declared exception: computed once on pre-cutoff data; CV scores of the
   chosen set are optimistic and the report says so).
5. **Extra candidate (4.5).** "Promised lead days" = `order_estimated_delivery_date` − purchase,
   in days (known at checkout). Candidate feature, kept only if it wins on the folds in s06; also a
   regression reference model (Olist's own promise) (G-17).
6. **Rationale (4.6).** For each kept feature: formula, grain, checkout availability,
   missingness, hypothesised signal, verified citation.
7. **Candidate sets (4.7).** Per model family: the selected set, with and without 4.5.
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
| s04-D2 | Skew trigger | log1p if skewness > 1 | G-22 | Agreed |
| s04-D3 | Target cap | None | G-25 | Agreed |
| s04-D4 | Collinearity drops | Flagged by cut-offs, decided by the team, recorded | G-26 | Agreed |
| s04-D5 | Selection | EDA ranking, cumulative threshold fixed before fitting | G-19 | Agreed (threshold value pending s03 output) |
| s04-D6 | Promised lead days | Candidate feature and regression reference | G-17 | Agreed |
| s04-D7 | Missing distance | Route median in folds | G-27 | Agreed |

## 5. Outputs (per task, under `stages/s04_features/<task>/outputs/`)
- `feature_dictionary.csv`: feature, formula, grain, availability, missingness, transform, kept,
  reason, citation.
- `reduction_rationale.csv`: feature, flagged by (r / VIF / constant / duplicate), paired with,
  team decision, rationale, decided by, date.
- `candidate_sets.json`: family → feature list (with / without promised lead days).
- `recipes.json`: family → imputation, encoding, scaling, transforms.

## 6. Checks
- Every computation reads only pre-cutoff rows (assert on purchase timestamps).
- No fitted object is saved in this stage's outputs.
- Every feature dropped for collinearity has a row in `reduction_rationale.csv`.
- The cumulative threshold is recorded in `protocol.yaml` before s06 has any output.

## 7. Milestone 2 reuse
`src/models/refinement_selected_v4.py` (log1p + median imputation pattern) and
`src/models/pipelines.py` (ColumnTransformer layout), copied into `e5lib/factory.py` with
provenance. Fix when copying: calendar fields numeric throughout (remove the string conversion in
`normalize_inputs()`); add the route-median transformer.

## 8. Report hooks
Feature engineering section: feature dictionary, reduction rationale table, selection threshold
and its stated limitation.

## 9. Open questions
- Cumulative-importance threshold (95% or 99%): set by the team once the s03 ranking exists.
