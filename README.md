# SmartCommerce — IT5006 Group 11

This repository contains the Olist e-commerce dashboard and the Milestone 2 predictive modelling study for IT5006 (AY 2026/27 Semester 1). **Experiment 4 is the current modelling pipeline supporting the Word report.** Use the `milestone-2` branch and run the commands below from the repository root.

## Start here: current report and evidence

- [Word report with tracked changes](docs/reports/Team11_Phase2_IT5006_AY2627Sem1_final.docx): current results are in the main modelling sections and Appendix H.
- [Notebook 10](notebooks/10_matched_two_cycle_pipeline.ipynb): walkthrough of the saved split checks, two modelling cycles, model selection, final results and scoring. It reads saved evidence and does not retrain models.
- [Experiment 4 guide](experiments/experiment_4/README.md): protocol, implementation, reproduction and interpretation.
- [Saved evidence](artifacts/metrics/experiment-4/run-01/): all 130 validation-fold models/predictions and 26 final reference bundles/predictions, plus comparison tables and verification records.
- [Active configuration](src/models/configs/active_pipeline.json): selected models and bundle locations used by the [scorer](src/models/experiment4_score.py).

The report Markdown and existing PDF remain historical while human revision is pending. The current report source is the tracked Word document; see [report status](docs/reports/README.md).

## One pipeline, two modelling cycles

Both cycles use the same task-specific five expanding chronological folds, customer purging and training-label maturity rules. Every candidate fits preprocessing within its training fold. Checkout predictors exclude downstream delivery/review outcomes; their event-time availability remains a reconstructed-data limitation.

1. Load the committed feature table, source reviews and split/feature contracts. Apply cart eligibility, task eligibility, label-time checks and customer separation.
2. **Cycle 1:** compare nine-feature dummy, plain unpenalized linear/logistic, single-tree and forest references.
3. **Cycle 2:** test controlled feature expansion, input transformations, regression target transformation, regularization and forest refinements. Keep both successful and unsuccessful comparisons. The fixed catalogue contains 15 regression and 11 classification recipes.
4. Select regression by minimum mean validation MAE and classification by maximum mean validation Average Precision. Choose the illustrative classification threshold from the selected model's development out-of-fold predictions. Save these choices before terminal scoring.
5. Refit all 26 fixed references on eligible preterminal training data and calculate terminal diagnostics without replacing models or retuning the threshold from terminal results.
6. Verify saved predictions, memberships, metrics, selection and bundle checksums; generate comparison tables/charts and score through the active configuration.

| Current selected model | Development validation mean ± sample SD | Terminal diagnostic |
| --- | --- | --- |
| Regression: 11-feature log-input/log-target Random Forest, 50 trees, depth 14, minimum leaf 50, no target clipping | MAE 5.0858 ± 1.2092 days | MAE 3.7277 days |
| Classification: 12-feature logged-input L2 Logistic Regression, C=0.01 | Average Precision 0.2349 ± 0.0617 | Average Precision 0.1752 |

These SDs describe variation across five chronological windows. The models are selected on development validation. The development data were reused adaptively and the terminal cohort was previously inspected, so terminal results are not an untouched-test claim.

The frozen classification threshold is **0.13740171395086628** under illustrative false-positive cost 1 and false-negative cost 5. Its terminal loss is **9,902 versus 8,535 for no alerts**. This experimental alert policy is **not recommended for operational deployment**. More complex models or refinements do not automatically improve validation performance.

## Reproduce Experiment 4

### 1. Install the recorded modelling environment

The completed run used Python **3.10.19**. Use Python 3.10 with the exact package versions in [Experiment 4 requirements](experiments/experiment_4/requirements.txt); use 3.10.19 when matching the recorded environment. The root `requirements.txt` serves the dashboard and is not the pinned modelling environment.

```bash
python3.10 -m venv .venv-experiment4
source .venv-experiment4/bin/activate
python -m pip install -r experiments/experiment_4/requirements.txt
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
```

On Windows, activate with `.venv-experiment4\Scripts\activate` and set the two thread variables in your shell. The commands below use the activated environment's `python`.

The necessary input CSVs, contracts and fitted evidence are committed. Run from the repository root so the local `src` and `experiments` modules resolve. The saved [input hashes](artifacts/metrics/experiment-4/run-01/input_hashes.json) identify the canonical inputs; do not overwrite them when reproducing.

### 2. Verify the committed evidence without fitting

```bash
python -m experiments.experiment_4.verify --run artifacts/metrics/experiment-4/run-01
```

Expected result: `status: passed`, 130 validation folds and 26 terminal prediction files checked, matching memberships/selection/threshold, and `no_new_fits: true`. The verification reads fitted pipelines, checks predictions and metrics, and writes `verification.json` in the chosen run directory. Small floating-point differences are checked with numerical tolerances.

Open [Notebook 10](notebooks/10_matched_two_cycle_pipeline.ipynb) in your notebook viewer to inspect the saved evidence interactively. Install Jupyter separately if your editor does not provide a notebook runner.

### 3. Retrain the complete fixed catalogue into a fresh directory

