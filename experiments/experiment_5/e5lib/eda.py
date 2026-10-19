"""EDA statistics shared by the two s03 nodes (blueprint spec/blueprints/s03_eda.md).

Written for Experiment 5 (Milestone 2's experiment_3/run_eda_outliers.py was read as reference
only). Every function is label-aware only where the blueprint asks for a target diagnostic; the
collinearity and missingness summaries use the predictors alone. Missing values are dropped per
feature (pairwise), and every result reports the rows it used.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.feature_selection import mutual_info_classif
from sklearn.metrics import roc_auc_score

PERCENTILES = (1, 5, 25, 50, 75, 95, 99)
DISCRETE_MAX_LEVELS = 30  # numeric features with at most this many values use the discrete overlap and MI


def profile(x: pd.Series) -> dict:
    """count, mean, SD, min, 1/5/25/50/75/95/99%, max, skewness, kurtosis (excess), missing share."""
    v = x.dropna().astype(float)
    out = {"count": int(len(v)), "missing_share": float(x.isna().mean()), "mean": float(v.mean()),
           "sd": float(v.std()), "min": float(v.min())}
    out.update({f"p{q}": float(np.percentile(v, q)) for q in PERCENTILES})
    out.update({"max": float(v.max()), "skewness": float(stats.skew(v, bias=False)),
                "kurtosis": float(stats.kurtosis(v, bias=False))})
    return out


def is_discrete(x: pd.Series) -> bool:
    return x.dropna().nunique() <= DISCRETE_MAX_LEVELS


def correlations(x: pd.Series, y: pd.Series) -> dict:
    """Pearson and Spearman on the rows where both are present."""
    m = x.notna() & y.notna()
    xs, ys = x[m].astype(float), y[m].astype(float)
    if xs.nunique() < 2:
        return {"n": int(m.sum()), "pearson": np.nan, "spearman": np.nan}
    return {"n": int(m.sum()), "pearson": float(stats.pearsonr(xs, ys)[0]),
            "spearman": float(stats.spearmanr(xs, ys)[0])}


def rank_correlation_ratio(cat: pd.Series, y: pd.Series) -> dict:
    """Spearman-scale association of a nominal feature with a numeric target.

    The target is ranked, each level is replaced by the mean target rank of its rows, and the
    Pearson correlation of the ranks with those level means is returned. This equals the square
    root of the Kruskal-Wallis epsilon-squared (the correlation ratio on ranks), so it is 0 when
    every level has the same rank distribution and is on the same 0-1 scale as |Spearman|.
    """
    m = cat.notna() & y.notna()
    r = stats.rankdata(y[m].astype(float))
    level_mean = pd.Series(r, index=cat[m].index).groupby(cat[m].astype(str)).transform("mean")
    if level_mean.nunique() < 2:
        return {"n": int(m.sum()), "value": 0.0}
    return {"n": int(m.sum()), "value": float(abs(np.corrcoef(r, level_mean.to_numpy())[0, 1]))}


def overlap(x: pd.Series, y: pd.Series, log1p: bool = False, grid: int = 512) -> dict:
    """Overlap coefficient of the class-conditional distributions (100% = no signal).

    Continuous features: Gaussian KDE (Scott bandwidth) per class on a common grid; the
    coefficient is the integral of min(f0, f1). Features with at most DISCRETE_MAX_LEVELS values
    use the class-conditional frequencies (sum of min(p0, p1)), because a KDE smears a count.
    log1p=True evaluates the KDE on the log1p scale; the coefficient is invariant under a monotone
    transform, the log scale only gives the kernel a less skewed shape.
    """
    m = x.notna() & y.notna()
    xs, ys = x[m].astype(float), y[m].astype(int)
    if is_discrete(xs):
        p = pd.crosstab(xs, ys, normalize="columns")
        curve = pd.DataFrame({"x": p.index.astype(float), "class_0": p[0].to_numpy(), "class_1": p[1].to_numpy()})
        return {"n": int(m.sum()), "overlap": float(np.minimum(p[0], p[1]).sum()), "method": "discrete frequencies",
                "curve": curve}
    v = np.log1p(xs) if log1p else xs
    lo, hi = np.percentile(v, 0.1), np.percentile(v, 99.9)
    g = np.linspace(lo, hi, grid)
    f0, f1 = (stats.gaussian_kde(v[ys == k])(g) for k in (0, 1))
    area = np.trapezoid(np.minimum(f0, f1), g) / np.trapezoid(0.5 * (f0 + f1), g)
    curve = pd.DataFrame({"x": g, "class_0": f0, "class_1": f1})
    return {"n": int(m.sum()), "overlap": float(area), "method": "KDE (log1p scale)" if log1p else "KDE",
            "curve": curve}


def auc(x: pd.Series, y: pd.Series) -> dict:
    m = x.notna() & y.notna()
    a = float(roc_auc_score(y[m].astype(int), x[m].astype(float)))
    return {"n": int(m.sum()), "roc_auc": a, "roc_auc_symmetric": max(a, 1 - a),
            "direction": "higher value, more detractors" if a >= 0.5 else "lower value, more detractors"}


def mutual_information(x: pd.Series, y: pd.Series, discrete: bool, seed: int) -> dict:
    """mutual_info_classif on the rows where x is present (nats); categorical x is label-coded."""
    m = x.notna() & y.notna()
    xs = x[m]
    if xs.dtype == object or str(xs.dtype) in ("string", "str", "category"):
        xs = pd.Series(pd.factorize(xs.astype(str), sort=True)[0], index=xs.index)
        discrete = True
    elif discrete:  # integer codes, so the contingency estimator sees labels, not floats
        xs = pd.Series(pd.factorize(xs, sort=True)[0], index=xs.index)
    mi = mutual_info_classif(xs.to_numpy(float).reshape(-1, 1), y[m].astype(int).to_numpy(),
                             discrete_features=[discrete], random_state=seed)[0]
    return {"n": int(m.sum()), "mutual_information": float(mi),
            "estimator": "discrete (contingency)" if discrete else "continuous (k-NN, k=3)"}


def one_hot_correlations(cat: pd.Series, y: pd.Series) -> pd.DataFrame:
    """Per level: n, share, target median/IQR/mean and the Pearson correlation of its drop-first dummy."""
    m = cat.notna() & y.notna()
    c, t = cat[m].astype(str), y[m].astype(float)
    levels = sorted(c.unique())
    rows = []
    for i, lev in enumerate(levels):
        d = (c == lev).astype(float)
        q1, med, q3 = np.percentile(t[d == 1], (25, 50, 75))
        rows.append({"level": lev, "n": int(d.sum()), "share": float(d.mean()), "target_median": float(med),
                     "target_q1": float(q1), "target_q3": float(q3), "target_mean": float(t[d == 1].mean()),
                     "dummy": "dropped (reference)" if i == 0 else "kept",
                     "dummy_correlation": np.nan if i == 0 or d.nunique() < 2 else float(np.corrcoef(d, t)[0, 1])})
    return pd.DataFrame(rows)


def vif(df: pd.DataFrame) -> pd.Series:
    """Variance inflation factor per column on complete rows: 1 / (1 - R^2) of each column on the rest.

    Least squares per column (not the inverse correlation matrix), so an exact duplicate gives
    an infinite VIF instead of a singular-matrix error. Columns constant on the complete rows get
    NaN (no variance to inflate) and are left out of the other columns' regressions.
    """
    x = df.dropna().astype(float)
    sd = x.std()
    out = {}
    for col in x.columns:
        if sd[col] == 0:
            out[col] = np.nan
            continue
        others = [c for c in x.columns if c != col and sd[c] > 0]
        a = np.column_stack([np.ones(len(x))] + [((x[c] - x[c].mean()) / sd[c]).to_numpy() for c in others])
        b = ((x[col] - x[col].mean()) / sd[col]).to_numpy()
        coef, *_ = np.linalg.lstsq(a, b, rcond=None)
        resid = b - a @ coef
        r2 = 1 - float(resid @ resid) / float(b @ b)
        out[col] = np.inf if r2 >= 1 - 1e-12 else 1.0 / (1.0 - r2)
    return pd.Series(out)


def collinear_groups(pearson: pd.DataFrame, spearman: pd.DataFrame, vifs: pd.Series,
                     corr_above: float, vif_above: float,
                     identical: list[tuple[str, str]] = ()) -> tuple[pd.DataFrame, list[dict]]:
    """Flagged pairs (|Pearson| or |Spearman| above the cut-off) and groups.

    Groups are the connected components of the flagged-pair graph. A feature whose VIF is above
    the cut-off but has no flagged pair forms its own group, listed with its three most correlated
    partners, so the team sees every flag. Identical pairs are listed but not grouped: the s04
    duplicate rule drops them without a team decision. Nothing is dropped here (s04 4.3, G-26).
    """
    same = {frozenset(x) for x in identical}
    cols = list(pearson.columns)
    pairs = []
    for i, a in enumerate(cols):
        for b in cols[i + 1:]:
            p, s = pearson.loc[a, b], spearman.loc[a, b]
            if abs(p) > corr_above or abs(s) > corr_above:
                pairs.append({"feature_a": a, "feature_b": b, "pearson": float(p), "spearman": float(s),
                              "identical": frozenset((a, b)) in same})
    parent = {c: c for c in cols}

    def find(c):
        while parent[c] != c:
            c = parent[c]
        return c
    for pr in pairs:
        if pr["identical"]:
            continue
        parent[find(pr["feature_a"])] = find(pr["feature_b"])
    comp: dict[str, list[str]] = {}
    for c in cols:
        comp.setdefault(find(c), []).append(c)
    groups = []
    for members in comp.values():
        flagged_vif = [c for c in members if vifs.get(c, 0) > vif_above]
        if len(members) > 1:
            groups.append({"features": members, "reason": "pairwise correlation above cut-off",
                           "vif": {c: float(vifs.get(c, np.nan)) for c in members}})
        elif flagged_vif:
            c = members[0]
            partners = pearson[c].drop(c).abs().sort_values(ascending=False).head(3)
            groups.append({"features": [c], "reason": "VIF above cut-off without a flagged pair",
                           "vif": {c: float(vifs[c])},
                           "top_partners": {k: float(pearson.loc[c, k]) for k in partners.index}})
    return pd.DataFrame(pairs, columns=["feature_a", "feature_b", "pearson", "spearman", "identical"]), groups


def cumulative_ranking(values: dict[str, float], measure: str) -> pd.DataFrame:
    """Rank features by value (descending, ties by name); share and cumulative share of the total."""
    df = pd.DataFrame({"feature": list(values), "value": [max(float(v), 0.0) for v in values.values()]})
    df = df.sort_values(["value", "feature"], ascending=[False, True], kind="mergesort").reset_index(drop=True)
    total = df["value"].sum()
    df.insert(1, "measure", measure)
    df["rank"] = np.arange(1, len(df) + 1)
    df["share"] = df["value"] / total
    df["cumulative_share"] = df["share"].cumsum().clip(upper=1.0)
    df.loc[df.index[-1], "cumulative_share"] = 1.0  # exact end point (float sums)
    return df


def cut_point(ranking: pd.DataFrame, threshold: float) -> int:
    """Number of top-ranked features needed for the cumulative share to reach the threshold."""
    return int((ranking["cumulative_share"] < threshold - 1e-12).sum() + 1)


def iqr_outliers(x: pd.Series) -> dict:
    v = x.dropna().astype(float)
    q1, q3 = np.percentile(v, (25, 75))
    iqr = q3 - q1
    return {"q1": float(q1), "q3": float(q3), "iqr": float(iqr),
            "share_outside_1_5_iqr": float(((v < q1 - 1.5 * iqr) | (v > q3 + 1.5 * iqr)).mean()),
            "share_outside_3_iqr": float(((v < q1 - 3 * iqr) | (v > q3 + 3 * iqr)).mean())}


def json_safe(obj):
    """NaN -> None and +-inf -> "inf"/"-inf", recursively, so eda_summary.json is strict JSON."""
    if isinstance(obj, dict):
        return {str(k): json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_safe(v) for v in obj]
    if isinstance(obj, (float, np.floating)):
        f = float(obj)
        return None if np.isnan(f) else ("inf" if f == np.inf else "-inf" if f == -np.inf else f)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    return obj
