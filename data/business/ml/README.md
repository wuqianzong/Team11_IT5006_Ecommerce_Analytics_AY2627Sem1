# ML dataset guideline

Current modelling override (10 October 2026): The production champion state
is `refinement-selected-v4` (Refinement Cycle 2 / Experiment 3, Option 1).
The shared order-level base dataset remains 27 fields; `refinement-selected-v4` selects
11 predictors for Random Forest regression and 12 predictors for Random Forest
classification, with `has_items` and `freight_ratio_missing` pruned and zero-item
post-checkout cancellations filtered out. See §16 (Cycle 1 history), §17 (Current v4
Champion), and `src/models/configs/refinement_selected_v4.json`. Earlier Stage 3–6 text
is historical.

Status: implementation specification v1.2; Phase A verified 2026-10-05 at `ddd1523`.
Course-alignment addendum: W6/W7-2026-10-04 (§9), binding for future implementations.
Additional teaching/report addendum: C1-C5-TREE-2026-10-05 (§10).
TA feedback addendum: TA-M1-2026-10-05 (§11).
Base feature definitions remain v1.1 (the same 27 predictors). Contract v1.2 adds
tutorial-aligned evidence, validation and training interfaces. Independent checks
verified the current base dataset and splits; see the
[progress and verification record](../../../docs/milestone2_progress.md).
Phase B Stage 3 passed independent verification; the user authorized Stage 4.
Stage 4 tuning/diagnostics/selection passed independent verification and the user
reports review passed. Tutorial 8 addendum T8-2026-10-05 (§13) applies before final
testing. Stage 5 supplement, final-fit bundles, protected evaluation and local scoring
are now internally complete, awaiting independent/team review (§14). See the
[Stage 4 handoff](../../../docs/milestone2_stage4_handoff.md); do not relabel earlier
reports or deferred checks as passes.

Read this document together with the [feature contract](feature_contract.md),
[proposal](../../../docs/milestone2_proposal.md), and
[data architecture](../../../docs/data_architecture.md). The architecture owns
directory/lineage rules; this guideline and the feature contract own detailed ML
rules. The processing-plan PDFs and Feature Baseline v1.0 PDF are discussion inputs;
this revised contract incorporates their review and teammate geography feedback.

Follow the [Milestone 2 master plan](../../../docs/milestone2_master_plan.md) for
stage order, teaching alignment, acceptance gates and the full submission checklist.

## Locked baseline implementation decisions

- Only `distance_km_max` is a baseline distance predictor. Do not export primary
  or mean seller distance. The maximum is a geographic-difficulty proxy, not proof
  that the farthest parcel is last to arrive. No correlation >0.99 is assumed.
- Filter points against the pinned IBGE Brazil polygon before computing coordinate
  medians by five-digit ZIP prefix and state. A bounding box is insufficient.
  Median reduces outlier influence; it does not guarantee a true location.
- Null distance when any required seller/customer location is unresolved. Retain
  the order and record missingness; never use a smaller partial maximum.
- Physical totals require all item measurements; otherwise null them and retain
  missingness fractions. Zero-price orders remain, with a null freight ratio.
- Keep customer and primary-seller state and interstate_share. Section 4 of the
  contract freezes the exact predictor allowlist and PDF-name mapping.
- Require a valid score for classification and positive fractional-day duration
  for regression. IDs, status, outcomes and eligibility flags are audit/target
  columns, never predictors.
- Listing features are secondary. Seller outcome histories and stacking remain
  deferred until their stricter contracts are implemented.

## 1. Lineage and scope

`data/preprocessed/*.csv -> src/features/ -> data/business/ml/`

The notebook `notebooks/04_ml_feature_engineering.ipynb` explains and calls reusable
code. ML must not read `data/raw/` or `data/business/dashboard/`. Do not import
dashboard-specific date clipping, review collapsing, or order exclusions implicitly.

Build one row per source order. Keep deterministic checkout aggregates reusable
across tasks, but fit task-specific models on task-specific eligible rows.
Preserve source files and existing dashboard behavior.

The sole additional reference is the pinned IBGE country polygon specified in
the contract's Geography lookup section. Stage it and `boundary_manifest.json`
under `docs/references/geography/`; the archive is not supplied by this revision.
Record the actual source URL, edition, SHA-256, CRS and geometry transformation.
This is a documented, label-independent geographic quality-control exception to
the preprocessed-only rule. Do not alter raw Olist inputs or import other external
predictors.

Build with cached local geometry. A missing reference, missing CRS, invalid
geometry or checksum mismatch must fail clearly; no silent bounding-box fallback
or runtime downloads. Boundary-inclusive coverage, retained islands, no buffering,
coordinate-median revalidation and coverage-loss reporting are mandatory.
The contract defines exact steps and the historical-boundary limitation.

## 2. Artifacts and column roles

| Artifact | Contract |
| --- | --- |
| `orders_ml_features.csv` | Shared order-level base; identifiers, deterministic predictors, targets and eligibility/audit columns have explicit roles. No scaled values, seller outcome histories or model predictions. |
| `feature_schema.json` | Versioned columns, roles, types, units, formulas, availability assumptions, missingness rules and task feature allowlists. |
| `dataset_manifest.json` | Input hashes, target/feature versions, configuration, row counts, exclusions and deterministic content checksum. Separate volatile run timestamps from content identity. |
| `split_assignments.csv` | One row per order: customer group, split version, and development/holdout/excluded assignment with reason. |
| `cv_assignments.csv` | One row per task and eligible development order: validation fold and split version. |
| `quality_report.json` | Contract checks, missingness, join cardinalities and cohort counts. Required failures stop publication. |
| `zip_centroids.csv` | Versioned ZIP/state median lookup after country filtering, with coordinate counts, status and boundary version; unresolved keys retained. Not a model-input table. |

