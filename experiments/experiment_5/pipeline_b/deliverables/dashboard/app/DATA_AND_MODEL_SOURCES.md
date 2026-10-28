# Team 11 Dashboard — Data and Model Sources

This document explains where the dashboard's business data, model evidence, model files, scoring inputs, and inference results come from.

The dashboard reads only frozen and accepted local Experiment 5 outputs. It does not call an external API, retrain a model, or read test labels to select a model or threshold.

## 1. End-to-end provenance

```text
Canvas Olist raw CSV
        |
        +-- Phase 1 business dashboard data
        |       +-- Business overview tab
        |
        +-- Experiment 5 s02 clean records
                +-- Pipeline A models
                +-- Pipeline B population and history features
                +-- B5 chronological customer-purged folds
                +-- B6/B7 training and tuning
                +-- B8 frozen recipes and thresholds
                +-- T1 single joint test and frozen bundles
                +-- B9 conclusion evidence
                +-- B10 release, router and app sources
                +-- B12 promise-buffer evidence
                            |
                            +-- Delivery lead time and Detractor risk tabs
```

## 2. Repository snapshot

- Shared branch: `e5/deliverables-henry`
- Initial dashboard implementation commit: `de70c8a`
- Experiment 5 release record: `experiments/experiment_5/pipeline_b/release/e5-release-2.json`
- Reproduced release tag: `e5-reproduced`
- Frozen-model tag: `e5-B-frozen`
- One-time joint-test tag: `e5-T1-tested`

## 3. Business overview data

### Direct source

```text
data/business/dashboard/smartcommerce_consolidated.csv
```

This is the Phase 1 business-analysis dataset. It contains order, order-item, customer, seller, product, payment, and review information.

The dashboard filters, sorts, groups, aggregates, and formats this dataset to show:

- KPI matrix;
- Category overview;
- Revenue variance;
- Delivery SLA;
- Buyer profiles;
- Seller profiles.

### Scope

- This tab describes all orders and statuses.
- It is not the model test cohort.
- The tab is explicitly labelled:

```text
Descriptive view of all orders; not model results
```

- The dashboard uses data from March 2017 onward.
- Monthly charts use complete months only.

### Phase 1 code provenance

Some order-level aggregation logic is adapted from:

```text
deployment/app.py
commit 86538e0a7dfff8dcd87d4be921591312660fcc71
```

The dashboard copy is:

```text
dashboard/app/dashboard_core/business_tab.py
```

`deployment/app.py` itself is not modified.

## 4. Model-result evidence

The dashboard does not recompute model metrics. It reads stored result tables and figures from the following accepted stages.

### 4.1 T1 — one-time joint test

Path:

```text
experiments/experiment_5/pipeline_b/stages/t1_joint_test/<task>/outputs/
```

`<task>` is either:

- `regression`
- `classification`

| File | Purpose |
| --- | --- |
| `metrics_test.csv` | Final A/B test metrics |
| `fold_and_test_table.csv` | Validation folds and test metrics |
| `predictions_test.csv.gz` | T1 saved predictions used for parity checks |
| `figures/test_errors.png` | Regression error distribution |
| `figures/test_curves.png` | Classification PR, ROC, and reliability curves |
| `test_rows_B.csv` | T1 kept/removed B test rows |

### 4.2 B9 — conclusion evidence

Path:

```text
experiments/experiment_5/pipeline_b/stages/b09/<task>/outputs/
```

| File | Purpose |
| --- | --- |
| `train_val_test.csv` | Train, validation, and test results with 95% intervals |
| `paired_test_differences.csv` | Paired B−A and B−dummy comparisons |
| `validation_and_test.csv` | Fold-window and test metrics |
| `subgroups.csv` | State, route, distance, and month slices |
| `business_by_route.csv` | Business results by route |
| `permutation_importance.csv` | Frozen-model permutation importance |
| `coefficients.csv` | Coefficients, odds ratios, or per-unit ratios |
| `drift.csv` | Development-to-test drift |
| `a_fallback_by_scope.csv` | A results inside and outside B scope |
| `residuals_summary.csv` | Regression residual quantiles and late shares |
| `threshold_options_curve.csv` | Stored threshold rows for classification |
| `missed_dispatch_rule_test.csv` | Missed-dispatch rule results |
| `label_sensitivity.csv` | Lowest-review vs first-review sensitivity |

