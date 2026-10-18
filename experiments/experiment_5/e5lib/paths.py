"""Every path used by Experiment 5 (README section 13.1).

No stage hard-codes a path. Writes are allowed only inside the Experiment 5 folder
(containment rule, README section 0.1). Set E5_ROOT to point the foundation at another
copy of the folder (used by the tests).
"""
from __future__ import annotations

import os
from pathlib import Path

from . import stage_rank

E5 = Path(os.environ.get("E5_ROOT", Path(__file__).resolve().parents[1])).resolve()
REPO = Path(os.environ.get("E5_REPO_ROOT", Path(__file__).resolve().parents[3])).resolve()


class ContainmentError(RuntimeError):
    """A write was attempted outside experiments/experiment_5/."""


def stage_dir(stage: str, task: str) -> Path:
    stage_rank(stage)
    return E5 / "stages" / stage / task


def outputs_dir(stage: str, task: str) -> Path:
    return stage_dir(stage, task) / "outputs"


def review_dir(stage: str, task: str, round_: int) -> Path:
    if round_ < 1:
        raise ValueError("review rounds start at 1")
    return stage_dir(stage, task) / "review" / f"round_{round_}"


def raw_data_dir() -> Path:
    """Canvas copy of the nine Olist CSVs (read-only, outside Experiment 5)."""
    return REPO / "data" / "raw"


def reference_dir() -> Path:
    """Read-only reference material (e.g. IBGE geography) outside Experiment 5."""
    return REPO / "docs" / "references"


def spec_path(name: str) -> Path:
    return E5 / "spec" / name


def evidence_dir() -> Path:
    return E5 / "evidence"


def assert_inside_e5(path: Path) -> Path:
    """Return the resolved path, or raise if it is outside the Experiment 5 folder."""
    resolved = Path(path).resolve()
    if resolved != E5 and E5 not in resolved.parents:
        raise ContainmentError(f"refusing to write outside {E5}: {resolved}")
    return resolved


def rel(path: Path) -> str:
    """Path relative to the repository root, with forward slashes (for manifests and links)."""
    resolved = Path(path).resolve()
    try:
        return resolved.relative_to(REPO).as_posix()
    except ValueError:
        return resolved.as_posix()
