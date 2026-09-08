"""Data contracts for the core and business-mart layers.

Mirrors ``schemas.py`` (which owns raw/staging) for the canonical core facts and
dimensions (docs/data_architecture.md §4.3) and the presentation-ready marts
(§4.4). Each table records its grain, primary key, and exact column order; the
builder and validator both read these so a contract is defined once.

The core layer stores *canonical* source columns only. Derived outcomes
(delivery_days, is_late, is_on_time, ...) are forbidden here and belong to the
descriptive business marts (§4.5 / §8 Milestone 1).
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Core: canonical facts and dimensions (one table per entity, explicit grain).
# ---------------------------------------------------------------------------
CORE_SCHEMAS: dict[str, dict] = {
    "fact_orders": {
        "grain": "one row per order_id",
        "primary_key": ["order_id"],
        "columns": [
            "order_id", "customer_id", "order_status",
            "order_purchase_timestamp", "order_approved_at",
            "order_delivered_carrier_date", "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    },
    "fact_order_items": {
        "grain": "one row per (order_id, order_item_id)",
        "primary_key": ["order_id", "order_item_id"],
        "columns": [
            "order_id", "order_item_id", "product_id", "seller_id",
            "shipping_limit_date", "price", "freight_value",
        ],
    },
    "fact_payments": {
        "grain": "one row per source payment record",
        "primary_key": ["order_id", "payment_sequential"],
        "columns": [
            "order_id", "payment_sequential", "payment_type",
            "payment_installments", "payment_value",
        ],
    },
    "fact_reviews": {
        "grain": "one row per review record",
        "primary_key": [],  # review_id is NOT unique in the source
        "columns": [
            "review_id", "order_id", "review_score",
            "review_comment_title", "review_comment_message",
            "review_creation_date", "review_answer_timestamp",
        ],
    },
    "dim_customers": {
        "grain": "one row per customer_id (customer_unique_id is the rollup key)",
        "primary_key": ["customer_id"],
        "columns": [
            "customer_id", "customer_unique_id", "customer_zip_code_prefix",
            "customer_city", "customer_state",
        ],
    },
    "dim_products": {
        "grain": "one row per product_id",
        "primary_key": ["product_id"],
        "columns": [
            "product_id", "product_category_name", "product_category_name_english",
            "product_name_lenght", "product_description_lenght",
            "product_photos_qty", "product_weight_g", "product_length_cm",
            "product_height_cm", "product_width_cm",
        ],
    },
    "dim_sellers": {
        "grain": "one row per seller_id",
        "primary_key": ["seller_id"],
        "columns": [
            "seller_id", "seller_zip_code_prefix", "seller_city", "seller_state",
        ],
    },
    "dim_geography": {
        "grain": "one row per geolocation_zip_code_prefix (Brazil-filtered)",
        "primary_key": ["geolocation_zip_code_prefix"],
        "columns": [
            "geolocation_zip_code_prefix", "geolocation_state", "geolocation_city",
            "centroid_lat", "centroid_lng", "n_records",
        ],
    },
}

CORE_ORDER: list[str] = [
    "fact_orders", "fact_order_items", "fact_payments", "fact_reviews",
    "dim_customers", "dim_products", "dim_sellers", "dim_geography",
]

# Referential integrity: (fact_table, fk_col) -> (dim_table, pk_col).
# Every fact foreign key must resolve to a dimension primary key.
REFERENTIAL_INTEGRITY: list[tuple[tuple[str, str], tuple[str, str]]] = [
    (("fact_orders", "customer_id"), ("dim_customers", "customer_id")),
    (("fact_order_items", "order_id"), ("fact_orders", "order_id")),
    (("fact_order_items", "product_id"), ("dim_products", "product_id")),
    (("fact_order_items", "seller_id"), ("dim_sellers", "seller_id")),
    (("fact_payments", "order_id"), ("fact_orders", "order_id")),
    (("fact_reviews", "order_id"), ("fact_orders", "order_id")),
]

# ---------------------------------------------------------------------------
# Marts: presentation-ready tables (flat, dashboard reads these, not joins).
# ---------------------------------------------------------------------------
MART_SCHEMAS: dict[str, dict] = {
    "mart_order_dashboard": {
        "grain": "one row per order",
        "primary_key": ["order_id"],
        "columns": [
            "order_id", "customer_id", "order_status", "order_purchase_timestamp",
            "order_delivered_customer_date", "order_estimated_delivery_date",
            "customer_unique_id", "customer_city", "customer_state",
            "order_item_count", "order_price_total", "order_freight_total",
            "order_value_total", "distinct_categories", "top_category",
            "review_score", "review_creation_date", "payment_value_total",
            "payment_installments_max", "payment_count", "payment_type_primary",
            "has_review", "order_purchase_date", "year", "month", "year_month",
            "day_of_week", "day_name", "hour", "delivery_days", "late_days",
            "is_on_time", "is_late",
        ],
    },
    "mart_order_items": {
        "grain": "one row per (order_id, order_item_id)",
        "primary_key": ["order_id", "order_item_id"],
        "columns": [
            "order_id", "order_item_id", "product_id", "seller_id",
            "shipping_limit_date", "price", "freight_value",
            "product_category_name", "product_category_name_english",
            "product_weight_g", "customer_id", "order_status",
            "order_purchase_timestamp", "order_delivered_customer_date",
            "order_estimated_delivery_date", "customer_unique_id",
            "customer_city", "customer_state", "seller_city", "seller_state",
            "review_score", "review_creation_date", "payment_value_total",
            "payment_installments_max", "payment_count", "payment_type_primary",
            "order_purchase_date", "year", "month", "year_month",
            "day_of_week", "day_name", "hour", "delivery_days", "late_days",
            "is_on_time", "is_late", "item_value",
        ],
    },
    "mart_category_daily": {
        "grain": "one row per (order_purchase_date, product_category_name_english)",
        "primary_key": ["order_purchase_date", "product_category_name_english"],
        "columns": [
            "order_purchase_date", "product_category_name_english", "n_orders",
            "items_sold", "revenue", "avg_price", "avg_freight", "n_delivered",
            "n_on_time", "n_reviews", "sum_review_score", "n_1_2_star",
            "n_customers",
        ],
    },
    "mart_state_summary": {
        "grain": "one row per state",
        "primary_key": ["state"],
        "columns": [
            "state", "state_name", "lat", "lng", "zip_prefix_count",
            "n_orders", "total_value", "avg_delivery_days", "on_time_rate",
        ],
    },
    "mart_data_quality": {
        "grain": "one row per materialized table",
        "primary_key": ["layer", "table"],
        "columns": [
            "layer", "table", "grain", "rows", "primary_key",
            "pk_unique", "status",
        ],
    },
}

MART_ORDER: list[str] = [
    "mart_order_dashboard", "mart_order_items", "mart_category_daily",
    "mart_state_summary", "mart_data_quality",
]
