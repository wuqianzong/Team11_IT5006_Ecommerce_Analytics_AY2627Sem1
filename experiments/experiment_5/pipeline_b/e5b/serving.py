"""B10 serving (blueprint pipeline_b/spec/blueprints/b10_release.md, B10.4 and B10.5).

Release(task) routes each order to B's or A's frozen T1 bundle by B's scope (B-G-06) and applies the configured
threshold: B's operating 4/15 (B-G-07) with the frozen 1/6 beside it, A's frozen 1/6 for the fallback (B10-D2).
In-scope classification orders not yet handed over get no score (B10-D9). Inference only: nothing here fits.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from e5lib.training import predict

from . import b02
from .env import b_outputs_dir

B_OPERATING = 4 / 15        # B-G-07 (B-G-09 withdrawn as a typo)
FROZEN = 1 / 6              # frozen threshold of A and B (schema.json); A's fallback threshold (B10-D2)
SCOPE_COLS = ("customer_state", "primary_seller_state", "distance_km_max")
UF = ("AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI",
      "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO")   # Brazil's 27 federative units
MAX_DISTANCE_KM = 5000.0    # above Brazil's widest extent (about 4,400 km): an impossible distance
HANDOVER = "order_handed_over_late"
NO_SCORE = "no score: in scope, not yet handed over (B10-D9; missed-dispatch rule applies)"


def in_scope(d: pd.DataFrame) -> pd.Series:
    """B's scope (B-C1, B-C2): customer and primary seller state in the seven states, distance present."""
    return d.customer_state.isin(b02.STATES) & d.primary_seller_state.isin(b02.STATES) & d.distance_km_max.notna()


def scope_reason(d: pd.DataFrame) -> pd.Series:
    r = pd.Series("in scope", index=d.index)
    r[d.distance_km_max.isna()] = "outside: distance missing"
    r[~d.primary_seller_state.isin(b02.STATES)] = "outside: seller state"
    r[~d.customer_state.isin(b02.STATES)] = "outside: customer state"
    return r


def encoder_levels(model) -> dict[str, list[str]]:
    """Category levels the bundle's one-hot encoder learned (unseen levels are ignored by it)."""
    pipe = model.regressor_ if hasattr(model, "regressor_") else model.calibrated_classifiers_[0].estimator
    prep = pipe.named_steps["prep"]
    cat = prep.named_transformers_["cat"]
    cols = next(c for name, _, c in prep.transformers_ if name == "cat")
    return {c: [str(v) for v in lv] for c, lv in zip(cols, cat.named_steps["onehot"].categories_)}


