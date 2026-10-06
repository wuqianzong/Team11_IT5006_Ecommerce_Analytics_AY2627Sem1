"""Read-only Stage 4 lineage, OOF, search/selection and decision-policy verification."""
from __future__ import annotations

import argparse
import json
import unittest
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.common.loaders import sha256_file
from src.features.contract import PREDICTOR_ALLOWLIST
from .data import ROOT, TARGETS, load_development, task_rows, fold_indices
from .evaluate import metrics
from .io import ids_digest
from .stage4 import choose_candidate, summarize, predict, paired_differences
from .policy import apply_threshold, select_cost_threshold, threshold_curve
from .tuned_pipelines import tuned_state


def assert_metrics(saved, calculated):
    for key,value in calculated.items():
        if isinstance(value,(int,float,np.number)) and not isinstance(value,(bool,np.bool_)):
            np.testing.assert_allclose(saved[key],value,atol=1e-9,rtol=1e-9)
        elif value is not None and saved[key]!=value:
            raise ValueError(f"Metric metadata mismatch: {key}")


def read_csv(path, **kwargs):
    # Saved attainable thresholds can equal a predicted float exactly. Ordinary
    # decimal parsing may move it by an ulp and change a >= boundary decision.
    return pd.read_csv(path, float_precision="round_trip", **kwargs)


