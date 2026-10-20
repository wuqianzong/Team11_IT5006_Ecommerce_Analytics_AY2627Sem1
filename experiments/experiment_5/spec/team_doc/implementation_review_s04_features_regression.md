# s04 Features › regression — evidence cards

Round 1 · run `20261020T062548Z` · 12 checks, all PASS. Coverage, decisions and review dropdowns are on the parent tab "s04 Features"; comment on any card here.

## 4.1 Baseline

**Approved solution:** The 24 predictors of e5lib/contract.py (G-61; has\_items, freight\_ratio\_missing and payment\_missing are not in the contract: the first two leak a later cancellation, payment\_missing is constant after 2.11; G-30, G-42, G-51); `purchase_month`, `purchase_dayofweek`, `purchase_hour` numeric. Classification adds the three candidates adopted at the s03 gate: product\_photos\_qty, product\_description\_lenght, seller\_prior\_review\_mean (G-70)

**What was done:** Pool from e5lib.contract.pool('regression'): 24 features = 24 contract predictors; 4 categorical, calendar fields numeric (G-22).

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

**Check** order\_estimated\_delivery\_date and est\_delivery\_days are not features (G-35): PASS

**Files** (stages/s04\_features/regression/outputs/, run 20261020T062548Z): baseline\_pool.csv

## 4.2 Transforms

**Approved solution:** log1p only for the five contract candidates total\_price, total\_freight, total\_weight\_g, total\_volume\_cm3, distance\_km\_max, each with pre-cutoff skewness > 1, and for classification product\_description\_lenght under the same rule (photo count and seller rating never logged; G-70); freight\_ratio, counts, calendar fields, 0/1 indicators and 0–1 shares never logged; missing values stay missing through log1p and are imputed afterwards (G-47, G-62); log1p regression target. No target cap: extreme values are handled by the s02 outlier removal and the log target

**What was done:** log1p for 5 of 5 candidates by pre-cutoff skewness > 1: total\_price 10.13; total\_freight 8.13; total\_weight\_g 6.63; total\_volume\_cm3 7.40; distance\_km\_max 1.64. Regression target log1p(lead\_days), scored in days (G-36); no target cap (G-25).

**Reasoning:** Missing values stay missing through log1p and are imputed afterwards inside the fold pipeline (G-47).

| feature | log\_candidate | skewness | log1p | rule |
| --- | --- | --- | --- | --- |
| n\_items | no | 7.85 | no | never logged: integer count (G-62, G-70) |
| n\_products | no | 7.68 | no | never logged: integer count (G-62, G-70) |
| n\_sellers | no | 10.11 | no | never logged: integer count (G-62, G-70) |
| n\_categories | no | -2.15 | no | never logged: integer count (G-62, G-70) |
| total\_price | yes | 10.13 | yes | log1p because pre-cutoff skewness 10.13 > 1 |
| total\_freight | yes | 8.13 | yes | log1p because pre-cutoff skewness 8.13 > 1 |
| freight\_ratio | no | 11.01 | no | never logged: team decision in the s01 review (G-62) |
| total\_weight\_g | yes | 6.63 | yes | log1p because pre-cutoff skewness 6.63 > 1 |
| total\_volume\_cm3 | yes | 7.40 | yes | log1p because pre-cutoff skewness 7.40 > 1 |
| weight\_missing\_fraction | no | 69.32 | no | never logged: bounded 0-1 share (G-47) |
| volume\_missing\_fraction | no | 69.32 | no | never logged: bounded 0-1 share (G-47) |
| primary\_category | no | — | no | categorical: one-hot, never logged |
| category\_missing\_fraction | no | 7.59 | no | never logged: bounded 0-1 share (G-47) |
| customer\_state | no | — | no | categorical: one-hot, never logged |
| primary\_seller\_state | no | — | no | categorical: one-hot, never logged |
| distance\_km\_max | yes | 1.64 | yes | log1p because pre-cutoff skewness 1.64 > 1 |
| distance\_missing\_fraction | no | 9.17 | no | never logged: bounded 0-1 share (G-47) |
| interstate\_share | no | -0.63 | no | never logged: bounded 0-1 share (G-47) |
| purchase\_month | no | 0.38 | no | never logged: numeric calendar position (G-22, G-47) |
| purchase\_dayofweek | no | 0.16 | no | never logged: numeric calendar position (G-22, G-47) |
| purchase\_hour | no | -0.61 | no | never logged: numeric calendar position (G-22, G-47) |
| primary\_payment\_type | no | — | no | categorical: one-hot, never logged |
| payment\_installments\_max | no | 1.59 | no | never logged: integer count (G-62, G-70) |
| n\_payment\_methods | no | 6.32 | no | never logged: integer count (G-62, G-70) |

