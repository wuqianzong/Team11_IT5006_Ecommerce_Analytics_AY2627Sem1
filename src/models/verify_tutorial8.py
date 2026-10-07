"""Standalone development-only Tutorial 8 verifier; no finalization/scoring imports."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from src.common.loaders import sha256_file
from .data import ROOT, load_development, task_rows, fold_indices
from .io import ids_digest, write_json
from .pipelines import normalize_inputs
from .tutorial8 import group_subset

def check_files(path):
    manifest = json.loads((path / "run_manifest.json").read_text())
    for name, digest in manifest["output_hashes"].items():
        file = (path / name).resolve()
        if not file.is_relative_to(path.resolve()) or sha256_file(file) != digest:
            raise ValueError(f"Checksum mismatch {name}")
    return manifest

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

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="stage5-tutorial8-v1")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if Path(args.run_id).name != args.run_id: raise ValueError("Unsafe run ID")
    path = ROOT / "artifacts/metrics" / args.run_id
    report = verify_supplement(path)
    report.update(stage="5_pre_holdout_diagnostics", run_manifest_sha256=sha256_file(path / "run_manifest.json"), verifier_sha256=sha256_file(Path(__file__)))
    print(json.dumps(report, indent=2))
    if args.report:
        if args.report.exists(): raise FileExistsError("Existing verification report")
        write_json(report, args.report)


if __name__ == "__main__":
    main()
