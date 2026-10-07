"""Publish/inspect complete final bundles and compact development diagnostics.

The final verifier checks final predictions/models fully. Compact diagnostic
inspection does not claim to recheck omitted curve coordinates or fold models.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.common.loaders import sha256_file
from .data import ROOT, load_development
from .io import write_json
from .reproduction import RECEIPT, evaluation_receipt
from .verify_checkpoint import checked_path, MAX_FILE_BYTES

INVENTORY = "publication_inventory.json"


def check_published(root, inventory):
    if inventory.get("stage") != 5 or inventory.get("evaluation_mode") != "frozen_holdout_reproduction_not_independent_test":
        raise ValueError("Wrong Stage 5 publication mode")
    published = inventory.get("published_files", {})
    if not published or set(published) & set(inventory.get("omitted_files", {})):
        raise ValueError("Invalid Stage 5 publication inventory")
    if "artifacts/metrics/stage5-final-v1/publication_inventory.json" in published:
        raise ValueError("Inventory cannot hash itself")
    for name, digest in published.items():
        file = checked_path(root, name)
        if not file.is_file() or sha256_file(file) != digest:
            raise ValueError(f"Published output missing or altered: {name}")


def inspect_diagnostics(root):
    path = root / "artifacts/metrics/stage5-tutorial8-v1"
    manifest = json.loads((path / "run_manifest.json").read_text())
    if manifest["holdout_evaluated"] or manifest["fit_count"] != 10:
        raise ValueError("Invalid diagnostic boundary")
    source = root / "artifacts/metrics/stage4-selection-v1"
    if manifest["source_stage4_manifest_sha256"] != sha256_file(source / "run_manifest.json") or manifest["selection_sha256"] != sha256_file(source / "selection_record.json"):
        raise ValueError("Diagnostic lineage mismatch")
    _, _, hashes = load_development(root)
    if manifest["input_hashes"] != hashes:
        raise ValueError("Diagnostic frozen inputs changed")
    learning = pd.read_csv(path / "learning_curve.csv", float_precision="round_trip")
    evidence = json.loads((path / "learning_fit_evidence.json").read_text())
    if len(learning) != 30 or len(evidence) != 15 or sum(r["fit"] for r in evidence) != 10:
        raise ValueError("Diagnostic fit/record coverage")
    if not np.isfinite(learning[["average_precision", "roc_auc"]]).all().all():
        raise ValueError("Invalid diagnostic scores")
    for fold in range(5):
        part = learning.loc[learning.fold.eq(fold)]
        if len(part) != 6 or set(part.fraction_training_groups) != {.25, .5, 1.}:
            raise ValueError("Incomplete learning curve fold")
    return {"status": "passed_compact_diagnostic_inspection", "fits": 10,
            "omitted_curve_coordinates_and_fold_models_reverified": False}


def verify_checkpoint(root=ROOT):
    from .verify_stage5 import verify
    path = root / "artifacts/metrics/stage5-final-v1"
    inventory = json.loads((path / INVENTORY).read_text())
    check_published(root, inventory)
    diagnostic = inspect_diagnostics(root)
    final = verify(path, root)  # All final predictions/bundles are published.
    return {"status": "passed_stage5_checkpoint_verification", "stage": 5,
            "published_files_checked": len(inventory["published_files"]),
            "diagnostics": diagnostic, "final_verification": final,
            "holdout_evaluated": True, "independent_test_estimate": False}


def publish_inventory(root=ROOT):
    from .verify_stage5 import verify
    from .verify_tutorial8 import verify_supplement
    path = root / "artifacts/metrics/stage5-final-v1"
    if (path / INVENTORY).exists():
        raise FileExistsError("Stage 5 publication inventory already exists")
    final = verify(path, root)
    supplement = verify_supplement(root / "artifacts/metrics/stage5-tutorial8-v1", root)
    directories = [root / "artifacts/metrics" / n for n in
                   ["stage5-tutorial8-v1", "stage5-final-v1", "stage5-scoring-demo-v1"]]
    directories += [root / "artifacts/models" / t / "stage5-final-v1" for t in ["regression", "classification"]]
    files = sorted(p for directory in directories for p in directory.rglob("*") if p.is_file())
    files += [root / "artifacts/metrics" / n for n in
              ["stage5_holdout_access.json", RECEIPT, "stage5_tutorial8_internal_verification.json"]]
    published, omitted = {}, {}
    for file in files:
        name = str(file.relative_to(root))
        if name.endswith("stage5-tutorial8-v1/oof_curve_coordinates.csv"):
            omitted[name] = {"sha256": sha256_file(file), "bytes": file.stat().st_size,
                             "reason": "large intermediate development curve coordinates"}
        else:
            published[name] = sha256_file(file)
    write_json({"stage": 5, "schema_version": 1,
                "evaluation_mode": "frozen_holdout_reproduction_not_independent_test",
                "independent_test_estimate": False, "published_files": published,
                "omitted_files": omitted, "full_final_verification": final,
                "full_diagnostic_verification": supplement,
                "inspection_scope": "Final models/predictions verified fully. Compact diagnostic hashes, source lineage, fit counts and curve coverage checked; omitted development curve coordinates/fold models are not reverified."}, path / INVENTORY)
    return verify_checkpoint(root)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    print(json.dumps(publish_inventory() if args.publish else verify_checkpoint(), indent=2))
