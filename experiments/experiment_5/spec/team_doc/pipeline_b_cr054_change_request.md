# CR-054 / G-79 — Pipeline B = Pipeline A + this change request

**Status: DRAFT for team review · 2026-10-22.** Nothing is built and nothing is committed until the team approves this tab. On approval, the decision text in §3 goes into decision\_log.md as G-79 and the summary into CHANGELOG.md as CR-054 (text only; no pipeline A file or output changes). Overview chart: parent tab "Pipeline B (A + change request)".

## 1. Summary

Pipeline B narrows the business scope to the seven largest states, predicts the detractor risk at carrier handover instead of at checkout, and adds promise-free delivery-history features. Everything not listed in §4 is inherited from the accepted Pipeline A. Both pipelines are frozen before the test cohort is read; the test is read once for both; B is the delivered model.

## 2. Why

- **A sits near the checkout ceiling.** A's fold results beat the dummy only modestly in both tasks (s08 tabs), and the strongest driver of bad reviews, late delivery, is unknown at checkout (s03: detractor rate 57.2% when late vs 9.5% on time).
- **An exploratory check pointed to delivery history** (tab "Scratch check plan (probes)", outside both pipelines). It motivated B but is not part of B and is never cited: B's features are defined completely in §4, and B's own run produces all of B's evidence.
- **Business fit.** Customer service has no reason to act at checkout; acting when the parcel is handed over (or not handed over) gives a stronger signal and still leaves time to intervene.

## 3. Decision text (G-79, as it will go into the decision log)

> G-79 · Pipeline B is defined as Pipeline A plus the change list of CR-054 and nothing else. A is frozen at its s08 gate (8.5) without reading the test; B is built in pipeline\_b/ from A's accepted outputs and A's code, read-only, and goes through its own stage reviews and its own s08 gate. Both frozen pipelines are scored on the test cohort once, in one run, together with A on B's scope rows. B is the delivered model (report, slides, dashboard, business impact); A is reported as the baseline. Probes are never cited as results.

## 4. Change list (B differs from A only here)

