"""Typed loading and cleaning of the nine Olist tables (s02 2.1-2.2).

Provenance: rules copied from Milestone 2 `notebooks/01_data_cleaning.ipynb` (schema contract
and clean_table): declared types, ZIP prefixes as strings, categorical domains checked and
logged but rows kept, geolocation exact duplicates dropped, no imputation. State and payment
constants copied from Milestone 2 `src/features/contract.py` (names and values only).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import data

BR_STATES = frozenset({
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA",
    "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
})
ORDER_STATUS = frozenset({"approved", "canceled", "created", "delivered", "invoiced",
                          "processing", "shipped", "unavailable"})
PAYMENT_TYPE = frozenset({"boleto", "credit_card", "debit_card", "not_defined", "voucher"})
USABLE_PAYMENT_TYPES = frozenset({"credit_card", "boleto", "voucher", "debit_card"})
UNKNOWN = "Unknown"

# table -> (dtype per column, categorical domain checks, drop exact duplicates)
TABLES = {
    "orders": ({"order_id": "str", "customer_id": "str", "order_status": "category",
                "order_purchase_timestamp": "datetime", "order_approved_at": "datetime",
                "order_delivered_carrier_date": "datetime",
                "order_delivered_customer_date": "datetime",
                "order_estimated_delivery_date": "datetime"},
               {"order_status": ORDER_STATUS}, False),
    "order_items": ({"order_id": "str", "order_item_id": "int", "product_id": "str",
                     "seller_id": "str", "shipping_limit_date": "datetime",
                     "price": "float", "freight_value": "float"}, {}, False),
    "order_payments": ({"order_id": "str", "payment_sequential": "int",
                        "payment_type": "category", "payment_installments": "int",
                        "payment_value": "float"}, {"payment_type": PAYMENT_TYPE}, False),
    "order_reviews": ({"review_id": "str", "order_id": "str", "review_score": "int",
                       "review_comment_title": "str", "review_comment_message": "str",
                       "review_creation_date": "datetime",
                       "review_answer_timestamp": "datetime"}, {}, False),
    "customers": ({"customer_id": "str", "customer_unique_id": "str",
                   "customer_zip_code_prefix": "str", "customer_city": "str",
                   "customer_state": "category"}, {"customer_state": BR_STATES}, False),
    "sellers": ({"seller_id": "str", "seller_zip_code_prefix": "str", "seller_city": "str",
                 "seller_state": "category"}, {"seller_state": BR_STATES}, False),
    "products": ({"product_id": "str", "product_category_name": "str",
                  "product_name_lenght": "float", "product_description_lenght": "float",
                  "product_photos_qty": "float", "product_weight_g": "float",
                  "product_length_cm": "float", "product_height_cm": "float",
                  "product_width_cm": "float"}, {}, False),
    "geolocation": ({"geolocation_zip_code_prefix": "str", "geolocation_lat": "float",
                     "geolocation_lng": "float", "geolocation_city": "str",
                     "geolocation_state": "category"}, {"geolocation_state": BR_STATES}, True),
    "category_translation": ({"product_category_name": "str",
                              "product_category_name_english": "str"}, {}, False),
}
_READ_DTYPE = {"str": "string", "int": "int64", "float": "float64", "category": "string"}


def load_clean(table: str, stage: str = "s02_data") -> tuple[pd.DataFrame, dict]:
    """Read one raw table with declared types; returns (frame, cleaning log)."""
    dtypes, domains, dedup = TABLES[table]
    dates = [c for c, t in dtypes.items() if t == "datetime"]
    df = data.load_raw(table, stage,
                       dtype={c: _READ_DTYPE[t] for c, t in dtypes.items() if t != "datetime"},
                       parse_dates=dates)
    log = {"rows_raw": int(len(df)), "columns": list(df.columns)}
    if list(df.columns) != list(dtypes):
        raise ValueError(f"{table}: columns {list(df.columns)} differ from the declared schema")
    if dedup:
        before = len(df)
        df = df.drop_duplicates().reset_index(drop=True)
        log["exact_duplicates_dropped"] = int(before - len(df))
    log["domain_violations"] = {
        c: sorted(set(df[c].dropna().unique()) - set(allowed)) for c, allowed in domains.items()
    }
    log["rows_clean"] = int(len(df))
    log["nulls"] = {c: int(n) for c, n in df.isna().sum().items()}
    return df[list(dtypes)], log


def normalize_state(value) -> str:
    """Upper-cased Brazilian state code, or UNKNOWN (Milestone 2 contract.normalize_state)."""
    if value is None or (isinstance(value, float) and np.isnan(value)) or value is pd.NA:
        return UNKNOWN
    s = str(value).strip().upper()
    return s if s in BR_STATES else UNKNOWN
