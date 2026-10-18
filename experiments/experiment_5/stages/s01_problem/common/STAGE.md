---
node: s01_problem/common
owner: TBD
reviewer: TBD
status: IN_PROGRESS
depends_on: []
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s01_problem / common - Problem statement

Spec: `spec/pipeline_design.md` -> s01. Teacher/TA rows: `spec/sources.md` (search `S01`).
Blueprint: `spec/blueprints/s01_problem.md` (implement only when its status is AGREED).

**Gate question:** Are tasks, targets, metrics, cost, decision rule and budget fixed before any result?

## Purpose
Fix both checkout tasks, prediction time, stakeholders and their actions, targets and label rules, metrics, the illustrative FN:FP = 5:1 cost, model families, decision rule, grids, budget, seed 42 and the test cutoff (protocol layer a: pre-registered) - before any data is seen.

## Planned outputs (`outputs/`)
- spec/protocol.yaml v1.0 (proposed via CHANGELOG)
- task_contract.md (prediction time, stakeholder action, limits, metric and model rationale with verified citations)

## Gate criteria
- Every number later stages need is in protocol.yaml
- Decision rule and tie-breaks written before any result
- Stakeholder action stated, not only named
- Every citation verified to exist and support its claim
- protocol.yaml separates pre-registered values from data-dependent values owned by s04 and s05
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
