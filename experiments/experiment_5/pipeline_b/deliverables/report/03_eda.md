## 3 Exploratory analysis highlights

EDA used development orders only (before each task's test cutoff), so it never saw test outcomes.

- **Lead time is right-skewed** with a long tail of very late orders: median {{A3.reg.lead_median_days}} days, mean {{A3.reg.lead_mean_days}}, 95th percentile {{A3.reg.lead_p95_days}}, skewness {{A3.reg.lead_skewness}}. The regression models therefore predict log(1 + days), and day-count inputs are log-transformed.
- **Late delivery drives bad reviews.** The detractor rate is {{A3.clf.detractor_rate_late}} for orders delivered after Olist's promised date against {{A3.clf.detractor_rate_on_time}} for orders on time (description only: lateness is known only after delivery and is never a predictor). This is why B predicts the review risk at handover, when the seller's delay is known.
- **Delivery speed depends on the route.** Median lead time ranges from {{A3.reg.median_lead_SP}} days for customers in SP to {{A3.reg.median_lead_AM}} days in AM, and late handover varies by seller state, which motivated B's route feature and route history (figure: late handover by route).
- **The business changed over time.** Volumes, speed and detractor share move across 2017–2018, including the November 2017 Black Friday peak ({{A3.trend.orders_2017_11}} orders against {{A3.trend.orders_2017_10}} in October), so all evaluation is time-ordered.
- **Imbalance.** Detractors are a minority ({{A3.clf.dev_prevalence}} of development orders; test share {{B9.clf.test_prevalence_B}} on B's rows), so accuracy is not used; we report average precision, precision and recall.

The EDA figures above come from Pipeline A's s03 stage (development orders, all states), read from A's frozen outputs at tag e5-A-frozen (evidence 3.1–3.8).
