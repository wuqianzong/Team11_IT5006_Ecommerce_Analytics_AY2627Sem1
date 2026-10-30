## 6 Results

Validation scores chose the models, so they are optimistic; the test, read once on new customers after the models were frozen, is the unbiased estimate.

*Table 6. Lead time: validation and test results.*

| Model | Validation MAE (selection) | Test MAE | Test RMSE | Test R² | Within 3 days (test) |
| --- | --- | --- | --- | --- | --- |
| Linear regression (selected) | {{M2.reg.val_linear}} | {{M2.reg.test_mae_A}} | {{M2.reg.test_rmse_A}} | {{M2.reg.test_r2_A}} | {{M2.reg.test_within_3d_A}} |
| Dummy (median) | {{M2.reg.val_dummy}} | {{M2.reg.test_mae_Adummy}} | {{M2.reg.test_rmse_Adummy}} | {{M2.reg.test_r2_Adummy}} | {{M2.reg.test_within_3d_Adummy}} |

*Table 7. Detractor alert: validation and test results (precision, recall and F1 at the threshold 1/6).*

| Model | Validation AP (selection) | Test AP | Test ROC-AUC | Test Brier | Precision | Recall | F1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Logistic regression (selected) | {{M2.clf.val_linear}} | {{M2.clf.test_ap_A}} | {{M2.clf.test_roc_auc_A}} | {{M2.clf.test_brier_A}} | {{M2.clf.test_precision_A}} | {{M2.clf.test_recall_A}} | {{M2.clf.test_f1_A}} |
| Dummy (detractor share) | {{M2.clf.val_dummy}} | {{M2.clf.test_ap_Adummy}} | {{M2.clf.test_roc_auc_Adummy}} | {{M2.clf.test_brier_Adummy}} | — | — | — |

**Lead time.** The model beats the dummy on every test measure: MAE {{M2.reg.test_mae_A}} against {{M2.reg.test_mae_Adummy}} days, and {{M2.reg.test_within_3d_A}} of orders predicted within 3 days against {{M2.reg.test_within_3d_Adummy}}. R² is low ({{M2.reg.test_r2_A}}): most of the variation in delivery time is not visible at checkout. The test MAE is below the validation mean, which averages over folds that include the slow weeks after Black Friday and in early 2018 (section 1).

**Detractor alert.** The ranking is better than chance (AP {{M2.clf.test_ap_A}} against a detractor share of {{M2.clf.test_prevalence_A}}), but weak. At the frozen threshold it flags {{M2.clf.test_tp_A}} of {{M2.clf.test_positives}} detractors with {{M2.clf.test_fp_A}} false alerts, about {{M2.clf.test_alerts_per_day_A}} alerts a day, twice the validation rate and above the review capacity. Its weighted cost on the test, {{M2.clf.test_cost_A}}, is higher than the cost of sending no alert at all, {{M2.clf.test_cost_Adummy}}: the test period had fewer detractors than development, so a threshold set on development alerts too often. A checkout alert has little to work with, because the strongest driver of a bad review, a late delivery, is not yet known (section 7).

**What drives the predictions.** Permutation importance measures how much each feature contributes to the frozen model on the test orders: the score lost when the feature is shuffled. For lead time, distance dominates (shuffling it costs {{M2A.reg.top_importance}} days of MAE), followed by the seller's state, the product category and the payment type. For the alert, the number of sellers in the order ranks first (an AP loss of {{M2A.clf.top_importance}}), followed by the number of items and the seller's earlier review score: orders split across sellers, and sellers with poor past reviews, carry more risk. These are associations in the model, not causes. Coefficients and odds ratios are in appendix D.

*Figure: Permutation importance on the test orders, lead time (F.M2A.reg.importance) and detractor alert (F.M2A.clf.importance).*
