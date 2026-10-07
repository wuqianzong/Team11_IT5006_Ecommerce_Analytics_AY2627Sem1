"""Report-sized figures derived only from frozen numerical evidence."""
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import roc_curve, precision_recall_curve
from src.common.loaders import sha256_file

ROOT = Path(__file__).resolve().parents[2]


def main():
    out = ROOT / "artifacts/report/stage6-v1"
    out.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 12, "axes.spines.top": False, "axes.spines.right": False})
    a = ROOT / "artifacts/metrics/stage3-baseline-v1/eda/regression_monthly_outcomes.csv"
    b = ROOT / "artifacts/metrics/stage3-baseline-v1/eda/classification_monthly_outcomes.csv"
    r, c = pd.read_csv(a), pd.read_csv(b)
    r = r.loc[r.purchase_year_month.between("2017-01", "2018-08")]
    c = c.loc[c.purchase_year_month.between("2017-01", "2018-08")]
    fig, axes = plt.subplots(1, 2, figsize=(7.15, 2.9), layout="constrained")
    axes[0].plot(range(len(r)), r["median"], color="#176c91", marker=".")
    axes[0].set(ylabel="Median duration (days)")
    axes[1].plot(range(len(c)), c.negative_rate * 100, color="#b35521", marker=".")
    axes[1].set(ylabel="Negative reviews (%)")
    for ax in axes:
        ax.set_xticks([0, 6, 12, 19], ["Jan17", "Jul17", "Jan18", "Aug18"])
        ax.set_xlabel("Purchase month")
        ax.grid(alpha=.15)
    fig.savefig(out / "monthly.png", dpi=200); plt.close(fig)
    p = ROOT / "artifacts/metrics/stage5-tutorial8-v1/learning_curve.csv"
    curve = pd.read_csv(p)
    fig, ax = plt.subplots(figsize=(7.15, 2.7), layout="constrained")
    for partition, name, color in [("training_resubstitution", "Training", "#a85121"), ("validation", "Validation", "#176c91")]:
        part = curve.loc[curve.partition.eq(partition)].groupby("fraction_training_groups").average_precision.agg(["mean", "std"])
        if len(part) != 3: raise ValueError("Learning-curve partition coverage")
        ax.errorbar(part.index * 100, part["mean"], yerr=part["std"], marker="o", capsize=4, label=name, color=color)
    ax.set(xlabel="Training customer groups (%)", ylabel="Average precision", xticks=[25, 50, 100])
    ax.legend(frameon=False, loc="center right"); ax.grid(alpha=.15)
    fig.savefig(out / "learning.png", dpi=200); plt.close(fig)
    cls_path = ROOT / "artifacts/metrics/stage5-final-v1/classification_holdout_predictions.csv"
    reg_path = ROOT / "artifacts/metrics/stage5-final-v1/regression_holdout_predictions.csv"
    subgroup_path = ROOT / "artifacts/metrics/stage5-final-v1/holdout_subgroups.csv"
    cls, reg, subgroup = pd.read_csv(cls_path), pd.read_csv(reg_path), pd.read_csv(subgroup_path)
    fig, axes = plt.subplots(1,2,figsize=(7.15,3.1),layout="constrained")
    fpr,tpr,_ = roc_curve(cls.target,cls.prediction)
    precision,recall,_ = precision_recall_curve(cls.target,cls.prediction)
    axes[0].plot(fpr,tpr,color="#176c91"); axes[0].plot([0,1],[0,1],ls="--",color="grey")
    axes[0].set(xlabel="False positive rate",ylabel="Recall")
    axes[1].plot(recall,precision,color="#176c91"); axes[1].axhline(cls.target.mean(),ls="--",color="grey")
    axes[1].set(xlabel="Recall",ylabel="Precision")
    fig.savefig(out / "holdout_curves.png",dpi=200); plt.close(fig)
    fig, axes = plt.subplots(1,2,figsize=(7.15,3.1),layout="constrained")
    # Deterministic evenly spaced sample for readability; metrics use all rows.
    sample = reg.iloc[::max(1,len(reg)//2500)]
    axes[0].scatter(sample.target,sample.prediction,s=3,alpha=.2,color="#176c91")
    maximum=max(reg.target.max(),reg.prediction.max())
    axes[0].plot([0,maximum],[0,maximum],ls="--",color="grey")
    axes[0].set(xlabel="Actual days",ylabel="Predicted days")
    part=subgroup.loc[subgroup.task.eq("regression") & subgroup.dimension.eq("observed_duration_days")].copy()
    if len(part)!=4: raise ValueError("Duration band evidence")
    part=part.set_index("subgroup").loc[["0-7","7-14","14-30","30+"]].reset_index()
    axes[1].bar(range(len(part)),part.mae,color="#176c91")
    axes[1].set_xticks(range(len(part)),part.subgroup)
    axes[1].set(xlabel="Actual-duration band",ylabel="MAE (days)")
    fig.savefig(out / "holdout_errors.png",dpi=200); plt.close(fig)
    manifest = {"sources": {str(x.relative_to(ROOT)): sha256_file(x) for x in [a, b, p,cls_path,reg_path,subgroup_path]},
        "figure_sources": {"monthly":[str(x.relative_to(ROOT)) for x in [a,b]],"learning":[str(p.relative_to(ROOT))],
            "holdout_curves":[str(cls_path.relative_to(ROOT))],"holdout_errors":[str(x.relative_to(ROOT)) for x in [reg_path,subgroup_path]]},
        "outputs": {x.name: sha256_file(x) for x in out.glob("*.png")}, "notes": {
            "monthly": "development task populations; 2017-01 through 2018-08; all months/counts in source CSVs",
            "learning": "classification; mean and sample SD across 5 saved folds, not confidence intervals",
            "holdout_curves":"all eligible reviewed holdout rows; frozen model; no new fits",
            "holdout_errors":"scatter deterministic every max(1,n//2500)-th row, all points untrimmed; band metrics use all eligible regression rows"}}
    (out / "figure_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__": main()
