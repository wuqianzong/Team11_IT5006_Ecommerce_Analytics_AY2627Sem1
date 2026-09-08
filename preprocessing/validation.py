"""Data-contract validation for the raw and staging layers.

Implements the required checks from docs/data_architecture.md §7: expected
columns and types, unique/non-null primary keys, accepted categorical values,
plausible numeric and date ranges, source/output row counts, and deterministic
output. A failed check stops the pipeline (the staging builder refuses to write,
and this script exits non-zero).
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.common import core_schemas, loaders, schemas  # noqa: E402

DATE_MIN = pd.Timestamp("2015-01-01")
DATE_MAX = pd.Timestamp("2021-01-01")  # upper bound allows 4 known anomalous 2020 shipping dates

# Core tables whose row count must equal their staging source (dim_geography is
# deduplicated to zip prefixes, so it has no direct source row count).
CORE_SOURCE_ROWCOUNT = {
    "fact_orders": "orders",
    "fact_order_items": "order_items",
    "fact_payments": "payments",
    "fact_reviews": "reviews",
    "dim_customers": "customers",
    "dim_sellers": "sellers",
    "dim_products": "products",
}


def check_raw_files(manifest: pd.DataFrame, raw_dir: Path) -> list[str]:
    """Verify every raw file exists with the recorded byte count and checksum."""
    failures: list[str] = []
    for _, row in manifest.iterrows():
        path = raw_dir / row["raw_file"]
        if not path.exists():
            failures.append(f"{row['raw_file']}: missing from {raw_dir}")
            continue
        byte_count = path.stat().st_size
        if int(byte_count) != int(row["byte_count"]):
            failures.append(
                f"{row['raw_file']}: byte count {byte_count} != manifest {row['byte_count']}")
        sha = loaders.sha256_file(path)
        if sha != row["sha256"]:
            failures.append(f"{row['raw_file']}: SHA-256 mismatch")
        rows = loaders.count_rows(path)
        if rows != int(row["row_count"]):
            failures.append(
                f"{row['raw_file']}: row count {rows} != manifest {row['row_count']}")
    return failures


def check_staging_table(name: str, df: pd.DataFrame, expected_rows: int) -> list[str]:
    """Run every contract check on one typed staging table. Returns failures."""
    spec = schemas.SCHEMAS[name]
    expected_cols = list(spec["dtypes"].keys())
    failures: list[str] = []

    # 1. columns (exact set and order)
    if list(df.columns) != expected_cols:
        failures.append(f"columns {list(df.columns)} != expected {expected_cols}")

    # 2. source/output row count (grain preserved)
    if len(df) != expected_rows:
        failures.append(f"row count {len(df)} != source {expected_rows}")

    # 3. primary key unique + non-null
    pk = spec["primary_key"]
    if pk:
        if df[pk].isna().any().any():
            failures.append(f"primary key {pk} has nulls")
        if df.duplicated(subset=pk).any():
            failures.append(f"primary key {pk} has duplicates")

    # 4. accepted categorical values
    for col, allowed in spec["categorical"].items():
        actual = set(df[col].dropna().unique())
        bad = actual - set(allowed)
        if bad:
            failures.append(f"{col}: unexpected values {sorted(bad)}")

    # 5. plausible numeric ranges
    for col, (lo, hi) in spec["ranges"].items():
        s = pd.to_numeric(df[col], errors="coerce")
        if lo is not None and (s < lo).any():
            failures.append(f"{col}: values below {lo}")
        if hi is not None and (s > hi).any():
            failures.append(f"{col}: values above {hi}")

    # 6. plausible date ranges
    for col, dt in spec["dtypes"].items():
        if dt == "datetime":
            s = df[col]
            if (s < DATE_MIN).any() or (s > DATE_MAX).any():
                failures.append(f"{col}: dates outside {DATE_MIN.date()}..{DATE_MAX.date()}")

    # 7. data types
    for col, dt in spec["dtypes"].items():
        if dt == "datetime" and not pd.api.types.is_datetime64_any_dtype(df[col]):
            failures.append(f"{col}: expected datetime64, got {df[col].dtype}")
        elif dt == "int64" and not pd.api.types.is_integer_dtype(df[col]):
            failures.append(f"{col}: expected integer, got {df[col].dtype}")
        elif dt == "float64" and not pd.api.types.is_float_dtype(df[col]):
            failures.append(f"{col}: expected float, got {df[col].dtype}")

    return failures


def check_core_table(name: str, df: pd.DataFrame) -> list[str]:
    """Column set/order, primary-key uniqueness, and targeted domain checks."""
    spec = core_schemas.CORE_SCHEMAS[name]
    failures: list[str] = []

    if list(df.columns) != spec["columns"]:
        failures.append(f"columns {list(df.columns)} != expected {spec['columns']}")

    pk = spec["primary_key"]
    if pk:
        if df[pk].isna().any().any():
            failures.append(f"primary key {pk} has nulls")
        if df.duplicated(subset=pk).any():
            failures.append(f"primary key {pk} has duplicates")

    if name == "fact_orders":
        bad = set(df["order_status"].dropna().unique()) - schemas.ORDER_STATUS
        if bad:
            failures.append(f"order_status: unexpected {sorted(bad)}")
    if name == "dim_customers":
        bad = set(df["customer_state"].dropna().unique()) - schemas.BR_STATES
        if bad:
            failures.append(f"customer_state: unexpected {sorted(bad)}")
    if name == "dim_sellers":
        bad = set(df["seller_state"].dropna().unique()) - schemas.BR_STATES
        if bad:
            failures.append(f"seller_state: unexpected {sorted(bad)}")
    if name == "dim_geography":
        lat, lng = df["centroid_lat"], df["centroid_lng"]
        if not lat.between(-33.75, 5.30).all():
            failures.append("centroid_lat outside Brazil bounds")
        if not lng.between(-74.00, -34.00).all():
            failures.append("centroid_lng outside Brazil bounds")

    return failures


def check_referential_integrity(core: dict) -> list[str]:
    """Every fact foreign key must resolve to a dimension primary key (§7)."""
    failures: list[str] = []
    for (ft, fc), (dt, dc) in core_schemas.REFERENTIAL_INTEGRITY:
        fact_vals = set(core[ft][fc].dropna().unique())
        dim_vals = set(core[dt][dc].dropna().unique())
        orphans = fact_vals - dim_vals
        if orphans:
            sample = ", ".join(sorted(map(str, orphans))[:3])
            failures.append(f"{ft}.{fc} -> {dt}.{dc}: {len(orphans)} orphan value(s) "
                            f"e.g. {sample}")
    return failures


def check_mart_table(name: str, df: pd.DataFrame) -> list[str]:
    """Column set/order and primary-key uniqueness for a presentation mart."""
    spec = core_schemas.MART_SCHEMAS[name]
    failures: list[str] = []

    if list(df.columns) != spec["columns"]:
        failures.append(f"columns {list(df.columns)} != expected {spec['columns']}")

    pk = spec["primary_key"]
    if pk:
        if df[pk].isna().any().any():
            failures.append(f"primary key {pk} has nulls")
        if df.duplicated(subset=pk).any():
            failures.append(f"primary key {pk} has duplicates")
    return failures


def check_determinism(name: str, raw_dir: Path) -> tuple[bool, str]:
    """Load + serialize twice; identical bytes prove deterministic output."""
    a = loaders.load_typed_table(name, raw_dir)
    b = loaders.load_typed_table(name, raw_dir)
    with tempfile.TemporaryDirectory() as td:
        pa, pb = Path(td) / "a.parquet", Path(td) / "b.parquet"
        a.to_parquet(pa, index=False)
        b.to_parquet(pb, index=False)
        same = pa.read_bytes() == pb.read_bytes()
    return same, ("identical" if same else "DIFFERENT")


def run_full_validation(raw_dir: Path, staging_dir: Path,
                        manifest_path: Path, check_determinism_flag: bool) -> dict:
    manifest = pd.read_csv(manifest_path)
    report = {"raw_failures": check_raw_files(manifest, raw_dir), "staging": {}}
    for name in schemas.TABLE_ORDER:
        expected_rows = int(manifest.loc[manifest["table"] == name, "row_count"].iloc[0])
        parquet = staging_dir / f"{name}.parquet"
        if not parquet.exists():
            report["staging"][name] = ["parquet file missing"]
            continue
        df = pd.read_parquet(parquet)
        report["staging"][name] = check_staging_table(name, df, expected_rows)
        if check_determinism_flag:
            same, msg = check_determinism(name, raw_dir)
            if not same:
                report["staging"][name].append(f"determinism: {msg}")
    return report


def main() -> None:
    raw_dir = ROOT / "data" / "raw"
    staging_dir = ROOT / "data" / "staging"
    core_dir = ROOT / "data" / "processed" / "core"
    mart_dir = ROOT / "data" / "processed" / "marts"
    manifest_path = ROOT / "data" / "metadata" / "raw_manifest.csv"
    determinism = "--determinism" in sys.argv

    if not manifest_path.exists():
        sys.exit("FATAL: raw_manifest.csv not found — run ingest_raw.py first.")

    report = run_full_validation(raw_dir, staging_dir, manifest_path, determinism)
    manifest = pd.read_csv(manifest_path)
    rowcount = dict(zip(manifest["table"], manifest["row_count"]))

    print("=" * 62)
    print("RAW LAYER")
    if report["raw_failures"]:
        for f in report["raw_failures"]:
            print("  [FAIL]", f)
    else:
        print("  [OK] all 9 files present, byte counts + SHA-256 + row counts match")

    print("=" * 62)
    print("STAGING LAYER")
    total_fail = len(report["raw_failures"])
    for name in schemas.TABLE_ORDER:
        fails = report["staging"][name]
        total_fail += len(fails)
        status = "OK  " if not fails else "FAIL"
        print(f"  [{status}] {name}")
        for f in fails:
            print(f"        - {f}")

    # ---- core layer ----
    core: dict[str, pd.DataFrame] = {}
    print("=" * 62)
    print("CORE LAYER")
    for name in core_schemas.CORE_ORDER:
        path = core_dir / f"{name}.parquet"
        if not path.exists():
            print(f"  [FAIL] {name}: parquet missing")
            total_fail += 1
            continue
        df = pd.read_parquet(path)
        core[name] = df
        fails = check_core_table(name, df)
        src = CORE_SOURCE_ROWCOUNT.get(name)
        if src and len(df) != int(rowcount[src]):
            fails.append(f"row count {len(df)} != staging {rowcount[src]}")
        total_fail += len(fails)
        status = "OK  " if not fails else "FAIL"
        print(f"  [{status}] {name}  ({len(df):,} rows)")
        for f in fails:
            print(f"        - {f}")

    if core:
        ri = check_referential_integrity(core)
        total_fail += len(ri)
        print("  --- referential integrity ---")
        if ri:
            for f in ri:
                print(f"  [FAIL] {f}")
        else:
            print("  [OK] all fact FKs resolve to dimension PKs")

    # ---- marts layer ----
    print("=" * 62)
    print("MARTS LAYER")
    for name in core_schemas.MART_ORDER:
        path = mart_dir / f"{name}.parquet"
        if not path.exists():
            print(f"  [FAIL] {name}: parquet missing")
            total_fail += 1
            continue
        df = pd.read_parquet(path)
        fails = check_mart_table(name, df)
        if name == "mart_order_dashboard" and "fact_orders" in core:
            if len(df) != len(core["fact_orders"]):
                fails.append(f"row count {len(df)} != fact_orders {len(core['fact_orders'])}")
        if name == "mart_order_items" and "fact_order_items" in core:
            if len(df) != len(core["fact_order_items"]):
                fails.append(f"row count {len(df)} != fact_order_items {len(core['fact_order_items'])}")
        if name == "mart_state_summary" and len(df) > 27:
            fails.append(f"{len(df)} states > 27 Brazilian states")
        total_fail += len(fails)
        status = "OK  " if not fails else "FAIL"
        print(f"  [{status}] {name}  ({len(df):,} rows)")
        for f in fails:
            print(f"        - {f}")

    print("=" * 62)
    if total_fail:
        print(f"VALIDATION FAILED: {total_fail} issue(s).")
        sys.exit(1)
    print("VALIDATION PASSED: raw, staging, core, and marts all green.")


if __name__ == "__main__":
    main()
