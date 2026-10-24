"""B8 additions to A's gate (B8 blueprint methods 3–4): adoption comparison (G-79), mean and SE by
population (Henry, R-02) and the missed-dispatch rule (B-C10). Appends to B8's outputs.

A's side is A's frozen recipe (e5-A-frozen) refitted per fold on A's s05 training rows; scores are
the primary metric on the raw (uncalibrated) predictions: MAE in days, or average precision, which a
monotone calibration does not change.
"""
from __future__ import annotations

import hashlib
import json

import numpy as np
import pandas as pd

from e5lib import protocol
from e5lib.metrics import PRIMARY, score
from e5lib.paths import E5, raw_data_dir
from e5lib.training import TARGET, fit_fold

from . import history as h
from .env import BWriter, b_outputs_dir

A_S06 = "stages/s06_training/{task}/outputs"
A_S08 = "stages/s08_selection/{task}/outputs"
A_S05 = "stages/s05_partition/{task}/outputs"
STATES = ("SP", "MG", "RJ", "PR", "RS", "BA", "SC")


def _metric(task, y, p):
    m, _ = PRIMARY[task]
    return float(score(task, y, y_pred=p)[m]) if task == "regression" else float(score(task, y, proba=p)[m])


def _summary(per_fold: pd.Series) -> tuple[float, float]:
    return float(per_fold.mean()), float(per_fold.std(ddof=1) / np.sqrt(len(per_fold)))


class AppendWriter(BWriter):
    """B's writer that keeps the files and evidence index A's s08 code wrote in the same folder."""

    def __init__(self, stage, task):
        super().__init__(stage, task, clean=False)
        idx = self.dir / "_evidence_index.json"
        if idx.exists():
            prev = json.loads(idx.read_text())
            self.index.update({k: prev[k] for k in ("files", "checks", "deviations", "cards") if k in prev})
            self._prev_decisions = prev
        dec = self.dir / "decision.json"
        self._decisions = json.loads(dec.read_text()) if dec.exists() else []


