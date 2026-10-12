# Milestone 2 reproduction notes

These notes clarify the submitted report's evidence and reproduction path. They
were added after submission on 12 October 2026. The submitted Word/PDF report and
all originally fitted model weights, policies and published metrics are unchanged.
The report's frozen evidence was already committed at `e61dcf1`.

## Verification versus retraining

The report's bare terminal command now performs no-fit verification and writes to
an unused `artifacts/reproduction/` directory. The verifier checks the original
terminal evaluation's bundle hashes before deserializing models, verifies dataset
lineage, and refuses to overwrite source data, submitted documents, canonical
metrics or an earlier verification run. All nine original reference/selected
bundles are now included in Git, rather than only the selected pair. Both tasks'
training IDs, the classification selected predictions and chronological OOF
probabilities are also included.

The original training environment recorded Python 3.10.19 and numpy 2.2.6,
pandas 2.3.3, scipy 1.15.3, scikit-learn 1.7.2 and joblib 1.5.2. Use
`requirements-milestone2.txt`. Verification was additionally tested with Python
3.13.5 and those same numerical versions. The generic dashboard requirements have
been aligned on the numerical pins. The verification receipt records versions,
source/evidence hashes and numeric comparisons.

No-fit verification is reproduction of an already inspected cohort, not a new
independent test, a new optimization or proof that leakage is impossible.
Optional rebuilding uses the same recorded architecture in a separate directory;
its training recipe is described in README and is not run by the notebook.

## Report evidence map

| Report location | Evidence | Meaning |
| --- | --- | --- |
| Section 4.2 / Table E.2 Cycle 1 | `artifacts/metrics/experiment-3/feature_importance/feature_dimension_score_comparison.csv` | Customer-grouped CV on the nine-feature core; separate from earlier v3 chronological results |
| Table C.2 / Figure C.1 | `artifacts/metrics/experiment-3/transforms_and_tuning/phase4b_tuning_results.csv` and `phase4_default_vs_tuned_comparison.csv` | Expanded-feature grouped screening/tuning; changes include transformations as well as tuning |
| Table C.1 | `artifacts/metrics/refinement-selected-v4/development_fold_metrics.csv` | Five expanding windows for the selected models only |
| Figures D.1/D.2 | `artifacts/metrics/experiment-3/feature_importance/regression_11_feature_importance.csv` and `classification_12_feature_importance.csv` | Tree-regressor and logistic-classifier permutation diagnostics, not final-forest attribution |
| Tables E.1/E.2/E.4/E.5/E.6/F.5 | `artifacts/metrics/refinement-selected-v4/terminal/` | Frozen terminal metrics, subgroup rows and fold-resubstitution/validation summaries |
| Table E.3 / Figure E.6 | `classification_policy_comparison.json`, `classification_selected_predictions.csv` | Fixed threshold 0.17, with no terminal retuning |
| Section 6.3 | `frozen_decision_policy.json`, `classification_development_oof.csv` | Recorded empirical chronological OOF threshold ~0.1822; frozen policy 0.17 |
| Table A.1 / Table F.1 | `artifacts/metrics/report-evidence-exp3/` and `experiments/experiment_3/verify_report_evidence.py` | Development target moments and actual final regression training/terminal cohort statistics |
| Figure E.5A | `artifacts/metrics/refinement-core-v2-terminal/regression_diagnostics_cycle1.png` | Earlier 11-feature diagnostic, not a matched nine-feature Cycle 1 temporal baseline |

Paths in the terminal directory are relative to
`artifacts/metrics/refinement-selected-v4/`. Figure files reproduce diagnostic
content; pixel identity is not asserted across operating systems/fonts. The new
classification chart compares no alerts, default 0.50 and frozen 0.17. It neither
labels 0.17 globally optimal nor plots the minimum loss at an unrelated threshold.

## Cohort corrections supported by data

The no-fit verifier emits `table_f3_basket_counts.csv` and
`table_f4_target_statistics.csv`. They are also archived with the reproduction
receipt. These are corrections in the repository, not amendments to the submission.

- Table F.3: among 59,466 final regression training orders, one-item count is
  **53,424**, two–three-item count **5,448**, and four-plus count **594**. The
  submitted table has 53,426 / 5,446 / 594. Its terminal counts are correct.
- Table F.4: final classifier training has **59,740 orders**, **8,957 positives**,
  prevalence **14.9933%**. The submitted 11.0–13.4% range does not describe this
  cohort. Terminal prevalence is 1,707 / 15,769 = **10.8250%**.
- Training cohort IDs are checked against the SHA-256 digests in each frozen
  model's metadata. Table F.1 describes regression cohorts; its denominator must
  not be silently reused for classifier training.

## Interpretation limits and evidence not supplied

- There is no matched chronological baseline-family comparison in Table C.1.
  Grouped-CV gains are not matched temporal gains. Publishing existing evidence
  does not fill an unperformed experiment, and no new baseline experiment was
  run in this repository update.
- Forest-reference and selected-classifier AP are identical (0.182328...). The
  improvement from threshold 0.50 to 0.17 concerns decisions and illustrative
  FN/FP loss, not ranking AP.
- Figure B.2's CSV shows improvement from nine to expanded features, not a
  universal optimum at 11/12. For regression, the original 27-feature models have
  lower MAE than the expanded counterparts in that screening comparison. Its
  classification axis clips scores below 0.25.
- Figure E.7 is a lead-time-versus-distance scatter with a 60-day line; it does
  not display Cook's distance. The 60-day cap is a training-target treatment.
- Saved terminal regression residual mean is -1.1441 days; the residual plot
  does not establish zero bias or homoscedasticity. Lower terminal MAE and Brier
  loss do not identify operational causes or prove absence of overfitting.
- The 70% large-error/distance claim, precise hub locations and buffer choices
  do not have a documented quantitative decision analysis in the frozen evidence.
  They should be treated as hypotheses for investigation, not established effects.

## Literature provenance clarification

The report's domain-specific bibliography entries do not match the papers listed
in the submitted Phase 1 bibliography. Verified publisher records for the Phase 1
papers are:

- Cui, Lu, Sun and Golden, *Sooner or Later? Promising Delivery Speed in Online
  Retail*, Manufacturing & Service Operations Management 26(1), 233–251 (2024
  issue; published online 2023): https://doi.org/10.1287/msom.2021.0174
- Deshpande and Pendem, *Logistics Performance, Ratings, and Its Impact on
  Customer Purchasing Behavior and Sales in E-Commerce Platforms*, Manufacturing
  & Service Operations Management 25(3), 827–845 (2023 issue; online 2022):
  https://doi.org/10.1287/msom.2021.1045

These papers motivate delivery-promise and delivery/ratings problems. A feature
such as freight-to-price ratio or interstate share is a team-designed proxy; this
repository update does not claim the papers specifically validated that formula
or a causal state-border tax mechanism. The report's Leite entry was not verified
as written. No missing citation or experiment has been invented.
