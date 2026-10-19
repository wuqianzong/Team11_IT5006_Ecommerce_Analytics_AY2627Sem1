"""s03_eda/regression: EDA of lead_days on pre-cutoff orders (blueprint spec/blueprints/s03_eda.md).

Steps 3.1 (target profile), 3.3 (outcome trends), 3.4 (numeric features vs lead_days), 3.5
(categorical features vs lead_days), 3.8 (importance ranking, missingness, outliers, collinearity)
and 3.9 (eda_review_pack.md for the human gate, G-31). Only development rows are loaded: eligible
regression orders purchased before the task's test cutoff (data.load population guard).
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402

from e5lib import contract, data, eda, protocol  # noqa: E402
from e5lib import eda_sections as sec  # noqa: E402
from e5lib.outputs import Writer  # noqa: E402

STAGE, TASK = "s03_eda", "regression"
Y = "lead_days"
PLOT_SAMPLE = 2000  # points per scatter panel (plot only; statistics use every row)
TOP_LEVELS = 15     # levels shown per violin panel (statistics use every level)


def main() -> None:
    w = Writer(STAGE, TASK)
    p = protocol.load()
    seed = int(p["seed"])
    cutoff = pd.Timestamp(protocol.get("data_dependent.test_cutoffs.values")[TASK])
    d = sec.load_dates(data.load("records", TASK, "development", STAGE))
    y = d[Y].astype(float)
    num = list(contract.numeric())
    run_note = (f"Rows: {len(d):,} eligible regression orders purchased before the test cutoff {cutoff} "
                f"(latest purchase used {d['purchase_ts'].max()}).")

    # 3.1 Regression target ------------------------------------------------------------------------
    prof = eda.profile(y)
    target = pd.DataFrame([{"statistic": k, "value": v} for k, v in prof.items()])
    w.table("target_regression_lead_days", target, ids=("3.1",))
    grid = np.linspace(0, float(np.percentile(y, 99.9)), 400)
    dens = stats.gaussian_kde(y)(grid)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(grid, dens)
    ax.fill_between(grid, dens, alpha=0.2)
    for q, ls in (("p50", "-"), ("p95", "--"), ("p99", ":")):
        ax.axvline(prof[q], color="0.3", ls=ls, lw=1, label=f"{q} = {prof[q]:.1f} days")
    ax.set_xlabel("lead_days (purchase to delivery)")
    ax.set_ylabel("density")
    ax.set_title(f"lead_days KDE, pre-cutoff orders (n = {prof['count']:,}; skewness {prof['skewness']:.2f})")
    ax.legend()
    w.figure("target_lead_days_kde", fig, pd.DataFrame({"lead_days": grid, "density": dens}), ids=("3.1",),
             title="lead_days KDE")
    plt.close(fig)

    # 3.3 Outcome trends ---------------------------------------------------------------------------
    tr = sec.trends(w, d, TASK)
    trq = tr[tr["orders"] >= sec.MIN_MONTH_ORDERS]  # ranges quoted in cards

    # 3.4 Numeric features vs lead_days ------------------------------------------------------------
    rows, pts = [], []
    rng = np.random.default_rng(seed)
    for c in num:
        r = {"feature": c, **eda.correlations(d[c], y)}
        r["abs_spearman"] = abs(r["spearman"])
        r.update({f"feature_{k}": v for k, v in eda.profile(d[c]).items()})
        rows.append(r)
        ok = d[c].notna().to_numpy().nonzero()[0]
        take = rng.choice(ok, size=min(PLOT_SAMPLE, len(ok)), replace=False)
        pts.append(pd.DataFrame({"feature": c, "x": d[c].to_numpy(float)[take], "lead_days": y.to_numpy()[take]}))
    numeric = pd.DataFrame(rows).sort_values(["abs_spearman", "feature"], ascending=[False, True], kind="mergesort")
    w.table("numeric_feature_target_lead_days", numeric, ids=("3.4",))
    pts = pd.concat(pts, ignore_index=True)
    fig, axes = plt.subplots(5, 4, figsize=(16, 18))
    for ax, c in zip(axes.flat, numeric["feature"]):
        s = pts[pts["feature"] == c]
        logx = c in contract.LOG_CANDIDATES
        ax.scatter(np.log1p(s["x"]) if logx else s["x"], s["lead_days"], s=3, alpha=0.25)
        r = numeric.set_index("feature").loc[c]
        ax.set_title(f"{c}\nPearson {r['pearson']:.3f}, Spearman {r['spearman']:.3f}", fontsize=8)
        ax.set_xlabel(f"log1p({c})" if logx else c, fontsize=7)
        ax.tick_params(labelsize=6)
    for ax in axes.flat:
        ax.set_ylabel("lead_days", fontsize=7)
    fig.suptitle(f"Numeric features vs lead_days (random {PLOT_SAMPLE:,} orders per panel, seed {seed}; "
                 "sorted by |Spearman|)", y=1.0)
    fig.tight_layout()
    w.figure("numeric_vs_lead_days", fig, pts, ids=("3.4",), title="Numeric features vs lead_days")
    plt.close(fig)

    # 3.5 Categorical features vs lead_days (calendar fields as categories for the plots only) -----
    cat_rows, ratio = [], {}
    for c in contract.CATEGORICAL:
        oh = eda.one_hot_correlations(d[c], y)
        rcr = eda.rank_correlation_ratio(d[c], y)
        ratio[c] = rcr["value"]
        cat_rows.append(oh.assign(feature=c, encoding="one-hot (drop-first)", rank_correlation_ratio=rcr["value"]))
    for c in contract.CALENDAR_NUMERIC:
        oh = eda.one_hot_correlations(d[c], y)
        oh["dummy"], oh["dummy_correlation"] = "not encoded: numeric feature, categorical for plots only", np.nan
        cat_rows.append(oh.assign(feature=c, encoding="numeric (plots only)", rank_correlation_ratio=np.nan))
    cat = pd.concat(cat_rows, ignore_index=True)
    cat = cat[["feature", "encoding", "level", "n", "share", "target_median", "target_q1", "target_q3", "target_mean",
               "dummy", "dummy_correlation", "rank_correlation_ratio"]]
    cat["level_order"] = pd.to_numeric(cat["level"], errors="coerce")
    cat = cat.sort_values(["feature", "level_order", "level"], kind="mergesort").drop(columns="level_order")
    w.table("categorical_feature_target_lead_days", cat, ids=("3.5",))

    ylim = float(np.percentile(y, 99))
    fig, axes = plt.subplots(len(contract.CATEGORICAL) + len(contract.CALENDAR_NUMERIC), 1, figsize=(14, 26))
    shown = []
    for ax, c in zip(axes, list(contract.CATEGORICAL) + list(contract.CALENDAR_NUMERIC)):
        if c in contract.CALENDAR_NUMERIC:
            levels = sorted(d[c].dropna().unique())
        else:
            levels = d[c].value_counts().head(TOP_LEVELS).index.tolist()
        groups = [y[(d[c] == lev) & (y <= ylim)].to_numpy() for lev in levels]
        ax.violinplot(groups, showmedians=True, showextrema=False)
        for i, g in enumerate(groups, start=1):
            q1, q3 = np.percentile(g, (25, 75))
            ax.vlines(i, q1, q3, color="k", lw=3)
        ax.set_xticks(range(1, len(levels) + 1), [str(v) for v in levels], rotation=45, fontsize=7, ha="right")
        more = "" if c in contract.CALENDAR_NUMERIC or d[c].nunique() <= TOP_LEVELS else \
            f" (top {TOP_LEVELS} of {d[c].nunique()} levels by count)"
        ax.set_title(f"{c}{more}", fontsize=9)
        ax.set_ylabel("lead_days", fontsize=8)
        shown.append(cat[(cat["feature"] == c) & cat["level"].astype(str).isin([str(v) for v in levels])])
    fig.suptitle(f"lead_days by level: median (line) and IQR (bar); lead_days above p99 ({ylim:.1f} days) "
                 "not drawn", y=1.0)
    fig.tight_layout()
    w.figure("categorical_vs_lead_days", fig, pd.concat(shown, ignore_index=True), ids=("3.5",),
             title="Categorical features vs lead_days (violins)")
    plt.close(fig)

    # 3.8 Ranking, missingness, outliers, collinearity ----------------------------------------------
    col = sec.quality_and_collinearity(w, d, p)
    skew = sec.log_candidate_skewness(d, p)
    values = {**numeric.set_index("feature")["abs_spearman"].to_dict(), **ratio}
    method = {c: "|Spearman|" for c in num} | {c: "rank correlation ratio (Spearman scale)" for c in contract.CATEGORICAL}
    rank, cuts = sec.ranking(w, {c: values[c] for c in contract.PREDICTORS}, TASK, p, method)
    dist_missing = float(d["distance_km_max"].isna().mean())
    extra = [
        {"finding": f"lead_days skewness {prof['skewness']:.2f}, p99 {prof['p99']:.1f} vs median {prof['p50']:.1f} days",
         "evidence": "target_regression_lead_days.csv", "change_it_motivates": "log1p regression target (G-36)",
         "stage_that_tests_it": "s04 4.2, s06"},
        {"finding": f"median lead time ranges {trq['median_lead_days'].min():.1f} to {trq['median_lead_days'].max():.1f} "
                    f"days across purchase months with at least {sec.MIN_MONTH_ORDERS} orders",
         "evidence": "outcome_trends.csv", "change_it_motivates": "time-ordered expanding folds, not random folds",
         "stage_that_tests_it": "s05 5.5"},
        {"finding": f"distance_km_max missing on {dist_missing:.2%} of orders",
         "evidence": "feature_quality.csv:missing_share", "change_it_motivates":
         "route-median fill (customer x seller state) with the missing indicator, fitted in folds (G-27)",
         "stage_that_tests_it": "s04 4.8, s06"},
    ]
    sec.rationale(w, TASK, skew, col, rank, cuts, extra)

    summary = {"task": TASK, "rows": int(len(d)), "test_cutoff": str(cutoff),
               "latest_purchase_used": str(d["purchase_ts"].max()), "target_profile": prof,
               "log1p_candidates": skew.to_dict(orient="records"),
               "ranking_measure": sec.MEASURE[TASK], "cut_points": cuts,
               "top_features": rank["feature"].head(5).tolist(),
               "collinearity": {"cut_offs": {"abs_correlation_above": col["corr_above"], "vif_above": col["vif_above"]},
                                "vif_complete_rows": col["vif_rows"], "groups": col["groups"],
                                "identical_columns": col["duplicates"], "constant_columns": col["constant"]},
               "missing_share": {k: v for k, v in col["quality"].set_index("feature")["missing_share"].items() if v > 0}}
    w.json("eda_summary", eda.json_safe(summary), ids=("3.1", "3.3", "3.8"))
    w.decision("importance ranking for s04 selection", f"{sec.MEASURE[TASK]} over the 24 contract predictors (3.8)",
               "24 contract predictors", rank["feature"].tolist(), ["importance_ranking.csv"], ids=("3.8",),
               notes=f"cut points {cuts}; threshold chosen by the team (G-31)")

    # 3.9 Review pack ---------------------------------------------------------------------------
    t_tab = target.assign(value=target["value"].map(lambda v: f"{v:,.4f}" if isinstance(v, float) else f"{v:,}"))
    sections = [
        ("Target: lead_days (3.1)", sec._md_table(t_tab) + "\n\n![lead_days KDE](figures/target_lead_days_kde.png)"),
        ("Outcome trends (3.3)", sec._md_table(tr) + "\n\n![trends](figures/outcome_trends.png)"),
        ("Numeric features vs lead_days (3.4)",
         sec._md_table(numeric[["feature", "n", "pearson", "spearman", "feature_missing_share", "feature_skewness"]])
         + "\n\n![scatter](figures/numeric_vs_lead_days.png)"),
        ("Categorical features vs lead_days (3.5)",
         "Rank correlation ratio per categorical feature: " + ", ".join(f"{k} {v:.4f}" for k, v in ratio.items())
         + ". Per-level medians, IQR and drop-first dummy correlations: categorical_feature_target_lead_days.csv."
         "\n\n![violins](figures/categorical_vs_lead_days.png)"),
        ("Missingness and outliers (3.8)", sec._md_table(col["quality"][["feature", "type", "missing_share",
                                                                         "share_outside_1_5_iqr", "share_outside_3_iqr", "vif", "vif_note"]])),
        ("Skewness of the log1p candidates (3.8, for s04 4.2)", sec._md_table(skew)),
    ]
    sec.review_pack(w, TASK, run_note, sections, rank, cuts, col)

    # Checks ------------------------------------------------------------------------------------
    w.check("no order on or after the test cutoff loaded", d["purchase_ts"].max() < cutoff, ids=("3.1", "3.3", "3.8"),
            detail=f"latest purchase {d['purchase_ts'].max()}, cutoff {cutoff}")
    w.check("all 24 contract predictors diagnosed against lead_days",
            set(numeric["feature"]) | set(cat.loc[cat["encoding"] != "numeric (plots only)", "feature"])
            == set(contract.PREDICTORS), ids=("3.4", "3.5"))
    w.check("importance_ranking has the 24 contract predictors and ends at cumulative share 1.0",
            len(rank) == 24 and set(rank["feature"]) == set(contract.PREDICTORS)
            and rank["cumulative_share"].iloc[-1] == 1.0 and rank["cumulative_share"].is_monotonic_increasing,
            ids=("3.8",), detail=f"{len(rank)} rows")
    w.check("ranking measure is the pre-registered one",
            p["features"]["selection"]["ranking"][TASK] == sec.MEASURE[TASK], ids=("3.8",))
    w.check("outcome trends show outcomes, not volume only",
            {"median_lead_days", "late_vs_promised_rate", "detractor_rate"} <= set(tr.columns), ids=("3.3",))
    w.check("review pack lists both cut points and every flagged group",
            all(str(k) for k in cuts.values()) and len(cuts) == 2, ids=("3.9",))

    # Evidence cards --------------------------------------------------------------------------------
    top = numeric.iloc[0]
    w.explain("3.1", done=f"lead_days profile on {prof['count']:,} pre-cutoff orders: median {prof['p50']:.2f}, "
              f"mean {prof['mean']:.2f}, SD {prof['sd']:.2f}, p99 {prof['p99']:.2f}, max {prof['max']:.2f} days; "
              f"skewness {prof['skewness']:.2f}, excess kurtosis {prof['kurtosis']:.2f}.",
              conclusion="Right-skewed target: supports the pre-registered log1p target (G-36).")
    w.explain("3.3", done=f"{len(tr)} purchase months; over the {len(trq)} months with at least "
              f"{sec.MIN_MONTH_ORDERS} orders: median lead time {trq['median_lead_days'].min():.1f} to "
              f"{trq['median_lead_days'].max():.1f} days, late-vs-promised rate {trq['late_vs_promised_rate'].min():.1%} "
              f"to {trq['late_vs_promised_rate'].max():.1%}, detractor rate {trq['detractor_rate'].min():.1%} to "
              f"{trq['detractor_rate'].max():.1%}; every month is in the table with its counts.",
              reasoning="Late is delivery after order_estimated_delivery_date, used here only as a description (G-35).")
    w.explain("3.4", done=f"{len(num)} numeric predictors: Pearson and Spearman with lead_days on the rows where the "
              f"feature is present, plus each feature's percentile profile; strongest |Spearman|: {top['feature']} "
              f"({top['spearman']:.3f}). Scatter panels use {PLOT_SAMPLE:,} random orders each (seed {seed}); "
              "log1p x-axis for the five log1p candidates (plot only).")
    w.explain("3.5", done="Four categorical predictors: per-level median, IQR and mean of lead_days, drop-first dummy "
              "correlations (reference level = first in sorted order), and one rank correlation ratio per feature; "
              "the three calendar fields are shown per level for the plots only and stay numeric.",
              reasoning="Spearman needs an ordered feature, so a nominal feature gets the rank correlation ratio "
                        "(square root of the Kruskal-Wallis epsilon-squared): the same 0-1 scale as |Spearman| on "
                        "the ranked target. Flagged for the team to confirm (decision 1).")
    w.explain("3.8", done=f"Ranking over the 24 contract predictors by {sec.MEASURE[TASK]} (rank correlation ratio for "
              f"the four categorical ones): top 5 {rank['feature'].head(5).tolist()}; cut points {cuts} (features "
              f"needed for each cumulative share). Missingness, IQR outliers, Pearson/Spearman matrix and VIF on "
              f"{col['vif_rows']:,} complete rows; flagged groups: {[g['features'] for g in col['groups']]}; identical "
              f"columns: {col['duplicates']}.")
    w.explain("3.9", done="eda_review_pack.md lists every table and figure above, the ranking with both cut points, "
              "the flagged collinear groups and the YAML block the team fills in spec/human_decisions.yaml.",
              conclusion="Stop: s04 waits for the team's threshold and collinearity decisions (G-31).")
    w.finish(seed=seed)


if __name__ == "__main__":
    main()
