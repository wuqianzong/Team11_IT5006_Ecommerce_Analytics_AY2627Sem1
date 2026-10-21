# s06 Training › classification — evidence cards

Round 3 · run `20261021T032248Z` · 6 checks, all PASS. Coverage and review dropdowns are on the parent tab "s06 Training"; comment on any card here.

## 6.1 Pipeline factory

**Approved solution:** Assembly only, no new transformation. One function combines the s04 recipe (feature set, imputation, encoding, scaling, log1p and log target, all defined in s04) with an estimator into one sklearn Pipeline with a stable `candidate`\_id; regression log target via TransformedTargetRegressor(func=log1p, inverse`_func=expm1)`, always scored on raw days. The pipeline is fitted inside each s05 training fold; that is where the learned steps defined in s04 (medians, scaler, route median) get their values, so nothing is fitted on validation or test rows

**What was done:** 4 candidates built by e5lib.factory from the s04 recipes.json (one spec per family) with the s06 settings from protocol.yaml; every pipeline fitted inside each of the 5 training folds (176,512 training rows over the folds). Learned imputation values per fold are in imputation\_by\_fold.csv, with the validation rows whose category level was unseen in the training fold (the one-hot step encodes them as all zeros).

**Imputation inside the folds** (linear/logistic pipeline; rows where a value was filled or a category level was unseen; the median is learned on the training fold, on the log1p scale for log1p inputs):

| fold | feature | rule | learned\_value | learned\_scale | filled\_train | filled\_validation | validation\_rows\_unseen\_level |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | distance\_km\_max | route median (customer\_state x primary\_seller\_state, then customer\_state, then global), before log1p | 457.2 | km (global fallback median) | 108 | 228 |  |
| 1 | total\_volume\_cm3 | median + missing indicator (after log1p) | 8.987 | log1p | 11 | 5 |  |
| 1 | product\_description\_lenght | median + missing indicator (after log1p) | 6.368 | log1p | 261 | 180 |  |
| 1 | total\_weight\_g | median + missing indicator (after log1p) | 6.686 | log1p | 11 | 5 |  |
| 1 | seller\_prior\_review\_mean | median + missing indicator | 4.25 | raw | 2,138 | 702 |  |
| 1 | product\_photos\_qty | median + missing indicator | 2 | raw | 261 | 180 |  |
| 1 | primary\_category | missing -> 'Unknown' level | Unknown | category | 0 | 0 | 16 |
| 1 | primary\_seller\_state | missing -> 'Unknown' level | Unknown | category | 0 | 0 | 2 |
| 2 | distance\_km\_max | route median (customer\_state x primary\_seller\_state, then customer\_state, then global), before log1p | 452 | km (global fallback median) | 331 | 181 |  |
| 2 | total\_volume\_cm3 | median + missing indicator (after log1p) | 8.987 | log1p | 15 | 0 |  |
| 2 | product\_description\_lenght | median + missing indicator (after log1p) | 6.356 | log1p | 447 | 175 |  |
| 2 | total\_weight\_g | median + missing indicator (after log1p) | 6.746 | log1p | 15 | 0 |  |
| 2 | seller\_prior\_review\_mean | median + missing indicator | 4.222 | raw | 2,807 | 648 |  |
| 2 | product\_photos\_qty | median + missing indicator | 2 | raw | 447 | 175 |  |
| 2 | primary\_category | missing -> 'Unknown' level | Unknown | category | 0 | 0 | 7 |
| 3 | distance\_km\_max | route median (customer\_state x primary\_seller\_state, then customer\_state, then global), before log1p | 454.4 | km (global fallback median) | 491 | 117 |  |
| 3 | total\_volume\_cm3 | median + missing indicator (after log1p) | 8.987 | log1p | 16 | 0 |  |
| 3 | product\_description\_lenght | median + missing indicator (after log1p) | 6.364 | log1p | 586 | 322 |  |
| 3 | total\_weight\_g | median + missing indicator (after log1p) | 6.746 | log1p | 16 | 0 |  |
| 3 | seller\_prior\_review\_mean | median + missing indicator | 4.233 | raw | 3,376 | 543 |  |
| 3 | product\_photos\_qty | median + missing indicator | 2 | raw | 586 | 322 |  |
| 3 | primary\_category | missing -> 'Unknown' level | Unknown | category | 0 | 0 | 2 |
| 3 | primary\_seller\_state | missing -> 'Unknown' level | Unknown | category | 0 | 0 | 14 |
| 4 | distance\_km\_max | route median (customer\_state x primary\_seller\_state, then customer\_state, then global), before log1p | 448.6 | km (global fallback median) | 625 | 121 |  |
| 4 | total\_volume\_cm3 | median + missing indicator (after log1p) | 8.987 | log1p | 16 | 0 |  |
| 4 | product\_description\_lenght | median + missing indicator (after log1p) | 6.365 | log1p | 888 | 219 |  |
| 4 | total\_weight\_g | median + missing indicator (after log1p) | 6.686 | log1p | 16 | 0 |  |
| 4 | seller\_prior\_review\_mean | median + missing indicator | 4.233 | raw | 3,891 | 473 |  |
| 4 | product\_photos\_qty | median + missing indicator | 2 | raw | 888 | 219 |  |
| 4 | primary\_seller\_state | missing -> 'Unknown' level | Unknown | category | 0 | 0 | 5 |
| 5 | distance\_km\_max | route median (customer\_state x primary\_seller\_state, then customer\_state, then global), before log1p | 447.1 | km (global fallback median) | 744 | 102 |  |
| 5 | total\_volume\_cm3 | median + missing indicator (after log1p) | 8.959 | log1p | 16 | 0 |  |
| 5 | product\_description\_lenght | median + missing indicator (after log1p) | 6.38 | log1p | 1,133 | 87 |  |
| 5 | total\_weight\_g | median + missing indicator (after log1p) | 6.686 | log1p | 16 | 0 |  |
| 5 | seller\_prior\_review\_mean | median + missing indicator | 4.219 | raw | 4,458 | 572 |  |
| 5 | product\_photos\_qty | median + missing indicator | 2 | raw | 1,133 | 87 |  |

**Check** preprocessing fitted inside the training fold only (learned medians equal the training-fold medians): PASS (15 fitted pipelines checked) **Check** every candidate uses its s04 recipe unchanged (selected features, log1p inputs): PASS (selected set of 19 features)

**Files** (stages/s06\_training/classification/outputs/, run 20261021T032248Z): imputation\_by\_fold.csv

## 6.2 Families, basic to complex

**Approved solution:** On each task's selected feature set (s04 4.4), through the s04 recipe (4.8: imputation, encoding, scaling) with the s04 4.2 log transforms always on (log1p on the five contract candidates with pre-cutoff skewness > 1, plus product\_description\_lenght for classification, G-47, G-62, G-70, and on the regression target; G-36). The classification set is chosen from the 24 contract predictors plus the three candidates adopted at the s03 gate (G-70), in this order: dummy (`DummyRegressor(strategy='median')` / `DummyClassifier(strategy='prior')`) → plain `LinearRegression` / `LogisticRegression(penalty=None, solver='lbfgs', max_iter=5000)` → `DecisionTree` (starting settings max\_depth=5, min\_samples\_leaf=100) → `RandomForest` (200 trees, max\_depth=10, min\_samples\_leaf=50, max\_features='sqrt'). Seed 42

**What was done:** Families basic to complex, validation ap mean ± SE over the folds: dummy 0.1482 ± 0.0198; linear/logistic 0.2435 ± 0.0314; single tree 0.2158 ± 0.0233; forest 0.2544 ± 0.0267. Ladder: linear/logistic kept over dummy; single tree not kept over linear/logistic; forest not kept over linear/logistic. One-SE choice over all four: linear/logistic (best mean: forest).

**Observation:** Paired per-fold gain of each step (positive = the more complex family is better; description only, s01 1.7): linear/logistic vs dummy +0.0953 (paired SE 0.0157), better in 5 of 5 folds; single tree vs linear/logistic -0.0277 (paired SE 0.0115), better in 0 of 5 folds; forest vs linear/logistic +0.0109 (paired SE 0.0063), better in 4 of 5 folds.

**Reasoning:** A more complex family is adopted only when its gain over the current family clears one standard error of the fold means (the agreed rule). The fold SE also carries the level differences between folds (drift), so a small but consistent paired gain can stay below it; the paired figures show that without changing the decision.

**Conclusion:** These are selection scores on the folds, not generalisation estimates (G-10). s07 tunes the linear and tree families and compares each tuned configuration with its plain s06 model (G-55).

**Fold means of AP** (candidates.csv):

| family | estimator | params | train\_mean | validation\_mean | validation\_se | kept | reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dummy | dummy\_prior | {} | 0.1281 | 0.1482 | 0.0198 | True | baseline (simplest family) |
| linear/logistic | logistic | {} | 0.2213 | 0.2435 | 0.0314 | True | kept: beats dummy by more than one SE |
| single tree | tree\_clf | {"max\_depth": 5, "min\_samples\_leaf": 100} | 0.2078 | 0.2158 | 0.0233 | False | not kept: within one SE of linear/logistic, the simpler family stays |
| forest | forest\_clf | {"max\_depth": 10, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 0.2570 | 0.2544 | 0.0267 | False | not kept: within one SE of linear/logistic, the simpler family stays |

**Paired per-fold gain of each ladder step** (paired\_differences.csv; positive = the more complex family is better; description only, s01 1.7):

| comparison | gain\_fold\_1 | gain\_fold\_2 | gain\_fold\_3 | gain\_fold\_4 | gain\_fold\_5 | mean\_gain | paired\_se | folds\_better | kept\_by\_one\_se\_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear/logistic vs dummy | 0.0419 | 0.0864 | 0.0952 | 0.1325 | 0.1207 | 0.0953 | 0.0157 | 5 | True |
| single tree vs linear/logistic | -0.0137 | -0.0071 | -0.0143 | -0.0701 | -0.0332 | -0.0277 | 0.0115 | 0 | False |
| forest vs linear/logistic | 0.0193 | 0.0254 | 0.0135 | -0.0114 | 0.0078 | 0.0109 | 0.0063 | 4 | False |

**Decisions (decision.json):**

- Keep linear/logistic over dummy? Chosen: linear/logistic (best mean: linear/logistic; band 0.2121 to 0.2749; paired gain of the complex family +0.0953 (paired SE 0.0157), better in 5 of 5 folds (description only))
- Keep single tree over linear/logistic? Chosen: linear/logistic (best mean: linear/logistic; band 0.2121 to 0.2749; paired gain of the complex family -0.0277 (paired SE 0.0115), better in 0 of 5 folds (description only))
- Keep forest over linear/logistic? Chosen: linear/logistic (best mean: forest; band 0.2277 to 0.2811; paired gain of the complex family +0.0109 (paired SE 0.0063), better in 4 of 5 folds (description only))
- Family carried as the s06 reference (all four candidates) Chosen: linear/logistic (best mean: forest; ladder result: linear/logistic. s07 tunes the linear and tree families whatever this result (s07 principle).)

&#91;image: Family ladder, classification\]

**Check** identical rows and folds for every candidate: PASS (4 candidates x 5 folds) **Check** every candidate uses its s04 recipe unchanged (selected features, log1p inputs): PASS (selected set of 19 features) **Check** the simplest model of each family is present (dummy, plain linear/logistic, depth-5 tree, s06 forest): PASS

**Files** (stages/s06\_training/classification/outputs/, run 20261021T032248Z): candidates.csv, counts.json, decision.json, figures/family\_ladder.csv, figures/family\_ladder.png, paired\_differences.csv

## 6.4 Scores recorded

**Approved solution:** For every candidate and fold: training and validation scores on all s01 metrics, row and positive counts, fit time, convergence warnings

**What was done:** metrics\_long.csv: training and validation scores for 4 candidates x 5 folds on every s01 metric (threshold metrics at 0.5 and 1/6); fit\_log.csv: rows and warnings per fit, fit times in \_manifest.json (convergence warnings: 0); predictions.csv.gz: 248,092 out-of-fold predictions.

**Mean over the 5 folds** (metrics\_long.csv; threshold metrics are description only, the threshold is chosen in s08):

| family | phase | ap | roc\_auc | brier | precision @0.5 | recall @0.5 | precision @1/6 | recall @1/6 | f1 @1/6 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dummy | train | 0.1281 | 0.5000 | 0.1116 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| dummy | validation | 0.1482 | 0.5000 | 0.1269 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| forest | train | 0.2570 | 0.6842 | 0.1072 | 0.0000 | 0.0000 | 0.2851 | 0.2609 | 0.2652 |
| forest | validation | 0.2544 | 0.6336 | 0.1234 | 0.0000 | 0.0000 | 0.3194 | 0.2085 | 0.2337 |
| linear/logistic | train | 0.2213 | 0.6399 | 0.1078 | 0.5147 | 0.0139 | 0.2335 | 0.3121 | 0.2643 |
| linear/logistic | validation | 0.2435 | 0.6213 | 0.1243 | 0.4755 | 0.0167 | 0.2877 | 0.2370 | 0.2296 |
| single tree | train | 0.2078 | 0.6267 | 0.1078 | 0.3296 | 0.0145 | 0.2421 | 0.2708 | 0.2553 |
| single tree | validation | 0.2158 | 0.5952 | 0.1242 | 0.3813 | 0.0135 | 0.2822 | 0.2198 | 0.2441 |

**Fit time and warnings** (fit\_log.csv; fit times from \_manifest.json, which is not hashed because they change from run to run):

| family | mean\_fit\_seconds | warnings |
| --- | --- | --- |
| dummy | 0.15 | 0 |
| forest | 1.01 | 0 |
| linear/logistic | 0.79 | 0 |
| single tree | 0.27 | 0 |

**Check** identical rows and folds for every candidate: PASS (4 candidates x 5 folds) **Check** no test row read: every row used was purchased before the test cutoff: PASS (latest purchase 2018-05-23 11:29:51, cutoff 2018-05-26 12:16:34)

**Files** (stages/s06\_training/classification/outputs/, run 20261021T032248Z): figures/family\_ladder.csv, figures/family\_ladder.png, fit\_log.csv, metrics\_long.csv, predictions.csv.gz

## 6.6 Classification diagnostics

**Approved solution:** Out-of-fold PR and ROC curves, reliability curve, Brier, predicted-probability histogram per class

**What was done:** Pooled out-of-fold PR, ROC and reliability curves for every family, Brier score, and the predicted-probability histogram per class for the best non-dummy family. dummy: AP 0.1503, ROC-AUC 0.4990, Brier 0.1281; linear/logistic: AP 0.2297, ROC-AUC 0.6053, Brier 0.1256; single tree: AP 0.2198, ROC-AUC 0.5835, Brier 0.1255; forest: AP 0.2453, ROC-AUC 0.6192, Brier 0.1247.

**Reasoning:** Pooled curves join the five validation blocks; the selection rule uses the per-fold means in 6.2, so the two can differ slightly.

**Pooled out-of-fold scores** (oof\_diagnostics.csv):

| family | pooled\_oof\_ap | pooled\_oof\_roc\_auc | pooled\_oof\_brier | mean\_predicted | observed\_prevalence |
| --- | --- | --- | --- | --- | --- |
| dummy | 0.1503 | 0.4990 | 0.1281 | 0.1274 | 0.1499 |
| linear/logistic | 0.2297 | 0.6053 | 0.1256 | 0.1148 | 0.1499 |
| single tree | 0.2198 | 0.5835 | 0.1255 | 0.1212 | 0.1499 |
| forest | 0.2453 | 0.6192 | 0.1247 | 0.1228 | 0.1499 |

&#91;image: Classification diagnostics\]

**Files** (stages/s06\_training/classification/outputs/, run 20261021T032248Z): curves/pr\_dummy.csv, curves/pr\_forest.csv, curves/pr\_linear.csv, curves/pr\_tree.csv, curves/reliability\_dummy.csv, curves/reliability\_forest.csv, curves/reliability\_linear.csv, curves/reliability\_tree.csv, curves/roc\_dummy.csv, curves/roc\_forest.csv, curves/roc\_linear.csv, curves/roc\_tree.csv, figures/classification\_diagnostics.csv, figures/classification\_diagnostics.png, oof\_diagnostics.csv, predictions.csv.gz

## 6.7 Learning curves and design matrix

**Approved solution:** Learning curves on the latest fold (training sizes 20–100%, same validation block), to read under- vs overfitting before s07. Encoded design-matrix rank and condition number for the linear models

**What was done:** Learning curves on fold 5: the most recent 20, 40, 60, 80 and 100% of its training rows against the same validation block (10,251 rows). Linear/logistic design matrix per training fold: fold 1 rank 129 of 129, condition number 763; fold 2 rank 134 of 134, condition number 1.03e+03; fold 3 rank 135 of 135, condition number 1.22e+03; fold 4 rank 137 of 137, condition number 1.47e+03; fold 5 rank 138 of 138, condition number 1.55e+03.

**Observation:** dummy validation ap 0.1081 with the most recent 20% vs 0.1081 with all rows; linear/logistic validation ap 0.2036 with the most recent 20% vs 0.2288 with all rows; single tree validation ap 0.1978 with the most recent 20% vs 0.1956 with all rows; forest validation ap 0.2327 with the most recent 20% vs 0.2365 with all rows; target mean in fold 5: training 0.1440, validation 0.1081.

**Reasoning:** Subsets keep the rows closest to the validation block, so a smaller training set is not also an older one; the tree recipe is not measured (rank-deficient by design, s04 M-01).

**Learning curves, latest fold** (curves/learning\_curves.csv):

| family | share | train\_rows | train\_ap | validation\_ap |
| --- | --- | --- | --- | --- |
| dummy | 0.2000 | 12,072 | 0.1774 | 0.1081 |
| linear/logistic | 0.2000 | 12,072 | 0.3590 | 0.2036 |
| single tree | 0.2000 | 12,072 | 0.3085 | 0.1978 |
| forest | 0.2000 | 12,072 | 0.3837 | 0.2327 |
| dummy | 0.4000 | 24,144 | 0.1692 | 0.1081 |
| linear/logistic | 0.4000 | 24,144 | 0.3313 | 0.2162 |
| single tree | 0.4000 | 24,144 | 0.3010 | 0.1949 |
| forest | 0.4000 | 24,144 | 0.3599 | 0.2309 |
| dummy | 0.6000 | 36,217 | 0.1593 | 0.1081 |
| linear/logistic | 0.6000 | 36,217 | 0.2997 | 0.2216 |
| single tree | 0.6000 | 36,217 | 0.2780 | 0.2039 |
| forest | 0.6000 | 36,217 | 0.3261 | 0.2324 |
| dummy | 0.8000 | 48,289 | 0.1472 | 0.1081 |
| linear/logistic | 0.8000 | 48,289 | 0.2682 | 0.2265 |
| single tree | 0.8000 | 48,289 | 0.2620 | 0.1914 |
| forest | 0.8000 | 48,289 | 0.3001 | 0.2379 |
| dummy | 1.0000 | 60,361 | 0.1440 | 0.1081 |
| linear/logistic | 1.0000 | 60,361 | 0.2500 | 0.2288 |
| single tree | 1.0000 | 60,361 | 0.2452 | 0.1956 |
| forest | 1.0000 | 60,361 | 0.2815 | 0.2365 |

&#91;image: Learning curves, classification\]

**Design matrix per training fold, linear/logistic recipe** (design\_matrix\_by\_fold.csv):

| fold | rows | encoded\_columns | duplicates\_dropped | columns | rank | full\_rank | condition\_number |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 11,077 | 131 | missingindicator\_total\_weight\_g; missingindicator\_product\_photos\_qty | 129 | 129 | True | 762.7 |
| 2 | 23,573 | 136 | missingindicator\_total\_weight\_g; missingindicator\_product\_photos\_qty | 134 | 134 | True | 1026.3 |
| 3 | 33,568 | 137 | missingindicator\_total\_weight\_g; missingindicator\_product\_photos\_qty | 135 | 135 | True | 1224.8 |
| 4 | 47,933 | 139 | missingindicator\_total\_weight\_g; missingindicator\_product\_photos\_qty | 137 | 137 | True | 1474.6 |
| 5 | 60,361 | 140 | missingindicator\_total\_weight\_g; missingindicator\_product\_photos\_qty | 138 | 138 | True | 1549.5 |

**Check** linear/logistic design matrix full rank in every training fold: PASS (fold 1 rank 129 of 129; fold 2 rank 134 of 134; fold 3 rank 135 of 135; fold 4 rank 137 of 137; fold 5 rank 138 of 138)

**Files** (stages/s06\_training/classification/outputs/, run 20261021T032248Z): curves/learning\_curves.csv, design\_matrix\_by\_fold.csv, figures/learning\_curves.csv, figures/learning\_curves.png

## 6.8 Outputs

**Approved solution:** `metrics_long.csv`, out-of-fold `predictions.csv.gz`, `decision.json` (each family comparison under the decision rule, with fold scores), `figures/`

**What was done:** Outputs: metrics\_long.csv, predictions.csv.gz, candidates.csv, decision.json, fit\_log.csv, imputation\_by\_fold.csv, design\_matrix\_by\_fold.csv, curves/ and figures/ with sidecar data.

**Files** (stages/s06\_training/classification/outputs/, run 20261021T032248Z): counts.json
