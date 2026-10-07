"""Stage 5 fixtures: no real holdout fitting or scoring."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import joblib
import numpy as np
import pandas as pd

from src.common.loaders import sha256_file
from src.features.contract import PREDICTOR_ALLOWLIST, NUMERIC_COLUMNS, CATEGORICAL_COLUMNS
from src.models.data import ROOT
from src.models.finalize import feature_stats, per_class_report, report_metrics, basket_band
from src.models.io import write_json
from src.models.pipelines import make_pipeline
from src.models.policy import apply_threshold
from src.models.score import Scorer, checked_manifest
from src.models.tutorial8 import group_subset


def fixture():
    frame = pd.DataFrame({c: [1., 2., np.nan, 3.] for c in NUMERIC_COLUMNS})
    for c in CATEGORICAL_COLUMNS: frame[c] = ["unknown"] * 4
    for c in ["has_items", "freight_ratio_missing", "payment_missing"]: frame[c] = [1., 0., np.nan, 1.]
    for c in ["weight_missing_fraction", "volume_missing_fraction", "category_missing_fraction", "distance_missing_fraction", "interstate_share"]: frame[c] = [.1, .2, np.nan, .3]
    frame["purchase_month"] = [1, 2, np.nan, 3]
    frame["purchase_dayofweek"] = [1, 2, np.nan, 3]
    frame["purchase_hour"] = [1, 2, np.nan, 3]
    frame["order_id"] = ["a", "b", "c", "d"]
    return frame


class Stage5Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.frame = fixture()
        self.config = json.loads((ROOT / "src/models/configs/stage3_baseline.json").read_text())
        self.schema = json.loads((ROOT / "data/business/ml/feature_schema.json").read_text())

    def bundle(self, task="classification"):
        directory = self.root / task; directory.mkdir()
        pipe = make_pipeline(task, "tree", self.config).fit(self.frame, [0, 1, 0, 1])
        joblib.dump(pipe, directory / "pipeline.joblib")
        write_json(self.schema, directory / "feature_schema.json")
        write_json({}, directory / "feature_stats.json"); write_json({}, directory / "configuration.json")
        write_json({"task": task, "model_version": "fixture", "feature_version": "v1.1", "contract_version": "v1.2", "split_version": "v1.1"}, directory / "metadata.json")
        if task == "classification": write_json({"kind": "fixed_threshold", "positive_class": 1, "threshold": .5, "comparison": ">="}, directory / "decision_policy.json")
        write_json({"output_hashes": {p.name: sha256_file(p) for p in directory.iterdir()}}, directory / "bundle_manifest.json")
        return directory

    def test_nested_group_selection_and_reorder(self):
        rows = pd.DataFrame({"customer_unique_id": ["x", "x", "y", "z", "w"], "order_id": list("abcde")})
        small = rows.iloc[group_subset(rows, .25)]
        medium = rows.iloc[group_subset(rows, .5)]
        self.assertLessEqual(set(small.order_id), set(medium.order_id))
        reversed_rows = rows.iloc[::-1]
        self.assertEqual(set(small.order_id), set(reversed_rows.iloc[group_subset(reversed_rows, .25)].order_id))
        self.assertEqual(set(rows.iloc[group_subset(rows, 1)].order_id), set(rows.order_id))

    def test_invalid_group_sampling(self):
        with self.assertRaises(ValueError): group_subset(pd.DataFrame({"customer_unique_id": [None]}), .5)
        with self.assertRaises(ValueError): group_subset(pd.DataFrame({"customer_unique_id": ["x"]}), 0)

    def test_stats_denominators_sd_and_categorical_counts(self):
        s = feature_stats(self.frame, self.schema, "hash")
        self.assertEqual(s["numeric"]["total_price"]["missing_n"], 1)
        self.assertEqual(s["numeric"]["total_price"]["sd"], 1)
        self.assertEqual(sum(s["categorical"]["purchase_month"]["normalized_counts"].values()), 4)

    def test_undefined_metric_conventions(self):
        self.assertIsNone(report_metrics("classification", [0, 0], [.1, .2])["average_precision"])
        self.assertIsNone(report_metrics("classification", [0, 1], [.1, .2])["precision_1"])
        self.assertIsNone(report_metrics("regression", [], [])["mae"])
        self.assertIsNone(per_class_report([0, 0], [.1, .2], .5)[1]["recall"])

    def test_basket_boundaries(self):
        self.assertEqual(basket_band(pd.Series([0, 1, 2, 3, 4])).tolist(), ["0", "1", "2-3", "2-3", "4+"])

    def test_no_fit_single_batch_column_row_order_and_isolation(self):
        scorer = Scorer(self.bundle())
        with patch.object(scorer.pipeline, "fit", side_effect=AssertionError("inference fit")):
            batch = scorer.score(self.frame)
            singles = [scorer.score(self.frame.iloc[[i]]).iloc[0].probability_1 for i in range(4)]
            np.testing.assert_allclose(batch.probability_1, singles, atol=1e-12)
            reordered = scorer.score(self.frame.iloc[::-1, ::-1])
            np.testing.assert_allclose(batch.probability_1, reordered.probability_1.iloc[::-1], atol=1e-12)
            extended = scorer.score(self.frame.assign(is_detractor=[9]*4, lead_days=[999]*4))
            np.testing.assert_array_equal(batch.probability_1, extended.probability_1)

    def test_bad_row_isolated_and_null(self):
        scorer = Scorer(self.bundle())
        frame = self.frame.copy(); frame.loc[1, "total_price"] = -1
        scored = scorer.score(frame)
        self.assertEqual(scored.status.tolist(), ["valid", "invalid", "valid", "valid"])
        self.assertTrue(pd.isna(scored.iloc[1].prediction))

    def test_missing_columns_and_duplicate_identifiers(self):
        scorer = Scorer(self.bundle())
        self.assertTrue(scorer.score(self.frame.drop(columns="n_items")).status.eq("invalid").all())
        dup = self.frame.copy(); dup.loc[1, "order_id"] = "a"
        self.assertEqual(scorer.score(dup).status.tolist()[:2], ["invalid", "invalid"])

    def test_missing_unseen_and_all_missing_values(self):
        scorer = Scorer(self.bundle())
        frame = self.frame.copy(); frame.loc[0, PREDICTOR_ALLOWLIST] = np.nan
        frame.loc[1, "primary_category"] = "never_seen_category"
        self.assertTrue(scorer.score(frame).status.eq("valid").all())

    def test_corrupt_bundle_fails_before_deserialization(self):
        path = self.bundle(); (path / "configuration.json").write_text("changed")
        with patch("src.models.score.joblib.load", side_effect=AssertionError("must not load")):
            with self.assertRaises(ValueError): Scorer(path)

    def test_path_traversal_manifest(self):
        path = self.bundle()
        manifest = json.loads((path / "bundle_manifest.json").read_text())
        manifest["output_hashes"]["../classification/configuration.json"] = "bad"
        write_json(manifest, path / "bundle_manifest.json")
        with self.assertRaises(ValueError): checked_manifest(path)

    def test_independent_task_pipelines_and_boundary(self):
        a, b = Scorer(self.bundle("classification")), Scorer(self.bundle("regression"))
        self.assertIsNot(a.pipeline.named_steps["preprocess"], b.pipeline.named_steps["preprocess"])
        threshold = .16387042604339028
        np.testing.assert_array_equal(apply_threshold([np.nextafter(threshold, 0), threshold, np.nextafter(threshold, 1)],
            {"kind": "fixed_threshold", "positive_class": 1, "threshold": threshold}), [0, 1, 1])


if __name__ == "__main__": unittest.main()
