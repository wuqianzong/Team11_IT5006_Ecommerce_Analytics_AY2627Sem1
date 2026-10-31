from __future__ import annotations

import pandas as pd

from dashboard_core.routing import B_STATES, DashboardRelease


class _NoopRelease:
    threshold = {"A": 1 / 6, "B": 1 / 6}

    def check(self, frame: pd.DataFrame) -> pd.DataFrame:
        return pd.DataFrame(
            columns=["order_id", "level", "rule", "column", "message"]
        )

    def predict(self, frame: pd.DataFrame) -> pd.DataFrame:
        raise AssertionError("The routing-only test must not perform inference")


def test_route_scope_explains_b_and_a_decisions() -> None:
    router = DashboardRelease("classification", release=_NoopRelease())
    frame = pd.DataFrame(
        [
            {
                "order_id": "inside",
                "customer_state": "SP",
                "primary_seller_state": "RJ",
                "distance_km_max": 120.0,
            },
            {
                "order_id": "customer-outside",
                "customer_state": "CE",
                "primary_seller_state": "SP",
                "distance_km_max": 120.0,
            },
            {
                "order_id": "seller-outside",
                "customer_state": "SP",
                "primary_seller_state": "CE",
                "distance_km_max": 120.0,
            },
            {
                "order_id": "distance-missing",
                "customer_state": "SP",
                "primary_seller_state": "RJ",
                "distance_km_max": None,
            },
        ]
    )

    routed = router.route_scope(frame)

    assert B_STATES == {"SP", "MG", "RJ", "PR", "RS", "BA", "SC"}
    assert routed["in_b_scope"].tolist() == [True, False, False, False]
    assert routed["scope_reason"].tolist() == [
        "in scope",
        "outside: customer state",
        "outside: seller state",
        "outside: distance missing",
    ]

