# B implementation reviews

Implementation reviews for Pipeline B, in the same format as Pipeline A's "Implementation reviews": one tab per stage with a coverage table and a review dropdown per evidence card, and one sub-tab per task with the cards (approved solution from the B blueprint, what was done, checks, files). Every number is read from the stage's committed outputs under pipeline\_b/stages/; the card IDs are B's (B2.1, B2.2, …).

**How to review.** Comment on any card or point; set the dropdown to Approved or Change. A change reopens the stage, and the later B stages rerun in order. Pipeline A is frozen (tag e5-A-frozen) and is not affected by anything here.

## Progress

| Stage | Blueprint | Build | Lead review | Team review | Tag |
| --- | --- | --- | --- | --- | --- |
| B2 Population and features | AGREED | round 2 (B-G-03 cap on B's rows and seven-state summary; B-G-04 names) | ACCEPTED round 2 | Henry reviewed round 1; round 2 open | e5-B-s02-accepted-r2 |
| B4 Features | AGREED | round 2 (B-G-02 nesting; B-G-04 names) | ACCEPTED round 2 | Henry reviewed round 1; round 2 open | e5-B-s04-accepted |
| B5 Partition | DRAFT (B-G-01 decided) | not started | — | — | — |
| B6–B7 Training and tuning | DRAFT | not started | — | — | — |
| B8 Selection (gate, freeze) | DRAFT | not started | — | team reviews B6–B8 together at the gate | — |
| Joint test run (A and B) | to be drafted with B8 | not started | — | — | — |

## Decision B-G-02 (agreed 2026-10-23: option 1, applied in B4 round 2)

**B-G-02 (B4): drop customer\_state and primary\_seller\_state when route is kept?** Route nests both state columns, so B4's linear/logistic design matrix is not full rank. Options and evidence are at the top of the sub-tab "B4 Features"; please comment there.
