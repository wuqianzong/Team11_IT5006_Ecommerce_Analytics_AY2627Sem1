"""Business context for the report's problem statement (Henry, delegated lead, 2026-10-30).

Monthly revenue and customer repeat rate from the dashboard's Business overview data, computed with the
dashboard's own code (dashboard_core.data.load_business_complete_months and
business_tab.calculate_kpi_matrix), so the report and the app's Business overview tab agree. Descriptive data,
outside Pipelines A and B: nothing here reads a model, a stage output or a test-period order.

Window: March 2017 (the dashboard's first month) to April 2018, the last complete month before the test period
starts on 26 May 2018. Order counts are not written: this data uses the dashboard's cleaning, so its counts would
not match the report's development orders.

    deliverables/dashboard/app/.venv/Scripts/python.exe deliverables/business_context/make_business_context.py

Writes outputs/ (monthly_kpis.csv, summary.json, figures/revenue_repeat_by_month.png and .csv) with
_manifest.json (run id, commit, input and code sha256, output sha256) and _evidence_index.json. The register reads
these files as BIZ/<file> (build_evidence_B.verify_biz_source).
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
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
APP = HERE.parent / "dashboard" / "app"
REPO = HERE.parents[4]
sys.path.insert(0, str(APP))
from dashboard_core import paths  # noqa: E402
from dashboard_core.business_tab import calculate_kpi_matrix  # noqa: E402
from dashboard_core.data import load_business_complete_months  # noqa: E402

FIRST, LAST = "2017-03", "2018-04"
OUT = HERE / "outputs"
BLUE = "#2563eb"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _rel(p: Path) -> str:
    return p.resolve().relative_to(REPO).as_posix()


def main() -> None:
    frame = load_business_complete_months()
    frame = frame[(frame["year_month"] >= FIRST) & (frame["year_month"] <= LAST)]
    kpi = calculate_kpi_matrix(frame, "year_month").T
    monthly = pd.DataFrame({
        "month": kpi.index.astype(str),
        "revenue_brl": kpi["Total Revenue (R$)"].astype(float).values,
        "repeat_rate": kpi["Customer Repeat Rate"].astype(float).values,
    })
    assert monthly["month"].tolist()[0] == FIRST and monthly["month"].tolist()[-1] == LAST, monthly["month"].tolist()

    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    monthly.to_csv(OUT / "monthly_kpis.csv", index=False, lineterminator="\n")
    monthly.to_csv(OUT / "figures" / "revenue_repeat_by_month.csv", index=False, lineterminator="\n")

    peak = monthly.loc[monthly["revenue_brl"].idxmax()]
    by_month = monthly.set_index("month")
    summary = {
        "window": {"first_month": FIRST, "last_month": LAST, "months": int(len(monthly))},
        "revenue": {
            "first_month_brl": float(by_month.loc[FIRST, "revenue_brl"]),
            "last_month_brl": float(by_month.loc[LAST, "revenue_brl"]),
            "growth_ratio": float(by_month.loc[LAST, "revenue_brl"] / by_month.loc[FIRST, "revenue_brl"]),
            "peak_month": str(peak["month"]),
            "peak_brl": float(peak["revenue_brl"]),
            "oct_2017_brl": float(by_month.loc["2017-10", "revenue_brl"]),
            "window_total_brl": float(monthly["revenue_brl"].sum()),
        },
        "repeat_rate": {
            "mean": float(monthly["repeat_rate"].mean()),
            "min": float(monthly["repeat_rate"].min()),
            "max": float(monthly["repeat_rate"].max()),
        },
        "definitions": {
            "revenue_brl": "sum of item prices (freight excluded) of the month's orders, as the dashboard's KPI matrix",
            "repeat_rate": "share of the month's customers (customer_unique_id) with more than one order in that month",
        },
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8", newline="\n")

    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.8), dpi=200)
    x = range(len(monthly))
    labels = [pd.Period(m).strftime("%b %y") for m in monthly["month"]]
    ax1.bar(x, monthly["revenue_brl"] / 1e6, color=BLUE, width=0.7)
    ax1.set_title("Monthly revenue (R$ million, item prices)", loc="left", fontsize=12)
    ax2.plot(x, monthly["repeat_rate"] * 100, color=BLUE, linewidth=2, marker="o", markersize=5)
    ax2.set_title("Repeat rate (% of customers, 2+ orders in the month)", loc="left", fontsize=12)
    ax2.set_ylim(0, max(monthly["repeat_rate"] * 100) * 1.25)
    for ax in (ax1, ax2):
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, rotation=60, ha="right", fontsize=10)
        ax.grid(axis="y", color="#e5e7eb", linewidth=0.8)
        ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(OUT / "figures" / "revenue_repeat_by_month.png")
    plt.close(fig)

    index = {"node": "BIZ/business_context", "files": {
        "monthly_kpis.csv": {"ids": ["BIZ.1"], "kind": "table"},
        "summary.json": {"ids": ["BIZ.1"], "kind": "json"},
        "figures/revenue_repeat_by_month.png": {"ids": ["BIZ.1"], "kind": "figure"},
        "figures/revenue_repeat_by_month.csv": {"ids": ["BIZ.1"], "kind": "figure_data"},
    }}
    (OUT / "_evidence_index.json").write_text(json.dumps(index, indent=2), encoding="utf-8", newline="\n")
    git = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True).stdout.strip()  # noqa: E731
    code = [Path(__file__), APP / "dashboard_core" / "data.py", APP / "dashboard_core" / "business_tab.py"]
    outputs = [p for p in sorted(OUT.rglob("*")) if p.is_file() and not p.name.startswith("_manifest")]
    manifest = {
        "node": "BIZ/business_context",
        "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "commit": git("rev-parse", "HEAD"),
        "dirty": bool(git("status", "--porcelain", "--", *[_rel(p) for p in code])),
        "window": {"first_month": FIRST, "last_month": LAST},
        "inputs": {_rel(paths.BUSINESS_DATA_PATH): _sha(paths.BUSINESS_DATA_PATH)},
        "code": {_rel(p): _sha(p) for p in code},
        "outputs": {_rel(p): _sha(p) for p in outputs},
    }
    (OUT / "_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
