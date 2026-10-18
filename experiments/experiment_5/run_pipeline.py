"""Experiment 5 orchestrator (README sections 6.2, 9.1 and 13.3).

    python experiments/experiment_5/run_pipeline.py status
    python experiments/experiment_5/run_pipeline.py run --node s02_data/common
    python experiments/experiment_5/run_pipeline.py run --from s04_features [--task regression]
    python experiments/experiment_5/run_pipeline.py pack --node s02_data/common --round 1
    python experiments/experiment_5/run_pipeline.py check

The run gate: a node runs only when every upstream node is ACCEPTED and FRESH. After a
rerun, a node whose decision.json changed while ACCEPTED is set to REOPENED.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from e5lib import manifest, review, stage_rank  # noqa: E402
from e5lib.paths import E5, outputs_dir, review_dir, stage_dir  # noqa: E402

STATUSES = ("TODO", "IN_PROGRESS", "READY_FOR_REVIEW", "CHANGES_REQUESTED", "ACCEPTED", "REOPENED")


# ---- nodes and stage cards ------------------------------------------------------------
def nodes() -> list[dict]:
    spec = json.loads((E5 / "spec" / "stages.json").read_text(encoding="utf-8"))
    out = []
    for st in spec["stages"]:
        for task in st["tasks"]:
            out.append({"stage": st["id"], "task": task, "node": f"{st['id']}/{task}",
                        "deps": [d.replace("{task}", task) for d in st["depends_on"]]})
    return sorted(out, key=lambda n: (stage_rank(n["stage"]), n["task"]))


def node_map() -> dict[str, dict]:
    return {n["node"]: n for n in nodes()}


def upstream(node: str) -> list[str]:
    nm, seen, todo = node_map(), [], list(node_map()[node]["deps"])
    while todo:
        d = todo.pop()
        if d not in seen:
            seen.append(d)
            todo.extend(nm[d]["deps"])
    return sorted(seen, key=lambda d: stage_rank(d.split("/")[0]))


def card(node: str) -> Path:
    stage, task = node.split("/")
    return stage_dir(stage, task) / "STAGE.md"


def get_status(node: str) -> str:
    m = re.search(r"^status:\s*([A-Z_]+)", card(node).read_text(encoding="utf-8"), re.M)
    return m.group(1) if m else "TODO"


def set_status(node: str, status: str) -> None:
    if status not in STATUSES:
        raise ValueError(status)
    path = card(node)
    text = re.sub(r"^status:\s*[A-Z_]+", f"status: {status}", path.read_text(encoding="utf-8"), count=1, flags=re.M)
    path.write_text(text, encoding="utf-8")


# ---- commands -------------------------------------------------------------------------
def cmd_status(_args) -> int:
    print(f"{'node':38} {'card':18} {'outputs':8} run_id")
    for n in nodes():
        fresh, reasons = manifest.status(n["stage"], n["task"])
        m = manifest.read(n["stage"], n["task"]) or {}
        print(f"{n['node']:38} {get_status(n['node']):18} {fresh:8} {m.get('run_id', '-')}"
              + (f"  ({'; '.join(reasons)})" if fresh == "STALE" else ""))
    return 0


def gate(node: str) -> list[str]:
    problems = []
    for d in upstream(node):
        stage, task = d.split("/")
        if get_status(d) != "ACCEPTED":
            problems.append(f"{d} is {get_status(d)}, not ACCEPTED")
        fresh, reasons = manifest.status(stage, task)
        if fresh != "FRESH":
            problems.append(f"{d} outputs are {fresh}: {'; '.join(reasons)}")
    return problems


def run_node(node: str) -> int:
    stage, task = node.split("/")
    problems = gate(node)
    if problems:
        print(f"REFUSED {node}: upstream not accepted and fresh (README section 9.1)")
        for p in problems:
            print(f"  - {p}")
        return 2
    script = stage_dir(stage, task) / "run.py"
    if not script.exists():
        print(f"{node}: no run.py yet")
        return 2
    decision = outputs_dir(stage, task) / "decision.json"
    before = decision.read_text(encoding="utf-8") if decision.exists() else None
    env = {**os.environ, "PYTHONPATH": str(E5) + os.pathsep + os.environ.get("PYTHONPATH", "")}
    print(f"running {node}")
    rc = subprocess.run([sys.executable, str(script)], cwd=E5, env=env).returncode
    if rc != 0:
        print(f"{node} failed (exit {rc})")
        return rc
    after = decision.read_text(encoding="utf-8") if decision.exists() else None
    status = get_status(node)
    if status == "ACCEPTED" and before != after:
        set_status(node, "REOPENED")
        print(f"{node}: decision.json changed after acceptance -> REOPENED (README section 9.2)")
    elif status == "TODO":
        set_status(node, "IN_PROGRESS")
    return 0


def cmd_run(args) -> int:
    if args.node:
        targets = [args.node]
    else:
        start = stage_rank(args.from_)
        targets = [n["node"] for n in nodes() if stage_rank(n["stage"]) >= start
                   and (args.task is None or n["task"] in (args.task, "common"))]
    for t in targets:
        if t not in node_map():
            print(f"unknown node {t}")
            return 2
        rc = run_node(t)
        if rc:
            return rc
    return 0


def cmd_pack(args) -> int:
    stage, task = args.node.split("/")
    if review_dir(stage, task, args.round).exists():
        print(f"round {args.round} already packed; rounds are append-only (README section 9.1)")
        return 2
    path = review.build_pack(stage, task, args.round)
    set_status(args.node, "READY_FOR_REVIEW")
    print(f"wrote {path}")
    return 0


def cmd_check(_args) -> int:
    ok = True
    for n in nodes():
        if manifest.read(n["stage"], n["task"]) is None:
            continue
        fresh, reasons = manifest.status(n["stage"], n["task"])
        if fresh != "FRESH":
            ok = False
            print(f"STALE {n['node']}: {'; '.join(reasons)}")
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "."], cwd=E5, capture_output=True,
                           text=True).stdout.strip()
    if dirty:
        ok = False
        print("working tree has uncommitted changes in experiments/experiment_5")
    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", str(E5 / "tests")], cwd=E5).returncode
    if tests != 0:
        ok = False
        print("contract tests failed")
    print("CHECK PASSED" if ok else "CHECK FAILED")
    return 0 if ok else 1


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    r = sub.add_parser("run")
    g = r.add_mutually_exclusive_group(required=True)
    g.add_argument("--node")
    g.add_argument("--from", dest="from_")
    r.add_argument("--task", choices=["regression", "classification"])
    pk = sub.add_parser("pack")
    pk.add_argument("--node", required=True)
    pk.add_argument("--round", type=int, required=True)
    sub.add_parser("check")
    args = p.parse_args(argv)
    return {"status": cmd_status, "run": cmd_run, "pack": cmd_pack, "check": cmd_check}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
