"""s08 selection shared by both task nodes (blueprint spec/blueprints/s08_selection.md).

Written for Experiment 5 from the blueprint; no code or numbers from earlier experiments.

Gate part (8.1-8.4), run on the s05 folds only:
- finalists (8.1): each family's carried model from s07 plus the dummy, plain linear/logistic and
  single-tree references from s06, refitted on the same rows and folds
- recommendation (8.2): the s01 one-SE rule over the finalists (G-33), with the basic-to-complex
  ladder and paired fold gains shown beside it; the team confirms at the gate (G-39)
- calibration (8.3, classification): raw vs sigmoid, kept only if mean Brier improves and mean AP
  stays within one fold SE of the raw model (G-16, G-45, G-52)
- threshold table (8.4, classification): no alerts, 0.50, 1/6 and the empirical cost minimum, with
  alerts per day and the marginal trade-off; the team picks at the hard stop (G-39)

The run stops at the gate until the team's combined review of s06-s08 has filled
spec/human_decisions.yaml s08 (G-78). Once it has:
- freeze (8.5): frozen_recipe.json (features, transforms, estimator and settings, calibration,
  threshold, team decisions) with its sha256, written from development rows only.
The run then stops after the freeze: the final fit, the single test and the bundle (8.6-8.8) run
together with Pipeline B (lead decision 2026-10-23; draft G-79).
"""
from __future__ import annotations

import hashlib
import json
import warnings

import numpy as np
import pandas as pd

from . import factory
from .training import FAMILIES, FAMILY_LABEL, TARGET, candidate_specs, fit_fold, ladder, paired_gain, score_rows
from .tuning import base_spec, family_grid, single_threaded

STAGE = "s08_selection"
THRESHOLDS = {"0.5": 0.5, "1/6": 1.0 / 6.0}


# ---------------------------------------------------------------------------------------------
# Finalists (8.1)
# ---------------------------------------------------------------------------------------------
def finalists(task: str, recipes: dict, protocol: dict, s07_counts: dict, s07_grid: pd.DataFrame, seed: int) -> list[dict]:
    """dummy, plain linear/logistic and single tree from s06, plus each family's carried model from s07.

    Simplicity rank: family order (s01 1.7); inside a family the plain s06 model before a tuned one.
    """
    plain = {c["family"]: c for c in candidate_specs(task, recipes, protocol["families"]["s06_settings"], seed)}
    out = [dict(plain["dummy"], source="s06 reference"), dict(plain["linear"], source="s06 reference"),
           dict(plain["tree"], source="s06 reference")]
    for fam in ("linear", "tree", "forest"):
        cid = s07_counts["carried"][fam]
        if cid == plain[fam]["candidate_id"]:
            if fam == "forest":
                out.append(dict(plain["forest"], source="s07 carried (plain s06)"))
            continue
        params = json.loads(s07_grid.set_index("candidate_id").loc[cid, "params"])
        est, _ = family_grid(task, fam, protocol["grids"])
        spec = dict(base_spec(task, fam, recipes, est, seed), params=params)
        out.append({"family": fam, "spec": spec, "candidate_id": cid, "source": "s07 tuned (beyond one SE of plain)"})
    for i, c in enumerate(sorted(out, key=lambda c: (FAMILIES.index(c["family"]), c["source"] != "s06 reference"))):
        c["simplicity"] = i
    return sorted(out, key=lambda c: c["simplicity"])


def decisions_complete(task: str, decisions: dict) -> bool:
    """The s08 section of human_decisions.yaml is filled for this task (model; classification also threshold)."""
    return bool(decisions.get("model")) and (task == "regression" or bool(decisions.get("threshold")))


def frozen_recipe(task: str, spec: dict, calibration: str | None, threshold: dict | None, decisions: dict,
                  cutoff, seed: int) -> dict:
    """The 8.5 freeze record. Its sha256 covers every other field, so any later change shows."""
    body = {"pipeline": "A", "step": "8.5", "task": task, "model": decisions["model"]["chosen"],
            "estimator": spec["estimator"], "params": spec.get("params", {}),
            "features": {"numeric": spec["numeric"], "categorical": spec["categorical"]},
            "transforms": {k: spec[k] for k in ("log_inputs", "route_median", "drop_duplicates", "log_target") if k in spec},
            "calibration": calibration, "threshold": threshold, "random_state": spec.get("random_state", seed),
            "final_fit": "all development orders whose labels were observable before the test cutoff (8.6)",
            "test_cutoff": str(cutoff), "test_read": False, "decisions": decisions}
    body["sha256"] = hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest()
    return body


