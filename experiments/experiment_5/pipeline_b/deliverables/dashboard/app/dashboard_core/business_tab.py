"""Tab 1: Business overview (plan revision 2, D1-D2).

Descriptive view of all orders, not model results. Every Phase 1 section is ported from
`deployment/app.py` (commit f31998e) with its logic unchanged; that file is not edited.
Changes from Phase 1: benchmarks live in the session (Phase 1 wrote them to a config
file), incomplete months stay excluded (plan section 2), and two rating distributions are
added (customer and seller), each order counted once at its lowest valid score, the rule
of the report's detractor label.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

from dashboard_core.data import load_business_complete_months

# Ported from deployment/app.py@f31998e: DEFAULT_CONFIG, STAR_GRADIENT, RED_CELL_STYLE.
DEFAULTS = {
    "lookback": 3,
    "default_category": "health_beauty",
    "min_orders": 100,
    "delivery_days_y_max": 100,
    "top_n_gainers_losers": 5,
    "top_n_buyers": 100,
    "top_n_sellers": 100,
    "total_revenue": 950000.0,
    "total_orders": 6500.0,
    "average_order_value": 130.0,
    "price_ratio": 0.90,
    "freight_ratio": 0.10,
    "repeat_rate": 0.009,
    "ontime_rate": 0.90,
    "delivery_days": 8.8,
    "review_score": 4.0,
    "low_rating": 0.10,
}
STAR_GRADIENT = ["#ef4444", "#f97316", "#eab308", "#84cc16", "#22c55e"]
RED_CELL_STYLE = "background-color: #fecaca; color: #991b1b; font-weight: bold;"
MIN_SELLER_ORDERS = 10
LOW_SELLER_SCORE = 3.5


def format_business_num(val, is_currency=False, is_pct=False):  # deployment/app.py@f31998e
    if pd.isna(val) or val is None:
        return "-"
    prefix = "R$ " if is_currency else ""
    if is_pct:
        return f"{prefix}{val * 100:.3g}%"
    abs_v = abs(val)
    if abs_v >= 1000:
        return f"{prefix}{val:,.0f}"
    if 1 <= abs_v < 1000:
        return f"{prefix}{val:.2f}"
    return f"{prefix}{val:.3g}"


def _controls(categories: list[str]) -> dict:
    """Phase 1's benchmark panel; values are kept in the session, never written to a file."""
    with st.expander("Benchmarks and parameters (Phase 1 defaults; changes last for this session)"):
        c1, c2, c3 = st.columns(3)
        cfg = {
            "lookback": c1.slider("Lookback periods", 1, 12, DEFAULTS["lookback"], key="biz_lookback"),
            "min_orders": c1.number_input("Min orders per category (SLA)", value=DEFAULTS["min_orders"], key="biz_min_orders"),
            "delivery_days_y_max": c1.slider("Delivery days max y-axis", 20, 300, DEFAULTS["delivery_days_y_max"], key="biz_ymax"),
            "top_n_gainers_losers": c1.slider("Top N gainers / losers", 3, 15, DEFAULTS["top_n_gainers_losers"], key="biz_topn"),
            "total_revenue": c2.number_input("Target total revenue (R$, per month)", value=DEFAULTS["total_revenue"], key="biz_rev"),
            "total_orders": c2.number_input("Target total orders (per month)", value=DEFAULTS["total_orders"], key="biz_orders"),
            "average_order_value": c2.number_input("Target AOV (R$)", value=DEFAULTS["average_order_value"], key="biz_aov"),
            "price_ratio": c2.slider("Target price ratio (%)", 50, 100, int(DEFAULTS["price_ratio"] * 100), key="biz_price") / 100,
            "freight_ratio": c2.slider("Max freight ratio (%)", 0, 50, int(DEFAULTS["freight_ratio"] * 100), key="biz_freight") / 100,
            "repeat_rate": c3.slider("Min repeat rate (‰)", 1, 100, int(DEFAULTS["repeat_rate"] * 1000), key="biz_repeat") / 1000,
            "ontime_rate": c3.slider("Min on-time delivery rate (%)", 50, 100, int(DEFAULTS["ontime_rate"] * 100), key="biz_ontime") / 100,
            "delivery_days": c3.number_input("Max delivery days", value=DEFAULTS["delivery_days"], key="biz_days"),
            "review_score": c3.slider("Min average review score", 1.0, 5.0, DEFAULTS["review_score"], 0.1, key="biz_review"),
            "low_rating": c3.slider("Max 1 and 2 star share (%)", 1, 30, int(DEFAULTS["low_rating"] * 100), key="biz_low") / 100,
        }
    default = DEFAULTS["default_category"]
    cfg["category"] = default if default in categories else categories[0]
    return cfg


