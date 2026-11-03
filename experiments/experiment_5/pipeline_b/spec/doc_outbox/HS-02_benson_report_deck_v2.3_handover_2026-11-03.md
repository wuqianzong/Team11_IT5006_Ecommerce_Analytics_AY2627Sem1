# HS-02 · from: Henry (delegated lead) · to: Benson (experiment lead) · report and deck v2.3 handover
Status: OPEN 2026-11-03 · Answer by: 2026-11-04 (slides), 2026-11-08 (report) · Type: TASK

Paste everything below the line into your Claude session. Henry is out of tokens; your agent continues the final
report v2.3 and deck v2.3 from where his stopped.

---

## Get the right state
git fetch origin; git switch e5/validation-fixes-henry (pushed at ed434a7; not merged into milestone-3 or main)

## State (checked 2026-11-03)
- Unmerged, waiting for Benson's approval: B-CR-50 (business case), B-CR-51 (page budget), B-CR-52 (figures 20–23
  side by side) in `pipeline_b/CHANGELOG_B.md`; B-G-19 to B-G-23 `Proposed` and B-G-24 (Henry's 2/3-page limit) in
  `spec/decision_log_B.md`. Henry's summary: `doc_outbox/reply_benson_2026-11-03_v2.3_business_case.md`.
- Review doc https://claude.ai/artifact/USWnVhiKr35AqXwc4zQHAw at rev 59 (doc `de36b17f-b2e0-4686-b0ca-850ea2508b48`,
  tab `655ad2ae-6305`, body `41e1fe95-a208`). Deck v2.3 https://claude.ai/artifact/NBiGTdX9JKB5kAeeX34gvc, version 48
  (18 slides).
- Exports: `pipeline_b/deliverables/exports/2026-11-03/Team11_final_report_v2.3.docx` (body pages 2–20, references
  from page 20; limit 20) and `Team11_final_deck_v2.3.pptx`.
- Audit 9/9 on `deliverables/audit/inputs/report_export_rev59.md` and deck version 48; register 508 items.
- Deadlines: slides 4 Nov, report 8 Nov.

## Rules (binding; from README §0.1, §7–§9, both CLAUDE.md files and HS-01)
1. Write only inside `experiments/experiment_5/`. Never commit `_DONOTCOMMIT/`; run `git diff --cached --name-only`
   before every commit.
2. Every number comes from the register (`pipeline_b/evidence/registry_B.yaml`) as a `{{id}}` placeholder; never type
   one by hand.
3. Edit the sources first (`deliverables/report/*.md`, deck slides in `deliverables/deck/project/slides/`), then the
   doc or deck; never the reverse.
4. A new chart needs a producer with a manifest (patterns: `deliverables/deck/renders/`, `deliverables/report/renders/`)
   and a register entry.
5. After every change: `.venv/Scripts/python.exe pipeline_b/build_evidence_B.py build` and `check <files>`; the
   deliverables audit (command in `deliverables/audit/README.md`) must be 9/9; then
   `.venv/Scripts/python.exe -m pytest pipeline_b/tests tests/test_guards.py`.
6. Records for each change: a B-CR in `CHANGELOG_B.md` (next B-CR-53, next decision B-G-25), a row in
   `deliverables/report/records/CHANGES.md`, a `WORKLOG.md` entry, the audit README's "Last run".
7. The report body ends on or before page 20 (`format_submission_docx.ps1` prints it).
8. Version labels move together for report and deck (doc title and note, deck footers, export file names,
   `deliverables/README.md`); a content change after v2.3 is v2.4.
9. Commit with `git commit -F <message file>` ending in the attribution line; never force-push; never push to main.

## Rebuild the Word copy
Scripts and steps: `pipeline_b/deliverables/report/build/README.md` (`docx_fill.py`, `report_v2_3_figs.tsv`,
`pair_fill.py`, `format_submission_docx.ps1`; Windows with Word for the last step). Download the doc's Word export in a
browser; update the .tsv when the doc's pictures change.

## Saving tokens
- Batch commands so a round takes few calls.
- Read the newest `WORKLOG.md` entry and the last rows of the records, not whole logs.
- Read the doc with `sinceRev` (changes since the last rev you know), not in full.
- No inline base64 exports: download in a browser, or rebuild from the previous export plus a verified change list,
  as `deliverables/audit/README.md` describes for rev 59.
- One visual check per round.

## Tasks
1. Recheck and approve (or change) B-CR-50 to B-CR-52 and B-G-19 to B-G-24, including literature rows 13 and 14;
   merge into milestone-3.
2. Rename the review doc: its file name still reads v2.2 (heading and note say v2.3).
3. Further refinements as you decide, under the rules above.

## After answering
Set Status: ANSWERED with the merge commit; record your decisions in `spec/decision_log_B.md` and
`spec/human_decisions_B.yaml`.