def verify(path,root=ROOT):
    path=Path(path)
    manifest=json.loads((path/"run_manifest.json").read_text())
    if manifest["stage"]!=4 or manifest["holdout_evaluated"] is not False:raise ValueError("Invalid stage/holdout")
    for name,digest in manifest["output_hashes"].items():
        file=(path/name).resolve()
        if not file.is_relative_to(path.resolve()) or sha256_file(file)!=digest:raise ValueError(f"Output hash mismatch: {name}")
    development,cv,hashes=load_development(root)
    if hashes!=manifest["input_hashes"]:raise ValueError("Input identity changed")
    config=json.loads((path/"configuration.json").read_text())
    selection=json.loads((path/"selection_record.json").read_text())
    # configuration.json is canonical sorted JSON; config_sha256 identifies the
    # predeclared source bytes. They need not have identical whitespace/key order.
    if selection["config_sha256"]!=manifest["config_sha256"]:raise ValueError("Source configuration identity mismatch")
    if selection["holdout_evaluated"] is not False or selection["features"]!=PREDICTOR_ALLOWLIST:raise ValueError("Selected contract mismatch")
    if sha256_file(path/"selection_record.json")!=manifest["selection_record_sha256"]:raise ValueError("Selection checksum mismatch")
    if selection["input_hashes"]!=hashes:raise ValueError("Selection input mismatch")
    source=root/"artifacts/metrics"/config["stage3_run_id"]
    if sha256_file(source/"run_manifest.json")!=manifest["source_stage3_manifest_sha256"]:raise ValueError("Baseline identity mismatch")
    folds=read_csv(path/"fold_metrics.csv")
    summary=read_csv(path/"cv_summary.csv")
    pd.testing.assert_frame_equal(summarize(folds),summary,check_dtype=False,atol=1e-9,rtol=1e-9)
    pd.testing.assert_frame_equal(paired_differences(folds,config),read_csv(path/"paired_fold_differences.csv"),check_dtype=False,atol=1e-9,rtol=1e-9)
    predictions=read_csv(path/"candidate_oof_predictions.csv",dtype={"order_id":"string"})
    pooled=read_csv(path/"pooled_oof_metrics.csv")
    selected=read_csv(path/"selected_oof_predictions.csv",dtype={"order_id":"string"})
    fits=json.loads((path/"fit_evidence.json").read_text())
    if len(fits)!=manifest["fit_count"] or len(fits)!=config["max_fits"]:raise ValueError("Fit budget/coverage mismatch")
    covered=0
    for task in TARGETS:
        rows=task_rows(development,cv,task)
        winner=choose_candidate(summary,task,config)
        if winner!=selection["tasks"][task]["candidate"]["id"]:raise ValueError("Selected candidate rule mismatch")
        expected_candidates={f"baseline_{m}" for m in ["dummy","linear","tree"]}|{c["id"] for c in config[f"{task}_candidates"]}
        if set(predictions.loc[predictions.task.eq(task)].candidate)!=expected_candidates:raise ValueError("Search candidate coverage")
        for candidate in expected_candidates:
            part=predictions.loc[predictions.task.eq(task)&predictions.candidate.eq(candidate)]
            if part.order_id.duplicated().any() or set(part.order_id)!=set(rows.order_id) or set(part.partition)!={"development_oof"}:raise ValueError("OOF coverage/partition")
            aligned=rows[["order_id",TARGETS[task],"validation_fold"]].merge(part,on="order_id",validate="one_to_one",suffixes=("_source","_output"))
            np.testing.assert_array_equal(aligned.validation_fold_source,aligned.validation_fold_output)
            np.testing.assert_allclose(aligned[TARGETS[task]],aligned.target,atol=1e-12)
            saved=pooled.loc[pooled.task.eq(task)&pooled.candidate.eq(candidate)].iloc[0]
            assert_metrics(saved,metrics(task,aligned.target,aligned.prediction))
            for fold,tr,va in fold_indices(rows):
                partfold=part.loc[part.validation_fold.eq(fold)]
                savedfold=folds.loc[folds.task.eq(task)&folds.candidate.eq(candidate)&folds.fold.eq(fold)&folds.partition.eq("validation")]
                if len(savedfold)!=1:raise ValueError("Fold coverage")
                assert_metrics(savedfold.iloc[0],metrics(task,partfold.target,partfold.prediction))
                covered+=1
        part=selected.loc[selected.task.eq(task)]
        reference=predictions.loc[predictions.task.eq(task)&predictions.candidate.eq(winner)].sort_values("order_id").reset_index(drop=True)
        pd.testing.assert_frame_equal(part.sort_values("order_id").reset_index(drop=True),reference,check_dtype=False,atol=1e-9,rtol=1e-9)
        for fold,tr,va in fold_indices(rows):
            for phase,variant in [("search",None),("selected_diagnostics",None),("sensitivity","no_payment")]+([("sensitivity","item_bearing_only")] if task=="classification" else []):
                records=[f for f in fits if f["task"]==task and f["fold"]==fold and f["phase"]==phase and f.get("variant")==variant]
                if phase=="search" and len(records)!=len(config[f"{task}_candidates"]):raise ValueError("Search fit evidence coverage")
                if phase!="search" and len(records)!=1:raise ValueError("Diagnostic/sensitivity fit coverage")
                actual_tr,actual_va=tr,va
                if variant=="item_bearing_only":
                    actual_tr=tr[rows.iloc[tr].n_items.to_numpy()>0];actual_va=va[rows.iloc[va].n_items.to_numpy()>0]
                for record in records:
                    if record["train_order_ids_sha256"]!=ids_digest(rows.iloc[actual_tr].order_id) or record["validation_order_ids_sha256"]!=ids_digest(rows.iloc[actual_va].order_id):raise ValueError("Fit lineage mismatch")
                    if any(w["category"]=="ConvergenceWarning" for w in record["warnings"]):raise ValueError("Unconverged fit")
            pipe=joblib.load(path/"cv_models"/f"{task}_selected_fold{fold}.joblib")
            score=predict(task,pipe,rows.iloc[va][PREDICTOR_ALLOWLIST])
            expected=rows.iloc[va][["order_id"]].merge(part,on="order_id",validate="one_to_one")
            np.testing.assert_allclose(score,expected.prediction,atol=1e-9,rtol=1e-9)
            evidence=[f for f in fits if f["task"]==task and f["fold"]==fold and f["phase"]=="selected_diagnostics"][0]
            state=tuned_state(pipe,rows.iloc[tr][PREDICTOR_ALLOWLIST])
            if state!= {key:evidence[key] for key in state}:raise ValueError("Saved fold-trained statistics mismatch")
    policy=json.loads((path/"decision_policy.json").read_text())
    if sha256_file(path/"decision_policy.json")!=selection["decision_policy_sha256"]:raise ValueError("Policy checksum mismatch")
    cls=selected.loc[selected.task.eq("classification")].sort_values("order_id")
    cut,report=select_cost_threshold(cls.target,cls.prediction,config["proposed_primary_cost_ratio"])
    if policy["threshold"]!=cut:raise ValueError("Chosen threshold mismatch")
    assert_metrics(selection["policy_metrics"],report)
    policy_pred=read_csv(path/"selected_classification_policy_predictions.csv",dtype={"order_id":"string"}).sort_values("order_id")
    np.testing.assert_array_equal(policy_pred.order_id,cls.order_id)
    np.testing.assert_array_equal(policy_pred.policy_decision,apply_threshold(cls.prediction,policy))
    curve=threshold_curve(cls.target,cls.prediction)
    for ratio in config["cost_ratios"]:curve[f"illustrative_cost_ratio_{ratio}"]=curve.fp+ratio*curve.fn
    pd.testing.assert_frame_equal(curve,read_csv(path/"threshold_curve.csv"),check_dtype=False,atol=1e-12,rtol=1e-12)
    scenarios=read_csv(path/"threshold_scenarios.csv")
    for ratio in config["cost_ratios"]:
        _,calculated=select_cost_threshold(cls.target,cls.prediction,ratio)
        saved=scenarios.loc[scenarios.cost_ratio_fn_to_fp.eq(ratio)&scenarios.policy.eq("optimized_development_oof")].iloc[0]
        assert_metrics(saved,calculated)
    sensitivity=read_csv(path/"sensitivity_oof_predictions.csv",dtype={"order_id":"string"})
    smetrics=read_csv(path/"sensitivity_fold_metrics.csv")
    for (task,variant,scope,fold),part in sensitivity.groupby(["task","variant","model_scope","validation_fold"]):
        rows=task_rows(development,cv,task);expected=rows.loc[rows.validation_fold.eq(fold)]
        if variant=="item_bearing_only":expected=expected.loc[expected.n_items.gt(0)]
        if part.order_id.duplicated().any() or set(part.order_id)!=set(expected.order_id):raise ValueError("Sensitivity matched cohort mismatch")
        saved=smetrics.loc[smetrics.task.eq(task)&smetrics.variant.eq(variant)&smetrics.model_scope.eq(scope)&smetrics.fold.eq(fold)].iloc[0]
        aligned=expected[["order_id",TARGETS[task]]].merge(part,on="order_id",validate="one_to_one")
        np.testing.assert_allclose(aligned[TARGETS[task]],aligned.target,atol=1e-12)
        assert_metrics(saved,metrics(task,part.target,part.prediction))
    result=unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.discover(str(root/"src/models/tests")))
    if not result.wasSuccessful():raise ValueError("Fixtures failed")
    report={"status":"passed_internal_verification","stage":4,"fits":len(fits),"candidate_fold_metrics":covered,
        "output_files_checked":len(manifest["output_hashes"]),"unit_tests":result.testsRun,"holdout_evaluated":False,
        "selected_candidates":{task:selection["tasks"][task]["candidate"]["id"] for task in TARGETS},
        "independent_agent_review":"pending","team_explanation_review":"pending"}
    print(json.dumps(report,indent=2));return report


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--run-id",default="stage4-selection-v1")
    args=parser.parse_args()
    if Path(args.run_id).name!=args.run_id:raise ValueError("Unsafe run ID")
    verify(ROOT/"artifacts/metrics"/args.run_id)
