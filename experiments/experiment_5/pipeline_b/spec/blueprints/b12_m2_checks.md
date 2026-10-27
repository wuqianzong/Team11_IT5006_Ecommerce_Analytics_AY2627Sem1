# B12 — Milestone 2 feedback checks: feature-ranking stability and promise buffers (blueprint)

| Field | Value |
| --- | --- |
| Stage | B12, Pipeline B (answers the Milestone 2 TA feedback, points 3 and 10; docs/Project/Milestone2/TA feedback for milestone 2.md) |
| Nodes | regression (B12.1, B12.2), classification (B12.1) |
| Status | AGREED (experiment lead, 2026-10-27: "build the feature-ranking stability check and the buffer curve as a small analysis stage, then cut e5-release-2 before migration") |
| Inputs frozen | B2, B4, B5, B8 accepted runs; T1 at e5-T1-tested (EVIDENCE.md); release e5-release-1 |

## 0. Scope

Description only. Nothing here changes a feature set, model, calibration or threshold, refits a frozen
recipe, or reads the test cohort again (G-79). B12.1 uses development rows only. B12.2 reads labels
already saved in T1's `predictions_test.csv.gz` and in B8's out-of-fold predictions, as B9 and B10 did.
The outputs go into the report's limitations and business sections and the dashboard; they are cut into
release `e5-release-2`.

## 1. B12.1 Feature-ranking stability inside the folds (TA point 3)

The TA asked for feature screening under the same chronological, customer-purged CV as tuning and
selection. B4 ranks features once on all development rows (a declared design exception, README §8
rule 4). B12.1 measures how much that choice matters.

1. **Reproduce.** Recompute B4's ranking, reduction and 99% selection on all of B2's development rows
   with B4's own functions; it must give B4's accepted selected set exactly (otherwise stop).
2. **Per fold.** Repeat it on each fold's training rows only (B5 `folds_B.csv`, role train).
3. **Report** per fold: features selected, Jaccard overlap with B4's set, features added and dropped,
   Spearman correlation of the importance ranks with B4's, and the rank of each B4-selected feature;
   across folds, how often each feature is selected.

Reading: high overlap means screening on pooled development rows did not drive the selected set. A
feature that enters or leaves in some folds is listed. Selection scores are not recomputed and the
models are not refitted (that would re-choose after the test).

## 2. B12.2 Promise-buffer curve (TA point 10; regression)

The TA asked that buffer sizes be derived, not asserted.

1. **Residual** e = actual − predicted lead days (positive = later than promised).
2. **Curve** for buffers 0 to 30 days in steps of 0.5 (validation residuals are heavy-tailed, B9.16): share of orders arriving after prediction +
   buffer (late), for B on its validation rows (B8 out-of-fold, the frozen recipe), B on its test rows,
   A on B's test rows and A on its own test rows (T1).
3. **Buffer chosen on validation, read on test.** For on-time targets of 90% and 95%, the smallest
   buffer on the grid whose validation late share is at most 10% (5%); then the test late share at
   that buffer. Choosing on validation and reading on test keeps the test unbiased for this choice.
4. **By customer state** (B's seven states, at least 100 test orders): late share at both buffers.

## 3. Outputs (per task, `pipeline_b/stages/b12/<task>/outputs/`)

`ranking_stability_by_fold.csv`, `ranking_stability_features.csv`, `ranking_stability.json`;
regression also `buffer_curve.csv`, `buffer_choice.csv`, `buffer_by_state.csv`, figures
`ranking_stability` and `buffer_curve` with sidecar data. Evidence IDs B12.1, B12.2.

## 4. Checks

- The full-development recomputation equals B4's accepted selection (B4 `selected_features_B.json`).
- Every fold uses training rows only, and no test row is read for B12.1.
- B12.2's B test residuals equal those behind B9.16 (late shares at 3 and 6 days equal `residuals_summary.csv`).
- A's tree matches e5-A-frozen.
