## 7 Results

On the same test orders Pipeline B beats Pipeline A in both tasks. Validation scores were used to choose the models, so they are optimistic selection scores; only the test, read once, is an unbiased estimate.

### 7.1 Delivery lead time

*Table 3. Delivery lead time, validation and test results.*

| | Training MAE | Validation MAE (selection) | Test MAE [95% interval] | Test RMSE | Test R² | Within 3 days (test) |
| --- | --- | --- | --- | --- | --- | --- |
| Pipeline B (delivered) | {{B9.reg.train_mae_B}} | {{B9.reg.val_mae_B}} | {{B9.reg.test_mae_B}} [{{B9.reg.test_mae_B_lo}}, {{B9.reg.test_mae_B_hi}}] | {{B9.reg.test_rmse_B}} | {{B9.reg.test_r2_B}} | {{B9.reg.test_within3_B}} |
| Pipeline A on the same test orders | | | {{B9.reg.test_mae_A_on_B}} | {{B9.reg.test_rmse_A_on_B}} | {{B9.reg.test_r2_A_on_B}} | {{B9.reg.test_within3_A_on_B}} |
| Dummy (median) on the same test orders | | | {{B9.reg.test_mae_dummy_B}} | | | |

Pipeline B's MAE minus Pipeline A's is {{B9.reg.mae_diff}} days on the same {{T1.reg.test_rows_B}} test orders (paired bootstrap interval {{B9.reg.mae_diff_lo}} to {{B9.reg.mae_diff_hi}}), so the gain is not an accident of the sample. RMSE, which weights large misses more, and R², the share of the variation in lead time that the model explains, point the same way. R² is low for both: much of the variation in delivery time is not visible at checkout. Pipeline A's R² on these orders is below zero, so it does worse than predicting the test period's average lead time, consistent with the faster test period (section 7.4). The training error is lower than the validation error and higher than the test error because the three periods differ in speed, not because the model overfits (section 6.2).

*Figure: Lead time by validation fold and on the test, with time windows (F.reg.validation_and_test).*

**Residuals, read honestly.** On validation the errors lean late: the average order arrives {{B9.reg.resid_mean_val_B}} days after the prediction, with a long right tail. On the test they lean early: mean {{B9.reg.resid_mean_test_B}} days, median {{B9.reg.resid_median_B}}, because the test period was faster than the development period (section 7.4). The residuals are therefore neither centred on zero nor constant in spread, and a promise built on the prediction needs a buffer chosen for the current period (section 9). {{B9.reg.late_3d_B}} of test orders arrive more than 3 days after the prediction ({{B9.reg.late_3d_A_on_B}} for Pipeline A) and {{B9.reg.late_6d_B}} more than 6 days after.

*Figure: Residuals on the test orders, Pipeline B and Pipeline A (F.reg.residuals).*

**Where it errs.** Slices are judged only with at least 100 test orders. Pipeline B is better than Pipeline A in every judged customer state, distance band and basket size, on {{B9.reg.routes_B_better}} of the {{B9.reg.routes_judged}} routes with enough orders, and in most months (Table K14; by state in appendix E).

### 7.2 Detractor alert

*Table 4. Detractor alert, validation and test results.*

| | Validation AP (selection) | Test AP [95% interval] | Test ROC-AUC | Test Brier |
| --- | --- | --- | --- | --- |
| Pipeline B (at handover) | {{B9.clf.val_ap_B}} | {{B9.clf.test_ap_B}} [{{B9.clf.test_ap_B_lo}}, {{B9.clf.test_ap_B_hi}}] | {{B9.clf.test_auc_B}} | {{B9.clf.test_brier_B}} |
| Pipeline A on the same test orders (at checkout) | | {{B9.clf.test_ap_A_on_B}} | {{B9.clf.test_auc_A_on_B}} | {{B9.clf.test_brier_A_on_B}} |

Pipeline B ranks detractors better by {{B9.clf.ap_diff}} AP (paired interval {{B9.clf.ap_diff_lo}} to {{B9.clf.ap_diff_hi}}) on {{T1.clf.test_rows_B}} test orders with {{T1.clf.test_detractors_B}} detractors, and is better on ROC-AUC and on the Brier score, which measures how well calibrated the probabilities are. The two pipelines predict at different moments, so part of the gain is the later moment itself.

