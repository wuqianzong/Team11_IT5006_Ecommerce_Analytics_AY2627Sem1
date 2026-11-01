import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

# =============================================================================
# 1. EXECUTIVE SUMMARY & SYSTEM ARCHITECTURE
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "business" / "dashboard"
DATA_PATH = DATA_DIR / "smartcommerce_consolidated.csv"
CONFIG_PATH = DATA_DIR / "dashboard_default.config"

st.set_page_config(
    page_title="Executive Operations Master Dashboard",
    page_icon="📊",
    layout="wide",
)

# Benchmark & Config Default Master Schema
DEFAULT_CONFIG = {
    "lookback_periods_default": 3,
    "default_category": "health_beauty",
    "min_total_orders_per_time": 100,
    "delivery_days_y_max": 100,
    "top_n_gainers_losers": 5,
    "top_n_buyers": 100,
    "top_star_buyers": 5,
    "top_n_sellers": 100,
    "top_star_sellers": 5,
    "total_revenue": 950000.0,
    "total_orders": 6500.0,
    "average_order_value": 130.0,
    "price_ratio_pct": 0.90,
    "freight_ratio_pct": 0.10,
    "customer_repeat_rate_pct": 0.009,
    "ontime_delivery_rate_pct": 0.90,
    "average_delivery_days": 8.8,
    "average_review_score": 4.0,
    "low_rating_ratio_pct": 0.10,
    "category_benchmarks": {},
}


def load_config():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r") as f:
                cfg = json.load(f)
                merged = DEFAULT_CONFIG.copy()
                merged.update(cfg)
                return merged
        except Exception:
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(cfg):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=4)


config = load_config()

# Data Loader
@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        # Resilient fallback: dynamically merge from data/business/dashboard/ CSVs
        if (DATA_DIR / "olist_orders_dataset.csv").exists():
            orders = pd.read_csv(DATA_DIR / "olist_orders_dataset.csv")
            order_items = pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv")
            customers = pd.read_csv(DATA_DIR / "olist_customers_dataset.csv")
            products = pd.read_csv(DATA_DIR / "olist_products_dataset.csv")
            sellers = pd.read_csv(DATA_DIR / "olist_sellers_dataset.csv")
            payments = pd.read_csv(DATA_DIR / "olist_order_payments_dataset.csv")
            reviews = pd.read_csv(DATA_DIR / "olist_order_reviews_dataset.csv")
            trans = pd.read_csv(DATA_DIR / "product_category_name_translation.csv")

            products = products.merge(trans, on="product_category_name", how="left")
            products["product_category_name_english"] = products["product_category_name_english"].fillna("Unknown")

            payments_by_order = payments.groupby("order_id").agg({
                "payment_value": "sum",
                "payment_installments": "max"
            }).reset_index()

            df = order_items.copy()
            df = df.merge(products[["product_id", "product_category_name_english", "product_description_lenght", "product_photos_qty", "product_weight_g"]], on="product_id", how="left")
            df = df.merge(orders, on="order_id", how="left")
            df = df.merge(customers[["customer_id", "customer_unique_id", "customer_state", "customer_city"]], on="customer_id", how="left")
            df = df.merge(sellers[["seller_id", "seller_city", "seller_state"]], on="seller_id", how="left")
            df = df.merge(payments_by_order, on="order_id", how="left")
            df = df.merge(reviews[["review_id", "order_id", "review_score"]], on="order_id", how="left")
            df.dropna(subset=["order_id"], inplace=True)
            # Cache to disk for instant future loading
            try:
                df.to_csv(DATA_PATH, index=False)
            except Exception:
                pass
        else:
            st.error(f"Data mart file not found at: {DATA_PATH}")
            st.stop()
    else:
        df = pd.read_csv(DATA_PATH)

    date_cols = [c for c in df.columns if "date" in c or "timestamp" in c]
    for c in date_cols:
        df[c] = pd.to_datetime(df[c], errors="coerce")

    if "order_purchase_timestamp" in df.columns:
        df["order_purchase_timestamp"] = pd.to_datetime(
            df["order_purchase_timestamp"]
        )
        df["year_month"] = df["order_purchase_timestamp"].dt.strftime("%Y-%m")
        df["year_week"] = df["order_purchase_timestamp"].dt.strftime("%Y-%W")
    return df


df_raw = load_data()

# =============================================================================
# 2. VISUAL AESTHETICS & FORMATTING UTILITIES
# =============================================================================
STAR_GRADIENT = ["#ef4444", "#f97316", "#eab308", "#84cc16", "#22c55e"]
RED_CELL_STYLE = "background-color: #fecaca; color: #991b1b; font-weight: bold;"


