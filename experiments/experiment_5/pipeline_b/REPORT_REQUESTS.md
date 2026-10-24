# Requests for the final report (Pipeline B)

Team requests about what the final report must contain. Each row says where the citable evidence
will come from; numbers are taken only from runs listed as current in `EVIDENCE.md`, never from
this file or from exploratory checks.

| ID | Date | From | Request | Status | Citable evidence |
| --- | --- | --- | --- | --- | --- |
| R-01 | 2026-10-24 | Henry (B6 › regression, B6.7) | Appendix: explain "full rank" and why fold 5 has more columns than fold 1, as evidence that feature columns are linearly independent. | Verified (see note 1); to write in the appendix | `stages/b06/<task>/outputs/design_matrix_by_fold.csv` (rank, columns, condition number per fold); category levels per training fold from `stages/b02/<task>/outputs/records_B.csv.gz` with `stages/b05/<task>/outputs/folds_B.csv` |
| R-02 | 2026-10-24 | Henry (B6 › regression, B6.2) | B summary: when comparing A and B, show each population's mean and SE, and test whether B's smaller SE comes from the outlier cap and the seven-state scope. | Exploratory check done (note 2); citable table to be produced by B8 (`se_decomposition.csv`, B8 blueprint method 3) | `stages/b08/<task>/outputs/se_decomposition.csv` (after B8 runs) |

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
