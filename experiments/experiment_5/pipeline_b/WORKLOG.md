# Pipeline B work log (append only)

One entry per work session: date, who, what was done, commits, checks, next, questions for Benson.
Newest at the bottom. Never edit an earlier entry; correct it in a later one.

## 2026-10-26 · Henry + Claude · B10 handover setup

**Done**
- Branch `e5/b10-henry` from `milestone-3` at 85822c8 (= `e5-B-s09-accepted`).
- Tags fetched and verified: `e5-A-frozen` c7d15c7, `e5-B-frozen` e4fa1a6, `e5-T1-tested` 7e6941f,
  `e5-B-s09-accepted` 85822c8. They were missing from the remote until Benson pushed them today.
- Environment: created `experiments/experiment_5/.venv` (git-ignored by the existing `.venv` rule) and
  installed `requirements.txt`; every pinned version installed as listed.
  **Deviation (approved by Benson):** Python 3.13.7 instead of the pinned 3.13.9 (the only Python on
  Henry's machine). B10.1 parity is the acceptance test for this environment.
- Reverted a local edit to the repo-root `.gitignore` (rule 1); `_DONOTCOMMIT/` is excluded through
  `.git/info/exclude` instead (local, not part of the repo).
- Decisions from Benson recorded: B-G-08 (parity re-prediction without labels or scoring); B10-D2 to
  D7 agreed as recommended, in the blueprint draft.
- Created `HANDOVER.md`, this log, `spec/doc_outbox/`.

**Checks**
- `.venv/Scripts/python.exe -m pytest -q pipeline_b/tests`: 6 passed, 5 skipped (the slow adapter
  equivalence tests, skipped unless `E5B_SLOW=1`, by design). Not yet run with `E5B_SLOW=1`.

**Next**
- Draft `spec/blueprints/b10_release.md` and its doc copy; stop for agreement.

**Questions for Benson**
1. Henry's remark (2026-10-26) says "B-G-07 decided the threshold 5/14 for B". `spec/decision_log_B.md`
   B-G-07, `spec/human_decisions_B.yaml` b09.classification.operating_threshold (value 0.2667,
   label "4/15") and B9 `threshold_options.csv` all record 4/15. The draft keeps 4/15 until this is
   confirmed (B10-D8).

## 2026-10-26 · Henry + Claude · B10 blueprint DRAFT

**Done**
- Setup committed as d8fbe8c ("Pipeline B: B10 handover setup").
- Drafted `spec/blueprints/b10_release.md` (Status DRAFT): B10.1 parity, B10.2 release manifest,
  B10.3 serving configuration (scope rule, B at 4/15 and 1/6, A fallback at 1/6, expected alert
  volumes for the team to confirm), B10.4 router, B10.5 input checks, B10.6 drift profile, B10.7 app
  sources plus R-14 data. Decisions B10-D1 to D7 agreed by Benson; D8 and D9 open.
- Doc-ready copy: `spec/doc_outbox/b10_blueprint_tab.md` (section for the tab "B blueprints B2–B9
  and joint test"). Not published.

**Checks**
- None run on new code (no B10 code yet).

**Next**
- Agreement of the blueprint (Henry and Benson, or the lead), then mark AGREED with who and date.
- Then B10 code (B-CR-22), clean reruns on that commit, pytest, EVIDENCE.md rows, review tabs.

**Questions for Benson**
1. B10-D8: 4/15 (recorded in B-G-07) or 5/14 (Henry's remark)? See the earlier entry.
2. B10-D9: in-scope classification orders before handover get no score, only the missed-dispatch
   rule; A is not used for them. Agree?

## 2026-10-26 · Henry + Claude · B10 blueprint AGREED

**Done**
- Henry for the team: B10-D8 = 5/14, recorded as a new post-test change B-G-09 (B-G-07's 4/15 marked
  Superseded; frozen 1/6 unchanged); B10-D9 agreed (no score for in-scope orders before handover).
  `human_decisions_B.yaml` b10.classification; EVIDENCE.md superseded row for 4/15.
- Blueprint status AGREED; doc outbox copy regenerated (not yet published); HANDOVER.md rule 6.

**Next**
- B10 code (`e5b/b10.py`, `e5b/serving.py`), tests, commit B-CR-22, clean reruns.

**Questions for Benson**
1. Confirm B-G-09 (operating threshold 5/14, replacing 4/15).

## 2026-10-26 · Henry + Claude · B10 code, first build runs (uncommitted)

**Done**
- Wrote `e5b/serving.py` (router and input checks) and `e5b/b10.py`; `b10` added to STAGES (env.py) and
  BUILT (b_run.py). Not committed yet.
- Build run regression: all 13 checks PASS. Parity (B10.1): A on A, A on B, B on B within 1e-9 (max
  difference about 1e-14) on Python 3.13.7, so the environment passes its acceptance test.
- Build run classification: parity, manifest, router, input checks, drift and app sources PASS; two
  consistency checks FAIL (below).

**Finding: refits are not reproducible across machines**
- Re-predicting with the frozen bundles is exact here. Refitting is not: B9.10's out-of-fold sigmoid
  rebuild (refit of the frozen logistic recipe per development fold) gives per-fold AP that differs from
  B8's calibration_folds.csv by up to about 1.5e-3 on Henry's machine (B9 matched within 1e-9 on Benson's).
  Same result on repeated runs here; it changes with OpenBLAS settings, so it is floating-point
  sensitivity of the unregularised logistic fit, not randomness.
- Effect: B at 1/6 on validation gives 5,833 alerts here vs 5,865 in B9 threshold_options.csv; the
  test rows (no refit) match exactly.
- This also matters for the later reproduction check (A's s10 10.4): any stage that refits may not
  reproduce byte for byte on another machine.

**Questions for Benson**
1. B10.3 validation figures: restate from stored files without refitting (proposed to Henry), or rebuild
   on Benson's machine?

## 2026-10-26 · Henry + Claude · B10 built for review

**Done**
- Henry: no refit in B10 (B10-D10); the team accepts B's alert volume at 5/14, below the 6/day review cap
  (B10-D2). Recorded in the blueprint and `human_decisions_B.yaml` b10.
- B10.3 reworked: validation restated from B9's files (1/6 exact; 5/14 bracketed by the stored 0.36 and
  0.35 rows; A out of scope derived exactly from B9.15); test at 1/6 and 5/14 from T1's saved predictions.
- Code committed as 60a6c3c (B-CR-22). Clean runs 20261026T015521Z (regression) and 20261026T015559Z
  (classification), dirty false; a second run gave byte-identical outputs. EVIDENCE.md rows added
  (tag column e5-B-s10-accepted, pending approval).
- Review tabs written to `spec/doc_outbox/`: b10_review.md, b10_review_regression.md,
  b10_review_classification.md (generated from the outputs; not published).

**Checks**
- B10 regression 13 of 13 PASS, classification 15 of 15 PASS.
- `pytest pipeline_b/tests`: 11 passed, 5 skipped (slow adapter tests; see the next entry for the
  `E5B_SLOW=1` result).

**Next**
- Approval of B10 by Benson or the lead; then tag `e5-B-s10-accepted` on the branch.

**Questions for Benson**
1. Confirm B-G-09 (5/14).
2. Out-of-profile SD limit for the app (B10.6 shows shares at 3, 4 and 5 SD).
3. On the test, A's fallback at 1/6 gives about six times B's daily alerts (threshold_results.csv); the
   team accepted B's volume. Is A's volume acceptable too?

## 2026-10-26 · Henry + Claude · slow adapter tests on Henry's machine

**Checks**
- `E5B_SLOW=1 pytest pipeline_b/tests/test_adapter.py`: 5 failed, 1 passed (8 min). The failures are the
  equivalence tests that refit A's s06/s07/s08 code on A's inputs and compare with A's frozen outputs
  (for example: s08 classification "finalists refitted on the same rows and folds reproduce their s06 fold
  scores"). Same cause as the B10 finding above: refits are not bit-reproducible on this machine. No B10
  output depends on a refit (B10-D10); no tracked file changed.

**Questions for Benson**
1. The reproduction check before migration (A's s10 10.4) compares output hashes after a full rerun. On a
   machine other than yours, every refitting stage will differ slightly. Should that check use a
   tolerance on scores and predictions instead of hashes, or run only on your machine?

## 2026-10-26 · Henry + Claude · B10 review answers

- Henry confirmed B-G-09 (5/14); decision log and YAML updated.
- Henry accepted A's fallback volume at 1/6 (B10-D2).
- Out-of-profile SD limit: explained to Henry, decision pending.

## 2026-10-26 · Henry + Claude · Out-of-profile limit 4 SD

- Henry chose 4 SD (B10-D11): the app warns when a numeric input is more than 4 SD from the training
  mean; warning only. Code commit adf23d6 (B-CR-23), one input-check case added.
- Clean runs 20261026T020904Z (regression) and 20261026T021016Z (classification) on adf23d6, dirty
  false, byte-identical on a second run, 13 + 15 checks PASS. EVIDENCE.md, README, HANDOVER and the
  review tabs updated (tabs regenerated from the outputs; not published).
- Next: Henry's review of B10, then approval and the tag e5-B-s10-accepted. Not pushed.

## 2026-10-26 · Henry + Claude · B10 accepted

- Henry approved B10 on behalf of Benson (aligned with him while he is away). Henry pushed
  e5/b10-henry (94fd132) himself.
- Records: EVIDENCE.md rows final, README status ACCEPTED, HANDOVER, CHANGELOG_B B-CR-24.
- Tagged the acceptance commit `e5-B-s10-accepted` (local; Henry pushes the tag).
- Next (only when ordered): report and deck drafts, release sign-off `e5-release-1`, migration (lead),
  reproduction check (note B10-D10: refits are not bit-reproducible across machines), app build.
- For Benson: please review B10 on return; decisions B-G-08, B-G-09, B10-D1 to D11 are in the logs.

## 2026-10-26 · Henry + Claude · B11 report and deck blueprint DRAFT

- Henry pushed e5/b10-henry (058f7d9); the tag e5-B-s10-accepted still needs `git push origin e5-B-s10-accepted`.
- Henry's decisions: draft report and deck now, before migration (B11-D1); blueprint first (D2);
  B's own register `build_evidence_B.py` (D3); report as a Claude Doc, deck generated with editable
  text and tables (D4).
- Drafted `spec/blueprints/b11_report_deck.md` (DRAFT) and `spec/doc_outbox/b11_blueprint_tab.md`.
  Open: B11-D5 to D9. Stopped for agreement.
- For Benson: B11-D1 deviates from s10-D3's order (deliverables before migration) because of the 4 Nov
  slide lock; numbers are re-checked before submission.
