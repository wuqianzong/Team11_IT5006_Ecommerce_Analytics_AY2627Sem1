# s07 Tuning › regression — evidence cards

Round 2 (accepted) · run `20261021T042137Z` · 6 checks, all PASS. Round 2 differs from round 1 only in the validation-curve figures (dashed training lines now in their series colour); every table and value is unchanged. Coverage and review dropdowns are on the parent tab "s07 Tuning"; comment on any card here.

## 7.1 Linear (regression)

**Approved solution:** Ridge(alpha): 0.01, 0.1, 0.5, 1, 5, 10, 20, 50, 100

**What was done:** linear/logistic: 9 configurations; best mean 5.4620 days ({'alpha': 20.0}); one-SE choice {"alpha": 100.0} with 5.4642 ± 0.6711 days.

**Observation:** Against the plain s06 model (5.4701 days): paired gain of the tuned model +0.0059 days (paired SE 0.0056), better in 4 of 5 folds; carried: plain model. For description only, the best-mean grid point against the plain model: paired gain +0.0081 days (paired SE 0.0035), better in 4 of 5 folds.

**Reasoning:** The tuned configuration replaces the plain s06 model only if it beats it by more than one standard error of the fold means (G-55); otherwise the simpler plain model stays.

**Top 8 configurations by validation MAE, plus the one-SE choice** (grid\_results.csv; 9 configurations (days)):

| params | train\_mean | validation\_mean | validation\_se | train\_validation\_gap | rank | chosen\_in\_family |
| --- | --- | --- | --- | --- | --- | --- |
| {"alpha": 20.0} | 4.2917 | 5.4620 | 0.6728 | 1.1703 | 1 | False |
| {"alpha": 50.0} | 4.2954 | 5.4621 | 0.6720 | 1.1667 | 2 | False |
| {"alpha": 10.0} | 4.2903 | 5.4627 | 0.6731 | 1.1725 | 3 | False |
| {"alpha": 5.0} | 4.2894 | 5.4637 | 0.6731 | 1.1743 | 4 | False |
| {"alpha": 100.0} | 4.3009 | 5.4642 | 0.6711 | 1.1633 | 5 | True |
| {"alpha": 1.0} | 4.2882 | 5.4656 | 0.6729 | 1.1774 | 6 | False |
| {"alpha": 0.5} | 4.2878 | 5.4663 | 0.6728 | 1.1785 | 7 | False |
| {"alpha": 0.1} | 4.2866 | 5.4679 | 0.6729 | 1.1813 | 8 | False |

**Against the plain s06 model** (plain\_vs\_tuned.csv; paired figures are description only):

| plain\_mean | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | paired\_se | tuned\_better\_folds | carried | best\_mean | paired\_gain\_of\_best\_mean | best\_mean\_paired\_se | best\_mean\_better\_folds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5.4701 | 5.4642 | 0.6711 | 0.0059 | 0.0056 | 4 | plain | 5.4620 | 0.0081 | 0.0035 | 4 |

&#91;image: Validation curve, linear/logistic, regression\]

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 9 configurations; single tree 36 configurations; forest 24 configurations)

**Files** (stages/s07\_tuning/regression/outputs/, run 20261021T035843Z): grid\_results.csv

## 7.3 Decision tree

**Approved solution:** max\_depth: 4, 5, 6, 8, 10, 12, 14, 16, 18 (includes the s06 depth 5; G-43); min\_samples\_leaf: 20, 50, 100, 200; classifier also class\_weight: None, balanced

**What was done:** single tree: 36 configurations; best mean 5.3760 days ({'max\_depth': 8, 'min\_samples\_leaf': 200}); one-SE choice {"max\_depth": 4, "min\_samples\_leaf": 200} with 5.4332 ± 0.7125 days.