class Release:
    """The two frozen bundles of one task with the serving rule; `config` is B10's serving_config.json."""

    def __init__(self, task: str, config: dict | None = None, bundles: Path | None = None):
        self.task = task
        root = bundles or b_outputs_dir("t1_joint_test", task) / "bundles"
        self.models = {p: joblib.load(root / p / "model.joblib") for p in "AB"}
        self.schemas = {p: json.loads((root / p / "schema.json").read_text()) for p in "AB"}
        self.levels = {p: encoder_levels(m) for p, m in self.models.items()}
        cfg = config or {}
        thr = cfg.get("thresholds", {})
        self.threshold = {"B": thr.get("B_operating", {}).get("value", B_OPERATING),
                          "A": thr.get("A_fallback", {}).get("value", FROZEN)}
        self.profile = cfg.get("out_of_profile", {})   # {"sd": K, "numeric": {pipe: {col: {"mean", "std"}}}}; K None = off

    @classmethod
    def load(cls, task: str) -> "Release":
        return cls(task, json.loads((b_outputs_dir("b10", task) / "serving_config.json").read_text()))

    # B10.5 input checks -----------------------------------------------------------------------------------
    def check(self, d: pd.DataFrame) -> pd.DataFrame:
        """One row per problem: order_id, level (error or warning), rule, column, message."""
        out = []

        def add(mask, level, rule, col, msg):
            for oid in d.order_id[mask]:
                out.append({"order_id": oid, "level": level, "rule": rule, "column": col, "message": msg})

        for c in SCOPE_COLS + ("n_items", "payment_installments_max"):
            if c not in d:
                add(pd.Series(True, index=d.index), "error", "missing column", c, f"column {c} is required")
        if out:
            return pd.DataFrame(out)
        for c in ("customer_state", "primary_seller_state"):
            add(~d[c].isin(UF), "error", "unknown state", c, f"{c} is not a Brazilian state code")
        dist = pd.to_numeric(d.distance_km_max, errors="coerce")
        add(d.distance_km_max.notna() & dist.isna(), "error", "type", "distance_km_max", "distance_km_max is not a number")
        add((dist < 0) | (dist > MAX_DISTANCE_KM), "error", "impossible distance", "distance_km_max",
            f"distance must be between 0 and {MAX_DISTANCE_KM:,.0f} km")
        items = pd.to_numeric(d.n_items, errors="coerce")
        add(items.isna() | (items < 1), "error", "no items", "n_items", "an order needs at least one item")
        add(pd.to_numeric(d.payment_installments_max, errors="coerce").isna(), "error", "missing installments",
            "payment_installments_max", "payment_installments_max is missing or not a number")
        mine = {"B": in_scope(d), "A": ~in_scope(d)}
        k = self.profile.get("sd")
        for p in "AB":
            s, sel = self.schemas[p], mine[p]
            if not sel.any():
                continue
            for c in s["numeric"] + s["categorical"]:
                # B's handover facts may be absent before handover: such orders get no score (B10-D9), not an error
                if c not in d and not (p == "B" and self.task == "classification" and c.startswith("order_")):
                    add(sel, "error", "missing column", c, f"column {c} is required by {p}'s model")
            for c in s["numeric"]:
                if c not in d:
                    continue
                v = pd.to_numeric(d[c], errors="coerce")
                prof = (self.profile.get("numeric") or {}).get(p, {}).get(c, {})
                add(sel & d[c].notna() & v.isna(), "error", "type", c, f"{c} is not a number")
                if prof.get("min", 0) >= 0:   # only where training never had a negative value
                    add(sel & (v < 0), "error", "negative value", c, f"{c} cannot be negative")
                add(sel & d[c].isna(), "warning", "missing value", c, f"{c} is missing; {p}'s model imputes the training median")
                if k and prof.get("std", 0) > 0:
                    add(sel & ((v - prof["mean"]) / prof["std"]).abs().gt(k), "warning", "out of profile", c,
                        f"{c} is more than {k} SD from the training mean")
            for c in s["categorical"]:
                if c in d:
                    add(sel & d[c].notna() & ~d[c].astype(str).isin(self.levels[p].get(c, [])), "warning",
                        "unseen category", c, f"{c} level not seen in training; {p}'s encoder ignores it")
        return pd.DataFrame(out, columns=["order_id", "level", "rule", "column", "message"])

    # B10.4 routing ------------------------------------------------------------------------------------------
    def predict(self, d: pd.DataFrame) -> pd.DataFrame:
        """order_id, scope_reason, model, status, prediction, threshold, alert (classification), alert_at_frozen."""
        d = d.reset_index(drop=True)
        issues = self.check(d)
        bad = set(issues.order_id[issues.level == "error"]) if len(issues) else set()
        res = pd.DataFrame({"order_id": d.order_id, "scope_reason": scope_reason(d), "model": "", "status": "",
                            "prediction": np.nan, "threshold": np.nan})
        rejected = d.order_id.isin(bad)
        scope = in_scope(d)
        if self.task == "classification":
            handed_over = d[HANDOVER].notna() if HANDOVER in d else pd.Series(False, index=d.index)
        else:
            handed_over = pd.Series(True, index=d.index)   # regression predicts at checkout
        waiting = scope & ~rejected & ~handed_over
        res.loc[rejected, "status"] = "rejected: input error"
        res.loc[waiting, "status"] = NO_SCORE
        for p, mask in (("B", scope & ~rejected & ~waiting), ("A", ~scope & ~rejected)):
            if mask.any():
                res.loc[mask, "model"] = f"{p} frozen"
                res.loc[mask, "status"] = "scored"
                res.loc[mask, "prediction"] = predict(self.task, self.models[p], d[mask])
                res.loc[mask, "threshold"] = self.threshold[p]
        if self.task == "classification":
            res["alert"] = res.prediction >= res.threshold
            res["alert_at_frozen"] = res.prediction >= FROZEN
        else:
            res = res.drop(columns="threshold")
        return res
