"""Deterministic base-table builder (feature_contract.md v1.2, Phase A).

Entrypoint: ``python -m src.features.build_features``

Reads ``data/preprocessed/*.csv`` (plus the pinned IBGE boundary under
``docs/references/geography/``) and writes, under ``data/business/ml/``:

    orders_ml_features.csv   one row per source order
    feature_schema.json      versioned column roles/types/units/formulas
    dataset_manifest.json    input hashes, config, row counts, content checksum
    zip_centroids.csv        polygon-filtered ZIP/state median lookup
    quality_report.json      contract checks, missingness, coverage, cohorts

No imputation, scaling, encoding or learned transform happens here; those are
training-fold operations. Run ``python -m src.features.create_splits`` afterwards
for the development/holdout and CV manifests.

Outputs are written to a staging directory and published only when every required
check passes, so a failed build leaves the previous published artifacts intact
(feature_contract.md §11.4). Generated CSVs use explicit LF line endings.
"""
from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from src.common.loaders import sha256_file, sha256_file_lf

from .aggregation import (
    aggregate_items,
    aggregate_payments,
    aggregate_reviews,
    resolve_english_category,
)
from .checks import run_fixture_checks
from .contract import (
    BASE_COLUMN_ORDER,
    CATEGORICAL_COLUMNS,
    CONTRACT_VERSION,
    FEATURE_SCHEMA,
    FEATURE_VERSION,
    NUMERIC_COLUMNS,
    PREDICTOR_ALLOWLIST,
    SPLIT_VERSION,
    UNKNOWN,
    normalize_state,
)
from .geography import (
    BOUNDARY_VERSION,
    build_zip_centroids,
    compute_distance_features,
    compute_geography_coverage,
    prepare_boundary,
)
from .serialization import write_csv_lf, write_text_lf

STAGING_DIR = "_staging"


# ---------------------------------------------------------------------------
# Loaders (explicit dtypes + date parsing for determinism)
# ---------------------------------------------------------------------------

def _load_orders(pre: Path) -> pd.DataFrame:
    return pd.read_csv(
        pre / "olist_orders_dataset.csv",
        usecols=["order_id", "customer_id", "order_status",
                 "order_purchase_timestamp", "order_delivered_customer_date"],
        dtype={"order_id": "str", "customer_id": "str", "order_status": "str"},
        parse_dates=["order_purchase_timestamp", "order_delivered_customer_date"],
    )


def _load_items(pre: Path) -> pd.DataFrame:
    return pd.read_csv(
        pre / "olist_order_items_dataset.csv",
        usecols=["order_id", "order_item_id", "product_id", "seller_id",
                 "price", "freight_value"],
        dtype={"order_id": "str", "product_id": "str", "seller_id": "str",
               "order_item_id": "int64", "price": "float64", "freight_value": "float64"},
    )


def _load_payments(pre: Path) -> pd.DataFrame:
    return pd.read_csv(
        pre / "olist_order_payments_dataset.csv",
        usecols=["order_id", "payment_sequential", "payment_type",
                 "payment_installments", "payment_value"],
        dtype={"order_id": "str", "payment_type": "str", "payment_sequential": "int64",
               "payment_installments": "float64", "payment_value": "float64"},
    )


def _load_reviews(pre: Path) -> pd.DataFrame:
    return pd.read_csv(
        pre / "olist_order_reviews_dataset.csv",
        usecols=["review_id", "order_id", "review_score", "review_answer_timestamp"],
        dtype={"review_id": "str", "order_id": "str", "review_score": "str"},
        parse_dates=["review_answer_timestamp"],
    )


def _load_customers(pre: Path) -> pd.DataFrame:
    return pd.read_csv(
        pre / "olist_customers_dataset.csv",
        usecols=["customer_id", "customer_unique_id", "customer_zip_code_prefix",
                 "customer_state"],
        dtype={"customer_id": "str", "customer_unique_id": "str", "customer_state": "str",
               "customer_zip_code_prefix": "str"},
    )


def _load_products(pre: Path) -> pd.DataFrame:
    return pd.read_csv(
        pre / "olist_products_dataset.csv",
        usecols=["product_id", "product_category_name", "product_weight_g",
                 "product_length_cm", "product_height_cm", "product_width_cm"],
        dtype={"product_id": "str", "product_category_name": "str",
               "product_weight_g": "float64", "product_length_cm": "float64",
               "product_height_cm": "float64", "product_width_cm": "float64"},
    )


