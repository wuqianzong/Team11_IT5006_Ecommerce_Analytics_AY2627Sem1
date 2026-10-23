# s08 selection review pack: regression

Recommendation (one-SE rule, s01 1.7): **linear/logistic** (`reg.sel.log.linear`). Ladder result (each more complex family kept only beyond one SE): linear/logistic.

## Finalists (validation, mean over the five folds)

| family | source | validation_mean | validation_se | train_validation_gap | grid_edge | recommended |
| --- | --- | --- | --- | --- | --- | --- |
| dummy | s06 reference | 6.4946 | 0.6889 | 1.1828 | not a grid configuration (dummy) | False |
| linear/logistic | s06 reference | 5.4701 | 0.6733 | 1.1839 | plain s06 model, not a grid configuration | True |
| single tree | s06 reference | 5.4244 | 0.7147 | 1.0711 | none | False |
| forest | s07 carried (plain s06) | 5.4434 | 0.6826 | 1.0837 | none | False |

## Every s01 metric (mean and SE over the folds)

| family | mae_mean | mae_se | r2_mean | r2_se | rmse_mean | rmse_se | within_3d_mean | within_3d_se |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dummy | 6.4946 | 0.6889 | -0.1355 | 0.0415 | 9.5348 | 1.1572 | 0.3390 | 0.0229 |
| linear/logistic | 5.4701 | 0.6733 | 0.0911 | 0.0729 | 8.5785 | 1.1785 | 0.4654 | 0.0256 |
| single tree | 5.4244 | 0.7147 | 0.0975 | 0.0761 | 8.5599 | 1.2074 | 0.4730 | 0.0303 |
| forest | 5.4434 | 0.6826 | 0.0971 | 0.0728 | 8.5599 | 1.1951 | 0.4583 | 0.0229 |

## Ladder, basic to complex (paired gains are description only)

| comparison | gain_fold_1 | gain_fold_2 | gain_fold_3 | gain_fold_4 | gain_fold_5 | mean_gain | paired_se | folds_better | kept_by_one_se_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear/logistic vs dummy | 0.8707 | 0.6007 | 1.2257 | 1.1670 | 1.2582 | 1.0245 | 0.1262 | 5 | True |
| single tree vs linear/logistic | 0.0210 | 0.1807 | -0.1317 | -0.0643 | 0.2231 | 0.0458 | 0.0685 | 3 | False |
| forest vs linear/logistic | 0.0189 | 0.2254 | -0.1517 | -0.0007 | 0.0418 | 0.0267 | 0.0601 | 3 | False |

## Learning curves of the recommendation (s06, latest fold)

| family | share | train_rows | train_mae | validation_mae |
| --- | --- | --- | --- | --- |
| linear | 0.2000 | 11976 | 4.6255 | 3.3949 |
| linear | 0.4000 | 23952 | 5.1253 | 4.4433 |
| linear | 0.6000 | 35928 | 5.0768 | 4.1482 |
| linear | 0.8000 | 47904 | 4.8466 | 3.9106 |
| linear | 1.0000 | 59880 | 4.8148 | 3.8233 |

## Team decision and freeze (8.5)

Model: `reg.sel.log.linear` (recommended `reg.sel.log.linear`), grid edge action none; Henry; experiment lead (Wu Qianzong), 2026-10-23: one-SE recommendation over the finalists (s01 1.7, G-33); the agreed rule is kept and s06 is not reopened.

Frozen recipe: frozen_recipe.json, sha256 `df4beee32d7b6bef5736e21e53aad6b1caea3233a066c222e46708aca38899d2`. The test cohort is not read; the final fit, test and bundle (8.6-8.8) run together with Pipeline B.
