# B6 › regression — evidence cards

## Supplement for decisions and the report (added 2026-10-24; DOC\_GAPS D-01, D-02)

Added after the pipeline ran, from accepted outputs only; nothing above is changed. Charts marked doc\_support come from pipeline\_b/stages/doc\_support/regression/outputs (run 20261024T065707Z, uncommitted, reads accepted outputs only). B6 figures and tables: pipeline\_b/stages/b06/regression/outputs (run 20261023T162830Z).

**Family ladder** (figures/family\_ladder.png):

&#91;image: family ladder\]

**Per-fold MAE of every family, training and validation** (doc\_support b\_b06\_per\_fold\_scores.csv from b06 metrics\_long.csv; validation = selection scores):

&#91;image: per-fold scores\]

| family | phase | fold\_1 | fold\_2 | fold\_3 | fold\_4 | fold\_5 | mean | se |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dummy | train | 4.5093 | 4.4272 | 4.4127 | 5.1081 | 5.5114 | 4.7937 | 0.2207 |
| dummy | validation | 4.4073 | 5.9751 | 6.8000 | 8.1627 | 4.4995 | 5.9689 | 0.7107 |
| forest | train | 3.8961 | 3.6164 | 3.5615 | 4.0943 | 4.3856 | 3.9108 | 0.1530 |
| forest | validation | 3.5846 | 5.2012 | 5.6926 | 6.8655 | 3.4698 | 4.9627 | 0.6457 |
| linear | train | 3.7720 | 3.5345 | 3.5057 | 4.0895 | 4.4018 | 3.8607 | 0.1711 |
| linear | validation | 3.7223 | 5.4678 | 5.6140 | 6.7724 | 3.5469 | 5.0247 | 0.6115 |
| tree | train | 3.9165 | 3.6352 | 3.6063 | 4.1466 | 4.4398 | 3.9489 | 0.1576 |
| tree | validation | 3.6808 | 5.1292 | 5.7792 | 7.0115 | 3.6654 | 5.0532 | 0.6394 |

**Paired gains between rungs, fold by fold** (paired\_differences.csv; gain > 0 = the more complex model is better):

| comparison | gain\_fold\_1 | gain\_fold\_2 | gain\_fold\_3 | gain\_fold\_4 | gain\_fold\_5 | mean\_gain | paired\_se | folds\_better | kept\_by\_one\_se\_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear/logistic vs dummy | 0.6850 | 0.5072 | 1.1860 | 1.3903 | 0.9526 | 0.9442 | 0.1606 | 5 | True |
| single tree vs linear/logistic | 0.0415 | 0.3386 | -0.1652 | -0.2391 | -0.1185 | -0.0285 | 0.1027 | 2 | False |
| forest vs linear/logistic | 0.1377 | 0.2667 | -0.0787 | -0.0931 | 0.0771 | 0.0619 | 0.0677 | 3 | False |

**Learning curves** (figures/learning\_curves.png; curves/learning\_curves.csv):

&#91;image: learning curves\]

| family | share | train\_rows | train\_mae | validation\_mae |
| --- | --- | --- | --- | --- |
| dummy | 0.2000 | 9,483 | 6.0732 | 4.8820 |
| linear | 0.2000 | 9,483 | 4.3413 | 3.1600 |
| tree | 0.2000 | 9,483 | 4.4241 | 3.3624 |
| forest | 0.2000 | 9,483 | 4.4527 | 3.5731 |
| dummy | 0.4000 | 18,966 | 6.3690 | 4.9534 |
| linear | 0.4000 | 18,966 | 4.7686 | 4.2864 |
| tree | 0.4000 | 18,966 | 4.9442 | 4.0173 |
| forest | 0.4000 | 18,966 | 4.8642 | 3.8763 |
| dummy | 0.6000 | 28,449 | 6.1009 | 4.8385 |
| linear | 0.6000 | 28,449 | 4.7639 | 3.8166 |
| tree | 0.6000 | 28,449 | 4.8295 | 3.7583 |
| forest | 0.6000 | 28,449 | 4.7607 | 3.7322 |
| dummy | 0.8000 | 37,932 | 5.7156 | 4.5381 |
| linear | 0.8000 | 37,932 | 4.4582 | 3.5837 |
| tree | 0.8000 | 37,932 | 4.4725 | 3.6581 |
| forest | 0.8000 | 37,932 | 4.4350 | 3.4808 |
| dummy | 1.0000 | 47,415 | 5.5114 | 4.4995 |
| linear | 1.0000 | 47,415 | 4.4018 | 3.5469 |
| tree | 1.0000 | 47,415 | 4.4398 | 3.6654 |
| forest | 1.0000 | 47,415 | 4.3856 | 3.4698 |

