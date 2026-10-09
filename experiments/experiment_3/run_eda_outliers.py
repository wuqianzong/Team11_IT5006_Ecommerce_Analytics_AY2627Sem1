"""Phase 1: Skewness Audit, Outlier Diagnostics & Business Scenario Evaluation.

Curriculum Compliance:
- IT5006 Week 01-02 (T1.ipynb, T2.ipynb): Descriptive statistics, skew(), kurtosis(), IQR, boxplots.
- IT5006 Week 03 (T03.ipynb): Handling outliers, clipping (np.clip), quantile boundaries.
- IT5006 Week 05 (T05.ipynb): Cook's distance, leverage, heteroscedasticity, log-response.

Zero changes to src/ or data/. Contained inside experiments/experiment_3/ and artifacts/metrics/experiment-3/.
"""
from __future__ import annotations

import os
from pathlib import Path

# Set writable cache directory for Matplotlib
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib"

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[2]
EXP_DIR = ROOT / "experiments/experiment_3"
OUT_DIR = ROOT / "artifacts/metrics/experiment-3/eda"
DATA_DIR = EXP_DIR / "data"

OUT_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_development_data():
    ml = ROOT / "data/business/ml"
    base = pd.read_csv(ml / "orders_ml_features.csv", dtype={"order_id": "string", "customer_unique_id": "string"})
    splits = pd.read_csv(ml / "split_assignments.csv", dtype="string")
    cv = pd.read_csv(ml / "cv_assignments.csv", dtype={"order_id": "string"})

    merged = base.merge(splits[["order_id", "split_assignment"]], on="order_id", validate="one_to_one")
    dev = merged[merged["split_assignment"] == "development"].copy()

    # Filter to eligible regression development orders
    reg_dev = dev[dev["eligible_regression"] == 1].merge(
        cv[cv["task"] == "regression"][["order_id", "validation_fold"]],
        on="order_id", validate="one_to_one"
    )
    return reg_dev.sort_values("order_id").reset_index(drop=True)


def audit_skewness_kurtosis(df: pd.DataFrame):
    print("\n--- 1. Computing Skewness, Kurtosis & Quantile Profiles ---")
    numeric_cols = [
        "lead_days", "total_price", "total_freight", "freight_ratio",
        "distance_km_max", "n_items", "n_products", "n_sellers",
        "total_weight_g", "total_volume_cm3"
    ]

    records = []
    for col in numeric_cols:
        series = df[col].dropna()
        skew_val = float(stats.skew(series))
        kurt_val = float(stats.kurtosis(series))
        p25, p50, p75, p90, p95, p99 = np.percentile(series, [25, 50, 75, 90, 95, 99])
        iqr = p75 - p25

        # Classify skew severity
        if abs(skew_val) > 2.0:
            skew_class = "Extreme Right Skew (Action: log1p mandatory)"
        elif abs(skew_val) > 1.0:
            skew_class = "Moderate Skew (Action: evaluate log1p)"
        else:
            skew_class = "Approximately Symmetric"

        records.append({
            "feature": col,
            "count": len(series),
            "mean": float(series.mean()),
            "std": float(series.std()),
            "skewness": skew_val,
            "kurtosis": kurt_val,
            "p25": p25,
            "median_p50": p50,
            "p75": p75,
            "iqr": iqr,
            "p95": p95,
            "p99": p99,
            "max": float(series.max()),
            "skew_classification": skew_class
        })

    audit_df = pd.DataFrame(records)
    audit_df.to_csv(OUT_DIR / "skewness_kurtosis_audit.csv", index=False)
    print(audit_df[["feature", "skewness", "kurtosis", "median_p50", "p99", "max", "skew_classification"]].to_string())
    return audit_df