def _window(frame: pd.DataFrame, cfg: dict) -> tuple[pd.DataFrame, str, list[str], list[str]]:
    grain = st.radio("Date grain", ["Monthly", "Weekly"], horizontal=True, key="biz_grain")
    time_col = "year_month" if grain == "Monthly" else "year_week"
    frame = frame.copy()
    if time_col == "year_week":
        frame["year_week"] = frame["order_purchase_timestamp"].dt.strftime("%Y-%W")
    available = sorted(frame[time_col].dropna().unique())
    start = max(0, len(available) - int(cfg["lookback"]))
    first, last = st.select_slider(
        "Active period window", options=available, value=(available[start], available[-1]), key=f"biz_window_{time_col}"
    )
    selected = [p for p in available if first <= p <= last]
    st.session_state["biz_scale"] = 7.0 / 30.0 if grain == "Weekly" else 1.0
    st.session_state["biz_weekly"] = grain == "Weekly"
    return frame, time_col, available, selected


def calculate_kpi_matrix(df_data: pd.DataFrame, time_col: str) -> pd.DataFrame:  # deployment/app.py@f31998e
    grouped = df_data.groupby(time_col)
    res = pd.DataFrame()
    order_level = df_data.drop_duplicates("order_id")
    order_grouped = order_level.groupby(time_col)
    res["Total Revenue (R$)"] = grouped["price"].sum()
    res["Total Orders"] = order_grouped["order_id"].nunique()
    res["Average Order Value (R$)"] = res["Total Revenue (R$)"] / res["Total Orders"]
    tot_price = grouped["price"].sum()
    tot_freight = grouped["freight_value"].sum()
    tot_val = tot_price + tot_freight
    res["Price to Order Value (%)"] = tot_price / tot_val
    res["Freight to Order Value (%)"] = tot_freight / tot_val
    cust_orders = df_data.groupby([time_col, "customer_unique_id"])["order_id"].nunique()
    repeat_custs = cust_orders[cust_orders > 1].groupby(time_col).size()
    total_custs = df_data.groupby(time_col)["customer_unique_id"].nunique()
    res["Customer Repeat Rate"] = (repeat_custs / total_custs).fillna(0)
    res["On-Time Delivery Rate"] = order_grouped["is_on_time"].mean()
    res["Average Delivery Days"] = order_grouped["delivery_days"].mean()
    res["Average Review Score"] = grouped["review_score"].mean()
    res["% Rating 1 & 2"] = grouped["review_score"].apply(
        lambda s: (s.isin([1, 2])).sum() / len(s) if len(s) > 0 else 0
    )
    return res.T


def _benchmarks(cfg: dict) -> dict:
    sf = st.session_state.get("biz_scale", 1.0)
    return {
        "Total Revenue (R$)": cfg["total_revenue"] * sf,
        "Total Orders": cfg["total_orders"] * sf,
        "Average Order Value (R$)": cfg["average_order_value"],
        "Price to Order Value (%)": cfg["price_ratio"],
        "Freight to Order Value (%)": cfg["freight_ratio"],
        "Customer Repeat Rate": "N/A" if st.session_state.get("biz_weekly") else cfg["repeat_rate"],
        "On-Time Delivery Rate": cfg["ontime_rate"],
        "Average Delivery Days": cfg["delivery_days"],
        "Average Review Score": cfg["review_score"],
        "% Rating 1 & 2": cfg["low_rating"],
    }


def is_non_compliant(metric, val, target):  # deployment/app.py@f31998e
    if target == "N/A" or pd.isna(val) or target is None:
        return False
    if metric in [
        "Total Revenue (R$)", "Total Orders", "Average Order Value (R$)", "Price to Order Value (%)",
        "Customer Repeat Rate", "On-Time Delivery Rate", "Average Review Score",
    ]:
        return val < target
    if metric in ["Freight to Order Value (%)", "Average Delivery Days", "% Rating 1 & 2"]:
        return val > target
    return False