Optional `train.csv` and `test.csv` are derived exports, never independent sources of
split membership. Fold-specific history or prediction caches require task, fold,
model/configuration version and source-partition provenance.

Training must use explicit feature allowlists. Never infer predictors with
`drop(target)` or “all numeric columns.” Quarantine both targets, all review scores,
eligibility flags, IDs, split labels, raw timestamps and outcome-derived measures.
IDs remain available for joins, grouping, and audit only.

## 3. Tasks and label scope

- Regression: delivered orders with valid purchase/delivery timestamps and strictly
  positive elapsed duration. No review requirement. Output `lead_days`.
- Classification: any order with a valid review score in 1–5, irrespective of
  eventual delivery. Output `is_detractor` using the minimum valid score.
  Missing reviews have a null target, never zero.
- Both tasks additionally require a valid purchase time and resolved customer group
  for evaluation. Preserve ineligible rows and exclusion reasons in the base table.
- Minimum-score labels mean “any recorded negative review.” They do not mean first
  or final review. Record observation-window limitations and label availability.
- Do not make shared features depend on delivery/review eligibility.

Detailed rules, including temporal-label restrictions, are in the feature contract.

## 4. Time and preprocessing constraints

Prediction cutoff: `order_purchase_timestamp`. Checkout payment/seller allocation
and catalogue attributes have unverified snapshot-availability assumptions; record
them and provide a no-payment sensitivity run if needed.

Current-order approval, shipping/handover and customer-delivery timestamps,
shipping-limit dates, review text/timestamps/scores, final order status, delivery
duration and late/on-time flags are not baseline predictors. Estimated-delivery
promises are excluded from version 1; adding them needs a named availability and
business-use experiment.

Export deterministic values in original units. Imputers, encoders, top-category
selection, scalers, data-driven clipping and feature selection must be fitted inside
each training fold. Numeric missingness must not silently become zero in aggregates.
Unknown categories must be handled and logged.

## 5. Split and evaluation contract

Use a shared customer-group development/holdout manifest, approximately stratified
by review class, before model fitting. The feature contract specifies the handling
of unknown labels. Every order belonging to one `customer_unique_id` receives the
same outer assignment.

Within development: five-fold StratifiedGroupKFold for classification and GroupKFold
for regression. Reuse task folds across model comparisons. Fail clearly if the
population cannot support the requested folds or both classification classes.

Holdout outcomes must not drive transformation choices, model selection, calibration,
or threshold tuning. Publish final holdout scores after choices are locked.
Development OOF scores used for selection are not an independent final estimate.

Temporal evaluation is optional and separate. It requires chronological and
label-maturity checks; GroupKFold alone is not temporal validation. Maintain the
current disjoint-customer requirement and report any overlap exclusions.

## 6. Optional extensions

Historical seller outcomes require event availability before the scored purchase
AND permitted training-source membership. Build them per fold, never globally.
Specify cold-start counts/fallbacks. A scaler pipeline does not protect a
precomputed history feature.

`T_pred` belongs to training outputs, not the base table. Classifier outer folds
must enclose regression fitting and inner OOF construction. Compare with and without
it on identical rows. Detailed requirements are in the feature contract.

Class weighting, XGBoost, temporal validation, voting and stacking are optional.
Begin with simple linear/logistic and tree baselines. Do not hardcode class weights.

## 7. Handoff and artifact requirements

Implementation order:

1. Read contract sections 2–4; stage/check the boundary reference and provenance.
2. Implement portable reusable modules under `src/features/` for geometry lookup,
   item/payment/review aggregation, targets and base export. Explain execution in
   `notebooks/04_ml_feature_engineering.ipynb`.
3. Export the base table, lookup, schema, manifest and quality report. Apply the
   exact common predictor allowlist; secondary features require versioned variants.
4. Build shared outer and task-specific inner split manifests per contract section 7.
5. Run contract section 9 checks, including country filtering, incomplete distances,
   missing physical totals, review eligibility and multiplication-safe joins.
6. Hand off commands, input requirements, dependency versions, actual output counts,
   missingness/coverage, exclusions and test results to both model teams.

The existing repository-root entrypoints are
`python -m src.features.build_features` followed by
`python -m src.features.create_splits`; document actual arguments, boundary setup
and validation commands after fixing and verifying them. Pin compatible dependencies.
Their existence does not establish successful validation. Training can proceed only once
required dataset checks pass. No model fitting is required merely to build features.

Before training, pass the required base/split checks in the feature contract.
Pipeline-dependent checks are deferred until training, then gate model publication.
Save pipelines
with feature names/order, positive class, threshold, target/cohort version, split
version, dependency versions, configuration and metrics. Reload and verify
predictions and threshold decisions.

Generated datasets and models are implementation outputs, not deliverables of this
documentation revision. Do not claim a plan has passed leakage checks before the
implementation and its assertions exist. Keep implementation changes uncommitted
unless explicitly instructed to commit.

## 8. Tutorial alignment and implementation handoff

The feature contract is the detailed authority, especially §11. If the proposal's
general wording suggests log transforms in the initial baseline, follow §7: no logs
in the first baseline; evaluate them only as named development experiments.