def _load_sellers(pre: Path) -> pd.DataFrame:
    return pd.read_csv(
        pre / "olist_sellers_dataset.csv",
        usecols=["seller_id", "seller_zip_code_prefix", "seller_state"],
        dtype={"seller_id": "str", "seller_state": "str", "seller_zip_code_prefix": "str"},
    )


def _load_geolocation(pre: Path) -> pd.DataFrame:
    return pd.read_csv(
        pre / "olist_geolocation_dataset.csv",
        usecols=["geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng",
                 "geolocation_state"],
        dtype={"geolocation_state": "str", "geolocation_zip_code_prefix": "str",
               "geolocation_lat": "float64", "geolocation_lng": "float64"},
    )


def _load_translation(pre: Path) -> pd.DataFrame:
    return pd.read_csv(
        pre / "product_category_name_translation.csv",
        dtype={"product_category_name": "str", "product_category_name_english": "str"},
    )


def _assert_unique(df: pd.DataFrame, cols, label: str) -> None:
    sub = df[cols]
    if sub.duplicated().any():
        raise ValueError(f"{label}: duplicate key {list(cols)} found")
    if sub.isna().any().any():
        raise ValueError(f"{label}: null key {list(cols)} found")


# ---------------------------------------------------------------------------
# Reason-code assembly
# ---------------------------------------------------------------------------

def _join_reasons(ordered: list[tuple[str, np.ndarray]]) -> list[str]:
    parts = [np.where(mask, label, "") for label, mask in ordered]
    return [";".join(x for x in row if x) for row in zip(*parts)]


# ---------------------------------------------------------------------------
# Per-feature schema enrichment (source columns, grain, availability)
# ---------------------------------------------------------------------------

_FEATURE_META: dict[str, dict] = {
    "n_items": {"source_columns": ["order_item_id"], "grain": "order"},
    "has_items": {"source_columns": ["n_items"], "grain": "order"},
    "n_products": {"source_columns": ["product_id"], "grain": "order"},
    "n_sellers": {"source_columns": ["seller_id"], "grain": "order"},
    "n_categories": {"source_columns": ["english_category"], "grain": "order"},
    "total_price": {"source_columns": ["price"], "grain": "order"},
    "total_freight": {"source_columns": ["freight_value"], "grain": "order"},
    "freight_ratio": {"source_columns": ["total_freight", "total_price"], "grain": "order"},
    "freight_ratio_missing": {"source_columns": ["freight_ratio"], "grain": "order"},
    "total_weight_g": {"source_columns": ["product_weight_g"], "grain": "order"},
    "total_volume_cm3": {"source_columns": ["product_length_cm", "product_height_cm", "product_width_cm"], "grain": "order"},
    "weight_missing_fraction": {"source_columns": ["product_weight_g"], "grain": "order"},
    "volume_missing_fraction": {"source_columns": ["product_length_cm", "product_height_cm", "product_width_cm"], "grain": "order"},
    "primary_category": {"source_columns": ["english_category"], "grain": "order (primary item)"},
    "category_missing_fraction": {"source_columns": ["english_category"], "grain": "order"},
    "customer_state": {"source_columns": ["customer_state"], "grain": "customer"},
    "primary_seller_state": {"source_columns": ["seller_state"], "grain": "order (primary seller)"},
    "distance_km_max": {"source_columns": ["geolocation_lat", "geolocation_lng", "customer_zip_code_prefix", "customer_state", "seller_zip_code_prefix", "seller_state"], "grain": "order (distinct sellers)"},
    "distance_missing_fraction": {"source_columns": ["distance_km_max"], "grain": "order (distinct sellers)"},
    "interstate_share": {"source_columns": ["customer_state", "seller_state"], "grain": "order (distinct sellers)"},
    "purchase_month": {"source_columns": ["order_purchase_timestamp"], "grain": "order"},
    "purchase_dayofweek": {"source_columns": ["order_purchase_timestamp"], "grain": "order"},
    "purchase_hour": {"source_columns": ["order_purchase_timestamp"], "grain": "order"},
    "primary_payment_type": {"source_columns": ["payment_type", "payment_value"], "grain": "order"},
    "payment_installments_max": {"source_columns": ["payment_installments"], "grain": "order"},
    "n_payment_methods": {"source_columns": ["payment_type"], "grain": "order"},
    "payment_missing": {"source_columns": ["payment_type", "payment_value"], "grain": "order"},
}

