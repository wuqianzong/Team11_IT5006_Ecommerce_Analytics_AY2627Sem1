## 6 Modelling and the A-to-B decision

Models are compared from the simplest upwards, on the same time-ordered folds, under rules fixed before any test order was read. We first built a complete baseline (Pipeline A), then one focused improvement (Pipeline B) that changes only what Pipeline A's evidence pointed to; both were frozen and scored once on the test together.

### 6.1 Validation design

Leakage takes several forms beyond rows shared between training and test (Kapoor and Narayanan, 2023). Our orders are dated and customers return, so a random or stratified split would train on orders placed after the ones it predicts, and could put one customer on both sides. We therefore use five chronological, expanding folds before the test period: each fold trains on all orders up to a date and validates on the following weeks (windows and sizes in Tables A2 and A3). Customers seen in a validation window are removed from its training rows, and a training order counts only if its label (delivery or review) was known before the validation window starts.

*Figure: Time-ordered folds and the test period (F.reg.partition).*

Minimum fold sizes were set before the folds were built; Pipeline B's fold 1 falls short on training orders and was kept as a recorded deviation, and instead of stratifying, each fold's detractor share is reported (appendix A). Every random step uses seed 42, so a rerun on the same machine reproduces every stored output exactly.

### 6.2 Model ladder

We use two model families, linear and tree-based, each started from its simplest variant, as the project description requires: a dummy that predicts the median lead time or the detractor share; plain linear regression or unpenalised logistic regression; a single decision tree; and a random forest of 200 trees (Breiman, 2001). Tree ensembles are the natural non-linear comparison for tabular data of this kind (Grinsztajn et al., 2022). Plain least squares and unpenalised logistic regression need a full-rank design matrix, which section 5.2 shows holds in every fold. Stacking and gradient boosting were considered but not added (section 2).

Each step up the ladder must beat the step below it on the same folds. Appendix H gives every candidate's fold scores; Tables K8 and K9 give the mean gain over the five folds, its paired standard error and the number of folds in which the more complex model wins (MAE in days, a positive gain means lower error; AP for the alert).

*Figure: Model ladder on the five folds, lead time (F.reg.family_ladder) and detractor alert (F.clf.family_ladder).*

**Training results.** Tables 4 and 5 put each delivered model's training, validation and test scores side by side. Training and validation are means over the five folds; the test model is refitted once on all development rows. The gap is validation minus training.

*Table 4. Training results, delivery lead time (MAE in days; lower is better).*

| Model | Final-fit rows | Training MAE | Validation MAE | Test MAE | Gap |
| --- | --- | --- | --- | --- | --- |
| Pipeline B, plain linear (delivered) | {{RT.reg.fit_rows}} | {{RT.reg.B.train}} | {{RT.reg.B.validation}} | {{RT.reg.B.test}} | {{RT.reg.B.gap}} |
| Dummy (median) | {{RT.reg.fit_rows}} | {{RT.reg.dummy.train}} | {{RT.reg.dummy.validation}} | {{RT.reg.dummy.test}} | {{RT.reg.dummy.gap}} |

*Table 5. Training results, detractor alert (AP; higher is better).*

| Model | Final-fit rows | Training AP | Validation AP | Test AP | Gap |
| --- | --- | --- | --- | --- | --- |
| Pipeline B, plain logistic, raw probabilities | {{RT.clf.fit_rows}} | {{RT.clf.raw.train}} | {{RT.clf.raw.validation}} | {{RT.clf.raw.test}} | {{RT.clf.raw.gap}} |
| Pipeline B, plain logistic, calibrated (delivered) | {{RT.clf.fit_rows}} | none (see text) | {{RT.clf.cal.validation}} | {{RT.clf.cal.test}} | none |
| Dummy (detractor share) | {{RT.clf.fit_rows}} | {{RT.clf.dummy.train}} | {{RT.clf.dummy.validation}} | {{RT.clf.dummy.test}} | {{RT.clf.dummy.gap}} |

