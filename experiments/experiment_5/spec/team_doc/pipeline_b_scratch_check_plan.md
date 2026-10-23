# Quick probe report (plan v3 §0) · 2026-10-22

**Indicative only, never to be cited in the report or slides.** Run outside the repository (session scratch folder); afterwards nothing in experiment\_5 was newer than the start of the run, git status was identical, every pipeline node was still FRESH with the same run IDs, and no bonus\_round folder exists. Simplified features as in §0; seven-state population; regression at checkout (61,245 orders, cap 93.65 days), classification at carrier handover (61,258 orders); five s05 folds; validation scores. History coverage: about 96% of orders have seller history and 96% a route with at least 10 deliveries in the last three weeks.

## Results

**Regression (MAE, days; lower is better), mean ± SE over the folds**

| Model | s08 (full scope, reference) | Probe, accepted features | Probe, + new features | Gain from new features (paired) |
| --- | --- | --- | --- | --- |
| dummy | 6.4946 | 5.9794 ± 0.7158 | — | — |
| linear | 5.4701 | 5.2004 ± 0.6492 | 5.0399 ± 0.6107 | −0.1605 days (paired SE 0.0492), better in 5 of 5 folds |
| forest | 5.4434 | 5.0713 ± 0.6850 | 4.9998 ± 0.6228 | −0.0715 days (paired SE 0.0700), better in 4 of 5 |

R² rises from 0.040 to 0.086 (linear) and from 0.086 to 0.112 (forest).

**Classification at handover (AP; higher is better), mean ± SE over the folds**

| Model | s08 (checkout, full scope, reference) | Probe, accepted features | Probe, + new features | Gain from new features (paired) |
| --- | --- | --- | --- | --- |
| dummy (prevalence) | 0.1482 | 0.1380 ± 0.0198 | — | — |
| logistic | 0.2435 | 0.2391 ± 0.0341 | 0.2590 ± 0.0348 | +0.0199 (paired SE 0.0052), better in 5 of 5 |
| forest | 0.2544 | 0.2490 ± 0.0310 | 0.2723 ± 0.0328 | +0.0233 (paired SE 0.0064), better in 4 of 5 |

ROC-AUC rises from 0.631 to 0.651 (logistic) and from 0.642 to 0.667 (forest). The prevalence is lower in this population (0.138 vs 0.148), so compare AP as a multiple of prevalence: s08 logistic 1.6×, probe logistic with the new features 1.9×.

**Which new features carry the signal** (permutation importance on the validation folds, mean over folds):

- Regression: the seller's past dispatch days and the route one-hot are the strongest new features in the linear model, close behind distance; the route's last-three-week lead time comes next. The lateness rates add little.
- Classification: this order's own handover delay (late days, dispatch days) is the strongest new signal in both models, then the route one-hot. The prior lateness rates of the seller and the route add little.

**Missed-dispatch rule** (classification population, before the handover filter): orders never handed over: 429, of which 374 are detractors (87%). A wider rule, "shipping limit passed without handover" (never shipped or shipped late), flags 5,904 orders: 30.6% are detractors (vs 12.7% among the rest), catching 20.3% of all detractors.

## Reading

1. **The gains are real but modest.** The new features help in every or nearly every fold for both tasks, but none clears the agreed one-SE rule, because the fold SE (about 0.6 days, about 0.03 AP) is dominated by drift between folds, as in s06–s08.
2. **Narrowing the scope moves the numbers more than the features do.** Regression MAE drops from 5.47 (s08) to 5.20 just from the seven-state scope and the cap. That is an easier population, not a better model, and is not like-for-like with s08.
3. **What carries the signal is dispatch and route, not lateness rates.** Seller dispatch speed and route lead time help regression; this order's own dispatch delay helps classification, which supports predicting at handover. The rate features from Henry's design (F1) contribute least, so the full run could drop or simplify them.
4. **The missed-dispatch rule is a strong, simple alert.** Never-shipped orders are 87% detractors and can be flagged with no model.

