## 5 Features, multicollinearity and selection

Every feature has a definition, a time window and a reason. Correlated and nested features are removed by a stated rule before selection, and a ranking rule then keeps the smallest set that carries 99% of the ranked signal. Both steps run on development orders only, never on the test period.

### 5.1 Pipeline B's feature set

Pipeline B's new features describe how this seller and this route have delivered recently, measured only on other orders. None uses Olist's estimated delivery date, so none inherits the old promise. Pipeline B adds the route (seller state to customer state); the seller's prior late-handover rate, late-handover days and dispatch days, over all complete weeks before the prediction week; and the route's recent delivery days and carrier transit days, a weighted mean of the last three complete weeks (0.5, 0.3, 0.2). For the alert it adds two facts known at handover: whether, and by how many days, this order's handover missed its shipping limit, and the days from purchase to handover. Table K5 gives each feature's definition, window and reason.

A seller with no earlier handovers takes the recent mean of sellers in the same state. A route with fewer than ten deliveries in the last three weeks takes a blend of its seller state's and customer state's recent means, and then the overall mean. Most rows soon have their own seller and route history (figure below), which is why the first six weeks are used as a warm-up and not modelled.

*Figure: Share of rows with their own seller and route history, by quarter (F.reg.history_coverage).*

**Grounding.** Logistics performance is studied alongside ratings and sales on e-commerce platforms (Deshpande and Pendem, 2023; cited for the question only). The reason to expect the seller's history to matter comes from our own data: late delivery goes with more detractors, and late handovers differ between seller states and routes (section 4). For the route features we found no audited source, so they rest on an operational assumption, that a route slow last week is likely slow this week, which section 7 tests.

**Inherited from Pipeline A.** Pipeline B also starts from Pipeline A's 24 checkout predictors: basket counts, price and freight, physical size, product category, geography (customer and seller state, distance, interstate share), purchase calendar and payment. For the alert Pipeline A added three candidates kept after the exploratory screening: the primary product's photo count and description length, and the seller's average review score on earlier orders. Skewed money, size, distance and day-count features are log-transformed, as described in section 3.

### 5.2 Multicollinearity check

Strongly correlated predictors make linear coefficients unstable and split importance between partners, even when accuracy is unaffected. The check uses only stored outputs:

- **Pipeline B.** The route determines both the customer state and the seller state: every route level fixes both, so their one-hot columns are sums of the route's columns. Keeping all three would make the linear design matrix rank-deficient, so the two state columns are dropped whenever the route is kept. The same step drops the missing-distance share, which is constant because every kept order has a distance, and the duplicate pair found in Pipeline A's pool (below; Table K6). After encoding, a missing-value indicator identical to another column is also dropped (weight for the alert, volume for lead time).

- **Every fold.** After the drops, the linear design matrix is full rank in every training fold, so plain least squares and unpenalised logistic regression have unique coefficients. The condition number shows how close the columns come to collinearity (appendix C).

- **Pipeline A's pool, the inherited base.** The exploratory stage computed pairwise correlations and a variance inflation factor (VIF) for each numeric predictor on development orders. A pair is flagged above an absolute correlation of {{A3.corr_cut}}, and a predictor above a VIF of {{A3.vif_cut}}. No predictor reached the VIF cut-off in either task (appendix J). One pair was identical on every development order, the missing-weight and missing-volume shares; the lower-ranked of the two was dropped (Table K7).

- **What was not measured.** Correlation and VIF were not computed for the new history features, which are averages of related quantities; the full-rank check rules out exact dependence but not strong correlation (section 10).

### 5.3 Feature selection

Selection ranks each candidate by its association with the target on development orders: the absolute Spearman correlation for lead time and mutual information for the alert. It then keeps features in rank order until they reach 99% of the cumulative score.

*Figure: Feature ranking and the 99% rule, lead time (F.reg.selection) and detractor alert (F.clf.selection).*

Ranking once on all development orders is a design choice, and it makes the validation scores slightly optimistic, because the folds' validation orders helped choose the features; the test period is unaffected. To check how much the choice depends on the rows, the ranking was repeated inside each training fold.

- **Lead time:** the selected sets overlap by {{B12.reg.rank_jaccard_min}} to 1.00 (mean {{B12.reg.rank_jaccard_mean}}), and {{B12.reg.rank_always}} of the {{B12.reg.rank_selected}} selected features are kept in every fold.
- **Detractor alert:** overlap {{B12.clf.rank_jaccard_min}} to 1.00 (mean {{B12.clf.rank_jaccard_mean}}), weakest in fold 1, which has the fewest training orders; {{B12.clf.rank_always}} of {{B12.clf.rank_selected}} are kept in every fold.

For lead time the ranking is stable: the route and its recent speed, distance and the interstate share stay at the top in every fold. For the alert the ranks move a lot between folds, most in the early folds with the fewest training orders, so its selected set is a reasonable choice, not a uniquely determined one (section 10; charts by fold in appendix I).

Every new feature passed the cut in both tasks where it applies. The full list of selected features, with transforms and ranks, is in appendix D, beside Pipeline A's, so the two pipelines can be compared feature by feature.
