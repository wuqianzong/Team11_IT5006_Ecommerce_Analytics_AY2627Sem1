"""Seller history at checkout (G-69): strict time, own order excluded, cold start, brute-force match."""
import numpy as np
import pandas as pd

ts = pd.Timestamp


def _data():
    orders = pd.DataFrame({"order_id": ["o1", "o2", "o3", "o4", "o5"],
                           "seller_id": ["s", "s", "s", "s", None],
                           "purchase_ts": [ts("2018-01-01 10:00:00"), ts("2018-01-05 10:00:00"),
                                           ts("2018-01-10 10:00:00"), ts("2018-01-10 10:00:00"), ts("2018-01-11")]})
    reviews = pd.DataFrame({"order_id": ["o1", "o2", "o3", "o1"],
                            "review_score": [5, 1, 4, 3],
                            "review_answer_timestamp": [ts("2018-01-05 10:00:00"),  # exactly o2's purchase: not before
                                                        ts("2018-01-08 00:00:00"),
                                                        ts("2018-01-09 00:00:00"),  # o3's own review, before its purchase
                                                        ts("2018-01-20")]})
    deliveries = pd.DataFrame({"order_id": ["o1", "o2"], "delivered_ts": [ts("2018-01-04"), ts("2018-01-09 12:00:00")],
                               "estimated_ts": [ts("2018-01-03"), ts("2018-01-20")]})
    return orders, reviews, deliveries


def test_strict_time_own_order_and_cold_start():
    from e5lib.seller_history import seller_history
    orders, reviews, deliveries = _data()
    h = seller_history(orders, reviews, deliveries).set_index(orders["order_id"])
    assert np.isnan(h.loc["o1", "seller_prior_review_mean"]) and h.loc["o1", "seller_prior_review_count"] == 0
    # o2: o1's review answered at exactly o2's purchase second does not count
    assert h.loc["o2", "seller_prior_review_count"] == 0 and h.loc["o2", "seller_prior_delivered_count"] == 1
    assert h.loc["o2", "seller_prior_late_share"] == 1.0
    # o3: o1 (5) and o2 (1) count; o3's own early review does not
    assert h.loc["o3", "seller_prior_review_count"] == 2 and h.loc["o3", "seller_prior_review_mean"] == 3.0
    assert h.loc["o3", "seller_prior_detractor_share"] == 0.5 and h.loc["o3", "seller_prior_late_share"] == 0.5
    # o4 (same second as o3, other order) sees o3's own review too
    assert h.loc["o4", "seller_prior_review_count"] == 3
    assert h.loc["o5"].isna().all()  # no seller (zero-item order): history unknown


def test_matches_brute_force():
    from e5lib.seller_history import brute_force, seller_history
    orders, reviews, deliveries = _data()
    fast = seller_history(orders, reviews, deliveries).set_index(orders["order_id"])
    slow = brute_force(orders, reviews, deliveries, orders["order_id"])
    pd.testing.assert_frame_equal(fast.sort_index(), slow.sort_index(), check_names=False)
