# B8 › regression — gate evidence

## Supplement for decisions and the report (added 2026-10-24; DOC\_GAPS D-01, R-05)

Added after the pipeline ran, from accepted outputs only; nothing above is changed. Charts marked doc\_support come from pipeline\_b/stages/doc\_support/regression/outputs (run 20261024T065707Z, uncommitted, reads accepted outputs only). B8 figures: pipeline\_b/stages/b08/regression/outputs/figures (run 20261024T042516Z).

**Finalists** (figures/finalists.png):

&#91;image: finalists\]

**Population comparison, mean ± SE (R-05)** (doc\_support figures/r05\_population.png; data: population\_summary.csv; raw scores as in the adoption rule):

&#91;image: population comparison\]

| population\_and\_model | metric | mean\_5\_folds | se\_5\_folds | mean\_folds\_2\_5 | se\_folds\_2\_5 |
| --- | --- | --- | --- | --- | --- |
| A's frozen model on A's validation rows | mae | 5.4701 | 0.6733 | 5.8039 | 0.7549 |
| A's frozen model on B's validation rows | mae | 5.1423 | 0.6616 | 5.4969 | 0.7211 |
| B's recommended model (reg.sel.log.linear) on B's validation rows | mae | 5.0247 | 0.6115 | 5.3503 | 0.6682 |

Round 1 · AT THE GATE, not frozen · run `20261024T032040Z` on uncommitted code (working tree on 171f23d) · 7 checks, all PASS · the test cohort is not read. Coverage and review dropdowns are on the parent tab "B8 Selection". Updated 2026-10-24 with fold-by-fold results of every finalist and the adoption result for every finalist.

*Text from A's code refers to B's inputs: "s04 recipe" = B4, "s05 folds" = B5, "s06"/"s07" = B6/B7, and "spec/human\_decisions.yaml section s08" = pipeline\_b/spec/human\_decisions\_B.yaml section b08.*

## B8.1–B8.4 Selection review pack (written by A's s08 code on B's inputs)

Cards:

Recommendation (one-SE rule, s01 1.7): **linear/logistic** (`reg.sel.log.linear`). Ladder result (each more complex family kept only beyond one SE): linear/logistic.

## Finalists (validation, mean over the five folds)

| family | source | validation\_mean | validation\_se | train\_validation\_gap | grid\_edge | recommended |
| --- | --- | --- | --- | --- | --- | --- |
| dummy | s06 reference | 5.9689 | 0.7107 | 1.1751 | not a grid configuration (dummy) | False |
| linear/logistic | s06 reference | 5.0247 | 0.6115 | 1.1640 | plain s06 model, not a grid configuration | True |
| single tree | s06 reference | 5.0532 | 0.6394 | 1.1043 | none | False |
| forest | s07 carried (plain s06) | 4.9627 | 0.6457 | 1.0520 | none | False |

## Every s01 metric (mean and SE over the folds)

| family | mae\_mean | mae\_se | r2\_mean | r2\_se | rmse\_mean | rmse\_se | within\_3d\_mean | within\_3d\_se |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dummy | 5.9689 | 0.7107 | -0.1398 | 0.0414 | 8.7467 | 1.2172 | 0.3752 | 0.0259 |
| linear/logistic | 5.0247 | 0.6115 | 0.0873 | 0.0530 | 7.8367 | 1.1084 | 0.5010 | 0.0269 |
| single tree | 5.0532 | 0.6394 | 0.0869 | 0.0498 | 7.8619 | 1.1623 | 0.4926 | 0.0276 |
| forest | 4.9627 | 0.6457 | 0.1148 | 0.0600 | 7.7535 | 1.1711 | 0.4943 | 0.0268 |

*Metric note (Henry's question):* **within\_3d** is the share of orders whose predicted delivery time is within ±3 days of the actual delivery time (|predicted − actual| ≤ 3 days), so higher is better. **within\_3d\_mean** is that share averaged over the five validation folds, and **within\_3d\_se** is its standard error over the folds (fold SD / √5). Likewise, \_mean and \_se on every other metric are the mean and SE over the five folds. Definition: e5lib/metrics.py (A's s01 metric set).

