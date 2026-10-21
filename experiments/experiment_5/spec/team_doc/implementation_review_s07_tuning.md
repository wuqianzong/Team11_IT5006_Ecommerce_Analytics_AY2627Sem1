# s07 Tuning — implementation review

> **ACCEPTED · round 2 · 2026-10-21 · tag e5-s07-accepted · accepted by the experiment lead under G-78.** Accepted runs 20261021T042137Z (regression) and 20261021T042900Z (classification) on a clean tree (code commit 7eb8197). Round 2 differs from round 1 only in the validation-curve figures. The agreed one-SE rule is kept: the plain s06 model is carried in every family and the ladder ends at linear/logistic in both tasks; the paired gains and best-mean grid points stay description only, and a paired-SE rule is left for the team at the combined s08 review. Class weight: none is treated as simpler than balanced, as built.

**Round 1 · LEAD REVIEW (G-78)** · runs `20261021T035843Z` (regression) and `20261021T040619Z` (classification) · coverage 6 of 6 per task, 0 MISSING · 6 + 6 checks, all PASS. Under G-78 the experiment lead reviews and accepts s07 on its own; the team reviews s06, s07 and s08 together at the s08 gate, before anything reads the test cohort. Evidence cards are in the two sub-tabs. Nothing is committed until s07 is accepted (G-64).

## Current (round 1)

### Coverage

| Task | ID | Solution step | Coverage | Checks | Review |
| --- | --- | --- | --- | --- | --- |
| regression | 7.1 | Linear (regression) | IMPLEMENTED | PASS | Open |
| regression | 7.3 | Decision tree | IMPLEMENTED | PASS | Open |
| regression | 7.4 | Random forest | IMPLEMENTED | PASS | Open |
| regression | 7.5 | Search method | IMPLEMENTED | PASS | Open |
| regression | 7.6 | Overfitting check | IMPLEMENTED | — | Open |
| regression | 7.7 | Outputs | IMPLEMENTED | PASS | Open |
| classification | 7.2 | Logistic (classification) | IMPLEMENTED | PASS | Open |
| classification | 7.3 | Decision tree | IMPLEMENTED | PASS | Open |
| classification | 7.4 | Random forest | IMPLEMENTED | PASS | Open |
| classification | 7.5 | Search method | IMPLEMENTED | PASS | Open |
| classification | 7.6 | Overfitting check | IMPLEMENTED | — | Open |
| classification | 7.7 | Outputs | IMPLEMENTED | PASS | Open |

### Summary

Each family's grid gives a one-SE choice (the simplest configuration within one SE of the best mean); that choice replaces the plain s06 model only if it beats it by more than one SE (G-55). The ladder over the carried families keeps a more complex family only on the same rule (description only; s08 chooses).

| Task | Carried per family | Ladder result |
| --- | --- | --- |
| regression | linear/logistic: plain; single tree: plain; forest: plain | linear/logistic |
| classification | linear/logistic: plain; single tree: plain; forest: plain | linear/logistic |

### Points for review

1. **The agreed rule carries every plain s06 model (7.5).** Inside each grid the fold SE also carries the level differences between folds (drift), so the one-SE choice lands on or near the simplest corner of the grid, and that choice does not beat the plain model by more than one SE. The paired figures show where tuning does help consistently, for description only: Regression: linear/logistic best-mean point +0.0081 days vs plain (paired SE 0.0035, better in 4 of 5 folds), one-SE choice +0.0059 days (better in 4 of 5); single tree best-mean point +0.0483 days vs plain (paired SE 0.0239, better in 4 of 5 folds), one-SE choice -0.0088 days (better in 1 of 5); forest best-mean point +0.0893 days vs plain (paired SE 0.0186, better in 5 of 5 folds), one-SE choice -0.1338 days (better in 0 of 5). Classification: linear/logistic best-mean point +0.0118 vs plain (paired SE 0.0045, better in 5 of 5 folds), one-SE choice +0.0118 (better in 5 of 5); single tree best-mean point +0.0058 vs plain (paired SE 0.0037, better in 5 of 5 folds), one-SE choice -0.0024 (better in 2 of 5); forest best-mean point +0.0019 vs plain (paired SE 0.0008, better in 4 of 5 folds), one-SE choice -0.0012 (better in 1 of 5). Changing the rule (for example a paired SE) would be a protocol change (G-33, G-55) and is not made here; I suggest the team looks at it at the combined s08 review, before any test score exists. For decision at the s08 gate.
2. **The one-SE choice can be worse than the plain model.** Example: the regression forest's one-SE choice (shallow, large leaf) is worse than the plain s06 forest in every fold; the rule then keeps the plain forest, so nothing worse is carried. For information.
3. **Class weight in the simplicity order (7.2–7.4).** The blueprint orders alpha, C, depth and leaf but not class weight; I treat no class weight as simpler than balanced. Please confirm.
4. **Deterministic search.** Every estimator runs on one thread and GridSearchCV runs the configurations in parallel, so two reruns give byte-identical outputs (checked); fit times are in \_manifest.json. The grid point with the s06 plain settings reproduces the s06 fold scores exactly (check).
5. **Figure fix pending.** In the validation-curve figures the dashed training lines do not use the colour of their validation series; fixed in the next round together with any comments.

## Round history

### Round 1 — 2026-10-21

- First build of s07 for both tasks: new foundation module e5lib/tuning.py with tests/test\_tuning.py (55 tests pass). The foundation change made s01–s06 stale; they were rerun with byte-identical outputs and stay ACCEPTED.
- Comments and resolutions: none yet.

### Round 2 and acceptance — 2026-10-21

- The experiment lead accepted s07 (G-78), keeping the agreed one-SE rule.
- Code committed first (7eb8197), with the figure fix: the dashed training lines of the validation curves now use the colour of their validation series. s01–s07 rerun on the clean tree (dirty false): s01–s06 byte-identical; s07 identical to round 1 except the six figures. Round 2 packed, committed and tagged e5-s07-accepted; s08 unlocks.
