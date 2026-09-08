"""Staging-layer builder (docs/data_architecture.md §4.2).

Reads each raw CSV, applies its staging contract (parse dates, assign dtypes,
retain source grain), validates the result, and — only if every check passes —
writes one Parquet per source table to ``data/staging/``.

No joins, aggregations, dashboard calculations, or target construction happen
here: the staging layer stays typed and source-aligned.

Usage:
    python preprocessing/build_staging.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common import loaders, schemas  # noqa: E402
from preprocessing import validation  # noqa: E402


def main() -> None:
    raw_dir = ROOT / "data" / "raw"
    staging_dir = ROOT / "data" / "staging"
    manifest_path = ROOT / "data" / "metadata" / "raw_manifest.csv"

    if not manifest_path.exists():
        sys.exit("FATAL: raw_manifest.csv not found — run ingest_raw.py first.")
    manifest = pd.read_csv(manifest_path)
    expected_rows = dict(zip(manifest["table"], manifest["row_count"]))

    staging_dir.mkdir(parents=True, exist_ok=True)

    failed = False
    for name in schemas.TABLE_ORDER:
        df = loaders.load_typed_table(name, raw_dir)
        issues = validation.check_staging_table(name, df, int(expected_rows[name]))
        if issues:
            failed = True
            print(f"[FAIL] {name}: not written")
            for f in issues:
                print(f"        - {f}")
            continue  # refuse to publish an invalid table (§7)
        df.to_parquet(staging_dir / f"{name}.parquet", index=False)
        print(f"[OK]   {name:12s} {len(df):>9,} rows -> {name}.parquet")

    if failed:
        sys.exit("\nStaging build ABORTED: invalid tables were not written. "
                 "Fix the contract and re-run.")

    print("\nAll 9 staging tables validated and written to data/staging/.")
    print("Run `python preprocessing/validation.py --determinism` for the full report.")


if __name__ == "__main__":
    main()
