---
node: s10_release/common
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s09_conclusion/regression
  - s09_conclusion/classification
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s10_release / common - Release

Spec: `spec/pipeline_design.md` -> s10. Teacher/TA rows: `spec/sources.md` (search `S10`).
Blueprint: `spec/blueprints/s10_release.md` (implement only when its status is AGREED).

**Gate question:** Do the app, dashboard, report and slides all trace to one reproduced release?

## Purpose
Reload parity of the bundles; team approval; lead-ordered migration with a reproduction README (README section 12); reproduction check; then the Streamlit app and dashboard, report and slides from the reproduced outputs, walkthrough notebook, and input checks with error handling.

## Planned outputs (`outputs/`)
- parity.json
- input_validation.json
- migration_check.json
- app/ and dashboard (inside experiments/experiment_5 until migration)
- deliverables/ report and deck drafts citing evidence IDs
- walkthrough notebook

## Gate criteria
- Every table and chart in the model tabs traced to a stage output in app_sources.json; business dashboard tab labelled as its own descriptive scope (G-41)
- App loads the s08 bundle unchanged
- Reproduction check matches the release before any deliverable is built
- Nothing written outside experiments/experiment_5/ before the lead orders migration
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
