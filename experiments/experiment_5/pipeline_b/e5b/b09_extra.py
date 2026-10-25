"""B9 round 2 (Henry's B9 review, 2026-10-25): B9.10 operating threshold options (B-G-07), B9.11 drift by fold,
B9.12 payment type, B9.13 business summary by route, B9.14 validation and test together, B9.15 A outside B's scope
(B-G-06), B9.16 residual distribution (regression). Called from b09.run; writes into the same B9 output folder.

No frozen model is refitted on new data and the test is not read again: out-of-fold sigmoid probabilities are rebuilt by
refitting the frozen recipes on the development folds (as B8 and A's s08 did) and checked against their calibration step.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from e5lib import factory
from e5lib.metrics import COST_FN, COST_FP, score
from e5lib.paths import E5, raw_data_dir
from e5lib.training import TARGET

from . import b02
from .env import b_outputs_dir

A_ST = E5 / "stages"
OPERATING = 4 / 15          # B-G-07
FROZEN = 1 / 6
CAP = 6                     # alerts/day asked for at the review
GRID = np.round(np.arange(0.02, 0.61, 0.01), 2)
MIN_SLICE = 100
IN_S, OUT_S = "inside B's scope", "outside B's scope"
B_ROWS = "B's test rows"


def _in_scope(d: pd.DataFrame) -> pd.Series:
    return d.customer_state.isin(b02.STATES) & d.primary_seller_state.isin(b02.STATES) & d.distance_km_max.notna()


def _days(ts: pd.Series) -> float:
    return float((ts.max().normalize() - ts.min().normalize()).days + 1)


def _at(y, p, t, days):
    f = p >= t
    tp, fp = int((f & (y == 1)).sum()), int((f & (y == 0)).sum())
    fn = int(((~f) & (y == 1)).sum())
    return {"threshold": float(t), "alerts": tp + fp, "alerts_per_day": (tp + fp) / days, "tp": tp, "fp": fp, "fn": fn,
            "precision": tp / (tp + fp) if tp + fp else np.nan, "recall": tp / (tp + fn) if tp + fn else np.nan,
            "fp_per_tp": fp / tp if tp else np.nan, "cost_5_to_1": COST_FN * fn + COST_FP * fp, "cost_1_to_1": fn + fp}


def _oof_sigmoid(spec, rec, folds, y_col):
    """Out-of-fold sigmoid probabilities of a frozen recipe, refitted per development fold (as B8 / s08)."""
    from e5lib.tuning import single_threaded
    rows = []
    for k in sorted(folds.fold.unique()):
        tr = folds[(folds.fold == k) & (folds.role == "train")].order_id
        va = folds[(folds.fold == k) & (folds.role == "validation")].order_id
        m = factory.build(dict(spec, calibration="sigmoid"))
        single_threaded(m.estimator)
        m.fit(rec.loc[tr], rec.loc[tr, y_col].to_numpy())
        rows.append(pd.DataFrame({"order_id": va.to_numpy(), "fold": int(k), "p": m.predict_proba(rec.loc[va])[:, 1],
                                  "y": rec.loc[va, y_col].to_numpy()}))
    return pd.concat(rows, ignore_index=True)


def _drift(dev: pd.DataFrame, oth: pd.DataFrame, spec: dict, y_col: str, period: str, pipe: str) -> list[dict]:
    out = []
    for c in spec["numeric"]:
        if c not in dev or c not in oth:
            continue
        x0, x1 = dev[c].astype(float), oth[c].astype(float)
        sd = np.sqrt((x0.var() + x1.var()) / 2)
        out.append({"pipeline": pipe, "period": period, "kind": "numeric", "feature": c,
                    "change": float((x1.mean() - x0.mean()) / sd) if sd > 0 else 0.0, "measure": "SMD"})
    for c in spec["categorical"]:
        if c not in dev or c not in oth:
            continue
        s0, s1 = dev[c].value_counts(normalize=True), oth[c].value_counts(normalize=True)
        lv = s0.index.union(s1.index)
        out.append({"pipeline": pipe, "period": period, "kind": "categorical", "feature": c,
                    "change": float((s1.reindex(lv, fill_value=0) - s0.reindex(lv, fill_value=0)).abs().sum() / 2), "measure": "TVD"})
    t0, t1 = dev[y_col].astype(float), oth[y_col].astype(float)
    sd = np.sqrt((t0.var() + t1.var()) / 2)
    out.append({"pipeline": pipe, "period": period, "kind": "target", "feature": y_col,
                "change": float((t1.mean() - t0.mean()) / sd) if sd > 0 else 0.0, "measure": "SMD"})
    return out


def run(task: str, w, c: dict) -> dict:
    """c: context from b09.run (a, a_test, b_test, df, ev, pt, piv, tvt, seed, b_spec, cutoff, label_ts)."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    rng = np.random.default_rng(c["seed"] + 1)
    y_col = TARGET[task]
    metric = "mae" if task == "regression" else "ap"
    a, a_test, b_test, df, pt, piv = c["a"], c["a_test"], c["b_test"], c["df"], c["pt"], c["piv"]
    out = {}

    b_rec = pd.read_csv(w.read(b_outputs_dir("b02", task) / "records_B.csv.gz"), parse_dates=["purchase_ts"], low_memory=False).set_index("order_id", drop=False)
    b_folds = pd.read_csv(w.read(b_outputs_dir("b05", task) / "folds_B.csv"))
    a_rec = a[a[f"eligible_{task}"].astype(bool)].set_index("order_id", drop=False)
    a_folds = pd.read_csv(w.read(A_ST / f"s05_partition/{task}/outputs/folds.csv"))
    a_spec = json.loads(w.read(A_ST / f"s08_selection/{task}/outputs/selected_spec.json").read_text())["spec"]
    b_spec = c["b_spec"]

    # out-of-fold validation predictions of the frozen recipes ---------------------------------------------------
    if task == "classification":
        b_oof = _oof_sigmoid(b_spec, b_rec, b_folds, y_col)
        a_oof = _oof_sigmoid(a_spec, a_rec, a_folds, y_col)
        cal_b = pd.read_csv(w.read(b_outputs_dir("b08", task) / "calibration_folds.csv"))
        cal_a = pd.read_csv(w.read(A_ST / "s08_selection/classification/outputs/calibration_folds.csv"))
        dev_b = max(abs(score(task, g.y.to_numpy(), proba=g.p.to_numpy())["ap"] - float(cal_b[(cal_b.variant == "sigmoid") & (cal_b.fold == k)].ap.iloc[0])) for k, g in b_oof.groupby("fold"))
        dev_a = max(abs(score(task, g.y.to_numpy(), proba=g.p.to_numpy())["ap"] - float(cal_a[(cal_a.variant == "sigmoid") & (cal_a.fold == k)].ap.iloc[0])) for k, g in a_oof.groupby("fold"))
        w.check("rebuilt out-of-fold sigmoid probabilities reproduce B8's and A's calibration step (AP per fold)", max(dev_a, dev_b) < 1e-9,
                ("B9.10", "B9.15"), f"max difference B {dev_b:.1e}, A {dev_a:.1e}")
    else:
        ap_ = pd.read_csv(w.read(A_ST / "s08_selection/regression/outputs/predictions.csv.gz"))
        ap_ = ap_[ap_.candidate_id == a_rec_id(task)]
        a_oof = ap_.rename(columns={"y_pred": "p", "y_true": "y"})[["order_id", "fold", "p", "y"]]
        bp_ = pd.read_csv(w.read(b_outputs_dir("b08", task) / "predictions.csv.gz"))
        bp_ = bp_[bp_.candidate_id == a_rec_id(task)]
        b_oof = bp_.rename(columns={"y_pred": "p", "y_true": "y"})[["order_id", "fold", "p", "y"]]

    # B9.10 operating threshold options (classification) -------------------------------------------------------------
    if task == "classification":
        vdays = sum(_days(b_rec.loc[g.order_id, "purchase_ts"]) for _, g in b_oof.groupby("fold"))
        tdays = _days(b_test.purchase_ts)
        bt = pt[(pt.model == "B frozen") & (pt.rows == "B test rows")]
        at_b = pt[(pt.model == "A frozen") & (pt.rows == "B test rows")]
        at_a = pt[(pt.model == "A frozen") & (pt.rows == "A test rows")]
        adays = _days(a_test.purchase_ts)
        curve = []
        for t in sorted(set(GRID.tolist()) | {FROZEN, OPERATING}):
            for period, y, p, d in (("validation (out-of-fold)", b_oof.y.to_numpy(), b_oof.p.to_numpy(), vdays),
                                    ("test (post-test view)", bt.y_true.to_numpy(), bt.y_pred.to_numpy(), tdays)):
                curve.append({"period": period, **_at(y.astype(int), p, t, d)})
        cv = pd.DataFrame(curve)
        w.table("threshold_options_curve", cv, ids=("B9.10",))
        opts = []
        for name, t in (("frozen 1/6", FROZEN), ("operating 4/15 (B-G-07)", OPERATING)):
            for model, period, y, p, d in (("B frozen", "validation (out-of-fold), B rows", b_oof.y, b_oof.p, vdays),
                                           ("B frozen", "test, B rows", bt.y_true, bt.y_pred, tdays),
                                           ("A frozen", "validation (out-of-fold), A rows", a_oof.y, a_oof.p,
                                            sum(_days(a_rec.loc[g.order_id, "purchase_ts"]) for _, g in a_oof.groupby("fold"))),
                                           ("A frozen", "test, B rows", at_b.y_true, at_b.y_pred, tdays),
                                           ("A frozen", "test, A rows", at_a.y_true, at_a.y_pred, adays)):
                opts.append({"threshold_name": name, "model": model, "rows": period,
                             **_at(y.to_numpy().astype(int), p.to_numpy(), t, d)})
        op = pd.DataFrame(opts)
        w.table("threshold_options", op, ids=("B9.10",))
        fig, ax = plt.subplots(1, 2, figsize=(13, 4.6))
        for period, ls in (("validation (out-of-fold)", "-"), ("test (post-test view)", "--")):
            s = cv[(cv.period == period) & cv.threshold.isin(GRID)]
            ax[0].plot(s.threshold, s.precision, ls, color="#1f77b4", label=f"precision, {period}")
            ax[0].plot(s.threshold, s.recall, ls, color="#ff7f0e", label=f"recall, {period}")
            ax[1].plot(s.threshold, s.fp_per_tp, ls, color="#d62728", label=f"FP per TP, {period}")
            ax[1].plot(s.threshold, s.alerts_per_day, ls, color="#7f7f7f", label=f"alerts/day, {period}")
        for a_ in ax:
            for t, lab in ((FROZEN, "1/6 frozen"), (OPERATING, "4/15 operating")):
                a_.axvline(t, color="k", lw=0.8, ls=":")
                a_.text(t, 0.97, f" {lab}", fontsize=8, va="top", transform=a_.get_xaxis_transform())
            a_.set_xlabel("threshold on B's sigmoid probability")
        ax[1].axhline(CAP, color="#7f7f7f", lw=0.6)
        ax[1].axhline(1, color="#d62728", lw=0.6)
        ax[1].set_ylim(0, 25)
        ax[0].set(ylabel="share", title="Precision and recall vs threshold")
        ax[1].set(title="False alarms per true detractor, and alerts per day (lines at 1 and 6)")
        ax[0].legend(fontsize=7, loc="center right")
        ax[1].legend(fontsize=7, loc="upper right")
        fig.tight_layout()
        w.figure("threshold_options", fig, cv, ids=("B9.10",), title="Operating threshold options (B-G-07)")
        plt.close(fig)
        o4 = op[(op.threshold_name.str.startswith("operating")) & (op.model == "B frozen")].set_index("rows")
        o6 = op[(op.threshold_name.str.startswith("frozen")) & (op.model == "B frozen")].set_index("rows")
        out["thr"] = (o6, o4)
        w.explain("B9.10", done=(f"Operating threshold 4/15 (B-G-07, post-test) vs frozen 1/6 on B's rows. Validation: {o4.loc['validation (out-of-fold), B rows', 'alerts_per_day']:.1f} "
                                 f"alerts/day, FP per TP {o4.loc['validation (out-of-fold), B rows', 'fp_per_tp']:.2f}, recall {o4.loc['validation (out-of-fold), B rows', 'recall']:.3f} "
                                 f"(1/6: {o6.loc['validation (out-of-fold), B rows', 'alerts_per_day']:.1f}/day, {o6.loc['validation (out-of-fold), B rows', 'fp_per_tp']:.2f}, {o6.loc['validation (out-of-fold), B rows', 'recall']:.3f}). "
                                 f"Test: {o4.loc['test, B rows', 'alerts_per_day']:.1f}/day, FP per TP {o4.loc['test, B rows', 'fp_per_tp']:.2f}, precision {o4.loc['test, B rows', 'precision']:.3f}, "
                                 f"recall {o4.loc['test, B rows', 'recall']:.3f} (1/6: {o6.loc['test, B rows', 'alerts_per_day']:.1f}/day, {o6.loc['test, B rows', 'fp_per_tp']:.2f}). "
                                 f"Cost 5:1 at 4/15 {o4.loc['test, B rows', 'cost_5_to_1']:,.0f} vs {o6.loc['test, B rows', 'cost_5_to_1']:,.0f} at 1/6; cost 1:1 {o4.loc['test, B rows', 'cost_1_to_1']:,.0f} vs {o6.loc['test, B rows', 'cost_1_to_1']:,.0f}."))

    # B9.11 drift by fold -----------------------------------------------------------------------------------------------
    rows = []
    for pipe, rec, folds, spec in (("B", b_rec, b_folds, b_spec), ("A", a_rec, a_folds, a_spec)):
        for k in sorted(folds.fold.unique()):
            tr = rec.loc[folds[(folds.fold == k) & (folds.role == "train")].order_id]
            va = rec.loc[folds[(folds.fold == k) & (folds.role == "validation")].order_id]
            rows += _drift(tr, va, spec, y_col, f"fold {k}", pipe)
    lab = c["label_ts"]
    b_fit = b_rec[pd.to_datetime(b_rec[lab]) < c["cutoff"]]
    a_fit = a_rec[(a_rec.purchase_ts < c["cutoff"]) & (pd.to_datetime(a_rec[lab]) < c["cutoff"])]
    rows += _drift(b_fit, b_test, b_spec, y_col, "test", "B")
    rows += _drift(a_fit, a_test, a_spec, y_col, "test", "A")
    dbf = pd.DataFrame(rows)
    w.table("drift_by_fold", dbf, ids=("B9.11",))
    fig, axes = plt.subplots(1, 2, figsize=(13, 0.35 * max(dbf.groupby("pipeline").feature.nunique()) + 2))
    for ax, pipe in zip(axes, ("B", "A")):
        h = dbf[(dbf.pipeline == pipe) & dbf.kind.isin(["numeric", "target"])].pivot_table(index="feature", columns="period", values="change")
        h = h[[f"fold {k}" for k in range(1, 6)] + ["test"]]
        h = h.reindex(h.abs().max(axis=1).sort_values().index)
        im = ax.imshow(h.to_numpy(), cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
        ax.set_xticks(range(h.shape[1]), h.columns)
        ax.set_yticks(range(h.shape[0]), h.index, fontsize=7)
        for i in range(h.shape[0]):
            for j in range(h.shape[1]):
                v = h.iat[i, j]
                if abs(v) >= 0.2:
                    ax.text(j, i, f"{v:+.1f}", ha="center", va="center", fontsize=6)
        ax.set_title(f"{pipe}: SMD, validation (or test) minus training rows")
    fig.colorbar(im, ax=axes, shrink=0.6)
    w.figure("drift_by_fold", fig, dbf, ids=("B9.11",), title="Drift by fold (training vs validation) and final fit vs test")
    plt.close(fig)
    big = dbf[(dbf.kind == "numeric") & (dbf.change.abs() >= 0.2)]
    rec_ = big.groupby(["pipeline", "feature"]).period.nunique().sort_values(ascending=False)
    w.explain("B9.11", done=(f"Training vs validation drift per fold for A and B, plus final fit vs test (SMD for numeric features and the target, TVD for categorical). "
                             f"Numeric features with |SMD| >= 0.2 in at least 3 of the 6 periods: "
                             + (", ".join(f"{p} {f} ({n})" for (p, f), n in rec_[rec_ >= 3].items()) or "none") + "."))

    # B9.12 payment type (regression) ---------------------------------------------------------------------------------------
    if task == "regression":
        o = pd.read_csv(w.read(raw_data_dir() / "olist_orders_dataset.csv"), usecols=["order_id", "order_purchase_timestamp", "order_approved_at"],
                        parse_dates=["order_purchase_timestamp", "order_approved_at"])
        o["approval_days"] = (o.order_approved_at - o.order_purchase_timestamp).dt.total_seconds() / 86400
        prow = []
        for period, d in (("development (B rows)", b_rec), ("test (B rows)", b_test)):
            m = d.reset_index(drop=True)[["order_id", "primary_payment_type", y_col]].merge(o[["order_id", "approval_days"]], on="order_id", how="left")
            for pty, g in m.groupby("primary_payment_type"):
                prow.append({"period": period, "primary_payment_type": pty, "orders": len(g), "approval_days_median": g.approval_days.median(),
                             "approval_days_mean": g.approval_days.mean(), "lead_days_mean": g[y_col].mean(), "lead_days_median": g[y_col].median(),
                             "lead_minus_approval_days_mean": (g[y_col] - g.approval_days).mean()})
        ptab = pd.DataFrame(prow)
        w.table("payment_type", ptab, ids=("B9.12",))
        dv = ptab[ptab.period.str.startswith("development")].set_index("primary_payment_type")
        w.explain("B9.12", done=(f"Lead time starts at purchase; Olist approves an order when payment clears. Development rows: median purchase-to-approval "
                                 f"boleto {dv.loc['boleto', 'approval_days_median']:.2f} days vs credit card {dv.loc['credit_card', 'approval_days_median']:.2f}; mean lead time "
                                 f"{dv.loc['boleto', 'lead_days_mean']:.2f} vs {dv.loc['credit_card', 'lead_days_mean']:.2f} days; lead time after approval "
                                 f"{dv.loc['boleto', 'lead_minus_approval_days_mean']:.2f} vs {dv.loc['credit_card', 'lead_minus_approval_days_mean']:.2f}. "
                                 "Payment type stands for payment-clearance delay, not delivery quality (observation)."))

    # B9.13 business summary by route ------------------------------------------------------------------------------------------
    a_all = a_test.assign(route=a_test.primary_seller_state + "->" + a_test.customer_state, in_scope=_in_scope(a_test))
    paa = pt[(pt.model == "A frozen") & (pt.rows == "A test rows")].set_index("order_id").loc[a_all.order_id]
    a_all = a_all.assign(pa=paa.y_pred.to_numpy(), y=paa.y_true.to_numpy())
    rr = []
    if task == "regression":
        for rt, g in df.groupby(b02.ROUTE):
            rr.append({"rows": B_ROWS, "route": rt, "orders": len(g), "mae_A": np.mean(np.abs(g.pa - g.y)), "mae_B": np.mean(np.abs(g.pb - g.y)),
                       "within_3d_A": np.mean(np.abs(g.pa - g.y) <= 3), "within_3d_B": np.mean(np.abs(g.pb - g.y) <= 3),
                       "more_than_3d_late_A": np.mean(g.y > g.pa + 3), "more_than_3d_late_B": np.mean(g.y > g.pb + 3), "judged": len(g) >= MIN_SLICE})
        for rt, g in a_all.groupby("route"):
            rr.append({"rows": "A's test rows (all routes)", "route": rt, "in_b_scope": bool(g.in_scope.all()), "orders": len(g),
                       "mae_A": np.mean(np.abs(g.pa - g.y)), "within_3d_A": np.mean(np.abs(g.pa - g.y) <= 3),
                       "more_than_3d_late_A": np.mean(g.y > g.pa + 3), "judged": len(g) >= MIN_SLICE})
    else:
        for rt, g in df.groupby(b02.ROUTE):
            r = {"rows": B_ROWS, "route": rt, "orders": len(g), "detractors": int(g.y.sum())}
            for nm, col in (("A", "pa"), ("B", "pb")):
                for tn, t in (("1/6", FROZEN), ("4/15", OPERATING)):
                    s = _at(g.y.to_numpy().astype(int), g[col].to_numpy(), t, 1.0)
                    r[f"alerts_{nm}_{tn}"], r[f"precision_{nm}_{tn}"], r[f"recall_{nm}_{tn}"] = s["alerts"], s["precision"], s["recall"]
            r["judged"] = r["detractors"] > MIN_SLICE
            rr.append(r)
        for rt, g in a_all.groupby("route"):
            r = {"rows": "A's test rows (all routes)", "route": rt, "in_b_scope": bool(g.in_scope.all()), "orders": len(g), "detractors": int(g.y.sum())}
            for tn, t in (("1/6", FROZEN), ("4/15", OPERATING)):
                s = _at(g.y.to_numpy().astype(int), g.pa.to_numpy(), t, 1.0)
                r[f"alerts_A_{tn}"], r[f"precision_A_{tn}"], r[f"recall_A_{tn}"] = s["alerts"], s["precision"], s["recall"]
            r["judged"] = r["detractors"] > MIN_SLICE
            rr.append(r)
    br = pd.DataFrame(rr).sort_values(["rows", "orders"], ascending=[False, False])
    w.table("business_by_route", br, ids=("B9.13",))
    jb = br[(br.rows == B_ROWS) & br.judged]
    w.explain("B9.13", done=(f"Routes judged ({'at least 100 orders' if task == 'regression' else 'more than 100 detractors'}): {len(jb)} of "
                             f"{int((br.rows == B_ROWS).sum())} on B's test rows; "
                             + (f"B has the lower MAE on {int((jb.mae_B < jb.mae_A).sum())} of them. " if task == "regression" else "")
                             + "A on all of A's test routes is listed too (in or out of B's scope)."))

    # B9.14 validation and test together, with each period's time window (Henry) --------------------------------------------------
    ft = pd.read_csv(w.read(b_outputs_dir("t1_joint_test", task) / "fold_and_test_table.csv"))
    tvt = c["tvt"]
    win = {r.period: f"{r.start} to {r.end}" for r in ft.itertuples()}
    vt = []
    for col, (model, rows_) in (("B_on_B_rows", ("B frozen", "B test rows")), ("A_on_B_rows", ("A frozen", "B test rows")), ("A_on_A_rows", ("A frozen", "A test rows"))):
        f = ft[ft.period.str.startswith("fold")][col].to_numpy()
        t = tvt[(tvt.model == model) & (tvt.rows == rows_) & (tvt.metric == metric)].iloc[0]
        vt.append({"series": col.replace("_", " "), **{f"fold_{i}": v for i, v in enumerate(f, 1)}, "mean_5_folds": f.mean(), "se_5_folds": f.std(ddof=1) / np.sqrt(len(f)),
                   "test": t.test, "test_ci_low": t.test_ci_low, "test_ci_high": t.test_ci_high, "metric": metric})
    vtt = pd.DataFrame(vt)
    w.table("validation_and_test", vtt, ids=("B9.14",))
    wt = ft[["period", "kind", "start", "end", "festival_days"]].copy()
    w.table("validation_and_test_windows", wt, ids=("B9.14",))
    periods = [f"fold {k}" for k in range(1, 6)] + ["test"]
    fig, ax = plt.subplots(figsize=(11, 4.6))
    cols = {"B on B rows": "#1f77b4", "A on B rows": "#7f7f7f", "A on A rows": "#bdbdbd"}
    for i, r in enumerate(vtt.itertuples()):
        off = (i - 1) * 0.12
        fv = [getattr(r, f"fold_{k}") for k in range(1, 6)]
        ax.plot(np.arange(5) + off, fv, "o-", color=cols[r.series], ms=5, lw=1, label=f"{r.series}")
        ax.hlines(r.mean_5_folds, -0.3, 4.3, color=cols[r.series], ls="--", lw=0.8)
        ax.errorbar(5 + off, r.test, yerr=[[r.test - r.test_ci_low], [r.test_ci_high - r.test]], fmt="D", color=cols[r.series], capsize=4)
    ax.axvline(4.5, color="k", lw=0.6, ls=":")
    labels = [f"{p}\n{win[p].replace(' to ', ' –\n')}" for p in periods]
    ax.set_xticks(range(6), labels, fontsize=8)
    ax.set(ylabel=metric.upper(), title=f"Validation folds (selection scores; dashed = 5-fold mean) and test (read once, 95% bootstrap), {task}")
    ax.legend(fontsize=7)
    fig.tight_layout()
    w.figure("validation_and_test", fig, vtt, ids=("B9.14",), title="Validation and test together, with time windows")
    plt.close(fig)
    w.explain("B9.14", done=("Each series: five validation folds, their mean ± SE, and the test with its 95% bootstrap interval; each period's time window is in "
                             "validation_and_test_windows.csv and on the chart. "
                             + "; ".join(f"{r.series}: folds mean {r.mean_5_folds:.4f} ± {r.se_5_folds:.4f}, test {r.test:.4f} [{r.test_ci_low:.4f}, {r.test_ci_high:.4f}]" for r in vtt.itertuples())
                             + f". Test window {win['test']}."))

    # B9.16 residual distribution and late shares (regression; Henry: promise ranges with 3- and 6-day buffers) -----------------------
    if task == "regression":
        rrow, hist = [], []
        b_oof_v = b_oof.copy()
        for name, y, p in (("B on B's test rows", df.y.to_numpy(), df.pb.to_numpy()), ("A on B's test rows", df.y.to_numpy(), df.pa.to_numpy()),
                           ("A on A's test rows", a_all.y.to_numpy(), a_all.pa.to_numpy()),
                           ("B on B's validation rows (out-of-fold)", b_oof_v.y.to_numpy(), b_oof_v.p.to_numpy()),
                           ("A on A's validation rows (out-of-fold)", a_oof.y.to_numpy(), a_oof.p.to_numpy())):
            e = y - p                      # positive = arrived later than predicted
            q = np.percentile(e, [5, 25, 50, 75, 95])
            rrow.append({"series": name, "orders": len(e), "mean_days": e.mean(), "p05": q[0], "p25": q[1], "median": q[2], "p75": q[3], "p95": q[4],
                         "share_later_than_predicted": np.mean(e > 0), "share_more_than_3d_late": np.mean(e > 3), "share_more_than_6d_late": np.mean(e > 6),
                         "share_more_than_3d_early": np.mean(e < -3), "share_within_3d": np.mean(np.abs(e) <= 3), "share_within_6d": np.mean(np.abs(e) <= 6)})
            if "test" in name:
                cnt, edges = np.histogram(np.clip(e, -20, 20), bins=np.arange(-20, 21, 1))
                hist += [{"series": name, "bin_from_days": a_, "bin_to_days": b_, "orders": int(n_)} for a_, b_, n_ in zip(edges[:-1], edges[1:], cnt)]
        rt = pd.DataFrame(rrow)
        w.table("residuals_summary", rt, ids=("B9.16",))
        hd = pd.DataFrame(hist)
        w.table("residuals_histogram", hd, ids=("B9.16",))
        fig, ax = plt.subplots(figsize=(10, 4.2))
        for name, col in (("B on B's test rows", "#1f77b4"), ("A on B's test rows", "#7f7f7f")):
            h = hd[hd.series == name]
            ax.step(h.bin_from_days, h.orders / h.orders.sum(), where="post", color=col, label=name)
        for x_, lab in ((3, "3 days late"), (6, "6 days late")):
            ax.axvline(x_, color="#d62728", ls=":", lw=0.9)
            ax.text(x_, 0.97, f" {lab}", transform=ax.get_xaxis_transform(), fontsize=8, va="top")
        ax.set(xlabel="actual minus predicted lead time (days; positive = later than predicted; clipped at ±20)", ylabel="share of orders",
               title="Residuals on B's test rows: B vs A")
        ax.legend(fontsize=8)
        fig.tight_layout()
        w.figure("residuals", fig, hd, ids=("B9.16",), title="Residual distribution (B9.16)")
        plt.close(fig)
        rb = rt.set_index("series")
        bt_, at_ = rb.loc["B on B's test rows"], rb.loc["A on B's test rows"]
        out["resid"] = rb
        w.explain("B9.16", done=(f"Residual = actual minus predicted lead time. On B's test rows, B's orders arrive more than 3 days after its prediction in "
                                 f"{bt_.share_more_than_3d_late:.1%} of cases and more than 6 days after in {bt_.share_more_than_6d_late:.1%} (A on the same rows "
                                 f"{at_.share_more_than_3d_late:.1%} and {at_.share_more_than_6d_late:.1%}); median residual B {bt_['median']:+.2f} days, A {at_['median']:+.2f}; "
                                 f"95th percentile B {bt_.p95:+.2f}, A {at_.p95:+.2f}. With a 6-day buffer on B's prediction, {1 - bt_.share_more_than_6d_late:.1%} of test orders arrive in time."))

    # B9.15 A outside B's scope (B-G-06) ---------------------------------------------------------------------------------------------
    a_oof = a_oof.merge(a[["order_id", "customer_state", "primary_seller_state", "distance_km_max", "purchase_ts"]], on="order_id", how="left")
    a_oof["in_scope"] = _in_scope(a_oof)
    fb = []
    for k, g in a_oof.groupby("fold"):
        for sc, h in g.groupby("in_scope"):
            s = score(task, h.y.to_numpy(), y_pred=h.p.to_numpy()) if task == "regression" else score(task, h.y.to_numpy().astype(int), proba=h.p.to_numpy(), threshold=FROZEN)
            fb.append({"period": f"fold {k}", "scope": IN_S if sc else OUT_S, "orders": len(h),
                       **({"detractors": int(h.y.sum())} if task == "classification" else {}), **{m: s[m] for m in (["mae", "rmse", "within_3d"] if task == "regression" else ["ap", "roc_auc", "brier", "precision", "recall"])}})
    for sc, h in a_all.groupby("in_scope"):
        y, p = h.y.to_numpy(), h.pa.to_numpy()
        s = score(task, y, y_pred=p) if task == "regression" else score(task, y.astype(int), proba=p, threshold=FROZEN)
        bs = []
        for _ in range(1000):
            ix = rng.integers(0, len(y), len(y))
            bs.append(score(task, y[ix], y_pred=p[ix])[metric] if task == "regression" else score(task, y[ix].astype(int), proba=p[ix])[metric])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        fb.append({"period": "test", "scope": IN_S if sc else OUT_S, "orders": len(h),
                   **({"detractors": int(y.sum())} if task == "classification" else {}), **{m: s[m] for m in (["mae", "rmse", "within_3d"] if task == "regression" else ["ap", "roc_auc", "brier", "precision", "recall"])},
                   f"{metric}_ci_low": lo, f"{metric}_ci_high": hi})
    fbt = pd.DataFrame(fb)
    summ = fbt[fbt.period.str.startswith("fold")].groupby("scope")[metric].agg(mean_5_folds="mean", se_5_folds=lambda x: x.std(ddof=1) / np.sqrt(len(x))).reset_index()
    w.table("a_fallback_by_scope", fbt, ids=("B9.15",))
    w.table("a_fallback_summary", summ, ids=("B9.15",))
    ts = fbt[fbt.period == "test"].set_index("scope")
    ss = summ.set_index("scope")
    w.explain("B9.15", done=(f"A's frozen model by B's scope (B-G-06 fallback). Validation {metric.upper()} mean over 5 folds: inside {ss.loc[IN_S, 'mean_5_folds']:.4f}, "
                             f"outside {ss.loc[OUT_S, 'mean_5_folds']:.4f}. Test: inside {ts.loc[IN_S, metric]:.4f} "
                             f"({int(ts.loc[IN_S, 'orders']):,} orders), outside {ts.loc[OUT_S, metric]:.4f} "
                             f"[{ts.loc[OUT_S, metric + '_ci_low']:.4f}, {ts.loc[OUT_S, metric + '_ci_high']:.4f}] "
                             f"({int(ts.loc[OUT_S, 'orders']):,} orders)."))
    out["fallback"] = (ss, ts)
    return out


def a_rec_id(task: str) -> str:
    return "reg.sel.log.linear" if task == "regression" else "clf.sel.log.logistic"
