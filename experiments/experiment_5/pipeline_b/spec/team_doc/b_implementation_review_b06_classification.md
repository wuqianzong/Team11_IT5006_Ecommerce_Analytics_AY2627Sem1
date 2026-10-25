# B6 › classification — evidence cards

## Supplement for decisions and the report (added 2026-10-24; DOC\_GAPS D-01, D-02)

Added after the pipeline ran, from accepted outputs only; nothing above is changed. Charts marked doc\_support come from pipeline\_b/stages/doc\_support/classification/outputs (run 20261024T065723Z, uncommitted, reads accepted outputs only). B6 figures and tables: pipeline\_b/stages/b06/classification/outputs (run 20261023T162918Z).

**Family ladder** (figures/family\_ladder.png):

&#91;image: family ladder\]

**Per-fold AP of every family, training and validation** (doc\_support b\_b06\_per\_fold\_scores.csv from b06 metrics\_long.csv; validation = selection scores):

&#91;image: per-fold scores\]

| family | phase | fold\_1 | fold\_2 | fold\_3 | fold\_4 | fold\_5 | mean | se |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dummy | train | 0.1151 | 0.1064 | 0.1071 | 0.1204 | 0.1347 | 0.1167 | 0.0052 |
| dummy | validation | 0.0982 | 0.1395 | 0.1433 | 0.2079 | 0.1010 | 0.1380 | 0.0198 |
| forest | train | 0.2694 | 0.2570 | 0.2617 | 0.3110 | 0.3346 | 0.2868 | 0.0153 |
| forest | validation | 0.1810 | 0.2859 | 0.2952 | 0.3652 | 0.2421 | 0.2739 | 0.0305 |
| linear | train | 0.2214 | 0.2067 | 0.2146 | 0.2569 | 0.2851 | 0.2369 | 0.0148 |
| linear | validation | 0.1566 | 0.2738 | 0.2762 | 0.3713 | 0.2301 | 0.2616 | 0.0349 |
| tree | train | 0.1910 | 0.1861 | 0.1970 | 0.2437 | 0.2798 | 0.2195 | 0.0182 |
| tree | validation | 0.1430 | 0.2338 | 0.2599 | 0.3575 | 0.2028 | 0.2394 | 0.0354 |

**Paired gains between rungs, fold by fold** (paired\_differences.csv; gain > 0 = the more complex model is better):

| comparison | gain\_fold\_1 | gain\_fold\_2 | gain\_fold\_3 | gain\_fold\_4 | gain\_fold\_5 | mean\_gain | paired\_se | folds\_better | kept\_by\_one\_se\_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear/logistic vs dummy | 0.0584 | 0.1342 | 0.1330 | 0.1634 | 0.1291 | 0.1236 | 0.0174 | 5 | True |
| single tree vs linear/logistic | -0.0136 | -0.0399 | -0.0163 | -0.0137 | -0.0273 | -0.0222 | 0.0051 | 0 | False |
| forest vs linear/logistic | 0.0245 | 0.0122 | 0.0190 | -0.0061 | 0.0120 | 0.0123 | 0.0052 | 4 | False |

**Learning curves** (figures/learning\_curves.png; curves/learning\_curves.csv):

&#91;image: learning curves\]

| family | share | train\_rows | train\_ap | validation\_ap |
| --- | --- | --- | --- | --- |
| dummy | 0.2000 | 9,447 | 0.1759 | 0.1010 |
| linear | 0.2000 | 9,447 | 0.3986 | 0.2183 |
| tree | 0.2000 | 9,447 | 0.3551 | 0.1658 |
| forest | 0.2000 | 9,447 | 0.4287 | 0.2230 |
| dummy | 0.4000 | 18,895 | 0.1619 | 0.1010 |
| linear | 0.4000 | 18,895 | 0.3674 | 0.2173 |
| tree | 0.4000 | 18,895 | 0.3434 | 0.2007 |
| forest | 0.4000 | 18,895 | 0.4022 | 0.2318 |
| dummy | 0.6000 | 28,342 | 0.1525 | 0.1010 |
| linear | 0.6000 | 28,342 | 0.3368 | 0.2291 |
| tree | 0.6000 | 28,342 | 0.3220 | 0.2130 |
| forest | 0.6000 | 28,342 | 0.3850 | 0.2381 |
| dummy | 0.8000 | 37,790 | 0.1390 | 0.1010 |
| linear | 0.8000 | 37,790 | 0.3066 | 0.2281 |
| tree | 0.8000 | 37,790 | 0.2999 | 0.1987 |
| forest | 0.8000 | 37,790 | 0.3556 | 0.2423 |
| dummy | 1.0000 | 47,237 | 0.1347 | 0.1010 |
| linear | 1.0000 | 47,237 | 0.2851 | 0.2301 |
| tree | 1.0000 | 47,237 | 0.2798 | 0.2028 |
| forest | 1.0000 | 47,237 | 0.3346 | 0.2421 |