_AVAILABILITY_DEFAULT = (
    "checkout-complete simulation: item/payment/catalogue snapshot availability assumed; "
    "payments have no event timestamps and catalogue attributes have no historical versions"
)
_AVAILABILITY = {
    "distance_km_max": "static IBGE BR_Pais_2024 boundary (2016-2018 orders); label-independent reference",
    "distance_missing_fraction": "static IBGE BR_Pais_2024 boundary (2016-2018 orders); label-independent reference",
    "purchase_month": "source clock convention; no timezone conversion",
    "purchase_dayofweek": "source clock convention; no timezone conversion",
    "purchase_hour": "source clock convention; no timezone conversion",
}


def _enriched_schema() -> dict:
    cols = []
    for c in FEATURE_SCHEMA:
        entry = dict(c)
        if c["role"] == "feature":
            meta = _FEATURE_META[c["name"]]
            entry["source_columns"] = meta["source_columns"]
            entry["aggregation_grain"] = meta["grain"]
            entry["availability_assumption"] = _AVAILABILITY.get(c["name"], _AVAILABILITY_DEFAULT)
        cols.append(entry)
    return {
        "version": FEATURE_VERSION,
        "contract_version": CONTRACT_VERSION,
        "predictor_allowlist": PREDICTOR_ALLOWLIST,
        "categorical_columns": CATEGORICAL_COLUMNS,
        "numeric_columns": NUMERIC_COLUMNS,
        "columns": cols,
    }


# ---------------------------------------------------------------------------
# Pure order-grain assembly (no file I/O)
# ---------------------------------------------------------------------------

