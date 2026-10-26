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
