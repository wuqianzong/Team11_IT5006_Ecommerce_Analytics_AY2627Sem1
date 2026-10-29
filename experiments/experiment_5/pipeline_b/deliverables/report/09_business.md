## 9 Business recommendations

Three actions follow from the results; each is labelled as an observation (measured here), a literature-supported hypothesis or an unmeasured mechanism, and the dashboard shows the detail behind each.

*Table 21. Recommended actions and their evidence.*

| Action | What the evidence shows | Label | Dashboard |
| --- | --- | --- | --- |
| Promise a range, not a date | On validation, a buffer of {{B12.reg.buffer_90}} days puts 90% of orders on time and {{B12.reg.buffer_95}} days 95%; on the faster test period those buffers leave {{B12.reg.buffer_90_test_late}} and {{B12.reg.buffer_95_test_late}} late. Choose the buffer on recent weeks and watch the late share by state. Overly optimistic promises carry costs after the sale (Cui et al., 2024) | Observation; literature-supported hypothesis for the cost of over-promising | Lead time, promise buffer |
| Alert customer service at handover | The improved pipeline at 4/15 sends {{B10.clf.B_4_15_test_alerts_day}} alerts a day at precision {{B10.clf.B_4_15_test_precision}}; with the baseline's fallback at 1/6 the total is {{B10.clf.combined_test_alerts_day}} a day at precision {{B10.clf.combined_test_precision}} | Observation | Detractor risk, alert statistics |
| Flag missed dispatch with a rule | Orders whose shipping limit passes without handover are detractors with precision {{B9.clf.missed_dispatch_precision}}, and the rule catches {{B9.clf.missed_dispatch_share}} of all detractors on the test period, with no model | Observation | Detractor risk, missed dispatch |

*Figure: Share of orders late against buffer size, validation and test (F.reg.buffer_curve).*

**Cost.** Weighting a missed detractor as five false alerts, the serving rule's test cost is {{B10.clf.combined_test_cost_5_1}} ({{B10.clf.B_4_15_test_cost_5_1}} from the improved pipeline and {{B10.clf.A_out_test_cost_5_1}} from the fallback). The weighting is an assumption; the dashboard shows the trade-off at other thresholds.

**Review order when capacity is short.** The improved pipeline's alerts at 4/15 are reviewed first ({{B10.clf.B_4_15_test_alerts_day}} a day at precision {{B10.clf.B_4_15_test_precision}}). The baseline fallback's alerts outside the seven states come next ({{B10.clf.A_out_test_alerts_day}} a day at precision {{B10.clf.A_out_test_precision}}). The review cap of {{B10.clf.review_cap}} alerts a day asked for at the model review applies to the improved pipeline alone; with the fallback the combined volume is higher, which the team accepted. The fallback scores at checkout, but its alerts are reviewed at carrier handover, like the improved pipeline's, so each order's handover delay is known by then. Within the fallback, orders are reviewed by handover delay, longest first, with order value as the tie-break; an order not handed over by its shipping limit is flagged by the missed-dispatch rule. This order is an operational rule, not a measured result: the precisions above are measured for each stream, and no stored output evaluates the ordering inside the fallback.

**Slow sellers and routes.** The seller's earlier dispatch delay and the route's recent speed are among the strongest predictors (section 7.4). That late delivery goes with more detractors is an observation in our own data (section 4); that working on these sellers and routes would improve reviews is an unmeasured mechanism, because nothing here tests an intervention. The dashboard ranks routes and categories by observed outcomes for each quarter so operations can choose where to look first.
