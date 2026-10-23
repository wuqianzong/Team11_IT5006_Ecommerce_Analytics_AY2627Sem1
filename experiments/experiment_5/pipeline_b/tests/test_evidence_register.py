"""EVIDENCE.md lists the current run of every built B stage, and the manifests agree with it."""
import json
import re
from pathlib import Path

B_ROOT = Path(__file__).resolve().parents[1]


def _current_rows():
    text = (B_ROOT / "EVIDENCE.md").read_text()
    table = text.split("## Current runs")[1].split("\n## ")[0]
    rows = re.findall(r"^\| (b\d\d) \| (\w+) \| (\d{8}T\d{6}Z) \| (\w+) \| ([\w-]+) \|", table, re.M)
    assert rows, "no current rows in EVIDENCE.md"
    return rows


def test_register_matches_manifests():
    for stage, task, run_id, commit, _tag in _current_rows():
        man = json.loads((B_ROOT / "stages" / stage / task / "outputs" / "_manifest.json").read_text())
        assert man["run_id"] == run_id, f"{stage}/{task}: manifest {man['run_id']}, register {run_id}"
        assert man["commit"].startswith(commit), f"{stage}/{task}: manifest commit {man['commit'][:7]}"
        assert not man["dirty"], f"{stage}/{task}: current run was made on a dirty tree"


def test_every_built_stage_is_registered():
    listed = {(s, t) for s, t, *_ in _current_rows()}
    built = {(p.parents[1].name, p.parent.name) for p in (B_ROOT / "stages").glob("*/*/outputs")}
    assert built == listed, f"unregistered: {sorted(built - listed)}; missing: {sorted(listed - built)}"
