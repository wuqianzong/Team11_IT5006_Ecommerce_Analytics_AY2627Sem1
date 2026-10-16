<!-- AUTHORITATIVE Milestone 3 / Experiment 5 pipeline design. This file is the only version
     that counts; edit it here (and mirror changes in spec/stages.json, README §3.1).
     Origin: content identical to docs/milestone3_baseline_pipeline_design_2026-10-13.txt as of
     2026-10-16 (only headings converted to Markdown). That docs/ file is superseded and is
     not updated. After the design freeze, changes go through README §9.2 and CHANGELOG.md. -->

# Milestone 3 baseline pipeline design
13 October 2026 — design only; no training or implementation changes

PURPOSE
Rebuild the Milestone 2 modelling workflow as a coherent baseline for the final report, presentation and deployed application. Retain Olist, the two checkout prediction problems, the leakage exclusions, the nine-feature core, task-specific expansions and two model families. Improve the evaluation design and evidence chain rather than introduce unrelated algorithms. No target score, winning model or threshold is assumed in advance.

SOURCES AND STATUS
Directly reviewed: Tutorials 1, 2, 3, 4, 5, T07_Main, Tutorial 7 non-agentic reference solution, Tutorial 8, Week 6 deployment slides, the project brief, teacher expectations and current model/experiment source. There is no separately named Tutorial 6 notebook in the supplied tutorial folder; the supplied Week 6 training/deployment material provides that part of the mapping.
This is an adaptation of taught principles to chronological, repeated-customer Olist data. The tutorials' random/stratified teaching splits are not copied literally where that would break chronological prediction. Nested CV, an ensemble or every taught algorithm is not mandatory for this project.

## A. CURRENT MILESTONE 2 PIPELINE

### A1. Frame two checkout tasks and build order-level data.
- Regression: delivery minus purchase timestamp, fractional days; logistics stakeholder; MAE primary, RMSE/R2 secondary.
- Classification: recorded review score <=2; CX/support stakeholder; AP primary, ROC-AUC/Brier and threshold decisions secondary.
- Join seven tables; use customer_unique_id for group isolation; quarantine outcome-derived predictors.

### A2. Outer customer-group split and task eligibility.
- Saved development/holdout manifests and five customer-grouped development folds.
- Classification removes zero-item orders and has_items/freight_ratio_missing predictors.
- Chronological fitting later restricts pre-terminal training, purges customers and checks label maturity. Terminal dates start on2018-05-25.

### A3. Development EDA and collinearity diagnostics.
- Distribution/tail diagnostics and an outlier-treatment study.
- Candidate27-feature correlations/design rank; define9-feature core.
- These are descriptive/diagnostic calculations; their encoded matrix is not necessarily the final estimator's matrix.

### A4. Nine-feature grouped-CV family benchmarks.
- Ridge, logistic(C=.01), simple trees and starter forests; dummy references drawn from separately saved baseline evidence.
- This selected evidence does not begin with matched plain OLS and unregularized logistic variants.

### A5. Task-specific expansion and diagnostic importance.
- Regression:9 ->11 via maximum distance and distance-missing fraction.
- Classification:9 ->12 via seller count, primary seller state and interstate share.
- Grouped CV compares subsets; permutation diagnostics describe a tree regressor and logistic classifier.

### A6. Transformations and grouped hyperparameter search.
- Input log1p and regression target log1p; search Ridge alpha, logistic C, tree depth/leaf and forest depth/leaf; forest50 trees.
- Grouped-search preprocessing one-hot encodes calendars and scales numeric columns.
- Regression target cap60 is not included in that tuning fit.
- Historical and filtered classification tuning evidence are separately available in the current reproduction package.

### A7. Separate grouped probability-calibration/cost studies.
- Raw versus sigmoid calibration and illustrative FP:FN costs1:1,1:5,1:10.
- This is a separate grouped study, not the chronological selected-pipeline OOF calculation.

