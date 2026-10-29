"""Detractor-risk tab."""
from __future__ import annotations

import json

from dashboard_core import paths

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from dashboard_core.charts import bar_chart, dual_line_chart, horizontal_bar_chart
from dashboard_core.data import build_scoring_rows, evidence_table, scoring_order_ids
from dashboard_core.routing import B_STATES, DashboardRelease


def _scope_banner(config: dict) -> None:
    counts = config["test_rows_by_scope"]
    st.info(
        "Orders in the seven states are scored by Pipeline B (improved model). "
        "All other orders are scored by Pipeline A (baseline model). Every prediction "
        "shows which model made it."
    )
    left, right = st.columns(2)
    left.metric("Test orders inside B's scope", f"{counts['inside']:,}")
    right.metric("Test orders outside B's scope", f"{counts['outside']:,}")
    st.caption("B10.3 · validation = selection score; test = read once.")


def _headline() -> None:
    st.subheader("3.1 Headline")
    table = evidence_table("classification", "b09", "train_val_test.csv")
    pairs = evidence_table("classification", "b09", "paired_test_differences.csv")
    metrics = evidence_table("classification", "t1_joint_test", "metrics_test.csv")
    b = table[(table["model"] == "B frozen") & (table["rows"] == "B test rows")].set_index("metric")
    a = table[(table["model"] == "A frozen") & (table["rows"] == "B test rows")].set_index("metric")
    prevalence = metrics[
        (metrics["model"] == "B frozen")
        & (metrics["rows"] == "B test rows")
        & (metrics["metric"] == "prevalence")
    ]["value"].iloc[0]

    diff = pairs[
        (pairs["comparison"] == "B frozen minus A frozen")
        & (pairs["rows"] == "B test rows")
        & (pairs["metric"] == "ap")
    ].iloc[0]
    cols = st.columns(6)
    for column, metric, label in zip(
        cols[:3],
        ("ap", "roc_auc", "brier"),
        ("AP", "ROC-AUC", "Brier"),
    ):
        column.metric(f"B {label}", f"{b.loc[metric, 'test']:.3f}")
        column.caption(
            f"95% CI {b.loc[metric, 'test_ci_low']:.3f}–{b.loc[metric, 'test_ci_high']:.3f}"
        )
    cols[3].metric("A AP on same orders", f"{a.loc['ap', 'test']:.3f}")
    cols[4].metric("B minus A (AP)", f"{diff['difference']:+.4f}")
    cols[4].caption(f"95% CI {diff['ci_low']:+.4f} to {diff['ci_high']:+.4f}")
    cols[5].metric("Detractor prevalence", f"{prevalence:.1%}")
    compare = pairs[
        (pairs["comparison"] == "B frozen minus A frozen")
        & (pairs["rows"] == "B test rows")
    ]
    st.dataframe(compare, width="stretch", hide_index=True)


def _fit_over_time() -> None:
    st.subheader("3.2 Fit over time")
    table = evidence_table("classification", "t1_joint_test", "fold_and_test_table.csv")
    chart = table[["period", "A_on_B_rows", "B_on_B_rows"]].rename(
        columns={"A_on_B_rows": "A on B rows", "B_on_B_rows": "B on B rows"}
    )
    dual_line_chart(
        chart,
        "period",
        ["A on B rows", "B on B rows"],
        "Validation folds and test — stored primary metric",
        "Metric",
    )
    st.dataframe(table, width="stretch", hide_index=True)
    st.caption("T1.6 · validation = selection score; test = read once.")


def _curves() -> None:
    st.subheader("3.3 Curves")
    image = paths.t1_output("classification", "figures/test_curves.png")
    if image.is_file():
        st.image(str(image), caption="T1.4 · stored PR, ROC and reliability curves")


def _stored_threshold_choices(curve: pd.DataFrame) -> list[float]:
    values = sorted({float(value) for value in curve["threshold"].dropna()})

    def nearest(target: float) -> float:
        return min(values, key=lambda value: abs(value - target))

    candidates = list(np.arange(0.02, 0.6001, 0.01)) + [1 / 6, 4 / 15]
    return sorted({nearest(float(value)) for value in candidates})


def _threshold_label(value: float) -> str:
    if np.isclose(value, 4 / 15, atol=1e-4):
        return "4/15 (operating)"
    if np.isclose(value, 1 / 6, atol=1e-4):
        return "1/6 (frozen)"
    return f"{value:.2f}"


