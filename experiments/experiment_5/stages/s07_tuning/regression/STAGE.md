---
node: s07_tuning/regression
owner: TBD
reviewer: TBD
status: ACCEPTED
depends_on:
  - s06_training/regression
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s07_tuning / regression - Tuning

Spec: `spec/pipeline_design.md` -> s07. Teacher/TA rows: `spec/sources.md` (search `S07`).
Blueprint: `spec/blueprints/s07_tuning.md` (implement only when its status is AGREED).

**Gate question:** Is every tuned candidate a complete pipeline scored on the same folds?

## Purpose
Bounded grids on the same folds: Ridge alpha; tree depth and leaf; forest depth and leaf. Every candidate a whole pipeline.

## Planned outputs (`outputs/`)
- grid_results.csv (every config: params, fold scores, mean, SD, rank, runtime, convergence)
- predictions.csv.gz (out-of-fold, finalists)

## Gate criteria
- Grids taken from protocol.yaml
- No configuration switched after the search
- Pooled out-of-fold and mean-fold scores kept distinct
<!-- END GENERATED -->

## Working log (README section 9.1; one row per solution ID, every code change names its ID)
| ID | What was built | Commit | Evidence (files, figures) | Coverage | Round |
| --- | --- | --- | --- | --- | --- |
| 7.1 | Linear (regression): linear/logistic: 9 configurations; best mean 5.4620 days ({'alpha': 20.0}); one-SE choice {"alpha": 100.0} with 5.4642 ± 0.6711 days. Against the plain s06 model (5.4701 days): paired gain of the tuned model +0.0059 days (paired SE 0.0056), better in 4 of 5 folds; carried: plain model. For description only, the best-mean grid point against the plain model: paired gain +0.0081 days (paired SE 0.0035), better in 4 of 5 folds. | code commit 7eb8197; acceptance commit (e5-s07-accepted) | grid_results.csv | IMPLEMENTED | 1 |
| 7.3 | Decision tree: single tree: 36 configurations; best mean 5.3760 days ({'max_depth': 8, 'min_samples_leaf': 200}); one-SE choice {"max_depth": 4, "min_samples_leaf": 200} with 5.4332 ± 0.7125 days. Against the plain s06 model (5.4244 days): paired gain of the tuned model -0.0088 days (paired SE 0.0359), better in 1 of 5 folds; carried: plain model. For description only, the best-mean grid point against the plain model: paired gain +0.0483 days (paired SE 0.0239), better in 4 of 5 folds. | code commit 7eb8197; acceptance commit (e5-s07-accepted) | grid_results.csv | IMPLEMENTED | 1 |
| 7.4 | Random forest: forest: 24 configurations; best mean 5.3541 days ({'max_depth': 18, 'max_features': 'sqrt', 'min_samples_leaf': 20}); one-SE choice {"max_depth": 8, "max_features": "sqrt", "min_samples_leaf": 200} with 5.5772 ± 0.6758 days. Against the plain s06 model (5.4434 days): paired gain of the tuned model -0.1338 days (paired SE 0.0150), better in 0 of 5 folds; carried: plain model. For description only, the best-mean grid point against the plain model: paired gain +0.0893 days (paired SE 0.0186), better in 5 of 5 folds. | code commit 7eb8197; acceptance commit (e5-s07-accepted) | grid_results.csv | IMPLEMENTED | 1 |
| 7.5 | Search method: GridSearchCV over the whole s04 pipeline on the s05 folds, scoring neg_mean_absolute_error, refit=False, return_train_score=True, seed 42; 69 configurations in total. Carried per family: linear/logistic plain s06; single tree plain s06; forest plain s06. Ladder over the carried families (description only; s08 decides): linear/logistic kept over dummy (paired gain +1.0245 days, better in 5 of 5 folds); single tree not kept over linear/logistic (paired gain +0.0458 days, better in 3 of 5 folds); forest not kept over linear/logistic (paired gain +0.0267 days, better in 3 of 5 folds); result linear/logistic. | code commit 7eb8197; acceptance commit (e5-s07-accepted) | candidates.csv, counts.json, decision.json, grid_results.csv, ladder_preview.csv, plain_vs_tuned.csv | IMPLEMENTED | 1 |
| 7.6 | Overfitting check: train_validation_gap for every configuration in grid_results.csv (positive = worse on validation). Gap of each family's one-SE choice: linear/logistic +1.1633 days; single tree +1.0192 days; forest +1.0763 days. | code commit 7eb8197; acceptance commit (e5-s07-accepted) | curves/validation_curve_forest.csv, curves/validation_curve_linear.csv, curves/validation_curve_tree.csv, figures/validation_curve_forest.png, figures/validation_curve_linear.png, figures/validation_curve_tree.png, grid_results.csv | IMPLEMENTED | 2 |
| 7.7 | Outputs: grid_results.csv, plain_vs_tuned.csv, ladder_preview.csv, candidates.csv, decision.json, out-of-fold predictions of each family's best (predictions.csv.gz) with pooled vs mean-fold scores (oof_scores.csv), validation curves (curves/, figures/); fit times in _manifest.json. | code commit 7eb8197; acceptance commit (e5-s07-accepted) | counts.json, oof_scores.csv, predictions.csv.gz | IMPLEMENTED | 1 |

## Review rounds (append-only; each round has review/round_N/ and a section in the doc tab)
| Round | Commit | Run ID | Review pack | Outcome | Date |
| --- | --- | --- | --- | --- | --- |
| 1 | code commit 7eb8197; acceptance commit (e5-s07-accepted) | 20261021T035843Z | review/round_1/review_pack.md | accepted by the experiment lead (G-78); validation-curve figure colours to be fixed in the acceptance rerun | 2026-10-21 |
| 2 | code commit 7eb8197; acceptance commit (e5-s07-accepted) | 20261021T042137Z | review/round_2/review_pack.md | accepted: clean rerun; only the validation-curve figures changed (dashed training lines in their series colour); every table identical to round 1 | 2026-10-21 |

## Accepted result (the only result the report and slides may cite)
- Accepted round: 2 - commit: the "s07 accepted" commit, tag `e5-s07-accepted` (code 7eb8197) - run ID: 20261021T042137Z (clean tree, dirty false; evidence identical to review/round_2) - approved by: experiment lead (Wu Qianzong) under G-78 (team review of s06-s08 together at the s08 gate) - date: 2026-10-21
- Decisions: one-SE choice inside each grid and against the plain s06 model (G-33, G-55) kept as agreed; the plain s06 model is carried in every family; paired gains and the best-mean grid point are description only; a paired-SE rule is left for the team at the combined s08 review. Class weight in the simplicity order: none before balanced, as built.

### Changes after acceptance
- 2026-10-23, CR-053/CR-055 (s08 build and freeze): rerun 20261023T084131Z on a clean tree (commit a7329b2, dirty false) after the foundation change (e5lib/selection.py); every value output byte-identical. Status stays ACCEPTED. The combined team review of s06-s08 (G-78) confirmed s07 without change: the agreed one-SE rule is kept.

## Deviations from blueprint
None.

## Open questions
