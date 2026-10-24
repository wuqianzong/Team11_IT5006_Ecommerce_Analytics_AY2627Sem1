# T1 › classification

Single test read · run `20261024T044555Z` at 2026-10-24T04:45:37 UTC · 7 checks, all PASS · never rerun (a rerun would be a second test read). Coverage and review dropdowns are on the parent tab "T1 Joint test".

## T1.1 Freezes and test rows

**What was done:** Frozen recipes checked (A 8de9d4f13159…, B da056ab74eff…). Test read once at 2026-10-24T04:45:37.575137+00:00: A 18,966 rows (s05 manifest); B 15,492 rows after B's rules (removed: B\_STATE 3,252; B\_DISTANCE 144; B\_REVIEW\_BEFORE\_HANDOVER 42; B\_NO\_HANDOVER 36). B's history features use every event completed before each row's prediction week (J-1 (a)).

From A's test cohort to B's test cohort (test\_rows\_B.csv):

| step | rows |
| --- | --- |
| A test rows (s05 test manifest) | 18,966 |
| removed: B\_STATE | 3,252 |
| removed: B\_DISTANCE | 144 |
| removed: B\_REVIEW\_BEFORE\_HANDOVER | 42 |
| removed: B\_NO\_HANDOVER | 36 |
| B test rows | 15,492 |

Test-size check for B's cohort (test\_size\_B.json; G-46 asks at least 15% of rows and of detractors):

| item | value |
| --- | --- |
| b\_test\_rows | 15492.0000 |
| b\_final\_fit\_rows | 59188.0000 |
| b\_test\_share\_of\_fit\_plus\_test | 0.2074 |
| b\_test\_detractors | 1541.0000 |
| b\_dev\_detractors | 8063.0000 |
| b\_test\_detractor\_share | 0.1605 |

- PASS: both frozen recipes recompute their sha256 (A e5-A-frozen, B e5-B-frozen) (A 8de9d4f13159…, B da056ab74eff…)
- PASS: A's test rows equal A's s05 test manifest; B's test rows are a subset after B's rules; no development row among them (A 18,966, B 15,492 test rows)
- PASS: leakage re-check on B's test rows: features recomputed by brute force from events in weeks before the prediction week match (300 rows, max difference 0.00e+00)
- PASS: no recipe field changed after the read: both frozen recipes still recompute the same sha256
- PASS: A's tree untouched: A's code matches e5-A-frozen after the run

## T1.2 Final fits

**What was done:** Final fits on development rows with labels observable before the cutoff: A 74,970 rows, B 59,188 rows; frozen recipes with sigmoid calibration (B-G-05); dummies refitted the same way.

- PASS: every final-fit row has a label observable before the test cutoff (A 74,970, B 59,188 rows)

## T1.3 Test metrics (every G-24 metric)

**What was done:** Test AP: A on A's rows 0.1750; A on B's rows 0.1785; B on B's rows 0.1972. All G-24 metrics in metrics\_test.csv.

&#91;embedded content: metrics\_test.csv · T1 run 20261024T044555Z · test AP by model and rows\]

Full table (metrics\_test.csv). "Plain reference" = the logistic recipe from A's s04 / B's B4, refitted the same way; "dummy" = the B4/s04 dummy. Threshold-dependent metrics use 1/6 for every model (the plain logistic is not calibrated, so its threshold metrics are not like-for-like).

| metric | A on A's rows | A on B's rows | B on B's rows | A plain reference | B plain reference | A dummy | B dummy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ap | 0.1750 | 0.1785 | 0.1972 | 0.1775 | 0.1992 | 0.1038 | 0.0995 |
| roc\_auc | 0.5952 | 0.6040 | 0.6360 | 0.5995 | 0.6341 | 0.5000 | 0.5000 |
| brier | 0.0933 | 0.0893 | 0.0867 | 0.0935 | 0.0864 | 0.0948 | 0.0909 |
| precision | 0.1526 | 0.1583 | 0.2077 | 0.1507 | 0.2258 | 0.0000 | 0.0000 |
| recall | 0.3801 | 0.3556 | 0.3005 | 0.3740 | 0.2544 | 0.0000 | 0.0000 |
| f1 | 0.2178 | 0.2191 | 0.2456 | 0.2148 | 0.2392 | 0.0000 | 0.0000 |
| alerts\_per\_day | 51.0521 | 36.0625 | 23.2188 | 50.8854 | 18.0833 | 0.0000 | 0.0000 |
| alert\_rate | 0.2584 | 0.2235 | 0.1439 | 0.2576 | 0.1121 | 0.0000 | 0.0000 |
| tp | 748.0000 | 548.0000 | 463.0000 | 736.0000 | 392.0000 | 0.0000 | 0.0000 |
| fp | 4153.0000 | 2914.0000 | 1766.0000 | 4149.0000 | 1344.0000 | 0.0000 | 0.0000 |
| fn | 1220.0000 | 993.0000 | 1078.0000 | 1232.0000 | 1149.0000 | 1968.0000 | 1541.0000 |
| tn | 12845.0000 | 11037.0000 | 12185.0000 | 12849.0000 | 12607.0000 | 16998.0000 | 13951.0000 |
| cost | 10253.0000 | 7879.0000 | 7156.0000 | 10309.0000 | 7089.0000 | 9840.0000 | 7705.0000 |
| prevalence | 0.1038 | 0.0995 | 0.0995 | 0.1038 | 0.0995 | 0.1038 | 0.0995 |
| n\_pos | 1968.0000 | 1541.0000 | 1541.0000 | 1968.0000 | 1541.0000 | 1968.0000 | 1541.0000 |
| n\_rows | 18966.0000 | 15492.0000 | 15492.0000 | 18966.0000 | 15492.0000 | 18966.0000 | 15492.0000 |

