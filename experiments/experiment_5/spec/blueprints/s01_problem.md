# s01_problem — blueprint

| Field | Value |
| --- | --- |
| Stage | s01_problem (`../pipeline_design.md` → s01) |
| Nodes | common |
| Status | AGREED |
| Owner | TBD |
| Last agreed | 2026-10-18 (team review, doc tab "Model solution (s01, s06–s10)", section s01) |
| Discussion | Claude Doc "Milestone 3 pipeline stages", tab "Model solution (s01, s06–s10)", section s01 |

## 1. Goal and gate
Goal: fix everything that must be decided before any data is modelled, and write it to the
pre-registered layer of `spec/protocol.yaml`.
Gate: tasks, targets, metrics, cost, decision rule and budget fixed before any result
(`../stages.json`).

## 2. Inputs
- Project brief (Phase 2–3), teacher's Milestone 2 note (rubric), Milestone 1 TA feedback,
  Tutorials 1–8 (`../sources.md`).
- No data. s01 runs before s02 and reads no Olist file.

## 3. Method
1. **Tasks and prediction time (1.1).** Regression: delivery lead time in fractional days.
   Classification: will an eligible order (not cancelled or unavailable, and reviewed) receive a
   1–2 star review (`is_detractor`, positive class 1). The classification score is therefore
   the risk of a 1–2 star review if the customer reviews; the report states this scope limit.
   Both are predicted at checkout (`order_purchase_timestamp`).
2. **Stakeholders and action (1.2).**
   - Regression → logistics / fulfilment planning: an expected lead time per order at checkout,
     used to flag long-haul orders and set realistic delivery promises.
   - Classification → customer-experience team: a daily list of at-risk orders for proactive
     contact (status update, check with the seller).
   - Each states who sees what, when, and the cost of each error.
3. **Targets and populations (1.3).** As agreed in s02 (G-20): minimum-review label with a
   first-review sensitivity check; delivered orders (regression); not cancelled or
   unavailable, with a review (classification). Scope limits stated in the report.
4. **Metrics (1.4).**
   - Regression: MAE primary (in days, robust to the long tail), RMSE, R², share within ±3 days.
   - Classification: AP primary (suits a minority positive class; prevalence measured in s03,
     not assumed), ROC-AUC, Brier, and precision, recall, F1 and confusion matrix at the
     threshold. Accuracy is never reported alone.
   - Charts: precision–recall and ROC curves, out-of-fold in s06 (6.6) and on the test cohort in
     s09, saved with their curve data (design rule 8).
   - Citations (verified): Willmott & Matsuura 2005, *Climate Research* 30:79–82
     (MAE vs RMSE); Saito & Rehmsmeier 2015, *PLoS ONE* 10(3):e0118432 (PR vs ROC under
     imbalance); Brier 1950, *Monthly Weather Review* 78:1–3.
5. **Cost assumption (1.5).** Illustrative cost FN:FP = 5:1 (a missed detractor costs as much
   as five unnecessary contacts). Stated as an assumption, never as measured ROI.
   Citation (verified): Elkan 2001, "The Foundations of Cost-Sensitive Learning", IJCAI.
6. **Model families (1.6).** Two families plus references: dummy (median / prior); linear
   (LinearRegression, Ridge; LogisticRegression); tree (DecisionTree, RandomForest). No
   boosting, voting or stacking.
7. **Decision rule (1.7): one-standard-error rule** (G-33).
   - For every candidate: the mean and standard error (fold SD / √5) of the primary metric over
     the five s05 folds.
   - Find the best mean, then keep the simplest candidate whose mean is within one standard
     error of the best. A more complex variant is therefore kept only if it beats the simpler
     one by more than one standard error. Ties go to the simpler model.
   - The same rule chooses within the s06 ladder and within each s07 grid, and gives the
     recommendation among the s08 finalists, which the team confirms at the s08 gate (G-39).
   - Simplicity order (pre-registered in `protocol.yaml`): dummy < linear/logistic < single
     tree < forest. Within a family, these count as simpler: stronger regularisation (higher
     alpha, lower C), shallower trees and larger leaves.
   - Paired per-fold differences are reported alongside, as description only.
   - Fallback: if no complex variant passes, the best simple model goes forward. If no model
     beats the dummy, the dummy is the reported result ("no signal at checkout").
   - The rule is fixed before any result and never loosened afterwards. A team override at the
     s08 gate is a logged protocol deviation, reported beside the one-SE choice (G-44).
   - Literature: Breiman, Friedman, Olshen & Stone 1984 (CART); Hastie, Tibshirani & Friedman
     2009, *The Elements of Statistical Learning*, §7.10. Industry practice: glmnet
     `lambda.1se` (Friedman, Hastie & Tibshirani 2010, *J. Stat. Softw.* 33(1)); scikit-learn
     example "Balance model complexity and cross-validated score".
8. **Search budget (1.8).** Grids are fixed in s07 (one per family, listed there). The random
   forest uses 200 trees; seed 42 everywhere. No new grid points are added after results are
   seen.

## 4. Decisions
| ID | Question | Answer | Basis | Status |
| --- | --- | --- | --- | --- |
| s01-D1 | Classification task wording | Eligible order (not cancelled/unavailable, reviewed); score read as risk if reviewed | G-34; G-20 | Agreed |
| s01-D2 | Primary metrics | MAE (regression), AP (classification); PR and ROC charts | Teacher note §5; G-24 | Agreed |
| s01-D3 | Cost | FN:FP = 5:1, illustrative | Elkan 2001 | Agreed |
| s01-D4 | Families | Dummy, linear/logistic, tree/forest | Brief; Tutorial 8 | Agreed |
| s01-D5 | Decision rule | One-standard-error rule, simplest within 1 SE of best, with fallback | G-33 | Agreed |
| s01-D6 | Budget | Fixed grids, 200 trees, seed 42 | Brief | Agreed |

## 5. Outputs (`stages/s01_problem/common/outputs/`)
- `spec/protocol.yaml`, pre-registered layer: tasks, prediction time, label rule, metrics,
  cost, families, simplicity order, decision rule, grids, budget, seed, the 80/20 split rule.
- `task_contract.md`: prediction time, stakeholder actions, metric and model rationale with the
  verified citations above, scope limits.

## 6. Checks
- `protocol.yaml` pre-registered layer is committed before any s02 output exists (commit order).
- Every citation in `task_contract.md` is in the verified list above.

## 7. Milestone 2 reuse
None (wording and metric rationale are rewritten; no Milestone 2 result is used, G-29).

## 8. Report hooks
Introduction and problem definition: tasks, stakeholders and actions, metrics and cost, model
selection rule.

## 9. Open questions
None.
