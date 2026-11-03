# HS-03 · from: Benson (experiment lead) · to: Henry · produce report and deck v2.4 (Word and PowerPoint)
Status: OPEN 2026-11-03 · Answer by: before submission (slides and report due 8 Nov) · Type: TASK

Paste everything below the line into your Claude session.

---

## Get the right state
git fetch origin; git switch e5/validation-fixes-henry; git pull (head is the HS-03 commit, after 348e86d).
Benson merged this branch into milestone-3 and main on 2026-11-03 (B-CR-60), before your production. Keep working on
e5/validation-fixes-henry; after your 9/9, Benson merges again.

## What changed since your v2.3 (sources only, content final)
Read `CHANGELOG_B.md` B-CR-53 to B-CR-58, `spec/doc_outbox/reply_henry_2026-11-03_v2.4_content.md` and the newest
`WORKLOG.md` entries. In short:
- Business case: recommended buffer is the 5% recent-weeks rule (6.5 days; median promise 15.0 days, 4.2% late
  against Olist's 18.6 days, 5.5%; B-G-25); alert costs against no alert and populations (Tables K19, K21); proposed
  workflow by reason (Table K22); trigger and goal in the executive summary, §1 and slide 2; 2.9% repeat customers
  over 14 months; Fisher cited only for actual delivery.
- TA's advice (B-G-28): training results (§6.2 summary; appendix H with the learning curves), alert error analysis
  (§7.2 summary; appendix E, Table E4), reason for every Pipeline A feature (§5.1, Table D3 new column).
- Moved to the appendix, content kept (B-CR-57): learning curves and ladder gains (H), error analysis and the two
  by-state figures (E), full workflow paragraph (K).
- New evidence: BC.6 `cost_check.csv`, BC.7 `retention.csv`, BC.8 `error_profile.csv` (business case producer, no
  refit); register 622 items.
- Sources that changed: report `00_executive_summary`, `01_problem`, `05_features`, `06_modelling`, `07_results`,
  `09_business`, `10_limitations`, `12_appendices`; slides `business` (2), `a_features` (6), `test_reg` (14),
  `test_clf` (15), `use_reg` (16), `use_clf` (17); `deck/project/deck.json` title v2.4.

## Rules (binding; as HS-02)
1. Write only inside `experiments/experiment_5/`; never commit `_DONOTCOMMIT/`; `git diff --cached --name-only` before
   every commit.
2. Content is final. Do not change wording or numbers. If you find an error, write it in your reply to Benson and fix
   it in the source first (`deliverables/report/*.md`, `deliverables/deck/project/slides/*.html`), never only in the
   doc or deck.
3. Every number comes from the register as `{{id}}`; fill with `pipeline_b/build_evidence_B.py fill <src> <dst>`.
4. Version labels move together to v2.4: review doc title, note and file name (the file name still reads v2.2), deck
   footers if any, export names, `deliverables/README.md`.
5. After the sync: `build_evidence_B.py build` and `check` on all sources; the deliverables audit
   (`deliverables/audit/README.md`) must be 9/9; `pytest pipeline_b/tests tests/test_guards.py`.
6. Records: B-CR-59 onwards in `CHANGELOG_B.md`, a row in `report/records/CHANGES.md`, a `WORKLOG.md` entry, the audit
   README "Last run", `deliverables/README.md`.
7. The report body ends on or before page 20 (`format_submission_docx.ps1` prints it). If it does not, move more
   detail to the appendix with a body summary and pointer (Benson's rule: move, keep the content). First candidates:
   §7.1 "Residuals" paragraph and figure to appendix E; §5.2 detail to appendix J; §6.1 fold rules to appendix A.
   Record each move.
8. Commit with `git commit -F <message file>` ending in the attribution lines; never force-push; never push to main or
   milestone-3.

## Steps
1. Optional, to keep your image bytes (machine difference, documented in B-CR-53): on Windows rerun
   `deliverables/business_case/make_business_case.py` (dashboard venv) and
   `deliverables/deck/renders/make_deck_renders.py`, then `build_evidence_B.py build`. CSV and JSON should come out
   byte-identical; record it. Without the rerun the committed Linux renders are pixel-identical to yours except the
   promise chart, with different PNG bytes.
2. Review doc (v2.3 rev 59): sync every changed section from the filled sources; rename to "Team 11 final report v2.4";
   pictures: figure 24 promise chart replaced (`F.BC.promise_compare`); new learning curves
   (`F.reg.learning_curves`, `F.clf.learning_curves`) in appendix H; `F.reg.by_state` and `F.clf.by_state` move from
   §7.1 and §7.2 to appendix E. Update `deliverables/audit/figure_map.json` and the Word picture list
   (copy `report/build/report_v2_3_figs.tsv` to `report_v2_4_figs.tsv`).
3. Deck artifact (v2.3 version 48): sync slides 2, 6, 14, 15, 16, 17 from the filled templates; slide 16's promise
   chart from `F.BC.promise_compare.deck`; title v2.4.
4. Refresh `deliverables/audit/inputs/` (new `report_export_revNN.md`, deck JSON and assets), run the audit to 9/9.
5. Word: `report/build/` README steps (`docx_fill.py`, `pair_fill.py`, `format_submission_docx.ps1`); check page 20.
6. Exports to `deliverables/exports/<date>/Team11_final_report_v2.4.docx` and `Team11_final_deck_v2.4.pptx`.
7. One visual check of each export (charts placed, tables readable, no "[image:" left, no `{{` left).
8. Reply in `spec/doc_outbox/reply_benson_<date>_v2.4_production.md`: commits, audit result, body page range,
   anything moved, anything you think is wrong. Set this file's Status to ANSWERED.

## Not yours
Benson merges your production into milestone-3 and main. Already done: decisions B-G-19 to B-G-28 Agreed,
literature rows 13 and 14 signed, hosted app checked.

## Saving tokens
Batch commands; read the newest WORKLOG entry and the last rows of records, not whole logs; read the doc with
`sinceRev`; no inline base64 exports; one visual check per round.
