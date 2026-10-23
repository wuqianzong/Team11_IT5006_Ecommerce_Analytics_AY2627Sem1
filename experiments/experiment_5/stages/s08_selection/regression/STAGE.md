---
node: s08_selection/regression
owner: TBD
reviewer: TBD
status: READY_FOR_REVIEW
depends_on:
  - s07_tuning/regression
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s08_selection / regression - Selection

Spec: `spec/pipeline_design.md` -> s08. Teacher/TA rows: `spec/sources.md` (search `S08`).
Blueprint: `spec/blueprints/s08_selection.md` (implement only when its status is AGREED).

**Gate question:** Was the recipe frozen before the test cohort was scored once?

## Purpose
Select the model on threshold-free scores against the dummy and simplest models; freeze the recipe; fit on development orders with labels available before the test cutoff; score the test cohort once.

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
| 8.1 | Finalists: 4 finalists refitted on the five s05 folds: dummy (s06 reference) 6.4946 ± 0.6889 days; linear/logistic (s06 reference) 5.4701 ± 0.6733 days; single tree (s06 reference) 5.4244 ± 0.7147 days; forest (s07 carried (plain s06)) 5.4434 ± 0.6826 days (validation mae, mean ± SE). | code a7329b2; acceptance commit (e5-A-frozen) | candidates.csv, counts.json, figures/finalists.csv, figures/finalists.json, figures/finalists.png, metrics_long.csv, predictions.csv.gz | IMPLEMENTED | 1 |
| 8.2 | Choose the model: One-SE recommendation: linear/logistic (best mean: single tree). Ladder basic to complex: linear/logistic kept over dummy (paired gain +1.0245 days, better in 5 of 5 folds); single tree not kept over linear/logistic (paired gain +0.0458 days, better in 3 of 5 folds); forest not kept over linear/logistic (paired gain +0.0267 days, better in 3 of 5 folds); ladder result linear/logistic. Grid edge of the recommendation: plain s06 model, not a grid configuration. | code a7329b2; acceptance commit (e5-A-frozen) | candidates.csv, counts.json, decision.json, figures/finalists.csv, figures/finalists.json, figures/finalists.png, ladder.csv, selected_spec.json, selection_review_pack.md | IMPLEMENTED | 1 |
| 8.5 | Freeze: Recipe frozen for reg.sel.log.linear: 14 numeric and 4 categorical features, estimator linear, calibration none; sha256 df4beee32d7b6bef5736e21e53aad6b1caea3233a066c222e46708aca38899d2. Written from development rows only; the test cohort is not loaded. | code a7329b2; acceptance commit (e5-A-frozen) | counts.json, decision.json, frozen_recipe.json, selection_review_pack.md | IMPLEMENTED | 2 |
| 8.6 | Final fit: not built; runs once, together with Pipeline B, after both are frozen (lead decision 2026-10-23; draft G-79) | — | — | MISSING (by design until the joint test run) | 2 |
| 8.7 | Test once: not built; runs once, together with Pipeline B, after both are frozen (lead decision 2026-10-23; draft G-79) | — | — | MISSING (by design until the joint test run) | 2 |
| 8.8 | Bundle: not built; runs once, together with Pipeline B, after both are frozen (lead decision 2026-10-23; draft G-79) | — | — | MISSING (by design until the joint test run) | 2 |

## Review rounds (append-only; each round has review/round_N/ and a section in the doc tab)
| Round | Commit | Run ID | Review pack | Outcome | Date |
| --- | --- | --- | --- | --- | --- |
| 1 | code a7329b2; acceptance commit (e5-A-frozen) | 20261021T050311Z | review/round_1/review_pack.md | lead review (G-78); gate part 8.1-8.2 only, 8.5-8.8 wait for the combined team review | 2026-10-21 |
| 2 | code a7329b2; acceptance commit (e5-A-frozen) | 20261023T082458Z | review/round_2/review_pack.md | combined team review of s06-s08 done (decisions in human_decisions.yaml s08, Henry and the experiment lead, 2026-10-23); 8.5 freeze built and run; stops before the test (A waits for B); accepted by the lead for 8.1-8.5, clean rerun 20261023T084947Z identical | 2026-10-23 |

## Accepted result (the only result the report and slides may cite)
- Accepted round: 2, for 8.1-8.5 (the freeze) - commit: the "s08 frozen" commit, tag `e5-A-frozen` (code a7329b2) - run ID: 20261023T084947Z (clean tree, dirty false; outputs identical to review/round_2) - approved by: experiment lead (Wu Qianzong) after the team's combined review of s06-s08 (G-78) - date: 2026-10-23
- Frozen recipe: frozen_recipe.json, sha256 df4beee32d7b6bef5736e21e53aad6b1caea3233a066c222e46708aca38899d2. 8.6-8.8 (final fit, single test, bundle) are not yet run: they run once, together with Pipeline B (lead decision 2026-10-23; draft G-79), and are accepted then.

## Deviations from blueprint
None.

## Open questions