def _counts_row(stats: pd.Series) -> None:
    """TP, FP and FN on their own row, so the full counts are readable."""
    cols = st.columns(3)
    for column, key, label in zip(cols, ("tp", "fp", "fn"), ("True positives", "False positives", "False negatives")):
        column.metric(label, "-" if pd.isna(stats[key]) else f"{int(stats[key]):,}")


def _alert_statistics() -> float:
    st.subheader("3.4 Alert work statistics")
    st.caption("B9.10 / B10.3 · Validation is the selection view; test is post-test only.")
    curve = evidence_table("classification", "b09", "threshold_options_curve.csv")
    results = evidence_table("classification", "b10", "threshold_results.csv")
    view = st.radio(
        "View",
        ["Validation", "Test (post-test view)"],
        horizontal=True,
        key="classification_threshold_view",
    )
    period = "validation (out-of-fold)" if view == "Validation" else "test (post-test view)"
    if view != "Validation":
        st.caption("post-test view; the threshold was not chosen on it")
    b_curve = curve[curve["period"] == period].sort_values("threshold")

    choices = _stored_threshold_choices(b_curve)
    selected = st.select_slider(
        "B threshold (seven states)",
        options=choices,
        value=min(choices, key=lambda value: abs(value - 4 / 15)),
        format_func=_threshold_label,
        key="classification_threshold",
    )
    row = b_curve.iloc[(b_curve["threshold"] - selected).abs().argmin()]

    a_row = results[
        (results["model"] == "A frozen")
        & results["rows"].str.startswith("validation" if view == "Validation" else "test")
    ].iloc[0]
    combined_row = results[
        (results["model"] == "B frozen + A frozen")
        & results["rows"].str.startswith("validation" if view == "Validation" else "test")
    ].iloc[0]

    st.markdown("**B — seven states**")
    cols = st.columns(6)
    cols[0].metric("Alerts/day", f"{row['alerts_per_day']:.2f}")
    cols[1].metric("Precision", f"{row['precision']:.1%}")
    cols[2].metric("Recall", f"{row['recall']:.1%}")
    cols[3].metric("FP per TP", f"{row['fp_per_tp']:.2f}")
    cols[4].metric("Cost 5:1", f"{row['cost_5_to_1']:,.0f}")
    cols[5].metric("Cost 1:1", f"{row['cost_1_to_1']:,.0f}")
    _counts_row(row)

    st.markdown("**A — other orders, fixed at 1/6**")
    a_cols = st.columns(6)
    a_cols[0].metric("Alerts/day", f"{a_row['alerts_per_day']:.2f}")
    a_cols[1].metric("Precision", f"{a_row['precision']:.1%}")
    a_cols[2].metric("Recall", f"{a_row['recall']:.1%}")
    a_cols[3].metric("FP per TP", "-" if pd.isna(a_row["fp_per_tp"]) else f"{a_row['fp_per_tp']:.2f}")
    a_cols[4].metric("Cost 5:1", "-" if pd.isna(a_row["cost_5_to_1"]) else f"{a_row['cost_5_to_1']:,.0f}")
    a_cols[5].metric("Cost 1:1", "-" if pd.isna(a_row["cost_1_to_1"]) else f"{a_row['cost_1_to_1']:,.0f}")
    _counts_row(a_row)

    st.markdown("**Combined serving rule**")
    if np.isclose(selected, 4 / 15):
        st.metric("Combined alerts/day", f"{combined_row['alerts_per_day']:.2f}")
        st.dataframe(pd.DataFrame([combined_row]), width="stretch", hide_index=True)
    else:
        combined = float(row["alerts_per_day"] + a_row["alerts_per_day"])
        st.metric("Combined alerts/day", f"{combined:.2f}")
        st.caption(
            "Derived for display: B alerts/day at the selected threshold plus "
            "A alerts/day at 1/6. Combined cost is unavailable at this threshold."
        )

    fig, axis = plt.subplots(figsize=(10, 4))
    axis.plot(b_curve["threshold"], b_curve["precision"], label="Precision", color="#2563eb")
    axis.plot(b_curve["threshold"], b_curve["recall"], label="Recall", color="#dc2626")
    axis.axvline(selected, color="#111827", linestyle="--", linewidth=1.2, label="Chosen threshold")
    axis.set_xlabel("Threshold")
    axis.set_ylabel("Precision / recall")
    axis2 = axis.twinx()
    axis2.plot(
        b_curve["threshold"],
        b_curve["alerts_per_day"],
        label="Alerts/day",
        color="#f59e0b",
    )
    cap = json.loads(paths.serving_config_path("classification").read_text(encoding="utf-8"))[
        "review_alert_cap_per_day"
    ]
    axis2.axhline(cap, color="#7c3aed", linestyle=":", linewidth=1.2, label=f"{cap}/day review cap (B only)")
    axis2.set_ylabel("Alerts/day")
    lines = axis.get_legend_handles_labels()
    lines2 = axis2.get_legend_handles_labels()
    axis.legend(lines[0] + lines2[0], lines[1] + lines2[1], loc="best", fontsize=8)
    fig.tight_layout()
    st.pyplot(fig, width="stretch")
    plt.close(fig)

    alerts = pd.DataFrame(
        {
            "model": ["Pipeline B", "Pipeline A"],
            "alerts_per_day": [
                float(row["alerts_per_day"]),
                float(a_row["alerts_per_day"]),
            ],
        }
    )
    bar_chart(
        alerts,
        "model",
        "alerts_per_day",
        "Alerts per day under the serving rule",
        "Alerts/day",
    )
    if np.isclose(selected, 4 / 15):
        view_label = "validation" if view == "Validation" else "test (post-test view)"
        st.info(
            f"The {cap}-a-day review cap applies to Pipeline B's alerts: B sends "
            f"{row['alerts_per_day']:.2f} a day at 4/15 ({view_label}). The combined volume, "
            f"{combined_row['alerts_per_day']:.2f} a day, includes A's fallback and is higher, "
            "as the team accepted."
        )
    st.info(
        "Alert review order when capacity is short (operational rule, not a measured result): "
        "Pipeline B alerts at 4/15 first; then Pipeline A fallback alerts, reviewed at carrier "
        "handover, by handover delay (longest first), with order value as the tie-break."
    )
    return float(selected)


