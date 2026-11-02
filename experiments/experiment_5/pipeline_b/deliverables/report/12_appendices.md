## Appendices

### A. Validation and test windows

Validation folds are selection scores; the test was read once.

*Table A1. Validation and test windows.*

{{table:APX.windows}}

*Table A2. Fold sizes, lead time.*

{{table:B5.reg.folds}}

*Table A3. Fold sizes and class support, detractor alert.*

{{table:B5.clf.folds}}

Drift is measured for each fold as the standardised mean difference of each numeric feature, and of the target, between the fold's validation rows and its training rows: the difference of the two means divided by the pooled standard deviation, the square root of the average of the two variances. The last column compares the test rows with the rows of the final fit in the same way. A positive value means the later rows have the higher mean.

*Figure: Drift by fold, lead time: standardised mean difference of each feature and of the target, validation rows against training rows for each fold, and test rows against the final fit's rows (F.reg.drift).*

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

**Derived features.** Almost every feature is computed from the nine raw tables rather than read from one column; a feature read straight from a raw column shows that column. Tables D3 and D4 give the formula of each, as stored with the feature pipelines. Order-level sums, counts and shares are taken over the order's items after the joins of section 3; history features use only other orders whose events were complete before this order's prediction week.

*Table D3. Pipeline A's features and how each is derived (both tasks; the missing-value indicators are added inside each fold).*

{{table:APX.features_derived_A}}

*Table D4. Pipeline B's new features and how each is derived.*

{{table:APX.features_derived_B}}

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

### G. Data model and population chain

Every model row is one order. Table G1 shows how each of the nine raw tables reaches it (section 3).

*Table G1. Data model: grain, key and join of each raw table.*

| Table | One row per | Key | How it reaches the order | Used for |
| --- | --- | --- | --- | --- |
| orders | order | order_id | the unit of every model row | purchase time and status; delivery and carrier dates only for the lead-time label and the handover moment |
| order_items | item of an order | order_id, order_item_id | aggregated to the order, then one to one | counts of items, products, sellers and categories; total price, freight, weight and volume; the primary item |
| order_payments | payment of an order | order_id, payment_sequential | aggregated to the order, then one to one | main payment type, largest number of instalments |
| order_reviews | review of an order | review_id, order_id | aggregated to the order, then one to one | the detractor label (lowest valid score; first review as a check); never a predictor |
| customers | customer of an order | customer_id | orders to customers, many to one | customer state and ZIP prefix; customer_unique_id links repeat customers |
| sellers | seller | seller_id | through the items, many to one | seller state and ZIP prefix (primary seller; every seller for distance) |
| products | product | product_id | through the items, many to one | category, weight, dimensions |
| product_category_name_translation | category | product_category_name | through the products, many to one | English category name |
| geolocation | observed point of a ZIP prefix | geolocation_zip_code_prefix | median latitude and longitude per prefix inside Brazil, joined to customers and sellers on the prefix | seller-to-customer distance |

Every removal from Pipeline B's population, by rule.

*Table G2. Exclusions by rule, lead time.*

{{table:B2.reg.exclusions}}

*Table G3. Exclusions by rule, detractor alert.*

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

### K. Supporting tables for sections 1–10

These tables were moved from the body to keep it within the page limit; the body quotes their key numbers. They are in section order.

*Table K1. Pipeline A's evidence and the changes it led to (section 1.1).*

| What Pipeline A's evidence showed | Change in Pipeline B | How it was checked before the test |
| --- | --- | --- |
| The strongest signal of a bad review, late delivery ({{A3.clf.detractor_rate_late}} detractors when late against {{A3.clf.detractor_rate_on_time}} on time), is unknown at checkout | The alert moves to carrier handover, where this order's dispatch delay is known; orders never handed over are flagged by a rule | Validation AP on the same rows (section 6.5) |
| Delivery speed varies with the route and changes over time (section 4), but checkout features carry no recent seller or route behaviour | Seller and route history features (section 5.1) | Ranking and selection (section 5.3); validation scores |
| Distant, thinly served states add noise that a single model fits poorly | Scope narrowed to the seven largest states with known distance; Pipeline A serves every other order | The scope effect is measured separately (section 7) |

*Table K2. Detractor results under the lowest-review and first-review labels, test orders (section 3).*

{{table:B9.clf.label_sensitivity}}

*Table K3. Population chain from Pipeline A's development orders to Pipeline B's rows (section 3).*