## Decision for the team

Go on to the full v3 (expected gains of about this size, with the full fallbacks and weights), go on with a simplified v3 (dispatch, route and own-handover features only), or stop here and record the probe as a finding for s09.

# Bonus round — scratch check 01, plan v3

**Status: PLAN v3 · 2026-10-22 · for human review; not executed.** v3 = v2 + Henry's answers to 7a–7h + the team's three refinements: (1) prior lateness in both tasks, (2) classification predicts at carrier handover, (3) recent lead-time features for regression. Not taken: full-population rerun, gradient boosting, quantile models, recency windows (no new model family, as required by the professor). Counts marked "measured" come from pre-cutoff orders only.

## 0. Quick probe first (team request, 2026-10-22)

Before building v3 in full, a quick probe tests whether the idea carries signal and which features matter. The team then decides whether to go ahead with the full plan.

- **Where:** the session's own scratch folder, outside the repository, so nothing in experiment\_5 is written at all. Results come back as a short probe report in this doc. The numbers are indicative only and are never cited in the report or slides.
- **Simplified features:** F1 and F2 as plain means (seller: all earlier complete weeks; route: last three complete weeks, unweighted), with the overall mean when there is no history (no state fallbacks yet). F3 as in v3. Same leakage rule (§3), same population (§2), classification at handover.
- **Comparison:** per task, the accepted features vs the accepted features + every new feature, with plain linear/logistic and the forest on the five s05 folds: fold mean ± SE and paired gain.
- **Feature importance:** permutation importance on the validation folds (drop in MAE / AP when a feature is shuffled) and standardised linear coefficients, for the new features and the strongest accepted ones.
- **Missed-dispatch rule (classification):** how many detractors a simple rule catches, "shipping limit passed with no handover" (see §7, point 2), and its precision.
- **Not frozen:** the probe is exploratory. The freeze in §7 point 3 applies to the full run, if the team approves it.

## 1. Isolation: the accepted pipeline is not touched

- **Nothing existing changes.** No file under stages/, e5lib/, spec/, tests/, run\_pipeline.py, protocol.yaml or human\_decisions.yaml is written; no pipeline stage is rerun; no pipeline doc tab is edited. Everything decided here stays here (Henry, 7h).
- **One folder.** Script, results and summary only in experiments/experiment\_5/bonus\_round/scratch\_check\_01/. The pipeline never imports it.
- **Read-only inputs.** Accepted outputs (s02 records.csv.gz, s04 recipes.json, s05 folds) and the raw Olist CSVs, read with pandas; nothing is written back.
- **No test read.** Development rows on the s05 fold boundaries only; the test cohorts are never loaded, so the single test of s08 stays single.
- **Checks at the end.** git diff of stages/, e5lib/, spec/ and tests/ is empty; run\_pipeline.py status shows every node FRESH with the same run IDs; the s08 output hashes are unchanged.
- **Commit** only on the lead's go-ahead, as a separate commit touching bonus\_round/ only.

## 2. Population (both tasks)

| Rule | Detail | Measured |
| --- | --- | --- |
| Seven states | Customer state and primary seller state both in SP, MG, RJ, PR, RS, BA, SC; missing state removed | with the next rule: 81.3% of regression and 81.2% of classification pre-cutoff orders stay |
| Address | distance\_km\_max missing → removed | (included above) |
| Outlier cap (regression) | lead\_days > mean + 8 × SD with the s02 pre-cutoff mean and SD, no floor: 93.65 days (7a) | removes 32 orders |
| Warm-up | Orders purchased in the first six weeks (from 2017-01-01) removed after the history features are built | 61,224 regression, 61,777 classification orders remain |
| Handover (classification, every step) | The order must have a carrier handover date; orders whose review was answered at or before handover are removed (label already known) | 61,348 have a handover; 140 reviews before handover. The 429 never handed over are 87.2% detractors: reported separately, not hidden |

