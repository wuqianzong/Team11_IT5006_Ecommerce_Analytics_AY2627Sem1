## 7 Results

On the same test orders the improved pipeline beats the baseline in both tasks. Validation scores were used to choose the models, so they are optimistic selection scores; only the test, read once, is an unbiased estimate. Fold-by-fold validation results and the test are shown together, each with its time window, because each fold is itself a later period that the model had not seen.

### 7.1 Delivery lead time

| | Validation MAE (selection) | Test MAE [95% interval] | Within 3 days (test) |
| --- | --- | --- | --- |
| Improved pipeline (delivered) | {{B9.reg.val_mae_B}} | {{B9.reg.test_mae_B}} [{{B9.reg.test_mae_B_lo}}, {{B9.reg.test_mae_B_hi}}] | {{B9.reg.test_within3_B}} |
| Baseline on the same test orders | | {{B9.reg.test_mae_A_on_B}} | {{B9.reg.test_within3_A_on_B}} |
| Dummy (median) on the same test orders | | {{B9.reg.test_mae_dummy_B}} | |

The improved pipeline's MAE minus the baseline's is {{B9.reg.mae_diff}} days on the same {{T1.reg.test_rows_B}} test orders (paired bootstrap interval {{B9.reg.mae_diff_lo}} to {{B9.reg.mae_diff_hi}}), so the gain is not an accident of the sample.

*Figure: Lead time by validation fold and on the test, with time windows (F.reg.validation_and_test).*

**Residuals, read honestly.** On validation the errors lean late: the average order arrives {{B9.reg.resid_mean_val_B}} days after the prediction, with a long right tail. On the test they lean early: mean {{B9.reg.resid_mean_test_B}} days, median {{B9.reg.resid_median_B}}, because the test period was faster than the development period (section 7.4). The residuals are therefore neither centred on zero nor constant in spread, and a promise built on the prediction needs a buffer chosen for the current period (section 9). {{B9.reg.late_3d_B}} of test orders arrive more than 3 days after the prediction ({{B9.reg.late_3d_A_on_B}} for the baseline) and {{B9.reg.late_6d_B}} more than 6 days after.

*Figure: Residuals on the test orders, improved pipeline and baseline (F.reg.residuals).*

**Where it errs.** Slices are judged only with at least 100 test orders. The improved pipeline is better than the baseline in every judged customer state, distance band and basket size, on {{B9.reg.routes_B_better}} of the {{B9.reg.routes_judged}} routes with enough orders, and in most months:

{{table:B9.reg.slices_aggregate}}

*Figure: Lead-time error by customer state (F.reg.by_state).*

### 7.2 Detractor alert

| | Validation AP (selection) | Test AP [95% interval] | Test ROC-AUC | Test Brier |
| --- | --- | --- | --- | --- |
| Improved pipeline (at handover) | {{B9.clf.val_ap_B}} | {{B9.clf.test_ap_B}} [{{B9.clf.test_ap_B_lo}}, {{B9.clf.test_ap_B_hi}}] | {{B9.clf.test_auc_B}} | {{B9.clf.test_brier_B}} |
| Baseline on the same test orders (at checkout) | | {{B9.clf.test_ap_A_on_B}} | {{B9.clf.test_auc_A_on_B}} | {{B9.clf.test_brier_A_on_B}} |

The improved pipeline ranks detractors better by {{B9.clf.ap_diff}} AP (paired interval {{B9.clf.ap_diff_lo}} to {{B9.clf.ap_diff_hi}}) on {{T1.clf.test_rows_B}} test orders with {{T1.clf.test_detractors_B}} detractors, and is better on ROC-AUC and on the Brier score, which measures how well calibrated the probabilities are. The two pipelines predict at different moments, so part of the gain is the later moment itself.

*Figure: Detractor alert by validation fold and on the test (F.clf.validation_and_test); PR, ROC and reliability curves on the test (F.clf.test_curves).*

**At the threshold.** At the frozen 1/6, the unbiased result, the improved pipeline sends {{B10.clf.B_1_6_test_alerts_day}} alerts a day on the test with precision {{B10.clf.B_1_6_test_precision}} and recall {{B10.clf.B_1_6_test_recall}}. After the test the business moved its operating threshold to 4/15 to cut false alarms, a post-test change reported beside the frozen result: {{B10.clf.B_4_15_test_alerts_day}} alerts a day, precision {{B10.clf.B_4_15_test_precision}}, recall {{B10.clf.B_4_15_test_recall}}. Orders outside the seven states are alerted by the baseline at its frozen 1/6 (section 9).

*Figure: Precision, recall and alerts per day against the threshold, marking 1/6 and 4/15 (F.clf.threshold_options).*

**Slices.** Precision and recall by customer state and route are judged only where the test has more than 100 detractors, which holds for few slices (appendix E). In every judged slice the improved pipeline is more precise; the baseline, which alerts more orders, has the higher recall in most of them.

*Figure: Detractor alert by customer state (F.clf.by_state).*

**Label choice.** Scored against the first review instead of the lowest, both pipelines' results change only in the fourth decimal (section 3), so the label rule does not drive the comparison.

### 7.3 Where the gain comes from

The improved pipeline changed three things at once: the scope, the features and, for the alert, the prediction moment. Scoring the baseline's frozen model on the improved pipeline's own validation rows separates the scope effect from the rest (five-fold means):

| | Baseline, all states | Baseline, seven-state rows | Improved, seven-state rows |
| --- | --- | --- | --- |
| Lead time, MAE (days) | {{B8.reg.pop_A_on_A}} | {{B8.reg.pop_A_on_B}} | {{B8.reg.pop_B_on_B}} |
| Detractor alert, AP | {{B8.clf.pop_A_on_A}} | {{B8.clf.pop_A_on_B}} | {{B8.clf.pop_B_on_B}} |

For lead time most of the lower error comes from the narrower scope, because the baseline is already better on the seven-state rows, and the rest from the new features. For the alert the scope changes almost nothing, so the gain comes from the history features and the later prediction moment.

*Figure: Where the gain comes from: scope vs features (F.reg.population); ROC-AUC and Brier by population (F.clf.auc_brier).*

### 7.4 What drives the predictions, and drift

Permutation importance measures how much each feature contributes to the frozen model on the test orders: the score lost when the feature is shuffled. For lead time the seller's earlier dispatch days, the route and the distance rank highest, so the seller's own delay matters at least as much as the journey. For the alert, the number of sellers in the order and the route's recent delivery and transit times rank above this order's handover delay, so route conditions and basket complexity carry more signal about a bad review than the dispatch delay alone. These are associations in the frozen model, not causes.

*Figure: Permutation importance, lead time (F.reg.importance) and detractor alert (F.clf.importance).*

This ranking differs from the selection ranking of section 5.4: Spearman correlation {{B9.reg.rank_spearman}} for lead time and {{B9.clf.rank_spearman}} for the alert, with {{B9.reg.rank_top10}} and {{B9.clf.rank_top10}} of the top ten features shared. The difference is expected: selection scored one feature at a time on development orders, whereas importance measures each feature inside the fitted model on the test period, where correlated features share credit.

*Figure: Coefficients, lead time (F.reg.coefficients); odds ratios, detractor alert (F.clf.coefficients).*

The test period differs from development: deliveries were faster and reviews happier, and the route history features shifted most. Validation and test scores therefore describe different periods, and the test gain partly reflects that the history features track the faster period as it happens.

*Figure: Drift between development and test, by fold (F.reg.drift).*
