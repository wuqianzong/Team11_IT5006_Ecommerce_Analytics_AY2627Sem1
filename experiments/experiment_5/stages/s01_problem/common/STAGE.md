---
node: s01_problem/common
owner: TBD
reviewer: TBD
status: TODO
depends_on: []
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s01_problem / common - Problem statement

Spec: `spec/pipeline_design.md` -> s01. Teacher/TA rows: `spec/sources.md` (search `S01`).

**Gate question:** Are tasks, targets, metrics, cost, decision rule and budget fixed before any result?

## Purpose
Fix both checkout tasks, prediction time, stakeholders and their actions, targets and label rules, metrics, the illustrative FN:FP = 5:1 cost, model families, decision rule, search budget and seed 42 - before any result.

## Planned outputs (`outputs/`)
- spec/protocol.yaml v1.0 (proposed via CHANGELOG)
- task_contract.md (prediction time, stakeholder action, limits, metric and model rationale with verified citations)

## Gate criteria
- Every number later stages need is in protocol.yaml
- Decision rule and tie-breaks written before any result
- Stakeholder action stated, not only named
- Every citation verified to exist and support its claim
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
