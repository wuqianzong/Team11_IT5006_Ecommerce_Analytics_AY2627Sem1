# Model solution — s01 and s06 to s10 (in review)

Oct 17, 2026 · @B

This is my complete draft for the stages not yet covered: the problem contract (s01) and everything from training to release (s06–s10). It builds on the frozen s02–s05 solution. Review it the same way: set each row's Review cell, comment where you want changes.

## How this draft was built

- **Sources:** the project brief (Phase 2 and 3 deliverables, model-family budget, imbalance and deployment guidance), the teacher's Milestone 2 note (the rubric), the Milestone 1 TA feedback, and the tutorial sequence. Tutorial 5 covers linear regression and residuals; Tutorial 7's reference solution covers pipeline → CV vs baseline → out-of-fold probabilities → threshold → fit once, test once → interpret → save and reload → QA; Tutorial 8 covers dummy → logistic → tree → forest and tuning; the Week 6 slides cover deployment. Milestone 2 code is reused as logic only; none of its results are used (G-29).
- **Every row is a recommendation** with its basis. Where the team must choose, the row says so and the item is repeated under Open items.
- **Review** the same way as s02–s05: set each Review cell to Approved, or Change with a comment. Approved stages get their tag switched in the Pipeline v2 chart and their blueprint committed as AGREED.
- Citations marked "to verify" are checked against the source in s01 before the report uses them.

## s01 — Problem statement (one contract for both tasks)

s01 fixes everything that must be decided before any data is modelled; its numbers go into the pre-registered layer of `protocol.yaml`.

