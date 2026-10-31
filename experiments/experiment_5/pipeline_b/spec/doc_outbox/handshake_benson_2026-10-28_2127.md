# Handshake prompt for Benson's Claude (from Henry, 2026-10-28 21:27)

Paste everything below the line into Benson's Claude Code session at the repo root.

---

You are working for Benson (experiment lead) on Experiment 5, Pipeline B. Henry's Claude has finished the steps
Benson set after 250204b. Branch `e5/deliverables-henry` is pushed at **b2ef881**. One failure is in the audit
script, which is Benson's, so the official audit cannot pass until Benson fixes it.

**Step 0. Get up to date (read only).**
1. `git fetch origin`, `git switch e5/deliverables-henry`, `git pull --rebase origin e5/deliverables-henry`;
   confirm b2ef881 is in the log.
2. Read the last `pipeline_b/WORKLOG.md` entry ("Benson's audit steps (after 250204b)") and
   `pipeline_b/deliverables/report/records/CHANGES.md` (last row).
3. Do not edit Henry's files (`deliverables/report/`, `deliverables/deck/`, `deliverables/dashboard/DASHBOARD_PLAN.md`,
   `evidence/registry_B.yaml`, `WORKLOG.md`, `HANDOVER.md`, `spec/doc_outbox/`). Never rerun a stage, T1 or a
   model; never tag without Benson; never commit `_DONOTCOMMIT/`.

**What Henry's side did (for Benson to review)**
- Review doc at rev 34: one `*Figure N.*` caption per chart (the 8 combined captions were split), and a header note
  without dates.
- `deliverables/audit/figure_map.json`: `doc` section rebuilt for the 28 charts, with blob and asset ids read from
  the doc's blob records (your one-time exception). `deck` is unchanged; the note's date is updated.
- `deliverables/audit/inputs/`: `report_export_rev34.md`, 28 doc assets, 14 deck assets and the 15 live slides.
  The rev 29 export and the residuals asset were removed.
- Report sources: every paragraph is on one line, so it compares line for line with the doc export. No wording
  changed.
- `CHANGES.md` and `literature_register.md` moved to `deliverables/report/records/`: the audit reads every `*.md`
  in `deliverables/report/` as report text.
- `HANDOVER.md` marked closed; `spec/doc_outbox/README.md` marks the B10/B11 files and sync notes complete.

**Step 1. The failure to fix (Benson's script).** Run, from `experiments/experiment_5`:

```
python pipeline_b/audit_deliverables_B.py --doc pipeline_b/deliverables/audit/inputs/report_export_rev34.md --deck pipeline_b/deliverables/audit/inputs/deck --doc-assets pipeline_b/deliverables/audit/inputs/doc_assets --deck-assets pipeline_b/deliverables/audit/inputs/deck_assets
```

It stops with `FileNotFoundError: ...\pipeline_b\stages\A\s03_eda\outputs\_manifest.json`. In `chart_ok`, the
manifest path is built from `e["source"]`, which for the four A-source charts (B-G-11, B-G-13) starts with `A/`:

- F.A3.reg.target_kde ← `A/s03_eda/regression/outputs/figures/target_lead_days_kde.png`
- F.A3.reg.outcome_trends ← `A/s03_eda/regression/outputs/figures/outcome_trends.png`
- F.A3.clf.outcome_trends ← `A/s03_eda/classification/outputs/figures/outcome_trends.png`
- F.A3.reg.correlation_heatmap ← `A/s03_eda/regression/outputs/figures/numeric_correlation_heatmap.png`

Proposed fix, in Benson's words: for a source starting with `A/`, compare the asset and the register figure with
A's file at tag `e5-A-frozen` (sha256, as `build_evidence_B.verify_a_source` does), instead of a B manifest.

Henry's Claude checked by hand that for each of the four, doc asset = register figure = A's file at
`e5-A-frozen`. A diagnostic copy of the script, kept in a scratchpad and not committed, skips the manifest lookup
for these four and gives **PASS on all 9 checks**.

**Step 2. After Benson's OK:** fix `chart_ok`, rerun the command above, and report each check as PASS or FAIL. If
all pass, write `deliverables/audit/audit_result.json` (the script's default `--out`) and commit (message starts
"Pipeline B:"). Tell Henry the commit.

**Step 3. Benson's files to close.** `deliverables/HANDOVER_TO_HENRY.md`, `DELIVERABLE_IDEAS.md` and
`M2_FEEDBACK_GAPS.md` are Benson's. Henry asks Benson to mark them complete when he agrees. Still open on Henry's
side:
- the app URL and screenshots for report §8;
- final proofreading and the PDF export (report due 2026-11-08; slides lock 2026-11-04).

**Step 4. Also open.**
- Solomon's dashboard app is not on any origin branch (checked after fetch, 2026-10-28). Ask Solomon where he
  pushed it.
- Hosting and launch of the app: Benson's call (dashboard plan §6.1, §7).
- A's join diagram (B-G-13): Henry decides whether to add it to report §3 and deck slide 3. If added, it becomes
  chart 29 and the audit is rerun.

**Step 5. Reply to Henry** with: the `chart_ok` fix commit, the audit result, and which of the three files in Step 3
are now marked complete.
