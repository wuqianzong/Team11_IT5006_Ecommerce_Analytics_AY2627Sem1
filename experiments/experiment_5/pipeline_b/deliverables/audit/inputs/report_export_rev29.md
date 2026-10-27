# Team 11 final report — delivery time and detractor alerts

Oct 26, 2026 · @Henry

Draft for team review. Every number is filled from the Pipeline B register (pipeline\_b/evidence/registry\_B.yaml); comment on any point.

## Executive summary

Olist's customer-service and operations teams need two answers for each order: how many days delivery will take, and whether the customer is likely to leave a bad review (1 or 2 stars). We built both predictions on the Olist data with two pipelines. Pipeline A is the baseline: all states, predicting at checkout. Pipeline B is the delivered model: A plus one change request, covering orders whose customer and seller are both in the seven largest states (SP, MG, RJ, PR, RS, BA, SC), adding seller and route delivery history, and predicting the review risk when the seller hands the parcel to the carrier.

Both pipelines were frozen before the test period was read, and the test was read once for both.

| Task | Pipeline B (delivered) | Pipeline A on the same orders | B minus A (95% interval) |
| --- | --- | --- | --- |
| Delivery lead time, MAE in days (lower is better) | 3.30 | 4.03 | -0.729 \[-0.754, -0.703\] |
| Share of orders predicted within 3 days | 57.6% | 44.3% |  |
| Detractor ranking, average precision (higher is better) | 0.197 | 0.178 | +0.0187 \[+0.0089, +0.0291\] |

B is better than A on the same test orders in both tasks, and both intervals exclude zero. Orders outside B's seven states are served by A's frozen model. For the alert team, B runs at an operating threshold of 4/15, chosen after the test to cut false alarms: about 5.6 alerts a day on the test period, with precision 0.346. The frozen threshold of 1/6 remains the unbiased test result (section 5).

Recommendations: show delivery promises as a range around B's prediction rather than a single date; send detractor alerts at handover to customer service; flag orders whose shipping limit passes without a handover (section 7).

## 1 Problem definition and stakeholders

We frame one delivery-experience problem as two tasks (the brief's dual framing).

|  | Regression: delivery lead time | Classification: detractor alert |
| --- | --- | --- |
| Question | How many days from purchase to delivery? | Will the customer leave a 1–2 star review? |
| Target | Lead time in days (log scale in the model) | Detractor = lowest valid review score of the order is 1 or 2 |
| Prediction moment | At checkout (A and B) | A: at checkout; B: at carrier handover |
| Stakeholder and action | Fulfilment and customer service set the delivery promise shown to the customer | Customer service contacts at-risk customers before the review is written |
| Primary metric | MAE (days); also RMSE, R², share within 3 days | Average precision (PR-AUC); also ROC-AUC, Brier, precision and recall at the threshold |
| Error cost | Late promises hurt trust more than early ones; reported as residual buffers | Illustrative cost 5 per missed detractor, 1 per false alert |

**Why handover for classification.** Late delivery is the strongest driver of bad reviews and is unknown at checkout. At handover the seller's dispatch delay is known and there is still time to act. Customer service has no reason to act at checkout. B's alert therefore cannot fire before handover; orders not yet handed over get no score, and a separate rule flags orders whose shipping limit passes without a handover.

**Success criteria (fixed before the test).** A more complex model is kept only if it beats the simpler one by more than one standard error over the validation folds (one-SE rule). B is adopted for a task when its mean validation score beats A's frozen model on the same rows; both are then scored once on the test.

## 2 Dataset and preprocessing

**Data.** The Canvas copy of the Olist dataset: nine tables (orders, items, payments, reviews, customers, sellers, products, geolocation, category translation), joined into one row per order. Customer-level logic (test separation, repeat customers) uses `customer_unique_id`, never `customer_id`.

**Leakage control.** Every column was audited for the time it becomes known. Delivery dates and review dates are outcomes and never predictors. Olist's own estimated delivery date is not used anywhere in B (it comes from the algorithm our regression replaces). Carrier handover dates appear in two ways only: as past events of other orders (seller and route history, using complete weeks before the prediction week), and, for B's classifier, as this order's own handover facts, because B predicts at handover (the brief allows features known "at the moment it ships").

**Test period.** Each task's newest 20% of orders is the test cohort, held out before EDA and feature work; development customers who reappear in the test are removed. Anything learned from data (imputation, encoding, scaling, calibration) is fitted inside the training folds.

**B's population.** Starting from A's 76,925 regression development orders, B removes orders outside the seven states (13,777), orders without a distance (606), extreme lead times above mean + 8 SD of B's own rows (45), and the first six weeks used to warm up the history features (1,264). Classification also removes orders never handed over and orders reviewed before handover.

**B's new features** (all free of Olist's promise): the route (seller state → customer state); the seller's earlier late-handover rate, late days and dispatch days; the route's recent delivery days and carrier transit days (weighted mean of the last three complete weeks, with state fallbacks); and, for classification, this order's handover lateness and dispatch days.

