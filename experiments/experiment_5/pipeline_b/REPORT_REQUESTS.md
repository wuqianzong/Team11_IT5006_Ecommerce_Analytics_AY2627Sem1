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
