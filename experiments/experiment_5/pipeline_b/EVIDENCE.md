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
| b06 | regression | 20261023T162830Z | e358f81 | e5-B-s06-accepted | 1 |
| b06 | classification | 20261023T162918Z | e358f81 | e5-B-s06-accepted | 1 |
| b07 | regression | 20261023T163311Z | e358f81 | e5-B-s07-accepted | 1 |
| b07 | classification | 20261023T164241Z | e358f81 | e5-B-s07-accepted | 1 |
| b08 | regression | 20261024T042516Z | a4a0ded | e5-B-frozen | 1 |
| b08 | classification | 20261024T042619Z | a4a0ded | e5-B-frozen | 1 |
| t1_joint_test | regression | 20261024T044531Z | e4fa1a6 | e5-T1-tested | single read |
| t1_joint_test | classification | 20261024T044555Z | e4fa1a6 | e5-T1-tested | single read |
| b09 | regression | 20261025T132406Z | b09c396 | e5-B-s09-accepted | 2 |
| b09 | classification | 20261025T132538Z | b09c396 | e5-B-s09-accepted | 2 |
| doc_support | regression | 20261025T132541Z | b09c396 | e5-B-s09-accepted | 1 |
| doc_support | classification | 20261025T132552Z | b09c396 | e5-B-s09-accepted | 1 |
| b10 | regression | 20261027T044744Z | 906fe39 | e5-B-s10-accepted-r3 | 3 (accepted by the experiment lead 2026-10-27) |
| b10 | classification | 20261027T044819Z | 906fe39 | e5-B-s10-accepted-r3 | 3 (accepted by the experiment lead 2026-10-27) |
| b12 | regression | 20261027T120743Z | 3a27dbf | e5-release-2 | 1 (Milestone 2 feedback checks) |
| b12 | classification | 20261027T120801Z | 3a27dbf | e5-release-2 | 1 (Milestone 2 feedback checks) |

**B10 rows:** round 3 (B-G-10: A's fallback test cost and the combined B + A line in threshold_results.csv; thresholds unchanged, 4/15
operating, 1/6 frozen, A 1/6), clean runs on 906fe39 (Henry's machine), byte-identical on a second run. Accepted by the experiment lead
2026-10-27, tag e5-B-s10-accepted-r3 (B-CR-34). Round 2 (clean runs on 1e36f0a) is superseded (table below).
Round 1 (5/14, tag e5-B-s10-accepted) is superseded (table below). Round 2 approved by Henry on Benson's behalf on 2026-10-26; tag e5-B-s10-accepted-r2.

**T1 is never rerun** (a rerun is a second test read; joint_test.md §1). Its run was made on a tree
with the T1 code not yet committed (manifest `dirty: true`, HEAD e4fa1a6). The manifest records the
sha256 of every B code file that ran; the register test checks those hashes against the committed
files instead of a clean rerun. Cite T1 numbers only from these two runs.

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
| B5 build runs 20261023T160116Z, 20261023T160119Z (uncommitted code) | nowhere now (human_decisions_B.yaml b05 cites the accepted runs) | clean reruns above |
| B6/B7 build runs before commit e358f81 (uncommitted code) | nowhere (byte-identical to the current runs) | clean reruns above |
| A's s06/s07 scores (all states, A's features) | A's review tabs | never compared with B6/B7 scores directly; the like-for-like A–B comparison is B8's (G-79) |
| B8 gate runs before a4a0ded (raw calibration, raw threshold tables, threshold options 1/6 = 19.2/day and 0.15 = 24.6/day on raw probabilities) | B8 doc tabs written at the gate; Henry's threads | B8 frozen run: sigmoid (B-G-05), threshold tables on sigmoid probabilities (threshold_table_sigmoid.csv), frozen_recipe.json |
| T1 dry run on stand-in rows (last 8 weeks of development rows used as a fake test set, to exercise the code path before the single read; outputs deleted) | nowhere | never evidence; T1 runs above |
| B9 build runs before b09c396 (round 1 20261024T05xxxxZ, round 2 20261025T09xxxxZ and the confirmation build; uncommitted code) and doc support build runs 20261024T06xxxxZ | B9 tabs ("Run ..." lines) and supplement sections cite those run IDs; the accepted reruns are byte-identical | B9 and doc support rows above |
| B10 round 2 runs 20261026T024749Z, 20261026T024858Z on 1e36f0a (tag e5-B-s10-accepted-r2): A's fallback test row without counts or cost (NaN) | review tabs b10_review*.md (round 2), sync_for_benson.md, the report and deck before 2026-10-27 | B10 round 3 (B-G-10); every other figure unchanged |
| B10 round 1 runs 20261026T020904Z, 20261026T021016Z on adf23d6 (tag e5-B-s10-accepted): operating threshold 5/14 (B-G-09, withdrawn as a typo) | review tabs b10_review*.md before round 2; the report doc before 2026-10-26 evening | B10 round 2 (4/15, B-G-07) |
| Probe 1 and probe 2 (probe 2 withdrawn) | doc tab "Scratch check plan" | never evidence; motivation only (G-79) |

## Where definitions live

- What B is: CR-054 (G-79) as amended by `spec/decision_log_B.md` (B-G-01 onward). Where they differ, the decision log wins.
- How each stage works: `spec/blueprints/b0*.md` (AGREED versions).
- Feature names, formulas and reasons: `stages/b04/<task>/outputs/feature_dictionary_B.csv`.