def format_business_num(val, is_currency=False, is_pct=False):
    if pd.isna(val) or val is None:
        return "-"
    prefix = "R$ " if is_currency else ""

    if is_pct:
        return f"{prefix}{val * 100:.3g}%"

    abs_v = abs(val)
    if abs_v >= 1000:
        return f"{prefix}{val:,.0f}"
    elif 1 <= abs_v < 1000:
        return f"{prefix}{val:.2f}"
    else:
        return f"{prefix}{val:.3g}"


# =============================================================================
# 4. MASTER CONTROL PANEL & DYNAMIC SELECTION (STEP 0)
# =============================================================================
st.sidebar.title("⚙️ Dashboard Controls & Config")

with st.sidebar.expander("🌐 Global Benchmarks & Parameters", expanded=False):
    lookback = st.slider(
        "Lookback Periods", 1, 12, int(config["lookback_periods_default"])
    )
    categories = sorted(
        df_raw["product_category_name_english"].dropna().unique()
    )
    default_cat_idx = (
        categories.index(config["default_category"])
        if config["default_category"] in categories
        else 0
    )
    selected_cat = st.selectbox(
        "Default Category", categories, index=default_cat_idx
    )

    min_orders = st.number_input(
        "Min Orders / Period (SLA)",
        value=int(config["min_total_orders_per_time"]),
    )
    deliv_y_max = st.slider(
        "Delivery Days Max Y-Axis",
        20,
        300,
        int(config["delivery_days_y_max"]),
    )
    top_n_gl = st.slider(
        "Top N Gainers/Losers", 3, 15, int(config["top_n_gainers_losers"])
    )

    bm_rev = st.number_input(
        "Target Total Revenue (R$)", value=float(config["total_revenue"])
    )
    bm_orders = st.number_input(
        "Target Total Orders", value=float(config["total_orders"])
    )
    bm_aov = st.number_input(
        "Target AOV (R$)", value=float(config["average_order_value"])
    )
    bm_price_ratio = st.slider(
        "Target Price Ratio (%)",
        50,
        100,
        int(config["price_ratio_pct"] * 100),
    ) / 100.0
    bm_freight_ratio = (
        st.slider(
            "Max Freight Ratio (%)",
            0,
            50,
            int(config["freight_ratio_pct"] * 100),
        )
        / 100.0
    )
    bm_repeat_rate = (
        st.slider(
            "Min Repeat Rate (%)",
            1,
            100,
            int(config["customer_repeat_rate_pct"] * 1000),
        )
        / 1000.0
    )
    bm_ontime = (
        st.slider(
            "Min On-Time Delivery Rate (%)",
            50,
            100,
            int(config["ontime_delivery_rate_pct"] * 100),
        )
        / 100.0
    )
    bm_deliv_days = st.number_input(
        "Max Delivery Days", value=float(config["average_delivery_days"])
    )
    bm_review_score = st.slider(
        "Min Avg Review Score",
        1.0,
        5.0,
        float(config["average_review_score"]),
        0.1,
    )
    bm_low_rating = (
        st.slider(
            "Max 1&2 Star Ratio (%)",
            1,
            30,
            int(config["low_rating_ratio_pct"] * 100),
        )
        / 100.0
    )

    if st.button("💾 Save Global Defaults"):
        config.update(
            {
                "lookback_periods_default": lookback,
                "default_category": selected_cat,
                "min_total_orders_per_time": min_orders,
                "delivery_days_y_max": deliv_y_max,
                "top_n_gainers_losers": top_n_gl,
                "total_revenue": bm_rev,
                "total_orders": bm_orders,
                "average_order_value": bm_aov,
                "price_ratio_pct": bm_price_ratio,
                "freight_ratio_pct": bm_freight_ratio,
                "customer_repeat_rate_pct": bm_repeat_rate,
                "ontime_delivery_rate_pct": bm_ontime,
                "average_delivery_days": bm_deliv_days,
                "average_review_score": bm_review_score,
                "low_rating_ratio_pct": bm_low_rating,
            }
        )
        save_config(config)
        st.success("Global config saved successfully!")

