"""Recreate the six-order development scoring example from frozen raw-unit features.

No fitting or holdout access. Existing example directories are never overwritten.
"""
import argparse
from pathlib import Path

from src.common.loaders import sha256_file
from src.features.contract import PREDICTOR_ALLOWLIST
from .data import ROOT, load_development
from .io import write_csv_lf, write_json
from .score import Scorer


def run(root=ROOT, run_id="stage5-scoring-demo-v1", model_id="stage5-final-v1"):
    if Path(run_id).name != run_id or not run_id or Path(model_id).name != model_id or not model_id:
        raise ValueError("Unsafe run/model ID")
    out = root / "artifacts/metrics" / run_id
    if out.exists():
        raise FileExistsError("Existing scoring example cannot be overwritten")
    development, _, _ = load_development(root)
    sample = development.iloc[:6][["order_id"] + PREDICTOR_ALLOWLIST]
    out.mkdir(parents=True)
    source = out / "original_unit_development_sample.csv"
    write_csv_lf(sample, source)
    # Read the actual CLI-style CSV bytes with round-trip float parsing.
    import pandas as pd
    frame = pd.read_csv(source, dtype={"order_id": "string"}, float_precision="round_trip")
    for task in ["regression", "classification"]:
        result = Scorer(root / "artifacts/models" / task / model_id).score(frame)
        write_csv_lf(result, out / f"{task}_scores.csv")
        write_json({"input_sha256": sha256_file(source), "n": len(result),
                    "valid": int(result.status.eq("valid").sum()),
                    "invalid": int(result.status.eq("invalid").sum()),
                    "ignored_columns": [], "no_fit": True}, out / f"{task}_scores.qa.json")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", default="stage5-scoring-demo-v1")
    parser.add_argument("--model-id", default="stage5-final-v1")
    args = parser.parse_args()
    print(run(run_id=args.run_id, model_id=args.model_id))
