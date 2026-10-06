"""Bounded Stage 4 search/selection. All fits and decisions are development only."""
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
from sklearn.exceptions import ConvergenceWarning

from src.common.loaders import sha256_file
from src.features.contract import PREDICTOR_ALLOWLIST, FEATURE_VERSION, CONTRACT_VERSION, SPLIT_VERSION
from .data import ROOT, TARGETS, load_development, task_rows, fold_indices
from .evaluate import metrics
from .io import ids_digest, write_csv_lf, write_json
from .stage4_checkpoint import stage4_identity as identity, ensure_baseline
from .pipelines import positive_probability
from .policy import select_cost_threshold, apply_threshold, threshold_curve
from .train import conditioning, _plots_and_tables
from .tuned_pipelines import make_tuned_pipeline, tuned_state, tuned_encoding

CONFIG = Path(__file__).parent / "configs/stage4_search.json"
BLOCKS = {
    "basket": ["n_items", "has_items", "n_products", "n_sellers", "n_categories"],
    "financial": ["total_price", "total_freight", "freight_ratio", "freight_ratio_missing"],
    "physical": ["total_weight_g", "total_volume_cm3", "weight_missing_fraction", "volume_missing_fraction"],
    "category": ["primary_category", "category_missing_fraction"],
    "states": ["customer_state", "primary_seller_state", "interstate_share"],
    "distance": ["distance_km_max", "distance_missing_fraction"],
    "calendar": ["purchase_month", "purchase_dayofweek", "purchase_hour"],
    "payment": ["primary_payment_type", "payment_installments_max", "n_payment_methods", "payment_missing"],
}


def predict(task, pipe, X):
    return pipe.predict(X) if task == "regression" else positive_probability(pipe, X)


def choose_candidate(summary, task, config):
    metric = config["primary_metrics"][task] + "_mean"
    part = summary.loc[summary.task.eq(task) & ~summary.family.eq("dummy")].copy()
    if part.empty or not np.isfinite(part[metric]).all():
        raise ValueError("Cannot select from missing/invalid scores")
    best = part[metric].min() if task == "regression" else part[metric].max()
    gap = part[metric] - best if task == "regression" else best - part[metric]
    eligible = part.loc[gap <= config["selection_tolerance"][task] + 1e-12].copy()
    eligible["preference"] = eligible.family.map({v:i for i,v in enumerate(config["family_preference"])})
    if eligible.preference.isna().any():
        raise ValueError("Unranked family")
    return eligible.sort_values(["preference", metric, "candidate"],
             ascending=[True, task == "regression", True]).iloc[0].candidate


def summarize(folds):
    columns = [c for c in ["mae", "rmse", "r2", "average_precision", "roc_auc", "brier", "accuracy"] if c in folds]
    val = folds.loc[folds.partition.eq("validation")]
    table = val.groupby(["task", "candidate", "family"])[columns].agg(["mean", "std"])
    table.columns = [f"{name}_{stat}" for name,stat in table.columns]
    result = table.reset_index()
    seconds = val.groupby(["task", "candidate"]).fit_seconds.sum().rename("total_fit_seconds").reset_index()
    return result.merge(seconds, on=["task", "candidate"], validate="one_to_one")


class Budget:
    def __init__(self, config):
        self.config, self.start, self.count = config, time.monotonic(), 0

    def fit(self, pipe, X, y):
        if self.count >= self.config["max_fits"] or time.monotonic()-self.start >= self.config["max_wall_seconds"]:
            raise RuntimeError("Predeclared fit/time budget exhausted; no complete run published")
        self.count += 1
        start = time.perf_counter()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            pipe.fit(X, y)
        if any(issubclass(w.category, ConvergenceWarning) for w in caught):
            raise RuntimeError("Unconverged candidate; no complete run published")
        return time.perf_counter()-start, [{"category":w.category.__name__, "message":str(w.message)} for w in caught]


