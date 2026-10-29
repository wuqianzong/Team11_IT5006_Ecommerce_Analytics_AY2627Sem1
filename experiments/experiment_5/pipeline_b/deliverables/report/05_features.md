## 5 Features, multicollinearity and selection

Every feature has a definition, a time window and a reason. Correlated and nested features are removed by a stated rule before selection, and a ranking rule then keeps the smallest set that carries 99% of the ranked signal. Both steps run on development orders only, never on the test period.

### 5.1 Pipeline A's predictor pool

Pipeline A starts from 24 predictors that are all known at checkout, grouped as follows:

- **Basket:** counts of items, products, sellers and categories.
- **Price and freight:** total price, total freight and the freight-to-price ratio.
- **Physical size:** total weight and volume, with the share of items whose size is missing.
- **Product:** the primary category, with the share of items whose category is missing.
- **Geography:** customer state, primary seller state, the largest seller-to-customer distance with the share of items whose distance is missing, and the share of items shipped across a state border.
- **Calendar:** purchase month, day of week and hour.
- **Payment:** main payment type, largest number of instalments and number of payment methods.

The alert adds three candidates kept after the exploratory screening: the primary product's photo count and description length, and the seller's average review score on earlier orders. Skewed money, size, distance and day-count features are log-transformed, as described in section 3.

### 5.2 Pipeline B's new features

The new features describe how this seller and this route have delivered recently, measured only on other orders. None uses Olist's estimated delivery date, so none inherits the old promise.

*Table 6. Pipeline B's new features.*

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

*Figure: Share of rows with their own seller and route history, by quarter (F.reg.history_coverage).*

**Grounding.** Logistics performance is studied alongside ratings and sales on e-commerce platforms (Deshpande and Pendem, 2023); we cite this for the question it studies, not for any effect or direction. The reason to expect the seller's history to matter comes from our own development data: late delivery goes with more detractors, and the share of late handovers differs between seller states and routes (section 4). Our seller features measure the logistics performance of the seller who ships the order. For the route features we found no audited source, so their use rests on an operational assumption: a route that was slow last week is likely to be slow this week. Section 7 tests that assumption against the data instead of taking it for granted.

### 5.3 Multicollinearity check

Strongly correlated predictors make linear coefficients unstable and split importance between partners, even when accuracy is unaffected. The check uses only stored outputs:

- **Pipeline A's pool.** The exploratory stage computed pairwise correlations and a variance inflation factor (VIF) for each numeric predictor on development orders. A pair is flagged above an absolute correlation of {{A3.corr_cut}}, and a predictor above a VIF of {{A3.vif_cut}}. No predictor reached the VIF cut-off in either task (appendix J). One pair was identical on every development order, the missing-weight and missing-volume shares; the lower-ranked of the two was dropped.

*Table 7. Pipeline A's predictor pairs above the correlation cut-off.*

{{table:A3.reg.collinear_pairs}}

- **Pipeline B.** The route determines both the customer state and the seller state: every route level fixes both, so their one-hot columns are sums of the route's columns. Keeping all three would make the linear design matrix rank-deficient, so the two state columns are dropped whenever the route is kept. The same step drops the missing-distance share, which is constant because every kept order has a distance, and the duplicate pair found in Pipeline A's pool.

*Table 8. Features removed by Pipeline B's reduction step, lead time.*

{{table:B4.reg.reduction}}

- **Every fold.** After the drops, the linear design matrix is full rank in every training fold, so plain least squares and unpenalised logistic regression have unique coefficients. The condition number shows how close the columns come to collinearity (appendix C).
- **What was not measured.** Correlation and VIF were not computed for the new history features. They are averages of related quantities (for example, a seller's late-handover rate and late days), so some correlation among them is likely. The full-rank check rules out exact dependence but not strong correlation, and the stored outputs cannot show more. We state this as a limit (section 10) rather than run new analysis.

### 5.4 Feature selection

Selection ranks each candidate by its association with the target on development orders: the absolute Spearman correlation for lead time and mutual information for the alert. It then keeps features in rank order until they reach 99% of the cumulative score.

*Figure: Feature ranking and the 99% rule, lead time (F.reg.selection) and detractor alert (F.clf.selection).*

Ranking once on all development orders is a design choice, and it makes the validation scores slightly optimistic, because the folds' validation orders helped choose the features; the test period is unaffected. To check how much the choice depends on the rows, the ranking was repeated inside each training fold.

- **Lead time:** the selected sets overlap by {{B12.reg.rank_jaccard_min}} to 1.00 (mean {{B12.reg.rank_jaccard_mean}}), and {{B12.reg.rank_always}} of the {{B12.reg.rank_selected}} selected features are kept in every fold.
- **Detractor alert:** overlap {{B12.clf.rank_jaccard_min}} to 1.00 (mean {{B12.clf.rank_jaccard_mean}}), weakest in fold 1, which has the fewest training orders; {{B12.clf.rank_always}} of {{B12.clf.rank_selected}} are kept in every fold.

For lead time the ranking is stable: the route and its recent speed, distance and the interstate share stay at the top in every fold. For the alert the ranks move a lot between folds, even for features ranked near the top on all development orders, and several of them drop out of one fold's selection; the early folds, with the fewest training orders, move most. A likely reason, not tested here, is that mutual information estimated on a minority-class target varies more on small samples. The selected set for the alert should therefore be read as a reasonable choice, not a uniquely determined one (section 10; ranking charts by fold in appendix I).

Every new feature passed the cut in both tasks where it applies. The full list of selected features, with transforms and ranks, is in appendix D, beside Pipeline A's, so the two pipelines can be compared feature by feature.