The plain models do not overfit. For lead time the dummy, which has no features, shows the same gap as the linear model, so the gap is a period effect: the validation weeks were slower than the training weeks, and the test weeks faster. For the alert, validation AP is slightly above training AP for both the logistic model and the dummy, because the validation windows hold more detractors. The calibrated model has no single training AP: its sigmoid is fitted on time-ordered inner splits of each training fold, so the calibrated scores exist only out of sample. The raw row shows how the same logistic model fits its own training rows; calibration then maps its probabilities onto the shared scale used for the threshold and costs (section 6.4). The learning curves (appendix H) show that the most recent orders predict best and that more data narrows the gap without lifting validation much.

### 6.3 Tuning

Each family was then tuned on the same folds, with grids fixed before any tuning result was seen (Ridge alpha, logistic C, tree and forest depth and leaf size, and class weight for every classifier; appendix F). Class weighting is how the grid treats the imbalance. We did not resample: the alert uses calibrated probabilities and a cost-based threshold, and in logistic risk models imbalance corrections can distort the calibration of the predicted risk (Van den Goorbergh et al., 2022).

Tuning changed little (Tables K10 and K11). For lead time the tuned linear model's paired gain is {{B7.reg.tuned_gain_linear}} days and the tuned forest's {{B7.reg.tuned_gain_forest}}; for the alert the tuned logistic model gains {{B7.clf.tuned_gain_linear}} AP, well inside its fold-to-fold standard error of {{B7.clf.tuned_se_linear}}, and the tuned forest {{B7.clf.tuned_gain_forest}}. No tuned configuration beat its plain model by enough to be carried forward. The forest's best configuration sits at the edge of its grid in both tasks, so a wider grid might do better; the grid was fixed in advance and not extended, because the selection rule below keeps the plain model either way (section 10).

### 6.4 Selection, calibration and threshold

**The one-standard-error rule.** Among the finalists, we keep the simplest model whose mean validation score is within one standard error of the best mean, where the standard error measures how much the score varies from fold to fold. The forest had the best mean in both tasks, but within one standard error of the plain model, so the plain linear model (lead time) and the plain logistic model (alert) were selected. This is a deliberate preference for simplicity: for the alert the forest wins in four of five folds by more than its paired standard error, but by much less than the fold-to-fold variation the rule uses, and the simpler model is easier to explain, calibrate and serve.

**Calibration.** The alert's probabilities are calibrated with a sigmoid fitted on time-ordered inner splits, so that both pipelines share one probability scale for thresholds and costs. The pre-set rule preferred the raw probabilities (slightly better Brier score); we kept the sigmoid for comparability, a recorded deviation (section 10).

**Threshold.** With a missed detractor weighted as five false alerts, an alert pays off when the predicted risk exceeds 1/6, and that is the frozen threshold. After the test, the business chose a higher operating threshold for Pipeline B, 4/15, to cut false alarms; the frozen 1/6 result stays the unbiased test result (section 7).

### 6.5 Adopting Pipeline B

Section 1.1 sets out Pipeline A's limits and the change each one led to.

**The adoption rule, fixed before the test.** Pipeline B is adopted for a task if, on its own validation rows, its five-fold mean beats Pipeline A's frozen model refitted on the same folds, even by a small margin. It did, in every fold of both tasks (Tables K12 and K13): Pipeline B's MAE is lower by {{B8.reg.adopt_gain_fold1}} days in fold 1 up to {{B8.reg.adopt_gain_fold4}} in fold 4, and its AP (before calibration, as the rule specifies) higher by {{B8.clf.adopt_gain_fold5}} in fold 5 up to {{B8.clf.adopt_gain_fold2}} in fold 2.

Both pipelines then went to the single test read regardless of this result, and the test did not re-choose any model, calibration or threshold. Everything else was inherited unchanged from Pipeline A: the folds, the model families and grids, the selection rule, the metrics and the calibration and threshold procedure.
