"""Order-grain aggregation of items, payments and reviews (feature_contract v1.1).

Every function is pure and deterministic: it consumes preprocessed tables and
returns per-``order_id`` frames. No item x payment x review Cartesian product is
ever formed — each fact table is collapsed to the order grain independently.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .contract import UNKNOWN, USABLE_PAYMENT_TYPES


# ---------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------

def resolve_english_category(products: pd.DataFrame, translation: pd.DataFrame) -> pd.DataFrame:
    """Attach a resolved English category; null for missing/untranslated names.

    The English label comes from ``product_category_name_translation.csv`` keyed
    on the Portuguese ``product_category_name``. Categories absent from the
    translation table stay unresolved (counted in ``category_missing_fraction``).
    """
    t = translation.rename(columns={
        "product_category_name": "_cat_pt",
        "product_category_name_english": "english_category",
    })
    prod = products.merge(
        t[["_cat_pt", "english_category"]],
        left_on="product_category_name", right_on="_cat_pt", how="left",
    ).drop(columns=["_cat_pt"])
    return prod


def aggregate_items(products_with_cat: pd.DataFrame,
                    items: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Collapse items to the order grain.

    Returns ``(item_agg, primary_rows, order_seller_pairs)`` where:
    - ``item_agg`` is indexed by ``order_id`` and carries every item-derived
      feature plus the primary item's resolved attributes;
    - ``primary_rows`` is the deterministic primary item per order;
    - ``order_seller_pairs`` is the distinct (order_id, seller_id) set for
      distance/interstate computation.
    """
    it = items.merge(
        products_with_cat[
            ["product_id", "english_category", "product_weight_g",
             "product_length_cm", "product_height_cm", "product_width_cm"]
        ],
        on="product_id", how="left",
    )

    price = pd.to_numeric(it["price"], errors="coerce")
    freight = pd.to_numeric(it["freight_value"], errors="coerce")
    weight = pd.to_numeric(it["product_weight_g"], errors="coerce")
    ln = pd.to_numeric(it["product_length_cm"], errors="coerce")
    ht = pd.to_numeric(it["product_height_cm"], errors="coerce")
    wd = pd.to_numeric(it["product_width_cm"], errors="coerce")

    it["_price_ok"] = price.notna() & np.isfinite(price) & (price >= 0)
    it["_freight_ok"] = freight.notna() & np.isfinite(freight) & (freight >= 0)
    it["_weight_ok"] = weight.notna() & np.isfinite(weight) & (weight > 0)
    it["_vol_ok"] = (ln.notna() & np.isfinite(ln) & (ln > 0)
                     & ht.notna() & np.isfinite(ht) & (ht > 0)
                     & wd.notna() & np.isfinite(wd) & (wd > 0))
    it["_cat_ok"] = it["english_category"].notna()

    it["_weight"] = weight.where(it["_weight_ok"])
    it["_volume"] = (ln * ht * wd).where(it["_vol_ok"])

    agg = it.groupby("order_id").agg(
        n_items=("order_item_id", "size"),
        n_products=("product_id", "nunique"),
        n_sellers=("seller_id", "nunique"),
        n_categories=("english_category", "nunique"),
        price_invalid=("_price_ok", lambda s: int((~s).sum())),
        freight_invalid=("_freight_ok", lambda s: int((~s).sum())),
        weight_invalid=("_weight_ok", lambda s: int((~s).sum())),
        volume_invalid=("_vol_ok", lambda s: int((~s).sum())),
        category_missing=("_cat_ok", lambda s: int((~s).sum())),
        seller_missing=("seller_id", lambda s: int(s.isna().sum())),
        total_price_sum=("price", "sum"),
        total_freight_sum=("freight_value", "sum"),
        weight_sum=("_weight", "sum"),
        volume_sum=("_volume", "sum"),
    )

    n = agg["n_items"].astype(float)

    agg["total_price"] = np.where(agg["price_invalid"] == 0, agg["total_price_sum"], np.nan)
    agg["total_freight"] = np.where(agg["freight_invalid"] == 0, agg["total_freight_sum"], np.nan)
    agg["total_weight_g"] = np.where(agg["weight_invalid"] == 0, agg["weight_sum"], np.nan)
    agg["total_volume_cm3"] = np.where(agg["volume_invalid"] == 0, agg["volume_sum"], np.nan)

    agg["weight_missing_fraction"] = agg["weight_invalid"] / n
    agg["volume_missing_fraction"] = agg["volume_invalid"] / n
    agg["category_missing_fraction"] = agg["category_missing"] / n

    agg["freight_ratio"] = np.where(
        (agg["total_price"].isna()) | (agg["total_price"] <= 0) | (agg["total_freight"].isna()),
        np.nan,
        agg["total_freight"] / agg["total_price"],
    )
    agg["has_items"] = (agg["n_items"] > 0).astype(int)
    agg["freight_ratio_missing"] = agg["freight_ratio"].isna().astype(int)
    agg["seller_id_missing"] = (agg["seller_missing"] > 0).astype(int)

    # Deterministic primary item: price desc (missing last), order_item_id asc.
    it_sorted = it.sort_values(
        ["order_id", "price", "order_item_id"],
        ascending=[True, False, True], na_position="last", kind="mergesort",
    )
    primary = it_sorted.drop_duplicates("order_id", keep="first").set_index("order_id")
    primary = primary[["seller_id", "english_category"]].rename(
        columns={"seller_id": "primary_seller_id",
                 "english_category": "primary_category"})

    order_seller_pairs = (
        it[["order_id", "seller_id"]].dropna(subset=["seller_id"])
        .drop_duplicates().reset_index(drop=True)
    )

    return agg, primary, order_seller_pairs


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------

