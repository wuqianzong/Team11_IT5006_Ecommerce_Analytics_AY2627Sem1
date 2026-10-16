---
node: s02_partitions/classification
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s01_records/common
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s02_partitions / classification - Partitions

Spec: `spec/pipeline_design.md` -> STAGE2. Teacher/TA rows: `spec/sources.md` (search `S02`).

**Gate question:** Are windows chronological, customers purged, labels mature and both classes supported?

## Purpose
Freeze selection folds (four earlier expanding windows), the confirmation window (last pre-terminal window) and the Milestone 2 terminal benchmark manifest; customer purge and label maturity at every fit origin.

## Planned outputs (`outputs/`)
- selection_folds.csv
- confirmation_manifest.csv
- benchmark_manifest.csv
- counts.json (rows, customers, positives per fold/population)
- checks.json (overlap, maturity, class support)

## Gate criteria
- No Milestone 2 held-out IDs in development
- Training outcomes available before each fit origin
- Customers purged across train/validation
- Both classes present in every fold (classification)
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
