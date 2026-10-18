---
node: s05_partition/regression
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s02_data/common
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s05_partition / regression - Partition

Spec: `spec/pipeline_design.md` -> s05. Teacher/TA rows: `spec/sources.md` (search `S05`).
Blueprint: `spec/blueprints/s05_partition.md` (implement only when its status is AGREED).

**Gate question:** Are folds chronological, customers purged, labels mature and classes supported?

## Purpose
Sort by purchase time; hold out each task's newest 20% as its test cohort (cutoff computed in s02 by the 80/20 rule; exact IDs frozen); remove test orders whose customer also appears in development; check test size per task (regression >= 15% of eligible delivered orders; classification >= 15% of eligible reviewed orders and of all eligible detractors) and report the prevalence gap, alerting and stopping on failure (no random fallback); build five time-ordered expanding CV folds on development orders with customer purge, label maturity and class-support checks; seed 42 documented.

## Planned outputs (`outputs/`)
- folds.csv
- test_manifest.csv (task-specific test cohort)
- counts.json (rows, customers, positives per fold and cohort)
- checks.json (customer purge, maturity, rows lost to maturity, class support, minimum training rows)

## Gate criteria
- No test customer in development (repeat customers removed from test; order_id and customer_unique_id checked)
- Test size checks per task (G-46)
- Never a random split
- Five expanding folds; customers purged across training and validation in every fold
- Every fold: max training purchase time < min validation purchase time, and no shared customer_unique_id (asserted)
- Training outcomes available before each fold origin
- Both classes present in every fold (classification)
- Any boundary move logged before s06 runs
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
