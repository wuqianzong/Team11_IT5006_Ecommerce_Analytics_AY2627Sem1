"""s04 feature definition shared by both task nodes (blueprint spec/blueprints/s04_features.md).

Nothing here fits a model or saves a fitted object. The pool comes only from
contract.pool(task); the threshold and collinearity drops only from spec/human_decisions.yaml.

- pool_ranking: the s03 ranking restricted to the pool, shares re-normalised (4.4, CR-042)
- transforms: log1p decision from pre-cutoff skewness (4.2, G-47, G-62, G-70)
- reduction: constant and duplicate columns dropped, team collinearity drops applied (4.3, G-26)
- selection: walk the core ranking to the cumulative threshold (4.4, G-19)
- recipes / factory_spec: the pipeline recipe per model family (4.8, G-27)
- design_matrix: rank and condition number of the encoded matrix per recipe (4.3)
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import yaml

from . import contract, eda, factory
from .paths import spec_path

SKEW_TRIGGER = 1.0  # protocol features.log1p.skewness_threshold (checked against protocol in run.py)
ROUTE_KEYS = (("customer_state", "primary_seller_state"), ("customer_state",))

# Hypothesised signal per pool feature (claim type: hypothesis, tested only by the models in s06-s08).
SIGNAL = {
    "n_items": "more items mean more picking and packing and more chances that one item is late or wrong",
    "n_products": "distinct products widen the chance of a stock or quality problem",
    "n_sellers": "several sellers ship separate parcels, so the order is complete only when the slowest one arrives",
    "n_categories": "mixed baskets combine items with different handling",
    "total_price": "expensive orders raise expectations and may get different handling",
    "total_freight": "freight reflects distance, weight and carrier service level",
    "freight_ratio": "a freight cost high relative to the price may disappoint the customer",
    "total_weight_g": "heavy parcels travel by slower freight services",
    "total_volume_cm3": "bulky parcels travel by slower freight services",
    "weight_missing_fraction": "missing catalogue dimensions mark less complete listings",
    "volume_missing_fraction": "missing catalogue dimensions mark less complete listings",
    "primary_category": "categories differ in handling, seller mix and customer expectations",
    "category_missing_fraction": "a missing category marks less complete listings",
    "customer_state": "destination region drives the transport route and its reliability",
    "primary_seller_state": "origin region drives the transport route and its reliability",
    "distance_km_max": "longer customer-seller distance means longer transit",
    "distance_missing_fraction": "a missing location marks unusual or incomplete addresses",
    "interstate_share": "interstate legs add hand-overs and tax checkpoints",
    "purchase_month": "seasonal peaks (e.g. year-end) load the logistics network",
    "purchase_dayofweek": "orders placed before a weekend wait longer for dispatch",
    "purchase_hour": "late orders miss the same-day dispatch cut-off",
    "primary_payment_type": "boleto payments clear later than cards, delaying dispatch",
    "payment_installments_max": "instalments relate to order value and buyer profile",
    "n_payment_methods": "split payments are rare and may mark unusual orders",
    "product_photos_qty": "listings with more photos set clearer expectations",
    "product_description_lenght": "longer descriptions set clearer expectations",
    "seller_prior_review_mean": "the seller rating shown at checkout summarises the seller's past service",
}

# Sources checked in Experiment 5 (s04 round 3, 2026-10-20) against the publisher record and abstract
# (RePEc / Crossref); the full texts were not accessible, so each claim is limited to what the abstract states.
# Nothing is carried from earlier experiments.
REFERENCES = {
    "deshpande2023": "Deshpande, V. & Pendem, P. K. (2023). Logistics Performance, Ratings, and Its Impact on Customer "
                     "Purchasing Behavior and Sales in E-Commerce Platforms. Manufacturing & Service Operations "
                     "Management 25(3):827-845. doi:10.1287/msom.2021.1045",
    "leite2024": "Leite, G. A. de A., Pinochet, L. H. C., Pardim, V. I. & Onusic, L. M. (2024). Uso de Machine Learning "
                 "para entendimento das relações de consumo no modelo de negócio (SaaS enabled Marketplace) do Olist. "
                 "Revista Tecnologia e Sociedade 20(60):328. doi:10.3895/rts.v20n60.16920",
}
# What each source supports (abstract level): longer delivery and delivery past the promise lower customers'
# ratings (Tmall, 15M orders; deshpande2023); on Olist, the gap between promised and actual delivery is the most
# important factor for the review score (leite2024). So features that make delivery longer or harder are
# literature-supported hypotheses for is_detractor. Neither source tests the regression features.
_DELIVERY_PROXIES = ("distance_km_max", "interstate_share", "customer_state", "primary_seller_state", "total_freight",
                     "freight_ratio", "total_weight_g", "total_volume_cm3", "n_sellers")
VERIFIED_ON = "2026-10-20"


def references(feature: str, task: str) -> list[str]:
    """Verified sources for a feature's hypothesised signal (classification delivery proxies only)."""
    if task == "classification" and feature in _DELIVERY_PROXIES:
        return ["deshpande2023", "leite2024"]
    return []


