"""Executive-style tables for the SmartCommerce dashboard.

Reproduces the teammate's "PowerBI executive" presentation: a metric x period
KPI table with a data-driven benchmark column and red highlighting on misses,
plus a top-category detail table. Returns pandas Styler / DataFrame — no
Streamlit calls — so rendering stays in app.py.
"""
from __future__ import annotations

import pandas as pd

# Metrics where a *lower* value is better (everything else: higher is better).
LOWER_IS_BETTER = {"Avg Delivery Days"}

_METRICS = [
    "Total Orders",
    "Total Revenue (R$)",
    "Average Order Value (R$)",
    "Customer Repeat Rate",
    "On-Time Delivery Rate",
    "Avg Delivery Days",
    "Avg Review Score",
]


def _fmt(metric: str, v) -> str:
    if pd.isna(v):
        return "–"
    if metric == "Total Orders":
        return f"{v:,.0f}"
    if metric in ("Total Revenue (R$)", "Average Order Value (R$)"):
        return f"R$ {v:,.0f}"
    if metric in ("Customer Repeat Rate", "On-Time Delivery Rate"):
        return f"{v:.1%}"
    return f"{v:.2f}"


def _period_metrics(orders: pd.DataFrame, period_col: str,
                    periods: list[str]) -> tuple[pd.DataFrame, pd.Series]:
    """Return (metric x period numeric DataFrame, benchmark Series).

    Benchmark = the period average (data-driven), unlike the teammate's
    hardcoded thresholds — so the scorecard adapts to the selected window.
    """
    d = orders.copy()
    cols = {m: [] for m in _METRICS}
    for p in periods:
        sub = d[d[period_col] == p]
        n = sub["order_id"].nunique()
        rev = sub["order_value_total"].sum()
        aov = rev / n if n else 0.0
        pc = sub.groupby("customer_unique_id")["order_id"].nunique()
        repeat = (pc > 1).mean() if len(pc) else 0.0
        dv = sub[sub["order_status"] == "delivered"]
        ontime = dv["is_on_time"].dropna().mean() if len(dv) else float("nan")
        deldays = dv["delivery_days"].dropna().mean() if len(dv) else float("nan")
        score = sub["review_score"].dropna().mean()

        cols["Total Orders"].append(n)
        cols["Total Revenue (R$)"].append(rev)
        cols["Average Order Value (R$)"].append(aov)
        cols["Customer Repeat Rate"].append(repeat)
        cols["On-Time Delivery Rate"].append(ontime)
        cols["Avg Delivery Days"].append(deldays)
        cols["Avg Review Score"].append(score)

    df = pd.DataFrame(cols, index=[str(p) for p in periods]).T
    return df, df.mean(axis=1)


def kpi_scorecard(orders: pd.DataFrame, period_col: str, periods: list[str]):
    """Metric x period scorecard; benchmark = period average, red = miss."""
    numeric, bench = _period_metrics(orders, period_col, periods)

    display = pd.DataFrame(index=numeric.index, columns=numeric.columns, dtype="object")
    for m in numeric.index:
        display.loc[m] = [_fmt(m, v) for v in numeric.loc[m]]
    display["Benchmark"] = [_fmt(m, bench[m]) for m in numeric.index]

    bad = pd.DataFrame(False, index=numeric.index, columns=numeric.columns)
    for m in numeric.index:
        vals = numeric.loc[m]
        bad.loc[m] = (vals > bench[m]) if m in LOWER_IS_BETTER else (vals < bench[m])

    def _style(_df):
        css = pd.DataFrame("", index=numeric.index, columns=list(display.columns))
        for c in bad.columns:
            css[c] = bad[c].map(
                lambda b: "background-color:#fecaca;color:#991b1b;font-weight:600"
                if b else "")
        return css

    return display.style.apply(_style, axis=None)


def category_table(items: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Top-N categories by revenue with a rich executive detail table."""
    g = items.groupby("product_category_name_english").agg(
        n_orders=("order_id", "nunique"),
        n_customers=("customer_unique_id", "nunique"),
        items_sold=("order_item_id", "count"),
        revenue=("price", "sum"),
        revenue_freight=("item_value", "sum"),
        avg_price=("price", "mean"),
        avg_freight=("freight_value", "mean"),
        avg_rating=("review_score", "mean"),
        avg_delivery=("delivery_days", "mean"),
    )

    def _pct_neg(s):
        s = s.dropna()
        return (s.isin([1, 2]).mean()) if len(s) else float("nan")

    g["pct_neg"] = items.groupby("product_category_name_english")["review_score"].apply(_pct_neg)
    g = g.sort_values("revenue", ascending=False).head(top_n)

    out = pd.DataFrame({
        "Category": g.index,
        "Total Orders": g["n_orders"].map(lambda v: f"{v:,.0f}"),
        "Total Customers": g["n_customers"].map(lambda v: f"{v:,.0f}"),
        "Products Sold": g["items_sold"].map(lambda v: f"{v:,.0f}"),
        "Total Revenue": g["revenue"].map(lambda v: f"R$ {v:,.0f}"),
        "Revenue + Freight": g["revenue_freight"].map(lambda v: f"R$ {v:,.0f}"),
        "Average Price": g["avg_price"].map(lambda v: f"R$ {v:,.0f}"),
        "Average Freight": g["avg_freight"].map(lambda v: f"R$ {v:,.0f}"),
        "Average Rating": g["avg_rating"].map(lambda v: f"{v:.2f}"),
        "Avg Delivery Days": g["avg_delivery"].map(lambda v: f"{v:.1f}"),
        "% Ratings (1 & 2)": g["pct_neg"].map(lambda v: f"{v:.1%}"),
    }).reset_index(drop=True)
    return out
