"""Record a dated screenshot folder for the register (B-CR-48).

Screenshots are captured by hand from the running app, so there is no stage run. This writes the folder's
_manifest.json (sha256 of every PNG, with the commit it was recorded on) and _evidence_index.json (each PNG tagged
APP.SHOT), so the register can read them as SHOT/<file> (build_evidence_B.verify_manifest_source) and the audit can
check that a screenshot on a slide equals the committed file.

    python experiments/experiment_5/pipeline_b/deliverables/dashboard/app/screenshots/record_screenshots.py 2026-10-30
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[6]


def main(folder: str) -> None:
    out = HERE / folder
    pngs = sorted(out.glob("*.png"))
    git = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True).stdout.strip()  # noqa: E731
    rel = lambda p: p.resolve().relative_to(REPO).as_posix()  # noqa: E731
    manifest = {"node": f"SHOT/{folder}", "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
                "commit": git("rev-parse", "HEAD"), "dirty": bool(git("status", "--porcelain", "--", rel(out))),
                "inputs": {}, "code": {rel(Path(__file__)): hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
                "outputs": {rel(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in pngs}}
    (out / "_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8", newline="\n")
    index = {"node": f"SHOT/{folder}", "files": {p.name: {"ids": ["APP.SHOT"], "kind": "figure"} for p in pngs}}
    (out / "_evidence_index.json").write_text(json.dumps(index, indent=2), encoding="utf-8", newline="\n")
    print(len(pngs), "screenshots recorded")


if __name__ == "__main__":
    main(sys.argv[1])