**Residual diagnostics** (figures/residual\_diagnostics.png; quantiles every 10% from curves/residual\_quantiles\_\*.csv):

&#91;image: residuals\]

linear/logistic:

| quantile | residual |
| --- | --- |
| 0.005 | -9.783 |
| 0.100 | -3.675 |
| 0.195 | -2.258 |
| 0.290 | -1.204 |
| 0.385 | -0.206 |
| 0.480 | 0.868 |
| 0.575 | 2.044 |
| 0.670 | 3.509 |
| 0.765 | 5.560 |
| 0.860 | 9.041 |
| 0.955 | 18.362 |

forest:

| quantile | residual |
| --- | --- |
| 0.005 | -7.950 |
| 0.100 | -3.986 |
| 0.195 | -2.768 |
| 0.290 | -1.770 |
| 0.385 | -0.781 |
| 0.480 | 0.255 |
| 0.575 | 1.472 |
| 0.670 | 2.999 |
| 0.765 | 5.220 |
| 0.860 | 8.802 |
| 0.955 | 18.420 |

**Design matrix per fold (linear/logistic)** (design\_matrix\_by\_fold.csv; full rank and condition number, see REPORT\_REQUESTS R-01):

| fold | candidate\_id | rows | encoded\_columns | duplicates\_dropped | columns | rank | full\_rank | condition\_number |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | reg.sel.log.linear | 7,932 | 131 | missingindicator\_total\_volume\_cm3 | 130 | 130 | True | 244.7404 |
| 2 | reg.sel.log.linear | 18,077 | 139 | missingindicator\_total\_volume\_cm3 | 138 | 138 | True | 285.0665 |
| 3 | reg.sel.log.linear | 26,184 | 140 | missingindicator\_total\_volume\_cm3 | 139 | 139 | True | 243.4654 |
| 4 | reg.sel.log.linear | 37,647 | 141 | missingindicator\_total\_volume\_cm3 | 140 | 140 | True | 385.7845 |
| 5 | reg.sel.log.linear | 47,415 | 141 | missingindicator\_total\_volume\_cm3 | 140 | 140 | True | 433.5520 |

**Imputation per fold** (imputation\_by\_fold.csv; values learned on each training fold only):

