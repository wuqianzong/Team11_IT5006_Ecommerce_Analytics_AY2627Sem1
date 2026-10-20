# Stage blueprints — index

A blueprint is the detailed, implementable solution for one stage of the frozen design
([`../pipeline_design.md`](../pipeline_design.md) v1.0). Implementation follows the
blueprint; the stage's `STAGE.md` records how it actually ran.

## How blueprints are maintained

- **Claude drafts and maintains them.** Each blueprint is written complete, with a
  recommended answer for every decision and its basis (tutorial, literature, Milestone 2
  evidence). Team input can be informal (doc comments, chat, review notes); each one is folded
  in and recorded in the [decision log](decision_log.md).
- **Status:** `NOT STARTED` → `DRAFT` → `DISCUSSING` → `AGREED`. Only an `AGREED` blueprint is
  implemented. After `AGREED`, changes need a CHANGELOG change request (README §9.2).
- **One home for every number.** Agreed values go to `spec/protocol.yaml`, or are marked
  "chosen on the folds in sNN". A blueprint never defines a number another file also defines.
- **Interfaces are checked.** Each stage's outputs must match the next stage's inputs (file
  names, columns, what has already been fitted). A change to one blueprint updates the
  blueprints it touches in the same revision.
- **Every revision is checked** against the frozen design, the leakage rules (README §8), the
  teacher rubric and the brief (`../sources.md`).
- Discussion copy: the Claude Doc "Milestone 3 pipeline stages" (one tab per stage when in
  discussion). This folder is the binding record.

## Index

| Stage | Blueprint | Status | Open items | Last change |
| --- | --- | --- | --- | --- |
| s01 Problem statement | [s01_problem.md](s01_problem.md) | AGREED | — | 2026-10-18: approved in team review (one-SE decision rule, eligible-order task wording) |
| s02 Data preprocessing | [s02_data.md](s02_data.md) | AGREED | — | 2026-10-17: approved in team walkthrough |
| s03 EDA | [s03_eda.md](s03_eda.md) | AGREED | — | 2026-10-17: approved in team walkthrough |
| s04 Features | [s04_features.md](s04_features.md) | AGREED | Cumulative threshold (95/99%) set after s03 output | 2026-10-17: approved in team walkthrough |
| s05 Partition | [s05_partition.md](s05_partition.md) | AGREED | — | 2026-10-17: approved in team walkthrough |
| s06 Training | [s06_training.md](s06_training.md) | AGREED | — | 2026-10-18: approved in team review (families only; log transforms fixed, G-36) |
| s07 Tuning | [s07_tuning.md](s07_tuning.md) | AGREED | — | 2026-10-18: approved in team review (grids G-37; one-SE selection) |
| s08 Selection | [s08_selection.md](s08_selection.md) | AGREED | — | 2026-10-18: approved in team review (human gates for model and threshold, G-39) |
| s09 Conclusion | [s09_conclusion.md](s09_conclusion.md) | AGREED | — | 2026-10-18: approved in team review (state slices with 100-detractor rule; EDA consistency check G-40) |
| s10 Release | [s10_release.md](s10_release.md) | AGREED | — | 2026-10-18: approved in team review (three-tab app, data scopes G-41) |

Template for new blueprints: [`_TEMPLATE.md`](_TEMPLATE.md).

## Implementation progress (README §9.1)

Build status per stage. Updated at each status change, together with the stage card and the
Pipeline v2 chart.

| Stage | Build status | Current round | Accepted round (commit) | Review tab |
| --- | --- | --- | --- | --- |
| s01 Problem statement | ACCEPTED | 2 | 2 (tag e5-s01-accepted) | Implementation reviews › s01 Problem |
| s02 Data preprocessing | ACCEPTED | 2 | 2 (tag e5-s02-accepted) | Implementation reviews › s02 Data |
| s03 EDA | ACCEPTED | 5 | regression 3, classification 5 (CR-043; tag e5-s03-accepted) | Implementation reviews › s03 EDA (sub-tabs: regression, classification) |
| s04 Features | IN REVIEW | 3 | — | Implementation reviews › s04 Features (sub-tabs: regression, classification) |
| s05 Partition | IN REVIEW | 2 | — | Implementation reviews › s05 Partition (sub-tabs: regression, classification); reviewed with s04 (G-74) |
| s06 Training | NOT STARTED | — | — | — |
| s07 Tuning | NOT STARTED | — | — | — |
| s08 Selection | NOT STARTED | — | — | — |
| s09 Conclusion | NOT STARTED | — | — | — |
| s10 Release | NOT STARTED | — | — | — |
