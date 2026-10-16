---
node: s00_contract/common
owner: TBD
reviewer: TBD
status: TODO
depends_on: []
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s00_contract / common - Contract

Spec: `spec/pipeline_design.md` -> STAGE0. Teacher/TA rows: `spec/sources.md` (search `S00`).

**Gate question:** Are targets, populations, metrics, decision rules and budget frozen before any result?

## Purpose
Freeze tasks, targets, positive class, eligible populations, excluded post-outcome columns, stakeholders, metrics, the illustrative FN:FP = 5:1 cost, decision/tie rules, model families and search budget - before any result.

## Planned outputs (`outputs/`)
- spec/protocol.yaml v1.0 (proposed via CHANGELOG)
- task_contract.md (per-task prediction time, stakeholder action, limits)

## Gate criteria
- Every number later stages need is in protocol.yaml
- Decision rules and tie-breaks written before any result
- Teacher/TA/brief rows for S00 in spec/sources.md satisfied
- Milestone 2 TA comments added to spec/sources.md section 3.2
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