**Classification diagnostics: PR, ROC and reliability per family** (figures/classification\_diagnostics.png; curves/pr\_\*, roc\_\*, reliability\_\*.csv):

&#91;image: classification diagnostics\]

**Design matrix per fold (linear/logistic)** (design\_matrix\_by\_fold.csv; full rank and condition number, see REPORT\_REQUESTS R-01):

| fold | candidate\_id | rows | encoded\_columns | duplicates\_dropped | columns | rank | full\_rank | condition\_number |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | clf.sel.log.logistic | 7,592 | 135 | missingindicator\_total\_weight\_g | 134 | 134 | True | 910.1418 |
| 2 | clf.sel.log.logistic | 17,595 | 143 | missingindicator\_total\_weight\_g | 142 | 142 | True | 912.7803 |
| 3 | clf.sel.log.logistic | 25,529 | 144 | missingindicator\_total\_weight\_g | 143 | 143 | True | 834.4698 |
| 4 | clf.sel.log.logistic | 37,140 | 145 | missingindicator\_total\_weight\_g | 144 | 144 | True | 864.5277 |
| 5 | clf.sel.log.logistic | 47,237 | 145 | missingindicator\_total\_weight\_g | 144 | 144 | True | 934.2296 |

**Imputation per fold** (imputation\_by\_fold.csv; values learned on each training fold only):

