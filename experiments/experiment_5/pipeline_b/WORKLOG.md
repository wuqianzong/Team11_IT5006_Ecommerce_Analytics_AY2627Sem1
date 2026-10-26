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
