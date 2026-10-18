"""Standard output writers (README sections 5.5, 13.1 and design rule 8).

Writer(stage, task) is the only way a stage writes outputs. Every call takes ids=(...),
the solution IDs the output serves; the review pack uses those tags to build the coverage
table and the evidence cards. explain() records the card text (expectation, observation,
reasoning, conclusion) for an ID; pass computed values in, never typed numbers.

A run starts from an empty outputs/ folder (earlier runs stay in git history), and ends
with Writer.finish(seed), which writes the evidence index and the run manifest.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Iterable, Sequence

import pandas as pd

from . import data, manifest
from .paths import assert_inside_e5, outputs_dir

INDEX = "_evidence_index.json"
CLAIM_LABELS = ("observation", "literature-supported hypothesis", "unmeasured mechanism")
REQUIRED = {
    "metrics_long": ["node", "task", "population", "phase", "fold", "candidate_id", "metric", "value", "n_rows", "n_pos"],
    "predictions": ["order_id", "task", "population", "fold", "candidate_id", "y_true", "y_pred"],
    "candidates": ["candidate_id", "description", "kept", "reason"],
}


def _ids(ids: Sequence[str] | str) -> list[str]:
    ids = [ids] if isinstance(ids, str) else list(ids)
    if not ids:
        raise ValueError("every output needs at least one solution ID (ids=...)")
    return [str(i) for i in ids]


class Writer:
    def __init__(self, stage: str, task: str, clean: bool = True):
        self.stage, self.task = stage, task
        self.dir = assert_inside_e5(outputs_dir(stage, task))
        if clean and self.dir.exists():
            shutil.rmtree(self.dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.index: dict[str, Any] = {"node": f"{stage}/{task}", "files": {}, "checks": [],
                                      "deviations": {}, "cards": {}}
        self._decisions: list[dict] = []

    # ---- helpers -------------------------------------------------------------------
    def _path(self, relpath: str) -> Path:
        p = assert_inside_e5(self.dir / relpath)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def _tag(self, relpath: str, ids: Iterable[str], kind: str) -> None:
        entry = self.index["files"].setdefault(relpath, {"ids": [], "kind": kind})
        entry["ids"] = sorted(set(entry["ids"]) | set(ids), key=lambda s: [int(x) for x in s.split(".")])

    @staticmethod
    def _require(df: pd.DataFrame, kind: str) -> None:
        missing = [c for c in REQUIRED[kind] if c not in df.columns]
        if missing:
            raise ValueError(f"{kind} lacks required columns {missing} (README section 5.5)")

    # ---- standard shapes -----------------------------------------------------------
    def metrics_long(self, df: pd.DataFrame, ids) -> Path:
        df = df.assign(node=df.get("node", f"{self.stage}/{self.task}"), task=df.get("task", self.task))
        self._require(df, "metrics_long")
        return self.table("metrics_long", df[REQUIRED["metrics_long"] + [c for c in df.columns if c not in REQUIRED["metrics_long"]]], ids)

    def predictions(self, df: pd.DataFrame, ids, name: str = "predictions") -> Path:
        self._require(df, "predictions")
        return self.table(name, df, ids, compress=True)

    def candidates(self, df: pd.DataFrame, ids) -> Path:
        self._require(df, "candidates")
        return self.table("candidates", df, ids)

    def table(self, name: str, df: pd.DataFrame, ids, compress: bool = False) -> Path:
        rel = f"{name}.csv.gz" if compress else f"{name}.csv"
        df.to_csv(self._path(rel), index=False)
        self._tag(rel, _ids(ids), "table")
        return self.dir / rel

    def curve(self, name: str, df: pd.DataFrame, ids) -> Path:
        rel = f"curves/{name}.csv"
        df.to_csv(self._path(rel), index=False)
        self._tag(rel, _ids(ids), "curve")
        return self.dir / rel

    def figure(self, name: str, fig, data: pd.DataFrame, ids, title: str | None = None) -> Path:
        """PNG plus its sidecar data (design rule 8); fig is a matplotlib Figure."""
        png, side, meta = f"figures/{name}.png", f"figures/{name}.csv", f"figures/{name}.json"
        fig.savefig(self._path(png), dpi=150, bbox_inches="tight")
        data.to_csv(self._path(side), index=False)
        self._path(meta).write_text(json.dumps({"title": title or name, "ids": _ids(ids), "data": side}, indent=2))
        for rel, kind in ((png, "figure"), (side, "figure_data"), (meta, "figure_meta")):
            self._tag(rel, _ids(ids), kind)
        return self.dir / png

    def json(self, name: str, obj: Any, ids) -> Path:
        rel = f"{name}.json"
        self._path(rel).write_text(json.dumps(obj, indent=2, default=str))
        self._tag(rel, _ids(ids), "json")
        return self.dir / rel

    def text(self, name: str, content: str, ids) -> Path:
        self._path(name).write_text(content)
        self._tag(name, _ids(ids), "text")
        return self.dir / name

    def decision(self, question: str, rule: Any, candidates: Any, chosen: Any, files: Sequence[str], ids,
                 notes: str = "") -> None:
        self._decisions.append({"question": question, "rule": rule, "candidates_compared": candidates,
                                "chosen": chosen, "evidence_files": list(files), "notes": notes,
                                "ids": _ids(ids)})

    # ---- review support ------------------------------------------------------------
    def check(self, name: str, passed: bool, ids, detail: str = "") -> bool:
        self.index["checks"].append({"name": name, "passed": bool(passed), "detail": detail, "ids": _ids(ids)})
        return bool(passed)

    def deviation(self, sid: str, text: str) -> None:
        """Record a difference from the approved solution (shown as DEVIATION in coverage)."""
        self.index["deviations"][str(sid)] = text

    def explain(self, sid: str, *, done: str = "", inputs: str = "", expectation: str = "",
                observation: str = "", reasoning: str = "", conclusion: str = "",
                label: str = "observation") -> None:
        """Evidence-card text for one solution ID (README section 9.1)."""
        if label not in CLAIM_LABELS:
            raise ValueError(f"label must be one of {CLAIM_LABELS}")
        self.index["cards"][str(sid)] = {"done": done, "inputs": inputs, "expectation": expectation,
                                         "observation": observation, "reasoning": reasoning,
                                         "conclusion": conclusion, "label": label}

    # ---- end of run ----------------------------------------------------------------
    def finish(self, seed: int | None = None, extra: dict | None = None) -> Path:
        if self._decisions:
            ids = sorted({i for d in self._decisions for i in d["ids"]})
            self.json("decision", self._decisions, ids)
        self.index["checks_failed"] = [c["name"] for c in self.index["checks"] if not c["passed"]]
        self._path(INDEX).write_text(json.dumps(self.index, indent=2))
        return manifest.write(self.stage, self.task, reads=data.reads(), seed=seed, extra=extra)
