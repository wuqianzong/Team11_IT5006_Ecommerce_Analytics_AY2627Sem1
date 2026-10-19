# s02 Data — implementation review

**ACCEPTED · round 2 · 2026-10-19** · run `20261019T072845Z` · tag `e5-s02-accepted` · all 13 rows Approved · 21 checks, all PASS · approved by the experiment lead. Round 2 only adds the zero-item reasoning to card 2.7; every data output is identical to round 1. This tab is frozen as the record of the s02 review; s03 may start.

## Current (round 2; data values identical to round 1, so the cards show the round 1 run)

### Coverage

| ID | Solution step | Coverage | Checks | Review |
| --- | --- | --- | --- | --- |
| 2.1 | Load | IMPLEMENTED | — | Approved |
| 2.2 | Clean | IMPLEMENTED | — | Approved |
| 2.3 | Geography | IMPLEMENTED | PASS | Approved |
| 2.4 | Join | IMPLEMENTED | PASS | Approved |
| 2.5 | Predictors | IMPLEMENTED | PASS | Approved |
| 2.6 | Targets | IMPLEMENTED | PASS | Approved |
| 2.7 | Leakage audit | IMPLEMENTED | PASS | Approved |
| 2.8 | Populations | IMPLEMENTED | PASS | Approved |
| 2.9 | Outliers | IMPLEMENTED | PASS | Approved |
| 2.10 | Missing installments | IMPLEMENTED | — | Approved |
| 2.11 | Missing payment | IMPLEMENTED | — | Approved |
| 2.12 | Data documentation | IMPLEMENTED | PASS | Approved |
| 2.13 | Negative values | IMPLEMENTED | PASS | Approved |

### Decisions for the team

1. **Lead-time outliers apply to regression only (2.9).** lead\_days exists only for delivered orders, so LEAD\_DAYS\_OUTLIER removes orders from the regression population only; DISTANCE\_OUTLIER applies to both tasks. The blueprint does not say which task loses an order with an extreme lead time. Please confirm, or say the classification population should drop them too.
2. **Where the test cutoff is computed (2.8).** G-28 says after the population rules and before the outlier rule. I applied every row-local rule first (2.6/2.8, 2.10, 2.11, 2.13), then the 80/20 cutoff, then the outlier rule (its statistics need the cutoff). Please confirm.
3. **s01 check 1.9 made rerun-safe.** Rerunning s01 after the foundation change made its check "pre-registered before any later stage has outputs" fail, because s02 now exists. It now checks that every later stage used the same pre-registered layer. protocol.yaml and all s01 values are unchanged. Please confirm s01 stays ACCEPTED.
4. **Date-order violations are logged, not removed (2.7).** The counts are in card 2.7 (e.g. approval after carrier pickup, a first review answered before purchase). The blueprint says log only; the only date rule that removes orders is delivery not after purchase (INVALID\_LEAD\_TIME). Please confirm.

**Status: all four accepted with the stage (2026-10-19).** 1 → G-66, 2 → G-67 (s02 blueprint, pipeline design and Feature solution tab updated); 3 → recorded on the s01 card and review tab; 4 → already the blueprint rule (log only).

### Checks

