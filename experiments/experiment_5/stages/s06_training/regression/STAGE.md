---
node: s06_training/regression
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s04_features/regression
  - s05_partition/regression
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s06_training / regression - Training

Spec: `spec/pipeline_design.md` -> s06. Teacher/TA rows: `spec/sources.md` (search `S06`).
Blueprint: `spec/blueprints/s06_training.md` (implement only when its status is AGREED).

**Gate question:** Do the models run basic to complex on identical folds, with each choice justified?

## Purpose
On the s05 folds: median dummy, plain LinearRegression, single decision tree, random forest, each one Pipeline from the s04 recipe; residuals and learning curves; feature set and log transforms fixed by s04 (always on, G-36).

## Planned outputs (`outputs/`)
- metrics_long.csv (train + validation per fold)
- predictions.csv.gz (out-of-fold)
- figures/ (residuals, learning curves)
- decision.json

## Gate criteria
- Identical rows and folds for every candidate
- Preprocessing fitted inside folds
- Simplest model of each family present
- Every model uses the s04 selected features with log transforms on (G-36); no feature or transform testing on the folds
- Each more complex family kept only under the s01 decision rule
<!-- END GENERATED -->

## Working log (README section 9.1; one row per solution ID, every code change names its ID)
| ID | What was built | Commit | Evidence (files, figures) | Coverage | Round |
| --- | --- | --- | --- | --- | --- |

## Review rounds (append-only; each round has review/round_N/ and a section in the doc tab)
| Round | Commit | Run ID | Review pack | Outcome | Date |
| --- | --- | --- | --- | --- | --- |

## Accepted result (the only result the report and slides may cite)
- Accepted round: - commit: - run ID: - approved by: - date:

## Deviations from blueprint
None.

## Open questions
