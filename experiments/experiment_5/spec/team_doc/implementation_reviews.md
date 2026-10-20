# Implementation reviews

Stages are built and reviewed one at a time, in pipeline order, s01 to s10. A stage starts only when every upstream stage is ACCEPTED. The technical foundation (shared code, run gate, guards, tests) is built first and is not reviewed as a stage; it changes whenever a stage review needs it, and every change is logged (G-60). The binding rules are in README §9.1 (CR-024, G-59). s01, s02 and s03 are ACCEPTED (s03 with the classification candidate screens, CR-037 to CR-039; s01–s03 corrected after the external audit, CR-042; data from 2017-01-01, CR-043); s04 and s05 were reviewed together and are ACCEPTED, s04 first (round 3 each, G-74); s06 is next.

## Progress

This table mirrors the build tags on the Pipeline v2 chart and the progress table in the blueprint index.

| Stage | Build status | Current round | Accepted round (commit) | Review tab |
| --- | --- | --- | --- | --- |
| s01 Problem statement | ACCEPTED | 2 | 2 (453896d, tag e5-s01-accepted) | s01 Problem |
| s02 Data preprocessing | ACCEPTED | 2 | 2 (tag e5-s02-accepted) | s02 Data |
| s03 EDA | ACCEPTED | 5 (classification, CR-043) | regression 3, classification 5 (tag e5-s03-accepted) | s03 EDA |
| s04 Features | ACCEPTED | 3 | 3 (tag e5-s04-accepted) | s04 Features |
| s05 Partition | ACCEPTED | 3 | 3 (tag e5-s05-accepted) | s05 Partition |
| s06 Training&#32; | NOT STARTED | — | — | — |
| s07 Tuning | NOT STARTED | — | — | — |
| s08 Selection | NOT STARTED | — | — | — |
| s09 Conclusion | NOT STARTED | — | — | — |
| s10 Release | NOT STARTED | — | — | — |

## How a stage review works

1. **Build and run.** Code follows the AGREED blueprint. Every change names the solution ID it serves (e.g. 2.9), and all outputs and process evidence are saved under the stage folder.
2. **Pack.** Code generates the review pack and a coverage table: every solution ID of the stage, marked IMPLEMENTED, DEVIATION or MISSING. A MISSING row blocks acceptance.
3. **Review tab.** A sub-tab of this tab is opened for the stage when it starts. Stages that run per task (s03–s09) also get one sub-tab per task for the evidence cards.
4. **Rounds.** Comments are answered in their threads; fixes come as a new round with a new run; nothing is committed or pushed during the rounds (G-64). Only rows whose evidence changed are reviewed again.
5. **Accept.** Every row Approved, no MISSING row, every check PASS, then the experiment lead approves. The stage card records the accepted round; the stage is committed once, tagged e5-sNN-accepted, together with a fresh export of every doc tab to spec/team\_doc/ for audit; the chart's build tag turns ACCEPTED, and the next stage unlocks.

## What a stage tab contains

**Two parts (since CR-042, 2026-10-20).** Every stage tab opens with **Part A — Final result**: the accepted values, tables and charts, generated from the accepted run; it is the only part the report, slides and later stages cite. **Part B — Review record** follows: the rounds as the team reviewed them, with their decisions and comment threads; its numbers are superseded. The list below describes Part B.

- **Status banner:** round, status, commit, run ID; after acceptance, the accepted round, approver and date.
- **Review layer** (one per round, in Part B; the result to cite is Part A):
  - the coverage table, with each ID linking to its evidence card;
  - decisions for the team (s03 and s08 human gates);
  - the evidence cards.
- **Evidence card per solution ID:**
  - approved solution (quoted);
  - what was done and its inputs;
  - process data;
  - results: tables and charts shown inline;
  - expectation vs observation;
  - reasoning and conclusion, each claim labelled observation, literature-supported hypothesis or unmeasured mechanism;
  - deviation;
  - checks;
  - file names with the round's run ID (the values themselves are shown in the card).
- **Round history** (append-only): per round, what changed and why, which rows were rerun, and every comment with its resolution. A card is copied here before it is replaced.

Tabs are never deleted. An accepted stage tab is frozen as the record, and later changes are added as dated sections. Each round is also saved in the repo under stages/sNN/\<task>/review/round\_N/.
