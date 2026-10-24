# B8 › classification — gate evidence

Round 1 · AT THE GATE, not frozen · run `20261024T032112Z` on uncommitted code (working tree on 171f23d) · 9 checks, all PASS · the test cohort is not read. Coverage and review dropdowns are on the parent tab "B8 Selection".

*Text from A's code refers to B's inputs: "s04 recipe" = B4, "s05 folds" = B5, "s06"/"s07" = B6/B7, and "spec/human\_decisions.yaml section s08" = pipeline\_b/spec/human\_decisions\_B.yaml section b08.*

## B8.1–B8.4 Selection review pack (written by A's s08 code on B's inputs)

Cards: 

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

## Team decision (A's wording; for B read human\_decisions\_B.yaml section b08)

Record in spec/human_decisions.yaml, section s08.classification: `model` (chosen, recommended, rationale, grid_edge_action, decided_by, date), `threshold` (value, daily_alert_cap, rationale, decided_by, date). Under G-78 this is decided at the combined review of s06-s08; only then do 8.5-8.8 run.

## Fold-by-fold results of every finalist (metrics\_long.csv, validation)

**ap** per fold (columns: finalist family):

| fold | dummy\_prior | forest\_clf | logistic | tree\_clf |
| --- | --- | --- | --- | --- |
| 1 | 0.0982 | 0.1810 | 0.1566 | 0.1430 |
| 2 | 0.1395 | 0.2859 | 0.2738 | 0.2338 |
| 3 | 0.1433 | 0.2952 | 0.2762 | 0.2599 |
| 4 | 0.2079 | 0.3652 | 0.3713 | 0.3575 |
| 5 | 0.1010 | 0.2421 | 0.2301 | 0.2028 |

**roc_auc** per fold (columns: finalist family):

| fold | dummy\_prior | forest\_clf | logistic | tree\_clf |
| --- | --- | --- | --- | --- |
| 1 | 0.5000 | 0.6356 | 0.5975 | 0.5953 |
| 2 | 0.5000 | 0.6749 | 0.6655 | 0.6381 |
| 3 | 0.5000 | 0.6697 | 0.6502 | 0.6445 |
| 4 | 0.5000 | 0.6745 | 0.6839 | 0.6762 |
| 5 | 0.5000 | 0.6793 | 0.6708 | 0.6627 |

**brier** per fold (columns: finalist family):

| fold | dummy\_prior | forest\_clf | logistic | tree\_clf |
| --- | --- | --- | --- | --- |
| 1 | 0.0889 | 0.0868 | 0.0875 | 0.0874 |
| 2 | 0.1212 | 0.1160 | 0.1170 | 0.1160 |
| 3 | 0.1240 | 0.1175 | 0.1166 | 0.1173 |
| 4 | 0.1723 | 0.1628 | 0.1618 | 0.1574 |
| 5 | 0.0919 | 0.0867 | 0.0878 | 0.0891 |

**Calibration per fold** (calibration\_folds.csv):

| variant | fold | ap | brier | roc\_auc |
| --- | --- | --- | --- | --- |
| raw | 1 | 0.1566 | 0.0875 | 0.5975 |
| sigmoid | 1 | 0.1468 | 0.0885 | 0.5810 |
| raw | 2 | 0.2738 | 0.1170 | 0.6655 |
| sigmoid | 2 | 0.2575 | 0.1169 | 0.6477 |
| raw | 3 | 0.2762 | 0.1166 | 0.6502 |
| sigmoid | 3 | 0.2641 | 0.1184 | 0.6332 |
| raw | 4 | 0.3713 | 0.1618 | 0.6839 |
| sigmoid | 4 | 0.3411 | 0.1616 | 0.6556 |
| raw | 5 | 0.2301 | 0.0878 | 0.6708 |
| sigmoid | 5 | 0.2316 | 0.0876 | 0.6687 |

**Reliability, raw vs sigmoid** (curves/reliability\_raw\_vs\_sigmoid.csv: mean predicted probability vs observed detractor share per bin; on the diagonal = well calibrated):

