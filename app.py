"""SmartCommerce — Olist Executive Operations Dashboard (Streamlit).

PowerBI-style executive layout (reproduces the teammate's presentation) fed by
the layered business marts: raw -> staging -> core -> marts
(docs/data_architecture.md). Plotly figures keep the charts interactive.
"""
import pandas as pd
import streamlit as st

from dashboard import charts, data_loader, tables, theme

st.set_page_config(page_title="Olist Operations Master Dashboard", layout="wide")

# ---- data ---------------------------------------------------------
orders = data_loader.load_orders()
items = data_loader.load_items()

# ---- control panel (PowerBI style) ---------------------------------
st.sidebar.title("⚙️ Control Panel")
grain = st.sidebar.radio("Time Grain:", options=["Monthly", "Weekly"], index=0)

if grain == "Monthly":
    orders["_period"] = orders["order_purchase_timestamp"].dt.to_period("M").astype(str)
    items["_period"] = items["order_purchase_timestamp"].dt.to_period("M").astype(str)
else:
    oiso = orders["order_purchase_timestamp"].dt.isocalendar()
    orders["_period"] = (oiso["year"].astype(str).str[-2:] + "-"
                         + oiso["week"].astype(str).str.zfill(2))
    iiso = items["order_purchase_timestamp"].dt.isocalendar()
    items["_period"] = (iiso["year"].astype(str).str[-2:] + "-"
                        + iiso["week"].astype(str).str.zfill(2))

valid_periods = sorted(orders["_period"].dropna().unique().tolist())
default_start_idx = max(0, len(valid_periods) - 3)
default_end_idx = len(valid_periods) - 1

col_start, col_end = st.sidebar.columns(2)
with col_start:
    start_period = st.selectbox("Start Period:", valid_periods, index=default_start_idx)
with col_end:
    end_period = st.selectbox("End Period:", valid_periods, index=default_end_idx)

if start_period > end_period:
    st.sidebar.error("⚠️ Start Period must be earlier than or equal to End Period.")
    st.stop()

all_categories = sorted(items["product_category_name_english"].dropna().unique().tolist())
default_cat = "health_beauty" if "health_beauty" in all_categories else all_categories[0]
selected_category = st.sidebar.selectbox(
    "Product Category Deep Dive:", all_categories, index=all_categories.index(default_cat))

st.sidebar.success(f"✅ Data Synced: {grain} ({start_period} to {end_period})")

# ---- filtered windows ----------------------------------------------
periods = [p for p in valid_periods if start_period <= p <= end_period]
orders_f = orders[orders["_period"].isin(periods)]
items_f = items[items["_period"].isin(periods)]

st.title("Olist Executive Operations Dashboard")
st.markdown("---")

# ---- 1. executive KPI performance summary --------------------------
st.header("📈 EXECUTIVE BUSINESS KPI PERFORMANCE SUMMARY")
st.dataframe(tables.kpi_scorecard(orders_f, "_period", periods), width="stretch")
st.markdown("---")

# ---- 2. top 20 product category overview ---------------------------
st.header("🏆 TOP 20 PRODUCT CATEGORY OVERVIEW")
st.dataframe(tables.category_table(items_f), width="stretch")
st.markdown("---")

# ---- 3. category revenue gainers & losers variance -----------------
st.header("📊 CATEGORY REVENUE GAINERS & LOSERS VARIANCE")
s_idx = valid_periods.index(start_period)
e_idx = valid_periods.index(end_period)
period_len = e_idx - s_idx + 1
prev_s_idx = max(0, s_idx - period_len)
prev_e_idx = s_idx - 1
if prev_e_idx >= 0:
    prev_periods = valid_periods[prev_s_idx:prev_e_idx + 1]
    prev_items = items[items["_period"].isin(prev_periods)]
    st.plotly_chart(charts.category_gainers_losers(items_f, prev_items),
                    width="stretch", key="gainers_losers")
else:
    st.info("Insufficient historical baseline data prior to the start period "
            "for a period-over-period comparison.")
