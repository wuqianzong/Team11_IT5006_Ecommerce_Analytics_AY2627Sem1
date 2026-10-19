# Implementation reviews

Stages are built and reviewed one at a time, in pipeline order, s01 to s10. A stage starts only when every upstream stage is ACCEPTED. The technical foundation (shared code, run gate, guards, tests) is built first and is not reviewed as a stage; it changes whenever a stage review needs it, and every change is logged (G-60). The binding rules are in README §9.1 (CR-024, G-59). s01 and s02 are ACCEPTED; s03 is next.

## Progress

This table mirrors the build tags on the Pipeline v2 chart and the progress table in the blueprint index.

| Stage | Build status | Current round | Accepted round (commit) | Review tab |
| --- | --- | --- | --- | --- |
| s01 Problem statement | ACCEPTED | 2 | 2 (453896d, tag e5-s01-accepted) | s01 Problem |
| s02 Data preprocessing | ACCEPTED | 2 | 2 (tag e5-s02-accepted) | s02 Data |
| s03 EDA | NOT STARTED | — | — | — |
| s04 Features | NOT STARTED | — | — | — |
| s05 Partition | NOT STARTED | — | — | — |
| s06 Training | NOT STARTED | — | — | — |
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

- **Status banner:** round, status, commit, run ID; after acceptance, the accepted round, approver and date.
- **Current layer** (latest round only; the only place to read the result):
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
