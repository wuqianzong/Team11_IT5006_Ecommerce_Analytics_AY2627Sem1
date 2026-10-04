"""Constants and column contracts for the ML base table.

This mirrors ``data/business/ml/feature_contract.md`` (v1.2). The 27-column
predictor allowlist and base feature definitions remain v1.1; the contract
version is tracked separately from the feature and split versions. Targets,
identifiers, eligibility and audit columns are declared with explicit roles so
that training never infers predictors by dropping a target or selecting "all
numeric columns".
"""
from __future__ import annotations

import pandas as pd

# ---------------------------------------------------------------------------
# Frozen constants
# ---------------------------------------------------------------------------

# 27 Brazilian federative-unit codes (feature_contract.md §4 geography step 2).
VALID_STATES = frozenset({
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG",
    "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
})

# Usable payment types (feature_contract.md §4). Normalized lowercase + trimmed.
USABLE_PAYMENT_TYPES = frozenset({"credit_card", "boleto", "voucher", "debit_card"})

UNKNOWN = "Unknown"

# Version strings shared across artifacts (build + splits). Base features stay
# v1.1; the contract revision and the corrected split manifest are versioned
# separately and explicitly (feature_contract.md header + README Phase A step 3).
FEATURE_VERSION = "v1.1"
CONTRACT_VERSION = "v1.2"
SPLIT_VERSION = "v1.1"


def normalize_state(value) -> str:
    """Normalize a Brazilian UF code; return ``UNKNOWN`` for anything invalid."""
    if value is None:
        return UNKNOWN
    if isinstance(value, float) and pd.isna(value):
        return UNKNOWN
    s = str(value).strip().upper()
    return s if s in VALID_STATES else UNKNOWN

# Exact 27-column predictor allowlist, in the contract's frozen order.
PREDICTOR_ALLOWLIST = [
    "n_items", "has_items", "n_products", "n_sellers", "n_categories",
    "total_price", "total_freight", "freight_ratio", "freight_ratio_missing",
    "total_weight_g", "total_volume_cm3", "weight_missing_fraction",
    "volume_missing_fraction", "primary_category", "category_missing_fraction",
    "customer_state", "primary_seller_state", "distance_km_max",
    "distance_missing_fraction", "interstate_share",
    "purchase_month", "purchase_dayofweek", "purchase_hour",
    "primary_payment_type", "payment_installments_max", "n_payment_methods",
    "payment_missing",
]

# Categorical predictors (downstream OHE with handle_unknown='ignore').
CATEGORICAL_COLUMNS = [
    "customer_state", "primary_seller_state", "primary_category",
    "primary_payment_type", "purchase_month", "purchase_dayofweek", "purchase_hour",
]

# Numeric predictors = allowlist minus categoricals.
NUMERIC_COLUMNS = [c for c in PREDICTOR_ALLOWLIST if c not in CATEGORICAL_COLUMNS]

# ---------------------------------------------------------------------------
# Base-table column roles (export order for orders_ml_features.csv)
# ---------------------------------------------------------------------------

IDENTIFIER_COLUMNS = ["order_id", "customer_id", "customer_unique_id"]
TARGET_COLUMNS = ["lead_days", "review_score_min", "is_detractor"]
ELIGIBILITY_COLUMNS = ["eligible_regression", "eligible_classification"]
AUDIT_COLUMNS = [
    "prediction_timestamp", "order_status",
    "regression_exclusion_reason", "classification_exclusion_reason",
    "regression_label_available_at", "review_latest_observed_at",
    "review_count", "seller_id_missing",
]

# Export order: identifiers, audit anchor, targets, eligibility, audit, features.
BASE_COLUMN_ORDER = (
    ["order_id", "customer_id", "customer_unique_id",
     "prediction_timestamp", "order_status",
     "lead_days", "review_score_min", "is_detractor",
     "eligible_regression", "eligible_classification",
     "regression_exclusion_reason", "classification_exclusion_reason",
     "regression_label_available_at", "review_latest_observed_at",
     "review_count", "seller_id_missing"]
    + PREDICTOR_ALLOWLIST
)

# ---------------------------------------------------------------------------
# Per-column schema (serialized to feature_schema.json)
# ---------------------------------------------------------------------------

def _role(role: str, **kw) -> dict:
    d = {"role": role}
    d.update(kw)
    return d


