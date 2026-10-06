import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.common.loaders import sha256_file
from src.models.stage4_checkpoint import ensure_baseline, check_files, compare_baseline_tables


class Stage4CheckpointTests(unittest.TestCase):
    def test_incomplete_baseline_requires_explicit_rebuild(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "stage3-baseline-v1"
            path.mkdir()
            (path / "run_manifest.json").write_text(json.dumps({"output_hashes": {"oof_predictions.csv": "missing"}}))
            with patch("src.models.train.run", side_effect=AssertionError("No implicit fit")):
                with self.assertRaises(FileNotFoundError):
                    ensure_baseline(path)
            self.assertTrue(path.exists())

    def test_compact_hashes_and_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            names = ["run_manifest.json", "selection_record.json", "decision_policy.json"]
            for name in names:
                (path / name).write_text("{}")
            inventory = {"stage": 4, "holdout_evaluated": False,
                         "published_files": {n: sha256_file(path / n) for n in names}}
            check_files(path, inventory)
            (path / names[0]).write_text("altered")
            with self.assertRaises(ValueError):
                check_files(path, inventory)
            inventory["holdout_evaluated"] = True
            with self.assertRaises(ValueError):
                check_files(path, inventory)

    def test_explicit_recovery_preserves_old_run_and_compares(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "artifacts/metrics/stage3-baseline-v1"
            path.mkdir(parents=True)
            (path / "run_manifest.json").write_text(json.dumps({"output_hashes": {"oof_predictions.csv": "missing"}}))
            (path / "configuration.json").write_text("{}")
            def build(**kwargs):
                self.assertFalse(path.exists())
                self.assertTrue(kwargs["config_path"].is_file())
                path.mkdir()
                return path
            with patch("src.models.verify_checkpoint.verify_checkpoint") as compact, \
                 patch("src.models.train.run", side_effect=build) as train, \
                 patch("src.models.verify.verify") as full, \
                 patch("src.models.stage4_checkpoint.compare_baseline_tables") as compare:
                result = ensure_baseline(path, root, rebuild=True)
            self.assertTrue(result["rebuilt"])
            self.assertTrue(Path(result["preserved"]).joinpath("configuration.json").is_file())
            for call in [compact, train, full, compare]:
                call.assert_called_once()


if __name__ == "__main__":
    unittest.main()
