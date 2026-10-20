---
node: s02_data/common
owner: TBD
reviewer: TBD
status: ACCEPTED
depends_on:
  - s01_problem/common
reads: []   # exact upstream files used
writes: []  # every file run.py produces
---

<!-- BEGIN GENERATED from spec/stages.json -->
# s02_data / common - Data preprocessing

Spec: `spec/pipeline_design.md` -> s02. Teacher/TA rows: `spec/sources.md` (search `S02`).
Blueprint: `spec/blueprints/s02_data.md` (implement only when its status is AGREED).

**Gate question:** Are joins, grains, targets and leakage exclusions verified?

## Purpose
Load and clean the nine Olist tables deterministically, join aggregation-first to one row per order, build both targets with label-availability timestamps, audit every column against checkout time and apply the zero-item classification rule. Population and data-quality rules applied to development and test alike: zero-item orders out of both tasks; classification limited to orders not cancelled or unavailable with a valid review; lead_days > max(100, mean + 12 SD of pre-cutoff orders) and distance_km_max > 4,397.53 km removed as suspected data-entry errors; orders with missing payment_installments_max removed.

## Planned outputs (`outputs/`)
- records.csv.gz (IDs for audit + features + targets + timestamps)
- exclusions.csv
- data_hashes.json (input and IBGE boundary sha256)
- audit.json (joins, grains, leakage, label sensitivity)
- data_dictionary.csv (every raw and derived column; NIBRS model, G-58)
- figures/data_structure.png (tables, keys, one-to-many links, aggregate-first join)

## Gate criteria
- Only row-local deterministic rules; nothing learned
- Every column classified as known or not known at checkout
- Minimum vs first review label sensitivity recorded
- Input hashes recorded
- Data dictionary covers every raw and derived column and matches the leakage tags (G-58)
- Per-task test cutoff computed by the 80/20 rule and recorded (not assumed from Milestone 2)
- Outlier threshold computed on pre-cutoff orders only; every removal counted in exclusions.csv
- order_status, order_approved_at, shipping_limit_date never predictors; has_items, freight_ratio_missing and payment_missing not in the 24-predictor contract (G-61)
- Date-order audit run on every order; violations logged
<!-- END GENERATED -->

