---
node: s04_features/regression
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s03_eda/regression
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s04_features / regression - Features

Spec: `spec/pipeline_design.md` -> s04. Teacher/TA rows: `spec/sources.md` (search `S04`).

**Gate question:** Are features and recipes defined without fitting or using labels?

## Purpose
Define, without fitting: the 27-feature baseline; log transforms and a target-cap step whose value is chosen later on the folds; label-free reduction to a core set; rationale and citations; candidate feature sets per model; the pipeline recipe per model (impute, encode, scale).

## Planned outputs (`outputs/`)
- feature_dictionary.csv (formula, grain, availability, missingness, rationale, citation)
- candidate_sets.json (per model)
- recipes.json (pipeline recipe per model)

## Gate criteria
- Only label-free checks used for reduction
- Cap value not fixed here; candidates declared in protocol.yaml
- Every retained feature has a rationale
- Nothing fitted on data
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
