"""Read frozen artifacts, validate lineage, and isolate development before analysis."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.common.loaders import sha256_file, sha256_file_lf
from src.features.contract import PREDICTOR_ALLOWLIST, CONTRACT_VERSION, FEATURE_VERSION, SPLIT_VERSION

ROOT = Path(__file__).resolve().parents[2]
TARGETS = {"regression": "lead_days", "classification": "is_detractor"}


def load_development(root: Path = ROOT):
    ml = root / "data/business/ml"
    schema = json.loads((ml / "feature_schema.json").read_text())
    manifest = json.loads((ml / "dataset_manifest.json").read_text())
    split_report = json.loads((ml / "split_report.json").read_text())
    if schema["predictor_allowlist"] != PREDICTOR_ALLOWLIST:
        raise ValueError("Predictor schema differs from frozen allowlist")
    if (schema["version"], schema["contract_version"], split_report["split_version"]) != (
            FEATURE_VERSION, CONTRACT_VERSION, SPLIT_VERSION):
        raise ValueError("Unsupported feature/contract/split version")
    if sha256_file(ml / "orders_ml_features.csv") != manifest["content_checksum"]:
        raise ValueError("Base dataset hash mismatch")
    for filename, digest in manifest["input_hashes"].items():
        if sha256_file_lf(root / "data/preprocessed" / filename) != digest:
            raise ValueError(f"Source hash mismatch: {filename}")
    base = pd.read_csv(ml / "orders_ml_features.csv", dtype={
        "order_id": "string", "customer_id": "string", "customer_unique_id": "string"})
    splits = pd.read_csv(ml / "split_assignments.csv", dtype="string")
    cv = pd.read_csv(ml / "cv_assignments.csv", dtype={"order_id": "string"})
    for name, frame in [("base", base), ("splits", splits)]:
        if frame.order_id.isna().any() or frame.order_id.duplicated().any():
            raise ValueError(f"{name}: missing/duplicate order key")
    if set(base.order_id) != set(splits.order_id):
        raise ValueError("Outer manifest does not cover exactly the base orders")
    if not set(splits.split_assignment).issubset({"development", "holdout", "excluded"}):
        raise ValueError("Invalid outer assignment")
    if set(cv.task) != set(TARGETS) or cv.duplicated(["order_id", "task"]).any():
        raise ValueError("Invalid task fold keys")
    if set(cv.split_version) != {SPLIT_VERSION} or set(splits.split_version) != {SPLIT_VERSION}:
        raise ValueError("Manifest version mismatch")
    merged = base.merge(splits[["order_id", "customer_unique_id", "split_assignment"]],
                        on="order_id", validate="one_to_one", suffixes=("", "_manifest"))
    if not merged.customer_unique_id.fillna("").equals(merged.customer_unique_id_manifest.fillna("")):
        raise ValueError("Manifest group differs from base")
    if splits.groupby("customer_unique_id").split_assignment.nunique().gt(1).any():
        raise ValueError("Customer spans outer partitions")
    development = merged.loc[merged.split_assignment.eq("development")].copy()
    if not set(cv.order_id).issubset(set(development.order_id)):
        raise ValueError("CV contains non-development orders")
    for task in TARGETS:
        eligible = development.loc[development[f"eligible_{task}"].eq(1)]
        folds = cv.loc[cv.task.eq(task)]
        if set(eligible.order_id) != set(folds.order_id):
            raise ValueError(f"{task}: folds do not exactly cover eligible development")
        aligned = eligible.merge(folds[["order_id", "validation_fold"]], on="order_id", validate="one_to_one")
        if set(aligned.validation_fold) != set(range(5)):
            raise ValueError("Expected saved folds 0..4")
        if aligned.groupby("customer_unique_id").validation_fold.nunique().gt(1).any():
            raise ValueError("Customer spans validation folds")
        if aligned[TARGETS[task]].isna().any():
            raise ValueError("Eligible target missing")
        if task == "regression" and not aligned.lead_days.gt(0).all():
            raise ValueError("Regression duration invalid")
        if task == "classification":
            for _, group in aligned.groupby("validation_fold"):
                if set(group.is_detractor) != {0, 1}:
                    raise ValueError("Classification fold lacks both classes")
    hashes = {p.name: sha256_file(p) for p in ml.iterdir() if p.is_file() and p.suffix in {".csv", ".json"}}
    # The full base is deliberately not returned. Only development outcomes can
    # reach downstream audit/training code; full-file reading is integrity-only.
    return development.sort_values("order_id").reset_index(drop=True), cv, hashes


def task_rows(development, cv, task):
    if task not in TARGETS:
        raise ValueError(f"Unknown task: {task}")
    rows = development.loc[development[f"eligible_{task}"].eq(1)].merge(
        cv.loc[cv.task.eq(task), ["order_id", "validation_fold"]], on="order_id", validate="one_to_one")
    return rows.sort_values("order_id").reset_index(drop=True)


def fold_indices(rows):
    for fold in sorted(rows.validation_fold.unique()):
        val = np.flatnonzero(rows.validation_fold.to_numpy() == fold)
        train = np.flatnonzero(rows.validation_fold.to_numpy() != fold)
        if set(rows.iloc[train].customer_unique_id) & set(rows.iloc[val].customer_unique_id):
            raise ValueError("Training/validation customer overlap")
        yield int(fold), train, val
