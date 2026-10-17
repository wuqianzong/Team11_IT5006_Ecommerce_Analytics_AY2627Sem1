---
node: s08_selection/regression
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s07_tuning/regression
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s08_selection / regression - Selection

Spec: `spec/pipeline_design.md` -> s08. Teacher/TA rows: `spec/sources.md` (search `S08`).
Blueprint: `spec/blueprints/s08_selection.md` (implement only when its status is AGREED).

**Gate question:** Was the recipe frozen before the test cohort was scored once?

## Purpose
Select the model on threshold-free scores against the dummy and simplest models; freeze the recipe; fit on development orders with labels available before the test cutoff; score the test cohort once.

## Planned outputs (`outputs/`)
- selected_spec.json
- threshold_table.csv (classification: no alerts, 0.50, 0.17, empirical optimum)
- frozen_recipe.json
- bundle/ (pipeline, threshold, schema, versions, training-ID digest, checksums)
- metrics_long.csv (phase = test) + predictions.csv.gz

## Gate criteria
- Model selected before the threshold
- Persisted probability recipe is the one the threshold was chosen on
- Final-fit training labels available before the test cutoff
- Recipe and threshold frozen before the test cohort is read
- Test cohort scored once
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
