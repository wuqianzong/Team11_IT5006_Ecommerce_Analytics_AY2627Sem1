"""Catalogue, stable serialization and legacy loading checks; no data fits."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import joblib
from .combination_runner import design
from .inputs import SubsetInputContract, load_trial
from .runner import ROOT
from src.models.refinement_core import CORE_FEATURES


class CombinationTests(unittest.TestCase):
    def test_budget_tasks_and_unique_columns(self):
        protocol, _ = design()
        self.assertEqual(sum(len(b['tasks']) for b in protocol['blocks']), 10)
        self.assertEqual(sum('regression' in b['tasks'] for b in protocol['blocks']), 6)
        self.assertEqual(sum('classification' in b['tasks'] for b in protocol['blocks']), 4)
        for b in protocol['blocks']:
            self.assertEqual(len(b['columns']), len(set(b['columns'])))
            self.assertFalse(set(b['columns']) & set(CORE_FEATURES))
            if 'payment' in b['add_blocks']:
                self.assertTrue(b['retrospective_sensitivity_only'])

    def test_stable_contract_loads_in_fresh_process(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'contract.joblib'
            joblib.dump(SubsetInputContract(tuple(CORE_FEATURES)), path)
            subprocess.run([sys.executable, '-c', 'import joblib,sys; x=joblib.load(sys.argv[1]); assert x.__class__.__module__ == "experiments.feature_selection_v3.inputs"', str(path)], cwd=ROOT, check=True)

    def test_legacy_loader_restores_main_namespace(self):
        module = sys.modules['__main__']
        previous = getattr(module, 'SubsetInputContract', None)
        had = hasattr(module, 'SubsetInputContract')
        # Synthetic serialization fixture: no saved Olist model dependency.
        from .runner import SubsetInputContract as Legacy
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'legacy.joblib'
            old_identity = Legacy.__module__
            module.SubsetInputContract = Legacy
            try:
                Legacy.__module__ = '__main__'
                joblib.dump(Legacy(tuple(CORE_FEATURES)), path)
            finally:
                Legacy.__module__ = old_identity
                if had:
                    module.SubsetInputContract = previous
                else:
                    del module.SubsetInputContract
            pipeline = load_trial(path)
        self.assertEqual(list(pipeline.columns), CORE_FEATURES)
        self.assertEqual(hasattr(module, 'SubsetInputContract'), had)
        self.assertIs(getattr(module, 'SubsetInputContract', None), previous)


if __name__ == '__main__':
    unittest.main()
