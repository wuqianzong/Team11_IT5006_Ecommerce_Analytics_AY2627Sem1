# s08 Selection › classification — evidence cards

## Supplement for decisions and the report (added 2026-10-24; DOC\_GAPS D-05)

Added after the pipeline ran, from accepted outputs only; nothing above is changed. Charts marked doc\_support come from pipeline\_b/stages/doc\_support/classification/outputs (run 20261024T065723Z, uncommitted, reads accepted outputs only). Source: A's s08 outputs at e5-A-frozen (run 20261023T085014Z).

**Per-fold AP of every finalist** (A's s08 metrics\_long.csv; selection scores):

| candidate\_id | phase | fold\_1 | fold\_2 | fold\_3 | fold\_4 | fold\_5 | mean | se |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| clf.sel.log.dummy\_prior | train | 0.1273 | 0.1187 | 0.1190 | 0.1317 | 0.1440 | 0.1281 | 0.0047 |
| clf.sel.log.dummy\_prior | validation | 0.1111 | 0.1533 | 0.1509 | 0.2175 | 0.1081 | 0.1482 | 0.0198 |
| clf.sel.log.forest\_clf.max\_depth=10.max\_features=sqrt.min\_samples\_leaf=50 | train | 0.2660 | 0.2325 | 0.2346 | 0.2704 | 0.2815 | 0.2570 | 0.0099 |
| clf.sel.log.forest\_clf.max\_depth=10.max\_features=sqrt.min\_samples\_leaf=50 | validation | 0.1724 | 0.2650 | 0.2596 | 0.3386 | 0.2365 | 0.2544 | 0.0267 |
| clf.sel.log.logistic | train | 0.2206 | 0.1988 | 0.2040 | 0.2332 | 0.2500 | 0.2213 | 0.0094 |
| clf.sel.log.logistic | validation | 0.1531 | 0.2396 | 0.2461 | 0.3500 | 0.2288 | 0.2435 | 0.0314 |
| clf.sel.log.tree\_clf.max\_depth=5.min\_samples\_leaf=100 | train | 0.1922 | 0.1833 | 0.1901 | 0.2280 | 0.2452 | 0.2078 | 0.0122 |
| clf.sel.log.tree\_clf.max\_depth=5.min\_samples\_leaf=100 | validation | 0.1393 | 0.2325 | 0.2318 | 0.2798 | 0.1956 | 0.2158 | 0.0233 |

**Best threshold under each daily alert cap** (doc\_support a\_threshold\_by\_cap.csv, from A's s08 curves/threshold\_curve.csv):

| daily\_alert\_cap | best\_threshold\_in\_curve | alerts\_per\_day | precision | recall | cost |
| --- | --- | --- | --- | --- | --- |
| 5 | 0.2500 | 4.7275 | 0.3581 | 0.0628 | 44612.0000 |
| 10 | 0.2100 | 9.2087 | 0.3138 | 0.1072 | 43680.0000 |
| 15 | 0.1900 | 14.0290 | 0.2787 | 0.1451 | 43231.0000 |
| 20 | 0.1800 | 17.5072 | 0.2652 | 0.1723 | 42913.0000 |
| 25 | 0.1700 | 21.9710 | 0.2565 | 0.2091 | 42401.0000 |
| 30 | 0.1600 | 28.2899 | 0.2459 | 0.2581 | 41845.0000 |
| 35 | 0.1600 | 28.2899 | 0.2459 | 0.2581 | 41845.0000 |
| 40 | 0.1500 | 36.8986 | 0.2327 | 0.3186 | 41443.0000 |
| 50 | 0.1400 | 48.9971 | 0.2212 | 0.4022 | 40955.0000 |

**The frozen threshold 1/6 fold by fold on A's validation rows** (doc\_support a\_threshold\_by\_fold.csv; sigmoid refit per fold, verified to reproduce A's calibration AP):

| fold | threshold | alerts | tp | fp | fn | tn | precision | recall | cost |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.1667 | 59 | 13 | 46 | 1,427 | 11,470 | 0.2203 | 0.0090 | 7181.0000 |
| 2 | 0.1667 | 499 | 179 | 320 | 1,806 | 10,645 | 0.3587 | 0.0902 | 9350.0000 |
| 3 | 0.1667 | 976 | 301 | 675 | 1,652 | 10,313 | 0.3084 | 0.1541 | 8935.0000 |
| 4 | 0.1667 | 2,834 | 956 | 1,878 | 1,855 | 8,236 | 0.3373 | 0.3401 | 11153.0000 |
| 5 | 0.1667 | 3,864 | 628 | 3,236 | 480 | 5,907 | 0.1625 | 0.5668 | 5636.0000 |

**Full threshold curve** (A's s08 curves/threshold\_curve.csv; the chart is above):

| threshold | tp | fp | fn | tn | alerts | alerts\_per\_day | alert\_rate | error\_rate | precision | recall | f1 | cost | extra\_false\_alarms\_per\_extra\_detractor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.6000 | 15 | 17 | 9,282 | 52,709 | 32 | 0.0928 | 0.0005 | 0.1499 | 0.4688 | 0.0016 | 0.0032 | 46427.0000 |  |
| 0.5900 | 17 | 17 | 9,280 | 52,709 | 34 | 0.0986 | 0.0005 | 0.1499 | 0.5000 | 0.0018 | 0.0036 | 46417.0000 | 0.0000 |
| 0.5800 | 20 | 22 | 9,277 | 52,704 | 42 | 0.1217 | 0.0007 | 0.1499 | 0.4762 | 0.0022 | 0.0043 | 46407.0000 | 1.6667 |
| 0.5700 | 21 | 23 | 9,276 | 52,703 | 44 | 0.1275 | 0.0007 | 0.1499 | 0.4773 | 0.0023 | 0.0045 | 46403.0000 | 1.0000 |
| 0.5600 | 27 | 24 | 9,270 | 52,702 | 51 | 0.1478 | 0.0008 | 0.1498 | 0.5294 | 0.0029 | 0.0058 | 46374.0000 | 0.1667 |
| 0.5500 | 30 | 24 | 9,267 | 52,702 | 54 | 0.1565 | 0.0009 | 0.1498 | 0.5556 | 0.0032 | 0.0064 | 46359.0000 | 0.0000 |
| 0.5400 | 32 | 27 | 9,265 | 52,699 | 59 | 0.1710 | 0.0010 | 0.1498 | 0.5424 | 0.0034 | 0.0068 | 46352.0000 | 1.5000 |
| 0.5300 | 34 | 31 | 9,263 | 52,695 | 65 | 0.1884 | 0.0010 | 0.1498 | 0.5231 | 0.0037 | 0.0073 | 46346.0000 | 2.0000 |
| 0.5200 | 39 | 38 | 9,258 | 52,688 | 77 | 0.2232 | 0.0012 | 0.1499 | 0.5065 | 0.0042 | 0.0083 | 46328.0000 | 1.4000 |
| 0.5100 | 46 | 39 | 9,251 | 52,687 | 85 | 0.2464 | 0.0014 | 0.1498 | 0.5412 | 0.0049 | 0.0098 | 46294.0000 | 0.1429 |
| 0.5000 | 51 | 44 | 9,246 | 52,682 | 95 | 0.2754 | 0.0015 | 0.1498 | 0.5368 | 0.0055 | 0.0109 | 46274.0000 | 1.0000 |
| 0.4900 | 55 | 56 | 9,242 | 52,670 | 111 | 0.3217 | 0.0018 | 0.1499 | 0.4955 | 0.0059 | 0.0117 | 46266.0000 | 3.0000 |
| 0.4800 | 61 | 62 | 9,236 | 52,664 | 123 | 0.3565 | 0.0020 | 0.1499 | 0.4959 | 0.0066 | 0.0130 | 46242.0000 | 1.0000 |
| 0.4700 | 70 | 76 | 9,227 | 52,650 | 146 | 0.4232 | 0.0024 | 0.1500 | 0.4795 | 0.0075 | 0.0148 | 46211.0000 | 1.5556 |
| 0.4600 | 77 | 85 | 9,220 | 52,641 | 162 | 0.4696 | 0.0026 | 0.1500 | 0.4753 | 0.0083 | 0.0163 | 46185.0000 | 1.2857 |
| 0.4500 | 89 | 97 | 9,208 | 52,629 | 186 | 0.5391 | 0.0030 | 0.1500 | 0.4785 | 0.0096 | 0.0188 | 46137.0000 | 1.0000 |
| 0.4400 | 105 | 109 | 9,192 | 52,617 | 214 | 0.6203 | 0.0035 | 0.1500 | 0.4907 | 0.0113 | 0.0221 | 46069.0000 | 0.7500 |
| 0.4300 | 120 | 124 | 9,177 | 52,602 | 244 | 0.7072 | 0.0039 | 0.1500 | 0.4918 | 0.0129 | 0.0252 | 46009.0000 | 1.0000 |
| 0.4200 | 135 | 144 | 9,162 | 52,582 | 279 | 0.8087 | 0.0045 | 0.1500 | 0.4839 | 0.0145 | 0.0282 | 45954.0000 | 1.3333 |
| 0.4100 | 142 | 166 | 9,155 | 52,560 | 308 | 0.8928 | 0.0050 | 0.1503 | 0.4610 | 0.0153 | 0.0296 | 45941.0000 | 3.1429 |
| 0.4000 | 151 | 182 | 9,146 | 52,544 | 333 | 0.9652 | 0.0054 | 0.1504 | 0.4535 | 0.0162 | 0.0314 | 45912.0000 | 1.7778 |
| 0.3900 | 164 | 211 | 9,133 | 52,515 | 375 | 1.0870 | 0.0060 | 0.1507 | 0.4373 | 0.0176 | 0.0339 | 45876.0000 | 2.2308 |
| 0.3800 | 179 | 231 | 9,118 | 52,495 | 410 | 1.1884 | 0.0066 | 0.1507 | 0.4366 | 0.0193 | 0.0369 | 45821.0000 | 1.3333 |
| 0.3700 | 195 | 254 | 9,102 | 52,472 | 449 | 1.3014 | 0.0072 | 0.1508 | 0.4343 | 0.0210 | 0.0400 | 45764.0000 | 1.4375 |
| 0.3600 | 212 | 298 | 9,085 | 52,428 | 510 | 1.4783 | 0.0082 | 0.1513 | 0.4157 | 0.0228 | 0.0432 | 45723.0000 | 2.5882 |
| 0.3500 | 229 | 329 | 9,068 | 52,397 | 558 | 1.6174 | 0.0090 | 0.1515 | 0.4104 | 0.0246 | 0.0465 | 45669.0000 | 1.8235 |
| 0.3400 | 255 | 365 | 9,042 | 52,361 | 620 | 1.7971 | 0.0100 | 0.1517 | 0.4113 | 0.0274 | 0.0514 | 45575.0000 | 1.3846 |
| 0.3300 | 279 | 413 | 9,018 | 52,313 | 692 | 2.0058 | 0.0112 | 0.1521 | 0.4032 | 0.0300 | 0.0559 | 45503.0000 | 2.0000 |
| 0.3200 | 303 | 451 | 8,994 | 52,275 | 754 | 2.1855 | 0.0122 | 0.1523 | 0.4019 | 0.0326 | 0.0603 | 45421.0000 | 1.5833 |
| 0.3100 | 334 | 502 | 8,963 | 52,224 | 836 | 2.4232 | 0.0135 | 0.1526 | 0.3995 | 0.0359 | 0.0659 | 45317.0000 | 1.6452 |
| 0.3000 | 362 | 555 | 8,935 | 52,171 | 917 | 2.6580 | 0.0148 | 0.1530 | 0.3948 | 0.0389 | 0.0709 | 45230.0000 | 1.8929 |
| 0.2900 | 403 | 626 | 8,894 | 52,100 | 1,029 | 2.9826 | 0.0166 | 0.1535 | 0.3916 | 0.0433 | 0.0781 | 45096.0000 | 1.7317 |
| 0.2800 | 444 | 705 | 8,853 | 52,021 | 1,149 | 3.3304 | 0.0185 | 0.1541 | 0.3864 | 0.0478 | 0.0850 | 44970.0000 | 1.9268 |
| 0.2700 | 480 | 802 | 8,817 | 51,924 | 1,282 | 3.7159 | 0.0207 | 0.1551 | 0.3744 | 0.0516 | 0.0907 | 44887.0000 | 2.6944 |
| 0.2600 | 530 | 901 | 8,767 | 51,825 | 1,431 | 4.1478 | 0.0231 | 0.1559 | 0.3704 | 0.0570 | 0.0988 | 44736.0000 | 1.9800 |
| 0.2500 | 584 | 1,047 | 8,713 | 51,679 | 1,631 | 4.7275 | 0.0263 | 0.1574 | 0.3581 | 0.0628 | 0.1069 | 44612.0000 | 2.7037 |
| 0.2400 | 654 | 1,229 | 8,643 | 51,497 | 1,883 | 5.4580 | 0.0304 | 0.1592 | 0.3473 | 0.0703 | 0.1170 | 44444.0000 | 2.6000 |
| 0.2300 | 741 | 1,464 | 8,556 | 51,262 | 2,205 | 6.3913 | 0.0356 | 0.1616 | 0.3361 | 0.0797 | 0.1288 | 44244.0000 | 2.7011 |
| 0.2200 | 853 | 1,785 | 8,444 | 50,941 | 2,638 | 7.6464 | 0.0425 | 0.1649 | 0.3234 | 0.0918 | 0.1429 | 44005.0000 | 2.8661 |
| 0.2100 | 997 | 2,180 | 8,300 | 50,546 | 3,177 | 9.2087 | 0.0512 | 0.1690 | 0.3138 | 0.1072 | 0.1599 | 43680.0000 | 2.7431 |
| 0.2000 | 1,146 | 2,772 | 8,151 | 49,954 | 3,918 | 11.3565 | 0.0632 | 0.1761 | 0.2925 | 0.1233 | 0.1734 | 43527.0000 | 3.9732 |
| 0.1900 | 1,349 | 3,491 | 7,948 | 49,235 | 4,840 | 14.0290 | 0.0780 | 0.1844 | 0.2787 | 0.1451 | 0.1908 | 43231.0000 | 3.5419 |
| 0.1800 | 1,602 | 4,438 | 7,695 | 48,288 | 6,040 | 17.5072 | 0.0974 | 0.1956 | 0.2652 | 0.1723 | 0.2089 | 42913.0000 | 3.7431 |
| 0.1700 | 1,944 | 5,636 | 7,353 | 47,090 | 7,580 | 21.9710 | 0.1222 | 0.2094 | 0.2565 | 0.2091 | 0.2304 | 42401.0000 | 3.5029 |
| 0.1600 | 2,400 | 7,360 | 6,897 | 45,366 | 9,760 | 28.2899 | 0.1574 | 0.2299 | 0.2459 | 0.2581 | 0.2519 | 41845.0000 | 3.7807 |
| 0.1500 | 2,962 | 9,768 | 6,335 | 42,958 | 12,730 | 36.8986 | 0.2052 | 0.2596 | 0.2327 | 0.3186 | 0.2689 | 41443.0000 | 4.2847 |
| 0.1400 | 3,739 | 13,165 | 5,558 | 39,561 | 16,904 | 48.9971 | 0.2725 | 0.3019 | 0.2212 | 0.4022 | 0.2854 | 40955.0000 | 4.3719 |
| 0.1300 | 4,782 | 19,077 | 4,515 | 33,649 | 23,859 | 69.1565 | 0.3847 | 0.3804 | 0.2004 | 0.5144 | 0.2885 | 41652.0000 | 5.6683 |
| 0.1200 | 6,274 | 29,601 | 3,023 | 23,125 | 35,875 | 103.9855 | 0.5784 | 0.5260 | 0.1749 | 0.6748 | 0.2778 | 44716.0000 | 7.0536 |
| 0.1100 | 7,439 | 37,644 | 1,858 | 15,082 | 45,083 | 130.6754 | 0.7269 | 0.6369 | 0.1650 | 0.8002 | 0.2736 | 46934.0000 | 6.9039 |
| 0.1000 | 8,251 | 43,727 | 1,046 | 8,999 | 51,978 | 150.6609 | 0.8380 | 0.7219 | 0.1587 | 0.8875 | 0.2693 | 48957.0000 | 7.4914 |
| 0.0900 | 8,798 | 47,930 | 499 | 4,796 | 56,728 | 164.4290 | 0.9146 | 0.7808 | 0.1551 | 0.9463 | 0.2665 | 50425.0000 | 7.6837 |
| 0.0800 | 9,076 | 50,389 | 221 | 2,337 | 59,465 | 172.3623 | 0.9588 | 0.8160 | 0.1526 | 0.9762 | 0.2640 | 51494.0000 | 8.8453 |
| 0.0700 | 9,198 | 51,742 | 99 | 984 | 60,940 | 176.6377 | 0.9825 | 0.8358 | 0.1509 | 0.9894 | 0.2619 | 52237.0000 | 11.0902 |
| 0.0600 | 9,236 | 52,209 | 61 | 517 | 61,445 | 178.1014 | 0.9907 | 0.8428 | 0.1503 | 0.9934 | 0.2611 | 52514.0000 | 12.2895 |
| 0.0500 | 9,259 | 52,402 | 38 | 324 | 61,661 | 178.7275 | 0.9942 | 0.8455 | 0.1502 | 0.9959 | 0.2610 | 52592.0000 | 8.3913 |
| 0.0400 | 9,280 | 52,560 | 17 | 166 | 61,840 | 179.2464 | 0.9970 | 0.8477 | 0.1501 | 0.9982 | 0.2609 | 52645.0000 | 7.5238 |
| 0.0300 | 9,290 | 52,660 | 7 | 66 | 61,950 | 179.5652 | 0.9988 | 0.8492 | 0.1500 | 0.9992 | 0.2608 | 52695.0000 | 10.0000 |
| 0.0200 | 9,296 | 52,721 | 1 | 5 | 62,017 | 179.7594 | 0.9999 | 0.8500 | 0.1499 | 0.9999 | 0.2607 | 52726.0000 | 10.1667 |

Round 1 · run `20261021T050340Z` · 5 checks, all PASS · gate part only: 8.5–8.8 are not built until the team's combined review of s06–s08 (G-78). Coverage and review dropdowns are on the parent tab "s08 Selection"; comment on any card here.

## 8.1 Finalists

**Approved solution:** Each family's best from s07, plus the dummy and the plain linear/logistic and single-tree references from s06, compared on the same rows and folds (fold mean and standard error; paired per-fold differences shown as description)

**What was done:** 4 finalists refitted on the five s05 folds: dummy (s06 reference) 0.1482 ± 0.0198; linear/logistic (s06 reference) 0.2435 ± 0.0314; single tree (s06 reference) 0.2158 ± 0.0233; forest (s07 carried (plain s06)) 0.2544 ± 0.0267 (validation ap, mean ± SE).

**Finalists, validation AP, mean ± SE over the five folds** (candidates.csv):

| family | source | validation\_mean | validation\_se | train\_validation\_gap | grid\_edge | recommended |
| --- | --- | --- | --- | --- | --- | --- |
| dummy | s06 reference | 0.1482 | 0.0198 | -0.0201 | not a grid configuration (dummy) | False |
| linear/logistic | s06 reference | 0.2435 | 0.0314 | -0.0222 | plain s06 model, not a grid configuration | True |
| single tree | s06 reference | 0.2158 | 0.0233 | -0.0080 | none | False |
| forest | s07 carried (plain s06) | 0.2544 | 0.0267 | 0.0025 | none | False |

&#91;image: Finalists, classification\]

**Check** finalists refitted on the same rows and folds reproduce their s06 fold scores: PASS (4 of 4 reproduced) **Check** finalists: the dummy, plain linear/logistic and single tree references plus each family's s07 carried model: PASS (4 finalists) **Check** no test row read: every row used was purchased before the test cutoff: PASS (latest purchase 2018-05-23 11:29:51, cutoff 2018-05-26 12:16:34)

**Files** (stages/s08\_selection/classification/outputs/, run 20261021T050340Z): candidates.csv, counts.json, figures/finalists.csv, figures/finalists.json, figures/finalists.png, metrics\_long.csv, predictions.csv.gz

## 8.2 Choose the model

**Approved solution:** One-standard-error rule (1.7) on the primary metric (MAE / AP): the simplest finalist whose mean is within one standard error of the best mean is the recommendation. The final choice is a human gate (G-39): the run stops and presents a selection pack, then the team confirms or overrides in spec/human\_decisions.yaml with its rationale. An override is a protocol deviation: logged as a CR in CHANGELOG, with the one-SE choice shown beside it in the report and slides (G-44). The pack holds each finalist's fold mean ± standard error on all s01 metrics, the train–validation gap and learning curves, plus a flag when a chosen setting sits at a grid edge. A grid-edge choice is resolved by the team, never silently: either widen that grid (change request; s07 reruns and keeps all configurations) or revisit s03–s04. Validation scores are reported as selection scores, not generalisation

**What was done:** One-SE recommendation: linear/logistic (best mean: forest). Ladder basic to complex: linear/logistic kept over dummy (paired gain +0.0953, better in 5 of 5 folds); single tree not kept over linear/logistic (paired gain -0.0277, better in 0 of 5 folds); forest not kept over linear/logistic (paired gain +0.0109, better in 4 of 5 folds); ladder result linear/logistic. Grid edge of the recommendation: plain s06 model, not a grid configuration.

**Reasoning:** The recommendation follows the pre-registered rule; the team confirms or overrides it at the gate (G-39), and an override is logged as a protocol deviation (G-44). Validation scores are selection scores, not generalisation estimates (G-10).

**Conclusion:** The run stops here. Under G-78 the team reviews s06, s07 and s08 together before the freeze, the final fit and the single test (8.5-8.8).

**Every s01 metric, mean and SE over the folds** (candidates.csv):

| family | ap\_mean | ap\_se | brier\_mean | brier\_se | roc\_auc\_mean | roc\_auc\_se |
| --- | --- | --- | --- | --- | --- | --- |
| dummy | 0.1482 | 0.0198 | 0.1269 | 0.0145 | 0.5000 | 0.0000 |
| linear/logistic | 0.2435 | 0.0314 | 0.1243 | 0.0143 | 0.6213 | 0.0161 |
| single tree | 0.2158 | 0.0233 | 0.1242 | 0.0145 | 0.5952 | 0.0104 |
| forest | 0.2544 | 0.0267 | 0.1234 | 0.0143 | 0.6336 | 0.0095 |

**Ladder, basic to complex** (ladder.csv; paired gains are description only):

| comparison | gain\_fold\_1 | gain\_fold\_2 | gain\_fold\_3 | gain\_fold\_4 | gain\_fold\_5 | mean\_gain | paired\_se | folds\_better | kept\_by\_one\_se\_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear/logistic vs dummy | 0.0419 | 0.0864 | 0.0952 | 0.1325 | 0.1207 | 0.0953 | 0.0157 | 5 | True |
| single tree vs linear/logistic | -0.0137 | -0.0071 | -0.0143 | -0.0701 | -0.0332 | -0.0277 | 0.0115 | 0 | False |
| forest vs linear/logistic | 0.0193 | 0.0254 | 0.0135 | -0.0114 | 0.0078 | 0.0109 | 0.0063 | 4 | False |

**Check** no test row read: every row used was purchased before the test cutoff: PASS (latest purchase 2018-05-23 11:29:51, cutoff 2018-05-26 12:16:34) **Check** the run stops at the gate: no frozen\_recipe.json, the test cohort is not read (G-39, G-78): PASS (team decisions in human\_decisions.yaml s08: not yet made)

**Files** (stages/s08\_selection/classification/outputs/, run 20261021T050340Z): candidates.csv, counts.json, decision.json, figures/finalists.csv, figures/finalists.json, figures/finalists.png, ladder.csv, selected\_spec.json, selection\_review\_pack.md

## 8.3 Calibration (classification)

**Approved solution:** Reliability curve and Brier on the chosen model's out-of-fold probabilities. Raw probabilities by default; a sigmoid-calibrated variant (CalibratedClassifierCV, time-ordered inner splits inside each training fold) is always scored as a full candidate, with no trigger to decide (G-52), and kept only if mean Brier improves and mean AP stays within one fold SE of the raw model (G-45)

**What was done:** Raw vs sigmoid (CalibratedClassifierCV, time-ordered inner splits) on the recommended model, per fold: mean Brier raw 0.12426 vs sigmoid 0.12391; mean AP raw 0.2435 vs sigmoid 0.2317 (one fold SE 0.0314). Kept: sigmoid.

**Raw vs sigmoid, mean over the folds** (calibration\_folds.csv):

| variant | ap | brier | roc\_auc |
| --- | --- | --- | --- |
| raw | 0.24351 | 0.12426 | 0.62127 |
| sigmoid | 0.23173 | 0.12391 | 0.61426 |

**Per fold** (calibration\_folds.csv):

| variant | fold | ap | brier | roc\_auc |
| --- | --- | --- | --- | --- |
| raw | 1 | 0.15308 | 0.09871 | 0.56997 |
| sigmoid | 1 | 0.14805 | 0.09857 | 0.56894 |
| raw | 2 | 0.23963 | 0.13074 | 0.61929 |
| sigmoid | 2 | 0.23223 | 0.12907 | 0.61356 |
| raw | 3 | 0.24611 | 0.12483 | 0.60666 |
| sigmoid | 3 | 0.23447 | 0.12603 | 0.60855 |
| raw | 4 | 0.34995 | 0.17356 | 0.65392 |
| sigmoid | 4 | 0.32206 | 0.17019 | 0.62929 |
| raw | 5 | 0.22876 | 0.09345 | 0.65650 |
| sigmoid | 5 | 0.22181 | 0.09567 | 0.65095 |

&#91;image: Reliability, raw vs sigmoid\]

**Check** calibration inner splits are time-ordered: every training fold sorted by purchase time: PASS

**Files** (stages/s08\_selection/classification/outputs/, run 20261021T050340Z): calibration\_folds.csv, curves/reliability\_raw\_vs\_sigmoid.csv, decision.json, figures/calibration.csv, figures/calibration.json, figures/calibration.png, predictions.csv.gz, selected\_spec.json, selection\_review\_pack.md

## 8.4 Threshold (classification)

**Approved solution:** From the out-of-fold probabilities of the chosen recipe: compare no alerts, 0.50, the theoretical cost cutoff 1/6 and the empirical cost minimum of 5·FN + FP (ties → higher threshold, fewer alerts). HARD STOP (G-39): the run stops and presents, for every candidate threshold: alerts per day, alert rate (TP+FP)/N, error rate (FN+FP)/N, precision, recall, F1 and cost. It also shows the marginal trade-off: extra false alarms per extra detractor caught between neighbouring thresholds. Under the 5:1 cost an alert pays off only while that ratio stays at or below 5, which is why the theoretical cutoff is 1/6 = C\_FP/(C\_FP+C\_FN) (Elkan 2001). The team picks the threshold in spec/human\_decisions.yaml and may set a daily alert cap the CX team can handle; the choice and its reason go into the report

**What was done:** Threshold candidates on the out-of-fold probabilities of the calibrated recommended model (62,023 validation rows, 345 days): 0.50 (t=0.5000): 0.3 alerts/day, precision 0.537, recall 0.005, cost 46,274; 1/6 (cost cutoff) (t=0.1667): 23.9 alerts/day, precision 0.252, recall 0.223, cost 42,255; empirical minimum of 5\*FN + FP (t=0.1371): 53.5 alerts/day, precision 0.218, recall 0.432, cost 40,839; no alerts: cost 46,485.

**Reasoning:** Under the 5:1 cost an alert pays off while the extra false alarms per extra detractor caught stay at or below 5 (Elkan 2001). The threshold is a business choice: the team picks it at the hard stop, with an optional daily alert cap (G-39, G-56).

**Threshold candidates** (threshold\_table.csv; cost = 5·FN + FP, illustrative):

| candidate | threshold | alerts\_per\_day | alert\_rate | error\_rate | precision | recall | f1 | cost | extra\_false\_alarms\_per\_extra\_detractor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| no alerts | inf | 0.0000 | 0.0000 | 0.1499 | 0.0000 | 0.0000 | 0.0000 | 46485.0000 |  |
| 0.50 | 0.5000 | 0.2754 | 0.0015 | 0.1498 | 0.5368 | 0.0055 | 0.0109 | 46274.0000 | 0.8627 |
| 1/6 (cost cutoff) | 0.1667 | 23.8609 | 0.1327 | 0.2156 | 0.2523 | 0.2234 | 0.2370 | 42255.0000 | 3.0163 |
| empirical minimum of 5\*FN + FP | 0.1371 | 53.4609 | 0.2974 | 0.3178 | 0.2177 | 0.4319 | 0.2895 | 40839.0000 | 4.2693 |

&#91;image: Threshold trade-off\]

**Files** (stages/s08\_selection/classification/outputs/, run 20261021T050340Z): curves/threshold\_curve.csv, decision.json, figures/threshold\_tradeoff.csv, figures/threshold\_tradeoff.json, figures/threshold\_tradeoff.png, selection\_review\_pack.md, threshold\_table.csv

## 8.5 Freeze

**Approved solution:** Write frozen\_recipe.json (features, transforms, recipe, estimator and settings, calibration, threshold) with its hash, before the test cohort is read

**Round 2 (2026-10-23), run `20261023T082539Z`.** **What was done:** Recipe frozen for clf.sel.log.logistic: 16 numeric and 3 categorical features, estimator logistic, calibration sigmoid, threshold 0.1667 on the sigmoid-calibrated probability (daily alert cap 25; out-of-fold 23.9 alerts/day); sha256 8de9d4f13159db2d77716df7070f745bea118390cdb3a624cede3ab19d9277d8. Written from development rows only; the test cohort is not loaded. **Conclusion:** Pipeline A stops after the freeze. The final fit, the single test read and the bundle (8.6–8.8) run together with Pipeline B (lead decision 2026-10-23; draft G-79). **Check** frozen recipe follows the team decisions: PASS (clf.sel.log.logistic). **Check** the decided threshold keeps the out-of-fold alerts within the daily cap: PASS (23.9 alerts/day at 0.1667, cap 25). **Check** frozen before any test row is read: PASS. **Files:** frozen\_recipe.json, decision.json, counts.json, selection\_review\_pack.md

## 8.6 Final fit

**Approved solution:** Fit the frozen recipe on all development orders whose labels were observable before the test cutoff

**Not built (MISSING by design).** Runs only after the team's combined review of s06–s08 has filled spec/human\_decisions.yaml s08.classification (G-39, G-78); the freeze is written before the test cohort is read.

## 8.7 Test once

**Approved solution:** Score each task's test cohort once with the agreed metric list (G-24), including the dummy and plain linear/logistic references refitted the same way for comparison

**Not built (MISSING by design).** Runs only after the team's combined review of s06–s08 has filled spec/human\_decisions.yaml s08.classification (G-39, G-78); the freeze is written before the test cohort is read.

## 8.8 Bundle

**Approved solution:** joblib pipeline, threshold, feature schema, package versions, training-ID digest, training\_profile.json (numeric distributions, category shares) for drift checks, checksums

**Not built (MISSING by design).** Runs only after the team's combined review of s06–s08 has filled spec/human\_decisions.yaml s08.classification (G-39, G-78); the freeze is written before the test cohort is read.