## 3. Leakage rule for every history feature

Calendar weeks, Monday to Sunday. A past order counts in the week its outcome became known: handover in the carrier-date week, logistics lateness and lead time in the customer-delivery week. An order uses only complete weeks before its **prediction week**, so every counted event finished before the prediction time (Henry, d and e). Regression predicts at checkout: its prediction week is the purchase week. Classification predicts at carrier handover in every step: its prediction week is the handover week. The current order's own estimated delivery date is never used (Q5, G-35; 7g).

## 4. Features

**Route (both tasks):** customer\_state + "->" + seller\_state, one-hot; drop-first for linear/logistic, every level kept for the forest (s04 convention, 7f).

**F1. Prior lateness (both tasks; refinement 1)**

| Feature | Past-order label | Order-level value | Fallback |
| --- | --- | --- | --- |
| Seller handover late rate, days | Late when carrier date > last shipping\_limit\_date; days = max(0, carrier − shipping limit) | Mean over all of the seller's handovers in earlier weeks | New seller: weighted 3-week mean of sellers in the same seller state |
| Route logistics late rate, days | Late when delivered > estimated date + max(0, seller handover late days); days = max(0, delivered − that date) | Weighted 3-week mean of the route: 0.5 × (w−1) + 0.3 × (w−2) + 0.2 × (w−3), weights renormalised over weeks with deliveries | Fewer than 10 route deliveries in the 3 weeks (7c): 0.7 × seller state's + 0.3 × customer state's weighted 3-week mean, then the overall one |

> **v3.1 amendment (side-chat conclusions, 2026-10-22, for team review; not executed).** The "Route logistics late rate, days" row above is withdrawn. Its label compares past orders with Olist's old estimated delivery date, and that date comes from the algorithm our regression would replace (train–serve skew). Replacement, promise-free: the route's recent lead days and dispatch days, and handover late against the shipping limit (kept). If a lateness label is wanted, define it against our own model's out-of-fold prediction plus a buffer. This supersedes the earlier answer to 7g. See section 8 for the other side-chat conclusions.

Weekly values: late rate = share late; lateness days = mean of max(0, days) over all orders (7b). Measured: seller handover late 9.2% (median 1.0 day when late), logistics late 7.1% (median 5.9 days when late).

**F2. Recent lead time (regression only; refinement 3)**

| Feature | Past-order value | Order-level value | Fallback |
| --- | --- | --- | --- |
| Seller dispatch days | carrier date − purchase time | Mean over all of the seller's handovers in earlier weeks | as for the seller rows of F1 |
| Route lead days | delivered − purchase time (the regression target of past orders) | Weighted 3-week mean of the route's weekly median lead days | as for the route rows of F1 |

**F3. At handover (classification; refinement 2).** Classification moves its prediction time from checkout to the moment the seller hands the parcel to the carrier, for the whole task (steps C1–C4), not just one feature. Every checkout feature is still known then, and the seller's dispatch on this order becomes known too: this order's handover late flag, handover late days and dispatch days (carrier − purchase; measured median 2.3 days). F1 is built at the handover week. Rationale (team): the checkout estimate assumes normal seller packing speed; a late dispatch is new information about the coming delivery and the review.

**Scaling**, fitted inside the folds: rates and flags standard-scaled only; all day counts log1p then standard-scaled.

## 5. Comparisons

Models at every step: dummy, plain s06 linear/logistic, forest, with the accepted s04 recipe plus the new columns; s05 fold membership; seed 42.

**Regression (prediction at checkout)**

| Step | Population | Features | Answers |
| --- | --- | --- | --- |
| S08 | full | accepted | published s08 fold scores (reference) |
| R0 | seven-state validation rows | accepted s08 models, trained on full data | scope alone, like-for-like base |
| R1 | bonus population | accepted | training on the narrowed scope |
| R2 | same | + route | route |
| R3 | same | + F1 prior lateness | refinement 1 |
| R4 | same | + F2 recent lead time | refinement 3 |