| fold | feature | rule | learned\_value | learned\_scale | route\_groups | filled\_train | filled\_validation | validation\_rows\_unseen\_level |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | route\_recent\_carrier\_transit\_days | median + missing indicator (after log1p) | 2.058662769706647 | log1p |  | 0 | 0 |  |
| 1 | route\_recent\_delivery\_days | median + missing indicator (after log1p) | 2.408964412411697 | log1p |  | 0 | 0 |  |
| 1 | seller\_prior\_dispatch\_days | median + missing indicator (after log1p) | 1.3256547611057525 | log1p |  | 0 | 0 |  |
| 1 | seller\_prior\_late\_handover\_days | median + missing indicator (after log1p) | 0.0507391560929218 | log1p |  | 0 | 0 |  |
| 1 | order\_dispatch\_days | median + missing indicator (after log1p) | 1.1244259199572957 | log1p |  | 0 | 0 |  |
| 1 | total\_freight | median + missing indicator (after log1p) | 2.8069901489571136 | log1p |  | 0 | 0 |  |
| 1 | total\_volume\_cm3 | median + missing indicator (after log1p) | 8.979542601725113 | log1p |  | 8 | 4 |  |
| 1 | total\_price | median + missing indicator (after log1p) | 4.394202210604015 | log1p |  | 0 | 0 |  |
| 1 | order\_handover\_late\_days | median + missing indicator (after log1p) | 0.0 | log1p |  | 0 | 0 |  |
| 1 | total\_weight\_g | median + missing indicator (after log1p) | 6.68586094706836 | log1p |  | 8 | 4 |  |
| 1 | product\_description\_lenght | median + missing indicator (after log1p) | 6.338594078203183 | log1p |  | 175 | 152 |  |
| 1 | distance\_km\_max | median + missing indicator (after log1p) | 5.9139816517329935 | log1p |  | 0 | 0 |  |
| 1 | seller\_prior\_review\_mean | median + missing indicator | 4.24 | raw |  | 817 | 534 |  |
| 1 | freight\_ratio | median + missing indicator | 0.2103448275862068 | raw |  | 0 | 0 |  |
| 1 | n\_items | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 1 | seller\_prior\_late\_handover\_rate | median + missing indicator | 0.0416666666666666 | raw |  | 0 | 0 |  |
| 1 | n\_products | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 1 | n\_sellers | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 1 | purchase\_month | median + missing indicator | 4.0 | raw |  | 0 | 0 |  |
| 1 | order\_handed\_over\_late | median + missing indicator | 0.0 | raw |  | 0 | 0 |  |
| 1 | interstate\_share | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 1 | n\_categories | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 1 | payment\_installments\_max | median + missing indicator | 2.0 | raw |  | 0 | 0 |  |
| 1 | route\_seller\_to\_customer\_state | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 9.000 |
| 1 | primary\_category | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 62.000 |
| 2 | route\_recent\_carrier\_transit\_days | median + missing indicator (after log1p) | 2.0585660126414775 | log1p |  | 0 | 0 |  |
| 2 | route\_recent\_delivery\_days | median + missing indicator (after log1p) | 2.374238111422271 | log1p |  | 0 | 0 |  |
| 2 | seller\_prior\_dispatch\_days | median + missing indicator (after log1p) | 1.33319632024829 | log1p |  | 0 | 0 |  |
| 2 | seller\_prior\_late\_handover\_days | median + missing indicator (after log1p) | 0.04886305899565808 | log1p |  | 0 | 0 |  |
| 2 | order\_dispatch\_days | median + missing indicator (after log1p) | 1.1601116185928924 | log1p |  | 0 | 0 |  |
| 2 | total\_freight | median + missing indicator (after log1p) | 2.808800104202353 | log1p |  | 0 | 0 |  |
| 2 | total\_volume\_cm3 | median + missing indicator (after log1p) | 8.987321812850125 | log1p |  | 11 | 0 |  |
| 2 | total\_price | median + missing indicator (after log1p) | 4.393213824064446 | log1p |  | 0 | 0 |  |
| 2 | order\_handover\_late\_days | median + missing indicator (after log1p) | 0.0 | log1p |  | 0 | 0 |  |
| 2 | total\_weight\_g | median + missing indicator (after log1p) | 6.7464121285733745 | log1p |  | 11 | 0 |  |
| 2 | product\_description\_lenght | median + missing indicator (after log1p) | 6.331501849893691 | log1p |  | 336 | 137 |  |
| 2 | distance\_km\_max | median + missing indicator (after log1p) | 5.904488144868549 | log1p |  | 0 | 0 |  |
| 2 | seller\_prior\_review\_mean | median + missing indicator | 4.221009079416159 | raw |  | 1,323 | 507 |  |
| 2 | freight\_ratio | median + missing indicator | 0.2126269956458635 | raw |  | 0 | 0 |  |
| 2 | n\_items | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 2 | seller\_prior\_late\_handover\_rate | median + missing indicator | 0.0357142857142857 | raw |  | 0 | 0 |  |
| 2 | n\_products | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 2 | n\_sellers | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 2 | purchase\_month | median + missing indicator | 6.0 | raw |  | 0 | 0 |  |
| 2 | order\_handed\_over\_late | median + missing indicator | 0.0 | raw |  | 0 | 0 |  |
| 2 | interstate\_share | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 2 | n\_categories | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 2 | payment\_installments\_max | median + missing indicator | 2.0 | raw |  | 0 | 0 |  |
| 2 | route\_seller\_to\_customer\_state | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 0.000 |
| 2 | primary\_category | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 6.000 |
| 3 | route\_recent\_carrier\_transit\_days | median + missing indicator (after log1p) | 2.0402250646286935 | log1p |  | 0 | 0 |  |
| 3 | route\_recent\_delivery\_days | median + missing indicator (after log1p) | 2.3577298585049467 | log1p |  | 0 | 0 |  |
| 3 | seller\_prior\_dispatch\_days | median + missing indicator (after log1p) | 1.3372370402566485 | log1p |  | 0 | 0 |  |
| 3 | seller\_prior\_late\_handover\_days | median + missing indicator (after log1p) | 0.04621686047083749 | log1p |  | 0 | 0 |  |
| 3 | order\_dispatch\_days | median + missing indicator (after log1p) | 1.1805477907701138 | log1p |  | 0 | 0 |  |
| 3 | total\_freight | median + missing indicator (after log1p) | 2.8142103969306005 | log1p |  | 0 | 0 |  |
| 3 | total\_volume\_cm3 | median + missing indicator (after log1p) | 8.987321812850125 | log1p |  | 12 | 0 |  |
| 3 | total\_price | median + missing indicator (after log1p) | 4.393213824064446 | log1p |  | 0 | 0 |  |
| 3 | order\_handover\_late\_days | median + missing indicator (after log1p) | 0.0 | log1p |  | 0 | 0 |  |
| 3 | total\_weight\_g | median + missing indicator (after log1p) | 6.732210706467206 | log1p |  | 12 | 0 |  |
| 3 | product\_description\_lenght | median + missing indicator (after log1p) | 6.349138991379798 | log1p |  | 444 | 253 |  |
| 3 | distance\_km\_max | median + missing indicator (after log1p) | 5.906390590524521 | log1p |  | 0 | 0 |  |
| 3 | seller\_prior\_review\_mean | median + missing indicator | 4.232558139534884 | raw |  | 1,760 | 382 |  |
| 3 | freight\_ratio | median + missing indicator | 0.2121552604698671 | raw |  | 0 | 0 |  |
| 3 | n\_items | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 3 | seller\_prior\_late\_handover\_rate | median + missing indicator | 0.0344827586206896 | raw |  | 0 | 0 |  |
| 3 | n\_products | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 3 | n\_sellers | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 3 | purchase\_month | median + missing indicator | 7.0 | raw |  | 0 | 0 |  |
| 3 | order\_handed\_over\_late | median + missing indicator | 0.0 | raw |  | 0 | 0 |  |
| 3 | interstate\_share | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 3 | n\_categories | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 3 | payment\_installments\_max | median + missing indicator | 2.0 | raw |  | 0 | 0 |  |
| 3 | route\_seller\_to\_customer\_state | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 0.000 |
| 3 | primary\_category | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 2.000 |
| 4 | route\_recent\_carrier\_transit\_days | median + missing indicator (after log1p) | 2.0585660126414775 | log1p |  | 0 | 0 |  |
| 4 | route\_recent\_delivery\_days | median + missing indicator (after log1p) | 2.370762331016513 | log1p |  | 0 | 0 |  |
| 4 | seller\_prior\_dispatch\_days | median + missing indicator (after log1p) | 1.3549328837236616 | log1p |  | 0 | 0 |  |
| 4 | seller\_prior\_late\_handover\_days | median + missing indicator (after log1p) | 0.05153564299660608 | log1p |  | 0 | 0 |  |
| 4 | order\_dispatch\_days | median + missing indicator (after log1p) | 1.2326581129020893 | log1p |  | 0 | 0 |  |
| 4 | total\_freight | median + missing indicator (after log1p) | 2.8130106367386967 | log1p |  | 0 | 0 |  |
| 4 | total\_volume\_cm3 | median + missing indicator (after log1p) | 8.987321812850125 | log1p |  | 12 | 0 |  |
| 4 | total\_price | median + missing indicator (after log1p) | 4.394449154672439 | log1p |  | 0 | 0 |  |
| 4 | order\_handover\_late\_days | median + missing indicator (after log1p) | 0.0 | log1p |  | 0 | 0 |  |
| 4 | total\_weight\_g | median + missing indicator (after log1p) | 6.698268054115413 | log1p |  | 12 | 0 |  |
| 4 | product\_description\_lenght | median + missing indicator (after log1p) | 6.352629396319567 | log1p |  | 691 | 174 |  |
| 4 | distance\_km\_max | median + missing indicator (after log1p) | 5.898108877729477 | log1p |  | 0 | 0 |  |
| 4 | seller\_prior\_review\_mean | median + missing indicator | 4.232558139534884 | raw |  | 2,147 | 371 |  |
| 4 | freight\_ratio | median + missing indicator | 0.2101512689086135 | raw |  | 0 | 0 |  |
| 4 | n\_items | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 4 | seller\_prior\_late\_handover\_rate | median + missing indicator | 0.037037037037037 | raw |  | 0 | 0 |  |
| 4 | n\_products | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 4 | n\_sellers | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 4 | purchase\_month | median + missing indicator | 8.0 | raw |  | 0 | 0 |  |
| 4 | order\_handed\_over\_late | median + missing indicator | 0.0 | raw |  | 0 | 0 |  |
| 4 | interstate\_share | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 4 | n\_categories | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 4 | payment\_installments\_max | median + missing indicator | 2.0 | raw |  | 0 | 0 |  |
| 4 | route\_seller\_to\_customer\_state | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 0.000 |
| 4 | primary\_category | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 0.000 |
| 5 | route\_recent\_carrier\_transit\_days | median + missing indicator (after log1p) | 2.07376632453799 | log1p |  | 0 | 0 |  |
| 5 | route\_recent\_delivery\_days | median + missing indicator (after log1p) | 2.3893374785972212 | log1p |  | 0 | 0 |  |
| 5 | seller\_prior\_dispatch\_days | median + missing indicator (after log1p) | 1.3591485128189609 | log1p |  | 0 | 0 |  |
| 5 | seller\_prior\_late\_handover\_days | median + missing indicator (after log1p) | 0.05629013037984402 | log1p |  | 0 | 0 |  |
| 5 | order\_dispatch\_days | median + missing indicator (after log1p) | 1.2319830781188552 | log1p |  | 0 | 18 |  |
| 5 | total\_freight | median + missing indicator (after log1p) | 2.8142103969306005 | log1p |  | 0 | 0 |  |
| 5 | total\_volume\_cm3 | median + missing indicator (after log1p) | 8.97727273946428 | log1p |  | 12 | 0 |  |
| 5 | total\_price | median + missing indicator (after log1p) | 4.414735809083586 | log1p |  | 0 | 0 |  |
| 5 | order\_handover\_late\_days | median + missing indicator (after log1p) | 0.0 | log1p |  | 0 | 0 |  |
| 5 | total\_weight\_g | median + missing indicator (after log1p) | 6.68586094706836 | log1p |  | 12 | 0 |  |
| 5 | product\_description\_lenght | median + missing indicator (after log1p) | 6.363028103540465 | log1p |  | 875 | 73 |  |
| 5 | distance\_km\_max | median + missing indicator (after log1p) | 5.897626840832933 | log1p |  | 0 | 0 |  |
| 5 | seller\_prior\_review\_mean | median + missing indicator | 4.217391304347826 | raw |  | 2,566 | 494 |  |
| 5 | freight\_ratio | median + missing indicator | 0.209728183118741 | raw |  | 0 | 0 |  |
| 5 | n\_items | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 5 | seller\_prior\_late\_handover\_rate | median + missing indicator | 0.0386363636363636 | raw |  | 0 | 0 |  |
| 5 | n\_products | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 5 | n\_sellers | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 5 | purchase\_month | median + missing indicator | 7.0 | raw |  | 0 | 0 |  |
| 5 | order\_handed\_over\_late | median + missing indicator | 0.0 | raw |  | 0 | 0 |  |
| 5 | interstate\_share | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 5 | n\_categories | median + missing indicator | 1.0 | raw |  | 0 | 0 |  |
| 5 | payment\_installments\_max | median + missing indicator | 2.0 | raw |  | 0 | 0 |  |
| 5 | route\_seller\_to\_customer\_state | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 0.000 |
| 5 | primary\_category | missing -> 'Unknown' level | Unknown | category |  | 0 | 0 | 0.000 |