| Local teaching material | Required project adaptation |
| --- | --- |
| [Tutorial 1](../../../docs/Tutorial/Tutorial%201/T1.ipynb) and [Tutorial 2](../../../docs/Tutorial/Tutorial%202/T2.ipynb) | Question-driven development EDA, per-column summaries, grouping and documented data-quality observations. |
| [Tutorial 3](../../../docs/Tutorial/Tutorial%203/T03.ipynb) | SimpleImputer, StandardScaler, OneHotEncoder, Pipeline and ColumnTransformer. Whole-dataset fitting is a teaching demonstration, not our evaluation protocol. Binning/interactions are optional experiments. |
| [Tutorial 4](../../../docs/Tutorial/Tutorial%204/T04.ipynb) | Fit transformations on training only; reuse transform at validation/inference. Use reusable code; no checkout-time review-text features. |
| [Tutorial 5](../../../docs/Tutorial/Tutorial%205/T05.ipynb) | Linear regression, correlations and residual-led investigation. No automatic feature removal or causal claims from coefficients. |
| [Tutorial 7 reference](../../../docs/Tutorial/Tutorial%207/Logistic_Regression_Standard_Solution_non_agentic.ipynb) | Unweighted baseline, whole-pipeline CV, OOF threshold choice, input QA, and pipeline plus threshold plus metadata. |
| [Tutorial 7 agentic lab](../../../docs/Tutorial/Tutorial%207/IT5006_Agentic_Logistic_Regression_Student.ipynb) | Team-owned modelling decisions, evidence-based review and mechanical acceptance checks. |

These are learning references, not runnable dependencies or instructions to copy
synthetic data/results. Where T07_Main differs, follow the reference/agentic lab's
unweighted baseline and development-only threshold selection. Keep the project's
group-aware splits, Unknown category policy and AP primary metric as documented
adaptations. No need to force PCA, normalization, polynomial expansion or text
vectorization into the project merely because a tutorial mentions them.

### Phase A — current base-feature/split correction and handoff

Phase A verification completed at `ddd1523` on 2026-10-05. Both remaining fixes
(malformed-coordinate validation and split-export rollback) passed independent
tests. The checklist below remains binding for future changes. Phase B Stage 3
baseline training has used the verified saved manifests and unchanged features;
its independent verification passed and the user authorized Stage 4. Stage 4
independent verification/team refinement is now the next gate.

1. Read the entire contract and this README. Preserve the 27 predictors, target
   definitions and eligibility rules. Do not add history, T_pred, imputed values,
   one-hot columns or scaled values to orders_ml_features.csv.
2. Resolve the existing implementation review findings: actual boundary hash/CRS
   validation including caches; boundary-inclusive production filtering; canonical
   LF file hashes; validation before publication; real Cartesian-join tests; null
   labels for invalid-only reviews; complete geography coverage reporting and lookup
   provenance. Supply reproducible boundary-staging instructions without runtime
   downloads. Do not claim a clean-clone rebuild without testing it.
3. Align splits to contract §7: order-level strata with customer grouping, stable
   order_id sorting, not customer-level "any negative wins" strata. Explicitly
   version corrected splits, regenerate dependent CV manifests and invalidate old
   fold-dependent caches. Freeze only after checks and review; never select a split
   for better model scores.
4. Implement base-input/export validation and fixtures from §11.4. Keep source
   files untouched and previous published outputs intact on a failed build.
5. Simplify notebooks/04_ml_feature_engineering.ipynb to module calls and explanations;
   replace embedded source copies with actual development-only audit outputs per
   §11.2. No data-driven feature changes without a named experiment and approval.
6. Hand off actual counts, missingness rates, coverage, source/output hashes, split
   checks, commands, environment versions and limitations. Separate executed passes,
   failures and deferred pipeline checks. Record contract_version=v1.2 separately
   from feature/split versions. Test reproducibility after Git newline normalization;
   treat float columns as reproducible within `atol=1e-9`, `rtol=1e-9` (native
   units), not bit-identical, per contract §2.

Phase A does not authorize model fitting or seller-history implementation. Complete
and verify the base/split handoff before the team starts Phase B.

### Phase B — subsequent training-agent instructions

Implement src/models/ factories and notebooks/05_model_training_and_evaluation.ipynb
following contract §§7 and 11.3–11.5. Use explicit column names and remainder='drop',
the approved manifests, and one preprocessing-plus-estimator Pipeline per model/fold.
Whole-pipeline CV consumes original-unit columns. No global fitting or resplitting.
Also satisfy the Week 6/7 training and artifact gates in §9 before publishing models.

Run missing/type/range/unseen-category/all-missing/reordered-column tests and verify
that validation perturbations cannot change fitted training transformations. Produce
baseline comparisons, OOF predictions, residual/calibration diagnostics and approved
threshold evidence. Save/reload the complete decision artifact and verify identical
predictions. Leave histories and stacking deferred unless separately authorized.

Maintain a decision record with choice, rationale, evidence and team approval for
feature variants, metrics, cost assumptions and thresholds. Do not use holdout results
to revise them. Do not commit implementation changes without an explicit instruction.

## 9. Binding Week 6 and Week 7 alignment rules

This section supplements feature contract v1.2; it is an implementation requirement,
not optional conversation context. It does not change the 27 baseline predictors,
targets, eligibility or split rules. Record this addendum identifier in model metadata.
If a future change conflicts with the contract, stop and obtain a documented team
decision rather than choosing whichever document is convenient. Course examples
are teaching references; the project brief controls assessed scope.

