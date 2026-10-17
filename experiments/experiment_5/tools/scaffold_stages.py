"""Create or refresh Experiment 5 node folders and STAGE.md cards from spec/stages.json.

Run after any edit to spec/stages.json (README section 3.1):

    python experiments/experiment_5/tools/scaffold_stages.py           # apply
    python experiments/experiment_5/tools/scaffold_stages.py --check   # exit 1 if out of date

Safe to rerun. It never deletes folders and never touches a node's code or outputs.
In each STAGE.md it regenerates only `node`, `depends_on` and the GENERATED block;
owner/reviewer/status/reads/writes and all human-written sections are preserved.
Cards that are READY_FOR_REVIEW or ACCEPTED are not changed without --force,
because changing an accepted stage needs a CHANGELOG entry (README section 9.2).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

E5 = Path(__file__).resolve().parents[1]
SPEC = E5 / "spec" / "stages.json"
STAGES = E5 / "stages"
README = E5 / "README.md"

BEGIN, END = "<!-- BEGIN GENERATED from spec/stages.json -->", "<!-- END GENERATED -->"
IDX_BEGIN, IDX_END = "<!-- BEGIN STAGE INDEX from spec/stages.json -->", "<!-- END STAGE INDEX -->"
KEPT_KEYS = ("owner", "reviewer", "status", "reads", "writes")
DEFAULT_KEPT = {
    "owner": "owner: TBD",
    "reviewer": "reviewer: TBD",
    "status": "status: TODO",
    "reads": "reads: []   # exact upstream files used",
    "writes": "writes: []  # every file run.py produces",
}
LOCKED_STATUSES = {"READY_FOR_REVIEW", "ACCEPTED"}

HUMAN_SECTIONS = """
## Review summary (owner fills at gate; cite files, never type numbers from memory)
- What was done:
- Decision and rule applied (`outputs/decision.json`):
- Key evidence (file -> what it shows):
- Limitations:

## Gate check (reviewer)
- [ ] Every gate criterion above is met (note any exception)
- [ ] `run_pipeline.py run --node` reproduces all outputs from a clean tree
- [ ] Standard output shapes and `_manifest.json` present (README section 5.5)

## Deviations from spec
None.

## Open questions

