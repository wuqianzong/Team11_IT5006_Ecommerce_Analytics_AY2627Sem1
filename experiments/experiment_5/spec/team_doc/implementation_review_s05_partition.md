# s05 Partition — implementation review

> **ACCEPTED · round 3 · 2026-10-20 · tag e5-s05-accepted · approved by the experiment lead after Henry's review, after s04 (G-74).** Accepted runs 20261020T145621Z (regression) and 20261020T145612Z (classification), on a clean tree; every output is identical to the round 3 review packs, so the cards in the sub-tabs are the accepted values. Test cohorts (new-customer time-ordered holdouts): regression 18,788 orders (19.54% of eligible), classification 18,966 (19.52%). Decisions: G-74 (minimum training rows per fold and detractors per part), development–test drift accepted, classification test detractor share 14.59% (1,968 of 13,488) accepted as protocol deviation G-75 and reported in s09 with the absolute count. Report appendix requests (fold tables, partition diagram) are recorded in the s05 and s10 report hooks.

**Round 1 · IN REVIEW (together with s04, G-74)** · runs `20261020T073917Z` (regression) and `20261020T073908Z` (classification) · coverage 8 of 8 per task (classification 5.4 DEVIATION, accepted as G-75), 0 MISSING · 9 + 11 checks, all PASS. s05 depends only on s02. s04 is accepted and committed before s05 (G-74). Nothing is committed until acceptance (G-64).

## Current (round 1)

### Coverage

| Task | ID | Solution step | Coverage | Checks | Review |
| --- | --- | --- | --- | --- | --- |
| regression | 5.1 | Order | IMPLEMENTED | — | Approved |
| regression | 5.2 | Test cohort | IMPLEMENTED | PASS | Approved |
| regression | 5.3 | Test-side purge | IMPLEMENTED | PASS | Approved |
| regression | 5.4 | Test checks | IMPLEMENTED | PASS | Approved |
| regression | 5.5 | CV folds | IMPLEMENTED | PASS | Approved |
| regression | 5.6 | Fold customer purge | IMPLEMENTED | PASS | Approved |
| regression | 5.7 | Label maturity | IMPLEMENTED | PASS | Approved |
| regression | 5.8 | Class support and training size | IMPLEMENTED | PASS | Approved |
| classification | 5.1 | Order | IMPLEMENTED | — | Approved |
| classification | 5.2 | Test cohort | IMPLEMENTED | PASS | Approved |
| classification | 5.3 | Test-side purge | IMPLEMENTED | PASS | Approved |
| classification | 5.4 | Test checks | DEVIATION | PASS | Approved |
| classification | 5.5 | CV folds | IMPLEMENTED | PASS | Approved |
| classification | 5.6 | Fold customer purge | IMPLEMENTED | PASS | Approved |
| classification | 5.7 | Label maturity | IMPLEMENTED | PASS | Approved |
| classification | 5.8 | Class support and training size | IMPLEMENTED | PASS | Approved |

### Summary

| Task | Development orders | Test orders (share of eligible) | Repeat-customer test orders removed | Training rows, folds 1-5 | Validation rows, folds 1-5 |
| --- | --- | --- | --- | --- | --- |
| regression | 76,925 | 18,788 (19.54%) | 453 | 11,297, 23,864, 33,927, 47,957, 59,880 | 12,820, 12,820, 12,818, 12,811, 10,740 |
| classification | 77,736 | 18,966 (19.52%) | 468 | 11,077, 23,573, 33,568, 47,933, 60,361 | 12,956, 12,950, 12,941, 12,925, 10,251 |

### Decisions for the team

1. **Fold minimums (G-74, proposed).** G-53 asks for a pre-registered minimum number of training rows per fold, but no value was set. I pre-registered them in s01 before building any fold: 10,000 training rows per fold (both tasks) and 100 detractors in each classification training and validation part. The smallest fold has 11,297 (regression) and 11,077 (classification) training rows. Please confirm the values.
2. **Classification test detractors (G-75, accepted).** The test cohort keeps 1,968 of 13,488 eligible detractors (14.59%), below the pre-registered 15%. The experiment lead accepted this as a protocol deviation instead of moving the cutoff; s09 states it with the absolute count. For information.
3. **Drift between development and test (5.4).** Regression: mean lead time 13.42 days in development vs 8.74 in test (median 11.17 vs 7.43). Classification: detractor rate 14.78% vs 10.38%. The test period is faster and happier than development, as the s03 trends showed. This is real drift the test score faces, not a split error; s09 reports it (9.4). For information.
4. **Label maturity drops (5.7).** Training rows whose label was observed only after their fold's validation block starts are dropped (orders still in transit or not yet reviewed at that point): 1,405–4,274 per fold in regression and 1,756–5,035 in classification (fold\_summary.csv). Validation rows need their label before the test cutoff. Please confirm this reading of 5.7.

