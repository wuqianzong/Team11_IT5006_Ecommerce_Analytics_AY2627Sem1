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

## 2026-10-26 · Henry + Claude · B11 blueprint AGREED

- Henry: B11-D5 (report doc in Henry's account), D7 (ensemble wording), D8 (Team 11), D9 (Claude drafts,
  team edits, AI use declared) as recommended; D6 changed: the deck is a Claude Slides deck (not python-pptx).
- Next: number register `build_evidence_B.py` and `evidence/registry_B.yaml`.

## 2026-10-26 · Henry + Claude · B11.1 number register

- `build_evidence_B.py` (build, fill, check) and `evidence/registry_B.yaml`: 90 items (57 numbers,
  17 tables, 16 figures). Each source must be the Current run in EVIDENCE.md with a matching sha256,
  and the item's evidence ID must be tagged on that file. A's baseline numbers come from T1/B9 files.
- Report and deck text will use `{{id}}` placeholders; `fill` replaces them, unresolved ones fail.
- `tests/test_register_B.py` (5 tests); pytest 16 passed, 5 skipped.
- Next: report outline in a Claude Doc (Henry's account) and section drafts; then the Slides deck.

## 2026-10-26 · Henry + Claude · B11.2 report draft v1

- Report sources `deliverables/report/00–09` with placeholders; all resolve (`check`). Filled text in the
  Claude Doc https://claude.ai/artifact/Gp8qHXHdffLf3t78JcMWid (Henry's account) for team review.
- Corrected one draft claim before publishing (top permutation-importance features, checked against B9 files).
- Open: charts in the doc, A's s03 EDA numbers in the register, appendices, app placeholders; then the Slides deck.

## 2026-10-26 · Henry + Claude · Report charts embedded

- The 16 register figures uploaded to the report doc and embedded with numbered captions and evidence IDs
  (mapping in deliverables/README.md).
- Figure 10 (B9.10 threshold options) still marks the superseded 4/15; a 5/14 version needs a B10 chart.

## 2026-10-26 · Henry + Claude · B10 round 2: threshold back to 4/15

- Henry: 5/14 was a typo; the operating threshold is 4/15. B-G-09 withdrawn, B-G-07 reinstated.
- Code 1e36f0a (B-CR-26): serving.py 4/15; b10.py restates B9's exact 4/15 validation row (no bracket) and checks
  the 1/6 and 4/15 test rows against B9. Clean runs 20261026T024749Z / 20261026T024858Z, byte-identical, all checks pass.
- EVIDENCE.md: round 2 current; round 1 (5/14, tag e5-B-s10-accepted) superseded. Tag not moved.
- Register rebuilt (ids B_4_15); report sources and the report doc updated (no 5/14 left); Figure 10 kept, it
  already marks 1/6 and 4/15, caption corrected.
- Outbox regenerated; `spec/doc_outbox/sync_for_benson.md` summarises every change for Benson.
- Open: approval of round 2 and the r2 tag; re-confirm alert volumes at 4/15.

## 2026-10-26 · Henry + Claude · B10 round 2 accepted

- Henry approved round 2 on Benson's behalf and re-confirmed the alert volumes at 4/15 (B10-D2).
- Records: EVIDENCE.md, README (ACCEPTED round 2), human_decisions_B.yaml, blueprint, HANDOVER, sync note, report
  source and doc (§7), review tabs. Code unchanged, so the round-2 runs on 1e36f0a stay current.
- Tagged the acceptance commit `e5-B-s10-accepted-r2` (local; Henry pushes the branch and the tag).

## 2026-10-26 · Henry + Claude · Audit and report appendices

- Audit: tests pass; A's foundation matches e5-A-frozen (only the allowed G-79 entry differs in A's tree); nothing
  written outside pipeline_b since 85822c8; every current run's outputs match their manifests; register rebuild
  identical; report doc matches filled sources; changelog ids B-CR-01 to 27 continuous. One stale copy fixed
  (b10_blueprint_tab.md, commit 6c6bf62).
- Report: appendices A–F (windows, glossary, full rank, selected features, train/validation/test tables, AI-use
  declaration) via new `{{table:id}}` placeholders (B-CR-28). Remaining: s03 EDA numbers, app placeholders.
- Next: Claude Slides deck.

## 2026-10-26 · Henry + Claude · B11.3 deck v1

