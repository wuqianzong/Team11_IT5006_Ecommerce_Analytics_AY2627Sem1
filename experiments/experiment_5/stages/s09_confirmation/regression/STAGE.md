---
node: s09_confirmation/regression
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s08_policy/regression
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s09_confirmation / regression - Confirmation

Spec: `spec/pipeline_design.md` -> STAGE9. Teacher/TA rows: `spec/sources.md` (search `S09`).

**Gate question:** Does the frozen method hold up without being changed?

## Purpose
Fit frozen recipes at confirmation start; evaluate the reserved confirmation window for the selected pipeline AND dummy / plain-linear / simple-tree references on identical rows.

## Planned outputs (`outputs/`)
- metrics_long.csv (phase=confirmation)
- predictions.csv.gz
- figures/
- decision.json (accept / reopen)

## Gate criteria
- Recipe unchanged from S08
- Matched references included
- Reopen documented in CHANGELOG if triggered
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
