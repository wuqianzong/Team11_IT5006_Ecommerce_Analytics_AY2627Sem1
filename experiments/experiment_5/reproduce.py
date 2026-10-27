"""Reproduce Experiment 5 in place (README section 12, CR-061).

    python experiments/experiment_5/reproduce.py run [--pipeline a|b]
    python experiments/experiment_5/reproduce.py compare [--tag e5-release-2] [--machine reference|other]

Run this on a clean checkout of the release tag. `run` reruns Pipeline A's s01-s08 and Pipeline B's
stages in order from the raw data. T1 is not rerun: the test cohort was read once (e5-T1-tested), and
its saved predictions and bundles stay as committed (B-G-08 parity checks them). A's s09 and s10 were
replaced by T1, B9 and B10 (G-79) and never ran.

`compare` checks every output file listed in each rerun node's manifest against the hash recorded in
the release tag's manifest, and writes reproduction/reproduction_check.json. On the reference machine
(the lead's Mac, CR-056) files must be identical; gzip files are compared on their content, model
pickles and PNGs are reported but not gated. On another machine numbers are judged by tolerance:
predictions 1e-9, refitted scores 2e-3 (absolute), counts and labels equal.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

E5 = Path(__file__).resolve().parent
REPO = E5.parents[1]
OUT = E5 / "reproduction"

A_NODES = ["s01_problem/common", "s02_data/common"] + [
    f"{s}/{t}" for s in ("s03_eda", "s04_features", "s05_partition", "s06_training", "s07_tuning",
                         "s08_selection") for t in ("regression", "classification")]
B_NODES = [f"{s}/{t}" for s in ("b02", "b04", "b05", "b06", "b07", "b08", "b09", "doc_support", "b10", "b12")
           for t in ("regression", "classification")]
NOT_GATED = (".joblib", ".pkl", ".png")


def manifest_path(node: str) -> Path:
    stage, task = node.split("/")
    base = E5 / "stages" if not stage.startswith(("b", "doc_")) else E5 / "pipeline_b" / "stages"
    return base / stage / task / "outputs" / "_manifest.json"


def cmd_run(args) -> int:
    OUT.mkdir(exist_ok=True)
    py = sys.executable
    steps = []
    if args.pipeline in (None, "a"):
        steps += [(n, [py, str(E5 / "run_pipeline.py"), "run", "--node", n]) for n in A_NODES]
    if args.pipeline in (None, "b"):
        steps += [(n, [py, str(E5 / "pipeline_b" / "b_run.py"), "run", "--node", n]) for n in B_NODES]
    log = OUT / "run_log.txt"
    with log.open("a", encoding="utf-8", newline="\n") as fh:
        for node, cmd in steps:
            start = datetime.now(timezone.utc)
            fh.write(f"{start:%Y-%m-%dT%H:%M:%SZ} START {node}\n")
            fh.flush()
            rc = subprocess.run(cmd, cwd=REPO, stdout=fh, stderr=subprocess.STDOUT).returncode
            secs = (datetime.now(timezone.utc) - start).total_seconds()
            fh.write(f"END {node} exit {rc} ({secs:.0f} s)\n")
            fh.flush()
            if rc != 0:
                fh.write("STOPPED: a node failed\n")
                return rc
        fh.write("ALL NODES DONE\n")
    return 0


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _git_show(tag: str, rel: str) -> bytes | None:
    r = subprocess.run(["git", "show", f"{tag}:{rel}"], cwd=REPO, capture_output=True)
    return r.stdout if r.returncode == 0 else None


def _numeric_diff(old: bytes, new: bytes, name: str) -> tuple[str, float | None]:
    import numpy as np
    import pandas as pd
    if name.endswith(".gz"):
        old, new = gzip.decompress(old), gzip.decompress(new)
        if old == new:
            return "identical content (gzip header only)", 0.0
        name = name[:-3]
    if name.endswith(".csv"):
        a, b = pd.read_csv(io.BytesIO(old)), pd.read_csv(io.BytesIO(new))
        if list(a.columns) != list(b.columns) or a.shape != b.shape:
            return "DIFFERENT shape or columns", None
        num = a.select_dtypes("number").columns
        other = [c for c in a.columns if c not in num]
        if not a[other].astype(str).equals(b[other].astype(str)):
            return "DIFFERENT text or labels", None
        d = float(np.nanmax(np.abs(a[num].to_numpy(float) - b[num].to_numpy(float)))) if len(num) else 0.0
        return ("numbers within 1e-9" if d <= 1e-9 else "numbers within 2e-3" if d <= 2e-3
                else "DIFFERENT numbers"), d
    if name.endswith(".json"):
        def flat(x, p=""):
            if isinstance(x, dict):
                for k, v in x.items():
                    yield from flat(v, f"{p}.{k}")
            elif isinstance(x, list):
                for i, v in enumerate(x):
                    yield from flat(v, f"{p}[{i}]")
            else:
                yield p, x
        fa, fb = dict(flat(json.loads(old))), dict(flat(json.loads(new)))
        if fa.keys() != fb.keys():
            return "DIFFERENT keys", None
        d, text = 0.0, []
        for k in fa:
            va, vb = fa[k], fb[k]
            if isinstance(va, (int, float)) and isinstance(vb, (int, float)) and not isinstance(va, bool):
                d = max(d, abs(float(va) - float(vb)))
            elif va != vb:
                text.append(k)
        volatile = ("run_id", "commit", "runtime", "created", "dirty", "generated", "_at", "timestamp")
        if any(not any(v in k for v in volatile) for k in text):
            return "DIFFERENT text values", None
        return ("numbers within 1e-9" if d <= 1e-9 else "numbers within 2e-3" if d <= 2e-3
                else "DIFFERENT numbers"), d
    return "DIFFERENT bytes", None


def cmd_compare(args) -> int:
    OUT.mkdir(exist_ok=True)
    nodes, summary = [], {}
    for node in A_NODES + B_NODES:
        mp = manifest_path(node)
        rel_m = mp.relative_to(REPO).as_posix()
        old_m, new_m = _git_show(args.tag, rel_m), json.loads(mp.read_text(encoding="utf-8"))
        if old_m is None:
            nodes.append({"node": node, "result": "no manifest at the release tag"})
            continue
        old_m = json.loads(old_m)
        rerun = new_m.get("run_id") != old_m.get("run_id")
        files = []
        for rel, old_sha in old_m["outputs"].items():
            name = Path(rel).name
            if name in ("_manifest.json", "_evidence_index.json"):
                continue
            p = REPO / rel
            if not p.exists():
                res, d = "MISSING", None
            else:
                new_b = p.read_bytes()
                if _sha(new_b) == old_sha:
                    res, d = "identical", 0.0
                elif rel.endswith(NOT_GATED):
                    res, d = "bytes differ (not gated)", None
                else:
                    res, d = _numeric_diff(_git_show(args.tag, rel) or b"", new_b, name)
            summary[res] = summary.get(res, 0) + 1
            files.append({"file": rel, "result": res, "max_abs_diff": d})
        nodes.append({"node": node, "release_run": old_m.get("run_id"), "rerun": new_m.get("run_id"),
                      "rerun_happened": rerun, "files": files})
    gate_ok = {"identical", "identical content (gzip header only)", "bytes differ (not gated)"}
    if args.machine == "other":
        gate_ok |= {"numbers within 1e-9", "numbers within 2e-3"}
    else:
        gate_ok |= {"numbers within 1e-9"}
    all_rerun = all(n.get("rerun_happened") for n in nodes if "files" in n)
    verdict = "PASS" if all_rerun and set(summary) <= gate_ok else "FAIL"
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, capture_output=True, text=True).stdout.strip()
    result = {"release_tag": args.tag, "checkout": head, "machine": args.machine,
              "platform": platform.platform(), "python": platform.python_version(),
              "rule": "CR-056 hashes" if args.machine == "reference" else "CR-056 tolerance",
              "t1": "not rerun (single read, e5-T1-tested); saved predictions and bundles kept",
              "all_nodes_rerun": all_rerun, "summary": summary, "verdict": verdict, "nodes": nodes}
    (OUT / "reproduction_check.json").write_text(json.dumps(result, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps({k: result[k] for k in ("verdict", "all_nodes_rerun", "summary")}, indent=2))
    return 0 if verdict == "PASS" else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--pipeline", choices=("a", "b"))
    c = sub.add_parser("compare")
    c.add_argument("--tag", default="e5-release-2")
    c.add_argument("--machine", choices=("reference", "other"), default="other")
    args = ap.parse_args()
    return cmd_run(args) if args.cmd == "run" else cmd_compare(args)


if __name__ == "__main__":
    sys.exit(main())
