## Executive summary

For each Olist order we predict, at checkout, how many days delivery will take and whether the customer will leave a 1 or 2 star review. The first sets a delivery promise; the second lets customer service act before the review is written. Both matter because the platform's revenue grew fast while late deliveries and bad reviews rose with volume.

**Method.** One row per order with only what is known at checkout; every learned step fitted inside time-ordered, customer-purged folds; correlated features removed and the rest selected by a 99% ranking rule; two model families, linear and tree-based, compared from a dummy upwards, keeping the simplest model within one standard error of the best. Plain linear regression and plain logistic regression were selected and scored once on a held-out test period of new customers.

**Results.** Lead time: test MAE {{M2.reg.test_mae_A}} days against {{M2.reg.test_mae_Adummy}} for the dummy. Detractor alert: test AP {{M2.clf.test_ap_A}} against a detractor share of {{M2.clf.test_prevalence_A}}; at the frozen threshold it alerts too often on the test period.

**Use and limits.** Promise a range around the lead-time prediction; use the alert as a ranking within review capacity. The alert is limited by what checkout cannot see, and all findings are associations, not causes.
