---
node: s02_data/common
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s01_problem/common
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s02_data / common - Data preprocessing

Spec: `spec/pipeline_design.md` -> s02. Teacher/TA rows: `spec/sources.md` (search `S02`).
Blueprint: `spec/blueprints/s02_data.md` (implement only when its status is AGREED).

**Gate question:** Are joins, grains, targets and leakage exclusions verified?

## Purpose
Load and clean the nine Olist tables deterministically, join aggregation-first to one row per order, build both targets with label-availability timestamps, audit every column against checkout time and apply the zero-item classification rule. Population and data-quality rules applied to development and test alike: zero-item orders out of both tasks; classification limited to orders not cancelled or unavailable with a valid review; lead_days > max(100, mean + 12 SD of pre-cutoff orders) and distance_km_max > 4,397.53 km removed as suspected data-entry errors; orders with missing payment_installments_max removed.

## Planned outputs (`outputs/`)
- records.csv.gz (IDs for audit + features + targets + timestamps)
- exclusions.csv
- data_hashes.json (input and IBGE boundary sha256)
- audit.json (joins, grains, leakage, label sensitivity)

## Gate criteria
- Only row-local deterministic rules; nothing learned
- Every column classified as known or not known at checkout
- Minimum vs first review label sensitivity recorded
- Input hashes recorded
- Per-task test cutoff computed by the 80/20 rule and recorded (not assumed from Milestone 2)
- Outlier threshold computed on pre-cutoff orders only; every removal counted in exclusions.csv
- order_status, order_approved_at, shipping_limit_date, has_items, freight_ratio_missing and payment_missing never predictors
- Date-order audit run on every order; violations logged
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
