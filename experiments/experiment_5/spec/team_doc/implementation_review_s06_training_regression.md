# s06 Training › regression — evidence cards

Round 3 · run `20261021T032208Z` · 7 checks, all PASS. Coverage and review dropdowns are on the parent tab "s06 Training"; comment on any card here.

## 6.1 Pipeline factory

**Approved solution:** Assembly only, no new transformation. One function combines the s04 recipe (feature set, imputation, encoding, scaling, log1p and log target, all defined in s04) with an estimator into one sklearn Pipeline with a stable `candidate`\_id; regression log target via TransformedTargetRegressor(func=log1p, inverse`_func=expm1)`, always scored on raw days. The pipeline is fitted inside each s05 training fold; that is where the learned steps defined in s04 (medians, scaler, route median) get their values, so nothing is fitted on validation or test rows

**What was done:** 4 candidates built by e5lib.factory from the s04 recipes.json (one spec per family) with the s06 settings from protocol.yaml; every pipeline fitted inside each of the 5 training folds (176,925 training rows over the folds). Learned imputation values per fold are in imputation\_by\_fold.csv, with the validation rows whose category level was unseen in the training fold (the one-hot step encodes them as all zeros).

**Imputation inside the folds** (linear/logistic pipeline; rows where a value was filled or a category level was unseen; the median is learned on the training fold, on the log1p scale for log1p inputs):

| fold | feature | rule | learned\_value | learned\_scale | filled\_train | filled\_validation | validation\_rows\_unseen\_level |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | distance\_km\_max | route median (customer\_state x primary\_seller\_state, then customer\_state, then global), before log1p | 452.6 | km (global fallback median) | 112 | 221 |  |
| 1 | total\_weight\_g | median + missing indicator (after log1p) | 6.686 | log1p | 11 | 5 |  |
| 1 | total\_volume\_cm3 | median + missing indicator (after log1p) | 8.987 | log1p | 11 | 5 |  |
| 1 | primary\_category | missing -> 'Unknown' level | Unknown | category | 0 | 0 | 15 |
| 1 | primary\_seller\_state | missing -> 'Unknown' level | Unknown | category | 0 | 0 | 2 |
| 2 | distance\_km\_max | route median (customer\_state x primary\_seller\_state, then customer\_state, then global), before log1p | 450.6 | km (global fallback median) | 328 | 177 |  |
| 2 | total\_weight\_g | median + missing indicator (after log1p) | 6.746 | log1p | 15 | 0 |  |
| 2 | total\_volume\_cm3 | median + missing indicator (after log1p) | 8.987 | log1p | 15 | 0 |  |
| 2 | primary\_category | missing -> 'Unknown' level | Unknown | category | 0 | 0 | 7 |
| 3 | distance\_km\_max | route median (customer\_state x primary\_seller\_state, then customer\_state, then global), before log1p | 451 | km (global fallback median) | 486 | 114 |  |
| 3 | total\_weight\_g | median + missing indicator (after log1p) | 6.746 | log1p | 16 | 0 |  |
| 3 | total\_volume\_cm3 | median + missing indicator (after log1p) | 8.987 | log1p | 16 | 0 |  |
| 3 | primary\_category | missing -> 'Unknown' level | Unknown | category | 0 | 0 | 2 |
| 3 | primary\_seller\_state | missing -> 'Unknown' level | Unknown | category | 0 | 0 | 14 |
| 4 | distance\_km\_max | route median (customer\_state x primary\_seller\_state, then customer\_state, then global), before log1p | 446.9 | km (global fallback median) | 613 | 119 |  |
| 4 | total\_weight\_g | median + missing indicator (after log1p) | 6.686 | log1p | 16 | 0 |  |
| 4 | total\_volume\_cm3 | median + missing indicator (after log1p) | 8.987 | log1p | 16 | 0 |  |
| 5 | distance\_km\_max | route median (customer\_state x primary\_seller\_state, then customer\_state, then global), before log1p | 444.4 | km (global fallback median) | 729 | 105 |  |
| 5 | total\_weight\_g | median + missing indicator (after log1p) | 6.686 | log1p | 16 | 0 |  |
| 5 | total\_volume\_cm3 | median + missing indicator (after log1p) | 8.959 | log1p | 16 | 0 |  |

**Check** preprocessing fitted inside the training fold only (learned medians equal the training-fold medians): PASS (15 fitted pipelines checked) **Check** every candidate uses its s04 recipe unchanged (selected features, log1p inputs, log target): PASS (selected set of 18 features) **Check** regression scored on raw days (log target inverted): PASS

**Files** (stages/s06\_training/regression/outputs/, run 20261021T032208Z): imputation\_by\_fold.csv

## 6.2 Families, basic to complex

**Approved solution:** On each task's selected feature set (s04 4.4), through the s04 recipe (4.8: imputation, encoding, scaling) with the s04 4.2 log transforms always on (log1p on the five contract candidates with pre-cutoff skewness > 1, plus product\_description\_lenght for classification, G-47, G-62, G-70, and on the regression target; G-36). The classification set is chosen from the 24 contract predictors plus the three candidates adopted at the s03 gate (G-70), in this order: dummy (`DummyRegressor(strategy='median')` / `DummyClassifier(strategy='prior')`) → plain `LinearRegression` / `LogisticRegression(penalty=None, solver='lbfgs', max_iter=5000)` → `DecisionTree` (starting settings max\_depth=5, min\_samples\_leaf=100) → `RandomForest` (200 trees, max\_depth=10, min\_samples\_leaf=50, max\_features='sqrt'). Seed 42

**What was done:** Families basic to complex, validation mae mean ± SE over the folds: dummy 6.4946 ± 0.6889 days; linear/logistic 5.4701 ± 0.6733 days; single tree 5.4244 ± 0.7147 days; forest 5.4434 ± 0.6826 days. Ladder: linear/logistic kept over dummy; single tree not kept over linear/logistic; forest not kept over linear/logistic. One-SE choice over all four: linear/logistic (best mean: single tree).

**Observation:** Paired per-fold gain of each step (positive = the more complex family is better; description only, s01 1.7): linear/logistic vs dummy +1.0245 days (paired SE 0.1262), better in 5 of 5 folds; single tree vs linear/logistic +0.0458 days (paired SE 0.0685), better in 3 of 5 folds; forest vs linear/logistic +0.0267 days (paired SE 0.0601), better in 3 of 5 folds.

**Reasoning:** A more complex family is adopted only when its gain over the current family clears one standard error of the fold means (the agreed rule). The fold SE also carries the level differences between folds (drift), so a small but consistent paired gain can stay below it; the paired figures show that without changing the decision.

**Conclusion:** These are selection scores on the folds, not generalisation estimates (G-10). s07 tunes the linear and tree families and compares each tuned configuration with its plain s06 model (G-55).

**Fold means of MAE** (candidates.csv):

| family | estimator | params | train\_mean | validation\_mean | validation\_se | kept | reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dummy | dummy\_median | {} | 5.3118 | 6.4946 | 0.6889 | True | baseline (simplest family) |
| linear/logistic | linear | {} | 4.2862 | 5.4701 | 0.6733 | True | kept: beats dummy by more than one SE |
| single tree | tree\_reg | {"max\_depth": 5, "min\_samples\_leaf": 100} | 4.3533 | 5.4244 | 0.7147 | False | not kept: within one SE of linear/logistic, the simpler family stays |
| forest | forest\_reg | {"max\_depth": 10, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 4.3597 | 5.4434 | 0.6826 | False | not kept: within one SE of linear/logistic, the simpler family stays |

**Paired per-fold gain of each ladder step** (paired\_differences.csv; positive = the more complex family is better; description only, s01 1.7):

| comparison | gain\_fold\_1 | gain\_fold\_2 | gain\_fold\_3 | gain\_fold\_4 | gain\_fold\_5 | mean\_gain | paired\_se | folds\_better | kept\_by\_one\_se\_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear/logistic vs dummy | 0.8707 | 0.6007 | 1.2257 | 1.1670 | 1.2582 | 1.0245 | 0.1262 | 5 | True |
| single tree vs linear/logistic | 0.0210 | 0.1807 | -0.1317 | -0.0643 | 0.2231 | 0.0458 | 0.0685 | 3 | False |
| forest vs linear/logistic | 0.0189 | 0.2254 | -0.1517 | -0.0007 | 0.0418 | 0.0267 | 0.0601 | 3 | False |

**Decisions (decision.json):**

- Keep linear/logistic over dummy? Chosen: linear/logistic (best mean: linear/logistic; band 4.7968 to 6.1434; paired gain of the complex family +1.0245 (paired SE 0.1262), better in 5 of 5 folds (description only))
- Keep single tree over linear/logistic? Chosen: linear/logistic (best mean: single tree; band 4.7097 to 6.1390; paired gain of the complex family +0.0458 (paired SE 0.0685), better in 3 of 5 folds (description only))
- Keep forest over linear/logistic? Chosen: linear/logistic (best mean: forest; band 4.7607 to 6.1260; paired gain of the complex family +0.0267 (paired SE 0.0601), better in 3 of 5 folds (description only))
- Family carried as the s06 reference (all four candidates) Chosen: linear/logistic (best mean: single tree; ladder result: linear/logistic. s07 tunes the linear and tree families whatever this result (s07 principle).)

&#91;image: Family ladder, regression\]

**Check** identical rows and folds for every candidate: PASS (4 candidates x 5 folds) **Check** every candidate uses its s04 recipe unchanged (selected features, log1p inputs, log target): PASS (selected set of 18 features) **Check** the simplest model of each family is present (dummy, plain linear/logistic, depth-5 tree, s06 forest): PASS

**Files** (stages/s06\_training/regression/outputs/, run 20261021T032208Z): candidates.csv, counts.json, decision.json, figures/family\_ladder.csv, figures/family\_ladder.png, paired\_differences.csv

## 6.4 Scores recorded

**Approved solution:** For every candidate and fold: training and validation scores on all s01 metrics, row and positive counts, fit time, convergence warnings

**What was done:** metrics\_long.csv: training and validation scores for 4 candidates x 5 folds on every s01 metric; fit\_log.csv: rows and warnings per fit, fit times in \_manifest.json (convergence warnings: 0); predictions.csv.gz: 248,036 out-of-fold predictions.

**Mean over the 5 folds** (metrics\_long.csv; threshold metrics are description only, the threshold is chosen in s08):

| family | phase | mae | rmse | r2 | within\_3d |
| --- | --- | --- | --- | --- | --- |
| dummy | train | 5.3118 | 8.0528 | -0.0432 | 0.4001 |
| dummy | validation | 6.4946 | 9.5348 | -0.1355 | 0.3390 |
| forest | train | 4.3597 | 7.0610 | 0.1973 | 0.5048 |
| forest | validation | 5.4434 | 8.5599 | 0.0971 | 0.4583 |
| linear/logistic | train | 4.2862 | 6.8815 | 0.2382 | 0.5132 |
| linear/logistic | validation | 5.4701 | 8.5785 | 0.0911 | 0.4654 |
| single tree | train | 4.3533 | 6.9494 | 0.2222 | 0.5059 |
| single tree | validation | 5.4244 | 8.5599 | 0.0975 | 0.4730 |

**Fit time and warnings** (fit\_log.csv; fit times from \_manifest.json, which is not hashed because they change from run to run):

| family | mean\_fit\_seconds | warnings |
| --- | --- | --- |
| dummy | 0.20 | 0 |
| forest | 1.24 | 0 |
| linear/logistic | 0.35 | 0 |
| single tree | 0.37 | 0 |

**Check** identical rows and folds for every candidate: PASS (4 candidates x 5 folds) **Check** no test row read: every row used was purchased before the test cutoff: PASS (latest purchase 2018-05-24 18:56:59, cutoff 2018-05-27 12:30:34) **Check** regression scored on raw days (log target inverted): PASS

**Files** (stages/s06\_training/regression/outputs/, run 20261021T032208Z): figures/family\_ladder.csv, figures/family\_ladder.png, fit\_log.csv, metrics\_long.csv, predictions.csv.gz

## 6.5 Residual diagnostics

**Approved solution:** Residual vs fitted, residual histogram, Q–Q plot on out-of-fold predictions of the plain linear model and the best tree model

**What was done:** Residual vs fitted, histogram and Q-Q plot on out-of-fold predictions of the plain linear model and the better tree model (single tree). linear: residual mean 3.32, median 1.28, skewness 2.65, share above +10 days 14.11%; tree: residual mean 3.22, median 1.05, skewness 2.70, share above +10 days 14.16%.

&#91;image: Residual diagnostics, regression\]

**Files** (stages/s06\_training/regression/outputs/, run 20261021T032208Z): curves/residual\_quantiles\_linear.csv, curves/residual\_quantiles\_tree.csv, figures/residual\_diagnostics.csv, figures/residual\_diagnostics.png, predictions.csv.gz

## 6.7 Learning curves and design matrix

**Approved solution:** Learning curves on the latest fold (training sizes 20–100%, same validation block), to read under- vs overfitting before s07. Encoded design-matrix rank and condition number for the linear models

**What was done:** Learning curves on fold 5: the most recent 20, 40, 60, 80 and 100% of its training rows against the same validation block (10,740 rows). Linear/logistic design matrix per training fold: fold 1 rank 128 of 128, condition number 312; fold 2 rank 133 of 133, condition number 341; fold 3 rank 134 of 134, condition number 353; fold 4 rank 137 of 137, condition number 428; fold 5 rank 137 of 137, condition number 454.

**Observation:** dummy validation mae 5.4686 with the most recent 20% vs 5.0815 with all rows; linear/logistic validation mae 3.3949 with the most recent 20% vs 3.8233 with all rows; single tree validation mae 3.7316 with the most recent 20% vs 3.6002 with all rows; forest validation mae 3.9228 with the most recent 20% vs 3.7815 with all rows; target mean in fold 5: training 13.1094, validation 9.6289.

**Reasoning:** Subsets keep the rows closest to the validation block, so a smaller training set is not also an older one; the tree recipe is not measured (rank-deficient by design, s04 M-01).

**Learning curves, latest fold** (curves/learning\_curves.csv):

| family | share | train\_rows | train\_mae | validation\_mae |
| --- | --- | --- | --- | --- |
| dummy | 0.2000 | 11,976 | 6.3738 | 5.4686 |
| linear/logistic | 0.2000 | 11,976 | 4.6255 | 3.3949 |
| single tree | 0.2000 | 11,976 | 4.7511 | 3.7316 |
| forest | 0.2000 | 11,976 | 4.7867 | 3.9228 |
| dummy | 0.4000 | 23,952 | 6.7421 | 5.5683 |
| linear/logistic | 0.4000 | 23,952 | 5.1253 | 4.4433 |
| single tree | 0.4000 | 23,952 | 5.2420 | 4.4240 |
| forest | 0.4000 | 23,952 | 5.2526 | 4.2625 |
| dummy | 0.6000 | 35,928 | 6.4463 | 5.4225 |
| linear/logistic | 0.6000 | 35,928 | 5.0768 | 4.1482 |
| single tree | 0.6000 | 35,928 | 5.1582 | 4.0532 |
| forest | 0.6000 | 35,928 | 5.1375 | 4.0239 |
| dummy | 0.8000 | 47,904 | 6.1159 | 5.1298 |
| linear/logistic | 0.8000 | 47,904 | 4.8466 | 3.9106 |
| single tree | 0.8000 | 47,904 | 4.8449 | 3.5922 |
| forest | 0.8000 | 47,904 | 4.8728 | 3.7976 |
| dummy | 1.0000 | 59,880 | 5.9542 | 5.0815 |
| linear/logistic | 1.0000 | 59,880 | 4.8148 | 3.8233 |
| single tree | 1.0000 | 59,880 | 4.8356 | 3.6002 |
| forest | 1.0000 | 59,880 | 4.8477 | 3.7815 |

&#91;image: Learning curves, regression\]

**Design matrix per training fold, linear/logistic recipe** (design\_matrix\_by\_fold.csv):

| fold | rows | encoded\_columns | duplicates\_dropped | columns | rank | full\_rank | condition\_number |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 11,297 | 129 | missingindicator\_total\_volume\_cm3 | 128 | 128 | True | 312.0 |
| 2 | 23,864 | 134 | missingindicator\_total\_volume\_cm3 | 133 | 133 | True | 340.8 |
| 3 | 33,927 | 135 | missingindicator\_total\_volume\_cm3 | 134 | 134 | True | 353.2 |
| 4 | 47,957 | 138 | missingindicator\_total\_volume\_cm3 | 137 | 137 | True | 428.1 |
| 5 | 59,880 | 138 | missingindicator\_total\_volume\_cm3 | 137 | 137 | True | 453.8 |

**Check** linear/logistic design matrix full rank in every training fold: PASS (fold 1 rank 128 of 128; fold 2 rank 133 of 133; fold 3 rank 134 of 134; fold 4 rank 137 of 137; fold 5 rank 137 of 137)

**Files** (stages/s06\_training/regression/outputs/, run 20261021T032208Z): curves/learning\_curves.csv, design\_matrix\_by\_fold.csv, figures/learning\_curves.csv, figures/learning\_curves.png

## 6.8 Outputs

**Approved solution:** `metrics_long.csv`, out-of-fold `predictions.csv.gz`, `decision.json` (each family comparison under the decision rule, with fold scores), `figures/`

**What was done:** Outputs: metrics\_long.csv, predictions.csv.gz, candidates.csv, decision.json, fit\_log.csv, imputation\_by\_fold.csv, design\_matrix\_by\_fold.csv, curves/ and figures/ with sidecar data.

**Files** (stages/s06\_training/regression/outputs/, run 20261021T032208Z): counts.json
