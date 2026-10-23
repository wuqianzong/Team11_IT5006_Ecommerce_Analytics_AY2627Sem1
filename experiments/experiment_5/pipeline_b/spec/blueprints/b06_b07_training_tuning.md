# B6–B7 — training and tuning (blueprint)

| Field | Value |
| --- | --- |
| Stage | B6, B7, Pipeline B (G-79) |
| Nodes | regression, classification |
| Status | AGREED (experiment lead, 2026-10-24) |
| Inherits from A | everything: `e5lib/training.py` and `e5lib/tuning.py` (their `run()` functions, unchanged), families, s06 settings, s07 grids, one-SE rule, metrics, seed 42, A's s06-D1 to D4 and s07-D1 to D4 |

## 1. Goal and gate
Goal: run A's training ladder (s06) and tuning (s07) on B's rows, recipes and folds, with **A's
own code paths**, so the only differences between A and B are the inputs CR-054 changes.
Gate: as A's s06 and s07; in addition, an equivalence test shows the B runner reproduces A's
accepted s06 and s07 outputs when it is fed A's inputs.

## 2. Inputs (current runs in `../../EVIDENCE.md`)
- B4 `recipes_B.json`, `selected_features_B.json`.
- B5 `folds_B.csv` (A's folds restricted to B rows; fold 1 under B-G-01).
- B2 `records_B.csv.gz` (B's development rows; only rows in `folds_B.csv` are used).
- A's protocol settings and grids (`../../spec/protocol.yaml`, read-only, tag e5-A-frozen).

## 3. Method
1. **Same code, other inputs (no copy).** A's `training.run(task)` and `tuning.run(task)` read
   their inputs through four functions: `data.upstream`, `data.load`, `cv.folds` and
   `outputs.Writer`. B's runner (`e5b/adapter.py`) calls A's `run()` unchanged and supplies only
   these four for the duration of the call:
   - `upstream` maps s04 → B4 (`recipes_B.json`, `selected_features_B.json`) and s06 → B6;
   - `load("records", …, "development")` returns B2's rows that are in B5's folds;
   - `folds` yields B5's (fold, train ids, validation ids) in A's format;
   - `Writer` is B's writer: outputs go to `pipeline_b/stages/b06|b07/<task>/outputs/` and
     evidence IDs get a "B" prefix (6.2 → B6.2).
   The originals are restored after the call, even on error. No line of A's orchestration is
   copied into B.
2. **B6** = A's s06 on B's inputs: dummy, plain linear/logistic, single tree, forest; the
   basic-to-complex ladder under the one-SE rule; paired gains as description; residual and
   classification diagnostics; learning curves.
3. **B7** = A's s07 on B's inputs: A's grids per family; one-SE choice inside each grid and
   against the plain B6 model (G-55).
4. **No new choices.** A's s06 and s07 decisions apply unchanged. If B's results hit a condition
   A's code flags for a human (for example a chosen value on a grid edge), the run reports it and
   the lead decides; nothing is changed silently.

## 4. Outputs
As A's s06 and s07 (metrics_long.csv, predictions, candidates.csv, decision.json, grid_results.csv,
figures and curves), under `pipeline_b/stages/b06/<task>/outputs/` and `b07/<task>/outputs/`, with
evidence IDs B6.x and B7.x and B's manifest (inputs listed by B path).

## 5. Checks
- All of A's s06 and s07 checks, run by A's code on B's inputs.
- **Equivalence test** (`tests/test_adapter.py`): the adapter fed A's own inputs (A's s04 recipes,
  A's s05 folds, A's records) gives `metrics_long.csv` and `decision.json` identical to A's
  accepted s06 outputs at e5-A-frozen; same for s07 `grid_results.csv` on one family. This proves
  the adapter changes nothing but the inputs.
- After the call the four functions are A's originals again; A's tree stays FRESH
  (`run_pipeline.py status`), and A's code matches e5-A-frozen (`assert_a_frozen`).
- Every B6/B7 row comes from a B5 fold; no test row is read.
- Two runs give identical outputs.

## 6. Reviews
The experiment lead accepts B6 and B7 after a brief review. The team reviews B6–B8 together at the
B8 gate (as G-78), where the A–B adoption comparison (G-79) is made.

## 7. Cost note
B's folds hold fewer rows than A's (B5 fold_summary_B.csv), so B7 runs no longer than A's s07. It runs in the background.
