## 1 Problem and metrics

Olist is a Brazilian marketplace: independent sellers ship each order to the customer through a carrier, and the customer reviews the purchase afterwards. Two things go wrong often enough to matter. Deliveries arrive later than the customer expected, and a share of customers leave a 1 or 2 star review, which hurts the seller's and the platform's reputation.

**Why it matters to the business.** The development period, January 2017 to late May 2018, holds {{B2.reg.dev_rows_A}} delivered orders, each worth on average R$ {{A3.reg.price_mean}} in goods plus R$ {{A3.reg.freight_mean}} in freight, so a customer lost to a poor experience is revenue lost to the seller and the platform. The business grew fast: monthly revenue from item prices rose from R$ {{BIZ.rev_2017_03}} in March 2017 to R$ {{BIZ.rev_2018_04}} in April 2018, {{BIZ.rev_growth}} times as much, with a peak of R$ {{BIZ.rev_peak}} in November 2017 against R$ {{BIZ.rev_2017_10}} in October (figure below). Delivery is where the experience breaks under pressure. When volume jumped in November 2017 (Black Friday: {{A3.trend.orders_2017_11}} orders against {{A3.trend.orders_2017_10}} in October), the share of orders delivered after Olist's promised date rose from {{A3.trend.late_2017_10}} to {{A3.trend.late_2017_11}}, and it peaked at {{A3.trend.late_2018_03}} in March 2018. Late orders go with bad reviews: {{A3.clf.detractor_rate_late}} of late orders received a 1 or 2 star review, against {{A3.clf.detractor_rate_on_time}} of orders delivered on time, and the detractor share rose from {{A3.trend.detractor_2017_10}} in October 2017 to {{A3.trend.detractor_2018_03}} in March 2018 ({{A3.clf.dev_prevalence}} over the whole period). Reviews are public, and a disappointed customer may not buy again. Promising faster is not a free fix either: in an experiment with an online retailer, faster delivery promises raised sales and profit but also reduced customer retention (Cui et al., 2024). Few customers order again soon: in a typical month only {{BIZ.repeat_mean}} of customers placed more than one order in that month (between {{BIZ.repeat_min}} and {{BIZ.repeat_max}}), so revenue rests on many occasional buyers, for whom one late delivery or one bad review can be the whole experience of the platform.

*Figure: Monthly revenue (item prices, freight excluded) and customer repeat rate, March 2017 to April 2018, the last full month before the test period; Business overview data of the dashboard, computed with the dashboard's own code (F.BIZ.revenue_repeat).*

The two models answer these two problems. The lead-time model gives a delivery promise the operation can keep, so sales are not bought with broken promises; the detractor alert lets customer service reach an at-risk customer before the review is written. We frame one delivery experience as two prediction tasks, each made at the moment the business can still act on it.

*Table 2. The two prediction tasks.*

| | Regression: delivery lead time | Classification: detractor alert |
| --- | --- | --- |
| Question | How many days from purchase to delivery? | Will the customer leave a 1–2 star review? |
| Target | Lead time in days, purchase to delivery (modelled on the log scale) | Detractor: the order's lowest valid review score is 1 or 2 |
| Prediction moment | At checkout | At carrier handover (Pipeline A predicts at checkout) |
| Who uses it, and how | Fulfilment and customer service show a delivery range to the customer when the order is placed | Customer service contacts customers at risk after the parcel is handed to the carrier, before the review is written |
| Primary metric | MAE in days; RMSE, R² and the share within 3 days reported beside it | Average precision (AP); ROC-AUC, Brier score, precision and recall at the threshold reported beside it |
| Cost of an error | A late promise breaks the customer's expectation; an early one only looks pessimistic | One missed detractor is weighted as five false alerts (an assumption, used to set the threshold) |

**Why these moments.** At checkout the platform has the basket, the prices, the seller and customer locations and the seller's past behaviour, which is what a delivery promise can use. A review alert at checkout would come too early: the strongest signal of a bad review in our data is a late delivery, and nothing about this order's dispatch is known yet. At carrier handover the seller's own delay is known and there is still time to contact the customer, so the alert is made then. Orders that are never handed over cannot be scored; a simple rule flags them when the shipping limit passes (section 9).

**Why MAE and AP.** MAE is measured in days, the unit of the promise, and is less driven by a few very late orders than RMSE, which we report alongside. Detractors are a minority of orders ({{B9.clf.test_prevalence_B}} of Pipeline B's test orders), so accuracy would look high for a model that never alerts: with imbalanced classes, accuracy can hide weak detection of the minority class (He and Garcia, 2009). AP summarises precision over all recall levels; a random ranking scores about the detractor share, so that share is the baseline AP is judged against. The cost weighting turns the ranking into a decision: the alert threshold is the probability above which an alert costs less than a likely missed detractor.

**How we judge success.** Each task has two yardsticks, both measured on the same test orders. The first is the dummy model, which predicts the median lead time or the detractor share for every order: a useful model must beat it clearly. On the test, the delivered model's MAE is {{B9.reg.test_mae_B}} days against {{B9.reg.test_mae_dummy_B}} for the dummy, and its AP is {{B9.clf.test_ap_B}} against a detractor share of {{B9.clf.test_prevalence_B}}. The second is Pipeline A, scored on the same orders (section 1.1). The rules for keeping a more complex model and for adopting Pipeline B were fixed before the test was read; no business target in days or AP was set in advance, so these yardsticks are how we judge the result, not a promise made beforehand.

**Stakeholders.** Fulfilment owns the delivery promise; customer service owns the alert and the contact; seller management uses both to see which sellers and routes fall behind. Each gets a view in the dashboard (section 8).

### 1.1 From baseline to delivered model

Pipeline A was built first, for every order, and is sound. Its validation results beat its dummies: MAE {{B9.reg.val_mae_A_on_A}} days against {{B9.reg.val_mae_Adummy_on_A}} for its dummy, and AP {{B9.clf.val_ap_A_on_A}} against {{B9.clf.val_ap_Adummy_on_A}}.

Its own exploration then showed three limits, and each led to one change in Pipeline B, the delivered model:

*Table 3. Pipeline A's evidence and the changes it led to.*

| What Pipeline A's evidence showed | Change in Pipeline B | How it was checked before the test |
| --- | --- | --- |
| The strongest signal of a bad review, late delivery ({{A3.clf.detractor_rate_late}} detractors when late against {{A3.clf.detractor_rate_on_time}} on time), is unknown at checkout | The alert moves to carrier handover, where this order's dispatch delay is known; orders never handed over are flagged by a rule | Validation AP on the same rows (section 6.5) |
| Delivery speed varies with the route and changes over time (section 4), but checkout features carry no recent seller or route behaviour | Seller and route history features (section 5.1) | Ranking and selection (section 5.3); validation scores |
| Distant, thinly served states add noise that a single model fits poorly | Scope narrowed to the seven largest states with known distance; Pipeline A serves every other order | The scope effect is measured separately (section 7) |

Pipeline B was adopted only after it beat Pipeline A on the same validation folds, under a rule fixed before the test (section 6.5). Pipeline A's frozen model still serves every order outside the seven states.
