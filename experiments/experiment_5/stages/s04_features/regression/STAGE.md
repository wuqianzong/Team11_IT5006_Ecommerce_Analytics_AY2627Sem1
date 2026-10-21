---
node: s04_features/regression
owner: TBD
reviewer: TBD
status: ACCEPTED
depends_on:
  - s03_eda/regression
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s04_features / regression - Features

Spec: `spec/pipeline_design.md` -> s04. Teacher/TA rows: `spec/sources.md` (search `S04`).
Blueprint: `spec/blueprints/s04_features.md` (implement only when its status is AGREED).

**Gate question:** Are features and recipes defined without fitting or using labels?

## Purpose
Define, without fitting: the 24-predictor baseline from e5lib/contract.py (G-61; numeric calendar fields), plus for classification the candidates adopted at the s03 gate (G-70: product_photos_qty, product_description_lenght, seller_prior_review_mean; read through e5lib.contract.pool); log1p for the five contract candidates (and, for classification, product_description_lenght; G-70) with pre-cutoff skewness > 1 (G-47, G-62) and for the regression target; the pre-registered label-free reduction to a core set; feature selection by the s03 importance ranking at the team's cumulative threshold (95% or 99%, fixed before any model is fitted); encoded design-matrix rank per recipe; rationale and citations; order_estimated_delivery_date never a feature (G-35); the pipeline recipe per model (impute, encode, scale).

## Planned outputs (`outputs/`)
- feature_dictionary.csv (formula, grain, availability, missingness, rationale, citation)
- selected_features.json (one set per task, all families)
- recipes.json (pipeline recipe per model)
- reduction_rationale.csv (flagged features, team decision, rationale)

## Gate criteria
- Reduction and importance selection use pre-cutoff orders only, never test
- Every collinearity drop is a recorded team decision with rationale (reduction_rationale.csv)
- Threshold and collinearity drops read from spec/human_decisions.yaml (team-decided after s03); s04 stops if missing
- No target cap (G-25)
- Every retained feature has a rationale
- order_estimated_delivery_date not used as a feature or reference (G-35)
- Nothing fitted on data
<!-- END GENERATED -->

## Working log (README section 9.1; one row per solution ID, every code change names its ID)
| ID | What was built | Commit | Evidence (files, figures) | Coverage | Round |
| --- | --- | --- | --- | --- | --- |
| 4.1 | Baseline: Pool from e5lib.contract.pool('regression'): 24 features = 24 contract predictors; 4 categorical, calendar fields numeric (G-22). | acceptance commit (e5-s04-accepted) | baseline_pool.csv | IMPLEMENTED | 1 |
| 4.2 | Transforms: log1p for 5 of 5 candidates by pre-cutoff skewness > 1: total_price 10.13; total_freight 8.13; total_weight_g 6.63; total_volume_cm3 7.40; distance_km_max 1.64. Regression target log1p(lead_days), scored in days (G-36); no target cap (G-25). | acceptance commit (e5-s04-accepted) | transforms.csv | IMPLEMENTED | 1 |
| 4.3 | Reduction: Core set 23 of 24: weight_missing_fraction dropped (duplicate, kept volume_missing_fraction). Team collinearity drops: 0 (none flagged in s03). Encoded design matrix: linear: 138 encoded columns, duplicates dropped [missingindicator_total_volume_cm3], 137 columns, rank 137, condition number 424; tree: 142 encoded columns, duplicates dropped [missingindicator_total_volume_cm3], 141 columns, rank 138, condition number 9.02e+16. | acceptance commit (e5-s04-accepted) | reduction_rationale.csv, design_matrix.csv | IMPLEMENTED | 1 |
| 4.4 | Selection: Core ranking by absolute Spearman, re-normalised over the 23 core features; 18 kept at the 99% threshold. Dropped by the cut: distance_missing_fraction, category_missing_fraction, n_payment_methods, volume_missing_fraction, purchase_hour. | acceptance commit (e5-s04-accepted) | selection_ranking.csv, figures/selection_cumulative.png, figures/selection_cumulative.csv, figures/selection_cumulative.json, decision.json | IMPLEMENTED | 1 |
| 4.6 | Rationale: feature_dictionary.csv: 27 rows (every pool feature and the derived missing indicators): formula, grain, checkout availability, missingness, transform, imputation, kept and reason, hypothesised signal and claim type; 0 rows cite a source checked in Experiment 5 (0 of 21 kept). | acceptance commit (e5-s04-accepted) | feature_dictionary.csv | DEVIATION | 3 |
| 4.7 | Selected set: selected_features.json: 18 features (14 numeric, 4 categorical), 3 derived missing indicators, log1p inputs ['distance_km_max', 'total_freight', 'total_price', 'total_weight_g', 'total_volume_cm3']; one set used by every family (G-49). | acceptance commit (e5-s04-accepted) | selected_features.json, decision.json | IMPLEMENTED | 1 |
| 4.8 | Pipeline recipe: recipes.json: one e5lib.factory spec per family (dummy = dummy_median, linear = linear, tree = tree_reg, forest = forest_reg): log1p, median imputation with missing indicators, route median for distance_km_max, one-hot with unknown levels ignored (drop-first and StandardScaler for linear/logistic only). | acceptance commit (e5-s04-accepted) | recipes.json, design_matrix.csv | IMPLEMENTED | 1 |