```bash
python -m experiments.experiment_4.run --output artifacts/generated/experiment4-reproduction-01
python -m experiments.experiment_4.verify --run artifacts/generated/experiment4-reproduction-01
python -m experiments.experiment_4.summarize --run artifacts/generated/experiment4-reproduction-01
```

This performs **130 fold fits and 26 final fits**. The original run took approximately six minutes in its recorded environment; time varies with hardware. Choose a new directory name for each attempt: the runner refuses to overwrite an existing run, and failures must be retained. `protocol.json` already defines the fixed candidate catalogue; do not rerun `freeze_protocol.py` as a prerequisite.

The summarizer creates paired-comparison tables, split checks, selected subgroup results, train/validation/terminal comparisons and three diagnostic figures under the new run directory. It summarizes saved predictions without retraining. Reproduction does not change the active configuration, which continues to point to the accepted `run-01` bundles.

### 4. Demonstrate scoring with the accepted selected models

Create a five-row feature sample from the committed input and score both tasks:

```bash
python - <<'PY'
from pathlib import Path
import pandas as pd
folder = Path('artifacts/generated/experiment4-scoring-demo')
folder.mkdir(parents=True, exist_ok=True)
pd.read_csv('data/business/ml/orders_ml_features.csv', dtype={'order_id': 'string'}).head(5).to_csv(folder / 'checkout_features.csv', index=False)
PY
python -m src.models.experiment4_score --task regression --input artifacts/generated/experiment4-scoring-demo/checkout_features.csv --output artifacts/generated/experiment4-scoring-demo/regression.csv
python -m src.models.experiment4_score --task classification --input artifacts/generated/experiment4-scoring-demo/checkout_features.csv --output artifacts/generated/experiment4-scoring-demo/classification.csv
```

This is an interface demonstration, not another evaluation. The scorer uses the active configuration, verifies bundle hashes and requires unique, non-null `order_id` values plus the model's constructed predictor columns. It does not fit models and refuses to overwrite an existing scoring output. Use fresh output names when repeating the demonstration. Classification output includes the frozen experimental rule; interpret it with the negative policy result above.

## Locate the evidence behind the report

All paths below are relative to `artifacts/metrics/experiment-4/run-01/`.

| Evidence | Files |
| --- | --- |
| Fixed recipes, environment, source/input hashes | `protocol.json`, `freeze.json`, `input_hashes.json` |
| Cohort checks and exclusions | `fold_membership.csv`, `exclusions.csv`, `split_audit.csv`, `terminal_identities.csv`, `terminal_eligibility.csv` |
| Training/validation results and controlled refinements | `fold_metrics.csv`, `summary.csv`, `paired_comparisons.csv` |
| Every fold model and validation prediction | `development/`, `*_oof.csv` |
| Development-only model and threshold choices | `selection_freeze.json`, `decision_policy.json`, `threshold_curve.csv` |
| Final bundles, predictions and results | `bundles/`, `terminal/`, `final_training_metrics.csv`, `terminal_metrics.csv`, `train_validation_terminal.csv`, `selected_subgroups.csv` |
| Report charts and verification | `figures/`, `completion.json`, `verification.json`, `active_scoring_verification.json`, `report_lineage.json` |

`verification_attempt_01.json` preserves an initial CSV probability-parsing verification failure. It was resolved using pandas `float_precision='round_trip'` for exact boundary decisions; fits and threshold selection were unchanged. Keep this setting when independently reconstructing the threshold from saved CSV probabilities.

## Repository structure and historical work

```text
 data/raw/                      Original Olist CSV inputs
 data/preprocessed/             Typed/cleaned transactional inputs
 data/reference/geography/      Geographic reference inputs
 data/business/dashboard/       Dashboard tables
 data/business/ml/              Canonical ML features, splits and contracts
 notebooks/01–04                Data preparation and feature construction
 notebooks/05–09                Historical modelling and diagnostics
 notebooks/10_matched_two_cycle_pipeline.ipynb  Current evidence walkthrough
 src/models/experiment4_pipeline.py             Current model factory and bundle scorer
 src/models/experiment4_score.py                Active scoring entry point
 src/models/configs/active_pipeline.json        Current selected bundles
 experiments/experiment_4/      Current fixed-catalogue study and pinned requirements
 experiments/experiment_3/      Historical refinement research
 experiments/refinement_cycle1/ Historical chronological refinement
 artifacts/metrics/experiment-4/run-01/         Current accepted evidence
 docs/reports/                  Current tracked Word report and report status
 deployment/app.py              Streamlit dashboard
 app.py                         Dashboard launcher
```

Notebooks 05–09, Experiment 3 and the `refinement-selected-v3/v4` bundles preserve earlier exploration. They are not the instructions for reproducing the current report. See the [notebook index](notebooks/README.md), [Experiment 3 archive](experiments/experiment_3/README.md) and [earlier refinement guide](experiments/refinement_cycle1/README.md) for those records. Their scores come from their own protocols and should not be substituted for Experiment 4's matched comparisons.

## Run the dashboard

Use a separate environment for the dashboard's dependencies:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

The dashboard uses `data/business/dashboard/`; Experiment 4 uses `data/business/ml/`. The current model scorer is a local interface and the experimental alert policy is not deployed to the dashboard.
