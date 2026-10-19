<!-- AUTHORITATIVE Milestone 3 / Experiment 5 pipeline design. This file is the only version
     that counts; edit it here (and mirror changes in spec/stages.json, README §3.1).
     v1.0 FROZEN 2026-10-17 by the team (CHANGELOG CR-001); v1.1 audit fixes (CR-003); v1.2 team feature-solution decisions (CR-004 to CR-009); rule 8 evidence retention (CR-013); s01 decision rule (CR-014); promised lead days dropped (CR-015); log transforms fixed, no s06 Step B (CR-016); s06–s07 agreed (CR-017); test cohort wording and s08 selection rule (CR-018); s08 agreed with human gates (CR-019); s09–s10 agreed (CR-020); audit 2 decisions (CR-021); audit 3 decisions (CR-022); data documentation (CR-023). It replaces the 13-stage draft
     derived from docs/milestone3_baseline_pipeline_design_2026-10-13.txt, which is superseded
     and not updated. After this freeze, changes go through README §9.2 and CHANGELOG.md. -->

# Milestone 3 baseline pipeline design — v1.2 (frozen 2026-10-17; CR-003 audit, CR-004 feature solution)

## Purpose

One clean, end-to-end pass from problem statement to business conclusion, in the textbook
order taught in Tutorials 1–8, for the two Milestone 2 checkout tasks on Olist:

- **Regression** — delivery lead time (purchase to delivery, fractional days); logistics stakeholder.
- **Classification** — recorded low review (score ≤ 2, positive class 1); customer-experience stakeholder.

Every Milestone 2 method is kept, but moved into this single flow; what Milestone 2 got wrong
is corrected and what it lacked is added (see "Changes from Milestone 2" below). There is **one
training cycle**, not two. No target score, winning model, feature set or threshold
is assumed in advance; those are decided by evidence inside the stages below and recorded in
`spec/protocol.yaml` or the stage's `decision.json`.

## Sources and authority

Project brief (Phase 3 deliverables and modelling guidelines); teacher expectations for
Milestone 2 (used as the grading rubric; Milestone 2 TA comments were not available and are not
waited for — team decision 2026-10-17); Milestone 1 TA feedback; Tutorials 1–8 and the Week 6
deployment slides. The step order follows the Tutorial 7 reference solution
(audit → protect test set → one pipeline → CV against a baseline → out-of-fold probabilities →
threshold → fit once, evaluate once → interpret → save and reload → QA) and Tutorial 8
(dummy → logistic → decision tree → random forest → tuning). `spec/sources.md` maps every
requirement to a stage.

Adaptation: the tutorials use random or stratified splits; Olist is chronological with repeat
customers, so this design uses a chronological test cohort and chronological, customer-purged
CV folds, and checks class support per fold instead of stratifying.

## Rules that hold in every stage

1. **One validation protocol.** The same chronological, customer-purged folds for every
   candidate, from the first dummy to the last tuned model.
2. **Defined vs fitted.** Cleaning and feature formulas are deterministic and row-local and may
   run before the split. Anything learned from data (imputation, encoding, scaling, caps from
   percentiles, model-based feature selection, calibration) is *defined* as a recipe in s04 and
   *fitted* only inside training folds through an sklearn Pipeline (Tutorials 3–4).
   Two declared exceptions, both computed once on orders before the test cutoff (never on
   test rows), pre-registered as fixed rules and reported as limitations:
   (a) the s04 label-free reduction from the 24 contract predictors to a core set (correlation, VIF, constant or
   duplicate columns); (b) the s04 feature selection by the s03 importance ranking (team
   decision G-19). Exception (b) uses development labels, including those of later validation
   folds, so CV scores of the selected set are optimistic; the report says so.
