# B5 — partition (blueprint)

| Field | Value |
| --- | --- |
| Stage | B5, Pipeline B |
| Nodes | regression, classification |
| Status | AGREED (experiment lead, 2026-10-24) |
| Inherits from A | s05 folds.csv (fold boundaries and membership), A's test manifest, A's minimums |

## 1. Goal and gate
Goal: keep A's five time-ordered folds, restricted to B's rows, so A and B are compared on the
same periods.
Gate: every B row sits in A's fold of the same order; minimums checked and any shortfall recorded.

## 2. Inputs
- A `stages/s05_partition/<task>/outputs/folds.csv` (order_id, fold, role, purchase_ts) and
  `test_manifest.csv`, at tag e5-A-frozen.
- B2 `records_B.csv.gz` (current run in `../../EVIDENCE.md`).

## 3. Method
1. **B folds = A's folds ∩ B's development rows**, joined on order_id. Each (fold, role) row of A
   is kept when its order is a B row; no new boundaries, no re-purging, no re-ordering. An order
   keeps every (fold, role) it has in A (expanding windows).
2. **B rows outside A's folds** (removed by A's customer purge or label-maturity rules) are not
   used; they are listed with reason `NOT_IN_A_FOLDS` in `exclusions_B5.csv` and counted.
3. **Sizes and class support per fold and role**, against A's minimums (protocol cv.minimums:
   10,000 training rows per fold; classification 100 detractors in each training and validation
   part) and the B-G-01 safeguard (fold 1: at least 5,000 training rows; classification at least
   300 training detractors).
4. **Date ranges** per fold and role from B's rows, next to A's boundaries, so the periods can be
   checked as identical.

## 4. Outputs (per task, `pipeline_b/stages/b05/<task>/outputs/`)
`folds_B.csv` (order_id, fold, role, purchase_ts), `fold_summary_B.csv` (per fold: A's boundaries,
B train/validation rows, B dates, classification detractors and prevalence, A's rows for
comparison), `exclusions_B5.csv`, `minimums_B.csv` (each minimum, observed value, PASS / ACCEPTED
DEVIATION (B-G-01) / FAIL). Evidence IDs: B5.1 fold membership, B5.2 sizes and class support,
B5.3 minimums and safeguard.

## 5. Checks
- Every B fold row exists in A's folds.csv with the same fold and role.
- No B fold row is in A's test manifest; every B fold order is a B2 development row.
- B5 rows + `NOT_IN_A_FOLDS` rows = B2 rows.
- Minimums: PASS, or fold 1's training-row shortfall accepted under B-G-01 within its safeguard;
  any other failure, or a safeguard breach, stops B5.
- Two runs give byte-identical outputs.

## 5a. Pre-build measurement (2026-10-23, for this approval only)
Computed directly from A's folds.csv ∩ the current B2 records, not a stage output. B5's own
`fold_summary_B.csv` becomes the evidence once it runs.

| Task | Fold 1 training rows | Fold 1 training detractors | Smallest validation part | B2 rows outside A's folds |
| --- | --- | --- | --- | --- |
| regression | 7,932 (minimum 10,000; safeguard 5,000) | — | 9,059 rows (fold 5) | 1,550 |
| classification | 7,592 (minimum 10,000; safeguard 5,000) | 874 (safeguard 300) | 873 detractors (fold 5) | 2,076 |

The safeguard holds in both tasks, so B5 does not stop. Fold 1 is the only part below a
minimum, which is the shortfall B-G-01 accepts; folds 2–5 meet 10,000 training rows, and every
classification part keeps at least 100 detractors.

## 6. Decision: fold 1 below the minimum (B-G-01, 2026-10-23)
Fold 1 is expected to fall below 10,000 training rows once B's scope removes about a fifth of
the orders. **Decided by the experiment lead: keep A's five folds unchanged and accept fold 1's
shortfall as a recorded deviation** (as G-75 for A's test check), so the A–B comparison stays on
identical periods and G-79's 5-fold mean is unchanged. Not chosen: dropping fold 1 (loses a
fifth of the evidence and changes A's accepted 5-fold basis) and merging folds 1–2 for B only
(breaks the like-for-like comparison).

Safeguards:
1. B5 measures the real sizes. If fold 1 has fewer than 5,000 training rows, or (classification)
   fewer than 300 training detractors, B5 stops and the team decides again; the 100-detractor
   minimum per part still applies as a hard check.
2. The observed counts are written into `human_decisions_B.yaml` b05 once B5 has run.
3. B8 shows the adoption comparison on all five folds (the decision) and on folds 2–5
   (description only).
