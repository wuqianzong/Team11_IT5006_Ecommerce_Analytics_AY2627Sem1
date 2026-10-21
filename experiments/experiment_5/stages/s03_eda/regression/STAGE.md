---
node: s03_eda/regression
owner: TBD
reviewer: TBD
status: ACCEPTED
depends_on:
  - s02_data/common
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s03_eda / regression - EDA

Spec: `spec/pipeline_design.md` -> s03. Teacher/TA rows: `spec/sources.md` (search `S03`).
Blueprint: `spec/blueprints/s03_eda.md` (implement only when its status is AGREED).

**Gate question:** Does every planned change follow from a pre-cutoff observation?

## Purpose
Question-driven EDA on orders before the test cutoff: target profiles; outcome trends over time; diagnostics of the 24 contract predictors against each target, importance ranking over all 24 (G-42, G-61) (scatter, Pearson and Spearman; violins and one-hot correlations; class-conditional KDE overlap and per-feature ROC-AUC; mutual information); one importance ranking per task for s04; missingness, outliers and collinearity among raw numeric features; classification only: candidate screen of the s02 screening columns (3.10-3.13, G-68, G-69) with an extended ranking, adoption decided by the team at the gate (G-70).

## Planned outputs (`outputs/`)
- figures/*.png + sidecar json
- target and per-feature diagnostic tables (csv)
- importance_ranking.csv (per task)
- eda_summary.json
- candidate_rationale.csv (finding, evidence, change it motivates, stage that tests it)

## Gate criteria
- No order on or after the test cutoff loaded
- Outcome trends shown, not volume only
- All 24 contract predictors diagnosed against the task's target
- Classification: every screening candidate diagnosed; adoption recorded in spec/human_decisions.yaml (adopted_candidates)
- Each proposed change linked to an observation
- Outputs written under the stage's outputs/, never artifacts/
- Stop: eda_review_pack.md presented; team decisions recorded in spec/human_decisions.yaml before s04 runs
<!-- END GENERATED -->

## Working log (README section 9.1; one row per solution ID, every code change names its ID)
| ID | What was built | Commit | Evidence (files, figures) | Coverage | Round |
| --- | --- | --- | --- | --- | --- |
| 3.1 | Regression target: lead_days profile on 76,925 pre-cutoff orders: median 11.17, mean 13.42, SD 9.45, p99 47.29, max 133.24 days; skewness 2.41, excess kurtosis 11.64. | acceptance commit (e5-s03-accepted) | target_regression_lead_days.csv, figures/target_lead_days_kde.png, eda_summary.json | IMPLEMENTED | 1 |
| 3.3 | Outcome trends: 17 purchase months; over the 17 months with at least 100 orders: median lead time 9.0 to 14.3 days, late-vs-promised rate 3.1% to 21.4%, detractor rate 9.5% to 21.2%; every month is in the table with its counts. | acceptance commit (e5-s03-accepted) | outcome_trends.csv, figures/outcome_trends.png, eda_summary.json | IMPLEMENTED | 1 |
| 3.4 | Numeric features vs lead_days: 20 numeric predictors: Pearson and Spearman with lead_days on the rows where the feature is present, plus each feature's percentile profile; strongest \|Spearman\|: distance_km_max (0.541). Scatter panels use 2,000 random orders each (seed 42); log1p x-axis for the five log1p candidates (plot only). | acceptance commit (e5-s03-accepted) | numeric_feature_target_lead_days.csv, figures/numeric_vs_lead_days.png | IMPLEMENTED | 1 |
| 3.5 | Categorical features vs lead_days: Four categorical predictors: per-level median, IQR and mean of lead_days, drop-first dummy correlations (reference level = first in sorted order), and one rank correlation ratio per feature; the three calendar fields are shown per level for the plots only and stay numeric. | acceptance commit (e5-s03-accepted) | categorical_feature_target_lead_days.csv, figures/categorical_vs_lead_days.png | IMPLEMENTED | 1 |
| 3.8 | Importance ranking: Ranking over the 24 contract predictors by absolute Spearman (rank correlation ratio for the four categorical ones): top 5 ['distance_km_max', 'customer_state', 'interstate_share', 'total_freight', 'primary_category']; cut points {'0.95': 14, '0.99': 18} (features needed for each cumulative share). Missingness, IQR outliers, Pearson/Spearman matrix and VIF on 76,019 complete rows; flagged groups: []; identical columns: [('weight_missing_fraction', 'volume_missing_fraction')]. | acceptance commit (e5-s03-accepted) | feature_quality.csv, collinear_pairs.csv, numeric_correlations.csv, figures/numeric_correlation_heatmap.png, importance_ranking.csv, figures/cumulative_importance.png, candidate_rationale.csv, eda_summary.json, decision.json | IMPLEMENTED | 1 |
| 3.9 | Human gate (review pack for s04 decisions): eda_review_pack.md lists every table and figure above, the ranking with both cut points, the flagged collinear groups and the YAML block the team fills in spec/human_decisions.yaml. | acceptance commit (e5-s03-accepted) | figures/cumulative_importance.png, eda_review_pack.md | IMPLEMENTED | 1 |

## Review rounds (append-only; each round has review/round_N/ and a section in the doc tab)
| Round | Commit | Run ID | Review pack | Outcome | Date |
| --- | --- | --- | --- | --- | --- |
| 1 | uncommitted on f4b7cbf (G-64) | 20261019T081153Z | review/round_1/review_pack.md | comments answered; Henry: 3.1–3.4 agree, thresholds proposed (regression 99%/18; classification 99%/17, open until the screen); candidate screen requested | 2026-10-19 |
| 2 | uncommitted on f4b7cbf (G-64) | 20261019T140119Z | review/round_2/review_pack.md | reviewed: all rows unchanged (evidence hashes equal round 1); rerun only because s02 records gained the classification screening columns | 2026-10-19 |
| 3 | acceptance commit (tag e5-s03-accepted) | 20261019T151309Z | review/round_3/review_pack.md | accepted: all rows unchanged (evidence hashes equal round 2) | 2026-10-19 |

## Accepted result (the only result the report and slides may cite)
- **Current run to cite: 20261020T145535Z** (CR-048, 2026-10-20). The working log above shows this run's values; the lines below record the acceptance history.
- Accepted round: 3 - commit: the "s03 accepted" commit, tag `e5-s03-accepted` - run ID: 20261019T151309Z - approved by: experiment lead (Wu Qianzong), after team review in the doc tab "Implementation reviews › s03 EDA" - date: 2026-10-19
- Gate decisions (spec/human_decisions.yaml, G-70): threshold 99%; no collinearity drop.

## Changes after acceptance (README section 9.2)
- 2026-10-20, CR-042 (G-71, external audit): rerun 20261019T163336Z on a clean tree (dirty false); every value output byte-identical; only the manifest changed. Approved by the experiment lead. Status stays ACCEPTED (no decision.json changed).
- 2026-10-20, CR-043 (G-72, data start 2017-01-01): rerun 20261020T053125Z on a clean tree (dirty false); pre-cutoff orders 77,139 → 76,925; values shift slightly; the 95% and 99% cuts keep the same 14 and 18 features, so the gate decisions stand. Approved by the experiment lead. Status stays ACCEPTED (no decision.json changed).
- 2026-10-20, CR-044 to CR-048 (s04/s05 build): rerun 20261020T145535Z on a clean tree (commit c7114d3 and its index follow-up); every value output unchanged (rerun after the s04/s05 foundation modules). Approved by the experiment lead. Status stays ACCEPTED.
- 2026-10-21, CR-049 to CR-051 (audit follow-up, G-78, s06 build): rerun 20261021T033032Z on a clean tree (commit 0734057, dirty false) after the foundation change (e5lib/training.py; s04 automatic duplicate rows keep the rule date); every value output byte-identical. Status stays ACCEPTED.

## Deviations from blueprint
None.

## Open questions
- Resolved at acceptance (G-70): thresholds, collinearity, method decisions 1-4.