- Claude Slides deck https://claude.ai/artifact/VtyNdrjEovfAvycTPmvy23, 12 slides, every number filled from the
  register (all placeholders resolve); charts uploaded as images; text and tables editable.
- Sources committed under deliverables/deck/. Open: app screenshot and URL (slide "deploy"), team review, PDF/PPTX
  download for Canvas by 4 Nov.

## 2026-10-26 · Henry + Claude · Deliverables audit

- `audit_deliverables_B.py` (B-CR-29) on the live report doc (rev 25, exported) and deck (downloaded slides and
  chart assets): 16 report charts and 6 deck charts byte-identical to register figures and their stage outputs;
  12 slides equal fresh fills of their templates; report body equals the filled sources line for line; 12 headline
  numbers recomputed directly from T1's saved test predictions match; every deck number is also in the report.
  All 9 checks pass. Evidence in deliverables/audit/.
- Text claims (forest within one SE, B adopted on 5 of 5 folds, fold-1 deviation, drift, top importance features)
  checked against B8/B9 outputs and decision records.

## 2026-10-26 · Henry + Claude · Third-party audit V2 response (B-CR-30)

- Verified all 15 findings read-only (all valid; register count in the audit stale). Henry approved doc-only fixes.
- Fixed: cap disclosure (report §7, §8; deck alerts), B-G-05 in limitations (report, deck), route-feature label
  (report §7, deck notes), appendix C tree note, README B11 status, B11 blueprint input tag r2, deliverables README,
  decision-log note for B10-F4. Live report doc (rev 28) and deck (6 versions) updated; audit rerun 9/9 PASS.
- Open: s03 EDA numbers (decision), app and URL (migration), final exports, A fallback cost (B10 code change),
  full references (lookup). Response table: deliverables/audit/third_party_audit_v2_response.md.

## 2026-10-27 · Henry + Claude · after Benson's review at 8b6d7fb

**Done**
- Step 0: Henry answered H-1 = yes (A's fallback test cost) and H-2 = yes (cite A's s03 EDA); recorded as B-G-10 and B-G-11,
  Proposed, Henry for the team, Benson to ratify (edb0094).
- Step 1: register test builds into pytest's tmp folder; pytest no longer rewrites evidence/build/ (B-CR-31, edb0094).
- Step 2: blueprint §8 round 3 agreed by Henry; code 906fe39 (B-CR-32); clean runs 20261027T044744Z (regression) and
  20261027T044819Z (classification), dirty false, byte-identical on a second run, 13 + 16 checks pass; only
  threshold_results.csv and serving_config.json change. EVIDENCE.md round 3 Current, round 2 superseded; r3 review tabs
  (555afb2). No tag.
- Step 3: build_evidence_B.py accepts A/<stage>/<task>/outputs/<file> sources only if equal to the file at e5-A-frozen and
  tagged with the cited A evidence ID; 11 A3 items; report §3 updated; tests for the rule (5a496e5, B-CR-33).
- Step 4: register rebuilt, 117 items, check resolves every placeholder (368fa3e). Live report doc updated to rev 29
  (§3 bullets and source line, §7 cost paragraph) and deck slide 8 to version 1793077250-4a3c, from the filled sources.
  Audit inputs committed under deliverables/audit/inputs/; audit 9/9 PASS on them (ae02684).