## Working log (README section 9.1; one row per solution ID, every code change names its ID)
| ID | What was built | Commit | Evidence (files, figures) | Coverage | Round |
| --- | --- | --- | --- | --- | --- |
| 2.1 | Load: Nine raw tables read with declared types; sha256 of every file and of the IBGE archive, derived geometry and manifest in data_hashes.json (12 files). | acceptance commit (e5-s02-accepted) | data_hashes.json | IMPLEMENTED | 1 |
| 2.2 | Clean: Declared types per the Milestone 2 cleaning schema; ZIP prefixes read as strings; categorical domains checked (violations kept, listed in audit.json); geolocation exact duplicates dropped: 261,831 of 1,000,163 rows. No imputation. | acceptance commit (e5-s02-accepted) | audit.json | IMPLEMENTED | 1 |
| 2.3 | Geography: ZIP/state median centroids after the IBGE boundary filter: 738,303 of 738,332 geolocation rows accepted; 19,023 keys, by status {'resolved': 19015, 'median_outside_polygon': 4, 'no_surviving_coordinates': 4}. | acceptance commit (e5-s02-accepted) | zip_centroids.csv, data_hashes.json, audit.json | IMPLEMENTED | 1 |
| 2.4 | Join: Items, payments and reviews aggregated to order_id first, then left-joined one-to-one (pandas validate); output rows 99,441 = orders 99,441. | acceptance commit (e5-s02-accepted) | records.csv.gz, audit.json | IMPLEMENTED | 1 |
| 2.5 | Predictors: The 24 predictors of e5lib/contract.py built with the Milestone 2 formulas; calendar fields numeric; has_items, freight_ratio_missing and payment_missing not built. Screening candidates (G-68, classification only, not predictors): product_photos_qty, product_description_lenght, product_name_lenght, est_delivery_days, customer_region, seller_region, region_pair, seller_prior_review_mean, seller_prior_review_count, seller_prior_detractor_share, seller_prior_delivered_count, seller_prior_late_share. Product fields from the primary item; est_delivery_days = estimated delivery date minus purchase; regions are the IBGE macro-regions of the customer and primary-seller states and their pair; seller history uses only the primary seller's events strictly before purchase, own order excluded. | acceptance commit (e5-s02-accepted) | records.csv.gz | IMPLEMENTED | 1 |
| 2.6 | Targets: lead_days for delivered orders with delivery after purchase; is_detractor from the minimum valid score; first-review label kept. Min and first labels agree on 98,615 of 98,673 reviewed orders. | acceptance commit (e5-s02-accepted) | records.csv.gz, audit.json | IMPLEMENTED | 1 |
| 2.7 | Leakage audit: Every raw and records column tagged known / not known at checkout (data_dictionary.csv, audit.json); date-order violations logged: {'order_purchase_timestamp <= order_approved_at': 0, 'order_approved_at <= order_delivered_carrier_date': 1359, 'order_delivered_carrier_date <= order_delivered_customer_date': 23, 'order_estimated_delivery_date > order_purchase_timestamp': 0, 'first review answer > order_purchase_timestamp': 63, 'order_delivered_customer_date > order_purchase_timestamp (delivered orders)': 0}. | acceptance commit (e5-s02-accepted) | data_dictionary.csv, audit.json | IMPLEMENTED | 1 |
| 2.8 | Populations: Population rules applied per task and written to exclusions.csv; counts in exclusion_counts.csv. Test cutoffs (80/20 on eligible orders after the population rules, before the outlier rule): {'regression': '2018-05-27 12:30:34', 'classification': '2018-05-26 12:16:34'}. | acceptance commit (e5-s02-accepted) | records.csv.gz, exclusions.csv, exclusion_counts.csv | IMPLEMENTED | 1 |
| 2.9 | Outliers: Lead-time threshold max(100, mean + 12 SD) = 133.71 days from pre-cutoff regression orders (mean 13.49, SD 10.02); distance limit 4397.53 km. Removals on or after each cutoff: [{'task': 'regression', 'outlier_removals_on_or_after_cutoff': 1}, {'task': 'classification', 'outlier_removals_on_or_after_cutoff': 0}]. | acceptance commit (e5-s02-accepted) | exclusions.csv, exclusion_counts.csv, audit.json | IMPLEMENTED | 1 |
| 2.10 | Missing installments: Orders with no usable payment_installments_max removed from both tasks (MISSING_INSTALLMENTS). | acceptance commit (e5-s02-accepted) | exclusions.csv, exclusion_counts.csv | IMPLEMENTED | 1 |
| 2.11 | Missing payment: Orders with no payment rows or only not_defined types removed from both tasks (NO_USABLE_PAYMENT). | acceptance commit (e5-s02-accepted) | exclusions.csv, exclusion_counts.csv | IMPLEMENTED | 1 |
| 2.12 | Data documentation: data_dictionary.csv: 103 rows (every raw and records column, plus the three columns not in the contract); figures/data_structure.png with its link table. | acceptance commit (e5-s02-accepted) | data_dictionary.csv, figures/data_structure.png, figures/data_structure.csv, figures/data_structure.json | IMPLEMENTED | 1 |
| 2.13 | Negative values: Orders with a negative value in ['total_price', 'total_freight', 'total_weight_g', 'total_volume_cm3', 'distance_km_max'] removed from both tasks (NEGATIVE_VALUE); zero kept. | acceptance commit (e5-s02-accepted) | exclusions.csv, exclusion_counts.csv | IMPLEMENTED | 1 |