3. **Test cohorts protected.** Each task has its own test cohort: its newest 20% of eligible
   orders by purchase time. The cutoff is recomputed from the data in s02 by the 80/20 rule, not
   taken from Milestone 2 (G-28); exact IDs frozen in s05. No Experiment 5 decision sees it
   before s08, so it is a new held-out test, named a "new-customer time-ordered holdout" with its
   actual share after the purge (G-38, G-48). Test orders from customers who also
   appear in development are removed from the test cohort (test-boundary customer purge; team
   decision G-18), so each test cohort contains new customers only.
   Steps s03–s04 use only orders before the test cutoff (date rule; the purge, applied in s05,
   matters for model fitting); no step reads test labels until the final evaluation in s08.
4. **Honest estimates.** CV scores are selection scores, used to choose and reported as such,
   never as a generalisation estimate. The test cohorts give the only held-out estimate (G-38).
5. **Simplest first, one change at a time.** A more complex variant is kept only if it passes the
   decision rule in `protocol.yaml`; otherwise the simpler one stays.
6. **Every number comes from a stage output.** Report, slides, app and dashboard read the same
   evidence; nothing is typed by hand. No Milestone 2 result or metric is reused for any decision
   or conclusion; every count, threshold, cutoff and score is recomputed here. Milestone 2 code
   may be reused as logic only (G-29).
7. **Claims are labelled** as observation, literature-supported hypothesis, or unmeasured
   mechanism.
8. **Evidence is kept, not recomputed** (G-32). Every stage, the reproduction run included, stores
   what it produced as files that can be read without rerunning any model: the intermediate
   results behind each decision as well as the final one (every candidate's per-fold scores and
   out-of-fold predictions, every grid cell, rejected options with the reason, threshold and
   calibration curves, EDA tables), every figure as PNG plus a sidecar with its plotted data,
   fitted bundles for finalists and the release model, and `decision.json` naming the files it
   used. Nothing is overwritten in place: earlier runs stay retrievable by git commit and
   release tag. The report, slides, app and dashboard read these stored files through the
   evidence registry, never a fresh model run.

## The ten stages

Each stage links to its detailed blueprint (index: [`blueprints/README.md`](blueprints/README.md)).

### s01 — Problem statement (common)
Blueprint: [`blueprints/s01_problem.md`](blueprints/s01_problem.md)
Two tasks at checkout (prediction time = `order_purchase_timestamp`); stakeholder and the action
they take (who sees which prediction, when, and what they do); targets and label rules
(minimum-review label with a first-review sensitivity check); metrics (MAE primary, RMSE/R² and
share within ±3 days
secondary; AP primary, ROC-AUC/Brier/precision/recall/F1 secondary) and the illustrative
FN:FP = 5:1 cost; model families (dummy references, linear/logistic, tree/forest); decision
rule and tie-breaks; search budget; seed 42; the 80/20 test-split rule. `spec/protocol.yaml` has two layers:
(a) **pre-registered** values fixed here before any data is seen (tasks, metrics, cost, decision
rule, families, grids, budget, seed, the 80/20 split rule); (b) **data-dependent** values, each owned by
one stage and frozen at that stage's gate, before any model result: the per-task test cutoffs (s02); the core set and candidate
sets (s04), fold boundaries and class-support threshold (s05). Moving a fold
boundary in s05 is allowed only before s06 runs and is logged in CHANGELOG.
OUTPUT: `protocol.yaml` v1.0, `task_contract.md` (prediction time, stakeholder action, limits,
metric and model rationale with verified citations).
TEACHING: Tutorials 1–2; T7 reference §1.