**Check** every computation reads only pre-cutoff rows: PASS (latest purchase 2018-05-27 12:20:21, cutoff 2018-05-27 12:30:34; 76,925 rows) **Check** log1p only for the log1p candidates with skewness above the trigger: PASS (total\_price 10.13, total\_freight 8.13, total\_weight\_g 6.63, total\_volume\_cm3 7.40, distance\_km\_max 1.64) **Check** no target cap and no target among the features (G-25): PASS

**Files** (stages/s04\_features/regression/outputs/, run 20261020T062548Z): transforms.csv

## 4.3 Reduction

**Approved solution:** Drop constant and duplicate features automatically. Highly collinear features are only flagged, by cut-offs pre-registered in `protocol.yaml` (|correlation| > 0.9 or VIF > 10); for each flagged group the team decides which feature to drop, and the decision and its rationale are recorded in reduction\_rationale.csv and written into the report. Then report the encoded design-matrix rank and condition number per recipe

**What was done:** Core set 23 of 24: weight\_missing\_fraction dropped (duplicate, kept volume\_missing\_fraction). Team collinearity drops: 0 (none flagged in s03). Encoded design matrix: linear: 138 encoded columns, duplicates dropped \[missingindicator\_total\_volume\_cm3\], 137 columns, rank 137, condition number 424; tree: 142 encoded columns, duplicates dropped \[missingindicator\_total\_volume\_cm3\], 141 columns, rank 138, condition number 9.02e+16.

**Reasoning:** Rank and condition number are measured once on pre-cutoff rows; the preprocessing fitted for this measurement is not saved. Fields that are always missing together give identical missing indicators, so the 4.3 duplicate rule is applied to the encoded columns inside each training fold (factory step 'dedupe'); the linear/logistic matrix is then full rank. The tree recipe keeps every one-hot level, so its matrix is rank-deficient by design, which does not affect trees.

**Reduction** (reduction\_rationale.csv):

| feature | flagged\_by | paired\_with | team\_decision | rationale | decided\_by | date |
| --- | --- | --- | --- | --- | --- | --- |
| weight\_missing\_fraction | duplicate | volume\_missing\_fraction | drop (automatic) | identical to volume\_missing\_fraction on every pre-cutoff order; volume\_missing\_fraction ranks higher (22 vs 23) | rule s04 4.3 | 2026-10-20 |

**Encoded design matrix** (pre-cutoff rows; preprocessing fitted only for this measurement, not saved):

| family | estimator | rows | encoded\_columns | duplicates\_dropped | columns | rank | full\_rank | condition\_number |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear | linear | 76,925 | 138 | missingindicator\_total\_volume\_cm3 | 137 | 137 | yes | 424.1 |
| tree | tree\_reg | 76,925 | 142 | missingindicator\_total\_volume\_cm3 | 141 | 138 | no | 9.02e+16 |

