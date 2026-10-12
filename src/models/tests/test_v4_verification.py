"""Verification guards and metric comparisons; no model fitting or real data."""
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src.models.refinement_selected_v4_verify import compare_tables, output_location


class V4VerificationTests(unittest.TestCase):
    def table(self):
        return pd.DataFrame({'task': ['regression', 'classification'],
                             'n': [10, 12], 'score': [0.2, np.nan], 'defined': [True, False]})

    def test_boolean_nan_and_reordered_rows_compare(self):
        expected = self.table()
        result = compare_tables(expected.iloc[::-1], expected, ['task'])
        self.assertTrue(result.passed.all())

    def test_changed_metric_fails(self):
        expected = self.table()
        changed = expected.copy(); changed.loc[0, 'score'] += 0.001
        self.assertFalse(compare_tables(changed, expected, ['task']).passed.all())

    def test_missing_value_is_not_silently_equal(self):
        expected = self.table()
        changed = expected.copy(); changed.loc[0, 'score'] = np.nan
        self.assertFalse(compare_tables(changed, expected, ['task']).passed.all())

    def test_missing_and_duplicate_rows_refused(self):
        expected = self.table()
        for changed in [expected.iloc[:1], pd.concat([expected, expected])]:
            with self.assertRaises(ValueError):
                compare_tables(changed, expected, ['task'])

    def test_missing_column_refused(self):
        with self.assertRaises(ValueError):
            compare_tables(self.table().drop(columns='score'), self.table(), ['task'])

    def test_evidence_and_existing_output_protected(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = Path(tmp) / 'frozen'; run.mkdir()
            for output in [run, run / 'terminal/new', Path(tmp)]:
                with self.assertRaises((ValueError, FileExistsError)):
                    output_location(run, output)
            self.assertEqual(output_location(run, Path(tmp)/'new'), (Path(tmp)/'new').resolve())


if __name__ == '__main__':
    unittest.main()