def _styled(table: pd.DataFrame, targets: dict, metrics_on: str) -> "pd.io.formats.style.Styler":
    """Format cells as Phase 1 did and mark those that miss their benchmark.

    metrics_on is "index" when each row is a metric (KPI matrix) and "columns" when each
    column is one (category tables).
    """
    formatted = pd.DataFrame(index=table.index, columns=table.columns, dtype=object)
    styles = pd.DataFrame("", index=table.index, columns=table.columns)
    for row in table.index:
        for col in table.columns:
            metric = row if metrics_on == "index" else col
            val = table.loc[row, col]
            if isinstance(val, str):
                formatted.loc[row, col] = val
                continue
            is_curr = "Revenue" in metric or "Value" in metric
            is_pct = ("%" in metric or "Rate" in metric or "Ratio" in metric) and "Value" not in metric
            formatted.loc[row, col] = format_business_num(val, is_currency=is_curr, is_pct=is_pct)
            if col != "Benchmark" and is_non_compliant(metric, val, targets.get(metric)):
                styles.loc[row, col] = RED_CELL_STYLE
    return formatted.style.apply(lambda _: styles, axis=None)


def _kpi_section(df: pd.DataFrame, time_col: str, cfg: dict) -> pd.DataFrame:
    st.subheader("KPI matrix")
    kpi = calculate_kpi_matrix(df, time_col)
    bms = _benchmarks(cfg)
    shown = kpi.copy()
    shown["Benchmark"] = [bms[m] for m in shown.index]
    st.dataframe(_styled(shown, bms, "index"), width="stretch")
    st.caption("Red: misses its benchmark. Revenue and order targets are per month, scaled for weeks.")

    st.subheader("KPI diagnostic stack")
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.heatmap(kpi.T.astype(float).corr(numeric_only=True), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    ax.set_title("KPI correlations across the selected periods", fontweight="bold")
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("Period-over-period growth")
    metrics = ["Total Revenue (R$)", "Total Orders", "On-Time Delivery Rate", "Average Review Score"]
    pop = kpi.loc[metrics].T.astype(float).pct_change().dropna(how="all")
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for idx, metric in enumerate(metrics):
        ax = axes[idx // 2, idx % 2]
        vals = pop[metric].dropna() if metric in pop else pd.Series(dtype=float)
        ax.bar(range(len(vals)), vals * 100, color=["#22c55e" if v >= 0 else "#ef4444" for v in vals], width=0.4)
        ax.set_xticks(range(len(vals)))
        ax.set_xticklabels(vals.index, rotation=30, ha="right", fontsize=9)
        for x, v in enumerate(vals):
            ax.text(x, v * 50, f"{'▲' if v >= 0 else '▼'} {abs(v) * 100:.1f}%", ha="center", va="center",
                    fontsize=8, fontweight="bold", color="white")
        ax.set_title(f"Growth: {metric}", fontweight="bold", fontsize=10)
        ax.set_ylabel("Change (%)")
        ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    return kpi


def build_category_overview(df_data: pd.DataFrame) -> pd.DataFrame:  # deployment/app.py@f31998e
    cat_grouped = df_data.groupby("product_category_name_english")
    order_cat = df_data.drop_duplicates(["order_id", "product_category_name_english"]).groupby(
        "product_category_name_english"
    )
    rev = cat_grouped["price"].sum()
    orders = order_cat["order_id"].nunique()
    tot_val = cat_grouped["price"].sum() + cat_grouped["freight_value"].sum()
    cust_orders = df_data.groupby(["product_category_name_english", "customer_unique_id"])["order_id"].nunique()
    repeat_custs = cust_orders[cust_orders > 1].groupby("product_category_name_english").size()
    return pd.DataFrame(
        {
            "Total Revenue (R$)": rev,
            "Total Orders": orders,
            "Average Order Value (R$)": rev / orders,
            "Price to Order Value (%)": cat_grouped["price"].sum() / tot_val,
            "Freight to Order Value (%)": cat_grouped["freight_value"].sum() / tot_val,
            "Customer Repeat Rate": (repeat_custs / cat_grouped["customer_unique_id"].nunique()).fillna(0),
            "On-Time Delivery Rate": order_cat["is_on_time"].mean(),
            "Average Delivery Days": order_cat["delivery_days"].mean(),
            "Average Review Score": cat_grouped["review_score"].mean(),
            "% Rating 1 & 2": cat_grouped["review_score"].apply(
                lambda s: (s.isin([1, 2])).sum() / len(s) if len(s) > 0 else 0
            ),
        }
    )


def _category_section(df: pd.DataFrame, cfg: dict) -> None:
    st.subheader("Category overview")
    summary = build_category_overview(df)
    # Phase 1's fixed category targets; revenue and order targets apply to the whole business only.
    targets = {
        "Price to Order Value (%)": cfg["price_ratio"], "Freight to Order Value (%)": cfg["freight_ratio"],
        "Customer Repeat Rate": cfg["repeat_rate"], "On-Time Delivery Rate": cfg["ontime_rate"],
        "Average Delivery Days": cfg["delivery_days"], "Average Review Score": cfg["review_score"],
        "% Rating 1 & 2": cfg["low_rating"],
    }
    st.markdown("**Top 10 categories by revenue**")
    st.dataframe(_styled(summary.nlargest(10, "Total Revenue (R$)"), targets, "columns"), width="stretch")
    st.markdown("**Bottom 10 categories by revenue**")
    st.dataframe(_styled(summary.nsmallest(10, "Total Revenue (R$)"), targets, "columns"), width="stretch")


def _variance_section(frame: pd.DataFrame, df: pd.DataFrame, time_col: str, available: list[str],
                      selected: list[str], cfg: dict) -> None:
    st.subheader("Revenue variance")
    start = available.index(selected[0])
    prior = available[max(0, start - len(selected)):start]
    if not prior:
        st.info("Not enough earlier periods to compare with an equal prior window.")
        return
    current = df.groupby("product_category_name_english")["price"].sum()
    previous = frame[frame[time_col].isin(prior)].groupby("product_category_name_english")["price"].sum()
    var = pd.DataFrame({"Current": current, "Prior": previous}).fillna(0)
    var["Delta"] = var["Current"] - var["Prior"]
    n = int(cfg["top_n_gainers_losers"])
    combined = pd.concat([var.nlargest(n, "Delta"), var.nsmallest(n, "Delta")]).drop_duplicates()
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(combined.index, combined["Delta"], color=["#22c55e" if d >= 0 else "#ef4444" for d in combined["Delta"]])
    for bar, delta in zip(bars, combined["Delta"]):
        ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, f" {'▲' if delta >= 0 else '▼'} R$ {abs(delta):,.0f}",
                va="center", ha="left" if delta >= 0 else "right", color="#15803d" if delta >= 0 else "#991b1b",
                fontweight="bold")
    ax.set_title(f"Top {n} revenue gainers and losers against the prior equal window", fontweight="bold")
    ax.set_xlabel("Revenue change (R$)")
    ax.axvline(0, color="black", linewidth=0.8)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def _star_shares(orders: pd.DataFrame, by: str | None) -> pd.DataFrame:
    counts = (orders.groupby([by, "score"]).size().unstack(fill_value=0) if by
              else orders["score"].value_counts().to_frame().T)
    counts = counts.reindex(columns=[1, 2, 3, 4, 5], fill_value=0)
    return counts.div(counts.sum(axis=1), axis=0).fillna(0)


def _stacked_stars(ax, shares: pd.DataFrame, title: str) -> None:
    bottoms = np.zeros(len(shares))
    for idx, star in enumerate([1, 2, 3, 4, 5]):
        ax.bar([str(i) for i in shares.index], shares[star], bottom=bottoms, label=f"{star}★", color=STAR_GRADIENT[idx])
        bottoms += shares[star].to_numpy()
    ax.set_title(title, fontweight="bold")
    ax.set_ylabel("Share of orders")
    ax.tick_params(axis="x", rotation=45)
    ax.legend(loc="upper right", fontsize=8)


def _deep_dive_section(df: pd.DataFrame, time_col: str, cfg: dict) -> None:
    st.subheader("Category deep dive")
    categories = sorted(df["product_category_name_english"].dropna().unique())
    category = st.selectbox("Category", categories,
                            index=categories.index(cfg["category"]) if cfg["category"] in categories else 0,
                            key="biz_deep_category")
    deep = df[df["product_category_name_english"] == category]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    trend = deep.groupby(time_col)["price"].sum()
    axes[0].plot(trend.index, trend.values, marker="o", color="#2563eb", linewidth=2)
    axes[0].set_title(f"Revenue: {category}", fontweight="bold")
    axes[0].set_ylabel("Revenue (R$)")
    axes[0].tick_params(axis="x", rotation=45)
    _stacked_stars(axes[1], _star_shares(_order_scores(deep, time_col), time_col), "Review-score mix (each order once)")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    volume = deep.drop_duplicates("order_id").groupby(time_col)["order_id"].nunique()
    axes[0].bar(volume.index, volume.values, color="#3b82f6")
    axes[0].set_title(f"Orders: {category}", fontweight="bold")
    axes[0].tick_params(axis="x", rotation=45)
    delivered = deep.drop_duplicates("order_id").dropna(subset=["delivery_days"])
    sns.boxplot(data=delivered, x=time_col, y="delivery_days", ax=axes[1], color="#93c5fd")
    axes[1].set_ylim(0, cfg["delivery_days_y_max"])
    axes[1].set_title(f"Delivery days (y-axis capped at {cfg['delivery_days_y_max']})", fontweight="bold")
    axes[1].tick_params(axis="x", rotation=45)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def _sla_section(df: pd.DataFrame, cfg: dict) -> None:
    st.subheader("Order-level SLA by category")
    counts = df.groupby("product_category_name_english")["order_id"].nunique()
    valid = counts[counts >= cfg["min_orders"]].index
    dedup = df[df["product_category_name_english"].isin(valid)].drop_duplicates(["order_id", "product_category_name_english"])
    rows = []
    for category, group in dedup.groupby("product_category_name_english"):
        days = group["delivery_days"].dropna()
        rows.append({
            "Category": category,
            "Total Orders": group["order_id"].nunique(),
            "On-Time Rate": group["is_on_time"].mean(),
            "Avg Review Score": df.loc[df["product_category_name_english"] == category, "review_score"].mean(),
            "P5 Delivery Days": days.quantile(0.05) if len(days) else np.nan,
            "Mean Delivery Days": days.mean() if len(days) else np.nan,
            "P95 Delivery Days": days.quantile(0.95) if len(days) else np.nan,
        })
    sla = pd.DataFrame(rows)
    if sla.empty:
        st.info("No category reaches the minimum order count in this window.")
        return
    worst = set(sla.nsmallest(5, "On-Time Rate")["Category"])
    shown = sla.copy()
    shown["Total Orders"] = shown["Total Orders"].map(lambda x: f"{x:,.0f}")
    shown["On-Time Rate"] = shown["On-Time Rate"].map(lambda x: f"{x * 100:.2f}%")
    for column in ("Avg Review Score",):
        shown[column] = shown[column].map(lambda x: f"{x:.2f}")
    for column in ("P5 Delivery Days", "Mean Delivery Days", "P95 Delivery Days"):
        shown[column] = shown[column].map(lambda x: f"{x:.1f}")
    st.dataframe(
        shown.style.apply(lambda r: [RED_CELL_STYLE if r["Category"] in worst else ""] * len(r), axis=1),
        width="stretch", hide_index=True,
    )
    st.caption(f"Categories with at least {cfg['min_orders']} orders; red: the 5 lowest on-time rates.")


def _profiles_section(df: pd.DataFrame, time_col: str, cfg: dict) -> None:
    st.subheader("Buyer and seller profiles")
    left, right = st.columns(2)
    for column, key, title, color in ((left, "customer_state", "Top 10 buyer states by revenue", "#2563eb"),
                                      (right, "seller_state", "Top 10 seller states by revenue", "#3b82f6")):
        with column:
            values = df.groupby(key)["price"].sum().nlargest(10).sort_values()
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.barh(values.index, values.values, color=color)
            ax.set_title(title, fontweight="bold")
            ax.set_xlabel("Revenue (R$)")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

    st.markdown("**Cohort growth over time**")
    left, right = st.columns(2)
    for column, key, n, label in ((left, "customer_unique_id", DEFAULTS["top_n_buyers"], "buyers"),
                                  (right, "seller_id", DEFAULTS["top_n_sellers"], "sellers")):
        top = df.groupby(key)["price"].sum().nlargest(n).index
        growth = df[df[key].isin(top)].groupby(time_col)["price"].sum().pct_change().dropna()
        with column:
            fig, ax = plt.subplots(figsize=(6, 4))
            ax.bar(range(len(growth)), growth * 100, color=["#22c55e" if v >= 0 else "#ef4444" for v in growth], width=0.4)
            ax.set_xticks(range(len(growth)))
            ax.set_xticklabels(growth.index, rotation=45, ha="right")
            ax.set_title(f"Top {n} {label}: revenue growth", fontweight="bold")
            ax.set_ylabel("Growth (%)")
            ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)


