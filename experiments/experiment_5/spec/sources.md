# Requirement sources → Experiment 5 stages

Purpose: one place where every external expectation is mapped to the stage that
must satisfy it. Each stage's gate review checks the rows that name it.
Local copies of the sources live in `docs/` (not in git); ask a teammate if missing.

## 1. Teacher expectations (Milestone 2 note, still binding)

Full text: [`teacher_expectation_m2.md`](teacher_expectation_m2.md).

| # | Expectation | Satisfied in | Evidence |
| --- | --- | --- | --- |
| T1 | 1–2 problems covering classification and regression | S00 | `protocol.yaml` tasks |
| T2 | Clear business stakeholder | S00, S08, S12 | task contract; policy decision; report |
| T3 | Target present/derivable from Olist | S00, S01 | target definitions; record table audit |
| T4 | All predictors known before outcome (no leakage) | S00, S01 | excluded-column list; availability audit |
| T5 | Customer-level grouping on `customer_unique_id` | S02 | group-overlap / purge checks |
| T6 | No post-outcome predictors | S01 | leakage audit |
| T7 | sklearn Pipelines; preprocessing fit inside CV folds | S04–S10 (via `e5lib.factory`) | factory tests; manifest |
| T8 | Plan for imbalanced target | S00, S02, S08 | fold prevalence; AP/Brier/threshold policy |
| T9 | Rationale for every engineered feature, literature-linked | S03, S05 | candidate-rationale table |
| T10 | Simplest variant first in each family | S04 | dummy / plain linear / plain logistic / single tree |
| T11 | Every complex model beats its family baseline | S06, S07 | ablation & grid tables vs baseline |
| T12 | 2–3 well-evaluated models over a long list | S07, S12 | selection tables; report scope |
| T13 | Justified metrics, literature-cited | S00, S12 | metric rationale |
| T14 | CV with documented seeds | S00, all | `protocol.yaml` seed; manifests |
| T15 | Not accuracy alone for imbalanced targets | S04–S10 | AP, ROC-AUC, Brier, confusion counts |
| T16 | Feature importance linked to business context | S05, S08 | permutation importance of the explained model |
| T17 | No random splits on temporal data | S02 | chronological windows |
| T18 | Error analysis, not only aggregate metrics | S05, S09, S10 | residuals, subgroups, curves |
| T19 | Train–Validate–Test comparison | S07, S09, S10, S12 | master metric table with distinct phases |
| T20 | Limitations discussion | S12 (inputs from every `STAGE.md`) | report limitations |

## 2. Project brief (Phase 3 additions)

| Requirement | Stage |
| --- | --- |
| Integrated final report and presentation | S12 |
| Deployed application using the model (at least one task) | S11 |
| Reproducible repository structure | Platform (`run_pipeline.py`), S12 |

Check the brief PDF at S00 and add any missing Phase 3 requirement here.

## 3. TA feedback

### 3.1 Milestone 1 TA feedback (`TA-M1-2026-10-05`, from `docs/milestone1_feedback_response.md`)

| TA concern | Stage |
| --- | --- |
| Literature organised around the two chosen tasks | S00, S12 |
| Justify linear baselines vs trees; explain why RF is the first extension | S04, S06 |
| Explicit features with formula, grain, availability, signal, missingness | S01, S03, S05 |
| Cited metric rationale and regression trade-offs | S00, S12 |
| Narrow scope and modest testable gap | S00 |
| Per-task prediction-time statement | S00 |
| Joins and one-to-many handling shown | S01 |
| Lowest-review label bias: minimum-vs-first review sensitivity | S01 (label audit), S03 |
| EDA tied to modelling decisions | S03 |
| Temporal outcome trends, not volume only | S03 |
| Separate observations / literature hypotheses / unmeasured mechanisms | all `STAGE.md` review summaries, S12 |
| Stakeholder action: who sees what, when, error trade-off | S00, S08 |
| Single coherent report narrative | S12 |
| Integrate model output into dashboard | S11 |

### 3.2 Milestone 2 TA comments

**TODO before S00 is accepted:** paste the Milestone 2 TA comments here and map each
to a stage, in the same format as §3.1.

## 4. Tutorial sequence → stages

| Tutorial | Topic used | Stages |
| --- | --- | --- |
| T1–T2 | problem framing, EDA, communication | S00, S03, S12 |
| T3 | data preparation, preprocessing | S01, S04 |
| T4 | split before preprocessing; pipelines | S02, S04 |
| T5 | linear regression, diagnostics, regularisation | S04, S05, S06 |
| Week 6 slides | training, deployment, bulk scoring | S11 |
| T7 (incl. non-agentic reference solution) | logistic regression, calibration, thresholds | S04, S08 |
| T8 | trees/forests, tuning, final fit, persistence | S06, S07, S10, S11 |

Adaptation: the tutorials use random/stratified splits for teaching; Olist is
chronological with repeat customers, so S02 uses chronological, customer-purged
windows instead (see `pipeline_design.md` Stage 2).
