# s10_release — blueprint

| Field | Value |
| --- | --- |
| Stage | s10_release (`../pipeline_design.md` → s10) |
| Nodes | common |
| Status | AGREED |
| Owner | TBD |
| Last agreed | 2026-10-18 (team review, doc tab "Model solution (s01, s06–s10)", section s10) |
| Discussion | Claude Doc "Milestone 3 pipeline stages", tab "Model solution (s01, s06–s10)", section s10 |

## 1. Goal and gate
Goal: release the experiment in a fixed order:
- parity, then approval;
- then migration and a matching reproduction;
- only then the app, dashboard, report and slides.

Deadlines: slides locked 4 Nov; report and ZIP due 8 Nov.

## 2. Inputs
- s08 bundles; all stage outputs.
- `evidence/registry.yaml`.
- `data/business/dashboard/` (business tab only, read-only).

## 3. Method
1. **Reload parity (10.1).** Load each s08 bundle from disk and re-predict the test cohort. The
   predictions must be identical to the in-memory ones (`parity.json`).
2. **Approval (10.2).** Every stage card is ACCEPTED with a commit hash, `run_pipeline.py check`
   passes, and the team signs off. Release tag `e5-release-1`.
3. **Migration (10.3).** Only when the experiment lead orders it.
   - Copy into the brief's layout (`data/ notebooks/ src/ deployment/ docs/`); only paths
     change.
   - Add a reproduction README (setup, data placement, one command) and a pinned
     `requirements.txt`.
   - The Experiment 5 ML data replaces the current contents of `data/business/ml`.
4. **Reproduction check (10.4).** Rerun from the working folders on a clean checkout. Every
   output hash and every number in `numbers.json` must match the release
   (`migration_check.json`). Nothing below starts until it matches.
5. **Streamlit app (10.5; G-41).** One app with three tabs.
   - **Business dashboard (10.6).** Extends the Phase 1 dashboard (`deployment/app.py`); it is
     not a new build. It keeps its own descriptive data (`data/business/dashboard/`: all orders
     and statuses, Phase 1 rules such as filtering incomplete months out of the monthly charts).
     It is labelled as a separate scope and its numbers are never mixed with model results.
   - **Lead time** and **Detractor risk.** Machine-learning scope; they read only pipeline
     outputs (`evidence/build`), and the app computes no statistic itself. Seven panels per tab:

     | Panel | Lead time | Detractor risk | Source |
     | --- | --- | --- | --- |
     | Headline | MAE with 95% CI, share within ±3 days, gain over the dummy, test size, release tag | AP, ROC-AUC, Brier with CIs, prevalence; at the threshold: alerts per day, precision, recall, detractors caught | s08, s09 9.1–9.2 |
     | Fit | Predicted vs actual, residual histogram, decile calibration | PR, ROC and reliability curves, confusion matrix | s08, s09 |
     | Policy | Share of orders whose prediction exceeds the promised date, by state | Read-only threshold explorer with the chosen threshold and cap | s08 `threshold_table.csv`, s09 9.7 |
     | Where it errs | MAE by state (with n), distance band, month | Precision and recall by state (> 100 detractors), the "too few" list, the aggregate | s09 9.3 |
     | Why | Permutation importance, EDA-consistency badge, key s03 charts | Same, plus logistic odds ratios | s03, s09 9.5 |
     | Score | One order with an interval from test residual quantiles; bulk CSV | One order with risk score, risk band and alert flag; bulk CSV | s08 bundle (inference only) |
     | Data health | Drift table and training period; out-of-profile input warning | Same | s09 9.4, `training_profile.json` |

   - Input checks read types, allowed values and ranges from the s02 `data_dictionary.csv`
     (G-58), with clear errors: types, ranges, unknown states, no items, missing
     installments, impossible distance. The detractor-risk tab also takes the classification inputs
     adopted at the s03 gate (G-70): the main product's photo count and description length, and the seller's
     rating at checkout (looked up from reviews answered before the order; blank for a new seller).
   - Inference never fits. The app is deployed on Streamlit Cloud, and the live URL is tested
     before submission.
6. **Report and slides (10.7).**
   - Both are built from `evidence/build/` (reproduced outputs) and follow the brief's section
     list.
   - Every number is cited by evidence ID and checked against `numbers.json`, and citations are
     verified.
   - The report is 15–20 pages. The slides are a 10-minute story with app screenshots.
7. **Walkthrough notebook (10.8).** A read-only notebook that loads the released evidence and
   bundles and walks through every stage with markdown. It fits nothing.

## 4. Decisions
| ID | Question | Answer | Basis | Status |
| --- | --- | --- | --- | --- |
| s10-D1 | App scope | Three tabs: business dashboard, lead time, detractor risk | G-41; brief Phase 3 | Agreed |
| s10-D2 | Dashboard data | Business tab keeps its own descriptive scope; model tabs read pipeline outputs only | G-41 | Agreed |
| s10-D3 | Order | Parity → approval → migration → reproduction → deliverables | G-07 | Agreed |

## 5. Outputs (10.9)
`parity.json`, `input_validation.json`, `migration_check.json`, `app_sources.json` (every table
and chart in the model tabs mapped to its stage output and evidence ID), app and dashboard code,
report and deck drafts, notebook, release notes.

## 6. Checks
- Parity identical.
- Reproduction hashes match.
- Every model-tab element is listed in `app_sources.json`.
- Every report number matches `numbers.json`.

## 7. Milestone 2 reuse
`deployment/app.py` (Phase 1 dashboard) is extended after migration. No Milestone 2 model,
bundle or `data/business/ml` file is used.

## 8. Report hooks
Deployment section (app screenshots, URL, usage), reproducibility appendix.

## 9. Open questions
None.
