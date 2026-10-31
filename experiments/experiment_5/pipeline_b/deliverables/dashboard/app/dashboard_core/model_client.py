"""Where predictions come from: the hosted model API when MODEL_API_URL is set, else the local bundles.

Both paths run the same frozen T1 bundles through e5b.serving.Release (plan revision 2, 6a.2).
The API is the service in `deliverables/dashboard/api/`; it fits nothing.
"""
from __future__ import annotations

import json
import os
import urllib.request

import pandas as pd

from dashboard_core.routing import DashboardRelease

API_ENV = "MODEL_API_URL"
TIMEOUT_SECONDS = 90  # a free-tier service may need to wake up first


def api_url() -> str | None:
    value = os.environ.get(API_ENV, "").strip()
    return value.rstrip("/") or None


def source_label() -> str:
    url = api_url()
    return f"model API ({url})" if url else "local frozen bundles"


def predict(task: str, frame: pd.DataFrame) -> pd.DataFrame:
    url = api_url()
    if not url:
        return DashboardRelease(task).predict(frame)
    payload = json.dumps(
        {"rows": json.loads(frame.to_json(orient="records", date_format="iso"))}
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{url}/predict/{task}",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        body = json.loads(response.read().decode("utf-8"))
    return pd.DataFrame(body["predictions"])


def check(task: str, frame: pd.DataFrame) -> pd.DataFrame:
    """Input checks run locally: they read only the stored training profiles."""
    return DashboardRelease(task).check(frame)