**Observation:** Against the plain s06 model (5.4244 days): paired gain of the tuned model -0.0088 days (paired SE 0.0359), better in 1 of 5 folds; carried: plain model. For description only, the best-mean grid point against the plain model: paired gain +0.0483 days (paired SE 0.0239), better in 4 of 5 folds.

**Reasoning:** The tuned configuration replaces the plain s06 model only if it beats it by more than one standard error of the fold means (G-55); otherwise the simpler plain model stays.

**Top 8 configurations by validation MAE, plus the one-SE choice** (grid\_results.csv; 36 configurations (days)):

| params | train\_mean | validation\_mean | validation\_se | train\_validation\_gap | rank | chosen\_in\_family |
| --- | --- | --- | --- | --- | --- | --- |
| {"max\_depth": 8, "min\_samples\_leaf": 200} | 4.2917 | 5.3760 | 0.7055 | 1.0843 | 1 | False |
| {"max\_depth": 18, "min\_samples\_leaf": 200} | 4.2607 | 5.3820 | 0.7091 | 1.1213 | 2 | False |
| {"max\_depth": 14, "min\_samples\_leaf": 200} | 4.2613 | 5.3823 | 0.7090 | 1.1211 | 3 | False |
| {"max\_depth": 16, "min\_samples\_leaf": 200} | 4.2608 | 5.3826 | 0.7085 | 1.1218 | 4 | False |
| {"max\_depth": 8, "min\_samples\_leaf": 100} | 4.2564 | 5.3827 | 0.7089 | 1.1263 | 5 | False |
| {"max\_depth": 10, "min\_samples\_leaf": 200} | 4.2744 | 5.3834 | 0.7036 | 1.1090 | 6 | False |
| {"max\_depth": 12, "min\_samples\_leaf": 200} | 4.2652 | 5.3855 | 0.7049 | 1.1204 | 7 | False |
| {"max\_depth": 10, "min\_samples\_leaf": 100} | 4.2192 | 5.3905 | 0.7061 | 1.1713 | 8 | False |
| {"max\_depth": 4, "min\_samples\_leaf": 200} | 4.4140 | 5.4332 | 0.7125 | 1.0192 | 27 | True |

**Against the plain s06 model** (plain\_vs\_tuned.csv; paired figures are description only):

| plain\_mean | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | paired\_se | tuned\_better\_folds | carried | best\_mean | paired\_gain\_of\_best\_mean | best\_mean\_paired\_se | best\_mean\_better\_folds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5.4244 | 5.4332 | 0.7125 | -0.0088 | 0.0359 | 1 | plain | 5.3760 | 0.0483 | 0.0239 | 4 |

&#91;image: Validation curve, single tree, regression\]

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 9 configurations; single tree 36 configurations; forest 24 configurations) **Check** the grid point with the s06 plain settings reproduces the s06 fold scores (tree, forest): PASS (2 of 2 reproduced)

**Files** (stages/s07\_tuning/regression/outputs/, run 20261021T035843Z): grid\_results.csv

## 7.4 Random forest

**Approved solution:** 200 trees; max\_depth: 8, 10, 12, 14, 16, 18; min\_samples\_leaf: 20, 50, 100, 200 (forest grid unchanged by G-43); max\_features: sqrt; classifier also class\_weight: None, balanced

