<!-- AUTHORITATIVE Milestone 3 / Experiment 5 pipeline design. This file is the only version
     that counts; edit it here (and mirror changes in spec/stages.json, README §3.1).
     v1.0 FROZEN 2026-10-17 by the team (CHANGELOG CR-001); v1.1 audit fixes (CR-003). It replaces the 13-stage draft
     derived from docs/milestone3_baseline_pipeline_design_2026-10-13.txt, which is superseded
     and not updated. After this freeze, changes go through README §9.2 and CHANGELOG.md. -->

# Milestone 3 baseline pipeline design — v1.1 (frozen 2026-10-17, audit fixes CR-003)

## Purpose

One clean, end-to-end pass from problem statement to business conclusion, in the textbook
order taught in Tutorials 1–8, for the two Milestone 2 checkout tasks on Olist:

- **Regression** — delivery lead time (purchase to delivery, fractional days); logistics stakeholder.
- **Classification** — recorded low review (score ≤ 2, positive class 1); customer-experience stakeholder.

Every Milestone 2 method is kept, but moved into this single flow; what Milestone 2 got wrong
is corrected and what it lacked is added (see "Changes from Milestone 2" below). There is **one
training cycle**, not two. No target score, winning model, feature set, cap value or threshold
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
   One declared exception: the s04 reduction from 27 features to a core set uses label-free
   structural checks (correlation, VIF, constant or duplicate columns) computed once on
   orders before the test cutoff. It never sees labels or test rows; it is pre-registered as a fixed rule
   and reported as a limitation, not presented as fold-fitted.
3. **Test cohorts protected.** Each task has its own test cohort: the Milestone 2 terminal
   cohort for that task (purchase on or after the frozen cutoff, 2018-05-25; classification also
   excludes zero-item orders), exact IDs frozen in s05. Development orders from customers who
   appear in a test cohort are removed (test-boundary customer purge, as in Milestone 2).
   Steps s03–s04 use only orders before the test cutoff (date rule; the purge, applied in s05,
   matters for model fitting); no step reads test labels until the final evaluation in s08.
4. **Honest estimates.** CV scores are selection scores, used to choose and reported as such,
   never as a generalisation estimate. The test cohorts give the only held-out estimate; they
   were scored in Milestone 2, so they are described as historical held-out tests, not unseen
   data.
5. **Simplest first, one change at a time.** A more complex variant is kept only if it passes the
   decision rule in `protocol.yaml`; otherwise the simpler one stays.
6. **Every number comes from a stage output.** Report, slides, app and dashboard read the same
   evidence; nothing is typed by hand.
7. **Claims are labelled** as observation, literature-supported hypothesis, or unmeasured
   mechanism.

## The ten stages

Each stage links to its detailed blueprint (index: [`blueprints/README.md`](blueprints/README.md)).

### s01 — Problem statement (common)
Blueprint: [`blueprints/s01_problem.md`](blueprints/s01_problem.md)
Two tasks at checkout (prediction time = `order_purchase_timestamp`); stakeholder and the action
they take (who sees which prediction, when, and what they do); targets and label rules
(minimum-review label with a first-review sensitivity check); metrics (MAE primary, RMSE/R²
secondary; AP primary, ROC-AUC/Brier/precision/recall/F1 secondary) and the illustrative
FN:FP = 5:1 cost; model families (dummy references, linear/logistic, tree/forest); decision
rule and tie-breaks; search budget; seed 42; test cutoff. `spec/protocol.yaml` has two layers:
(a) **pre-registered** values fixed here before any data is seen (tasks, metrics, cost, decision
rule, families, grids, budget, seed, test cutoff); (b) **data-dependent** values, each owned by
one stage and frozen at that stage's gate, before any model result: the core set and candidate
sets and cap candidates (s04), fold boundaries and class-support threshold (s05). Moving a fold
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
at checkout (Milestone 2 wrongly listed it as post-checkout); zero-item orders are excluded from
classification. IDs are kept for audit, never as predictors.
OUTPUT: `records.csv.gz`, `exclusions.csv`, `data_hashes.json`, `audit.json` (joins, grains,
leakage, label sensitivity).
TEACHING: Tutorial 3; T7 reference §3; brief leakage warning.

