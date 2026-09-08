"""Business-mart builder (docs/data_architecture.md §4.4).

Reads the core tables and produces flat, presentation-ready tables in
``data/processed/marts/``. All joins and metric logic live here in code, so the
dashboard reads materialized marts instead of re-deriving joins and metrics.

Marts produced:
  - mart_order_dashboard : one row per order, including observed outcomes.
  - mart_order_items     : one row per (order, item) — for category/seller detail.
  - mart_category_daily  : one row per (date, category) — additive daily counts.
  - mart_state_summary   : one row per state — centroid + order aggregates.
  - mart_data_quality    : one row per table — operational visibility of checks.

Usage:
    python preprocessing/build_marts.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common import core_schemas, schemas  # noqa: E402
from preprocessing import validation  # noqa: E402


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for c in df.columns:
        d = df[c].dtype
        if isinstance(d, pd.CategoricalDtype) or isinstance(d, pd.StringDtype):
            out[c] = df[c].astype(object)
    return out


def _add_temporal(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["order_purchase_date"] = df["order_purchase_timestamp"].dt.normalize()
    df["year"] = df["order_purchase_timestamp"].dt.year
    df["month"] = df["order_purchase_timestamp"].dt.month
    df["year_month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
    df["day_of_week"] = df["order_purchase_timestamp"].dt.dayofweek  # 0 = Monday
    df["day_name"] = df["order_purchase_timestamp"].dt.day_name()
    df["hour"] = df["order_purchase_timestamp"].dt.hour
    return df


def _add_delivery_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Observed outcomes — allowed in descriptive marts, never in ML features."""
    df = df.copy()
    delivered = df["order_delivered_customer_date"].notna()
    df["delivery_days"] = (
        df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
    ).dt.days
    df["late_days"] = (
        df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]
    ).dt.days
    df["is_on_time"] = pd.Series(np.nan, index=df.index, dtype="boolean")
    df["is_late"] = pd.Series(np.nan, index=df.index, dtype="boolean")
    df.loc[delivered, "is_on_time"] = (
        df.loc[delivered, "order_delivered_customer_date"]
        <= df.loc[delivered, "order_estimated_delivery_date"]
    )
    df.loc[delivered, "is_late"] = (
        df.loc[delivered, "order_delivered_customer_date"]
        > df.loc[delivered, "order_estimated_delivery_date"]
    )
    return df


def _load_core(core_dir: Path) -> dict[str, pd.DataFrame]:
    return {
        name: _normalize(pd.read_parquet(core_dir / f"{name}.parquet"))
        for name in core_schemas.CORE_ORDER
    }


def _payment_summary(payments: pd.DataFrame) -> pd.DataFrame:
    agg = payments.groupby("order_id").agg(
        payment_value_total=("payment_value", "sum"),
        payment_installments_max=("payment_installments", "max"),
        payment_count=("payment_sequential", "max"),
    ).reset_index()
    # primary payment type = the type with the largest total value for the order
    primary = (
        payments.groupby(["order_id", "payment_type"])["payment_value"].sum()
        .reset_index()
        .sort_values(["order_id", "payment_value"], ascending=[True, False])
        .drop_duplicates("order_id")[["order_id", "payment_type"]]
        .rename(columns={"payment_type": "payment_type_primary"})
    )
    return agg.merge(primary, on="order_id", how="left")


def _review_primary(reviews: pd.DataFrame) -> pd.DataFrame:
    return (
        reviews.sort_values("review_creation_date")
        .drop_duplicates("order_id", keep="first")[
            ["order_id", "review_score", "review_creation_date"]
        ]
    )