### A8. Selected-model chronological confirmation and final fitting.
- Fixed forest architecture receives five expanding-window confirmations with customer purging and label maturity.
- Final preprocessing uses numeric calendars, forest-specific encoding/scaling choices and a regression60-day target cap.
- Only selected models get this chronological CV; other final references are fitted for terminal comparison.
- Chronological OOF yields an empirical threshold; deployment threshold remains configured0.17.

### A9. Terminal evaluation, diagnostic tables, persistence and scoring.
- Fit pre-terminal eligible training; serialize models and metadata.
- Score common terminal task cohorts; compare final references, decisions and79subgroups; audit distributions.
- Current notebook is an evidence/scoring walkthrough. Bare terminal command is no-fit verification; separate build command retrains.

## B. WHAT TO CHANGE IN THE DESIGN

1. One primary validation protocol from the first learning model onward. Do not compare a grouped screening score with a chronological score as a model improvement.
2. Matched dummy, plain linear/logistic and single-tree baselines before regularization/forest complexity. The teacher explicitly requests simplest variants.
3. Split and reserve evaluation membership before target-driven feature/model choices or learned preprocessing. Row-local deterministic joins/formulas can precede the split; learned imputation, encoding, scaling and data-derived thresholds cannot.
4. Treat feature set, numeric/categorical representation, imputation, transformations, target cap and estimator as one candidate pipeline. The winning candidate is exactly the pipeline subsequently confirmed, refitted and deployed.
5. Compare interventions separately before combining them. More complexity or a cap is accepted only if development evidence supports it.
6. Assess probability calibration before choosing an operating threshold, and make one explicit policy decision before final evaluation. Avoid competing threshold stories.
7. Provide a confirmation stage that was not used for tuning in this run. Do not perform its evaluation and then go back and change the selected model while retaining the same confirmation claim.
8. Generate model comparisons, report tables, captions, plots and deployed model information from one versioned evidence registry.

## C. PROPOSED TEXTBOOK PIPELINE

### STAGE0 — Freeze the analysis questions and decision criteria.
Keep both Milestone2 targets and checkout time. Define eligible populations, positive class1, excluded post-outcome columns, stakeholders, metrics and illustrative FN5/FP1 assumption. State scope: predictions describe observed delivered/reviewed orders with available cart inputs. Do not claim a measured intervention ROI.
Choose simplicity preference/tie handling and search budget before results. Use only linear and tree-based families, plus dummy references. No mandatory boosting, voting, stacking, NB or resampling.
OUTPUT: problem/target/feature contract and evaluation protocol.
TEACHING: problem scoping; Tutorials1–2; teacher notes.

### STAGE1 — Construct and validate deterministic checkout records.
Reuse the existing joins, targets and checkout features; audit keys, join cardinalities, units, duplicate review aggregation and target-availability timestamps. Define freight_ratio consistently. Apply zero-item classification eligibility before constructing any classification comparison. Retain IDs for audit, never as predictors.
Deterministic invalid-value checks and row-local formulas do not learn from held-out distributions. Any learned missingness or outlier treatment belongs inside later folds.
OUTPUT: versioned raw feature/target table, exclusions and data hashes.
TEACHING: Tutorials1–3 and leakage guidance.

### STAGE2 — Freeze partitions, customer isolation and label maturity.
Retain the existing Milestone2 terminal cohort IDs as a historical comparison benchmark. Keep all originally held-out IDs out of development; do not silently reclaim earlier held-out rows or future development rows as extra training data. Reuse validated chronological pre-terminal membership where compatible, otherwise explicitly version changed membership.
Use the earlier four expanding windows for development selection and the last pre-terminal window for confirmation. The confirmation interval is approximately2018-03-08 to2018-05-25 using the existing boundaries; exact timestamps and row IDs must be frozen.
At every fit origin, training outcomes must have become available before that origin; purge training customers belonging to validation. All candidate pipelines share exactly the same task-specific rows and folds. Task eligibility can differ between regression and classification.
If selection is frozen at confirmation start, selection-study labels must be available by that date. Confirmation labels are assessed with a predeclared follow-up/as-of rule. Record exclusions and resulting population limitations rather than using future-known training outcomes.
Chronological ordering takes priority over randomized stratification; check both classes, fold prevalence and sample support without rearranging future orders to balance classes. If a fold lacks support, revise boundaries before fitting.
These chronological windows have also been examined in prior work. Reserving the last window now makes it a confirmation not used for selection in the new run, not a newly blind dataset. The existing terminal cohort has already been examined: it remains a historical benchmark, not a newly untouched test. A genuinely fresh independent test requires genuinely unexamined data. Do not manufacture one by reshuffling examined records.
OUTPUT: selection/confirmation/benchmark manifests, class counts, availability and group-overlap checks.
TEACHING: Tutorial4 split-before-preprocessing; Tutorials7–8 protected evaluation; Olist adaptation.