*Figure: Detractor alert by validation fold and on the test (F.clf.validation_and_test); PR, ROC and reliability curves on the test (F.clf.test_curves).*

**At the threshold.** At the frozen 1/6, the unbiased result, Pipeline B sends {{B10.clf.B_1_6_test_alerts_day}} alerts a day on the test with precision {{B10.clf.B_1_6_test_precision}} and recall {{B10.clf.B_1_6_test_recall}}, an F1 score of {{B9.clf.test_f1_B}}; Pipeline A at its own 1/6 on the same orders has precision {{B9.clf.test_precision_A_on_B}}, recall {{B9.clf.test_recall_A_on_B}} and F1 {{B9.clf.test_f1_A_on_B}}. After the test the business moved its operating threshold to 4/15 to cut false alarms, a post-test change reported beside the frozen result: {{B10.clf.B_4_15_test_alerts_day}} alerts a day, precision {{B10.clf.B_4_15_test_precision}}, recall {{B10.clf.B_4_15_test_recall}}. Orders outside the seven states are alerted by Pipeline A at its frozen 1/6 (section 9).

*Figure: Precision, recall and alerts per day against the threshold, marking 1/6 and 4/15 (F.clf.threshold_options).*

**Slices.** Precision and recall by customer state and route are judged only where the test has more than 100 detractors, which holds for few slices (appendix E). In every judged slice Pipeline B is more precise; Pipeline A, which alerts more orders, has the higher recall in most of them.

**Which orders the alert gets wrong** (appendix E, Table E4; stored test predictions, no refit). At the frozen 1/6, Pipeline B misses {{BC.err.16_MD_n}} detractors, {{BC.err.16_MD_share}} of all on its test orders; only {{BC.err.16_MD_late_delivery}} of them arrived after Olist's estimate, so for most the delivery went to plan and the reason for the review is not in the data. False alerts include many late handovers that still arrived on time ({{BC.err.16_FA_late_handover}} handed over late, {{BC.err.16_FA_late_delivery}} delivered late): the alert catches delivery-driven complaints.

### 7.3 Where the gain comes from

Pipeline B changed three things at once: the scope, the features and, for the alert, the prediction moment. Scoring Pipeline A's frozen model on Pipeline B's own validation rows separates the scope effect from the rest (five-fold means, Table K15).

For lead time, Pipeline A's MAE falls from {{B8.reg.pop_A_on_A}} days on all states to {{B8.reg.pop_A_on_B}} on the seven-state rows, and Pipeline B reaches {{B8.reg.pop_B_on_B}}: most of the lower error comes from the narrower scope, the rest from the new features. For the alert, on the calibrated scale of Table 4, Pipeline A's AP barely moves ({{B8.clf.pop_A_on_A}} to {{B8.clf.pop_A_on_B}}) while Pipeline B reaches {{B8.clf.pop_B_on_B}}, so the gain comes from the history features and the later prediction moment. ROC-AUC and Brier by population are in appendix E.

*Figure: Where the gain comes from: scope vs features (F.reg.population).*

### 7.4 What the models rely on, and drift

Permutation importance is the test score the frozen model loses when a feature is shuffled. For lead time the seller's earlier dispatch days, the route and the distance rank highest, so the seller's own delay matters at least as much as the journey. For the alert, the number of sellers in the order and the route's recent delivery and transit times rank above this order's handover delay, so route conditions and basket complexity carry more signal about a bad review than the dispatch delay alone. These are associations in the frozen model, not causes.

*Figure: Permutation importance, lead time (F.reg.importance.report) and detractor alert (F.clf.importance.report).*

This ranking differs from the selection ranking of section 5.3: Spearman correlation {{B9.reg.rank_spearman}} for lead time and {{B9.clf.rank_spearman}} for the alert, with {{B9.reg.rank_top10}} and {{B9.clf.rank_top10}} of the top ten features shared. This is expected: selection scored one feature at a time on development orders, while importance is measured inside the fitted model, where correlated features share credit.

*Figure: Coefficients, lead time (F.reg.coefficients.report); odds ratios, detractor alert (F.clf.coefficients.report).*

The test period differs from development: deliveries were faster and reviews happier, and the route history features shifted most. Validation and test scores therefore describe different periods, and the test gain partly reflects that the history features track the faster period as it happens (drift by fold in appendix A).
