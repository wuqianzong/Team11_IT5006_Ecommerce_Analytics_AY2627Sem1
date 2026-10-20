---
node: s05_partition/classification
owner: TBD
reviewer: TBD
status: ACCEPTED
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
| 5.1 | Order: 97,170 eligible classification orders sorted by purchase_ts (ties by order_id): 77,736 development orders before the s02 cutoff 2018-05-26 12:16:34, 19,434 on or after it. | acceptance commit (e5-s05-accepted) |  | IMPLEMENTED | 1 |
| 5.2 | Test cohort: every eligible order purchased on or after 2018-05-26 12:16:34; after the purge 18,966 order_ids frozen in test_manifest.csv (2018-05-26 12:16:34 to 2018-08-29 15:00:37). | acceptance commit (e5-s05-accepted) | test_manifest.csv, counts.json | IMPLEMENTED | 1 |
| 5.3 | Test-side purge: 468 test orders (2.41%) belong to customers who also bought in development and were removed. The new-customer time-ordered holdout holds 18,966 orders, 19.52% of eligible orders after the purge. | acceptance commit (e5-s05-accepted) | test_manifest.csv, counts.json | IMPLEMENTED | 1 |
| 5.4 | Test checks: test keeps >= 15% of eligible reviewed orders: PASS (18,966 of 97,170 = 19.52%); test keeps >= 15% of all eligible detractors: FAIL (1,968 of 13,488 = 14.59%). Prevalence: development 14.78%, test 10.38% (gap -4.41%). | acceptance commit (e5-s05-accepted) | counts.json, checks.json | DEVIATION | 3 |
| 5.5 | CV folds: 5 expanding folds on development, validation blocks of 12,956 orders each (last block takes the remainder); boundaries written to protocol.yaml data_dependent.fold_boundaries; training strictly before validation in every fold. | acceptance commit (e5-s05-accepted) | folds.csv, fold_summary.csv, figures/partition_diagram.png, figures/partition_diagram.csv, figures/partition_diagram.json, checks.json | IMPLEMENTED | 3 |
| 5.6 | Fold customer purge: Training orders whose customer_unique_id appears in the fold's validation block removed: fold 1 is 123, fold 2 is 211, fold 3 is 265, fold 4 is 251, fold 5 is 340 rows. | acceptance commit (e5-s05-accepted) | folds.csv, fold_summary.csv, checks.json | IMPLEMENTED | 3 |
| 5.7 | Label maturity: A training order is used only if its answer (is_detractor, known on its review answer date) was already known on the day its fold's validation block starts; a validation order only if its answer was known before the test cutoff. Dropped: fold 1 is 1,756 train / 0 validation, fold 2 is 2,128 train / 6 validation, fold 3 is 5,035 train / 15 validation, fold 4 is 3,640 train / 31 validation, fold 5 is 4,079 train / 2,705 validation. | acceptance commit (e5-s05-accepted) | folds.csv, fold_summary.csv, checks.json | IMPLEMENTED | 3 |
| 5.8 | Class support and training size: Training rows per fold: fold 1 is 11,077, fold 2 is 23,573, fold 3 is 33,568, fold 4 is 47,933, fold 5 is 60,361 (minimum 10,000, pre-registered); detractors training / validation: fold 1 is 1,410 / 1,440, fold 2 is 2,798 / 1,985, fold 3 is 3,993 / 1,953, fold 4 is 6,312 / 2,811, fold 5 is 8,694 / 1,108 (minimum 100). | acceptance commit (e5-s05-accepted) | fold_summary.csv, counts.json, checks.json | IMPLEMENTED | 3 |

## Review rounds (append-only; each round has review/round_N/ and a section in the doc tab)
| Round | Commit | Run ID | Review pack | Outcome | Date |
| --- | --- | --- | --- | --- | --- |
| 1 | acceptance commit (e5-s05-accepted) | 20261020T073908Z | review/round_1/review_pack.md | reviewed (with s04, G-74) | 2026-10-20 |
| 2 | acceptance commit (e5-s05-accepted) | 20261020T124714Z | review/round_2/review_pack.md | reviewed: 5.7 reworded; G-74 minimums agreed, drift accepted (Henry) | 2026-10-20 |
| 3 | acceptance commit (e5-s05-accepted) | 20261020T145612Z | review/round_3/review_pack.md | accepted: all comments resolved (fold wording “fold k is n”, G-74 minimums, drift accepted, detractor share waived as G-75); run on a clean tree after commit a740fe2 | 2026-10-20 |

## Accepted result (the only result the report and slides may cite)
- Accepted round: 3 - commit: the "s05 accepted" commit, tag `e5-s05-accepted` - run ID: 20261020T145612Z (clean tree, dirty false; evidence identical to review/round_3) - approved by: experiment lead (Wu Qianzong), after team review (Henry) in the doc tab "Implementation reviews › s05 Partition" - date: 2026-10-20
- Decisions: minimum training rows per fold and positives per part (G-74); test drift between development and test accepted; test detractor share below 15% accepted as protocol deviation G-75.

## Deviations from blueprint
- 5.4: the test cohort keeps 1,968 of 13,488 eligible detractors (14.59%), below the pre-registered 15% (G-46); accepted by the experiment lead as a protocol deviation (G-75, human_decisions.yaml s05), stated in s09 with the absolute count.

## Open questions
