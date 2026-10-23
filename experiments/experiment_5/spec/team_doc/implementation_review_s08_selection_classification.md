# s08 Selection › classification — evidence cards

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
