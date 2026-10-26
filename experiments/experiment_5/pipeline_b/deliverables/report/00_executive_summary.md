## Executive summary

Olist's customer-service and operations teams need two answers for each order: how many days delivery will take, and whether the customer is likely to leave a bad review (1 or 2 stars). We built both predictions on the Olist data with two pipelines. Pipeline A is the baseline: all states, predicting at checkout. Pipeline B is the delivered model: A plus one change request, covering orders whose customer and seller are both in the seven largest states (SP, MG, RJ, PR, RS, BA, SC), adding seller and route delivery history, and predicting the review risk when the seller hands the parcel to the carrier.

Both pipelines were frozen before the test period was read, and the test was read once for both.

| Task | Pipeline B (delivered) | Pipeline A on the same orders | B minus A (95% interval) |
| --- | --- | --- | --- |
| Delivery lead time, MAE in days (lower is better) | {{B9.reg.test_mae_B}} | {{B9.reg.test_mae_A_on_B}} | {{B9.reg.mae_diff}} [{{B9.reg.mae_diff_lo}}, {{B9.reg.mae_diff_hi}}] |
| Share of orders predicted within 3 days | {{B9.reg.test_within3_B}} | {{B9.reg.test_within3_A_on_B}} | |
| Detractor ranking, average precision (higher is better) | {{B9.clf.test_ap_B}} | {{B9.clf.test_ap_A_on_B}} | {{B9.clf.ap_diff}} [{{B9.clf.ap_diff_lo}}, {{B9.clf.ap_diff_hi}}] |

B is better than A on the same test orders in both tasks, and both intervals exclude zero. Orders outside B's seven states are served by A's frozen model. For the alert team, B runs at an operating threshold of 5/14, chosen after the test to cut false alarms: about {{B10.clf.B_5_14_test_alerts_day}} alerts a day on the test period, with precision {{B10.clf.B_5_14_test_precision}}. The frozen threshold of 1/6 remains the unbiased test result (section 5).

Recommendations: show delivery promises as a range around B's prediction rather than a single date; send detractor alerts at handover to customer service; flag orders whose shipping limit passes without a handover (section 7).
