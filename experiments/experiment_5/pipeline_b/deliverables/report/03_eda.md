## 3 Exploratory analysis highlights

EDA used development orders only (before each task's test cutoff), so it never saw test outcomes.

- **Lead time is right-skewed** with a long tail of very late orders, so the regression models predict log(1 + days) and day-count inputs are log-transformed.
- **Late delivery drives bad reviews.** The detractor rate is far higher for orders delivered after Olist's promised date than for orders on time; this is why B predicts the review risk at handover, when the seller's delay is known.
- **Delivery speed depends on the route.** Lead time and late handover vary strongly by seller state and customer state, which motivated B's route feature and route history (figure: late handover by route).
- **The business changed over time.** Volumes, speed and detractor share move across 2017–2018, including the November 2017 Black Friday peak, so all evaluation is time-ordered.
- **Imbalance.** Detractors are a minority (test share {{B9.clf.test_prevalence_B}} on B's rows), so accuracy is not used; we report average precision, precision and recall.

Open item: the EDA figures and rates from Pipeline A's s03 stage are not yet in B's register; they will be added before the report is final.
