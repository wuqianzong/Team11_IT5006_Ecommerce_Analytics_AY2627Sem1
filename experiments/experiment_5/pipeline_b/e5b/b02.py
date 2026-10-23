"""B2: population rules and history features for Pipeline B (blueprint
pipeline_b/spec/blueprints/b02_population_features.md; CR-054 B-C1 to B-C9; G-79).

Evidence IDs: B2.1 population, B2.2 prediction time, B2.3 events, B2.4 weeks, B2.5 features,
B2.6 test rows.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from e5lib import protocol
from e5lib.paths import E5, raw_data_dir

from . import history as h
from .env import BWriter, assert_a_frozen

STAGE = "b02"
STATES = ("SP", "MG", "RJ", "PR", "RS", "BA", "SC")             # B-C1
CAP_SD = 8                                                     # B-C3: mean + 8 SD, no floor
WARMUP_END = pd.Timestamp("2017-01-01") + pd.Timedelta(weeks=6)  # B-C4
A_RECORDS = E5 / "stages/s02_data/common/outputs/records.csv.gz"
A_AUDIT = E5 / "stages/s02_data/common/outputs/audit.json"
SAMPLE = 300                                                   # rows re-checked by brute force


def _rule(d: pd.DataFrame, mask: pd.Series, code: str, out: list) -> pd.DataFrame:
    out.append(pd.DataFrame({"order_id": d.loc[mask, "order_id"], "reason_code": code}))
    return d[~mask]


def run(task: str) -> None:
    assert_a_frozen()
    w = BWriter(STAGE, task)
    seed = int(protocol.load()["seed"])
    cutoff = pd.Timestamp(protocol.get("data_dependent.test_cutoffs.values")[task])
    raw = raw_data_dir()
    for f in ("olist_orders_dataset.csv", "olist_order_items_dataset.csv", "olist_sellers_dataset.csv",
              "olist_customers_dataset.csv"):
        w.read(raw / f)
    a = pd.read_csv(w.read(A_RECORDS), parse_dates=["purchase_ts", "review_label_ts", "lead_label_ts"])
    a = a.drop(columns=[c for c in a.columns if "estimated" in c or c == "est_delivery_days"])
    a_dev = a[a[f"eligible_{task}"] & (a.purchase_ts < cutoff)].copy()
    audit = json.loads(w.read(A_AUDIT).read_text())["outlier_threshold"]
    cap = audit["pre_cutoff_mean"] + CAP_SD * audit["pre_cutoff_sd"]

    ev = h.load_events(raw, cutoff)
    facts = ev[["order_id", "seller_id", "seller_state", "carrier_ts", "ship_limit", "h_late", "h_days", "dispatch"]]
    d = a_dev.merge(facts, on="order_id", how="left")

    # B2.1 population (B-C1 to B-C5), first failing rule wins -------------------------------
    removed: list = []
    d = _rule(d, ~(d.customer_state.isin(STATES) & d.primary_seller_state.isin(STATES)), "B_STATE", removed)
    d = _rule(d, d.distance_km_max.isna(), "B_DISTANCE", removed)
    if task == "regression":
        d = _rule(d, d.lead_days > cap, "B_LEAD_CAP", removed)
    else:
        d = _rule(d, d.carrier_ts.isna(), "B_NO_HANDOVER", removed)
        d = _rule(d, d.review_label_ts <= d.carrier_ts, "B_REVIEW_BEFORE_HANDOVER", removed)

    # B2.2 prediction time; B2.4 prediction week ----------------------------------------------
    d["b_prediction_ts"] = d.purchase_ts if task == "regression" else d.carrier_ts
    d["b_prediction_week"] = h.week(d.b_prediction_ts).astype("int64")
    d["route"] = d.customer_state + "->" + d.primary_seller_state
    q = d[["seller_id", "seller_state", "customer_state", "route"]].assign(pw=d.b_prediction_week)

    # B2.5 features (B-C6 to B-C9) -------------------------------------------------------------
    sf = h.seller_features(ev, q)
    rl = h.route_feature(ev, q, "lead", "b_route_lead_days")
    rt = h.route_feature(ev, q, "transit", "b_route_transit_days")
    d = pd.concat([d, sf, rl, rt], axis=1)
    if task == "classification":
        d["b_own_handover_late"] = d.h_late
        d["b_own_late_days"] = d.h_days
        d["b_own_dispatch_days"] = d.dispatch

    # warm-up removed after the features are built (B-C4)
    d = _rule(d, d.purchase_ts < WARMUP_END, "B_WARMUP", removed)
    exc = pd.concat(removed, ignore_index=True).assign(task=task)

    # leakage re-check by brute force on a fixed sample -----------------------------------------
    rng = np.random.default_rng(seed)
    hand = ev[ev.hw.notna()].astype({"hw": "int64"})
    dlv = ev[ev.dw.notna() & ev.lead.notna()].astype({"dw": "int64"})
    sample = d.iloc[np.sort(rng.choice(len(d), size=min(SAMPLE, len(d)), replace=False))]
    diffs, last_ok = [], True
    for r in sample.itertuples():
        if r.b_seller_source == "seller":
            past = hand[(hand.seller_id == r.seller_id) & (hand.hw < r.b_prediction_week)]
            diffs.append(abs(past.h_late.mean() - r.b_seller_late_rate))
            last_ok &= bool(past.hw.max() < r.b_prediction_week)
        if r.b_route_lead_days_source == "route":
            num = den = 0.0
            for k, wt in zip((1, 2, 3), h.WEIGHTS):
                v = dlv[(dlv.route == r.route) & (dlv.dw == r.b_prediction_week - k)].lead
                if len(v):
                    num += wt * v.median()
                    den += wt
            diffs.append(abs(num / den - r.b_route_lead_days))
    max_diff = float(np.max(diffs)) if diffs else 0.0

    # outputs -----------------------------------------------------------------------------------
    keep_cols = [c for c in d.columns if c not in ("carrier_ts", "ship_limit", "h_late", "h_days", "dispatch", "seller_state")]
    out = d[keep_cols].sort_values(["b_prediction_ts", "order_id"]).reset_index(drop=True)
    w.table("records_B", out, ids=("B2.1", "B2.2", "B2.5"), compress=True)
    w.table("exclusions_B", exc[["order_id", "task", "reason_code"]], ids=("B2.1",))
    counts = exc.groupby("reason_code").size().reindex(
        ["B_STATE", "B_DISTANCE", "B_LEAD_CAP", "B_NO_HANDOVER", "B_REVIEW_BEFORE_HANDOVER", "B_WARMUP"]).dropna().astype(int)
    ct = pd.concat([pd.DataFrame({"step": ["A development rows (s02, pre-cutoff, eligible)"], "rows": [len(a_dev)]}),
                    pd.DataFrame({"step": [f"removed: {k}" for k in counts.index], "rows": counts.to_numpy()}),
                    pd.DataFrame({"step": ["B development rows"], "rows": [len(out)]})], ignore_index=True)
    w.table("exclusion_counts_B", ct, ids=("B2.1",))
    quarter = out.b_prediction_ts.dt.to_period("Q").astype(str)
    cov = []
    for col in ("b_seller_source", "b_route_lead_days_source", "b_route_transit_days_source"):
        t = pd.crosstab(quarter, out[col], normalize="index").reset_index().melt(id_vars="b_prediction_ts", var_name="source", value_name="share")
        cov.append(t.assign(feature=col.replace("_source", "")).rename(columns={"b_prediction_ts": "quarter"}))
    w.table("history_coverage", pd.concat(cov, ignore_index=True)[["feature", "quarter", "source", "share"]], ids=("B2.5",))
    lat = ev[ev.hw.notna()].assign(week_start=lambda x: (h.WEEK_ZERO + pd.to_timedelta(x.hw.astype("int64") * 7, unit="D")).dt.strftime("%Y-%m-%d"))
    ls = (lat.groupby(["route", "customer_state", "seller_state", "week_start", "seller_id"])
          .agg(handovers=("h_late", "size"), seller_late_rate=("h_late", "mean"), seller_late_days=("h_days", "mean"),
               transit_days_median=("transit", "median"), lead_days_median=("lead", "median")).reset_index())
    w.table("lateness_summary_B", ls, ids=("B2.5",), compress=True)
    feats = [c for c in out.columns if c.startswith("b_") and not c.endswith(("_source", "_n", "_n3", "_week", "_ts"))] + ["route"]
    w.json("feature_build_log", {"task": task, "cutoff": str(cutoff), "lead_cap_days": cap, "warmup_end": str(WARMUP_END),
                                 "weights": h.WEIGHTS, "min_route_events": h.MIN_ROUTE_EVENTS, "state_mix": h.STATE_MIX,
                                 "events": int(len(ev)), "features": feats}, ids=("B2.3", "B2.4", "B2.5"))

    # checks ------------------------------------------------------------------------------------
    w.check("B development rows are a subset of A's eligible pre-cutoff rows", bool(out.order_id.isin(a_dev.order_id).all()),
            ("B2.1",), f"{len(out):,} of {len(a_dev):,}")
    w.check("removal counts add up: A rows = B rows + removed", len(a_dev) == len(out) + len(exc), ("B2.1",),
            f"{len(a_dev):,} = {len(out):,} + {len(exc):,}")
    w.check("no test row: every B row purchased before the test cutoff", bool(out.purchase_ts.max() < cutoff), ("B2.6",),
            f"latest purchase {out.purchase_ts.max()}, cutoff {cutoff}")
    w.check("no column from the estimated delivery date", not any("estimated" in c or c == "est_delivery_days" for c in out.columns),
            ("B2.3",))
    w.check("seller state from the raw tables equals A's primary_seller_state", bool((d.seller_state == d.primary_seller_state).all()),
            ("B2.3",))
    w.check("leakage re-check: features recomputed by brute force from events in weeks before the prediction week match",
            max_diff < 1e-9 and last_ok, ("B2.4", "B2.5"), f"{len(sample)} rows, max difference {max_diff:.2e}")
    if task == "regression":
        w.check("lead-time cap applied: no B row above mean + 8 SD of A's s02 pre-cutoff orders (audit.json)",
                bool(out.lead_days.max() <= cap), ("B2.1",), f"cap {cap:.2f} days; longest B lead time {out.lead_days.max():.2f}")

    # cards -------------------------------------------------------------------------------------
    rm = "; ".join(f"{k} {v:,}" for k, v in counts.items())
    w.explain("B2.1", done=f"From {len(a_dev):,} A development rows (s02, eligible, before the cutoff) to {len(out):,} B rows. Removed: {rm}.")
    w.explain("B2.2", done="Prediction time: " + ("purchase time (checkout)." if task == "regression" else "carrier handover time."))
    w.explain("B2.3", done=f"{len(ev):,} raw orders purchased before the cutoff {cutoff}; primary seller by A's rule (highest price, then lowest item id); "
              "the estimated delivery date column is not read.")
    w.explain("B2.4", done="Calendar weeks from Monday 2016-01-04; handover events in their carrier-date week, delivery events in their delivery week; "
              "a row uses only weeks before its prediction week.")
    srcs = "; ".join(f"{c.replace('_source', '')}: " + ", ".join(f"{k} {v:.1%}" for k, v in out[c].value_counts(normalize=True).items())
                     for c in ("b_seller_source", "b_route_lead_days_source", "b_route_transit_days_source"))
    w.explain("B2.5", done=f"Features built: {', '.join(feats)}. History sources: {srcs}.")
    w.explain("B2.6", done="Development rows only; test-row features are built in the joint test run.")
    w.finish(seed=seed)
    if w.index["checks_failed"]:
        raise SystemExit(f"B2 {task}: checks failed: {w.index['checks_failed']}")
    print(f"B2 {task}: {len(out):,} rows, {len(feats)} features")
