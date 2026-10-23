# B5 Partition — implementation review

**Round 1 · ACCEPTED by the experiment lead (2026-10-24, tag e5-B-s05-accepted) · team review open.** Runs `20261023T160529Z` (regression) and `20261023T160533Z` (classification) on code commit 19b5355, clean tree; a second run is byte-identical. Coverage 3 of 3 per task, 0 MISSING; 5 + 5 checks, all PASS. Evidence cards are in the two sub-tabs.

## Current (round 1)

### Coverage

| Task | ID | Solution step | Coverage | Checks | Review |
| --- | --- | --- | --- | --- | --- |
| regression | B5.1 | Fold membership | IMPLEMENTED | PASS | Open |
| regression | B5.2 | Sizes, dates and class support | IMPLEMENTED | PASS | Open |
| regression | B5.3 | Minimums and B-G-01 safeguard | IMPLEMENTED | PASS | Open |
| classification | B5.1 | Fold membership | IMPLEMENTED | PASS | Open |
| classification | B5.2 | Sizes, dates and class support | IMPLEMENTED | PASS | Open |
| classification | B5.3 | Minimums and B-G-01 safeguard | IMPLEMENTED | PASS | Open |

### Summary

B5 keeps A's five time-ordered folds and keeps a B row in each (fold, role) where A has it. There are no new boundaries, purges or reordering, so A and B are compared on the same periods (G-79, B-G-01).

| Task | Fold 5 rows (train + validation) | B2 rows outside A's folds | Fold 1 training rows | Fold 1 training detractors | Smallest validation part |
| --- | --- | --- | --- | --- | --- |
| regression | 56,474 | 1,550 | 7,932 | — | 9,059 |
| classification | 55,883 | 2,076 | 7,592 | 874 | 8,646 |

### Points for review

1. **Fold 1 is the only part below a minimum.** It has 7,932 (regression) and 7,592 (classification) training rows against 10,000. B-G-01 accepts this, and both are above the 5,000 safeguard. Fold 1 has 874 classification training detractors against the 300 safeguard (minimums\_B.csv).
2. **Every classification part keeps at least 100 detractors.** The smallest is 873, in the fold-5 validation part (fold\_summary\_B.csv).
3. **Rows outside A's folds** (1,550 regression, 2,076 classification) are B2 rows that A's purge or label-maturity rules leave out of every fold. They are listed in exclusions\_B5.csv and not used.
4. **Same periods as A.** Every B row lies inside A's fold boundaries (check B5.2). B8's adoption comparison and the B-C13 fold table therefore use identical periods for A and B.

## Round history

### Round 1 — 2026-10-24

- First build of B5 for both tasks (B-CR-07): e5b/b05.py. The blueprint was AGREED after the pre-build safeguard measurement. Accepted by the experiment lead after a clean rerun (tag e5-B-s05-accepted).
- Henry: no comments on B5 yet. B5 follows B-G-01 and supports B-C13.
