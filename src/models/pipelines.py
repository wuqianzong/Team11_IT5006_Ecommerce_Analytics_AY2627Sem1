"""Name-based validation and fold-fitted preprocessing; no learned global transforms."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from src.features.contract import (PREDICTOR_ALLOWLIST, CATEGORICAL_COLUMNS,
                                  NUMERIC_COLUMNS, VALID_STATES, USABLE_PAYMENT_TYPES, UNKNOWN)

COUNTS = {"n_items", "n_products", "n_sellers", "n_categories", "n_payment_methods"}
FLAGS = {"has_items", "freight_ratio_missing", "payment_missing"}
POSITIVE = {"total_weight_g", "total_volume_cm3", "payment_installments_max"}
FRACTIONS = {"weight_missing_fraction", "volume_missing_fraction", "category_missing_fraction",
             "distance_missing_fraction", "interstate_share"}
CALENDAR = {"purchase_month": (1, 12), "purchase_dayofweek": (0, 6), "purchase_hour": (0, 23)}


def normalize_inputs(frame: pd.DataFrame):
    if not isinstance(frame, pd.DataFrame) or frame.columns.duplicated().any():
        raise ValueError("Features must be a dataframe with unique named columns")
    missing = set(PREDICTOR_ALLOWLIST) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing predictor columns: {sorted(missing)}")
    result = frame[PREDICTOR_ALLOWLIST].copy()
    quality = {}
    for col in NUMERIC_COLUMNS + list(CALENDAR):
        value = pd.to_numeric(result[col], errors="coerce")
        bad = result[col].notna() & value.isna()
        if bad.any() or np.isinf(value.to_numpy(dtype=float, na_value=np.nan)).any():
            raise ValueError(f"{col}: malformed/nonfinite numeric value")
        valid = value.dropna()
        if (valid < 0).any():
            raise ValueError(f"{col}: negative value")
        if col in COUNTS | FLAGS | set(CALENDAR) | {"payment_installments_max"}:
            if not np.equal(valid, np.floor(valid)).all():
                raise ValueError(f"{col}: fractional count/code")
        if col in FLAGS and not valid.isin([0, 1]).all():
            raise ValueError(f"{col}: flag outside 0/1")
        if col in POSITIVE and not valid.gt(0).all():
            raise ValueError(f"{col}: requires strictly positive value")
        if col in FRACTIONS and not valid.le(1).all():
            raise ValueError(f"{col}: fraction outside [0,1]")
        if col in CALENDAR:
            low, high = CALENDAR[col]
            if not valid.between(low, high).all():
                raise ValueError(f"{col}: calendar outside [{low},{high}]")
            result[col] = value.map(lambda v: UNKNOWN if pd.isna(v) else str(int(v)))
        else:
            result[col] = value.astype(float)
    for col in ["customer_state", "primary_seller_state", "primary_payment_type", "primary_category"]:
        tokens = result[col].astype("string").str.strip()
        if col.endswith("state"):
            tokens = tokens.str.upper()
            invalid = tokens.notna() & ~tokens.isin(VALID_STATES) & ~tokens.eq(UNKNOWN.upper())
            tokens = tokens.where(tokens.isin(VALID_STATES), UNKNOWN)
        elif col == "primary_payment_type":
            tokens = tokens.str.lower()
            invalid = tokens.notna() & ~tokens.isin(USABLE_PAYMENT_TYPES) & ~tokens.eq(UNKNOWN.lower())
            tokens = tokens.where(tokens.isin(USABLE_PAYMENT_TYPES), UNKNOWN)
        else:
            invalid = tokens.notna() & tokens.eq("")
            tokens = tokens.replace("", UNKNOWN).fillna(UNKNOWN)
        quality[col] = {"malformed_tokens": int(invalid.sum()), "missing_cells": int(result[col].isna().sum())}
        result[col] = tokens.fillna(UNKNOWN).astype(object)
    return result, quality


class InputContract(TransformerMixin, BaseEstimator):
    def fit(self, X, y=None):
        normalize_inputs(X)
        self.feature_names_in_ = np.array(PREDICTOR_ALLOWLIST, dtype=object)
        self.n_features_in_ = len(PREDICTOR_ALLOWLIST)
        return self

    def transform(self, X):
        return normalize_inputs(X)[0]

    def get_feature_names_out(self, input_features=None):
        return np.array(PREDICTOR_ALLOWLIST, dtype=object)


def make_pipeline(task, model, config):
    if task not in {"regression", "classification"} or model not in {"dummy", "linear", "tree"}:
        raise ValueError("Unsupported baseline task/model")
    linear = model == "linear"
    numeric = [("impute", SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True))]
    if linear:
        numeric.append(("scale", StandardScaler()))
    preprocessor = ColumnTransformer([
        ("numeric", Pipeline(numeric), NUMERIC_COLUMNS),
        ("categorical", OneHotEncoder(handle_unknown="ignore", drop="first" if linear else None,
                                      sparse_output=True), CATEGORICAL_COLUMNS),
    ], remainder="drop", sparse_threshold=1.0, verbose_feature_names_out=True)
    if model == "dummy":
        estimator = DummyRegressor(strategy="median") if task == "regression" else DummyClassifier(strategy="prior")
    elif model == "linear" and task == "regression":
        estimator = LinearRegression(**config["linear"])
    elif model == "linear":
        params = dict(config["logistic"])
        if params["C"] == "infinity":
            params["C"] = np.inf  # sklearn 1.9 unpenalized logistic baseline.
        estimator = LogisticRegression(**params, random_state=config["seed"])
    else:
        cls = DecisionTreeRegressor if task == "regression" else DecisionTreeClassifier
        estimator = cls(**config["tree"], criterion="squared_error" if task == "regression" else "gini",
                        random_state=config["seed"])
    return Pipeline([("inputs", InputContract()), ("preprocess", preprocessor), ("model", estimator)])


def positive_probability(pipeline, X):
    classes = pipeline.named_steps["model"].classes_
    indices = np.flatnonzero(classes == 1)
    if len(indices) != 1:
        raise ValueError("Expected explicit positive class 1")
    return pipeline.predict_proba(X)[:, int(indices[0])]


def encoding_audit(pipeline, X):
    normalized, quality = normalize_inputs(X)
    enc = pipeline.named_steps["preprocess"].named_transformers_["categorical"]
    categories = {}
    for i, col in enumerate(CATEGORICAL_COLUMNS):
        unknown = ~normalized[col].isin(enc.categories_[i])
        categories[col] = {"unseen_count": int(unknown.sum()), "denominator": len(X),
                           "training_categories": enc.categories_[i].tolist(),
                           "reference": None if enc.drop_idx_ is None else str(enc.categories_[i][enc.drop_idx_[i]])}
    return {"token_quality": quality, "categories": categories}
