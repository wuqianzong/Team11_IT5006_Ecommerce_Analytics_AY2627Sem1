"""s03 statistics in e5lib/eda.py: overlap, rank correlation ratio, VIF, ranking and cut points."""
import numpy as np
import pandas as pd


def test_overlap_identical_and_separated():
    from e5lib.eda import overlap
    rng = np.random.default_rng(0)
    x = pd.Series(rng.normal(size=4000))
    y = pd.Series(np.r_[np.zeros(2000), np.ones(2000)])
    assert overlap(x, y)["overlap"] > 0.9  # same distribution in both classes
    sep = pd.Series(np.r_[rng.normal(0, 1, 2000), rng.normal(50, 1, 2000)])
    assert overlap(sep, y)["overlap"] < 0.01
    counts = pd.Series(np.r_[np.ones(2000), np.full(2000, 2.0)])
    r = overlap(counts, y)
    assert r["method"] == "discrete frequencies" and r["overlap"] == 0.0


def test_rank_correlation_ratio_zero_and_one():
    from e5lib.eda import rank_correlation_ratio
    cat = pd.Series(["a", "b"] * 50)
    assert rank_correlation_ratio(cat, pd.Series(np.arange(100.0)))["value"] < 0.05
    y = pd.Series(np.where(cat == "a", 1.0, 2.0) + np.arange(100) * 1e-6)
    assert rank_correlation_ratio(cat, y)["value"] > 0.85


def test_vif_duplicate_is_infinite_and_constant_is_nan():
    from e5lib.eda import vif
    rng = np.random.default_rng(1)
    a = rng.normal(size=300)
    df = pd.DataFrame({"a": a, "b": a, "c": rng.normal(size=300), "k": np.ones(300)})
    v = vif(df)
    assert np.isinf(v["a"]) and np.isinf(v["b"]) and v["c"] < 1.1 and np.isnan(v["k"])


def test_cumulative_ranking_and_cut_points():
    from e5lib.eda import cumulative_ranking, cut_point
    r = cumulative_ranking({"x": 0.5, "y": 0.3, "z": 0.15, "w": 0.05}, "m")
    assert list(r["feature"]) == ["x", "y", "z", "w"] and r["cumulative_share"].iloc[-1] == 1.0
    assert cut_point(r, 0.95) == 3 and cut_point(r, 0.99) == 4 and cut_point(r, 0.8) == 2


def test_identical_pair_is_not_a_team_group():
    from e5lib.eda import collinear_groups
    cols = ["a", "b", "c", "d"]
    corr = pd.DataFrame(np.eye(4), index=cols, columns=cols)
    corr.loc["a", "b"] = corr.loc["b", "a"] = 1.0
    corr.loc["c", "d"] = corr.loc["d", "c"] = 0.95
    pairs, groups = collinear_groups(corr, corr, pd.Series(1.0, index=cols), 0.9, 10, identical=[("a", "b")])
    assert len(pairs) == 2 and pairs["identical"].tolist() == [True, False]
    assert [g["features"] for g in groups] == [["c", "d"]]
