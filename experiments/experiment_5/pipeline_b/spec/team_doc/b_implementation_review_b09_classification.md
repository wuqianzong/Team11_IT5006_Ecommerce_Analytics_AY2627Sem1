# B9 › classification

## Accepted (2026-10-25) — confirmation additions; accepted run 20261025T132538Z on b09c396 (tag e5-B-s09-accepted)

B9 is confirmed by Henry and the experiment lead. The accepted clean rerun is byte-identical to the build runs cited below, so every number in this tab is unchanged. Added at confirmation:

### B9.14 Validation and test with time windows (R-17)

**What was done:** Each series: five validation folds, their mean ± SE, and the test with its 95% bootstrap interval; each period's time window is in validation\_and\_test\_windows.csv and on the chart. B on B rows: folds mean 0.2482 ± 0.0313, test 0.1972 \[0.1808, 0.2176\]; A on B rows: folds mean 0.2302 ± 0.0305, test 0.1785 \[0.1631, 0.1974\]; A on A rows: folds mean 0.2317 ± 0.0276, test 0.1750 \[0.1611, 0.1891\]. Test window 2018-05-26 to 2018-08-29.

&#91;image: validation and test with windows\]

| period | kind | start | end | festival\_days |
| --- | --- | --- | --- | --- |
| fold 1 | validation (selection score, G-10) | 2017-06-17 | 2017-09-26 |  |
| fold 2 | validation (selection score, G-10) | 2017-09-26 | 2017-12-02 | 2017-11-24 |
| fold 3 | validation (selection score, G-10) | 2017-12-02 | 2018-02-04 | 2017-12-25 |
| fold 4 | validation (selection score, G-10) | 2018-02-04 | 2018-03-31 |  |
| fold 5 | validation (selection score, G-10) | 2018-03-31 | 2018-05-23 |  |
| test | test (unbiased, read once) | 2018-05-26 | 2018-08-29 |  |

## Round 2 — Henry's B9 review (added 2026-10-25; run 20261025T090945Z, uncommitted)

