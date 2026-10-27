"""B12: Milestone 2 feedback checks (blueprint pipeline_b/spec/blueprints/b12_m2_checks.md; TA points 3 and 10).

B12.1 feature-ranking stability inside the folds (both tasks); B12.2 promise-buffer curve (regression).
Description only: no feature set, model, calibration or threshold changes, no refit of a frozen recipe and no
second test read. B12.1 uses development rows only; B12.2 reads labels already saved by B8 (out-of-fold) and
T1 (test), as B9 and B10 did.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from e5lib import eda, features as af, protocol
from e5lib.paths import E5

from . import b02, b04
from .b09_extra import a_rec_id
from .env import BWriter, assert_a_frozen, b_outputs_dir

STAGE = "b12"
BUFFERS = np.round(np.arange(0, 30.01, 0.5), 1)   # validation residuals are heavy-tailed (B9.16: 95th percentile about 17 days)
TARGETS = (0.90, 0.95)
MIN_SLICE = 100


def _select(d: pd.DataFrame, task: str, seed: int, threshold: float) -> tuple[list[str], pd.DataFrame]:
    """B4's ranking, reduction and selection (B4.2, B4.3) on the rows given."""
    pool = b04.b_pool(task)
    values, _ = b04.importance(d, task, pool, seed)
    rank = eda.cumulative_ranking(values, "B pool")
    core, _ = b04.reduce(d, pool, dict(zip(rank["feature"], rank["rank"])))
    sel_rank, selected = af.selection(rank, core, threshold)
    return selected, sel_rank


def _ranking_stability(w: BWriter, task: str, seed: int) -> None:
    threshold = af.decisions(task)["threshold"]
    d = pd.read_csv(w.read(b_outputs_dir("b02", task) / "records_B.csv.gz"), low_memory=False)
    folds = pd.read_csv(w.read(b_outputs_dir("b05", task) / "folds_B.csv"))
    accepted = json.loads(w.read(b_outputs_dir("b04", task) / "selected_features_B.json").read_text(encoding="utf-8"))["selected"]

    full_sel, full_rank = _select(d, task, seed, threshold)
    w.check("recomputing B4 on all development rows gives B4's accepted selected set", full_sel == accepted, ("B12.1",),
            f"{len(full_sel)} features")
    full_pos = dict(zip(full_rank["feature"], full_rank["rank"]))

    rows, per_feature = [], {f: [] for f in full_rank["feature"]}
    train_only = True
    for k in sorted(folds.fold.unique()):
        ids = folds[(folds.fold == k) & (folds.role == "train")].order_id
        dk = d[d.order_id.isin(ids)]
        train_only &= not folds[(folds.fold == k) & (folds.role != "train")].order_id.isin(dk.order_id).any()
        sel, rk = _select(dk, task, seed, threshold)
        pos = dict(zip(rk["feature"], rk["rank"]))
        common = [f for f in full_rank["feature"] if f in pos]
        rho = spearmanr([full_pos[f] for f in common], [pos[f] for f in common]).statistic
        a, b = set(accepted), set(sel)
        rows.append({"fold": int(k), "training_rows": len(dk), "selected": len(sel), "jaccard_with_B4": len(a & b) / len(a | b),
                     "added_vs_B4": ", ".join(sorted(b - a)), "dropped_vs_B4": ", ".join(sorted(a - b)),
                     "spearman_ranks_vs_B4": rho})
        for f in per_feature:
            per_feature[f].append((pos.get(f), f in b))
    w.check("every fold ranks on its training rows only", bool(train_only), ("B12.1",))
    by_fold = pd.DataFrame(rows)
    w.table("ranking_stability_by_fold", by_fold, ids=("B12.1",))
    feats = pd.DataFrame([{"feature": f, "rank_all_development_rows": int(full_pos[f]), "selected_by_B4": f in accepted,
                           **{f"rank_fold_{i + 1}": (None if r is None else int(r)) for i, (r, _) in enumerate(v)},
                           "folds_selected": int(sum(s for _, s in v))} for f, v in per_feature.items()])
    w.table("ranking_stability_features", feats, ids=("B12.1",))
    always = int(((feats.selected_by_B4) & (feats.folds_selected == len(rows))).sum())
    summary = {"task": task, "threshold": threshold, "selected_by_B4": len(accepted), "folds": len(rows),
               "B4_features_selected_in_every_fold": always,
               "jaccard_min": float(by_fold.jaccard_with_B4.min()), "jaccard_mean": float(by_fold.jaccard_with_B4.mean()),
               "spearman_min": float(by_fold.spearman_ranks_vs_B4.min()),
               "features_ever_added": sorted({x for s in by_fold.added_vs_B4 for x in s.split(", ") if x}),
               "features_ever_dropped": sorted({x for s in by_fold.dropped_vs_B4 for x in s.split(", ") if x})}
    w.json("ranking_stability", summary, ids=("B12.1",))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    show = feats.sort_values("rank_all_development_rows")
    fig, ax = plt.subplots(figsize=(8, 0.5 + 0.32 * len(show)))
    for i, r in enumerate(show.itertuples()):
        fr = [getattr(r, f"rank_fold_{j}") for j in range(1, len(rows) + 1)]
        ax.scatter(fr, [i] * len(fr), s=14, color="#7f7f7f", zorder=2)
        ax.scatter([r.rank_all_development_rows], [i], s=28, marker="D", color="#1f77b4" if r.selected_by_B4 else "#bdbdbd", zorder=3)
    ax.set_yticks(range(len(show)), show.feature, fontsize=7)
    ax.invert_yaxis()
    ax.set(xlabel="importance rank (1 = most important)", title=f"B4 ranking on all development rows (diamond; blue = selected) vs each training fold (dots), {task}")
    fig.tight_layout()
    w.figure("ranking_stability", fig, feats, ids=("B12.1",), title="Feature-ranking stability inside the folds")
    plt.close(fig)
    w.explain("B12.1", done=(f"B4's ranking and {threshold:.0%} selection repeated on each fold's training rows: Jaccard overlap with B4's "
                             f"{len(accepted)} selected features {summary['jaccard_min']:.2f} to {by_fold.jaccard_with_B4.max():.2f} "
                             f"(mean {summary['jaccard_mean']:.2f}); {always} of {len(accepted)} B4 features selected in every fold; "
                             f"rank correlation with B4 at least {summary['spearman_min']:.2f}. Added in some fold: "
                             f"{', '.join(summary['features_ever_added']) or 'none'}; dropped in some fold: {', '.join(summary['features_ever_dropped']) or 'none'}."))


