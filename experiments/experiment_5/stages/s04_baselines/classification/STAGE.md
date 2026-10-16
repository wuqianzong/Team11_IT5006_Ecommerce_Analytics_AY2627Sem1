---
node: s04_baselines/classification
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s02_partitions/classification
  - s03_eda/classification
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s04_baselines / classification - Baselines

Spec: `spec/pipeline_design.md` -> STAGE4. Teacher/TA rows: `spec/sources.md` (search `S04`).

**Gate question:** Do simplest matched baselines exist on identical rows and folds?

## Purpose
Matched simplest baselines on the 9-feature core via e5lib.factory: prior DummyClassifier, unregularised LogisticRegression (penalty=None), documented single DecisionTreeClassifier.

## Planned outputs (`outputs/`)
- metrics_long.csv (train + validation per fold)
- predictions.csv.gz (OOF)
- decision.json (baseline reference per family)
- design_diagnostics.json (actual fitted matrix rank/condition)

## Gate criteria
- Identical rows and folds for all candidates
- Preprocessing inside folds
- Solver/convergence recorded
- Simplest baseline per family exists
<!-- END GENERATED -->

## Review summary (owner fills at gate; cite files, never type numbers from memory)
- What was done:
- Decision and rule applied (`outputs/decision.json`):
- Key evidence (file -> what it shows):
- Limitations:

## Gate check (reviewer)
- [ ] Every gate criterion above is met (note any exception)
- [ ] `run_pipeline.py run --node` reproduces all outputs from a clean tree
- [ ] Standard output shapes and `_manifest.json` present (README section 5.5)

## Deviations from spec
None.

## Open questions

## Sign-off
- Accepted by: - date: - commit: -
