"""Prediction API for the dashboard (plan revision 2, 6a.2): the frozen T1 bundles behind HTTP.

POST /predict/{task} with {"rows": [...]} returns e5b.serving.Release.predict for those rows:
the same routing (B inside the seven states, A elsewhere), input checks and thresholds as the
app's local path. Nothing is fitted and no label is read; the caller sends model inputs only.

Run locally from the repository root:
    uvicorn experiments.experiment_5.pipeline_b.deliverables.dashboard.api.main:app --port 8000
"""
from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

PIPELINE_B = Path(__file__).resolve().parents[3]
E5 = PIPELINE_B.parent
for root in (E5, PIPELINE_B):
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

from e5b.serving import Release  # noqa: E402  (needs the source roots above)

TASKS = ("regression", "classification")
DATE_COLUMNS = ("purchase_ts", "carrier_ts", "ship_limit", "prediction_ts", "lead_label_ts", "review_label_ts")

app = FastAPI(title="Team 11 frozen model API", version="1.0")


class Rows(BaseModel):
    rows: list[dict]


@lru_cache(maxsize=None)
def release(task: str) -> Release:
    return Release.load(task)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "tasks": list(TASKS), "thresholds": release("classification").threshold}


@app.post("/predict/{task}")
def predict(task: str, body: Rows) -> dict:
    if task not in TASKS:
        raise HTTPException(status_code=404, detail=f"unknown task {task!r}; expected one of {TASKS}")
    if not body.rows:
        raise HTTPException(status_code=422, detail="no rows")
    frame = pd.DataFrame(body.rows)
    for column in DATE_COLUMNS:
        if column in frame:
            frame[column] = pd.to_datetime(frame[column], errors="coerce").dt.tz_localize(None)
    result = release(task).predict(frame)
    result = result.astype(object).where(pd.notna(result), None)
    return {"predictions": result.replace({np.bool_(True): True, np.bool_(False): False}).to_dict(orient="records")}
