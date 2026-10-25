"""Pipeline B environment: folders, the A-frozen guard and B's output writer.

B writes only under pipeline_b/. It reuses A's Writer for every file format (tables, JSON,
figures, checks, evidence cards) but points it at pipeline_b/stages/<stage>/<task>/outputs and
writes B's own manifest, so nothing in A's stages/ is touched (G-79).
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from e5lib import manifest as a_manifest
from e5lib.outputs import INDEX, Writer
from e5lib.paths import E5, assert_inside_e5, rel

B_ROOT = E5 / "pipeline_b"
A_FROZEN_TAG = "e5-A-frozen"
STAGES = ("b02", "b04", "b05", "b06", "b07", "b08", "t1_joint_test", "b09", "doc_support")
_STARTED = time.time()


def b_outputs_dir(stage: str, task: str) -> Path:
    if stage not in STAGES:
        raise ValueError(f"unknown Pipeline B stage {stage!r}")
    return B_ROOT / "stages" / stage / task / "outputs"


def _git(*args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=E5, capture_output=True, check=True).stdout


def assert_a_frozen() -> dict[str, str]:
    """Every A foundation file must equal its copy at tag e5-A-frozen; returns their hashes."""
    hashes, changed = {}, []
    for p in a_manifest.foundation_files():
        current = a_manifest.sha256(p)
        frozen = hashlib.sha256(_git("show", f"{A_FROZEN_TAG}:./{p.relative_to(E5).as_posix()}")).hexdigest()
        hashes[rel(p)] = current
        if current != frozen:
            changed.append(rel(p))
    if changed:
        raise SystemExit(f"Pipeline B refuses to run: A's code differs from {A_FROZEN_TAG}: {changed}")
    return hashes


def _id_key(s: str):
    head, _, tail = s.partition(".")
    return (head, int(tail) if tail.isdigit() else tail)


class BWriter(Writer):
    """A's Writer, writing into pipeline_b/stages/<stage>/<task>/outputs with B's manifest."""

    def __init__(self, stage: str, task: str, clean: bool = True):
        self.stage, self.task = stage, task
        self.dir = assert_inside_e5(b_outputs_dir(stage, task))
        if clean and self.dir.exists():
            shutil.rmtree(self.dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.index = {"node": f"B/{stage}/{task}", "pipeline": "B", "files": {}, "checks": [],
                      "deviations": {}, "cards": {}}
        self._decisions = []
        self.reads: list[Path] = []

    def _tag(self, relpath: str, ids: Iterable[str], kind: str) -> None:
        entry = self.index["files"].setdefault(relpath, {"ids": [], "kind": kind})
        entry["ids"] = sorted(set(entry["ids"]) | set(ids), key=_id_key)

    def read(self, path: Path) -> Path:
        """Record an input file for the manifest and return it."""
        self.reads.append(Path(path))
        return Path(path)

    def finish(self, seed: int | None = None, extra: dict | None = None) -> Path:
        if self._decisions:
            ids = sorted({i for d in self._decisions for i in d["ids"]}, key=_id_key)
            self.json("decision", self._decisions, ids)
        self.index["checks_failed"] = [c["name"] for c in self.index["checks"] if not c["passed"]]
        self._path(INDEX).write_text(json.dumps(self.index, indent=2), encoding="utf-8", newline="\n")
        dirty = bool(subprocess.run(["git", "status", "--porcelain", "--", "pipeline_b",
                                     ":(exclude,glob)pipeline_b/stages/**"], cwd=E5, capture_output=True,
                                    text=True).stdout.strip())
        outputs = sorted(p for p in self.dir.rglob("*") if p.is_file() and p.name != a_manifest.MANIFEST)
        man = {
            "node": f"B/{self.stage}/{self.task}", "pipeline": "B",
            "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
            "commit": _git("rev-parse", "HEAD").decode().strip(), "dirty": dirty,
            "a_frozen_tag": A_FROZEN_TAG, "a_foundation": assert_a_frozen(),
            "code": {rel(p): a_manifest.sha256(p) for p in sorted((B_ROOT / "e5b").glob("*.py")) + [B_ROOT / "b_run.py"]},
            "reads": {rel(p): a_manifest.sha256(p) for p in sorted(set(self.reads)) if p.is_file()},
            "outputs": {rel(p): a_manifest.sha256(p) for p in outputs},
            "versions": a_manifest.versions(), "seed": seed, "runtime_s": round(time.time() - _STARTED, 2),
            **({"extra": extra} if extra else {}),
        }
        path = self.dir / a_manifest.MANIFEST
        path.write_text(json.dumps(man, indent=2), encoding="utf-8", newline="\n")
        return path
