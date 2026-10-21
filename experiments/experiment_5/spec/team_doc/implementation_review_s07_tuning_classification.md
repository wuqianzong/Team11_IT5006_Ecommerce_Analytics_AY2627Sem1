# s07 Tuning › classification — evidence cards

Round 2 (accepted) · run `20261021T042900Z` · 6 checks, all PASS. Round 2 differs from round 1 only in the validation-curve figures (dashed training lines now in their series colour); every table and value is unchanged. Coverage and review dropdowns are on the parent tab "s07 Tuning"; comment on any card here.

## 7.2 Logistic (classification)

**Approved solution:** LogisticRegression(C) with L2: 0.01, 0.1, 0.5, 1, 5, 10, 20, 50, 100; class\_weight: None, balanced

**What was done:** linear/logistic: 18 configurations; best mean 0.2553 ({'C': 0.01, 'class\_weight': None}); one-SE choice {"C": 0.01, "class\_weight": null} with 0.2553 ± 0.0294.

**Observation:** Against the plain s06 model (0.2435): paired gain of the tuned model +0.0118 (paired SE 0.0045), better in 5 of 5 folds; carried: plain model. For description only, the best-mean grid point against the plain model: paired gain +0.0118 (paired SE 0.0045), better in 5 of 5 folds.

**Reasoning:** The tuned configuration replaces the plain s06 model only if it beats it by more than one standard error of the fold means (G-55); otherwise the simpler plain model stays.

**Top 8 configurations by validation AP, plus the one-SE choice** (grid\_results.csv; 18 configurations):

| params | train\_mean | validation\_mean | validation\_se | train\_validation\_gap | rank | chosen\_in\_family |
| --- | --- | --- | --- | --- | --- | --- |
| {"C": 0.01, "class\_weight": null} | 0.2113 | 0.2553 | 0.0294 | -0.0440 | 1 | True |
| {"C": 0.01, "class\_weight": "balanced"} | 0.2122 | 0.2532 | 0.0296 | -0.0410 | 2 | False |
| {"C": 0.1, "class\_weight": null} | 0.2167 | 0.2506 | 0.0305 | -0.0339 | 3 | False |
| {"C": 0.1, "class\_weight": "balanced"} | 0.2162 | 0.2492 | 0.0302 | -0.0330 | 4 | False |
| {"C": 0.5, "class\_weight": null} | 0.2190 | 0.2481 | 0.0308 | -0.0292 | 5 | False |
| {"C": 1.0, "class\_weight": null} | 0.2196 | 0.2470 | 0.0310 | -0.0273 | 6 | False |
| {"C": 0.5, "class\_weight": "balanced"} | 0.2177 | 0.2466 | 0.0304 | -0.0288 | 7 | False |
| {"C": 1.0, "class\_weight": "balanced"} | 0.2182 | 0.2456 | 0.0304 | -0.0274 | 8 | False |

**Against the plain s06 model** (plain\_vs\_tuned.csv; paired figures are description only):

| plain\_mean | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | paired\_se | tuned\_better\_folds | carried | best\_mean | paired\_gain\_of\_best\_mean | best\_mean\_paired\_se | best\_mean\_better\_folds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.2435 | 0.2553 | 0.0294 | 0.0118 | 0.0045 | 5 | plain | 0.2553 | 0.0118 | 0.0045 | 5 |

&#91;image: Validation curve, linear/logistic, classification\]

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 18 configurations; single tree 72 configurations; forest 48 configurations)

**Files** (stages/s07\_tuning/classification/outputs/, run 20261021T040619Z): grid\_results.csv

## 7.3 Decision tree

**Approved solution:** max\_depth: 4, 5, 6, 8, 10, 12, 14, 16, 18 (includes the s06 depth 5; G-43); min\_samples\_leaf: 20, 50, 100, 200; classifier also class\_weight: None, balanced

**What was done:** single tree: 72 configurations; best mean 0.2216 ({'class\_weight': None, 'max\_depth': 10, 'min\_samples\_leaf': 200}); one-SE choice {"class\_weight": null, "max\_depth": 4, "min\_samples\_leaf": 200} with 0.2134 ± 0.0217.

