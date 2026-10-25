"""EVIDENCE.md lists the current run of every built B stage, and the manifests agree with it."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

B_ROOT = Path(__file__).resolve().parents[1]
T1_TAG = "e5-T1-tested"


def _current_rows():
    text = (B_ROOT / "EVIDENCE.md").read_text()
    table = text.split("## Current runs")[1].split("\n## ")[0]
    rows = re.findall(r"^\| (b\d\d|t1_joint_test|doc_support) \| (\w+) \| (\d{8}T\d{6}Z) \| (\w+) \| ([\w-]+) \|", table, re.M)
    assert rows, "no current rows in EVIDENCE.md"
    return rows


def _code_at_t1_tag(relpath: str) -> bytes:
    repo = B_ROOT.parents[2]
    tagged = subprocess.run(["git", "show", f"{T1_TAG}:{relpath}"], cwd=repo, capture_output=True)
    return tagged.stdout if tagged.returncode == 0 else (repo / relpath).read_bytes()


def test_register_matches_manifests():
    for stage, task, run_id, commit, _tag in _current_rows():
        man = json.loads((B_ROOT / "stages" / stage / task / "outputs" / "_manifest.json").read_text())
        assert man["run_id"] == run_id, f"{stage}/{task}: manifest {man['run_id']}, register {run_id}"
        assert man["commit"].startswith(commit), f"{stage}/{task}: manifest commit {man['commit'][:7]}"
        if stage == "t1_joint_test":
            # the single test read cannot be rerun clean: the code that ran must equal the code at the T1 tag
            # (the working tree until the tag exists)
            for relpath, sha in man["code"].items():
                now = hashlib.sha256(_code_at_t1_tag(relpath)).hexdigest()
                assert now == sha, f"{stage}/{task}: {relpath} differs from the code that read the test"
        else:
            assert not man["dirty"], f"{stage}/{task}: current run was made on a dirty tree"


def test_every_built_stage_is_registered():
    listed = {(s, t) for s, t, *_ in _current_rows()}
    built = {(p.parents[1].name, p.parent.name) for p in (B_ROOT / "stages").glob("*/*/outputs")}
    assert built == listed, f"unregistered: {sorted(built - listed)}; missing: {sorted(listed - built)}"
