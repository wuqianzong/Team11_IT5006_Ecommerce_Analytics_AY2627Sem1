# Documentation gaps to close after the pipeline runs (A and B)

Recorded 2026-10-24 at the experiment lead's request. Decision: finish the pipeline first (B8 gate →
freeze → joint test run → B9/B10), then close these gaps in one pass, before the report and slides
(slides lock 2026-11-04, report 2026-11-08). Almost everything below uses outputs that already exist;
no stage needs a rerun unless noted. Numbers are taken only from runs current in `EVIDENCE.md`
(B) or from A at tag `e5-A-frozen`.

Kept in pipeline_b/ because B never writes in A's folders; items marked A are doc-only changes to
A's review tabs, built from A's frozen outputs.

## 1. Charts and tables in the review tabs

| ID | Pipeline | Gap | Source (already exists?) | Effort |
| --- | --- | --- | --- | --- |
| D-01 | B | No charts in any B tab. 16 PNGs exist: B6 family ladder, residual / classification diagnostics, learning curves; B7 validation curves (3 per task); B8 finalists, calibration, threshold trade-off | yes, `stages/b06–b08/<task>/outputs/figures/` | embed in tabs |
| D-02 | B | B6 tab thinner than A's s06: missing per-fold paired gains, per-fold scores of each candidate, learning-curve table, design matrix per fold, imputation per fold, residual statistics | yes (`paired_differences.csv`, `metrics_long.csv`, `curves/learning_curves.csv`, `design_matrix_by_fold.csv`, `imputation_by_fold.csv`, `curves/residual_*`) | tables only |
| D-03 | B | No charts at all for B2, B4, B5 (A has partition diagram, ranking chart, EDA charts) | no: plots to make from B2/B4/B5 outputs (history coverage by quarter, lateness by route, feature ranking, fold sizes / partition diagram) | small plotting step |
| D-04 | A | s07 tabs show only the top 8 configurations, no per-fold scores, no "effect of each parameter", no grid-edge note (B7 now has all of these) | yes, `../stages/s07_tuning/<task>/outputs/grid_results.csv` | tables only |
| D-05 | A | s08 tabs: no per-fold finalist scores, no adoption-style alternatives, no best-threshold-per-cap table, no threshold results by fold, no full threshold-curve table (the chart is there) | mostly yes (`metrics_long.csv`, `curves/threshold_curve.csv`, `predictions.csv.gz`); by-cap and by-fold tables are derived from those files | tables only |
| D-06 | A | s06 tabs: per-fold scores of each candidate not tabled (paired per-fold gains are) | yes, `metrics_long.csv` | tables only |

## 2. Teacher-expectation gaps (project brief + Milestone 2 teacher note)

| ID | Pipeline | Requirement | Status in the tabs | Where it will be closed |
| --- | --- | --- | --- | --- |
| T-01 | B | Ground engineered features in the Phase 1 literature, with citations | B features have reasons (feature_dictionary_B.csv) but no citations | add a citation column / note (doc) |
| T-02 | A, B | "Use stratified splits for imbalanced classes" vs our time-ordered folds | the reason (temporal data, no random splits; prevalence shown per fold) is not written in any tab | one paragraph in s05/B5 tabs and the report |
| T-03 | A, B | Ensemble is optional; decision not to use it | not documented | one line in s01/B8 and the report |
| T-04 | B | Feature importance / interpretability (coefficients, odds ratios, permutation importance) linked to business | not yet | B9 (as A's 9.5) |
| T-05 | B | Error analysis, not aggregate metrics only (by state, route, distance; precision/recall by state) | only overall residual diagnostics (B6.5) | B9 (as A's 9.3) |
| T-06 | A, B | Train–validate–test comparison | train and validation documented; test not run | joint test run + B-C13 fold-by-fold-and-test table |
| T-07 | B | Limitations discussion | only CR-054 §8 | B9 (as A's 9.8), incl. fold-1 deviation, different prediction moments, all-state history |
| T-08 | B | Actionable insights / business impact for the stakeholder | missed-dispatch rule only | B9 (as A's 9.7) |
| T-09 | B | Deployed app (Streamlit), README, repo layout, report, slides with app screenshots | not yet | B10 / s10 (B is the delivered model, G-79) |
| T-10 | A, B | Metric glossary (e.g. within_3d, _mean/_se) | answered in thread (R-03) | report |

## 3. Related records

- `REPORT_REQUESTS.md` (R-01 full-rank appendix, R-02 mean ± SE by population, R-03 metric glossary).
- `EVIDENCE.md` (which runs are citable).

## 4. Status (2026-10-24, filled at the experiment lead's request after B9)

| ID | Status | Where |
| --- | --- | --- |
| D-01 | DONE | B6, B7, B8 task sub-tabs: "Supplement for decisions and the report" (16 run figures embedded) |
| D-02 | DONE | B6 task sub-tabs, supplement: per-fold scores, paired gains, learning curves, residual quantiles, design matrix, imputation |
| D-03 | DONE | B2, B4, B5 task sub-tabs, supplement (doc\_support charts) |
| D-04 | DONE | A s07 task sub-tabs, supplement: full grid per family, per-fold scores, effect of each parameter, grid edge |
| D-05 | DONE | A s08 task sub-tabs, supplement: per-fold finalist scores; classification adds threshold by cap, by fold, full curve |
| D-06 | DONE | A s06 task sub-tabs, supplement: per-fold scores of every family |
| T-01 | PARTLY | Report notes tab §6: handover/dispatch features cite the G-76-checked sources; route and recent-speed features have no checked source (unmeasured mechanism until one is checked) |
| T-02, T-03, T-10 | DONE | Report notes tab §2, §3, §4 |
| T-04, T-05, T-07, T-08 | DONE | B9 Conclusion tab and sub-tabs |
| T-06 | DONE | T1 (B-C13 table) and B9.1 |
| T-09 | DEFERRED | B10, after the team confirms B9 |

New outputs: pipeline\_b/stages/doc\_support/<task>/outputs (e5b/doc\_support.py; runs 20261024T065707Z regression, 20261024T065723Z classification; uncommitted). They read A's frozen and B's accepted outputs only; A's sigmoid refit per fold reproduces A's s08 calibration AP exactly (check in the run). REPORT\_REQUESTS R-01, R-03, R-04: Report notes tab; R-05, R-06: B8 sub-tabs.
