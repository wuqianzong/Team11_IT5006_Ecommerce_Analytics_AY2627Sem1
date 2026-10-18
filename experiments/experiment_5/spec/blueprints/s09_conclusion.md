# s09_conclusion — blueprint

| Field | Value |
| --- | --- |
| Stage | s09_conclusion (`../pipeline_design.md` → s09) |
| Nodes | regression, classification |
| Status | AGREED |
| Owner | TBD |
| Last agreed | 2026-10-18 (team review, doc tab "Model solution (s01, s06–s10)", section s09) |
| Discussion | Claude Doc "Milestone 3 pipeline stages", tab "Model solution (s01, s06–s10)", section s09 |

## 1. Goal and gate
Goal: describe the frozen model's results for the business. Nothing here feeds back into a
choice. Every claim is labelled as an observation, a literature-supported hypothesis or an
unmeasured mechanism.
Gate: every conclusion follows from the test results and their limits.

## 2. Inputs
- s08 outputs (test metrics and predictions, bundle, `threshold_table.csv`, team decisions).
- s06–s08 fold scores; s03 importance ranking and EDA tables.

## 3. Method
1. **Train–validation–test table (9.1).** One table per task, for the winner and for the dummy
   and plain linear/logistic references:
   - training scores (fold mean);
   - validation selection scores (fold mean ± SD);
   - test scores with 95% bootstrap intervals (1,000 resamples of test orders, seed 42).
2. **Gain over baselines (9.2).** Winner vs the dummy and vs the plain model on test, with an
   interval on the difference (paired bootstrap).
3. **Error analysis (9.3; G-40).**
   - Regression: errors by customer state, distance band, basket size and purchase month.
     Slices under 100 orders are descriptive only.
   - Classification: precision and recall by customer state.
     - A state is judged only if its test cohort holds more than 100 detractors; the others are
       listed as "too few detractors to judge".
     - Aggregate over the judged states: pooled precision and recall, plus the mean and spread
       of the per-state values.
     - Secondary slices, under the same 100-detractor rule: basket size (items in the order)
       and seller count (distinct sellers in the order).
4. **Drift (9.4).** Training vs test: standardised mean differences of numeric features,
   category-share changes and target prevalence. Flags the features that moved most.
5. **Interpretation (9.5; G-40).**
   - Permutation importance of the frozen model on the test cohort (description, no decisions).
   - Coefficients and odds ratios of the plain linear and logistic models.
   - Top rules of the single tree (`export_text`).
   - EDA consistency check: the model's importance ranking (numeric and categorical
     separately) is compared with the s03 ranking, using Spearman rank correlation and top-10
     overlap. On divergence (correlation < 0.5 or fewer than 5 of the top 10 shared) the run
     alerts the team with a recommended action. It never changes the frozen pipeline; a fix
     would be a new release.
6. **Label sensitivity (9.6).** Classification test metrics re-scored with the first-review
   label.
7. **Business conclusions (9.7).** Only actions the evidence supports, each claim labelled.
   - Regression: what MAE means for delivery promises. Reliable promises matter more than fast
     ones: show where predicted lead time exceeds the promised date, by customer state, linked
     to the s03 late-vs-promised and detractor trends.
   - Classification: alerts per day at the threshold, the share that are true detractors,
     detractors caught, and the illustrative cost vs sending no alerts. Proactive contact is a
     service-recovery action, and a caught detractor is a retention opportunity.
   - Literature (venues confirmed; read in full before the report cites them): Griffis et al.
     2012, *Journal of Business Logistics*; Amorim, Eng-Larsson & Rooderkerk 2025, *Journal of
     Retailing*.
8. **Limitations (9.8).** Checkout-only information; fulfilled and reviewed populations;
   optimistic CV from the EDA-based selection; illustrative cost; no causal claims. The test
   cohort is this experiment's own held-out test (G-38).

## 4. Decisions
| ID | Question | Answer | Basis | Status |
| --- | --- | --- | --- | --- |
| s09-D1 | Slices | Customer state; judged only with > 100 detractors; pooled aggregate | G-40 | Agreed |
| s09-D2 | Importance check | EDA vs model ranking; alert only, no silent change | G-40 | Agreed |
| s09-D3 | Permutation importance data | Test cohort, description only | Open item (team ticked) | Agreed |
| s09-D4 | Test cohort wording | New held-out test of this experiment | G-38 | Agreed |

## 5. Outputs (per task, under `stages/s09_conclusion/<task>/outputs/`)
- Master metric table, `subgroups.csv` (with the judged / too-few flag and the aggregates),
  drift table, importance and interpretation tables, `eda_consistency.json`, `conclusion.md`.
- Figures with sidecar data and `curves/` (design rule 8).

## 6. Checks
- Validation scores are labelled as selection scores.
- Importance describes the selected model.
- Every recommendation is traced to evidence.

## 7. Milestone 2 reuse
Bootstrap and permutation-importance helpers from `src/reporting/`, copied with provenance; no
Milestone 2 result is used.

## 8. Report hooks
Results, error analysis, interpretation, business conclusions and limitations sections.

## 9. Open questions
None.
