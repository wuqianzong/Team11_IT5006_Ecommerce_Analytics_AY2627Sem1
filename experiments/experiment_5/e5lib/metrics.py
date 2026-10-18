"""Metric definitions and the s01 decision rule (README section 13.1).

score() returns every s01 metric for a task (G-24). one_se_select() applies the
one-standard-error rule (G-33, G-55): among candidates whose fold-mean primary metric is
within one standard error of the best mean, choose the simplest.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.metrics import (average_precision_score, brier_score_loss, confusion_matrix, f1_score,
                             mean_absolute_error, mean_squared_error, precision_score, r2_score,
                             recall_score, roc_auc_score)

PRIMARY = {"regression": ("mae", False), "classification": ("ap", True)}  # (metric, higher_is_better)
COST_FN, COST_FP = 5.0, 1.0  # s01 1.5 illustrative cost


def score(task: str, y_true, y_pred=None, proba=None, threshold: float | None = None) -> dict[str, float]:
    y_true = np.asarray(y_true)
    out: dict[str, float] = {"n_rows": float(len(y_true))}
    if task == "regression":
        y_pred = np.asarray(y_pred, dtype=float)
        err = y_pred - y_true
        out.update({
            "mae": mean_absolute_error(y_true, y_pred),
            "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
            "r2": r2_score(y_true, y_pred),
            "within_3d": float(np.mean(np.abs(err) <= 3.0)),
        })
        return out
    if task != "classification":
        raise KeyError(task)
    out["n_pos"] = float(y_true.sum())
    out["prevalence"] = float(y_true.mean())
    if proba is not None:
        proba = np.asarray(proba, dtype=float)
        out.update({
            "ap": average_precision_score(y_true, proba),
            "roc_auc": roc_auc_score(y_true, proba) if len(np.unique(y_true)) == 2 else np.nan,
            "brier": brier_score_loss(y_true, proba),
        })
        if threshold is not None:
            y_pred = (proba >= threshold).astype(int)
    if y_pred is not None:
        y_pred = np.asarray(y_pred).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
        n = len(y_true)
        out.update({
            "precision": precision_score(y_true, y_pred, zero_division=0),
            "recall": recall_score(y_true, y_pred, zero_division=0),
            "f1": f1_score(y_true, y_pred, zero_division=0),
            "tp": float(tp), "fp": float(fp), "tn": float(tn), "fn": float(fn),
            "alert_rate": (tp + fp) / n, "error_rate": (fn + fp) / n,
            "cost": COST_FN * fn + COST_FP * fp,
        })
    return out


def fold_summary(results: pd.DataFrame, metric: str) -> pd.DataFrame:
    """Per-candidate mean, SD, SE and fold count from long results (candidate_id, fold, metric, value)."""
    r = results[results["metric"] == metric]
    g = r.groupby("candidate_id")["value"]
    summary = pd.DataFrame({"mean": g.mean(), "sd": g.std(ddof=1), "n_folds": g.count()})
    summary["se"] = summary["sd"] / np.sqrt(summary["n_folds"])
    return summary


def one_se_select(results: pd.DataFrame, metric: str, higher_is_better: bool,
                  simplicity: dict[str, int]) -> dict:
    """Apply the one-SE rule.

    results: long table with candidate_id, fold, metric, value (validation scores).
    simplicity: candidate_id -> rank (lower = simpler), pre-registered order (s01 1.7).
    Returns the best candidate, the chosen one, the band and the summary table.
    """
    summary = fold_summary(results, metric)
    missing = set(summary.index) - set(simplicity)
    if missing:
        raise ValueError(f"no simplicity rank for {sorted(missing)}")
    best = summary["mean"].idxmax() if higher_is_better else summary["mean"].idxmin()
    best_mean, best_se = summary.loc[best, "mean"], summary.loc[best, "se"]
    if higher_is_better:
        within = summary[summary["mean"] >= best_mean - best_se]
    else:
        within = summary[summary["mean"] <= best_mean + best_se]
    chosen = min(within.index, key=lambda c: (simplicity[c], c))
    summary = summary.assign(simplicity=[simplicity[c] for c in summary.index],
                             within_one_se=summary.index.isin(within.index))
    return {"metric": metric, "best": best, "chosen": chosen,
            "band": [float(best_mean - best_se), float(best_mean + best_se)],
            "summary": summary.reset_index()}
