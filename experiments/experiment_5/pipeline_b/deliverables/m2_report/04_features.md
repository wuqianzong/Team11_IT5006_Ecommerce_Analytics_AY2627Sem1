## 4 Feature engineering and selection

Every feature has a definition, a reason and a time window: all are known at checkout. Correlated features are removed by a stated rule before selection, and a ranking rule then keeps the smallest set that carries 99% of the ranked signal. Both steps use development orders only.

**Predictor pool.** We start from 24 predictors known at checkout, grouped by what they describe (formulas in appendix B):

- **Basket:** counts of items, products, sellers and categories. More sellers mean more parcels that must all arrive.
- **Price and freight:** total price, total freight and the freight-to-price ratio. Freight reflects distance and size as the seller priced them.
- **Physical size:** total weight and volume, with the share of items whose size is missing.
- **Product:** the primary category, with the share of items whose category is missing.
- **Geography:** customer state, primary seller state, the largest seller-to-customer distance with the share of items whose distance is missing, and the share of items shipped across a state border.
- **Calendar:** purchase month, day of week and hour, for seasonal and weekly load.
- **Payment:** main payment type, largest number of instalments and number of payment methods.

The alert adds three candidates kept after the exploratory screening: the primary product's photo count and description length, and the seller's average review score on earlier orders. Logistics performance is studied alongside ratings and sales on e-commerce platforms (Deshpande and Pendem, 2023); we cite this for the question it studies, not for any effect, and test each feature's use in our own data.

**Multicollinearity check.** Strongly correlated predictors make linear coefficients unstable and split importance between partners. Pairwise correlations and the variance inflation factor (VIF) of each numeric predictor were computed on development orders. A pair is flagged above an absolute correlation of {{A3.corr_cut}}, and a predictor above a VIF of {{A3.vif_cut}}. No predictor reached the VIF cut-off in either task (appendix B). One pair was identical on every development order, the missing-weight and missing-volume shares, and the lower-ranked of the two was dropped.

*Table 3. Predictor pairs above the correlation cut-off, lead time.*

{{table:A3.reg.collinear_pairs}}

**Selection.** Each remaining candidate is ranked by its association with the target on development orders: the absolute Spearman correlation for lead time and mutual information for the alert. Features are kept in rank order until they reach 99% of the cumulative score, which keeps 18 of the lead-time candidates and 19 of the alert candidates (full rankings in appendix B). Distance, customer state and the interstate share lead for lead time; the seller's earlier review score, freight and the freight ratio lead for the alert.

*Figure: Selection ranking and the 99% rule, lead time (F.M2.reg.selection_cumulative) and detractor alert (F.M2.clf.selection_cumulative).*

Ranking once on all development orders is a design choice: it makes the validation scores slightly optimistic, because the folds' validation orders helped choose the features. The test period is unaffected (section 7).
