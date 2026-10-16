---
node: s08_policy/regression
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s07_tuning/regression
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s08_policy / regression - Policy

Spec: `spec/pipeline_design.md` -> STAGE8. Teacher/TA rows: `spec/sources.md` (search `S08`).

**Gate question:** Is the recipe (and probability/threshold policy) frozen before confirmation?

## Purpose
Learning curves, interpretation (simple-tree rules, permutation importance of the selected model) and error profile; freeze the regression recipe before confirmation.

## Planned outputs (`outputs/`)
- learning_curve.csv + figures
- calibration.csv (classification)
- threshold_table.csv (classification: counts, precision, recall, F1, alerts, cost)
- frozen_recipe.json
- decision.json

## Gate criteria
- Probability recipe frozen before threshold (classification)
- Recipe frozen before S09
- No confirmation/benchmark labels used
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