| fold | feature | rule | learned\_value | learned\_scale | route\_groups | filled\_train | filled\_validation | validation\_rows\_unseen\_level |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | route\_recent\_carrier\_transit\_days | median + missing indicator (after log1p) | 2.0622154620238375 | log1p |  | 0 | 0 |  |
| 1 | route\_recent\_delivery\_days | median + missing indicator (after log1p) | 2.405646248398061 | log1p |  | 0 | 0 |  |
| 1 | distance\_km\_max | median + missing indicator (after log1p) | 5.909602810408822 | log1p |  | 0 | 0 |  |
| 1 | total\_freight | median + missing indicator (after log1p) | 2.8069901489571136 | log1p |  | 0 | 0 |  |
| 1 | seller\_prior\_dispatch\_days | median + missing indicator (after log1p) | 1.3258016073819254 | log1p |  | 0 | 0 |  |
| 1 | seller\_prior\_late\_handover\_days | median + missing indicator (after log1p) | 0.05294859651759884 | log1p |  | 0 | 0 |  |
| 1 | total\_weight\_g | median + missing indicator (after log1p) | 6.68586094706836 | log1p |  | 8 | 4 |  |
| 1 | total\_price | median + missing indicator (after log1p) | 4.393213824064446 | log1p |  | 0 | 0 |  |
| 1 | total\_volume\_cm3 | median + missing indicator (after log1p) | 8.979542601725113 | log1p |  | 8 | 4 |  |
| 1 | interstate\_share | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 1 | seller\_prior\_late\_handover\_rate | median + missing indicator | 0.0433465085638998 | raw |  | 0 | 0 |  |
| 1 | freight\_ratio | median + missing indicator | 0.2101840736294518 | raw |  | 0 | 0 |  |
| 1 | purchase\_dayofweek | median + missing indicator | 3.0 | raw |  | 0 | 0 |  |
| 1 | n\_sellers | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 1 | purchase\_month | median + missing indicator | 4.0 | raw |  | 0 | 0 |  |
| 1 | n\_products | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 1 | payment\_installments\_max | median + missing indicator | 2.0 | raw |  | 0 | 0 |  |
| 1 | n\_items | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 1 | route\_seller\_to\_customer\_state | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 9.000 |
| 1 | primary\_category | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 62.000 |
| 1 | primary\_payment\_type | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 0.000 |
| 2 | route\_recent\_carrier\_transit\_days | median + missing indicator (after log1p) | 2.0585660126414775 | log1p |  | 0 | 0 |  |
| 2 | route\_recent\_delivery\_days | median + missing indicator (after log1p) | 2.3720245730698664 | log1p |  | 0 | 0 |  |
| 2 | distance\_km\_max | median + missing indicator (after log1p) | 5.903860923768761 | log1p |  | 0 | 0 |  |
| 2 | total\_freight | median + missing indicator (after log1p) | 2.8112082932048366 | log1p |  | 0 | 0 |  |
| 2 | seller\_prior\_dispatch\_days | median + missing indicator (after log1p) | 1.33319632024829 | log1p |  | 0 | 0 |  |
| 2 | seller\_prior\_late\_handover\_days | median + missing indicator (after log1p) | 0.05021692814462943 | log1p |  | 0 | 0 |  |
| 2 | total\_weight\_g | median + missing indicator (after log1p) | 6.7464121285733745 | log1p |  | 11 | 0 |  |
| 2 | total\_price | median + missing indicator (after log1p) | 4.393213824064446 | log1p |  | 0 | 0 |  |
| 2 | total\_volume\_cm3 | median + missing indicator (after log1p) | 8.987321812850125 | log1p |  | 11 | 0 |  |
| 2 | interstate\_share | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 2 | seller\_prior\_late\_handover\_rate | median + missing indicator | 0.0364025695931477 | raw |  | 0 | 0 |  |
| 2 | freight\_ratio | median + missing indicator | 0.2114893617021276 | raw |  | 0 | 0 |  |
| 2 | purchase\_dayofweek | median + missing indicator | 3.0 | raw |  | 0 | 0 |  |
| 2 | n\_sellers | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 2 | purchase\_month | median + missing indicator | 6.0 | raw |  | 0 | 0 |  |
| 2 | n\_products | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 2 | payment\_installments\_max | median + missing indicator | 2.0 | raw |  | 0 | 0 |  |
| 2 | n\_items | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 2 | route\_seller\_to\_customer\_state | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 0.000 |
| 2 | primary\_category | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 6.000 |
| 2 | primary\_payment\_type | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 0.000 |
| 3 | route\_recent\_carrier\_transit\_days | median + missing indicator (after log1p) | 2.039382120427744 | log1p |  | 0 | 0 |  |
| 3 | route\_recent\_delivery\_days | median + missing indicator (after log1p) | 2.355779619980923 | log1p |  | 0 | 0 |  |
| 3 | distance\_km\_max | median + missing indicator (after log1p) | 5.902476881221825 | log1p |  | 0 | 0 |  |
| 3 | total\_freight | median + missing indicator (after log1p) | 2.813610696762703 | log1p |  | 0 | 0 |  |
| 3 | seller\_prior\_dispatch\_days | median + missing indicator (after log1p) | 1.3378119209801416 | log1p |  | 0 | 0 |  |
| 3 | seller\_prior\_late\_handover\_days | median + missing indicator (after log1p) | 0.04743112236452102 | log1p |  | 0 | 0 |  |
| 3 | total\_weight\_g | median + missing indicator (after log1p) | 6.7464121285733745 | log1p |  | 12 | 0 |  |
| 3 | total\_price | median + missing indicator (after log1p) | 4.394202210604015 | log1p |  | 0 | 0 |  |
| 3 | total\_volume\_cm3 | median + missing indicator (after log1p) | 8.987321812850125 | log1p |  | 12 | 0 |  |
| 3 | interstate\_share | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 3 | seller\_prior\_late\_handover\_rate | median + missing indicator | 0.03536359425660025 | raw |  | 0 | 0 |  |
| 3 | freight\_ratio | median + missing indicator | 0.2104664041173794 | raw |  | 0 | 0 |  |
| 3 | purchase\_dayofweek | median + missing indicator | 3.0 | raw |  | 0 | 0 |  |
| 3 | n\_sellers | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 3 | purchase\_month | median + missing indicator | 8.0 | raw |  | 0 | 0 |  |
| 3 | n\_products | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 3 | payment\_installments\_max | median + missing indicator | 2.0 | raw |  | 0 | 0 |  |
| 3 | n\_items | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 3 | route\_seller\_to\_customer\_state | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 0.000 |
| 3 | primary\_category | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 2.000 |
| 3 | primary\_payment\_type | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 0.000 |
| 4 | route\_recent\_carrier\_transit\_days | median + missing indicator (after log1p) | 2.0585660126414775 | log1p |  | 0 | 0 |  |
| 4 | route\_recent\_delivery\_days | median + missing indicator (after log1p) | 2.361058983165069 | log1p |  | 0 | 0 |  |
| 4 | distance\_km\_max | median + missing indicator (after log1p) | 5.896413118371149 | log1p |  | 0 | 0 |  |
| 4 | total\_freight | median + missing indicator (after log1p) | 2.8130106367386967 | log1p |  | 0 | 0 |  |
| 4 | seller\_prior\_dispatch\_days | median + missing indicator (after log1p) | 1.3549328837236616 | log1p |  | 0 | 0 |  |
| 4 | seller\_prior\_late\_handover\_days | median + missing indicator (after log1p) | 0.0522700599008528 | log1p |  | 0 | 0 |  |
| 4 | total\_weight\_g | median + missing indicator (after log1p) | 6.716594773520978 | log1p |  | 12 | 0 |  |
| 4 | total\_price | median + missing indicator (after log1p) | 4.406719247264253 | log1p |  | 0 | 0 |  |
| 4 | total\_volume\_cm3 | median + missing indicator (after log1p) | 8.987321812850125 | log1p |  | 12 | 0 |  |
| 4 | interstate\_share | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 4 | seller\_prior\_late\_handover\_rate | median + missing indicator | 0.037037037037037 | raw |  | 0 | 0 |  |
| 4 | freight\_ratio | median + missing indicator | 0.2096227867590454 | raw |  | 0 | 0 |  |
| 4 | purchase\_dayofweek | median + missing indicator | 3.0 | raw |  | 0 | 0 |  |
| 4 | n\_sellers | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 4 | purchase\_month | median + missing indicator | 8.0 | raw |  | 0 | 0 |  |
| 4 | n\_products | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 4 | payment\_installments\_max | median + missing indicator | 2.0 | raw |  | 0 | 0 |  |
| 4 | n\_items | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 4 | route\_seller\_to\_customer\_state | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 0.000 |
| 4 | primary\_category | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 0.000 |
| 4 | primary\_payment\_type | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 0.000 |
| 5 | route\_recent\_carrier\_transit\_days | median + missing indicator (after log1p) | 2.065164471033561 | log1p |  | 0 | 0 |  |
| 5 | route\_recent\_delivery\_days | median + missing indicator (after log1p) | 2.3771590817105235 | log1p |  | 0 | 0 |  |
| 5 | distance\_km\_max | median + missing indicator (after log1p) | 5.893053042566731 | log1p |  | 0 | 0 |  |
| 5 | total\_freight | median + missing indicator (after log1p) | 2.8142103969306005 | log1p |  | 0 | 0 |  |
| 5 | seller\_prior\_dispatch\_days | median + missing indicator (after log1p) | 1.359366736444718 | log1p |  | 0 | 0 |  |
| 5 | seller\_prior\_late\_handover\_days | median + missing indicator (after log1p) | 0.056907461905662295 | log1p |  | 0 | 0 |  |
| 5 | total\_weight\_g | median + missing indicator (after log1p) | 6.68586094706836 | log1p |  | 12 | 0 |  |
| 5 | total\_price | median + missing indicator (after log1p) | 4.418720118610357 | log1p |  | 0 | 0 |  |
| 5 | total\_volume\_cm3 | median + missing indicator (after log1p) | 8.980046316633132 | log1p |  | 12 | 0 |  |
| 5 | interstate\_share | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 5 | seller\_prior\_late\_handover\_rate | median + missing indicator | 0.0388349514563106 | raw |  | 0 | 0 |  |
| 5 | freight\_ratio | median + missing indicator | 0.2095158597662771 | raw |  | 0 | 0 |  |
| 5 | purchase\_dayofweek | median + missing indicator | 3.0 | raw |  | 0 | 0 |  |
| 5 | n\_sellers | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 5 | purchase\_month | median + missing indicator | 6.0 | raw |  | 0 | 0 |  |
| 5 | n\_products | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 5 | payment\_installments\_max | median + missing indicator | 2.0 | raw |  | 0 | 0 |  |
| 5 | n\_items | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 5 | route\_seller\_to\_customer\_state | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 0.000 |
| 5 | primary\_category | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 0.000 |
| 5 | primary\_payment\_type | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 0.000 |

