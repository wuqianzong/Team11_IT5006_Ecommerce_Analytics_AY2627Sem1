"""Versioned 11-input transaction-core interface; original 27-input models unchanged."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.compose import ColumnTransformer
from src.features.contract import UNKNOWN, VALID_STATES
from .tuned_pipelines import make_tuned_pipeline

CORE_FEATURES = ['n_items', 'has_items', 'n_products', 'total_price', 'total_freight',
                 'freight_ratio', 'freight_ratio_missing', 'customer_state',
                 'purchase_month', 'purchase_dayofweek', 'purchase_hour']
CORE_SCHEMA_VERSION = 'transaction-core-v2'
CALENDAR = {'purchase_month': (1,12), 'purchase_dayofweek': (0,6), 'purchase_hour': (0,23)}

def normalize_core(frame):
    if not isinstance(frame, pd.DataFrame) or frame.columns.duplicated().any():
        raise ValueError('Unique named dataframe columns required')
    if set(frame.columns) != set(CORE_FEATURES):
        raise ValueError('Expected exactly 11 core predictors; missing=' + str(sorted(set(CORE_FEATURES)-set(frame))) + '; extra=' + str(sorted(set(frame)-set(CORE_FEATURES))))
    result = frame[CORE_FEATURES].copy()
    for col in [x for x in CORE_FEATURES if x!='customer_state']:
        value = pd.to_numeric(result[col], errors='coerce')
        if (result[col].notna() & value.isna()).any() or np.isinf(value.to_numpy(dtype=float,na_value=np.nan)).any():
            raise ValueError(f'{col}: malformed/nonfinite value')
        valid = value.dropna()
        if valid.lt(0).any():raise ValueError(f'{col}: negative value')
        if col in {'n_items','n_products','has_items','freight_ratio_missing'} | set(CALENDAR):
            if not np.equal(valid,np.floor(valid)).all():raise ValueError(f'{col}: fractional count/code')
        if col in {'has_items','freight_ratio_missing'} and not valid.isin([0,1]).all():
            raise ValueError(f'{col}: invalid flag')
        if col in CALENDAR:
            lo,hi=CALENDAR[col]
            if not valid.between(lo,hi).all():raise ValueError(f'{col}: invalid calendar component')
            result[col]=value.map(lambda v: UNKNOWN if pd.isna(v) else str(int(v)))
        else:result[col]=value.astype(float)
    states=result.customer_state.astype('string').str.strip().str.upper()
    result['customer_state']=states.where(states.isin(VALID_STATES),UNKNOWN).fillna(UNKNOWN).astype(object)
    return result

class CoreInputContract(TransformerMixin, BaseEstimator):
    def fit(self,X,y=None):
        normalize_core(X)
        self.feature_names_in_=np.array(CORE_FEATURES,dtype=object)
        self.n_features_in_=len(CORE_FEATURES)
        return self
    def transform(self,X):return normalize_core(X)
    def get_feature_names_out(self,input_features=None):return np.array(CORE_FEATURES,dtype=object)

def make_core_pipeline(task,candidate,baseline_config):
    pipe=make_tuned_pipeline(task,candidate,baseline_config)
    original=pipe.named_steps['preprocess']
    transforms=[(name,clone(est),[c for c in cols if c in CORE_FEATURES]) for name,est,cols in original.transformers]
    pipe.set_params(inputs=CoreInputContract(),preprocess=ColumnTransformer(transforms,remainder='drop',sparse_threshold=1.,verbose_feature_names_out=True))
    return pipe
