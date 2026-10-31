"""Central path definitions for the dashboard app.

The dashboard reads Pipeline B's frozen outputs in place. This module is the only
place that knows their repository-relative locations.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

TASKS = ("regression", "classification")

APP_DIR = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = APP_DIR.parent
DELIVERABLES_DIR = DASHBOARD_DIR.parent
PIPELINE_B = DELIVERABLES_DIR.parent
E5 = PIPELINE_B.parent
REPO = E5.parent.parent
MPL_CONFIG_DIR = APP_DIR / ".matplotlib-cache"
MPL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(MPL_CONFIG_DIR))

BUSINESS_DATA_DIR = REPO / "data" / "business" / "dashboard"
BUSINESS_DATA_PATH = BUSINESS_DATA_DIR / "smartcommerce_consolidated.csv"
EVIDENCE_BUILD_DIR = PIPELINE_B / "evidence" / "build"

# e5b and e5lib are source trees rather than installed packages.
for import_root in (E5, PIPELINE_B):
    value = str(import_root)
    if value not in sys.path:
        sys.path.insert(0, value)


def require_task(task: str) -> str:
    if task not in TASKS:
        raise ValueError(f"Unknown dashboard task {task!r}; expected one of {TASKS}")
    return task


def b10_output(task: str, filename: str) -> Path:
    return PIPELINE_B / "stages" / "b10" / require_task(task) / "outputs" / filename


def b09_output(task: str, filename: str) -> Path:
    return PIPELINE_B / "stages" / "b09" / require_task(task) / "outputs" / filename


def b12_output(task: str, filename: str) -> Path:
    return PIPELINE_B / "stages" / "b12" / require_task(task) / "outputs" / filename


def t1_output(task: str, filename: str) -> Path:
    return (
        PIPELINE_B
        / "stages"
        / "t1_joint_test"
        / require_task(task)
        / "outputs"
        / filename
    )


def evidence_output(task: str, stage: str, filename: str) -> Path:
    require_task(task)
    return PIPELINE_B / "stages" / stage / task / "outputs" / filename


def bundle_dir(task: str, pipeline: str) -> Path:
    require_task(task)
    if pipeline not in {"A", "B"}:
        raise ValueError(f"Unknown pipeline {pipeline!r}; expected 'A' or 'B'")
    return t1_output(task, "bundles") / pipeline


def app_sources_path(task: str) -> Path:
    return b10_output(task, "app_sources.json")


def serving_config_path(task: str) -> Path:
    return b10_output(task, "serving_config.json")


def input_validation_path(task: str) -> Path:
    return b10_output(task, "input_validation.json")


def drift_profile_path(task: str) -> Path:
    return b10_output(task, "drift_profile.json")


def resolve_e5_relative(relative_path: str) -> Path:
    """Resolve a path written relative to experiments/experiment_5/."""
    path = Path(relative_path)
    return path if path.is_absolute() else E5 / path


def require_file(path: Path) -> Path:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def bundle_files(task: str, pipeline: str) -> tuple[Path, Path, Path]:
    root = bundle_dir(task, pipeline)
    return (
        require_file(root / "model.joblib"),
        require_file(root / "schema.json"),
        require_file(root / "training_profile.json"),
    )

