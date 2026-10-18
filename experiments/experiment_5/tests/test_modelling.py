"""Folds, candidate IDs, the factory and the decision rule."""
import warnings

import numpy as np
import pandas as pd
import pytest


def test_fold_rules_and_splits(e5):
    from e5lib import cv
    out = e5 / "stages" / "s05_partition" / "regression" / "outputs"
    out.mkdir(parents=True)
    folds = pd.DataFrame({
        "order_id": ["a", "b", "c", "a", "b", "c", "d"],
        "fold": [1, 1, 1, 2, 2, 2, 2],
        "role": ["train", "train", "validation", "train", "train", "train", "validation"],
        "purchase_ts": pd.to_datetime(["2018-01-01", "2018-01-02", "2018-02-01"] * 2 + ["2018-03-01"]),
    })
    folds.to_csv(out / "folds.csv", index=False, lineterminator="\n")
    records = pd.DataFrame({"order_id": list("abcd"), "customer_unique_id": ["x", "y", "z", "x"]})
    results = cv.check_fold_rules(folds, records)
    by = {(r["fold"], r["rule"]): r["passed"] for r in results}
    assert by[(1, "train_before_validation")] and by[(1, "no_shared_customer")]
    assert not by[(2, "no_shared_customer")]  # customer x on both sides of fold 2
    splits = cv.sklearn_splits(pd.Series(["d", "c", "b", "a"]), "regression", stage="s06_training")
    assert [list(s) for s in splits[0]] == [[3, 2], [1]]


def test_candidate_ids_are_stable():
    from e5lib.candidates import make_id
    spec = {"task": "regression", "estimator": "ridge", "params": {"alpha": 10.0}, "log_inputs": ["x"]}
    assert make_id(spec) == "reg.sel.log.ridge.alpha=10" == make_id(dict(spec))
    clf = {"task": "classification", "estimator": "logistic", "params": {"C": 0.1, "class_weight": "balanced"},
           "calibration": "sigmoid"}
    assert make_id(clf) == "clf.sel.raw.logistic.C=0.1.class_weight=balanced.sigmoid"


def _frame(n=300, seed=0):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame({
        "price": rng.lognormal(3, 1, n),
        "distance_km_max": np.where(rng.random(n) < 0.1, np.nan, rng.lognormal(6, 0.5, n)),
        "customer_state": rng.choice(["SP", "RJ", "MG"], n),
        "primary_seller_state": rng.choice(["SP", "PR"], n),
    })
    y_reg = 5 + 0.002 * df["distance_km_max"].fillna(400) + rng.normal(0, 1, n)
    y_clf = (rng.random(n) < 0.2).astype(int)
    return df, y_reg.clip(lower=0.5), y_clf


@pytest.mark.parametrize("task,estimator,extra", [
    ("regression", "dummy_median", {}),
    ("regression", "linear", {"log_target": True}),
    ("regression", "ridge", {"params": {"alpha": 1.0}, "log_target": True}),
    ("regression", "tree_reg", {"params": {"max_depth": 5, "min_samples_leaf": 20}}),
    ("regression", "forest_reg", {"params": {"max_depth": 6, "min_samples_leaf": 20}}),
    ("classification", "dummy_prior", {}),
    ("classification", "logistic", {}),
    ("classification", "logistic", {"params": {"C": 0.1, "class_weight": "balanced"}, "calibration": "sigmoid"}),
    ("classification", "tree_clf", {"params": {"max_depth": 4}}),
    ("classification", "forest_clf", {"params": {"max_depth": 8, "min_samples_leaf": 20}}),
])
def test_factory_builds_and_fits(task, estimator, extra):
    from e5lib import factory
    X, y_reg, y_clf = _frame()
    spec = {"task": task, "estimator": estimator, "numeric": ["price", "distance_km_max"],
            "categorical": ["customer_state"], "log_inputs": ["price", "distance_km_max"],
            "route_median": {"column": "distance_km_max",
                             "keys": [["customer_state", "primary_seller_state"], ["customer_state"]]},
            **extra}
    model = factory.build(spec)
    cols = factory.feature_columns(spec)
    with warnings.catch_warnings():
        warnings.simplefilter("error", FutureWarning)
        warnings.simplefilter("error", DeprecationWarning)
        model.fit(X[cols], y_reg if task == "regression" else y_clf)
    if task == "regression":
        assert np.isfinite(model.predict(X[cols])).all()
    else:
        p = model.predict_proba(X[cols])[:, 1]
        assert ((p >= 0) & (p <= 1)).all()


def test_factory_rejects_wrong_combinations():
    from e5lib import factory
    with pytest.raises(ValueError):
        factory.build({"task": "classification", "estimator": "ridge", "numeric": ["a"]})
    with pytest.raises(ValueError):
        factory.build({"task": "classification", "estimator": "logistic", "numeric": ["a"], "log_target": True})


def test_route_median_is_learned_in_fit():
    from e5lib.factory import RouteMedianImputer
    train = pd.DataFrame({"d": [10.0, 20.0, 100.0, np.nan], "a": ["x", "x", "y", "x"], "b": ["p", "p", "q", "p"]})
    imp = RouteMedianImputer("d", (("a", "b"), ("a",))).fit(train)
    out = imp.transform(pd.DataFrame({"d": [np.nan, np.nan], "a": ["x", "z"], "b": ["p", "p"]}))
    assert out["d"].tolist() == [15.0, 20.0]  # route median, then global median
    assert out["d_missing"].tolist() == [1, 1]


def test_metrics_and_one_se_rule():
    from e5lib import metrics
    reg = metrics.score("regression", [1, 2, 3, 10], [1, 2, 4, 5])
    assert reg["mae"] == pytest.approx(1.5) and reg["within_3d"] == pytest.approx(0.75)
    clf = metrics.score("classification", [0, 0, 1, 1], proba=[0.1, 0.6, 0.4, 0.9], threshold=0.5)
    assert clf["tp"] == 1 and clf["fp"] == 1 and clf["cost"] == 5 * 1 + 1
    rows = []
    for k, (a, b) in enumerate([(3.0, 2.9), (3.1, 3.0), (3.0, 3.1)]):
        rows += [{"candidate_id": "simple", "fold": k, "metric": "mae", "value": a},
                 {"candidate_id": "complex", "fold": k, "metric": "mae", "value": b}]
    res = metrics.one_se_select(pd.DataFrame(rows), "mae", higher_is_better=False,
                                simplicity={"simple": 0, "complex": 1})
    assert res["best"] == "complex" and res["chosen"] == "simple"  # simple is within one SE
