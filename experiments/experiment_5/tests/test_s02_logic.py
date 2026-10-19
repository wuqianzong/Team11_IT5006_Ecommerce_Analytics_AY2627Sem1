"""Ported s02 logic: aggregation rules, ZIP normalisation, distance."""
import pandas as pd


def test_payments_usable_type_and_installments():
    from e5lib.aggregation import aggregate_payments
    p = pd.DataFrame({"order_id": ["a", "a", "b", "c"], "payment_sequential": [1, 2, 1, 1],
                      "payment_type": ["credit_card", "voucher", "not_defined", "boleto"],
                      "payment_installments": [3, 1, 1, 0], "payment_value": [50.0, 80.0, 10.0, 20.0]})
    out = aggregate_payments(p)
    assert out.loc["a", "primary_payment_type"] == "voucher" and out.loc["a", "payment_installments_max"] == 3
    assert not out.loc["b", "has_usable_type"] and out.loc["b", "primary_payment_type"] == "Unknown"
    assert pd.isna(out.loc["c", "payment_installments_max"])  # zero installments are not usable


def test_reviews_min_and_first_label():
    from e5lib.aggregation import aggregate_reviews
    ts = pd.to_datetime
    r = pd.DataFrame({"review_id": ["r1", "r2", "r3"], "order_id": ["a", "a", "b"], "review_score": [5, 1, 3],
                      "review_creation_date": ts(["2018-01-01", "2018-01-05", "2018-01-02"]),
                      "review_answer_timestamp": ts(["2018-01-02", "2018-01-06", "2018-01-03"])})
    out = aggregate_reviews(r)
    assert out.loc["a", "is_detractor"] == 1 and out.loc["a", "is_detractor_first"] == 0
    assert out.loc["a", "review_label_ts"] == ts("2018-01-06") and out.loc["b", "is_detractor"] == 0


def test_items_primary_and_missing_totals():
    from e5lib.aggregation import aggregate_items
    prod = pd.DataFrame({"product_id": ["p1", "p2"], "english_category": ["toys", None],
                         "product_weight_g": [100.0, None], "product_length_cm": [10.0, 10.0],
                         "product_height_cm": [10.0, 10.0], "product_width_cm": [10.0, 10.0]})
    it = pd.DataFrame({"order_id": ["a", "a"], "order_item_id": [1, 2], "product_id": ["p1", "p2"],
                       "seller_id": ["s1", "s2"], "price": [10.0, 30.0], "freight_value": [5.0, 5.0]})
    agg, primary, pairs = aggregate_items(prod, it)
    assert agg.loc["a", "total_price"] == 40 and pd.isna(agg.loc["a", "total_weight_g"])
    assert agg.loc["a", "weight_missing_fraction"] == 0.5 and primary.loc["a", "primary_seller_id"] == "s2"
    assert len(pairs) == 2 and "has_items" not in agg.columns


def test_zip_and_haversine():
    from e5lib.geography import haversine_km, normalize_zip
    assert normalize_zip("1001") == "01001" and normalize_zip("abc") is None and normalize_zip(None) is None
    assert abs(float(haversine_km(0, 0, 0, 1)) - 111.19) < 0.1
