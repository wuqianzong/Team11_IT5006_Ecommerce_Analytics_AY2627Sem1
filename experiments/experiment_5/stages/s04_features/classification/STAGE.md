---
node: s04_features/classification
owner: TBD
reviewer: TBD
status: ACCEPTED
depends_on:
  - s03_eda/classification
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s04_features / classification - Features

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
| 4.1 | Baseline: Pool from e5lib.contract.pool('classification'): 27 features = 24 contract predictors + 3 adopted at the s03 gate (product_description_lenght, product_photos_qty, seller_prior_review_mean); 4 categorical, calendar fields numeric (G-22). | acceptance commit (e5-s04-accepted) | baseline_pool.csv | IMPLEMENTED | 1 |
| 4.2 | Transforms: log1p for 6 of 6 candidates by pre-cutoff skewness > 1: total_price 10.06; total_freight 8.10; total_weight_g 6.59; total_volume_cm3 7.48; distance_km_max 1.64; product_description_lenght 2.05. | acceptance commit (e5-s04-accepted) | transforms.csv | IMPLEMENTED | 1 |
| 4.3 | Reduction: Core set 26 of 27: weight_missing_fraction dropped (duplicate, kept volume_missing_fraction). Team collinearity drops: 0 (none flagged in s03). Encoded design matrix: linear: 140 encoded columns, duplicates dropped [missingindicator_total_weight_g; missingindicator_product_photos_qty], 138 columns, rank 138, condition number 1.55e+03; tree: 143 encoded columns, duplicates dropped [missingindicator_total_weight_g; missingindicator_product_photos_qty], 141 columns, rank 139, condition number 7.99e+16. | acceptance commit (e5-s04-accepted) | reduction_rationale.csv, design_matrix.csv | IMPLEMENTED | 1 |
| 4.4 | Selection: Core ranking by mutual information, re-normalised over the 26 core features; 19 kept at the 99% threshold. Dropped by the cut: category_missing_fraction, purchase_hour, purchase_dayofweek, distance_missing_fraction, primary_payment_type, volume_missing_fraction, n_payment_methods. | acceptance commit (e5-s04-accepted) | selection_ranking.csv, figures/selection_cumulative.png, figures/selection_cumulative.csv, figures/selection_cumulative.json, decision.json | IMPLEMENTED | 1 |
| 4.6 | Rationale: feature_dictionary.csv: 33 rows (every pool feature and the derived missing indicators): formula, grain, checkout availability, missingness, transform, imputation, kept and reason, hypothesised signal and claim type; 9 rows cite a source checked in Experiment 5 (9 of 25 kept). | acceptance commit (e5-s04-accepted) | feature_dictionary.csv | DEVIATION | 3 |
| 4.7 | Selected set: selected_features.json: 19 features (16 numeric, 3 categorical), 6 derived missing indicators, log1p inputs ['total_freight', 'total_volume_cm3', 'total_price', 'product_description_lenght', 'total_weight_g', 'distance_km_max']; one set used by every family (G-49). | acceptance commit (e5-s04-accepted) | selected_features.json, decision.json | IMPLEMENTED | 1 |
| 4.8 | Pipeline recipe: recipes.json: one e5lib.factory spec per family (dummy = dummy_prior, linear = logistic, tree = tree_clf, forest = forest_clf): log1p, median imputation with missing indicators, route median for distance_km_max, one-hot with unknown levels ignored (drop-first and StandardScaler for linear/logistic only). | acceptance commit (e5-s04-accepted) | recipes.json, design_matrix.csv | IMPLEMENTED | 1 |

## Review rounds (append-only; each round has review/round_N/ and a section in the doc tab)
| Round | Commit | Run ID | Review pack | Outcome | Date |
| --- | --- | --- | --- | --- | --- |
| 1 | acceptance commit (e5-s04-accepted) | 20261020T062543Z | review/round_1/review_pack.md | reviewed: lead comment on 4.6 (no reliance on earlier experiments) | 2026-10-20 |
| 2 | acceptance commit (e5-s04-accepted) | 20261020T070530Z | review/round_2/review_pack.md | reviewed: 4.6 without Milestone 2 references; other rows unchanged | 2026-10-20 |
| 3 | acceptance commit (e5-s04-accepted) | 20261020T124703Z | review/round_3/review_pack.md | accepted: all comments resolved (G-73, G-76 agreed; G-27 and the tree encoding kept); accepted run 20261020T145604Z on a clean tree, outputs identical to this pack | 2026-10-20 |

## Accepted result (the only result the report and slides may cite)
- Accepted round: 3 - commit: the "s04 accepted" commit, tag `e5-s04-accepted` - run ID: 20261020T145604Z (clean tree, dirty false; evidence identical to review/round_3) - approved by: experiment lead (Wu Qianzong), after team review (Henry) in the doc tab "Implementation reviews › s04 Features" - date: 2026-10-20
- Decisions: threshold 99% and no collinearity drop (G-70); duplicate encoded columns dropped in the fold (G-73); citations only from sources checked in Experiment 5 (G-76); route median for missing distance kept (G-27).

## Deviations from blueprint
- 4.6: verified citation only for the classification delivery proxies (G-76); all other kept features are unmeasured mechanisms.

## Open questions

- Review tab must show a feature × task table (24 contract predictors; kept for regression, kept for classification, reason), built from both feature_dictionary.csv files (promised to Henry in the s02 review, 2.12).
- Review tab must have a section "Imputation inside the folds": per feature the rule (median + missing indicator; route median with fallbacks for distance_km_max; "Unknown" for categoricals), the order (log1p, then impute) and, per fold, the learned medians and the counts filled in training and validation, taken from the fitted pipelines (Henry, s02 review 2.12).
