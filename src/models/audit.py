"""Problem-driven development EDA and review-target sensitivity, never predictor construction."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.features.contract import PREDICTOR_ALLOWLIST, NUMERIC_COLUMNS, CATEGORICAL_COLUMNS
from .data import task_rows
from .io import write_csv_lf, write_json


def first_review_audit(development, reviews):
    reviews = reviews.copy()
    reviews["source_row_index"] = np.arange(len(reviews))
    # Filter source reviews to permitted orders before any score analysis.
    rows = reviews.merge(development[["order_id", "prediction_timestamp"]], on="order_id", validate="many_to_one")
    score = pd.to_numeric(rows.review_score, errors="coerce")
    valid = score.between(1, 5) & score.eq(np.floor(score))
    answer = pd.to_datetime(rows.review_answer_timestamp, errors="coerce")
    purchase = pd.to_datetime(rows.prediction_timestamp, errors="coerce")
    rows["valid_score"] = score.where(valid)
    rows["answer"] = answer
    rows["exclusion"] = np.select([~valid, answer.isna(), answer < purchase],
                                   ["invalid_score", "missing_or_invalid_answer", "answer_before_purchase"], default="usable")
    usable = rows.loc[rows.exclusion.eq("usable")].copy()
    usable["review_id_sort"] = usable.review_id.fillna("")
    first = usable.sort_values(["order_id", "answer", "review_id_sort", "source_row_index"], kind="mergesort").drop_duplicates("order_id")
    baseline = development.loc[development.eligible_classification.eq(1),
                               ["order_id", "review_score_min", "is_detractor", "review_count"]]
    minima = rows.groupby("order_id").valid_score.min()
    computed = baseline.order_id.map(minima)
    if not np.array_equal(computed.to_numpy(), baseline.review_score_min.to_numpy()):
        raise ValueError("Review-audit minima disagree with frozen baseline labels")
    common = baseline.merge(first[["order_id", "valid_score", "answer", "review_id", "source_row_index"]],
                            on="order_id", validate="one_to_one").rename(columns={"valid_score": "review_score_first"})
    common["is_detractor_first"] = common.review_score_first.le(2).astype(int)
    if (common.review_score_min > common.review_score_first).any() or (common.is_detractor < common.is_detractor_first).any():
        raise ValueError("Minimum-score direction assertion failed")
    common["label_disagrees"] = common.is_detractor.ne(common.is_detractor_first).astype(int)
    counts = pd.crosstab(common.is_detractor, common.is_detractor_first).reindex(index=[0, 1], columns=[0, 1], fill_value=0)
    summary = {"development_review_rows": len(rows), "baseline_orders": len(baseline),
               "baseline_negative_prevalence": float(baseline.is_detractor.mean()),
               "baseline_multi_review_orders": int(baseline.review_count.gt(1).sum()),
               "common_orders": len(common), "missing_alternative_orders": len(baseline) - len(common),
               "exclusions_first_failure": rows.exclusion.value_counts().to_dict(),
               "valid_score_missing_answer_rows": int((valid & answer.isna()).sum()),
               "baseline_score_counts": baseline.review_score_min.value_counts().sort_index().to_dict(),
               "direction_assertion": "passed", "alternative_retraining": "not performed",
               "matched": {}, "disagreement_table": counts.to_dict()}
    for name, cohort in [("all", common), ("multi_review", common.loc[common.review_count.gt(1)])]:
        summary["matched"][name] = {"n": len(cohort), "disagreements": int(cohort.label_disagrees.sum()),
            "baseline_prevalence": float(cohort.is_detractor.mean()),
            "first_prevalence": float(cohort.is_detractor_first.mean()),
            "prevalence_difference": float((cohort.is_detractor - cohort.is_detractor_first).mean()),
            "minimum_score_counts": cohort.review_score_min.value_counts().sort_index().to_dict(),
            "first_score_counts": cohort.review_score_first.value_counts().sort_index().to_dict()}
    summary["review_timing"] = {"answer_before_purchase_valid_score_rows": int((valid & (answer < purchase)).sum()),
                               "usable_review_lag_days_quantiles": ((usable.answer - pd.to_datetime(usable.prediction_timestamp)).dt.total_seconds()/86400).quantile([0,.25,.5,.75,1]).to_dict()}
    return common, summary


def feature_summary(rows):
    summary = rows[NUMERIC_COLUMNS].describe().T.reset_index(names="feature")
    summary["missing_n"] = summary.feature.map(rows[NUMERIC_COLUMNS].isna().sum())
    summary["missing_fraction"] = summary.missing_n / len(rows)
    summary["denominator"] = len(rows)
    summary["constant_nonmissing"] = summary.feature.map(rows[NUMERIC_COLUMNS].nunique()).le(1)
    return summary


def _groups(rows, task, feature):
    values = rows[feature]
    if feature == "n_items":
        group = pd.cut(values,[-1,0,1,3,np.inf],labels=["0","1","2–3","4+"]).astype("string").fillna("Unknown")
    elif feature in CATEGORICAL_COLUMNS or values.nunique() <= 8:
        group = values.astype("string").fillna("Unknown")
    else:
        # Descriptive development quantiles only. Never exported as model features.
        group = pd.qcut(values, 4, duplicates="drop").astype("string").fillna("Unknown")
    target = "lead_days" if task == "regression" else "is_detractor"
    table = rows.assign(eda_group=group).groupby("eda_group", observed=True)[target].agg(
        n="count", mean="mean", median="median", p25=lambda s:s.quantile(.25), p75=lambda s:s.quantile(.75))
    if task == "classification":
        table["positives"] = rows.assign(eda_group=group).groupby("eda_group", observed=True)[target].sum()
    return table.reset_index().assign(feature=feature, task=task, missing_feature_n=int(values.isna().sum()))


def run_audits(root, development, cv, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out.mkdir()
    figures = out / "figures"
    figures.mkdir()
    reviews = pd.read_csv(root / "data/preprocessed/olist_order_reviews_dataset.csv",
                          usecols=["order_id", "review_id", "review_score", "review_answer_timestamp"], dtype={"order_id":"string", "review_id":"string"})
    common, review_summary = first_review_audit(development, reviews)
    write_csv_lf(common, out / "review_label_comparison.csv")
    write_json(review_summary, out / "review_label_audit.json")
    orders = pd.read_csv(root / "data/preprocessed/olist_orders_dataset.csv",
                         usecols=["order_id", "order_delivered_customer_date", "order_estimated_delivery_date"], dtype={"order_id":"string"})
    outcomes = development.merge(orders, on="order_id", validate="one_to_one")
    delivered = pd.to_datetime(outcomes.order_delivered_customer_date, errors="coerce")
    estimated = pd.to_datetime(outcomes.order_estimated_delivery_date, errors="coerce")
    outcomes["late"] = (delivered > estimated).astype(float).where(outcomes.eligible_regression.eq(1) & delivered.notna() & estimated.notna())
    outcomes["purchase_year_month"] = pd.to_datetime(outcomes.prediction_timestamp).dt.to_period("M").astype(str)
    relationships = []
    month_tables = []
    task_counts = {}
    for task in ["regression", "classification"]:
        rows = task_rows(outcomes, cv, task)
        task_counts[task] = {"n":len(rows), "customer_groups":rows.customer_unique_id.nunique()}
        if task == "classification":
            task_counts[task]["positives"] = int(rows.is_detractor.sum())
        write_csv_lf(feature_summary(rows), out / f"{task}_numeric_summary.csv")
        category_tables = []
        for col in CATEGORICAL_COLUMNS:
            category_tables.append(rows[col].astype("string").fillna("Unknown").value_counts().rename_axis("category").reset_index(name="n").assign(feature=col, denominator=len(rows)))
        write_csv_lf(pd.concat(category_tables), out / f"{task}_category_counts.csv")
        correlation = rows[NUMERIC_COLUMNS + (["lead_days"] if task == "regression" else ["is_detractor"])].corr()
        write_csv_lf(correlation.reset_index(names="feature"), out / f"{task}_pearson_correlations.csv")
        pair_counts = rows[correlation.columns].notna().astype(int).T.dot(rows[correlation.columns].notna().astype(int))
        write_csv_lf(pair_counts.reset_index(names="feature"), out / f"{task}_correlation_pair_counts.csv")
        for col in ["customer_state", "distance_km_max", "interstate_share", "n_items", "n_sellers", "total_weight_g", "total_volume_cm3", "total_price", "total_freight", "freight_ratio", "primary_category", "primary_payment_type", "purchase_month"]:
            relationships.append(_groups(rows, task, col))
        grouped = rows.groupby("purchase_year_month")
        if task == "regression":
            month = grouped.lead_days.agg(n="count", median="median", p25=lambda s:s.quantile(.25), p75=lambda s:s.quantile(.75)).reset_index()
            month["late_valid_n"] = month.purchase_year_month.map(grouped.late.count())
            month["late_rate"] = month.purchase_year_month.map(grouped.late.mean())
        else:
            month = grouped.is_detractor.agg(n="count", positives="sum", negative_rate="mean").reset_index()
            score = pd.crosstab(rows.purchase_year_month, rows.review_score_min).reindex(columns=[1,2,3,4,5],fill_value=0)
            write_csv_lf(score.reset_index(), out / "monthly_review_score_counts.csv")
        month_tables.append(month.assign(task=task))
        write_csv_lf(month, out / f"{task}_monthly_outcomes.csv")
        fig, ax = plt.subplots(figsize=(9,4))
        key = "median" if task == "regression" else "negative_rate"
        ax.plot(month.purchase_year_month, month[key], marker="o", markersize=3)
        ax.set(ylabel="Median lead time (days)" if task == "regression" else "Recorded negative-review rate",
               title=f"Development {task} outcomes by purchase month (eligible cohort)")
        ax.tick_params(axis="x", rotation=65);fig.tight_layout();fig.savefig(figures / f"{task}_monthly.png",dpi=150);plt.close(fig)
        fig, axes = plt.subplots(1,4,figsize=(12,3))
        for ax,col in zip(axes,["total_price","total_weight_g","total_volume_cm3","distance_km_max"]):
            vals = rows[col].dropna()
            ax.hist(np.log1p(vals), bins=35)
            ax.set(xlabel=f"log1p({col})",ylabel="Orders",title=f"Observed n={len(vals):,}")
        fig.suptitle(f"Development {task}: display transform only, models use original units")
        fig.tight_layout();fig.savefig(figures/f"{task}_distributions.png",dpi=150);plt.close(fig)
    relation_table = pd.concat(relationships,ignore_index=True)
    write_csv_lf(relation_table, out / "feature_outcome_relationships.csv")
    fig, axes = plt.subplots(2,3,figsize=(12,7))
    for i,task in enumerate(["regression","classification"]):
        for j,feature in enumerate(["distance_km_max","n_items","freight_ratio"]):
            table = relation_table.loc[relation_table.task.eq(task) & relation_table.feature.eq(feature)]
            # For n_items retain all groups; labels and n are saved in companion CSV.
            axes[i,j].bar(np.arange(len(table)), table["median" if task=="regression" else "mean"])
            axes[i,j].set_xticks(np.arange(len(table)),table.eda_group,rotation=65,ha="right",fontsize=7)
            axes[i,j].set(title=f"{task}: {feature}",ylabel="Median days" if task=="regression" else "Negative rate")
    fig.tight_layout();fig.savefig(figures/"relationships.png",dpi=150);plt.close(fig)
    intersection = outcomes.loc[outcomes.eligible_regression.eq(1) & outcomes.eligible_classification.eq(1)].copy()
    intersection["duration_band"] = pd.cut(intersection.lead_days,[0,7,14,30,np.inf], labels=["0–7","7–14","14–30",">30"],right=True).astype("string")
    for feature in ["duration_band","late"]:
        table = intersection.groupby(feature,dropna=False).is_detractor.agg(n="count",positives="sum",negative_rate="mean").reset_index()
        write_csv_lf(table,out/f"review_vs_{feature}_diagnostic.csv")
    join_example = {"synthetic_fixture_not_observed":True,"items":[{"price":10,"freight":2},{"price":20,"freight":3}],
                    "payments":[12,23],"review_scores":[5,1],"raw_cartesian_rows":8,
                    "unsafe_cartesian_price_sum":120,"correct_n_items":2,"correct_total_price":30,
                    "correct_total_freight":5,"correct_freight_ratio":5/30,"correct_review_min":1,
                    "correct_is_detractor":1,"correct_order_rows":1}
    write_json(join_example,out/"join_worked_fixture.json")
    summary = {"development_orders":len(development),"tasks":task_counts,
               "review_audit":review_summary,"outcome_intersection_n":len(intersection),
               "late_rule":"actual customer delivery timestamp > estimated timestamp; full source precision, not date-only",
               "late_valid_intersection_n":int(intersection.late.notna().sum()),
               "correlation_policy":"pairwise complete Pearson, no imputation; pair counts separately saved",
               "display_policy":"log1p distributions for display only; no baseline logs or clipping",
               "caveat":"Recent/sparse months and variable follow-up prevent causal or future-time claims"}
    write_json(summary,out/"audit_summary.json")
    return summary
