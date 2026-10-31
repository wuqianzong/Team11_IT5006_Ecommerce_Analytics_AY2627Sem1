# HS-01 · from: Benson · to: Henry (delegated lead) · validation fixes on milestone-3
Status: SENT 2026-10-31 (received, in progress) · Answer by: 2026-11-02 (proposed) · Type: TASK

## Get the right state
git fetch origin; git switch e5/validation-fixes-henry (cut from milestone-3 at 54bc6d0)

## Context
Benson's Claude validated milestone-3 at 54bc6d0 on Benson's Mac: frozen code and outputs unchanged since
`e5-reproduced`, tags match origin, the dashboard's 21 tests pass. Two fixes are needed, recorded as findings
T-11 and T-06 in `../../deliverables/audit/findings.yaml`; the report as received and the triage are in
`../../deliverables/audit/runs/2026-10-31_benson_validation_54bc6d0.md`.

## Tasks
1. T-11 (high): line-ending-safe manifest hashes for text inputs; rerun the business_context producer; rebuild the
   register (decision B-G-15).
2. T-06 (medium): encoding guard, option 1 in tooling and tests, option 2b exclusion of the 8 frozen e5b modules
   (decision B-G-16).
3. Acceptance checks: A suite, `pipeline_b/tests`, register build (only the commit line changes), deliverables audit
   9/9, normalised CSV hash `32c2f4ee…` on both machines.
4. One CR in `CHANGELOG.md`, one B-CR in `CHANGELOG_B.md` (Henry as delegated lead); commit, push.

## What we do not do
No T1 rerun, no refit, no tag moved; no edit to the frozen e5b modules; no change in `tests/test_guards.py` other
than the exclusion list.

## After answering
Reply to Benson with the commit and the checks that ran; set Status: ANSWERED. Benson's Claude rechecks on the Mac;
on PASS, T-11 and T-06 become Verified and this hand-off CLOSED.
