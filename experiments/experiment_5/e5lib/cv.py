"""The s05 cross-validation folds (README sections 5 and 13.1).

s05_partition writes folds.csv (order_id, fold, role, purchase_ts). Stages from s06 on
use the folds only through this module: customer purge and label maturity are already
applied in that file, and check_fold_rules() asserts them again.
"""
from __future__ import annotations

from typing import Iterator

import numpy as np
import pandas as pd

from . import data

ROLES = ("train", "validation")


def load_folds(task: str, stage: str) -> pd.DataFrame:
    path = data.upstream("s05_partition", task, "folds.csv", stage)
    folds = pd.read_csv(path, parse_dates=["purchase_ts"])
    missing = {"order_id", "fold", "role", "purchase_ts"} - set(folds.columns)
    if missing:
        raise ValueError(f"folds.csv lacks columns {sorted(missing)}")
    bad = set(folds["role"]) - set(ROLES)
    if bad:
        raise ValueError(f"folds.csv has unknown roles {sorted(bad)}")
    return folds


def folds(task: str, stage: str) -> Iterator[tuple[int, np.ndarray, np.ndarray]]:
    """Yield (fold, train_order_ids, validation_order_ids) in fold order."""
    f = load_folds(task, stage)
    for k in sorted(f["fold"].unique()):
        part = f[f["fold"] == k]
        yield int(k), part.loc[part.role == "train", "order_id"].to_numpy(), \
            part.loc[part.role == "validation", "order_id"].to_numpy()


def sklearn_splits(order_ids: pd.Series | np.ndarray, task: str, stage: str) -> list[tuple[np.ndarray, np.ndarray]]:
    """Positional (train_idx, val_idx) pairs for sklearn's cv= argument.

    order_ids must be the order_id column aligned with X. Rows of X not in a fold's
    train or validation set are simply left out of that fold.
    """
    pos = pd.Series(np.arange(len(order_ids)), index=pd.Index(order_ids, name="order_id"))
    if pos.index.has_duplicates:
        raise ValueError("order_id must be unique in X")
    out = []
    for _, train_ids, val_ids in folds(task, stage):
        out.append((pos.reindex(train_ids).dropna().astype(int).to_numpy(),
                    pos.reindex(val_ids).dropna().astype(int).to_numpy()))
    return out


def check_fold_rules(folds_df: pd.DataFrame, records: pd.DataFrame) -> list[dict]:
    """Assert the s05 fold rules; returns one result per fold and rule.

    records needs order_id, customer_unique_id and purchase_ts. Rules: training strictly
    before validation (anti-temporal leakage) and no customer on both sides (purge).
    """
    merged = folds_df.merge(records[["order_id", "customer_unique_id"]], on="order_id", how="left")
    if merged["customer_unique_id"].isna().any():
        raise ValueError("folds.csv has order_ids that are not in the records")
    results = []
    for k, part in merged.groupby("fold"):
        tr, va = part[part.role == "train"], part[part.role == "validation"]
        results.append({"fold": int(k), "rule": "train_before_validation",
                        "passed": bool(tr["purchase_ts"].max() < va["purchase_ts"].min())})
        shared = set(tr["customer_unique_id"]) & set(va["customer_unique_id"])
        results.append({"fold": int(k), "rule": "no_shared_customer",
                        "passed": not shared, "detail": f"{len(shared)} shared customers"})
    return results
