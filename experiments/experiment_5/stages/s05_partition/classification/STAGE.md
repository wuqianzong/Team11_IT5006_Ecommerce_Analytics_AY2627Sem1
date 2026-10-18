---
node: s05_partition/classification
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s02_data/common
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s05_partition / classification - Partition

Spec: `spec/pipeline_design.md` -> s05. Teacher/TA rows: `spec/sources.md` (search `S05`).
Blueprint: `spec/blueprints/s05_partition.md` (implement only when its status is AGREED).

**Gate question:** Are folds chronological, customers purged, labels mature and classes supported?

## Purpose
Sort by purchase time; hold out each task's newest 20% as its test cohort (cutoff computed in s02 by the 80/20 rule; exact IDs frozen); remove test orders whose customer also appears in development; check test size and review share (>= 15% each) and report the prevalence gap, alerting and stopping on failure (no random fallback); build five time-ordered expanding CV folds on development orders with customer purge, label maturity and class-support checks; seed 42 documented.

## Planned outputs (`outputs/`)
- folds.csv
- test_manifest.csv (task-specific test cohort)
- counts.json (rows, customers, positives per fold and cohort)
- checks.json (customer purge, maturity, rows lost to maturity, class support)

## Gate criteria
- No test customer in development (repeat customers removed from test; order_id and customer_unique_id checked)
- Test cohort >= 15% of eligible orders and >= 15% of reviewed orders
- Never a random split
- Five expanding folds; customers purged across training and validation in every fold
- Every fold: max training purchase time < min validation purchase time, and no shared customer_unique_id (asserted)
- Training outcomes available before each fold origin
- Both classes present in every fold (classification)
- Any boundary move logged before s06 runs
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
