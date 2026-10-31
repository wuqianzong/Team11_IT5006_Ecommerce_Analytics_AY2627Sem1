## 5 Models, validation and tuning

Models are compared from the simplest upwards, on the same time-ordered folds, under rules fixed before any test order was read.

**Validation design.** Leakage takes several forms beyond rows shared between training and test (Kapoor and Narayanan, 2023). Our orders are dated and customers return, so a random split would train on orders placed after the ones it predicts and could put one customer on both sides. We use five chronological, expanding folds before the test period: each fold trains on all orders up to a date and validates on the following weeks. Customers seen in a validation window are removed from its training rows, and a training order counts only if its label was known before the validation window starts (fold windows in appendix A). Cross-validation of this kind estimates how a model generalises, and the more flexible a model, the more its variance must be weighed against its lower bias (James et al., 2023).

**Model ladder.** We use two families, linear and tree-based, each started from its simplest variant: a dummy that predicts the median lead time or the detractor share; plain linear regression or unpenalised logistic regression, with the pipeline as preprocessing (Müller and Guido, 2016); a single decision tree; and a random forest, which averages many randomised trees (Breiman, 2001) and is a strong baseline on medium-sized tabular data (Grinsztajn et al., 2022). Each step must beat the step below it on the same folds. Tables 4 and 5 give the mean gain over the five folds, its paired standard error and the folds won (a positive gain is lower MAE or higher AP).

*Table 4. Model ladder on the five folds, lead time (gain in MAE days).*

{{table:M2.reg.ladder}}

*Table 5. Model ladder on the five folds, detractor alert (gain in AP).*

{{table:M2.clf.ladder}}

The linear and logistic models beat the dummy in every fold. The single tree and the forest gain little over them for lead time, and the tree is worse for the alert.

**Tuning.** Each family was then tuned on the same folds with grids fixed in advance: Ridge alpha and logistic C from 0.01 to 100; tree depth 4 to 18 and minimum leaf size 20 to 200; forest depth 8 to 18 and leaf size 20 to 200; and class weight (none or balanced) for every classifier. Class weighting is how the grid treats the imbalance. We did not resample, because the alert's threshold needs calibrated probabilities, and imbalance corrections can distort the calibration of logistic risk models (van den Goorbergh et al., 2022). A tuned configuration is carried forward only if it beats its plain model by more than one standard error of its fold scores; none did (appendix C).

**Selection.** Among the finalists we keep the simplest model whose mean validation score is within one standard error of the best. For lead time the single tree has the best mean MAE, {{M2.reg.val_tree}} days (standard error {{M2.reg.val_se_tree}}), against {{M2.reg.val_linear}} for plain linear regression, so the linear model is kept. For the alert the forest has the best mean AP, {{M2.clf.val_forest}} (standard error {{M2.clf.val_se_forest}}), against {{M2.clf.val_linear}} for plain logistic regression, so the logistic model is kept. This is a deliberate preference for simplicity: the forest wins four of five alert folds by more than its paired standard error, but by much less than the fold-to-fold variation the rule uses.

**Calibration and threshold.** The logistic model's probabilities are calibrated with a sigmoid fitted on time-ordered inner splits. With a missed detractor weighted as five false alerts, an alert pays off when the predicted risk exceeds 1/6, which is the frozen threshold. On the validation folds it sends {{M2.clf.oof_alerts_per_day}} alerts a day, within customer service's review capacity of {{M2.clf.daily_alert_cap}}, with precision {{M2.clf.oof_precision}} and recall {{M2.clf.oof_recall}}.
