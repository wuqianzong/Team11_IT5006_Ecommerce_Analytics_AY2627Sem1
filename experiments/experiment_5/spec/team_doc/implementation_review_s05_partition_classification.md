# s05 Partition › classification — evidence cards

Round 1 · run `20261020T073908Z` · 11 checks, all PASS (5.4 through the accepted deviation G-75). Coverage and review dropdowns are on the parent tab "s05 Partition"; comment on any card here.

## 5.1 Order

**Approved solution:** Sort each task's eligible orders by purchase timestamp, earliest first

**What was done:** 97,170 eligible classification orders sorted by purchase\_ts (ties by order\_id): 77,736 development orders before the s02 cutoff 2018-05-26 12:16:34, 19,434 on or after it.

| Item | Value |
| --- | --- |
| eligible orders | 97,170 |
| development (before the cutoff) | 77,736 |
| on or after the cutoff | 19,434 |
| test cutoff (s02) | 2018-05-26 12:16:34 |

**Files** (stages/s05\_partition/classification/outputs/, run 20261020T073908Z):

## 5.2 Test cohort

**Approved solution:** Newest 20% per task, computed fresh: the cutoff is the purchase timestamp at the 80% position of that task's eligible orders (after the s02 row-local population rules, before the outlier rule; G-67). It is computed in s02, recorded in protocol.yaml (data-dependent layer), and the exact IDs are frozen in `test_manifest.csv`. The cohort is defined only by this experiment's data and rules and is a new held-out test (G-38)

**What was done:** Test cohort: every eligible order purchased on or after 2018-05-26 12:16:34; after the purge 18,966 order\_ids frozen in test\_manifest.csv (2018-05-26 12:16:34 to 2018-08-29 15:00:37).

**Conclusion:** Defined only by this experiment's data and rules (G-38).

| Item | Value |
| --- | --- |
| test orders (after the purge) | 18,966 |
| test customers | 18,758 |
| share of eligible orders | 19.52% |

**Check** no test order\_id or customer\_unique\_id in development: PASS (468 repeat-customer test orders removed) **Check** never a random split: test is every eligible order on or after the cutoff, minus repeat customers: PASS

**Files** (stages/s05\_partition/classification/outputs/, run 20261020T073908Z): test\_manifest.csv, counts.json

## 5.3 Test-side purge

**Approved solution:** Remove test orders whose `customer_unique_id` also appears in development (count logged). The test cohort is then new customers only, named a "new-customer time-ordered holdout" and always stated with its actual share of eligible orders after the purge and the share the purge removed (G-48)

**What was done:** 468 test orders (2.41%) belong to customers who also bought in development and were removed. The new-customer time-ordered holdout holds 18,966 orders, 19.52% of eligible orders after the purge.

| Item | Value |
| --- | --- |
| orders on or after the cutoff | 19,434 |
| removed: customer also in development | 468 (2.41%) |
| test orders kept | 18,966 |
| cohort name | new-customer time-ordered holdout |

**Check** no test order\_id or customer\_unique\_id in development: PASS (468 repeat-customer test orders removed)

**Files** (stages/s05\_partition/classification/outputs/, run 20261020T073908Z): test\_manifest.csv, counts.json

## 5.4 Test checks

**Approved solution:** Per task (G-46): regression test keeps at least 15% of eligible delivered orders; classification test keeps at least 15% of eligible reviewed orders and at least 15% of all eligible detractors; train–test prevalence gap reported. On failure: alert the team and stop, never a random split

**What was done:** test keeps >= 15% of eligible reviewed orders: PASS (18,966 of 97,170 = 19.52%); test keeps >= 15% of all eligible detractors: FAIL (1,968 of 13,488 = 14.59%). Prevalence: development 14.78%, test 10.38% (gap -4.41%).

**Reasoning:** The test cohort is later in time; a gap here is the drift the test score has to face, not a split error. No random fallback exists.

