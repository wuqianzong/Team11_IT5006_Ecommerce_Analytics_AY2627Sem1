# SmartCommerce — IT5006 Group 11 (Olist E-Commerce Analytics)

Delivery lead-time prediction, detractor-risk alerts and a Streamlit dashboard for the **Olist Brazilian E-Commerce** dataset (2016–2018), built for **IT5006: Fundamentals of Data Analytics (AY 2026/27 Semester 1)**.

## ▶️ Start here

The final project (**Milestone 3**) is **Experiment 5**, in [`experiments/experiment_5/`](experiments/experiment_5/).
Its stage outputs, models and evidence register are frozen: the final report, the slides and the dashboard
read their numbers from them, so they are not edited after the release.

| I want to… | Go to |
| --- | --- |
| Open the final dashboard | [How to run the dashboard](#-how-to-run-the-dashboard) (`streamlit run app.py`) |
| Check how Experiment 5 was reproduced, or rerun it myself | [Appendix A](#appendix-a-reproducing-milestone-3-experiment-5-and-checking-its-dashboard) |
| Read Experiment 5's results without rerunning anything | [`notebooks/10_milestone3_experiment5.ipynb`](notebooks/10_milestone3_experiment5.ipynb) |
| Read Experiment 5's protocol and decisions | [`experiments/experiment_5/README.md`](experiments/experiment_5/README.md) |
| Verify the earlier Milestone 2 results | [Milestone 2 reproduction](#milestone-2-reproduction-and-report-evidence-earlier-milestone) |

Three separate Python environments are used, one per purpose:

| Purpose | Requirements file | Python |
| --- | --- | --- |
| Dashboard (local and Streamlit Community Cloud) | `requirements.txt` | 3.12–3.14 |
| Experiment 5 reproduction and tests | `experiments/experiment_5/requirements.txt` | 3.13 (release built on 3.13.9) |
| Milestone 2 verification (earlier milestone) | `requirements-milestone2.txt` | 3.10 or 3.13 |

---

## 📁 Repository Structure

The repository strictly follows the official course specification (**Page 7 of the Project Description**):

```text
.
├── data/
│   ├── raw/                  # 9 original, untouched Olist CSV files
│   ├── preprocessed/         # 9 cleaned & typed baseline CSVs (lossless type standardization)
│   ├── reference/geography/  # Pinned IBGE boundary and provenance for distance features
│   └── business/
│       ├── dashboard/        # 9 processed CSVs + smartcommerce_consolidated.csv (ready for Streamlit)
│       └── ml/               # Checkout-proxy features, targets, frozen splits and contracts
│
├── notebooks/
│   ├── 01_data_cleaning.ipynb                         # Stage 1: raw -> preprocessed (types, zip codes, GPS dedup)
│   ├── 02_dashboard_preprocessing.ipynb               # Stage 2: preprocessed -> business/dashboard (filtering & metrics)
│   ├── 03_business_dashboard_data_preprocessing.ipynb # Stage 3: data preview, table consolidation & KPI validation
│   ├── 04_ml_feature_engineering.ipynb                # Stage 4: deterministic ML features and split manifests
│   ├── 05_model_training_and_evaluation.ipynb        # Historical Baseline (Stage 5A): 27-feature random-group fits
│   ├── 06_model_tuning_and_selection.ipynb           # Historical Baseline (Stage 5B): bounded development selection
│   ├── 07_final_evaluation_and_scoring.ipynb         # Historical Baseline (Stage 5C): frozen random holdout scoring
│   ├── 08_refined_models_and_evidence.ipynb         # Refinement Cycle 1: leak-free chronological split (v3: tree/logistic)
│   ├── 09_refinement_cycle2_migration.ipynb          # Refinement Cycle 2: current champion models (v4: tuned RF + log1p)
│   └── 10_milestone3_experiment5.ipynb               # Milestone 3: Experiment 5 walkthrough from stored outputs (optional rerun)
│
├── deployment/               # Official directory for the dashboard application
│   ├── app.py                # Launcher: runs the Milestone 3 dashboard (experiments/experiment_5/.../dashboard/app/app.py)
│   └── app_milestone1.py     # Milestone 1 Executive Operations dashboard (kept for reference)
│
├── src/                      # Reusable Python source code and shared utilities
│   ├── common/               # Shared schemas, loaders, and utilities
│   ├── features/             # Feature engineering encoders and transformers
│   └── models/               # Model training, hyperparameter tuning, and evaluation
│
├── experiments/              # Systematic experimentation, ablation studies, and trial protocols
│   ├── refinement_cycle1/    # Whole-cycle orchestration and initial diagnostics
│   ├── feature_selection_v3/ # Feature blocks, combinations and model comparisons
│   ├── experiment_3/         # Comprehensive 6-phase refinement study (reproducible champion research)
│   └── experiment_5/         # MILESTONE 3 (final), self-contained; see Appendix A
│       ├── stages/           # Pipeline A (all states, at checkout): stages s01–s08
│       ├── pipeline_b/       # Pipeline B (seven states, at carrier handover): B2–B12, joint test T1,
│       │                     #   evidence register, and deliverables/ (report, deck, dashboard, audit)
│       ├── reproduction/     # Recorded reproduction of release e5-release-2 (ACCEPTANCE.md)
│       ├── reproduce.py      # Rerun (run) and compare-with-release (compare)
│       └── requirements.txt  # Experiment 5 environment (Python 3.13)
│
├── artifacts/                # Serialized model pipelines and evaluation metrics
│   ├── models/               # .joblib / .pkl model artifacts
│   └── metrics/              # Evaluation reports, confusion matrices, and benchmark bundles
│       ├── refinement-selected-v3/  # Refinement Cycle 1 accepted bundles & evidence
│       └── refinement-selected-v4/  # Refinement Cycle 2 (Current Champion) bundles & evidence
│
├── app.py                    # Root entrypoint launcher (delegates to deployment/app.py -> Milestone 3 dashboard)
├── requirements.txt          # Dashboard / Streamlit Cloud dependencies (Python 3.12-3.14)
├── requirements-milestone2.txt # Frozen environment for verifying Milestone 2
├── scripts/
│   └── reproduce_experiment5.py # Rerun Experiment 5 on any machine and check it (Appendix A.2)
├── REPRODUCE.md              # Short Experiment 5 reproduction card (full guide: Appendix A)
└── README.md
```

---

## 🔄 Data Architecture & Lineage

The data is organized into three clean layers under `data/`:

* **Dashboard Track**: $\text{data/raw/} \xrightarrow{\textbf{Stage 1}} \text{data/preprocessed/} \xrightarrow{\textbf{Stage 2}} \text{data/business/dashboard/} \xrightarrow{\textbf{Stage 3}} \text{smartcommerce\_consolidated.csv}$
* **Machine Learning Track**: $\text{data/raw/} \xrightarrow{\textbf{Stage 1}} \text{data/preprocessed/} \xrightarrow{\textbf{Stage 4}} \text{data/business/ml/orders\_ml\_features.csv} \xrightarrow{\textbf{Models}} \text{artifacts/metrics/}$

| Layer | Folder Path | Purpose & Rules |
| :--- | :--- | :--- |
| **1. Raw** | `data/raw/` | Exact, immutable copies of the 9 original Olist CSV files downloaded from Canvas. Never edit or overwrite manually. |
| **2. Preprocessed** | `data/preprocessed/` | **Lossless baseline**: Parses ISO datetimes (`pd.to_datetime`), preserves 5-digit zip codes as strings (`01037`), checks categorical enums, and removes 261,831 exact duplicate GPS rows. Keeps 100% of transaction rows across all other tables. |
| **3A. Business (Dashboard)** | `data/business/dashboard/` | **Dashboard-ready tables**: Applies business rules for executive presentation: removes timestamp sequence errors, filters orders to the stable operating period (**2017-01 to 2018-08**), collapses multi-reviews to lowest score, and pre-calculates `delivery_days`, `is_on_time`, and `item_revenue`. Houses `smartcommerce_consolidated.csv`. |
| **3B. Business (ML)** | `data/business/ml/` | **Predictive modelling features & targets**: 27 checkout-proxy predictors plus separate outcomes/eligibility in `orders_ml_features.csv`. All features are strictly restricted to information available at the point of checkout. |

---

## 🚀 How to Run the Dashboard

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

Use Python 3.12, 3.13 or 3.14. The pins match the dashboard's own
`experiments/experiment_5/pipeline_b/deliverables/dashboard/app/requirements.txt`, which load the
frozen Milestone 3 model bundles.

### 2. Launch Streamlit
Both launchers open the **Milestone 3 dashboard** (Business overview, Delivery lead time,
Detractor risk at handover, ML deployment), which lives in
`experiments/experiment_5/pipeline_b/deliverables/dashboard/app/` (see its README):
```bash
streamlit run app.py
# or
streamlit run deployment/app.py
```
Open the printed local URL (usually `http://localhost:8501`) in your browser.

On Streamlit Community Cloud, either `app.py` or `deployment/app.py` works as the main file; both
use the root `requirements.txt`. The app predicts with the frozen bundles in the repository unless
the `MODEL_API_URL` secret points to the model API.

To check the dashboard (tests, what each tab reads, and how it relates to the frozen evidence), see
[Appendix A.3](#a3-check-the-dashboard).

The Milestone 1 dashboard is kept as `deployment/app_milestone1.py`, written for the Milestone 1
environment (the `milestone-1` branch).

---

## Milestone 2 reproduction and report evidence (earlier milestone)

Start here to verify the submitted Milestone 2 results. The submitted report is
unchanged. Repository documentation below clarifies its reproduction instructions
and records evidence corrections separately.

### 1. Install the frozen modelling environment

Use a separate environment for the model bundles. The original build used Python
3.10.19; its five numerical/model package versions are recorded in
`artifacts/metrics/refinement-selected-v4/build_freeze.json`.

```bash
python3 -m venv .venv-milestone2
source .venv-milestone2/bin/activate
python -m pip install -r requirements-milestone2.txt
```

Python 3.13.5 with these same numerical versions was also checked for no-fit
reproduction. This is a model-verification environment; dashboard dependencies
are in `requirements.txt`, which since Milestone 3 pins the newer versions the Milestone 3
dashboard needs, so use `requirements-milestone2.txt`, not `requirements.txt`, to verify Milestone 2.

### 2. Run the command printed in the submitted report

```bash
python -m src.models.refinement_selected_v4_terminal
```

The bare command now verifies the frozen evidence. It checks bundle and dataset
checksums, scores all nine saved model/reference bundles, checks both selected
models against published per-order predictions, compares all terminal metrics,
79 subgroup rows and the train–validate–test matrix, and checks the recorded OOF
policy costs. It performs **no model fitting or threshold selection**.

Outputs go to a new directory under `artifacts/reproduction/`, never to the
published evidence directory. Specify another unused directory if desired:

```bash
python -m src.models.refinement_selected_v4_terminal --output /tmp/milestone2-check
```

A successful run prints `PASS` and writes `verification.json`,
`metric_comparison.csv`, predictions, diagnostic charts and cohort statistics.
The holdout has already been inspected: this is reproduction of the reported
results, not a new independent test. Frozen threshold 0.17 is a deployment policy;
the recorded chronological OOF empirical threshold is about 0.1822.

An archived receipt from the checked reproduction is in
[`artifacts/metrics/milestone2-reproduction-receipt/`](artifacts/metrics/milestone2-reproduction-receipt/).

### 3. Inspect the executable notebook

Open [`notebooks/09_refinement_cycle2_migration.ipynb`](notebooks/09_refinement_cycle2_migration.ipynb).
Select the Python interpreter from `.venv-milestone2` as its kernel. If using a
separate Jupyter installation, register that environment first:

```bash
python -m ipykernel install --user --name it5006-milestone2 --display-name "IT5006 Milestone 2"
```

It shows the report's nine-feature screening, 11/12-feature tuning, chronological
confirmation, frozen terminal verification and example scoring. It explicitly
inspects existing fits rather than retraining. The optional training recipe is
listed below. Notebook 08 is an earlier architecture, **not** the report's
nine-feature Cycle 1 benchmark.

### Evidence for the two cycles

The report compares **two families**: linear (Ridge/logistic) and tree-based
(single tree/random forest), with separate dummy references.

| Evidence | Protocol and source |
| --- | --- |
| Cycle 1, 9-feature comparison | Grouped CV: `artifacts/metrics/experiment-3/feature_importance/feature_dimension_score_comparison.csv` |
| Cycle 2 candidate tuning, Table C.2 | Grouped CV: `artifacts/metrics/experiment-3/transforms_and_tuning/phase4b_tuning_results.csv` |
| Default versus tuned candidates, Figure C.1 | `artifacts/metrics/experiment-3/transforms_and_tuning/phase4_default_vs_tuned_comparison.csv` |
| Selected-model chronological confirmation, Table C.1 | `artifacts/metrics/refinement-selected-v4/development_fold_metrics.csv` |
| Common terminal comparison, Table E.2 | `artifacts/metrics/refinement-selected-v4/terminal/metrics.csv`; all saved reference bundles are included |
| Train–validate–test, Tables E.1/F.5 | `artifacts/metrics/refinement-selected-v4/terminal/train_val_test_comparison.csv` |
| Permutation importance, Figures D.1/D.2 | Published tree-regressor and logistic-classifier CSV/PNG files in the feature-importance directory; these do not measure final-forest importance |
| Frozen policy and recorded OOF cost | `frozen_decision_policy.json` and `classification_development_oof.csv` in the v4 directory |
| Cohort and target statistics, Tables A.1/F.1 | `artifacts/metrics/report-evidence-exp3/`; both final training-ID files are included |

The selected terminal regression scores are MAE **3.7185 days**, RMSE **5.3085**
and R² **0.1871**. Classification AP is **0.1823**, ROC-AUC **0.5864** and Brier
**0.0949** on 15,769 orders. Frozen threshold 0.17 yields TP=456, FP=1,859,
FN=1,251, precision=19.70%, recall=26.71%, F1=0.2268 and illustrative loss=8,114
for FN=5, FP=1. The regression cohort has 15,615 orders.

Grouped screening scores and chronological confirmation scores use different
protocols. They are not a matched temporal estimate of improvement between the
two cycles. The forest reference and selected classifier have identical ranking
scores; applying the frozen policy changes decisions and illustrative loss, not AP.
Condition number 70.77/rank 71 applies to the encoded **nine-feature core**, not
all expanded-model matrices. The 27-feature matrix is singular.

### 4. Verify descriptive report statistics without loading models

Use an unused output directory to preserve the published audit files:

```bash
python experiments/experiment_3/verify_report_evidence.py --output /tmp/milestone2-statistics
```

This reproduces raw development target moments, Table F.1 statistics/drift and the
zero-item decomposition. See the separate evidence notes for the submitted report's
basket-count and classification-prevalence corrections:
[`docs/milestone2_reproduction_notes.md`](docs/milestone2_reproduction_notes.md).

### 5. Score a historical checkout example without fitting

```bash
python -m src.models.refinement_selected_v4 score \
  --bundle artifacts/metrics/refinement-selected-v4/bundles/regression/selected \
  --input examples/milestone2_checkout_orders.csv \
  --output /tmp/milestone2-lead-days.csv

python -m src.models.refinement_selected_v4 score \
  --bundle artifacts/metrics/refinement-selected-v4/bundles/classification/selected \
  --input examples/milestone2_checkout_orders.csv \
  --output /tmp/milestone2-detractor-risk.csv
```

The example includes predictor columns only, sampled from the saved development
data. It demonstrates scoring historical records, not a live integration.
Existing scoring output files are refused.

### Optional: rebuild the frozen model recipe

This retrains the recorded configuration and can take considerably longer than
verification. It performs no new hyperparameter search, recomputes OOF diagnostics
and retains deployment threshold 0.17. It does not alter the submitted bundles.

```bash
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
python -m src.models.refinement_selected_v4 build --output artifacts/reproduction/v4-rebuilt
python -m src.models.refinement_selected_v4_terminal \
  --run artifacts/reproduction/v4-rebuilt --acknowledge-previously-inspected-terminal
```

### Reproduce both grouped-CV tuning setups

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python experiments/experiment_3/reproduce_tuning.py \
  --output artifacts/reproduction/tuning-both
```

Use the pinned Milestone 2 environment and an unused output directory. This runs
55 current configurations (11 regression / 12 classification predictors) and 27
historical classification configurations (14 predictors, including zero-item
orders). Each uses the original five customer-grouped folds. It exports all
parameters, fold training/validation scores, means, population SDs, ranks and
selected configurations, then verifies the frozen final results without fitting
on terminal labels. It does not replace accepted model bundles or report evidence.

The two classification setups use the same saved folds and parameter grids:

| Setup | Predictors | Development orders | Logistic AP | Tree AP | Forest AP |
| --- | ---: | ---: | ---: | ---: | ---: |
| Historical screening | 14, including `has_items` and `freight_ratio_missing` | 78,938, including 604 zero-item orders | 0.29998 | 0.28428 | 0.30642 |
| Current screening | 12, excluding those two flags | 78,334, with zero-item orders excluded | 0.25538 | 0.23877 | 0.25878 |

Both select the same parameters and rank forest first, logistic second and tree
third. The forest's AP margin over logistic is 0.00644 and 0.00340 respectively.
Because both the cohort and feature list differ, this comparison does not isolate
the effect of either change. The historical scores correspond to the saved
screening table; the current setup applies the zero-item leakage-remediation rule.
Final chronological and terminal evaluation are separate stages, and their metrics
reproduce exactly after retraining. Detailed grids and provenance are published in
`artifacts/metrics/milestone2-tuning-reproduction/`.

For research-stage grouped comparisons and tuning, see
[`experiments/experiment_3/README.md`](experiments/experiment_3/README.md).
Their outputs are exploratory screening evidence, separate from the chronological
confirmation and final terminal metrics. No new training is needed to verify the
submitted scores.

---

## Appendix A. Reproducing Milestone 3 (Experiment 5) and checking its dashboard

Experiment 5 is reproduced **in place**: everything it needs is in `experiments/experiment_5/` plus the raw
Olist tables in `data/raw/`. The folders of earlier milestones (`src/`, `artifacts/`, `notebooks/01`–`09`) are
not used. Its outputs are frozen evidence: a check reruns the pipelines in a **separate clone** and compares,
and never commits new outputs.

### A.1 Releases and tags

| Tag | Meaning |
| --- | --- |
| `e5-A-frozen` | Pipeline A's code frozen; Pipeline B imports it read-only and refuses to run if it changed |
| `e5-T1-tested` | The held-out test cohort was read once, by the joint test T1 (both pipelines scored) |
| `e5-release-2` | The release: every stage's current run, recorded in `experiments/experiment_5/pipeline_b/release/e5-release-2.json` |
| `e5-reproduced` | Release 2 plus `reproduce.py` and the accepted reproduction record (`experiments/experiment_5/reproduction/`) |

Between `e5-release-2` and `e5-reproduced` only the reproduction script, its record and documents were added;
no code or stage output changed. Between `e5-reproduced` and `main`, no stage output of Pipeline A or B
changed either: later commits add the report, deck, dashboard, audit and documents. The dashboard on `main`
therefore reads exactly the reproduced evidence.

**T1 is never rerun.** Rereading the test cohort would turn the test into a selection step. T1's saved
predictions and model bundles stay as committed; stage B10 re-predicts them from the bundles, without
labels, as a parity check.

### A.2 Check the reproduction

**Option 1: read the recorded reproduction (no rerun).** The team reran release 2 from the raw data on the
reference machine (the experiment lead's Mac, Python 3.13.9) on 2026-10-27:

- [`experiments/experiment_5/reproduction/ACCEPTANCE.md`](experiments/experiment_5/reproduction/ACCEPTANCE.md):
  the decision record. All 34 stage/task nodes (Pipeline A s01–s08, Pipeline B B2–B12) exited 0.
- `experiments/experiment_5/reproduction/reproduction_check.json`: the file-by-file comparison. 622 of 629
  output files are byte-identical. Its `verdict` reads `FAIL` because the reference-machine rule requires
  identical files. The 7 files that differ are all in B10, whose release copy was produced on another machine
  (Windows, Python 3.13.7). They differ by float noise of at most 2.1e-14 and the recorded interpreter version.
  The experiment lead therefore judged those 7 files by the cross-machine tolerance rule below, under which they
  pass. Reproduction accepted; tag `e5-reproduced`.
- `experiments/experiment_5/reproduction/run_log.txt`: the run log.

**Option 2: rerun it yourself, on any machine (recommended).** One script reruns every stage from the raw
data and checks the result against the release. It works on macOS, Linux and Windows, and gets past the two
exact-match safeguards that a machine difference would otherwise trip (see
[A.2.1](#a21-machine-differences-what-to-expect-and-why)).

1. Clone the repository. On Windows, keep LF line endings: the recorded input hashes were taken on LF bytes,
   and a CRLF checkout of `data/raw/` makes every stage look stale.

   ```bash
   git clone -c core.autocrlf=false https://github.com/wuqianzong/Team11_IT5006_Ecommerce_Analytics_AY2627Sem1.git
   cd Team11_IT5006_Ecommerce_Analytics_AY2627Sem1
   ```

2. Create the Experiment 5 environment (Python 3.13; the same requirements file as at the release):

   ```bash
   python3.13 -m venv experiments/experiment_5/.venv
   experiments/experiment_5/.venv/bin/pip install -r experiments/experiment_5/requirements.txt
   ```

3. Run the reproduction:

   ```bash
   experiments/experiment_5/.venv/bin/python scripts/reproduce_experiment5.py
   ```

   On Windows: `experiments\experiment_5\.venv\Scripts\python.exe scripts\reproduce_experiment5.py`.

   The script ([`scripts/reproduce_experiment5.py`](scripts/reproduce_experiment5.py)) does not touch your
   checkout. It:

   1. creates a separate git worktree at tag `e5-reproduced`, next to the clone (`../e5-reproduce-check`;
      change it with `--workdir`);
   2. reruns the same 34 stage/task nodes, in the same order and with the same commands as
      `experiments/experiment_5/reproduce.py run`: Pipeline A s01–s08, then Pipeline B B2–B12 (T1 is not
      rerun). It prints one line per node;
   3. **decision check:** compares every decision field in the 42 decision files (`decision.json`,
      `selected_spec.json`, `frozen_recipe.json`, `adoption_decision.json`, `serving_config.json`,
      `counts.json`) with the release: chosen models, hyperparameters, features, transforms, calibration,
      row counts and the alert thresholds. Statistics (floating-point scores and out-of-fold counts), free-text
      notes, hashes and run metadata are not decisions and are left to the next step. It also requires B10's
      parity check: the frozen T1 models must re-predict the stored test predictions within 1e-9;
   4. **file-by-file check:** runs `reproduce.py compare --machine other` (rule CR-056).

   It writes `cross_machine_run.json`, `decision_check.json` and `reproduction_check.json` in the worktree's
   `experiments/experiment_5/reproduction/`, and ends with a summary. Expected result on any machine: every
   node runs and the **decision check reports `PASS`**. On the reference Mac the file-by-file check also
   passes (files byte-identical); on other machines it reports `FAIL` on refitted scores and counts, for the
   reasons and by the amounts in A.2.1. It takes about 25 minutes on the reference Mac; on a 4-core cloud
   Linux machine it took 47 minutes (2026-11-01: 34 of 34 nodes, decision check `PASS`). Delete the worktree afterwards with
   `git worktree remove --force ../e5-reproduce-check`.

   The script stops on any failure other than the two known safeguards.

**Option 2b: the team's original procedure (reference Mac).** In a fresh clone,
`git checkout e5-reproduced`, then `python experiments/experiment_5/reproduce.py run` and
`python experiments/experiment_5/reproduce.py compare --machine reference`. This is how the accepted
reproduction (Option 1) was made. On any other machine, `reproduce.py run` stops after s06 (A.2.1), so use
Option 2. (Check out `e5-reproduced`, not `e5-release-2`: `reproduce.py` was added after the release commit;
the code and stage outputs of the two tags are the same.)

#### A.2.1 Machine differences: what to expect and why

**Summary.** Experiment 5 is deterministic: on one machine, a rerun gives byte-identical files. Across
machines (CPU, operating system, maths library), floating-point arithmetic differs in the last digits, and
stages that **refit** models carry that difference into their scores. The team found and documented this
before the release; a full rerun on Linux on 2026-11-01 confirmed it. No modelling decision changes, and the
results in the report's test section do not depend on a refit.

**Evidence that it is a machine difference, not an error**

| Evidence | Source |
| --- | --- |
| Outputs made byte-identical across operating systems (line endings, fixed gzip timestamps), after a Windows audit | CR-031, commit `6e65d94` (2026-10-19) |
| Reruns byte-identical on the reference Mac at every stage acceptance (forests predict with one thread for this) | CR-051, CR-055; commits `0734057`, `9853ce5`, `6198c2c`, `c7d15c7`, and the B2–B9 acceptance commits (2026-10-21 to 25) |
| On Henry's Windows machine, refitting the frozen logistic recipe gave fold AP up to about 1.5e-3 away, identical on repeated runs, changing with OpenBLAS settings: "floating-point sensitivity of the unregularised logistic fit, not randomness". Validation alerts at 1/6: 5,833 vs 5,865; test rows (no refit) equal | `experiments/experiment_5/pipeline_b/WORKLOG.md`, 2026-10-26 |
| Policy: the Mac's hash check is the gate; other machines are judged by tolerance | CR-056 / B-CR-35, commit `46d68a4` (2026-10-27) |
| Accepted reproduction on the Mac: 34 of 34 nodes, 622 of 629 files byte-identical | CR-062, `reproduction/ACCEPTANCE.md` |
| Full rerun on Linux x86-64 (Python 3.13.18, pinned packages): repeated runs byte-identical; data, folds and protocol identical to the release; every decision equal; frozen T1 models re-predict the test predictions within 3.6e-13 | Option 2 run, 2026-11-01 |

**Where the differences come from.** Models with a unique, exactly computed fit agree to floating-point
noise: linear regression within 6e-13; single trees and dummy models identical. Random forests (near-tied
splits) differ by up to 0.055 days in regression and 0.003 in probability. The largest differences are in
the plain logistic regression, which has no regularisation (`C=inf`): its out-of-fold probabilities differ by
up to 0.13 (Pipeline A) and 0.24 (Pipeline B) on individual orders, matching the team's Windows finding of
"floating-point sensitivity of the unregularised logistic fit". Scores averaged over the folds move much
less (below).

**Size of the differences (Linux rerun vs the release, 629 files)**

| Group | Files | Difference |
| --- | --- | --- |
| Identical | 258 | none |
| Floating-point noise | 102 | at most 1e-9 |
| Within the refit tolerance | 95 | at most 2e-3 |
| Not judged (model pickles, PNG figures, gzip bytes) | 89 | not compared |
| Above the tolerance | 85 | see below |

The 85 files above the tolerance are:

- **refitted predictions and curves:** as above;
- **counts at thresholds:** small probability shifts move some orders across a threshold. At the thresholds
  in use (B10), alerts differ by up to 1.8% (34 of 5,865 validation alerts; about 0.1 alerts per day) and
  precision by up to 0.006; in the full threshold grids, up to about 10% at extreme thresholds;
- **two quantities that are noise by nature:** the condition number of the tree family's design matrix,
  which is rank-deficient (about 1e17 on both machines), and "distinct values" counts in s03 that count floats differing in the last
  digit as distinct (release 6,373 vs Linux 6,351).

Validation scores in decision notes differ in the fourth decimal (Linux vs release: a paired gain of
+0.0268 vs +0.0267; mean validation AP of the logistic model 0.2436 vs 0.2435).

**How to read the file-by-file result off the reference Mac.** The experiment record (CR-056, kept unchanged
as the record of the team's decision) judges other machines by tolerance: predictions within 1e-9, refitted
scores within 2e-3, and counts and labels equal. That rule was written before a full rerun had been made off
the Mac. A full rerun shows that refitted stages cannot meet "counts equal": a probability that moves in the
fourth decimal moves an order across a threshold, so the counts at that threshold change. The
`reproduction_check.json` therefore reports `FAIL` on another machine. Read each category this way:

| Category in `reproduction_check.json` | What it means off the Mac | Machine difference? |
| --- | --- | --- |
| `identical`, `numbers within 1e-9` | Same result | Not applicable |
| `numbers within 2e-3` | Refitted scores within the tolerance | Yes, expected |
| `bytes differ (not gated)` | Model pickles, PNG renders, gzip bytes; not compared by rule | Yes, expected |
| `DIFFERENT numbers` in refitted stages (s06–s08, B6–B10): predictions, curves, threshold tables, counts | Refitted probabilities move; orders cross thresholds | Yes: sizes in the table above |
| `DIFFERENT text values` in `decision.json` notes, frozen recipes, `counts.json`, `adoption_decision.json`, `parity.json`, `release_manifest.json` | Scores printed to 4 decimals, out-of-fold statistics, the frozen recipe's sha256 recorded in other files, the recorded interpreter version | Yes, as long as the decision check passes |
| `DIFFERENT text or labels` in `imputation_by_fold.csv` | Learned imputation medians differing in the 15th–16th significant digit (the file mixes text and numbers, so it is compared as text) | Yes: noise by nature |
| `DIFFERENT text or labels` in `doc_support/*/b2_lateness_by_route.csv` | The same routes and values; two rows swap order because a mean differs in its last digit (18.79515625 vs 18.795156250000005) | Yes: noise by nature |
| `DIFFERENT numbers` in s03 `feature_quality.csv` and the s04/B4 design-matrix tables | "Distinct values" counts of floats and the condition number of a rank-deficient matrix | Yes: noise by nature |
| `DIFFERENT bytes` in review packs and `conclusion.md` | Text reports that quote the moved scores | Yes |

A difference is **not** explained by the machine if the decision check reports `FAIL` (a model, hyperparameter,
feature, threshold or row count changed), if B10 parity fails (the frozen models no longer re-predict the test),
or if any file of s01, s02, s05, B2 or B5 (protocol, data, folds) differs beyond 1e-9. On the Linux rerun none
of these happened.

**Why `reproduce.py run` stops on another machine, and why that is not a failure.** Two safeguards compare
text or hashes exactly, which holds only on the producing machine:

1. `run_pipeline.py` marks an accepted stage `REOPENED` when any text in its `decision.json` changes, so the
   team re-reviews a changed result during development (README §9.2 of Experiment 5). The notes in that file
   print scores to 4 decimals, so a 1e-4 shift changes the text although the decision fields are equal. s07
   then refuses to start. The script restores the committed status cards after each node: a reproduction is
   a check, not a new review.
2. B10 classification checks that the frozen recipes recompute their sha256. Those files also record
   out-of-fold statistics (Linux vs release: 24.04 vs 23.86 alerts per day), so the hash changes although the recipe
   settings are equal. The script continues past this one check and records it.

**What a difference does not affect.** T1 (the held-out test) is never rerun. The test results in the report,
the slides and the dashboard come from T1's stored predictions and frozen bundles, which re-predict exactly on
any machine (B10 parity). The model choices and thresholds that produced them are the ones the decision check
compares.

**Option 3: read the results without rerunning.**
[`notebooks/10_milestone3_experiment5.ipynb`](notebooks/10_milestone3_experiment5.ipynb) shows every stage's
stored results (partition, model selection, the joint test, the Milestone 2 feedback checks, the number
register and the deployment inputs). Run it with the Experiment 5 environment as its kernel (install Jupyter
into it with `pip install jupyter`; Jupyter is not in the pinned set and does not affect any result). Leave
`RUN_REPRODUCTION = False` on `main`. Its `True` setting calls `reproduce.py run`, which completes only on the
reference Mac (A.2.1); to rerun on any other machine, use Option 2.

**Read-only checks on `main`** (they change no file), with `PY=experiments/experiment_5/.venv/bin/python`:

```bash
$PY experiments/experiment_5/run_pipeline.py status        # Pipeline A: every s01–s08 output FRESH
$PY -m pytest -p no:cacheprovider experiments/experiment_5/tests             # 59 tests
$PY -m pytest -p no:cacheprovider experiments/experiment_5/pipeline_b/tests  # 23 tests (+5 slow, skipped unless E5B_SLOW=1)
```

In `status`, s08 shows `READY_FOR_REVIEW` and s09, s10 show `TODO`/`MISSING`. This is expected: s08's gate fed
the joint test T1, and A's s09 and s10 were replaced by T1, B9 and B10 (decision G-79). Pipeline B's current
runs are listed in `experiments/experiment_5/pipeline_b/EVIDENCE.md`.

### A.3 Check the dashboard

The dashboard is in
[`experiments/experiment_5/pipeline_b/deliverables/dashboard/app/`](experiments/experiment_5/pipeline_b/deliverables/dashboard/app/).
It was built after the release, so check it on `main` (it is not in `e5-reproduced`). It fits no model and
reads no test label: it reads the dashboard business data (`data/business/dashboard/`), stored Pipeline B
stage outputs (B9, B10, B12, T1) and the frozen T1 model bundles.

1. From the repository root, with the dashboard environment (`pip install -r requirements.txt`, Python
   3.12–3.14):

   ```bash
   streamlit run app.py
   ```

   It opens four tabs: **Business overview**, **Delivery lead time**, **Detractor risk at handover** and
   **ML deployment**. The sidebar says where predictions come from (`local frozen bundles`, or the model API
   when `MODEL_API_URL` is set).

2. Run the dashboard's tests (they check the file loaders and router, that every threshold on the slider is a
   stored threshold, that every planned panel is present, and that the alert list and its scores match the
   stored test predictions without reading a label):

   ```bash
   pip install pytest
   cd experiments/experiment_5/pipeline_b/deliverables/dashboard/app
   python -m pytest -q -p no:cacheprovider tests      # 21 tests
   ```

3. Trace any panel to its source:
   [`DATA_AND_MODEL_SOURCES.md`](experiments/experiment_5/pipeline_b/deliverables/dashboard/app/DATA_AND_MODEL_SOURCES.md)
   lists every file each tab reads, and the dashboard plan
   ([`DASHBOARD_PLAN.md`](experiments/experiment_5/pipeline_b/deliverables/dashboard/DASHBOARD_PLAN.md))
   gives each panel's question and source. Screenshots from 2026-10-30 are in `app/screenshots/2026-10-30/`.

### A.4 How the report and slides use the evidence

The report and slides contain no hand-typed numbers: each number, table and figure has an ID in
`experiments/experiment_5/pipeline_b/evidence/registry_B.yaml`, and is accepted only if its source file
matches the hash in the current run's manifest. The built register is `pipeline_b/evidence/build/`
(`numbers_B.json`, tables, figures). The deliverables audit (9 checks, all passing on report revision 73 and
deck version 39) and the command to rerun it are in
[`experiments/experiment_5/pipeline_b/deliverables/audit/README.md`](experiments/experiment_5/pipeline_b/deliverables/audit/README.md).