| Step | Lead time | Detractor alert |
| --- | --- | --- |
| Pipeline A development orders (eligible, before the test period) | {{B2.reg.dev_rows_A}} | {{B2.clf.dev_rows_A}} |
| Customer or seller outside the seven states | − {{B2.reg.removed_state}} | − {{B2.clf.removed_state}} |
| Distance unknown | − {{B2.reg.removed_distance}} | − {{B2.clf.removed_distance}} |
| Lead time above Pipeline B's cap | − {{B2.reg.removed_cap}} | — |
| Never handed over to the carrier | — | − {{B2.clf.removed_no_handover}} |
| Reviewed at or before handover | — | − {{B2.clf.removed_review_before_handover}} |
| First six weeks (history warm-up) | − {{B2.reg.removed_warmup}} | − {{B2.clf.removed_warmup}} |
| Pipeline B's development orders | {{B2.reg.dev_rows_B}} | {{B2.clf.dev_rows_B}} |
| Of these, with the label known before the test period (final fit) | {{T1.reg.fit_rows_B}} | {{T1.clf.fit_rows_B}} |
| Fold 5: training rows / validation rows | {{B5.reg.fold5_train_rows}} / {{B5.reg.fold5_validation_rows}} | {{B5.clf.fold5_train_rows}} / {{B5.clf.fold5_validation_rows}} |
| Test orders | {{T1.reg.test_rows_B}} | {{T1.clf.test_rows_B}} ({{T1.clf.test_detractors_B}} detractors) |

*Table K4. Exploratory findings and the decisions they led to (section 4).*

| What the data shows | Decision it led to | Section |
| --- | --- | --- |
| Right-skewed lead time with a long late tail | Log target and log day counts; keep the tail | 3 |
| Late delivery and bad reviews go together | Alert at carrier handover; lateness never a predictor | 1, 6 |
| Speed differs by route and state | Route feature and recent route speed; seven-state scope | 5, 6 |
| Volumes and outcomes change over time | Time-ordered folds and test period | 6 |
| Detractors are a minority | Average precision; cost-based threshold; class weight in the grid | 1, 6 |
| One identical predictor pair | Dropped before selection | 5 |

*Table K5. Pipeline B's new features (section 5.1).*

| Feature | Definition | Window | Reason |
| --- | --- | --- | --- |
| Route (seller state → customer state) | The pair of states the parcel travels between | — | Delivery time differs by origin and destination in ways distance alone misses |
| Seller prior late-handover rate | Share of the seller's earlier handovers made after their shipping limit | All complete weeks before the prediction week | A seller that dispatched late before is likely to do so again |
| Seller prior late-handover days | Mean days by which those earlier handovers missed the limit (0 if on time) | As above | The size of past delays, not only their frequency |
| Seller prior dispatch days | Mean days from purchase to handover over the seller's earlier orders | As above | Packing speed is part of every lead time |
| Route recent delivery days | Typical purchase-to-delivery time on the route | Weighted mean of the last three complete weeks (0.5, 0.3, 0.2) | Recent delivery conditions on the route |
| Route recent carrier transit days | Typical handover-to-delivery time on the route | As above | The carrier's part of the lead time, with the seller's delay removed |
| This order's handover lateness (alert only) | Whether, and by how many days, this order's handover missed its shipping limit | At handover | A late dispatch is new information about the coming delivery and review |
| This order's dispatch days (alert only) | Days from purchase to this order's handover | At handover | How long the customer has already waited |

*Table K6. Features removed by Pipeline B's reduction step, lead time (section 5.2).*

{{table:B4.reg.reduction}}

*Table K7. Pipeline A's predictor pairs above the correlation cut-off (section 5.2).*

{{table:A3.reg.collinear_pairs}}

*Table K8. Model ladder on the five folds, lead time, MAE in days (section 6.2).*

{{table:B6.reg.ladder}}

*Table K9. Model ladder on the five folds, detractor alert, AP (section 6.2).*

{{table:B6.clf.ladder}}

*Table K10. Plain against tuned models, lead time (section 6.3).*

{{table:B7.reg.plain_vs_tuned}}

*Table K11. Plain against tuned models, detractor alert (section 6.3).*

{{table:B7.clf.plain_vs_tuned}}

*Table K12. Adoption check on Pipeline B's folds, lead time, MAE in days (section 6.5).*

{{table:B8.reg.adoption}}

*Table K13. Adoption check on Pipeline B's folds, detractor alert, AP (section 6.5).*

{{table:B8.clf.adoption}}

*Table K14. Lead-time error by slice, test orders (section 7.1).*

{{table:B9.reg.slices_aggregate}}

*Table K15. Where the gain comes from: validation scores by population (section 7.3).*