**What was done:** forest: 24 configurations; best mean 5.3541 days ({'max\_depth': 18, 'max\_features': 'sqrt', 'min\_samples\_leaf': 20}); one-SE choice {"max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 200} with 5.5772 ± 0.6758 days.

**Observation:** Against the plain s06 model (5.4434 days): paired gain of the tuned model -0.1338 days (paired SE 0.0150), better in 0 of 5 folds; carried: plain model. For description only, the best-mean grid point against the plain model: paired gain +0.0893 days (paired SE 0.0186), better in 5 of 5 folds.

**Reasoning:** The tuned configuration replaces the plain s06 model only if it beats it by more than one standard error of the fold means (G-55); otherwise the simpler plain model stays.

**Top 8 configurations by validation MAE, plus the one-SE choice** (grid\_results.csv; 24 configurations (days)):

| params | train\_mean | validation\_mean | validation\_se | train\_validation\_gap | rank | chosen\_in\_family |
| --- | --- | --- | --- | --- | --- | --- |
| {"max\_depth": 18, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 4.1778 | 5.3541 | 0.6936 | 1.1763 | 1 | False |
| {"max\_depth": 16, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 4.1988 | 5.3629 | 0.6912 | 1.1641 | 2 | False |
| {"max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 4.2257 | 5.3777 | 0.6914 | 1.1520 | 3 | False |
| {"max\_depth": 12, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 4.2677 | 5.3871 | 0.6890 | 1.1194 | 4 | False |
| {"max\_depth": 18, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 4.2776 | 5.4025 | 0.6892 | 1.1249 | 5 | False |
| {"max\_depth": 16, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 4.2859 | 5.4044 | 0.6880 | 1.1185 | 6 | False |
| {"max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 4.2995 | 5.4138 | 0.6848 | 1.1144 | 7 | False |
| {"max\_depth": 12, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 4.3217 | 5.4204 | 0.6854 | 1.0987 | 8 | False |
| {"max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 4.5009 | 5.5772 | 0.6758 | 1.0763 | 24 | True |

**Against the plain s06 model** (plain\_vs\_tuned.csv; paired figures are description only):

| plain\_mean | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | paired\_se | tuned\_better\_folds | carried | best\_mean | paired\_gain\_of\_best\_mean | best\_mean\_paired\_se | best\_mean\_better\_folds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5.4434 | 5.5772 | 0.6758 | -0.1338 | 0.0150 | 0 | plain | 5.3541 | 0.0893 | 0.0186 | 5 |

&#91;image: Validation curve, forest, regression\]

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 9 configurations; single tree 36 configurations; forest 24 configurations) **Check** the grid point with the s06 plain settings reproduces the s06 fold scores (tree, forest): PASS (2 of 2 reproduced)

**Files** (stages/s07\_tuning/regression/outputs/, run 20261021T035843Z): grid\_results.csv

## 7.5 Search method

**Approved solution:** GridSearchCV over the full Pipeline with cv = the s05 fold iterator, scoring = the primary metric (neg MAE, average precision), refit=False, return\_train\_score=True, seed 42. Best per family = the simplest configuration within one standard error of the best mean (s01 1.7). Simpler means higher alpha, lower C, shallower depth, then larger leaf. It is then compared with the family's plain s06 model by the same one-SE rule: if the plain model's mean is within one SE of the tuned configuration's mean, the plain model is kept (G-55)

**What was done:** GridSearchCV over the whole s04 pipeline on the s05 folds, scoring neg\_mean\_absolute\_error, refit=False, return\_train\_score=True, seed 42; 69 configurations in total. Carried per family: linear/logistic plain s06; single tree plain s06; forest plain s06. Ladder over the carried families (description only; s08 decides): linear/logistic kept over dummy (paired gain +1.0245 days, better in 5 of 5 folds); single tree not kept over linear/logistic (paired gain +0.0458 days, better in 3 of 5 folds); forest not kept over linear/logistic (paired gain +0.0267 days, better in 3 of 5 folds); result linear/logistic.

**Conclusion:** Selection scores on the folds, not generalisation estimates (G-10). The finalists and the final choice are made in s08 at its gate (G-39).

**Plain vs tuned per family** (plain\_vs\_tuned.csv):

| family | plain\_mean | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | tuned\_better\_folds | carried |
| --- | --- | --- | --- | --- | --- | --- |
| linear/logistic | 5.4701 | 5.4642 | 0.6711 | 0.0059 | 4 | plain |
| single tree | 5.4244 | 5.4332 | 0.7125 | -0.0088 | 1 | plain |
| forest | 5.4434 | 5.5772 | 0.6758 | -0.1338 | 0 | plain |

**Ladder over the carried families** (ladder\_preview.csv; description only, s08 chooses):

| comparison | mean\_gain | paired\_se | folds\_better | kept\_by\_one\_se\_rule |
| --- | --- | --- | --- | --- |
| linear/logistic vs dummy | 1.0245 | 0.1262 | 5 | True |
| single tree vs linear/logistic | 0.0458 | 0.0685 | 3 | False |
| forest vs linear/logistic | 0.0267 | 0.0601 | 3 | False |

**Check** same folds as s06 (rows per fold equal): PASS **Check** every configuration scored on all five folds, whole pipeline refitted per fold: PASS **Check** no test row read: every row used was purchased before the test cutoff: PASS (latest purchase 2018-05-27 12:20:21, cutoff 2018-05-27 12:30:34)

**Files** (stages/s07\_tuning/regression/outputs/, run 20261021T035843Z): candidates.csv, counts.json, decision.json, grid\_results.csv, ladder\_preview.csv, plain\_vs\_tuned.csv

## 7.6 Overfitting check

**Approved solution:** For each configuration report the train–validation gap; flag the best configuration if the gap is large and a simpler one is within the decision rule

**What was done:** train\_validation\_gap for every configuration in grid\_results.csv (positive = worse on validation). Gap of each family's one-SE choice: linear/logistic +1.1633 days; single tree +1.0192 days; forest +1.0763 days.

**Reasoning:** The one-SE choice is already the simplest configuration within the rule, so no simpler configuration within the rule exists to flag; the gaps are reported for the review.

**Gap of each family's one-SE choice** (grid\_results.csv):

| family | params | train\_mean | validation\_mean | train\_validation\_gap |
| --- | --- | --- | --- | --- |
| linear | {"alpha": 100.0} | 4.3009 | 5.4642 | 1.1633 |
| tree | {"max\_depth": 4, "min\_samples\_leaf": 200} | 4.4140 | 5.4332 | 1.0192 |
| forest | {"max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 4.5009 | 5.5772 | 1.0763 |

**Files** (stages/s07\_tuning/regression/outputs/, run 20261021T035843Z): curves/validation\_curve\_forest.csv, curves/validation\_curve\_linear.csv, curves/validation\_curve\_tree.csv, figures/validation\_curve\_forest.csv, figures/validation\_curve\_forest.png, figures/validation\_curve\_linear.csv, figures/validation\_curve\_linear.png, figures/validation\_curve\_tree.csv, figures/validation\_curve\_tree.png, grid\_results.csv

## 7.7 Outputs

**Approved solution:** grid\_results.csv (every configuration: parameters, per-fold train and validation scores, mean, SD, rank, fit time, convergence), out-of-fold predictions of each family's best, kept separate as pooled OOF vs mean-fold scores

**What was done:** grid\_results.csv, plain\_vs\_tuned.csv, ladder\_preview.csv, candidates.csv, decision.json, out-of-fold predictions of each family's best (predictions.csv.gz) with pooled vs mean-fold scores (oof\_scores.csv), validation curves (curves/, figures/); fit times in \_manifest.json.

**Out-of-fold scores of each family's one-SE choice, pooled vs mean-fold** (oof\_scores.csv):

| family | mean\_fold\_mae | pooled\_oof\_mae | pooled\_oof\_rmse | pooled\_oof\_r2 |
| --- | --- | --- | --- | --- |
| linear/logistic | 5.4642 | 5.5184 | 9.0018 | 0.0958 |
| single tree | 5.4332 | 5.4922 | 8.9775 | 0.1007 |
| forest | 5.5772 | 5.6331 | 9.1207 | 0.0717 |

**Check** refitting each family's best per fold gives the grid's validation scores: PASS (15 refits)

**Files** (stages/s07\_tuning/regression/outputs/, run 20261021T035843Z): counts.json, oof\_scores.csv, predictions.csv.gz