def aggregate_payments(payments: pd.DataFrame) -> pd.DataFrame:
    """Collapse payments to the order grain.

    Usable rows = usable type (credit_card/boleto/voucher/debit_card, normalized)
    AND finite positive payment_value. ``payment_installments_max`` uses only
    positive, finite installments.
    """
    p = payments.copy()
    p["_type"] = p["payment_type"].map(
        lambda v: str(v).strip().lower()
        if isinstance(v, str) else (str(v).strip().lower() if v is not None else None)
    )
    p.loc[~p["_type"].isin(USABLE_PAYMENT_TYPES), "_type"] = None

    val = pd.to_numeric(p["payment_value"], errors="coerce")
    inst = pd.to_numeric(p["payment_installments"], errors="coerce")

    p["_usable"] = p["_type"].notna() & val.notna() & np.isfinite(val) & (val > 0)
    p["_val"] = val.where(p["_usable"])
    p["_inst"] = inst.where(p["_usable"] & inst.notna() & np.isfinite(inst) & (inst > 0))

    usable = p[p["_usable"]]

    totals = (
        usable.groupby(["order_id", "_type"], as_index=False)["_val"].sum()
        .rename(columns={"_val": "_total"})
    )
    totals = totals.sort_values(
        ["order_id", "_total", "_type"], ascending=[True, False, True], kind="mergesort"
    )
    primary = totals.drop_duplicates("order_id", keep="first")[["order_id", "_type"]]

    out = pd.DataFrame({"order_id": payments["order_id"].unique()})

    if len(usable):
        n_methods = usable.groupby("order_id")["_type"].nunique().rename("n_payment_methods")
        inst_max = usable.groupby("order_id")["_inst"].max().rename("payment_installments_max")
        out = out.merge(n_methods, on="order_id", how="left")
        out = out.merge(inst_max, on="order_id", how="left")
    else:
        out["n_payment_methods"] = np.nan
        out["payment_installments_max"] = np.nan

    out = out.merge(
        primary.rename(columns={"_type": "primary_payment_type"}), on="order_id", how="left"
    )
    out["n_payment_methods"] = out["n_payment_methods"].fillna(0).astype(int)
    out["primary_payment_type"] = out["primary_payment_type"].fillna(UNKNOWN)
    out["payment_missing"] = (out["primary_payment_type"] == UNKNOWN).astype(int)
    return out.set_index("order_id")


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------

def aggregate_reviews(reviews: pd.DataFrame) -> pd.DataFrame:
    """Collapse reviews to the order grain.

    A valid score is an integer in 1..5. ``review_latest_observed_at`` is the max
    valid answer timestamp; a valid score with a missing answer date still feeds
    ``review_score_min`` but not the observation timestamp.
    """
    r = reviews.copy()
    score = pd.to_numeric(r["review_score"], errors="coerce")
    valid = score.notna() & np.isfinite(score) & (score % 1 == 0) & (score >= 1) & (score <= 5)
    ans = pd.to_datetime(r["review_answer_timestamp"], errors="coerce", utc=False)

    r["_score"] = score.where(valid)
    r["_ans_contrib"] = ans.where(valid)

    out = r.groupby("order_id").agg(
        review_count=("review_id", "size"),
        review_score_min=("_score", "min"),
        review_latest_observed_at=("_ans_contrib", "max"),
    )

    det = pd.Series(pd.NA, index=out.index, dtype="Int64")
    det[out["review_score_min"] <= 2] = 1
    det[out["review_score_min"] >= 3] = 0
    out["is_detractor"] = det

    rmin = pd.Series(pd.NA, index=out.index, dtype="Int64")
    rmin[out["review_score_min"].notna()] = out.loc[out["review_score_min"].notna(), "review_score_min"].astype("Int64")
    out["review_score_min"] = rmin
    return out
