"""Read-only Stage 3 artifact verification plus contract fixtures. Never fit real data."""
from __future__ import annotations

import argparse
import json
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from src.common.loaders import sha256_file
from .data import ROOT, TARGETS, load_development, task_rows, fold_indices
from .evaluate import metrics
from .io import ids_digest


def verify(path: Path, root=ROOT):
    manifest=json.loads((path/"run_manifest.json").read_text())
    if manifest["holdout_evaluated"] is not False or manifest["stage"]!=3:
        raise ValueError("Wrong stage or holdout access")
    for relative,digest in manifest["output_hashes"].items():
        file=(path/relative).resolve()
        if not file.is_relative_to(path.resolve()) or sha256_file(file)!=digest:
            raise ValueError(f"Output checksum mismatch: {relative}")
    development,cv,hashes=load_development(root)
    if hashes!=manifest["input_hashes"]:raise ValueError("Input identity changed")
    if ids_digest(development.order_id)!=manifest["development_order_ids_sha256"]:
        raise ValueError("Development population mismatch")
    predictions=pd.read_csv(path/"oof_predictions.csv",dtype={"order_id":"string"})
    pooled=pd.read_csv(path/"pooled_oof_metrics.csv")
    fits=json.loads((path/"fit_evidence.json").read_text())
    fold_metrics=pd.read_csv(path/"fold_metrics.csv")
    checked=0
    for task in TARGETS:
        rows=task_rows(development,cv,task)
        for model in ["dummy","linear","tree"]:
            pred=predictions.loc[predictions.task.eq(task)&predictions.model.eq(model)]
            if pred.order_id.duplicated().any() or set(pred.order_id)!=set(rows.order_id):raise ValueError("OOF coverage")
            if set(pred.partition)!={"development_oof"}:raise ValueError("Invalid OOF partition")
            aligned=rows[["order_id",TARGETS[task],"validation_fold"]].merge(pred,on="order_id",validate="one_to_one",suffixes=("_source","_output"))
            np.testing.assert_array_equal(aligned.validation_fold_source,aligned.validation_fold_output)
            np.testing.assert_allclose(aligned[TARGETS[task]],aligned.target,rtol=0,atol=1e-12)
            calculated=metrics(task,aligned.target,aligned.prediction)
            saved=pooled.loc[pooled.task.eq(task)&pooled.model.eq(model)].iloc[0]
            for key,value in calculated.items():
                if value is not None and not isinstance(value,bool):np.testing.assert_allclose(saved[key],value,rtol=1e-10,atol=1e-10)
            for fold,train,val in fold_indices(rows):
                evidence=[f for f in fits if f["task"]==task and f["model"]==model and f["fold"]==fold]
                if len(evidence)!=1:raise ValueError("Missing/duplicate fit evidence")
                evidence=evidence[0]
                if evidence["train_order_ids_sha256"]!=ids_digest(rows.iloc[train].order_id):raise ValueError("Training lineage mismatch")
                if evidence["validation_order_ids_sha256"]!=ids_digest(rows.iloc[val].order_id):raise ValueError("Validation lineage mismatch")
                subset=pred.loc[pred.validation_fold.eq(fold)]
                calc=metrics(task,subset.target,subset.prediction)
                savedfold=fold_metrics.loc[fold_metrics.task.eq(task)&fold_metrics.model.eq(model)&fold_metrics.fold.eq(fold)&fold_metrics.partition.eq("validation")]
                if len(savedfold)!=1:raise ValueError("Missing/duplicate fold metrics")
                for key,value in calc.items():
                    if value is not None and not isinstance(value,bool):np.testing.assert_allclose(savedfold.iloc[0][key],value,rtol=1e-10,atol=1e-10)
                checked+=1
    suite=unittest.defaultTestLoader.discover(str(root/"src/models/tests"))
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():raise ValueError("Model-contract fixtures failed")
    report={"status":"passed_internal_verification", "fold_model_records":checked,"unit_tests":result.testsRun,
            "output_files_checked":len(manifest["output_hashes"]),"holdout_evaluated":False,
            "independent_agent_review":"pending", "team_explanation_review":"pending"}
    print(json.dumps(report,indent=2));return report


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id",default="stage3-baseline-v1")
    args=parser.parse_args()
    if Path(args.run_id).name!=args.run_id:raise ValueError("Invalid run ID")
    verify(ROOT/"artifacts/metrics"/args.run_id)