| Check | Result | Detail | IDs |
| --- | --- | --- | --- |
| orders key order\_id unique and non-null | PASS | 0 duplicates, 0 nulls | 2.4 |
| customers key customer\_id unique and non-null | PASS | 0 duplicates, 0 nulls | 2.4 |
| products key product\_id unique and non-null | PASS | 0 duplicates, 0 nulls | 2.4 |
| sellers key seller\_id unique and non-null | PASS | 0 duplicates, 0 nulls | 2.4 |
| category\_translation key product\_category\_name unique and non-null | PASS | 0 duplicates, 0 nulls | 2.4 |
| order\_items key \['order\_id', 'order\_item\_id'\] unique and non-null | PASS | 0 duplicates, 0 nulls | 2.4 |
| order\_payments key \['order\_id', 'payment\_sequential'\] unique and non-null | PASS | 0 duplicates, 0 nulls | 2.4 |
| output rows = orders | PASS | 99441 rows, 99441 orders | 2.4 |
| every order has a customer | PASS | 0 without | 2.4 |
| order\_id unique and non-null in records | PASS | — | 2.4 |
| records hold exactly the 24 contract predictors | PASS | — | 2.5 |
| no predictor tagged not known at checkout | PASS | — | 2.7 |
| data dictionary: one row per raw and records column | PASS | — | 2.12 |
| data dictionary tags match the audit leakage tags | PASS | — | 2.7, 2.12 |
| outlier statistics use only pre-cutoff orders | PASS | latest purchase used 2018-05-26 18:16:57, cutoff 2018-05-26 18:18:03 | 2.9 |
| every reason code has its pre-registered description | PASS | — | 2.8, 2.13 |
| no order silently dropped: every ineligible order has an exclusion row | PASS | — | 2.8 |
| eligible orders have their target | PASS | — | 2.6 |
| eligible orders have no negative log1p candidate | PASS | — | 2.13 |
| IBGE boundary hashes verified | PASS | archive e84c4d4ab199 | 2.3 |
| test cutoffs recorded in protocol.yaml | PASS | {'regression': '2018-05-26 18:18:03', 'classification': '2018-05-25 18:44:28'} | 2.8 |

### Evidence cards

#### 2.1 Load

**Approved solution:** Canvas copy of the 9 Olist tables; sha256 of each file in `data_hashes.json`

**What was done:** Nine raw tables read with declared types; sha256 of every file and of the IBGE archive, derived geometry and manifest in data\_hashes.json (12 files).

| File | sha256 (first 16) |
| --- | --- |
| data/raw/olist\_orders\_dataset.csv | 8df58ef3d2d7e994… |
| data/raw/olist\_order\_items\_dataset.csv | 0bc4d068c4fe38cb… |
| data/raw/olist\_order\_payments\_dataset.csv | 4f713964f2815dbb… |
| data/raw/olist\_order\_reviews\_dataset.csv | 81336b6e5183133b… |
| data/raw/olist\_customers\_dataset.csv | 983a422239e1712d… |
| data/raw/olist\_sellers\_dataset.csv | 1f643d2b950373b8… |
| data/raw/olist\_products\_dataset.csv | 3e6569628a17fbc7… |
| data/raw/olist\_geolocation\_dataset.csv | b514f6fc991b9566… |
| data/raw/product\_category\_name\_translation.csv | 9da093e114e51753… |
| data/reference/geography/BR\_Pais\_2024.zip | e84c4d4ab199e646… |
| data/reference/geography/BR\_Pais\_2024\_4326.geojson | 779cd7671fd8ff7a… |
| data/reference/geography/boundary\_manifest.json | 76ae80bf1408c96d… |

**Files** (local, run 20261019T054216Z): data\_hashes.json

#### 2.2 Clean

**Approved solution:** Declared types; ZIP prefixes kept as strings (leading zeros); categorical domain checks logged, rows kept; geolocation exact duplicates dropped (counts recomputed and logged). No imputation

**What was done:** Declared types per the Milestone 2 cleaning schema; ZIP prefixes read as strings; categorical domains checked (violations kept, listed in audit.json); geolocation exact duplicates dropped: 261,831 of 1,000,163 rows. No imputation.

| Table | Raw rows | Clean rows | Exact duplicates dropped | Columns with nulls (count) |
| --- | --- | --- | --- | --- |
| orders | 99,441 | 99,441 | 0 | order\_approved\_at 160, order\_delivered\_carrier\_date 1,783, order\_delivered\_customer\_date 2,965 |
| order\_items | 112,650 | 112,650 | 0 | none |
| order\_payments | 103,886 | 103,886 | 0 | none |
| order\_reviews | 99,224 | 99,224 | 0 | review\_comment\_title 87,656, review\_comment\_message 58,247 |
| customers | 99,441 | 99,441 | 0 | none |
| sellers | 3,095 | 3,095 | 0 | none |
| products | 32,951 | 32,951 | 0 | product\_category\_name 610, product\_name\_lenght 610, product\_description\_lenght 610, product\_photos\_qty 610, product\_weight\_g 2, product\_length\_cm 2, product\_height\_cm 2, product\_width\_cm 2 |
| geolocation | 1,000,163 | 738,332 | 261,831 | none |
| category\_translation | 71 | 71 | 0 | none |

