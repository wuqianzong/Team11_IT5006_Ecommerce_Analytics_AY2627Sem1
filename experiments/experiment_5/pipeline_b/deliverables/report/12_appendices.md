## Appendices

### A. Validation and test windows

Validation folds are selection scores; the test was read once.

{{table:APX.windows}}

Fold sizes, lead time:

{{table:B5.reg.folds}}

Fold sizes and class support, detractor alert:

{{table:B5.clf.folds}}

### B. Metric glossary

| Metric | Meaning |
| --- | --- |
| MAE | Mean absolute error of the predicted lead time, in days (primary for lead time; lower is better) |
| RMSE | Root mean squared error in days; penalises large misses more than MAE |
| R² | Share of the variance in lead time explained; can be negative on a shifted period |
| Within 3 days | Share of orders whose prediction is within 3 days of the actual lead time |
| AP | Average precision, the area under the precision–recall curve (primary for the alert) |
| ROC-AUC | Probability that a random detractor scores higher than a random non-detractor |
| Brier | Mean squared error of the predicted probability (calibration and sharpness) |
| Precision, recall | At a threshold: share of alerts that are detractors; share of detractors alerted |
| Paired gain | Per-fold difference between two models on the same rows; its mean and standard error describe the comparison |
| One-SE rule | Keep the simplest model whose fold mean is within one standard error of the best |
| Selection score | A fold score used to choose models; optimistic. Only the test is unbiased |

### C. Full rank of the linear design matrix

Full rank means no column is an exact linear combination of the others, so the coefficients are unique. The number of
columns grows by fold because the one-hot step learns its categories from each training fold. The condition number
shows how close the columns come to collinearity.

Lead time:

{{table:APX.reg.full_rank}}

Detractor alert:

{{table:APX.clf.full_rank}}

### D. Selected features

Lead time:

{{table:APX.reg.features}}

Detractor alert:

{{table:APX.clf.features}}

### E. Train, validation and test tables

Lead time:

{{table:APX.reg.train_val_test}}

Detractor alert:

{{table:APX.clf.train_val_test}}

Slices, detractor alert (judged only with more than 100 test detractors):

{{table:B9.clf.slices_aggregate}}

### F. Tuning grids and the grid edge

Every configuration of every family, with its mean and standard error over the five validation folds and the gap
between training and validation scores.

Lead time:

{{table:B7.reg.grid}}

Detractor alert:

{{table:B7.clf.grid}}

### G. Population chain detail

Every removal from the improved pipeline's population, by rule.

Lead time:

{{table:B2.reg.exclusions}}

Detractor alert:

{{table:B2.clf.exclusions}}

### H. Model candidates on the five folds

Lead time:

{{table:B6.reg.candidates}}

Detractor alert:

{{table:B6.clf.candidates}}

### I. Feature ranking by fold

The selection ranking repeated inside each training fold.

Lead time:

{{table:B12.reg.ranking_by_fold}}

Detractor alert:

{{table:B12.clf.ranking_by_fold}}

### J. Correlation and variance inflation

Variance inflation factor of each numeric predictor in the baseline pool, development orders.

Lead time:

{{table:A3.reg.vif}}

Detractor alert:

{{table:A3.clf.vif}}

Features dropped by the improved pipeline's reduction step, detractor alert:

{{table:B4.clf.reduction}}

### K. Declaration of AI use

The team used Anthropic's Claude (Claude Code) throughout. It wrote and ran most of the pipeline code under the
team's instructions, drafted the stage documentation, built the number register, and drafted this report and the
slides. The team set the problem, the scope and every decision recorded in the project's decision logs, reviewed each
stage before it was accepted, and checked the drafts. Every number in the report is filled from the stored pipeline
outputs through the register, never typed; an audit script compares the report and slides against those outputs.
Every reference was checked by the team against the publisher's record, and the claims made from each source were
checked against that record (literature register).
