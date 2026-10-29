"""Alerted held-out orders for the Score an order tab (plan revision 2, panel 4.1-4.2).

The alert list is read from T1's stored test predictions (order_id, model, rows and
y_pred only; the label column y_true is never read) and the serving rule's thresholds.
Model inputs for the listed orders are rebuilt with the frozen T1 row builder, with
every label column excluded, exactly as the score panels do. Nothing is fitted.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
import streamlit as st

from dashboard_core import paths
from dashboard_core.routing import in_scope, load_release

LABEL_COLUMNS = frozenset(
    {"lead_days", "lead_label_ts", "is_detractor", "is_detractor_first", "review_label_ts"}
)
# Known only after delivery or review: never shown on the tab.
OUTCOME_COLUMNS = frozenset(
    {"order_estimated_delivery_date", "est_delivery_days", "eligible_regression", "eligible_classification"}
)
RECORDS_PATH = paths.E5 / "stages" / "s02_data" / "common" / "outputs" / "records.csv.gz"
RAW_DIR = paths.REPO / "data" / "raw"


@st.cache_data(show_spinner=False)
def _records() -> pd.DataFrame:
    frame = pd.read_csv(
        RECORDS_PATH,
        usecols=lambda column: column not in LABEL_COLUMNS,
        low_memory=False,
    )
    frame["purchase_ts"] = pd.to_datetime(frame["purchase_ts"], errors="coerce")
    return frame


@st.cache_data(show_spinner=False)
def _stored_alert_predictions() -> pd.DataFrame:
    """Stored classification test predictions, without the label column."""
    return pd.read_csv(
        paths.t1_output("classification", "predictions_test.csv.gz"),
        usecols=["order_id", "model", "rows", "y_pred"],
        low_memory=False,
    )


@st.cache_data(show_spinner=False)
def alerted_order_ids() -> pd.DataFrame:
    """order_id, model and stored risk of every held-out order the serving rule alerts on.

    B frozen on B's test rows at B's operating threshold; A frozen at its frozen
    threshold on the test orders outside B's scope.
    """
    threshold = load_release("classification").threshold
    stored = _stored_alert_predictions()
    b = stored[(stored["model"] == "B frozen") & (stored["rows"] == "B test rows")]
    b = b[b["y_pred"] >= threshold["B"]].assign(pipeline="B", threshold=threshold["B"])

    a_all = stored[(stored["model"] == "A frozen") & (stored["rows"] == "A test rows")]
    records = _records()
    a_records = records[records["order_id"].isin(a_all["order_id"])]
    outside = set(a_records.loc[~in_scope(a_records).to_numpy(), "order_id"])
    a = a_all[a_all["order_id"].isin(outside) & (a_all["y_pred"] >= threshold["A"])]
    a = a.assign(pipeline="A", threshold=threshold["A"])

    return (
        pd.concat([b, a], ignore_index=True)
        .rename(columns={"y_pred": "stored_risk"})[["order_id", "pipeline", "stored_risk", "threshold"]]
    )


@st.cache_data(show_spinner=False)
def _events() -> pd.DataFrame:
    from e5lib.paths import raw_data_dir
    from e5b import history
    from e5b.t1_joint_test import EVENTS_UNTIL

    return history.load_events(raw_data_dir(), EVENTS_UNTIL)


def _lead_cap() -> float:
    log = paths.evidence_output("regression", "b02", "feature_build_log.json")
    return float(json.loads(log.read_text(encoding="utf-8"))["lead_cap_days"])


@st.cache_data(show_spinner=False)
def model_rows(task: str, order_ids: tuple[str, ...]) -> pd.DataFrame:
    """Model inputs for the given held-out orders, rebuilt with the frozen T1 row builder."""
    from e5b.t1_joint_test import b_rows

    records = _records()
    base = records[records["order_id"].isin(order_ids)].copy()
    base["lead_days"] = np.nan
    base["lead_label_ts"] = pd.NaT
    base["review_label_ts"] = pd.NaT
    cap = _lead_cap() if task == "regression" else None
    built, _ = b_rows(task, base, _events(), cap)
    extra = [column for column in built.columns if column not in base.columns or column == "order_id"]
    return base.merge(built[extra].drop_duplicates("order_id"), on="order_id", how="left").reset_index(drop=True)


@st.cache_data(show_spinner=True)
def alert_queue() -> pd.DataFrame:
    """The alert list with the facts known at handover, in the review order (plan 6a, report section 9).

    Pipeline B's alerts first, by risk; then Pipeline A's, by handover delay (longest
    first) with order value as the tie-break.
    """
    alerts = alerted_order_ids()
    records = _records()
    keep = [
        "order_id", "purchase_ts", "customer_state", "primary_category",
        "total_price", "total_freight", "seller_prior_review_mean",
    ]
    queue = alerts.merge(records[keep], on="order_id", how="left").merge(
        handover_facts(), on="order_id", how="left"
    )
    queue["review_rank"] = np.where(queue["pipeline"] == "B", 0, 1)
    queue = queue.sort_values(
        ["review_rank", "stored_risk", "handover_delay_days", "total_price"],
        ascending=[True, False, False, False],
    )
    # Inside A's group the order is delay, then value; risk only breaks remaining ties.
    a = queue[queue["pipeline"] == "A"].sort_values(
        ["handover_delay_days", "total_price", "stored_risk"], ascending=[False, False, False]
    )
    queue = pd.concat([queue[queue["pipeline"] == "B"], a], ignore_index=True)
    queue.insert(0, "review_position", np.arange(1, len(queue) + 1))
    return queue.drop(columns=["review_rank"])


@st.cache_data(show_spinner=False)
def handover_facts() -> pd.DataFrame:
    """Seller, handover time, shipping limit, handover delay and dispatch days for every order.

    From the frozen history events (e5b.history); the delivery time they also hold is
    an outcome and is dropped here.
    """
    events = _events()
    return events[["order_id", "seller_id", "seller_state", "carrier_ts", "ship_limit", "h_days", "dispatch"]].rename(
        columns={"carrier_ts": "handover_ts", "ship_limit": "shipping_limit", "h_days": "handover_delay_days",
                 "dispatch": "dispatch_days"}
    ).drop_duplicates("order_id")


@st.cache_data(show_spinner=False)
def order_items(order_id: str) -> pd.DataFrame:
    """The order's items: category, seller, price, freight, size (all known at checkout)."""
    items = pd.read_csv(RAW_DIR / "olist_order_items_dataset.csv")
    items = items[items["order_id"] == order_id]
    products = pd.read_csv(RAW_DIR / "olist_products_dataset.csv")
    names = pd.read_csv(RAW_DIR / "product_category_name_translation.csv")
    items = items.merge(products, on="product_id", how="left").merge(names, on="product_category_name", how="left")
    items["volume_cm3"] = items["product_length_cm"] * items["product_height_cm"] * items["product_width_cm"]
    return items[
        [
            "order_item_id", "product_category_name_english", "seller_id", "price", "freight_value",
            "product_weight_g", "volume_cm3", "shipping_limit_date",
        ]
    ].rename(columns={"product_category_name_english": "category"})


@st.cache_data(show_spinner=False)
def places(customer_id: str, seller_id: str) -> dict[str, str]:
    customers = pd.read_csv(RAW_DIR / "olist_customers_dataset.csv")
    sellers = pd.read_csv(RAW_DIR / "olist_sellers_dataset.csv")
    customer = customers[customers["customer_id"] == customer_id]
    seller = sellers[sellers["seller_id"] == seller_id]
    return {
        "customer_city": customer["customer_city"].iloc[0] if len(customer) else "",
        "seller_city": seller["seller_city"].iloc[0] if len(seller) else "",
    }
