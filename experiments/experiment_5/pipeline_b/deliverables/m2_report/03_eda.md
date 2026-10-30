## 3 Exploration highlights

Exploration used development orders only, so it never saw a test outcome. Each fact below led to a design decision. Patterns are described, not explained: the data does not record why a route is slow or why a customer is unhappy.

**Lead time is right-skewed.** Half of the orders arrive within {{A3.reg.lead_median_days}} days, but a long tail of very late orders pulls the mean to {{A3.reg.lead_mean_days}} days; the 95th percentile is {{A3.reg.lead_p95_days}} and the skewness {{A3.reg.lead_skewness}}. A model fitted on raw days would chase the tail, so the regression predicts the log of 1 plus the lead time.

*Figure: Lead-time distribution, development orders (F.A3.reg.target_kde).*

**Late delivery and bad reviews go together.** Among orders delivered after Olist's promised date the detractor rate is {{A3.clf.detractor_rate_late}}; among orders delivered on time it is {{A3.clf.detractor_rate_on_time}}. Lateness is known only after delivery, so it is never a predictor, but it bounds what a checkout alert can achieve.

**Speed depends on where the order goes.** Median lead time ranges from {{A3.reg.median_lead_SP}} days for customers in SP to {{A3.reg.median_lead_AM}} days in AM, so customer and seller state enter the model beside the distance.

**The business changes over time.** Order volume, lead time, the late-delivery rate and the detractor rate all move across 2017 and 2018. A model evaluated on a random split would mix these periods and train on the future; every evaluation here is time-ordered instead.

*Figure: Monthly orders and lead time (F.A3.reg.outcome_trends) and monthly detractor rate (F.A3.clf.outcome_trends), development orders.*

**Detractors are a minority** ({{A3.clf.dev_prevalence}} of development orders), so we judge the alert by average precision against the detractor share and set its threshold from error costs.
