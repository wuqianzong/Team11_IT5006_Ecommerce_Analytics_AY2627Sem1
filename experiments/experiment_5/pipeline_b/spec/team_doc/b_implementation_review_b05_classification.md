# B5 › classification — evidence cards

Round 1 · ACCEPTED by the experiment lead (tag e5-B-s05-accepted) · run `20261023T160533Z` on code commit 19b5355 (clean tree) · 5 checks, all PASS. Coverage and review dropdowns are on the parent tab "B5 Partition"; comment on any card here.

## B5.1 Fold membership

**Approved solution (B5 blueprint):** B folds = A's folds ∩ B's development rows, joined on order\_id. Each (fold, role) row of A is kept when its order is a B row; no new boundaries, no re-purging, no re-ordering. An order keeps every (fold, role) it has in A (expanding windows). B rows outside A's folds (removed by A's customer purge or label-maturity rules) are not used; they are listed with reason NOT\_IN\_A\_FOLDS in exclusions\_B5.csv and counted.

**What was done:** A's five folds restricted to B's rows: 185,308 fold rows covering 59,182 B orders; 2,076 B2 rows are outside A's folds (A's customer purge or label maturity) and are not used.

**Rows outside A's folds** (exclusions\_B5.csv): 2,076, reason NOT\_IN\_A\_FOLDS.

**Check** every B fold row exists in A's folds.csv with the same fold and role: PASS (185,308 fold rows) **Check** no B fold row is in A's test manifest; every fold order is a B2 row: PASS **Check** B2 rows = orders in B folds + NOT\_IN\_A\_FOLDS rows: PASS (61,258 = 59,182 + 2,076)

**Files** (pipeline\_b/stages/b05/classification/outputs/, run 20261023T160533Z): exclusions\_B5.csv, folds\_B.csv

## B5.2 Sizes, dates and class support

**Approved solution (B5 blueprint):** Date ranges per fold and role from B's rows, next to A's boundaries, so the periods can be checked as identical.

**What was done:** Per fold, training / validation rows: 1: 7,592 / 10,324 (874 / 1,014 detractors); 2: 17,595 / 10,342 (1,872 / 1,443 detractors); 3: 25,529 / 10,450 (2,734 / 1,497 detractors); 4: 37,140 / 10,453 (4,472 / 2,173 detractors); 5: 47,237 / 8,646 (6,363 / 873 detractors).

**Sizes per fold, B next to A** (fold\_summary\_B.csv):

| fold | train\_rows | a\_train\_rows | validation\_rows | a\_validation\_rows | train\_positives | train\_prevalence | validation\_positives | validation\_prevalence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 7,592 | 11,077 | 10,324 | 12,956 | 874 | 0.115 | 1,014 | 0.098 |
| 2 | 17,595 | 23,573 | 10,342 | 12,950 | 1,872 | 0.106 | 1,443 | 0.140 |
| 3 | 25,529 | 33,568 | 10,450 | 12,941 | 2,734 | 0.107 | 1,497 | 0.143 |
| 4 | 37,140 | 47,933 | 10,453 | 12,925 | 4,472 | 0.120 | 2,173 | 0.208 |
| 5 | 47,237 | 60,361 | 8,646 | 10,251 | 6,363 | 0.135 | 873 | 0.101 |

**Dates: A's boundaries and B's first and last row** (fold\_summary\_B.csv):

| fold | a\_train\_start | a\_train\_end | train\_first | train\_last | a\_validation\_start | a\_validation\_end | validation\_first | validation\_last |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2017-01-05 11:56:06 | 2017-06-13 03:24:05 | 2017-02-12 00:20:45 | 2017-06-13 03:24:05 | 2017-06-17 23:50:22 | 2017-09-26 09:23:05 | 2017-06-17 23:50:22 | 2017-09-26 09:10:27 |
| 2 | 2017-01-05 11:56:06 | 2017-09-21 09:04:59 | 2017-02-12 00:20:45 | 2017-09-21 09:04:59 | 2017-09-26 09:37:01 | 2017-12-02 18:56:39 | 2017-09-26 09:37:01 | 2017-12-02 18:56:39 |
| 3 | 2017-01-05 11:56:06 | 2017-11-29 19:35:55 | 2017-02-12 00:20:45 | 2017-11-29 19:35:55 | 2017-12-02 19:00:27 | 2018-02-04 16:04:56 | 2017-12-02 19:00:27 | 2018-02-04 16:04:56 |
| 4 | 2017-01-05 11:56:06 | 2018-02-01 13:41:36 | 2017-02-12 00:20:45 | 2018-02-01 13:41:36 | 2018-02-04 16:10:12 | 2018-03-31 20:05:18 | 2018-02-04 16:10:12 | 2018-03-31 20:05:18 |
| 5 | 2017-01-05 11:56:06 | 2018-03-28 11:52:01 | 2017-02-12 00:20:45 | 2018-03-28 11:52:01 | 2018-03-31 20:10:17 | 2018-05-23 11:29:51 | 2018-03-31 20:10:17 | 2018-05-23 11:29:51 |

**Check** B folds keep A's periods: every B row lies inside A's fold boundaries: PASS

**Files** (pipeline\_b/stages/b05/classification/outputs/, run 20261023T160533Z): fold\_summary\_B.csv

## B5.3 Minimums and B-G-01 safeguard

**Approved solution (B5 blueprint):** Sizes and class support per fold and role, against A's minimums (protocol cv.minimums: 10,000 training rows per fold; classification 100 detractors in each training and validation part) and the B-G-01 safeguard (fold 1: at least 5,000 training rows; classification at least 300 training detractors).

**What was done:** Minimums: 16 PASS, 1 accepted deviation, 0 FAIL. Fold 1 training rows: 7,592 of 10,000 (B-G-01).

**Minimums** (minimums\_B.csv):

| fold | minimum | required | observed | status |
| --- | --- | --- | --- | --- |
| 1 | training rows | 10,000 | 7,592 | ACCEPTED DEVIATION (B-G-01) |
| 1 | train detractors | 100 | 874 | PASS |
| 1 | validation detractors | 100 | 1,014 | PASS |
| 2 | training rows | 10,000 | 17,595 | PASS |
| 2 | train detractors | 100 | 1,872 | PASS |
| 2 | validation detractors | 100 | 1,443 | PASS |
| 3 | training rows | 10,000 | 25,529 | PASS |
| 3 | train detractors | 100 | 2,734 | PASS |
| 3 | validation detractors | 100 | 1,497 | PASS |
| 4 | training rows | 10,000 | 37,140 | PASS |
| 4 | train detractors | 100 | 4,472 | PASS |
| 4 | validation detractors | 100 | 2,173 | PASS |
| 5 | training rows | 10,000 | 47,237 | PASS |
| 5 | train detractors | 100 | 6,363 | PASS |
| 5 | validation detractors | 100 | 873 | PASS |
| 1 | B-G-01 safeguard: training rows | 5,000 | 7,592 | PASS |
| 1 | B-G-01 safeguard: training detractors | 300 | 874 | PASS |

**Check** minimums met, or fold 1's training-row shortfall accepted under B-G-01 within its safeguard: PASS (fold 1 training rows 7,592)

**Files** (pipeline\_b/stages/b05/classification/outputs/, run 20261023T160533Z): minimums\_B.csv
