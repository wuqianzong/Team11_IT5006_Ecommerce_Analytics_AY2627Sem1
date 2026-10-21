---
node: s06_training/regression
owner: TBD
reviewer: TBD
status: ACCEPTED
depends_on:
  - s04_features/regression
  - s05_partition/regression
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s06_training / regression - Training

Spec: `spec/pipeline_design.md` -> s06. Teacher/TA rows: `spec/sources.md` (search `S06`).
Blueprint: `spec/blueprints/s06_training.md` (implement only when its status is AGREED).

**Gate question:** Do the models run basic to complex on identical folds, with each choice justified?

## Purpose
On the s05 folds: median dummy, plain LinearRegression, single decision tree, random forest, each one Pipeline from the s04 recipe; residuals and learning curves; feature set and log transforms fixed by s04 (always on, G-36).

## Planned outputs (`outputs/`)
- metrics_long.csv (train + validation per fold)
- predictions.csv.gz (out-of-fold)
- figures/ (residuals, learning curves)
- decision.json

## Gate criteria
- Identical rows and folds for every candidate
- Preprocessing fitted inside folds
- Simplest model of each family present
- Every model uses the s04 selected features with log transforms on (G-36); no feature or transform testing on the folds
- Each more complex family kept only under the s01 decision rule
<!-- END GENERATED -->

## Working log (README section 9.1; one row per solution ID, every code change names its ID)
| ID | What was built | Commit | Evidence (files, figures) | Coverage | Round |
| --- | --- | --- | --- | --- | --- |
| 6.1 | Pipeline factory: 4 candidates built by e5lib.factory from the s04 recipes.json (one spec per family) with the s06 settings from protocol.yaml; every pipeline fitted inside each of the 5 training folds (176,925 training rows over the folds). Learned imputation values per fold are in imputation_by_fold.csv, with the validation rows whose category level was unseen in the training fold (the one-hot step encodes them as all zeros). | code commit 0734057; acceptance commit (e5-s06-accepted) | imputation_by_fold.csv | IMPLEMENTED | 1 |
| 6.2 | Families, basic to complex: Families basic to complex, validation mae mean ± SE over the folds: dummy 6.4946 ± 0.6889 days; linear/logistic 5.4701 ± 0.6733 days; single tree 5.4244 ± 0.7147 days; forest 5.4434 ± 0.6826 days. Ladder: linear/logistic kept over dummy; single tree not kept over linear/logistic; forest not kept over linear/logistic. One-SE choice over all four: linear/logistic (best mean: single tree). Paired per-fold gain of each step (positive = the more complex family is better; description only, s01 1.7): linear/logistic vs dummy +1.0245 days (paired SE 0.1262), better in 5 of 5 folds; single tree vs linear/logistic +0.0458 days (paired SE 0.0685), better in 3 of 5 folds; forest vs linear/logistic +0.0267 days (paired SE 0.0601), better in 3 of 5 folds. | code commit 0734057; acceptance commit (e5-s06-accepted) | candidates.csv, counts.json, decision.json, figures/family_ladder.png, paired_differences.csv | IMPLEMENTED | 2 |
| 6.4 | Scores recorded: metrics_long.csv: training and validation scores for 4 candidates x 5 folds on every s01 metric; fit_log.csv: rows and warnings per fit, fit times in _manifest.json (convergence warnings: 0); predictions.csv.gz: 248,036 out-of-fold predictions. | code commit 0734057; acceptance commit (e5-s06-accepted) | figures/family_ladder.png, fit_log.csv, metrics_long.csv, predictions.csv.gz | IMPLEMENTED | 3 |
| 6.5 | Residual diagnostics: Residual vs fitted, histogram and Q-Q plot on out-of-fold predictions of the plain linear model and the better tree model (single tree). linear: residual mean 3.32, median 1.28, skewness 2.65, share above +10 days 14.11%; tree: residual mean 3.22, median 1.05, skewness 2.70, share above +10 days 14.16%. | code commit 0734057; acceptance commit (e5-s06-accepted) | curves/residual_quantiles_linear.csv, curves/residual_quantiles_tree.csv, figures/residual_diagnostics.png, predictions.csv.gz | IMPLEMENTED | 1 |
| 6.7 | Learning curves and design matrix: Learning curves on fold 5: the most recent 20, 40, 60, 80 and 100% of its training rows against the same validation block (10,740 rows). Linear/logistic design matrix per training fold: fold 1 rank 128 of 128, condition number 312; fold 2 rank 133 of 133, condition number 341; fold 3 rank 134 of 134, condition number 353; fold 4 rank 137 of 137, condition number 428; fold 5 rank 137 of 137, condition number 454. | code commit 0734057; acceptance commit (e5-s06-accepted) | curves/learning_curves.csv, design_matrix_by_fold.csv, figures/learning_curves.png | IMPLEMENTED | 1 |
| 6.8 | Outputs: Outputs: metrics_long.csv, predictions.csv.gz, candidates.csv, decision.json, fit_log.csv, imputation_by_fold.csv, design_matrix_by_fold.csv, curves/ and figures/ with sidecar data. | code commit 0734057; acceptance commit (e5-s06-accepted) | counts.json | IMPLEMENTED | 1 |

## Review rounds (append-only; each round has review/round_N/ and a section in the doc tab)
| Round | Commit | Run ID | Review pack | Outcome | Date |
| --- | --- | --- | --- | --- | --- |
| 1 | code commit 0734057; acceptance commit (e5-s06-accepted) | 20261021T025126Z | review/round_1/review_pack.md | reviewed by the lead: add the paired fold differences required by s01 1.7 | 2026-10-21 |
| 2 | code commit 0734057; acceptance commit (e5-s06-accepted) | 20261021T031437Z | review/round_2/review_pack.md | superseded before review: a rerun showed forest predictions and fit times differ in the last digits from run to run | 2026-10-21 |
| 3 | code commit 0734057; acceptance commit (e5-s06-accepted) | 20261021T032208Z | review/round_3/review_pack.md | accepted by the experiment lead (G-78; learning-curve subsets confirmed); paired differences added (6.2), forest predicts with one thread and fit times in _manifest.json; decisions unchanged | 2026-10-21 |

## Accepted result (the only result the report and slides may cite)
- Accepted round: 3 - commit: the "s06 accepted" commit, tag `e5-s06-accepted` (code 0734057) - run ID: 20261021T033145Z (clean tree, dirty false; evidence identical to review/round_3) - approved by: experiment lead (Wu Qianzong) under G-78 (team review of s06-s08 together at the s08 gate) - date: 2026-10-21
- Decisions: family ladder under the one-SE rule (G-33), paired fold gains as description only (s01 1.7); learning-curve subsets keep the most recent rows of the latest fold (lead, round 3).

## Deviations from blueprint
None.

## Open questions
