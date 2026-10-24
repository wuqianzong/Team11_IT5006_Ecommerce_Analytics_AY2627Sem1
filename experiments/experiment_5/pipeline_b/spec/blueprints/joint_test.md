# Joint test run — A and B, one test read (blueprint)

| Field | Value |
| --- | --- |
| Stage | T1 joint test run (G-79; A's 8.6–8.8 and B8.6–B8.8; CR-054 B-C13) |
| Nodes | regression, classification |
| Status | AGREED (experiment lead, 2026-10-24; J-1 = (a), the recommended option) |
| Inputs frozen | A: `../../stages/s08_selection/<task>/outputs/frozen_recipe.json` at e5-A-frozen; B: `stages/b08/<task>/outputs/frozen_recipe.json` at e5-B-frozen |

## 1. Goal and gate
Goal: score both frozen pipelines on the test cohort exactly once, in one run, with the agreed
metrics, plus A on B's test rows (like-for-like), and build the bundles for release.
Gate: the run refuses to start unless both frozen recipes exist and their sha256 values match the
tagged files; it reads the test cohort once and writes a test-read record; a second run that
reads the test again is a deviation and must be recorded as such.

## 2. Where the outputs go (changes the overview's step 7)
`pipeline_b/stages/t1_joint_test/<task>/outputs/`, with sub-results for A and B. A's frozen tree
(`../../stages/`) is **not** written, so A stays FRESH and matches e5-A-frozen. The overview tab
said "test outputs in both trees"; this blueprint replaces that with one joint folder (README rule 1:
B never writes in A's folders).

## 3. Method
1. **Check the freezes.** Recompute both sha256 values; refuse on any mismatch.
2. **Final fit (A 8.6, B8.6).** Each frozen recipe is fitted once on all its development orders
   whose labels were observable before the task's test cutoff (A: A's eligible development rows;
   B: B2 rows with the same label rule). Classification fits include the frozen calibration
   (sigmoid for both; B-G-05) with time-ordered inner splits, as in 8.3.
3. **Test rows.**
   - A: A's test cohort from `test_manifest.csv` (s05), unchanged.
   - B: A's test cohort filtered by B's population rules B-C1 to B-C5 (CR-054 §6). The B-C3 cap uses the
     value frozen from B's development rows (83.66 days, B2 feature_build_log.json), never
     recomputed on the test. Removal counts are recorded per rule.
   - B's history features for test rows use only events completed before each row's prediction week,
     as in B2. **Decision for the lead (J-1):** (a) the history includes events from earlier in the
     test period, as it would in deployment (recommended), or (b) the history is frozen at the test
     cutoff, which is more conservative but stale for later test weeks. Either way a row's own label
     is never used.
4. **Test once (A 8.7, B8.7).** Score with the G-24 metric list on:
   - A's model on A's test rows;
   - A's model on B's test rows;
   - B's model on B's test rows.
   References (dummy, plain linear/logistic) are refitted the same way. For classification, the
   frozen thresholds (1/6, cap 25) are applied to the calibrated probabilities; the confusion
   matrix, precision, recall, F1, alerts per day and illustrative cost are reported. The test-size
   checks G-46/G-54/G-75 are reported for B's test cohort, and a shortfall is reported, not fixed.
5. **Bundles (A 8.8, B8.8).** `joblib` pipeline, threshold, feature schema, package versions,
   training-ID digest, `training_profile.json` and checksums, for both A and B. B's bundle is the
   one released (G-79).
6. **Fold-by-fold and test table (B-C13).** One table per task: a row per validation fold (dates,
   festival weeks marked) and a test row, A and B side by side. Fold rows are labelled selection
   scores (G-10); only the test row is unbiased.

## 4. Outputs (per task)
`test_read.json` (time, row counts, sha256 of both recipes, "read once"), `test_rows_B.csv`
(B's test rows with removal reasons), `metrics_test.csv` (model × rows × metric),
`predictions_test.csv.gz`, `confusion_test.csv` (classification), `fold_and_test_table.csv`
(B-C13), bundles under `bundles/A/` and `bundles/B/`. Evidence IDs T1.1 to T1.6.

## 5. Checks
- Both recipes' sha256 equal the tagged files; no recipe field changes after the read.
- Test rows equal A's manifest (A) and A's manifest after B's rules (B); no development row is
  among them.
- B's test-row features use only events completed before each row's prediction week (the same
  brute-force check as B2.4/B2.5, on a sample).
- Reloading each bundle and re-predicting the test rows gives identical predictions (as A's 10.1).
- A's tree stays FRESH; A's code matches e5-A-frozen.

## 6. After the run
No model, calibration or threshold changes after the read (G-79: the test does not re-choose). A
later threshold change (Henry: "may adjust after s10") is reported as a post-test change, with the
frozen-threshold test result kept as the unbiased one. B9/B10 (conclusion and release) follow as one
combined blueprint: B gets the full analysis; A appears only as the baseline and in the comparison.