### STAGE3 — Question-driven EDA on selection data.
Summarize missingness, counts, prevalence, raw lead-time distribution, seasonality, geographic/basket relationships and feature-target associations. Examine constants, correlation and the actual linear design's numerical rank. Explain legitimate long deliveries versus invalid records.
Use this to propose a small declared set of changes. Do not fit preprocessing on all development and feed that fitted transform into CV. Do not choose variables/caps from confirmation or terminal labels.
OUTPUT: population-labelled EDA, candidate rationale table and short hypotheses.
TEACHING: Tutorials1–3/5/7–8.

### STAGE4 — Build one canonical pipeline factory and matched simplest baselines.
Start with the existing9core raw features, raw regression target and unweighted classification.
Fit median DummyRegressor and prior DummyClassifier on each training fold. Fit plain LinearRegression, plain unregularized LogisticRegression and a documented simple single tree for both tasks. The tree's depth/leaf settings are explicit starting settings, not claimed library defaults.
Use the same data representation rules throughout selection, confirmation and final fit: for continuity with the final Milestone2 representation, calendars begin as numeric; state codes are categorical. Impute inside folds; one-hot encode states with unknown handling; scale numeric features for linear/logistic models, not as an unexplained later change. Use drop-first for intercept-based linear models; forest state encoding can use all levels if consistently declared in its family template. Diagnose the actual fitted matrix; do not inherit a condition number from a different encoding.
Logistic penalty=None is the plain baseline; Ridge and finite-C logistic are subsequent regularized variants. Record solver, convergence and seed42.
OUTPUT: per-fold training/validation metrics, counts, predictions and simplest-family comparison.
TEACHING: Tutorials3/5/7–8; project brief simplest-family baseline requirement.

### STAGE5 — Diagnose baselines, then test targeted features.
Generate regression residual-versus-fitted, residual distribution and Q–Q diagnostics from development validation predictions; inspect state/distance/basket errors. For classification inspect AP/PR, ROC, Brier, prevalence and probability reliability; avoid an accuracy-only assessment.
Compare9core with11regression/12classification inputs, holding estimator settings and preprocessing rules fixed. Feature additions are deterministic checkout formulas; any empirical feature selector is fit inside training folds.
Compute task-specific permutation diagnostics on validation rows and identify the model they explain. Do not use a tree/logistic importance plot as the final forest's interpretation.
OUTPUT: paired same-fold feature comparisons and diagnostic rationale.
TEACHING: Tutorials1–2/5/7–8.

### STAGE6 — Controlled transformations and complexity progression.
For regression compare raw target, log1p target, and log1p plus fixed60-day training-target cap. Test input logs separately so target and predictor effects can be distinguished. Evaluate all variants against original, uncapped validation lead_days. If estimating a percentile cap instead, estimate it only in each training fold. Do not automatically remove true long deliveries.
Within the linear family compare plain models with Ridge/finite-C logistic. Within the tree family compare the documented simple tree, tuned/pruned tree and starter forest. Introduce the forest after the single-tree baseline; compare it on the same feature set and folds.
Changes are candidates, not guaranteed improvements. Retain the simpler/raw alternative if a complex variant fails the declared decision rule.
OUTPUT: intervention/ablation table with unchanged and changed components, per-fold deltas and decisions.
TEACHING: Tutorials3/5/8; teacher complexity guidance.

