## 3 Data and preprocessing

Every model row is one order, built only from what is known at that task's prediction moment, and every step below states its rule, its reason and where it is fitted. Steps learned from data are fitted on each training fold only, inside one scikit-learn pipeline, so no statistic from a validation or test order reaches a model (Kapoor and Narayanan, 2023; Müller and Guido, 2016).

**Sources and joins.** We use the Canvas copy of the Olist dataset: nine tables (orders, order items, payments, reviews, customers, sellers, products, geolocation and the category translation). The order is the unit. Items, payments and reviews have several rows per order, so each is aggregated to the order first and then joined one to one; customers join many to one. From the items we take the counts of items, products, sellers and categories, the total price, freight, weight and volume, and the primary item (the highest-priced, ties broken by item id), which gives the primary category and the primary seller. From the payments we take the main payment type and the largest number of instalments. Locations come from the median latitude and longitude of each ZIP prefix inside Brazil; the distance feature is the largest seller-to-customer distance in the order. Customers are matched across orders on `customer_unique_id`, because `customer_id` is new for every order; this is what lets us keep the same customer out of both training and test.

**Targets.** Lead time is the number of days from purchase to delivery, for delivered orders with valid timestamps. The detractor label is 1 when the order's lowest valid review score is 1 or 2. An order can have more than one review; taking the lowest could bias the label towards detractors, so every classification result is also scored against the first-review label. The two agree closely on the test (table below), so the choice does not drive the conclusions.

*Table 3. Detractor results under the lowest-review and first-review labels, test orders.*

{{table:B9.clf.label_sensitivity}}

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

*Table 4. Population chain from the baseline's development orders to the improved pipeline's rows.*

| Step | Lead time | Detractor alert |
| --- | --- | --- |
| Baseline development orders (eligible, before the test period) | {{B2.reg.dev_rows_A}} | {{B2.clf.dev_rows_A}} |
| Customer or seller outside the seven states | − {{B2.reg.removed_state}} | − {{B2.clf.removed_state}} |
| Distance unknown | − {{B2.reg.removed_distance}} | − {{B2.clf.removed_distance}} |
| Lead time above the improved pipeline's cap | − {{B2.reg.removed_cap}} | — |
| Never handed over to the carrier | — | − {{B2.clf.removed_no_handover}} |
| Reviewed at or before handover | — | − {{B2.clf.removed_review_before_handover}} |
| First six weeks (history warm-up) | − {{B2.reg.removed_warmup}} | − {{B2.clf.removed_warmup}} |
| Improved pipeline's development orders | {{B2.reg.dev_rows_B}} | {{B2.clf.dev_rows_B}} |
| Of these, with the label known before the test period (final fit) | {{T1.reg.fit_rows_B}} | {{T1.clf.fit_rows_B}} |
| Fold 5: training rows / validation rows | {{B5.reg.fold5_train_rows}} / {{B5.reg.fold5_validation_rows}} | {{B5.clf.fold5_train_rows}} / {{B5.clf.fold5_validation_rows}} |
| Test orders | {{T1.reg.test_rows_B}} | {{T1.clf.test_rows_B}} ({{T1.clf.test_detractors_B}} detractors) |

The final fit uses fewer rows than the development set because a label must be known before the test period starts: an order delivered or reviewed after the cutoff cannot train the model that is tested on that period. Fold 5's training and validation rows together are fewer again, because the folds also purge customers who appear on both sides and require each training label to be known before its validation window (section 6).