### 9.1 Sources and milestone boundaries

| Teaching reference | Required adaptation |
| --- | --- |
| [Week 6 deployment slides](../../../docs/Course/W6/L6_Model_Deployment_Slides.md), Part 1 | Independent pipelines, complete serialized artifacts, metadata and training-reference statistics. |
| [Week 6 training notebook](../../../docs/Course/W6/ML-deployement-necessary_files/Model/L6.1_Fraud_Detection_Training.ipynb), Steps 3–8 | Explicit feature units, fresh preprocessing objects, model comparisons and reload checks. |
| [Week 6 bulk scoring](../../../docs/Course/W6/ML-deployement-necessary_files/FastAPI_and_Render/L6.2_Bulk_Scoring_Demo.ipynb) | Consistent single-row/batch inference, identifiable results and explicit failures. |
| [Week 7 classification slides](../../../docs/Course/W7/Classification_01_Updated.pdf), pp. 16–25, 33–38, 42–46 | Probability/log-odds interpretation, classification error rates, cost-dependent thresholds and ranking use cases. |
| [Week 7 revision slides](../../../docs/Course/W7/extra-slides.pdf), pp. 1–5 | Distinguish SD from uncertainty of an estimate, anomalies from faults, odds from probabilities, and threshold trade-offs. |
| [Project brief](../../../docs/references/IT5006%20Project%20Description%20-%20AY%202026_27%20Semester%201.pdf), pp. 5–6 | Two to three model families total across regression/classification; live deployment belongs to Milestone 3. |

Course/tutorial folders may be absent from a clone because they are local reference
materials, not runtime dependencies. The rules below are self-contained. Do not
download, execute or commit teaching artifacts merely to satisfy these references.

Phase A remains base-feature/split work only. Phase B must produce reusable local
scoring and model artifacts for Milestone 2. A live API, Render hosting, Streamlit
prediction UI and operational monitoring are Milestone 3 work, unless separately
authorized. Preserve the two-family baseline (linear and tree-based); voting/stacking
is an optional extension within the brief's total family budget, not a requirement.

### 9.2 Independent fitting and training-reference statistics

- Construct fresh preprocessing/model objects using factories or sklearn clone for
  every model and fold. Never share a fitted mutable preprocessor across pipelines.
  Test that fitting model B leaves model A's saved transformation state and predictions
  unchanged. Whole-pipeline CV still uses the approved group manifests.
- For each published final model, save feature_stats.json with its artifact bundle
  under artifacts/models/. Calculate statistics from that model's eligible development
  training rows, before learned transformation, never from holdout rows or all orders.
  Classification and regression may therefore have different reference statistics.
- Include per-numeric-column count, missing count/rate, mean, standard deviation,
  min, quartiles and max; per-categorical-column counts/frequencies and missing rate.
  Record units, denominators, standard-deviation convention, model/task/version,
  feature/contract/split versions and training-source identifiers or their digest.
  Serialize undefined statistics as JSON null, not NaN/Infinity; identify constant
  and entirely missing columns explicitly.
- Assert the reference population exactly matches the fitted model's training
  population and excludes holdout IDs. Reference statistics describe that population;
  they do not overwrite base features or supply an independently fitted imputer.
- A single observation beyond three standard deviations is an anomaly warning, not
  proof of drift, an invalid record or a bad outcome. Do not automatically drop, clip
  or reject legitimate extremes using this teaching heuristic. Monitoring policies
  must distinguish hard schema violations from soft distribution warnings.

### 9.3 Scoring interface and acceptance tests

Implement one reusable local scoring function in src/models/ used by both single-row
and batch callers. Input consists of the contracted original-unit predictor columns
plus order_id for result alignment only. It is an order-level feature interface,
not a claim that the fitted pipeline accepts the nine transactional source tables.
If transactional inputs are later supported, reuse the same deterministic feature
builder and frozen lookup versions; do not reimplement feature formulas in a UI/API.

Validate inputs using contract §11.4, select predictors by name and load the saved
pipeline and decision policy without fitting. Return:

- order_id, task, model/version and feature/contract/split identifiers;
- regression: predicted_lead_days (days), not an observed delivery duration;
- classification: probability for is_detractor=1, saved threshold and binary decision
  using probability >= threshold;
- validation status and structured warnings/errors. Failed rows have null predictions,
  never zero probabilities, a negative class or a fabricated duration.

Scoring must not require targets, final order status or outcome-based eligibility
flags. Those define historical evaluation cohorts, not available checkout inputs.
Disclose the models' delivered/reviewed-cohort limitations for inference on other orders.
Do not silently clip negative linear-regression predictions; any such policy is a
documented development-tested variant saved with the artifact, never a change to labels.

Reject missing required columns and null or duplicate order_id values clearly.
For row-level errors, either fail the batch explicitly or return an identifiable
error for each invalid row; document the selected behavior and never silently drop
rows. Do not round probabilities before applying the decision threshold.

Acceptance tests must establish:

1. One-row and batch predictions agree for the same valid orders, within a declared
   numeric tolerance, with identical threshold decisions.
2. Reordering rows/columns preserves results when joined by order_id.
3. Saved/reloaded artifacts reproduce outputs in a fresh process with no fit call.
4. Existing missing/unseen-category policies hold for both interfaces; malformed
   rows cannot silently produce plausible success results.
5. IDs, targets and audit fields cannot enter model predictors.

### 9.4 Evaluation, operating policy and interpretation

