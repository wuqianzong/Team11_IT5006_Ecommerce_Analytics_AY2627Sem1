"""Synthetic schema/rule tests only; not Olist performance evidence."""
import unittest
import numpy as np
import pandas as pd
from sklearn.base import clone
from .runner import SubsetInputContract, read_design, make_pipeline, screen_flag, canonical_membership
from src.models.refinement_core import CORE_FEATURES, normalize_core

class FeatureScreenTests(unittest.TestCase):
    def setUp(self):
        self.protocol, self.config = read_design()
        self.row = {'n_items': 2, 'has_items': 1, 'n_products': 1, 'total_price': 30.,
                    'total_freight': 5., 'freight_ratio': 1/6, 'freight_ratio_missing': 0,
                    'customer_state': 'sp', 'purchase_month': 5, 'purchase_dayofweek': 2, 'purchase_hour': 14}

    def test_exact_core_normalization(self):
        f = pd.DataFrame([self.row])
        pd.testing.assert_frame_equal(SubsetInputContract(tuple(CORE_FEATURES)).transform(f), normalize_core(f))

    def test_missing_and_extra_columns_rejected(self):
        f = pd.DataFrame([self.row])
        contract = SubsetInputContract(tuple(CORE_FEATURES))
        for malformed in [f.drop(columns='n_items'), f.assign(is_detractor=1)]:
            with self.assertRaises(ValueError):
                contract.transform(malformed)

    def test_duplicate_column_and_feature_rejected(self):
        f = pd.DataFrame([self.row])
        with self.assertRaises(ValueError):
            SubsetInputContract(tuple(CORE_FEATURES) + ('n_items',)).transform(f)
        with self.assertRaises(ValueError):
            SubsetInputContract(tuple(CORE_FEATURES)).transform(pd.concat([f, f[['n_items']]], axis=1))

    def test_fraction_and_bad_numeric_rejected(self):
        f = pd.DataFrame([{**self.row, 'distance_missing_fraction': 1.1}])
        with self.assertRaises(ValueError):
            SubsetInputContract(tuple(f.columns)).transform(f)
        with self.assertRaises(ValueError):
            SubsetInputContract(tuple(CORE_FEATURES)).transform(pd.DataFrame([{**self.row, 'total_price': 'bad'}]))

    def test_fresh_preprocessors_and_only_selected_columns(self):
        for block in self.protocol['blocks']:
            cols = CORE_FEATURES + block['columns']
            a = make_pipeline('classification', self.config['selected']['classification'], self.config['baseline_config'], cols)
            b = clone(a)
            actual = [c for _, _, cs in a.named_steps['preprocess'].transformers for c in cs]
            self.assertEqual(set(actual), set(cols))
            self.assertIsNot(a.named_steps['preprocess'], b.named_steps['preprocess'])

    def test_promising_needs_mean_and_four_windows(self):
        self.assertTrue(screen_flag('classification', [.01]*5, self.protocol))
        self.assertFalse(screen_flag('classification', [.02, .02, .02, -.001, -.001], self.protocol))
        self.assertFalse(screen_flag('regression', [.04]*5, self.protocol))
        with self.assertRaises(ValueError):
            screen_flag('regression', [np.nan]*5, self.protocol)

    def test_no_terminal_or_automatic_followup(self):
        self.assertFalse(self.protocol['terminal_evaluation_allowed'])
        self.assertFalse(self.protocol['followup_execution_allowed'])
        self.assertEqual(self.protocol['stage_fit_ceiling'], 50)

    def test_membership_values_not_storage_dtype(self):
        original = pd.DataFrame({'task': ['regression'], 'fold': [0], 'role': ['training'], 'order_id': ['abc']})
        reloaded = original.astype({'order_id': 'string'})
        pd.testing.assert_frame_equal(canonical_membership(original), canonical_membership(reloaded))
        with self.assertRaises(ValueError):
            canonical_membership(pd.concat([original, original]))

if __name__ == '__main__':
    unittest.main(verbosity=2)
