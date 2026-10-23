# Pipeline B evidence register

**The only place that says which B evidence is current.** The final report, slides and dashboard
cite a Pipeline B number only if all four hold:

1. it is read from a file under `pipeline_b/stages/<stage>/<task>/outputs/`;
2. that folder's `_manifest.json` has the `run_id` listed as **Current** below;
3. the checked-out tree is at or after the tag listed for that stage;
4. the evidence ID is a B ID (B2.1, B4.5, …).

Never cite a number from a doc tab, the team-doc mirror, a superseded round, a probe, a chat
message or memory. `tests/test_evidence_register.py` fails if this table and the manifests disagree.

Pipeline A's evidence is frozen at tag `e5-A-frozen`: cite A only from `../stages/` at that tag.

## Current runs

| Stage | Task | Current run_id | Code commit | Tag | Round |
| --- | --- | --- | --- | --- | --- |
| b02 | regression | 20261023T154814Z | e960870 | e5-B-s02-accepted-r2 | 2 |
| b02 | classification | 20261023T154822Z | e960870 | e5-B-s02-accepted-r2 | 2 |
| b04 | regression | 20261023T154827Z | e960870 | e5-B-s04-accepted | 2 |
| b04 | classification | 20261023T154833Z | e960870 | e5-B-s04-accepted | 2 |
| b05 | regression | 20261023T160529Z | 19b5355 | e5-B-s05-accepted | 1 |
| b05 | classification | 20261023T160533Z | 19b5355 | e5-B-s05-accepted | 1 |

When a stage is accepted again, replace its rows here in the same commit and move the old rows
to the table below.

## Superseded (never cite)

| What | Where it still appears | Replaced by |
| --- | --- | --- |
| B2 round 1 runs 20261023T134738Z, 20261023T134750Z (tag e5-B-s02-accepted): cap 93.63 days from A's orders, 61,245 regression rows, old feature names | git history; "Round 1 cards" sections of the B2 doc sub-tabs; B2 stage tab "Points for review (round 1)" | B2 round 2 (B-G-03, B-G-04) |
| B2 round 2 build runs 20261023T153736Z, 20261023T153744Z | B2 doc cards (figures are byte-identical to the current runs) | clean reruns above |
| B4 round 1 runs 20261023T134940Z, 20261023T134947Z (never committed): full-rank check failed, old names | "Round 1 cards" sections of the B4 doc sub-tabs | B4 round 2 (B-G-02, B-G-04) |
| B4 round 2 build runs 20261023T153748Z, 20261023T153754Z | B4 doc cards (byte-identical to the current runs) | clean reruns above |
| Cap "93.65 days" (rounded inputs) and "93.63 days" (A's s02 orders) | CR-054 B-C3 (marked AMENDED), overview tab (marked AMENDED), B-CR-03 | B-G-03: computed on B's rows, value in b02/regression feature_build_log.json |
| Route written customer -> seller; names b_seller_*, b_route_*, b_own_*, route | CR-054 B-C6 (marked AMENDED), round-1 cards | B-G-04 names (decision_log_B.md) |
| B5 build runs 20261023T160116Z, 20261023T160119Z (uncommitted code) | human_decisions_B.yaml b05 observed counts (same figures) | clean reruns above |
| Probe 1 and probe 2 (probe 2 withdrawn) | doc tab "Scratch check plan" | never evidence; motivation only (G-79) |

## Where definitions live

- What B is: CR-054 (G-79) as amended by `spec/decision_log_B.md` (B-G-01 onward). Where they differ, the decision log wins.
- How each stage works: `spec/blueprints/b0*.md` (AGREED versions).
- Feature names, formulas and reasons: `stages/b04/<task>/outputs/feature_dictionary_B.csv`.
