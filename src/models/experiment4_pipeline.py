"""Matched two-cycle pipelines and the authoritative Experiment 4 scoring interface."""
from pathlib import Path
import json
import numpy as np
import joblib
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.preprocessing import FunctionTransformer, StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.dummy import DummyRegressor, DummyClassifier
from .refinement_inputs import SelectedInputs

def build(task,candidate):
    cols=candidate['features'];family=candidate['family'];linear=family in ['plain','regularized'];seed=42
    skew=[c for c in ['total_price','total_freight','distance_km_max'] if c in cols]
    cat=[c for c in ['customer_state','primary_seller_state'] if c in cols]
    other=[c for c in cols if c not in skew+cat]
    def num(log,indicator):
        steps=[]
        if log:steps.append(('log1p',FunctionTransformer(np.log1p,feature_names_out='one-to-one')))
        steps.append(('impute',SimpleImputer(strategy='median',add_indicator=indicator)))
        if linear:steps.append(('scale',StandardScaler()))
        return Pipeline(steps)
    transforms=[('skewed_num',num(candidate.get('input_log',False),False),skew),('standard_num',num(False,True),other),('categorical',OneHotEncoder(handle_unknown='ignore',drop='first' if linear else None,sparse_output=False),cat)]
    if family=='dummy':model=DummyRegressor(strategy='median') if task=='regression' else DummyClassifier(strategy='prior')
    elif family=='plain':model=LinearRegression(tol=1e-6) if task=='regression' else LogisticRegression(penalty=None,solver='lbfgs',max_iter=2000,tol=1e-4,random_state=seed)
    elif family=='regularized':model=Ridge(alpha=candidate.get('alpha',100),random_state=seed) if task=='regression' else LogisticRegression(C=.01,max_iter=2000,solver='lbfgs',tol=1e-4,random_state=seed)
    elif family=='tree':model=(DecisionTreeRegressor if task=='regression' else DecisionTreeClassifier)(max_depth=candidate.get('depth',5),min_samples_leaf=candidate.get('leaf',100),random_state=seed)
    elif family=='forest':model=(RandomForestRegressor if task=='regression' else RandomForestClassifier)(n_estimators=50,max_depth=14,min_samples_leaf=candidate.get('leaf',20),random_state=seed,n_jobs=1)
    else:raise ValueError(family)
    pipe=Pipeline([('inputs',SelectedInputs(tuple(cols))),('preprocess',ColumnTransformer(transforms,remainder='drop',verbose_feature_names_out=True)),('model',model)])
    return TransformedTargetRegressor(regressor=pipe,func=np.log1p,inverse_func=np.expm1) if task=='regression' and candidate.get('target_log',False) else pipe

def predict(task,pipe,frame):
    return pipe.predict(frame) if task=='regression' else pipe.predict_proba(frame)[:,1]

class Experiment4Scorer:
    def __init__(self,bundle):
        self.bundle=Path(bundle);self.schema=json.loads((self.bundle/'feature_schema.json').read_text());self.pipe=joblib.load(self.bundle/'pipeline.joblib');self.task=self.schema['task']
        self.policy=json.loads((self.bundle/'decision_policy.json').read_text()) if self.task=='classification' else None
    def score(self,frame):
        import pandas as pd
        cols=self.schema['predictor_allowlist'];values=predict(self.task,self.pipe,frame[cols]);out=pd.DataFrame({'order_id':frame.order_id.to_numpy()})
        if self.task=='regression':out['lead_days_prediction']=values
        else:out['probability_1']=values;out['predicted_class']=(values>=self.policy['threshold']).astype(int)
        return out
