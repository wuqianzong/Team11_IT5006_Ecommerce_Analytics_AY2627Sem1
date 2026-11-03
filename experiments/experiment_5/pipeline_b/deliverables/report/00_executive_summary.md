## Executive summary

For each Olist order the business needs two answers: how many days delivery will take, so the customer can be promised a realistic range, and whether the customer is likely to leave a 1 or 2 star review, so customer service can act before it is written. We predict the first at checkout and the second when the parcel is handed to the carrier.

**Method.** Every model row holds only what is known at its prediction moment; every step learned from data is fitted inside time-ordered, customer-purged folds; correlated and nested features are removed by a stated rule before selection; and models are compared from the simplest upwards, keeping the simpler one unless a more complex one is better by more than the fold-to-fold variation. We first built Pipeline A, a complete baseline for every order, and then Pipeline B, the delivered model, a focused improvement: the seven largest states, the seller's and the route's recent delivery history, and the alert moved to carrier handover. The rule for adopting the improvement was fixed before the test, and both pipelines were frozen and scored once on the same test period.

*Table 1. Headline test results, Pipeline B and Pipeline A on the same test orders.*

| Task | Pipeline B | Pipeline A on the same orders | Difference (95% interval) |
| --- | --- | --- | --- |
| Delivery lead time, MAE in days (lower is better) | {{B9.reg.test_mae_B}} | {{B9.reg.test_mae_A_on_B}} | {{B9.reg.mae_diff}} [{{B9.reg.mae_diff_lo}}, {{B9.reg.mae_diff_hi}}] |
| Share of orders predicted within 3 days | {{B9.reg.test_within3_B}} | {{B9.reg.test_within3_A_on_B}} | |
| Detractor ranking, average precision (higher is better) | {{B9.clf.test_ap_B}} | {{B9.clf.test_ap_A_on_B}} | {{B9.clf.ap_diff}} [{{B9.clf.ap_diff_lo}}, {{B9.clf.ap_diff_hi}}] |

Pipeline B is better on the same test orders in both tasks, and both intervals exclude zero. On the validation folds, most of the lead-time gain comes from the narrower scope, the rest from the new features; for the alert it comes from the features and the later moment. Orders outside the seven states are served by Pipeline A's frozen model.

**Use.** Olist's own delivery estimate missed the actual lead time by {{BC.promise.olist_mae_2dp}} days on average on the same test orders. Pipeline B plus a buffer gives a promise the operation can keep: reset monthly on recent weeks, the buffer was {{BC.buffer.recentolist_buffer_days}} days, as long as Olist's promise but late for {{BC.promise.B10_late}} of test orders against {{BC.promise.olist_late}} (a post-test analysis). Late orders were often handed over late by the seller, so flag orders whose shipping limit passes without a handover, and alert customer service at handover (about {{B10.clf.combined_test_alerts_day}} alerts a day on the test, including the fallback) so it can reach at-risk customers before they review.

**Limits.** The test period was faster than development, the operating threshold was chosen after the test (the frozen threshold's result is reported as the unbiased one), and all findings are associations, not causes.
