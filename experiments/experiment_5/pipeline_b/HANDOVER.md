# Pipeline B handover (B10 Release)

**Status: CLOSED (2026-10-28).** B10 is finished: branch `e5/b10-henry` was merged into `milestone-3` on
2026-10-27 and is not worked on again. Henry's current work (report, deck, dashboard plan) is on
`e5/deliverables-henry`; its state is in `WORKLOG.md`. The open items below are kept as a record; the ones still
live (release tag, migration, app URL) are Benson's or Solomon's and are tracked in `WORKLOG.md`.

**Who is working:** Henry and his Claude, on branch `e5/b10-henry`, while Benson (Wu Qianzong,
experiment lead) is away. Benson's Claude resumes from this file and `WORKLOG.md`.

## Current state (2026-10-26)

- B9 accepted on 2026-10-25, tag `e5-B-s09-accepted` (commit 85822c8). B10 starts from there.
- Tags verified on the remote: `e5-A-frozen` c7d15c7, `e5-B-frozen` e4fa1a6, `e5-T1-tested` 7e6941f,
  `e5-B-s09-accepted` 85822c8.
- B10 scope B10.1–B10.7 approved by Benson; the blueprint `spec/blueprints/b10_release.md` is a DRAFT
  waiting for agreement. No B10 code yet.
- Environment: `experiments/experiment_5/.venv` on Python 3.13.7 (the pin says 3.13.9; deviation
  approved by Benson, logged in `WORKLOG.md`). B10.1 parity is the acceptance test for it.
  Windows interpreter: `.venv/Scripts/python.exe`.

## Rules for this handover (from Benson's brief to Henry, binding)

1. Write only inside `experiments/experiment_5/pipeline_b/`. Read anything else.
2. No migration into the working folders.
3. T1 was read once (`e5-T1-tested`): never rerun it, never score the test cohort again, never re-choose
   a model, calibration or threshold. Re-predicting T1's test rows without labels or scoring, for
   parity only, is allowed (B-G-08).
4. A frozen at `e5-A-frozen`, B at `e5-B-frozen`. Never move or re-create a tag; never refit a
   frozen recipe on new data.
5. Never type a metric from memory; cite the output file or evidence ID. B numbers only from runs
   listed Current in `EVIDENCE.md`.
6. Decided: B serves orders inside its scope, A's frozen model the rest (B-G-06); classification
   operating threshold 4/15 (B-G-07; B-G-09's 5/14 withdrawn as a typo), frozen 1/6 kept as the unbiased
   result; A's fallback alerts at A's frozen 1/6 (B10-D2); in-scope orders before handover get no
   score (B10-D9). No more complex model families.
7. No report, slide deck or reproduction package unless Henry says so. Dashboard work only as far as
   the B10 blueprint covers it.
8. Unclear or conflicting spec: quote the text (file and section) and ask Henry.
9. Never push to `milestone-3` or `main`. Push only `e5/b10-henry`, and only when Henry says so.
10. Do not tag `e5-B-s10-accepted` until Henry confirms Benson or the lead approved.

## Where things are

| What | Where |
| --- | --- |
| Session log (read first) | `WORKLOG.md` |
| B10 blueprint | `spec/blueprints/b10_release.md` |
| Doc-ready text for the team doc (nobody on this branch can edit the doc) | `spec/doc_outbox/` |
| Decisions | `spec/decision_log_B.md` (next id B-G-10), `spec/human_decisions_B.yaml` |
| Current evidence | `EVIDENCE.md` |
| Frozen bundles used by B10 | `stages/t1_joint_test/<task>/outputs/bundles/{A,B}/` |

## How the team doc stays in sync

Henry's account cannot reach the team doc through Claude (it lives in Benson's account), so:
Claude writes doc-ready text to `spec/doc_outbox/`; Benson's Claude publishes it later, or Henry pastes
it by hand. Team comments reach Claude through Henry; each decision is recorded in the decision log
and the YAML. Benson refreshes the read-only mirror `spec/team_doc/` when a stage is accepted.

## Open items

- Benson reviewed the branch at 8b6d7fb (22 of 22 tests pass on his machine). Since then (2026-10-27): B-CR-31 (register test
  builds into tmp), B10 round 3 (B-G-10, B-CR-32), A's s03 EDA in the register (B-G-11, B-CR-33), report doc rev 29, deck
  version 1793077250-4a3c, audit inputs committed and audit 9/9. Summary: `spec/doc_outbox/sync_for_benson_r2.md`.
- 2026-10-27, Benson: B-G-10 and B-G-11 ratified; B10 round 3 accepted, tag e5-B-s10-accepted-r3 (B-CR-34).
- Reproduction-check policy decided (CR-056, B-CR-35): hash check on Benson's machine is the gate; other machines by tolerance.
- 2026-10-27, Benson: e5/b10-henry merged into milestone-3 (fast-forward to 46d68a4, pushed); outbox published to the doc
  (B10 Release tab and sub-tabs, B10 and B11 blueprint sections); mirror spec/team_doc/ refreshed.
- Henry: start new work from milestone-3 on a new branch (for example e5/b11-henry); keep WORKLOG, HANDOVER and doc_outbox.
- Still Benson's: release tag e5-release-1, migration (README §12), app and URL.
- Not tagged in this session by rule. Slow adapter tests fail on Henry's machine (refits not bit-reproducible), pass on Benson's.
