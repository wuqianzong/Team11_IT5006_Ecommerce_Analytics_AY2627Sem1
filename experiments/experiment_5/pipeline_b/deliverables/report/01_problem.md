## 1 Problem and metrics

Olist is a Brazilian marketplace: independent sellers ship each order to the customer through a carrier, and the customer reviews the purchase afterwards. Two things go wrong often enough to matter. Deliveries arrive later than the customer expected, and a share of customers leave a 1 or 2 star review, which hurts the seller's and the platform's reputation. We frame one delivery experience as two prediction tasks, each made at the moment the business can still act on it.

*Table 2. The two prediction tasks.*

| | Regression: delivery lead time | Classification: detractor alert |
| --- | --- | --- |
| Question | How many days from purchase to delivery? | Will the customer leave a 1–2 star review? |
| Target | Lead time in days, purchase to delivery (modelled on the log scale) | Detractor: the order's lowest valid review score is 1 or 2 |
| Prediction moment | At checkout | At carrier handover (the baseline predicts at checkout) |
| Who uses it, and how | Fulfilment and customer service show a delivery range to the customer when the order is placed | Customer service contacts customers at risk after the parcel is handed to the carrier, before the review is written |
| Primary metric | MAE in days; RMSE, R² and the share within 3 days reported beside it | Average precision (AP); ROC-AUC, Brier score, precision and recall at the threshold reported beside it |
| Cost of an error | A late promise breaks the customer's expectation; an early one only looks pessimistic | One missed detractor is weighted as five false alerts (an assumption, used to set the threshold) |

**Why these moments.** At checkout the platform has the basket, the prices, the seller and customer locations and the seller's past behaviour, which is what a delivery promise can use. A review alert at checkout would come too early: the strongest driver of a bad review is a late delivery, and nothing about this order's dispatch is known yet. At carrier handover the seller's own delay is known and there is still time to contact the customer, so the alert is made then. Orders that are never handed over cannot be scored; a simple rule flags them when the shipping limit passes (section 9).

**Why MAE and AP.** MAE is measured in days, the unit of the promise, and is less driven by a few very late orders than RMSE, which we report alongside. Detractors are a minority of orders ({{B9.clf.test_prevalence_B}} of the improved pipeline's test orders), so accuracy would look high for a model that never alerts: with imbalanced classes, accuracy can hide weak detection of the minority class (He and Garcia, 2009). AP summarises precision over all recall levels; a random ranking scores about the detractor share, so that share is the baseline AP is judged against. The cost weighting turns the ranking into a decision: the alert threshold is the probability above which an alert costs less than a likely missed detractor.

**How we judge success.** Each task has two yardsticks, both measured on the same test orders. The first is the dummy model, which predicts the median lead time or the detractor share for every order: a useful model must beat it clearly. On the test, the delivered model's MAE is {{B9.reg.test_mae_B}} days against {{B9.reg.test_mae_dummy_B}} for the dummy, and its AP is {{B9.clf.test_ap_B}} against a detractor share of {{B9.clf.test_prevalence_B}}. The second is the baseline pipeline, scored on the same orders (section 6). The rules for keeping a more complex model and for adopting the improved pipeline were fixed before the test was read; no business target in days or AP was set in advance, so these yardsticks are how we judge the result, not a promise made beforehand.

**Stakeholders.** Fulfilment owns the delivery promise; customer service owns the alert and the contact; seller management uses both to see which sellers and routes fall behind. Each gets a view in the dashboard (section 8).
