## 7 Insights and limitations

**What the business can do now.**

- **Fulfilment:** show a delivery range, not a single date, built from the lead-time prediction and its error on recent orders. The model already beats a fixed median promise, and the range keeps the promise one the operation can meet (section 1).
- **Customer service:** use the alert as a ranking, not a rule. Review the highest-risk orders first up to the daily capacity, rather than every order above 1/6, and re-set the threshold as the detractor share moves.
- **Seller management:** orders split across several sellers and sellers with poor past reviews carry more detractor risk; these are the places to look first.

**Limitations.**

- **What checkout cannot see.** The strongest driver of a bad review, a late delivery, is unknown at checkout, which keeps the alert weak; a later prediction moment, once the order is dispatched, would know more.
- **Weak fit for lead time.** R² is low: much of the variation in delivery time depends on events after checkout.
- **The threshold did not transfer.** The test period had fewer detractors, so the frozen 1/6 alerted too often and cost more than no alert; the threshold needs monitoring and re-setting.
- **Optimistic validation.** Features were ranked once on all development orders, so validation scores are slightly optimistic; the test is unaffected.
- **Grid edge.** The forest's best configurations sit at the edge of the fixed grid; the grid was not extended, because the selection rule keeps the plain models either way.
- **Associations, not causes.** Importance and coefficients describe the frozen models, not the effect of changing a feature.
