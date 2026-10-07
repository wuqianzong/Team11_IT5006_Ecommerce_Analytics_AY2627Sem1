"""Stage 5: frozen final fits, one protected holdout evaluation and local bundles."""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import time
import warnings
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import roc_curve, precision_recall_curve

from src.common.loaders import sha256_file
from src.features.contract import PREDICTOR_ALLOWLIST, NUMERIC_COLUMNS, CATEGORICAL_COLUMNS
from .data import ROOT, TARGETS, load_development, task_rows
from .evaluate import metrics
from .io import write_json, write_csv_lf, ids_digest
from .stage5_identity import identity as phase_identity
from .reproduction import reserve, update, MODE
from .pipelines import normalize_inputs, positive_probability
from .tuned_pipelines import make_tuned_pipeline, tuned_state, tuned_encoding
from .tutorial8 import check_source


def feature_stats(frame, schema, input_digest):
    normalized, _ = normalize_inputs(frame)
    units = {c["name"]: c.get("unit", "count/code or dimensionless; see description") for c in schema["columns"]}
    result = {"population": "eligible development training only", "n": len(frame), "sd_ddof": 1,
              "source_dataset_sha256": input_digest, "training_order_ids_sha256": ids_digest(frame.order_id),
              "numeric": {}, "categorical": {}}
    for col in NUMERIC_COLUMNS:
        values = normalized[col].dropna()
        result["numeric"][col] = {"unit": units[col], "denominator": len(frame), "observed_n": len(values),
            "missing_n": int(frame[col].isna().sum()), "mean": values.mean(), "sd": values.std(ddof=1),
            "minimum": values.min(), "q25": values.quantile(.25), "median": values.median(),
            "q75": values.quantile(.75), "maximum": values.max()}
    for col in CATEGORICAL_COLUMNS:
        result["categorical"][col] = {"unit": units[col], "denominator": len(frame),
            "raw_missing_n": int(frame[col].isna().sum()), "normalized_counts": normalized[col].value_counts().to_dict()}
    return result


def report_metrics(task, y, score, threshold=.5):
    y = np.asarray(y)
    if len(y) == 0:
        return {"n": 0, "unavailable_reason": "empty subgroup", "mae": None, "rmse": None, "r2": None,
                "average_precision": None, "roc_auc": None, "positives": 0 if task == "classification" else None,
                "negatives": 0 if task == "classification" else None, "precision_1": None, "recall_1": None,
                "f1_1": None, "brier": None, "threshold": threshold if task == "classification" else None}
    result = metrics(task, y, score, threshold)
    if task == "classification":
        if not result["precision_defined"]:
            result["precision_1"] = None
        result["alerts"] = result["tp"] + result["fp"]
        result["illustrative_cost_5_to_1"] = result["fp"] + 5 * result["fn"]
        result["alert_fraction"] = result["alerts"] / len(y)
        if not result["ranking_metrics_defined"]:
            result["ranking_unavailable_reason"] = "only one observed class"
        if not result["precision_defined"]:
            result["precision_unavailable_reason"] = "no predicted positives"
    return result


def per_class_report(y, probability, threshold):
    y = np.asarray(y).astype(int)
    pred = (np.asarray(probability) >= threshold).astype(int)
    records = []
    for label in [0, 1]:
        tp = int(((y == label) & (pred == label)).sum())
        actual, predicted = int((y == label).sum()), int((pred == label).sum())
        records.append({"class": label, "meaning": "recorded nonnegative review" if label == 0 else "recorded negative review",
            "support": actual, "predicted_n": predicted, "precision": tp / predicted if predicted else None,
            "recall": tp / actual if actual else None, "f1": 2 * tp / (actual + predicted) if actual + predicted else None,
            "threshold": threshold, "precision_unavailable_reason": None if predicted else "no predictions for class",
            "recall_unavailable_reason": None if actual else "no observed class"})
    return records


def basket_band(values):
    return pd.Series(np.select([values.eq(0), values.eq(1), values.between(2, 3)], ["0", "1", "2-3"], default="4+"), index=values.index)