with st.sidebar.expander("🏷️ Category Benchmark Overrides", expanded=False):
    cat_to_override = st.selectbox(
        "Category to Override", categories, key="cat_override_select"
    )
    existing_cat_bm = config.get("category_benchmarks", {}).get(
        cat_to_override, {}
    )

    cat_bm_rev = st.number_input(
        "Category Revenue Target (R$)",
        value=float(existing_cat_bm.get("total_revenue", 0.0)),
    )
    cat_bm_orders = st.number_input(
        "Category Orders Target",
        value=float(existing_cat_bm.get("total_orders", 0.0)),
    )
    cat_bm_aov = st.number_input(
        "Category AOV Target (R$)",
        value=float(existing_cat_bm.get("average_order_value", 0.0)),
    )
    cat_bm_deliv = st.number_input(
        "Category Max Delivery Days Target",
        value=float(
            existing_cat_bm.get("average_delivery_days", bm_deliv_days)
        ),
    )
    cat_bm_review = st.slider(
        "Category Min Review Score Target",
        1.0,
        5.0,
        float(existing_cat_bm.get("average_review_score", bm_review_score)),
        0.1,
    )

    if st.button("💾 Save Category Benchmark"):
        if "category_benchmarks" not in config:
            config["category_benchmarks"] = {}
        config["category_benchmarks"][cat_to_override] = {
            "total_revenue": cat_bm_rev if cat_bm_rev > 0 else None,
            "total_orders": cat_bm_orders if cat_bm_orders > 0 else None,
            "average_order_value": cat_bm_aov if cat_bm_aov > 0 else None,
            "average_delivery_days": cat_bm_deliv,
            "average_review_score": cat_bm_review,
        }
        save_config(config)
        st.success(f"Saved custom targets for {cat_to_override}!")

grain = st.radio("Select Date Grain", ["Monthly", "Weekly"], horizontal=True)

with st.spinner("Filtering dynamic data grain..."):
    time_col = "year_month" if grain == "Monthly" else "year_week"
    available_periods = sorted(df_raw[time_col].dropna().unique())

    default_start_idx = max(0, len(available_periods) - lookback)
    start_period, end_period = st.select_slider(
        "Active Period Window",
        options=available_periods,
        value=(
            available_periods[default_start_idx],
            available_periods[-1],
        ),
    )

    selected_periods = [
        p for p in available_periods if start_period <= p <= end_period
    ]
    df_filtered = df_raw[df_raw[time_col].isin(selected_periods)].copy()


def get_scaling_factor():
    return 7.0 / 30.0 if grain == "Weekly" else 1.0


def calculate_kpi_matrix(df_data):
    grouped = df_data.groupby(time_col)
    res = pd.DataFrame()

    order_level = df_data.drop_duplicates("order_id")
    order_grouped = order_level.groupby(time_col)

    res["Total Revenue (R$)"] = grouped["price"].sum()
    res["Total Orders"] = order_grouped["order_id"].nunique()
    res["Average Order Value (R$)"] = (
        res["Total Revenue (R$)"] / res["Total Orders"]
    )

    tot_price = grouped["price"].sum()
    tot_freight = grouped["freight_value"].sum()
    tot_val = tot_price + tot_freight
    res["Price to Order Value (%)"] = tot_price / tot_val
    res["Freight to Order Value (%)"] = tot_freight / tot_val

    cust_orders = df_data.groupby([time_col, "customer_unique_id"])[
        "order_id"
    ].nunique()
    repeat_custs = cust_orders[cust_orders > 1].groupby(time_col).size()
    total_custs = df_data.groupby(time_col)["customer_unique_id"].nunique()
    res["Customer Repeat Rate"] = (repeat_custs / total_custs).fillna(0)

    res["On-Time Delivery Rate"] = order_grouped["is_on_time"].mean()
    res["Average Delivery Days"] = order_grouped["delivery_days"].mean()
    res["Average Review Score"] = grouped["review_score"].mean()

    low_ratings = grouped["review_score"].apply(
        lambda s: (s.isin([1, 2])).sum() / len(s) if len(s) > 0 else 0
    )
    res["% Rating 1 & 2"] = low_ratings
    return res.T


def get_effective_benchmarks():
    sf = get_scaling_factor()
    bm = {
        "Total Revenue (R$)": bm_rev * sf,
        "Total Orders": bm_orders * sf,
        "Average Order Value (R$)": bm_aov,
        "Price to Order Value (%)": bm_price_ratio,
        "Freight to Order Value (%)": bm_freight_ratio,
        "Customer Repeat Rate": (
            "N/A" if grain == "Weekly" else bm_repeat_rate
        ),
        "On-Time Delivery Rate": bm_ontime,
        "Average Delivery Days": bm_deliv_days,
        "Average Review Score": bm_review_score,
        "% Rating 1 & 2": bm_low_rating,
    }
    return bm


def is_non_compliant(metric, val, target):
    if target == "N/A" or pd.isna(val) or target is None:
        return False
    if metric in [
        "Total Revenue (R$)",
        "Total Orders",
        "Average Order Value (R$)",
        "Price to Order Value (%)",
        "Customer Repeat Rate",
        "On-Time Delivery Rate",
        "Average Review Score",
    ]:
        return val < target
    if metric in [
        "Freight to Order Value (%)",
        "Average Delivery Days",
        "% Rating 1 & 2",
    ]:
        return val > target
    return False


# =============================================================================
# STEP 1: EXECUTIVE KPI PERFORMANCE DASHBOARD & FULL-WIDTH VISUAL STACK
# =============================================================================
st.title("📈 Executive Operations Master Dashboard")
st.header("Step 1: Executive Business KPI Performance Matrix")

