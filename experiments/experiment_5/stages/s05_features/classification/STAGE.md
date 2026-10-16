---
node: s05_features/classification
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s04_baselines/classification
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s05_features / classification - Features

Spec: `spec/pipeline_design.md` -> STAGE5. Teacher/TA rows: `spec/sources.md` (search `S05`).

**Gate question:** Do expansions help with estimator and preprocessing fixed?

## Purpose
Diagnose baselines (AP/PR, ROC, Brier, prevalence, reliability) and compare core 9 vs 12 features with estimator and preprocessing held fixed; permutation importance on validation rows of a named model.

## Planned outputs (`outputs/`)
- metrics_long.csv
- paired_deltas.csv (per fold)
- figures/
- importance.csv (states which candidate it explains)
- decision.json

## Gate criteria
- Only features change between paired candidates
- Importance attributed to the right model
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
