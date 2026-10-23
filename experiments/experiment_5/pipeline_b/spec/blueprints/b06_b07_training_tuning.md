# B6–B7 — training and tuning (blueprint)

| Field | Value |
| --- | --- |
| Stage | B6, B7, Pipeline B |
| Nodes | regression, classification |
| Status | DRAFT |
| Inherits from A | everything: e5lib/training.py and tuning.py, families, s06 settings, s07 grids, one-SE rule, metrics, seed 42 |

## 1. Goal and gate
Goal: run A's training ladder and tuning, unchanged, on B's rows, recipes and folds.
Gate: same as A's s06 and s07; only the inputs differ.

## 2. Inputs
B4 `recipes_B.json`, B5 `folds_B.csv`, B2 `records_B.csv.gz`, A's protocol settings and grids.

## 3. Method
- B6: dummy, plain linear/logistic, single tree, forest; the basic-to-complex ladder under the
  one-SE rule; paired gains as description; residual and classification diagnostics; learning
  curves (A's s06 code, read-only).
- B7: A's grids per family; one-SE choice inside each grid and against the plain B6 model (G-55)
  (A's s07 code, read-only).

## 4. Outputs
As A's s06 and s07, under `pipeline_b/stages/b06/` and `b07/`, with evidence IDs B6.x and B7.x.

## 5. Checks
As A's s06 and s07, plus: the code imported from e5lib matches A's foundation hash at e5-A-frozen.

## 6. Reviews
The experiment lead accepts B6 and B7 after a brief review; the team reviews B6–B8 together at
the B8 gate (as G-78).
