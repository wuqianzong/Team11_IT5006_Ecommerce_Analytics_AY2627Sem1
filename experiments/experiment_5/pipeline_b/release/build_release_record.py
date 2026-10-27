"""Write the release record pipeline_b/release/<tag>.json (README §7, §12 step 1; CR-058, B-G-12).

    python pipeline_b/release/build_release_record.py e5-release-1

Checks, each recorded with its detail; the record is written only if all pass:
1. A's tree equals tag e5-A-frozen apart from the one allowed G-79 decision-log entry;
2. A's run_pipeline.py check: every failure is the guard finding on pipeline_b/ text IO (recorded deviation, CR-058);
3. B's tests pass (pytest pipeline_b/tests) and change nothing in the tree;
4. every Current row of EVIDENCE.md matches its stage manifest (run ID, commit, clean tree);
5. B's register resolves every placeholder in the report and deck sources;
6. the deliverables audit on the committed inputs passes every check.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

B = Path(__file__).resolve().parents[1]
E5 = B.parent
ROOT = E5.parents[1]
PY = sys.executable
ALLOWED_A_DIFF = {"experiments/experiment_5/spec/blueprints/decision_log.md"}


def sh(*args: str, cwd: Path = E5) -> subprocess.CompletedProcess:
    return subprocess.run(list(args), cwd=cwd, capture_output=True, text=True, encoding="utf-8")


def a_frozen() -> dict:
    out = sh("git", "diff", "--name-only", "e5-A-frozen", "HEAD", "--", "stages", "e5lib", "spec", "tests", "run_pipeline.py").stdout.split()
    extra = sorted(set(out) - ALLOWED_A_DIFF)
    return {"name": "A's tree equals e5-A-frozen (only the G-79 decision-log entry differs)", "passed": not extra,
            "detail": {"differs": sorted(out), "not_allowed": extra}}


def a_check() -> dict:
    r = sh(PY, "run_pipeline.py", "check")
    failed = re.findall(r"^FAILED (\S+)", r.stdout, re.M)
    findings = re.findall(r"'([^']+?\.py):\d+ \w+'", r.stdout)
    only_guard = failed == ["tests/test_guards.py::test_text_io_names_an_encoding"]
    only_b = bool(findings) and all(f.startswith("pipeline_b/") for f in findings)
    summary = re.findall(r"^\d+ (?:failed|passed).*$", r.stdout, re.M)
    ok = r.returncode == 0 or (only_guard and only_b)
    return {"name": "A's run_pipeline.py check passes, apart from the recorded pipeline_b/ text-IO guard finding (CR-058)",
            "passed": ok, "detail": {"returncode": r.returncode, "failed_tests": failed, "summary": summary,
                                      "deviation": None if r.returncode == 0 else "test_text_io_names_an_encoding lists only pipeline_b/ files"}}


def b_tests() -> dict:
    before = sh("git", "status", "--porcelain", "--", "pipeline_b").stdout
    r = sh(PY, "-m", "pytest", "-q", "pipeline_b/tests")
    clean = sh("git", "status", "--porcelain", "--", "pipeline_b").stdout == before   # the tests write nothing tracked
    last = (r.stdout.strip().splitlines() or [""])[-1]
    return {"name": "B's tests pass and change nothing in the tree", "passed": r.returncode == 0 and clean,
            "detail": {"summary": last, "tree_clean_after": clean}}


def evidence() -> tuple[dict, list]:
    table = (B / "EVIDENCE.md").read_text(encoding="utf-8").split("## Superseded")[0]
    rows = re.findall(r"^\| (b\d\d|t1_joint_test|doc_support) \| (\w+) \| (\d{8}T\d{6}Z) \| (\w+) \| ([\w-]+) \|", table, re.M)
    out, ok, bad = [], True, []
    for stage, task, run, commit, tag in rows:
        m = json.loads((B / "stages" / stage / task / "outputs" / "_manifest.json").read_text(encoding="utf-8"))
        match = m["run_id"] == run and m["commit"].startswith(commit)
        clean = not m.get("dirty", False) or stage == "t1_joint_test"   # T1 ran once before its code commit (EVIDENCE.md)
        ok &= match and clean
        if not (match and clean):
            bad.append(f"{stage}/{task}")
        out.append({"pipeline": "B", "node": f"{stage}/{task}", "run_id": run, "commit": m["commit"], "tag": tag})
    return {"name": "every Current row of EVIDENCE.md matches its stage manifest", "passed": ok and bool(rows),
            "detail": {"rows": len(rows), "mismatch": bad}}, out


def a_runs() -> list:
    res = []
    for man in sorted((E5 / "stages").glob("*/*/outputs/_manifest.json")):
        m = json.loads(man.read_text(encoding="utf-8"))
        node = f"{man.parts[-4]}/{man.parts[-3]}"
        res.append({"pipeline": "A", "node": node, "run_id": m.get("run_id"), "commit": m.get("commit"), "tag": "e5-A-frozen"})
    return res


def register() -> dict:
    files = sorted(str(p.relative_to(E5)) for p in (B / "deliverables" / "report").glob("*.md"))
    files += sorted(str(p.relative_to(E5)) for p in (B / "deliverables" / "deck" / "project" / "slides").glob("*"))
    r = sh(PY, "pipeline_b/build_evidence_B.py", "check", *files)
    return {"name": "B's register resolves every placeholder in the report and deck sources", "passed": r.returncode == 0,
            "detail": {"files": len(files), "output": (r.stdout + r.stderr).strip().splitlines()[-3:]}}


def audit(out_dir: Path) -> dict:
    inp = "pipeline_b/deliverables/audit/inputs"
    export = sorted((B / "deliverables" / "audit" / "inputs").glob("report_export_rev*.md"))[-1]
    r = sh(PY, "pipeline_b/audit_deliverables_B.py", "--doc", str(export.relative_to(E5)), "--deck", f"{inp}/deck",
           "--doc-assets", f"{inp}/doc_assets", "--deck-assets", f"{inp}/deck_assets", "--out", str(out_dir / "audit_result.json"))
    lines = [l for l in r.stdout.splitlines() if l.startswith(("PASS", "FAIL"))]
    n_pass = sum(l.startswith("PASS") for l in lines)
    return {"name": "deliverables audit on the committed inputs passes every check", "passed": bool(lines) and n_pass == len(lines),
            "detail": {"passed": n_pass, "checks": len(lines), "report_export": export.name}}


def main(tag: str) -> int:
    rel = B / "release"
    checks = [a_frozen(), a_check(), b_tests()]
    ev, b_runs = evidence()
    checks += [ev, register(), audit(rel)]
    for c in checks:
        print(("PASS" if c["passed"] else "FAIL"), "|", c["name"])
    if not all(c["passed"] for c in checks):
        print("release record NOT written")
        return 1
    head = sh("git", "rev-parse", "HEAD").stdout.strip()
    rec = {"release": tag, "built_on_commit": head, "decisions": ["G-79", "CR-056", "CR-058", "B-G-12"],
           "replaced_under_G79": {"A s08 (8.6-8.8)": "T1 joint test", "A s09": "B9", "A s10": "B10"},
           "reference_machine": "experiment lead's machine (CR-056); B10 round-3 outputs and the register build were produced on Henry's machine",
           "checks": checks, "runs": a_runs() + b_runs}
    (rel / f"{tag}.json").write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {rel / (tag + '.json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "e5-release-1"))
