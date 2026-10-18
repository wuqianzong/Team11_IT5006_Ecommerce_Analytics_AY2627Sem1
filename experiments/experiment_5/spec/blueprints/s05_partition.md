# s05_partition — blueprint

| Field | Value |
| --- | --- |
| Stage | s05_partition (`../pipeline_design.md` → s05) |
| Nodes | regression, classification |
| Status | AGREED |
| Owner | TBD |
| Last agreed | 2026-10-18 (wording, CR-018; audit 2, CR-021; audit 3, CR-022); first 2026-10-17 (team walkthrough, doc tab "Feature solution (s02–s05)") |
| Discussion | Claude Doc "Milestone 3 pipeline stages", tab "Feature solution (s02–s05)", section s05 |

## 1. Goal and gate
Goal: hold out each task's test cohort by time, keep test customers out of training, and build
five time-ordered CV folds with no customer, time or label-timing leakage.
Gate: folds chronological, customers purged, labels mature, classes supported (`../stages.json`).

## 2. Inputs
- `stages/s02_data/common/outputs/records.csv.gz` (task-eligible rows, after all s02 rules).
- `spec/protocol.yaml`: per-task test cutoff (computed in s02), number of folds (5), minimum
  training rows per fold, minimum positives per fold, seed 42.
- Depends on s02 only (not on s03–s04).

## 3. Method
1. **Order (5.1).** Sort each task's eligible orders by purchase timestamp, earliest first.
2. **Test cohort (5.2).** Orders on or after the task's s02 cutoff (the 80% position, G-28); exact
   `order_id`s frozen in `test_manifest.csv`. The cohort is defined only by this experiment's
   data and rules (G-38).
3. **Test-side purge (5.3, G-18).** Remove test orders whose `customer_unique_id` appears in
   development; log the count. The test cohort is new customers only and is named everywhere a
   "new-customer time-ordered holdout", always stated with its actual share of eligible orders
   after the purge and the share the purge removed (G-48).
4. **Test checks (5.4), per task (G-46).** Regression: test keeps ≥ 15% of eligible delivered
   orders. Classification: test keeps ≥ 15% of eligible reviewed orders and ≥ 15% of all eligible
   detractors. Report the train–test prevalence gap. On failure: alert and stop. Never a random split.
5. **CV folds (5.5).** Five expanding, time-ordered folds on development (`TimeSeriesSplit`
   style, equal-sized validation blocks by order count); boundary dates written to
   `protocol.yaml`. Anti-temporal-leakage rule: training holds only orders purchased before the
   validation block starts.
6. **Fold customer purge (5.6).** In each fold, remove training orders whose `customer_unique_id`
   appears in that validation block.
7. **Label maturity (5.7).** A label counts only from when it was observable (`lead_days` at
   delivery, `is_detractor` at the last review answer). Training rows: label observable before
   their fold's validation block starts. Validation rows: label observable before the task's test
   cutoff. Dropped rows counted per fold.
8. **Class support and training size (5.8).** Every fold's training part holds at least the
   minimum number of rows pre-registered in `protocol.yaml`, for both tasks (G-53).
   Classification also: positives and prevalence per fold, training and validation; minimum
   count from `protocol.yaml`. A boundary may move only before s06 runs, logged in CHANGELOG.

## 4. Decisions
| ID | Question | Answer | Basis | Status |
| --- | --- | --- | --- | --- |
| s05-D1 | Test cutoff | 80/20 per task, computed in s02 | G-28 | Agreed |
| s05-D2 | Test-boundary purge side | Remove from test | G-18 | Agreed |
| s05-D3 | Fold purge side | Remove from training | Keeps validation blocks complete in time | Agreed |
| s05-D4 | CV window | Five expanding folds, equal-sized blocks | G-23 | Agreed |
| s05-D5 | Label timing | As step 7 | Label-timing leakage rule | Agreed |
| s05-D6 | Random fallback | Never; alert and stop | Teacher pitfall | Agreed |

## 5. Outputs (per task, under `stages/s05_partition/<task>/outputs/`)
- `test_manifest.csv`: `order_id`, `customer_unique_id`, `purchase_ts`.
- `folds.csv`: `order_id`, `fold`, `role` (train / validation), `purchase_ts`.
- `counts.json`: rows, customers, positives per fold and per cohort; purge and maturity drops;
  test share of eligible orders after the purge (G-48).
- `checks.json`: per-fold assertions and results; test-size and review-share checks.

## 6. Checks (asserted, run fails if any is false)
- No test `order_id` or `customer_unique_id` in development.
- Every fold: max training purchase time < min validation purchase time.
- Every fold: no shared `customer_unique_id` between training and validation.
- Every fold: every training label observable before the validation block starts.
- Every fold, both tasks: training rows ≥ the pre-registered minimum (G-53).
- Classification: both classes present in every fold's training and validation parts, at or
  above the minimum count.
- Test size checks per task as step 4 (G-46).

## 7. Milestone 2 reuse
`src/models/refinement_temporal.py` (window, purge and maturity logic) copied into `e5lib/cv.py`
with a provenance comment. Change when copying: test-side purge instead of development-side;
equal-sized blocks instead of calendar windows; no Milestone 2 dates or counts.

## 8. Report hooks
Validation design section: partition diagram, fold sizes and prevalence, purge and maturity
counts, test-cohort description.

## 9. Open questions
None.
