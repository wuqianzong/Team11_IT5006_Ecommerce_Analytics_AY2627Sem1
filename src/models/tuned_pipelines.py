"""Stage 4 model factory; preserves Stage 3 factories and frozen raw feature contract."""
from __future__ import annotations

import numpy as np
from scipy import sparse
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor

from .pipelines import make_pipeline, normalize_inputs

PAYMENT_COLUMNS = {"primary_payment_type", "payment_installments_max", "n_payment_methods", "payment_missing"}


def make_tuned_pipeline(task, candidate, baseline_config, variant="full"):
    if task not in {"regression", "classification"} or variant not in {"full", "no_payment"}:
        raise ValueError("Unknown task/feature variant")
    family = candidate["family"]
    if "baseline_model" in candidate:
        pipe = make_pipeline(task, candidate["baseline_model"], baseline_config)
    else:
        linear = family in {"ridge", "logistic"}
        pipe = make_pipeline(task, "linear" if linear else "tree", baseline_config)
        params = dict(candidate["params"])
        seed = baseline_config["seed"]
        if family == "ridge" and task == "regression":
            estimator = Ridge(**params)
        elif family == "logistic" and task == "classification":
            estimator = LogisticRegression(**params, random_state=seed)
        elif family == "tree":
            cls = DecisionTreeRegressor if task == "regression" else DecisionTreeClassifier
            estimator = cls(**params, random_state=seed,
                            criterion="squared_error" if task == "regression" else "gini")
        elif family == "forest":
            cls = RandomForestRegressor if task == "regression" else RandomForestClassifier
            estimator = cls(**params, random_state=seed, n_jobs=1,
                            criterion="squared_error" if task == "regression" else "gini")
        else:
            raise ValueError("Unsupported family/task")
        pipe.set_params(model=estimator)
    if variant == "no_payment":
        original = pipe.named_steps["preprocess"]
        transforms = [(name, clone(transform), [c for c in columns if c not in PAYMENT_COLUMNS])
                      for name, transform, columns in original.transformers]
        pipe.set_params(preprocess=ColumnTransformer(transforms, remainder="drop",
                        sparse_threshold=1.0, verbose_feature_names_out=True))
    return pipe


def tuned_encoding(pipe, X):
    normalized, quality = normalize_inputs(X)
    columns = pipe.named_steps["preprocess"].transformers_[1][2]
    enc = pipe.named_steps["preprocess"].named_transformers_["categorical"]
    categories = {}
    for i,col in enumerate(columns):
        categories[col] = {"unseen_count":int((~normalized[col].isin(enc.categories_[i])).sum()),
            "denominator":len(X),"training_categories":enc.categories_[i].tolist(),
            "reference":None if enc.drop_idx_ is None else str(enc.categories_[i][enc.drop_idx_[i]])}
    return {"token_quality":quality,"categories":categories}


def tuned_state(pipe, X):
    transformed=pipe[:-1].transform(X)
    names=pipe[:-1].get_feature_names_out()
    values=transformed.data if sparse.issparse(transformed) else transformed
    if len(names)!=transformed.shape[1] or not np.isfinite(values).all():raise ValueError("Invalid transformed design")
    preprocess=pipe.named_steps["preprocess"]
    columns=preprocess.transformers_[0][2]
    numeric=preprocess.named_transformers_["numeric"]
    state={"transformed_feature_names":names.tolist(),"dimension":len(names),"sparse":sparse.issparse(transformed),
        "imputer_statistics":dict(zip(columns,numeric.named_steps["impute"].statistics_)),
        "training_encoding":tuned_encoding(pipe,X)}
    if "scale" in numeric.named_steps:
        state.update(scaler_mean=numeric.named_steps["scale"].mean_.tolist(),
                     scaler_scale=numeric.named_steps["scale"].scale_.tolist())
    return state
