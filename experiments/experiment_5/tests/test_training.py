"""s06 training helpers: candidate specs, the family ladder, fold-only preprocessing, learning-curve subsets."""
import numpy as np
import pandas as pd


def _recipes(task="regression"):
    base = {"task": task, "numeric": ["price", "distance_km_max"], "categorical": ["customer_state"],
            "log_inputs": ["price", "distance_km_max"],
            "route_median": {"column": "distance_km_max", "keys": [["customer_state", "primary_seller_state"], ["customer_state"]]},
            "drop_duplicates": True}
    est = {"regression": ["dummy_median", "linear", "tree_reg", "forest_reg"],
           "classification": ["dummy_prior", "logistic", "tree_clf", "forest_clf"]}[task]
    out = {}
    for fam, e in zip(("dummy", "linear", "tree", "forest"), est):
        spec = dict(base, estimator=e)
        if task == "regression":
            spec["log_target"] = True
        out[fam] = {"spec": spec}
    return out


SETTINGS = {"tree": {"max_depth": 5, "min_samples_leaf": 100},
            "forest": {"n_estimators": 200, "max_depth": 10, "min_samples_leaf": 50, "max_features": "sqrt"}}


def test_candidate_specs_keep_the_s04_recipe():
    from e5lib.training import candidate_specs
    rec = _recipes()
    cands = candidate_specs("regression", rec, SETTINGS, 42)
    assert [c["family"] for c in cands] == ["dummy", "linear", "tree", "forest"]
    for c in cands:
        stripped = {k: v for k, v in c["spec"].items() if k not in ("params", "random_state")}
        assert stripped == rec[c["family"]]["spec"]
    assert cands[2]["spec"]["params"] == {"max_depth": 5, "min_samples_leaf": 100}
    assert "n_estimators" not in cands[3]["spec"]["params"]  # 200 trees are fixed in the factory
    assert cands[1]["candidate_id"] == "reg.sel.log.linear"


def test_ladder_keeps_a_complex_family_only_beyond_one_se():
    from e5lib.training import ladder
    rows = []
    vals = {"d": [10, 11, 10, 11, 10], "l": [5, 6, 5, 6, 5], "t": [4.9, 6.1, 4.9, 6.0, 5.0], "f": [2, 2.1, 2, 2.1, 2]}
    for cid, v in vals.items():
        rows += [{"candidate_id": cid, "fold": k, "metric": "mae", "value": x} for k, x in enumerate(v, 1)]
    steps = ladder(pd.DataFrame(rows), "mae", False, ["d", "l", "t", "f"])
    assert [s["complex_kept"] for s in steps] == [True, False, True]
    assert steps[-1]["simpler"] == "l" and steps[-1]["chosen"] == "f"


def test_preprocessing_is_learned_from_the_training_fold_only():
    from e5lib import factory
    from e5lib.training import candidate_specs, fit_fold, imputer_fitted_on_training
    rng = np.random.default_rng(0)
    n = 400
    X = pd.DataFrame({"price": rng.lognormal(3, 1, n),
                      "distance_km_max": np.where(rng.random(n) < 0.2, np.nan, rng.lognormal(6, 0.5, n)),
                      "customer_state": rng.choice(["SP", "RJ"], n), "primary_seller_state": rng.choice(["SP", "PR"], n)})
    y = rng.lognormal(2, 0.5, n)
    spec = candidate_specs("regression", _recipes(), SETTINGS, 42)[1]["spec"]
    cols = factory.feature_columns(spec)
    model, _, _, info = fit_fold("regression", spec, X.iloc[:300][cols], y[:300], X.iloc[300:][cols])
    assert imputer_fitted_on_training(model, X.iloc[:300][cols], spec)
    assert not imputer_fitted_on_training(model, X[cols].assign(price=X["price"] * 3), spec)
    assert info["convergence_warnings"] == 0


def test_learning_curve_subset_is_the_most_recent_rows():
    from e5lib.training import recent_subset
    ts = pd.Series(pd.to_datetime(["2018-01-05", "2018-01-01", "2018-01-03", "2018-01-02", "2018-01-04"]),
                   index=list("abcde"))
    assert list(recent_subset(np.array(list("abcde")), ts, 0.4)) == ["e", "a"]


def test_paired_gain_is_signed_by_metric_direction():
    from e5lib.training import paired_gain
    rows = [{"candidate_id": c, "fold": k, "metric": "m", "value": v}
            for c, vals in {"a": [5, 6, 7], "b": [4, 6.5, 6]}.items() for k, v in enumerate(vals, 1)]
    df = pd.DataFrame(rows)
    low = paired_gain(df, "a", "b", higher=False)  # lower is better: b wins folds 1 and 3
    assert low["folds_better"] == 2 and abs(low["mean_gain"] - (1 - 0.5 + 1) / 3) < 1e-12
    high = paired_gain(df, "a", "b", higher=True)
    assert high["folds_better"] == 1 and abs(high["mean_gain"] + low["mean_gain"]) < 1e-12
