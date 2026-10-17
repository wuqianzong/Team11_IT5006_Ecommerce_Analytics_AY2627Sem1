# Decision log — Experiment 5 blueprints

Every decision across all stages: what was decided, who raised it, and why. Newest first.
The report's methodology and limitations sections can be written from this log.
Status: Proposed (in a draft) · Agreed · Superseded (link the replacing row).

| ID | Date | Stage | Decision | Raised by | Basis | Status |
| --- | --- | --- | --- | --- | --- | --- |
| G-17 | 2026-10-17 | s04 | `order_estimated_delivery_date` (known at checkout, not in the 27 baseline): recommended as an added candidate feature tested on the folds in s06 and as a regression business reference | Pipeline audit #11 | Milestone 2 misclassified it; leaving the correction unused was inconsistent | Proposed |
| G-16 | 2026-10-17 | s08 | Calibration is a candidate component: raw by default; a sigmoid variant (calibrator fitted inside training folds) is scored as a complete candidate if reliability fails; the threshold is chosen on the persisted probability recipe | Pipeline audit #9 | README §5.3 vs s08 were inconsistent | Agreed |
| G-15 | 2026-10-17 | s06 | Comparison order: (A) families on the core set with raw target/inputs; (B) within a family, feature sets, then input logs, then target transform and cap, one at a time | Pipeline audit #8 | One cause per change (rule 5) | Agreed |
| G-14 | 2026-10-17 | s01, s04, s05 | `protocol.yaml` has two layers: pre-registered (s01) and data-dependent (s04 sets, cap candidates; s05 boundaries, support threshold), each frozen at its gate before s06 | Pipeline audit #7 | s01 cannot fix data-dependent values | Agreed |
| G-13 | 2026-10-17 | s03, s04 | s03 measures collinearity on raw numeric features only; encoded design-matrix rank and condition number move to s04 (recipe) and s06 (fitted) | Pipeline audit #6 | Encoding is defined in s04 | Agreed |
| G-12 | 2026-10-17 | s05, s06 | DAG: s05 depends on s02 only; s06 depends on s04 and s05 | Pipeline audit #5 | Partition needs no feature recipe; avoids needless reruns | Agreed |
| G-11 | 2026-10-17 | s04 | The 27 → core reduction is a pre-registered label-free rule on pre-cutoff orders, declared as the one exception to fold-fitting and reported as a limitation | Pipeline audit #4 | Contradiction with design rule 2 | Agreed |
| G-10 | 2026-10-17 | all | CV scores are reported as selection scores only; the test cohorts (historical) are the only held-out estimate | Pipeline audit #3 | Selection reuses the folds; no unexamined data remains | Agreed |
| G-09 | 2026-10-17 | s05, s08 | Test-boundary customer purge (development orders of test customers removed) and final-fit label maturity (labels available before the test cutoff), both kept from Milestone 2; one test cohort per task | Pipeline audit #1, #2, #10 | `src/models/refinement_temporal.py` lines 11–16 and 37 | Agreed |
| G-08 | 2026-10-17 | s10 | Work directly on `milestone-3`; no `e5/*` branches | Team | Small team, changes contained in `experiments/experiment_5/` (CR-002) | Agreed |
| G-07 | 2026-10-17 | s10 | Report, slides and dashboard cite the reproduced outputs, built only after the reproduction check matches the release | Team review | Graders open the submitted repo; README §12 | Agreed |
| G-06 | 2026-10-17 | s08 | Select the model on threshold-free scores first, then calibration, then threshold from out-of-fold predictions, then fit once and test once | Team question | Tutorial 7 reference §6–9 | Agreed |
| G-05 | 2026-10-17 | s07 | Class weight (None vs balanced) is a tuning-grid option for the classifiers, not a training step | Team question | T7/T8 set `class_weight` in the model; He & Garcia 2009; van den Goorbergh et al. 2022 | Agreed |
| G-04 | 2026-10-17 | s06–s07 | Regularisation (Ridge alpha, logistic C) and tree/forest depth and leaf are tuned together in s07; s06 trains plain models | Team | Regularisation strength is a hyperparameter (T7–T8 GridSearchCV) | Agreed |
| G-03 | 2026-10-17 | s04, s06 | A target-cap step exists, but its value is not fixed; candidates (including no cap) are declared in `protocol.yaml` and chosen on the folds; scoring always on uncapped days | Team | Milestone 2 fixed 60 days outside tuning | Agreed |
| G-02 | 2026-10-17 | s04 | Start from the 27-feature baseline, reduce label-free to a core set, list candidate sets per model; each model's set is chosen on the folds in s06 | Team | One training cycle replaces Milestone 2's 9 → 11/12 second cycle | Agreed |
| G-01 | 2026-10-17 | all | One ten-stage textbook pass; chronological CV folds plus one test cohort (Milestone 2 terminal cohort, historical) | Team review | Tutorials 7–8; frozen design v1.0 (CR-001) | Agreed |