FEATURE_SCHEMA = [
    _role("identifier", name="order_id", dtype="string",
          description="Source order key; unique non-null; audit/join only."),
    _role("identifier", name="customer_id", dtype="string",
          description="Session key; audit/join only, never a predictor."),
    _role("identifier", name="customer_unique_id", dtype="string",
          description="Persistent customer key used for CV grouping."),
    _role("audit", name="prediction_timestamp", dtype="datetime",
          description="Checkout cutoff anchor (order_purchase_timestamp); splitting only."),
    _role("audit", name="order_status", dtype="string",
          description="Final source status; audit only, never a predictor."),
    _role("target", name="lead_days", dtype="float", unit="days",
          description="(delivered - purchase) seconds / 86400; delivered + strictly positive."),
    _role("target_source", name="review_score_min", dtype="int",
          description="Minimum valid score 1-5 across supplied reviews; null if none."),
    _role("target", name="is_detractor", dtype="int",
          description="1 if review_score_min <= 2; 0 if >= 3; null if no valid score."),
    _role("eligibility", name="eligible_regression", dtype="int",
          description="Delivered + valid positive lead_days + valid prediction time + resolved group."),
    _role("eligibility", name="eligible_classification", dtype="int",
          description="Valid review target + valid prediction time + resolved group; delivery not required."),
    _role("audit", name="regression_exclusion_reason", dtype="string",
          description="Ordered reason codes for regression ineligibility."),
    _role("audit", name="classification_exclusion_reason", dtype="string",
          description="Ordered reason codes for classification ineligibility."),
    _role("audit", name="regression_label_available_at", dtype="datetime",
          description="Customer delivery timestamp for valid regression outcomes."),
    _role("audit", name="review_latest_observed_at", dtype="datetime",
          description="Max valid answer timestamp across contributing valid reviews."),
    _role("audit", name="review_count", dtype="int",
          description="Number of review records for the order."),
    _role("audit", name="seller_id_missing", dtype="int",
          description="Any item seller_id missing -> complete seller set unknown."),

    _role("feature", name="n_items", dtype="int", phase="base",
          description="Count of item rows per order."),
    _role("feature", name="has_items", dtype="int", phase="base",
          description="int(n_items > 0)."),
    _role("feature", name="n_products", dtype="int", phase="base",
          description="Distinct non-null product_id among items."),
    _role("feature", name="n_sellers", dtype="int", phase="base",
          description="Distinct non-null seller_id among items."),
    _role("feature", name="n_categories", dtype="int", phase="base",
          description="Distinct resolved translated English categories, excluding Unknown."),
    _role("feature", name="total_price", dtype="float", unit="BRL", phase="base",
          description="Sum item price, each item once."),
    _role("feature", name="total_freight", dtype="float", unit="BRL", phase="base",
          description="Sum item freight_value, each item once."),
    _role("feature", name="freight_ratio", dtype="float", phase="base",
          description="total_freight / total_price; null if denominator <= 0 or either missing."),
    _role("feature", name="freight_ratio_missing", dtype="int", phase="base",
          description="int(freight_ratio is null)."),
    _role("feature", name="total_weight_g", dtype="float", unit="g", phase="base",
          description="Sum product_weight_g; null if any item weight invalid/missing or no items."),
    _role("feature", name="total_volume_cm3", dtype="float", unit="cm^3", phase="base",
          description="Sum length*height*width; null if any item volume unknown or no items."),
    _role("feature", name="weight_missing_fraction", dtype="float", phase="base",
          description="Invalid/unknown item weights / n_items; null if no items."),
    _role("feature", name="volume_missing_fraction", dtype="float", phase="base",
          description="Invalid/unknown item volumes / n_items; null if no items."),
    _role("feature", name="primary_category", dtype="string", phase="base",
          description="English category of the deterministic primary item."),
    _role("feature", name="category_missing_fraction", dtype="float", phase="base",
          description="Fraction of items lacking a resolved category; null if no items."),
    _role("feature", name="customer_state", dtype="string", phase="base",
          description="Customer state, normalized; invalid -> Unknown."),
    _role("feature", name="primary_seller_state", dtype="string", phase="base",
          description="Seller state of the primary item; Unknown for absent/unresolved."),
    _role("feature", name="distance_km_max", dtype="float", unit="km", phase="base",
          description="Max Haversine distance from customer to each distinct seller."),
    _role("feature", name="distance_missing_fraction", dtype="float", phase="base",
          description="Distinct sellers with unresolved distance / n_sellers; null if no sellers."),
    _role("feature", name="interstate_share", dtype="float", phase="base",
          description="Fraction of distinct sellers whose state differs from customer state."),
    _role("feature", name="purchase_month", dtype="int", phase="base",
          description="Purchase month 1-12, categorical."),
    _role("feature", name="purchase_dayofweek", dtype="int", phase="base",
          description="Purchase day of week 0-6 (Monday=0), categorical."),
    _role("feature", name="purchase_hour", dtype="int", phase="base",
          description="Purchase hour 0-23, categorical."),
    _role("feature", name="primary_payment_type", dtype="string", phase="base",
          description="Payment type with largest summed value; ties lexicographic; Unknown if none usable."),
    _role("feature", name="payment_installments_max", dtype="int", phase="base",
          description="Max positive recorded installments across usable payment rows."),
    _role("feature", name="n_payment_methods", dtype="int", phase="base",
          description="Distinct usable payment types."),
    _role("feature", name="payment_missing", dtype="int", phase="base",
          description="int(no usable payment rows)."),
]


def role_map() -> dict[str, str]:
    """column name -> role."""
    return {c["name"]: c["role"] for c in FEATURE_SCHEMA}
