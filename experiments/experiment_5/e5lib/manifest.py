"""Run manifests and staleness (README sections 6.1 and 13.1).

Every run.py ends with manifest.write(...). The manifest records the run identity
(run_id, git commit and dirty flag), sha256 of the stage code, the foundation code,
protocol.yaml, every file read and every output, plus Python and package versions,
the seed and the runtime. status() compares the current state with the manifest.
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import time
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path
from typing import Iterable

from . import data, protocol
from .paths import E5, REPO, assert_inside_e5, outputs_dir, rel, spec_path, stage_dir

MANIFEST = "_manifest.json"
PACKAGES = ("numpy", "pandas", "scikit-learn", "scipy", "joblib", "matplotlib", "PyYAML")
_STARTED = time.time()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _hash_files(paths: Iterable[Path]) -> dict[str, str]:
    return {rel(p): sha256(p) for p in sorted(set(Path(p).resolve() for p in paths)) if p.is_file()}


def code_files(stage: str, task: str) -> list[Path]:
    return sorted(stage_dir(stage, task).glob("*.py"))


def foundation_files() -> list[Path]:
    return sorted((E5 / "e5lib").glob("*.py")) + [E5 / "run_pipeline.py"]


def output_files(stage: str, task: str) -> list[Path]:
    out = outputs_dir(stage, task)
    return sorted(p for p in out.rglob("*") if p.is_file() and p.name != MANIFEST) if out.exists() else []


# Files a run or the review process writes; they never make a run "dirty".
GENERATED = ("stages/*/*/outputs/**", "stages/*/*/review/**", "stages/*/*/STAGE.md", "spec/protocol.yaml",
             "evidence/build/**", "evidence/build_draft/**")


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=E5, capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def git_state() -> dict[str, object]:
    """HEAD commit, and whether code or spec in Experiment 5 differs from it (generated files excluded)."""
    commit = git("rev-parse", "HEAD")
    excludes = [f":(exclude,glob){g}" for g in GENERATED]
    dirty = bool(git("status", "--porcelain", "--", ".", *excludes))
    return {"commit": commit or None, "dirty": dirty}


def versions() -> dict[str, str]:
    found = {"python": platform.python_version()}
    for pkg in PACKAGES:
        try:
            found[pkg] = metadata.version(pkg)
        except metadata.PackageNotFoundError:
            found[pkg] = "not installed"
    return found


def write(stage: str, task: str, reads: Iterable[Path] | None = None, seed: int | None = None,
          extra: dict | None = None) -> Path:
    """Write outputs/_manifest.json for this run; returns its path."""
    reads = list(reads) if reads is not None else data.reads()
    protocol_path = spec_path("protocol.yaml")
    layers = protocol.layer_hashes() if protocol_path.exists() else {}
    used = ["pre_registered"] + [f"data_dependent.{s}" for s in protocol.used_sections()]
    manifest = {
        "node": f"{stage}/{task}",
        "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        **git_state(),
        "code": _hash_files(code_files(stage, task)),
        "foundation": _hash_files(foundation_files()),
        "protocol": {k: layers.get(k) for k in used},
        "reads": _hash_files(reads),
        "outputs": _hash_files(output_files(stage, task)),
        "versions": versions(),
        "seed": seed,
        "runtime_s": round(time.time() - _STARTED, 2),
        **({"extra": extra} if extra else {}),
    }
    path = assert_inside_e5(outputs_dir(stage, task) / MANIFEST)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=False), encoding="utf-8", newline="\n")
    return path


def read(stage: str, task: str) -> dict | None:
    path = outputs_dir(stage, task) / MANIFEST
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def status(stage: str, task: str) -> tuple[str, list[str]]:
    """FRESH, STALE or MISSING, with the reasons for STALE."""
    m = read(stage, task)
    if m is None:
        return "MISSING", ["no manifest"]
    reasons = []
    if m["code"] != _hash_files(code_files(stage, task)):
        reasons.append("stage code changed")
    if m.get("foundation") != _hash_files(foundation_files()):
        reasons.append("foundation code changed")
    protocol_path = spec_path("protocol.yaml")
    layers = protocol.layer_hashes() if protocol_path.exists() else {}
    for layer, digest in (m.get("protocol") or {}).items():
        if layers.get(layer) != digest:
            reasons.append(f"protocol.yaml {layer} changed")
    for path_str, digest in m["reads"].items():
        p = REPO / path_str
        if not p.exists() or sha256(p) != digest:
            reasons.append(f"input changed: {path_str}")
    if m["outputs"] != _hash_files(output_files(stage, task)):
        reasons.append("outputs edited after the run")
    return ("STALE", reasons) if reasons else ("FRESH", [])
