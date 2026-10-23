"""B4: features for Pipeline B (blueprint pipeline_b/spec/blueprints/b04_features.md;
CR-054 B-C11, B-C12; G-79).

A's method, read-only from e5lib: the s03 importance measures (regression |Spearman| for numeric
features and the rank correlation ratio for categorical ones; classification mutual information),
the cumulative ranking and cut point, the 4.2 skewness rule, the factory and the design-matrix
diagnostics. B adds its candidates, B's feature kinds (route is categorical) and the B dictionary.

Evidence IDs: B4.1 pool, B4.2 ranking, B4.3 selection, B4.4 transforms, B4.5 recipes and dictionary.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from e5lib import contract, eda, factory, features as af, protocol
from e5lib.paths import E5

from .env import BWriter, assert_a_frozen, b_outputs_dir

STAGE = "b04"
A_DICT = "stages/s04_features/{task}/outputs/feature_dictionary.csv"
ROUTE = "route_seller_to_customer_state"
NESTED_IN_ROUTE = ("customer_state", "primary_seller_state")   # B-G-02

# B candidates (CR-054): name -> (scope, change ID, kind, definition, formula, reason, log1p)
B_FEATURES = {
    "route_seller_to_customer_state": ("both", "B-C6", "categorical", "Route of the order: primary seller's state to the customer's state",
              "primary_seller_state + '->' + customer_state",
              "delivery time and experience differ by origin-destination pair; captures interactions distance alone misses", False),
    "seller_prior_late_handover_rate": ("both", "B-C7", "numeric", "Prior seller late-handover rate: share of the seller's earlier handovers made after their last shipping limit",
                           "mean over the seller's handovers in weeks before the prediction week of 1[carrier date > last shipping_limit_date]; new seller: weighted 3-week mean of sellers in the same state",
                           "a seller that dispatched late before is likely to dispatch late again (Henry)", False),
    "seller_prior_late_handover_days": ("both", "B-C7", "numeric", "Prior seller late-handover days: mean days by which the seller's earlier handovers missed the shipping limit (0 if on time)",
                           "mean of max(0, carrier date - last shipping_limit_date) over the seller's earlier handovers; same fallback",
                           "the size of past dispatch delays, not only their frequency (Henry)", True),
    "seller_prior_dispatch_days": ("both", "B-C7", "numeric", "Prior seller dispatch days: mean days from purchase to carrier handover over the seller's earlier orders",
                               "mean of (carrier date - purchase time) over the seller's earlier handovers; same fallback",
                               "seller packing speed is part of every lead time", True),
    "route_recent_delivery_days": ("both", "B-C8", "numeric", "Recent route delivery days: recent typical purchase-to-delivery time on the route",
                          "weighted 3-week mean (0.5, 0.3, 0.2) of the route's weekly median lead days; < 10 route events -> 0.7 x seller state + 0.3 x customer state, then overall",
                          "recent delivery conditions on the route (Henry: may also shape the customer's experience)", True),
    "route_recent_carrier_transit_days": ("both", "B-C8b", "numeric", "Recent route carrier transit days: recent typical carrier-to-customer time on the route",
                             "as route_recent_delivery_days, on (delivery date - carrier date)",
                             "the logistics part of the lead time with the seller's delay removed; promise-free (v3.1)", True),
    "order_handed_over_late": ("classification", "B-C9", "numeric", "This order was handed to the carrier after its last shipping limit",
                            "1[carrier date > last shipping_limit_date] of this order (known at handover)",
                            "a late dispatch is new information about the coming delivery and the review", False),
    "order_handover_late_days": ("classification", "B-C9", "numeric", "Days this order's handover missed the shipping limit (0 if on time)",
                        "max(0, carrier date - last shipping_limit_date) of this order", "size of this order's dispatch delay", True),
    "order_dispatch_days": ("classification", "B-C9", "numeric", "Days from purchase to this order's carrier handover",
                            "carrier date - purchase time of this order", "how long the customer has already waited at handover", True),
}


def b_pool(task: str) -> list[str]:
    return list(contract.pool(task)) + [f for f, v in B_FEATURES.items() if v[0] in ("both", task)]


def b_kind(f: str) -> str:
    return "categorical" if f in contract.CATEGORICAL or f == ROUTE else "numeric"


def importance(d: pd.DataFrame, task: str, pool: list[str], seed: int) -> tuple[dict, dict]:
    """A's s03 measures on B's rows."""
    values, method = {}, {}
    y = d["lead_days"] if task == "regression" else d["is_detractor"]
    for f in pool:
        if task == "regression":
            if b_kind(f) == "categorical":
                values[f], method[f] = eda.rank_correlation_ratio(d[f], y)["value"], "rank correlation ratio"
            else:
                values[f], method[f] = abs(eda.correlations(d[f], y)["spearman"]), "absolute Spearman"
        else:
            disc = True if b_kind(f) == "categorical" else eda.is_discrete(d[f])
            m = eda.mutual_information(d[f], y, discrete=disc, seed=seed)
            values[f], method[f] = m["mutual_information"], f"mutual_info_classif, {m['estimator']}"
    return values, method


def reduce(d: pd.DataFrame, pool: list[str], rank_of: dict) -> tuple[list[str], pd.DataFrame]:
    """A's 4.3 rule on B's pool: drop constants and the lower-ranked of identical columns; B-G-02:
    with route in the pool, drop the two state columns that route nests."""
    rows, dropped = [], set()
    if ROUTE in pool:
        for f in NESTED_IN_ROUTE:
            if f in pool:
                rows.append({"feature": f, "flagged_by": "nested in route (B-G-02)", "paired_with": ROUTE,
                             "rationale": f"every {ROUTE} level fixes {f}; its one-hot columns are sums of route's"})
                dropped.add(f)
    for f in pool:
        if d[f].nunique(dropna=True) <= 1:
            rows.append({"feature": f, "flagged_by": "constant", "paired_with": "", "rationale": "one value on B rows"})
            dropped.add(f)
    for i, a in enumerate(pool):
        for b in pool[i + 1:]:
            if a in dropped or b in dropped or b_kind(a) != b_kind(b):
                continue
            if d[a].equals(d[b]):
                drop, keep = (b, a) if rank_of.get(a, 1e9) <= rank_of.get(b, 1e9) else (a, b)
                rows.append({"feature": drop, "flagged_by": "duplicate", "paired_with": keep,
                             "rationale": f"identical to {keep} on every B row; {keep} ranks higher"})
                dropped.add(drop)
    return [f for f in pool if f not in dropped], pd.DataFrame(rows, columns=["feature", "flagged_by", "paired_with", "rationale"])


def spec_for(task: str, selected: list[str], logged: list[str], estimator: str) -> dict:
    spec = {"task": task, "estimator": estimator,
            "numeric": [f for f in selected if b_kind(f) == "numeric"],
            "categorical": [f for f in selected if b_kind(f) == "categorical"],
            "log_inputs": [f for f in selected if f in logged]}
    # no route-median fill: B-C2 removes every row with distance missing, so the fill and its
    # missing flag would be constant on B rows (B-G-02)
    spec["drop_duplicates"] = True
    if task == "regression":
        spec["log_target"] = True
    return spec


def run(task: str) -> None:
    assert_a_frozen()
    w = BWriter(STAGE, task)
    p = protocol.load()
    seed = int(p["seed"])
    threshold = af.decisions(task)["threshold"]
    d = pd.read_csv(w.read(b_outputs_dir("b02", task) / "records_B.csv.gz"), low_memory=False)
    a_dict = pd.read_csv(w.read(E5 / A_DICT.format(task=task)))

    # B4.1 pool and B4.2 ranking ------------------------------------------------------------------
    pool = b_pool(task)
    values, method = importance(d, task, pool, seed)
    rank = eda.cumulative_ranking(values, "B pool")
    rank["method"] = rank["feature"].map(method)
    rank["source"] = [B_FEATURES[f][1] if f in B_FEATURES else ("adopted candidate (G-70)" if f in contract.adopted(task) else "contract predictor")
                      for f in rank["feature"]]
    w.table("pool_ranking_B", rank.drop(columns=["measure"]), ids=("B4.1", "B4.2"))

    # B4.3 reduction and selection at A's threshold --------------------------------------------------
    core, red = reduce(d, pool, dict(zip(rank["feature"], rank["rank"])))
    w.table("reduction_B", red, ids=("B4.3",))
    sel_rank, selected = af.selection(rank, core, threshold)
    sel_rank = sel_rank.assign(source=sel_rank["feature"].map(dict(zip(rank["feature"], rank["source"]))))
    w.table("selection_ranking_B", sel_rank, ids=("B4.3",))
    w.json("selected_features_B", {"task": task, "threshold": threshold, "selected": selected,
                                   "dropped_below_threshold": [f for f in sel_rank["feature"] if f not in selected]}, ids=("B4.3",))

    # B4.4 transforms --------------------------------------------------------------------------------
    a_tr = af.transforms(d, task).set_index("feature")
    tr_rows = []
    for f in pool:
        if f in B_FEATURES:
            lg = B_FEATURES[f][6]
            rule = ("categorical: one-hot (drop-first for linear/logistic, every level for trees)" if b_kind(f) == "categorical"
                    else "log1p: day count (Henry)" if lg else "never logged: rate or flag, scaled only (Henry)")
            tr_rows.append({"feature": f, "skewness": np.nan if b_kind(f) == "categorical" else float(eda.profile(d[f])["skewness"]),
                            "log1p": lg, "rule": rule})
        else:
            r = a_tr.loc[f]
            tr_rows.append({"feature": f, "skewness": r["skewness"], "log1p": bool(r["log1p"]), "rule": r["rule"] + " (A's 4.2 rule on B rows)"})
    tr = pd.DataFrame(tr_rows)
    w.table("transforms_B", tr, ids=("B4.4",))
    logged = tr.loc[tr["log1p"].astype(bool), "feature"].tolist()

    # B4.5 recipes, design matrix and dictionary ----------------------------------------------------
    recipes = {fam: {"estimator": est, "spec": spec_for(task, selected, logged, est)} for fam, est in af.FAMILIES[task].items()}
    w.json("recipes_B", recipes, ids=("B4.5",))
    dm = []
    for fam in ("linear", "tree"):
        dm.append({"family": fam, **af.design_matrix(d, recipes[fam]["spec"])})
    dm = pd.DataFrame(dm)
    w.table("design_matrix_B", dm, ids=("B4.5",))
    rank_ix = sel_rank.set_index("feature")
    pool_ix = rank.set_index("feature")
    a_ix = a_dict.set_index("feature")
    drows = []
    for f in pool:
        kept = f in selected
        why = (f"selected: rank {int(rank_ix.loc[f, 'rank'])} of {len(sel_rank)}, cumulative share {rank_ix.loc[f, 'cumulative_share']:.4f} within {threshold:.0%}"
               if kept else (f"dropped: {red.set_index('feature').loc[f, 'flagged_by']}" if f in set(red["feature"])
                             else f"dropped: rank {int(rank_ix.loc[f, 'rank'])}, beyond the {threshold:.0%} cumulative share"))
        trf = tr.set_index("feature").loc[f, "rule"]
        if f in B_FEATURES:
            sc, cid, kd, defn, formula, reason, _ = B_FEATURES[f]
            src = f"Pipeline B ({cid})"
        else:
            r = a_ix.loc[f]
            sc, kd, defn, formula, reason, src = task, r["kind"], r["formula"], r["formula"], r["hypothesised_signal"], f"Pipeline A: {r['source']}"
        drows.append({"feature": f, "scope": sc, "source": src, "kind": kd, "definition": defn, "formula": formula,
                      "reason": reason, "transform": trf, "missing_share": float(d[f].isna().mean()),
                      "pool_rank": int(pool_ix.loc[f, "rank"]), "pool_share": float(pool_ix.loc[f, "share"]),
                      "importance": float(pool_ix.loc[f, "value"]), "importance_method": method[f], "kept": kept, "selection_reason": why})
    fd = pd.DataFrame(drows).sort_values("pool_rank").reset_index(drop=True)
    w.table("feature_dictionary_B", fd, ids=("B4.5",))

    # checks --------------------------------------------------------------------------------------
    w.check("the ranked set equals B's pool", set(rank["feature"]) == set(pool), ("B4.1", "B4.2"), f"{len(pool)} features")
    k = eda.cut_point(sel_rank, threshold)
    w.check(f"the kept set is exactly the {threshold:.0%} cumulative-share prefix of the core ranking",
            selected == list(sel_rank["feature"].head(k)), ("B4.3",), f"{len(selected)} of {len(sel_rank)} kept")
    w.check("every pool feature has a dictionary row with formula and reason",
            bool(fd[["formula", "reason"]].notna().all().all()) and len(fd) == len(pool), ("B4.5",))
    w.check("linear/logistic design matrix is full rank on B rows", bool(dm.loc[dm.family == "linear", "full_rank"].iloc[0]), ("B4.5",),
            f"rank {int(dm.loc[dm.family == 'linear', 'rank'].iloc[0])} of {int(dm.loc[dm.family == 'linear', 'columns'].iloc[0])}")
    w.check("no feature from the estimated delivery date", not any("estimated" in f or f == "est_delivery_days" for f in pool), ("B4.1",))

    # cards ---------------------------------------------------------------------------------------
    newf = [f for f in pool if f in B_FEATURES]
    w.explain("B4.1", done=f"B pool: A's {len(contract.pool(task))} pool features plus {len(newf)} B candidates ({', '.join(newf)}).")
    w.explain("B4.2", done="Ranking on B's development rows with A's measures (" + ("|Spearman|; rank correlation ratio for categorical"
              if task == "regression" else "mutual information") + "): top 8 " + "; ".join(
              f"{r.feature} {r.share:.3f}" for r in rank.head(8).itertuples()) + ".")
    kept_b = [f for f in selected if f in B_FEATURES]
    drop_b = [f for f in newf if f not in selected]
    w.explain("B4.3", done=f"{len(selected)} of {len(sel_rank)} core features kept at the {threshold:.0%} cumulative share (A's G-70 threshold). "
              f"B features kept: {', '.join(kept_b) or 'none'}; B features dropped: {', '.join(drop_b) or 'none'}. "
              f"Reduction: {len(red)} dropped (" + "; ".join(f"{r.feature}: {r.flagged_by}" for r in red.itertuples()) + ").")
    w.explain("B4.4", done=f"log1p on {len(logged)} features ({', '.join(logged)}); B day counts logged, B rates and flags scaled only.")
    w.explain("B4.5", done=f"Recipes for dummy, linear/logistic, tree and forest with A's factory; linear design matrix rank "
              f"{int(dm.loc[dm.family == 'linear', 'rank'].iloc[0])} of {int(dm.loc[dm.family == 'linear', 'columns'].iloc[0])}; "
              f"feature_dictionary_B.csv has {len(fd)} rows.")
    w.finish(seed=seed)
    if w.index["checks_failed"]:
        raise SystemExit(f"B4 {task}: checks failed: {w.index['checks_failed']}")
    print(f"B4 {task}: {len(selected)} of {len(sel_rank)} kept; B kept {kept_b}; B dropped {drop_b}")