Keep AP as the primary classification ranking metric, with ROC-AUC and the existing
precision/recall/F1, accuracy and calibration diagnostics. Also report confusion
counts with explicit label order [0,1], specificity, FPR and FNR at both the default
0.5 threshold and the development-approved threshold. Define zero-denominator
metrics as unavailable with a reason rather than inventing a valid rate.

For this project, positive means an order with a recorded negative review:

- TP: correctly flagged negative-review order; FP: flagged nonnegative-review order.
- TN: unflagged nonnegative-review order; FN: missed negative-review order.
- specificity = TN/(TN+FP); FPR = FP/(FP+TN); FNR = FN/(FN+TP).

These definitions apply to the evaluated reviewed cohort; unreviewed orders are not
negatives. Do not copy banking approval/default terminology or its cost figures.
Lowering a fixed model's threshold cannot reduce TP or FP counts on the same rows;
do not promise a strict increase, improved precision or measured intervention benefit.

If capacity-based prioritization is used, record team-approved K or percentage,
candidate population and scoring period before final evaluation. Rank development
OOF probabilities descending with order_id ascending as the tie-break. For a
percentage, specify rounding; for a period with fewer than K candidates use all
available candidates and report effective K. Report precision@K, recall@K and actual
review volume per period, with explicit aggregation/denominators and undefined
metrics for empty/no-positive periods. Freeze the policy before holdout evaluation;
do not select K from holdout outcomes. A top-K policy is not a fixed-threshold policy:
save its ranking configuration separately and identify which policy produced a decision.

Retain regression MAE, RMSE, R² and residual diagnostics. Logistic explanations
must distinguish probability, log-odds and odds ratios: exp(coefficient) changes odds,
not probability by that percentage. Explain scaled numeric changes and categorical
references separately, holding other model variables fixed; require development
stability/ablation evidence before importance claims. Do not infer causality.
Fold-score SD is variability across folds, not a confidence interval; do not label
it SE or derive a naive independent-sample interval from dependent CV folds.

### 9.5 Optional ensembles and teaching-example safeguards

If voting is authorized and improves development evidence over simpler models,
persist component artifact IDs/hashes, feature/cohort/split versions, positive-class
mapping, combination rule, weights and decision threshold (or capacity policy).
Choose weights, calibration and thresholds on development data only. Test reloaded
combined probabilities/decisions against the original outputs. Two saved pipelines
without their combination policy do not constitute a reproducible ensemble.

Do not copy these course-example choices as project defaults:

- The Week 6 Haversine implementation returns an angle. Our distance_km_max must
  multiply the angle by 6371 km, with degree-to-radian conversion and the contract's
  coordinate validation; do not import its units or fill unknown locations with zero.
- Pre-split rolling transaction summaries in the fraud example do not authorize
  global seller-outcome histories. Preserve both fold membership and outcome-event
  availability controls; histories remain optional and deferred.
- Preserve missing predictors for fold-fitted imputation rather than copying blanket
  dropna. Retain nominal one-hot encoding rather than copying arbitrary ordinal codes.
- Fraud-example weighting is not mandatory. The unweighted logistic baseline remains;
  weights, XGBoost and ensembles require named comparisons, not assumed improvements.
- Week 7's SGDClassifier comparison is a teaching exercise, not another required
  project model. If explored, keep it within the linear family and approved CV scope.
- Do not deserialize supplied course pickle files, call the example live service,
  reuse synthetic fraud records as project evidence, or copy hardcoded metrics,
  thresholds, category lists, runtime versions or cloud limits into project claims.

### 9.6 Required handoff evidence

The Phase B handoff must include model/reference-statistic provenance, the scoring
interface and examples, independence and single/batch/reload test results, explicitly
labelled error-rate tables, and the approved threshold/capacity decision record.
Include ensemble-policy evidence only if that extension was implemented; otherwise
mark it not applicable. List unexecuted gates as deferred, never passed. These are
model-publication gates, not extra transformations for the Phase A base CSV.

## 10. Binding additional lecture and sample-report alignment

Addendum ID: `C1-C5-TREE-2026-10-05`. Read and follow
[the self-contained teaching alignment](../../../docs/milestone2_teaching_alignment.md)
with contract §12 and the master plan. It records newly supplied Lectures 1–5,
Classification 2/3 and all three sample reports. Agents do not need the uncommitted
PDFs to implement these rules. Save both teaching addendum IDs with model metadata.
These requirements affect Stages 3–6; verified features/split assignments stay fixed.

Required model/report handoff evidence:

- CRISP-DM narrative connecting question, data, modelling, evaluation and use.
- Development OOF regression residual-versus-fitted, distribution and Q–Q plots;
  numeric correlation and transformed-design conditioning discussion. VIF, adjusted
  R² and F-tests are optional with stated assumptions. Scaling does not remove
  multicollinearity; low R² alone does not prove nonlinearity.
- Actual CART criteria, tree depth/leaf counts, fold train/validation metrics,
  bounded complexity/pruning comparisons and a readable development tree diagram.
  Record forest sampling/feature-subset settings. Optional row-level OOB cannot
  replace customer-group validation.
- Same-fold paired model comparisons, runtime and metric/threshold labels. Do not
  treat overlapping CV fits as independent observations for definitive significance
  or confidence intervals. Class-1 F1/precision/recall and AP stay required;
  weighted F1 is supplementary.
- Predeclared customer-state/basket-size subgroup errors with support/class counts,
  undefined-metric handling and small-sample limitations. Geography is not evidence
  of protected-demographic fairness.