Round 1 · ACCEPTED by the experiment lead (tag e5-B-s06-accepted) · run `20261023T162918Z` on code commit e358f81 (clean tree) · 6 checks, all PASS. Coverage and review dropdowns are on the parent tab "B6 Training"; comment on any card here.

*Card text is written by A's code, so its stage words refer to B's inputs: "s04 recipe" = B4 recipes\_B.json, "s05 folds" = B5 folds\_B.csv, "s06" = B6, "s08 decides" = B8 decides.*

**Approved solution for every card (B6–B7 blueprint):** B6 = A's s06 on B's inputs: dummy, plain linear/logistic, single tree, forest; the basic-to-complex ladder under the one-SE rule; paired gains as description; residual and classification diagnostics; learning curves. Same code, other inputs (no copy).

## B6.1

**What was done:** 4 candidates built by e5lib.factory from the s04 recipes.json (one spec per family) with the s06 settings from protocol.yaml; every pipeline fitted inside each of the 5 training folds (135,093 training rows over the folds). Learned imputation values per fold are in imputation\_by\_fold.csv, with the validation rows whose category level was unseen in the training fold (the one-hot step encodes them as all zeros).

**Check** preprocessing fitted inside the training fold only (learned medians equal the training-fold medians): PASS (15 fitted pipelines checked) **Check** every candidate uses its s04 recipe unchanged (selected features, log1p inputs): PASS (selected set of 25 features)

