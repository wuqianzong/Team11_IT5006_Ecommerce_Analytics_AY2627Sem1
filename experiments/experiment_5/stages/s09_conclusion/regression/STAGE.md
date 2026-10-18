---
node: s09_conclusion/regression
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s08_selection/regression
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s09_conclusion / regression - Conclusion

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
- Test cohort described as this experiment's held-out test, scored once in s08 (G-38)
- Every recommendation traced to evidence
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
