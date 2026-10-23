"""Pipeline B history features (B2 blueprint, CR-054 B-C6 to B-C9).

Events come from raw orders purchased before the task's test cutoff. A handover event counts in
the week of its carrier date, a delivery event in the week of its delivery date. A row uses only
complete calendar weeks (Monday to Sunday) before its prediction week, so nothing that happened
after the prediction time is counted. The estimated delivery date is never loaded.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

WEEK_ZERO = pd.Timestamp("2016-01-04")   # a Monday; weeks are counted from here
WEIGHTS = (0.5, 0.3, 0.2)                # weeks w-1, w-2, w-3 (Henry, plan v3)
MIN_ROUTE_EVENTS = 10                    # route events over the 3 weeks (Henry, 7c)
STATE_MIX = (0.7, 0.3)                   # seller state, customer state (Henry, 7c)
ORDER_COLS = ["order_id", "customer_id", "order_purchase_timestamp", "order_delivered_carrier_date",
              "order_delivered_customer_date"]   # order_estimated_delivery_date deliberately not read


def week(ts: pd.Series) -> pd.Series:
    return ((ts.dt.normalize() - WEEK_ZERO).dt.days // 7).astype("Int64")


def _days(a: pd.Series, b: pd.Series) -> pd.Series:
    return (a - b).dt.total_seconds() / 86400


def load_events(raw: Path, cutoff: pd.Timestamp) -> pd.DataFrame:
    """One row per order purchased before the cutoff, with its handover and delivery facts."""
    o = pd.read_csv(raw / "olist_orders_dataset.csv", usecols=ORDER_COLS,
                    parse_dates=["order_purchase_timestamp", "order_delivered_carrier_date",
                                 "order_delivered_customer_date"])
    o = o[o.order_purchase_timestamp < cutoff]
    it = pd.read_csv(raw / "olist_order_items_dataset.csv", parse_dates=["shipping_limit_date"])
    it = it[it.order_id.isin(o.order_id)]
    prim = (it.sort_values(["order_id", "price", "order_item_id"], ascending=[True, False, True])
            .drop_duplicates("order_id")[["order_id", "seller_id"]])
    limit = it.groupby("order_id").shipping_limit_date.max().rename("ship_limit").reset_index()
    sellers = pd.read_csv(raw / "olist_sellers_dataset.csv", usecols=["seller_id", "seller_state"])
    customers = pd.read_csv(raw / "olist_customers_dataset.csv", usecols=["customer_id", "customer_state"])
    ev = (o.merge(prim, on="order_id").merge(limit, on="order_id").merge(sellers, on="seller_id")
          .merge(customers, on="customer_id"))
    ev = ev.rename(columns={"order_purchase_timestamp": "purchase_ts", "order_delivered_carrier_date": "carrier_ts",
                            "order_delivered_customer_date": "delivered_ts"})
    ev["route"] = ev.seller_state + "->" + ev.customer_state   # seller state -> customer state
    handed = ev.carrier_ts.notna()
    ev["h_late"] = np.where(handed, (ev.carrier_ts > ev.ship_limit).astype(float), np.nan)
    ev["h_days"] = _days(ev.carrier_ts, ev.ship_limit).clip(lower=0)
    disp = _days(ev.carrier_ts, ev.purchase_ts)
    ev["dispatch"] = disp.where(disp >= 0)
    lead = _days(ev.delivered_ts, ev.purchase_ts)
    ev["lead"] = lead.where(lead >= 0)
    transit = _days(ev.delivered_ts, ev.carrier_ts)
    ev["transit"] = transit.where(transit >= 0)
    ev["hw"] = week(ev.carrier_ts)
    ev["dw"] = week(ev.delivered_ts)
    return ev.sort_values("order_id").reset_index(drop=True)


def weighted3(weekly: pd.DataFrame, query: pd.DataFrame, keys: list[str], cols: list[str]) -> pd.DataFrame:
    """Weighted mean of a weekly statistic over weeks pw-1..pw-3 (weights 0.5, 0.3, 0.2, renormalised
    over the weeks that have a value), plus the number of events behind it.
    weekly: keys + 'week' + cols + 'n'; query: keys + 'pw'. Returns one row per query row."""
    out = pd.DataFrame(index=query.index)
    num = {c: np.zeros(len(query)) for c in cols}
    den = {c: np.zeros(len(query)) for c in cols}
    n3 = np.zeros(len(query))
    for k, w in zip((1, 2, 3), WEIGHTS):
        q = query[keys + ["pw"]].assign(week=query.pw - k)
        m = q.merge(weekly, on=keys + ["week"], how="left")
        n3 += m["n"].fillna(0).to_numpy()
        for c in cols:
            v = m[c].to_numpy(dtype=float)
            ok = ~np.isnan(v)
            num[c] += np.where(ok, w * v, 0.0)
            den[c] += np.where(ok, w, 0.0)
    for c in cols:
        out[c] = np.where(den[c] > 0, num[c] / np.where(den[c] > 0, den[c], 1), np.nan)
    out["n3"] = n3
    return out


def _weekly(ev: pd.DataFrame, keys: list[str], wcol: str, cols: list[str], stat: str) -> pd.DataFrame:
    g = ev.groupby(keys + [wcol])
    t = g[cols].agg(stat)
    t["n"] = g.size()
    return t.reset_index().rename(columns={wcol: "week"}).astype({"week": "int64"})


def seller_features(ev: pd.DataFrame, query: pd.DataFrame) -> pd.DataFrame:
    """Prior seller late rate, late days and dispatch days (B-C7): mean over all of the seller's
    handovers in weeks before pw; a seller with none takes the weighted 3-week mean of sellers in
    the same seller state, then the overall weighted 3-week mean.
    query: seller_id, seller_state, pw (int). Returns seller_prior_* columns, source and last week used."""
    hand = ev[ev.hw.notna()].astype({"hw": "int64"})
    cols = ["h_late", "h_days", "dispatch"]
    g = hand.groupby(["seller_id", "hw"])[cols].agg(["sum", "count"])
    g.columns = [f"{a}_{b}" for a, b in g.columns]
    g = g.reset_index().sort_values("hw")
    for c in cols:
        g[f"{c}_cs"] = g.groupby("seller_id")[f"{c}_sum"].cumsum()
        g[f"{c}_cn"] = g.groupby("seller_id")[f"{c}_count"].cumsum()
    q = query[["seller_id", "pw"]].reset_index().sort_values("pw")
    m = pd.merge_asof(q, g, left_on="pw", right_on="hw", by="seller_id", allow_exact_matches=False,
                      direction="backward").set_index("index").reindex(query.index)
    own = pd.DataFrame({c: m[f"{c}_cs"] / m[f"{c}_cn"] for c in cols}, index=query.index)
    has_own = m["h_late_cn"].fillna(0) > 0
    st = weighted3(_weekly(hand, ["seller_state"], "hw", cols, "mean"), query.assign(pw=query.pw), ["seller_state"], cols)
    allq = query.assign(k=1)
    ov = weighted3(_weekly(hand.assign(k=1), ["k"], "hw", cols, "mean"), allq, ["k"], cols)
    out = pd.DataFrame(index=query.index)
    src = np.where(has_own, "own seller history", np.where(st[cols[0]].notna(), "seller-state fallback",
                                                           np.where(ov[cols[0]].notna(), "overall fallback", "none")))
    names = {"h_late": "seller_prior_late_handover_rate", "h_days": "seller_prior_late_handover_days", "dispatch": "seller_prior_dispatch_days"}
    for c in cols:
        out[names[c]] = np.where(has_own, own[c], np.where(st[c].notna(), st[c], ov[c]))
    out["seller_prior_source"] = src
    out["seller_prior_handovers"] = m["h_late_cn"].fillna(0).astype(int)
    out["seller_prior_last_week"] = m["hw"]
    return out


def route_feature(ev: pd.DataFrame, query: pd.DataFrame, col: str, name: str) -> pd.DataFrame:
    """Route lead or transit days (B-C8, B-C8b): weighted 3-week mean of the route's weekly median;
    fewer than 10 route events in the 3 weeks -> 0.7 x seller state's + 0.3 x customer state's
    weighted 3-week mean (whichever exists if only one does), then the overall one.
    query: route, seller_state, customer_state, pw (int)."""
    dlv = ev[ev.dw.notna() & ev[col].notna()].astype({"dw": "int64"})
    r = weighted3(_weekly(dlv, ["route"], "dw", [col], "median"), query, ["route"], [col])
    s = weighted3(_weekly(dlv, ["seller_state"], "dw", [col], "median"), query, ["seller_state"], [col])
    c = weighted3(_weekly(dlv, ["customer_state"], "dw", [col], "median"), query, ["customer_state"], [col])
    o = weighted3(_weekly(dlv.assign(k=1), ["k"], "dw", [col], "median"), query.assign(k=1), ["k"], [col])
    own = (r["n3"] >= MIN_ROUTE_EVENTS) & r[col].notna()
    both = s[col].notna() & c[col].notna()
    mix = np.where(both, STATE_MIX[0] * s[col] + STATE_MIX[1] * c[col], np.where(s[col].notna(), s[col], c[col]))
    has_state = s[col].notna() | c[col].notna()
    value = np.where(own, r[col], np.where(has_state, mix, o[col]))
    src = np.where(own, "own route history", np.where(has_state, "state-mix fallback", np.where(o[col].notna(), "overall fallback", "none")))
    return pd.DataFrame({name: value, f"{name}_source": src, f"{name}_route_events_3w": r["n3"].astype(int)}, index=query.index)
