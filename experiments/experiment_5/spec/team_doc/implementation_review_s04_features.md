# s04 Features — implementation review

> **ACCEPTED · round 3 · 2026-10-20 · tag e5-s04-accepted · approved by the experiment lead after Henry's review.** Accepted runs 20261020T145617Z (regression) and 20261020T145604Z (classification), on a clean tree; every output is identical to the round 3 review packs, so the cards in the sub-tabs are the accepted values. Selected sets: regression 18 features, classification 19 (+ derived missing indicators). Decisions: G-70, G-73 (duplicate encoded columns), G-76 (citations checked in Experiment 5), G-27 kept (route median), tree encoding kept. Report appendix requests are recorded in the s04 and s10 report hooks.

**Round 1 · IN REVIEW** · runs `20261020T062548Z` (regression) and `20261020T062543Z` (classification) · coverage 7 of 7 per task (6 IMPLEMENTED, 4.6 DEVIATION), 0 MISSING · 12 + 12 checks, all PASS. Evidence cards are in the two sub-tabs; approve rows here and comment anywhere. Nothing is committed until s04 is accepted (G-64). Nothing is fitted in s04: the recipes are fitted inside the folds in s06–s08.

## Current (round 1)

### Coverage

| Task | ID | Solution step | Coverage | Checks | Review |
| --- | --- | --- | --- | --- | --- |
| regression | 4.1 | Baseline | IMPLEMENTED | PASS | Approved |
| regression | 4.2 | Transforms | IMPLEMENTED | PASS | Approved |
| regression | 4.3 | Reduction | IMPLEMENTED | PASS | Approved |
| regression | 4.4 | Selection | IMPLEMENTED | PASS | Approved |
| regression | 4.6 | Rationale | DEVIATION | PASS | Approved |
| regression | 4.7 | Selected set | IMPLEMENTED | PASS | Approved |
| regression | 4.8 | Pipeline recipe | IMPLEMENTED | PASS | Approved |
| classification | 4.1 | Baseline | IMPLEMENTED | PASS | Approved |
| classification | 4.2 | Transforms | IMPLEMENTED | PASS | Approved |
| classification | 4.3 | Reduction | IMPLEMENTED | PASS | Approved |
| classification | 4.4 | Selection | IMPLEMENTED | PASS | Approved |
| classification | 4.6 | Rationale | DEVIATION | PASS | Approved |
| classification | 4.7 | Selected set | IMPLEMENTED | PASS | Approved |
| classification | 4.8 | Pipeline recipe | IMPLEMENTED | PASS | Approved |

### Selected feature sets (4.7)

- **Regression:** 18 of 23 core features at 99%: distance\_km\_max, customer\_state, interstate\_share, total\_freight, primary\_category, freight\_ratio, total\_price, primary\_seller\_state, total\_weight\_g, primary\_payment\_type, total\_volume\_cm3, n\_sellers, payment\_installments\_max, purchase\_dayofweek, n\_products, purchase\_month, n\_items, n\_categories.
- **Classification:** 19 of 26 core features at 99%: seller\_prior\_review\_mean, total\_freight, freight\_ratio, total\_volume\_cm3, total\_price, n\_items, product\_description\_lenght, customer\_state, total\_weight\_g, n\_products, n\_sellers, purchase\_month, distance\_km\_max, interstate\_share, primary\_category, n\_categories, primary\_seller\_state, payment\_installments\_max, product\_photos\_qty.
- Both match the s03 preview (same features). The derived missing indicators come with their parent features (classification includes the seller-rating indicator).

### Feature × task

Every pool feature, kept or not, per task (from both feature\_dictionary.csv files; promised in the s02 review, 2.12).

