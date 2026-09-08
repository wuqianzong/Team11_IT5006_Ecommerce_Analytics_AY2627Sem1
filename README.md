# IT5006 Group 11 — Dashboard (Milestone 1)

Layered data pipeline + Streamlit executive dashboard for the Olist e-commerce
dataset, built to the team specification in `docs/data_architecture.md`.

This branch ships the **dashboard and the pre-generated processed data together**:
teammates can run the dashboard or load the data directly without re-running the
pipeline. The source-raw CSVs (a public byte-for-byte copy, ~121 MB) are **not**
committed — see *Data policy* below.

## Structure

```
app.py                        Streamlit dashboard entry point
dashboard/                    Dashboard module (charts, tables, theme, loader)
preprocessing/                Pipeline: raw -> staging -> core -> marts -> validation
src/common/                   Data contracts (schemas, core_schemas, loaders)
docs/data_architecture.md     Authoritative team specification
data/
  staging/                    9 typed, source-aligned Parquet tables (committed)
  processed/core/             8 canonical fact/dimension tables (committed)
  processed/marts/            5 presentation-ready business marts (committed)
  metadata/raw_manifest.csv   Raw-file manifest: byte count, row count, SHA-256 (committed)
```

## Data flow

| Layer | Location | Notes |
| --- | --- | --- |
| Raw | `data/raw/` | 9 original Olist CSVs, immutable, SHA-256 recorded (not committed) |
| Staging | `data/staging/` | typed, source-aligned Parquet; no joins/aggregations |
| Core | `data/processed/core/` | 8 facts/dimensions, explicit grain + primary key |
| Marts | `data/processed/marts/` | 5 dashboard-ready tables; outcomes labelled here |
| Dashboard | `app.py` + `dashboard/` | reads marts only |

## Run the dashboard (works out of the box)

```bash
streamlit run app.py
```

## Regenerate the data (reproduce the pipeline)

```bash
python preprocessing/ingest_raw.py --source ../archive   # copy raw CSVs + manifest
python preprocessing/build_staging.py                     # raw -> typed staging
python preprocessing/build_core.py                        # staging -> 8 core tables
python preprocessing/build_marts.py                       # core -> 5 marts
python preprocessing/validation.py --determinism          # full contract check
```

## Validation status (all green)

- **Raw** — 9 files, byte counts + SHA-256 + row counts match the manifest.
- **Staging** — 9/9 tables OK (columns, dtypes, PK, categorical values, ranges, row counts, determinism).
- **Core** — 8/8 tables OK; referential integrity passed (6 FK→PK pairs).

  | table | rows |
  | --- | --- |
  | fact_orders | 99,441 |
  | fact_order_items | 112,650 |
  | fact_payments | 103,886 |
  | fact_reviews | 99,224 |
  | dim_customers | 99,441 |
  | dim_products | 32,951 |
  | dim_sellers | 3,095 |
  | dim_geography | 19,010 |

- **Marts** — 5/5 tables OK.

  | table | rows |
  | --- | --- |
  | mart_order_dashboard | 99,441 |
  | mart_order_items | 112,650 |
  | mart_category_daily | 18,990 |
  | mart_state_summary | 27 |
  | mart_data_quality | 12 |

## Data policy

- **Committed**: `data/staging/`, `data/processed/core/`, `data/processed/marts/`,
  and `data/metadata/raw_manifest.csv` — the directly-usable processed data.
- **Not committed**: `data/raw/` (the 9 source CSVs, ~121 MB), a byte-for-byte copy
  of the public Olist dataset; regenerate it with `ingest_raw.py --source ../archive`.

## Notes

- `customer_id` and `customer_unique_id` are **not** interchangeable; both are kept.
- Outcome columns (`delivery_days`, `is_on_time`, `is_late`, `late_days`) live only
  in the marts and are reserved for Milestone 2 ML targets.