**Classification**

| Step | Prediction time | Features | Answers |
| --- | --- | --- | --- |
| S08 | checkout | accepted | published s08 fold scores (reference) |
| C0 | checkout | accepted s08 models (checkout), scored on the bonus handover rows | like-for-like base |
| C1 | carrier handover | accepted, retrained on the bonus handover population | narrowed scope and later prediction time |
| C2 | carrier handover | + route | route |
| C3 | carrier handover | + F1 prior lateness (built at the handover week) | refinement 1 |
| C4 | carrier handover | + F3 this order's dispatch facts | refinement 2 |

Per step: fold mean ± SE on every s01 metric; paired gain vs the previous step and vs R0/C0 (same rows), folds better; the one-SE verdict (s01 1.7). S08 against the last step is the headline but not like-for-like (different population, and for classification a different prediction time); R0/C0 against the last step is. Every classification step from C0 onward scores the same rows (orders with a handover).

## 6. Report (two pages, in bonus\_round/)

- **Page 1, models:** both ladders; how much the bonus round improves on s08 and by how much; what each refinement adds.
- **Page 2, lateness:** table by route, week and seller with customer and seller state (late rate and lateness days of each kind); which kind dominates late deliveries and detractors; what the business can do (seller dispatch vs carrier and route); what predicting at handover would mean for customer-service timing.

## 7. Points for the reviewers

1. **Weekly lead-time statistic (F2):** median of lead days per route-week, because lead time is skewed, while the lateness days of F1 use the mean (zero-inflated, 7b). Confirm or change.
2. **Handover population (classification):** the 140 orders reviewed at or before handover leave the task (label already known); the 429 never handed over cannot be scored at handover and are reported separately (87.2% detractors).
3. **Settings are frozen** once this plan is approved: one run, no tuning of weights, windows or thresholds on these folds.

**On point 2 (measured, bonus classification population before handover filtering):** the 429 orders never handed over hold 374 detractors, 4.2% of the 8,882. All but 3 sit in status processing (224) or invoiced (202), and only 3 were reviewed before the seller's shipping limit passed. The 140 orders reviewed before handover are 75% detractors. These are not lost: they are orders the seller failed to dispatch, and that failure is visible at the shipping limit. Suggested design: (1) the handover model scores every order the seller ships; (2) a simple rule, "shipping limit passed with no handover", raises an alert for the rest, with no model. The probe measures how many detractors the rule catches and its precision.

## 8. Side-chat conclusions (v3.1, for team review; not executed)

1. **Train–serve skew of the old estimated date.** Olist's order\_estimated\_delivery\_date comes from the algorithm our regression will replace. It stays out of every model, as now, and also out of every history label (amendment under F1).
2. **Expectation-gap curve (new descriptive check).** On pre-cutoff data only: the detractor rate against the actual delivery gap (days early or late against the promise shown), and against total lead days. Also count how many orders fall near a zero gap, because the old promises were generous. The curve is assumed to transfer to a new promise; the 57% "late" rate does not.
3. **Promise policy note.** If our regression sets the promise, show the prediction plus a buffer from the out-of-fold errors (for example, 90% delivered on time), not the raw prediction. The buffer then sets how many orders miss the promise, and so how many alerts a promise-date rule would raise.
4. **Limitation for s09.** Historical reviews reacted to the old promise; whether that behaviour transfers to a new promise is a hypothesis to monitor after launch.

# Plan v2 (superseded by v3 above; kept because the answers to 7a–7h sit on it)

**Status: PLAN v2 · 2026-10-22 · built from Henry's comments on v1 (below). Nothing runs until the open clarifications (section 7) are answered and the team confirms.** Counts marked "measured" were measured for this plan on pre-cutoff orders only.

## 1. Purpose

