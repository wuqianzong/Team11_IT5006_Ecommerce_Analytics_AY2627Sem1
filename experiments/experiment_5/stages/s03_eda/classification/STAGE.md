---
node: s03_eda/classification
owner: TBD
reviewer: TBD
status: ACCEPTED
depends_on:
  - s02_data/common
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s03_eda / classification - EDA

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
| 3.2 | Classification target: 77,736 pre-cutoff orders: 11,493 low reviews (score <= 2, 14.78%) and 66,243 normal reviews (score >= 3, 85.22%). | acceptance commit (e5-s03-accepted) | target_classification_is_detractor.csv, figures/target_is_detractor_bar.png, eda_summary.json | IMPLEMENTED | 1 |
| 3.3 | Outcome trends: 17 purchase months; over the 17 months with at least 100 orders: detractor rate 10.7% to 22.5%, late-vs-promised rate 2.8% to 21.1%, median lead time 9.0 to 14.3 days; every month is in the table with its counts. | acceptance commit (e5-s03-accepted) | outcome_trends.csv, figures/outcome_trends.png, eda_summary.json | IMPLEMENTED | 1 |
| 3.6 | Numeric features vs is_detractor: 20 numeric predictors: class-conditional distributions with the overlap coefficient (KDE for continuous features, class frequencies for features with at most 30 values), per-feature ROC-AUC and mutual information on the same rows; lowest overlap: total_freight (86.6%, ROC-AUC 0.587). | acceptance commit (e5-s03-accepted) | numeric_feature_target_is_detractor.csv, figures/numeric_vs_is_detractor.png | IMPLEMENTED | 1 |
| 3.7 | Categorical features vs is_detractor: Four categorical predictors: mutual_info_classif (discrete, seed 42) and per-level detractor rates; calendar fields shown per level for the plots only. MI: customer_state 0.0051, primary_seller_state 0.0009, primary_category 0.0026, primary_payment_type 0.0000 nats. | acceptance commit (e5-s03-accepted) | categorical_feature_target_is_detractor.csv, figures/categorical_vs_is_detractor.png | IMPLEMENTED | 1 |
| 3.8 | Importance ranking: Ranking over the 24 contract predictors by mutual information (discrete estimator for categorical features and features with at most 30 values, k-NN estimator for the rest): top 5 ['total_freight', 'freight_ratio', 'total_volume_cm3', 'total_price', 'n_items']; cut points {'0.95': 14, '0.99': 17}. Missingness, IQR outliers, Pearson/Spearman matrix and VIF on 76,810 complete rows; flagged groups: []; identical columns: [('weight_missing_fraction', 'volume_missing_fraction')]. | acceptance commit (e5-s03-accepted) | feature_quality.csv, collinear_pairs.csv, numeric_correlations.csv, figures/numeric_correlation_heatmap.png, importance_ranking.csv, figures/cumulative_importance.png, candidate_rationale.csv, eda_summary.json, decision.json | IMPLEMENTED | 1 |
| 3.9 | Human gate (review pack for s04 decisions): eda_review_pack.md lists every table and figure above, the ranking with both cut points, the flagged collinear groups and the YAML block the team fills in spec/human_decisions.yaml. | acceptance commit (e5-s03-accepted) | figures/cumulative_importance.png, eda_review_pack.md | IMPLEMENTED | 1 |
| 3.10 | Candidate screen (G-68): Screening columns (not predictors) diagnosed against is_detractor with the 3.6 measures; numeric ones also with skewness, correlation with the 20 numeric predictors and VIF in the extended numeric set. Product fields (primary item): product_photos_qty: rank 26, MI 0.0005, ROC-AUC 0.480, overlap 96.3%; product_description_lenght: rank 9, MI 0.0054, ROC-AUC 0.492, overlap 97.8%; product_name_lenght: rank 36, MI 0.0000, ROC-AUC 0.504, overlap 97.2%. Extended ranking over 24 + 12 candidates; cut points {'0.95': 22, '0.99': 26} (official 3.8 ranking unchanged at 24). | acceptance commit (e5-s03-accepted) | candidate_screen_is_detractor.csv, candidate_ranking_extended.csv, candidate_collinear_pairs.csv, figures/candidate_screen.png | IMPLEMENTED | 2 |
| 3.11 | Screening columns (not predictors) diagnosed against is_detractor with the 3.6 measures; numeric ones also with skewness, correlation with the 20 numeric predictors and VIF in the extended numeric set | acceptance commit (e5-s03-accepted) | candidate_screen_3_11.csv | IMPLEMENTED | 3 |
| 3.12 | Screening columns (not predictors) diagnosed against is_detractor with the 3.6 measures; numeric ones also with skewness, correlation with the 20 numeric predictors and VIF in the extended numeric set | acceptance commit (e5-s03-accepted) | candidate_screen_3_12.csv | IMPLEMENTED | 3 |
| 3.13 | Screening columns (not predictors) diagnosed against is_detractor with the 3.6 measures; numeric ones also with skewness, correlation with the 20 numeric predictors and VIF in the extended numeric set | acceptance commit (e5-s03-accepted) | candidate_screen_3_13.csv | IMPLEMENTED | 3 |

