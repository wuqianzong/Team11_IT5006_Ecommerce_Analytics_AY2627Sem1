# B5 › regression — evidence cards

## Supplement for decisions and the report (added 2026-10-24; DOC\_GAPS D-03)

Added after the pipeline ran, from accepted outputs only; nothing above is changed. Charts marked doc\_support come from pipeline\_b/stages/doc\_support/regression/outputs (run 20261024T065707Z, uncommitted, reads accepted outputs only).

**Partition diagram: A's fold boundaries with B's and A's rows** (doc\_support figures/b5\_partition.png; data: b05 fold\_summary\_B.csv):

&#91;image: partition\]

Round 1 · ACCEPTED by the experiment lead (tag e5-B-s05-accepted) · run `20261023T160529Z` on code commit 19b5355 (clean tree) · 5 checks, all PASS. Coverage and review dropdowns are on the parent tab "B5 Partition"; comment on any card here.

## B5.1 Fold membership

**Approved solution (B5 blueprint):** B folds = A's folds ∩ B's development rows, joined on order\_id. Each (fold, role) row of A is kept when its order is a B row; no new boundaries, no re-purging, no re-ordering. An order keeps every (fold, role) it has in A (expanding windows). B rows outside A's folds (removed by A's customer purge or label-maturity rules) are not used; they are listed with reason NOT\_IN\_A\_FOLDS in exclusions\_B5.csv and counted.

**What was done:** A's five folds restricted to B's rows: 187,873 fold rows covering 59,683 B orders; 1,550 B2 rows are outside A's folds (A's customer purge or label maturity) and are not used.

**Rows outside A's folds** (exclusions\_B5.csv): 1,550, reason NOT\_IN\_A\_FOLDS.

**Check** every B fold row exists in A's folds.csv with the same fold and role: PASS (187,873 fold rows) **Check** no B fold row is in A's test manifest; every fold order is a B2 row: PASS **Check** B2 rows = orders in B folds + NOT\_IN\_A\_FOLDS rows: PASS (61,233 = 59,683 + 1,550)

**Files** (pipeline\_b/stages/b05/regression/outputs/, run 20261023T160529Z): exclusions\_B5.csv, folds\_B.csv

## B5.2 Sizes, dates and class support

**Approved solution (B5 blueprint):** Date ranges per fold and role from B's rows, next to A's boundaries, so the periods can be checked as identical.

**What was done:** Per fold, training / validation rows: 1: 7,932 / 10,323; 2: 18,077 / 10,364; 3: 26,184 / 10,443; 4: 37,647 / 10,429; 5: 47,415 / 9,059.

**Sizes per fold, B next to A** (fold\_summary\_B.csv):

| fold | train\_rows | a\_train\_rows | validation\_rows | a\_validation\_rows |
| --- | --- | --- | --- | --- |
| 1 | 7,932 | 11,297 | 10,323 | 12,820 |
| 2 | 18,077 | 23,864 | 10,364 | 12,820 |
| 3 | 26,184 | 33,927 | 10,443 | 12,818 |
| 4 | 37,647 | 47,957 | 10,429 | 12,811 |
| 5 | 47,415 | 59,880 | 9,059 | 10,740 |

**Dates: A's boundaries and B's first and last row** (fold\_summary\_B.csv):

| fold | a\_train\_start | a\_train\_end | train\_first | train\_last | a\_validation\_start | a\_validation\_end | validation\_first | validation\_last |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2017-01-05 11:56:06 | 2017-06-15 17:52:57 | 2017-02-12 00:20:45 | 2017-06-15 17:52:57 | 2017-06-19 15:25:29 | 2017-09-27 08:48:59 | 2017-06-19 15:25:29 | 2017-09-27 08:48:59 |
| 2 | 2017-01-05 11:56:06 | 2017-09-25 12:23:20 | 2017-02-12 00:20:45 | 2017-09-25 12:23:20 | 2017-09-27 08:56:52 | 2017-12-03 17:07:46 | 2017-09-27 08:56:52 | 2017-12-03 17:04:39 |
| 3 | 2017-01-05 11:56:06 | 2017-12-01 08:49:02 | 2017-02-12 00:20:45 | 2017-12-01 08:49:02 | 2017-12-03 17:11:47 | 2018-02-05 00:05:58 | 2017-12-03 17:11:47 | 2018-02-05 00:05:58 |
| 4 | 2017-01-05 11:56:06 | 2018-02-02 15:26:38 | 2017-02-12 00:20:45 | 2018-02-02 15:26:38 | 2018-02-05 00:06:00 | 2018-04-01 16:46:20 | 2018-02-05 00:06:00 | 2018-04-01 16:46:20 |
| 5 | 2017-01-05 11:56:06 | 2018-03-29 01:12:21 | 2017-02-12 00:20:45 | 2018-03-29 01:12:21 | 2018-04-01 16:51:42 | 2018-05-24 18:56:59 | 2018-04-01 16:53:25 | 2018-05-24 18:56:59 |

**Check** B folds keep A's periods: every B row lies inside A's fold boundaries: PASS

**Files** (pipeline\_b/stages/b05/regression/outputs/, run 20261023T160529Z): fold\_summary\_B.csv

## B5.3 Minimums and B-G-01 safeguard

**Approved solution (B5 blueprint):** Sizes and class support per fold and role, against A's minimums (protocol cv.minimums: 10,000 training rows per fold; classification 100 detractors in each training and validation part) and the B-G-01 safeguard (fold 1: at least 5,000 training rows; classification at least 300 training detractors).

**What was done:** Minimums: 5 PASS, 1 accepted deviation, 0 FAIL. Fold 1 training rows: 7,932 of 10,000 (B-G-01).

**Minimums** (minimums\_B.csv):

| fold | minimum | required | observed | status |
| --- | --- | --- | --- | --- |
| 1 | training rows | 10,000 | 7,932 | ACCEPTED DEVIATION (B-G-01) |
| 2 | training rows | 10,000 | 18,077 | PASS |
| 3 | training rows | 10,000 | 26,184 | PASS |
| 4 | training rows | 10,000 | 37,647 | PASS |
| 5 | training rows | 10,000 | 47,415 | PASS |
| 1 | B-G-01 safeguard: training rows | 5,000 | 7,932 | PASS |

**Check** minimums met, or fold 1's training-row shortfall accepted under B-G-01 within its safeguard: PASS (fold 1 training rows 7,932)

**Files** (pipeline\_b/stages/b05/regression/outputs/, run 20261023T160529Z): minimums\_B.csv
