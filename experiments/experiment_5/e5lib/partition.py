"""s05 partition shared by both task nodes (blueprint spec/blueprints/s05_partition.md).

Written for Experiment 5 from the blueprint; no code or numbers from earlier experiments.

- order and test cohort (5.1, 5.2): eligible orders on or after the s02 cutoff, frozen in test_manifest.csv
- test-side purge (5.3, G-18): test orders of customers seen in development are removed
- test checks (5.4, G-46): size shares per task; failure stops the run (no random fallback)
- folds (5.5-5.7): five expanding, time-ordered folds with equal-sized validation blocks by order count,
  training-side customer purge and label maturity
- class support and training size (5.8, G-53): minimums pre-registered in protocol.yaml cv.minimums
"""
from __future__ import annotations

import numpy as np
import pandas as pd

STAGE = "s05_partition"
LABEL = {"regression": ("lead_days", "lead_label_ts"), "classification": ("is_detractor", "review_label_ts")}


def block_starts(ts: pd.Series, n_folds: int) -> list[tuple[int, int]]:
    """(start, end) row positions of the validation blocks on time-sorted rows.

    Equal-sized blocks of n // (n_folds + 1) rows at the end of the data (TimeSeriesSplit layout). A block
    start that falls inside a run of equal timestamps moves forward to the first new timestamp, so that
    training stays strictly before validation.
    """
    n = len(ts)
    size = n // (n_folds + 1)
    v = ts.to_numpy()
    out = []
    for k in range(n_folds):
        start = n - (n_folds - k) * size
        end = start + size if k < n_folds - 1 else n
        while 0 < start < end and v[start] == v[start - 1]:
            start += 1
        out.append((start, end))
    return out