def _missed_dispatch() -> None:
    st.subheader("3.5 Missed-dispatch rule")
    table = evidence_table("classification", "b09", "missed_dispatch_rule_test.csv")
    st.dataframe(table, width="stretch", hide_index=True)


def _operational_priorities() -> None:
    st.subheader("3.7 Operational priorities")
    top = evidence_table("classification", "b10", "top_routes_categories.csv")
    routes = evidence_table("classification", "b09", "business_by_route.csv")
    quarter = st.selectbox("Quarter", sorted(top["window"].unique()), key="classification_quarter")
    window = top[top["window"] == quarter]
    left, right = st.columns(2)
    with left:
        route = window[window["dimension"] == "route_seller_to_customer_state"]
        bar_chart(route, "level", "outcome", "Top routes — observed detractor share", "Share")
        st.dataframe(route, width="stretch", hide_index=True)
    with right:
        category = window[window["dimension"] == "primary_category"]
        bar_chart(
            category,
            "level",
            "outcome",
            "Top categories — observed detractor share",
            "Share",
            "#f59e0b",
        )
        st.dataframe(category, width="stretch", hide_index=True)
    st.markdown("**All routes on the test period**")
    st.dataframe(routes, width="stretch", hide_index=True)


def _detractors_by_state() -> None:
    st.subheader("3.6 Detractors by state")
    table = evidence_table("classification", "b09", "subgroups.csv")
    fallback = evidence_table("classification", "b09", "a_fallback_by_scope.csv")
    states = table[
        (table["slice"] == "customer_state") & table["value"].isin(sorted(B_STATES))
    ][["value", "orders", "detractors"]].copy()
    states["share"] = states["detractors"] / states["orders"]
    other = fallback[
        (fallback["period"] == "test") & (fallback["scope"] == "outside B's scope")
    ].iloc[0]
    states.loc[len(states)] = {
        "value": "Other states",
        "orders": other["orders"],
        "detractors": other["detractors"],
        "share": other["detractors"] / other["orders"],
    }
    states = states.rename(columns={"value": "state", "share": "detractor_share"})
    bar_chart(
        states,
        "state",
        "detractor_share",
        "Detractor share by state",
        "Share",
        "#dc2626",
    )
    st.dataframe(states, width="stretch", hide_index=True)
    st.caption("Detractor share is derived for display from stored counts.")