def permutation_blocks(task, pipe, X, y, ids, fold, config):
    rng = np.random.default_rng(config["seed"] + fold)
    indices = np.sort(rng.choice(len(X), min(len(X),config["permutation_sample_per_fold"]), replace=False))
    sample = X.iloc[indices].copy().reset_index(drop=True)
    truth = np.asarray(y)[indices]
    metric = config["primary_metrics"][task]
    baseline = metrics(task, truth, predict(task,pipe,sample))[metric]
    evidence = []
    for block, columns in BLOCKS.items():
        for repeat in range(config["permutation_repeats"]):
            shuffled = sample.copy()
            ordering = rng.permutation(len(sample))
            shuffled.loc[:,columns] = sample.iloc[ordering][columns].to_numpy()
            changed = metrics(task, truth, predict(task,pipe,shuffled))[metric]
            degradation = changed-baseline if task=="regression" else baseline-changed
            evidence.append({"task":task,"fold":fold,"block":block,"repeat":repeat,"n":len(sample),
                "sample_order_ids_sha256":ids_digest(np.asarray(ids)[indices]),"primary_metric":metric,
                "unpermuted_score":baseline,"permuted_score":changed,"degradation":degradation})
    return evidence


def paired_differences(folds, config):
    result=[]
    val=folds.loc[folds.partition.eq("validation")]
    for task in TARGETS:
        metric=config["primary_metrics"][task]
        pivot=val.loc[val.task.eq(task)].pivot(index="fold",columns="candidate",values=metric)
        for candidate in pivot.columns:
            for reference in ["baseline_linear","baseline_tree"]:
                if candidate==reference:continue
                for fold in pivot.index:
                    delta=pivot.loc[fold,candidate]-pivot.loc[fold,reference]
                    result.append({"task":task,"candidate":candidate,"reference":reference,"fold":fold,
                        "metric":metric,"candidate_minus_reference":delta,
                        "improvement":-delta if task=="regression" else delta})
    return pd.DataFrame(result)