def assemble_base(orders, customers, products, sellers, geolocation, translation,
                  items, payments, reviews, polygon) -> dict:
    """Assemble one order-grain base row per source order from typed tables.

    Pure with respect to the filesystem: it consumes typed tables and the validated
    boundary polygon and returns the base table plus intermediates. Keeping the
    join logic here (rather than buried behind loaders) makes it directly testable
    with the small Cartesian-join fixture (feature_contract.md §11.4).
    """
    # Key uniqueness (fail, never silently drop).
    _assert_unique(orders, "order_id", "orders")
    _assert_unique(customers, "customer_id", "customers")
    _assert_unique(products, "product_id", "products")
    _assert_unique(sellers, "seller_id", "sellers")
    _assert_unique(translation, "product_category_name", "translation")
    _assert_unique(items, ["order_id", "order_item_id"], "items")
    _assert_unique(payments, ["order_id", "payment_sequential"], "payments")

    # Boundary-filtered ZIP/state median lookup.
    centroids, geo_filter_report = build_zip_centroids(geolocation, polygon)

    # Categories, then order-grain aggregation (items / payments / reviews).
    products_cat = resolve_english_category(products, translation)
    item_agg, primary, order_seller_pairs = aggregate_items(products_cat, items)
    pay_agg = aggregate_payments(payments)
    rev_agg = aggregate_reviews(reviews)

    # Geography (distance/interstate) over distinct seller pairs.
    geo = compute_distance_features(orders, customers, sellers, order_seller_pairs, centroids)

    # Assemble one row per order.
    base = orders.merge(customers, on="customer_id", how="left", validate="many_to_one")
    base = base.merge(item_agg, left_on="order_id", right_index=True, how="left", validate="one_to_one")
    base = base.merge(
        primary[["primary_seller_id", "primary_category"]],
        left_on="order_id", right_index=True, how="left", validate="one_to_one")
    base = base.merge(pay_agg, left_on="order_id", right_index=True, how="left", validate="one_to_one")
    base = base.merge(rev_agg, left_on="order_id", right_index=True, how="left", validate="one_to_one")
    base = base.merge(geo, left_on="order_id", right_index=True, how="left", validate="one_to_one")

    # Defaults for orders with no items / payments / reviews.
    for col, default in [("n_items", 0), ("has_items", 0), ("n_products", 0),
                         ("n_sellers", 0), ("n_categories", 0),
                         ("seller_id_missing", 0), ("freight_ratio_missing", 1)]:
        base[col] = base[col].fillna(default)
    base["primary_category"] = base["primary_category"].fillna(UNKNOWN)
    base["primary_payment_type"] = base["primary_payment_type"].fillna(UNKNOWN)
    base["n_payment_methods"] = base["n_payment_methods"].fillna(0).astype(int)
    base["payment_missing"] = base["payment_missing"].fillna(1).astype(int)
    base["review_count"] = base["review_count"].fillna(0).astype(int)

    # seller_id_missing override: complete seller set unknown.
    missing_seller = base["seller_id_missing"] == 1
    base.loc[missing_seller, ["distance_km_max", "distance_missing_fraction", "interstate_share"]] = np.nan

    # States (normalized) + primary seller state.
    base["customer_state"] = base["customer_state"].map(normalize_state)
    seller_state_map = sellers.set_index("seller_id")["seller_state"].map(normalize_state)
    base["primary_seller_state"] = base["primary_seller_id"].map(seller_state_map).fillna(UNKNOWN)

    # Time-component features (categorical codes).
    pt = base["order_purchase_timestamp"]
    base["purchase_month"] = pt.dt.month
    base["purchase_dayofweek"] = pt.dt.dayofweek  # Monday=0
    base["purchase_hour"] = pt.dt.hour

    # Targets.
    delivered = base["order_delivered_customer_date"]
    elapsed = (delivered - pt).dt.total_seconds() / 86400.0
    lead_ok = (base["order_status"] == "delivered") & pt.notna() & delivered.notna() & (elapsed > 0)
    base["lead_days"] = np.where(lead_ok, elapsed, np.nan)
    base["regression_label_available_at"] = base["order_delivered_customer_date"].where(lead_ok)

    # Eligibility + exclusion reasons.
    group_resolved = base["customer_unique_id"].notna()
    pred_ok = pt.notna()

    reg_reasons = _join_reasons([
        ("not_delivered", (base["order_status"] != "delivered").to_numpy()),
        ("missing_delivery_timestamp",
         ((base["order_status"] == "delivered") & delivered.isna()).to_numpy()),
        ("missing_prediction_timestamp", (~pred_ok).to_numpy()),
        ("nonpositive_lead_days",
         ((base["order_status"] == "delivered") & pt.notna() & delivered.notna()
          & (elapsed <= 0)).to_numpy()),
        ("missing_customer_group", (~group_resolved).to_numpy()),
    ])
    cls_reasons = _join_reasons([
        ("missing_review_target", base["is_detractor"].isna().to_numpy()),
        ("missing_prediction_timestamp", (~pred_ok).to_numpy()),
        ("missing_customer_group", (~group_resolved).to_numpy()),
    ])

    base["regression_exclusion_reason"] = reg_reasons
    base["classification_exclusion_reason"] = cls_reasons
    base["eligible_regression"] = (base["regression_exclusion_reason"] == "").astype(int)
    base["eligible_classification"] = (base["classification_exclusion_reason"] == "").astype(int)

    # Rename prediction anchor and keep only the contracted column order.
    base = base.rename(columns={"order_purchase_timestamp": "prediction_timestamp"})
    base = base[BASE_COLUMN_ORDER]

    # Nullable integer targets back to Int64 (clean serialization).
    base["review_score_min"] = _to_int64(base["review_score_min"])
    base["is_detractor"] = _to_int64(base["is_detractor"])

    base = base.sort_values("order_id", kind="mergesort").reset_index(drop=True)
    return {
        "base": base,
        "centroids": centroids,
        "geo_filter_report": geo_filter_report,
        "polygon": polygon,
        "source": {
            "orders": orders, "items": items, "payments": payments, "reviews": reviews,
            "customers": customers, "products": products, "sellers": sellers,
            "geolocation": geolocation, "translation": translation,
        },
        "order_seller_pairs": order_seller_pairs,
    }


def build(repo_root: Path) -> dict:
    """Load preprocessed tables + the boundary, then assemble the base table."""
    pre = repo_root / "data" / "preprocessed"

    orders = _load_orders(pre)
    items = _load_items(pre)
    payments = _load_payments(pre)
    reviews = _load_reviews(pre)
    customers = _load_customers(pre)
    products = _load_products(pre)
    sellers = _load_sellers(pre)
    geolocation = _load_geolocation(pre)
    translation = _load_translation(pre)

    polygon, boundary_manifest = prepare_boundary(repo_root)

    built = assemble_base(orders, customers, products, sellers, geolocation,
                          translation, items, payments, reviews, polygon)
    built["boundary_manifest"] = boundary_manifest
    return built


