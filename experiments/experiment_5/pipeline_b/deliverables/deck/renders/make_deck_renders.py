"""Presentation renders of the deck's charts (decision D3, B-CR-43).

Each render redraws one register chart from the data file saved beside its stored PNG, sized to its slide box with
text of at least 18 pt at that size, so it can be read in presentation mode. No stage is rerun, no model is fitted
and no number is computed that the stored data file does not hold; the original PNGs and the report are unchanged.

    python experiments/experiment_5/pipeline_b/deliverables/deck/renders/make_deck_renders.py

Writes outputs/<register id>.deck.png with outputs/_manifest.json (run id, commit, input/code/output sha256) and
outputs/_evidence_index.json (each render carries its original's evidence ID). The register reads them as
DECK/<file> (build_evidence_B.verify_manifest_source).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
B_ROOT = HERE.parents[2]
E5 = B_ROOT.parent
REPO = E5.parents[1]
OUT = HERE / "outputs"
A_OUT = E5 / "stages"
B_OUT = B_ROOT / "stages"
BLUE, GREY, LIGHT, RED, ORANGE = "#2563eb", "#6b7280", "#9ec5fe", "#dc2626", "#ea580c"
FONT = 18
INPUTS: list[Path] = []

plt.rcParams.update({"font.size": FONT, "axes.titlesize": FONT, "axes.labelsize": FONT, "xtick.labelsize": FONT,
                     "ytick.labelsize": FONT, "legend.fontsize": FONT - 2, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.titlelocation": "left"})


def _read(p: Path) -> pd.DataFrame:
    INPUTS.append(p)
    return pd.read_csv(p)


def _json(p: Path) -> dict:
    INPUTS.append(p)
    return json.loads(p.read_text(encoding="utf-8"))


def _fig(w_px: int, h_px: int, ncols: int = 1, **kw):
    return plt.subplots(1, ncols, figsize=(w_px / 100, h_px / 100), **kw)


def _save(fig, name: str) -> None:
    fig.savefig(OUT / f"{name}.deck.png", dpi=200)
    plt.close(fig)


def _grid(ax, axis="y"):
    ax.grid(axis=axis, color="#e5e7eb", linewidth=0.8)
    ax.set_axisbelow(True)


def cumulative(task: str, name: str) -> None:
    d = _read(A_OUT / f"s03_eda/{task}/outputs/figures/cumulative_importance.csv").sort_values("rank")
    cuts = _json(A_OUT / f"s03_eda/{task}/outputs/eda_summary.json")["cut_points"]
    fig, ax = _fig(836, 470)
    ax.bar(d["rank"], d["share"], color="#d1d5db", width=0.75, label="share of total")
    ax.plot(d["rank"], d["cumulative_share"], color=BLUE, linewidth=2.5, marker="o", markersize=6, label="cumulative share")
    for q, c, col in (("0.95", cuts["0.95"], "#16a34a"), ("0.99", cuts["0.99"], ORANGE)):
        ax.axvline(c + 0.5, color=col, linestyle="--", linewidth=1.5)
        ax.text(c + 0.3, 0.62 if q == "0.95" else 0.48, f"{int(float(q) * 100)}%: top {c}", color=col, rotation=90, va="bottom")
    top = ", ".join(d["feature"].head(3))
    ax.text(0.3, 0.47, f"Top 3: {top}", transform=ax.transAxes, va="top", fontsize=FONT - 3, wrap=True)
    ax.set_xlabel("feature rank (of 24)")
    ax.set_ylabel("share")
    ax.set_xticks([1, 5, 10, 15, 20, 24])
    ax.set_ylim(0, 1.08)
    ax.legend(loc="lower right", frameon=False)
    _grid(ax)
    fig.tight_layout()
    _save(fig, name)


def heatmap(name: str) -> None:
    d = _read(A_OUT / "s03_eda/regression/outputs/figures/numeric_correlation_heatmap.csv")
    d = d[d.feature_a < d.feature_b].assign(strength=lambda x: x.spearman.abs())
    s = d[d.strength >= 0.5].sort_values("strength")
    fig, ax = _fig(820, 700)
    ax.barh([f"{a}\n– {b}" for a, b in zip(s.feature_a, s.feature_b)], s.strength,
            color=[RED if v > 0 else BLUE for v in s.spearman], height=0.7)
    for i, v in enumerate(s.spearman):
        ax.text(abs(v) + 0.01, i, f"{v:+.2f}", va="center", fontsize=FONT - 2)
    ax.axvline(0.9, color="#111827", linestyle="--", linewidth=1.5)
    ax.text(0.905, len(s) - 0.4, "flag at 0.9", fontsize=FONT - 2)
    ax.set_xlim(0.4, 1.12)
    ax.set_xlabel("|Spearman ρ|  (red +, blue −)")
    ax.set_title(f"{len(s)} pairs with |ρ| ≥ 0.5")
    ax.tick_params(axis="y", labelsize=FONT - 3)
    _grid(ax, "x")
    fig.tight_layout()
    _save(fig, name)


def screen_promise(name: str) -> None:
    d = _read(A_OUT / "s03_eda/classification/outputs/figures/candidate_screen_promise.csv")
    fig, ax = _fig(560, 260)
    ax.plot(d["x"], d["class_0"], color=GREY, linewidth=2.5, label="normal")
    ax.plot(d["x"], d["class_1"], color=RED, linewidth=2.5, label="detractor")
    ax.set_xlabel("promised delivery days, log(1 + x)")
    ax.set_yticks([])
    ax.legend(frameon=False, loc="upper right")
    fig.tight_layout()
    _save(fig, name)


def lateness_by_route(name: str) -> None:
    d = _read(B_OUT / "doc_support/regression/outputs/figures/b2_lateness_by_route.csv")
    fig, (a1, a2) = _fig(1112, 260, ncols=2)
    x = np.arange(len(d))
    a1.bar(x, d["late_handover_rate"] * 100, color=BLUE, width=0.7)
    a1.set_title("late handover, % of handovers")
    a2.bar(x, d["median_delivery_days"], color=GREY, width=0.7)
    a2.set_title("median delivery days")
    for a in (a1, a2):
        a.set_xticks(x)
        a.set_xticklabels(d["route"], rotation=90, fontsize=FONT - 2)
        _grid(a)
    fig.tight_layout(w_pad=2)
    _save(fig, name)


REGION = {"North": "N", "Northeast": "NE", "Center-West": "CW", "Southeast": "SE", "South": "S"}


def screen_region(name: str) -> None:
    d = _read(A_OUT / "s03_eda/classification/outputs/figures/candidate_screen_region.csv")
    cr = d[d.feature == "customer_region"]
    overall = cr.detractors.sum() / cr.n.sum() * 100
    fig, axs = plt.subplots(1, 3, figsize=(11.12, 2.5), gridspec_kw={"width_ratios": [5, 5, 15]})
    for ax, (feat, title) in zip(axs, (("customer_region", "customer"), ("seller_region", "seller"),
                                         ("region_pair", "region pair (15 largest)"))):
        s = d[d.feature == feat]
        if feat == "region_pair":
            s = s.sort_values("n", ascending=False).head(15)
            labels = [">".join(REGION[p] for p in lv.split(">")) for lv in s.level]
        else:
            labels = [REGION[lv] for lv in s.level]
        ax.bar(range(len(s)), s.detractor_rate * 100, color="#e06666", width=0.7)
        ax.axhline(overall, color="#111827", linestyle="--", linewidth=1.2)
        ax.set_xticks(range(len(s)))
        ax.set_xticklabels(labels, rotation=90 if feat == "region_pair" else 0, fontsize=FONT - 2)
        ax.set_title(title)
        _grid(ax)
    axs[0].set_ylabel("detractors %")
    fig.tight_layout(w_pad=1)
    _save(fig, name)


def selection(task: str, name: str) -> None:
    d = _read(B_OUT / f"doc_support/{task}/outputs/figures/b4_selection.csv").sort_values("rank")
    kept, total = int(d.selected.astype(bool).sum()), len(d)
    t = d.head(8).iloc[::-1]
    fig, ax = _fig(836, 330)
    colors = [BLUE if str(s).startswith("B-") else "#c4c9d1" for s in t.source]
    ax.barh(t.feature, t.share * 100, color=colors, height=0.7)
    ax.set_xlabel("share of total ranking score, %")
    ax.tick_params(axis="y", labelsize=FONT - 2)
    ax.set_title(f"top 8 of {total}; {kept} kept (99% rule)", fontsize=FONT - 2)
    _grid(ax, "x")
    fig.tight_layout()
    _save(fig, name)


def population(name: str) -> None:
    d = _read(B_OUT / "doc_support/regression/outputs/figures/r05_population.csv")
    labels = ["A model,\nA rows", "A model,\nB rows", "B model,\nB rows"]
    x = np.arange(len(d))
    fig, ax = _fig(836, 480)
    ax.bar(x - 0.2, d.mean_5_folds, 0.4, yerr=d.se_5_folds, capsize=6, color=BLUE, label="5 folds (decision)")
    ax.bar(x + 0.2, d.mean_folds_2_5, 0.4, yerr=d.se_folds_2_5, capsize=6, color=LIGHT, label="folds 2–5 (description)")
    for i, v in enumerate(d.mean_5_folds):
        ax.text(i - 0.2, v / 2, f"{v:.2f}", ha="center", color="white", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("validation MAE, days")
    ax.legend(frameon=False, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.38))
    _grid(ax)
    fig.tight_layout()
    _save(fig, name)


def confusion(name: str) -> None:
    d = _read(B_OUT / "doc_support/classification/outputs/figures/r06_confusion.csv")
    fig, axs = _fig(836, 480, ncols=2)
    for ax, (_, r), title in zip(axs, d.iterrows(), ("Pipeline A, 1/6", "Pipeline B, 1/6")):
        m = np.array([[r.tn, r.fp], [r.fn, r.tp]], dtype=float)
        ax.imshow(m, cmap="Blues", vmin=0, vmax=m.max() * 1.1)
        for i in range(2):
            for j in range(2):
                ax.text(j, i, f"{int(m[i, j]):,}", ha="center", va="center", fontsize=FONT + 2,
                        color="white" if m[i, j] > m.max() * 0.5 else "#111827", fontweight="bold")
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["no alert", "alert"])
        ax.set_yticks([0, 1])
        ax.set_yticklabels(["normal", "detractor"] if ax is axs[0] else ["", ""])
        ax.set_title(title)
        ax.set_xlabel("predicted")
        for sp in ax.spines.values():
            sp.set_visible(False)
    axs[0].set_ylabel("actual")
    fig.tight_layout()
    _save(fig, name)


def residuals(name: str) -> None:
    d = _read(B_OUT / "b09/regression/outputs/figures/residuals.csv")
    fig, ax = _fig(872, 350)
    for series, col, lab in (("B on B's test rows", BLUE, "Pipeline B"), ("A on B's test rows", GREY, "Pipeline A")):
        s = d[d.series == series]
        share = s.orders / s.orders.sum() * 100
        ax.step(s.bin_from_days, share, where="post", color=col, linewidth=2.5, label=lab)
    for x, lab in ((3, "3 days late"), (6, "6 days late")):
        ax.axvline(x, color=RED, linestyle="--", linewidth=1.3)
        ax.text(x + 0.3, ax.get_ylim()[1] * 0.35, lab, color=RED, fontsize=FONT - 3, rotation=90, va="bottom")
    ax.set_xlabel("actual − predicted lead time, days (positive = late)")
    ax.set_ylabel("% of orders")
    ax.set_xlim(-20, 20)
    ax.legend(frameon=False, loc="upper left")
    _grid(ax)
    fig.tight_layout()
    _save(fig, name)


def by_state(name: str) -> None:
    d = _read(B_OUT / "b09/regression/outputs/figures/by_customer_state.csv")
    x = np.arange(len(d))
    fig, ax = _fig(872, 350)
    ax.bar(x - 0.2, d.mae_A, 0.4, color=GREY, label="Pipeline A")
    ax.bar(x + 0.2, d.mae_B, 0.4, color=BLUE, label="Pipeline B")
    ax.set_xticks(x)
    ax.set_xticklabels([f"{v}\n{n:,}" for v, n in zip(d.value, d.orders)], fontsize=FONT - 2)
    ax.set_ylabel("test MAE (days)")
    ax.legend(frameon=False, ncol=2, loc="upper left")
    _grid(ax)
    fig.tight_layout()
    _save(fig, name)


def buffer_curve(name: str) -> None:
    d = _read(B_OUT / "b12/regression/outputs/figures/buffer_curve.csv")
    ch = _read(B_OUT / "b12/regression/outputs/buffer_choice.csv")
    fig, ax = _fig(700, 300)
    for series, col, ls, lab in (("B on B's validation rows (out-of-fold)", LIGHT, "-", "B, validation"),
                                 ("B on B's test rows", BLUE, "-", "B, test"),
                                 ("A on B's test rows", GREY, "--", "A, test")):
        s = d[d.series == series]
        ax.plot(s.buffer_days, s.share_late * 100, color=col, linestyle=ls, linewidth=2.5, label=lab)
    for _, r in ch.iterrows():
        ax.axvline(r.buffer_days_chosen_on_validation, color=RED, linestyle=":", linewidth=1.5)
        ax.text(r.buffer_days_chosen_on_validation - 1.4, 18, f"{int(r.on_time_target * 100)}% on time",
                color=RED, fontsize=FONT - 3, rotation=90, va="bottom")
    ax.set_xlabel("buffer added to the prediction (days)")
    ax.set_ylabel("% delivered late")
    ax.legend(frameon=False, loc="upper right")
    _grid(ax)
    fig.tight_layout()
    _save(fig, name)


def threshold_options(name: str) -> None:
    d = _read(B_OUT / "b09/classification/outputs/figures/threshold_options.csv")
    fig, (a1, a2) = _fig(972, 300, ncols=2)
    for period, ls in (("validation (out-of-fold)", "--"), ("test (post-test view)", "-")):
        s = d[d.period == period]
        a1.plot(s.threshold, s.precision, color=BLUE, linestyle=ls, linewidth=2.2)
        a1.plot(s.threshold, s.recall, color=ORANGE, linestyle=ls, linewidth=2.2)
        a2.plot(s.threshold, s.alerts_per_day, color=GREY, linestyle=ls, linewidth=2.2)
    a1.plot([], [], color=BLUE, label="precision")
    a1.plot([], [], color=ORANGE, label="recall")
    a2.plot([], [], color=GREY, linestyle="--", label="validation")
    a2.plot([], [], color=GREY, linestyle="-", label="test")
    a2.set_ylim(0, 60)
    a1.set_ylim(0, 1.35)
    for a in (a1, a2):
        for t, lab in ((1 / 6, "1/6"), (4 / 15, "4/15")):
            a.axvline(t, color="#111827", linestyle=":", linewidth=1.2)
            a.text(t + 0.005, a.get_ylim()[1] * 0.9, lab, fontsize=FONT - 3)
        a.set_xlabel("threshold")
        _grid(a)
    a1.set_title("precision and recall")
    a2.set_title("alerts per day")
    a1.legend(frameon=False, loc="upper right", bbox_to_anchor=(1.0, 1.02))
    a2.legend(frameon=False, loc="upper right")
    fig.tight_layout(w_pad=2)
    _save(fig, name)


RENDERS = {
    "F.A3.reg.cumulative_importance": (lambda n: cumulative("regression", n), "3.4"),
    "F.A3.clf.cumulative_importance": (lambda n: cumulative("classification", n), "3.6"),
    "F.A3.reg.correlation_heatmap": (heatmap, "3.8"),
    "F.A3.clf.screen_promise": (screen_promise, None),
    "F.reg.lateness_by_route": (lateness_by_route, None),
    "F.A3.clf.screen_region": (screen_region, None),
    "F.reg.selection": (lambda n: selection("regression", n), None),
    "F.clf.selection": (lambda n: selection("classification", n), None),
    "F.reg.population": (population, None),
    "F.clf.confusion": (confusion, None),
    "F.reg.residuals": (residuals, None),
    "F.reg.by_state": (by_state, None),
    "F.reg.buffer_curve": (buffer_curve, None),
    "F.clf.threshold_options": (threshold_options, None),
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    numbers = json.loads((B_ROOT / "evidence/build/numbers_B.json").read_text(encoding="utf-8"))
    files = {}
    for rid, (fn, _) in RENDERS.items():
        fn(rid)
        files[f"{rid}.deck.png"] = {"ids": [numbers[rid]["evidence"]], "kind": "figure"}
    (OUT / "_evidence_index.json").write_text(json.dumps({"node": "DECK/deck_renders", "files": files}, indent=2),
                                              encoding="utf-8", newline="\n")
    git = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True).stdout.strip()  # noqa: E731
    rel = lambda p: p.resolve().relative_to(REPO).as_posix()  # noqa: E731
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()  # noqa: E731
    outputs = [p for p in sorted(OUT.iterdir()) if p.is_file() and p.name != "_manifest.json"]
    manifest = {"node": "DECK/deck_renders", "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
                "commit": git("rev-parse", "HEAD"), "dirty": bool(git("status", "--porcelain", "--", rel(Path(__file__)))),
                "inputs": {rel(p): sha(p) for p in sorted(set(INPUTS))}, "code": {rel(Path(__file__)): sha(Path(__file__))},
                "outputs": {rel(p): sha(p) for p in outputs}}
    (OUT / "_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8", newline="\n")
    print(len(files), "renders")


if __name__ == "__main__":
    main()
