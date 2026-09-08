"""Shared, deterministic loaders for the raw and staging layers.

These functions are pure: given the same raw file they return the same typed
table, with no timestamps, randomness, or hidden state. That purity is what
makes the staging layer reproducible (docs/data_architecture.md §4.2).
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

from src.common import schemas


def sha256_file(path: Path) -> str:
    """Streaming SHA-256 of a file's bytes (memory-safe for large files)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def count_rows(path: Path) -> int:
    """Row count (excluding header) using a real CSV parser, so quoted
    newlines inside fields (e.g. review comments) are handled correctly."""
    return int(pd.read_csv(path, usecols=[0]).shape[0])


def load_typed_table(name: str, raw_dir: Path) -> pd.DataFrame:
    """Load one raw CSV and apply its staging contract.

    Types dates, assigns dtypes, and reorders columns to the canonical order
    defined in ``schemas.SCHEMAS``. Performs no joins, aggregations, or derived
    columns — the staging layer stays source-aligned (docs/data_architecture.md
    §4.2).
    """
    spec = schemas.SCHEMAS[name]
    raw = pd.read_csv(raw_dir / spec["raw_file"])

    expected = list(spec["dtypes"].keys())
    missing = [c for c in expected if c not in raw.columns]
    if missing:
        raise ValueError(f"{name}: raw file missing columns {missing}")

    for col, dt in spec["dtypes"].items():
        if dt == "datetime":
            raw[col] = pd.to_datetime(raw[col], errors="coerce")
        elif dt == "string":
            raw[col] = raw[col].astype("string")
        elif dt == "int64":
            raw[col] = raw[col].astype("int64")
        elif dt == "float64":
            raw[col] = raw[col].astype("float64")
        elif dt == "category":
            raw[col] = raw[col].astype("category")
        else:
            raise ValueError(f"{name}.{col}: unknown dtype marker {dt!r}")

    return raw[expected]
