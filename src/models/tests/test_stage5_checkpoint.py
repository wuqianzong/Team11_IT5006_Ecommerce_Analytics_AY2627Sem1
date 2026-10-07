import tempfile
import unittest
from pathlib import Path

from src.common.loaders import sha256_file
from src.models.stage5_checkpoint import check_published


class Stage5CheckpointTests(unittest.TestCase):
    def test_published_hashes_and_declaration(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file = root / "evidence.json"; file.write_text("{}")
            inventory = {"stage": 5, "evaluation_mode": "frozen_holdout_reproduction_not_independent_test",
                         "published_files": {"evidence.json": sha256_file(file)}}
            check_published(root, inventory)
            file.write_text("changed")
            with self.assertRaises(ValueError): check_published(root, inventory)
            inventory["evaluation_mode"] = "first_test"
            with self.assertRaises(ValueError): check_published(root, inventory)

    def test_escape_and_overlap_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inventory = {"stage": 5, "evaluation_mode": "frozen_holdout_reproduction_not_independent_test",
                         "published_files": {"../outside": "x"}}
            with self.assertRaises(ValueError): check_published(root, inventory)
            inventory["omitted_files"] = {"../outside": {}}
            with self.assertRaises(ValueError): check_published(root, inventory)