A sandbox ("bonus round"), outside the accepted pipeline, with two aims (Henry): (1) narrow the business problem to the main market so the data are less noisy; (2) try delivery-lateness features that could give the business usable insight. The result is compared with s08 to show whether, and by how much, it improves.

## 2. Ground rules (unchanged from v1)

- Code and results only in experiments/experiment\_5/bonus\_round/scratch\_check\_01/ (script, results, summary); never imported by the pipeline (Q6).
- Development rows only, on the s05 fold time boundaries; the test cohort is not read. If anything is later adopted, it goes through a change request and the single test stays single.
- Every feature uses only outcomes observed before the order's purchase week (section 4).
- est\_delivery\_days stays out of modelling (Q5, G-35): the old C2 (predicted lateness) is dropped.
- Same accepted s04 recipe plus the new columns; models: dummy, plain s06 linear/logistic and forest (Henry); seed 42; one-SE rule with paired gains beside it.

## 3. Population (both tasks)

| Rule | Detail | Measured (pre-cutoff) |
| --- | --- | --- |
| Seven states | Customer state and primary seller state both in SP, MG, RJ, PR, RS, BA, SC; missing state removed | together with the next rule: 62,542 of 76,925 regression orders (81.3%), 63,135 of 77,736 classification orders (81.2%) |
| Address | distance\_km\_max missing → removed | (included above) |
| Outlier cap (regression) | lead\_days > mean + 8 × SD, no 100-day floor (Q3) | 93.65 days with the s02 values (removes 32 orders), or 83.66 days if mean and SD are recomputed on the seven-state population (clarification a) |
| Warm-up | Orders purchased in the first six weeks (from 2017-01-01) are removed after the history features are built (Q2) | 61,224 regression and 61,777 classification orders remain |

## 4. Features

**Route (both tasks):** route = customer\_state + "->" + seller\_state, one-hot with drop-first (49 routes in the seven states).

**Two kinds of lateness, per past order** (Q1):

| Kind | Late when | Lateness days | Measured share late |
| --- | --- | --- | --- |
| Seller handover | carrier date > last shipping\_limit\_date of the order's items | max(0, carrier date − last shipping limit) | 9.2% (median 1.0 day when late) |
| Logistics | delivered to customer > estimated delivery date + max(0, seller handover late days) | max(0, delivered − that adjusted date) | 7.1% (median 5.9 days when late) |

**Weekly aggregation:** calendar weeks (Monday–Sunday). A past order counts in the week its outcome became known: the carrier-date week for handover, the delivery week for logistics. An order purchased in week w uses only weeks w−1 and earlier, so nothing after purchase leaks in (clarification e).

**Order-level features:**

| Feature | Definition | Fallback |
| --- | --- | --- |
| prior seller handover late rate, days | Mean over all of this seller's handovers in weeks ≤ w−1 | New seller: weighted 3-week mean of the sellers in the same seller state |
| prior route logistics late rate, days | Weighted 3-week mean of the route: 0.5 × (w−1) + 0.3 × (w−2) + 0.2 × (w−3); weights renormalised over weeks that have deliveries | Fewer than 20 route deliveries in the 3 weeks: clarification c |

Scaling, fitted inside the folds: rates standard-scaled only; days log1p then standard-scaled.

## 5. Comparisons (ladder per task)

| ID | Population | Features | Answers |
| --- | --- | --- | --- |
| S08 | full | accepted | the published s08 fold scores (reference) |
| B0 | seven-state validation rows | accepted s08 models, trained on the full population | how much of any change is the scope alone |
| B1 | seven-state, trained and scored | accepted | effect of training on the narrowed scope |
| B2 | same | + route | route |
| B3 | same | + prior seller handover lateness | seller |
| B4 | same | + prior route logistics lateness | logistics (full bonus model) |

Each row: dummy, linear/logistic, forest; fold mean ± SE on every s01 metric; paired gain vs the previous row and vs B0 (same rows), folds better, one-SE verdict. S08 vs B4 is shown as the headline but is not like-for-like (different populations); B0 vs B4 is.

