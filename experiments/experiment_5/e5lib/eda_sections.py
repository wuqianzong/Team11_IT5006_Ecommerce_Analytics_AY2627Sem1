"""s03 output sections shared by the regression and classification nodes.

Each function takes the node's Writer and its pre-cutoff development rows, writes its tables and
figures with their solution IDs, and returns the values the evidence cards and the review pack
quote. The task-specific diagnostics (3.1/3.4/3.5 and 3.2/3.6/3.7) stay in each node's run.py.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from . import contract, eda  # noqa: E402

TARGET = {"regression": "lead_days", "classification": "is_detractor"}
MEASURE = {"regression": "absolute Spearman", "classification": "mutual information"}
MIN_MONTH_ORDERS = 100  # months quoted in card ranges; the trend table and figure keep every month


def load_dates(d: pd.DataFrame) -> pd.DataFrame:
    for c in ("order_estimated_delivery_date", "lead_label_ts", "review_label_ts"):
        d[c] = pd.to_datetime(d[c])
    return d


# ---------------------------------------------------------------------------------------------
# 3.3 Outcome trends
# ---------------------------------------------------------------------------------------------
def trends(w, d: pd.DataFrame, task: str) -> pd.DataFrame:
    """Per purchase month: orders, median lead time, late-vs-promised rate, detractor rate, with counts."""
    m = d["purchase_ts"].dt.to_period("M").astype(str)
    has_lead = d["lead_days"].notna()
    late = (d["lead_label_ts"] > d["order_estimated_delivery_date"]).where(has_lead)
    g = pd.DataFrame({"month": m, "lead": d["lead_days"], "late": late.astype(float),
                      "det": d["is_detractor"].astype(float)}).groupby("month")
    t = pd.DataFrame({"orders": g.size(), "orders_with_lead_time": g["lead"].count(),
                      "median_lead_days": g["lead"].median(), "late_vs_promised_rate": g["late"].mean(),
                      "orders_with_review": g["det"].count(), "detractor_rate": g["det"].mean()}).reset_index()
    w.table("outcome_trends", t, ids=("3.3",))

    fig, ax = plt.subplots(4, 1, figsize=(11, 10), sharex=True)
    x = np.arange(len(t))
    ax[0].bar(x, t["orders"], color="0.6")
    ax[0].set_ylabel("orders")
    ax[1].plot(x, t["median_lead_days"], marker="o")
    ax[1].set_ylabel("median lead days")
    ax[2].plot(x, t["late_vs_promised_rate"], marker="o", color="tab:red")
    ax[2].set_ylabel("late vs promised")
    ax[3].plot(x, t["detractor_rate"], marker="o", color="tab:purple")
    ax[3].set_ylabel("detractor rate")
    ax[3].set_xticks(x, t["month"], rotation=60, fontsize=7)
    fig.suptitle(f"Outcome trends by purchase month ({task} population, pre-cutoff orders)")
    fig.tight_layout()
    w.figure("outcome_trends", fig, t, ids=("3.3",), title="Outcome trends by purchase month")
    plt.close(fig)
    return t


# ---------------------------------------------------------------------------------------------
# 3.8 Missingness, outliers, collinearity among raw numeric features (label-free)
# ---------------------------------------------------------------------------------------------
def quality_and_collinearity(w, d: pd.DataFrame, p: dict) -> dict:
    num = list(contract.numeric())
    col = p["features"]["collinearity"]
    corr_above, vif_above = float(col["abs_correlation_above"]), float(col["vif_above"])
    pearson, spearman = d[num].corr(), d[num].corr(method="spearman")
    vifs = eda.vif(d[num])
    constant = [c for c in contract.PREDICTORS if d[c].nunique(dropna=False) <= 1]
    duplicates = [(a, b) for i, a in enumerate(contract.PREDICTORS) for b in contract.PREDICTORS[i + 1:]
                  if d[a].equals(d[b])]
    pairs, groups = eda.collinear_groups(pearson, spearman, vifs, corr_above, vif_above, duplicates)

    rows = []
    for c in contract.PREDICTORS:
        r = {"feature": c, "type": "categorical" if c in contract.CATEGORICAL else "numeric",
             "missing_share": float(d[c].isna().mean()), "distinct_values": int(d[c].nunique())}
        if c in num:
            r.update(eda.iqr_outliers(d[c]))
            r["vif"] = float(vifs[c])
            r["vif_note"] = "constant on the complete rows" if np.isnan(vifs[c]) else ""
        rows.append(r)
    quality = pd.DataFrame(rows)
    w.table("feature_quality", quality, ids=("3.8",))
    w.table("collinear_pairs", pairs, ids=("3.8",))
    corr_long = pearson.stack().rename("pearson").to_frame().join(spearman.stack().rename("spearman"))
    corr_long.index.names = ["feature_a", "feature_b"]
    w.table("numeric_correlations", corr_long.reset_index(), ids=("3.8",))

    fig, ax = plt.subplots(figsize=(10, 8.5))
    im = ax.imshow(spearman.to_numpy(), vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_xticks(range(len(num)), num, rotation=90, fontsize=7)
    ax.set_yticks(range(len(num)), num, fontsize=7)
    for i in range(len(num)):
        for j in range(len(num)):
            v = spearman.iat[i, j]
            if i != j and abs(v) >= 0.5:
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6)
    fig.colorbar(im, ax=ax, shrink=0.7, label="Spearman")
    ax.set_title(f"Spearman correlation among the {len(num)} numeric contract predictors (|r| >= 0.5 labelled)")
    w.figure("numeric_correlation_heatmap", fig, corr_long.reset_index(), ids=("3.8",),
             title="Correlation among raw numeric features")
    plt.close(fig)
    return {"pairs": pairs, "groups": groups, "quality": quality, "constant": constant, "duplicates": duplicates,
            "corr_above": corr_above, "vif_above": vif_above, "vif_rows": int(len(d[num].dropna()))}


def log_candidate_skewness(d: pd.DataFrame, p: dict) -> pd.DataFrame:
    thr = float(p["features"]["log1p"]["skewness_threshold"])
    rows = []
    for c in p["features"]["log1p"]["candidates"]:
        s = eda.profile(d[c])["skewness"]
        rows.append({"feature": c, "skewness": s, "threshold": thr, "log1p": bool(s > thr)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------------------------
# 3.8 Importance ranking with cumulative-share cut points
# ---------------------------------------------------------------------------------------------
def ranking(w, values: dict[str, float], task: str, p: dict, method: dict[str, str]) -> tuple[pd.DataFrame, dict]:
    r = eda.cumulative_ranking(values, MEASURE[task])
    r["method"] = r["feature"].map(method)
    r["type"] = np.where(r["feature"].isin(contract.CATEGORICAL), "categorical", "numeric")
    w.table("importance_ranking", r, ids=("3.8",))
    options = [float(x) for x in p["features"]["selection"]["cumulative_threshold_options"]]
    cuts = {f"{t:.2f}": eda.cut_point(r, t) for t in options}

    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = r["rank"].to_numpy()
    ax.bar(x, r["share"], color="0.75", label="share of total")
    ax.plot(x, r["cumulative_share"], marker="o", color="tab:blue", label="cumulative share")
    for (t, k), colr in zip(cuts.items(), ("tab:green", "tab:orange")):
        ax.axhline(float(t), color=colr, ls="--", lw=1)
        ax.axvline(k, color=colr, ls=":", lw=1)
        ax.text(k + 0.2, float(t) - 0.06, f"{float(t):.0%}: top {k}", color=colr, fontsize=8)
    ax.set_xticks(x, r["feature"], rotation=75, fontsize=7, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("share")
    ax.set_title(f"{task}: cumulative importance ({MEASURE[task]}) over the 24 contract predictors")
    ax.legend(loc="center right", fontsize=8)
    fig.tight_layout()
    w.figure("cumulative_importance", fig, r, ids=("3.8", "3.9"), title="Cumulative importance with cut points")
    plt.close(fig)
    return r, cuts


# ---------------------------------------------------------------------------------------------
# candidate_rationale.csv: finding -> evidence -> change it motivates -> stage that tests it
# ---------------------------------------------------------------------------------------------
def rationale(w, task: str, skew: pd.DataFrame, col: dict, rank: pd.DataFrame, cuts: dict,
              extra: list[dict]) -> pd.DataFrame:
    rows = []
    for s in skew.itertuples():
        rows.append({"finding": f"{s.feature} pre-cutoff skewness {s.skewness:.2f} "
                                f"({'above' if s.log1p else 'not above'} {s.threshold:g})",
                     "evidence": "eda_summary.json:log1p_candidates",
                     "change_it_motivates": f"log1p on {s.feature}" if s.log1p else f"no log1p on {s.feature}",
                     "stage_that_tests_it": "s04 4.2 (applied), s06 (fitted inside folds)"})
    for c in col["constant"]:
        rows.append({"finding": f"{c} is constant on pre-cutoff orders", "evidence": "feature_quality.csv:distinct_values",
                     "change_it_motivates": f"drop {c} automatically", "stage_that_tests_it": "s04 4.3"})
    for a, b in col["duplicates"]:
        rows.append({"finding": f"{a} and {b} are identical on every pre-cutoff order",
                     "evidence": "collinear_pairs.csv", "change_it_motivates": f"drop one of {a}, {b} automatically "
                     "(duplicate rule)", "stage_that_tests_it": "s04 4.3"})
    for g in col["groups"]:
        rows.append({"finding": f"collinear group {', '.join(g['features'])} ({g['reason']})",
                     "evidence": "collinear_pairs.csv, feature_quality.csv:vif",
                     "change_it_motivates": "team decides which feature to drop, with rationale (human_decisions.yaml)",
                     "stage_that_tests_it": "s04 4.3"})
    for t, k in cuts.items():
        rows.append({"finding": f"top {k} of 24 features reach {float(t):.0%} of total {MEASURE[task]}",
                     "evidence": "importance_ranking.csv:cumulative_share",
                     "change_it_motivates": f"selected set = top {k} if the team picks {float(t):.0%}",
                     "stage_that_tests_it": "s04 4.4 (threshold fixed before fitting), s06"})
    rows += extra
    df = pd.DataFrame(rows, columns=["finding", "evidence", "change_it_motivates", "stage_that_tests_it"])
    w.table("candidate_rationale", df, ids=("3.8",))
    return df


# ---------------------------------------------------------------------------------------------
# 3.9 Human gate: eda_review_pack.md
# ---------------------------------------------------------------------------------------------
def _md_table(df: pd.DataFrame, floatfmt: str = "{:.4f}") -> str:
    def fmt(v):
        if isinstance(v, float):
            return "" if np.isnan(v) else ("inf" if np.isinf(v) else floatfmt.format(v))
        return str(v)
    head = "| " + " | ".join(df.columns) + " |\n| " + " | ".join("---" for _ in df.columns) + " |\n"
    return head + "\n".join("| " + " | ".join(fmt(v) for v in r) + " |" for r in df.itertuples(index=False))


def review_pack(w, task: str, run_note: str, sections: list[tuple[str, str]], rank: pd.DataFrame,
                cuts: dict, col: dict) -> str:
    lines = [f"# EDA review pack: s03_eda/{task}", "",
             "Human gate before s04 (G-31). Every table and figure of this node is listed below; the team records "
             "its decisions in `spec/human_decisions.yaml` (section `s03_to_s04." + task + "`), logged in "
             "CHANGELOG.md. s04 does not run until both are recorded.", "", run_note, ""]
    for title, body in sections:
        lines += [f"## {title}", "", body, ""]
    lines += ["## Importance ranking (3.8)", "", f"Measure: {MEASURE[task]}. All 24 contract predictors.", "",
              _md_table(rank[["rank", "feature", "type", "method", "value", "share", "cumulative_share"]]), "",
              "![cumulative importance](figures/cumulative_importance.png)", ""]
    lines += ["| Threshold option | Features kept (top k) | Features kept |", "| --- | --- | --- |"]
    for t, k in cuts.items():
        lines.append(f"| {float(t):.0%} | {k} | {', '.join(rank['feature'].head(k))} |")
    lines += ["", "## Collinearity among raw numeric features (3.8)", "",
              f"Cut-offs from protocol.yaml: |correlation| > {col['corr_above']:g} (Pearson or Spearman) or "
              f"VIF > {col['vif_above']:g}; VIF on {col['vif_rows']:,} complete rows (a column constant on those rows "
              "has no VIF). Nothing is dropped in s03.", ""]
    if col["duplicates"]:
        lines.append("Identical columns (dropped automatically in s04 4.3, no team decision needed): "
                     + "; ".join(f"{a} = {b}" for a, b in col["duplicates"]) + ".")
        lines.append("")
    if col["constant"]:
        lines += ["Constant columns (dropped automatically in s04 4.3): " + ", ".join(col["constant"]) + ".", ""]
    if col["groups"]:
        lines += ["| Flagged group | Reason | VIF |", "| --- | --- | --- |"]
        for g in col["groups"]:
            vif_txt = ", ".join(f"{k} {'inf' if np.isinf(v) else f'{v:.1f}'}" for k, v in g["vif"].items())
            lines.append(f"| {', '.join(g['features'])} | {g['reason']} | {vif_txt} |")
    else:
        lines.append("No group needs a team decision: no pair of distinct columns above the correlation "
                     "cut-off and no VIF above the VIF cut-off.")
    lines += ["", _md_table(col["pairs"]) if len(col["pairs"]) else "No pair above the cut-off.", "",
              "![correlation heatmap](figures/numeric_correlation_heatmap.png)", "",
              "## Decisions for the team (record in spec/human_decisions.yaml)", "",
              "```yaml", "s03_to_s04:", f"  {task}:",
              "    cumulative_importance_threshold: 0.95   # or 0.99",
              "    collinearity_drops:"]
    for g in col["groups"]:
        lines.append(f"      - {{group: [{', '.join(g['features'])}], drop: <feature>, rationale: \"...\", "
                     "decided_by: <name>, date: YYYY-MM-DD}")
    if contract.screening(task):
        lines.append(f"    adopted_candidates: []   # any of {list(contract.screening(task))} (G-68), with rationale")
    lines += ["```", ""]
    text = "\n".join(lines)
    w.text("eda_review_pack.md", text, ids=("3.9",))
    return text


__all__ = ["TARGET", "MEASURE", "load_dates", "trends", "quality_and_collinearity", "log_candidate_skewness",
           "ranking", "rationale", "review_pack"]


# ---------------------------------------------------------------------------------------------
# 3.10-3.13 Candidate screen (G-68, G-69): screening columns, classification only
# ---------------------------------------------------------------------------------------------
def screen_group(w, d: pd.DataFrame, y: pd.Series, names: list[str], sid: str, fig_name: str, title: str,
                 seed: int, num: list[str], task: str = "classification") -> tuple[pd.DataFrame, pd.DataFrame]:
    """Diagnostics of one candidate group against the binary target, with a figure.

    Numeric candidates: the 3.6 measures (overlap, ROC-AUC, mutual information), skewness and the most
    correlated numeric predictor. Categorical candidates: mutual information (discrete), overlap of the
    class-conditional level frequencies and a per-level detractor-rate table; no ROC-AUC (a nominal
    feature has no order).
    """
    meta = contract.SCREENING_CANDIDATES[task]
    rows, curves, levels = [], [], []
    for c in names:
        cat = meta[c]["kind"] == "categorical"
        if cat:
            codes = pd.Series(pd.factorize(d[c].astype(str), sort=True)[0], index=d.index).astype(float)
            ov = eda.overlap(codes, y)
            m = eda.mutual_information(d[c], y, discrete=True, seed=seed)
            g = pd.DataFrame({"level": d[c].astype(str), "y": y}).groupby("level")["y"]
            lv = pd.DataFrame({"n": g.size(), "detractors": g.sum(), "detractor_rate": g.mean()}).reset_index()
            levels.append(lv.assign(feature=c, share=lv["n"] / len(d)))
            rows.append({"feature": c, "kind": "categorical", "n": m["n"], "missing_share": float(d[c].isna().mean()),
                         "levels": int(d[c].nunique()), "overlap_coefficient": ov["overlap"],
                         "overlap_method": "discrete frequencies of the levels", "roc_auc": np.nan,
                         "direction": "", "mutual_information": m["mutual_information"], "mi_estimator": m["estimator"],
                         "skewness": np.nan, "planned_transform": meta[c]["transform"]})
        else:
            logged = "log1p" in meta[c]["transform"].split(";")[0] and d[c].min() >= 0
            ov = eda.overlap(d[c], y, log1p=logged)
            a = eda.auc(d[c], y)
            m = eda.mutual_information(d[c], y, discrete=eda.is_discrete(d[c]), seed=seed)
            pr = eda.profile(d[c])
            cor = pd.Series({n: d[c].corr(d[n], method="spearman") for n in num})
            top = cor.abs().idxmax()
            rows.append({"feature": c, "kind": "numeric", "n": ov["n"], "missing_share": pr["missing_share"],
                         "levels": int(d[c].nunique()), "overlap_coefficient": ov["overlap"],
                         "overlap_method": ov["method"], "roc_auc": a["roc_auc"], "direction": a["direction"],
                         "mutual_information": m["mutual_information"], "mi_estimator": m["estimator"],
                         "skewness": pr["skewness"], "planned_transform": meta[c]["transform"],
                         "most_correlated_predictor": top, "spearman_with_it": float(cor[top]),
                         "mean_class_0": float(d.loc[y == 0, c].mean()), "mean_class_1": float(d.loc[y == 1, c].mean())})
            curves.append(ov["curve"].assign(feature=c, method=ov["method"]))
    table = pd.DataFrame(rows)
    level_table = pd.concat(levels, ignore_index=True)[["feature", "level", "n", "share", "detractors", "detractor_rate"]] \
        if levels else pd.DataFrame(columns=["feature", "level", "n", "share", "detractors", "detractor_rate"])

    fig, axes = plt.subplots(1, len(names), figsize=(5 * len(names), 4.6), squeeze=False)
    prevalence = float(y.mean())
    for ax, c in zip(axes[0], names):
        r = table.set_index("feature").loc[c]
        if r["kind"] == "categorical":
            lv = level_table[level_table["feature"] == c].sort_values("n", ascending=False, kind="mergesort").head(15)
            ax.bar(range(len(lv)), lv["detractor_rate"], color="tab:red", alpha=0.7)
            ax.axhline(prevalence, color="k", ls="--", lw=1)
            ax.set_xticks(range(len(lv)), lv["level"], rotation=60, fontsize=6, ha="right")
            ax.set_ylabel("detractor rate", fontsize=7)
            ax.set_title(f"{c} ({int(r['levels'])} levels{', top 15 shown' if r['levels'] > 15 else ''})\n"
                         f"MI {r['mutual_information']:.4f}, overlap {r['overlap_coefficient']:.1%}", fontsize=8)
        else:
            cv = curves[[x["feature"].iat[0] for x in curves].index(c)]
            if r["overlap_method"] == "discrete frequencies":
                wdt = 0.4 * (np.min(np.diff(cv["x"])) if len(cv) > 1 else 1.0)
                ax.bar(cv["x"] - wdt / 2, cv["class_0"], width=wdt, color="0.6", label="normal")
                ax.bar(cv["x"] + wdt / 2, cv["class_1"], width=wdt, color="tab:red", label="detractor")
            else:
                ax.plot(cv["x"], cv["class_0"], color="0.4", label="normal")
                ax.plot(cv["x"], cv["class_1"], color="tab:red", label="detractor")
                ax.fill_between(cv["x"], np.minimum(cv["class_0"], cv["class_1"]), color="tab:purple", alpha=0.2)
            ax.set_xlabel(f"log1p({c})" if str(r["overlap_method"]).endswith("(log1p scale)") else c, fontsize=7)
            ax.set_title(f"{c}\noverlap {r['overlap_coefficient']:.1%}, ROC-AUC {r['roc_auc']:.3f}", fontsize=8)
            ax.legend(fontsize=6)
        ax.tick_params(labelsize=6)
    fig.suptitle(title, y=1.03)
    fig.tight_layout()
    side = pd.concat(curves, ignore_index=True) if curves else level_table
    w.figure(fig_name, fig, side, ids=(sid,), title=title)
    plt.close(fig)
    return table, level_table
