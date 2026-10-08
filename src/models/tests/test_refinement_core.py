"""Synthetic interface tests; no predictive fitting or terminal evaluation."""
import unittest
import numpy as np
import pandas as pd
from src.models.refinement_core import CORE_FEATURES,normalize_core,make_core_pipeline
from src.models.pipelines import normalize_inputs
from src.features.contract import PREDICTOR_ALLOWLIST

class CoreTests(unittest.TestCase):
    def fixture(self):
        return pd.DataFrame([dict(n_items=2,has_items=1,n_products=2,total_price=100,total_freight=10,
            freight_ratio=.1,freight_ratio_missing=0,customer_state='sp',purchase_month=5,purchase_dayofweek=1,purchase_hour=12)])
    def test_matches_original_normalisation(self):
        core=self.fixture()
        envelope=pd.DataFrame({c:[np.nan] for c in PREDICTOR_ALLOWLIST})
        for col in CORE_FEATURES:envelope[col]=core[col]
        normalized,_=normalize_inputs(envelope)
        pd.testing.assert_frame_equal(normalize_core(core),normalized[CORE_FEATURES])
    def test_missing_column_rejected(self):
        with self.assertRaises(ValueError):normalize_core(self.fixture().drop(columns='total_price'))
    def test_extra_outcome_rejected(self):
        f=self.fixture();f['lead_days']=5
        with self.assertRaises(ValueError):normalize_core(f)
    def test_invalid_numbers_rejected(self):
        for col,value in [('n_items',1.2),('total_price',-1),('total_freight',np.inf),('purchase_month',13),('has_items',2),('freight_ratio','bad')]:
            f=self.fixture();f[col]=value
            with self.subTest(col=col),self.assertRaises(ValueError):normalize_core(f)
    def test_null_cell_not_missing_column(self):
        f=self.fixture();f['total_price']=np.nan
        self.assertTrue(normalize_core(f).total_price.isna().all())
    def test_reordered_columns_preserved(self):
        f=self.fixture();pd.testing.assert_frame_equal(normalize_core(f),normalize_core(f[list(reversed(CORE_FEATURES))]))
    def test_states_unknown_semantics(self):
        f=self.fixture();f['customer_state']='bad'
        self.assertEqual(normalize_core(f).customer_state.iloc[0],'Unknown')
    def test_duplicate_columns_rejected(self):
        f=self.fixture();f=pd.concat([f,f[['n_items']]],axis=1)
        with self.assertRaises(ValueError):normalize_core(f)

if __name__=='__main__':unittest.main(verbosity=2)
