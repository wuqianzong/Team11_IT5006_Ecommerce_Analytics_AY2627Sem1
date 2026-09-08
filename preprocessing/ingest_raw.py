"""Raw-layer ingestion (docs/data_architecture.md §4.1).

Copies the nine original Olist CSVs byte-for-byte into ``data/raw/`` and writes
``data/metadata/raw_manifest.csv`` recording each file's name, byte count, row
count, and SHA-256 checksum. Raw files are local-only and must not be committed
(``.gitignore`` already excludes ``data/raw/*``).

Fails clearly if an expected source file is absent.

Usage:
    python preprocessing/ingest_raw.py [--source DIR]
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common import loaders, schemas  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest raw Olist CSVs into data/raw/")
    parser.add_argument("--source", type=Path,
                        default=ROOT.parent / "archive",
                        help="Directory holding the 9 original CSVs")
    args = parser.parse_args()

    raw_dir = ROOT / "data" / "raw"
    metadata_dir = ROOT / "data" / "metadata"
    raw_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    records = []
    for name in schemas.TABLE_ORDER:
        raw_file = schemas.SCHEMAS[name]["raw_file"]
        src = args.source / raw_file
        if not src.exists():
            sys.exit(f"FATAL: expected raw file not found: {src}")

        dst = raw_dir / raw_file
        shutil.copy2(src, dst)  # byte-for-byte copy

        records.append({
            "table": name,
            "raw_file": raw_file,
            "byte_count": dst.stat().st_size,
            "row_count": loaders.count_rows(dst),
            "sha256": loaders.sha256_file(dst),
        })
        print(f"ingested {raw_file:38s} rows={records[-1]['row_count']:>8,} "
              f"bytes={records[-1]['byte_count']:>12,}")

    manifest = pd.DataFrame(records)
    manifest_path = metadata_dir / "raw_manifest.csv"
    manifest.to_csv(manifest_path, index=False)
    print(f"\nwrote manifest -> {manifest_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
