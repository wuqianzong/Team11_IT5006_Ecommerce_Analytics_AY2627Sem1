---
node: s03_eda/classification
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s02_data/common
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s03_eda / classification - EDA

Spec: `spec/pipeline_design.md` -> s03. Teacher/TA rows: `spec/sources.md` (search `S03`).
Blueprint: `spec/blueprints/s03_eda.md` (implement only when its status is AGREED).

**Gate question:** Does every planned change follow from a pre-cutoff observation?

## Purpose
Question-driven EDA on orders before the test cutoff: target profiles; outcome trends over time; diagnostics of all 27 contract features against each target, importance ranking over the 24 eligible predictors (G-42) (scatter, Pearson and Spearman; violins and one-hot correlations; class-conditional KDE overlap and per-feature ROC-AUC; mutual information); one importance ranking per task for s04; missingness, outliers and collinearity among raw numeric features.

## Planned outputs (`outputs/`)
- figures/*.png + sidecar json
- target and per-feature diagnostic tables (csv)
- importance_ranking.csv (per task)
- eda_summary.json
- candidate_rationale.csv (finding, evidence, change it motivates, stage that tests it)

## Gate criteria
- No order on or after the test cutoff loaded
- Outcome trends shown, not volume only
- All 27 features diagnosed against the task's target
- Each proposed change linked to an observation
- Outputs written under the stage's outputs/, never artifacts/
- Stop: eda_review_pack.md presented; team decisions recorded in spec/human_decisions.yaml before s04 runs
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
