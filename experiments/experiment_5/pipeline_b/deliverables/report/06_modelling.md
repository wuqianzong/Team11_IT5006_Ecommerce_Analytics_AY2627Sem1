## 6 Modelling and the A-to-B decision

Models are compared from the simplest upwards, on the same time-ordered folds, under rules fixed before any test order was read. We first built a complete baseline (Pipeline A), then one focused improvement (Pipeline B) that changes only what Pipeline A's evidence pointed to; both were frozen and scored once on the test together.

### 6.1 Validation design

Leakage takes several forms beyond rows shared between training and test (Kapoor and Narayanan, 2023). Our orders are dated and customers return, so a random or stratified split would train on orders placed after the ones it predicts, and could put one customer on both sides. We therefore use five chronological, expanding folds before the test period: each fold trains on all orders up to a date and validates on the following weeks (windows and sizes in Tables A2 and A3). Customers seen in a validation window are removed from its training rows, and a training order counts only if its label (delivery or review) was known before the validation window starts.

*Figure: Time-ordered folds and the test period (F.reg.partition).*

Each fold must have at least {{B5.min_train_rows}} training orders and, for the alert, 100 detractors in each part; the minimums were set before the folds were built. Fold 1 of Pipeline B falls short on training orders ({{B5.reg.fold1_train_rows}} for lead time, {{B5.clf.fold1_train_rows}} for the alert), because the seven-state scope and the warm-up remove early orders. We kept it, as a recorded deviation, so the two pipelines are compared on identical periods; every detractor minimum is met. Instead of stratifying, each fold's detractor share is reported, and it moves with the business over time (appendix A). Every metric is defined in appendix B. Every random step (trees, forests, tuning) uses seed 42, and forests predict on a single thread, so a rerun on the same machine reproduces every stored output exactly.

### 6.2 Model ladder

We use two model families, linear and tree-based, each started from its simplest variant, as the project description requires: a dummy that predicts the median lead time or the detractor share; plain linear regression or unpenalised logistic regression; a single decision tree; and a random forest of 200 trees (Breiman, 2001). Tree ensembles are the natural non-linear comparison for tabular data of this kind (Grinsztajn et al., 2022). Plain least squares and unpenalised logistic regression need a full-rank design matrix, which section 5.2 shows holds in every fold. Stacking and gradient boosting were considered but not added (section 2).

Each step up the ladder must beat the step below it on the same folds. Appendix H gives every candidate's fold scores; Tables K8 and K9 give the mean gain over the five folds, its paired standard error and the number of folds in which the more complex model wins (MAE in days, a positive gain means lower error; AP for the alert).

*Figure: Model ladder on the five folds, lead time (F.reg.family_ladder) and detractor alert (F.clf.family_ladder).*

*Table 5. Training and validation scores by model family, mean of the five folds (lead time MAE in days, lower is better; alert AP before calibration, higher is better).*

| Family | Lead time: training MAE | Lead time: validation MAE | Alert: training AP | Alert: validation AP |
| --- | --- | --- | --- | --- |
| Dummy | {{B6.reg.dummy_train}} | {{B6.reg.dummy_validation}} | {{B6.clf.dummy_train}} | {{B6.clf.dummy_validation}} |
| Linear or logistic regression | {{B6.reg.linear_train}} | {{B6.reg.linear_validation}} | {{B6.clf.linear_train}} | {{B6.clf.linear_validation}} |
| Single tree | {{B6.reg.tree_train}} | {{B6.reg.tree_validation}} | {{B6.clf.tree_train}} | {{B6.clf.tree_validation}} |
| Random forest | {{B6.reg.forest_train}} | {{B6.reg.forest_validation}} | {{B6.clf.forest_train}} | {{B6.clf.forest_validation}} |

