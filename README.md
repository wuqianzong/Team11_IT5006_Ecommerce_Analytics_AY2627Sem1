# IT5006 Group 11 — Dashboard (Milestone 1)

Layered data pipeline + Streamlit executive dashboard for the Olist e-commerce
dataset, built to the team specification in `docs/data_architecture.md`.

This branch holds the **code (the reproducible template)**. Generated data is
**not committed** (see *Data policy* below) — it is regenerated locally by
running the pipeline.

## Structure

```
app.py                        Streamlit dashboard entry point
dashboard/                    Dashboard module (charts, tables, theme, loader)
preprocessing/                Pipeline: raw -> staging -> core -> marts -> validation
src/common/                   Data contracts (schemas, core_schemas, loaders)
docs/data_architecture.md     Authoritative team specification
data/                         Empty layer directories (data is generated locally)
```

## Data flow

| Layer | Location | Notes |
| --- | --- | --- |
| Raw | `data/raw/` | 9 original Olist CSVs, immutable, SHA-256 recorded |
| Staging | `data/staging/` | typed, source-aligned Parquet; no joins/aggregations |
| Core | `data/processed/core/` | 8 facts/dimensions, explicit grain + primary key |
| Marts | `data/processed/marts/` | 5 dashboard-ready tables; outcomes labelled here |
| Dashboard | `app.py` + `dashboard/` | reads marts only |

## Run the dashboard

```bash
streamlit run app.py
```

## Regenerate the data

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
- **Marts** — 5/5 tables OK.

## Data policy

Generated data (`data/raw/`, `data/staging/`, `data/processed/`) is gitignored and
not committed, per `docs/data_architecture.md` §4.1 and `.gitignore`. The code is
the template: running the pipeline over the same source reproduces byte-identical
Parquet (determinism is validated).

## Notes

- `customer_id` and `customer_unique_id` are **not** interchangeable; both are kept.
- Outcome columns (`delivery_days`, `is_on_time`, `is_late`, `late_days`) live only
  in the marts and are reserved for Milestone 2 ML targets.