### 4.3 B10 — release and serving

Path:

```text
experiments/experiment_5/pipeline_b/stages/b10/<task>/outputs/
```

| File | Purpose |
| --- | --- |
| `app_sources.json` | Panel-to-file and evidence-ID mapping |
| `serving_config.json` | Scope, thresholds, alert volumes, and out-of-profile rule |
| `input_validation.json` | Input rules and test cases |
| `drift_profile.json` | Bundle training profile and warning thresholds |
| `top_routes_categories.csv` | Top routes/categories by quarter |
| `threshold_results.csv` | Stored B, A, and combined threshold results |
| `release_manifest.json` | Bundle, recipe, training-row, and SHA-256 metadata |
| `router_check.json` | B/A routing verification |

### 4.4 B12 — promise-buffer evidence

Path:

```text
experiments/experiment_5/pipeline_b/stages/b12/regression/outputs/
```

| File | Purpose |
| --- | --- |
| `buffer_curve.csv` | Buffer size and late-delivery share |
| `buffer_choice.csv` | Buffers for 90% and 95% on-time targets |
| `buffer_by_state.csv` | Late share by state at the chosen buffers |
| `figures/buffer_curve.png` | Stored buffer-curve chart |

## 5. Model files

Each task has two frozen bundles: A and B.

```text
experiments/experiment_5/pipeline_b/stages/t1_joint_test/<task>/outputs/bundles/A/
experiments/experiment_5/pipeline_b/stages/t1_joint_test/<task>/outputs/bundles/B/
```

Each bundle contains:

```text
model.joblib
schema.json
training_profile.json
```

| File | Purpose |
| --- | --- |
| `model.joblib` | Trained sklearn Pipeline containing preprocessing and the estimator |
| `schema.json` | Numeric/categorical inputs, model ID, threshold, training rows, and versions |
| `training_profile.json` | Training-period numeric means/SDs and category shares |

### How the models were produced

1. Canvas Olist raw CSV files enter Experiment 5 s02.
2. s02 creates order-level `records.csv.gz`, records hashes, exclusions, and the data dictionary.
3. Pipeline B creates its seven-state population and history features in B2.
4. B5 creates chronological, customer-purged time-series folds.
5. B6/B7 train, compare, and tune models on the same folds.
6. B8 freezes the recipe, calibration choice, and threshold.
7. T1 reads the test cohort once and saves predictions and frozen A/B bundles.
8. The dashboard reloads the T1 bundles and never retrains them.

## 6. A/B routing

Routing comes from:

```text
experiments/experiment_5/pipeline_b/e5b/serving.py
```

and B10 `serving_config.json`.

Pipeline B is used when:

- customer state is in `SP, MG, RJ, PR, RS, BA, SC`;
- primary seller state is in the same seven states;
- `distance_km_max` is present.

All other orders use Pipeline A.

| Task | Pipeline B prediction time | Pipeline A prediction time |
| --- | --- | --- |
| Regression | Checkout | Checkout |
| Classification | Carrier handover | Checkout |

For classification, in-scope orders that have not yet been handed over are not scored. The missed-dispatch rule flags them after the shipping limit passes.

## 7. Score-panel inputs and inference

The Score panels are the only dashboard components that execute model inference.

### Model loading

Models are loaded through:

```text
experiments/experiment_5/pipeline_b/e5b/serving.py
Release.load(task)
```

### Held-out feature rows

The held-out demo picker uses:

