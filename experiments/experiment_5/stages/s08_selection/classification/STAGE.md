---
node: s08_selection/classification
owner: TBD
reviewer: TBD
status: READY_FOR_REVIEW
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
| 8.1 | Finalists: 4 finalists refitted on the five s05 folds: dummy (s06 reference) 0.1482 ± 0.0198; linear/logistic (s06 reference) 0.2435 ± 0.0314; single tree (s06 reference) 0.2158 ± 0.0233; forest (s07 carried (plain s06)) 0.2544 ± 0.0267 (validation ap, mean ± SE). | code a7329b2; acceptance commit (e5-A-frozen) | candidates.csv, counts.json, figures/finalists.csv, figures/finalists.json, figures/finalists.png, metrics_long.csv, predictions.csv.gz | IMPLEMENTED | 1 |
| 8.2 | Choose the model: One-SE recommendation: linear/logistic (best mean: forest). Ladder basic to complex: linear/logistic kept over dummy (paired gain +0.0953, better in 5 of 5 folds); single tree not kept over linear/logistic (paired gain -0.0277, better in 0 of 5 folds); forest not kept over linear/logistic (paired gain +0.0109, better in 4 of 5 folds); ladder result linear/logistic. Grid edge of the recommendation: plain s06 model, not a grid configuration. | code a7329b2; acceptance commit (e5-A-frozen) | candidates.csv, counts.json, decision.json, figures/finalists.csv, figures/finalists.json, figures/finalists.png, ladder.csv, selected_spec.json, selection_review_pack.md | IMPLEMENTED | 1 |
| 8.3 | Calibration: Raw vs sigmoid (CalibratedClassifierCV, time-ordered inner splits) on the recommended model, per fold: mean Brier raw 0.12426 vs sigmoid 0.12391; mean AP raw 0.2435 vs sigmoid 0.2317 (one fold SE 0.0314). Kept: sigmoid. | code a7329b2; acceptance commit (e5-A-frozen) | calibration_folds.csv, curves/reliability_raw_vs_sigmoid.csv, decision.json, figures/calibration.csv, figures/calibration.json, figures/calibration.png, predictions.csv.gz, selected_spec.json, selection_review_pack.md | IMPLEMENTED | 1 |
| 8.4 | Threshold: Threshold candidates on the out-of-fold probabilities of the calibrated recommended model (62,023 validation rows, 345 days): 0.50 (t=0.5000): 0.3 alerts/day, precision 0.537, recall 0.005, cost 46,274; 1/6 (cost cutoff) (t=0.1667): 23.9 alerts/day, precision 0.252, recall 0.223, cost 42,255; empirical minimum of 5*FN + FP (t=0.1371): 53.5 alerts/day, precision 0.218, recall 0.432, cost 40,839; no alerts: cost 46,485. | code a7329b2; acceptance commit (e5-A-frozen) | curves/threshold_curve.csv, decision.json, figures/threshold_tradeoff.csv, figures/threshold_tradeoff.json, figures/threshold_tradeoff.png, selection_review_pack.md, threshold_table.csv | IMPLEMENTED | 1 |
| 8.5 | Freeze: Recipe frozen for clf.sel.log.logistic: 16 numeric and 3 categorical features, estimator logistic, calibration sigmoid, threshold 0.1667 on the sigmoid-calibrated probability (daily alert cap 25; out-of-fold 23.9 alerts/day); sha256 8de9d4f13159db2d77716df7070f745bea118390cdb3a624cede3ab19d9277d8. Written from development rows only; the test cohort is not loaded. | code a7329b2; acceptance commit (e5-A-frozen) | counts.json, decision.json, frozen_recipe.json, selection_review_pack.md | IMPLEMENTED | 2 |
| 8.6 | Final fit: not built; runs once, together with Pipeline B, after both are frozen (lead decision 2026-10-23; draft G-79) | — | — | MISSING (by design until the joint test run) | 2 |
| 8.7 | Test once: not built; runs once, together with Pipeline B, after both are frozen (lead decision 2026-10-23; draft G-79) | — | — | MISSING (by design until the joint test run) | 2 |
| 8.8 | Bundle: not built; runs once, together with Pipeline B, after both are frozen (lead decision 2026-10-23; draft G-79) | — | — | MISSING (by design until the joint test run) | 2 |

## Review rounds (append-only; each round has review/round_N/ and a section in the doc tab)
| Round | Commit | Run ID | Review pack | Outcome | Date |
| --- | --- | --- | --- | --- | --- |
| 1 | code a7329b2; acceptance commit (e5-A-frozen) | 20261021T050340Z | review/round_1/review_pack.md | lead review (G-78); gate part 8.1-8.4 only, 8.5-8.8 wait for the combined team review | 2026-10-21 |
| 2 | code a7329b2; acceptance commit (e5-A-frozen) | 20261023T082539Z | review/round_2/review_pack.md | combined team review of s06-s08 done (decisions in human_decisions.yaml s08, Henry and the experiment lead, 2026-10-23); 8.5 freeze built and run; stops before the test (A waits for B); accepted by the lead for 8.1-8.5, clean rerun 20261023T085014Z identical | 2026-10-23 |

## Accepted result (the only result the report and slides may cite)
- Accepted round: 2, for 8.1-8.5 (the freeze) - commit: the "s08 frozen" commit, tag `e5-A-frozen` (code a7329b2) - run ID: 20261023T085014Z (clean tree, dirty false; outputs identical to review/round_2) - approved by: experiment lead (Wu Qianzong) after the team's combined review of s06-s08 (G-78) - date: 2026-10-23
- Frozen recipe: frozen_recipe.json, sha256 8de9d4f13159db2d77716df7070f745bea118390cdb3a624cede3ab19d9277d8. 8.6-8.8 (final fit, single test, bundle) are not yet run: they run once, together with Pipeline B (lead decision 2026-10-23; draft G-79), and are accepted then.

## Deviations from blueprint
None.

## Open questions
