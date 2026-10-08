"""Frozen taught-family comparison checks; no performance fits."""
import unittest
from .model_runner import design
from .runner import make_pipeline
from .inputs import SubsetInputContract
from src.models.refinement_core import CORE_FEATURES


class ModelGateTests(unittest.TestCase):
    def test_budget_reuse_and_shortlist(self):
        protocol, _ = design()
        self.assertEqual(len(protocol['blocks']) * 5, 50)
        self.assertEqual(len(protocol['reuse']) * 5, 15)
        self.assertEqual(protocol['feature_selection_attempts_already_consumed'], 100)
        self.assertFalse(protocol['terminal_evaluation_allowed'])
        expected = {'r13': 13, 'r19': 19, 'c14': 14}
        for b in protocol['blocks']:
            self.assertEqual(len(CORE_FEATURES + b['columns']), expected[b['feature_set']])

    def test_baseline_model_factories(self):
        protocol, config = design()
        for b in protocol['blocks']:
            cols = CORE_FEATURES + b['columns']
            pipe = make_pipeline(b['tasks'][0], b['candidate'], config['baseline_config'], cols)
            pipe.set_params(inputs=SubsetInputContract(tuple(cols)))
            self.assertEqual(list(pipe.named_steps['inputs'].columns), cols)
            self.assertFalse(hasattr(pipe.named_steps['model'], 'n_features_in_'))
            if b['id'] == 'c14_plain_logistic':
                self.assertEqual(pipe.named_steps['model'].C, float('inf'))


if __name__ == '__main__':
    unittest.main()
