---
node: s07_tuning/classification
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s06_training/classification
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s07_tuning / classification - Tuning

Spec: `spec/pipeline_design.md` -> s07. Teacher/TA rows: `spec/sources.md` (search `S07`).
Blueprint: `spec/blueprints/s07_tuning.md` (implement only when its status is AGREED).

**Gate question:** Is every tuned candidate a complete pipeline scored on the same folds?

## Purpose
Bounded grids on the same folds: logistic C; tree depth and leaf; forest depth and leaf; class weight None vs balanced. Every candidate a whole pipeline.

## Planned outputs (`outputs/`)
- grid_results.csv (every config: params, fold scores, mean, SD, rank, runtime, convergence)
- predictions.csv.gz (out-of-fold, finalists)

## Gate criteria
- Grids taken from protocol.yaml
- No configuration switched after the search
- Pooled out-of-fold and mean-fold scores kept distinct
<!-- END GENERATED -->

## Review summary (owner fills at gate; cite files, never type numbers from memory)
- What was done:
- Decision and rule applied (`outputs/decision.json`):
- Key evidence (file -> what it shows):
- Limitations:

## Gate check (reviewer)
- [ ] Every gate criterion above is met (note any exception)
- [ ] `run_pipeline.py run --node` reproduces all outputs from a clean tree
- [ ] Standard output shapes and `_manifest.json` present (README section 5.5)

## Deviations from spec
None.

## Open questions

## Sign-off
- Accepted by: - date: - commit: -