&#91;image: test\_metrics\_comparison\]

## T1.4 Classification at the frozen threshold (1/6 on sigmoid probabilities, cap 25 alerts/day)

**What was done:** At the frozen threshold 1/6 on sigmoid probabilities, B's test rows: A precision 0.158, recall 0.356; B precision 0.208, recall 0.300, 23.2 alerts/day (cap 25).

&#91;embedded content: metrics\_test.csv · T1 run 20261024T044555Z · alerts/day, precision, recall at 1/6; cap 25 from frozen\_recipe.json\]

Confusion matrices on B's test rows (confusion\_test.csv):

| model | threshold | tn | fp | fn | tp |
| --- | --- | --- | --- | --- | --- |
| A frozen | 0.1667 | 11,037 | 2,914 | 993 | 548 |
| B frozen | 0.1667 | 12,185 | 1,766 | 1,078 | 463 |

&#91;image: confusion\_test\]

PR, ROC and reliability on B's test rows:

&#91;image: test\_curves\]

## T1.5 Bundles

**What was done:** Bundles for A and B (model.joblib, schema.json, training\_profile.json); reload parity {'A': True, 'B': True}. B's bundle is the release (G-79).

| Item | A bundle | B bundle (release, G-79) |
| --- | --- | --- |
| model | clf.sel.log.logistic | clf.sel.log.logistic |
| frozen sha256 | `8de9d4f13159db2d…` | `da056ab74eff0957…` |
| features (numeric + categorical) | 16 + 3 | 23 + 2 |
| calibration | sigmoid | sigmoid |
| threshold | 0.1667 | 0.1667 |
| training rows | 74,970 | 59,188 |
| versions | sklearn 1.9.0, pandas 3.0.1, numpy 2.4.2 | same |

Files: bundles/A|B/model.joblib, schema.json, training\_profile.json; checksums in \_manifest.json.

- PASS: each bundle reloads and re-predicts the test rows identically ({'A': True, 'B': True})

## T1.6 Fold by fold and test (B-C13)

**What was done:** Fold-by-fold (selection scores) and test (unbiased) table for A and B, festival days marked (fold\_and\_test\_table.csv).

&#91;embedded content: fold\_and\_test\_table.csv · T1 run 20261024T044555Z (folds from b08 metrics\_by\_population\_folds.csv, sigmoid)\]

Fold rows are selection scores (G-10): the models were chosen on them, so they are optimistic. Only the test row is unbiased. Folds are B5's validation blocks; festival days inside a block are marked.

| period | kind | start | end | festival\_days | metric | A\_on\_A\_rows | A\_on\_B\_rows | B\_on\_B\_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fold 1 | validation (selection score, G-10) | 2017-06-17 | 2017-09-26 | nan | ap | 0.1480 | 0.1361 | 0.1468 |
| fold 2 | validation (selection score, G-10) | 2017-09-26 | 2017-12-02 | 2017-11-24 | ap | 0.2322 | 0.2320 | 0.2575 |
| fold 3 | validation (selection score, G-10) | 2017-12-02 | 2018-02-04 | 2017-12-25 | ap | 0.2345 | 0.2390 | 0.2641 |
| fold 4 | validation (selection score, G-10) | 2018-02-04 | 2018-03-31 | nan | ap | 0.3221 | 0.3273 | 0.3411 |
| fold 5 | validation (selection score, G-10) | 2018-03-31 | 2018-05-23 | nan | ap | 0.2218 | 0.2165 | 0.2316 |
| test | test (unbiased, read once) | 2018-05-26 | 2018-08-29 | nan | ap | 0.1750 | 0.1785 | 0.1972 |

&#91;image: fold\_and\_test\]

**Files**: pipeline\_b/stages/t1\_joint\_test/classification/outputs/ (run 20261024T044555Z): bundles/A/model.joblib, bundles/A/schema.json, bundles/A/training\_profile.json, bundles/B/model.joblib, bundles/B/schema.json, bundles/B/training\_profile.json, confusion\_test.csv, fold\_and\_test\_table.csv, metrics\_test.csv, predictions\_test.csv.gz, test\_read.json, test\_rows\_B.csv, test\_size\_B.json; plus figures/.
