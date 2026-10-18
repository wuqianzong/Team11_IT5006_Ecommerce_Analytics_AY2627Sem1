# Requirement sources → Experiment 5 stages

Purpose: one place where every external expectation is mapped to the stage that
must satisfy it. Each stage's gate review checks the rows that name it.
Stage tags S01–S10 are the ten stages of `pipeline_design.md` v1.0 (frozen 2026-10-17).
Local copies of the sources live in `docs/` (not in git); ask a teammate if missing.

## 1. Teacher expectations (Milestone 2 note, used as the grading rubric)

Full text: [`teacher_expectation_m2.md`](teacher_expectation_m2.md).

| # | Expectation | Satisfied in | Evidence |
| --- | --- | --- | --- |
| T1 | 1–2 problems covering classification and regression | S01 | `protocol.yaml` tasks |
| T2 | Clear business stakeholder | S01, S09, S10 | task contract; stakeholder actions; report |
| T3 | Target present/derivable from Olist | S01, S02 | target definitions; record audit |
| T4 | All predictors known before outcome (no leakage) | S02 | leakage audit of every column |
| T5 | Customer-level grouping on `customer_unique_id` | S05 | customer purge / overlap checks |
| T6 | No post-outcome predictors | S02 | leakage audit |
| T7 | sklearn Pipelines; preprocessing fit inside CV folds | S04 (recipe), S06–S08 (fitted via `e5lib.factory`) | recipes; factory tests; manifest |
| T8 | Plan for imbalanced target | S01, S05, S07, S08 | class support per fold; class-weight grid; AP/Brier; threshold |
| T9 | Rationale for every engineered feature, literature-linked | S03, S04 | `feature_dictionary.csv`; candidate rationale |
| T10 | Simplest variant first in each family | S06 | dummy / plain linear / plain logistic / single tree |
| T11 | Every complex model beats its family baseline | S06, S07, S08 | decision records; finalists vs baselines |
| T12 | 2–3 well-evaluated models over a long list | S08, S10 | selection table; report scope |
| T13 | Justified metrics, literature-cited | S01, S10 | metric rationale |
| T14 | CV with documented seeds | S01, S05, all | `protocol.yaml` seed 42; manifests |
| T15 | Not accuracy alone for imbalanced targets | S06–S09 | AP, ROC-AUC, Brier, confusion counts |
| T16 | Feature importance linked to business context | S09 | permutation importance of the selected model |
| T17 | No random splits on temporal data | S05 | chronological test cohort and folds |
| T18 | Error analysis, not only aggregate metrics | S06, S09 | residuals, learning curves, subgroups |
| T19 | Train–Validate–Test comparison | S09, S10 | train–validation–test table with CIs |
| T20 | Limitations discussion | S09, S10 (inputs from every `STAGE.md`) | conclusion; report limitations |

## 2. Project brief (Phase 3)

| Requirement | Stage |
| --- | --- |
| Integrated final report (15–20 pages) and presentation (slides locked 4 Nov) | S10 |
| Deployed application using the model (at least one task), live URL, usage instructions, error handling | S10 |
| Dashboard with model outputs (Phase 1 dashboard extended) | S10 |
| Reproducible repository structure, README, requirements, notebooks | S10 (migration and reproduction check) |
| Use the Canvas copy of the Olist data | S02 |

## 3. TA feedback

### 3.1 Milestone 1 TA feedback (`docs/Project/Milestone1/TA Feedback.txt`; response in `docs/milestone1_feedback_response.md`)

| TA concern | Stage |
| --- | --- |
| Literature organised around the two chosen tasks | S01, S10 |
| Justify linear baselines vs trees; explain why RF is the first extension | S01, S06 |
| Explicit features with formula, grain, availability, signal, missingness | S02, S04 |
| Cited metric rationale and regression trade-offs | S01, S10 |
| Narrow scope and modest testable gap | S01 |
| Per-task prediction-time statement | S01 |
| Joins and one-to-many handling shown | S02 |
| Lowest-review label bias: minimum-vs-first review sensitivity | S02 (label audit), S09 |
| EDA tied to modelling decisions | S03 |
| Temporal outcome trends, not volume only | S03 |
| Separate observations / literature hypotheses / unmeasured mechanisms | all `STAGE.md` review summaries, S09, S10 |
| Stakeholder action: who sees what, when, error trade-off | S01, S08, S09 |
| Single coherent report narrative | S10 |
| Integrate model output into dashboard | S10 |

### 3.2 Milestone 2 TA comments

Not used. Milestone 2 is still being graded; on 2026-10-17 the team decided not to wait.
The teacher's Milestone 2 expectation note (§1) is the rubric the TAs grade against.

## 3.3 Teacher reference material

| Source | Used for | Stage |
| --- | --- | --- |
| NIBRS data dictionary and structure diagram (`docs/references/NIBRS/`, shared by the teacher) | Model for documenting the data: column-level dictionary, missing-value meaning, table structure with one-to-many links. The NIBRS data itself is not used | S02 (data_dictionary.csv, structure diagram), S04, S10 (report, app input checks) |

## 4. Tutorial sequence → stages

| Tutorial | Topic used | Stages |
| --- | --- | --- |
| T1–T2 | problem framing, question-driven EDA, confidence intervals, communication | S01, S03, S09, S10 |
| T3 | data preparation, preprocessing, ColumnTransformer | S02, S04 |
| T4 | split before preprocessing; pipelines | S04, S05 |
| T5 | linear regression, residual diagnostics, regularisation | S03, S06, S07 |
| Week 6 slides | training, deployment, drift, bulk scoring | S10 |
| T7 (incl. non-agentic reference solution) | protect test set, pipeline, CV vs baseline, OOF probabilities, threshold, fit once / test once, interpretation, save and reload, QA | S05, S06, S08, S09, S10 |
| T8 | dummy → logistic → tree → forest, tuning, learning curves, persistence | S06, S07, S08, S10 |

Adaptation: the tutorials use random/stratified splits for teaching; Olist is
chronological with repeat customers, so S05 holds out a chronological test cohort and
builds chronological, customer-purged CV folds, and checks class support per fold
instead of stratifying (see `pipeline_design.md` s05).
