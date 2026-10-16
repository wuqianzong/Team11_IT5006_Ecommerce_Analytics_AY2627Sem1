---
node: s11_deployment/common
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s10_benchmark/regression
  - s10_benchmark/classification
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s11_deployment / common - Deployment

Spec: `spec/pipeline_design.md` -> STAGE11. Teacher/TA rows: `spec/sources.md` (search `S11`).

**Gate question:** Does the app load the same artifact and reproduce its predictions?

## Purpose
Reload bundles, verify in-memory vs reloaded parity, validate single/batch/missing/invalid/unknown inputs; Streamlit app with two task tabs using held-out records as simulated orders.

## Planned outputs (`outputs/`)
- app/ (Streamlit app code; runs from this node folder, loads S10 bundles from their outputs/)
- parity.json
- input_validation.json
- app instructions + screenshots

## Gate criteria
- App loads the S10 bundle unchanged
- Inference never fits
- App and bundles stay inside experiments/experiment_5/ (no deployment/ changes before migration)
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
