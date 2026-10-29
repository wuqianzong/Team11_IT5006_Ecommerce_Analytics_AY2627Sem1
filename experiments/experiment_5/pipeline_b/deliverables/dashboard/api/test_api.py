"""The API returns exactly what the local serving path returns (run with the app's environment plus httpx)."""
import json
import sys
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

APP_DIR = Path(__file__).resolve().parents[1] / "app"
sys.path.insert(0, str(APP_DIR))

from dashboard_core import alerts  # noqa: E402
from dashboard_core.routing import DashboardRelease  # noqa: E402

from main import app  # noqa: E402

client = TestClient(app)


def test_health_reports_the_serving_thresholds() -> None:
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert abs(body["thresholds"]["B"] - 4 / 15) < 1e-12
    assert abs(body["thresholds"]["A"] - 1 / 6) < 1e-12


def test_api_predictions_equal_local_predictions() -> None:
    queue = alerts.alert_queue()
    ids = tuple(queue["order_id"].iloc[[0, 1, 540, 541]])
    for task in ("classification", "regression"):
        rows = alerts.model_rows(task, ids)
        payload = {"rows": json.loads(rows.to_json(orient="records", date_format="iso"))}
        api = pd.DataFrame(client.post(f"/predict/{task}", json=payload).json()["predictions"])
        local = DashboardRelease(task).predict(rows)
        assert (api["model"] == local["model"]).all()
        assert (api["prediction"].astype(float) - local["prediction"]).abs().max() < 1e-9


def test_unknown_task_is_refused() -> None:
    assert client.post("/predict/other", json={"rows": [{"order_id": "x"}]}).status_code == 404