## 6. Report (two pages)

- **Page 1, models:** the ladder above for both tasks, with how much the bonus round improves on s08, and by how much.
- **Page 2, lateness:** table by route, week and seller with customer state and seller state (late rate and lateness days for each kind); which kind dominates the late deliveries and the detractor rate; what the business can do (seller dispatch vs carrier and route actions).

## 7. Clarifications needed (Henry)

a. **Cap statistics:** mean and SD from the s02 pre-cutoff orders as today (cap 93.65 days) or recomputed on the seven-state population (83.66 days)?

b. **"Median" lateness:** about 91–93% of orders are on time, so the weekly median of lateness days is 0 almost everywhere. Proposal: weekly late rate = share late, weekly lateness days = mean of max(0, days) over all orders. Alternative: median days over the late orders only.

c. **Small routes:** only 31% of route-weeks reach 20 deliveries over three weeks, though those cover about 92% of orders. For the rest, proposal: use the customer state's weighted 3-week mean, then the overall one.

d. **Lateness features in regression too?** They are defined for both tasks above; confirm.

e. **Event week:** history counted in the week the outcome became known (as above), not the purchase week, so in-transit orders never leak. Confirm.

f. **Route one-hot for the forest:** drop-first as asked for linear/logistic; the s04 tree recipe keeps every level. Keep that convention?

g. **G-35:** the logistics label uses past orders' estimated dates (history only; the current order's promise is never a feature). Confirm this is acceptable under "keep est\_delivery\_days out of modelling".

h. **Scope change:** if adopted, the seven-state scope changes the problem statement (s01) and the population (s02) for both tasks, which would reopen every stage. Noted here so the decision is explicit.

# Plan v1 (superseded by v2 above; kept because the comments sit on it)

**Status: PLAN, for team comments · 2026-10-21 · nothing is run until the team confirms this plan.** Comment on any line; the open questions are at the end.

## 1. Why

Henry's comments on the s06 tabs: the models beat the dummy only modestly (regression MAE 5.4701 vs dummy 6.4946 days, R² 0.0911; classification AP 0.2435 vs prevalence 0.1482, ROC-AUC 0.6213; s08 candidates.csv). Did we miss a feature? A scratch check measures a few candidate changes on the folds before the recipe is frozen. After 8.5 (freeze) and the single test, any such change would be post hoc, so this is the last point to look.

## 2. Ground rules

- **Outside the pipeline.** No stage, output, card or accepted result changes. The script and its results live in a scratch folder (Q6) and are kept as the evidence for the decision.
- **Development rows only.** The five s05 folds; no row on or after either test cutoff is read (the same guard as the stages). The test cutoffs do not move.
- **Checkout-time only.** Every new feature uses only events that happened strictly before the order's purchase time; the order's own outcome is never counted (G-69 rule).
- **Same models and recipe.** The accepted s04 recipe and the plain s06 models (linear with log target; logistic; the forest as the best-mean comparator), same folds, seed 42. The baseline run must reproduce the s06 fold scores exactly (check).
- **Rule fixed before running.** A variant counts as material only if it passes the agreed one-SE rule against the baseline (s01 1.7, G-33). The paired fold gains are reported beside it as description, as in s06–s08.

## 3. Regression variants (task 1, lead days)

