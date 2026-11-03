"""Business case for report and deck v2.4 (B-CR-50; v2.4 changes B-CR-53, decisions B-G-25 to B-G-27).

Post-test analysis on Pipeline B's held-out test orders (the seven states). Read only: it reads the stored T1 test
predictions, B8's out-of-fold validation predictions, the s02 order records, the raw order events (as e5b.history
loads them) and B9/B10 result tables, and it scores scenarios with the frozen T1 bundles through the dashboard's
own scenario code. Nothing is fitted and no stage output is changed. The frozen 12.0-day buffer chosen by b12 on
validation stays the unbiased result; every test number here is a post-test view.

    deliverables/dashboard/app/.venv/Scripts/python.exe deliverables/business_case/make_business_case.py

Outputs (evidence BC.1 to BC.5):
    promise_compare.csv   BC.1  Olist's estimate, Dummy, A, B and B + buffers: median promise, MAE, late share (test)
    buffer_recent.csv     BC.2  buffer chosen on B8's last validation fold only, against b12's 12.0 days
    expedite.csv          BC.3  late orders handed over late: on time if carrier transit were 10% faster (scenario)
    discount.csv          BC.4  still-late orders the serving rule flags: alert stops under freight scenarios (association)
    reach.csv             BC.5  alerts/day, precision and detractors reached/day for the alert options, with each
                                option's population and its cost against no alert on that population (v2.4)
    cost_check.csv        BC.6  5:1 cost of no alert, 1/6 and 4/15 on validation and test, per population (v2.4)
    retention.csv         BC.7  customers with more than one order over March 2017 to April 2018 (v2.4)
    summary.json          headline numbers of all five; figures/promise_compare.png (+ .csv)
with _manifest.json (run id, commit, input and code sha256, output sha256) and _evidence_index.json. The register
reads these files as BCASE/<file> (build_evidence_B.verify_manifest_source).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
APP = HERE.parent / "dashboard" / "app"
B_ROOT = HERE.parents[1]
E5 = B_ROOT.parent
REPO = HERE.parents[4]
sys.path.insert(0, str(APP))
warnings.filterwarnings("ignore", message=".*No runtime found.*")
import platform  # noqa: E402

from dashboard_core import alerts, model_client, paths, score_tab  # noqa: E402
from dashboard_core.data import load_business_complete_months  # noqa: E402
from dashboard_core.routing import in_scope  # noqa: E402
from e5b.b09_extra import a_rec_id  # noqa: E402
from e5b.t1_joint_test import EVENTS_UNTIL  # noqa: E402
from e5lib.paths import raw_data_dir  # noqa: E402

OUT = HERE / "outputs"
STAGES = B_ROOT / "stages"
T1_REG = STAGES / "t1_joint_test" / "regression" / "outputs" / "predictions_test.csv.gz"
T1_CLF = STAGES / "t1_joint_test" / "classification" / "outputs" / "predictions_test.csv.gz"
B08_REG = STAGES / "b08" / "regression" / "outputs" / "predictions.csv.gz"
B12_CHOICE = STAGES / "b12" / "regression" / "outputs" / "buffer_choice.csv"
B10_THR = STAGES / "b10" / "classification" / "outputs" / "threshold_results.csv"
B09_RULE = STAGES / "b09" / "classification" / "outputs" / "missed_dispatch_rule_test.csv"
RECORDS = E5 / "stages" / "s02_data" / "common" / "outputs" / "records.csv.gz"
RAW = raw_data_dir()
RAW_FILES = ["olist_orders_dataset.csv", "olist_order_items_dataset.csv", "olist_sellers_dataset.csv",
             "olist_customers_dataset.csv"]

GRID = np.round(np.arange(0, 30.01, 0.5), 1)   # b12's 0.5-day grid
SHOWN_BUFFERS = (3.0, 5.0, 6.0, 12.0)           # Henry's 3 and 6, Benson's 5 and 12 (B-G-19)
FROZEN_BUFFER = 12.0                            # b12, 90% on time on all validation folds
RECENT_TARGET = 0.05                            # recommended rule: at most 5% late on recent weeks (B-G-25, v2.4)
BIZ_FIRST, BIZ_LAST = "2017-03", "2018-04"      # the business overview's months (business_context)
COST_FN, COST_FP = 5, 1                         # a missed detractor weighs as five false alerts
B_THRESHOLD = 4 / 15
A_THRESHOLD = 1 / 6
EXPEDITE = score_tab.LOGISTICS_CUT              # transit 10% faster, as the dashboard's "Logistics -10%" (B-G-20)
BLUE, GREY, ORANGE = "#2563eb", "#9ca3af", "#F4A259"


def _sha(p: Path) -> str:
    """sha256; text files with CRLF normalised to LF, as build_evidence_B._sha (B-G-15, B-CR-46)."""
    data = p.read_bytes()
    if p.suffix.lower() in {".csv", ".json", ".md", ".txt", ".py"}:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def _rel(p: Path) -> str:
    return p.resolve().relative_to(REPO).as_posix()


def _late(actual: np.ndarray, promise: np.ndarray) -> float:
    return float(np.mean(actual > promise))


def _smallest(actual: np.ndarray, pred: np.ndarray, target: float) -> float:
    return float(next(b for b in GRID if _late(actual, pred + b) <= target))


def _row(series: str, actual: np.ndarray, promise: np.ndarray) -> dict:
    return {"series": series, "orders": int(len(actual)), "median_promise_days": float(np.median(promise)),
            "mae_days": float(np.mean(np.abs(actual - promise))), "share_late": _late(actual, promise),
            "late_orders": int(np.sum(actual > promise))}


def main() -> None:
    records = pd.read_csv(RECORDS, usecols=["order_id", "purchase_ts", "est_delivery_days", "customer_state",
                                            "primary_seller_state", "distance_km_max"])
    records["purchase_ts"] = pd.to_datetime(records["purchase_ts"])
    t1 = pd.read_csv(T1_REG)
    on_b = lambda m: t1[(t1.model == m) & (t1.rows == "B test rows")].set_index("order_id")  # noqa: E731
    b, dummy, a = on_b("B frozen"), on_b("B dummy"), on_b("A frozen")
    test = b[["y_true", "y_pred"]].join(dummy["y_pred"].rename("dummy")).join(a["y_pred"].rename("a"))
    test = test.join(records.set_index("order_id")[["est_delivery_days", "purchase_ts"]])
    assert test.notna().all().all() and len(test) == len(b), "every B test order needs all predictions and Olist's estimate"
    y = test["y_true"].to_numpy()

    # BC.2 buffer on recent weeks: B8's last validation fold only (no refit; out-of-fold predictions) -------------
    b8 = pd.read_csv(B08_REG)
    b8 = b8[b8.candidate_id == a_rec_id("regression")].merge(records[["order_id", "purchase_ts", "est_delivery_days"]],
                                                              on="order_id", how="left")
    assert b8["est_delivery_days"].notna().all()
    last = b8[b8.fold == b8.fold.max()]
    ya, pa = b8.y_true.to_numpy(), b8.y_pred.to_numpy()
    yl, pl, ol = last.y_true.to_numpy(), last.y_pred.to_numpy(), last.est_delivery_days.to_numpy()
    b12 = pd.read_csv(B12_CHOICE).set_index("on_time_target")
    all_folds_10 = _smallest(ya, pa, 0.10)
    assert all_folds_10 == float(b12.loc[0.9, "buffer_days_chosen_on_validation"]) == FROZEN_BUFFER, "b12's 12.0 days reproduced"
    olist_last = _late(yl, ol)
    rules = [("all validation folds, late share <= 10% (b12, frozen)", "1-5", ya, pa, 0.10),
             ("last validation fold, late share <= 10%", str(int(last.fold.max())), yl, pl, 0.10),
             ("last validation fold, late share <= Olist's on that fold", str(int(last.fold.max())), yl, pl, olist_last),
             ("last validation fold, late share <= 5% (recommended)", str(int(last.fold.max())), yl, pl, RECENT_TARGET)]
    recent = []
    for rule, folds, yy, pp, target in rules:
        buf = _smallest(yy, pp, target)
        rows = b8 if folds == "1-5" else last
        recent.append({"rule": rule, "folds": folds, "orders": int(len(yy)),
                       "first_purchase": rows.purchase_ts.min().date().isoformat(),
                       "last_purchase": rows.purchase_ts.max().date().isoformat(),
                       "target_share_late": float(target), "buffer_days": buf, "validation_share_late": _late(yy, pp + buf),
                       "validation_share_late_no_buffer": _late(yy, pp),
                       "olist_validation_share_late": _late(yy, rows.est_delivery_days.to_numpy()),
                       "test_share_late_B": _late(y, test.y_pred.to_numpy() + buf),
                       "test_median_promise_days": float(np.median(test.y_pred.to_numpy() + buf)),
                       "test_mae_days": float(np.mean(np.abs(y - test.y_pred.to_numpy() - buf)))})
    recent = pd.DataFrame(recent)
    olist_rule = float(recent.iloc[2]["buffer_days"])    # v2.3 rule: Olist's late share on recent weeks (B-G-21, superseded)
    recommended = float(recent.iloc[3]["buffer_days"])   # v2.4 rule: at most 5% late on recent weeks (B-G-25)
    OLIST_RULE = f"Pipeline B + {olist_rule:g} days (recent weeks, Olist's late share)"
    REC = f"Pipeline B + {recommended:g} days (recommended: recent weeks, 5% late)"

    # BC.1 promise comparison on B's test orders --------------------------------------------------------------------
    promises = [("Olist estimate", test.est_delivery_days), ("Dummy (median)", test.dummy), ("Pipeline A", test.a),
                ("Pipeline B", test.y_pred)]
    promises += [(f"Pipeline B + {d:g} days", test.y_pred + d) for d in SHOWN_BUFFERS]
    promises += [(OLIST_RULE, test.y_pred + olist_rule), (REC, test.y_pred + recommended)]
    compare = pd.DataFrame([_row(s, y, p.to_numpy()) for s, p in promises])
    compare.insert(1, "kind", ["Olist's own promise", "baseline", "model", "model"] + ["model + buffer"] * (len(compare) - 4))

    # BC.3 transit 10% faster for late orders whose seller handed over late (scenario) ----------------------------
    events = alerts._events().set_index("order_id")
    test = test.join(events[["carrier_ts", "ship_limit", "h_late", "dispatch", "transit"]])
    late_handover = test.h_late.eq(1).to_numpy()
    transit = test.transit.to_numpy()
    sped = y - EXPEDITE * np.nan_to_num(transit, nan=0.0)
    expedite, still_late = [], {}
    for name, promise in (("Olist estimate", test.est_delivery_days.to_numpy()),
                          (f"Pipeline B + {FROZEN_BUFFER:g} days (frozen buffer)", test.y_pred.to_numpy() + FROZEN_BUFFER),
                          (OLIST_RULE, test.y_pred.to_numpy() + olist_rule),
                          (REC, test.y_pred.to_numpy() + recommended)):
        late = y > promise
        group = late & late_handover & ~np.isnan(transit)
        rescued = group & (sped <= promise)
        expedite.append({"promise": name, "orders": int(len(y)), "late_orders": int(late.sum()),
                         "late_with_late_handover": int(group.sum()),
                         "share_of_late_with_late_handover": float(group.sum() / late.sum()),
                         "on_time_if_transit_10pct_faster": int(rescued.sum()),
                         "share_of_late_handover_group_on_time": float(rescued.sum() / group.sum()),
                         "share_of_all_late_on_time": float(rescued.sum() / late.sum()),
                         "late_share_after": float((late & ~rescued).sum() / len(y))})
        still_late[name] = test.index[late & ~rescued]
    expedite = pd.DataFrame(expedite)

    # BC.4 still-late orders the serving rule flags (B at 4/15): freight scenarios on the alert model ------------
    clf = pd.read_csv(T1_CLF)
    bc = clf[(clf.model == "B frozen") & (clf.rows == "B test rows")].set_index("order_id")
    flagged_all = bc.index[bc.y_pred >= B_THRESHOLD]
    pool = sorted(set().union(*[set(v) for v in still_late.values()]) & set(flagged_all))
    rows = score_tab.alerts.model_rows("classification", tuple(pool))
    lead = model_client.predict("regression", alerts.model_rows("regression", tuple(pool))).set_index("order_id")["prediction"]
    ids = rows["order_id"].astype(str)
    saving = pd.Series(EXPEDITE * (lead.reindex(ids).to_numpy() - events.loc[ids, "dispatch"].to_numpy()).clip(min=0))
    scen = score_tab._scenario_rows(rows, True, saving)
    scored = model_client.predict("classification", scen)
    scored["scenario"], scored["base"] = scen["scenario"].to_numpy(), scen["base_order_id"].to_numpy()
    asis = scored[scored.scenario == "As is"].set_index("base")["prediction"]
    assert np.allclose(asis.reindex(pool).to_numpy(), bc.loc[pool, "y_pred"].to_numpy(), atol=1e-9), "bundles reproduce T1's stored risk"
    floor = float(alerts._records()["total_freight"].quantile(0.01))
    freight_after = scen.set_index("order_id")["total_freight"]
    discount = []
    for name, ids_late in still_late.items():
        group = sorted(set(ids_late) & set(flagged_all))
        det = int(bc.loc[group, "y_true"].sum())
        for label, _, _ in score_tab.SCENARIOS:
            s = scored[(scored.scenario == label) & scored.base.isin(group)]
            stops = s.prediction < s.threshold
            outside = (freight_after.loc[s.order_id].to_numpy() < floor) & (rows.set_index("order_id").loc[s.base, "total_freight"].to_numpy() >= floor)
            discount.append({"promise": name, "still_late_orders": int(len(ids_late)), "flagged_by_B_4_15": len(group),
                             "detractors_among_flagged": det, "scenario": label, "scored": int(len(s)),
                             "alert_stops": int(stops.sum()), "share_alert_stops": float(stops.mean()) if len(s) else float("nan"),
                             "alert_stops_outside_training_range": int((stops.to_numpy() & outside).sum())})
    discount = pd.DataFrame(discount)

    # BC.5 reach of the alert options: alerts/day x precision = detractors reached a day --------------------------
    thr = pd.read_csv(B10_THR)
    pick = lambda name, rows_: thr[(thr.threshold_name == name) & (thr.rows == rows_)].iloc[0]  # noqa: E731
    b415 = pick("B operating 4/15 (B-G-07)", "test, B rows (post-test view)")
    a16 = pick("A frozen 1/6 (B10-D2)", "test, A rows outside B's scope")
    days = float(b415.alerts / b415.alerts_per_day)
    assert abs(a16.alerts / a16.alerts_per_day - days) < 1e-9
    a_test = clf[(clf.model == "A frozen") & (clf.rows == "A test rows")].merge(records, on="order_id", how="left")
    a_out = a_test[~in_scope(a_test).to_numpy()]
    assert int((a_out.y_pred >= A_THRESHOLD).sum()) == int(a16.alerts), "A's fallback at 1/6 reproduces B10"
    f = a_out.y_pred >= B_THRESHOLD
    rule_tab = pd.read_csv(B09_RULE).set_index("group")
    rule = rule_tab.loc["all flagged (rule fires)"]
    rule_pop_det = int(round(rule.detractors / rule.share_of_all_detractors))
    assert rule_pop_det == int(rule_tab.detractors.loc[["all flagged (rule fires)", "not flagged"]].sum())
    a_out_det = int(a_out.y_true.sum())
    assert a_out_det == int(a16.tp + a16.fn)
    a415_tp = int(a_out.loc[f, "y_true"].sum())
    seven, outside = "seven states (Pipeline B's orders)", "outside the seven states (fallback orders)"
    reach = pd.DataFrame([
        {"option": "Pipeline B at 4/15 (seven states)", "population": seven, "alerts": int(b415.alerts),
         "precision": float(b415.precision), "detractors_in_population": int(b415.tp + b415.fn), "tp": int(b415.tp),
         "basis": "B10 threshold_results (test, post-test view)"},
        {"option": "Pipeline A fallback at 1/6 (outside the seven states)", "population": outside, "alerts": int(a16.alerts),
         "precision": float(a16.precision), "detractors_in_population": a_out_det, "tp": int(a16.tp),
         "basis": "B10 threshold_results (test, post-test view)"},
        {"option": "Pipeline A fallback at 4/15 (outside the seven states)", "population": outside, "alerts": int(f.sum()),
         "precision": float(a_out.loc[f, "y_true"].mean()), "detractors_in_population": a_out_det, "tp": a415_tp,
         "basis": "T1 stored predictions (test, post-test view; threshold not tuned on test)"},
        {"option": "Missed-dispatch rule alone", "population": seven + "; overlaps B's alerts", "alerts": int(rule.orders),
         "precision": float(rule.precision), "detractors_in_population": rule_pop_det, "tp": int(rule.detractors),
         "basis": "B9 missed_dispatch_rule_test (test)"},
    ])
    reach["fp"] = reach.alerts - reach.tp
    reach["fn"] = reach.detractors_in_population - reach.tp
    reach["cost_5_to_1"] = COST_FN * reach.fn + COST_FP * reach.fp
    reach["cost_no_alert"] = COST_FN * reach.detractors_in_population
    reach["alerts_per_day"] = reach.alerts / days
    reach["detractors_reached_per_day"] = reach.precision * reach.alerts_per_day
    reach["test_days"] = days
    assert int(reach.cost_5_to_1.iloc[0]) == int(b415.cost_5_to_1) and int(reach.cost_5_to_1.iloc[1]) == int(a16.cost_5_to_1)

    # BC.6 cost of each threshold against no alert, on the population it serves, validation and test -------------
    def cost_rows(rows_label: str, b_rows: str, a_rows: str) -> list[dict]:
        b16, b4, a1 = pick("B frozen 1/6", b_rows), pick("B operating 4/15 (B-G-07)", b_rows), pick("A frozen 1/6 (B10-D2)", a_rows)
        b_det, a_det = int(b16.tp + b16.fn), int(a1.tp + a1.fn)
        out = [("Pipeline B, no alert", seven, COST_FN * b_det), ("Pipeline B at 1/6", seven, int(b16.cost_5_to_1)),
               ("Pipeline B at 4/15", seven, int(b4.cost_5_to_1)),
               ("Fallback, no alert", outside, COST_FN * a_det), ("Fallback (A) at 1/6", outside, int(a1.cost_5_to_1))]
        if rows_label == "test":
            out.append(("Fallback (A) at 4/15", outside, int(reach.cost_5_to_1.iloc[2])))
        out += [("Serving rule: no alert", "all served orders", COST_FN * (b_det + a_det)),
                ("Serving rule: B at 4/15, fallback at 1/6", "all served orders", int(b4.cost_5_to_1 + a1.cost_5_to_1)),
                ("Serving rule: B at 4/15, no fallback alert", "all served orders", int(b4.cost_5_to_1) + COST_FN * a_det)]
        return [{"rows": rows_label, "policy": p, "population": pop, "cost_5_to_1": int(c)} for p, pop, c in out]
    costs = pd.DataFrame(cost_rows("validation", "validation (out-of-fold), B rows",
                                   "validation (out-of-fold), A rows outside B's scope")
                         + cost_rows("test", "test, B rows (post-test view)", "test, A rows outside B's scope"))
    assert int(costs.query("rows == 'test' and policy == 'Serving rule: B at 4/15, fallback at 1/6'").cost_5_to_1.iloc[0]) == int(
        pick("B 4/15 + A 1/6 (serving rule)", "test, all rows (post-test view)").cost_5_to_1)

    # BC.7 retention: customers with more than one order over the business overview's months -------------------
    biz = load_business_complete_months()
    biz = biz[(biz["year_month"] >= BIZ_FIRST) & (biz["year_month"] <= BIZ_LAST)]
    per_customer = biz.groupby("customer_unique_id")["order_id"].nunique()
    retention = pd.DataFrame([{"first_month": BIZ_FIRST, "last_month": BIZ_LAST, "customers": int(len(per_customer)),
                               "customers_more_than_one_order": int((per_customer > 1).sum()),
                               "share_more_than_one_order": float((per_customer > 1).mean()),
                               "definition": "customer_unique_id with more than one order over the whole window "
                                             "(business overview data, dashboard_core.data.load_business_complete_months)"}])

    # outputs --------------------------------------------------------------------------------------------------------
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    for name, frame in (("promise_compare", compare), ("buffer_recent", recent), ("expedite", expedite),
                        ("discount", discount), ("reach", reach), ("cost_check", costs), ("retention", retention)):
        frame.to_csv(OUT / f"{name}.csv", index=False, lineterminator="\n")
    by = compare.set_index("series")
    freight = discount[discount.scenario.isin([lab for lab, _, _ in score_tab.SCENARIOS])]
    summary = {
        "test_orders": int(len(y)),
        "test_window": {"first_purchase": test.purchase_ts.min().date().isoformat(), "last_purchase": test.purchase_ts.max().date().isoformat()},
        "promise": {s.replace(" ", "_").replace("(", "").replace(")", "").replace("+", "plus").replace("-", "_").lower(): {
            "median_promise_days": float(r.median_promise_days), "mae_days": float(r.mae_days), "share_late": float(r.share_late)}
            for s, r in by.iterrows()},
        "buffer": {"frozen_b12_days": FROZEN_BUFFER, "recent_10pct_days": float(recent.iloc[1]["buffer_days"]),
                   "recent_olist_days": olist_rule, "recent_5pct_days": recommended, "recommended_days": recommended,
                   "olist_last_fold_share_late": olist_last,
                   "last_fold": int(last.fold.max()), "last_fold_first_purchase": recent.iloc[1]["first_purchase"],
                   "last_fold_last_purchase": recent.iloc[1]["last_purchase"],
                   "b_no_buffer_last_fold_share_late": float(recent.iloc[1]["validation_share_late_no_buffer"]),
                   "b_no_buffer_all_folds_share_late": float(recent.iloc[0]["validation_share_late_no_buffer"])},
        "expedite": {r.promise: {k: (float(v) if isinstance(v, float) else int(v)) for k, v in r._asdict().items() if k not in ("Index", "promise")}
                     for r in expedite.itertuples()},
        "discount_best": {p: {"flagged": int(g.flagged_by_B_4_15.iloc[0]), "detractors": int(g.detractors_among_flagged.iloc[0]),
                              "free_shipping_stops": int(g.loc[g.scenario == "Free shipping", "alert_stops"].iloc[0]),
                              "freight_30_stops": int(g.loc[g.scenario == "Freight −30%", "alert_stops"].iloc[0])}
                          for p, g in freight.groupby("promise")},
        "reach": {r.option: {"alerts_per_day": float(r.alerts_per_day), "precision": float(r.precision),
                             "detractors_reached_per_day": float(r.detractors_reached_per_day)} for r in reach.itertuples()},
        "labels": {
            "BC.1": "observation on test orders (post-test view); the frozen 12.0-day buffer from b12 is the unbiased result",
            "BC.2": "operational rule: buffer chosen on the last validation fold (no test data); test late share is a post-test view",
            "BC.3": f"scenario, unmeasured mechanism: actual carrier transit shortened by {EXPEDITE:.0%} for late orders handed over late",
            "BC.4": "association, not an effect: the alert model's risk under the dashboard's freight scenarios",
            "BC.5": "observation (precision, alerts/day on test, post-test view); reach = precision x alerts/day",
            "BC.6": "assumption (5:1 cost); thresholds set on validation, test costs a post-test view",
            "BC.7": "observation: repeat customers over the whole window, not a churn or lifetime measure",
        },
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8", newline="\n")

    # figure: promise length against late share ------------------------------------------------------------------
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(10, 4.6), dpi=200)
    fig_rows = compare.iloc[::-1].reset_index(drop=True)
    colours = [ORANGE if k == "Olist's own promise" else (GREY if k == "baseline" else BLUE) for k in fig_rows.kind]
    ax.barh(fig_rows.series, fig_rows.median_promise_days, color=colours, height=0.65)
    for i, r in fig_rows.iterrows():
        ax.text(r.median_promise_days + 0.3, i, f"{r.median_promise_days:.1f} d · {r.share_late:.1%} late · MAE {r.mae_days:.1f}",
                va="center", fontsize=9.5)
    ax.set_xlim(0, fig_rows.median_promise_days.max() * 1.6)
    ax.set_xlabel("median promised lead time on B's test orders (days)")
    ax.set_title("Promise length and late share (test orders, post-test view)", loc="left", fontsize=12)
    ax.grid(axis="x", color="#e5e7eb", linewidth=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(OUT / "figures" / "promise_compare.png")
    plt.close(fig)
    compare.to_csv(OUT / "figures" / "promise_compare.csv", index=False, lineterminator="\n")

    index = {"node": "BCASE/business_case", "files": {
        "promise_compare.csv": {"ids": ["BC.1"], "kind": "table"},
        "buffer_recent.csv": {"ids": ["BC.2"], "kind": "table"},
        "expedite.csv": {"ids": ["BC.3"], "kind": "table"},
        "discount.csv": {"ids": ["BC.4"], "kind": "table"},
        "reach.csv": {"ids": ["BC.5"], "kind": "table"},
        "cost_check.csv": {"ids": ["BC.6"], "kind": "table"},
        "retention.csv": {"ids": ["BC.7"], "kind": "table"},
        "summary.json": {"ids": ["BC.1", "BC.2", "BC.3", "BC.4", "BC.5", "BC.6", "BC.7"], "kind": "json"},
        "figures/promise_compare.png": {"ids": ["BC.1"], "kind": "figure"},
        "figures/promise_compare.csv": {"ids": ["BC.1"], "kind": "figure_data"},
    }}
    (OUT / "_evidence_index.json").write_text(json.dumps(index, indent=2), encoding="utf-8", newline="\n")
    git = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True).stdout.strip()  # noqa: E731
    code = [Path(__file__), APP / "dashboard_core" / "score_tab.py", APP / "dashboard_core" / "alerts.py",
            APP / "dashboard_core" / "model_client.py", APP / "dashboard_core" / "routing.py",
            APP / "dashboard_core" / "data.py"]
    inputs = [T1_REG, T1_CLF, B08_REG, B12_CHOICE, B10_THR, B09_RULE, RECORDS, paths.BUSINESS_DATA_PATH] + [RAW / f for f in RAW_FILES]
    outputs = [p for p in sorted(OUT.rglob("*")) if p.is_file() and not p.name.startswith("_manifest")]
    manifest = {
        "node": "BCASE/business_case",
        "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "commit": git("rev-parse", "HEAD"),
        "dirty": bool(git("status", "--porcelain", "--", *[_rel(p) for p in code])),
        "events_until": str(EVENTS_UNTIL),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "inputs": {_rel(p): _sha(p) for p in inputs},
        "code": {_rel(p): _sha(p) for p in code},
        "outputs": {_rel(p): _sha(p) for p in outputs},
    }
    (OUT / "_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
