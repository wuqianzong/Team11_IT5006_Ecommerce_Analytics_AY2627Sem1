# s01 Problem — implementation review

**ACCEPTED · round 2 · 2026-10-18** · run `20261018T150315Z` · commit `453896d` (tag `e5-s01-accepted`) · all 9 rows Approved · 7 checks, all PASS · approved by the experiment lead. This tab is frozen as the record of the s01 review; s02 may start.

## Current (round 2)

### Coverage

| ID | Solution step | Coverage | Checks | Review |
| --- | --- | --- | --- | --- |
| 1.1 | Tasks and prediction time | IMPLEMENTED | — | Approved |
| 1.2 | Stakeholders and action | IMPLEMENTED | — | Approved |
| 1.3 | Targets and populations | IMPLEMENTED | PASS | Approved |
| 1.4 | Metrics | IMPLEMENTED | PASS | Approved |
| 1.5 | Cost assumption | IMPLEMENTED | PASS | Approved |
| 1.6 | Model families | IMPLEMENTED | — | Approved |
| 1.7 | Decision rule | IMPLEMENTED | PASS | Approved |
| 1.8 | Search budget | IMPLEMENTED | PASS | Approved |
| 1.9 | Outputs | IMPLEMENTED | PASS | Approved |

### Decisions for the team

1. **log1p candidates (1.3).** G-47 says log1p only for continuous positive-scale features. I read that as: total\_price, total\_freight, freight\_ratio, total\_weight\_g, total\_volume\_cm3, distance\_km\_max. Counts (n\_items, n\_products, n\_sellers, n\_categories, n\_payment\_methods, payment\_installments\_max) are never logged. Please confirm, or name counts to add.
2. **Contract predictor names (1.3).** The 27 names come from the Milestone 2 contract code (names only, no results; G-29). Please confirm the list in card 1.3.

**Status: both decided in round 1 (see the comment threads), applied in round 2.**

- Decision 1 → **G-62**: log1p candidates are total\_price, total\_freight, total\_weight\_g, total\_volume\_cm3, distance\_km\_max (each only if pre-cutoff skewness > 1); freight\_ratio and counts are never logged; missing values stay missing through log1p; new s02 step 2.13 removes orders with a negative candidate value (zero kept). Follow-up from the same thread → **G-63**: every s02 removal rule writes exclusions.csv rows with step, reason\_code and reason\_description, one description per code (codes in card 1.3).
- Decision 2 → **G-61**: the contract is the 24 predictors of a new e5lib/contract.py written for Experiment 5; has\_items, freight\_ratio\_missing and payment\_missing are listed there as not in the contract, with their reason, and are not built in s02.

### Checks

| Check | Result | Detail | IDs |
| --- | --- | --- | --- |
| pre-registered before any later stage has outputs | PASS | stages with outputs: none | 1.9 |
| contract: 24 distinct predictors, groups and log1p candidates consistent | PASS | — | 1.3 |
| not-in-contract columns have a reason and are not predictors | PASS | — | 1.3 |
| one description per exclusion reason code | PASS | 9 codes | 1.3 |
| every citation is in the verified list | PASS | 8 citations | 1.4, 1.5, 1.7 |
| grids match the AGREED s07 blueprint | PASS | — | 1.8 |
| all ten blueprints AGREED | PASS | — | 1.9 |

### Evidence cards

#### 1.1 Tasks and prediction time

**Approved solution:** Regression: delivery lead time in fractional days. Classification: will an eligible order (not cancelled or unavailable, and reviewed) receive a 1–2 star review (is\_detractor, positive class 1). Both predicted at checkout.

**What was done:** Two tasks pre-registered: lead\_days (regression) and is\_detractor (classification, positive class 1), both predicted at order\_purchase\_timestamp.

**Conclusion:** Matches s01 1.1 and G-34 (eligible-order wording and scope limit). *(claim type: observation)*

| Key | Value |
| --- | --- |
| Prediction time | order\_purchase\_timestamp |
| Regression target | lead\_days (days) |
| Classification target | is\_detractor, positive class 1 |
| Score meaning | risk of a 1-2 star review if the customer reviews (scope limit) |

**Files** (local, run 20261018T150315Z): protocol\_preregistered.yaml, preregistered\_values.csv, task\_contract.md

#### 1.2 Stakeholders and action

**Approved solution:** Regression → logistics / fulfilment planning; classification → customer-experience team, daily list of at-risk orders for proactive contact.

**What was done:** Stakeholder and action recorded per task in protocol.yaml and task\_contract.md.

**Conclusion:** Regression: logistics / fulfilment planning: expected lead time per order at checkout, to flag long-haul orders and set realistic delivery promises. Classification: customer-experience team: daily list of at-risk orders for proactive contact (status update, check with the seller). *(claim type: observation)*

