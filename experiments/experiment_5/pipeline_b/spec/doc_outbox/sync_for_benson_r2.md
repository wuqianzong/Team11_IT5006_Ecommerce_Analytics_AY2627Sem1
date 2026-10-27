# Sync note for Benson, round 2 (branch e5/b10-henry, after your review at 8b6d7fb)

Written 2026-10-27 by Henry's Claude. Read with `../../HANDOVER.md` and the last `../../WORKLOG.md` entry. The first note
(`sync_for_benson.md`) covers everything up to 8b6d7fb; this one covers only what changed since. Nothing is merged into
`milestone-3` and no tag was created.

## Open for you

### 1. What changed since 8b6d7fb

| Step | What | Change log |
| --- | --- | --- |
| Step 1 | `build_evidence_B.build()` takes an output folder (CLI default unchanged); the register test builds into pytest's tmp folder, so running pytest leaves `git status` clean | B-CR-31 |
| Step 0, H-1 | B10 round 3: A's fallback test row gets TP, FP, FN and both costs from T1's saved predictions (checked against B9.15), plus combined "B 4/15 + A 1/6 (serving rule)" rows; thresholds, models and every other output unchanged (regression byte-identical to round 2) | B-CR-32 |
| Step 0, H-2 | Register reads A's s03 EDA from A's frozen tree: sources `A/<stage>/<task>/outputs/<file>`, accepted only if equal to the file at `e5-A-frozen` (sha256) and tagged with the cited A evidence ID; 11 A3 items; report §3 cites them and drops its open-item line | B-CR-33 |
| Step 4 | Register rebuilt (117 items); report §7 adds the serving-rule cost; deck slide 8 fills A's recall and the combined precision and recall; live report doc rev 29 and deck version 1793077250-4a3c updated from the filled sources | B-CR-33 |
| Step 4 | Audit inputs committed under `deliverables/audit/inputs/` (report export rev 29, 12 slides, 16 + 6 chart assets); the audit reruns from them without Henry's account; all 9 checks PASS | B-CR-33 |

### 2. Commits (oldest first)

edb0094 (B-CR-31, B-G-10/11 proposed) · 906fe39 (round 3 code) · 555afb2 (round 3 clean runs, evidence, r3 tabs) ·
5a496e5 (register A-source rule, sources) · 368fa3e (register rebuild) · ae02684 (report, deck, audit inputs, audit 9/9) ·
the close-out commit after it (README, HANDOVER, WORKLOG, this note).

### 3. Current runs (EVIDENCE.md)

| Stage | Task | Run | Commit | Round |
| --- | --- | --- | --- | --- |
| b10 | regression | 20261027T044744Z | 906fe39 | 3 (no tag yet) |
| b10 | classification | 20261027T044819Z | 906fe39 | 3 (no tag yet) |

Round 2 (20261026T024749Z, 20261026T024858Z on 1e36f0a, tag e5-B-s10-accepted-r2) is superseded. Every other Current
row is unchanged.

### 4. Decisions to ratify

| ID | Decision | Recorded |
| --- | --- | --- |
| B-G-10 | B10.3 adds A's fallback test cost and the combined serving-rule line (B10 round 3; blueprint §8) | Proposed, Henry for the team |
| B-G-11 | The report cites A's s03 EDA numbers, read from A's frozen tree at e5-A-frozen | Proposed, Henry for the team |

Both are in `../decision_log_B.md` and `../human_decisions_B.yaml`. After ratifying: tag the round-3 commit (your call on the
tag name) and set the status to Agreed.

### 5. Doc tabs to publish

| Outbox file | Doc tab |
| --- | --- |
| b10_review_r3.md | B10 Release (stage tab): a "Round 3" section above round 2 |
| b10_review_r3_regression.md | B10 Release › regression: round 3 section |
| b10_review_r3_classification.md | B10 Release › classification: round 3 section |

The files listed in the first note, if not yet published, still apply; `README.md` in this folder tracks what is published.

### 6. Test results on Henry's machine

`pytest -q pipeline_b/tests`: 20 passed, 5 skipped; the tree stays clean. With `E5B_SLOW=1` the 5 slow adapter tests fail
here, as before (refits not bit-reproducible across machines); they passed on your machine. Not "fixed", by rule.

### 7. Not done here (your decisions)

Ratifying "Henry for Benson" approvals, the reproduction-check tolerance policy (note: even B10, which refits nothing,
differs across machines at about 1e-16 in parity and drift outputs, so hash equality fails off the producing machine),
merging into `milestone-3`, the release tag, migration (README §12), the app and its URL.
