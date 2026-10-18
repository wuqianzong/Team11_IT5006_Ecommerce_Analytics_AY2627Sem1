"""Predictor contract for Experiment 5 (s01 1.3; G-61, G-62).

Written for this experiment, not copied from Milestone 2: the 24 predictors every task may use,
their groups, which ones may take log1p, and the columns that are not in the contract and why.
s01 records these lists in spec/protocol.yaml; later stages read them from there. The feature
formulas live in the s02 feature code; this module only names and groups the columns.
"""
from __future__ import annotations

PREDICTORS = (
    # basket
    "n_items", "n_products", "n_sellers", "n_categories",
    # price and freight
    "total_price", "total_freight", "freight_ratio",
    # physical totals and missing fractions
    "total_weight_g", "total_volume_cm3", "weight_missing_fraction", "volume_missing_fraction",
    # product category
    "primary_category", "category_missing_fraction",
    # geography
    "customer_state", "primary_seller_state", "distance_km_max", "distance_missing_fraction",
    "interstate_share",
    # calendar (numeric, G-22)
    "purchase_month", "purchase_dayofweek", "purchase_hour",
    # payment
    "primary_payment_type", "payment_installments_max", "n_payment_methods",
)

CATEGORICAL = ("customer_state", "primary_seller_state", "primary_category", "primary_payment_type")
CALENDAR_NUMERIC = ("purchase_month", "purchase_dayofweek", "purchase_hour")
COUNTS = ("n_items", "n_products", "n_sellers", "n_categories", "n_payment_methods", "payment_installments_max")
SHARES = ("weight_missing_fraction", "volume_missing_fraction", "category_missing_fraction",
          "distance_missing_fraction", "interstate_share")

# log1p only when pre-cutoff skewness > 1 (s04 4.2). Missing values stay missing through log1p
# and are imputed afterwards; orders with a negative value here are removed in s02 (G-62).
LOG_CANDIDATES = ("total_price", "total_freight", "total_weight_g", "total_volume_cm3", "distance_km_max")
NEVER_LOGGED = {
    "freight_ratio": "team decision in the s01 review (G-62)",
    "counts": "integer counts (G-62)",
    "calendar fields": "numeric calendar positions (G-22, G-47)",
    "shares and fractions": "bounded 0-1 values (G-47)",
}

# Columns that are not in the contract, kept here so the reason stays documented.
NOT_IN_CONTRACT = {
    "has_items": "post-purchase leakage: encodes a later cancellation (G-30)",
    "freight_ratio_missing": "post-purchase leakage: encodes a later cancellation (G-30)",
    "payment_missing": "constant after the population rules: s02 2.11 removes orders without a usable payment (G-42, G-51)",
}


def numeric() -> tuple[str, ...]:
    return tuple(c for c in PREDICTORS if c not in CATEGORICAL)


def validate() -> list[str]:
    """Problems with the lists above; empty when the contract is consistent."""
    problems = []
    if len(PREDICTORS) != 24 or len(set(PREDICTORS)) != 24:
        problems.append("the contract must hold 24 distinct predictors")
    for name, group in (("CATEGORICAL", CATEGORICAL), ("CALENDAR_NUMERIC", CALENDAR_NUMERIC), ("COUNTS", COUNTS),
                        ("SHARES", SHARES), ("LOG_CANDIDATES", LOG_CANDIDATES)):
        if not set(group) <= set(PREDICTORS):
            problems.append(f"{name} names a column outside the contract")
    logged = set(LOG_CANDIDATES)
    if logged & set(CATEGORICAL + CALENDAR_NUMERIC + COUNTS + SHARES + ("freight_ratio",)):
        problems.append("a never-logged column is a log1p candidate")
    if set(NOT_IN_CONTRACT) & set(PREDICTORS):
        problems.append("a column is both in and out of the contract")
    return problems
