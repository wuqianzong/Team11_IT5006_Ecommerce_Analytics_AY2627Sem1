"""s04 helpers: duplicate-column rule in the factory, pool ranking, selection, transforms."""
import numpy as np
import pandas as pd


def test_drop_duplicate_columns_keeps_first():
    from e5lib.factory import DropDuplicateColumns
    X = np.array([[1, 1, 0, 1], [0, 0, 1, 0], [1, 1, 1, 1.0]])
    t = DropDuplicateColumns().fit(X)
    assert t.keep_.tolist() == [0, 2] and t.dropped_ == [1, 3]
    assert t.transform(X).shape == (3, 2)
    assert t.get_feature_names_out(["a", "b", "c", "d"]).tolist() == ["a", "c"]


def test_pool_ranking_is_the_pool_renormalised():
    from e5lib import contract
    from e5lib.features import pool_ranking
    pool = contract.pool("classification")
    extra = pd.DataFrame({"feature": list(pool) + ["est_delivery_days", "region_pair"],
                          "value": [1.0] * len(pool) + [5.0, 5.0]})
    r = pool_ranking("classification", extra)
    assert set(r["feature"]) == set(pool) and abs(r["share"].sum() - 1) < 1e-12
    assert r["cumulative_share"].iloc[-1] == 1.0


def test_selection_cut_and_core_filter():
    from e5lib.features import selection
    ranking = pd.DataFrame({"feature": ["a", "b", "c", "d"], "value": [0.5, 0.3, 0.15, 0.05]})
    out, sel = selection(ranking, ["a", "b", "c", "d"], 0.95)
    assert sel == ["a", "b", "c"] and out["selected"].tolist() == [True, True, True, False]
    out, sel = selection(ranking, ["a", "c", "d"], 0.95)  # b dropped in reduction: shares re-normalised
    assert abs(out["share"].sum() - 1) < 1e-12 and sel == ["a", "c", "d"]  # 0.714, 0.929, 1.0


def test_factory_spec_routes_distance_and_dedupes():
    from e5lib.features import factory_spec
    s = factory_spec("regression", ["distance_km_max", "customer_state", "n_items"], ["distance_km_max"], "linear")
    assert s["route_median"]["column"] == "distance_km_max" and s["drop_duplicates"] and s["log_target"]
    assert s["categorical"] == ["customer_state"] and s["log_inputs"] == ["distance_km_max"]
