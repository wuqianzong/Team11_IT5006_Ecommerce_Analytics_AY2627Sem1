## 6 Modelling and the A-to-B decision

Models are compared from the simplest upwards, on the same time-ordered folds, under rules fixed before any test order was read. We first built a complete baseline (Pipeline A), then one focused improvement (Pipeline B) that changes only what the baseline's evidence pointed to; both were frozen and scored once on the test together.

### 6.1 Validation design

Orders are dated and customers return, so a random or stratified split would train on orders placed after the ones it predicts, and could put one customer on both sides (Kapoor and Narayanan, 2023). We therefore use five chronological, expanding folds before the test period: each fold trains on all orders up to a date and validates on the following weeks. Customers seen in a validation window are removed from its training rows, and a training order counts only if its label (delivery or review) was known before the validation window starts.

*Figure: Time-ordered folds and the test period (F.reg.partition).*

{{table:B5.reg.folds}}

Each fold must have at least {{B5.min_train_rows}} training orders and, for the alert, 100 detractors in each part; the minimums were set before the folds were built. Fold 1 of the improved pipeline falls short on training orders ({{B5.reg.fold1_train_rows}} for lead time, {{B5.clf.fold1_train_rows}} for the alert), because the seven-state scope and the warm-up remove early orders. We kept it, as a recorded deviation, so the two pipelines are compared on identical periods; every detractor minimum is met. Instead of stratifying, each fold's detractor share is reported, and it moves with the business over time (appendix A).

### 6.2 Model ladder

We use two model families, linear and tree-based, each started from its simplest form (James et al., 2023): a dummy that predicts the median lead time or the detractor share; plain linear regression or unpenalised logistic regression; a single decision tree; and a random forest of 200 trees (Breiman, 2001). Tree ensembles are the natural non-linear comparison for tabular data of this kind (Grinsztajn et al., 2022). Plain least squares and unpenalised logistic regression need a full-rank design matrix, which section 5.3 shows holds in every fold. Stacking (Wolpert, 1992) and gradient boosting (Chen and Guestrin, 2016) were considered but not added: the project limits the number of model families, and the forest itself did not clear the selection rule.

Each step up the ladder must beat the step below it on the same folds. The table gives the mean gain over the five folds, its paired standard error and the number of folds in which the more complex model wins (MAE in days, a positive gain means lower error; AP for the alert).

*Figure: Model ladder on the five folds, lead time (F.reg.family_ladder) and detractor alert (F.clf.family_ladder).*

Lead time:

{{table:B6.reg.ladder}}

Detractor alert:

{{table:B6.clf.ladder}}

The linear and logistic models beat the dummy in every fold. The single tree is worse than the linear model in both tasks. The forest is slightly better on average, more consistently so for the alert.

### 6.3 Tuning

Each family was then tuned on the same folds, with grids fixed before any tuning result was seen: Ridge alpha and logistic C from 0.01 to 100; tree depth 4 to 18 and minimum leaf size 20 to 200; forest depth 8 to 18 and leaf size 20 to 200 with square-root feature sampling; and class weight (none or balanced) for every classifier (appendix F). Class weighting is how the grid treats the imbalance. We did not resample: the alert uses calibrated probabilities and a cost-based threshold, and in logistic risk models imbalance corrections can distort the calibration of the predicted risk (Van den Goorbergh et al., 2022; He and Garcia, 2009).

Lead time:

{{table:B7.reg.plain_vs_tuned}}

Detractor alert:

{{table:B7.clf.plain_vs_tuned}}

Tuning changed little: no tuned configuration beat its plain model by enough to be carried forward. The forest's best configuration sits at the edge of its grid in both tasks: the smallest leaf size, with the deepest trees for lead time and the shallowest for the alert. A best value on the boundary means a wider grid might do better. The grid was fixed in advance and was not extended, because the selection rule below keeps the plain model either way; extending it after the test would mean choosing on the test (section 10).

### 6.4 Selection, calibration and threshold

**The one-standard-error rule.** Among the finalists, we keep the simplest model whose mean validation score is within one standard error of the best mean, where the standard error measures how much the score varies from fold to fold. The forest had the best mean in both tasks, but within one standard error of the plain model, so the plain linear model (lead time) and the plain logistic model (alert) were selected. This is a deliberate preference for simplicity, and it should be read with the paired results above: for the alert the forest beats the logistic model in four of five folds, by more than its paired standard error, but by much less than the fold-to-fold variation that the rule uses. The rule was fixed before training, and the simpler model is easier to explain, calibrate and serve.

**Calibration.** The alert's probabilities are calibrated with a sigmoid fitted on time-ordered inner splits, so that both pipelines share one probability scale for thresholds and costs. The pre-set rule would have kept the raw probabilities, which had a slightly better Brier score; we kept the sigmoid for comparability and record it as a deviation (section 10).

**Threshold.** With a missed detractor weighted as five false alerts, an alert pays off when the predicted risk exceeds 1/6, and that is the frozen threshold. After the test, the business chose a higher operating threshold for the improved pipeline, 4/15, to cut false alarms; the frozen 1/6 result stays the unbiased test result (section 7).

### 6.5 Why A became B

The baseline was complete and sound, and its own evidence showed where it could not go further:

| What the baseline's evidence showed | Change in the improved pipeline | How it was checked before the test |
| --- | --- | --- |
| The strongest driver of a bad review, late delivery ({{A3.clf.detractor_rate_late}} detractors when late against {{A3.clf.detractor_rate_on_time}} on time), is unknown at checkout | The alert moves to carrier handover, where this order's dispatch delay is known; orders never handed over are flagged by a rule | Validation AP on the same rows (below) |
| Delivery speed varies with the route and changes over time (section 4), but checkout features carry no recent seller or route behaviour | Seller and route history features (section 5.2) | Ranking and selection (section 5.4); validation scores |
| Distant, thinly served states add noise that a single model fits poorly | Scope narrowed to the seven largest states with known distance; the baseline serves every other order | The scope effect is measured separately (section 7) |

The baseline's validation results set the bar: MAE {{B9.reg.val_mae_A_on_A}} days against {{B9.reg.val_mae_Adummy_on_A}} for its dummy, and AP {{B9.clf.val_ap_A_on_A}} against {{B9.clf.val_ap_Adummy_on_A}}.

**The adoption rule, fixed before the test.** The improved pipeline is adopted for a task if, on its own validation rows, its five-fold mean beats the baseline's frozen model refitted on the same folds, even by a small margin. It did, in every fold of both tasks:

Lead time (MAE in days):

{{table:B8.reg.adoption}}

Detractor alert (AP):

{{table:B8.clf.adoption}}

Both pipelines then went to the single test read regardless of this result, and the test did not re-choose any model, calibration or threshold. Everything else was inherited unchanged from the baseline: the folds, the model families and grids, the selection rule, the metrics and the calibration and threshold procedure.
