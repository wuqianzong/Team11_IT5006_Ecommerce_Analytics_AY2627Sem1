---
node: s03_eda/classification
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s02_partitions/classification
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s03_eda / classification - EDA

Spec: `spec/pipeline_design.md` -> STAGE3. Teacher/TA rows: `spec/sources.md` (search `S03`).

**Gate question:** Does every planned change follow from an observed, selection-only finding?

## Purpose
Question-driven EDA on SELECTION data only: missingness, distributions/tails, seasonality, geography/basket relations, feature-target associations, linear design rank. Produce a small declared set of candidate changes.

## Planned outputs (`outputs/`)
- figures/*.png + sidecar json
- candidate_rationale.csv (change, observation, literature, hypothesis, stage to test)
- eda_summary.json

## Gate criteria
- Only the selection population loaded
- Each proposed change linked to an observation
- Nothing fitted on all development and fed into CV
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