def build_folds(dev: pd.DataFrame, task: str, cutoff: pd.Timestamp, n_folds: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (folds rows, per-fold summary). dev must be sorted by purchase_ts."""
    y, lab_ts = LABEL[task]
    rows, summary = [], []
    for k, (start, end) in enumerate(block_starts(dev["purchase_ts"], n_folds), start=1):
        val = dev.iloc[start:end]
        val_start = val["purchase_ts"].min()
        tr = dev.iloc[:start]
        n_tr0, n_val0 = len(tr), len(val)
        shared = tr["customer_unique_id"].isin(set(val["customer_unique_id"]))
        tr = tr[~shared]
        immature_tr = ~(tr[lab_ts] < val_start)
        tr = tr[~immature_tr]
        immature_val = ~(val[lab_ts] < cutoff)
        val = val[~immature_val]
        s = {"fold": k, "train_start": str(tr["purchase_ts"].min()), "train_end": str(tr["purchase_ts"].max()),
             "validation_start": str(val_start), "validation_end": str(val["purchase_ts"].max()),
             "train_rows_before": n_tr0, "purged_customers_rows": int(shared.sum()),
             "train_immature_rows": int(immature_tr.sum()), "train_rows": len(tr),
             "validation_rows_before": n_val0, "validation_immature_rows": int(immature_val.sum()),
             "validation_rows": len(val)}
        if task == "classification":
            s.update({"train_positives": int(tr[y].sum()), "train_prevalence": float(tr[y].mean()),
                      "validation_positives": int(val[y].sum()), "validation_prevalence": float(val[y].mean())})
        else:
            s.update({"train_mean_lead_days": float(tr[y].mean()), "validation_mean_lead_days": float(val[y].mean())})
        summary.append(s)
        for role, part in (("train", tr), ("validation", val)):
            rows.append(pd.DataFrame({"order_id": part["order_id"].to_numpy(), "fold": k, "role": role,
                                      "purchase_ts": part["purchase_ts"].to_numpy()}))
    return pd.concat(rows, ignore_index=True), pd.DataFrame(summary)


def run(task: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from . import cv, data, protocol
    from .outputs import Writer

    w = Writer(STAGE, task)
    p = protocol.load()
    seed = int(p["seed"])
    n_folds = int(p["cv"]["n_folds"])
    mins = p["cv"]["minimums"]
    sc = p["split"]["size_checks"][task]
    y, lab_ts = LABEL[task]
    cutoff = pd.Timestamp(protocol.get("data_dependent.test_cutoffs.values")[task])

    # 5.1 Order -------------------------------------------------------------------------------------
    allr = data.load("records", task, "all", STAGE)
    for c in (lab_ts,):
        allr[c] = pd.to_datetime(allr[c])
    allr = allr.sort_values(["purchase_ts", "order_id"], kind="mergesort").reset_index(drop=True)
    dev = allr[allr["purchase_ts"] < cutoff].reset_index(drop=True)
    test0 = allr[allr["purchase_ts"] >= cutoff]

    # 5.2-5.3 Test cohort and test-side purge ---------------------------------------------------------
    repeat = test0["customer_unique_id"].isin(set(dev["customer_unique_id"]))
    test = test0[~repeat]
    w.table("test_manifest", test[["order_id", "customer_unique_id", "purchase_ts"]], ids=("5.2", "5.3"))

    # 5.4 Test checks ---------------------------------------------------------------------------------
    n_all = len(allr)
    share_after = len(test) / n_all
    tchecks = []
    if task == "regression":
        tchecks.append(("min_share_of_eligible_delivered", "test keeps >= 15% of eligible delivered orders", share_after >= sc["min_share_of_eligible_delivered"],
                        f"{len(test):,} of {n_all:,} = {share_after:.2%}"))
        gap = {"development_mean_lead_days": float(dev[y].mean()), "test_mean_lead_days": float(test[y].mean()),
               "development_median_lead_days": float(dev[y].median()), "test_median_lead_days": float(test[y].median())}
    else:
        det_share = float(test[y].sum() / allr[y].sum())
        tchecks.append(("min_share_of_eligible_reviewed", "test keeps >= 15% of eligible reviewed orders", share_after >= sc["min_share_of_eligible_reviewed"],
                        f"{len(test):,} of {n_all:,} = {share_after:.2%}"))
        tchecks.append(("min_share_of_detractors", "test keeps >= 15% of all eligible detractors", det_share >= sc["min_share_of_detractors"],
                        f"{int(test[y].sum()):,} of {int(allr[y].sum()):,} = {det_share:.2%}"))
        gap = {"development_prevalence": float(dev[y].mean()), "test_prevalence": float(test[y].mean()),
               "prevalence_gap": float(test[y].mean() - dev[y].mean())}

    # 5.5-5.7 Folds -----------------------------------------------------------------------------------
    folds, summ = build_folds(dev, task, cutoff, n_folds)
    w.table("folds", folds, ids=("5.5", "5.6", "5.7"))
    w.table("fold_summary", summ, ids=("5.5", "5.6", "5.7", "5.8"))

    fig, ax = plt.subplots(figsize=(11, 4))
    for r in summ.itertuples():
        t0, t1 = pd.Timestamp(r.train_start), pd.Timestamp(r.train_end)
        v0, v1 = pd.Timestamp(r.validation_start), pd.Timestamp(r.validation_end)
        ax.barh(r.fold, (t1 - t0).days, left=t0, color="tab:blue", height=0.6)
        ax.barh(r.fold, max((v1 - v0).days, 1), left=v0, color="tab:orange", height=0.6)
        ax.text(v1, r.fold, f"  train {r.train_rows:,} / val {r.validation_rows:,}", va="center", fontsize=8)
    t_min, t_max = test["purchase_ts"].min(), test["purchase_ts"].max()
    ax.barh(n_folds + 1, (t_max - t_min).days, left=t_min, color="tab:red", height=0.6)
    ax.text(t_max, n_folds + 1, f"  test {len(test):,} (new customers)", va="center", fontsize=8)
    ax.set_yticks(list(range(1, n_folds + 1)) + [n_folds + 1])
    ax.set_yticklabels([f"fold {k}" for k in range(1, n_folds + 1)] + ["test"])
    ax.invert_yaxis()
    ax.set_title(f"{task}: expanding folds (blue train, orange validation) and test cohort (red)")
    fig.tight_layout()
    diagram = pd.concat([summ[["fold", "train_start", "train_end", "validation_start", "validation_end", "train_rows", "validation_rows"]],
                         pd.DataFrame([{"fold": "test", "validation_start": str(t_min), "validation_end": str(t_max),
                                        "validation_rows": len(test)}])], ignore_index=True)
    w.figure("partition_diagram", fig, diagram, ids=("5.5",), title="Partition diagram")
    plt.close(fig)

    # Protocol data-dependent entries (s05 owns them) --------------------------------------------------
    protocol.set_task_entry("fold_boundaries", task, [
        {"fold": int(r.fold), "train_end": r.train_end, "validation_start": r.validation_start,
         "validation_end": r.validation_end} for r in summ.itertuples()], STAGE)
    protocol.set_task_entry("min_training_rows", task, {"required": int(mins["training_rows_per_fold"]),
                                                        "observed_min": int(summ["train_rows"].min())}, STAGE)
    if task == "classification":
        protocol.set_task_entry("class_support", task, {"required_positives_per_part": int(mins["positives_per_part"]), "folds": [
            {"fold": int(r.fold), "train_positives": int(r.train_positives), "validation_positives": int(r.validation_positives)}
            for r in summ.itertuples()]}, STAGE)

    # counts.json and checks.json ------------------------------------------------------------------------
    counts = {"task": task, "test_cutoff": str(cutoff), "eligible_orders": n_all, "development_orders": len(dev),
              "development_customers": int(dev["customer_unique_id"].nunique()),
              "test_before_purge": len(test0), "test_purged_repeat_customer_orders": int(repeat.sum()),
              "test_orders": len(test), "test_customers": int(test["customer_unique_id"].nunique()),
              "test_share_of_eligible_after_purge": share_after,
              "test_share_removed_by_purge": float(repeat.sum() / len(test0)), "cohort_name": p["split"]["name"],
              "development_vs_test": gap, "folds": summ.to_dict(orient="records"), "seed": seed}
    if task == "classification":
        counts.update({"development_positives": int(dev[y].sum()), "test_positives": int(test[y].sum())})
    w.json("counts", counts, ids=("5.2", "5.3", "5.4", "5.8"))

    rules = cv.check_fold_rules(folds, allr)
    res = []
    def chk(name, ok, ids, detail=""):
        res.append({"check": name, "passed": bool(ok), "detail": detail, "ids": list(ids)})
        w.check(name, ok, ids=ids, detail=detail)
    chk("no test order_id or customer_unique_id in development",
        not set(test["order_id"]) & set(dev["order_id"]) and not set(test["customer_unique_id"]) & set(dev["customer_unique_id"]),
        ("5.2", "5.3"), f"{int(repeat.sum()):,} repeat-customer test orders removed")
    import yaml
    from .paths import spec_path
    accepted = {d["check"]: d for d in (((yaml.safe_load(spec_path("human_decisions.yaml").read_text(encoding="utf-8"))
                                          .get("s05") or {}).get(task) or {}).get("accepted_test_check_deviations") or [])}
    for key, name, ok, det in tchecks:
        if not ok and key in accepted:
            a = accepted[key]
            w.deviation("5.4", f"{name}: FAILED ({det}); accepted by the team as a protocol deviation (G-75): {a['rationale']} "
                               f"({a['decided_by']}, {a['date']})")
            chk(f"{name}, or a recorded team deviation", True, ("5.4",), f"{det}: below the minimum, accepted deviation G-75")
        else:
            chk(name, ok, ("5.4",), det)
    chk("never a random split: test is every eligible order on or after the cutoff, minus repeat customers",
        set(test0["order_id"]) == set(allr.loc[allr["purchase_ts"] >= cutoff, "order_id"]), ("5.2",))
    chk("every fold: max training purchase time < min validation purchase time",
        all(r["passed"] for r in rules if r["rule"] == "train_before_validation"), ("5.5",))
    chk("every fold: no shared customer_unique_id between training and validation",
        all(r["passed"] for r in rules if r["rule"] == "no_shared_customer"), ("5.6",))
    lab = allr.set_index("order_id")[lab_ts]
    vstart = summ.set_index("fold")["validation_start"].map(pd.Timestamp)
    tr_rows = folds[folds["role"] == "train"]
    va_rows = folds[folds["role"] == "validation"]
    chk("every fold: every training label observable before the validation block starts",
        bool((tr_rows["order_id"].map(lab).to_numpy() < tr_rows["fold"].map(vstart).to_numpy()).all()), ("5.7",),
        f"{int(summ['train_immature_rows'].sum()):,} training rows dropped over the folds")
    chk("every validation label observable before the test cutoff", bool((va_rows["order_id"].map(lab) < cutoff).all()), ("5.7",),
        f"{int(summ['validation_immature_rows'].sum()):,} validation rows dropped")
    chk(f"every fold: training rows >= {mins['training_rows_per_fold']:,} (G-53)",
        bool((summ["train_rows"] >= mins["training_rows_per_fold"]).all()), ("5.8",),
        "; ".join(f"fold {r.fold} is {r.train_rows:,}" for r in summ.itertuples()))
    if task == "classification":
        m = mins["positives_per_part"]
        chk(f"every fold: both classes present, >= {m} detractors in training and in validation",
            bool(((summ["train_positives"] >= m) & (summ["validation_positives"] >= m)
                  & (summ["train_rows"] > summ["train_positives"]) & (summ["validation_rows"] > summ["validation_positives"])).all()),
            ("5.8",), "; ".join(f"fold {r.fold} is {r.train_positives:,} / {r.validation_positives:,}" for r in summ.itertuples()))
    chk("five folds with equal-sized validation blocks before maturity drops",
        len(summ) == n_folds and summ["validation_rows_before"].iloc[:-1].max() - summ["validation_rows_before"].iloc[:-1].min()
        <= summ["validation_rows_before"].max() * 0.01, ("5.5",),
        ", ".join(f"{v:,}" for v in summ["validation_rows_before"]))
    w.json("checks", res, ids=("5.4", "5.5", "5.6", "5.7", "5.8"))

    # Evidence cards ----------------------------------------------------------------------------------------
    w.explain("5.1", done=f"{n_all:,} eligible {task} orders sorted by purchase_ts (ties by order_id): {len(dev):,} "
              f"development orders before the s02 cutoff {cutoff}, {len(test0):,} on or after it.")
    w.explain("5.2", done=f"Test cohort: every eligible order purchased on or after {cutoff}; after the purge "
              f"{len(test):,} order_ids frozen in test_manifest.csv ({test['purchase_ts'].min()} to {test['purchase_ts'].max()}).",
              conclusion="Defined only by this experiment's data and rules (G-38).")
    w.explain("5.3", done=f"{int(repeat.sum()):,} test orders ({repeat.mean():.2%}) belong to customers who also bought "
              f"in development and were removed. The {p['split']['name']} holds {len(test):,} orders, "
              f"{share_after:.2%} of eligible orders after the purge.")
    w.explain("5.4", done="; ".join(f"{n}: {'PASS' if ok else 'FAIL'} ({d})" for _, n, ok, d in tchecks) + ". "
              + ("Prevalence: development {development_prevalence:.2%}, test {test_prevalence:.2%} (gap {prevalence_gap:+.2%})."
                 .format(**gap) if task == "classification" else
                 "lead_days: development mean {development_mean_lead_days:.2f} / median {development_median_lead_days:.2f}; "
                 "test mean {test_mean_lead_days:.2f} / median {test_median_lead_days:.2f} days.".format(**gap)),
              reasoning="The test cohort is later in time; a gap here is the drift the test score has to face, not a "
                        "split error. No random fallback exists.")
    w.explain("5.5", done=f"{n_folds} expanding folds on development, validation blocks of "
              f"{summ['validation_rows_before'].iloc[0]:,} orders each (last block takes the remainder); boundaries "
              "written to protocol.yaml data_dependent.fold_boundaries; training strictly before validation in every fold.")
    w.explain("5.6", done="Training orders whose customer_unique_id appears in the fold's validation block removed: "
              + ", ".join(f"fold {r.fold} is {r.purged_customers_rows:,}" for r in summ.itertuples()) + " rows.")
    what = "delivery date" if task == "regression" else "review answer date"
    w.explain("5.7", done=f"A training order is used only if its answer ({y}, known on its {what}) was already known on the "
              "day its fold's validation block starts; a validation order only if its answer was known before the test "
              "cutoff. Dropped: " + ", ".join(f"fold {r.fold} is {r.train_immature_rows:,} train / "
                                              f"{r.validation_immature_rows:,} validation" for r in summ.itertuples()) + ".",
              reasoning="Each fold imitates training the model on the day the validation block starts. An order bought "
                        "before that day but delivered (or reviewed) after it had no answer yet on that day, so learning "
                        "from it would use information from the future. Most dropped rows are the last few weeks of "
                        "orders before each boundary, still in transit or not yet reviewed then.")
    w.explain("5.8", done="Training rows per fold: " + ", ".join(f"fold {r.fold} is {r.train_rows:,}" for r in summ.itertuples())
              + f" (minimum {mins['training_rows_per_fold']:,}, pre-registered)" + (
              "; detractors training / validation: " + ", ".join(f"fold {r.fold} is {r.train_positives:,} / {r.validation_positives:,}"
                                                                  for r in summ.itertuples()) + f" (minimum {mins['positives_per_part']})"
              if task == "classification" else "") + ".")
    w.finish(seed=seed)
    failed = [r["check"] for r in res if not r["passed"]]
    if failed:
        raise SystemExit(f"s05 {task}: checks failed, alert the team and stop (no random fallback): {failed}")
