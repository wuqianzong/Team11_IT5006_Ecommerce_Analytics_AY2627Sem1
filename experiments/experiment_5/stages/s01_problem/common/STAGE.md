---
node: s01_problem/common
owner: TBD
reviewer: TBD
status: READY_FOR_REVIEW
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
| 1.1 | Tasks and prediction time: Two tasks pre-registered: lead_days (regression) and is_detractor (classification, positive class 1), both predicted at order_purchase_timestamp. | 26810a0 | protocol_preregistered.yaml, preregistered_values.csv, task_contract.md | IMPLEMENTED | 1 |
| 1.2 | Stakeholders and action: Stakeholder and action recorded per task in protocol.yaml and task_contract.md. | 26810a0 | protocol_preregistered.yaml, preregistered_values.csv, task_contract.md | IMPLEMENTED | 1 |
| 1.3 | Targets and populations: Populations, label rule and the predictor contract recorded: 27 contract predictors, 3 excluded with reasons, 24 eligible; calendar fields numeric. | 26810a0 | protocol_preregistered.yaml, preregistered_values.csv, task_contract.md | IMPLEMENTED | 1 |
| 1.4 | Metrics: Primary metrics: MAE (regression), AP (classification), with secondary metrics and charts; evaluation settings for s09 pre-registered. | 26810a0 | protocol_preregistered.yaml, preregistered_values.csv, task_contract.md | IMPLEMENTED | 1 |
| 1.5 | Cost assumption: Illustrative cost FN:FP = 5:1. | 26810a0 | protocol_preregistered.yaml, preregistered_values.csv, task_contract.md | IMPLEMENTED | 1 |
| 1.6 | Model families: 5 regression and 4 classification estimators, with the s06 plain settings. | 26810a0 | protocol_preregistered.yaml, preregistered_values.csv, task_contract.md | IMPLEMENTED | 1 |
| 1.7 | Decision rule: One-standard-error rule, simplicity order, plain-vs-tuned comparison, fallback, s08 gate, calibration keep rule and threshold candidates pre-registered. | 26810a0 | protocol_preregistered.yaml, preregistered_values.csv, task_contract.md | IMPLEMENTED | 1 |
| 1.8 | Search budget: Grids fixed: tree depths [4, 5, 6, 8, 10, 12, 14, 16, 18], forest depths [8, 10, 12, 14, 16, 18], leaves [20, 50, 100, 200], alpha and C [0.01, 0.1, 0.5, 1, 5, 10, 20, 50, 100]; forest 200 trees; seed 42. | 26810a0 | protocol_preregistered.yaml, preregistered_values.csv, task_contract.md | IMPLEMENTED | 1 |
| 1.9 | Outputs: spec/protocol.yaml (pre-registered layer) and task_contract.md written; the values are also listed in preregistered_values.csv for review. | 26810a0 | protocol_preregistered.yaml, preregistered_values.csv | IMPLEMENTED | 1 |

## Review rounds (append-only; each round has review/round_N/ and a section in the doc tab)
| Round | Commit | Run ID | Review pack | Outcome | Date |
| --- | --- | --- | --- | --- | --- |
| 1 | code 26810a0, evidence 1cad146 | 20261018T133930Z | review/round_1/review_pack.md | in review | 2026-10-18 |

## Accepted result (the only result the report and slides may cite)
- Accepted round: - commit: - run ID: - approved by: - date:

## Deviations from blueprint
None.

## Open questions