Round 1 · ACCEPTED by the experiment lead (tag e5-B-s06-accepted) · run `20261023T162830Z` on code commit e358f81 (clean tree) · 7 checks, all PASS. Coverage and review dropdowns are on the parent tab "B6 Training"; comment on any card here.

*Card text is written by A's code, so its stage words refer to B's inputs: "s04 recipe" = B4 recipes\_B.json, "s05 folds" = B5 folds\_B.csv, "s06" = B6, "s08 decides" = B8 decides.*

**Approved solution for every card (B6–B7 blueprint):** B6 = A's s06 on B's inputs: dummy, plain linear/logistic, single tree, forest; the basic-to-complex ladder under the one-SE rule; paired gains as description; residual and classification diagnostics; learning curves. Same code, other inputs (no copy).

## B6.1

**What was done:** 4 candidates built by e5lib.factory from the s04 recipes.json (one spec per family) with the s06 settings from protocol.yaml; every pipeline fitted inside each of the 5 training folds (137,255 training rows over the folds). Learned imputation values per fold are in imputation\_by\_fold.csv, with the validation rows whose category level was unseen in the training fold (the one-hot step encodes them as all zeros).

**Check** preprocessing fitted inside the training fold only (learned medians equal the training-fold medians): PASS (15 fitted pipelines checked) **Check** every candidate uses its s04 recipe unchanged (selected features, log1p inputs, log target): PASS (selected set of 21 features) **Check** regression scored on raw days (log target inverted): PASS