| variant | mean\_predicted | observed\_share |
| --- | --- | --- |
| raw | 0.0378 | 0.0697 |
| raw | 0.0581 | 0.0789 |
| raw | 0.0685 | 0.0952 |
| raw | 0.0777 | 0.0936 |
| raw | 0.0865 | 0.1113 |
| raw | 0.0968 | 0.1215 |
| raw | 0.1094 | 0.1372 |
| raw | 0.1273 | 0.1603 |
| raw | 0.1596 | 0.2153 |
| raw | 0.2965 | 0.3110 |
| sigmoid | 0.0590 | 0.0848 |
| sigmoid | 0.0850 | 0.0958 |
| sigmoid | 0.0962 | 0.0950 |
| sigmoid | 0.1056 | 0.1077 |
| sigmoid | 0.1132 | 0.0998 |
| sigmoid | 0.1186 | 0.1070 |
| sigmoid | 0.1242 | 0.1227 |
| sigmoid | 0.1334 | 0.1575 |
| sigmoid | 0.1553 | 0.2175 |
| sigmoid | 0.2507 | 0.3063 |

**Best threshold under each daily alert cap** (threshold\_by\_cap.csv, from the threshold curve on a 0.01 grid; lowest illustrative cost 5·FN + FP within the cap):

| daily\_alert\_cap | best\_threshold\_in\_curve | alerts\_per\_day | precision | recall | cost |
| --- | --- | --- | --- | --- | --- |
| 5 | 0.3000 | 4.9681 | 0.4096 | 0.1003 | 32502.0000 |
| 10 | 0.2300 | 9.2435 | 0.3512 | 0.1600 | 31469.0000 |
| 15 | 0.1900 | 14.2145 | 0.3132 | 0.2194 | 30688.0000 |
| 20 | 0.1700 | 18.2928 | 0.2965 | 0.2673 | 30085.0000 |
| 25 | 0.1500 | 24.5507 | 0.2764 | 0.3344 | 29424.0000 |
| 30 | 0.1400 | 28.9333 | 0.2630 | 0.3750 | 29232.0000 |
| 35 | 0.1300 | 34.3304 | 0.2509 | 0.4246 | 29012.0000 |
| 40 | 0.1300 | 34.3304 | 0.2509 | 0.4246 | 29012.0000 |
| 50 | 0.1300 | 34.3304 | 0.2509 | 0.4246 | 29012.0000 |

**Threshold candidates fold by fold** (threshold\_by\_fold.csv, raw recommended model):

| fold | candidate | threshold | alerts | tp | fp | fn | precision | recall | cost |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.50 | 0.5000 | 34 | 15 | 19 | 999 | 0.4412 | 0.0148 | 5014.0000 |
| 1 | 1/6 (cost cutoff) | 0.1667 | 786 | 155 | 631 | 859 | 0.1972 | 0.1529 | 4926.0000 |
| 1 | empirical minimum of 5*FN + FP | 0.1306 | 1,767 | 286 | 1,481 | 728 | 0.1619 | 0.2821 | 5121.0000 |
| 2 | 0.50 | 0.5000 | 32 | 17 | 15 | 1,426 | 0.5312 | 0.0118 | 7145.0000 |
| 2 | 1/6 (cost cutoff) | 0.1667 | 646 | 258 | 388 | 1,185 | 0.3994 | 0.1788 | 6313.0000 |
| 2 | empirical minimum of 5*FN + FP | 0.1306 | 1,120 | 385 | 735 | 1,058 | 0.3438 | 0.2668 | 6025.0000 |
| 3 | 0.50 | 0.5000 | 83 | 52 | 31 | 1,445 | 0.6265 | 0.0347 | 7256.0000 |
| 3 | 1/6 (cost cutoff) | 0.1667 | 1,546 | 452 | 1,094 | 1,045 | 0.2924 | 0.3019 | 6319.0000 |
| 3 | empirical minimum of 5*FN + FP | 0.1306 | 2,975 | 715 | 2,260 | 782 | 0.2403 | 0.4776 | 6170.0000 |
| 4 | 0.50 | 0.5000 | 89 | 56 | 33 | 2,117 | 0.6292 | 0.0258 | 10618.0000 |
| 4 | 1/6 (cost cutoff) | 0.1667 | 1,703 | 694 | 1,009 | 1,479 | 0.4075 | 0.3194 | 8404.0000 |
| 4 | empirical minimum of 5*FN + FP | 0.1306 | 2,955 | 1,079 | 1,876 | 1,094 | 0.3651 | 0.4965 | 7346.0000 |
| 5 | 0.50 | 0.5000 | 110 | 55 | 55 | 818 | 0.5000 | 0.0630 | 4145.0000 |
| 5 | 1/6 (cost cutoff) | 0.1667 | 1,931 | 387 | 1,544 | 486 | 0.2004 | 0.4433 | 3974.0000 |
| 5 | empirical minimum of 5*FN + FP | 0.1306 | 2,896 | 491 | 2,405 | 382 | 0.1695 | 0.5624 | 4315.0000 |

