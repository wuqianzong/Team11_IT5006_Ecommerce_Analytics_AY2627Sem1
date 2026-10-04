"""LF-deterministic serialization helpers for generated ML artifacts.

feature_contract.md §2 requires UTF-8 with explicit LF line endings for generated
CSVs and hashing the actual canonical LF files (not a pre-Git CRLF
representation). On Windows, Python text mode translates ``\\n`` to ``\\r\\n`` by
default, so every writer here opens files with ``newline=""`` (no translation).
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd


def publish_atomic(staging: Path, target: Path, replace=os.replace) -> None:
    """Publish every staged file into ``target``, rolling back on a handled error.

    Backs up each pre-existing target file in memory before replacing it; if any
    replacement raises, every already-replaced file is restored to its exact prior
    bytes (or removed, when it did not exist before) and the original error is
    re-raised, so the target directory is never left partially updated after a
    handled publication failure (feature_contract.md §11.4).

    This is rollback-on-exception, not crash-atomic: a hard crash between two
    replacements can still leave a mixed old/new set. ``replace`` is injectable
    for tests that want to fail after one or more successful replacements.
    """
    files = sorted(staging.iterdir())
    backups: dict[str, bytes] = {}
    replaced: list[str] = []
    try:
        for f in files:
            dst = target / f.name
            if dst.exists():
                backups[f.name] = dst.read_bytes()
            replace(f, dst)
            replaced.append(f.name)
    except Exception:
        for name in reversed(replaced):
            dst = target / name
            if name in backups:
                dst.write_bytes(backups[name])
            else:
                dst.unlink(missing_ok=True)
        raise


def write_csv_lf(df: pd.DataFrame, path: Path) -> None:
    """Write a CSV with explicit LF line endings and no index column."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        df.to_csv(f, index=False, lineterminator="\n")


def write_text_lf(text: str, path: Path) -> None:
    """Write UTF-8 text with explicit LF line endings."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        f.write(text)
