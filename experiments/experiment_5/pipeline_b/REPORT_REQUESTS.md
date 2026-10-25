# Requests for the final report (Pipeline B)

Team requests about what the final report must contain. Each row says where the citable evidence
will come from; numbers are taken only from runs listed as current in `EVIDENCE.md`, never from
this file or from exploratory checks.

| ID | Date | From | Request | Status | Citable evidence |
| --- | --- | --- | --- | --- | --- |
| R-01 | 2026-10-24 | Henry (B6 › regression, B6.7) | Appendix: explain "full rank" and why fold 5 has more columns than fold 1, as evidence that feature columns are linearly independent. | Verified (see note 1); to write in the appendix | `stages/b06/<task>/outputs/design_matrix_by_fold.csv` (rank, columns, condition number per fold); category levels per training fold from `stages/b02/<task>/outputs/records_B.csv.gz` with `stages/b05/<task>/outputs/folds_B.csv` |
| R-02 | 2026-10-24 | Henry (B6 › regression, B6.2) | B summary: when comparing A and B, show each population's mean and SE, and test whether B's smaller SE comes from the outlier cap and the seven-state scope. | Exploratory check done (note 2); citable table to be produced by B8 (`se_decomposition.csv`, B8 blueprint method 3) | `stages/b08/<task>/outputs/se_decomposition.csv` (after B8 runs) |
| R-03 | 2026-10-24 | Henry (B8 › regression, metrics table) | Report: explain within\_3d, within\_3d\_mean and within\_3d\_se (and the \_mean/\_se convention for every metric) for the team. | Answered in the thread; note added under the B8 table; to write in the report's metric glossary | `../e5lib/metrics.py` (definition: share of orders with abs(predicted - actual) <= 3 days); values from `stages/b08/regression/outputs/candidates.csv` |
| R-04 | 2026-10-24 | Henry (B8 stage tab, point 3) | Report: explain where B's advantage comes from (scope vs features and prediction time). | Agreed; to write | `stages/b08/<task>/outputs/population_summary.csv`, `se_decomposition.csv` |
| R-05 | 2026-10-24 | Henry (B8 › regression, population summary) | Report and slides: the mean ± SE by population table plus a comparison chart, for both tasks, to show what B's work contributes. | To do after the pipeline (charts: DOC_GAPS D-list) | `stages/b08/<task>/outputs/population_summary.csv` |
| R-06 | 2026-10-24 | Henry (B8 › classification, population summary) | B8 page, report and slides: ROC-AUC (and Brier) by population beside AP, and a confusion-matrix comparison (A at its threshold, B at its chosen threshold, on B's validation rows), with charts. | ROC-AUC and Brier: next B8 run; confusion matrices: B8 run after the b08 threshold decision; charts after the pipeline | B8 outputs (to be added) |
| R-07 | 2026-10-25 | Henry (B9 › regression, B9.4) | Drift in the report appendix; drift for every fold, training vs validation (A and B) | Done: B9.11 drift\_by\_fold (B9 round 2) | B9 outputs (to add: drift by fold, heatmap) |
| R-08 | 2026-10-25 | Henry (B9 sub-tabs) | Report notes: ratio\_per\_unit = e^coefficient; odds\_ratio = e^coefficient; bootstrap interval wording | Done: Report notes tab §8; report glossary | e5lib/metrics.py, B9 coefficients.csv |
| R-09 | 2026-10-25 | Henry (B9 › regression) | Business link of primary\_payment\_type | Done: B9.12 payment\_type.csv (B9 round 2) | raw orders (approval time) with records\_B (to add) |
| R-10 | 2026-10-25 | Henry (B9.7) | Business summary by route, for A and B | Done: B9.13 business\_by\_route.csv (B9 round 2) | B9 outputs (to add) |
| R-11 | 2026-10-25 | Henry (B blueprints, B9.2 / T1.6) | Conclusion shows validation folds and test together (table and chart) | Done: B9.14 validation\_and\_test.csv and chart (B9 round 2) | T1 fold\_and\_test\_table.csv, B9 train\_val\_test.csv |
| R-12 | 2026-10-25 | Henry (B blueprints, B8 / B-C13) | A's results outside the seven states, fold by fold and test (fallback for out-of-scope orders) | Done: B9.15 a\_fallback\_by\_scope.csv (B9 round 2); B-G-06 agreed | A s08 OOF, T1 predictions (to add) |
| R-13 | 2026-10-25 | Henry (B blueprints, point 7) | Operating threshold options with FP/TP 1 to 1.5 or below 1, cap 6/day; precision and recall vs threshold chart | Done: B9.10 threshold\_options (B9 round 2); operating threshold 4/15 (B-G-07) | b08 threshold\_curve\_sigmoid.csv, T1 predictions (to add as B9.10) |
| R-14 | 2026-10-25 | Henry (B9 › classification) | Dashboard: top 5 routes and categories by time window, charts plus full table; dashboard essentials | Design suggested in thread (observed outcomes by window, coefficient as second column); B10 | B10 |
| R-15 | 2026-10-25 | Henry (B9 stage, alert 1) | Note in the report: permutation importance (fitted model, test period) and B4's ranking (one feature at a time, development) differ by design | To write in the report | B9 ranking\_consistency.json |
| R-16 | 2026-10-25 | Henry (B9 stage, alert 2) | Residual distribution; share of orders more than 3 and more than 6 days after B's prediction, in the report and the dashboard (promise ranges) | Done: B9.16 residuals\_summary.csv, residuals\_histogram.csv; report and dashboard later | B9.16 |
| R-17 | 2026-10-25 | Henry (B9 stage, drift) | Every validation-and-test score shown with its time window, ideally in the chart labels | Done in B9.14 (validation\_and\_test\_windows.csv, chart labels); apply in the report | B9.14 |
| R-18 | 2026-10-25 | Henry (Report notes §1) | Report and deck: charts of key metrics and fold-by-fold validation and test in the body, detail tables in the appendix; highlight the engineered features and their impact | For the report and deck (after B10) | Report notes §1, B9.2, B9.5 |

## Notes

1. **R-01, verified 2026-10-24.** Full rank means no column of the linear/logistic design matrix is
   an exact linear combination of the others, so the coefficients are uniquely determined. The
   column count differs by fold because the one-hot step learns its categories from each training
   fold: fold 1 (the shortest training period) sees fewer category levels than fold 5. Full rank
   rules out exact collinearity only; how close columns are to collinear is shown by the
   condition number reported beside the rank in the same file. Write the exact level counts and
   condition numbers from the files above, not from this note.
2. **R-02, exploratory (not citable).** Using A's and B's stored out-of-fold predictions on the
   same validation rows, a quick decomposition suggested that the seven-state scope mainly lowers
   the mean error, the cap removes very few validation rows, and most of the SE difference for
   the linear model comes from B's features (largest in the worst fold); for the dummy model B's
   SE was not smaller. B8 produces this decomposition as an output so the report can cite it. With
   five folds, an SE itself is imprecise, so small SE differences should not be over-read.