## 3 Exploratory analysis highlights

EDA used development orders only (before each task's test cutoff), so it never saw test outcomes.

- **Lead time is right-skewed** with a long tail of very late orders: median 11.2 days, mean 13.4, 95th percentile 31.1, skewness 2.41. The regression models therefore predict log(1 + days), and day-count inputs are log-transformed.
- **Late delivery drives bad reviews.** The detractor rate is 57.2% for orders delivered after Olist's promised date against 9.5% for orders on time (description only: lateness is known only after delivery and is never a predictor). This is why B predicts the review risk at handover, when the seller's delay is known.
- **Delivery speed depends on the route.** Median lead time ranges from 7.8 days for customers in SP to 27.1 days in AM, and late handover varies by seller state, which motivated B's route feature and route history (figure: late handover by route).
- **The business changed over time.** Volumes, speed and detractor share move across 2017–2018, including the November 2017 Black Friday peak (7,284 orders against 4,478 in October), so all evaluation is time-ordered.
- **Imbalance.** Detractors are a minority (14.8% of development orders; test share 9.9% on B's rows), so accuracy is not used; we report average precision, precision and recall.

&#91;image: Late handover by route (B2)\]

*Figure 1. Late handover by route, seven-state routes, development period (doc support DS.1).*

The EDA figures above come from Pipeline A's s03 stage (development orders, all states), read from A's frozen outputs at tag e5-A-frozen (evidence 3.1–3.8).

## 4 Modelling approach

**Two pipelines, one change request.** Pipeline A replays the course workflow in ten steps (problem, data, EDA, features, partition, training, tuning, selection, conclusion, release). Pipeline B is A plus change request CR-054 and nothing else: B's population, prediction moment and new features; every other choice (folds, model families, grids, selection rule, metrics, calibration and threshold procedure) is inherited from A and reused through A's own code.

**Features.** Each task starts from A's predictor pool plus B's new candidates. Features are ranked on development rows (Spearman correlation with the log target for regression, mutual information for classification) and the top features reaching 99% of the cumulative share are kept. Day counts are log1p-transformed; numeric features are scaled and categories one-hot encoded (first level dropped for linear models). Every step is inside one scikit-learn pipeline fitted per training fold.

&#91;image: Feature ranking and the 99% rule\]

*Figure 2. Feature ranking and the 99% cumulative-share rule, regression (DS.2).*

**Validation.** Five chronological, customer-purged folds plus the held-out test period (figure: time-ordered folds). We do not use random or stratified splits because orders are dated and customers return: a random split would train on the future. Instead each fold's class support is checked against minimums set in advance.

&#91;image: Time-ordered folds and the test period\]

*Figure 3. Five time-ordered validation folds and the held-out test period (DS.3).*

**Model ladder (two families).** Dummy baseline → plain linear regression / unregularised logistic regression → single decision tree → random forest, then grid tuning of each family, all on the same folds. Class weight (none or balanced) is a grid option for the classifiers.

**Selection.** The one-SE rule keeps the simplest model within one standard error of the best fold mean. In both tasks the forest had the best mean but stayed within one SE, so the plain linear model (regression) and plain logistic model (classification) were selected. The classifier's probabilities are sigmoid-calibrated (as A, so A and B share one probability scale), and the alert threshold of 1/6 follows from the 5:1 cost.

**Ensembles.** The random forest is our ensemble (bagged trees). Stacking or voting were optional in the brief; within the course's limit on model families we did not add them, and the forest did not beat the simple models by more than one SE.

**Adoption of B.** On the same validation rows, B's selected model beat A's frozen model in both tasks, so B is the delivered model; both went to the single test read.

## 5 Results and evaluation

Validation scores were used to choose models, so they are optimistic ("selection scores"); only the test, read once, is unbiased.

### 5.1 Delivery lead time

|  | Validation MAE (selection) | Test MAE \[95% interval\] | Within 3 days (test) |
| --- | --- | --- | --- |
| B (delivered) | 5.02 | 3.30 \[3.24, 3.35\] | 57.6% |
| A on B's test orders |  | 4.03 | 44.3% |
| Dummy (median) on B's test orders |  | 4.38 |  |

B's MAE minus A's is -0.729 days on the same 15,422 test orders (paired bootstrap interval -0.754 to -0.703). B is better on 20 of the 20 routes with at least 100 test orders.

&#91;image: Lead time: validation folds and test\]

*Figure 4. Delivery lead time: validation folds (selection scores) and the test, A and B (B9.14).*

**Where the gain comes from.** On validation, A's frozen model scores MAE 5.470 on all states, 5.142 on B's seven-state rows, and B scores 5.025 on the same rows: most of the lower error comes from the narrower scope, the rest from B's features.

&#91;image: Where B's gain comes from\]

*Figure 5. Where B's gain comes from: scope vs features, validation MAE (DS.5).*

**Late tail.** 11.1% of B's test orders arrive more than 3 days after its prediction (9.3% for A on the same orders) and 4.7% more than 6 days after. B is closer on average but predicts shorter times, so a promise built on it needs a buffer (section 7).

&#91;image: Residuals on B's test rows\]

*Figure 6. Residuals on B's test rows, B vs A (B9.16).*

&#91;image: Lead-time error by customer state\]

*Figure 7. Lead-time error by customer state (B9.3).*

### 5.2 Detractor alert

|  | Validation AP (selection) | Test AP \[95% interval\] | Test ROC-AUC |
| --- | --- | --- | --- |
| B (delivered, at handover) | 0.248 | 0.197 \[0.181, 0.218\] | 0.636 |
| A on B's test orders (at checkout) |  | 0.178 |  |

B ranks detractors better than A by +0.0187 AP (interval +0.0089 to +0.0291) on 15,492 test orders with 1,541 detractors. Part of the gain is the later prediction moment.

&#91;image: Detractor alert: validation folds and test\]

*Figure 8. Detractor alert: validation folds (selection scores) and the test, A and B (B9.14).*

&#91;image: PR, ROC and reliability curves\]

*Figure 9. PR, ROC and reliability curves on B's test rows (T1.4).*

**At the threshold.** At the frozen 1/6 (the unbiased result), B sends 23.2 alerts a day on the test with precision 0.208 and recall 0.300. After the test the team moved B's operating threshold to 4/15 to cut false alarms (a post-test business change, reported beside the frozen result): 5.6 alerts a day, precision 0.346, recall 0.121.

&#91;image: Threshold options\]

*Figure 10. Precision, recall and alerts per day against the threshold (B9.10). The chart marks the frozen 1/6 and the operating 4/15 (B-G-07).*

&#91;image: Detractor alert by customer state\]

*Figure 11. Detractor alert precision and recall by customer state (B9.3).*

### 5.3 Interpretation and drift

B's coefficients (regression) and odds ratios (classification) are read per one standard deviation of each transformed feature; permutation importance on the test rows ranks the seller's earlier dispatch days, the route and the distance highest for lead time, and the number of sellers, the route's recent delivery days, the number of items and the route's recent transit days highest for the detractor alert. This ranking differs from the feature-selection ranking by design: selection scored one feature at a time on development data, importance measures the fitted model on the test period. The test period is faster and happier than development, and the route history features moved most; validation and test scores are therefore not on the same footing.

&#91;image: Permutation importance, regression\]

*Figure 12. Permutation importance, B regression (test rows) (B9.5).*

&#91;image: Permutation importance, classification\]

*Figure 13. Permutation importance, B classification (test rows) (B9.5).*

&#91;image: Regression coefficients\]

*Figure 14. B's regression coefficients (B9.5).*

&#91;image: Classification odds ratios\]

*Figure 15. B's classification odds ratios (B9.5).*

## 6 Model deployment and application

**Release package.** The two frozen models of each task (B, and A as fallback) are packaged with their schemas, training profiles and checksums. Reloaded from disk, they re-predict the saved test predictions exactly (largest difference 1e-14 for regression, 2e-16 for classification), from test rows rebuilt with every label column emptied.

**Serving rule.** A router sends each order to B when the customer and seller are both in the seven states and the distance is known, otherwise to A (15,570 and 3,396 classification test orders respectively). B's alert uses the operating threshold 4/15; A's fallback uses its frozen 1/6. Orders inside B's scope that are not yet handed over get no score.

**Input checks.** Unknown states, impossible distances, orders without items and missing instalments are rejected with a clear message; missing values (imputed) and unseen categories are accepted with a warning, and so is any numeric input more than 4 standard deviations from the training mean.

**Application.** A Streamlit app with three tabs: the business dashboard from Phase 1, delivery lead time and detractor risk. The model tabs read only stored outputs and score held-out historical orders, as the brief allows.

Placeholder: the live URL, usage instructions and screenshots will be added once the app is deployed.

## 7 Business recommendations and impact

Each recommendation is labelled as an observation (measured here), a literature-supported hypothesis or an unmeasured mechanism.

1. **Promise a range, not a date** (observation). B's prediction is within 6 days for 87.0% of test orders, and 4.7% arrive more than 6 days after it. Show customers B's prediction plus a buffer, and monitor late deliveries by state, where the error differs most.
2. **Alert customer service at handover** (observation). At 4/15, B sends about 5.6 alerts a day with precision 0.346, about 1.89 false alarms per true detractor. Orders outside the seven states, scored by A at 1/6, add about 14.9 a day at precision 0.133: in total about 20.5 a day. The team accepted these volumes. The 6 alerts a day asked for at the B9 review applies to B's alerts only; the combined volume is above it, so customer service needs capacity for both streams, and A's fallback alerts are the less precise share and the first to review if capacity is short.
3. **Flag missed dispatch** (observation). A simple rule, shipping limit passed without handover, flags orders with detractor precision 21.2% and catches 16.8% of all detractors on the test period. It needs no model.
4. **Work on slow sellers and routes**. Slow dispatch by sellers is a literature-supported hypothesis (late or slow delivery lowers ratings; Deshpande and Pendem 2023, Leite et al. 2024). The route and its recent speed are an unmeasured mechanism: no source was checked for them, so the link rests on operational reasoning only. Both are among the strongest predictors; the dashboard lists the top routes and categories by quarter with their observed outcomes.

Illustrative cost (5 per missed detractor, 1 per false alert): B at the frozen 1/6 costs 7,156 on the test against 7,705 with no alerts. Under the serving rule (B at 4/15 inside the seven states, A at 1/6 outside) the test cost is 9,211: 7,123 from B and 2,088 from A's fallback (3,115 at 1:1), with precision 0.192 and recall 0.198 over all scored orders. A's fallback has recall 0.528 on its own detractors but the lower precision above (post-test view of T1's saved predictions; the frozen 1/6 result stays the unbiased one).

## 8 Limitations and next steps

- **Scope.** B covers only orders whose customer and seller are in the seven states; other orders get A's baseline model.
- **Different prediction moments.** B's classifier acts at handover and A's at checkout, so part of B's gain is the later moment.
- **Post-test threshold.** 4/15 was chosen after reading the test; the frozen 1/6 result is the unbiased one.
- **Alert capacity.** The 6 alerts a day asked for at the B9 review applies to B only; with A's fallback at 1/6 the combined volume is higher (section 7), which the team accepted.
- **Calibration override.** The pre-set calibration rule kept raw probabilities for B's classifier; the team chose sigmoid calibration instead (decision B-G-05) so that A and B share one probability scale at the test. This is a recorded deviation from the rule.
- **Drift.** The test period is faster and happier than development; scores may move as the business changes.
- **Fold 1** has fewer training rows than the pre-set minimum for B; it was kept so A and B are compared on the same periods.
- **Reproducibility.** Predictions of the frozen models reproduce exactly on another machine; refitting the unregularised logistic model gives slightly different numbers across machines, so the reproduction check compares predictions, and refitted results within a tolerance.
- **No causal claims.** Features describe association, not the effect of an intervention.

&#91;image: Drift by fold, regression\]

*Figure 16. Drift between training and validation rows by fold, and final fit vs test, regression (B9.11).*

Next steps: deploy the app, monitor alert precision and late deliveries by state each month, and test the promise buffer and the handover alert with customer service.

## References and appendices

- Olist Brazilian E-Commerce Public Dataset (Kaggle); Canvas copy used.
- James, Witten, Hastie and Tibshirani (2023), *An Introduction to Statistical Learning with Applications in Python*, Springer.
- Müller and Guido (2021), *Introduction to Machine Learning with Python*, O'Reilly.
- Breiman (2001), Random forests, *Machine Learning* 45(1).
- He and Garcia (2009), Learning from imbalanced data, *IEEE TKDE* 21(9).
- Deshpande and Pendem (2023), *Manufacturing & Service Operations Management* 25(3).
- Leite et al. (2024), *RTS* 20(60).
- IT5006 lectures 3–8 and tutorials 5, 7 and 8.

Appendices A to F follow.

## Appendices

### A. Validation and test windows

Validation folds are selection scores (G-10); the test was read once.

| period | kind | start | end | festival\_days |
| --- | --- | --- | --- | --- |
| fold 1 | validation (selection score, G-10) | 2017-06-19 | 2017-09-27 |  |
| fold 2 | validation (selection score, G-10) | 2017-09-27 | 2017-12-03 | 2017-11-24 |
| fold 3 | validation (selection score, G-10) | 2017-12-03 | 2018-02-05 | 2017-12-25 |
| fold 4 | validation (selection score, G-10) | 2018-02-05 | 2018-04-01 |  |
| fold 5 | validation (selection score, G-10) | 2018-04-01 | 2018-05-24 |  |
| test | test (unbiased, read once) | 2018-05-27 | 2018-08-29 |  |

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

Full rank means no column is an exact linear combination of the others, so coefficients are unique. Columns grow by fold because the one-hot step learns categories from each training fold. The check matters for the linear and logistic models, which were selected; tree models do not need a full-rank design matrix, so the tree candidates' rank and condition number are not a quality measure for them.

Regression:

| fold | rows | encoded\_columns | columns | rank | full\_rank | condition\_number |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 7932 | 131 | 130 | 130 | True | 244.7 |
| 2 | 18077 | 139 | 138 | 138 | True | 285.1 |
| 3 | 26184 | 140 | 139 | 139 | True | 243.5 |
| 4 | 37647 | 141 | 140 | 140 | True | 385.8 |
| 5 | 47415 | 141 | 140 | 140 | True | 433.6 |

Classification:

| fold | rows | encoded\_columns | columns | rank | full\_rank | condition\_number |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 7592 | 135 | 134 | 134 | True | 910.1 |
| 2 | 17595 | 143 | 142 | 142 | True | 912.8 |
| 3 | 25529 | 144 | 143 | 143 | True | 834.5 |
| 4 | 37140 | 145 | 144 | 144 | True | 864.5 |
| 5 | 47237 | 145 | 144 | 144 | True | 934.2 |

### D. Selected features

Regression:

| feature | kind | transform | pool\_rank |
| --- | --- | --- | --- |
| route\_seller\_to\_customer\_state | categorical | categorical: one-hot (drop-first for linear/logistic, every level for trees) | 1 |
| route\_recent\_carrier\_transit\_days | numeric | log1p: day count (Henry) | 2 |
| route\_recent\_delivery\_days | numeric | log1p: day count (Henry) | 3 |
| distance\_km\_max | numeric | log1p because pre-cutoff skewness 1.26 > 1 (A's 4.2 rule on B rows) | 4 |
| interstate\_share | numeric | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) | 5 |
| total\_freight | numeric | log1p because pre-cutoff skewness 9.42 > 1 (A's 4.2 rule on B rows) | 7 |
| seller\_prior\_dispatch\_days | numeric | log1p: day count (Henry) | 8 |
| primary\_category | categorical | categorical: one-hot, never logged (A's 4.2 rule on B rows) | 9 |
| seller\_prior\_late\_handover\_rate | numeric | never logged: rate or flag, scaled only (Henry) | 10 |
| seller\_prior\_late\_handover\_days | numeric | log1p: day count (Henry) | 11 |
| freight\_ratio | numeric | never logged: team decision in the s01 review (G-62) (A's 4.2 rule on B rows) | 12 |
| total\_weight\_g | numeric | log1p because pre-cutoff skewness 6.94 > 1 (A's 4.2 rule on B rows) | 14 |
| total\_price | numeric | log1p because pre-cutoff skewness 11.03 > 1 (A's 4.2 rule on B rows) | 15 |
| primary\_payment\_type | categorical | categorical: one-hot, never logged (A's 4.2 rule on B rows) | 16 |
| total\_volume\_cm3 | numeric | log1p because pre-cutoff skewness 7.63 > 1 (A's 4.2 rule on B rows) | 17 |
| purchase\_dayofweek | numeric | never logged: numeric calendar position (G-22, G-47) (A's 4.2 rule on B rows) | 18 |
| n\_sellers | numeric | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) | 19 |
| purchase\_month | numeric | never logged: numeric calendar position (G-22, G-47) (A's 4.2 rule on B rows) | 20 |
| n\_products | numeric | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) | 21 |
| payment\_installments\_max | numeric | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) | 22 |
| n\_items | numeric | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) | 23 |

Classification:

| feature | kind | transform | pool\_rank |
| --- | --- | --- | --- |
| route\_recent\_carrier\_transit\_days | numeric | log1p: day count (Henry) | 1 |
| route\_recent\_delivery\_days | numeric | log1p: day count (Henry) | 2 |
| seller\_prior\_dispatch\_days | numeric | log1p: day count (Henry) | 3 |
| seller\_prior\_late\_handover\_days | numeric | log1p: day count (Henry) | 4 |
| seller\_prior\_review\_mean | numeric | never logged: 1-5 rating (G-70) (A's 4.2 rule on B rows) | 5 |
| order\_dispatch\_days | numeric | log1p: day count (Henry) | 6 |
| freight\_ratio | numeric | never logged: team decision in the s01 review (G-62) (A's 4.2 rule on B rows) | 7 |
| total\_freight | numeric | log1p because pre-cutoff skewness 9.45 > 1 (A's 4.2 rule on B rows) | 8 |
| total\_volume\_cm3 | numeric | log1p because pre-cutoff skewness 7.65 > 1 (A's 4.2 rule on B rows) | 9 |
| n\_items | numeric | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) | 10 |
| route\_seller\_to\_customer\_state | categorical | categorical: one-hot (drop-first for linear/logistic, every level for trees) | 11 |
| seller\_prior\_late\_handover\_rate | numeric | never logged: rate or flag, scaled only (Henry) | 12 |
| total\_price | numeric | log1p because pre-cutoff skewness 11.11 > 1 (A's 4.2 rule on B rows) | 13 |
| order\_handover\_late\_days | numeric | log1p: day count (Henry) | 14 |
| total\_weight\_g | numeric | log1p because pre-cutoff skewness 6.94 > 1 (A's 4.2 rule on B rows) | 15 |
| product\_description\_lenght | numeric | log1p because pre-cutoff skewness 2.06 > 1 (A's 4.2 rule on B rows) | 16 |
| n\_products | numeric | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) | 18 |
| n\_sellers | numeric | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) | 19 |
| purchase\_month | numeric | never logged: numeric calendar position (G-22, G-47) (A's 4.2 rule on B rows) | 20 |
| order\_handed\_over\_late | numeric | never logged: rate or flag, scaled only (Henry) | 21 |
| distance\_km\_max | numeric | log1p because pre-cutoff skewness 1.26 > 1 (A's 4.2 rule on B rows) | 22 |
| primary\_category | categorical | categorical: one-hot, never logged (A's 4.2 rule on B rows) | 23 |
| interstate\_share | numeric | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) | 24 |
| n\_categories | numeric | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) | 25 |
| payment\_installments\_max | numeric | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) | 26 |

### E. Train, validation and test tables

Regression:

| model | rows | metric | train\_mean | validation\_mean | validation\_se | test | test\_ci\_low | test\_ci\_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B frozen | B test rows | mae | 3.861 | 5.025 | 0.6115 | 3.299 | 3.245 | 3.353 |
| B frozen | B test rows | rmse | 6.044 | 7.837 | 1.108 | 4.775 | 4.593 | 4.951 |
| B frozen | B test rows | r2 | 0.2437 | 0.08733 | 0.05303 | 0.1849 | 0.1616 | 0.2074 |
| B frozen | B test rows | within\_3d | 0.5563 | 0.501 | 0.0269 | 0.5755 | 0.5676 | 0.5838 |
| A frozen | B test rows | mae |  | 5.142 | 0.6616 | 4.028 | 3.97 | 4.083 |
| A frozen | B test rows | rmse |  | 7.99 | 1.187 | 5.359 | 5.197 | 5.511 |
| A frozen | B test rows | r2 |  | 0.05744 | 0.06186 | -0.02651 | -0.06142 | 0.006686 |
| A frozen | B test rows | within\_3d |  | 0.4883 | 0.02646 | 0.4429 | 0.4352 | 0.451 |
| B plain | B test rows | mae | 3.861 | 5.025 | 0.6115 | 3.299 | 3.245 | 3.353 |
| B plain | B test rows | rmse | 6.044 | 7.837 | 1.108 | 4.775 | 4.593 | 4.951 |
| B plain | B test rows | r2 | 0.2437 | 0.08733 | 0.05303 | 0.1849 | 0.1616 | 0.2074 |
| B plain | B test rows | within\_3d | 0.5563 | 0.501 | 0.0269 | 0.5755 | 0.5676 | 0.5838 |
| B dummy | B test rows | mae | 4.794 | 5.969 | 0.7107 | 4.385 | 4.327 | 4.441 |
| B dummy | B test rows | rmse | 7.105 | 8.747 | 1.217 | 5.709 | 5.54 | 5.876 |
| B dummy | B test rows | r2 | -0.04354 | -0.1398 | 0.04139 | -0.1651 | -0.19 | -0.1428 |
| B dummy | B test rows | within\_3d | 0.4394 | 0.3752 | 0.02589 | 0.371 | 0.3636 | 0.3784 |
| A frozen | A test rows | mae | 4.286 | 5.47 | 0.6733 | 4.336 | 4.281 | 4.39 |
| A frozen | A test rows | rmse | 6.882 | 8.578 | 1.179 | 5.729 | 5.594 | 5.875 |
| A frozen | A test rows | r2 | 0.2382 | 0.09112 | 0.07289 | 0.03397 | 0.004485 | 0.05933 |
| A frozen | A test rows | within\_3d | 0.5132 | 0.4654 | 0.02563 | 0.4138 | 0.4066 | 0.4204 |
| A plain | A test rows | mae | 4.286 | 5.47 | 0.6733 | 4.336 | 4.281 | 4.39 |
| A plain | A test rows | rmse | 6.882 | 8.578 | 1.179 | 5.729 | 5.594 | 5.875 |
| A plain | A test rows | r2 | 0.2382 | 0.09112 | 0.07289 | 0.03397 | 0.004485 | 0.05933 |
| A plain | A test rows | within\_3d | 0.5132 | 0.4654 | 0.02563 | 0.4138 | 0.4066 | 0.4204 |
| A dummy | A test rows | mae | 5.312 | 6.495 | 0.6889 | 4.876 | 4.819 | 4.934 |
| A dummy | A test rows | rmse | 8.053 | 9.535 | 1.157 | 6.261 | 6.115 | 6.42 |
| A dummy | A test rows | r2 | -0.04316 | -0.1355 | 0.04145 | -0.154 | -0.1735 | -0.1361 |
| A dummy | A test rows | within\_3d | 0.4001 | 0.339 | 0.02291 | 0.3213 | 0.314 | 0.3283 |

Classification:

| model | rows | metric | validation\_mean | validation\_se | test | test\_ci\_low | test\_ci\_high | test\_detractors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B frozen | B test rows | ap | 0.2482 | 0.03126 | 0.1972 | 0.1808 | 0.2176 | 1541 |
| B frozen | B test rows | roc\_auc | 0.6372 | 0.01518 | 0.636 | 0.6201 | 0.6517 | 1541 |
| B frozen | B test rows | brier | 0.1146 | 0.0135 | 0.0867 | 0.08342 | 0.09018 | 1541 |
| B frozen | B test rows | precision |  |  | 0.2077 | 0.1905 | 0.2256 | 1541 |
| B frozen | B test rows | recall |  |  | 0.3005 | 0.2771 | 0.3243 | 1541 |
| B frozen | B test rows | f1 |  |  | 0.2456 | 0.2265 | 0.2642 | 1541 |
| B frozen | B test rows | alert\_rate |  |  | 0.1439 | 0.1384 | 0.1498 | 1541 |
| A frozen | B test rows | ap | 0.2302 | 0.03046 | 0.1785 | 0.1631 | 0.1974 | 1541 |
| A frozen | B test rows | roc\_auc | 0.6259 | 0.01193 | 0.604 | 0.5894 | 0.6203 | 1541 |
| A frozen | B test rows | brier | 0.1162 | 0.01349 | 0.08926 | 0.08616 | 0.09264 | 1541 |
| A frozen | B test rows | precision |  |  | 0.1583 | 0.1463 | 0.1713 | 1541 |
| A frozen | B test rows | recall |  |  | 0.3556 | 0.3327 | 0.3806 | 1541 |
| A frozen | B test rows | f1 |  |  | 0.2191 | 0.204 | 0.2354 | 1541 |
| A frozen | B test rows | alert\_rate |  |  | 0.2235 | 0.2166 | 0.2299 | 1541 |
| B plain | B test rows | ap | 0.2616 | 0.03494 | 0.1992 | 0.1828 | 0.2197 | 1541 |
| B plain | B test rows | roc\_auc | 0.6536 | 0.01502 | 0.6341 | 0.6184 | 0.6495 | 1541 |
| B plain | B test rows | brier | 0.1141 | 0.01359 | 0.08642 | 0.083 | 0.09004 | 1541 |
| B plain | B test rows | precision |  |  | 0.2258 | 0.2056 | 0.2456 | 1541 |
| B plain | B test rows | recall |  |  | 0.2544 | 0.2332 | 0.2763 | 1541 |
| B plain | B test rows | f1 |  |  | 0.2392 | 0.2193 | 0.2587 | 1541 |
| B plain | B test rows | alert\_rate |  |  | 0.1121 | 0.1073 | 0.117 | 1541 |
| B dummy | B test rows | ap | 0.138 | 0.01983 | 0.09947 | 0.09508 | 0.104 | 1541 |
| B dummy | B test rows | roc\_auc | 0.5 | 0 | 0.5 | 0.5 | 0.5 | 1541 |
| B dummy | B test rows | brier | 0.1197 | 0.01502 | 0.09093 | 0.08773 | 0.09422 | 1541 |
| B dummy | B test rows | precision |  |  | 0 | 0 | 0 | 1541 |
| B dummy | B test rows | recall |  |  | 0 | 0 | 0 | 1541 |
| B dummy | B test rows | f1 |  |  | 0 | 0 | 0 | 1541 |
| B dummy | B test rows | alert\_rate |  |  | 0 | 0 | 0 | 1541 |
| A frozen | A test rows | ap | 0.2317 | 0.02763 | 0.175 | 0.1611 | 0.1891 | 1968 |
| A frozen | A test rows | roc\_auc | 0.6143 | 0.01353 | 0.5952 | 0.5822 | 0.6086 | 1968 |
| A frozen | A test rows | brier | 0.1239 | 0.01344 | 0.09328 | 0.09038 | 0.09607 | 1968 |
| A frozen | A test rows | precision |  |  | 0.1526 | 0.1428 | 0.1621 | 1968 |
| A frozen | A test rows | recall |  |  | 0.3801 | 0.3601 | 0.4018 | 1968 |
| A frozen | A test rows | f1 |  |  | 0.2178 | 0.2047 | 0.2304 | 1968 |
| A frozen | A test rows | alert\_rate |  |  | 0.2584 | 0.2521 | 0.2641 | 1968 |
| A plain | A test rows | ap | 0.2435 | 0.03142 | 0.1775 | 0.1636 | 0.1919 | 1968 |
| A plain | A test rows | roc\_auc | 0.6213 | 0.01606 | 0.5995 | 0.5863 | 0.6127 | 1968 |
| A plain | A test rows | brier | 0.1243 | 0.01427 | 0.0935 | 0.09054 | 0.09629 | 1968 |
| A plain | A test rows | precision |  |  | 0.1507 | 0.1405 | 0.1598 | 1968 |
| A plain | A test rows | recall |  |  | 0.374 | 0.3541 | 0.3951 | 1968 |
| A plain | A test rows | f1 |  |  | 0.2148 | 0.2021 | 0.2264 | 1968 |
| A plain | A test rows | alert\_rate |  |  | 0.2576 | 0.2509 | 0.2635 | 1968 |
| A dummy | A test rows | ap | 0.1482 | 0.01977 | 0.1038 | 0.09955 | 0.1079 | 1968 |
| A dummy | A test rows | roc\_auc | 0.5 | 0 | 0.5 | 0.5 | 0.5 | 1968 |
| A dummy | A test rows | brier | 0.1269 | 0.01452 | 0.09484 | 0.09186 | 0.09774 | 1968 |
| A dummy | A test rows | precision |  |  | 0 | 0 | 0 | 1968 |
| A dummy | A test rows | recall |  |  | 0 | 0 | 0 | 1968 |
| A dummy | A test rows | f1 |  |  | 0 | 0 | 0 | 1968 |
| A dummy | A test rows | alert\_rate |  |  | 0 | 0 | 0 | 1968 |

### F. Declaration of AI use

The team used Anthropic's Claude (Claude Code) as an assistant for code, pipeline documentation, this report's first draft and the slides. Every number is generated from the stored pipeline outputs through the number register; the team reviewed the methods, decisions and text, and the decisions recorded in the project's decision logs are the team's.
