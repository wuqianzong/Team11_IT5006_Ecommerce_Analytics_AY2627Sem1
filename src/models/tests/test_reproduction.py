"""Synthetic receipt/protocol checks; never fit or read the real holdout."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.common.loaders import sha256_file
from src.models.io import write_json
from src.models.reproduction import canonical_hash, validate_protocol, reserve, update, RECEIPT


class ReproductionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.metrics = self.root / "artifacts/metrics"
        self.metrics.mkdir(parents=True)
        self.policy = {"kind": "fixed_threshold", "positive_class": 1, "comparison": ">=", "threshold": .2}
        self.hashes = {"features": "fixture"}
        self.selection = {"features": ["x"], "feature_version": "v1", "contract_version": "v1",
                          "split_version": "v1", "baseline_config": {"seed": 42},
                          "selection_rule": {"rule": "fixture"}, "config_sha256": "fixture",
                          "input_hashes": self.hashes, "positive_class": 1,
                          "decision_policy_sha256": canonical_hash(self.policy),
                          "tasks": {t: {"candidate": {"family": "forest", "params": {"max_depth": 16}}}
                                    for t in ["regression", "classification"]}}
        self.original = self.metrics / "stage5_holdout_access.json"
        write_json({"run_id": "final", "state": "evaluated_and_published",
                    "selection_sha256": canonical_hash(self.selection), "input_hashes": self.hashes,
                    "run_manifest_sha256": "old-manifest"}, self.original)
        self.original_bytes = self.original.read_bytes()
        self.protocol = self.root / "protocol.json"
        write_json({"original_receipt_sha256": sha256_file(self.original),
                    "original_receipt": json.loads(self.original.read_text()),
                    "accepted_selection": self.selection, "accepted_policy": self.policy}, self.protocol)

    def validate(self, selection=None, policy=None, hashes=None):
        return validate_protocol(self.root, "final", selection or self.selection,
                                 policy or self.policy, hashes or self.hashes, self.protocol)

    def test_timestamp_metadata_may_change_but_protocol_must_match(self):
        current = {**self.selection, "frozen_at_utc": "new actual execution time"}
        self.validate(selection=current)

    def test_changed_candidate_policy_features_or_preprocessing_rejected(self):
        for key in ["features", "baseline_config"]:
            changed = copy.deepcopy(self.selection); changed[key] = "changed"
            with self.assertRaises(ValueError): self.validate(selection=changed)
        changed = copy.deepcopy(self.selection)
        changed["tasks"]["classification"]["candidate"]["params"]["max_depth"] = 12
        with self.assertRaises(ValueError): self.validate(selection=changed)
        with self.assertRaises(ValueError): self.validate(policy={**self.policy, "threshold": .21})

    def test_changed_inputs_original_receipt_or_reference_rejected(self):
        with self.assertRaises(ValueError): self.validate(hashes={"features": "changed"})
        reference = json.loads(self.protocol.read_text())
        reference["accepted_selection"]["features"] = ["other"]
        write_json(reference, self.protocol)
        with self.assertRaises(ValueError): self.validate()
        self.original.write_text("{}")
        with self.assertRaises(ValueError): self.validate()

    def test_missing_original_receipt_and_wrong_run_id_rejected(self):
        with self.assertRaises(ValueError):
            validate_protocol(self.root, "another", self.selection, self.policy, self.hashes, self.protocol)
        self.original.unlink()
        with self.assertRaises(FileNotFoundError): self.validate()

    def test_exclusive_reservation_preserves_original_and_rejects_duplicate(self):
        context = reserve(self.root, "final", self.selection, self.policy, self.hashes, self.protocol)
        self.assertEqual(context["record"]["state"], "reserved_before_reproduction_fits")
        self.assertFalse(context["record"]["independent_test_estimate"])
        with self.assertRaises(FileExistsError):
            reserve(self.root, "final", self.selection, self.policy, self.hashes, self.protocol)
        self.assertEqual(self.original.read_bytes(), self.original_bytes)

    def test_existing_outputs_refused_before_reservation(self):
        (self.metrics / "final").mkdir()
        with self.assertRaises(FileExistsError):
            reserve(self.root, "final", self.selection, self.policy, self.hashes, self.protocol)
        self.assertFalse((self.metrics / RECEIPT).exists())

    def test_failure_record_is_retained_without_changing_original(self):
        from src.models.finalize import run
        def fail(*args, **kwargs):
            kwargs["context"].update(reserve(self.root, "final", self.selection, self.policy, self.hashes, self.protocol))
            raise RuntimeError("synthetic failure before fitting")
        with patch("src.models.finalize._run", side_effect=fail):
            with self.assertRaises(RuntimeError): run("final", root=self.root, replay=True)
        receipt = json.loads((self.metrics / RECEIPT).read_text())
        self.assertEqual(receipt["state"], "failed_during_reproduction")
        self.assertEqual(self.original.read_bytes(), self.original_bytes)


if __name__ == "__main__":
    unittest.main()
