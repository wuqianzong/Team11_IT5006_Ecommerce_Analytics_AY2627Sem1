# Team 11 Dashboard App

This directory contains the Streamlit dashboard for Milestone 3.

## Current status

The approved dashboard plan is implemented:

- central paths;
- read-only manifest and bundle loaders;
- a thin wrapper around `pipeline_b/e5b/serving.py`;
- input-validation summaries;
- the Business overview tab;
- the Delivery lead time panels;
- the Detractor risk panels, including the B threshold slider and held-out scoring;
- loader, routing and AppTest coverage.

## Revision 2 (Henry's side, 2026-10-29)

Plan revision 2 (`../DASHBOARD_PLAN.md`) adds a fourth tab, **ML deployment** (named Score an order until revision 2.3; alerted held-out orders, their
details at handover, both predictions, scenarios), ports every Phase 1 section into Tab 1 with the customer and
seller rating distributions, and applies the review fixes (cap wording, 4/15 label, intervals, TP/FP/FN row).
Hosting: the model API in `../api/` on Render.com and this app on Streamlit Community Cloud; see `../api/README.md`.

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

Screenshots are in `screenshots/`:

- `business_overview.png`
- `delivery_lead_time.png`
- `detractor_risk.png`
- `threshold_4_15.png`
- `score_order.png`

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

The Score panels rebuild held-out inputs through the frozen T1 row builder and
show a deterministic 500-row demonstration sample. All target columns are
excluded before scoring. Batch scoring accepts uploaded feature-level CSV rows.

The business tab reads only `data/business/dashboard/`.

## Missing files

None of the files named by the approved plan are missing.

## Known source gap

`serving_config.json` does not contain the model version, release tag or training
period requested by the data-health text. The app reports this gap instead of
inventing or computing those values.

No model is fitted, no test label is read, and this app does not deploy or migrate any evidence.

The earlier shipping/freight what-if is not present because it is not part of the
approved `DASHBOARD_PLAN.md`.