**Files** (local, run 20261019T054216Z): audit.json

#### 2.3 Geography

**Approved solution:** ZIP centroids = median lat/lng per ZIP prefix and state, after the IBGE Brazil boundary filter (archive hash recorded)

**What was done:** ZIP/state median centroids after the IBGE boundary filter: 738,303 of 738,332 geolocation rows accepted; 19,023 keys, by status {'resolved': 19015, 'median\_outside\_polygon': 4, 'no\_surviving\_coordinates': 4}.

**Conclusion:** Archive and derived geometry match the pinned hashes.

| Key | Value |
| --- | --- |
| Geolocation rows (after de-duplication) | 738,332 |
| Accepted (inside IBGE boundary) | 738,303 |
| First failure reasons | {'outside\_polygon': 29} |
| ZIP/state keys | 19,023 |
| Keys by status | {'resolved': 19015, 'median\_outside\_polygon': 4, 'no\_surviving\_coordinates': 4} |
| Boundary | BR\_Pais\_2024, EPSG:4674 to EPSG:4326, repair: none (invalid geometry rejected; zero-buffer policy) |
| Archive sha256 | e84c4d4ab199e646… |

**Files** (local, run 20261019T054216Z): zip\_centroids.csv, data\_hashes.json, audit.json

#### 2.4 Join

**Approved solution:** Orders ← customers (many-to-one on `customer_id`); items, payments and reviews aggregated to `order_id` first, then left-joined one-to-one; key-uniqueness and merge-cardinality checks; output rows = orders

**What was done:** Items, payments and reviews aggregated to order\_id first, then left-joined one-to-one (pandas validate); output rows 99,441 = orders 99,441.

| Join check | Result | Detail |
| --- | --- | --- |
| orders key order\_id unique and non-null | PASS | 0 duplicates, 0 nulls |
| customers key customer\_id unique and non-null | PASS | 0 duplicates, 0 nulls |
| products key product\_id unique and non-null | PASS | 0 duplicates, 0 nulls |
| sellers key seller\_id unique and non-null | PASS | 0 duplicates, 0 nulls |
| category\_translation key product\_category\_name unique and non-null | PASS | 0 duplicates, 0 nulls |
| order\_items key \['order\_id', 'order\_item\_id'\] unique and non-null | PASS | 0 duplicates, 0 nulls |
| order\_payments key \['order\_id', 'payment\_sequential'\] unique and non-null | PASS | 0 duplicates, 0 nulls |
| output rows = orders | PASS | 99441 rows, 99441 orders |
| every order has a customer | PASS | 0 without |

**Files** (local, run 20261019T054216Z): records.csv.gz, audit.json

#### 2.5 Predictors

**Approved solution:** The 24 predictors of e5lib/contract.py (G-61; has\_items, freight\_ratio\_missing and payment\_missing are not in the contract and are not built): basket (items, products, sellers, categories), price and freight, physical totals and missing fractions, primary category and seller state, distance, interstate share, calendar, payment

**What was done:** The 24 predictors of e5lib/contract.py built with the Milestone 2 formulas; calendar fields numeric; has\_items, freight\_ratio\_missing and payment\_missing not built.

All 99,441 orders, before any exclusion (description of the built columns only; target analysis is s03, pre-cutoff).

