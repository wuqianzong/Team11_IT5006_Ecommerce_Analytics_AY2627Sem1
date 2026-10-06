"""Stage 4 executable identity, explicit baseline recovery and compact inspection.

Full build: python -m src.models.stage4 --rebuild-baseline
Publish compact inventory: python -m src.models.stage4_checkpoint --publish
Inspect compact evidence: python -m src.models.stage4_checkpoint
No compact inspection claims to reverify omitted predictions or fitted models.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

from src.common.loaders import sha256_file
from .data import ROOT, load_development
from .io import identity, write_json
from .verify_checkpoint import INVENTORY, MAX_FILE_BYTES, checked_path


def stage4_identity(root):
    result = identity(root)
    paths = [root / "src/models" / f"{name}.py" for name in
             ["stage4", "tuned_pipelines", "policy", "verify_stage4", "stage4_checkpoint"]]
    paths += [root / "src/models/configs/stage4_search.json",
              root / "src/models/tests/test_stage4.py",
              root / "src/models/tests/test_stage4_checkpoint.py"]
    hashes = {**result["implementation_and_document_hashes"],
              **{str(p.relative_to(root)): sha256_file(p) for p in paths}}
    result.update(scope="stage4_selection_executable_dependencies",
                  implementation_and_document_hashes=hashes,
                  code_identity_sha256=hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest())
    return result


def compare_baseline_tables(preserved, rebuilt):
    for name in ["fold_metrics.csv", "cv_summary.csv", "pooled_oof_metrics.csv"]:
        left = pd.read_csv(preserved / name, float_precision="round_trip")
        right = pd.read_csv(rebuilt / name, float_precision="round_trip")
        columns = [c for c in left if "seconds" not in c]
        pd.testing.assert_frame_equal(left[columns], right[columns], check_dtype=False,
                                      atol=1e-9, rtol=1e-9)


def ensure_baseline(path, root=ROOT, rebuild=False):
    """Do not overwrite an existing run or silently train from an inspection call."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError("Build Stage 3 first with python -m src.models.train")
    manifest = json.loads((path / "run_manifest.json").read_text())
    missing = [name for name in manifest["output_hashes"] if not checked_path(path, name).is_file()]
    if not missing:
        for name, digest in manifest["output_hashes"].items():
            if sha256_file(checked_path(path, name)) != digest:
                raise ValueError(f"Existing baseline artifact altered: {name}")
        return {"rebuilt": False}
    if not rebuild:
        raise FileNotFoundError("Compact Stage 3 evidence lacks intermediates. Explicitly use --rebuild-baseline; existing evidence will be preserved under archive/.")
    from .verify_checkpoint import verify_checkpoint
    from .train import run
    from .verify import verify
    verify_checkpoint(path, root)  # Reject damaged compact evidence before moving anything.
    archive = root / "archive"
    archive.mkdir(exist_ok=True)
    preserved = Path(tempfile.mkdtemp(prefix="stage3-before-rebuild-", dir=archive)) / path.name
    shutil.move(str(path), str(preserved))
    # On failure, both the preserved evidence and any newly published run remain
    # available for diagnosis. Nothing is deleted to conceal a failed comparison.
    rebuilt = run(root=root, run_id=path.name, config_path=preserved / "configuration.json")
    verify(rebuilt, root)
    compare_baseline_tables(preserved, rebuilt)
    return {"rebuilt": True, "preserved": str(preserved), "baseline_metric_parity": "passed"}


def check_files(path, inventory):
    if inventory.get("stage") != 4 or inventory.get("holdout_evaluated") is not False:
        raise ValueError("Wrong Stage 4 checkpoint/holdout flag")
    published = inventory.get("published_files", {})
    if not {"run_manifest.json", "selection_record.json", "decision_policy.json"} <= set(published):
        raise ValueError("Missing Stage 4 publication evidence")
    if INVENTORY in published or set(published) & set(inventory.get("omitted_files", {})):
        raise ValueError("Invalid publication inventory overlap")
    for name, digest in published.items():
        file = checked_path(path, name)
        if not file.is_file() or sha256_file(file) != digest:
            raise ValueError(f"Published output missing or altered: {name}")


