from pathlib import Path

import pandas as pd

from dashboard_core import paths
from dashboard_core.classification_tab import _stored_threshold_choices


APP_DIR = Path(__file__).resolve().parents[1]
PLAN = paths.DASHBOARD_DIR / "DASHBOARD_PLAN.md"


def test_plan_is_approved() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "Status: APPROVED" in text


def test_every_threshold_slider_stop_is_a_stored_threshold() -> None:
    curve = pd.read_csv(
        paths.evidence_output(
            "classification", "b09", "threshold_options_curve.csv"
        )
    )
    validation = curve[curve["period"] == "validation (out-of-fold)"]
    stored = {round(float(value), 12) for value in validation["threshold"]}
    choices = _stored_threshold_choices(validation)
    assert choices
    assert all(round(value, 12) in stored for value in choices)
    assert min(choices) <= 0.02 + 1e-9
    assert max(choices) >= 0.60 - 1e-9


def test_forbidden_scope_and_threshold_wording_is_absent() -> None:
    source = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (APP_DIR / "dashboard_core").rglob("*.py")
    ).lower()
    assert "not served" not in source
    assert "4/16" not in source