def _late(e: np.ndarray, b: float) -> float:
    return float(np.mean(e > b))


def _buffers(w: BWriter) -> None:
    task = "regression"
    t1 = pd.read_csv(w.read(b_outputs_dir("t1_joint_test", task) / "predictions_test.csv.gz"))
    bp = pd.read_csv(w.read(b_outputs_dir("b08", task) / "predictions.csv.gz"))
    bp = bp[bp.candidate_id == a_rec_id(task)]
    series = {"B on B's validation rows (out-of-fold)": bp, "B on B's test rows": t1[(t1.model == "B frozen") & (t1.rows == "B test rows")],
              "A on B's test rows": t1[(t1.model == "A frozen") & (t1.rows == "B test rows")],
              "A on A's test rows": t1[(t1.model == "A frozen") & (t1.rows == "A test rows")]}
    res = {k: (v.y_true - v.y_pred).to_numpy() for k, v in series.items()}

    curve = pd.DataFrame([{"series": k, "orders": len(e), "buffer_days": b, "share_late": _late(e, b), "share_on_time": 1 - _late(e, b)}
                          for k, e in res.items() for b in BUFFERS])
    w.table("buffer_curve", curve, ids=("B12.2",))
    rs = pd.read_csv(w.read(b_outputs_dir("b09", task) / "residuals_summary.csv")).set_index("series")
    eb = res["B on B's test rows"]
    same = all(abs(_late(eb, b) - rs.loc["B on B's test rows", f"share_more_than_{b}d_late"]) < 1e-12 for b in (3, 6))
    w.check("B's test residuals equal those behind B9.16 (late shares at 3 and 6 days)", same, ("B12.2",))

    ev, choice = res["B on B's validation rows (out-of-fold)"], []
    for t in TARGETS:
        ok = [b for b in BUFFERS if _late(ev, b) <= 1 - t]
        b = ok[0] if ok else None
        choice.append({"on_time_target": t, "buffer_days_chosen_on_validation": b,
                       "validation_share_late": None if b is None else _late(ev, b),
                       "test_share_late_B": None if b is None else _late(eb, b),
                       "test_share_late_A_on_B_rows": None if b is None else _late(res["A on B's test rows"], b),
                       "rule": f"smallest buffer on the 0.5-day grid with validation late share <= {1 - t:.0%}"})
    ch = pd.DataFrame(choice)
    w.table("buffer_choice", ch, ids=("B12.2",))

    b_rows = series["B on B's test rows"].copy()
    states = pd.read_csv(w.read(E5 / "stages/s02_data/common/outputs/records.csv.gz"), usecols=["order_id", "customer_state"])
    b_rows = b_rows.merge(states, on="order_id", how="left")
    st = []
    for s, g in b_rows.groupby("customer_state"):
        e = (g.y_true - g.y_pred).to_numpy()
        st.append({"customer_state": s, "test_orders": len(g), "judged": len(g) >= MIN_SLICE,
                   **{f"share_late_at_{r.buffer_days_chosen_on_validation}d": _late(e, r.buffer_days_chosen_on_validation)
                      for r in ch.itertuples() if r.buffer_days_chosen_on_validation is not None}})
    w.table("buffer_by_state", pd.DataFrame(st), ids=("B12.2",))
    w.check("every B test row has a customer state in B's seven states", bool(b_rows.customer_state.isin(b02.STATES).all()), ("B12.2",))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(9, 4.4))
    for (k, g), col in zip(curve.groupby("series", sort=False), ("#9ecae1", "#1f77b4", "#7f7f7f", "#bdbdbd")):
        ax.plot(g.buffer_days, g.share_late, marker="o", ms=3, lw=1.4, color=col, label=k)
    for j, r in enumerate(ch.itertuples()):
        if r.buffer_days_chosen_on_validation is not None:
            ax.axvline(r.buffer_days_chosen_on_validation, color="#d62728", ls=":", lw=0.9)
            ax.text(r.buffer_days_chosen_on_validation, 0.97 - 0.08 * j, f" {r.on_time_target:.0%} on time (validation)", transform=ax.get_xaxis_transform(), fontsize=8, va="top")
    ax.set(xlabel="buffer added to the predicted lead time (days)", ylabel="share of orders delivered later than prediction + buffer",
           title="Promise buffer: late share by buffer (buffer chosen on validation, read on test)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    w.figure("buffer_curve", fig, curve, ids=("B12.2",), title="Promise-buffer curve")
    plt.close(fig)
    txt = "; ".join(f"{r.on_time_target:.0%} on time on validation needs {r.buffer_days_chosen_on_validation} days, which leaves "
                    f"{r.test_share_late_B:.1%} of B's test orders late (A on the same orders {r.test_share_late_A_on_B_rows:.1%})"
                    for r in ch.itertuples() if r.buffer_days_chosen_on_validation is not None)
    w.explain("B12.2", done=(f"Late share against a buffer of 0 to 30 days for B and A (validation out-of-fold and T1 test). {txt}. "
                             "Validation residuals lean late and the test period is faster (drift, B9.4), so a buffer chosen on validation "
                             "is conservative on the test."))


def run(task: str) -> None:
    assert_a_frozen()
    w = BWriter(STAGE, task)
    seed = int(protocol.load()["seed"])
    _ranking_stability(w, task, seed)
    if task == "regression":
        _buffers(w)
    w.finish(seed=seed)
    if w.index["checks_failed"]:
        raise SystemExit(f"B12 {task}: checks failed: {w.index['checks_failed']}")
    rs = json.loads((b_outputs_dir(STAGE, task) / "ranking_stability.json").read_text(encoding="utf-8"))
    print(f"B12 {task}: Jaccard {rs['jaccard_min']:.2f}-{rs['jaccard_mean']:.2f} mean; {rs['B4_features_selected_in_every_fold']} of {rs['selected_by_B4']} in every fold")