**Full threshold curve** (curves/threshold\_curve.csv, out-of-fold over all five folds):

| threshold | alerts | alerts\_per\_day | precision | recall | f1 | cost | tp | fp | fn |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.6000 | 157 | 0.4551 | 0.6115 | 0.0137 | 0.0268 | 34581.0000 | 96 | 61 | 6,904 |
| 0.5900 | 175 | 0.5072 | 0.6057 | 0.0151 | 0.0295 | 34539.0000 | 106 | 69 | 6,894 |
| 0.5800 | 186 | 0.5391 | 0.6075 | 0.0161 | 0.0315 | 34508.0000 | 113 | 73 | 6,887 |
| 0.5700 | 195 | 0.5652 | 0.5897 | 0.0164 | 0.0320 | 34505.0000 | 115 | 80 | 6,885 |
| 0.5600 | 211 | 0.6116 | 0.5687 | 0.0171 | 0.0333 | 34491.0000 | 120 | 91 | 6,880 |
| 0.5500 | 227 | 0.6580 | 0.5639 | 0.0183 | 0.0354 | 34459.0000 | 128 | 99 | 6,872 |
| 0.5400 | 241 | 0.6986 | 0.5685 | 0.0196 | 0.0378 | 34419.0000 | 137 | 104 | 6,863 |
| 0.5300 | 264 | 0.7652 | 0.5720 | 0.0216 | 0.0416 | 34358.0000 | 151 | 113 | 6,849 |
| 0.5200 | 287 | 0.8319 | 0.5749 | 0.0236 | 0.0453 | 34297.0000 | 165 | 122 | 6,835 |
| 0.5100 | 312 | 0.9043 | 0.5769 | 0.0257 | 0.0492 | 34232.0000 | 180 | 132 | 6,820 |
| 0.5000 | 348 | 1.0087 | 0.5603 | 0.0279 | 0.0531 | 34178.0000 | 195 | 153 | 6,805 |
| 0.4900 | 387 | 1.1217 | 0.5556 | 0.0307 | 0.0582 | 34097.0000 | 215 | 172 | 6,785 |
| 0.4800 | 412 | 1.1942 | 0.5437 | 0.0320 | 0.0604 | 34068.0000 | 224 | 188 | 6,776 |
| 0.4700 | 435 | 1.2609 | 0.5356 | 0.0333 | 0.0627 | 34037.0000 | 233 | 202 | 6,767 |
| 0.4600 | 462 | 1.3391 | 0.5260 | 0.0347 | 0.0651 | 34004.0000 | 243 | 219 | 6,757 |
| 0.4500 | 496 | 1.4377 | 0.5222 | 0.0370 | 0.0691 | 33942.0000 | 259 | 237 | 6,741 |
| 0.4400 | 544 | 1.5768 | 0.5110 | 0.0397 | 0.0737 | 33876.0000 | 278 | 266 | 6,722 |
| 0.4300 | 590 | 1.7101 | 0.5068 | 0.0427 | 0.0788 | 33796.0000 | 299 | 291 | 6,701 |
| 0.4200 | 642 | 1.8609 | 0.5000 | 0.0459 | 0.0840 | 33716.0000 | 321 | 321 | 6,679 |
| 0.4100 | 705 | 2.0435 | 0.4979 | 0.0501 | 0.0911 | 33599.0000 | 351 | 354 | 6,649 |
| 0.4000 | 766 | 2.2203 | 0.4883 | 0.0534 | 0.0963 | 33522.0000 | 374 | 392 | 6,626 |
| 0.3900 | 835 | 2.4203 | 0.4886 | 0.0583 | 0.1041 | 33387.0000 | 408 | 427 | 6,592 |
| 0.3800 | 903 | 2.6174 | 0.4817 | 0.0621 | 0.1101 | 33293.0000 | 435 | 468 | 6,565 |
| 0.3700 | 990 | 2.8696 | 0.4747 | 0.0671 | 0.1176 | 33170.0000 | 470 | 520 | 6,530 |
| 0.3600 | 1,057 | 3.0638 | 0.4655 | 0.0703 | 0.1221 | 33105.0000 | 492 | 565 | 6,508 |
| 0.3500 | 1,129 | 3.2725 | 0.4579 | 0.0739 | 0.1272 | 33027.0000 | 517 | 612 | 6,483 |
| 0.3400 | 1,226 | 3.5536 | 0.4535 | 0.0794 | 0.1352 | 32890.0000 | 556 | 670 | 6,444 |
| 0.3300 | 1,338 | 3.8783 | 0.4387 | 0.0839 | 0.1408 | 32816.0000 | 587 | 751 | 6,413 |
| 0.3200 | 1,463 | 4.2406 | 0.4306 | 0.0900 | 0.1489 | 32683.0000 | 630 | 833 | 6,370 |
| 0.3100 | 1,581 | 4.5826 | 0.4219 | 0.0953 | 0.1555 | 32579.0000 | 667 | 914 | 6,333 |
| 0.3000 | 1,714 | 4.9681 | 0.4096 | 0.1003 | 0.1611 | 32502.0000 | 702 | 1,012 | 6,298 |
| 0.2900 | 1,876 | 5.4377 | 0.4003 | 0.1073 | 0.1692 | 32370.0000 | 751 | 1,125 | 6,249 |
| 0.2800 | 2,038 | 5.9072 | 0.3901 | 0.1136 | 0.1759 | 32268.0000 | 795 | 1,243 | 6,205 |
| 0.2700 | 2,217 | 6.4261 | 0.3834 | 0.1214 | 0.1844 | 32117.0000 | 850 | 1,367 | 6,150 |
| 0.2600 | 2,408 | 6.9797 | 0.3750 | 0.1290 | 0.1920 | 31990.0000 | 903 | 1,505 | 6,097 |
| 0.2500 | 2,633 | 7.6319 | 0.3680 | 0.1384 | 0.2012 | 31819.0000 | 969 | 1,664 | 6,031 |
| 0.2400 | 2,899 | 8.4029 | 0.3598 | 0.1490 | 0.2107 | 31641.0000 | 1,043 | 1,856 | 5,957 |
| 0.2300 | 3,189 | 9.2435 | 0.3512 | 0.1600 | 0.2198 | 31469.0000 | 1,120 | 2,069 | 5,880 |
| 0.2200 | 3,480 | 10.0870 | 0.3451 | 0.1716 | 0.2292 | 31274.0000 | 1,201 | 2,279 | 5,799 |
| 0.2100 | 3,888 | 11.2696 | 0.3320 | 0.1844 | 0.2371 | 31142.0000 | 1,291 | 2,597 | 5,709 |
| 0.2000 | 4,331 | 12.5536 | 0.3221 | 0.1993 | 0.2462 | 30961.0000 | 1,395 | 2,936 | 5,605 |
| 0.1900 | 4,904 | 14.2145 | 0.3132 | 0.2194 | 0.2581 | 30688.0000 | 1,536 | 3,368 | 5,464 |
| 0.1800 | 5,529 | 16.0261 | 0.3071 | 0.2426 | 0.2711 | 30341.0000 | 1,698 | 3,831 | 5,302 |
| 0.1700 | 6,311 | 18.2928 | 0.2965 | 0.2673 | 0.2811 | 30085.0000 | 1,871 | 4,440 | 5,129 |
| 0.1600 | 7,282 | 21.1072 | 0.2859 | 0.2974 | 0.2916 | 29790.0000 | 2,082 | 5,200 | 4,918 |
| 0.1500 | 8,470 | 24.5507 | 0.2764 | 0.3344 | 0.3027 | 29424.0000 | 2,341 | 6,129 | 4,659 |
| 0.1400 | 9,982 | 28.9333 | 0.2630 | 0.3750 | 0.3092 | 29232.0000 | 2,625 | 7,357 | 4,375 |
| 0.1300 | 11,844 | 34.3304 | 0.2509 | 0.4246 | 0.3154 | 29012.0000 | 2,972 | 8,872 | 4,028 |
| 0.1200 | 14,245 | 41.2899 | 0.2332 | 0.4746 | 0.3127 | 29313.0000 | 3,322 | 10,923 | 3,678 |
| 0.1100 | 17,275 | 50.0725 | 0.2181 | 0.5383 | 0.3104 | 29667.0000 | 3,768 | 13,507 | 3,232 |
| 0.1000 | 21,190 | 61.4203 | 0.2021 | 0.6117 | 0.3038 | 30498.0000 | 4,282 | 16,908 | 2,718 |
| 0.0900 | 25,794 | 74.7652 | 0.1868 | 0.6883 | 0.2938 | 31886.0000 | 4,818 | 20,976 | 2,182 |
| 0.0800 | 31,293 | 90.7043 | 0.1731 | 0.7737 | 0.2829 | 33797.0000 | 5,416 | 25,877 | 1,584 |
| 0.0700 | 36,880 | 106.8986 | 0.1610 | 0.8481 | 0.2706 | 36258.0000 | 5,937 | 30,943 | 1,063 |
| 0.0600 | 41,968 | 121.6464 | 0.1528 | 0.9159 | 0.2618 | 38502.0000 | 6,411 | 35,557 | 589 |
| 0.0500 | 45,756 | 132.6261 | 0.1462 | 0.9557 | 0.2536 | 40616.0000 | 6,690 | 39,066 | 310 |
| 0.0400 | 47,915 | 138.8841 | 0.1429 | 0.9781 | 0.2494 | 41833.0000 | 6,847 | 41,068 | 153 |
| 0.0300 | 49,074 | 142.2435 | 0.1411 | 0.9894 | 0.2470 | 42518.0000 | 6,926 | 42,148 | 74 |
| 0.0200 | 49,695 | 144.0435 | 0.1401 | 0.9949 | 0.2457 | 42911.0000 | 6,964 | 42,731 | 36 |