## Review rounds (append-only; each round has review/round_N/ and a section in the doc tab)
| Round | Commit | Run ID | Review pack | Outcome | Date |
| --- | --- | --- | --- | --- | --- |
| 1 | acceptance commit (e5-s04-accepted) | 20261020T062548Z | review/round_1/review_pack.md | reviewed: lead comment on 4.6 (no reliance on earlier experiments) | 2026-10-20 |
| 2 | acceptance commit (e5-s04-accepted) | 20261020T070535Z | review/round_2/review_pack.md | reviewed: 4.6 without Milestone 2 references; other rows unchanged | 2026-10-20 |
| 3 | acceptance commit (e5-s04-accepted) | 20261020T124722Z | review/round_3/review_pack.md | accepted: all comments resolved (G-73, G-76 agreed; G-27 and the tree encoding kept); accepted run 20261020T145617Z on a clean tree, outputs identical to this pack | 2026-10-20 |

## Accepted result (the only result the report and slides may cite)
- Accepted round: 3 - commit: the "s04 accepted" commit, tag `e5-s04-accepted` - run ID: 20261020T145617Z (clean tree, dirty false; evidence identical to review/round_3) - approved by: experiment lead (Wu Qianzong), after team review (Henry) in the doc tab "Implementation reviews › s04 Features" - date: 2026-10-20
- Decisions: threshold 99% and no collinearity drop (G-70); duplicate encoded columns dropped in the fold (G-73); citations only from sources checked in Experiment 5 (G-76); route median for missing distance kept (G-27).

## Changes after acceptance (README section 9.2)
- 2026-10-21, CR-049 to CR-051 (audit follow-up, G-78, s06 build): rerun 20261021T033112Z on a clean tree (commit 0734057, dirty false) after the foundation change (e5lib/training.py; s04 automatic duplicate rows keep the rule date); every value output byte-identical. Status stays ACCEPTED.
- 2026-10-21, CR-052 (s07 build): rerun 20261021T041716Z on a clean tree (commit 7eb8197, dirty false) after the foundation change (e5lib/tuning.py); every value output byte-identical. Status stays ACCEPTED.

## Deviations from blueprint
- 4.6: verified citation only for the classification delivery proxies (G-76); all other kept features are unmeasured mechanisms.

## Open questions

None. Both items raised in the s02 review (2.12) are closed (CR-049):
- Feature × task table: delivered in the doc tab "Implementation reviews › s04 Features" (section "Feature × task"), built from both feature_dictionary.csv files.
- Imputation inside the folds: the rule and order per feature are delivered in the same tab (section "Imputation inside the folds"); the learned medians and filled counts per fold need fitted pipelines and are an s06 report hook.