### Checks

| Task | Check | Result | Detail | IDs |
| --- | --- | --- | --- | --- |
| regression | no test order\_id or customer\_unique\_id in development | PASS | 453 repeat-customer test orders removed | 5.2, 5.3 |
| regression | test keeps >= 15% of eligible delivered orders | PASS | 18,788 of 96,166 = 19.54% | 5.4 |
| regression | never a random split: test is every eligible order on or after the cutoff, minus repeat customers | PASS | — | 5.2 |
| regression | every fold: max training purchase time < min validation purchase time | PASS | — | 5.5 |
| regression | every fold: no shared customer\_unique\_id between training and validation | PASS | — | 5.6 |
| regression | every fold: every training label observable before the validation block starts | PASS | 14,207 training rows dropped over the folds | 5.7 |
| regression | every validation label observable before the test cutoff | PASS | 2,091 validation rows dropped | 5.7 |
| regression | every fold: training rows >= 10,000 (G-53) | PASS | fold 1 11,297; fold 2 23,864; fold 3 33,927; fold 4 47,957; fold 5 59,880 | 5.8 |
| regression | five folds with equal-sized validation blocks before maturity drops | PASS | 12,820, 12,820, 12,820, 12,820, 12,820 | 5.5 |
| classification | no test order\_id or customer\_unique\_id in development | PASS | 468 repeat-customer test orders removed | 5.2, 5.3 |
| classification | test keeps >= 15% of eligible reviewed orders | PASS | 18,966 of 97,170 = 19.52% | 5.4 |
| classification | test keeps >= 15% of all eligible detractors, or a recorded team deviation | PASS | 1,968 of 13,488 = 14.59%: below the minimum, accepted deviation G-75 | 5.4 |
| classification | never a random split: test is every eligible order on or after the cutoff, minus repeat customers | PASS | — | 5.2 |
| classification | every fold: max training purchase time < min validation purchase time | PASS | — | 5.5 |
| classification | every fold: no shared customer\_unique\_id between training and validation | PASS | — | 5.6 |
| classification | every fold: every training label observable before the validation block starts | PASS | 16,638 training rows dropped over the folds | 5.7 |
| classification | every validation label observable before the test cutoff | PASS | 2,757 validation rows dropped | 5.7 |
| classification | every fold: training rows >= 10,000 (G-53) | PASS | fold 1 11,077; fold 2 23,573; fold 3 33,568; fold 4 47,933; fold 5 60,361 | 5.8 |
| classification | every fold: both classes present, >= 100 detractors in training and in validation | PASS | fold 1 1,410/1,440; fold 2 2,798/1,985; fold 3 3,993/1,953; fold 4 6,312/2,811; fold 5 8,694/1,108 | 5.8 |
| classification | five folds with equal-sized validation blocks before maturity drops | PASS | 12,956, 12,956, 12,956, 12,956, 12,956 | 5.5 |

## Round history

### Round 1 — 2026-10-20

- First build of s05 for both tasks, written for Experiment 5 from the blueprint (new foundation module e5lib/partition.py; no code from earlier experiments). Started while s04 is in review (G-74).
- The classification run stopped on the G-46 detractor-share check (14.59% < 15%), as designed; the lead accepted it as a protocol deviation (G-75) and the run completed.
- Comments and resolutions: none yet.

### Round 2 — 2026-10-20

- Henry's review: decision 1 (fold minimums) agreed (G-74); decision 3 (drift) accepted; decision 4 (label maturity) explained in its thread and the 5.7 cards reworded in plain language.
- Open for the lead: Henry's proposal to replace the 15% minimum detractor share with an accepted range of 10–30%, instead of the recorded deviation G-75.
- Runs 20261020T124728Z (regression) and 20261020T124714Z (classification); review packs review/round\_2/. Only the 5.7 wording changed; every data output is unchanged.

### Round 3 — 2026-10-20

- Henry's last comments: the 10–30% range is not pursued (the shortfall stays the recorded deviation G-75); fold counts now read “fold k is n” in cards 5.6–5.8 and their checks; fold tables and the partition diagram recorded for the report appendix.
- Runs 20261020T145621Z (regression) and 20261020T145612Z (classification) on a clean tree after commit a740fe2 (dirty false); review packs review/round\_3/. Only wording changed; every data output is unchanged.

### Acceptance — 2026-10-20

- s04 was accepted, committed and tagged first (e5-s04-accepted, G-74). s05 accepted by the experiment lead on round 3, committed and tagged e5-s05-accepted.