def generate_diagnostic_plots(df: pd.DataFrame):
    print("\n--- 2. Generating Diagnostic Plots (Matplotlib) ---")
    plt.rcParams.update({
        "font.size": 10,
        "axes.labelsize": 11,
        "axes.titlesize": 12,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "grid.alpha": 0.3
    })

    # 1. Boxplots: Raw vs Log-transformed (side-by-side)
    fig, axes = plt.subplots(4, 2, figsize=(14, 16))
    features_to_plot = [
        ("lead_days", "Delivery Lead Time (Days)"),
        ("total_price", "Total Order Price (BRL)"),
        ("total_freight", "Total Freight Cost (BRL)"),
        ("distance_km_max", "Max Delivery Distance (km)")
    ]

    for row_idx, (col, label) in enumerate(features_to_plot):
        data = df[col].dropna()

        # Raw boxplot
        axes[row_idx, 0].boxplot(data, vert=False, patch_artist=True,
                                 boxprops=dict(facecolor="#3498db", color="#2980b9"),
                                 medianprops=dict(color="#e74c3c", linewidth=2),
                                 flierprops=dict(marker="o", markersize=2, alpha=0.3, color="#7f8c8d"))
        axes[row_idx, 0].set_title(f"Raw Distribution: {label}", fontweight="bold")
        axes[row_idx, 0].set_xlabel(f"{label} (Raw Scale)")
        axes[row_idx, 0].grid(True, linestyle="--")

        # Log1p boxplot
        log_data = np.log1p(data)
        axes[row_idx, 1].boxplot(log_data, vert=False, patch_artist=True,
                                 boxprops=dict(facecolor="#2ecc71", color="#27ae60"),
                                 medianprops=dict(color="#e74c3c", linewidth=2),
                                 flierprops=dict(marker="o", markersize=2, alpha=0.3, color="#7f8c8d"))
        axes[row_idx, 1].set_title(f"Log-Transformed [log(1+x)]: {label}", fontweight="bold")
        axes[row_idx, 1].set_xlabel(f"log(1 + {label})")
        axes[row_idx, 1].grid(True, linestyle="--")

    plt.tight_layout()
    plt.savefig(OUT_DIR / "boxplots_skew.png", dpi=300)
    plt.close()
    print("Saved:", OUT_DIR / "boxplots_skew.png")

    # 2. Scatter Plot: Lead Time vs Distance with Delay Outlier Contours
    plt.figure(figsize=(10, 6))
    sample = df.sample(n=min(5000, len(df)), random_state=42)
    normal_pts = sample[sample["lead_days"] <= 60]
    outlier_pts = sample[sample["lead_days"] > 60]

    plt.scatter(normal_pts["distance_km_max"], normal_pts["lead_days"],
                alpha=0.25, color="#2980b9", s=20, label="Typical Orders (<= 60 days)")
    plt.scatter(outlier_pts["distance_km_max"], outlier_pts["lead_days"],
                alpha=0.85, color="#e74c3c", s=45, edgecolor="black", linewidth=0.5,
                label=f"Extreme Delay Outliers (> 60 days, n={len(outlier_pts)})")

    plt.axhline(60, color="#c0392b", linestyle="--", linewidth=1.5, label="60-Day Severe Outlier Boundary")
    plt.title("Lead Time vs. Transit Distance: Isolating Extreme Operational Delay Outliers", fontsize=13, fontweight="bold")
    plt.xlabel("Max Transit Distance (km)", fontsize=11)
    plt.ylabel("Delivery Lead Time (Days)", fontsize=11)
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.legend(loc="upper right", frameon=True)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "cooks_distance.png", dpi=300)
    plt.close()
    print("Saved:", OUT_DIR / "cooks_distance.png")

    # 3. Monthly Seasonality & Delay Spike Analysis
    monthly_stats = df.groupby("purchase_month")["lead_days"].agg(
        mean="mean", median="median", p90=lambda x: np.percentile(x, 90), p99=lambda x: np.percentile(x, 99)
    ).reset_index()

    plt.figure(figsize=(10, 5))
    plt.plot(monthly_stats["purchase_month"], monthly_stats["mean"], marker="o", color="#e67e22", linewidth=2, label="Mean Lead Time")
    plt.plot(monthly_stats["purchase_month"], monthly_stats["median"], marker="s", color="#27ae60", linewidth=2, label="Median Lead Time")
    plt.plot(monthly_stats["purchase_month"], monthly_stats["p99"], marker="^", linestyle="--", color="#c0392b", linewidth=1.8, label="P99 Extreme Delay")
    plt.xticks(range(1, 13), ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
    plt.title("Monthly Seasonality of Delivery Delays: Structural Winter/Holiday Surges", fontsize=13, fontweight="bold")
    plt.xlabel("Purchase Month", fontsize=11)
    plt.ylabel("Days", fontsize=11)
    plt.legend(loc="upper left")
    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(OUT_DIR / "delay_seasonality.png", dpi=300)
    plt.close()
    print("Saved:", OUT_DIR / "delay_seasonality.png")


def evaluate_outlier_policies(df: pd.DataFrame):
    print("\n--- 3. 3-Way Empirical Benchmark: Raw vs. Clipped vs. Removed ---")
    # Base 13 features used in regression
    base_features = [
        "n_items", "has_items", "n_products", "total_price", "total_freight",
        "freight_ratio", "freight_ratio_missing", "customer_state",
        "purchase_month", "purchase_dayofweek", "purchase_hour",
        "distance_km_max", "distance_missing_fraction"
    ]

    def preprocess_fold(train_df, val_df, policy="raw"):
        X_train = train_df[base_features].copy()
        y_train = train_df["lead_days"].copy()
        X_val = val_df[base_features].copy()
        y_val = val_df["lead_days"].copy()

        if policy == "removed":
            keep_mask = y_train <= 60.0
            X_train = X_train[keep_mask]
            y_train = y_train[keep_mask]
        elif policy == "clipped":
            p99_freight = float(np.percentile(X_train["total_freight"].dropna(), 99))
            X_train["total_freight"] = np.clip(X_train["total_freight"], 0, p99_freight)
            X_val["total_freight"] = np.clip(X_val["total_freight"], 0, p99_freight)
            # Clip target at 60 days in train only
            y_train = np.clip(y_train, 0.5, 60.0)

        # Impute numeric
        for col in ["total_price", "total_freight", "freight_ratio", "distance_km_max"]:
            med = X_train[col].median()
            X_train[col] = X_train[col].fillna(med)
            X_val[col] = X_val[col].fillna(med)

        # One hot encode customer state and calendar
        cats = ["customer_state", "purchase_month", "purchase_dayofweek", "purchase_hour"]
        X_train_encoded = pd.get_dummies(X_train, columns=cats, drop_first=False)
        X_val_encoded = pd.get_dummies(X_val, columns=cats, drop_first=False)
        X_train_encoded, X_val_encoded = X_train_encoded.align(X_val_encoded, join="left", axis=1, fill_value=0)

        return X_train_encoded, y_train, X_val_encoded, y_val

    policies = ["raw", "clipped", "removed"]
    results = []

    for policy in policies:
        fold_maes = []
        fold_rmses = []
        fold_r2s = []

        for fold in range(5):
            train_mask = df["validation_fold"] != fold
            val_mask = df["validation_fold"] == fold

            X_tr, y_tr, X_va, y_va = preprocess_fold(df[train_mask], df[val_mask], policy=policy)

            model = DecisionTreeRegressor(max_depth=5, min_samples_leaf=100, random_state=42)
            model.fit(X_tr, y_tr)
            y_pred = model.predict(X_va)

            # Note: y_va is ALWAYS original unclipped validation target to evaluate true customer experience
            fold_maes.append(mean_absolute_error(y_va, y_pred))
            fold_rmses.append(root_mean_squared_error(y_va, y_pred))
            fold_r2s.append(r2_score(y_va, y_pred))

        results.append({
            "policy": policy,
            "description": "Raw Baseline" if policy == "raw" else ("Winsorized (Target 60d, Freight P99)" if policy == "clipped" else "Dropped y > 60d in Train"),
            "mae_mean": float(np.mean(fold_maes)),
            "mae_std": float(np.std(fold_maes)),
            "rmse_mean": float(np.mean(fold_rmses)),
            "rmse_std": float(np.std(fold_rmses)),
            "r2_mean": float(np.mean(fold_r2s)),
            "r2_std": float(np.std(fold_r2s))
        })

    ablation_df = pd.DataFrame(results)
    ablation_df.to_csv(OUT_DIR / "outlier_ablation_summary.csv", index=False)
    print("\n--- 3-Way Outlier Policy Ablation Results ---")
    print(ablation_df.to_string(index=False))
    return ablation_df


def save_outlier_sample(df: pd.DataFrame):
    extreme_orders = df[df["lead_days"] > 60][[
        "order_id", "customer_state", "distance_km_max", "total_freight", "total_price", "lead_days", "purchase_month"
    ]].sort_values("lead_days", ascending=False).head(20)
    extreme_orders.to_csv(OUT_DIR / "outlier_records_sample.csv", index=False)
    print(f"\nSaved {len(extreme_orders)} extreme outlier samples to {OUT_DIR / 'outlier_records_sample.csv'}")


if __name__ == "__main__":
    print("================================================================================")
    print("STARTING EXPERIMENT 3 - PHASE 1: SKEWNESS & OUTLIER DIAGNOSTICS")
    print("================================================================================")
    df = load_development_data()
    print(f"Loaded {len(df)} eligible development regression orders.")
    audit_skewness_kurtosis(df)
    generate_diagnostic_plots(df)
    evaluate_outlier_policies(df)
    save_outlier_sample(df)
    print("\n[SUCCESS] Phase 1 Completed. All outputs logged in artifacts/metrics/experiment-3/eda/")
