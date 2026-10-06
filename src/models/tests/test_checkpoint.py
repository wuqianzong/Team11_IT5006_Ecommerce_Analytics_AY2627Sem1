import tempfile
import unittest
from pathlib import Path

from src.common.loaders import sha256_file
from src.models.verify_checkpoint import check_published_files, checked_path


class CompactCheckpointTests(unittest.TestCase):
    def test_missing_and_changed_published_file(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "run_manifest.json"
            manifest.write_text("{}\n")
            inventory = {"stage": 3, "holdout_evaluated": False,
                         "published_files": {manifest.name: sha256_file(manifest)},
                         "omitted_files": {"cv_models/omitted.joblib": {"reason": "fixture"}}}
            check_published_files(root, inventory)
            manifest.write_text("changed")
            with self.assertRaises(ValueError):
                check_published_files(root, inventory)
            manifest.unlink()
            with self.assertRaises(ValueError):
                check_published_files(root, inventory)

    def test_path_escape_and_symlink_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ["../outside", "/outside"]:
                with self.assertRaises(ValueError):
                    checked_path(root, name)
            (root / "escape").symlink_to(root.parent, target_is_directory=True)
            with self.assertRaises(ValueError):
                checked_path(root, "escape/file")

    def test_reject_wrong_stage_and_holdout_flag(self):
        with tempfile.TemporaryDirectory() as directory:
            for stage, flag in [(4, False), (3, True)]:
                with self.assertRaises(ValueError):
                    check_published_files(Path(directory), {"stage": stage, "holdout_evaluated": flag})


if __name__ == "__main__":
    unittest.main()
