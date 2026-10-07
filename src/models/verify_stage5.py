"""Read-only Stage 5 verification, including fresh-process no-fit reload checks."""
from __future__ import annotations

import argparse
import json
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from src.common.loaders import sha256_file
from src.features.contract import PREDICTOR_ALLOWLIST
from .data import ROOT, TARGETS, load_development, task_rows, fold_indices
from .finalize import feature_stats, report_metrics, per_class_report, subgroup_tables, holdout_rows
from .io import clean_json, ids_digest, write_json
from .pipelines import normalize_inputs, positive_probability
from .score import Scorer
from .tutorial8 import group_subset
from .reproduction import evaluation_receipt


def check_files(path):
    manifest = json.loads((path / "run_manifest.json").read_text())
    for name, digest in manifest["output_hashes"].items():
        file = (path / name).resolve()
        if not file.is_relative_to(path.resolve()) or sha256_file(file) != digest:
            raise ValueError(f"Checksum mismatch {name}")
    return manifest


def compare(saved, calculated):
    # Numerical round-trip comparisons; metadata/undefined values exact.
    if isinstance(calculated, dict):
        for key, value in calculated.items(): compare(saved[key], value)
    elif isinstance(calculated, list):
        if len(saved) != len(calculated): raise ValueError("Length mismatch")
        for a, b in zip(saved, calculated): compare(a, b)
    elif isinstance(calculated, (int, float, np.number)) and not isinstance(calculated, (bool, np.bool_)):
        np.testing.assert_allclose(saved, calculated, atol=1e-10, rtol=1e-10)
    elif saved != calculated:
        raise ValueError(f"Metadata mismatch: {saved} != {calculated}")


def verify_supplement(path, root=ROOT):
    manifest = check_files(path)
    if manifest["holdout_evaluated"] or manifest["fit_count"] != 10 or manifest["wall_seconds"] > 1800:
        raise ValueError("Supplement budget/holdout flag")
    development, cv, hashes = load_development(root)
    if manifest["input_hashes"] != hashes: raise ValueError("Supplement input hashes")
    source = root / "artifacts/metrics/stage4-selection-v1"
    if manifest["source_stage4_manifest_sha256"] != sha256_file(source / "run_manifest.json"):
        raise ValueError("Supplement source hash")
    rows = task_rows(development, cv, "classification")
    evidence = json.loads((path / "learning_fit_evidence.json").read_text())
    table = pd.read_csv(path / "learning_curve.csv", float_precision="round_trip")
    if len(evidence) != 15 or len(table) != 30: raise ValueError("Learning curve coverage")
    for fold, tr, va in fold_indices(rows):
        training = rows.iloc[tr].reset_index(drop=True)
        for fraction in [.25, .5, 1.]:
            subset = training.iloc[group_subset(training, fraction)]
            records = [r for r in evidence if r["fold"] == fold and r["fraction_training_groups"] == fraction]
            if len(records) != 1: raise ValueError("Learning record coverage")
            rec = records[0]
            if rec["train_order_ids_sha256"] != ids_digest(subset.order_id) or rec["train_group_ids_sha256"] != ids_digest(set(subset.customer_unique_id)) or rec["validation_order_ids_sha256"] != ids_digest(rows.iloc[va].order_id):
                raise ValueError("Learning membership mismatch")
            if rec["training_n"] != len(subset) or rec["training_positives"] != int(subset.is_detractor.sum()):
                raise ValueError("Learning count mismatch")
            if fraction < 1:
                normalized, _ = normalize_inputs(subset)
                columns = root / "data/business/ml/feature_schema.json"
                numeric = json.loads(columns.read_text())["numeric_columns"]
                calculated = normalized[numeric].median().fillna(0).to_numpy()
                np.testing.assert_allclose(calculated, rec["imputer_statistics"], atol=1e-12)
            elif rec["checkpoint_sha256"] != sha256_file(source / "cv_models" / f"classification_selected_fold{fold}.joblib"):
                raise ValueError("Reused model hash")
    if not np.isfinite(table[["average_precision", "roc_auc"]]).all().all(): raise ValueError("Learning scores invalid")
    return {"status": "passed_internal_verification", "fit_count": 10, "fold_size_records": 15,
            "holdout_evaluated": False, "output_files_checked": len(manifest["output_hashes"])}


