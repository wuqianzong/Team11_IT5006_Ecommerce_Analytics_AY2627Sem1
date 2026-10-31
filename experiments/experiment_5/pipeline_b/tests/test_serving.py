"""B10 serving rule (B-G-06), thresholds (B-G-07, B10-D2), no score before handover (B10-D9) and input checks (B10.5)."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import yaml

B_ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(B_ROOT.parent), str(B_ROOT)]

from e5b import serving  # noqa: E402
from e5b.env import b_outputs_dir  # noqa: E402


def _order(rls: serving.Release, oid: str, **change) -> pd.DataFrame:
    """One synthetic order: every model feature at its training mean or first encoder level, in B's scope."""
    row = {"order_id": oid, "customer_state": "SP", "primary_seller_state": "SP", "distance_km_max": 20.0,
           "n_items": 1, "payment_installments_max": 1}
    for p in "AB":
        prof = json.loads((b_outputs_dir("t1_joint_test", rls.task) / f"bundles/{p}/training_profile.json").read_text(encoding="utf-8"))
        for c in rls.schemas[p]["numeric"]:
            row.setdefault(c, prof[c]["mean"])
        for c in rls.schemas[p]["categorical"]:
            row.setdefault(c, rls.levels[p][c][0])
    row["route_seller_to_customer_state"] = "SP->SP"
    row.update(change)
    return pd.DataFrame([row])


def test_scope_reasons():
    d = pd.DataFrame({"customer_state": ["SP", "AM", "SP", "SP"], "primary_seller_state": ["MG", "SP", "GO", "RJ"],
                      "distance_km_max": [10.0, 10.0, 10.0, np.nan]})
    assert serving.in_scope(d).tolist() == [True, False, False, False]
    assert serving.scope_reason(d).tolist() == ["in scope", "outside: customer state", "outside: seller state", "outside: distance missing"]


def test_thresholds_match_decisions():
    hd = yaml.safe_load((B_ROOT / "spec/human_decisions_B.yaml").read_text(encoding="utf-8"))["b10"]["classification"]
    assert serving.B_OPERATING == pytest.approx(hd["operating_threshold"]["value"], abs=1e-15)
    assert serving.FROZEN == pytest.approx(hd["out_of_scope_threshold"]["value"], abs=1e-15)
    for p in "AB":
        schema = json.loads((b_outputs_dir("t1_joint_test", "classification") / f"bundles/{p}/schema.json").read_text(encoding="utf-8"))
        assert schema["threshold"]["value"] == pytest.approx(serving.FROZEN, abs=1e-15)   # bundles keep the frozen 1/6


@pytest.mark.parametrize("task", ["regression", "classification"])
def test_routing_and_input_checks(task):
    rls = serving.Release(task)
    cases = pd.concat([_order(rls, "in"), _order(rls, "out", customer_state="AM"),
                       _order(rls, "bad_state", customer_state="XX"), _order(rls, "bad_dist", distance_km_max=-1.0),
                       _order(rls, "no_items", n_items=0), _order(rls, "no_inst", payment_installments_max=np.nan)],
                      ignore_index=True)
    r = rls.predict(cases).set_index("order_id")
    assert r.loc["in", "model"] == "B frozen" and r.loc["in", "status"] == "scored" and np.isfinite(r.loc["in", "prediction"])
    assert r.loc["out", "model"] == "A frozen" and r.loc["out", "status"] == "scored"
    for oid in ("bad_state", "bad_dist", "no_items", "no_inst"):
        assert r.loc[oid, "status"].startswith("rejected") and np.isnan(r.loc[oid, "prediction"])
    if task == "classification":
        assert r.loc["in", "threshold"] == serving.B_OPERATING and r.loc["out", "threshold"] == serving.FROZEN
        w = rls.predict(_order(rls, "wait", order_handed_over_late=np.nan)).iloc[0]
        assert w.status == serving.NO_SCORE and w.model == "" and np.isnan(w.prediction)


def test_unseen_category_is_a_warning_not_an_error():
    rls = serving.Release("regression")
    iss = rls.check(_order(rls, "x", primary_category="not_a_category"))
    assert set(iss.level) == {"warning"} and "unseen category" in set(iss.rule)
