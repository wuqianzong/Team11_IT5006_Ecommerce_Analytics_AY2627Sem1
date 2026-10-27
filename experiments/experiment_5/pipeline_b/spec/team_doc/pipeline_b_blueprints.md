# Pipeline B blueprints — B2 to B8, joint test T1, B9

**Status: DRAFT · 2026-10-23.** One blueprint per B stage, drafted from the approved CR-054. Each lists only what B changes; everything else is inherited from Pipeline A at tag e5-A-frozen. No B code is written until a blueprint is AGREED. Repo copy: experiments/experiment\_5/pipeline\_b/spec/blueprints/. **Decided 2026-10-23:** B5, fold 1 is expected to fall below A's minimum of 10,000 training rows; A's five folds are kept and the shortfall is a recorded deviation (B-G-01, B5 section 6).

## B2 — population and history features

| Field | Value |
| --- | --- |
| Stage | B2, Pipeline B (G-79, CR-054 B-C1 to B-C9) |
| Nodes | regression, classification |
| Status | AGREED (experiment lead, 2026-10-23: follows plan v3 and Henry's comments); round 2 changes B-G-03, B-G-04 |
| Inherits from A | s02 `records.csv.gz` (tag e5-A-frozen), A's test cutoffs, raw Olist tables (read-only) |

### 1. Goal and gate

Goal: apply B's population rules and build B's history features for the development rows of each task, with no information from after the prediction time. Gate: every history value uses only events completed before the row's prediction week; the estimated delivery date is read nowhere; counts reconcile with A's s02.

### 2. Inputs

- `../../stages/s02_data/common/outputs/records.csv.gz` (A, accepted).
- Raw tables: orders, order\_items, sellers, customers (`data/raw/`, read-only).
- A's test cutoffs (`spec/protocol.yaml` data\_dependent.test\_cutoffs).

### 3. Method

1. **Population (B-C1 to B-C5)**, applied to A's task-eligible rows, each removal with a reason code in `exclusions_B.csv`:
   - B\_STATE: customer or primary seller state outside SP, MG, RJ, PR, RS, BA, SC, or missing;
   - B\_DISTANCE: distance\_km\_max missing;
   - B\_LEAD\_CAP (regression): lead\_days > mean + 8 × SD of lead\_days on B's own development rows after B\_STATE and B\_DISTANCE (B-G-03; computed each run, recorded in feature\_build\_log.json; no floor);
   - B\_NO\_HANDOVER (classification): no carrier handover date;
   - B\_REVIEW\_BEFORE\_HANDOVER (classification): review answered at or before handover;
   - B\_WARMUP: purchased before 2017-02-12 (first six weeks), removed after the features are built.
2. **Prediction time.** Regression: purchase time. Classification: carrier handover time.
3. **Events.** One row per raw order purchased before the task's test cutoff: primary seller (highest price, then lowest item id, A's rule), last shipping limit, carrier date, delivery date, route = seller\_state + "->" + customer\_state. The estimated delivery date column is dropped on load.
4. **Weeks.** Calendar weeks, Monday to Sunday. A handover event counts in its carrier-date week; a delivery event in its delivery week. A row uses only complete weeks before its prediction week.
5. **Features (B-C6 to B-C9)**, all candidates for both tasks unless stated: Feature names (B-G-04) are in brackets.
   - route (categorical) \[route\_seller\_to\_customer\_state\];
   - prior seller late-handover rate, prior seller late-handover days, prior seller dispatch days (B-C7) \[seller\_prior\_late\_handover\_rate, seller\_prior\_late\_handover\_days, seller\_prior\_dispatch\_days\]: mean over all of the seller's earlier handover weeks; a seller with no history takes the weighted 3-week mean of sellers in the same seller state;
   - recent route delivery days (B-C8) and recent route carrier transit days (B-C8b) \[route\_recent\_delivery\_days, route\_recent\_carrier\_transit\_days\]: weighted 3-week mean (0.5, 0.3, 0.2 for weeks w−1, w−2, w−3) of the route's weekly median, the weights renormalised over the weeks that have events; fewer than 10 route events in the 3 weeks → 0.7 × seller state's + 0.3 × customer state's weighted 3-week mean, then the overall one;
   - classification only (B-C9): this order's handover late flag, late days and dispatch days \[order\_handed\_over\_late, order\_handover\_late\_days, order\_dispatch\_days\].
6. **Test rows.** B2 builds features for development rows only. Test-row features are built in the joint test run, from events known before each test row's prediction week.

### 4. Outputs (per task, `pipeline_b/stages/b02/<task>/outputs/`)

`records_B.csv.gz` (development rows, A's columns + B's), `exclusions_B.csv`, `exclusion_counts_B.csv`, `history_coverage.csv` (share of rows on own history vs each fallback, per quarter), `lateness_summary_B.csv.gz` (descriptive, Henry: by route, week and seller with customer state and seller state — handover count, late-handover rate, mean late-handover days, median carrier transit days and median delivery days; seven-state routes only (B-G-03), events before the cutoff only; any A comparison filters A to the same seven states), `feature_build_log.json`.

### 5. Checks

- Every history value uses events whose week is before the row's prediction week (asserted per row).
- No column derived from order\_estimated\_delivery\_date exists.
- Development rows ⊆ A's development rows; removal counts add up per reason.
- No test row is in records\_B.csv.gz.
- Two runs give byte-identical outputs.

## B4 — features

| Field | Value |
| --- | --- |
| Stage | B4, Pipeline B (CR-054 B-C11, B-C12) |
| Nodes | regression, classification |
| Status | AGREED (experiment lead, 2026-10-23); round 2 change B-G-02 |
| Inherits from A | s04 method and code (pool, transforms, duplicate rule, selection at 99%), A's recipes.json conventions |

### 1. Goal and gate

