# Review pack: s07_tuning/regression, round 1

| Field | Value |
| --- | --- |
| Run ID | `20261021T035843Z` |
| Base commit | `9853ce53079c1d92566bcfda96eb9a1540585545` plus uncommitted changes (committed at acceptance) |
| Outputs | FRESH |
| Coverage | 6 implemented, 0 deviation, 0 missing |
| Failed checks | 0 |
| Ready for acceptance | yes |

## Coverage

| ID | Solution step | Coverage | Checks | Changed since last round | Evidence |
| --- | --- | --- | --- | --- | --- |
| [7.1](#card-7-1) | Linear (regression) | IMPLEMENTED | PASS | yes | [grid_results.csv](../../outputs/grid_results.csv) |
| [7.3](#card-7-3) | Decision tree | IMPLEMENTED | PASS | yes | [grid_results.csv](../../outputs/grid_results.csv) |
| [7.4](#card-7-4) | Random forest | IMPLEMENTED | PASS | yes | [grid_results.csv](../../outputs/grid_results.csv) |
| [7.5](#card-7-5) | Search method | IMPLEMENTED | PASS | yes | [grid_results.csv](../../outputs/grid_results.csv), [plain_vs_tuned.csv](../../outputs/plain_vs_tuned.csv), [ladder_preview.csv](../../outputs/ladder_preview.csv), [candidates.csv](../../outputs/candidates.csv), [counts.json](../../outputs/counts.json), [decision.json](../../outputs/decision.json) |
| [7.6](#card-7-6) | Overfitting check | IMPLEMENTED | — | yes | [grid_results.csv](../../outputs/grid_results.csv), [validation_curve_linear.csv](../../outputs/curves/validation_curve_linear.csv), [validation_curve_linear.png](../../outputs/figures/validation_curve_linear.png), [validation_curve_linear.csv](../../outputs/figures/validation_curve_linear.csv), [validation_curve_linear.json](../../outputs/figures/validation_curve_linear.json), [validation_curve_tree.csv](../../outputs/curves/validation_curve_tree.csv), [validation_curve_tree.png](../../outputs/figures/validation_curve_tree.png), [validation_curve_tree.csv](../../outputs/figures/validation_curve_tree.csv), [validation_curve_tree.json](../../outputs/figures/validation_curve_tree.json), [validation_curve_forest.csv](../../outputs/curves/validation_curve_forest.csv), [validation_curve_forest.png](../../outputs/figures/validation_curve_forest.png), [validation_curve_forest.csv](../../outputs/figures/validation_curve_forest.csv), [validation_curve_forest.json](../../outputs/figures/validation_curve_forest.json) |
| [7.7](#card-7-7) | Outputs | IMPLEMENTED | PASS | yes | [predictions.csv.gz](../../outputs/predictions.csv.gz), [oof_scores.csv](../../outputs/oof_scores.csv), [counts.json](../../outputs/counts.json) |

## Evidence cards

### 7.1 Linear (regression) {#card-7-1}

Coverage: **IMPLEMENTED**; checks: **PASS**.

- **What was done:** linear/logistic: 9 configurations; best mean 5.4620 days ({'alpha': 20.0}); one-SE choice {"alpha": 100.0} with 5.4642 ± 0.6711 days.
- **Observation:** Against the plain s06 model (5.4701 days): paired gain of the tuned model +0.0059 days (paired SE 0.0056), better in 4 of 5 folds; carried: plain model. For description only, the best-mean grid point against the plain model: paired gain +0.0081 days (paired SE 0.0035), better in 4 of 5 folds.
- **Reasoning:** The tuned configuration replaces the plain s06 model only if it beats it by more than one standard error of the fold means (G-55); otherwise the simpler plain model stays.
- **Claim type:** observation
- **Check every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output):** PASS linear/logistic 9 configurations; single tree 36 configurations; forest 24 configurations
- **Files:** [grid_results.csv](../../outputs/grid_results.csv)

### 7.3 Decision tree {#card-7-3}

Coverage: **IMPLEMENTED**; checks: **PASS**.

- **What was done:** single tree: 36 configurations; best mean 5.3760 days ({'max_depth': 8, 'min_samples_leaf': 200}); one-SE choice {"max_depth": 4, "min_samples_leaf": 200} with 5.4332 ± 0.7125 days.
- **Observation:** Against the plain s06 model (5.4244 days): paired gain of the tuned model -0.0088 days (paired SE 0.0359), better in 1 of 5 folds; carried: plain model. For description only, the best-mean grid point against the plain model: paired gain +0.0483 days (paired SE 0.0239), better in 4 of 5 folds.
- **Reasoning:** The tuned configuration replaces the plain s06 model only if it beats it by more than one standard error of the fold means (G-55); otherwise the simpler plain model stays.
- **Claim type:** observation
- **Check every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output):** PASS linear/logistic 9 configurations; single tree 36 configurations; forest 24 configurations
- **Check the grid point with the s06 plain settings reproduces the s06 fold scores (tree, forest):** PASS 2 of 2 reproduced
- **Files:** [grid_results.csv](../../outputs/grid_results.csv)

### 7.4 Random forest {#card-7-4}

Coverage: **IMPLEMENTED**; checks: **PASS**.

- **What was done:** forest: 24 configurations; best mean 5.3541 days ({'max_depth': 18, 'max_features': 'sqrt', 'min_samples_leaf': 20}); one-SE choice {"max_depth": 8, "max_features": "sqrt", "min_samples_leaf": 200} with 5.5772 ± 0.6758 days.
- **Observation:** Against the plain s06 model (5.4434 days): paired gain of the tuned model -0.1338 days (paired SE 0.0150), better in 0 of 5 folds; carried: plain model. For description only, the best-mean grid point against the plain model: paired gain +0.0893 days (paired SE 0.0186), better in 5 of 5 folds.
- **Reasoning:** The tuned configuration replaces the plain s06 model only if it beats it by more than one standard error of the fold means (G-55); otherwise the simpler plain model stays.
- **Claim type:** observation
- **Check every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output):** PASS linear/logistic 9 configurations; single tree 36 configurations; forest 24 configurations
- **Check the grid point with the s06 plain settings reproduces the s06 fold scores (tree, forest):** PASS 2 of 2 reproduced
- **Files:** [grid_results.csv](../../outputs/grid_results.csv)

### 7.5 Search method {#card-7-5}

Coverage: **IMPLEMENTED**; checks: **PASS**.

- **What was done:** GridSearchCV over the whole s04 pipeline on the s05 folds, scoring neg_mean_absolute_error, refit=False, return_train_score=True, seed 42; 69 configurations in total. Carried per family: linear/logistic plain s06; single tree plain s06; forest plain s06. Ladder over the carried families (description only; s08 decides): linear/logistic kept over dummy (paired gain +1.0245 days, better in 5 of 5 folds); single tree not kept over linear/logistic (paired gain +0.0458 days, better in 3 of 5 folds); forest not kept over linear/logistic (paired gain +0.0267 days, better in 3 of 5 folds); result linear/logistic.
- **Conclusion:** Selection scores on the folds, not generalisation estimates (G-10). The finalists and the final choice are made in s08 at its gate (G-39).
- **Claim type:** observation
- **Check same folds as s06 (rows per fold equal):** PASS
- **Check every configuration scored on all five folds, whole pipeline refitted per fold:** PASS
- **Check no test row read: every row used was purchased before the test cutoff:** PASS latest purchase 2018-05-27 12:20:21, cutoff 2018-05-27 12:30:34
- **Files:** [grid_results.csv](../../outputs/grid_results.csv), [plain_vs_tuned.csv](../../outputs/plain_vs_tuned.csv), [ladder_preview.csv](../../outputs/ladder_preview.csv), [candidates.csv](../../outputs/candidates.csv), [counts.json](../../outputs/counts.json), [decision.json](../../outputs/decision.json)

### 7.6 Overfitting check {#card-7-6}

Coverage: **IMPLEMENTED**; checks: **—**.

- **What was done:** train_validation_gap for every configuration in grid_results.csv (positive = worse on validation). Gap of each family's one-SE choice: linear/logistic +1.1633 days; single tree +1.0192 days; forest +1.0763 days.
- **Reasoning:** The one-SE choice is already the simplest configuration within the rule, so no simpler configuration within the rule exists to flag; the gaps are reported for the review.
- **Claim type:** observation

![figures/validation_curve_linear.png](../../outputs/figures/validation_curve_linear.png)


![figures/validation_curve_tree.png](../../outputs/figures/validation_curve_tree.png)


![figures/validation_curve_forest.png](../../outputs/figures/validation_curve_forest.png)

- **Files:** [grid_results.csv](../../outputs/grid_results.csv), [validation_curve_linear.csv](../../outputs/curves/validation_curve_linear.csv), [validation_curve_linear.png](../../outputs/figures/validation_curve_linear.png), [validation_curve_linear.csv](../../outputs/figures/validation_curve_linear.csv), [validation_curve_linear.json](../../outputs/figures/validation_curve_linear.json), [validation_curve_tree.csv](../../outputs/curves/validation_curve_tree.csv), [validation_curve_tree.png](../../outputs/figures/validation_curve_tree.png), [validation_curve_tree.csv](../../outputs/figures/validation_curve_tree.csv), [validation_curve_tree.json](../../outputs/figures/validation_curve_tree.json), [validation_curve_forest.csv](../../outputs/curves/validation_curve_forest.csv), [validation_curve_forest.png](../../outputs/figures/validation_curve_forest.png), [validation_curve_forest.csv](../../outputs/figures/validation_curve_forest.csv), [validation_curve_forest.json](../../outputs/figures/validation_curve_forest.json)

### 7.7 Outputs {#card-7-7}

Coverage: **IMPLEMENTED**; checks: **PASS**.

- **What was done:** grid_results.csv, plain_vs_tuned.csv, ladder_preview.csv, candidates.csv, decision.json, out-of-fold predictions of each family's best (predictions.csv.gz) with pooled vs mean-fold scores (oof_scores.csv), validation curves (curves/, figures/); fit times in _manifest.json.
- **Claim type:** observation
- **Check refitting each family's best per fold gives the grid's validation scores:** PASS 15 refits
- **Files:** [predictions.csv.gz](../../outputs/predictions.csv.gz), [oof_scores.csv](../../outputs/oof_scores.csv), [counts.json](../../outputs/counts.json)
