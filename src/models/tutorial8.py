"""Bounded pre-holdout development diagnostics. No holdout access or model selection."""
from __future__ import annotations

import argparse
import hashlib
import json
import time
import warnings
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve, precision_recall_curve
from sklearn.tree import export_text

from src.common.loaders import sha256_file
from src.features.contract import PREDICTOR_ALLOWLIST
from .data import ROOT, load_development, task_rows, fold_indices
from .evaluate import metrics
from .io import write_json, write_csv_lf, ids_digest
from .stage5_identity import identity
from .tuned_pipelines import make_tuned_pipeline
from .pipelines import positive_probability


def group_subset(rows, fraction, seed=42):
    if not 0 < fraction <= 1 or rows.customer_unique_id.isna().any():
        raise ValueError("Invalid training groups/fraction")
    groups = sorted(set(map(str, rows.customer_unique_id)), key=lambda x: (
        hashlib.sha256(f"{seed}:{x}".encode()).hexdigest(), x))
    selected = set(groups[:int(np.ceil(len(groups) * fraction))])
    return np.flatnonzero(rows.customer_unique_id.astype(str).isin(selected).to_numpy())


def check_source(path):
    manifest = json.loads((path / "run_manifest.json").read_text())
    if manifest["stage"] != 4 or manifest["holdout_evaluated"]:
        raise ValueError("Invalid source stage")
    for name, digest in manifest["output_hashes"].items():
        file = (path / name).resolve()
        if not file.is_relative_to(path.resolve()) or sha256_file(file) != digest:
            raise ValueError(f"Source checksum mismatch: {name}")
    selection = json.loads((path / "selection_record.json").read_text())
    if sha256_file(path / "selection_record.json") != manifest["selection_record_sha256"]:
        raise ValueError("Selection checksum mismatch")
    if sha256_file(path / "decision_policy.json") != selection["decision_policy_sha256"]:
        raise ValueError("Policy checksum mismatch")
    return selection, manifest


