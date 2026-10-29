"""Tab 4: Score an order (plan revision 2, panels 4.1-4.4).

Held-out orders the serving rule alerts on, the facts known at carrier handover, both
predictions, and scenarios on the alert model's inputs. Inference only: the frozen
bundles score every row and nothing is fitted. No delivery date, order status or review
of the order is shown, because those are outcomes.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from dashboard_core import alerts, model_client
from dashboard_core.data import evidence_table

LOGISTICS_CUT = 0.10
FREIGHT_CUTS = (("Freight −20%", 0.20), ("Freight −30%", 0.30), ("Freight −50%", 0.50), ("Free shipping", 0.99))
ROUTE_INPUTS = ("route_recent_carrier_transit_days", "route_recent_delivery_days")
SCENARIO_LABEL = "Scenario on the model's inputs: an association, not the effect of the action."


def _alert_list() -> pd.Series | None:
    st.subheader("4.1 Alerted orders")
    st.caption(
        "Held-out (test-period) orders the serving rule alerts on: Pipeline B at 4/15 inside the seven "
        "states, Pipeline A at 1/6 elsewhere. Listed in the review order for when capacity is short "
        "(operational rule, not a measured result): B first by risk; then A by handover delay, longest "
        "first, with order value as the tie-break. Risks are the stored T1 predictions; no label is read."
    )
    queue = alerts.alert_queue()
    left, middle, right = st.columns(3)
    pipelines = left.multiselect("Model", ["B", "A"], default=["B", "A"], key="score_pipeline")
    states = middle.multiselect(
        "Customer state", sorted(queue["customer_state"].dropna().unique()), key="score_states"
    )
    categories = right.multiselect(
        "Category", sorted(queue["primary_category"].dropna().unique()), key="score_categories"
    )
    shown = queue[queue["pipeline"].isin(pipelines)]
    if states:
        shown = shown[shown["customer_state"].isin(states)]
    if categories:
        shown = shown[shown["primary_category"].isin(categories)]
    counts = queue.groupby("pipeline").size()
    cols = st.columns(3)
    cols[0].metric("Pipeline B alerts", f"{int(counts.get('B', 0)):,}")
    cols[1].metric("Pipeline A alerts", f"{int(counts.get('A', 0)):,}")
    cols[2].metric("Shown after filters", f"{len(shown):,}")
    table = shown[
        [
            "review_position", "order_id", "pipeline", "stored_risk", "customer_state", "seller_state",
            "primary_category", "total_price", "total_freight", "handover_delay_days",
        ]
    ].rename(columns={"stored_risk": "risk", "handover_delay_days": "handover delay (days)"})
    event = st.dataframe(
        table,
        width="stretch",
        hide_index=True,
        height=320,
        on_select="rerun",
        selection_mode="single-row",
        key="score_queue",
        column_config={"risk": st.column_config.NumberColumn(format="%.3f")},
    )
    if not len(shown):
        st.info("No alerted order matches the filters.")
        return None
    selected = event.selection.rows if event is not None else []
    position = selected[0] if selected else 0
    st.caption("Select a row to open the order; the first row is open by default.")
    return shown.iloc[position]


def _details(order: pd.Series) -> None:
    st.subheader("4.2 Order details (known at carrier handover)")
    records = alerts._records()
    record = records[records["order_id"] == order["order_id"]].iloc[0]
    place = alerts.places(str(record["customer_id"]), str(order.get("seller_id", "")))

    def show(value, kind="text") -> str:
        if value is None or (isinstance(value, float) and np.isnan(value)) or pd.isna(value):
            return "—"
        if kind == "money":
            return f"R\\$ {float(value):,.2f}"  # escaped: Streamlit reads $...$ as LaTeX
        if kind == "days":
            return f"{float(value):.1f} days"
        if kind == "time":
            return pd.Timestamp(value).strftime("%Y-%m-%d %H:%M")
        if kind == "count":
            return f"{int(value):,}"
        if kind == "share":
            return f"{float(value):.1%}"
        if kind == "score":
            return f"{float(value):.2f} / 5"
        return str(value)

    customer, seller, order_box = st.columns(3)
    with customer:
        st.markdown("**Customer**")
        st.write(f"Customer: `{str(record['customer_unique_id'])[:12]}…`")
        st.write(f"City, state: {place['customer_city'].title()}, {record['customer_state']}")
        st.write(f"Purchased: {show(record['purchase_ts'], 'time')}")
        st.write(f"Payment: {show(record['primary_payment_type'])}, {show(record['payment_installments_max'], 'count')} instalments")
    with seller:
        st.markdown("**Seller**")
        st.write(f"Seller: `{str(order.get('seller_id', ''))[:12]}…`")
        st.write(f"City, state: {str(place['seller_city']).title()}, {show(order.get('seller_state'))}")
        st.write(f"Prior average review: {show(record['seller_prior_review_mean'], 'score')} "
                 f"({show(record['seller_prior_review_count'], 'count')} earlier reviews)")
        st.write(f"Prior late-delivery share: {show(record['seller_prior_late_share'], 'share')}")
    with order_box:
        st.markdown("**Order and handover**")
        st.write(f"Total price: {show(record['total_price'], 'money')}; freight: {show(record['total_freight'], 'money')}")
        st.write(f"Shipping limit: {show(order.get('shipping_limit'), 'time')}")
        st.write(f"Handed to carrier: {show(order.get('handover_ts'), 'time')}")
        st.write(f"Dispatch: {show(order.get('dispatch_days'), 'days')}; "
                 f"handover delay: {show(order.get('handover_delay_days'), 'days')}")
        st.write(f"Distance: {show(round(float(record['distance_km_max']), 1) if pd.notna(record['distance_km_max']) else None)} km")
    st.markdown("**Items**")
    st.dataframe(alerts.order_items(str(order["order_id"])), width="stretch", hide_index=True)


def _scenario_rows(row: pd.DataFrame, pipeline: str, transit_saving: float | None) -> pd.DataFrame:
    frames = [row.assign(scenario="As is")]
    if pipeline == "B" and transit_saving is not None and all(c in row for c in ROUTE_INPUTS):
        faster = row.copy()
        for column in ROUTE_INPUTS:
            faster[column] = (faster[column] - transit_saving).clip(lower=0)
        frames.append(faster.assign(scenario="Logistics −10%"))
    for label, cut in FREIGHT_CUTS:
        cheaper = row.copy()
        for column in ("total_freight", "freight_ratio"):
            if column in cheaper:
                cheaper[column] = cheaper[column] * (1 - cut)
        frames.append(cheaper.assign(scenario=label))
    scenarios = pd.concat(frames, ignore_index=True)
    scenarios["order_id"] = scenarios["order_id"].astype(str) + "#" + scenarios["scenario"]
    return scenarios


def _predictions_and_scenarios(order: pd.Series) -> None:
    order_id = str(order["order_id"])
    pipeline = str(order["pipeline"])
    clf_row = alerts.model_rows("classification", (order_id,))
    reg_row = alerts.model_rows("regression", (order_id,))
    risk = model_client.predict("classification", clf_row).iloc[0]
    lead = model_client.predict("regression", reg_row).iloc[0]

    st.subheader("4.3 Predictions")
    badge = "Pipeline B" if risk["model"] == "B frozen" else (
        f"Pipeline A (outside B's scope: {str(risk['scope_reason']).replace('outside: ', '')})"
    )
    residuals = evidence_table("regression", "b09", "residuals_summary.csv")
    series = "B on B's test rows" if lead["model"] == "B frozen" else "A on A's test rows"
    band = residuals[residuals["series"] == series].iloc[0]
    purchase = pd.Timestamp(alerts._records().set_index("order_id").loc[order_id, "purchase_ts"])
    dispatch = order.get("dispatch_days")
    transit = None
    if pd.notna(lead["prediction"]) and pd.notna(dispatch):
        transit = max(float(lead["prediction"]) - float(dispatch), 0.0)

    top, bottom = st.columns(2), st.columns(2)
    cols = [top[0], top[1], bottom[0], bottom[1]]
    cols[0].metric("Alert risk", f"{risk['prediction']:.3f}")
    cols[0].caption(f"{badge}; threshold {risk['threshold']:.3f}; alert {'yes' if risk['alert'] else 'no'}")
    cols[1].metric("Predicted lead time", f"{lead['prediction']:.1f} days")
    cols[1].caption(
        f"Stored-residual band {lead['prediction'] + band['p05']:.1f}–{lead['prediction'] + band['p95']:.1f} days (p05–p95)"
    )
    cols[2].metric("Estimated arrival", (purchase + pd.Timedelta(days=float(lead["prediction"]))).strftime("%Y-%m-%d"))
    cols[2].caption("Purchase time plus the predicted lead time")
    cols[3].metric("Estimated transit", "—" if transit is None else f"{transit:.1f} days")
    cols[3].caption("Predicted lead time minus dispatch days (never below 0)")
    st.caption(f"Predictions from the {model_client.source_label()}; inference only, nothing is fitted.")

    st.subheader("4.4 Scenarios")
    st.warning(SCENARIO_LABEL)
    saving = None if transit is None else LOGISTICS_CUT * transit
    scenarios = _scenario_rows(clf_row, pipeline, saving)
    scored = model_client.predict("classification", scenarios)
    scored["scenario"] = scenarios["scenario"].to_numpy()
    issues = model_client.check("classification", scenarios)
    out = issues[issues["rule"] == "out of profile"] if len(issues) else issues
    by_row = out.groupby("order_id")["column"].apply(lambda c: sorted(set(c))).to_dict() if len(out) else {}
    base_id = scenarios.loc[scenarios["scenario"] == "As is", "order_id"].iloc[0]
    base_cols = set(by_row.get(base_id, []))

    def profile_note(order_key: str) -> str:
        cols = by_row.get(order_key, [])
        new = [c for c in cols if c not in base_cols]
        if new:
            return "new: " + ", ".join(new)
        return "as the order itself" if cols else ""
    base_risk = float(scored.loc[scored["scenario"] == "As is", "prediction"].iloc[0])
    result = pd.DataFrame(
        {
            "scenario": scored["scenario"],
            "risk": scored["prediction"].round(3),
            "change": (scored["prediction"] - base_risk).round(3),
            "alert still fires": np.where(scored["prediction"] >= scored["threshold"], "yes", "no"),
            "out-of-profile inputs": [profile_note(key) for key in scenarios["order_id"]],
        }
    )
    if saving is not None and pipeline == "B":
        arrival = purchase + pd.Timedelta(days=float(lead["prediction"]) - saving)
        result["estimated arrival"] = np.where(
            result["scenario"] == "Logistics −10%", arrival.strftime("%Y-%m-%d"), ""
        )
    st.dataframe(result, width="stretch", hide_index=True)
    if base_cols:
        st.caption("Out of profile already in the order itself (more than 4 SD from the training mean): "
                   + ", ".join(sorted(base_cols)) + ". \"new\" marks inputs a scenario pushed out of profile.")
    notes = [
        "Freight scenarios scale the order's freight and freight-to-price ratio. "
        "\"Free shipping\" is modelled as 99% off freight, because almost no order in the data had zero freight.",
    ]
    if pipeline == "B":
        notes.append(
            "Logistics −10% moves the estimated arrival earlier by 10% of the estimated transit "
            f"({'—' if saving is None else f'{saving:.1f} days'}) and cuts the route's recent carrier transit "
            "days and recent delivery days by the same days: the alert model has no input for this order's "
            "own transit, and its two route inputs are correlated."
        )
    else:
        notes.append("Logistics −10% is not shown: Pipeline A's alert model has no route inputs.")
    for note in notes:
        st.caption(note)


def render() -> None:
    st.header("Score an order")
    st.info("Inference on held-out orders with the frozen models. Nothing is fitted and no test label is read.")
    order = _alert_list()
    if order is None:
        return
    _details(order)
    _predictions_and_scenarios(order)
