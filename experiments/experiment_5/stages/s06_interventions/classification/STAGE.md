---
node: s06_interventions/classification
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s05_features/classification
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s06_interventions / classification - Interventions

Spec: `spec/pipeline_design.md` -> STAGE6. Teacher/TA rows: `spec/sources.md` (search `S06`).

**Gate question:** Is each added complexity justified one change at a time?

## Purpose
One-change-at-a-time ablations: input logs, unregularised vs finite-C logistic, single tree vs pruned tree vs starter forest.

## Planned outputs (`outputs/`)
- ablation.csv (unchanged/changed component, per-fold deltas, decision)
- metrics_long.csv
- decision.json

## Gate criteria
- Each added complexity justified by the protocol rule
- Simpler variant kept when the rule fails
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
