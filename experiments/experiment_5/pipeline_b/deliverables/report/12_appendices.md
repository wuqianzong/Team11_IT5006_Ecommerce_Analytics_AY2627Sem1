## Appendices

### A. Validation and test windows

Validation folds are selection scores; the test was read once.

*Table A1. Validation and test windows.*

{{table:APX.windows}}

*Table A2. Fold sizes, lead time.*

{{table:B5.reg.folds}}

*Table A3. Fold sizes and class support, detractor alert.*

{{table:B5.clf.folds}}

*Figure: Drift between development and test, by fold (F.reg.drift).*

### B. Metric glossary

*Table B1. Metric glossary.*

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

Full rank means no column is an exact linear combination of the others, so the coefficients are unique. The number of columns grows by fold because the one-hot step learns its categories from each training fold. The condition number shows how close the columns come to collinearity.

*Table C1. Rank and condition number of the linear design matrix by fold, lead time.*

{{table:APX.reg.full_rank}}

*Table C2. Rank and condition number of the linear design matrix by fold, detractor alert.*

{{table:APX.clf.full_rank}}

### D. Selected features

*Table D1. Selected features, lead time.*

{{table:APX.reg.features}}

*Table D2. Selected features, detractor alert.*

{{table:APX.clf.features}}

### E. Train, validation and test tables

*Table E1. Train, validation and test results, lead time.*

{{table:APX.reg.train_val_test}}

*Table E2. Train, validation and test results, detractor alert.*

{{table:APX.clf.train_val_test}}

*Table E3. Detractor alert by slice, judged only with more than 100 test detractors.*

{{table:B9.clf.slices_aggregate}}

*Figure: ROC-AUC and Brier by population, detractor alert (F.clf.auc_brier).*

### F. Tuning grids and the grid edge

Every configuration of every family, with its mean and standard error over the five validation folds and the gap between training and validation scores.

*Table F1. Tuning grid, lead time.*

{{table:B7.reg.grid}}

*Table F2. Tuning grid, detractor alert.*

{{table:B7.clf.grid}}

### G. Population chain detail

Every removal from Pipeline B's population, by rule.

*Table G1. Exclusions by rule, lead time.*

{{table:B2.reg.exclusions}}

*Table G2. Exclusions by rule, detractor alert.*

{{table:B2.clf.exclusions}}

### H. Model candidates on the five folds

*Table H1. Model candidates on the five folds, lead time.*

{{table:B6.reg.candidates}}

*Table H2. Model candidates on the five folds, detractor alert.*

{{table:B6.clf.candidates}}

### I. Feature ranking by fold

The selection ranking repeated inside each training fold.

*Table I1. Feature ranking by training fold, lead time.*

{{table:B12.reg.ranking_by_fold}}

*Table I2. Feature ranking by training fold, detractor alert.*

{{table:B12.clf.ranking_by_fold}}

*Figure: Ranking stability across the five folds, lead time (F.reg.ranking_stability) and detractor alert (F.clf.ranking_stability).*

### J. Correlation and variance inflation

Variance inflation factor of each numeric predictor in Pipeline A's pool, development orders.

*Table J1. Variance inflation factors of Pipeline A's pool, lead time.*

{{table:A3.reg.vif}}

*Table J2. Variance inflation factors of Pipeline A's pool, detractor alert.*

{{table:A3.clf.vif}}

*Table J3. Features dropped by Pipeline B's reduction step, detractor alert.*

{{table:B4.clf.reduction}}

*Figure: Pairwise correlations of Pipeline A's numeric predictors, development orders (F.A3.reg.correlation_heatmap).*

### K. Dashboard screenshots

Two views of the app, reading the stored test outputs.

*Screenshots 1–2. The detractor tab's alert statistics on the test period at the operating threshold 4/15 (S.05_alert_stats_test_4_15) and the ML deployment tab's list of alerted held-out orders (S.06_score_alert_list).*

### L. Declaration of AI use

The team used Anthropic's Claude (Claude Code) throughout. It wrote and ran most of the pipeline code under the team's instructions, drafted the stage documentation, built the number register, and drafted this report and the slides. The team set the problem, the scope and every decision recorded in the project's decision logs, reviewed each stage before it was accepted, and checked the drafts. Every number in the report is filled from the stored pipeline outputs through the register, never typed; an audit script compares the report and slides against those outputs. Every reference was checked by the team against the publisher's record, and the claims made from each source were checked against that record (literature register).
