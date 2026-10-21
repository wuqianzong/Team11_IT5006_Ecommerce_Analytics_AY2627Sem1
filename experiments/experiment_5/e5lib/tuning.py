"""s07 tuning shared by both task nodes (blueprint spec/blueprints/s07_tuning.md).

Written for Experiment 5 from the blueprint; no code or numbers from earlier experiments.

- grids (7.1-7.4): read from protocol.yaml (pre-registered in s01, G-37, G-43)
- search (7.5): GridSearchCV over the whole s04 pipeline on the s05 folds, refit=False,
  return_train_score=True; best per family = the simplest configuration within one standard
  error of the best mean (s01 1.7), then compared with the family's plain s06 model by the same
  rule: the plain model is kept unless the tuned one beats it by more than one SE (G-55)
- overfitting check (7.6): train-validation gap of every configuration
- the cross-family ladder of the family winners is shown as description only; s08 chooses
- every estimator is single-threaded (the search runs configurations in parallel), so reruns are
  byte-identical; fit times go to the run manifest
"""
from __future__ import annotations

import itertools
import json
import warnings

import numpy as np
import pandas as pd

from . import factory
from .candidates import make_id
from .training import FAMILIES, FAMILY_LABEL, TARGET, candidate_specs, fit_fold, ladder, paired_gain

STAGE = "s07_tuning"
TUNED = ("linear", "tree", "forest")
SCORING = {"regression": "neg_mean_absolute_error", "classification": "average_precision"}


# ---------------------------------------------------------------------------------------------
# Grids (7.1-7.4)
# ---------------------------------------------------------------------------------------------
def family_grid(task: str, family: str, grids: dict) -> tuple[str, dict]:
    """(estimator, parameter grid) of one family, straight from protocol.yaml grids."""
    cw = {"class_weight": list(grids["class_weight"])} if task == "classification" else {}
    if family == "linear":
        if task == "regression":
            return "ridge", {"alpha": [float(a) for a in grids["ridge_alpha"]]}
        return "logistic", {"C": [float(c) for c in grids["logistic_C"]], **cw}
    g = grids[family]
    est = {"tree": "tree_reg", "forest": "forest_reg"}[family] if task == "regression" else \
          {"tree": "tree_clf", "forest": "forest_clf"}[family]
    grid = {"max_depth": list(g["max_depth"]), "min_samples_leaf": list(g["min_samples_leaf"]), **cw}
    if family == "forest":
        if int(g["n_estimators"]) != factory.FOREST_TREES:
            raise ValueError("protocol forest size differs from e5lib.factory.FOREST_TREES")
        grid["max_features"] = [g["max_features"]]
    return est, grid


def configurations(grid: dict) -> list[dict]:
    keys = sorted(grid)
    return [dict(zip(keys, vals)) for vals in itertools.product(*(grid[k] for k in keys))]


def simplicity_key(family: str, params: dict) -> tuple:
    """Lower = simpler (s01 1.7): higher alpha, lower C, shallower depth, then larger leaf;
    no class weighting is simpler than balanced."""
    cw = 0 if params.get("class_weight") in (None, "None") else 1
    if "alpha" in params:
        return (-params["alpha"],)
    if "C" in params:
        return (params["C"], cw)
    return (params["max_depth"], -params["min_samples_leaf"], cw)


def base_spec(task: str, family: str, recipes: dict, estimator: str, seed: int) -> dict:
    spec = dict(recipes[family]["spec"])
    spec["estimator"] = estimator
    spec["random_state"] = seed
    return spec


def single_threaded(model):
    """Set every forest inside the model to one thread (determinism; the search parallelises)."""
    inner = model.regressor if hasattr(model, "regressor") else model
    final = inner.named_steps["model"]
    if hasattr(final, "n_jobs"):
        final.set_params(n_jobs=1)
    return model


def param_prefix(task: str, spec: dict) -> str:
    return "regressor__model__" if task == "regression" and spec.get("log_target") else "model__"