### STAGE7 — Bounded tuning of COMPLETE pipelines.
Tune only promising variants on the selection folds. Initial bounds can reuse Milestone2: Ridge alphas .01,.1,1,10,100,500; logistic C .001,.01,.1,1,10; tree depths4,6,8,10 and leaves20,50,100,200; forest depths6,10,14 and leaves20,50 with50trees. Pruning can use a small declared ccp_alpha grid if baseline diagnostics justify it.
Every grid candidate includes its feature set, preprocessing and regression target treatment. No post-search switch from categorical to numeric calendars, new target cap, changed cohort or other untested configuration. If a component changes, it is a new development comparison.
Save every configuration's parameters, fold training/validation scores, means, sample SD, rank, runtime and convergence. Keep pooled OOF AP distinct from mean-fold AP. Scores used for selection are selection scores, not an independent performance estimate.
Compare the winner to dummy and simplest-family alternatives on identical selection rows. Freeze the model recipe provisionally; do not force the forest to win because it won Milestone2.
OUTPUT: complete grid tables, selected full pipeline and decision record.
TEACHING: Tutorials7–8 and brief; grid search is optional in some tutorial cells but is an appropriate bounded continuation of Milestone2.

### STAGE8 — Interpretation, calibration and operating policy BEFORE confirmation.
Run learning curves using deterministic nested customer-group subsets within training windows, with the same validation rows. Record actual sizes and class support; use train/validation gaps descriptively. Export rules from the actual simple tree and final-model validation permutation importance.
Inspect selected classifier OOF calibration. Raw is the initial probability model. If testing sigmoid calibration, train its calibrator only inside the outer training population using chronology/group-respecting internal splits; assess its outer validation outputs as a complete candidate. Choose it only with documented AP/Brier/business trade-offs. No terminal-label calibration.
Freeze the chosen probability recipe, then choose an operating threshold from its selection OOF predictions using the declared costs/capacity. Compare no alerts, exact .50, legacy .17 and the empirical development optimum. Include exact .50 explicitly; do not substitute the nearest grid point. The theoretical calibrated FP1/FN5 cutoff1/6 is a check under those assumptions, not proof an empirical score is calibrated or a measured business optimum.
Use a deterministic threshold/tie rule; record counts, precision, recall, F1, alerts and illustrative cost. Neither .17 nor the forest is predetermined. Selection OOF reused for this decision is not independent evaluation of the selected policy.
OUTPUT: full decision artifact specification (pipeline/calibrator/threshold/cost assumptions) and diagnostics.
TEACHING: Tutorial7 reference solution §§7–8/10–11; Tutorial8 diagnostics.

### STAGE9 — Chronological confirmation of the frozen method.
Fit the frozen recipes on the training population available at confirmation start and evaluate the reserved pre-terminal confirmation window. Include dummy and frozen plain-linear/simple-tree comparisons on the identical confirmation rows, not just the selected forest.
Assess model improvement and the frozen policy without changing them from confirmation results. If a material issue triggers another development iteration, retire that confirmation's independent role and document the reopened selection; never silently tune against it.
OUTPUT: matched baseline/selected confirmation table, curve/error analyses and accept/reopen decision.
TEACHING: Tutorials4/7–8 evaluation discipline; project-specific temporal extension.

### STAGE10 — Final refit and historical benchmark evaluation.
After confirmation, refit the unchanged recipe on all eligible pre-terminal development training whose outcomes are available at the final fit cutoff. Refit learned components using their declared training-only rules; retain the frozen threshold. Persist the complete probability/calibration construction if adopted, not just an underlying forest.
Score the fixed Milestone2 terminal benchmark once for this frozen release and do not use those outcomes for model/policy changes. Produce matched reference comparisons, train/validation/confirmation/benchmark tables with distinct denominators, threshold confusion counts, subgroup support and limitations. Do not call old benchmark data newly unseen or silently compare a4-fold mean with Milestone2's5-fold mean as if they were identical estimands.
If later refitting for production uses benchmark-labelled data, that creates a separately versioned deployment model and does not inherit this release's benchmark score. For this baseline, retain the evaluated pre-terminal-fit artifacts for deployment.
OUTPUT: final release's benchmark metrics/predictions and evaluation manifest.
TEACHING: Tutorials7–8 final fitting/evaluation; brief.