def _order_scores(df: pd.DataFrame, time_col: str | None = None) -> pd.DataFrame:
    """One row per order: its lowest valid review score (1-5), the detractor label's rule."""
    valid = df[df["review_score"].between(1, 5)]
    keys = ["order_id"] + ([time_col] if time_col else [])
    orders = valid.groupby(keys, as_index=False).agg(score=("review_score", "min"), seller_id=("seller_id", "first"))
    orders["score"] = orders["score"].astype(int)
    return orders


def _seller_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Each seller's average order score: an order with several sellers counts for each of them."""
    valid = df[df["review_score"].between(1, 5)]
    per_order = valid.groupby(["order_id", "seller_id"], as_index=False)["review_score"].min()
    per_order = per_order.merge(
        valid.groupby("order_id", as_index=False)["review_score"].min().rename(columns={"review_score": "score"}),
        on="order_id",
    )
    return per_order.groupby("seller_id").agg(orders=("order_id", "nunique"), mean_score=("score", "mean")).reset_index()


def _ratings_section(df: pd.DataFrame, time_col: str) -> None:
    st.subheader("Customer rating distribution")
    orders = _order_scores(df, time_col)
    overall = _star_shares(orders, None)
    cols = st.columns(5)
    for idx, star in enumerate([1, 2, 3, 4, 5]):
        cols[idx].metric(f"{star}★ orders", f"{overall[star].iloc[0]:.1%}")
    fig, ax = plt.subplots(figsize=(12, 4))
    _stacked_stars(ax, _star_shares(orders, time_col), "Share of orders by star, per period")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.caption(f"{len(orders):,} reviewed orders; each order counted once at its lowest valid score "
               "(the report's detractor label uses the same rule: 1 or 2 stars).")

    st.subheader("Seller rating distribution")
    sellers = _seller_scores(df)
    rated = sellers[sellers["orders"] >= MIN_SELLER_ORDERS]
    if rated.empty:
        st.info(f"No seller has {MIN_SELLER_ORDERS} reviewed orders in this window; widen the window.")
        return
    low = (rated["mean_score"] < LOW_SELLER_SCORE).mean()
    cols = st.columns(3)
    cols[0].metric("Sellers shown", f"{len(rated):,}")
    cols[1].metric("Median seller score", f"{rated['mean_score'].median():.2f}")
    cols[2].metric(f"Sellers below {LOW_SELLER_SCORE}", f"{low:.1%}")
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.hist(rated["mean_score"], bins=np.arange(1, 5.01, 0.1), color="#3b82f6", edgecolor="white")
    ax.axvline(LOW_SELLER_SCORE, color="#ef4444", linestyle="--", linewidth=1.2, label=f"{LOW_SELLER_SCORE}")
    ax.set_xlabel("Seller's average order score")
    ax.set_ylabel("Sellers")
    ax.set_title(f"Sellers with at least {MIN_SELLER_ORDERS} reviewed orders", fontweight="bold")
    ax.legend(fontsize=8)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.dataframe(rated.nsmallest(10, "mean_score").rename(columns={"mean_score": "average score"}),
                 width="stretch", hide_index=True)
    st.caption("The 10 lowest-rated sellers in this window.")


def render() -> None:
    st.header("Business overview")
    st.info("Descriptive view of all orders; not model results")
    frame = load_business_complete_months()
    if frame.empty:
        st.warning("No complete months are available from March 2017.")
        return
    categories = sorted(frame["product_category_name_english"].dropna().unique())
    cfg = _controls(categories)
    frame, time_col, available, selected = _window(frame, cfg)
    df = frame[frame[time_col].isin(selected)].copy()

    _kpi_section(df, time_col, cfg)
    _category_section(df, cfg)
    _variance_section(frame, df, time_col, available, selected, cfg)
    _deep_dive_section(df, time_col, cfg)
    _sla_section(df, cfg)
    _profiles_section(df, time_col, cfg)
    _ratings_section(df, time_col)
