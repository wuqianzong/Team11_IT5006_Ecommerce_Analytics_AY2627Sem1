# B5 — partition (blueprint)

| Field | Value |
| --- | --- |
| Stage | B5, Pipeline B |
| Nodes | regression, classification |
| Status | DRAFT |
| Inherits from A | s05 folds.csv (fold boundaries and membership), A's test manifest, A's minimums |

## 1. Goal and gate
Goal: keep A's five time-ordered folds, restricted to B's rows, so A and B are compared on the
same periods.
Gate: every B row sits in A's fold of the same order; minimums checked and any shortfall recorded.

## 2. Inputs
- A `stages/s05_partition/<task>/outputs/folds.csv` and `test_manifest.csv`.
- B2 `records_B.csv.gz`.

## 3. Method
1. B folds = A's folds ∩ B's development rows (order_id); no new boundaries.
2. Class support and size per fold against A's pre-registered minimums (protocol cv.minimums:
   10,000 training rows per fold; classification 100 detractors per training and validation part).

## 4. Outputs (per task, `pipeline_b/stages/b05/<task>/outputs/`)
`folds_B.csv`, `fold_summary_B.csv`, `checks.json`.

## 5. Checks
- Every B row keeps A's fold and role.
- No test row is in a B fold.
- Minimums: PASS, or the fold-1 training-row shortfall accepted under B-G-01 (within its
  safeguard floor); any other failure stops B5.

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
