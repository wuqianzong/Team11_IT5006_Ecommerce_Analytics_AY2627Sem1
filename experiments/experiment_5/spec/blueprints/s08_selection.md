# s08_selection — blueprint

| Field | Value |
| --- | --- |
| Stage | s08_selection (`../pipeline_design.md` → s08) |
| Nodes | regression, classification |
| Status | AGREED |
| Owner | TBD |
| Last agreed | 2026-10-18 (team review, doc tab "Model solution (s01, s06–s10)", section s08) |
| Discussion | Claude Doc "Milestone 3 pipeline stages", tab "Model solution (s01, s06–s10)", section s08 |

## 1. Goal and gate
Goal: choose the model, calibration and threshold on the folds with two human gates, freeze
them, fit once, and score each task's test cohort exactly once.
Gate: recipe and threshold frozen before the test cohort is read; test scored once.

## 2. Inputs
- s06 plain models and s07 family winners (out-of-fold predictions, `grid_results.csv`).
- s02 records, s05 folds and `test_manifest.csv`.
- `spec/protocol.yaml` (decision rule, cost 5:1, metric list, seed 42).
- `spec/human_decisions.yaml`, section `s08` (team decisions, G-39).

## 3. Method
1. **Finalists (8.1).** Each family's best from s07, plus the dummy, the plain linear/logistic and
   the single-tree references from s06. All are compared on the same rows and folds: fold mean
   and standard error, with paired per-fold differences shown as description only.
2. **Choose the model (8.2): human gate.**
   - The s01 one-standard-error rule (G-33) on the primary metric (MAE / AP) gives the
     recommendation: the simplest finalist within one SE of the best mean.
   - The run stops and writes `selection_review_pack.md`. It holds, for each finalist, the fold
     mean ± SE on all s01 metrics, the train–validation gap and learning curves. It flags any
     chosen setting that sits at a grid edge.
   - The team confirms or overrides the recommendation in `human_decisions.yaml` (s08.model),
     with its rationale.
   - A grid-edge choice is resolved, never silently:
     - either widen that grid, which is a change request; s07 then reruns and keeps all
       configurations;
     - or revisit s03–s04.
   - Validation scores are reported as selection scores, not generalisation estimates (G-10).
3. **Calibration, classification (8.3).** Reliability curve and Brier score on the chosen model's
   out-of-fold probabilities. Raw probabilities by default. If they are poorly calibrated, a
   sigmoid variant (`CalibratedClassifierCV`, time-ordered inner splits inside each training
   fold) is scored as a full candidate. It is kept only if Brier improves without losing AP
   (G-16).
4. **Threshold, classification (8.4): hard stop.**
   - Candidates, from the out-of-fold probabilities of the chosen recipe: no alerts, 0.50, the
     theoretical cost cutoff 1/6 = C_FP/(C_FP+C_FN) (Elkan 2001), and the empirical minimum of
     5·FN + FP. Ties go to the higher threshold, which gives fewer alerts.
   - The run stops and writes `threshold_table.csv` and the pack. For each threshold it shows:
     - alerts per day and the alert rate (TP+FP)/N;
     - the error rate (FN+FP)/N;
     - precision, recall, F1 and cost;
     - the marginal trade-off, i.e. extra false alarms per extra detractor caught between
       neighbouring thresholds. Under the 5:1 cost an alert pays off only while this is ≤ 5.
   - The team picks the threshold in `human_decisions.yaml` (s08.threshold), with an optional
     daily alert cap for CX capacity, and the reason goes into the report.
5. **Freeze (8.5).** Write `frozen_recipe.json` with its hash, before the test cohort is read. It
   records features, transforms, recipe, estimator and settings, calibration and threshold.
6. **Final fit (8.6).** Fit the frozen recipe on all development orders whose labels were
   observable before the test cutoff.
7. **Test once (8.7).** Score each task's test cohort once with the G-24 metric list. The dummy
   and plain linear/logistic references are refitted the same way for comparison.
8. **Bundle (8.8).** `joblib` pipeline, threshold, feature schema, package versions,
   training-ID digest, `training_profile.json` (numeric distributions, category shares) for
   drift checks, checksums.

## 4. Decisions
| ID | Question | Answer | Basis | Status |
| --- | --- | --- | --- | --- |
| s08-D1 | Model choice | One-SE rule recommends; team confirms at a gate | G-33, G-39 | Agreed |
| s08-D2 | Grid-edge winner | Team widens grid (CR) or revisits s03–s04 | G-39 | Agreed |
| s08-D3 | Calibration | Raw default; sigmoid candidate if reliability fails | G-16 | Agreed |
| s08-D4 | Threshold | Hard stop; team chooses from the trade-off table; optional alert cap | G-39; Elkan 2001 | Agreed |
| s08-D5 | Test | Once, after freeze, with references | G-06, G-24 | Agreed |

## 5. Outputs (per task, under `stages/s08_selection/<task>/outputs/`)
- `selection_review_pack.md`, `selected_spec.json`, `threshold_table.csv`, `frozen_recipe.json`.
- Model bundle with `training_profile.json`; test `metrics_long.csv` and `predictions.csv.gz`.
- `decision.json` (recommendation, team decision, rationale), `candidates.csv`, `curves/`
  (design rule 8).

## 6. Checks
- s08 stops if `human_decisions.yaml` s08 entries for its task are missing.
- `frozen_recipe.json` hash recorded before any test row is loaded (population guard).
- Test scored exactly once per release; any later change is a reopened selection (README §9.3).

## 7. Milestone 2 reuse
Threshold-table and bundle code patterns from `src/models/` with provenance; no Milestone 2
threshold or score is used (G-29).

## 8. Report hooks
Selection section: finalist table, selection pack summary and team decision, calibration
curve, threshold trade-off table and chosen threshold.

## 9. Open questions
None.
