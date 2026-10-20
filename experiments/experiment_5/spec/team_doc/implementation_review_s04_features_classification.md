# s04 Features › classification — evidence cards

Round 1 · run `20261020T062543Z` · 12 checks, all PASS. Coverage, decisions and review dropdowns are on the parent tab "s04 Features"; comment on any card here.

## 4.1 Baseline

**Approved solution:** The 24 predictors of e5lib/contract.py (G-61; has\_items, freight\_ratio\_missing and payment\_missing are not in the contract: the first two leak a later cancellation, payment\_missing is constant after 2.11; G-30, G-42, G-51); `purchase_month`, `purchase_dayofweek`, `purchase_hour` numeric. Classification adds the three candidates adopted at the s03 gate: product\_photos\_qty, product\_description\_lenght, seller\_prior\_review\_mean (G-70)

**What was done:** Pool from e5lib.contract.pool('classification'): 27 features = 24 contract predictors + 3 adopted at the s03 gate (product\_description\_lenght, product\_photos\_qty, seller\_prior\_review\_mean); 4 categorical, calendar fields numeric (G-22).

**Conclusion:** has\_items, freight\_ratio\_missing, payment\_missing and order\_estimated\_delivery\_date are not in the pool.

| feature | source | kind | calendar\_numeric |
| --- | --- | --- | --- |
| n\_items | contract predictor | numeric | no |
| n\_products | contract predictor | numeric | no |
| n\_sellers | contract predictor | numeric | no |
| n\_categories | contract predictor | numeric | no |
| total\_price | contract predictor | numeric | no |
| total\_freight | contract predictor | numeric | no |
| freight\_ratio | contract predictor | numeric | no |
| total\_weight\_g | contract predictor | numeric | no |
| total\_volume\_cm3 | contract predictor | numeric | no |
| weight\_missing\_fraction | contract predictor | numeric | no |
| volume\_missing\_fraction | contract predictor | numeric | no |
| primary\_category | contract predictor | categorical | no |
| category\_missing\_fraction | contract predictor | numeric | no |
| customer\_state | contract predictor | categorical | no |
| primary\_seller\_state | contract predictor | categorical | no |
| distance\_km\_max | contract predictor | numeric | no |
| distance\_missing\_fraction | contract predictor | numeric | no |
| interstate\_share | contract predictor | numeric | no |
| purchase\_month | contract predictor | numeric | yes |
| purchase\_dayofweek | contract predictor | numeric | yes |
| purchase\_hour | contract predictor | numeric | yes |
| primary\_payment\_type | contract predictor | categorical | no |
| payment\_installments\_max | contract predictor | numeric | no |
| n\_payment\_methods | contract predictor | numeric | no |
| product\_photos\_qty | adopted candidate (G-70) | numeric | no |
| product\_description\_lenght | adopted candidate (G-70) | numeric | no |
| seller\_prior\_review\_mean | adopted candidate (G-70) | numeric | no |

**Check** order\_estimated\_delivery\_date and est\_delivery\_days are not features (G-35): PASS

**Files** (stages/s04\_features/classification/outputs/, run 20261020T062543Z): baseline\_pool.csv

## 4.2 Transforms

**Approved solution:** log1p only for the five contract candidates total\_price, total\_freight, total\_weight\_g, total\_volume\_cm3, distance\_km\_max, each with pre-cutoff skewness > 1, and for classification product\_description\_lenght under the same rule (photo count and seller rating never logged; G-70); freight\_ratio, counts, calendar fields, 0/1 indicators and 0–1 shares never logged; missing values stay missing through log1p and are imputed afterwards (G-47, G-62); log1p regression target. No target cap: extreme values are handled by the s02 outlier removal and the log target

**What was done:** log1p for 6 of 6 candidates by pre-cutoff skewness > 1: total\_price 10.06; total\_freight 8.10; total\_weight\_g 6.59; total\_volume\_cm3 7.48; distance\_km\_max 1.64; product\_description\_lenght 2.05.

**Reasoning:** Missing values stay missing through log1p and are imputed afterwards inside the fold pipeline (G-47).

