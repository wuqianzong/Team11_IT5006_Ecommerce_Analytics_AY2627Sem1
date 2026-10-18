---
node: s08_selection/classification
owner: TBD
reviewer: TBD
status: TODO
depends_on:
  - s07_tuning/classification
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s08_selection / classification - Selection

Spec: `spec/pipeline_design.md` -> s08. Teacher/TA rows: `spec/sources.md` (search `S08`).
Blueprint: `spec/blueprints/s08_selection.md` (implement only when its status is AGREED).

**Gate question:** Was the recipe frozen before the test cohort was scored once?

## Purpose
Select the model on threshold-free scores against the dummy and simplest models; calibration as a candidate component (raw by default, sigmoid variant scored on the same folds if reliability fails); threshold from the chosen probability recipe's out-of-fold predictions under the 5:1 cost; freeze; fit on development orders with labels available before the test cutoff; score the test cohort once.

## Planned outputs (`outputs/`)
- selected_spec.json
- threshold_table.csv (classification: no alerts, 0.50, theoretical 1/6, empirical optimum)
- frozen_recipe.json
- bundle/ (pipeline, threshold, schema, versions, training-ID digest, training_profile.json for drift, checksums)
- metrics_long.csv (phase = test) + predictions.csv.gz

## Gate criteria
- Team decisions for model choice and threshold recorded in spec/human_decisions.yaml (G-39)
- Model selected before the threshold
- Persisted probability recipe is the one the threshold was chosen on
- Final-fit training labels available before the test cutoff
- Recipe and threshold frozen before the test cohort is read
- Test cohort scored once
- Test metrics cover the agreed list (G-24); AP reported once as PR-AUC
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