def run(task: str) -> None:
    w = AppendWriter("b08", task)
    seed = int(protocol.load()["seed"])
    metric, higher = PRIMARY[task]
    y_col = TARGET[task]
    unit = " days" if task == "regression" else ""

    # A's frozen recipe and spec (sha256 re-checked) ----------------------------------------------
    rec = json.loads(w.read(E5 / A_S08.format(task=task) / "frozen_recipe.json").read_text())
    body = {k: v for k, v in rec.items() if k != "sha256"}
    sha_ok = hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest() == rec["sha256"]
    spec = json.loads(w.read(E5 / A_S08.format(task=task) / "selected_spec.json").read_text())["spec"]
    spec_ok = (spec["estimator"] == rec["estimator"] and spec["numeric"] == rec["features"]["numeric"]
               and spec["categorical"] == rec["features"]["categorical"] and spec.get("params", {}) == rec["params"]
               and all(spec.get(k) == v for k, v in rec["transforms"].items()))

    # rows: A's records and folds; B's validation rows; B's recommended model's out-of-fold predictions
    a_rec = pd.read_csv(w.read(E5 / "stages/s02_data/common/outputs/records.csv.gz"), parse_dates=["purchase_ts"], low_memory=False)
    a_rec = a_rec[a_rec[f"eligible_{task}"].astype(bool)].set_index("order_id", drop=False)
    a_folds = pd.read_csv(w.read(E5 / A_S05.format(task=task) / "folds.csv"))
    b_folds = pd.read_csv(w.read(b_outputs_dir("b05", task) / "folds_B.csv"))
    sel_b = json.loads((w.dir / "selected_spec.json").read_text())
    b_rec_id = sel_b["recommended"]
    b_pred = pd.read_csv(w.dir / "predictions.csv.gz")
    b_pred = b_pred[b_pred.candidate_id == b_rec_id]
    a_oof = pd.read_csv(w.read(E5 / A_S06.format(task=task) / "predictions.csv.gz"))
    a_oof = a_oof[a_oof.candidate_id == rec["model"]].set_index(["fold", "order_id"])

    rows, max_dev, a_preds = [], 0.0, {}
    for k in sorted(a_folds.fold.unique()):
        tr = a_folds[(a_folds.fold == k) & (a_folds.role == "train")].order_id
        a_va = a_folds[(a_folds.fold == k) & (a_folds.role == "validation")].order_id
        b_va = b_folds[(b_folds.fold == k) & (b_folds.role == "validation")].order_id
        Xtr = a_rec.loc[tr]
        _, _, pa_all, _ = fit_fold(task, spec, Xtr, Xtr[y_col].to_numpy(), a_rec.loc[a_va])
        pa_all = pd.Series(pa_all, index=a_va.to_numpy())
        a_preds[int(k)] = pa_all
        stored = a_oof.loc[k].reindex(a_va)["y_pred"].to_numpy()
        max_dev = max(max_dev, float(np.nanmax(np.abs(stored - pa_all.to_numpy()))))
        y_a = a_rec.loc[a_va, y_col].to_numpy()
        y_b = a_rec.loc[b_va, y_col].to_numpy()
        bp = b_pred[b_pred.fold == k].set_index("order_id").reindex(b_va)
        rows.append({"fold": int(k), "a_rows": len(a_va), "b_rows": len(b_va),
                     "a_model_on_a_rows": _metric(task, y_a, pa_all.to_numpy()),
                     "a_model_on_b_rows": _metric(task, y_b, pa_all.reindex(b_va).to_numpy()),
                     "b_model_on_b_rows": _metric(task, bp.y_true.to_numpy(), bp.y_pred.to_numpy()),
                     "b_rows_y_match": bool(np.allclose(bp.y_true.to_numpy(), y_b))})
    f = pd.DataFrame(rows)
    sign = 1.0 if higher else -1.0
    f["paired_gain_b_over_a"] = sign * (f.b_model_on_b_rows - f.a_model_on_b_rows)
    w.table("se_decomposition", f[["fold", "a_rows", "b_rows", "a_model_on_a_rows", "a_model_on_b_rows", "b_model_on_b_rows"]], ids=("B8.A",))
    summ = []
    for col, label in (("a_model_on_a_rows", "A's frozen model on A's validation rows"),
                       ("a_model_on_b_rows", "A's frozen model on B's validation rows"),
                       ("b_model_on_b_rows", f"B's recommended model ({b_rec_id}) on B's validation rows")):
        m5, se5 = _summary(f[col])
        m4, se4 = _summary(f.loc[f.fold >= 2, col])
        summ.append({"population_and_model": label, "metric": metric, "mean_5_folds": m5, "se_5_folds": se5,
                     "mean_folds_2_5": m4, "se_folds_2_5": se4})
    summ = pd.DataFrame(summ)
    g5, gse5 = _summary(f.paired_gain_b_over_a)
    g4, gse4 = _summary(f.loc[f.fold >= 2, "paired_gain_b_over_a"])
    adopt = bool(g5 > 0)
    ad = f[["fold", "b_rows", "a_model_on_b_rows", "b_model_on_b_rows", "paired_gain_b_over_a"]].copy()
    w.table("adoption_comparison", ad, ids=("B8.A",))
    w.table("population_summary", summ, ids=("B8.A",))
    w.json("adoption_decision", {"task": task, "metric": metric, "higher_is_better": higher,
                                 "a_frozen_model": rec["model"], "a_frozen_sha256": rec["sha256"], "b_recommended": b_rec_id,
                                 "mean_paired_gain_5_folds": g5, "paired_se_5_folds": gse5,
                                 "b_better_folds": int((f.paired_gain_b_over_a > 0).sum()),
                                 "mean_paired_gain_folds_2_5": g4, "paired_se_folds_2_5": gse4,
                                 "rule": "B is adopted for the task when its 5-fold mean beats A's on the same B rows, even by a thin margin (G-79); folds 2-5 are description only (B-G-01); both go to the joint test run",
                                 "b_adopted_on_folds": adopt}, ids=("B8.A",))

    # every finalist against A on the same rows (the team may choose a finalist other than the recommendation)
    fin = pd.read_csv(w.dir / "candidates.csv")[["candidate_id", "family"]]
    allp = pd.read_csv(w.dir / "predictions.csv.gz")
    frows = []
    for cid, fam in fin.itertuples(index=False):
        for r in f.itertuples():
            b_va = b_folds[(b_folds.fold == r.fold) & (b_folds.role == "validation")].order_id
            bp = allp[(allp.candidate_id == cid) & (allp.fold == r.fold)].set_index("order_id").reindex(b_va)
            bs = _metric(task, bp.y_true.to_numpy(), bp.y_pred.to_numpy())
            frows.append({"candidate_id": cid, "family": fam, "fold": r.fold, "a_model_on_b_rows": r.a_model_on_b_rows,
                          "b_model_on_b_rows": bs, "paired_gain_b_over_a": sign * (bs - r.a_model_on_b_rows)})
    fa = pd.DataFrame(frows)
    w.table("adoption_by_finalist", fa, ids=("B8.A",))
    fs = fa.groupby(["candidate_id", "family"], sort=False).agg(
        b_mean=("b_model_on_b_rows", "mean"), gain_mean=("paired_gain_b_over_a", "mean"),
        gain_se=("paired_gain_b_over_a", lambda x: x.std(ddof=1) / np.sqrt(len(x))),
        folds_b_better=("paired_gain_b_over_a", lambda x: int((x > 0).sum()))).reset_index()
    fs["b_adopted_on_folds_if_chosen"] = fs.gain_mean > 0
    w.table("adoption_by_finalist_summary", fs, ids=("B8.A",))

    # threshold choice support (classification): best threshold under each daily cap; per-fold results
    if task == "classification":
        from e5lib.metrics import COST_FN, COST_FP
        from e5lib.selection import confusion_at
        tc = pd.read_csv(w.dir / "curves" / "threshold_curve.csv")
        crows = []
        for cap in (5, 10, 15, 20, 25, 30, 35, 40, 50):
            ok = tc[tc.alerts_per_day <= cap]
            if ok.empty:
                continue
            b = ok.sort_values(["cost", "threshold"], ascending=[True, False]).iloc[0]
            crows.append({"daily_alert_cap": cap, "best_threshold_in_curve": b.threshold, "alerts_per_day": b.alerts_per_day,
                          "precision": b.precision, "recall": b.recall, "cost": b.cost})
        w.table("threshold_by_cap", pd.DataFrame(crows), ids=("B8.4",))
        tt = pd.read_csv(w.dir / "threshold_table.csv")
        tt = tt[np.isfinite(tt.threshold)]
        rp = allp[allp.candidate_id == b_rec_id]
        trows = []
        for k, part in rp.groupby("fold"):
            y, p_ = part.y_true.to_numpy().astype(int), part.y_pred.to_numpy()
            for cand in tt.itertuples():
                c = confusion_at(y, p_, cand.threshold)
                trows.append({"fold": int(k), "candidate": cand.candidate, "threshold": cand.threshold, "alerts": c["tp"] + c["fp"],
                              "tp": c["tp"], "fp": c["fp"], "fn": c["fn"],
                              "precision": c["tp"] / (c["tp"] + c["fp"]) if c["tp"] + c["fp"] else np.nan,
                              "recall": c["tp"] / (c["tp"] + c["fn"]) if c["tp"] + c["fn"] else np.nan,
                              "cost": COST_FN * c["fn"] + COST_FP * c["fp"]})
        w.table("threshold_by_fold", pd.DataFrame(trows), ids=("B8.4",))

    # metrics by population, raw and (classification, B-G-05) sigmoid -------------------------------------
    mets = ["mae", "rmse", "r2", "within_3d"] if task == "regression" else ["ap", "roc_auc", "brier"]

    def mrow(model, variant, rows_name, k, y, p_):
        s = score(task, y, y_pred=p_) if task == "regression" else score(task, y, proba=p_)
        return [{"model": model, "variant": variant, "rows": rows_name, "fold": int(k), "metric": m, "value": float(s[m])} for m in mets]

    long = []
    variants = {"raw": (a_preds, None)}
    b_sig = None
    if task == "classification":
        from e5lib import factory
        from e5lib.tuning import single_threaded
        a_sig = {}
        cal_a = dict(spec, calibration="sigmoid")
        for k in sorted(a_folds.fold.unique()):
            tr = a_folds[(a_folds.fold == k) & (a_folds.role == "train")].order_id
            a_va = a_folds[(a_folds.fold == k) & (a_folds.role == "validation")].order_id
            cm = factory.build(cal_a)
            single_threaded(cm.estimator)
            cm.fit(a_rec.loc[tr], a_rec.loc[tr, y_col].to_numpy())
            a_sig[int(k)] = pd.Series(cm.predict_proba(a_rec.loc[a_va])[:, 1], index=a_va.to_numpy())
        b_rec_rows = pd.read_csv(b_outputs_dir("b02", task) / "records_B.csv.gz", parse_dates=["purchase_ts"], low_memory=False).set_index("order_id", drop=False)
        cal_b = dict(sel_b["spec"], calibration="sigmoid")
        b_sig = {}
        for k in sorted(b_folds.fold.unique()):
            tr = b_folds[(b_folds.fold == k) & (b_folds.role == "train")].order_id
            b_va = b_folds[(b_folds.fold == k) & (b_folds.role == "validation")].order_id
            cm = factory.build(cal_b)
            single_threaded(cm.estimator)
            cm.fit(b_rec_rows.loc[tr], b_rec_rows.loc[tr, y_col].to_numpy())
            b_sig[int(k)] = pd.Series(cm.predict_proba(b_rec_rows.loc[b_va])[:, 1], index=b_va.to_numpy())
        variants["sigmoid"] = (a_sig, b_sig)
    for variant, (a_p, b_p) in variants.items():
        for k in sorted(a_folds.fold.unique()):
            a_va = a_folds[(a_folds.fold == k) & (a_folds.role == "validation")].order_id
            b_va = b_folds[(b_folds.fold == k) & (b_folds.role == "validation")].order_id
            long += mrow("A frozen model", variant, "A validation rows", k, a_rec.loc[a_va, y_col].to_numpy(), a_p[int(k)].reindex(a_va).to_numpy())
            long += mrow("A frozen model", variant, "B validation rows", k, a_rec.loc[b_va, y_col].to_numpy(), a_p[int(k)].reindex(b_va).to_numpy())
            if b_p is None:
                bp = b_pred[b_pred.fold == k].set_index("order_id").reindex(b_va)
                long += mrow("B recommended model", variant, "B validation rows", k, bp.y_true.to_numpy(), bp.y_pred.to_numpy())
            else:
                long += mrow("B recommended model", variant, "B validation rows", k, a_rec.loc[b_va, y_col].to_numpy(), b_p[int(k)].reindex(b_va).to_numpy())
    mlong = pd.DataFrame(long)
    w.table("metrics_by_population_folds", mlong, ids=("B8.A",))
    msum = (mlong.groupby(["model", "variant", "rows", "metric"], sort=False)["value"]
            .agg(mean_5_folds="mean", se_5_folds=lambda x: x.std(ddof=1) / np.sqrt(len(x))).reset_index())
    w.table("metrics_by_population", msum, ids=("B8.A",))
    if task == "classification":
        cal = pd.read_csv(w.dir / "calibration_folds.csv")
        mine = mlong[(mlong.model == "B recommended model") & (mlong.variant == "sigmoid") & (mlong.metric == "ap")].sort_values("fold").value.to_numpy()
        theirs = cal[cal.variant == "sigmoid"].sort_values("fold").ap.to_numpy()
        sig_dev = float(np.max(np.abs(mine - theirs)))
        w.check("B's sigmoid refit reproduces A's s08 calibration step (sigmoid AP per fold)", sig_dev < 1e-9, ("B8.A",), f"max difference {sig_dev:.2e}")

    # B-G-05: B's threshold tables on sigmoid probabilities ---------------------------------------------
    if task == "classification":
        from e5lib.metrics import COST_FN, COST_FP
        from e5lib.selection import empirical_cost_minimum, threshold_rows
        sp = pd.concat([pd.DataFrame({"order_id": s.index, "fold": k, "p": s.to_numpy()}) for k, s in b_sig.items()], ignore_index=True)
        sp["y"] = a_rec.loc[sp.order_id, y_col].to_numpy()
        vdays = 0.0
        for k in sorted(b_folds.fold.unique()):
            ts_ = a_rec.loc[b_folds[(b_folds.fold == k) & (b_folds.role == "validation")].order_id, "purchase_ts"]
            vdays += (ts_.max().normalize() - ts_.min().normalize()).days + 1
        yt, pt = sp.y.to_numpy().astype(int), sp.p.to_numpy()
        emp = empirical_cost_minimum(yt, pt, COST_FN, COST_FP)
        cand = {"no alerts": float("inf"), "0.50": 0.5, "1/6 (cost cutoff)": 1 / 6, "empirical minimum of 5*FN + FP": emp}
        w.table("threshold_table_sigmoid", threshold_rows(yt, pt, cand, vdays, COST_FN, COST_FP), ids=("B8.4",))
        grid = np.round(np.arange(0.02, 0.61, 0.01), 2)
        tcs = threshold_rows(yt, pt, {f"{x:.2f}": x for x in grid}, vdays, COST_FN, COST_FP)
        w.table("threshold_curve_sigmoid", tcs, ids=("B8.4",))
        crows = []
        for cap in (5, 10, 15, 20, 25, 30, 35, 40, 50):
            ok = tcs[tcs.alerts_per_day <= cap]
            if not ok.empty:
                b_ = ok.sort_values(["cost", "threshold"], ascending=[True, False]).iloc[0]
                crows.append({"daily_alert_cap": cap, "best_threshold_in_curve": b_.threshold, "alerts_per_day": b_.alerts_per_day,
                              "precision": b_.precision, "recall": b_.recall, "cost": b_.cost})
        w.table("threshold_by_cap_sigmoid", pd.DataFrame(crows), ids=("B8.4",))
        frows = []
        for k, part in sp.groupby("fold"):
            for name, th in (("1/6 (cost cutoff)", 1 / 6), ("empirical minimum of 5*FN + FP", emp)):
                c = confusion_at(part.y.to_numpy().astype(int), part.p.to_numpy(), th)
                al = c["tp"] + c["fp"]
                frows.append({"fold": int(k), "candidate": name, "threshold": th, "alerts": al, **c,
                              "precision": c["tp"] / al if al else np.nan, "recall": c["tp"] / (c["tp"] + c["fn"]) if c["tp"] + c["fn"] else np.nan,
                              "cost": COST_FN * c["fn"] + COST_FP * c["fp"]})
        w.table("threshold_by_fold_sigmoid", pd.DataFrame(frows), ids=("B8.4",))

    # B8.5 freeze (B-G-05): B's frozen recipe, labelled B, with sigmoid and the threshold on sigmoid probabilities
    import yaml
    from e5lib.selection import frozen_recipe
    dec = ((yaml.safe_load(w.read(E5 / "pipeline_b/spec/human_decisions_B.yaml").read_text()) or {}).get("b08") or {}).get(task) or {}
    fr_path = w.dir / "frozen_recipe.json"
    if fr_path.exists():
        a_side = json.loads(fr_path.read_text())  # written by A's code: rule calibration, label "A"
        cal, thr = a_side["calibration"], a_side.get("threshold")
        override = (dec.get("calibration_override") or {}).get("value")
        if task == "classification" and override == "sigmoid":
            row = threshold_rows(yt, pt, {"team decision": float(dec["threshold"]["value"])}, vdays, COST_FN, COST_FP).iloc[0]
            thr = {"value": float(dec["threshold"]["value"]), "daily_alert_cap": dec["threshold"].get("daily_alert_cap"),
                   "applies_to": "sigmoid-calibrated probability", "oof_alerts_per_day": float(row.alerts_per_day),
                   "oof_precision": float(row.precision), "oof_recall": float(row.recall), "oof_cost": float(row.cost)}
            cal = "sigmoid"
            w.deviation("B8.3", "calibration sigmoid by team decision B-G-05 (the 8.3 rule result is raw); threshold computed on sigmoid probabilities")
        recipe = frozen_recipe(task, sel_b["spec"], cal, thr, dec, pd.Timestamp(protocol.get("data_dependent.test_cutoffs.values")[task]), seed)
        recipe.update({"pipeline": "B", "step": "B8.5"})
        body = {k: v for k, v in recipe.items() if k != "sha256"}
        recipe["sha256"] = hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()
        w.json("frozen_recipe", recipe, ids=("B8.5",))
        sel_b.update({"calibration": cal, "threshold": thr, "calibration_override": "B-G-05" if cal != a_side["calibration"] else None})
        w.json("selected_spec", sel_b, ids=("B8.2", "B8.3") if task == "classification" else ("B8.2",))
        w.check("B's frozen recipe: labelled B, the team's chosen model, sha256 recomputes", recipe["pipeline"] == "B"
                and recipe["model"] == dec["model"]["chosen"] == b_rec_id
                and hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest() == recipe["sha256"],
                ("B8.5",), f"sha256 {recipe['sha256'][:12]}…")
        if task == "classification":
            w.check("B-G-05 applied: calibration sigmoid and the threshold on sigmoid probabilities keeps out-of-fold alerts within the cap",
                    recipe["calibration"] == "sigmoid" and thr["applies_to"] == "sigmoid-calibrated probability"
                    and (thr["daily_alert_cap"] is None or thr["oof_alerts_per_day"] <= thr["daily_alert_cap"]), ("B8.5",),
                    f"{thr['oof_alerts_per_day']:.1f} alerts/day at {thr['value']:.4f}, cap {thr['daily_alert_cap']}")
        w.explain("B8.5", done=(f"Frozen recipe for B ({recipe['model']}): calibration {recipe['calibration'] or 'none'}"
                                + (f", threshold {thr['value']:.4f} on the {thr['applies_to']} (daily cap {thr['daily_alert_cap']}; "
                                   f"out-of-fold {thr['oof_alerts_per_day']:.1f} alerts/day, precision {thr['oof_precision']:.3f}, "
                                   f"recall {thr['oof_recall']:.3f})" if thr else "")
                                + f"; sha256 {recipe['sha256']}. Written before any test row is read; decisions in human_decisions_B.yaml b08."))

        # confusion matrices at the frozen thresholds on B's validation rows (Henry, R-06)
        if task == "classification":
            crow = []
            for name, probs_by_fold, t_ in (("A frozen model (sigmoid, 1/6)", a_sig, float(rec["threshold"]["value"])),
                                            ("B frozen model (sigmoid, 1/6)", b_sig, thr["value"])):
                for k in sorted(b_folds.fold.unique()):
                    b_va = b_folds[(b_folds.fold == k) & (b_folds.role == "validation")].order_id
                    c = confusion_at(a_rec.loc[b_va, y_col].to_numpy().astype(int), probs_by_fold[int(k)].reindex(b_va).to_numpy(), t_)
                    al = c["tp"] + c["fp"]
                    crow.append({"model": name, "threshold": t_, "fold": int(k), **c, "alerts": al,
                                 "precision": c["tp"] / al if al else np.nan, "recall": c["tp"] / (c["tp"] + c["fn"]),
                                 "cost": COST_FN * c["fn"] + COST_FP * c["fp"]})
            cm_ = pd.DataFrame(crow)
            tot = cm_.groupby(["model", "threshold"], sort=False)[["tp", "fp", "fn", "tn", "alerts", "cost"]].sum().reset_index()
            tot["fold"] = "all"
            tot["precision"] = tot.tp / tot.alerts
            tot["recall"] = tot.tp / (tot.tp + tot.fn)
            w.table("confusion_comparison", pd.concat([cm_, tot[cm_.columns]], ignore_index=True), ids=("B8.A",))

    # missed-dispatch rule (classification) -----------------------------------------------------------
    if task == "classification":
        cutoff = pd.Timestamp(protocol.get("data_dependent.test_cutoffs.values")[task])
        for fname in ("olist_orders_dataset.csv", "olist_order_items_dataset.csv", "olist_sellers_dataset.csv", "olist_customers_dataset.csv"):
            w.read(raw_data_dir() / fname)
        ev = h.load_events(raw_data_dir(), cutoff)
        pop = a_rec[(a_rec.purchase_ts < cutoff) & a_rec.customer_state.isin(STATES) & a_rec.primary_seller_state.isin(STATES)
                    & a_rec.distance_km_max.notna() & (a_rec.purchase_ts >= pd.Timestamp("2017-01-01") + pd.Timedelta(weeks=6))]
        pop = pop[["order_id", "is_detractor"]].reset_index(drop=True).merge(ev[["order_id", "carrier_ts", "ship_limit"]], on="order_id", how="left")
        never = pop.carrier_ts.isna()
        late = pop.carrier_ts.notna() & (pop.carrier_ts > pop.ship_limit)
        flag = never | late
        tot_det = int(pop.is_detractor.sum())
        mrows = []
        for name, m in (("never handed over", never), ("handed over after the limit", late), ("all flagged (rule fires)", flag),
                        ("not flagged", ~flag)):
            n, d = int(m.sum()), int(pop.loc[m, "is_detractor"].sum())
            mrows.append({"group": name, "orders": n, "detractors": d, "precision": d / n if n else np.nan,
                          "share_of_all_detractors": d / tot_det if tot_det else np.nan})
        md_ = pd.DataFrame(mrows)
        w.table("missed_dispatch_rule", md_, ids=("B8.M",))
        al = md_.set_index("group").loc["all flagged (rule fires)"]
        w.explain("B8.M", done=(f"Population: A-eligible classification development orders in the seven states with a distance, after the "
                                f"warm-up ({len(pop):,} orders, {tot_det:,} detractors). The rule fires when the last shipping limit passes "
                                f"with no carrier handover: {int(al.orders):,} orders, {int(al.detractors):,} detractors (precision "
                                f"{al.precision:.3f}, {al.share_of_all_detractors:.1%} of all detractors). A rule, not a model (B-C10)."))
        w.check("missed-dispatch groups add up to the population", int(never.sum() + late.sum() + (~flag).sum()) == len(pop), ("B8.M",),
                f"{len(pop):,} orders")

    # checks and card ---------------------------------------------------------------------------------
    w.check("A's frozen recipe unchanged: sha256 recomputes and A's selected spec matches it", sha_ok and spec_ok, ("B8.A",),
            f"sha256 {rec['sha256'][:12]}…")
    w.check("A's refit reproduces A's stored s06 out-of-fold predictions on A's validation rows", max_dev < 1e-6, ("B8.A",),
            f"max difference {max_dev:.2e}")
    w.check("B's validation rows and labels are exactly B5's, in every fold", bool(f.b_rows_y_match.all())
            and int(f.b_rows.sum()) == int((b_folds.role == "validation").sum()), ("B8.A",), f"{int(f.b_rows.sum()):,} validation rows")
    w.explain("B8.A", done=(f"Adoption comparison (G-79) on {metric.upper()}{unit}: A's frozen model ({rec['model']}) refitted per fold on A's training "
                            f"rows vs B's recommended model ({b_rec_id}), both on B's validation rows. Mean paired gain of B over A "
                            f"{g5:+.4f}{unit} (paired SE {gse5:.4f}), B better in {int((f.paired_gain_b_over_a > 0).sum())} of 5 folds; "
                            f"folds 2-5 (description only, B-G-01): {g4:+.4f}{unit}. By the fold rule B is "
                            f"{'adopted' if adopt else 'not adopted'} for {task}; A and B both go to the joint test run. "
                            "Mean and SE by population are in population_summary.csv (R-02)."))
    w.finish(seed=seed)
    if w.index["checks_failed"]:
        raise SystemExit(f"B8 {task}: checks failed: {w.index['checks_failed']}")
    print(f"B8 {task}: B over A {g5:+.4f}{unit} (5 folds), adopted={adopt}")
