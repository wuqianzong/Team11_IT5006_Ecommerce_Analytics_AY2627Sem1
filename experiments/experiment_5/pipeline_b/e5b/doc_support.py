"""Doc support: charts and derived tables that the review tabs and the report need but no stage wrote
(pipeline_b/DOC_GAPS.md D-01 to D-06, REPORT_REQUESTS.md R-05, R-06). Reads A's frozen outputs (tag e5-A-frozen) and
B's accepted outputs; changes no model, no choice and no stage output. Writes only under pipeline_b/stages/doc_support.

Evidence IDs: DS.1 B2 history and lateness charts, DS.2 B4 selection chart, DS.3 partition chart (A and B),
DS.4 per-fold candidate scores (A s06, B B6), DS.5 population comparison (R-05), DS.6 ROC-AUC, Brier and confusion
comparison (R-06), DS.7 A's threshold by cap and by fold (D-05).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from e5lib import factory, protocol
from e5lib.metrics import COST_FN, COST_FP, score
from e5lib.paths import E5
from e5lib.training import TARGET

from .env import BWriter, assert_a_frozen, b_outputs_dir

STAGE = "doc_support"
A_ST = E5 / "stages"
PRIMARY = {"regression": "mae", "classification": "ap"}
B_NEW = ("B-C6", "B-C7", "B-C8", "B-C8b", "B-C9")


def _plt():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def run(task: str) -> None:
    assert_a_frozen()
    w = BWriter(STAGE, task)
    seed = int(protocol.load()["seed"])
    plt = _plt()
    m = PRIMARY[task]

    # DS.1 B2: history coverage by quarter; lateness by route ------------------------------------------------
    cov = pd.read_csv(w.read(b_outputs_dir("b02", task) / "history_coverage.csv"))
    feats = list(dict.fromkeys(cov.feature))
    fig, axes = plt.subplots(1, len(feats), figsize=(5 * len(feats), 3.8), sharey=True)
    for ax, f in zip(axes, feats):
        p = cov[cov.feature == f].pivot_table(index="quarter", columns="source", values="share", fill_value=0)
        bottom = np.zeros(len(p))
        for i, s in enumerate(p.columns):
            ax.bar(p.index, p[s], bottom=bottom, label=s, color=["#1f77b4", "#9ecae1", "#c6dbef", "#d9d9d9"][i % 4] if s.startswith("own") or i else "#1f77b4")
            bottom += p[s].to_numpy()
        ax.set_title(f)
        ax.tick_params(axis="x", rotation=60)
        ax.legend(fontsize=7)
    axes[0].set_ylabel("share of B rows")
    fig.suptitle(f"Where each history feature comes from, by quarter ({task}; own history vs fallbacks)")
    fig.tight_layout()
    w.figure("b2_history_coverage", fig, cov, ids=("DS.1",), title="History coverage by quarter")
    plt.close(fig)
    ls = pd.read_csv(w.read(b_outputs_dir("b02", task) / "lateness_summary_B.csv.gz"))
    ls["late_n"] = ls.late_handover_rate * ls.handovers
    rt = ls.groupby("route").agg(handovers=("handovers", "sum"), late=("late_n", "sum"),
                                 median_delivery_days=("delivery_days_median", "median")).reset_index()
    rt["late_handover_rate"] = rt.late / rt.handovers
    rt = rt.sort_values("handovers", ascending=False).drop(columns=["late"])
    w.table("b2_lateness_by_route", rt, ids=("DS.1",))
    top = rt.head(15).iloc[::-1]
    fig, ax = plt.subplots(1, 2, figsize=(11, 5), sharey=True)
    ax[0].barh(top.route, top.late_handover_rate, color="#1f77b4")
    ax[0].set(xlabel="late-handover rate (share of handovers after the shipping limit)", title="Late handover")
    ax[1].barh(top.route, top.median_delivery_days, color="#7f7f7f")
    ax[1].set(xlabel="median of weekly median delivery days", title="Delivery time")
    fig.suptitle("15 busiest routes (seller state -> customer state), development period")
    fig.tight_layout()
    w.figure("b2_lateness_by_route", fig, top, ids=("DS.1",), title="Lateness by route")
    plt.close(fig)

    # DS.2 B4 selection: share and cumulative share, B's new features marked -----------------------------------
    rk = pd.read_csv(w.read(b_outputs_dir("b04", task) / "selection_ranking_B.csv")).sort_values("rank")
    fig, ax = plt.subplots(figsize=(11, 4.5))
    col = np.where(rk.source.isin(B_NEW), "#1f77b4", "#bdbdbd")
    ax.bar(range(len(rk)), rk.share, color=col)
    ax2 = ax.twinx()
    ax2.plot(range(len(rk)), rk.cumulative_share, color="k", marker=".")
    ax2.axhline(0.99, color="k", ls=":", lw=0.8)
    cut = int(rk.selected.astype(bool).sum())
    ax.axvline(cut - 0.5, color="#d62728", ls="--", lw=0.8)
    ax.set_xticks(range(len(rk)), rk.feature, rotation=75, ha="right", fontsize=7)
    ax.set(ylabel="share of total importance", title=f"B4 selection ({task}): blue = B's new features, red line = 99% cut ({cut} kept)")
    ax2.set_ylabel("cumulative share")
    fig.tight_layout()
    w.figure("b4_selection", fig, rk, ids=("DS.2",), title="B4 selection ranking")
    plt.close(fig)

    # DS.3 partition: A's folds and B's rows per fold ------------------------------------------------------------
    fs = pd.read_csv(w.read(b_outputs_dir("b05", task) / "fold_summary_B.csv"))
    fig, ax = plt.subplots(figsize=(10, 3.6))
    for r in fs.itertuples():
        t0, t1 = pd.Timestamp(r.a_train_start), pd.Timestamp(r.a_train_end)
        v0, v1 = pd.Timestamp(r.a_validation_start), pd.Timestamp(r.a_validation_end)
        ax.barh(r.fold, (t1 - t0).days, left=t0, color="#c6dbef")
        ax.barh(r.fold, (v1 - v0).days, left=v0, color="#1f77b4")
        ax.text(t0, r.fold, f" train B {r.train_rows:,} / A {r.a_train_rows:,}", va="center", fontsize=7)
        ax.text(v1, r.fold, f" val B {r.validation_rows:,} / A {r.a_validation_rows:,}", va="center", fontsize=7)
    ax.invert_yaxis()
    ax.set(ylabel="fold", title=f"Time-ordered folds ({task}): A's boundaries, B's rows inside them (light = training, dark = validation)")
    fig.tight_layout()
    w.figure("b5_partition", fig, fs, ids=("DS.3",), title="Partition: A's folds with B's rows")
    plt.close(fig)

    # DS.4 per-fold scores of every candidate: A's s06 and B's B6 --------------------------------------------------
    for tag, path in (("a_s06", A_ST / f"s06_training/{task}/outputs/metrics_long.csv"), ("b_b06", b_outputs_dir("b06", task) / "metrics_long.csv")):
        ml = pd.read_csv(w.read(path))
        ml = ml[(ml.metric == m) & ml.threshold.isna()] if "threshold" in ml else ml[ml.metric == m]
        t = ml.pivot_table(index=["family", "candidate_id", "phase"], columns="fold", values="value").reset_index()
        t.columns = [f"fold_{c}" if isinstance(c, (int, np.integer)) else c for c in t.columns]
        fc = [c for c in t.columns if str(c).startswith("fold_")]
        t["mean"], t["se"] = t[fc].mean(axis=1), t[fc].std(axis=1, ddof=1) / np.sqrt(len(fc))
        w.table(f"{tag}_per_fold_scores", t, ids=("DS.4",))
        v = t[t.phase == "validation"]
        fig, ax = plt.subplots(figsize=(8, 4))
        for r in v.itertuples():
            ax.plot(range(1, len(fc) + 1), [getattr(r, c) for c in fc], marker="o", label=r.family)
        ax.set(xlabel="fold", ylabel=m, xticks=range(1, len(fc) + 1),
               title=f"{'A s06' if tag == 'a_s06' else 'B B6'} {task}: validation {m.upper()} per fold, every family (selection scores)")
        ax.legend()
        fig.tight_layout()
        w.figure(f"{tag}_per_fold_scores", fig, v, ids=("DS.4",), title="Per-fold validation scores")
        plt.close(fig)

    # DS.5 population comparison (R-05) ------------------------------------------------------------------------------
    ps = pd.read_csv(w.read(b_outputs_dir("b08", task) / "population_summary.csv"))
    fig, ax = plt.subplots(figsize=(8, 3.8))
    x = np.arange(len(ps))
    ax.bar(x - 0.2, ps.mean_5_folds, 0.4, yerr=ps.se_5_folds, color="#1f77b4", label="5 folds (decision)", capsize=4)
    ax.bar(x + 0.2, ps.mean_folds_2_5, 0.4, yerr=ps.se_folds_2_5, color="#9ecae1", label="folds 2-5 (description)", capsize=4)
    ax.set_xticks(x, ["A model,\nA rows", "A model,\nB rows", "B model,\nB rows"])
    ax.set(ylabel=f"{m.upper()} (mean ± SE)", title=f"Validation {m.upper()} by population ({task}); raw scores as in B8's adoption rule")
    ax.legend()
    fig.tight_layout()
    w.figure("r05_population", fig, ps, ids=("DS.5",), title="Population comparison (R-05)")
    plt.close(fig)

    # DS.6 ROC-AUC, Brier, confusion (R-06; classification) -----------------------------------------------------------
    if task == "classification":
        mp = pd.read_csv(w.read(b_outputs_dir("b08", task) / "metrics_by_population.csv"))
        mp = mp[mp.variant == "sigmoid"]
        fig, axes = plt.subplots(1, 3, figsize=(13, 3.8))
        for ax, mm in zip(axes, ("ap", "roc_auc", "brier")):
            s = mp[mp.metric == mm]
            ax.bar(range(len(s)), s.mean_5_folds, yerr=s.se_5_folds, color=["#7f7f7f", "#9ecae1", "#1f77b4"], capsize=4)
            ax.set_xticks(range(len(s)), [f"{a.split()[0]} model,\n{b.split()[0]} rows" for a, b in zip(s.model, s.rows)])
            ax.set_title(f"{mm} (sigmoid, mean ± SE over 5 folds)")
        fig.suptitle("Validation AP, ROC-AUC and Brier by population (lower Brier is better)")
        fig.tight_layout()
        w.figure("r06_auc_brier", fig, mp, ids=("DS.6",), title="AP, ROC-AUC and Brier by population (R-06)")
        plt.close(fig)
        cc = pd.read_csv(w.read(b_outputs_dir("b08", task) / "confusion_comparison.csv"))
        pooled = cc[cc.fold.astype(str).str.lower().isin(["all", "pooled", "total"])] if cc.fold.dtype == object else cc.iloc[0:0]
        if pooled.empty:
            pooled = cc.groupby("model")[["tp", "fp", "fn", "tn"]].sum().reset_index()
        fig, axes = plt.subplots(1, len(pooled), figsize=(4.5 * len(pooled), 3.8))
        for ax, r in zip(np.atleast_1d(axes), pooled.itertuples()):
            mat = np.array([[r.tn, r.fp], [r.fn, r.tp]], dtype=float)
            ax.imshow(mat, cmap="Blues")
            for i in range(2):
                for j in range(2):
                    ax.text(j, i, f"{int(mat[i, j]):,}", ha="center", va="center")
            ax.set_xticks([0, 1], ["predicted no", "predicted detractor"])
            ax.set_yticks([0, 1], ["actual no", "actual detractor"])
            ax.set_title(r.model, fontsize=9)
        fig.suptitle("Confusion on B's validation rows, 5 folds pooled, threshold 1/6 on sigmoid probabilities")
        fig.tight_layout()
        w.figure("r06_confusion", fig, pooled, ids=("DS.6",), title="Confusion comparison (R-06)")
        plt.close(fig)

    # DS.7 A's threshold by cap and by fold (D-05; classification) ----------------------------------------------------
    if task == "classification":
        from e5lib.selection import confusion_at
        from e5lib.tuning import single_threaded
        tc = pd.read_csv(w.read(A_ST / "s08_selection/classification/outputs/curves/threshold_curve.csv"))
        crows = []
        for cap in (5, 10, 15, 20, 25, 30, 35, 40, 50):
            ok = tc[tc.alerts_per_day <= cap]
            if not ok.empty:
                b = ok.sort_values(["cost", "threshold"], ascending=[True, False]).iloc[0]
                crows.append({"daily_alert_cap": cap, "best_threshold_in_curve": b.threshold, "alerts_per_day": b.alerts_per_day,
                              "precision": b.precision, "recall": b.recall, "cost": b.cost})
        w.table("a_threshold_by_cap", pd.DataFrame(crows), ids=("DS.7",))
        y_col = TARGET[task]
        a_rec = pd.read_csv(w.read(A_ST / "s02_data/common/outputs/records.csv.gz"), parse_dates=["purchase_ts"], low_memory=False).set_index("order_id", drop=False)
        folds = pd.read_csv(w.read(A_ST / "s05_partition/classification/outputs/folds.csv"))
        spec = dict(json.loads(w.read(A_ST / "s08_selection/classification/outputs/selected_spec.json").read_text())["spec"], calibration="sigmoid")
        cal = pd.read_csv(w.read(A_ST / "s08_selection/classification/outputs/calibration_folds.csv"))
        frows, devs = [], []
        for k in sorted(folds.fold.unique()):
            tr = folds[(folds.fold == k) & (folds.role == "train")].order_id
            va = folds[(folds.fold == k) & (folds.role == "validation")].order_id
            cm = factory.build(spec)
            single_threaded(cm.estimator)
            cm.fit(a_rec.loc[tr], a_rec.loc[tr, y_col].to_numpy())
            p = cm.predict_proba(a_rec.loc[va])[:, 1]
            y = a_rec.loc[va, y_col].to_numpy().astype(int)
            devs.append(abs(score(task, y, proba=p)["ap"] - float(cal[(cal.variant == "sigmoid") & (cal.fold == k)].ap.iloc[0])))
            c = confusion_at(y, p, 1 / 6)
            al = c["tp"] + c["fp"]
            frows.append({"fold": int(k), "threshold": 1 / 6, "alerts": al, **c, "precision": c["tp"] / al if al else np.nan,
                          "recall": c["tp"] / (c["tp"] + c["fn"]) if c["tp"] + c["fn"] else np.nan, "cost": COST_FN * c["fn"] + COST_FP * c["fp"]})
        w.table("a_threshold_by_fold", pd.DataFrame(frows), ids=("DS.7",))
        w.check("A's sigmoid refit per fold reproduces A's s08 calibration AP", max(devs) < 1e-9, ("DS.7",), f"max difference {max(devs):.2e}")
        w.explain("DS.7", done="A's best threshold under each daily cap (from A's s08 threshold curve) and A's 1/6 threshold fold by fold on A's validation rows (sigmoid refit, verified against A's calibration step).")

    w.check("A's tree untouched: A's code matches e5-A-frozen", bool(assert_a_frozen()), ("DS.1",))
    w.explain("DS.1", done="B2 history-source shares by quarter and the 15 busiest routes' late-handover rate and delivery time.")
    w.explain("DS.2", done="B4 ranking with B's new features marked and the 99% cut.")
    w.explain("DS.3", done="A's fold boundaries with B's and A's row counts per fold.")
    w.explain("DS.4", done=f"Per-fold {m.upper()} of every s06 / B6 family, training and validation (tables), validation chart.")
    w.explain("DS.5", done="Mean ± SE of the primary metric by population, 5 folds and folds 2-5 (R-05).")
    if task == "classification":
        w.explain("DS.6", done="AP, ROC-AUC and Brier by population (sigmoid) and pooled confusion matrices at 1/6 on B's validation rows (R-06).")
    w.finish(seed=seed)
    if w.index["checks_failed"]:
        raise SystemExit(f"doc_support {task}: checks failed: {w.index['checks_failed']}")
    print(f"doc_support {task}: {len(w.index['files'])} files")
