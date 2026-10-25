# B9 conclusion — classification (for team review)

Every number below is read from this folder's files or T1's metrics_test.csv. Validation scores are selection scores (G-10); only test numbers are unbiased.

## Answer

- B ranks detractors better than A on the same test orders: AP 0.1972 vs 0.1785, difference +0.0187 [+0.0089, +0.0291] (paired bootstrap).
- At the frozen threshold 1/6, B sends 23.2 alerts/day (cap 25) with precision 0.208 and recall 0.300; A sends 51.1/day on its own rows, above the cap.
- Illustrative cost (5 per missed detractor, 1 per false alert): B 7,156 vs 7,705 with no alerts.
- Operating threshold 4/15 (B-G-07, post-test business change; the frozen 1/6 result above stays the unbiased one): on the test B sends 5.6 alerts/day with 1.89 false alarms per true detractor (1/6: 3.81), precision 0.346, recall 0.121 (B9.10).
- Orders outside B's scope fall back to A (B-G-06). A's validation AP outside the scope 0.2257 vs inside 0.2356; test outside 0.1614 on 3,396 orders (B9.15).
- Validation folds and the test are shown together, with each period's time window, in validation_and_test.csv and validation_and_test_windows.csv (B9.14): folds are selection scores across seasons; the test is one recent window.

## Evidence by step

- **B9.1**: Train, validation (selection scores, G-10) and test with 95% bootstrap intervals (1000 resamples, seed 42) for B, A and references. B's test AP 0.1972 [0.1808, 0.2176], width 0.0369; 1,541 test detractors.
- **B9.2**: B minus A on B's test rows: AP +0.0187 [+0.0089, +0.0291] (excludes zero).
- **B9.3**: Slices judged with more than 100 test detractors. Customer state: 3 judged, 4 too few. Pooled over judged states: precision A 0.164 / B 0.219, recall A 0.338 / B 0.278.
- **B9.4**: 4 numeric features moved by |SMD| >= 0.2 between final-fit and test rows: route_recent_delivery_days -0.76, route_recent_carrier_transit_days -0.58, purchase_month +0.41, order_dispatch_days -0.21. Target: prevalence 0.136 -> 0.099 (G-77).
- **B9.5**: Largest term: route_seller_to_customer_state_RS->MG. Top permutation feature: n_sellers. Against B4's ranking: Spearman 0.31, top-10 overlap 6; DIVERGES: team alerted, model unchanged.
- **B9.6**: B's test AP with the agreed label 0.1972; with the first-review label 0.1972.
- **B9.7**: At 1/6: B 23.2 alerts/day, precision 0.208, 463 detractors caught, cost 7,156 vs 7,705 with no alerts. Missed-dispatch rule on the test period: 1,273 orders flagged, precision 0.212, 16.8% of detractors.
- **B9.8**: Limitations listed in conclusion.md (scope, prediction moments, B-G-01, J-1 (a), B-G-05, G-75/G-77, illustrative cost, no causal claims).
- **B9.10**: Operating threshold 4/15 (B-G-07, post-test) vs frozen 1/6 on B's rows. Validation: 4.0 alerts/day, FP per TP 1.35, recall 0.084 (1/6: 17.0/day, 2.35, 0.250). Test: 5.6/day, FP per TP 1.89, precision 0.346, recall 0.121 (1/6: 23.2/day, 3.81). Cost 5:1 at 4/15 7,123 vs 7,156 at 1/6; cost 1:1 1,707 vs 2,844.
- **B9.11**: Training vs validation drift per fold for A and B, plus final fit vs test (SMD for numeric features and the target, TVD for categorical). Numeric features with |SMD| >= 0.2 in at least 3 of the 6 periods: A purchase_month (6), B purchase_month (6), B route_recent_carrier_transit_days (4), B route_recent_delivery_days (4).
- **B9.13**: Routes judged (more than 100 detractors): 3 of 48 on B's test rows; A on all of A's test routes is listed too (in or out of B's scope).
- **B9.14**: Each series: five validation folds, their mean ± SE, and the test with its 95% bootstrap interval; each period's time window is in validation_and_test_windows.csv and on the chart. B on B rows: folds mean 0.2482 ± 0.0313, test 0.1972 [0.1808, 0.2176]; A on B rows: folds mean 0.2302 ± 0.0305, test 0.1785 [0.1631, 0.1974]; A on A rows: folds mean 0.2317 ± 0.0276, test 0.1750 [0.1611, 0.1891]. Test window 2018-05-26 to 2018-08-29.
- **B9.15**: A's frozen model by B's scope (B-G-06 fallback). Validation AP mean over 5 folds: inside 0.2356, outside 0.2257. Test: inside 0.1798 (15,570 orders), outside 0.1614 [0.1350, 0.1964] (3,396 orders).

## Limitations

- Scope: seven states (B-C1); orders outside them are served by A's frozen model (B-G-06), whose results there are in B9.15.
- Prediction moments differ: checkout for regression, carrier handover for classification; the classifier cannot act before handover.
- Fold 1 is below A's training-row minimum (B-G-01); the 5-fold comparison keeps it.
- B's history features for test rows use earlier test weeks (J-1 (a)), as in deployment; the test gain may partly reflect that recency.
- The test period is the newest and differs from development (G-77); A's classification test cohort is below the 15% detractor share (G-75).
- No causal claims: features describe association, not the effect of an intervention.
- B classification uses sigmoid calibration by decision (B-G-05), a deviation from the 8.3 rule.
- Cost is illustrative (5 per missed detractor, 1 per false alert).

## Questions for the team

1. Confirm B as the delivered model for this task (G-79), on the test evidence above.
2. Any slice or limitation that must be resolved before B10 and the report?
3. Operating threshold decided: 4/15 (B-G-07), reported as a post-test change beside the frozen 1/6; confirm the alert volume suits the contact team.
