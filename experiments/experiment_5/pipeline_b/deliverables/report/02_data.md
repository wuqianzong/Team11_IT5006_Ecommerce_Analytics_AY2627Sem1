## 2 Dataset and preprocessing

**Data.** The Canvas copy of the Olist dataset: nine tables (orders, items, payments, reviews, customers, sellers, products, geolocation, category translation), joined into one row per order. Customer-level logic (test separation, repeat customers) uses `customer_unique_id`, never `customer_id`.

**Leakage control.** Every column was audited for the time it becomes known. Delivery dates and review dates are outcomes and never predictors. Olist's own estimated delivery date is not used anywhere in B (it comes from the algorithm our regression replaces). Carrier handover dates appear in two ways only: as past events of other orders (seller and route history, using complete weeks before the prediction week), and, for B's classifier, as this order's own handover facts, because B predicts at handover (the brief allows features known "at the moment it ships").

**Test period.** Each task's newest 20% of orders is the test cohort, held out before EDA and feature work; development customers who reappear in the test are removed. Anything learned from data (imputation, encoding, scaling, calibration) is fitted inside the training folds.

**B's population.** Starting from A's {{B2.reg.dev_rows_A}} regression development orders, B removes orders outside the seven states ({{B2.reg.removed_state}}), orders without a distance ({{B2.reg.removed_distance}}), extreme lead times above mean + 8 SD of B's own rows ({{B2.reg.removed_cap}}), and the first six weeks used to warm up the history features ({{B2.reg.removed_warmup}}). Classification also removes orders never handed over and orders reviewed before handover.

**B's new features** (all free of Olist's promise): the route (seller state → customer state); the seller's earlier late-handover rate, late days and dispatch days; the route's recent delivery days and carrier transit days (weighted mean of the last three complete weeks, with state fallbacks); and, for classification, this order's handover lateness and dispatch days.
