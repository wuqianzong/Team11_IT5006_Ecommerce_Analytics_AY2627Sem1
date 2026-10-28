"""Business overview tab.

The order-level helpers are adapted from deployment/app.py at commit
86538e0a7dfff8dcd87d4be921591312660fcc71. They preserve the Phase 1
descriptive scope and formulas while making the page fit the new tab structure.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard_core import paths
from dashboard_core.charts import bar_chart, line_chart
from dashboard_core.data import load_business_complete_months


def _order_level(frame: pd.DataFrame) -> pd.DataFrame:
    """Adapted from deployment/app.py: order-level views use one row per order."""
    columns = [
        "order_id",
        "order_purchase_timestamp",
        "year_month",
        "customer_unique_id",
        "customer_state",
        "seller_state",
        "delivery_days",
        "is_on_time",
        "review_score",
    ]
    available = [column for column in columns if column in frame.columns]
    return frame[available].drop_duplicates("order_id").copy()


def _kpis(frame: pd.DataFrame) -> dict[str, float | int]:
    """Adapted from deployment/app.py calculate_kpi_matrix."""
    orders = _order_level(frame)
    delivered = orders.dropna(subset=["is_on_time"])
    reviews = orders.dropna(subset=["review_score"])
    total_revenue = float(frame["price"].sum() + frame["freight_value"].sum())
    total_orders = int(orders["order_id"].nunique())
    customers = orders.groupby("customer_unique_id")["order_id"].nunique()
    return {
        "Revenue": total_revenue,
        "Orders": total_orders,
        "Average order value": total_revenue / max(total_orders, 1),
        "Repeat-customer rate": float((customers > 1).mean()) if len(customers) else 0.0,
        "On-time delivery": float(delivered["is_on_time"].astype(bool).mean())
        if len(delivered)
        else 0.0,
        "Average delivery days": float(delivered["delivery_days"].mean())
        if len(delivered)
        else 0.0,
        "Average rating": float(reviews["review_score"].mean()) if len(reviews) else 0.0,
        "Rating 1–2 share": float(reviews["review_score"].isin([1, 2]).mean())
        if len(reviews)
        else 0.0,
    }


def _category_overview(frame: pd.DataFrame) -> pd.DataFrame:
    """Adapted from deployment/app.py build_category_overview."""
    data = frame.dropna(subset=["product_category_name_english"]).copy()
    grouped = data.groupby("product_category_name_english")
    order_grouped = data.drop_duplicates(["order_id", "product_category_name_english"]).groupby(
        "product_category_name_english"
    )
    result = pd.DataFrame(
        {
            "Revenue": grouped["price"].sum() + grouped["freight_value"].sum(),
            "Orders": order_grouped["order_id"].nunique(),
            "On-time rate": order_grouped["is_on_time"].mean(),
            "Average delivery days": order_grouped["delivery_days"].mean(),
            "Average rating": grouped["review_score"].mean(),
            "Rating 1–2 share": grouped["review_score"].apply(
                lambda values: values.isin([1, 2]).mean() if len(values) else 0.0
            ),
        }
    )
    result["Average order value"] = result["Revenue"] / result["Orders"].replace(0, 1)
    return result


def render() -> None:
    st.header("Business overview")
    st.info("Descriptive view of all orders; not model results")

    frame = load_business_complete_months()
    if frame.empty:
        st.warning("No complete months are available from March 2017.")
        return

    st.subheader("KPI matrix")
    kpis = _kpis(frame)
    first = st.columns(4)
    first[0].metric("Total revenue", f"R$ {kpis['Revenue']:,.0f}")
    first[1].metric("Total orders", f"{kpis['Orders']:,}")
    first[2].metric("Average order value", f"R$ {kpis['Average order value']:,.2f}")
    first[3].metric("Repeat-customer rate", f"{kpis['Repeat-customer rate']:.1%}")
    second = st.columns(4)
    second[0].metric("On-time delivery", f"{kpis['On-time delivery']:.1%}")
    second[1].metric("Average delivery days", f"{kpis['Average delivery days']:.2f}")
    second[2].metric("Average rating", f"{kpis['Average rating']:.2f}")
    second[3].metric("Rating 1–2 share", f"{kpis['Rating 1–2 share']:.1%}")

    st.subheader("Category overview")
    category = _category_overview(frame)
    top_categories = category.nlargest(10, "Revenue").reset_index()
    bottom_categories = category.nsmallest(10, "Revenue").reset_index()
    left, right = st.columns(2)
    with left:
        st.markdown("**Top 10 categories by revenue**")
        st.dataframe(top_categories, width="stretch", hide_index=True)
    with right:
        st.markdown("**Bottom 10 categories by revenue**")
        st.dataframe(bottom_categories, width="stretch", hide_index=True)

    st.subheader("Revenue variance")
    monthly_revenue = (
        frame.groupby("year_month")
        .agg(revenue=("price", "sum"))
        .reset_index()
        .assign(change=lambda data: data["revenue"].pct_change())
    )
    line_chart(monthly_revenue, "year_month", "revenue", "Revenue by month", "Revenue (R$)")
    st.dataframe(monthly_revenue, width="stretch", hide_index=True)

    st.subheader("Delivery SLA")
    sla = (
        frame.dropna(subset=["delivery_days"])
        .drop_duplicates("order_id")
        .groupby("customer_state")
        .agg(
            orders=("order_id", "nunique"),
            on_time_rate=("is_on_time", "mean"),
            mean_delivery_days=("delivery_days", "mean"),
            p95_delivery_days=("delivery_days", lambda values: values.quantile(0.95)),
        )
        .sort_values("orders", ascending=False)
        .head(15)
        .reset_index()
    )
    st.dataframe(sla, width="stretch", hide_index=True)

    st.subheader("Buyer and seller profiles")
    buyer_profiles = (
        frame.groupby("customer_state")["price"].sum().nlargest(10).sort_values().reset_index()
    )
    seller_profiles = (
        frame.groupby("seller_state")["price"].sum().nlargest(10).sort_values().reset_index()
    )
    left, right = st.columns(2)
    with left:
        bar_chart(
            buyer_profiles,
            "customer_state",
            "price",
            "Top buyer states by revenue",
            "Revenue (R$)",
        )
    with right:
        bar_chart(
            seller_profiles,
            "seller_state",
            "price",
            "Top seller states by revenue",
            "Revenue (R$)",
            "#16a34a",
        )

