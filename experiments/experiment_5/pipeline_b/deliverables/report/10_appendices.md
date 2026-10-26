## Appendices

### A. Validation and test windows

Validation folds are selection scores (G-10); the test was read once.

{{table:APX.windows}}

### B. Metric glossary

| Metric | Meaning |
| --- | --- |
| MAE | Mean absolute error of the predicted lead time, in days (primary for regression; lower is better) |
| RMSE | Root mean squared error in days; penalises large misses more than MAE |
| R² | Share of the variance in lead time explained; can be negative on a shifted period |
| within 3 days | Share of orders whose prediction is within 3 days of the actual lead time |
| AP | Average precision, the area under the precision–recall curve (primary for classification) |
| ROC-AUC | Probability that a random detractor scores higher than a random non-detractor |
| Brier | Mean squared error of the predicted probability (calibration and sharpness) |
| precision, recall | At a threshold: share of alerts that are detractors; share of detractors alerted |
| one-SE rule | Keep the simplest model whose fold mean is within one standard error of the best |
| selection score | Fold scores used to choose models; optimistic. Only the test is unbiased |

### C. Full rank of the linear design matrix

Full rank means no column is an exact linear combination of the others, so coefficients are unique. Columns grow by fold because the one-hot step learns categories from each training fold.

Regression:

{{table:APX.reg.full_rank}}

Classification:

{{table:APX.clf.full_rank}}

### D. Selected features

Regression:

{{table:APX.reg.features}}

Classification:

{{table:APX.clf.features}}

### E. Train, validation and test tables

Regression:

{{table:APX.reg.train_val_test}}

Classification:

{{table:APX.clf.train_val_test}}

### F. Declaration of AI use

The team used Anthropic's Claude (Claude Code) as an assistant for code, pipeline documentation, this report's first draft and the slides. Every number is generated from the stored pipeline outputs through the number register; the team reviewed the methods, decisions and text, and the decisions recorded in the project's decision logs are the team's.