| Key | Value |
| --- | --- |
| Regression | logistics / fulfilment planning: expected lead time per order at checkout, to flag long-haul orders and set realistic delivery promises |
| Classification | customer-experience team: daily list of at-risk orders for proactive contact (status update, check with the seller) |

**Files** (local, run 20261018T150315Z): protocol\_preregistered.yaml, preregistered\_values.csv, task\_contract.md

#### 1.3 Targets and populations

**Approved solution:** As agreed in s02: minimum-review label with first-review sensitivity; delivered orders (regression); not cancelled or unavailable, with a review (classification); scope limits stated.

**What was done (round 2):** Populations, label rule and the predictor contract recorded from e5lib/contract.py: 24 predictors (4 categorical, calendar fields numeric); 3 columns listed as not in the contract with their reason; 9 exclusion reason codes for s02.

**Reasoning:** Round 2 applies the round 1 review: the contract is defined directly as the 24 predictors (G-61); log1p candidates are total\_price, total\_freight, total\_weight\_g, total\_volume\_cm3 and distance\_km\_max, while freight\_ratio and counts are never logged; missing values stay missing through log1p; orders with a negative candidate value are removed in s02 (G-62); every s02 removal is written to exclusions.csv with a reason code and description (G-63).

**Conclusion:** Feeds s02 (populations, exclusion codes, the 24 predictors to build) and s03-s04 (feature groups, log1p candidates). *(claim type: observation)*

| Key | Value |
| --- | --- |
| Both tasks | zero-item orders excluded; orders with missing payment\_installments\_max removed; orders without a usable payment removed (no payment rows, or only not\_defined); orders with a negative value in a log1p candidate removed (zero kept) |
| Regression | delivered orders with a valid lead time |
| Classification | orders not cancelled or unavailable, with a valid review; targets never imputed |
| Outlier rule | lead\_days > max(100, mean + 12 \* SD), mean and SD from pre-cutoff orders; distance > 4397.53 km |
| Contract | e5lib/contract.py (G-61) |
| Predictors (24) | n\_items, n\_products, n\_sellers, n\_categories, total\_price, total\_freight, freight\_ratio, total\_weight\_g, total\_volume\_cm3, weight\_missing\_fraction, volume\_missing\_fraction, primary\_category, category\_missing\_fraction, customer\_state, primary\_seller\_state, distance\_km\_max, distance\_missing\_fraction, interstate\_share, purchase\_month, purchase\_dayofweek, purchase\_hour, primary\_payment\_type, payment\_installments\_max, n\_payment\_methods |
| Not in the contract | has\_items: post-purchase leakage: encodes a later cancellation (G-30); freight\_ratio\_missing: post-purchase leakage: encodes a later cancellation (G-30); payment\_missing: constant after the population rules: s02 2.11 removes orders without a usable payment (G-42, G-51) |
| Categorical | customer\_state, primary\_seller\_state, primary\_category, primary\_payment\_type |
| Calendar (numeric) | purchase\_month, purchase\_dayofweek, purchase\_hour |
| log1p candidates (if skewness > 1.0) | total\_price, total\_freight, total\_weight\_g, total\_volume\_cm3, distance\_km\_max |
| Never logged | freight\_ratio (team decision in the s01 review, G-62); counts: n\_items, n\_products, n\_sellers, n\_categories, n\_payment\_methods, payment\_installments\_max (G-62); calendar fields (G-22, G-47); shares and fractions (G-47) |
| Missing values | stay missing through log1p; imputed afterwards in the fold pipeline |
| Negative values | orders removed in s02 2.13 (reason NEGATIVE\_VALUE) |
| exclusions.csv | order\_id, task, step, reason\_code, reason\_description; one row per removed order and reason, every removal rule included; one description per code (G-63) |
| INVALID\_LEAD\_TIME | not delivered, or delivery time missing or not after purchase (s02 2.6, 2.8) |
| ZERO\_ITEMS | order has no items (s02 2.8) |
| CANCELLED\_OR\_UNAVAILABLE | order cancelled or unavailable (s02 2.8) |
| NO\_VALID\_REVIEW | no valid review score (s02 2.8) |
| LEAD\_DAYS\_OUTLIER | lead\_days above max(100, mean + 12 SD) of pre-cutoff orders (s02 2.9) |
| DISTANCE\_OUTLIER | distance\_km\_max above 4,397.53 km (s02 2.9) |
| MISSING\_INSTALLMENTS | payment\_installments\_max missing (s02 2.10) |
| NO\_USABLE\_PAYMENT | no payment rows, or only the not\_defined payment type (s02 2.11) |
| NEGATIVE\_VALUE | negative value in a log1p candidate (s02 2.13) |