def run(root=ROOT, run_id="stage4-selection-v1", config_path=CONFIG, rebuild_baseline=False):
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}",run_id):raise ValueError("Unsafe run ID")
    config=json.loads(Path(config_path).read_text())
    if config["stage"]!=4 or config["holdout_evaluation"] is not False or config["folds"]!=5 or config["n_jobs"]!=1:
        raise ValueError("Invalid Stage 4 boundaries")
    expected=sum(len(config[f"{task}_candidates"])*5 for task in TARGETS)+25
    if expected!=config["max_fits"]:raise ValueError("Configuration fit budget mismatch")
    source=root/"artifacts/metrics"/config["stage3_run_id"]
    ensure_baseline(source, root, rebuild=rebuild_baseline)
    prior_manifest=json.loads((source/"run_manifest.json").read_text())
    if prior_manifest["stage"]!=3 or prior_manifest["holdout_evaluated"] is not False:raise ValueError("Invalid baseline source")
    for name,digest in prior_manifest["output_hashes"].items():
        if sha256_file(source/name)!=digest:raise ValueError("Baseline artifact changed")
    base_config=json.loads((source/"configuration.json").read_text())
    if base_config["seed"]!=config["seed"]:raise ValueError("Baseline seed mismatch")
    development,cv,hashes=load_development(root)
    if hashes!=prior_manifest["input_hashes"]:raise ValueError("Frozen data changed since approved baseline")
    code=identity(root);started=datetime.now(timezone.utc).isoformat();budget=Budget(config)
    parent=root/"artifacts/metrics";target=parent/run_id
    if target.exists():raise FileExistsError("Existing run cannot be overwritten")
    baseline_folds=pd.read_csv(source/"fold_metrics.csv")
    baseline_predictions=pd.read_csv(source/"oof_predictions.csv",dtype={"order_id":"string"})
    candidates={};all_folds=[];all_predictions=[];fits=[];coefficients=[]
    with tempfile.TemporaryDirectory(prefix=".stage4-",dir=parent) as temp:
        out=Path(temp);(out/"cv_models").mkdir();(out/"diagnostics").mkdir()
        write_json(config,out/"configuration.json")
        for task in TARGETS:
            rows=task_rows(development,cv,task);X=rows[PREDICTOR_ALLOWLIST];y=rows[TARGETS[task]].to_numpy()
            candidates[task]={}
            for model in ["dummy","linear","tree"]:
                candidate={"id":f"baseline_{model}","family":model,"params":{},"baseline_model":model}
                candidates[task][candidate["id"]]=candidate
                old=baseline_folds.loc[baseline_folds.task.eq(task)&baseline_folds.model.eq(model)].copy()
                old["candidate"]=candidate["id"];old["family"]=model;old["source"]="reused_approved_stage3"
                all_folds.append(old.drop(columns="model"))
                pred=baseline_predictions.loc[baseline_predictions.task.eq(task)&baseline_predictions.model.eq(model)].copy()
                pred["candidate"]=candidate["id"]
                all_predictions.append(pred.drop(columns="model"))
            for candidate in config[f"{task}_candidates"]:
                candidates[task][candidate["id"]]=candidate
                for fold,tr,va in fold_indices(rows):
                    print(f"search {task}/{candidate['id']}/fold {fold}",flush=True)
                    pipe=make_tuned_pipeline(task,candidate,base_config)
                    seconds,caught=budget.fit(pipe,X.iloc[tr],y[tr])
                    scores=predict(task,pipe,X.iloc[va]);train_scores=predict(task,pipe,X.iloc[tr])
                    common={"task":task,"candidate":candidate["id"],"family":candidate["family"],"fold":fold,
                            "fit_seconds":seconds,"training_n":len(tr),"validation_n":len(va),"source":"stage4_search"}
                    for partition,truth,values in [("training_resubstitution",y[tr],train_scores),("validation",y[va],scores)]:
                        all_folds.append(pd.DataFrame([{**common,"partition":partition,**metrics(task,truth,values)}]))
                    all_predictions.append(pd.DataFrame({"order_id":rows.iloc[va].order_id.to_numpy(),"task":task,
                        "candidate":candidate["id"],"partition":"development_oof","validation_fold":fold,"target":y[va],"prediction":scores}))
                    state=tuned_state(pipe,X.iloc[tr]);est=pipe.named_steps["model"]
                    record={**common,"phase":"search","train_order_ids_sha256":ids_digest(rows.iloc[tr].order_id),
                        "validation_order_ids_sha256":ids_digest(rows.iloc[va].order_id),"warnings":caught,
                        "validation_encoding":tuned_encoding(pipe,X.iloc[va]),**state}
                    if hasattr(est,"tree_"):record.update(tree_depth=est.get_depth(),tree_leaves=est.get_n_leaves(),criterion=est.criterion)
                    if candidate["family"]=="forest":
                        record.update(criterion=est.criterion,n_estimators=len(est.estimators_),bootstrap=est.bootstrap,
                            max_features=est.max_features,depths=[e.get_depth() for e in est.estimators_],
                            leaves=[e.get_n_leaves() for e in est.estimators_],n_jobs=est.n_jobs)
                    if hasattr(est,"coef_"):
                        names=state["transformed_feature_names"];values=np.ravel(est.coef_)
                        if len(names)!=len(values):raise ValueError("Coefficient alignment")
                        for name,value in zip(names,values):coefficients.append({"task":task,"candidate":candidate["id"],"fold":fold,
                            "feature":name,"coefficient":value,"odds_ratio":np.exp(value) if task=="classification" else None})
                        record["intercept"]=np.ravel(est.intercept_).tolist()
                        if fold==0:write_json(conditioning(pipe,X.iloc[tr]),out/"diagnostics"/f"{task}_{candidate['id']}_conditioning.json")
                    if candidate["family"]=="tree" and fold==0:
                        import matplotlib.pyplot as plt
                        from sklearn.tree import plot_tree
                        fig,ax=plt.subplots(figsize=(14,6))
                        plot_tree(est,max_depth=2,feature_names=state["transformed_feature_names"],filled=True,fontsize=6,ax=ax)
                        ax.set_title(f"{task}/{candidate['id']}: top levels; fitted depth {est.get_depth()}")
                        fig.tight_layout();fig.savefig(out/"diagnostics"/f"{task}_{candidate['id']}_top_levels.png",dpi=160);plt.close(fig)
                    fits.append(record)
        folds=pd.concat(all_folds,ignore_index=True);predictions=pd.concat(all_predictions,ignore_index=True)
        summary=summarize(folds);selections={task:choose_candidate(summary,task,config) for task in TARGETS}
        selected=[];permutations=[];sensitivities=[];sensitivity_predictions=[]
        for task in TARGETS:
            rows=task_rows(development,cv,task);X=rows[PREDICTOR_ALLOWLIST];y=rows[TARGETS[task]].to_numpy()
            candidate=candidates[task][selections[task]]
            expected_pred=predictions.loc[predictions.task.eq(task)&predictions.candidate.eq(candidate["id"])]
            if expected_pred.order_id.duplicated().any() or set(expected_pred.order_id)!=set(rows.order_id):raise ValueError("Selected OOF coverage")
            for fold,tr,va in fold_indices(rows):
                print(f"selected diagnostics {task}/{candidate['id']}/fold {fold}",flush=True)
                pipe=make_tuned_pipeline(task,candidate,base_config)
                seconds,caught=budget.fit(pipe,X.iloc[tr],y[tr]);scores=predict(task,pipe,X.iloc[va])
                expected=rows.iloc[va][["order_id"]].merge(expected_pred,on="order_id",validate="one_to_one")
                np.testing.assert_allclose(scores,expected.prediction,atol=1e-9,rtol=1e-9)
                state=tuned_state(pipe,X.iloc[tr])
                checkpoint=out/"cv_models"/f"{task}_selected_fold{fold}.joblib"
                joblib.dump(pipe,checkpoint);reloaded=predict(task,joblib.load(checkpoint),X.iloc[va])
                np.testing.assert_allclose(scores,reloaded,atol=1e-12,rtol=1e-12)
                fits.append({"task":task,"candidate":candidate["id"],"fold":fold,"phase":"selected_diagnostics",
                    "fit_seconds":seconds,"warnings":caught,"train_order_ids_sha256":ids_digest(rows.iloc[tr].order_id),
                    "validation_order_ids_sha256":ids_digest(rows.iloc[va].order_id),"checkpoint_sha256":sha256_file(checkpoint),
                    "reproduced_selected_oof_and_reload":"passed","validation_encoding":tuned_encoding(pipe,X.iloc[va]),**state})
                permutations.extend(permutation_blocks(task,pipe,X.iloc[va],y[va],rows.iloc[va].order_id.to_numpy(),fold,config))
                for variant in ["no_payment"]+(["item_bearing_only"] if task=="classification" else []):
                    str_idx,sva_idx=tr,va
                    if variant=="item_bearing_only":
                        str_idx=tr[rows.iloc[tr].n_items.to_numpy()>0]
                        sva_idx=va[rows.iloc[va].n_items.to_numpy()>0]
                    alternate=make_tuned_pipeline(task,candidate,base_config,"no_payment" if variant=="no_payment" else "full")
                    sec,warning=budget.fit(alternate,X.iloc[str_idx],y[str_idx])
                    changed=predict(task,alternate,X.iloc[sva_idx]);reference=predict(task,pipe,X.iloc[sva_idx])
                    for label,score in [("sensitivity",changed),("full_model_matched_validation",reference)]:
                        sensitivities.append({"task":task,"variant":variant,"model_scope":label,"candidate":candidate["id"],
                            "fold":fold,"training_n":len(str_idx) if label=="sensitivity" else len(tr),
                            "fit_seconds":sec if label=="sensitivity" else 0.,**metrics(task,y[sva_idx],score)})
                        sensitivity_predictions.append(pd.DataFrame({"order_id":rows.iloc[sva_idx].order_id.to_numpy(),"task":task,
                            "variant":variant,"model_scope":label,"validation_fold":fold,"target":y[sva_idx],"prediction":score}))
                    fits.append({"task":task,"candidate":candidate["id"],"fold":fold,"phase":"sensitivity","variant":variant,
                        "fit_seconds":sec,"warnings":warning,"train_order_ids_sha256":ids_digest(rows.iloc[str_idx].order_id),
                        "validation_order_ids_sha256":ids_digest(rows.iloc[sva_idx].order_id),
                        "validation_encoding":tuned_encoding(alternate,X.iloc[sva_idx]),**tuned_state(alternate,X.iloc[str_idx])})
            selected.append(expected_pred)
            # Existing plot code expects model column; plots are selected-config OOF, not holdout.
            _plots_and_tables(task,rows,expected_pred.rename(columns={"candidate":"model"}),out/"diagnostics",base_config)
        chosen=pd.concat(selected,ignore_index=True)
        cls=chosen.loc[chosen.task.eq("classification")].sort_values("order_id")
        scenario=[]
        for ratio in config["cost_ratios"]:
            threshold,report=select_cost_threshold(cls.target,cls.prediction,ratio)
            scenario.append({"policy":"optimized_development_oof",**report})
            for name,cut in [("default_0.5",.5),("no_alert",np.nextafter(1.,np.inf)),("all_alert",0.)]:
                info=metrics("classification",cls.target,cls.prediction,cut)
                info.update(cost_ratio_fn_to_fp=ratio,illustrative_cost=info["fp"]+ratio*info["fn"],alerts=info["tp"]+info["fp"])
                scenario.append({"policy":name,**info})
        threshold,primary_report=select_cost_threshold(cls.target,cls.prediction,config["proposed_primary_cost_ratio"])
        policy={"kind":"fixed_threshold","positive_class":1,"comparison":">=","threshold":threshold,
            "cost_ratio_fn_to_fp":config["proposed_primary_cost_ratio"],"false_positive_cost":1,
            "cost_assumption":"illustrative, not measured Olist business cost",
            "team_policy_approval":"user delegated choice of sensible taught policy; illustrative 5:1 chosen",
            "threshold_selection_population":"selected development OOF; after tuning, not independent",
            "tie_break":config["threshold_tie_break"],"candidate":selections["classification"]}
        decisions=apply_threshold(cls.prediction,policy)
        write_json(policy,out/"decision_policy.json")
        if not np.array_equal(decisions,apply_threshold(cls.prediction,json.loads((out/"decision_policy.json").read_text()))):raise ValueError("Policy reload mismatch")
        cls=cls.copy();cls["policy_decision"]=decisions;cls["policy_threshold"]=threshold
        write_csv_lf(cls,out/"selected_classification_policy_predictions.csv")
        record={"stage":4,"frozen_at_utc":datetime.now(timezone.utc).isoformat(),"holdout_evaluated":False,
            "feature_version":FEATURE_VERSION,"contract_version":CONTRACT_VERSION,"split_version":SPLIT_VERSION,
            "features":PREDICTOR_ALLOWLIST,"positive_class":1,"selection_rule":{
                "primary_metrics":config["primary_metrics"],"practical_tolerance":config["selection_tolerance"],
                "family_preference":config["family_preference"],"tie_break":"best score then lexical ID"},
            "tasks":{task:{"candidate":candidates[task][selections[task]],"cv_selection_summary":
                summary.loc[summary.task.eq(task)&summary.candidate.eq(selections[task])].iloc[0].to_dict()} for task in TARGETS},
            "input_hashes":hashes,"source_stage3_manifest_sha256":sha256_file(source/"run_manifest.json"),
            "config_sha256":sha256_file(config_path),"decision_policy_file":"decision_policy.json",
            "decision_policy_sha256":sha256_file(out/"decision_policy.json"),
            "policy_metrics":primary_report,"baseline_config":base_config,
            "independent_agent_review":"pending","team_explanation_review":"pending",
            "team_policy_approval":"user delegated choice of sensible taught policy; illustrative 5:1 chosen",
            "limitations":["CV scores and threshold performance are selected on development, not independent estimates",
                "mixed-time customer holdout does not estimate future drift","snapshot availability remains unproven",
                "missing reviews are unknown; recorded negatives are not latent satisfaction",
                "sensitivity results do not silently change primary contract/cohort","no final-fit deployment model exists"],
            "optional_methods_deferred":config["optional_methods_deferred"]}
        write_json(record,out/"selection_record.json")
        write_csv_lf(folds,out/"fold_metrics.csv");write_csv_lf(summary,out/"cv_summary.csv")
        write_csv_lf(predictions.sort_values(["task","candidate","order_id"]),out/"candidate_oof_predictions.csv")
        write_csv_lf(chosen.sort_values(["task","order_id"]),out/"selected_oof_predictions.csv")
        write_csv_lf(paired_differences(folds,config),out/"paired_fold_differences.csv")
        pooled=[]
        for (task,candidate),part in predictions.groupby(["task","candidate"]):
            rows=task_rows(development,cv,task)
            if part.order_id.duplicated().any() or set(part.order_id)!=set(rows.order_id):raise ValueError("Candidate OOF coverage")
            pooled.append({"task":task,"candidate":candidate,"partition":"development_selection_oof",**metrics(task,part.target,part.prediction)})
        write_csv_lf(pd.DataFrame(pooled),out/"pooled_oof_metrics.csv")
        write_csv_lf(pd.DataFrame(coefficients),out/"linear_coefficients_by_name.csv")
        coefficient_table=pd.DataFrame(coefficients)
        stability=coefficient_table.groupby(["task","candidate","feature"]).coefficient.agg(
            folds_present="size",mean="mean",std="std",minimum="min",maximum="max",
            positive_folds=lambda x:int((x>0).sum()),negative_folds=lambda x:int((x<0).sum())).reset_index()
        write_csv_lf(stability,out/"coefficient_stability.csv")
        write_csv_lf(pd.DataFrame(permutations),out/"block_permutation_importance.csv")
        write_csv_lf(pd.DataFrame(sensitivities),out/"sensitivity_fold_metrics.csv")
        write_csv_lf(pd.concat(sensitivity_predictions),out/"sensitivity_oof_predictions.csv")
        write_csv_lf(pd.DataFrame(scenario),out/"threshold_scenarios.csv")
        curve=threshold_curve(cls.target,cls.prediction)
        for ratio in config["cost_ratios"]:curve[f"illustrative_cost_ratio_{ratio}"]=curve.fp+ratio*curve.fn
        write_csv_lf(curve,out/"threshold_curve.csv")
        import matplotlib.pyplot as plt
        from sklearn.metrics import precision_recall_curve
        precision,recall,cuts=precision_recall_curve(cls.target,cls.prediction)
        fig,axes=plt.subplots(1,2,figsize=(11,4))
        axes[0].plot(recall,precision);axes[0].axhline(cls.target.mean(),color="grey",ls="--")
        axes[0].scatter(primary_report["recall_1"],primary_report["precision_1"],label="Illustrative 5:1 choice")
        axes[0].set(xlabel="Recall of recorded-negative reviews",ylabel="Precision",title="Selected development OOF PR");axes[0].legend()
        attainable=curve.loc[curve.threshold<=1]
        for ratio in config["cost_ratios"]:axes[1].plot(attainable.threshold,attainable[f"illustrative_cost_ratio_{ratio}"]/len(cls),label=f"FN:FP {ratio}:1")
        axes[1].axvline(threshold,color="black",ls="--");axes[1].set(xlabel="Probability threshold",ylabel="Illustrative cost per reviewed order",title="Development-selected; not intervention savings")
        axes[1].legend();fig.tight_layout();fig.savefig(out/"diagnostics"/"classification_policy_tradeoffs.png",dpi=150);plt.close(fig)
        write_json(fits,out/"fit_evidence.json")
        for filename,digest in hashes.items():
            if sha256_file(root/"data/business/ml"/filename)!=digest:raise ValueError("Frozen data changed during run")
        if identity(root)["code_identity_sha256"]!=code["code_identity_sha256"]:raise ValueError("Implementation/documents changed during run")
        if budget.count!=config["max_fits"]:raise ValueError("Not all predeclared fits completed")
        files={str(p.relative_to(out)):sha256_file(p) for p in out.rglob("*") if p.is_file()}
        manifest={"stage":4,"run_id":run_id,"status":"completed_internal_checks_pending_independent_and_team_review",
            "started_at_utc":started,"completed_at_utc":datetime.now(timezone.utc).isoformat(),"holdout_evaluated":False,
            "fit_count":budget.count,"wall_seconds":time.monotonic()-budget.start,"config_sha256":sha256_file(config_path),
            "input_hashes":hashes,"code_identity":code,"source_stage3_manifest_sha256":sha256_file(source/"run_manifest.json"),
            "selection_record_sha256":sha256_file(out/"selection_record.json"),"checkpoint_policy":"diagnostic fold models, not final-fit bundles",
            "command":f"python -m src.models.stage4 --run-id {run_id} --config {config_path.relative_to(root) if Path(config_path).is_relative_to(root) else config_path}",
            "environment":{p:importlib.metadata.version(p) for p in ["pandas","numpy","scikit-learn","scipy","joblib","matplotlib"]},
            "teaching_addenda":prior_manifest["teaching_addenda"],"output_hashes":files}
        write_json(manifest,out/"run_manifest.json");os.rename(out,target)
    print(f"Published {target}; selected {selections}; holdout untouched",flush=True)
    return target


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id",default="stage4-selection-v1")
    parser.add_argument("--config",type=Path,default=CONFIG)
    parser.add_argument("--rebuild-baseline", action="store_true",
                        help="Explicitly preserve and rebuild missing Stage 3 intermediates from compact evidence")
    args=parser.parse_args();run(run_id=args.run_id,config_path=args.config,rebuild_baseline=args.rebuild_baseline)
