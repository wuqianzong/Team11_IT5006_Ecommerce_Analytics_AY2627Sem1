---
node: s04_features/classification
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s03_eda/classification
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s04_features / classification - Features

Spec: `spec/pipeline_design.md` -> s04. Teacher/TA rows: `spec/sources.md` (search `S04`).
Blueprint: `spec/blueprints/s04_features.md` (implement only when its status is AGREED).

**Gate question:** Are features and recipes defined without fitting or using labels?

## Purpose
Define, without fitting: the 27-feature baseline (numeric calendar fields); log1p for continuous positive-scale features with pre-cutoff skewness > 1 (G-47) and for the regression target; the pre-registered label-free reduction to a core set; feature selection by the s03 importance ranking at the team's cumulative threshold (95% or 99%, fixed before any model is fitted); encoded design-matrix rank per recipe; rationale and citations; order_estimated_delivery_date never a feature (G-35); the pipeline recipe per model (impute, encode, scale).

## Planned outputs (`outputs/`)
- feature_dictionary.csv (formula, grain, availability, missingness, rationale, citation)
- selected_features.json (one set per task, all families)
- recipes.json (pipeline recipe per model)
- reduction_rationale.csv (flagged features, team decision, rationale)

## Gate criteria
- Reduction and importance selection use pre-cutoff orders only, never test
- Every collinearity drop is a recorded team decision with rationale (reduction_rationale.csv)
- Threshold and collinearity drops read from spec/human_decisions.yaml (team-decided after s03); s04 stops if missing
- No target cap (G-25)
- Every retained feature has a rationale
- order_estimated_delivery_date not used as a feature or reference (G-35)
- Nothing fitted on data
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
