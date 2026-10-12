"""Check grid-export metric signs and safe output boundaries."""
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.model_selection import GridSearchCV
from experiments.experiment_3.run_phase4_transforms_and_tuning import export_grid_results
from experiments.experiment_3.reproduce_tuning import reproduce, ROOT


class TuningExportTest(unittest.TestCase):
    def test_mae_export_retains_rank_and_fold_variation(self):
        x = np.arange(24).reshape(-1, 1)
        y = np.arange(24) + np.sin(np.arange(24))
        search = GridSearchCV(Ridge(), {'alpha': [0.01, 100]}, cv=3,
                              scoring='neg_mean_absolute_error', return_train_score=True).fit(x, y)
        with tempfile.TemporaryDirectory() as tmp:
            frame = export_grid_results(search, Path(tmp)/'grid.csv', 'regression', 'Ridge')
            np.testing.assert_allclose(frame.mean_test_metric, -frame.mean_test_score)
            np.testing.assert_array_equal(frame.rank_test_score, search.cv_results_['rank_test_score'])
            np.testing.assert_allclose(frame.std_test_score, search.cv_results_['std_test_score'])
            folds = frame[[f'split{i}_test_metric' for i in range(3)]]
            np.testing.assert_allclose(folds.mean(axis=1), frame.mean_test_metric)
            np.testing.assert_allclose(folds.std(axis=1, ddof=0), frame.std_test_score)
            self.assertEqual(frame.selected.sum(), 1)
            self.assertTrue(frame.iloc[search.best_index_].selected)
            self.assertEqual(len(pd.read_csv(Path(tmp)/'grid.csv')), 2)

    def test_canonical_directory_is_rejected_before_training(self):
        with self.assertRaises(ValueError):
            reproduce(ROOT/'artifacts/metrics/refinement-selected-v4')

    def test_existing_output_is_rejected_before_training(self):
        with patch('pathlib.Path.exists', return_value=True):
            with self.assertRaises(FileExistsError):
                reproduce(ROOT/'artifacts/reproduction/test-existing-output')


if __name__ == '__main__':
    unittest.main()
