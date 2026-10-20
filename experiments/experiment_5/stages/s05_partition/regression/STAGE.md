---
node: s05_partition/regression
owner: TBD
reviewer: TBD
status: ACCEPTED
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
| 5.1 | Order: 96,166 eligible regression orders sorted by purchase_ts (ties by order_id): 76,925 development orders before the s02 cutoff 2018-05-27 12:30:34, 19,241 on or after it. | acceptance commit (e5-s05-accepted) |  | IMPLEMENTED | 1 |
| 5.2 | Test cohort: every eligible order purchased on or after 2018-05-27 12:30:34; after the purge 18,788 order_ids frozen in test_manifest.csv (2018-05-27 12:30:34 to 2018-08-29 15:00:37). | acceptance commit (e5-s05-accepted) | test_manifest.csv, counts.json | IMPLEMENTED | 1 |
| 5.3 | Test-side purge: 453 test orders (2.35%) belong to customers who also bought in development and were removed. The new-customer time-ordered holdout holds 18,788 orders, 19.54% of eligible orders after the purge. | acceptance commit (e5-s05-accepted) | test_manifest.csv, counts.json | IMPLEMENTED | 1 |
| 5.4 | Test checks: test keeps >= 15% of eligible delivered orders: PASS (18,788 of 96,166 = 19.54%). lead_days: development mean 13.42 / median 11.17; test mean 8.74 / median 7.43 days. | acceptance commit (e5-s05-accepted) | counts.json, checks.json | IMPLEMENTED | 3 |
| 5.5 | CV folds: 5 expanding folds on development, validation blocks of 12,820 orders each (last block takes the remainder); boundaries written to protocol.yaml data_dependent.fold_boundaries; training strictly before validation in every fold. | acceptance commit (e5-s05-accepted) | folds.csv, fold_summary.csv, figures/partition_diagram.png, figures/partition_diagram.csv, figures/partition_diagram.json, checks.json | IMPLEMENTED | 3 |
| 5.6 | Fold customer purge: Training orders whose customer_unique_id appears in the fold's validation block removed: fold 1 is 123, fold 2 is 209, fold 3 is 264, fold 4 is 254, fold 5 is 343 rows. | acceptance commit (e5-s05-accepted) | folds.csv, fold_summary.csv, checks.json | IMPLEMENTED | 3 |
| 5.7 | Label maturity: A training order is used only if its answer (lead_days, known on its delivery date) was already known on the day its fold's validation block starts; a validation order only if its answer was known before the test cutoff. Dropped: fold 1 is 1,405 train / 0 validation, fold 2 is 1,572 train / 0 validation, fold 3 is 4,274 train / 2 validation, fold 4 is 3,074 train / 9 validation, fold 5 is 3,882 train / 2,080 validation. | acceptance commit (e5-s05-accepted) | folds.csv, fold_summary.csv, checks.json | IMPLEMENTED | 3 |
| 5.8 | Class support and training size: Training rows per fold: fold 1 is 11,297, fold 2 is 23,864, fold 3 is 33,927, fold 4 is 47,957, fold 5 is 59,880 (minimum 10,000, pre-registered). | acceptance commit (e5-s05-accepted) | fold_summary.csv, counts.json, checks.json | IMPLEMENTED | 3 |

## Review rounds (append-only; each round has review/round_N/ and a section in the doc tab)
| Round | Commit | Run ID | Review pack | Outcome | Date |
| --- | --- | --- | --- | --- | --- |
| 1 | acceptance commit (e5-s05-accepted) | 20261020T073917Z | review/round_1/review_pack.md | reviewed (with s04, G-74) | 2026-10-20 |
| 2 | acceptance commit (e5-s05-accepted) | 20261020T124728Z | review/round_2/review_pack.md | reviewed: 5.7 reworded; G-74 minimums agreed, drift accepted (Henry) | 2026-10-20 |
| 3 | acceptance commit (e5-s05-accepted) | 20261020T145621Z | review/round_3/review_pack.md | accepted: all comments resolved (fold wording “fold k is n”, G-74 minimums, drift accepted, detractor share waived as G-75); run on a clean tree after commit a740fe2 | 2026-10-20 |

## Accepted result (the only result the report and slides may cite)
- Accepted round: 3 - commit: the "s05 accepted" commit, tag `e5-s05-accepted` - run ID: 20261020T145621Z (clean tree, dirty false; evidence identical to review/round_3) - approved by: experiment lead (Wu Qianzong), after team review (Henry) in the doc tab "Implementation reviews › s05 Partition" - date: 2026-10-20
- Decisions: minimum training rows per fold and positives per part (G-74); test drift between development and test accepted (G-77).

## Deviations from blueprint
None.

## Open questions
