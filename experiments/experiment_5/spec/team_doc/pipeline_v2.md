# Pipeline v2 — textbook order (frozen)

Oct 17, 2026 · @B

**Frozen on 17 Oct 2026** as the Experiment 5 design v1.0 (`spec/pipeline_design.md`, `spec/stages.json`, change CR-001). From now on, changes go through a change request in `CHANGELOG.md`. There is no target cap (CR-005), and the log transforms are fixed from EDA (CR-016).

One pass in ten steps, following the team's order and the Tutorial 7–8 workflow; no second training cycle. Every Milestone 2 method is kept and moved into this flow; amber marks one that stays but is corrected, blue marks something Milestone 2 lacked.

&#91;embedded content: Pipeline v2 · 10 steps, one pass\]

**Chart box to solution IDs.** A step box gets a ✓ when every ID listed for it is approved in its implementation review. A stage is ACCEPTED only when all its IDs are approved, including the stage-level IDs that have no box.

| Stage | Chart boxes → solution IDs | Stage-level IDs (no box) |
| --- | --- | --- |
| 1 Problem | Two tasks at checkout → 1.1 · Stakeholder and action → 1.2 · Targets and label rules → 1.3 · Metrics and 5:1 cost → 1.4, 1.5 | 1.6–1.9 |
| 2 Data | Load and clean 9 tables → 2.1–2.3 · Join, aggregate per order → 2.4–2.6 · Leakage audit, removal rules → 2.7–2.11, 2.13 | 2.12 |
| 3 EDA | Target shape and tails → 3.1, 3.2 · Outcome trends over time → 3.3 · Feature-target relationships → 3.4–3.7 · Missingness, outliers and collinearity → 3.8 | 3.9 (human gate) |
| 4 Features | Feature baseline → 4.1 · Log inputs and target → 4.2 · Feature reduction → 4.3 · Feature selection by EDA ranking → 4.4, 4.7 · Rationale and citations → 4.6 · Pipeline: impute, encode, scale → 4.8 | — (4.5 retired) |
| 5 Partition | Partition strategy against leakage → 5.1 · Hold out test, purge customers → 5.2–5.4 · Chronological expanding folds → 5.5 · Customer purge, label maturity → 5.6, 5.7 · Class support per fold → 5.8 · Seed 42, documented → 5.5 | — |
| 6 Training | Same features, logs on, all models → 6.1 · Dummy, plain linear/logistic, single tree, random forest → 6.2 · Residuals and learning curves → 6.5–6.7 | 6.4, 6.8 (6.3 retired) |
| 7 Tuning | Linear family → 7.1, 7.2 · Tree family → 7.3 · Forest → 7.4 · Class weight → 7.2–7.4 · Whole pipelines, same folds → 7.5 | 7.6, 7.7 |
| 8 Selection | Finalists vs baselines → 8.1, 8.2 · Calibration check → 8.3 · Threshold from OOF, 5:1 cost → 8.4 · Final fit, test once → 8.5–8.7 | 8.8 |
| 9 Conclusion | Train-val-test table → 9.1, 9.2 · Subgroup errors and drift → 9.3, 9.4 · Interpretation → 9.5 · Stakeholder actions, limits → 9.7, 9.8 | 9.6 |
| 10 Release | Saved bundle, reload parity → 10.1 · Approve → 10.2 · Migrate → 10.3 · Reproduction check → 10.4 · Streamlit app and dashboard → 10.5, 10.6 · Input checks → 10.5 · Report, slides → 10.7 · Walkthrough notebook → 10.8 | 10.9 |

The test cohort is held out in step 5, and steps 3–4 already exclude its dates (each task's newest 20%, cutoff computed in step 2), so EDA and feature work never see its outcomes; anything learned from data (imputation, encoding, scaling) is fitted inside the folds in step 6.

## Flags

**Dropped from Milestone 2**

- Two training cycles → one basic-to-complex ladder in step 6.
- Customer-grouped CV screening beside chronological confirmation → chronological folds only.
- A separate confirmation window → not needed; CV folds plus one test, as in Tutorials 7–8.
- Starting from 9 features → step 4 starts from the 24-predictor contract (G-61), reduces it, then selects one set per task by the EDA ranking; step 6 uses that set for every model.
- Cook's distance as the reason for the 60-day cap → no target cap; extreme lead times are handled by the step 2 outlier rule and the log target.

**Corrected (amber)**

- Step 1: stakeholders were only named; state who sees which prediction, when, and what they do. Keep the minimum-review label, with a first-review sensitivity check.
- Step 2, leakage audit: `order_estimated_delivery_date` is known at checkout; Milestone 2 wrongly listed it as post-checkout.
- Step 4: three Milestone 2 citations could not be traced; verify or drop them. One pipeline recipe per model (impute, encode, scale) replaces Milestone 2's several builders and post-search switches; it is defined here and fitted only inside the folds.
- Step 5: the test cohort is held out here, with its dates already excluded from steps 3–4; chronological expanding folds replace grouped CV.
- Step 6: dummies are fitted on the same folds (Milestone 2 drew them from separate evidence); the log target and input logs are fixed from EDA in step 4, not added after tuning.
- Step 7: every grid candidate is a whole pipeline on the same folds; class weight (None vs balanced) is one grid option for the classifiers.
- Step 8: finalists are compared with the baselines on the same rows; calibration uses out-of-fold predictions, not a separate grouped study; one threshold replaces Milestone 2's 0.17 vs 0.1822.
- Step 9: importance explains the selected model; recommendations stay within the evidence (Milestone 2's hubs, buffers and vouchers were never tested).
- Step 10: once the experiment is approved, it is migrated to the working folders with a reproduction README; only after the reproduction check matches the release do the dashboard, report and slides get built, citing the reproduced outputs and never typed numbers.

**Audit fixes (design v1.1, CR-003):** each task has its own test cohort, and development orders from its customers are removed. The final fit uses only labels available before the test cutoff. Cross-validation scores are reported as selection scores only. The reduction from the 24 eligible predictors to a core set is a declared label-free exception. Partition depends only on the data step. Training compares families only; the feature set and log transforms are fixed in step 4. Calibration is a candidate component. Using `order_estimated_delivery_date` as a candidate feature was proposed, then dropped on 18 Oct (G-35).

**Evidence rule (design rule 8, CR-013, proposed):** every step, the reproduction in step 10 included, stores its results as files that can be read without rerunning any model. This covers the intermediate evidence behind each decision as well as the final choice:

- every candidate's per-fold scores and out-of-fold predictions, every grid cell, and each rejected option with its reason (`candidates.csv`);
- threshold, calibration, learning and validation curves as data (`curves/*.csv`), and EDA tables;
- every figure as PNG plus a sidecar file with the plotted data;
- fitted bundles for the finalists and the release model;
- `decision.json` naming the files each decision used.

Nothing is overwritten: earlier runs stay retrievable by commit and release tag, and files over 50 MB are kept on the shared drive with their hash. The report, slides, app and dashboard read these stored files through the evidence registry, never a fresh run.

**Order check:** features come before partition, matching the team's order (Tutorial 7's reference splits first). It stays leak-free because steps 3–4 use only pre-test dates, step 4 defines recipes without fitting, and every model-based choice happens on the folds in steps 6–7.

**Test cohort:** each task's newest 20%, defined and scored only in this experiment. Experiment 5 is independent of earlier milestones, so it is a new held-out test (G-38).