**Deviation:** test keeps >= 15% of all eligible detractors: FAILED (1,968 of 13,488 = 14.59%); accepted by the team as a protocol deviation (G-75): 1,968 test detractors are enough to evaluate the classifier; moving the cutoff after seeing the shares would be a post-hoc change. Reported in s09 with the absolute count (G-54) (experiment lead (Wu Qianzong), 2026-10-20)

| Item | Value |
| --- | --- |
| development prevalence | 14.78% |
| test prevalence | 10.38% |
| prevalence gap | -4.41% |
| development / test detractors | 11,493 / 1,968 |

**Check** test keeps >= 15% of eligible reviewed orders: PASS (18,966 of 97,170 = 19.52%) **Check** test keeps >= 15% of all eligible detractors, or a recorded team deviation: PASS (1,968 of 13,488 = 14.59%: below the minimum, accepted deviation G-75)

**Files** (stages/s05\_partition/classification/outputs/, run 20261020T073908Z): counts.json, checks.json

## 5.5 CV folds

**Approved solution:** Five time-ordered expanding folds on development (`TimeSeriesSplit` style, equal-sized validation blocks); boundary dates recorded in `protocol.yaml` (data-dependent layer). Anti-temporal-leakage rule: in every fold, training holds only orders purchased before the validation block starts, never later ones; asserted per fold (max training purchase time < min validation purchase time)

**What was done:** 5 expanding folds on development, validation blocks of 12,956 orders each (last block takes the remainder); boundaries written to protocol.yaml data\_dependent.fold\_boundaries; training strictly before validation in every fold.

| fold | train\_start | train\_end | validation\_start | validation\_end | validation\_rows\_before | train\_rows | validation\_rows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2017-01-05 11:56:06 | 2017-06-13 03:24:05 | 2017-06-17 23:50:22 | 2017-09-26 09:23:05 | 12,956 | 11,077 | 12,956 |
| 2 | 2017-01-05 11:56:06 | 2017-09-21 09:04:59 | 2017-09-26 09:37:01 | 2017-12-02 18:56:39 | 12,956 | 23,573 | 12,950 |
| 3 | 2017-01-05 11:56:06 | 2017-11-29 19:35:55 | 2017-12-02 19:00:27 | 2018-02-04 16:04:56 | 12,956 | 33,568 | 12,941 |
| 4 | 2017-01-05 11:56:06 | 2018-02-01 13:41:36 | 2018-02-04 16:10:12 | 2018-03-31 20:05:18 | 12,956 | 47,933 | 12,925 |
| 5 | 2017-01-05 11:56:06 | 2018-03-28 11:52:01 | 2018-03-31 20:10:17 | 2018-05-23 11:29:51 | 12,956 | 60,361 | 10,251  |

&#91;image: Partition diagram, classification\]

**Check** every fold: max training purchase time < min validation purchase time: PASS **Check** five folds with equal-sized validation blocks before maturity drops: PASS (12,956, 12,956, 12,956, 12,956, 12,956)

**Files** (stages/s05\_partition/classification/outputs/, run 20261020T073908Z): folds.csv, fold\_summary.csv, figures/partition\_diagram.png, figures/partition\_diagram.csv, figures/partition\_diagram.json, checks.json

## 5.6 Fold customer purge

**Approved solution:** In each fold, training orders whose customer\_unique\_id appears in that validation block are removed, so no customer is on both sides, as at the test boundary; asserted per fold (no shared customer\_unique\_id between training and validation, counts logged)

**What was done:** Training orders whose customer\_unique\_id appears in the fold's validation block removed: fold 1 is 123, fold 2 is 211, fold 3 is 265, fold 4 is 251, fold 5 is 340 rows.

| fold | train\_rows\_before | purged\_customers\_rows |
| --- | --- | --- |
| 1 | 12,956 | 123 |
| 2 | 25,912 | 211 |
| 3 | 38,868 | 265 |
| 4 | 51,824 | 251 |
| 5 | 64,780 | 340 |

