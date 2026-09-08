"""Core-layer builder (docs/data_architecture.md §4.3).

Reads the staging Parquet tables and produces the eight canonical fact/dimension
tables in ``data/processed/core/``. Every table has an explicit grain and
primary-key expectation; a failed contract check stops the pipeline (§7).

Facts keep the canonical source columns only. Derived outcomes (delivery_days,
late_days, is_on_time, is_late, ...) are deferred to the business marts.

Usage:
    python preprocessing/build_core.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common import core_schemas, schemas  # noqa: E402
from preprocessing import validation  # noqa: E402

# Brazil bounding box. Staging keeps the 26 out-of-Brazil geolocation rows (its
# grain is source-aligned); the core dim_geography filters to Brazil before
# building zip centroids (§4.2 notes, §4.3 grain rule).
BR_LAT = (-33.75, 5.30)
BR_LNG = (-74.00, -34.00)


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    """Convert category/string dtypes to object for clean, warning-free joins.

    Dates stay datetime64, numerics stay numeric, and missing values survive as
    NaN (a nullable <NA> becomes NaN, which pandas treats identically here).
    """
    out = df.copy()
    for c in df.columns:
        d = df[c].dtype
        if isinstance(d, pd.CategoricalDtype) or isinstance(d, pd.StringDtype):
            out[c] = df[c].astype(object)
    return out


def _mode(s: pd.Series):
    """Most common non-null value of a group (None when the group is empty)."""
    m = s.dropna().mode()
    return m.iloc[0] if len(m) else None


def build_core(staging_dir: Path) -> dict[str, pd.DataFrame]:
    """Build the eight core tables from staging. No cross-table business
    aggregations here — facts stay source-aligned, dimensions add only lookups.
    """
    orders = _normalize(pd.read_parquet(staging_dir / "orders.parquet"))
    items = _normalize(pd.read_parquet(staging_dir / "order_items.parquet"))
    payments = _normalize(pd.read_parquet(staging_dir / "payments.parquet"))
    reviews = _normalize(pd.read_parquet(staging_dir / "reviews.parquet"))
    customers = _normalize(pd.read_parquet(staging_dir / "customers.parquet"))
    sellers = _normalize(pd.read_parquet(staging_dir / "sellers.parquet"))
    products = _normalize(pd.read_parquet(staging_dir / "products.parquet"))
    geolocation = _normalize(pd.read_parquet(staging_dir / "geolocation.parquet"))
    translation = _normalize(pd.read_parquet(staging_dir / "translation.parquet"))

    # ---- facts: canonical, source-aligned (FKs resolve to dimensions) ----
    fact_orders = orders.copy()
    fact_order_items = items.copy()
    fact_payments = payments.copy()
    fact_reviews = reviews.copy()

    # ---- dim_customers: one row per customer_id -------------------------
    # customer_unique_id is the customer-level rollup key (NOT interchangeable
    # with customer_id — §4.3). Both are kept so facts can join on customer_id.
    dim_customers = customers.copy()

    # ---- dim_products: product_id + English category name (lookup only) --
    dim_products = products.merge(
        translation[["product_category_name", "product_category_name_english"]],
        on="product_category_name", how="left",
    )
    dim_products["product_category_name_english"] = (
        dim_products["product_category_name_english"]
        .fillna(dim_products["product_category_name"])
        .fillna("unknown")
    )
    # place the English name next to its Portuguese source (canonical order)
    dim_products = dim_products[
        ["product_id", "product_category_name", "product_category_name_english",
         "product_name_lenght", "product_description_lenght",
         "product_photos_qty", "product_weight_g", "product_length_cm",
         "product_height_cm", "product_width_cm"]
    ]

    # ---- dim_sellers: one row per seller_id ------------------------------
    dim_sellers = sellers.copy()

    # ---- dim_geography: one row per zip prefix, Brazil-filtered centroid --
    geo = geolocation[
        geolocation["geolocation_lat"].between(*BR_LAT)
        & geolocation["geolocation_lng"].between(*BR_LNG)
    ]
    counts = geo.groupby("geolocation_zip_code_prefix").size().rename("n_records")
    centroids = geo.groupby("geolocation_zip_code_prefix").agg(
        geolocation_state=("geolocation_state", _mode),
        geolocation_city=("geolocation_city", _mode),
        centroid_lat=("geolocation_lat", "mean"),
        centroid_lng=("geolocation_lng", "mean"),
    )
    dim_geography = centroids.join(counts).reset_index()

    return {
        "fact_orders": fact_orders,
        "fact_order_items": fact_order_items,
        "fact_payments": fact_payments,
        "fact_reviews": fact_reviews,
        "dim_customers": dim_customers,
        "dim_products": dim_products,
        "dim_sellers": dim_sellers,
        "dim_geography": dim_geography,
    }


def main() -> None:
    staging_dir = ROOT / "data" / "staging"
    core_dir = ROOT / "data" / "processed" / "core"

    required = [
        "orders", "order_items", "payments", "reviews",
        "customers", "sellers", "products", "geolocation", "translation",
    ]
    missing = [t for t in required if not (staging_dir / f"{t}.parquet").exists()]
    if missing:
        sys.exit("FATAL: missing staging tables: " + ", ".join(missing)
                 + " — run build_staging.py first.")

    core_dir.mkdir(parents=True, exist_ok=True)
    core = build_core(staging_dir)

    failed = False
    for name in core_schemas.CORE_ORDER:
        df = core[name]
        spec = core_schemas.CORE_SCHEMAS[name]
        issues = validation.check_core_table(name, df)
        if issues:
            failed = True
            print(f"[FAIL] {name}: not written")
            for f in issues:
                print(f"        - {f}")
            continue
        df = df[spec["columns"]]  # enforce canonical column order
        df.to_parquet(core_dir / f"{name}.parquet", index=False)
        print(f"[OK]   {name:16s} {len(df):>9,} rows -> {name}.parquet")

    # referential integrity: every fact FK must resolve to a dimension PK (§7)
    ri_issues = validation.check_referential_integrity(core)
    for f in ri_issues:
        failed = True
        print(f"[FAIL] referential integrity: {f}")

    if failed:
        sys.exit("\nCore build ABORTED: invalid tables were not written.")

    print("\nAll 8 core tables validated and written to data/processed/core/.")
    print("Run `python preprocessing/build_marts.py` next.")


if __name__ == "__main__":
    main()