### s03 — EDA (regression, classification; pre-cutoff orders only)
Blueprint: [`blueprints/s03_eda.md`](blueprints/s03_eda.md)
Question-driven, before the test dates: target shape and tails; outcome trends over time
(lead time, late rate, detractor rate, not volume only); feature–target relationships;
missingness, outliers and collinearity among raw numeric features (correlation, VIF). The rank
and condition number of the actual encoded design matrix are computed in s04 (from the recipe)
and s06 (as fitted), not here. Each finding
that motivates a later choice is listed with its evidence.
OUTPUT: figures with sidecar data, `eda_summary.json`, `candidate_rationale.csv`.
TEACHING: Tutorials 1–2 and 5; T7–T8 §3; Lecture 5 (multicollinearity).

### s04 — Features (regression, classification; defined, not fitted)
Blueprint: [`blueprints/s04_features.md`](blueprints/s04_features.md)
In order: feature baseline (the 27 Milestone 2 candidate features); log transforms of skewed
inputs and of the regression target, plus a **target-cap step whose value is not fixed here**
(candidate values, including "no cap", are declared in `protocol.yaml` and chosen on the folds in
s06; scoring always uses uncapped days); feature reduction from 27 to a core set by the
pre-registered label-free rule (rule 2 exception: correlation, VIF, constant or duplicate
columns, on pre-cutoff orders only), plus the encoded design-matrix rank and condition number
for each recipe; rationale and verified citations for every retained
feature; candidate feature sets for each model; a decision on
`order_estimated_delivery_date` (known at checkout, absent from the 27 baseline): recommended as
an added candidate feature (promised lead days) tested on the folds in s06, and as a business
reference for regression (Olist's own promise); the pipeline recipe per model (imputation with
missing indicators, one-hot encoding with unknown handling, scaling for linear/logistic only).
OUTPUT: `feature_dictionary.csv` (formula, grain, availability, missingness, rationale,
citation), candidate sets per model, recipe table.
TEACHING: Tutorials 3–5; teacher note §3.

### s05 — Partition (regression, classification; depends on s02 only)
Blueprint: [`blueprints/s05_partition.md`](blueprints/s05_partition.md)
Partition strategy against leakage; hold out each task's test cohort (exact IDs frozen) and
remove development orders from customers who appear in that test cohort; chronological
expanding CV folds on the development orders; customer purge (training customers who appear in
validation are removed) and label maturity (training outcomes available before each fold
origin); class support per fold (positives and prevalence; move a boundary if a fold is too
thin); seed 42 documented.
OUTPUT: `folds.csv`, `test_manifest.csv`, `counts.json`, `checks.json` (overlap, maturity,
share of rows lost to maturity, class support).
Partitioning needs only s02 records, so s05 does not depend on s03–s04; s06 depends on both
s04 (recipes) and s05 (folds).
TEACHING: Tutorial 4 split before preprocessing; T7 reference §4.

### s06 — Training, basic to complex (regression, classification)
Blueprint: [`blueprints/s06_training.md`](blueprints/s06_training.md)
On the s05 folds, every model built as one Pipeline from the s04 recipe: dummy baselines
(median / prior) → plain LinearRegression and unregularised LogisticRegression → single decision
tree → random forest. Residual plots (regression) and learning curves diagnose under- and
over-fitting. Comparison order, so every change has one cause: (A) on the core set with raw
target and inputs, compare the families dummy → linear/logistic → tree → forest; (B) within each
family, holding the model fixed, compare candidate feature sets, then input logs, then the
target transform and cap candidates (regression), one at a time, each kept only if it passes the
decision rule. Both steps use the same folds.
OUTPUT: `metrics_long.csv` (train and validation per fold), out-of-fold `predictions.csv.gz`,
diagnostics figures, `decision.json`.
TEACHING: Tutorial 5; T7 §5–6; T8 §5 and §8–9.