### s02 — Data preprocessing (common)
Blueprint: [`blueprints/s02_data.md`](blueprints/s02_data.md)
Load the Canvas copy of the nine tables and record their hashes; clean deterministically
(types, zip prefixes as strings, geolocation de-duplication, IBGE boundary filter from
`docs/references/geography`, invalid timestamps flagged); join aggregation-first to one row per
order with cardinality checks; build both targets with their label-availability timestamps.
Leakage audit of every column against checkout time — `order_estimated_delivery_date` is known
at checkout (Milestone 2 wrongly listed it as post-checkout) but is never a predictor (G-35); it
only describes late-vs-promised trends in s03; `order_status`, `order_approved_at`,
`shipping_limit_date` are never predictors; `has_items` and `freight_ratio_missing` (post-purchase leakage) and `payment_missing` (constant once orders without a usable payment are removed) are not in the contract (G-42, G-51, G-61); a date-order
audit (purchase ≤ approval ≤ carrier ≤ delivery, estimated date and review answer after purchase)
logs violations; payment fields are assumed fixed at checkout (no timestamp in the data) (G-30). IDs are kept for audit, never as predictors.
Test cutoff per task (G-28, G-67): after the row-local population rules and before the outlier rule, the
purchase timestamp at the 80% position of the task's eligible orders; recorded in `audit.json`
and `protocol.yaml`.
Population and data-quality rules (G-20 to G-23), applied identically to development and test
and written to `exclusions.csv`, one row per removed order and reason with a reason code and its description (G-63):
- zero-item orders (`n_items == 0`) excluded from both tasks;
- orders with a negative value in a log1p candidate removed from both tasks (zero kept; G-62);
- regression: delivered orders with valid positive lead time; classification: orders not
  cancelled or unavailable with a valid review (targets never imputed). Both are scope
  limitations: the models describe orders that end up fulfilled and reviewed;
- suspected data-entry errors removed: `lead_days` > max(100, mean + 12 × SD), with mean and SD
  computed on pre-cutoff orders only (regression population only, G-66), or `distance_km_max` >
  4,397.53 km (both tasks);
- orders with missing `payment_installments_max` removed (the app's input checks reject the
  same case);
- orders without a usable payment (no payment rows, or only `not_defined`) removed (G-51).
OUTPUT: `records.csv.gz`, `exclusions.csv`, `data_hashes.json`, `audit.json` (joins, grains,
leakage, label sensitivity), and the generated data documentation following the NIBRS model the
teacher shared: `data_dictionary.csv` (every raw and derived column: type, nullable, grain,
missing-value meaning, known at checkout, eligibility) and the table-structure diagram (G-58).
TEACHING: Tutorial 3; T7 reference §3; brief leakage warning.

