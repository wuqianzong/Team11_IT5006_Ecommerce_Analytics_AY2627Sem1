"""LF-deterministic serialization helpers for generated ML artifacts.

feature_contract.md §2 requires UTF-8 with explicit LF line endings for generated
CSVs and hashing the actual canonical LF files (not a pre-Git CRLF
representation). On Windows, Python text mode translates ``\\n`` to ``\\r\\n`` by
default, so every writer here opens files with ``newline=""`` (no translation).
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def write_csv_lf(df: pd.DataFrame, path: Path) -> None:
    """Write a CSV with explicit LF line endings and no index column."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        df.to_csv(f, index=False, lineterminator="\n")


def write_text_lf(text: str, path: Path) -> None:
    """Write UTF-8 text with explicit LF line endings."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        f.write(text)