| feature | log\_candidate | skewness | log1p | rule |
| --- | --- | --- | --- | --- |
| n\_items | no | 7.53 | no | never logged: integer count (G-62, G-70) |
| n\_products | no | 7.73 | no | never logged: integer count (G-62, G-70) |
| n\_sellers | no | 10.24 | no | never logged: integer count (G-62, G-70) |
| n\_categories | no | -2.22 | no | never logged: integer count (G-62, G-70) |
| total\_price | yes | 10.06 | yes | log1p because pre-cutoff skewness 10.06 > 1 |
| total\_freight | yes | 8.10 | yes | log1p because pre-cutoff skewness 8.10 > 1 |
| freight\_ratio | no | 10.93 | no | never logged: team decision in the s01 review (G-62) |
| total\_weight\_g | yes | 6.59 | yes | log1p because pre-cutoff skewness 6.59 > 1 |
| total\_volume\_cm3 | yes | 7.48 | yes | log1p because pre-cutoff skewness 7.48 > 1 |
| weight\_missing\_fraction | no | 69.68 | no | never logged: bounded 0-1 share (G-47) |
| volume\_missing\_fraction | no | 69.68 | no | never logged: bounded 0-1 share (G-47) |
| primary\_category | no | — | no | categorical: one-hot, never logged |
| category\_missing\_fraction | no | 7.53 | no | never logged: bounded 0-1 share (G-47) |
| customer\_state | no | — | no | categorical: one-hot, never logged |
| primary\_seller\_state | no | — | no | categorical: one-hot, never logged |
| distance\_km\_max | yes | 1.64 | yes | log1p because pre-cutoff skewness 1.64 > 1 |
| distance\_missing\_fraction | no | 9.11 | no | never logged: bounded 0-1 share (G-47) |
| interstate\_share | no | -0.64 | no | never logged: bounded 0-1 share (G-47) |
| purchase\_month | no | 0.38 | no | never logged: numeric calendar position (G-22, G-47) |
| purchase\_dayofweek | no | 0.16 | no | never logged: numeric calendar position (G-22, G-47) |
| purchase\_hour | no | -0.61 | no | never logged: numeric calendar position (G-22, G-47) |
| primary\_payment\_type | no | — | no | categorical: one-hot, never logged |
| payment\_installments\_max | no | 1.59 | no | never logged: integer count (G-62, G-70) |
| n\_payment\_methods | no | 6.33 | no | never logged: integer count (G-62, G-70) |
| product\_photos\_qty | no | 1.89 | no | never logged: integer count (G-62, G-70) |
| product\_description\_lenght | yes | 2.05 | yes | log1p because pre-cutoff skewness 2.05 > 1 |
| seller\_prior\_review\_mean | no | -1.83 | no | never logged: 1-5 rating (G-70) |

**Check** every computation reads only pre-cutoff rows: PASS (latest purchase 2018-05-26 12:12:15, cutoff 2018-05-26 12:16:34; 77,736 rows) **Check** log1p only for the log1p candidates with skewness above the trigger: PASS (total\_price 10.06, total\_freight 8.10, total\_weight\_g 6.59, total\_volume\_cm3 7.48, distance\_km\_max 1.64, product\_description\_lenght 2.05) **Check** no target cap and no target among the features (G-25): PASS

**Files** (stages/s04\_features/classification/outputs/, run 20261020T062543Z): transforms.csv

## 4.3 Reduction

**Approved solution:** Drop constant and duplicate features automatically. Highly collinear features are only flagged, by cut-offs pre-registered in `protocol.yaml` (|correlation| > 0.9 or VIF > 10); for each flagged group the team decides which feature to drop, and the decision and its rationale are recorded in reduction\_rationale.csv and written into the report. Then report the encoded design-matrix rank and condition number per recipe

**What was done:** Core set 26 of 27: weight\_missing\_fraction dropped (duplicate, kept volume\_missing\_fraction). Team collinearity drops: 0 (none flagged in s03). Encoded design matrix: linear: 140 encoded columns, duplicates dropped \[missingindicator\_total\_weight\_g; missingindicator\_product\_photos\_qty\], 138 columns, rank 138, condition number 1.55e+03; tree: 143 encoded columns, duplicates dropped \[missingindicator\_total\_weight\_g; missingindicator\_product\_photos\_qty\], 141 columns, rank 139, condition number 7.99e+16.

