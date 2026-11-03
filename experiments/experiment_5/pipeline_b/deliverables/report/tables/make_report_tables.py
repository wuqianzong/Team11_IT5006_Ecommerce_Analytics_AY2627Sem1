"""Body tables for report v2.4: training, validation and test side by side with the generalisation gap (B-CR-61).

Read only: it reads B9's stored train_val_test.csv for both tasks and T1's final-fit row counts. Nothing is fitted
and no stage output is changed. The gap (validation minus training, five-fold means) is the one derived column;
every other value is copied from B9.

    .venv/Scripts/python.exe pipeline_b/deliverables/report/tables/make_report_tables.py   (from experiments/experiment_5/)

Outputs (evidence RT.1):
    train_gap.csv   RT.1  per task: final-fit rows, five-fold training and validation means, test score and the gap,
                          for Pipeline B's delivered model, its raw logistic model (alert) and the dummy
with _manifest.json (run id, commit, input and code sha256, output sha256) and _evidence_index.json. The register
reads these files as RTAB/<file> (build_evidence_B.verify_manifest_source).
"""
from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE / "outputs"
B_ROOT = HERE.parents[2]
REPO = HERE.parents[5]
STAGES = B_ROOT / "stages"
TVT = {t: STAGES / "b09" / t / "outputs" / "train_val_test.csv" for t in ("regression", "classification")}
FIT = {t: STAGES / "t1_joint_test" / t / "outputs" / "test_size_B.json" for t in ("regression", "classification")}

# (task, metric, model in train_val_test.csv, label in the report)
ROWS = [
    ("regression", "mae", "B frozen", "Pipeline B, plain linear (delivered)"),
    ("regression", "mae", "B dummy", "Dummy (median)"),
    ("classification", "ap", "B plain", "Pipeline B, plain logistic, raw probabilities"),
    ("classification", "ap", "B frozen", "Pipeline B, plain logistic, calibrated (delivered)"),
    ("classification", "ap", "B dummy", "Dummy (detractor share)"),
]


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _rel(p: Path) -> str:
    return p.resolve().relative_to(REPO).as_posix()


def main() -> None:
    rows = []
    for task, metric, model, label in ROWS:
        df = pd.read_csv(TVT[task])
        r = df[(df.model == model) & (df.rows == "B test rows") & (df.metric == metric)]
        assert len(r) == 1, (task, model, metric)
        r = r.iloc[0]
        fit_rows = json.loads(FIT[task].read_text(encoding="utf-8"))["b_final_fit_rows"]
        rows.append({"task": task, "row": label, "model": model, "metric": metric, "final_fit_rows": int(fit_rows),
                     "train_mean": r.train_mean, "validation_mean": r.validation_mean, "test": r.test,
                     "gap_validation_minus_train": r.validation_mean - r.train_mean})
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "train_gap.csv", index=False, lineterminator="\n")

    index = {"node": "RTAB/report_tables", "files": {"train_gap.csv": {"ids": ["RT.1"], "kind": "table"}}}
    (OUT / "_evidence_index.json").write_text(json.dumps(index, indent=2), encoding="utf-8", newline="\n")
    git = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True).stdout.strip()  # noqa: E731
    code = [Path(__file__)]
    inputs = list(TVT.values()) + list(FIT.values())
    outputs = [p for p in sorted(OUT.rglob("*")) if p.is_file() and not p.name.startswith("_manifest")]
    manifest = {
        "node": "RTAB/report_tables",
        "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "commit": git("rev-parse", "HEAD"),
        "dirty": bool(git("status", "--porcelain", "--", *[_rel(p) for p in code])),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "inputs": {_rel(p): _sha(p) for p in inputs},
        "code": {_rel(p): _sha(p) for p in code},
        "outputs": {_rel(p): _sha(p) for p in outputs},
    }
    (OUT / "_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8", newline="\n")
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
