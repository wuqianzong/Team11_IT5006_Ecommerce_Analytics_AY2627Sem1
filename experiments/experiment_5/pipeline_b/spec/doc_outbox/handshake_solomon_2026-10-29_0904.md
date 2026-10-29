# Handshake prompt for Solomon's Claude (from Henry, 2026-10-29 09:04)

Paste everything below the line into Solomon's Claude Code session at the repo root.

---

You are working for Solomon, who built the Team 11 dashboard in
`experiments/experiment_5/pipeline_b/deliverables/dashboard/app/` (commits 9d6cc35 and 12d2614 on branch
`e5/deliverables-henry`). Henry's Claude reviewed it on 2026-10-29 against the approved `DASHBOARD_PLAN.md`. Henry
plans to merge your work once the points below are settled.

**Review result.** On a fresh Python 3.12.10 environment built from `requirements.txt`, all 13 tests pass. The app
runs with no errors on any tab, and all 19 planned panels are present. The test-period numbers match the report:
lead time 3.30 against 4.03, B at 4/15 with 5.62 alerts a day and 34.6% precision, A's fallback at 14.88 and 13.3%,
and 20.50 alerts a day combined. The scope banner, the model badges, "Not scored yet", "derived for display" and the
alert review order note all use the plan's wording. Thank you.

**Step 0.** `git fetch origin`, `git switch e5/deliverables-henry`, `git pull --rebase origin e5/deliverables-henry`.
The same rules as before apply: write only in `deliverables/dashboard/app/`; the app reads and never computes; never
"not served" or "4/16"; commit messages start with "Pipeline B:"; pull with rebase before pushing; never force-push;
never push to `milestone-3` or `main`; never commit `_DONOTCOMMIT/`.

**Step 1. Required fix (wording).** In 3.4, the combined line says "The stored combined ... volume is 20.50
alerts/day, against the 6/day review cap." The 6-a-day review cap asked for at the B9 review applies to
Pipeline B alone (B-CR-30, third-party audit finding B10-F1; the team accepted a higher combined volume). Comparing the combined volume with that cap misstates the rule. Suggested
wording: "The 6-a-day review cap applies to Pipeline B's alerts; the combined volume includes A's fallback and is
higher, as the team accepted." If you show B against the cap, compare B's own alerts a day with it.

**Step 2. Improvements (please do; small).**
1. **Slider label.** The operating stop reads "0.2667 (operating)". Show it as "4/15 (operating)", and the frozen stop
   as "1/6 (frozen)" if it is on the slider. The report and deck use the fractions.
2. **Headline intervals.** Plan rows 2.1 and 3.1 ask for the 95% intervals on the KPI cards. Today they appear only in
   the hover help, and B minus A is in a table below. Show each interval under its card (for example "95% CI
   3.24–3.35"), and B minus A with its interval as its own card. B against the dummy (lead time) can stay in the table.
3. **Screenshot for the report.** `screenshots/threshold_4_15.png` shows the Validation view (4.00 a day). Report §8
   quotes the test figures, so add a second screenshot of 3.4 in the "Test (post-test view)" at 4/15. Keep the
   validation one.
4. **Plan-contract test (optional).** Add a test that every panel id of the plan (2.1–2.9, 3.1–3.10) appears as a
   panel header in the app.

**Step 3. Hosting (Henry's request).** The app runs only at `http://localhost:8501`. Henry needs a hosted address
for report §8 and for the live demo (slides lock 2026-11-04; report due 2026-11-08). Ask Benson where to host it
(plan §6.1 and §7), and check that the host can run Python 3.12 with the pinned packages and read the stored
outputs the app needs, without the raw data under `_DONOTCOMMIT/`. If hosting is not possible by 2026-11-03, tell
Henry, so the demo can run from a laptop.

**Step 4. Reply to Henry** with: the fix commit, the improvements done (or why not), the test-view screenshot, and
the hosted URL (or the hosting status).
