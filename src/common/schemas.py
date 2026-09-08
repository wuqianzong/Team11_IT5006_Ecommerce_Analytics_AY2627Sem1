"""Data contracts for the raw and staging layers.

Single source of truth for the nine Olist source tables: their raw filenames,
column dtypes, primary keys, accepted categorical values, and plausible numeric
ranges. Both the staging builder and the validator read these definitions, so a
contract is defined once and enforced everywhere.

See docs/data_architecture.md §4.1 (raw) and §4.2 (staging).

dtype markers used below:
    "string"   -> nullable string (missing preserved as <NA>)
    "int64"    -> 64-bit integer (only for columns with no missing values)
    "float64"  -> 64-bit float
    "datetime" -> datetime64[ns]
    "category" -> pandas categorical (low-cardinality value domain)
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Accepted categorical / value domains (docs/data_architecture.md §7)
# ---------------------------------------------------------------------------
BR_STATES: frozenset[str] = frozenset({
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA",
    "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN",
    "RO", "RR", "RS", "SC", "SE", "SP", "TO",
})

ORDER_STATUS: frozenset[str] = frozenset({
    "approved", "canceled", "created", "delivered", "invoiced",
    "processing", "shipped", "unavailable",
})

PAYMENT_TYPE: frozenset[str] = frozenset({
    "boleto", "credit_card", "debit_card", "not_defined", "voucher",
})

REVIEW_SCORE: frozenset[int] = frozenset({1, 2, 3, 4, 5})

# Brazilian state abbreviation -> full name (reference lookup for geography).
BR_STATE_NAMES: dict[str, str] = {
    "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas",
    "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal",
    "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão",
    "MT": "Mato Grosso", "MS": "Mato Grosso do Sul", "MG": "Minas Gerais",
    "PA": "Pará", "PB": "Paraíba", "PR": "Paraná", "PE": "Pernambuco",
    "PI": "Piauí", "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte",
    "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima",
    "SC": "Santa Catarina", "SP": "São Paulo", "SE": "Sergipe",
    "TO": "Tocantins",
}

# ---------------------------------------------------------------------------
# Per-table staging contracts.
# Column order in ``dtypes`` is the canonical staging column order.
# ---------------------------------------------------------------------------
SCHEMAS: dict[str, dict] = {
    "orders": {
        "raw_file": "olist_orders_dataset.csv",
        "primary_key": ["order_id"],
        "dtypes": {
            "order_id": "string",
            "customer_id": "string",
            "order_status": "category",
            "order_purchase_timestamp": "datetime",
            "order_approved_at": "datetime",
            "order_delivered_carrier_date": "datetime",
            "order_delivered_customer_date": "datetime",
            "order_estimated_delivery_date": "datetime",
        },
        "categorical": {"order_status": ORDER_STATUS},
        "ranges": {},
        "notes": "Delivery/approval dates are legitimately missing for orders not "
                 "yet approved or delivered.",
    },
    "order_items": {
        "raw_file": "olist_order_items_dataset.csv",
        "primary_key": ["order_id", "order_item_id"],
        "dtypes": {
            "order_id": "string",
            "order_item_id": "int64",
            "product_id": "string",
            "seller_id": "string",
            "shipping_limit_date": "datetime",
            "price": "float64",
            "freight_value": "float64",
        },
        "categorical": {},
        "ranges": {
            "order_item_id": (1, 100),
            "price": (0.0, None),
            "freight_value": (0.0, None),
        },
        "notes": "Grain = one row per (order_id, order_item_id). Four rows have "
                 "anomalous shipping_limit_date values in Feb-Apr 2020 (outside the "
                 "2016-2018 window); retained to preserve grain.",
    },
    "payments": {
        "raw_file": "olist_order_payments_dataset.csv",
        "primary_key": ["order_id", "payment_sequential"],
        "dtypes": {
            "order_id": "string",
            "payment_sequential": "int64",
            "payment_type": "category",
            "payment_installments": "int64",
            "payment_value": "float64",
        },
        "categorical": {"payment_type": PAYMENT_TYPE},
        "ranges": {
            "payment_sequential": (1, 100),
            "payment_installments": (0, 100),
            "payment_value": (0.0, None),
        },
        "notes": "Grain = one row per (order_id, payment_sequential). An order may "
                 "have several payment records. payment_installments is 0 for two "
                 "records (boleto/not_defined); its minimum is 0, not 1.",
    },
    "reviews": {
        "raw_file": "olist_order_reviews_dataset.csv",
        "primary_key": [],
        "dtypes": {
            "review_id": "string",
            "order_id": "string",
            "review_score": "int64",
            "review_comment_title": "string",
            "review_comment_message": "string",
            "review_creation_date": "datetime",
            "review_answer_timestamp": "datetime",
        },
        "categorical": {},
        "ranges": {"review_score": (1, 5)},
        "notes": "Grain = one row per review record (source rows). review_id is "
                 "NOT unique in the source: 789 ids repeat across 1,603 rows, so no "
                 "primary key is enforced here. Comment title/message are frequently "
                 "empty (preserved as <NA>).",
    },
    "customers": {
        "raw_file": "olist_customers_dataset.csv",
        "primary_key": ["customer_id"],
        "dtypes": {
            "customer_id": "string",
            "customer_unique_id": "string",
            "customer_zip_code_prefix": "int64",
            "customer_city": "string",
            "customer_state": "category",
        },
        "categorical": {"customer_state": BR_STATES},
        "ranges": {"customer_zip_code_prefix": (0, 100000)},
        "notes": "customer_id identifies the record attached to an order; "
                 "customer_unique_id is the customer-level identity. They are NOT "
                 "interchangeable (docs/data_architecture.md §4.3).",
    },
    "sellers": {
        "raw_file": "olist_sellers_dataset.csv",
        "primary_key": ["seller_id"],
        "dtypes": {
            "seller_id": "string",
            "seller_zip_code_prefix": "int64",
            "seller_city": "string",
            "seller_state": "category",
        },
        "categorical": {"seller_state": BR_STATES},
        "ranges": {"seller_zip_code_prefix": (0, 100000)},
        "notes": "",
    },
    "products": {
        "raw_file": "olist_products_dataset.csv",
        "primary_key": ["product_id"],
        "dtypes": {
            "product_id": "string",
            "product_category_name": "string",
            "product_name_lenght": "float64",
            "product_description_lenght": "float64",
            "product_photos_qty": "float64",
            "product_weight_g": "float64",
            "product_length_cm": "float64",
            "product_height_cm": "float64",
            "product_width_cm": "float64",
        },
        "categorical": {},
        "ranges": {
            "product_name_lenght": (0.0, None),
            "product_description_lenght": (0.0, None),
            "product_photos_qty": (0.0, None),
            "product_weight_g": (0.0, None),
            "product_length_cm": (0.0, None),
            "product_height_cm": (0.0, None),
            "product_width_cm": (0.0, None),
        },
        "notes": "610 'orphan' products have no category and no name/photo "
                 "metadata (values preserved as <NA>). Column names "
                 "'product_name_lenght' / 'product_description_lenght' keep the "
                 "source spelling (missing 'h') for raw traceability.",
    },
    "geolocation": {
        "raw_file": "olist_geolocation_dataset.csv",
        "primary_key": [],  # no natural key: duplicate (zip, lat, lng) rows exist
        "dtypes": {
            "geolocation_zip_code_prefix": "int64",
            "geolocation_lat": "float64",
            "geolocation_lng": "float64",
            "geolocation_city": "string",
            "geolocation_state": "category",
        },
        "categorical": {"geolocation_state": BR_STATES},
        "ranges": {
            "geolocation_zip_code_prefix": (0, 100000),
            "geolocation_lat": (-90.0, 90.0),
            "geolocation_lng": (-180.0, 180.0),
        },
        "notes": "No primary key; duplicates are retained (grain = source rows). "
                 "26 rows carry out-of-Brazil coordinates (e.g. lat>10 or lng>-30); "
                 "staging keeps them and the core dim_geography layer filters to "
                 "Brazil before building centroids.",
    },
    "translation": {
        "raw_file": "product_category_name_translation.csv",
        "primary_key": ["product_category_name"],
        "dtypes": {
            "product_category_name": "string",
            "product_category_name_english": "string",
        },
        "categorical": {},
        "ranges": {},
        "notes": "Portuguese -> English product-category names.",
    },
}

# Stable processing order (also the manifest row order).
TABLE_ORDER: list[str] = [
    "orders",
    "order_items",
    "payments",
    "reviews",
    "customers",
    "sellers",
    "products",
    "geolocation",
    "translation",
]