Goal: rank B's feature pool on B's development rows with A's method, keep the features that reach 99% of the cumulative importance, and write B's recipes and feature dictionary. Gate: the selected set follows the 99% rule exactly; every B feature is documented.

### 2. Inputs

- B2 `records_B.csv.gz` per task.
- A's task pool (`e5lib.contract.pool(task)`: 24 predictors; classification + the three adopted).
- A's s04 transforms and duplicate rule (`e5lib.features`, read-only).

### 3. Method

1. **Pool.** A's task pool + B's candidates (B-C6 to B-C9; names B-G-04); route counts as one feature.
2. **Ranking.** A's ranking on B's development rows: |Spearman| with the log target for regression, mutual information for classification, as in A's s03/s04.
3. **Selection (B-C11).** Keep the top features reaching 99% of the cumulative share (A's G-70 threshold). A feature below the cut is dropped with its rank and share recorded.
4. **Transforms.** A's rules: log1p for skewed counts and all day counts; rates and flags scaled only; route one-hot (drop-first for linear/logistic, every level for trees); A's duplicate rule; imputation fitted inside the folds. B-G-02: with route in the pool, customer\_state and primary\_seller\_state are dropped in the reduction as nested in route; no route-median fill for distance\_km\_max, which B-C2 leaves never missing.
5. **Recipes.** One recipe per family (dummy, linear/logistic, tree, forest), built with A's code.

### 4. Outputs (per task, `pipeline_b/stages/b04/<task>/outputs/`)

`selection_ranking_B.csv`, `selected_features_B.json`, `recipes_B.json`, `feature_dictionary_B.csv` (B-C12: name, scope, definition, formula, reason, transform, rank, share, kept or dropped with reason), `design_matrix_B.csv`.

### 5. Checks

- The ranked set equals B's pool; the kept set is exactly the 99% prefix.
- Every kept feature has a feature\_dictionary\_B.csv row with formula and reason.
- The linear/logistic design matrix is full rank.

## B5 — partition (blueprint)

| Field | Value |
| --- | --- |
| Stage | B5, Pipeline B |
| Nodes | regression, classification |
| Status | AGREED (experiment lead, 2026-10-23); built and accepted (tag e5-B-s05-accepted) |
| Inherits from A | s05 folds.csv (fold boundaries and membership), A's test manifest, A's minimums |

### 1. Goal and gate

Goal: keep A's five time-ordered folds, restricted to B's rows, so A and B are compared on the same periods. Gate: every B row sits in A's fold of the same order; minimums checked and any shortfall recorded.

### 2. Inputs

- A `stages/s05_partition/<task>/outputs/folds.csv` and `test_manifest.csv`.
- B2 `records_B.csv.gz`.

### 3. Method

1. B folds = A's folds ∩ B's development rows (order\_id); no new boundaries.
2. Class support and size per fold against A's pre-registered minimums (protocol cv.minimums: 10,000 training rows per fold; classification 100 detractors per training and validation part).

### 4. Outputs (per task, `pipeline_b/stages/b05/<task>/outputs/`)

`folds_B.csv`, `fold_summary_B.csv`, `checks.json`.

### 5. Checks

- Every B row keeps A's fold and role.
- No test row is in a B fold.
- Minimums: PASS, or FAIL recorded with the team's decision.

### 6. Decision: fold 1 below the minimum (B-G-01, 2026-10-23)

Fold 1 is expected to fall below 10,000 training rows once B's scope removes about a fifth of the orders. **Decided by the experiment lead: keep A's five folds unchanged and accept fold 1's shortfall as a recorded deviation** (as G-75 for A's test check), so the A–B comparison stays on identical periods and G-79's 5-fold mean is unchanged. Not chosen: dropping fold 1 (loses a fifth of the evidence and changes A's accepted 5-fold basis) and merging folds 1–2 for B only (breaks the like-for-like comparison).

Safeguards: (1) B5 measures the real sizes; if fold 1 has fewer than 5,000 training rows, or (classification) fewer than 300 training detractors, B5 stops and the team decides again; the 100-detractor minimum per part stays a hard check. (2) The observed counts go into human\_decisions\_B.yaml b05 once B5 has run. (3) B8 shows the adoption comparison on all five folds (the decision) and on folds 2–5 (description only).

## B6–B7 — training and tuning (blueprint)

| Field | Value |
| --- | --- |
| Stage | B6, B7, Pipeline B |
| Nodes | regression, classification |
| Status | AGREED (experiment lead, 2026-10-24); built and accepted (tags e5-B-s06-accepted, e5-B-s07-accepted) |
| Inherits from A | everything: e5lib/training.py and tuning.py, families, s06 settings, s07 grids, one-SE rule, metrics, seed 42 |

### 1. Goal and gate

Goal: run A's training ladder and tuning, unchanged, on B's rows, recipes and folds. Gate: same as A's s06 and s07; only the inputs differ.

### 2. Inputs

B4 `recipes_B.json`, B5 `folds_B.csv`, B2 `records_B.csv.gz`, A's protocol settings and grids.

### 3. Method

- B6: dummy, plain linear/logistic, single tree, forest; the basic-to-complex ladder under the one-SE rule; paired gains as description; residual and classification diagnostics; learning curves (A's s06 code, read-only).
- B7: A's grids per family; one-SE choice inside each grid and against the plain B6 model (G-55) (A's s07 code, read-only).

### 4. Outputs

As A's s06 and s07, under `pipeline_b/stages/b06/` and `b07/`, with evidence IDs B6.x and B7.x.

### 5. Checks

As A's s06 and s07, plus: the code imported from e5lib matches A's foundation hash at e5-A-frozen.

### 6. Reviews

The experiment lead accepts B6 and B7 after a brief review; the team reviews B6–B8 together at the B8 gate (as G-78).

