# B10 Release — round 3, for team review

**Built · clean runs 20261027T044744Z (regression), 20261027T044819Z (classification) on 906fe39, all checks PASS; byte-identical on a second run.** Round 3 (B-G-10, blueprint §8) adds A's fallback test cost and the combined serving-rule line; every other figure equals round 2. Built by Henry's Claude on branch e5/b10-henry. Not tagged: Benson tags after he approves. Round 2 tabs stay as published.

## What changed in round 3

1. **A's fallback cost on the test (audit B10-F2).** A at 1/6 on its test rows outside B's scope: 1,428 alerts, 190 TP, 1,238 FP, 170 FN; precision 0.133, recall 0.528; cost 2,088 at 5:1 and 1,408 at 1:1. From the labels already saved by T1, as B's test rows; precision and recall equal B9.15's test row (check).
2. **Combined serving rule, B 4/15 + A 1/6.** Test (post-test view): 20.5 alerts/day, precision 0.192, recall 0.198, cost 9,211 at 5:1 and 3,115 at 1:1 (B's part 7,123 at 5:1). Validation: 10.5 alerts/day, precision 0.305, recall 0.124.
3. **Unchanged:** thresholds (4/15 operating, 1/6 frozen, A 1/6), parity, router, input checks, drift profile, app sources; the frozen 1/6 T1 result stays the unbiased test result (G-79). Regression outputs equal round 2 in content.

## Decisions for Benson to ratify

- B-G-10: A's fallback test cost and the combined line (this round).
- B-G-11: the report cites A's s03 EDA numbers from A's frozen tree.

## Coverage

| Task | Evidence | Status | Review |
| --- | --- | --- | --- |
| regression | B10.1 | IMPLEMENTED | Open |
| regression | B10.2 | IMPLEMENTED | Open |
| regression | B10.3 | IMPLEMENTED | Open |
| regression | B10.4 | IMPLEMENTED | Open |
| regression | B10.5 | IMPLEMENTED | Open |
| regression | B10.6 | IMPLEMENTED | Open |
| regression | B10.7 | IMPLEMENTED | Open |
| classification | B10.1 | IMPLEMENTED | Open |
| classification | B10.2 | IMPLEMENTED | Open |
| classification | B10.3 | IMPLEMENTED | Open |
| classification | B10.4 | IMPLEMENTED | Open |
| classification | B10.5 | IMPLEMENTED | Open |
| classification | B10.6 | IMPLEMENTED | Open |
| classification | B10.7 | IMPLEMENTED | Open |

## Next

On Benson's approval: tag the round-3 commit. Then, each only when ordered: sign-off and e5-release-1, migration (lead), reproduction check, app and dashboard build.