| Feature | Source | Regression | Classification |
| --- | --- | --- | --- |
| n\_items | contract | kept: rank 17 of 23 in the core ranking, cumulative share 0.9875 reached within 99% | kept: rank 6 of 26 in the core ranking, cumulative share 0.5632 reached within 99% |
| n\_products | contract | kept: rank 15 of 23 in the core ranking, cumulative share 0.9663 reached within 99% | kept: rank 10 of 26 in the core ranking, cumulative share 0.7735 reached within 99% |
| n\_sellers | contract | kept: rank 12 of 23 in the core ranking, cumulative share 0.9208 reached within 99% | kept: rank 11 of 26 in the core ranking, cumulative share 0.8166 reached within 99% |
| n\_categories | contract | kept: rank 18 of 23 in the core ranking, cumulative share 0.9920 reached within 99% | kept: rank 16 of 26 in the core ranking, cumulative share 0.9671 reached within 99% |
| total\_price | contract | kept: rank 7 of 23 in the core ranking, cumulative share 0.8016 reached within 99% | kept: rank 5 of 26 in the core ranking, cumulative share 0.4863 reached within 99% |
| total\_freight | contract | kept: rank 4 of 23 in the core ranking, cumulative share 0.6734 reached within 99% | kept: rank 2 of 26 in the core ranking, cumulative share 0.2238 reached within 99% |
| freight\_ratio | contract | kept: rank 6 of 23 in the core ranking, cumulative share 0.7693 reached within 99% | kept: rank 3 of 26 in the core ranking, cumulative share 0.3169 reached within 99% |
| total\_weight\_g | contract | kept: rank 9 of 23 in the core ranking, cumulative share 0.8596 reached within 99% | kept: rank 9 of 26 in the core ranking, cumulative share 0.7266 reached within 99% |
| total\_volume\_cm3 | contract | kept: rank 11 of 23 in the core ranking, cumulative share 0.9041 reached within 99% | kept: rank 4 of 26 in the core ranking, cumulative share 0.4068 reached within 99% |
| weight\_missing\_fraction | contract | not kept: duplicate, identical to volume\_missing\_fraction on every pre-cutoff order; volume\_missing\_fraction ranks higher (22 vs 23) | not kept: duplicate, identical to volume\_missing\_fraction on every pre-cutoff order; volume\_missing\_fraction ranks higher (25 vs 26) |
| volume\_missing\_fraction | contract | not kept: rank 22 of 23, after the 99% cut | not kept: rank 25 of 26, after the 99% cut |
| primary\_category | contract | kept: rank 5 of 23 in the core ranking, cumulative share 0.7238 reached within 99% | kept: rank 15 of 26 in the core ranking, cumulative share 0.9507 reached within 99% |
| category\_missing\_fraction | contract | not kept: rank 20 of 23, after the 99% cut | not kept: rank 20 of 26, after the 99% cut |
| customer\_state | contract | kept: rank 2 of 23 in the core ranking, cumulative share 0.3612 reached within 99% | kept: rank 8 of 26 in the core ranking, cumulative share 0.6737 reached within 99% |
| primary\_seller\_state | contract | kept: rank 8 of 23 in the core ranking, cumulative share 0.8331 reached within 99% | kept: rank 17 of 26 in the core ranking, cumulative share 0.9765 reached within 99% |
| distance\_km\_max | contract | kept: rank 1 of 23 in the core ranking, cumulative share 0.1866 reached within 99% | kept: rank 13 of 26 in the core ranking, cumulative share 0.8955 reached within 99% |
| distance\_missing\_fraction | contract | not kept: rank 19 of 23, after the 99% cut | not kept: rank 23 of 26, after the 99% cut |
| interstate\_share | contract | kept: rank 3 of 23 in the core ranking, cumulative share 0.5335 reached within 99% | kept: rank 14 of 26 in the core ranking, cumulative share 0.9232 reached within 99% |
| purchase\_month | contract | kept: rank 16 of 23 in the core ranking, cumulative share 0.9780 reached within 99% | kept: rank 12 of 26 in the core ranking, cumulative share 0.8587 reached within 99% |
| purchase\_dayofweek | contract | kept: rank 14 of 23 in the core ranking, cumulative share 0.9526 reached within 99% | not kept: rank 22 of 26, after the 99% cut |
| purchase\_hour | contract | not kept: rank 23 of 23, after the 99% cut | not kept: rank 21 of 26, after the 99% cut |
| primary\_payment\_type | contract | kept: rank 10 of 23 in the core ranking, cumulative share 0.8844 reached within 99% | not kept: rank 24 of 26, after the 99% cut |
| payment\_installments\_max | contract | kept: rank 13 of 23 in the core ranking, cumulative share 0.9372 reached within 99% | kept: rank 18 of 26 in the core ranking, cumulative share 0.9849 reached within 99% |
| n\_payment\_methods | contract | not kept: rank 21 of 23, after the 99% cut | not kept: rank 26 of 26, after the 99% cut |
| product\_photos\_qty | adopted (G-70) | not in pool (classification only) | kept: rank 19 of 26 in the core ranking, cumulative share 0.9906 reached within 99% |
| product\_description\_lenght | adopted (G-70) | not in pool (classification only) | kept: rank 7 of 26 in the core ranking, cumulative share 0.6198 reached within 99% |
| seller\_prior\_review\_mean | adopted (G-70) | not in pool (classification only) | kept: rank 1 of 26 in the core ranking, cumulative share 0.1159 reached within 99% |