### s03 — EDA (regression, classification; pre-cutoff orders only)
Blueprint: [`blueprints/s03_eda.md`](blueprints/s03_eda.md)
Question-driven, before the test dates: target profiles (`lead_days` KDE and percentile table
incl. 1/5/25/50/75/95/99%, skewness, kurtosis; `is_detractor` bar chart with counts and shares);
outcome trends over time (lead time, late-vs-promised rate, detractor rate by purchase month, not
volume only); diagnostics of the 24 contract predictors, with the importance ranking over all 24 (G-42, G-61) — numeric vs `lead_days`: scatter, Pearson and
Spearman; categorical vs `lead_days`: violin plots and one-hot (drop-first) correlations;
numeric vs `is_detractor`: class-conditional KDEs with overlap coefficient and per-feature
ROC-AUC; categorical vs `is_detractor`: mutual information (seed 42); calendar fields treated as
categorical for plots only. One importance ranking per task is produced here for s04 (G-19).
**Human gate (G-31):** implementation stops after s03; every EDA table and figure is presented to
the team in `eda_review_pack.md`, and s04 runs only after the team records its decisions
(cumulative-importance threshold, collinearity drops) in `spec/human_decisions.yaml`.
Missingness, outliers and collinearity among raw numeric features (correlation, VIF). The rank
and condition number of the actual encoded design matrix are computed in s04 (from the recipe)
and s06 (as fitted), not here. Each finding
that motivates a later choice is listed with its evidence.
OUTPUT: figures with sidecar data, target profile tables, per-feature diagnostic tables,
`importance_ranking.csv` per task, `eda_summary.json`, `candidate_rationale.csv` (all under the
stage's `outputs/`, never `artifacts/`).
TEACHING: Tutorials 1–2 and 5; T7–T8 §3; Lecture 5 (multicollinearity).

### s04 — Features (regression, classification; defined, not fitted)
Blueprint: [`blueprints/s04_features.md`](blueprints/s04_features.md)
In order: feature baseline (the 24 predictors of `e5lib/contract.py`, written for this experiment;
`has_items`, `freight_ratio_missing` and `payment_missing` are not in the contract because they
leak a later cancellation or are constant after the population rules: G-30, G-42, G-51, G-61);
calendar fields (`purchase_month`, `purchase_dayofweek`, `purchase_hour`) kept numeric; log1p for
`total_price`, `total_freight`, `total_weight_g`, `total_volume_cm3` and `distance_km_max` when
their pre-cutoff skewness exceeds 1 (never `freight_ratio`, counts, calendar fields, indicators or
0–1 shares; missing values stay missing; G-47, G-62), and for the regression target. **No target cap** (team decision G-25): extreme lead times are
handled by the s02 outlier removal and the log target; feature reduction from the 24 contract predictors to a core set (rule 2 exception, pre-cutoff orders only): constant
and duplicate columns dropped automatically; highly collinear features flagged by pre-registered
cut-offs (|correlation| > 0.9 or VIF > 10) and the team decides which to drop, with the rationale
recorded in `reduction_rationale.csv` and stated in the report (G-26), plus the encoded design-matrix rank and condition number
for each recipe; feature selection by the s03 importance ranking: keep the features that reach
the team's cumulative-importance threshold (95% or 99%), chosen by the team from the ranking
before any model is fitted (rule 2 exception b); rationale and verified citations for every
retained feature; one selected set per task, used by every model family (G-49); `order_estimated_delivery_date` is not
used as a feature or a reference model (G-35: in production the promised date would come from
the task 1 prediction itself); the pipeline recipe per model (imputation with
missing indicators — `distance_km_max` takes the route median, customer_state × primary_seller_state
with customer_state then global fallbacks, after log1p, fitted inside training folds (G-27) — one-hot encoding with unknown handling, scaling for linear/logistic only).
OUTPUT: `feature_dictionary.csv` (formula, grain, availability, missingness, rationale,
citation), `selected_features.json`, recipe table.
TEACHING: Tutorials 3–5; teacher note §3.

### s05 — Partition (regression, classification; depends on s02 only)
Blueprint: [`blueprints/s05_partition.md`](blueprints/s05_partition.md)
Partition strategy against leakage; sort by purchase time and hold out each task's newest 20%
as its test cohort, using the cutoff computed in s02 (exact IDs frozen); remove from the test cohort any order whose customer also appears in
development; check per task that the test cohort keeps at least 15% of eligible delivered orders
(regression) or at least 15% of eligible reviewed orders and of all eligible detractors
(classification) (G-46), and report the train–test prevalence gap (a chronological split is checked,
not stratified). If a check fails, alert the team and stop — never fall back to a random split.
Five time-ordered, expanding CV folds on the development orders (`TimeSeriesSplit` style, n = 5); customer purge (training orders whose `customer_unique_id` appears in
the validation block are removed; no customer on both sides, asserted per fold) and the
anti-temporal-leakage rule (training only earlier than validation, asserted per fold) and label maturity (a label counts only from when it was observable: `lead_days` at delivery,
`is_detractor` at the last review answer; training rows need their label observable before
their fold's validation block starts, validation rows before the task's test cutoff; dropped
rows counted per fold); class support per fold (positives and prevalence; move a boundary if a fold is too
thin); seed 42 documented.
OUTPUT: `folds.csv`, `test_manifest.csv`, `counts.json`, `checks.json` (customer purge, maturity,
share of rows lost to maturity, class support).
Partitioning needs only s02 records, so s05 does not depend on s03–s04; s06 depends on both
s04 (recipes) and s05 (folds).
TEACHING: Tutorial 4 split before preprocessing; T7 reference §4.

### s06 — Training, basic to complex (regression, classification)
Blueprint: [`blueprints/s06_training.md`](blueprints/s06_training.md)
On the s05 folds, every model built as one Pipeline from the s04 recipe: dummy baselines
(median / prior) → plain LinearRegression and unregularised LogisticRegression → single decision
tree → random forest. Residual plots (regression) and learning curves diagnose under- and
over-fitting. All models use the s04 selected feature set with the s04 log transforms always on
(log1p on inputs with pre-cutoff skewness > 1 and on the regression target; G-36), and the
families are compared in order dummy → linear/logistic → tree → forest under the decision rule.
Feature set and transforms are fixed by s04 and not tested on the folds.
OUTPUT: `metrics_long.csv` (train and validation per fold), out-of-fold `predictions.csv.gz`,
diagnostics figures, `decision.json`.
TEACHING: Tutorial 5; T7 §5–6; T8 §5 and §8–9.

### s07 — Tuning: regularise and tune (regression, classification)
Blueprint: [`blueprints/s07_tuning.md`](blueprints/s07_tuning.md)
Bounded grids on the same folds. Linear family: Ridge alpha and logistic C (regularisation
strength). Tree family and forest: depth and minimum leaf size (same grid).
Grids fixed before any result (blueprint s07). Best per family = simplest configuration within
one standard error of the best mean (s01 rule), kept only if it beats the family's plain s06 model. Class weight (None vs balanced) is a grid option for the
classifiers. Every grid candidate is a whole pipeline; nothing is switched after the search.
OUTPUT: `grid_results.csv` (every configuration, fold scores, mean, SD, rank, runtime,
convergence), finalists' out-of-fold predictions.
TEACHING: T7–T8 GridSearchCV.

### s08 — Selection, policy and test once (regression, classification)
Blueprint: [`blueprints/s08_selection.md`](blueprints/s08_selection.md)
Select the model first on threshold-free scores (MAE; AP, ROC-AUC, Brier), comparing finalists
with the dummy and the simplest model of each family on the same rows. The s01 one-SE rule gives
the recommendation; the team confirms it at a human gate, and resolves any grid-edge winner by
widening the grid (change request) or revisiting s03–s04 (G-39). Classification only:
calibration is a candidate component, raw by default. If the out-of-fold reliability check fails,
a sigmoid-calibrated variant (calibrator fitted inside each training fold on time-ordered inner
splits) is scored as a complete candidate on the same folds; the chosen probability recipe is the
one persisted. Then choose the threshold from that recipe's out-of-fold predictions under the 5:1
cost (compare no alerts, 0.50, the theoretical cost cutoff 1/6 and the empirical optimum). This
is a hard stop: the team picks the threshold from a table of alert volume, error rate and extra
false alarms per extra detractor caught, with an optional daily alert cap (G-39). Freeze the
recipe and threshold, then fit on the development orders whose labels were available before the
test cutoff (final-fit label maturity) and score each task's test cohort
exactly once.
Test metrics (G-24): regression MAE, RMSE, R², share within ±3 days; classification AP (= PR-AUC,
reported once), ROC-AUC, Brier, confusion matrix, precision, recall and F1 at the threshold,
illustrative cost, and the prevalence baseline. The bundle also stores training-data metadata
for drift checks (numeric distributions; category shares).
OUTPUT: `selection_review_pack.md`, `selected_spec.json`, `threshold_table.csv`, `frozen_recipe.json`, model bundle (with
`training_profile.json`),
test `metrics_long.csv` and predictions.
TEACHING: T7 reference §6–9.

### s09 — Conclusion for the business (regression, classification)
Blueprint: [`blueprints/s09_conclusion.md`](blueprints/s09_conclusion.md)
Train–validation–test table with bootstrap confidence intervals; subgroup errors (regression by
customer state, distance, basket, month; classification by customer state, judged only where the
test cohort has more than 100 detractors, with a pooled aggregate) and training-vs-test drift;
interpretation of the winner (permutation importance on the selected model, tree rules,
coefficients and odds ratios of the plain models) with an EDA consistency check that alerts the
team on divergence and never changes the frozen pipeline (G-40);
stakeholder actions supported by the evidence, and limitations. The test cohort is the held-out test of this experiment, scored once in s08.
OUTPUT: master metric table, `subgroups.csv`, drift table, importance and interpretation tables,
`conclusion.md`.
TEACHING: T7 reference §10; T2 confidence intervals; teacher note §5–6.

### s10 — Release: migrate and deliver (common)
Blueprint: [`blueprints/s10_release.md`](blueprints/s10_release.md)
Saved bundle with reload parity; team approval of the experiment; migration to the working
folders with a reproduction README (README §12, ordered by the experiment lead); reproduction
check that every output and number matches the release; then one Streamlit app with three tabs
(the Phase 1 business dashboard on its own descriptive data scope, and lead-time and detractor-risk
model tabs that read only pipeline outputs; G-41),
the report and slides built from the reproduced outputs, the walkthrough notebook, and input
checks with error handling in the app.
OUTPUT: `parity.json`, `input_validation.json`, `app_sources.json`, release tag, migration check, app,
report and deck drafts that cite evidence IDs, notebook.
TEACHING: Week 6 deployment slides; T7 reference §11–14; brief Phase 3.

## Changes from Milestone 2

**Dropped:** two training cycles (now one ladder in s06); customer-grouped CV screening beside
chronological confirmation (now chronological folds only); a separate confirmation window (CV
plus one test, as in Tutorials 7–8); starting from 9 features (now the 24-predictor contract, G-61,
reduced and selected by the EDA ranking in s04, one set per task used by every model); the 60-day target cap applied outside tuning and
justified by Cook's distance (no cap now; extreme values handled by the s02 outlier rule).

**Corrected:** stakeholders named but not their actions; test-boundary customer purge and
final-fit label maturity kept from Milestone 2 and written into s05/s08; label rule without sensitivity check;
`order_estimated_delivery_date` misclassified; three untraceable citations (verify or drop);
several preprocessing builders and post-search switches (one recipe per model, fitted in folds);
dummies drawn from separate evidence (now fitted on the same folds); tuning on different folds
from selection; calibration from a separate grouped study; two threshold stories (0.17 vs
0.1822); importance explaining a non-selected model; recommendations beyond the evidence; numbers
typed by hand.

**Added:** outcome trends over time and feature–target relationships in EDA; plain linear and
logistic baselines; residuals and learning curves; class weight as a tuning option; the
train–validation–test table with confidence intervals (validation
labelled as selection scores); dashboard and app with input checks;
approval, migration and reproduction check before any deliverable is built.

## Decisions recorded in `protocol.yaml`, not in this design

Two layers (see s01). Data-dependent: exact fold boundaries, class-support threshold, minimum training rows per fold (G-53) and the
label-maturity rule for validation rows (s05); core set and selected set (s04).
Pre-registered (s01): the decision rule for
keeping a more complex variant (one-standard-error rule: the simplest candidate whose mean
primary metric is within one standard error of the best, G-33); grids and budget; the label rule; seed; the 80/20 split rule.

## Report and presentation structure (brief Phase 3)

Executive summary → problem and stakeholder (s01) → dataset and preprocessing (s02) → EDA
highlights (s03) → features (s04) → validation design (s05) → modelling, basic to complex (s06–s07)
→ selection, policy and results (s08–s09) → deployment and application (s10) → business
recommendations, limitations → references. Every number cites an evidence ID from the reproduced
outputs.

## Appendix — Milestone 2 pipeline (reference only)

Milestone 2 framed the same two tasks; built order-level data from seven tables; used
customer-grouped development folds for screening and tuning; reduced 27 candidate features to a
9-feature core and expanded to 11 (regression) and 12 (classification) in a second cycle; tuned
Ridge, logistic C, trees and 50-tree forests; applied input and target log1p and a 60-day target
cap outside tuning; ran separate grouped calibration and cost studies; confirmed only the
selected forests on five chronological expanding windows; froze a 0.17 threshold; and scored the
terminal cohort starting 2018-05-25. Its code and artifacts (`src/`, `artifacts/`,
`experiments/experiment_3/`) are reference only.