def grid_edge(task: str, fam: str, spec: dict, grids: dict) -> str:
    """Name the parameters that sit at the edge of their pre-registered grid (8.2), or say why none apply."""
    params = spec.get("params") or {}
    if fam == "dummy":
        return "not a grid configuration (dummy)"
    try:
        _, grid = family_grid(task, fam, grids)
    except KeyError:
        return "not a grid configuration"
    hits = []
    for k, vals in grid.items():
        num = [v for v in vals if isinstance(v, (int, float)) and not isinstance(v, bool)]
        if k in params and num and len(num) > 1 and params[k] in (min(num), max(num)):
            hits.append(f"{k}={params[k]}")
    if not any(k in params for k in grid):
        return "plain s06 model, not a grid configuration"
    return "; ".join(hits) if hits else "none"


# ---------------------------------------------------------------------------------------------
# Threshold table (8.4)
# ---------------------------------------------------------------------------------------------
def confusion_at(y: np.ndarray, p: np.ndarray, t: float) -> dict:
    pred = p >= t
    tp = int(np.sum(pred & (y == 1)))
    fp = int(np.sum(pred & (y == 0)))
    fn = int(np.sum(~pred & (y == 1)))
    tn = int(np.sum(~pred & (y == 0)))
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}


def empirical_cost_minimum(y: np.ndarray, p: np.ndarray, c_fn: float, c_fp: float) -> float:
    """Threshold minimising c_fn*FN + c_fp*FP over every distinct probability (and 'no alerts');
    ties go to the higher threshold (fewer alerts)."""
    order = np.argsort(-p, kind="mergesort")
    ps, ys = p[order], y[order]
    tp = np.cumsum(ys == 1)
    fp = np.cumsum(ys == 0)
    last = np.r_[ps[1:] != ps[:-1], True]           # alert = p >= this value: take the last row of each tie
    cand_t, cand_tp, cand_fp = ps[last], tp[last], fp[last]
    n_pos = int(np.sum(y == 1))
    cost = c_fn * (n_pos - cand_tp) + c_fp * cand_fp
    best = float(cost.min())
    no_alert_cost = c_fn * n_pos
    if no_alert_cost <= best:
        return float("inf")
    return float(cand_t[cost == best].max())


def threshold_rows(y: np.ndarray, p: np.ndarray, thresholds: dict, days: float, c_fn: float, c_fp: float) -> pd.DataFrame:
    rows = []
    n = len(y)
    for name, t in thresholds.items():
        c = confusion_at(y, p, t)
        alerts = c["tp"] + c["fp"]
        prec = c["tp"] / alerts if alerts else 0.0
        rec = c["tp"] / (c["tp"] + c["fn"]) if (c["tp"] + c["fn"]) else 0.0
        rows.append({"candidate": name, "threshold": t, **c, "alerts": alerts, "alerts_per_day": alerts / days,
                     "alert_rate": alerts / n, "error_rate": (c["fn"] + c["fp"]) / n, "precision": prec, "recall": rec,
                     "f1": 2 * prec * rec / (prec + rec) if prec + rec else 0.0, "cost": c_fn * c["fn"] + c_fp * c["fp"]})
    t = pd.DataFrame(rows).sort_values("threshold", ascending=False).reset_index(drop=True)
    # marginal trade-off against the next higher threshold: extra false alarms per extra detractor caught
    d_tp, d_fp = t["tp"].diff(), t["fp"].diff()
    t["extra_false_alarms_per_extra_detractor"] = np.where(d_tp > 0, d_fp / d_tp.where(d_tp > 0), np.nan)
    return t


