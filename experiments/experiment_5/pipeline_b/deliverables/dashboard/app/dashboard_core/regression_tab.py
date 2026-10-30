"""Delivery lead-time tab."""
from __future__ import annotations

import streamlit as st

from dashboard_core import paths
from dashboard_core.charts import bar_chart, dual_line_chart, horizontal_bar_chart, line_chart
from dashboard_core.data import evidence_table
from dashboard_core.loaders import load_bundle_schema


def _scope_banner(config: dict) -> None:
    counts = config["test_rows_by_scope"]
    st.info(
        "Orders in the seven states are scored by Pipeline B (improved model). "
        "All other orders are scored by Pipeline A (baseline model). Every prediction "
        "shows which model made it."
    )
    cols = st.columns(2)
    cols[0].metric("Test orders inside B's scope", f"{counts['inside']:,}")
    cols[1].metric("Test orders outside B's scope", f"{counts['outside']:,}")
    st.caption("B10.3 · test rows by scope · validation = selection score; test = read once.")


def _headline() -> None:
    table = evidence_table("regression", "b09", "train_val_test.csv")
    pairs = evidence_table("regression", "b09", "paired_test_differences.csv")
    b = table[(table["model"] == "B frozen") & (table["rows"] == "B test rows")].set_index("metric")
    a = table[(table["model"] == "A frozen") & (table["rows"] == "B test rows")].set_index("metric")

    st.subheader("2.1 Headline")
    st.caption("Validation = selection score; test = read once. B10.3 / B9.1–B9.2.")
    diff = pairs[
        (pairs["comparison"] == "B frozen minus A frozen")
        & (pairs["rows"] == "B test rows")
        & (pairs["metric"] == "mae")
    ].iloc[0]
    cols = st.columns(5)
    cols[0].metric("B MAE (days)", f"{b.loc['mae', 'test']:.2f}")
    cols[0].caption(f"95% CI {b.loc['mae', 'test_ci_low']:.2f}–{b.loc['mae', 'test_ci_high']:.2f}")
    cols[1].metric("A MAE on same orders", f"{a.loc['mae', 'test']:.2f}")
    cols[2].metric("B minus A (days)", f"{diff['difference']:+.3f}")
    cols[2].caption(f"95% CI {diff['ci_low']:+.3f} to {diff['ci_high']:+.3f}")
    cols[3].metric("Within ±3 days", f"{b.loc['within_3d', 'test']:.1%}")
    cols[4].metric("Test rows", f"{int(b.loc['mae', 'test_rows']):,}")

    compare = pairs[
        (pairs["comparison"].isin(["B frozen minus A frozen", "B frozen minus B dummy"]))
        & (pairs["rows"] == "B test rows")
    ]
    st.dataframe(compare, width="stretch", hide_index=True)


def _promise_buffer() -> None:
    st.subheader("2.4 Promise buffer")
    st.caption("B12.2 · The highlighted decision panel for setting delivery promises.")
    curve = evidence_table("regression", "b12", "buffer_curve.csv")
    choice = evidence_table("regression", "b12", "buffer_choice.csv")
    state = evidence_table("regression", "b12", "buffer_by_state.csv")
    series = st.selectbox("View", sorted(curve["series"].dropna().unique()), key="buffer_series")
    selected = curve[curve["series"] == series]
    line_chart(
        selected,
        "buffer_days",
        "share_late",
        f"Share late against buffer — {series}",
        "Share late",
    )
    st.dataframe(choice, width="stretch", hide_index=True)
    st.dataframe(state, width="stretch", hide_index=True)
    image = paths.b12_output("regression", "figures/buffer_curve.png")
    if image.is_file():
        st.image(str(image), caption="Stored B12 buffer curve")


def _operational_priorities() -> None:
    st.subheader("2.6 Operational priorities")
    st.caption("B10.7 / B9.13 · Observed outcomes; coefficient shown beside as model attribution.")
    top = evidence_table("regression", "b10", "top_routes_categories.csv")
    routes = evidence_table("regression", "b09", "business_by_route.csv")
    quarter = st.selectbox("Quarter", sorted(top["window"].unique()), key="regression_quarter")
    window = top[top["window"] == quarter]
    left, right = st.columns(2)
    with left:
        route = window[window["dimension"] == "route_seller_to_customer_state"]
        bar_chart(route, "level", "outcome", "Top routes — observed mean lead time", "Days")
        st.dataframe(route, width="stretch", hide_index=True)
    with right:
        category = window[window["dimension"] == "primary_category"]
        bar_chart(
            category,
            "level",
            "outcome",
            "Top categories — observed mean lead time",
            "Days",
            "#f59e0b",
        )
        st.dataframe(category, width="stretch", hide_index=True)
    st.markdown("**All routes on the test period**")
    st.dataframe(routes, width="stretch", hide_index=True)


