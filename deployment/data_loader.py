"""deployment/data_loader.py: Cached loaders for the business dashboard CSV tables.

Provides access to the 9 dashboard-ready tables in data/business/dashboard/
as well as cached analytical joins needed for the Streamlit dashboard.
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "business" / "dashboard"


# ----------------------------------------------------------------------
# 1. Base Table Loaders (Direct 1:1 with data/business/dashboard/ CSVs)
# ----------------------------------------------------------------------

@st.cache_data
def load_orders_base() -> pd.DataFrame:
    """Load orders dataset with derived delivery and temporal features."""
    return pd.read_csv(
        DATA_DIR / "olist_orders_dataset.csv",
        parse_dates=[
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    )


@st.cache_data
def load_order_items() -> pd.DataFrame:
    """Load order items dataset with item revenue and shipping limit dates."""
    return pd.read_csv(
        DATA_DIR / "olist_order_items_dataset.csv",
        parse_dates=["shipping_limit_date"],
    )


@st.cache_data
def load_customers() -> pd.DataFrame:
    """Load customers dataset with string zip codes preserving leading zeros."""
    return pd.read_csv(
        DATA_DIR / "olist_customers_dataset.csv",
        dtype={"customer_zip_code_prefix": str},
    )


@st.cache_data
def load_payments() -> pd.DataFrame:
    """Load cleaned order payments dataset."""
    return pd.read_csv(DATA_DIR / "olist_order_payments_dataset.csv")


@st.cache_data
def load_reviews() -> pd.DataFrame:
    """Load order reviews dataset (collapsed to one per order with lowest score)."""
    return pd.read_csv(
        DATA_DIR / "olist_order_reviews_dataset.csv",
        parse_dates=["review_creation_date", "review_answer_timestamp"],
    )


@st.cache_data
def load_products() -> pd.DataFrame:
    """Load product catalog dataset."""
    return pd.read_csv(DATA_DIR / "olist_products_dataset.csv")


@st.cache_data
def load_sellers() -> pd.DataFrame:
    """Load sellers dataset with string zip codes preserving leading zeros."""
    return pd.read_csv(
        DATA_DIR / "olist_sellers_dataset.csv",
        dtype={"seller_zip_code_prefix": str},
    )


@st.cache_data
def load_geolocation() -> pd.DataFrame:
    """Load deduplicated geolocation coordinates."""
    return pd.read_csv(
        DATA_DIR / "olist_geolocation_dataset.csv",
        dtype={"geolocation_zip_code_prefix": str},
    )


@st.cache_data
def load_translation() -> pd.DataFrame:
    """Load product category English translations."""
    return pd.read_csv(
        DATA_DIR / "product_category_name_translation.csv",
        encoding="utf-8-sig",
    )


@st.cache_data
def load_all() -> dict[str, pd.DataFrame]:
    """Load all 9 business dashboard tables into a dictionary."""
    return {
        "orders": load_orders_base(),
        "order_items": load_order_items(),
        "customers": load_customers(),
        "payments": load_payments(),
        "reviews": load_reviews(),
        "products": load_products(),
        "sellers": load_sellers(),
        "geolocation": load_geolocation(),
        "translation": load_translation(),
    }


# ----------------------------------------------------------------------
# 2. Enriched Loaders (Cached joins consumed by Streamlit app & charts)
# ----------------------------------------------------------------------

@st.cache_data
def load_orders() -> pd.DataFrame:
    """Load orders joined with order_value_total, customer info, and review_score."""
    orders = load_orders_base().copy()
    payments = load_payments()
    customers = load_customers()
    reviews = load_reviews()

    # Calculate total payment value per order
    order_pay = (
        payments.groupby("order_id")["payment_value"]
        .sum()
        .rename("order_value_total")
    )
    orders = orders.merge(order_pay, on="order_id", how="left")
    orders["order_value_total"] = orders["order_value_total"].fillna(0.0)

    # Attach customer attributes
    orders = orders.merge(
        customers[["customer_id", "customer_unique_id", "customer_state", "customer_city"]],
        on="customer_id",
        how="left",
    )

    # Attach review score
    orders = orders.merge(
        reviews[["order_id", "review_score"]],
        on="order_id",
        how="left",
    )

    return orders


@st.cache_data
def load_items() -> pd.DataFrame:
    """Load order items joined with product English names, seller, and order metadata."""
    items = load_order_items().copy()
    orders = load_orders()
    products = load_products()
    translation = load_translation()
    sellers = load_sellers()

    # Product category English name
    prod = products.merge(translation, on="product_category_name", how="left")
    prod["product_category_name_english"] = prod["product_category_name_english"].fillna("unknown")

    # Merge items with orders metadata
    items = items.merge(
        orders[[
            "order_id",
            "order_purchase_timestamp",
            "customer_id",
            "customer_unique_id",
            "customer_state",
            "delivery_days",
            "is_on_time",
            "order_status",
            "review_score",
        ]],
        on="order_id",
        how="inner",
    )

    # Merge product details
    items = items.merge(
        prod[["product_id", "product_category_name_english"]],
        on="product_id",
        how="left",
    )

    # Merge seller state
    items = items.merge(
        sellers[["seller_id", "seller_state"]],
        on="seller_id",
        how="left",
    )

    # Ensure item_value exists (item_revenue = price + freight_value)
    items["item_value"] = items["item_revenue"]

    return items


@st.cache_data
def load_geo_state() -> pd.DataFrame:
    """Aggregate state-level orders, revenue, on-time rates, and lat/lng centroids."""
    orders = load_orders()
    geo = load_geolocation()

    # Calculate mean centroids per state
    geo_centroids = geo.groupby("geolocation_state")[["geolocation_lat", "geolocation_lng"]].mean()

    # Aggregate delivered orders by state
    delivered = orders[orders["order_status"] == "delivered"]
    state_agg = (
        delivered.groupby("customer_state")
        .agg(
            n_orders=("order_id", "nunique"),
            total_value=("order_value_total", "sum"),
            on_time_rate=("is_on_time", "mean"),
            avg_delivery_days=("delivery_days", "mean"),
        )
        .reset_index()
    )

    state_summary = state_agg.merge(
        geo_centroids,
        left_on="customer_state",
        right_index=True,
        how="left",
    ).rename(
        columns={
            "customer_state": "state",
            "geolocation_lat": "lat",
            "geolocation_lng": "lng",
        }
    )
    state_summary["state_name"] = state_summary["state"]
    return state_summary


@st.cache_data
def load_category_daily() -> pd.DataFrame:
    """Aggregate daily category sales for time-series trend and heatmap charts."""
    items = load_items().copy()
    items["order_purchase_date"] = items["order_purchase_timestamp"].dt.floor("D")

    cat_daily = (
        items.groupby(["order_purchase_date", "product_category_name_english"], as_index=False)
        .agg(
            orders=("order_id", "nunique"),
            items=("order_item_id", "count"),
            revenue=("item_revenue", "sum"),
        )
    )
    return cat_daily


@st.cache_data
def load_data_quality() -> pd.DataFrame:
    """Row counts and operational quality metrics across business dashboard tables."""
    tables = load_all()
    records = []
    for name, df in tables.items():
        records.append({
            "layer": "business/dashboard",
            "table": f"olist_{name}_dataset.csv" if not name.startswith("product") else "product_category_name_translation.csv",
            "rows": len(df),
            "columns": len(df.columns),
            "status": "OK",
        })
    return pd.DataFrame(records)
