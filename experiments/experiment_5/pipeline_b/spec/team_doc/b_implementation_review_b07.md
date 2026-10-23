# B7 Tuning — implementation review

**Round 1 · ACCEPTED by the experiment lead (2026-10-24, tag e5-B-s07-accepted) · team review at the B8 gate (G-78).** Runs `20261023T163311Z` (regression) and `20261023T164241Z` (classification) on code commit e358f81, clean tree; a second run is byte-identical. 6 + 6 checks, all PASS. Evidence cards are in the two sub-tabs. B7 runs A's own s07 code unchanged on B's inputs (B4 recipes, B5 folds, B2 rows) through e5b/adapter.py.

## Current (round 1)

### Coverage

| Task | ID | Coverage | Checks | Review |
| --- | --- | --- | --- | --- |
| regression | B7.1 | IMPLEMENTED | PASS | Open |
| regression | B7.3 | IMPLEMENTED | PASS | Open |
| regression | B7.4 | IMPLEMENTED | PASS | Open |
| regression | B7.5 | IMPLEMENTED | PASS | Open |
| regression | B7.6 | IMPLEMENTED | — | Open |
| regression | B7.7 | IMPLEMENTED | PASS | Open |
| classification | B7.2 | IMPLEMENTED | PASS | Open |
| classification | B7.3 | IMPLEMENTED | PASS | Open |
| classification | B7.4 | IMPLEMENTED | PASS | Open |
| classification | B7.5 | IMPLEMENTED | PASS | Open |
| classification | B7.6 | IMPLEMENTED | — | Open |
| classification | B7.7 | IMPLEMENTED | PASS | Open |

### Points for review

1. **Plain B6 models are carried in every family, both tasks (G-55).** No tuned configuration beats its plain B6 model by more than one SE (plain\_vs\_tuned.csv).
2. **Closest call: tuned logistic.** The classification one-SE choice (clf.sel.log.logistic.C=0.01.class\_weight=none) scores 0.2734 against the plain 0.2616: paired gain +0.0118 (paired SE 0.0051), better in 4 of 5 folds. It stays within one fold SE (0.0318), so the plain model is carried, as in A. The grid-edge check and the final model choice are made at the B8 gate.
3. **Grids are A's, unchanged** (pre-registered in protocol.yaml); the grid point with the s06 plain settings reproduces B6's fold scores, and per-fold refits reproduce the grid scores (checks).
4. **Same method as A, proven.** tests/test\_adapter.py reproduces A's accepted s07 regression outputs exactly through the B adapter.
5. **Scores are selection scores (G-10)**, not generalisation estimates; the A–B comparison and test come later (B8, joint test run).

## Round history

### Round 1 — 2026-10-24

- First build (B-CR-09): e5b/adapter.py and e5b/b07.py; equivalence test 4 of 4 pass. Accepted by the experiment lead after a clean rerun (tag e5-B-s07-accepted).
- Henry: no comments yet; the team reviews B6–B8 together at the B8 gate.