**Training results.** For the alert the plain logistic model scores about the same on its training and validation rows (AP {{B6.clf.linear_train}} against {{B6.clf.linear_validation}}), so it does not memorise the training orders; the forest fits its training rows more closely ({{B6.clf.forest_train}} against {{B6.clf.forest_validation}}). For lead time every family's validation error is higher than its training error, by about as much for the dummy ({{B6.reg.dummy_train}} against {{B6.reg.dummy_validation}} days) as for the linear model ({{B6.reg.linear_train}} against {{B6.reg.linear_validation}}): a model with no features shows the same gap, so it comes from slower validation windows, not from overfitting. The learning curves on fold 5 (figure below) train each model on the most recent 20% to 100% of its {{B6.reg.lc_train_rows_100}} training orders. The linear model's validation MAE is lowest with the most recent 20% ({{B6.reg.lc_plain_validation_20}} days, against {{B6.reg.lc_plain_validation_100}} with all rows): recent orders predict the next weeks best, a sign of drift that Pipeline B's recent-history features address. The logistic model's validation AP stays near {{B6.clf.lc_plain_validation_100}} while its training AP falls from {{B6.clf.lc_plain_train_20}} to {{B6.clf.lc_plain_train_100}}, largely because older rows hold fewer detractors (the dummy's training AP, which equals the detractor share, falls from {{B6.clf.lc_dummy_train_20}} to {{B6.clf.lc_dummy_train_100}}). More data narrows the gap without lifting validation much: the models are limited by what is known at the prediction moment, not by the number of orders.

*Figure: Learning curves on fold 5, lead time (F.reg.learning_curves) and detractor alert (F.clf.learning_curves).*

The linear model beats the dummy in every fold, by {{B6.reg.gain_linear}} days of MAE on average, and the logistic model by {{B6.clf.gain_linear}} AP. The single tree is worse than the linear model in both tasks: {{B6.reg.gain_tree}} days, better in {{B6.reg.gain_tree_folds}} of five folds, and {{B6.clf.gain_tree}} AP, better in {{B6.clf.gain_tree_folds}}. The forest is slightly better on average, {{B6.reg.gain_forest}} days (paired standard error {{B6.reg.gain_forest_se}}, better in {{B6.reg.gain_forest_folds}} folds), and more consistently so for the alert, {{B6.clf.gain_forest}} AP (standard error {{B6.clf.gain_forest_se}}, better in {{B6.clf.gain_forest_folds}} folds).

### 6.3 Tuning

Each family was then tuned on the same folds, with grids fixed before any tuning result was seen: Ridge alpha and logistic C from 0.01 to 100; tree depth 4 to 18 and minimum leaf size 20 to 200; forest depth 8 to 18 and leaf size 20 to 200 with square-root feature sampling; and class weight (none or balanced) for every classifier (appendix F). Class weighting is how the grid treats the imbalance. We did not resample: the alert uses calibrated probabilities and a cost-based threshold, and in logistic risk models imbalance corrections can distort the calibration of the predicted risk (Van den Goorbergh et al., 2022).

Tuning changed little (Tables K10 and K11). For lead time the tuned linear model's paired gain is {{B7.reg.tuned_gain_linear}} days and the tuned forest's {{B7.reg.tuned_gain_forest}}; for the alert the tuned logistic model gains {{B7.clf.tuned_gain_linear}} AP, well inside its fold-to-fold standard error of {{B7.clf.tuned_se_linear}}, and the tuned forest {{B7.clf.tuned_gain_forest}}. No tuned configuration beat its plain model by enough to be carried forward. The forest's best configuration sits at the edge of its grid in both tasks, so a wider grid might do better; the grid was fixed in advance and not extended, because the selection rule below keeps the plain model either way (section 10).

### 6.4 Selection, calibration and threshold

**The one-standard-error rule.** Among the finalists, we keep the simplest model whose mean validation score is within one standard error of the best mean, where the standard error measures how much the score varies from fold to fold. The forest had the best mean in both tasks, but within one standard error of the plain model, so the plain linear model (lead time) and the plain logistic model (alert) were selected. This is a deliberate preference for simplicity: for the alert the forest wins in four of five folds by more than its paired standard error, but by much less than the fold-to-fold variation the rule uses, and the simpler model is easier to explain, calibrate and serve.

**Calibration.** The alert's probabilities are calibrated with a sigmoid fitted on time-ordered inner splits, so that both pipelines share one probability scale for thresholds and costs. The pre-set rule preferred the raw probabilities (slightly better Brier score); we kept the sigmoid for comparability, a recorded deviation (section 10).

**Threshold.** With a missed detractor weighted as five false alerts, an alert pays off when the predicted risk exceeds 1/6, and that is the frozen threshold. After the test, the business chose a higher operating threshold for Pipeline B, 4/15, to cut false alarms; the frozen 1/6 result stays the unbiased test result (section 7).

### 6.5 Adopting Pipeline B

Section 1.1 sets out Pipeline A's limits and the change each one led to.

**The adoption rule, fixed before the test.** Pipeline B is adopted for a task if, on its own validation rows, its five-fold mean beats Pipeline A's frozen model refitted on the same folds, even by a small margin. It did, in every fold of both tasks (Tables K12 and K13): Pipeline B's MAE is lower by {{B8.reg.adopt_gain_fold1}} days in fold 1 up to {{B8.reg.adopt_gain_fold4}} in fold 4, and its AP (before calibration, as the rule specifies) higher by {{B8.clf.adopt_gain_fold5}} in fold 5 up to {{B8.clf.adopt_gain_fold2}} in fold 2.

Both pipelines then went to the single test read regardless of this result, and the test did not re-choose any model, calibration or threshold. Everything else was inherited unchanged from Pipeline A: the folds, the model families and grids, the selection rule, the metrics and the calibration and threshold procedure.