def _to_int64(s: pd.Series) -> pd.Series:
    out = pd.Series(pd.NA, index=s.index, dtype="Int64")
    out[s.notna()] = pd.to_numeric(s[s.notna()], errors="coerce").astype("Int64")
    return out


# ---------------------------------------------------------------------------
# Serialization (to a caller-supplied directory, so staging is possible)
# ---------------------------------------------------------------------------

_DATE_COLS = ["prediction_timestamp", "regression_label_available_at",
              "review_latest_observed_at"]


def _serialize_date_col(df: pd.DataFrame, col: str) -> None:
    df[col] = [t.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(t) else "" for t in df[col]]


def export(repo_root: Path, built: dict, out_dir: Path, all_checks: list[dict]) -> None:
    """Write every artifact (base CSV, lookup, schema, manifests, report) to out_dir."""
    base = built["base"]
    centroids = built["centroids"]
    boundary_manifest = built["boundary_manifest"]

    # Fixed column order + date serialization, then LF CSV.
    out = base.copy()
    for col in _DATE_COLS:
        _serialize_date_col(out, col)
    csv_path = out_dir / "orders_ml_features.csv"
    write_csv_lf(out, csv_path)

    write_csv_lf(centroids, out_dir / "zip_centroids.csv")

    write_text_lf(json.dumps(_enriched_schema(), indent=2) + "\n",
                  out_dir / "feature_schema.json")

    # Input hashes (content identity) + boundary provenance. Inputs are hashed
    # LF-normalized so the recorded identity is checkout-line-ending independent.
    pre = repo_root / "data" / "preprocessed"
    input_names = [
        "olist_orders_dataset.csv", "olist_order_items_dataset.csv",
        "olist_order_payments_dataset.csv", "olist_order_reviews_dataset.csv",
        "olist_customers_dataset.csv", "olist_products_dataset.csv",
        "olist_sellers_dataset.csv", "olist_geolocation_dataset.csv",
        "product_category_name_translation.csv",
    ]
    input_hashes = {n: sha256_file_lf(pre / n) for n in input_names}

    manifest = {
        "feature_version": FEATURE_VERSION,
        "contract_version": CONTRACT_VERSION,
        "split_version": SPLIT_VERSION,
        "config": {
            "earth_radius_km": 6371.0,
            "usable_payment_types": sorted(["credit_card", "boleto", "voucher", "debit_card"]),
            "boundary_product": boundary_manifest["product"],
            "boundary_version": BOUNDARY_VERSION,
            "boundary_archive_sha256": boundary_manifest["archive_sha256"],
            "boundary_derived_geometry_sha256": boundary_manifest["derived_geometry_sha256"],
            "source_crs": boundary_manifest["original_crs"],
            "target_crs": boundary_manifest["target_crs"],
            "library_versions": boundary_manifest["library_versions"],
        },
        "input_hashes": input_hashes,
        "row_counts": {
            "source_orders": int(len(built["source"]["orders"])),
            "output_orders": int(len(base)),
            "orders_with_items": int((base["has_items"] == 1).sum()),
            "eligible_regression": int(base["eligible_regression"].sum()),
            "eligible_classification": int(base["eligible_classification"].sum()),
        },
        "content_checksum": sha256_file(csv_path),
        "zip_centroids_sha256": sha256_file(out_dir / "zip_centroids.csv"),
        "content_hash_algorithm": "sha256",
        "newline_convention": "LF",
        "run_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    write_text_lf(json.dumps(manifest, indent=2) + "\n",
                  out_dir / "dataset_manifest.json")

    write_text_lf(json.dumps(_quality_report_payload(built, all_checks), indent=2) + "\n",
                  out_dir / "quality_report.json")


# ---------------------------------------------------------------------------
# Data-level checks + quality report
# ---------------------------------------------------------------------------

