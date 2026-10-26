<!-- For the team doc: tab "B blueprints B2–B9 and joint test", new section after B9. Source: pipeline_b/spec/blueprints/b10_release.md (DRAFT, 2026-10-26). -->

## B10 — release of B's frozen models, with A as fallback (blueprint)

Repo copy: `experiments/experiment_5/pipeline_b/spec/blueprints/b10_release.md`.

| Field | Value |
| --- | --- |
| Stage | B10 release (G-79; A's s10 blueprint `../../../spec/blueprints/s10_release.md` adapted to B) |
| Nodes | regression, classification |
| Status | DRAFT (2026-10-26, Henry's Claude; scope B10.1–B10.7 approved by the experiment lead (Wu Qianzong) 2026-10-26; B10-D1 to D7 agreed, D8 and D9 open) |
| Inputs frozen | T1 at tag e5-T1-tested (runs 20261024T044531Z, 20261024T044555Z); B8 at e5-B-frozen; A at e5-A-frozen; B9 at e5-B-s09-accepted (runs 20261025T132406Z, 20261025T132538Z) |

### 0. Scope

B10 turns the frozen T1 bundles into a release package that an app can serve, and proves that the
package predicts exactly what T1 predicted. It covers A's 10.1 (parity), the serving rule (B-G-06)
and threshold (B-G-07), A's 10.5 input checks, the drift profile and the map of every app element to
its source. Everything stays in `pipeline_b/`.

Not in B10 (later, each only when ordered): the release tag `e5-release-1` and team sign-off (A's
10.2), migration into the working folders (10.3, experiment lead only, README §12), the reproduction
check (10.4), the Streamlit app build and live URL (10.5–10.6), the report and slides (10.7), the
walkthrough notebook (10.8).

### 1. Goal and gate

Goal: one release package per task (B's bundle, A's bundle as fallback, the serving rule, both
thresholds, input checks, drift profile, app sources), each file with its sha256. Gate: every bundle
re-predicts T1's saved test predictions within 1e-9 (B-G-08); every sha256 matches the frozen and
tagged files; no model, calibration or threshold changes; the team reviews the package and confirms
the expected alert volumes before any app is built.

### 2. Inputs (read only; no refit, no scoring of the test cohort)

- T1 `stages/t1_joint_test/<task>/outputs/`: `bundles/A/` and `bundles/B/` (`model.joblib`,
  `schema.json`, `training_profile.json`), `predictions_test.csv.gz`, `test_rows_B.csv`,
  `test_read.json`.
- Frozen recipes: B `stages/b08/<task>/outputs/frozen_recipe.json` (e5-B-frozen); A
  `../../stages/s08_selection/<task>/outputs/frozen_recipe.json` (e5-A-frozen).
- Test-row features rebuilt with T1's verified builder (`e5b.t1_joint_test.b_rows`), as B9 does; the
  labels are not read (B-G-08).
- B9 outputs: `threshold_options.csv` (B9.10), `a_fallback_by_scope.csv` (B9.15), `drift.csv` (B9.4),
  `residuals_summary.csv` (B9.16), `business_by_route.csv` (B9.13), `subgroups.csv` (B9.3).
- A's s02 `../../stages/s02_data/common/outputs/data_dictionary.csv` (types, ranges, allowed values;
  G-58).
- For R-14 (B10-D7): B2 `records_B.csv.gz` (development rows, observed outcomes only).

### 3. Method

1. **Reload parity (B10.1; A's 10.1; B-G-08).** Load each of the four bundles from disk (A and B, both
   tasks) and re-predict T1's test rows: A on A's test rows, A on B's test rows, B on B's test rows,
   features rebuilt with `b_rows`. Each prediction equals the saved value in
   `predictions_test.csv.gz` within 1e-9, row by row; any mismatch stops the stage. No label is read,
   no metric is computed. This is also the acceptance test of the Python 3.13.7 environment.
2. **Release manifest (B10.2).** Per bundle: sha256 of `model.joblib`, `schema.json`,
   `training_profile.json`; the frozen recipe's sha256 against `schema.json` `frozen_sha256` and against
   the file at its tag; feature lists, model id, calibration, training rows, training-ID digest; the
   package versions in `schema.json` against the running environment (any difference is listed; a
   difference that changes a prediction already fails B10.1).
3. **Serving configuration (B10.3; B-G-06, B-G-07, B10-D2).**
   - Scope rule, per order: customer state and primary seller state both in SP, MG, RJ, PR, RS, BA, SC,
     and `distance_km_max` present → B; otherwise → A. Regression predicts at checkout for both.
     Classification: B at carrier handover, A at checkout (B10-D9 for in-scope orders before handover).
   - Thresholds (classification): B operating 4/15 (B-G-07; see B10-D8), B frozen 1/6 kept beside it;
     A fallback at A's frozen 1/6 (B10-D2).
   - For each threshold, the expected volumes, restated from existing files, never recomputed on test
     labels: B at 1/6 and at 4/15 from B9 `threshold_options.csv` (alerts/day, precision, recall, FP/TP,
     cost 5:1 and 1:1, on validation and test); A out of scope at 1/6: precision and recall from B9
     `a_fallback_by_scope.csv`, and alerts/day counted from A's out-of-fold sigmoid probabilities
     (validation, rebuilt as B9.10) and from T1's saved test predictions (A's test rows outside B's
     scope; a count of predictions above 1/6, no labels). Plus the combined volume: B in scope at 4/15
     plus A out of scope at 1/6. **The team confirms these volumes at the B10 review (B10-D2).**