## Sign-off
- Accepted by: - date: - commit: -
"""


def load_nodes() -> list[dict]:
    spec = json.loads(SPEC.read_text())
    nodes, seen_ids = [], set()
    for st in spec["stages"]:
        if st["id"] in seen_ids:
            sys.exit(f"duplicate stage id {st['id']}")
        seen_ids.add(st["id"])
        for task in st["tasks"]:
            purpose = st["purpose"][task] if isinstance(st["purpose"], dict) else st["purpose"]
            nodes.append({
                **st,
                "task": task,
                "node": f"{st['id']}/{task}",
                "purpose": purpose,
                "deps": [d.replace("{task}", task) for d in st["depends_on"]],
            })
    names = {n["node"] for n in nodes}
    for n in nodes:
        for d in n["deps"]:
            if d not in names:
                sys.exit(f"{n['node']} depends on unknown node {d}")
    return nodes


def split_front_matter(text: str) -> tuple[dict[str, str], str]:
    """Return raw top-level front-matter blocks keyed by name, and the body."""
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    blocks: dict[str, list[str]] = {}
    key = None
    for line in m.group(1).splitlines():
        top = re.match(r"^([A-Za-z_]+):", line)
        if top:
            key = top.group(1)
            blocks[key] = [line]
        elif key:
            blocks[key].append(line)
    return {k: "\n".join(v) for k, v in blocks.items()}, m.group(2)


def generated_block(n: dict) -> str:
    lines = [
        BEGIN,
        f"# {n['id']} / {n['task']} - {n['title']}",
        "",
        f"Spec: `spec/pipeline_design.md` -> {n['design_ref']}. "
        f"Teacher/TA rows: `spec/sources.md` (search `{n['id'][:3].upper()}`).",
        *([f"Blueprint: `{n['blueprint']}` (implement only when its status is AGREED)."]
          if n.get("blueprint") else []),
        "",
        f"**Gate question:** {n['gate_question']}",
        "",
        "## Purpose",
        n["purpose"],
        "",
        "## Planned outputs (`outputs/`)",
        *[f"- {o}" for o in n["outputs"]],
        "",
        "## Gate criteria",
        *[f"- {g}" for g in n["gate"]],
        END,
    ]
    return "\n".join(lines)


def render_card(n: dict, old: str | None) -> str:
    kept, body = split_front_matter(old) if old else ({}, "")
    deps = "depends_on: []" if not n["deps"] else "depends_on:\n" + "\n".join(f"  - {d}" for d in n["deps"])
    fm = ["---", f"node: {n['node']}"]
    fm += [kept.get(k, DEFAULT_KEPT[k]) for k in ("owner", "reviewer", "status")]
    fm += [deps]
    fm += [kept.get(k, DEFAULT_KEPT[k]) for k in ("reads", "writes")]
    fm += ["---"]
    gen = generated_block(n)
    if body and BEGIN in body and END in body:
        pre, rest = body.split(BEGIN, 1)
        _, post = rest.split(END, 1)
        new_body = pre + gen + post
    else:
        new_body = "\n" + gen + "\n" + HUMAN_SECTIONS
    return "\n".join(fm) + "\n" + new_body


def stage_index(nodes: list[dict]) -> str:
    spec = json.loads(SPEC.read_text())
    rows = [
        IDX_BEGIN,
        f"_Generated from `spec/stages.json` v{spec['version']} ({spec['design_version']}). Do not edit by hand._",
        "",
        "| Stage | Nodes | Depends on | Key outputs | Gate question |",
        "| --- | --- | --- | --- | --- |",
    ]
    for st in spec["stages"]:
        tasks = ", ".join(st["tasks"])
        deps = ", ".join(sorted({d.split("/")[0] for d in st["depends_on"]})) or "-"
        outs = "; ".join(o.split(" (")[0] for o in st["outputs"][:3])
        rows.append(f"| {st['id']} {st['title']} | {tasks} | {deps} | {outs} | {st['gate_question']} |")
    rows.append(IDX_END)
    return "\n".join(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="report differences, change nothing, exit 1 if any")
    ap.add_argument("--force", action="store_true", help="also refresh READY_FOR_REVIEW/ACCEPTED cards")
    args = ap.parse_args()

    nodes = load_nodes()
    changes, warnings = [], []

    for n in nodes:
        folder = STAGES / n["id"] / n["task"]
        card = folder / "STAGE.md"
        old = card.read_text() if card.exists() else None
        new = render_card(n, old)
        if old == new:
            continue
        status = split_front_matter(old)[0].get("status", "") if old else ""
        if any(s in status for s in LOCKED_STATUSES) and not args.force:
            warnings.append(f"SKIPPED {n['node']} ({status.strip()}): spec changed; "
                            "add a CHANGELOG entry, then rerun with --force")
            continue
        changes.append(("create" if old is None else "update") + f" {card.relative_to(E5)}")
        if not args.check:
            (folder / "outputs").mkdir(parents=True, exist_ok=True)
            (folder / "outputs" / ".gitkeep").touch()
            card.write_text(new)

    readme = README.read_text()
    if IDX_BEGIN in readme and IDX_END in readme:
        pre, rest = readme.split(IDX_BEGIN, 1)
        _, post = rest.split(IDX_END, 1)
        new_readme = pre + stage_index(nodes) + post
        if new_readme != readme:
            changes.append("update README.md stage index")
            if not args.check:
                README.write_text(new_readme)
    else:
        warnings.append("README.md has no stage-index markers; index not updated")

    expected = {n["node"] for n in nodes}
    if STAGES.exists():
        for d in sorted(p for p in STAGES.glob("*/*") if p.is_dir()):
            node = f"{d.parent.name}/{d.name}"
            if node not in expected:
                warnings.append(f"ORPHAN {node}: not in spec/stages.json (not deleted; "
                                "move useful work, then remove it in a reviewed PR)")

    for c in changes:
        print(("WOULD " if args.check else "") + c)
    for w in warnings:
        print(w)
    if not changes and not warnings:
        print(f"up to date: {len(nodes)} nodes")
    return 1 if args.check and (changes or any(w.startswith(("SKIPPED", "ORPHAN")) for w in warnings)) else 0


if __name__ == "__main__":
    sys.exit(main())
