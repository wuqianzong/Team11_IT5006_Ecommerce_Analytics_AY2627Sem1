---
node: s12_package/common
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s11_deployment/common
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s12_package / common - Package

Spec: `spec/pipeline_design.md` -> STAGE12. Teacher/TA rows: `spec/sources.md` (search `S12`).

**Gate question:** Does every number in report, deck and app trace to one release?

## Purpose
Build evidence/build from evidence/registry.yaml; master metric table; verify every report/deck/app number against numbers.json; cut the release tag.

## Planned outputs (`outputs/`)
- evidence/build/** (via build_evidence.py)
- deliverables/ report & deck drafts that cite evidence IDs
- report_number_check.json
- release notes

## Gate criteria
- run_pipeline.py check passes
- Every report/deck number traces to an evidence ID
- Story follows design section E
- Nothing written outside experiments/experiment_5/; migration only on the experiment lead's instruction (README section 12)
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