st.markdown("---")

# ---- 4. deep-dive category performance -----------------------------
st.header(f"🔍 DEEP DIVE CATEGORY PERFORMANCE: [{selected_category.upper()}]")
cat_df = items_f[items_f["product_category_name_english"] == selected_category]
trend = (cat_df.groupby("_period", as_index=False)
         .agg(Revenue=("price", "sum"), Orders=("order_id", "nunique")))
col = st.columns(2)
col[0].plotly_chart(charts.trend_line(trend, "_period", "Revenue", "Revenue Trend"),
                    width="stretch", key="dd_rev")
col[1].plotly_chart(charts.trend_bar(trend, "_period", "Orders", "Order Volume"),
                    width="stretch", key="dd_ord")
col2 = st.columns(2)
col2[0].plotly_chart(charts.review_stacked(cat_df, "_period",
                                           "Review Score Distribution (%)"),
                     width="stretch", key="dd_review")
col2[1].plotly_chart(charts.delivery_boxplot(cat_df, "_period",
                                             "Delivery Days (capped 0–100)"),
                     width="stretch", key="dd_delivery")
st.markdown("---")


def _geo_profile(df: pd.DataFrame, state_col: str, title_prefix: str, color: str):
    top = (df.groupby(state_col)["price"].sum()
           .sort_values(ascending=False).head(10).index.tolist())
    sub = df[df[state_col].isin(top)]
    col = st.columns(3)
    col[0].plotly_chart(charts.revenue_bar(sub, state_col, f"{title_prefix} Revenue",
                                           color=color, order=top),
                        width="stretch")
    col[1].plotly_chart(charts.review_stacked(sub, state_col,
                                              f"{title_prefix} Review Ratings (%)",
                                              order=top, show_legend=False),
                        width="stretch")
    col[2].plotly_chart(charts.delivery_boxplot(sub, state_col,
                                                f"{title_prefix} Delivery Days "
                                                "(capped 0–100)",
                                                order=top, color=color),
                        width="stretch")


# ---- 5 & 6. geographic profile (buyer & seller) --------------------
st.header("🗺️ BUYER GEOGRAPHIC PROFILE ANALYSIS")
_geo_profile(items_f, "customer_state", "Buyer State", theme.BUYER_BLUE)
st.markdown("---")

st.header("🏬 SELLER GEOGRAPHIC PROFILE ANALYSIS")
_geo_profile(items_f, "seller_state", "Seller State", theme.SELLER_ORANGE)
st.markdown("---")

# ---- 7. national state performance (mart_state_summary, delivered orders) --
st.header("🗺️ NATIONAL STATE PERFORMANCE (all 27 states)")
st.caption("Aggregated over delivered orders — full history, not period-filtered.")
state_summary = data_loader.load_geo_state()
st.plotly_chart(charts.state_map(state_summary), width="stretch", key="state_map")
col = st.columns(2)
col[0].plotly_chart(charts.state_on_time_bar(state_summary), width="stretch", key="state_ontime")
col[1].plotly_chart(charts.state_on_time_scatter(state_summary), width="stretch", key="state_scatter")
st.markdown("---")

# ---- 8. category time trends (mart_category_daily, daily grain) ----
st.header("📅 CATEGORY TIME TRENDS")
st.caption("Full-history seasonality view (daily grain), not affected by the period filter.")
cat_daily = data_loader.load_category_daily()
col = st.columns(2)
col[0].plotly_chart(charts.category_multi_line(cat_daily, "revenue"), width="stretch", key="cat_multi")
col[1].plotly_chart(charts.category_heatmap(cat_daily, "revenue"), width="stretch", key="cat_heat")
st.markdown("---")

# ---- 9. data quality (collapsed pipeline-health panel) ----
with st.expander("🔧 Data Quality (pipeline health)", expanded=False):
    dq = data_loader.load_data_quality()
    st.dataframe(dq, width="stretch", hide_index=True)
    st.plotly_chart(charts.data_quality_bar(dq), width="stretch", key="dq_bar")
