"""B10: release of B's frozen models with A as fallback (blueprint pipeline_b/spec/blueprints/b10_release.md;
G-79, B-G-06, B-G-08, B-G-09, B10-D1 to D9).

No refit of a frozen model and no second test read. The test rows are rebuilt with T1's verified builder with every
label column blanked first (B-G-08), so parity, routing and input checks never see a test label. The only test labels
used are those already saved in T1's predictions_test.csv.gz, for B's results at 1/6 and 5/14 (B-G-09, as B9.10).

Evidence IDs: B10.1 parity, B10.2 release manifest, B10.3 serving configuration, B10.4 router, B10.5 input checks,
B10.6 drift profile, B10.7 app sources (with R-14 top routes and categories).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from e5lib import data, protocol
from e5lib.metrics import COST_FN, COST_FP
from e5lib.paths import E5, raw_data_dir
from e5lib.training import TARGET, predict

from . import b02
from . import history as h
from .b09 import A_RECORDS, A_S05
from .b09_extra import CAP, _at, _days
from .env import A_FROZEN_TAG, BWriter, _git, assert_a_frozen, b_outputs_dir
from .serving import B_OPERATING, FROZEN, MAX_DISTANCE_KM, NO_SCORE, Release, encoder_levels, in_scope
from .t1_joint_test import EVENTS_UNTIL, LABEL_TS, _sha_ok, b_rows

STAGE = "b10"
B_FROZEN_TAG, T1_TAG = "e5-B-frozen", "e5-T1-tested"
LABELS = ("lead_days", "lead_label_ts", "is_detractor", "is_detractor_first", "review_label_ts")
TOL = 1e-9
SD_OPTIONS = (3, 4, 5)        # out-of-profile thresholds shown for the team (B10.6); none is chosen here
MIN_VOLUME = 100              # orders per window to rank a route or category (R-14; G-40 convention)
TOP_N = 5


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _at_tag(tag: str, path: Path) -> bytes | None:
    try:
        return _git("show", f"{tag}:./{path.relative_to(E5).as_posix()}")
    except Exception:
        return None


def _blank_labels(d: pd.DataFrame) -> pd.DataFrame:
    """B-G-08: every label column emptied before the rows are used, so no test label is read."""
    d = d.copy()
    for c in LABELS:
        if c in d:
            d[c] = pd.NaT if c.endswith("_ts") else np.nan
    return d


def _dev_rows(task: str, w: BWriter, cutoff: pd.Timestamp) -> dict[str, pd.DataFrame]:
    """The final-fit rows of T1 (labels observable before the cutoff), to recompute digests and training ranges."""
    a_dev = data.load("records", task, "development", "s08_selection")
    a_dev[LABEL_TS[task]] = pd.to_datetime(a_dev[LABEL_TS[task]])
    b_dev = pd.read_csv(w.read(b_outputs_dir("b02", task) / "records_B.csv.gz"), parse_dates=["purchase_ts", LABEL_TS[task]],
                        low_memory=False)
    return {"A": a_dev[a_dev[LABEL_TS[task]] < cutoff].reset_index(drop=True),
            "B": b_dev[b_dev[LABEL_TS[task]] < cutoff].reset_index(drop=True)}


def run(task: str) -> None:
    assert_a_frozen()
    w = BWriter(STAGE, task)
    seed = int(protocol.load()["seed"])
    y_col = TARGET[task]
    cutoff = pd.Timestamp(protocol.get("data_dependent.test_cutoffs.values")[task])
    t1 = b_outputs_dir("t1_joint_test", task)
    recipe = {"A": E5 / f"stages/s08_selection/{task}/outputs/frozen_recipe.json", "B": b_outputs_dir("b08", task) / "frozen_recipe.json"}
    tags = {"A": A_FROZEN_TAG, "B": B_FROZEN_TAG}

    # test rows rebuilt without labels (B-G-08) ---------------------------------------------------------------
    saved = pd.read_csv(w.read(t1 / "predictions_test.csv.gz"), usecols=["order_id", "model", "rows", "y_pred"])
    kept = pd.read_csv(w.read(t1 / "test_rows_B.csv"))
    kept_ids = set(kept.order_id[kept.kept.astype(bool)])
    a = pd.read_csv(w.read(A_RECORDS), parse_dates=["purchase_ts", "review_label_ts", "lead_label_ts"], low_memory=False)
    man = pd.read_csv(w.read(Path(A_S05.format(task=task)) / "test_manifest.csv"))
    a_test = _blank_labels(a[a[f"eligible_{task}"].astype(bool) & a.order_id.isin(man.order_id)].reset_index(drop=True))
    for f in ("olist_orders_dataset.csv", "olist_order_items_dataset.csv", "olist_sellers_dataset.csv", "olist_customers_dataset.csv"):
        w.read(raw_data_dir() / f)
    ev = h.load_events(raw_data_dir(), EVENTS_UNTIL)
    cap = json.loads(w.read(b_outputs_dir("b02", "regression") / "feature_build_log.json").read_text())["lead_cap_days"]
    b_all, b_exc = b_rows(task, a_test, ev, cap if task == "regression" else None)   # blank labels: label rules remove nothing
    b_all = b_all.reset_index(drop=True)
    b_test = b_all[b_all.order_id.isin(kept_ids)].reset_index(drop=True)
    allowed = {"B_STATE", "B_DISTANCE"} | ({"B_NO_HANDOVER"} if task == "classification" else set())
    w.check("with labels blanked, only the label-free rules remove test rows (" + ", ".join(sorted(allowed)) + ")",
            set(b_exc.reason_code) <= allowed, ("B10.1",), "; ".join(f"{k} {v:,}" for k, v in b_exc.reason_code.value_counts().items()))
    label_free = all(a_test[c].isna().all() for c in LABELS if c in a_test)
    w.check("no test label is read: every label column of the rebuilt test rows is empty (B-G-08)", label_free, ("B10.1",),
            ", ".join(c for c in LABELS if c in a_test))
    w.check("the rebuilt rows contain exactly T1's kept B test rows", set(b_test.order_id) == kept_ids, ("B10.1",),
            f"{len(b_test):,} of {len(kept_ids):,}")

    # B10.1 parity ---------------------------------------------------------------------------------------------
    models = {p: joblib.load(w.read(t1 / f"bundles/{p}/model.joblib")) for p in "AB"}
    a_on_b = a_test.set_index("order_id").loc[b_test.order_id].reset_index()
    par = []
    for model, rows, p, X in (("A frozen", "A test rows", "A", a_test), ("A frozen", "B test rows", "A", a_on_b),
                              ("B frozen", "B test rows", "B", b_test)):
        ref = saved[(saved.model == model) & (saved.rows == rows)].set_index("order_id").y_pred
        re_ = predict(task, models[p], X)
        diff = np.abs(re_ - ref.loc[X.order_id].to_numpy())
        par.append({"model": model, "rows": rows, "n_rows": int(len(X)), "n_t1_rows": int(len(ref)),
                    "max_abs_diff": float(diff.max()), "within_tolerance": bool(diff.max() <= TOL and len(X) == len(ref))})
    parity = {"task": task, "tolerance": TOL, "labels_read": False, "decision": "B-G-08", "results": par,
              "python": __import__("platform").python_version(), "passed": all(r["within_tolerance"] for r in par)}
    w.json("parity", parity, ids=("B10.1",))
    w.check("every bundle reloads from disk and re-predicts T1's saved test predictions within 1e-9", parity["passed"], ("B10.1",),
            "; ".join(f"{r['model']} on {r['rows']}: max {r['max_abs_diff']:.1e} ({r['n_rows']:,} rows)" for r in par))
    if not parity["passed"]:
        w.finish(seed=seed)
        raise SystemExit(f"B10 {task}: parity failed; the release package is not built (B10.1)")

    # B10.2 release manifest --------------------------------------------------------------------------------------
    dev = _dev_rows(task, w, cutoff)
    import sklearn
    env_versions = {"sklearn": sklearn.__version__, "pandas": pd.__version__, "numpy": np.__version__}
    rel = {"task": task, "released": "B (inside B's scope); A as fallback outside it (B-G-06)", "bundles": {}}
    ok = True
    for p in "AB":
        rec_bytes = recipe[p].read_bytes()
        rec = json.loads(rec_bytes)
        schema = json.loads(w.read(t1 / f"bundles/{p}/schema.json").read_text())
        files = {n: _sha(w.read(t1 / f"bundles/{p}/{n}").read_bytes()) for n in ("model.joblib", "schema.json", "training_profile.json")}
        at_t1 = {n: _sha(b) if (b := _at_tag(T1_TAG, t1 / f"bundles/{p}/{n}")) is not None else None for n in files}
        at_tag = _at_tag(tags[p], w.read(recipe[p]))
        digest = _sha("".join(sorted(dev[p].order_id)).encode())
        e = {"files_sha256": files, "files_equal_t1_tag": {n: at_t1[n] == s for n, s in files.items()},
             "frozen_recipe": recipe[p].relative_to(E5).as_posix(), "frozen_recipe_tag": tags[p],
             "frozen_recipe_sha256_field": rec["sha256"], "recipe_recomputes_sha256": _sha_ok(rec),
             "recipe_equals_tagged_file": at_tag is not None and _sha(at_tag) == _sha(rec_bytes),
             "schema_frozen_sha256_matches": schema["frozen_sha256"] == rec["sha256"],
             "model": schema["model"], "calibration": schema["calibration"], "numeric": schema["numeric"],
             "categorical": schema["categorical"], "frozen_threshold": schema["threshold"],
             "training_rows": schema["training_rows"], "training_rows_recomputed": int(len(dev[p])),
             "training_id_digest_matches": digest == schema["training_id_digest"],
             "versions_bundle": schema["versions"], "versions_environment": env_versions,
             "version_differences": {k: [v, env_versions[k]] for k, v in schema["versions"].items() if env_versions.get(k) != v}}
        rel["bundles"][p] = e
        ok &= all(e["files_equal_t1_tag"].values()) and e["recipe_recomputes_sha256"] and e["recipe_equals_tagged_file"] \
            and e["schema_frozen_sha256_matches"] and e["training_id_digest_matches"] and e["training_rows"] == e["training_rows_recomputed"]
    w.json("release_manifest", rel, ids=("B10.2",))
    w.check("bundle files equal T1's tagged files; frozen recipes recompute their sha256, equal their tagged files and match the schemas; "
            "training rows and digests recompute", ok, ("B10.2",))
    w.check("the frozen thresholds in the bundles are unchanged (1/6 for classification)", task == "regression" or all(
        abs(rel["bundles"][p]["frozen_threshold"]["value"] - FROZEN) < 1e-15 for p in "AB"), ("B10.2", "B10.3"))

    # B10.3 serving configuration -------------------------------------------------------------------------------
    scope_test = in_scope(a_test)
    a_days = _days(a_test.purchase_ts)
    cfg = {"task": task, "scope_rule": "customer state and primary seller state in " + ", ".join(b02.STATES) + ", distance_km_max present (B-C1, B-C2)",
           "inside_scope": "B frozen (T1 bundles/B)", "outside_scope": "A frozen (T1 bundles/A), B-G-06",
           "prediction_moment": {"B": "checkout" if task == "regression" else "carrier handover", "A": "checkout"},
           "test_rows_by_scope": {"inside": int(scope_test.sum()), "outside": int((~scope_test).sum())}}
    results = None
    if task == "classification":
        tdays = _days(b_test.purchase_ts)
        lab = pd.read_csv(t1 / "predictions_test.csv.gz", usecols=["order_id", "model", "rows", "y_true", "y_pred"])
        bt = lab[(lab.model == "B frozen") & (lab.rows == "B test rows")]
        at_ = lab[(lab.model == "A frozen") & (lab.rows == "A test rows")].set_index("order_id").loc[a_test.order_id]
        # B10-D10: no refit here. Refits of the frozen recipes are not bit-reproducible across machines (WORKLOG
        # 2026-10-26), so validation figures are restated from B9's stored files; test figures use T1's saved predictions.
        b9 = pd.read_csv(w.read(b_outputs_dir("b09", task) / "threshold_options.csv"))
        b9c = pd.read_csv(w.read(b_outputs_dir("b09", task) / "threshold_options_curve.csv"))
        fb = pd.read_csv(w.read(b_outputs_dir("b09", task) / "a_fallback_by_scope.csv"))
        keep = ["threshold", "alerts", "alerts_per_day", "tp", "fp", "fn", "precision", "recall", "fp_per_tp", "cost_5_to_1", "cost_1_to_1"]
        rows = []
        v16 = b9[(b9.threshold_name == "frozen 1/6") & (b9.model == "B frozen") & (b9.rows == "validation (out-of-fold), B rows")].iloc[0]
        rows.append({"model": "B frozen", "threshold_name": "B frozen 1/6", "rows": "validation (out-of-fold), B rows",
                     **v16[keep].to_dict(), "source": "b09 threshold_options.csv (B9.10)"})
        for t_, side in ((0.36, "above"), (0.35, "below")):
            r = b9c[(b9c.period == "validation (out-of-fold)") & (b9c.threshold.round(4) == t_)].iloc[0]
            rows.append({"model": "B frozen", "threshold_name": f"B {t_:.2f} (nearest stored threshold {side} 5/14)",
                         "rows": "validation (out-of-fold), B rows", **r[keep].to_dict(), "source": "b09 threshold_options_curve.csv (B9.10)"})
        for name, t in (("B frozen 1/6", FROZEN), ("B operating 5/14 (B-G-09)", B_OPERATING)):
            rows.append({"model": "B frozen", "threshold_name": name, "rows": "test, B rows (post-test view)",
                         **_at(bt.y_true.to_numpy().astype(int), bt.y_pred.to_numpy(), t, tdays), "source": "T1 predictions_test.csv.gz"})
        # A outside B's scope on validation at 1/6: counts derived from B9.15 (TP = recall x detractors, alerts = TP / precision)
        a_folds = pd.read_csv(w.read(E5 / f"stages/s05_partition/{task}/outputs/folds.csv"))
        a_ts = a.set_index("order_id").purchase_ts
        out_f = fb[(fb.scope == "outside B's scope") & fb.period.str.startswith("fold")].copy()
        out_f["tp"] = out_f.recall * out_f.detractors
        out_f["alerts"] = out_f.tp / out_f.precision
        integral = bool(np.allclose(out_f[["tp", "alerts"]], out_f[["tp", "alerts"]].round(), atol=1e-6))
        out_f[["tp", "alerts"]] = out_f[["tp", "alerts"]].round().astype(int)
        vdays_a = sum(_days(a_ts.loc[a_folds[(a_folds.fold == k) & (a_folds.role == "validation")].order_id])
                      for k in sorted(a_folds.fold.unique()))
        tp_, al_, det_ = int(out_f.tp.sum()), int(out_f.alerts.sum()), int(out_f.detractors.sum())
        rows.append({"model": "A frozen", "threshold_name": "A frozen 1/6 (B10-D2)", "rows": "validation (out-of-fold), A rows outside B's scope",
                     "threshold": FROZEN, "alerts": al_, "alerts_per_day": al_ / vdays_a, "tp": tp_, "fp": al_ - tp_, "fn": det_ - tp_,
                     "precision": tp_ / al_, "recall": tp_ / det_, "fp_per_tp": (al_ - tp_) / tp_,
                     "cost_5_to_1": COST_FN * (det_ - tp_) + COST_FP * (al_ - tp_), "cost_1_to_1": det_ - tp_ + al_ - tp_,
                     "source": "derived from b09 a_fallback_by_scope.csv (B9.15) fold rows; days from A's s05 folds.csv"})
        out_t = at_.y_pred.to_numpy()[~scope_test.to_numpy()]
        fbt = fb[(fb.period == "test") & (fb.scope == "outside B's scope")].iloc[0]
        rows.append({"model": "A frozen", "threshold_name": "A frozen 1/6 (B10-D2)", "rows": "test, A rows outside B's scope",
                     "threshold": FROZEN, "alerts": int((out_t >= FROZEN).sum()), "alerts_per_day": float((out_t >= FROZEN).sum() / a_days),
                     "precision": fbt.precision, "recall": fbt.recall,
                     "source": "alerts counted from T1 predictions_test.csv.gz; precision and recall from b09 a_fallback_by_scope.csv (B9.15)"})
        results = pd.DataFrame(rows)
        w.table("threshold_results", results, ids=("B10.3",))
        b9t = b9[(b9.threshold_name == "frozen 1/6") & (b9.model == "B frozen") & (b9.rows == "test, B rows")].iloc[0]
        mt = results[(results.threshold_name == "B frozen 1/6") & (results.rows == "test, B rows (post-test view)")].iloc[0]
        w.check("B's 1/6 test results from T1's saved predictions equal B9 threshold_options.csv (alerts, TP, FP, FN)",
                all(int(mt[k]) == int(b9t[k]) for k in ("alerts", "tp", "fp", "fn")), ("B10.3",))
        w.check("A's out-of-scope fold counts derive exactly from B9.15 (TP and alerts are whole numbers)", integral, ("B10.3",),
                f"{al_:,} alerts, {tp_:,} TP over {vdays_a:.0f} validation days")
        g = lambda name, rws: results[(results.threshold_name == name) & (results.rows == rws)].iloc[0]
        lo = float(g("B 0.36 (nearest stored threshold above 5/14)", "validation (out-of-fold), B rows").alerts_per_day)
        hi = float(g("B 0.35 (nearest stored threshold below 5/14)", "validation (out-of-fold), B rows").alerts_per_day)
        a_v = float(g("A frozen 1/6 (B10-D2)", "validation (out-of-fold), A rows outside B's scope").alerts_per_day)
        b_t = float(g("B operating 5/14 (B-G-09)", "test, B rows (post-test view)").alerts_per_day)
        a_t = float(g("A frozen 1/6 (B10-D2)", "test, A rows outside B's scope").alerts_per_day)
        vol = {"validation": {"B_inside_at_5_14": {"between": [lo, hi], "note": "bracketed by B9's stored 0.36 and 0.35 rows (no refit, B10-D10)"},
                              "A_outside_at_1_6": a_v, "combined_alerts_per_day": {"between": [lo + a_v, hi + a_v]}},
               "test": {"B_inside_at_5_14": b_t, "A_outside_at_1_6": a_t, "combined_alerts_per_day": b_t + a_t}}
        waiting = scope_test & ~a_test.order_id.isin(b_all.order_id)
        cfg.update({
            "thresholds": {"B_operating": {"value": B_OPERATING, "label": "5/14", "decision": "B-G-09", "applies_to": "sigmoid-calibrated probability"},
                           "B_frozen": {"value": FROZEN, "label": "1/6", "decision": "frozen at B8.5 (e5-B-frozen); unbiased test result",
                                        "daily_alert_cap": rel["bundles"]["B"]["frozen_threshold"]["daily_alert_cap"]},
                           "A_fallback": {"value": FROZEN, "label": "1/6", "decision": "B10-D2 (A's frozen threshold)"}},
            "review_alert_cap_per_day": CAP,
            "before_handover": {"rule": NO_SCORE, "decision": "B10-D9", "test_rows_in_scope_not_handed_over": int(waiting.sum())},
            "expected_alerts_per_day": vol,
            "volumes_confirmed_by_team": {"confirmed": True, "by": "Henry for the team", "date": "2026-10-26",
                                          "note": "B at 5/14 gives fewer alerts/day than the 6/day asked at the B9 review; accepted (B10-D2)"}, "results_file": "threshold_results.csv"})
    cfg["out_of_profile"] = {"sd": None, "options": list(SD_OPTIONS), "note": "the team chooses the SD limit at the B10 review (B10.6)"}

    # B10.6 drift profile (written before the router so the router can read the training ranges) -----------------
    prof, beyond = {"task": task, "reference_test_drift": "b09 drift.csv (B9.4)", "bundles": {}}, []
    rel_rows = {"A": a_test, "B": b_test}
    tp_ok = True
    for p in "AB":
        schema, tp = json.loads((t1 / f"bundles/{p}/schema.json").read_text()), json.loads(w.read(t1 / f"bundles/{p}/training_profile.json").read_text())
        num = {}
        for c in schema["numeric"]:
            x = dev[p][c].astype(float)
            tp_ok &= abs(x.mean() - tp[c]["mean"]) < 1e-9 and abs(x.std() - tp[c]["std"]) < 1e-9
            num[c] = {"mean": tp[c]["mean"], "std": tp[c]["std"], "min": float(x.min()), "p01": float(x.quantile(0.01)),
                      "p99": float(x.quantile(0.99)), "max": float(x.max()), "missing_share": float(x.isna().mean())}
            z = ((rel_rows[p][c].astype(float) - tp[c]["mean"]) / tp[c]["std"]).abs() if tp[c]["std"] > 0 else pd.Series(0.0, index=rel_rows[p].index)
            beyond.append({"pipeline": p, "feature": c, "rows": f"{p} test rows", "n_rows": int(len(rel_rows[p])),
                           **{f"share_beyond_{k}sd": float((z > k).mean()) for k in SD_OPTIONS}})
        prof["bundles"][p] = {"numeric": num, "categorical_levels": encoder_levels(models[p])}
    w.json("drift_profile", prof, ids=("B10.6",))
    w.table("out_of_profile_shares", pd.DataFrame(beyond), ids=("B10.6",))
    w.check("the training profile in each bundle recomputes from T1's final-fit rows (mean and SD within 1e-9)", tp_ok, ("B10.6",))
    cfg["out_of_profile"]["numeric"] = {p: {c: {k: v[k] for k in ("mean", "std", "min")} for c, v in prof["bundles"][p]["numeric"].items()} for p in "AB"}
    w.json("serving_config", cfg, ids=("B10.3",))

    # B10.4 router ---------------------------------------------------------------------------------------------
    rls = Release(task, cfg)
    bcols = [c for c in b_all.columns if c not in a_test.columns]
    inp = a_test.merge(b_all[["order_id"] + bcols], on="order_id", how="left")
    routed = rls.predict(inp).set_index("order_id")
    ref_a = saved[(saved.model == "A frozen") & (saved.rows == "A test rows")].set_index("order_id").y_pred
    ref_b = saved[(saved.model == "B frozen") & (saved.rows == "B test rows")].set_index("order_id").y_pred
    out_ids = a_test.order_id[~scope_test.to_numpy()]
    d_b = float(np.max(np.abs(routed.loc[b_test.order_id, "prediction"].to_numpy() - ref_b.loc[b_test.order_id].to_numpy())))
    d_a = float(np.max(np.abs(routed.loc[out_ids, "prediction"].to_numpy() - ref_a.loc[out_ids].to_numpy())))
    summary = routed.groupby(["scope_reason", "model", "status"], dropna=False).size().rename("orders").reset_index()
    rc = {"task": task, "max_abs_diff_B_rows": d_b, "max_abs_diff_A_outside_rows": d_a, "tolerance": TOL,
          "routes": summary.to_dict(orient="records"),
          "in_scope_scored_without_t1_reference": int(((routed.model == "B frozen") & ~routed.index.isin(b_test.order_id)).sum()),
          "note": "B rows outside T1's kept set (regression: above the lead cap; classification: review answered before handover) are "
                  "scored by B at serving time but have no T1 prediction to compare with"}
    w.json("router_check", rc, ids=("B10.4",))
    w.check("the router reproduces T1's predictions: B on B's test rows and A on the out-of-scope rows (within 1e-9)", max(d_a, d_b) <= TOL,
            ("B10.4",), f"B {d_b:.1e}, A {d_a:.1e}")
    w.check("no test row is rejected by the input checks", not routed.status.str.startswith("rejected").any(), ("B10.4", "B10.5"),
            f"{int(routed.status.str.startswith('rejected').sum())} rejected")
    reasons = set(routed.scope_reason)
    w.check("every scope reason and route occurs (in scope; customer state; seller state" + ("; before handover" if task == "classification" else "") + ")",
            {"in scope", "outside: customer state", "outside: seller state"} <= reasons
            and (task == "regression" or (routed.status == NO_SCORE).any()), ("B10.4",), str(sorted(reasons)))

    # B10.5 input checks ---------------------------------------------------------------------------------------
    base_b = inp[inp.order_id.isin(b_test.order_id)].iloc[[0]].reset_index(drop=True)
    base_a = inp[~scope_test.to_numpy()].iloc[[0]].reset_index(drop=True)
    num_b = rls.schemas["B"]["numeric"][0]
    neg_b = next(c for c in rls.schemas["B"]["numeric"] if cfg["out_of_profile"]["numeric"]["B"][c]["min"] >= 0 and c != num_b)
    cases = [("valid in-scope order", base_b, {}, "scored", "B frozen"),
             ("valid out-of-scope order", base_a, {}, "scored", "A frozen"),
             ("unknown customer state", base_b, {"customer_state": "XX"}, "rejected", "unknown state"),
             ("negative distance", base_b, {"distance_km_max": -5.0}, "rejected", "impossible distance"),
             ("distance beyond Brazil", base_b, {"distance_km_max": MAX_DISTANCE_KM + 1}, "rejected", "impossible distance"),
             ("no items", base_b, {"n_items": 0}, "rejected", "no items"),
             ("missing installments", base_b, {"payment_installments_max": np.nan}, "rejected", "missing installments"),
             ("text in a numeric feature", base_b, {num_b: "abc"}, "rejected", "type"),
             ("negative value where training has none", base_b, {neg_b: -1.0}, "rejected", "negative value"),
             ("missing numeric value (imputed)", base_b, {num_b: np.nan}, "scored", "missing value"),
             ("unseen category (ignored)", base_b, {"primary_category": "not_a_category"}, "scored", "unseen category"),
             ("distance missing: out of scope", base_b, {"distance_km_max": np.nan}, "scored", "A frozen")]
    if task == "classification":
        cases.append(("in scope, not yet handed over", base_b, {"order_handed_over_late": np.nan}, NO_SCORE, ""))
    cres = []
    for name, base, change, expect, detail in cases:
        x = base.copy()
        for k, v in change.items():
            x[k] = x[k].astype(object) if isinstance(v, str) else x[k]
            x[k] = v
        x["order_id"] = f"case-{len(cres) + 1}"
        r = rls.predict(x).iloc[0]
        iss = rls.check(x)
        rules = sorted(set(iss.rule)) if len(iss) else []
        passed = r.status.startswith(expect) and (detail == "" or detail in rules or r.model == detail)
        cres.append({"case": name, "change": {k: (None if v is np.nan else v) for k, v in change.items()}, "expected": f"{expect} ({detail})" if detail else expect,
                     "status": r.status, "model": r.model, "rules": rules, "passed": bool(passed)})
    rules_doc = [{"rule": "missing column", "level": "error", "source": "bundle schema.json (numeric, categorical) and the scope columns"},
                 {"rule": "unknown state", "level": "error", "source": "Brazil's 27 state codes"},
                 {"rule": "type", "level": "error", "source": "numeric features in schema.json"},
                 {"rule": "impossible distance", "level": "error", "source": f"0 to {MAX_DISTANCE_KM:,.0f} km"},
                 {"rule": "no items", "level": "error", "source": "n_items >= 1 (A's s10 10.5)"},
                 {"rule": "missing installments", "level": "error", "source": "A's s10 10.5"},
                 {"rule": "negative value", "level": "error", "source": "numeric features whose training minimum is >= 0 (drift_profile.json)"},
                 {"rule": "missing value", "level": "warning", "source": "the bundle imputes the training median"},
                 {"rule": "unseen category", "level": "warning", "source": "levels of the bundle's one-hot encoder (ignored when unseen)"},
                 {"rule": "out of profile", "level": "warning", "source": "drift_profile.json; off until the team sets the SD limit (B10.6)"}]
    dd = pd.read_csv(w.read(E5 / "stages/s02_data/common/outputs/data_dictionary.csv"))
    w.json("input_validation", {"task": task, "rules": rules_doc, "cases": cres,
                                "data_dictionary_columns": sorted(set(dd.column) & set(rls.schemas["A"]["numeric"] + rls.schemas["B"]["numeric"]))},
           ids=("B10.5",))
    w.check("every input-check case gives the expected outcome", all(c["passed"] for c in cres), ("B10.5",),
            "; ".join(c["case"] for c in cres if not c["passed"]) or f"{len(cres)} cases")

    # B10.7 app sources and R-14 ------------------------------------------------------------------------------------
    st = lambda s: b_outputs_dir(s, task)
    panels = [("headline", "test metrics of A and B", "t1_joint_test", "metrics_test.csv", "T1.3"),
              ("headline", "train, validation and test with 95% intervals", "b09", "train_val_test.csv", "B9.1"),
              ("headline", "B minus A on the same test orders", "b09", "paired_test_differences.csv", "B9.2"),
              ("fit", "validation folds and test together", "b09", "validation_and_test.csv", "B9.14"),
              ("fit", "fold-by-fold and test table", "t1_joint_test", "fold_and_test_table.csv", "T1.6"),
              ("where it errs", "slices by state, route and more", "b09", "subgroups.csv", "B9.3"),
              ("where it errs", "business summary by route", "b09", "business_by_route.csv", "B9.13"),
              ("why", "coefficients", "b09", "coefficients.csv", "B9.5"),
              ("why", "permutation importance", "b09", "permutation_importance.csv", "B9.5"),
              ("data health", "drift, development vs test", "b09", "drift.csv", "B9.4"),
              ("data health", "training profile and out-of-profile shares", "b10", "drift_profile.json", "B10.6"),
              ("score", "serving rule and thresholds", "b10", "serving_config.json", "B10.3"),
              ("score", "input checks", "b10", "input_validation.json", "B10.5"),
              ("fallback", "A inside and outside B's scope", "b09", "a_fallback_by_scope.csv", "B9.15")]
    if task == "classification":
        panels += [("policy", "B at 1/6 and 5/14, A out of scope at 1/6", "b10", "threshold_results.csv", "B10.3"),
                   ("fit", "PR, ROC and reliability on B's test rows", "t1_joint_test", "figures/test_curves.png", "T1.4"),
                   ("fit", "confusion matrices at 1/6", "t1_joint_test", "confusion_test.csv", "T1.4"),
                   ("policy", "missed-dispatch rule on the test period", "b09", "missed_dispatch_rule_test.csv", "B9.7"),
                   ("why", "label sensitivity", "b09", "label_sensitivity.csv", "B9.6")]
    else:
        panels += [("fit", "residual distribution and promise buffers", "b09", "residuals_summary.csv", "B9.16"),
                   ("fit", "errors on B's test rows", "t1_joint_test", "figures/test_errors.png", "T1.3")]
    src, src_ok = [], True
    for panel, what, stage, f, eid in panels:
        path = st(stage) / f
        if stage == "b10":
            exists, has_id = True, True   # written by this run; tagged below
        else:
            idx = json.loads((st(stage) / "_evidence_index.json").read_text())
            exists, has_id = path.exists(), eid in idx["files"].get(f, {}).get("ids", [])
        src_ok &= exists and has_id
        src.append({"panel": panel, "element": what, "file": path.relative_to(E5).as_posix(), "evidence_id": eid,
                    "exists": exists, "id_tagged": has_id})
    # R-14 (B10-D7): top routes and categories by quarter, observed outcomes on B's development rows
    bd = dev["B"].copy()
    bd["window"] = bd.purchase_ts.dt.to_period("Q").astype(str)
    coef = pd.read_csv(w.read(st("b09") / "coefficients.csv")).set_index("term").coefficient
    top = []
    for dim in (b02.ROUTE, "primary_category"):
        g = bd.groupby(["window", dim])[y_col].agg(orders="size", outcome="mean").reset_index()
        g = g[g.orders >= MIN_VOLUME].sort_values(["window", "outcome", dim], ascending=[True, False, True])
        g["rank"] = g.groupby("window").cumcount() + 1
        g = g[g["rank"] <= TOP_N].rename(columns={dim: "level"}).assign(dimension=dim)
        g["coefficient"] = [coef.get(f"{dim}_{lv}", np.nan) for lv in g.level]
        top.append(g)
    top = pd.concat(top, ignore_index=True)[["window", "dimension", "rank", "level", "orders", "outcome", "coefficient"]]
    top.insert(6, "outcome_name", "mean lead_days (observed)" if task == "regression" else "detractor share (observed)")
    w.table("top_routes_categories", top, ids=("B10.7",))
    src.append({"panel": "dashboard (R-14)", "element": "top 5 routes and categories by quarter", "file": f"pipeline_b/stages/b10/{task}/outputs/top_routes_categories.csv",
                "evidence_id": "B10.7", "exists": True, "id_tagged": True})
    w.json("app_sources", {"task": task, "rule": "the app reads these files only and computes no statistic (A's s10 10.5)", "elements": src}, ids=("B10.7",))
    w.check("every app element names an existing file tagged with its evidence ID", src_ok, ("B10.7",), f"{len(src)} elements")
    w.check("A's tree untouched: A's code matches e5-A-frozen", bool(assert_a_frozen()), ("B10.2",))

    # cards ----------------------------------------------------------------------------------------------------------
    w.explain("B10.1", done=("Bundles reloaded from disk re-predict T1's saved test predictions on rows rebuilt with every label column empty (B-G-08): "
                             + "; ".join(f"{r['model']} on {r['rows']} max difference {r['max_abs_diff']:.1e} over {r['n_rows']:,} rows" for r in par)
                             + f". Python {parity['python']}."))
    w.explain("B10.2", done=("Release manifest: sha256 of every bundle file (equal to tag e5-T1-tested), frozen recipes equal to their tags "
                             f"(A {A_FROZEN_TAG}, B {B_FROZEN_TAG}), training digests recomputed. Version differences: "
                             + (json.dumps({p: rel['bundles'][p]['version_differences'] for p in 'AB'}) )))
    if task == "classification":
        v, t = cfg["expected_alerts_per_day"]["validation"], cfg["expected_alerts_per_day"]["test"]
        w.explain("B10.3", done=(f"Serving: B inside its scope at 5/14 (B-G-09), frozen 1/6 kept beside it; A outside at 1/6 (B10-D2). Expected alerts/day, "
                                 f"validation: B {v['B_inside_at_5_14']['between'][0]:.1f} to {v['B_inside_at_5_14']['between'][1]:.1f} (bracketed, no refit, B10-D10) "
                                 f"+ A {v['A_outside_at_1_6']:.1f}; test (post-test view): B {t['B_inside_at_5_14']:.1f} + A {t['A_outside_at_1_6']:.1f} "
                                 f"= {t['combined_alerts_per_day']:.1f}. Volumes accepted by the team (Henry, 2026-10-26; threshold_results.csv)."))
    else:
        w.explain("B10.3", done=(f"Serving: B inside its scope, A outside (B-G-06), both at checkout. Test rows inside {cfg['test_rows_by_scope']['inside']:,}, "
                                 f"outside {cfg['test_rows_by_scope']['outside']:,}."))
    w.explain("B10.4", done=(f"Router (e5b/serving.py) on every A test row: reproduces T1 within {max(d_a, d_b):.1e}. Routes: "
                             + "; ".join(f"{r['scope_reason']} / {r['model'] or '-'} / {r['status']}: {r['orders']:,}" for r in rc['routes'])))
    w.explain("B10.5", done=f"{len(rules_doc)} input rules; {sum(c['passed'] for c in cres)} of {len(cres)} test cases give the expected outcome (input_validation.json).")
    w.explain("B10.6", done=("Training ranges per feature from T1's final-fit rows; shares of test rows beyond 3, 4 and 5 SD in out_of_profile_shares.csv. "
                             "The SD limit is the team's choice (off until set)."))
    w.explain("B10.7", done=(f"{len(src)} app elements mapped to files and evidence IDs (app_sources.json); R-14 top {TOP_N} routes and categories per quarter "
                             f"with at least {MIN_VOLUME} orders, observed outcomes on development rows, coefficient beside (top_routes_categories.csv)."))
    w.finish(seed=seed)
    if w.index["checks_failed"]:
        raise SystemExit(f"B10 {task}: checks failed: {w.index['checks_failed']}")
    print(f"B10 {task}: parity max {max(r['max_abs_diff'] for r in par):.1e}; {len(cres)} input cases; {len(src)} app elements")
