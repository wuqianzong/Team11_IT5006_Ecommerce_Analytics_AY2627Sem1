# B4 Features — implementation review

**Round 2 · ACCEPTED by the experiment lead (2026-10-23, tag e5-B-s04-accepted; B-G-02, B-G-04) · team review open.** Clean reruns `20261023T154827Z` (regression) and `20261023T154833Z` (classification) on code commit e960870, clean tree. They are byte-identical to the round-2 build runs 20261023T153748Z and 20261023T153754Z, whose figures appear below. Coverage 5 of 5 per task, 0 MISSING; 5 + 5 checks, all PASS, and the linear/logistic design matrix is full rank. In each sub-tab, the round-2 cards come first and the round-1 cards follow below.

## Decision B-G-02 (agreed: option 1)

Route (B-C6) is customer state → primary seller state, so every route level fixes both customer\_state and primary\_seller\_state, which are also in A's pool and both pass the 99% cut. Their one-hot columns are then linear combinations of route's columns, and the linear design matrix loses rank (B4.5; design\_matrix\_B.csv). Options:

1. **Drop customer\_state and primary\_seller\_state whenever route is kept** (proposed). Route carries all of their information; trees lose nothing, and the linear/logistic matrix becomes full rank. Recorded as B-G-02 with a reduction row "nested in route".
2. Keep all three and rely on the regularisation of the linear/logistic models. The matrix stays rank-deficient and the coefficients of the three are not identifiable, which makes the B8 coefficient reading unreliable.

Decided 2026-10-23: option 1 (Henry and the experiment lead). Applied in round 2; see "Round 2 changes" below.

## Current (round 2)

### Coverage

| Task | ID | Solution step | Coverage | Checks | Review |
| --- | --- | --- | --- | --- | --- |
| regression | B4.1 | Pool | IMPLEMENTED | PASS | Open |
| regression | B4.2 | Ranking | IMPLEMENTED | PASS | Open |
| regression | B4.3 | Selection at 99% (B-C11) | IMPLEMENTED | PASS | Open |
| regression | B4.4 | Transforms | IMPLEMENTED | — | Open |
| regression | B4.5 | Recipes and dictionary (B-C12) | IMPLEMENTED | PASS | Open |
| classification | B4.1 | Pool | IMPLEMENTED | PASS | Open |
| classification | B4.2 | Ranking | IMPLEMENTED | PASS | Open |
| classification | B4.3 | Selection at 99% (B-C11) | IMPLEMENTED | PASS | Open |
| classification | B4.4 | Transforms | IMPLEMENTED | — | Open |
| classification | B4.5 | Recipes and dictionary (B-C12) | IMPLEMENTED | PASS | Open |

### Summary

B4 ranks B's pool (A's task pool plus B's candidates, route counted as one feature) on B's development rows with A's measures, applies A's reduction rule, keeps the 99% cumulative-share prefix (B-C11) and builds the recipes and feature\_dictionary\_B.csv (B-C12) with A's code.

| Task | Pool | Kept at 99% (of core) | B features kept | Top 3 | Linear design rank |
| --- | --- | --- | --- | --- | --- |
| regression | 30 (24 A + 6 B) | 21 of 26 | 6 of 6 | route\_seller\_to\_customer\_state, route\_recent\_carrier\_transit\_days, route\_recent\_delivery\_days | 140 of 140 |
| classification | 36 (27 A + 9 B) | 25 of 32 | 9 of 9 | route\_recent\_carrier\_transit\_days, route\_recent\_delivery\_days, seller\_prior\_dispatch\_days | 145 of 145 |

### Round 2 changes

1. **B-G-02 applied.** With route in the pool, customer\_state and primary\_seller\_state are dropped in the reduction as "nested in route" (reduction\_B.csv). The route-median fill for distance is no longer used: B-C2 leaves distance never missing, so the fill and its missing flag would be constant. The linear/logistic design matrix is now full rank: 140 of 140 columns for regression and 145 of 145 for classification. The condition numbers are 253.2 and 956.4 (design\_matrix\_B.csv).
2. **Tree matrices remain rank-deficient by design.** Trees keep every level of each categorical, so each set of one-hot columns sums to one. This does not affect tree models.
3. **Selection.** The core sets are now 26 features (regression) and 32 (classification), and the 99% rule keeps 21 and 25 of them. Every B feature is still kept (selection\_ranking\_B.csv).
4. **Names (B-G-04).** B2's new names are used throughout, including feature\_dictionary\_B.csv.

### Points for review (round 1; Henry's answers are in the comments)

1. **B features rank at the top.** In both tasks all B candidates pass the 99% cut; the route history features (transit and lead days) are in the top three (selection\_ranking\_B.csv). For classification the carrier-handover facts (B-C9) are kept too.
2. **Route is ranked as one feature** with the rank correlation ratio (regression) or mutual information (classification), as A ranks its other categoricals.
3. **The ranking uses all development rows**, as A's s04 did; folds come in B5. This is A's inherited method, not a B change.
4. **Transforms follow A's 4.2 rule plus Henry's day-count rule**: all B day counts are logged, rates and flags only scaled (transforms\_B.csv).
5. **Full-rank failure** — see the decision above. The tree matrix shows the same nesting; it does not harm trees, but the fix applies to both.

## Round history

### Round 2 — 2026-10-23

- B-G-02 and B-G-04 applied (B-CR-04) in e5b/b04.py. Runs 20261023T153748Z and 20261023T153754Z; all checks pass; not committed.
- Comments: Henry chose option 1 and confirmed points 1–4; his comments are answered in their threads.

### Round 1 — 2026-10-23

- First build of B4 for both tasks: e5b/b04.py, not committed. The full-rank check failed, which led to B-G-02.