def _why() -> None:
    st.subheader("3.8 Why")
    importance = evidence_table("classification", "b09", "permutation_importance.csv")
    coefficients = evidence_table("classification", "b09", "coefficients.csv")
    sensitivity = evidence_table("classification", "b09", "label_sensitivity.csv")
    horizontal_bar_chart(
        importance,
        "feature",
        "importance_mean",
        "Permutation importance",
        "Mean importance",
    )
    st.dataframe(importance, width="stretch", hide_index=True)
    st.markdown("**Odds ratios and reading note**")
    st.dataframe(coefficients, width="stretch", hide_index=True)
    st.markdown("**Label sensitivity**")
    st.dataframe(sensitivity, width="stretch", hide_index=True)


def _score_one(
    frame: pd.DataFrame,
    router: DashboardRelease,
    b_threshold: float,
) -> tuple[pd.Series, str]:
    scored = router.predict(frame).iloc[0]
    model_code = "B" if scored["model"] == "B frozen" else "A"
    threshold = b_threshold if model_code == "B" else router.threshold["A"]
    scored["threshold"] = threshold
    if scored["status"] == "scored":
        scored["alert"] = bool(scored["prediction"] >= threshold)
    return scored, model_code


def _score_order(b_threshold: float) -> None:
    st.subheader("3.9 Score an order")
    st.caption("Inference only: frozen bundles are used; nothing is fitted.")
    upload = st.file_uploader("Upload a CSV of held-out feature rows", type=["csv"], key="clf_score_upload")
    if upload is not None:
        frame = pd.read_csv(upload)
        if "order_id" not in frame:
            st.error("The CSV must include an order_id column.")
            return
        router = DashboardRelease("classification")
        scored = router.predict(frame)
        scored["threshold"] = np.where(
            scored["model"] == "B frozen",
            b_threshold,
            router.threshold["A"],
        )
        scored["alert"] = np.where(
            scored["status"] == "scored",
            scored["prediction"] >= scored["threshold"],
            np.nan,
        )
        st.dataframe(scored, width="stretch", hide_index=True)
        st.download_button(
            "Download scored CSV",
            scored.to_csv(index=False).encode("utf-8"),
            "classification_scored.csv",
            "text/csv",
            key="clf_download",
        )
        return

    if not st.checkbox("Load held-out order picker", key="classification_load_scores"):
        st.caption("Enable the picker to prepare frozen-model inputs from held-out orders.")
        return
    with st.spinner("Preparing held-out feature rows…"):
        frame = build_scoring_rows("classification")
    choices = scoring_order_ids("classification")
    order_id = st.selectbox("Held-out order", choices, key="classification_order")
    base_frame = frame[frame["order_id"].astype(str) == order_id].iloc[[0]].copy()
    router = DashboardRelease("classification")
    base, model_code = _score_one(base_frame, router, b_threshold)
    badge = (
        "Pipeline B"
        if model_code == "B"
        else f"Pipeline A (outside B's scope: {base['scope_reason'].replace('outside: ', '')})"
    )

    if base["status"] != "scored":
        st.warning(
            "Not scored yet: scored at carrier handover. If the shipping limit passes "
            "without handover, the missed-dispatch rule flags it."
        )
        return
    st.metric("Risk score", f"{base['prediction']:.3f}")
    st.write(f"**Model:** {badge}")
    st.write(f"**Threshold:** {base['threshold']:.4f}")
    st.write(f"**Alert:** {'yes' if base['alert'] else 'no'}")

    issues = router.check(base_frame)
    if len(issues):
        st.warning("Input-check messages")
        st.dataframe(issues, width="stretch", hide_index=True)


def _data_health() -> None:
    st.subheader("3.10 Data health and transparency")
    drift = evidence_table("classification", "b09", "drift.csv")
    fallback = evidence_table("classification", "b09", "a_fallback_by_scope.csv")
    config = json.loads(paths.serving_config_path("classification").read_text(encoding="utf-8"))
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


def _score_pointer(panel: str) -> None:
    st.subheader(f"{panel} Score an order")
    st.info("Scoring moved to the Score an order tab (plan revision 2): alerted held-out orders, "
            "their details, both predictions and scenarios.")


def render() -> None:
    st.header("Detractor risk at handover")
    config = json.loads(paths.serving_config_path("classification").read_text(encoding="utf-8"))
    _scope_banner(config)
    _headline()
    _fit_over_time()
    _curves()
    threshold = _alert_statistics()
    _missed_dispatch()
    _detractors_by_state()
    _operational_priorities()
    _why()
    _score_pointer("3.9")
    _data_health()

