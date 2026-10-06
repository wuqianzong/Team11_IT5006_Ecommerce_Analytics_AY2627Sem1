from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import joblib
import numpy as np
import pandas as pd

from src.models.policy import threshold_curve, select_cost_threshold, apply_threshold
from src.models.stage4 import CONFIG, choose_candidate, Budget, permutation_blocks
from src.models.train import DEFAULT_CONFIG
from src.models.tuned_pipelines import make_tuned_pipeline, tuned_state, PAYMENT_COLUMNS
from src.models.tests.test_baselines import fixture


class Stage4Tests(unittest.TestCase):
    def setUp(self):
        self.x=fixture();self.y=np.array([0,1]*6)
        self.base=json.loads(DEFAULT_CONFIG.read_text());self.config=json.loads(CONFIG.read_text())

    def test_threshold_matches_exhaustive(self):
        y=np.array([1,0,1,0,1,0]);p=np.array([0,.2,.2,.8,1,1])
        for ratio in [1,2,5,10]:
            cut,result=select_cost_threshold(y,p,ratio)
            candidates=[np.nextafter(1.,np.inf),*np.unique(p)]
            costs=[int(((p>=t)&(y==0)).sum()+ratio*((p<t)&(y==1)).sum()) for t in candidates]
            best=min(costs)
            self.assertEqual(result["illustrative_cost"],best)
            self.assertEqual(cut,max(t for t,c in zip(candidates,costs) if c==best))

    def test_exact_score_ties_not_split(self):
        curve=threshold_curve([1,0,1,0],[.5]*4)
        self.assertEqual(len(curve),2)
        self.assertEqual(curve.iloc[1].tp,2);self.assertEqual(curve.iloc[1].fp,2)

    def test_no_alert_endpoint(self):
        t,result=select_cost_threshold([0,0],[1,1],1)
        self.assertGreater(t,1);self.assertEqual(result["alerts"],0)

    def test_threshold_monotonic_counts(self):
        curve=threshold_curve(self.y,np.linspace(0,1,12))
        self.assertTrue((np.diff(curve.tp)>=0).all());self.assertTrue((np.diff(curve.fp)>=0).all())

    def test_bad_policy_inputs(self):
        for y,p in [([],[]),([2],[.5]),([0],[np.nan]),([0],[1.1])]:
            with self.assertRaises(ValueError):threshold_curve(y,p)
        with self.assertRaises(ValueError):select_cost_threshold([0],[.2],0)

    def test_policy_boundary_serialization_and_row_order(self):
        policy={"kind":"fixed_threshold","positive_class":1,"threshold":.2}
        p=np.array([.1,.2,.3])
        np.testing.assert_array_equal(apply_threshold(p,policy),[0,1,1])
        np.testing.assert_array_equal(apply_threshold(p[::-1],json.loads(json.dumps(policy))),[1,1,0])
        with self.assertRaises(ValueError):apply_threshold([np.inf],policy)

    def test_exact_threshold_csv_float_roundtrip(self):
        from src.models.verify_stage4 import read_csv
        value=.12345678901234567
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"probabilities.csv"
            pd.DataFrame({"prediction":[value]}).to_csv(path,index=False)
            loaded=read_csv(path).prediction.to_numpy()
            self.assertEqual(loaded[0],value)
            policy={"kind":"fixed_threshold","positive_class":1,"threshold":value}
            np.testing.assert_array_equal(apply_threshold(loaded,policy),[1])

    def test_selection_prefers_simplicity_within_margin(self):
        table=pd.DataFrame({"task":["classification"]*3,"candidate":["b","c","a"],
                            "family":["linear","forest","logistic"],"average_precision_mean":[.299,.3,.2995]})
        self.assertEqual(choose_candidate(table,"classification",self.config),"b")
        table.average_precision_mean=[.297,.3,.2975]
        self.assertEqual(choose_candidate(table,"classification",self.config),"c")

    def test_regression_selection_direction(self):
        table=pd.DataFrame({"task":["regression"]*2,"candidate":["a","b"],"family":["linear","forest"],"mae_mean":[5.01,5.]})
        self.assertEqual(choose_candidate(table,"regression",self.config),"a")
        table.mae_mean=[5.03,5.]
        self.assertEqual(choose_candidate(table,"regression",self.config),"b")

    def test_fit_budget_rejects_extra_fit(self):
        budget=Budget({"max_fits":0,"max_wall_seconds":100})
        with self.assertRaises(RuntimeError):budget.fit(None,None,None)

    def test_time_budget_rejects_fit(self):
        budget=Budget({"max_fits":1,"max_wall_seconds":0})
        with self.assertRaises(RuntimeError):budget.fit(None,None,None)

    def test_all_candidate_factories_and_train_only_stats(self):
        for task in ["regression","classification"]:
            for candidate in self.config[f"{task}_candidates"]:
                # Small synthetic forest size only for the fixture, not real search.
                candidate=json.loads(json.dumps(candidate))
                if candidate["family"]=="forest":candidate["params"]["n_estimators"]=2
                pipe=make_tuned_pipeline(task,candidate,self.base).fit(self.x,self.y)
                state=tuned_state(pipe,self.x)
                self.assertIn("total_price",state["imputer_statistics"])
                self.assertEqual(state["dimension"],len(state["transformed_feature_names"]))
                self.assertEqual(state["imputer_statistics"]["total_price"],np.median(self.x.total_price))
                if candidate["family"] in {"tree","forest"}:
                    self.assertNotIn("scale",pipe.named_steps["preprocess"].named_transformers_["numeric"].named_steps)

    def test_no_payment_is_real_exclusion_and_stats_names(self):
        candidate=self.config["classification_candidates"][0]
        pipe=make_tuned_pipeline("classification",candidate,self.base,"no_payment").fit(self.x,self.y)
        names=pipe[:-1].get_feature_names_out()
        state=tuned_state(pipe,self.x)
        for col in PAYMENT_COLUMNS:
            self.assertFalse(any(col in name for name in names))
            self.assertNotIn(col,state["imputer_statistics"])
        changed=self.x.copy();changed.primary_payment_type="boleto";changed.payment_installments_max=99
        np.testing.assert_allclose(pipe.predict_proba(self.x),pipe.predict_proba(changed))

    def test_metadata_column_reorder_and_fresh_reload(self):
        candidate=self.config["classification_candidates"][0]
        pipe=make_tuned_pipeline("classification",candidate,self.base).fit(self.x,self.y)
        score=pipe.predict_proba(self.x)
        x=self.x.iloc[:,::-1].copy();x["target"]=self.y;x["lead_days"]=999
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"model.joblib";joblib.dump(pipe,p)
            restored=joblib.load(p)
            np.testing.assert_allclose(score,restored.predict_proba(x),atol=1e-12)

    def test_joint_permutation_does_not_fit_or_mutate_inputs(self):
        candidate=self.config["classification_candidates"][0]
        pipe=make_tuned_pipeline("classification",candidate,self.base).fit(self.x,self.y)
        original=self.x.copy();config={**self.config,"permutation_repeats":1}
        with patch.object(pipe,"fit",side_effect=AssertionError("No fitting permitted")):
            results=permutation_blocks("classification",pipe,self.x,self.y,np.arange(12),0,config)
        self.assertEqual(len(results),8)
        pd.testing.assert_frame_equal(original,self.x)


if __name__=="__main__":unittest.main()
