"""Synthetic structural tests; never project performance evidence."""
import json
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from experiments.refinement_cycle1.initial_reference.diagnostics import RareState, pipeline, choose, complete_mask, PROTOCOL

class DiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.protocol = json.loads(PROTOCOL.read_text())
    def test_primary_predictor_columns_exact(self):
        for task in ['regression','classification']:
            for c in self.protocol['candidates'][task]:
                p = pipeline(task,c,self.protocol['baseline_config'],self.protocol['primary_features'])
                cols = [x for _,_,columns in p.named_steps['preprocess'].transformers for x in columns]
                self.assertEqual(set(cols),set(self.protocol['primary_features']))
                self.assertFalse(set(cols) & {'n_sellers','n_categories','primary_payment_type'})
    def test_fresh_transformers(self):
        c=self.protocol['candidates']['regression'][1]
        a=pipeline('regression',c,self.protocol['baseline_config'],self.protocol['primary_features'])
        b=pipeline('regression',c,self.protocol['baseline_config'],self.protocol['primary_features'])
        self.assertIsNot(a.named_steps['preprocess'].transformers[0][1],b.named_steps['preprocess'].transformers[0][1])
    def test_rare_mapping_train_only_unknown_distinct(self):
        train=pd.DataFrame({'customer_state':['SP']*8+['RJ','Unknown']})
        t=RareState().fit(train)
        val=pd.DataFrame({'customer_state':['SP','RJ','AC','Unknown']})
        self.assertEqual(t.transform(val).customer_state.tolist(),['SP','__REFINEMENT_RARE__','__REFINEMENT_RARE__','Unknown'])
        self.assertNotIn('AC',t.seen_)
        self.assertEqual(val.customer_state.tolist(),['SP','RJ','AC','Unknown'])
    def test_complete_case_null_fails(self):
        f=pd.DataFrame({'has_items':[1,1,1], 'payment_missing':[0,0,0],
                        'weight_missing_fraction':[0,np.nan,.1], 'volume_missing_fraction':[0,0,0],
                        'category_missing_fraction':[0,0,0], 'distance_missing_fraction':[0,0,0]})
        self.assertEqual(complete_mask(f).tolist(),[True,False,False])
    def test_selection_simpler_within_tolerance(self):
        cs=[{'id':'simple','family':'linear'}, {'id':'complex','family':'forest','params':{'max_depth':16,'min_samples_leaf':20}}]
        records=[{'experiment':'E01','task':'regression','candidate':c['id'],'partition':'validation','mae':5.01 if c['id']=='simple' else 5.0} for c in cs for fold in range(5)]
        self.assertEqual(choose(records,'regression',cs)['id'],'simple')
    def test_incomplete_comparison_rejected(self):
        with self.assertRaises(ValueError):
            choose([], 'regression',[{'id':'missing','family':'linear'}])
    def test_budget_exact(self):
        self.assertEqual(sum(x['predictive_fits'] for x in self.protocol['experiments']),255)

if __name__=='__main__':unittest.main(verbosity=2)
