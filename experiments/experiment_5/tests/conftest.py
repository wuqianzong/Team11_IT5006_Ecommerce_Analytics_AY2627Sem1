"""Contract-test fixtures: a throwaway copy of the Experiment 5 layout (never the real data)."""
from __future__ import annotations

import importlib
import json
import shutil
import sys
from pathlib import Path

import pandas as pd
import pytest
import yaml

REAL_E5 = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REAL_E5))

MODULES = ["e5lib", "e5lib.paths", "e5lib.protocol", "e5lib.data", "e5lib.manifest", "e5lib.cv",
           "e5lib.candidates", "e5lib.factory", "e5lib.metrics", "e5lib.outputs", "e5lib.review",
           "run_pipeline"]


@pytest.fixture()
def e5(tmp_path, monkeypatch):
    """A fresh fake repo with experiments/experiment_5 inside; modules reloaded against it."""
    repo = tmp_path / "repo"
    root = repo / "experiments" / "experiment_5"
    (root / "spec").mkdir(parents=True)
    shutil.copy(REAL_E5 / "spec" / "solution_ids.json", root / "spec" / "solution_ids.json")
    shutil.copy(REAL_E5 / "spec" / "stages.json", root / "spec" / "stages.json")
    (root / "spec" / "protocol.yaml").write_text(yaml.safe_dump({"seed": 42}))
    shutil.copytree(REAL_E5 / "e5lib", root / "e5lib")
    (root / "run_pipeline.py").write_text("# placeholder for foundation hashing\n")
    for st in json.loads((root / "spec" / "stages.json").read_text())["stages"]:
        for task in st["tasks"]:
            d = root / "stages" / st["id"] / task
            d.mkdir(parents=True)
            (d / "STAGE.md").write_text(f"---\nnode: {st['id']}/{task}\nstatus: TODO\n---\n")
    (repo / "data" / "raw").mkdir(parents=True)
    monkeypatch.setenv("E5_ROOT", str(root))
    monkeypatch.setenv("E5_REPO_ROOT", str(repo))
    for name in MODULES:
        if name in sys.modules:
            importlib.reload(sys.modules[name])
        else:
            importlib.import_module(name)
    sys.modules["e5lib.data"]._READS.clear()
    sys.modules["e5lib.protocol"]._USED_SECTIONS.clear()
    return root


def write_records(root: Path, rows: list[dict]) -> Path:
    out = root / "stages" / "s02_data" / "common" / "outputs"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "records.csv.gz"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path
