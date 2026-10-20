# s05 Partition › regression — evidence cards

Round 1 · run `20261020T073917Z` · 9 checks, all PASS. Coverage and review dropdowns are on the parent tab "s05 Partition"; comment on any card here.

## 5.1 Order

**Approved solution:** Sort each task's eligible orders by purchase timestamp, earliest first

**What was done:** 96,166 eligible regression orders sorted by purchase\_ts (ties by order\_id): 76,925 development orders before the s02 cutoff 2018-05-27 12:30:34, 19,241 on or after it.

| Item | Value |
| --- | --- |
| eligible orders | 96,166 |
| development (before the cutoff) | 76,925 |
| on or after the cutoff | 19,241 |
| test cutoff (s02) | 2018-05-27 12:30:34 |

**Files** (stages/s05\_partition/regression/outputs/, run 20261020T073917Z):

## 5.2 Test cohort

**Approved solution:** Newest 20% per task, computed fresh: the cutoff is the purchase timestamp at the 80% position of that task's eligible orders (after the s02 row-local population rules, before the outlier rule; G-67). It is computed in s02, recorded in protocol.yaml (data-dependent layer), and the exact IDs are frozen in `test_manifest.csv`. The cohort is defined only by this experiment's data and rules and is a new held-out test (G-38)

**What was done:** Test cohort: every eligible order purchased on or after 2018-05-27 12:30:34; after the purge 18,788 order\_ids frozen in test\_manifest.csv (2018-05-27 12:30:34 to 2018-08-29 15:00:37).

**Conclusion:** Defined only by this experiment's data and rules (G-38).

| Item | Value |
| --- | --- |
| test orders (after the purge) | 18,788 |
| test customers | 18,578 |
| share of eligible orders | 19.54% |

**Check** no test order\_id or customer\_unique\_id in development: PASS (453 repeat-customer test orders removed) **Check** never a random split: test is every eligible order on or after the cutoff, minus repeat customers: PASS

**Files** (stages/s05\_partition/regression/outputs/, run 20261020T073917Z): test\_manifest.csv, counts.json

## 5.3 Test-side purge

**Approved solution:** Remove test orders whose `customer_unique_id` also appears in development (count logged). The test cohort is then new customers only, named a "new-customer time-ordered holdout" and always stated with its actual share of eligible orders after the purge and the share the purge removed (G-48)

**What was done:** 453 test orders (2.35%) belong to customers who also bought in development and were removed. The new-customer time-ordered holdout holds 18,788 orders, 19.54% of eligible orders after the purge.

| Item | Value |
| --- | --- |
| orders on or after the cutoff | 19,241 |
| removed: customer also in development | 453 (2.35%) |
| test orders kept | 18,788 |
| cohort name | new-customer time-ordered holdout |

**Check** no test order\_id or customer\_unique\_id in development: PASS (453 repeat-customer test orders removed)

**Files** (stages/s05\_partition/regression/outputs/, run 20261020T073917Z): test\_manifest.csv, counts.json

## 5.4 Test checks

**Approved solution:** Per task (G-46): regression test keeps at least 15% of eligible delivered orders; classification test keeps at least 15% of eligible reviewed orders and at least 15% of all eligible detractors; train–test prevalence gap reported. On failure: alert the team and stop, never a random split

**What was done:** test keeps >= 15% of eligible delivered orders: PASS (18,788 of 96,166 = 19.54%). lead\_days: development mean 13.42 / median 11.17; test mean 8.74 / median 7.43 days.

**Reasoning:** The test cohort is later in time; a gap here is the drift the test score has to face, not a split error. No random fallback exists.

| Item | Value |
| --- | --- |
| development mean lead days | 13.42 |
| test mean lead days | 8.74 |
| development median lead days | 11.17 |
| test median lead days | 7.43 |

**Check** test keeps >= 15% of eligible delivered orders: PASS (18,788 of 96,166 = 19.54%)

**Files** (stages/s05\_partition/regression/outputs/, run 20261020T073917Z): counts.json, checks.json

## 5.5 CV folds

**Approved solution:** Five time-ordered expanding folds on development (`TimeSeriesSplit` style, equal-sized validation blocks); boundary dates recorded in `protocol.yaml` (data-dependent layer). Anti-temporal-leakage rule: in every fold, training holds only orders purchased before the validation block starts, never later ones; asserted per fold (max training purchase time < min validation purchase time)

**What was done:** 5 expanding folds on development, validation blocks of 12,820 orders each (last block takes the remainder); boundaries written to protocol.yaml data\_dependent.fold\_boundaries; training strictly before validation in every fold.

| fold | train\_start | train\_end | validation\_start | validation\_end | validation\_rows\_before | train\_rows | validation\_rows |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2017-01-05 11:56:06 | 2017-06-15 17:52:57 | 2017-06-19 15:25:29 | 2017-09-27 08:48:59 | 12,820 | 11,297 | 12,820 |
| 2 | 2017-01-05 11:56:06 | 2017-09-25 12:23:20 | 2017-09-27 08:56:52 | 2017-12-03 17:07:46 | 12,820 | 23,864 | 12,820 |
| 3 | 2017-01-05 11:56:06 | 2017-12-01 08:49:02 | 2017-12-03 17:11:47 | 2018-02-05 00:05:58 | 12,820 | 33,927 | 12,818 |
| 4 | 2017-01-05 11:56:06 | 2018-02-02 15:26:38 | 2018-02-05 00:06:00 | 2018-04-01 16:46:20 | 12,820 | 47,957 | 12,811 |
| 5 | 2017-01-05 11:56:06 | 2018-03-29 01:12:21 | 2018-04-01 16:51:42 | 2018-05-24 18:56:59 | 12,820 | 59,880 | 10,740 |