**Files** (local, run 20261018T150315Z): protocol\_preregistered.yaml, preregistered\_values.csv, task\_contract.md; contract source e5lib/contract.py

#### 1.4 Metrics

**Approved solution:** MAE primary (regression); AP primary (classification), with ROC-AUC, Brier, precision, recall, F1 and confusion matrix; PR and ROC charts; accuracy never alone.

**What was done:** Primary metrics: MAE (regression), AP (classification), with secondary metrics and charts; evaluation settings for s09 pre-registered.

**Conclusion:** 3 verified citations in the task contract. *(claim type: observation)*

| Key | Value |
| --- | --- |
| Regression | primary mae; rmse, r2, within\_3d |
| Classification | primary ap; roc\_auc, brier, precision, recall, f1, confusion\_matrix |
| Bootstrap | 1000 resamples, 95% intervals |
| Slices | classification states with > 100 detractors; regression slices under 100 orders descriptive |

**Files** (local, run 20261018T150315Z): protocol\_preregistered.yaml, preregistered\_values.csv, task\_contract.md

#### 1.5 Cost assumption

**Approved solution:** Illustrative cost FN:FP = 5:1, stated as an assumption (Elkan 2001).

**What was done:** Illustrative cost FN:FP = 5:1.

**Conclusion:** Stated as an assumption; drives the s08 threshold table (cost cutoff 1/6). *(claim type: observation)*

| Key | Value |
| --- | --- |
| Cost | FN:FP = 5:1 |
| Nature | illustrative assumption, never measured ROI |

**Files** (local, run 20261018T150315Z): protocol\_preregistered.yaml, preregistered\_values.csv, task\_contract.md

#### 1.6 Model families

**Approved solution:** Dummy (median / prior); linear (LinearRegression, Ridge; LogisticRegression); tree (DecisionTree, RandomForest). No boosting, voting or stacking.

**What was done:** 5 regression and 4 classification estimators, with the s06 plain settings.

**Conclusion:** No boosting, voting or stacking. *(claim type: observation)*

| Key | Value |
| --- | --- |
| Regression | dummy\_median, linear, ridge, tree\_reg, forest\_reg |
| Classification | dummy\_prior, logistic, tree\_clf, forest\_clf |
| s06 tree | {'max\_depth': 5, 'min\_samples\_leaf': 100} |
| s06 forest | {'n\_estimators': 200, 'max\_depth': 10, 'min\_samples\_leaf': 50, 'max\_features': 'sqrt'} |
| Logistic | unregularised (C = inf), lbfgs, max\_iter 5000 |

**Files** (local, run 20261018T150315Z): protocol\_preregistered.yaml, preregistered\_values.csv, task\_contract.md

#### 1.7 Decision rule

**Approved solution:** One-standard-error rule with the simplicity order, plain-vs-tuned comparison and fallback; s08 gate with override as a logged deviation; threshold is a business judgement.

**What was done:** One-standard-error rule, simplicity order, plain-vs-tuned comparison, fallback, s08 gate, calibration keep rule and threshold candidates pre-registered.

**Conclusion:** e5lib.metrics.one\_se\_select implements the rule; its contract tests cover the simpler-within-one-SE case. *(claim type: observation)*

| Key | Value |
| --- | --- |
| Rule | keep the simplest candidate whose fold-mean primary metric is within one standard error of the best mean; SE = fold SD / sqrt(5); ties go to the simpler |
| Simplicity order | dummy < linear/logistic < single tree < forest |
| Within a family | higher alpha, lower C, shallower depth, then larger leaf |
| Plain vs tuned | the plain s06 model is kept if it is within one SE of the tuned configuration (G-55) |
| Fallback | if no complex variant passes, the best simple model goes forward; if nothing beats the dummy, the dummy is the result |
| Calibration | mean Brier improves and mean AP stays within one fold SE of the raw model |
| Threshold candidates | no alerts; 0.5; 1/6 (cost cutoff); empirical minimum of 5\*FN + FP |

**Files** (local, run 20261018T150315Z): protocol\_preregistered.yaml, preregistered\_values.csv, task\_contract.md

#### 1.8 Search budget

**Approved solution:** Grids fixed in s07; random forest 200 trees; seed 42; no new grid points after results.

**What was done:** Grids fixed: tree depths \[4, 5, 6, 8, 10, 12, 14, 16, 18\], forest depths \[8, 10, 12, 14, 16, 18\], leaves \[20, 50, 100, 200\], alpha and C \[0.01, 0.1, 0.5, 1, 5, 10, 20, 50, 100\]; forest 200 trees; seed 42.

**Conclusion:** Checked against the AGREED s07 blueprint (see check). *(claim type: observation)*

