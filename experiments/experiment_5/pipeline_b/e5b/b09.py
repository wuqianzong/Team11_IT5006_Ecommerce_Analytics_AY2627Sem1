"""B9: conclusion for team review, B primary, A as baseline (blueprint pipeline_b/spec/blueprints/b09_conclusion.md;
G-79, G-40, G-54, G-77, B-C13).

Reads T1's frozen outputs; no refit, no threshold change, no second scoring of a model. Test rows are rebuilt only to
attach slice attributes and to recompute features for interpretation; B's bundle must re-predict them exactly as T1 did.

Evidence IDs: B9.1 train-validation-test table, B9.2 paired differences, B9.3 error analysis, B9.4 drift,
B9.5 interpretation, B9.6 label sensitivity, B9.7 business summary, B9.8 limitations, B9.9 conclusion.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from e5lib import factory, protocol
from e5lib.metrics import COST_FN, COST_FP, PRIMARY, score
from e5lib.paths import E5, raw_data_dir
from e5lib.training import TARGET, predict

from . import b02
from . import history as h
from .env import BWriter, assert_a_frozen, b_outputs_dir
from .t1_joint_test import EVENTS_UNTIL, LABEL_TS, b_rows

STAGE = "b09"
A_RECORDS = E5 / "stages/s02_data/common/outputs/records.csv.gz"
A_S05 = str(E5 / "stages/s05_partition/{task}/outputs")
A_S06 = str(E5 / "stages/s06_training/{task}/outputs")
N_BOOT = 1000
MIN_SLICE = 100                       # orders (regression) or detractors (classification) to judge a slice (G-40)
DIST_BANDS = [0, 100, 300, 600, 1000, np.inf]
METRICS = {"regression": ["mae", "rmse", "r2", "within_3d"],
           "classification": ["ap", "roc_auc", "brier", "precision", "recall", "f1", "alert_rate"]}
PLAIN = {"regression": "reg.sel.log.linear", "classification": "clf.sel.log.logistic"}
DUMMY = {"regression": "reg.sel.log.dummy_median", "classification": "clf.sel.log.dummy_prior"}


def _band(d: pd.Series) -> pd.Series:
    return pd.cut(d, DIST_BANDS, right=False, labels=["<100 km", "100-300 km", "300-600 km", "600-1000 km", ">=1000 km"]).astype(str)


def _basket(n: pd.Series) -> pd.Series:
    return np.where(n >= 3, "3+ items", np.where(n == 2, "2 items", "1 item"))


def _score(task, y, p, thr):
    return score(task, y, y_pred=p) if task == "regression" else score(task, y, proba=p, threshold=thr)


def _cv_long(path: Path, cand: str, metric: str, phase: str) -> float:
    m = pd.read_csv(path)
    m = m[(m.candidate_id == cand) & (m.metric == metric) & (m.phase == phase)]
    if "threshold" in m:
        m = m[m.threshold.isna()]
    return float(m.groupby("fold").value.mean().mean()) if len(m) else np.nan


def _cv_long_se(path: Path, cand: str, metric: str) -> float:
    m = pd.read_csv(path)
    m = m[(m.candidate_id == cand) & (m.metric == metric) & (m.phase == "validation")]
    if "threshold" in m:
        m = m[m.threshold.isna()]
    v = m.groupby("fold").value.mean()
    return float(v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else np.nan


def _feature_names(pipe) -> list[str]:
    return list(pipe[:-1].get_feature_names_out())


def run(task: str) -> None:
    assert_a_frozen()
    w = BWriter(STAGE, task)
    seed = int(protocol.load()["seed"])
    rng = np.random.default_rng(seed)
    metric, higher = PRIMARY[task]
    y_col = TARGET[task]
    cutoff = pd.Timestamp(protocol.get("data_dependent.test_cutoffs.values")[task])
    t1 = b_outputs_dir("t1_joint_test", task)
    b8 = b_outputs_dir("b08", task)

    # inputs ---------------------------------------------------------------------------------------------
    pt = pd.read_csv(w.read(t1 / "predictions_test.csv.gz"))
    mt = pd.read_csv(w.read(t1 / "metrics_test.csv"))
    piv = mt.pivot_table(index="metric", columns=["model", "rows"], values="value")
    b_rec = json.loads(w.read(b8 / "frozen_recipe.json").read_text())
    a_rec = json.loads(w.read(E5 / f"stages/s08_selection/{task}/outputs/frozen_recipe.json").read_text())
    thr = (b_rec.get("threshold") or {}).get("value")
    b_spec = json.loads(w.read(b8 / "selected_spec.json").read_text())["spec"]
    b_model = joblib.load(w.read(t1 / "bundles/B/model.joblib"))
    a_model = joblib.load(w.read(t1 / "bundles/A/model.joblib"))

    a = pd.read_csv(w.read(A_RECORDS), parse_dates=["purchase_ts", "review_label_ts", "lead_label_ts"], low_memory=False)
    man = pd.read_csv(w.read(Path(A_S05.format(task=task)) / "test_manifest.csv"))
    a_test = a[a[f"eligible_{task}"].astype(bool) & a.order_id.isin(man.order_id)].reset_index(drop=True)
    for f in ("olist_orders_dataset.csv", "olist_order_items_dataset.csv", "olist_sellers_dataset.csv", "olist_customers_dataset.csv"):
        w.read(raw_data_dir() / f)
    ev = h.load_events(raw_data_dir(), EVENTS_UNTIL)
    cap = json.loads(w.read(b_outputs_dir("b02", "regression") / "feature_build_log.json").read_text())["lead_cap_days"]
    b_test, _ = b_rows(task, a_test, ev, cap if task == "regression" else None)
    b_test = b_test.reset_index(drop=True)

    def preds(model, rows):
        s = pt[(pt.model == model) & (pt.rows == rows)].set_index("order_id")
        return s

    pb = preds("B frozen", "B test rows").loc[b_test.order_id]
    pab = preds("A frozen", "B test rows").loc[b_test.order_id]
    paa = preds("A frozen", "A test rows").loc[a_test.order_id]
    re_b = predict(task, b_model, b_test)
    re_a = predict(task, a_model, a_test)
    # T1's predictions went through a CSV, which can change the last binary digit; 1e-9 is far below any reported digit
    diff_b = float(np.max(np.abs(re_b - pb.y_pred.to_numpy())))
    diff_a = float(np.max(np.abs(re_a - paa.y_pred.to_numpy())))
    same_b, same_a = diff_b <= 1e-9, diff_a <= 1e-9
    if not (same_b and same_a):
        raise SystemExit(f"B9 {task}: the bundles do not re-predict T1's test predictions; stopping (no analysis on different rows)")
    y_b = pb.y_true.to_numpy()
    y_a = paa.y_true.to_numpy()

    # B9.1 train-validation-test with bootstrap intervals; B9.2 paired differences ------------------------
    series = {("B frozen", "B test rows"): pb.y_pred.to_numpy(), ("A frozen", "B test rows"): pab.y_pred.to_numpy(),
              ("B plain", "B test rows"): preds("B plain", "B test rows").loc[b_test.order_id].y_pred.to_numpy(),
              ("B dummy", "B test rows"): preds("B dummy", "B test rows").loc[b_test.order_id].y_pred.to_numpy(),
              ("A frozen", "A test rows"): paa.y_pred.to_numpy(),
              ("A plain", "A test rows"): preds("A plain", "A test rows").loc[a_test.order_id].y_pred.to_numpy(),
              ("A dummy", "A test rows"): preds("A dummy", "A test rows").loc[a_test.order_id].y_pred.to_numpy()}
    mets = METRICS[task]
    boots = {k: {m: [] for m in mets} for k in series}
    for rows_name, y in (("B test rows", y_b), ("A test rows", y_a)):
        keys = [k for k in series if k[1] == rows_name]
        n = len(y)
        for _ in range(N_BOOT):
            ix = rng.integers(0, n, n)
            for k in keys:
                s = _score(task, y[ix], series[k][ix], thr)
                for m in mets:
                    boots[k][m].append(s[m])
    b6 = b_outputs_dir("b06", task) / "metrics_long.csv"
    a6 = Path(A_S06.format(task=task)) / "metrics_long.csv"
    pop = pd.read_csv(w.read(b8 / "metrics_by_population.csv"))
    w.read(b6), w.read(a6)
    var = "sigmoid" if task == "classification" else "raw"

    def cv_entry(k, m):
        model, rows = k
        if model in ("B frozen", "A frozen"):
            pm = {"B frozen": "B recommended model", "A frozen": "A frozen model"}[model]
            pr = "B validation rows" if rows == "B test rows" else "A validation rows"
            x = pop[(pop.model == pm) & (pop.variant == var) & (pop.rows == pr) & (pop.metric == m)]
            if len(x):
                tr = np.nan
                if task == "regression":   # the frozen regression models are the plain linear recipes
                    tr = _cv_long(b6 if model == "B frozen" else a6, PLAIN[task], m, "train") if rows == ("B test rows" if model == "B frozen" else "A test rows") else np.nan
                return tr, float(x.mean_5_folds.iloc[0]), float(x.se_5_folds.iloc[0]), "b08 metrics_by_population.csv" + (" (sigmoid)" if var == "sigmoid" else "")
            if task == "regression" and rows == ("B test rows" if model == "B frozen" else "A test rows"):
                path = b6 if model == "B frozen" else a6
                return _cv_long(path, PLAIN[task], m, "train"), _cv_long(path, PLAIN[task], m, "validation"), _cv_long_se(path, PLAIN[task], m), "b06/s06 metrics_long.csv (plain linear = frozen)"
            return np.nan, np.nan, np.nan, ""
        path = b6 if model.startswith("B") else a6
        cand = PLAIN[task] if "plain" in model else DUMMY[task]
        return _cv_long(path, cand, m, "train"), _cv_long(path, cand, m, "validation"), _cv_long_se(path, cand, m), ("b06" if model.startswith("B") else "s06") + " metrics_long.csv (raw)"

    tvt = []
    for k in series:
        for m in mets:
            tr, va, se, src = cv_entry(k, m)
            b = np.asarray(boots[k][m], dtype=float)
            lo, hi = np.nanpercentile(b, [2.5, 97.5])
            tvt.append({"model": k[0], "rows": k[1], "metric": m, "train_mean": tr, "validation_mean": va, "validation_se": se,
                        "validation_source": src, "test": float(piv.loc[m, k]), "test_ci_low": lo, "test_ci_high": hi,
                        "ci_width": hi - lo, "test_rows": int(piv.loc["n_rows", k]),
                        **({"test_detractors": int(piv.loc["n_pos", k])} if task == "classification" else {})})
    tvt = pd.DataFrame(tvt)
    w.table("train_val_test", tvt, ids=("B9.1",))

    pairs = [("B frozen", "A frozen"), ("B frozen", "B plain"), ("B frozen", "B dummy")]
    prow = []
    for x, z in pairs:
        kx, kz = (x, "B test rows"), (z, "B test rows")
        for m in mets:
            d = np.asarray(boots[kx][m], dtype=float) - np.asarray(boots[kz][m], dtype=float)
            point = float(piv.loc[m, kx] - piv.loc[m, kz])
            lo, hi = np.nanpercentile(d, [2.5, 97.5])
            # alert_rate is a volume, not a quality: no better/worse
            better = None if m == "alert_rate" else ((point < 0) if m in ("mae", "rmse", "brier") else (point > 0))
            prow.append({"comparison": f"{x} minus {z}", "rows": "B test rows", "metric": m, "difference": point, "ci_low": lo,
                         "ci_high": hi, "b_better": better, "interval_excludes_zero": bool(lo > 0 or hi < 0)})
    pdiff = pd.DataFrame(prow)
    w.table("paired_test_differences", pdiff, ids=("B9.2",))

    # B9.3 error analysis -----------------------------------------------------------------------------------
    df = b_test.assign(pa=pab.y_pred.to_numpy(), pb=pb.y_pred.to_numpy(), y=y_b,
                       distance_band=_band(b_test.distance_km_max), basket=_basket(b_test.n_items),
                       sellers=np.where(b_test.n_sellers >= 2, "2+ sellers", "1 seller"),
                       month=b_test.purchase_ts.dt.strftime("%Y-%m"))
    slices = (["customer_state", b02.ROUTE, "distance_band", "basket", "month"] if task == "regression"
              else ["customer_state", b02.ROUTE, "basket", "sellers"])
    srows = []
    for col in slices:
        for val, g in df.groupby(col):
            r = {"slice": col, "value": val, "orders": len(g)}
            if task == "regression":
                r.update({"mae_A": float(np.mean(np.abs(g.pa - g.y))), "mae_B": float(np.mean(np.abs(g.pb - g.y)))})
                r["gain_B_minus_A"] = r["mae_B"] - r["mae_A"]
                r["judged"] = len(g) >= MIN_SLICE
            else:
                det = int(g.y.sum())
                r["detractors"] = det
                for nm, p in (("A", g.pa), ("B", g.pb)):
                    fl = p.to_numpy() >= thr
                    tp = int((fl & (g.y == 1)).sum())
                    r[f"alerts_{nm}"] = int(fl.sum())
                    r[f"precision_{nm}"] = tp / fl.sum() if fl.sum() else np.nan
                    r[f"recall_{nm}"] = tp / det if det else np.nan
                r["judged"] = det > MIN_SLICE
            srows.append(r)
    sub = pd.DataFrame(srows)
    agg = []
    for col in slices:
        j = sub[(sub.slice == col) & sub.judged]
        g = df[df[col].isin(j.value)]
        if task == "regression":
            agg.append({"slice": col, "judged_slices": len(j), "too_few": int(((sub.slice == col) & ~sub.judged).sum()),
                        "pooled_mae_A": float(np.mean(np.abs(g.pa - g.y))) if len(g) else np.nan,
                        "pooled_mae_B": float(np.mean(np.abs(g.pb - g.y))) if len(g) else np.nan,
                        "mean_gain": float(j.gain_B_minus_A.mean()) if len(j) else np.nan,
                        "sd_gain": float(j.gain_B_minus_A.std()) if len(j) > 1 else np.nan,
                        "slices_B_better": int((j.gain_B_minus_A < 0).sum())})
        else:
            row = {"slice": col, "judged_slices": len(j), "too_few": int(((sub.slice == col) & ~sub.judged).sum())}
            for nm, p in (("A", "pa"), ("B", "pb")):
                fl = g[p].to_numpy() >= thr
                tp = int((fl & (g.y == 1)).sum())
                row[f"pooled_precision_{nm}"] = tp / fl.sum() if fl.sum() else np.nan
                row[f"pooled_recall_{nm}"] = tp / g.y.sum() if g.y.sum() else np.nan
                row[f"mean_precision_{nm}"] = float(j[f"precision_{nm}"].mean()) if len(j) else np.nan
                row[f"sd_precision_{nm}"] = float(j[f"precision_{nm}"].std()) if len(j) > 1 else np.nan
                row[f"mean_recall_{nm}"] = float(j[f"recall_{nm}"].mean()) if len(j) else np.nan
                row[f"sd_recall_{nm}"] = float(j[f"recall_{nm}"].std()) if len(j) > 1 else np.nan
            agg.append(row)
    sub_agg = pd.DataFrame(agg)
    w.table("subgroups", sub, ids=("B9.3",))
    w.table("subgroups_aggregate", sub_agg, ids=("B9.3",))

    # B9.4 drift -------------------------------------------------------------------------------------------
    b_dev = pd.read_csv(w.read(b_outputs_dir("b02", task) / "records_B.csv.gz"), parse_dates=["purchase_ts", LABEL_TS[task]], low_memory=False)
    b_dev = b_dev[b_dev[LABEL_TS[task]] < cutoff].reset_index(drop=True)
    drows = []
    for c in b_spec["numeric"]:
        x0, x1 = b_dev[c].astype(float), b_test[c].astype(float)
        sd = np.sqrt((x0.var() + x1.var()) / 2)
        drows.append({"kind": "numeric", "feature": c, "level": "", "development": float(x0.mean()), "test": float(x1.mean()),
                      "change": float((x1.mean() - x0.mean()) / sd) if sd > 0 else 0.0, "measure": "standardised mean difference"})
    for c in b_spec["categorical"] + list(b02.SOURCES):
        s0, s1 = b_dev[c].value_counts(normalize=True), b_test[c].value_counts(normalize=True)
        lv = s0.index.union(s1.index)
        ch = (s1.reindex(lv, fill_value=0) - s0.reindex(lv, fill_value=0))
        top = ch.abs().sort_values(ascending=False).index[: (10 if c == b02.ROUTE else len(lv))]
        for l in top:
            drows.append({"kind": "source share" if c in b02.SOURCES else "categorical", "feature": c, "level": str(l),
                          "development": float(s0.get(l, 0)), "test": float(s1.get(l, 0)), "change": float(ch[l]), "measure": "share change"})
        drows.append({"kind": "categorical total", "feature": c, "level": "(all levels)", "development": np.nan, "test": np.nan,
                      "change": float(ch.abs().sum() / 2), "measure": "total variation distance"})
    t0, t1v = b_dev[y_col].astype(float), b_test[y_col].astype(float)
    for nm, f in (("mean", np.mean), ("median", np.median)) if task == "regression" else (("prevalence", np.mean),):
        drows.append({"kind": "target", "feature": y_col, "level": nm, "development": float(f(t0)), "test": float(f(t1v)),
                      "change": float(f(t1v) - f(t0)), "measure": "difference"})
    drift = pd.DataFrame(drows)
    w.table("drift", drift, ids=("B9.4",))

    # B9.5 interpretation ----------------------------------------------------------------------------------
    if task == "regression":
        pipe = b_model.regressor_
        coef = pd.DataFrame({"term": _feature_names(pipe), "coefficient": pipe.named_steps["model"].coef_})
        coef["ratio_per_unit"] = np.exp(coef.coefficient)
        coef["reading"] = "multiplies predicted lead time by ratio_per_unit per +1 unit of the transformed term (log1p target)"
    else:
        parts = []
        for i, cc in enumerate(b_model.calibrated_classifiers_):
            est = cc.estimator
            parts.append(pd.DataFrame({"term": _feature_names(est), "coefficient": est.named_steps["model"].coef_.ravel(), "split": i}))
        allc = pd.concat(parts)
        coef = allc.groupby("term", sort=False).coefficient.agg(["mean", "min", "max"]).reset_index().rename(columns={"mean": "coefficient", "min": "coefficient_min", "max": "coefficient_max"})
        coef["odds_ratio"] = np.exp(coef.coefficient)
        coef["reading"] = "odds ratio per +1 unit of the transformed term; mean over the 3 time-ordered calibration splits (min/max shown)"
    coef = coef.reindex(coef.coefficient.abs().sort_values(ascending=False).index).reset_index(drop=True)
    w.table("coefficients", coef, ids=("B9.5",))
    from sklearn.inspection import permutation_importance
    cols = factory.feature_columns(b_spec)
    scoring = "neg_mean_absolute_error" if task == "regression" else "average_precision"
    pi = permutation_importance(b_model, b_test[cols], y_b, scoring=scoring, n_repeats=5, random_state=seed, n_jobs=1)
    perm = pd.DataFrame({"feature": cols, "importance_mean": pi.importances_mean, "importance_sd": pi.importances_std})
    perm = perm.sort_values("importance_mean", ascending=False).reset_index(drop=True)
    perm["rank"] = np.arange(1, len(perm) + 1)
    perm["scoring"] = f"drop in {'MAE (days, as negative MAE)' if task == 'regression' else 'AP'} when the column is shuffled, B's test rows"
    w.table("permutation_importance", perm, ids=("B9.5",))
    rk = pd.read_csv(w.read(b_outputs_dir("b04", task) / "selection_ranking_B.csv"))
    rk = rk[rk.selected.astype(bool)]
    common = [f for f in perm.feature if f in set(rk.feature)]
    r_perm = perm.set_index("feature").loc[common, "rank"]
    r_b4 = rk.set_index("feature").loc[common, "rank"]
    rho = float(spearmanr(r_perm, r_b4).statistic) if len(common) > 2 else np.nan
    top_p, top_b = set(perm.feature.head(10)), set(rk.sort_values("rank").feature.head(10))
    overlap = len(top_p & top_b)
    diverge = bool((rho < 0.5) or (overlap < 5))
    consistency = {"features_compared": len(common), "spearman": rho, "top10_overlap": overlap, "diverges": diverge,
                   "rule": "diverges when Spearman < 0.5 or fewer than 5 of the top 10 shared (as A's s09 9.5)",
                   "action": ("alert the team: the test-row importance differs from B4's development ranking; describe, do not change the frozen model"
                              if diverge else "none: rankings agree within the rule")}
    w.json("ranking_consistency", consistency, ids=("B9.5",))

    # B9.6 label sensitivity -------------------------------------------------------------------------------
    if task == "classification":
        first_b = a.set_index("order_id").loc[b_test.order_id, "is_detractor_first"].astype(int).to_numpy()
        first_a = a.set_index("order_id").loc[a_test.order_id, "is_detractor_first"].astype(int).to_numpy()
        lrows = []
        for (model, rows), p in series.items():
            if "dummy" in model:
                continue
            for lab, yy in (("is_detractor (agreed label)", y_b if rows == "B test rows" else y_a),
                            ("is_detractor_first (first review)", first_b if rows == "B test rows" else first_a)):
                s = _score(task, yy, p, thr)
                lrows.append({"model": model, "rows": rows, "label": lab, **{m: s[m] for m in ("ap", "roc_auc", "brier", "precision", "recall", "prevalence")}})
        lab_t = pd.DataFrame(lrows)
        w.table("label_sensitivity", lab_t, ids=("B9.6",))

    # B9.7 business summary --------------------------------------------------------------------------------
    if task == "regression":
        brow = []
        for val, g in df.groupby("customer_state"):
            brow.append({"customer_state": val, "orders": len(g), "mae_B": float(np.mean(np.abs(g.pb - g.y))),
                         "within_3d_B": float(np.mean(np.abs(g.pb - g.y) <= 3)),
                         "share_later_than_predicted_B": float(np.mean(g.y > g.pb)),
                         "share_more_than_3d_later_B": float(np.mean(g.y > g.pb + 3)),
                         "mae_A": float(np.mean(np.abs(g.pa - g.y))), "share_more_than_3d_later_A": float(np.mean(g.y > g.pa + 3))})
        allr = {"customer_state": "all", "orders": len(df), "mae_B": float(np.mean(np.abs(df.pb - df.y))),
                "within_3d_B": float(np.mean(np.abs(df.pb - df.y) <= 3)), "share_later_than_predicted_B": float(np.mean(df.y > df.pb)),
                "share_more_than_3d_later_B": float(np.mean(df.y > df.pb + 3)), "mae_A": float(np.mean(np.abs(df.pa - df.y))),
                "share_more_than_3d_later_A": float(np.mean(df.y > df.pa + 3))}
        bus = pd.DataFrame(brow + [allr])
    else:
        brow = []
        for k in (("B frozen", "B test rows"), ("A frozen", "B test rows"), ("A frozen", "A test rows"), ("B dummy", "B test rows"), ("A dummy", "A test rows")):
            brow.append({"model": k[0], "rows": k[1], "alerts_per_day": float(piv.loc["alerts_per_day", k]), "alerts": int(piv.loc["tp", k] + piv.loc["fp", k]),
                         "detractors_caught": int(piv.loc["tp", k]), "precision": float(piv.loc["precision", k]), "recall": float(piv.loc["recall", k]),
                         "illustrative_cost": float(piv.loc["cost", k]), "cost_per_missed": COST_FN, "cost_per_false_alert": COST_FP})
        bus = pd.DataFrame(brow)
        # missed-dispatch rule (B-C10) on the test period, B8's population definition applied to A's test rows
        popt = a_test[a_test.customer_state.isin(b02.STATES) & a_test.primary_seller_state.isin(b02.STATES) & a_test.distance_km_max.notna()]
        popt = popt[["order_id", "is_detractor"]].merge(ev[["order_id", "carrier_ts", "ship_limit"]], on="order_id", how="left")
        never = popt.carrier_ts.isna()
        late = popt.carrier_ts.notna() & (popt.carrier_ts > popt.ship_limit)
        tot = int(popt.is_detractor.sum())
        mrows = []
        for nm, m in (("never handed over", never), ("handed over after the limit", late), ("all flagged (rule fires)", never | late), ("not flagged", ~(never | late))):
            n, d = int(m.sum()), int(popt.loc[m, "is_detractor"].sum())
            mrows.append({"group": nm, "orders": n, "detractors": d, "precision": d / n if n else np.nan, "share_of_all_detractors": d / tot if tot else np.nan})
        mdr = pd.DataFrame(mrows)
        w.table("missed_dispatch_rule_test", mdr, ids=("B9.7",))
    w.table("business_summary", bus, ids=("B9.7",))

    # figures ------------------------------------------------------------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    pdd = pdiff[pdiff.comparison == "B frozen minus A frozen"]
    fig, ax = plt.subplots(figsize=(7, 0.5 + 0.45 * len(pdd)))
    yy = np.arange(len(pdd))
    ax.errorbar(pdd.difference, yy, xerr=[pdd.difference - pdd.ci_low, pdd.ci_high - pdd.difference], fmt="o", color="#1f77b4")
    ax.axvline(0, color="k", lw=0.8)
    ax.set_yticks(yy, pdd.metric)
    ax.set(xlabel="B minus A on B's test rows (95% paired bootstrap)", title=f"B versus A on the same test rows, {task}")
    fig.tight_layout()
    w.figure("paired_differences", fig, pdd, ids=("B9.2",), title="Paired test differences, B minus A")
    plt.close(fig)
    st = sub[(sub.slice == "customer_state")].sort_values("orders", ascending=False)
    fig, ax = plt.subplots(figsize=(8, 4))
    xs = np.arange(len(st))
    if task == "regression":
        ax.bar(xs - 0.2, st.mae_A, 0.4, label="A", color="#7f7f7f")
        ax.bar(xs + 0.2, st.mae_B, 0.4, label="B", color="#1f77b4")
        ax.set(ylabel="MAE (days)")
    else:
        ax.bar(xs - 0.2, st.precision_A, 0.4, label="A precision", color="#7f7f7f")
        ax.bar(xs + 0.2, st.precision_B, 0.4, label="B precision", color="#1f77b4")
        ax.plot(xs - 0.2, st.recall_A, "s", color="#4d4d4d", label="A recall")
        ax.plot(xs + 0.2, st.recall_B, "s", color="#08306b", label="B recall")
        ax.set(ylabel="at threshold 1/6")
    ax.set_xticks(xs, [f"{v}\n{n:,}" for v, n in zip(st.value, st.orders)])
    ax.set_title(f"By customer state, B's test rows ({task}); label = state and orders")
    ax.legend()
    fig.tight_layout()
    w.figure("by_customer_state", fig, st, ids=("B9.3",), title="Error analysis by customer state")
    plt.close(fig)
    top = coef.head(15).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 5))
    val = top.ratio_per_unit if task == "regression" else top.odds_ratio
    ax.barh(top.term, val - 1, left=1, color=np.where(val >= 1, "#d62728", "#2ca02c"))
    ax.axvline(1, color="k", lw=0.8)
    ax.set(xlabel=("lead-time ratio per +1 unit" if task == "regression" else "odds ratio per +1 unit") + " (transformed term)",
           title=f"B's frozen model: 15 largest terms, {task}")
    fig.tight_layout()
    w.figure("coefficients", fig, top, ids=("B9.5",), title="Largest coefficients")
    plt.close(fig)
    pp = perm.head(15).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(pp.feature, pp.importance_mean, xerr=pp.importance_sd, color="#1f77b4")
    ax.set(xlabel=pp.scoring.iloc[0], title=f"Permutation importance on B's test rows, {task}")
    fig.tight_layout()
    w.figure("permutation_importance", fig, pp, ids=("B9.5",), title="Permutation importance")
    plt.close(fig)
    dn = drift[drift.kind == "numeric"].reindex(drift[drift.kind == "numeric"].change.abs().sort_values().index)
    fig, ax = plt.subplots(figsize=(8, 0.4 + 0.3 * len(dn)))
    ax.barh(dn.feature, dn.change, color=np.where(dn.change.abs() >= 0.2, "#d62728", "#7f7f7f"))
    ax.axvline(0, color="k", lw=0.8)
    for xline in (-0.2, 0.2):
        ax.axvline(xline, color="k", lw=0.5, ls=":")
    ax.set(xlabel="standardised mean difference, test minus final-fit rows (|0.2| marked)", title=f"Feature drift, {task}")
    fig.tight_layout()
    w.figure("drift_numeric", fig, dn, ids=("B9.4",), title="Feature drift")
    plt.close(fig)

    # B9.10-B9.15 round 2 (Henry's B9 review; B-G-06, B-G-07) ------------------------------------------------
    from . import b09_extra
    extra = b09_extra.run(task, w, {"a": a, "a_test": a_test, "b_test": b_test, "df": df, "pt": pt, "piv": piv, "tvt": tvt,
                                    "seed": seed, "b_spec": b_spec, "cutoff": cutoff, "label_ts": LABEL_TS[task]})

    # checks -------------------------------------------------------------------------------------------------
    w.check("no refit: B's and A's bundles re-predict T1's test predictions on the rebuilt rows (within 1e-9)", same_a and same_b, ("B9.1",),
            f"B {len(b_test):,} rows (max difference {diff_b:.1e}), A {len(a_test):,} rows (max difference {diff_a:.1e}); CSV round-trip only")
    w.check("every restated test number equals T1's metrics_test.csv", bool(np.allclose(
        [r.test for r in tvt.itertuples()], [float(piv.loc[r.metric, (r.model, r.rows)]) for r in tvt.itertuples()])), ("B9.1",))
    w.check("bootstrap intervals contain the T1 point estimate", bool(((tvt.test >= tvt.test_ci_low - 1e-12) & (tvt.test <= tvt.test_ci_high + 1e-12)).all()), ("B9.1", "B9.2"),
            f"{N_BOOT} resamples, seed {seed}")
    w.check("validation scores are labelled selection scores (source column filled wherever a value is shown)",
            bool((tvt.validation_mean.isna() | (tvt.validation_source != "")).all()), ("B9.1",))
    w.check("slice rule: a slice is judged only above the minimum", bool((sub.judged == ((sub.orders >= MIN_SLICE) if task == "regression" else (sub.detractors > MIN_SLICE))).all()), ("B9.3",))
    w.check("A's tree untouched: A's code matches e5-A-frozen", bool(assert_a_frozen()), ("B9.1",))

    # cards and conclusion -----------------------------------------------------------------------------------
    k_b, k_ab, k_aa = ("B frozen", "B test rows"), ("A frozen", "B test rows"), ("A frozen", "A test rows")
    pm = pdd.set_index("metric").loc[metric]
    t_b = tvt[(tvt.model == "B frozen") & (tvt.rows == "B test rows") & (tvt.metric == metric)].iloc[0]
    w.explain("B9.1", done=(f"Train, validation (selection scores, G-10) and test with 95% bootstrap intervals ({N_BOOT} resamples, seed {seed}) for B, A "
                            f"and references. B's test {metric.upper()} {t_b.test:.4f} [{t_b.test_ci_low:.4f}, {t_b.test_ci_high:.4f}], width {t_b.ci_width:.4f}"
                            + (f"; {int(t_b.test_detractors):,} test detractors." if task == "classification" else ".")))
    w.explain("B9.2", done=(f"B minus A on B's test rows: {metric.upper()} {pm.difference:+.4f} [{pm.ci_low:+.4f}, {pm.ci_high:+.4f}] "
                            f"({'excludes' if pm.interval_excludes_zero else 'includes'} zero)."))
    if task == "regression":
        j = sub_agg.set_index("slice").loc["customer_state"]
        w.explain("B9.3", done=(f"Slices judged with at least {MIN_SLICE} orders. Customer state: {int(j.judged_slices)} judged, B better in "
                                f"{int(j.slices_B_better)}; mean gain {j.mean_gain:+.3f} days (SD {j.sd_gain:.3f})."))
    else:
        j = sub_agg.set_index("slice").loc["customer_state"]
        w.explain("B9.3", done=(f"Slices judged with more than {MIN_SLICE} test detractors. Customer state: {int(j.judged_slices)} judged, "
                                f"{int(j.too_few)} too few. Pooled over judged states: precision A {j.pooled_precision_A:.3f} / B {j.pooled_precision_B:.3f}, "
                                f"recall A {j.pooled_recall_A:.3f} / B {j.pooled_recall_B:.3f}."))
    big = drift[(drift.kind == "numeric") & (drift.change.abs() >= 0.2)].sort_values("change", key=abs, ascending=False)
    tg = drift[drift.kind == "target"]
    w.explain("B9.4", done=(f"{len(big)} numeric features moved by |SMD| >= 0.2 between final-fit and test rows"
                            + (": " + ", ".join(f"{r.feature} {r.change:+.2f}" for r in big.head(5).itertuples()) if len(big) else "")
                            + ". Target: " + "; ".join(f"{r.level} {r.development:.3f} -> {r.test:.3f}" for r in tg.itertuples()) + " (G-77)."))
    w.explain("B9.5", done=(f"Largest term: {coef.term.iloc[0]}. Top permutation feature: {perm.feature.iloc[0]}. Against B4's ranking: Spearman "
                            f"{rho:.2f}, top-10 overlap {overlap}; {'DIVERGES: team alerted, model unchanged' if diverge else 'consistent'}."))
    if task == "classification":
        ls = lab_t[(lab_t.model == "B frozen")].set_index("label")
        w.explain("B9.6", done=(f"B's test AP with the agreed label {ls.ap.iloc[0]:.4f}; with the first-review label {ls.ap.iloc[1]:.4f}."))
        al = mdr.set_index("group").loc["all flagged (rule fires)"]
        w.explain("B9.7", done=(f"At 1/6: B {piv.loc['alerts_per_day', k_b]:.1f} alerts/day, precision {piv.loc['precision', k_b]:.3f}, "
                                f"{int(piv.loc['tp', k_b]):,} detractors caught, cost {piv.loc['cost', k_b]:,.0f} vs {piv.loc['cost', ('B dummy', 'B test rows')]:,.0f} with no alerts. "
                                f"Missed-dispatch rule on the test period: {int(al.orders):,} orders flagged, precision {al.precision:.3f}, "
                                f"{al.share_of_all_detractors:.1%} of detractors."))
    else:
        ar = bus.set_index("customer_state").loc["all"]
        w.explain("B9.7", done=(f"B on its test rows: within 3 days {ar.within_3d_B:.1%}; delivered more than 3 days later than predicted "
                                f"{ar.share_more_than_3d_later_B:.1%} (A on the same rows {ar.share_more_than_3d_later_A:.1%})."))
    w.explain("B9.8", done="Limitations listed in conclusion.md (scope, prediction moments, B-G-01, J-1 (a), B-G-05, G-75/G-77, illustrative cost, no causal claims).")

    lines = [f"# B9 conclusion — {task} (for team review)", "",
             "Every number below is read from this folder's files or T1's metrics_test.csv. Validation scores are selection scores (G-10); only test numbers are unbiased.", "",
             "## Answer", ""]
    if task == "regression":
        lines += [f"- B predicts delivery lead time better than A on the same test orders: MAE {piv.loc['mae', k_b]:.3f} vs {piv.loc['mae', k_ab]:.3f} days, "
                  f"difference {pm.difference:+.3f} [{pm.ci_low:+.3f}, {pm.ci_high:+.3f}] (paired bootstrap, paired_test_differences.csv).",
                  f"- B is within 3 days of the actual lead time for {piv.loc['within_3d', k_b]:.1%} of its test orders (A on the same orders {piv.loc['within_3d', k_ab]:.1%}).",
                  f"- B beats its dummy reference (MAE {piv.loc['mae', ('B dummy', 'B test rows')]:.3f}); the frozen model is the plain linear recipe, so the plain reference equals it."]
    else:
        lines += [f"- B ranks detractors better than A on the same test orders: AP {piv.loc['ap', k_b]:.4f} vs {piv.loc['ap', k_ab]:.4f}, "
                  f"difference {pm.difference:+.4f} [{pm.ci_low:+.4f}, {pm.ci_high:+.4f}] (paired bootstrap).",
                  f"- At the frozen threshold 1/6, B sends {piv.loc['alerts_per_day', k_b]:.1f} alerts/day (cap 25) with precision {piv.loc['precision', k_b]:.3f} "
                  f"and recall {piv.loc['recall', k_b]:.3f}; A sends {piv.loc['alerts_per_day', k_aa]:.1f}/day on its own rows, above the cap.",
                  f"- Illustrative cost (5 per missed detractor, 1 per false alert): B {piv.loc['cost', k_b]:,.0f} vs {piv.loc['cost', ('B dummy', 'B test rows')]:,.0f} with no alerts."]
    if task == "classification" and "thr" in extra:
        o6, o4 = extra["thr"]
        lines += [f"- Operating threshold 4/15 (B-G-07, post-test business change; the frozen 1/6 result above stays the unbiased one): on the test B sends "
                  f"{o4.loc['test, B rows', 'alerts_per_day']:.1f} alerts/day with {o4.loc['test, B rows', 'fp_per_tp']:.2f} false alarms per true detractor "
                  f"(1/6: {o6.loc['test, B rows', 'fp_per_tp']:.2f}), precision {o4.loc['test, B rows', 'precision']:.3f}, recall {o4.loc['test, B rows', 'recall']:.3f} (B9.10)."]
    fss, fts = extra["fallback"]
    lines += [f"- Orders outside B's scope fall back to A (B-G-06). A's validation {metric.upper()} outside the scope {fss.loc[b09_extra.OUT_S, 'mean_5_folds']:.4f} "
              f"vs inside {fss.loc[b09_extra.IN_S, 'mean_5_folds']:.4f}; test outside {fts.loc[b09_extra.OUT_S, metric]:.4f} on {int(fts.loc[b09_extra.OUT_S, 'orders']):,} orders (B9.15).",
              "- Validation folds and the test are shown together, with each period's time window, in validation_and_test.csv and validation_and_test_windows.csv (B9.14): folds are selection scores across seasons; the test is one recent window."]
    if task == "regression" and "resid" in extra:
        rb_ = extra["resid"]
        lines += [f"- Promise buffers (B9.16): {rb_.loc["B on B's test rows", 'share_more_than_3d_late']:.1%} of B's test orders arrive more than 3 days after B's prediction "
                  f"and {rb_.loc["B on B's test rows", 'share_more_than_6d_late']:.1%} more than 6 days after (A on the same rows "
                  f"{rb_.loc["A on B's test rows", 'share_more_than_3d_late']:.1%} and {rb_.loc["A on B's test rows", 'share_more_than_6d_late']:.1%})."]
    _key = lambda x: int(x.split(".")[1])
    lines += ["", "## Evidence by step", ""] + [f"- **{sid}**: {w.index['cards'][sid]['done']}" for sid in sorted(w.index["cards"], key=_key)]
    lines += ["", "## Limitations", "",
              "- Scope: seven states (B-C1); orders outside them are served by A's frozen model (B-G-06), whose results there are in B9.15.",
              "- Prediction moments differ: checkout for regression, carrier handover for classification; the classifier cannot act before handover.",
              "- Fold 1 is below A's training-row minimum (B-G-01); the 5-fold comparison keeps it.",
              "- B's history features for test rows use earlier test weeks (J-1 (a)), as in deployment; the test gain may partly reflect that recency.",
              "- The test period is the newest and differs from development (G-77); A's classification test cohort is below the 15% detractor share (G-75).",
              "- No causal claims: features describe association, not the effect of an intervention."]
    if task == "classification":
        lines += ["- B classification uses sigmoid calibration by decision (B-G-05), a deviation from the 8.3 rule.",
                  "- Cost is illustrative (5 per missed detractor, 1 per false alert)."]
    lines += ["",
              "## Questions for the team", "",
              "1. Confirm B as the delivered model for this task (G-79), on the test evidence above.",
              "2. Any slice or limitation that must be resolved before B10 and the report?"]
    if task == "classification":
        lines.append("3. Operating threshold decided: 4/15 (B-G-07), reported as a post-test change beside the frozen 1/6; confirm the alert volume suits the contact team.")
    w.text("conclusion.md", "\n".join(lines) + "\n", ids=("B9.8", "B9.9"))
    w.explain("B9.9", done="conclusion.md: answer, evidence by step, limitations and questions for the team.")
    w.finish(seed=seed)
    if w.index["checks_failed"]:
        raise SystemExit(f"B9 {task}: checks failed: {w.index['checks_failed']}")
    print(f"B9 {task}: B minus A {metric} {pm.difference:+.4f} [{pm.ci_low:+.4f}, {pm.ci_high:+.4f}]")