## Review rounds (append-only; each round has review/round_N/ and a section in the doc tab)
| Round | Commit | Run ID | Review pack | Outcome | Date |
| --- | --- | --- | --- | --- | --- |
| 1 | uncommitted on f4b7cbf (G-64) | 20261019T081206Z | review/round_1/review_pack.md | comments answered; Henry: 3.1–3.4 agree, thresholds proposed (regression 99%/18; classification 99%/17, open until the screen); candidate screen requested | 2026-10-19 |
| 2 | uncommitted on f4b7cbf (G-64) | 20261019T140130Z | review/round_2/review_pack.md | reviewed: new card 3.10 candidate screen (G-68); 3.2, 3.3, 3.8, 3.9 change only through shared files (eda_summary.json, candidate_rationale.csv), values unchanged | 2026-10-19 |
| 3 | acceptance commit (tag e5-s03-accepted) | 20261019T151336Z | review/round_3/review_pack.md | accepted: cards 3.11-3.13 new, 3.10 extended to 24 + 12; product_photos_qty and product_description_lenght adopted; Henry: 99% threshold both tasks | 2026-10-19 |
| 4 | CR-042 commits (tag e5-s03-accepted moved) | 20261019T163353Z | review/round_4/review_pack.md | re-accepted by the experiment lead after CR-042 (G-71): values shift slightly (seller_prior_review_mean MI 0.0104 → 0.0094, still rank 2 of 36); the 99% cut of the 27-feature pool keeps the same 19 features in a slightly different order; gate decisions G-70 unchanged | 2026-10-20 |
| 5 | CR-043 commits (tag e5-s03-accepted moved) | 20261020T053142Z | review/round_5/review_pack.md | re-accepted by the experiment lead after CR-043 (G-72, data start 2017-01-01): pre-cutoff orders 77,965 → 77,736; seller_prior_review_mean MI 0.0094 → 0.0110, now rank 1 of 36; the 99% cuts keep the same 17 of 24 and the same 19 of the 27-feature pool, order of near-tied features changed; gate decisions G-70 unchanged | 2026-10-20 |

## Accepted result (the only result the report and slides may cite)
- Accepted round: 5 (CR-043; first accepted in round 3 on 2026-10-19) - commit: the CR-043 commit, tag `e5-s03-accepted` - run ID: 20261020T145553Z (current run after CR-048; values unchanged) (clean tree, dirty false) - approved by: experiment lead (Wu Qianzong), after team review in the doc tab "Implementation reviews › s03 EDA" - date: 2026-10-20
- Gate decisions (spec/human_decisions.yaml, G-70): threshold 99%; no collinearity drop; adopted candidates product_photos_qty, product_description_lenght, seller_prior_review_mean.

## Changes after acceptance (README section 9.2)
- 2026-10-20, CR-044 to CR-048 (s04/s05 build): rerun 20261020T145553Z on a clean tree (commit c7114d3 and its index follow-up); every value output unchanged (rerun after the s04/s05 foundation modules). Approved by the experiment lead. Status stays ACCEPTED.

## Deviations from blueprint
None.

## Open questions
- Resolved at acceptance (G-70): thresholds, collinearity, method decisions 1-4, candidate adoption (3.10-3.13).
