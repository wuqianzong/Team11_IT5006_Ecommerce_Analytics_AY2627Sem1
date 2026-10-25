# B4 › regression — evidence cards

## Supplement for decisions and the report (added 2026-10-24; DOC\_GAPS D-03)

Added after the pipeline ran, from accepted outputs only; nothing above is changed. Charts marked doc\_support come from pipeline\_b/stages/doc\_support/regression/outputs (run 20261024T065707Z, uncommitted, reads accepted outputs only).

**Selection ranking with B's new features marked and the 99% cut** (doc\_support figures/b4\_selection.png; data: b04 selection\_ranking\_B.csv):

&#91;image: B4 selection\]

Round 2 (B-G-02, B-G-04; built, not yet committed) · run `20261023T153748Z` on uncommitted code (working tree on aed9cfa) · 5 checks, all PASS. Coverage and review dropdowns are on the parent tab "B4 Features"; comment on any card here.

## B4.1 Pool

**Approved solution (B4 blueprint):** Pool. A's task pool + B's candidates (B-C6 to B-C9; names B-G-04); route counts as one feature.

**What was done:** B pool: A's 24 pool features plus 6 B candidates (route\_seller\_to\_customer\_state, seller\_prior\_late\_handover\_rate, seller\_prior\_late\_handover\_days, seller\_prior\_dispatch\_days, route\_recent\_delivery\_days, route\_recent\_carrier\_transit\_days).

**Pool by source** (pool\_ranking\_B.csv): contract predictor 24; B-C7 3; B-C6 1; B-C8b 1; B-C8 1.

**Check** the ranked set equals B's pool: PASS (30 features) **Check** no feature from the estimated delivery date: PASS

**Files** (pipeline\_b/stages/b04/regression/outputs/, run 20261023T153748Z): pool\_ranking\_B.csv

## B4.2 Ranking

**Approved solution (B4 blueprint):** Ranking. A's ranking on B's development rows: |Spearman| with the log target for regression, mutual information for classification, as in A's s03/s04.

**What was done:** Ranking on B's development rows with A's measures (|Spearman|; rank correlation ratio for categorical): top 8 route\_seller\_to\_customer\_state 0.110; route\_recent\_carrier\_transit\_days 0.105; route\_recent\_delivery\_days 0.105; distance\_km\_max 0.105; interstate\_share 0.101; customer\_state 0.092; total\_freight 0.078; seller\_prior\_dispatch\_days 0.044.

**Full pool ranking** (pool\_ranking\_B.csv):

| rank | feature | source | method | value | share | cumulative\_share |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | route\_seller\_to\_customer\_state | B-C6 | rank correlation ratio | 0.5317 | 0.1100 | 0.1100 |
| 2 | route\_recent\_carrier\_transit\_days | B-C8b | absolute Spearman | 0.5099 | 0.1054 | 0.2154 |
| 3 | route\_recent\_delivery\_days | B-C8 | absolute Spearman | 0.5096 | 0.1054 | 0.3208 |
| 4 | distance\_km\_max | contract predictor | absolute Spearman | 0.5088 | 0.1052 | 0.4260 |
| 5 | interstate\_share | contract predictor | absolute Spearman | 0.4867 | 0.1007 | 0.5267 |
| 6 | customer\_state | contract predictor | rank correlation ratio | 0.4458 | 0.0922 | 0.6189 |
| 7 | total\_freight | contract predictor | absolute Spearman | 0.3772 | 0.0780 | 0.6969 |
| 8 | seller\_prior\_dispatch\_days | B-C7 | absolute Spearman | 0.2105 | 0.0435 | 0.7404 |
| 9 | primary\_category | contract predictor | rank correlation ratio | 0.1666 | 0.0344 | 0.7749 |
| 10 | seller\_prior\_late\_handover\_rate | B-C7 | absolute Spearman | 0.1548 | 0.0320 | 0.8069 |
| 11 | seller\_prior\_late\_handover\_days | B-C7 | absolute Spearman | 0.1389 | 0.0287 | 0.8356 |
| 12 | freight\_ratio | contract predictor | absolute Spearman | 0.1036 | 0.0214 | 0.8570 |
| 13 | primary\_seller\_state | contract predictor | rank correlation ratio | 0.1021 | 0.0211 | 0.8782 |
| 14 | total\_weight\_g | contract predictor | absolute Spearman | 0.0908 | 0.0188 | 0.8969 |
| 15 | total\_price | contract predictor | absolute Spearman | 0.0904 | 0.0187 | 0.9156 |
| 16 | primary\_payment\_type | contract predictor | rank correlation ratio | 0.0819 | 0.0169 | 0.9326 |
| 17 | total\_volume\_cm3 | contract predictor | absolute Spearman | 0.0757 | 0.0157 | 0.9482 |
| 18 | purchase\_dayofweek | contract predictor | absolute Spearman | 0.0468 | 0.0097 | 0.9579 |
| 19 | n\_sellers | contract predictor | absolute Spearman | 0.0450 | 0.0093 | 0.9672 |
| 20 | purchase\_month | contract predictor | absolute Spearman | 0.0366 | 0.0076 | 0.9748 |
| 21 | n\_products | contract predictor | absolute Spearman | 0.0336 | 0.0070 | 0.9818 |
| 22 | payment\_installments\_max | contract predictor | absolute Spearman | 0.0327 | 0.0068 | 0.9885 |
| 23 | n\_items | contract predictor | absolute Spearman | 0.0203 | 0.0042 | 0.9927 |
| 24 | n\_categories | contract predictor | absolute Spearman | 0.0123 | 0.0025 | 0.9953 |
| 25 | category\_missing\_fraction | contract predictor | absolute Spearman | 0.0057 | 0.0012 | 0.9965 |
| 26 | n\_payment\_methods | contract predictor | absolute Spearman | 0.0057 | 0.0012 | 0.9976 |
| 27 | purchase\_hour | contract predictor | absolute Spearman | 0.0053 | 0.0011 | 0.9987 |
| 28 | volume\_missing\_fraction | contract predictor | absolute Spearman | 0.0031 | 0.0006 | 0.9994 |
| 29 | weight\_missing\_fraction | contract predictor | absolute Spearman | 0.0031 | 0.0006 | 1.0000 |
| 30 | distance\_missing\_fraction | contract predictor | absolute Spearman |  |  | 1.0000 |

