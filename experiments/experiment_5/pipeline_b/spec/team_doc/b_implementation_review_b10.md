# B10 Release — for team review

**ACCEPTED round 3** by the experiment lead (Wu Qianzong), 2026-10-27 · tag `e5-B-s10-accepted-r3` · B-G-10 and B-G-11 ratified (B-CR-34). Built by Henry and his Claude on branch e5/b10-henry; merged into milestone-3 at 46d68a4. Verified on the lead's machine: tests 25 of 25, deliverables audit 9 of 9; B10 rerun reproduces threshold\_results.csv and serving\_config.json exactly, other outputs differ only in the last float digit (reproduction policy CR-056). Published from pipeline\_b/spec/doc\_outbox/; round 2 is kept below for the record (superseded).

## Round 3 (current)

**Built · clean runs 20261027T044744Z (regression), 20261027T044819Z (classification) on 906fe39, all checks PASS; byte-identical on a second run.** Round 3 (B-G-10, blueprint §8) adds A's fallback test cost and the combined serving-rule line; every other figure equals round 2. Built by Henry's Claude on branch e5/b10-henry. Not tagged: Benson tags after he approves. Round 2 tabs stay as published.

### What changed in round 3

1. **A's fallback cost on the test (audit B10-F2).** A at 1/6 on its test rows outside B's scope: 1,428 alerts, 190 TP, 1,238 FP, 170 FN; precision 0.133, recall 0.528; cost 2,088 at 5:1 and 1,408 at 1:1. From the labels already saved by T1, as B's test rows; precision and recall equal B9.15's test row (check).
2. **Combined serving rule, B 4/15 + A 1/6.** Test (post-test view): 20.5 alerts/day, precision 0.192, recall 0.198, cost 9,211 at 5:1 and 3,115 at 1:1 (B's part 7,123 at 5:1). Validation: 10.5 alerts/day, precision 0.305, recall 0.124.
3. **Unchanged:** thresholds (4/15 operating, 1/6 frozen, A 1/6), parity, router, input checks, drift profile, app sources; the frozen 1/6 T1 result stays the unbiased test result (G-79). Regression outputs equal round 2 in content.

### Decisions for Benson to ratify

- B-G-10: A's fallback test cost and the combined line (this round).
- B-G-11: the report cites A's s03 EDA numbers from A's frozen tree.

### Coverage

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

### Next

On Benson's approval: tag the round-3 commit. Then, each only when ordered: sign-off and e5-release-1, migration (lead), reproduction check, app and dashboard build.

## Round 2 (superseded by round 3)

**Built · clean runs 20261026T024749Z (regression), 20261026T024858Z (classification) on 1e36f0a, all checks PASS; byte-identical on a second run.** Built by Henry's Claude on branch e5/b10-henry while Benson is away (pipeline\_b/HANDOVER.md). Approved by Henry on Benson's behalf; tag e5-B-s10-accepted-r2.

### Points for review

1. **Parity (B10.1).** The T1 bundles reload and re-predict T1's saved test predictions within 1e-9 on Python 3.13.7, from test rows rebuilt with every label column blanked (B-G-08). This is the acceptance test of Henry's environment.
2. **Operating threshold 4/15 (B-G-07), round 2.** Round 1 used 5/14 (B-G-09); Henry confirmed 5/14 was a typo, so B-G-09 is withdrawn and B10 is rerun with 4/15. The frozen 1/6 and its T1 result stay the unbiased result. Round 1 is superseded (tag e5-B-s10-accepted stays on it); round 2 approved by Henry for Benson, tag e5-B-s10-accepted-r2.
3. **Alert volumes (B10-D2), re-confirmed by the team (Henry, 2026-10-26).** Test (post-test view): B 5.6/day at 4/15 plus A 14.9/day at 1/6 outside B's scope = 20.5/day. Validation: B 4.0/day plus A 6.5/day. Most alerts come from A's fallback outside the seven states (classification sub-tab, threshold\_results.csv).
4. **No refit (B10-D10).** Refitting the frozen logistic recipe is not bit-reproducible across machines: on Henry's machine the out-of-fold rebuild differs from B8's calibration step by up to about 1.5e-3 AP per fold. B10 therefore restates B9's stored files (1/6 and 4/15 exactly). This also matters for the later reproduction check (A's s10 10.4).
5. **Before handover (B10-D9).** In-scope orders not yet handed over get no score; the missed-dispatch rule flags them.
6. **Out-of-profile limit (B10-D11):** the app warns when a numeric input is more than 4 SD from the training mean; warning only.

### Coverage

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

### Next

On approval: tag e5-B-s10-accepted on the branch. Then, each only when ordered: sign-off and e5-release-1, migration (lead), reproduction check, app and dashboard build, report and slides.