**Check** every fold: no shared customer\_unique\_id between training and validation: PASS

**Files** (stages/s05\_partition/classification/outputs/, run 20261020T073908Z): folds.csv, fold\_summary.csv, checks.json

## 5.7 Label maturity

**Approved solution:** A label counts only from the moment it was observable: lead\_days at the delivery timestamp, is\_detractor at the last review answer. Training rows: keep an order only if its label was observable before its fold's validation block starts. Validation rows: keep an order only if its label was observable before the task's test cutoff. Rows dropped by this rule are counted per fold

**What was done (round 2, reworded):** A training order is used only if its answer (is\_detractor, known on its review answer date) was already known on the day its fold's validation block starts; a validation order only if its answer was known before the test cutoff. Dropped rows per fold are in the table below.

**Reasoning:** Each fold imitates training the model on the day the validation block starts. An order bought before that day but reviewed after it had no answer yet on that day, so learning from it would use information from the future. Most dropped rows are the last few weeks of orders before each boundary, not yet delivered or reviewed then. Example: validation starts 1 Dec; an order bought 20 Nov and reviewed 8 Dec is left out of that fold's training.

| fold | train\_immature\_rows | validation\_rows\_before | validation\_immature\_rows |
| --- | --- | --- | --- |
| 1 | 1,756 | 12,956 | 0 |
| 2 | 2,128 | 12,956 | 6 |
| 3 | 5,035 | 12,956 | 15 |
| 4 | 3,640 | 12,956 | 31 |
| 5 | 4,079 | 12,956 | 2,705 |

**Check** every fold: every training label observable before the validation block starts: PASS (16,638 training rows dropped over the folds) **Check** every validation label observable before the test cutoff: PASS (2,757 validation rows dropped)

**Files** (stages/s05\_partition/classification/outputs/, run 20261020T073908Z): folds.csv, fold\_summary.csv, checks.json

## 5.8 Class support and training size

**Approved solution:** Both tasks: every fold's training part holds at least the minimum number of rows pre-registered in protocol.yaml (G-53). Classification also: positives and prevalence per fold, training and validation; minimum count pre-registered in `protocol.yaml`; a boundary may move only before s06 runs, logged in CHANGELOG

**What was done:** Training rows per fold: fold 1 is 11,077, fold 2 is 23,573, fold 3 is 33,568, fold 4 is 47,933, fold 5 is 60,361 (minimum 10,000, pre-registered); detractors training / validation: fold 1 is 1,410 / 1,440, fold 2 is 2,798 / 1,985, fold 3 is 3,993 / 1,953, fold 4 is 6,312 / 2,811, fold 5 is 8,694 / 1,108 (minimum 100).

| fold | train\_rows | train\_positives | train\_prevalence | validation\_positives | validation\_prevalence |
| --- | --- | --- | --- | --- | --- |
| 1 | 11,077 | 1,410 | 0.1273 | 1,440 | 0.1111 |
| 2 | 23,573 | 2,798 | 0.1187 | 1,985 | 0.1533 |
| 3 | 33,568 | 3,993 | 0.1190 | 1,953 | 0.1509 |
| 4 | 47,933 | 6,312 | 0.1317 | 2,811 | 0.2175 |
| 5 | 60,361 | 8,694 | 0.1440 | 1,108 | 0.1081 |

**Check** every fold: training rows >= 10,000 (G-53): PASS (fold 1 is 11,077; fold 2 is 23,573; fold 3 is 33,568; fold 4 is 47,933; fold 5 is 60,361) **Check** every fold: both classes present, >= 100 detractors in training and in validation: PASS (fold 1 is 1,410 / 1,440; fold 2 is 2,798 / 1,985; fold 3 is 3,993 / 1,953; fold 4 is 6,312 / 2,811; fold 5 is 8,694 / 1,108)

**Files** (stages/s05\_partition/classification/outputs/, run 20261020T073908Z): fold\_summary.csv, counts.json, checks.json
