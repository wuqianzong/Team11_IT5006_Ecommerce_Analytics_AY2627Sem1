"""Original-unit local scoring of trusted, checksummed Stage 5 bundles; never fits."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.common.loaders import sha256_file
from src.features.contract import PREDICTOR_ALLOWLIST
from .io import write_csv_lf, write_json
from .pipelines import normalize_inputs, positive_probability
from .policy import apply_threshold


def checked_manifest(path):
    path = Path(path).resolve()
    manifest = json.loads((path / "bundle_manifest.json").read_text())
    for name, digest in manifest["output_hashes"].items():
        file = (path / name).resolve()
        if not file.is_relative_to(path) or sha256_file(file) != digest:
            raise ValueError(f"Bundle checksum mismatch: {name}")
    if not {"pipeline.joblib", "metadata.json", "feature_schema.json", "feature_stats.json",
            "configuration.json"}.issubset(manifest["output_hashes"]):
        raise ValueError("Incomplete scoring bundle")
    return manifest


class Scorer:
    def __init__(self, bundle):
        self.bundle = Path(bundle)
        checked_manifest(self.bundle)  # Never deserialize untrusted joblib files.
        self.metadata = json.loads((self.bundle / "metadata.json").read_text())
        self.task = self.metadata["task"]
        schema = json.loads((self.bundle / "feature_schema.json").read_text())
        if self.task not in {"regression", "classification"} or schema["predictor_allowlist"] != PREDICTOR_ALLOWLIST:
            raise ValueError("Unsupported bundle contract")
        self.pipeline = joblib.load(self.bundle / "pipeline.joblib")
        self.policy = None
        if self.task == "classification":
            self.policy = json.loads((self.bundle / "decision_policy.json").read_text())
            apply_threshold([0., 1.], self.policy)
            if self.policy.get("comparison") != ">=":
                raise ValueError("Unsupported policy comparison")

    def score(self, features):
        if not isinstance(features, pd.DataFrame):
            raise ValueError("Named dataframe required")
        if features.columns.duplicated().any():
            raise ValueError("Duplicate column names")
        frame = features.reset_index(drop=True)
        ids = frame.order_id.astype("string") if "order_id" in frame else pd.Series(pd.NA, index=frame.index, dtype="string")
        bad_id = ids.isna() | ids.str.strip().eq("").fillna(True) | ids.duplicated(keep=False)
        missing = sorted(set(PREDICTOR_ALLOWLIST) - set(frame.columns))
        records, valid = [], []
        for i in range(len(frame)):
            record = {"input_row": i, "order_id": None if pd.isna(ids.iloc[i]) else str(ids.iloc[i]),
                      "task": self.task, "model_version": self.metadata["model_version"],
                      "feature_version": self.metadata["feature_version"],
                      "contract_version": self.metadata["contract_version"],
                      "split_version": self.metadata["split_version"],
                      "prediction": None, "probability_1": None, "decision": None,
                      "threshold": self.policy["threshold"] if self.policy else None,
                      "status": "invalid", "error": None, "warnings": None}
            if bad_id.iloc[i]:
                record["error"] = "missing/blank/duplicate order_id"
            elif missing:
                record["error"] = "missing predictor columns: " + ",".join(missing)
            else:
                try:
                    _, quality = normalize_inputs(frame.iloc[[i]])
                    notices = {k: v for k, v in quality.items() if v["malformed_tokens"] or v["missing_cells"]}
                    notices["missing_predictor_cells"] = [c for c in PREDICTOR_ALLOWLIST if pd.isna(frame.iloc[i][c])]
                    record["warnings"] = json.dumps(notices, sort_keys=True)
                    record["status"] = "valid"
                    valid.append(i)
                except (ValueError, TypeError) as error:
                    record["error"] = str(error)
            records.append(record)
        if valid:
            X = frame.iloc[valid][PREDICTOR_ALLOWLIST]
            values = self.pipeline.predict(X) if self.task == "regression" else positive_probability(self.pipeline, X)
            if not np.isfinite(values).all():
                raise ValueError("Nonfinite model output")
            decisions = apply_threshold(values, self.policy) if self.policy else None
            for j, i in enumerate(valid):
                records[i]["prediction"] = float(values[j]) if self.task == "regression" else int(decisions[j])
                if self.policy:
                    records[i].update(probability_1=float(values[j]), decision=int(decisions[j]))
        return pd.DataFrame(records, columns=["input_row", "order_id", "task", "model_version", "feature_version",
            "contract_version", "split_version", "prediction", "probability_1", "decision", "threshold", "status", "error", "warnings"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.with_suffix(".qa.json").exists():
        raise ValueError("Refusing to overwrite existing scoring outputs")
    with args.input.open(newline="", encoding="utf-8") as f:
        headers = next(csv.reader(f), [])
    if len(headers) != len(set(headers)):
        raise ValueError("Duplicate CSV column names")
    frame = pd.read_csv(args.input, dtype={"order_id": "string"}, float_precision="round_trip")
    result = Scorer(args.bundle).score(frame)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    write_csv_lf(result, args.output)
    write_json({"input_sha256": sha256_file(args.input), "n": len(result),
                "valid": int(result.status.eq("valid").sum()), "invalid": int(result.status.eq("invalid").sum()),
                "ignored_columns": sorted(set(frame.columns) - set(PREDICTOR_ALLOWLIST) - {"order_id"}),
                "no_fit": True}, args.output.with_suffix(".qa.json"))


if __name__ == "__main__":
    main()
