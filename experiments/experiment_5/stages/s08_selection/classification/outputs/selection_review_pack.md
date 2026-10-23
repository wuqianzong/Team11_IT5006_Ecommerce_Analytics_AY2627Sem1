# s08 selection review pack: classification

Recommendation (one-SE rule, s01 1.7): **linear/logistic** (`clf.sel.log.logistic`). Ladder result (each more complex family kept only beyond one SE): linear/logistic.

## Finalists (validation, mean over the five folds)

| family | source | validation_mean | validation_se | train_validation_gap | grid_edge | recommended |
| --- | --- | --- | --- | --- | --- | --- |
| dummy | s06 reference | 0.1482 | 0.0198 | -0.0201 | not a grid configuration (dummy) | False |
| linear/logistic | s06 reference | 0.2435 | 0.0314 | -0.0222 | plain s06 model, not a grid configuration | True |
| single tree | s06 reference | 0.2158 | 0.0233 | -0.0080 | none | False |
| forest | s07 carried (plain s06) | 0.2544 | 0.0267 | 0.0025 | none | False |

## Every s01 metric (mean and SE over the folds)

| family | ap_mean | ap_se | brier_mean | brier_se | roc_auc_mean | roc_auc_se |
| --- | --- | --- | --- | --- | --- | --- |
| dummy | 0.1482 | 0.0198 | 0.1269 | 0.0145 | 0.5000 | 0.0000 |
| linear/logistic | 0.2435 | 0.0314 | 0.1243 | 0.0143 | 0.6213 | 0.0161 |
| single tree | 0.2158 | 0.0233 | 0.1242 | 0.0145 | 0.5952 | 0.0104 |
| forest | 0.2544 | 0.0267 | 0.1234 | 0.0143 | 0.6336 | 0.0095 |

## Ladder, basic to complex (paired gains are description only)

| comparison | gain_fold_1 | gain_fold_2 | gain_fold_3 | gain_fold_4 | gain_fold_5 | mean_gain | paired_se | folds_better | kept_by_one_se_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear/logistic vs dummy | 0.0419 | 0.0864 | 0.0952 | 0.1325 | 0.1207 | 0.0953 | 0.0157 | 5 | True |
| single tree vs linear/logistic | -0.0137 | -0.0071 | -0.0143 | -0.0701 | -0.0332 | -0.0277 | 0.0115 | 0 | False |
| forest vs linear/logistic | 0.0193 | 0.0254 | 0.0135 | -0.0114 | 0.0078 | 0.0109 | 0.0063 | 4 | False |

## Learning curves of the recommendation (s06, latest fold)

| family | share | train_rows | train_ap | validation_ap |
| --- | --- | --- | --- | --- |
| linear | 0.2000 | 12072 | 0.3590 | 0.2036 |
| linear | 0.4000 | 24144 | 0.3313 | 0.2162 |
| linear | 0.6000 | 36217 | 0.2997 | 0.2216 |
| linear | 0.8000 | 48289 | 0.2682 | 0.2265 |
| linear | 1.0000 | 60361 | 0.2500 | 0.2288 |

## Calibration (8.3)

Mean Brier raw 0.12426, sigmoid 0.12391; mean AP raw 0.2435, sigmoid 0.2317; one fold SE of raw AP 0.0314. Kept: sigmoid.

## Threshold candidates (8.4, hard stop)

| candidate | threshold | alerts_per_day | alert_rate | error_rate | precision | recall | f1 | cost | extra_false_alarms_per_extra_detractor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| no alerts | inf | 0.0000 | 0.0000 | 0.1499 | 0.0000 | 0.0000 | 0.0000 | 46485.0000 |  |
| 0.50 | 0.5000 | 0.2754 | 0.0015 | 0.1498 | 0.5368 | 0.0055 | 0.0109 | 46274.0000 | 0.8627 |
| 1/6 (cost cutoff) | 0.1667 | 23.8609 | 0.1327 | 0.2156 | 0.2523 | 0.2234 | 0.2370 | 42255.0000 | 3.0163 |
| empirical minimum of 5*FN + FP | 0.1371 | 53.4609 | 0.2974 | 0.3178 | 0.2177 | 0.4319 | 0.2895 | 40839.0000 | 4.2693 |

## Team decision and freeze (8.5)

Model: `clf.sel.log.logistic` (recommended `clf.sel.log.logistic`), grid edge action none; Henry; experiment lead (Wu Qianzong), 2026-10-23: one-SE recommendation over the finalists (s01 1.7, G-33); the agreed rule is kept and s06 is not reopened; sigmoid calibration kept under the agreed rule (8.3).

Threshold: 0.1667 on the sigmoid-calibrated probability, daily alert cap 25; out-of-fold 23.9 alerts/day, precision 0.252, recall 0.223.

Frozen recipe: frozen_recipe.json, sha256 `8de9d4f13159db2d77716df7070f745bea118390cdb3a624cede3ab19d9277d8`. The test cohort is not read; the final fit, test and bundle (8.6-8.8) run together with Pipeline B.
