"""Diagnostic checkpoint scoring. Final deployment/threshold bundles are Stage 5."""
from __future__ import annotations

import joblib
import pandas as pd

from .pipelines import positive_probability


def score_checkpoint(path, features, task):
    if "order_id" not in features or features.order_id.isna().any() or features.order_id.duplicated().any():
        raise ValueError("Unique non-null order_id required for alignment")
    if task not in {"regression","classification"}:
        raise ValueError("Unknown task")
    pipeline=joblib.load(path)  # Only load trusted local project checkpoints.
    values=pipeline.predict(features) if task=="regression" else positive_probability(pipeline,features)
    output=pd.DataFrame({"order_id":features.order_id.to_numpy(),"task":task,"prediction":values,
                         "policy":"diagnostic fold checkpoint; not final/deployed"})
    if task=="classification":
        output["diagnostic_threshold"]=.5
        output["diagnostic_decision"]=(values>=.5).astype(int)
    return output
