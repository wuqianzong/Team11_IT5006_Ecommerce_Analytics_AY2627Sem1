# B2 — population and history features (blueprint)

| Field | Value |
| --- | --- |
| Stage | B2, Pipeline B (G-79, CR-054 B-C1 to B-C9) |
| Nodes | regression, classification |
| Status | DRAFT |
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
   - B_LEAD_CAP (regression): lead_days > 93.65 (mean + 8 × SD of A's s02 pre-cutoff orders,
     audit.json; no floor);
   - B_NO_HANDOVER (classification): no carrier handover date;
   - B_REVIEW_BEFORE_HANDOVER (classification): review answered at or before handover;
   - B_WARMUP: purchased before 2017-02-12 (first six weeks), removed after the features are built.
2. **Prediction time.** Regression: purchase time. Classification: carrier handover time.
3. **Events.** One row per raw order purchased before the task's test cutoff: primary seller
   (highest price, then lowest item id, A's rule), last shipping limit, carrier date, delivery
   date, route = customer_state + "->" + seller_state. The estimated delivery date column is
   dropped on load.
4. **Weeks.** Calendar weeks, Monday to Sunday. A handover event counts in its carrier-date
   week; a delivery event in its delivery week. A row uses only complete weeks before its
   prediction week.
5. **Features (B-C6 to B-C9)**, all candidates for both tasks unless stated:
   - route (categorical);
   - prior seller late rate, prior seller late days, prior seller dispatch days (B-C7): mean over
     all of the seller's earlier handover weeks; a seller with no history takes the weighted
     3-week mean of sellers in the same seller state;
   - route lead days (B-C8) and route transit days (B-C8b): weighted 3-week mean (0.5, 0.3, 0.2
     for weeks w−1, w−2, w−3) of the route's weekly median; fewer than 10 route events in the
     3 weeks → 0.7 × seller state's + 0.3 × customer state's weighted 3-week mean, then the
     overall one;
   - classification only (B-C9): this order's handover late flag, late days and dispatch days.
6. **Test rows.** B2 builds features for development rows only. Test-row features are built in
   the joint test run, from events known before each test row's prediction week.

## 4. Outputs (per task, `pipeline_b/stages/b02/<task>/outputs/`)
`records_B.csv.gz` (development rows, A's columns + B's), `exclusions_B.csv`,
`exclusion_counts_B.csv`, `history_coverage.csv` (share of rows on own history vs each
fallback, per fold period), `feature_build_log.json`.

## 5. Checks
- Every history value uses events whose week is before the row's prediction week (asserted per row).
- No column derived from order_estimated_delivery_date exists.
- Development rows ⊆ A's development rows; removal counts add up per reason.
- No test row is in records_B.csv.gz.
- Two runs give byte-identical outputs.
