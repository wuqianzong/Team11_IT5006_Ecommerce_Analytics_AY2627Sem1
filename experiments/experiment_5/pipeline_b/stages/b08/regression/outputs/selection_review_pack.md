# s08 selection review pack: regression

Recommendation (one-SE rule, s01 1.7): **linear/logistic** (`reg.sel.log.linear`). Ladder result (each more complex family kept only beyond one SE): linear/logistic.

## Finalists (validation, mean over the five folds)

| family | source | validation_mean | validation_se | train_validation_gap | grid_edge | recommended |
| --- | --- | --- | --- | --- | --- | --- |
| dummy | s06 reference | 5.9689 | 0.7107 | 1.1751 | not a grid configuration (dummy) | False |
| linear/logistic | s06 reference | 5.0247 | 0.6115 | 1.1640 | plain s06 model, not a grid configuration | True |
| single tree | s06 reference | 5.0532 | 0.6394 | 1.1043 | none | False |
| forest | s07 carried (plain s06) | 4.9627 | 0.6457 | 1.0520 | none | False |

## Every s01 metric (mean and SE over the folds)

| family | mae_mean | mae_se | r2_mean | r2_se | rmse_mean | rmse_se | within_3d_mean | within_3d_se |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dummy | 5.9689 | 0.7107 | -0.1398 | 0.0414 | 8.7467 | 1.2172 | 0.3752 | 0.0259 |
| linear/logistic | 5.0247 | 0.6115 | 0.0873 | 0.0530 | 7.8367 | 1.1084 | 0.5010 | 0.0269 |
| single tree | 5.0532 | 0.6394 | 0.0869 | 0.0498 | 7.8619 | 1.1623 | 0.4926 | 0.0276 |
| forest | 4.9627 | 0.6457 | 0.1148 | 0.0600 | 7.7535 | 1.1711 | 0.4943 | 0.0268 |

## Ladder, basic to complex (paired gains are description only)

| comparison | gain_fold_1 | gain_fold_2 | gain_fold_3 | gain_fold_4 | gain_fold_5 | mean_gain | paired_se | folds_better | kept_by_one_se_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear/logistic vs dummy | 0.6850 | 0.5072 | 1.1860 | 1.3903 | 0.9526 | 0.9442 | 0.1606 | 5 | True |
| single tree vs linear/logistic | 0.0415 | 0.3386 | -0.1652 | -0.2391 | -0.1185 | -0.0285 | 0.1027 | 2 | False |
| forest vs linear/logistic | 0.1377 | 0.2667 | -0.0787 | -0.0931 | 0.0771 | 0.0619 | 0.0677 | 3 | False |

## Learning curves of the recommendation (s06, latest fold)

| family | share | train_rows | train_mae | validation_mae |
| --- | --- | --- | --- | --- |
| linear | 0.2000 | 9483 | 4.3413 | 3.1600 |
| linear | 0.4000 | 18966 | 4.7686 | 4.2864 |
| linear | 0.6000 | 28449 | 4.7639 | 3.8166 |
| linear | 0.8000 | 37932 | 4.4582 | 3.5837 |
| linear | 1.0000 | 47415 | 4.4018 | 3.5469 |

## Team decision and freeze (8.5)

Model: `reg.sel.log.linear` (recommended `reg.sel.log.linear`), grid edge action none; Henry; experiment lead (Wu Qianzong), 2026-10-24: one-SE recommendation over the finalists, same rule as A (s01 1.7, G-33); the forest has the best mean but is within one SE of the plain linear model.

Frozen recipe: frozen_recipe.json, sha256 `fceef777e53fb6a498b227b5aed8d34ef67bf0696dcb6415b4756e52650d26a0`. The test cohort is not read; the final fit, test and bundle (8.6-8.8) run together with Pipeline B.
