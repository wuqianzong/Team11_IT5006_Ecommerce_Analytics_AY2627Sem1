# s02_data — blueprint

| Field | Value |
| --- | --- |
| Stage | s02_data (`../pipeline_design.md` → s02) |
| Nodes | common |
| Status | AGREED |
| Owner | TBD |
| Last agreed | 2026-10-18 (audit 3, CR-022); first 2026-10-17 (team walkthrough, doc tab "Feature solution (s02–s05)") |
| Discussion | Claude Doc "Milestone 3 pipeline stages", tab "Feature solution (s02–s05)", section s02 |

## 1. Goal and gate
Goal: one row per order with audit IDs, the 24 contract predictors (`e5lib/contract.py`, G-61), both targets with label-available
times, and every exclusion counted.
Gate: joins, grains, targets and leakage exclusions verified (`../stages.json`).

## 2. Inputs
- The Canvas copy of the nine Olist CSVs (read-only, outside Experiment 5).
- IBGE boundary archive staged per `docs/references/geography/README.md`.
- `spec/protocol.yaml`: the 80/20 split rule, outlier rule constants (100 days, 12 SD,
  4,397.53 km).
- Population: all orders. The outlier threshold statistics use orders before the test cutoff only.

## 3. Method
1. **Load.** Read the nine tables; record sha256 of every file in `data_hashes.json`.
2. **Clean.** Declared types; ZIP prefixes as strings (leading zeros kept); categorical domain
   checks logged, rows kept; geolocation exact duplicates dropped (counts recomputed and logged).
   No imputation.
3. **Geography.** ZIP centroids = median latitude/longitude per ZIP prefix and state, after the
   IBGE Brazil boundary filter; archive and derived-geometry hashes recorded.
4. **Join.** Orders ← customers (many-to-one on `customer_id`). Items, payments and reviews are
   aggregated to `order_id` first, then left-joined one-to-one. Assert key uniqueness, merge
   cardinality, and output rows = orders.
5. **Predictors.** Build the 24 predictors of `e5lib/contract.py` (basket, price and freight,
   physical totals and missing fractions, primary category and seller state, distance,
   interstate share, calendar, payment) with the Milestone 2 formulas (G-61). `has_items`,
   `freight_ratio_missing` and `payment_missing` are not in the contract and are not built.
   Also built, as screening columns for s03 classification only (not predictors; G-68, CR-037):
   `product_photos_qty`, `product_description_lenght`, `product_name_lenght`, each the value of the
   primary item; catalogue fields are assumed fixed at checkout. CR-038 (G-69) adds est_delivery_days,
   customer_region, seller_region, region_pair and the seller_prior_* history columns (events of the primary
   seller strictly before purchase, own order excluded, reviews answered at or before their own order's
   purchase never counted (G-71); checked against a direct recomputation).
6. **Targets.** `lead_days` = delivery − purchase in fractional days (delivered, valid
   timestamps, > 0), label available at delivery. `is_detractor` = minimum valid review score ≤ 2,
   label available at the last review answer. Keep the first-review label for a sensitivity
   check.
7. **Leakage audit** (G-30). Tag every column known / not known at checkout.
   - Never predictors (post-purchase leakage, or constant after the population rules): `order_status`,
     `order_approved_at`, carrier and customer delivery dates, `shipping_limit_date`, review
     fields. `has_items` and `freight_ratio_missing` would encode a later cancellation and
     `payment_missing` would be constant after step 11, so none of them is in the contract
     (G-30, G-42, G-51, G-61). `order_estimated_delivery_date`
     is known at checkout but is never a predictor (G-35); it is kept in `records.csv.gz` only for
     the s03 late-vs-promised trend.
   - Date-order audit on every order: purchase ≤ approval ≤ carrier ≤ delivery; estimated date >
     purchase; review answer > purchase. Violations logged in `audit.json`; an order whose
     delivery is not after purchase leaves regression (step 6).
   - Payment fields have no timestamp; "chosen at checkout" is a stated assumption.
   - Final `order_status` defines populations only (step 8), never an input.
8. **Populations** (G-20). Orders purchased before 2017-01-01 00:00:00 out of both tasks
   (BEFORE_DATA_START, G-72): the 2016 months are too thin to be representative; their reviews and
   deliveries never count in seller history. Zero-item orders out of both tasks. Regression: delivered orders with
   a valid lead time. Classification: orders not cancelled or unavailable, with a valid review;
   targets never imputed. An order with a review answered at or before its purchase leaves
   classification (INVALID_REVIEW_TIME, G-71): the timing is impossible, so its label is not trusted.
9. **Outliers** (G-21). Remove, from development and test alike: `lead_days` > max(100, mean +
   12 × SD), with mean and SD from pre-cutoff orders only; `distance_km_max` > 4,397.53 km.
   The number of orders this removes on or after each task's test cutoff is recorded in
   `exclusions.csv` and stated in the s09 limitations (audit 2 A1, rule kept by the team).
   The lead-time rule removes orders from the regression population only (lead_days exists only
   for delivered orders); the distance rule removes them from both tasks (G-66).
