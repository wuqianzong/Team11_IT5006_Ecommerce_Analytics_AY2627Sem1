"""Order-grain aggregation of items, payments and reviews (s02 2.4-2.6).

Provenance: copied from Milestone 2 `src/features/aggregation.py` (feature_contract v1.1).
Each fact table is collapsed to one row per order_id on its own, so no item x payment x review
product is ever formed. Changes for Experiment 5: has_items, freight_ratio_missing and
payment_missing are not built (not in the contract, G-61); payments also report whether the
order has a usable payment type (s02 2.11, G-51); reviews also give the first-review label and
the label-available timestamp (s02 2.6); the primary item also carries the catalogue fields
screened in s03 (PRIMARY_PRODUCT_FIELDS, G-68).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .cleaning import UNKNOWN, USABLE_PAYMENT_TYPES

# Catalogue fields taken from the primary item (screening candidates, G-68).
PRIMARY_PRODUCT_FIELDS = ("product_photos_qty", "product_description_lenght", "product_name_lenght")


def resolve_english_category(products: pd.DataFrame, translation: pd.DataFrame) -> pd.DataFrame:
    """Products with english_category; null when the name is missing or untranslated."""
    t = translation.rename(columns={"product_category_name": "_pt",
                                    "product_category_name_english": "english_category"})
    return products.merge(t[["_pt", "english_category"]], left_on="product_category_name",
                          right_on="_pt", how="left", validate="many_to_one").drop(columns="_pt")


def aggregate_items(products_cat: pd.DataFrame, items: pd.DataFrame):
    """(item features per order, primary item per order, distinct order-seller pairs)."""
    it = items.merge(products_cat[["product_id", "english_category", "product_weight_g",
                                   "product_length_cm", "product_height_cm", "product_width_cm",
                                   *PRIMARY_PRODUCT_FIELDS]],
                     on="product_id", how="left", validate="many_to_one")
    price, freight = it["price"].astype(float), it["freight_value"].astype(float)
    weight = it["product_weight_g"].astype(float)
    ln, ht, wd = (it[c].astype(float) for c in ("product_length_cm", "product_height_cm", "product_width_cm"))
    it["_price_ok"] = price.notna() & np.isfinite(price) & (price >= 0)
    it["_freight_ok"] = freight.notna() & np.isfinite(freight) & (freight >= 0)
    it["_weight_ok"] = weight.notna() & np.isfinite(weight) & (weight > 0)
    it["_vol_ok"] = (ln > 0) & (ht > 0) & (wd > 0) & np.isfinite(ln) & np.isfinite(ht) & np.isfinite(wd)
    it["_cat_ok"] = it["english_category"].notna()
    it["_weight"] = weight.where(it["_weight_ok"])
    it["_volume"] = (ln * ht * wd).where(it["_vol_ok"])

    agg = it.groupby("order_id").agg(
        n_items=("order_item_id", "size"), n_products=("product_id", "nunique"),
        n_sellers=("seller_id", "nunique"), n_categories=("english_category", "nunique"),
        price_bad=("_price_ok", lambda s: int((~s).sum())),
        freight_bad=("_freight_ok", lambda s: int((~s).sum())),
        weight_bad=("_weight_ok", lambda s: int((~s).sum())),
        volume_bad=("_vol_ok", lambda s: int((~s).sum())),
        category_bad=("_cat_ok", lambda s: int((~s).sum())),
        seller_missing=("seller_id", lambda s: int(s.isna().sum())),
        price_sum=("price", "sum"), freight_sum=("freight_value", "sum"),
        weight_sum=("_weight", "sum"), volume_sum=("_volume", "sum"))
    n = agg["n_items"].astype(float)
    agg["total_price"] = np.where(agg["price_bad"] == 0, agg["price_sum"], np.nan)
    agg["total_freight"] = np.where(agg["freight_bad"] == 0, agg["freight_sum"], np.nan)
    agg["total_weight_g"] = np.where(agg["weight_bad"] == 0, agg["weight_sum"], np.nan)
    agg["total_volume_cm3"] = np.where(agg["volume_bad"] == 0, agg["volume_sum"], np.nan)
    agg["weight_missing_fraction"] = agg["weight_bad"] / n
    agg["volume_missing_fraction"] = agg["volume_bad"] / n
    agg["category_missing_fraction"] = agg["category_bad"] / n
    agg["freight_ratio"] = np.where(agg["total_price"].isna() | (agg["total_price"] <= 0)
                                    | agg["total_freight"].isna(), np.nan,
                                    agg["total_freight"] / agg["total_price"])
    agg["seller_id_missing"] = (agg["seller_missing"] > 0).astype(int)

    # Primary item: highest price (missing last), then lowest order_item_id.
    primary = (it.sort_values(["order_id", "price", "order_item_id"], ascending=[True, False, True],
                              na_position="last", kind="mergesort")
               .drop_duplicates("order_id").set_index("order_id")[["seller_id", "english_category", *PRIMARY_PRODUCT_FIELDS]]
               .rename(columns={"seller_id": "primary_seller_id", "english_category": "primary_category"}))
    pairs = it[["order_id", "seller_id"]].dropna().drop_duplicates().reset_index(drop=True)
    keep = ["n_items", "n_products", "n_sellers", "n_categories", "total_price", "total_freight",
            "freight_ratio", "total_weight_g", "total_volume_cm3", "weight_missing_fraction",
            "volume_missing_fraction", "category_missing_fraction", "seller_id_missing"]
    return agg[keep], primary, pairs


def aggregate_payments(payments: pd.DataFrame) -> pd.DataFrame:
    """Per order: primary_payment_type, payment_installments_max, n_payment_methods, has_usable_type.

    Usable rows (Milestone 2 rule): usable type and finite positive value. Installments use
    positive finite values on usable rows. has_usable_type is False when the order has only
    not_defined (or unknown) payment types (s02 2.11).
    """
    p = payments.copy()
    p["_type"] = p["payment_type"].astype("string").str.strip().str.lower()
    p["_type_ok"] = p["_type"].isin(USABLE_PAYMENT_TYPES)
    val, inst = p["payment_value"].astype(float), p["payment_installments"].astype(float)
    p["_usable"] = p["_type_ok"] & val.notna() & np.isfinite(val) & (val > 0)
    p["_val"] = val.where(p["_usable"])
    p["_inst"] = inst.where(p["_usable"] & (inst > 0) & np.isfinite(inst))
    out = pd.DataFrame(index=pd.Index(p["order_id"].unique(), name="order_id"))
    out["has_usable_type"] = p.groupby("order_id")["_type_ok"].any()
    u = p[p["_usable"]]
    out["n_payment_methods"] = u.groupby("order_id")["_type"].nunique()
    out["payment_installments_max"] = u.groupby("order_id")["_inst"].max()
    totals = (u.groupby(["order_id", "_type"], as_index=False)["_val"].sum()
              .sort_values(["order_id", "_val", "_type"], ascending=[True, False, True], kind="mergesort")
              .drop_duplicates("order_id").set_index("order_id")["_type"])
    out["primary_payment_type"] = totals
    out["n_payment_methods"] = out["n_payment_methods"].fillna(0).astype(int)
    out["primary_payment_type"] = out["primary_payment_type"].fillna(UNKNOWN).astype(object)
    return out


def aggregate_reviews(reviews: pd.DataFrame) -> pd.DataFrame:
    """Per order: review_count, review_score_min, is_detractor, is_detractor_first, review_label_ts.

    A valid score is an integer 1..5. is_detractor = minimum valid score <= 2, available at the
    last valid answer (review_label_ts). The first review is the earliest by creation date, then
    answer time, then review_id; is_detractor_first uses its score (label sensitivity, s09 9.6).
    """
    r = reviews.copy()
    score = r["review_score"].astype(float)
    r["_valid"] = score.notna() & (score % 1 == 0) & (score >= 1) & (score <= 5)
    r["_score"] = score.where(r["_valid"])
    r["_ans"] = r["review_answer_timestamp"].where(r["_valid"])
    out = r.groupby("order_id").agg(review_count=("review_id", "size"), review_score_min=("_score", "min"),
                                    review_label_ts=("_ans", "max"))
    v = r[r["_valid"]].sort_values(["order_id", "review_creation_date", "review_answer_timestamp", "review_id"],
                                   kind="mergesort")
    out["review_score_first"] = v.drop_duplicates("order_id").set_index("order_id")["_score"]
    for col, src in (("is_detractor", "review_score_min"), ("is_detractor_first", "review_score_first")):
        out[col] = pd.Series(np.where(out[src].isna(), np.nan, (out[src] <= 2).astype(float)),
                             index=out.index).astype("Int64")
    return out
