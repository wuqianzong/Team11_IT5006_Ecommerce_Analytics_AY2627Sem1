## 5 Features, multicollinearity and selection

Every feature has a definition, a time window and a reason. Correlated and nested features are removed by a stated rule before selection, and a ranking rule then keeps the smallest set that carries 99% of the ranked signal. Both steps run on development orders only, never on the test period.

### 5.1 Pipeline B's feature set

Pipeline B's new features describe how this seller and this route have delivered recently, measured only on other orders. None uses Olist's estimated delivery date, so none inherits the old promise. Pipeline B adds the route (seller state to customer state); the seller's prior late-handover rate, late-handover days and dispatch days, over all complete weeks before the prediction week; and the route's recent delivery days and carrier transit days, a weighted mean of the last three complete weeks (0.5, 0.3, 0.2). For the alert it adds two facts known at handover: whether, and by how many days, this order's handover missed its shipping limit, and the days from purchase to handover. Table K5 gives each feature's definition, window and reason. Table 3 gives the reason for each family of features, old and new.

*Table 3. Feature families: when each is known and why it is included. The reasons are predictive hypotheses that selection and the models test, not causes.*

| Feature family | Examples | Available at | Why included |
| --- | --- | --- | --- |
| Geography and distance | Customer and seller state, route, distance, interstate share | Checkout | Longer and interstate journeys need more carrier legs; lead time rises with distance (section 4) |
| Route history (Pipeline B) | Route's recent delivery days and carrier transit days | Checkout, from complete weeks before | A route slow in recent weeks is likely slow now; tracks the current period's speed without Olist's estimate |
| Seller history (Pipeline B) | Seller's prior late-handover rate, late-handover days, dispatch days | Checkout, from complete weeks before | A seller who dispatched late before is likely to again; late handovers differ between sellers and states (section 4) |
| Basket complexity | Items, products, sellers and categories in the order | Checkout | More items and sellers mean more picking and separate parcels, and more chances for one part to go wrong |
| Price, freight and size | Price, freight, freight-to-price ratio, weight, volume, category | Checkout | Freight reflects distance and parcel size; heavy or bulky parcels may travel by slower services |
| Payment and calendar | Payment type, instalments, purchase hour, weekday and month | Checkout | Boleto payments clear before dispatch; weekend orders wait for the next working day; seasonal peaks load carriers |
| Handover lateness (alert only) | Missed shipping limit (yes or no, days late), days from purchase to handover | Carrier handover | A late handover is the first sign of a late delivery, and late delivery goes with more detractors (section 4) |

A seller with no earlier handovers takes the recent mean of sellers in the same state. A route with fewer than ten deliveries in the last three weeks takes a blend of its seller state's and customer state's recent means, and then the overall mean. Most rows soon have their own seller and route history (figure below), which is why the first six weeks are used as a warm-up and not modelled.

*Figure: Share of rows with their own seller and route history, by quarter (F.reg.history_coverage).*

**Grounding.** Logistics performance is studied alongside ratings and sales on e-commerce platforms (Deshpande and Pendem, 2023; cited for the question only). The reason to expect the seller's history to matter comes from our own data: late delivery goes with more detractors, and late handovers differ between seller states and routes (section 4). For the route features we found no audited source, so they rest on an operational assumption, that a route slow last week is likely slow this week, which section 7 tests.

**Inherited from Pipeline A.** Pipeline B starts from Pipeline A's 24 checkout predictors (the geography, basket, price and payment families of Table 3; formula and reason for each in Table D3). For the alert Pipeline A added three candidates kept after the exploratory screening: the primary product's photo count and description length, which set the customer's expectations, and the seller's average review score on earlier orders, which summarises the seller's past service. Skewed money, size, distance and day-count features are log-transformed, as described in section 3.

### 5.2 Multicollinearity check

Strongly correlated predictors make linear coefficients unstable and split importance between partners, even when accuracy is unaffected. The check uses only stored outputs:

- **Pipeline B.** The route determines both the customer state and the seller state: every route level fixes both, so their one-hot columns are sums of the route's columns. Keeping all three would make the linear design matrix rank-deficient, so the two state columns are dropped whenever the route is kept. The same step drops the missing-distance share, which is constant because every kept order has a distance, and the duplicate pair found in Pipeline A's pool (appendix J; Table K6). After encoding, a missing-value indicator identical to another column is also dropped (weight for the alert, volume for lead time).

- **Every fold.** After the drops, the linear design matrix is full rank in every training fold, so plain least squares and unpenalised logistic regression have unique coefficients. The condition number shows how close the columns come to collinearity (appendix C).

Pipeline A's pool, the inherited base, passed a correlation and variance-inflation check; correlation among the new history features was not measured (appendix J; section 10).

### 5.3 Feature selection

Selection ranks each candidate by its association with the target on development orders: the absolute Spearman correlation for lead time and mutual information for the alert. It then keeps features in rank order until they reach 99% of the cumulative score.

*Figure: Feature ranking and the 99% rule, lead time (F.reg.selection) and detractor alert (F.clf.selection).*

Ranking once on all development orders is a design choice, and it makes the validation scores slightly optimistic, because the folds' validation orders helped choose the features; the test period is unaffected. Repeating the ranking inside each training fold measures how much it depends on the rows (appendix I).

For lead time the ranking is stable: the route and its recent speed, distance and the interstate share stay at the top in every fold. For the alert the ranks move a lot between folds, most in the early folds with the fewest training orders, so its selected set is a reasonable choice, not a uniquely determined one (section 10; charts by fold in appendix I).

Every new feature passed the cut in both tasks where it applies. The full list of selected features, with transforms and ranks, is in appendix D, beside Pipeline A's, so the two pipelines can be compared feature by feature.
