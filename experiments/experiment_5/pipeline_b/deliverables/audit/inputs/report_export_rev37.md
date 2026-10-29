# Team 11 final report — delivery time and detractor alerts

Oct 26, 2026 · @Henry

Draft for team review. Every number is filled from the Pipeline B register (pipeline\_b/evidence/registry\_B.yaml); comment on any point. Revised: the full report written to plan v2, with the alert review order in section 9 and references checked against publisher records; the dated change record is pipeline\_b/deliverables/report/records/CHANGES.md, and earlier drafts stay in the doc history.

## Executive summary

For each Olist order the business needs two answers: how many days delivery will take, so the customer can be promised a realistic range, and whether the customer is likely to leave a 1 or 2 star review, so customer service can act before it is written. We predict the first at checkout and the second when the parcel is handed to the carrier.

**Method.** Every model row holds only what is known at its prediction moment; every step learned from data is fitted inside time-ordered, customer-purged folds; correlated and nested features are removed by a stated rule before selection; and models are compared from the simplest upwards, keeping the simpler one unless a more complex one is better by more than the fold-to-fold variation. We first built a complete baseline (Pipeline A) and then one focused improvement (Pipeline B): the seven largest states, the seller's and the route's recent delivery history, and the alert moved to carrier handover. The rule for adopting the improvement was fixed before the test, and both pipelines were frozen and scored once on the same test period.

| Task | Improved pipeline | Baseline on the same orders | Difference (95% interval) |
| --- | --- | --- | --- |
| Delivery lead time, MAE in days (lower is better) | 3.30 | 4.03 | -0.729 \[-0.754, -0.703\] |
| Share of orders predicted within 3 days | 57.6% | 44.3% |  |
| Detractor ranking, average precision (higher is better) | 0.197 | 0.178 | +0.0187 \[+0.0089, +0.0291\] |

The improved pipeline is better on the same test orders in both tasks, and both intervals exclude zero. For lead time most of the gain comes from the narrower scope, the rest from the new features; for the alert it comes from the features and the later moment. Orders outside the seven states are served by the baseline's frozen model.

**Use.** Show delivery promises as a range around the prediction; alert customer service at handover (about 20.5 alerts a day on the test, including the fallback); flag orders whose shipping limit passes without a handover.

