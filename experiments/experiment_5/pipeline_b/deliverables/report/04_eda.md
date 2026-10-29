## 4 Exploratory analysis

Exploration used development orders only, before each task's test period, so it never saw a test outcome. Each fact below led to a decision in the design; the table at the end lists them side by side. Patterns are described, not explained: the data does not record why a route is slow or why a customer is unhappy.

**Lead time is right-skewed.** Half of the orders arrive within {{A3.reg.lead_median_days}} days, but a long tail of very late orders pulls the mean above the median: median {{A3.reg.lead_median_days}} days, mean {{A3.reg.lead_mean_days}}, 95th percentile {{A3.reg.lead_p95_days}}, skewness {{A3.reg.lead_skewness}}. A model fitted on raw days would chase the tail, so the regression predicts the log of 1 plus the lead time, and day-count inputs are log-transformed the same way.

*Figure: Lead-time distribution, development orders (F.A3.reg.target_kde).*

**Late delivery and bad reviews go together.** Among orders delivered after Olist's promised date, the detractor rate is {{A3.clf.detractor_rate_late}}; among orders delivered on time it is {{A3.clf.detractor_rate_on_time}}. Lateness is known only after delivery, so it is never a predictor. But it explains why an alert made at checkout has little to work with, and why Pipeline B waits for carrier handover, when the seller's part of any delay is already known.

**Speed depends on the route.** Median lead time ranges from {{A3.reg.median_lead_SP}} days for customers in SP to {{A3.reg.median_lead_AM}} days in AM, and the share of late handovers differs between seller states and routes. A single distance number does not capture this, which motivated the route feature and the route's recent speed.

*Figure: Late handover by route (F.reg.lateness_by_route).*

**The business changes over time.** Order volume, lead time, the late-delivery rate and the detractor rate all move across 2017 and 2018. November 2017, with Black Friday, had {{A3.trend.orders_2017_11}} orders against {{A3.trend.orders_2017_10}} in October, and delivery slowed in the weeks after. A model evaluated on a random split would mix these periods; every evaluation here is time-ordered instead.

*Figure: Monthly orders and lead time (F.A3.reg.outcome_trends) and monthly detractor rate (F.A3.clf.outcome_trends), development orders.*

**Detractors are a minority.** {{A3.clf.dev_prevalence}} of development orders are detractors (on Pipeline B's test orders, {{B9.clf.test_prevalence_B}}), so a model that never alerts would look accurate. We report average precision against the detractor share and set the alert threshold from error costs.

**Predictors overlap little.** A first look at pairwise correlations among the numeric predictors found one identical pair and no other pair above the cut-off; section 5.2 checks this formally with the variance inflation factor.

**The newest weeks may be incomplete.** The data ends in late 2018. The slowest deliveries for orders placed in the final weeks may not have arrived when the data was extracted, so the test period, the newest fifth of orders, may under-represent very late deliveries and make its error look slightly better (section 10).

*Table 5. Exploratory findings and the decisions they led to.*

| What the data shows | Decision it led to | Section |
| --- | --- | --- |
| Right-skewed lead time with a long late tail | Log target and log day counts; keep the tail | 3 |
| Late delivery and bad reviews go together | Alert at carrier handover; lateness never a predictor | 1, 6 |
| Speed differs by route and state | Route feature and recent route speed; seven-state scope | 5, 6 |
| Volumes and outcomes change over time | Time-ordered folds and test period | 6 |
| Detractors are a minority | Average precision; cost-based threshold; class weight in the grid | 1, 6 |
| One identical predictor pair | Dropped before selection | 5 |
