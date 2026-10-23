# B4 — features (blueprint)

| Field | Value |
| --- | --- |
| Stage | B4, Pipeline B (CR-054 B-C11, B-C12) |
| Nodes | regression, classification |
| Status | AGREED (experiment lead, 2026-10-23); round 2 change B-G-02 |
| Inherits from A | s04 method and code (pool, transforms, duplicate rule, selection at 99%), A's recipes.json conventions |

## 1. Goal and gate
Goal: rank B's feature pool on B's development rows with A's method, keep the features that
reach 99% of the cumulative importance, and write B's recipes and feature dictionary.
Gate: the selected set follows the 99% rule exactly; every B feature is documented.

## 2. Inputs
- B2 `records_B.csv.gz` per task.
- A's task pool (`e5lib.contract.pool(task)`: 24 predictors; classification + the three adopted).
- A's s04 transforms and duplicate rule (`e5lib.features`, read-only).

## 3. Method
1. **Pool.** A's task pool + B's candidates (B-C6 to B-C9; names B-G-04); route counts as one feature.
2. **Ranking.** A's ranking on B's development rows: |Spearman| with the log target for
   regression, mutual information for classification, as in A's s03/s04.
3. **Selection (B-C11).** Keep the top features reaching 99% of the cumulative share (A's G-70
   threshold). A feature below the cut is dropped with its rank and share recorded.
4. **Transforms.** A's rules: log1p for skewed counts and all day counts; rates and flags
   scaled only; route one-hot (drop-first for linear/logistic, every level for trees); A's
   duplicate rule; imputation fitted inside the folds. B-G-02: with route in the pool,
   customer_state and primary_seller_state are dropped in the reduction as nested in route; no
   route-median fill for distance_km_max, which B-C2 leaves never missing.
5. **Recipes.** One recipe per family (dummy, linear/logistic, tree, forest), built with A's code.

## 4. Outputs (per task, `pipeline_b/stages/b04/<task>/outputs/`)
`selection_ranking_B.csv`, `selected_features_B.json`, `recipes_B.json`,
`feature_dictionary_B.csv` (B-C12: name, scope, definition, formula, reason, transform, rank,
share, kept or dropped with reason), `design_matrix_B.csv`.

## 5. Checks
- The ranked set equals B's pool; the kept set is exactly the 99% prefix.
- Every kept feature has a feature_dictionary_B.csv row with formula and reason.
- The linear/logistic design matrix is full rank.