kpi_df = calculate_kpi_matrix(df_filtered)
benchmarks = get_effective_benchmarks()

display_kpi = kpi_df.copy()
display_kpi["Benchmark"] = [benchmarks[m] for m in display_kpi.index]


def style_kpi_table(df_disp):
    formatted = pd.DataFrame(index=df_disp.index, columns=df_disp.columns)
    style_matrix = pd.DataFrame(
        "", index=df_disp.index, columns=df_disp.columns
    )

    for metric in df_disp.index:
        is_curr = "Revenue" in metric or "Value" in metric
        is_pct = (
            "%" in metric or "Rate" in metric or "Ratio" in metric
        ) and ("Value" not in metric)
        target = benchmarks[metric]

        for col in df_disp.columns:
            val = df_disp.loc[metric, col]
            if col == "Benchmark":
                formatted.loc[metric, col] = (
                    "N/A"
                    if val == "N/A"
                    else format_business_num(
                        val, is_currency=is_curr, is_pct=is_pct
                    )
                )
            else:
                formatted.loc[metric, col] = format_business_num(
                    val, is_currency=is_curr, is_pct=is_pct
                )
                if is_non_compliant(metric, val, target):
                    style_matrix.loc[metric, col] = RED_CELL_STYLE
                    style_matrix.loc[metric, "RowLabel"] = RED_CELL_STYLE

    def apply_styles(x):
        df_st = pd.DataFrame("", index=x.index, columns=x.columns)
        for r in x.index:
            for c in x.columns:
                if style_matrix.loc[r, c] != "":
                    df_st.loc[r, c] = style_matrix.loc[r, c]
        return df_st

    return formatted.style.apply(apply_styles, axis=None)


st.dataframe(style_kpi_table(display_kpi), use_container_width=True)

st.subheader("KPI Diagnostic Stack")

fig_corr, ax_corr = plt.subplots(figsize=(12, 5))
sns.heatmap(
    kpi_df.T.corr(numeric_only=True),
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    ax=ax_corr,
    cbar=True,
)
ax_corr.set_title(
    "KPI Correlations Matrix", fontweight="bold", fontsize=12
)
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
st.pyplot(fig_corr)

# Period over Period Growth Rate Section
st.subheader("Period over Period Growth Rate")

fig_pop, axes_pop = plt.subplots(2, 2, figsize=(12, 9))
pop_metrics = [
    "Total Revenue (R$)",
    "Total Orders",
    "On-Time Delivery Rate",
    "Average Review Score",
]
pop_df = kpi_df.loc[pop_metrics].T.pct_change().dropna(how="all")