## B8 — selection, gate and freeze (blueprint)

| Field | Value |
| --- | --- |
| Stage | B8, Pipeline B (G-79; CR-054 B-C10, B-C13) |
| Nodes | regression, classification |
| Status | AGREED (experiment lead, 2026-10-24); built, decided and frozen (tag e5-B-frozen; B-G-05) |
| Inherits from A | e5lib/selection.py (finalists, one-SE recommendation, calibration, threshold table, freeze) |

### 1. Goal and gate

Goal: choose B's model, calibration and threshold at a human gate, compare B with A on the same rows (G-79 adoption rule), and freeze B without reading the test. Gate: team decisions in `human_decisions_B.yaml` b08; frozen\_recipe\_B.json written before any test row is read.

### 2. Method

1. **B8.1–B8.4** as A's 8.1–8.4 (finalists, one-SE recommendation, calibration raw vs sigmoid, threshold table) on B's rows. The daily alert cap is decided again for B, because B's scope and prediction time differ from A's.
2. **Adoption comparison (G-79).** Per task: A's frozen recipe (e5-A-frozen) refitted per fold on A's training rows and scored on B's validation rows, against B's recommended model on the same rows. B is adopted for a task when its 5-fold mean beats A's, even by a thin margin. Paired gains are shown beside it, and the same comparison on folds 2–5 as description only (B-G-01). Whatever the result, A and B both go to the joint test run.
3. **Missed-dispatch rule (B-C10).** Orders whose shipping limit passed with no handover, counted on the development period: flagged orders, detractors among them, precision and the share of all detractors caught.
4. **Freeze (B8.5).** frozen\_recipe\_B.json with its sha256, as A's 8.5.

### 3. Outputs (per task, `pipeline_b/stages/b08/<task>/outputs/`)

As A's s08 gate and freeze, plus `adoption_comparison.csv` and (classification) `missed_dispatch_rule.csv`.

### 4. After the freeze

The joint test run (A's 8.6–8.8 and B8.6–B8.8 together) and the fold-by-fold table (B-C13) have their own blueprint, below (AGREED; run once, tag e5-T1-tested).

## Joint test T1 — A and B, one test read (blueprint)

Repo copy: `experiments/experiment_5/pipeline_b/spec/blueprints/joint_test.md`.

| Field | Value |
| --- | --- |
| Stage | T1 joint test run (G-79; A's 8.6–8.8 and B8.6–B8.8; CR-054 B-C13) |
| Nodes | regression, classification |
| Status | AGREED (experiment lead, 2026-10-24; J-1 = (a), the recommended option) |
| Inputs frozen | A: `../../stages/s08_selection/<task>/outputs/frozen_recipe.json` at e5-A-frozen; B: `stages/b08/<task>/outputs/frozen_recipe.json` at e5-B-frozen |

### 1. Goal and gate

Goal: score both frozen pipelines on the test cohort exactly once, in one run, with the agreed metrics, plus A on B's test rows (like-for-like), and build the bundles for release. Gate: the run refuses to start unless both frozen recipes exist and their sha256 values match the tagged files; it reads the test cohort once and writes a test-read record; a second run that reads the test again is a deviation and must be recorded as such.

### 2. Where the outputs go (changes the overview's step 7)

`pipeline_b/stages/t1_joint_test/<task>/outputs/`, with sub-results for A and B. A's frozen tree (`../../stages/`) is **not** written, so A stays FRESH and matches e5-A-frozen. The overview tab said "test outputs in both trees"; this blueprint replaces that with one joint folder (README rule 1: B never writes in A's folders).

### 3. Method

1. **Check the freezes.** Recompute both sha256 values; refuse on any mismatch.
2. **Final fit (A 8.6, B8.6).** Each frozen recipe is fitted once on all its development orders whose labels were observable before the task's test cutoff (A: A's eligible development rows; B: B2 rows with the same label rule). Classification fits include the frozen calibration (sigmoid for both; B-G-05) with time-ordered inner splits, as in 8.3.
3. **Test rows.**
   - A: A's test cohort from `test_manifest.csv` (s05), unchanged.
   - B: A's test cohort filtered by B's population rules B-C1 to B-C5 (CR-054 §6). The B-C3 cap uses the value frozen from B's development rows (83.66 days, B2 feature\_build\_log.json), never recomputed on the test. Removal counts are recorded per rule.
   - B's history features for test rows use only events completed before each row's prediction week, as in B2. **Decision for the lead (J-1):** (a) the history includes events from earlier in the test period, as it would in deployment (recommended), or (b) the history is frozen at the test cutoff, which is more conservative but stale for later test weeks. Either way a row's own label is never used.
4. **Test once (A 8.7, B8.7).** Score with the G-24 metric list on:
   - A's model on A's test rows;
   - A's model on B's test rows;
   - B's model on B's test rows. References (dummy, plain linear/logistic) are refitted the same way. For classification, the frozen thresholds (1/6, cap 25) are applied to the calibrated probabilities; the confusion matrix, precision, recall, F1, alerts per day and illustrative cost are reported. The test-size checks G-46/G-54/G-75 are reported for B's test cohort, and a shortfall is reported, not fixed.
5. **Bundles (A 8.8, B8.8).** `joblib` pipeline, threshold, feature schema, package versions, training-ID digest, `training_profile.json` and checksums, for both A and B. B's bundle is the one released (G-79).
6. **Fold-by-fold and test table (B-C13).** One table per task: a row per validation fold (dates, festival weeks marked) and a test row, A and B side by side. Fold rows are labelled selection scores (G-10); only the test row is unbiased.

### 4. Outputs (per task)