| | Pipeline A, all states | Pipeline A, seven-state rows | Pipeline B, seven-state rows |
| --- | --- | --- | --- |
| Lead time, MAE (days) | {{B8.reg.pop_A_on_A}} | {{B8.reg.pop_A_on_B}} | {{B8.reg.pop_B_on_B}} |
| Detractor alert, AP | {{B8.clf.pop_A_on_A}} | {{B8.clf.pop_A_on_B}} | {{B8.clf.pop_B_on_B}} |

*Table K16. Recommended actions and their evidence (section 9).*

| Action | What the evidence shows | Label | Dashboard |
| --- | --- | --- | --- |
| Promise a range, not a date | On validation, a buffer of {{B12.reg.buffer_90}} days puts 90% of orders on time and {{B12.reg.buffer_95}} days 95%; on the faster test period those buffers leave {{B12.reg.buffer_90_test_late}} and {{B12.reg.buffer_95_test_late}} late. Choose the buffer on recent weeks and watch the late share by state. Overly optimistic promises carry costs after the sale (Cui et al., 2024) | Observation; literature-supported hypothesis for the cost of over-promising | Lead time, promise buffer |
| Alert customer service at handover | Pipeline B at 4/15 sends {{B10.clf.B_4_15_test_alerts_day}} alerts a day at precision {{B10.clf.B_4_15_test_precision}}; with the baseline's fallback at 1/6 the total is {{B10.clf.combined_test_alerts_day}} a day at precision {{B10.clf.combined_test_precision}} | Observation | Detractor risk, alert statistics |
| Flag missed dispatch with a rule | Orders whose shipping limit passes without handover are detractors with precision {{B9.clf.missed_dispatch_precision}}, and the rule catches {{B9.clf.missed_dispatch_share}} of all detractors on the test period, with no model | Observation | Detractor risk, missed dispatch |

*Table K17. Limitations and how each is handled (section 10).*

| Limit | What it means | How it is handled |
| --- | --- | --- |
| Seven-state scope | Pipeline B covers only orders whose customer and seller are in the seven states with a known distance | Pipeline A's frozen model serves every other order, and each prediction shows which model made it |
| Different prediction moments | Pipeline B's alert acts at handover, Pipeline A's at checkout, so part of the gain is the later moment | Stated wherever the two are compared (section 7) |
| Post-test threshold | The operating threshold 4/15 was chosen after the test was read | The frozen 1/6 result is reported as the unbiased one |
| Calibration override | The pre-set rule would have kept raw probabilities; sigmoid calibration was kept so both pipelines share one scale | Recorded as a deviation (section 6.4) |
| Screening on pooled rows | Features were ranked once on all development orders, so validation scores are slightly optimistic | Ranking stability by fold is reported (section 5.3); the test is unaffected |
| Unstable alert ranking | For the alert, feature ranks move a lot between folds, most in the early folds | The selected set is read as a reasonable choice, not a unique one |
| Unmeasured correlation | Correlation and VIF were not computed for the new history features; full rank rules out only exact dependence | Coefficients of related history features are read with care |
| Grid edge | The forest's best configuration sits on the edge of its grid | The grid was fixed in advance and not extended after the test; the plain model is kept by the selection rule |
| Fold 1 below minimum | Pipeline B's first fold has fewer training orders than the pre-set minimum | Kept so both pipelines are compared on identical periods |
| Drift | The test period was faster and happier than development, and the route history features shifted most | Validation and test are reported separately; the promise buffer should be set on recent weeks |
| Latest deliveries possibly missing | The slowest deliveries for the newest orders may not have arrived when the data was extracted | The test error may look slightly better than it will in operation |
| Reproducibility | The frozen models' predictions reproduce exactly on another machine; refitting gives slightly different numbers across machines | Reproduction compares predictions exactly and refitted scores within a tolerance |
| Associations, not causes | Features describe association with the outcome, not the effect of acting on them | Recommendations are labelled by evidence type (section 9) |

### L. Dashboard screenshots

Two views of the app, reading the stored test outputs.

*Screenshots 1–2. The detractor tab's alert statistics on the test period at the operating threshold 4/15 (S.05_alert_stats_test_4_15) and the ML deployment tab's list of alerted held-out orders (S.06_ml_deployment_alert_list).*

### M. Declaration of AI use

The team used Anthropic's Claude (Claude Code) throughout. It wrote and ran most of the pipeline code under the team's instructions, drafted the stage documentation, built the number register, and drafted this report and the slides. The team set the problem, the scope and every decision recorded in the project's decision logs, reviewed each stage before it was accepted, and checked the drafts. Every number in the report is filled from the stored pipeline outputs through the register, never typed; an audit script compares the report and slides against those outputs. Every reference was checked by the team against the publisher's record, and the claims made from each source were checked against that record (literature register).
