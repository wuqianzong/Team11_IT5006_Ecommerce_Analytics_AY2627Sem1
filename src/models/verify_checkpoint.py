"""Inspect compact Stage 3 evidence without claiming to verify omitted models/OOF.

Publish inventory only after full verification: python -m src.models.verify_checkpoint --publish
Read-only compact inspection: python -m src.models.verify_checkpoint
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.common.loaders import sha256_file
from .data import ROOT, load_development
from .io import write_json

INVENTORY = "publication_inventory.json"
MAX_FILE_BYTES = 5 * 1024 * 1024


def checked_path(path, relative):
    name = Path(relative)
    file = (path / name).resolve()
    if name.is_absolute() or ".." in name.parts or not file.is_relative_to(path.resolve()):
        raise ValueError("Unsafe publication path")
    return file


def check_published_files(path, inventory):
    if inventory.get("stage") != 3 or inventory.get("holdout_evaluated") is not False:
        raise ValueError("Wrong checkpoint or holdout flag")
    if not inventory.get("published_files") or "run_manifest.json" not in inventory["published_files"]:
        raise ValueError("Missing published evidence inventory")
    if INVENTORY in inventory["published_files"]:
        raise ValueError("Inventory cannot hash itself")
    for name, expected in inventory["published_files"].items():
        file = checked_path(path, name)
        if not file.is_file() or sha256_file(file) != expected:
            raise ValueError(f"Published output missing or altered: {name}")
    if set(inventory["published_files"]) & set(inventory.get("omitted_files", {})):
        raise ValueError("Published and omitted inventories overlap")


def publish_inventory(path, root=ROOT):
    from .verify import verify
    if (path / INVENTORY).exists():
        raise FileExistsError("Publication inventory already exists")
    result = verify(path, root)  # Full local models, predictions and tests checked first.
    published, omitted = {}, {}
    for file in sorted(path.rglob("*")):
        if not file.is_file():
            continue
        name = str(file.relative_to(path))
        reason = ("intermediate fold model" if name.startswith("cv_models/") else
                  "full intermediate prediction dump" if name == "oof_predictions.csv" else
                  "large intermediate table" if file.stat().st_size > MAX_FILE_BYTES else None)
        if reason:
            omitted[name] = {"sha256": sha256_file(file), "bytes": file.stat().st_size,
                             "reason": reason, "rebuild": "src.models.train"}
        else:
            published[name] = sha256_file(file)
    write_json({"stage": 3, "schema_version": 1, "holdout_evaluated": False,
                "published_files": published, "omitted_files": omitted,
                "full_local_verification_at_publication": result,
                "inspection_scope": "Published checksums, frozen input identity and consistency of fold metric summaries. Omitted OOF predictions/fold models are not reverified by compact inspection.",
                "full_build": "python -m src.models.train (requires absent canonical run folder)",
                "full_verification": "python -m src.models.verify"}, path / INVENTORY)
    return verify_checkpoint(path, root)


def verify_checkpoint(path, root=ROOT):
    inventory = json.loads((path / INVENTORY).read_text())
    check_published_files(path, inventory)
    manifest = json.loads((path / "run_manifest.json").read_text())
    if manifest["stage"] != 3 or manifest["holdout_evaluated"] is not False:
        raise ValueError("Wrong run manifest")
    _, _, hashes = load_development(root)
    if hashes != manifest["input_hashes"]:
        raise ValueError("Frozen inputs changed")
    folds = pd.read_csv(path / "fold_metrics.csv", float_precision="round_trip")
    summary = pd.read_csv(path / "cv_summary.csv", float_precision="round_trip")
    for row in summary.to_dict("records"):
        values = folds.loc[folds.task.eq(row["task"]) & folds.model.eq(row["model"]) & folds.partition.eq("validation")]
        if len(values) != 5 or set(values.fold) != set(range(5)):
            raise ValueError("Incomplete published fold metrics")
        for metric in ["mae", "rmse", "r2", "average_precision", "roc_auc", "brier", "accuracy"]:
            if metric in values and f"{metric}_mean" in row and pd.notna(row[f"{metric}_mean"]):
                np.testing.assert_allclose(row[f"{metric}_mean"], values[metric].mean(), atol=1e-10, rtol=1e-10)
                np.testing.assert_allclose(row[f"{metric}_std"], values[metric].std(ddof=1), atol=1e-10, rtol=1e-10)
    return {"status": "passed_compact_checkpoint_inspection", "stage": 3,
            "published_files_checked": len(inventory["published_files"]),
            "omitted_files_not_checked": len(inventory["omitted_files"]),
            "holdout_evaluated": False, "model_fitting": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    path = ROOT / "artifacts/metrics/stage3-baseline-v1"
    result = publish_inventory(path) if args.publish else verify_checkpoint(path)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