def _data_checks(built: dict) -> list[dict]:
    base = built["base"]
    src = built["source"]
    results = []

    def add(fid, ok, detail):
        results.append({"id": fid, "status": "pass" if ok else "fail", "detail": detail})

    add("one_row_per_order", len(base) == len(src["orders"]),
        f"{len(base)} output rows vs {len(src['orders'])} source orders")
    add("unique_nonnull_order_id", base["order_id"].notna().all() and base["order_id"].is_unique,
        "order_id unique and non-null")
    add("join_cardinality_items",
        (base["has_items"] == 1).sum() == src["items"]["order_id"].nunique(),
        "orders with items match distinct item order_ids")
    add("has_items_coherent",
        ((base["has_items"] == 1) == (base["n_items"] > 0)).all(),
        "has_items == int(n_items > 0) for every row")
    add("review_label_null_iff_no_valid_score",
        (base["is_detractor"].isna() == base["review_score_min"].isna()).all(),
        "is_detractor null exactly when no valid review score (invalid-only reviews stay null)")
    add("no_review_implies_null_label",
        ((base["review_count"] > 0) | base["is_detractor"].isna()).all(),
        "every order with zero reviews has a null detractor label")
    add("delivered_unreviewed_is_regression_candidate",
        bool(((base["order_status"] == "delivered") & base["review_count"].eq(0)
              & base["eligible_regression"].eq(1)).any()),
        "some delivered unreviewed orders are regression-eligible")
    add("reviewed_nondelivered_is_classification_candidate",
        bool(((base["order_status"] != "delivered") & base["review_count"].gt(0)
              & base["eligible_classification"].eq(1)).any()),
        "some reviewed non-delivered orders are classification-eligible")
    add("freight_ratio_missing_coherent",
        (base["freight_ratio_missing"] == base["freight_ratio"].isna().astype(int)).all(),
        "freight_ratio_missing == int(freight_ratio is null)")
    add("payment_missing_coherent",
        (base["payment_missing"] == (base["primary_payment_type"] == UNKNOWN).astype(int)).all(),
        "payment_missing == int(primary_payment_type is Unknown)")

    return results


def _missingness(base: pd.DataFrame) -> dict:
    return {c: int(base[c].isna().sum()) for c in PREDICTOR_ALLOWLIST}


def _cohort_counts(base: pd.DataFrame) -> dict:
    return {
        "orders": int(len(base)),
        "delivered": int((base["order_status"] == "delivered").sum()),
        "with_items": int((base["has_items"] == 1).sum()),
        "multi_item": int((base["n_items"] > 1).sum()),
        "multi_seller": int((base["n_sellers"] > 1).sum()),
        "with_review": int((base["review_count"] > 0).sum()),
        "detractor": int((base["is_detractor"] == 1).sum()),
        "non_detractor": int((base["is_detractor"] == 0).sum()),
        "eligible_regression": int(base["eligible_regression"].sum()),
        "eligible_classification": int(base["eligible_classification"].sum()),
        "regression_exclusions": base["regression_exclusion_reason"].value_counts().to_dict(),
        "classification_exclusions": base["classification_exclusion_reason"].value_counts().to_dict(),
    }