| ID | Change | Detail |
| --- | --- | --- |
| R0 | Baseline | Accepted s06 linear and forest |
| R1 | Tighter outlier cap (s02 2.9) | lead\_days > max(100, mean + 8 × SD), mean and SD from pre-cutoff orders (today 12 × SD). With the s02 values (mean 13.49, SD 10.02, audit.json), mean + 8 × SD = 93.65, so the 100-day floor becomes the limit (today 133.71). Measured for this plan: 29 pre-cutoff regression orders lie above 100 days. Scored two ways so the population change is not mistaken for a model gain: (a) on the capped validation rows, (b) on the original validation rows. |
| R2 | Seller delivery history | The primary seller's earlier orders delivered strictly before purchase: median lead days (new), delivered count and late share (already built in s02 as screening columns, never tried for regression, G-68) |
| R3 | Route delivery history | Median lead days of earlier orders on the same route (customer\_state × primary\_seller\_state), deliveries completed before purchase, shrunk toward the overall median when the route has few orders (Q4) |
| R4 | All together | R1 + R2 + R3 |

## 4. Classification variants (task 2, detractor)

| ID | Change | Detail |
| --- | --- | --- |
| C0 | Baseline | Accepted s06 logistic and forest |
| C1 | Route lateness ratio by month | For each route (customer\_state × primary\_seller\_state) and month: the share of earlier orders that were late, using only deliveries completed before the order's month starts (Q2). Shrunk toward the overall rate when the route has few orders (Q4); route order count added as log1p. Definition of "late": Q1 |
| C2 | Predicted lateness | Out-of-fold task 1 prediction minus the promised days (est\_delivery\_days), the G-69 design. Uses Olist's promised date, which G-35 keeps out of modelling (Q5) |
| C3 | All together | C1 + C2 |

## 5. Outputs

- Per variant and fold: primary metric (MAE / AP) and every s01 metric; mean ± SE; paired gain vs baseline with paired SE and folds better; the one-SE verdict.
- Coverage of each new feature (share of orders with history) and its fold-1 vs fold-5 distribution.
- A one-page summary posted as a reply to Henry's two threads.

## 6. What happens after

- **No variant material:** reply with the numbers, keep the accepted pipeline, and s09 reports the checkout-time ceiling as a limitation (the s03 gap: detractor rate 57.2% when late vs 9.5% on time). The combined review then decides model and threshold.
- **A variant is material:** the team decides whether to adopt it. Adoption is a change request: s02 (cap and columns; the cap also changes the test cohort, as 2.9 does today), s03 (screen and gate decision), s04, then s05–s08 rerun in order and are re-accepted (G-78: reopen the earliest affected stage). C2 also needs G-35 reversed.

## 7. Open questions for the team

1. **Q1 — what counts as "late" for the route ratio?** The proposal reads "delivered to the customer after the last shipping\_limit\_date of the order's items". shipping\_limit\_date is the seller's deadline to hand the parcel to the carrier (median about 6 days after purchase), not the delivery promise, so by that test 80.1% of pre-cutoff delivered orders are "late" and the ratio will barely differ between routes. Alternatives: (B) seller handed over late (carrier date after the last shipping limit): 9.1%; (C) delivered after the estimated delivery date: 8.7% (measured for this plan, pre-cutoff classification orders). Suggestion: compute all three and report each.
2. **Q2 — time window.** Previous complete calendar months only (suggested, simple and clearly before purchase), or every delivery completed strictly before the purchase second?
3. **Q3 — cap.** Confirm 8 × SD, knowing the 100-day floor binds, so in effect the cap is 100 days. If adopted it applies to development and test alike, as 2.9 does today.
4. **Q4 — small routes.** Shrink toward the overall rate with 20 pseudo-orders (suggested), or require a minimum route count?
5. **Q5 — C2 in scope?** It tests whether predicted lateness carries signal, but adopting it would reverse G-35 and make classification depend on task 1.
6. **Q6 — where the scratch code lives.** Suggested: experiments/experiment\_5/scratch/scratch\_check\_01/ (script, results, summary), committed with the decision as evidence, never imported by the pipeline.

# WITHDRAWN — Quick probe 2 (2026-10-22): not used, not reported

> **WITHDRAWN by the team, 2026-10-22.** Probe 2 is a failed exploration. Its features, numbers and conclusions are **not used for any decision** and must **not appear in the report, slides or s09**. It is kept only as a record, at the bottom of this tab. The current probe result is "Quick probe report (plan v3 §0)". The v3.1 amendment (no old-promise labels) rests on the side-chat reasoning, not on this probe.