def subgroup_tables(task, rows, score, threshold):
    records = []
    dimensions = {"customer_state": rows.customer_state.fillna("unknown"), "basket_size": basket_band(rows.n_items)}
    levels = {"customer_state": sorted(set(dimensions["customer_state"])), "basket_size": ["0", "1", "2-3", "4+"]}
    if task == "regression":
        dimensions["observed_duration_days"] = pd.cut(rows.lead_days, [0, 7, 14, 30, np.inf], labels=["0-7", "7-14", "14-30", "30+"], right=True).astype("string")
        levels["observed_duration_days"] = ["0-7", "7-14", "14-30", "30+"]
    for dimension, categories in dimensions.items():
        for label in levels[dimension]:
            mask = categories.eq(label).to_numpy(dtype=bool)
            values = report_metrics(task, rows.loc[mask, TARGETS[task]], np.asarray(score)[mask], threshold)
            records.append({"task": task, "dimension": dimension, "subgroup": str(label),
                            "small_support_flag": int(mask.sum()) < 100, **values})
    return records


def holdout_rows(root, development, expected_hashes):
    ml = root / "data/business/ml"
    if sha256_file(ml / "orders_ml_features.csv") != expected_hashes["orders_ml_features.csv"]:
        raise ValueError("Holdout source identity mismatch")
    base = pd.read_csv(ml / "orders_ml_features.csv", dtype={"order_id": "string", "customer_unique_id": "string"})
    splits = pd.read_csv(ml / "split_assignments.csv", dtype="string")
    selected_ids = splits.loc[splits.split_assignment.eq("holdout"), "order_id"]
    holdout = base.loc[base.order_id.isin(selected_ids)].sort_values("order_id").reset_index(drop=True)
    if holdout.order_id.duplicated().any() or set(holdout.order_id) != set(selected_ids):
        raise ValueError("Holdout coverage mismatch")
    if set(holdout.customer_unique_id) & set(development.customer_unique_id):
        raise ValueError("Outer customer overlap")
    return holdout


def evaluation_plots(out, task, y, score, threshold):
    y, score = np.asarray(y), np.asarray(score)
    if task == "regression":
        residual = y - score
        fig, axes = plt.subplots(2, 2, figsize=(10, 8))
        axes[0, 0].scatter(y, score, s=3, alpha=.12); axes[0, 0].plot([0, y.max()], [0, y.max()], "k--")
        axes[0, 0].set(xlabel="Observed lead days", ylabel="Predicted lead days")
        axes[0, 1].scatter(score, residual, s=3, alpha=.12); axes[0, 1].axhline(0, color="black", ls="--")
        axes[0, 1].set(xlabel="Predicted lead days", ylabel="Observed minus predicted (days)")
        axes[1, 0].hist(residual, bins=80); axes[1, 0].set(xlabel="Residual (days)", ylabel="Orders")
        stats.probplot(residual, dist="norm", plot=axes[1, 1])
        fig.suptitle("Frozen forest: final holdout regression diagnostics")
        fig.tight_layout(); fig.savefig(out / "regression_holdout_diagnostics.png", dpi=150); plt.close(fig)
    else:
        fpr, tpr, _ = roc_curve(y, score)
        precision, recall, _ = precision_recall_curve(y, score)
        fig, axes = plt.subplots(1, 3, figsize=(13, 4))
        axes[0].plot(fpr, tpr); axes[0].plot([0, 1], [0, 1], "k--")
        axes[0].set(xlabel="False positive rate", ylabel="Recall of recorded negatives", title="Final holdout ROC")
        axes[1].plot(recall, precision); axes[1].axhline(y.mean(), color="grey", ls="--")
        axes[1].set(xlabel="Recall of recorded negatives", ylabel="Precision", title="Final holdout PR")
        reliability = []
        bins = np.minimum((score * 10).astype(int), 9)
        for b in range(10):
            mask = bins == b
            reliability.append({"bin": b, "lower_inclusive": b / 10, "upper": (b + 1) / 10,
                "n": int(mask.sum()), "mean_probability": float(score[mask].mean()) if mask.any() else None,
                "observed_negative_fraction": float(y[mask].mean()) if mask.any() else None})
        table = pd.DataFrame(reliability)
        write_csv_lf(table, out / "classification_reliability.csv")
        axes[2].plot(table.mean_probability, table.observed_negative_fraction, "o-")
        axes[2].plot([0, 1], [0, 1], "k--"); axes[2].set(xlabel="Mean probability", ylabel="Observed fraction", title="Reliability (bin counts saved)")
        fig.tight_layout(); fig.savefig(out / "classification_holdout_curves.png", dpi=150); plt.close(fig)
        for tag, cut in [("default", .5), ("frozen_policy", threshold)]:
            m = report_metrics(task, y, score, cut)
            matrix = np.array([[m["tn"], m["fp"]], [m["fn"], m["tp"]]])
            normalized = matrix / matrix.sum(axis=1, keepdims=True)
            write_json({"label_order": [0, 1], "threshold": cut, "raw": matrix.tolist(),
                        "normalized_by_true_class": normalized.tolist()}, out / f"confusion_{tag}.json")
            fig, axes = plt.subplots(1, 2, figsize=(9, 4))
            for ax, values, title in zip(axes, [matrix, normalized], ["Counts", "True-class row fractions"]):
                ax.imshow(values, cmap="Blues")
                for i in range(2):
                    for j in range(2): ax.text(j, i, f"{values[i,j]:.3f}" if title != "Counts" else str(values[i,j]), ha="center", color="black", bbox={"facecolor": "white", "alpha": .7, "edgecolor": "none"})
                ax.set(xticks=[0, 1], yticks=[0, 1], xlabel="Predicted class", ylabel="Observed class", title=title)
            fig.suptitle(f"Final holdout {tag}: class 1 = recorded negative review")
            fig.tight_layout(); fig.savefig(out / f"confusion_{tag}.png", dpi=150); plt.close(fig)


