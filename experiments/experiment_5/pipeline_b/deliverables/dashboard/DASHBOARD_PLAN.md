# Dashboard plan (contract between Henry and Solomon)

Status: APPROVED by Henry, revision 2, 2026-10-29 (decisions D1–D5 of the gap analysis https://claude.ai/artifact/WNhnLGdNqzWRWsjdBrwBwU; revision 1 approved 2026-10-28). Owner: Henry (content). Builder: Solomon (revision 1); Henry's side (revision 2 and hosting).
A change to this plan is Henry's commit (HANDOVER_TO_HENRY.md §4.7).

## 0. Rules the app follows

1. **Reads, never computes.** Every number and chart comes from a stored file listed below (G-41, A's s10 rule
   10.5, D-2). The app may filter, sort, look up and format; it never computes a metric, refits or reads a test
   label. Two display exceptions agreed by Henry (2026-10-28): the share in panel 3.6 (detractors ÷ orders, both
   stored) and the combined alert line in panel 3.4 at a slider position other than 4/15 (B's row + A's row, both
   stored); each is labelled "derived for display".
2. **Scoring is inference only.** The Score panel re-predicts held-out (test-period) orders with the frozen T1
   bundles through `pipeline_b/e5b/serving.py` (`Release.load(task)`), without labels (B-G-08). Nothing is fitted.
3. **Paths.** Model files: `experiments/experiment_5/pipeline_b/stages/<stage>/<task>/outputs/` (written below as
   `<stage>/<task>/…`); no migration (CR-061). Business tab: `data/business/dashboard/` (read only).
4. **Labels on every model number:** which model (Pipeline B or Pipeline A), which rows (B's test rows, A's
   test rows outside B's scope, validation folds), and "validation = selection score; test = read once".
5. **Thresholds (the dashboard shows the adopted model for business decisions):** B, inside the seven states,
   has a threshold slider over the stored B9.10 thresholds, starting at its operating threshold 4/15 (B-G-07).
   A's fallback, outside B's scope, stays fixed at its frozen 1/6 (B10-D2): A's counts are stored at 1/6 only, so no
   slider for A (Henry, option 4). The report and deck evaluate the options at A 1/6 and B 4/15, and keep B's
   frozen 1/6 as the unbiased test result.

## 1. Scope message (Henry's decision)

Binding rule B-G-06: Pipeline B scores orders whose customer and primary seller are both in SP, MG, RJ, PR, RS,
BA or SC and whose distance is known; Pipeline A's frozen model scores every other order.

- **Banner on both model tabs:** "Orders in the seven states are scored by Pipeline B (improved model). All other
  orders are scored by Pipeline A (baseline model). Every prediction shows which model made it." Plus the test
  split: orders inside / outside B's scope (`b10/<task>/serving_config.json` → `test_rows_by_scope`, B10.3).
- **Per order (Score panel):** a badge "Pipeline B" or "Pipeline A (outside B's scope: <reason>)" from the
  router's `scope_reason`.
- **Detractor tab only:** an in-scope order not yet handed over shows "Not scored yet: scored at carrier
  handover. If the shipping limit passes without handover, the missed-dispatch rule flags it" (B10-D9).
- The "not served" wording of CR-054 is not used anywhere (superseded by B-G-06).

## 2. Tabs

| Tab | Scope | Data |
| --- | --- | --- |
| 1 Business overview | Descriptive, all orders and statuses (Phase 1 dashboard, extended, not rebuilt; D-3, D-4) | `data/business/dashboard/` only; labelled "Descriptive view of all orders; not model results"; incomplete months stay excluded from monthly charts |
| 2 Delivery lead time | Model results, regression (B inside, A outside) | files in §3 |
| 3 Detractor risk at handover | Model results, classification (B inside, A outside) | files in §4 |
| 4 Score an order | Inference on held-out orders the models alert on (B at 4/15 inside the seven states, A at 1/6 elsewhere), with order details and scenarios | §4a |

Tab 1 keeps every Phase 1 section, ported from `deployment/app.py` with provenance comments (revision 2, D1):
KPI matrix per period against sidebar benchmarks with misses highlighted; KPI diagnostic stack; period-over-period
growth; category top and bottom 10 with highlighting; revenue variance; category deep dive (review-score mix over
time, SLA); order-level SLA; buyer and seller profiles with cohort growth. Revision 2 adds two panels:
**customer rating distribution** (share of orders by star 1–5, overall and by month; each order counted once at its
lowest valid score, the detractor label's rule, D2) and **seller rating distribution** (histogram of each seller's
average score, sellers with at least 10 reviewed orders, with the share below 3.5). Benchmarks live in the session,
not in a file.

## 3. Tab 2: Delivery lead time

| # | Panel | What it shows | Decision it supports | Reads (file, evidence ID) | Chart |
| --- | --- | --- | --- | --- | --- |
| 2.1 | Headline | B's test MAE (days) with 95% interval, share within 3 days, A on the same orders, B minus A with interval, B vs dummy, test rows | Is B good enough to set promises? | `t1_joint_test/regression/metrics_test.csv` (T1.3); `b09/regression/train_val_test.csv` (B9.1); `b09/regression/paired_test_differences.csv` (B9.2) | KPI cards |
| 2.2 | Fit over time | Five validation folds and the test, A and B, with time windows | Is performance stable over time? | `b09/regression/validation_and_test.csv` (B9.14); `t1_joint_test/regression/fold_and_test_table.csv` (T1.6) | Dot-and-interval chart + table |
| 2.3 | Errors | Error distribution on B's test rows; residual quantiles; share more than 3 and 6 days late | How wrong can a promise be? | `t1_joint_test/regression/figures/test_errors.png` (T1.3); `b09/regression/residuals_summary.csv` (B9.16) | Stored image + table |
| 2.4 | Promise buffer | Share of orders late against buffer size (validation and test); buffer for 90% and 95% on time; late share by state at those buffers | What buffer to add to the shown promise | **New sources:** `b12/regression/buffer_curve.csv`, `buffer_choice.csv`, `buffer_by_state.csv`, `figures/buffer_curve.png` (B12.2) | Line chart + table + bar by state |
| 2.5 | Where it errs | MAE of A and B by customer state, route, distance band, month, with order counts; slices with fewer than 100 orders marked "too few to judge" | Where to monitor or adjust promises | `b09/regression/subgroups.csv` (B9.3) | Bar chart (gain B − A) + table |
| 2.6 | Operational priorities (R-14, D-6a) | Quarter selector: top 5 routes and top 5 categories by observed mean lead time (≥ 100 orders), model coefficient beside; all routes on the test period below | Which routes and categories need operational attention | `b10/regression/top_routes_categories.csv` (B10.7); `b09/regression/business_by_route.csv` (B9.13) | Two bar charts + full table |
| 2.7 | Why | Permutation importance; coefficients as "ratio per unit" with the reading note | Which factors drive delivery time | `b09/regression/permutation_importance.csv`, `coefficients.csv` (B9.5) | Horizontal bars + table |
| 2.8 | Score an order | Pick a held-out order (or upload a CSV of held-out orders): prediction in days, interval from test residual quantiles (p05–p95), which model scored it, input-check messages | Demonstrates the deployed model | Bundles `t1_joint_test/regression/bundles/{A,B}/` via `serving.py`; `b10/regression/serving_config.json` (B10.3), `input_validation.json` (B10.5); interval from `residuals_summary.csv` (B9.16) | Form + result card; CSV download |
| 2.9 | Data health and transparency | Drift between development and test; out-of-profile warning rule (4 SD, B10-D11); A's results inside vs outside B's scope; model version, release tag, training period, definitions, limits | Can the numbers be trusted today? | `b09/regression/drift.csv` (B9.4); `b10/regression/drift_profile.json` (B10.6); `b09/regression/a_fallback_by_scope.csv` (B9.15); `b10/regression/serving_config.json` (B10.3) | Tables + text |

## 4. Tab 3: Detractor risk at handover

| # | Panel | What it shows | Decision it supports | Reads (file, evidence ID) | Chart |
| --- | --- | --- | --- | --- | --- |
| 3.1 | Headline | B's test AP, ROC-AUC, Brier with intervals and the detractor share; A on the same orders; B minus A AP with interval | Does B rank risky orders better? | `t1_joint_test/classification/metrics_test.csv` (T1.3); `b09/classification/train_val_test.csv` (B9.1); `paired_test_differences.csv` (B9.2) | KPI cards |
| 3.2 | Fit over time | Validation folds and test, A and B, with windows | Stability over time | `b09/classification/validation_and_test.csv` (B9.14); `t1_joint_test/classification/fold_and_test_table.csv` (T1.6) | Dot-and-interval chart + table |
| 3.3 | Curves | PR, ROC and reliability curves on B's test rows | How good are the scores at any threshold | `t1_joint_test/classification/figures/test_curves.png` (T1.4) | Stored image |
| 3.4 | Alert work statistics (dynamic threshold for B) | **B, seven states:** slider over the stored thresholds (0.02–0.60 in 0.01 steps, plus 1/6 and 4/15), default 4/15 marked "operating threshold". For the chosen threshold: alerts per day, precision, recall, false alarms per true detractor, cost 5:1 and 1:1, TP/FP/FN; chart of precision, recall and alerts per day against the threshold with the chosen point and the 6/day review cap. **A, other orders:** fixed at 1/6, same measures. **Combined (serving rule):** B at the chosen threshold + A at 1/6 per day; at 4/15 read from the stored row, elsewhere derived for display. Validation (out-of-fold) is the default view; a toggle shows the test period labelled "post-test view; the threshold was not chosen on it" | Staffing and the business threshold: how many alerts customer service can handle, at what precision and cost | B: `b09/classification/threshold_options_curve.csv` (B9.10), columns threshold, alerts_per_day, tp, fp, fn, precision, recall, fp_per_tp, cost_5_to_1, cost_1_to_1 for each period. A and combined at 4/15: `b10/classification/threshold_results.csv` (B10.3), rows "A frozen 1/6 (B10-D2)" and "B 4/15 + A 1/6 (serving rule)"; cap: `serving_config.json` `review_alert_cap_per_day` | Slider + KPI cards + line chart + stacked bar of alerts/day (B, A) |
| 3.5 | Missed-dispatch rule | Orders never handed over or handed over after the limit, their detractor precision and share of all detractors | A rule-based alert next to the model (P-3) | `b09/classification/missed_dispatch_rule_test.csv` (B9.7) | Table |
| 3.6 | Detractors by state | Test period: for each of the seven states (B's test rows) the orders, the detractors and the detractor share; one row "Other states" for the orders scored by A (outside B's scope: other customer or seller states, or distance unknown) with the same three columns. Share = detractors ÷ orders, derived for display. No alert metrics here (the stored per-state alert results are at the frozen 1/6) | Where bad reviews concentrate geographically | Seven states: `b09/classification/subgroups.csv` (B9.3), rows slice = customer_state, columns value, orders, detractors. Other states: `b09/classification/a_fallback_by_scope.csv` (B9.15), row period = test, scope = "outside B's scope", columns orders, detractors | Bar chart of the share + table |
| 3.7 | Operational priorities (R-14) | Quarter selector: top 5 routes and categories by observed detractor share (≥ 100 orders), odds-ratio coefficient beside; all routes on the test period below | Where to act on sellers, routes, categories | `b10/classification/top_routes_categories.csv` (B10.7); `b09/classification/business_by_route.csv` (B9.13) | Two bar charts + full table |
| 3.8 | Why | Permutation importance; odds ratios with the reading note; label sensitivity (first vs lowest review) | Which factors drive bad reviews | `b09/classification/permutation_importance.csv`, `coefficients.csv` (B9.5); `label_sensitivity.csv` (B9.6) | Horizontal bars + tables |
| 3.9 | Score an order | Pick or upload held-out orders: risk score, alert yes/no at the model's threshold (B 4/15, A 1/6), which model, "not scored yet" before handover, input-check messages | Demonstrates the deployed model | Bundles `t1_joint_test/classification/bundles/{A,B}/` via `serving.py`; `b10/classification/serving_config.json` (B10.3), `input_validation.json` (B10.5) | Form + result card; CSV download |
| 3.10 | Data health and transparency | As 2.9, classification files | As 2.9 | `b09/classification/drift.csv` (B9.4); `b10/classification/drift_profile.json` (B10.6); `a_fallback_by_scope.csv` (B9.15); `serving_config.json` (B10.3) | Tables + text |

## 4a. Tab 4: Score an order (revision 2, D3–D4)

Panels 2.8 and 3.9 move here; tabs 2 and 3 point to this tab.

| # | Panel | Content | Source |
| --- | --- | --- | --- |
| 4.1 | Alerted orders | Held-out (test-period) orders the serving rule alerts on: B frozen on B's test rows at 4/15; A frozen at 1/6 on orders outside B's scope. Filter by model, state, category; pick one | `t1_joint_test/classification/predictions_test.csv.gz` (order_id, model, rows, y_pred only; the label column is never read); scope from the router (`serving.py`) |
| 4.2 | Order details | Only what is known at carrier handover: customer (city, state), seller (city, state, prior average review), items (category, price, freight, weight, volume), payment type and instalments, purchase time, shipping limit, handover time, dispatch days, handover delay. Delivery dates, order status and the order's own review are never shown | `data/raw/` via the frozen T1 row builder, label columns excluded |
| 4.3 | Predictions | Model badge; alert risk against its threshold; predicted lead time with the stored-residual interval and estimated arrival; estimated transit = predicted lead time − dispatch days (≥ 0) | Bundles via `serving.py`; `residuals_summary.csv` (B9.16) |
| 4.4 | Scenarios | Logistics −10%: estimated arrival earlier by 10% of the estimated transit; the alert model's route inputs (recent carrier transit days, recent delivery days) cut by the same days. Freight −20%, −30%, −50% and "Free shipping" (modelled as −99%, stated in the small print): freight and freight-to-price ratio scaled. Each shows risk before and after and whether the alert still fires; out-of-profile warning where it applies. Logistics applies to B orders only (A has no route inputs). Label: "Scenario on the model's inputs: an association, not the effect of the action" | Bundles via `serving.py` (inference only) |

## 5. Suggested panels not built (D-6b)

| Suggestion | Decision | Reason |
| --- | --- | --- |
| Alert work queue (daily list of alerted orders) | Replaced in revision 2 by panel 4.1 (alerted held-out orders) | Henry, 2026-10-29 |
| Seller watchlist (rising late handover) | Dropped | No stored output; the evidence is frozen |
| Weekly model health monitoring | Dropped | No live data; 2.9 / 3.10 show the stored drift instead |
| Threshold slider for A's fallback | Not built | A's out-of-scope counts are stored at 1/6 only; a slider would need new evidence (Henry chose option 4) |

## 6. Decisions taken (Henry, 2026-10-28)

1. **Business tab code:** Solomon copies the Phase 1 functions he needs from `deployment/app.py` into `app/`, each
   with a provenance comment (source file and commit); `deployment/app.py` is not edited. Hosting and launch: ask
   Benson (HANDOVER §4.2).
2. **Panel 3.6:** detractors by state for the seven states plus one "Other states" row, counts and share; no alert
   metrics (see the panel).
3. **Score panels 2.8 and 3.9:** built. They score one held-out order at a time (or an uploaded CSV of held-out
   orders) with the frozen bundles; they are not the dropped work queue.
4. **Thresholds:** B dynamic, A fixed at 1/6 (option 4); report and deck use A 1/6 and B 4/15.

## 6a. Decisions taken (Henry, 2026-10-29, revision 2)

1. **Ownership (D5):** Henry's side implements revision 2 and the review fixes in `app/`; Solomon is told.
2. **Hosting (D5):** the frozen models are served from Render.com (free tier) as a small prediction API; the app is
   hosted on Streamlit Community Cloud (free tier) and calls the API when `MODEL_API_URL` is set, else predicts
   locally with the same bundles. Accounts and repository access are set up by Henry or Benson.
3. **Review fixes:** the cap sentence (B-CR-30), TP / FP / FN on their own row, 4/15 and 1/6 slider labels, visible
   95% intervals and B minus A cards, a test-view screenshot, a panel-presence test.
4. **What the scenarios are:** inference with edited inputs through the frozen bundles; no refit, no new feature
   (the regression's estimate is shown beside the alert model, never fed into it).

## 7. Waits for later

App URL and screenshots (for the report §8 and deck slide 15, "use"), after hosting.
