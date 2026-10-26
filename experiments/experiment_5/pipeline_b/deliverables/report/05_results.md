## 5 Results and evaluation

Validation scores were used to choose models, so they are optimistic ("selection scores"); only the test, read once, is unbiased.

### 5.1 Delivery lead time

| | Validation MAE (selection) | Test MAE [95% interval] | Within 3 days (test) |
| --- | --- | --- | --- |
| B (delivered) | {{B9.reg.val_mae_B}} | {{B9.reg.test_mae_B}} [{{B9.reg.test_mae_B_lo}}, {{B9.reg.test_mae_B_hi}}] | {{B9.reg.test_within3_B}} |
| A on B's test orders | | {{B9.reg.test_mae_A_on_B}} | {{B9.reg.test_within3_A_on_B}} |
| Dummy (median) on B's test orders | | {{B9.reg.test_mae_dummy_B}} | |

B's MAE minus A's is {{B9.reg.mae_diff}} days on the same {{T1.reg.test_rows_B}} test orders (paired bootstrap interval {{B9.reg.mae_diff_lo}} to {{B9.reg.mae_diff_hi}}). B is better on {{B9.reg.routes_B_better}} of the {{B9.reg.routes_judged}} routes with at least 100 test orders.

**Where the gain comes from.** On validation, A's frozen model scores MAE {{B8.reg.pop_A_on_A}} on all states, {{B8.reg.pop_A_on_B}} on B's seven-state rows, and B scores {{B8.reg.pop_B_on_B}} on the same rows: most of the lower error comes from the narrower scope, the rest from B's features.

**Late tail.** {{B9.reg.late_3d_B}} of B's test orders arrive more than 3 days after its prediction ({{B9.reg.late_3d_A_on_B}} for A on the same orders) and {{B9.reg.late_6d_B}} more than 6 days after. B is closer on average but predicts shorter times, so a promise built on it needs a buffer (section 7).

### 5.2 Detractor alert

| | Validation AP (selection) | Test AP [95% interval] | Test ROC-AUC |
| --- | --- | --- | --- |
| B (delivered, at handover) | {{B9.clf.val_ap_B}} | {{B9.clf.test_ap_B}} [{{B9.clf.test_ap_B_lo}}, {{B9.clf.test_ap_B_hi}}] | {{B9.clf.test_auc_B}} |
| A on B's test orders (at checkout) | | {{B9.clf.test_ap_A_on_B}} | |

B ranks detractors better than A by {{B9.clf.ap_diff}} AP (interval {{B9.clf.ap_diff_lo}} to {{B9.clf.ap_diff_hi}}) on {{T1.clf.test_rows_B}} test orders with {{T1.clf.test_detractors_B}} detractors. Part of the gain is the later prediction moment.

**At the threshold.** At the frozen 1/6 (the unbiased result), B sends {{B10.clf.B_1_6_test_alerts_day}} alerts a day on the test with precision {{B10.clf.B_1_6_test_precision}} and recall {{B10.clf.B_1_6_test_recall}}. After the test the team moved B's operating threshold to 4/15 to cut false alarms (a post-test business change, reported beside the frozen result): {{B10.clf.B_4_15_test_alerts_day}} alerts a day, precision {{B10.clf.B_4_15_test_precision}}, recall {{B10.clf.B_4_15_test_recall}}.

### 5.3 Interpretation and drift

B's coefficients (regression) and odds ratios (classification) are read per one standard deviation of each transformed feature; permutation importance on the test rows ranks the seller's earlier dispatch days, the route and the distance highest for lead time, and the number of sellers, the route's recent delivery days, the number of items and the route's recent transit days highest for the detractor alert. This ranking differs from the feature-selection ranking by design: selection scored one feature at a time on development data, importance measures the fitted model on the test period. The test period is faster and happier than development, and the route history features moved most; validation and test scores are therefore not on the same footing.
