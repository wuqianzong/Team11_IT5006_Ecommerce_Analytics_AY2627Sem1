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
- data_dictionary.csv (every raw and derived column; NIBRS model, G-58)
- figures/data_structure.png (tables, keys, one-to-many links, aggregate-first join)

## Gate criteria
- Only row-local deterministic rules; nothing learned
- Every column classified as known or not known at checkout
- Minimum vs first review label sensitivity recorded
- Input hashes recorded
- Data dictionary covers every raw and derived column and matches the leakage tags (G-58)
- Per-task test cutoff computed by the 80/20 rule and recorded (not assumed from Milestone 2)
- Outlier threshold computed on pre-cutoff orders only; every removal counted in exclusions.csv
- order_status, order_approved_at, shipping_limit_date, has_items, freight_ratio_missing and payment_missing never predictors
- Date-order audit run on every order; violations logged
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
