"""Pipeline B number register for the report and deck (blueprint spec/blueprints/b11_report_deck.md, B11.1).

    python pipeline_b/build_evidence_B.py build              # evidence/build/: numbers_B.json, tables, figures
    python pipeline_b/build_evidence_B.py fill IN.md OUT.md  # replace {{id}} placeholders from numbers_B.json
    python pipeline_b/build_evidence_B.py check FILE...      # every {{id}} in the files resolves

evidence/registry_B.yaml lists every number, table and figure the report and deck use:

    - id: B9.2.reg.mae_diff
      kind: number                 # number | table | figure
      source: b09/regression/outputs/paired_test_differences.csv   # under pipeline_b/stages/
      select: {comparison: B frozen minus A frozen, metric: mae}    # rows of a CSV (one row for a number)
      value: difference            # CSV column, or a dotted key path for JSON
      format: "{:+.3f}"            # Python format for the text
      evidence: B9.2
      used_in: [report 5, deck 6]

A source is accepted only if its stage/task folder holds the run listed Current in EVIDENCE.md and the file's
sha256 equals the one in that run's _manifest.json. Separate from A's build_evidence.py (B11-D3). A's baseline
numbers come from B's T1 and B9 files, which score A. The one exception (B-G-11): a source written
A/<stage>/<task>/outputs/<file> is read from A's frozen tree, read only, and accepted only if the file's sha256
equals the file at tag e5-A-frozen.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
import yaml

B_ROOT = Path(__file__).resolve().parent
STAGES = B_ROOT / "stages"
REGISTRY = B_ROOT / "evidence" / "registry_B.yaml"
BUILD = B_ROOT / "evidence" / "build"
A_STAGES = B_ROOT.parent / "stages"     # Pipeline A's frozen tree (read only)
A_TAG = "e5-A-frozen"
PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z0-9_.\-]+)\s*\}\}")


def current_runs() -> dict[tuple[str, str], str]:
    """(stage, task) -> run_id from the Current table of EVIDENCE.md."""
    table = (B_ROOT / "EVIDENCE.md").read_text(encoding="utf-8").split("## Current runs")[1].split("\n## ")[0]
    rows = re.findall(r"^\| (b\d\d|t1_joint_test|doc_support) \| (\w+) \| (\d{8}T\d{6}Z) \|", table, re.M)
    return {(s, t): r for s, t, r in rows}


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def verify_source(src: str, runs: dict) -> tuple[Path, str]:
    """The file must sit in a Current run's outputs and match its manifest; returns (path, run_id)."""
    parts = Path(src).parts
    if len(parts) < 4 or parts[2] != "outputs":
        raise ValueError(f"{src}: expected <stage>/<task>/outputs/<file>")
    key = (parts[0], parts[1])
    if key not in runs:
        raise ValueError(f"{src}: {key[0]}/{key[1]} has no Current run in EVIDENCE.md")
    out = STAGES / parts[0] / parts[1] / "outputs"
    man = json.loads((out / "_manifest.json").read_text())
    if man["run_id"] != runs[key]:
        raise ValueError(f"{src}: manifest run {man['run_id']} is not the Current run {runs[key]}")
    path = STAGES / src
    rel = path.relative_to(B_ROOT.parents[2]).as_posix()   # manifests key outputs from the repository root
    expected = man["outputs"].get(rel)
    if expected is None or expected != _sha(path):
        raise ValueError(f"{src}: sha256 does not match the Current run's manifest")
    return path, man["run_id"]


def verify_a_source(src: str) -> tuple[Path, str]:
    """A/<stage>/<task>/outputs/<file>: the file must equal its copy at tag e5-A-frozen (B-G-11); returns (path, run_id)."""
    parts = Path(src).parts
    if len(parts) < 5 or parts[0] != "A" or parts[3] != "outputs":
        raise ValueError(f"{src}: expected A/<stage>/<task>/outputs/<file>")
    path = A_STAGES.joinpath(*parts[1:])
    if not path.is_file():
        raise ValueError(f"{src}: no such file in A's tree")
    repo = B_ROOT.parents[2]
    rel = path.relative_to(repo).as_posix()
    tagged = subprocess.run(["git", "show", f"{A_TAG}:{rel}"], cwd=repo, capture_output=True)
    if tagged.returncode != 0:
        raise ValueError(f"{src}: not in tag {A_TAG}")
    if hashlib.sha256(tagged.stdout).hexdigest() != _sha(path):
        raise ValueError(f"{src}: sha256 differs from the file at tag {A_TAG}")
    man = json.loads((path.parents[len(parts) - 5] / "_manifest.json").read_text())
    return path, f"{man['run_id']} @ {A_TAG}"


def _outputs(src: str, path: Path) -> tuple[Path, str]:
    """The outputs folder holding the source and the file's path inside it (key of _evidence_index.json)."""
    head = 4 if Path(src).parts[0] == "A" else 3
    inner = Path(*Path(src).parts[head:])
    return path.parents[len(inner.parts) - 1], inner.as_posix()


def _select(df: pd.DataFrame, sel: dict | None) -> pd.DataFrame:
    for col, val in (sel or {}).items():
        df = df[df[col].isin(val if isinstance(val, list) else [val])]
    return df


def _value(item: dict, path: Path):
    if path.suffix == ".json":
        v = json.loads(path.read_text())
        for k in str(item["value"]).split("."):
            v = v[int(k)] if isinstance(v, list) else v[k]
        return v
    rows = _select(pd.read_csv(path), item.get("select"))
    if len(rows) != 1:
        raise ValueError(f"{item['id']}: selection gives {len(rows)} rows, expected 1")
    v = rows.iloc[0][item["value"]]
    return v.item() if hasattr(v, "item") else v