**Files** (pipeline\_b/stages/b06/classification/outputs/, run 20261023T162918Z): imputation\_by\_fold.csv

## B6.2

**What was done:** Families basic to complex, validation ap mean ± SE over the folds: dummy 0.1380 ± 0.0198; linear/logistic 0.2616 ± 0.0349; single tree 0.2394 ± 0.0354; forest 0.2739 ± 0.0305. Ladder: linear/logistic kept over dummy; single tree not kept over linear/logistic; forest not kept over linear/logistic. One-SE choice over all four: linear/logistic (best mean: forest).

**Candidates** (candidates.csv):

| candidate\_id | family | validation\_mean | validation\_se | kept | reason |
| --- | --- | --- | --- | --- | --- |
| clf.sel.log.dummy\_prior | dummy | 0.1380 | 0.0198 | True | baseline (simplest family) |
| clf.sel.log.logistic | linear/logistic | 0.2616 | 0.0349 | True | kept: beats dummy by more than one SE |
| clf.sel.log.tree\_clf.max\_depth=5.min\_samples\_leaf=100 | single tree | 0.2394 | 0.0354 | False | not kept: within one SE of linear/logistic, the simpler family stays |
| clf.sel.log.forest\_clf.max\_depth=10.max\_features=sqrt.min\_samples\_leaf=50 | forest | 0.2739 | 0.0305 | False | not kept: within one SE of linear/logistic, the simpler family stays |

