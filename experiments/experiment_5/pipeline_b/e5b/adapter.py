"""Run A's stage code unchanged on B's inputs (B6–B7 blueprint, method 1).

A's training.run() and tuning.run() read their inputs only through data.upstream, data.load,
cv.folds and outputs.Writer. run_a_stage() swaps exactly these four for the duration of one call
and restores the originals afterwards, even on error; no line of A's orchestration is copied.
"""
from __future__ import annotations

import contextlib
import json
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

from e5lib import cv, data, outputs

from .env import BWriter, assert_inside_e5, b_outputs_dir

REDIRECT = ("upstream", "load", "folds", "Writer")


def _bid(ids) -> list[str]:
    ids = [ids] if isinstance(ids, str) else list(ids)
    return [i if str(i).startswith("B") else f"B{i}" for i in map(str, ids)]


class AdapterWriter(BWriter):
    """B's writer as seen by A's code: A's evidence IDs get a 'B' prefix (6.2 -> B6.2)."""

    reads_from: list[Path] = []

    def __init__(self, stage: str, task: str, out_dir: Path | None = None):
        if out_dir is None:
            super().__init__(stage, task)
            return
        # equivalence test: write into out_dir and never touch pipeline_b/stages
        import shutil
        self.stage, self.task = stage, task
        self.dir = assert_inside_e5(out_dir)
        if self.dir.exists():
            shutil.rmtree(self.dir)
        self.dir.mkdir(parents=True)
        self.index = {"node": f"B/{stage}/{task}", "pipeline": "B", "files": {}, "checks": [],
                      "deviations": {}, "cards": {}}
        self._decisions = []
        self.reads = []

    def _tag(self, relpath, ids, kind):
        super()._tag(relpath, _bid(ids), kind)

    def check(self, name, passed, ids, detail=""):
        return super().check(name, passed, _bid(ids), detail)

    def explain(self, sid, **kw):
        super().explain(_bid(sid)[0], **kw)

    def deviation(self, sid, text):
        super().deviation(_bid(sid)[0], text)

    def decision(self, question, rule, candidates, chosen, files, ids, notes=""):
        super().decision(question, rule, candidates, chosen, files, _bid(ids), notes)

    def finish(self, seed=None, extra=None):
        self.reads.extend(AdapterWriter.reads_from)
        return super().finish(seed=seed, extra=extra)


@contextlib.contextmanager
def redirected(upstream: Callable, load: Callable, folds: Callable, writer: Callable):
    saved = (data.upstream, data.load, cv.folds, outputs.Writer)
    data.upstream, data.load, cv.folds, outputs.Writer = upstream, load, folds, writer
    try:
        yield
    finally:
        data.upstream, data.load, cv.folds, outputs.Writer = saved


def originals_restored() -> bool:
    import importlib
    fresh = {n: getattr(importlib.import_module(m), n) for m, n in
             (("e5lib.data", "upstream"), ("e5lib.data", "load"), ("e5lib.cv", "folds"), ("e5lib.outputs", "Writer"))}
    return fresh["upstream"].__module__ == "e5lib.data" and fresh["load"].__module__ == "e5lib.data" \
        and fresh["folds"].__module__ == "e5lib.cv" and fresh["Writer"].__module__ == "e5lib.outputs"


def b_inputs(task: str, b_stage: str, out_dir: Path | None = None):
    """The four functions for a B run: B4 recipes, B2 rows in B5 folds, B5 folds, B's writer."""
    AdapterWriter.reads_from = []

    def rec(p: Path) -> Path:
        AdapterWriter.reads_from.append(Path(p))
        return Path(p)

    files = {("s04_features", "recipes.json"): b_outputs_dir("b04", task) / "recipes_B.json",
             ("s04_features", "selected_features.json"): b_outputs_dir("b04", task) / "selected_features_B.json"}

    def upstream(source_stage, source_task, filename, stage):
        if source_stage == "s06_training":
            return rec(b_outputs_dir("b06", task) / filename)
        if (source_stage, filename) not in files:
            raise KeyError(f"B adapter has no mapping for {source_stage}/{filename}")
        return rec(files[(source_stage, filename)])

    folds_b = pd.read_csv(rec(b_outputs_dir("b05", task) / "folds_B.csv"), parse_dates=["purchase_ts"])

    def load(name, task_, population, stage):
        if (name, task_, population) != ("records", task, "development"):
            raise KeyError(f"B adapter serves only development records of {task}, not {name}/{task_}/{population}")
        df = pd.read_csv(rec(b_outputs_dir("b02", task) / "records_B.csv.gz"), parse_dates=["purchase_ts"], low_memory=False)
        return df[df.order_id.isin(folds_b.order_id)].reset_index(drop=True)

    def folds(task_, stage):
        for k in sorted(folds_b.fold.unique()):
            part = folds_b[folds_b.fold == k]
            yield int(k), part.loc[part.role == "train", "order_id"].to_numpy(), \
                part.loc[part.role == "validation", "order_id"].to_numpy()

    def writer(stage, task_, clean=True):
        return AdapterWriter(b_stage, task_, out_dir)

    return upstream, load, folds, writer


def a_inputs(task: str, b_stage: str, out_dir: Path, s06_dir: Path | None = None):
    """Equivalence test: A's own inputs, B's writer into out_dir (s06 outputs from s06_dir)."""
    AdapterWriter.reads_from = []
    up, ld, fo = data.upstream, data.load, cv.folds

    def upstream(source_stage, source_task, filename, stage):
        if source_stage == "s06_training" and s06_dir is not None:
            return s06_dir / filename
        return up(source_stage, source_task, filename, stage)

    def writer(stage, task_, clean=True):
        return AdapterWriter(b_stage, task_, out_dir)

    return upstream, ld, fo, writer


def run_a_stage(module, task: str, fns) -> None:
    with redirected(*fns):
        module.run(task)
