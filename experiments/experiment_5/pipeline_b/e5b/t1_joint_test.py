"""T1: the joint test run — A and B frozen recipes, one test read (blueprint
pipeline_b/spec/blueprints/joint_test.md; G-79, G-24, B-C13, B-G-05; J-1 = (a)).

Outputs go to pipeline_b/stages/t1_joint_test/<task>/outputs; A's frozen tree is never written.
The run refuses to start if the test has already been read (test_read.json present).

Evidence IDs: T1.1 freezes and rows, T1.2 final fits, T1.3 test metrics, T1.4 classification at the
threshold, T1.5 bundles, T1.6 fold-by-fold and test table (B-C13).
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from e5lib import data, factory, protocol
from e5lib.metrics import PRIMARY, score
from e5lib.paths import E5, raw_data_dir
from e5lib.training import TARGET, predict

from . import b02
from . import history as h
from .env import BWriter, assert_a_frozen, b_outputs_dir

STAGE = "t1_joint_test"
A_S08 = str(E5 / "stages/s08_selection/{task}/outputs")
A_S04 = str(E5 / "stages/s04_features/{task}/outputs")
LABEL_TS = {"regression": "lead_label_ts", "classification": "review_label_ts"}
FESTIVALS = (pd.Timestamp("2017-11-24"), pd.Timestamp("2017-12-25"))   # Black Friday and Christmas 2017
EVENTS_UNTIL = pd.Timestamp("2100-01-01")   # J-1 (a): every event, each row uses only weeks before its prediction week


def b_rows(task: str, a_rows: pd.DataFrame, ev: pd.DataFrame, cap: float | None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """B's population rules and history features for a set of A rows (the B2 logic, without the warm-up)."""
    facts = ev[["order_id", "seller_id", "seller_state", "carrier_ts", "ship_limit", "h_late", "h_days", "dispatch"]]
    d = a_rows.merge(facts, on="order_id", how="left")
    removed: list = []
    d = b02._rule(d, ~(d.customer_state.isin(b02.STATES) & d.primary_seller_state.isin(b02.STATES)), "B_STATE", removed)
    d = b02._rule(d, d.distance_km_max.isna(), "B_DISTANCE", removed)
    if task == "regression":
        d = b02._rule(d, d.lead_days > cap, "B_LEAD_CAP", removed)
    else:
        d = b02._rule(d, d.carrier_ts.isna(), "B_NO_HANDOVER", removed)
        d = b02._rule(d, d.review_label_ts <= d.carrier_ts, "B_REVIEW_BEFORE_HANDOVER", removed)
    d["prediction_ts"] = d.purchase_ts if task == "regression" else d.carrier_ts
    d["prediction_week"] = h.week(d.prediction_ts).astype("int64")
    d[b02.ROUTE] = d.primary_seller_state + "->" + d.customer_state
    q = d[["seller_id", "seller_state", "customer_state"]].assign(route=d[b02.ROUTE], pw=d.prediction_week)
    sf = h.seller_features(ev, q)
    rl = h.route_feature(ev, q, "lead", "route_recent_delivery_days")
    rt = h.route_feature(ev, q, "transit", "route_recent_carrier_transit_days")
    d = pd.concat([d, sf, rl, rt], axis=1)
    if task == "classification":
        d["order_handed_over_late"] = d.h_late
        d["order_handover_late_days"] = d.h_days
        d["order_dispatch_days"] = d.dispatch
    exc = pd.concat(removed, ignore_index=True) if removed else pd.DataFrame(columns=["order_id", "reason_code"])
    return d, exc


