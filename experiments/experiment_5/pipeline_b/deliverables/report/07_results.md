## 7 Results

On the same test orders Pipeline B beats Pipeline A in both tasks. Validation scores were used to choose the models, so they are optimistic selection scores; only the test, read once, is an unbiased estimate.

### 7.1 Delivery lead time

*Table 6. Delivery lead time, validation and test results.*

| | Training MAE | Validation MAE (selection) | Test MAE [95% interval] | Test RMSE | Test R² | Within 3 days (test) |
| --- | --- | --- | --- | --- | --- | --- |
| Pipeline B (delivered) | {{B9.reg.train_mae_B}} | {{B9.reg.val_mae_B}} | {{B9.reg.test_mae_B}} [{{B9.reg.test_mae_B_lo}}, {{B9.reg.test_mae_B_hi}}] | {{B9.reg.test_rmse_B}} | {{B9.reg.test_r2_B}} | {{B9.reg.test_within3_B}} |
| Pipeline A on the same test orders | | | {{B9.reg.test_mae_A_on_B}} | {{B9.reg.test_rmse_A_on_B}} | {{B9.reg.test_r2_A_on_B}} | {{B9.reg.test_within3_A_on_B}} |
| Dummy (median) on the same test orders | | | {{B9.reg.test_mae_dummy_B}} | | | |

Pipeline B's MAE minus Pipeline A's is {{B9.reg.mae_diff}} days on the same {{T1.reg.test_rows_B}} test orders (paired bootstrap interval {{B9.reg.mae_diff_lo}} to {{B9.reg.mae_diff_hi}}), so the gain is not an accident of the sample. RMSE, which weights large misses more, and R², the share of the variation in lead time that the model explains, point the same way. R² is low for both: much of the variation in delivery time is not visible at checkout. Pipeline A's R² on these orders is below zero, so it does worse than predicting the test period's average lead time, consistent with the faster test period (section 7.4).

*Figure: Lead time by validation fold and on the test, with time windows (F.reg.validation_and_test).*

### 7.1.1 Error analysis, lead time

A residual is the actual lead time minus the prediction: positive means the order arrived later than predicted.

*Table 7. Residuals on the test orders (days, actual minus predicted).*

| | Mean | Median | 5th / 95th percentile | Within 3 days | Over 3 days late | Over 6 days late | Over 3 days early |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pipeline B | {{RES.B.mean}} | {{RES.B.median}} | {{RES.B.p05}} / {{RES.B.p95}} | {{RES.B.within3}} | {{B9.reg.late_3d_B}} | {{B9.reg.late_6d_B}} | {{RES.B.early3}} |
| Pipeline A, same orders | {{RES.A.mean}} | {{RES.A.median}} | {{RES.A.p05}} / {{RES.A.p95}} | {{RES.A.within3}} | {{B9.reg.late_3d_A_on_B}} | {{RES.A.late6}} | {{RES.A.early3}} |

**Early or late.** On the test the errors lean early (mean {{B9.reg.resid_mean_test_B}} days): the typical order arrives sooner than predicted, and early misses of more than 3 days outnumber late ones. On validation they leaned late (mean {{B9.reg.resid_mean_val_B}} days, with a long right tail), because the test period was faster than the development period (section 7.4). The residuals are therefore neither centred on zero nor constant in spread, so a promise built on the prediction needs a buffer chosen for the current period (section 9). The late tail is what breaks a promise, and Pipeline B's is slightly heavier than Pipeline A's because it predicts shorter lead times (residual figure in appendix E).

