from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import joblib
import numpy as np
import pandas as pd
from scipy import sparse

from src.features.contract import PREDICTOR_ALLOWLIST, NUMERIC_COLUMNS, CATEGORICAL_COLUMNS
from src.models.audit import first_review_audit
from src.models.data import fold_indices
from src.models.evaluate import metrics, capacity_metrics
from src.models.pipelines import make_pipeline, normalize_inputs, positive_probability, encoding_audit
from src.models.predict import score_checkpoint
from src.models.train import DEFAULT_CONFIG, run, transformed_evidence


def fixture():
    x=pd.DataFrame({c:np.ones(12) for c in PREDICTOR_ALLOWLIST})
    x["customer_state"]=["SP","RJ"]*6
    x["primary_seller_state"]="SP";x["primary_category"]=["books","toys"]*6
    x["primary_payment_type"]="credit_card";x["purchase_hour"]=12;x["purchase_dayofweek"]=0
    x["total_price"]=np.arange(12)*10+1
    x["total_freight"]=np.arange(12)+1
    x["freight_ratio"]=x.total_freight/x.total_price
    x["volume_missing_fraction"]=0;x["weight_missing_fraction"]=0
    x["distance_missing_fraction"]=0;x["category_missing_fraction"]=0
    return x


class BaselineContractTests(unittest.TestCase):
    def setUp(self):
        self.x=fixture();self.config=json.loads(DEFAULT_CONFIG.read_text());self.y=np.array([0,1]*6)

    def test_missing_column(self):
        with self.assertRaisesRegex(ValueError,"Missing predictor"):normalize_inputs(self.x.drop(columns="n_items"))

    def test_duplicate_columns(self):
        with self.assertRaises(ValueError):normalize_inputs(pd.concat([self.x,self.x[["n_items"]]],axis=1))

    def test_malformed_numeric(self):
        x=self.x.astype(object);x.loc[0,"total_price"]="bad"
        with self.assertRaises(ValueError):normalize_inputs(x)

    def test_infinities(self):
        for value in [np.inf,-np.inf]:
            x=self.x.astype({"total_price":float});x.loc[0,"total_price"]=value
            with self.assertRaises(ValueError):normalize_inputs(x)

    def test_negative(self):
        for col in ["n_items","total_price","distance_km_max"]:
            x=self.x.copy();x.loc[0,col]=-1
            with self.assertRaises(ValueError):normalize_inputs(x)

    def test_fractional_count(self):
        x=self.x.copy();x.loc[0,"n_items"]=1.5
        with self.assertRaises(ValueError):normalize_inputs(x)

    def test_flag_range(self):
        x=self.x.copy();x.loc[0,"has_items"]=2
        with self.assertRaises(ValueError):normalize_inputs(x)

    def test_positive_measurements(self):
        for col in ["total_weight_g","total_volume_cm3","payment_installments_max"]:
            x=self.x.copy();x.loc[0,col]=0
            with self.assertRaises(ValueError):normalize_inputs(x)

    def test_fraction_range(self):
        x=self.x.copy();x.loc[0,"interstate_share"]=1.1
        with self.assertRaises(ValueError):normalize_inputs(x)

    def test_calendar_range(self):
        for col,value in [("purchase_month",13),("purchase_dayofweek",7),("purchase_hour",24)]:
            x=self.x.copy();x.loc[0,col]=value
            with self.assertRaises(ValueError):normalize_inputs(x)

    def test_calendar_normalization(self):
        x=self.x.astype(object);x.loc[0,"purchase_month"]="1.0"
        normalized,_=normalize_inputs(x)
        self.assertEqual(normalized.loc[0,"purchase_month"],normalized.loc[1,"purchase_month"])

    def test_state_payment_quality(self):
        x=self.x.copy();x.loc[0,"customer_state"]="Europe";x.loc[0,"primary_payment_type"]="bad"
        normalized,quality=normalize_inputs(x)
        self.assertEqual(normalized.loc[0,"customer_state"],"Unknown")
        self.assertEqual(quality["primary_payment_type"]["malformed_tokens"],1)

    def test_nulls_unseen_all_missing_stable(self):
        x=self.x.copy();x["total_weight_g"]=np.nan
        p=make_pipeline("classification","linear",self.config).fit(x,self.y)
        future=x.iloc[:2].copy();future.loc[future.index[0],"primary_category"]="valid_unseen_category"
        future.loc[future.index[1],"total_price"]=np.nan
        z=p[:-1].transform(future);values=z.data if sparse.issparse(z) else z
        self.assertTrue(np.isfinite(values).all())
        self.assertEqual(z.shape[1],len(p[:-1].get_feature_names_out()))
        stats=p.named_steps["preprocess"].named_transformers_["numeric"].named_steps["impute"].statistics_
        self.assertEqual(stats[NUMERIC_COLUMNS.index("total_weight_g")],0)
        self.assertEqual(encoding_audit(p,future)["categories"]["primary_category"]["unseen_count"],1)

    def test_reordered_columns_and_metadata_isolation(self):
        p=make_pipeline("classification","linear",self.config).fit(self.x,self.y)
        reordered=self.x[list(reversed(self.x.columns))].assign(lead_days=999,is_detractor=1,customer_unique_id="secret")
        np.testing.assert_allclose(positive_probability(p,self.x),positive_probability(p,reordered))
        self.assertFalse(set(["lead_days","is_detractor","customer_unique_id"]) & set(p.named_steps["inputs"].get_feature_names_out()))

    def test_validation_perturbation_does_not_fit(self):
        p=make_pipeline("classification","linear",self.config).fit(self.x,self.y)
        before=transformed_evidence(p,self.x)
        future=self.x.assign(total_price=999999,primary_category="future_only",is_detractor=1-self.y)
        positive_probability(p,future)
        after=transformed_evidence(p,self.x)
        self.assertEqual(before,after)

    def test_independent_pipeline_fitting(self):
        p=make_pipeline("classification","linear",self.config).fit(self.x,self.y)
        before=positive_probability(p,self.x)
        q=make_pipeline("classification","tree",self.config).fit(self.x.assign(total_price=555),1-self.y)
        self.assertIsNot(p.named_steps["preprocess"],q.named_steps["preprocess"])
        np.testing.assert_array_equal(before,positive_probability(p,self.x))

    def test_artifact_reload_single_batch_and_reorder(self):
        for task in ["regression","classification"]:
            p=make_pipeline(task,"linear",self.config).fit(self.x,self.y if task=="classification" else np.arange(12)+1)
            with tempfile.TemporaryDirectory() as temp:
                path=Path(temp)/"p.joblib";joblib.dump(p,path)
                x=self.x.assign(order_id=[f"o{i}" for i in range(12)])
                batch=score_checkpoint(path,x,task)
                singles=pd.concat([score_checkpoint(path,x.iloc[[i]],task) for i in range(12)])
                np.testing.assert_allclose(batch.prediction,singles.prediction,atol=1e-12,rtol=1e-12)
                reordered=score_checkpoint(path,x.iloc[::-1][list(reversed(x.columns))],task)
                np.testing.assert_allclose(batch.prediction.to_numpy()[::-1],reordered.prediction,atol=1e-12,rtol=1e-12)
                if task=="classification":np.testing.assert_array_equal(batch.diagnostic_decision,singles.diagnostic_decision)

    def test_factory_baseline_conventions(self):
        p=make_pipeline("classification","linear",self.config)
        self.assertEqual(p.named_steps["model"].C,np.inf)
        self.assertIsNone(p.named_steps["model"].class_weight)
        t=make_pipeline("regression","tree",self.config)
        self.assertNotIn("scale",t.named_steps["preprocess"].transformers[0][1].named_steps)
        self.assertEqual(t.named_steps["model"].criterion,"squared_error")

    def test_positive_class_mapping(self):
        class Fake:
            named_steps={"model":type("Estimator",(),{"classes_":np.array([1,0])})()}
            def predict_proba(self,x):return np.array([[.8,.2]])
        self.assertEqual(positive_probability(Fake(),None)[0],.8)

    def test_known_metrics(self):
        r=metrics("regression",[1,3],[2,2]);self.assertEqual(r["mae"],1);self.assertEqual(r["rmse"],1)
        c=metrics("classification",[0,0,1,1],[.1,.7,.8,.2])
        self.assertEqual([c[k] for k in ["tn","fp","fn","tp"]],[1,1,1,1])
        self.assertEqual(c["f1_1"],.5)

    def test_undefined_subgroup_metrics(self):
        c=metrics("classification",[0,0],[.1,.2]);self.assertIsNone(c["roc_auc"]);self.assertIsNone(c["average_precision"])
        self.assertIsNone(c["recall_1"]);self.assertFalse(c["precision_defined"])

    def test_capacity_ties(self):
        c=capacity_metrics([0,1],[.2,.2],["b","a"],.5)
        self.assertEqual(c["captured_positives"],1)

    def test_group_overlap_rejected(self):
        rows=pd.DataFrame({"validation_fold":[0,1],"customer_unique_id":["same","same"]})
        with self.assertRaises(ValueError):list(fold_indices(rows))

    def test_review_audit_validity_exclusions_and_tie(self):
        development=pd.DataFrame({"order_id":["a","b"],"prediction_timestamp":["2020-01-01"]*2,
            "eligible_classification":[1,1],"review_score_min":[1,5],"is_detractor":[1,0],"review_count":[4,1]})
        reviews=pd.DataFrame({"order_id":["a"]*4+["b"],"review_id":["z","a","c","d","e"],
            "review_score":[5,4,1,9,5],"review_answer_timestamp":["2020-01-03","2020-01-03",None,"2019-12-01","2019-12-01"]})
        common,summary=first_review_audit(development,reviews)
        self.assertEqual(common.review_score_first.iloc[0],4)
        self.assertEqual(common.label_disagrees.iloc[0],1)
        self.assertEqual(summary["missing_alternative_orders"],1)
        self.assertEqual(summary["exclusions_first_failure"]["answer_before_purchase"],1)
        self.assertEqual(summary["exclusions_first_failure"]["invalid_score"],1)

    def test_no_overwrite_and_failed_new_run_cleanup(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);old=root/"artifacts/metrics/existing";old.mkdir(parents=True)
            sentinel=old/"sentinel";sentinel.write_text("preserve")
            with self.assertRaises(FileExistsError):run(root=root,run_id="existing")
            with patch("src.models.train.identity",return_value={}),patch("src.models.train.load_development",return_value=(None,None,{})),patch("src.models.train.run_audits",side_effect=ValueError("injected audit failure")):
                with self.assertRaisesRegex(ValueError,"injected"):run(root=root,run_id="new")
            self.assertFalse((root/"artifacts/metrics/new").exists());self.assertEqual(sentinel.read_text(),"preserve")
            self.assertEqual([p.name for p in old.parent.iterdir()],["existing"])


if __name__=="__main__":unittest.main()