**Limits.** The test period was faster than development, the operating threshold was chosen after the test (the frozen threshold's result is reported as the unbiased one), and all findings are associations, not causes.

## 1 Problem and metrics

Olist is a Brazilian marketplace: independent sellers ship each order to the customer through a carrier, and the customer reviews the purchase afterwards. Two things go wrong often enough to matter. Deliveries arrive later than the customer expected, and a share of customers leave a 1 or 2 star review, which hurts the seller's and the platform's reputation. We frame one delivery experience as two prediction tasks, each made at the moment the business can still act on it.

|  | Regression: delivery lead time | Classification: detractor alert |
| --- | --- | --- |
| Question | How many days from purchase to delivery? | Will the customer leave a 1–2 star review? |
| Target | Lead time in days, purchase to delivery (modelled on the log scale) | Detractor: the order's lowest valid review score is 1 or 2 |
| Prediction moment | At checkout | At carrier handover (the baseline predicts at checkout) |
| Who uses it, and how | Fulfilment and customer service show a delivery range to the customer when the order is placed | Customer service contacts customers at risk after the parcel is handed to the carrier, before the review is written |
| Primary metric | MAE in days; RMSE, R² and the share within 3 days reported beside it | Average precision (AP); ROC-AUC, Brier score, precision and recall at the threshold reported beside it |
| Cost of an error | A late promise breaks the customer's expectation; an early one only looks pessimistic | One missed detractor is weighted as five false alerts (an assumption, used to set the threshold) |

**Why these moments.** At checkout the platform has the basket, the prices, the seller and customer locations and the seller's past behaviour, which is what a delivery promise can use. A review alert at checkout would come too early: the strongest driver of a bad review is a late delivery, and nothing about this order's dispatch is known yet. At carrier handover the seller's own delay is known and there is still time to contact the customer, so the alert is made then. Orders that are never handed over cannot be scored; a simple rule flags them when the shipping limit passes (section 9).

**Why MAE and AP.** MAE is measured in days, the unit of the promise, and is less driven by a few very late orders than RMSE, which we report alongside. Detractors are a minority of orders (9.9% of the improved pipeline's test orders), so accuracy would look high for a model that never alerts. AP summarises precision over all recall levels and is judged against the detractor share, which is what a random ranking would achieve (He and Garcia, 2009). The cost weighting turns the ranking into a decision: the alert threshold is the probability above which an alert costs less than a likely missed detractor.

**How we judge success.** Each task has two yardsticks, both measured on the same test orders. The first is the dummy model, which predicts the median lead time or the detractor share for every order: a useful model must beat it clearly. On the test, the delivered model's MAE is 3.30 days against 4.38 for the dummy, and its AP is 0.197 against a detractor share of 9.9%. The second is the baseline pipeline, scored on the same orders (section 6). The rules for keeping a more complex model and for adopting the improved pipeline were fixed before the test was read; no business target in days or AP was set in advance, so these yardsticks are how we judge the result, not a promise made beforehand.

**Stakeholders.** Fulfilment owns the delivery promise; customer service owns the alert and the contact; seller management uses both to see which sellers and routes fall behind. Each gets a view in the dashboard (section 8).

## 2 Literature review

The literature shaped three things in this project: what the predictions are for, how the models are compared, and how the evaluation guards against optimistic results. We organise it around our two questions and our method, and for each source we state the choice it supports. Every source was checked against the publisher's record; a source whose detailed results were not audited is cited only for the question it studies.

### 2.1 Delivery promises and customer response

**Delivery time and the promise.** Cui et al. (2024) separate the delivery speed promised to shoppers from the speed actually delivered. In an experiment with an online retailer they varied only the displayed promise, while the physical delivery stayed the same. Faster promises raised sales and profit, but also raised returns and reduced customer retention, and the authors argue that promises should be set for longer-run customer value rather than for conversion alone. This is why our lead-time model is framed as the input to a promise range (section 9) and not as a single date to display: a promise that is too optimistic has a cost after the purchase.

**Logistics and ratings.** Deshpande and Pendem (2023) study how logistics performance and ratings relate to purchasing behaviour and sales on an e-commerce platform. We cite their study for the question it addresses, the link between logistics and the ratings customers give, which is the link our detractor alert relies on; we do not cite specific effects from it. Our own data shows the size of that link for Olist directly (section 4).

**Gap.** None of the audited sources predicts a bad review at the moment a parcel is handed to the carrier, or separates the seller's dispatch delay from the carrier's transit time. Both are central to this project: the alert is made at handover, and the new features measure the seller's and the route's delivery history separately (section 5).

### 2.2 Choosing and comparing models

**Simple models first.** James et al. (2023) and Müller and Guido (2016) set out the practice we follow: start from a trivial baseline and a simple model, estimate generalisation by resampling, and add complexity only when it improves held-out performance. Müller and Guido also stress fitting preprocessing inside a pipeline, so that it does not leak information from the evaluation data. Our model ladder (section 6.2) starts from a dummy and from plain linear and logistic regression for exactly this reason.

**Tree ensembles.** A random forest averages many randomised trees, and its error depends on the strength of the individual trees and the correlation between them (Breiman, 2001). On the medium-sized tabular datasets they studied, tree ensembles remained strong baselines against deep learning (Grinsztajn et al., 2022). We therefore use the forest as the non-linear comparison for both tasks, alongside a single tree, rather than a neural network.

**Considered and not used.** Stacked generalisation learns a second-stage model from the held-out predictions of first-stage models (Wolpert, 1992), and gradient-boosted trees are a scalable alternative for tabular data (Chen and Guestrin, 2016). The project limits the number of model families, and the forest itself did not beat the simpler models by more than the selection rule requires, so neither was added (section 6.2).

### 2.3 Evaluation without optimism

**Leakage.** Kapoor and Narayanan (2023) show that leakage takes several forms beyond overlap between training and test rows, propose a taxonomy of leakage types, and find it inflating reported results across many published studies. Our defences are our own application of that warning: a leakage rule for each prediction moment, time-ordered folds that purge returning customers, preprocessing fitted inside each fold, and a test period read once (sections 3 and 6).

**Imbalanced targets.** He and Garcia (2009) review learning with unequal class sizes: accuracy can hide weak detection of the minority class, evaluation should reflect the class balance and the cost of each error, and resampling or cost-sensitive learning are options rather than requirements. Detractors are a minority of orders, so we judge the alert by average precision against the detractor share and set its threshold from an assumed cost ratio. For logistic risk models, Van den Goorbergh et al. (2022) show that imbalance corrections can harm the calibration of the predicted risks. Our alert needs calibrated probabilities to apply a cost threshold, so we tested class weighting as a grid option but did not resample (section 6.3).

### 2.4 What we take from the literature

| Source | What it supports in this project | Section |
| --- | --- | --- |
| Cui et al. (2024) | Treat the lead-time prediction as input to a promise range, set for longer-run value | 9 |
| Deshpande and Pendem (2023) | Logistics performance and ratings are linked; the alert targets that link | 1, 5 |
| James et al. (2023); Müller and Guido (2016) | Baselines first, resampling, preprocessing inside the pipeline | 3, 6 |
| Breiman (2001); Grinsztajn et al. (2022) | The random forest as the non-linear comparison on tabular data | 6 |
| Wolpert (1992); Chen and Guestrin (2016) | Stacking and boosting, considered and not used | 6 |
| Kapoor and Narayanan (2023) | Leakage rules per prediction moment, time-ordered folds, fold-local preprocessing | 3, 6 |
| He and Garcia (2009) | Average precision and a cost threshold instead of accuracy | 1, 6 |
| Van den Goorbergh et al. (2022) | Class weighting tested; no resampling, to keep probabilities calibrated | 6 |

## 3 Data and preprocessing

Every model row is one order, built only from what is known at that task's prediction moment, and every step below states its rule, its reason and where it is fitted. Steps learned from data are fitted on each training fold only, inside one scikit-learn pipeline, so no statistic from a validation or test order reaches a model (Kapoor and Narayanan, 2023; Müller and Guido, 2016).

**Sources and joins.** We use the Canvas copy of the Olist dataset: nine tables (orders, order items, payments, reviews, customers, sellers, products, geolocation and the category translation). The order is the unit. Items, payments and reviews have several rows per order, so each is aggregated to the order first and then joined one to one; customers join many to one. From the items we take the counts of items, products, sellers and categories, the total price, freight, weight and volume, and the primary item (the highest-priced, ties broken by item id), which gives the primary category and the primary seller. From the payments we take the main payment type and the largest number of instalments. Locations come from the median latitude and longitude of each ZIP prefix inside Brazil; the distance feature is the largest seller-to-customer distance in the order. Customers are matched across orders on `customer_unique_id`, because `customer_id` is new for every order; this is what lets us keep the same customer out of both training and test.

**Targets.** Lead time is the number of days from purchase to delivery, for delivered orders with valid timestamps. The detractor label is 1 when the order's lowest valid review score is 1 or 2. An order can have more than one review; taking the lowest could bias the label towards detractors, so every classification result is also scored against the first-review label. The two agree closely on the test (table below), so the choice does not drive the conclusions.

| model | label | ap | roc\_auc | brier | precision | recall |
| --- | --- | --- | --- | --- | --- | --- |
| B frozen | is\_detractor (agreed label) | 0.1972 | 0.636 | 0.0867 | 0.2077 | 0.3005 |
| B frozen | is\_detractor\_first (first review) | 0.1972 | 0.6363 | 0.08665 | 0.2077 | 0.3006 |
| A frozen | is\_detractor (agreed label) | 0.1785 | 0.604 | 0.08926 | 0.1583 | 0.3556 |
| A frozen | is\_detractor\_first (first review) | 0.1785 | 0.6043 | 0.08921 | 0.1583 | 0.3558 |

**Which orders each task keeps.** Both tasks drop orders purchased before 2017 (the 2016 months are too thin to represent the business), orders without items, orders without a usable payment or with missing instalments, orders with a negative price, freight, weight, volume or distance, and orders whose distance exceeds the width of Brazil. Regression keeps delivered orders with a valid lead time, and removes lead times that are extreme against the development orders (above the larger of 100 days and the mean plus 12 standard deviations). Classification keeps orders that were not cancelled or unavailable and have a valid review; an order whose review is dated at or before its purchase is removed, because its label cannot be trusted. These are the eligible orders.

**Leakage rules, set for each prediction moment.** A column may be a predictor only if its value exists at the moment of prediction.

- At checkout (lead time, and the baseline's alert): delivery dates, carrier dates, the order status, the approval time and every review field are outcomes or later events and never predictors.
- At carrier handover (the improved alert): this order's handover facts are known, its handover delay against the shipping limit and its dispatch time, but its delivery and review are not.
- Olist's estimated delivery date is known at checkout but is never used, because it is the output of the very process our lead-time model would replace.
- History features (the seller's and the route's recent behaviour) use only other orders whose events were complete in the weeks before this order's prediction week; no order ever sees its own outcome.

**Missing values, skew and outliers.** Numeric gaps are filled with the training fold's median, and a missing-value indicator is added so the model can tell a filled value from a real one; categorical gaps become their own "Unknown" level. Skewed money, weight, volume, distance and day-count features are log-transformed (log of 1 plus the value); integer counts are left as they are. The long late tail of lead time is kept: very late orders are real customer experiences, so the regression predicts the log of 1 plus the lead time instead of trimming them.

**Encoding and scaling.** States, route and category are one-hot encoded; the linear and logistic models drop one reference level per variable so that the design matrix stays full rank, while trees keep every level. A level never seen in training is ignored at prediction time. Numeric features are standardised for the linear and logistic models only. All of this is learned on the training fold and applied unchanged to its validation fold.

**Test period.** For each task the newest 20% of eligible orders, by purchase time, form the test period. It was held out before any exploration or feature work, and development customers who reappear in it were removed. It was scored exactly once, for both pipelines together.

**The improved pipeline's population.** The improved pipeline (section 6) keeps orders whose customer and primary seller are both in the seven largest states (SP, MG, RJ, PR, RS, BA, SC) and whose distance is known, applies a tighter lead-time cap computed on its own rows (mean plus 8 standard deviations), and drops the first six weeks of data, which are needed to start the seller and route history. For the alert it also drops orders never handed over and orders reviewed before their handover. The chain below accounts for every order from the baseline's development set to the rows each model trains on.

| Step | Lead time | Detractor alert |
| --- | --- | --- |
| Baseline development orders (eligible, before the test period) | 76,925 | 77,736 |
| Customer or seller outside the seven states | − 13,777 | − 13,983 |
| Distance unknown | − 606 | − 618 |
| Lead time above the improved pipeline's cap | − 45 | — |
| Never handed over to the carrier | — | − 461 |
| Reviewed at or before handover | — | − 146 |
| First six weeks (history warm-up) | − 1,264 | − 1,270 |
| Improved pipeline's development orders | 61,233 | 61,258 |
| Of these, with the label known before the test period (final fit) | 59,683 | 59,188 |
| Fold 5: training rows / validation rows | 47,415 / 9,059 | 47,237 / 8,646 |
| Test orders | 15,422 | 15,492 (1,541 detractors) |

The final fit uses fewer rows than the development set because a label must be known before the test period starts: an order delivered or reviewed after the cutoff cannot train the model that is tested on that period. Fold 5's training and validation rows together are fewer again, because the folds also purge customers who appear on both sides and require each training label to be known before its validation window (section 6).

## 4 Exploratory analysis

Exploration used development orders only, before each task's test period, so it never saw a test outcome. Each fact below led to a decision in the design; the table at the end lists them side by side. Patterns are described, not explained: the data does not record why a route is slow or why a customer is unhappy.

**Lead time is right-skewed.** Half of the orders arrive within 11.2 days, but a long tail of very late orders pulls the mean above the median: median 11.2 days, mean 13.4, 95th percentile 31.1, skewness 2.41. A model fitted on raw days would chase the tail, so the regression predicts the log of 1 plus the lead time, and day-count inputs are log-transformed the same way.

&#91;image: Lead-time distribution, development orders (Pipeline A EDA)\]

*Figure 1. Lead-time distribution, development orders (F.A3.reg.target\_kde).*

**Late delivery and bad reviews go together.** Among orders delivered after Olist's promised date, the detractor rate is 57.2%; among orders delivered on time it is 9.5%. Lateness is known only after delivery, so it is never a predictor. But it explains why an alert made at checkout has little to work with, and why the improved pipeline waits for carrier handover, when the seller's part of any delay is already known.

**Speed depends on the route.** Median lead time ranges from 7.8 days for customers in SP to 27.1 days in AM, and the share of late handovers differs between seller states and routes. A single distance number does not capture this, which motivated the route feature and the route's recent speed.

&#91;image: Late handover by route (B2)\]

*Figure 2. Late handover by route (F.reg.lateness\_by\_route).*

**The business changes over time.** Order volume, lead time, the late-delivery rate and the detractor rate all move across 2017 and 2018. November 2017, with Black Friday, had 7,284 orders against 4,478 in October, and delivery slowed in the weeks after. A model evaluated on a random split would mix these periods; every evaluation here is time-ordered instead.

&#91;image: Monthly orders and outcomes, development orders (Pipeline A EDA)\]

*Figure 3. Monthly orders and lead time, development orders (F.A3.reg.outcome\_trends).*

&#91;image: Monthly detractor rate, development orders (Pipeline A EDA)\]

*Figure 4. Monthly detractor rate, development orders (F.A3.clf.outcome\_trends).*

**Detractors are a minority.** 14.8% of development orders are detractors (on the improved pipeline's test orders, 9.9%), so a model that never alerts would look accurate. We report average precision against the detractor share and set the alert threshold from error costs.

**Predictors overlap little.** A first look at pairwise correlations among the numeric predictors found one identical pair and no other pair above the cut-off; section 5.3 checks this formally with the variance inflation factor.

**The newest weeks may be incomplete.** The data ends in late 2018. The slowest deliveries for orders placed in the final weeks may not have arrived when the data was extracted, so the test period, the newest fifth of orders, may under-represent very late deliveries and make its error look slightly better (section 10).

| What the data shows | Decision it led to | Section |
| --- | --- | --- |
| Right-skewed lead time with a long late tail | Log target and log day counts; keep the tail | 3 |
| Late delivery and bad reviews go together | Alert at carrier handover; lateness never a predictor | 1, 6 |
| Speed differs by route and state | Route feature and recent route speed; seven-state scope | 5, 6 |
| Volumes and outcomes change over time | Time-ordered folds and test period | 6 |
| Detractors are a minority | Average precision; cost-based threshold; class weight in the grid | 1, 6 |
| One identical predictor pair | Dropped before selection | 5 |

## 5 Features, multicollinearity and selection

Every feature has a definition, a time window and a reason. Correlated and nested features are removed by a stated rule before selection, and a ranking rule then keeps the smallest set that carries 99% of the ranked signal. Both steps run on development orders only, never on the test period.

### 5.1 The baseline's predictor pool

The baseline pipeline starts from 24 predictors that are all known at checkout, grouped as follows:

- **Basket:** counts of items, products, sellers and categories.
- **Price and freight:** total price, total freight and the freight-to-price ratio.
- **Physical size:** total weight and volume, with the share of items whose size is missing.
- **Product:** the primary category, with the share of items whose category is missing.
- **Geography:** customer state, primary seller state, the largest seller-to-customer distance with the share of items whose distance is missing, and the share of items shipped across a state border.
- **Calendar:** purchase month, day of week and hour.
- **Payment:** main payment type, largest number of instalments and number of payment methods.

The alert adds three candidates kept after the exploratory screening: the primary product's photo count and description length, and the seller's average review score on earlier orders. Skewed money, size, distance and day-count features are log-transformed, as described in section 3.

### 5.2 The improved pipeline's new features

The new features describe how this seller and this route have delivered recently, measured only on other orders. None uses Olist's estimated delivery date, so none inherits the old promise.

| Feature | Definition | Window | Reason |
| --- | --- | --- | --- |
| Route (seller state → customer state) | The pair of states the parcel travels between | — | Delivery time differs by origin and destination in ways distance alone misses |
| Seller prior late-handover rate | Share of the seller's earlier handovers made after their shipping limit | All complete weeks before the prediction week | A seller that dispatched late before is likely to do so again |
| Seller prior late-handover days | Mean days by which those earlier handovers missed the limit (0 if on time) | As above | The size of past delays, not only their frequency |
| Seller prior dispatch days | Mean days from purchase to handover over the seller's earlier orders | As above | Packing speed is part of every lead time |
| Route recent delivery days | Typical purchase-to-delivery time on the route | Weighted mean of the last three complete weeks (0.5, 0.3, 0.2) | Recent delivery conditions on the route |
| Route recent carrier transit days | Typical handover-to-delivery time on the route | As above | The carrier's part of the lead time, with the seller's delay removed |
| This order's handover lateness (alert only) | Whether, and by how many days, this order's handover missed its shipping limit | At handover | A late dispatch is new information about the coming delivery and review |
| This order's dispatch days (alert only) | Days from purchase to this order's handover | At handover | How long the customer has already waited |

A seller with no earlier handovers takes the recent mean of sellers in the same state. A route with fewer than ten deliveries in the last three weeks takes a blend of its seller state's and customer state's recent means, and then the overall mean. Most rows soon have their own seller and route history (figure below), which is why the first six weeks are used as a warm-up and not modelled.

&#91;image: Share of rows with their own seller and route history, by quarter\]

*Figure 5. Share of rows with their own seller and route history, by quarter (F.reg.history\_coverage).*

**Grounding.** Studies of e-commerce platforms examine how logistics performance relates to customer ratings and purchasing (Deshpande and Pendem, 2023); we cite this for the question it studies, not for any effect size. Our seller features measure the logistics performance of the seller who ships the order. For the route features we found no audited source, so their use rests on an operational assumption: a route that was slow last week is likely to be slow this week. Section 7 tests that assumption against the data instead of taking it for granted.

### 5.3 Multicollinearity check

Strongly correlated predictors make linear coefficients unstable and split importance between partners, even when accuracy is unaffected. The check uses only stored outputs:

- **Baseline pool.** The exploratory stage computed pairwise correlations and a variance inflation factor (VIF) for each numeric predictor on development orders. A pair is flagged above an absolute correlation of 0.9, and a predictor above a VIF of 10. No predictor reached the VIF cut-off in either task (appendix J). One pair was identical on every development order, the missing-weight and missing-volume shares; the lower-ranked of the two was dropped.

| feature\_a | feature\_b | pearson | spearman | identical |
| --- | --- | --- | --- | --- |
| weight\_missing\_fraction | volume\_missing\_fraction | 1 | 1 | True |

&#91;image: Pairwise correlations of A's numeric predictors (Pipeline A EDA)\]

*Figure 6. Pairwise correlations of the baseline's numeric predictors (F.A3.reg.correlation\_heatmap).*

- **Improved pipeline.** The route determines both the customer state and the seller state: every route level fixes both, so their one-hot columns are sums of the route's columns. Keeping all three would make the linear design matrix rank-deficient, so the two state columns are dropped whenever the route is kept. The same step drops the missing-distance share, which is constant because every kept order has a distance, and the duplicate pair found in the baseline pool.

| feature | flagged\_by | paired\_with |
| --- | --- | --- |
| customer\_state | nested in route (B-G-02) | route\_seller\_to\_customer\_state |
| primary\_seller\_state | nested in route (B-G-02) | route\_seller\_to\_customer\_state |
| distance\_missing\_fraction | constant |  |
| weight\_missing\_fraction | duplicate | volume\_missing\_fraction |

- **Every fold.** After the drops, the linear design matrix is full rank in every training fold, so plain least squares and unpenalised logistic regression have unique coefficients. The condition number shows how close the columns come to collinearity (appendix C).
- **What was not measured.** Correlation and VIF were not computed for the new history features. They are averages of related quantities (for example, a seller's late-handover rate and late days), so some correlation among them is likely. The full-rank check rules out exact dependence but not strong correlation, and the stored outputs cannot show more. We state this as a limit (section 10) rather than run new analysis.

### 5.4 Feature selection

Selection ranks each candidate by its association with the target on development orders: the absolute Spearman correlation for lead time and mutual information for the alert. It then keeps features in rank order until they reach 99% of the cumulative score.

&#91;image: Feature ranking and the 99% rule, regression\]

*Figure 7. Feature ranking and the 99% rule, lead time (F.reg.selection).*

&#91;image: Feature ranking and the 99% rule, detractor alert\]

*Figure 8. Feature ranking and the 99% rule, detractor alert (F.clf.selection).*

Ranking once on all development orders is a design choice, and it makes the validation scores slightly optimistic, because the folds' validation orders helped choose the features; the test period is unaffected. To check how much the choice depends on the rows, the ranking was repeated inside each training fold.

- **Lead time:** the selected sets overlap by 0.90 to 1.00 (mean 0.94), and 17 of the 21 selected features are kept in every fold.
- **Detractor alert:** overlap 0.68 to 1.00 (mean 0.88), weakest in fold 1, which has the fewest training orders; 18 of 25 are kept in every fold.

For lead time the ranking is stable: the route and its recent speed, distance and the interstate share stay at the top in every fold. For the alert the ranks move a lot between folds, even for features ranked near the top on all development orders, and several of them drop out of one fold's selection; the early folds, with the fewest training orders, move most. A likely reason, not tested here, is that mutual information estimated on a minority-class target varies more on small samples. The selected set for the alert should therefore be read as a reasonable choice, not a uniquely determined one (section 10).

&#91;image: Delivery lead time: feature ranking on all development rows vs each training fold\]

*Figure 9. Ranking stability across the five folds, lead time (F.reg.ranking\_stability).*

&#91;image: Detractor alert: feature ranking on all development rows vs each training fold\]

*Figure 10. Ranking stability across the five folds, detractor alert (F.clf.ranking\_stability).*

Every new feature passed the cut in both tasks where it applies. The full list of selected features, with transforms and ranks, is in appendix D, beside the baseline's, so the two pipelines can be compared feature by feature.

## 6 Modelling and the A-to-B decision

Models are compared from the simplest upwards, on the same time-ordered folds, under rules fixed before any test order was read. We first built a complete baseline (Pipeline A), then one focused improvement (Pipeline B) that changes only what the baseline's evidence pointed to; both were frozen and scored once on the test together.

### 6.1 Validation design

Orders are dated and customers return, so a random or stratified split would train on orders placed after the ones it predicts, and could put one customer on both sides (Kapoor and Narayanan, 2023). We therefore use five chronological, expanding folds before the test period: each fold trains on all orders up to a date and validates on the following weeks. Customers seen in a validation window are removed from its training rows, and a training order counts only if its label (delivery or review) was known before the validation window starts.

&#91;image: Time-ordered folds and the test period\]

*Figure 11. Time-ordered folds and the test period (F.reg.partition).*

| fold | train\_first | train\_last | train\_rows | validation\_first | validation\_last | validation\_rows |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 2017-02-12 00:20:45 | 2017-06-15 17:52:57 | 7932 | 2017-06-19 15:25:29 | 2017-09-27 08:48:59 | 10323 |
| 2 | 2017-02-12 00:20:45 | 2017-09-25 12:23:20 | 18077 | 2017-09-27 08:56:52 | 2017-12-03 17:04:39 | 10364 |
| 3 | 2017-02-12 00:20:45 | 2017-12-01 08:49:02 | 26184 | 2017-12-03 17:11:47 | 2018-02-05 00:05:58 | 10443 |
| 4 | 2017-02-12 00:20:45 | 2018-02-02 15:26:38 | 37647 | 2018-02-05 00:06:00 | 2018-04-01 16:46:20 | 10429 |
| 5 | 2017-02-12 00:20:45 | 2018-03-29 01:12:21 | 47415 | 2018-04-01 16:53:25 | 2018-05-24 18:56:59 | 9059 |

Each fold must have at least 10,000 training orders and, for the alert, 100 detractors in each part; the minimums were set before the folds were built. Fold 1 of the improved pipeline falls short on training orders (7,932 for lead time, 7,592 for the alert), because the seven-state scope and the warm-up remove early orders. We kept it, as a recorded deviation, so the two pipelines are compared on identical periods; every detractor minimum is met. Instead of stratifying, each fold's detractor share is reported, and it moves with the business over time (appendix A).

### 6.2 Model ladder

We use two model families, linear and tree-based, each started from its simplest form (James et al., 2023): a dummy that predicts the median lead time or the detractor share; plain linear regression or unpenalised logistic regression; a single decision tree; and a random forest of 200 trees (Breiman, 2001). Tree ensembles are the natural non-linear comparison for tabular data of this kind (Grinsztajn et al., 2022). Plain least squares and unpenalised logistic regression need a full-rank design matrix, which section 5.3 shows holds in every fold. Stacking (Wolpert, 1992) and gradient boosting (Chen and Guestrin, 2016) were considered but not added: the project limits the number of model families, and the forest itself did not clear the selection rule.

Each step up the ladder must beat the step below it on the same folds. The table gives the mean gain over the five folds, its paired standard error and the number of folds in which the more complex model wins (MAE in days, a positive gain means lower error; AP for the alert).

&#91;image: Model ladder on the five folds, lead time\]

*Figure 12. Model ladder on the five folds, lead time (F.reg.family\_ladder).*

&#91;image: Model ladder on the five folds, detractor alert\]

*Figure 13. Model ladder on the five folds, detractor alert (F.clf.family\_ladder).*

Lead time:

| comparison | mean\_gain | paired\_se | folds\_better | kept\_by\_one\_se\_rule |
| --- | --- | --- | --- | --- |
| linear/logistic vs dummy | 0.9442 | 0.1606 | 5 | True |
| single tree vs linear/logistic | -0.02855 | 0.1027 | 2 | False |
| forest vs linear/logistic | 0.06193 | 0.0677 | 3 | False |

Detractor alert:

| comparison | mean\_gain | paired\_se | folds\_better | kept\_by\_one\_se\_rule |
| --- | --- | --- | --- | --- |
| linear/logistic vs dummy | 0.1236 | 0.01742 | 5 | True |
| single tree vs linear/logistic | -0.02217 | 0.005108 | 0 | False |
| forest vs linear/logistic | 0.01232 | 0.005154 | 4 | False |

The linear and logistic models beat the dummy in every fold. The single tree is worse than the linear model in both tasks. The forest is slightly better on average, more consistently so for the alert.

### 6.3 Tuning

Each family was then tuned on the same folds, with grids fixed before any tuning result was seen: Ridge alpha and logistic C from 0.01 to 100; tree depth 4 to 18 and minimum leaf size 20 to 200; forest depth 8 to 18 and leaf size 20 to 200 with square-root feature sampling; and class weight (none or balanced) for every classifier (appendix F). Class weighting is how the grid treats the imbalance. We did not resample: the alert uses calibrated probabilities and a cost-based threshold, and in logistic risk models imbalance corrections can distort the calibration of the predicted risk (Van den Goorbergh et al., 2022; He and Garcia, 2009).

Lead time:

| family | plain\_mean | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | paired\_se | carried |
| --- | --- | --- | --- | --- | --- | --- |
| linear/logistic | 5.025 | 5.021 | 0.5946 | 0.00412 | 0.02701 | plain |
| single tree | 5.053 | 5.084 | 0.6443 | -0.03087 | 0.02687 | plain |
| forest | 4.963 | 5.082 | 0.649 | -0.1193 | 0.02599 | plain |

Detractor alert:

| family | plain\_mean | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | paired\_se | carried |
| --- | --- | --- | --- | --- | --- | --- |
| linear/logistic | 0.2616 | 0.2734 | 0.03179 | 0.0118 | 0.005107 | plain |
| single tree | 0.2394 | 0.2298 | 0.02967 | -0.009644 | 0.007588 | plain |
| forest | 0.2739 | 0.2625 | 0.02971 | -0.01144 | 0.002612 | plain |

Tuning changed little: no tuned configuration beat its plain model by enough to be carried forward. The forest's best configuration sits at the edge of its grid in both tasks: the smallest leaf size, with the deepest trees for lead time and the shallowest for the alert. A best value on the boundary means a wider grid might do better. The grid was fixed in advance and was not extended, because the selection rule below keeps the plain model either way; extending it after the test would mean choosing on the test (section 10).

### 6.4 Selection, calibration and threshold

**The one-standard-error rule.** Among the finalists, we keep the simplest model whose mean validation score is within one standard error of the best mean, where the standard error measures how much the score varies from fold to fold. The forest had the best mean in both tasks, but within one standard error of the plain model, so the plain linear model (lead time) and the plain logistic model (alert) were selected. This is a deliberate preference for simplicity, and it should be read with the paired results above: for the alert the forest beats the logistic model in four of five folds, by more than its paired standard error, but by much less than the fold-to-fold variation that the rule uses. The rule was fixed before training, and the simpler model is easier to explain, calibrate and serve.

**Calibration.** The alert's probabilities are calibrated with a sigmoid fitted on time-ordered inner splits, so that both pipelines share one probability scale for thresholds and costs. The pre-set rule would have kept the raw probabilities, which had a slightly better Brier score; we kept the sigmoid for comparability and record it as a deviation (section 10).

**Threshold.** With a missed detractor weighted as five false alerts, an alert pays off when the predicted risk exceeds 1/6, and that is the frozen threshold. After the test, the business chose a higher operating threshold for the improved pipeline, 4/15, to cut false alarms; the frozen 1/6 result stays the unbiased test result (section 7).

### 6.5 Why A became B

The baseline was complete and sound, and its own evidence showed where it could not go further:

| What the baseline's evidence showed | Change in the improved pipeline | How it was checked before the test |
| --- | --- | --- |
| The strongest driver of a bad review, late delivery (57.2% detractors when late against 9.5% on time), is unknown at checkout | The alert moves to carrier handover, where this order's dispatch delay is known; orders never handed over are flagged by a rule | Validation AP on the same rows (below) |
| Delivery speed varies with the route and changes over time (section 4), but checkout features carry no recent seller or route behaviour | Seller and route history features (section 5.2) | Ranking and selection (section 5.4); validation scores |
| Distant, thinly served states add noise that a single model fits poorly | Scope narrowed to the seven largest states with known distance; the baseline serves every other order | The scope effect is measured separately (section 7) |

The baseline's validation results set the bar: MAE 5.47 days against 6.49 for its dummy, and AP 0.232 against 0.148.

**The adoption rule, fixed before the test.** The improved pipeline is adopted for a task if, on its own validation rows, its five-fold mean beats the baseline's frozen model refitted on the same folds, even by a small margin. It did, in every fold of both tasks:

Lead time (MAE in days):

| fold | b\_rows | a\_model\_on\_b\_rows | b\_model\_on\_b\_rows | paired\_gain\_b\_over\_a |
| --- | --- | --- | --- | --- |
| 1 | 10323 | 3.724 | 3.722 | 0.001477 |
| 2 | 10364 | 5.516 | 5.468 | 0.04797 |
| 3 | 10443 | 5.755 | 5.614 | 0.1411 |
| 4 | 10429 | 7.11 | 6.772 | 0.3375 |
| 5 | 9059 | 3.607 | 3.547 | 0.06012 |

Detractor alert (AP):

| fold | b\_rows | a\_model\_on\_b\_rows | b\_model\_on\_b\_rows | paired\_gain\_b\_over\_a |
| --- | --- | --- | --- | --- |
| 1 | 10324 | 0.1407 | 0.1566 | 0.01585 |
| 2 | 10342 | 0.2386 | 0.2738 | 0.03512 |
| 3 | 10450 | 0.25 | 0.2762 | 0.02618 |
| 4 | 10453 | 0.3563 | 0.3713 | 0.01497 |
| 5 | 8646 | 0.2237 | 0.2301 | 0.006408 |

Both pipelines then went to the single test read regardless of this result, and the test did not re-choose any model, calibration or threshold. Everything else was inherited unchanged from the baseline: the folds, the model families and grids, the selection rule, the metrics and the calibration and threshold procedure.

## 7 Results

On the same test orders the improved pipeline beats the baseline in both tasks. Validation scores were used to choose the models, so they are optimistic selection scores; only the test, read once, is an unbiased estimate. Fold-by-fold validation results and the test are shown together, each with its time window, because each fold is itself a later period that the model had not seen.

### 7.1 Delivery lead time

|  | Validation MAE (selection) | Test MAE \[95% interval\] | Within 3 days (test) |
| --- | --- | --- | --- |
| Improved pipeline (delivered) | 5.02 | 3.30 \[3.24, 3.35\] | 57.6% |
| Baseline on the same test orders |  | 4.03 | 44.3% |
| Dummy (median) on the same test orders |  | 4.38 |  |

The improved pipeline's MAE minus the baseline's is -0.729 days on the same 15,422 test orders (paired bootstrap interval -0.754 to -0.703), so the gain is not an accident of the sample.

&#91;image: Delivery lead time: validation folds (selection scores) and the test, A and B\]

*Figure 14. Lead time by validation fold and on the test, with time windows (F.reg.validation\_and\_test).*

**Residuals, read honestly.** On validation the errors lean late: the average order arrives +2.9 days after the prediction, with a long right tail. On the test they lean early: mean -1.1 days, median -1.6, because the test period was faster than the development period (section 7.4). The residuals are therefore neither centred on zero nor constant in spread, and a promise built on the prediction needs a buffer chosen for the current period (section 9). 11.1% of test orders arrive more than 3 days after the prediction (9.3% for the baseline) and 4.7% more than 6 days after.

&#91;image: Residuals on B's test rows: B vs A\]

*Figure 15. Residuals on the test orders, improved pipeline and baseline (F.reg.residuals).*

**Where it errs.** Slices are judged only with at least 100 test orders. The improved pipeline is better than the baseline in every judged customer state, distance band and basket size, on 20 of the 20 routes with enough orders, and in most months:

| slice | judged\_slices | too\_few | pooled\_mae\_A | pooled\_mae\_B | mean\_gain | sd\_gain | slices\_B\_better |
| --- | --- | --- | --- | --- | --- | --- | --- |
| customer\_state | 7 | 0 | 4.028 | 3.299 | -0.9297 | 0.275 | 7 |
| route\_seller\_to\_customer\_state | 20 | 28 | 3.97 | 3.233 | -0.8155 | 0.3866 | 20 |
| distance\_band | 5 | 0 | 4.028 | 3.299 | -0.7444 | 0.3128 | 5 |
| basket | 3 | 0 | 4.028 | 3.299 | -0.6387 | 0.0949 | 3 |
| month | 4 | 0 | 4.028 | 3.299 | -0.5456 | 0.5487 | 3 |

&#91;image: Lead-time error by customer state\]

*Figure 16. Lead-time error by customer state (F.reg.by\_state).*

### 7.2 Detractor alert

|  | Validation AP (selection) | Test AP \[95% interval\] | Test ROC-AUC | Test Brier |
| --- | --- | --- | --- | --- |
| Improved pipeline (at handover) | 0.248 | 0.197 \[0.181, 0.218\] | 0.636 | 0.0867 |
| Baseline on the same test orders (at checkout) |  | 0.178 | 0.604 | 0.0893 |

The improved pipeline ranks detractors better by +0.0187 AP (paired interval +0.0089 to +0.0291) on 15,492 test orders with 1,541 detractors, and is better on ROC-AUC and on the Brier score, which measures how well calibrated the probabilities are. The two pipelines predict at different moments, so part of the gain is the later moment itself.

&#91;image: Detractor alert: validation folds (selection scores) and the test, A and B\]

*Figure 17. Detractor alert: validation folds (selection scores) and the test, A and B (F.clf.validation\_and\_test).*

&#91;image: PR, ROC and reliability curves on B's test rows\]

*Figure 18. PR, ROC and reliability curves on the improved pipeline's test rows (F.clf.test\_curves).*

**At the threshold.** At the frozen 1/6, the unbiased result, the improved pipeline sends 23.2 alerts a day on the test with precision 0.208 and recall 0.300. After the test the business moved its operating threshold to 4/15 to cut false alarms, a post-test change reported beside the frozen result: 5.6 alerts a day, precision 0.346, recall 0.121. Orders outside the seven states are alerted by the baseline at its frozen 1/6 (section 9).

&#91;image: Precision, recall and alerts per day against the threshold\]

*Figure 19. Precision, recall and alerts per day against the threshold, marking 1/6 and 4/15 (F.clf.threshold\_options).*

**Slices.** Precision and recall by customer state and route are judged only where the test has more than 100 detractors, which holds for few slices (appendix E). In every judged slice the improved pipeline is more precise; the baseline, which alerts more orders, has the higher recall in most of them.

&#91;image: Detractor alert precision and recall by customer state\]

*Figure 20. Detractor alert by customer state (F.clf.by\_state).*

**Label choice.** Scored against the first review instead of the lowest, both pipelines' results change only in the fourth decimal (section 3), so the label rule does not drive the comparison.

### 7.3 Where the gain comes from

The improved pipeline changed three things at once: the scope, the features and, for the alert, the prediction moment. Scoring the baseline's frozen model on the improved pipeline's own validation rows separates the scope effect from the rest (five-fold means):

|  | Baseline, all states | Baseline, seven-state rows | Improved, seven-state rows |
| --- | --- | --- | --- |
| Lead time, MAE (days) | 5.470 | 5.142 | 5.025 |
| Detractor alert, AP | 0.244 | 0.242 | 0.262 |

For lead time most of the lower error comes from the narrower scope, because the baseline is already better on the seven-state rows, and the rest from the new features. For the alert the scope changes almost nothing, so the gain comes from the history features and the later prediction moment.

&#91;image: Where B's gain comes from: scope vs features\]

*Figure 21. Where the lead-time gain comes from: scope and features (F.reg.population).*

&#91;image: ROC-AUC and Brier by population, detractor alert\]

*Figure 22. ROC-AUC and Brier score by population, detractor alert (F.clf.auc\_brier).*

### 7.4 What drives the predictions, and drift

Permutation importance measures how much each feature contributes to the frozen model on the test orders: the score lost when the feature is shuffled. For lead time the seller's earlier dispatch days, the route and the distance rank highest, so the seller's own delay matters at least as much as the journey. For the alert, the number of sellers in the order and the route's recent delivery and transit times rank above this order's handover delay, so route conditions and basket complexity carry more signal about a bad review than the dispatch delay alone. These are associations in the frozen model, not causes.

&#91;image: Permutation importance, B regression (test rows)\]

*Figure 23. Permutation importance on the test rows, lead time (F.reg.importance).*

&#91;image: Permutation importance, B classification (test rows)\]

*Figure 24. Permutation importance on the test rows, detractor alert (F.clf.importance).*

This ranking differs from the selection ranking of section 5.4: Spearman correlation 0.16 for lead time and 0.31 for the alert, with 7 and 6 of the top ten features shared. The difference is expected: selection scored one feature at a time on development orders, whereas importance measures each feature inside the fitted model on the test period, where correlated features share credit.

&#91;image: B's regression coefficients\]

*Figure 25. Linear regression coefficients, lead time (F.reg.coefficients).*

&#91;image: B's classification odds ratios\]

*Figure 26. Logistic regression odds ratios, detractor alert (F.clf.coefficients).*

The test period differs from development: deliveries were faster and reviews happier, and the route history features shifted most. Validation and test scores therefore describe different periods, and the test gain partly reflects that the history features track the faster period as it happens.

&#91;image: Drift by fold, regression\]

*Figure 27. Drift between development and test, by fold (F.reg.drift).*

## 8 Deployment and dashboard

The released models predict exactly what was tested, and the dashboard shows only stored results, each labelled with the model that produced it.

**Release package.** For each task, the improved pipeline's frozen model and the baseline's (as fallback) are packaged with their feature schemas, training profiles and checksums. Reloaded from disk, they re-predict the saved test predictions exactly (largest difference 1e-14 for lead time and 2e-16 for the alert), from test rows rebuilt with every label column emptied, so no label is read.

**Serving rule.** A router sends each order to the improved pipeline when its customer and seller are both in the seven states and its distance is known, and to the baseline otherwise (15,570 and 3,396 of the alert's test orders). Every prediction carries a badge naming the model and, outside the seven states, the reason. Inside the seven states, an order not yet handed over gets no alert score; the missed-dispatch rule flags it if its shipping limit passes.

**Input checks.** Unknown states, impossible distances, orders without items and missing instalments are rejected with a clear message. Missing values, unseen categories and numeric inputs more than 4 standard deviations from the training mean are accepted with a warning.

**Dashboard.** A Streamlit app with four tabs: a business overview of all orders (descriptive, labelled as a separate scope from the model results), delivery lead time, detractor risk at handover, and scoring of the alerted held-out orders. The model tabs read only stored outputs and score held-out historical orders. The alert tab's threshold slider moves the improved pipeline's threshold over the stored options (default 4/15) and shows alerts per day, precision, recall and cost; the baseline's fallback stays at its frozen 1/6.

**Using the app.** The app lives in `deliverables/dashboard/app/` with its own environment (Python 3.12 and the package versions pinned in its requirements file, which load the frozen models unchanged). Running `streamlit run app.py` from that folder opens it at `http://localhost:8501`; the README there gives the exact commands. For hosting, the frozen models are served by a small prediction API that returns exactly what the local models return, and the hosted address will be added here once it is live. The sidebar names the stored outputs each tab reads and states that no model is fitted and no test label is read. On the detractor tab, a radio button switches the alert statistics between validation (the selection view) and the test (a post-test view), and the slider moves the improved pipeline's threshold, starting at 4/15. A fourth tab, Score an order, lists the held-out orders the serving rule alerts on, in the review order of section 9, with each order's details as known at handover, both predictions and two kinds of scenario on the alert model's inputs (logistics 10% faster; freight discounts up to free shipping), each labelled as an association, not the effect of the action. The app's tests check the file loaders and the router, that every slider position is a stored threshold, that the forbidden scope and threshold wording is absent, that every planned panel is present, and that the alert list and its scores match the stored test predictions without reading a label.

## 9 Business recommendations

Three actions follow from the results; each is labelled as an observation (measured here), a literature-supported hypothesis or an unmeasured mechanism, and the dashboard shows the detail behind each.

| Action | What the evidence shows | Label | Dashboard |
| --- | --- | --- | --- |
| Promise a range, not a date | On validation, a buffer of 12.0 days puts 90% of orders on time and 17.5 days 95%; on the faster test period those buffers leave 1.5% and 0.7% late. Choose the buffer on recent weeks and watch the late share by state. Overly optimistic promises carry costs after the sale (Cui et al., 2024) | Observation; literature-supported hypothesis for the cost of over-promising | Lead time, promise buffer |
| Alert customer service at handover | The improved pipeline at 4/15 sends 5.6 alerts a day at precision 0.346; with the baseline's fallback at 1/6 the total is 20.5 a day at precision 0.192 | Observation | Detractor risk, alert statistics |
| Flag missed dispatch with a rule | Orders whose shipping limit passes without handover are detractors with precision 21.2%, and the rule catches 16.8% of all detractors on the test period, with no model | Observation | Detractor risk, missed dispatch |

&#91;image: Promise buffer: share of orders delivered later than prediction plus buffer; buffer chosen on validation, read on the test\]

*Figure 28. Share of orders late against buffer size, validation and test (F.reg.buffer\_curve).*

**Cost.** Weighting a missed detractor as five false alerts, the serving rule's test cost is 9,211 (7,123 from the improved pipeline and 2,088 from the fallback). The weighting is an assumption; the dashboard shows the trade-off at other thresholds.

**Review order when capacity is short.** The improved pipeline's alerts at 4/15 are reviewed first (5.6 a day at precision 0.346). The baseline fallback's alerts outside the seven states come next (14.9 a day at precision 0.133). The review cap of 6 alerts a day asked for at the model review applies to the improved pipeline alone; with the fallback the combined volume is higher, which the team accepted. The fallback scores at checkout, but its alerts are reviewed at carrier handover, like the improved pipeline's, so each order's handover delay is known by then. Within the fallback, orders are reviewed by handover delay, longest first, with order value as the tie-break; an order not handed over by its shipping limit is flagged by the missed-dispatch rule. This order is an operational rule, not a measured result: the precisions above are measured for each stream, and no stored output evaluates the ordering inside the fallback.

**Slow sellers and routes.** The seller's earlier dispatch delay and the route's recent speed are among the strongest predictors (section 7.4). That slower logistics goes with worse ratings is a literature-supported hypothesis (Deshpande and Pendem, 2023); that working on these sellers and routes would improve reviews is an unmeasured mechanism, because nothing here tests an intervention. The dashboard ranks routes and categories by observed outcomes for each quarter so operations can choose where to look first.

## 10 Limitations

All limitations are collected here. All validation in this project uses time-ordered, customer-purged folds, and the test period was read once; the limits below are what remains.

| Limit | What it means | How it is handled |
| --- | --- | --- |
| Seven-state scope | The improved pipeline covers only orders whose customer and seller are in the seven states with a known distance | The baseline's frozen model serves every other order, and each prediction shows which model made it |
| Different prediction moments | The improved alert acts at handover, the baseline's at checkout, so part of the gain is the later moment | Stated wherever the two are compared (section 7) |
| Post-test threshold | The operating threshold 4/15 was chosen after the test was read | The frozen 1/6 result is reported as the unbiased one |
| Calibration override | The pre-set rule would have kept raw probabilities; sigmoid calibration was kept so both pipelines share one scale | Recorded as a deviation (section 6.4) |
| Screening on pooled rows | Features were ranked once on all development orders, so validation scores are slightly optimistic | Ranking stability by fold is reported (section 5.4); the test is unaffected |
| Unstable alert ranking | For the alert, feature ranks move a lot between folds, most in the early folds | The selected set is read as a reasonable choice, not a unique one |
| Unmeasured correlation | Correlation and VIF were not computed for the new history features; full rank rules out only exact dependence | Coefficients of related history features are read with care |
| Grid edge | The forest's best configuration sits on the edge of its grid | The grid was fixed in advance and not extended after the test; the plain model is kept by the selection rule |
| Fold 1 below minimum | The improved pipeline's first fold has fewer training orders than the pre-set minimum | Kept so both pipelines are compared on identical periods |
| Drift | The test period was faster and happier than development, and the route history features shifted most | Validation and test are reported separately; the promise buffer should be set on recent weeks |
| Latest deliveries possibly missing | The slowest deliveries for the newest orders may not have arrived when the data was extracted | The test error may look slightly better than it will in operation |
| Reproducibility | The frozen models' predictions reproduce exactly on another machine; refitting gives slightly different numbers across machines | Reproduction compares predictions exactly and refitted scores within a tolerance |
| Associations, not causes | Features describe association with the outcome, not the effect of acting on them | Recommendations are labelled by evidence type (section 9) |

**Next steps.** Deploy the app; monitor alert precision and late deliveries by state each month; set the promise buffer on recent weeks; and test the handover alert with customer service before scaling it.

## References

Breiman, L. (2001). Random Forests. *Machine Learning*, 45, 5–32. https://doi.org/10.1023/A:1010933404324

Chen, T., & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 785–794. https://doi.org/10.1145/2939672.2939785

Cui, R., Lu, Z., Sun, T., & Golden, J. M. (2024). Sooner or Later? Promising Delivery Speed in Online Retail. *Manufacturing & Service Operations Management*, 26(1), 233–251. https://doi.org/10.1287/msom.2021.0174

Deshpande, V., & Pendem, P. K. (2023). Logistics Performance, Ratings, and Its Impact on Customer Purchasing Behavior and Sales in E-Commerce Platforms. *Manufacturing & Service Operations Management*, 25(3), 827–845. https://doi.org/10.1287/msom.2021.1045

Grinsztajn, L., Oyallon, E., & Varoquaux, G. (2022). Why Do Tree-Based Models Still Outperform Deep Learning on Typical Tabular Data? *Advances in Neural Information Processing Systems*, 35 (Datasets and Benchmarks Track). https://proceedings.neurips.cc/paper\_files/paper/2022/file/0378c7692da36807bdec87ab043cdadc-Paper-Datasets\_and\_Benchmarks.pdf

He, H., & Garcia, E. A. (2009). Learning from Imbalanced Data. *IEEE Transactions on Knowledge and Data Engineering*, 21(9), 1263–1284. https://doi.org/10.1109/TKDE.2008.239

James, G., Witten, D., Hastie, T., Tibshirani, R., & Taylor, J. (2023). *An Introduction to Statistical Learning: with Applications in Python*. Springer. https://doi.org/10.1007/978-3-031-38747-0

Kapoor, S., & Narayanan, A. (2023). Leakage and the Reproducibility Crisis in Machine-Learning-Based Science. *Patterns*, 4(9), 100804. https://doi.org/10.1016/j.patter.2023.100804

Müller, A. C., & Guido, S. (2016). *Introduction to Machine Learning with Python: A Guide for Data Scientists*. O'Reilly. https://www.oreilly.com/library/view/introduction-to-machine/9781449369880/

van den Goorbergh, R., van Smeden, M., Timmerman, D., & Van Calster, B. (2022). The Harm of Class Imbalance Corrections for Risk Prediction Models: Illustration and Simulation Using Logistic Regression. *Journal of the American Medical Informatics Association*, 29(9), 1525–1534. https://doi.org/10.1093/jamia/ocac093

Wolpert, D. H. (1992). Stacked Generalization. *Neural Networks*, 5(2), 241–259. https://doi.org/10.1016/S0893-6080(05)80023-1

**Data.** Olist Brazilian E-Commerce Public Dataset, the Canvas copy provided for the course (originally published on Kaggle).

## Appendices

### A. Validation and test windows

Validation folds are selection scores; the test was read once.

| period | kind | start | end | festival\_days |
| --- | --- | --- | --- | --- |
| fold 1 | validation (selection score, G-10) | 2017-06-19 | 2017-09-27 |  |
| fold 2 | validation (selection score, G-10) | 2017-09-27 | 2017-12-03 | 2017-11-24 |
| fold 3 | validation (selection score, G-10) | 2017-12-03 | 2018-02-05 | 2017-12-25 |
| fold 4 | validation (selection score, G-10) | 2018-02-05 | 2018-04-01 |  |
| fold 5 | validation (selection score, G-10) | 2018-04-01 | 2018-05-24 |  |
| test | test (unbiased, read once) | 2018-05-27 | 2018-08-29 |  |

Fold sizes, lead time:

| fold | train\_first | train\_last | train\_rows | validation\_first | validation\_last | validation\_rows |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 2017-02-12 00:20:45 | 2017-06-15 17:52:57 | 7932 | 2017-06-19 15:25:29 | 2017-09-27 08:48:59 | 10323 |
| 2 | 2017-02-12 00:20:45 | 2017-09-25 12:23:20 | 18077 | 2017-09-27 08:56:52 | 2017-12-03 17:04:39 | 10364 |
| 3 | 2017-02-12 00:20:45 | 2017-12-01 08:49:02 | 26184 | 2017-12-03 17:11:47 | 2018-02-05 00:05:58 | 10443 |
| 4 | 2017-02-12 00:20:45 | 2018-02-02 15:26:38 | 37647 | 2018-02-05 00:06:00 | 2018-04-01 16:46:20 | 10429 |
| 5 | 2017-02-12 00:20:45 | 2018-03-29 01:12:21 | 47415 | 2018-04-01 16:53:25 | 2018-05-24 18:56:59 | 9059 |

Fold sizes and class support, detractor alert:

| fold | a\_train\_start | a\_train\_end | a\_validation\_start | a\_validation\_end | train\_rows | train\_first | train\_last | a\_train\_rows | train\_positives | train\_prevalence | validation\_rows | validation\_first | validation\_last | a\_validation\_rows | validation\_positives | validation\_prevalence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2017-01-05 11:56:06 | 2017-06-13 03:24:05 | 2017-06-17 23:50:22 | 2017-09-26 09:23:05 | 7592 | 2017-02-12 00:20:45 | 2017-06-13 03:24:05 | 11077 | 874 | 0.1151 | 10324 | 2017-06-17 23:50:22 | 2017-09-26 09:10:27 | 12956 | 1014 | 0.09822 |
| 2 | 2017-01-05 11:56:06 | 2017-09-21 09:04:59 | 2017-09-26 09:37:01 | 2017-12-02 18:56:39 | 17595 | 2017-02-12 00:20:45 | 2017-09-21 09:04:59 | 23573 | 1872 | 0.1064 | 10342 | 2017-09-26 09:37:01 | 2017-12-02 18:56:39 | 12950 | 1443 | 0.1395 |
| 3 | 2017-01-05 11:56:06 | 2017-11-29 19:35:55 | 2017-12-02 19:00:27 | 2018-02-04 16:04:56 | 25529 | 2017-02-12 00:20:45 | 2017-11-29 19:35:55 | 33568 | 2734 | 0.1071 | 10450 | 2017-12-02 19:00:27 | 2018-02-04 16:04:56 | 12941 | 1497 | 0.1433 |
| 4 | 2017-01-05 11:56:06 | 2018-02-01 13:41:36 | 2018-02-04 16:10:12 | 2018-03-31 20:05:18 | 37140 | 2017-02-12 00:20:45 | 2018-02-01 13:41:36 | 47933 | 4472 | 0.1204 | 10453 | 2018-02-04 16:10:12 | 2018-03-31 20:05:18 | 12925 | 2173 | 0.2079 |
| 5 | 2017-01-05 11:56:06 | 2018-03-28 11:52:01 | 2018-03-31 20:10:17 | 2018-05-23 11:29:51 | 47237 | 2017-02-12 00:20:45 | 2018-03-28 11:52:01 | 60361 | 6363 | 0.1347 | 8646 | 2018-03-31 20:10:17 | 2018-05-23 11:29:51 | 10251 | 873 | 0.101 |

### B. Metric glossary

| Metric | Meaning |
| --- | --- |
| MAE | Mean absolute error of the predicted lead time, in days (primary for lead time; lower is better) |
| RMSE | Root mean squared error in days; penalises large misses more than MAE |
| R² | Share of the variance in lead time explained; can be negative on a shifted period |
| Within 3 days | Share of orders whose prediction is within 3 days of the actual lead time |
| AP | Average precision, the area under the precision–recall curve (primary for the alert) |
| ROC-AUC | Probability that a random detractor scores higher than a random non-detractor |
| Brier | Mean squared error of the predicted probability (calibration and sharpness) |
| Precision, recall | At a threshold: share of alerts that are detractors; share of detractors alerted |
| Paired gain | Per-fold difference between two models on the same rows; its mean and standard error describe the comparison |
| One-SE rule | Keep the simplest model whose fold mean is within one standard error of the best |
| Selection score | A fold score used to choose models; optimistic. Only the test is unbiased |

### C. Full rank of the linear design matrix

Full rank means no column is an exact linear combination of the others, so the coefficients are unique. The number of columns grows by fold because the one-hot step learns its categories from each training fold. The condition number shows how close the columns come to collinearity.

Lead time:

| fold | rows | encoded\_columns | columns | rank | full\_rank | condition\_number |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 7932 | 131 | 130 | 130 | True | 244.7 |
| 2 | 18077 | 139 | 138 | 138 | True | 285.1 |
| 3 | 26184 | 140 | 139 | 139 | True | 243.5 |
| 4 | 37647 | 141 | 140 | 140 | True | 385.8 |
| 5 | 47415 | 141 | 140 | 140 | True | 433.6 |

Detractor alert:

| fold | rows | encoded\_columns | columns | rank | full\_rank | condition\_number |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 7592 | 135 | 134 | 134 | True | 910.1 |
| 2 | 17595 | 143 | 142 | 142 | True | 912.8 |
| 3 | 25529 | 144 | 143 | 143 | True | 834.5 |
| 4 | 37140 | 145 | 144 | 144 | True | 864.5 |
| 5 | 47237 | 145 | 144 | 144 | True | 934.2 |

### D. Selected features

Lead time:

| feature | kind | transform | pool\_rank |
| --- | --- | --- | --- |
| route\_seller\_to\_customer\_state | categorical | categorical: one-hot (drop-first for linear/logistic, every level for trees) | 1 |
| route\_recent\_carrier\_transit\_days | numeric | log1p: day count (Henry) | 2 |
| route\_recent\_delivery\_days | numeric | log1p: day count (Henry) | 3 |
| distance\_km\_max | numeric | log1p because pre-cutoff skewness 1.26 > 1 (A's 4.2 rule on B rows) | 4 |
| interstate\_share | numeric | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) | 5 |
| total\_freight | numeric | log1p because pre-cutoff skewness 9.42 > 1 (A's 4.2 rule on B rows) | 7 |
| seller\_prior\_dispatch\_days | numeric | log1p: day count (Henry) | 8 |
| primary\_category | categorical | categorical: one-hot, never logged (A's 4.2 rule on B rows) | 9 |
| seller\_prior\_late\_handover\_rate | numeric | never logged: rate or flag, scaled only (Henry) | 10 |
| seller\_prior\_late\_handover\_days | numeric | log1p: day count (Henry) | 11 |
| freight\_ratio | numeric | never logged: team decision in the s01 review (G-62) (A's 4.2 rule on B rows) | 12 |
| total\_weight\_g | numeric | log1p because pre-cutoff skewness 6.94 > 1 (A's 4.2 rule on B rows) | 14 |
| total\_price | numeric | log1p because pre-cutoff skewness 11.03 > 1 (A's 4.2 rule on B rows) | 15 |
| primary\_payment\_type | categorical | categorical: one-hot, never logged (A's 4.2 rule on B rows) | 16 |
| total\_volume\_cm3 | numeric | log1p because pre-cutoff skewness 7.63 > 1 (A's 4.2 rule on B rows) | 17 |
| purchase\_dayofweek | numeric | never logged: numeric calendar position (G-22, G-47) (A's 4.2 rule on B rows) | 18 |
| n\_sellers | numeric | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) | 19 |
| purchase\_month | numeric | never logged: numeric calendar position (G-22, G-47) (A's 4.2 rule on B rows) | 20 |
| n\_products | numeric | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) | 21 |
| payment\_installments\_max | numeric | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) | 22 |
| n\_items | numeric | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) | 23 |

Detractor alert:

| feature | kind | transform | pool\_rank |
| --- | --- | --- | --- |
| route\_recent\_carrier\_transit\_days | numeric | log1p: day count (Henry) | 1 |
| route\_recent\_delivery\_days | numeric | log1p: day count (Henry) | 2 |
| seller\_prior\_dispatch\_days | numeric | log1p: day count (Henry) | 3 |
| seller\_prior\_late\_handover\_days | numeric | log1p: day count (Henry) | 4 |
| seller\_prior\_review\_mean | numeric | never logged: 1-5 rating (G-70) (A's 4.2 rule on B rows) | 5 |
| order\_dispatch\_days | numeric | log1p: day count (Henry) | 6 |
| freight\_ratio | numeric | never logged: team decision in the s01 review (G-62) (A's 4.2 rule on B rows) | 7 |
| total\_freight | numeric | log1p because pre-cutoff skewness 9.45 > 1 (A's 4.2 rule on B rows) | 8 |
| total\_volume\_cm3 | numeric | log1p because pre-cutoff skewness 7.65 > 1 (A's 4.2 rule on B rows) | 9 |
| n\_items | numeric | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) | 10 |
| route\_seller\_to\_customer\_state | categorical | categorical: one-hot (drop-first for linear/logistic, every level for trees) | 11 |
| seller\_prior\_late\_handover\_rate | numeric | never logged: rate or flag, scaled only (Henry) | 12 |
| total\_price | numeric | log1p because pre-cutoff skewness 11.11 > 1 (A's 4.2 rule on B rows) | 13 |
| order\_handover\_late\_days | numeric | log1p: day count (Henry) | 14 |
| total\_weight\_g | numeric | log1p because pre-cutoff skewness 6.94 > 1 (A's 4.2 rule on B rows) | 15 |
| product\_description\_lenght | numeric | log1p because pre-cutoff skewness 2.06 > 1 (A's 4.2 rule on B rows) | 16 |
| n\_products | numeric | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) | 18 |
| n\_sellers | numeric | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) | 19 |
| purchase\_month | numeric | never logged: numeric calendar position (G-22, G-47) (A's 4.2 rule on B rows) | 20 |
| order\_handed\_over\_late | numeric | never logged: rate or flag, scaled only (Henry) | 21 |
| distance\_km\_max | numeric | log1p because pre-cutoff skewness 1.26 > 1 (A's 4.2 rule on B rows) | 22 |
| primary\_category | categorical | categorical: one-hot, never logged (A's 4.2 rule on B rows) | 23 |
| interstate\_share | numeric | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) | 24 |
| n\_categories | numeric | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) | 25 |
| payment\_installments\_max | numeric | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) | 26 |

### E. Train, validation and test tables

Lead time:

| model | rows | metric | train\_mean | validation\_mean | validation\_se | test | test\_ci\_low | test\_ci\_high |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B frozen | B test rows | mae | 3.861 | 5.025 | 0.6115 | 3.299 | 3.245 | 3.353 |
| B frozen | B test rows | rmse | 6.044 | 7.837 | 1.108 | 4.775 | 4.593 | 4.951 |
| B frozen | B test rows | r2 | 0.2437 | 0.08733 | 0.05303 | 0.1849 | 0.1616 | 0.2074 |
| B frozen | B test rows | within\_3d | 0.5563 | 0.501 | 0.0269 | 0.5755 | 0.5676 | 0.5838 |
| A frozen | B test rows | mae |  | 5.142 | 0.6616 | 4.028 | 3.97 | 4.083 |
| A frozen | B test rows | rmse |  | 7.99 | 1.187 | 5.359 | 5.197 | 5.511 |
| A frozen | B test rows | r2 |  | 0.05744 | 0.06186 | -0.02651 | -0.06142 | 0.006686 |
| A frozen | B test rows | within\_3d |  | 0.4883 | 0.02646 | 0.4429 | 0.4352 | 0.451 |
| B plain | B test rows | mae | 3.861 | 5.025 | 0.6115 | 3.299 | 3.245 | 3.353 |
| B plain | B test rows | rmse | 6.044 | 7.837 | 1.108 | 4.775 | 4.593 | 4.951 |
| B plain | B test rows | r2 | 0.2437 | 0.08733 | 0.05303 | 0.1849 | 0.1616 | 0.2074 |
| B plain | B test rows | within\_3d | 0.5563 | 0.501 | 0.0269 | 0.5755 | 0.5676 | 0.5838 |
| B dummy | B test rows | mae | 4.794 | 5.969 | 0.7107 | 4.385 | 4.327 | 4.441 |
| B dummy | B test rows | rmse | 7.105 | 8.747 | 1.217 | 5.709 | 5.54 | 5.876 |
| B dummy | B test rows | r2 | -0.04354 | -0.1398 | 0.04139 | -0.1651 | -0.19 | -0.1428 |
| B dummy | B test rows | within\_3d | 0.4394 | 0.3752 | 0.02589 | 0.371 | 0.3636 | 0.3784 |
| A frozen | A test rows | mae | 4.286 | 5.47 | 0.6733 | 4.336 | 4.281 | 4.39 |
| A frozen | A test rows | rmse | 6.882 | 8.578 | 1.179 | 5.729 | 5.594 | 5.875 |
| A frozen | A test rows | r2 | 0.2382 | 0.09112 | 0.07289 | 0.03397 | 0.004485 | 0.05933 |
| A frozen | A test rows | within\_3d | 0.5132 | 0.4654 | 0.02563 | 0.4138 | 0.4066 | 0.4204 |
| A plain | A test rows | mae | 4.286 | 5.47 | 0.6733 | 4.336 | 4.281 | 4.39 |
| A plain | A test rows | rmse | 6.882 | 8.578 | 1.179 | 5.729 | 5.594 | 5.875 |
| A plain | A test rows | r2 | 0.2382 | 0.09112 | 0.07289 | 0.03397 | 0.004485 | 0.05933 |
| A plain | A test rows | within\_3d | 0.5132 | 0.4654 | 0.02563 | 0.4138 | 0.4066 | 0.4204 |
| A dummy | A test rows | mae | 5.312 | 6.495 | 0.6889 | 4.876 | 4.819 | 4.934 |
| A dummy | A test rows | rmse | 8.053 | 9.535 | 1.157 | 6.261 | 6.115 | 6.42 |
| A dummy | A test rows | r2 | -0.04316 | -0.1355 | 0.04145 | -0.154 | -0.1735 | -0.1361 |
| A dummy | A test rows | within\_3d | 0.4001 | 0.339 | 0.02291 | 0.3213 | 0.314 | 0.3283 |

Detractor alert:

| model | rows | metric | validation\_mean | validation\_se | test | test\_ci\_low | test\_ci\_high | test\_detractors |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B frozen | B test rows | ap | 0.2482 | 0.03126 | 0.1972 | 0.1808 | 0.2176 | 1541 |
| B frozen | B test rows | roc\_auc | 0.6372 | 0.01518 | 0.636 | 0.6201 | 0.6517 | 1541 |
| B frozen | B test rows | brier | 0.1146 | 0.0135 | 0.0867 | 0.08342 | 0.09018 | 1541 |
| B frozen | B test rows | precision |  |  | 0.2077 | 0.1905 | 0.2256 | 1541 |
| B frozen | B test rows | recall |  |  | 0.3005 | 0.2771 | 0.3243 | 1541 |
| B frozen | B test rows | f1 |  |  | 0.2456 | 0.2265 | 0.2642 | 1541 |
| B frozen | B test rows | alert\_rate |  |  | 0.1439 | 0.1384 | 0.1498 | 1541 |
| A frozen | B test rows | ap | 0.2302 | 0.03046 | 0.1785 | 0.1631 | 0.1974 | 1541 |
| A frozen | B test rows | roc\_auc | 0.6259 | 0.01193 | 0.604 | 0.5894 | 0.6203 | 1541 |
| A frozen | B test rows | brier | 0.1162 | 0.01349 | 0.08926 | 0.08616 | 0.09264 | 1541 |
| A frozen | B test rows | precision |  |  | 0.1583 | 0.1463 | 0.1713 | 1541 |
| A frozen | B test rows | recall |  |  | 0.3556 | 0.3327 | 0.3806 | 1541 |
| A frozen | B test rows | f1 |  |  | 0.2191 | 0.204 | 0.2354 | 1541 |
| A frozen | B test rows | alert\_rate |  |  | 0.2235 | 0.2166 | 0.2299 | 1541 |
| B plain | B test rows | ap | 0.2616 | 0.03494 | 0.1992 | 0.1828 | 0.2197 | 1541 |
| B plain | B test rows | roc\_auc | 0.6536 | 0.01502 | 0.6341 | 0.6184 | 0.6495 | 1541 |
| B plain | B test rows | brier | 0.1141 | 0.01359 | 0.08642 | 0.083 | 0.09004 | 1541 |
| B plain | B test rows | precision |  |  | 0.2258 | 0.2056 | 0.2456 | 1541 |
| B plain | B test rows | recall |  |  | 0.2544 | 0.2332 | 0.2763 | 1541 |
| B plain | B test rows | f1 |  |  | 0.2392 | 0.2193 | 0.2587 | 1541 |
| B plain | B test rows | alert\_rate |  |  | 0.1121 | 0.1073 | 0.117 | 1541 |
| B dummy | B test rows | ap | 0.138 | 0.01983 | 0.09947 | 0.09508 | 0.104 | 1541 |
| B dummy | B test rows | roc\_auc | 0.5 | 0 | 0.5 | 0.5 | 0.5 | 1541 |
| B dummy | B test rows | brier | 0.1197 | 0.01502 | 0.09093 | 0.08773 | 0.09422 | 1541 |
| B dummy | B test rows | precision |  |  | 0 | 0 | 0 | 1541 |
| B dummy | B test rows | recall |  |  | 0 | 0 | 0 | 1541 |
| B dummy | B test rows | f1 |  |  | 0 | 0 | 0 | 1541 |
| B dummy | B test rows | alert\_rate |  |  | 0 | 0 | 0 | 1541 |
| A frozen | A test rows | ap | 0.2317 | 0.02763 | 0.175 | 0.1611 | 0.1891 | 1968 |
| A frozen | A test rows | roc\_auc | 0.6143 | 0.01353 | 0.5952 | 0.5822 | 0.6086 | 1968 |
| A frozen | A test rows | brier | 0.1239 | 0.01344 | 0.09328 | 0.09038 | 0.09607 | 1968 |
| A frozen | A test rows | precision |  |  | 0.1526 | 0.1428 | 0.1621 | 1968 |
| A frozen | A test rows | recall |  |  | 0.3801 | 0.3601 | 0.4018 | 1968 |
| A frozen | A test rows | f1 |  |  | 0.2178 | 0.2047 | 0.2304 | 1968 |
| A frozen | A test rows | alert\_rate |  |  | 0.2584 | 0.2521 | 0.2641 | 1968 |
| A plain | A test rows | ap | 0.2435 | 0.03142 | 0.1775 | 0.1636 | 0.1919 | 1968 |
| A plain | A test rows | roc\_auc | 0.6213 | 0.01606 | 0.5995 | 0.5863 | 0.6127 | 1968 |
| A plain | A test rows | brier | 0.1243 | 0.01427 | 0.0935 | 0.09054 | 0.09629 | 1968 |
| A plain | A test rows | precision |  |  | 0.1507 | 0.1405 | 0.1598 | 1968 |
| A plain | A test rows | recall |  |  | 0.374 | 0.3541 | 0.3951 | 1968 |
| A plain | A test rows | f1 |  |  | 0.2148 | 0.2021 | 0.2264 | 1968 |
| A plain | A test rows | alert\_rate |  |  | 0.2576 | 0.2509 | 0.2635 | 1968 |
| A dummy | A test rows | ap | 0.1482 | 0.01977 | 0.1038 | 0.09955 | 0.1079 | 1968 |
| A dummy | A test rows | roc\_auc | 0.5 | 0 | 0.5 | 0.5 | 0.5 | 1968 |
| A dummy | A test rows | brier | 0.1269 | 0.01452 | 0.09484 | 0.09186 | 0.09774 | 1968 |
| A dummy | A test rows | precision |  |  | 0 | 0 | 0 | 1968 |
| A dummy | A test rows | recall |  |  | 0 | 0 | 0 | 1968 |
| A dummy | A test rows | f1 |  |  | 0 | 0 | 0 | 1968 |
| A dummy | A test rows | alert\_rate |  |  | 0 | 0 | 0 | 1968 |

Slices, detractor alert (judged only with more than 100 test detractors):

| slice | judged\_slices | too\_few | pooled\_precision\_A | pooled\_recall\_A | mean\_precision\_A | sd\_precision\_A | mean\_recall\_A | sd\_recall\_A | pooled\_precision\_B | pooled\_recall\_B | mean\_precision\_B | sd\_precision\_B | mean\_recall\_B | sd\_recall\_B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| customer\_state | 3 | 4 | 0.1643 | 0.3378 | 0.1883 | 0.04757 | 0.4547 | 0.3381 | 0.2188 | 0.2782 | 0.2311 | 0.03673 | 0.3327 | 0.1872 |
| route\_seller\_to\_customer\_state | 3 | 45 | 0.1564 | 0.3385 | 0.1814 | 0.04839 | 0.5148 | 0.4137 | 0.2085 | 0.2767 | 0.2178 | 0.02897 | 0.3507 | 0.2099 |
| basket | 2 | 1 | 0.1488 | 0.3219 | 0.2013 | 0.132 | 0.4893 | 0.3753 | 0.1991 | 0.2677 | 0.2542 | 0.1452 | 0.3971 | 0.2901 |
| sellers | 2 | 0 | 0.1583 | 0.3556 | 0.2924 | 0.2235 | 0.6511 | 0.4934 | 0.2077 | 0.3005 | 0.3137 | 0.1947 | 0.6135 | 0.5227 |

### F. Tuning grids and the grid edge

Every configuration of every family, with its mean and standard error over the five validation folds and the gap between training and validation scores.

Lead time:

| family | params | validation\_mean | validation\_se | train\_validation\_gap |
| --- | --- | --- | --- | --- |
| linear | {"alpha": 0.01} | 5.025 | 0.6115 | 1.164 |
| linear | {"alpha": 0.1} | 5.024 | 0.6114 | 1.164 |
| linear | {"alpha": 0.5} | 5.024 | 0.6113 | 1.163 |
| linear | {"alpha": 1.0} | 5.023 | 0.6112 | 1.162 |
| linear | {"alpha": 5.0} | 5.02 | 0.6099 | 1.158 |
| linear | {"alpha": 10.0} | 5.02 | 0.6083 | 1.156 |
| linear | {"alpha": 20.0} | 5.019 | 0.6056 | 1.153 |
| linear | {"alpha": 50.0} | 5.02 | 0.6 | 1.148 |
| linear | {"alpha": 100.0} | 5.021 | 0.5946 | 1.142 |
| tree | {"max\_depth": 4, "min\_samples\_leaf": 20} | 5.084 | 0.6428 | 1.065 |
| tree | {"max\_depth": 4, "min\_samples\_leaf": 50} | 5.088 | 0.6403 | 1.072 |
| tree | {"max\_depth": 4, "min\_samples\_leaf": 100} | 5.084 | 0.6426 | 1.065 |
| tree | {"max\_depth": 4, "min\_samples\_leaf": 200} | 5.084 | 0.6443 | 1.061 |
| tree | {"max\_depth": 5, "min\_samples\_leaf": 20} | 5.052 | 0.6432 | 1.108 |
| tree | {"max\_depth": 5, "min\_samples\_leaf": 50} | 5.061 | 0.6384 | 1.116 |
| tree | {"max\_depth": 5, "min\_samples\_leaf": 100} | 5.053 | 0.6394 | 1.104 |
| tree | {"max\_depth": 5, "min\_samples\_leaf": 200} | 5.058 | 0.6437 | 1.096 |
| tree | {"max\_depth": 6, "min\_samples\_leaf": 20} | 5.018 | 0.6524 | 1.143 |
| tree | {"max\_depth": 6, "min\_samples\_leaf": 50} | 5.008 | 0.6544 | 1.125 |
| tree | {"max\_depth": 6, "min\_samples\_leaf": 100} | 5.017 | 0.658 | 1.119 |
| tree | {"max\_depth": 6, "min\_samples\_leaf": 200} | 5.016 | 0.6613 | 1.099 |
| tree | {"max\_depth": 8, "min\_samples\_leaf": 20} | 5.001 | 0.6579 | 1.251 |
| tree | {"max\_depth": 8, "min\_samples\_leaf": 50} | 4.976 | 0.6605 | 1.188 |
| tree | {"max\_depth": 8, "min\_samples\_leaf": 100} | 4.974 | 0.6603 | 1.149 |
| tree | {"max\_depth": 8, "min\_samples\_leaf": 200} | 4.976 | 0.6676 | 1.103 |
| tree | {"max\_depth": 10, "min\_samples\_leaf": 20} | 5.053 | 0.6539 | 1.424 |
| tree | {"max\_depth": 10, "min\_samples\_leaf": 50} | 5.02 | 0.6526 | 1.302 |
| tree | {"max\_depth": 10, "min\_samples\_leaf": 100} | 4.995 | 0.6542 | 1.205 |
| tree | {"max\_depth": 10, "min\_samples\_leaf": 200} | 4.98 | 0.6588 | 1.121 |
| tree | {"max\_depth": 12, "min\_samples\_leaf": 20} | 5.103 | 0.6419 | 1.574 |
| tree | {"max\_depth": 12, "min\_samples\_leaf": 50} | 5.046 | 0.6513 | 1.364 |
| tree | {"max\_depth": 12, "min\_samples\_leaf": 100} | 4.996 | 0.6523 | 1.221 |
| tree | {"max\_depth": 12, "min\_samples\_leaf": 200} | 4.976 | 0.6562 | 1.12 |
| tree | {"max\_depth": 14, "min\_samples\_leaf": 20} | 5.138 | 0.6337 | 1.678 |
| tree | {"max\_depth": 14, "min\_samples\_leaf": 50} | 5.051 | 0.6485 | 1.384 |
| tree | {"max\_depth": 14, "min\_samples\_leaf": 100} | 4.993 | 0.6481 | 1.221 |
| tree | {"max\_depth": 14, "min\_samples\_leaf": 200} | 4.976 | 0.6562 | 1.12 |
| tree | {"max\_depth": 16, "min\_samples\_leaf": 20} | 5.163 | 0.6271 | 1.741 |
| tree | {"max\_depth": 16, "min\_samples\_leaf": 50} | 5.049 | 0.6443 | 1.387 |
| tree | {"max\_depth": 16, "min\_samples\_leaf": 100} | 4.994 | 0.6485 | 1.223 |
| tree | {"max\_depth": 16, "min\_samples\_leaf": 200} | 4.976 | 0.6562 | 1.12 |
| tree | {"max\_depth": 18, "min\_samples\_leaf": 20} | 5.165 | 0.6257 | 1.759 |
| tree | {"max\_depth": 18, "min\_samples\_leaf": 50} | 5.052 | 0.6453 | 1.391 |
| tree | {"max\_depth": 18, "min\_samples\_leaf": 100} | 4.993 | 0.6482 | 1.223 |
| tree | {"max\_depth": 18, "min\_samples\_leaf": 200} | 4.976 | 0.6562 | 1.12 |
| forest | {"max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 4.973 | 0.6554 | 1.054 |
| forest | {"max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 4.986 | 0.6519 | 1.033 |
| forest | {"max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 100} | 5.022 | 0.6484 | 1.028 |
| forest | {"max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 5.082 | 0.649 | 1.032 |
| forest | {"max\_depth": 10, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 4.935 | 0.6503 | 1.084 |
| forest | {"max\_depth": 10, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 4.963 | 0.6457 | 1.052 |
| forest | {"max\_depth": 10, "max\_features": "sqrt", "min\_samples\_leaf": 100} | 5.003 | 0.6423 | 1.033 |
| forest | {"max\_depth": 10, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 5.072 | 0.6443 | 1.034 |
| forest | {"max\_depth": 12, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 4.909 | 0.6501 | 1.109 |
| forest | {"max\_depth": 12, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 4.939 | 0.645 | 1.053 |
| forest | {"max\_depth": 12, "max\_features": "sqrt", "min\_samples\_leaf": 100} | 4.988 | 0.641 | 1.03 |
| forest | {"max\_depth": 12, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 5.069 | 0.6431 | 1.036 |
| forest | {"max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 4.894 | 0.646 | 1.128 |
| forest | {"max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 4.932 | 0.6439 | 1.059 |
| forest | {"max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 100} | 4.992 | 0.64 | 1.039 |
| forest | {"max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 5.068 | 0.643 | 1.036 |
| forest | {"max\_depth": 16, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 4.889 | 0.6458 | 1.145 |
| forest | {"max\_depth": 16, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 4.933 | 0.6441 | 1.067 |
| forest | {"max\_depth": 16, "max\_features": "sqrt", "min\_samples\_leaf": 100} | 4.987 | 0.6402 | 1.037 |
| forest | {"max\_depth": 16, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 5.065 | 0.6428 | 1.035 |
| forest | {"max\_depth": 18, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 4.887 | 0.6462 | 1.157 |
| forest | {"max\_depth": 18, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 4.932 | 0.6441 | 1.07 |
| forest | {"max\_depth": 18, "max\_features": "sqrt", "min\_samples\_leaf": 100} | 4.987 | 0.6403 | 1.038 |
| forest | {"max\_depth": 18, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 5.066 | 0.6431 | 1.035 |

Detractor alert:

| family | params | validation\_mean | validation\_se | train\_validation\_gap |
| --- | --- | --- | --- | --- |
| linear | {"C": 0.01, "class\_weight": null} | 0.2734 | 0.03179 | -0.04629 |
| linear | {"C": 0.01, "class\_weight": "balanced"} | 0.2721 | 0.03204 | -0.04556 |
| linear | {"C": 0.1, "class\_weight": null} | 0.2717 | 0.03348 | -0.03882 |
| linear | {"C": 0.1, "class\_weight": "balanced"} | 0.2699 | 0.03295 | -0.03957 |
| linear | {"C": 0.5, "class\_weight": null} | 0.2692 | 0.03389 | -0.03394 |
| linear | {"C": 0.5, "class\_weight": "balanced"} | 0.2671 | 0.03294 | -0.03595 |
| linear | {"C": 1.0, "class\_weight": null} | 0.2678 | 0.03386 | -0.03214 |
| linear | {"C": 1.0, "class\_weight": "balanced"} | 0.2658 | 0.033 | -0.03451 |
| linear | {"C": 5.0, "class\_weight": null} | 0.2646 | 0.03417 | -0.02802 |
| linear | {"C": 5.0, "class\_weight": "balanced"} | 0.2631 | 0.03329 | -0.03147 |
| linear | {"C": 10.0, "class\_weight": null} | 0.2633 | 0.03453 | -0.02621 |
| linear | {"C": 10.0, "class\_weight": "balanced"} | 0.2621 | 0.03341 | -0.03041 |
| linear | {"C": 20.0, "class\_weight": null} | 0.2626 | 0.03442 | -0.02561 |
| linear | {"C": 20.0, "class\_weight": "balanced"} | 0.2618 | 0.03354 | -0.03003 |
| linear | {"C": 50.0, "class\_weight": null} | 0.2616 | 0.03486 | -0.02443 |
| linear | {"C": 50.0, "class\_weight": "balanced"} | 0.2616 | 0.03372 | -0.02968 |
| linear | {"C": 100.0, "class\_weight": null} | 0.2616 | 0.03485 | -0.02464 |
| linear | {"C": 100.0, "class\_weight": "balanced"} | 0.2602 | 0.03442 | -0.0283 |
| tree | {"class\_weight": null, "max\_depth": 4, "min\_samples\_leaf": 20} | 0.2272 | 0.02898 | -0.01755 |
| tree | {"class\_weight": null, "max\_depth": 4, "min\_samples\_leaf": 50} | 0.2255 | 0.03001 | -0.01985 |
| tree | {"class\_weight": null, "max\_depth": 4, "min\_samples\_leaf": 100} | 0.2279 | 0.02894 | -0.02255 |
| tree | {"class\_weight": null, "max\_depth": 4, "min\_samples\_leaf": 200} | 0.2298 | 0.02967 | -0.03038 |
| tree | {"class\_weight": null, "max\_depth": 5, "min\_samples\_leaf": 20} | 0.2386 | 0.03469 | -0.007572 |
| tree | {"class\_weight": null, "max\_depth": 5, "min\_samples\_leaf": 50} | 0.2379 | 0.03671 | -0.01519 |
| tree | {"class\_weight": null, "max\_depth": 5, "min\_samples\_leaf": 100} | 0.2394 | 0.03539 | -0.0199 |
| tree | {"class\_weight": null, "max\_depth": 5, "min\_samples\_leaf": 200} | 0.2387 | 0.03499 | -0.02747 |
| tree | {"class\_weight": null, "max\_depth": 6, "min\_samples\_leaf": 20} | 0.2202 | 0.02528 | 0.03157 |
| tree | {"class\_weight": null, "max\_depth": 6, "min\_samples\_leaf": 50} | 0.2242 | 0.02953 | 0.0128 |
| tree | {"class\_weight": null, "max\_depth": 6, "min\_samples\_leaf": 100} | 0.2283 | 0.02803 | 0.003448 |
| tree | {"class\_weight": null, "max\_depth": 6, "min\_samples\_leaf": 200} | 0.2267 | 0.02792 | -0.007118 |
| tree | {"class\_weight": null, "max\_depth": 8, "min\_samples\_leaf": 20} | 0.2125 | 0.02591 | 0.07815 |
| tree | {"class\_weight": null, "max\_depth": 8, "min\_samples\_leaf": 50} | 0.2262 | 0.02888 | 0.03644 |
| tree | {"class\_weight": null, "max\_depth": 8, "min\_samples\_leaf": 100} | 0.2292 | 0.02994 | 0.02061 |
| tree | {"class\_weight": null, "max\_depth": 8, "min\_samples\_leaf": 200} | 0.2323 | 0.0278 | -0.001048 |
| tree | {"class\_weight": null, "max\_depth": 10, "min\_samples\_leaf": 20} | 0.2071 | 0.02604 | 0.1208 |
| tree | {"class\_weight": null, "max\_depth": 10, "min\_samples\_leaf": 50} | 0.2243 | 0.02955 | 0.06152 |
| tree | {"class\_weight": null, "max\_depth": 10, "min\_samples\_leaf": 100} | 0.2333 | 0.02961 | 0.02892 |
| tree | {"class\_weight": null, "max\_depth": 10, "min\_samples\_leaf": 200} | 0.2345 | 0.02852 | 0.003455 |
| tree | {"class\_weight": null, "max\_depth": 12, "min\_samples\_leaf": 20} | 0.2086 | 0.0242 | 0.1508 |
| tree | {"class\_weight": null, "max\_depth": 12, "min\_samples\_leaf": 50} | 0.2197 | 0.02889 | 0.08261 |
| tree | {"class\_weight": null, "max\_depth": 12, "min\_samples\_leaf": 100} | 0.2325 | 0.02942 | 0.03714 |
| tree | {"class\_weight": null, "max\_depth": 12, "min\_samples\_leaf": 200} | 0.2297 | 0.02915 | 0.01183 |
| tree | {"class\_weight": null, "max\_depth": 14, "min\_samples\_leaf": 20} | 0.2018 | 0.02464 | 0.1816 |
| tree | {"class\_weight": null, "max\_depth": 14, "min\_samples\_leaf": 50} | 0.2175 | 0.02886 | 0.09587 |
| tree | {"class\_weight": null, "max\_depth": 14, "min\_samples\_leaf": 100} | 0.2287 | 0.02987 | 0.04515 |
| tree | {"class\_weight": null, "max\_depth": 14, "min\_samples\_leaf": 200} | 0.2294 | 0.02916 | 0.01332 |
| tree | {"class\_weight": null, "max\_depth": 16, "min\_samples\_leaf": 20} | 0.1997 | 0.02436 | 0.2039 |
| tree | {"class\_weight": null, "max\_depth": 16, "min\_samples\_leaf": 50} | 0.2154 | 0.02817 | 0.1055 |
| tree | {"class\_weight": null, "max\_depth": 16, "min\_samples\_leaf": 100} | 0.2281 | 0.02979 | 0.04758 |
| tree | {"class\_weight": null, "max\_depth": 16, "min\_samples\_leaf": 200} | 0.2327 | 0.02822 | 0.01039 |
| tree | {"class\_weight": null, "max\_depth": 18, "min\_samples\_leaf": 20} | 0.1979 | 0.02353 | 0.2203 |
| tree | {"class\_weight": null, "max\_depth": 18, "min\_samples\_leaf": 50} | 0.2146 | 0.02728 | 0.1092 |
| tree | {"class\_weight": null, "max\_depth": 18, "min\_samples\_leaf": 100} | 0.2284 | 0.02973 | 0.0481 |
| tree | {"class\_weight": null, "max\_depth": 18, "min\_samples\_leaf": 200} | 0.2327 | 0.02823 | 0.01057 |
| tree | {"class\_weight": "balanced", "max\_depth": 4, "min\_samples\_leaf": 20} | 0.2223 | 0.02828 | -0.00851 |
| tree | {"class\_weight": "balanced", "max\_depth": 4, "min\_samples\_leaf": 50} | 0.2236 | 0.02779 | -0.0124 |
| tree | {"class\_weight": "balanced", "max\_depth": 4, "min\_samples\_leaf": 100} | 0.2244 | 0.02792 | -0.01439 |
| tree | {"class\_weight": "balanced", "max\_depth": 4, "min\_samples\_leaf": 200} | 0.2232 | 0.02756 | -0.01919 |
| tree | {"class\_weight": "balanced", "max\_depth": 5, "min\_samples\_leaf": 20} | 0.2242 | 0.02919 | 0.009191 |
| tree | {"class\_weight": "balanced", "max\_depth": 5, "min\_samples\_leaf": 50} | 0.2272 | 0.02945 | 0.002055 |
| tree | {"class\_weight": "balanced", "max\_depth": 5, "min\_samples\_leaf": 100} | 0.2264 | 0.02866 | -0.002144 |
| tree | {"class\_weight": "balanced", "max\_depth": 5, "min\_samples\_leaf": 200} | 0.2269 | 0.02836 | -0.0121 |
| tree | {"class\_weight": "balanced", "max\_depth": 6, "min\_samples\_leaf": 20} | 0.2218 | 0.03004 | 0.03078 |
| tree | {"class\_weight": "balanced", "max\_depth": 6, "min\_samples\_leaf": 50} | 0.2239 | 0.02934 | 0.02082 |
| tree | {"class\_weight": "balanced", "max\_depth": 6, "min\_samples\_leaf": 100} | 0.2284 | 0.0272 | 0.007573 |
| tree | {"class\_weight": "balanced", "max\_depth": 6, "min\_samples\_leaf": 200} | 0.2293 | 0.02838 | -0.006417 |
| tree | {"class\_weight": "balanced", "max\_depth": 8, "min\_samples\_leaf": 20} | 0.2144 | 0.02992 | 0.07698 |
| tree | {"class\_weight": "balanced", "max\_depth": 8, "min\_samples\_leaf": 50} | 0.2216 | 0.0275 | 0.04937 |
| tree | {"class\_weight": "balanced", "max\_depth": 8, "min\_samples\_leaf": 100} | 0.226 | 0.02934 | 0.02796 |
| tree | {"class\_weight": "balanced", "max\_depth": 8, "min\_samples\_leaf": 200} | 0.2304 | 0.02891 | 0.002987 |
| tree | {"class\_weight": "balanced", "max\_depth": 10, "min\_samples\_leaf": 20} | 0.205 | 0.02637 | 0.1245 |
| tree | {"class\_weight": "balanced", "max\_depth": 10, "min\_samples\_leaf": 50} | 0.2131 | 0.02793 | 0.07872 |
| tree | {"class\_weight": "balanced", "max\_depth": 10, "min\_samples\_leaf": 100} | 0.2244 | 0.02875 | 0.04171 |
| tree | {"class\_weight": "balanced", "max\_depth": 10, "min\_samples\_leaf": 200} | 0.227 | 0.02995 | 0.01144 |
| tree | {"class\_weight": "balanced", "max\_depth": 12, "min\_samples\_leaf": 20} | 0.1994 | 0.02592 | 0.1646 |
| tree | {"class\_weight": "balanced", "max\_depth": 12, "min\_samples\_leaf": 50} | 0.2128 | 0.02621 | 0.09793 |
| tree | {"class\_weight": "balanced", "max\_depth": 12, "min\_samples\_leaf": 100} | 0.2208 | 0.02978 | 0.05227 |
| tree | {"class\_weight": "balanced", "max\_depth": 12, "min\_samples\_leaf": 200} | 0.2299 | 0.02894 | 0.01138 |
| tree | {"class\_weight": "balanced", "max\_depth": 14, "min\_samples\_leaf": 20} | 0.1938 | 0.02548 | 0.2015 |
| tree | {"class\_weight": "balanced", "max\_depth": 14, "min\_samples\_leaf": 50} | 0.2107 | 0.02574 | 0.1144 |
| tree | {"class\_weight": "balanced", "max\_depth": 14, "min\_samples\_leaf": 100} | 0.2193 | 0.02887 | 0.05748 |
| tree | {"class\_weight": "balanced", "max\_depth": 14, "min\_samples\_leaf": 200} | 0.226 | 0.02981 | 0.01695 |
| tree | {"class\_weight": "balanced", "max\_depth": 16, "min\_samples\_leaf": 20} | 0.1896 | 0.02547 | 0.2306 |
| tree | {"class\_weight": "balanced", "max\_depth": 16, "min\_samples\_leaf": 50} | 0.2079 | 0.02687 | 0.1221 |
| tree | {"class\_weight": "balanced", "max\_depth": 16, "min\_samples\_leaf": 100} | 0.2213 | 0.02799 | 0.0575 |
| tree | {"class\_weight": "balanced", "max\_depth": 16, "min\_samples\_leaf": 200} | 0.2292 | 0.02878 | 0.01409 |
| tree | {"class\_weight": "balanced", "max\_depth": 18, "min\_samples\_leaf": 20} | 0.1897 | 0.02501 | 0.2488 |
| tree | {"class\_weight": "balanced", "max\_depth": 18, "min\_samples\_leaf": 50} | 0.2098 | 0.02576 | 0.1232 |
| tree | {"class\_weight": "balanced", "max\_depth": 18, "min\_samples\_leaf": 100} | 0.2182 | 0.02841 | 0.06136 |
| tree | {"class\_weight": "balanced", "max\_depth": 18, "min\_samples\_leaf": 200} | 0.2292 | 0.02876 | 0.01427 |
| forest | {"class\_weight": null, "max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.2761 | 0.03041 | 0.0257 |
| forest | {"class\_weight": null, "max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 0.2746 | 0.03054 | 0.0002213 |
| forest | {"class\_weight": null, "max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 100} | 0.2703 | 0.03047 | -0.0153 |
| forest | {"class\_weight": null, "max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 0.2625 | 0.02971 | -0.02304 |
| forest | {"class\_weight": null, "max\_depth": 10, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.2745 | 0.03063 | 0.05163 |
| forest | {"class\_weight": null, "max\_depth": 10, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 0.2739 | 0.03047 | 0.01286 |
| forest | {"class\_weight": null, "max\_depth": 10, "max\_features": "sqrt", "min\_samples\_leaf": 100} | 0.2708 | 0.03034 | -0.008784 |
| forest | {"class\_weight": null, "max\_depth": 10, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 0.2642 | 0.03036 | -0.02214 |
| forest | {"class\_weight": null, "max\_depth": 12, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.2739 | 0.02993 | 0.07694 |
| forest | {"class\_weight": null, "max\_depth": 12, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 0.2733 | 0.03063 | 0.02425 |
| forest | {"class\_weight": null, "max\_depth": 12, "max\_features": "sqrt", "min\_samples\_leaf": 100} | 0.2692 | 0.03025 | -0.003239 |
| forest | {"class\_weight": null, "max\_depth": 12, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 0.2634 | 0.02971 | -0.02047 |
| forest | {"class\_weight": null, "max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.2745 | 0.02927 | 0.1011 |
| forest | {"class\_weight": null, "max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 0.2726 | 0.03119 | 0.03286 |
| forest | {"class\_weight": null, "max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 100} | 0.2692 | 0.03038 | -0.0008786 |
| forest | {"class\_weight": null, "max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 0.2644 | 0.03032 | -0.02057 |
| forest | {"class\_weight": null, "max\_depth": 16, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.2754 | 0.03005 | 0.1152 |
| forest | {"class\_weight": null, "max\_depth": 16, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 0.2738 | 0.03039 | 0.03645 |
| forest | {"class\_weight": null, "max\_depth": 16, "max\_features": "sqrt", "min\_samples\_leaf": 100} | 0.2694 | 0.03046 | 0.0005274 |
| forest | {"class\_weight": null, "max\_depth": 16, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 0.2645 | 0.0306 | -0.02002 |
| forest | {"class\_weight": null, "max\_depth": 18, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.274 | 0.02946 | 0.1324 |
| forest | {"class\_weight": null, "max\_depth": 18, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 0.2738 | 0.03103 | 0.0398 |
| forest | {"class\_weight": null, "max\_depth": 18, "max\_features": "sqrt", "min\_samples\_leaf": 100} | 0.2699 | 0.03025 | 0.0009521 |
| forest | {"class\_weight": null, "max\_depth": 18, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 0.2645 | 0.0305 | -0.02017 |
| forest | {"class\_weight": "balanced", "max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.2695 | 0.03025 | 0.04042 |
| forest | {"class\_weight": "balanced", "max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 0.2679 | 0.03092 | 0.004336 |
| forest | {"class\_weight": "balanced", "max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 100} | 0.2661 | 0.02988 | -0.01306 |
| forest | {"class\_weight": "balanced", "max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 0.2588 | 0.03035 | -0.02386 |
| forest | {"class\_weight": "balanced", "max\_depth": 10, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.2693 | 0.03016 | 0.07407 |
| forest | {"class\_weight": "balanced", "max\_depth": 10, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 0.2675 | 0.03036 | 0.01984 |
| forest | {"class\_weight": "balanced", "max\_depth": 10, "max\_features": "sqrt", "min\_samples\_leaf": 100} | 0.2655 | 0.02999 | -0.006509 |
| forest | {"class\_weight": "balanced", "max\_depth": 10, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 0.2593 | 0.03012 | -0.0221 |
| forest | {"class\_weight": "balanced", "max\_depth": 12, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.2679 | 0.03052 | 0.1048 |
| forest | {"class\_weight": "balanced", "max\_depth": 12, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 0.2689 | 0.03008 | 0.02958 |
| forest | {"class\_weight": "balanced", "max\_depth": 12, "max\_features": "sqrt", "min\_samples\_leaf": 100} | 0.2658 | 0.02956 | -0.003048 |
| forest | {"class\_weight": "balanced", "max\_depth": 12, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 0.2596 | 0.03053 | -0.02124 |
| forest | {"class\_weight": "balanced", "max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.2687 | 0.03031 | 0.1282 |
| forest | {"class\_weight": "balanced", "max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 0.2681 | 0.02999 | 0.03707 |
| forest | {"class\_weight": "balanced", "max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 100} | 0.2662 | 0.02996 | -0.001152 |
| forest | {"class\_weight": "balanced", "max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 0.2592 | 0.03017 | -0.02085 |
| forest | {"class\_weight": "balanced", "max\_depth": 16, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.2669 | 0.03034 | 0.1494 |
| forest | {"class\_weight": "balanced", "max\_depth": 16, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 0.2687 | 0.03055 | 0.04106 |
| forest | {"class\_weight": "balanced", "max\_depth": 16, "max\_features": "sqrt", "min\_samples\_leaf": 100} | 0.2655 | 0.02966 | -0.000483 |
| forest | {"class\_weight": "balanced", "max\_depth": 16, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 0.2592 | 0.02999 | -0.02066 |
| forest | {"class\_weight": "balanced", "max\_depth": 18, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.2685 | 0.03024 | 0.1609 |
| forest | {"class\_weight": "balanced", "max\_depth": 18, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 0.2689 | 0.03055 | 0.04307 |
| forest | {"class\_weight": "balanced", "max\_depth": 18, "max\_features": "sqrt", "min\_samples\_leaf": 100} | 0.2655 | 0.03005 | 0.0005076 |
| forest | {"class\_weight": "balanced", "max\_depth": 18, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 0.2589 | 0.02992 | -0.02044 |

### G. Population chain detail

Every removal from the improved pipeline's population, by rule.

Lead time:

| step | rows |
| --- | --- |
| A development rows (s02, pre-cutoff, eligible) | 76925 |
| removed: B\_STATE | 13777 |
| removed: B\_DISTANCE | 606 |
| removed: B\_LEAD\_CAP | 45 |
| removed: B\_WARMUP | 1264 |
| B development rows | 61233 |

Detractor alert:

| step | rows |
| --- | --- |
| A development rows (s02, pre-cutoff, eligible) | 77736 |
| removed: B\_STATE | 13983 |
| removed: B\_DISTANCE | 618 |
| removed: B\_NO\_HANDOVER | 461 |
| removed: B\_REVIEW\_BEFORE\_HANDOVER | 146 |
| removed: B\_WARMUP | 1270 |
| B development rows | 61258 |

### H. Model candidates on the five folds

Lead time:

| family | estimator | train\_mean | validation\_mean | validation\_se | kept |
| --- | --- | --- | --- | --- | --- |
| dummy | dummy\_median | 4.794 | 5.969 | 0.7107 | True |
| linear/logistic | linear | 3.861 | 5.025 | 0.6115 | True |
| single tree | tree\_reg | 3.949 | 5.053 | 0.6394 | False |
| forest | forest\_reg | 3.911 | 4.963 | 0.6457 | False |

Detractor alert:

| family | estimator | train\_mean | validation\_mean | validation\_se | kept |
| --- | --- | --- | --- | --- | --- |
| dummy | dummy\_prior | 0.1167 | 0.138 | 0.01983 | True |
| linear/logistic | logistic | 0.2369 | 0.2616 | 0.03494 | True |
| single tree | tree\_clf | 0.2195 | 0.2394 | 0.03539 | False |
| forest | forest\_clf | 0.2868 | 0.2739 | 0.03047 | False |

### I. Feature ranking by fold

The selection ranking repeated inside each training fold.

Lead time:

| fold | training\_rows | selected | jaccard\_with\_B4 | added\_vs\_B4 | dropped\_vs\_B4 | spearman\_ranks\_vs\_B4 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 7932 | 19 | 0.9048 |  | n\_products, payment\_installments\_max | 0.9378 |
| 2 | 18077 | 21 | 0.9091 | n\_payment\_methods | payment\_installments\_max | 0.9651 |
| 3 | 26184 | 21 | 1 |  |  | 0.9836 |
| 4 | 37647 | 20 | 0.9524 |  | n\_items | 0.974 |
| 5 | 47415 | 20 | 0.9524 |  | purchase\_month | 0.9822 |

Detractor alert:

| fold | training\_rows | selected | jaccard\_with\_B4 | added\_vs\_B4 | dropped\_vs\_B4 | spearman\_ranks\_vs\_B4 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 7592 | 22 | 0.6786 | product\_photos\_qty, purchase\_dayofweek, purchase\_hour | distance\_km\_max, interstate\_share, order\_dispatch\_days, seller\_prior\_dispatch\_days, seller\_prior\_late\_handover\_days, total\_price | 0.2203 |
| 2 | 17595 | 25 | 0.8519 | product\_photos\_qty, purchase\_hour | distance\_km\_max, route\_recent\_carrier\_transit\_days | 0.6694 |
| 3 | 25529 | 27 | 0.9259 | category\_missing\_fraction, purchase\_hour |  | 0.82 |
| 4 | 37140 | 26 | 0.9615 | purchase\_hour |  | 0.9564 |
| 5 | 47237 | 25 | 1 |  |  | 0.9736 |

### J. Correlation and variance inflation

Variance inflation factor of each numeric predictor in the baseline pool, development orders.

Lead time:

| feature | vif | vif\_note |
| --- | --- | --- |
| n\_items | 1.656 |  |
| n\_products | 1.799 |  |
| n\_sellers | 1.857 |  |
| n\_categories | 4.821 |  |
| total\_price | 1.476 |  |
| total\_freight | 3.334 |  |
| freight\_ratio | 1.26 |  |
| total\_weight\_g | 3.609 |  |
| total\_volume\_cm3 | 3.473 |  |
| weight\_missing\_fraction |  | constant on the complete rows |
| volume\_missing\_fraction |  | constant on the complete rows |
| category\_missing\_fraction | 4.271 |  |
| distance\_km\_max | 1.685 |  |
| distance\_missing\_fraction |  | constant on the complete rows |
| interstate\_share | 1.501 |  |
| purchase\_month | 1.003 |  |
| purchase\_dayofweek | 1.002 |  |
| purchase\_hour | 1.001 |  |
| payment\_installments\_max | 1.155 |  |
| n\_payment\_methods | 1.002 |  |

Detractor alert:

| feature | vif | vif\_note |
| --- | --- | --- |
| n\_items | 1.647 |  |
| n\_products | 1.802 |  |
| n\_sellers | 1.856 |  |
| n\_categories | 4.919 |  |
| total\_price | 1.475 |  |
| total\_freight | 3.322 |  |
| freight\_ratio | 1.259 |  |
| total\_weight\_g | 3.498 |  |
| total\_volume\_cm3 | 3.424 |  |
| weight\_missing\_fraction |  | constant on the complete rows |
| volume\_missing\_fraction |  | constant on the complete rows |
| category\_missing\_fraction | 4.368 |  |
| distance\_km\_max | 1.682 |  |
| distance\_missing\_fraction |  | constant on the complete rows |
| interstate\_share | 1.499 |  |
| purchase\_month | 1.003 |  |
| purchase\_dayofweek | 1.002 |  |
| purchase\_hour | 1.001 |  |
| payment\_installments\_max | 1.154 |  |
| n\_payment\_methods | 1.002 |  |

Features dropped by the improved pipeline's reduction step, detractor alert:

| feature | flagged\_by | paired\_with |
| --- | --- | --- |
| customer\_state | nested in route (B-G-02) | route\_seller\_to\_customer\_state |
| primary\_seller\_state | nested in route (B-G-02) | route\_seller\_to\_customer\_state |
| distance\_missing\_fraction | constant |  |
| weight\_missing\_fraction | duplicate | volume\_missing\_fraction |

### K. Declaration of AI use

The team used Anthropic's Claude (Claude Code) throughout. It wrote and ran most of the pipeline code under the team's instructions, drafted the stage documentation, built the number register, and drafted this report and the slides. The team set the problem, the scope and every decision recorded in the project's decision logs, reviewed each stage before it was accepted, and checked the drafts. Every number in the report is filled from the stored pipeline outputs through the register, never typed; an audit script compares the report and slides against those outputs. Every reference was checked by the team against the publisher's record, and the claims made from each source were checked against that record (literature register).
