"""Seller history at checkout (screening candidates, s02; G-69).

Written for Experiment 5. For each order with primary seller s and purchase time t, only events of
s that happened strictly before t (to the second) count, and the order's own events never count:

- review events: every valid review (integer score 1..5) of s's orders, at its answer timestamp;
- delivery events: every delivered order of s, at its customer-delivery timestamp, late when the
  delivery is after its estimated delivery date.

An earlier order is attributed to its primary seller (the primary_category rule). The order's own
events are removed by order_id, because some reviews carry an answer timestamp before their order's
recorded purchase (s02 2.7 date audit).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

COLUMNS = ("seller_prior_review_mean", "seller_prior_review_count", "seller_prior_detractor_share",
           "seller_prior_delivered_count", "seller_prior_late_share")


def _prior(orders: pd.DataFrame, events: pd.DataFrame, value_cols: list[str]) -> pd.DataFrame:
    """Per order: sums of value_cols over the seller's events strictly before purchase_ts, own order excluded."""
    ev = events.sort_values(["ts", "order_id"], kind="mergesort").reset_index(drop=True)
    cum = ev.groupby("seller_id")[value_cols].cumsum().add_prefix("cum_")
    ev = pd.concat([ev[["seller_id", "ts"]], cum], axis=1)
    left = orders[["order_id", "seller_id", "purchase_ts"]].dropna(subset=["seller_id"]).sort_values(
        "purchase_ts", kind="mergesort")
    m = pd.merge_asof(left, ev, left_on="purchase_ts", right_on="ts", by="seller_id",
                      allow_exact_matches=False, direction="backward")
    out = m.set_index("order_id")[[f"cum_{c}" for c in value_cols]].fillna(0.0)
    out.columns = value_cols
    # own events that fall before the order's own purchase would be counted above: remove them
    own = events.merge(orders[["order_id", "seller_id", "purchase_ts"]], on=["order_id", "seller_id"])
    own = own[own["ts"] < own["purchase_ts"]].groupby("order_id")[value_cols].sum()
    out = out.sub(own.reindex(out.index).fillna(0.0))
    return out.reindex(orders["order_id"].to_numpy()).set_axis(orders.index)


def seller_history(orders: pd.DataFrame, reviews: pd.DataFrame, deliveries: pd.DataFrame) -> pd.DataFrame:
    """orders: order_id, seller_id (primary seller, may be missing), purchase_ts.
    reviews: order_id, review_score, review_answer_timestamp (raw rows; invalid scores ignored).
    deliveries: order_id, delivered_ts, estimated_ts (delivered orders only).
    Returns the COLUMNS, indexed like orders."""
    seller_of = orders.set_index("order_id")["seller_id"]
    score = reviews["review_score"].astype(float)
    valid = score.notna() & (score % 1 == 0) & (score >= 1) & (score <= 5) & reviews["review_answer_timestamp"].notna()
    rv = pd.DataFrame({"order_id": reviews.loc[valid, "order_id"].to_numpy(),
                       "ts": reviews.loc[valid, "review_answer_timestamp"].to_numpy(),
                       "score": score[valid].to_numpy(), "n": 1.0,
                       "det": (score[valid] <= 2).astype(float).to_numpy()})
    rv["seller_id"] = rv["order_id"].map(seller_of)
    dv = pd.DataFrame({"order_id": deliveries["order_id"].to_numpy(), "ts": deliveries["delivered_ts"].to_numpy(),
                       "n": 1.0, "late": (deliveries["delivered_ts"] > deliveries["estimated_ts"]).astype(float).to_numpy()})
    dv["seller_id"] = dv["order_id"].map(seller_of)
    r = _prior(orders, rv.dropna(subset=["seller_id"]), ["score", "n", "det"])
    d = _prior(orders, dv.dropna(subset=["seller_id", "ts"]), ["n", "late"])
    out = pd.DataFrame(index=orders.index)
    out["seller_prior_review_count"] = r["n"]
    out["seller_prior_review_mean"] = np.where(r["n"] > 0, r["score"] / r["n"].where(r["n"] > 0), np.nan)
    out["seller_prior_detractor_share"] = np.where(r["n"] > 0, r["det"] / r["n"].where(r["n"] > 0), np.nan)
    out["seller_prior_delivered_count"] = d["n"]
    out["seller_prior_late_share"] = np.where(d["n"] > 0, d["late"] / d["n"].where(d["n"] > 0), np.nan)
    return out[list(COLUMNS)]


def brute_force(orders: pd.DataFrame, reviews: pd.DataFrame, deliveries: pd.DataFrame, order_ids) -> pd.DataFrame:
    """Direct per-order recomputation (slow; used by the s02 check on a sample)."""
    seller_of = orders.set_index("order_id")["seller_id"]
    o = orders.set_index("order_id")
    score = reviews["review_score"].astype(float)
    valid = score.notna() & (score % 1 == 0) & (score >= 1) & (score <= 5) & reviews["review_answer_timestamp"].notna()
    rv = reviews[valid].assign(seller_id=lambda x: x["order_id"].map(seller_of), s=score[valid])
    dv = deliveries.assign(seller_id=lambda x: x["order_id"].map(seller_of))
    rows = {}
    for oid in order_ids:
        s, t = o.at[oid, "seller_id"], o.at[oid, "purchase_ts"]
        if pd.isna(s):
            rows[oid] = dict.fromkeys(COLUMNS, np.nan)  # no seller: history unknown
            continue
        r = rv[(rv["seller_id"] == s) & (rv["review_answer_timestamp"] < t) & (rv["order_id"] != oid)]
        d = dv[(dv["seller_id"] == s) & (dv["delivered_ts"] < t) & (dv["order_id"] != oid)]
        rows[oid] = {"seller_prior_review_mean": r["s"].mean() if len(r) else np.nan,
                     "seller_prior_review_count": float(len(r)),
                     "seller_prior_detractor_share": (r["s"] <= 2).mean() if len(r) else np.nan,
                     "seller_prior_delivered_count": float(len(d)),
                     "seller_prior_late_share": (d["delivered_ts"] > d["estimated_ts"]).mean() if len(d) else np.nan}
    return pd.DataFrame.from_dict(rows, orient="index")[list(COLUMNS)]