| Predictor | Type | Non-missing | Min / median / max (numeric) or levels | Top levels |
| --- | --- | --- | --- | --- |
| n\_items | numeric | 99,441 | 0 / 1 / 21 |  |
| n\_products | numeric | 99,441 | 0 / 1 / 8 |  |
| n\_sellers | numeric | 99,441 | 0 / 1 / 5 |  |
| n\_categories | numeric | 99,441 | 0 / 1 / 3 |  |
| total\_price | numeric | 98,666 | 0.85 / 86.9 / 1.344e+04 |  |
| total\_freight | numeric | 98,666 | 0 / 17.17 / 1795 |  |
| freight\_ratio | numeric | 98,666 | 0 / 0.2244 / 21.45 |  |
| total\_weight\_g | numeric | 98,644 | 2 / 750 / 1.844e+05 |  |
| total\_volume\_cm3 | numeric | 98,650 | 168 / 7260 / 1.476e+06 |  |
| weight\_missing\_fraction | numeric | 98,666 | 0 / 0 / 1 |  |
| volume\_missing\_fraction | numeric | 98,666 | 0 / 0 / 1 |  |
| primary\_category | categorical | 99,441 | 72 | bed\_bath\_table 9,328; health\_beauty 8,801; sports\_leisure 7,683 |
| category\_missing\_fraction | numeric | 98,666 | 0 / 0 / 1 |  |
| customer\_state | categorical | 99,441 | 27 | SP 41,746; RJ 12,852; MG 11,635 |
| primary\_seller\_state | categorical | 99,441 | 24 | SP 69,939; MG 7,858; PR 7,605 |
| distance\_km\_max | numeric | 97,534 | 0 / 434.8 / 3579 |  |
| distance\_missing\_fraction | numeric | 98,666 | 0 / 0 / 1 |  |
| interstate\_share | numeric | 98,666 | 0 / 1 / 1 |  |
| purchase\_month | numeric | 99,441 | 1 / 6 / 12 |  |
| purchase\_dayofweek | numeric | 99,441 | 0 / 3 / 6 |  |
| purchase\_hour | numeric | 99,441 | 0 / 15 / 23 |  |
| primary\_payment\_type | categorical | 99,441 | 5 | credit\_card 74,935; boleto 19,784; voucher 3,191 |
| payment\_installments\_max | numeric | 99,435 | 1 / 2 / 24 |  |
| n\_payment\_methods | numeric | 99,441 | 0 / 1 / 2 |  |

**Files** (local, run 20261019T054216Z): records.csv.gz

#### 2.6 Targets

**Approved solution:** `lead_days` = delivery − purchase in fractional days (delivered, valid, > 0), available at delivery. `is_detractor` = minimum valid review score ≤ 2, available at the last review answer; first-review label kept for a sensitivity check

**What was done:** lead\_days for delivered orders with delivery after purchase; is\_detractor from the minimum valid score; first-review label kept. Min and first labels agree on 98,615 of 98,673 reviewed orders.

| Key | Value |
| --- | --- |
| Orders with a valid lead time (lead\_days) | 96,470 |
| Orders with a valid review label (is\_detractor) | 98,673 |
| Minimum-review and first-review labels agree | 98,615 |
| Orders with more than one review | 547 |

**Files** (local, run 20261019T054216Z): records.csv.gz, audit.json

#### 2.7 Leakage audit

**Approved solution:** Every column tagged known / not known at checkout. Delivery dates, `order_status` and review fields are never predictors; `order_estimated_delivery_date` is known at checkout but is never a predictor: in production the promised date would come from the task 1 prediction (G-35). It is used only to describe late-vs-promised trends in s03. Also never predictors, because they are only known after purchase: order\_approved\_at, shipping\_limit\_date, has\_items and freight\_ratio\_missing (post-purchase leakage: both encode a later cancellation). payment\_missing is known at checkout but excluded as constant, because 2.11 removes every order without a usable payment (G-42, G-51). Date-order audit on every order: purchase ≤ approval ≤ carrier ≤ delivery, estimated date > purchase, review answer > purchase; violations are logged, and an order whose delivery is not after purchase leaves regression (2.6). Payment fields carry no timestamp, so "chosen at checkout" is a stated assumption. Final order\_status is used only to define populations (2.8), never as an input (G-30)

**What was done:** Every raw and records column tagged known / not known at checkout (data\_dictionary.csv, audit.json); date-order violations logged: {'order\_purchase\_timestamp <= order\_approved\_at': 0, 'order\_approved\_at <= order\_delivered\_carrier\_date': 1359, 'order\_delivered\_carrier\_date <= order\_delivered\_customer\_date': 23, 'order\_estimated\_delivery\_date > order\_purchase\_timestamp': 0, 'first review answer > order\_purchase\_timestamp': 63, 'order\_delivered\_customer\_date > order\_purchase\_timestamp (delivered orders)': 0}.

