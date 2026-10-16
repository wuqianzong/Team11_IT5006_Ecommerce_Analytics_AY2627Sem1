---
node: s07_tuning/classification
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s06_interventions/classification
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s07_tuning / classification - Tuning

Spec: `spec/pipeline_design.md` -> STAGE7. Teacher/TA rows: `spec/sources.md` (search `S07`).

**Gate question:** Is the winner a complete pipeline, compared with dummy and simplest family?

## Purpose
Bounded grid search over COMPLETE pipelines on selection folds using protocol.yaml grids; compare the winner with dummy and simplest family on identical rows.

## Planned outputs (`outputs/`)
- grid_results.csv (every config: params, fold scores, mean, SD, rank, runtime, convergence)
- predictions.csv.gz (OOF of finalists)
- selected_spec.json
- decision.json

## Gate criteria
- No post-search configuration switch
- Pooled OOF vs mean-fold kept distinct
- Winner compared with baselines
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
