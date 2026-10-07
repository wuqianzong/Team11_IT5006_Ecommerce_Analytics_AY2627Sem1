"""Explicit, locked reproduction of a previously evaluated frozen holdout.

Never delete or rewrite the original access receipt to permit another evaluation.
This guard binds the accepted selection to that receipt, checks the current
semantic protocol, and records new execution separately before fitting starts.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from src.common.loaders import sha256_file
from .io import clean_json

MODE = "frozen_holdout_reproduction_not_independent_test"
RECEIPT = "stage5_holdout_reproduction.json"
PROTOCOL = Path(__file__).parent / "configs/stage5_frozen_protocol.json"


def canonical_hash(value):
    return hashlib.sha256((json.dumps(clean_json(value), indent=2, sort_keys=True,
                                      allow_nan=False) + "\n").encode()).hexdigest()


def validate_protocol(root, run_id, selection, policy, hashes, protocol_path=PROTOCOL):
    original_path = root / "artifacts/metrics/stage5_holdout_access.json"
    protocol = json.loads(Path(protocol_path).read_text())
    original = json.loads(original_path.read_text())
    if sha256_file(original_path) != protocol["original_receipt_sha256"] or original != protocol["original_receipt"]:
        raise ValueError("Original holdout receipt changed or unrelated to accepted protocol")
    if original["state"] != "evaluated_and_published" or run_id != original["run_id"]:
        raise ValueError("Reproduction must use the original canonical run ID")
    accepted = protocol["accepted_selection"]
    if canonical_hash(accepted) != original["selection_sha256"]:
        raise ValueError("Accepted selection is not bound to the original receipt")
    if canonical_hash(protocol["accepted_policy"]) != accepted["decision_policy_sha256"]:
        raise ValueError("Accepted policy checksum mismatch")
    for key in ["features", "feature_version", "contract_version", "split_version",
                "baseline_config", "selection_rule", "config_sha256", "input_hashes", "positive_class"]:
        if selection[key] != accepted[key]:
            raise ValueError(f"Frozen reproduction protocol changed: {key}")
    if hashes != original["input_hashes"] or hashes != accepted["input_hashes"]:
        raise ValueError("Frozen reproduction inputs changed")
    for task in ["regression", "classification"]:
        if selection["tasks"][task]["candidate"] != accepted["tasks"][task]["candidate"]:
            raise ValueError(f"Frozen candidate changed: {task}")
    if policy != protocol["accepted_policy"] or canonical_hash(policy) != selection["decision_policy_sha256"]:
        raise ValueError("Frozen classification policy changed")
    return protocol


def durable_write(path, record, exclusive=False):
    text = json.dumps(clean_json(record), indent=2, sort_keys=True, allow_nan=False) + "\n"
    if exclusive:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(text); stream.flush(); os.fsync(stream.fileno())
        return
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     prefix=".receipt-", delete=False) as stream:
        stream.write(text); stream.flush(); os.fsync(stream.fileno())
        temporary = Path(stream.name)
    os.replace(temporary, path)


def reserve(root, run_id, selection, policy, hashes, protocol_path=PROTOCOL):
    protocol = validate_protocol(root, run_id, selection, policy, hashes, protocol_path)
    destinations = [root / "artifacts/metrics" / run_id] + [
        root / "artifacts/models" / task / run_id for task in ["regression", "classification"]]
    if any(path.exists() for path in destinations):
        raise FileExistsError("Existing final outputs/bundles cannot be overwritten")
    record = {"evaluation_mode": MODE, "run_id": run_id,
              "state": "reserved_before_reproduction_fits",
              "created_utc": datetime.now(timezone.utc).isoformat(),
              "original_receipt_sha256": protocol["original_receipt_sha256"],
              "original_run_manifest_sha256": protocol["original_receipt"]["run_manifest_sha256"],
              "accepted_selection_sha256": protocol["original_receipt"]["selection_sha256"],
              "selection_sha256": canonical_hash(selection), "input_hashes": hashes,
              "policy_sha256": canonical_hash(policy), "protocol_sha256": sha256_file(protocol_path),
              "independent_test_estimate": False}
    path = root / "artifacts/metrics" / RECEIPT
    durable_write(path, record, exclusive=True)  # One attempt; prevents concurrent/duplicate publication.
    return {"path": path, "record": record}


def update(context, **fields):
    context["record"].update(fields)
    durable_write(context["path"], context["record"])


def evaluation_receipt(root, manifest, run_id):
    mode = manifest.get("evaluation_mode")
    if mode is None:
        return json.loads((root / "artifacts/metrics/stage5_holdout_access.json").read_text())
    if mode != MODE:
        raise ValueError("Unknown final evaluation mode")
    path = root / "artifacts/metrics" / RECEIPT
    receipt = json.loads(path.read_text())
    original_path = root / "artifacts/metrics/stage5_holdout_access.json"
    if receipt.get("evaluation_mode") != MODE or receipt.get("independent_test_estimate") is not False:
        raise ValueError("Reproduction receipt declaration mismatch")
    if sha256_file(original_path) != receipt["original_receipt_sha256"]:
        raise ValueError("Original receipt integrity mismatch")
    if manifest.get("independent_test_estimate") is not False or manifest.get("original_receipt_sha256") != receipt["original_receipt_sha256"]:
        raise ValueError("Final manifest reproduction declaration mismatch")
    source = root / "artifacts/metrics/stage4-selection-v1"
    selection = json.loads((source / "selection_record.json").read_text())
    policy = json.loads((source / "decision_policy.json").read_text())
    validate_protocol(root, run_id, selection, policy, manifest["input_hashes"])
    if receipt["protocol_sha256"] != sha256_file(PROTOCOL) or receipt["selection_sha256"] != manifest["selection_sha256"]:
        raise ValueError("Reproduction receipt protocol/selection lineage mismatch")
    return receipt