def _rel(p: Path) -> str:
    """Path stored in numbers_B.json: relative to pipeline_b/ for the default build, absolute elsewhere (tests)."""
    try:
        return p.relative_to(B_ROOT).as_posix()
    except ValueError:
        return p.as_posix()


def build(out_dir: Path = BUILD) -> dict:
    """Build the register into out_dir (default evidence/build/; tests pass a temporary folder)."""
    out_dir = Path(out_dir)
    items = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    ids = [i["id"] for i in items]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        raise SystemExit(f"duplicate registry ids: {dup}")
    runs = current_runs()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    (out_dir / "tables").mkdir(parents=True)
    (out_dir / "figures").mkdir(parents=True)
    numbers, errors = {}, []
    for it in items:
        try:
            if Path(it["source"]).parts[0] == "A":
                path, run_id = verify_a_source(it["source"])
            else:
                path, run_id = verify_source(it["source"], runs)
            outs, inner = _outputs(it["source"], path)
            idx = json.loads((outs / "_evidence_index.json").read_text())
            tagged = idx["files"].get(inner, {}).get("ids", [])
            if it["evidence"] not in tagged:
                raise ValueError(f"evidence {it['evidence']} is not tagged on {it['source']} (tagged: {tagged})")
            entry = {"kind": it["kind"], "source": it["source"], "run_id": run_id, "evidence": it["evidence"],
                     "used_in": it.get("used_in", [])}
            if it["kind"] == "number":
                v = _value(it, path)
                entry.update(value=v, text=it.get("format", "{}").format(v))
            elif it["kind"] == "table":
                df = _select(pd.read_csv(path), it.get("select"))
                df = df[it["columns"]] if it.get("columns") else df
                out = out_dir / "tables" / f"{it['id']}.csv"
                df.to_csv(out, index=False, lineterminator="\n")
                entry.update(file=_rel(out), rows=int(len(df)))
            elif it["kind"] == "figure":
                out = out_dir / "figures" / f"{it['id']}{path.suffix}"
                shutil.copyfile(path, out)
                entry.update(file=_rel(out), caption=it.get("caption", ""))
            else:
                raise ValueError(f"unknown kind {it['kind']}")
            numbers[it["id"]] = entry
        except Exception as e:   # collect every problem, then fail once
            errors.append(f"{it.get('id')}: {e}")
    if errors:
        raise SystemExit("registry build failed:\n  " + "\n  ".join(errors))
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=B_ROOT, capture_output=True, text=True).stdout.strip()
    (out_dir / "numbers_B.json").write_text(json.dumps(numbers, indent=2, default=str), encoding="utf-8", newline="\n")
    (out_dir / "build_manifest.json").write_text(json.dumps(
        {"commit": commit, "registry_sha256": _sha(REGISTRY), "items": len(numbers),
         "current_runs": {f"{s}/{t}": r for (s, t), r in sorted(runs.items())}}, indent=2), encoding="utf-8", newline="\n")
    return numbers


def _numbers() -> dict:
    return json.loads((BUILD / "numbers_B.json").read_text(encoding="utf-8"))


TABLE = re.compile(r"\{\{\s*table:([A-Za-z0-9_.\-]+)\s*\}\}")


def missing(text: str, numbers: dict) -> list[str]:
    bad = {m for m in PLACEHOLDER.findall(text) if m not in numbers or numbers[m]["kind"] != "number"}
    bad |= {f"table:{m}" for m in TABLE.findall(text) if m not in numbers or numbers[m]["kind"] != "table"}
    return sorted(bad)


def _cell(v) -> str:
    if isinstance(v, float):
        if v != v:
            return ""
        return f"{v:,.0f}" if v.is_integer() and abs(v) >= 1 else f"{v:.4g}"
    return str(v).replace("|", "\\|")


def markdown_table(entry: dict) -> str:
    """A registry table as a Markdown table, values as stored (floats to 4 significant digits)."""
    df = pd.read_csv(B_ROOT / entry["file"])
    rows = ["| " + " | ".join(map(str, df.columns)) + " |", "| " + " | ".join("---" for _ in df.columns) + " |"]
    rows += ["| " + " | ".join(_cell(v) for v in r) + " |" for r in df.itertuples(index=False)]
    return "\n".join(rows)


def fill(text: str, numbers: dict) -> str:
    bad = missing(text, numbers)
    if bad:
        raise SystemExit(f"unresolved placeholders: {bad}")
    text = TABLE.sub(lambda m: markdown_table(numbers[m.group(1)]), text)
    return PLACEHOLDER.sub(lambda m: numbers[m.group(1)]["text"], text)


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    f = sub.add_parser("fill")
    f.add_argument("src")
    f.add_argument("dst")
    c = sub.add_parser("check")
    c.add_argument("files", nargs="+")
    a = ap.parse_args()
    if a.cmd == "build":
        print(f"built {len(build())} items into {BUILD.relative_to(B_ROOT)}")
    elif a.cmd == "fill":
        Path(a.dst).write_text(fill(Path(a.src).read_text(encoding="utf-8"), _numbers()), encoding="utf-8", newline="\n")
    else:
        nums, bad = _numbers(), {}
        for p in a.files:
            m = missing(Path(p).read_text(encoding="utf-8"), nums)
            if m:
                bad[p] = m
        if bad:
            raise SystemExit(f"unresolved placeholders: {bad}")
        print("all placeholders resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
