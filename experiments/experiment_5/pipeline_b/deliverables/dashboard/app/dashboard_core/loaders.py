"""Read-only loaders for dashboard manifests and frozen bundle metadata."""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from dashboard_core import paths


@dataclass(frozen=True)
class AppSourceElement:
    panel: str
    element: str
    relative_file: str
    evidence_id: str
    exists: bool
    id_tagged: bool
    path: Path


@dataclass(frozen=True)
class AppSources:
    task: str
    rule: str
    elements: tuple[AppSourceElement, ...]


@dataclass(frozen=True)
class TaskConfig:
    task: str
    app_sources: AppSources
    serving_config: dict[str, Any]
    input_validation: dict[str, Any]
    drift_profile: dict[str, Any]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(paths.require_file(path).read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def load_app_sources(task: str) -> AppSources:
    raw = _read_json(paths.app_sources_path(task))
    elements = tuple(
        AppSourceElement(
            panel=str(item["panel"]),
            element=str(item["element"]),
            relative_file=str(item["file"]),
            evidence_id=str(item["evidence_id"]),
            exists=bool(item["exists"]),
            id_tagged=bool(item["id_tagged"]),
            path=paths.resolve_e5_relative(str(item["file"])),
        )
        for item in raw["elements"]
    )
    return AppSources(task=task, rule=str(raw["rule"]), elements=elements)


@lru_cache(maxsize=None)
def load_serving_config(task: str) -> dict[str, Any]:
    return _read_json(paths.serving_config_path(task))


@lru_cache(maxsize=None)
def load_input_validation(task: str) -> dict[str, Any]:
    return _read_json(paths.input_validation_path(task))


@lru_cache(maxsize=None)
def load_drift_profile(task: str) -> dict[str, Any]:
    return _read_json(paths.drift_profile_path(task))


@lru_cache(maxsize=None)
def load_bundle_schema(task: str, pipeline: str) -> dict[str, Any]:
    _, schema_path, _ = paths.bundle_files(task, pipeline)
    return _read_json(schema_path)


@lru_cache(maxsize=None)
def load_bundle_paths(task: str) -> dict[str, dict[str, Path]]:
    return {
        pipeline: {
            "model": model_path,
            "schema": schema_path,
            "training_profile": profile_path,
        }
        for pipeline in ("A", "B")
        for model_path, schema_path, profile_path in (
            paths.bundle_files(task, pipeline),
        )
    }


@lru_cache(maxsize=None)
def load_task_config(task: str) -> TaskConfig:
    return TaskConfig(
        task=task,
        app_sources=load_app_sources(task),
        serving_config=load_serving_config(task),
        input_validation=load_input_validation(task),
        drift_profile=load_drift_profile(task),
    )


def missing_app_source_files(task: str) -> list[str]:
    return [
        element.relative_file
        for element in load_app_sources(task).elements
        if not element.path.is_file()
    ]


def untagged_app_sources(task: str) -> list[str]:
    return [
        element.relative_file
        for element in load_app_sources(task).elements
        if not element.id_tagged
    ]

