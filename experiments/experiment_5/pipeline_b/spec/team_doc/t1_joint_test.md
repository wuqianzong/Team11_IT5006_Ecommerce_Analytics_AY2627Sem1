# T1 Joint test — A and B, one test read

**Test read once · 2026-10-24 · runs `20261024T044531Z` (regression) and `20261024T044555Z` (classification) · 7 + 7 checks, all PASS · never rerun.** Blueprint spec/blueprints/joint\_test.md (AGREED; J-1 = (a): B's history features for a test row use every event completed before that row's prediction week, including earlier test weeks, as in deployment). Code: pipeline\_b/e5b/t1\_joint\_test.py. The run was made on HEAD e4fa1a6 with the T1 code not yet committed; each manifest records the sha256 of the code that ran, and tests/test\_evidence\_register.py checks the committed code against it (EVIDENCE.md). A's frozen tree was not written (A stays at e5-A-frozen). Before the read, the T1 row builder was checked on development rows: with B2's events it reproduces records\_B.csv.gz exactly (0 differing values, both tasks).

## Headline (metrics\_test.csv; CV means from b08 metrics\_by\_population.csv, sigmoid for classification)

| Task | Metric | A on A's test rows | A on B's test rows | B on B's test rows | B minus A on B's rows | CV mean, A on B's rows (B8) | CV mean, B on B's rows (B8) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| regression | MAE (lower is better) | 4.3364 | 4.0280 | 3.2992 | -0.7288 | 5.1423 | 5.0247 |
| classification | AP (higher is better) | 0.1750 | 0.1785 | 0.1972 | +0.0187 | 0.2302 | 0.2482 |

## What the test says, for decisions and the report

1. **B is confirmed on the test, both tasks, on the same rows.** Regression: B's MAE is 0.7288 days lower than A's on B's test rows (CV gain on the same comparison was 0.1176). Classification: B's AP is +0.0187 higher (CV +0.0180).
2. **The regression gain on the test is larger than in CV.** Possible reasons, not tested here: B's route history is recent (weeks before the prediction week, J-1 (a)), and the test period is the newest, faster period (G-77 drift; no festival week in the test block). The report states the CV gain and the test gain side by side and does not claim the test gain as the expected gain.
3. **Classification is harder on the test for every model**: AP falls from about 0.23–0.25 in CV to 0.178–0.197. Test prevalence is 9.9% on B's rows (1,541 detractors) and 10.4% on A's rows (G-75, G-77).
4. **Alert volume at the frozen threshold 1/6 (cap 25/day).** B: 23.2 alerts/day on its test rows (out-of-fold at the gate 17.0), within the cap. A: 51.1/day on A's rows and 36.1/day on B's rows (out-of-fold at its gate 23.9), above the cap. G-79: the test does not re-choose the threshold; a later change is reported as a post-test change.
5. **Illustrative cost (5 per missed detractor, 1 per false alert).** B 7,156 vs 7,705 for alerting nobody on B's rows. A 10,253 vs 9,840 for alerting nobody on A's rows: at this cost ratio A's alerts cost more than they save on the test.
6. **References.** Regression: the frozen models are the plain linear recipes (log target), so "plain" equals "frozen". Classification: B's plain logistic (no calibration) has AP 0.1992 vs 0.1972 for the frozen sigmoid model, and Brier 0.0864 vs 0.0867: calibration does not change the ranking much. Both beat the dummy.
7. **Test size (G-46).** B's test cohort is 20.5% (regression) and 20.7% (classification) of final-fit plus test rows, and holds 16.0% of B's detractors (1,541): all at least 15%. Confidence intervals for the test metrics (G-54) are not in this run; they are computed in B9–B10 from predictions\_test.csv.gz without refitting.
8. **Bundles.** A's and B's bundles reload and re-predict the test rows identically. B's bundle is the release (G-79).

## Coverage

| Task | Evidence | Status | Review |
| --- | --- | --- | --- |
| regression | T1.1 | IMPLEMENTED | Open |
| regression | T1.2 | IMPLEMENTED | Open |
| regression | T1.3 | IMPLEMENTED | Open |
| regression | T1.5 | IMPLEMENTED | Open |
| regression | T1.6 | IMPLEMENTED | Open |
| classification | T1.1 | IMPLEMENTED | Open |
| classification | T1.2 | IMPLEMENTED | Open |
| classification | T1.3 | IMPLEMENTED | Open |
| classification | T1.4 | IMPLEMENTED | Open |
| classification | T1.5 | IMPLEMENTED | Open |
| classification | T1.6 | IMPLEMENTED | Open |

## Next

B9–B10 (combined, B primary, A as baseline): interpretation, error analysis by state / route / distance, test CIs (G-54), train–validation–test table (this tab's T1.6), business impact, limitations, deployment from B's bundle. Documentation gaps in DOC\_GAPS.md follow the pipeline.