**Check** every computation reads only pre-cutoff rows: PASS (latest purchase 2018-05-27 12:20:21, cutoff 2018-05-27 12:30:34; 76,925 rows) **Check** threshold and collinearity drops read from human\_decisions.yaml: PASS (threshold 0.99; team drops 0) **Check** every collinearity drop has a row in reduction\_rationale.csv: PASS **Check** linear/logistic design matrix has full column rank after the duplicate rule: PASS (rank 137 of 137; tree recipe (full one-hot, no scaling) is rank-deficient by design: each categorical's dummies sum to 1, which does not affect trees)

**Files** (stages/s04\_features/regression/outputs/, run 20261020T062548Z): reduction\_rationale.csv, design\_matrix.csv

## 4.4 Selection

**Approved solution:** Keep features in s03 ranking order until the cumulative share reaches the team's threshold (95% or 99%), fixed before any model is fitted. CV scores of the chosen set will be somewhat optimistic; the report says so

**What was done:** Core ranking by absolute Spearman, re-normalised over the 23 core features; 18 kept at the 99% threshold. Dropped by the cut: distance\_missing\_fraction, category\_missing\_fraction, n\_payment\_methods, volume\_missing\_fraction, purchase\_hour.

**Reasoning:** Declared exception (G-19): the ranking is computed once on pre-cutoff orders, so CV scores of the chosen set are optimistic; the report says so.

| rank | feature | value | share | cumulative\_share | selected |
| --- | --- | --- | --- | --- | --- |
| 1 | distance\_km\_max | 0.5411 | 0.1866 | 0.1866 | yes |
| 2 | customer\_state | 0.5059 | 0.1745 | 0.3612 | yes |
| 3 | interstate\_share | 0.4996 | 0.1723 | 0.5335 | yes |
| 4 | total\_freight | 0.4057 | 0.1399 | 0.6734 | yes |
| 5 | primary\_category | 0.1459 | 0.0503 | 0.7238 | yes |
| 6 | freight\_ratio | 0.1321 | 0.0456 | 0.7693 | yes |
| 7 | total\_price | 0.0935 | 0.0323 | 0.8016 | yes |
| 8 | primary\_seller\_state | 0.0913 | 0.0315 | 0.8331 | yes |
| 9 | total\_weight\_g | 0.0768 | 0.0265 | 0.8596 | yes |
| 10 | primary\_payment\_type | 0.0718 | 0.0248 | 0.8844 | yes |
| 11 | total\_volume\_cm3 | 0.0573 | 0.0198 | 0.9041 | yes |
| 12 | n\_sellers | 0.0484 | 0.0167 | 0.9208 | yes |
| 13 | payment\_installments\_max | 0.0475 | 0.0164 | 0.9372 | yes |
| 14 | purchase\_dayofweek | 0.0446 | 0.0154 | 0.9526 | yes |
| 15 | n\_products | 0.0397 | 0.0137 | 0.9663 | yes |
| 16 | purchase\_month | 0.0338 | 0.0117 | 0.9780 | yes |
| 17 | n\_items | 0.0278 | 0.0096 | 0.9875 | yes |
| 18 | n\_categories | 0.0130 | 0.0045 | 0.9920 | yes |
| 19 | distance\_missing\_fraction | 0.0101 | 0.0035 | 0.9955 | no |
| 20 | category\_missing\_fraction | 0.0060 | 0.0021 | 0.9975 | no |
| 21 | n\_payment\_methods | 0.0031 | 0.0011 | 0.9986 | no |
| 22 | volume\_missing\_fraction | 0.0022 | 0.0007 | 0.9994 | no |
| 23 | purchase\_hour | 0.0019 | 0.0006 | 1.0000 | no |

&#91;image: Cumulative share, regression\]

**Check** every computation reads only pre-cutoff rows: PASS (latest purchase 2018-05-27 12:20:21, cutoff 2018-05-27 12:30:34; 76,925 rows) **Check** ranked feature set equals contract.pool(task) and shares sum to 1: PASS (24 features, measure: absolute Spearman) **Check** threshold and collinearity drops read from human\_decisions.yaml: PASS (threshold 0.99; team drops 0)

**Files** (stages/s04\_features/regression/outputs/, run 20261020T062548Z): selection\_ranking.csv, figures/selection\_cumulative.png, figures/selection\_cumulative.csv, figures/selection\_cumulative.json, decision.json

## 4.6 Rationale

**Approved solution:** Each kept feature: formula, grain, checkout availability, missingness, hypothesised signal, verified citation

**What was done (round 3):** feature\_dictionary.csv: 27 rows (every pool feature and the derived missing indicators): formula, grain, checkout availability, missingness, transform, imputation, kept and reason, hypothesised signal and claim type; 0 rows cite a source checked in Experiment 5 (0 of 21 kept).

**Reasoning:** References are carried from the Milestone 2 report and are not yet verified against their sources; the hypotheses are tested only by the models (s06-s08).

**Rounds 2–3 (lead and Henry):** Milestone 2 references removed (round 2); papers re-checked in this experiment (round 3, G-76). Deshpande & Pendem (2023) and Leite et al. (2024) support, at abstract level, that longer or late delivery lowers customer ratings, so they are cited for the classification delivery proxies only. Neither tests lead time, so no regression feature has a verified source: every regression signal is an unmeasured mechanism. Cui et al. (2024) studies the promised delivery speed and is not cited.

**Deviation (round 3):** Verified citation for 0 of 21 kept features; the blueprint asks for one per kept feature. The others are stated as unmeasured mechanisms (no source from earlier experiments).

| feature | source | kind | missing\_share | transform | imputation | kept | reason | hypothesised\_signal | claim\_type | sources |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| n\_items | contract predictor (G-61) | numeric | 0.0000 | never logged: integer count (G-62, G-70) | median (no missing value on pre-cutoff orders) | yes | selected: rank 17 of 23 in the core ranking, cumulative share 0.9875 reached within 99% | more items mean more picking and packing and more chances that one item is late or wrong | unmeasured mechanism | — |
| n\_products | contract predictor (G-61) | numeric | 0.0000 | never logged: integer count (G-62, G-70) | median (no missing value on pre-cutoff orders) | yes | selected: rank 15 of 23 in the core ranking, cumulative share 0.9663 reached within 99% | distinct products widen the chance of a stock or quality problem | unmeasured mechanism | — |
| n\_sellers | contract predictor (G-61) | numeric | 0.0000 | never logged: integer count (G-62, G-70) | median (no missing value on pre-cutoff orders) | yes | selected: rank 12 of 23 in the core ranking, cumulative share 0.9208 reached within 99% | several sellers ship separate parcels, so the order is complete only when the slowest one arrives | unmeasured mechanism | — |
| n\_categories | contract predictor (G-61) | numeric | 0.0000 | never logged: integer count (G-62, G-70) | median (no missing value on pre-cutoff orders) | yes | selected: rank 18 of 23 in the core ranking, cumulative share 0.9920 reached within 99% | mixed baskets combine items with different handling | unmeasured mechanism | — |
| total\_price | contract predictor (G-61) | numeric | 0.0000 | log1p because pre-cutoff skewness 10.13 > 1 | median (no missing value on pre-cutoff orders) | yes | selected: rank 7 of 23 in the core ranking, cumulative share 0.8016 reached within 99% | expensive orders raise expectations and may get different handling | unmeasured mechanism | — |
| total\_freight | contract predictor (G-61) | numeric | 0.0000 | log1p because pre-cutoff skewness 8.13 > 1 | median (no missing value on pre-cutoff orders) | yes | selected: rank 4 of 23 in the core ranking, cumulative share 0.6734 reached within 99% | freight reflects distance, weight and carrier service level | unmeasured mechanism | — |
| freight\_ratio | contract predictor (G-61) | numeric | 0.0000 | never logged: team decision in the s01 review (G-62) | median (no missing value on pre-cutoff orders) | yes | selected: rank 6 of 23 in the core ranking, cumulative share 0.7693 reached within 99% | a freight cost high relative to the price may disappoint the customer | unmeasured mechanism | — |
| total\_weight\_g | contract predictor (G-61) | numeric | 0.0002 | log1p because pre-cutoff skewness 6.63 > 1 | median + missing indicator | yes | selected: rank 9 of 23 in the core ranking, cumulative share 0.8596 reached within 99% | heavy parcels travel by slower freight services | unmeasured mechanism | — |
| total\_volume\_cm3 | contract predictor (G-61) | numeric | 0.0002 | log1p because pre-cutoff skewness 7.40 > 1 | median + missing indicator | yes | selected: rank 11 of 23 in the core ranking, cumulative share 0.9041 reached within 99% | bulky parcels travel by slower freight services | unmeasured mechanism | — |
| weight\_missing\_fraction | contract predictor (G-61) | numeric | 0.0000 | never logged: bounded 0-1 share (G-47) | median (no missing value on pre-cutoff orders) | no | dropped in reduction (4.3): duplicate, identical to volume\_missing\_fraction on every pre-cutoff order; volume\_missing\_fraction ranks higher (22 vs 23) | missing catalogue dimensions mark less complete listings | unmeasured mechanism | — |
| volume\_missing\_fraction | contract predictor (G-61) | numeric | 0.0000 | never logged: bounded 0-1 share (G-47) | median (no missing value on pre-cutoff orders) | no | not selected: rank 22 of 23, after the 99% cut | missing catalogue dimensions mark less complete listings | unmeasured mechanism | — |
| primary\_category | contract predictor (G-61) | categorical | 0.0000 | categorical: one-hot, never logged | missing -> 'Unknown' level | yes | selected: rank 5 of 23 in the core ranking, cumulative share 0.7238 reached within 99% | categories differ in handling, seller mix and customer expectations | unmeasured mechanism | — |
| category\_missing\_fraction | contract predictor (G-61) | numeric | 0.0000 | never logged: bounded 0-1 share (G-47) | median (no missing value on pre-cutoff orders) | no | not selected: rank 20 of 23, after the 99% cut | a missing category marks less complete listings | unmeasured mechanism | — |
| customer\_state | contract predictor (G-61) | categorical | 0.0000 | categorical: one-hot, never logged | missing -> 'Unknown' level | yes | selected: rank 2 of 23 in the core ranking, cumulative share 0.3612 reached within 99% | destination region drives the transport route and its reliability | unmeasured mechanism | — |
| primary\_seller\_state | contract predictor (G-61) | categorical | 0.0000 | categorical: one-hot, never logged | missing -> 'Unknown' level | yes | selected: rank 8 of 23 in the core ranking, cumulative share 0.8331 reached within 99% | origin region drives the transport route and its reliability | unmeasured mechanism | — |
| distance\_km\_max | contract predictor (G-61) | numeric | 0.0116 | log1p because pre-cutoff skewness 1.64 > 1 | route median (customer\_state x primary\_seller\_state, then customer\_state, then global) + distance\_km\_max\_missing (G-27) | yes | selected: rank 1 of 23 in the core ranking, cumulative share 0.1866 reached within 99% | longer customer-seller distance means longer transit | unmeasured mechanism | — |
| distance\_missing\_fraction | contract predictor (G-61) | numeric | 0.0000 | never logged: bounded 0-1 share (G-47) | median (no missing value on pre-cutoff orders) | no | not selected: rank 19 of 23, after the 99% cut | a missing location marks unusual or incomplete addresses | unmeasured mechanism | — |
| interstate\_share | contract predictor (G-61) | numeric | 0.0000 | never logged: bounded 0-1 share (G-47) | median (no missing value on pre-cutoff orders) | yes | selected: rank 3 of 23 in the core ranking, cumulative share 0.5335 reached within 99% | interstate legs add hand-overs and tax checkpoints | unmeasured mechanism | — |
| purchase\_month | contract predictor (G-61) | numeric | 0.0000 | never logged: numeric calendar position (G-22, G-47) | median (no missing value on pre-cutoff orders) | yes | selected: rank 16 of 23 in the core ranking, cumulative share 0.9780 reached within 99% | seasonal peaks (e.g. year-end) load the logistics network | unmeasured mechanism | — |
| purchase\_dayofweek | contract predictor (G-61) | numeric | 0.0000 | never logged: numeric calendar position (G-22, G-47) | median (no missing value on pre-cutoff orders) | yes | selected: rank 14 of 23 in the core ranking, cumulative share 0.9526 reached within 99% | orders placed before a weekend wait longer for dispatch | unmeasured mechanism | — |
| purchase\_hour | contract predictor (G-61) | numeric | 0.0000 | never logged: numeric calendar position (G-22, G-47) | median (no missing value on pre-cutoff orders) | no | not selected: rank 23 of 23, after the 99% cut | late orders miss the same-day dispatch cut-off | unmeasured mechanism | — |
| primary\_payment\_type | contract predictor (G-61) | categorical | 0.0000 | categorical: one-hot, never logged | missing -> 'Unknown' level | yes | selected: rank 10 of 23 in the core ranking, cumulative share 0.8844 reached within 99% | boleto payments clear later than cards, delaying dispatch | unmeasured mechanism | — |
| payment\_installments\_max | contract predictor (G-61) | numeric | 0.0000 | never logged: integer count (G-62, G-70) | median (no missing value on pre-cutoff orders) | yes | selected: rank 13 of 23 in the core ranking, cumulative share 0.9372 reached within 99% | instalments relate to order value and buyer profile | unmeasured mechanism | — |
| n\_payment\_methods | contract predictor (G-61) | numeric | 0.0000 | never logged: integer count (G-62, G-70) | median (no missing value on pre-cutoff orders) | no | not selected: rank 21 of 23, after the 99% cut | split payments are rare and may mark unusual orders | unmeasured mechanism | — |
| distance\_km\_max\_missing | derived from distance\_km\_max in the fold pipeline | numeric (0/1) | 0.0000 | never logged: 0/1 indicator (G-47) | none | yes | kept with its parent distance\_km\_max (1.16% missing on pre-cutoff orders); not ranked | a missing value carries its own meaning | unmeasured mechanism | — |
| missingindicator\_total\_weight\_g | derived from total\_weight\_g in the fold pipeline | numeric (0/1) | 0.0000 | never logged: 0/1 indicator (G-47) | none | yes | kept with its parent total\_weight\_g (0.02% missing on pre-cutoff orders); not ranked | a missing value carries its own meaning | unmeasured mechanism | — |
| missingindicator\_total\_volume\_cm3 | derived from total\_volume\_cm3 in the fold pipeline | numeric (0/1) | 0.0000 | never logged: 0/1 indicator (G-47) | none | yes | kept with its parent total\_volume\_cm3 (0.02% missing on pre-cutoff orders); not ranked | a missing value carries its own meaning | unmeasured mechanism | — |

**Check** feature\_dictionary covers every pool feature and every selected feature has a rationale: PASS

**Files** (stages/s04\_features/regression/outputs/, run 20261020T062548Z): feature\_dictionary.csv

## 4.7 Selected set

**Approved solution:** One selected set per task, used by every model family (G-49). Pool: the 24 contract predictors; classification adds product\_photos\_qty, product\_description\_lenght and seller\_prior\_review\_mean, adopted at the s03 gate (G-70)

**What was done:** selected\_features.json: 18 features (14 numeric, 4 categorical), 3 derived missing indicators, log1p inputs \['distance\_km\_max', 'total\_freight', 'total\_price', 'total\_weight\_g', 'total\_volume\_cm3'\]; one set used by every family (G-49).

| Item | Value |
| --- | --- |
| selected (in ranking order) | distance\_km\_max, customer\_state, interstate\_share, total\_freight, primary\_category, freight\_ratio, total\_price, primary\_seller\_state, total\_weight\_g, primary\_payment\_type, total\_volume\_cm3, n\_sellers, payment\_installments\_max, purchase\_dayofweek, n\_products, purchase\_month, n\_items, n\_categories |
| numeric | distance\_km\_max, interstate\_share, total\_freight, freight\_ratio, total\_price, total\_weight\_g, total\_volume\_cm3, n\_sellers, payment\_installments\_max, purchase\_dayofweek, n\_products, purchase\_month, n\_items, n\_categories |
| categorical | customer\_state, primary\_category, primary\_seller\_state, primary\_payment\_type |
| log1p inputs | distance\_km\_max, total\_freight, total\_price, total\_weight\_g, total\_volume\_cm3 |
| derived missing indicators | distance\_km\_max\_missing, missingindicator\_total\_weight\_g, missingindicator\_total\_volume\_cm3 |
| route median | distance\_km\_max |
| log target | yes |
| threshold | 99% |

**Check** selected set and threshold recorded in protocol.yaml (data\_dependent.selected\_set): PASS **Check** order\_estimated\_delivery\_date and est\_delivery\_days are not features (G-35): PASS

**Files** (stages/s04\_features/regression/outputs/, run 20261020T062548Z): selected\_features.json, decision.json

## 4.8 Pipeline recipe

**Approved solution:** Per family: median imputation + missing indicators, except distance\_km\_max, which takes the route median (customer\_state × primary\_seller\_state; fallback customer\_state, then global; after log1p) learned in each training fold; one-hot with unknown handling (drop-first for linear/logistic only); scaling for linear/logistic only; fitted later inside folds

**What was done:** recipes.json: one e5lib.factory spec per family (dummy = dummy\_median, linear = linear, tree = tree\_reg, forest = forest\_reg): log1p, median imputation with missing indicators, route median for distance\_km\_max, one-hot with unknown levels ignored (drop-first and StandardScaler for linear/logistic only).

**Conclusion:** Fitted only inside each training fold in s06-s08 (G-27).

| family | estimator | numeric | route median | categorical | scaling | duplicates |
| --- | --- | --- | --- | --- | --- | --- |
| dummy | dummy\_median | log1p (columns in log\_inputs) then median imputation with a missing indicator per column that has missing values in the training fold | distance\_km\_max: missing values filled with the median of customer\_state x primary\_seller\_state, else customer\_state, else the global median, learned in the training fold, plus distance\_km\_max\_missing (G-27) | missing -> 'Unknown'; one-hot, handle\_unknown='ignore' | none | encoded columns identical to an earlier column in the training fold are dropped (4.3 rule; e.g. the missing indicators of fields that are always missing together) |
| linear | linear | log1p (columns in log\_inputs) then median imputation with a missing indicator per column that has missing values in the training fold; StandardScaler | distance\_km\_max: missing values filled with the median of customer\_state x primary\_seller\_state, else customer\_state, else the global median, learned in the training fold, plus distance\_km\_max\_missing (G-27) | missing -> 'Unknown'; one-hot, handle\_unknown='ignore', drop='first' | StandardScaler | encoded columns identical to an earlier column in the training fold are dropped (4.3 rule; e.g. the missing indicators of fields that are always missing together) |
| tree | tree\_reg | log1p (columns in log\_inputs) then median imputation with a missing indicator per column that has missing values in the training fold | distance\_km\_max: missing values filled with the median of customer\_state x primary\_seller\_state, else customer\_state, else the global median, learned in the training fold, plus distance\_km\_max\_missing (G-27) | missing -> 'Unknown'; one-hot, handle\_unknown='ignore' | none | encoded columns identical to an earlier column in the training fold are dropped (4.3 rule; e.g. the missing indicators of fields that are always missing together) |
| forest | forest\_reg | log1p (columns in log\_inputs) then median imputation with a missing indicator per column that has missing values in the training fold | distance\_km\_max: missing values filled with the median of customer\_state x primary\_seller\_state, else customer\_state, else the global median, learned in the training fold, plus distance\_km\_max\_missing (G-27) | missing -> 'Unknown'; one-hot, handle\_unknown='ignore' | none | encoded columns identical to an earlier column in the training fold are dropped (4.3 rule; e.g. the missing indicators of fields that are always missing together) |

**Check** linear/logistic design matrix has full column rank after the duplicate rule: PASS (rank 137 of 137; tree recipe (full one-hot, no scaling) is rank-deficient by design: each categorical's dummies sum to 1, which does not affect trees) **Check** no fitted object saved in the outputs: PASS (none) **Check** every family recipe builds an estimator from e5lib.factory: PASS

**Files** (stages/s04\_features/regression/outputs/, run 20261020T062548Z): recipes.json, design\_matrix.csv