## Review rounds (append-only; each round has review/round_N/ and a section in the doc tab)
| Round | Commit | Run ID | Review pack | Outcome | Date |
| --- | --- | --- | --- | --- | --- |
| 1 | uncommitted on 123cf32 (G-64) | 20261019T054216Z | review/round_1/review_pack.md | all 13 rows approved; 4 decisions accepted with the stage (G-66, G-67); promised card 2.7 line | 2026-10-19 |
| 2 | acceptance commit (tag e5-s02-accepted) | 20261019T072845Z | review/round_2/review_pack.md | accepted: card 2.7 text only, every data output identical to round 1 | 2026-10-19 |

## Accepted result (the only result the report and slides may cite)
- **Current run to cite: 20261020T145526Z** (CR-048, 2026-10-20). The working log above shows this run's values; the lines below record the acceptance history.
- Accepted round: 2 - commit: the "s02 accepted" commit, tag `e5-s02-accepted` - run ID: 20261019T072845Z - approved by: experiment lead (Wu Qianzong), after team review in the doc tab "Implementation reviews › s02 Data" - date: 2026-10-19
- Evidence: `outputs/_manifest.json`, `review/round_2/review_pack.md`; test cutoffs in `spec/protocol.yaml` (data_dependent.test_cutoffs).

## Changes after acceptance (README section 9.2)
- 2026-10-19, CR-037 (G-68): records.csv.gz gains product_photos_qty, product_description_lenght and product_name_lenght (value of the primary item, missing stays missing), tagged known at checkout, with data dictionary rows and a new check (2.5, 2.7, 2.12). Populations, exclusions and test cutoffs unchanged. Rerun 20261019T140111Z. Approved by the experiment lead; reviewed with s03 round 2 in the doc (dated addendum on this stage's tab). Status stays ACCEPTED (no decision.json changed).
- 2026-10-19, CR-038 (G-69): records gain est_delivery_days, customer_region, seller_region, region_pair and five seller_prior_* columns; new checks: seller history equals a direct recomputation on 2,000 random orders, est_delivery_days after purchase and regions complete. Populations, exclusions and test cutoffs unchanged. Rerun 20261019T151257Z. Approved by the experiment lead; reviewed with s03 round 3. Status stays ACCEPTED.
- 2026-10-20, CR-042 (G-71, external audit): rerun 20261019T163328Z on a clean tree (dirty false); classification removes orders with a review answered at or before purchase (2.8, INVALID_REVIEW_TIME, 63 orders in exclusions.csv); seller_prior_* columns no longer count such reviews; new check (G-71). Classification eligible 97,464 → 97,457, pre-cutoff 77,971 → 77,965; classification test cutoff 2018-05-25 18:44:28 → 18:43:19 (audit.json, protocol.yaml). Regression unchanged. Approved by the experiment lead. Status stays ACCEPTED (no decision.json changed).
- 2026-10-20, CR-043 (G-72, data start 2017-01-01): rerun 20261020T053117Z on a clean tree (dirty false); orders purchased before 2017-01-01 leave both tasks (2.8, BEFORE_DATA_START, 329 orders per task in exclusion_counts.csv) and their reviews and deliveries leave the seller-history inputs; new check (G-72). Eligible regression 96,432 → 96,166, classification 97,457 → 97,170; test cutoffs regression 2018-05-26 18:18:03 → 2018-05-27 12:30:34, classification 2018-05-25 18:43:19 → 2018-05-26 12:16:34; lead-time outlier threshold 133.91 → 133.71 days (audit.json, protocol.yaml). Approved by the experiment lead. Status stays ACCEPTED (no decision.json changed).
- 2026-10-20, CR-044 to CR-048 (s04/s05 build): rerun 20261020T145526Z on a clean tree (commit c7114d3 and its index follow-up); data_dictionary.csv: missing meaning of the seller-history screening columns corrected (it said "product without a catalogue value"), catalogue note limited to the product fields; every other output unchanged. Approved by the experiment lead. Status stays ACCEPTED.

## Deviations from blueprint
None.

## Open questions
- Resolved: lead-time outliers from regression only, distance outliers from both tasks (G-66).
- Resolved: test cutoff after the row-local population rules, before the outlier rule (G-67).