def run(run_id="stage5-tutorial8-v1", root=ROOT):
    if Path(run_id).name != run_id or not run_id:
        raise ValueError("Unsafe run ID")
    out = root / "artifacts/metrics" / run_id
    source = root / "artifacts/metrics/stage4-selection-v1"
    selection, source_manifest = check_source(source)
    development, cv, hashes = load_development(root)
    if hashes != selection["input_hashes"]:
        raise ValueError("Frozen input mismatch")
    out.mkdir(exist_ok=False, parents=True)
    started = time.monotonic()
    code = identity(root)
    rows = task_rows(development, cv, "classification")
    candidate = selection["tasks"]["classification"]["candidate"]
    folds = pd.read_csv(source / "fold_metrics.csv", float_precision="round_trip")
    fits = json.loads((source / "fit_evidence.json").read_text())
    evidence, curve_records = [], []
    fit_count = 0
    for fold, tr, va in fold_indices(rows):
        training = rows.iloc[tr].reset_index(drop=True)
        validation = rows.iloc[va]
        previous = set()
        for fraction in [.25, .5, 1.]:
            subset = training.iloc[group_subset(training, fraction)]
            groups = set(subset.customer_unique_id)
            if not previous <= groups or groups & set(validation.customer_unique_id):
                raise ValueError("Group nesting/isolation failed")
            previous = groups
            if set(subset.is_detractor) != {0, 1}:
                raise ValueError("Subset lacks both classes")
            common = {"fold": fold, "fraction_training_groups": fraction,
                      "training_n": len(subset), "training_groups": len(groups),
                      "training_positives": int(subset.is_detractor.sum()),
                      "validation_n": len(validation), "validation_groups": validation.customer_unique_id.nunique(),
                      "validation_positives": int(validation.is_detractor.sum()),
                      "train_order_ids_sha256": ids_digest(subset.order_id),
                      "train_group_ids_sha256": ids_digest(groups),
                      "validation_order_ids_sha256": ids_digest(validation.order_id)}
            if fraction == 1.:
                matching = [f for f in fits if f["phase"] == "search" and f["task"] == "classification"
                            and f["candidate"] == candidate["id"] and f["fold"] == fold]
                if len(matching) != 1 or matching[0]["train_order_ids_sha256"] != common["train_order_ids_sha256"] or matching[0]["validation_order_ids_sha256"] != common["validation_order_ids_sha256"]:
                    raise ValueError("Full fold reuse lineage mismatch")
                pipe = joblib.load(source / "cv_models" / f"classification_selected_fold{fold}.joblib")
                if any(pipe.named_steps["model"].get_params()[k] != v for k, v in candidate["params"].items()):
                    raise ValueError("Full-size model configuration mismatch")
                for partition in ["training_resubstitution", "validation"]:
                    saved = folds.loc[folds.task.eq("classification") & folds.candidate.eq(candidate["id"])
                                      & folds.fold.eq(fold) & folds.partition.eq(partition)]
                    if len(saved) != 1:
                        raise ValueError("Full-size score coverage")
                    curve_records.append({**common, "partition": partition, "source": "verified_stage4_reuse",
                        "average_precision": float(saved.iloc[0].average_precision), "roc_auc": float(saved.iloc[0].roc_auc)})
                evidence.append({**common, "fit": False, "checkpoint_sha256": sha256_file(source / "cv_models" / f"classification_selected_fold{fold}.joblib")})
            else:
                if fit_count >= 10 or time.monotonic() - started > 1800:
                    raise RuntimeError("Tutorial 8 budget exhausted; partial evidence retained")
                print(f"learning curve fold={fold} fraction={fraction} n={len(subset)}", flush=True)
                pipe = make_tuned_pipeline("classification", candidate, selection["baseline_config"])
                begin = time.monotonic()
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    pipe.fit(subset[PREDICTOR_ALLOWLIST], subset.is_detractor)
                fit_count += 1
                evidence.append({**common, "fit": True, "seconds": time.monotonic() - begin,
                    "warnings": [{"category": w.category.__name__, "message": str(w.message)} for w in caught],
                    "imputer_statistics": pipe.named_steps["preprocess"].named_transformers_["numeric"].named_steps["impute"].statistics_.tolist()})
                for partition, frame in [("training_resubstitution", subset), ("validation", validation)]:
                    m = metrics("classification", frame.is_detractor, positive_probability(pipe, frame[PREDICTOR_ALLOWLIST]))
                    curve_records.append({**common, "partition": partition, "source": "fresh_subset_fit",
                                          "average_precision": m["average_precision"], "roc_auc": m["roc_auc"]})
            write_json(evidence, out / "learning_fit_evidence.json")
            write_csv_lf(pd.DataFrame(curve_records), out / "learning_curve.csv")
    if time.monotonic() - started > 1800:
        raise RuntimeError("Tutorial 8 wall-time budget exceeded")
    table = pd.DataFrame(curve_records)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    for metric, ax in zip(["average_precision", "roc_auc"], axes):
        for partition, part in table.groupby("partition"):
            for _, values in part.groupby("fold"):
                ax.plot(values.training_n, values[metric], alpha=.18)
            aggregate = part.groupby("fraction_training_groups").agg(n=("training_n", "mean"), mean=(metric, "mean"), sd=(metric, "std"))
            ax.errorbar(aggregate.n, aggregate["mean"], yerr=aggregate.sd, marker="o", label=partition)
        ax.set(xlabel="Eligible training orders (group subsets)", ylabel=metric, title="Selected-model development diagnostic")
        ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(out / "learning_curves.png", dpi=150); plt.close(fig)
    all_predictions = pd.read_csv(source / "candidate_oof_predictions.csv", dtype={"order_id": "string"}, float_precision="round_trip")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    coordinates, summaries = [], []
    for name in ["baseline_dummy", "baseline_linear", "baseline_tree", candidate["id"]]:
        part = all_predictions.loc[all_predictions.task.eq("classification") & all_predictions.candidate.eq(name)]
        if part.order_id.duplicated().any() or set(part.order_id) != set(rows.order_id):
            raise ValueError("OOF comparison coverage")
        aligned = rows[["order_id", "is_detractor", "validation_fold"]].merge(part, on="order_id", validate="one_to_one", suffixes=("_source", "_saved"))
        np.testing.assert_array_equal(aligned.is_detractor, aligned.target)
        np.testing.assert_array_equal(aligned.validation_fold_source, aligned.validation_fold_saved)
        m = metrics("classification", part.target, part.prediction)
        summaries.append({"candidate": name, "population": "pooled development selection OOF", **m})
        fpr, tpr, _ = roc_curve(part.target, part.prediction)
        precision, recall, _ = precision_recall_curve(part.target, part.prediction)
        axes[0].plot(fpr, tpr, label=f"{name}: {m['roc_auc']:.3f}")
        axes[1].plot(recall, precision, label=f"{name}: {m['average_precision']:.3f}")
        coordinates.extend({"candidate": name, "curve": "ROC", "x": x, "y": y} for x, y in zip(fpr, tpr))
        coordinates.extend({"candidate": name, "curve": "PR", "x": x, "y": y} for x, y in zip(recall, precision))
    axes[0].plot([0, 1], [0, 1], "k--", alpha=.4)
    axes[1].axhline(rows.is_detractor.mean(), color="grey", ls="--")
    axes[0].set(xlabel="False positive rate", ylabel="Recall of recorded negatives", title="Development selection OOF ROC")
    axes[1].set(xlabel="Recall of recorded negatives", ylabel="Precision", title="Development selection OOF PR")
    for ax in axes: ax.legend(fontsize=6)
    fig.tight_layout(); fig.savefig(out / "oof_comparison.png", dpi=150); plt.close(fig)
    write_csv_lf(pd.DataFrame(coordinates), out / "oof_curve_coordinates.csv")
    write_csv_lf(pd.DataFrame(summaries), out / "oof_comparison_metrics.csv")
    tree_path = root / "artifacts/metrics/stage3-baseline-v1/cv_models/classification_tree_fold0.joblib"
    baseline_dir = tree_path.parent.parent
    baseline_manifest = json.loads((baseline_dir / "run_manifest.json").read_text())
    if sha256_file(baseline_dir / "run_manifest.json") != source_manifest["source_stage3_manifest_sha256"] or sha256_file(tree_path) != baseline_manifest["output_hashes"]["cv_models/classification_tree_fold0.joblib"]:
        raise ValueError("Tree checkpoint lineage mismatch")
    tree = joblib.load(tree_path)
    one = rows.loc[rows.validation_fold.eq(0)].iloc[[0]]
    transformed = tree[:-1].transform(one[PREDICTOR_ALLOWLIST])
    names = tree[:-1].get_feature_names_out()
    values = transformed.toarray()[0] if hasattr(transformed, "toarray") else transformed[0]
    est = tree.named_steps["model"]
    path_nodes = est.decision_path(transformed).indices
    conditions = []
    for node in path_nodes:
        feature = est.tree_.feature[node]
        if feature >= 0:
            value, cut = float(values[feature]), float(est.tree_.threshold[node])
            conditions.append({"node": int(node), "feature": str(names[feature]), "transformed_value": value,
                "operator": "<=" if value <= cut else ">", "threshold": cut})
    probability = positive_probability(tree, one[PREDICTOR_ALLOWLIST])[0]
    np.testing.assert_allclose(probability, est.predict_proba(transformed)[0, list(est.classes_).index(1)], atol=1e-12)
    (out / "development_tree_rules.txt").write_text(export_text(est, feature_names=list(names)), encoding="utf-8")
    write_json({"task": "classification", "model": "baseline CART, not selected forest", "fold": 0,
        "checkpoint_sha256": sha256_file(tree_path), "order_id": str(one.iloc[0].order_id),
        "conditions": conditions, "leaf": int(est.apply(transformed)[0]), "probability_1": probability,
        "tree_default_prediction": int(tree.predict(one[PREDICTOR_ALLOWLIST])[0]),
        "raw_predictors": one[PREDICTOR_ALLOWLIST].iloc[0].to_dict(),
        "numeric_note": "Original units after training imputation; indicator and one-hot values are 0/1",
        "scale_present": "scale" in tree.named_steps["preprocess"].named_transformers_["numeric"].named_steps}, out / "worked_tree_path.json")
    if identity(root)["code_identity_sha256"] != code["code_identity_sha256"]:
        raise ValueError("Supplement executable dependencies changed during run")
    write_json({"stage": "5_pre_holdout_diagnostics", "holdout_evaluated": False,
        "fit_count": fit_count, "wall_seconds": time.monotonic() - started, "input_hashes": hashes,
        "source_stage4_manifest_sha256": sha256_file(source / "run_manifest.json"),
        "selection_sha256": sha256_file(source / "selection_record.json"), "teaching_addendum": "T8-2026-10-05",
        "code": code, "status": "internally_complete_pending_review",
        "output_hashes": {p.name: sha256_file(p) for p in out.iterdir() if p.is_file()}}, out / "run_manifest.json")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="stage5-tutorial8-v1")
    run(parser.parse_args().run_id)
