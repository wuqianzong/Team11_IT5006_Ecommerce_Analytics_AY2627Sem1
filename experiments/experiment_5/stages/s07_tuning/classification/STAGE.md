---
node: s07_tuning/classification
owner: TBD
reviewer: TBD
status: ACCEPTED
depends_on:
  - s06_training/classification
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s07_tuning / classification - Tuning

Spec: `spec/pipeline_design.md` -> s07. Teacher/TA rows: `spec/sources.md` (search `S07`).
Blueprint: `spec/blueprints/s07_tuning.md` (implement only when its status is AGREED).

**Gate question:** Is every tuned candidate a complete pipeline scored on the same folds?

## Purpose
Bounded grids on the same folds: logistic C; tree depth and leaf; forest depth and leaf; class weight None vs balanced. Every candidate a whole pipeline.

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
| 7.2 | Logistic (classification): linear/logistic: 18 configurations; best mean 0.2553 ({'C': 0.01, 'class_weight': None}); one-SE choice {"C": 0.01, "class_weight": null} with 0.2553 ± 0.0294. Against the plain s06 model (0.2435): paired gain of the tuned model +0.0118 (paired SE 0.0045), better in 5 of 5 folds; carried: plain model. For description only, the best-mean grid point against the plain model: paired gain +0.0118 (paired SE 0.0045), better in 5 of 5 folds. | code commit 7eb8197; acceptance commit (e5-s07-accepted) | grid_results.csv | IMPLEMENTED | 1 |
| 7.3 | Decision tree: single tree: 72 configurations; best mean 0.2216 ({'class_weight': None, 'max_depth': 10, 'min_samples_leaf': 200}); one-SE choice {"class_weight": null, "max_depth": 4, "min_samples_leaf": 200} with 0.2134 ± 0.0217. Against the plain s06 model (0.2158): paired gain of the tuned model -0.0024 (paired SE 0.0022), better in 2 of 5 folds; carried: plain model. For description only, the best-mean grid point against the plain model: paired gain +0.0058 (paired SE 0.0037), better in 5 of 5 folds. | code commit 7eb8197; acceptance commit (e5-s07-accepted) | grid_results.csv | IMPLEMENTED | 1 |
| 7.4 | Random forest: forest: 48 configurations; best mean 0.2563 ({'class_weight': None, 'max_depth': 10, 'max_features': 'sqrt', 'min_samples_leaf': 20}); one-SE choice {"class_weight": null, "max_depth": 8, "max_features": "sqrt", "min_samples_leaf": 200} with 0.2533 ± 0.0268. Against the plain s06 model (0.2544): paired gain of the tuned model -0.0012 (paired SE 0.0005), better in 1 of 5 folds; carried: plain model. For description only, the best-mean grid point against the plain model: paired gain +0.0019 (paired SE 0.0008), better in 4 of 5 folds. | code commit 7eb8197; acceptance commit (e5-s07-accepted) | grid_results.csv | IMPLEMENTED | 1 |
| 7.5 | Search method: GridSearchCV over the whole s04 pipeline on the s05 folds, scoring average_precision, refit=False, return_train_score=True, seed 42; 138 configurations in total. Carried per family: linear/logistic plain s06; single tree plain s06; forest plain s06. Ladder over the carried families (description only; s08 decides): linear/logistic kept over dummy (paired gain +0.0953, better in 5 of 5 folds); single tree not kept over linear/logistic (paired gain -0.0277, better in 0 of 5 folds); forest not kept over linear/logistic (paired gain +0.0109, better in 4 of 5 folds); result linear/logistic. | code commit 7eb8197; acceptance commit (e5-s07-accepted) | candidates.csv, counts.json, decision.json, grid_results.csv, ladder_preview.csv, plain_vs_tuned.csv | IMPLEMENTED | 1 |
| 7.6 | Overfitting check: train_validation_gap for every configuration in grid_results.csv (positive = worse on validation). Gap of each family's one-SE choice: linear/logistic -0.0440; single tree -0.0200; forest -0.0305. | code commit 7eb8197; acceptance commit (e5-s07-accepted) | curves/validation_curve_forest.csv, curves/validation_curve_linear.csv, curves/validation_curve_tree.csv, figures/validation_curve_forest.png, figures/validation_curve_linear.png, figures/validation_curve_tree.png, grid_results.csv | IMPLEMENTED | 2 |
| 7.7 | Outputs: grid_results.csv, plain_vs_tuned.csv, ladder_preview.csv, candidates.csv, decision.json, out-of-fold predictions of each family's best (predictions.csv.gz) with pooled vs mean-fold scores (oof_scores.csv), validation curves (curves/, figures/); fit times in _manifest.json. | code commit 7eb8197; acceptance commit (e5-s07-accepted) | counts.json, oof_scores.csv, predictions.csv.gz | IMPLEMENTED | 1 |

## Review rounds (append-only; each round has review/round_N/ and a section in the doc tab)
| Round | Commit | Run ID | Review pack | Outcome | Date |
| --- | --- | --- | --- | --- | --- |
| 1 | code commit 7eb8197; acceptance commit (e5-s07-accepted) | 20261021T040619Z | review/round_1/review_pack.md | accepted by the experiment lead (G-78); validation-curve figure colours to be fixed in the acceptance rerun | 2026-10-21 |
| 2 | code commit 7eb8197; acceptance commit (e5-s07-accepted) | 20261021T042900Z | review/round_2/review_pack.md | accepted: clean rerun; only the validation-curve figures changed (dashed training lines in their series colour); every table identical to round 1 | 2026-10-21 |

## Accepted result (the only result the report and slides may cite)
- Accepted round: 2 - commit: the "s07 accepted" commit, tag `e5-s07-accepted` (code 7eb8197) - run ID: 20261021T042900Z (clean tree, dirty false; evidence identical to review/round_2) - approved by: experiment lead (Wu Qianzong) under G-78 (team review of s06-s08 together at the s08 gate) - date: 2026-10-21
- Decisions: one-SE choice inside each grid and against the plain s06 model (G-33, G-55) kept as agreed; the plain s06 model is carried in every family; paired gains and the best-mean grid point are description only; a paired-SE rule is left for the team at the combined s08 review. Class weight in the simplicity order: none before balanced, as built.

## Deviations from blueprint
None.

## Open questions