`test_read.json` (time, row counts, sha256 of both recipes, "read once"), `test_rows_B.csv` (B's test rows with removal reasons), `metrics_test.csv` (model × rows × metric), `predictions_test.csv.gz`, `confusion_test.csv` (classification), `fold_and_test_table.csv` (B-C13), bundles under `bundles/A/` and `bundles/B/`. Evidence IDs T1.1 to T1.6.

### 5. Checks

- Both recipes' sha256 equal the tagged files; no recipe field changes after the read.
- Test rows equal A's manifest (A) and A's manifest after B's rules (B); no development row is among them.
- B's test-row features use only events completed before each row's prediction week (the same brute-force check as B2.4/B2.5, on a sample).
- Reloading each bundle and re-predicting the test rows gives identical predictions (as A's 10.1).
- A's tree stays FRESH; A's code matches e5-A-frozen.

### 6. After the run

No model, calibration or threshold changes after the read (G-79: the test does not re-choose). A later threshold change (Henry: "may adjust after s10") is reported as a post-test change, with the frozen-threshold test result kept as the unbiased one. B9/B10 (conclusion and release) follow as one combined blueprint: B gets the full analysis; A appears only as the baseline and in the comparison.

## B9 — conclusion, B primary, A as baseline (blueprint)

Repo copy: `experiments/experiment_5/pipeline_b/spec/blueprints/b09_conclusion.md`.

| Field | Value |
| --- | --- |
| Stage | B9 conclusion (G-79 join plan; A's s09 blueprint `../../../spec/blueprints/s09_conclusion.md` adapted to B) |
| Nodes | regression, classification |
| Status | AGREED (experiment lead, 2026-10-24; B9-D1 to B9-D4 as recommended) |
| Inputs frozen | T1 at tag e5-T1-tested (runs 20261024T044531Z, 20261024T044555Z); B8 at e5-B-frozen; B4, B5 accepted runs (EVIDENCE.md) |

### 0. Scope (experiment lead, 2026-10-24)

This stage finishes the implementation and writes a conclusion **for team review**. It does not build the report, the deck, the dashboard or app, or the reproduction package. Those, and the release work of A's s10 (B10), start only after the team confirms the conclusion. The T1 bundles already exist; B10 will package B's bundle.

### 1. Goal and gate

Goal: describe what B's frozen models achieve on the test, where they fail, why they predict what they predict and what the business can do with them, with A as the baseline. Nothing here feeds back into a model, calibration or threshold choice (G-79: the test does not re-choose). Every claim is labelled as an observation, a literature-supported hypothesis or an unmeasured mechanism. Gate: the team reviews the conclusion tab and confirms (or asks for changes) before B10, the report, the deck and the dashboard start.

### 2. Inputs (read only; no refit, no second test read)

- T1 `predictions_test.csv.gz` (every model × rows), `metrics_test.csv`, `fold_and_test_table.csv`, bundles.
- Test-row attributes for slices: A's s02 records for the T1 test order IDs (customer state, distance, basket size, seller count, purchase month, first-review label), and B's test-row features rebuilt with T1's `b_rows` (verified builder). Check: B's bundle re-predicts the rebuilt rows exactly as `predictions_test.csv.gz` (otherwise stop).
- B6–B8 fold scores (training and validation means), B4 `selection_ranking_B.csv`, B8 `missed_dispatch_rule.csv`.

### 3. Method

1. **Train–validation–test table (B9.1; B-C13, T-06).** Per task, for B's frozen model, A's frozen model (on A's rows and on B's rows) and the plain and dummy references: training mean, validation selection score (mean ± SE, labelled G-10), test score with a 95% bootstrap interval (1,000 resamples of test orders, seed 42). Classification adds the absolute number of test detractors and each interval's width (G-54).
2. **B versus A on the same rows (B9.2).** Paired bootstrap interval on the test difference (B minus A on B's test rows) for MAE and AP, plus RMSE, R², within\_3d, ROC-AUC and Brier; B versus its dummy and plain references the same way.
3. **Error analysis (B9.3; G-40, T-05).**
   - Regression: absolute error of A and B by customer state, route (seller → customer state), distance band, basket size and purchase month; slices under 100 orders descriptive only.
   - Classification: precision and recall at 1/6 by customer state and route, judged only with more than 100 test detractors (others "too few to judge"); pooled and mean ± spread over the judged slices; secondary slices basket size and seller count.
   - Where B gains most and where it does not (gain by slice, same rule).
4. **Drift (B9.4; G-77).** Final-fit rows vs test rows: standardised mean differences of B's numeric features, category-share changes, target shift (lead time; prevalence). Includes B's history features and their source shares (own history vs fallbacks) on test vs development. Feeds point 2 of the T1 tab (why the regression test gain exceeds the CV gain): described, not tested.
5. **Interpretation (B9.5; T-04).** Coefficients (regression, log scale) and odds ratios (classification) of B's frozen models with their transforms; permutation importance of B's frozen model on B's test rows (description only); comparison with B4's selection ranking (Spearman and top-10 overlap; on divergence the run alerts the team, never changes the model).
6. **Label sensitivity (B9.6).** Classification test metrics re-scored with the first-review label.
7. **Business conclusions (B9.7; T-08).**
   - Regression: what B's MAE and within\_3d mean for delivery promises, by customer state.
   - Classification: alerts/day at 1/6 (cap 25), the share that are detractors, detractors caught, illustrative cost vs no alerts, for B and A (T1.4); the missed-dispatch rule (B-C10) on the test period beside the classifier.
   - Each recommendation traced to a file and evidence ID.
8. **Limitations (B9.8; T-07).** Seven-state scope; different prediction moments (checkout for regression, handover for classification); fold-1 deviation (B-G-01); history from earlier test weeks (J-1 a); sigmoid deviation (B-G-05); test drift (G-77) and A's test detractor shortfall (G-75); illustrative cost; no causal claims.
9. **Conclusion (B9.9).** One page per task in `conclusion.md` and in the doc tab: the answer, the evidence, the limits, and the questions for the team (including whether to revisit the threshold after the test, which would be reported as a post-test change).

### 4. Decisions for the lead and team

| ID | Question | Recommendation | Status |
| --- | --- | --- | --- |
| B9-D1 | Slices and the 100-detractor rule | As A's s09 (G-40), plus route for B | Agreed |
| B9-D2 | Permutation importance data | B's test rows, description only (as A's s09-D3) | Agreed |
| B9-D3 | A's single-tree rules (A's 9.5) | Dropped: neither frozen model is a tree | Agreed |
| B9-D4 | A's EDA consistency check against s03 | Replaced by the check against B4's ranking (B-C11) | Agreed |

### 5. Outputs (per task, `pipeline_b/stages/b09/<task>/outputs/`)

`train_val_test.csv`, `paired_test_differences.csv`, `subgroups.csv` (judged / too-few flag, aggregates), `drift.csv`, `coefficients.csv`, `permutation_importance.csv`, `ranking_consistency.json`, `label_sensitivity.csv` (classification), `business_summary.csv`, `conclusion.md`, figures with sidecar data. Evidence IDs B9.1 to B9.9.

### 6. Checks

- No refit and no threshold change: B's bundle re-predicts the T1 predictions exactly.
- Every test number equals the T1 value it restates (metrics\_test.csv).
- Validation scores are labelled selection scores; only test numbers are called unbiased.
- Every recommendation names its file and evidence ID.

### 7. After B9

Team review in the doc (B9 tab and sub-tabs). On confirmation: B10 release (bundle packaging, app), then the report, deck, dashboard and reproduction, and the DOC\_GAPS.md pass.

## B10 — release of B's frozen models, with A as fallback (blueprint)

Repo copy: `experiments/experiment_5/pipeline_b/spec/blueprints/b10_release.md`.

| Field | Value |
| --- | --- |
| Stage | B10 release (G-79; A's s10 blueprint `../../../spec/blueprints/s10_release.md` adapted to B) |
| Nodes | regression, classification |
| Status | AGREED 2026-10-26: scope B10.1–B10.7 and B10-D1 to D7 by the experiment lead (Wu Qianzong); B10-D8 (4/15; B-G-09 withdrawn), D9, D10 (no refit) and D11 by Henry for the team. Round 2 (2026-10-26): back to 4/15. Drafted by Henry's Claude |
| Inputs frozen | T1 at tag e5-T1-tested (runs 20261024T044531Z, 20261024T044555Z); B8 at e5-B-frozen; A at e5-A-frozen; B9 at e5-B-s09-accepted (runs 20261025T132406Z, 20261025T132538Z) |

### 0. Scope

B10 turns the frozen T1 bundles into a release package that an app can serve, and proves that the package predicts exactly what T1 predicted. It covers A's 10.1 (parity), the serving rule (B-G-06) and threshold (B-G-07), A's 10.5 input checks, the drift profile and the map of every app element to its source. Everything stays in `pipeline_b/`.

Not in B10 (later, each only when ordered): the release tag `e5-release-1` and team sign-off (A's 10.2), migration into the working folders (10.3, experiment lead only, README §12), the reproduction check (10.4), the Streamlit app build and live URL (10.5–10.6), the report and slides (10.7), the walkthrough notebook (10.8).

### 1. Goal and gate

Goal: one release package per task (B's bundle, A's bundle as fallback, the serving rule, both thresholds, input checks, drift profile, app sources), each file with its sha256. Gate: every bundle re-predicts T1's saved test predictions within 1e-9 (B-G-08); every sha256 matches the frozen and tagged files; no model, calibration or threshold changes; the team reviews the package and confirms the expected alert volumes before any app is built.

### 2. Inputs (read only; no refit, no scoring of the test cohort)

- T1 `stages/t1_joint_test/<task>/outputs/`: `bundles/A/` and `bundles/B/` (`model.joblib`, `schema.json`, `training_profile.json`), `predictions_test.csv.gz`, `test_rows_B.csv`, `test_read.json`.
- Frozen recipes: B `stages/b08/<task>/outputs/frozen_recipe.json` (e5-B-frozen); A `../../stages/s08_selection/<task>/outputs/frozen_recipe.json` (e5-A-frozen).
- Test-row features rebuilt with T1's verified builder (`e5b.t1_joint_test.b_rows`), as B9 does; the labels are not read (B-G-08).
- B9 outputs: `threshold_options.csv` (B9.10), `a_fallback_by_scope.csv` (B9.15), `drift.csv` (B9.4), `residuals_summary.csv` (B9.16), `business_by_route.csv` (B9.13), `subgroups.csv` (B9.3).
- A's s02 `../../stages/s02_data/common/outputs/data_dictionary.csv` (types, ranges, allowed values; G-58).
- For R-14 (B10-D7): B2 `records_B.csv.gz` (development rows, observed outcomes only).

### 3. Method

1. **Reload parity (B10.1; A's 10.1; B-G-08).** Load each of the four bundles from disk (A and B, both tasks) and re-predict T1's test rows: A on A's test rows, A on B's test rows, B on B's test rows, features rebuilt with `b_rows`. Each prediction equals the saved value in `predictions_test.csv.gz` within 1e-9, row by row; any mismatch stops the stage. No label is read, no metric is computed. This is also the acceptance test of the Python 3.13.7 environment.
2. **Release manifest (B10.2).** Per bundle: sha256 of `model.joblib`, `schema.json`, `training_profile.json`; the frozen recipe's sha256 against `schema.json` `frozen_sha256` and against the file at its tag; feature lists, model id, calibration, training rows, training-ID digest; the package versions in `schema.json` against the running environment (any difference is listed; a difference that changes a prediction already fails B10.1).
3. **Serving configuration (B10.3; B-G-06, B-G-07, B10-D2).**
   - Scope rule, per order: customer state and primary seller state both in SP, MG, RJ, PR, RS, BA, SC, and `distance_km_max` present → B; otherwise → A. Regression predicts at checkout for both. Classification: B at carrier handover, A at checkout. In-scope orders not yet handed over get no score; the missed-dispatch rule (B-C10) flags them once the shipping limit passes; A is not used for them (B10-D9).
   - Thresholds (classification): B operating 4/15 (B-G-07), B frozen 1/6 kept beside it; A fallback at A's frozen 1/6 (B10-D2).
   - Results at both B thresholds, without refitting anything (B10-D10): alerts/day, precision, recall, FP/TP, cost 5:1 and 1:1, confusion counts.
     - Validation (out-of-fold): B at 1/6 and at 4/15 restated exactly from B9 `threshold_options.csv`; A out of scope at 1/6 derived from B9.15's fold rows (TP = recall × detractors, alerts = TP / precision; checked to be whole numbers), days from A's s05 folds.
     - Test (post-test view): B at 1/6 and 4/15 from T1's saved predictions; both rows must equal B9 `threshold_options.csv`. A out of scope at 1/6: alerts counted from T1's saved predictions, precision and recall restated from B9.15.
     - The combined daily volume: B in scope at 4/15 plus A out of scope at 1/6, re-confirmed by the team (Henry, 2026-10-26; B10-D2).
4. **Router (B10.4).** `e5b/serving.py`: `predict(order) -> {prediction, alert, threshold_name, model, scope_reason}`. It validates the input (B10.5), applies the scope rule, calls the matching bundle and applies the configured threshold. It never fits. Tests: every T1 test row routed through it gives T1's saved prediction (same tolerance), and each scope reason is exercised.
5. **Input checks (B10.5; A's 10.5).** Per bundle schema: column present, type, range or allowed values (from `data_dictionary.csv` and the training profile), unknown state or category, no items, missing instalments, impossible distance; clear error messages. Written as `input_validation.json` with one test case per rule, run through the router.
6. **Drift profile (B10.6).** Per bundle: the training profile (mean and SD per numeric feature, category shares) and the out-of-profile rule for the app (a numeric value beyond a set number of SDs, a category unseen in training), with B9.4's drift table as the reference for the test period. The limit is 4 SD (B10-D11, Henry 2026-10-26): a warning only, the order is still scored.
7. **App sources (B10.7).** `app_sources.json`: every number and chart the model tabs will show (A's s10 panel list, adapted to B: headline, fit, policy at 1/6 and 4/15, where it errs, why, score, data health), mapped to its output file and evidence ID; the app computes no statistic. Plus R-14 (B10-D7): `top_routes_categories.csv`, observed outcomes by time window on development rows (top 5 routes and categories, minimum volume per window), with the coefficient as a second column; data only, charts with the app.

### 4. Outputs (per task, `pipeline_b/stages/b10/<task>/outputs/`)

`parity.json`, `release_manifest.json`, `serving_config.json`, `input_validation.json`, `drift_profile.json`, `app_sources.json`, `top_routes_categories.csv` (R-14), checks and manifest. Code: `e5b/b10.py`, `e5b/serving.py`; `b10` added to `STAGES` in `e5b/env.py` and `BUILT` in `b_run.py`; tests in `pipeline_b/tests/` (router, parity, evidence register). Evidence IDs B10.1 to B10.7.

### 5. Checks

- Parity: all four bundles re-predict T1 within 1e-9, row counts equal T1's; no label column read.
- sha256 of every bundle file and frozen recipe matches T1, B8 and the tagged files.
- `schema.json` thresholds unchanged (1/6); 4/15 lives only in `serving_config.json`.
- B's 1/6 and 4/15 test results from T1's saved predictions equal B9 `threshold_options.csv`; A's out-of-scope validation counts derive exactly from B9.15.
- No frozen recipe is refitted anywhere in B10 (B10-D10).
- Router reproduces T1's predictions on every test row; every scope reason covered by a test.
- Every number in `serving_config.json` equals the B9 or T1 value it restates.
- Every app element in `app_sources.json` names an existing file and evidence ID.
- A's tree untouched: A's code matches e5-A-frozen.
- Clean rerun on the committed code (`dirty: false`), byte-identical outputs.

### 6. Decisions

| ID | Question | Recommendation | Status |
| --- | --- | --- | --- |
| B10-D1 | Re-predicting T1's test rows for parity vs "never read the test cohort again" | Allowed for parity only: no labels, no scoring | Agreed (B-G-08; experiment lead 2026-10-26) |
| B10-D2 | Threshold for A's alerts on out-of-scope orders | A's own frozen 1/6 (B-G-07 is for B only); `serving_config.json` shows the expected out-of-scope alerts/day at 1/6 and the combined volume | Agreed (lead 2026-10-26); volumes re-confirmed for 4/15 (Henry for the team, 2026-10-26) |
| B10-D3 | What the app can score | Held-out historical orders with features rebuilt by T1's builder; no free-form input | Agreed (lead 2026-10-26) |
| B10-D4 | Handover facts for classification | Stored orders only (follows D3) | Agreed (lead 2026-10-26) |
| B10-D5 | Where the app code lives | Inside `pipeline_b/` until the lead orders migration; live URL after migration | Agreed (lead 2026-10-26) |
| B10-D6 | Tags | `e5-B-s10-accepted` on the branch after approval; `e5-release-1` waits for migration | Agreed (lead 2026-10-26) |
| B10-D7 | R-14 top routes and categories | Data output only (observed outcomes, minimum volume, coefficient as second column); charts with the app | Agreed (lead 2026-10-26) |
| B10-D8 | Operating threshold value | 4/15 as recorded in B-G-07. On 2026-10-26 5/14 was first recorded as B-G-09; Henry then confirmed 5/14 was a typo, so B-G-09 is withdrawn and B10 is rerun (round 2) | Agreed (Henry, 2026-10-26) |
| B10-D10 | Validation figures need out-of-fold probabilities; rebuilding them refits the frozen recipe, and on Henry's machine the refit differs from B8's calibration step by up to about 1.5e-3 AP per fold (B9 matched within 1e-9 on Benson's) | No refit in B10: restate B9's stored files (1/6 and 4/15 are stored exactly); test from T1's saved predictions | Agreed (Henry, 2026-10-26) |
| B10-D11 | Out-of-profile limit for the app's warning | 4 SD from the training mean: under 1% of test rows per feature on average; 3 SD warns on up to 7.7% of orders for one feature (out\_of\_profile\_shares.csv) | Agreed (Henry, 2026-10-26) |
| B10-D9 | In-scope classification orders not yet handed over: B cannot score them (it predicts at handover) | No score until handover, and the missed-dispatch rule (B-C10) flags the order once its shipping limit passes; A is not used for them (A is the fallback for out-of-scope orders only, B-G-06) | Agreed (Henry, 2026-10-26) |

### 7. After B10

Team review of the package (doc tab copy in `../doc_outbox/`). On approval: tag `e5-B-s10-accepted` on the branch. Then, each only when ordered: team sign-off and `e5-release-1`, migration (lead), reproduction check, app and dashboard build with the live URL, report and slides.

## B11 — final report and deck drafts, from B's evidence (blueprint)

Repo copy: `experiments/experiment_5/pipeline_b/spec/blueprints/b11_report_deck.md`.

| Field | Value |
| --- | --- |
| Stage | B11 deliverables: report and deck drafts (A's s10 10.7 adapted to B; G-79: B delivered, A baseline) |
| Nodes | common (one report, one deck, both tasks) |
| Status | AGREED 2026-10-26 (Henry: B11-D1 to D9; D6 changed to Claude Slides). Drafted by Henry's Claude |
| Inputs frozen | Every B run listed Current in `../../EVIDENCE.md` (B2 to B10, T1, doc support); B10 at tag e5-B-s10-accepted-r2 (round 2, 4/15) |

### 0. Scope and order (decisions of 2026-10-26)

Henry's decisions on the deliverables (B11-D1 to D4):

1. **Draft now, before migration and the reproduction check** (a deviation from s10-D3's order, because the slides lock on 4 Nov). Drafts live in `pipeline_b/deliverables/`. Before submission every number is re-checked against the reproduced outputs (s10 10.4), or against the same Current runs if the team submits without migration.
2. **Blueprint first**, as every B stage.
3. **B's own number register**, `pipeline_b/build_evidence_B.py`, separate from A's `build_evidence.py`.
4. **Report as a Claude Doc** for the team to review and comment (not the Milestone 2 Word route); **deck as a Claude Slides deck** (no team template): text and tables stay editable, charts are images.

Not in B11: migration, the reproduction check, the Streamlit app and its live URL (each only when ordered). Report and deck keep marked placeholders for the app (deployment section, screenshots) until then.

### 1. Goal and gate

Goal: a 15–20 page report and a 10-minute deck that follow the brief's Phase 3 section list, tell one story (B delivered, A as baseline), and carry no hand-typed number. Gate: every number and table in both resolves to `numbers_B.json` (built from Current runs only); the team reviews the report in the Claude Doc and the deck file; open placeholders are listed.

### 2. Number register (B11.1, `build_evidence_B.py`)

- `pipeline_b/evidence/registry_B.yaml` lists every number, table and figure the report and deck use (A's registry format: `id`, `kind` number/table/figure, `source` file, `select`, `used_in`), with B evidence IDs. A's baseline numbers come from B's T1 and B9 files, which already score A (A on A's rows, A on B's rows); A's own tree is not read for the register and never written.
- The builder refuses to run unless each source file belongs to a run listed Current in EVIDENCE.md (its `_manifest.json` run\_id and sha256 match), then writes `pipeline_b/evidence/build/numbers_B.json`, table CSVs and figure copies, each with its source file, run\_id and evidence ID.
- Report and deck text uses placeholders such as `{{B9.2.reg.mae_diff}}`; a filler replaces them from `numbers_B.json` with the registry's format. A placeholder that does not resolve fails the build.
- Test: every placeholder in the report and deck sources is in the registry; every registry item resolves.

### 3. Report (B11.2)

Source: `pipeline_b/deliverables/report/*.md`, one file per section, with placeholders. Filled output is published as a Claude Doc in Henry's account for the team (B11-D5); the doc is the review copy, the repo holds the source. Exported to PDF at the end (12 pt, captions, labelled tables; `TeamX_...` naming).

| § | Section (brief Phase 3) | Pages | Content and sources |
| --- | --- | --- | --- |
| — | Cover, executive summary | 1 | Problem, delivered model, headline test results with intervals (B9.1, B9.2), business answer |
| 1 | Problem definition and stakeholder | 1.5 | Two tasks, prediction moments (checkout; handover for classification), stakeholders and actions, 5:1 cost (s01; CR-054) |
| 2 | Dataset and preprocessing | 2 | Tables and joins, `customer_unique_id`, leakage audit (s02); B's population rules and history features (B2); why carrier dates are allowed as *past* events and at handover only (brief leakage warning) |
| 3 | Exploratory analysis highlights | 1.5 | Target shape, trends over time, late delivery vs detractors (s03); route lateness (B2 lateness summary) |
| 4 | Modelling approach | 3 | Pipeline A, then B = A + CR-054; features and 99% rule (B4; Report notes §6 citations); time-ordered folds and why not stratified (Report notes §2); model ladder dummy → linear/logistic → tree → forest, one-SE rule (B6–B8); calibration and threshold (B8, B-G-05); ensemble decision (§3, wording per B11-D7) |
| 5 | Results and evaluation | 4 | Train–validation–test table with intervals, A vs B on the same rows (B9.1, B9.2, B9.14); where B's gain comes from (Report notes §1); error analysis by state and route (B9.3, B9.13); residual buffers (B9.16); classification at 1/6 (unbiased) and 4/15 (post-test, B-G-07) (B10.3); interpretation: coefficients, odds ratios, permutation importance and its divergence from B4 (B9.5, R-15); drift (B9.4, B9.11) |
| 6 | Model deployment and application | 1.5 | Release package and serving rule (B10): parity, router, A fallback, input checks, out-of-profile warning; app URL and screenshots **placeholder** |
| 7 | Business recommendations and impact | 2 | Delivery promises with buffers, alert volumes and costs, missed-dispatch rule, route actions (B9.7, B9.13, B10.3, R-14); observation / hypothesis / unmeasured-mechanism labels |
| 8 | Limitations and next steps | 1 | Scope, prediction moments, fold-1 deviation, drift, post-test threshold, refit reproducibility (B10-D10), no causal claims |
| — | References; appendices | (excluded) | Full rank (R-01), metric glossary, fold boundaries, recipes, full tables, AI-use declaration |

Report requests R-01 to R-18 and DOC\_GAPS T-01 to T-10 are each mapped to a section in the registry (`used_in`); the build lists any request without a home.

### 4. Deck (B11.3)

- A Claude Slides deck (artifact type "Slides") in Henry's account, shared with the team like the report doc (B11-D6). Slide text comes from `pipeline_b/deliverables/deck/slides.md` (one block per slide, with placeholders), filled from `numbers_B.json`. One house style for the deck (palette, fonts, title, content, two-column, table and chart layouts). **Every title, bullet and table is editable deck text or table; only charts are images** (the stage PNGs, uploaded as assets). Speaker notes carry the talk track and the source of each number.
- About 12 slides for 10 minutes: title; problem and stakeholders; data and leakage control; A → B (what changed and why); model ladder and selection; results A vs B (both tasks); where B errs; threshold and alert volumes; business actions; deployment (app screenshots placeholder); limitations; summary.
- Downloaded as .pptx and PDF for Canvas and the ZIP (B11-D6).

### 5. Outputs

`pipeline_b/build_evidence_B.py`, `evidence/registry_B.yaml`, `evidence/build/` (numbers\_B.json, tables, figures, build manifest); `deliverables/report/*.md` and the filled report; `deliverables/deck/slides.md` and the Slides deck; `deliverables/placeholders.md` (open items: app URL, screenshots, reproduction re-check).

### 6. Checks

- Every number, table and figure in report and deck resolves to `numbers_B.json`; none is typed.
- Every register source is a Current run in EVIDENCE.md (run\_id and sha256).
- Superseded evidence (e.g. 4/15, B2 round 1) is never cited.
- Validation scores are labelled selection scores (G-10); test numbers come from T1 or B9/B10 post-test views, and 1/6 is called the unbiased result.
- The deck has no text or table inside a picture (every image asset is a chart PNG from the register).
- Report body 15–20 pages after export; deck about 12 slides.
- Brief compliance list (Phase 3 sections, leakage, imbalance, 2–3 families, baselines, CV, seeds) ticked with the section that satisfies each.

### 7. Decisions

| ID | Question | Recommendation | Status |
| --- | --- | --- | --- |
| B11-D1 | Draft before migration and reproduction | Yes, in `pipeline_b/deliverables/`; re-check before submission | Agreed (Henry, 2026-10-26) |
| B11-D2 | Blueprint first | This blueprint | Agreed (Henry, 2026-10-26) |
| B11-D3 | Number register | `build_evidence_B.py`, separate from A's | Agreed (Henry, 2026-10-26) |
| B11-D4 | Formats | Report as a Claude Doc for review; deck generated, editable text and tables, charts as images | Agreed (Henry, 2026-10-26) |
| B11-D5 | Whose account holds the report doc. A doc in Henry's account can be read and edited by Henry's Claude (comments included); Benson's Claude cannot reach it, as Henry's Claude cannot reach Benson's doc | Henry's account, shared with the team by link for browser review; the repo Markdown stays the source | Agreed (Henry, 2026-10-26) |
| B11-D6 | Deck format | Claude Slides deck in Henry's account; editable text and tables, charts as images; download .pptx and PDF | Agreed (Henry, 2026-10-26; replaces the python-pptx proposal) |
| B11-D7 | Ensemble wording. Report notes §3 says the course "rules out" a more complex family; the brief lists voting/stacking as an optional third family built from the chosen ones, and Benson says the professor forbids more complex families | Write "ensembles were optional; within the course's limit on model families the team kept linear and tree families, with the random forest as the bagged ensemble; stacking was not added", and cite the brief accurately | Agreed (Henry, 2026-10-26) |
| B11-D8 | Team name and numbers in file names (`TeamX_…`) | Team 11, from the Milestone 2 report name | Agreed (Henry, 2026-10-26) |
| B11-D9 | Report authorship: Claude drafts every section from the register, the team edits in the doc; AI use declared (brief policy) | As stated | Agreed (Henry, 2026-10-26) |

### 8. Timeline (slides lock 4 Nov 23:59, report 8 Nov 23:59)

| Date | Step |
| --- | --- |
| 27 Oct | Register and builder; report outline in the doc |
| 28–30 Oct | Report sections 1–8 drafted; deck v1 |
| 31 Oct – 2 Nov | Team review of doc and deck; app placeholders filled if migration and app are done |
| 3 Nov | Deck final check (numbers, compliance list); 4 Nov submit |
| 5–7 Nov | Report final edits, PDF export, re-check numbers; 8 Nov submit ZIP |