| # | Item | Solution | Basis | Review |
| --- | --- | --- | --- | --- |
| 1.1 | Tasks and prediction time | Regression: delivery lead time in fractional days. Classification: will an eligible order (not cancelled or unavailable, and reviewed) receive a 1–2 star review (`is_detractor`, positive class 1). The classification score is therefore the risk of a 1–2 star review if the customer reviews; the report states this scope limit. Both predicted at checkout (`order_purchase_timestamp`) | [Brief](#mspt9bk2440.18909): 1–2 problems covering both types; [teacher note §1](#mspt9bk2440.16418) | Approved |
| 1.2 | Stakeholders and action | Regression → logistics / fulfilment planning: an expected lead time per order at checkout, used to flag long-haul orders and set realistic delivery promises. Classification → customer-experience team: a daily list of at-risk orders for proactive contact (status update, check with the seller). Each states who sees what, when, and the cost of each error | Milestone 1 TA: stakeholders were only named | Approved |
| 1.3 | Targets and populations | As agreed in s02: minimum-review label with first-review sensitivity; delivered orders (regression); not cancelled or unavailable, with a review (classification); scope limits stated | [G-20](#mspt9bk2440.20575) | Approved |
| 1.4 | Metrics | Regression: MAE primary (in days, robust to the long tail), RMSE, R², share within ±3 days. Classification: AP primary (suits a minority positive class; prevalence measured in s03, not assumed), ROC-AUC, Brier (probability quality), precision, recall, F1 and confusion matrix at the threshold. Accuracy never alone. Charts: precision–recall and ROC curves, out-of-fold in s06 (6.6) and on the test cohort in s09, saved with their curve data. Citations (verified): Willmott & Matsuura 2005 (MAE vs RMSE); Saito & Rehmsmeier 2015 (PR vs ROC under imbalance); Brier 1950 | [Brief](#mspt9bk2440.18909) metric list; [teacher note §5](#mspt9bk2440.17160); [Milestone 1 TA](#mspt9bk2440.19075) (cited metric rationale) | Approved |
| 1.5 | Cost assumption | Illustrative cost FN:FP = 5:1 (a missed detractor costs five unnecessary contacts). Stated as an assumption, never as measured ROI. Citation (verified): Elkan 2001 (cost-sensitive thresholds) | [G-24](#mspt9bk2440.20920); [brief](#mspt9bk2440.18909) imbalance note | Approved |
| 1.6 | Model families | Two families plus references: dummy (median / prior); linear (LinearRegression, Ridge; LogisticRegression); tree (DecisionTree, RandomForest). No boosting, voting or stacking | [Brief](#mspt9bk2440.18909): 2–3 families, simplest first; [Tutorial 8](#mspt9bk2440.18516) | Approved |
| 1.7 | Decision rule | A more complex variant is kept only if its mean on the primary metric over the five s05 folds beats the simpler one by more than one standard error (the one-standard-error rule). Procedure: for every candidate, the mean and standard error (fold SD / √5) of the primary metric; find the best mean; keep the simplest candidate whose mean is within one standard error of the best. The same rule chooses within the s06 ladder, within each s07 grid, and gives the recommendation among the s08 finalists, which the team confirms at the s08 gate (G-39). Simplicity order, pre-registered in protocol.yaml: dummy < linear/logistic < single tree < forest; within a family, stronger regularisation (higher alpha, lower C), shallower trees and larger leaves are simpler. Paired per-fold differences are reported alongside, as description only. Fallback: if no complex variant passes, the best simple model goes forward; if no model beats the dummy, the dummy is the reported result ("no signal at checkout"). The rule is fixed before any result and never loosened afterwards; a team override at the s08 gate is a logged protocol deviation, reported beside the one-SE choice (G-44). The alert threshold is not part of this rule: it is a business judgement at the s08 hard stop; default recommendation: minimise the illustrative cost subject to the daily alert cap (G-56) | [Teacher note §4](#mspt9bk2440.16984) (beat the family baseline); one-SE rule: Breiman et al. 1984 (CART); Hastie, Tibshirani & Friedman 2009, ESL §7.10; [glmnet lambda.1se](https://rdrr.io/cran/glmnet/man/cv.glmnet.html); [scikit-learn refit example](https://scikit-learn.org/stable/auto_examples/model_selection/plot_grid_search_refit_callable.html); [rule 5](#mspt9bk2440.21359) | Approved |
| 1.8 | Search budget | Grids fixed in s07 (one grid per family, listed there); random forest uses 200 trees; seed 42 everywhere; no new grid points after results are seen | Brief: tuning methodology, reproducibility | Approved |
| 1.9 | Outputs | `protocol.yaml` pre-registered layer and `task_contract.md` (prediction time, stakeholder action, metric and model rationale with verified citations, scope limits) | Design s01 | Approved |

## s06 — Training, basic to complex (per task)

Every model is one sklearn Pipeline built from the s04 recipe and scored on the five s05 folds; all preprocessing is fitted inside each training fold. Plain models only here; regularisation and tuning are s07.

| # | Step | Solution | Basis | Review |
| --- | --- | --- | --- | --- |
| 6.1 | Pipeline factory | Assembly only, no new transformation. One function combines the s04 recipe (feature set, imputation, encoding, scaling, log1p and log target, all defined in s04) with an estimator into one sklearn Pipeline with a stable `candidate_id`; regression log target via `TransformedTargetRegressor(func=log1p, inverse_func=expm1)`, always scored on raw days. The pipeline is fitted inside each s05 training fold; that is where the learned steps defined in s04 (medians, scaler, route median) get their values, so nothing is fitted on validation or test rows | [Tutorial 4](#mspt9bk2440.17752) Pipeline; [Tutorial 7 §5](#mspt9bk2440.17926); [README §5.3](#mspt9bk2440.21498) | Approved |
| 6.2 | Families, basic to complex | On each task's selected feature set (s04 4.4), through the s04 recipe (4.8: imputation, encoding, scaling) with the s04 4.2 log transforms always on (log1p on the five contract candidates with pre-cutoff skewness > 1, plus product\_description\_lenght for classification, G-47, G-62, G-70, and on the regression target; G-36). The classification set is chosen from the 24 contract predictors plus the three candidates adopted at the s03 gate (G-70), in this order: dummy (`DummyRegressor(strategy='median')` / `DummyClassifier(strategy='prior')`) → plain `LinearRegression` / `LogisticRegression(penalty=None, solver='lbfgs', max_iter=5000)` → `DecisionTree` (starting settings max\_depth=5, min\_samples\_leaf=100) → `RandomForest` (200 trees, max\_depth=10, min\_samples\_leaf=50, max\_features='sqrt'). Seed 42 | [Tutorial 8 §5–9](#mspt9bk2440.18516); [brief](#mspt9bk2440.18909) "simplest first"; [G-36](#mspt9bk2440.25926) | Approved |
| 6.4 | Scores recorded | For every candidate and fold: training and validation scores on all s01 metrics, row and positive counts, fit time, convergence warnings | [Teacher note §5](#mspt9bk2440.17160) (train–validate comparison) | Approved |
| 6.5 | Residual diagnostics (regression) | Residual vs fitted, residual histogram, Q–Q plot on out-of-fold predictions of the plain linear model and the best tree model | [Tutorial 5](#mspt9bk2440.17843) residual analysis | Approved |
| 6.6 | Classification diagnostics | Out-of-fold PR and ROC curves, reliability curve, Brier, predicted-probability histogram per class | [Tutorial 7 §6.3, §7](#mspt9bk2440.17926) | Approved |
| 6.7 | Learning curves and design matrix | Learning curves on the latest fold (training sizes 20–100%, same validation block), to read under- vs overfitting before s07. Encoded design-matrix rank and condition number for the linear models | [Tutorial 7 §7.1](#mspt9bk2440.17926); [Tutorial 8](#mspt9bk2440.18516); [Lecture 5](#mspt9bk2440.18801) | Approved |
| 6.8 | Outputs | `metrics_long.csv`, out-of-fold `predictions.csv.gz`, `decision.json` (each family comparison under the decision rule, with fold scores), `figures/` | [README §5.5](#mspt9bk2440.21612) | Approved |

6.3 (within-family tests of feature set and log transforms) was removed on 18 Oct: the feature set and log transforms are fixed in s04 from EDA (G-36). Rows 6.4–6.8 keep their numbers so existing references stay valid.

## s07 — Tuning: regularise and tune (per task)

Bounded grids on the same five folds, each candidate a whole pipeline carrying the s04 feature set and log transforms. Grids are fixed here before any tuning result is seen. Principle (teacher note §4): a tuned configuration is kept only if it beats its family's plain s06 model (plain linear/logistic, single tree) under the s01 decision rule (1.7); otherwise the plain model stays. Both families are still tuned and reported.

| # | Family | Grid | Basis | Review |
| --- | --- | --- | --- | --- |
| 7.1 | Linear (regression) | `Ridge(alpha)`: 0.01, 0.1, 0.5, 1, 5, 10, 20, 50, 100 | [Tutorial 5](#mspt9bk2440.17843) regularisation; [Tutorials 7–8](#mspt9bk2440.17926) GridSearchCV | Approved |
| 7.2 | Logistic (classification) | `LogisticRegression(C)` with L2: 0.01, 0.1, 0.5, 1, 5, 10, 20, 50, 100; `class_weight`: None, balanced | [Tutorial 7](#mspt9bk2440.17926); [G-05](#mspt9bk2440.19327) | Approved |
| 7.3 | Decision tree | max\_depth: 4, 5, 6, 8, 10, 12, 14, 16, 18 (includes the s06 depth 5; G-43); min\_samples\_leaf: 20, 50, 100, 200; classifier also `class_weight`: None, balanced | [Tutorial 8 §8](#mspt9bk2440.18516) tuning cell | Approved |
| 7.4 | Random forest | 200 trees; max\_depth: 8, 10, 12, 14, 16, 18; min\_samples\_leaf: 20, 50, 100, 200 (forest grid unchanged by G-43); max\_features: sqrt; classifier also `class_weight`: None, balanced | [Tutorial 8 §9](#mspt9bk2440.18516); Breiman 2001, Machine Learning 45:5–32 (verified) | Approved |
| 7.5 | Search method | `GridSearchCV` over the full Pipeline with `cv` = the s05 fold iterator, scoring = the primary metric (neg MAE, average precision), `refit=False`, `return_train_score=True`, seed 42. Best per family = the simplest configuration within one standard error of the best mean (s01 1.7). Simpler means higher alpha, lower C, shallower depth, then larger leaf. It is then compared with the family's plain s06 model by the same one-SE rule: if the plain model's mean is within one SE of the tuned configuration's mean, the plain model is kept (G-55) | [Tutorials 7–8](#mspt9bk2440.17926); [rule 5](#mspt9bk2440.21359) | Approved |
| 7.6 | Overfitting check | For each configuration report the train–validation gap; flag the best configuration if the gap is large and a simpler one is within the decision rule | [Teacher note §6](#mspt9bk2440.17339) (train–validate–test) | Approved |
| 7.7 | Outputs | `grid_results.csv` (every configuration: parameters, per-fold train and validation scores, mean, SD, rank, fit time, convergence), out-of-fold predictions of each family's best, kept separate as pooled OOF vs mean-fold scores | Design s07 | Approved |

## s08 — Selection, policy and test once (per task)

Tutorial 7 order: choose the model on threshold-free scores, then check calibration, then set the threshold, then fit once and score the test cohort once. Nothing after 8.5 may change the recipe.

| # | Step | Solution | Basis | Review |
| --- | --- | --- | --- | --- |
| 8.1 | Finalists | Each family's best from s07, plus the dummy and the plain linear/logistic and single-tree references from s06, compared on the same rows and folds (fold mean and standard error; paired per-fold differences shown as description) | [Teacher note §4](#mspt9bk2440.16984); [Tutorial 7 §6](#mspt9bk2440.17926) | Approved |
| 8.2 | Choose the model | One-standard-error rule (1.7) on the primary metric (MAE / AP): the simplest finalist whose mean is within one standard error of the best mean is the recommendation. The final choice is a human gate (G-39): the run stops and presents a selection pack, then the team confirms or overrides in spec/human\_decisions.yaml with its rationale. An override is a protocol deviation: logged as a CR in CHANGELOG, with the one-SE choice shown beside it in the report and slides (G-44). The pack holds each finalist's fold mean ± standard error on all s01 metrics, the train–validation gap and learning curves, plus a flag when a chosen setting sits at a grid edge. A grid-edge choice is resolved by the team, never silently: either widen that grid (change request; s07 reruns and keeps all configurations) or revisit s03–s04. Validation scores are reported as selection scores, not generalisation | [G-06](#mspt9bk2440.19430), [G-10](#mspt9bk2440.19722) | Approved |
| 8.3 | Calibration (classification) | Reliability curve and Brier on the chosen model's out-of-fold probabilities. Raw probabilities by default; a sigmoid-calibrated variant (`CalibratedClassifierCV`, time-ordered inner splits inside each training fold) is always scored as a full candidate, with no trigger to decide (G-52), and kept only if mean Brier improves and mean AP stays within one fold SE of the raw model (G-45) | [G-16](#mspt9bk2440.20045); [Tutorial 7](#mspt9bk2440.17926) | Approved |
| 8.4 | Threshold (classification) | From the out-of-fold probabilities of the chosen recipe: compare no alerts, 0.50, the theoretical cost cutoff 1/6 and the empirical cost minimum of 5·FN + FP (ties → higher threshold, fewer alerts). HARD STOP (G-39): the run stops and presents, for every candidate threshold: alerts per day, alert rate (TP+FP)/N, error rate (FN+FP)/N, precision, recall, F1 and cost. It also shows the marginal trade-off: extra false alarms per extra detractor caught between neighbouring thresholds. Under the 5:1 cost an alert pays off only while that ratio stays at or below 5, which is why the theoretical cutoff is 1/6 = C\_FP/(C\_FP+C\_FN) (Elkan 2001). The team picks the threshold in spec/human\_decisions.yaml and may set a daily alert cap the CX team can handle; the choice and its reason go into the report | [Tutorial 7 reference §8](#mspt9bk2440.17926); [G-29](#mspt9bk2440.21185) | Approved |
| 8.5 | Freeze | Write `frozen_recipe.json` (features, transforms, recipe, estimator and settings, calibration, threshold) with its hash, before the test cohort is read | Rule 3; Design s08 | Approved |
| 8.6 | Final fit | Fit the frozen recipe on all development orders whose labels were observable before the test cutoff | [Tutorial 7 §9](#mspt9bk2440.17926); label-timing rule | Approved |
| 8.7 | Test once | Score each task's test cohort once with the agreed metric list (G-24), including the dummy and plain linear/logistic references refitted the same way for comparison | [Tutorial 7 §9](#mspt9bk2440.17926); [teacher note §6](#mspt9bk2440.17339) | Approved |
| 8.8 | Bundle | `joblib` pipeline, threshold, feature schema, package versions, training-ID digest, `training_profile.json` (numeric distributions, category shares) for drift checks, checksums | [Tutorial 7 §11](#mspt9bk2440.17926); [Week 6 slides](#mspt9bk2440.18741) | Approved |

## s09 — Conclusion for the business (per task)

All results here describe the frozen model; nothing feeds back into a choice. Every claim is labelled observation, literature-supported hypothesis, or unmeasured mechanism.

| # | Analysis | Solution | Basis | Review |
| --- | --- | --- | --- | --- |
| 9.1 | Train–validation–test table | One table per task: training (fold mean), validation (selection scores, fold mean ± SD) and test, for the winner and the dummy and plain linear/logistic references. Test metrics carry 95% bootstrap intervals (1,000 resamples of test orders, seed 42). Classification also reports the absolute number of test detractors and each interval's width, so the 15% share check is not read as "enough" (G-54) | [Teacher note §6](#mspt9bk2440.17339); [Tutorial 2](#mspt9bk2440.17653) confidence intervals; [G-10](#mspt9bk2440.19722) | Approved |
| 9.2 | Gain over baselines | Winner vs dummy and vs the plain model on test, with interval on the difference (paired bootstrap) | Brief: every complex model must beat its baseline | Approved |
| 9.3 | Error analysis | Regression: errors by customer state, distance band, basket size, purchase month. Classification: precision and recall by customer state. A state is evaluated only if its test cohort holds more than 100 detractors (is\_detractor = 1); states at or below that are listed as "too few detractors to judge". Over the evaluated states, an aggregate result: pooled precision and recall, plus the mean and spread of the per-state values. Secondary slices, with the same 100-detractor rule: basket size (number of items in the order) and seller count (number of distinct sellers in the order; multi-seller orders ship in several parcels). Regression slices under 100 orders are descriptive only | [Teacher note §6](#mspt9bk2440.17339) (no aggregate-only reporting) | Approved |
| 9.4 | Drift | Training vs test: standardised mean differences of numeric features, category-share changes and the target of each task (regression lead time: mean, median and distribution; classification prevalence); flags features that moved most. The test cohorts are the newest period and differ from development; the report never describes them as drawn from the development distribution (G-77) | Week 6 slides (drift) | Approved |
| 9.5 | Interpretation | Permutation importance of the frozen model on the test cohort (description, no decisions), coefficients / odds ratios of the plain linear and logistic models, top rules of the single tree (export\_text). EDA consistency check (G-40): compare the frozen model's importance ranking, numeric and categorical features separately, with the s03 EDA ranking (Spearman rank correlation and top-10 overlap), and report it. If they diverge (rank correlation below 0.5 or fewer than 5 of the top 10 shared), the run alerts the team with a recommended action. It never changes the frozen pipeline; any change is a new release | [Tutorial 7 §10](#mspt9bk2440.17926); [Tutorial 8 §8.1](#mspt9bk2440.18516); [teacher note §5](#mspt9bk2440.17160) | Approved |
| 9.6 | Label sensitivity | Classification test metrics re-scored with the first-review label | Milestone 1 TA (label bias) | Approved |
| 9.7 | Business conclusions | Regression: what MAE means for delivery promises (e.g. buffer days by region). Classification: alerts per day at the threshold, share that are true detractors, detractors caught, illustrative cost vs no alerts. Only actions the evidence supports, each labelled observation, literature-supported hypothesis or unmeasured mechanism. E-commerce reading: (a) lead time: reliable promises matter more than fast ones, so show where predicted lead time exceeds the promised date by customer state and link it to the s03 late-vs-promised and detractor trends; (b) detractor alerts: proactive contact is a service-recovery action, and fast contact with an apology is what the recovery literature supports; (c) retention: fulfilment performance drives referrals and repeat orders, so a caught detractor is a retention opportunity. Literature (venue confirmed; read in full before citing): Griffis et al. 2012, Journal of Business Logistics (fulfilment and referrals); Amorim, Eng-Larsson & Rooderkerk 2025, Journal of Retailing (fulfilment failures delay the next order) | Brief: actionable insights; Milestone 2 overreach corrected | Approved |
| 9.8 | Limitations | Checkout-only information; fulfilled and reviewed populations; optimistic CV from the EDA-based selection; illustrative cost; no causal claims; the test cohort is a new-customer time-ordered holdout, stated with its actual share (G-48); the number of test-period orders removed by the s02 lead-time outlier rule is stated | [Teacher note §6](#mspt9bk2440.17339); [G-10](#mspt9bk2440.19722), [G-19](#mspt9bk2440.20345) | Approved |

## s10 — Release: migrate and deliver (one stage)

Order matters: parity and approval first, then migration and a matching reproduction, and only then the app, dashboard, report and slides. Deadlines: slides locked 4 Nov, report and ZIP 8 Nov.

| # | Step | Solution | Basis | Review |
| --- | --- | --- | --- | --- |
| 10.1 | Reload parity | Load each s08 bundle from disk, re-predict the test cohort, require identical predictions to the in-memory ones (`parity.json`) | [Tutorial 7 §12](#mspt9bk2440.17926); [Week 6 slides](#mspt9bk2440.18741) | Approved |
| 10.2 | Approval | Every stage card ACCEPTED with commit hash; `run_pipeline.py check` passes; team signs off; release tag `e5-release-1` | [README §9](#mspt9bk2440.21754), [§12](#mspt9bk2440.21844) | Approved |
| 10.3 | Migration | Ordered by the experiment lead: copy into the brief's layout (`data/ notebooks/ src/ deployment/ docs/`), paths only, plus a reproduction README (setup, data placement, one command) and pinned `requirements.txt` | [README §12](#mspt9bk2440.21844); [brief](#mspt9bk2440.18909) repo requirements; [G-07](#mspt9bk2440.19590) | Approved |
| 10.4 | Reproduction check | Rerun from the working folders on a clean checkout; every output hash and every number in `numbers.json` must match the release (`migration_check.json`). Nothing below starts until it matches | [G-07](#mspt9bk2440.19590) | Approved |
| 10.5 | Streamlit app | One app with three tabs: the existing business dashboard (10.6), Lead time, and Detractor risk. The two model tabs are machine-learning scope: they read only this pipeline's outputs (evidence/build; after migration, the migrated Experiment 5 data in data/business/ml, never its current Milestone 2 files), and the app computes no statistic itself (G-41). Tab contents: see "Model tab design" below the table. In the model tabs: Pick a held-out test order or enter one; show the prediction, the alert at the frozen threshold and a plain explanation of inputs. Input checks read types, allowed values and ranges from the s02 data dictionary (G-58), with clear errors (types, ranges, unknown states, no items, missing installments, impossible distance). The Detractor risk tab also takes the three inputs adopted at the s03 gate (G-70): the main product's photo count and description length, and the seller's rating at checkout (looked up from reviews answered before the order; blank for a new seller). Drift warning from `training_profile.json`; bulk CSV scoring with download. Inference never fits. Deployed on Streamlit Cloud, live URL tested before submission | [Brief](#mspt9bk2440.18909) Phase 3 deployment; [Week 6 slides](#mspt9bk2440.18741); [Tutorial 7 §13](#mspt9bk2440.17926) | Approved |
| 10.6 | Dashboard | Business dashboard tab: extend the Phase 1 dashboard (deployment/app.py), not a new build. It keeps its own scope and data: data/business/dashboard/, a general view of all orders and statuses with the Phase 1 rules (e.g. incomplete months filtered out of monthly charts). It is labelled in the app and report as a separate descriptive scope; its numbers are never mixed with model results (G-41) | Milestone 1 TA (add models to the dashboard) | Approved |
| 10.7 | Report and slides | Built from `evidence/build/` (reproduced outputs): brief's section list, every number cited by evidence ID and checked against `numbers.json`, citations verified, 15–20 pages. Slides: 10-minute story with app screenshots | [Brief](#mspt9bk2440.18909) Phase 3; [G-07](#mspt9bk2440.19590) | Approved |
| 10.8 | Walkthrough notebook | Read-only notebook that loads the released evidence and bundles and walks through every stage with markdown; no fitting | Brief: notebooks with markdown | Approved |
| 10.9 | Outputs | `parity.json`, `input_validation.json`, `migration_check.json`, app and dashboard code, app\_sources.json (every table and chart in the app mapped to its stage output and evidence ID), report and deck drafts, notebook, release notes | Design s10 | Approved |

### Model tab design (10.5)

Both tabs follow common model-dashboard practice: headline KPIs first, then where the model works and fails, then why, then scoring, then data health. Every element reads a stored output listed in app\_sources.json.

| Panel | Lead time tab (regression) | Detractor risk tab (classification) | Source |
| --- | --- | --- | --- |
| 1 Headline | MAE in days with 95% CI, share within ±3 days, gain over the dummy, test size, release tag | AP, ROC-AUC, Brier with CIs, prevalence; at the chosen threshold: alerts per day, precision, recall, detractors caught | s08 test metrics, s09 9.1–9.2 |
| 2 Fit | Predicted vs actual (hexbin), residual histogram, mean predicted vs actual by decile | PR and ROC curves, reliability curve, confusion matrix at the threshold | s08, s09 |
| 3 Policy | Promise check: share of orders whose prediction exceeds the promised date, by state | Threshold explorer (read-only): alerts per day vs precision and recall, cost curve, chosen threshold and daily cap marked | s08 threshold\_table.csv, s09 9.7 |
| 4 Where it errs | MAE by customer state (with n), distance band, month | Precision and recall by customer state (states with > 100 detractors), plus the "too few" list and the aggregate | s09 9.3 |
| 5 Why | Permutation importance, EDA-consistency badge, key s03 charts (target distribution, trends) | Permutation importance, logistic odds ratios, EDA-consistency badge, key s03 charts | s03, s09 9.5 |
| 6 Score | One order (form or held-out pick) with prediction and an interval from test residual quantiles; bulk CSV with download | One order with risk score, risk band and alert flag; bulk CSV with download | s08 bundle; inference only |
| 7 Data health | Drift table and training-period range; warning when an input is outside the training profile | Same | s09 9.4, training\_profile.json |

## Open items for the team

Each has my recommended answer; tick it when agreed, or comment.

- [x] **Decision rule (1.7):** was "mean paired improvement > 0 and wins in at least 4 of 5 folds". Resolved: replaced by the one-standard-error rule, with the fallback written into 1.7.
- [x] **Forest size (1.8, 7.4):** 200 trees. Enough for stable scores on \~70k orders and still fast; more trees rarely change the ranking.
- [x] **Alert capacity (8.4):** moved into the 8.4 hard stop. The team sets the threshold, and any daily alert cap, after seeing the alert volume and trade-off table.
- [x] **Permutation importance on test (9.5):** recommended, as description of the final model only. The alternative (last validation fold) avoids touching test but explains a slightly different fit.
- [x] **App scope (10.5):** resolved: three tabs (business dashboard, lead time, detractor risk). The project brief (IT5006 project description, Phase 3) requires a deployed app for at least one task.
- [x] **Dashboard (10.6):** resolved: extend, not rebuild. It keeps its own descriptive data scope; the model tabs use pipeline outputs only (10.5, 10.6).
- [x] **Citations:** 1.4, 1.5 and 1.7 verified against their sources (Willmott & Matsuura 2005; Saito & Rehmsmeier 2015; Brier 1950; Elkan 2001; one-SE rule). 7.4 (Breiman 2001) verified too.

## References used in this tab

Each citation in the tables above links to its entry here. "T" plus a number in a citation means a tutorial (T7 = Tutorial 7), not a row of the teacher-expectation table.

### Teacher's Milestone 2 note (the rubric)

Source: `experiments/experiment_5/spec/teacher_expectation_m2.md`.

#### Teacher note §1 — Problem scoping

One or two problems covering classification and regression; a clear business stakeholder; a target present in or derivable from Olist; every predictor known before the outcome.

#### Teacher note §2 — Data preparation

Group on `customer_unique_id` for customer-level problems; no post-outcome predictors; scikit-learn Pipelines so preprocessing is fitted inside the CV folds; a plan for an imbalanced target.

#### Teacher note §3 — Feature engineering

A rationale for every engineered feature, grounded in the Phase 1 literature where possible.

#### Teacher note §4 — Modelling

Simplest variant in each family first; every more complex model must beat its family baseline; two or three well-evaluated models beat a long list.

#### Teacher note §5 — Evaluation

Justified, cited metrics; cross-validation with documented seeds; not accuracy alone for imbalanced targets; feature importance tied to the business.

#### Teacher note §6 — Common pitfalls

No advanced model without a baseline; no random splits on temporal data; no features without rationale; error analysis, not aggregate metrics only; a train–validate–test comparison; a limitations discussion.

### Tutorials and lectures

Local copies are in `docs/Tutorial/` (not in git).

#### Tutorial 2

Question-driven EDA and confidence intervals (used for the bootstrap intervals in s09).

#### Tutorial 4

Split before preprocessing; one scikit-learn Pipeline with a ColumnTransformer.

#### Tutorial 5

Linear regression: residual analysis and regularisation (Ridge, Lasso).

#### Tutorial 7

Two notebooks. A plain section number (§5 to §13) refers to the reference solution `Logistic_Regression_Standard_Solution_non_agentic.ipynb`: §5 one end-to-end pipeline; §6 cross-validate against a baseline; §7 out-of-fold probabilities; §8 threshold from business costs; §9 fit on all training data, then evaluate once; §10 interpret the coefficients; §11 save the decision artifact; §12 reload and score new cases; §13 production QA and input validation. A dotted number refers to `T07_Main.ipynb`: §6.3 ROC and precision–recall curves; §7 model diagnostics; §7.1 learning curves.

#### Tutorial 8

`T08_Classficiation_Models.ipynb`: §5 baseline comparison and GridSearchCV; §6 evaluation; §7 diagnostics; §8 decision tree, with its tuning cell; §8.1 readable tree rules; §9 random forest; §10 all models compared.

#### Week 6 slides

Training, deployment, drift and bulk scoring.

#### Lecture 5

Cited beside learning curves; the exact slide still needs checking.

### Project brief and TA feedback

#### Project brief

[IT5006 project description](https://prakashsukhwal.github.io/IT5006/IT5006_Project_Description_2026Aug_V2.html): Phase 2 modelling guidance and the Phase 3 deliverables (report, slides, deployed app, dashboard, reproducible repository).

#### Milestone 1 TA feedback

`docs/Project/Milestone1/TA Feedback.txt`. Points used here: cited metric rationale, stakeholder actions, and the label sensitivity check.

### Decision log (G-numbers)

Source: `experiments/experiment_5/spec/blueprints/decision_log.md`.

#### G-05

Class weight (None vs balanced) is a tuning-grid option for the classifiers, not a training step.

#### G-06

Choose the model on threshold-free scores first, then check calibration, then set the threshold from out-of-fold predictions, then fit once and test once.

#### G-07

Report, slides and dashboard cite the reproduced outputs, and are built only after the reproduction check matches the release.

#### G-10

Cross-validation scores are reported as selection scores only; the test cohorts give the only held-out estimate.

#### G-36

Log transforms are always on, decided from EDA: log1p on every non-negative input with pre-cutoff skewness above 1 (all models) and on the regression target, scored on raw days. They are not tested on the folds; s06 compares families only. Supersedes G-15. Refined by G-47 and G-62: only total\_price, total\_freight, total\_weight\_g, total\_volume\_cm3 and distance\_km\_max can be logged.

#### G-16

Calibration is a candidate component: raw by default; a sigmoid variant, fitted inside the training folds, is scored as a complete candidate if reliability fails.

#### G-35

`order_estimated_delivery_date` (promised lead days) is never a feature or a reference model: in production the promised date would come from the task 1 prediction itself. It only describes late-vs-promised trends in s03. Supersedes G-17.

#### G-19

Features selected by one EDA importance ranking per task, computed once on pre-cutoff orders, up to the team's cumulative threshold (95% or 99%). This is a declared exception, so CV scores of the selected set are optimistic.

#### G-20

Populations: zero-item orders out of both tasks; classification uses orders not cancelled or unavailable and with a valid review; orders with missing installments removed and rejected by the app.

#### G-22

Calendar fields are numeric; log1p for every non-negative numeric feature with pre-cutoff skewness above 1, and for the regression target. Refined by G-47 and G-62: only the five contract candidates can be logged.

#### G-24

Test metrics. Regression: MAE, RMSE, R², share within ±3 days. Classification: AP, ROC-AUC, Brier, confusion matrix, precision/recall/F1 at the threshold, illustrative cost, prevalence baseline. A training-data profile is saved in the bundle for drift checks.

#### G-29

No Milestone 2 result or metric is reused; every count, threshold, cutoff and score is recomputed. Milestone 2 code may be reused as logic only.

### Design rules and README

#### Rule 5

Design rule 5, simplest first: a more complex variant is kept only if it passes the decision rule; otherwise the simpler one stays.

#### README §5.3

Candidates and the pipeline factory: every model is built by `e5lib.factory.build` as a whole pipeline.

#### README §5.5

Standard output files: `metrics_long.csv`, `predictions.csv.gz`, `decision.json`, `counts.json`, figures with sidecar data, run manifest.

#### README §9

Stage gates and change control, including the special rule for the test cohort.

#### README §12

Migration to the working folders, only after full approval by the experiment lead.