# ---------------------------------------------------------------------------------------------
# Node runner (stages/s08_selection/<task>/run.py calls run(task))
# ---------------------------------------------------------------------------------------------
def run(task: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import yaml
    from sklearn.calibration import calibration_curve

    from . import cv, data, protocol
    from .metrics import COST_FN, COST_FP, PRIMARY, fold_summary, one_se_select, score
    from .outputs import Writer
    from .paths import outputs_dir, spec_path

    warnings.filterwarnings("ignore", message="Found unknown categories", category=UserWarning)
    w = Writer(STAGE, task)
    p = protocol.load()
    seed = int(p["seed"])
    metric, higher = PRIMARY[task]
    unit = " days" if task == "regression" else ""
    y_col = TARGET[task]
    cutoff = pd.Timestamp(protocol.get("data_dependent.test_cutoffs.values")[task])

    recipes = json.loads(data.upstream("s04_features", task, "recipes.json", STAGE).read_text(encoding="utf-8"))
    s06_ml = pd.read_csv(data.upstream("s06_training", task, "metrics_long.csv", STAGE), keep_default_na=False)
    s06_lc = pd.read_csv(data.upstream("s06_training", task, "curves/learning_curves.csv", STAGE))
    s07_counts = json.loads(data.upstream("s07_tuning", task, "counts.json", STAGE).read_text(encoding="utf-8"))
    s07_grid = pd.read_csv(data.upstream("s07_tuning", task, "grid_results.csv", STAGE))
    decisions = ((yaml.safe_load(spec_path("human_decisions.yaml").read_text(encoding="utf-8")) or {}).get("s08") or {}).get(task) or {}
    decided = decisions_complete(task, decisions)
    d = data.load("records", task, "development", STAGE).set_index("order_id", drop=False)
    fold_list = list(cv.folds(task, STAGE))
    fins = finalists(task, recipes, p, s07_counts, s07_grid, seed)
    cols = factory.feature_columns(fins[1]["spec"])

    # 8.1 Refit every finalist on the same rows and folds ------------------------------------
    metric_rows, pred_rows, val_primary = [], [], []
    for k, tr_ids, va_ids in fold_list:
        Xtr, ytr = d.loc[tr_ids, cols], d.loc[tr_ids, y_col].to_numpy()
        Xva, yva = d.loc[va_ids, cols], d.loc[va_ids, y_col].to_numpy()
        for c in fins:
            _, ptr, pva, _ = fit_fold(task, c["spec"], Xtr, ytr, Xva)
            for phase, yy, pp in (("train", ytr, ptr), ("validation", yva, pva)):
                for r in score_rows(task, yy, pp, THRESHOLDS if task == "classification" else {}):
                    metric_rows.append({"population": "development", "phase": phase, "fold": k, "candidate_id": c["candidate_id"],
                                        "n_rows": len(yy), "n_pos": int(yy.sum()) if task == "classification" else "",
                                        "family": c["family"], **r})
            pred_rows.append(pd.DataFrame({"order_id": va_ids, "task": task, "population": "development", "fold": k,
                                           "candidate_id": c["candidate_id"], "y_true": yva, "y_pred": pva}))
    ml = pd.DataFrame(metric_rows)
    w.metrics_long(ml, ids=("8.1",))
    preds = pd.concat(pred_rows, ignore_index=True)
    w.predictions(preds, ids=("8.1", "8.3" if task == "classification" else "8.1"))
    val = ml[(ml["phase"] == "validation") & (ml["metric"] == metric)][["candidate_id", "fold", "metric", "value"]]
    trn = ml[(ml["phase"] == "train") & (ml["metric"] == metric)][["candidate_id", "fold", "metric", "value"]]
    vs, ts = fold_summary(val, metric), fold_summary(trn, metric)

    # finalist table: fold mean ± SE on every s01 metric, gap, grid edge
    allm = ml[(ml["phase"] == "validation") & (ml["threshold"] == "")].groupby(["candidate_id", "metric"])["value"]
    mean_tab = allm.mean().unstack()
    se_tab = (allm.std(ddof=1) / np.sqrt(len(fold_list))).unstack()
    rows = []
    for c in fins:
        cid = c["candidate_id"]
        gap = (ts.loc[cid, "mean"] - vs.loc[cid, "mean"]) if higher else (vs.loc[cid, "mean"] - ts.loc[cid, "mean"])
        row = {"candidate_id": cid, "family": FAMILY_LABEL[c["family"]], "source": c["source"], "simplicity": c["simplicity"],
               "params": json.dumps(c["spec"].get("params", {}), sort_keys=True), "train_mean": ts.loc[cid, "mean"],
               "validation_mean": vs.loc[cid, "mean"], "validation_se": vs.loc[cid, "se"], "train_validation_gap": gap,
               "grid_edge": grid_edge(task, c["family"], c["spec"], p["grids"])}
        for m in mean_tab.columns:
            if m not in ("prevalence",):
                row[f"{m}_mean"] = mean_tab.loc[cid, m]
                row[f"{m}_se"] = se_tab.loc[cid, m]
        rows.append(row)
    ftab = pd.DataFrame(rows)

    # 8.2 Recommendation: one-SE over the finalists, with the ladder and paired gains ------------
    simp = {c["candidate_id"]: c["simplicity"] for c in fins}
    rec = one_se_select(val, metric, higher, simp)
    order = [c["candidate_id"] for c in fins]
    steps = ladder(val, metric, higher, order)
    lad_result = order[0]
    for s in steps:
        if s["complex_kept"]:
            lad_result = s["complex"]
    fam_of = {c["candidate_id"]: c["family"] for c in fins}
    recommended = rec["chosen"]
    ftab["recommended"] = ftab["candidate_id"] == recommended
    ftab["within_one_se_of_best"] = ftab["candidate_id"].isin(rec["summary"].loc[rec["summary"]["within_one_se"], "candidate_id"])
    w.candidates(ftab.assign(description=ftab["family"] + " (" + ftab["source"] + ")", kept=ftab["recommended"],
                             reason=np.where(ftab["recommended"], "one-SE recommendation (team confirms at the gate, G-39)",
                                             "finalist, not the one-SE recommendation")), ids=("8.1", "8.2"))
    pg = pd.DataFrame([{"comparison": f"{FAMILY_LABEL[fam_of[s['complex']]]} vs {FAMILY_LABEL[fam_of[s['simpler']]]}",
                        "simpler": s["simpler"], "complex": s["complex"],
                        **{f"gain_fold_{k}": g for k, g in s["paired"]["fold_gains"].items()},
                        "mean_gain": s["paired"]["mean_gain"], "paired_se": s["paired"]["paired_se"],
                        "folds_better": s["paired"]["folds_better"], "kept_by_one_se_rule": s["complex_kept"]} for s in steps])
    w.table("ladder", pg, ids=("8.2",))
    w.decision("Model recommended at the s08 gate", f"one-SE rule over the finalists on validation {metric} (s01 1.7, G-33)",
               order, recommended, ["candidates.csv", "metrics_long.csv", "ladder.csv"], ids=("8.2",),
               notes=f"best mean: {rec['best']}; band {rec['band'][0]:.4f} to {rec['band'][1]:.4f}; ladder result "
                     f"(basic to complex, each step kept only beyond one SE): {lad_result}. The team confirms or overrides "
                     "in human_decisions.yaml s08.model (G-39); an override is a protocol deviation (G-44).")
    rec_spec = next(c for c in fins if c["candidate_id"] == recommended)

    # ladder figure
    fig, ax = plt.subplots(figsize=(8, 4))
    for i, c in enumerate(fins):
        v = val[val["candidate_id"] == c["candidate_id"]]
        ax.scatter([i] * len(v), v["value"], color="tab:gray", s=14)
        ax.errorbar(i, vs.loc[c["candidate_id"], "mean"], yerr=vs.loc[c["candidate_id"], "se"], fmt="o",
                    color="tab:red" if c["candidate_id"] == recommended else "tab:blue", capsize=5)
    ax.set_xticks(range(len(fins)))
    ax.set_xticklabels([f"{FAMILY_LABEL[c['family']]}\n({c['source'].split(' (')[0]})" for c in fins], fontsize=7)
    ax.set_ylabel(metric.upper() + unit)
    ax.set_title(f"{task}: finalists, validation {metric} per fold (grey), mean ± SE; red = recommendation")
    fig.tight_layout()
    w.figure("finalists", fig, ftab[["candidate_id", "family", "source", "validation_mean", "validation_se", "recommended"]],
             ids=("8.1", "8.2"), title="Finalists")
    plt.close(fig)

    # 8.3 Calibration and 8.4 threshold (classification) -----------------------------------
    sel = {"task": task, "recommended": recommended, "spec": rec_spec["spec"], "calibration": None}
    if task == "classification":
        cal_spec = dict(rec_spec["spec"], calibration="sigmoid")
        cal_rows, cal_preds, sorted_ok = [], [], []
        for k, tr_ids, va_ids in fold_list:
            sorted_ok.append(bool(d.loc[tr_ids, "purchase_ts"].is_monotonic_increasing))
            Xtr, ytr = d.loc[tr_ids, cols], d.loc[tr_ids, y_col].to_numpy()
            Xva, yva = d.loc[va_ids, cols], d.loc[va_ids, y_col].to_numpy()
            cm = factory.build(cal_spec)
            single_threaded(cm.estimator)
            raw_p = preds[(preds["candidate_id"] == recommended) & (preds["fold"] == k)]["y_pred"].to_numpy()
            cm.fit(Xtr, ytr)
            cal_p = cm.predict_proba(Xva)[:, 1]
            for name, pp in (("raw", raw_p), ("sigmoid", cal_p)):
                s = score(task, yva, proba=pp)
                cal_rows.append({"variant": name, "fold": k, "ap": s["ap"], "brier": s["brier"], "roc_auc": s["roc_auc"]})
            cal_preds.append(pd.DataFrame({"order_id": va_ids, "fold": k, "y_true": yva, "raw": raw_p, "sigmoid": cal_p}))
        ct = pd.DataFrame(cal_rows)
        w.table("calibration_folds", ct, ids=("8.3",))
        cp = pd.concat(cal_preds, ignore_index=True)
        g = ct.groupby("variant")
        mean, sd = g.mean(numeric_only=True), g.std(ddof=1, numeric_only=True)
        ap_se = sd.loc["raw", "ap"] / np.sqrt(len(fold_list))
        keep_cal = bool(mean.loc["sigmoid", "brier"] < mean.loc["raw", "brier"] and mean.loc["sigmoid", "ap"] >= mean.loc["raw", "ap"] - ap_se)
        sel["calibration"] = "sigmoid" if keep_cal else None
        w.decision("Calibrate the recommended model?", "keep sigmoid only if mean Brier improves and mean AP stays within one "
                   "fold SE of the raw model (G-16, G-45, G-52)", ["raw", "sigmoid"], "sigmoid" if keep_cal else "raw",
                   ["calibration_folds.csv"], ids=("8.3",),
                   notes=f"mean Brier raw {mean.loc['raw', 'brier']:.5f}, sigmoid {mean.loc['sigmoid', 'brier']:.5f}; mean AP raw "
                         f"{mean.loc['raw', 'ap']:.4f}, sigmoid {mean.loc['sigmoid', 'ap']:.4f} (one fold SE {ap_se:.4f})")
        fig, ax = plt.subplots(figsize=(5.5, 5))
        rel = []
        for name in ("raw", "sigmoid"):
            frac, mp = calibration_curve(cp["y_true"], cp[name], n_bins=10, strategy="quantile")
            ax.plot(mp, frac, marker="o", label=name)
            rel.append(pd.DataFrame({"variant": name, "mean_predicted": mp, "observed_share": frac}))
        ax.plot([0, 1], [0, 1], "k--", lw=0.8)
        ax.set(xlabel="mean predicted probability", ylabel="observed detractor share", title="Reliability, pooled out-of-fold")
        ax.legend()
        fig.tight_layout()
        rel = pd.concat(rel, ignore_index=True)
        w.curve("reliability_raw_vs_sigmoid", rel, ids=("8.3",))
        w.figure("calibration", fig, rel, ids=("8.3",), title="Calibration")
        plt.close(fig)

        # 8.4 thresholds on the chosen recipe's out-of-fold probabilities
        probs = cp["sigmoid" if keep_cal else "raw"].to_numpy()
        yt = cp["y_true"].to_numpy()
        vdays = 0.0
        for k, _, va_ids in fold_list:
            ts_ = d.loc[va_ids, "purchase_ts"]
            vdays += (ts_.max().normalize() - ts_.min().normalize()).days + 1
        emp = empirical_cost_minimum(yt, probs, COST_FN, COST_FP)
        cand = {"no alerts": float("inf"), "0.50": 0.5, "1/6 (cost cutoff)": 1 / 6,
                "empirical minimum of 5*FN + FP": emp}
        tt = threshold_rows(yt, probs, cand, vdays, COST_FN, COST_FP)
        w.table("threshold_table", tt, ids=("8.4",))
        grid = np.round(np.arange(0.02, 0.61, 0.01), 2)
        tc = threshold_rows(yt, probs, {f"{t:.2f}": t for t in grid}, vdays, COST_FN, COST_FP)
        w.curve("threshold_curve", tc, ids=("8.4",))
        fig, axes = plt.subplots(1, 2, figsize=(12, 4))
        tc2 = tc.sort_values("threshold")
        axes[0].plot(tc2["threshold"], tc2["cost"], label="cost 5*FN + FP")
        for name, t in cand.items():
            if np.isfinite(t):
                axes[0].axvline(t, ls=":", lw=0.8)
                axes[0].text(t, tc2["cost"].max(), name, rotation=90, fontsize=6, va="top")
        axes[0].set(xlabel="threshold", ylabel="illustrative cost", title="Cost by threshold (out-of-fold)")
        axes[1].plot(tc2["alerts_per_day"], tc2["precision"], label="precision")
        axes[1].plot(tc2["alerts_per_day"], tc2["recall"], label="recall")
        axes[1].set(xlabel="alerts per day", title="Precision and recall vs alert volume")
        axes[1].legend()
        fig.tight_layout()
        w.figure("threshold_tradeoff", fig, tc2, ids=("8.4",), title="Threshold trade-off")
        plt.close(fig)
        team_t = None
        if decided:
            dt = decisions["threshold"]
            row = threshold_rows(yt, probs, {"team decision": float(dt["value"])}, vdays, COST_FN, COST_FP).iloc[0]
            team_t = {"value": float(dt["value"]), "daily_alert_cap": dt.get("daily_alert_cap"),
                      "applies_to": "sigmoid-calibrated probability" if keep_cal else "raw probability",
                      "oof_alerts_per_day": float(row.alerts_per_day), "oof_precision": float(row.precision),
                      "oof_recall": float(row.recall), "oof_cost": float(row.cost)}
            sel["threshold"] = team_t
        w.decision("Alert threshold", "hard stop: the team picks from the trade-off table (G-39); default recommendation: "
                   "minimise the illustrative cost subject to any daily alert cap (G-56)", list(cand),
                   (f"{team_t['value']:.4f} (daily alert cap {team_t['daily_alert_cap']})" if team_t else "awaiting the team"),
                   ["threshold_table.csv", "curves/threshold_curve.csv"] + (["human_decisions.yaml"] if team_t else []), ids=("8.4",),
                   notes=f"empirical cost minimum at {emp:.4f}; validation days {vdays:.0f}" + (
                       f"; team decision {decisions['threshold']['decided_by']}, {decisions['threshold']['date']}: "
                       f"{decisions['threshold']['rationale']}" if team_t else ""))
    w.json("selected_spec", sel, ids=("8.2",) + (("8.3",) if task == "classification" else ()))

    # learning curves of the recommendation (from s06, for the pack)
    lc = s06_lc[s06_lc["candidate_id"] == recommended] if recommended in set(s06_lc["candidate_id"]) else s06_lc.iloc[0:0]

    # Checks --------------------------------------------------------------------------------------
    s06_val = s06_ml[(s06_ml["phase"] == "validation") & (s06_ml["metric"] == metric)].copy()
    s06_val["value"] = pd.to_numeric(s06_val["value"])
    repro = []
    for c in fins:
        ref = s06_val[s06_val["candidate_id"] == c["candidate_id"]].sort_values("fold")["value"].to_numpy()
        if len(ref):
            mine = val[val["candidate_id"] == c["candidate_id"]].sort_values("fold")["value"].to_numpy()
            repro.append(np.allclose(mine, ref, rtol=0, atol=1e-9))
    w.check("finalists refitted on the same rows and folds reproduce their s06 fold scores", bool(repro) and all(repro),
            ("8.1",), f"{sum(repro)} of {len(repro)} reproduced")
    w.check("finalists: the dummy, plain linear/logistic and single tree references plus each family's s07 carried model",
            {"dummy", "linear", "tree", "forest"} <= {c["family"] for c in fins}, ("8.1",),
            f"{len(fins)} finalists")
    used = np.concatenate([np.concatenate([t, v]) for _, t, v in fold_list])
    w.check("no test row read: every row used was purchased before the test cutoff", bool(d.loc[used, "purchase_ts"].max() < cutoff),
            ("8.1", "8.2"), f"latest purchase {d.loc[used, 'purchase_ts'].max()}, cutoff {cutoff}")
    recipe = None
    if decided:
        chosen = decisions["model"]["chosen"]
        if chosen != recommended:
            raise SystemExit(f"s08 {task}: the team chose {chosen}, not the recommendation {recommended}; 8.3-8.4 must be "
                             "rerun on the chosen model before the freeze (blueprint 8.2)")
        recipe = frozen_recipe(task, rec_spec["spec"], sel["calibration"], sel.get("threshold"), decisions, cutoff, seed)
        w.json("frozen_recipe", recipe, ids=("8.5",))
        w.decision("Model chosen at the s08 gate", "team decision in human_decisions.yaml s08.model (G-39)", order, chosen,
                   ["human_decisions.yaml", "candidates.csv"], ids=("8.2", "8.5"),
                   notes=f"{decisions['model']['decided_by']}, {decisions['model']['date']}: {decisions['model']['rationale']}")
        w.check("frozen recipe follows the team decisions: chosen model is a finalist and the recommendation",
                chosen in order and chosen == recommended, ("8.5",), chosen)
        if task == "classification":
            cap = team_t["daily_alert_cap"]
            w.check("the decided threshold keeps the out-of-fold alerts within the daily cap",
                    cap is None or team_t["oof_alerts_per_day"] <= cap, ("8.4", "8.5"),
                    f"{team_t['oof_alerts_per_day']:.1f} alerts/day at {team_t['value']:.4f}, cap {cap}")
        w.check("frozen before any test row is read: the run uses development rows only, all purchased before the cutoff",
                bool(d.loc[used, "purchase_ts"].max() < cutoff), ("8.5",), f"sha256 {recipe['sha256']}")
    else:
        frozen = outputs_dir(STAGE, task) / "frozen_recipe.json"
        w.check("the run stops at the gate: no frozen_recipe.json, the test cohort is not read (G-39, G-78)", not frozen.exists(),
                ("8.2",), "team decisions in human_decisions.yaml s08: not yet made")
    if task == "classification":
        w.check("calibration inner splits are time-ordered: every training fold sorted by purchase time", all(sorted_ok), ("8.3",))

    # Evidence cards --------------------------------------------------------------------------
    w.explain("8.1", done=f"{len(fins)} finalists refitted on the five s05 folds: " + "; ".join(
        f"{FAMILY_LABEL[c['family']]} ({c['source']}) {vs.loc[c['candidate_id'], 'mean']:.4f} ± {vs.loc[c['candidate_id'], 'se']:.4f}{unit}"
        for c in fins) + f" (validation {metric}, mean ± SE).",
        inputs="s06 metrics and learning curves; s07 counts.json (carried model per family) and grid_results.csv; s05 folds.")
    w.explain("8.2", done=f"One-SE recommendation: {FAMILY_LABEL[fam_of[recommended]]} (best mean: {FAMILY_LABEL[fam_of[rec['best']]]}). "
              "Ladder basic to complex: " + "; ".join(
                  f"{FAMILY_LABEL[fam_of[s['complex']]]} {'kept' if s['complex_kept'] else 'not kept'} over "
                  f"{FAMILY_LABEL[fam_of[s['simpler']]]} (paired gain {s['paired']['mean_gain']:+.4f}{unit}, better in "
                  f"{s['paired']['folds_better']} of 5 folds)" for s in steps) + f"; ladder result {FAMILY_LABEL[fam_of[lad_result]]}. "
              f"Grid edge of the recommendation: {ftab.set_index('candidate_id').loc[recommended, 'grid_edge']}.",
              reasoning="The recommendation follows the pre-registered rule; the team confirms or overrides it at the gate "
                        "(G-39), and an override is logged as a protocol deviation (G-44). Validation scores are selection "
                        "scores, not generalisation estimates (G-10).",
              conclusion=("The team confirmed the recommendation at the combined review of s06-s08 (human_decisions.yaml s08, "
                          f"{decisions['model']['date']})." if decided else
                          "The run stops here. Under G-78 the team reviews s06, s07 and s08 together before the freeze, "
                          "the final fit and the single test (8.5-8.8)."))
    if task == "classification":
        w.explain("8.3", done=f"Raw vs sigmoid (CalibratedClassifierCV, time-ordered inner splits) on the recommended model, "
                  f"per fold: mean Brier raw {mean.loc['raw', 'brier']:.5f} vs sigmoid {mean.loc['sigmoid', 'brier']:.5f}; mean AP "
                  f"raw {mean.loc['raw', 'ap']:.4f} vs sigmoid {mean.loc['sigmoid', 'ap']:.4f} (one fold SE {ap_se:.4f}). "
                  f"Kept: {'sigmoid' if keep_cal else 'raw probabilities'}.")
        best = tt[tt["candidate"] == "empirical minimum of 5*FN + FP"].iloc[0]
        w.explain("8.4", done="Threshold candidates on the out-of-fold probabilities of the "
                  f"{'calibrated' if keep_cal else 'raw'} recommended model ({len(yt):,} validation rows, {vdays:.0f} days): " + "; ".join(
                      f"{r.candidate} (t={r.threshold:.4f}): {r.alerts_per_day:.1f} alerts/day, precision {r.precision:.3f}, recall "
                      f"{r.recall:.3f}, cost {r.cost:,.0f}" for r in tt.itertuples() if np.isfinite(r.threshold)) +
                  f"; no alerts: cost {tt[tt['candidate'] == 'no alerts']['cost'].iloc[0]:,.0f}.",
                  reasoning="Under the 5:1 cost an alert pays off while the extra false alarms per extra detractor caught stay "
                            "at or below 5 (Elkan 2001). The threshold is a business choice: the team picks it at the hard stop, "
                            "with an optional daily alert cap (G-39, G-56).")
    if recipe:
        t = recipe["threshold"]
        w.explain("8.5", done=f"Recipe frozen for {recipe['model']}: {len(recipe['features']['numeric'])} numeric and "
                  f"{len(recipe['features']['categorical'])} categorical features, estimator {recipe['estimator']}, calibration "
                  f"{recipe['calibration'] or 'none'}" + (f", threshold {t['value']:.4f} on the {t['applies_to']} (daily alert cap "
                  f"{t['daily_alert_cap']}; out-of-fold {t['oof_alerts_per_day']:.1f} alerts/day)" if t else "") +
                  f"; sha256 {recipe['sha256']}. Written from development rows only; the test cohort is not loaded.",
                  inputs="spec/human_decisions.yaml s08 (team decisions, 2026-10-23); this run's finalists, calibration and "
                         "threshold table.",
                  conclusion="Pipeline A stops after the freeze. The final fit, the single test read and the bundle (8.6-8.8) "
                             "run together with Pipeline B (lead decision 2026-10-23; draft G-79).")
    w.json("counts", {"task": task, "finalists": order, "recommended": recommended, "best_mean": rec["best"],
                      "ladder_result": lad_result, "calibration": sel["calibration"],
                      "stopped_after": "8.5 (frozen)" if recipe else "8.4 (gate)",
                      "frozen_sha256": recipe["sha256"] if recipe else None, "seed": seed},
           ids=("8.1", "8.2") + (("8.5",) if recipe else ()))
    w.text("selection_review_pack.md", selection_pack(task, ftab, pg, recommended, lad_result, fam_of, lc, unit,
                                                      tt if task == "classification" else None,
                                                      (mean, ap_se, keep_cal) if task == "classification" else None, recipe),
           ids=("8.2",) + (("8.3", "8.4") if task == "classification" else ()) + (("8.5",) if recipe else ()))
    w.finish(seed=seed)
    if w.index["checks_failed"]:
        raise SystemExit(f"s08 {task}: checks failed: {w.index['checks_failed']}")
    print(f"s08 {task}: " + (f"frozen (8.5), sha256 {recipe['sha256'][:12]}; stops before the test (waits for Pipeline B)" if recipe
                             else f"stopped at the gate (G-39, G-78); team decisions go to spec/human_decisions.yaml s08.{task}"))


def selection_pack(task, ftab, pg, recommended, lad_result, fam_of, lc, unit, tt, cal, recipe=None) -> str:
    """selection_review_pack.md: what the team needs at the gate, generated from the outputs."""
    def tab(df, ff=4):
        df = df.copy()
        for c in df.columns:
            if pd.api.types.is_float_dtype(df[c]):
                df[c] = df[c].map(lambda v: "" if pd.isna(v) else f"{v:.{ff}f}")
        return "\n".join(["| " + " | ".join(map(str, df.columns)) + " |", "| " + " | ".join("---" for _ in df.columns) + " |"] +
                         ["| " + " | ".join(str(v) for v in r) + " |" for r in df.itertuples(index=False)])
    keep = [c for c in ftab.columns if c in ("family", "source", "validation_mean", "validation_se", "train_validation_gap",
                                             "grid_edge", "recommended")]
    out = [f"# s08 selection review pack: {task}", "",
           f"Recommendation (one-SE rule, s01 1.7): **{FAMILY_LABEL[fam_of[recommended]]}** (`{recommended}`). "
           f"Ladder result (each more complex family kept only beyond one SE): {FAMILY_LABEL[fam_of[lad_result]]}.", "",
           "## Finalists (validation, mean over the five folds)", "", tab(ftab[keep]), "",
           "## Every s01 metric (mean and SE over the folds)", "",
           tab(ftab[["family"] + [c for c in ftab.columns if (c.endswith("_mean") or c.endswith("_se"))
                                  and c not in ("train_mean", "validation_mean", "validation_se")]]), "",
           "## Ladder, basic to complex (paired gains are description only)", "",
           tab(pg.drop(columns=["simpler", "complex"])), ""]
    if len(lc):
        out += ["## Learning curves of the recommendation (s06, latest fold)", "", tab(lc.drop(columns=["candidate_id"])), ""]
    if tt is not None:
        mean, ap_se, keep_cal = cal
        out += ["## Calibration (8.3)", "", f"Mean Brier raw {mean.loc['raw', 'brier']:.5f}, sigmoid {mean.loc['sigmoid', 'brier']:.5f}; "
                f"mean AP raw {mean.loc['raw', 'ap']:.4f}, sigmoid {mean.loc['sigmoid', 'ap']:.4f}; one fold SE of raw AP {ap_se:.4f}. "
                f"Kept: {'sigmoid' if keep_cal else 'raw'}.", "",
                "## Threshold candidates (8.4, hard stop)", "",
                tab(tt[["candidate", "threshold", "alerts_per_day", "alert_rate", "error_rate", "precision", "recall", "f1", "cost",
                        "extra_false_alarms_per_extra_detractor"]]), ""]
    if recipe:
        dm, t = recipe["decisions"]["model"], recipe["threshold"]
        out += ["## Team decision and freeze (8.5)", "",
                f"Model: `{dm['chosen']}` (recommended `{dm['recommended']}`), grid edge action {dm['grid_edge_action']}; "
                f"{dm['decided_by']}, {dm['date']}: {dm['rationale']}.", ""]
        if t:
            out += [f"Threshold: {t['value']:.4f} on the {t['applies_to']}, daily alert cap {t['daily_alert_cap']}; out-of-fold "
                    f"{t['oof_alerts_per_day']:.1f} alerts/day, precision {t['oof_precision']:.3f}, recall {t['oof_recall']:.3f}.", ""]
        out += [f"Frozen recipe: frozen_recipe.json, sha256 `{recipe['sha256']}`. The test cohort is not read; the final fit, "
                "test and bundle (8.6-8.8) run together with Pipeline B.", ""]
    else:
        out += ["## Team decision", "",
                f"Record in spec/human_decisions.yaml, section s08.{task}: `model` (chosen, recommended, rationale, grid_edge_action, "
                "decided_by, date)" + (", `threshold` (value, daily_alert_cap, rationale, decided_by, date)" if tt is not None else "") +
                ". Under G-78 this is decided at the combined review of s06-s08; only then do 8.5-8.8 run.", ""]
    return "\n".join(out)
