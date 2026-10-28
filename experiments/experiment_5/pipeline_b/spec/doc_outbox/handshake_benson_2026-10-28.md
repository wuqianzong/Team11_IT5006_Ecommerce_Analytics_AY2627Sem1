# Handshake prompt for Benson's Claude (from Henry, 2026-10-28)

Paste everything below the line into Benson's Claude Code session at the repo root.

---

You are working for Benson (experiment lead) on Experiment 5, Pipeline B. Henry's branch `e5/deliverables-henry`
(pushed, head 393579e) holds the reworked report, the 15-slide deck and the approved dashboard plan. Henry needs two
decisions and one file change from Benson so the deliverables audit can run.

**Step 0. Get up to date (read only).**
1. `git fetch origin` and `git log --oneline origin/e5/deliverables-henry -15`; confirm 393579e is there.
2. Read, on that branch: `experiments/experiment_5/pipeline_b/WORKLOG.md` (the 2026-10-28 entries, "Questions
   for Benson"), `deliverables/report/CHANGES.md`, `deliverables/audit/figure_map.json` and
   `audit_deliverables_B.py` (line 70 and the chart checks).
3. Do not edit Henry's files (`deliverables/report/`, `deliverables/deck/`, `deliverables/dashboard/DASHBOARD_PLAN.md`,
   `evidence/registry_B.yaml`, `WORKLOG.md`, `HANDOVER.md`, `spec/doc_outbox/`). Never rerun a stage, T1 or a
   model; never tag; never push to `milestone-3` or `main`; never commit `_DONOTCOMMIT/`.

**Step 1. Decision for Benson: the audit's chart count.** `audit_deliverables_B.py` line 70 expects exactly 16
report charts; the report now has 28. Proposed change: read the expected count from `figure_map.json` (the number of
`doc` entries). Ask Benson: approve, or keep a hard-coded count (then 28)?

**Step 2. Decision for Benson: A's s02 figures.** B-G-11 lets the register read A's s03 outputs from tag
`e5-A-frozen`. Henry asks whether the same rule may cover A's s02 data-structure figure (join diagram), for
report §3 and deck slide 3. Today slide 3 has a diagram built on the slide (no numbers) and §3 has no figure, so a
"no" changes nothing. Ask Benson: yes or no.

**Step 3. Update `figure_map.json` (Benson's file), after his OK.**
- `deck`: asset id → register figure. Add:
  - 50fdc703d99e15f5c4a7777ee6fbd14b F.A3.reg.target_kde
  - 55679204d325313ce29239b9bb6233b0 F.reg.lateness_by_route
  - 8bc9d14e0f89ead4d86268b56740e773 F.A3.reg.outcome_trends
  - 92b53ee5e77920e4ed1d4d3413e42f9c F.reg.history_coverage
  - c4ea3f0a8d8c5c3d379501a5c9bd9f98 F.A3.reg.correlation_heatmap
  - 4bd6826282b44966a891f99a10bea5aa F.reg.selection
  - 87433e4d8e5e7299c327c25d0b3ab428 F.clf.ranking_stability
  - 8c3466a8505cdbaac46fe14c08d92041 F.reg.family_ladder
  - 926ff6cf67efd1bc07c1c4667eebe324 F.clf.family_ladder
  Keep 23cdda49…, 3d0b5f02…, 1abc90f2…, 5c1cf0ec…, 9705c7c3…. Remove 2dcb30e7… (residuals; no longer on the deck).
- `doc`: the review doc (https://claude.ai/artifact/Gp8qHXHdffLf3t78JcMWid, rev 32) numbers its figures 1–28 in a new
  order. Rebuild the `doc` map by reading each image's blob from the doc and its asset from the doc's blob records,
  as on 2026-10-26. The 12 new blobs and their register figures:
  - blob/8339181d-5267 F.A3.reg.target_kde; blob/d74ff836-7bd4 F.A3.reg.outcome_trends;
    blob/98ace730-b532 F.A3.clf.outcome_trends; blob/914ec01d-9e51 F.reg.history_coverage;
    blob/1636d72e-cff4 F.A3.reg.correlation_heatmap; blob/42157256-7b88 F.clf.selection;
    blob/3044a81c-e3ed F.reg.ranking_stability; blob/c87abb1f-57ab F.clf.ranking_stability;
    blob/11276969-f35a F.reg.family_ladder; blob/c26f6dfc-698d F.clf.family_ladder;
    blob/3fe38cbf-9b92 F.clf.auc_brier; blob/ef04f6b4-bdb5 F.reg.buffer_curve.
  The other 16 reuse the blobs already in the map.
- Commit on a branch of Benson's choosing (message starts "Pipeline B:"). Tell Henry the commit, so he can bring it
  into `e5/deliverables-henry`.

**Step 4. Run the audit and report.** With Benson's change in place: export the review doc as markdown, download the
doc and deck chart assets, and run
`python pipeline_b/audit_deliverables_B.py --doc <report.md> --deck <dir> --doc-assets <dir> --deck-assets <dir>`.
Report each check PASS or FAIL with its detail. Do not fix Henry's text yourself: list any failure for Henry.

**Step 5. Reply to Henry** with: the two decisions, the figure_map commit, and the audit result.
