"""Pipeline B runner (G-79). Usage: python pipeline_b/b_run.py run --node b02/regression

Imports Pipeline A's code read-only (e5lib) and B's own code (pipeline_b/e5b); refuses to run
when A's code differs from tag e5-A-frozen.
"""
import argparse
import importlib
import sys
from pathlib import Path

B_ROOT = Path(__file__).resolve().parent
sys.path[:0] = [str(B_ROOT.parent), str(B_ROOT)]

BUILT = ("b02", "b04", "b05")


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--node", required=True, help="stage/task, e.g. b02/regression")
    args = ap.parse_args()
    stage, task = args.node.split("/")
    if stage not in BUILT or task not in ("regression", "classification"):
        raise SystemExit(f"unknown or not yet built node {args.node}; built stages: {BUILT}")
    importlib.import_module(f"e5b.{stage}").run(task)
    return 0


if __name__ == "__main__":
    sys.exit(main())
