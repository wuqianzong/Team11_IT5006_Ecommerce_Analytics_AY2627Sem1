# B6 Training — implementation review

**Round 1 · ACCEPTED by the experiment lead (2026-10-24, tag e5-B-s06-accepted) · team review at the B8 gate (G-78).** Runs `20261023T162830Z` (regression) and `20261023T162918Z` (classification) on code commit e358f81, clean tree; a second run is byte-identical. 7 + 6 checks, all PASS. Evidence cards are in the two sub-tabs. B6 runs A's own s06 code unchanged on B's inputs (B4 recipes, B5 folds, B2 rows) through e5b/adapter.py.

## Current (round 1)

### Coverage

| Task | ID | Coverage | Checks | Review |
| --- | --- | --- | --- | --- |
| regression | B6.1 | IMPLEMENTED | PASS | Open |
| regression | B6.2 | IMPLEMENTED | PASS | Open |
| regression | B6.4 | IMPLEMENTED | PASS | Open |
| regression | B6.5 | IMPLEMENTED | — | Open |
| regression | B6.7 | IMPLEMENTED | PASS | Open |
| regression | B6.8 | IMPLEMENTED | — | Open |
| classification | B6.1 | IMPLEMENTED | PASS | Open |
| classification | B6.2 | IMPLEMENTED | PASS | Open |
| classification | B6.4 | IMPLEMENTED | PASS | Open |
| classification | B6.6 | IMPLEMENTED | — | Open |
| classification | B6.7 | IMPLEMENTED | PASS | Open |
| classification | B6.8 | IMPLEMENTED | — | Open |

### Points for review

1. **Ladder (B6.2).** Regression: Families basic to complex, validation mae mean ± SE over the folds: dummy 5.9689 ± 0.7107 days; linear/logistic 5.0247 ± 0.6115 days; single tree 5.0532 ± 0.6394 days; forest 4.9627 ± 0.6457 days. Ladder: linear/logistic kept over dummy; single tree not kept over linear/logistic; forest not kept over linear/logistic. One-SE choice over all four: linear/logistic (best mean: forest). Classification: Families basic to complex, validation ap mean ± SE over the folds: dummy 0.1380 ± 0.0198; linear/logistic 0.2616 ± 0.0349; single tree 0.2394 ± 0.0354; forest 0.2739 ± 0.0305. Ladder: linear/logistic kept over dummy; single tree not kept over linear/logistic; forest not kept over linear/logistic. One-SE choice over all four: linear/logistic (best mean: forest).
2. **Full rank in every fold (B6.7).** The linear/logistic design matrix is full rank in every training fold of both tasks, so B-G-02 works as intended (design\_matrix\_by\_fold.csv).
3. **Same method as A, proven.** tests/test\_adapter.py feeds A's own inputs through the B adapter and reproduces A's accepted s06 outputs exactly (both tasks). The only differences from A are B's inputs.
4. **Do not compare these scores with A's s06 tab.** A's s06 numbers come from different rows (all states, A's features). The like-for-like A–B comparison is in B8, on B's validation rows (G-79).
5. **Fold 1 is smaller** (B-G-01). Its scores carry more noise; the SEs above include it.

## Round history

### Round 1 — 2026-10-24

- First build (B-CR-09): e5b/adapter.py and e5b/b06.py; equivalence test 4 of 4 pass. Accepted by the experiment lead after a clean rerun (tag e5-B-s06-accepted).
- Henry: no comments yet; the team reviews B6–B8 together at the B8 gate.
