import json
import unittest
import numpy as np
import pandas as pd
from sklearn.base import clone
from src.models.refinement_selected import CONFIG
from src.models.refinement_inputs import SelectedInputs, selected_pipeline


class SelectedContractTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads(CONFIG.read_text())
        self.row = dict(n_items=1, has_items=1, n_products=1, total_price=100., total_freight=10., freight_ratio=.1,
                        freight_ratio_missing=0, customer_state='SP', purchase_month=1, purchase_dayofweek=0, purchase_hour=12,
                        distance_km_max=200., distance_missing_fraction=0, n_sellers=1, primary_seller_state='SP', interstate_share=0.)

    def test_task_shapes_and_fresh_pipeline(self):
        for task, count in [('regression', 13), ('classification', 14)]:
            cols = self.config['predictors_by_task'][task]
            self.assertEqual(len(cols), count)
            pipe = selected_pipeline(task, self.config['selected'][task], self.config['baseline_config'], cols)
            other = clone(pipe)
            self.assertIsNot(pipe.named_steps['preprocess'], other.named_steps['preprocess'])
            self.assertEqual(list(pipe.named_steps['inputs'].columns), cols)

    def test_strict_and_malformed_inputs(self):
        cols = self.config['predictors_by_task']['regression']
        f = pd.DataFrame([self.row])[cols]
        contract = SelectedInputs(tuple(cols))
        self.assertEqual(contract.transform(f).shape, (1, 13))
        for bad in [f.drop(columns='n_items'), f.assign(review_score=1), f.assign(n_items=1.5), f.assign(distance_missing_fraction=1.1), f.assign(distance_km_max=np.inf)]:
            with self.assertRaises(ValueError):
                contract.transform(bad)

    def test_no_terminal_selection_and_fit_budget(self):
        self.assertFalse(self.config['terminal_evaluation_allowed'])
        self.assertEqual(self.config['application_fit_ceiling'], 19)


if __name__ == '__main__':
    unittest.main()