def verify(path, root=ROOT):
    manifest = check_files(path)
    if manifest["stage"] != 5 or not manifest["holdout_evaluated"] or manifest["fit_count"] != 2:
        raise ValueError("Final run stage/fit count")
    receipt = evaluation_receipt(root, manifest, path.name)
    if receipt["state"] != "evaluated_and_published" or receipt["run_id"] != path.name or receipt["run_manifest_sha256"] != sha256_file(path / "run_manifest.json"):
        raise ValueError("Protected evaluation receipt")
    development, cv, hashes = load_development(root)
    if manifest["input_hashes"] != hashes: raise ValueError("Final input identity mismatch")
    holdout = holdout_rows(root, development, hashes)
    schema = json.loads((root / "data/business/ml/feature_schema.json").read_text())
    selection = json.loads((root / "artifacts/metrics/stage4-selection-v1/selection_record.json").read_text())
    source_policy = json.loads((root / "artifacts/metrics/stage4-selection-v1/decision_policy.json").read_text())
    if manifest["selection_sha256"] != sha256_file(root / "artifacts/metrics/stage4-selection-v1/selection_record.json"):
        raise ValueError("Final selection mismatch")
    outcomes = json.loads((path / "holdout_metrics.json").read_text())
    subgroup, reports, validations = [], [], {}
    preprocessors = []
    with patch.object(Pipeline, "fit", side_effect=AssertionError("Verifier/inference must never fit")):
        for task in TARGETS:
            bundle = root / "artifacts/models" / task / path.name
            if sha256_file(bundle / "bundle_manifest.json") != manifest["bundle_manifest_sha256"][task]:
                raise ValueError("Bundle lineage mismatch")
            scorer = Scorer(bundle)
            if scorer.metadata["model_version"] != path.name or scorer.metadata["input_hashes"] != hashes:
                raise ValueError("Bundle versions/input lineage")
            for version in ["feature_version", "contract_version", "split_version"]:
                if scorer.metadata[version] != selection[version]: raise ValueError("Bundle contract version mismatch")
            configuration = json.loads((bundle / "configuration.json").read_text())
            compare(scorer.pipeline.named_steps["model"].get_params(), configuration["estimator_params"])
            preprocessors.append(scorer.pipeline.named_steps["preprocess"])
            if sha256_file(bundle / "pipeline.joblib") != receipt["pipeline_hashes"][task]: raise ValueError("Final pipeline receipt mismatch")
            compare(scorer.pipeline.named_steps["model"].get_params(), selection["tasks"][task]["candidate"]["params"])
            training = task_rows(development, cv, task)
            compare(json.loads((bundle / "feature_stats.json").read_text()), clean_json(feature_stats(training, schema, hashes["orders_ml_features.csv"])))
            if scorer.metadata["training"]["training_order_ids_sha256"] != ids_digest(training.order_id): raise ValueError("Final train population")
            normalized, _ = normalize_inputs(training)
            numeric = schema["numeric_columns"]
            actual_imputer = scorer.pipeline.named_steps["preprocess"].named_transformers_["numeric"].named_steps["impute"]
            np.testing.assert_allclose(actual_imputer.statistics_, normalized[numeric].median().fillna(0), atol=1e-12)
            encoder = scorer.pipeline.named_steps["preprocess"].named_transformers_["categorical"]
            for col, categories in zip(schema["categorical_columns"], encoder.categories_):
                np.testing.assert_array_equal(categories, sorted(normalized[col].unique()))
            rows = holdout.loc[holdout[f"eligible_{task}"].eq(1)].reset_index(drop=True)
            saved = pd.read_csv(path / f"{task}_holdout_predictions.csv", dtype={"order_id": "string"}, float_precision="round_trip")
            if not saved.order_id.equals(rows.order_id): raise ValueError("Holdout row alignment")
            np.testing.assert_array_equal(saved.target, rows[TARGETS[task]])
            fresh = scorer.pipeline.predict(rows[PREDICTOR_ALLOWLIST]) if task == "regression" else positive_probability(scorer.pipeline, rows[PREDICTOR_ALLOWLIST])
            np.testing.assert_allclose(fresh, saved.prediction, atol=1e-12, rtol=1e-12)
            threshold = scorer.policy["threshold"] if scorer.policy else .5
            compare(outcomes[task]["metrics"], report_metrics(task, saved.target, saved.prediction, threshold))
            if task == "classification":
                compare(scorer.policy, source_policy)
                np.testing.assert_array_equal(saved.policy_decision, (saved.prediction >= threshold).astype(int))
                compare(outcomes[task]["default_0_5_metrics"], report_metrics(task, saved.target, saved.prediction, .5))
                for tag, cut in [("default_0_5", .5), ("frozen_policy", threshold)]:
                    reports.extend({"policy": tag, **r} for r in per_class_report(saved.target, saved.prediction, cut))
            subgroup.extend(subgroup_tables(task, rows, saved.prediction, threshold))
            # Raw predictors only; no target or status at inference.
            sample = rows.iloc[:16][["order_id"] + PREDICTOR_ALLOWLIST]
            batch = scorer.score(sample)
            if not batch.status.eq("valid").all(): raise ValueError("Valid sample scoring failed")
            field = "probability_1" if task == "classification" else "prediction"
            single = [scorer.score(sample.iloc[[i]]).iloc[0][field] for i in range(len(sample))]
            np.testing.assert_allclose(single, batch[field], atol=1e-12, rtol=1e-12)
            np.testing.assert_allclose(scorer.score(sample.iloc[::-1, ::-1])[field].iloc[::-1], batch[field], atol=1e-12)
            extended = sample.assign(lead_days=-999, is_detractor=999, order_status="changed")
            np.testing.assert_array_equal(scorer.score(extended)[field], batch[field])
            missing = sample.iloc[[0]].copy(); missing[PREDICTOR_ALLOWLIST] = np.nan
            unseen = sample.iloc[[1]].copy(); unseen["primary_category"] = "not_a_training_category"
            if scorer.score(missing).iloc[0].status != "valid" or scorer.score(unseen).iloc[0].status != "valid": raise ValueError("Missing/unseen scoring failed")
            invalid = sample.copy(); invalid.loc[invalid.index[2], "total_price"] = -1
            invalid_result = scorer.score(invalid)
            if invalid_result.iloc[2].status != "invalid" or not pd.isna(invalid_result.iloc[2].prediction): raise ValueError("Invalid row fallback")
            if len(invalid_result) != len(sample) or int(invalid_result.status.eq("invalid").sum()) != 1: raise ValueError("Invalid row isolation")
            validations[task] = {"holdout_n": len(rows), "reload_tolerance": 1e-12, "sample_n": len(sample),
                "single_batch_reorder_isolation_missing_unseen_invalid": "passed", "no_fit": True}
        if preprocessors[0] is preprocessors[1]: raise ValueError("Shared final preprocessing")
    actual = pd.read_csv(path / "holdout_subgroups.csv", float_precision="round_trip")
    expected = pd.DataFrame(subgroup)
    pd.testing.assert_frame_equal(actual, expected, check_dtype=False, atol=1e-10, rtol=1e-10)
    expected_reports = pd.DataFrame(reports)
    expected_reports = expected_reports.where(expected_reports.notna(), np.nan)
    pd.testing.assert_frame_equal(pd.read_csv(path / "classification_per_class_report.csv", float_precision="round_trip"), expected_reports, check_dtype=False, atol=1e-12)
    tests = unittest.TextTestRunner(verbosity=1).run(unittest.defaultTestLoader.discover(str(root / "src/models/tests")))
    if not tests.wasSuccessful(): raise ValueError("Unit fixtures failed")
    return {"status": "passed_internal_verification", "stage": 5, "unit_tests": tests.testsRun,
            "output_files_checked": len(manifest["output_hashes"]), "tasks": validations,
            "run_manifest_sha256": sha256_file(path / "run_manifest.json"),
            "verifier_sha256": sha256_file(Path(__file__)),
            "holdout_evaluated": True, "independent_agent_review": "pending", "team_review": "pending"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="stage5-final-v1")
    parser.add_argument("--supplement-only", action="store_true")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    path = ROOT / "artifacts/metrics" / args.run_id
    report = verify_supplement(path) if args.supplement_only else verify(path)
    print(json.dumps(report, indent=2))
    if args.report:
        if args.report.exists(): raise ValueError("Report already exists")
        write_json(report, args.report)
