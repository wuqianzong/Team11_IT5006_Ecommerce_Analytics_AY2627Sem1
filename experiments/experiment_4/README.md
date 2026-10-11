# Matched two-cycle pipeline

This is the active Milestone 2 evidence study. One chronological protocol supports two modelling cycles: nine-feature simple references, followed by controlled task-specific feature expansion, input/target transformations, regularization and forest comparisons. The fixed catalogue contains 15 regression and 11 classification recipes: 130 fold fits and 26 final reference fits. Earlier experiments remain historical exploration.

## Read the completed evidence

Use `artifacts/metrics/experiment-4/run-01/`:

- `protocol.json`, `freeze.json`, `fold_membership.csv`, `exclusions.csv`, `split_audit.csv`: candidate catalogue, environment, sources and cohorts.
- `fold_metrics.csv`, `summary.csv`, `paired_comparisons.csv`: training/validation comparisons and five paired differences. SD is sample SD across chronological windows, not an independent confidence interval.
- `development/` and `*_oof.csv`: every fold pipeline and validation prediction.
- `selection_freeze.json`, `decision_policy.json`, `threshold_curve.csv`: validation-only choices and frozen policy, saved before terminal scoring.
- `bundles/`, `final_training_metrics.csv`, `train_validation_terminal.csv`, `terminal_metrics.csv`, `terminal/`, `selected_subgroups.csv`, `figures/`: fitted references, selected results and terminal diagnostics.
- `verification.json`: independent numerical, membership, decision and checksum checks. `verification_attempt_01.json` records the initial verification parsing issue; the model fits were unchanged.

The regression choice is the 11-feature log-input/log-target forest with 50 trees, depth 14 and minimum leaf 50, without target clipping. Classification uses the 12-feature logged-input L2 LogisticRegression with C=0.01. Plain unpenalized counterparts are genuinely evaluated under the same protocol.

The classifier is selected for development AP, not terminal AP or outreach utility. Its OOF-selected threshold is 0.13740171395086628 under illustrative FP=1/FN=5 costs. Terminal loss is 9,902 versus 8,535 for no alerts. The frozen alert policy is **not recommended for operational deployment**. It remains saved as an evaluated policy; terminal results do not retune it.

## Reproduce and verify

Start with the [root reproduction guide](../../README.md#reproduce-experiment-4) for environment setup, verification of the committed evidence, and a runnable scoring demonstration. Use the versions recorded in `freeze.json` (original Python 3.10.19) and `requirements.txt`; install them with `python -m pip install -r experiments/experiment_4/requirements.txt` in a dedicated environment. From the repository root, choose a fresh output directory:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m experiments.experiment_4.run --output artifacts/generated/experiment4-reproduction-01
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m experiments.experiment_4.verify --run artifacts/generated/experiment4-reproduction-01
MPLCONFIGDIR=/tmp/it5006-mpl python -m experiments.experiment_4.summarize --run artifacts/generated/experiment4-reproduction-01
```

Never overwrite an accepted run. Retain failures. Read probability CSVs with pandas `float_precision='round_trip'` when reproducing exact threshold decisions: default float conversion may move a boundary probability by one floating-point step.

The report's raw cohort distribution summaries can also be reproduced without model fitting:

```bash
python -m experiments.experiment_4.cohort_summary --run artifacts/metrics/experiment-4/run-01 --output artifacts/generated/report-cohort-summary-01
```

This checks the accepted feature-input hash, selects rows using the saved training/terminal order identifiers, and writes raw numeric, state, basket, seller and target summaries to a fresh directory.

## Active zero-fit scoring

`src/models/configs/active_pipeline.json` identifies the selected bundles. `src.models.experiment4_score` validates checksums, required columns and order identifiers before scoring:

The following commands assume you have supplied a CSV containing unique `order_id` values and the required constructed predictor columns. For a complete example using the committed feature data, follow the [root scoring demonstration](../../README.md#4-demonstrate-scoring-with-the-accepted-selected-models).

```bash
python -m src.models.experiment4_score --task regression --input constructed_checkout_features.csv --output new_regression_scores.csv
python -m src.models.experiment4_score --task classification --input constructed_checkout_features.csv --output new_classification_scores.csv
```

These are local scoring artifacts, not a deployed or validated outreach service. The classification scoring output includes the frozen experimental decision rule; its negative terminal utility must accompany any interpretation.

## Interpretation

Both cycles share task-specific chronological folds, customer purging and training-label maturity. Preprocessing fits inside each fold. Comparisons retain failed refinements: feature expansion can hurt trees, and forests do not automatically beat simpler models. The report presents the pipeline in logical order. Read-only distribution or integrity checks are placed at their relevant stage without changing their populations or decisions.

Development data were reused adaptively, and the terminal cohort was previously inspected. These conditions prevent an untouched-test claim. Checkout features reconstruct database snapshots rather than certify event-time availability. Review/delivery eligibility is conditional on recorded outcomes. None of these limits is removed by rearranging the report.
