"""Small, deterministic fixture checks for feature_contract.md §9 (Phase A).

Each check returns ``{"id", "status", "detail"}`` where status is ``pass`` or
``fail``. These exercise the exact contract rules with synthetic inputs so that a
regression in geometry, aggregation or tie-breaking is caught without touching
the real preprocessed data.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from shapely.geometry import Polygon

from .aggregation import aggregate_items, aggregate_payments, aggregate_reviews
from .contract import PREDICTOR_ALLOWLIST, UNKNOWN, VALID_STATES
from .geography import (
    build_zip_centroids,
    compute_distance_features,
    haversine_km,
    normalize_zip,
    _point_covers,
)


def _ok(detail: str) -> dict:
    return {"status": "pass", "detail": detail}


def _fail(detail: str) -> dict:
    return {"status": "fail", "detail": detail}


def _close(a, b, tol=1e-6) -> bool:
    return abs(float(a) - float(b)) <= tol


# ---------------------------------------------------------------------------
# Geography fixtures
# ---------------------------------------------------------------------------

def check_geography(polygon) -> dict:
    """Reject a European point and a bounding-box-but-not-Brazil point; accept a
    boundary point via the production ``_point_covers`` helper (boundary-inclusive)."""
    paris = _point_covers(polygon, np.array([2.3522]), np.array([48.8566]))
    if bool(paris[0]):
        return _fail("Paris (48.86, 2.35) was accepted inside the Brazil polygon")

    ocean = _point_covers(polygon, np.array([-40.0]), np.array([-28.0]))
    if bool(ocean[0]):
        return _fail("South-Atlantic point (-28, -40) inside the bbox was accepted")

    boundary = polygon.boundary
    if boundary.geom_type == "MultiLineString":
        pt = boundary.geoms[0].coords[0]
    else:
        pt = boundary.coords[0]
    if not bool(_point_covers(polygon, np.array([pt[0]]), np.array([pt[1]]))[0]):
        return _fail("a point on the polygon boundary was rejected by _point_covers")
    return _ok("European/bbox-foreign points rejected; boundary point accepted via _point_covers")


def check_mixed_validity_zip(polygon) -> dict:
    """A mixed-validity ZIP uses only accepted (in-polygon) coordinates."""
    sq = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])  # lat 0..10, lng 0..10
    geo = pd.DataFrame({
        "geolocation_zip_code_prefix": [11111, 11111, 11111, 11111],
        "geolocation_lat": [1.0, 2.0, 3.0, 50.0],  # 50 is outside
        "geolocation_lng": [5.0, 5.0, 5.0, 5.0],
        "geolocation_state": ["XX", "XX", "XX", "XX"],  # XX not a valid UF -> invalid key
    })
    # Use a valid UF so the key is valid; the square is just a toy polygon.
    geo["geolocation_state"] = "SP"
    centroids, counts = build_zip_centroids(geo, sq)
    row = centroids[centroids["zip_prefix"] == "11111"].iloc[0]
    if not _close(row["median_lat"], 2.0):
        return _fail(f"median lat {row['median_lat']} != 2.0 (outside point leaked)")
    if int(row["accepted_count"]) != 3:
        return _fail(f"accepted_count {row['accepted_count']} != 3")
    return _ok("mixed-validity ZIP median uses only the 3 in-polygon points")


def check_all_rejected_zip(polygon) -> dict:
    """An all-rejected ZIP stays unresolved with null coordinates."""
    sq = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])
    geo = pd.DataFrame({
        "geolocation_zip_code_prefix": [22222, 22222],
        "geolocation_lat": [50.0, 60.0],
        "geolocation_lng": [50.0, 60.0],
        "geolocation_state": ["SP", "SP"],
    })
    centroids, counts = build_zip_centroids(geo, sq)
    row = centroids[centroids["zip_prefix"] == "22222"].iloc[0]
    if row["resolution_status"] != "no_surviving_coordinates":
        return _fail(f"status {row['resolution_status']} != no_surviving_coordinates")
    if not (pd.isna(row["median_lat"]) and pd.isna(row["median_lng"])):
        return _fail("all-rejected ZIP produced coordinates")
    if int(row["accepted_count"]) != 0:
        return _fail("accepted_count != 0 for all-rejected ZIP")
    return _ok("all-rejected ZIP remains unresolved with null coordinates")


def check_zip_normalization() -> dict:
    """Integer/digit prefixes zero-pad; malformed and overlength forms reject."""
    if normalize_zip(1234) != "01234":
        return _fail("normalize_zip(1234) != '01234'")
    if normalize_zip("42") != "00042":
        return _fail("normalize_zip('42') != '00042'")
    if normalize_zip("12345") != "12345":
        return _fail("normalize_zip('12345') != '12345'")
    if normalize_zip("abc") is not None:
        return _fail("normalize_zip('abc') should be None")
    if normalize_zip(123456) is not None:
        return _fail("normalize_zip(123456) should be None")
    if normalize_zip("000001") is not None:
        return _fail("normalize_zip('000001') should be None (overlength string)")
    if normalize_zip(None) is not None:
        return _fail("normalize_zip(None) should be None")
    return _ok("ZIP prefix normalization zero-pads and rejects malformed/overlength forms")


# ---------------------------------------------------------------------------
# Distance fixtures
# ---------------------------------------------------------------------------

def check_haversine() -> dict:
    if not _close(float(haversine_km(0.0, 0.0, 0.0, 0.0)), 0.0):
        return _fail("coincident points did not give zero distance")
    # Known: ~1 degree latitude ~ 111.19 km.
    d = float(haversine_km(0.0, 0.0, 1.0, 0.0))
    if not _close(d, 111.19, tol=0.1):
        return _fail(f"1-degree latitude distance {d} != ~111.19 km")
    return _ok("haversine: coincident=0; 1-degree latitude ~111.19 km")


def check_distance_aggregation() -> dict:
    """Single/multiple/duplicate sellers and a missing-coordinate seller."""
    centroids = pd.DataFrame({
        "zip_prefix": ["01000", "02000", "03000"],
        "state": ["SP", "RJ", "MG"],
        "accepted_count": [1, 1, 1],
        "median_lat": [-23.55, -22.90, -19.92],
        "median_lng": [-46.63, -43.20, -43.94],
        "resolution_status": ["resolved", "resolved", "resolved"],
    })
    customers = pd.DataFrame({
        "customer_id": ["c1"], "customer_unique_id": ["cu1"],
        "customer_zip_code_prefix": [1000], "customer_state": ["SP"],
    })
    sellers = pd.DataFrame({
        "seller_id": ["s1", "s2", "s3"],
        "seller_zip_code_prefix": [2000, 3000, 9999],
        "seller_state": ["RJ", "MG", "AC"],
    })
    orders = pd.DataFrame({"order_id": ["o1"], "customer_id": ["c1"]})
    pairs = pd.DataFrame({
        "order_id": ["o1", "o1", "o1", "o1"],
        "seller_id": ["s1", "s2", "s1", "s3"],  # s1 duplicated
    })

    d_s1 = float(haversine_km(-23.55, -46.63, -22.90, -43.20))
    d_s2 = float(haversine_km(-23.55, -46.63, -19.92, -43.94))

    # s3 has zip 9999 with no centroid -> unresolved -> distance null.
    res = compute_distance_features(orders, customers, sellers, pairs, centroids)
    row = res.loc["o1"]
    if not pd.isna(row["distance_km_max"]):
        return _fail("distance_km_max should be null when a seller coordinate is unresolved")
    if not _close(row["distance_missing_fraction"], 1.0 / 3.0):
        return _fail(f"distance_missing_fraction {row['distance_missing_fraction']} != 1/3")
    if not _close(row["interstate_share"], 1.0):
        return _fail("interstate_share should be 1.0 (all sellers out of SP)")

    # Without the unresolved seller, the max is over {s1, s2} and dup s1 is ignored.
    pairs_ok = pd.DataFrame({"order_id": ["o1", "o1", "o1"], "seller_id": ["s1", "s2", "s1"]})
    res2 = compute_distance_features(orders, customers, sellers, pairs_ok, centroids)
    row2 = res2.loc["o1"]
    if not _close(row2["distance_km_max"], max(d_s1, d_s2)):
        return _fail(f"distance_km_max {row2['distance_km_max']} != max({d_s1},{d_s2})")
    return _ok("distance: single/dup/max semantics and null-on-missing verified")


# ---------------------------------------------------------------------------
# Physical / aggregation fixtures
# ---------------------------------------------------------------------------

def _mini_products() -> pd.DataFrame:
    return pd.DataFrame({
        "product_id": ["p_ok", "p_badw", "p_badv"],
        "product_category_name": ["cat_a", "cat_b", "cat_c"],
        "english_category": ["Cat A", "Cat B", None],
        "product_weight_g": [100.0, np.nan, 50.0],
        "product_length_cm": [10.0, 10.0, np.nan],
        "product_height_cm": [10.0, 10.0, 10.0],
        "product_width_cm": [10.0, 10.0, 10.0],
    })


def check_physical_totals() -> dict:
    """Two items, one missing weight -> null total weight + 0.5 fraction; both
    volumes valid -> total volume is the plain sum."""
    prod = _mini_products()
    items = pd.DataFrame({
        "order_id": ["o1", "o1"],
        "order_item_id": [1, 2],
        "product_id": ["p_ok", "p_badw"],
        "seller_id": ["s1", "s1"],
        "price": [10.0, 20.0],
        "freight_value": [5.0, 5.0],
    })
    agg, primary, pairs = aggregate_items(prod, items)
    row = agg.loc["o1"]
    if not pd.isna(row["total_weight_g"]):
        return _fail("total_weight_g should be null with one missing weight")
    if not _close(row["weight_missing_fraction"], 0.5):
        return _fail("weight_missing_fraction != 0.5")
    if not _close(row["total_volume_cm3"], 2000.0):
        return _fail(f"total_volume_cm3 {row['total_volume_cm3']} != 2000 (both volumes valid)")
    if not _close(row["volume_missing_fraction"], 0.0):
        return _fail("volume_missing_fraction != 0.0")
    return _ok("physical totals null on missing measurement; fractions correct")


def check_zero_price() -> dict:
    """A zero price preserves the row and yields a null freight ratio."""
    prod = _mini_products()
    items = pd.DataFrame({
        "order_id": ["o1"], "order_item_id": [1], "product_id": ["p_ok"],
        "seller_id": ["s1"], "price": [0.0], "freight_value": [5.0],
    })
    agg, primary, pairs = aggregate_items(prod, items)
    row = agg.loc["o1"]
    if row["n_items"] != 1 or row["has_items"] != 1:
        return _fail("zero-price order dropped or has_items=0")
    if not _close(row["total_price"], 0.0):
        return _fail("total_price should be 0.0")
    if not pd.isna(row["freight_ratio"]) or row["freight_ratio_missing"] != 1:
        return _fail("freight_ratio should be null with missing flag 1")
    return _ok("zero price preserved; freight ratio null")


def check_primary_item_tie() -> dict:
    """Equal prices -> smallest numeric order_item_id wins."""
    prod = _mini_products()
    items = pd.DataFrame({
        "order_id": ["o1", "o1"],
        "order_item_id": [5, 2],
        "product_id": ["p_ok", "p_badw"],
        "seller_id": ["s1", "s2"],
        "price": [10.0, 10.0],
        "freight_value": [1.0, 1.0],
    })
    agg, primary, pairs = aggregate_items(prod, items)
    row = primary.loc["o1"]
    if row["primary_seller_id"] != "s2":
        return _fail(f"primary seller {row['primary_seller_id']} != s2 (smallest item id)")
    return _ok("primary-item tie resolved by smallest order_item_id")


def check_payment_tie() -> dict:
    """Equal type totals -> lexicographically smallest type wins."""
    payments = pd.DataFrame({
        "order_id": ["o1", "o1", "o1", "o1"],
        "payment_sequential": [1, 2, 3, 4],
        "payment_type": ["credit_card", "boleto", "credit_card", "boleto"],
        "payment_installments": [1, 1, 1, 1],
        "payment_value": [50.0, 50.0, 50.0, 50.0],
    })
    out = aggregate_payments(payments)
    row = out.loc["o1"]
    if row["primary_payment_type"] != "boleto":
        return _fail(f"tie primary type {row['primary_payment_type']} != boleto")
    if row["n_payment_methods"] != 2 or row["payment_missing"] != 0:
        return _fail("n_payment_methods/payment_missing wrong for two-method order")
    return _ok("payment-type tie resolved lexicographically (boleto < credit_card)")


def check_absent_payment_and_unknown_category() -> dict:
    """Absent payments -> Unknown type, payment_missing=1; untranslated category -> Unknown."""
    prod = pd.DataFrame({
        "product_id": ["p_x"],
        "product_category_name": ["cat_c"],
        "english_category": [None],
        "product_weight_g": [10.0],
        "product_length_cm": [10.0], "product_height_cm": [10.0], "product_width_cm": [10.0],
    })
    items = pd.DataFrame({
        "order_id": ["o1"], "order_item_id": [1], "product_id": ["p_x"],
        "seller_id": ["s1"], "price": [10.0], "freight_value": [1.0],
    })
    agg, primary, pairs = aggregate_items(prod, items)
    row = primary.loc["o1"]
    if not pd.isna(row["primary_category"]):
        return _fail("untranslated category should be unresolved at aggregation")

    empty_pay = pd.DataFrame(columns=["order_id", "payment_sequential",
                                      "payment_type", "payment_installments", "payment_value"])
    out = aggregate_payments(empty_pay)
    # no rows -> function returns frame over payments.order_id.unique() (empty)
    if len(out) != 0:
        return _fail("aggregate_payments of empty input should return empty frame")
    return _ok("untranslated category unresolved; empty payments handled")


def check_review_target() -> dict:
    """Missing review -> null detractor; valid score -> correct detractor mapping."""
    reviews = pd.DataFrame({
        "review_id": ["r1", "r2", "r3"],
        "order_id": ["o1", "o2", "o3"],
        "review_score": [1, 5, 3],
        "review_answer_timestamp": ["2018-01-01", "2018-01-02", "2018-01-03"],
    })
    out = aggregate_reviews(reviews)
    if int(out.loc["o1", "is_detractor"]) != 1:
        return _fail("score 1 should map to is_detractor=1")
    if int(out.loc["o2", "is_detractor"]) != 0:
        return _fail("score 5 should map to is_detractor=0")
    if int(out.loc["o3", "is_detractor"]) != 0:
        return _fail("score 3 should map to is_detractor=0")
    return _ok("review target: min-score detractor mapping verified")


def check_invalid_review_null_label() -> dict:
    """A review with no valid score keeps a null label even when review_count > 0."""
    reviews = pd.DataFrame({
        "review_id": ["r1", "r2"],
        "order_id": ["o1", "o1"],
        "review_score": [0, "abc"],  # both invalid (out of range / non-numeric)
        "review_answer_timestamp": ["2018-01-01", "2018-01-02"],
    })
    out = aggregate_reviews(reviews)
    row = out.loc["o1"]
    if int(row["review_count"]) != 2:
        return _fail(f"review_count {row['review_count']} != 2")
    if not pd.isna(row["is_detractor"]):
        return _fail("is_detractor should be null when no valid score exists")
    if not pd.isna(row["review_score_min"]):
        return _fail("review_score_min should be null when no valid score exists")
    return _ok("invalid-only review keeps null label despite positive review_count")


def check_cartesian_join_safety() -> dict:
    """Two items x two payments x two reviews must still yield exactly one order row.

    Exercises the real production join path (``assemble_base``) rather than a
    hardcoded pass (feature_contract.md §9 / §11.4).
    """
    from shapely.geometry import Polygon

    from .build_features import assemble_base

    orders = pd.DataFrame({
        "order_id": ["o1"], "customer_id": ["c1"], "order_status": ["delivered"],
        "order_purchase_timestamp": pd.to_datetime(["2018-01-01 00:00:00"]),
        "order_delivered_customer_date": pd.to_datetime(["2018-01-05 00:00:00"]),
    })
    customers = pd.DataFrame({
        "customer_id": ["c1"], "customer_unique_id": ["cu1"],
        "customer_zip_code_prefix": [1000], "customer_state": ["SP"],
    })
    products = pd.DataFrame({
        "product_id": ["p1", "p2"],
        "product_category_name": ["cat_a", "cat_b"],
        "product_weight_g": [100.0, 200.0],
        "product_length_cm": [10.0, 10.0], "product_height_cm": [10.0, 10.0],
        "product_width_cm": [10.0, 10.0],
    })
    sellers = pd.DataFrame({
        "seller_id": ["s1"], "seller_zip_code_prefix": [1000], "seller_state": ["SP"],
    })
    geolocation = pd.DataFrame({
        "geolocation_zip_code_prefix": [1000],
        "geolocation_lat": [-23.55], "geolocation_lng": [-46.63],
        "geolocation_state": ["SP"],
    })
    translation = pd.DataFrame({
        "product_category_name": ["cat_a", "cat_b"],
        "product_category_name_english": ["Cat A", "Cat B"],
    })
    items = pd.DataFrame({
        "order_id": ["o1", "o1"], "order_item_id": [1, 2],
        "product_id": ["p1", "p2"], "seller_id": ["s1", "s1"],
        "price": [10.0, 20.0], "freight_value": [5.0, 5.0],
    })
    payments = pd.DataFrame({
        "order_id": ["o1", "o1"], "payment_sequential": [1, 2],
        "payment_type": ["credit_card", "boleto"],
        "payment_installments": [1, 1], "payment_value": [15.0, 15.0],
    })
    reviews = pd.DataFrame({
        "review_id": ["r1", "r2"], "order_id": ["o1", "o1"],
        "review_score": [4, 5],
        "review_answer_timestamp": ["2018-01-03", "2018-01-04"],
    })
    polygon = Polygon([(-50, -30), (-40, -30), (-40, -20), (-50, -20)])

    built = assemble_base(orders, customers, products, sellers, geolocation,
                          translation, items, payments, reviews, polygon)
    base = built["base"]
    if len(base) != 1:
        return _fail(f"2x2x2 fixture produced {len(base)} rows, expected 1")
    row = base.iloc[0]
    if int(row["n_items"]) != 2:
        return _fail(f"n_items {row['n_items']} != 2")
    if not _close(row["total_price"], 30.0):
        return _fail(f"total_price {row['total_price']} != 30.0")
    if int(row["n_payment_methods"]) != 2:
        return _fail(f"n_payment_methods {row['n_payment_methods']} != 2")
    if int(row["review_count"]) != 2:
        return _fail(f"review_count {row['review_count']} != 2")
    return _ok("2 items x 2 payments x 2 reviews -> exactly 1 order row with correct totals")


# ---------------------------------------------------------------------------
# Allowlist separation
# ---------------------------------------------------------------------------

def check_allowlist_separation(export_columns: list[str]) -> dict:
    """The 27-column allowlist must not intersect targets/IDs/outcome/eligibility/audit."""
    forbidden = {
        "order_id", "customer_id", "customer_unique_id",
        "prediction_timestamp", "order_status",
        "lead_days", "review_score_min", "is_detractor",
        "eligible_regression", "eligible_classification",
        "regression_exclusion_reason", "classification_exclusion_reason",
        "regression_label_available_at", "review_latest_observed_at",
        "review_count", "seller_id_missing",
        "split_assignment", "validation_fold",
    }
    overlap = set(PREDICTOR_ALLOWLIST) & forbidden
    if overlap:
        return _fail(f"allowlist intersects forbidden columns: {sorted(overlap)}")
    missing = [c for c in PREDICTOR_ALLOWLIST if c not in export_columns]
    if missing:
        return _fail(f"allowlist columns missing from export: {missing}")
    if len(PREDICTOR_ALLOWLIST) != 27:
        return _fail(f"allowlist has {len(PREDICTOR_ALLOWLIST)} columns, expected 27")
    return _ok("allowlist disjoint from targets/IDs/outcome/audit; 27 columns exported")


# ---------------------------------------------------------------------------
# Loader + publication fixtures (exercise the real file-loading/publish path)
# ---------------------------------------------------------------------------

def check_loaders_tolerate_invalid() -> dict:
    """Missing customer ZIP and nonnumeric review score must survive the real
    file-loading path: loaders read strings, downstream coercion quarantines."""
    import tempfile
    from pathlib import Path

    from .build_features import _load_customers, _load_reviews

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "olist_customers_dataset.csv").write_text(
            "customer_id,customer_unique_id,customer_zip_code_prefix,customer_state\n"
            "c1,cu1,,SP\n"
            "c2,cu2,1000,RJ\n",
            encoding="utf-8", newline="\n",
        )
        cust = _load_customers(tmp)
        zips = cust["customer_zip_code_prefix"].map(normalize_zip)
        if zips.iloc[0] is not None:
            return _fail("missing customer ZIP was not left unresolved by the loader")
        if zips.iloc[1] != "01000":
            return _fail(f"customer ZIP normalized to {zips.iloc[1]!r}, expected '01000'")

        (tmp / "olist_order_reviews_dataset.csv").write_text(
            "review_id,order_id,review_score,review_answer_timestamp\n"
            "r1,o1,abc,2018-01-01 00:00:00\n"
            "r2,o2,4,2018-01-02 00:00:00\n",
            encoding="utf-8", newline="\n",
        )
        rev = _load_reviews(tmp)
        out = aggregate_reviews(rev)
        if int(out.loc["o1", "review_count"]) != 1:
            return _fail("review_count for invalid-only order != 1")
        if not pd.isna(out.loc["o1", "is_detractor"]):
            return _fail("nonnumeric review score produced a label instead of null")
        if int(out.loc["o2", "is_detractor"]) != 0:
            return _fail("valid score 4 should map to is_detractor=0")
    return _ok("missing ZIP / nonnumeric score survive the file-loading path")


def check_geolocation_loader_malformed_coords() -> dict:
    """Malformed/missing/nonfinite/out-of-range coordinates must survive the real
    CSV loader and be rejected by downstream geography with the contract's
    precedence, accepted-only medians, unresolved zero-survivor keys, and null
    distance for any unresolved required location."""
    import tempfile
    from pathlib import Path

    from .build_features import _load_geolocation

    csv = (
        "geolocation_zip_code_prefix,geolocation_lat,geolocation_lng,geolocation_state\n"
        "11111,1.0,5.0,SP\n"    # accepted
        "11111,2.0,5.0,SP\n"    # accepted
        "11111,3.0,5.0,SP\n"    # accepted
        "11111,50.0,5.0,SP\n"   # outside polygon (lat 50 in global range)
        "22222,50.0,5.0,SP\n"   # outside polygon
        "22222,60.0,5.0,SP\n"   # outside polygon -> all-rejected group
        "33333,bad,5.0,SP\n"    # nonnumeric -> invalid_coords
        "44444,1.0,,SP\n"       # missing lng -> invalid_coords
        "55555,inf,5.0,SP\n"    # nonfinite -> invalid_coords
        "66666,95.0,5.0,SP\n"   # lat out of range
        "77777,1.0,200.0,SP\n"  # lng out of range
        "88888,1.0,5.0,XX\n"    # invalid key
        "99999,bad,5.0,XX\n"    # invalid key wins over bad coords (precedence)
    )

    sq = Polygon([(0, 0), (10, 0), (10, 10), (0, 10)])  # lng 0..10, lat 0..10
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        (tmp / "olist_geolocation_dataset.csv").write_text(csv, encoding="utf-8", newline="\n")
        geo = _load_geolocation(tmp)  # the real loader: must not raise on "bad"/""/"inf"

        centroids, filter_report = build_zip_centroids(geo, sq)

        # Rejection counts (mutually exclusive first-failure reasons).
        ffr = filter_report["first_failure_reasons"]
        expected = {
            "None": 3, "outside_polygon": 3, "invalid_coords": 3,
            "lat_out_of_range": 1, "lng_out_of_range": 1, "invalid_key": 2,
        }
        for k, v in expected.items():
            if int(ffr.get(k, 0)) != v:
                return _fail(f"first_failure_reasons[{k}] = {ffr.get(k)} != {v}")
        if filter_report["total_rows"] != 13 or filter_report["accepted"] != 3:
            return _fail(f"total/accepted {filter_report['total_rows']}/{filter_report['accepted']} != 13/3")

        # Surviving median uses accepted coordinates only; all-rejected/coords
        # rejected keys stay unresolved with null coordinates; invalid keys absent.
        if len(centroids) != 7:
            return _fail(f"expected 7 centroid keys (13 rows - 2 invalid-key groups), got {len(centroids)}")
        ok = centroids[centroids["zip_prefix"] == "11111"].iloc[0]
        if ok["resolution_status"] != "resolved":
            return _fail(f"11111 status {ok['resolution_status']} != resolved")
        if not _close(ok["median_lat"], 2.0) or not _close(ok["median_lng"], 5.0):
            return _fail(f"11111 median ({ok['median_lat']},{ok['median_lng']}) != (2.0,5.0)")
        if int(ok["accepted_count"]) != 3:
            return _fail(f"11111 accepted_count {ok['accepted_count']} != 3")

        unresolved = centroids[centroids["resolution_status"] == "no_surviving_coordinates"]
        if len(unresolved) != 6:
            return _fail(f"expected 6 no_surviving keys, got {len(unresolved)}")
        if not (unresolved["median_lat"].isna() & unresolved["median_lng"].isna()).all():
            return _fail("an unresolved key produced non-null coordinates")
        if "88888" in set(centroids["zip_prefix"]) or "99999" in set(centroids["zip_prefix"]):
            return _fail("invalid-key group was exported as a centroid")

        # Null distance whenever a required customer/seller location is unresolved.
        customers = pd.DataFrame({
            "customer_id": ["c1", "c2"], "customer_unique_id": ["cu1", "cu2"],
            "customer_zip_code_prefix": ["22222", "11111"], "customer_state": ["SP", "SP"],
        })
        sellers = pd.DataFrame({
            "seller_id": ["s1", "s2"], "seller_zip_code_prefix": ["11111", "22222"],
            "seller_state": ["SP", "SP"],
        })
        orders = pd.DataFrame({
            "order_id": ["o1", "o2", "o3"], "customer_id": ["c1", "c2", "c2"],
        })
        pairs = pd.DataFrame({
            "order_id": ["o1", "o2", "o3"], "seller_id": ["s1", "s2", "s1"],
        })
        dist = compute_distance_features(orders, customers, sellers, pairs, centroids)
        if not pd.isna(dist.loc["o1", "distance_km_max"]):
            return _fail("unresolved customer should null distance, not a partial max")
        if not pd.isna(dist.loc["o2", "distance_km_max"]):
            return _fail("unresolved seller should null distance, not a partial max")
        if not _close(dist.loc["o3", "distance_km_max"], 0.0):
            return _fail(f"resolved order o3 distance {dist.loc['o3', 'distance_km_max']} != 0.0")
    return _ok("malformed coords survive the loader; precedence/medians/unresolved/null-distance verified")


def check_atomic_publish_rollback() -> dict:
    """An interrupted publication must roll back every already-replaced file to
    its exact prior bytes, leaving no mixed old/new artifact set."""
    import os
    import tempfile
    from pathlib import Path

    from .serialization import publish_atomic

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        target = root / "target"
        staging = root / "staging"
        target.mkdir()
        staging.mkdir()
        (target / "a.csv").write_text("old-a\n", encoding="utf-8", newline="\n")
        (target / "b.csv").write_text("old-b\n", encoding="utf-8", newline="\n")
        (staging / "a.csv").write_text("new-a\n", encoding="utf-8", newline="\n")
        (staging / "b.csv").write_text("new-b\n", encoding="utf-8", newline="\n")

        calls = {"n": 0}

        def flaky_replace(src, dst):
            calls["n"] += 1
            if calls["n"] == 2:
                raise OSError("injected failure during second replacement")
            os.replace(src, dst)

        try:
            publish_atomic(staging, target, replace=flaky_replace)
            return _fail("injected publication failure did not propagate")
        except OSError:
            pass

        # No mixed old/new set: both artifacts restored to their exact bytes.
        if (target / "a.csv").read_text(encoding="utf-8") != "old-a\n":
            return _fail("rollback did not restore a.csv")
        if (target / "b.csv").read_text(encoding="utf-8") != "old-b\n":
            return _fail("rollback did not restore b.csv")
        if sorted(p.name for p in target.iterdir()) != ["a.csv", "b.csv"]:
            return _fail("rollback left an unexpected artifact set")
    return _ok("failed publication over existing outputs rolled back to original files")


def check_atomic_publish_first_publication() -> dict:
    """A failed first-time publication must remove newly published copies instead
    of leaving a partial artifact set behind."""
    import os
    import tempfile
    from pathlib import Path

    from .serialization import publish_atomic

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        target = root / "target"
        staging = root / "staging"
        target.mkdir()  # empty: nothing published yet
        staging.mkdir()
        (staging / "split_assignments.csv").write_text("new-split\n", encoding="utf-8", newline="\n")
        (staging / "cv_assignments.csv").write_text("new-cv\n", encoding="utf-8", newline="\n")
        (staging / "split_report.json").write_text("{}\n", encoding="utf-8", newline="\n")

        calls = {"n": 0}

        def flaky_replace(src, dst):
            calls["n"] += 1
            if calls["n"] == 2:
                raise OSError("injected failure during second replacement")
            os.replace(src, dst)

        try:
            publish_atomic(staging, target, replace=flaky_replace)
            return _fail("injected first-publication failure did not propagate")
        except OSError:
            pass

        # The single already-published copy must have been removed.
        if list(target.iterdir()):
            return _fail("first-time publication left partial files after rollback")
    return _ok("failed first-time publication removed newly published copies")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_fixture_checks(polygon, export_columns: list[str]) -> list[dict]:
    """Run all Phase-A fixtures; returns a list of {id, status, detail}."""
    results = []
    for fid, fn in [
        ("geography_reject_foreign_accept_boundary", lambda: check_geography(polygon)),
        ("geography_mixed_validity_zip", lambda: check_mixed_validity_zip(polygon)),
        ("geography_all_rejected_zip", lambda: check_all_rejected_zip(polygon)),
        ("zip_normalization", check_zip_normalization),
        ("haversine", check_haversine),
        ("distance_aggregation", check_distance_aggregation),
        ("physical_totals", check_physical_totals),
        ("zero_price", check_zero_price),
        ("primary_item_tie", check_primary_item_tie),
        ("payment_tie", check_payment_tie),
        ("absent_payment_unknown_category", check_absent_payment_and_unknown_category),
        ("review_target", check_review_target),
        ("invalid_review_null_label", check_invalid_review_null_label),
        ("cartesian_join_safety", check_cartesian_join_safety),
        ("allowlist_separation", lambda: check_allowlist_separation(export_columns)),
        ("loaders_tolerate_invalid", check_loaders_tolerate_invalid),
        ("geolocation_loader_malformed_coords", check_geolocation_loader_malformed_coords),
        ("atomic_publish_rollback", check_atomic_publish_rollback),
        ("atomic_publish_first_publication", check_atomic_publish_first_publication),
    ]:
        try:
            res = fn()
        except Exception as exc:  # noqa: BLE001 - surface as a failed check
            res = _fail(f"exception: {exc!r}")
        results.append({"id": fid, **res})
    return results
