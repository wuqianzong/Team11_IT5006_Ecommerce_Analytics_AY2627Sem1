---
node: s09_conclusion/classification
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s08_selection/classification
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s09_conclusion / classification - Conclusion

Spec: `spec/pipeline_design.md` -> s09. Teacher/TA rows: `spec/sources.md` (search `S09`).
Blueprint: `spec/blueprints/s09_conclusion.md` (implement only when its status is AGREED).

**Gate question:** Does every conclusion follow from the test results and their limits?

## Purpose
Train-validation-test table with bootstrap confidence intervals, subgroup errors and drift, interpretation of the selected model, stakeholder actions supported by the evidence, and limitations.

## Planned outputs (`outputs/`)
- master_metrics.csv (train / validation / test, with CIs)
- subgroups.csv
- drift.csv
- importance.csv (states the model it explains)
- conclusion.md

## Gate criteria
- Validation scores labelled as selection scores, not generalisation estimates
- Importance explains the selected model
- Test cohort described as historical held-out, not unseen
- Every recommendation traced to evidence
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
