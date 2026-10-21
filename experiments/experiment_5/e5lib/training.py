"""s06 training shared by both task nodes (blueprint spec/blueprints/s06_training.md).

Written for Experiment 5 from the blueprint; no code or numbers from earlier experiments.

- pipeline factory (6.1): the s04 recipe of each family plus its s06 settings, built by e5lib.factory
- families, basic to complex (6.2): dummy -> linear/logistic -> single tree -> forest, kept by the s01
  one-standard-error rule (G-33)
- scores recorded (6.4): training and validation scores per candidate and fold, fit time, warnings
- diagnostics (6.5 regression, 6.6 classification) on out-of-fold predictions
- learning curves and design matrix (6.7) on the latest fold
- every pipeline is fitted inside a training fold only; no test row is read (population guard)
"""
from __future__ import annotations

import time
import warnings

import numpy as np
import pandas as pd

from . import factory
from .candidates import make_id

STAGE = "s06_training"
TARGET = {"regression": "lead_days", "classification": "is_detractor"}
FAMILIES = ("dummy", "linear", "tree", "forest")  # simplicity order, s01 1.7
FAMILY_LABEL = {"dummy": "dummy", "linear": "linear/logistic", "tree": "single tree", "forest": "forest"}
LEARNING_SIZES = (0.2, 0.4, 0.6, 0.8, 1.0)


# ---------------------------------------------------------------------------------------------
# Candidates (6.1, 6.2)
# ---------------------------------------------------------------------------------------------
def s06_params(family: str, settings: dict) -> dict:
    """Plain s06 settings of a family from protocol.yaml families.s06_settings (s01 1.6)."""
    if family == "tree":
        return dict(settings["tree"])
    if family == "forest":
        # 200 trees are fixed in e5lib.factory (s01 1.8), so n_estimators is not passed again.
        f = dict(settings["forest"])
        if int(f.pop("n_estimators")) != factory.FOREST_TREES:
            raise ValueError("protocol forest size differs from e5lib.factory.FOREST_TREES")
        return f
    return {}  # dummy; plain linear; logistic unregularised (C = inf is the factory default)


def candidate_specs(task: str, recipes: dict, settings: dict, seed: int) -> list[dict]:
    """One spec per family, in simplicity order: the s04 recipe unchanged, plus params and seed."""
    out = []
    for rank, fam in enumerate(FAMILIES):
        spec = dict(recipes[fam]["spec"])
        params = s06_params(fam, settings)
        if params:
            spec["params"] = params
        spec["random_state"] = seed
        out.append({"family": fam, "simplicity": rank, "spec": spec, "candidate_id": make_id(spec)})
    return out


# ---------------------------------------------------------------------------------------------
# Fitting and scoring (6.4)
# ---------------------------------------------------------------------------------------------
def _single_thread_predict(model) -> None:
    """Forests fit in parallel (deterministic per tree) but sum their trees in thread order when predicting,
    which changes the last digits from run to run. Predicting with one thread keeps reruns byte-identical."""
    for est in (getattr(model, "regressor_", None), model):
        if est is not None and hasattr(est, "named_steps"):
            final = est.named_steps["model"]
            if hasattr(final, "n_jobs"):
                final.n_jobs = 1


def predict(task: str, model, X: pd.DataFrame) -> np.ndarray:
    _single_thread_predict(model)
    if task == "regression":
        return np.asarray(model.predict(X), dtype=float)
    return np.asarray(model.predict_proba(X)[:, 1], dtype=float)


def fit_fold(task: str, spec: dict, Xtr, ytr, Xva):
    """Fit one pipeline on a training fold; returns (model, train predictions, validation predictions, info)."""
    model = factory.build(spec)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        t0 = time.perf_counter()
        model.fit(Xtr, ytr)
        fit_s = time.perf_counter() - t0
    names = sorted({type(c.message).__name__ for c in caught if issubclass(c.category, Warning)})
    conv = sum(1 for c in caught if c.category.__name__ == "ConvergenceWarning")
    return model, predict(task, model, Xtr), predict(task, model, Xva), {
        "fit_seconds": fit_s, "warnings": len(caught), "convergence_warnings": conv, "warning_types": "; ".join(names)}


