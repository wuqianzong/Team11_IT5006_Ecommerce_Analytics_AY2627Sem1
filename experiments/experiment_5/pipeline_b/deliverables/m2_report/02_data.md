## 2 Data and preprocessing

Every model row is one order, built only from what is known at checkout, and every step below states its rule, its reason and where it is fitted. Steps learned from data are fitted on each training fold only, inside one scikit-learn pipeline, so no statistic from a validation or test order reaches a model (Kapoor and Narayanan, 2023; Müller and Guido, 2016).

**Sources and joins.** We use the Canvas copy of the Olist dataset: nine tables (orders, order items, payments, reviews, customers, sellers, products, geolocation and the category translation), with {{M2.raw_orders}} orders. The order is the unit. Items, payments and reviews have several rows per order, so each is aggregated to the order first and then joined one to one; customers join many to one. From the items we take the counts of items, products, sellers and categories, the total price, freight, weight and volume, and the primary item (the highest-priced, ties broken by item id), which gives the primary category and the primary seller. From the payments we take the main payment type and the largest number of instalments. Locations come from the median latitude and longitude of each ZIP prefix inside Brazil; the distance feature is the largest seller-to-customer distance in the order. Customers are matched across orders on `customer_unique_id`, because `customer_id` is new for every order; this is what lets us keep the same customer out of both training and test.

**Targets.** Lead time is the number of days from purchase to delivery, for delivered orders with valid timestamps. The detractor label is 1 when the order's lowest valid review score is 1 or 2. An order can have more than one review; taking the lowest could bias the label towards detractors, so the alert is also scored against the first-review label: its test AP is {{M2.clf.test_ap_A}} with the lowest review and {{M2.clf.test_ap_first_A}} with the first, so the choice does not drive the result.

**Which orders each task keeps.** Table 2 lists the cleaning rules; an order can match more than one rule.

*Table 2. Orders removed by each cleaning rule.*

| Rule | Reason | Lead time | Detractor alert |
| --- | --- | --- | --- |
| Purchased before 2017 | The 2016 months are too thin to represent the business | {{M2.reg.excl_before_data_start}} | {{M2.clf.excl_before_data_start}} |
| Not delivered, or lead time missing or not after purchase | No valid target | {{M2.reg.excl_invalid_lead_time}} | — |
| Cancelled or unavailable | No completed purchase to review | — | {{M2.clf.excl_cancelled_or_unavailable}} |
| No valid review score | No valid target | — | {{M2.clf.excl_no_valid_review}} |
| Review answered at or before the purchase | A data error; the label cannot be trusted | — | {{M2.clf.excl_invalid_review_time}} |
| No items | A checkout always has items | {{M2.reg.excl_zero_items}} | {{M2.clf.excl_zero_items}} |
| Missing instalments, or no usable payment | Payment inputs unknown | {{M2.reg.excl_missing_installments}} + {{M2.reg.excl_no_usable_payment}} | {{M2.clf.excl_missing_installments}} + {{M2.clf.excl_no_usable_payment}} |
| Lead time above the larger of 100 days and the mean plus 12 standard deviations | Extreme against the development orders | {{M2.reg.excl_lead_days_outlier}} | — |
| Eligible orders | | {{M2.reg.eligible_orders}} | {{M2.clf.eligible_orders}} |

**Leakage rules.** A column may be a predictor only if its value exists at checkout. Delivery dates, carrier dates, the order status, the approval time and every review field are outcomes or later events and never predictors. Olist's estimated delivery date is known at checkout but is never used, because it is the output of the very process our lead-time model would replace. The seller's average review score on earlier orders uses only reviews answered before this order was placed.

**Missing values, skew and outliers.** Numeric gaps are filled with the training fold's median, and a missing-value indicator is added so the model can tell a filled value from a real one; categorical gaps become their own "Unknown" level. Skewed money, weight, volume, distance and day-count features are log-transformed (log of 1 plus the value); integer counts are left as they are. The long late tail of lead time is kept: very late orders are real customer experiences, so the regression predicts the log of 1 plus the lead time instead of trimming them.

**Encoding and scaling.** States and category are one-hot encoded; the linear and logistic models drop one reference level per variable so that the design matrix stays full rank, while trees keep every level. A level never seen in training is ignored at prediction time. Numeric features are standardised for the linear and logistic models only. All of this is learned on the training fold and applied unchanged to its validation fold.

**Test period.** For each task the newest 20% of eligible orders by purchase time, {{M2.reg.test_before_purge}} for lead time and {{M2.clf.test_before_purge}} for the alert, form the test period. It was held out before any exploration or feature work. Customers who also appear in development were removed from it ({{M2.reg.test_purged_repeat_customer_orders}} and {{M2.clf.test_purged_repeat_customer_orders}} orders), leaving {{M2.reg.test_orders}} and {{M2.clf.test_orders}} test orders, so the test measures new customers only. Development keeps {{M2.reg.development_orders}} and {{M2.clf.development_orders}} orders. The test was scored exactly once, after the models were frozen.
