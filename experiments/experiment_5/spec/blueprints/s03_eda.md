# s03_eda — blueprint

| Field | Value |
| --- | --- |
| Stage | s03_eda (`../pipeline_design.md` → s03) |
| Nodes | regression, classification |
| Status | AGREED |
| Owner | TBD |
| Last agreed | 2026-10-17 (team walkthrough, doc tab "Feature solution (s02–s05)") |
| Discussion | Claude Doc "Milestone 3 pipeline stages", tab "Feature solution (s02–s05)", section s03 |

## 1. Goal and gate
Goal: describe the targets and the 24 contract predictors against each target on pre-cutoff orders,
and produce one importance ranking per task over the 24 eligible predictors for s04 (G-42).
Gate: every planned change follows from a pre-cutoff observation (`../stages.json`).

## 2. Inputs
- `stages/s02_data/common/outputs/records.csv.gz` (task-eligible rows, purchase before
  the task's test cutoff from s02 only).
- `spec/protocol.yaml`: test cutoff, seed 42.

## 3. Method
1. **Regression target (3.1).** `lead_days` KDE; table with count, mean, SD, min, 1/5/25/50/75/95/99%
   percentiles, max, skewness, kurtosis.
2. **Classification target (3.2).** `is_detractor` bar chart; counts and shares of low (≤ 2) and
   normal (≥ 3) reviews.
3. **Trends over time (3.3).** Per purchase month: median lead time, late-vs-promised rate
   (delivered after `order_estimated_delivery_date`), detractor rate, order count.
4. **Numeric features vs `lead_days` (3.4).** Scatter per feature; Pearson and Spearman; full
   percentile profile; sorted by absolute correlation.
5. **Categorical features vs `lead_days` (3.5).** Violin plots; one-hot (drop-first)
   correlations; calendar fields treated as categorical for plots only.
6. **Numeric features vs `is_detractor` (3.6).** Class-conditional KDEs with overlap coefficient
   (0% = complete separation, 100% = no signal) and per-feature ROC-AUC on the same rows.
7. **Categorical features vs `is_detractor` (3.7).** `mutual_info_classif`, discrete features,
   `random_state=42`.
8. **Importance ranking (3.8).** One measure per task, so cumulative shares are meaningful:
   absolute Spearman (regression), mutual information (classification). All 24 contract
   predictors are ranked, so cumulative shares are over the selection pool (G-42, G-61).
   Also report missingness, outliers and correlation/VIF among raw numeric features.
9. **Human gate (G-31).** Stop here. Build `eda_review_pack.md` (every table and figure above, plus
   the flagged collinear groups and the cumulative-importance curve with the 95% and 99% cut
   points marked) and present it to the team. The pipeline does not run s04 until the team
   records its decisions in `spec/human_decisions.yaml` (threshold; feature dropped from each
   flagged group, with rationale) via CHANGELOG.

## 4. Decisions
| ID | Question | Answer | Basis | Status |
| --- | --- | --- | --- | --- |
| s03-D1 | Population | Pre-cutoff orders only | Design rule 3 | Agreed |
| s03-D2 | Ranking measure | Spearman (regression), mutual information (classification) | G-19; one measure per task | Agreed |
| s03-D4 | Human gate before s04 | Stop and present all EDA; team decides threshold and collinearity drops | G-31 | Agreed |
| s03-D3 | Output location | Stage `outputs/`, never `artifacts/` | README §0.1 containment | Agreed |

## 5. Outputs (per task, under `stages/s03_eda/<task>/outputs/`)
- `target_regression_lead_days.csv` or `target_classification_is_detractor.csv`
- `outcome_trends.csv`
- Regression: `numeric_feature_target_lead_days.csv`, `categorical_feature_target_lead_days.csv`
- Classification: `numeric_feature_target_is_detractor.csv`, `categorical_feature_target_is_detractor.csv`
- `importance_ranking.csv` (feature, measure, value, rank, cumulative share)
- `eda_summary.json`, `candidate_rationale.csv`, `figures/*.png` with sidecar `*.json`
- `eda_review_pack.md` (the human-review pack for the s03 → s04 gate)

## 6. Checks
- Assert max purchase timestamp < the task's test cutoff (from `protocol.yaml`).
- All 24 contract predictors present in the diagnostic tables.
- `importance_ranking.csv` has exactly 24 rows (the eligible predictors) and its cumulative share
  ends at 1.0.
- s04 refuses to run if `spec/human_decisions.yaml` lacks the s03 decisions for its task.

## 7. Milestone 2 reuse
`experiments/experiment_3/run_eda_outliers.py` (skewness, quantile profiles) as reference only;
rewrite inside the stage `run.py`.

## 8. Report hooks
EDA highlights section: target profiles, outcome trends, top features per task.

## 9. Open questions
None.