## Ladder, basic to complex (paired gains are description only)

| comparison | gain\_fold\_1 | gain\_fold\_2 | gain\_fold\_3 | gain\_fold\_4 | gain\_fold\_5 | mean\_gain | paired\_se | folds\_better | kept\_by\_one\_se\_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear/logistic vs dummy | 0.6850 | 0.5072 | 1.1860 | 1.3903 | 0.9526 | 0.9442 | 0.1606 | 5 | True |
| single tree vs linear/logistic | 0.0415 | 0.3386 | -0.1652 | -0.2391 | -0.1185 | -0.0285 | 0.1027 | 2 | False |
| forest vs linear/logistic | 0.1377 | 0.2667 | -0.0787 | -0.0931 | 0.0771 | 0.0619 | 0.0677 | 3 | False |

## Learning curves of the recommendation (s06, latest fold)

| family | share | train\_rows | train\_mae | validation\_mae |
| --- | --- | --- | --- | --- |
| linear | 0.2000 | 9483 | 4.3413 | 3.1600 |
| linear | 0.4000 | 18966 | 4.7686 | 4.2864 |
| linear | 0.6000 | 28449 | 4.7639 | 3.8166 |
| linear | 0.8000 | 37932 | 4.4582 | 3.5837 |
| linear | 1.0000 | 47415 | 4.4018 | 3.5469 |

## Team decision (A's wording; for B read human\_decisions\_B.yaml section b08)

Record in spec/human\_decisions.yaml, section s08.regression: `model` (chosen, recommended, rationale, grid\_edge\_action, decided\_by, date). Under G-78 this is decided at the combined review of s06-s08; only then do 8.5-8.8 run.

## Fold-by-fold results of every finalist (metrics\_long.csv, validation)

**mae** per fold (columns: finalist family):

| fold | dummy\_median | forest\_reg | linear | tree\_reg |
| --- | --- | --- | --- | --- |
| 1 | 4.4073 | 3.5846 | 3.7223 | 3.6808 |
| 2 | 5.9751 | 5.2012 | 5.4678 | 5.1292 |
| 3 | 6.8000 | 5.6926 | 5.6140 | 5.7792 |
| 4 | 8.1627 | 6.8655 | 6.7724 | 7.0115 |
| 5 | 4.4995 | 3.4698 | 3.5469 | 3.6654 |

**rmse** per fold (columns: finalist family):

| fold | dummy\_median | forest\_reg | linear | tree\_reg |
| --- | --- | --- | --- | --- |
| 1 | 6.3082 | 5.6386 | 5.8892 | 5.7869 |
| 2 | 9.3205 | 8.5830 | 8.9070 | 8.4437 |
| 3 | 10.2310 | 9.0812 | 8.9242 | 9.1092 |
| 4 | 12.1833 | 10.9342 | 10.7672 | 11.2087 |
| 5 | 5.6904 | 4.5306 | 4.6961 | 4.7609 |

**r2** per fold (columns: finalist family):

| fold | dummy\_median | forest\_reg | linear | tree\_reg |
| --- | --- | --- | --- | --- |
| 1 | -0.0117 | 0.1917 | 0.1182 | 0.1486 |
| 2 | -0.1599 | 0.0164 | -0.0593 | 0.0481 |
| 3 | -0.2065 | 0.0494 | 0.0820 | 0.0436 |
| 4 | -0.2383 | 0.0026 | 0.0328 | -0.0481 |
| 5 | -0.0823 | 0.3139 | 0.2628 | 0.2424 |

**within\_3d** per fold (columns: finalist family):

| fold | dummy\_median | forest\_reg | linear | tree\_reg |
| --- | --- | --- | --- | --- |
| 1 | 0.4528 | 0.5792 | 0.5860 | 0.5868 |
| 2 | 0.4059 | 0.5023 | 0.4956 | 0.5000 |
| 3 | 0.3495 | 0.4565 | 0.4584 | 0.4404 |
| 4 | 0.2995 | 0.4214 | 0.4340 | 0.4339 |
| 5 | 0.3684 | 0.5120 | 0.5313 | 0.5019 |

