"""s08 selection helpers: grid-edge flag, the empirical cost minimum and the threshold table."""
import numpy as np

GRIDS = {"ridge_alpha": [0.01, 1, 100], "logistic_C": [0.1, 1], "class_weight": [None, "balanced"],
         "tree": {"max_depth": [4, 8, 12], "min_samples_leaf": [20, 200]},
         "forest": {"max_depth": [8, 10], "min_samples_leaf": [50], "n_estimators": 200, "max_features": "sqrt"}}


def test_grid_edge_flags_only_the_ends_of_a_numeric_grid():
    from e5lib.selection import grid_edge
    assert grid_edge("regression", "tree", {"params": {"max_depth": 8, "min_samples_leaf": 200}}, GRIDS) == "min_samples_leaf=200"
    assert grid_edge("regression", "tree", {"params": {"max_depth": 12, "min_samples_leaf": 20}}, GRIDS) == "max_depth=12; min_samples_leaf=20"
    assert grid_edge("regression", "linear", {"params": {"alpha": 1}}, GRIDS) == "none"
    assert grid_edge("regression", "tree", {"params": {}}, GRIDS).startswith("plain s06 model")
    assert grid_edge("regression", "dummy", {}, GRIDS).startswith("not a grid configuration")


def test_empirical_cost_minimum_and_ties_to_the_higher_threshold():
    from e5lib.selection import empirical_cost_minimum
    y = np.array([1, 0, 1, 0, 0, 0])
    p = np.array([0.9, 0.8, 0.6, 0.3, 0.2, 0.1])
    # cost 5*FN + FP: t=0.9 -> 5; t=0.8 -> 6; t=0.6 -> 1; lower thresholds add false alarms
    assert empirical_cost_minimum(y, p, 5, 1) == 0.6
    # equal costs at 0.6 and 0.3 when FP is free: the higher threshold wins
    assert empirical_cost_minimum(y, p, 5, 0) == 0.6
    # alerts never pay off: no alerts
    assert np.isinf(empirical_cost_minimum(np.array([1, 0, 0]), np.array([0.1, 0.9, 0.8]), 1, 5))


def test_threshold_rows_counts_and_marginal_trade_off():
    from e5lib.selection import threshold_rows
    y = np.array([1, 0, 1, 0, 0, 0])
    p = np.array([0.9, 0.8, 0.6, 0.3, 0.2, 0.1])
    t = threshold_rows(y, p, {"no alerts": float("inf"), "a": 0.85, "b": 0.5, "c": 0.15}, days=2, c_fn=5, c_fp=1)
    assert list(t["candidate"]) == ["no alerts", "a", "b", "c"]
    assert list(t["alerts"]) == [0, 1, 3, 5] and list(t["cost"]) == [10, 5, 1, 3]
    assert t.loc[1, "alerts_per_day"] == 0.5 and t.loc[2, "precision"] == 2 / 3
    # a -> b: one extra detractor for one extra false alarm; b -> c: no extra detractor
    assert t.loc[2, "extra_false_alarms_per_extra_detractor"] == 1.0
    assert np.isnan(t.loc[3, "extra_false_alarms_per_extra_detractor"])


def test_freeze_needs_complete_decisions_and_hashes_every_field():
    from e5lib.selection import decisions_complete, frozen_recipe
    assert not decisions_complete("regression", {"model": None})
    assert decisions_complete("regression", {"model": {"chosen": "a"}})
    assert not decisions_complete("classification", {"model": {"chosen": "a"}, "threshold": None})
    dec = {"model": {"chosen": "a"}, "threshold": {"value": 1 / 6, "daily_alert_cap": 25}}
    assert decisions_complete("classification", dec)
    spec = {"estimator": "logistic", "numeric": ["x"], "categorical": ["c"], "log_inputs": ["x"], "random_state": 42}
    r1 = frozen_recipe("classification", spec, "sigmoid", {"value": 1 / 6}, dec, "2018-05-26", 42)
    r2 = frozen_recipe("classification", spec, "sigmoid", {"value": 1 / 6}, dec, "2018-05-26", 42)
    r3 = frozen_recipe("classification", spec, None, {"value": 1 / 6}, dec, "2018-05-26", 42)
    assert r1 == r2 and r1["sha256"] != r3["sha256"] and r1["test_read"] is False and r1["model"] == "a"
