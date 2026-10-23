# B4 › classification — evidence cards

Round 2 (B-G-02, B-G-04; built, not yet committed) · run `20261023T153754Z` on uncommitted code (working tree on aed9cfa) · 5 checks, all PASS. Coverage and review dropdowns are on the parent tab "B4 Features"; comment on any card here.

## B4.1 Pool

**Approved solution (B4 blueprint):** Pool. A's task pool + B's candidates (B-C6 to B-C9; names B-G-04); route counts as one feature.

**What was done:** B pool: A's 27 pool features plus 9 B candidates (route\_seller\_to\_customer\_state, seller\_prior\_late\_handover\_rate, seller\_prior\_late\_handover\_days, seller\_prior\_dispatch\_days, route\_recent\_delivery\_days, route\_recent\_carrier\_transit\_days, order\_handed\_over\_late, order\_handover\_late\_days, order\_dispatch\_days).

**Pool by source** (pool\_ranking\_B.csv): contract predictor 24; B-C7 3; adopted candidate (G-70) 3; B-C9 3; B-C8b 1; B-C8 1; B-C6 1.

**Check** the ranked set equals B's pool: PASS (36 features) **Check** no feature from the estimated delivery date: PASS

**Files** (pipeline\_b/stages/b04/classification/outputs/, run 20261023T153754Z): pool\_ranking\_B.csv

## B4.2 Ranking

**Approved solution (B4 blueprint):** Ranking. A's ranking on B's development rows: |Spearman| with the log target for regression, mutual information for classification, as in A's s03/s04.

**What was done:** Ranking on B's development rows with A's measures (mutual information): top 8 route\_recent\_carrier\_transit\_days 0.094; route\_recent\_delivery\_days 0.093; seller\_prior\_dispatch\_days 0.081; seller\_prior\_late\_handover\_days 0.070; seller\_prior\_review\_mean 0.052; order\_dispatch\_days 0.046; freight\_ratio 0.045; total\_freight 0.045.

**Full pool ranking** (pool\_ranking\_B.csv):

| rank | feature | source | method | value | share | cumulative\_share |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | route\_recent\_carrier\_transit\_days | B-C8b | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0193 | 0.0945 | 0.0945 |
| 2 | route\_recent\_delivery\_days | B-C8 | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0190 | 0.0928 | 0.1873 |
| 3 | seller\_prior\_dispatch\_days | B-C7 | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0165 | 0.0809 | 0.2681 |
| 4 | seller\_prior\_late\_handover\_days | B-C7 | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0142 | 0.0696 | 0.3378 |
| 5 | seller\_prior\_review\_mean | adopted candidate (G-70) | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0106 | 0.0518 | 0.3896 |
| 6 | order\_dispatch\_days | B-C9 | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0094 | 0.0461 | 0.4357 |
| 7 | freight\_ratio | contract predictor | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0092 | 0.0450 | 0.4806 |
| 8 | total\_freight | contract predictor | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0092 | 0.0449 | 0.5255 |
| 9 | total\_volume\_cm3 | contract predictor | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0090 | 0.0442 | 0.5697 |
| 10 | n\_items | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0081 | 0.0397 | 0.6094 |
| 11 | route\_seller\_to\_customer\_state | B-C6 | mutual\_info\_classif, discrete (contingency) | 0.0080 | 0.0389 | 0.6483 |
| 12 | seller\_prior\_late\_handover\_rate | B-C7 | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0079 | 0.0387 | 0.6870 |
| 13 | total\_price | contract predictor | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0066 | 0.0323 | 0.7193 |
| 14 | order\_handover\_late\_days | B-C9 | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0063 | 0.0307 | 0.7499 |
| 15 | total\_weight\_g | contract predictor | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0060 | 0.0292 | 0.7792 |
| 16 | product\_description\_lenght | adopted candidate (G-70) | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0059 | 0.0287 | 0.8079 |
| 17 | customer\_state | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0057 | 0.0279 | 0.8358 |
| 18 | n\_products | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0050 | 0.0242 | 0.8600 |
| 19 | n\_sellers | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0046 | 0.0225 | 0.8825 |
| 20 | purchase\_month | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0044 | 0.0216 | 0.9042 |
| 21 | order\_handed\_over\_late | B-C9 | mutual\_info\_classif, discrete (contingency) | 0.0043 | 0.0210 | 0.9252 |
| 22 | distance\_km\_max | contract predictor | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0043 | 0.0209 | 0.9461 |
| 23 | primary\_category | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0031 | 0.0154 | 0.9614 |
| 24 | interstate\_share | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0031 | 0.0153 | 0.9768 |
| 25 | n\_categories | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0016 | 0.0077 | 0.9844 |
| 26 | payment\_installments\_max | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0008 | 0.0040 | 0.9884 |
| 27 | primary\_seller\_state | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0007 | 0.0036 | 0.9920 |
| 28 | product\_photos\_qty | adopted candidate (G-70) | mutual\_info\_classif, discrete (contingency) | 0.0007 | 0.0033 | 0.9953 |
| 29 | category\_missing\_fraction | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0004 | 0.0021 | 0.9974 |
| 30 | purchase\_hour | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0004 | 0.0020 | 0.9995 |
| 31 | purchase\_dayofweek | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0001 | 0.0004 | 0.9999 |
| 32 | primary\_payment\_type | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0000 | 0.0000 | 0.9999 |
| 33 | volume\_missing\_fraction | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0000 | 0.0000 | 1.0000 |
| 34 | weight\_missing\_fraction | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0000 | 0.0000 | 1.0000 |
| 35 | n\_payment\_methods | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0000 | 0.0000 | 1.0000 |
| 36 | distance\_missing\_fraction | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0000 | 0.0000 | 1.0000 |