**Files** (pipeline\_b/stages/b06/regression/outputs/, run 20261023T162830Z): imputation\_by\_fold.csv

## B6.2

**What was done:** Families basic to complex, validation mae mean ± SE over the folds: dummy 5.9689 ± 0.7107 days; linear/logistic 5.0247 ± 0.6115 days; single tree 5.0532 ± 0.6394 days; forest 4.9627 ± 0.6457 days. Ladder: linear/logistic kept over dummy; single tree not kept over linear/logistic; forest not kept over linear/logistic. One-SE choice over all four: linear/logistic (best mean: forest).

**Candidates** (candidates.csv):

| candidate\_id | family | validation\_mean | validation\_se | kept | reason |
| --- | --- | --- | --- | --- | --- |
| reg.sel.log.dummy\_median | dummy | 5.9689 | 0.7107 | True | baseline (simplest family) |
| reg.sel.log.linear | linear/logistic | 5.0247 | 0.6115 | True | kept: beats dummy by more than one SE |
| reg.sel.log.tree\_reg.max\_depth=5.min\_samples\_leaf=100 | single tree | 5.0532 | 0.6394 | False | not kept: within one SE of linear/logistic, the simpler family stays |
| reg.sel.log.forest\_reg.max\_depth=10.max\_features=sqrt.min\_samples\_leaf=50 | forest | 4.9627 | 0.6457 | False | not kept: within one SE of linear/logistic, the simpler family stays |

