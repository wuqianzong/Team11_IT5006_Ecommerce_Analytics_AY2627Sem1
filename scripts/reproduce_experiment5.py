"""Rerun Experiment 5 (Milestone 3) on any machine and check it against the release.

    python scripts/reproduce_experiment5.py [--workdir DIR] [--tag e5-reproduced] [--skip-run]

Run it with the Experiment 5 interpreter (Python 3.13, experiments/experiment_5/requirements.txt), from a
clone of the repository. It never changes this checkout: everything happens in a separate git worktree at
the reproduced release (default ../e5-reproduce-check).

Steps
1. Create the worktree at tag e5-reproduced (release e5-release-2 plus reproduce.py).
2. Rerun the same 34 stage/task nodes, in the same order and with the same commands as
   `experiments/experiment_5/reproduce.py run`: Pipeline A s01-s08, Pipeline B B2-B12. T1 is not rerun.
3. Check every modelling decision against the release (decision check, this script).
4. Run `experiments/experiment_5/reproduce.py compare --machine other` (file-by-file check, CR-056).

Two exact-match safeguards are built for the team's reference machine, where a rerun is byte-identical
(README Appendix A.2). On another machine, floating-point differences move refitted scores in the fourth
decimal, and these safeguards would stop the rerun although no decision changed:
- run_pipeline.py marks an ACCEPTED stage REOPENED when any text in its decision.json changes (the notes
  print scores to 4 decimals), and the next stage then refuses to start. This script restores the
  committed status cards (STAGE.md) after each node, because a reproduction is a check, not a new review.
  It records which nodes would have been reopened.
- B10 classification fails its check that the frozen recipes recompute their sha256, because those recipe
  files also record out-of-fold statistics. This script continues past that one check only, and records it.
Any other failure stops the run.

Outputs, in the worktree's experiments/experiment_5/reproduction/:
- cross_machine_run.json: each node's exit code, time, and the safeguards passed over;
- decision_check.json: every decision field compared with the release (PASS or FAIL);
- reproduction_check.json: the file-by-file comparison written by reproduce.py compare.
Nothing is committed.
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import platform
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
E5_REL = Path("experiments") / "experiment_5"
B10_HASH_CHECK = ("bundle files equal T1's tagged files; frozen recipes recompute their sha256, "
                  "equal their tagged files and match the schemas; training rows and digests recompute")

# Decision check: files that hold decisions, and the fields that are statistics or run metadata rather
# than decisions. Floats are statistics, except threshold values, which are decisions and must be equal.
DECISION_FILES = ("decision.json", "selected_spec.json", "frozen_recipe.json", "adoption_decision.json",
                  "serving_config.json", "counts.json")
SKIP_KEYS = {"notes", "sha256", "run_id", "recorded_utc", "python", "platform", "commit", "code_commit"}
SKIP_PREFIXES = ("oof_",)
SKIP_SUFFIXES = ("_sha256", "_digest")


def git(*args: str, cwd: Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout


def load_nodes(wt: Path):
    spec = importlib.util.spec_from_file_location("e5_reproduce", wt / E5_REL / "reproduce.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.A_NODES, mod.B_NODES


def restore_status_cards(wt: Path) -> None:
    cards = [p for p in git("ls-files", "--", str(E5_REL), cwd=wt).splitlines() if p.endswith("STAGE.md")]
    for i in range(0, len(cards), 200):
        git("checkout", "-q", "--", *cards[i:i + 200], cwd=wt)


def only_b10_hash_check_failed(output: str) -> bool:
    for line in output.splitlines():
        if "checks failed:" in line:
            try:
                failed = ast.literal_eval(line.split("checks failed:", 1)[1].strip())
            except (ValueError, SyntaxError):
                return False
            return bool(failed) and all(item == B10_HASH_CHECK for item in failed)
    return False


def run_nodes(wt: Path) -> dict:
    a_nodes, b_nodes = load_nodes(wt)
    py, e5 = sys.executable, wt / E5_REL
    steps = [(n, [py, str(e5 / "run_pipeline.py"), "run", "--node", n]) for n in a_nodes]
    steps += [(n, [py, str(e5 / "pipeline_b" / "b_run.py"), "run", "--node", n]) for n in b_nodes]
    out_dir = e5 / "reproduction" / "cross_machine_logs"
    out_dir.mkdir(parents=True, exist_ok=True)
    rows, stopped = [], None
    for i, (node, cmd) in enumerate(steps, 1):
        t0 = time.time()
        print(f"[{i:2d}/{len(steps)}] {node} ...", end=" ", flush=True)
        r = subprocess.run(cmd, cwd=wt, capture_output=True, text=True)
        text = r.stdout + r.stderr
        (out_dir / (node.replace("/", "__") + ".log")).write_text(text, encoding="utf-8", newline="\n")
        reopened = "REOPENED" in r.stdout
        restore_status_cards(wt)
        row = {"node": node, "exit": r.returncode, "seconds": round(time.time() - t0),
               "would_be_reopened": reopened, "safeguard_passed_over": None}
        if reopened:
            row["safeguard_passed_over"] = "decision.json text changed (scores at 4 decimals); status card restored"
        if r.returncode != 0:
            if node == "b10/classification" and only_b10_hash_check_failed(text):
                row["safeguard_passed_over"] = "B10 frozen-recipe sha256 check (recipes record out-of-fold statistics)"
            else:
                stopped = node
        rows.append(row)
        note = f" ({row['safeguard_passed_over']})" if row["safeguard_passed_over"] else ""
        print(f"exit {r.returncode}, {row['seconds']} s{note}", flush=True)
        if stopped:
            print(f"STOPPED: {node} failed for a reason other than the two known safeguards; see "
                  f"{out_dir / (node.replace('/', '__') + '.log')}")
            break
    return {"nodes": rows, "stopped_at": stopped, "all_nodes_run": stopped is None and len(rows) == len(steps)}


def decision_fields(obj, path=""):
    """Yield (path, value) for decision fields: strings, booleans, integers and threshold values."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in SKIP_KEYS or k.startswith(SKIP_PREFIXES) or k.endswith(SKIP_SUFFIXES):
                continue
            yield from decision_fields(v, f"{path}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from decision_fields(v, f"{path}[{i}]")
    elif isinstance(obj, float):
        if "threshold" in path.lower() and path.endswith("/value"):
            yield path, obj
    else:
        yield path, obj


def check_decisions(wt: Path, tag: str) -> dict:
    files = sorted(p for name in DECISION_FILES for p in (wt / E5_REL).rglob(f"stages/*/*/outputs/{name}"))
    results = []
    for p in files:
        rel = p.relative_to(wt).as_posix()
        old = subprocess.run(["git", "show", f"{tag}:{rel}"], cwd=wt, capture_output=True)
        if old.returncode != 0:
            continue
        a = dict(decision_fields(json.loads(old.stdout.decode("utf-8"))))
        b = dict(decision_fields(json.loads(p.read_text(encoding="utf-8"))))
        diffs = [{"field": k, "release": a.get(k), "rerun": b.get(k)} for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)]
        results.append({"file": rel, "fields_compared": len(a), "differences": diffs})
    parity = {}
    for task in ("regression", "classification"):
        f = wt / E5_REL / "pipeline_b" / "stages" / "b10" / task / "outputs" / "parity.json"
        parity[task] = json.loads(f.read_text(encoding="utf-8")).get("passed") if f.exists() else None
    ok = all(not r["differences"] for r in results) and all(v is True for v in parity.values())
    return {"rule": "every decision field equal to the release; frozen T1 models re-predict the stored test "
                    "predictions within 1e-9 (B10 parity)",
            "verdict": "PASS" if ok else "FAIL", "files_checked": len(results),
            "files_with_differences": [r for r in results if r["differences"]],
            "b10_parity_passed": parity}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--workdir", type=Path, default=REPO.parent / "e5-reproduce-check")
    ap.add_argument("--tag", default="e5-reproduced")
    ap.add_argument("--skip-run", action="store_true", help="only rerun the checks on an existing worktree")
    args = ap.parse_args()
    wt = args.workdir.resolve()

    if not args.skip_run:
        if wt.exists():
            print(f"{wt} already exists; remove it (git worktree remove --force {wt}) or pass --workdir")
            return 2
        subprocess.run(["git", "fetch", "-q", "--tags", "origin"], cwd=REPO)
        git("worktree", "add", "--detach", str(wt), args.tag, cwd=REPO)
        print(f"worktree at {args.tag}: {wt}")
    run = run_nodes(wt) if not args.skip_run else {"nodes": [], "stopped_at": None, "all_nodes_run": None}
    out = wt / E5_REL / "reproduction"
    if not args.skip_run:
        run.update({"tag": args.tag, "python": platform.python_version(), "platform": platform.platform()})
        (out / "cross_machine_run.json").write_text(json.dumps(run, indent=1) + "\n", encoding="utf-8", newline="\n")
        if run["stopped_at"]:
            return 1

    dec = check_decisions(wt, "e5-release-2")
    (out / "decision_check.json").write_text(json.dumps(dec, indent=1) + "\n", encoding="utf-8", newline="\n")
    subprocess.run([sys.executable, str(wt / E5_REL / "reproduce.py"), "compare", "--machine", "other"], cwd=wt,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    cmp_ = json.loads((out / "reproduction_check.json").read_text(encoding="utf-8"))

    passed_over = [r for r in run["nodes"] if r["safeguard_passed_over"]]
    print("\n=== Summary")
    if not args.skip_run:
        print(f"Nodes run: {len(run['nodes'])}; safeguards passed over on: "
              f"{', '.join(r['node'] for r in passed_over) or 'none (byte-identical machine)'}")
    print(f"Decision check: {dec['verdict']} ({dec['files_checked']} decision files; B10 parity {dec['b10_parity_passed']})")
    print(f"File-by-file check (reproduce.py compare, CR-056): {cmp_['verdict']} {cmp_['summary']}")
    print("On a machine other than the reference Mac the file-by-file check is expected to report FAIL on refitted")
    print("counts and scores; README Appendix A.2 explains why and what size of difference to expect.")
    print(f"Reports: {out / 'cross_machine_run.json'}, {out / 'decision_check.json'}, {out / 'reproduction_check.json'}")
    return 0 if dec["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