| Key | Value |
| --- | --- |
| Ridge alpha / logistic C | 0.01, 0.1, 0.5, 1, 5, 10, 20, 50, 100 |
| Tree depth | 4, 5, 6, 8, 10, 12, 14, 16, 18 |
| Forest depth | 8, 10, 12, 14, 16, 18 |
| Leaf | 20, 50, 100, 200 |
| Class weight | None, balanced |
| Forest trees | 200 |
| Seed | 42 |

**Files** (local, run 20261018T150315Z): protocol\_preregistered.yaml, preregistered\_values.csv, task\_contract.md

#### 1.9 Outputs

**Approved solution:** protocol.yaml pre-registered layer and task\_contract.md.

**What was done:** spec/protocol.yaml (pre-registered layer) and task\_contract.md written; the values are also listed in preregistered\_values.csv for review.

**Conclusion:** Later stages read these values through e5lib.protocol; none hard-codes them. *(claim type: observation)*

| Key | Value |
| --- | --- |
| Written | spec/protocol.yaml (pre-registered layer), task\_contract.md, preregistered\_values.csv |
| Version | 1.0 |

**Files** (local, run 20261018T150315Z): protocol\_preregistered.yaml, preregistered\_values.csv

## Round history

### Round 1 — 2026-10-18

- First build of s01. No data read; values taken from the AGREED blueprints and decision log.
- Foundation fixes made while building (CR-027): protocol hashed by layer, dirty check ignores generated files, review links pinned to the evidence commit.
- Comments: Henry on the log1p candidates (missing and negative values, freight\_ratio and counts) and on exclusions.csv reason codes; the lead on defining a 24-predictor contract.py. All decided in the threads; outcome: changes requested on 1.3.

### Round 2 — 2026-10-18

- Run 20261018T150315Z on the uncommitted working tree (base commit 0e87418; G-64). Coverage 9 of 9 IMPLEMENTED, 7 checks PASS.
- 1.3 changed: new e5lib/contract.py with the 24 predictors (G-61); log1p candidates narrowed, negative-value rule as s02 step 2.13 (G-62); 9 exclusion reason codes pre-registered for s02 exclusions.csv (G-63). Checks on the 27-predictor list replaced by contract and reason-code checks.
- Spec amended to match (CR-028): s02 steps 5, 7, 12 (new), outputs and reuse; s03 and s04 feature counts and log1p wording; pipeline design, decision log G-61 to G-64.
- Foundation (CR-028): review rounds are packed without a commit; s01 is committed once, at acceptance.
- Rows 1.1, 1.2 and 1.4–1.9 show the same values as round 1 (their shared output files were regenerated).
- Comments and resolutions: none yet.

* Outcome: all 9 rows Approved by the team; accepted by the experiment lead. Committed as `453896d`, tagged `e5-s01-accepted`; the run's manifest is FRESH against that commit (CR-029).

### Later change — 2026-10-19 (after acceptance)

- s01 was rerun after foundation changes (CR-030, CR-031, CR-033); every value output is byte-identical. The 1.9 check "pre-registered before any later stage has outputs" failed on reruns once s02 existed, so it is now "later stages used this pre-registered layer" (each later manifest's pre-registered hash must equal s01's). The lead confirms this in the s02 review (decision 3). The tables above show round 2 as accepted.

## Addendum — 2026-10-19, CR-037 (G-68): screening candidates registered

Approved by the experiment lead after the s03 round 1 review; reviewed together with s03 round 2. s01 stays ACCEPTED. Run 20261019T140139Z.

- **1.3:** protocol.yaml (pre-registered layer) gains features.screening\_candidates from e5lib/contract.py: product\_photos\_qty (scaled, never logged), product\_description\_lenght and product\_name\_lenght (log1p if pre-cutoff skewness > 1, then scaled), classification only, value of the primary item. They are not predictors; a candidate enters the classification selection pool only if the team adopts it at the s03 gate.
- The addition was made after the first EDA and is disclosed as post-hoc in the report, with the assumption that catalogue fields are fixed at checkout.
- **New check (1.3):** screening candidates are task-scoped and outside the 24 predictors: PASS. All other pre-registered values are unchanged.

## Addendum — 2026-10-19, CR-038 (G-69): more screening candidates

Approved by the experiment lead; reviewed together with s03 round 3. s01 stays ACCEPTED. Run 20261019T151352Z.

- **1.3:** features.screening\_candidates gains est\_delivery\_days, customer\_region, seller\_region, region\_pair and five seller\_prior\_\* columns; each entry now names its group (the s03 card that screens it), kind and planned transform. Added notes: est\_delivery\_days is screened for classification only (G-35 reopened for this screen) and, if adopted, trains on out-of-fold task 1 predictions; the seller-history time rule.
- Adopted at the s03 gate so far: product\_photos\_qty, product\_description\_lenght (human\_decisions.yaml).
