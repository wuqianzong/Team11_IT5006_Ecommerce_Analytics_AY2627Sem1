# B9 conclusion — regression (for team review)

Every number below is read from this folder's files or T1's metrics_test.csv. Validation scores are selection scores (G-10); only test numbers are unbiased.

## Answer

- B predicts delivery lead time better than A on the same test orders: MAE 3.299 vs 4.028 days, difference -0.729 [-0.754, -0.703] (paired bootstrap, paired_test_differences.csv).
- B is within 3 days of the actual lead time for 57.6% of its test orders (A on the same orders 44.3%).
- B beats its dummy reference (MAE 4.385); the frozen model is the plain linear recipe, so the plain reference equals it.
- Orders outside B's scope fall back to A (B-G-06). A's validation MAE outside the scope 6.7480 vs inside 5.1827; test outside 5.7491 on 3,366 orders (B9.15).
- Validation folds and the test are shown together, with each period's time window, in validation_and_test.csv and validation_and_test_windows.csv (B9.14): folds are selection scores across seasons; the test is one recent window.
- Promise buffers (B9.16): 11.1% of B's test orders arrive more than 3 days after B's prediction and 4.7% more than 6 days after (A on the same rows 9.3% and 4.3%).

## Evidence by step

- **B9.1**: Train, validation (selection scores, G-10) and test with 95% bootstrap intervals (1000 resamples, seed 42) for B, A and references. B's test MAE 3.2992 [3.2449, 3.3533], width 0.1084.
- **B9.2**: B minus A on B's test rows: MAE -0.7288 [-0.7537, -0.7030] (excludes zero).
- **B9.3**: Slices judged with at least 100 orders. Customer state: 7 judged, B better in 7; mean gain -0.930 days (SD 0.275).
- **B9.4**: 3 numeric features moved by |SMD| >= 0.2 between final-fit and test rows: route_recent_delivery_days -0.73, route_recent_carrier_transit_days -0.56, purchase_month +0.41. Target: mean 12.111 -> 7.904; median 10.053 -> 6.957 (G-77).
- **B9.5**: Largest term: primary_category_arts_and_craftmanship. Top permutation feature: seller_prior_dispatch_days. Against B4's ranking: Spearman 0.16, top-10 overlap 7; DIVERGES: team alerted, model unchanged.
- **B9.7**: B on its test rows: within 3 days 57.6%; delivered more than 3 days later than predicted 11.1% (A on the same rows 9.3%).
- **B9.8**: Limitations listed in conclusion.md (scope, prediction moments, B-G-01, J-1 (a), B-G-05, G-75/G-77, illustrative cost, no causal claims).
- **B9.11**: Training vs validation drift per fold for A and B, plus final fit vs test (SMD for numeric features and the target, TVD for categorical). Numeric features with |SMD| >= 0.2 in at least 3 of the 6 periods: A purchase_month (6), B purchase_month (6), B route_recent_carrier_transit_days (4), B route_recent_delivery_days (4).
- **B9.12**: Lead time starts at purchase; Olist approves an order when payment clears. Development rows: median purchase-to-approval boleto 1.21 days vs credit card 0.01; mean lead time 13.24 vs 12.04 days; lead time after approval 11.87 vs 11.87. Payment type stands for payment-clearance delay, not delivery quality (observation).
- **B9.13**: Routes judged (at least 100 orders): 20 of 48 on B's test rows; B has the lower MAE on 20 of them. A on all of A's test routes is listed too (in or out of B's scope).
- **B9.14**: Each series: five validation folds, their mean ± SE, and the test with its 95% bootstrap interval; each period's time window is in validation_and_test_windows.csv and on the chart. B on B rows: folds mean 5.0247 ± 0.6115, test 3.2992 [3.2449, 3.3533]; A on B rows: folds mean 5.1423 ± 0.6616, test 4.0280 [3.9701, 4.0834]; A on A rows: folds mean 5.4701 ± 0.6733, test 4.3364 [4.2813, 4.3900]. Test window 2018-05-27 to 2018-08-29.
- **B9.15**: A's frozen model by B's scope (B-G-06 fallback). Validation MAE mean over 5 folds: inside 5.1827, outside 6.7480. Test: inside 4.0280 (15,422 orders), outside 5.7491 [5.5929, 5.8946] (3,366 orders).
- **B9.16**: Residual = actual minus predicted lead time. On B's test rows, B's orders arrive more than 3 days after its prediction in 11.1% of cases and more than 6 days after in 4.7% (A on the same rows 9.3% and 4.3%); median residual B -1.64 days, A -2.72; 95th percentile B +5.77, A +5.33. With a 6-day buffer on B's prediction, 95.3% of test orders arrive in time.

## Limitations

- Scope: seven states (B-C1); orders outside them are served by A's frozen model (B-G-06), whose results there are in B9.15.
- Prediction moments differ: checkout for regression, carrier handover for classification; the classifier cannot act before handover.
- Fold 1 is below A's training-row minimum (B-G-01); the 5-fold comparison keeps it.
- B's history features for test rows use earlier test weeks (J-1 (a)), as in deployment; the test gain may partly reflect that recency.
- The test period is the newest and differs from development (G-77); A's classification test cohort is below the 15% detractor share (G-75).
- No causal claims: features describe association, not the effect of an intervention.

## Questions for the team

1. Confirm B as the delivered model for this task (G-79), on the test evidence above.
2. Any slice or limitation that must be resolved before B10 and the report?