**Check** identical rows and folds for every candidate: PASS (4 candidates x 5 folds) **Check** every candidate uses its s04 recipe unchanged (selected features, log1p inputs): PASS (selected set of 25 features) **Check** the simplest model of each family is present (dummy, plain linear/logistic, depth-5 tree, s06 forest): PASS

**Files** (pipeline\_b/stages/b06/classification/outputs/, run 20261023T162918Z): candidates.csv, counts.json, decision.json, paired\_differences.csv; plus 3 figure/curve files

## B6.4

**What was done:** metrics\_long.csv: training and validation scores for 4 candidates x 5 folds on every s01 metric (threshold metrics at 0.5 and 1/6); fit\_log.csv: rows and warnings per fit, fit times in \_manifest.json (convergence warnings: 0); predictions.csv.gz: 200,860 out-of-fold predictions.

**Check** identical rows and folds for every candidate: PASS (4 candidates x 5 folds) **Check** no test row read: every row used was purchased before the test cutoff: PASS (latest purchase 2018-05-23 11:29:51, cutoff 2018-05-26 12:16:34)

**Files** (pipeline\_b/stages/b06/classification/outputs/, run 20261023T162918Z): fit\_log.csv, metrics\_long.csv, predictions.csv.gz; plus 3 figure/curve files

## B6.6

**What was done:** Pooled out-of-fold PR, ROC and reliability curves for every family, Brier score, and the predicted-probability histogram per class for the best non-dummy family. dummy: AP 0.1406, ROC-AUC 0.5012, Brier 0.1207; linear/logistic: AP 0.2587, ROC-AUC 0.6531, Brier 0.1152; single tree: AP 0.2556, ROC-AUC 0.6444, Brier 0.1144; forest: AP 0.2684, ROC-AUC 0.6642, Brier 0.1150.

**Files** (pipeline\_b/stages/b06/classification/outputs/, run 20261023T162918Z): oof\_diagnostics.csv, predictions.csv.gz; plus 15 figure/curve files

## B6.7

**What was done:** Learning curves on fold 5: the most recent 20, 40, 60, 80 and 100% of its training rows against the same validation block (8,646 rows). Linear/logistic design matrix per training fold: fold 1 rank 134 of 134, condition number 910; fold 2 rank 142 of 142, condition number 913; fold 3 rank 143 of 143, condition number 834; fold 4 rank 144 of 144, condition number 865; fold 5 rank 144 of 144, condition number 934.

**Check** linear/logistic design matrix full rank in every training fold: PASS (fold 1 rank 134 of 134; fold 2 rank 142 of 142; fold 3 rank 143 of 143; fold 4 rank 144 of 144; fold 5 rank 144 of 144)

**Files** (pipeline\_b/stages/b06/classification/outputs/, run 20261023T162918Z): design\_matrix\_by\_fold.csv; plus 4 figure/curve files

## B6.8

**What was done:** Outputs: metrics\_long.csv, predictions.csv.gz, candidates.csv, decision.json, fit\_log.csv, imputation\_by\_fold.csv, design\_matrix\_by\_fold.csv, curves/ and figures/ with sidecar data.

**Files** (pipeline\_b/stages/b06/classification/outputs/, run 20261023T162918Z): counts.json