def build_marts(core_dir: Path) -> dict[str, pd.DataFrame]:
    c = _load_core(core_dir)
    fact_orders = c["fact_orders"]
    fact_order_items = c["fact_order_items"]
    dim_customers = c["dim_customers"]
    dim_products = c["dim_products"]
    dim_sellers = c["dim_sellers"]
    dim_geography = c["dim_geography"]

    review_primary = _review_primary(c["fact_reviews"])
    payment_summary = _payment_summary(c["fact_payments"])

    # ---- mart_order_items: item grain with category/seller/order context ----
    items_agg = fact_order_items.merge(
        dim_products[["product_id", "product_category_name",
                      "product_category_name_english", "product_weight_g"]],
        on="product_id", how="left",
    )
    items_agg = items_agg.merge(
        fact_orders[["order_id", "customer_id", "order_status",
                     "order_purchase_timestamp", "order_delivered_customer_date",
                     "order_estimated_delivery_date"]],
        on="order_id", how="left",
    )
    items_agg = items_agg.merge(
        dim_customers[["customer_id", "customer_unique_id",
                       "customer_city", "customer_state"]],
        on="customer_id", how="left",
    )
    items_agg = items_agg.merge(
        dim_sellers[["seller_id", "seller_city", "seller_state"]],
        on="seller_id", how="left",
    )
    items_agg = items_agg.merge(review_primary, on="order_id", how="left")
    items_agg = items_agg.merge(payment_summary, on="order_id", how="left")
    items_agg = _add_temporal(items_agg)
    items_agg = _add_delivery_metrics(items_agg)
    items_agg["item_value"] = items_agg["price"] + items_agg["freight_value"]

    # ---- mart_order_dashboard: order grain with rolled-up item/review/payment -
    items_for_order = fact_order_items.merge(
        dim_products[["product_id", "product_category_name_english"]],
        on="product_id", how="left",
    )
    items_for_order["item_value"] = (
        items_for_order["price"] + items_for_order["freight_value"]
    )
    order_item_agg = items_for_order.groupby("order_id").agg(
        order_item_count=("order_item_id", "count"),
        order_price_total=("price", "sum"),
        order_freight_total=("freight_value", "sum"),
        order_value_total=("item_value", "sum"),
        distinct_categories=("product_category_name_english", "nunique"),
    ).reset_index()
    top_category = (
        items_for_order.groupby(["order_id", "product_category_name_english"])["price"]
        .sum().reset_index()
        .sort_values(["order_id", "price"], ascending=[True, False])
        .drop_duplicates("order_id")[["order_id", "product_category_name_english"]]
        .rename(columns={"product_category_name_english": "top_category"})
    )
    order_item_agg = order_item_agg.merge(top_category, on="order_id", how="left")

    orders_agg = fact_orders.merge(
        dim_customers[["customer_id", "customer_unique_id",
                       "customer_city", "customer_state"]],
        on="customer_id", how="left",
    )
    orders_agg = orders_agg.merge(order_item_agg, on="order_id", how="left")
    orders_agg = orders_agg.merge(review_primary, on="order_id", how="left")
    orders_agg = orders_agg.merge(payment_summary, on="order_id", how="left")
    orders_agg["has_review"] = orders_agg["review_score"].notna()
    orders_agg = _add_temporal(orders_agg)
    orders_agg = _add_delivery_metrics(orders_agg)
    orders_agg = orders_agg.drop(
        columns=["order_approved_at", "order_delivered_carrier_date"],
        errors="ignore",
    )

    # ---- mart_category_daily: one row per (date, category), additive counts -
    cat = items_agg.copy()
    cat["_neg"] = np.where(
        cat["review_score"].notna(), cat["review_score"].isin([1, 2]).astype(float), np.nan
    )
    category_daily = (
        cat.groupby(["order_purchase_date", "product_category_name_english"],
                    as_index=False)
        .agg(
            n_orders=("order_id", "nunique"),
            items_sold=("order_item_id", "count"),
            revenue=("price", "sum"),
            avg_price=("price", "mean"),
            avg_freight=("freight_value", "mean"),
            n_delivered=("is_on_time", lambda s: s.notna().sum()),
            n_on_time=("is_on_time", lambda s: s.fillna(False).sum()),
            n_reviews=("review_score", lambda s: s.notna().sum()),
            sum_review_score=("review_score", "sum"),
            n_1_2_star=("_neg", lambda s: s.dropna().sum()),
            n_customers=("customer_unique_id", "nunique"),
        )
    )

    # ---- mart_state_summary: one row per state, centroid + aggregates -------
    state_geo = (
        dim_geography.groupby("geolocation_state", as_index=False)
        .agg(
            lat=("centroid_lat", "mean"),
            lng=("centroid_lng", "mean"),
            zip_prefix_count=("geolocation_zip_code_prefix", "count"),
        )
        .rename(columns={"geolocation_state": "state"})
    )
    delivered = orders_agg[orders_agg["order_status"] == "delivered"]
    state_orders = (
        delivered.groupby("customer_state", as_index=False)
        .agg(
            n_orders=("order_id", "nunique"),
            total_value=("order_value_total", "sum"),
            avg_delivery_days=("delivery_days", "mean"),
            on_time_rate=("is_on_time", lambda s: s.dropna().mean()),
        )
        .rename(columns={"customer_state": "state"})
    )
    state_summary = state_geo.merge(state_orders, on="state", how="left")
    state_summary["state_name"] = (
        state_summary["state"].map(schemas.BR_STATE_NAMES).fillna(state_summary["state"])
    )
    state_summary = state_summary[
        ["state", "state_name", "lat", "lng", "zip_prefix_count",
         "n_orders", "total_value", "avg_delivery_days", "on_time_rate"]
    ]

    return {
        "mart_order_dashboard": orders_agg,
        "mart_order_items": items_agg,
        "mart_category_daily": category_daily,
        "mart_state_summary": state_summary,
    }


