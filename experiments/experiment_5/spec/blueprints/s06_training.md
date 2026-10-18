# s06_training — blueprint

| Field | Value |
| --- | --- |
| Stage | s06_training (`../pipeline_design.md` → s06) |
| Nodes | regression, classification |
| Status | AGREED |
| Owner | TBD |
| Last agreed | 2026-10-18 (team review, doc tab "Model solution (s01, s06–s10)", section s06) |
| Discussion | Claude Doc "Milestone 3 pipeline stages", tab "Model solution (s01, s06–s10)", section s06 |

## 1. Goal and gate
Goal: train every model family basic to complex on the s05 folds, as one sklearn Pipeline each,
and record all scores and diagnostics. Regularisation and tuning belong to s07.
Gate: models run basic to complex on identical folds, with each choice justified
(`../stages.json`).

## 2. Inputs
- `stages/s02_data/common/outputs/records.csv.gz` (development rows only).
- `stages/s04_features/<task>/outputs/candidate_sets.json` (the selected set) and `recipes.json`.
- `stages/s05_partition/<task>/outputs/folds.csv`.
- `spec/protocol.yaml`: decision rule (s01), seed 42.

## 3. Method
1. **Pipeline factory (6.1). Assembly only; no new transformation.** `e5lib.factory.build`
   combines the s04 recipe (feature set, imputation, encoding, scaling, log1p and log target,
   all defined in s04) with an estimator into one sklearn Pipeline with a stable `candidate_id`.
   - Regression log target: `TransformedTargetRegressor(func=log1p, inverse_func=expm1)`,
     always scored on raw days.
   - The pipeline is fitted inside each s05 training fold. That is where the learned steps
     defined in s04 (medians, scaler, route median) get their values, so nothing is fitted on
     validation or test rows.
2. **Families, basic to complex (6.2).** Each task uses its s04 selected feature set (4.4)
   through the s04 recipe (4.8), with the s04 4.2 log transforms always on: log1p on inputs with
   pre-cutoff skewness > 1, and on the regression target (G-36). In order:
   - `DummyRegressor(strategy='median')` / `DummyClassifier(strategy='prior')`;
   - plain `LinearRegression` / `LogisticRegression(penalty=None, solver='lbfgs', max_iter=5000)`;
   - `DecisionTree` (max_depth=5, min_samples_leaf=100);
   - `RandomForest` (200 trees, max_depth=10, min_samples_leaf=50, max_features='sqrt').
   Seed 42. A more complex family is kept only under the s01 decision rule (G-33).
3. *(6.3 removed: feature set and log transforms are fixed in s04, G-36.)*
4. **Scores recorded (6.4).** For every candidate and fold: training and validation scores on all
   s01 metrics, row and positive counts, fit time, convergence warnings.
5. **Residual diagnostics, regression (6.5).** Residual vs fitted, residual histogram and Q–Q plot
   on out-of-fold predictions of the plain linear model and the best tree model.
6. **Classification diagnostics (6.6).** Out-of-fold PR and ROC curves, reliability curve,
   Brier score, and a predicted-probability histogram per class.
7. **Learning curves and design matrix (6.7).** Learning curves on the latest fold (training sizes
   20–100%, same validation block). Encoded design-matrix rank and condition number for the
   linear models.

## 4. Decisions
| ID | Question | Answer | Basis | Status |
| --- | --- | --- | --- | --- |
| s06-D1 | Where transforms are defined | s04 only; s06 assembles and fits in folds | Tutorial 4; README §5.3 | Agreed |
| s06-D2 | Comparison | Families only, dummy → linear/logistic → tree → forest | G-36; Tutorial 8 | Agreed |
| s06-D3 | Log transforms | Always on from EDA, not tested on folds | G-36 | Agreed |
| s06-D4 | Keep rule | s01 one-standard-error rule | G-33 | Agreed |

## 5. Outputs (per task, under `stages/s06_training/<task>/outputs/`)
- `metrics_long.csv`, out-of-fold `predictions.csv.gz`, `candidates.csv` (design rule 8).
- `decision.json`: each family comparison under the decision rule, with fold scores.
- `figures/*.png` with sidecar data; `curves/*.csv` (PR, ROC, reliability, learning curves).

## 6. Checks
- Identical rows and folds for every candidate; preprocessing fitted only inside training folds.
- The simplest model of each family is present.
- No test row is read (population guard).

## 7. Milestone 2 reuse
`src/models/pipelines.py` (ColumnTransformer layout) and the dummy/ladder code in
`src/models/`, copied into `e5lib/factory.py` with provenance. No Milestone 2 result is used.

## 8. Report hooks
Modelling section: family ladder table (train and validation scores), residual and diagnostic
figures, learning curves.

## 9. Open questions
None.