**Where it errs.** Error grows with distance, from {{SL.reg.dist_near.mae_B}} days of MAE in the shortest distance band to {{SL.reg.dist_far.mae_B}} in the longest. By customer state it is largest in Bahia ({{SL.reg.state_BA.mae_B}}) and smallest in São Paulo ({{SL.reg.state_SP.mae_B}}); the worst judged route is São Paulo to Bahia ({{SL.reg.route_SPBA.mae_B}}). Single-item baskets err slightly more than baskets of three or more items ({{SL.reg.basket_1.mae_B}} against {{SL.reg.basket_3.mae_B}}). The one slice where Pipeline B is not better than Pipeline A is the first, partial test month, May 2018 ({{SL.reg.month_05.mae_B}} against {{SL.reg.month_05.mae_A}} on {{SL.reg.month_05.orders}} orders).

**Too small to judge.** Slices are judged only with at least 100 test orders. Every state, distance band, basket size and month qualifies, but {{SL.reg.routes_too_few}} routes do not; Pipeline B is better on {{B9.reg.routes_B_better}} of the {{B9.reg.routes_judged}} judged routes (Table K14; by state in appendix E).

### 7.2 Detractor alert

*Table 8. Detractor alert, validation and test results.*

| | Validation AP (selection) | Test AP [95% interval] | Test ROC-AUC | Test Brier |
| --- | --- | --- | --- | --- |
| Pipeline B (at handover) | {{B9.clf.val_ap_B}} | {{B9.clf.test_ap_B}} [{{B9.clf.test_ap_B_lo}}, {{B9.clf.test_ap_B_hi}}] | {{B9.clf.test_auc_B}} | {{B9.clf.test_brier_B}} |
| Pipeline A on the same test orders (at checkout) | | {{B9.clf.test_ap_A_on_B}} | {{B9.clf.test_auc_A_on_B}} | {{B9.clf.test_brier_A_on_B}} |

Pipeline B ranks detractors better by {{B9.clf.ap_diff}} AP (paired interval {{B9.clf.ap_diff_lo}} to {{B9.clf.ap_diff_hi}}) on {{T1.clf.test_rows_B}} test orders with {{T1.clf.test_detractors_B}} detractors, and is better on ROC-AUC and on the Brier score, which measures how well calibrated the probabilities are. The two pipelines predict at different moments, so part of the gain is the later moment itself.

*Figure: Detractor alert by validation fold and on the test (F.clf.validation_and_test); PR, ROC and reliability curves on the test (F.clf.test_curves).*

**At the threshold.** At the frozen 1/6, the unbiased result, Pipeline B sends {{B10.clf.B_1_6_test_alerts_day}} alerts a day on the test, with an F1 score of {{B9.clf.test_f1_B}} against Pipeline A's {{B9.clf.test_f1_A_on_B}} at its own 1/6 on the same orders (precision and recall in Table 9). After the test the business moved its operating threshold to 4/15 to cut false alarms ({{B10.clf.B_4_15_test_alerts_day}} alerts a day), a post-test change reported beside the frozen result. Orders outside the seven states are alerted by Pipeline A at its frozen 1/6 (section 9).

*Figure: Precision, recall and alerts per day against the threshold, marking 1/6 and 4/15 (F.clf.threshold_options).*

### 7.2.1 Error analysis, detractor alert

A true positive (TP) is an alerted detractor, a false positive (FP) an alert on a customer who was not a detractor, and a false negative (FN) a detractor the alert missed.

*Table 9. Confusion counts on Pipeline B's test orders ({{T1.clf.test_rows_B}} orders, {{T1.clf.test_detractors_B}} detractors).*

| Model and threshold | Alerts | TP | FP | FN | Precision | Recall | FP per TP |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pipeline B, frozen 1/6 | {{CM.B16.alerts}} | {{CM.B16.tp}} | {{CM.B16.fp}} | {{CM.B16.fn}} | {{B10.clf.B_1_6_test_precision}} | {{B10.clf.B_1_6_test_recall}} | {{CM.B16.fp_per_tp}} |
| Pipeline B, operating 4/15 (post-test) | {{CM.B415.alerts}} | {{CM.B415.tp}} | {{CM.B415.fp}} | {{CM.B415.fn}} | {{B10.clf.B_4_15_test_precision}} | {{B10.clf.B_4_15_test_recall}} | {{CM.B415.fp_per_tp}} |
| Pipeline A, frozen 1/6, same orders | {{CM.A16.alerts}} | {{CM.A16.tp}} | {{CM.A16.fp}} | {{CM.A16.fn}} | {{CM.A16.precision}} | {{CM.A16.recall}} | {{CM.A16.fp_per_tp}} |

