"""Strict task-specific original-unit inputs; no experiment/document dependency."""
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.compose import ColumnTransformer
from src.features.contract import PREDICTOR_ALLOWLIST
from .pipelines import normalize_inputs
from .tuned_pipelines import make_tuned_pipeline


class SelectedInputs(TransformerMixin, BaseEstimator):
    def __init__(self, columns):
        self.columns = columns

    def transform(self, X):
        if not isinstance(X, pd.DataFrame) or X.columns.duplicated().any():
            raise ValueError('Unique named dataframe required')
        if len(set(self.columns)) != len(self.columns) or not set(self.columns) <= set(PREDICTOR_ALLOWLIST):
            raise ValueError('Invalid predictor specification')
        if set(X.columns) != set(self.columns):
            raise ValueError('Exactly the task predictors required; IDs/outcomes prohibited')
        normalized, _ = normalize_inputs(X.reindex(columns=PREDICTOR_ALLOWLIST))
        return normalized[list(self.columns)]

    def fit(self, X, y=None):
        self.transform(X)
        self.feature_names_in_ = np.array(self.columns, dtype=object)
        self.n_features_in_ = len(self.columns)
        return self

    def get_feature_names_out(self, input_features=None):
        return np.array(self.columns, dtype=object)


def selected_pipeline(task, candidate, baseline_config, columns):
    pipe = make_tuned_pipeline(task, candidate, baseline_config)
    transforms = [(name, clone(est), [c for c in cols if c in columns])
                  for name, est, cols in pipe.named_steps['preprocess'].transformers]
    pipe.set_params(inputs=SelectedInputs(tuple(columns)),
                    preprocess=ColumnTransformer(transforms, remainder='drop', sparse_threshold=1., verbose_feature_names_out=True))
    return pipe