**Checks**
- `pytest -q pipeline_b/tests`: 20 passed, 5 skipped; `git status` clean afterwards.
- `E5B_SLOW=1`: 20 passed, 5 failed (the 5 slow adapter equivalence tests, which refit; expected on this machine, pass on
  Benson's; not "fixed", by rule). Tree clean afterwards.

**Next**
- Benson: ratify B-G-10, B-G-11; approve and tag B10 round 3; publish the r3 tabs (sync_for_benson_r2.md).

**Questions for Benson**
1. Ratify B-G-10 and B-G-11?
2. Tag name for B10 round 3 (round 2 was e5-B-s10-accepted-r2)?
3. Reproduction-check tolerance policy: even B10 (no refit) differs across machines at about 1e-16 in parity and drift
   outputs, so a hash comparison fails off the producing machine.

## 2026-10-27 · Benson + Claude · review of round 3 (4cce399), ratification, B10 round 3 accepted

**Done**
- Pulled e5/b10-henry at 4cce399. Every change since 8b6d7fb is inside pipeline_b/; A's tree and every accepted stage's
  outputs unchanged; no tag moved or created.
- Benson ratified B-G-10 and B-G-11 (now Agreed) and accepted B10 round 3; tag e5-B-s10-accepted-r3 on the commit that
  records this (B-CR-34). Not pushed.

**Checks (Benson's machine)**
- `pytest -q pipeline_b/tests`: 20 passed, 5 skipped; `E5B_SLOW=1`: 25 passed. Tree clean after both.
- Deliverables audit on deliverables/audit/inputs/: 9 of 9 PASS.
- B10 rerun at 4cce399: threshold_results.csv and serving_config.json reproduce exactly; parity, router, drift and
  top-routes outputs differ only in the last float digit (about 1e-16); all checks pass. Rerun not committed.

**Next (Benson)**
- Reproduction-check policy, merge into milestone-3, publish the outbox tabs, release tag, migration.

## 2026-10-27 · Benson + Claude · reproduction-check policy

- Benson chose option 1 (CR-056, B-CR-35): README §12 step 4's hash check runs on his machine and is the gate; reruns on
  any other machine are judged by tolerance (predictions 1e-9, refitted scores 2e-3 absolute, counts equal, report and
  slide numbers equal at the precision shown). Reason: Mac and Windows floating-point results differ slightly.

## 2026-10-27 · Benson + Claude · merge and publish

- e5/b10-henry and tag e5-B-s10-accepted-r3 pushed; milestone-3 fast-forwarded to 46d68a4 and pushed.
- Published from spec/doc_outbox/: new tab "B10 Release" with sub-tabs regression and classification (acceptance note,
  round 3, round 2 kept below as superseded); B10 and B11 sections appended to the blueprints tab (renamed "B blueprints
  B2–B11 and joint test"). doc_outbox/README.md marks every file published. Mirror spec/team_doc/ refreshed.
- Next for Henry: branch from milestone-3 for new work. Benson: e5-release-1, migration, app.

## 2026-10-28 · Henry + Claude · deliverables branch: population-chain register items

**Done**
- Branch `e5/deliverables-henry` cut from `milestone-3` at 86538e0 (after bc35656; tags e5-release-2, e5-reproduced).
- Register: 13 items for the report's population chain (TA point 2), all from Current B files, no stage or A file read:
  B2 classification removals and B development rows (both tasks, `exclusion_counts_B.csv`, B2.1); regression final-fit
  rows (T1 `test_size_B.json`, T1.1); fold-5 training and validation rows (B5 `fold_summary_B.csv`, B5.2).
- Read-only check (scratchpad, not cited): the 6 classification orders in the final fit but in no fold are not a payment
  issue (all have instalments and a payment type; none belongs to a test customer). They were purchased in
  Mar–Jun 2017 and reviewed 10–13 months later (Apr–May 2018): too late to be a training label in any fold, too early
  to be a validation row, but reviewed before the test cutoff, so the final fit keeps them.
- Decisions with Henry: chain starts at A's development rows (A's rules in words, no A counts); dashboard keeps A's
  fallback at 1/6 (B10-D2), statistics panel only, 1/6 for B not shown in the dashboard.

**Questions for Benson**
- None.

## 2026-10-28 · Henry + Claude · report plan v2 and first report sections

**Done**
- Plan v2 doc "Team 11 final report and deck plan v2" (https://claude.ai/artifact/GLWW2y5uMfHUd3Riewju1m): Henry's
  comments applied and answered (18–20 pages; 15 slides in 12 minutes; 12 audited sources only; stored collinearity
  outputs only, no rerun; change record; manual literature checklist; A's stored EDA figures may be shown).
- deliverables/report/CHANGES.md and literature_register.md started (c9c693b).
- Register: 202 items (plan v2 exhibits from stored outputs, A's s03 under B-G-11; §6 and §7 items), rebuilt each time.
- Report sources renumbered to plan v2 (02 literature and 05 features new) and §1, §3, §5, §6, §7 written
  (3702134, b72f3fc, dd15c8f, 4ac27fd and the §7 commit). Claims were checked against the stored files; two drafted
  claims were corrected (alert ranking stability; slice recall).

**Not done yet**
- Executive summary, §2 literature, §4 EDA, §8–§10, references, appendices; review doc refresh; deck rework.

**Questions for Benson**
1. audit_deliverables_B.py line 70 expects exactly 16 report charts; plan v2 adds more. May the check read the count
   from figure_map.json instead (your file)?
2. A's s02 data-structure figure (join diagram) would serve report §3 and deck slide 3; B-G-11 covers A's s03 only.
   May the register read A's s02 figures under the same rule?

## 2026-10-28 · Henry + Claude · review doc refresh and 15-slide deck

**Done**
- Report sources complete (17d6db1); change record hashes filled in.
- Review doc https://claude.ai/artifact/Gp8qHXHdffLf3t78JcMWid (rev 30): body replaced by the full filled report,
  28 figures (16 earlier doc blobs plus 12 new register figures uploaded to the doc), revision note dated 2026-10-28.
  One open question thread (alert cut order) lost its anchor; answered in the thread.
- Deck https://claude.ai/artifact/VtyNdrjEovfAvycTPmvy23 (version 13): reworked to the 15 slides of plan v2
  (cover, problem, data, prep, eda, routes, features, collin, selection, method, ladder, atob, gain, results, use);
  retired reg, clf, alerts, actions, deploy, limits, close. 82 register ids, all also in the report; 9 new register
  figures uploaded as deck assets.

**Not done yet**
- Audit not run: its chart checks need figure_map.json updated (Benson's file): 28 doc charts (line 70 hard-codes 16)
  and the deck's new image map below. Team review of doc and deck; app URL and screenshots (report §8).

**Questions for Benson**
1. (repeat) May audit line 70 read the chart count from figure_map.json?
2. Deck entries for figure_map.json, asset id → register figure:
   50fdc703d99e15f5c4a7777ee6fbd14b F.A3.reg.target_kde; 55679204d325313ce29239b9bb6233b0 F.reg.lateness_by_route;
   8bc9d14e0f89ead4d86268b56740e773 F.A3.reg.outcome_trends; 92b53ee5e77920e4ed1d4d3413e42f9c F.reg.history_coverage;
   c4ea3f0a8d8c5c3d379501a5c9bd9f98 F.A3.reg.correlation_heatmap; 4bd6826282b44966a891f99a10bea5aa F.reg.selection;
   87433e4d8e5e7299c327c25d0b3ab428 F.clf.ranking_stability; 8c3466a8505cdbaac46fe14c08d92041 F.reg.family_ladder;
   926ff6cf67efd1bc07c1c4667eebe324 F.clf.family_ladder. Keep 23cdda49…, 3d0b5f02…, 1abc90f2…, 5c1cf0ec…, 9705c7c3…;
   drop 2dcb30e7… (residuals, no longer on the deck).

## 2026-10-28 · Henry · decision: alert priority when review capacity is short

- Henry's decision: alerts from the improved pipeline at 4/15 come first. The baseline fallback's alerts come next,
  sorted by handover delay, then by order value.
- Settled by Henry (later 2026-10-28): the fallback's alerts are reviewed at handover; delay first, order value as
  the tie-break. Written into report §9 (review-order paragraph with the fallback's own alerts a day and precision)
  and deck slide 15, labelled an operational rule, not a measured result. Review doc rev 32 and deck version 14
  updated; the doc thread on the cut order answered.
  and a reply in the doc thread.

## 2026-10-28 · Henry + Claude · literature check, dashboard approval, push

**Done**
- 7f1bad0: references and literature register checked against publisher records (Crossref, NeurIPS proceedings,
  library catalogues). ISLP fifth author added; van den Goorbergh et al. full list; Grinsztajn et al. page range
  removed; initials added; ISLP dropped for the one-SE rule and VIF (no chapter abstract supports them; the report
  used both uncited). Detail in deliverables/report/CHANGES.md and literature_register.md.
- 9b5da75: DASHBOARD_PLAN.md APPROVED by Henry; stale references fixed.
- `build_evidence_B.py check`: all placeholders resolve in the report and the deck.
- Branch e5/deliverables-henry pushed to origin (Henry's instruction).

**Not done yet**
- `audit_deliverables_B.py` not run: its chart checks need figure_map.json updated by Benson (questions above).
- Review doc reference list still shows the old author forms; refresh after Henry's review.
- Alert priority text (report §9, deck slide 15) waits on the two open points recorded above.

## 2026-10-28 · Henry + Claude · Benson's audit steps (after 250204b)

**Done**
- Pulled 250204b (audit counts charts from figure_map and checks captions; deck map; B-G-13).
- Review doc rev 34: every chart has its own "Figure N." caption (the 8 combined captions split, since the check
  counts `*Figure N.`); the header note no longer carries dates (its numbers counted as report numbers).
- figure_map.json `doc` section rebuilt for the 28 charts (blob and asset read from the doc's blob records), under
  Benson's one-time exception; `deck` and `note` sections unchanged except the note's date.
- Audit inputs: report_export_rev34.md, 28 doc assets, 14 deck assets, the 15 live slides; rev29 export and the
  residuals asset removed.
- Report sources: paragraphs unwrapped to one line each, so they compare line for line with the doc export (text
  unchanged). CHANGES.md and literature_register.md moved to deliverables/report/records/, because the audit reads
  every *.md in deliverables/report/ as report text.
- Handover files: HANDOVER.md marked CLOSED; spec/doc_outbox/README.md marks the B10/B11 files and the sync notes
  complete, Benson's handshake answered, Solomon's open.

**Audit result**
- The official run stops with an error before any result: `chart_ok` reads the manifest at
  `stages/A/s03_eda/outputs/_manifest.json`, but the four A-source charts (F.A3.reg.target_kde,
  F.A3.reg.outcome_trends, F.A3.clf.outcome_trends, F.A3.reg.correlation_heatmap) come from A's frozen tree.
- Checked by hand: each of the four doc assets equals its register figure, and the register figure equals A's file at
  `e5-A-frozen` (sha256).
- A diagnostic copy of the script (scratchpad only, not committed), which skips the manifest lookup for those four,
  gives PASS on all 9 checks.

**Questions for Benson**
1. audit_deliverables_B.py `chart_ok`: please handle A sources (B-G-11, B-G-13): check against A's file at
   `e5-A-frozen` instead of a B manifest. Then the official run can pass.
2. HANDOVER_TO_HENRY.md, DELIVERABLE_IDEAS.md and M2_FEEDBACK_GAPS.md are yours: mark them complete when you agree
   (report and deck done; app URL and screenshots, final proofreading and PDF still open).

**Not done yet**
- Solomon's app is not on any origin branch (checked after fetch).
- A's join diagram (B-G-13) not placed: Henry to decide.

## 2026-10-29 · Henry + Claude · Solomon's app reviewed; report §8; cap statement restored

**Done**
- Pulled e302e8b (Benson: chart_ok handles A sources; audit 9/9 on rev 34; his handover files complete) and
  Solomon's 9d6cc35 and 12d2614 (app in deliverables/dashboard/app/).
- Python 3.12.10 installed (per user); app .venv built from requirements.txt (git-ignored). 13 of 13 app tests pass.
  The app runs with no error on any tab; all 19 planned panels are present; the test-view numbers at 4/15 match the
  report. Review findings for Solomon in spec/doc_outbox/handshake_solomon_2026-10-29_0904.md: one wording fix (3.4
  compares the combined volume with the 6-a-day cap, which applies to B alone), four small improvements (4/15
  label, visible intervals, test-view screenshot, panel test) and the hosting request.
- Report §8: placeholder replaced by "Using the app" (local URL; hosted address to follow).
- Report §9 and deck slide 15 notes: review-cap statement restored (B-CR-30 requires it; the plan-v2 rewrite had
  dropped it).
- Audit (official script): 9/9 PASS on doc rev 36 with the live deck (version 17); one run takes about 16 s.
- Reminder set for Henry: finish review, proofreading and PDF on 2026-10-30.

**Not done yet**
- Hosting and a public URL (Solomon, with Benson). Proofreading and PDF (Henry, by 2026-10-30).

## 2026-10-29 · Henry + Claude · dashboard plan revision 2 implemented on our side

**Done**
- Gap analysis and fix plan (Claude Doc https://claude.ai/artifact/WNhnLGdNqzWRWsjdBrwBwU); Henry's decisions D1–D5
  recorded there. DASHBOARD_PLAN.md revision 2 (APPROVED 2026-10-29): Tab 1 ports every Phase 1 section plus customer
  and seller rating distributions (each order once at its lowest valid score); new Tab 4 "Score an order"; hosting
  on Render.com (model API) and Streamlit Community Cloud (app); 2.8 and 3.9 point to Tab 4.
- App (Solomon's code, edited on our side per D5): review fixes G1–G4 (cap sentence per B-CR-30; TP/FP/FN row;
  4/15 and 1/6 labels; visible intervals and B-minus-A cards); Tab 1 rewritten from deployment/app.py@f31998e;
  new alerts.py, score_tab.py, model_client.py. The alert list comes from T1's stored predictions without the label
  column: 540 B alerts at 4/15 and 1,428 A alerts at 1/6 outside the scope (the report's 5.6 and 14.9 a day); live
  rebuilt scores equal the stored ones (largest difference 1.7e-16). Scenarios: logistics −10% (regression's
  estimated transit = predicted lead time − dispatch days; the alert model's two route inputs cut by the same days;
  B only) and freight −20/−30/−50/−99% ("Free shipping"); all labelled as associations.
- Model API (deliverables/dashboard/api/, FastAPI): same predictions as the local path (≤ 1e-11 over JSON);
  hosting settings in api/README.md. Accounts and repository access are Henry's or Benson's to set up.
- Tests: app 18/18, API 3/3 (Python 3.12.10). Browser pass over all four tabs, no exception.
- Report §8 updated (four tabs, Score an order, API); review doc rev 37; audit 9/9 on rev 37.
- Solomon: handshake_solomon_2026-10-29_1015.md (what changed; check it runs); the 09:04 one superseded, never sent.

**Not done yet**
- G5: new screenshots (test view at 4/15, the new tabs) — to take from the hosted app.
- Hosting: Render and Streamlit accounts, repository access, branch choice (Henry or Benson).

## 2026-10-29 · Henry + Claude · Score an order tab, revision 2.1

**Done** (Henry's four points)
- 4.1: one order picked with a radio button over a 25-order page (the table's checkbox selection removed);
  review_position shown as sn; model column moved to the right.
- 4.2: order id, sn and model shown first; predictions and scenarios renumbered 4.2.1 and 4.2.2.
- New 4.3: every alerted order under every scenario (5 single + logistics −10% with each of the 4 freight cuts):
  counts of alerts that would stop, and the list for the scenarios picked (downloadable). Results on the 1,968
  alerts: logistics −10% stops 34 of 536 B alerts; freight −20% 227, −30% 353, −50% 647, free shipping 1,765
  (all 1,967 free-shipping rows fall below R$ 7.39, the 1st percentile of freight, so that result is an
  extrapolation and is marked "outside training range"); logistics + freight 78 to 451. All labelled as associations.
- Plan revision 2.1 (panels 4.1–4.3); tests 19/19; browser pass, no exception.

## 2026-10-29 · Henry + Claude · deck v2 (A first)

**Done**
- Henry's five deck comments (slides 7, 11, 12, 13, 14): A first, A's limits shown by charts, then B; combined pages;
  validation and test on separate slides; regression and classification test on one slide each, labelled by task,
  with more data.
- v1 kept: https://claude.ai/artifact/VtyNdrjEovfAvycTPmvy23 untouched; its sources frozen in deliverables/deck_v1/
  (identical to the live v1 after fill).
- v2: new deck https://claude.ai/artifact/NBiGTdX9JKB5kAeeX34gvc, 15 slides (cover, problem, data, prep, eda,
  a_features, a_select, a_models, a_limits, b_features, b_scope, validation, test_reg, test_clf, use); sources replace
  deliverables/deck/. 88 register ids, all also in the report; 18 charts uploaded to the v2 deck.
- Register: 5 new figure items (A's s02 join diagram under B-G-13; A's s03 cumulative importance and screens 3.11,
  3.12 under B-G-11); 207 items.

**Not done yet**
- Slides 7 and 8 carry pending chart slots for A's s04–s08 figures; audit on v2 needs the deck map updated.

**Questions for Benson** (spec/doc_outbox/handshake_benson_deck_v2.md)
1. Extend B-G-13 to A's s04–s08 figures (proposed B-G-14)?
2. Replace figure_map.json's deck section with the v2 asset map.

## 2026-10-29 · Henry + Claude · deck v2, review round 2 (bigger charts)

**Done**
- Henry's five v2 comments (slides 5-9 and "all the following slides"): slides 5-15 relaid chart first (narrower
  margins, smaller title, text moved into short card rows or wide two-row tables, details to speaker notes).
- Slide 5: A's detractor target bar (new register item F.A3.clf.target_bar, A evidence 3.2, B-G-11) beside the KDE.
- Slide 7: heatmap enlarged; the pending A selection-curve note moved to the bottom.
- Slide 8: the fold chart F.reg.partition (A's boundaries, B's rows inside) full width, as in v1; A's own ladder
  chart is still pending the A-source rule (B's ladder is not shown on an A slide).
- Slide 14: test curves full width with a wide table; the threshold chart moved to slide 15 next to the buffer.
- Checked rendered at 1920x1080 (local headless Edge with the register PNGs): no overlaps; 88 ids, all in the report.
- Register 208 items; v2 deck version 4; handshake deck map gains the two new asset ids.

**Not done yet**
- Charts whose own text is small (A's s03 screens on slide 9, the two-chart slides 6, 10, 12, 15) stay hard to read
  (Decision 3 in the Benson handshake asks for presentation renders from the saved figure data).
  at half width; a fix needs presentation renders with larger fonts (Benson's call) or more slides.
- Audit on v2 waits on Benson's figure_map update; nothing pushed.

## 2026-10-29 · Henry + Claude · deck v2, review round 3 (one type scale); Benson prompt combined

**Done**
- Pushed e5/deliverables-henry (2 commits from round 2 and the literature audit).
- Henry's round 3 comments: slide 5 caption at least 28 px; slide 10 "(limit 2)" unclear (it named A's limit 2 on
  slide 9, never a cap) → replaced by a table column "Answers A's limit" with the limit spelled out; slide 11 table and
  text box fonts balanced; "balance font size, chart size and table size" across the deck.
- Every slide on one scale: body, tables and chart labels 28 px, titles 48 px, section labels 24 px, footers 22 px;
  padding 88/112/128 px. Wide tables on slides 11, 13 and 14 transposed (metrics as rows) so they fit at 28 px;
  Brier moved into the ranking table on slide 14. Henry's editor edits on slides 8, 9, 11, 13 were layout only (text
  checked identical) and were rebuilt on the scale. Local headless render: no slide past y 952, no horizontal
  overflow. 88 register ids, all also in the report. v2 deck version 27 (1793270042-108a).
- spec/doc_outbox/handshake_benson_2026-10-29_combined.md (D1–D7): merges the unsent deck v2 and Pipeline A report
  prompts, which both proposed B-G-14; deck chart boxes updated to round 3 (bdb47ae, pushed).

**Not done yet**
- Audit on v2 waits on Benson (D2 deck map). Chart-internal text still small until D3 renders exist.

## 2026-10-29 · Henry + Claude · Score an order 4.1: selector in the table (revision 2.2)

**Done**
- 4.1: the radio row under the table is replaced by the table's own selection column at the left
  (`st.dataframe`, `selection_mode="single-row-required"`): one order always picked, the first by default, reset per
  page. DASHBOARD_PLAN.md 4.1 row updated (revision 2.2).
- App tests 19/19. Browser pass on the tab: picking a row updates 4.2; page 2 opens on sn 26; no console error.

## 2026-10-29 · Henry + Claude · speaker notes, app screenshots, report review

**Done**
- Brief checked: the final report limit is 15–20 pages (excluding cover, references, appendices), 12 pt,
  single-spaced, with figure captions and table labels; no word limit. The ~8,150 words in plan v2 was our own
  estimate of what fits 18–20 pages with the figures. The talk is 10 minutes plus 5 of Q&A (plan v2 assumed 12).
- Speaker notes rewritten for a 10-minute slot (9:00 of slides at about 110 words a minute, then a 1:00 demo), in
  each slide template's notes; deck v2 version 28 (1793274446-5837), slide bodies unchanged. 80 register ids, all in
  the report. Printable script with the demo steps: deliverables/deck/SPEAKER_NOTES.md.
- Eight app screenshots at 1600x1000 from the local app (headless Edge, stored outputs only):
  deliverables/dashboard/app/screenshots/2026-10-29/. Not yet placed in the deck (would need deck-map entries).

**Noticed**
- Panel 2.4 (promise buffer) opens on "A on A's test rows"; B's view should probably be the default.

**Not done yet**
- Hosting and the live URL: Benson (with the branch merge).

## 2026-10-29 · Henry + Claude · report: cover, table labels, page count, RMSE/R²/F1, trims, screenshots

**Done**
- Cover page (00_cover.md): title, course, team, app URL and member names as placeholders, GitHub link, date.
- Table labels on all 44 tables (body Tables 1–22, appendix A1–J3), numbered in the sources so they match the doc.
- Register 216 items: test RMSE and R² for both pipelines; F1, and A's precision and recall, at 1/6 (b09
  train_val_test, B9.1). §7.1 table gains RMSE and R² (A's R² on B's test orders is below zero, stated); §7.2 adds F1.
- §2 literature cut to about 430 words; the source table removed (its content is in records/literature_register.md).
- Four charts moved to appendices A, E, I, J; §8 gains two app screenshots (captioned "Screenshots 1–2.").
- Page check: the filled report rendered at 12 pt Times New Roman, single-spaced, A4, 2 cm margins, every figure,
  printed with headless Edge. Body (executive summary to limitations) 16 pages, was 18; whole document 24.
- Review doc rev 56 (body replaced from the sources; the header note's date removed, which the audit read as a
  number). Audit on the rev 56 export: 8/9 pass; deck charts fail until Benson maps v2 (D2).
- Restructure plan for items 4–6 (B first, naming), for Henry's review before any change:
  https://claude.ai/artifact/FRCGWYMKA4Q4fAKoWvaVqi
- Benson prompt gains D8: figure_map doc section renumbered for rev 56 (spec/doc_outbox/figure_map_doc_rev56_proposed.json).

**Not done yet**
- Items 4–6 wait on Henry's review of the plan. Member names and the live URL on the cover.

## 2026-10-29: report restructure (items 4–6), business background, screenshots to appendix

Henry approved the restructure plan (https://claude.ai/artifact/FRCGWYMKA4Q4fAKoWvaVqi) with its recommended options
and asked for business figures in §1 and the screenshots in the appendix. Revenue and repeat-customer figures are not
stored anywhere the register may read; Henry chose stored figures only (no new run).

- 9b77200 item 6: "Pipeline A" / "Pipeline B" throughout (66 lines, list in report/records/naming_changes_item6.txt).
- 6e872e0 item 5: §5 leads with Pipeline B's features; A's pool condensed to one inherited-base paragraph.
- b204328 item 4: new §1.1 holds Table 14 (now Table 3); §6.5 "Adopting Pipeline B".
- This commit: §1 "Why it matters to the business" (7 new A3 register items, 223 built); screenshots to appendix K;
  tables renumbered. Each step: placeholder set compared with the previous commit, `check` resolves every
  placeholder. Body 17 pages at 12 pt.
- Deck footers that cite report sections updated (slides 7, 9, 10).

- Henry approved the result. Review doc rev 57: body replaced from the sources (doc_body builder v4). Export in
  deliverables/audit/inputs/report_export_rev57.md. Audit 8/9 pass; the ninth is the deck chart map (Benson D2).

**Not done yet**
- figure_map D8 still holds: no figure changed order. Member names and the live URL on the cover.

## 2026-10-30: business context in §1, dashboard revision 2.3

Henry (delegated lead) kept the report at 12 pt single-spaced (the brief's format) and asked for revenue and the
customer repeat rate in the problem statement, quoted in the text under the audit's rules, from the dashboard's
Business overview data and without touching Pipelines A or B.

- Dashboard revision 2.3: the score panels leave tabs 2 and 3 (data health is now 2.8 and 3.9), tab 4 is named
  "ML deployment"; app tests 19/19; checked in the browser. Screenshots unchanged (the tab bar is not in them).
- B-CR-41: `deliverables/business_context/make_business_context.py` (dashboard code, March 2017 to April 2018,
  before the test period) wrote run 20261030T004253Z on commit 3268c20; the register reads it as `BIZ/<file>`
  and the audit checks the chart against its manifest. 9 register items (232 built).
- §1: revenue sentence and repeat rate (replaces "churn is not measured"), new Figure 1. figure_map doc section
  rebuilt for 29 figures (replaces Benson's D8). Review doc rev 58; audit 8/9 (deck map, D2). Body 17 pages.

**Not done yet**
- Milestone 2 report (Pipeline A only, 6–8 pages): plan next.
- Deck v2 chart map (D2) and the cover's member names and app URL.