def decisions(task: str) -> dict:
    """The task's s03 gate decisions; raises if the team has not recorded them (G-31)."""
    hd = yaml.safe_load(spec_path("human_decisions.yaml").read_text(encoding="utf-8"))
    d = (hd.get("s03_to_s04") or {}).get(task) or {}
    thr = d.get("cumulative_importance_threshold")
    if thr not in (0.95, 0.99):
        raise RuntimeError(f"human_decisions.yaml s03_to_s04.{task}.cumulative_importance_threshold is not 0.95 or 0.99")
    if d.get("collinearity_drops") is None:
        raise RuntimeError(f"human_decisions.yaml s03_to_s04.{task}.collinearity_drops is missing")
    return {"threshold": float(thr), "collinearity_drops": list(d["collinearity_drops"])}


def pool_ranking(task: str, ranking: pd.DataFrame) -> pd.DataFrame:
    """Restrict an s03 ranking (feature, value) to contract.pool(task) and re-normalise (4.4)."""
    pool = contract.pool(task)
    r = ranking[ranking["feature"].isin(pool)][["feature", "value"]]
    out = eda.cumulative_ranking(dict(zip(r["feature"], r["value"])), "")
    adopted = set(contract.adopted(task))
    out.insert(2, "source", ["adopted candidate (G-70)" if f in adopted else "contract predictor" for f in out["feature"]])
    return out.drop(columns=[c for c in ("measure",) if c in out.columns])


def kind(feature: str) -> str:
    return "categorical" if feature in contract.CATEGORICAL else "numeric"


def log_candidates(task: str) -> tuple[str, ...]:
    extra = ("product_description_lenght",) if "product_description_lenght" in contract.pool(task) else ()
    return tuple(contract.LOG_CANDIDATES) + extra


def transforms(d: pd.DataFrame, task: str, trigger: float = SKEW_TRIGGER) -> pd.DataFrame:
    """log1p decision per pool feature from pre-cutoff skewness (4.2)."""
    rows = []
    cands = set(log_candidates(task))
    for f in contract.pool(task):
        if kind(f) == "categorical":
            rows.append({"feature": f, "log_candidate": False, "skewness": np.nan, "log1p": False,
                         "rule": "categorical: one-hot, never logged"})
            continue
        sk = float(eda.profile(d[f])["skewness"])  # same estimator as s03 (bias-corrected)
        if f in cands:
            rows.append({"feature": f, "log_candidate": True, "skewness": sk, "log1p": sk > trigger,
                         "rule": f"log1p because pre-cutoff skewness {sk:.2f} > {trigger:g}" if sk > trigger
                         else f"not logged: skewness {sk:.2f} <= {trigger:g}"})
        else:
            rows.append({"feature": f, "log_candidate": False, "skewness": sk, "log1p": False,
                         "rule": _never_logged_reason(f)})
    return pd.DataFrame(rows)


