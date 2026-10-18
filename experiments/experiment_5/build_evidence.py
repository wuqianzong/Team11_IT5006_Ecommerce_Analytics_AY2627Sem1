"""Build evidence/build/ from accepted stage outputs (README sections 7 and 13.1).

    python experiments/experiment_5/build_evidence.py           # release build: needs `check` to pass
    python experiments/experiment_5/build_evidence.py --draft   # evidence/build_draft/, for working drafts

evidence/registry.yaml lists every item the report, slides and app use:

    - id: T6.1-reg-training
      kind: table              # table | figure | number
      source: stages/s06_training/regression/outputs/metrics_long.csv
      select: {phase: validation, metric: [mae, rmse, r2]}
      aggregate: mean_sd_by_candidate    # optional, tables only
      value_column: value                # numbers only (default "value")
      used_in: [report 5.1, deck slide 6]
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd
import yaml

E5 = Path(__file__).resolve().parent
sys.path.insert(0, str(E5))

from e5lib import manifest  # noqa: E402
from e5lib.paths import assert_inside_e5  # noqa: E402


def _select(df: pd.DataFrame, select: dict | None) -> pd.DataFrame:
    for col, val in (select or {}).items():
        df = df[df[col].isin(val if isinstance(val, list) else [val])]
    return df


def _aggregate(df: pd.DataFrame, how: str | None) -> pd.DataFrame:
    if not how:
        return df
    if how == "mean_sd_by_candidate":
        g = df.groupby(["candidate_id", "metric"])["value"]
        return g.agg(["mean", "std", "count"]).reset_index()
    raise ValueError(f"unknown aggregate {how!r}")


def build(draft: bool) -> int:
    if not draft:
        rc = subprocess.run([sys.executable, str(E5 / "run_pipeline.py"), "check"]).returncode
        if rc != 0:
            print("refusing to build release evidence: run_pipeline.py check failed (use --draft for drafts)")
            return 1
    registry_path = E5 / "evidence" / "registry.yaml"
    items = yaml.safe_load(registry_path.read_text()) if registry_path.exists() else []
    out = assert_inside_e5(E5 / "evidence" / ("build_draft" if draft else "build"))
    if out.exists():
        shutil.rmtree(out)
    (out / "tables").mkdir(parents=True)
    (out / "figures").mkdir()
    numbers, sources = {}, set()
    for item in items or []:
        src = E5 / item["source"]
        sources.add(src)
        kind = item["kind"]
        if kind == "figure":
            shutil.copy(src, out / "figures" / f"{item['id']}{src.suffix}")
            sidecar = src.with_suffix(".csv")
            if sidecar.exists():
                shutil.copy(sidecar, out / "figures" / f"{item['id']}.csv")
            continue
        df = _select(pd.read_csv(src), item.get("select"))
        if kind == "table":
            df = _aggregate(df, item.get("aggregate"))
            df.to_csv(out / "tables" / f"{item['id']}.csv", index=False)
            try:
                md = df.to_markdown(index=False)
            except ImportError:  # tabulate not installed
                md = df.to_string(index=False)
            (out / "tables" / f"{item['id']}.md").write_text(md)
        elif kind == "number":
            col = item.get("value_column", "value")
            if len(df) != 1:
                raise ValueError(f"{item['id']}: number selection must match exactly one row, got {len(df)}")
            numbers[item["id"]] = float(df[col].iloc[0])
        else:
            raise ValueError(f"{item['id']}: unknown kind {kind!r}")
    (out / "numbers.json").write_text(json.dumps(numbers, indent=2))
    runs = {}
    for src in sources:
        parts = src.relative_to(E5).parts
        if len(parts) > 3 and parts[0] == "stages":
            m = manifest.read(parts[1], parts[2]) or {}
            runs[f"{parts[1]}/{parts[2]}"] = {"run_id": m.get("run_id"), "commit": m.get("commit")}
    (out / "_release.json").write_text(json.dumps({"draft": draft, "nodes": runs}, indent=2))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", action="store_true")
    sys.exit(build(ap.parse_args().draft))