def verify_checkpoint(path, root=ROOT):
    from .stage4 import summarize, choose_candidate, paired_differences
    from .verify_stage4 import read_csv
    path = Path(path)
    inventory = json.loads((path / INVENTORY).read_text())
    check_files(path, inventory)
    manifest = json.loads((path / "run_manifest.json").read_text())
    config = json.loads((path / "configuration.json").read_text())
    selection = json.loads((path / "selection_record.json").read_text())
    policy = json.loads((path / "decision_policy.json").read_text())
    _, _, hashes = load_development(root)
    if manifest["stage"] != 4 or manifest["holdout_evaluated"] is not False or selection["holdout_evaluated"] is not False:
        raise ValueError("Invalid Stage 4 boundary")
    if manifest["input_hashes"] != hashes or selection["input_hashes"] != hashes:
        raise ValueError("Frozen inputs changed")
    if sha256_file(path / "selection_record.json") != manifest["selection_record_sha256"]:
        raise ValueError("Selection identity mismatch")
    if sha256_file(path / "decision_policy.json") != selection["decision_policy_sha256"]:
        raise ValueError("Policy identity mismatch")
    source = root / "artifacts/metrics" / config["stage3_run_id"]
    if sha256_file(source / "run_manifest.json") != manifest["source_stage3_manifest_sha256"]:
        raise ValueError("Baseline lineage changed")
    folds, summary = read_csv(path / "fold_metrics.csv"), read_csv(path / "cv_summary.csv")
    pd.testing.assert_frame_equal(summarize(folds), summary, check_dtype=False, atol=1e-9, rtol=1e-9)
    pd.testing.assert_frame_equal(paired_differences(folds, config), read_csv(path / "paired_fold_differences.csv"),
                                  check_dtype=False, atol=1e-9, rtol=1e-9)
    for task in ["regression", "classification"]:
        if choose_candidate(summary, task, config) != selection["tasks"][task]["candidate"]["id"]:
            raise ValueError("Selection rule mismatch")
    scenarios = read_csv(path / "threshold_scenarios.csv")
    chosen = scenarios.loc[scenarios.policy.eq("optimized_development_oof") &
                           scenarios.cost_ratio_fn_to_fp.eq(policy["cost_ratio_fn_to_fp"])]
    if len(chosen) != 1 or chosen.iloc[0].threshold != policy["threshold"]:
        raise ValueError("Published policy/scenario mismatch")
    return {"status": "passed_compact_checkpoint_inspection", "stage": 4,
            "published_files_checked": len(inventory["published_files"]),
            "omitted_files_not_checked": len(inventory["omitted_files"]),
            "holdout_evaluated": False, "model_fitting": False}


def publish_inventory(path, root=ROOT):
    from .verify_stage4 import verify
    if (path / INVENTORY).exists():
        raise FileExistsError("Publication inventory already exists")
    result = verify(path, root)
    published, omitted = {}, {}
    for file in sorted(path.rglob("*")):
        if not file.is_file():
            continue
        name = str(file.relative_to(path))
        reason = ("intermediate fold model" if name.startswith("cv_models/") else
                  "full intermediate prediction dump" if name.endswith("oof_predictions.csv") or
                  name == "selected_classification_policy_predictions.csv" else
                  "large intermediate table" if file.stat().st_size > MAX_FILE_BYTES else None)
        if reason:
            omitted[name] = {"sha256": sha256_file(file), "bytes": file.stat().st_size,
                             "reason": reason, "rebuild": "src.models.stage4"}
        else:
            published[name] = sha256_file(file)
    write_json({"stage": 4, "schema_version": 1, "holdout_evaluated": False,
                "published_files": published, "omitted_files": omitted,
                "full_local_verification_at_publication": result,
                "inspection_scope": "Published hashes, input/baseline lineage, fold summaries, paired differences and selection/policy consistency. Omitted predictions/models are not reverified.",
                "full_build": "Preserve existing Stage 4 run outside active artifacts, then python -m src.models.stage4 --rebuild-baseline; never overwrite an existing run.",
                "full_verification": "python -m src.models.verify_stage4"}, path / INVENTORY)
    return verify_checkpoint(path, root)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    path = ROOT / "artifacts/metrics/stage4-selection-v1"
    print(json.dumps(publish_inventory(path) if args.publish else verify_checkpoint(path), indent=2))