def _never_logged_reason(f: str) -> str:
    if f == "freight_ratio":
        return "never logged: team decision in the s01 review (G-62)"
    if f in contract.COUNTS or f == "product_photos_qty":
        return "never logged: integer count (G-62, G-70)"
    if f in contract.CALENDAR_NUMERIC:
        return "never logged: numeric calendar position (G-22, G-47)"
    if f in contract.SHARES:
        return "never logged: bounded 0-1 share (G-47)"
    if f == "seller_prior_review_mean":
        return "never logged: 1-5 rating (G-70)"
    return "never logged: not a log1p candidate (G-62)"


def reduction(d: pd.DataFrame, task: str, ranking: pd.DataFrame, team_drops: list, collinear: pd.DataFrame,
              date: str) -> tuple[list[str], pd.DataFrame]:
    """Core set = pool minus constant columns, duplicates and team collinearity drops (4.3, G-26).

    Of an identical pair the lower-ranked feature is dropped (ties: the later one in the pool order).
    Returns (core features in pool order, reduction_rationale rows).
    """
    pool = list(contract.pool(task))
    rank_of = dict(zip(ranking["feature"], ranking["rank"]))
    rows, dropped = [], set()
    for f in pool:
        if d[f].nunique(dropna=True) <= 1:
            rows.append({"feature": f, "flagged_by": "constant", "paired_with": "", "team_decision": "drop (automatic)",
                         "rationale": "one value on pre-cutoff orders", "decided_by": "rule s04 4.3", "date": date})
            dropped.add(f)
    for i, a in enumerate(pool):
        for b in pool[i + 1:]:
            if a in dropped or b in dropped or kind(a) != kind(b):
                continue
            if d[a].equals(d[b]):
                drop, keep = (b, a) if rank_of.get(a, 1e9) <= rank_of.get(b, 1e9) else (a, b)
                rows.append({"feature": drop, "flagged_by": "duplicate", "paired_with": keep,
                             "team_decision": "drop (automatic)",
                             "rationale": f"identical to {keep} on every pre-cutoff order; {keep} ranks higher "
                                          f"({rank_of.get(keep)} vs {rank_of.get(drop)})", "decided_by": "rule s04 4.3",
                             "date": date})
                dropped.add(drop)
    for g in team_drops:
        rows.append({"feature": g["drop"], "flagged_by": "|r| > 0.9 or VIF > 10", "paired_with": ", ".join(
            x for x in g["group"] if x != g["drop"]), "team_decision": "drop", "rationale": g["rationale"],
            "decided_by": g["decided_by"], "date": str(g["date"])})
        dropped.add(g["drop"])
    flagged = collinear[~collinear["identical"].astype(bool)] if len(collinear) else collinear
    for r in flagged.itertuples():
        if r.feature_a in pool and r.feature_b in pool and not ({r.feature_a, r.feature_b} & dropped):
            rows.append({"feature": f"{r.feature_a} / {r.feature_b}", "flagged_by": "|r| > 0.9 or VIF > 10",
                         "paired_with": "", "team_decision": "keep both", "rationale": "no drop recorded by the team",
                         "decided_by": "human_decisions.yaml", "date": date})
    cols = ["feature", "flagged_by", "paired_with", "team_decision", "rationale", "decided_by", "date"]
    return [f for f in pool if f not in dropped], pd.DataFrame(rows, columns=cols)


def selection(ranking: pd.DataFrame, core: list[str], threshold: float) -> tuple[pd.DataFrame, list[str]]:
    """Re-normalise the pool ranking over the core set and keep features up to the threshold (4.4)."""
    r = ranking[ranking["feature"].isin(core)]
    out = eda.cumulative_ranking(dict(zip(r["feature"], r["value"])), "")
    out = out.drop(columns=[c for c in ("measure",) if c in out.columns])
    k = eda.cut_point(out, threshold)
    out["selected"] = [i < k for i in range(len(out))]
    return out, list(out["feature"].head(k))


FAMILIES = {
    "regression": {"dummy": "dummy_median", "linear": "linear", "tree": "tree_reg", "forest": "forest_reg"},
    "classification": {"dummy": "dummy_prior", "linear": "logistic", "tree": "tree_clf", "forest": "forest_clf"},
}


