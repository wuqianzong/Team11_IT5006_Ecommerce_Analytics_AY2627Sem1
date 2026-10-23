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
- Minimums: PASS, or FAIL recorded with the team's decision.

## 6. Open question for the team
**Fold 1 is expected to fall below 10,000 training rows** once B's scope removes about a fifth
of the orders (the exact count comes from B5's own run). Options:
(a) accept it as a recorded deviation and keep A's five folds unchanged, so the A–B comparison
stays on identical periods (proposed; like G-75 for A's test check); (b) drop fold 1 and compare
on four folds for both pipelines; (c) merge folds 1 and 2 for B only, which breaks the
like-for-like comparison. The decision goes into `human_decisions_B.yaml` b05.