def _accuracy_by_segment() -> None:
    st.subheader("2.5 Where it errs")
    st.caption(
        "B9.3 · RMSE is not stored in the subgroup table, so only stored MAE is shown. "
        "Slices under 100 orders are marked too few to judge."
    )
    table = evidence_table("regression", "b09", "subgroups.csv")
    slice_name = st.selectbox(
        "Segment",
        sorted(table["slice"].dropna().unique()),
        key="regression_slice",
    )
    selected = table[table["slice"] == slice_name].copy()
    selected["label"] = selected["value"].astype(str)
    import matplotlib.pyplot as plt

    fig, axis = plt.subplots(figsize=(10, 4))
    axis.bar(
        selected["label"],
        selected["gain_B_minus_A"],
        color="#2563eb",
    )
    axis.axhline(0, color="#111827", linewidth=0.8)
    axis.set_title(f"B minus A MAE by {slice_name}")
    axis.set_ylabel("MAE difference (days)")
    axis.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    st.pyplot(fig, width="stretch")
    plt.close(fig)
    st.dataframe(selected, width="stretch", hide_index=True)


def _why() -> None:
    st.subheader("2.7 Why")
    importance = evidence_table("regression", "b09", "permutation_importance.csv")
    coefficients = evidence_table("regression", "b09", "coefficients.csv")
    horizontal_bar_chart(
        importance,
        "feature",
        "importance_mean",
        "Permutation importance",
        "Mean importance",
    )
    st.dataframe(importance, width="stretch", hide_index=True)
    st.markdown("**Coefficients as ratio per unit**")
    st.dataframe(coefficients, width="stretch", hide_index=True)
    st.caption("B9.5 · Coefficients describe the frozen model; they are not causal effects.")


def _fit_over_time() -> None:
    st.subheader("2.2 Fit over time")
    table = evidence_table("regression", "t1_joint_test", "fold_and_test_table.csv")
    chart = table[["period", "A_on_B_rows", "B_on_B_rows"]].rename(
        columns={"A_on_B_rows": "A on B rows", "B_on_B_rows": "B on B rows"}
    )
    dual_line_chart(
        chart,
        "period",
        ["A on B rows", "B on B rows"],
        "Validation folds and test — stored MAE",
        "MAE (days)",
    )
    st.dataframe(table, width="stretch", hide_index=True)
    st.caption("T1.6 · validation = selection score; test = read once.")


def _prediction_miss() -> None:
    st.subheader("2.3 Errors")
    image = paths.t1_output("regression", "figures/test_errors.png")
    if image.is_file():
        st.image(str(image), caption="T1.3 · stored error distribution")
    table = evidence_table("regression", "b09", "residuals_summary.csv")
    st.dataframe(table, width="stretch", hide_index=True)


def _data_health() -> None:
    st.subheader("2.8 Data health and transparency")
    drift = evidence_table("regression", "b09", "drift.csv")
    fallback = evidence_table("regression", "b09", "a_fallback_by_scope.csv")
    serving = paths.serving_config_path("regression")
    import json

    config = json.loads(serving.read_text(encoding="utf-8"))
    schema_a = load_bundle_schema("regression", "A")
    schema_b = load_bundle_schema("regression", "B")
    st.caption(
        f"Bundle model versions: A sklearn {schema_a['versions']['sklearn']}; "
        f"B sklearn {schema_b['versions']['sklearn']}."
    )
    st.markdown("**Drift between development and test**")
    st.dataframe(drift, width="stretch", hide_index=True)
    st.markdown("**A fallback inside vs outside B scope**")
    st.dataframe(fallback, width="stretch", hide_index=True)
    st.write(
        f"Out-of-profile warning rule: **{config['out_of_profile']['sd']} standard deviations**; "
        "warning only, the order is still scored."
    )
    st.warning(
        "Model version, release tag and training-period start/end are requested by the plan "
        "but are not present in the mapped serving_config.json source."
    )


def render() -> None:
    st.header("Delivery lead time")
    config = __import__("json").loads(
        paths.serving_config_path("regression").read_text(encoding="utf-8")
    )
    _scope_banner(config)
    _headline()
    _fit_over_time()
    _prediction_miss()
    _promise_buffer()
    _accuracy_by_segment()
    _operational_priorities()
    _why()
    _data_health()