10. **Missing installments** (G-20). Remove orders with missing `payment_installments_max`.
11. **Missing payment** (G-51). Remove orders without a usable payment (no payment rows, or only
    the `not_defined` payment type) from both tasks; count logged in `exclusions.csv`; the app
    rejects the same input.
12. **Negative values** (G-62; doc row 2.13). Remove, from both tasks, orders with a negative
    value in a log1p candidate (`total_price`, `total_freight`, `total_weight_g`,
    `total_volume_cm3`, `distance_km_max`); zero is kept (log1p(0) = 0) and missing values stay
    missing. Applied with steps 10–11.
13. **Test cutoff** (G-28, G-67). Per task, after every row-local population rule (steps 6, 8, 10,
    11, 12) and before the outlier rule (step 9): the purchase timestamp at the
    80% position of eligible orders, recorded in `audit.json` and added to `protocol.yaml`
    (data-dependent layer). Not taken from Milestone 2. Step 9's outlier statistics use orders
    before this cutoff.

14. **Data documentation** (G-58; doc row 2.12). Generated by the s02 code, never written by hand,
    following the NIBRS data-dictionary model the teacher shared (`docs/references/NIBRS/`):
    - `data_dictionary.csv`: one row per column of the 9 raw tables and of `records.csv.gz`, with
      table, column, type, nullable, grain, source table and column, meaning of a missing value
      (missing / zero / unknown / not applicable, e.g. no payment rows, `not_defined`, "Unknown"
      category, missing distance), known at checkout (yes / no, from step 7), label-available
      time where relevant, eligibility (eligible / excluded and reason), and a comment.
    - `figures/data_structure.png` with its sidecar data: the 9 tables with their keys and
      one-to-many links (orders to items, payments and reviews; customers to orders), and the
      aggregate-first join to one row per order (step 4).

## 4. Decisions
| ID | Question | Answer | Basis | Status |
| --- | --- | --- | --- | --- |
| s02-D1 | Populations | As step 8 | G-20 | Agreed |
| s02-D2 | Outlier removal | As step 9 | G-21 (team instruction) | Agreed |
| s02-D3 | Missing installments | Remove; app rejects the same input | G-20 | Agreed |
| s02-D8 | Data documentation | Generated data dictionary and structure diagram (NIBRS model) | G-58 | Agreed |
| s02-D11 | Outlier scope and cutoff placement | Lead-time outliers leave regression only, distance outliers both tasks (G-66); cutoff after the row-local rules, before the outlier rule (G-67) | s02 review round 1 | Agreed |
| s02-D9 | Negative values | Remove orders with a negative log1p candidate value (2.13); zero kept | G-62 | Agreed |
| s02-D10 | Exclusion record | Every removal rule writes exclusions.csv rows with a reason code and its one description | G-63 | Agreed |
| s02-D7 | Missing payment | Remove orders without a usable payment (2.11); payment_missing becomes constant and is excluded as constant | G-51 | Agreed |
| s02-D5 | Test cutoff | Recomputed per task by the 80/20 rule | G-28 | Agreed |
| s02-D6 | Post-purchase columns and date audit | As step 7 | G-30 | Agreed |
| s02-D4 | Label rule | Minimum review score, first-review sensitivity | Milestone 1 TA | Agreed |

## 5. Outputs
- `records.csv.gz`: `order_id`, `customer_id`, `customer_unique_id`, `purchase_ts`, the 24
  contract predictors, `order_estimated_delivery_date`, `lead_days`, `lead_label_ts`, `is_detractor`,
  `is_detractor_first`, `review_label_ts`, `eligible_regression`, `eligible_classification`.
- `exclusions.csv`: `order_id`, `task`, `step`, `reason_code`, `reason_description` (one row per
  removed order and reason, for every removal rule in steps 6–12; codes and descriptions from
  `protocol.yaml` `populations.exclusions`, one description per code; G-63).
- `data_hashes.json`, `audit.json` (key and cardinality checks, leakage tags, label agreement,
  outlier threshold actually computed, counts per rule).
- `data_dictionary.csv` and `figures/data_structure.png` (+ sidecar), as step 14 (G-58).

## 6. Checks
- Every column of the 9 raw tables and of `records.csv.gz` has exactly one row in
  `data_dictionary.csv`, and its known-at-checkout tag matches `audit.json` (G-58).
- Output rows = input orders before exclusions; `order_id` unique and non-null.
- No predictor tagged "not known at checkout".
- Outlier threshold computed only from orders with purchase < cutoff (assert on the timestamps).
- Exclusion counts per rule recorded; no order silently dropped.

## 7. Milestone 2 reuse
Copy into `e5lib/` with provenance comments: `notebooks/01_data_cleaning.ipynb` (cleaning rules),
`src/features/aggregation.py`, `src/features/geography.py`, `src/features/build_features.py`. The predictor list is not copied: it comes from
`e5lib/contract.py` (G-61). Fix when copying: keep calendar fields numeric (G-22, used in s04);
add the label-available timestamps and the new exclusion rules.

## 8. Report hooks
Dataset and preprocessing section: tables used, the data structure diagram and data dictionary
(appendix), exclusion counts per rule, label sensitivity result.

## 9. Open questions
None.
