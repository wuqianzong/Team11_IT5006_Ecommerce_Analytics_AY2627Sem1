"""B2 history features: weighting, fallbacks and the before-the-prediction-week rule."""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

B_ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(B_ROOT.parent), str(B_ROOT)]

from e5b import history as h  # noqa: E402


def _events(rows):
    ev = pd.DataFrame(rows, columns=["seller_id", "seller_state", "customer_state", "hw", "dw", "h_late", "h_days",
                                     "dispatch", "lead", "transit"])
    ev["route"] = ev.customer_state + "->" + ev.seller_state
    return ev.astype({"hw": "Int64", "dw": "Int64"})


def test_weighted3_renormalises_over_weeks_with_values():
    weekly = pd.DataFrame({"k": [1, 1], "week": [9, 7], "v": [10.0, 20.0], "n": [4, 6]})
    q = pd.DataFrame({"k": [1], "pw": [10]})
    r = h.weighted3(weekly, q, ["k"], ["v"])
    # weeks 9 (w=0.5) and 7 (w=0.2) present, week 8 missing: (0.5*10 + 0.2*20) / 0.7
    assert np.isclose(r.v.iloc[0], (0.5 * 10 + 0.2 * 20) / 0.7) and r.n3.iloc[0] == 10


def test_seller_history_uses_only_earlier_weeks_and_falls_back_to_state():
    ev = _events([("s1", "SP", "RJ", 5, 6, 1.0, 2.0, 3.0, 8.0, 5.0),
                  ("s1", "SP", "RJ", 8, 9, 0.0, 0.0, 1.0, 6.0, 4.0),
                  ("s1", "SP", "RJ", 10, 11, 1.0, 9.0, 9.0, 9.0, 9.0),   # same week as the query: excluded
                  ("s2", "SP", "MG", 9, 10, 1.0, 4.0, 2.0, 7.0, 5.0)])
    q = pd.DataFrame({"seller_id": ["s1", "s9"], "seller_state": ["SP", "SP"], "pw": [10, 10]})
    f = h.seller_features(ev, q)
    assert f.b_seller_late_rate.iloc[0] == 0.5 and f.b_seller_source.iloc[0] == "seller"
    assert f.b_seller_last_week.iloc[0] == 8
    # new seller: SP weekly means at weeks 9 (s2: 1.0) and 8 (s1: 0.0) with weights 0.5 and 0.3
    assert f.b_seller_source.iloc[1] == "seller_state"
    assert np.isclose(f.b_seller_late_rate.iloc[1], (0.5 * 1.0 + 0.3 * 0.0) / 0.8)


def test_route_needs_ten_events_else_state_mix():
    rows = [("s", "SP", "RJ", 1, 9, 0.0, 0.0, 1.0, 10.0, 6.0)] * 10 + [("s", "MG", "RJ", 1, 9, 0.0, 0.0, 1.0, 20.0, 8.0)] * 3
    ev = _events(rows)
    q = pd.DataFrame({"route": ["RJ->SP", "RJ->MG"], "seller_state": ["SP", "MG"], "customer_state": ["RJ", "RJ"], "pw": [10, 10]})
    r = h.route_feature(ev, q, "lead", "x")
    assert r.x_source.iloc[0] == "route" and r.x.iloc[0] == 10.0
    # 3 events only: 0.7 x MG seller-state median (20) + 0.3 x RJ customer-state median (10, over all 13 events)
    assert r.x_source.iloc[1] == "state_mix" and np.isclose(r.x.iloc[1], 0.7 * 20.0 + 0.3 * 10.0)
