---
node: s01_problem/common
owner: TBD
reviewer: TBD
status: ACCEPTED
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
| 1.3 | Targets and populations: Populations, label rule and the predictor contract recorded from e5lib/contract.py: 24 predictors (4 categorical, calendar fields numeric); 3 columns listed as not in the contract with their reason; 10 exclusion reason codes for s02. | acceptance commit (e5-s01-accepted) | protocol_preregistered.yaml, preregistered_values.csv, task_contract.md | IMPLEMENTED | 2 |
| 1.4 | Metrics: Primary metrics: MAE (regression), AP (classification), with secondary metrics and charts; evaluation settings for s09 pre-registered. | 26810a0 | protocol_preregistered.yaml, preregistered_values.csv, task_contract.md | IMPLEMENTED | 1 |
| 1.5 | Cost assumption: Illustrative cost FN:FP = 5:1. | 26810a0 | protocol_preregistered.yaml, preregistered_values.csv, task_contract.md | IMPLEMENTED | 1 |
| 1.6 | Model families: 5 regression and 4 classification estimators, with the s06 plain settings. | 26810a0 | protocol_preregistered.yaml, preregistered_values.csv, task_contract.md | IMPLEMENTED | 1 |
| 1.7 | Decision rule: One-standard-error rule, simplicity order, plain-vs-tuned comparison, fallback, s08 gate, calibration keep rule and threshold candidates pre-registered. | 26810a0 | protocol_preregistered.yaml, preregistered_values.csv, task_contract.md | IMPLEMENTED | 1 |
| 1.8 | Search budget: Grids fixed: tree depths [4, 5, 6, 8, 10, 12, 14, 16, 18], forest depths [8, 10, 12, 14, 16, 18], leaves [20, 50, 100, 200], alpha and C [0.01, 0.1, 0.5, 1, 5, 10, 20, 50, 100]; forest 200 trees; seed 42. | 26810a0 | protocol_preregistered.yaml, preregistered_values.csv, task_contract.md | IMPLEMENTED | 1 |
| 1.9 | Outputs: spec/protocol.yaml (pre-registered layer) and task_contract.md written; the values are also listed in preregistered_values.csv for review. | 26810a0 | protocol_preregistered.yaml, preregistered_values.csv | IMPLEMENTED | 1 |

## Review rounds (append-only; each round has review/round_N/ and a section in the doc tab)
| Round | Commit | Run ID | Review pack | Outcome | Date |
| --- | --- | --- | --- | --- | --- |
| 1 | code 26810a0, evidence 1cad146 | 20261018T133930Z | review/round_1/review_pack.md | changes requested on 1.3 (contract, log1p, exclusions) | 2026-10-18 |
| 2 | acceptance commit (tag e5-s01-accepted) | 20261018T150315Z | review/round_2/review_pack.md | accepted: all 9 rows Approved in the doc, 7 checks PASS | 2026-10-18 |

## Accepted result (the only result the report and slides may cite)
- **Current run to cite: 20261019T163354Z** (CR-042, 2026-10-20). The working log above shows this run's values; the lines below record the acceptance history.
- Accepted round: 2 - commit: the "s01 accepted" commit, tag `e5-s01-accepted` - run ID: 20261018T150315Z - approved by: experiment lead (Wu Qianzong), after team review in the doc tab "Implementation reviews › s01 Problem" - date: 2026-10-18
- Evidence: `outputs/_manifest.json` (output hashes), `review/round_2/review_pack.md`.
- 2026-10-19: rerun as run 20261018T164754Z after the foundation encoding fix (CR-030); every output byte-identical to the accepted run, decision unchanged, so the acceptance stands.
- 2026-10-19: rerun as run 20261018T165122Z after the line-ending fix (CR-031); outputs byte-identical again, acceptance stands.
- 2026-10-19: rerun as run 20261019T054239Z after the s02 foundation additions (CR-033). The 1.9 check "pre-registered before any later stage has outputs" failed on any rerun once s02 existed; it is now "later stages used this pre-registered layer" (compares each later manifest's pre-registered hash). protocol.yaml and every value output are byte-identical; only the check name and detail in _evidence_index.json changed. Confirmed with the s02 acceptance (decision 3). On Windows, `status` shows FRESH after the one-time refresh in README §13.3.

## Changes after acceptance (README section 9.2)
- 2026-10-19, CR-037 (G-68): protocol.yaml pre-registered layer gains features.screening_candidates (three catalogue fields, classification only, not predictors) from e5lib/contract.py SCREENING_CANDIDATES; new check that they stay outside the 24. Rerun 20261019T140139Z; all other values unchanged. Approved by the experiment lead; reviewed with s03 round 2 in the doc (dated addendum on this stage's tab). Status stays ACCEPTED (no decision.json changed).
- 2026-10-19, CR-038 (G-69): protocol.yaml screening_candidates gain the promise, region and seller-history entries with group and kind, a promise note (G-35 reopened for the screen) and the seller-history rule. Rerun 20261019T151352Z. Approved by the experiment lead; reviewed with s03 round 3. Status stays ACCEPTED.
- 2026-10-20, CR-042 (G-71, external audit): rerun 20261019T163354Z on a clean tree (dirty false); protocol.yaml gains reason code INVALID_REVIEW_TIME (G-71); every other value unchanged. Approved by the experiment lead. Status stays ACCEPTED (no decision.json changed).

## Deviations from blueprint
None.

## Open questions