def brute_force_diff(ev: pd.DataFrame, d: pd.DataFrame, seed: int) -> tuple[float, bool, int]:
    """B2's leakage re-check: recompute features from events in weeks before the prediction week on a sample."""
    rng = np.random.default_rng(seed)
    hand = ev[ev.hw.notna()].astype({"hw": "int64"})
    dlv = ev[ev.dw.notna() & ev.lead.notna()].astype({"dw": "int64"})
    sample = d.iloc[np.sort(rng.choice(len(d), size=min(b02.SAMPLE, len(d)), replace=False))]
    diffs, last_ok = [], True
    for r in sample.itertuples():
        if r.seller_prior_source == "own seller history":
            past = hand[(hand.seller_id == r.seller_id) & (hand.hw < r.prediction_week)]
            diffs.append(abs(past.h_late.mean() - r.seller_prior_late_handover_rate))
            last_ok &= bool(past.hw.max() < r.prediction_week)
        if r.route_recent_delivery_days_source == "own route history":
            num = den = 0.0
            for k, wt in zip((1, 2, 3), h.WEIGHTS):
                v = dlv[(dlv.route == getattr(r, b02.ROUTE)) & (dlv.dw == r.prediction_week - k)].lead
                if len(v):
                    num += wt * v.median()
                    den += wt
            diffs.append(abs(num / den - r.route_recent_delivery_days))
    return (float(np.max(diffs)) if diffs else 0.0), last_ok, len(sample)


def _sha_ok(recipe: dict) -> bool:
    body = {k: v for k, v in recipe.items() if k != "sha256"}
    return hashlib.sha256(json.dumps(body, sort_keys=True, default=str).encode()).hexdigest() == recipe["sha256"]


def _days(ts: pd.Series) -> float:
    return float((ts.max().normalize() - ts.min().normalize()).days + 1)


