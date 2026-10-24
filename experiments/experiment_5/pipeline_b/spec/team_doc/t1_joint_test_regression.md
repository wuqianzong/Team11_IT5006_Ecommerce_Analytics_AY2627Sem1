# T1 › regression

Single test read · run `20261024T044531Z` at 2026-10-24T04:45:19 UTC · 7 checks, all PASS · never rerun (a rerun would be a second test read). Coverage and review dropdowns are on the parent tab "T1 Joint test".

## T1.1 Freezes and test rows

**What was done:** Frozen recipes checked (A df4beee32d7b…, B 8f1241b5bc5f…). Test read once at 2026-10-24T04:45:19.920901+00:00: A 18,788 rows (s05 manifest); B 15,422 rows after B's rules (removed: B\_STATE 3,222; B\_DISTANCE 144). B's history features use every event completed before each row's prediction week (J-1 (a)).

From A's test cohort to B's test cohort (test\_rows\_B.csv):

| step | rows |
| --- | --- |
| A test rows (s05 test manifest) | 18,788 |
| removed: B\_STATE | 3,222 |
| removed: B\_DISTANCE | 144 |
| B test rows | 15,422 |

Test-size check for B's cohort (test\_size\_B.json; G-46 asks at least 15% of rows):

| item | value |
| --- | --- |
| b\_test\_rows | 15422.0000 |
| b\_final\_fit\_rows | 59683.0000 |
| b\_test\_share\_of\_fit\_plus\_test | 0.2053 |

- PASS: both frozen recipes recompute their sha256 (A e5-A-frozen, B e5-B-frozen) (A df4beee32d7b…, B 8f1241b5bc5f…)
- PASS: A's test rows equal A's s05 test manifest; B's test rows are a subset after B's rules; no development row among them (A 18,788, B 15,422 test rows)
- PASS: leakage re-check on B's test rows: features recomputed by brute force from events in weeks before the prediction week match (300 rows, max difference 0.00e+00)
- PASS: no recipe field changed after the read: both frozen recipes still recompute the same sha256
- PASS: A's tree untouched: A's code matches e5-A-frozen after the run

## T1.2 Final fits

**What was done:** Final fits on development rows with labels observable before the cutoff: A 74,834 rows, B 59,683 rows; frozen recipes; dummies refitted the same way.

- PASS: every final-fit row has a label observable before the test cutoff (A 74,834, B 59,683 rows)

## T1.3 Test metrics (every G-24 metric)

**What was done:** Test MAE: A on A's rows 4.3364; A on B's rows 4.0280; B on B's rows 3.2992. All G-24 metrics in metrics\_test.csv.

&#91;embedded content: metrics\_test.csv · T1 run 20261024T044531Z · test MAE by model and rows\]

Full table (metrics\_test.csv). "Plain reference" = the linear recipe from A's s04 / B's B4, refitted the same way; "dummy" = the B4/s04 dummy. Threshold-dependent metrics use 1/6 for every model.

| metric | A on A's rows | A on B's rows | B on B's rows | A plain reference | B plain reference | A dummy | B dummy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| mae | 4.3364 | 4.0280 | 3.2992 | 4.3364 | 3.2992 | 4.8755 | 4.3849 |
| rmse | 5.7289 | 5.3586 | 4.7750 | 5.7289 | 4.7750 | 6.2614 | 5.7088 |
| r2 | 0.0340 | -0.0265 | 0.1849 | 0.0340 | 0.1849 | -0.1540 | -0.1651 |
| within\_3d | 0.4138 | 0.4429 | 0.5755 | 0.4138 | 0.5755 | 0.3213 | 0.3710 |
| n\_rows | 18788.0000 | 15422.0000 | 15422.0000 | 18788.0000 | 15422.0000 | 18788.0000 | 15422.0000 |

&#91;image: test\_metrics\_comparison\]

Errors on B's test rows (figures/test\_errors.csv summarises them):

&#91;image: test\_errors\]

## T1.5 Bundles

**What was done:** Bundles for A and B (model.joblib, schema.json, training\_profile.json); reload parity {'A': True, 'B': True}. B's bundle is the release (G-79).

| Item | A bundle | B bundle (release, G-79) |
| --- | --- | --- |
| model | reg.sel.log.linear | reg.sel.log.linear |
| frozen sha256 | `df4beee32d7b6bef…` | `8f1241b5bc5fdc27…` |
| features (numeric + categorical) | 14 + 4 | 18 + 3 |
| calibration | None | None |
| threshold |  |  |
| training rows | 74,834 | 59,683 |
| versions | sklearn 1.9.0, pandas 3.0.1, numpy 2.4.2 | same |

Files: bundles/A|B/model.joblib, schema.json, training\_profile.json; checksums in \_manifest.json.

- PASS: each bundle reloads and re-predicts the test rows identically ({'A': True, 'B': True})

## T1.6 Fold by fold and test (B-C13)

**What was done:** Fold-by-fold (selection scores) and test (unbiased) table for A and B, festival days marked (fold\_and\_test\_table.csv).

&#91;embedded content: fold\_and\_test\_table.csv · T1 run 20261024T044531Z (folds from b08 metrics\_by\_population\_folds.csv)\]

Fold rows are selection scores (G-10): the models were chosen on them, so they are optimistic. Only the test row is unbiased. Folds are B5's validation blocks; festival days inside a block are marked.

| period | kind | start | end | festival\_days | metric | A\_on\_A\_rows | A\_on\_B\_rows | B\_on\_B\_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fold 1 | validation (selection score, G-10) | 2017-06-19 | 2017-09-27 | nan | mae | 4.1351 | 3.7238 | 3.7223 |
| fold 2 | validation (selection score, G-10) | 2017-09-27 | 2017-12-03 | 2017-11-24 | mae | 5.8682 | 5.5158 | 5.4678 |
| fold 3 | validation (selection score, G-10) | 2017-12-03 | 2018-02-05 | 2017-12-25 | mae | 6.0283 | 5.7551 | 5.6140 |
| fold 4 | validation (selection score, G-10) | 2018-02-05 | 2018-04-01 | nan | mae | 7.4957 | 7.1098 | 6.7724 |
| fold 5 | validation (selection score, G-10) | 2018-04-01 | 2018-05-24 | nan | mae | 3.8233 | 3.6070 | 3.5469 |
| test | test (unbiased, read once) | 2018-05-27 | 2018-08-29 | nan | mae | 4.3364 | 4.0280 | 3.2992 |

&#91;image: fold\_and\_test\]

**Files**: pipeline\_b/stages/t1\_joint\_test/regression/outputs/ (run 20261024T044531Z): bundles/A/model.joblib, bundles/A/schema.json, bundles/A/training\_profile.json, bundles/B/model.joblib, bundles/B/schema.json, bundles/B/training\_profile.json, fold\_and\_test\_table.csv, metrics\_test.csv, predictions\_test.csv.gz, test\_read.json, test\_rows\_B.csv, test\_size\_B.json; plus figures/.
