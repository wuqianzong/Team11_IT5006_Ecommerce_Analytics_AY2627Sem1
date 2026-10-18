"""Stable, readable candidate IDs (README section 5.3).

The same spec always gives the same candidate_id, so the same ID in two stages means the
identical pipeline.
"""
from __future__ import annotations

import re

TASK_PREFIX = {"regression": "reg", "classification": "clf"}


def _fmt(value) -> str:
    if value is None:
        return "none"
    if isinstance(value, bool):
        return "t" if value else "f"
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def make_id(spec: dict) -> str:
    """e.g. reg.sel.log.ridge.alpha=10 or clf.sel.log.logistic.C=0.1.class_weight=balanced.sigmoid"""
    task = TASK_PREFIX[spec["task"]]
    parts = [task, spec.get("feature_set", "sel"), "log" if spec.get("log_inputs") else "raw", spec["estimator"]]
    parts += [f"{k}={_fmt(v)}" for k, v in sorted((spec.get("params") or {}).items())]
    if spec.get("calibration"):
        parts.append(spec["calibration"])
    cid = ".".join(parts)
    if not re.fullmatch(r"[A-Za-z0-9_.=\-]+", cid):
        raise ValueError(f"candidate_id has unsafe characters: {cid}")
    return cid