for idx, metric in enumerate(pop_metrics):
    ax = axes_pop[idx // 2, idx % 2]
    if metric in pop_df.columns:
        vals = pop_df[metric].dropna()
        colors = ["#22c55e" if v >= 0 else "#ef4444" for v in vals]
        bars = ax.bar(range(len(vals)), vals * 100, color=colors, width=0.4)
        ax.set_xticks(range(len(vals)))
        ax.set_xticklabels(vals.index, rotation=30, ha="right", fontsize=9)

        if len(vals) > 0:
            v_min = (vals * 100).min()
            v_max = (vals * 100).max()
            pad = max(abs(v_min), abs(v_max)) * 0.5 if max(abs(v_min), abs(v_max)) > 0 else 5
            ax.set_ylim(min(v_min - pad, -8), max(v_max + pad, 8))

        for bar, v in zip(bars, vals):
            symbol = "▲" if v >= 0 else "▼"
            val_pct = v * 100
            y_pos = val_pct / 2.0
            ax.text(
                bar.get_x() + bar.get_width() / 2.0,
                y_pos,
                f"{symbol} {abs(val_pct):.1f}%",
                ha="center",
                va="center",
                fontsize=8,
                fontweight="bold",
                color="white",
            )

    ax.set_title(f"PoP Growth: {metric}", fontweight="bold", fontsize=10)
    ax.set_ylabel("Change (%)", fontsize=9)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")

plt.subplots_adjust(hspace=0.4, wspace=0.25)
st.pyplot(fig_pop)


# =============================================================================
# STEP 2: TOP 10 & BOTTOM 10 CATEGORY PERFORMANCE OVERVIEW
# =============================================================================
st.divider()
st.header("Step 2: Category Performance Overview (Top 10 & Bottom 10)")


def build_category_overview(df_data):
    cat_grouped = df_data.groupby("product_category_name_english")
    order_cat = df_data.drop_duplicates(
        ["order_id", "product_category_name_english"]
    ).groupby("product_category_name_english")

    rev = cat_grouped["price"].sum()
    orders = order_cat["order_id"].nunique()
    aov = rev / orders

    tot_price = cat_grouped["price"].sum()
    tot_freight = cat_grouped["freight_value"].sum()
    tot_val = tot_price + tot_freight
    price_ratio = tot_price / tot_val
    freight_ratio = tot_freight / tot_val

    cust_orders = df_data.groupby(
        ["product_category_name_english", "customer_unique_id"]
    )["order_id"].nunique()
    repeat_custs = (
        cust_orders[cust_orders > 1]
        .groupby("product_category_name_english")
        .size()
    )
    total_custs = cat_grouped["customer_unique_id"].nunique()
    repeat_rate = (repeat_custs / total_custs).fillna(0)

    ontime = order_cat["is_on_time"].mean()
    deliv_days = order_cat["delivery_days"].mean()
    review = cat_grouped["review_score"].mean()

    low_rating = cat_grouped["review_score"].apply(
        lambda s: (s.isin([1, 2])).sum() / len(s) if len(s) > 0 else 0
    )

    res = pd.DataFrame(
        {
            "Total Revenue (R$)": rev,
            "Total Orders": orders,
            "Average Order Value (R$)": aov,
            "Price to Order Value (%)": price_ratio,
            "Freight to Order Value (%)": freight_ratio,
            "Customer Repeat Rate": repeat_rate,
            "On-Time Delivery Rate": ontime,
            "Average Delivery Days": deliv_days,
            "Average Review Score": review,
            "% Rating 1 & 2": low_rating,
        }
    )
    return res


cat_summary = build_category_overview(df_filtered)
top_10_cats = cat_summary.sort_values(
    "Total Revenue (R$)", ascending=False
).head(10)
bot_10_cats = cat_summary.sort_values(
    "Total Revenue (R$)", ascending=True
).head(10)


def render_category_table(df_cat, title):
    st.subheader(title)
    df_disp = df_cat.copy()
    cat_bms = config.get("category_benchmarks", {})
    bm_cols = []

    for cat in df_disp.index:
        cat_override = cat_bms.get(cat, {})
        cat_bm_str = (
            f"Rev: {format_business_num(cat_override.get('total_revenue'), True)} | "
            f"Deliv: <{cat_override.get('average_delivery_days', bm_deliv_days)}d"
        )
        bm_cols.append(cat_bm_str)

    df_disp["Benchmark Summary"] = bm_cols

    def style_category(df_in):
        formatted = pd.DataFrame(index=df_in.index, columns=df_in.columns)
        style_matrix = pd.DataFrame(
            "", index=df_in.index, columns=df_in.columns
        )

        for cat in df_in.index:
            cat_override = cat_bms.get(cat, {})
            eff_bm = {
                "Total Revenue (R$)": cat_override.get("total_revenue"),
                "Total Orders": cat_override.get("total_orders"),
                "Average Order Value (R$)": cat_override.get(
                    "average_order_value"
                ),
                "Price to Order Value (%)": 0.90,
                "Freight to Order Value (%)": 0.10,
                "Customer Repeat Rate": 0.009,
                "On-Time Delivery Rate": 0.90,
                "Average Delivery Days": cat_override.get(
                    "average_delivery_days", 8.8
                ),
                "Average Review Score": cat_override.get(
                    "average_review_score", 4.0
                ),
                "% Rating 1 & 2": 0.10,
            }

            for col in df_in.columns:
                val = df_in.loc[cat, col]
                if col == "Benchmark Summary":
                    formatted.loc[cat, col] = str(val)
                else:
                    is_curr = "Revenue" in col or "Value" in col
                    is_pct = (
                        "%" in col or "Rate" in col or "Ratio" in col
                    ) and ("Value" not in col)
                    formatted.loc[cat, col] = format_business_num(
                        val, is_currency=is_curr, is_pct=is_pct
                    )

                    target = eff_bm.get(col)
                    if target is not None and is_non_compliant(
                        col, val, target
                    ):
                        style_matrix.loc[cat, col] = RED_CELL_STYLE

        def apply_styles(x):
            df_st = pd.DataFrame("", index=x.index, columns=x.columns)
            for r in x.index:
                for c in x.columns:
                    if style_matrix.loc[r, c] != "":
                        df_st.loc[r, c] = style_matrix.loc[r, c]
            return df_st

        return formatted.style.apply(apply_styles, axis=None)

    st.dataframe(style_category(df_disp), use_container_width=True)


render_category_table(top_10_cats, "Top 10 Categories by Revenue")
render_category_table(bot_10_cats, "Bottom 10 Categories by Revenue")


# =============================================================================
# STEP 3: PoP REVENUE GAINERS & LOSERS VARIANCE
# =============================================================================
st.divider()
st.header("Step 3: Period-over-Period Revenue Variance")

current_period_count = len(selected_periods)
start_idx = available_periods.index(selected_periods[0])
prior_start_idx = max(0, start_idx - current_period_count)
prior_periods = available_periods[prior_start_idx:start_idx]

if len(prior_periods) > 0:
    df_prior = df_raw[df_raw[time_col].isin(prior_periods)]

    rev_curr = df_filtered.groupby("product_category_name_english")[
        "price"
    ].sum()
    rev_prev = df_prior.groupby("product_category_name_english")["price"].sum()

    var_df = pd.DataFrame({"Current": rev_curr, "Prior": rev_prev}).fillna(0)
    var_df["Delta"] = var_df["Current"] - var_df["Prior"]

    top_gainers = var_df.sort_values("Delta", ascending=False).head(top_n_gl)
    top_losers = var_df.sort_values("Delta", ascending=True).head(top_n_gl)
    variance_combined = pd.concat([top_gainers, top_losers]).drop_duplicates()

    fig_var, ax_var = plt.subplots(figsize=(10, 5))
    colors = [
        "#22c55e" if d >= 0 else "#ef4444" for d in variance_combined["Delta"]
    ]
    bars = ax_var.barh(
        variance_combined.index, variance_combined["Delta"], color=colors
    )

    for bar, delta in zip(bars, variance_combined["Delta"]):
        symbol = "▲" if delta >= 0 else "▼"
        text_str = f" {symbol} R$ {abs(delta):,.0f}"
        if delta >= 0:
            ax_var.text(
                bar.get_width(),
                bar.get_y() + bar.get_height() / 2,
                text_str,
                va="center",
                ha="left",
                color="#15803d",
                fontweight="bold",
            )
        else:
            ax_var.text(
                bar.get_width(),
                bar.get_y() + bar.get_height() / 2,
                text_str,
                va="center",
                ha="right",
                color="#991b1b",
                fontweight="bold",
            )

    ax_var.set_title(
        f"Top {top_n_gl} PoP Revenue Gainers & Losers (vs. Prior Equal Window)",
        fontweight="bold",
    )
    ax_var.set_xlabel("Revenue Variance (R$)")
    ax_var.axvline(0, color="black", linewidth=0.8)
    plt.tight_layout()
    st.pyplot(fig_var)
else:
    st.info("Insufficient historical periods to compute prior window variance.")


# =============================================================================
# STEP 4: CATEGORY ANALYTICS & DEDUPLICATED SLA TABLE
# =============================================================================
st.divider()
st.header("Step 4: Category Diagnostic & Deduplicated SLA Analytics")

selected_diag_cat = st.selectbox(
    "Select Category for Deep Dive", categories, index=default_cat_idx
)
df_cat_deep = df_filtered[
    df_filtered["product_category_name_english"] == selected_diag_cat
]

fig_r1, axes_r1 = plt.subplots(1, 2, figsize=(12, 4))
cat_rev_trend = df_cat_deep.groupby(time_col)["price"].sum()
axes_r1[0].plot(
    cat_rev_trend.index,
    cat_rev_trend.values,
    marker="o",
    color="#2563eb",
    linewidth=2,
)
axes_r1[0].set_title(
    f"Revenue Trend: {selected_diag_cat}", fontweight="bold"
)
axes_r1[0].set_ylabel("Revenue (R$)")
axes_r1[0].tick_params(axis="x", rotation=45)

ratings_dist = (
    df_cat_deep.groupby([time_col, "review_score"])
    .size()
    .unstack(fill_value=0)
)
for star in [1, 2, 3, 4, 5]:
    if star not in ratings_dist.columns:
        ratings_dist[star] = 0
ratings_dist = ratings_dist[[1, 2, 3, 4, 5]]
ratings_pct = ratings_dist.div(ratings_dist.sum(axis=1), axis=0).fillna(0)

bottoms = np.zeros(len(ratings_pct))
for idx, star in enumerate([1, 2, 3, 4, 5]):
    axes_r1[1].bar(
        ratings_pct.index,
        ratings_pct[star],
        bottom=bottoms,
        label=f"{star}★",
        color=STAR_GRADIENT[idx],
    )
    bottoms += ratings_pct[star].values

axes_r1[1].set_title("100% Stacked Review Score Distribution", fontweight="bold")
axes_r1[1].set_ylabel("Share")
axes_r1[1].tick_params(axis="x", rotation=45)
axes_r1[1].legend(loc="upper right", fontsize=8)

plt.tight_layout()
st.pyplot(fig_r1)

fig_r2, axes_r2 = plt.subplots(1, 2, figsize=(12, 4))
cat_vol = (
    df_cat_deep.drop_duplicates("order_id")
    .groupby(time_col)["order_id"]
    .nunique()
)
axes_r2[0].bar(cat_vol.index, cat_vol.values, color="#3b82f6")
axes_r2[0].set_title(
    f"Order Volume: {selected_diag_cat}", fontweight="bold"
)
axes_r2[0].set_ylabel("Orders")
axes_r2[0].tick_params(axis="x", rotation=45)

order_deliv = df_cat_deep.drop_duplicates("order_id").dropna(
    subset=["delivery_days"]
)
sns.boxplot(
    data=order_deliv,
    x=time_col,
    y="delivery_days",
    ax=axes_r2[1],
    color="#93c5fd",
)
axes_r2[1].set_ylim(0, deliv_y_max)
axes_r2[1].set_title(
    f"Delivery Days Distribution (Capped [0, {deliv_y_max}])",
    fontweight="bold",
)
axes_r2[1].set_ylabel("Days")
axes_r2[1].tick_params(axis="x", rotation=45)

plt.tight_layout()
st.pyplot(fig_r2)

st.subheader("Order-Level Deduplicated SLA Performance")


def build_sla_table(df_data):
    cat_counts = df_data.groupby("product_category_name_english")[
        "order_id"
    ].nunique()
    valid_cats = cat_counts[cat_counts >= min_orders].index

    df_sla_filtered = df_data[
        df_data["product_category_name_english"].isin(valid_cats)
    ]
    order_dedup = df_sla_filtered.drop_duplicates(
        ["order_id", "product_category_name_english"]
    )

    sla_res = []
    for cat, grp in order_dedup.groupby("product_category_name_english"):
        tot_ord = grp["order_id"].nunique()
        ontime_rate = grp["is_on_time"].mean()
        avg_rev = df_data[df_data["product_category_name_english"] == cat][
            "review_score"
        ].mean()
        deliv = grp["delivery_days"].dropna()

        p5 = deliv.quantile(0.05) if len(deliv) > 0 else np.nan
        mean_d = deliv.mean() if len(deliv) > 0 else np.nan
        p95 = deliv.quantile(0.95) if len(deliv) > 0 else np.nan

        sla_res.append(
            {
                "Category": cat,
                "Total Orders": tot_ord,
                "On-Time Rate": ontime_rate,
                "Avg Review Score": avg_rev,
                "P5 Delivery Days": p5,
                "Mean Delivery Days": mean_d,
                "P95 Delivery Days": p95,
            }
        )

    sla_df = pd.DataFrame(sla_res)
    if not sla_df.empty:
        worst_5 = sla_df.sort_values("On-Time Rate", ascending=True).head(5)[
            "Category"
        ]

        def highlight_worst(row):
            if row["Category"] in worst_5.values:
                return [RED_CELL_STYLE] * len(row)
            return [""] * len(row)

        formatted_sla = sla_df.copy()
        formatted_sla["Total Orders"] = formatted_sla["Total Orders"].apply(
            lambda x: f"{x:,.0f}"
        )
        formatted_sla["On-Time Rate"] = formatted_sla["On-Time Rate"].apply(
            lambda x: f"{x*100:.2f}%"
        )
        formatted_sla["Avg Review Score"] = formatted_sla[
            "Avg Review Score"
        ].apply(lambda x: f"{x:.2f}")
        formatted_sla["P5 Delivery Days"] = formatted_sla[
            "P5 Delivery Days"
        ].apply(lambda x: f"{x:.1f}")
        formatted_sla["Mean Delivery Days"] = formatted_sla[
            "Mean Delivery Days"
        ].apply(lambda x: f"{x:.1f}")
        formatted_sla["P95 Delivery Days"] = formatted_sla[
            "P95 Delivery Days"
        ].apply(lambda x: f"{x:.1f}")

        st.dataframe(
            formatted_sla.style.apply(highlight_worst, axis=1),
            use_container_width=True,
        )


build_sla_table(df_filtered)


# =============================================================================
# STEPS 5 & 6: BUYER & SELLER PROFILES & COHORT TRACKING
# =============================================================================
st.divider()
st.header("Steps 5 & 6: Buyer & Seller Profiles and Cohort Tracking")

col_b, col_s = st.columns(2)

with col_b:
    st.subheader("Top 10 Buyer States by Revenue")
    buyer_states = (
        df_filtered.groupby("customer_state")["price"]
        .sum()
        .nlargest(10)
        .sort_values()
    )
    fig_bs, ax_bs = plt.subplots(figsize=(6, 4))
    ax_bs.barh(buyer_states.index, buyer_states.values, color="#2563eb")
    ax_bs.set_xlabel("Revenue (R$)")
    plt.tight_layout()
    st.pyplot(fig_bs)

with col_s:
    st.subheader("Top 10 Seller States by Revenue")
    seller_states = (
        df_filtered.groupby("seller_state")["price"]
        .sum()
        .nlargest(10)
        .sort_values()
    )
    fig_ss, ax_ss = plt.subplots(figsize=(6, 4))
    ax_ss.barh(seller_states.index, seller_states.values, color="#3b82f6")
    ax_ss.set_xlabel("Revenue (R$)")
    plt.tight_layout()
    st.pyplot(fig_ss)

st.subheader("Cohort Growth Rates (Time Series Trend)")

top_buyers_cohort = (
    df_filtered.groupby("customer_unique_id")["price"]
    .sum()
    .nlargest(config["top_n_buyers"])
    .index
)
top_sellers_cohort = (
    df_filtered.groupby("seller_id")["price"]
    .sum()
    .nlargest(config["top_n_sellers"])
    .index
)

buyer_cohort_ts = (
    df_filtered[df_filtered["customer_unique_id"].isin(top_buyers_cohort)]
    .groupby(time_col)["price"]
    .sum()
    .pct_change()
    .dropna()
)
seller_cohort_ts = (
    df_filtered[df_filtered["seller_id"].isin(top_sellers_cohort)]
    .groupby(time_col)["price"]
    .sum()
    .pct_change()
    .dropna()
)

col_cg1, col_cg2 = st.columns(2)

with col_cg1:
    fig_bc, ax_bc = plt.subplots(figsize=(6, 4))
    if not buyer_cohort_ts.empty:
        b_colors = ["#22c55e" if v >= 0 else "#ef4444" for v in buyer_cohort_ts]
        bars_b = ax_bc.bar(
            range(len(buyer_cohort_ts)), buyer_cohort_ts * 100, color=b_colors, width=0.4
        )
        ax_bc.set_xticks(range(len(buyer_cohort_ts)))
        ax_bc.set_xticklabels(buyer_cohort_ts.index, rotation=45, ha="right")

        if len(buyer_cohort_ts) > 0:
            v_min = (buyer_cohort_ts * 100).min()
            v_max = (buyer_cohort_ts * 100).max()
            pad = max(abs(v_min), abs(v_max)) * 0.5 if max(abs(v_min), abs(v_max)) > 0 else 5
            ax_bc.set_ylim(min(v_min - pad, -8), max(v_max + pad, 8))

        for bar, v in zip(bars_b, buyer_cohort_ts):
            symbol = "▲" if v >= 0 else "▼"
            val_pct = v * 100
            y_pos = val_pct / 2.0
            ax_bc.text(
                bar.get_x() + bar.get_width() / 2.0,
                y_pos,
                f"{symbol} {abs(val_pct):.1f}%",
                ha="center",
                va="center",
                fontsize=8,
                fontweight="bold",
                color="white",
            )
    ax_bc.set_title(
        f"Top {config['top_n_buyers']} Buyers Cohort Growth",
        fontweight="bold",
    )
    ax_bc.set_ylabel("Growth Rate (%)")
    ax_bc.axhline(0, color="black", linewidth=0.8, linestyle="--")
    plt.tight_layout()
    st.pyplot(fig_bc)

with col_cg2:
    fig_sc, ax_sc = plt.subplots(figsize=(6, 4))
    if not seller_cohort_ts.empty:
        s_colors = ["#22c55e" if v >= 0 else "#ef4444" for v in seller_cohort_ts]
        bars_s = ax_sc.bar(
            range(len(seller_cohort_ts)), seller_cohort_ts * 100, color=s_colors, width=0.4
        )
        ax_sc.set_xticks(range(len(seller_cohort_ts)))
        ax_sc.set_xticklabels(seller_cohort_ts.index, rotation=45, ha="right")

        if len(seller_cohort_ts) > 0:
            v_min = (seller_cohort_ts * 100).min()
            v_max = (seller_cohort_ts * 100).max()
            pad = max(abs(v_min), abs(v_max)) * 0.5 if max(abs(v_min), abs(v_max)) > 0 else 5
            ax_sc.set_ylim(min(v_min - pad, -8), max(v_max + pad, 8))

        for bar, v in zip(bars_s, seller_cohort_ts):
            symbol = "▲" if v >= 0 else "▼"
            val_pct = v * 100
            y_pos = val_pct / 2.0
            ax_sc.text(
                bar.get_x() + bar.get_width() / 2.0,
                y_pos,
                f"{symbol} {abs(val_pct):.1f}%",
                ha="center",
                va="center",
                fontsize=8,
                fontweight="bold",
                color="white",
            )
    ax_sc.set_title(
        f"Top {config['top_n_sellers']} Sellers Cohort Growth",
        fontweight="bold",
    )
    ax_sc.set_ylabel("Growth Rate (%)")
    ax_sc.axhline(0, color="black", linewidth=0.8, linestyle="--")
    plt.tight_layout()
    st.pyplot(fig_sc)