**Observation:** Against the plain s06 model (0.2158): paired gain of the tuned model -0.0024 (paired SE 0.0022), better in 2 of 5 folds; carried: plain model. For description only, the best-mean grid point against the plain model: paired gain +0.0058 (paired SE 0.0037), better in 5 of 5 folds.

**Reasoning:** The tuned configuration replaces the plain s06 model only if it beats it by more than one standard error of the fold means (G-55); otherwise the simpler plain model stays.

**Top 8 configurations by validation AP, plus the one-SE choice** (grid\_results.csv; 72 configurations):

| params | train\_mean | validation\_mean | validation\_se | train\_validation\_gap | rank | chosen\_in\_family |
| --- | --- | --- | --- | --- | --- | --- |
| {"class\_weight": null, "max\_depth": 10, "min\_samples\_leaf": 200} | 0.2293 | 0.2216 | 0.0230 | 0.0077 | 1 | False |
| {"class\_weight": null, "max\_depth": 8, "min\_samples\_leaf": 200} | 0.2224 | 0.2211 | 0.0227 | 0.0013 | 2 | False |
| {"class\_weight": null, "max\_depth": 12, "min\_samples\_leaf": 200} | 0.2325 | 0.2206 | 0.0229 | 0.0119 | 3 | False |
| {"class\_weight": null, "max\_depth": 14, "min\_samples\_leaf": 200} | 0.2340 | 0.2203 | 0.0228 | 0.0136 | 4 | False |
| {"class\_weight": null, "max\_depth": 18, "min\_samples\_leaf": 200} | 0.2350 | 0.2202 | 0.0227 | 0.0148 | 5 | False |
| {"class\_weight": null, "max\_depth": 16, "min\_samples\_leaf": 200} | 0.2345 | 0.2201 | 0.0227 | 0.0144 | 6 | False |
| {"class\_weight": "balanced", "max\_depth": 6, "min\_samples\_leaf": 200} | 0.2110 | 0.2193 | 0.0228 | -0.0084 | 7 | False |
| {"class\_weight": "balanced", "max\_depth": 10, "min\_samples\_leaf": 200} | 0.2288 | 0.2192 | 0.0228 | 0.0096 | 8 | False |
| {"class\_weight": null, "max\_depth": 4, "min\_samples\_leaf": 200} | 0.1934 | 0.2134 | 0.0217 | -0.0200 | 25 | True |

**Against the plain s06 model** (plain\_vs\_tuned.csv; paired figures are description only):

| plain\_mean | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | paired\_se | tuned\_better\_folds | carried | best\_mean | paired\_gain\_of\_best\_mean | best\_mean\_paired\_se | best\_mean\_better\_folds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.2158 | 0.2134 | 0.0217 | -0.0024 | 0.0022 | 2 | plain | 0.2216 | 0.0058 | 0.0037 | 5 |

&#91;image: Validation curve, single tree, classification\]

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 18 configurations; single tree 72 configurations; forest 48 configurations) **Check** the grid point with the s06 plain settings reproduces the s06 fold scores (tree, forest): PASS (2 of 2 reproduced)

**Files** (stages/s07\_tuning/classification/outputs/, run 20261021T040619Z): grid\_results.csv

## 7.4 Random forest

**Approved solution:** 200 trees; max\_depth: 8, 10, 12, 14, 16, 18; min\_samples\_leaf: 20, 50, 100, 200 (forest grid unchanged by G-43); max\_features: sqrt; classifier also class\_weight: None, balanced