| ID | Change | Definition |
| --- | --- | --- |
| B-C1 | Scope | Customer state and primary seller state both in SP, MG, RJ, PR, RS, BA, SC; orders with a missing state leave both tasks |
| B-C2 | Address | Orders with distance\_km\_max missing leave both tasks |
| B-C3 | Outlier cap (regression) | lead\_days > mean + 8 × SD, mean and SD of A's s02 pre-cutoff orders (93.65 days, audit.json values), no 100-day floor; replaces A's 2.9 rule inside B only |
| B-C4 | Warm-up | Orders purchased in the first six weeks of the data (from 2017-01-01) leave both tasks after the history features are built |
| B-C5 | Prediction time (classification) | At carrier handover. Orders never handed over, and orders whose review was answered at or before handover, leave the classification task |
| B-C6 | Route feature (both) | route = customer\_state + "->" + seller\_state, one-hot; drop-first for linear/logistic, every level for the forest (A's s04 convention) |
| B-C7 | Seller history (both) | Over the primary seller's earlier handovers: prior seller late rate (share of the seller's earlier handovers after their last shipping limit), prior seller late days (mean of max(0, carrier date − last shipping limit)) and prior seller dispatch days (mean of carrier date − purchase time). Mean over all complete weeks before the prediction week; a new seller takes the weighted 3-week mean of sellers in the same seller state |
| B-C8 | Route lead time (both) | Weighted 3-week mean (0.5, 0.3, 0.2 for weeks w−1, w−2, w−3) of the route's weekly median lead days; fewer than 10 route deliveries in the 3 weeks → 0.7 × seller state's + 0.3 × customer state's weighted 3-week mean, then the overall one |
| B-C8b | Route transit time (both; agreed by Henry, replaces logistics late) | Prior route transit days = delivered to customer − carrier date, i.e. the logistics part of the lead time with the seller's delay removed. Weighted 3-week mean of the route's weekly median, with the same weights and fallbacks as B-C8. Promise-free, so it measures logistics without Olist's old estimated date |
| B-C9 | This order at handover (classification) | Handover late flag, late days against the last shipping limit, dispatch days (carrier − purchase) |
| B-C10 | Missed-dispatch rule (classification) | An order whose shipping limit passes with no handover raises an alert; a rule, not a model, reported beside the classifier |
| B-C11 | Feature selection (both) | B4 ranks B's pool (A's task pool + B-C6 to B-C9 candidates, route as one feature) on B's pre-cutoff rows with A's ranking method (Spearman for regression, mutual information for classification) and keeps the top features reaching 99% of the cumulative share (A's G-70 threshold). A new feature that misses the cut is dropped and recorded |
| B-C12 | Feature dictionary (both) | feature\_dictionary\_B.csv per task (A's file is feature\_dictionary.csv): every B feature with name, scope (task), definition, formula, reason, transform, rank, share, kept or dropped with reason |
| B-C13 | Fold-by-fold result table (report) | One table per task with a row per validation fold (its date range, festival weeks marked) and a row for the test period, for A and B side by side. Generated from both pipelines' stored per-fold scores (A's existing outputs, nothing in A changes). Validation rows are labelled selection scores (G-10), because the models were chosen on them; the test row is the only unbiased estimate |

**Common rules for B-C7 to B-C9.** A past order counts in the week its outcome became known (carrier-date week for handover, delivery week for lead time). An order uses only complete weeks before its prediction week (purchase week for regression, handover week for classification). Rates are standard-scaled; day counts are log1p, then standard-scaled; both are fitted inside the folds. Olist's order\_estimated\_delivery\_date is used nowhere in B: not as a feature and not in any history label (train–serve skew: it comes from the algorithm our regression replaces).

**Inherited from A unchanged:** the 24-predictor contract and the s03 gate choices (classification adds the three adopted candidates), A's feature-selection method and threshold (B-C11 reapplies them to B's pool), s05 fold boundaries (rows filtered to B's population), model families and grids, the one-SE rule, metrics, calibration and threshold procedure, the human gates of s08, seed 42.

## 5. Stages of B

| B stage | Does | Reuses from A |
| --- | --- | --- |
| B2 | Applies B-C1 to B-C5 and builds the B-C6 to B-C9 columns | s02 records.csv.gz, raw tables |
| B4 | Ranks B's pool and applies the 99% rule (B-C11); builds the recipe with A's s04 code; writes feature\_dictionary\_B.csv (B-C12) | s04 recipes.json |
| B5 | Folds = A's folds restricted to B's rows, with class support checked | s05 folds.csv |
| B6–B7 | Training ladder and tuning | e5lib/training.py and tuning.py, read-only |
| B8 | Gate (B8.1–B8.4), freeze (B8.5); test, final fit and bundle in the shared run | e5lib/selection.py, read-only |
| B9, B10 | Conclusion and release on B, with the comparison table | s09 and s10 blueprints |

Each B stage is reviewed by the experiment lead; the team reviews B6 to B8 together at the B8 gate (as G-78 for A). The expectation-gap curve (scratch plan §8, item 2) is a descriptive check in B9.

## 6. Test protocol

- A is frozen at 8.5 and B at B8.5 before any test row is read.
- One run scores: A on A's test cohort; B on B's test cohort (A's cohort filtered by B-C1 to B-C5; cutoffs unchanged); A's frozen model on B's test rows (like-for-like).
- B's test cohort sizes and detractor counts are reported against G-46 and G-54; a shortfall is reported, the cutoff is never moved (as G-75).

## 7. Isolation and naming

- A lives in stages/ and is never edited after its freeze (tag e5-A-frozen). B lives in pipeline\_b/ with its own runner, spec/human\_decisions.yaml and tags (e5-B-sNN-accepted, e5-B-frozen); it imports A's code read-only, so A's foundation hash and run IDs never change.
- Names: "Pipeline A – baseline", "Pipeline B – improved". Evidence IDs: A keeps 6.2, 8.4 and so on; B uses B6.2, B8.4. Every manifest names its pipeline.
- Report, slides, dashboard: one comparison table, generated from both pipelines' outputs, is the only place A and B appear together; business impact and the dashboard cite B only.

**Logs and code.**

- **Shared logs, one entry each.** Only G-79 and CR-054 go into the experiment-level decision\_log.md and CHANGELOG.md. They are the governance records of experiment 5, not pipeline A outputs, and this decision changes A's own schedule (A stops at 8.5). Each entry is labelled "Pipeline B". Appending text rows changes no A code, stage, output or run ID: A's freshness check covers e5lib/ and run\_pipeline.py only.
- **B's own logs from then on.** Every later B change goes into pipeline\_b/CHANGELOG\_B.md and pipeline\_b/spec/decision\_log\_B.md (IDs B-CR-01, B-G-01, …), never into A's files.
- **Code.** B calls A's functions; it does not copy them. B's runner imports e5lib read-only for the inherited steps (factory, training, tuning, selection, metrics), so they are provably the same as A's. B's own package, pipeline\_b/e5b/, holds only what is new: B's filters, B's history features, the B4 ranking call, and B's stage runners. B's runner refuses to run if A's foundation hash differs from the one tagged e5-A-frozen, so A can never change underneath B.

## 8. Limitations to report

1. B covers about 81% of pre-cutoff orders (measured for the scratch plan); orders outside the seven states are out of scope, and the dashboard says so.
2. B was designed after probe 1 on the same folds, so its fold scores are mildly optimistic; the single test read is the fair comparison.
3. A predicts classification at checkout and B at handover: their comparison is on B's test rows, and the different prediction moments are stated.
4. Historical reviews reacted to Olist's old promise; whether that behaviour transfers to a promise set from our regression is a hypothesis to monitor after launch (s09).
5. If our regression sets the promise, it is shown as the prediction plus a buffer from out-of-fold errors, not the raw prediction (promise policy note).

## 9. Decisions for the team

1. **Approve the change list (§4)** as written, or amend it.
2. **Adoption rule, fixed before the test.** On folds, B is not expected to clear A by more than one fold SE (probe 1). Proposal: B is delivered as a business decision (scope and prediction time), provided its paired fold gain over A on B's rows is positive in at least 4 of 5 folds for each task; if not, the team revisits before the test is read. The test result is reported, never used to choose.
3. **Out-of-scope orders:** not served (proposed), or served by A as a documented fallback.
4. **Order of work:** A's combined review and freeze first, then B (proposed), or both in parallel.