**More false positives or false negatives.** At the frozen 1/6 Pipeline B makes more false positives than false negatives ({{CM.B16.fp}} against {{CM.B16.fn}}), as the cost weighting intends: a missed detractor counts as five false alerts. At 4/15 the balance flips: false positives fall to {{CM.B415.fp}} and false negatives rise to {{CM.B415.fn}}. Pipeline A catches more detractors on the same orders, but with {{CM.A16.fp_per_tp}} false alerts for each one.

**Which threshold for which constraint.** 1/6 minimises the five-to-one cost and suits a team that can work {{B10.clf.B_1_6_test_alerts_day}} alerts a day. 4/15 suits a team with capacity for about {{B10.clf.B_4_15_test_alerts_day}} a day that wants each contact to be worth making (precision {{B10.clf.B_4_15_test_precision}}). Missing fewer detractors would need a threshold below 1/6 and more capacity (figure above).

**Which orders it gets wrong.** Pipeline B misses {{BC.err.16_MD_share}} of the detractors at 1/6, and for most of them the delivery went to plan, so the reason for the review is not in the data; false alerts are often late handovers that the carrier made up (appendix E, Table E4).

**Too small to judge.** Slices are judged only with more than 100 test detractors: {{SL.clf.state_judged}} customer states and {{SL.clf.route_judged}} routes qualify, while {{SL.clf.state_too_few}} states and {{SL.clf.route_too_few}} routes are too small (Table E3). In every judged slice Pipeline B is more precise; Pipeline A, which alerts more orders, has the higher recall in most of them.

### 7.3 Where the gain comes from

Pipeline B changed three things at once: the scope, the features and, for the alert, the prediction moment. Scoring Pipeline A's frozen model on Pipeline B's own validation rows separates the scope effect from the rest (five-fold means, Table K15).

For lead time, Pipeline A's MAE falls from {{B8.reg.pop_A_on_A}} days on all states to {{B8.reg.pop_A_on_B}} on the seven-state rows, and Pipeline B reaches {{B8.reg.pop_B_on_B}}: most of the lower error comes from the narrower scope, the rest from the new features. For the alert, on the calibrated scale of Table 8, Pipeline A's AP barely moves ({{B8.clf.pop_A_on_A}} to {{B8.clf.pop_A_on_B}}) while Pipeline B reaches {{B8.clf.pop_B_on_B}}, so the gain comes from the history features and the later prediction moment. ROC-AUC and Brier by population are in appendix E.

*Figure: Where the gain comes from: scope vs features (F.reg.population).*

### 7.4 What the models rely on, and drift

Permutation importance is the test score the frozen model loses when a feature is shuffled. For lead time the seller's earlier dispatch days, the route and the distance rank highest, so the seller's own delay matters at least as much as the journey. For the alert, the number of sellers in the order and the route's recent delivery and transit times rank above this order's handover delay, so route conditions and basket complexity carry more signal about a bad review than the dispatch delay alone. These are associations in the frozen model, not causes.

*Figure: Permutation importance, lead time (F.reg.importance.report) and detractor alert (F.clf.importance.report).*

It differs from the selection ranking of section 5.3, as expected: selection scored one feature at a time, while importance is measured inside the fitted model, where correlated features share credit (appendix I).

*Figure: Coefficients, lead time (F.reg.coefficients.report); odds ratios, detractor alert (F.clf.coefficients.report).*

The test period was faster and happier than development, and the route history features shifted most (drift by fold in appendix A).
