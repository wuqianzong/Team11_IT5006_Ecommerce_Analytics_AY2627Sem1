# s08 Selection › regression — evidence cards

## Supplement for decisions and the report (added 2026-10-24; DOC\_GAPS D-05)

Added after the pipeline ran, from accepted outputs only; nothing above is changed. Source: A's s08 outputs at e5-A-frozen (run 20261023T084947Z).

**Per-fold MAE of every finalist** (A's s08 metrics\_long.csv; selection scores):

| candidate\_id | phase | fold\_1 | fold\_2 | fold\_3 | fold\_4 | fold\_5 | mean | se |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| reg.sel.log.dummy\_median | train | 5.0603 | 4.9911 | 4.9709 | 5.5825 | 5.9542 | 5.3118 | 0.1960 |
| reg.sel.log.dummy\_median | validation | 5.0057 | 6.4689 | 7.2540 | 8.6627 | 5.0815 | 6.4946 | 0.6889 |
| reg.sel.log.forest\_reg.max\_depth=10.max\_features=sqrt.min\_samples\_leaf=50 | train | 4.3092 | 4.0878 | 4.0226 | 4.5311 | 4.8477 | 4.3597 | 0.1513 |
| reg.sel.log.forest\_reg.max\_depth=10.max\_features=sqrt.min\_samples\_leaf=50 | validation | 4.1162 | 5.6428 | 6.1800 | 7.4963 | 3.7815 | 5.4434 | 0.6826 |
| reg.sel.log.linear | train | 4.2016 | 3.9941 | 3.9369 | 4.4836 | 4.8148 | 4.2862 | 0.1632 |
| reg.sel.log.linear | validation | 4.1351 | 5.8682 | 6.0283 | 7.4957 | 3.8233 | 5.4701 | 0.6733 |
| reg.sel.log.tree\_reg.max\_depth=5.min\_samples\_leaf=100 | train | 4.3040 | 4.0893 | 4.0242 | 4.5133 | 4.8356 | 4.3533 | 0.1481 |
| reg.sel.log.tree\_reg.max\_depth=5.min\_samples\_leaf=100 | validation | 4.1141 | 5.6875 | 6.1600 | 7.5600 | 3.6002 | 5.4244 | 0.7147 |

Round 1 · run `20261021T050311Z` · 4 checks, all PASS · gate part only: 8.5–8.8 are not built until the team's combined review of s06–s08 (G-78). Coverage and review dropdowns are on the parent tab "s08 Selection"; comment on any card here.

## 8.1 Finalists

**Approved solution:** Each family's best from s07, plus the dummy and the plain linear/logistic and single-tree references from s06, compared on the same rows and folds (fold mean and standard error; paired per-fold differences shown as description)

**What was done:** 4 finalists refitted on the five s05 folds: dummy (s06 reference) 6.4946 ± 0.6889 days; linear/logistic (s06 reference) 5.4701 ± 0.6733 days; single tree (s06 reference) 5.4244 ± 0.7147 days; forest (s07 carried (plain s06)) 5.4434 ± 0.6826 days (validation mae, mean ± SE).

**Finalists, validation MAE (days), mean ± SE over the five folds** (candidates.csv):

| family | source | validation\_mean | validation\_se | train\_validation\_gap | grid\_edge | recommended |
| --- | --- | --- | --- | --- | --- | --- |
| dummy | s06 reference | 6.4946 | 0.6889 | 1.1828 | not a grid configuration (dummy) | False |
| linear/logistic | s06 reference | 5.4701 | 0.6733 | 1.1839 | plain s06 model, not a grid configuration | True |
| single tree | s06 reference | 5.4244 | 0.7147 | 1.0711 | none | False |
| forest | s07 carried (plain s06) | 5.4434 | 0.6826 | 1.0837 | none | False |

&#91;image: Finalists, regression\]

**Check** finalists refitted on the same rows and folds reproduce their s06 fold scores: PASS (4 of 4 reproduced) **Check** finalists: the dummy, plain linear/logistic and single tree references plus each family's s07 carried model: PASS (4 finalists) **Check** no test row read: every row used was purchased before the test cutoff: PASS (latest purchase 2018-05-24 18:56:59, cutoff 2018-05-27 12:30:34)

**Files** (stages/s08\_selection/regression/outputs/, run 20261021T050311Z): candidates.csv, counts.json, figures/finalists.csv, figures/finalists.json, figures/finalists.png, metrics\_long.csv, predictions.csv.gz

## 8.2 Choose the model

**Approved solution:** One-standard-error rule (1.7) on the primary metric (MAE / AP): the simplest finalist whose mean is within one standard error of the best mean is the recommendation. The final choice is a human gate (G-39): the run stops and presents a selection pack, then the team confirms or overrides in spec/human\_decisions.yaml with its rationale. An override is a protocol deviation: logged as a CR in CHANGELOG, with the one-SE choice shown beside it in the report and slides (G-44). The pack holds each finalist's fold mean ± standard error on all s01 metrics, the train–validation gap and learning curves, plus a flag when a chosen setting sits at a grid edge. A grid-edge choice is resolved by the team, never silently: either widen that grid (change request; s07 reruns and keeps all configurations) or revisit s03–s04. Validation scores are reported as selection scores, not generalisation

**What was done:** One-SE recommendation: linear/logistic (best mean: single tree). Ladder basic to complex: linear/logistic kept over dummy (paired gain +1.0245 days, better in 5 of 5 folds); single tree not kept over linear/logistic (paired gain +0.0458 days, better in 3 of 5 folds); forest not kept over linear/logistic (paired gain +0.0267 days, better in 3 of 5 folds); ladder result linear/logistic. Grid edge of the recommendation: plain s06 model, not a grid configuration.

**Reasoning:** The recommendation follows the pre-registered rule; the team confirms or overrides it at the gate (G-39), and an override is logged as a protocol deviation (G-44). Validation scores are selection scores, not generalisation estimates (G-10).

**Conclusion:** The run stops here. Under G-78 the team reviews s06, s07 and s08 together before the freeze, the final fit and the single test (8.5-8.8).

**Every s01 metric, mean and SE over the folds** (candidates.csv):

| family | mae\_mean | mae\_se | r2\_mean | r2\_se | rmse\_mean | rmse\_se | within\_3d\_mean | within\_3d\_se |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dummy | 6.4946 | 0.6889 | -0.1355 | 0.0415 | 9.5348 | 1.1572 | 0.3390 | 0.0229 |
| linear/logistic | 5.4701 | 0.6733 | 0.0911 | 0.0729 | 8.5785 | 1.1785 | 0.4654 | 0.0256 |
| single tree | 5.4244 | 0.7147 | 0.0975 | 0.0761 | 8.5599 | 1.2074 | 0.4730 | 0.0303 |
| forest | 5.4434 | 0.6826 | 0.0971 | 0.0728 | 8.5599 | 1.1951 | 0.4583 | 0.0229 |

**Ladder, basic to complex** (ladder.csv; paired gains are description only):

| comparison | gain\_fold\_1 | gain\_fold\_2 | gain\_fold\_3 | gain\_fold\_4 | gain\_fold\_5 | mean\_gain | paired\_se | folds\_better | kept\_by\_one\_se\_rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear/logistic vs dummy | 0.8707 | 0.6007 | 1.2257 | 1.1670 | 1.2582 | 1.0245 | 0.1262 | 5 | True |
| single tree vs linear/logistic | 0.0210 | 0.1807 | -0.1317 | -0.0643 | 0.2231 | 0.0458 | 0.0685 | 3 | False |
| forest vs linear/logistic | 0.0189 | 0.2254 | -0.1517 | -0.0007 | 0.0418 | 0.0267 | 0.0601 | 3 | False |

**Check** no test row read: every row used was purchased before the test cutoff: PASS (latest purchase 2018-05-24 18:56:59, cutoff 2018-05-27 12:30:34) **Check** the run stops at the gate: no frozen\_recipe.json, the test cohort is not read (G-39, G-78): PASS (team decisions in human\_decisions.yaml s08: not yet made)

**Files** (stages/s08\_selection/regression/outputs/, run 20261021T050311Z): candidates.csv, counts.json, decision.json, figures/finalists.csv, figures/finalists.json, figures/finalists.png, ladder.csv, selected\_spec.json, selection\_review\_pack.md

## 8.5 Freeze

**Approved solution:** Write frozen\_recipe.json (features, transforms, recipe, estimator and settings, calibration, threshold) with its hash, before the test cohort is read

**Round 2 (2026-10-23), run `20261023T082458Z`.** **What was done:** Recipe frozen for reg.sel.log.linear: 14 numeric and 4 categorical features, estimator linear, calibration none; sha256 df4beee32d7b6bef5736e21e53aad6b1caea3233a066c222e46708aca38899d2. Written from development rows only; the test cohort is not loaded. **Conclusion:** Pipeline A stops after the freeze. The final fit, the single test read and the bundle (8.6–8.8) run together with Pipeline B (lead decision 2026-10-23; draft G-79). **Check** frozen recipe follows the team decisions (chosen model is a finalist and the recommendation): PASS (reg.sel.log.linear). **Check** frozen before any test row is read (development rows only, all purchased before the cutoff): PASS. **Files:** frozen\_recipe.json, decision.json, counts.json, selection\_review\_pack.md

## 8.6 Final fit

**Approved solution:** Fit the frozen recipe on all development orders whose labels were observable before the test cutoff

**Not built (MISSING by design).** Runs only after the team's combined review of s06–s08 has filled spec/human\_decisions.yaml s08.regression (G-39, G-78); the freeze is written before the test cohort is read.

## 8.7 Test once

**Approved solution:** Score each task's test cohort once with the agreed metric list (G-24), including the dummy and plain linear/logistic references refitted the same way for comparison

**Not built (MISSING by design).** Runs only after the team's combined review of s06–s08 has filled spec/human\_decisions.yaml s08.regression (G-39, G-78); the freeze is written before the test cohort is read.

## 8.8 Bundle

**Approved solution:** joblib pipeline, threshold, feature schema, package versions, training-ID digest, training\_profile.json (numeric distributions, category shares) for drift checks, checksums

**Not built (MISSING by design).** Runs only after the team's combined review of s06–s08 has filled spec/human\_decisions.yaml s08.regression (G-39, G-78); the freeze is written before the test cohort is read.
