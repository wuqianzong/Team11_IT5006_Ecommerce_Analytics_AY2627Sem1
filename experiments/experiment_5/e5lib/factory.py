"""The one pipeline factory: spec -> sklearn estimator (README sections 5.3 and 13.1).

Assembly only, no new transformation: the recipe comes from s04 (recipes.json), the
estimator and its settings from s06-s08. Everything learned (medians, route medians,
encoders, scaler, calibrator) is fitted inside the training data passed to .fit().

Spec keys
---------
task            "regression" | "classification"
numeric         numeric feature columns
categorical     categorical feature columns
log_inputs      numeric columns to log1p (s04 4.2, G-47)
estimator       one of ESTIMATORS
params          estimator settings (grids in s07)
route_median    optional {"column": ..., "keys": [[...], [...]]}: fill a column's missing values
                with the median of the first key group that has one, else the global median (G-27)
log_target      regression only: fit on log1p(y), predict expm1 (G-36)
drop_duplicates optional bool: drop encoded columns identical to an earlier column in the training
                data (s04 4.3 duplicate rule; e.g. missing indicators of fields that are always
                missing together)
calibration     classification only: None | "sigmoid" (G-52). Rows must be sorted by
                purchase time, because the inner splits are time-ordered.
random_state    default 42
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

LINEAR = {"linear", "ridge", "logistic"}
REGRESSORS = {"dummy_median", "linear", "ridge", "tree_reg", "forest_reg"}
CLASSIFIERS = {"dummy_prior", "logistic", "tree_clf", "forest_clf"}
FOREST_TREES = 200  # s01 1.8, s07 7.4


def _estimator(name: str, params: dict, seed: int):
    p = dict(params or {})
    if name == "dummy_median":
        return DummyRegressor(strategy="median")
    if name == "dummy_prior":
        return DummyClassifier(strategy="prior")
    if name == "linear":
        return LinearRegression(**p)
    if name == "ridge":
        return Ridge(**p)
    if name == "logistic":
        # Plain logistic (s06) has no C: an infinite C means no regularisation (sklearn >= 1.8).
        p.setdefault("C", np.inf)
        return LogisticRegression(solver="lbfgs", max_iter=5000, **p)
    if name == "tree_reg":
        return DecisionTreeRegressor(random_state=seed, **p)
    if name == "tree_clf":
        return DecisionTreeClassifier(random_state=seed, **p)
    if name == "forest_reg":
        p.setdefault("max_features", "sqrt")
        return RandomForestRegressor(n_estimators=FOREST_TREES, random_state=seed, n_jobs=-1, **p)
    if name == "forest_clf":
        p.setdefault("max_features", "sqrt")
        return RandomForestClassifier(n_estimators=FOREST_TREES, random_state=seed, n_jobs=-1, **p)
    raise KeyError(f"unknown estimator {name!r}")


class RouteMedianImputer(BaseEstimator, TransformerMixin):
    """Fill one column's missing values with route medians learned in fit (G-27).

    Adds <column>_missing (0/1). The median is invariant to log1p, so it can run before
    the log transform.
    """

    def __init__(self, column: str = "distance_km_max", keys: tuple = (("customer_state", "primary_seller_state"), ("customer_state",))):
        self.column = column
        self.keys = keys

    def fit(self, X: pd.DataFrame, y=None):
        known = X[X[self.column].notna()]
        self.levels_ = [known.groupby(list(k))[self.column].median() for k in self.keys]
        self.global_ = float(known[self.column].median())
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        X = X.copy()
        missing = X[self.column].isna()
        X[f"{self.column}_missing"] = missing.astype(int)
        for k, medians in zip(self.keys, self.levels_):
            todo = X[self.column].isna()
            if not todo.any():
                break
            idx = pd.MultiIndex.from_frame(X.loc[todo, list(k)]) if len(k) > 1 else X.loc[todo, k[0]]
            X.loc[todo, self.column] = medians.reindex(idx).to_numpy()
        X[self.column] = X[self.column].fillna(self.global_)
        return X


class DropDuplicateColumns(BaseEstimator, TransformerMixin):
    """Drop encoded columns identical to an earlier column in the fit data (s04 4.3)."""

    def fit(self, X, y=None):
        A = np.asarray(X, dtype=float)
        self.n_features_in_ = A.shape[1]
        seen, keep = {}, []
        for j in range(A.shape[1]):
            key = A[:, j].tobytes()
            if key not in seen:
                seen[key] = j
                keep.append(j)
        self.keep_ = np.array(keep, dtype=int)
        self.dropped_ = [j for j in range(A.shape[1]) if j not in seen.values()]
        return self

    def transform(self, X):
        return np.asarray(X, dtype=float)[:, self.keep_]

    def get_feature_names_out(self, input_features=None):
        names = np.asarray(input_features if input_features is not None
                           else [f"x{j}" for j in range(self.n_features_in_)], dtype=object)
        return names[self.keep_]


def _preprocessor(spec: dict) -> ColumnTransformer:
    linear = spec["estimator"] in LINEAR
    numeric = list(spec.get("numeric", []))
    if spec.get("route_median"):
        numeric.append(f"{spec['route_median']['column']}_missing")
    logged = [c for c in spec.get("log_inputs", []) if c in numeric]
    plain = [c for c in numeric if c not in logged]

    def num_steps(log: bool):
        steps = []
        if log:
            steps.append(("log1p", FunctionTransformer(np.log1p, feature_names_out="one-to-one")))
        steps.append(("impute", SimpleImputer(strategy="median", add_indicator=True)))
        if linear:
            steps.append(("scale", StandardScaler()))
        return Pipeline(steps)

    cat = Pipeline([
        ("impute", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", drop="first" if linear else None,
                                 sparse_output=False)),
    ])
    parts = []
    if logged:
        parts.append(("num_log", num_steps(True), logged))
    if plain:
        parts.append(("num", num_steps(False), plain))
    if spec.get("categorical"):
        parts.append(("cat", cat, list(spec["categorical"])))
    if not parts:
        raise ValueError("spec has no feature columns")
    return ColumnTransformer(parts, remainder="drop", verbose_feature_names_out=False)


def build(spec: dict):
    """Return one unfitted sklearn estimator for the spec."""
    task, name = spec["task"], spec["estimator"]
    seed = spec.get("random_state", 42)
    if task == "regression" and name not in REGRESSORS:
        raise ValueError(f"{name} is not a regression estimator")
    if task == "classification" and name not in CLASSIFIERS:
        raise ValueError(f"{name} is not a classification estimator")
    if spec.get("log_target") and task != "regression":
        raise ValueError("log_target applies to regression only")
    if spec.get("calibration") and task != "classification":
        raise ValueError("calibration applies to classification only")

    steps = []
    if spec.get("route_median"):
        rm = spec["route_median"]
        steps.append(("route_median", RouteMedianImputer(rm["column"], tuple(tuple(k) for k in rm["keys"]))))
    steps.append(("prep", _preprocessor(spec)))
    if spec.get("drop_duplicates"):
        steps.append(("dedupe", DropDuplicateColumns()))
    steps.append(("model", _estimator(name, spec.get("params"), seed)))
    model = Pipeline(steps)

    if spec.get("log_target"):
        model = TransformedTargetRegressor(regressor=model, func=np.log1p, inverse_func=np.expm1,
                                           check_inverse=False)
    if spec.get("calibration") == "sigmoid":
        model = CalibratedClassifierCV(model, method="sigmoid", cv=TimeSeriesSplit(n_splits=3))
    elif spec.get("calibration"):
        raise ValueError(f"unknown calibration {spec['calibration']!r}")
    return model


def feature_columns(spec: dict) -> list[str]:
    """Columns the estimator reads from X (route keys included)."""
    cols = list(spec.get("numeric", [])) + list(spec.get("categorical", []))
    if spec.get("route_median"):
        for key in spec["route_median"]["keys"]:
            cols += [c for c in key if c not in cols]
    return list(dict.fromkeys(cols))