### Imputation inside the folds

Order: log1p first (for the log1p inputs), then imputation, then encoding and scaling, all fitted on each training fold and applied to its validation fold (G-27, G-47). Missing shares below are on all pre-cutoff orders. The learned medians and the counts filled per fold need the folds, which s05 defines; they are reported from the fitted pipelines in s06 (promised in the s02 review, 2.12).

| Feature | Kind | Missing, regression (pre-cutoff) | Missing, classification (pre-cutoff) | Rule in the fold pipeline |
| --- | --- | --- | --- | --- |
| n\_items | numeric | 0.00% | 0.00% | median + missing indicator (indicator only if the training fold has missing values) |
| n\_products | numeric | 0.00% | 0.00% | median + missing indicator (indicator only if the training fold has missing values) |
| n\_sellers | numeric | 0.00% | 0.00% | median + missing indicator (indicator only if the training fold has missing values) |
| n\_categories | numeric | 0.00% | 0.00% | median + missing indicator (indicator only if the training fold has missing values) |
| total\_price | numeric | 0.00% | 0.00% | log1p, then median + missing indicator (indicator only if the training fold has missing values) |
| total\_freight | numeric | 0.00% | 0.00% | log1p, then median + missing indicator (indicator only if the training fold has missing values) |
| freight\_ratio | numeric | 0.00% | 0.00% | median + missing indicator (indicator only if the training fold has missing values) |
| total\_weight\_g | numeric | 0.02% | 0.02% | log1p, then median + missing indicator (indicator only if the training fold has missing values) |
| total\_volume\_cm3 | numeric | 0.02% | 0.02% | log1p, then median + missing indicator (indicator only if the training fold has missing values) |
| weight\_missing\_fraction | numeric | 0.00% | 0.00% | median + missing indicator (indicator only if the training fold has missing values) |
| volume\_missing\_fraction | numeric | 0.00% | 0.00% | median + missing indicator (indicator only if the training fold has missing values) |
| primary\_category | categorical | 0.00% | 0.00% | missing → 'Unknown' level, then one-hot (unknown levels ignored) |
| category\_missing\_fraction | numeric | 0.00% | 0.00% | median + missing indicator (indicator only if the training fold has missing values) |
| customer\_state | categorical | 0.00% | 0.00% | missing → 'Unknown' level, then one-hot (unknown levels ignored) |
| primary\_seller\_state | categorical | 0.00% | 0.00% | missing → 'Unknown' level, then one-hot (unknown levels ignored) |
| distance\_km\_max | numeric | 1.16% | 1.17% | log1p, then route median (customer\_state × primary\_seller\_state → customer\_state → global) + distance\_km\_max\_missing |
| distance\_missing\_fraction | numeric | 0.00% | 0.00% | median + missing indicator (indicator only if the training fold has missing values) |
| interstate\_share | numeric | 0.00% | 0.00% | median + missing indicator (indicator only if the training fold has missing values) |
| purchase\_month | numeric | 0.00% | 0.00% | median + missing indicator (indicator only if the training fold has missing values) |
| purchase\_dayofweek | numeric | 0.00% | 0.00% | median + missing indicator (indicator only if the training fold has missing values) |
| purchase\_hour | numeric | 0.00% | 0.00% | median + missing indicator (indicator only if the training fold has missing values) |
| primary\_payment\_type | categorical | 0.00% | 0.00% | missing → 'Unknown' level, then one-hot (unknown levels ignored) |
| payment\_installments\_max | numeric | 0.00% | 0.00% | median + missing indicator (indicator only if the training fold has missing values) |
| n\_payment\_methods | numeric | 0.00% | 0.00% | median + missing indicator (indicator only if the training fold has missing values) |
| product\_photos\_qty | numeric | — | 1.67% | median + missing indicator (indicator only if the training fold has missing values) |
| product\_description\_lenght | numeric | — | 1.67% | log1p, then median + missing indicator (indicator only if the training fold has missing values) |
| seller\_prior\_review\_mean | numeric | — | 6.83% | median + missing indicator (indicator only if the training fold has missing values) |