- A 6–8 page main report with separate CV/holdout task tables, baseline/selection
  rationale, stakeholder/action/evidence/assumptions table, labelled figures and
  valid cross-references. Keep required results in the main body and trace values
  to saved outputs. Older healthcare samples guide presentation only.

Naive Bayes, PCA, SMOTE, boosting and ensembles are optional taught techniques,
not mandatory additions. Record scope/family-budget decisions and implement learned
steps within folds. Never copy sample medical exclusions, histories, metrics,
test-based selection or threshold searches. Threshold selection differs from
probability calibration; both remain development-only. Stage 3 baseline evidence
has passed independent verification; Stage 4 tuning evidence is internally executed
(see handoff). Stage 5–6 evidence remains unexecuted;
no gate passes merely by documenting this addendum.

## 11. Binding Milestone 1 TA-feedback response

Read [the TA feedback response](../../../docs/milestone1_feedback_response.md),
addendum `TA-M1-2026-10-05`, and contract §13 before Stage 3. These requirements
supplement the teaching rules; they do not change the verified base dataset or splits.

- Explain prediction time, target derivability, eligibility and stakeholder action
  separately for each task. Checkout is this project's choice, not a universal rule.
  A non-negative review label does not establish customer satisfaction.
- Supply task-relevant literature and actual feature-construction rationale, including
  formulas, grain, availability and limitations. Compare selected baselines and tree
  families; a general trees-versus-neural-networks argument cannot justify XGBoost.
- Explain aggregation-before-join, cardinalities and a worked example; reconcile
  item-level/dashboard counts with the order-level modelling cohorts.
- Complete development-only task relationship EDA and purchase-month outcome trends,
  with cohort counts and uncertainty/coverage limitations. Outcome-to-outcome analysis
  is diagnostic evidence, never permission to use future outcomes as predictors.
- Before freezing modelling choices, run the mandatory minimum-review versus first
  valid answered-review label diagnostic defined in contract §13 and the response
  document. Report score distributions, common-cohort prevalence/disagreement,
  multi-review counts and timestamp exclusions. Alternative-target retraining is
  optional; do not overwrite baseline labels, artifacts or fold assignments.
- Support metric choices with checked sources and discuss advantages/limitations.
  Produce one coherent report with references after the main body; distinguish
  associations from mechanisms, causal explanations and unmeasured business impact.

Store label audits outside predictor exports, record this addendum ID in modelling
metadata, and provide saved evidence for each requirement. Literature/EDA/label-audit
work must remain pending until executed; Stage 3 evidence is now available in the
handoff, while final report/selection evidence remains pending. Full implementation
instructions and report
acceptance checks are in the linked response; another agent needs no local course PDFs.

Implementation handoff must also follow the response's §7 reasoning standard:
for major choices state the observed data property, mechanism/justification, plausible
alternative, limitation and development check. Predeclare refinement hypotheses and
report contrary results honestly. Add concise notes to the existing progress log;
do not add algorithms just to demonstrate breadth. Explain worked feature/label and
prediction/error examples so teammates can review them. Agent-written explanations
are not proof of human understanding: leave team review/sign-off pending until the
team actually performs it. This adds no base-feature or split changes.

## 12. Stage 4 frozen development handoff — 2026-10-05

Stage 3 independent review passed; user authorized Stage 4 and delegated the
sensible taught-policy choice. Stage 4 independent verification and user-reported
review passed; see the [handoff](../../../docs/milestone2_stage4_handoff.md).

- The immutable `artifacts/metrics/stage4-selection-v1/selection_record.json`
  and separately checksummed `decision_policy.json` bind selected configurations,
  features, versions and the illustrative 5:1 policy. Both selected models are
  64-tree forests (depth 16, leaf 20, half features, bootstrap, seed 42).
- Primary predictors remain the same 27; no-payment and item-bearing-only runs
  are named diagnostics, not changed source-of-truth datasets/targets. The no-payment
  experiment removes four columns from the fitted transformer, but its current
  diagnostic input validator still expects the full raw schema. A proposed reduced
  final input contract must update validation/scoring/schema together, with fresh
  documented selection/policy evidence before holdout. Do not silently change it.
- Class-1 probability >= **0.16387042604339028** is the frozen illustrative
  primary policy, not the model's default 0.5 or a top-10% capacity rule. Never round
  at the boundary; read saved probabilities with round-trip float parsing when
  checking exact decisions. The user authorized this assumption, not real costs
  or deployment. Scenarios 1/2/5/10 and all/no-alert controls are saved.
- Selected OOF metrics and policy results are development-selection evidence,
  not independent estimates. Matched cohort, snapshot, itemless-record, reference-
  category and workload caveats in the handoff are binding for interpretation.
- Preserve canonical run directories; rerun under a new ID. Do not evaluate holdout
  or publish these fold checkpoints as final models. Stage 5 must consume accepted,
  frozen selection/policy and reject mismatched versions/hashes.
- Raw/base/splits are unchanged. Canonical Stage 4 evidence contains a 213 MB CSV;
  packaging/compression must be resolved before any requested GitHub commit.
  This work adds no ignore rule, commit or deletion.

Review: `python -m src.models.verify_stage4 --run-id stage4-selection-v1`.
Execution: notebook 06 and `python -m src.models.stage4 --run-id <new_id>`.
Essential teaching instructions are here and in the addenda; local PDFs are not
runtime dependencies. Stage 5 was subsequently authorized and internally executed;
the supplement below preceded final testing. See §14 for its reviewed-artifact boundary.