```text
experiments/experiment_5/stages/s02_data/common/outputs/records.csv.gz
```

Test-row IDs are taken from:

```text
stages/t1_joint_test/<task>/outputs/predictions_test.csv.gz
```

Regression and classification B history features are rebuilt with the frozen T1 row builder:

```text
e5b.t1_joint_test.b_rows
```

All target and label columns are excluded before feature construction. No test label is read for scoring or model selection.

For a responsive local demonstration, the dropdown uses a deterministic 500-row held-out sample with:

```text
random_state = 42
```

Users may also upload a feature-level CSV for batch scoring.

### Prediction

Prediction is executed through:

```text
DashboardRelease.predict(...)
```

The dashboard does not call `.fit()`, refit, tune, or change calibration.

Regression prediction intervals use the p05–p95 residual quantiles stored in B9 `residuals_summary.csv`.

Classification alerts use:

- Pipeline B: the threshold selected on the dashboard slider, default `4/15`;
- Pipeline A: the fixed fallback threshold `1/6`.

## 8. Thresholds and derived values

The classification threshold rows come from:

```text
stages/b09/classification/outputs/threshold_options_curve.csv
```

Every regular slider stop maps to a stored threshold row.

| Item | Source |
| --- | --- |
| B operating threshold | `4/15` from the approved plan and B-G-07 |
| A fallback threshold | `1/6` from B10-D2 |
| Review alert capacity | `serving_config.json` |

At `4/15`, the combined B+A result is read from the stored B10 row.

At other B thresholds, the combined alert volume is the stored B alerts/day plus stored A alerts/day at fixed `1/6`. The dashboard labels this value:

```text
derived for display
```

Panel 3.6 derives detractor share from stored detractor and order counts and labels it:

```text
derived for display
```

## 9. Verification and model environment

### Frozen-bundle parity

The dashboard environment successfully reloads all four A/B bundles and reproduces T1 predictions on a 500-row sample.

| Task | Sample rows | Maximum prediction difference |
| --- | ---: | ---: |
| Regression | 500 | `1.07e-14` |
| Classification | 500 | `1.39e-16` |

Both are within T1's `1e-9` parity tolerance.

### Package versions

The bundle metadata records:

```text
scikit-learn 1.9.0
pandas 3.0.1
numpy 2.4.2
```

The dashboard uses its own local environment:

```text
dashboard/app/.venv
```

The local environment loads all four bundles successfully and passes the sample parity checks.

## 10. Known source gap

The approved plan asks the data-health panels to show:

- model version;
- release tag;
- training period.

The plan-mapped `serving_config.json` does not contain all three fields.

The dashboard therefore:

- does not guess;
- does not derive the training period at runtime;
- reports the missing source in the Data-health panel.

Model version is available in bundle `schema.json`, and release identity is available in the release record, but these are not fields in the plan's current `serving_config.json` mapping.

## 11. Key code entry points

| Function | File |
| --- | --- |
| App entry point | `dashboard/app/app.py` |
| Central paths | `dashboard/app/dashboard_core/paths.py` |
| Evidence loaders | `dashboard/app/dashboard_core/loaders.py` |
| Evidence and business data access | `dashboard/app/dashboard_core/data.py` |
| A/B routing wrapper | `dashboard/app/dashboard_core/routing.py` |
| Input validation | `dashboard/app/dashboard_core/validation.py` |
| Business tab | `dashboard/app/dashboard_core/business_tab.py` |
| Regression tab | `dashboard/app/dashboard_core/regression_tab.py` |
| Classification tab | `dashboard/app/dashboard_core/classification_tab.py` |
| Frozen serving implementation | `pipeline_b/e5b/serving.py` |
| T1 row builder | `pipeline_b/e5b/t1_joint_test.py` |
| Evidence register | `pipeline_b/evidence/registry_B.yaml` |
| Panel source mapping | `stages/b10/<task>/outputs/app_sources.json` |