| Date-order rule | Orders violating |
| --- | --- |
| order\_purchase\_timestamp <= order\_approved\_at | 0 |
| order\_approved\_at <= order\_delivered\_carrier\_date | 1359 |
| order\_delivered\_carrier\_date <= order\_delivered\_customer\_date | 23 |
| order\_estimated\_delivery\_date > order\_purchase\_timestamp | 0 |
| first review answer > order\_purchase\_timestamp | 63 |
| order\_delivered\_customer\_date > order\_purchase\_timestamp (delivered orders) | 0 |

Raw columns tagged not known at checkout: orders.order\_status, orders.order\_approved\_at, orders.order\_delivered\_carrier\_date, orders.order\_delivered\_customer\_date, order\_items.shipping\_limit\_date, order\_reviews.review\_score, order\_reviews.review\_comment\_title, order\_reviews.review\_comment\_message, order\_reviews.review\_creation\_date, order\_reviews.review\_answer\_timestamp. In records, only the targets and their label times are not known at checkout; every predictor is known at checkout (check).

**Files** (local, run 20261019T054216Z): data\_dictionary.csv, audit.json

#### 2.8 Populations

**Approved solution:** Zero-item orders out of both tasks. Regression: delivered orders with a valid lead time. Classification: orders not cancelled or unavailable, with a valid review; targets never imputed. Stated as a scope limit in the report

**What was done:** Population rules applied per task and written to exclusions.csv; counts in exclusion\_counts.csv. Test cutoffs (80/20 on eligible orders after the population rules, before the outlier rule): {'regression': '2018-05-26 18:18:03', 'classification': '2018-05-25 18:44:28'}.

**Reasoning:** Lead-time outliers are applied to the regression population only, because lead\_days exists only for delivered orders; distance outliers apply to both tasks. Flagged for the team to confirm.

| task | reason\_code | reason\_description | orders |
| --- | --- | --- | --- |
| regression | INVALID\_LEAD\_TIME | not delivered, or delivery time missing or not after purchase (s02 2.6, 2.8) | 2971 |
| regression | ZERO\_ITEMS | order has no items (s02 2.8) | 775 |
| classification | ZERO\_ITEMS | order has no items (s02 2.8) | 775 |
| classification | CANCELLED\_OR\_UNAVAILABLE | order cancelled or unavailable (s02 2.8) | 1234 |
| classification | NO\_VALID\_REVIEW | no valid review score (s02 2.8) | 768 |

| Task | Test cutoff (purchase\_ts) | Eligible after every rule | Eligible before cutoff |
| --- | --- | --- | --- |
| regression | 2018-05-26 18:18:03 | 96,432 | 77,139 |
| classification | 2018-05-25 18:44:28 | 97,464 | 77,971 |

**Files** (local, run 20261019T054216Z): records.csv.gz, exclusions.csv, exclusion\_counts.csv

#### 2.9 Outliers

**Approved solution:** Removed as suspected data-entry errors, in development and test alike: `lead_days` > max(100, mean + 12 × SD of pre-cutoff orders); `distance_km_max` > 4,397.53 km. Threshold and removal counts computed in s02 and logged

**What was done:** Lead-time threshold max(100, mean + 12 SD) = 133.91 days from pre-cutoff regression orders (mean 13.51, SD 10.03); distance limit 4397.53 km. Removals on or after each cutoff: \[{'task': 'regression', 'outlier\_removals\_on\_or\_after\_cutoff': 1}, {'task': 'classification', 'outlier\_removals\_on\_or\_after\_cutoff': 0}\].

| Key | Value |
| --- | --- |
| Rule | lead\_days > max(100, mean + 12 \* SD), mean and SD from pre-cutoff orders |
| Pre-cutoff mean / SD (days) | 13.51 / 10.03 |
| Lead-days threshold (days) | 133.91 |
| Latest purchase used for the statistics | 2018-05-26 18:16:57 |
| Distance limit (km) | 4397.53 |