### Decisions for the team

1. **Duplicate encoded columns (4.3, proposed G-73).** Weight and volume are always missing together, and so are the two catalogue fields (photos, description). Their missing indicators are identical, which made the linear/logistic design matrix rank-deficient (rank 137 of 138 regression, 138 of 140 classification). I apply the 4.3 duplicate rule to the encoded columns inside each training fold (factory step `dedupe`); both matrices are then full rank (condition number 424 and 1,550). Please confirm.
2. **Citations (4.6, DEVIATION).** The blueprint asks for verified citations. The candidate references are the Milestone 2 ones (Cui et al. 2024 for location features; Leite et al. 2024 for basket and product features; Deshpande & Pendem for the seller rating), not yet checked against their sources. Resolved in round 2 (lead comment: no reliance on earlier experiments): the Milestone 2 references are removed and every hypothesis is labelled an unmeasured mechanism. 4.6 stays a DEVIATION (no verified citation) unless the team wants sources found and checked independently.
3. **Identical pair weight\_missing\_fraction = volume\_missing\_fraction (4.3).** The rule keeps the higher-ranked one: volume\_missing\_fraction stays in the core set, weight\_missing\_fraction is dropped (both tasks). Neither is selected at 99%, so this does not change the selected sets. Please confirm.
4. **Tree recipe rank (4.8).** The tree recipe keeps every one-hot level, so its design matrix is rank-deficient by design (each categorical's dummies sum to 1). This does not affect trees; the rank check applies to the linear/logistic recipe only. Please confirm.

### Checks

| Task | Check | Result | Detail | IDs |
| --- | --- | --- | --- | --- |
| regression | every computation reads only pre-cutoff rows | PASS | latest purchase 2018-05-27 12:20:21, cutoff 2018-05-27 12:30:34; 76,925 rows | 4.2, 4.3, 4.4 |
| regression | ranked feature set equals contract.pool(task) and shares sum to 1 | PASS | 24 features, measure: absolute Spearman | 4.4 |
| regression | threshold and collinearity drops read from human\_decisions.yaml | PASS | threshold 0.99; team drops 0 | 4.3, 4.4 |
| regression | every collinearity drop has a row in reduction\_rationale.csv | PASS | — | 4.3 |
| regression | selected set and threshold recorded in protocol.yaml (data\_dependent.selected\_set) | PASS | — | 4.7 |
| regression | log1p only for the log1p candidates with skewness above the trigger | PASS | total\_price 10.13, total\_freight 8.13, total\_weight\_g 6.63, total\_volume\_cm3 7.40, distance\_km\_max 1.64 | 4.2 |
| regression | feature\_dictionary covers every pool feature and every selected feature has a rationale | PASS | — | 4.6 |
| regression | order\_estimated\_delivery\_date and est\_delivery\_days are not features (G-35) | PASS | — | 4.1, 4.7 |
| regression | no target cap and no target among the features (G-25) | PASS | — | 4.2 |
| regression | linear/logistic design matrix has full column rank after the duplicate rule | PASS | rank 137 of 137; tree recipe (full one-hot, no scaling) is rank-deficient by design: each categorical's dummies sum to 1, which does not affect trees | 4.3, 4.8 |
| regression | no fitted object saved in the outputs | PASS | none | 4.8 |
| regression | every family recipe builds an estimator from e5lib.factory | PASS | — | 4.8 |
| classification | every computation reads only pre-cutoff rows | PASS | latest purchase 2018-05-26 12:12:15, cutoff 2018-05-26 12:16:34; 77,736 rows | 4.2, 4.3, 4.4 |
| classification | ranked feature set equals contract.pool(task) and shares sum to 1 | PASS | 27 features, measure: mutual information | 4.4 |
| classification | threshold and collinearity drops read from human\_decisions.yaml | PASS | threshold 0.99; team drops 0 | 4.3, 4.4 |
| classification | every collinearity drop has a row in reduction\_rationale.csv | PASS | — | 4.3 |
| classification | selected set and threshold recorded in protocol.yaml (data\_dependent.selected\_set) | PASS | — | 4.7 |
| classification | log1p only for the log1p candidates with skewness above the trigger | PASS | total\_price 10.06, total\_freight 8.10, total\_weight\_g 6.59, total\_volume\_cm3 7.48, distance\_km\_max 1.64, product\_description\_lenght 2.05 | 4.2 |
| classification | feature\_dictionary covers every pool feature and every selected feature has a rationale | PASS | — | 4.6 |
| classification | order\_estimated\_delivery\_date and est\_delivery\_days are not features (G-35) | PASS | — | 4.1, 4.7 |
| classification | no target cap and no target among the features (G-25) | PASS | — | 4.2 |
| classification | linear/logistic design matrix has full column rank after the duplicate rule | PASS | rank 138 of 138; tree recipe (full one-hot, no scaling) is rank-deficient by design: each categorical's dummies sum to 1, which does not affect trees | 4.3, 4.8 |
| classification | no fitted object saved in the outputs | PASS | none | 4.8 |
| classification | every family recipe builds an estimator from e5lib.factory | PASS | — | 4.8 |

## Round history

### Round 1 — 2026-10-20

- First build of s04 for both tasks on pre-cutoff development orders. New foundation module e5lib/features.py with tests; factory gains the duplicate-column step (CR-044).
- The foundation change made s01–s03 stale; all rerun with identical values, except two cells of the s02 data dictionary: the missing meaning of the seller-history columns is corrected (it said "product without a catalogue value").
- Comments and resolutions: none yet.

### Round 2 — 2026-10-20

- Lead comment on 4.6: Experiment 5 must not rely on earlier experiments. The Milestone 2 references are removed from feature\_dictionary.csv; every hypothesised signal is now an unmeasured mechanism; 4.6 stays a DEVIATION (no verified citation). Only 4.6 changed (both tasks); every other output is unchanged.
- Runs 20261020T070535Z (regression) and 20261020T070530Z (classification); review packs review/round\_2/.

### Round 3 — 2026-10-20

- Henry's review: decisions 1 (duplicate encoded columns, G-73) and 3 (identical pair) agreed; decision 4 (tree recipe keeps every one-hot level) answered in its thread: that is the agreed 4.8 recipe.
- Decision 2 (citations): papers re-checked in this experiment (G-76). Deshpande & Pendem (2023) and Leite et al. (2024) are cited for the nine classification delivery proxies; Cui et al. (2024) is not cited (it studies the promised delivery speed). 4.6 stays a DEVIATION for kept features without a source (all regression features; 16 of 25 classification).
- Open for the lead: Henry's proposal to remove regression orders with a missing distance\_km\_max instead of the route median (G-27).
- Runs 20261020T124722Z (regression) and 20261020T124703Z (classification); review packs review/round\_3/. Only 4.6 changed.

### Acceptance — 2026-10-20

- Henry's last comments: distance proposal withdrawn (“OK, no change required”, G-27 kept); tree encoding kept; documentation requests (derived-feature formulas, recipe table) recorded for the report appendix.
- Code committed first (c7114d3), then s01–s05 rerun on the clean tree (dirty false). s04 accepted by the experiment lead, committed and tagged e5-s04-accepted before s05 (G-74).