def score_rows(task: str, y, pred, thresholds: dict[str, float]) -> list[dict]:
    """Every s01 metric as (metric, value, threshold) rows; threshold-dependent ones at each named threshold."""
    from .metrics import score
    rows = []
    if task == "regression":
        for k, v in score(task, y, y_pred=pred).items():
            if k != "n_rows":
                rows.append({"metric": k, "value": float(v), "threshold": ""})
        return rows
    base = score(task, y, proba=pred)
    for k in ("ap", "roc_auc", "brier", "prevalence"):
        rows.append({"metric": k, "value": float(base[k]), "threshold": ""})
    for name, t in thresholds.items():
        s = score(task, y, proba=pred, threshold=t)
        for k in ("precision", "recall", "f1", "tp", "fp", "tn", "fn", "alert_rate", "error_rate", "cost"):
            rows.append({"metric": k, "value": float(s[k]), "threshold": name})
    return rows


# ---------------------------------------------------------------------------------------------
# Decision rule (6.2, G-33)
# ---------------------------------------------------------------------------------------------
def paired_gain(val_scores: pd.DataFrame, simpler: str, complex_: str, higher: bool) -> dict:
    """Per-fold gain of the complex candidate over the simpler one (positive = complex better), its mean,
    paired SE and the number of folds it wins. Description only: the decision is the one-SE rule (s01 1.7)."""
    v = val_scores.pivot(index="fold", columns="candidate_id", values="value")
    gain = (v[complex_] - v[simpler]) if higher else (v[simpler] - v[complex_])
    return {"fold_gains": {int(k): float(g) for k, g in gain.items()}, "mean_gain": float(gain.mean()),
            "paired_se": float(gain.std(ddof=1) / np.sqrt(len(gain))), "folds_better": int((gain > 0).sum()),
            "n_folds": int(len(gain))}


def ladder(val_scores: pd.DataFrame, metric: str, higher: bool, order: list[str]) -> list[dict]:
    """Walk the families basic to complex: the next family replaces the current one only if the
    one-SE rule chooses it over the current one (s01 1.7), i.e. only an incremental gain beyond one
    standard error justifies the more complex family. val_scores: candidate_id, fold, metric, value."""
    from .metrics import one_se_select
    steps, current = [], order[0]
    for nxt in order[1:]:
        pair = val_scores[val_scores["candidate_id"].isin([current, nxt])]
        r = one_se_select(pair, metric, higher, {current: 0, nxt: 1})
        steps.append({"simpler": current, "complex": nxt, "best_mean": r["best"], "chosen": r["chosen"],
                      "band": r["band"], "complex_kept": r["chosen"] == nxt,
                      "paired": paired_gain(pair, current, nxt, higher),
                      "summary": r["summary"].to_dict(orient="records")})
        if r["chosen"] == nxt:
            current = nxt
    return steps


# ---------------------------------------------------------------------------------------------
# Checks and diagnostics helpers
# ---------------------------------------------------------------------------------------------
def imputer_fitted_on_training(model, Xtr: pd.DataFrame, spec: dict) -> bool:
    """The learned medians equal the medians of the training fold (6.1: preprocessing fitted in the fold)."""
    pipe = model.regressor_ if hasattr(model, "regressor_") else model
    Xs = Xtr
    if "route_median" in pipe.named_steps:
        Xs = pipe.named_steps["route_median"].transform(Xtr)
    prep = pipe.named_steps["prep"]
    ok = True
    for name, trans, cols in prep.transformers_:
        if not name.startswith("num"):
            continue
        vals = Xs[cols].to_numpy(dtype=float)
        if name == "num_log":
            vals = np.log1p(vals)
        expected = np.nanmedian(vals, axis=0)
        got = trans.named_steps["impute"].statistics_
        ok &= bool(np.allclose(got, expected, equal_nan=True))
    return ok


def recent_subset(train_ids: np.ndarray, ts: pd.Series, share: float) -> np.ndarray:
    """The most recent share of a training fold (learning curves, 6.7): the rows closest to validation."""
    order = ts.loc[train_ids].sort_values(kind="mergesort")
    n = max(1, int(round(len(order) * share)))
    return order.index[-n:].to_numpy()


