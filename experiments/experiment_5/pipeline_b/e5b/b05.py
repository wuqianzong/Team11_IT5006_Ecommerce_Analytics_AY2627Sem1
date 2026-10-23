"""B5: partition for Pipeline B (blueprint pipeline_b/spec/blueprints/b05_partition.md; G-79, B-G-01).

B's folds are A's s05 folds restricted to B's development rows: no new boundaries, purge or order.
Minimums are A's (protocol cv.minimums); fold 1's training-row shortfall is accepted under B-G-01
within its safeguard (5,000 training rows; classification 300 training detractors).

Evidence IDs: B5.1 fold membership, B5.2 sizes and class support, B5.3 minimums and safeguard.
"""
from __future__ import annotations

import pandas as pd

from e5lib import protocol
from e5lib.paths import E5

from .env import BWriter, assert_a_frozen, b_outputs_dir

STAGE = "b05"
A_S05 = "stages/s05_partition/{task}/outputs"
SAFEGUARD_TRAIN_ROWS = 5000     # B-G-01, fold 1
SAFEGUARD_TRAIN_POS = 300       # B-G-01, fold 1, classification
DEVIATION_FOLD = 1              # B-G-01


def run(task: str) -> None:
    assert_a_frozen()
    w = BWriter(STAGE, task)
    seed = int(protocol.load()["seed"])
    mins = protocol.get("cv.minimums")
    min_rows, min_pos = int(mins["training_rows_per_fold"]), int(mins["positives_per_part"])
    a_dir = E5 / A_S05.format(task=task)
    folds = pd.read_csv(w.read(a_dir / "folds.csv"))
    a_sum = pd.read_csv(w.read(a_dir / "fold_summary.csv"))
    test = pd.read_csv(w.read(a_dir / "test_manifest.csv"), usecols=["order_id"])
    cls = task == "classification"
    rec = pd.read_csv(w.read(b_outputs_dir("b02", task) / "records_B.csv.gz"),
                      usecols=["order_id"] + (["is_detractor"] if cls else []))

    # B5.1 membership: A's (fold, role) rows whose order is a B row ---------------------------------
    fb = folds[folds.order_id.isin(rec.order_id)].sort_values(["fold", "role", "purchase_ts", "order_id"]).reset_index(drop=True)
    out_rows = rec[~rec.order_id.isin(folds.order_id)]
    exc = pd.DataFrame({"order_id": out_rows.order_id.sort_values().to_numpy(), "task": task, "reason_code": "NOT_IN_A_FOLDS"})
    w.table("folds_B", fb, ids=("B5.1",))
    w.table("exclusions_B5", exc, ids=("B5.1",))

    # B5.2 sizes and class support ------------------------------------------------------------------
    m = fb.merge(rec, on="order_id", how="left")
    rows = []
    for k, a in a_sum.set_index("fold").iterrows():
        r = {"fold": k, "a_train_start": a.train_start, "a_train_end": a.train_end,
             "a_validation_start": a.validation_start, "a_validation_end": a.validation_end}
        for role, pre in (("train", "train"), ("validation", "validation")):
            part = m[(m.fold == k) & (m.role == role)]
            r[f"{pre}_rows"] = len(part)
            r[f"{pre}_first"], r[f"{pre}_last"] = part.purchase_ts.min(), part.purchase_ts.max()
            r[f"a_{pre}_rows"] = int(a[f"{pre}_rows"])
            if cls:
                r[f"{pre}_positives"] = int(part.is_detractor.sum())
                r[f"{pre}_prevalence"] = float(part.is_detractor.mean())
        rows.append(r)
    summ = pd.DataFrame(rows)
    w.table("fold_summary_B", summ, ids=("B5.2",))

    # B5.3 minimums and safeguard -------------------------------------------------------------------
    mrows = []
    for r in summ.itertuples():
        ok = r.train_rows >= min_rows
        status = "PASS" if ok else ("ACCEPTED DEVIATION (B-G-01)" if r.fold == DEVIATION_FOLD and r.train_rows >= SAFEGUARD_TRAIN_ROWS else "FAIL")
        mrows.append({"fold": r.fold, "minimum": "training rows", "required": min_rows, "observed": r.train_rows, "status": status})
        if cls:
            for pre in ("train", "validation"):
                v = getattr(r, f"{pre}_positives")
                mrows.append({"fold": r.fold, "minimum": f"{pre} detractors", "required": min_pos, "observed": v,
                              "status": "PASS" if v >= min_pos else "FAIL"})
    f1 = summ.set_index("fold").loc[DEVIATION_FOLD]
    mrows.append({"fold": DEVIATION_FOLD, "minimum": "B-G-01 safeguard: training rows", "required": SAFEGUARD_TRAIN_ROWS,
                  "observed": int(f1.train_rows), "status": "PASS" if f1.train_rows >= SAFEGUARD_TRAIN_ROWS else "FAIL"})
    if cls:
        mrows.append({"fold": DEVIATION_FOLD, "minimum": "B-G-01 safeguard: training detractors", "required": SAFEGUARD_TRAIN_POS,
                      "observed": int(f1.train_positives), "status": "PASS" if f1.train_positives >= SAFEGUARD_TRAIN_POS else "FAIL"})
    mn = pd.DataFrame(mrows)
    w.table("minimums_B", mn, ids=("B5.3",))

    # checks ----------------------------------------------------------------------------------------
    key = ["order_id", "fold", "role"]
    w.check("every B fold row exists in A's folds.csv with the same fold and role",
            len(fb.merge(folds[key], on=key)) == len(fb), ("B5.1",), f"{len(fb):,} fold rows")
    w.check("no B fold row is in A's test manifest; every fold order is a B2 row",
            not fb.order_id.isin(test.order_id).any() and fb.order_id.isin(rec.order_id).all(), ("B5.1",))
    n_in = fb.order_id.nunique()
    w.check("B2 rows = orders in B folds + NOT_IN_A_FOLDS rows", len(rec) == n_in + len(exc), ("B5.1",),
            f"{len(rec):,} = {n_in:,} + {len(exc):,}")
    w.check("B folds keep A's periods: every B row lies inside A's fold boundaries",
            bool(((summ.train_first >= summ.a_train_start) & (summ.train_last <= summ.a_train_end)
                  & (summ.validation_first >= summ.a_validation_start) & (summ.validation_last <= summ.a_validation_end)).all()), ("B5.2",))
    bad = mn[mn.status == "FAIL"]
    w.check("minimums met, or fold 1's training-row shortfall accepted under B-G-01 within its safeguard", bad.empty, ("B5.3",),
            "; ".join(f"fold {r.fold} {r.minimum} {r.observed:,} < {r.required:,}" for r in bad.itertuples()) or
            "; ".join(f"fold {r.fold} {r.minimum} {r.observed:,}" for r in mn[mn.status.str.startswith("ACCEPTED")].itertuples()))

    # cards -----------------------------------------------------------------------------------------
    w.explain("B5.1", done=f"A's five folds restricted to B's rows: {len(fb):,} fold rows covering {n_in:,} B orders; "
              f"{len(exc):,} B2 rows are outside A's folds (A's customer purge or label maturity) and are not used.")
    w.explain("B5.2", done="Per fold, training / validation rows: " + "; ".join(
        f"{r.fold}: {r.train_rows:,} / {r.validation_rows:,}" + (f" ({r.train_positives:,} / {r.validation_positives:,} detractors)" if cls else "")
        for r in summ.itertuples()) + ".")
    dev = mn[mn.status.str.startswith("ACCEPTED")]
    w.explain("B5.3", done=f"Minimums: {(mn.status == 'PASS').sum()} PASS, {len(dev)} accepted deviation, {len(bad)} FAIL. "
              + ("; ".join(f"Fold {r.fold} {r.minimum}: {r.observed:,} of {r.required:,} (B-G-01)" for r in dev.itertuples()) or "No deviation") + ".")
    w.finish(seed=seed)
    if w.index["checks_failed"]:
        raise SystemExit(f"B5 {task}: checks failed: {w.index['checks_failed']}")
    print(f"B5 {task}: {len(fb):,} fold rows, {n_in:,} orders; fold 1 train {int(f1.train_rows):,}")
