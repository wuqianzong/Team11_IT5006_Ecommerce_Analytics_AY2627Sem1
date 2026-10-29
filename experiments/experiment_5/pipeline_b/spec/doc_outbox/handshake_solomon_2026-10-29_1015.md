# Handshake prompt for Solomon's Claude (from Henry, 2026-10-29 10:15)

Supersedes `handshake_solomon_2026-10-29_0904.md` (never sent): Henry's side has now made those changes itself.

Paste everything below the line into Solomon's Claude Code session at the repo root.

---

You are working for Solomon, who built the Team 11 dashboard in
`experiments/experiment_5/pipeline_b/deliverables/dashboard/app/` (commits 9d6cc35 and 12d2614). Henry reviewed it on
2026-10-29: all 13 tests passed, the app ran cleanly and its test-period numbers matched the report. Thank you.
Henry then revised the dashboard plan and his side implemented the changes and the hosting set-up, so Solomon
does not need to build anything. This prompt tells Solomon what changed, so his copy stays in step.

**Step 0.** `git fetch origin`, `git switch e5/deliverables-henry`, `git pull --rebase origin e5/deliverables-henry`.
Do not edit `deliverables/dashboard/` while Henry's side is working on it; send suggestions to Henry instead.
The usual rules apply (commit messages start "Pipeline B:", no force-push, never push to `milestone-3` or `main`,
never commit `_DONOTCOMMIT/`).

**Step 1. Read what changed** (plan `DASHBOARD_PLAN.md`, revision 2, and `app/README.md`):
- Tab 1 now ports every Phase 1 section from `deployment/app.py` (KPI matrix with benchmarks, diagnostic stack,
  growth, category tables, revenue variance, category deep dive, order-level SLA, cohort growth) and adds customer
  and seller rating distributions (each order once at its lowest valid score).
- A fourth tab, Score an order: the held-out orders the serving rule alerts on (B at 4/15, A at 1/6 outside the
  seven states), in the capacity review order, with the order's details at handover, both predictions and scenarios
  (logistics −10%, freight −20/−30/−50%, free shipping). Panels 2.8 and 3.9 point to it.
- Review fixes: the cap sentence (the 6-a-day cap applies to Pipeline B alone, B-CR-30), TP / FP / FN on their own
  row, "4/15 (operating)" and "1/6 (frozen)" slider labels, visible 95% intervals and B minus A cards.
- New files: `app/dashboard_core/alerts.py`, `score_tab.py`, `model_client.py`, `app/tests/test_score_tab.py`, and
  `dashboard/api/` (a FastAPI service for the frozen models).

**Step 2. Check it runs on your machine.** With the app's environment, run `pytest app/tests` (18 tests) and
`pytest api/test_api.py` (3 tests; needs `fastapi`, `uvicorn` and `httpx`), then open the app and click through the
four tabs. Report anything that fails, with the message.

**Step 3. Hosting is Henry's side now.** The models go to Render.com and the app to Streamlit Community Cloud
(`dashboard/api/README.md` has every setting). No action for Solomon unless Henry asks.

**Step 4. Reply to Henry** with the test results from your machine and any issue you see.