| task | reason\_code | orders |
| --- | --- | --- |
| regression | LEAD\_DAYS\_OUTLIER | 35 |
| regression | DISTANCE\_OUTLIER | 0 |
| classification | DISTANCE\_OUTLIER | 0 |

Removals on or after each task's cutoff: regression 1; classification 0.

**Files** (local, run 20261019T054216Z): exclusions.csv, exclusion\_counts.csv, audit.json

#### 2.10 Missing installments

**Approved solution:** Orders with missing `payment_installments_max` removed (count logged); the app rejects the same input

**What was done:** Orders with no usable payment\_installments\_max removed from both tasks (MISSING\_INSTALLMENTS).

| task | reason\_code | reason\_description | orders |
| --- | --- | --- | --- |
| regression | MISSING\_INSTALLMENTS | payment\_installments\_max missing (s02 2.10) | 6 |
| classification | MISSING\_INSTALLMENTS | payment\_installments\_max missing (s02 2.10) | 6 |

**Files** (local, run 20261019T054216Z): exclusions.csv, exclusion\_counts.csv

#### 2.11 Missing payment

**Approved solution:** Orders without a usable payment (no payment rows, or only the not\_defined payment type) removed from both tasks (count logged); the app rejects the same input. payment\_missing is then always 0 and is excluded as constant

**What was done:** Orders with no payment rows or only not\_defined types removed from both tasks (NO\_USABLE\_PAYMENT).

| task | reason\_code | reason\_description | orders |
| --- | --- | --- | --- |
| regression | NO\_USABLE\_PAYMENT | no payment rows, or only the not\_defined payment type (s02 2.11) | 4 |
| classification | NO\_USABLE\_PAYMENT | no payment rows, or only the not\_defined payment type (s02 2.11) | 4 |

**Files** (local, run 20261019T054216Z): exclusions.csv, exclusion\_counts.csv

#### 2.12 Data documentation

**Approved solution:** Generated by the s02 code, following the NIBRS model the teacher shared. data\_dictionary.csv: one row per column of the 9 raw tables and of records.csv.gz, with type, nullable, grain, source, meaning of a missing value (missing / zero / unknown / not applicable), known at checkout, eligibility and a comment. figures/data\_structure.png: the tables, their keys and one-to-many links, and the aggregate-first join to one row per order. Used by the report, the s04 feature dictionary and the s10 app input checks

**What was done:** data\_dictionary.csv: 91 rows (every raw and records column, plus the three columns not in the contract); figures/data\_structure.png with its link table.

&#91;image: Data structure\]

data\_dictionary.csv has 91 rows: every column of the 9 raw tables, of records.csv.gz, and the 3 columns not in the contract. The records and not-built rows:

| table | column | known\_at\_checkout | eligibility | missing\_meaning | label\_available\_at |
| --- | --- | --- | --- | --- | --- |
| records | order\_id | yes | identifier | never missing |  |
| records | customer\_id | yes | identifier | never missing |  |
| records | customer\_unique\_id | yes | identifier | never missing |  |
| records | purchase\_ts | yes | prediction time | never missing |  |
| records | n\_items | yes | predictor (contract) | never missing |  |
| records | n\_products | yes | predictor (contract) | never missing |  |
| records | n\_sellers | yes | predictor (contract) | never missing |  |
| records | n\_categories | yes | predictor (contract) | never missing |  |
| records | total\_price | yes | predictor (contract) | missing (imputed later in the fold pipeline) |  |
| records | total\_freight | yes | predictor (contract) | missing (imputed later in the fold pipeline) |  |
| records | freight\_ratio | yes | predictor (contract) | missing (imputed later in the fold pipeline) |  |
| records | total\_weight\_g | yes | predictor (contract) | missing (imputed later in the fold pipeline) |  |
| records | total\_volume\_cm3 | yes | predictor (contract) | missing (imputed later in the fold pipeline) |  |
| records | weight\_missing\_fraction | yes | predictor (contract) | missing (imputed later in the fold pipeline) |  |
| records | volume\_missing\_fraction | yes | predictor (contract) | missing (imputed later in the fold pipeline) |  |
| records | primary\_category | yes | predictor (contract) | never missing |  |
| records | category\_missing\_fraction | yes | predictor (contract) | missing (imputed later in the fold pipeline) |  |
| records | customer\_state | yes | predictor (contract) | never missing |  |
| records | primary\_seller\_state | yes | predictor (contract) | never missing |  |
| records | distance\_km\_max | yes | predictor (contract) | missing (imputed later in the fold pipeline) |  |
| records | distance\_missing\_fraction | yes | predictor (contract) | missing (imputed later in the fold pipeline) |  |
| records | interstate\_share | yes | predictor (contract) | missing (imputed later in the fold pipeline) |  |
| records | purchase\_month | yes | predictor (contract) | never missing |  |
| records | purchase\_dayofweek | yes | predictor (contract) | never missing |  |
| records | purchase\_hour | yes | predictor (contract) | never missing |  |
| records | primary\_payment\_type | yes | predictor (contract) | never missing |  |
| records | payment\_installments\_max | yes | predictor (contract) | missing (imputed later in the fold pipeline) |  |
| records | n\_payment\_methods | yes | predictor (contract) | never missing |  |
| records | order\_estimated\_delivery\_date | yes | description only | not set |  |
| records | lead\_days | no | target (regression) | not delivered or invalid | lead\_label\_ts |
| records | lead\_label\_ts | no | label time | no valid lead time |  |
| records | is\_detractor | no | target (classification) | no valid review | review\_label\_ts |
| records | is\_detractor\_first | no | sensitivity label | no valid review | review\_label\_ts |
| records | review\_label\_ts | no | label time | no valid review |  |
| records | eligible\_regression |  | eligibility | never missing |  |
| records | eligible\_classification |  | eligibility | never missing |  |
| not built | has\_items | no | not in the contract |  |  |
| not built | freight\_ratio\_missing | no | not in the contract |  |  |
| not built | payment\_missing | yes | not in the contract |  |  |

**Files** (local, run 20261019T054216Z): data\_dictionary.csv, figures/data\_structure.png, figures/data\_structure.csv, figures/data\_structure.json

#### 2.13 Negative values

**Approved solution:** Orders with a negative value in a log1p candidate (total\_price, total\_freight, total\_weight\_g, total\_volume\_cm3, distance\_km\_max) removed from both tasks; zero kept, missing values stay missing. Every s02 removal rule writes exclusions.csv rows with step, reason\_code and reason\_description, one description per code pre-registered in protocol.yaml (G-63)

**What was done:** Orders with a negative value in \['total\_price', 'total\_freight', 'total\_weight\_g', 'total\_volume\_cm3', 'distance\_km\_max'\] removed from both tasks (NEGATIVE\_VALUE); zero kept.

| task | reason\_code | reason\_description | orders |
| --- | --- | --- | --- |
| regression | NEGATIVE\_VALUE | negative value in a log1p candidate (s02 2.13) | 0 |
| classification | NEGATIVE\_VALUE | negative value in a log1p candidate (s02 2.13) | 0 |

**Files** (local, run 20261019T054216Z): exclusions.csv, exclusion\_counts.csv

## Round history

### Round 1 — 2026-10-19

- First build of s02 from the raw Canvas tables and the staged IBGE boundary; cleaning, geography and aggregation logic ported from Milestone 2 into e5lib with provenance notes (CR-033).
- Foundation additions made s01 stale; s01 rerun with identical values, and its check 1.9 made rerun-safe (decision 3).
- Comments and resolutions: none yet.

### Round 2 — 2026-10-19

- Run 20261019T072845Z. Card 2.7 gains the zero-item reasoning promised in the 2.7 thread; no data output changed (all evidence hashes equal round 1).
- Comments answered in their threads: NO\_VALID\_REVIEW meaning, is\_detractor\_first and the label agreement, the 133.91-day threshold, order\_estimated\_delivery\_date (description only), the zero-item rule, the eligibility rules, distance\_missing\_fraction, the route-median fill, primary\_category translation. Two requests recorded for the s04 review tab: a feature × task table and evidence of imputation inside the folds.
- Outcome: all 13 rows Approved; accepted by the experiment lead; committed and tagged e5-s02-accepted (CR-035).
