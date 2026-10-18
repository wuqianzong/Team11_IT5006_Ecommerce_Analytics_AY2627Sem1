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

## Working log (README section 9.1; one row per solution ID, every code change names its ID)
| ID | What was built | Commit | Evidence (files, figures) | Coverage | Round |
| --- | --- | --- | --- | --- | --- |

## Review rounds (append-only; each round has review/round_N/ and a section in the doc tab)
| Round | Commit | Run ID | Review pack | Outcome | Date |
| --- | --- | --- | --- | --- | --- |

## Accepted result (the only result the report and slides may cite)
- Accepted round: - commit: - run ID: - approved by: - date:

## Deviations from blueprint
None.

## Open questions
