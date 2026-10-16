---
node: s10_benchmark/classification
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s09_confirmation/classification
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s10_benchmark / classification - Benchmark

Spec: `spec/pipeline_design.md` -> STAGE10. Teacher/TA rows: `spec/sources.md` (search `S10`).

**Gate question:** Is the confirmed recipe refitted unchanged and scored once?

## Purpose
Refit the unchanged recipe on all eligible pre-terminal training; score the Milestone 2 terminal benchmark once; subgroup and error analysis; persist complete bundles.

## Planned outputs (`outputs/`)
- bundle/ (pipeline, calibrator, threshold, schema, versions, training-ID digest, checksums)
- metrics_long.csv (phase=benchmark)
- predictions.csv.gz
- subgroups.csv

## Gate criteria
- Benchmark scored once per release
- Benchmark described as historical, not unseen
- Bundle is the exact evaluated artifact
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