&#91;image: Partition diagram, regression\]

**Check** every fold: max training purchase time < min validation purchase time: PASS **Check** five folds with equal-sized validation blocks before maturity drops: PASS (12,820, 12,820, 12,820, 12,820, 12,820)

**Files** (stages/s05\_partition/regression/outputs/, run 20261020T073917Z): folds.csv, fold\_summary.csv, figures/partition\_diagram.png, figures/partition\_diagram.csv, figures/partition\_diagram.json, checks.json

## 5.6 Fold customer purge

**Approved solution:** In each fold, training orders whose customer\_unique\_id appears in that validation block are removed, so no customer is on both sides, as at the test boundary; asserted per fold (no shared customer\_unique\_id between training and validation, counts logged)

**What was done:** Training orders whose customer\_unique\_id appears in the fold's validation block removed: fold 1 is 123, fold 2 is 209, fold 3 is 264, fold 4 is 254, fold 5 is 343 rows.

| fold | train\_rows\_before | purged\_customers\_rows |
| --- | --- | --- |
| 1 | 12,825 | 123 |
| 2 | 25,645 | 209 |
| 3 | 38,465 | 264 |
| 4 | 51,285 | 254 |
| 5 | 64,105 | 343 |

**Check** every fold: no shared customer\_unique\_id between training and validation: PASS

**Files** (stages/s05\_partition/regression/outputs/, run 20261020T073917Z): folds.csv, fold\_summary.csv, checks.json

## 5.7 Label maturity

**Approved solution:** A label counts only from the moment it was observable: lead\_days at the delivery timestamp, is\_detractor at the last review answer. Training rows: keep an order only if its label was observable before its fold's validation block starts. Validation rows: keep an order only if its label was observable before the task's test cutoff. Rows dropped by this rule are counted per fold

**What was done (round 2, reworded):** A training order is used only if its answer (lead\_days, known on its delivery date) was already known on the day its fold's validation block starts; a validation order only if its answer was known before the test cutoff. Dropped: fold 1 is 1,405 train / 0 validation, fold 2 is 1,572 train / 0 validation, fold 3 is 4,274 train / 2 validation, fold 4 is 3,074 train / 9 validation, fold 5 is 3,882 train / 2,080 validation.

**Reasoning:** Each fold imitates training the model on the day the validation block starts. An order bought before that day but delivered after it had no answer yet on that day, so learning from it would use information from the future. Most dropped rows are the last few weeks of orders before each boundary, still in transit then. Example: validation starts 1 Dec; an order bought 20 Nov and delivered 5 Dec is left out of that fold's training.

| fold | train\_immature\_rows | validation\_rows\_before | validation\_immature\_rows |
| --- | --- | --- | --- |
| 1 | 1,405 | 12,820 | 0 |
| 2 | 1,572 | 12,820 | 0 |
| 3 | 4,274 | 12,820 | 2 |
| 4 | 3,074 | 12,820 | 9 |
| 5 | 3,882 | 12,820 | 2,080 |

**Check** every fold: every training label observable before the validation block starts: PASS (14,207 training rows dropped over the folds) **Check** every validation label observable before the test cutoff: PASS (2,091 validation rows dropped)

**Files** (stages/s05\_partition/regression/outputs/, run 20261020T073917Z): folds.csv, fold\_summary.csv, checks.json

## 5.8 Class support and training size

**Approved solution:** Both tasks: every fold's training part holds at least the minimum number of rows pre-registered in protocol.yaml (G-53). Classification also: positives and prevalence per fold, training and validation; minimum count pre-registered in `protocol.yaml`; a boundary may move only before s06 runs, logged in CHANGELOG

**What was done:** Training rows per fold: fold 1 is 11,297, fold 2 is 23,864, fold 3 is 33,927, fold 4 is 47,957, fold 5 is 59,880 (minimum 10,000, pre-registered).

| fold | train\_rows | train\_mean\_lead\_days | validation\_mean\_lead\_days |
| --- | --- | --- | --- |
| 1 | 11,297 | 12.0263 | 11.5003 |
| 2 | 23,864 | 11.7163 | 13.8830 |
| 3 | 33,927 | 11.7023 | 14.6180 |
| 4 | 47,957 | 12.5868 | 16.5532 |
| 5 | 59,880 | 13.1094 | 9.6289 |

**Check** every fold: training rows >= 10,000 (G-53): PASS (fold 1 is 11,297; fold 2 is 23,864; fold 3 is 33,927; fold 4 is 47,957; fold 5 is 59,880)

**Files** (stages/s05\_partition/regression/outputs/, run 20261020T073917Z): fold\_summary.csv, counts.json, checks.json
