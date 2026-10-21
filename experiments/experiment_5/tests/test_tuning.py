"""s07 tuning helpers: grids from protocol, the simplicity order and the in-family one-SE choice."""
import json

import pandas as pd

GRIDS = {"ridge_alpha": [0.01, 1, 100], "logistic_C": [0.1, 1], "class_weight": [None, "balanced"],
         "tree": {"max_depth": [4, 8], "min_samples_leaf": [20, 200]},
         "forest": {"max_depth": [8, 10], "min_samples_leaf": [50], "n_estimators": 200, "max_features": "sqrt"}}


def test_family_grids_follow_the_protocol():
    from e5lib.tuning import configurations, family_grid
    est, g = family_grid("regression", "linear", GRIDS)
    assert est == "ridge" and len(configurations(g)) == 3
    est, g = family_grid("classification", "linear", GRIDS)
    assert est == "logistic" and len(configurations(g)) == 4  # C x class_weight
    est, g = family_grid("classification", "forest", GRIDS)
    assert est == "forest_clf" and len(configurations(g)) == 2 * 1 * 2 and g["max_features"] == ["sqrt"]
    assert "class_weight" not in family_grid("regression", "tree", GRIDS)[1]


def test_simplicity_order():
    from e5lib.tuning import simplicity_key
    assert simplicity_key("linear", {"alpha": 100}) < simplicity_key("linear", {"alpha": 0.01})
    assert simplicity_key("linear", {"C": 0.1, "class_weight": None}) < simplicity_key("linear", {"C": 0.1, "class_weight": "balanced"})
    assert simplicity_key("tree", {"max_depth": 4, "min_samples_leaf": 200}) < simplicity_key("tree", {"max_depth": 4, "min_samples_leaf": 20})
    assert simplicity_key("tree", {"max_depth": 4, "min_samples_leaf": 20}) < simplicity_key("tree", {"max_depth": 8, "min_samples_leaf": 200})


def test_best_in_family_takes_the_simplest_within_one_se():
    from e5lib.tuning import best_in_family
    rows = []
    for depth, vals in {4: [5.0, 6.0, 5.5, 6.5, 5.2], 8: [4.9, 5.9, 5.4, 6.4, 5.1], 12: [3.0, 3.1, 3.2, 3.0, 3.1]}.items():
        for k, v in enumerate(vals, 1):
            rows.append({"candidate_id": f"d{depth}", "family": "tree",
                         "params": json.dumps({"max_depth": depth, "min_samples_leaf": 50}), "fold": k, "train": v, "validation": v})
    r = best_in_family(pd.DataFrame(rows), "tree", "mae", higher=False)
    assert r["best"] == "d12" and r["chosen"] == "d12"  # deeper is clearly better: beyond one SE
    d8 = {x["fold"]: x["validation"] for x in rows if x["candidate_id"] == "d8"}
    rows = [dict(x, validation=d8[x["fold"]] - 0.05) if x["candidate_id"] == "d12" else x for x in rows]
    r = best_in_family(pd.DataFrame(rows), "tree", "mae", higher=False)
    assert r["chosen"] == "d4"  # within one SE of the best: the shallowest wins
