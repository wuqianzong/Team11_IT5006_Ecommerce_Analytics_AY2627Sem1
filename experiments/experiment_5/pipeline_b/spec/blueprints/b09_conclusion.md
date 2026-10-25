# B9 Conclusion — B primary, A as baseline (blueprint)

| Field | Value |
| --- | --- |
| Stage | B9 conclusion (G-79 join plan; A's s09 blueprint `../../../spec/blueprints/s09_conclusion.md` adapted to B) |
| Nodes | regression, classification |
| Status | AGREED (experiment lead, 2026-10-24; B9-D1 to B9-D4 as recommended); conclusion CONFIRMED by Henry and the lead 2026-10-25 |
| Inputs frozen | T1 at tag e5-T1-tested (runs 20261024T044531Z, 20261024T044555Z); B8 at e5-B-frozen; B4, B5 accepted runs (EVIDENCE.md) |

## 0. Scope (experiment lead, 2026-10-24)
This stage finishes the implementation and writes a conclusion **for team review**. It does not
build the report, the deck, the dashboard or app, or the reproduction package. Those, and the
release work of A's s10 (B10), start only after the team confirms the conclusion. The T1 bundles
already exist; B10 will package B's bundle.

## 1. Goal and gate
Goal: describe what B's frozen models achieve on the test, where they fail, why they predict what
they predict and what the business can do with them, with A as the baseline. Nothing here feeds
back into a model, calibration or threshold choice (G-79: the test does not re-choose). Every
claim is labelled as an observation, a literature-supported hypothesis or an unmeasured mechanism.
Gate: the team reviews the conclusion tab and confirms (or asks for changes) before B10, the
report, the deck and the dashboard start.

## 2. Inputs (read only; no refit, no second test read)
- T1 `predictions_test.csv.gz` (every model × rows), `metrics_test.csv`, `fold_and_test_table.csv`, bundles.
- Test-row attributes for slices: A's s02 records for the T1 test order IDs (customer state,
  distance, basket size, seller count, purchase month, first-review label), and B's test-row
  features rebuilt with T1's `b_rows` (verified builder). Check: B's bundle re-predicts the rebuilt
  rows exactly as `predictions_test.csv.gz` (otherwise stop).
- B6–B8 fold scores (training and validation means), B4 `selection_ranking_B.csv`, B8 `missed_dispatch_rule.csv`.

## 3. Method
1. **Train–validation–test table (B9.1; B-C13, T-06).** Per task, for B's frozen model, A's
   frozen model (on A's rows and on B's rows) and the plain and dummy references: training mean,
   validation selection score (mean ± SE, labelled G-10), test score with a 95% bootstrap interval
   (1,000 resamples of test orders, seed 42). Classification adds the absolute number of test
   detractors and each interval's width (G-54).