**Check** the ranked set equals B's pool: PASS (36 features)

**Files** (pipeline\_b/stages/b04/classification/outputs/, run 20261023T153754Z): pool\_ranking\_B.csv

## B4.3 Selection at 99% (B-C11)

**Approved solution (B4 blueprint):** Selection (B-C11). Keep the top features reaching 99% of the cumulative share (A's G-70 threshold). A feature below the cut is dropped with its rank and share recorded.

**What was done:** 25 of 32 core features kept at the 99% cumulative share (A's G-70 threshold). B features kept: route\_recent\_carrier\_transit\_days, route\_recent\_delivery\_days, seller\_prior\_dispatch\_days, seller\_prior\_late\_handover\_days, order\_dispatch\_days, route\_seller\_to\_customer\_state, seller\_prior\_late\_handover\_rate, order\_handover\_late\_days, order\_handed\_over\_late; B features dropped: none. Reduction: 4 dropped (customer\_state: nested in route (B-G-02); primary\_seller\_state: nested in route (B-G-02); distance\_missing\_fraction: constant; weight\_missing\_fraction: duplicate).

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
| 1 | route\_recent\_carrier\_transit\_days | B-C8b | 0.0975 | 0.0975 | True |
| 2 | route\_recent\_delivery\_days | B-C8 | 0.0959 | 0.1934 | True |
| 3 | seller\_prior\_dispatch\_days | B-C7 | 0.0835 | 0.2769 | True |
| 4 | seller\_prior\_late\_handover\_days | B-C7 | 0.0719 | 0.3488 | True |
| 5 | seller\_prior\_review\_mean | adopted candidate (G-70) | 0.0535 | 0.4023 | True |
| 6 | order\_dispatch\_days | B-C9 | 0.0476 | 0.4499 | True |
| 7 | freight\_ratio | contract predictor | 0.0464 | 0.4963 | True |
| 8 | total\_freight | contract predictor | 0.0463 | 0.5426 | True |
| 9 | total\_volume\_cm3 | contract predictor | 0.0456 | 0.5882 | True |
| 10 | n\_items | contract predictor | 0.0410 | 0.6292 | True |
| 11 | route\_seller\_to\_customer\_state | B-C6 | 0.0402 | 0.6694 | True |
| 12 | seller\_prior\_late\_handover\_rate | B-C7 | 0.0400 | 0.7094 | True |
| 13 | total\_price | contract predictor | 0.0334 | 0.7427 | True |
| 14 | order\_handover\_late\_days | B-C9 | 0.0317 | 0.7744 | True |
| 15 | total\_weight\_g | contract predictor | 0.0302 | 0.8046 | True |
| 16 | product\_description\_lenght | adopted candidate (G-70) | 0.0296 | 0.8342 | True |
| 17 | n\_products | contract predictor | 0.0250 | 0.8592 | True |
| 18 | n\_sellers | contract predictor | 0.0233 | 0.8825 | True |
| 19 | purchase\_month | contract predictor | 0.0223 | 0.9048 | True |
| 20 | order\_handed\_over\_late | B-C9 | 0.0217 | 0.9265 | True |
| 21 | distance\_km\_max | contract predictor | 0.0216 | 0.9481 | True |
| 22 | primary\_category | contract predictor | 0.0159 | 0.9640 | True |
| 23 | interstate\_share | contract predictor | 0.0158 | 0.9798 | True |
| 24 | n\_categories | contract predictor | 0.0079 | 0.9877 | True |
| 25 | payment\_installments\_max | contract predictor | 0.0041 | 0.9918 | True |
| 26 | product\_photos\_qty | adopted candidate (G-70) | 0.0034 | 0.9952 | False |
| 27 | category\_missing\_fraction | contract predictor | 0.0022 | 0.9974 | False |
| 28 | purchase\_hour | contract predictor | 0.0021 | 0.9995 | False |
| 29 | purchase\_dayofweek | contract predictor | 0.0004 | 0.9999 | False |
| 30 | primary\_payment\_type | contract predictor | 0.0000 | 1.0000 | False |
| 31 | volume\_missing\_fraction | contract predictor | 0.0000 | 1.0000 | False |
| 32 | n\_payment\_methods | contract predictor | 0.0000 | 1.0000 | False |

**Dropped below the threshold** (selected\_features\_B.json): product\_photos\_qty, category\_missing\_fraction, purchase\_hour, purchase\_dayofweek, primary\_payment\_type, volume\_missing\_fraction, n\_payment\_methods.

**Check** the kept set is exactly the 99% cumulative-share prefix of the core ranking: PASS (25 of 32 kept)

**Files** (pipeline\_b/stages/b04/classification/outputs/, run 20261023T153754Z): reduction\_B.csv, selected\_features\_B.json, selection\_ranking\_B.csv

## B4.4 Transforms

**Approved solution (B4 blueprint):** Transforms. A's rules: log1p for skewed counts and all day counts; rates and flags scaled only; route one-hot (drop-first for linear/logistic, every level for trees); A's duplicate rule; imputation fitted inside the folds. B-G-02: with route in the pool, customer\_state and primary\_seller\_state are dropped in the reduction as nested in route; no route-median fill for distance\_km\_max, which B-C2 leaves never missing.

**What was done:** log1p on 12 features (total\_price, total\_freight, total\_weight\_g, total\_volume\_cm3, distance\_km\_max, product\_description\_lenght, seller\_prior\_late\_handover\_days, seller\_prior\_dispatch\_days, route\_recent\_delivery\_days, route\_recent\_carrier\_transit\_days, order\_handover\_late\_days, order\_dispatch\_days); B day counts logged, B rates and flags scaled only.

**Transform per feature** (transforms\_B.csv):

| feature | skewness | log1p | rule |
| --- | --- | --- | --- |
| n\_items | 7.67 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| n\_products | 7.69 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| n\_sellers | 10.09 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| n\_categories | -2.02 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| total\_price | 11.11 | True | log1p because pre-cutoff skewness 11.11 > 1 (A's 4.2 rule on B rows) |
| total\_freight | 9.45 | True | log1p because pre-cutoff skewness 9.45 > 1 (A's 4.2 rule on B rows) |
| freight\_ratio | 15.27 | False | never logged: team decision in the s01 review (G-62) (A's 4.2 rule on B rows) |
| total\_weight\_g | 6.94 | True | log1p because pre-cutoff skewness 6.94 > 1 (A's 4.2 rule on B rows) |
| total\_volume\_cm3 | 7.65 | True | log1p because pre-cutoff skewness 7.65 > 1 (A's 4.2 rule on B rows) |
| weight\_missing\_fraction | 71.43 | False | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) |
| volume\_missing\_fraction | 71.43 | False | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) |
| primary\_category |  | False | categorical: one-hot, never logged (A's 4.2 rule on B rows) |
| category\_missing\_fraction | 7.59 | False | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) |
| customer\_state |  | False | categorical: one-hot, never logged (A's 4.2 rule on B rows) |
| primary\_seller\_state |  | False | categorical: one-hot, never logged (A's 4.2 rule on B rows) |
| distance\_km\_max | 1.26 | True | log1p because pre-cutoff skewness 1.26 > 1 (A's 4.2 rule on B rows) |
| distance\_missing\_fraction |  | False | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) |
| interstate\_share | -0.31 | False | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) |
| purchase\_month | 0.37 | False | never logged: numeric calendar position (G-22, G-47) (A's 4.2 rule on B rows) |
| purchase\_dayofweek | 0.16 | False | never logged: numeric calendar position (G-22, G-47) (A's 4.2 rule on B rows) |
| purchase\_hour | -0.60 | False | never logged: numeric calendar position (G-22, G-47) (A's 4.2 rule on B rows) |
| primary\_payment\_type |  | False | categorical: one-hot, never logged (A's 4.2 rule on B rows) |
| payment\_installments\_max | 1.65 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| n\_payment\_methods | 6.33 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| product\_photos\_qty | 1.91 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| product\_description\_lenght | 2.06 | True | log1p because pre-cutoff skewness 2.06 > 1 (A's 4.2 rule on B rows) |
| seller\_prior\_review\_mean | -1.79 | False | never logged: 1-5 rating (G-70) (A's 4.2 rule on B rows) |
| route\_seller\_to\_customer\_state |  | False | categorical: one-hot (drop-first for linear/logistic, every level for trees) |
| seller\_prior\_late\_handover\_rate | 2.99 | False | never logged: rate or flag, scaled only (Henry) |
| seller\_prior\_late\_handover\_days | 20.18 | True | log1p: day count (Henry) |
| seller\_prior\_dispatch\_days | 4.61 | True | log1p: day count (Henry) |
| route\_recent\_delivery\_days | 1.18 | True | log1p: day count (Henry) |
| route\_recent\_carrier\_transit\_days | 1.20 | True | log1p: day count (Henry) |
| order\_handed\_over\_late | 2.93 | False | never logged: rate or flag, scaled only (Henry) |
| order\_handover\_late\_days | 9.78 | True | log1p: day count (Henry) |
| order\_dispatch\_days | 3.42 | True | log1p: day count (Henry) |

**Files** (pipeline\_b/stages/b04/classification/outputs/, run 20261023T153754Z): transforms\_B.csv

## B4.5 Recipes and dictionary (B-C12)

**Approved solution (B4 blueprint):** Recipes. One recipe per family (dummy, linear/logistic, tree, forest), built with A's code.

**What was done:** Recipes for dummy, linear/logistic, tree and forest with A's factory; linear design matrix rank 145 of 145; feature\_dictionary\_B.csv has 36 rows.

**Design matrices** (design\_matrix\_B.csv):

| family | rows | encoded\_columns | duplicates\_dropped | columns | rank | full\_rank | condition\_number |
| --- | --- | --- | --- | --- | --- | --- | --- |
| linear | 61,258 | 146 | missingindicator\_total\_weight\_g | 145 | 145 | True | 956.4 |
| tree | 61,258 | 148 | missingindicator\_total\_weight\_g | 147 | 146 | False | 91338516592035600.0 |

**Feature dictionary, B features** (feature\_dictionary\_B.csv; the file also holds A's inherited features, 36 rows in all):

| feature | definition | formula | reason | transform | kept | selection\_reason |
| --- | --- | --- | --- | --- | --- | --- |
| route\_recent\_carrier\_transit\_days | Recent route carrier transit days: recent typical carrier-to-customer time on the route | as route\_recent\_delivery\_days, on (delivery date - carrier date) | the logistics part of the lead time with the seller's delay removed; promise-free (v3.1) | log1p: day count (Henry) | True | selected: rank 1 of 32, cumulative share 0.0975 within 99% |
| route\_recent\_delivery\_days | Recent route delivery days: recent typical purchase-to-delivery time on the route | weighted 3-week mean (0.5, 0.3, 0.2) of the route's weekly median lead days; < 10 route events -> 0.7 x seller state + 0.3 x customer state, then overall | recent delivery conditions on the route (Henry: may also shape the customer's experience) | log1p: day count (Henry) | True | selected: rank 2 of 32, cumulative share 0.1934 within 99% |
| seller\_prior\_dispatch\_days | Prior seller dispatch days: mean days from purchase to carrier handover over the seller's earlier orders | mean of (carrier date - purchase time) over the seller's earlier handovers; same fallback | seller packing speed is part of every lead time | log1p: day count (Henry) | True | selected: rank 3 of 32, cumulative share 0.2769 within 99% |
| seller\_prior\_late\_handover\_days | Prior seller late-handover days: mean days by which the seller's earlier handovers missed the shipping limit (0 if on time) | mean of max(0, carrier date - last shipping\_limit\_date) over the seller's earlier handovers; same fallback | the size of past dispatch delays, not only their frequency (Henry) | log1p: day count (Henry) | True | selected: rank 4 of 32, cumulative share 0.3488 within 99% |
| order\_dispatch\_days | Days from purchase to this order's carrier handover | carrier date - purchase time of this order | how long the customer has already waited at handover | log1p: day count (Henry) | True | selected: rank 6 of 32, cumulative share 0.4499 within 99% |
| route\_seller\_to\_customer\_state | Route of the order: primary seller's state to the customer's state | primary\_seller\_state + '->' + customer\_state | delivery time and experience differ by origin-destination pair; captures interactions distance alone misses | categorical: one-hot (drop-first for linear/logistic, every level for trees) | True | selected: rank 11 of 32, cumulative share 0.6694 within 99% |
| seller\_prior\_late\_handover\_rate | Prior seller late-handover rate: share of the seller's earlier handovers made after their last shipping limit | mean over the seller's handovers in weeks before the prediction week of 1\[carrier date > last shipping\_limit\_date\]; new seller: weighted 3-week mean of sellers in the same state | a seller that dispatched late before is likely to dispatch late again (Henry) | never logged: rate or flag, scaled only (Henry) | True | selected: rank 12 of 32, cumulative share 0.7094 within 99% |
| order\_handover\_late\_days | Days this order's handover missed the shipping limit (0 if on time) | max(0, carrier date - last shipping\_limit\_date) of this order | size of this order's dispatch delay | log1p: day count (Henry) | True | selected: rank 14 of 32, cumulative share 0.7744 within 99% |
| order\_handed\_over\_late | This order was handed to the carrier after its last shipping limit | 1\[carrier date > last shipping\_limit\_date\] of this order (known at handover) | a late dispatch is new information about the coming delivery and the review | never logged: rate or flag, scaled only (Henry) | True | selected: rank 20 of 32, cumulative share 0.9265 within 99% |

**Check** every pool feature has a dictionary row with formula and reason: PASS **Check** linear/logistic design matrix is full rank on B rows: PASS (rank 145 of 145)

**Files** (pipeline\_b/stages/b04/classification/outputs/, run 20261023T153754Z): design\_matrix\_B.csv, feature\_dictionary\_B.csv, recipes\_B.json

# Round 1 cards (superseded by round 2, kept for the record)

Run 20261023T134947Z on uncommitted code. Old feature names; full-rank check failed.

## B4.1 Pool

**Approved solution (B4 blueprint):** Pool. A's task pool + B's candidates (B-C6 to B-C9); route counts as one feature.

**What was done:** B pool: A's 27 pool features plus 9 B candidates (route, b\_seller\_late\_rate, b\_seller\_late\_days, b\_seller\_dispatch\_days, b\_route\_lead\_days, b\_route\_transit\_days, b\_own\_handover\_late, b\_own\_late\_days, b\_own\_dispatch\_days).

**Pool by source** (pool\_ranking\_B.csv): contract predictor 24; B-C7 3; adopted candidate (G-70) 3; B-C9 3; B-C8b 1; B-C8 1; B-C6 1.

**Check** the ranked set equals B's pool: PASS (36 features) **Check** no feature from the estimated delivery date: PASS

**Files** (pipeline\_b/stages/b04/classification/outputs/, run 20261023T134947Z): pool\_ranking\_B.csv

## B4.2 Ranking

**Approved solution (B4 blueprint):** Ranking. A's ranking on B's development rows: |Spearman| with the log target for regression, mutual information for classification, as in A's s03/s04.

**What was done:** Ranking on B's development rows with A's measures (mutual information): top 8 b\_route\_transit\_days 0.094; b\_route\_lead\_days 0.093; b\_seller\_dispatch\_days 0.081; b\_seller\_late\_days 0.070; seller\_prior\_review\_mean 0.052; b\_own\_dispatch\_days 0.046; freight\_ratio 0.045; total\_freight 0.045.

**Full pool ranking** (pool\_ranking\_B.csv):

| rank | feature | source | method | value | share | cumulative\_share |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | b\_route\_transit\_days | B-C8b | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0193 | 0.0945 | 0.0945 |
| 2 | b\_route\_lead\_days | B-C8 | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0190 | 0.0928 | 0.1873 |
| 3 | b\_seller\_dispatch\_days | B-C7 | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0165 | 0.0809 | 0.2681 |
| 4 | b\_seller\_late\_days | B-C7 | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0142 | 0.0696 | 0.3378 |
| 5 | seller\_prior\_review\_mean | adopted candidate (G-70) | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0106 | 0.0518 | 0.3896 |
| 6 | b\_own\_dispatch\_days | B-C9 | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0094 | 0.0461 | 0.4357 |
| 7 | freight\_ratio | contract predictor | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0092 | 0.0450 | 0.4806 |
| 8 | total\_freight | contract predictor | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0092 | 0.0449 | 0.5255 |
| 9 | total\_volume\_cm3 | contract predictor | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0090 | 0.0442 | 0.5697 |
| 10 | n\_items | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0081 | 0.0397 | 0.6094 |
| 11 | route | B-C6 | mutual\_info\_classif, discrete (contingency) | 0.0080 | 0.0389 | 0.6483 |
| 12 | b\_seller\_late\_rate | B-C7 | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0079 | 0.0387 | 0.6870 |
| 13 | total\_price | contract predictor | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0066 | 0.0323 | 0.7193 |
| 14 | b\_own\_late\_days | B-C9 | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0063 | 0.0307 | 0.7499 |
| 15 | total\_weight\_g | contract predictor | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0060 | 0.0292 | 0.7792 |
| 16 | product\_description\_lenght | adopted candidate (G-70) | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0059 | 0.0287 | 0.8079 |
| 17 | customer\_state | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0057 | 0.0279 | 0.8358 |
| 18 | n\_products | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0050 | 0.0242 | 0.8600 |
| 19 | n\_sellers | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0046 | 0.0225 | 0.8825 |
| 20 | purchase\_month | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0044 | 0.0216 | 0.9042 |
| 21 | b\_own\_handover\_late | B-C9 | mutual\_info\_classif, discrete (contingency) | 0.0043 | 0.0210 | 0.9252 |
| 22 | distance\_km\_max | contract predictor | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0043 | 0.0209 | 0.9461 |
| 23 | primary\_category | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0031 | 0.0154 | 0.9614 |
| 24 | interstate\_share | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0031 | 0.0153 | 0.9768 |
| 25 | n\_categories | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0016 | 0.0077 | 0.9844 |
| 26 | payment\_installments\_max | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0008 | 0.0040 | 0.9884 |
| 27 | primary\_seller\_state | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0007 | 0.0036 | 0.9920 |
| 28 | product\_photos\_qty | adopted candidate (G-70) | mutual\_info\_classif, discrete (contingency) | 0.0007 | 0.0033 | 0.9953 |
| 29 | category\_missing\_fraction | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0004 | 0.0021 | 0.9974 |
| 30 | purchase\_hour | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0004 | 0.0020 | 0.9995 |
| 31 | purchase\_dayofweek | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0001 | 0.0004 | 0.9999 |
| 32 | primary\_payment\_type | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0000 | 0.0000 | 0.9999 |
| 33 | volume\_missing\_fraction | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0000 | 0.0000 | 1.0000 |
| 34 | weight\_missing\_fraction | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0000 | 0.0000 | 1.0000 |
| 35 | n\_payment\_methods | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0000 | 0.0000 | 1.0000 |
| 36 | distance\_missing\_fraction | contract predictor | mutual\_info\_classif, discrete (contingency) | 0.0000 | 0.0000 | 1.0000 |

**Check** the ranked set equals B's pool: PASS (36 features)

**Files** (pipeline\_b/stages/b04/classification/outputs/, run 20261023T134947Z): pool\_ranking\_B.csv

## B4.3 Selection at 99% (B-C11)

**Approved solution (B4 blueprint):** Selection (B-C11). Keep the top features reaching 99% of the cumulative share (A's G-70 threshold). A feature below the cut is dropped with its rank and share recorded.

**What was done:** 27 of 34 core features kept at the 99% cumulative share (A's G-70 threshold). B features kept: b\_route\_transit\_days, b\_route\_lead\_days, b\_seller\_dispatch\_days, b\_seller\_late\_days, b\_own\_dispatch\_days, route, b\_seller\_late\_rate, b\_own\_late\_days, b\_own\_handover\_late; B features dropped: none. Reduction: 2 dropped as constant or duplicate.

**Reduction before selection** (reduction\_B.csv):

| feature | flagged\_by | paired\_with | rationale |
| --- | --- | --- | --- |
| distance\_missing\_fraction | constant | nan | one value on B rows |
| weight\_missing\_fraction | duplicate | volume\_missing\_fraction | identical to volume\_missing\_fraction on every B row; volume\_missing\_fraction ranks higher |

**Selection ranking on the core set** (selection\_ranking\_B.csv; kept = within 99%):

| rank | feature | source | share | cumulative\_share | selected |
| --- | --- | --- | --- | --- | --- |
| 1 | b\_route\_transit\_days | B-C8b | 0.0945 | 0.0945 | True |
| 2 | b\_route\_lead\_days | B-C8 | 0.0928 | 0.1873 | True |
| 3 | b\_seller\_dispatch\_days | B-C7 | 0.0809 | 0.2682 | True |
| 4 | b\_seller\_late\_days | B-C7 | 0.0696 | 0.3378 | True |
| 5 | seller\_prior\_review\_mean | adopted candidate (G-70) | 0.0518 | 0.3896 | True |
| 6 | b\_own\_dispatch\_days | B-C9 | 0.0461 | 0.4357 | True |
| 7 | freight\_ratio | contract predictor | 0.0450 | 0.4806 | True |
| 8 | total\_freight | contract predictor | 0.0449 | 0.5255 | True |
| 9 | total\_volume\_cm3 | contract predictor | 0.0442 | 0.5697 | True |
| 10 | n\_items | contract predictor | 0.0397 | 0.6094 | True |
| 11 | route | B-C6 | 0.0389 | 0.6483 | True |
| 12 | b\_seller\_late\_rate | B-C7 | 0.0387 | 0.6870 | True |
| 13 | total\_price | contract predictor | 0.0323 | 0.7193 | True |
| 14 | b\_own\_late\_days | B-C9 | 0.0307 | 0.7500 | True |
| 15 | total\_weight\_g | contract predictor | 0.0292 | 0.7792 | True |
| 16 | product\_description\_lenght | adopted candidate (G-70) | 0.0287 | 0.8079 | True |
| 17 | customer\_state | contract predictor | 0.0279 | 0.8358 | True |
| 18 | n\_products | contract predictor | 0.0242 | 0.8600 | True |
| 19 | n\_sellers | contract predictor | 0.0225 | 0.8826 | True |
| 20 | purchase\_month | contract predictor | 0.0216 | 0.9042 | True |
| 21 | b\_own\_handover\_late | B-C9 | 0.0210 | 0.9252 | True |
| 22 | distance\_km\_max | contract predictor | 0.0209 | 0.9461 | True |
| 23 | primary\_category | contract predictor | 0.0154 | 0.9615 | True |
| 24 | interstate\_share | contract predictor | 0.0153 | 0.9768 | True |
| 25 | n\_categories | contract predictor | 0.0077 | 0.9845 | True |
| 26 | payment\_installments\_max | contract predictor | 0.0040 | 0.9885 | True |
| 27 | primary\_seller\_state | contract predictor | 0.0036 | 0.9921 | True |
| 28 | product\_photos\_qty | adopted candidate (G-70) | 0.0033 | 0.9953 | False |
| 29 | category\_missing\_fraction | contract predictor | 0.0021 | 0.9975 | False |
| 30 | purchase\_hour | contract predictor | 0.0020 | 0.9995 | False |
| 31 | purchase\_dayofweek | contract predictor | 0.0004 | 0.9999 | False |
| 32 | primary\_payment\_type | contract predictor | 0.0000 | 1.0000 | False |
| 33 | volume\_missing\_fraction | contract predictor | 0.0000 | 1.0000 | False |
| 34 | n\_payment\_methods | contract predictor | 0.0000 | 1.0000 | False |

**Dropped below the threshold** (selected\_features\_B.json): product\_photos\_qty, category\_missing\_fraction, purchase\_hour, purchase\_dayofweek, primary\_payment\_type, volume\_missing\_fraction, n\_payment\_methods.

**Check** the kept set is exactly the 99% cumulative-share prefix of the core ranking: PASS (27 of 34 kept)

**Files** (pipeline\_b/stages/b04/classification/outputs/, run 20261023T134947Z): reduction\_B.csv, selected\_features\_B.json, selection\_ranking\_B.csv

## B4.4 Transforms

**Approved solution (B4 blueprint):** Transforms. A's rules: log1p for skewed counts and all day counts; rates and flags scaled only; route one-hot (drop-first for linear/logistic, every level for trees); A's duplicate rule; imputation and route-median fill fitted inside the folds.

**What was done:** log1p on 12 features (total\_price, total\_freight, total\_weight\_g, total\_volume\_cm3, distance\_km\_max, product\_description\_lenght, b\_seller\_late\_days, b\_seller\_dispatch\_days, b\_route\_lead\_days, b\_route\_transit\_days, b\_own\_late\_days, b\_own\_dispatch\_days); B day counts logged, B rates and flags scaled only.

**Transform per feature** (transforms\_B.csv):

| feature | skewness | log1p | rule |
| --- | --- | --- | --- |
| n\_items | 7.67 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| n\_products | 7.69 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| n\_sellers | 10.09 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| n\_categories | -2.02 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| total\_price | 11.11 | True | log1p because pre-cutoff skewness 11.11 > 1 (A's 4.2 rule on B rows) |
| total\_freight | 9.45 | True | log1p because pre-cutoff skewness 9.45 > 1 (A's 4.2 rule on B rows) |
| freight\_ratio | 15.27 | False | never logged: team decision in the s01 review (G-62) (A's 4.2 rule on B rows) |
| total\_weight\_g | 6.94 | True | log1p because pre-cutoff skewness 6.94 > 1 (A's 4.2 rule on B rows) |
| total\_volume\_cm3 | 7.65 | True | log1p because pre-cutoff skewness 7.65 > 1 (A's 4.2 rule on B rows) |
| weight\_missing\_fraction | 71.43 | False | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) |
| volume\_missing\_fraction | 71.43 | False | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) |
| primary\_category |  | False | categorical: one-hot, never logged (A's 4.2 rule on B rows) |
| category\_missing\_fraction | 7.59 | False | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) |
| customer\_state |  | False | categorical: one-hot, never logged (A's 4.2 rule on B rows) |
| primary\_seller\_state |  | False | categorical: one-hot, never logged (A's 4.2 rule on B rows) |
| distance\_km\_max | 1.26 | True | log1p because pre-cutoff skewness 1.26 > 1 (A's 4.2 rule on B rows) |
| distance\_missing\_fraction |  | False | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) |
| interstate\_share | -0.31 | False | never logged: bounded 0-1 share (G-47) (A's 4.2 rule on B rows) |
| purchase\_month | 0.37 | False | never logged: numeric calendar position (G-22, G-47) (A's 4.2 rule on B rows) |
| purchase\_dayofweek | 0.16 | False | never logged: numeric calendar position (G-22, G-47) (A's 4.2 rule on B rows) |
| purchase\_hour | -0.60 | False | never logged: numeric calendar position (G-22, G-47) (A's 4.2 rule on B rows) |
| primary\_payment\_type |  | False | categorical: one-hot, never logged (A's 4.2 rule on B rows) |
| payment\_installments\_max | 1.65 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| n\_payment\_methods | 6.33 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| product\_photos\_qty | 1.91 | False | never logged: integer count (G-62, G-70) (A's 4.2 rule on B rows) |
| product\_description\_lenght | 2.06 | True | log1p because pre-cutoff skewness 2.06 > 1 (A's 4.2 rule on B rows) |
| seller\_prior\_review\_mean | -1.79 | False | never logged: 1-5 rating (G-70) (A's 4.2 rule on B rows) |
| route |  | False | categorical: one-hot (drop-first for linear/logistic, every level for trees) |
| b\_seller\_late\_rate | 2.99 | False | never logged: rate or flag, scaled only (Henry) |
| b\_seller\_late\_days | 20.18 | True | log1p: day count (Henry) |
| b\_seller\_dispatch\_days | 4.61 | True | log1p: day count (Henry) |
| b\_route\_lead\_days | 1.18 | True | log1p: day count (Henry) |
| b\_route\_transit\_days | 1.20 | True | log1p: day count (Henry) |
| b\_own\_handover\_late | 2.93 | False | never logged: rate or flag, scaled only (Henry) |
| b\_own\_late\_days | 9.78 | True | log1p: day count (Henry) |
| b\_own\_dispatch\_days | 3.42 | True | log1p: day count (Henry) |

**Files** (pipeline\_b/stages/b04/classification/outputs/, run 20261023T134947Z): transforms\_B.csv

## B4.5 Recipes and dictionary (B-C12)

**Approved solution (B4 blueprint):** Recipes. One recipe per family (dummy, linear/logistic, tree, forest), built with A's code.

**What was done:** Recipes for dummy, linear/logistic, tree and forest with A's factory; linear design matrix rank 145 of 158; feature\_dictionary\_B.csv has 36 rows.

**Design matrices** (design\_matrix\_B.csv):

| family | rows | encoded\_columns | duplicates\_dropped | columns | rank | full\_rank | condition\_number |
| --- | --- | --- | --- | --- | --- | --- | --- |
| linear | 61,258 | 159 | missingindicator\_total\_weight\_g | 158 | 145 | False | 40149510245409656.0 |
| tree | 61,258 | 163 | missingindicator\_total\_weight\_g | 162 | 146 | False | 738213662884457600.0 |

**Feature dictionary, B features** (feature\_dictionary\_B.csv; the file also holds A's inherited features, 36 rows in all):

| feature | definition | formula | reason | transform | kept | selection\_reason |
| --- | --- | --- | --- | --- | --- | --- |
| b\_route\_transit\_days | Route transit days: recent typical carrier-to-customer time on the route | as b\_route\_lead\_days, on (delivery date - carrier date) | the logistics part of the lead time with the seller's delay removed; promise-free (v3.1) | log1p: day count (Henry) | True | selected: rank 1 of 34, cumulative share 0.0945 within 99% |
| b\_route\_lead\_days | Route lead days: recent typical purchase-to-delivery time on the route | weighted 3-week mean (0.5, 0.3, 0.2) of the route's weekly median lead days; < 10 route events -> 0.7 x seller state + 0.3 x customer state, then overall | recent delivery conditions on the route (Henry: may also shape the customer's experience) | log1p: day count (Henry) | True | selected: rank 2 of 34, cumulative share 0.1873 within 99% |
| b\_seller\_dispatch\_days | Prior seller dispatch days: mean days from purchase to carrier handover over the seller's earlier orders | mean of (carrier date - purchase time) over the seller's earlier handovers; same fallback | seller packing speed is part of every lead time | log1p: day count (Henry) | True | selected: rank 3 of 34, cumulative share 0.2682 within 99% |
| b\_seller\_late\_days | Prior seller late days: mean days by which the seller's earlier handovers missed the shipping limit (0 if on time) | mean of max(0, carrier date - last shipping\_limit\_date) over the seller's earlier handovers; same fallback | the size of past dispatch delays, not only their frequency (Henry) | log1p: day count (Henry) | True | selected: rank 4 of 34, cumulative share 0.3378 within 99% |
| b\_own\_dispatch\_days | Days from purchase to this order's carrier handover | carrier date - purchase time of this order | how long the customer has already waited at handover | log1p: day count (Henry) | True | selected: rank 6 of 34, cumulative share 0.4357 within 99% |
| route | Route of the order, customer state to primary seller state | customer\_state + '->' + primary\_seller\_state | delivery time and experience differ by origin-destination pair; captures interactions distance alone misses | categorical: one-hot (drop-first for linear/logistic, every level for trees) | True | selected: rank 11 of 34, cumulative share 0.6483 within 99% |
| b\_seller\_late\_rate | Prior seller late rate: share of the seller's earlier handovers made after their last shipping limit | mean over the seller's handovers in weeks before the prediction week of 1\[carrier date > last shipping\_limit\_date\]; new seller: weighted 3-week mean of sellers in the same state | a seller that dispatched late before is likely to dispatch late again (Henry) | never logged: rate or flag, scaled only (Henry) | True | selected: rank 12 of 34, cumulative share 0.6870 within 99% |
| b\_own\_late\_days | Days this order's handover missed the shipping limit (0 if on time) | max(0, carrier date - last shipping\_limit\_date) of this order | size of this order's dispatch delay | log1p: day count (Henry) | True | selected: rank 14 of 34, cumulative share 0.7500 within 99% |
| b\_own\_handover\_late | This order was handed to the carrier after its last shipping limit | 1\[carrier date > last shipping\_limit\_date\] of this order (known at handover) | a late dispatch is new information about the coming delivery and the review | never logged: rate or flag, scaled only (Henry) | True | selected: rank 21 of 34, cumulative share 0.9252 within 99% |

**Check** every pool feature has a dictionary row with formula and reason: PASS **Check** linear/logistic design matrix is full rank on B rows: FAIL (rank 145 of 158)

**Files** (pipeline\_b/stages/b04/classification/outputs/, run 20261023T134947Z): design\_matrix\_B.csv, feature\_dictionary\_B.csv, recipes\_B.json
