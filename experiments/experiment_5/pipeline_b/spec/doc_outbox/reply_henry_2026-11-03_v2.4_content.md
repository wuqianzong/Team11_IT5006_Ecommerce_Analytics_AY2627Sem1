# To Henry: report and deck v2.4 content is in the sources (2026-11-03, B-CR-53)

Hi Henry, following HS-02, Benson's session changed content only; review doc, deck artifact and exports are yours.
Branch `e5/validation-fixes-henry` (commit after `acda7ca`). Details: `CHANGELOG_B.md` B-CR-53, decisions B-G-25 to
B-G-27, `deliverables/audit/runs/2026-11-03_solomon_v2.3_audit.md`, `WORKLOG.md`.

## What changed in the sources

| File | Change |
| --- | --- |
| `report/00_executive_summary.md` | "Use": 5% recent-weeks buffer (6.5 days; 15.0-day promise, 4.2% late against Olist's 18.6 days, 5.5%) |
| `report/01_problem.md` | Whole-window repeat share (2.9%) beside the same-month rate; problem statement cites Cui and Salari, not Fisher |
| `report/09_business.md` | Reuse of saved test labels stated; 5% candidate rule needing a rolling backtest; 1/6 as the cost threshold set before the test; fallback cost against no alert; the rule does not replace the fallback; "Proposed workflow"; no-alert cost |
| `report/10_limitations.md` | Buffer rule set on one window; next step is a rolling backtest |
| `report/12_appendices.md` | K16 rows; K18 adds the 6.5-day row; K18 note; K19 population and cost columns and note; K20 under the 6.5-day promise; new Table K21 (cost against no alert); appendix M |
| `deck/project/slides/business.html`, `use_reg.html`, `use_clf.html` | Retention card, literature, buffer rule cards, table labels with populations, workflow cards, cost line, notes |

## Production steps for you

1. Optional, to keep your image bytes: on Windows rerun `deliverables/business_case/make_business_case.py` (dashboard
   venv) and `deliverables/deck/renders/make_deck_renders.py`, then `build_evidence_B.py build`. CSV and JSON outputs
   should be byte-identical to this commit's; only the promise chart changes against v2.3. Without the rerun, the
   committed Linux renders are pixel-identical but every deck image's bytes differ.
2. Review doc: §1, executive summary, §9, §10 and appendix K (new K21) and M from the filled sources; replace figure 24.
   Deck: slides 2, 16 (new chart) and 17. Version labels to v2.4 (rule 8); the review doc's file name still says v2.2.
3. Refresh `audit/inputs`, audit 9/9, tests, then `format_submission_docx.ps1`: the body grew about 100 words; if it
   passes page 20, trim §9 first (the dispatch and transit paragraphs can merge).
4. Export v2.4 (.docx, .pptx).

Not for you: Benson approves the Proposed decisions, signs literature rows 13 and 14, and merges.

## Added in B-CR-54 (same day)

| File | Change |
| --- | --- |
| `report/00_executive_summary.md` | New "Why" paragraph (trigger and goal) before "Method" |
| `report/01_problem.md` | Problem statement opens with the business goal |
| `report/09_business.md` | Dispatch and transit merged (service recovery is now step 3); workflow lets the reason pick the action (Table K22) and hands priorities to seller management weekly |
| `report/12_appendices.md` | New Table K22 "From alert to action" after K21 |
| `deck/project/slides/business.html`, `use_clf.html`; `deck/project/deck.json` | Goal on slide 2; slide 17 case-file and weekly cards and notes; deck title v2.4 |

Body text is about 175 words longer than v2.3 by source count. If the Word copy passes page 20, cut first from §1's
"Why it matters" (the Cui sentence repeats §2) and from §9's opening paragraph.

## Added in B-CR-56 (TA's advice)

| File | Change |
| --- | --- |
| `report/05_features.md` | Reason for each Pipeline A feature group |
| `report/06_modelling.md` | New body Table 5 (training and validation by family), "Training results" paragraph, learning-curve figures `F.reg.learning_curves` and `F.clf.learning_curves` (new pictures: add to `figure_map.json` and the Word picture list) |
| `report/07_results.md` | Table 3 training MAE column; §7.2 "Which orders the alert gets wrong" |
| `report/12_appendices.md` | Table D3 gains the reason column; new Table K23 (error profile) |
| `deck/project/slides/a_features.html`, `test_reg.html`, `test_clf.html` | Feature reasons; training to validation MAE row; error-profile card; notes |
