# Report change record

One row per commit that changes the report sources (`NN_*.md`). The review doc
(https://claude.ai/artifact/Gp8qHXHdffLf3t78JcMWid) is refreshed in place from the filled sources after each
change, so its version history keeps every earlier revision; each refresh adds a dated revision note in the doc.
Plan: "Team 11 final report and deck plan v2" (https://claude.ai/artifact/GLWW2y5uMfHUd3Riewju1m).

| Date | Commit | Sections | What changed | Why |
| --- | --- | --- | --- | --- |
| 2026-10-28 | c9c693b | — | Change record and literature register started | Plan v2, decision "change record" |
| 2026-10-28 | 3702134 | all files | Renumbered to plan v2: 02 literature (new stub), 03 data, 04 EDA, 05 features (new stub), 06 modelling, 07 results, 08 deployment, 09 business, 10 limitations, 11 references, 12 appendices; headings follow | Plan v2 section order |
| 2026-10-28 | 3702134 | §1 | Rewritten: tasks table, prediction moments, why MAE and AP, success yardsticks against the dummy and the baseline, stakeholders | TA lessons 1, 8; Milestone 1 stakeholder and prediction-time points |
| 2026-10-28 | 3702134 | §3 | Rewritten: joins and one-to-many links, targets and label sensitivity, eligibility rules in words, leakage rules per prediction moment, missing values and outliers, encoding inside the folds, test period, population chain per task | TA lesson 2; Milestone 1 joins, label and leakage points |
| 2026-10-28 | (this commit) | §5 | New section: baseline pool, the improved pipeline's history features with definitions, windows and reasons, grounding, multicollinearity check from stored outputs (A's correlations and VIF, nested-route drops, full rank), selection by the 99% rule and its fold stability, stated honestly for the alert | Plan v2 §5; TA lesson 3; P-7, P-10, P-16 |
