# Handshake for Benson: reworked Phase 2 report from Pipeline A (DRAFT, 2026-10-29)

Henry is writing a reworked Phase 2 (Milestone 2) technical report built only on Pipeline A, to send to the
instructor himself. It reads stored outputs only: no rerun of any stage, no refit, no change to `stages/`, the tags
or the release record. Every number comes through the register as a `{{id}}` placeholder. Four decisions and two
new stored outputs are needed from you.

## Decisions

**M2-D1. Read A's s01 and s04–s08 outputs.** B-G-11 (s03) and B-G-13 (s02) let B's register read A's files at tag
`e5-A-frozen`, sha256 checked, A's evidence ID carried. Extend the same rule to A's s01 and s04–s08 outputs: the
task contract, feature pool, transforms, reductions, selection ranking, folds, training ladder and paired
differences, learning curves, tuning grids and validation curves, finalists, calibration and threshold table.
Proposed decision id: B-G-14.

**M2-D2. Where the sources live.** Proposed: `pipeline_b/deliverables/m2_report/` (markdown sections, same fill and
audit as the final report), with Henry as owner, and the new register items in `evidence/registry_B.yaml` under
an `M2.` prefix. Or tell us another place inside `experiments/experiment_5/`.

**M2-D3. Audit coverage.** Should `audit_deliverables_B.py` also check the M2 report (doc export against the filled
sources, charts byte for byte), or is the fill/check step enough for this document?

**M2-D4. Test results in the M2 report.** The report would show A's frozen, plain and dummy models on A's own test
rows (T1, `metrics_test.csv`, `A test rows`), labelled as read once in the joint test read. Agree?

## New stored outputs (from the frozen A models; no refit)

**M2-N1. A's interpretation.** For A's frozen regression and classification models, on A's test rows:
permutation importance (same method and scoring as B9's `permutation_importance.csv`) and the coefficients /
odds ratios (as B9's `coefficients.csv`), each with a figure.

**M2-N2. A's error analysis.** For A's frozen models on A's test rows: errors by customer state (MAE and share
within 3 days; precision and recall at 1/6), with the same judged-slice rule as B9 (at least 100 test orders, or
100 detractors), and a residuals figure for A on A's rows (T1's `test_errors` covers B's rows only).

**M2-N3. A-only test charts.** Every T1 chart draws A and B together (`fold_and_test`, `test_curves`,
`confusion_test`, `test_metrics_comparison`, `test_errors`), so none can go in a report that shows only Pipeline A.
Needed, redrawn from the stored T1 and s06 data with A's rows only: validation folds and test for A (MAE; AP);
precision–recall, ROC and reliability curves on A's test rows; A's confusion matrix at 1/6; and train, validation
and test side by side for A's dummy, plain and frozen models.

These would sit in a small A-side stage of your choosing (for example `pipeline_b/stages/m2a/`) with `EVIDENCE.md`
entries, so the register can read them as a Current run.

## Not needed

Everything else is already stored: T1 has A's test metrics, confusion matrix at 1/6 and fold-and-test table on
A's rows; B9's `train_val_test.csv` and `threshold_options.csv` carry A's rows.