def imputation_table(task: str, fold: int, model, Xtr: pd.DataFrame, Xva: pd.DataFrame, spec: dict) -> list[dict]:
    """Learned imputation values and fill counts of one fitted pipeline (s06 report hook, Henry s02 2.12)."""
    pipe = model.regressor_ if hasattr(model, "regressor_") else model
    rows = []
    if "route_median" in pipe.named_steps:
        rm = pipe.named_steps["route_median"]
        c = rm.column
        rows.append({"task": task, "fold": fold, "feature": c, "rule": "route median (customer_state x primary_seller_state, "
                     "then customer_state, then global), before log1p", "learned_value": rm.global_,
                     "learned_scale": "km (global fallback median)", "route_groups": int(len(rm.levels_[0])),
                     "filled_train": int(Xtr[c].isna().sum()), "filled_validation": int(Xva[c].isna().sum())})
    Xs_tr = pipe.named_steps["route_median"].transform(Xtr) if "route_median" in pipe.named_steps else Xtr
    Xs_va = pipe.named_steps["route_median"].transform(Xva) if "route_median" in pipe.named_steps else Xva
    for name, trans, cols in pipe.named_steps["prep"].transformers_:
        if name == "remainder":
            continue
        imp = trans.named_steps["impute"]
        for j, col in enumerate(cols):
            if name.startswith("num"):
                rows.append({"task": task, "fold": fold, "feature": col,
                             "rule": "median + missing indicator" + (" (after log1p)" if name == "num_log" else ""),
                             "learned_value": float(imp.statistics_[j]),
                             "learned_scale": "log1p" if name == "num_log" else "raw",
                             "route_groups": "", "filled_train": int(Xs_tr[col].isna().sum()),
                             "filled_validation": int(Xs_va[col].isna().sum())})
            else:
                seen = set(Xs_tr[col].dropna())
                unseen = Xs_va[col].notna() & ~Xs_va[col].isin(seen)
                rows.append({"task": task, "fold": fold, "feature": col, "rule": "missing -> 'Unknown' level",
                             "learned_value": "Unknown", "learned_scale": "category", "route_groups": "",
                             "filled_train": int(Xs_tr[col].isna().sum()), "filled_validation": int(Xs_va[col].isna().sum()),
                             "validation_rows_unseen_level": int(unseen.sum())})
    return rows


def _curve_points(df: pd.DataFrame, key: str, n: int = 400) -> pd.DataFrame:
    """Thin a long curve to at most n points, keeping both ends (curve data stays small)."""
    if len(df) <= n:
        return df
    idx = np.unique(np.linspace(0, len(df) - 1, n).round().astype(int))
    return df.iloc[idx]


