---
node: s07_tuning/regression
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s06_training/regression
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s07_tuning / regression - Tuning

Spec: `spec/pipeline_design.md` -> s07. Teacher/TA rows: `spec/sources.md` (search `S07`).
Blueprint: `spec/blueprints/s07_tuning.md` (implement only when its status is AGREED).

**Gate question:** Is every tuned candidate a complete pipeline scored on the same folds?

## Purpose
Bounded grids on the same folds: Ridge alpha; tree depth and leaf; forest depth and leaf. Every candidate a whole pipeline.

## Planned outputs (`outputs/`)
- grid_results.csv (every config: params, fold scores, mean, SD, rank, runtime, convergence)
- predictions.csv.gz (out-of-fold, finalists)

## Gate criteria
- Grids taken from protocol.yaml
- No configuration switched after the search
- Pooled out-of-fold and mean-fold scores kept distinct
<!-- END GENERATED -->

## Working log (README section 9.1; one row per solution ID, every code change names its ID)
| ID | What was built | Commit | Evidence (files, figures) | Coverage | Round |
| --- | --- | --- | --- | --- | --- |

## Review rounds (append-only; each round has review/round_N/ and a section in the doc tab)
| Round | Commit | Run ID | Review pack | Outcome | Date |
| --- | --- | --- | --- | --- | --- |

## Accepted result (the only result the report and slides may cite)
- Accepted round: - commit: - run ID: - approved by: - date:

## Deviations from blueprint
None.

## Open questions