**Check** the ranked set equals B's pool: PASS (30 features)

**Files** (pipeline\_b/stages/b04/regression/outputs/, run 20261023T153748Z): pool\_ranking\_B.csv

## B4.3 Selection at 99% (B-C11)

**Approved solution (B4 blueprint):** Selection (B-C11). Keep the top features reaching 99% of the cumulative share (A's G-70 threshold). A feature below the cut is dropped with its rank and share recorded.

**What was done:** 21 of 26 core features kept at the 99% cumulative share (A's G-70 threshold). B features kept: route\_seller\_to\_customer\_state, route\_recent\_carrier\_transit\_days, route\_recent\_delivery\_days, seller\_prior\_dispatch\_days, seller\_prior\_late\_handover\_rate, seller\_prior\_late\_handover\_days; B features dropped: none. Reduction: 4 dropped (customer\_state: nested in route (B-G-02); primary\_seller\_state: nested in route (B-G-02); distance\_missing\_fraction: constant; weight\_missing\_fraction: duplicate).

**Reduction before selection** (reduction\_B.csv):

| feature | flagged\_by | paired\_with | rationale |
| --- | --- | --- | --- |
| customer\_state | nested in route (B-G-02) | route\_seller\_to\_customer\_state | every route\_seller\_to\_customer\_state level fixes customer\_state; its one-hot columns are sums of route's |
| primary\_seller\_state | nested in route (B-G-02) | route\_seller\_to\_customer\_state | every route\_seller\_to\_customer\_state level fixes primary\_seller\_state; its one-hot columns are sums of route's |
| distance\_missing\_fraction | constant | nan | one value on B rows |
| weight\_missing\_fraction | duplicate | volume\_missing\_fraction | identical to volume\_missing\_fraction on every B row; volume\_missing\_fraction ranks higher |

**Selection ranking on the core set** (selection\_ranking\_B.csv; kept = within 99%):

| rank | feature | source | share | cumulative\_share | selected |
| --- | --- | --- | --- | --- | --- |
| 1 | route\_seller\_to\_customer\_state | B-C6 | 0.1241 | 0.1241 | True |
| 2 | route\_recent\_carrier\_transit\_days | B-C8b | 0.1190 | 0.2431 | True |
| 3 | route\_recent\_delivery\_days | B-C8 | 0.1190 | 0.3621 | True |
| 4 | distance\_km\_max | contract predictor | 0.1188 | 0.4808 | True |
| 5 | interstate\_share | contract predictor | 0.1136 | 0.5944 | True |
| 6 | total\_freight | contract predictor | 0.0880 | 0.6825 | True |
| 7 | seller\_prior\_dispatch\_days | B-C7 | 0.0491 | 0.7316 | True |
| 8 | primary\_category | contract predictor | 0.0389 | 0.7705 | True |
| 9 | seller\_prior\_late\_handover\_rate | B-C7 | 0.0361 | 0.8066 | True |
| 10 | seller\_prior\_late\_handover\_days | B-C7 | 0.0324 | 0.8390 | True |
| 11 | freight\_ratio | contract predictor | 0.0242 | 0.8632 | True |
| 12 | total\_weight\_g | contract predictor | 0.0212 | 0.8844 | True |
| 13 | total\_price | contract predictor | 0.0211 | 0.9055 | True |
| 14 | primary\_payment\_type | contract predictor | 0.0191 | 0.9246 | True |
| 15 | total\_volume\_cm3 | contract predictor | 0.0177 | 0.9423 | True |
| 16 | purchase\_dayofweek | contract predictor | 0.0109 | 0.9532 | True |
| 17 | n\_sellers | contract predictor | 0.0105 | 0.9637 | True |
| 18 | purchase\_month | contract predictor | 0.0086 | 0.9723 | True |
| 19 | n\_products | contract predictor | 0.0078 | 0.9801 | True |
| 20 | payment\_installments\_max | contract predictor | 0.0076 | 0.9878 | True |
| 21 | n\_items | contract predictor | 0.0047 | 0.9925 | True |
| 22 | n\_categories | contract predictor | 0.0029 | 0.9954 | False |
| 23 | category\_missing\_fraction | contract predictor | 0.0013 | 0.9967 | False |
| 24 | n\_payment\_methods | contract predictor | 0.0013 | 0.9980 | False |
| 25 | purchase\_hour | contract predictor | 0.0012 | 0.9993 | False |
| 26 | volume\_missing\_fraction | contract predictor | 0.0007 | 1.0000 | False |

**Dropped below the threshold** (selected\_features\_B.json): n\_categories, category\_missing\_fraction, n\_payment\_methods, purchase\_hour, volume\_missing\_fraction.

**Check** the kept set is exactly the 99% cumulative-share prefix of the core ranking: PASS (21 of 26 kept)

**Files** (pipeline\_b/stages/b04/regression/outputs/, run 20261023T153748Z): reduction\_B.csv, selected\_features\_B.json, selection\_ranking\_B.csv

## B4.4 Transforms

**Approved solution (B4 blueprint):** Transforms. A's rules: log1p for skewed counts and all day counts; rates and flags scaled only; route one-hot (drop-first for linear/logistic, every level for trees); A's duplicate rule; imputation fitted inside the folds. B-G-02: with route in the pool, customer\_state and primary\_seller\_state are dropped in the reduction as nested in route; no route-median fill for distance\_km\_max, which B-C2 leaves never missing.

**What was done:** log1p on 9 features (total\_price, total\_freight, total\_weight\_g, total\_volume\_cm3, distance\_km\_max, seller\_prior\_late\_handover\_days, seller\_prior\_dispatch\_days, route\_recent\_delivery\_days, route\_recent\_carrier\_transit\_days); B day counts logged, B rates and flags scaled only.

**Transform per feature** (transforms\_B.csv):

| feature | skewness | log1p | rule |
| --- | --- | --- | --- |
| n\_items | 7.61 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| n\_products | 7.65 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| n\_sellers | 9.98 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| n\_categories | -1.98 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| total\_price | 11.03 | True | log1p because pre-cutoff skewness 11.03 > 1 (A's 4.2 rule on B rows) |
| total\_freight | 9.42 | True | log1p because pre-cutoff skewness 9.42 > 1 (A's 4.2 rule on B rows) |
| freight\_ratio | 15.32 | False | never logged: team decision in the s01 review (G-62) (A's 4.2 rule on B rows) |
| total\_weight\_g | 6.94 | True | log1p because pre-cutoff skewness 6.94 > 1 (A's 4.2 rule on B rows) |
| total\_volume\_cm3 | 7.63 | True | log1p because pre-cutoff skewness 7.63 > 1 (A's 4.2 rule on B rows) |
| weight\_missing\_fraction | 71.41 | False | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) |
| volume\_missing\_fraction | 71.41 | False | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) |
| primary\_category |  | False | categorical: one-hot, never logged (A's 4.2 rule on B rows) |
| category\_missing\_fraction | 7.61 | False | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) |
| customer\_state |  | False | categorical: one-hot, never logged (A's 4.2 rule on B rows) |
| primary\_seller\_state |  | False | categorical: one-hot, never logged (A's 4.2 rule on B rows) |
| distance\_km\_max | 1.26 | True | log1p because pre-cutoff skewness 1.26 > 1 (A's 4.2 rule on B rows) |
| distance\_missing\_fraction |  | False | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) |
| interstate\_share | -0.30 | False | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) |
| purchase\_month | 0.37 | False | never logged: numeric calendar position (G-22, G-47) (A's 4.2 rule on B rows) |
| purchase\_dayofweek | 0.16 | False | never logged: numeric calendar position (G-22, G-47) (A's 4.2 rule on B rows) |
| purchase\_hour | -0.61 | False | never logged: numeric calendar position (G-22, G-47) (A's 4.2 rule on B rows) |
| primary\_payment\_type |  | False | categorical: one-hot, never logged (A's 4.2 rule on B rows) |
| payment\_installments\_max | 1.65 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| n\_payment\_methods | 6.33 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| route\_seller\_to\_customer\_state |  | False | categorical: one-hot (drop-first for linear/logistic, every level for trees) |
| seller\_prior\_late\_handover\_rate | 3.03 | False | never logged: rate or flag, scaled only (Henry) |
| seller\_prior\_late\_handover\_days | 22.13 | True | log1p: day count (Henry) |
| seller\_prior\_dispatch\_days | 5.26 | True | log1p: day count (Henry) |
| route\_recent\_delivery\_days | 1.17 | True | log1p: day count (Henry) |
| route\_recent\_carrier\_transit\_days | 1.17 | True | log1p: day count (Henry) |

**Files** (pipeline\_b/stages/b04/regression/outputs/, run 20261023T153748Z): transforms\_B.csv

## B4.5 Recipes and dictionary (B-C12)

**Approved solution (B4 blueprint):** Recipes. One recipe per family (dummy, linear/logistic, tree, forest), built with A's code.

**What was done:** Recipes for dummy, linear/logistic, tree and forest with A's factory; linear design matrix rank 140 of 140; feature\_dictionary\_B.csv has 30 rows.

**Design matrices** (design\_matrix\_B.csv):

| family | rows | encoded\_columns | duplicates\_dropped | columns | rank | full\_rank | condition\_number |
| --- | --- | --- | --- | --- | --- | --- | --- |
| linear | 61,233 | 141 | missingindicator\_total\_volume\_cm3 | 140 | 140 | True | 253.2 |
| tree | 61,233 | 144 | missingindicator\_total\_volume\_cm3 | 143 | 141 | False | 77565488550624416.0 |

**Feature dictionary, B features** (feature\_dictionary\_B.csv; the file also holds A's inherited features, 30 rows in all):

| feature | definition | formula | reason | transform | kept | selection\_reason |
| --- | --- | --- | --- | --- | --- | --- |
| route\_seller\_to\_customer\_state | Route of the order: primary seller's state to the customer's state | primary\_seller\_state + '->' + customer\_state | delivery time and experience differ by origin-destination pair; captures interactions distance alone misses | categorical: one-hot (drop-first for linear/logistic, every level for trees) | True | selected: rank 1 of 26, cumulative share 0.1241 within 99% |
| route\_recent\_carrier\_transit\_days | Recent route carrier transit days: recent typical carrier-to-customer time on the route | as route\_recent\_delivery\_days, on (delivery date - carrier date) | the logistics part of the lead time with the seller's delay removed; promise-free (v3.1) | log1p: day count (Henry) | True | selected: rank 2 of 26, cumulative share 0.2431 within 99% |
| route\_recent\_delivery\_days | Recent route delivery days: recent typical purchase-to-delivery time on the route | weighted 3-week mean (0.5, 0.3, 0.2) of the route's weekly median lead days; < 10 route events -> 0.7 x seller state + 0.3 x customer state, then overall | recent delivery conditions on the route (Henry: may also shape the customer's experience) | log1p: day count (Henry) | True | selected: rank 3 of 26, cumulative share 0.3621 within 99% |
| seller\_prior\_dispatch\_days | Prior seller dispatch days: mean days from purchase to carrier handover over the seller's earlier orders | mean of (carrier date - purchase time) over the seller's earlier handovers; same fallback | seller packing speed is part of every lead time | log1p: day count (Henry) | True | selected: rank 7 of 26, cumulative share 0.7316 within 99% |
| seller\_prior\_late\_handover\_rate | Prior seller late-handover rate: share of the seller's earlier handovers made after their last shipping limit | mean over the seller's handovers in weeks before the prediction week of 1\[carrier date > last shipping\_limit\_date\]; new seller: weighted 3-week mean of sellers in the same state | a seller that dispatched late before is likely to dispatch late again (Henry) | never logged: rate or flag, scaled only (Henry) | True | selected: rank 9 of 26, cumulative share 0.8066 within 99% |
| seller\_prior\_late\_handover\_days | Prior seller late-handover days: mean days by which the seller's earlier handovers missed the shipping limit (0 if on time) | mean of max(0, carrier date - last shipping\_limit\_date) over the seller's earlier handovers; same fallback | the size of past dispatch delays, not only their frequency (Henry) | log1p: day count (Henry) | True | selected: rank 10 of 26, cumulative share 0.8390 within 99% |

**Check** every pool feature has a dictionary row with formula and reason: PASS **Check** linear/logistic design matrix is full rank on B rows: PASS (rank 140 of 140)

**Files** (pipeline\_b/stages/b04/regression/outputs/, run 20261023T153748Z): design\_matrix\_B.csv, feature\_dictionary\_B.csv, recipes\_B.json

# Round 1 cards (superseded by round 2, kept for the record)

Run 20261023T134940Z on uncommitted code. Old feature names; full-rank check failed.

## B4.1 Pool

**Approved solution (B4 blueprint):** Pool. A's task pool + B's candidates (B-C6 to B-C9); route counts as one feature.

**What was done:** B pool: A's 24 pool features plus 6 B candidates (route, b\_seller\_late\_rate, b\_seller\_late\_days, b\_seller\_dispatch\_days, b\_route\_lead\_days, b\_route\_transit\_days).

**Pool by source** (pool\_ranking\_B.csv): contract predictor 24; B-C7 3; B-C6 1; B-C8b 1; B-C8 1.

**Check** the ranked set equals B's pool: PASS (30 features) **Check** no feature from the estimated delivery date: PASS

**Files** (pipeline\_b/stages/b04/regression/outputs/, run 20261023T134940Z): pool\_ranking\_B.csv

## B4.2 Ranking

**Approved solution (B4 blueprint):** Ranking. A's ranking on B's development rows: |Spearman| with the log target for regression, mutual information for classification, as in A's s03/s04.

**What was done:** Ranking on B's development rows with A's measures (|Spearman|; rank correlation ratio for categorical): top 8 route 0.110; b\_route\_transit\_days 0.105; b\_route\_lead\_days 0.105; distance\_km\_max 0.105; interstate\_share 0.101; customer\_state 0.092; total\_freight 0.078; b\_seller\_dispatch\_days 0.044.

**Full pool ranking** (pool\_ranking\_B.csv):

| rank | feature | source | method | value | share | cumulative\_share |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | route | B-C6 | rank correlation ratio | 0.5317 | 0.1100 | 0.1100 |
| 2 | b\_route\_transit\_days | B-C8b | absolute Spearman | 0.5099 | 0.1055 | 0.2154 |
| 3 | b\_route\_lead\_days | B-C8 | absolute Spearman | 0.5097 | 0.1054 | 0.3208 |
| 4 | distance\_km\_max | contract predictor | absolute Spearman | 0.5087 | 0.1052 | 0.4260 |
| 5 | interstate\_share | contract predictor | absolute Spearman | 0.4867 | 0.1007 | 0.5267 |
| 6 | customer\_state | contract predictor | rank correlation ratio | 0.4458 | 0.0922 | 0.6189 |
| 7 | total\_freight | contract predictor | absolute Spearman | 0.3771 | 0.0780 | 0.6968 |
| 8 | b\_seller\_dispatch\_days | B-C7 | absolute Spearman | 0.2106 | 0.0435 | 0.7404 |
| 9 | primary\_category | contract predictor | rank correlation ratio | 0.1666 | 0.0345 | 0.7748 |
| 10 | b\_seller\_late\_rate | B-C7 | absolute Spearman | 0.1547 | 0.0320 | 0.8068 |
| 11 | b\_seller\_late\_days | B-C7 | absolute Spearman | 0.1388 | 0.0287 | 0.8356 |
| 12 | freight\_ratio | contract predictor | absolute Spearman | 0.1036 | 0.0214 | 0.8570 |
| 13 | primary\_seller\_state | contract predictor | rank correlation ratio | 0.1020 | 0.0211 | 0.8781 |
| 14 | total\_weight\_g | contract predictor | absolute Spearman | 0.0907 | 0.0188 | 0.8968 |
| 15 | total\_price | contract predictor | absolute Spearman | 0.0904 | 0.0187 | 0.9155 |
| 16 | primary\_payment\_type | contract predictor | rank correlation ratio | 0.0819 | 0.0169 | 0.9325 |
| 17 | total\_volume\_cm3 | contract predictor | absolute Spearman | 0.0756 | 0.0156 | 0.9481 |
| 18 | purchase\_dayofweek | contract predictor | absolute Spearman | 0.0468 | 0.0097 | 0.9578 |
| 19 | n\_sellers | contract predictor | absolute Spearman | 0.0450 | 0.0093 | 0.9671 |
| 20 | purchase\_month | contract predictor | absolute Spearman | 0.0369 | 0.0076 | 0.9747 |
| 21 | n\_products | contract predictor | absolute Spearman | 0.0337 | 0.0070 | 0.9817 |
| 22 | payment\_installments\_max | contract predictor | absolute Spearman | 0.0327 | 0.0068 | 0.9885 |
| 23 | n\_items | contract predictor | absolute Spearman | 0.0203 | 0.0042 | 0.9927 |
| 24 | n\_categories | contract predictor | absolute Spearman | 0.0123 | 0.0025 | 0.9952 |
| 25 | n\_payment\_methods | contract predictor | absolute Spearman | 0.0058 | 0.0012 | 0.9964 |
| 26 | category\_missing\_fraction | contract predictor | absolute Spearman | 0.0058 | 0.0012 | 0.9976 |
| 27 | purchase\_hour | contract predictor | absolute Spearman | 0.0054 | 0.0011 | 0.9987 |
| 28 | volume\_missing\_fraction | contract predictor | absolute Spearman | 0.0031 | 0.0006 | 0.9994 |
| 29 | weight\_missing\_fraction | contract predictor | absolute Spearman | 0.0031 | 0.0006 | 1.0000 |
| 30 | distance\_missing\_fraction | contract predictor | absolute Spearman |  |  | 1.0000 |

**Check** the ranked set equals B's pool: PASS (30 features)

**Files** (pipeline\_b/stages/b04/regression/outputs/, run 20261023T134940Z): pool\_ranking\_B.csv

## B4.3 Selection at 99% (B-C11)

**Approved solution (B4 blueprint):** Selection (B-C11). Keep the top features reaching 99% of the cumulative share (A's G-70 threshold). A feature below the cut is dropped with its rank and share recorded.

**What was done:** 23 of 28 core features kept at the 99% cumulative share (A's G-70 threshold). B features kept: route, b\_route\_transit\_days, b\_route\_lead\_days, b\_seller\_dispatch\_days, b\_seller\_late\_rate, b\_seller\_late\_days; B features dropped: none. Reduction: 2 dropped as constant or duplicate.

**Reduction before selection** (reduction\_B.csv):

| feature | flagged\_by | paired\_with | rationale |
| --- | --- | --- | --- |
| distance\_missing\_fraction | constant | nan | one value on B rows |
| weight\_missing\_fraction | duplicate | volume\_missing\_fraction | identical to volume\_missing\_fraction on every B row; volume\_missing\_fraction ranks higher |

**Selection ranking on the core set** (selection\_ranking\_B.csv; kept = within 99%):

| rank | feature | source | share | cumulative\_share | selected |
| --- | --- | --- | --- | --- | --- |
| 1 | route | B-C6 | 0.1100 | 0.1100 | True |
| 2 | b\_route\_transit\_days | B-C8b | 0.1055 | 0.2155 | True |
| 3 | b\_route\_lead\_days | B-C8 | 0.1055 | 0.3210 | True |
| 4 | distance\_km\_max | contract predictor | 0.1053 | 0.4263 | True |
| 5 | interstate\_share | contract predictor | 0.1007 | 0.5270 | True |
| 6 | customer\_state | contract predictor | 0.0923 | 0.6193 | True |
| 7 | total\_freight | contract predictor | 0.0780 | 0.6973 | True |
| 8 | b\_seller\_dispatch\_days | B-C7 | 0.0436 | 0.7409 | True |
| 9 | primary\_category | contract predictor | 0.0345 | 0.7753 | True |
| 10 | b\_seller\_late\_rate | B-C7 | 0.0320 | 0.8074 | True |
| 11 | b\_seller\_late\_days | B-C7 | 0.0287 | 0.8361 | True |
| 12 | freight\_ratio | contract predictor | 0.0214 | 0.8575 | True |
| 13 | primary\_seller\_state | contract predictor | 0.0211 | 0.8786 | True |
| 14 | total\_weight\_g | contract predictor | 0.0188 | 0.8974 | True |
| 15 | total\_price | contract predictor | 0.0187 | 0.9161 | True |
| 16 | primary\_payment\_type | contract predictor | 0.0170 | 0.9331 | True |
| 17 | total\_volume\_cm3 | contract predictor | 0.0157 | 0.9487 | True |
| 18 | purchase\_dayofweek | contract predictor | 0.0097 | 0.9584 | True |
| 19 | n\_sellers | contract predictor | 0.0093 | 0.9677 | True |
| 20 | purchase\_month | contract predictor | 0.0076 | 0.9754 | True |
| 21 | n\_products | contract predictor | 0.0070 | 0.9823 | True |
| 22 | payment\_installments\_max | contract predictor | 0.0068 | 0.9891 | True |
| 23 | n\_items | contract predictor | 0.0042 | 0.9933 | True |
| 24 | n\_categories | contract predictor | 0.0025 | 0.9958 | False |
| 25 | n\_payment\_methods | contract predictor | 0.0012 | 0.9970 | False |
| 26 | category\_missing\_fraction | contract predictor | 0.0012 | 0.9982 | False |
| 27 | purchase\_hour | contract predictor | 0.0011 | 0.9994 | False |
| 28 | volume\_missing\_fraction | contract predictor | 0.0006 | 1.0000 | False |

**Dropped below the threshold** (selected\_features\_B.json): n\_categories, n\_payment\_methods, category\_missing\_fraction, purchase\_hour, volume\_missing\_fraction.

**Check** the kept set is exactly the 99% cumulative-share prefix of the core ranking: PASS (23 of 28 kept)

**Files** (pipeline\_b/stages/b04/regression/outputs/, run 20261023T134940Z): reduction\_B.csv, selected\_features\_B.json, selection\_ranking\_B.csv

## B4.4 Transforms

**Approved solution (B4 blueprint):** Transforms. A's rules: log1p for skewed counts and all day counts; rates and flags scaled only; route one-hot (drop-first for linear/logistic, every level for trees); A's duplicate rule; imputation and route-median fill fitted inside the folds.

**What was done:** log1p on 9 features (total\_price, total\_freight, total\_weight\_g, total\_volume\_cm3, distance\_km\_max, b\_seller\_late\_days, b\_seller\_dispatch\_days, b\_route\_lead\_days, b\_route\_transit\_days); B day counts logged, B rates and flags scaled only.

**Transform per feature** (transforms\_B.csv):

| feature | skewness | log1p | rule |
| --- | --- | --- | --- |
| n\_items | 7.61 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| n\_products | 7.65 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| n\_sellers | 9.98 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| n\_categories | -1.98 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| total\_price | 11.03 | True | log1p because pre-cutoff skewness 11.03 > 1 (A's 4.2 rule on B rows) |
| total\_freight | 9.42 | True | log1p because pre-cutoff skewness 9.42 > 1 (A's 4.2 rule on B rows) |
| freight\_ratio | 15.30 | False | never logged: team decision in the s01 review (G-62) (A's 4.2 rule on B rows) |
| total\_weight\_g | 6.94 | True | log1p because pre-cutoff skewness 6.94 > 1 (A's 4.2 rule on B rows) |
| total\_volume\_cm3 | 7.63 | True | log1p because pre-cutoff skewness 7.63 > 1 (A's 4.2 rule on B rows) |
| weight\_missing\_fraction | 71.42 | False | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) |
| volume\_missing\_fraction | 71.42 | False | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) |
| primary\_category |  | False | categorical: one-hot, never logged (A's 4.2 rule on B rows) |
| category\_missing\_fraction | 7.61 | False | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) |
| customer\_state |  | False | categorical: one-hot, never logged (A's 4.2 rule on B rows) |
| primary\_seller\_state |  | False | categorical: one-hot, never logged (A's 4.2 rule on B rows) |
| distance\_km\_max | 1.26 | True | log1p because pre-cutoff skewness 1.26 > 1 (A's 4.2 rule on B rows) |
| distance\_missing\_fraction |  | False | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) |
| interstate\_share | -0.30 | False | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) |
| purchase\_month | 0.37 | False | never logged: numeric calendar position (G-22, G-47) (A's 4.2 rule on B rows) |
| purchase\_dayofweek | 0.16 | False | never logged: numeric calendar position (G-22, G-47) (A's 4.2 rule on B rows) |
| purchase\_hour | -0.61 | False | never logged: numeric calendar position (G-22, G-47) (A's 4.2 rule on B rows) |
| primary\_payment\_type |  | False | categorical: one-hot, never logged (A's 4.2 rule on B rows) |
| payment\_installments\_max | 1.65 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| n\_payment\_methods | 6.33 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| route |  | False | categorical: one-hot (drop-first for linear/logistic, every level for trees) |
| b\_seller\_late\_rate | 3.03 | False | never logged: rate or flag, scaled only (Henry) |
| b\_seller\_late\_days | 22.13 | True | log1p: day count (Henry) |
| b\_seller\_dispatch\_days | 5.26 | True | log1p: day count (Henry) |
| b\_route\_lead\_days | 1.16 | True | log1p: day count (Henry) |
| b\_route\_transit\_days | 1.17 | True | log1p: day count (Henry) |

**Files** (pipeline\_b/stages/b04/regression/outputs/, run 20261023T134940Z): transforms\_B.csv

## B4.5 Recipes and dictionary (B-C12)

**Approved solution (B4 blueprint):** Recipes. One recipe per family (dummy, linear/logistic, tree, forest), built with A's code.

**What was done:** Recipes for dummy, linear/logistic, tree and forest with A's factory; linear design matrix rank 140 of 153; feature\_dictionary\_B.csv has 30 rows.

**Design matrices** (design\_matrix\_B.csv):

| family | rows | encoded\_columns | duplicates\_dropped | columns | rank | full\_rank | condition\_number |
| --- | --- | --- | --- | --- | --- | --- | --- |
| linear | 61,245 | 154 | missingindicator\_total\_volume\_cm3 | 153 | 140 | False | 30184955682182392.0 |
| tree | 61,245 | 159 | missingindicator\_total\_volume\_cm3 | 158 | 141 | False | 999786359099036160.0 |

**Feature dictionary, B features** (feature\_dictionary\_B.csv; the file also holds A's inherited features, 30 rows in all):

| feature | definition | formula | reason | transform | kept | selection\_reason |
| --- | --- | --- | --- | --- | --- | --- |
| route | Route of the order, customer state to primary seller state | customer\_state + '->' + primary\_seller\_state | delivery time and experience differ by origin-destination pair; captures interactions distance alone misses | categorical: one-hot (drop-first for linear/logistic, every level for trees) | True | selected: rank 1 of 28, cumulative share 0.1100 within 99% |
| b\_route\_transit\_days | Route transit days: recent typical carrier-to-customer time on the route | as b\_route\_lead\_days, on (delivery date - carrier date) | the logistics part of the lead time with the seller's delay removed; promise-free (v3.1) | log1p: day count (Henry) | True | selected: rank 2 of 28, cumulative share 0.2155 within 99% |
| b\_route\_lead\_days | Route lead days: recent typical purchase-to-delivery time on the route | weighted 3-week mean (0.5, 0.3, 0.2) of the route's weekly median lead days; < 10 route events -> 0.7 x seller state + 0.3 x customer state, then overall | recent delivery conditions on the route (Henry: may also shape the customer's experience) | log1p: day count (Henry) | True | selected: rank 3 of 28, cumulative share 0.3210 within 99% |
| b\_seller\_dispatch\_days | Prior seller dispatch days: mean days from purchase to carrier handover over the seller's earlier orders | mean of (carrier date - purchase time) over the seller's earlier handovers; same fallback | seller packing speed is part of every lead time | log1p: day count (Henry) | True | selected: rank 8 of 28, cumulative share 0.7409 within 99% |
| b\_seller\_late\_rate | Prior seller late rate: share of the seller's earlier handovers made after their last shipping limit | mean over the seller's handovers in weeks before the prediction week of 1\[carrier date > last shipping\_limit\_date\]; new seller: weighted 3-week mean of sellers in the same state | a seller that dispatched late before is likely to dispatch late again (Henry) | never logged: rate or flag, scaled only (Henry) | True | selected: rank 10 of 28, cumulative share 0.8074 within 99% |
| b\_seller\_late\_days | Prior seller late days: mean days by which the seller's earlier handovers missed the shipping limit (0 if on time) | mean of max(0, carrier date - last shipping\_limit\_date) over the seller's earlier handovers; same fallback | the size of past dispatch delays, not only their frequency (Henry) | log1p: day count (Henry) | True | selected: rank 11 of 28, cumulative share 0.8361 within 99% |

**Check** every pool feature has a dictionary row with formula and reason: PASS **Check** linear/logistic design matrix is full rank on B rows: FAIL (rank 140 of 153)

**Files** (pipeline\_b/stages/b04/regression/outputs/, run 20261023T134940Z): design\_matrix\_B.csv, feature\_dictionary\_B.csv, recipes\_B.json