def run(task: str) -> None:
    assert_a_frozen()
    out_dir = b_outputs_dir(STAGE, task)
    if (out_dir / "test_read.json").exists():
        raise SystemExit(f"T1 {task}: the test has already been read ({out_dir / 'test_read.json'}); a second read is a "
                         "deviation and needs the lead's explicit decision")
    w = BWriter(STAGE, task)
    seed = int(protocol.load()["seed"])
    metric, higher = PRIMARY[task]
    y_col = TARGET[task]
    cutoff = pd.Timestamp(protocol.get("data_dependent.test_cutoffs.values")[task])

    # T1.1 freezes ---------------------------------------------------------------------------------
    a_rec = json.loads(w.read(Path(A_S08.format(task=task)) / "frozen_recipe.json").read_text())
    b_rec = json.loads(w.read(b_outputs_dir("b08", task) / "frozen_recipe.json").read_text())
    a_spec = json.loads(w.read(Path(A_S08.format(task=task)) / "selected_spec.json").read_text())["spec"]
    b_spec = json.loads(w.read(b_outputs_dir("b08", task) / "selected_spec.json").read_text())["spec"]
    if not (_sha_ok(a_rec) and _sha_ok(b_rec)):
        raise SystemExit(f"T1 {task}: a frozen recipe's sha256 does not recompute; refusing to read the test")
    if task == "classification":
        a_spec = dict(a_spec, calibration=a_rec["calibration"])
        b_spec = dict(b_spec, calibration=b_rec["calibration"])
    a_recipes = json.loads(w.read(Path(A_S04.format(task=task)) / "recipes.json").read_text())
    b_recipes = json.loads(w.read(b_outputs_dir("b04", task) / "recipes_B.json").read_text())

    # development rows for the final fits (labels observable before the cutoff) -----------------------
    a_dev = data.load("records", task, "development", "s08_selection")
    a_dev[LABEL_TS[task]] = pd.to_datetime(a_dev[LABEL_TS[task]])
    a_dev = a_dev[a_dev[LABEL_TS[task]] < cutoff].reset_index(drop=True)
    b_dev = pd.read_csv(w.read(b_outputs_dir("b02", task) / "records_B.csv.gz"), parse_dates=["purchase_ts", LABEL_TS[task]], low_memory=False)
    b_dev = b_dev[b_dev[LABEL_TS[task]] < cutoff].reset_index(drop=True)

    # the single test read -----------------------------------------------------------------------------
    a_test = data.load("records", task, "test", "s08_selection")
    read_at = datetime.now(timezone.utc).isoformat()
    for f in ("olist_orders_dataset.csv", "olist_order_items_dataset.csv", "olist_sellers_dataset.csv", "olist_customers_dataset.csv"):
        w.read(raw_data_dir() / f)
    ev = h.load_events(raw_data_dir(), EVENTS_UNTIL)
    cap = json.loads(w.read(b_outputs_dir("b02", "regression") / "feature_build_log.json").read_text())["lead_cap_days"]
    a_test = a_test.copy()
    for c in ("review_label_ts", "lead_label_ts"):
        if c in a_test:
            a_test[c] = pd.to_datetime(a_test[c])
    b_test, b_exc = b_rows(task, a_test, ev, cap if task == "regression" else None)
    b_test = b_test.reset_index(drop=True)
    max_diff, last_ok, n_sample = brute_force_diff(ev, b_test, seed)
    w.table("test_rows_B", pd.concat([b_test[["order_id"]].assign(kept=True, reason_code=""),
                                      b_exc.assign(kept=False)[["order_id", "kept", "reason_code"]]], ignore_index=True)
            .sort_values("order_id"), ids=("T1.1",))

    # T1.2 final fits --------------------------------------------------------------------------------
    def fit(spec, rows):
        m = factory.build(spec)
        m.fit(rows, rows[y_col].to_numpy())
        return m

    models = {"A frozen": fit(a_spec, a_dev), "A dummy": fit(a_recipes["dummy"]["spec"], a_dev),
              "A plain": fit(a_recipes["linear"]["spec"], a_dev),
              "B frozen": fit(b_spec, b_dev), "B dummy": fit(b_recipes["dummy"]["spec"], b_dev),
              "B plain": fit(b_recipes["linear"]["spec"], b_dev)}
    a_on_b = a_test.set_index("order_id").loc[b_test.order_id].reset_index()
    preds = {"A frozen|A test rows": predict(task, models["A frozen"], a_test),
             "A frozen|B test rows": predict(task, models["A frozen"], a_on_b),
             "A dummy|A test rows": predict(task, models["A dummy"], a_test),
             "A plain|A test rows": predict(task, models["A plain"], a_test),
             "B frozen|B test rows": predict(task, models["B frozen"], b_test),
             "B dummy|B test rows": predict(task, models["B dummy"], b_test),
             "B plain|B test rows": predict(task, models["B plain"], b_test)}
    ys = {"A test rows": a_test[y_col].to_numpy(), "B test rows": b_test[y_col].to_numpy()}
    w.json("test_read", {"task": task, "read_at_utc": read_at, "read_once": True, "a_test_rows": int(len(a_test)),
                         "b_test_rows": int(len(b_test)), "a_frozen_sha256": a_rec["sha256"], "b_frozen_sha256": b_rec["sha256"],
                         "events_until": "every event; each row uses only weeks before its prediction week (J-1 (a))"},
           ids=("T1.1",))

    # T1.3 / T1.4 metrics -------------------------------------------------------------------------------
    thr = {"A": (a_rec.get("threshold") or {}).get("value"), "B": (b_rec.get("threshold") or {}).get("value")}
    days = {"A test rows": _days(a_test.purchase_ts), "B test rows": _days(b_test.purchase_ts)}
    mrows, prow = [], []
    for key, p in preds.items():
        model, rows = key.split("|")
        y = ys[rows]
        s = score(task, y, y_pred=p) if task == "regression" else score(task, y, proba=p, threshold=thr[model[0]])
        if task == "classification":
            s["alerts_per_day"] = (s["tp"] + s["fp"]) / days[rows]
            s["threshold"] = thr[model[0]]
        for m_, v in s.items():
            mrows.append({"model": model, "rows": rows, "metric": m_, "value": float(v) if v is not None else np.nan})
        ids_ = a_test.order_id if rows == "A test rows" else b_test.order_id
        prow.append(pd.DataFrame({"order_id": ids_.to_numpy(), "model": model, "rows": rows, "y_true": y, "y_pred": p}))
    mt = pd.DataFrame(mrows)
    w.table("metrics_test", mt, ids=("T1.3", "T1.4") if task == "classification" else ("T1.3",))
    pt = pd.concat(prow, ignore_index=True)
    w.table("predictions_test", pt, ids=("T1.3",), compress=True)
    piv = mt.pivot_table(index="metric", columns=["model", "rows"], values="value")

    # test-size check for B's cohort (G-46, G-54; reported, not fixed) ----------------------------------
    size = {"b_test_rows": int(len(b_test)), "b_final_fit_rows": int(len(b_dev)),
            "b_test_share_of_fit_plus_test": float(len(b_test) / (len(b_test) + len(b_dev)))}
    if task == "classification":
        size.update({"b_test_detractors": int(b_test[y_col].sum()), "b_dev_detractors": int(b_dev[y_col].sum()),
                     "b_test_detractor_share": float(b_test[y_col].sum() / (b_test[y_col].sum() + b_dev[y_col].sum()))})
    w.json("test_size_B", size, ids=("T1.1",))

    # T1.5 bundles and reload parity ---------------------------------------------------------------------
    parity = {}
    for pipe, mkey, X in (("A", "A frozen", a_test), ("B", "B frozen", b_test)):
        rel = f"bundles/{pipe}/model.joblib"
        path = w._path(rel)
        joblib.dump(models[mkey], path)
        w._tag(rel, ("T1.5",), "bundle")
        reloaded = joblib.load(path)
        parity[pipe] = bool(np.array_equal(predict(task, reloaded, X), predict(task, models[mkey], X)))
        spec = a_spec if pipe == "A" else b_spec
        fr = a_rec if pipe == "A" else b_rec
        w.json(f"bundles/{pipe}/schema", {"pipeline": pipe, "task": task, "frozen_sha256": fr["sha256"], "model": fr["model"],
                                          "numeric": spec["numeric"], "categorical": spec["categorical"],
                                          "calibration": fr.get("calibration"), "threshold": fr.get("threshold"),
                                          "training_rows": int(len(a_dev if pipe == "A" else b_dev)),
                                          "training_id_digest": hashlib.sha256("".join(sorted((a_dev if pipe == "A" else b_dev).order_id)).encode()).hexdigest(),
                                          "versions": {"sklearn": __import__("sklearn").__version__, "pandas": pd.__version__, "numpy": np.__version__}},
               ids=("T1.5",))
        X_ = (a_dev if pipe == "A" else b_dev)
        prof = {c: {"mean": float(X_[c].mean()), "std": float(X_[c].std())} for c in spec["numeric"] if c in X_}
        prof.update({c: X_[c].value_counts(normalize=True).head(50).to_dict() for c in spec["categorical"] if c in X_})
        w.json(f"bundles/{pipe}/training_profile", prof, ids=("T1.5",))

    # T1.6 fold-by-fold and test table (B-C13) ------------------------------------------------------------
    mf = pd.read_csv(w.read(b_outputs_dir("b08", task) / "metrics_by_population_folds.csv"))
    variant = "sigmoid" if task == "classification" else "raw"
    mf = mf[(mf.metric == metric) & (mf.variant == variant)]
    fsum = pd.read_csv(w.read(b_outputs_dir("b05", task) / "fold_summary_B.csv"))
    rows = []
    for r in fsum.itertuples():
        vs, ve = pd.Timestamp(r.validation_first), pd.Timestamp(r.validation_last)
        fest = [str(d_.date()) for d_ in FESTIVALS if vs <= d_ <= ve]
        get = lambda model, rws: float(mf[(mf.fold == r.fold) & (mf.model == model) & (mf.rows == rws)].value.iloc[0])
        rows.append({"period": f"fold {r.fold}", "kind": "validation (selection score, G-10)", "start": str(vs.date()), "end": str(ve.date()),
                     "festival_days": "; ".join(fest), "A_on_A_rows": get("A frozen model", "A validation rows"),
                     "A_on_B_rows": get("A frozen model", "B validation rows"), "B_on_B_rows": get("B recommended model", "B validation rows")})
    rows.append({"period": "test", "kind": "test (unbiased, read once)", "start": str(b_test.purchase_ts.min().date()),
                 "end": str(b_test.purchase_ts.max().date()), "festival_days": "",
                 "A_on_A_rows": float(piv.loc[metric, ("A frozen", "A test rows")]),
                 "A_on_B_rows": float(piv.loc[metric, ("A frozen", "B test rows")]),
                 "B_on_B_rows": float(piv.loc[metric, ("B frozen", "B test rows")])})
    ft = pd.DataFrame(rows)
    ft.insert(5, "metric", metric)
    w.table("fold_and_test_table", ft, ids=("T1.6",))

    # charts ----------------------------------------------------------------------------------------------
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    mets = ["mae", "rmse", "r2", "within_3d"] if task == "regression" else ["ap", "roc_auc", "brier", "precision", "recall", "f1"]
    comp = pd.DataFrame([{"metric": m_, "series": f"{k[0]} on {k[1]}", "value": float(piv.loc[m_, k])}
                         for m_ in mets for k in (("A frozen", "A test rows"), ("A frozen", "B test rows"), ("B frozen", "B test rows"),
                                                  ("A plain", "A test rows"), ("B plain", "B test rows"),
                                                  ("A dummy", "A test rows"), ("B dummy", "B test rows"))])
    fig, axes = plt.subplots(1, len(mets), figsize=(3.2 * len(mets), 3.6))
    for ax, m_ in zip(axes, mets):
        sub = comp[comp.metric == m_]
        ax.bar(range(len(sub)), sub.value, color=["#7f7f7f", "#1f77b4", "#d62728", "#aec7e8", "#ff9896", "#d9d9d9", "#f2d0d0"])
        ax.set_xticks(range(len(sub)), [s.replace(" test rows", "") for s in sub.series], rotation=60, ha="right", fontsize=7)
        ax.set_title(m_)
    fig.suptitle(f"Test metrics, {task} (frozen models, plain linear/logistic and dummy references)")
    fig.tight_layout()
    w.figure("test_metrics_comparison", fig, comp, ids=("T1.3",), title="Test metrics comparison")
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(7, 4))
    for col, lab, c in (("A_on_A_rows", "A on A rows", "#7f7f7f"), ("A_on_B_rows", "A on B rows", "#1f77b4"), ("B_on_B_rows", "B on B rows", "#d62728")):
        ax.plot(ft.period, ft[col], marker="o", label=lab, color=c)
    ax.axvline(len(ft) - 1.5, ls=":", c="k", lw=0.8)
    ax.set(ylabel=metric, title=f"Fold by fold and test ({metric}; folds are selection scores, test is unbiased)")
    ax.legend()
    fig.tight_layout()
    w.figure("fold_and_test", fig, ft, ids=("T1.6",), title="Fold by fold and test (B-C13)")
    plt.close(fig)
    bt = pt[pt.rows == "B test rows"]
    if task == "classification":
        from sklearn.calibration import calibration_curve
        from sklearn.metrics import precision_recall_curve, roc_curve
        fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
        cur = []
        for model, c in (("A frozen", "#1f77b4"), ("B frozen", "#d62728")):
            s_ = bt[bt.model == model]
            pr, rc, _ = precision_recall_curve(s_.y_true, s_.y_pred)
            fpr, tpr, _ = roc_curve(s_.y_true, s_.y_pred)
            fr_, mp_ = calibration_curve(s_.y_true, s_.y_pred, n_bins=10, strategy="quantile")
            axes[0].plot(rc, pr, label=model, color=c)
            axes[1].plot(fpr, tpr, label=model, color=c)
            axes[2].plot(mp_, fr_, marker="o", label=model, color=c)
            cur.append(pd.DataFrame({"model": model, "curve": "reliability", "x": mp_, "y": fr_}))
        axes[1].plot([0, 1], [0, 1], "k--", lw=0.8)
        axes[2].plot([0, 1], [0, 1], "k--", lw=0.8)
        axes[0].set(xlabel="recall", ylabel="precision", title="PR curve, B's test rows")
        axes[1].set(xlabel="false positive rate", ylabel="true positive rate", title="ROC curve, B's test rows")
        axes[2].set(xlabel="mean predicted probability", ylabel="observed detractor share", title="Reliability, B's test rows")
        for ax in axes:
            ax.legend()
        fig.tight_layout()
        w.figure("test_curves", fig, pd.concat(cur, ignore_index=True), ids=("T1.4",), title="PR, ROC and reliability on B's test rows")
        plt.close(fig)
        cm = []
        fig, axes = plt.subplots(1, 2, figsize=(9, 4))
        for ax, (model, t_) in zip(axes, (("A frozen", thr["A"]), ("B frozen", thr["B"]))):
            s_ = bt[bt.model == model]
            yp = (s_.y_pred.to_numpy() >= t_).astype(int)
            yt_ = s_.y_true.to_numpy().astype(int)
            mat = np.array([[int(((yt_ == 0) & (yp == 0)).sum()), int(((yt_ == 0) & (yp == 1)).sum())],
                            [int(((yt_ == 1) & (yp == 0)).sum()), int(((yt_ == 1) & (yp == 1)).sum())]])
            ax.imshow(mat, cmap="Blues")
            for i in range(2):
                for j in range(2):
                    ax.text(j, i, f"{mat[i, j]:,}", ha="center", va="center")
            ax.set_xticks([0, 1], ["predicted no", "predicted detractor"])
            ax.set_yticks([0, 1], ["actual no", "actual detractor"])
            ax.set_title(f"{model} at {t_:.4f} (B's test rows)")
            cm.append({"model": model, "threshold": t_, "tn": mat[0, 0], "fp": mat[0, 1], "fn": mat[1, 0], "tp": mat[1, 1]})
        fig.tight_layout()
        cmd = pd.DataFrame(cm)
        w.table("confusion_test", cmd, ids=("T1.4",))
        w.figure("confusion_test", fig, cmd, ids=("T1.4",), title="Confusion matrices on B's test rows")
        plt.close(fig)
    else:
        fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
        err = []
        for model, c in (("A frozen", "#1f77b4"), ("B frozen", "#d62728")):
            s_ = bt[bt.model == model]
            e = s_.y_pred - s_.y_true
            axes[0].hist(e.clip(-30, 30), bins=60, alpha=0.5, label=model, color=c)
            smp = s_.sample(min(3000, len(s_)), random_state=seed)
            axes[1].scatter(smp.y_true, smp.y_pred, s=3, alpha=0.3, label=model, color=c)
            err.append(pd.DataFrame({"model": model, "error_days": e.to_numpy()}))
        axes[0].set(xlabel="predicted − actual (days, clipped at ±30)", title="Error distribution, B's test rows")
        axes[1].plot([0, 60], [0, 60], "k--", lw=0.8)
        axes[1].set(xlabel="actual lead time (days)", ylabel="predicted (days)", title="Predicted vs actual (sample of 3,000)")
        for ax in axes:
            ax.legend()
        fig.tight_layout()
        ed = pd.concat(err, ignore_index=True)
        w.figure("test_errors", fig, ed.groupby("model").error_days.describe().reset_index(), ids=("T1.3",), title="Errors on B's test rows")
        plt.close(fig)

    # checks ------------------------------------------------------------------------------------------------
    w.check("both frozen recipes recompute their sha256 (A e5-A-frozen, B e5-B-frozen)", True, ("T1.1",),
            f"A {a_rec['sha256'][:12]}…, B {b_rec['sha256'][:12]}…")
    man = pd.read_csv(E5 / f"stages/s05_partition/{task}/outputs/test_manifest.csv")
    w.check("A's test rows equal A's s05 test manifest; B's test rows are a subset after B's rules; no development row among them",
            set(a_test.order_id) == set(man.order_id) and set(b_test.order_id) <= set(a_test.order_id)
            and not set(b_test.order_id) & set(b_dev.order_id) and not set(a_test.order_id) & set(a_dev.order_id), ("T1.1",),
            f"A {len(a_test):,}, B {len(b_test):,} test rows")
    w.check("every final-fit row has a label observable before the test cutoff", bool((a_dev[LABEL_TS[task]] < cutoff).all()
            and (b_dev[LABEL_TS[task]] < cutoff).all()), ("T1.2",), f"A {len(a_dev):,}, B {len(b_dev):,} rows")
    w.check("leakage re-check on B's test rows: features recomputed by brute force from events in weeks before the prediction week match",
            max_diff < 1e-9 and last_ok, ("T1.1",), f"{n_sample} rows, max difference {max_diff:.2e}")
    w.check("no recipe field changed after the read: both frozen recipes still recompute the same sha256",
            _sha_ok(json.loads((Path(A_S08.format(task=task)) / "frozen_recipe.json").read_text())) and
            _sha_ok(json.loads((b_outputs_dir("b08", task) / "frozen_recipe.json").read_text())), ("T1.1",))
    w.check("each bundle reloads and re-predicts the test rows identically", all(parity.values()), ("T1.5",), str(parity))
    w.check("A's tree untouched: A's code matches e5-A-frozen after the run", bool(assert_a_frozen()), ("T1.1",))

    # cards -------------------------------------------------------------------------------------------------
    w.explain("T1.1", done=(f"Frozen recipes checked (A {a_rec['sha256'][:12]}…, B {b_rec['sha256'][:12]}…). Test read once at {read_at}: "
                            f"A {len(a_test):,} rows (s05 manifest); B {len(b_test):,} rows after B's rules (removed: "
                            + "; ".join(f"{k} {v:,}" for k, v in b_exc.reason_code.value_counts().items()) + "). "
                            "B's history features use every event completed before each row's prediction week (J-1 (a))."))
    w.explain("T1.2", done=(f"Final fits on development rows with labels observable before the cutoff: A {len(a_dev):,} rows, "
                            f"B {len(b_dev):,} rows; frozen recipes{' with sigmoid calibration (B-G-05)' if task == 'classification' else ''}; dummies refitted the same way."))
    w.explain("T1.3", done=(f"Test {metric.upper()}: A on A's rows {piv.loc[metric, ('A frozen', 'A test rows')]:.4f}; A on B's rows "
                            f"{piv.loc[metric, ('A frozen', 'B test rows')]:.4f}; B on B's rows {piv.loc[metric, ('B frozen', 'B test rows')]:.4f}. "
                            "All G-24 metrics in metrics_test.csv."))
    if task == "classification":
        w.explain("T1.4", done=(f"At the frozen threshold 1/6 on sigmoid probabilities, B's test rows: A precision "
                                f"{piv.loc['precision', ('A frozen', 'B test rows')]:.3f}, recall {piv.loc['recall', ('A frozen', 'B test rows')]:.3f}; "
                                f"B precision {piv.loc['precision', ('B frozen', 'B test rows')]:.3f}, recall {piv.loc['recall', ('B frozen', 'B test rows')]:.3f}, "
                                f"{piv.loc['alerts_per_day', ('B frozen', 'B test rows')]:.1f} alerts/day (cap 25)."))
    w.explain("T1.5", done="Bundles for A and B (model.joblib, schema.json, training_profile.json); reload parity " + str(parity) + ". B's bundle is the release (G-79).")
    w.explain("T1.6", done="Fold-by-fold (selection scores) and test (unbiased) table for A and B, festival days marked (fold_and_test_table.csv).")
    w.finish(seed=seed)
    if w.index["checks_failed"]:
        raise SystemExit(f"T1 {task}: checks failed: {w.index['checks_failed']}")
    print(f"T1 {task}: test {metric} A/A {piv.loc[metric, ('A frozen', 'A test rows')]:.4f}, A/B {piv.loc[metric, ('A frozen', 'B test rows')]:.4f}, "
          f"B/B {piv.loc[metric, ('B frozen', 'B test rows')]:.4f}")