### s07 — Tuning: regularise and tune (regression, classification)
Blueprint: [`blueprints/s07_tuning.md`](blueprints/s07_tuning.md)
Bounded grids on the same folds. Linear family: Ridge alpha and logistic C (regularisation
strength). Tree family: depth and minimum leaf size (and pruning if diagnostics justify it).
Forest: depth and leaf size. Class weight (None vs balanced) is a grid option for the
classifiers. Every grid candidate is a whole pipeline; nothing is switched after the search.
OUTPUT: `grid_results.csv` (every configuration, fold scores, mean, SD, rank, runtime,
convergence), finalists' out-of-fold predictions.
TEACHING: T7–T8 GridSearchCV.

### s08 — Selection, policy and test once (regression, classification)
Blueprint: [`blueprints/s08_selection.md`](blueprints/s08_selection.md)
Select the model first on threshold-free scores (MAE; AP, ROC-AUC, Brier), comparing finalists
with the dummy and the simplest model of each family on the same rows. Classification only:
calibration is a candidate component, raw by default. If the out-of-fold reliability check fails,
a sigmoid-calibrated variant (calibrator fitted inside each training fold on time-ordered inner
splits) is scored as a complete candidate on the same folds; the chosen probability recipe is the
one persisted. Then choose the threshold from that recipe's out-of-fold predictions under the 5:1
cost (compare no alerts, 0.50, the Milestone 2 value 0.17 and the empirical optimum). Freeze the
recipe and threshold, then fit on the development orders whose labels were available before the
test cutoff (final-fit label maturity, as in Milestone 2) and score each task's test cohort
exactly once.
OUTPUT: `selected_spec.json`, `threshold_table.csv`, `frozen_recipe.json`, model bundle,
test `metrics_long.csv` and predictions.
TEACHING: T7 reference §6–9.

### s09 — Conclusion for the business (regression, classification)
Blueprint: [`blueprints/s09_conclusion.md`](blueprints/s09_conclusion.md)
Train–validation–test table with bootstrap confidence intervals; subgroup errors (state,
distance, basket) and training-vs-test drift; interpretation of the winner (permutation
importance on the selected model, tree rules, coefficients and odds ratios of the plain models);
stakeholder actions supported by the evidence, and limitations. The test cohort is described as a
historical held-out test (Milestone 2 already scored it), not unseen data.
OUTPUT: master metric table, `subgroups.csv`, drift table, importance and interpretation tables,
`conclusion.md`.
TEACHING: T7 reference §10; T2 confidence intervals; teacher note §5–6.

### s10 — Release: migrate and deliver (common)
Blueprint: [`blueprints/s10_release.md`](blueprints/s10_release.md)
Saved bundle with reload parity; team approval of the experiment; migration to the working
folders with a reproduction README (README §12, ordered by the experiment lead); reproduction
check that every output and number matches the release; then the Streamlit app and dashboard,
the report and slides built from the reproduced outputs, the walkthrough notebook, and input
checks with error handling in the app.
OUTPUT: `parity.json`, `input_validation.json`, release tag, migration check, app and dashboard,
report and deck drafts that cite evidence IDs, notebook.
TEACHING: Week 6 deployment slides; T7 reference §11–14; brief Phase 3.

## Changes from Milestone 2

**Dropped:** two training cycles (now one ladder in s06); customer-grouped CV screening beside
chronological confirmation (now chronological folds only); a separate confirmation window (CV
plus one test, as in Tutorials 7–8); starting from 9 features (now the 27-feature baseline,
reduced in s04 and chosen per model in s06); Cook's distance as the reason for a 60-day cap (the
cap value is now chosen on the folds).

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

Two layers (see s01). Data-dependent: exact fold boundaries, class-support threshold and the
label-maturity rule for validation rows (s05); core set, candidate sets and cap candidates (s04).
Pre-registered (s01): the decision rule for
keeping a more complex variant (proposed: mean paired per-fold delta favours it and the sign
agrees in most folds); grids and budget; the label rule; seed; test cutoff.

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
