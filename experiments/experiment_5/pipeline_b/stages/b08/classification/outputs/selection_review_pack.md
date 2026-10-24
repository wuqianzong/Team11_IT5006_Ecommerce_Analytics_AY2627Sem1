# s08 selection review pack: classification

Recommendation (one-SE rule, s01 1.7): **linear/logistic** (`clf.sel.log.logistic`). Ladder result (each more complex family kept only beyond one SE): linear/logistic.

## Finalists (validation, mean over the five folds)

| family | source | validation_mean | validation_se | train_validation_gap | grid_edge | recommended |
| --- | --- | --- | --- | --- | --- | --- |
| dummy | s06 reference | 0.1380 | 0.0198 | -0.0212 | not a grid configuration (dummy) | False |
| linear/logistic | s06 reference | 0.2616 | 0.0349 | -0.0246 | plain s06 model, not a grid configuration | True |
| single tree | s06 reference | 0.2394 | 0.0354 | -0.0199 | none | False |
| forest | s07 carried (plain s06) | 0.2739 | 0.0305 | 0.0129 | none | False |

## Every s01 metric (mean and SE over the folds)

| family | ap_mean | ap_se | brier_mean | brier_se | roc_auc_mean | roc_auc_se |
| --- | --- | --- | --- | --- | --- | --- |
| dummy | 0.1380 | 0.0198 | 0.1197 | 0.0150 | 0.5000 | 0.0000 |
| linear/logistic | 0.2616 | 0.0349 | 0.1141 | 0.0136 | 0.6536 | 0.0150 |
| single tree | 0.2394 | 0.0354 | 0.1135 | 0.0127 | 0.6434 | 0.0138 |
| forest | 0.2739 | 0.0305 | 0.1139 | 0.0139 | 0.6668 | 0.0079 |

## Ladder, basic to complex (paired gains are description only)

| comparison | gain_fold_1 | gain_fold_2 | gain_fold_3 | gain_fold_4 | gain_fold_5 | mean_gain | paired_se | folds_better | kept_by_one_se_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear/logistic vs dummy | 0.0584 | 0.1342 | 0.1330 | 0.1634 | 0.1291 | 0.1236 | 0.0174 | 5 | True |
| single tree vs linear/logistic | -0.0136 | -0.0399 | -0.0163 | -0.0137 | -0.0273 | -0.0222 | 0.0051 | 0 | False |
| forest vs linear/logistic | 0.0245 | 0.0122 | 0.0190 | -0.0061 | 0.0120 | 0.0123 | 0.0052 | 4 | False |

## Learning curves of the recommendation (s06, latest fold)

| family | share | train_rows | train_ap | validation_ap |
| --- | --- | --- | --- | --- |
| linear | 0.2000 | 9447 | 0.3986 | 0.2183 |
| linear | 0.4000 | 18895 | 0.3674 | 0.2173 |
| linear | 0.6000 | 28342 | 0.3368 | 0.2291 |
| linear | 0.8000 | 37790 | 0.3066 | 0.2281 |
| linear | 1.0000 | 47237 | 0.2851 | 0.2301 |

## Calibration (8.3)

Mean Brier raw 0.11414, sigmoid 0.11461; mean AP raw 0.2616, sigmoid 0.2482; one fold SE of raw AP 0.0349. Kept: raw.

## Threshold candidates (8.4, hard stop)

| candidate | threshold | alerts_per_day | alert_rate | error_rate | precision | recall | f1 | cost | extra_false_alarms_per_extra_detractor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| no alerts | inf | 0.0000 | 0.0000 | 0.1394 | 0.0000 | 0.0000 | 0.0000 | 35000.0000 |  |
| 0.50 | 0.5000 | 1.0087 | 0.0069 | 0.1386 | 0.5603 | 0.0279 | 0.0531 | 34178.0000 | 0.7846 |
| 1/6 (cost cutoff) | 0.1667 | 19.1652 | 0.1317 | 0.1936 | 0.2943 | 0.2780 | 0.2859 | 29936.0000 | 2.5774 |
| empirical minimum of 5*FN + FP | 0.1306 | 33.9507 | 0.2333 | 0.2549 | 0.2524 | 0.4223 | 0.3159 | 28977.0000 | 4.0505 |

## Team decision and freeze (8.5)

Model: `clf.sel.log.logistic` (recommended `clf.sel.log.logistic`), grid edge action none; Henry; experiment lead (Wu Qianzong), 2026-10-24: one-SE recommendation over the finalists, same rule as A (s01 1.7, G-33); the forest has the best mean but is within one SE of the plain logistic model; calibration sigmoid by B-G-05.

Threshold: 0.1667 on the raw probability, daily alert cap 25; out-of-fold 19.2 alerts/day, precision 0.294, recall 0.278.

Frozen recipe: frozen_recipe.json, sha256 `337ff3ece7292c06e7c90f95a2b7d530960c108dd3dedddd80b3d9262c8d8c74`. The test cohort is not read; the final fit, test and bundle (8.6-8.8) run together with Pipeline B.