# ---------------------------------------------------------------------------------------------
# Search (7.5)
# ---------------------------------------------------------------------------------------------
def search(task: str, family: str, spec: dict, grid: dict, X: pd.DataFrame, y: np.ndarray, splits, n_jobs: int):
    """GridSearchCV over the whole pipeline; returns (long fold table, per-config fit seconds, warnings per config)."""
    from sklearn.model_selection import GridSearchCV
    est = single_threaded(factory.build(spec))
    pre = param_prefix(task, spec)
    configs = configurations(grid)
    rows, secs, warn = [], {}, {}
    # Linear families: one search per configuration on one thread, so convergence warnings are attributed;
    # tree families: one search for the whole grid, configurations in parallel.
    batches = [[c] for c in configs] if family == "linear" else [configs]
    for batch in batches:
        pg = {pre + k: sorted({c[k] for c in batch}, key=lambda v: (v is None, str(v))) for k in batch[0]}
        if len(batch) > 1:
            pg = {pre + k: grid[k] for k in grid}
        gs = GridSearchCV(est, pg, scoring=SCORING[task], cv=splits, refit=False, return_train_score=True,
                          n_jobs=1 if family == "linear" else n_jobs, error_score="raise")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            gs.fit(X, y)
        conv = sum(1 for c in caught if c.category.__name__ == "ConvergenceWarning")
        res = gs.cv_results_
        for i, params in enumerate(res["params"]):
            p = {k[len(pre):]: v for k, v in params.items()}
            spec_i = dict(spec, params=p)
            cid = make_id(spec_i)
            secs[cid] = round(float(res["mean_fit_time"][i]), 3)
            warn[cid] = conv if family == "linear" else 0
            for k in range(len(splits)):
                sign = -1.0 if task == "regression" else 1.0
                rows.append({"candidate_id": cid, "family": family, "params": json.dumps(p, sort_keys=True, default=str),
                             "fold": k + 1, "train": sign * float(res[f"split{k}_train_score"][i]),
                             "validation": sign * float(res[f"split{k}_test_score"][i])})
    return pd.DataFrame(rows), secs, warn


def best_in_family(fold_table: pd.DataFrame, family: str, metric: str, higher: bool) -> dict:
    """One-SE rule inside a family's grid (7.5)."""
    from .metrics import one_se_select
    val = fold_table.rename(columns={"validation": "value"}).assign(metric=metric)[["candidate_id", "fold", "metric", "value"]]
    params = fold_table.drop_duplicates("candidate_id").set_index("candidate_id")["params"].map(json.loads)
    order = sorted(params.index, key=lambda c: (simplicity_key(family, params[c]), c))
    r = one_se_select(val, metric, higher, {c: i for i, c in enumerate(order)})
    r["params"] = params[r["chosen"]]
    r["n_configs"] = len(order)
    return r


def grid_table(fold_table: pd.DataFrame, chosen: dict, higher: bool) -> pd.DataFrame:
    """grid_results.csv: one row per configuration with per-fold train/validation, mean, SD, SE, rank, gap."""
    out = []
    for cid, g in fold_table.groupby("candidate_id", sort=False):
        g = g.sort_values("fold")
        row = {"candidate_id": cid, "family": g["family"].iloc[0], "params": g["params"].iloc[0]}
        for r in g.itertuples():
            row[f"train_fold_{r.fold}"] = r.train
            row[f"validation_fold_{r.fold}"] = r.validation
        tr, va = g["train"].to_numpy(), g["validation"].to_numpy()
        row.update({"train_mean": tr.mean(), "validation_mean": va.mean(), "validation_sd": va.std(ddof=1),
                    "validation_se": va.std(ddof=1) / np.sqrt(len(va)),
                    # gap > 0 means the configuration scores worse on validation than on its training folds
                    "train_validation_gap": (tr.mean() - va.mean()) if higher else (va.mean() - tr.mean())})
        out.append(row)
    t = pd.DataFrame(out)
    t["rank"] = t.groupby("family")["validation_mean"].rank(ascending=not higher, method="min").astype(int)
    t["chosen_in_family"] = t["candidate_id"].isin(set(chosen.values()))
    return t