**Reasoning:** Rank and condition number are measured once on pre-cutoff rows; the preprocessing fitted for this measurement is not saved. Fields that are always missing together give identical missing indicators, so the 4.3 duplicate rule is applied to the encoded columns inside each training fold (factory step 'dedupe'); the linear/logistic matrix is then full rank. The tree recipe keeps every one-hot level, so its matrix is rank-deficient by design, which does not affect trees.

**Reduction** (reduction\_rationale.csv):

| feature | flagged\_by | paired\_with | team\_decision | rationale | decided\_by | date |
| --- | --- | --- | --- | --- | --- | --- |
| weight\_missing\_fraction | duplicate | volume\_missing\_fraction | drop (automatic) | identical to volume\_missing\_fraction on every pre-cutoff order; volume\_missing\_fraction ranks higher (25 vs 26) | rule s04 4.3 | 2026-10-20 |

**Encoded design matrix** (pre-cutoff rows; preprocessing fitted only for this measurement, not saved):

| family | estimator | rows | encoded\_columns | duplicates\_dropped | columns | rank | full\_rank | condition\_number |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear | logistic | 77,736 | 140 | missingindicator\_total\_weight\_g; missingindicator\_product\_photos\_qty | 138 | 138 | yes | 1,550.5 |
| tree | tree\_clf | 77,736 | 143 | missingindicator\_total\_weight\_g; missingindicator\_product\_photos\_qty | 141 | 139 | no | 7.99e+16 |

