# B2 — population and history features (blueprint)

| Field | Value |
| --- | --- |
| Stage | B2, Pipeline B (G-79, CR-054 B-C1 to B-C9) |
| Nodes | regression, classification |
| Status | AGREED (experiment lead, 2026-10-23: follows plan v3 and Henry's comments); round 2 changes B-G-03, B-G-04 |
| Inherits from A | s02 `records.csv.gz` (tag e5-A-frozen), A's test cutoffs, raw Olist tables (read-only) |

## 1. Goal and gate
Goal: apply B's population rules and build B's history features for the development rows of
each task, with no information from after the prediction time.
Gate: every history value uses only events completed before the row's prediction week; the
estimated delivery date is read nowhere; counts reconcile with A's s02.

## 2. Inputs
- `../../stages/s02_data/common/outputs/records.csv.gz` (A, accepted).
- Raw tables: orders, order_items, sellers, customers (`data/raw/`, read-only).
- A's test cutoffs (`spec/protocol.yaml` data_dependent.test_cutoffs).

## 3. Method
1. **Population (B-C1 to B-C5)**, applied to A's task-eligible rows, each removal with a reason
   code in `exclusions_B.csv`:
   - B_STATE: customer or primary seller state outside SP, MG, RJ, PR, RS, BA, SC, or missing;
   - B_DISTANCE: distance_km_max missing;
   - B_LEAD_CAP (regression): lead_days > mean + 8 × SD of lead_days on B's own development
     rows after B_STATE and B_DISTANCE (B-G-03; computed each run, recorded in
     feature_build_log.json; no floor);
   - B_NO_HANDOVER (classification): no carrier handover date;
   - B_REVIEW_BEFORE_HANDOVER (classification): review answered at or before handover;
   - B_WARMUP: purchased before 2017-02-12 (first six weeks), removed after the features are built.
2. **Prediction time.** Regression: purchase time. Classification: carrier handover time.
3. **Events.** One row per raw order purchased before the task's test cutoff: primary seller
   (highest price, then lowest item id, A's rule), last shipping limit, carrier date, delivery
   date, route = seller_state + "->" + customer_state. The estimated delivery date column is
   dropped on load.
4. **Weeks.** Calendar weeks, Monday to Sunday. A handover event counts in its carrier-date
   week; a delivery event in its delivery week. A row uses only complete weeks before its
   prediction week.
5. **Features (B-C6 to B-C9)**, all candidates for both tasks unless stated:
   Feature names (B-G-04) are in brackets.
   - route (categorical) [route_seller_to_customer_state];
   - prior seller late-handover rate, prior seller late-handover days, prior seller dispatch days
     (B-C7) [seller_prior_late_handover_rate, seller_prior_late_handover_days,
     seller_prior_dispatch_days]: mean over
     all of the seller's earlier handover weeks; a seller with no history takes the weighted
     3-week mean of sellers in the same seller state;
   - recent route delivery days (B-C8) and recent route carrier transit days (B-C8b)
     [route_recent_delivery_days, route_recent_carrier_transit_days]: weighted 3-week mean (0.5, 0.3, 0.2
     for weeks w−1, w−2, w−3) of the route's weekly median, the weights renormalised over the
     weeks that have events; fewer than 10 route events in the 3 weeks → 0.7 × seller state's + 0.3 × customer state's weighted 3-week mean, then the
     overall one;
   - classification only (B-C9): this order's handover late flag, late days and dispatch days
     [order_handed_over_late, order_handover_late_days, order_dispatch_days].
6. **Test rows.** B2 builds features for development rows only. Test-row features are built in
   the joint test run, from events known before each test row's prediction week.

## 4. Outputs (per task, `pipeline_b/stages/b02/<task>/outputs/`)
`records_B.csv.gz` (development rows, A's columns + B's), `exclusions_B.csv`,
`exclusion_counts_B.csv`, `history_coverage.csv` (share of rows on own history vs each
fallback, per quarter), `lateness_summary_B.csv.gz` (descriptive, Henry: by route, week and
seller with customer state and seller state — handover count, late-handover rate, mean
late-handover days, median carrier transit days and median delivery days; seven-state routes
only (B-G-03), events before the cutoff only; any A comparison filters A to the same seven
states), `feature_build_log.json`.

## 5. Checks
- Every history value uses events whose week is before the row's prediction week (asserted per row).
- No column derived from order_estimated_delivery_date exists.
- Development rows ⊆ A's development rows; removal counts add up per reason.
- No test row is in records_B.csv.gz.
- Two runs give byte-identical outputs.