def factory_spec(task: str, selected: list[str], logged: list[str], estimator: str) -> dict:
    """The e5lib.factory spec for one family; route median only when distance_km_max is selected (G-27)."""
    spec = {"task": task, "estimator": estimator,
            "numeric": [f for f in selected if kind(f) == "numeric"],
            "categorical": [f for f in selected if kind(f) == "categorical"],
            "log_inputs": [f for f in selected if f in logged]}
    if "distance_km_max" in selected:
        spec["route_median"] = {"column": "distance_km_max", "keys": [list(k) for k in ROUTE_KEYS]}
    spec["drop_duplicates"] = True  # identical encoded columns (e.g. co-missing indicators) dropped in the fold (4.3)
    if task == "regression":
        spec["log_target"] = True
    return spec


def recipes(task: str, selected: list[str], logged: list[str]) -> dict:
    out = {}
    for fam, est in FAMILIES[task].items():
        spec = factory_spec(task, selected, logged, est)
        linear = est in factory.LINEAR
        out[fam] = {
            "estimator": est, "spec": spec,
            "numeric": "log1p (columns in log_inputs) then median imputation with a missing indicator per column "
                       "that has missing values in the training fold" + ("; StandardScaler" if linear else ""),
            "route_median": ("distance_km_max: missing values filled with the median of customer_state x "
                             "primary_seller_state, else customer_state, else the global median, learned in the "
                             "training fold, plus distance_km_max_missing (G-27)") if "route_median" in spec else None,
            "categorical": "missing -> 'Unknown'; one-hot, handle_unknown='ignore'" + (", drop='first'" if linear else ""),
            "duplicates": "encoded columns identical to an earlier column in the training fold are dropped (4.3 rule; "
                          "e.g. the missing indicators of fields that are always missing together)",
            "scaling": "StandardScaler" if linear else "none",
            "target": "log1p(lead_days), predictions expm1, scored in days (G-36)" if task == "regression" else "is_detractor (0/1)",
            "fitted": "inside each training fold in s06-s08, never in s04",
        }
    return out


def design_matrix(d: pd.DataFrame, spec: dict) -> dict:
    """Rank and condition number of the encoded design matrix for one recipe, on pre-cutoff rows (4.3).

    The preprocessing is fitted here only to measure the matrix; nothing is saved.
    """
    s = dict(spec)
    s.pop("log_target", None)
    model = factory.build(s)
    pre = model.steps[:-1]
    from sklearn.pipeline import Pipeline
    before = Pipeline([st for st in pre if st[0] != "dedupe"]).fit_transform(d[factory.feature_columns(s)])
    pipe = Pipeline(pre)
    X = np.asarray(pipe.fit_transform(d[factory.feature_columns(s)]), dtype=float)
    dropped = []
    if "dedupe" in pipe.named_steps:
        cols = pipe.named_steps["prep"].get_feature_names_out()
        dropped = [str(cols[j]) for j in pipe.named_steps["dedupe"].dropped_]
    sv = np.linalg.svd(X, compute_uv=False)
    rank = int(np.sum(sv > sv.max() * max(X.shape) * np.finfo(float).eps))
    cond = float(sv.max() / sv.min()) if sv.min() > 0 else float("inf")
    return {"rows": int(X.shape[0]), "encoded_columns": int(np.asarray(before).shape[1]),
            "duplicates_dropped": "; ".join(dropped) or "none", "columns": int(X.shape[1]), "rank": rank,
            "full_rank": rank == X.shape[1], "condition_number": cond}


# ---------------------------------------------------------------------------------------------
# Node runner (stages/s04_features/<task>/run.py calls run(task))
# ---------------------------------------------------------------------------------------------
STAGE = "s04_features"


def _set_task_section(section: str, task: str, value) -> None:
    from . import protocol
    protocol.set_task_entry(section, task, value, STAGE)


