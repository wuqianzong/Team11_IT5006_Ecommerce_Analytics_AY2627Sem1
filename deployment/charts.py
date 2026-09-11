"""Chart builders for the SmartCommerce dashboard.

Every figure is returned with theme.apply_layout applied (quiet chrome,
recessive grid, system sans). Color follows the data-viz method:
  - single series -> one hue (blue) for every mark
  - ordinal buckets (1..5 stars) -> blue, light -> dark
  - magnitude on a map -> sequential blue
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from . import theme

_GRAN = {"Monthly": "ME", "Weekly": "W", "Daily": "D"}


# ----------------------------------------------------------------------
# Overview / Orders
# ----------------------------------------------------------------------
def orders_over_time(orders: pd.DataFrame, granularity: str = "Monthly") -> go.Figure:
    freq = _GRAN[granularity]
    s = orders.set_index("order_purchase_timestamp").resample(freq)["order_id"].count()
    fig = px.line(x=s.index, y=s.values, color_discrete_sequence=[theme.BLUE])
    fig.update_traces(line=dict(width=2))
    fig.update_yaxes(title="Orders", rangemode="tozero")
    return theme.apply_layout(fig, title=f"Order volume ({granularity.lower()})", height=340)


def order_status_bar(orders: pd.DataFrame) -> go.Figure:
    counts = orders["order_status"].value_counts()
    fig = px.bar(x=counts.values, y=counts.index, orientation="h",
                 color_discrete_sequence=[theme.BLUE])
    fig.update_xaxes(title="Orders", rangemode="tozero")
    fig.update_yaxes(title=None)
    return theme.apply_layout(fig, title="Order status", height=300)


def order_value_hist(orders: pd.DataFrame, clip: int = 1000) -> go.Figure:
    d = orders[["order_value_total"]].dropna()
    d = d[d["order_value_total"] < clip]
    fig = px.histogram(d, x="order_value_total", nbins=50,
                       color_discrete_sequence=[theme.BLUE])
    fig.update_xaxes(title="Order value (R$)")
    fig.update_yaxes(title="Orders")
    return theme.apply_layout(fig, title=f"Order value distribution (< R$ {clip:,})", height=320)


def orders_by_dow(orders: pd.DataFrame) -> go.Figure:
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    counts = orders["day_name"].value_counts().reindex(order).fillna(0).astype(int)
    fig = px.bar(x=counts.index, y=counts.values, color_discrete_sequence=[theme.BLUE])
    fig.update_yaxes(title="Orders", rangemode="tozero")
    return theme.apply_layout(fig, title="Orders by day of week", height=320)


def orders_by_hour(orders: pd.DataFrame) -> go.Figure:
    counts = orders["hour"].value_counts().sort_index()
    fig = px.bar(x=counts.index.astype(str), y=counts.values,
                 color_discrete_sequence=[theme.BLUE])
    fig.update_xaxes(title="Hour of day (purchase)")
    fig.update_yaxes(title="Orders", rangemode="tozero")
    return theme.apply_layout(fig, title="Orders by hour of day", height=320)


# ----------------------------------------------------------------------
# Delivery
# ----------------------------------------------------------------------
def delivery_days_hist(orders: pd.DataFrame, clip: int = 60) -> go.Figure:
    d = orders[orders["order_status"] == "delivered"][["delivery_days"]].dropna()
    d = d[d["delivery_days"] < clip]
    fig = px.histogram(d, x="delivery_days", nbins=40,
                       color_discrete_sequence=[theme.BLUE])
    fig.update_xaxes(title="Delivery days")
    fig.update_yaxes(title="Orders")
    return theme.apply_layout(fig, title=f"Delivery time distribution (< {clip} days)", height=320)


def on_time_over_time(orders: pd.DataFrame) -> go.Figure:
    d = orders[orders["order_status"] == "delivered"]
    r = (d.set_index("order_purchase_timestamp")
           .resample("ME")["is_on_time"]
           .agg(lambda s: s.dropna().mean()))
    fig = px.line(x=r.index, y=r.values, color_discrete_sequence=[theme.BLUE])
    fig.update_traces(line=dict(width=2))
    fig.update_yaxes(title="On-time rate", tickformat=".0%")
    return theme.apply_layout(fig, title="On-time delivery rate by month", height=320)


def on_time_by_state(orders: pd.DataFrame, top_n: int = 10, worst: bool = True) -> go.Figure:
    d = orders[orders["order_status"] == "delivered"]
    g = (d.groupby("customer_state")
           .agg(on_time=("is_on_time", lambda s: s.dropna().mean()),
                n_orders=("order_id", "nunique"))
           .reset_index())
    g = g.sort_values("on_time", ascending=worst).head(top_n)
    fig = px.bar(g, x="on_time", y="customer_state", orientation="h",
                 color_discrete_sequence=[theme.BLUE])
    fig.update_xaxes(title="On-time rate", tickformat=".0%", rangemode="tozero")
    title = "Lowest on-time rate by state" if worst else "Highest on-time rate by state"
    return theme.apply_layout(fig, title=title, height=360)


def estimated_vs_actual(orders: pd.DataFrame, sample: int = 5000) -> go.Figure:
    d = orders[orders["order_status"] == "delivered"].copy()
    d["estimated_lead"] = (d["order_estimated_delivery_date"]
                           - d["order_purchase_timestamp"]).dt.days
    d = d.dropna(subset=["delivery_days", "estimated_lead"])
    d = d[(d["delivery_days"] < 60) & (d["estimated_lead"] < 60)]
    if len(d) > sample:
        d = d.sample(sample, random_state=0)
    maxv = max(d["delivery_days"].max(), d["estimated_lead"].max())
    fig = px.scatter(d, x="estimated_lead", y="delivery_days",
                     color_discrete_sequence=[theme.BLUE], opacity=0.5)
    fig.add_trace(go.Scatter(x=[0, maxv], y=[0, maxv], mode="lines",
                             line=dict(color=theme.BASELINE, width=1),
                             hoverinfo="skip"))
    fig.update_xaxes(title="Estimated lead time (days)")
    fig.update_yaxes(title="Actual delivery days")
    return theme.apply_layout(fig, title="Estimated vs actual delivery (dots above line = late)",
                              height=380, legend=False)


# ----------------------------------------------------------------------
# Reviews
# ----------------------------------------------------------------------
def review_score_bar(orders: pd.DataFrame) -> go.Figure:
    counts = orders["review_score"].dropna().value_counts().sort_index()
    scores = counts.index.astype(int)
    colors = [theme.REVIEW_TRAFFIC_5[s - 1] for s in scores]  # 1 red -> 5 green
    fig = go.Figure(go.Bar(x=scores.astype(str), y=counts.values, marker_color=colors))
    fig.update_xaxes(title="Review score")
    fig.update_yaxes(title="Orders", rangemode="tozero")
    return theme.apply_layout(fig, title="Review score distribution (skewed high)", height=320)


def avg_score_over_time(orders: pd.DataFrame) -> go.Figure:
    d = orders.dropna(subset=["review_score"])
    r = d.set_index("order_purchase_timestamp")["review_score"].resample("ME").mean()
    fig = px.line(x=r.index, y=r.values, color_discrete_sequence=[theme.BLUE])
    fig.update_traces(line=dict(width=2))
    fig.update_yaxes(title="Avg score", range=[1, 5])
    return theme.apply_layout(fig, title="Average review score by month", height=320)


def category_avg_score(items: pd.DataFrame, top_n: int = 10) -> go.Figure:
    d = items.dropna(subset=["review_score"])
    g = (d.groupby("product_category_name_english")
           .agg(avg_score=("review_score", "mean"),
                n_orders=("order_id", "nunique"))
           .reset_index())
    g = g[g["n_orders"] >= 100].sort_values("avg_score").head(top_n)
    fig = px.bar(g, x="avg_score", y="product_category_name_english", orientation="h",
                 color_discrete_sequence=[theme.BLUE])
    fig.update_xaxes(title="Avg review score", range=[1, 5])
    fig.update_yaxes(title=None)
    return theme.apply_layout(fig, title=f"{top_n} lowest-rated categories (≥100 orders)",
                              height=360)


# ----------------------------------------------------------------------
# Categories
# ----------------------------------------------------------------------
def category_revenue(items: pd.DataFrame, top_n: int = 10) -> go.Figure:
    g = (items.groupby("product_category_name_english")
           .agg(revenue=("price", "sum"), n_orders=("order_id", "nunique"))
           .reset_index()
           .sort_values("revenue", ascending=False)
           .head(top_n))
    fig = px.bar(g, x="revenue", y="product_category_name_english", orientation="h",
                 color_discrete_sequence=[theme.BLUE])
    fig.update_xaxes(title="Revenue (R$)", rangemode="tozero")
    fig.update_yaxes(title=None)
    return theme.apply_layout(fig, title=f"Top {top_n} categories by revenue", height=360)


def category_orders(items: pd.DataFrame, top_n: int = 10) -> go.Figure:
    g = (items.groupby("product_category_name_english")
           .agg(n_orders=("order_id", "nunique"))
           .reset_index()
           .sort_values("n_orders", ascending=False)
           .head(top_n))
    fig = px.bar(g, x="n_orders", y="product_category_name_english", orientation="h",
                 color_discrete_sequence=[theme.BLUE])
    fig.update_xaxes(title="Orders", rangemode="tozero")
    fig.update_yaxes(title=None)
    return theme.apply_layout(fig, title=f"Top {top_n} categories by orders", height=360)


def category_price_box(items: pd.DataFrame, top_n: int = 5) -> go.Figure:
    top = (items.groupby("product_category_name_english")["order_id"].nunique()
              .sort_values(ascending=False).head(top_n).index)
    d = items[items["product_category_name_english"].isin(top)]
    fig = px.box(d, x="product_category_name_english", y="price",
                 color_discrete_sequence=[theme.BLUE], points=False)
    fig.update_xaxes(title=None)
    fig.update_yaxes(title="Item price (R$)")
    return theme.apply_layout(fig, title=f"Price spread — top {top_n} categories", height=360)


def category_on_time(items: pd.DataFrame, top_n: int = 10) -> go.Figure:
    d = items[items["order_status"] == "delivered"]
    g = (d.groupby("product_category_name_english")
           .agg(on_time=("is_on_time", lambda s: s.dropna().mean()),
                n_orders=("order_id", "nunique"))
           .reset_index())
    g = g[g["n_orders"] >= 200].sort_values("on_time").head(top_n)
    fig = px.bar(g, x="on_time", y="product_category_name_english", orientation="h",
                 color_discrete_sequence=[theme.BLUE])
    fig.update_xaxes(title="On-time rate", tickformat=".0%", rangemode="tozero")
    fig.update_yaxes(title=None)
    return theme.apply_layout(fig, title="Lowest on-time rate by category", height=360)


# ----------------------------------------------------------------------
# Geography
# ----------------------------------------------------------------------
def build_state_geo(orders: pd.DataFrame, geo_state: pd.DataFrame) -> pd.DataFrame:
    """Recompute state aggregates from the (filtered) orders and join centroids."""
    d = orders[orders["order_status"] == "delivered"]
    agg = (d.groupby("customer_state")
             .agg(n_orders=("order_id", "nunique"),
                  total_value=("order_value_total", "sum"),
                  avg_delivery_days=("delivery_days", "mean"),
                  on_time_rate=("is_on_time", lambda s: s.dropna().mean()))
             .reset_index()
             .rename(columns={"customer_state": "state"}))
    base = geo_state[["state", "state_name", "lat", "lng"]]
    return base.merge(agg, on="state", how="left")


def state_map(state_geo: pd.DataFrame) -> go.Figure:
    fig = px.scatter_geo(
        state_geo,
        lat="lat", lon="lng",
        size="n_orders", size_max=45,
        color="on_time_rate",
        color_continuous_scale=theme.SEQUENTIAL_BLUE,
        hover_name="state_name",
        hover_data={"n_orders": True, "on_time_rate": True,
                    "avg_delivery_days": True, "total_value": True},
        scope="south america",
    )
    fig.update_geos(
        showland=True, landcolor="#f9f9f7",
        showcountries=True, countrycolor="#c3c2b7",
        coastlinecolor="#c3c2b7", showframe=False,
        center=dict(lat=-14.5, lon=-53),
    )
    fig.update_coloraxes(colorbar=dict(title="On-time rate", thickness=12,
                                       tickformat=".0%", outlinewidth=0))
    return theme.apply_layout(fig, title="Orders & on-time rate by state", height=460)


def state_orders_bar(state_geo: pd.DataFrame, top_n: int = 10) -> go.Figure:
    g = state_geo.sort_values("n_orders", ascending=False).head(top_n)
    fig = px.bar(g, x="n_orders", y="state_name", orientation="h",
                 color_discrete_sequence=[theme.BLUE])
    fig.update_xaxes(title="Orders", rangemode="tozero")
    fig.update_yaxes(title=None)
    return theme.apply_layout(fig, title=f"Top {top_n} states by orders", height=360)


# ----------------------------------------------------------------------
# Executive presentation (reproduces the teammate's scorecard style)
# ----------------------------------------------------------------------
def review_distribution_over_time(orders: pd.DataFrame,
                                  granularity: str = "Monthly") -> go.Figure:
    """100% stacked share of 1..5-star reviews per period (red .. green)."""
    freq = "M" if granularity == "Monthly" else "W"
    d = orders.dropna(subset=["review_score"]).copy()
    d["_p"] = d["order_purchase_timestamp"].dt.to_period(freq)
    ct = pd.crosstab(d["_p"], d["review_score"], normalize="index") * 100
    for s in range(1, 6):
        if s not in ct.columns:
            ct[s] = 0.0
    ct = ct.reindex(sorted(ct.columns), axis=1)

    fig = go.Figure()
    for s in range(1, 6):
        fig.add_trace(go.Bar(
            name=f"{s} star", x=[str(p) for p in ct.index], y=ct[s],
            marker_color=theme.REVIEW_TRAFFIC_5[s - 1]))
    fig.update_layout(barmode="stack")
    fig.update_yaxes(title="Share of reviews", ticksuffix="%", range=[0, 100])
    return theme.apply_layout(fig, title="Review score distribution over time", height=360)


def category_gainers_losers(curr_items: pd.DataFrame, prev_items: pd.DataFrame,
                            top_n: int = 5) -> go.Figure:
    """Category revenue change: current period vs the previous equal-length
    period (period-over-period), red for losers and green for gainers."""
    cur = curr_items.groupby("product_category_name_english")["price"].sum()
    prev = prev_items.groupby("product_category_name_english")["price"].sum()
    diff = (cur - prev).fillna(0)
    combined = pd.concat([diff.nsmallest(top_n), diff.nlargest(top_n)]).sort_values()
    colors = [theme.LOSS if v < 0 else theme.GAIN for v in combined.values]
    labels = [f"{'+' if v >= 0 else '-'}R$ {abs(v):,.0f}" for v in combined.values]
    fig = go.Figure(go.Bar(x=combined.values, y=combined.index.astype(str),
                           orientation="h", marker_color=colors,
                           text=labels, textposition="outside",
                           textfont=dict(size=10, color=theme.INK_SECONDARY)))
    fig.add_vline(x=0, line_width=1, line_color=theme.BASELINE)
    fig.update_xaxes(title="Revenue change vs previous period (R$)")
    fig.update_yaxes(title=None)
    return theme.apply_layout(fig, title="Category revenue — gainers & losers "
                                         "(vs previous period)", height=360)


def review_stacked(df: pd.DataFrame, group_col: str, title: str,
                   order: list | None = None, height: int = 360,
                   show_legend: bool = True) -> go.Figure:
    """100% stacked share of 1..5-star reviews per group (red .. green)."""
    d = df.dropna(subset=["review_score"]).copy()
    ct = pd.crosstab(d[group_col], d["review_score"], normalize="index") * 100
    if order is not None:
        ct = ct.reindex([g for g in order if g in ct.index])
    for s in range(1, 6):
        if s not in ct.columns:
            ct[s] = 0.0
    ct = ct[sorted(ct.columns)]
    fig = go.Figure()
    for s in range(1, 6):
        fig.add_trace(go.Bar(name=f"{s}★", x=[str(i) for i in ct.index],
                             y=ct[s], marker_color=theme.REVIEW_TRAFFIC_5[s - 1]))
    fig.update_layout(barmode="stack")
    fig.update_yaxes(title="Share of reviews", ticksuffix="%", range=[0, 100])
    return theme.apply_layout(fig, title=title, height=height, legend=show_legend)


def delivery_boxplot(df: pd.DataFrame, group_col: str, title: str,
                     order: list | None = None, color: str | None = None,
                     height: int = 360) -> go.Figure:
    """Delivery-days box plot per group, capped to 0..100 days."""
    d = df[df["order_status"] == "delivered"][[group_col, "delivery_days"]].dropna()
    d = d[d["delivery_days"] <= 100]
    if order is not None:
        d[group_col] = pd.Categorical(d[group_col], categories=order, ordered=True)
        d = d.sort_values(group_col)
    fig = go.Figure(go.Box(x=d[group_col].astype(str), y=d["delivery_days"],
                           marker=dict(color=color or theme.BLUE_BOX)))
    fig.update_yaxes(title="Delivery days", range=[0, 100])
    return theme.apply_layout(fig, title=title, height=height)


def revenue_bar(df: pd.DataFrame, group_col: str, title: str,
                color: str | None = None, top_n: int = 10,
                order: list | None = None, height: int = 360) -> go.Figure:
    """Vertical revenue bar for the top-N groups (buyer/seller states, etc.)."""
    g = df.groupby(group_col)["price"].sum().sort_values(ascending=False)
    if order is not None:
        g = g.reindex([x for x in order if x in g.index])
    else:
        g = g.head(top_n)
    fig = go.Figure(go.Bar(x=g.index.astype(str), y=g.values,
                           marker_color=color or theme.BLUE_BAR))
    fig.update_yaxes(title="Revenue (R$)")
    return theme.apply_layout(fig, title=title, height=height)


def trend_line(df: pd.DataFrame, x: str, y: str, title: str,
               color: str | None = None, height: int = 320) -> go.Figure:
    """Line trend with markers (e.g. category revenue over periods)."""
    fig = go.Figure(go.Scatter(x=df[x].astype(str), y=df[y], mode="lines+markers",
                               line=dict(width=2, color=color or theme.BLUE_PRIMARY),
                               marker=dict(color=color or theme.BLUE_PRIMARY)))
    fig.update_yaxes(title=y)
    return theme.apply_layout(fig, title=title, height=height)


def trend_bar(df: pd.DataFrame, x: str, y: str, title: str,
              color: str | None = None, height: int = 320) -> go.Figure:
    """Vertical bar for a trend (e.g. category order volume over periods)."""
    fig = go.Figure(go.Bar(x=df[x].astype(str), y=df[y],
                           marker_color=color or theme.BLUE_BAR))
    fig.update_yaxes(title=y)
    return theme.apply_layout(fig, title=title, height=height)


def state_revenue_bar(df: pd.DataFrame, state_col: str, value_col: str,
                      title: str, top_n: int = 10) -> go.Figure:
    """Generic top-N revenue-by-state horizontal bar (buyer or seller)."""
    g = (df.groupby(state_col)[value_col].sum()
           .sort_values(ascending=False).head(top_n))
    fig = px.bar(x=g.values, y=g.index, orientation="h",
                 color_discrete_sequence=[theme.BLUE])
    fig.update_xaxes(title="Revenue (R$)", rangemode="tozero")
    fig.update_yaxes(title=None)
    return theme.apply_layout(fig, title=title, height=360)


# ----------------------------------------------------------------------
# National state performance (mart_state_summary)
# ----------------------------------------------------------------------
def state_on_time_bar(state_summary: pd.DataFrame, height: int = 560) -> go.Figure:
    """Rank all states by on-time delivery rate (worst first)."""
    d = state_summary.dropna(subset=["on_time_rate"]).sort_values("on_time_rate")
    fig = go.Figure(go.Bar(x=d["on_time_rate"], y=d["state_name"], orientation="h",
                           marker_color=theme.BLUE_BAR))
    fig.update_xaxes(title="On-time rate", tickformat=".0%", rangemode="tozero")
    fig.update_yaxes(title=None)
    return theme.apply_layout(fig, title="On-time delivery rate by state (worst first)",
                              height=height)


def state_on_time_scatter(state_summary: pd.DataFrame, height: int = 560) -> go.Figure:
    """Reliability (on-time) vs speed (delivery days); bubble size = orders."""
    d = state_summary.dropna(subset=["on_time_rate", "avg_delivery_days"])
    fig = px.scatter(d, x="avg_delivery_days", y="on_time_rate", size="n_orders",
                     size_max=50, hover_name="state_name",
                     hover_data={"n_orders": True, "total_value": True},
                     color_discrete_sequence=[theme.BLUE_PRIMARY])
    fig.update_xaxes(title="Avg delivery days")
    fig.update_yaxes(title="On-time rate", tickformat=".0%")
    return theme.apply_layout(fig, title="On-time rate vs delivery speed (bubble = orders)",
                              height=height)


# ----------------------------------------------------------------------
# Category time trends (mart_category_daily)
# ----------------------------------------------------------------------
def category_multi_line(cat_daily: pd.DataFrame, metric: str = "revenue",
                        top_n: int = 6, height: int = 480) -> go.Figure:
    """Top-N categories as separate monthly lines (side-by-side comparison)."""
    d = cat_daily.copy()
    d["month"] = d["order_purchase_date"].dt.to_period("M").astype(str)
    top = (d.groupby("product_category_name_english")[metric].sum()
            .nlargest(top_n).index.tolist())
    d = d[d["product_category_name_english"].isin(top)]
    monthly = (d.groupby(["month", "product_category_name_english"], as_index=False)[metric]
                 .sum().sort_values("month"))
    fig = px.line(monthly, x="month", y=metric, color="product_category_name_english",
                  color_discrete_sequence=theme.CATEGORICAL)
    fig.update_xaxes(title="Month")
    fig.update_yaxes(title=metric.replace("_", " ").title())
    fig = theme.apply_layout(fig, title=f"Top {top_n} categories — {metric} over time",
                             height=height)
    fig.update_layout(legend_title_text="Category")
    return fig


def category_heatmap(cat_daily: pd.DataFrame, metric: str = "revenue",
                     top_n: int = 15, height: int = 480) -> go.Figure:
    """Category × month heatmap of a metric (compact seasonality overview)."""
    d = cat_daily.copy()
    d["month"] = d["order_purchase_date"].dt.to_period("M").astype(str)
    top = (d.groupby("product_category_name_english")[metric].sum()
            .nlargest(top_n).index.tolist())
    d = d[d["product_category_name_english"].isin(top)]
    pivot = d.pivot_table(index="product_category_name_english",
                          columns="month", values=metric, aggfunc="sum", fill_value=0.0)
    pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).index]
    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=list(pivot.columns), y=list(pivot.index),
        colorscale=theme.SEQUENTIAL_BLUE,
        colorbar=dict(title=metric.replace("_", " ").title(), thickness=12, outlinewidth=0),
    ))
    fig.update_xaxes(title="Month", tickangle=45)
    fig.update_yaxes(title="Category")
    return theme.apply_layout(fig, title=f"Category × month {metric} heatmap", height=height)


# ----------------------------------------------------------------------
# Data-quality panel (mart_data_quality)
# ----------------------------------------------------------------------
def data_quality_bar(dq: pd.DataFrame, height: int = 420) -> go.Figure:
    """Row count per materialised table (log scale — spans 71 .. 1M rows)."""
    d = dq.sort_values("rows").copy()
    d["label"] = d["layer"] + " · " + d["table"]
    colors = [theme.STATUS["good"] if s == "OK" else theme.STATUS["critical"]
              for s in d["status"]]
    fig = go.Figure(go.Bar(x=d["rows"], y=d["label"], orientation="h", marker_color=colors))
    fig.update_xaxes(title="Rows", type="log")
    fig.update_yaxes(title=None)
    return theme.apply_layout(fig, title="Row count per table (log scale)", height=height)