# ---------------------------------------------------------------------------------------------
# Node runner (stages/s07_tuning/<task>/run.py calls run(task))
# ---------------------------------------------------------------------------------------------
def run(task: str) -> None:
    import os

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from . import cv, data, protocol
    from .metrics import PRIMARY, fold_summary, one_se_select, score
    from .outputs import Writer

    warnings.filterwarnings("ignore", message="Found unknown categories", category=UserWarning)
    w = Writer(STAGE, task)
    p = protocol.load()
    seed = int(p["seed"])
    metric, higher = PRIMARY[task]
    unit = " days" if task == "regression" else ""
    y_col = TARGET[task]
    cutoff = pd.Timestamp(protocol.get("data_dependent.test_cutoffs.values")[task])
    n_jobs = max(1, (os.cpu_count() or 2) - 1)

    recipes = json.loads(data.upstream("s04_features", task, "recipes.json", STAGE).read_text(encoding="utf-8"))
    s06_ml = pd.read_csv(data.upstream("s06_training", task, "metrics_long.csv", STAGE), keep_default_na=False)
    s06_counts = json.loads(data.upstream("s06_training", task, "counts.json", STAGE).read_text(encoding="utf-8"))
    d = data.load("records", task, "development", STAGE).reset_index(drop=True)
    plain = {c["family"]: c for c in candidate_specs(task, recipes, p["families"]["s06_settings"], seed)}
    cols = factory.feature_columns(plain["linear"]["spec"])
    X, y = d[cols], d[y_col].to_numpy()
    splits = cv.sklearn_splits(d["order_id"], task, STAGE)
    fold_list = list(cv.folds(task, STAGE))

    # Plain s06 validation fold scores (the reference of each family, G-55)
    s06_val = s06_ml[(s06_ml["phase"] == "validation") & (s06_ml["metric"] == metric)].copy()
    s06_val["value"] = pd.to_numeric(s06_val["value"])
    s06_scores = {fam: s06_val[s06_val["candidate_id"] == c["candidate_id"]].sort_values("fold")["value"].to_numpy()
                  for fam, c in plain.items()}

    # 7.1-7.5 Search every family ------------------------------------------------------------
    tables, fit_secs, conv, chosen, results = [], {}, {}, {}, {}
    for fam in TUNED:
        est, grid = family_grid(task, fam, p["grids"])
        spec = base_spec(task, fam, recipes, est, seed)
        ft, secs, wn = search(task, fam, spec, grid, X, y, splits, n_jobs)
        tables.append(ft)
        fit_secs.update(secs)
        conv.update(wn)
        r = best_in_family(ft, fam, metric, higher)
        results[fam] = {"spec": spec, "grid": grid, "best": r}
        chosen[fam] = r["chosen"]
    folds_long = pd.concat(tables, ignore_index=True)
    gt = grid_table(folds_long, chosen, higher)
    gt["convergence_warnings"] = gt["candidate_id"].map(conv)
    w.table("grid_results", gt, ids=("7.1" if task == "regression" else "7.2", "7.3", "7.4", "7.5", "7.6"))

    # Plain vs tuned (G-55), per family --------------------------------------------------------
    comp_rows, steps_plain = [], {}
    for fam in TUNED:
        tuned_id = chosen[fam]
        tv = folds_long[folds_long["candidate_id"] == tuned_id].sort_values("fold")["validation"].to_numpy()
        pid = plain[fam]["candidate_id"]
        long = pd.DataFrame([{"candidate_id": cid, "fold": k + 1, "metric": metric, "value": v}
                             for cid, vals in ((pid, s06_scores[fam]), (tuned_id, tv)) for k, v in enumerate(vals)])
        if tuned_id == pid:
            keep, band = pid, [np.nan, np.nan]
            pg = {"mean_gain": 0.0, "paired_se": 0.0, "folds_better": 0, "n_folds": len(tv)}
        else:
            r = one_se_select(long, metric, higher, {pid: 0, tuned_id: 1})
            keep, band = r["chosen"], r["band"]
            pg = paired_gain(long, pid, tuned_id, higher)
        steps_plain[fam] = keep
        best_id = results[fam]["best"]["best"]
        bv = folds_long[folds_long["candidate_id"] == best_id].sort_values("fold")["validation"].to_numpy()
        bl = pd.DataFrame([{"candidate_id": cid, "fold": k + 1, "metric": metric, "value": v}
                           for cid, vals in ((pid, s06_scores[fam]), (best_id, bv)) for k, v in enumerate(vals)])
        bg = paired_gain(bl, pid, best_id, higher) if best_id != pid else {"mean_gain": 0.0, "paired_se": 0.0, "folds_better": 0}
        comp_rows.append({"family": FAMILY_LABEL[fam], "plain_s06": pid, "tuned_best": tuned_id,
                          "plain_mean": s06_scores[fam].mean(), "tuned_mean": tv.mean(),
                          "tuned_se": tv.std(ddof=1) / np.sqrt(len(tv)), "paired_gain_of_tuned": pg["mean_gain"],
                          "paired_se": pg["paired_se"], "tuned_better_folds": pg["folds_better"],
                          "carried": "tuned" if keep == tuned_id and keep != pid else "plain",
                          "carried_candidate": keep,
                          # description only: the best-mean grid point against the plain model (not a decision)
                          "best_mean_candidate": best_id, "best_mean": bv.mean(),
                          "paired_gain_of_best_mean": bg["mean_gain"], "best_mean_paired_se": bg["paired_se"],
                          "best_mean_better_folds": bg["folds_better"]})
        w.decision(f"Keep the tuned {FAMILY_LABEL[fam]} over its plain s06 model?",
                   "one-SE rule on validation " + metric + ": the plain model stays unless the tuned one beats it by "
                   "more than one SE (G-55)", [pid, tuned_id], keep, ["grid_results.csv", "plain_vs_tuned.csv"],
                   ids=("7.5",), notes=f"band {band[0]:.4f} to {band[1]:.4f}; paired gain of the tuned model "
                                       f"{pg['mean_gain']:+.4f} (paired SE {pg['paired_se']:.4f}), better in "
                                       f"{pg['folds_better']} of {pg['n_folds']} folds (description only)")
    comp = pd.DataFrame(comp_rows)
    w.table("plain_vs_tuned", comp, ids=("7.5",))
    for fam in TUNED:
        w.decision(f"Best {FAMILY_LABEL[fam]} configuration in the grid",
                   f"one-SE rule inside the grid (s01 1.7): simplest within one SE of the best mean; simpler = "
                   "higher alpha, lower C, shallower depth, larger leaf, no class weight",
                   results[fam]["best"]["n_configs"], chosen[fam], ["grid_results.csv"], ids=("7.5",),
                   notes=f"best mean: {results[fam]['best']['best']}")

    # Ladder over the family winners (description only, s08 decides) ------------------------
    lad_long = [{"candidate_id": plain["dummy"]["candidate_id"], "fold": k + 1, "metric": metric, "value": v}
                for k, v in enumerate(s06_scores["dummy"])]
    for fam in TUNED:
        cid = steps_plain[fam]
        vals = s06_scores[fam] if cid == plain[fam]["candidate_id"] else \
            folds_long[folds_long["candidate_id"] == cid].sort_values("fold")["validation"].to_numpy()
        lad_long += [{"candidate_id": cid, "fold": k + 1, "metric": metric, "value": v} for k, v in enumerate(vals)]
    lad_long = pd.DataFrame(lad_long)
    order = [plain["dummy"]["candidate_id"]] + [steps_plain[f] for f in TUNED]
    lsteps = ladder(lad_long, metric, higher, order)
    fam_of = {plain["dummy"]["candidate_id"]: "dummy", **{steps_plain[f]: f for f in TUNED}}
    w.table("ladder_preview", pd.DataFrame([{
        "comparison": f"{FAMILY_LABEL[fam_of[s['complex']]]} vs {FAMILY_LABEL[fam_of[s['simpler']]]}",
        "simpler": s["simpler"], "complex": s["complex"], "mean_gain": s["paired"]["mean_gain"],
        "paired_se": s["paired"]["paired_se"], "folds_better": s["paired"]["folds_better"],
        "kept_by_one_se_rule": s["complex_kept"]} for s in lsteps]), ids=("7.5",))
    current = order[0]
    for s in lsteps:
        if s["complex_kept"]:
            current = s["complex"]
    lad_result = current

    # Out-of-fold predictions of each family's best (7.7), pooled vs mean-fold --------------
    pred_rows, oof_rows, refit_ok = [], [], []
    di = d.set_index("order_id", drop=False)
    for fam in TUNED:
        spec_b = dict(results[fam]["spec"], params=results[fam]["best"]["params"])
        cid = chosen[fam]
        g = folds_long[folds_long["candidate_id"] == cid].sort_values("fold")
        for (k, tr_ids, va_ids), grid_val in zip(fold_list, g["validation"]):
            model = single_threaded(factory.build(spec_b))
            Xtr, ytr = di.loc[tr_ids, cols], di.loc[tr_ids, y_col].to_numpy()
            Xva, yva = di.loc[va_ids, cols], di.loc[va_ids, y_col].to_numpy()
            model.fit(Xtr, ytr)
            pv = model.predict(Xva) if task == "regression" else model.predict_proba(Xva)[:, 1]
            s = score(task, yva, y_pred=pv) if task == "regression" else score(task, yva, proba=pv)
            refit_ok.append(abs(s[metric] - grid_val) < 1e-9)
            pred_rows.append(pd.DataFrame({"order_id": va_ids, "task": task, "population": "development", "fold": k,
                                           "candidate_id": cid, "y_true": yva, "y_pred": pv}))
        o = pd.concat([r for r in pred_rows if r["candidate_id"].iloc[0] == cid])
        pooled = score(task, o["y_true"], y_pred=o["y_pred"]) if task == "regression" else \
            score(task, o["y_true"], proba=o["y_pred"])
        oof_rows.append({"family": FAMILY_LABEL[fam], "candidate_id": cid, "mean_fold_" + metric: g["validation"].mean(),
                         "pooled_oof_" + metric: pooled[metric],
                         **({"pooled_oof_rmse": pooled["rmse"], "pooled_oof_r2": pooled["r2"]} if task == "regression" else
                            {"pooled_oof_roc_auc": pooled["roc_auc"], "pooled_oof_brier": pooled["brier"]})})
    preds = pd.concat(pred_rows, ignore_index=True)
    w.predictions(preds, ids=("7.7",))
    oof = pd.DataFrame(oof_rows)
    w.table("oof_scores", oof, ids=("7.7",))

    # candidates.csv --------------------------------------------------------------------------
    ctab = gt[["candidate_id", "family", "params", "validation_mean", "validation_se", "train_validation_gap", "rank"]].copy()
    ctab["description"] = ctab["family"].map(FAMILY_LABEL) + " grid configuration on the s04 recipe"
    ctab["kept"] = ctab["candidate_id"].isin([steps_plain[f] for f in TUNED])
    ctab["reason"] = [("best in family (one-SE) and carried: beats the plain s06 model by more than one SE" if r.candidate_id in steps_plain.values()
                       else "best in family (one-SE); the plain s06 model is carried (within one SE, G-55)" if r.candidate_id in chosen.values()
                       else "not the one-SE choice of its family grid") for r in ctab.itertuples()]
    w.candidates(ctab, ids=("7.5",))

    # Validation curves (7.6 / 7.7) -----------------------------------------------------------
    for fam in TUNED:
        g = gt[gt["family"] == fam].copy()
        prm = g["params"].map(json.loads)
        if fam == "linear":
            xkey = "alpha" if task == "regression" else "C"
            g["x"] = prm.map(lambda q: q[xkey])
            g["series"] = prm.map(lambda q: f"class_weight={q.get('class_weight')}" if task == "classification" else "")
        else:
            xkey = "max_depth"
            g["x"] = prm.map(lambda q: q["max_depth"])
            g["series"] = prm.map(lambda q: f"leaf={q['min_samples_leaf']}" + (f", cw={q.get('class_weight')}" if task == "classification" else ""))
        curve = g[["candidate_id", "series", "x", "train_mean", "validation_mean", "validation_se"]].sort_values(["series", "x"])
        w.curve(f"validation_curve_{fam}", curve, ids=("7.6",))
        fig, ax = plt.subplots(figsize=(8, 4.5))
        for sname, part in curve.groupby("series"):
            eb = ax.errorbar(part["x"], part["validation_mean"], yerr=part["validation_se"], marker="o", ms=3, capsize=2, label=f"val {sname}".strip())
            ax.plot(part["x"], part["train_mean"], ls="--", lw=0.8, alpha=0.6, color=eb[0].get_color())
        ax.axhline(s06_scores[fam].mean(), color="k", lw=0.8, ls=":", label="plain s06 (validation)")
        if fam == "linear":
            ax.set_xscale("log")
        ax.set(xlabel=xkey, ylabel=metric.upper() + unit, title=f"{task}: {FAMILY_LABEL[fam]} grid (solid validation ± SE, dashed training)")
        ax.legend(fontsize=6, ncol=2)
        fig.tight_layout()
        w.figure(f"validation_curve_{fam}", fig, curve, ids=("7.6",), title=f"Validation curve, {FAMILY_LABEL[fam]}")
        plt.close(fig)

    # Checks ------------------------------------------------------------------------------------
    used_grids = {f: family_grid(task, f, p["grids"])[1] for f in TUNED}
    n_cfg = {f: int((gt["family"] == f).sum()) for f in TUNED}
    w.check("every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output)",
            all(n_cfg[f] == len(configurations(used_grids[f])) for f in TUNED), ("7.1" if task == "regression" else "7.2", "7.3", "7.4"),
            "; ".join(f"{FAMILY_LABEL[f]} {n_cfg[f]} configurations" for f in TUNED))
    w.check("same folds as s06 (rows per fold equal)",
            [{"fold": k, "train_rows": len(t), "validation_rows": len(v)} for k, t, v in fold_list] == s06_counts["folds"], ("7.5",))
    every5 = folds_long.groupby("candidate_id")["fold"].nunique().eq(len(fold_list)).all()
    w.check("every configuration scored on all five folds, whole pipeline refitted per fold", bool(every5), ("7.5",))
    repro = []
    for fam in ("tree", "forest"):
        target = plain[fam]["spec"]["params"]
        hits = [cid for cid, q in zip(gt["candidate_id"], gt["params"].map(json.loads))
                if gt.loc[gt["candidate_id"] == cid, "family"].iloc[0] == fam
                and all(q.get(k) == v for k, v in target.items()) and q.get("class_weight") in (None,)]
        if hits:
            vals = folds_long[folds_long["candidate_id"] == hits[0]].sort_values("fold")["validation"].to_numpy()
            repro.append(np.allclose(vals, s06_scores[fam], rtol=0, atol=1e-9))
    w.check("the grid point with the s06 plain settings reproduces the s06 fold scores (tree, forest)",
            bool(repro) and all(repro), ("7.3", "7.4"), f"{sum(repro)} of {len(repro)} reproduced")
    w.check("refitting each family's best per fold gives the grid's validation scores", all(refit_ok), ("7.7",),
            f"{len(refit_ok)} refits")
    w.check("no test row read: every row used was purchased before the test cutoff", bool(d["purchase_ts"].max() < cutoff), ("7.5",),
            f"latest purchase {d['purchase_ts'].max()}, cutoff {cutoff}")

    # Evidence cards ----------------------------------------------------------------------------
    def fam_line(fam):
        b = results[fam]["best"]
        s = b["summary"].set_index("candidate_id")
        return (f"{FAMILY_LABEL[fam]}: {n_cfg[fam]} configurations; best mean {s.loc[b['best'], 'mean']:.4f}{unit} "
                f"({json.loads(gt.set_index('candidate_id').loc[b['best'], 'params'])}); one-SE choice "
                f"{json.dumps(b['params'], sort_keys=True)} with {s.loc[b['chosen'], 'mean']:.4f} ± {s.loc[b['chosen'], 'se']:.4f}{unit}")
    lin_id = "7.1" if task == "regression" else "7.2"
    for sid, fam in ((lin_id, "linear"), ("7.3", "tree"), ("7.4", "forest")):
        row = comp[comp["family"] == FAMILY_LABEL[fam]].iloc[0]
        w.explain(sid, done=fam_line(fam) + ".",
                  observation=f"Against the plain s06 model ({row.plain_mean:.4f}{unit}): paired gain of the tuned model "
                              f"{row.paired_gain_of_tuned:+.4f}{unit} (paired SE {row.paired_se:.4f}), better in "
                              f"{int(row.tuned_better_folds)} of 5 folds; carried: {row.carried} model. For description only, the "
                              f"best-mean grid point against the plain model: paired gain {row.paired_gain_of_best_mean:+.4f}{unit} "
                              f"(paired SE {row.best_mean_paired_se:.4f}), better in {int(row.best_mean_better_folds)} of 5 folds.",
                  reasoning="The tuned configuration replaces the plain s06 model only if it beats it by more than one "
                            "standard error of the fold means (G-55); otherwise the simpler plain model stays.")
    w.explain("7.5", done=f"GridSearchCV over the whole s04 pipeline on the s05 folds, scoring {SCORING[task]}, refit=False, "
              f"return_train_score=True, seed {seed}; {len(gt)} configurations in total. Carried per family: "
              + "; ".join(f"{FAMILY_LABEL[f]} {'tuned' if steps_plain[f] != plain[f]['candidate_id'] else 'plain s06'}" for f in TUNED)
              + ". Ladder over the carried families (description only; s08 decides): "
              + "; ".join(f"{FAMILY_LABEL[fam_of[s['complex']]]} {'kept' if s['complex_kept'] else 'not kept'} over "
                          f"{FAMILY_LABEL[fam_of[s['simpler']]]} (paired gain {s['paired']['mean_gain']:+.4f}{unit}, "
                          f"better in {s['paired']['folds_better']} of 5 folds)" for s in lsteps)
              + f"; result {FAMILY_LABEL[fam_of[lad_result]]}.",
              conclusion="Selection scores on the folds, not generalisation estimates (G-10). The finalists and the final "
                         "choice are made in s08 at its gate (G-39).")
    gaps = gt[gt["chosen_in_family"]].set_index("family")["train_validation_gap"]
    w.explain("7.6", done="train_validation_gap for every configuration in grid_results.csv (positive = worse on "
              "validation). Gap of each family's one-SE choice: " + "; ".join(f"{FAMILY_LABEL[f]} {gaps[f]:+.4f}{unit}" for f in TUNED) + ".",
              reasoning="The one-SE choice is already the simplest configuration within the rule, so no simpler "
                        "configuration within the rule exists to flag; the gaps are reported for the review.")
    w.explain("7.7", done="grid_results.csv, plain_vs_tuned.csv, ladder_preview.csv, candidates.csv, decision.json, "
              "out-of-fold predictions of each family's best (predictions.csv.gz) with pooled vs mean-fold scores "
              "(oof_scores.csv), validation curves (curves/, figures/); fit times in _manifest.json.")
    w.json("counts", {"task": task, "configurations": n_cfg, "chosen_in_family": chosen, "carried": steps_plain,
                      "ladder_result": lad_result, "primary_metric": metric, "seed": seed}, ids=("7.5", "7.7"))
    w.finish(seed=seed, extra={"fit_seconds": fit_secs})
    if w.index["checks_failed"]:
        raise SystemExit(f"s07 {task}: checks failed: {w.index['checks_failed']}")