def _build_data_quality(core_dir: Path, mart_dir: Path) -> pd.DataFrame:
    """One row per materialized table with a self-contained PK-uniqueness check."""
    rows = []
    for layer, order, d in [
        ("core", core_schemas.CORE_ORDER, core_dir),
        ("mart", [m for m in core_schemas.MART_ORDER if m != "mart_data_quality"], mart_dir),
    ]:
        for name in order:
            spec = (core_schemas.CORE_SCHEMAS if layer == "core"
                    else core_schemas.MART_SCHEMAS)[name]
            path = d / f"{name}.parquet"
            if not path.exists():
                rows.append([layer, name, spec["grain"], 0,
                             ", ".join(spec["primary_key"]), False, "MISSING"])
                continue
            df = pd.read_parquet(path)
            pk = spec["primary_key"]
            unique = bool(not pk or not df.duplicated(subset=pk).any())
            rows.append([layer, name, spec["grain"], len(df),
                         ", ".join(pk) or "(none)", unique,
                         "OK" if unique else "DUP_PK"])
    return pd.DataFrame(rows, columns=core_schemas.MART_SCHEMAS["mart_data_quality"]["columns"])


def main() -> None:
    core_dir = ROOT / "data" / "processed" / "core"
    mart_dir = ROOT / "data" / "processed" / "marts"

    missing = [t for t in core_schemas.CORE_ORDER
               if not (core_dir / f"{t}.parquet").exists()]
    if missing:
        sys.exit("FATAL: missing core tables: " + ", ".join(missing)
                 + " — run build_core.py first.")

    mart_dir.mkdir(parents=True, exist_ok=True)
    marts = build_marts(core_dir)

    failed = False
    for name in core_schemas.MART_ORDER:
        if name == "mart_data_quality":
            continue  # generated last, after the other marts are on disk
        df = marts[name]
        spec = core_schemas.MART_SCHEMAS[name]
        issues = validation.check_mart_table(name, df)
        if issues:
            failed = True
            print(f"[FAIL] {name}: not written")
            for f in issues:
                print(f"        - {f}")
            continue
        df = df[spec["columns"]]
        df.to_parquet(mart_dir / f"{name}.parquet", index=False)
        print(f"[OK]   {name:22s} {len(df):>9,} rows -> {name}.parquet")

    dq = _build_data_quality(core_dir, mart_dir)
    dq.to_parquet(mart_dir / "mart_data_quality.parquet", index=False)
    print(f"[OK]   {'mart_data_quality':22s} {len(dq):>9,} rows -> mart_data_quality.parquet")

    if failed:
        sys.exit("\nMarts build ABORTED: invalid tables were not written.")

    print("\nAll marts validated and written to data/processed/marts/.")
    print("Run `python preprocessing/validation.py` for the full-layer report.")


if __name__ == "__main__":
    main()
