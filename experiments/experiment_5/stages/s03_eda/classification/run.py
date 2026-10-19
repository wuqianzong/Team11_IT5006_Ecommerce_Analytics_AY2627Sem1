"""s03_eda/classification: EDA of is_detractor on pre-cutoff orders (blueprint spec/blueprints/s03_eda.md).

Steps 3.2 (target profile), 3.3 (outcome trends), 3.6 (numeric features vs is_detractor), 3.7
(categorical features vs is_detractor), 3.8 (importance ranking, missingness, outliers,
collinearity) and 3.9 (eda_review_pack.md for the human gate, G-31). Only development rows are
loaded: eligible classification orders purchased before the task's test cutoff.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from e5lib import contract, data, eda, protocol  # noqa: E402
from e5lib import eda_sections as sec  # noqa: E402
from e5lib.outputs import Writer  # noqa: E402

STAGE, TASK = "s03_eda", "classification"
Y = "is_detractor"
TOP_LEVELS = 15  # levels shown per bar panel (statistics use every level)


def main() -> None:
    w = Writer(STAGE, TASK)
    p = protocol.load()
    seed = int(p["seed"])
    cutoff = pd.Timestamp(protocol.get("data_dependent.test_cutoffs.values")[TASK])
    d = sec.load_dates(data.load("records", TASK, "development", STAGE))
    y = d[Y].astype(int)
    num = list(contract.numeric())
    run_note = (f"Rows: {len(d):,} eligible classification orders purchased before the test cutoff {cutoff} "
                f"(latest purchase used {d['purchase_ts'].max()}).")

    # 3.2 Classification target ------------------------------------------------------------------
    n1, n = int(y.sum()), int(len(y))
    target = pd.DataFrame([{"class": "low review (score <= 2), is_detractor = 1", "orders": n1, "share": n1 / n},
                           {"class": "normal review (score >= 3), is_detractor = 0", "orders": n - n1, "share": (n - n1) / n},
                           {"class": "total", "orders": n, "share": 1.0}])
    w.table("target_classification_is_detractor", target, ids=("3.2",))
    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.bar(["normal (>= 3)", "low (<= 2)"], [n - n1, n1], color=["0.65", "tab:red"])
    for i, (k, s) in enumerate(((n - n1, (n - n1) / n), (n1, n1 / n))):
        ax.text(i, k, f"{k:,}\n({s:.1%})", ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("orders")
    ax.set_ylim(0, (n - n1) * 1.15)
    ax.set_title(f"is_detractor, pre-cutoff orders (n = {n:,})")
    w.figure("target_is_detractor_bar", fig, target, ids=("3.2",), title="is_detractor counts")
    plt.close(fig)

    # 3.3 Outcome trends -------------------------------------------------------------------------
    tr = sec.trends(w, d, TASK)
    trq = tr[tr["orders"] >= sec.MIN_MONTH_ORDERS]  # ranges quoted in cards

    # 3.6 Numeric features vs is_detractor ---------------------------------------------------------
    rows, curves, mi, mi_method = [], [], {}, {}
    for c in num:
        ov = eda.overlap(d[c], y, log1p=c in contract.LOG_CANDIDATES)
        a = eda.auc(d[c], y)
        m = eda.mutual_information(d[c], y, discrete=eda.is_discrete(d[c]), seed=seed)
        mi[c], mi_method[c] = m["mutual_information"], m["estimator"]
        x = d[c]
        rows.append({"feature": c, "n": ov["n"], "overlap_coefficient": ov["overlap"], "overlap_method": ov["method"],
                     "roc_auc": a["roc_auc"], "roc_auc_symmetric": a["roc_auc_symmetric"], "direction": a["direction"],
                     "mutual_information": m["mutual_information"], "mi_estimator": m["estimator"],
                     "mean_class_0": float(x[y == 0].mean()), "mean_class_1": float(x[y == 1].mean()),
                     "median_class_0": float(x[y == 0].median()), "median_class_1": float(x[y == 1].median()),
                     **{f"feature_{k}": v for k, v in eda.profile(x).items()}})
        curves.append(ov["curve"].assign(feature=c, method=ov["method"]))
    numeric = pd.DataFrame(rows).sort_values(["overlap_coefficient", "feature"], kind="mergesort")
    w.table("numeric_feature_target_is_detractor", numeric, ids=("3.6",))
    curves = pd.concat(curves, ignore_index=True)[["feature", "method", "x", "class_0", "class_1"]]
    fig, axes = plt.subplots(5, 4, figsize=(16, 18))
    for ax, c in zip(axes.flat, numeric["feature"]):
        cv = curves[curves["feature"] == c]
        r = numeric.set_index("feature").loc[c]
        if r["overlap_method"] == "discrete frequencies":
            wdt = 0.4 * (np.min(np.diff(cv["x"])) if len(cv) > 1 else 1.0)
            ax.bar(cv["x"] - wdt / 2, cv["class_0"], width=wdt, color="0.6", label="normal")
            ax.bar(cv["x"] + wdt / 2, cv["class_1"], width=wdt, color="tab:red", label="detractor")
            ax.set_ylabel("share within class", fontsize=7)
        else:
            ax.plot(cv["x"], cv["class_0"], color="0.4", label="normal")
            ax.plot(cv["x"], cv["class_1"], color="tab:red", label="detractor")
            ax.fill_between(cv["x"], np.minimum(cv["class_0"], cv["class_1"]), color="tab:purple", alpha=0.2)
            ax.set_ylabel("density", fontsize=7)
        ax.set_xlabel(f"log1p({c})" if r["overlap_method"].endswith("(log1p scale)") else c, fontsize=7)
        ax.set_title(f"{c}\noverlap {r['overlap_coefficient']:.1%}, ROC-AUC {r['roc_auc']:.3f}", fontsize=8)
        ax.tick_params(labelsize=6)
    axes.flat[0].legend(fontsize=7)
    fig.suptitle("Numeric features by class (KDE, or class frequencies for features with <= 30 values); "
                 "sorted by overlap, lowest first", y=1.0)
    fig.tight_layout()
    w.figure("numeric_vs_is_detractor", fig, curves, ids=("3.6",), title="Class-conditional distributions")
    plt.close(fig)

    # 3.7 Categorical features vs is_detractor -----------------------------------------------------
    cat_rows = []
    for c in list(contract.CATEGORICAL) + list(contract.CALENDAR_NUMERIC):
        g = pd.DataFrame({"level": d[c].astype(str), "y": y}).groupby("level")["y"]
        lv = pd.DataFrame({"n": g.size(), "detractors": g.sum(), "detractor_rate": g.mean()}).reset_index()
        lv["share"] = lv["n"] / len(d)
        if c in contract.CATEGORICAL:
            m = eda.mutual_information(d[c], y, discrete=True, seed=seed)
            mi[c], mi_method[c] = m["mutual_information"], m["estimator"]
            lv = lv.assign(feature=c, encoding="categorical", mutual_information=m["mutual_information"])
        else:
            lv = lv.assign(feature=c, encoding="numeric (plots only; MI in the numeric table)", mutual_information=np.nan)
        cat_rows.append(lv)
    cat = pd.concat(cat_rows, ignore_index=True)
    cat["level_order"] = pd.to_numeric(cat["level"], errors="coerce")
    cat = cat.sort_values(["feature", "level_order", "level"], kind="mergesort").drop(columns="level_order")
    cat = cat[["feature", "encoding", "level", "n", "share", "detractors", "detractor_rate", "mutual_information"]]
    w.table("categorical_feature_target_is_detractor", cat, ids=("3.7",))

    prevalence = n1 / n
    panels = list(contract.CATEGORICAL) + list(contract.CALENDAR_NUMERIC)
    fig, axes = plt.subplots(len(panels), 1, figsize=(14, 24))
    shown = []
    for ax, c in zip(axes, panels):
        sub = cat[cat["feature"] == c]
        if c in contract.CATEGORICAL:
            sub = sub.sort_values("n", ascending=False, kind="mergesort").head(TOP_LEVELS)
        ax.bar(range(len(sub)), sub["detractor_rate"], color="tab:red", alpha=0.7)
        ax.axhline(prevalence, color="k", ls="--", lw=1, label=f"overall {prevalence:.1%}")
        ax.set_xticks(range(len(sub)), sub["level"], rotation=45, fontsize=7, ha="right")
        more = f" (top {TOP_LEVELS} of {d[c].nunique()} levels by count)" if c in contract.CATEGORICAL \
            and d[c].nunique() > TOP_LEVELS else ""
        mi_txt = f"; MI {mi[c]:.4f} nats" if c in contract.CATEGORICAL else ""
        ax.set_title(f"{c}{more}{mi_txt}", fontsize=9)
        ax.set_ylabel("detractor rate", fontsize=8)
        ax.legend(fontsize=7)
        shown.append(sub)
    fig.suptitle("Detractor rate by level (dashed: overall rate)", y=1.0)
    fig.tight_layout()
    w.figure("categorical_vs_is_detractor", fig, pd.concat(shown, ignore_index=True), ids=("3.7",),
             title="Detractor rate by level")
    plt.close(fig)

    # 3.8 Ranking, missingness, outliers, collinearity ----------------------------------------------
    col = sec.quality_and_collinearity(w, d, p)
    skew = sec.log_candidate_skewness(d, p)
    method = {c: f"mutual_info_classif, {mi_method[c]}" for c in contract.PREDICTORS}
    rank, cuts = sec.ranking(w, {c: mi[c] for c in contract.PREDICTORS}, TASK, p, method)
    # 3.10-3.13 Candidate screen (G-68, G-69): screening columns, not predictors ---------------------
    groups = [("3.10", "product", "candidate_screen", "Product fields of the primary item (G-68)"),
              ("3.11", "promise", "candidate_screen_promise", "Promised delivery days at checkout (G-69)"),
              ("3.12", "region", "candidate_screen_region", "IBGE macro-regions and the region pair (G-69)"),
              ("3.13", "seller_history", "candidate_screen_seller_history",
               "Primary seller's history strictly before checkout (G-69)")]
    cands = list(contract.screening(TASK))
    tables, level_tables = {}, []
    for sid_, grp, fname, title in groups:
        names = list(contract.screening_group(TASK, grp))
        tables[sid_], lv = sec.screen_group(w, d, y, names, sid_, fname, f"Candidate screen {sid_}: {title}", seed, num)
        level_tables.append(lv)
    screen = pd.concat([t.assign(card=k) for k, t in tables.items()], ignore_index=True)
    ext_numeric = [c for c in cands if contract.SCREENING_CANDIDATES[TASK][c]["kind"] == "numeric"]
    ext_num = num + ext_numeric
    ext_vif = eda.vif(d[ext_num])
    ext_pairs, ext_groups = eda.collinear_groups(d[ext_num].corr(), d[ext_num].corr(method="spearman"), ext_vif,
                                                 col["corr_above"], col["vif_above"], col["duplicates"])
    screen["vif_in_extended_set"] = screen["feature"].map(ext_vif)
    ext_pairs = ext_pairs[ext_pairs["feature_a"].isin(cands) | ext_pairs["feature_b"].isin(cands)]
    ext_groups = [g for g in ext_groups if set(g["features"]) & set(cands)]
    ext = eda.cumulative_ranking({**{c: mi[c] for c in contract.PREDICTORS},
                                  **screen.set_index("feature")["mutual_information"].to_dict()}, sec.MEASURE[TASK])
    ext["candidate"] = ext["feature"].isin(cands)
    ext["card"] = ext["feature"].map(screen.set_index("feature")["card"]).fillna("3.8")
    ext_cuts = {f"{t:.2f}": eda.cut_point(ext, t) for t in (float(x) for x in p["features"]["selection"]["cumulative_threshold_options"])}
    screen["rank_in_extended"] = screen["feature"].map(ext.set_index("feature")["rank"])
    screen["inside_95_cut"] = screen["rank_in_extended"] <= ext_cuts["0.95"]
    screen["inside_99_cut"] = screen["rank_in_extended"] <= ext_cuts["0.99"]
    for sid_, _, _, _ in groups:
        w.table(f"candidate_screen_{sid_.replace('.', '_')}", screen[screen["card"] == sid_], ids=(sid_,))
    w.table("candidate_screen_levels", pd.concat(level_tables, ignore_index=True), ids=("3.12",))
    w.table("candidate_ranking_extended", ext, ids=("3.10",))
    w.table("candidate_collinear_pairs", ext_pairs, ids=("3.10", "3.13"))

    fig, ax = plt.subplots(figsize=(13, 5.5))
    ax.bar(ext["rank"], ext["share"], color=np.where(ext["candidate"], "tab:orange", "0.7"))
    ax.plot(ext["rank"], ext["cumulative_share"], marker="o", ms=3, color="tab:blue")
    for (t, k), colr in zip(ext_cuts.items(), ("tab:green", "tab:orange")):
        ax.axhline(float(t), color=colr, ls="--", lw=1)
        ax.axvline(k + 0.5, color=colr, ls=":", lw=1)
        ax.text(k + 0.7, float(t) - 0.07, f"{float(t):.0%}: top {k}", color=colr, fontsize=8)
    ax.set_xticks(ext["rank"], ext["feature"], rotation=80, fontsize=6, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_title(f"Extended mutual-information ranking: 24 contract predictors + {len(cands)} screening candidates "
                 "(orange)", fontsize=10)
    fig.tight_layout()
    w.figure("candidate_ranking_extended", fig, ext, ids=("3.10",), title="Extended ranking")
    plt.close(fig)

    late = (d["lead_label_ts"] > d["order_estimated_delivery_date"]).where(d["lead_days"].notna())
    late_rate = d[Y].astype(float).groupby(late.astype(float)).mean()
    extra = [
        {"finding": f"detractor prevalence {prevalence:.2%} ({n1:,} of {n:,} pre-cutoff orders)",
         "evidence": "target_classification_is_detractor.csv",
         "change_it_motivates": "average precision with the prevalence baseline as the primary metric (s01)",
         "stage_that_tests_it": "s06, s08"},
        {"finding": f"detractor rate ranges {trq['detractor_rate'].min():.1%} to {trq['detractor_rate'].max():.1%} "
                    f"across purchase months with at least {sec.MIN_MONTH_ORDERS} orders",
         "evidence": "outcome_trends.csv", "change_it_motivates": "time-ordered expanding folds; class support per fold",
         "stage_that_tests_it": "s05 5.5, 5.8"},
    ]
    if {0.0, 1.0} <= set(late_rate.index):
        extra.append({"finding": f"detractor rate {late_rate[1.0]:.1%} for orders delivered after the promised date vs "
                                 f"{late_rate[0.0]:.1%} on time (description only, G-35)",
                      "evidence": "eda_summary.json:detractor_rate_by_late",
                      "change_it_motivates": "none: lateness is known only after delivery and is never a predictor; "
                                             "it explains why checkout-time signal is limited",
                      "stage_that_tests_it": "s09 (discussion)"})
    for r in screen.itertuples():
        extra.append({"finding": f"candidate {r.feature}: " + ("" if pd.isna(r.roc_auc) else f"ROC-AUC {r.roc_auc:.3f}, ") + f"overlap {r.overlap_coefficient:.1%}, "
                                 f"MI rank {r.rank_in_extended} of {len(ext)} in the extended ranking",
                      "evidence": f"candidate_screen_{r.card.replace('.', '_')}.csv, candidate_ranking_extended.csv",
                      "change_it_motivates": "team adopts or drops it at the s03 gate (G-68); if adopted it joins the "
                                             "classification selection pool with its planned transform",
                      "stage_that_tests_it": "s04 4.4 (pool), s06"})
    sec.rationale(w, TASK, skew, col, rank, cuts, extra)

    summary = {"task": TASK, "rows": n, "test_cutoff": str(cutoff), "latest_purchase_used": str(d["purchase_ts"].max()),
               "target": {"detractors": n1, "normal": n - n1, "prevalence": prevalence},
               "detractor_rate_by_late": {("late" if k == 1.0 else "on time"): float(v) for k, v in late_rate.items()},
               "log1p_candidates": skew.to_dict(orient="records"), "ranking_measure": sec.MEASURE[TASK],
               "cut_points": cuts, "top_features": rank["feature"].head(5).tolist(),
               "collinearity": {"cut_offs": {"abs_correlation_above": col["corr_above"], "vif_above": col["vif_above"]},
                                "vif_complete_rows": col["vif_rows"], "groups": col["groups"],
                                "identical_columns": col["duplicates"], "constant_columns": col["constant"]},
               "missing_share": {k: v for k, v in col["quality"].set_index("feature")["missing_share"].items() if v > 0},
               "candidate_screen": {"candidates": cands, "extended_cut_points": ext_cuts,
                                    "rows": screen.to_dict(orient="records"), "collinear_groups": ext_groups}}
    w.json("eda_summary", eda.json_safe(summary), ids=("3.2", "3.3", "3.8", "3.10", "3.11", "3.12", "3.13"))
    w.decision("importance ranking for s04 selection", f"{sec.MEASURE[TASK]} over the 24 contract predictors (3.8)",
               "24 contract predictors", rank["feature"].tolist(), ["importance_ranking.csv"], ids=("3.8",),
               notes=f"cut points {cuts}; threshold chosen by the team (G-31)")

    # 3.9 Review pack ---------------------------------------------------------------------------
    mi_cat = cat.drop_duplicates("feature").query("encoding == 'categorical'")[["feature", "mutual_information"]]
    sections = [
        ("Target: is_detractor (3.2)", sec._md_table(target) + "\n\n![bar](figures/target_is_detractor_bar.png)"),
        ("Outcome trends (3.3)", sec._md_table(tr) + "\n\n![trends](figures/outcome_trends.png)"),
        ("Numeric features vs is_detractor (3.6)",
         sec._md_table(numeric[["feature", "n", "overlap_coefficient", "overlap_method", "roc_auc", "mutual_information"]])
         + "\n\n![class-conditional](figures/numeric_vs_is_detractor.png)"),
        ("Categorical features vs is_detractor (3.7)", sec._md_table(mi_cat)
         + "\n\nPer-level detractor rates: categorical_feature_target_is_detractor.csv."
         "\n\n![detractor rate by level](figures/categorical_vs_is_detractor.png)"),
        ("Missingness and outliers (3.8)", sec._md_table(col["quality"][["feature", "type", "missing_share",
                                                                         "share_outside_1_5_iqr", "share_outside_3_iqr", "vif", "vif_note"]])),
        ("Skewness of the log1p candidates (3.8, for s04 4.2)", sec._md_table(skew)),
        ("Candidate screen (3.10-3.13, G-68, G-69; not predictors unless adopted)",
         sec._md_table(screen[["card", "feature", "kind", "n", "missing_share", "overlap_coefficient", "roc_auc",
                               "mutual_information", "rank_in_extended", "inside_95_cut", "inside_99_cut", "skewness",
                               "vif_in_extended_set"]])
         + f"\n\nExtended cut points (24 + {len(cands)}): {ext_cuts}. Collinear groups involving a candidate: "
         + (", ".join(str(g["features"]) for g in ext_groups) or "none")
         + ". Record adopted candidates under `adopted_candidates` in human_decisions.yaml."
         + "\n\n![extended ranking](figures/candidate_ranking_extended.png)"),
    ]
    sec.review_pack(w, TASK, run_note, sections, rank, cuts, col)

    # Checks ------------------------------------------------------------------------------------
    w.check("no order on or after the test cutoff loaded", d["purchase_ts"].max() < cutoff, ids=("3.2", "3.3", "3.8"),
            detail=f"latest purchase {d['purchase_ts'].max()}, cutoff {cutoff}")
    w.check("all 24 contract predictors diagnosed against is_detractor",
            set(numeric["feature"]) | set(cat.loc[cat["encoding"] == "categorical", "feature"]) == set(contract.PREDICTORS),
            ids=("3.6", "3.7"))
    w.check("importance_ranking has the 24 contract predictors and ends at cumulative share 1.0",
            len(rank) == 24 and set(rank["feature"]) == set(contract.PREDICTORS)
            and rank["cumulative_share"].iloc[-1] == 1.0 and rank["cumulative_share"].is_monotonic_increasing,
            ids=("3.8",), detail=f"{len(rank)} rows")
    w.check("ranking measure is the pre-registered one",
            p["features"]["selection"]["ranking"][TASK] == sec.MEASURE[TASK], ids=("3.8",))
    w.check("outcome trends show outcomes, not volume only",
            {"median_lead_days", "late_vs_promised_rate", "detractor_rate"} <= set(tr.columns), ids=("3.3",))
    w.check("review pack lists both cut points and every flagged group", len(cuts) == 2, ids=("3.9",))
    for sid_, grp, _, _ in groups:
        w.check(f"candidate screen {sid_} covers every {grp} candidate", set(tables[sid_]["feature"])
                == set(contract.screening_group(TASK, grp)), ids=(sid_,), detail=f"{len(tables[sid_])} candidates")
    w.check("extended ranking holds the 24 predictors and every candidate, ends at 1.0; official ranking unchanged at 24",
            len(ext) == 24 + len(cands) and ext["cumulative_share"].iloc[-1] == 1.0 and len(rank) == 24, ids=("3.10",),
            detail=f"{len(ext)} rows")

    # Evidence cards --------------------------------------------------------------------------------
    best = numeric.iloc[0]
    w.explain("3.2", done=f"{n:,} pre-cutoff orders: {n1:,} low reviews (score <= 2, {prevalence:.2%}) and "
              f"{n - n1:,} normal reviews (score >= 3, {(n - n1) / n:.2%}).",
              conclusion="Imbalanced target: average precision is read against the prevalence baseline.")
    w.explain("3.3", done=f"{len(tr)} purchase months; over the {len(trq)} months with at least "
              f"{sec.MIN_MONTH_ORDERS} orders: detractor rate {trq['detractor_rate'].min():.1%} to "
              f"{trq['detractor_rate'].max():.1%}, late-vs-promised rate {trq['late_vs_promised_rate'].min():.1%} to "
              f"{trq['late_vs_promised_rate'].max():.1%}, median lead time {trq['median_lead_days'].min():.1f} to "
              f"{trq['median_lead_days'].max():.1f} days; every month is in the table with its counts.",
              reasoning="Late is delivery after order_estimated_delivery_date, used here only as a description (G-35).")
    w.explain("3.6", done=f"{len(num)} numeric predictors: class-conditional distributions with the overlap "
              f"coefficient (KDE for continuous features, class frequencies for features with at most "
              f"{eda.DISCRETE_MAX_LEVELS} values), per-feature ROC-AUC and mutual information on the same rows; lowest "
              f"overlap: {best['feature']} ({best['overlap_coefficient']:.1%}, ROC-AUC {best['roc_auc']:.3f}).",
              reasoning="A KDE smears an integer count into values that cannot occur, so features with few values use "
                        "the class frequencies; the five log1p candidates use the KDE on the log1p scale (the "
                        "coefficient does not change under a monotone transform). Flagged for the team (decision 2).")
    w.explain("3.7", done="Four categorical predictors: mutual_info_classif (discrete, seed "
              f"{seed}) and per-level detractor rates; calendar fields shown per level for the plots only. "
              f"MI: {', '.join(f'{c} {mi[c]:.4f}' for c in contract.CATEGORICAL)} nats.")
    w.explain("3.8", done=f"Ranking over the 24 contract predictors by mutual information (discrete estimator for "
              f"categorical features and features with at most {eda.DISCRETE_MAX_LEVELS} values, k-NN estimator for "
              f"the rest): top 5 {rank['feature'].head(5).tolist()}; cut points {cuts}. Missingness, IQR outliers, "
              f"Pearson/Spearman matrix and VIF on {col['vif_rows']:,} complete rows; flagged groups: "
              f"{[g['features'] for g in col['groups']]}; identical columns: {col['duplicates']}.")
    def ranks(sid_):
        t_ = screen[screen["card"] == sid_]
        return "; ".join(f"{r.feature}: rank {r.rank_in_extended}, MI {r.mutual_information:.4f}"
                         + ("" if pd.isna(r.roc_auc) else f", ROC-AUC {r.roc_auc:.3f}") + f", overlap {r.overlap_coefficient:.1%}"
                         for r in t_.itertuples())
    common = ("Screening columns (not predictors) diagnosed against is_detractor with the 3.6 measures; numeric ones also "
              "with skewness, correlation with the 20 numeric predictors and VIF in the extended numeric set. ")
    w.explain("3.10", done=common + f"Product fields (primary item): {ranks('3.10')}. Extended ranking over 24 + "
              f"{len(cands)} candidates; cut points {ext_cuts} (official 3.8 ranking unchanged at {len(rank)}).",
              reasoning="The extended ranking shows where each candidate would enter; s04 recomputes the cumulative "
                        "share over the agreed pool (24 + adopted candidates). Screening on pre-cutoff orders and then "
                        "choosing is a post-hoc addition; the report says so.",
              conclusion="Team decision at the gate: adopt or drop each candidate (human_decisions.yaml).")
    w.explain("3.11", done=common + f"Promised delivery days: {ranks('3.11')}.",
              reasoning="G-35 is reopened for this screen only. Olist's own promise is measured here; in production the "
                        "promise would come from the task 1 prediction, so if adopted the classifier trains on "
                        "out-of-fold task 1 predictions, which makes classification s06 depend on regression s06.")
    w.explain("3.12", done=common + f"Regions (IBGE macro-regions; pair = customer>seller): {ranks('3.12')}. "
              "Per-level detractor rates in candidate_screen_levels.csv.",
              reasoning="A region has 5 levels instead of 27 states, so each level holds more orders; the pair captures "
                        "logistics corridors. Mutual information with many levels is biased upward, so compare the "
                        "region and state values with that in mind.")
    w.explain("3.13", done=common + f"Seller history at checkout: {ranks('3.13')}.",
              reasoning="Only the primary seller's events strictly before the purchase second count (reviews at their "
                        "answer time, deliveries at delivery time) and the order's own events never count; s02 checks "
                        "this against a direct recomputation on 2,000 orders. Sellers without history are missing, with "
                        "the counts at 0.")
    w.explain("3.9", done="eda_review_pack.md lists every table and figure above, the ranking with both cut points, "
              "the flagged collinear groups and the YAML block the team fills in spec/human_decisions.yaml.",
              conclusion="Stop: s04 waits for the team's threshold and collinearity decisions (G-31).")
    w.finish(seed=seed)


if __name__ == "__main__":
    main()
