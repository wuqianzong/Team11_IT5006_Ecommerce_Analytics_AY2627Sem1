"""Review packs with the coverage table (README section 9.1).

build_pack(stage, task, round) reads the stage's evidence index, manifest and the approved
solution IDs (spec/solution_ids.json) and writes review/round_N/review_pack.md and pack.json.
Coverage per solution ID: IMPLEMENTED (evidence and no failed check), DEVIATION (recorded
difference from the approved solution) or MISSING (no evidence). A MISSING row or a failed
check blocks acceptance. Rows whose evidence did not change since the previous round are
marked, so reviewers only re-check what changed.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from . import manifest as manifest_mod
from .outputs import INDEX
from .paths import REPO, assert_inside_e5, outputs_dir, rel, review_dir, spec_path

STATUSES = ("IMPLEMENTED", "DEVIATION", "MISSING")


def rel_to_e5(path: Path) -> str:
    from .paths import E5
    return Path(path).resolve().relative_to(E5).as_posix()


def solution_ids(stage: str, task: str) -> list[dict]:
    spec = json.loads(spec_path("solution_ids.json").read_text())
    if stage not in spec:
        raise KeyError(f"no solution IDs listed for {stage}")
    return [s for s in spec[stage] if task in s.get("tasks", [task])]


def github_base() -> str | None:
    try:
        url = subprocess.run(["git", "remote", "get-url", "origin"], cwd=REPO, capture_output=True,
                             text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    m = re.match(r"(?:git@github\.com:|https://github\.com/)(.+?)(?:\.git)?$", url)
    return f"https://github.com/{m.group(1)}" if m else None


def _link(path: str, commit: str | None, base: str | None) -> str:
    if base and commit:
        return f"[{Path(path).name}]({base}/blob/{commit}/{path})"
    return f"`{path}`"


def coverage(stage: str, task: str) -> list[dict]:
    out = outputs_dir(stage, task)
    index = json.loads((out / INDEX).read_text())
    m = manifest_mod.read(stage, task) or {}
    hashes = m.get("outputs", {})
    rows = []
    for sol in solution_ids(stage, task):
        sid = sol["id"]
        files = [f for f, e in index["files"].items() if sid in e["ids"]]
        checks = [c for c in index["checks"] if sid in c["ids"]]
        card = index["cards"].get(sid, {})
        if sid in index["deviations"]:
            status = "DEVIATION"
        elif files or checks or card:
            status = "IMPLEMENTED"
        else:
            status = "MISSING"
        check = "—" if not checks else ("FAIL" if any(not c["passed"] for c in checks) else "PASS")
        evidence = {f: hashes.get(rel(out / f)) for f in files}
        rows.append({"id": sid, "title": sol["title"], "status": status, "checks": check,
                     "files": files, "evidence_hashes": evidence, "card": card,
                     "check_detail": checks, "deviation": index["deviations"].get(sid, "")})
    return rows


def build_pack(stage: str, task: str, round_: int) -> Path:
    out = outputs_dir(stage, task)
    m = manifest_mod.read(stage, task)
    if m is None:
        raise FileNotFoundError(f"{stage}/{task} has no manifest: run the stage first")
    rows = coverage(stage, task)
    prev_file = review_dir(stage, task, round_ - 1) / "pack.json" if round_ > 1 else None
    prev = {r["id"]: r for r in json.loads(prev_file.read_text())["rows"]} if prev_file and prev_file.exists() else {}
    for r in rows:
        r["changed"] = (r["id"] not in prev) or (prev[r["id"]]["evidence_hashes"] != r["evidence_hashes"])

    # Links point at HEAD, which must already contain this run's outputs (commit them first).
    code_commit, base = m.get("commit"), github_base()
    commit = manifest_mod.git("rev-parse", "HEAD") or None
    uncommitted = manifest_mod.git("status", "--porcelain", "--", rel_to_e5(out))
    if uncommitted:
        raise RuntimeError(f"commit {stage}/{task} outputs before packing, so review links resolve")
    counts = {s: sum(r["status"] == s for r in rows) for s in STATUSES}
    failed = sum(r["checks"] == "FAIL" for r in rows)
    ready = counts["MISSING"] == 0 and failed == 0 and not m.get("dirty")
    prefix = rel(out)

    lines = [f"# Review pack: {stage}/{task}, round {round_}", "",
             "| Field | Value |", "| --- | --- |",
             f"| Code commit (run) | `{code_commit}`{' (DIRTY: not eligible for acceptance)' if m.get('dirty') else ''} |",
             f"| Evidence commit (links) | `{commit}` |",
             f"| Run ID | `{m['run_id']}` |",
             f"| Coverage | {counts['IMPLEMENTED']} implemented, {counts['DEVIATION']} deviation, {counts['MISSING']} missing |",
             f"| Failed checks | {failed} |",
             f"| Ready for acceptance | {'yes' if ready else 'no'} |", "",
             "## Coverage", "",
             "| ID | Solution step | Coverage | Checks | Changed since last round | Evidence |",
             "| --- | --- | --- | --- | --- | --- |"]
    for r in rows:
        ev = ", ".join(_link(f"{prefix}/{f}", commit, base) for f in r["files"]) or "—"
        lines.append(f"| [{r['id']}](#card-{r['id'].replace('.', '-')}) | {r['title']} | {r['status']} | "
                     f"{r['checks']} | {'yes' if r['changed'] else 'no'} | {ev} |")
    lines += ["", "## Evidence cards", ""]
    for r in rows:
        c = r["card"]
        lines += [f"### {r['id']} {r['title']} {{#card-{r['id'].replace('.', '-')}}}", "",
                  f"Coverage: **{r['status']}**; checks: **{r['checks']}**.", ""]
        for key, label in (("done", "What was done"), ("inputs", "Inputs"), ("expectation", "Expectation"),
                           ("observation", "Observation"), ("reasoning", "Reasoning"), ("conclusion", "Conclusion")):
            if c.get(key):
                lines.append(f"- **{label}:** {c[key]}")
        if c.get("label"):
            lines.append(f"- **Claim type:** {c['label']}")
        if r["deviation"]:
            lines.append(f"- **Deviation:** {r['deviation']}")
        for ch in r["check_detail"]:
            lines.append(f"- **Check {ch['name']}:** {'PASS' if ch['passed'] else 'FAIL'} {ch['detail']}".rstrip())
        for f in r["files"]:
            if f.endswith(".png"):
                lines.append(f"\n![{f}](../../outputs/{f})\n")
        if r["files"]:
            lines.append("- **Files:** " + ", ".join(_link(f"{prefix}/{f}", commit, base) for f in r["files"]))
        lines.append("")

    target = assert_inside_e5(review_dir(stage, task, round_))
    target.mkdir(parents=True, exist_ok=True)
    (target / "review_pack.md").write_text("\n".join(lines))
    (target / "pack.json").write_text(json.dumps({"stage": stage, "task": task, "round": round_,
                                                  "code_commit": code_commit, "evidence_commit": commit,
                                                  "run_id": m["run_id"],
                                                  "dirty": m.get("dirty"), "ready": ready,
                                                  "rows": rows}, indent=2))
    return target / "review_pack.md"
