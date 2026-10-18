# s07_tuning — blueprint

| Field | Value |
| --- | --- |
| Stage | s07_tuning (`../pipeline_design.md` → s07) |
| Nodes | regression, classification |
| Status | AGREED |
| Owner | TBD |
| Last agreed | 2026-10-18 (team review, doc tab "Model solution (s01, s06–s10)", section s07) |
| Discussion | Claude Doc "Milestone 3 pipeline stages", tab "Model solution (s01, s06–s10)", section s07 |

## 1. Goal and gate
Goal: regularise and tune each family with bounded grids on the same five folds, each candidate
a whole pipeline that carries the s04 feature set and log transforms.
Principle (teacher note §4): a tuned configuration is kept only if it beats its family's plain
s06 model (plain linear/logistic, single tree) under the s01 decision rule (G-33). Otherwise the
plain model stays. Both families are still tuned and reported.

## 2. Inputs
- s02 records (development rows), s04 selected set and recipes, s05 folds, s06 plain models.
- `spec/protocol.yaml`: the grids below (pre-registered), decision rule, seed 42.

## 3. Method
1. **Grids (fixed before any tuning result; G-37).**

   | # | Family | Grid |
   | --- | --- | --- |
   | 7.1 | Linear (regression) | `Ridge(alpha)`: 0.01, 0.1, 0.5, 1, 5, 10, 20, 50, 100 |
   | 7.2 | Logistic (classification) | `LogisticRegression(C)` with L2: 0.01, 0.1, 0.5, 1, 5, 10, 20, 50, 100; `class_weight`: None, balanced |
   | 7.3 | Decision tree | max_depth: 8, 10, 12, 14, 16, 18; min_samples_leaf: 20, 50, 100, 200; classifier also `class_weight`: None, balanced |
   | 7.4 | Random forest | Same grid as the tree; 200 trees; max_features='sqrt' |

2. **Search (7.5).** `GridSearchCV` over the full Pipeline with `cv` = the s05 fold iterator, and
   these settings:
   - scoring = the primary metric (neg MAE, average precision);
   - `refit=False`, `return_train_score=True`, seed 42.
   Best per family = the simplest configuration within one standard error of the best mean (s01
   1.7). Simpler means higher alpha, lower C, shallower depth, then larger leaf. That
   configuration is then kept only if it also passes the rule against the family's plain s06
   model.
3. **Overfitting check (7.6).** Report the train–validation gap for every configuration. Flag the
   chosen configuration if the gap is large while a simpler one is within the decision rule.

## 4. Decisions
| ID | Question | Answer | Basis | Status |
| --- | --- | --- | --- | --- |
| s07-D1 | Grids | As 7.1–7.4 | G-37; Tutorials 5, 7–8 | Agreed |
| s07-D2 | Best per family | One-SE rule, then must beat the plain s06 model | G-33; teacher note §4 | Agreed |
| s07-D3 | Class weight | Grid option for classifiers | G-05 | Agreed |
| s07-D4 | Forest size | 200 trees | Breiman 2001, *Machine Learning* 45:5–32 (verified) | Agreed |

## 5. Outputs (per task, under `stages/s07_tuning/<task>/outputs/`)
- `grid_results.csv`: every configuration with its parameters, per-fold train and validation
  scores, mean, SD, rank, fit time and convergence.
- Out-of-fold predictions of each family's best, with pooled out-of-fold scores kept separate
  from mean-fold scores.
- `decision.json`, `candidates.csv`, `figures/` and `curves/` (validation curves) (design rule 8).

## 6. Checks
- Grids in `protocol.yaml` match this blueprint and were committed before any s07 output.
- Same folds as s06; whole pipelines refitted per fold; no test row read.
- Compute note: up to 48 forest settings × 5 folds per task.

## 7. Milestone 2 reuse
Search loop patterns from `src/models/` (GridSearchCV over a Pipeline), copied with provenance.
No Milestone 2 grid result is used.

## 8. Report hooks
Tuning section: grid tables, validation curves, chosen configuration per family with its
train–validation gap.

## 9. Open questions
None.