**What was done:** forest: 48 configurations; best mean 0.2563 ({'class\_weight': None, 'max\_depth': 10, 'max\_features': 'sqrt', 'min\_samples\_leaf': 20}); one-SE choice {"class\_weight": null, "max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 200} with 0.2533 ± 0.0268.

**Observation:** Against the plain s06 model (0.2544): paired gain of the tuned model -0.0012 (paired SE 0.0005), better in 1 of 5 folds; carried: plain model. For description only, the best-mean grid point against the plain model: paired gain +0.0019 (paired SE 0.0008), better in 4 of 5 folds.

**Reasoning:** The tuned configuration replaces the plain s06 model only if it beats it by more than one standard error of the fold means (G-55); otherwise the simpler plain model stays.

**Top 8 configurations by validation AP, plus the one-SE choice** (grid\_results.csv; 48 configurations):

| params | train\_mean | validation\_mean | validation\_se | train\_validation\_gap | rank | chosen\_in\_family |
| --- | --- | --- | --- | --- | --- | --- |
| {"class\_weight": null, "max\_depth": 10, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.2853 | 0.2563 | 0.0267 | 0.0290 | 1 | False |
| {"class\_weight": null, "max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 100} | 0.2457 | 0.2562 | 0.0267 | -0.0105 | 2 | False |
| {"class\_weight": null, "max\_depth": 12, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.3040 | 0.2561 | 0.0263 | 0.0479 | 3 | False |
| {"class\_weight": null, "max\_depth": 18, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.3491 | 0.2561 | 0.0258 | 0.0930 | 4 | False |
| {"class\_weight": null, "max\_depth": 16, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.3374 | 0.2558 | 0.0261 | 0.0816 | 5 | False |
| {"class\_weight": null, "max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.3217 | 0.2558 | 0.0256 | 0.0659 | 6 | False |
| {"class\_weight": null, "max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 0.2732 | 0.2557 | 0.0264 | 0.0176 | 7 | False |
| {"class\_weight": "balanced", "max\_depth": 16, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.3414 | 0.2556 | 0.0262 | 0.0858 | 8 | False |
| {"class\_weight": null, "max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 0.2228 | 0.2533 | 0.0268 | -0.0305 | 39 | True |

**Against the plain s06 model** (plain\_vs\_tuned.csv; paired figures are description only):

| plain\_mean | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | paired\_se | tuned\_better\_folds | carried | best\_mean | paired\_gain\_of\_best\_mean | best\_mean\_paired\_se | best\_mean\_better\_folds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.2544 | 0.2533 | 0.0268 | -0.0012 | 0.0005 | 1 | plain | 0.2563 | 0.0019 | 0.0008 | 4 |

&#91;image: Validation curve, forest, classification\]

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 18 configurations; single tree 72 configurations; forest 48 configurations) **Check** the grid point with the s06 plain settings reproduces the s06 fold scores (tree, forest): PASS (2 of 2 reproduced)

**Files** (stages/s07\_tuning/classification/outputs/, run 20261021T040619Z): grid\_results.csv

## 7.5 Search method

**Approved solution:** GridSearchCV over the full Pipeline with cv = the s05 fold iterator, scoring = the primary metric (neg MAE, average precision), refit=False, return\_train\_score=True, seed 42. Best per family = the simplest configuration within one standard error of the best mean (s01 1.7). Simpler means higher alpha, lower C, shallower depth, then larger leaf. It is then compared with the family's plain s06 model by the same one-SE rule: if the plain model's mean is within one SE of the tuned configuration's mean, the plain model is kept (G-55)

**What was done:** GridSearchCV over the whole s04 pipeline on the s05 folds, scoring average\_precision, refit=False, return\_train\_score=True, seed 42; 138 configurations in total. Carried per family: linear/logistic plain s06; single tree plain s06; forest plain s06. Ladder over the carried families (description only; s08 decides): linear/logistic kept over dummy (paired gain +0.0953, better in 5 of 5 folds); single tree not kept over linear/logistic (paired gain -0.0277, better in 0 of 5 folds); forest not kept over linear/logistic (paired gain +0.0109, better in 4 of 5 folds); result linear/logistic.

**Conclusion:** Selection scores on the folds, not generalisation estimates (G-10). The finalists and the final choice are made in s08 at its gate (G-39).

**Plain vs tuned per family** (plain\_vs\_tuned.csv):

| family | plain\_mean | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | tuned\_better\_folds | carried |
| --- | --- | --- | --- | --- | --- | --- |
| linear/logistic | 0.2435 | 0.2553 | 0.0294 | 0.0118 | 5 | plain |
| single tree | 0.2158 | 0.2134 | 0.0217 | -0.0024 | 2 | plain |
| forest | 0.2544 | 0.2533 | 0.0268 | -0.0012 | 1 | plain |

**Ladder over the carried families** (ladder\_preview.csv; description only, s08 chooses):

| comparison | mean\_gain | paired\_se | folds\_better | kept\_by\_one\_se\_rule |
| --- | --- | --- | --- | --- |
| linear/logistic vs dummy | 0.0953 | 0.0157 | 5 | True |
| single tree vs linear/logistic | -0.0277 | 0.0115 | 0 | False |
| forest vs linear/logistic | 0.0109 | 0.0063 | 4 | False |

**Check** same folds as s06 (rows per fold equal): PASS **Check** every configuration scored on all five folds, whole pipeline refitted per fold: PASS **Check** no test row read: every row used was purchased before the test cutoff: PASS (latest purchase 2018-05-26 12:12:15, cutoff 2018-05-26 12:16:34)

**Files** (stages/s07\_tuning/classification/outputs/, run 20261021T040619Z): candidates.csv, counts.json, decision.json, grid\_results.csv, ladder\_preview.csv, plain\_vs\_tuned.csv

## 7.6 Overfitting check

**Approved solution:** For each configuration report the train–validation gap; flag the best configuration if the gap is large and a simpler one is within the decision rule

**What was done:** train\_validation\_gap for every configuration in grid\_results.csv (positive = worse on validation). Gap of each family's one-SE choice: linear/logistic -0.0440; single tree -0.0200; forest -0.0305.

**Reasoning:** The one-SE choice is already the simplest configuration within the rule, so no simpler configuration within the rule exists to flag; the gaps are reported for the review.

**Gap of each family's one-SE choice** (grid\_results.csv):

| family | params | train\_mean | validation\_mean | train\_validation\_gap |
| --- | --- | --- | --- | --- |
| linear | {"C": 0.01, "class\_weight": null} | 0.2113 | 0.2553 | -0.0440 |
| tree | {"class\_weight": null, "max\_depth": 4, "min\_samples\_leaf": 200} | 0.1934 | 0.2134 | -0.0200 |
| forest | {"class\_weight": null, "max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 0.2228 | 0.2533 | -0.0305 |

**Files** (stages/s07\_tuning/classification/outputs/, run 20261021T040619Z): curves/validation\_curve\_forest.csv, curves/validation\_curve\_linear.csv, curves/validation\_curve\_tree.csv, figures/validation\_curve\_forest.csv, figures/validation\_curve\_forest.png, figures/validation\_curve\_linear.csv, figures/validation\_curve\_linear.png, figures/validation\_curve\_tree.csv, figures/validation\_curve\_tree.png, grid\_results.csv

## 7.7 Outputs

**Approved solution:** grid\_results.csv (every configuration: parameters, per-fold train and validation scores, mean, SD, rank, fit time, convergence), out-of-fold predictions of each family's best, kept separate as pooled OOF vs mean-fold scores

**What was done:** grid\_results.csv, plain\_vs\_tuned.csv, ladder\_preview.csv, candidates.csv, decision.json, out-of-fold predictions of each family's best (predictions.csv.gz) with pooled vs mean-fold scores (oof\_scores.csv), validation curves (curves/, figures/); fit times in \_manifest.json.

**Out-of-fold scores of each family's one-SE choice, pooled vs mean-fold** (oof\_scores.csv):

| family | mean\_fold\_ap | pooled\_oof\_ap | pooled\_oof\_roc\_auc | pooled\_oof\_brier |
| --- | --- | --- | --- | --- |
| linear/logistic | 0.2553 | 0.2394 | 0.6132 | 0.1249 |
| single tree | 0.2134 | 0.2182 | 0.5772 | 0.1253 |
| forest | 0.2533 | 0.2396 | 0.6174 | 0.1253 |

**Check** refitting each family's best per fold gives the grid's validation scores: PASS (15 refits)

**Files** (stages/s07\_tuning/classification/outputs/, run 20261021T040619Z): counts.json, oof\_scores.csv, predictions.csv.gz
