"""Split-manifest builder (feature_contract.md v1.2 §7).

Entrypoint: ``python -m src.features.create_splits``

Reads the base table produced by ``build_features`` and writes, under
``data/business/ml/``:

    split_assignments.csv   one row per order: group, version, development/holdout/excluded
    cv_assignments.csv      one row per task and eligible development order: validation fold
    split_report.json       configuration, counts, checks, versions

Outer assignment: StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
on resolved customer groups with three per-order split-only strata (negative /
nonnegative / unknown review); fold 0 is the approximate 20% holdout, the rest
development. Order rows are passed with groups=customer_unique_id so every order
of a customer shares one outer assignment, but strata are per order — not an
"any negative review wins" customer-level stratum (feature_contract.md §7 step 2).
Inner task folds are independent five-fold splits within development
(StratifiedGroupKFold for classification, GroupKFold for regression).
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, StratifiedGroupKFold

from .contract import CONTRACT_VERSION, SPLIT_VERSION
from .serialization import publish_atomic, write_csv_lf, write_text_lf

OUTER_SPLITS = 5
OUTER_SEED = 42
INNER_SPLITS = 5
STAGING_DIR = "_staging"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_splits(ml: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    base = pd.read_csv(
        ml / "orders_ml_features.csv",
        usecols=["order_id", "customer_unique_id", "eligible_regression",
                 "eligible_classification", "is_detractor"],
    )
    base["_det"] = pd.to_numeric(base["is_detractor"], errors="coerce")

    resolved = base[base["customer_unique_id"].notna()].copy()
    excluded = base[base["customer_unique_id"].isna()].copy()

    # Order-level split-only strata (feature_contract.md §7 step 2).
    resolved["stratum"] = np.where(
        resolved["_det"] == 1, "negative",
        np.where(resolved["_det"] == 0, "nonnegative", "unknown"))

    # Stable order_id sort before splitting (feature_contract.md §7 step 2).
    resolved = resolved.sort_values("order_id", kind="mergesort").reset_index(drop=True)
    y = resolved["stratum"].to_numpy()
    gids = resolved["customer_unique_id"].to_numpy()

    sgkf = StratifiedGroupKFold(n_splits=OUTER_SPLITS, shuffle=True, random_state=OUTER_SEED)
    X = np.zeros((len(gids), 1))
    holdout_groups = set()
    for fold, (_, test_idx) in enumerate(sgkf.split(X, y, groups=gids)):
        if fold == 0:
            holdout_groups = set(gids[test_idx])

    assignments = resolved[["order_id", "customer_unique_id"]].copy()
    assignments["split_assignment"] = assignments["customer_unique_id"].map(
        lambda g: "holdout" if g in holdout_groups else "development")
    assignments["split_version"] = SPLIT_VERSION
    assignments["exclusion_reason"] = ""

    ex = excluded[["order_id", "customer_unique_id"]].copy()
    ex["split_assignment"] = "excluded"
    ex["split_version"] = SPLIT_VERSION
    ex["exclusion_reason"] = "missing_customer_group"

    assignments = pd.concat([assignments, ex], ignore_index=True)
    assignments = assignments.sort_values("order_id", kind="mergesort").reset_index(drop=True)

    # Inner task folds within development eligible rows.
    dev = resolved[~resolved["customer_unique_id"].isin(holdout_groups)].copy()

    cv_rows = []
    # Classification: StratifiedGroupKFold on binary is_detractor.
    cls_dev = dev[dev["eligible_classification"] == 1].copy()
    if len(cls_dev):
        cls_dev = cls_dev.sort_values("order_id", kind="mergesort").reset_index(drop=True)
        c_y = cls_dev["_det"].astype(int).to_numpy()  # 0/1 only (eligible => non-null)
        c_g = cls_dev["customer_unique_id"].to_numpy()
        cskf = StratifiedGroupKFold(n_splits=INNER_SPLITS, shuffle=True, random_state=OUTER_SEED)
        for fold, (_, test_idx) in enumerate(cskf.split(np.zeros((len(cls_dev), 1)), c_y, groups=c_g)):
            cv_rows.append(pd.DataFrame({
                "order_id": cls_dev["order_id"].iloc[test_idx].to_numpy(),
                "task": "classification",
                "validation_fold": fold,
            }))

    # Regression: GroupKFold.
    reg_dev = dev[dev["eligible_regression"] == 1].copy()
    if len(reg_dev):
        reg_dev = reg_dev.sort_values("order_id", kind="mergesort").reset_index(drop=True)
        r_g = reg_dev["customer_unique_id"].to_numpy()
        gkf = GroupKFold(n_splits=INNER_SPLITS)
        for fold, (_, test_idx) in enumerate(gkf.split(np.zeros((len(reg_dev), 1)), groups=r_g)):
            cv_rows.append(pd.DataFrame({
                "order_id": reg_dev["order_id"].iloc[test_idx].to_numpy(),
                "task": "regression",
                "validation_fold": fold,
            }))

    cv = pd.concat(cv_rows, ignore_index=True)
    cv["split_version"] = SPLIT_VERSION
    cv = cv.sort_values(["task", "order_id"], kind="mergesort").reset_index(drop=True)

    return assignments, cv


def _check_splits(assignments: pd.DataFrame, cv: pd.DataFrame,
                  base: pd.DataFrame) -> dict:
    results = []

    def add(fid, ok, detail):
        results.append({"id": fid, "status": "pass" if ok else "fail", "detail": detail})

    holdout = set(assignments.loc[assignments["split_assignment"] == "holdout", "customer_unique_id"])
    dev = set(assignments.loc[assignments["split_assignment"] == "development", "customer_unique_id"])
    add("outer_groups_disjoint", holdout.isdisjoint(dev),
        f"holdout {len(holdout)} groups disjoint from development {len(dev)} groups")

    # Both classification classes present in development and in each validation fold.
    cls_dev = cv[cv["task"] == "classification"].merge(
        base[["order_id", "is_detractor"]], on="order_id", how="left")
    if len(cls_dev):
        classes = sorted(pd.to_numeric(cls_dev["is_detractor"], errors="coerce").dropna().unique())
        add("classification_both_classes_development", set(classes) == {0.0, 1.0},
            f"development classification classes {classes}")
        per_fold_ok = all(
            set(pd.to_numeric(g["is_detractor"], errors="coerce").dropna().unique()) == {0.0, 1.0}
            for _, g in cls_dev.groupby("validation_fold"))
        add("classification_both_classes_each_fold", bool(per_fold_ok),
            "both classes present in every classification validation fold")

    # No holdout order appears in any CV assignment.
    holdout_orders = set(assignments.loc[assignments["split_assignment"] == "holdout", "order_id"])
    cv_orders = set(cv["order_id"])
    add("no_holdout_in_cv", holdout_orders.isdisjoint(cv_orders),
        "no holdout order assigned to an inner validation fold")

    return results


def _validate_staged(staging: Path, n_assignments: int, n_cv: int) -> None:
    """Confirm every staged split artifact exists, is non-empty and parseable
    before publication (feature_contract.md §11.4 validation-before-publish)."""
    expected = ["split_assignments.csv", "cv_assignments.csv", "split_report.json"]
    missing = [n for n in expected if not (staging / n).exists()]
    if missing:
        raise RuntimeError(f"staged split outputs missing before publication: {missing}")
    empty = [n for n in expected if (staging / n).stat().st_size == 0]
    if empty:
        raise RuntimeError(f"staged split outputs empty before publication: {empty}")

    split = pd.read_csv(staging / "split_assignments.csv")
    cv = pd.read_csv(staging / "cv_assignments.csv")
    json.loads((staging / "split_report.json").read_text(encoding="utf-8"))

    if len(split) != n_assignments:
        raise RuntimeError(
            f"staged split_assignments.csv has {len(split)} rows, expected {n_assignments}")
    if len(cv) != n_cv:
        raise RuntimeError(
            f"staged cv_assignments.csv has {len(cv)} rows, expected {n_cv}")


def main() -> None:
    repo = _repo_root()
    ml = repo / "data" / "business" / "ml"
    staging = ml / STAGING_DIR

    base = pd.read_csv(ml / "orders_ml_features.csv",
                       usecols=["order_id", "customer_unique_id", "is_detractor",
                                "eligible_regression", "eligible_classification"])
    assignments, cv = build_splits(ml)
    checks = _check_splits(assignments, cv, base)

    report = {
        "split_version": SPLIT_VERSION,
        "contract_version": CONTRACT_VERSION,
        "library_versions": {"scikit-learn": _sklearn_version()},
        "outer_config": {"n_splits": OUTER_SPLITS, "shuffle": True, "random_state": OUTER_SEED,
                         "holdout_fold": 0,
                         "strata": ["negative", "nonnegative", "unknown"],
                         "strata_grain": "per order, grouped by customer_unique_id"},
        "counts": {
            "holdout_orders": int((assignments["split_assignment"] == "holdout").sum()),
            "development_orders": int((assignments["split_assignment"] == "development").sum()),
            "excluded_orders": int((assignments["split_assignment"] == "excluded").sum()),
            "cv_classification_rows": int((cv["task"] == "classification").sum()),
            "cv_regression_rows": int((cv["task"] == "regression").sum()),
        },
        "checks": checks,
        "run_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    failed = [c for c in checks if c["status"] == "fail"]

    # Stage, run checks, publish only on success (feature_contract.md §11.4).
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    write_csv_lf(assignments, staging / "split_assignments.csv")
    write_csv_lf(cv, staging / "cv_assignments.csv")
    write_text_lf(json.dumps(report, indent=2) + "\n", staging / "split_report.json")

    if failed:
        raise RuntimeError(
            "Split checks failed; previous published outputs left intact.\n"
            + "\n".join(f"- {c['id']}: {c['detail']}" for c in failed))

    # Validate the staged bundle, then publish atomically (rollback on a handled
    # replacement failure; feature_contract.md §11.4).
    _validate_staged(staging, len(assignments), len(cv))
    publish_atomic(staging, ml)
    staging.rmdir()

    print("create_splits complete.")
    print(f"  split_assignments.csv: {len(assignments)} orders "
          f"(holdout {int((assignments['split_assignment']=='holdout').sum())}, "
          f"dev {int((assignments['split_assignment']=='development').sum())}, "
          f"excluded {int((assignments['split_assignment']=='excluded').sum())})")
    print(f"  cv_assignments.csv: {len(cv)} rows")


def _sklearn_version() -> str:
    import sklearn
    return sklearn.__version__


if __name__ == "__main__":
    main()