**Indicative only, never to be cited in the report or slides.** Run outside the repository; afterwards git status was identical, no file in experiment\_5 was newer than the start of the run, every pipeline run ID was unchanged, and no bonus\_round folder exists. Same populations, folds and models as probe 1 (regression 61,245 orders at checkout; classification 61,258 at handover).

**Base** = probe 1's new features **minus every label that uses Olist's old estimated date** (v3.1 amendment): seller handover lateness against the shipping limit, seller dispatch days, route one-hot, route 3-week lead (regression), this order's handover facts (classification). Groups added to the base one at a time, then together:

- **D, drift:** platform order load (last 7 days vs the 4 weeks before), network median lead time and handover-late share of the last 14 days, peak season, Black Friday week, days to the next national holiday.
- **G, finer geography:** median lead time of the customer's 3-digit zip × seller state over the last 4 weeks (at least 10 deliveries, else the state route, else overall).
- **P, product (classification):** product and category review history before the prediction time (smoothed), shipping-limit spread and number of seller states in the order.
- **B, bias correction (regression):** predictions shifted by the training-fold median residual.

## Results (validation, mean over the five folds; gain vs base, paired)

| Task, model | Base | + D drift | + G zip3 route | + P product | + all | + B bias shift on base |
| --- | --- | --- | --- | --- | --- | --- |
| Regression, linear (MAE days) | 5.0358 | 5.4070 (worse by 0.37; worse in 3 of 5 folds) | 5.0269 (−0.009) | — | 5.3902 (worse) | 5.0383 (no change) |
| Regression, forest (MAE days) | 4.9638 | 5.0044 (worse by 0.04) | 4.9414 (−0.022, better in 4 of 5) | — | 4.9766 | 4.9579 (−0.006) |
| Classification, logistic (AP) | 0.2602 | 0.2561 (−0.004) | 0.2621 (+0.002) | 0.2615 (+0.001) | 0.2588 | — |
| Classification, forest (AP) | 0.2727 | 0.2745 (+0.002) | 0.2762 (+0.004) | 0.2738 (+0.001) | 0.2758 (+0.003, better in 5 of 5) | — |

No variant clears the one-SE rule, and apart from the forest + G no paired gain is larger than a few hundredths of a day or a few thousandths of AP.

## Reading

1. **Removing the old-promise labels costs nothing.** The base here (without them) scores the same as probe 1 with them: regression linear 5.0358 vs 5.0399, classification logistic 0.2602 vs 0.2590. The v3.1 amendment is free.
2. **Drift features hurt the linear model.** Platform load and network speed swing strongly between periods (Black Friday 2017 in fold 1–2 training); a linear model on a log target extrapolates them into later folds. The forest is neutral. The fold-to-fold level shift is not captured by these signals.
3. **Finer geography adds a little for the forest only** (about 0.02 days). It overlaps with distance and the state route.
4. **Product history adds almost nothing for classification** (64% of orders have any product review history before handover). Bad reviews here are driven mostly by delivery and order composition: n\_items, n\_sellers and this order's handover delay remain the strongest signals.
5. **Bias correction does nothing:** the training-fold median residual is close to zero once the route lead features are in.

**Overall:** with probe 1 and probe 2 together, the useful new signal is the dispatch, route and own-handover features from probe 1; the rest of the available data adds nothing measurable. These data look close to their ceiling for both tasks.

## Decision options (withdrawn with probe 2; not for team action)

(a) Stop here and record both probes as a finding for s09 (ceiling, drift, what carried signal). (b) Run a slimmed v3 with only the probe-1 features that carried signal, all promise-free: seller dispatch days, seller handover lateness against the shipping limit, route one-hot and route lead (regression), plus this order's handover facts (classification). The full v3 with every group is not recommended.