**Checks (A's s08 code)**

- PASS: finalists refitted on the same rows and folds reproduce their s06 fold scores (4 of 4 reproduced)
- PASS: finalists: the dummy, plain linear/logistic and single tree references plus each family's s07 carried model (4 finalists)
- PASS: no test row read: every row used was purchased before the test cutoff (latest purchase 2018-05-24 18:56:59, cutoff 2018-05-27 12:30:34)
- PASS: the run stops at the gate: no frozen\_recipe.json, the test cohort is not read (G-39, G-78) (team decisions in human\_decisions.yaml s08: not yet made)

## B8.A Adoption comparison and mean ± SE by population (G-79; Henry R-02)

**What was done:** Adoption comparison (G-79) on MAE days: A's frozen model (reg.sel.log.linear) refitted per fold on A's training rows vs B's recommended model (reg.sel.log.linear), both on B's validation rows. Mean paired gain of B over A +0.1176 days (paired SE 0.0594), B better in 5 of 5 folds; folds 2-5 (description only, B-G-01): +0.1467 days. By the fold rule B is adopted for regression; A and B both go to the joint test run. Mean and SE by population are in population\_summary.csv (R-02).

**Per fold, on B's validation rows** (adoption\_comparison.csv; positive gain = B better):

| fold | b\_rows | a\_model\_on\_b\_rows | b\_model\_on\_b\_rows | paired\_gain\_b\_over\_a |
| --- | --- | --- | --- | --- |
| 1 | 10,323 | 3.7238 | 3.7223 | 0.0015 |
| 2 | 10,364 | 5.5158 | 5.4678 | 0.0480 |
| 3 | 10,443 | 5.7551 | 5.6140 | 0.1411 |
| 4 | 10,429 | 7.1098 | 6.7724 | 0.3375 |
| 5 | 9,059 | 3.6070 | 3.5469 | 0.0601 |

**Decision record** (adoption\_decision.json): mean paired gain +0.1176 days (paired SE 0.0594), B better in 5 of 5 folds; folds 2–5 +0.1467 days (description only). Rule: B is adopted for the task when its 5-fold mean beats A's on the same B rows, even by a thin margin (G-79); folds 2-5 are description only (B-G-01); both go to the joint test run. Result: B adopted on the folds.

**Every finalist against A on the same rows** (adoption\_by\_finalist\_summary.csv): would B still be adopted if the team chose another finalist?

| candidate\_id | family | b\_mean | gain\_mean | gain\_se | folds\_b\_better | b\_adopted\_on\_folds\_if\_chosen |
| --- | --- | --- | --- | --- | --- | --- |
| reg.sel.log.dummy\_median | dummy | 5.9689 | -0.8266 | 0.1137 | 0 | False |
| reg.sel.log.linear | linear/logistic | 5.0247 | 0.1176 | 0.0594 | 5 | True |
| reg.sel.log.tree\_reg.max\_depth=5.min\_samples\_leaf=100 | single tree | 5.0532 | 0.0891 | 0.0791 | 3 | True |
| reg.sel.log.forest\_reg.max\_depth=10.max\_features=sqrt.min\_samples\_leaf=50 | forest | 4.9627 | 0.1796 | 0.0445 | 5 | True |

**Fold by fold, every finalist** (adoption\_by\_finalist.csv; gain > 0 = B better):

| candidate\_id | family | fold | a\_model\_on\_b\_rows | b\_model\_on\_b\_rows | paired\_gain\_b\_over\_a |
| --- | --- | --- | --- | --- | --- |
| dummy\_median | dummy | 1 | 3.7238 | 4.4073 | -0.6835 |
| dummy\_median | dummy | 2 | 5.5158 | 5.9751 | -0.4593 |
| dummy\_median | dummy | 3 | 5.7551 | 6.8000 | -1.0449 |
| dummy\_median | dummy | 4 | 7.1098 | 8.1627 | -1.0528 |
| dummy\_median | dummy | 5 | 3.6070 | 4.4995 | -0.8925 |
| linear | linear/logistic | 1 | 3.7238 | 3.7223 | 0.0015 |
| linear | linear/logistic | 2 | 5.5158 | 5.4678 | 0.0480 |
| linear | linear/logistic | 3 | 5.7551 | 5.6140 | 0.1411 |
| linear | linear/logistic | 4 | 7.1098 | 6.7724 | 0.3375 |
| linear | linear/logistic | 5 | 3.6070 | 3.5469 | 0.0601 |
| tree\_reg | single tree | 1 | 3.7238 | 3.6808 | 0.0430 |
| tree\_reg | single tree | 2 | 5.5158 | 5.1292 | 0.3866 |
| tree\_reg | single tree | 3 | 5.7551 | 5.7792 | -0.0241 |
| tree\_reg | single tree | 4 | 7.1098 | 7.0115 | 0.0983 |
| tree\_reg | single tree | 5 | 3.6070 | 3.6654 | -0.0584 |
| forest\_reg | forest | 1 | 3.7238 | 3.5846 | 0.1391 |
| forest\_reg | forest | 2 | 5.5158 | 5.2012 | 0.3146 |
| forest\_reg | forest | 3 | 5.7551 | 5.6926 | 0.0625 |
| forest\_reg | forest | 4 | 7.1098 | 6.8655 | 0.2444 |
| forest\_reg | forest | 5 | 3.6070 | 3.4698 | 0.1372 |

**Mean and SE by population** (population\_summary.csv):

| population\_and\_model | metric | mean\_5\_folds | se\_5\_folds | mean\_folds\_2\_5 | se\_folds\_2\_5 |
| --- | --- | --- | --- | --- | --- |
| A's frozen model on A's validation rows | mae | 5.4701 | 0.6733 | 5.8039 | 0.7549 |
| A's frozen model on B's validation rows | mae | 5.1423 | 0.6616 | 5.4969 | 0.7211 |
| B's recommended model (reg.sel.log.linear) on B's validation rows | mae | 5.0247 | 0.6115 | 5.3503 | 0.6682 |

**Per-fold decomposition** (se\_decomposition.csv): A on A's rows → A on B's rows isolates B's scope; A on B's rows → B on B's rows isolates B's features and prediction time.

| fold | a\_rows | b\_rows | a\_model\_on\_a\_rows | a\_model\_on\_b\_rows | b\_model\_on\_b\_rows |
| --- | --- | --- | --- | --- | --- |
| 1 | 12,820 | 10,323 | 4.1351 | 3.7238 | 3.7223 |
| 2 | 12,820 | 10,364 | 5.8682 | 5.5158 | 5.4678 |
| 3 | 12,818 | 10,443 | 6.0283 | 5.7551 | 5.6140 |
| 4 | 12,811 | 10,429 | 7.4957 | 7.1098 | 6.7724 |
| 5 | 10,740 | 9,059 | 3.8233 | 3.6070 | 3.5469 |

- PASS: A's frozen recipe unchanged: sha256 recomputes and A's selected spec matches it (sha256 df4beee32d7b…)
- PASS: A's refit reproduces A's stored s06 out-of-fold predictions on A's validation rows (max difference 7.11e-15)
- PASS: B's validation rows and labels are exactly B5's, in every fold (50,618 validation rows)

**Files**: pipeline\_b/stages/b08/regression/outputs/ (run 20261024T032040Z): adoption\_by\_finalist.csv, adoption\_by\_finalist\_summary.csv, adoption\_comparison.csv, adoption\_decision.json, candidates.csv, counts.json, decision.json, ladder.csv, metrics\_long.csv, population\_summary.csv, predictions.csv.gz, se\_decomposition.csv, selected\_spec.json, selection\_review\_pack.md; plus figures/ and curves/.