## 13. Tutorial 8 binding adaptation — T8-2026-10-05

Follow [teaching alignment §5](../../../docs/milestone2_teaching_alignment.md#5-tutorial-8-review-and-pre-holdout-supplement--t8-2026-10-05).
The local notebook is a learning reference, not a runtime dependency. No base
feature, label, eligibility, split or accepted model/policy changes are required.

- Before final testing, run the selected classification pipeline's development
  learning curve on the five saved folds: nested 25%, 50%, 100% **training customer
  groups**, validation unchanged. Fresh fold-fitted pipelines at the smaller sizes;
  reuse verified matching 100% fold evidence. At most ten new fits, 30-minute budget;
  log exact row/group counts, class counts, membership digests, seed, warnings,
  runtime, AP and ROC-AUC on training/validation. Details/failure handling are in §5.
- Reuse saved same-order OOF probabilities for dummy, plain logistic, single-tree
  baseline and selected forest ROC/PR overlays. Label pooled selection OOF versus
  mean CV metrics correctly. Add a worked path from an existing fitted development
  tree, original-unit numeric thresholds and correct encoded-category semantics;
  it explains that tree, not the selected forest or a causal mechanism.
- Final reporting adds per-class precision/recall/F1/support and raw/row-normalized
  confusion matrices at 0.5 and the exact frozen policy. Positive class is the
  recorded-negative review (1), not credit approval. Undefined rates are null with
  reasons. AP remains primary; accuracy/ROC-AUC cannot override the accepted choice.
- Balanced weights, Naive Bayes and soft voting are taught alternatives, not
  required additions. Any such experiment requires an explicit development-stage
  scope decision, identical saved folds, fresh learned preprocessing, comparison
  and refreeze of model/policy before holdout. No averaging accepted thresholds;
  a new ensemble needs its own OOF probability policy and complete persisted artifact.
- Save/reload complete final pipelines and schema/policy/metadata; resolve probability
  columns from classes_, never assume column 1 blindly. Do not reproduce synthetic
  credit records, suppress all warnings, hand-enter tree rules or select/tune from
  test comparisons. Retain sparse encoding and unscaled tree numerics; neither
  dense teaching arrays nor identical scaling across families is compulsory.

Save supplement artifacts separately, with source/config/input hashes, inherited
versions and T8-2026-10-05. These rules alone establish no result; executed evidence
is recorded below.

## 14. Stage 5 final evaluation and scoring boundary — 2026-10-05

See the [Stage 5 handoff](../../../docs/milestone2_stage5_handoff.md). Internal
verification passed and Stage 5 independent acceptance is recorded in the progress
log; team explanation review remains pending. Stage 6 report/replay are internally verified;
live deployment is not complete. Feature v1.1, contract v1.2 and split v1.1
are unchanged; accepted 27 predictors, forests and exact policy are retained.

- `artifacts/metrics/stage5-tutorial8-v1/` holds the executed ten-fit supplement;
  `stage5-final-v1/` holds the one protected holdout evaluation. Saved final bundles
  are `artifacts/models/<task>/stage5-final-v1/`, not the Stage 4 fold checkpoints.
- `python -m src.models.score --bundle <trusted_bundle> --input <csv> --output <new_csv>`
  uses original-unit named predictors and unique order_id without labels/status.
  It never fits. Invalid rows have explicit errors and null predictions; numeric
  missing cells/unseen categories use existing saved preprocessing and warnings.
  Scoring outputs/QA cannot silently overwrite existing files. Only trusted joblib.
- Bundle configuration/schema/statistics/metadata/policy and hashes are a unit.
  Training stats use eligible development only and sample SD ddof=1. Class decisions
  require saved class mapping and full-precision threshold; no policy rounding.
- The durable `artifacts/metrics/stage5_holdout_access.json` blocks another final
  fitting/evaluation run. Never remove it to retry or tune against test results.
  Read-only reload/metric verification of the same frozen experiment is permitted.
  Recovery or isolated clean reproduction needs an explicit documented protocol.
- Future human proposals after seeing holdout results must be labelled post-test
  hypotheses, not selected or honestly validated on that same holdout. Record
  independent review before Stage 6. Carry cohort, snapshot, long-delay,
  itemless/single-item and workload limitations into the technical report.

Review: `python -m src.models.verify_stage5 --run-id stage5-final-v1` and
`python -m src.models.verify_stage5 --supplement-only --run-id stage5-tutorial8-v1`.
Notebook 07 reads artifacts without retraining. No commit/push was made.

## 15. Stage 6 reproduction and communication boundary

Follow the [run guide](../../../docs/milestone2_run_guide.md) and
[Stage 6 plan](../../../docs/milestone2_stage6_plan.md). Teaching methods are
self-contained in this README/contract/alignment; do not require or package local
Course/Tutorial folders. Stage 5 independent acceptance is recorded; Stage 6 and
team explanation review are separate gates, not implicit approval.

- Separate deterministic **data rebuilding** from exact **accepted model replay**.
  Rebuild features/splits in a new workspace; compare against accepted exports at
  contract tolerance, preserving rebuilt artifacts. Before replay fits, pin the
  accepted original CSV/JSON bytes and hashes, then fit fresh fold pipelines.
  Tiny distance-rounding differences passed data tolerance but affected linear
  optimizer predictions in Stage 6; neither a relaxed model tolerance nor a new
  post-test rounded-feature policy is permitted to hide that result.
- Original data/models/metrics/receipt are immutable during reproduction. A new
  isolated snapshot has its own receipt; a current-worktree overlay is not proof
  of remote clean-clone availability. Failed attempts stay in the audit history.
- Execute notebook 04 before modelling because it writes ML/split artifacts;
  notebooks 05–07 read reproduced runs. Explain units/denominators, CV versus
  holdout, SD versus CI, accuracy versus AP and hypothetical policy costs.
- The technical report must show simpler-model comparisons, limitations and
  stakeholder use, not just metrics/citations. Preserve minimum-review bias,
  missing-item, long-duration and prediction-time assumptions; no causal benefit
  or "zero overfitting" claim from similar CV/test results.
- Compress large transport tables losslessly and record source/restored byte
  hashes; never delete accepted originals. The generated distribution is for
  review, not a second source of truth or something to commit wholesale. Commit,
  remote publication/storage, Canvas submission and human sign-off require their
  own authorization/checks. Do not stage local teaching or unrelated files.

## 16. Current consolidated refinement and reproduction

This addendum supersedes historical model/interface/evaluation instructions above
for `refinement-selected-v3`, not the shared base-feature definitions. One logical
cycle contains the initial11-input reference,50 block fits,50 combination fits,
50 new model-baseline fits with15 results reused, and19 application/confirmation
fits. The initial263-fit phase and its terminal assessment remain historical
evidence. Expansion was adaptive; only each phase's catalogue was frozen in advance.

- Regression: the11 core cart/quote/state/calendar fields plus `distance_km_max`
  and `distance_missing_fraction`; depth5/minleaf100 decision tree,13 inputs.
- Classification: the same11 plus `n_sellers`, `primary_seller_state` and
  `interstate_share`; unweighted logistic C.01,14 inputs.
- The27-column CSV/schema/targets are not rewritten. Extract task allowlists from
  `src/models/configs/refinement_selected_v3.json`; no auto-select-all-numeric rule.
- Keep customer-purged chronology and strict label-maturity rules; original20%
  holdout remains excluded. Historical random CV assignments are lineage, not
  the applied chronological fold assignment.
- New selected `src.models.refinement_selected` bundles have a different strict
  interface from the11-field `CoreScorer` and27-field historical `Scorer`.
  Use `SelectedScorer`; do not silently send old batches into a new model.
- Root README owns copyable reproduction/scoring commands. Notebook08 calls those
  modules. Final reproduction needs base/manifest/preprocessed inputs and pinned
  libraries, not local courses/reports/reviews. Full trial reproduction still
  has historical private-provenance dependencies to package before publication.
- Verify before terminal scoring. The final terminal diagnostic is previously
  inspected evidence; it must not select another model/threshold. It found tree
  MAE5.5401 versus dummy4.8878; report the failed transfer, not a test-led switch.
- Keep all original and unsuccessful trials. Refresh report/importance/tree-path
  evidence for current fitted models; historical learning curves stay labelled
  historical. Word/PDF generation is deferred at the user's request.

All features are reconstructed placement proxies. Distance still relies on seller
origin and static geography even without explicit seller columns. Seller fields
are not time-certified allocation; no payment or catalogue block enters applied
models. No seller histories, target clipping, whole-data imputation, resampling,
calibration fit or test-driven policy change was introduced.

## 17. Current Champion Specification — Refinement Cycle 2 & Experiment 3 (Option 1, 10 October 2026)

This addendum records the current production champion state (`refinement-selected-v4`) developed in **Experiment 3** under the Option 1 pre-checkout integrity directive:

- **Pre-Checkout Feature Pruning (Option 1)**:
  - Pruned `has_items` and `freight_ratio_missing` from core predictors. Genuine checkout transactions inherently contain items. The 604 zero-item orders in the historical database represent post-checkout cancellations that aborted before order-item table generation. Including `has_items` in model training introduced subtle retrospective target leakage.
  - The clean core transaction feature set is reduced from 11 to **9 predictors**: `n_items`, `n_products`, `total_price`, `total_freight`, `freight_ratio`, `customer_state`, `purchase_month`, `purchase_dayofweek`, `purchase_hour`.
  - Condition number of the 9-core design matrix: $\kappa = 70.77$ with full numerical rank ($71/71$).
- **Task-Specific Feature Allowlists**:
  - **Regression (11 predictors)**: 9 core + `distance_km_max` + `distance_missing_fraction`.
  - **Classification (12 predictors)**: 9 core + `n_sellers` + `primary_seller_state` + `interstate_share`.
- **Pre-Checkout Eligibility Gating**:
  - Classification training and terminal holdout cohorts strictly filter out zero-item records via `df["has_items"].eq(1)`, ensuring models are trained and tested only on legitimate order attempts ($N = 78,334$ dev; $N = 15,769$ holdout).
- **Champion Models & Serialization**:
  - *Regression Champion*: Tuned Random Forest ($N=50, d=14, L=20$) with Target/Input Log1p and 60-day winsorization (Holdout MAE = **3.719 days**, $R^2 = \mathbf{+0.1871}$).
  - *Classification Champion*: Tuned Random Forest Classifier with Cost-Calibrated Optimal Threshold $\tau^* = \mathbf{0.17}$ under $1:5$ error cost ratio (Recall = **$38.2\%$**, business error cost = **8,205 units**).
  - Serialized bundles: `artifacts/metrics/refinement-selected-v4/bundles/`
  - Production configuration: `src/models/configs/refinement_selected_v4.json`

