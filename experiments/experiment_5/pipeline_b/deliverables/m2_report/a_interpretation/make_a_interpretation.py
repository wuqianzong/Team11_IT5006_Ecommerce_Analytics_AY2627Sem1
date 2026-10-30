"""Pipeline A's interpretation on A's own test rows, for the Milestone 2 report (decision M2-D3, B-CR-42).

Read-only: loads A's frozen T1 bundles and A's test rows, checks that the bundles re-predict T1's stored
predictions, then computes the coefficients (odds ratios for the alert) and the permutation importance with
the method, scoring, repeats and seed of B9.5. No model is fitted, no threshold or model is chosen, and T1 is
not rerun; the test labels are read only as B9.5 reads them, to score the shuffled copies.

    experiments/experiment_5/.venv/Scripts/python.exe
        experiments/experiment_5/pipeline_b/deliverables/m2_report/a_interpretation/make_a_interpretation.py

Writes outputs/<task>/ (coefficients.csv, permutation_importance.csv, figures/*.png and .csv) with
outputs/_manifest.json (run id, commit, input/code/output sha256) and outputs/_evidence_index.json. The register
reads them as M2A/<task>/<file> (build_evidence_B.verify_manifest_source).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
B_ROOT = HERE.parents[2]
E5 = B_ROOT.parent
REPO = E5.parents[1]
sys.path[:0] = [str(E5), str(B_ROOT)]
from e5lib import factory, protocol  # noqa: E402
from e5lib.training import TARGET, predict  # noqa: E402

OUT = HERE / "outputs"
A_RECORDS = E5 / "stages/s02_data/common/outputs/records.csv.gz"
BLUE = "#2563eb"
TOP = 15


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _rel(p: Path) -> str:
    return p.resolve().relative_to(REPO).as_posix()


def _feature_names(pipe) -> list[str]:
    # A's pipelines open with RouteMedianImputer, which fills a column in place and has no name map; skip it
    start = 1 if pipe.steps[0][0] == "route_median" else 0
    return list(pipe[start:-1].get_feature_names_out())


def _bar(df: pd.DataFrame, col: str, label: str, title: str, path: Path) -> None:
    top = df.head(TOP).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 5.2), dpi=200)
    ax.barh(top.iloc[:, 0].astype(str), top[col], color=BLUE, height=0.65)
    if col in ("odds_ratio", "ratio_per_unit"):
        ax.axvline(1.0, color="#6b7280", linewidth=1)
    ax.set_xlabel(label)
    ax.set_title(title, loc="left", fontsize=12)
    ax.grid(axis="x", color="#e5e7eb", linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", labelsize=9)
    fig.tight_layout()
    fig.savefig(path.with_suffix(".png"))
    plt.close(fig)
    top.iloc[::-1].to_csv(path.with_suffix(".csv"), index=False, lineterminator="\n")


def run(task: str, inputs: list[Path]) -> None:
    seed = int(protocol.load()["seed"])
    t1 = B_ROOT / "stages/t1_joint_test" / task / "outputs"
    s08 = E5 / "stages/s08_selection" / task / "outputs"
    s05 = E5 / "stages/s05_partition" / task / "outputs"
    inputs += [t1 / "bundles/A/model.joblib", t1 / "predictions_test.csv.gz", s08 / "selected_spec.json",
               s05 / "test_manifest.csv", A_RECORDS]
    model = joblib.load(t1 / "bundles/A/model.joblib")
    spec = json.loads((s08 / "selected_spec.json").read_text())["spec"]
    a = pd.read_csv(A_RECORDS, parse_dates=["purchase_ts", "review_label_ts", "lead_label_ts"], low_memory=False)
    man = pd.read_csv(s05 / "test_manifest.csv")
    a_test = a[a[f"eligible_{task}"].astype(bool) & a.order_id.isin(man.order_id)].reset_index(drop=True)

    pt = pd.read_csv(t1 / "predictions_test.csv.gz")
    stored = pt[(pt.model == "A frozen") & (pt.rows == "A test rows")].set_index("order_id").loc[a_test.order_id, "y_pred"]
    diff = float(np.max(np.abs(predict(task, model, a_test) - stored.to_numpy())))
    assert diff <= 1e-9, f"{task}: A's bundle does not re-predict T1 (max difference {diff})"

    out = OUT / task
    (out / "figures").mkdir(parents=True, exist_ok=True)
    if task == "regression":
        pipe = model.regressor_
        coef = pd.DataFrame({"term": _feature_names(pipe), "coefficient": pipe.named_steps["model"].coef_})
        coef["ratio_per_unit"] = np.exp(coef.coefficient)
        coef["reading"] = "multiplies predicted lead time by ratio_per_unit per +1 unit of the transformed term (log1p target)"
    else:
        parts = []
        for i, cc in enumerate(model.calibrated_classifiers_):
            est = cc.estimator
            parts.append(pd.DataFrame({"term": _feature_names(est), "coefficient": est.named_steps["model"].coef_.ravel(), "split": i}))
        allc = pd.concat(parts)
        coef = allc.groupby("term", sort=False).coefficient.agg(["mean", "min", "max"]).reset_index().rename(
            columns={"mean": "coefficient", "min": "coefficient_min", "max": "coefficient_max"})
        coef["odds_ratio"] = np.exp(coef.coefficient)
        coef["reading"] = f"odds ratio per +1 unit of the transformed term; mean over the {len(parts)} calibration splits (min/max shown)"
    coef = coef.reindex(coef.coefficient.abs().sort_values(ascending=False).index).reset_index(drop=True)
    coef.to_csv(out / "coefficients.csv", index=False, lineterminator="\n")

    from sklearn.inspection import permutation_importance
    cols = factory.feature_columns(spec)
    y = a_test[TARGET[task]].astype(float if task == "regression" else int).to_numpy()
    scoring = "neg_mean_absolute_error" if task == "regression" else "average_precision"
    pi = permutation_importance(model, a_test[cols], y, scoring=scoring, n_repeats=5, random_state=seed, n_jobs=1)
    perm = pd.DataFrame({"feature": cols, "importance_mean": pi.importances_mean, "importance_sd": pi.importances_std})
    perm = perm.sort_values("importance_mean", ascending=False).reset_index(drop=True)
    perm["rank"] = np.arange(1, len(perm) + 1)
    perm["scoring"] = f"drop in {'MAE (days, as negative MAE)' if task == 'regression' else 'AP'} when the column is shuffled, A's test rows"
    perm.to_csv(out / "permutation_importance.csv", index=False, lineterminator="\n")

    name = "lead time" if task == "regression" else "detractor alert"
    _bar(perm[["feature", "importance_mean"]], "importance_mean",
         "Drop in score when shuffled (MAE in days)" if task == "regression" else "Drop in average precision when shuffled",
         f"Permutation importance, {name}, A's test rows (top {TOP})", out / "figures" / "permutation_importance")
    ratio = "ratio_per_unit" if task == "regression" else "odds_ratio"
    _bar(coef[["term", ratio]], ratio, "Ratio per unit (predicted lead time)" if task == "regression" else "Odds ratio per unit",
         f"{'Coefficients' if task == 'regression' else 'Odds ratios'}, {name} (largest {TOP} by size)", out / "figures" / "coefficients")
    summary = {"rows": int(len(a_test)), "reprediction_max_difference": diff, "seed": seed, "n_repeats": 5,
               "top_feature": str(perm.feature.iloc[0]), "features": len(cols), "terms": int(len(coef))}
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8", newline="\n")
    print(task, summary)


def main() -> None:
    inputs: list[Path] = []
    for task in ("regression", "classification"):
        run(task, inputs)
    files = {}
    for task in ("regression", "classification"):
        for f in ("coefficients.csv", "permutation_importance.csv", "summary.json"):
            files[f"{task}/{f}"] = {"ids": ["M2A.1"], "kind": "json" if f.endswith(".json") else "table"}
        for f in ("permutation_importance", "coefficients"):
            files[f"{task}/figures/{f}.png"] = {"ids": ["M2A.1"], "kind": "figure"}
            files[f"{task}/figures/{f}.csv"] = {"ids": ["M2A.1"], "kind": "figure_data"}
    (OUT / "_evidence_index.json").write_text(json.dumps({"node": "M2A/a_interpretation", "files": files}, indent=2),
                                              encoding="utf-8", newline="\n")
    git = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True).stdout.strip()  # noqa: E731
    code = [Path(__file__)]
    outputs = [p for p in sorted(OUT.rglob("*")) if p.is_file() and p.name != "_manifest.json"]
    manifest = {
        "node": "M2A/a_interpretation",
        "run_id": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "commit": git("rev-parse", "HEAD"),
        "dirty": bool(git("status", "--porcelain", "--", *[_rel(p) for p in code])),
        "inputs": {_rel(p): _sha(p) for p in sorted(set(inputs))},
        "code": {_rel(p): _sha(p) for p in code},
        "outputs": {_rel(p): _sha(p) for p in outputs},
    }
    (OUT / "_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