def run(task: str) -> None:
    import json
    from datetime import date

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from . import data, protocol
    from .outputs import Writer

    w = Writer(STAGE, task)
    p = protocol.load()
    seed = int(p["seed"])
    today = date.today().isoformat()
    dec = decisions(task)  # stops here when the team has not decided (G-31)
    trigger = float(p["features"]["log1p"]["skewness_threshold"])
    cutoff = pd.Timestamp(protocol.get("data_dependent.test_cutoffs.values")[task])
    d = data.load("records", task, "development", STAGE)
    pool = list(contract.pool(task))
    adopted = set(contract.adopted(task))

    # 4.1 Baseline ------------------------------------------------------------------------------
    base = pd.DataFrame([{"feature": f, "source": "adopted candidate (G-70)" if f in adopted else "contract predictor",
                          "kind": kind(f), "calendar_numeric": f in contract.CALENDAR_NUMERIC} for f in pool])
    w.table("baseline_pool", base, ids=("4.1",))

    # Pool ranking from s03 (4.4 input) -----------------------------------------------------------
    src = "importance_ranking.csv" if task == "regression" else "candidate_ranking_extended.csv"
    s03 = pd.read_csv(data.upstream("s03_eda", task, src, STAGE))
    measure = str(s03["measure"].iloc[0])
    pr = pool_ranking(task, s03)

    # 4.2 Transforms ------------------------------------------------------------------------------
    tr = transforms(d, task, trigger)
    logged = list(tr.loc[tr["log1p"], "feature"])
    w.table("transforms", tr, ids=("4.2",))

    # 4.3 Reduction -------------------------------------------------------------------------------
    collinear = pd.read_csv(data.upstream("s03_eda", task, "collinear_pairs.csv", STAGE))
    core, red = reduction(d, task, pr, dec["collinearity_drops"], collinear, today)
    w.table("reduction_rationale", red, ids=("4.3",))

    # 4.4 Selection -------------------------------------------------------------------------------
    sel_rank, selected = selection(pr, core, dec["threshold"])
    w.table("selection_ranking", sel_rank, ids=("4.4",))
    fig, ax = plt.subplots(figsize=(10, 5))
    xs = np.arange(1, len(sel_rank) + 1)
    colors = ["tab:blue" if s else "0.7" for s in sel_rank["selected"]]
    ax.bar(xs, sel_rank["share"], color=colors)
    ax2 = ax.twinx()
    ax2.plot(xs, sel_rank["cumulative_share"], color="black", marker="o", ms=3)
    ax2.axhline(dec["threshold"], color="tab:red", ls="--", lw=1)
    ax2.set_ylim(0, 1.02)
    ax.set_xticks(xs)
    ax.set_xticklabels(sel_rank["feature"], rotation=75, ha="right", fontsize=8)
    ax.set_ylabel(f"share of total {measure}")
    ax2.set_ylabel("cumulative share")
    ax.set_title(f"{task}: core set ranking; {len(selected)} of {len(sel_rank)} kept at {dec['threshold']:.0%} (blue)")
    fig.tight_layout()
    w.figure("selection_cumulative", fig, sel_rank, ids=("4.4",), title="Cumulative share and selected features")
    plt.close(fig)
    _set_task_section("core_set", task, core)
    _set_task_section("selected_set", task, {"threshold": dec["threshold"], "features": selected})

    # 4.8 Recipes and design-matrix diagnostics ------------------------------------------------------
    rec = recipes(task, selected, logged)
    w.json("recipes", rec, ids=("4.8",))
    dm = []
    for fam in ("linear", "tree"):
        r = design_matrix(d, rec[fam]["spec"])
        dm.append({"family": fam, "estimator": rec[fam]["estimator"], **r})
    dm = pd.DataFrame(dm)
    w.table("design_matrix", dm, ids=("4.3", "4.8"))

    # 4.6 Rationale: feature dictionary -------------------------------------------------------------
    dd = pd.read_csv(data.upstream("s02_data", "common", "data_dictionary.csv", STAGE))
    dd = dd[dd["table"] == "records"].set_index("column")
    rank_of = sel_rank.set_index("feature")
    pr_of = pr.set_index("feature")
    red_of = {r.feature: r for r in red.itertuples()}
    tr_of = tr.set_index("feature")
    rows = []
    for f in pool:
        miss = float(d[f].isna().mean())
        if f in selected:
            reason = (f"selected: rank {int(rank_of.loc[f, 'rank'])} of {len(sel_rank)} in the core ranking, "
                      f"cumulative share {rank_of.loc[f, 'cumulative_share']:.4f} reached within {dec['threshold']:.0%}")
        elif f in red_of:
            reason = f"dropped in reduction (4.3): {red_of[f].flagged_by}, {red_of[f].rationale}"
        else:
            reason = (f"not selected: rank {int(rank_of.loc[f, 'rank'])} of {len(sel_rank)}, after the "
                      f"{dec['threshold']:.0%} cut")
        if f == "distance_km_max":
            imput = "route median (customer_state x primary_seller_state, then customer_state, then global) + distance_km_max_missing (G-27)"
        elif kind(f) == "categorical":
            imput = "missing -> 'Unknown' level"
        else:
            imput = "median + missing indicator" if miss > 0 else "median (no missing value on pre-cutoff orders)"
        refs = references(f, task)
        rows.append({"feature": f, "task": task, "source": "adopted candidate (G-70)" if f in adopted else "contract predictor (G-61)",
                     "kind": kind(f), "formula": dd.loc[f, "source"], "grain": dd.loc[f, "grain"],
                     "known_at_checkout": dd.loc[f, "known_at_checkout"], "missing_share": miss,
                     "missing_meaning": dd.loc[f, "missing_meaning"], "transform": tr_of.loc[f, "rule"],
                     "imputation": imput,
                     "encoding": "one-hot (drop-first for linear/logistic), unknown level ignored" if kind(f) == "categorical"
                                 else ("scaled for linear/logistic only"),
                     "pool_rank": int(pr_of.loc[f, "rank"]), "pool_share": float(pr_of.loc[f, "share"]),
                     "kept": f in selected, "reason": reason, "hypothesised_signal": SIGNAL[f],
                     "claim_type": "literature-supported hypothesis" if refs else "unmeasured mechanism",
                     "references": "; ".join(REFERENCES[k] for k in refs),
                     "citation_status": (f"checked {VERIFIED_ON} against the publisher record and abstract; supports: "
                                         "longer or late delivery lowers customer ratings" if refs else
                                         "none: no verified source; the signal is an unmeasured mechanism")})
    for f in selected:
        if kind(f) == "numeric" and d[f].isna().any():
            name = f"{f}_missing" if f == "distance_km_max" else f"missingindicator_{f}"
            rows.append({"feature": name, "task": task, "source": f"derived from {f} in the fold pipeline", "kind": "numeric (0/1)",
                         "formula": f"1 if {f} is missing, else 0", "grain": "order", "known_at_checkout": "yes",
                         "missing_share": 0.0, "missing_meaning": "never missing", "transform": "never logged: 0/1 indicator (G-47)",
                         "imputation": "none", "encoding": "scaled for linear/logistic only", "pool_rank": np.nan,
                         "pool_share": np.nan, "kept": True,
                         "reason": f"kept with its parent {f} ({d[f].isna().mean():.2%} missing on pre-cutoff orders); not ranked",
                         "hypothesised_signal": "a missing value carries its own meaning (e.g. a seller without an earlier review)"
                                                if f == "seller_prior_review_mean" else "a missing value carries its own meaning",
                         "claim_type": "unmeasured mechanism", "references": "", "citation_status": "none"})
    fd = pd.DataFrame(rows)
    w.table("feature_dictionary", fd, ids=("4.6",))

    # 4.7 Selected set ----------------------------------------------------------------------------------
    sel = {"task": task, "threshold": dec["threshold"], "ranking_measure": measure, "pool": pool, "core": core,
           "selected": selected, "numeric": rec["linear"]["spec"]["numeric"],
           "categorical": rec["linear"]["spec"]["categorical"], "log_inputs": rec["linear"]["spec"]["log_inputs"],
           "route_median": rec["linear"]["spec"].get("route_median"),
           "derived_indicators": [r for r in fd.loc[fd["source"].str.startswith("derived"), "feature"]],
           "log_target": task == "regression", "families": list(FAMILIES[task]),
           "pool_source": "e5lib.contract.pool(task)", "decisions": "spec/human_decisions.yaml s03_to_s04 (G-70)"}
    w.json("selected_features", sel, ids=("4.7",))
    w.decision("selected feature set", f"walk the core ranking ({measure}) to the cumulative threshold",
               f"{len(core)} core features", selected,
               ["selection_ranking.csv", "reduction_rationale.csv", "selected_features.json"], ids=("4.4", "4.7"),
               notes=f"threshold {dec['threshold']} from human_decisions.yaml")

    # Checks (blueprint section 6, gate) -----------------------------------------------------------------
    w.check("every computation reads only pre-cutoff rows", bool(d["purchase_ts"].max() < cutoff), ids=("4.2", "4.3", "4.4"),
            detail=f"latest purchase {d['purchase_ts'].max()}, cutoff {cutoff}; {len(d):,} rows")
    w.check("ranked feature set equals contract.pool(task) and shares sum to 1",
            set(pr["feature"]) == set(pool) and abs(pr["share"].sum() - 1) < 1e-9, ids=("4.4",),
            detail=f"{len(pr)} features, measure: {measure}")
    w.check("threshold and collinearity drops read from human_decisions.yaml", True, ids=("4.3", "4.4"),
            detail=f"threshold {dec['threshold']}; team drops {len(dec['collinearity_drops'])}")
    w.check("every collinearity drop has a row in reduction_rationale.csv",
            all(g["drop"] in set(red["feature"]) for g in dec["collinearity_drops"]), ids=("4.3",))
    w.check("selected set and threshold recorded in protocol.yaml (data_dependent.selected_set)",
            protocol.get("data_dependent.selected_set.values").get(task) == {"threshold": dec["threshold"], "features": selected},
            ids=("4.7",))
    w.check("log1p only for the log1p candidates with skewness above the trigger",
            set(logged) <= set(log_candidates(task)) and all(tr_of.loc[f, "skewness"] > trigger for f in logged), ids=("4.2",),
            detail=", ".join(f"{r.feature} {r.skewness:.2f}" for r in tr[tr["log_candidate"]].itertuples()))
    w.check("feature_dictionary covers every pool feature and every selected feature has a rationale",
            set(pool) <= set(fd["feature"]) and fd.loc[fd["kept"], "hypothesised_signal"].astype(bool).all(), ids=("4.6",))
    w.check("order_estimated_delivery_date and est_delivery_days are not features (G-35)",
            not {"order_estimated_delivery_date", "est_delivery_days"} & set(pool), ids=("4.1", "4.7"))
    w.check("no target cap and no target among the features (G-25)",
            not {"lead_days", "is_detractor"} & set(pool), ids=("4.2",))
    fitted = [x.name for x in w.dir.rglob("*") if x.suffix in {".pkl", ".joblib", ".pickle"}]
    lin = dm[dm["family"] == "linear"].iloc[0]
    w.check("linear/logistic design matrix has full column rank after the duplicate rule", bool(lin["full_rank"]),
            ids=("4.3", "4.8"), detail=f"rank {lin['rank']} of {lin['columns']}; tree recipe (full one-hot, no scaling) "
            "is rank-deficient by design: each categorical's dummies sum to 1, which does not affect trees")
    w.check("no fitted object saved in the outputs", not fitted, ids=("4.8",), detail=", ".join(fitted) or "none")
    w.check("every family recipe builds an estimator from e5lib.factory", all(
        factory.build(rec[f]["spec"]) is not None for f in rec), ids=("4.8",))

    # Evidence cards ------------------------------------------------------------------------------------
    n_ad = len(adopted)
    w.explain("4.1", done=f"Pool from e5lib.contract.pool('{task}'): {len(pool)} features = 24 contract predictors"
              + (f" + {n_ad} adopted at the s03 gate ({', '.join(sorted(adopted))})" if n_ad else "")
              + f"; {sum(kind(f) == 'categorical' for f in pool)} categorical, calendar fields numeric (G-22).",
              conclusion="has_items, freight_ratio_missing, payment_missing and order_estimated_delivery_date are not in the pool.")
    w.explain("4.2", done=f"log1p for {len(logged)} of {len(log_candidates(task))} candidates by pre-cutoff skewness > {trigger:g}: "
              + "; ".join(f"{r.feature} {r.skewness:.2f}" for r in tr[tr['log_candidate']].itertuples())
              + (". Regression target log1p(lead_days), scored in days (G-36); no target cap (G-25)." if task == "regression" else "."),
              reasoning="Missing values stay missing through log1p and are imputed afterwards inside the fold pipeline (G-47).")
    w.explain("4.3", done=f"Core set {len(core)} of {len(pool)}: "
              + ("; ".join(f"{r.feature} dropped ({r.flagged_by}{', kept ' + r.paired_with if r.paired_with else ''})"
                           for r in red.itertuples()) or "nothing dropped")
              + f". Team collinearity drops: {len(dec['collinearity_drops'])} (none flagged in s03). Encoded design matrix: "
              + "; ".join(f"{r.family}: {r.encoded_columns} encoded columns, duplicates dropped [{r.duplicates_dropped}], "
                        f"{r.columns} columns, rank {r.rank}, condition number {r.condition_number:.3g}" for r in dm.itertuples())
              + ".", reasoning="Rank and condition number are measured once on pre-cutoff rows; the preprocessing fitted for "
                               "this measurement is not saved. Fields that are always missing together give identical "
                               "missing indicators, so the 4.3 duplicate rule is applied to the encoded columns inside "
                               "each training fold (factory step 'dedupe'); the linear/logistic matrix is then full rank. "
                               "The tree recipe keeps every one-hot level, so its matrix is rank-deficient by design, "
                               "which does not affect trees.")
    w.explain("4.4", done=f"Core ranking by {measure}, re-normalised over the {len(core)} core features; "
              f"{len(selected)} kept at the {dec['threshold']:.0%} threshold. Dropped by the cut: "
              f"{', '.join(sel_rank.loc[~sel_rank['selected'], 'feature']) or 'none'}.",
              reasoning="Declared exception (G-19): the ranking is computed once on pre-cutoff orders, so CV scores of the "
                        "chosen set are optimistic; the report says so.")
    n_ref = int(fd["references"].astype(bool).sum())
    n_kept = int(fd["kept"].sum())
    n_kept_ref = int((fd["kept"] & fd["references"].astype(bool)).sum())
    w.explain("4.6", done=f"feature_dictionary.csv: {len(fd)} rows (every pool feature and the derived missing indicators): "
              "formula, grain, checkout availability, missingness, transform, imputation, kept and reason, hypothesised "
              f"signal and claim type; {n_ref} rows cite a source checked in Experiment 5 ({n_kept_ref} of {n_kept} kept).",
              reasoning="Sources were re-checked in this experiment (round 3, Henry's comment): Deshpande & Pendem (2023) and "
                        "Leite et al. (2024) support, at abstract level, that longer or late delivery lowers customer "
                        "ratings, so the classification delivery proxies are literature-supported hypotheses. Cui et al. "
                        "(2024) studies the promised delivery speed and does not support a location or distance feature, "
                        "so it is not cited. Every other signal is an unmeasured mechanism, tested only by the models.",
              label="literature-supported hypothesis" if n_ref else "unmeasured mechanism")
    if n_kept_ref < n_kept:
        w.deviation("4.6", f"Verified citation for {n_kept_ref} of {n_kept} kept features only; the blueprint asks for one per "
                    "kept feature. The others are stated as unmeasured mechanisms (no source from earlier experiments).")
    w.explain("4.7", done=f"selected_features.json: {len(selected)} features ({len(sel['numeric'])} numeric, "
              f"{len(sel['categorical'])} categorical), {len(sel['derived_indicators'])} derived missing indicators, "
              f"log1p inputs {sel['log_inputs']}; one set used by every family (G-49).")
    w.explain("4.8", done="recipes.json: one e5lib.factory spec per family (" + ", ".join(
              f"{k} = {v['estimator']}" for k, v in rec.items()) + "): log1p, median imputation with missing indicators, "
              "route median for distance_km_max, one-hot with unknown levels ignored (drop-first and StandardScaler for "
              "linear/logistic only).", conclusion="Fitted only inside each training fold in s06-s08 (G-27).")
    w.finish(seed=seed)