def _quality_report_payload(built: dict, all_checks: list[dict]) -> dict:
    base = built["base"]
    centroids = built["centroids"]
    src = built["source"]
    bm = built["boundary_manifest"]

    coverage = compute_geography_coverage(
        src["geolocation"], src["customers"], src["sellers"], centroids)

    resolved = centroids[centroids["resolution_status"] == "resolved"]

    # Zero/one/multiple-seller order counts with denominator.
    with_items = base["has_items"] == 1
    n_with_items = int(with_items.sum())
    seller_order_counts = {
        "zero_seller": int((with_items & (base["n_sellers"] == 0)).sum()),
        "one_seller": int((with_items & (base["n_sellers"] == 1)).sum()),
        "multi_seller": int((with_items & (base["n_sellers"] > 1)).sum()),
        "denominator_with_items": n_with_items,
    }

    # Order distance completeness.
    dist_resolved = int(base["distance_km_max"].notna().sum())
    dist_missing = int(base["distance_km_max"].isna().sum())
    dist_total = dist_resolved + dist_missing
    order_distance_completeness = {
        "resolved": dist_resolved,
        "missing": dist_missing,
        "fraction_resolved": (dist_resolved / dist_total) if dist_total else None,
    }

    # Distance missingness by state and task eligibility.
    distance_missingness = {}
    for task, elig_col in [("regression", "eligible_regression"),
                           ("classification", "eligible_classification")]:
        sub = base[base[elig_col] == 1]
        if len(sub):
            g = sub.groupby("customer_state")["distance_km_max"].agg(
                total="size", missing=lambda s: int(s.isna().sum()))
            g = g.assign(missing_fraction=g["missing"] / g["total"])
            distance_missingness[task] = g.reset_index().to_dict(orient="records")
        else:
            distance_missingness[task] = []

    return {
        "checks": all_checks,
        "checks_summary": {
            "passed": sum(1 for c in all_checks if c["status"] == "pass"),
            "failed": sum(1 for c in all_checks if c["status"] == "fail"),
        },
        "geography": {
            "boundary": {
                "product": bm.get("product"),
                "boundary_version": BOUNDARY_VERSION,
                "archive_sha256": bm.get("archive_sha256"),
                "derived_geometry_sha256": bm.get("derived_geometry_sha256"),
                "original_crs": bm.get("original_crs"),
                "target_crs": bm.get("target_crs"),
                "library_versions": bm.get("library_versions"),
            },
            "reference_filter": built["geo_filter_report"],
            "keys": {
                "total_keys": int(len(centroids)),
                "zero_survivor_keys": int((centroids["resolution_status"] == "no_surviving_coordinates").sum()),
                "out_of_country_median_keys": int((centroids["resolution_status"] == "median_outside_polygon").sum()),
                "resolved_keys": int(len(resolved)),
            },
            "coverage": coverage,
            "seller_order_counts": seller_order_counts,
            "order_distance_completeness": order_distance_completeness,
            "distance_missingness_by_state_eligibility": distance_missingness,
        },
        "cohort_counts": _cohort_counts(base),
        "predictor_missingness": _missingness(base),
        "deferred_checks": [
            "pipeline_fit_fold_only", "history_fixture", "temporal_fixture",
            "cascade_fixture", "reload_pipeline_threshold",
        ],
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def publish_atomic(staging: Path, target: Path, replace=os.replace) -> None:
    """Publish every staged file into ``target``, rolling back on any failure.

    Backs up each pre-existing target file in memory before replacing it; if any
    replacement raises, every already-replaced file is restored (or removed, when
    it did not exist before) and the error is re-raised, so the target directory
    is never left in a partially-updated state (feature_contract.md §11.4).
    """
    files = sorted(staging.iterdir())
    backups: dict[str, bytes] = {}
    replaced: list[str] = []
    try:
        for f in files:
            dst = target / f.name
            if dst.exists():
                backups[f.name] = dst.read_bytes()
            replace(f, dst)
            replaced.append(f.name)
    except Exception:
        for name in reversed(replaced):
            dst = target / name
            if name in backups:
                dst.write_bytes(backups[name])
            else:
                dst.unlink(missing_ok=True)
        raise


def main() -> None:
    repo = _repo_root()
    ml = repo / "data" / "business" / "ml"
    staging = ml / STAGING_DIR

    built = build(repo)

    # Fixture checks run against the prepared boundary + real export columns.
    fixture_results = run_fixture_checks(built["polygon"], BASE_COLUMN_ORDER)
    data_checks = _data_checks(built)
    all_checks = fixture_results + data_checks

    # Write everything to staging; publish only if every required check passes.
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    export(repo, built, staging, all_checks)

    failed = [c for c in all_checks if c["status"] == "fail"]
    if failed:
        raise RuntimeError(
            "Required checks failed; previous published outputs left intact.\n"
            + "\n".join(f"- {c['id']}: {c['detail']}" for c in failed))

    # Publish the complete bundle atomically (rollback on interrupted writes),
    # then clean staging.
    publish_atomic(staging, ml)
    staging.rmdir()

    base = built["base"]
    print("build_features complete.")
    print(f"  orders:      {len(base)} rows -> {ml / 'orders_ml_features.csv'}")
    print(f"  centroids:   {len(built['centroids'])} keys -> {ml / 'zip_centroids.csv'}")
    print(f"  eligible_regression:    {int(base['eligible_regression'].sum())}")
    print(f"  eligible_classification: {int(base['eligible_classification'].sum())}")
    print(f"  checks: {sum(1 for c in all_checks if c['status']=='pass')}/"
          f"{len(all_checks)} passed (see quality_report.json)")


if __name__ == "__main__":
    main()
