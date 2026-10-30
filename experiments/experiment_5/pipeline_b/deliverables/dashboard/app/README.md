# Team 11 Dashboard App

This directory contains the Streamlit dashboard for Milestone 3.

## Current status

Plan revision 2.3 (`../DASHBOARD_PLAN.md`, 2026-10-30) is implemented, with four tabs:

1. **Business overview:** every Phase 1 business section (KPI matrix, category overview, revenue variance, buyer and
   seller views, customer and seller rating distributions), on the dashboard's business data only.
2. **Delivery lead time:** panels 2.1–2.8 (headline, fit over time, errors, promise buffer, where it errs,
   operational priorities, why, data health). The promise buffer opens on Pipeline B's validation curve.
3. **Detractor risk at handover:** panels 3.1–3.9, with the B threshold slider over the stored thresholds
   (default 4/15; Pipeline A's fallback fixed at 1/6).
4. **ML deployment:** the held-out (test-period) orders the serving rule alerts on (4.1), each order's details at
   handover with both predictions and nine logistics and freight scenarios (4.2), and the orders whose alert would
   stop under a scenario (4.3). Scenarios are labelled as associations, not effects of the action.

Revision 2.3 removed the score pointers that tabs 2 and 3 kept after revision 2 moved scoring to tab 4, and renamed
tab 4 from "Score an order" to "ML deployment". Hosting plan: the model API in `../api/` and this app on Streamlit
Community Cloud (`../api/README.md`); the app is not hosted yet.

## Run locally

The app has its own isolated environment under `app/.venv`. It uses Python 3.12
with the package versions recorded in `requirements.txt`, which successfully loads
the frozen model bundles.

From the repository root on Windows:

```powershell
experiments\experiment_5\pipeline_b\deliverables\dashboard\app\.venv\Scripts\python.exe -m streamlit run experiments\experiment_5\pipeline_b\deliverables\dashboard\app\app.py
```

Run the dashboard tests:

```powershell
experiments\experiment_5\pipeline_b\deliverables\dashboard\app\.venv\Scripts\python.exe -m pytest experiments\experiment_5\pipeline_b\deliverables\dashboard\app\tests
```

The locally verified URL is `http://localhost:8501`.

Screenshots are in `screenshots/2026-10-30/` (1600 x 1000, headless Edge, after revision 2.3):
`01_business_overview.png`, `02_lead_time_headline.png`, `03_promise_buffer.png`, `04_detractor_headline.png`,
`05_alert_stats_test_4_15.png`, `06_ml_deployment_alert_list.png`, `07_ml_deployment_order_details.png`,
`08_ml_deployment_scenarios.png`. The 2026-10-29 set is kept as the earlier record; captures 02, 04 and 05 are
byte-identical in both sets.

## Input files

All files named by the approved plan are present. The app reads:

- `data/business/dashboard/smartcommerce_consolidated.csv`
- `stages/b10/<task>/outputs/app_sources.json`
- `stages/b10/<task>/outputs/serving_config.json`
- `stages/b10/<task>/outputs/input_validation.json`
- `stages/b10/<task>/outputs/drift_profile.json`
- `stages/b10/<task>/outputs/top_routes_categories.csv`
- `stages/b10/classification/outputs/threshold_results.csv`
- `stages/b09/<task>/outputs/train_val_test.csv`
- `stages/b09/<task>/outputs/paired_test_differences.csv`
- `stages/b09/<task>/outputs/validation_and_test.csv`
- `stages/b09/<task>/outputs/subgroups.csv`
- `stages/b09/<task>/outputs/permutation_importance.csv`
- `stages/b09/<task>/outputs/coefficients.csv`
- `stages/b09/<task>/outputs/drift.csv`
- `stages/b09/<task>/outputs/a_fallback_by_scope.csv`
- `stages/b09/<task>/outputs/business_by_route.csv`
- `stages/b09/regression/outputs/residuals_summary.csv`
- `stages/b09/classification/outputs/threshold_options_curve.csv`
- `stages/b09/classification/outputs/missed_dispatch_rule_test.csv`
- `stages/b09/classification/outputs/label_sensitivity.csv`
- `stages/b12/regression/outputs/buffer_curve.csv`
- `stages/b12/regression/outputs/buffer_choice.csv`
- `stages/b12/regression/outputs/buffer_by_state.csv`
- `stages/b12/regression/outputs/figures/buffer_curve.png`
- `stages/t1_joint_test/<task>/outputs/metrics_test.csv`
- `stages/t1_joint_test/<task>/outputs/fold_and_test_table.csv`
- `stages/t1_joint_test/<task>/outputs/predictions_test.csv.gz`
- `stages/t1_joint_test/<task>/outputs/figures/test_errors.png` (regression)
- `stages/t1_joint_test/<task>/outputs/figures/test_curves.png` (classification)
- `stages/t1_joint_test/<task>/outputs/bundles/{A,B}/model.joblib`
- `stages/t1_joint_test/<task>/outputs/bundles/{A,B}/schema.json`
- `stages/t1_joint_test/<task>/outputs/bundles/{A,B}/training_profile.json`

The ML deployment tab lists the alerted held-out orders from T1's stored test predictions (order id, model and
prediction only; the label column is never read), rebuilds each order's model inputs with the frozen T1 row builder,
and scores the scenarios with the frozen bundles.

The business tab reads only `data/business/dashboard/`.

## Missing files

None of the files named by the approved plan are missing.

## Known source gap

`serving_config.json` does not contain the model version, release tag or training
period requested by the data-health text. The app reports this gap instead of
inventing or computing those values.

No model is fitted, no test label is read, and this app does not deploy or migrate any evidence.

**Where predictions come from.** By default the app runs the frozen T1 bundles locally. When the environment variable
`MODEL_API_URL` is set, it sends the same rows to the model API (`POST {MODEL_API_URL}/predict/{task}`), which runs
the same bundles and fits nothing (`dashboard_core/model_client.py`; the API's tests check it returns what the local
path returns).