### STAGE11 — Persist, reload, validate and deploy the SAME artifact.
Save pipeline, optional calibrator, threshold, feature schema, positive-class mapping, versions, seeds, training-ID digest and checksums. Verify in-memory versus reloaded prediction parity; validate single/batch inputs, missing values, invalid values, unknown states and eligibility. Inference never fits or optimizes.
For Milestone3, a small Streamlit application loading the frozen bundles is sufficient; FastAPI is optional, not mandatory. Prefer two task tabs, or at least one deployed task as required by the brief. Show estimated delivery days and detractor probability/alert with plain explanations and input constraints. Use held-out historical records to simulate incoming orders; a live order feed is not required. Benchmark latency only if reporting a measured latency claim.
OUTPUT: versioned bundles, QA results, application URL/instructions and demonstration screenshots.
TEACHING: Tutorial8 persistence; Week6 training/deployment/bulk scoring.

### STAGE12 — Generate the final report and presentation from the evidence registry.
Every table, plot and numeric statement resolves to a run ID, task, cohort, phase, candidate, metric definition and source artifact. Preserve row-level/fold data in the appendix/repo; main text carries decisions, reasons, minimal supporting comparisons and limitations.
Tell one progression: simplest baselines -> diagnosed weaknesses -> targeted interventions -> bounded tuning -> probability/policy decision -> confirmation -> final evaluation -> stakeholder application. Show rejected changes where they explain a choice. Do not require performance to improve monotonically or promote correlations to causal impact.
Generate one report-ready master metric table and chart coordinates; make report/slide/UI values use that same source. Validate positive class, fractions/percentages, units, rounding and threshold definitions before locking the release.
OUTPUT: report-ready baseline package, presentation story and executable reproduction guide.
TEACHING: Tutorials1–2 communication; Week6 application; Phase3 integration requirements.

## D. PRACTICAL EXECUTION CONTRACT

- Design now; implement in a separate Milestone3 version only after this design is accepted. Preserve submitted Milestone2 files and fitted artifacts.
- Reuse raw data, join/feature formulas, eligibility rules, customer identity handling, chronology/group/maturity helper logic, baseline/tuning ranges and deployment scoring interface where appropriate.
- Replace separate inconsistent preprocessing builders with one factory; regenerate results after material protocol changes. Never carry forward a metric because the model name or feature count matches.
- If budget is tight, retain prior justified feature sets rather than rerun27-feature exploration; prioritize matched plain baselines, exact full-pipeline comparisons, final policy and deployment parity.
- Minimum release evidence: contracts; membership; fold/cohort counts; baseline/ablation/full-grid tables; OOF predictions; selected-pipeline diagnostics; policy; confirmation comparisons; final benchmark predictions/subgroups; complete bundles; report-to-evidence registry.
- No guaranteed AP/MAE improvement and no assumed unchanged winner. The deliverable is a defensible, reproducible baseline with a clear decision path.

## E. REPORT/PRESENTATION STRUCTURE
Problem and user -> dataset/checkout contract -> partition/validation diagram -> simple baselines -> EDA/diagnostic motivation -> feature/target/model interventions -> matched selection and policy -> confirmation and benchmark results -> live application -> limitations and next steps.
The two cycles can remain as labels for narrative clarity: Cycle1 establishes the simplest matched baseline; Cycle2 evaluates targeted improvements. Both use the same task eligibility, pipeline factory, validation definitions and evidence format. They are two iterations of one pipeline, not unrelated experiments stitched together.