Read only: no frozen model refitted on new data, no second test read. Decisions: B-G-06 (orders outside B's scope fall back to A) and B-G-07 (operating threshold 4/15, a post-test change; the frozen 1/6 stays the unbiased test result). Henry's requests: REPORT\_REQUESTS R-07 to R-13.

### B9.10 Operating threshold options (B-G-07)

**What was done:** Operating threshold 4/15 (B-G-07, post-test) vs frozen 1/6 on B's rows. Validation: 4.0 alerts/day, FP per TP 1.35, recall 0.084 (1/6: 17.0/day, 2.35, 0.250). Test: 5.6/day, FP per TP 1.89, precision 0.346, recall 0.121 (1/6: 23.2/day, 3.81). Cost 5:1 at 4/15 7,123 vs 7,156 at 1/6; cost 1:1 1,707 vs 2,844.

&#91;image: threshold\_options\]

1/6 and 4/15 for B and A (threshold\_options.csv; validation = out-of-fold sigmoid probabilities rebuilt per fold and checked against B8/s08; test = T1's saved predictions):

| threshold\_name | model | rows | threshold | alerts | alerts\_per\_day | tp | fp | fn | precision | recall | fp\_per\_tp | cost\_5\_to\_1 | cost\_1\_to\_1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| frozen 1/6 | B frozen | validation (out-of-fold), B rows | 0.167 | 5,865 | 17.000 | 1,749 | 4,116 | 5,251 | 0.298 | 0.250 | 2.353 | 30371.000 | 9,367 |
| frozen 1/6 | B frozen | test, B rows | 0.167 | 2,229 | 23.219 | 463 | 1,766 | 1,078 | 0.208 | 0.300 | 3.814 | 7156.000 | 2,844 |
| frozen 1/6 | A frozen | validation (out-of-fold), A rows | 0.167 | 8,232 | 23.861 | 2,077 | 6,155 | 7,220 | 0.252 | 0.223 | 2.963 | 42255.000 | 13,375 |
| frozen 1/6 | A frozen | test, B rows | 0.167 | 3,462 | 36.062 | 548 | 2,914 | 993 | 0.158 | 0.356 | 5.318 | 7879.000 | 3,907 |
| frozen 1/6 | A frozen | test, A rows | 0.167 | 4,901 | 51.052 | 748 | 4,153 | 1,220 | 0.153 | 0.380 | 5.552 | 10253.000 | 5,373 |
| operating 4/15 (B-G-07) | B frozen | validation (out-of-fold), B rows | 0.267 | 1,381 | 4.003 | 588 | 793 | 6,412 | 0.426 | 0.084 | 1.349 | 32853.000 | 7,205 |
| operating 4/15 (B-G-07) | B frozen | test, B rows | 0.267 | 540 | 5.625 | 187 | 353 | 1,354 | 0.346 | 0.121 | 1.888 | 7123.000 | 1,707 |
| operating 4/15 (B-G-07) | A frozen | validation (out-of-fold), A rows | 0.267 | 1,320 | 3.826 | 488 | 832 | 8,809 | 0.370 | 0.052 | 1.705 | 44877.000 | 9,641 |
| operating 4/15 (B-G-07) | A frozen | test, B rows | 0.267 | 651 | 6.781 | 201 | 450 | 1,340 | 0.309 | 0.130 | 2.239 | 7150.000 | 1,790 |
| operating 4/15 (B-G-07) | A frozen | test, A rows | 0.267 | 888 | 9.250 | 257 | 631 | 1,711 | 0.289 | 0.131 | 2.455 | 9186.000 | 2,342 |

Selected points of the curve (threshold\_options\_curve.csv has every 0.01 from 0.02 to 0.60):

| period | threshold | alerts | alerts\_per\_day | tp | fp | fn | precision | recall | fp\_per\_tp | cost\_5\_to\_1 | cost\_1\_to\_1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| validation (out-of-fold) | 0.120 | 21,279 | 61.678 | 4,152 | 17,127 | 2,848 | 0.195 | 0.593 | 4.125 | 31367.000 | 19,975 |
| test (post-test view) | 0.120 | 5,276 | 54.958 | 789 | 4,487 | 752 | 0.150 | 0.512 | 5.687 | 8247.000 | 5,239 |
| validation (out-of-fold) | 0.140 | 10,374 | 30.070 | 2,675 | 7,699 | 4,325 | 0.258 | 0.382 | 2.878 | 29324.000 | 12,024 |
| test (post-test view) | 0.140 | 3,618 | 37.688 | 605 | 3,013 | 936 | 0.167 | 0.393 | 4.980 | 7693.000 | 3,949 |
| validation (out-of-fold) | 0.167 | 5,865 | 17.000 | 1,749 | 4,116 | 5,251 | 0.298 | 0.250 | 2.353 | 30371.000 | 9,367 |
| test (post-test view) | 0.167 | 2,229 | 23.219 | 463 | 1,766 | 1,078 | 0.208 | 0.300 | 3.814 | 7156.000 | 2,844 |
| validation (out-of-fold) | 0.200 | 3,312 | 9.600 | 1,139 | 2,173 | 5,861 | 0.344 | 0.163 | 1.908 | 31478.000 | 8,034 |
| test (post-test view) | 0.200 | 1,270 | 13.229 | 319 | 951 | 1,222 | 0.251 | 0.207 | 2.981 | 7061.000 | 2,173 |
| validation (out-of-fold) | 0.220 | 2,505 | 7.261 | 913 | 1,592 | 6,087 | 0.364 | 0.130 | 1.744 | 32027.000 | 7,679 |
| test (post-test view) | 0.220 | 949 | 9.885 | 266 | 683 | 1,275 | 0.280 | 0.173 | 2.568 | 7058.000 | 1,958 |
| validation (out-of-fold) | 0.240 | 1,913 | 5.545 | 758 | 1,155 | 6,242 | 0.396 | 0.108 | 1.524 | 32365.000 | 7,397 |
| test (post-test view) | 0.240 | 741 | 7.719 | 226 | 515 | 1,315 | 0.305 | 0.147 | 2.279 | 7090.000 | 1,830 |
| validation (out-of-fold) | 0.267 | 1,381 | 4.003 | 588 | 793 | 6,412 | 0.426 | 0.084 | 1.349 | 32853.000 | 7,205 |
| test (post-test view) | 0.267 | 540 | 5.625 | 187 | 353 | 1,354 | 0.346 | 0.121 | 1.888 | 7123.000 | 1,707 |
| validation (out-of-fold) | 0.280 | 1,170 | 3.391 | 526 | 644 | 6,474 | 0.450 | 0.075 | 1.224 | 33014.000 | 7,118 |
| test (post-test view) | 0.280 | 471 | 4.906 | 164 | 307 | 1,377 | 0.348 | 0.106 | 1.872 | 7192.000 | 1,684 |
| validation (out-of-fold) | 0.300 | 949 | 2.751 | 438 | 511 | 6,562 | 0.462 | 0.063 | 1.167 | 33321.000 | 7,073 |
| test (post-test view) | 0.300 | 392 | 4.083 | 141 | 251 | 1,400 | 0.360 | 0.091 | 1.780 | 7251.000 | 1,651 |
| validation (out-of-fold) | 0.320 | 777 | 2.252 | 371 | 406 | 6,629 | 0.477 | 0.053 | 1.094 | 33551.000 | 7,035 |
| test (post-test view) | 0.320 | 316 | 3.292 | 126 | 190 | 1,415 | 0.399 | 0.082 | 1.508 | 7265.000 | 1,605 |
| validation (out-of-fold) | 0.360 | 510 | 1.478 | 269 | 241 | 6,731 | 0.527 | 0.038 | 0.896 | 33896.000 | 6,972 |
| test (post-test view) | 0.360 | 225 | 2.344 | 92 | 133 | 1,449 | 0.409 | 0.060 | 1.446 | 7378.000 | 1,582 |
| validation (out-of-fold) | 0.400 | 356 | 1.032 | 187 | 169 | 6,813 | 0.525 | 0.027 | 0.904 | 34234.000 | 6,982 |
| test (post-test view) | 0.400 | 151 | 1.573 | 73 | 78 | 1,468 | 0.483 | 0.047 | 1.068 | 7418.000 | 1,546 |
| validation (out-of-fold) | 0.500 | 129 | 0.374 | 70 | 59 | 6,930 | 0.543 | 0.010 | 0.843 | 34709.000 | 6,989 |
| test (post-test view) | 0.500 | 59 | 0.615 | 29 | 30 | 1,512 | 0.492 | 0.019 | 1.034 | 7590.000 | 1,542 |

### B9.11 Drift by fold, training vs validation, A and B (R-07; for the report appendix)

**What was done:** Training vs validation drift per fold for A and B, plus final fit vs test (SMD for numeric features and the target, TVD for categorical). Numeric features with |SMD| >= 0.2 in at least 3 of the 6 periods: A purchase\_month (6), B purchase\_month (6), B route\_recent\_carrier\_transit\_days (4), B route\_recent\_delivery\_days (4).

&#91;image: drift\_by\_fold\]

**B: numeric features and target, SMD (validation or test minus training rows)**:

| feature | fold 1 | fold 2 | fold 3 | fold 4 | fold 5 | test |
| --- | --- | --- | --- | --- | --- | --- |
| purchase\_month | 3.67 | 3.22 | -0.42 | -1.99 | -0.73 | 0.41 |
| route\_recent\_delivery\_days | -0.33 | -0.01 | 0.57 | 0.52 | 0.06 | -0.76 |
| route\_recent\_carrier\_transit\_days | -0.29 | -0.05 | 0.47 | 0.50 | 0.09 | -0.58 |
| seller\_prior\_review\_mean | -0.02 | 0.06 | -0.07 | -0.23 | -0.34 | -0.05 |
| order\_dispatch\_days | -0.03 | 0.17 | 0.12 | 0.03 | -0.30 | -0.21 |
| is\_detractor | -0.05 | 0.10 | 0.11 | 0.24 | -0.10 | -0.11 |
| seller\_prior\_late\_handover\_rate | -0.21 | -0.11 | -0.01 | 0.12 | -0.03 | -0.09 |
| seller\_prior\_late\_handover\_days | -0.20 | -0.17 | -0.12 | 0.00 | -0.04 | -0.07 |
| seller\_prior\_dispatch\_days | -0.10 | -0.03 | 0.03 | 0.10 | -0.07 | -0.19 |
| order\_handed\_over\_late | -0.03 | 0.10 | 0.11 | 0.05 | -0.17 | -0.03 |
| interstate\_share | -0.04 | 0.01 | -0.04 | -0.00 | -0.15 | -0.12 |
| distance\_km\_max | 0.02 | 0.02 | -0.06 | -0.01 | -0.15 | -0.09 |
| order\_handover\_late\_days | -0.06 | 0.06 | 0.08 | 0.02 | -0.15 | -0.08 |
| payment\_installments\_max | 0.01 | -0.05 | -0.11 | -0.10 | -0.09 | -0.06 |
| total\_freight | 0.04 | 0.04 | -0.01 | 0.04 | 0.03 | 0.11 |
| total\_volume\_cm3 | 0.03 | -0.03 | -0.06 | -0.05 | -0.03 | -0.10 |
| n\_categories | 0.07 | 0.04 | -0.04 | 0.00 | 0.09 | 0.10 |
| product\_description\_lenght | -0.00 | 0.01 | 0.02 | 0.07 | 0.08 | 0.08 |
| total\_weight\_g | 0.03 | -0.04 | -0.02 | -0.02 | 0.01 | -0.08 |
| n\_sellers | 0.06 | 0.03 | 0.02 | -0.01 | 0.06 | 0.04 |
| n\_items | 0.01 | 0.06 | -0.01 | 0.01 | 0.03 | -0.02 |
| freight\_ratio | -0.04 | -0.03 | -0.04 | 0.01 | -0.01 | 0.06 |
| n\_products | 0.00 | 0.03 | -0.00 | -0.05 | 0.02 | -0.00 |
| total\_price | -0.04 | 0.02 | -0.03 | -0.02 | 0.04 | 0.00 |

**B: categorical features, total variation distance**:

| feature | fold 1 | fold 2 | fold 3 | fold 4 | fold 5 | test |
| --- | --- | --- | --- | --- | --- | --- |
| primary\_category | 0.092 | 0.106 | 0.106 | 0.134 | 0.144 | 0.163 |
| route\_seller\_to\_customer\_state | 0.054 | 0.049 | 0.060 | 0.052 | 0.084 | 0.080 |

**A: numeric features and target, SMD (validation or test minus training rows)**:

| feature | fold 1 | fold 2 | fold 3 | fold 4 | fold 5 | test |
| --- | --- | --- | --- | --- | --- | --- |
| purchase\_month | 3.57 | 3.11 | -0.35 | -1.88 | -0.70 | 0.43 |
| seller\_prior\_review\_mean | -0.04 | 0.05 | -0.07 | -0.21 | -0.33 | -0.06 |
| is\_detractor | -0.05 | 0.10 | 0.09 | 0.23 | -0.11 | -0.13 |
| interstate\_share | -0.04 | 0.00 | -0.04 | -0.01 | -0.16 | -0.11 |
| distance\_km\_max | -0.01 | -0.00 | -0.04 | -0.01 | -0.16 | -0.06 |
| payment\_installments\_max | 0.02 | -0.04 | -0.11 | -0.10 | -0.09 | -0.05 |
| total\_freight | 0.03 | 0.05 | -0.02 | 0.04 | 0.02 | 0.11 |
| total\_volume\_cm3 | 0.01 | -0.03 | -0.07 | -0.06 | -0.04 | -0.11 |
| n\_categories | 0.08 | 0.04 | -0.05 | 0.00 | 0.09 | 0.10 |
| total\_weight\_g | 0.01 | -0.03 | -0.03 | -0.03 | -0.00 | -0.08 |
| product\_description\_lenght | -0.02 | 0.01 | 0.01 | 0.07 | 0.07 | 0.08 |
| n\_sellers | 0.07 | 0.03 | 0.02 | -0.01 | 0.06 | 0.04 |
| product\_photos\_qty | 0.01 | 0.01 | 0.02 | -0.06 | 0.03 | 0.00 |
| freight\_ratio | -0.04 | -0.04 | -0.03 | 0.02 | -0.02 | 0.05 |
| n\_items | 0.01 | 0.05 | -0.02 | 0.01 | 0.02 | -0.02 |
| n\_products | 0.01 | 0.03 | -0.00 | -0.05 | 0.02 | 0.00 |
| total\_price | -0.04 | 0.01 | -0.04 | -0.02 | 0.03 | 0.01 |

**A: categorical features, total variation distance**:

| feature | fold 1 | fold 2 | fold 3 | fold 4 | fold 5 | test |
| --- | --- | --- | --- | --- | --- | --- |
| customer\_state | 0.034 | 0.022 | 0.032 | 0.017 | 0.072 | 0.058 |
| primary\_category | 0.098 | 0.100 | 0.114 | 0.137 | 0.143 | 0.166 |
| primary\_seller\_state | 0.065 | 0.042 | 0.053 | 0.054 | 0.050 | 0.035 |

### B9.13 Business summary by route (R-10)

**What was done:** Routes judged (more than 100 detractors): 3 of 48 on B's test rows; A on all of A's test routes is listed too (in or out of B's scope).

A and B on B's test rows, judged routes (3 of 48; the rest are in business\_by\_route.csv as too small to judge):

| route | orders | detractors | alerts\_A\_1/6 | precision\_A\_1/6 | recall\_A\_1/6 | alerts\_A\_4/15 | precision\_A\_4/15 | recall\_A\_4/15 | alerts\_B\_1/6 | precision\_B\_1/6 | recall\_B\_1/6 | alerts\_B\_4/15 | precision\_B\_4/15 | recall\_B\_4/15 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SP->SP | 6,624 | 621 | 510 | 0.194 | 0.159 | 143 | 0.336 | 0.077 | 572.000 | 0.215 | 0.198 | 153.000 | 0.346 | 0.085 |
| SP->RJ | 1,293 | 161 | 1,219 | 0.128 | 0.969 | 222 | 0.243 | 0.335 | 499.000 | 0.190 | 0.590 | 87.000 | 0.310 | 0.168 |
| SP->MG | 1,236 | 125 | 234 | 0.222 | 0.416 | 42 | 0.333 | 0.112 | 133.000 | 0.248 | 0.264 | 34.000 | 0.412 | 0.112 |

A on all of A's test rows, judged routes (3 of 302; in\_b\_scope = False marks routes served by A under B-G-06):

| route | orders | detractors | alerts\_A\_1/6 | precision\_A\_1/6 | recall\_A\_1/6 | alerts\_A\_4/15 | precision\_A\_4/15 | recall\_A\_4/15 | in\_b\_scope |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SP->SP | 6,729 | 672 | 520 | 0.204 | 0.158 | 148 | 0.351 | 0.077 | False |
| SP->RJ | 1,316 | 163 | 1,240 | 0.127 | 0.969 | 224 | 0.241 | 0.331 | False |
| SP->MG | 1,269 | 130 | 238 | 0.227 | 0.415 | 44 | 0.341 | 0.115 | False |

### B9.14 Validation folds and test together (R-11)

**What was done:** Each series: five validation folds, their mean ± SE, and the test with its 95% bootstrap interval. B on B rows: folds mean 0.2482 ± 0.0313, test 0.1972 \[0.1808, 0.2176\]; A on B rows: folds mean 0.2302 ± 0.0305, test 0.1785 \[0.1631, 0.1974\]; A on A rows: folds mean 0.2317 ± 0.0276, test 0.1750 \[0.1611, 0.1891\].

&#91;image: validation\_and\_test\]

(validation\_and\_test.csv; folds are selection scores across seasons, the test is one recent window read once)

| series | fold\_1 | fold\_2 | fold\_3 | fold\_4 | fold\_5 | mean\_5\_folds | se\_5\_folds | test | test\_ci\_low | test\_ci\_high | metric |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B on B rows | 0.1468 | 0.2575 | 0.2641 | 0.3411 | 0.2316 | 0.2482 | 0.0313 | 0.1972 | 0.1808 | 0.2176 | ap |
| A on B rows | 0.1361 | 0.2320 | 0.2390 | 0.3273 | 0.2165 | 0.2302 | 0.0305 | 0.1785 | 0.1631 | 0.1974 | ap |
| A on A rows | 0.1480 | 0.2322 | 0.2345 | 0.3221 | 0.2218 | 0.2317 | 0.0276 | 0.1750 | 0.1611 | 0.1891 | ap |

### B9.15 A's model outside B's scope (R-12; B-G-06)

**What was done:** A's frozen model by B's scope (B-G-06 fallback). Validation AP mean over 5 folds: inside 0.2356, outside 0.2257. Test: inside 0.1798 (15,570 orders), outside 0.1614 \[0.1350, 0.1964\] (3,396 orders).

Fold by fold and test (a\_fallback\_by\_scope.csv; out of scope = customer or seller state outside the seven, or distance missing):

| period | scope | orders | detractors | ap | roc\_auc | brier | precision | recall | ap\_ci\_low | ap\_ci\_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fold 1 | outside B's scope | 2,541 | 348 | 0.1601 | 0.5258 | 0.1181 | 0.0952 | 0.0057 |  |  |
| fold 1 | inside B's scope | 10,415 | 1,092 | 0.1455 | 0.5803 | 0.0938 | 0.2895 | 0.0101 |  |  |
| fold 2 | outside B's scope | 2,474 | 432 | 0.2211 | 0.5558 | 0.1459 | 0.2882 | 0.1134 |  |  |
| fold 2 | inside B's scope | 10,476 | 1,553 | 0.2382 | 0.6255 | 0.1251 | 0.3951 | 0.0837 |  |  |
| fold 3 | outside B's scope | 2,388 | 364 | 0.2018 | 0.5643 | 0.1281 | 0.2184 | 0.1758 |  |  |
| fold 3 | inside B's scope | 10,553 | 1,589 | 0.2473 | 0.6177 | 0.1256 | 0.3470 | 0.1492 |  |  |
| fold 4 | outside B's scope | 2,416 | 591 | 0.3055 | 0.5656 | 0.1896 | 0.2929 | 0.4247 |  |  |
| fold 4 | inside B's scope | 10,509 | 2,220 | 0.3296 | 0.6423 | 0.1657 | 0.3566 | 0.3176 |  |  |
| fold 5 | outside B's scope | 1,581 | 215 | 0.2400 | 0.6277 | 0.1157 | 0.1678 | 0.7116 |  |  |
| fold 5 | inside B's scope | 8,670 | 893 | 0.2174 | 0.6498 | 0.0920 | 0.1609 | 0.5319 |  |  |
| test | outside B's scope | 3,396 | 360 | 0.1614 | 0.5778 | 0.0988 | 0.1331 | 0.5278 | 0.1350 | 0.1964 |
| test | inside B's scope | 15,570 | 1,608 | 0.1798 | 0.5987 | 0.0921 | 0.1607 | 0.3470 | 0.1647 | 0.1971 |

Five-fold summary (a\_fallback\_summary.csv):

| scope | mean\_5\_folds | se\_5\_folds |
| --- | --- | --- |
| inside B's scope | 0.2356 | 0.0295 |
| outside B's scope | 0.2257 | 0.0239 |

- PASS: rebuilt out-of-fold sigmoid probabilities reproduce B8's and A's calibration step (AP per fold) (max difference B 5.6e-17, A 8.3e-17)

Run `20261024T052644Z` on uncommitted code (working tree on 7e6941f) · 6 checks, all PASS · reads T1's frozen predictions; no refit, no threshold change. Coverage and review dropdowns are on the parent tab "B9 Conclusion".

## B9.1 Train, dddvalidation and test

**What was done:** Train, validation (selection scores, G-10) and test with 95% bootstrap intervals (1000 resamples, seed 42) for B, A and references. B's test AP 0.1972 \[0.1808, 0.2176\], width 0.0369; 1,541 test detractors.

Validation means are selection scores (G-10), mean over 5 folds ± SE; test = T1's single read with a 95% bootstrap interval (train\_val\_test.csv). Train means exist only where the model was fitted per fold in B6/s06 (plain and dummy; the frozen regression model is the plain linear recipe).

| model | rows | metric | train\_mean | validation\_mean | validation\_se | test | test\_ci\_low | test\_ci\_high | ci\_width | test\_rows | test\_detractors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B frozen | B test rows | ap |  | 0.2482 | 0.0313 | 0.1972 | 0.1808 | 0.2176 | 0.0369 | 15,492 | 1,541 |
| B frozen | B test rows | roc\_auc |  | 0.6372 | 0.0152 | 0.6360 | 0.6201 | 0.6517 | 0.0316 | 15,492 | 1,541 |
| B frozen | B test rows | brier |  | 0.1146 | 0.0135 | 0.0867 | 0.0834 | 0.0902 | 0.0068 | 15,492 | 1,541 |
| B frozen | B test rows | precision |  |  |  | 0.2077 | 0.1905 | 0.2256 | 0.0351 | 15,492 | 1,541 |
| B frozen | B test rows | recall |  |  |  | 0.3005 | 0.2771 | 0.3243 | 0.0472 | 15,492 | 1,541 |
| B frozen | B test rows | f1 |  |  |  | 0.2456 | 0.2265 | 0.2642 | 0.0377 | 15,492 | 1,541 |
| B frozen | B test rows | alert\_rate |  |  |  | 0.1439 | 0.1384 | 0.1498 | 0.0114 | 15,492 | 1,541 |
| A frozen | B test rows | ap |  | 0.2302 | 0.0305 | 0.1785 | 0.1631 | 0.1974 | 0.0344 | 15,492 | 1,541 |
| A frozen | B test rows | roc\_auc |  | 0.6259 | 0.0119 | 0.6040 | 0.5894 | 0.6203 | 0.0309 | 15,492 | 1,541 |
| A frozen | B test rows | brier |  | 0.1162 | 0.0135 | 0.0893 | 0.0862 | 0.0926 | 0.0065 | 15,492 | 1,541 |
| A frozen | B test rows | precision |  |  |  | 0.1583 | 0.1463 | 0.1713 | 0.0250 | 15,492 | 1,541 |
| A frozen | B test rows | recall |  |  |  | 0.3556 | 0.3327 | 0.3806 | 0.0479 | 15,492 | 1,541 |
| A frozen | B test rows | f1 |  |  |  | 0.2191 | 0.2040 | 0.2354 | 0.0315 | 15,492 | 1,541 |
| A frozen | B test rows | alert\_rate |  |  |  | 0.2235 | 0.2166 | 0.2299 | 0.0133 | 15,492 | 1,541 |
| B plain | B test rows | ap | 0.2369 | 0.2616 | 0.0349 | 0.1992 | 0.1828 | 0.2197 | 0.0369 | 15,492 | 1,541 |
| B plain | B test rows | roc\_auc | 0.6712 | 0.6536 | 0.0150 | 0.6341 | 0.6184 | 0.6495 | 0.0311 | 15,492 | 1,541 |
| B plain | B test rows | brier | 0.0977 | 0.1141 | 0.0136 | 0.0864 | 0.0830 | 0.0900 | 0.0070 | 15,492 | 1,541 |
| B plain | B test rows | precision |  |  |  | 0.2258 | 0.2056 | 0.2456 | 0.0400 | 15,492 | 1,541 |
| B plain | B test rows | recall |  |  |  | 0.2544 | 0.2332 | 0.2763 | 0.0431 | 15,492 | 1,541 |
| B plain | B test rows | f1 |  |  |  | 0.2392 | 0.2193 | 0.2587 | 0.0394 | 15,492 | 1,541 |
| B plain | B test rows | alert\_rate |  |  |  | 0.1121 | 0.1073 | 0.1170 | 0.0097 | 15,492 | 1,541 |
| B dummy | B test rows | ap | 0.1167 | 0.1380 | 0.0198 | 0.0995 | 0.0951 | 0.1040 | 0.0089 | 15,492 | 1,541 |
| B dummy | B test rows | roc\_auc | 0.5000 | 0.5000 | 0.0000 | 0.5000 | 0.5000 | 0.5000 | 0.0000 | 15,492 | 1,541 |
| B dummy | B test rows | brier | 0.1030 | 0.1197 | 0.0150 | 0.0909 | 0.0877 | 0.0942 | 0.0065 | 15,492 | 1,541 |
| B dummy | B test rows | precision |  |  |  | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 15,492 | 1,541 |
| B dummy | B test rows | recall |  |  |  | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 15,492 | 1,541 |
| B dummy | B test rows | f1 |  |  |  | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 15,492 | 1,541 |
| B dummy | B test rows | alert\_rate |  |  |  | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 15,492 | 1,541 |
| A frozen | A test rows | ap |  | 0.2317 | 0.0276 | 0.1750 | 0.1611 | 0.1891 | 0.0280 | 18,966 | 1,968 |
| A frozen | A test rows | roc\_auc |  | 0.6143 | 0.0135 | 0.5952 | 0.5822 | 0.6086 | 0.0264 | 18,966 | 1,968 |
| A frozen | A test rows | brier |  | 0.1239 | 0.0134 | 0.0933 | 0.0904 | 0.0961 | 0.0057 | 18,966 | 1,968 |
| A frozen | A test rows | precision |  |  |  | 0.1526 | 0.1428 | 0.1621 | 0.0193 | 18,966 | 1,968 |
| A frozen | A test rows | recall |  |  |  | 0.3801 | 0.3601 | 0.4018 | 0.0416 | 18,966 | 1,968 |
| A frozen | A test rows | f1 |  |  |  | 0.2178 | 0.2047 | 0.2304 | 0.0257 | 18,966 | 1,968 |
| A frozen | A test rows | alert\_rate |  |  |  | 0.2584 | 0.2521 | 0.2641 | 0.0120 | 18,966 | 1,968 |
| A plain | A test rows | ap | 0.2213 | 0.2435 | 0.0314 | 0.1775 | 0.1636 | 0.1919 | 0.0282 | 18,966 | 1,968 |
| A plain | A test rows | roc\_auc | 0.6399 | 0.6213 | 0.0161 | 0.5995 | 0.5863 | 0.6127 | 0.0264 | 18,966 | 1,968 |
| A plain | A test rows | brier | 0.1078 | 0.1243 | 0.0143 | 0.0935 | 0.0905 | 0.0963 | 0.0058 | 18,966 | 1,968 |
| A plain | A test rows | precision |  |  |  | 0.1507 | 0.1405 | 0.1598 | 0.0192 | 18,966 | 1,968 |
| A plain | A test rows | recall |  |  |  | 0.3740 | 0.3541 | 0.3951 | 0.0410 | 18,966 | 1,968 |
| A plain | A test rows | f1 |  |  |  | 0.2148 | 0.2021 | 0.2264 | 0.0243 | 18,966 | 1,968 |
| A plain | A test rows | alert\_rate |  |  |  | 0.2576 | 0.2509 | 0.2635 | 0.0126 | 18,966 | 1,968 |
| A dummy | A test rows | ap | 0.1281 | 0.1482 | 0.0198 | 0.1038 | 0.0995 | 0.1079 | 0.0083 | 18,966 | 1,968 |
| A dummy | A test rows | roc\_auc | 0.5000 | 0.5000 | 0.0000 | 0.5000 | 0.5000 | 0.5000 | 0.0000 | 18,966 | 1,968 |
| A dummy | A test rows | brier | 0.1116 | 0.1269 | 0.0145 | 0.0948 | 0.0919 | 0.0977 | 0.0059 | 18,966 | 1,968 |
| A dummy | A test rows | precision |  |  |  | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 18,966 | 1,968 |
| A dummy | A test rows | recall |  |  |  | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 18,966 | 1,968 |
| A dummy | A test rows | f1 |  |  |  | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 18,966 | 1,968 |
| A dummy | A test rows | alert\_rate |  |  |  | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 18,966 | 1,968 |

Where the validation numbers come from:

| model | rows | validation\_source |
| --- | --- | --- |
| B frozen | B test rows | b08 metrics\_by\_population.csv (sigmoid) |
| B frozen | B test rows | nan |
| A frozen | B test rows | b08 metrics\_by\_population.csv (sigmoid) |
| A frozen | B test rows | nan |
| B plain | B test rows | b06 metrics\_long.csv (raw) |
| B dummy | B test rows | b06 metrics\_long.csv (raw) |
| A frozen | A test rows | b08 metrics\_by\_population.csv (sigmoid) |
| A frozen | A test rows | nan |
| A plain | A test rows | s06 metrics\_long.csv (raw) |
| A dummy | A test rows | s06 metrics\_long.csv (raw) |

- PASS: no refit: B's and A's bundles re-predict T1's test predictions on the rebuilt rows (within 1e-9) (B 15,492 rows (max difference 9.7e-17), A 18,966 rows (max difference 9.7e-17); CSV round-trip only)
- PASS: every restated test number equals T1's metrics\_test.csv
- PASS: bootstrap intervals contain the T1 point estimate (1000 resamples, seed 42)
- PASS: validation scores are labelled selection scores (source column filled wherever a value is shown)
- PASS: A's tree untouched: A's code matches e5-A-frozen

## B9.2 B versus A, and B versus its references, on B's test rows

**What was done:** B minus A on B's test rows: AP +0.0187 \[+0.0089, +0.0291\] (excludes zero).

&#91;embedded content: paired\_test\_differences.csv · B9 run, B frozen minus A frozen on B's test rows (alert rate omitted: a volume, not a quality)\]

(paired\_test\_differences.csv; 1,000 paired resamples of test orders, seed 42)

| comparison | rows | metric | difference | ci\_low | ci\_high | b\_better | interval\_excludes\_zero |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B frozen minus A frozen | B test rows | ap | 0.0187 | 0.0089 | 0.0291 | True | True |
| B frozen minus A frozen | B test rows | roc\_auc | 0.0320 | 0.0203 | 0.0442 | True | True |
| B frozen minus A frozen | B test rows | brier | -0.0026 | -0.0031 | -0.0019 | True | True |
| B frozen minus A frozen | B test rows | precision | 0.0494 | 0.0368 | 0.0616 | True | True |
| B frozen minus A frozen | B test rows | recall | -0.0552 | -0.0771 | -0.0350 | False | True |
| B frozen minus A frozen | B test rows | f1 | 0.0266 | 0.0115 | 0.0404 | True | True |
| B frozen minus A frozen | B test rows | alert\_rate | -0.0796 | -0.0855 | -0.0733 | nan | True |
| B frozen minus B plain | B test rows | ap | -0.0020 | -0.0058 | 0.0022 | False | False |
| B frozen minus B plain | B test rows | roc\_auc | 0.0020 | -0.0044 | 0.0088 | True | False |
| B frozen minus B plain | B test rows | brier | 0.0003 | -0.0000 | 0.0006 | False | False |
| B frozen minus B plain | B test rows | precision | -0.0181 | -0.0284 | -0.0080 | False | True |
| B frozen minus B plain | B test rows | recall | 0.0461 | 0.0328 | 0.0589 | True | True |
| B frozen minus B plain | B test rows | f1 | 0.0064 | -0.0046 | 0.0170 | True | False |
| B frozen minus B plain | B test rows | alert\_rate | 0.0318 | 0.0281 | 0.0356 | nan | True |
| B frozen minus B dummy | B test rows | ap | 0.0977 | 0.0827 | 0.1165 | True | True |
| B frozen minus B dummy | B test rows | roc\_auc | 0.1360 | 0.1201 | 0.1517 | True | True |
| B frozen minus B dummy | B test rows | brier | -0.0042 | -0.0051 | -0.0033 | True | True |
| B frozen minus B dummy | B test rows | precision | 0.2077 | 0.1905 | 0.2256 | True | True |
| B frozen minus B dummy | B test rows | recall | 0.3005 | 0.2771 | 0.3243 | True | True |
| B frozen minus B dummy | B test rows | f1 | 0.2456 | 0.2265 | 0.2642 | True | True |
| B frozen minus B dummy | B test rows | alert\_rate | 0.1439 | 0.1384 | 0.1498 | nan | True |

- PASS: bootstrap intervals contain the T1 point estimate (1000 resamples, seed 42)

## B9.3 Error analysis by slice

**What was done:** Slices judged with more than 100 test detractors. Customer state: 3 judged, 4 too few. Pooled over judged states: precision A 0.164 / B 0.219, recall A 0.338 / B 0.278.

A slice is judged only with more than 100 test detractors; the rest are "too few to judge" (G-40). Precision and recall at the frozen threshold 1/6.

Aggregate over judged slices (subgroups\_aggregate.csv):

| slice | judged\_slices | too\_few | pooled\_precision\_A | pooled\_recall\_A | mean\_precision\_A | sd\_precision\_A | mean\_recall\_A | sd\_recall\_A | pooled\_precision\_B | pooled\_recall\_B | mean\_precision\_B | sd\_precision\_B | mean\_recall\_B | sd\_recall\_B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| customer\_state | 3 | 4 | 0.164 | 0.338 | 0.188 | 0.048 | 0.455 | 0.338 | 0.219 | 0.278 | 0.231 | 0.037 | 0.333 | 0.187 |
| route\_seller\_to\_customer\_state | 3 | 45 | 0.156 | 0.338 | 0.181 | 0.048 | 0.515 | 0.414 | 0.208 | 0.277 | 0.218 | 0.029 | 0.351 | 0.210 |
| basket | 2 | 1 | 0.149 | 0.322 | 0.201 | 0.132 | 0.489 | 0.375 | 0.199 | 0.268 | 0.254 | 0.145 | 0.397 | 0.290 |
| sellers | 2 | 0 | 0.158 | 0.356 | 0.292 | 0.223 | 0.651 | 0.493 | 0.208 | 0.300 | 0.314 | 0.195 | 0.613 | 0.523 |

&#91;image: by\_customer\_state\]

**customer\_state**:

| value | orders | detractors | alerts\_A | precision\_A | recall\_A | alerts\_B | precision\_B | recall\_B | judged |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SP | 8,450 | 815 | 719 | 0.203 | 0.179 | 701 | 0.233 | 0.200 | True |
| RJ | 2,056 | 256 | 1,576 | 0.135 | 0.832 | 723 | 0.194 | 0.547 | True |
| MG | 1,981 | 187 | 291 | 0.227 | 0.353 | 176 | 0.267 | 0.251 | True |
| PR | 925 | 81 | 75 | 0.160 | 0.148 | 76 | 0.224 | 0.210 | False |
| RS | 897 | 78 | 199 | 0.151 | 0.385 | 118 | 0.195 | 0.295 | False |
| BA | 610 | 71 | 407 | 0.133 | 0.761 | 321 | 0.159 | 0.718 | False |
| SC | 573 | 53 | 195 | 0.138 | 0.509 | 114 | 0.193 | 0.415 | False |

**route\_seller\_to\_customer\_state** — judged routes only (3 of 48; the other 45 are too small to judge; full list in subgroups.csv):

| value | orders | detractors | alerts\_A | precision\_A | recall\_A | alerts\_B | precision\_B | recall\_B | judged |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SP->SP | 6,624 | 621 | 510 | 0.194 | 0.159 | 572 | 0.215 | 0.198 | True |
| SP->RJ | 1,293 | 161 | 1,219 | 0.128 | 0.969 | 499 | 0.190 | 0.590 | True |
| SP->MG | 1,236 | 125 | 234 | 0.222 | 0.416 | 133 | 0.248 | 0.264 | True |

**basket**:

| value | orders | detractors | alerts\_A | precision\_A | recall\_A | alerts\_B | precision\_B | recall\_B | judged |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 item | 13,981 | 1,188 | 2,463 | 0.108 | 0.224 | 1,505 | 0.151 | 0.192 | True |
| 2 items | 1,168 | 269 | 689 | 0.295 | 0.755 | 454 | 0.357 | 0.602 | True |
| 3+ items | 343 | 84 | 310 | 0.255 | 0.940 | 270 | 0.270 | 0.869 | False |

**sellers**:

| value | orders | detractors | alerts\_A | precision\_A | recall\_A | alerts\_B | precision\_B | recall\_B | judged |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 seller | 15,230 | 1,423 | 3,200 | 0.134 | 0.302 | 1,972 | 0.176 | 0.244 | True |
| 2+ sellers | 262 | 118 | 262 | 0.450 | 1.000 | 257 | 0.451 | 0.983 | True |

- PASS: slice rule: a slice is judged only above the minimum

## B9.4 Drift: final-fit rows vs test rows (G-77)

**What was done:** 4 numeric features moved by |SMD| >= 0.2 between final-fit and test rows: route\_recent\_delivery\_days -0.76, route\_recent\_carrier\_transit\_days -0.58, purchase\_month +0.41, order\_dispatch\_days -0.21. Target: prevalence 0.136 -> 0.099 (G-77).

&#91;image: drift\_numeric\]

Numeric features (standardised mean difference, test minus final-fit; |0.2| or more is a notable move):

| feature | development | test | change |
| --- | --- | --- | --- |
| route\_recent\_delivery\_days | 10.832 | 7.880 | -0.761 |
| route\_recent\_carrier\_transit\_days | 7.645 | 5.466 | -0.583 |
| purchase\_month | 5.893 | 6.952 | 0.406 |
| order\_dispatch\_days | 3.261 | 2.621 | -0.209 |
| seller\_prior\_dispatch\_days | 3.238 | 2.871 | -0.194 |
| interstate\_share | 0.575 | 0.516 | -0.120 |
| total\_freight | 20.165 | 22.194 | 0.106 |
| total\_volume\_cm3 | 18205.301 | 15219.687 | -0.104 |
| n\_categories | 0.991 | 1.004 | 0.096 |
| distance\_km\_max | 424.490 | 392.623 | -0.090 |
| seller\_prior\_late\_handover\_rate | 0.084 | 0.074 | -0.090 |
| product\_description\_lenght | 772.952 | 822.648 | 0.076 |
| order\_handover\_late\_days | 0.219 | 0.135 | -0.076 |
| total\_weight\_g | 2471.214 | 2124.040 | -0.076 |
| seller\_prior\_late\_handover\_days | 0.281 | 0.218 | -0.073 |
| freight\_ratio | 0.284 | 0.301 | 0.060 |
| payment\_installments\_max | 2.887 | 2.740 | -0.056 |
| seller\_prior\_review\_mean | 4.172 | 4.151 | -0.050 |
| n\_sellers | 1.013 | 1.018 | 0.035 |
| order\_handed\_over\_late | 0.086 | 0.077 | -0.033 |
| n\_items | 1.145 | 1.136 | -0.018 |
| total\_price | 131.537 | 131.616 | 0.000 |
| n\_products | 1.039 | 1.039 | -0.000 |

Categorical features and history sources (total variation distance per feature; share changes of the levels that moved most):

| kind | feature | level | development | test | change |
| --- | --- | --- | --- | --- | --- |
| categorical | route\_seller\_to\_customer\_state | SP->SP | 0.379 | 0.428 | 0.048 |
| categorical | route\_seller\_to\_customer\_state | SP->RJ | 0.108 | 0.083 | -0.024 |
| categorical | route\_seller\_to\_customer\_state | SP->MG | 0.097 | 0.080 | -0.017 |
| categorical | route\_seller\_to\_customer\_state | SP->RS | 0.047 | 0.038 | -0.010 |
| categorical | route\_seller\_to\_customer\_state | SP->SC | 0.030 | 0.023 | -0.007 |
| categorical | route\_seller\_to\_customer\_state | RJ->SP | 0.015 | 0.021 | 0.006 |
| categorical | route\_seller\_to\_customer\_state | MG->SP | 0.033 | 0.028 | -0.005 |
| categorical | route\_seller\_to\_customer\_state | RJ->RJ | 0.011 | 0.016 | 0.005 |
| categorical | route\_seller\_to\_customer\_state | MG->RJ | 0.015 | 0.012 | -0.004 |
| categorical | route\_seller\_to\_customer\_state | RS->SP | 0.008 | 0.011 | 0.003 |
| categorical total | route\_seller\_to\_customer\_state | (all levels) |  |  | 0.080 |
| categorical | primary\_category | health\_beauty | 0.076 | 0.107 | 0.031 |
| categorical | primary\_category | housewares | 0.057 | 0.083 | 0.026 |
| categorical | primary\_category | cool\_stuff | 0.040 | 0.017 | -0.022 |
| categorical | primary\_category | sports\_leisure | 0.083 | 0.065 | -0.019 |
| categorical | primary\_category | watches\_gifts | 0.051 | 0.069 | 0.018 |
| categorical | primary\_category | toys | 0.042 | 0.027 | -0.016 |
| categorical | primary\_category | garden\_tools | 0.038 | 0.023 | -0.015 |
| categorical | primary\_category | furniture\_decor | 0.069 | 0.055 | -0.014 |
| categorical | primary\_category | construction\_tools\_construction | 0.005 | 0.019 | 0.014 |
| categorical | primary\_category | computers\_accessories | 0.069 | 0.056 | -0.013 |
| categorical | primary\_category | auto | 0.036 | 0.048 | 0.012 |
| categorical | primary\_category | Unknown | 0.017 | 0.006 | -0.011 |
| categorical | primary\_category | pet\_shop | 0.016 | 0.027 | 0.010 |
| categorical | primary\_category | telephony | 0.042 | 0.033 | -0.010 |
| categorical | primary\_category | perfumery | 0.032 | 0.024 | -0.007 |
| categorical | primary\_category | food | 0.003 | 0.010 | 0.007 |
| categorical | primary\_category | baby | 0.027 | 0.034 | 0.007 |
| categorical | primary\_category | fashion\_bags\_accessories | 0.020 | 0.014 | -0.006 |
| categorical | primary\_category | office\_furniture | 0.014 | 0.008 | -0.006 |
| categorical | primary\_category | construction\_tools\_lights | 0.001 | 0.007 | 0.006 |
| categorical | primary\_category | electronics | 0.026 | 0.021 | -0.005 |
| categorical | primary\_category | home\_appliances | 0.007 | 0.012 | 0.005 |
| categorical | primary\_category | home\_construction | 0.004 | 0.008 | 0.005 |
| categorical | primary\_category | consoles\_games | 0.011 | 0.008 | -0.003 |
| categorical | primary\_category | furniture\_living\_room | 0.003 | 0.006 | 0.003 |
| categorical | primary\_category | books\_technical | 0.002 | 0.005 | 0.003 |
| categorical | primary\_category | luggage\_accessories | 0.012 | 0.009 | -0.003 |
| categorical | primary\_category | art | 0.002 | 0.004 | 0.002 |
| categorical | primary\_category | market\_place | 0.003 | 0.001 | -0.002 |
| categorical | primary\_category | fashion\_shoes | 0.003 | 0.001 | -0.002 |
| categorical | primary\_category | small\_appliances\_home\_oven\_and\_coffee | 0.000 | 0.002 | 0.002 |
| categorical | primary\_category | signaling\_and\_security | 0.001 | 0.003 | 0.002 |
| categorical | primary\_category | home\_confort | 0.005 | 0.003 | -0.001 |
| categorical | primary\_category | small\_appliances | 0.007 | 0.005 | -0.001 |
| categorical | primary\_category | construction\_tools\_safety | 0.001 | 0.002 | 0.001 |
| categorical | primary\_category | agro\_industry\_and\_commerce | 0.002 | 0.003 | 0.001 |
| categorical | primary\_category | bed\_bath\_table | 0.103 | 0.102 | -0.001 |
| categorical | primary\_category | fashion\_underwear\_beach | 0.001 | 0.000 | -0.001 |
| categorical | primary\_category | arts\_and\_craftmanship | 0.000 | 0.001 | 0.001 |
| categorical | primary\_category | kitchen\_dining\_laundry\_garden\_furniture | 0.003 | 0.004 | 0.001 |
| categorical | primary\_category | cine\_photo | 0.000 | 0.001 | 0.001 |
| categorical | primary\_category | furniture\_bedroom | 0.001 | 0.002 | 0.001 |
| categorical | primary\_category | tablets\_printing\_image | 0.001 | 0.000 | -0.001 |
| categorical | primary\_category | drinks | 0.003 | 0.004 | 0.001 |
| categorical | primary\_category | party\_supplies | 0.000 | 0.001 | 0.001 |
| categorical | primary\_category | home\_appliances\_2 | 0.002 | 0.003 | 0.001 |
| categorical | primary\_category | stationery | 0.024 | 0.024 | 0.001 |
| categorical | primary\_category | diapers\_and\_hygiene | 0.000 | 0.001 | 0.001 |
| categorical | primary\_category | computers | 0.002 | 0.001 | -0.000 |
| categorical | primary\_category | furniture\_mattress\_and\_upholstery | 0.001 | 0.000 | -0.000 |
| categorical | primary\_category | fashion\_male\_clothing | 0.001 | 0.001 | -0.000 |
| categorical | primary\_category | costruction\_tools\_garden | 0.002 | 0.002 | 0.000 |
| categorical | primary\_category | air\_conditioning | 0.003 | 0.002 | -0.000 |
| categorical | primary\_category | fashio\_female\_clothing | 0.000 | 0.000 | -0.000 |
| categorical | primary\_category | music | 0.000 | 0.001 | 0.000 |
| categorical | primary\_category | fashion\_sport | 0.000 | 0.000 | -0.000 |
| categorical | primary\_category | food\_drink | 0.002 | 0.002 | -0.000 |
| categorical | primary\_category | fixed\_telephony | 0.002 | 0.002 | -0.000 |
| categorical | primary\_category | flowers | 0.000 | 0.000 | -0.000 |
| categorical | primary\_category | books\_imported | 0.001 | 0.001 | 0.000 |
| categorical | primary\_category | costruction\_tools\_tools | 0.001 | 0.001 | 0.000 |
| categorical | primary\_category | la\_cuisine | 0.000 | 0.000 | -0.000 |
| categorical | primary\_category | musical\_instruments | 0.006 | 0.006 | 0.000 |
| categorical | primary\_category | cds\_dvds\_musicals | 0.000 | 0.000 | -0.000 |
| categorical | primary\_category | audio | 0.003 | 0.003 | -0.000 |
| categorical | primary\_category | books\_general\_interest | 0.005 | 0.005 | -0.000 |
| categorical | primary\_category | dvds\_blu\_ray | 0.000 | 0.000 | 0.000 |
| categorical | primary\_category | home\_comfort\_2 | 0.000 | 0.000 | -0.000 |
| categorical | primary\_category | christmas\_supplies | 0.001 | 0.001 | 0.000 |
| categorical | primary\_category | fashion\_childrens\_clothes | 0.000 | 0.000 | -0.000 |
| categorical | primary\_category | industry\_commerce\_and\_business | 0.002 | 0.002 | 0.000 |
| categorical total | primary\_category | (all levels) |  |  | 0.163 |
| source share | seller\_prior\_source | own seller history | 0.967 | 0.963 | -0.004 |
| source share | seller\_prior\_source | seller-state fallback | 0.033 | 0.037 | 0.004 |
| categorical total | seller\_prior\_source | (all levels) |  |  | 0.004 |
| source share | route\_recent\_delivery\_days\_source | state-mix fallback | 0.041 | 0.027 | -0.014 |
| source share | route\_recent\_delivery\_days\_source | own route history | 0.959 | 0.973 | 0.014 |
| categorical total | route\_recent\_delivery\_days\_source | (all levels) |  |  | 0.014 |
| source share | route\_recent\_carrier\_transit\_days\_source | state-mix fallback | 0.041 | 0.027 | -0.014 |
| source share | route\_recent\_carrier\_transit\_days\_source | own route history | 0.959 | 0.973 | 0.014 |
| categorical total | route\_recent\_carrier\_transit\_days\_source | (all levels) |  |  | 0.014 |

Target:

| feature | level | development | test | change | measure |
| --- | --- | --- | --- | --- | --- |
| is\_detractor | prevalence | 0.136 | 0.099 | -0.037 | difference |

## B9.5 Interpretation

**What was done:** Largest term: route\_seller\_to\_customer\_state\_RS->MG. Top permutation feature: n\_sellers. Against B4's ranking: Spearman 0.31, top-10 overlap 6; DIVERGES: team alerted, model unchanged.

**Coefficients of B's frozen model** (coefficients.csv; odds ratio per +1 unit of the transformed term; mean over the 3 time-ordered calibration splits (min/max shown)). The largest terms are mostly single levels of categorical features (one-hot); the numeric terms are listed separately below because they carry the business levers.

&#91;image: coefficients\]

Largest 15 terms overall:

| term | coefficient | coefficient\_min | coefficient\_max | odds\_ratio |
| --- | --- | --- | --- | --- |
| route\_seller\_to\_customer\_state\_RS->MG | -1.814 | -3.551 | -0.823 | 0.163 |
| primary\_category\_food\_drink | -1.624 | -3.014 | -0.670 | 0.197 |
| primary\_category\_dvds\_blu\_ray | 1.604 | 0.593 | 2.158 | 4.974 |
| primary\_category\_books\_technical | -1.528 | -2.128 | -0.496 | 0.217 |
| route\_seller\_to\_customer\_state\_RS->RS | -1.322 | -1.647 | -1.105 | 0.267 |
| primary\_category\_costruction\_tools\_garden | -1.109 | -2.816 | 0.071 | 0.330 |
| primary\_category\_industry\_commerce\_and\_business | -1.066 | -1.535 | -0.320 | 0.344 |
| route\_seller\_to\_customer\_state\_BA->RJ | 1.014 | 0.379 | 2.257 | 2.757 |
| primary\_category\_cds\_dvds\_musicals | -0.995 | -1.274 | -0.471 | 0.370 |
| primary\_category\_fashion\_male\_clothing | 0.903 | 0.831 | 1.041 | 2.468 |
| route\_seller\_to\_customer\_state\_BA->PR | 0.897 | 0.371 | 1.250 | 2.452 |
| route\_seller\_to\_customer\_state\_RS->SC | -0.800 | -1.114 | -0.510 | 0.449 |
| route\_seller\_to\_customer\_state\_SC->BA | 0.780 | 0.684 | 0.872 | 2.182 |
| primary\_category\_art | 0.772 | 0.595 | 1.072 | 2.164 |
| route\_seller\_to\_customer\_state\_BA->RS | -0.759 | -0.947 | -0.571 | 0.468 |

Numeric terms (all):

| term | coefficient | coefficient\_min | coefficient\_max | odds\_ratio |
| --- | --- | --- | --- | --- |
| route\_recent\_delivery\_days | 0.332 | 0.129 | 0.450 | 1.394 |
| route\_recent\_carrier\_transit\_days | -0.170 | -0.221 | -0.111 | 0.844 |
| order\_dispatch\_days | 0.164 | 0.157 | 0.167 | 1.178 |
| n\_sellers | 0.140 | 0.099 | 0.165 | 1.150 |
| order\_handover\_late\_days | 0.139 | 0.131 | 0.147 | 1.149 |
| total\_freight | 0.127 | 0.086 | 0.160 | 1.135 |
| n\_items | 0.126 | 0.109 | 0.139 | 1.134 |
| seller\_prior\_review\_mean | -0.098 | -0.098 | -0.097 | 0.907 |
| interstate\_share | -0.073 | -0.356 | 0.078 | 0.929 |
| total\_volume\_cm3 | -0.060 | -0.087 | -0.046 | 0.942 |
| payment\_installments\_max | 0.045 | 0.035 | 0.054 | 1.046 |
| n\_categories | -0.044 | -0.062 | -0.010 | 0.957 |
| seller\_prior\_dispatch\_days | 0.037 | 0.017 | 0.058 | 1.038 |
| total\_price | -0.037 | -0.062 | 0.010 | 0.964 |
| product\_description\_lenght | -0.037 | -0.044 | -0.030 | 0.964 |
| seller\_prior\_late\_handover\_days | 0.031 | 0.007 | 0.044 | 1.032 |
| distance\_km\_max | -0.028 | -0.058 | 0.004 | 0.972 |
| n\_products | 0.024 | 0.022 | 0.027 | 1.024 |
| missingindicator\_total\_volume\_cm3 | 0.018 | 0.009 | 0.027 | 1.018 |
| missingindicator\_product\_description\_lenght | -0.015 | -0.037 | 0.005 | 0.985 |
| missingindicator\_seller\_prior\_review\_mean | 0.012 | -0.013 | 0.030 | 1.012 |
| order\_handed\_over\_late | -0.010 | -0.026 | 0.002 | 0.990 |
| freight\_ratio | -0.009 | -0.018 | 0.001 | 0.991 |
| purchase\_month | -0.004 | -0.084 | 0.074 | 0.996 |
| seller\_prior\_late\_handover\_rate | 0.003 | -0.001 | 0.007 | 1.003 |
| total\_weight\_g | -0.000 | -0.036 | 0.028 | 1.000 |

**Permutation importance on B's test rows** (permutation\_importance.csv; description only, B9-D2):

&#91;image: permutation\_importance\]

| feature | importance\_mean | importance\_sd | rank |
| --- | --- | --- | --- |
| n\_sellers | 0.0367 | 0.0030 | 1 |
| route\_recent\_delivery\_days | 0.0313 | 0.0020 | 2 |
| n\_items | 0.0154 | 0.0018 | 3 |
| route\_recent\_carrier\_transit\_days | 0.0148 | 0.0014 | 4 |
| order\_handover\_late\_days | 0.0131 | 0.0005 | 5 |
| order\_dispatch\_days | 0.0086 | 0.0006 | 6 |
| total\_freight | 0.0076 | 0.0018 | 7 |
| route\_seller\_to\_customer\_state | 0.0051 | 0.0007 | 8 |
| seller\_prior\_review\_mean | 0.0050 | 0.0007 | 9 |
| interstate\_share | 0.0022 | 0.0004 | 10 |
| n\_products | 0.0016 | 0.0003 | 11 |
| payment\_installments\_max | 0.0011 | 0.0003 | 12 |
| distance\_km\_max | 0.0004 | 0.0003 | 13 |
| total\_volume\_cm3 | 0.0003 | 0.0004 | 14 |
| product\_description\_lenght | 0.0002 | 0.0003 | 15 |
| freight\_ratio | 0.0002 | 0.0000 | 16 |
| seller\_prior\_late\_handover\_rate | 0.0000 | 0.0000 | 17 |
| total\_price | -0.0000 | 0.0002 | 18 |
| total\_weight\_g | -0.0000 | 0.0000 | 19 |
| order\_handed\_over\_late | -0.0000 | 0.0001 | 20 |
| purchase\_month | -0.0001 | 0.0000 | 21 |
| seller\_prior\_late\_handover\_days | -0.0002 | 0.0001 | 22 |
| seller\_prior\_dispatch\_days | -0.0007 | 0.0002 | 23 |
| n\_categories | -0.0020 | 0.0002 | 24 |
| primary\_category | -0.0024 | 0.0025 | 25 |

**Against B4's development ranking** (ranking\_consistency.json): 25 features compared, Spearman 0.31, top-10 overlap 6. Rule: diverges when Spearman < 0.5 or fewer than 5 of the top 10 shared (as A's s09 9.5). Result: **DIVERGES**. Action: alert the team: the test-row importance differs from B4's development ranking; describe, do not change the frozen model. Note: B4 ranks each feature alone (Spearman or mutual information with the target); permutation importance measures what the fitted model loses without the feature, given the others, on the test period, so the two answer different questions.

## B9.6 Label sensitivity

**What was done:** B's test AP with the agreed label 0.1972; with the first-review label 0.1972.

(label\_sensitivity.csv) The first-review label and the agreed label almost coincide in the test cohort (prevalence columns), so the results do not depend on the label choice.

| model | rows | label | ap | roc\_auc | brier | precision | recall | prevalence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B frozen | B test rows | is\_detractor (agreed label) | 0.1972 | 0.6360 | 0.0867 | 0.2077 | 0.3005 | 0.0995 |
| B frozen | B test rows | is\_detractor\_first (first review) | 0.1972 | 0.6363 | 0.0866 | 0.2077 | 0.3006 | 0.0994 |
| A frozen | B test rows | is\_detractor (agreed label) | 0.1785 | 0.6040 | 0.0893 | 0.1583 | 0.3556 | 0.0995 |
| A frozen | B test rows | is\_detractor\_first (first review) | 0.1785 | 0.6043 | 0.0892 | 0.1583 | 0.3558 | 0.0994 |
| B plain | B test rows | is\_detractor (agreed label) | 0.1992 | 0.6341 | 0.0864 | 0.2258 | 0.2544 | 0.0995 |
| B plain | B test rows | is\_detractor\_first (first review) | 0.1993 | 0.6343 | 0.0864 | 0.2258 | 0.2545 | 0.0994 |
| A frozen | A test rows | is\_detractor (agreed label) | 0.1750 | 0.5952 | 0.0933 | 0.1526 | 0.3801 | 0.1038 |
| A frozen | A test rows | is\_detractor\_first (first review) | 0.1750 | 0.5954 | 0.0932 | 0.1526 | 0.3803 | 0.1037 |
| A plain | A test rows | is\_detractor (agreed label) | 0.1775 | 0.5995 | 0.0935 | 0.1507 | 0.3740 | 0.1038 |
| A plain | A test rows | is\_detractor\_first (first review) | 0.1775 | 0.5996 | 0.0935 | 0.1507 | 0.3742 | 0.1037 |

## B9.7 Business summary

**What was done:** At 1/6: B 23.2 alerts/day, precision 0.208, 463 detractors caught, cost 7,156 vs 7,705 with no alerts. Missed-dispatch rule on the test period: 1,273 orders flagged, precision 0.212, 16.8% of detractors.

Alert volume, catch and illustrative cost at the frozen threshold (business\_summary.csv, restating T1's metrics\_test.csv):

| model | rows | alerts\_per\_day | alerts | detractors\_caught | precision | recall | illustrative\_cost | cost\_per\_missed | cost\_per\_false\_alert |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B frozen | B test rows | 23.219 | 2,229 | 463 | 0.208 | 0.300 | 7156.000 | 5.000 | 1.000 |
| A frozen | B test rows | 36.062 | 3,462 | 548 | 0.158 | 0.356 | 7879.000 | 5.000 | 1.000 |
| A frozen | A test rows | 51.052 | 4,901 | 748 | 0.153 | 0.380 | 10253.000 | 5.000 | 1.000 |
| B dummy | B test rows | 0.000 | 0 | 0 | 0.000 | 0.000 | 7705.000 | 5.000 | 1.000 |
| A dummy | A test rows | 0.000 | 0 | 0 | 0.000 | 0.000 | 9840.000 | 5.000 | 1.000 |

Missed-dispatch rule (B-C10) on the test period (missed\_dispatch\_rule\_test.csv), beside the development result from B8 (missed\_dispatch\_rule.csv):

Test period:

| group | orders | detractors | precision | share\_of\_all\_detractors |
| --- | --- | --- | --- | --- |
| never handed over | 36 | 29 | 0.806 | 0.018 |
| handed over after the limit | 1,237 | 241 | 0.195 | 0.150 |
| all flagged (rule fires) | 1,273 | 270 | 0.212 | 0.168 |
| not flagged | 14,297 | 1,338 | 0.094 | 0.832 |

Development period (B8):

| group | orders | detractors | precision | share\_of\_all\_detractors |
| --- | --- | --- | --- | --- |
| never handed over | 429 | 374 | 0.872 | 0.042 |
| handed over after the limit | 5,475 | 1,431 | 0.261 | 0.161 |
| all flagged (rule fires) | 5,904 | 1,805 | 0.306 | 0.203 |
| not flagged | 55,923 | 7,079 | 0.127 | 0.797 |

**Files**: pipeline\_b/stages/b09/classification/outputs/ (run 20261024T052644Z): business\_summary.csv, coefficients.csv, conclusion.md, drift.csv, label\_sensitivity.csv, missed\_dispatch\_rule\_test.csv, paired\_test\_differences.csv, permutation\_importance.csv, ranking\_consistency.json, subgroups.csv, subgroups\_aggregate.csv, train\_val\_test.csv; plus figures/.
