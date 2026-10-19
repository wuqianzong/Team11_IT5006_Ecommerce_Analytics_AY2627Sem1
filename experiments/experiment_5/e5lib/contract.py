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

# Screening candidates (G-68): built in s02 and screened in s03 classification only; not predictors.
# A candidate enters the classification selection pool only if the team adopts it at the s03 gate
# (human_decisions.yaml). Order-level rule: the value of the primary item (highest price, then lowest
# order_item_id), as for primary_category. Catalogue fields are assumed fixed at checkout (limitation).
# CR-038 (G-69) adds the promise, region and seller-history groups. Each entry names its group (the s03
# card that screens it), its kind and the transform planned if it is adopted.
_LOG = "log1p if pre-cutoff skewness > 1, then scaled"
_ONEHOT = "one-hot (drop-first for linear/logistic), unknown level handled"
SCREENING_CANDIDATES = {
    "classification": {
        "product_photos_qty": {"group": "product", "kind": "numeric",
                               "source": "products.product_photos_qty of the primary item",
                               "transform": "scaled, never logged (count)"},
        "product_description_lenght": {"group": "product", "kind": "numeric",
                                       "source": "products.product_description_lenght of the primary item",
                                       "transform": _LOG},
        "product_name_lenght": {"group": "product", "kind": "numeric",
                                "source": "products.product_name_lenght of the primary item", "transform": _LOG},
        "est_delivery_days": {"group": "promise", "kind": "numeric",
                              "source": "orders.order_estimated_delivery_date - order_purchase_timestamp (days)",
                              "transform": _LOG + "; in production fed by the task 1 prediction, so if adopted the "
                                           "classifier trains on out-of-fold task 1 predictions (G-69)"},
        "customer_region": {"group": "region", "kind": "categorical",
                            "source": "IBGE macro-region of customer_state", "transform": _ONEHOT},
        "seller_region": {"group": "region", "kind": "categorical",
                          "source": "IBGE macro-region of primary_seller_state", "transform": _ONEHOT},
        "region_pair": {"group": "region", "kind": "categorical",
                        "source": "customer_region > seller_region (route between macro-regions)", "transform": _ONEHOT},
        "seller_prior_review_mean": {"group": "seller_history", "kind": "numeric",
                                     "source": "mean valid review score of the primary seller's earlier orders, reviews "
                                               "answered strictly before this purchase (own order excluded)",
                                     "transform": "scaled; missing for sellers without an earlier review (imputed in "
                                                  "folds with a missing indicator)"},
        "seller_prior_review_count": {"group": "seller_history", "kind": "numeric",
                                      "source": "number of those reviews", "transform": _LOG},
        "seller_prior_detractor_share": {"group": "seller_history", "kind": "numeric",
                                         "source": "share of those reviews with score <= 2",
                                         "transform": "scaled, never logged (share); missing as for the mean"},
        "seller_prior_delivered_count": {"group": "seller_history", "kind": "numeric",
                                         "source": "number of the primary seller's earlier orders delivered strictly "
                                                   "before this purchase", "transform": _LOG},
        "seller_prior_late_share": {"group": "seller_history", "kind": "numeric",
                                    "source": "share of those deliveries after their estimated delivery date",
                                    "transform": "scaled, never logged (share); missing when no earlier delivery"},
    },
}


def screening(task: str) -> tuple[str, ...]:
    return tuple(SCREENING_CANDIDATES.get(task, {}))


def screening_group(task: str, group: str) -> tuple[str, ...]:
    return tuple(c for c, m in SCREENING_CANDIDATES.get(task, {}).items() if m["group"] == group)


def all_screening() -> tuple[str, ...]:
    return tuple(dict.fromkeys(c for t in SCREENING_CANDIDATES.values() for c in t))


# Columns that are not in the contract, kept here so the reason stays documented.
NOT_IN_CONTRACT = {
    "has_items": "post-purchase leakage: encodes a later cancellation (G-30)",
    "freight_ratio_missing": "post-purchase leakage: encodes a later cancellation (G-30)",
    "payment_missing": "constant after the population rules: s02 2.11 removes orders without a usable payment (G-42, G-51)",
}


def adopted(task: str) -> tuple[str, ...]:
    """Screening candidates adopted into the task's selection pool at the s03 gate (G-70).

    Read from spec/human_decisions.yaml (s03_to_s04.<task>.adopted_candidates), the one place the
    team records the adoption; each name must be a screening candidate of that task.
    """
    import yaml

    from .paths import spec_path
    hd = yaml.safe_load(spec_path("human_decisions.yaml").read_text(encoding="utf-8")) or {}
    rows = ((hd.get("s03_to_s04") or {}).get(task) or {}).get("adopted_candidates") or []
    names = tuple(r["feature"] for r in rows)
    unknown = set(names) - set(screening(task))
    if unknown:
        raise ValueError(f"adopted_candidates for {task} are not screening candidates: {sorted(unknown)}")
    return names


def pool(task: str) -> tuple[str, ...]:
    """The task's selection pool for s04: the 24 contract predictors plus the adopted candidates.

    The single source every later stage uses for the feature set it may select from (G-70):
    regression = the 24; classification = the 24 + product_photos_qty, product_description_lenght,
    seller_prior_review_mean. s04 selects from this pool by the 99% threshold.
    """
    return tuple(PREDICTORS) + adopted(task)


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
    if set(all_screening()) & (set(PREDICTORS) | set(NOT_IN_CONTRACT)):
        problems.append("a screening candidate is already a predictor or listed as not in the contract")
    return problems