# ---------------------------------------------------------------------------------------------
# Node runner (stages/s06_training/<task>/run.py calls run(task))
# ---------------------------------------------------------------------------------------------
def run(task: str) -> None:
    import json

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scipy import stats
    from sklearn.calibration import calibration_curve
    from sklearn.metrics import precision_recall_curve, roc_curve

    from . import cv, data, protocol
    from .features import design_matrix
    from .metrics import PRIMARY, fold_summary, one_se_select
    from .outputs import Writer

    warnings.filterwarnings("ignore", message="Found unknown categories", category=UserWarning)
    w = Writer(STAGE, task)
    p = protocol.load()
    seed = int(p["seed"])
    metric, higher = PRIMARY[task]
    y_col = TARGET[task]
    cutoff = pd.Timestamp(protocol.get("data_dependent.test_cutoffs.values")[task])
    thresholds = {"0.5": 0.5, "1/6": 1.0 / 6.0} if task == "classification" else {}

    recipes = json.loads(data.upstream("s04_features", task, "recipes.json", STAGE).read_text(encoding="utf-8"))
    selected = json.loads(data.upstream("s04_features", task, "selected_features.json", STAGE).read_text(encoding="utf-8"))
    d = data.load("records", task, "development", STAGE).set_index("order_id", drop=False)
    fold_list = list(cv.folds(task, STAGE))
    cands = candidate_specs(task, recipes, p["families"]["s06_settings"], seed)
    cols = factory.feature_columns(cands[0]["spec"])
    ids = [c["candidate_id"] for c in cands]

    # 6.1-6.4 Fit every candidate in every fold --------------------------------------------------
    metric_rows, pred_rows, fit_rows, rows_used, imputation, in_fold = [], [], [], {}, [], []
    models_last = {}
    for k, tr_ids, va_ids in fold_list:
        Xtr, ytr = d.loc[tr_ids, cols], d.loc[tr_ids, y_col].to_numpy()
        Xva, yva = d.loc[va_ids, cols], d.loc[va_ids, y_col].to_numpy()
        for c in cands:
            model, ptr, pva, info = fit_fold(task, c["spec"], Xtr, ytr, Xva)
            rows_used.setdefault(c["candidate_id"], []).append((k, hash(tuple(tr_ids)), hash(tuple(va_ids))))
            fit_rows.append({"candidate_id": c["candidate_id"], "family": c["family"], "fold": k,
                             "train_rows": len(tr_ids), "validation_rows": len(va_ids), **info})
            for phase, yy, pp in (("train", ytr, ptr), ("validation", yva, pva)):
                n_pos = int(yy.sum()) if task == "classification" else ""
                for r in score_rows(task, yy, pp, thresholds):
                    metric_rows.append({"population": "development", "phase": phase, "fold": k,
                                        "candidate_id": c["candidate_id"], "n_rows": len(yy), "n_pos": n_pos,
                                        "family": c["family"], **r})
            pred_rows.append(pd.DataFrame({"order_id": va_ids, "task": task, "population": "development", "fold": k,
                                           "candidate_id": c["candidate_id"], "y_true": yva, "y_pred": pva}))
            if c["family"] != "dummy":
                in_fold.append(imputer_fitted_on_training(model, Xtr, c["spec"]))
            if c["family"] == "linear":
                imputation += imputation_table(task, k, model, Xtr, Xva, c["spec"])
            if k == fold_list[-1][0]:
                models_last[c["family"]] = model

    ml = pd.DataFrame(metric_rows)
    w.metrics_long(ml, ids=("6.4",))
    preds = pd.concat(pred_rows, ignore_index=True)
    w.predictions(preds, ids=("6.4", "6.5" if task == "regression" else "6.6"))
    fits = pd.DataFrame(fit_rows)
    # Fit times change from run to run, so they go to the run manifest, not to a hashed output (README 13.3).
    fit_times = {f"{r.candidate_id}|fold {r.fold}": round(float(r.fit_seconds), 3) for r in fits.itertuples()}
    w.table("fit_log", fits.drop(columns=["fit_seconds"]), ids=("6.4",))
    w.table("imputation_by_fold", pd.DataFrame(imputation), ids=("6.1",))

    # 6.2 Decision rule: ladder and overall one-SE choice -----------------------------------------
    val = ml[(ml["phase"] == "validation") & (ml["metric"] == metric)][["candidate_id", "fold", "metric", "value"]]
    trn = ml[(ml["phase"] == "train") & (ml["metric"] == metric)][["candidate_id", "fold", "metric", "value"]]
    steps = ladder(val, metric, higher, ids)
    overall = one_se_select(val, metric, higher, {c["candidate_id"]: c["simplicity"] for c in cands})
    vs, ts = fold_summary(val, metric), fold_summary(trn, metric)
    forward = steps[-1]["chosen"] if steps else ids[0]
    kept = {ids[0]}
    for s in steps:
        if s["complex_kept"]:
            kept.add(s["complex"])
    fam_of = {c["candidate_id"]: c["family"] for c in cands}
    ctab = pd.DataFrame([{
        "candidate_id": c["candidate_id"], "family": FAMILY_LABEL[c["family"]], "estimator": c["spec"]["estimator"],
        "params": json.dumps(c["spec"].get("params", {}), sort_keys=True), "simplicity": c["simplicity"],
        "description": f"{FAMILY_LABEL[c['family']]} ({c['spec']['estimator']}) on the s04 recipe, s06 plain settings",
        "train_mean": ts.loc[c["candidate_id"], "mean"], "validation_mean": vs.loc[c["candidate_id"], "mean"],
        "validation_se": vs.loc[c["candidate_id"], "se"],
        "kept": c["candidate_id"] in kept,
        "reason": ("baseline (simplest family)" if c["family"] == "dummy" else
                   next(("kept: beats " + FAMILY_LABEL[fam_of[s["simpler"]]] + " by more than one SE" if s["complex_kept"] else
                         "not kept: within one SE of " + FAMILY_LABEL[fam_of[s["simpler"]]] + ", the simpler family stays")
                        for s in steps if s["complex"] == c["candidate_id"]))} for c in cands])
    w.candidates(ctab, ids=("6.2",))
    for s in steps:
        w.decision(f"Keep {FAMILY_LABEL[fam_of[s['complex']]]} over {FAMILY_LABEL[fam_of[s['simpler']]]}?",
                   f"one-SE rule on validation {metric} (s01 1.7, G-33)", [s["simpler"], s["complex"]],
                   s["chosen"], ["metrics_long.csv", "candidates.csv"], ids=("6.2",),
                   notes=f"best mean: {s['best_mean']}; band {s['band'][0]:.4f} to {s['band'][1]:.4f}; paired gain of the "
                         f"complex family {s['paired']['mean_gain']:+.4f} (paired SE {s['paired']['paired_se']:.4f}), better in "
                         f"{s['paired']['folds_better']} of {s['paired']['n_folds']} folds (description only)")
    pg = pd.DataFrame([{"comparison": f"{FAMILY_LABEL[fam_of[s['complex']]]} vs {FAMILY_LABEL[fam_of[s['simpler']]]}",
                        "simpler": s["simpler"], "complex": s["complex"],
                        **{f"gain_fold_{k}": g for k, g in s["paired"]["fold_gains"].items()},
                        "mean_gain": s["paired"]["mean_gain"], "paired_se": s["paired"]["paired_se"],
                        "folds_better": s["paired"]["folds_better"], "kept_by_one_se_rule": s["complex_kept"]}
                       for s in steps])
    w.table("paired_differences", pg, ids=("6.2",))
    w.decision("Family carried as the s06 reference (all four candidates)", f"one-SE rule on validation {metric}",
               ids, overall["chosen"], ["metrics_long.csv", "candidates.csv"], ids=("6.2",),
               notes=f"best mean: {overall['best']}; ladder result: {forward}. s07 tunes the linear and tree "
                     "families whatever this result (s07 principle).")

    # Ladder figure
    fig, ax = plt.subplots(figsize=(8, 4))
    for i, c in enumerate(cands):
        v = val[val["candidate_id"] == c["candidate_id"]]
        ax.scatter([i] * len(v), v["value"], color="tab:gray", s=14)
        m, se = vs.loc[c["candidate_id"], "mean"], vs.loc[c["candidate_id"], "se"]
        ax.errorbar(i, m, yerr=se, fmt="o", color="tab:blue", capsize=5)
        ax.scatter(i, ts.loc[c["candidate_id"], "mean"], marker="x", color="tab:orange")
    ax.set_xticks(range(len(cands)))
    ax.set_xticklabels([FAMILY_LABEL[c["family"]] for c in cands])
    ax.set_ylabel(metric.upper() + (" (days)" if task == "regression" else ""))
    ax.set_title(f"{task}: validation {metric} per fold (grey), mean ± SE (blue), training mean (x)")
    fig.tight_layout()
    lad = vs.reset_index().merge(ts.reset_index()[["candidate_id", "mean"]].rename(columns={"mean": "train_mean"}))
    w.figure("family_ladder", fig, lad, ids=("6.2", "6.4"), title="Family ladder")
    plt.close(fig)

    # 6.5 Residual diagnostics (regression) -------------------------------------------------------
    resid_note = ""
    if task == "regression":
        best_tree = min((c for c in cands if c["family"] in ("tree", "forest")),
                        key=lambda c: vs.loc[c["candidate_id"], "mean"])
        shown = [c for c in cands if c["family"] == "linear"] + [best_tree]
        fig, axes = plt.subplots(len(shown), 3, figsize=(13, 4 * len(shown)))
        side = []
        rng = np.random.default_rng(seed)
        for row, c in zip(axes, shown):
            o = preds[preds["candidate_id"] == c["candidate_id"]]
            res = o["y_true"].to_numpy() - o["y_pred"].to_numpy()
            fit = o["y_pred"].to_numpy()
            pick = rng.choice(len(o), size=min(5000, len(o)), replace=False)
            row[0].scatter(fit[pick], res[pick], s=3, alpha=0.3)
            row[0].axhline(0, color="k", lw=0.8)
            row[0].set(xlabel="fitted (days)", ylabel="residual = actual - fitted (days)", title=f"{c['family']}: residual vs fitted")
            row[1].hist(res, bins=80)
            row[1].set(xlabel="residual (days)", title="residual histogram")
            q = np.linspace(0.005, 0.995, 199)
            theo, emp = stats.norm.ppf(q), np.quantile((res - res.mean()) / res.std(), q)
            row[2].scatter(theo, emp, s=6)
            row[2].plot(theo, theo, color="k", lw=0.8)
            row[2].set(xlabel="normal quantile", ylabel="standardised residual quantile", title="Q-Q plot")
            side.append(pd.DataFrame({"candidate_id": c["candidate_id"], "kind": "scatter_sample", "x": fit[pick], "y": res[pick]}))
            side.append(pd.DataFrame({"candidate_id": c["candidate_id"], "kind": "qq", "x": theo, "y": emp}))
            w.curve(f"residual_quantiles_{c['family']}", pd.DataFrame({"quantile": q, "residual": np.quantile(res, q)}), ids=("6.5",))
            resid_note += (f"{c['family']}: residual mean {res.mean():.2f}, median {np.median(res):.2f}, "
                           f"skewness {stats.skew(res):.2f}, share above +10 days {np.mean(res > 10):.2%}; ")
        fig.tight_layout()
        w.figure("residual_diagnostics", fig, pd.concat(side, ignore_index=True), ids=("6.5",), title="Residual diagnostics")
        plt.close(fig)

    # 6.6 Classification diagnostics --------------------------------------------------------------
    diag_rows = []
    if task == "classification":
        fig, axes = plt.subplots(1, 4, figsize=(20, 4.5))
        for c in cands:
            o = preds[preds["candidate_id"] == c["candidate_id"]]
            yt, pr = o["y_true"].to_numpy(), o["y_pred"].to_numpy()
            prec, rec, thr = precision_recall_curve(yt, pr)
            pr_df = pd.DataFrame({"candidate_id": c["candidate_id"], "recall": rec, "precision": prec,
                                  "threshold": np.append(thr, np.nan)})
            fpr, tpr, rthr = roc_curve(yt, pr)
            roc_df = pd.DataFrame({"candidate_id": c["candidate_id"], "fpr": fpr, "tpr": tpr, "threshold": rthr})
            frac, mean_p = calibration_curve(yt, pr, n_bins=10, strategy="quantile") if c["family"] != "dummy" else \
                (np.array([yt.mean()]), np.array([pr.mean()]))
            rel_df = pd.DataFrame({"candidate_id": c["candidate_id"], "mean_predicted": mean_p, "observed_share": frac})
            w.curve(f"pr_{c['family']}", _curve_points(pr_df, "recall"), ids=("6.6",))
            w.curve(f"roc_{c['family']}", _curve_points(roc_df, "fpr"), ids=("6.6",))
            w.curve(f"reliability_{c['family']}", rel_df, ids=("6.6",))
            lab = FAMILY_LABEL[c["family"]]
            axes[0].plot(rec, prec, label=lab)
            axes[1].plot(fpr, tpr, label=lab)
            axes[2].plot(mean_p, frac, marker="o", label=lab)
            from .metrics import score
            s = score(task, yt, proba=pr)
            diag_rows.append({"candidate_id": c["candidate_id"], "family": lab, "pooled_oof_ap": s["ap"],
                              "pooled_oof_roc_auc": s["roc_auc"], "pooled_oof_brier": s["brier"],
                              "mean_predicted": float(pr.mean()), "observed_prevalence": float(yt.mean())})
        best_cl = max((c for c in cands if c["family"] != "dummy"), key=lambda c: vs.loc[c["candidate_id"], "mean"])
        o = preds[preds["candidate_id"] == best_cl["candidate_id"]]
        bins = np.linspace(0, 1, 41)
        h = []
        for cls in (0, 1):
            vals = o.loc[o["y_true"] == cls, "y_pred"]
            axes[3].hist(vals, bins=bins, alpha=0.5, density=True, label=f"is_detractor = {cls}")
            cnt, _ = np.histogram(vals, bins=bins)
            h.append(pd.DataFrame({"candidate_id": best_cl["candidate_id"], "class": cls, "bin_left": bins[:-1], "count": cnt}))
        axes[0].set(xlabel="recall", ylabel="precision", title="PR (pooled out-of-fold)")
        axes[1].plot([0, 1], [0, 1], "k--", lw=0.8)
        axes[1].set(xlabel="false positive rate", ylabel="true positive rate", title="ROC (pooled out-of-fold)")
        axes[2].plot([0, 1], [0, 1], "k--", lw=0.8)
        axes[2].set(xlabel="mean predicted probability", ylabel="observed detractor share", title="Reliability (deciles)")
        axes[3].set(xlabel="predicted probability", title=f"Predicted probability by class ({FAMILY_LABEL[best_cl['family']]})")
        for a in axes:
            a.legend(fontsize=7)
        fig.tight_layout()
        dtab = pd.DataFrame(diag_rows)
        w.table("oof_diagnostics", dtab, ids=("6.6",))
        w.figure("classification_diagnostics", fig, pd.concat(h, ignore_index=True), ids=("6.6",),
                 title="Classification diagnostics")
        plt.close(fig)

    # 6.7 Learning curves (latest fold) and design matrix ----------------------------------------
    k_last, tr_last, va_last = fold_list[-1]
    lc = []
    Xva, yva = d.loc[va_last, cols], d.loc[va_last, y_col].to_numpy()
    for share in LEARNING_SIZES:
        sub = recent_subset(tr_last, d["purchase_ts"], share)
        Xs, ys = d.loc[sub, cols], d.loc[sub, y_col].to_numpy()
        for c in cands:
            _, ptr, pva, _ = fit_fold(task, c["spec"], Xs, ys, Xva)
            from .metrics import score
            tr_s = score(task, ys, y_pred=ptr) if task == "regression" else score(task, ys, proba=ptr)
            va_s = score(task, yva, y_pred=pva) if task == "regression" else score(task, yva, proba=pva)
            lc.append({"candidate_id": c["candidate_id"], "family": c["family"], "share": share, "train_rows": len(sub),
                       "train_" + metric: tr_s[metric], "validation_" + metric: va_s[metric]})
    lc = pd.DataFrame(lc)
    w.curve("learning_curves", lc, ids=("6.7",))
    fig, axes = plt.subplots(1, len(cands), figsize=(4 * len(cands), 3.6), sharey=True)
    for a, c in zip(axes, cands):
        part = lc[lc["candidate_id"] == c["candidate_id"]]
        a.plot(part["train_rows"], part["train_" + metric], marker="o", label="training")
        a.plot(part["train_rows"], part["validation_" + metric], marker="o", label="validation")
        a.set(title=FAMILY_LABEL[c["family"]], xlabel=f"training rows (fold {k_last}, most recent)")
        a.legend(fontsize=7)
    axes[0].set_ylabel(metric.upper())
    fig.tight_layout()
    w.figure("learning_curves", fig, lc, ids=("6.7",), title="Learning curves")
    plt.close(fig)

    ytr_last = d.loc[tr_last, y_col].to_numpy()
    lc_note = "; ".join(
        f"{FAMILY_LABEL[c['family']]} validation {metric} {lc[(lc.candidate_id == c['candidate_id']) & (lc.share == LEARNING_SIZES[0])]['validation_' + metric].iloc[0]:.4f} "
        f"with the most recent 20% vs {lc[(lc.candidate_id == c['candidate_id']) & (lc.share == 1.0)]['validation_' + metric].iloc[0]:.4f} with all rows"
        for c in cands)
    target_note = (f"target mean in fold {k_last}: training {ytr_last.mean():.4f}, validation {yva.mean():.4f}")
    lin = next(c for c in cands if c["family"] == "linear")
    dm = []
    for k, tr_ids, _ in fold_list:
        r = design_matrix(d.loc[tr_ids], lin["spec"])
        dm.append({"fold": k, "candidate_id": lin["candidate_id"], **r})
    dm = pd.DataFrame(dm)
    w.table("design_matrix_by_fold", dm, ids=("6.7",))

    # Checks ----------------------------------------------------------------------------------------
    same_rows = all(v == rows_used[ids[0]] for v in rows_used.values())
    w.check("identical rows and folds for every candidate", same_rows, ("6.2", "6.4"),
            f"{len(cands)} candidates x {len(fold_list)} folds")
    w.check("preprocessing fitted inside the training fold only (learned medians equal the training-fold medians)",
            all(in_fold), ("6.1",), f"{len(in_fold)} fitted pipelines checked")
    unchanged = all({k: v for k, v in c["spec"].items() if k not in ("params", "random_state")} == recipes[c["family"]]["spec"]
                    for c in cands)
    w.check("every candidate uses its s04 recipe unchanged (selected features, log1p inputs" + (", log target)" if task == "regression" else ")"), unchanged,
            ("6.1", "6.2"), f"selected set of {len(selected['selected'])} features")
    w.check("the simplest model of each family is present (dummy, plain linear/logistic, depth-5 tree, s06 forest)",
            [c["family"] for c in cands] == list(FAMILIES), ("6.2",))
    used = np.concatenate([np.concatenate([t, v]) for _, t, v in fold_list])
    latest = d.loc[used, "purchase_ts"].max()
    w.check("no test row read: every row used was purchased before the test cutoff", bool(latest < cutoff), ("6.4",),
            f"latest purchase {latest}, cutoff {cutoff}")
    if task == "regression":
        w.check("regression scored on raw days (log target inverted)",
                bool((preds["y_pred"] > 0).all()) and all(c["spec"].get("log_target") for c in cands if c["family"] != "dummy"),
                ("6.1", "6.4"))
    w.check("linear/logistic design matrix full rank in every training fold", bool(dm["full_rank"].all()), ("6.7",),
            "; ".join(f"fold {r.fold} rank {r.rank} of {r.columns}" for r in dm.itertuples()))

    # Evidence cards ---------------------------------------------------------------------------------
    unit = " days" if task == "regression" else ""
    w.explain("6.1", done=f"{len(cands)} candidates built by e5lib.factory from the s04 recipes.json (one spec per family) "
              f"with the s06 settings from protocol.yaml; every pipeline fitted inside each of the {len(fold_list)} training "
              f"folds ({sum(len(t) for _, t, _ in fold_list):,} training rows over the folds). Learned imputation values "
              "per fold are in imputation_by_fold.csv, with the validation rows whose category level was unseen in "
              "the training fold (the one-hot step encodes them as all zeros).",
              inputs="s04 recipes.json and selected_features.json; s05 folds.csv; s02 records (development rows).")
    w.explain("6.2", done="Families basic to complex, validation " + metric + " mean ± SE over the folds: " +
              "; ".join(f"{FAMILY_LABEL[c['family']]} {vs.loc[c['candidate_id'], 'mean']:.4f} ± {vs.loc[c['candidate_id'], 'se']:.4f}{unit}"
                        for c in cands) + ". Ladder: " +
              "; ".join(f"{FAMILY_LABEL[fam_of[s['complex']]]} {'kept' if s['complex_kept'] else 'not kept'} over "
                        f"{FAMILY_LABEL[fam_of[s['simpler']]]}" for s in steps) +
              f". One-SE choice over all four: {FAMILY_LABEL[fam_of[overall['chosen']]]} (best mean: "
              f"{FAMILY_LABEL[fam_of[overall['best']]]}).",
              observation="Paired per-fold gain of each step (positive = the more complex family is better; description only, "
                          "s01 1.7): " + "; ".join(
                  f"{FAMILY_LABEL[fam_of[s['complex']]]} vs {FAMILY_LABEL[fam_of[s['simpler']]]} {s['paired']['mean_gain']:+.4f}{unit} "
                  f"(paired SE {s['paired']['paired_se']:.4f}), better in {s['paired']['folds_better']} of {s['paired']['n_folds']} folds"
                  for s in steps) + ".",
              reasoning="A more complex family is adopted only when its gain over the current family clears one standard error "
                        "of the fold means (the agreed rule). The fold SE also carries the level differences between folds "
                        "(drift), so a small but consistent paired gain can stay below it; the paired figures show that "
                        "without changing the decision.",
              conclusion="These are selection scores on the folds, not generalisation estimates (G-10). s07 tunes the "
                         "linear and tree families and compares each tuned configuration with its plain s06 model (G-55).")
    w.explain("6.4", done=f"metrics_long.csv: training and validation scores for {len(cands)} candidates x "
              f"{len(fold_list)} folds on every s01 metric" + (" (threshold metrics at 0.5 and 1/6)" if task == "classification" else "")
              + f"; fit_log.csv: rows and warnings per fit, fit times in _manifest.json (convergence warnings: {int(fits['convergence_warnings'].sum())}); "
              f"predictions.csv.gz: {len(preds):,} out-of-fold predictions.")
    if task == "regression":
        w.explain("6.5", done="Residual vs fitted, histogram and Q-Q plot on out-of-fold predictions of the plain linear "
                  "model and the better tree model (" + FAMILY_LABEL[best_tree["family"]] + "). " + resid_note.rstrip("; ") + ".",
                  label="observation")
    else:
        w.explain("6.6", done="Pooled out-of-fold PR, ROC and reliability curves for every family, Brier score, and the "
                  "predicted-probability histogram per class for the best non-dummy family. " +
                  "; ".join(f"{r['family']}: AP {r['pooled_oof_ap']:.4f}, ROC-AUC {r['pooled_oof_roc_auc']:.4f}, "
                            f"Brier {r['pooled_oof_brier']:.4f}" for r in diag_rows) + ".",
                  reasoning="Pooled curves join the five validation blocks; the selection rule uses the per-fold means "
                            "in 6.2, so the two can differ slightly.")
    w.explain("6.7", done=f"Learning curves on fold {k_last}: the most recent 20, 40, 60, 80 and 100% of its training rows "
              f"against the same validation block ({len(va_last):,} rows). Linear/logistic design matrix per training fold: "
              + "; ".join(f"fold {r.fold} rank {r.rank} of {r.columns}, condition number {r.condition_number:.3g}" for r in dm.itertuples()) + ".",
              observation=lc_note + "; " + target_note + ".",
              reasoning="Subsets keep the rows closest to the validation block, so a smaller training set is not also an "
                        "older one; the tree recipe is not measured (rank-deficient by design, s04 M-01).")
    w.explain("6.8", done="Outputs: metrics_long.csv, predictions.csv.gz, candidates.csv, decision.json, fit_log.csv, "
              "imputation_by_fold.csv, design_matrix_by_fold.csv, curves/ and figures/ with sidecar data.")
    w.json("counts", {"task": task, "candidates": ids, "folds": [{"fold": k, "train_rows": len(t), "validation_rows": len(v)}
                                                                 for k, t, v in fold_list],
                      "primary_metric": metric, "ladder_result": forward, "one_se_choice": overall["chosen"],
                      "best_mean": overall["best"], "seed": seed}, ids=("6.2", "6.8"))
    w.finish(seed=seed, extra={"fit_seconds": fit_times})
    failed = w.index["checks_failed"]
    if failed:
        raise SystemExit(f"s06 {task}: checks failed: {failed}")
