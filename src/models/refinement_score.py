"""Trusted/checksummed core-bundle scoring, in original units, never fits."""
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
from .score import checked_manifest
from .pipelines import positive_probability
from .policy import apply_threshold
from .refinement_core import CORE_FEATURES, CORE_SCHEMA_VERSION, normalize_core

class CoreScorer:
    def __init__(self,bundle):
        self.bundle=Path(bundle)
        checked_manifest(self.bundle)
        self.metadata=json.loads((self.bundle/'metadata.json').read_text())
        schema=json.loads((self.bundle/'feature_schema.json').read_text())
        if schema['version']!=CORE_SCHEMA_VERSION or schema['predictor_allowlist']!=CORE_FEATURES:raise ValueError('Wrong core schema')
        self.task=self.metadata['task']
        if self.task not in {'regression','classification'}:raise ValueError('Invalid task')
        self.pipeline=joblib.load(self.bundle/'pipeline.joblib')
        self.policy=json.loads((self.bundle/'decision_policy.json').read_text()) if self.task=='classification' else None
    def score(self,frame):
        if not isinstance(frame,pd.DataFrame) or frame.columns.duplicated().any():raise ValueError('Unique dataframe columns required')
        if set(frame.columns)!={'order_id',*CORE_FEATURES}:raise ValueError('Expected order_id and exactly eleven predictors')
        ids=frame.order_id.astype('string')
        if ids.isna().any() or ids.str.strip().eq('').any() or ids.duplicated().any():raise ValueError('Missing/blank/duplicate order_id')
        X=frame[CORE_FEATURES];normalize_core(X)
        values=self.pipeline.predict(X) if self.task=='regression' else positive_probability(self.pipeline,X)
        if not np.isfinite(values).all():raise ValueError('Nonfinite output')
        result=pd.DataFrame({'order_id':ids.to_numpy(),'task':self.task,'model_version':self.metadata['model_version']})
        if self.policy:
            result['probability_1']=values;result['decision']=apply_threshold(values,self.policy);result['threshold']=self.policy['threshold']
        else:result['lead_days_prediction']=values
        return result
