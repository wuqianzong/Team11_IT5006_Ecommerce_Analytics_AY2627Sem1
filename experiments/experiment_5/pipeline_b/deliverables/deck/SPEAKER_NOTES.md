# Deck v2: speaker script (10-minute slot)

Generated from the slide notes of deck v2 (https://claude.ai/artifact/NBiGTdX9JKB5kAeeX34gvc); the notes in the deck are
the source, with every number filled from the register. Timing: 9:00 of slides at about 110 words a minute,
then a 1:00 demo. The brief allows 10 minutes plus 5 minutes of Q&A.

## 1. Two predictions for every Olist order (0:20)

Good evening, we are Team 11. For every Olist order we make two predictions: how many days delivery will take, and whether the customer will leave a one- or two-star review. We built a baseline, Pipeline A, found its limits in its own evidence, and built Pipeline B to answer them.

## 2. Each prediction is made when the business can act (0:35)

Each prediction is made when someone can act on it. Lead time is predicted at checkout, when fulfilment shows the customer a delivery range, and we judge it by mean absolute error in days. The review alert is for customer service. Detractors are a minority, 9.9% of test orders, so accuracy would mislead and we use average precision. We weight a missed detractor as five false alerts, which puts the alert threshold at one in six.

## 3. Nine tables become one row per order (0:35)

Olist ships nine tables. Items, payments and reviews have several rows per order, so each is reduced to one row per order before the join, and the join stays one to one. Customers are matched on customer_unique_id, so the same person never sits on both sides of a split. The leakage rule: a column is a predictor only if it exists at the prediction moment. Delivery, carrier and review fields never are.

## 4. Every learned step is fitted on the training fold only (0:35)

Every learned step, imputation, encoding and scaling, sits inside one scikit-learn pipeline fitted on the training fold only and cloned for each model, so no validation or test statistic reaches a model. Missing numbers get the fold median and an indicator; skewed amounts get a log. We keep the late tail, because very late orders are real customers, and model the log of lead time instead. The newest 20% of orders were held out first and read once.

## 5. Lead time is skewed; detractors are a minority (0:35)

Two findings shaped the models. Lead time is skewed: median 11.2 days, skewness 2.41, hence the log target and MAE. And 14.8% of development orders are detractors, hence average precision, not accuracy. All exploration used development orders only; the test period was never looked at.

## 6. 24 checkout predictors, screened and ranked (0:30)

Pipeline A, the baseline, uses 24 predictors known at checkout: basket, price and freight, size, product, geography, calendar and payment. Each candidate was ranked by its association with the target. Notice what is missing: nothing about how this seller or this route has delivered recently.

## 7. Correlated features go first, then a 99% rule (0:35)

Before selection we check multicollinearity. We flag pairs above 0.9 correlation and features with a variance inflation factor above 10. No feature reached the VIF cut; one pair was identical, missing weight and missing volume, and we dropped one of them. Then a simple rule keeps the smallest set of features that carries 99% of the ranked signal.

## 8. Time-ordered folds; simple models first (0:35)

Validation uses five time-ordered folds: train on the past, validate on the following weeks, with returning customers removed from training. A random split would train on the future. Models climb a ladder from a dummy to linear or logistic, a tree and a forest, and we keep the simplest within one standard error. The baseline clearly beats its dummy: MAE 5.47 against 6.49 days, AP 0.232 against 0.148.

## 9. What the baseline cannot see at checkout (0:45)

But A's own evidence showed three limits. One: late delivery drives bad reviews, 57.2% detractors when late against 9.5% on time, yet at checkout lateness is unknown. Two: speed depends on the route and changes over time, from a median of 7.8 days to Sao Paulo to 27.1 to Amazonas, and checkout features carry no recent behaviour. Three: thin, distant routes are noisy and one model fits them poorly. Each limit points to one change in Pipeline B.

## 10. Recent seller and route history rank at the top (0:40)

Pipeline B answers the first two limits. New features describe the route and the recent history of the seller and the route: late handovers, dispatch days, recent delivery and transit times, computed only from other orders completed in earlier weeks. For the alert, B moves to carrier handover, where this order's own dispatch delay is known. In both tasks the new features rank at the top.

## 11. Seven states, nested states removed, plain models kept (0:35)

The third limit is answered by scope: B serves the seven largest states with a known distance, 61,233 development orders for lead time, and A's frozen model serves every other order. Inside the scope, the route fixes both states, so the state columns are dropped to keep the design matrix full rank. The same ladder and one-standard-error rule again keep the plain linear and logistic models.

## 12. B beats A on the folds; scope and features split the gain (0:40)

Before touching the test, we fixed the adoption rule: B must beat A on the same folds. It did, in every fold of both tasks. For lead time most of the gain is scope: A improves from 5.470 to 5.142 days on B's rows, and B reaches 5.025. For the alert, scope changes almost nothing; the gain comes from the new features and the later moment.

## 13. B’s promise errors are smaller on the same orders (0:40)

Then the test, read once. On the same orders B's error is 3.30 days against 4.03 for A; the difference, -0.729 days, has a 95% interval that excludes zero, and B is better on all 20 routes judged. 57.6% of orders land within three days. One caveat: B leaves slightly more orders more than three days late, so the promise needs a buffer.

## 14. B ranks likely detractors better on the same orders (0:40)

For the alert, B's average precision is 0.197 against 0.178, with an interval above zero, and ROC-AUC and Brier agree. Part of the gain is the later moment: B scores at handover, A at checkout. The frozen threshold of one in six is the unbiased result. After the test, the business chose four in fifteen to cut false alarms: 5.6 alerts a day at precision 0.346.

## 15. What operations can do now, shown live next (0:40)

What can operations do now? Promise a range: a 12.0-day buffer, chosen on validation, left 1.5% of test orders late. Alert at handover: with A's fallback outside the seven states, about 20.5 alerts a day; the 6-a-day review cap applies to B alone, and the team accepted the higher combined volume. Flag missed dispatch with a simple rule. Limits: four in fifteen was chosen after the test, the test period was faster than development, and these are associations, not causes. Let me show you the app.

## Demo (1:00)

1. Open the app on the **ML deployment** tab. "These are held-out test orders that the serving rule alerts on, B first by risk."
2. The first order is already picked in 4.1. Point at 4.2: "what we know at handover: the seller's delay, the route, both predictions, and which model made them."
3. In 4.2.2, show **Logistics −10%**: "if this route were 10% faster, the risk drops; this is an association, not the effect of the action."
4. Switch to **Detractor risk at handover**, panel 3.4: move the slider off 4/15 and back. "Operations choose the volume; precision and cost follow."
