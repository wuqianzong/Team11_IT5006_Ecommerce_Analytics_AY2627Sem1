"""Half-width report renders of four section 7.4 charts (B-CR-52).

The report places Figures 20-23 (permutation importance and B's coefficients, lead time and alert) as two
side-by-side pairs, so each chart prints about 3.3 in wide. Each render redraws one register chart from the data file
saved beside its stored PNG, at that print size with 9 pt text (8 pt feature names), in the stored order. No stage is rerun, no model is
fitted and no number is computed that the stored data file does not hold; the original PNGs and the deck are
unchanged. Long feature names wrap at underscores; one-hot terms are written "route RS->SP" and "category music"
(the stored names are route_seller_to_customer_state_RS->SP and primary_category_music).

    .venv/Scripts/python.exe pipeline_b/deliverables/report/renders/make_report_renders.py   (from experiments/experiment_5)

Writes outputs/<register id>.report.png with outputs/_manifest.json (run id, commit, input/code/output sha256) and
outputs/_evidence_index.json (each render carries its original's evidence ID). The register reads them as
REPORT/<file> (build_evidence_B.verify_manifest_source).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
B_ROOT = HERE.parents[2]
REPO = B_ROOT.parents[2]
OUT = HERE / "outputs"
B09 = B_ROOT / "stages" / "b09"
BLUE, GREEN, RED = "#1f77b4", "#2ca02c", "#d62728"   # the stored charts' colours
FONT = 9
W_IN, H_IN = 3.3, 4.3
INPUTS: list[Path] = []

plt.rcParams.update({"font.size": FONT, "axes.titlesize": FONT + 0.5, "axes.labelsize": FONT, "xtick.labelsize": FONT,
                     "ytick.labelsize": FONT - 1, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.titlelocation": "left"})


def _read(p: Path) -> pd.DataFrame:
    INPUTS.append(p)
    return pd.read_csv(p)


def _wrap(name: str, width: int = 26) -> str:
    """Break a feature name at underscores into lines of at most `width` characters (names are kept whole)."""
    lines, cur = [], ""
    for part in name.split("_"):
        piece = part if not cur else f"{cur}_{part}"
        if cur and len(piece) > width:
            lines.append(cur + "_")
            cur = part
        else:
            cur = piece
    return "\n".join(lines + [cur])


def _term(t: str) -> str:
    t = t.replace("route_seller_to_customer_state_", "route ").replace("primary_category_", "category ")
    return _wrap(t)


def _labels(fig, ax, title: str, xlabel: str) -> None:
    fig.suptitle(title, x=0.02, ha="left", fontsize=FONT + 0.5)
    ax.set_xlabel(xlabel, loc="right")
    ax.tick_params(axis="y", length=0)
    for t in ax.get_yticklabels():
        t.set_linespacing(0.95)


def _save(fig, name: str) -> None:
    fig.savefig(OUT / f"{name}.report.png", dpi=300)
    plt.close(fig)


def importance(task: str, name: str, title: str, xlabel: str) -> None:
    d = _read(B09 / task / "outputs/figures/permutation_importance.csv")
    fig, ax = plt.subplots(figsize=(W_IN, H_IN))
    ax.barh([_wrap(f) for f in d.feature], d.importance_mean, xerr=d.importance_sd, color=BLUE, height=0.7,
            error_kw={"linewidth": 1})
    ax.axvline(0, color="#111827", linewidth=0.6)
    _labels(fig, ax, title, xlabel)
    ax.margins(y=0.01)
    fig.tight_layout(pad=0.6)
    _save(fig, name)


def coefficients(task: str, name: str, title: str) -> None:
    d = _read(B09 / task / "outputs/figures/coefficients.csv")
    ratio = d["ratio_per_unit"] if "ratio_per_unit" in d else d["odds_ratio"]
    fig, ax = plt.subplots(figsize=(W_IN, H_IN))
    ax.barh([_term(t) for t in d.term], ratio - 1, left=1, color=[GREEN if r < 1 else RED for r in ratio], height=0.7)
    ax.axvline(1, color="#111827", linewidth=0.8)
    _labels(fig, ax, title, "lead-time ratio per +1 unit" if task == "regression" else "odds ratio per +1 unit")
    ax.margins(y=0.01)
    fig.tight_layout(pad=0.6)
    _save(fig, name)


RENDERS = {
    "F.reg.importance": lambda n: importance("regression", n, "Lead time, B's test rows", "MAE lost (days) when shuffled"),
    "F.clf.importance": lambda n: importance("classification", n, "Detractor alert, B's test rows",
                                             "AP lost when shuffled"),
    "F.reg.coefficients": lambda n: coefficients("regression", n, "Lead time: 15 largest terms"),
    "F.clf.coefficients": lambda n: coefficients("classification", n, "Detractor alert: 15 largest terms"),
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    numbers = json.loads((B_ROOT / "evidence/build/numbers_B.json").read_text(encoding="utf-8"))
    files = {}
    for rid, fn in RENDERS.items():
        fn(rid)
        files[f"{rid}.report.png"] = {"ids": [numbers[rid]["evidence"]], "kind": "figure"}
    (OUT / "_evidence_index.json").write_text(json.dumps({"node": "REPORT/report_renders", "files": files}, indent=2),
                                              encoding="utf-8", newline="\n")
    git = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True).stdout.strip()  # noqa: E731
    rel = lambda p: p.resolve().relative_to(REPO).as_posix()  # noqa: E731
    def sha(p: Path) -> str:   # text files with CRLF normalised to LF, as build_evidence_B._sha (B-G-15, B-CR-46)
        data = p.read_bytes()
        if p.suffix.lower() in {".csv", ".json", ".md", ".txt", ".py"}:
            data = data.replace(b"\r\n", b"\n")
        return hashlib.sha256(data).hexdigest()
    outputs = [p for p in sorted(OUT.iterdir()) if p.is_file() and p.name != "_manifest.json"]
    manifest = {"node": "REPORT/report_renders", "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
                "commit": git("rev-parse", "HEAD"), "dirty": bool(git("status", "--porcelain", "--", rel(Path(__file__)))),
                "inputs": {rel(p): sha(p) for p in sorted(set(INPUTS))}, "code": {rel(Path(__file__)): sha(Path(__file__))},
                "outputs": {rel(p): sha(p) for p in outputs}}
    (OUT / "_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8", newline="\n")
    print(len(files), "renders")


if __name__ == "__main__":
    main()
