---
node: s01_records/common
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s00_contract/common
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s01_records / common - Records

Spec: `spec/pipeline_design.md` -> STAGE1. Teacher/TA rows: `spec/sources.md` (search `S01`).

**Gate question:** Are joins, grains, units, eligibility and leakage exclusions verified?

## Purpose
Build the deterministic order-level feature/target table from the Milestone 2 joins and formulas; audit keys, join cardinality, units, review aggregation, target-availability timestamps, freight_ratio and zero-item classification eligibility.

## Planned outputs (`outputs/`)
- records.csv.gz (IDs for audit + features + targets + timestamps)
- exclusions.csv
- data_hashes.json (raw CSV sha256)
- audit.json (join/grain/leakage checks)

## Gate criteria
- Only row-local deterministic formulas; nothing learned
- Leakage exclusions listed and checked
- Label sensitivity (minimum vs first review) recorded
- Raw data hashes recorded
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