**Check** identical rows and folds for every candidate: PASS (4 candidates x 5 folds) **Check** every candidate uses its s04 recipe unchanged (selected features, log1p inputs, log target): PASS (selected set of 21 features) **Check** the simplest model of each family is present (dummy, plain linear/logistic, depth-5 tree, s06 forest): PASS

**Files** (pipeline\_b/stages/b06/regression/outputs/, run 20261023T162830Z): candidates.csv, counts.json, decision.json, paired\_differences.csv; plus 3 figure/curve files

## B6.4

**What was done:** metrics\_long.csv: training and validation scores for 4 candidates x 5 folds on every s01 metric; fit\_log.csv: rows and warnings per fit, fit times in \_manifest.json (convergence warnings: 0); predictions.csv.gz: 202,472 out-of-fold predictions.

**Check** identical rows and folds for every candidate: PASS (4 candidates x 5 folds) **Check** no test row read: every row used was purchased before the test cutoff: PASS (latest purchase 2018-05-24 18:56:59, cutoff 2018-05-27 12:30:34) **Check** regression scored on raw days (log target inverted): PASS

**Files** (pipeline\_b/stages/b06/regression/outputs/, run 20261023T162830Z): fit\_log.csv, metrics\_long.csv, predictions.csv.gz; plus 3 figure/curve files

## B6.5

**What was done:** Residual vs fitted, histogram and Q-Q plot on out-of-fold predictions of the plain linear model and the better tree model (forest). linear: residual mean 2.92, median 1.10, skewness 2.36, share above +10 days 12.22%; forest: residual mean 2.57, median 0.51, skewness 2.47, share above +10 days 11.99%.

**Files** (pipeline\_b/stages/b06/regression/outputs/, run 20261023T162830Z): predictions.csv.gz; plus 5 figure/curve files

## B6.7

**What was done:** Learning curves on fold 5: the most recent 20, 40, 60, 80 and 100% of its training rows against the same validation block (9,059 rows). Linear/logistic design matrix per training fold: fold 1 rank 130 of 130, condition number 245; fold 2 rank 138 of 138, condition number 285; fold 3 rank 139 of 139, condition number 243; fold 4 rank 140 of 140, condition number 386; fold 5 rank 140 of 140, condition number 434.

**Check** linear/logistic design matrix full rank in every training fold: PASS (fold 1 rank 130 of 130; fold 2 rank 138 of 138; fold 3 rank 139 of 139; fold 4 rank 140 of 140; fold 5 rank 140 of 140)

**Files** (pipeline\_b/stages/b06/regression/outputs/, run 20261023T162830Z): design\_matrix\_by\_fold.csv; plus 4 figure/curve files

## B6.8

**What was done:** Outputs: metrics\_long.csv, predictions.csv.gz, candidates.csv, decision.json, fit\_log.csv, imputation\_by\_fold.csv, design\_matrix\_by\_fold.csv, curves/ and figures/ with sidecar data.

**Files** (pipeline\_b/stages/b06/regression/outputs/, run 20261023T162830Z): counts.json
