# Follow-up prompt for Solomon's Claude (from Henry, 2026-10-28)

Paste everything below the line into Solomon's Claude Code session at the repo root.

---

You are working for Solomon, who builds the Team 11 dashboard. Henry owns its content; the contract is
`experiments/experiment_5/pipeline_b/deliverables/dashboard/DASHBOARD_PLAN.md`, now **APPROVED** by Henry
(commit 9b5da75 on branch `e5/deliverables-henry`, pushed; head 393579e). Henry and Solomon share that branch.

**Step 0. Get up to date (read only).**
1. `git fetch origin`, `git switch e5/deliverables-henry`, `git pull --rebase origin e5/deliverables-henry`.
2. Read DASHBOARD_PLAN.md in full: §0 rules, §1 scope message, §2–§4 tabs and panels (each with its source file),
   §6 decisions, §7 what waits.
3. Read `pipeline_b/e5b/serving.py` (`Release.load(task)`); this is the only way the Score panels predict.

**Rules (from the plan, binding).**
- Write only in `deliverables/dashboard/app/`. Do not edit the plan, the report, the deck, `e5b/`,
  `stages/*/outputs/` or `deployment/app.py` (copy the Phase 1 functions you need into `app/` with a provenance
  comment: source file and commit).
- The app reads, never computes: every number and chart comes from the stored file the plan names. Only the two
  display exceptions in §0.1 are allowed, labelled "derived for display". Never refit, never read a test label.
- Every model number is labelled with its model (Pipeline B or A), its rows and "validation = selection score;
  test = read once". The scope banner and per-order badge use the exact wording in §1; never write "not served".
- Thresholds: Pipeline B has a slider over the stored B9.10 thresholds, default 4/15; Pipeline A's fallback is fixed
  at 1/6. Never write "4/16".
- Never commit `_DONOTCOMMIT/`. Commit messages start with "Pipeline B:". Pull with rebase before pushing; never
  force-push; never push to `milestone-3` or `main`.

**New since the plan was approved (text only, no new panel).** Henry decided the alert review order when capacity
is short: Pipeline B's alerts at 4/15 first; then Pipeline A's fallback alerts, reviewed at carrier handover, by
handover delay (longest first) with order value as the tie-break. It is an operational rule, not a measured
result. If the alert-statistics panel (3.4) has room, show this as one note with that label; do not sort or
compute anything new for it. Ask Henry if it does not fit.

**Step 1. Build** the three tabs panel by panel, as the plan lists them. For each panel, check its source file
exists on this branch before coding; list any missing file for Henry instead of working around it.

**Step 2. Hosting.** Ask Benson where and how the app is launched (plan §6.1 and §7).

**Step 3. Deliver to Henry**, by 2026-11-03 if possible (slides lock 2026-11-04, report due 2026-11-08):
- the live URL and short usage instructions (for report §8);
- screenshots of each tab, and of the Score panel and the threshold slider at 4/15 (for report §8 and deck slide 15);
- a list of any panel not built, and why.