def identity(root):
    return phase_identity(root, "final")


def _run(run_id="stage5-final-v1", diagnostic_id="stage5-tutorial8-v1", root=ROOT,
         replay=False, context=None):
    if Path(run_id).name != run_id or not run_id:
        raise ValueError("Unsafe run ID")
    source = root / "artifacts/metrics/stage4-selection-v1"
    selection, _ = check_source(source)
    development, cv, hashes = load_development(root)
    if hashes != selection["input_hashes"] or selection["features"] != PREDICTOR_ALLOWLIST:
        raise ValueError("Accepted freeze differs from inputs")
    diagnostic = root / "artifacts/metrics" / diagnostic_id
    dmanifest = json.loads((diagnostic / "run_manifest.json").read_text())
    if dmanifest["holdout_evaluated"] or dmanifest["fit_count"] != 10 or dmanifest["input_hashes"] != hashes or dmanifest["selection_sha256"] != sha256_file(source / "selection_record.json"):
        raise ValueError("Incomplete/unrelated pre-holdout diagnostics")
    for name, digest in dmanifest["output_hashes"].items():
        if sha256_file(diagnostic / name) != digest:
            raise ValueError("Diagnostic hash mismatch")
    diagnostic_verification = json.loads((root / "artifacts/metrics/stage5_tutorial8_internal_verification.json").read_text())
    if diagnostic_verification["status"] != "passed_internal_verification" or diagnostic_verification["holdout_evaluated"]:
        raise ValueError("Pre-holdout diagnostic verification required")
    if diagnostic_verification.get("run_manifest_sha256") != sha256_file(diagnostic / "run_manifest.json"):
        raise ValueError("Diagnostic verification report is not bound to this run")
    out = root / "artifacts/metrics" / run_id
    ledger = root / "artifacts/metrics/stage5_holdout_access.json"
    policy = json.loads((source / "decision_policy.json").read_text())
    if replay:
        context.update(reserve(root, run_id, selection, policy, hashes))
        ledger = context["path"]
    elif ledger.exists():
        raise ValueError("Holdout already reserved/evaluated. Verify/recover saved run; do not refit or retune.")
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    code = identity(root)
    schema = json.loads((root / "data/business/ml/feature_schema.json").read_text())
    policy = json.loads((source / "decision_policy.json").read_text())
    runtime = {name: importlib.metadata.version(name) for name in ["numpy", "pandas", "scikit-learn", "scipy", "joblib", "matplotlib"]}
    runtime["python"] = platform.python_version()
    pipes, bundles, fitting = {}, {}, []
    for task in TARGETS:
        rows = task_rows(development, cv, task)
        candidate = selection["tasks"][task]["candidate"]
        print(f"Final fit {task} n={len(rows)}", flush=True)
        pipe = make_tuned_pipeline(task, candidate, selection["baseline_config"])
        begin = time.monotonic()
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always"); pipe.fit(rows[PREDICTOR_ALLOWLIST], rows[TARGETS[task]])
        fit = {"task": task, "n": len(rows), "groups": rows.customer_unique_id.nunique(),
            "training_order_ids_sha256": ids_digest(rows.order_id), "training_group_ids_sha256": ids_digest(set(rows.customer_unique_id)),
            "seconds": time.monotonic() - begin, "warnings": [{"category": w.category.__name__, "message": str(w.message)} for w in caught]}
        fitting.append(fit)
        bundle = root / "artifacts/models" / task / run_id
        bundle.mkdir(parents=True, exist_ok=False)
        joblib.dump(pipe, bundle / "pipeline.joblib", compress=3)
        write_json(schema, bundle / "feature_schema.json")
        write_json(feature_stats(rows, schema, hashes["orders_ml_features.csv"]), bundle / "feature_stats.json")
        write_json({"candidate": candidate, "estimator_params": pipe.named_steps["model"].get_params(),
                    "baseline_preprocessing_configuration": selection["baseline_config"]}, bundle / "configuration.json")
        if task == "classification":
            write_json(policy, bundle / "decision_policy.json")
        metadata = {"task": task, "model_version": run_id, "target": TARGETS[task],
            "feature_version": selection["feature_version"], "contract_version": selection["contract_version"],
            "split_version": selection["split_version"], "training": fit, "input_hashes": hashes,
            "selection_sha256": sha256_file(source / "selection_record.json"), "positive_class": 1 if task == "classification" else None,
            "decision_policy_sha256": selection["decision_policy_sha256"] if task == "classification" else None,
            "environment": runtime, "code_identity_sha256": code["code_identity_sha256"], "seed": 42,
            "teaching_addenda": ["W6/W7-2026-10-04", "C1-C5-TREE-2026-10-05", "TA-M1-2026-10-05", "T8-2026-10-05"],
            "fitted_state": tuned_state(pipe, rows[PREDICTOR_ALLOWLIST]),
            "inference": "Original-unit 27 predictors; targets/status/eligibility not required; order_id alignment only",
            "limitations": selection["limitations"][:-1], "cohort": "eventually delivered, valid positive lead time" if task == "regression" else "reviewed orders with valid minimum-score binary label",
            "created_utc": datetime.now(timezone.utc).isoformat()}
        if replay:
            metadata.update(evaluation_mode=MODE, independent_test_estimate=False,
                            original_receipt_sha256=context["record"]["original_receipt_sha256"])
        write_json(metadata, bundle / "metadata.json")
        pipes[task], bundles[task] = pipe, bundle
    write_json(fitting, out / "final_fit_evidence.json")
    # Exclusive durable receipt BEFORE holdout outcomes are returned or scored.
    receipt = {"run_id": run_id, "state": "reserved_before_holdout_access", "created_utc": datetime.now(timezone.utc).isoformat(),
        "selection_sha256": sha256_file(source / "selection_record.json"), "input_hashes": hashes,
        "pipeline_hashes": {t: sha256_file(p / "pipeline.joblib") for t, p in bundles.items()}}
    if replay:
        update(context, state="reserved_before_holdout_access", pipeline_hashes=receipt["pipeline_hashes"])
        receipt = context["record"]
    else:
        with ledger.open("x", encoding="utf-8") as f:
            json.dump(receipt, f, indent=2, sort_keys=True); f.write("\n"); f.flush()
            __import__("os").fsync(f.fileno())
    holdout = holdout_rows(root, development, hashes)
    results, subgroup, classes = {}, [], []
    for task in TARGETS:
        rows = holdout.loc[holdout[f"eligible_{task}"].eq(1)].reset_index(drop=True)
        if rows[TARGETS[task]].isna().any(): raise ValueError("Missing eligible holdout target")
        if task == "classification" and set(rows.is_detractor) != {0, 1}: raise ValueError("Holdout lacks both classes")
        score = pipes[task].predict(rows[PREDICTOR_ALLOWLIST]) if task == "regression" else positive_probability(pipes[task], rows[PREDICTOR_ALLOWLIST])
        cut = policy["threshold"] if task == "classification" else .5
        pred = pd.DataFrame({"order_id": rows.order_id, "task": task, "target": rows[TARGETS[task]], "prediction": score})
        if task == "classification": pred["policy_decision"] = (score >= cut).astype(int)
        else: pred["residual_days"] = rows.lead_days - score
        write_csv_lf(pred, out / f"{task}_holdout_predictions.csv")
        result = {"task": task, "partition": "final protected holdout", "groups": rows.customer_unique_id.nunique(),
            "holdout_order_ids_sha256": ids_digest(rows.order_id), "metrics": report_metrics(task, rows[TARGETS[task]], score, cut)}
        if replay:
            result.update(partition="frozen holdout reproduction; not an independent test",
                          evaluation_mode=MODE, independent_test_estimate=False)
        if task == "classification":
            result["default_0_5_metrics"] = report_metrics(task, rows.is_detractor, score, .5)
            result["constant_score_ap_reference"] = float(rows.is_detractor.mean())
            result["illustrative_controls"] = {"no_alert_cost": int(5 * rows.is_detractor.sum()),
                "all_alert_cost": int((rows.is_detractor == 0).sum()), "assumption": "FP=1, FN=5; not measured costs or intervention benefits"}
            for tag, threshold in [("default_0_5", .5), ("frozen_policy", cut)]:
                classes.extend({"policy": tag, **row} for row in per_class_report(rows.is_detractor, score, threshold))
        result["holdout_encoding_quality"] = tuned_encoding(pipes[task], rows[PREDICTOR_ALLOWLIST])
        results[task] = result
        subgroup.extend(subgroup_tables(task, rows, score, cut))
        evaluation_plots(out, task, rows[TARGETS[task]], score, cut)
        metadata = json.loads((bundles[task] / "metadata.json").read_text())
        metadata["final_holdout_evaluation"] = result
        write_json(metadata, bundles[task] / "metadata.json")
        write_json({"task": task, "model_version": run_id,
            "output_hashes": {p.name: sha256_file(p) for p in bundles[task].iterdir() if p.is_file()}}, bundles[task] / "bundle_manifest.json")
    write_json(results, out / "holdout_metrics.json")
    write_csv_lf(pd.DataFrame(subgroup), out / "holdout_subgroups.csv")
    write_csv_lf(pd.DataFrame(classes), out / "classification_per_class_report.csv")
    for name, digest in hashes.items():
        if sha256_file(root / "data/business/ml" / name) != digest: raise ValueError("Input changed during final run")
    if identity(root)["code_identity_sha256"] != code["code_identity_sha256"]: raise ValueError("Source changed during final run")
    manifest = {"stage": 5, "holdout_evaluated": True, "run_id": run_id, "input_hashes": hashes, "code": code,
        "fit_count": 2, "wall_seconds": time.monotonic() - started, "environment": runtime,
        "selection_sha256": sha256_file(source / "selection_record.json"), "policy_sha256": sha256_file(source / "decision_policy.json"),
        "diagnostic_manifest_sha256": sha256_file(diagnostic / "run_manifest.json"),
        "bundle_manifest_sha256": {t: sha256_file(p / "bundle_manifest.json") for t, p in bundles.items()},
        "output_hashes": {p.name: sha256_file(p) for p in out.iterdir() if p.is_file()},
        "independent_review": "pending", "team_refinement": "pending"}
    if replay:
        manifest.update(evaluation_mode=MODE, independent_test_estimate=False,
                        original_receipt_sha256=context["record"]["original_receipt_sha256"],
                        reproduction_receipt_file=ledger.name)
    write_json(manifest, out / "run_manifest.json")
    receipt.update(state="evaluated_and_published", run_manifest_sha256=sha256_file(out / "run_manifest.json"))
    if replay:
        update(context, state="evaluated_and_published", run_manifest_sha256=receipt["run_manifest_sha256"])
    else:
        write_json(receipt, ledger)
    return out


def run(run_id="stage5-final-v1", diagnostic_id="stage5-tutorial8-v1", root=ROOT, replay=False):
    context = {}
    try:
        return _run(run_id, diagnostic_id, root, replay=replay, context=context)
    except Exception as error:
        if context:
            update(context, state="failed_during_reproduction", failure_type=type(error).__name__,
                   failure_message=str(error))
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="stage5-final-v1")
    parser.add_argument("--diagnostic-id", default="stage5-tutorial8-v1")
    parser.add_argument("--replay", action="store_true",
                        help="Explicit reproduction of the accepted previously evaluated holdout; preserve original receipt")
    args = parser.parse_args(); run(args.run_id, args.diagnostic_id, replay=args.replay)