4. **Router (B10.4).** `e5b/serving.py`: `predict(order) -> {prediction, alert, threshold_name, model,
   scope_reason}`. It validates the input (B10.5), applies the scope rule, calls the matching bundle and
   applies the configured threshold. It never fits. Tests: every T1 test row routed through it gives
   T1's saved prediction (same tolerance), and each scope reason is exercised.
5. **Input checks (B10.5; A's 10.5).** Per bundle schema: column present, type, range or allowed
   values (from `data_dictionary.csv` and the training profile), unknown state or category, no items,
   missing instalments, impossible distance; clear error messages. Written as `input_validation.json`
   with one test case per rule, run through the router.
6. **Drift profile (B10.6).** Per bundle: the training profile (mean and SD per numeric feature,
   category shares) and the out-of-profile rule for the app (a numeric value beyond a set number of
   SDs, a category unseen in training), with B9.4's drift table as the reference for the test period.
   The number of SDs is proposed in the review tab, not chosen here.
7. **App sources (B10.7).** `app_sources.json`: every number and chart the model tabs will show
   (A's s10 panel list, adapted to B: headline, fit, policy at 1/6 and 4/15, where it errs, why, score,
   data health), mapped to its output file and evidence ID; the app computes no statistic. Plus R-14
   (B10-D7): `top_routes_categories.csv`, observed outcomes by time window on development rows (top 5
   routes and categories, minimum volume per window), with the coefficient as a second column; data
   only, charts with the app.

### 4. Outputs (per task, `pipeline_b/stages/b10/<task>/outputs/`)

`parity.json`, `release_manifest.json`, `serving_config.json`, `input_validation.json`,
`drift_profile.json`, `app_sources.json`, `top_routes_categories.csv` (R-14), checks and manifest.
Code: `e5b/b10.py`, `e5b/serving.py`; `b10` added to `STAGES` in `e5b/env.py` and `BUILT` in `b_run.py`;
tests in `pipeline_b/tests/` (router, parity, evidence register). Evidence IDs B10.1 to B10.7.

### 5. Checks

- Parity: all four bundles re-predict T1 within 1e-9, row counts equal T1's; no label column read.
- sha256 of every bundle file and frozen recipe matches T1, B8 and the tagged files.
- `schema.json` thresholds unchanged (1/6); 4/15 lives only in `serving_config.json`.
- Router reproduces T1's predictions on every test row; every scope reason covered by a test.
- Every number in `serving_config.json` equals the B9 or T1 value it restates.
- Every app element in `app_sources.json` names an existing file and evidence ID.
- A's tree untouched: A's code matches e5-A-frozen.
- Clean rerun on the committed code (`dirty: false`), byte-identical outputs.

### 6. Decisions

| ID | Question | Recommendation | Status |
| --- | --- | --- | --- |
| B10-D1 | Re-predicting T1's test rows for parity vs "never read the test cohort again" | Allowed for parity only: no labels, no scoring | Agreed (B-G-08; experiment lead 2026-10-26) |
| B10-D2 | Threshold for A's alerts on out-of-scope orders | A's own frozen 1/6 (B-G-07 is for B only); `serving_config.json` shows the expected out-of-scope alerts/day at 1/6 and the combined volume | Agreed (lead 2026-10-26); volumes to be confirmed by the team at the B10 review |
| B10-D3 | What the app can score | Held-out historical orders with features rebuilt by T1's builder; no free-form input | Agreed (lead 2026-10-26) |
| B10-D4 | Handover facts for classification | Stored orders only (follows D3) | Agreed (lead 2026-10-26) |
| B10-D5 | Where the app code lives | Inside `pipeline_b/` until the lead orders migration; live URL after migration | Agreed (lead 2026-10-26) |
| B10-D6 | Tags | `e5-B-s10-accepted` on the branch after approval; `e5-release-1` waits for migration | Agreed (lead 2026-10-26) |
| B10-D7 | R-14 top routes and categories | Data output only (observed outcomes, minimum volume, coefficient as second column); charts with the app | Agreed (lead 2026-10-26) |
| B10-D8 | Operating threshold value: Henry's 2026-10-26 remark says "5/14"; B-G-07, `human_decisions_B.yaml` b09 and B9 `threshold_options.csv` say 4/15 | Keep 4/15 as recorded. If the team means 5/14, that is a new post-test change (a new B-G entry and a B9.10 rerow from saved predictions), not a correction | Open (Henry, Benson) |
| B10-D9 | In-scope classification orders not yet handed over: B cannot score them (it predicts at handover) | No score until handover, and the missed-dispatch rule (B-C10) flags the order once its shipping limit passes; A is not used for them (A is the fallback for out-of-scope orders only, B-G-06) | Open (Henry, Benson) |

### 7. After B10

Team review of the package (doc tab copy in `../doc_outbox/`). On approval: tag `e5-B-s10-accepted`
on the branch. Then, each only when ordered: team sign-off and `e5-release-1`, migration (lead),
reproduction check, app and dashboard build with the live URL, report and slides.
