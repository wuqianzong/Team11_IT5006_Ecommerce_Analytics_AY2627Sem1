"""Stage 3: fixed baseline CV, development audits and provenance; never holdout scoring.

Run: python -m src.models.train --run-id stage3-baseline-v1
Existing run directories are immutable. Use a new ID for an approved rerun.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import re
import tempfile
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from scipy import sparse, stats
from sklearn.exceptions import ConvergenceWarning

from src.common.loaders import sha256_file
from src.features.contract import PREDICTOR_ALLOWLIST, NUMERIC_COLUMNS, FEATURE_VERSION, CONTRACT_VERSION, SPLIT_VERSION
from .audit import run_audits, feature_summary
from .data import ROOT, TARGETS, load_development, task_rows, fold_indices
from .evaluate import metrics, capacity_metrics
from .io import write_csv_lf, write_json, identity, ids_digest
from .pipelines import make_pipeline, positive_probability, encoding_audit

DEFAULT_CONFIG = Path(__file__).resolve().parent / "configs/stage3_baseline.json"


def validate_config(config):
    if config["tasks"] != ["regression", "classification"] or config["models"] != ["dummy", "linear", "tree"]:
        raise ValueError("Stage 3 requires the frozen three baselines and both tasks")
    if config["holdout_evaluation"] is not False or config["logistic"]["class_weight"] is not None:
        raise ValueError("Stage 3 forbids holdout evaluation/automatic weighting")
    if config["logistic"]["C"] != "infinity":
        raise ValueError("Use the unpenalized initial logistic baseline; regularization is Stage 4")
    if config["classification_diagnostic_threshold"] != .5 or not 0 < config["diagnostic_review_capacity"] <= 1:
        raise ValueError("Invalid diagnostic operating convention")


def transformed_evidence(pipeline, X):
    transformed = pipeline[:-1].transform(X)
    names = pipeline[:-1].get_feature_names_out()
    if len(names) != transformed.shape[1]:
        raise ValueError("Transformed names/dimensions misaligned")
    values = transformed.data if sparse.issparse(transformed) else transformed
    if not np.isfinite(values).all():
        raise ValueError("Nonfinite transformed input")
    numeric = pipeline.named_steps["preprocess"].named_transformers_["numeric"]
    result = {"transformed_feature_names": names.tolist(), "dimension":len(names),
              "sparse":sparse.issparse(transformed),
              "imputer_statistics":dict(zip(NUMERIC_COLUMNS,numeric.named_steps["impute"].statistics_)),
              "training_encoding":encoding_audit(pipeline,X)}
    if "scale" in numeric.named_steps:
        result["scaler_mean"] = numeric.named_steps["scale"].mean_.tolist()
        result["scaler_scale"] = numeric.named_steps["scale"].scale_.tolist()
    return result


def conditioning(pipeline, X):
    # Deterministic training-only sample; direct SVD avoids squaring condition
    # numbers via X.T @ X. It is a diagnostic, not a full-population rank proof.
    idx = np.linspace(0,len(X)-1,min(5000,len(X)),dtype=int)
    z = pipeline[:-1].transform(X.iloc[idx])
    estimate = z.shape[0] * (z.shape[1]+1) * 8
    if estimate > 64 * 1024**2:
        raise ValueError("Conditioning diagnostic exceeds 64 MiB dense allocation budget")
    z = z.toarray() if sparse.issparse(z) else z
    z = np.column_stack([np.ones(len(z)),z])
    singular = np.linalg.svd(z,compute_uv=False)
    tolerance = max(z.shape)*np.finfo(float).eps*singular[0]
    rank = int((singular>tolerance).sum())
    nonzero = singular[singular>tolerance]
    return {"sample_training_n":len(z),"columns_with_intercept":z.shape[1],"numerical_rank":rank,
            "rank_tolerance":tolerance,"rank_deficient":rank<z.shape[1],
            "condition_number":None if rank<z.shape[1] else singular[0]/singular[-1],
            "nonzero_subspace_condition_number":nonzero[0]/nonzero[-1],
            "constant_columns":np.flatnonzero(np.ptp(z,axis=0)==0).tolist(),
            "dense_bytes":estimate,"sample_policy":"up to 5000 evenly spaced sorted training orders",
            "limitation":"sample rank/conditioning only; no OLS inference or full-matrix rank claim"}


def _plots_and_tables(task, rows, predictions, out, config):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    subgroup_rows=[]
    for model, pred in predictions.groupby("model"):
        aligned = rows.merge(pred[["order_id","prediction"]],on="order_id",validate="one_to_one")
        y, score = aligned[TARGETS[task]],aligned.prediction
        if task=="regression":
            residual=y-score
            fig, axes=plt.subplots(1,3,figsize=(12,3.5))
            axes[0].hexbin(score,residual,gridsize=50,mincnt=1,bins="log")
            axes[0].axhline(0,color="black",lw=.7)
            axes[0].set(xlabel="OOF predicted days",ylabel="Observed minus predicted (days)")
            axes[1].hist(residual,bins=70);axes[1].set(xlabel="OOF residual (days)",ylabel="Orders")
            stats.probplot(residual,dist="norm",plot=axes[2]);axes[2].set(title="Normal Q–Q (diagnostic)",ylabel="Ordered residual days")
            fig.suptitle(f"Development regression: {model}; no clipping")
            fig.tight_layout();fig.savefig(out/f"regression_{model}_residuals.png",dpi=150);plt.close(fig)
        else:
            bins=pd.cut(score,np.linspace(0,1,11),include_lowest=True)
            reliability=pd.DataFrame({"bin":bins,"y":y,"p":score}).groupby("bin",observed=True).agg(
                n=("y","size"),positives=("y","sum"),mean_probability=("p","mean"),observed_rate=("y","mean")).reset_index()
            reliability["bin"]=reliability.bin.astype(str)
            write_csv_lf(reliability,out/f"classification_{model}_reliability.csv")
            fig,ax=plt.subplots(figsize=(4.5,4))
            ax.plot([0,1],[0,1],color="gray",ls="--")
            ax.plot(reliability.mean_probability,reliability.observed_rate,marker="o")
            ax.set(xlabel="Mean OOF probability",ylabel="Observed negative-review rate",title=f"Development {model}: reliability",xlim=(0,1),ylim=(0,1))
            fig.tight_layout();fig.savefig(out/f"classification_{model}_reliability.png",dpi=150);plt.close(fig)
        aligned["basket_size"]=pd.cut(aligned.n_items,[-1,0,1,3,np.inf],labels=["0","1","2–3","4+"]).astype("string")
        for feature in config["subgroups"]:
            for group, subset in aligned.groupby(feature,dropna=False,observed=True):
                values=metrics(task,subset[TARGETS[task]],subset.prediction)
                subgroup_rows.append({"task":task,"model":model,"feature":feature,"group":str(group),**values})
    write_csv_lf(pd.DataFrame(subgroup_rows),out/f"{task}_subgroup_metrics.csv")


def run(root=ROOT, run_id="stage3-baseline-v1", config_path=DEFAULT_CONFIG):
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}",run_id):
        raise ValueError("Unsafe run ID")
    config=json.loads(Path(config_path).read_text());validate_config(config)
    parent=root/"artifacts/metrics";parent.mkdir(parents=True,exist_ok=True)
    target=parent/run_id
    if target.exists():
        raise FileExistsError(f"Run already exists, never overwrite: {target}")
    started=datetime.now(timezone.utc).isoformat();code=identity(root)
    development,cv,hashes=load_development(root)
    # A disposable new-run workspace is published only after all checks succeed.
    with tempfile.TemporaryDirectory(prefix=".stage3-",dir=parent) as temp:
        out=Path(temp); (out/"cv_models").mkdir();(out/"diagnostics").mkdir()
        write_json(config,out/"configuration.json")
        audit=run_audits(root,development,cv,out/"eda")
        fold_results=[];pooled_results=[];all_predictions=[];coefficients=[];fit_evidence=[]
        for task in config["tasks"]:
            rows=task_rows(development,cv,task)
            X=rows[PREDICTOR_ALLOWLIST];y=rows[TARGETS[task]].to_numpy()
            if task=="classification":y=y.astype(int)
            task_predictions=[]
            for model in config["models"]:
                for fold,train,val in fold_indices(rows):
                    print(f"{task}/{model}/fold {fold}: fit {len(train)}; validate {len(val)}",flush=True)
                    pipeline=make_pipeline(task,model,config)
                    before=time.perf_counter()
                    with warnings.catch_warnings(record=True) as caught:
                        warnings.simplefilter("always")
                        pipeline.fit(X.iloc[train],y[train])
                        fit_seconds=time.perf_counter()-before
                        score=pipeline.predict(X.iloc[val]) if task=="regression" else positive_probability(pipeline,X.iloc[val])
                        train_score=pipeline.predict(X.iloc[train]) if task=="regression" else positive_probability(pipeline,X.iloc[train])
                    warnings_saved=[{"category":w.category.__name__,"message":str(w.message)} for w in caught]
                    if any(issubclass(w.category,ConvergenceWarning) for w in caught):
                        raise RuntimeError(f"Unconverged {task}/{model}/{fold}; record and fix before publication")
                    result={"task":task,"model":model,"fold":fold,"fit_seconds":fit_seconds,
                            "training_n":len(train),"validation_n":len(val),"training_groups":rows.iloc[train].customer_unique_id.nunique(),
                            "validation_groups":rows.iloc[val].customer_unique_id.nunique()}
                    for partition,truth,pred in [("training_resubstitution",y[train],train_score),("validation",y[val],score)]:
                        values=metrics(task,truth,pred,config["classification_diagnostic_threshold"])
                        fold_results.append({**result,"partition":partition,**values})
                    pred=pd.DataFrame({"order_id":rows.iloc[val].order_id.to_numpy(),"task":task,"model":model,
                                       "partition":"development_oof","validation_fold":fold,"target":y[val],"prediction":score})
                    task_predictions.append(pred)
                    state=transformed_evidence(pipeline,X.iloc[train])
                    record={**result,"train_order_ids_sha256":ids_digest(rows.iloc[train].order_id),
                            "validation_order_ids_sha256":ids_digest(rows.iloc[val].order_id),"warnings":warnings_saved,
                            "validation_encoding":encoding_audit(pipeline,X.iloc[val]),**state}
                    estimator=pipeline.named_steps["model"]
                    if model=="tree":
                        record.update(tree_depth=estimator.get_depth(),tree_leaves=estimator.get_n_leaves(),criterion=estimator.criterion)
                    if model=="linear":
                        coefs=np.ravel(estimator.coef_)
                        if len(coefs)!=len(state["transformed_feature_names"]):raise ValueError("Coefficient-name alignment")
                        coefficients.extend({"task":task,"fold":fold,"feature":name,"coefficient":float(coef)} for name,coef in zip(state["transformed_feature_names"],coefs))
                        record["intercept"]=np.ravel(estimator.intercept_).tolist()
                        if fold==0:write_json(conditioning(pipeline,X.iloc[train]),out/"diagnostics"/f"{task}_linear_conditioning.json")
                    checkpoint=out/"cv_models"/f"{task}_{model}_fold{fold}.joblib"
                    joblib.dump(pipeline,checkpoint)
                    loaded=joblib.load(checkpoint)
                    restored=loaded.predict(X.iloc[val]) if task=="regression" else positive_probability(loaded,X.iloc[val])
                    np.testing.assert_allclose(restored,score,atol=1e-12,rtol=1e-12)
                    if task=="classification":np.testing.assert_array_equal(restored>=.5,score>=.5)
                    record["reload_predictions_and_diagnostic_decisions"]="passed"
                    record["checkpoint_sha256"]=sha256_file(checkpoint)
                    fit_evidence.append(record)
                    if model=="tree" and fold==0:
                        import matplotlib.pyplot as plt
                        from sklearn.tree import plot_tree
                        fig,ax=plt.subplots(figsize=(14,6))
                        plot_tree(estimator,max_depth=2,feature_names=state["transformed_feature_names"],filled=True,fontsize=6,ax=ax)
                        ax.set_title(f"{task} baseline fold 0 tree: top levels only; fitted depth {estimator.get_depth()}")
                        fig.tight_layout();fig.savefig(out/"diagnostics"/f"{task}_tree_top_levels.png",dpi=180);plt.close(fig)
                model_predictions=pd.concat(task_predictions[-5:],ignore_index=True)
                if set(model_predictions.order_id)!=set(rows.order_id) or model_predictions.order_id.duplicated().any():
                    raise ValueError("OOF must cover every eligible development order once")
                values=metrics(task,model_predictions.target,model_predictions.prediction)
                if task=="classification":values.update(capacity_metrics(model_predictions.target,model_predictions.prediction,model_predictions.order_id,config["diagnostic_review_capacity"]))
                pooled_results.append({"task":task,"model":model,"partition":"development_oof",**values})
            predictions=pd.concat(task_predictions,ignore_index=True)
            _plots_and_tables(task,rows,predictions,out/"diagnostics",config)
            all_predictions.append(predictions)
        folds=pd.DataFrame(fold_results)
        write_csv_lf(folds,out/"fold_metrics.csv")
        write_csv_lf(pd.DataFrame(pooled_results),out/"pooled_oof_metrics.csv")
        write_csv_lf(pd.concat(all_predictions).sort_values(["task","model","order_id"]),out/"oof_predictions.csv")
        write_csv_lf(pd.DataFrame(coefficients),out/"linear_coefficients_by_name.csv")
        write_json(fit_evidence,out/"fit_evidence.json")
        val=folds.loc[folds.partition.eq("validation")]
        numeric_metrics=[c for c in ["mae","rmse","r2","average_precision","roc_auc","brier","precision_1","recall_1","f1_1","accuracy"] if c in val]
        summary=val.groupby(["task","model"])[numeric_metrics].agg(["mean","std"])
        summary.columns=[f"{a}_{b}" for a,b in summary.columns]
        write_csv_lf(summary.reset_index(),out/"cv_summary.csv")
        paired=[]
        for task in config["tasks"]:
            metric=config["primary_metrics"][task]
            pivot=val.loc[val.task.eq(task)].pivot(index="fold",columns="model",values=metric)
            for a,b in [("linear","dummy"),("tree","dummy"),("tree","linear")]:
                for fold in pivot.index:paired.append({"task":task,"metric":metric,"candidate":a,"reference":b,"fold":fold,
                                                     "candidate_minus_reference":pivot.loc[fold,a]-pivot.loc[fold,b],
                                                     "improvement":(pivot.loc[fold,b]-pivot.loc[fold,a]) if task=="regression" else (pivot.loc[fold,a]-pivot.loc[fold,b])})
        write_csv_lf(pd.DataFrame(paired),out/"paired_fold_differences.csv")
        # Confirm sources and fixed artifacts were not changed during this run.
        for filename,digest in hashes.items():
            if sha256_file(root/"data/business/ml"/filename)!=digest:raise ValueError("Input artifact changed during run")
        if identity(root)["code_identity_sha256"]!=code["code_identity_sha256"]:raise ValueError("Implementation changed during run")
        files={str(p.relative_to(out)):sha256_file(p) for p in out.rglob("*") if p.is_file()}
        manifest={"status":"completed_internal_checks_pending_independent_review","stage":3,"run_id":run_id,
                  "started_at_utc":started,"completed_at_utc":datetime.now(timezone.utc).isoformat(),
                  "feature_version":FEATURE_VERSION,"contract_version":CONTRACT_VERSION,"split_version":SPLIT_VERSION,
                  "teaching_addenda":["W6/W7-2026-10-04","C1-C5-TREE-2026-10-05","TA-M1-2026-10-05"],
                  "holdout_evaluated":False,"model_selection":"none","operational_threshold":"not selected",
                  "checkpoint_policy":"fold-training diagnostic pipelines, not final deployment artifacts",
                  "command":f"python -m src.models.train --run-id {run_id}","config_sha256":sha256_file(config_path),
                  "input_hashes":hashes,"code_identity":code,"development_order_ids_sha256":ids_digest(development.order_id),
                  "environment":{p:importlib.metadata.version(p) for p in ["pandas","numpy","scikit-learn","scipy","matplotlib","joblib"]},
                  "audit_counts":audit["tasks"],"output_hashes":files}
        write_json(manifest,out/"run_manifest.json")
        os.rename(out,target)
        # TemporaryDirectory cleanup sees an absent old path, never deletes target.
    print(f"Published new development-only run: {target}",flush=True)
    return target


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id",default="stage3-baseline-v1")
    parser.add_argument("--config",type=Path,default=DEFAULT_CONFIG)
    args=parser.parse_args();run(run_id=args.run_id,config_path=args.config)


if __name__=="__main__":main()