**Check** every computation reads only pre-cutoff rows: PASS (latest purchase 2018-05-26 12:12:15, cutoff 2018-05-26 12:16:34; 77,736 rows) **Check** threshold and collinearity drops read from human\_decisions.yaml: PASS (threshold 0.99; team drops 0) **Check** every collinearity drop has a row in reduction\_rationale.csv: PASS **Check** linear/logistic design matrix has full column rank after the duplicate rule: PASS (rank 138 of 138; tree recipe (full one-hot, no scaling) is rank-deficient by design: each categorical's dummies sum to 1, which does not affect trees)

**Files** (stages/s04\_features/classification/outputs/, run 20261020T062543Z): reduction\_rationale.csv, design\_matrix.csv

## 4.4 Selection

**Approved solution:** Keep features in s03 ranking order until the cumulative share reaches the team's threshold (95% or 99%), fixed before any model is fitted. CV scores of the chosen set will be somewhat optimistic; the report says so

**What was done:** Core ranking by mutual information, re-normalised over the 26 core features; 19 kept at the 99% threshold. Dropped by the cut: category\_missing\_fraction, purchase\_hour, purchase\_dayofweek, distance\_missing\_fraction, primary\_payment\_type, volume\_missing\_fraction, n\_payment\_methods.

**Reasoning:** Declared exception (G-19): the ranking is computed once on pre-cutoff orders, so CV scores of the chosen set are optimistic; the report says so.

| rank | feature | value | share | cumulative\_share | selected |
| --- | --- | --- | --- | --- | --- |
| 1 | seller\_prior\_review\_mean | 0.0110 | 0.1159 | 0.1159 | yes |
| 2 | total\_freight | 0.0102 | 0.1079 | 0.2238 | yes |
| 3 | freight\_ratio | 0.0088 | 0.0932 | 0.3169 | yes |
| 4 | total\_volume\_cm3 | 0.0085 | 0.0899 | 0.4068 | yes |
| 5 | total\_price | 0.0075 | 0.0795 | 0.4863 | yes |
| 6 | n\_items | 0.0073 | 0.0769 | 0.5632 | yes |
| 7 | product\_description\_lenght | 0.0054 | 0.0566 | 0.6198 | yes |
| 8 | customer\_state | 0.0051 | 0.0538 | 0.6737 | yes |
| 9 | total\_weight\_g | 0.0050 | 0.0530 | 0.7266 | yes |
| 10 | n\_products | 0.0044 | 0.0468 | 0.7735 | yes |
| 11 | n\_sellers | 0.0041 | 0.0432 | 0.8166 | yes |
| 12 | purchase\_month | 0.0040 | 0.0421 | 0.8587 | yes |
| 13 | distance\_km\_max | 0.0035 | 0.0368 | 0.8955 | yes |
| 14 | interstate\_share | 0.0026 | 0.0277 | 0.9232 | yes |
| 15 | primary\_category | 0.0026 | 0.0275 | 0.9507 | yes |
| 16 | n\_categories | 0.0016 | 0.0164 | 0.9671 | yes |
| 17 | primary\_seller\_state | 0.0009 | 0.0094 | 0.9765 | yes |
| 18 | payment\_installments\_max | 0.0008 | 0.0084 | 0.9849 | yes |
| 19 | product\_photos\_qty | 0.0005 | 0.0057 | 0.9906 | yes |
| 20 | category\_missing\_fraction | 0.0004 | 0.0045 | 0.9951 | no |
| 21 | purchase\_hour | 0.0003 | 0.0034 | 0.9985 | no |
| 22 | purchase\_dayofweek | 0.0001 | 0.0011 | 0.9996 | no |
| 23 | distance\_missing\_fraction | 0.0000 | 0.0003 | 0.9999 | no |
| 24 | primary\_payment\_type | 0.0000 | 0.0001 | 1.0000 | no |
| 25 | volume\_missing\_fraction | 0.0000 | 0.0000 | 1.0000 | no |
| 26 | n\_payment\_methods | 0.0000 | 0.0000 | 1.0000 | no |

&#91;image: Cumulative share, classification\]

**Check** every computation reads only pre-cutoff rows: PASS (latest purchase 2018-05-26 12:12:15, cutoff 2018-05-26 12:16:34; 77,736 rows) **Check** ranked feature set equals contract.pool(task) and shares sum to 1: PASS (27 features, measure: mutual information) **Check** threshold and collinearity drops read from human\_decisions.yaml: PASS (threshold 0.99; team drops 0)

**Files** (stages/s04\_features/classification/outputs/, run 20261020T062543Z): selection\_ranking.csv, figures/selection\_cumulative.png, figures/selection\_cumulative.csv, figures/selection\_cumulative.json, decision.json

## 4.6 Rationale

**Approved solution:** Each kept feature: formula, grain, checkout availability, missingness, hypothesised signal, verified citation

**What was done (round 3):** feature\_dictionary.csv: 33 rows (every pool feature and the derived missing indicators): formula, grain, checkout availability, missingness, transform, imputation, kept and reason, hypothesised signal and claim type; 9 rows cite a source checked in Experiment 5 (9 of 25 kept).

**Reasoning:** References are carried from the Milestone 2 report and are not yet verified against their sources; the hypotheses are tested only by the models (s06-s08).

**Rounds 2–3 (lead and Henry):** Milestone 2 references removed (round 2); papers re-checked in this experiment (round 3, G-76). Deshpande & Pendem (2023) and Leite et al. (2024) support, at abstract level, that longer or late delivery lowers customer ratings, so they are cited for the nine delivery proxies (distance, interstate share, both states, freight, freight ratio, weight, volume, number of sellers). Cui et al. (2024) studies the promised delivery speed and is not cited. Every other signal is an unmeasured mechanism.

**Deviation (round 3):** Verified citation for 9 of 25 kept features; the blueprint asks for one per kept feature. The others are stated as unmeasured mechanisms (no source from earlier experiments).

| feature | source | kind | missing\_share | transform | imputation | kept | reason | hypothesised\_signal | claim\_type | sources |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| n\_items | contract predictor (G-61) | numeric | 0.0000 | never logged: integer count (G-62, G-70) | median (no missing value on pre-cutoff orders) | yes | selected: rank 6 of 26 in the core ranking, cumulative share 0.5632 reached within 99% | more items mean more picking and packing and more chances that one item is late or wrong | unmeasured mechanism | — |
| n\_products | contract predictor (G-61) | numeric | 0.0000 | never logged: integer count (G-62, G-70) | median (no missing value on pre-cutoff orders) | yes | selected: rank 10 of 26 in the core ranking, cumulative share 0.7735 reached within 99% | distinct products widen the chance of a stock or quality problem | unmeasured mechanism | — |
| n\_sellers | contract predictor (G-61) | numeric | 0.0000 | never logged: integer count (G-62, G-70) | median (no missing value on pre-cutoff orders) | yes | selected: rank 11 of 26 in the core ranking, cumulative share 0.8166 reached within 99% | several sellers ship separate parcels, so the order is complete only when the slowest one arrives | literature-supported hypothesis | Deshpande, V; Leite, G |
| n\_categories | contract predictor (G-61) | numeric | 0.0000 | never logged: integer count (G-62, G-70) | median (no missing value on pre-cutoff orders) | yes | selected: rank 16 of 26 in the core ranking, cumulative share 0.9671 reached within 99% | mixed baskets combine items with different handling | unmeasured mechanism | — |
| total\_price | contract predictor (G-61) | numeric | 0.0000 | log1p because pre-cutoff skewness 10.06 > 1 | median (no missing value on pre-cutoff orders) | yes | selected: rank 5 of 26 in the core ranking, cumulative share 0.4863 reached within 99% | expensive orders raise expectations and may get different handling | unmeasured mechanism | — |
| total\_freight | contract predictor (G-61) | numeric | 0.0000 | log1p because pre-cutoff skewness 8.10 > 1 | median (no missing value on pre-cutoff orders) | yes | selected: rank 2 of 26 in the core ranking, cumulative share 0.2238 reached within 99% | freight reflects distance, weight and carrier service level | literature-supported hypothesis | Deshpande, V; Leite, G |
| freight\_ratio | contract predictor (G-61) | numeric | 0.0000 | never logged: team decision in the s01 review (G-62) | median (no missing value on pre-cutoff orders) | yes | selected: rank 3 of 26 in the core ranking, cumulative share 0.3169 reached within 99% | a freight cost high relative to the price may disappoint the customer | literature-supported hypothesis | Deshpande, V; Leite, G |
| total\_weight\_g | contract predictor (G-61) | numeric | 0.0002 | log1p because pre-cutoff skewness 6.59 > 1 | median + missing indicator | yes | selected: rank 9 of 26 in the core ranking, cumulative share 0.7266 reached within 99% | heavy parcels travel by slower freight services | literature-supported hypothesis | Deshpande, V; Leite, G |
| total\_volume\_cm3 | contract predictor (G-61) | numeric | 0.0002 | log1p because pre-cutoff skewness 7.48 > 1 | median + missing indicator | yes | selected: rank 4 of 26 in the core ranking, cumulative share 0.4068 reached within 99% | bulky parcels travel by slower freight services | literature-supported hypothesis | Deshpande, V; Leite, G |
| weight\_missing\_fraction | contract predictor (G-61) | numeric | 0.0000 | never logged: bounded 0-1 share (G-47) | median (no missing value on pre-cutoff orders) | no | dropped in reduction (4.3): duplicate, identical to volume\_missing\_fraction on every pre-cutoff order; volume\_missing\_fraction ranks higher (25 vs 26) | missing catalogue dimensions mark less complete listings | unmeasured mechanism | — |
| volume\_missing\_fraction | contract predictor (G-61) | numeric | 0.0000 | never logged: bounded 0-1 share (G-47) | median (no missing value on pre-cutoff orders) | no | not selected: rank 25 of 26, after the 99% cut | missing catalogue dimensions mark less complete listings | unmeasured mechanism | — |
| primary\_category | contract predictor (G-61) | categorical | 0.0000 | categorical: one-hot, never logged | missing -> 'Unknown' level | yes | selected: rank 15 of 26 in the core ranking, cumulative share 0.9507 reached within 99% | categories differ in handling, seller mix and customer expectations | unmeasured mechanism | — |
| category\_missing\_fraction | contract predictor (G-61) | numeric | 0.0000 | never logged: bounded 0-1 share (G-47) | median (no missing value on pre-cutoff orders) | no | not selected: rank 20 of 26, after the 99% cut | a missing category marks less complete listings | unmeasured mechanism | — |
| customer\_state | contract predictor (G-61) | categorical | 0.0000 | categorical: one-hot, never logged | missing -> 'Unknown' level | yes | selected: rank 8 of 26 in the core ranking, cumulative share 0.6737 reached within 99% | destination region drives the transport route and its reliability | literature-supported hypothesis | Deshpande, V; Leite, G |
| primary\_seller\_state | contract predictor (G-61) | categorical | 0.0000 | categorical: one-hot, never logged | missing -> 'Unknown' level | yes | selected: rank 17 of 26 in the core ranking, cumulative share 0.9765 reached within 99% | origin region drives the transport route and its reliability | literature-supported hypothesis | Deshpande, V; Leite, G |
| distance\_km\_max | contract predictor (G-61) | numeric | 0.0117 | log1p because pre-cutoff skewness 1.64 > 1 | route median (customer\_state x primary\_seller\_state, then customer\_state, then global) + distance\_km\_max\_missing (G-27) | yes | selected: rank 13 of 26 in the core ranking, cumulative share 0.8955 reached within 99% | longer customer-seller distance means longer transit | literature-supported hypothesis | Deshpande, V; Leite, G |
| distance\_missing\_fraction | contract predictor (G-61) | numeric | 0.0000 | never logged: bounded 0-1 share (G-47) | median (no missing value on pre-cutoff orders) | no | not selected: rank 23 of 26, after the 99% cut | a missing location marks unusual or incomplete addresses | unmeasured mechanism | — |
| interstate\_share | contract predictor (G-61) | numeric | 0.0000 | never logged: bounded 0-1 share (G-47) | median (no missing value on pre-cutoff orders) | yes | selected: rank 14 of 26 in the core ranking, cumulative share 0.9232 reached within 99% | interstate legs add hand-overs and tax checkpoints | literature-supported hypothesis | Deshpande, V; Leite, G |
| purchase\_month | contract predictor (G-61) | numeric | 0.0000 | never logged: numeric calendar position (G-22, G-47) | median (no missing value on pre-cutoff orders) | yes | selected: rank 12 of 26 in the core ranking, cumulative share 0.8587 reached within 99% | seasonal peaks (e.g. year-end) load the logistics network | unmeasured mechanism | — |
| purchase\_dayofweek | contract predictor (G-61) | numeric | 0.0000 | never logged: numeric calendar position (G-22, G-47) | median (no missing value on pre-cutoff orders) | no | not selected: rank 22 of 26, after the 99% cut | orders placed before a weekend wait longer for dispatch | unmeasured mechanism | — |
| purchase\_hour | contract predictor (G-61) | numeric | 0.0000 | never logged: numeric calendar position (G-22, G-47) | median (no missing value on pre-cutoff orders) | no | not selected: rank 21 of 26, after the 99% cut | late orders miss the same-day dispatch cut-off | unmeasured mechanism | — |
| primary\_payment\_type | contract predictor (G-61) | categorical | 0.0000 | categorical: one-hot, never logged | missing -> 'Unknown' level | no | not selected: rank 24 of 26, after the 99% cut | boleto payments clear later than cards, delaying dispatch | unmeasured mechanism | — |
| payment\_installments\_max | contract predictor (G-61) | numeric | 0.0000 | never logged: integer count (G-62, G-70) | median (no missing value on pre-cutoff orders) | yes | selected: rank 18 of 26 in the core ranking, cumulative share 0.9849 reached within 99% | instalments relate to order value and buyer profile | unmeasured mechanism | — |
| n\_payment\_methods | contract predictor (G-61) | numeric | 0.0000 | never logged: integer count (G-62, G-70) | median (no missing value on pre-cutoff orders) | no | not selected: rank 26 of 26, after the 99% cut | split payments are rare and may mark unusual orders | unmeasured mechanism | — |
| product\_photos\_qty | adopted candidate (G-70) | numeric | 0.0167 | never logged: integer count (G-62, G-70) | median + missing indicator | yes | selected: rank 19 of 26 in the core ranking, cumulative share 0.9906 reached within 99% | listings with more photos set clearer expectations | unmeasured mechanism | — |
| product\_description\_lenght | adopted candidate (G-70) | numeric | 0.0167 | log1p because pre-cutoff skewness 2.05 > 1 | median + missing indicator | yes | selected: rank 7 of 26 in the core ranking, cumulative share 0.6198 reached within 99% | longer descriptions set clearer expectations | unmeasured mechanism | — |
| seller\_prior\_review\_mean | adopted candidate (G-70) | numeric | 0.0683 | never logged: 1-5 rating (G-70) | median + missing indicator | yes | selected: rank 1 of 26 in the core ranking, cumulative share 0.1159 reached within 99% | the seller rating shown at checkout summarises the seller's past service | unmeasured mechanism | — |
| missingindicator\_seller\_prior\_review\_mean | derived from seller\_prior\_review\_mean in the fold pipeline | numeric (0/1) | 0.0000 | never logged: 0/1 indicator (G-47) | none | yes | kept with its parent seller\_prior\_review\_mean (6.83% missing on pre-cutoff orders); not ranked | a missing value carries its own meaning (e.g. a seller without an earlier review) | unmeasured mechanism | — |
| missingindicator\_total\_volume\_cm3 | derived from total\_volume\_cm3 in the fold pipeline | numeric (0/1) | 0.0000 | never logged: 0/1 indicator (G-47) | none | yes | kept with its parent total\_volume\_cm3 (0.02% missing on pre-cutoff orders); not ranked | a missing value carries its own meaning | unmeasured mechanism | — |
| missingindicator\_product\_description\_lenght | derived from product\_description\_lenght in the fold pipeline | numeric (0/1) | 0.0000 | never logged: 0/1 indicator (G-47) | none | yes | kept with its parent product\_description\_lenght (1.67% missing on pre-cutoff orders); not ranked | a missing value carries its own meaning | unmeasured mechanism | — |
| missingindicator\_total\_weight\_g | derived from total\_weight\_g in the fold pipeline | numeric (0/1) | 0.0000 | never logged: 0/1 indicator (G-47) | none | yes | kept with its parent total\_weight\_g (0.02% missing on pre-cutoff orders); not ranked | a missing value carries its own meaning | unmeasured mechanism | — |
| distance\_km\_max\_missing | derived from distance\_km\_max in the fold pipeline | numeric (0/1) | 0.0000 | never logged: 0/1 indicator (G-47) | none | yes | kept with its parent distance\_km\_max (1.17% missing on pre-cutoff orders); not ranked | a missing value carries its own meaning | unmeasured mechanism | — |
| missingindicator\_product\_photos\_qty | derived from product\_photos\_qty in the fold pipeline | numeric (0/1) | 0.0000 | never logged: 0/1 indicator (G-47) | none | yes | kept with its parent product\_photos\_qty (1.67% missing on pre-cutoff orders); not ranked | a missing value carries its own meaning | unmeasured mechanism | — |

**Sources (checked in Experiment 5, 2026-10-20, publisher record and abstract):**

- Deshpande, V. & Pendem, P. K. (2023). Logistics Performance, Ratings, and Its Impact on Customer Purchasing Behavior and Sales in E-Commerce Platforms. Manufacturing & Service Operations Management 25(3):827-845. doi:10.1287/msom.2021.1045
- Leite, G. A. de A., Pinochet, L. H. C., Pardim, V. I. & Onusic, L. M. (2024). Uso de Machine Learning para entendimento das relações de consumo no modelo de negócio (SaaS enabled Marketplace) do Olist. Revista Tecnologia e Sociedade 20(60):328. doi:10.3895/rts.v20n60.16920

**Check** feature\_dictionary covers every pool feature and every selected feature has a rationale: PASS

**Files** (stages/s04\_features/classification/outputs/, run 20261020T062543Z): feature\_dictionary.csv

## 4.7 Selected set

**Approved solution:** One selected set per task, used by every model family (G-49). Pool: the 24 contract predictors; classification adds product\_photos\_qty, product\_description\_lenght and seller\_prior\_review\_mean, adopted at the s03 gate (G-70)

**What was done:** selected\_features.json: 19 features (16 numeric, 3 categorical), 6 derived missing indicators, log1p inputs \['total\_freight', 'total\_volume\_cm3', 'total\_price', 'product\_description\_lenght', 'total\_weight\_g', 'distance\_km\_max'\]; one set used by every family (G-49).

| Item | Value |
| --- | --- |
| selected (in ranking order) | seller\_prior\_review\_mean, total\_freight, freight\_ratio, total\_volume\_cm3, total\_price, n\_items, product\_description\_lenght, customer\_state, total\_weight\_g, n\_products, n\_sellers, purchase\_month, distance\_km\_max, interstate\_share, primary\_category, n\_categories, primary\_seller\_state, payment\_installments\_max, product\_photos\_qty |
| numeric | seller\_prior\_review\_mean, total\_freight, freight\_ratio, total\_volume\_cm3, total\_price, n\_items, product\_description\_lenght, total\_weight\_g, n\_products, n\_sellers, purchase\_month, distance\_km\_max, interstate\_share, n\_categories, payment\_installments\_max, product\_photos\_qty |
| categorical | customer\_state, primary\_category, primary\_seller\_state |
| log1p inputs | total\_freight, total\_volume\_cm3, total\_price, product\_description\_lenght, total\_weight\_g, distance\_km\_max |
| derived missing indicators | missingindicator\_seller\_prior\_review\_mean, missingindicator\_total\_volume\_cm3, missingindicator\_product\_description\_lenght, missingindicator\_total\_weight\_g, distance\_km\_max\_missing, missingindicator\_product\_photos\_qty |
| route median | distance\_km\_max |
| log target | no |
| threshold | 99% |

**Check** selected set and threshold recorded in protocol.yaml (data\_dependent.selected\_set): PASS **Check** order\_estimated\_delivery\_date and est\_delivery\_days are not features (G-35): PASS

**Files** (stages/s04\_features/classification/outputs/, run 20261020T062543Z): selected\_features.json, decision.json

## 4.8 Pipeline recipe

**Approved solution:** Per family: median imputation + missing indicators, except distance\_km\_max, which takes the route median (customer\_state × primary\_seller\_state; fallback customer\_state, then global; after log1p) learned in each training fold; one-hot with unknown handling (drop-first for linear/logistic only); scaling for linear/logistic only; fitted later inside folds

**What was done:** recipes.json: one e5lib.factory spec per family (dummy = dummy\_prior, linear = logistic, tree = tree\_clf, forest = forest\_clf): log1p, median imputation with missing indicators, route median for distance\_km\_max, one-hot with unknown levels ignored (drop-first and StandardScaler for linear/logistic only).

**Conclusion:** Fitted only inside each training fold in s06-s08 (G-27).

| family | estimator | numeric | route median | categorical | scaling | duplicates |
| --- | --- | --- | --- | --- | --- | --- |
| dummy | dummy\_prior | log1p (columns in log\_inputs) then median imputation with a missing indicator per column that has missing values in the training fold | distance\_km\_max: missing values filled with the median of customer\_state x primary\_seller\_state, else customer\_state, else the global median, learned in the training fold, plus distance\_km\_max\_missing (G-27) | missing -> 'Unknown'; one-hot, handle\_unknown='ignore' | none | encoded columns identical to an earlier column in the training fold are dropped (4.3 rule; e.g. the missing indicators of fields that are always missing together) |
| linear | logistic | log1p (columns in log\_inputs) then median imputation with a missing indicator per column that has missing values in the training fold; StandardScaler | distance\_km\_max: missing values filled with the median of customer\_state x primary\_seller\_state, else customer\_state, else the global median, learned in the training fold, plus distance\_km\_max\_missing (G-27) | missing -> 'Unknown'; one-hot, handle\_unknown='ignore', drop='first' | StandardScaler | encoded columns identical to an earlier column in the training fold are dropped (4.3 rule; e.g. the missing indicators of fields that are always missing together) |
| tree | tree\_clf | log1p (columns in log\_inputs) then median imputation with a missing indicator per column that has missing values in the training fold | distance\_km\_max: missing values filled with the median of customer\_state x primary\_seller\_state, else customer\_state, else the global median, learned in the training fold, plus distance\_km\_max\_missing (G-27) | missing -> 'Unknown'; one-hot, handle\_unknown='ignore' | none | encoded columns identical to an earlier column in the training fold are dropped (4.3 rule; e.g. the missing indicators of fields that are always missing together) |
| forest | forest\_clf | log1p (columns in log\_inputs) then median imputation with a missing indicator per column that has missing values in the training fold | distance\_km\_max: missing values filled with the median of customer\_state x primary\_seller\_state, else customer\_state, else the global median, learned in the training fold, plus distance\_km\_max\_missing (G-27) | missing -> 'Unknown'; one-hot, handle\_unknown='ignore' | none | encoded columns identical to an earlier column in the training fold are dropped (4.3 rule; e.g. the missing indicators of fields that are always missing together) |

**Check** linear/logistic design matrix has full column rank after the duplicate rule: PASS (rank 138 of 138; tree recipe (full one-hot, no scaling) is rank-deficient by design: each categorical's dummies sum to 1, which does not affect trees) **Check** no fitted object saved in the outputs: PASS (none) **Check** every family recipe builds an estimator from e5lib.factory: PASS

**Files** (stages/s04\_features/classification/outputs/, run 20261020T062543Z): recipes.json, design\_matrix.csv