2. **B versus A on the same rows (B9.2).** Paired bootstrap interval on the test difference
   (B minus A on B's test rows) for MAE and AP, plus RMSE, R², within_3d, ROC-AUC and Brier;
   B versus its dummy and plain references the same way.
3. **Error analysis (B9.3; G-40, T-05).**
   - Regression: absolute error of A and B by customer state, route (seller → customer state),
     distance band, basket size and purchase month; slices under 100 orders descriptive only.
   - Classification: precision and recall at 1/6 by customer state and route, judged only with
     more than 100 test detractors (others "too few to judge"); pooled and mean ± spread over the
     judged slices; secondary slices basket size and seller count.
   - Where B gains most and where it does not (gain by slice, same rule).
4. **Drift (B9.4; G-77).** Final-fit rows vs test rows: standardised mean differences of B's
   numeric features, category-share changes, target shift (lead time; prevalence). Includes B's
   history features and their source shares (own history vs fallbacks) on test vs development.
   Feeds point 2 of the T1 tab (why the regression test gain exceeds the CV gain): described, not tested.
5. **Interpretation (B9.5; T-04).** Coefficients (regression, log scale) and odds ratios
   (classification) of B's frozen models with their transforms; permutation importance of B's
   frozen model on B's test rows (description only); comparison with B4's selection ranking
   (Spearman and top-10 overlap; on divergence the run alerts the team, never changes the model).
6. **Label sensitivity (B9.6).** Classification test metrics re-scored with the first-review label.
7. **Business conclusions (B9.7; T-08).**
   - Regression: what B's MAE and within_3d mean for delivery promises, by customer state.
   - Classification: alerts/day at 1/6 (cap 25), the share that are detractors, detractors caught,
     illustrative cost vs no alerts, for B and A (T1.4); the missed-dispatch rule (B-C10) on the
     test period beside the classifier.
   - Each recommendation traced to a file and evidence ID.
8. **Limitations (B9.8; T-07).** Seven-state scope; different prediction moments (checkout for
   regression, handover for classification); fold-1 deviation (B-G-01); history from earlier test
   weeks (J-1 a); sigmoid deviation (B-G-05); test drift (G-77) and A's test detractor shortfall
   (G-75); illustrative cost; no causal claims.
9. **Conclusion (B9.9).** One page per task in `conclusion.md` and in the doc tab: the answer,
   the evidence, the limits, and the questions for the team (including whether to revisit the
   threshold after the test, which would be reported as a post-test change).

## 4. Decisions for the lead and team
| ID | Question | Recommendation | Status |
| --- | --- | --- | --- |
| B9-D1 | Slices and the 100-detractor rule | As A's s09 (G-40), plus route for B | Agreed |
| B9-D2 | Permutation importance data | B's test rows, description only (as A's s09-D3) | Agreed |
| B9-D3 | A's single-tree rules (A's 9.5) | Dropped: neither frozen model is a tree | Agreed |
| B9-D4 | A's EDA consistency check against s03 | Replaced by the check against B4's ranking (B-C11) | Agreed |

## 5. Outputs (per task, `pipeline_b/stages/b09/<task>/outputs/`)
`train_val_test.csv`, `paired_test_differences.csv`, `subgroups.csv` (judged / too-few flag,
aggregates), `drift.csv`, `coefficients.csv`, `permutation_importance.csv`,
`ranking_consistency.json`, `label_sensitivity.csv` (classification), `business_summary.csv`,
`conclusion.md`, figures with sidecar data. Evidence IDs B9.1 to B9.9.

## 6. Checks
- No refit and no threshold change: B's bundle re-predicts the T1 predictions exactly.
- Every test number equals the T1 value it restates (metrics_test.csv).
- Validation scores are labelled selection scores; only test numbers are called unbiased.
- Every recommendation names its file and evidence ID.

## 8. Round 2 (Henry's B9 review, 2026-10-25; lead: "set threshold at 4/15, the rest is okay")
Same rules: read only, no refit of the frozen models, no second test read. Per-fold refits of the
frozen recipes on development folds (to rebuild out-of-fold sigmoid probabilities) are allowed
and checked against B8/s08's calibration step.
- **B9.10 Operating threshold options** (classification; B-G-07): precision, recall, FP/TP,
  alerts/day and cost (5:1 and 1:1) against the threshold, on validation (B's sigmoid out-of-fold)
  and on T1's test predictions; the frozen 1/6 and the operating 4/15 marked, cap 6/day shown;
  confusion at both on the test; A at both for comparison.
- **B9.11 Drift by fold** (R-07): training vs validation rows per fold, A and B (SMD, category
  share change, target), plus final-fit vs test; heatmap features × periods.
- **B9.12 Payment type** (R-09; regression): purchase-to-approval delay and lead time by payment
  type, development and test rows (raw orders' approval time).
- **B9.13 Business summary by route** (R-10): A and B on B's test rows; A on all of A's test rows;
  classification at 1/6 and 4/15; 100-order / 100-detractor rule.
- **B9.14 Validation and test together** (R-11): folds 1-5, mean ± SE and test with interval for B,
  A on B's rows and A on A's rows; dot-and-interval chart.
- **B9.15 A outside B's scope** (R-12; B-G-06): A per fold and on the test, in vs out of scope.
- **B9.16 Residual distribution** (R-16; regression, added at confirmation 2026-10-25): actual minus predicted lead time, shares more than 3 and more than 6 days late, quantiles, histogram; B9.14 also carries each period's time window (R-17).

## 7. After B9
Team review in the doc (B9 tab and sub-tabs). On confirmation: B10 release (bundle packaging,
app), then the report, deck, dashboard and reproduction, and the DOC_GAPS.md pass.
