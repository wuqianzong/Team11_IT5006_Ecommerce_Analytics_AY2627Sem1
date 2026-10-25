# Report notes — A and B (for the report and the team)

Added 2026-10-24 to close the documentation gaps in pipeline\_b/DOC\_GAPS.md (T-01, T-02, T-03, T-10) and the report requests R-01, R-03 and R-04. Every number comes from the file named beside it. Where a gap is closed in another tab, the map at the end says where.

## 1. Where B's advantage comes from (R-04)

B differs from A in scope (seven states, distance present, B's own lead-time cap), in features (seller and route history) and, for classification, in prediction time (carrier handover instead of checkout). Comparing A's frozen model on A's rows, A's model on B's rows and B's model on B's rows separates the scope effect from the rest (b08 population\_summary.csv, mean over 5 validation folds, raw scores as in the adoption rule):

| task | metric | A model, A rows | A model, B rows | B model, B rows | scope effect (A on B rows minus A on A rows) | B's features and prediction time (B minus A on B rows) |
| --- | --- | --- | --- | --- | --- | --- |
| regression | MAE (days) | 5.4701 | 5.1423 | 5.0247 | -0.3278 | -0.1176 |
| classification | AP | 0.2435 | 0.2419 | 0.2616 | -0.0016 | 0.0197 |

Reading: for regression, about three quarters of the lower MAE on B's rows comes from the narrower scope (A's model is already better on B's rows) and the rest from B's features; B's model is still better than A's on the same rows, and the joint test confirms that on unseen data (T1, B9.2). For classification, the scope barely changes A's AP, so B's gain comes from its features and later prediction time. The per-fold numbers and SE are in the B8 tabs (se\_decomposition.csv, R-02).

## 2. Why time-ordered folds and not stratified splits (T-02)

The tutorials use random or stratified splits. Olist orders are dated and customers return, so a random or stratified split would train on orders placed after the ones it predicts and could put one customer on both sides. Both pipelines therefore use a chronological test cohort and five chronological, customer-purged folds (spec/pipeline\_design.md, "Adaptation"; s05 and B5). Instead of stratifying, each fold's class support is checked against pre-registered minimums and reported. B's classification folds (b05 fold\_summary\_B.csv):

| fold | train\_rows | train\_positives | train\_prevalence | validation\_rows | validation\_positives | validation\_prevalence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 7,592 | 874 | 0.1151 | 10,324 | 1,014 | 0.0982 |
| 2 | 17,595 | 1,872 | 0.1064 | 10,342 | 1,443 | 0.1395 |
| 3 | 25,529 | 2,734 | 0.1071 | 10,450 | 1,497 | 0.1433 |
| 4 | 37,140 | 4,472 | 0.1204 | 10,453 | 2,173 | 0.2079 |
| 5 | 47,237 | 6,363 | 0.1347 | 8,646 | 873 | 0.1010 |

Prevalence differs by fold because the business changed over time (G-77); that is the reason for time-ordered evaluation, not a defect of the split.

## 3. No ensemble beyond the random forest (T-03)

The brief lists ensembles as optional. Both pipelines include one ensemble, the random forest (bagged trees), in the model ladder; under the agreed one-SE rule (G-33) the simpler linear/logistic model was kept in every task, and the team chose the simple models at the B8 gate. Stacking or boosting was not added: it would add a more complex model family, which the course instructions for this project rule out, and the forest result already shows that more flexibility did not beat the simple model by more than one SE.

## 4. Metric glossary (T-10, R-03)

Definitions from e5lib/metrics.py; the same code scores A and B.

| Metric | Meaning |
| --- | --- |
| MAE | mean absolute error of the predicted lead time, in days (lower is better; primary for regression) |
| RMSE | root mean squared error, in days; penalises large misses more than MAE |
| R² | share of the variance in lead time explained; can be negative on a shifted period |
| within\_3d | share of orders whose prediction is within 3 days of the actual lead time |
| AP | average precision: area under the precision-recall curve (higher is better; primary for classification) |
| ROC-AUC | probability that a random detractor gets a higher score than a random non-detractor |
| Brier | mean squared error of the predicted probability (lower is better; measures calibration and sharpness) |
| precision, recall, F1 | at a threshold: share of alerts that are detractors; share of detractors alerted; their harmonic mean |
| alert\_rate, alerts/day | share of orders alerted; alerts divided by the calendar days of the period |
| cost | illustrative: 5 per missed detractor + 1 per false alert (s01 1.5) |
| \_mean, \_se | mean over the 5 validation folds; standard error = standard deviation over folds / √5 |
| paired gain | per-fold difference between two models on the same rows; its mean and SE describe the comparison |
| one-SE rule | keep the simplest model whose mean is within one SE of the best (G-33) |
| selection score vs test | fold scores were used to choose models, so they are optimistic (G-10); only the test (read once, T1) is unbiased |

## 5. Full rank of the linear/logistic design matrix (R-01)

Full rank means no column is an exact linear combination of the others, so the coefficients are unique. The number of columns grows by fold because the one-hot step learns its categories from each training fold (later folds see more levels). The condition number shows how close to collinear the columns are (b06 design\_matrix\_by\_fold.csv):

| task | fold | rows | encoded\_columns | duplicates\_dropped | columns | rank | full\_rank | condition\_number |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| regression | 1 | 7,932 | 131 | missingindicator\_total\_volume\_cm3 | 130 | 130 | True | 244.7 |
| regression | 2 | 18,077 | 139 | missingindicator\_total\_volume\_cm3 | 138 | 138 | True | 285.1 |
| regression | 3 | 26,184 | 140 | missingindicator\_total\_volume\_cm3 | 139 | 139 | True | 243.5 |
| regression | 4 | 37,647 | 141 | missingindicator\_total\_volume\_cm3 | 140 | 140 | True | 385.8 |
| regression | 5 | 47,415 | 141 | missingindicator\_total\_volume\_cm3 | 140 | 140 | True | 433.6 |
| classification | 1 | 7,592 | 135 | missingindicator\_total\_weight\_g | 134 | 134 | True | 910.1 |
| classification | 2 | 17,595 | 143 | missingindicator\_total\_weight\_g | 142 | 142 | True | 912.8 |
| classification | 3 | 25,529 | 144 | missingindicator\_total\_weight\_g | 143 | 143 | True | 834.5 |
| classification | 4 | 37,140 | 145 | missingindicator\_total\_weight\_g | 144 | 144 | True | 864.5 |
| classification | 5 | 47,237 | 145 | missingindicator\_total\_weight\_g | 144 | 144 | True | 934.2 |

## 6. Literature for B's features (T-01)

Rule G-76: a feature is cited only to a source checked in Experiment 5 against the publisher record and abstract. Status of B's new features (names B-G-04):

| feature | status |
| --- | --- |
| order\_handed\_over\_late | literature-supported hypothesis (classification): late or slow delivery lowers ratings — Deshpande & Pendem 2023 (MSOM 25(3)); Leite et al. 2024 (RTS 20(60)), both checked in E5 (G-76) |
| order\_handover\_late\_days | literature-supported hypothesis (classification): late or slow delivery lowers ratings — Deshpande & Pendem 2023 (MSOM 25(3)); Leite et al. 2024 (RTS 20(60)), both checked in E5 (G-76) |
| order\_dispatch\_days | literature-supported hypothesis (classification): late or slow delivery lowers ratings — Deshpande & Pendem 2023 (MSOM 25(3)); Leite et al. 2024 (RTS 20(60)), both checked in E5 (G-76) |
| seller\_prior\_late\_handover\_rate | literature-supported hypothesis (classification): late or slow delivery lowers ratings — Deshpande & Pendem 2023 (MSOM 25(3)); Leite et al. 2024 (RTS 20(60)), both checked in E5 (G-76) |
| seller\_prior\_late\_handover\_days | literature-supported hypothesis (classification): late or slow delivery lowers ratings — Deshpande & Pendem 2023 (MSOM 25(3)); Leite et al. 2024 (RTS 20(60)), both checked in E5 (G-76) |
| seller\_prior\_dispatch\_days | literature-supported hypothesis (classification): late or slow delivery lowers ratings — Deshpande & Pendem 2023 (MSOM 25(3)); Leite et al. 2024 (RTS 20(60)), both checked in E5 (G-76) |
| route\_recent\_delivery\_days | unmeasured mechanism: no source checked in E5 yet (G-76); operational reasoning only (recent route speed predicts the next order's speed) |
| route\_recent\_carrier\_transit\_days | unmeasured mechanism: no source checked in E5 yet (G-76); operational reasoning only (recent route speed predicts the next order's speed) |
| route\_seller\_to\_customer\_state | unmeasured mechanism: no source checked in E5 yet (G-76); operational reasoning only (recent route speed predicts the next order's speed) |

The route and recent-speed features have no checked source yet. If the report should cite one, a source has to be checked under G-76 first; until then the report labels them as unmeasured mechanisms.

## 7. Where each teacher and team gap is covered now

| Gap | Where |
| --- | --- |
| D-01 to D-06 (charts and tables in the A and B tabs) | "Supplement for decisions and the report" section at the top of each B2–B8 and s06–s08 task sub-tab |
| R-05 population table and chart; R-06 ROC-AUC, Brier, confusion | B8 sub-tabs, supplement |
| T-04 interpretation, T-05 error analysis, T-07 limitations, T-08 business impact | B9 Conclusion tab and sub-tabs (B9.5, B9.3, conclusion, B9.7) |
| T-06 train–validation–test | T1 (B-C13 table) and B9.1 |
| T-01, T-02, T-03, T-10, R-01, R-03, R-04 | this tab |
| T-09 deployed app, README, report, slides | B10, after the team confirms B9 (lead, 2026-10-24) |

Doc-support outputs (charts, A's threshold-by-cap and by-fold tables): pipeline\_b/stages/doc\_support/\<task>/outputs, uncommitted until accepted.

## 8. Notes from Henry's B9 review (added 2026-10-25)

- **ratio\_per\_unit = e^coefficient** (regression). The model predicts log(1 + lead days), so a coefficient b multiplies (1 + predicted lead days) by e^b for one unit more of the transformed feature: one standard deviation after its transform for scaled numeric features (log1p for day counts), or that category level instead of the dropped reference level. For small b, e^b − 1 ≈ b (b = −0.05 is about 5% shorter).
- **odds\_ratio = e^coefficient** (classification). One unit more of the transformed feature multiplies the odds of being a detractor by e^b; above 1 raises the risk. For B the coefficient is the mean over the three calibration sub-models (min and max shown), so the odds ratio is approximate.
- **95% bootstrap interval.** Each resample draws the test orders with replacement (same number of orders) and recomputes the metric, 1,000 times (seed 42); the interval runs from the 2.5th to the 97.5th percentile of the 1,000 values (numpy percentile, interpolating between neighbours). For B minus A, both models are scored on the same resampled orders in each draw (paired), which is why those intervals are narrower than the single-model ones.
- **Label sensitivity (B9.6).** is\_detractor = 1 when the lowest valid review score of the order is 1 or 2; is\_detractor\_first uses the first review only. The same predictions are scored against both labels; the conclusion does not depend on the label definition.
- **Payment type (B9.12).** It measures payment-clearance delay (boleto must clear before approval), not delivery quality.
- **Coefficients vs operational ranking.** Coefficients are conditional associations from one frozen fit; rare levels are unstable. Business rankings of routes and categories use observed outcomes over a window with a minimum volume, with the coefficient as a second column (dashboard, B10).
