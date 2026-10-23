---
node: s06_training/classification
owner: TBD
reviewer: TBD
status: ACCEPTED
depends_on:
  - s04_features/classification
  - s05_partition/classification
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s06_training / classification - Training

Spec: `spec/pipeline_design.md` -> s06. Teacher/TA rows: `spec/sources.md` (search `S06`).
Blueprint: `spec/blueprints/s06_training.md` (implement only when its status is AGREED).

**Gate question:** Do the models run basic to complex on identical folds, with each choice justified?

## Purpose
On the s05 folds: prior dummy, unregularised LogisticRegression, single decision tree, random forest, each one Pipeline from the s04 recipe; learning curves; feature set and log transforms fixed by s04 (always on, G-36).

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
| 6.1 | Pipeline factory: 4 candidates built by e5lib.factory from the s04 recipes.json (one spec per family) with the s06 settings from protocol.yaml; every pipeline fitted inside each of the 5 training folds (176,512 training rows over the folds). Learned imputation values per fold are in imputation_by_fold.csv, with the validation rows whose category level was unseen in the training fold (the one-hot step encodes them as all zeros). | code commit 0734057; acceptance commit (e5-s06-accepted) | imputation_by_fold.csv | IMPLEMENTED | 1 |
| 6.2 | Families, basic to complex: Families basic to complex, validation ap mean ± SE over the folds: dummy 0.1482 ± 0.0198; linear/logistic 0.2435 ± 0.0314; single tree 0.2158 ± 0.0233; forest 0.2544 ± 0.0267. Ladder: linear/logistic kept over dummy; single tree not kept over linear/logistic; forest not kept over linear/logistic. One-SE choice over all four: linear/logistic (best mean: forest). Paired per-fold gain of each step (positive = the more complex family is better; description only, s01 1.7): linear/logistic vs dummy +0.0953 (paired SE 0.0157), better in 5 of 5 folds; single tree vs linear/logistic -0.0277 (paired SE 0.0115), better in 0 of 5 folds; forest vs linear/logistic +0.0109 (paired SE 0.0063), better in 4 of 5 folds. | code commit 0734057; acceptance commit (e5-s06-accepted) | candidates.csv, counts.json, decision.json, figures/family_ladder.png, paired_differences.csv | IMPLEMENTED | 2 |
| 6.4 | Scores recorded: metrics_long.csv: training and validation scores for 4 candidates x 5 folds on every s01 metric (threshold metrics at 0.5 and 1/6); fit_log.csv: rows and warnings per fit, fit times in _manifest.json (convergence warnings: 0); predictions.csv.gz: 248,092 out-of-fold predictions. | code commit 0734057; acceptance commit (e5-s06-accepted) | figures/family_ladder.png, fit_log.csv, metrics_long.csv, predictions.csv.gz | IMPLEMENTED | 3 |
| 6.6 | Classification diagnostics: Pooled out-of-fold PR, ROC and reliability curves for every family, Brier score, and the predicted-probability histogram per class for the best non-dummy family. dummy: AP 0.1503, ROC-AUC 0.4990, Brier 0.1281; linear/logistic: AP 0.2297, ROC-AUC 0.6053, Brier 0.1256; single tree: AP 0.2198, ROC-AUC 0.5835, Brier 0.1255; forest: AP 0.2453, ROC-AUC 0.6192, Brier 0.1247. | code commit 0734057; acceptance commit (e5-s06-accepted) | curves/pr_dummy.csv, curves/pr_forest.csv, curves/pr_linear.csv, curves/pr_tree.csv, curves/reliability_dummy.csv, curves/reliability_forest.csv, curves/reliability_linear.csv, curves/reliability_tree.csv, curves/roc_dummy.csv, curves/roc_forest.csv, curves/roc_linear.csv, curves/roc_tree.csv, figures/classification_diagnostics.png, oof_diagnostics.csv, predictions.csv.gz | IMPLEMENTED | 1 |
| 6.7 | Learning curves and design matrix: Learning curves on fold 5: the most recent 20, 40, 60, 80 and 100% of its training rows against the same validation block (10,251 rows). Linear/logistic design matrix per training fold: fold 1 rank 129 of 129, condition number 763; fold 2 rank 134 of 134, condition number 1.03e+03; fold 3 rank 135 of 135, condition number 1.22e+03; fold 4 rank 137 of 137, condition number 1.47e+03; fold 5 rank 138 of 138, condition number 1.55e+03. | code commit 0734057; acceptance commit (e5-s06-accepted) | curves/learning_curves.csv, design_matrix_by_fold.csv, figures/learning_curves.png | IMPLEMENTED | 1 |
| 6.8 | Outputs: Outputs: metrics_long.csv, predictions.csv.gz, candidates.csv, decision.json, fit_log.csv, imputation_by_fold.csv, design_matrix_by_fold.csv, curves/ and figures/ with sidecar data. | code commit 0734057; acceptance commit (e5-s06-accepted) | counts.json | IMPLEMENTED | 1 |

## Review rounds (append-only; each round has review/round_N/ and a section in the doc tab)
| Round | Commit | Run ID | Review pack | Outcome | Date |
| --- | --- | --- | --- | --- | --- |
| 1 | code commit 0734057; acceptance commit (e5-s06-accepted) | 20261021T025217Z | review/round_1/review_pack.md | reviewed by the lead: add the paired fold differences required by s01 1.7 | 2026-10-21 |
| 2 | code commit 0734057; acceptance commit (e5-s06-accepted) | 20261021T031538Z | review/round_2/review_pack.md | superseded before review: a rerun showed forest predictions and fit times differ in the last digits from run to run | 2026-10-21 |
| 3 | code commit 0734057; acceptance commit (e5-s06-accepted) | 20261021T032248Z | review/round_3/review_pack.md | accepted by the experiment lead (G-78; learning-curve subsets confirmed); paired differences added (6.2), forest predicts with one thread and fit times in _manifest.json; decisions unchanged | 2026-10-21 |

## Accepted result (the only result the report and slides may cite)
- Accepted round: 3 - commit: the "s06 accepted" commit, tag `e5-s06-accepted` (code 0734057) - run ID: 20261021T033221Z (clean tree, dirty false; evidence identical to review/round_3) - approved by: experiment lead (Wu Qianzong) under G-78 (team review of s06-s08 together at the s08 gate) - date: 2026-10-21
- Decisions: family ladder under the one-SE rule (G-33), paired fold gains as description only (s01 1.7); learning-curve subsets keep the most recent rows of the latest fold (lead, round 3).

## Changes after acceptance (README section 9.2)
- 2026-10-21, CR-052 (s07 build): rerun 20261021T041825Z on a clean tree (commit 7eb8197, dirty false) after the foundation change (e5lib/tuning.py); every value output byte-identical. Status stays ACCEPTED.
- 2026-10-23, CR-053/CR-055 (s08 build and freeze): rerun 20261023T083612Z on a clean tree (commit a7329b2, dirty false) after the foundation change (e5lib/selection.py); every value output byte-identical. Status stays ACCEPTED.

## Deviations from blueprint
None.

## Open questions