**Checks (A's s08 code)**

- PASS: finalists refitted on the same rows and folds reproduce their s06 fold scores (4 of 4 reproduced)
- PASS: finalists: the dummy, plain linear/logistic and single tree references plus each family's s07 carried model (4 finalists)
- PASS: no test row read: every row used was purchased before the test cutoff (latest purchase 2018-05-23 11:29:51, cutoff 2018-05-26 12:16:34)
- PASS: the run stops at the gate: no frozen\_recipe.json, the test cohort is not read (G-39, G-78) (team decisions in human\_decisions.yaml s08: not yet made)
- PASS: calibration inner splits are time-ordered: every training fold sorted by purchase time

## B8.A Adoption comparison and mean ± SE by population (G-79; Henry R-02)

**What was done:** Adoption comparison (G-79) on AP: A's frozen model (clf.sel.log.logistic) refitted per fold on A's training rows vs B's recommended model (clf.sel.log.logistic), both on B's validation rows. Mean paired gain of B over A +0.0197 (paired SE 0.0050), B better in 5 of 5 folds; folds 2-5 (description only, B-G-01): +0.0207. By the fold rule B is adopted for classification; A and B both go to the joint test run. Mean and SE by population are in population\_summary.csv (R-02).

**Per fold, on B's validation rows** (adoption\_comparison.csv; positive gain = B better):

| fold | b\_rows | a\_model\_on\_b\_rows | b\_model\_on\_b\_rows | paired\_gain\_b\_over\_a |
| --- | --- | --- | --- | --- |
| 1 | 10,324 | 0.1407 | 0.1566 | 0.0158 |
| 2 | 10,342 | 0.2386 | 0.2738 | 0.0351 |
| 3 | 10,450 | 0.2500 | 0.2762 | 0.0262 |
| 4 | 10,453 | 0.3563 | 0.3713 | 0.0150 |
| 5 | 8,646 | 0.2237 | 0.2301 | 0.0064 |

**Decision record** (adoption\_decision.json): mean paired gain +0.0197 (paired SE 0.0050), B better in 5 of 5 folds; folds 2–5 +0.0207 (description only). Rule: B is adopted for the task when its 5-fold mean beats A's on the same B rows, even by a thin margin (G-79); folds 2-5 are description only (B-G-01); both go to the joint test run. Result: B adopted on the folds.

**Every finalist against A on the same rows** (adoption\_by\_finalist\_summary.csv): would B still be adopted if the team chose another finalist?

| candidate\_id | family | b\_mean | gain\_mean | gain\_se | folds\_b\_better | b\_adopted\_on\_folds\_if\_chosen |
| --- | --- | --- | --- | --- | --- | --- |
| clf.sel.log.dummy\_prior | dummy | 0.1380 | -0.1039 | 0.0175 | 0 | False |
| clf.sel.log.logistic | linear/logistic | 0.2616 | 0.0197 | 0.0050 | 5 | True |
| clf.sel.log.tree\_clf.max\_depth=5.min\_samples\_leaf=100 | single tree | 0.2394 | -0.0025 | 0.0052 | 3 | False |
| clf.sel.log.forest\_clf.max\_depth=10.max\_features=sqrt.min\_samples\_leaf=50 | forest | 0.2739 | 0.0320 | 0.0077 | 5 | True |

**Fold by fold, every finalist** (adoption\_by\_finalist.csv; gain > 0 = B better):

| candidate\_id | family | fold | a\_model\_on\_b\_rows | b\_model\_on\_b\_rows | paired\_gain\_b\_over\_a |
| --- | --- | --- | --- | --- | --- |
| dummy\_prior | dummy | 1 | 0.1407 | 0.0982 | -0.0425 |
| dummy\_prior | dummy | 2 | 0.2386 | 0.1395 | -0.0991 |
| dummy\_prior | dummy | 3 | 0.2500 | 0.1433 | -0.1068 |
| dummy\_prior | dummy | 4 | 0.3563 | 0.2079 | -0.1484 |
| dummy\_prior | dummy | 5 | 0.2237 | 0.1010 | -0.1227 |
| logistic | linear/logistic | 1 | 0.1407 | 0.1566 | 0.0158 |
| logistic | linear/logistic | 2 | 0.2386 | 0.2738 | 0.0351 |
| logistic | linear/logistic | 3 | 0.2500 | 0.2762 | 0.0262 |
| logistic | linear/logistic | 4 | 0.3563 | 0.3713 | 0.0150 |
| logistic | linear/logistic | 5 | 0.2237 | 0.2301 | 0.0064 |
| tree\_clf | single tree | 1 | 0.1407 | 0.1430 | 0.0023 |
| tree\_clf | single tree | 2 | 0.2386 | 0.2338 | -0.0048 |
| tree\_clf | single tree | 3 | 0.2500 | 0.2599 | 0.0099 |
| tree\_clf | single tree | 4 | 0.3563 | 0.3575 | 0.0012 |
| tree\_clf | single tree | 5 | 0.2237 | 0.2028 | -0.0209 |
| forest\_clf | forest | 1 | 0.1407 | 0.1810 | 0.0403 |
| forest\_clf | forest | 2 | 0.2386 | 0.2859 | 0.0473 |
| forest\_clf | forest | 3 | 0.2500 | 0.2952 | 0.0452 |
| forest\_clf | forest | 4 | 0.3563 | 0.3652 | 0.0089 |
| forest\_clf | forest | 5 | 0.2237 | 0.2421 | 0.0184 |

**Mean and SE by population** (population\_summary.csv):

| population\_and\_model | metric | mean\_5\_folds | se\_5\_folds | mean\_folds\_2\_5 | se\_folds\_2\_5 |
| --- | --- | --- | --- | --- | --- |
| A's frozen model on A's validation rows | ap | 0.2435 | 0.0314 | 0.2661 | 0.0282 |
| A's frozen model on B's validation rows | ap | 0.2419 | 0.0344 | 0.2672 | 0.0302 |
| B's recommended model (clf.sel.log.logistic) on B's validation rows | ap | 0.2616 | 0.0349 | 0.2878 | 0.0298 |

**Per-fold decomposition** (se\_decomposition.csv): A on A's rows → A on B's rows isolates B's scope; A on B's rows → B on B's rows isolates B's features and prediction time.

| fold | a\_rows | b\_rows | a\_model\_on\_a\_rows | a\_model\_on\_b\_rows | b\_model\_on\_b\_rows |
| --- | --- | --- | --- | --- | --- |
| 1 | 12,956 | 10,324 | 0.1531 | 0.1407 | 0.1566 |
| 2 | 12,950 | 10,342 | 0.2396 | 0.2386 | 0.2738 |
| 3 | 12,941 | 10,450 | 0.2461 | 0.2500 | 0.2762 |
| 4 | 12,925 | 10,453 | 0.3500 | 0.3563 | 0.3713 |
| 5 | 10,251 | 8,646 | 0.2288 | 0.2237 | 0.2301 |

- PASS: A's frozen recipe unchanged: sha256 recomputes and A's selected spec matches it (sha256 8de9d4f13159…)
- PASS: A's refit reproduces A's stored s06 out-of-fold predictions on A's validation rows (max difference 1.11e-16)
- PASS: B's validation rows and labels are exactly B5's, in every fold (50,215 validation rows)

## B8.M Missed-dispatch rule (B-C10)

**What was done:** Population: A-eligible classification development orders in the seven states with a distance, after the warm-up (61,827 orders, 8,884 detractors). The rule fires when the last shipping limit passes with no carrier handover: 5,904 orders, 1,805 detractors (precision 0.306, 20.3% of all detractors). A rule, not a model (B-C10).

(missed\_dispatch\_rule.csv)

| group | orders | detractors | precision | share\_of\_all\_detractors |
| --- | --- | --- | --- | --- |
| never handed over | 429 | 374 | 0.8718 | 0.0421 |
| handed over after the limit | 5,475 | 1,431 | 0.2614 | 0.1611 |
| all flagged (rule fires) | 5,904 | 1,805 | 0.3057 | 0.2032 |
| not flagged | 55,923 | 7,079 | 0.1266 | 0.7968 |

- PASS: missed-dispatch groups add up to the population (61,827 orders)

**Files**: pipeline\_b/stages/b08/classification/outputs/ (run 20261024T032112Z): adoption\_by\_finalist.csv, adoption\_by\_finalist\_summary.csv, adoption\_comparison.csv, adoption\_decision.json, calibration\_folds.csv, candidates.csv, counts.json, decision.json, ladder.csv, metrics\_long.csv, missed\_dispatch\_rule.csv, population\_summary.csv, predictions.csv.gz, se\_decomposition.csv, selected\_spec.json, selection\_review\_pack.md, threshold\_by\_cap.csv, threshold\_by\_fold.csv, threshold\_table.csv; plus figures/ and curves/.