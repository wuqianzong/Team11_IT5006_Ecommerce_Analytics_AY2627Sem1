"""Task metrics with explicit positive class, denominators and operating conventions."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import (accuracy_score, average_precision_score, brier_score_loss,
                             confusion_matrix, mean_absolute_error, mean_squared_error,
                             precision_score, recall_score, f1_score, r2_score, roc_auc_score)


def metrics(task, y, score, threshold=0.5):
    y, score = np.asarray(y), np.asarray(score)
    if len(y) == 0 or len(y) != len(score) or not np.isfinite(score).all():
        raise ValueError("Empty, misaligned or nonfinite evaluation")
    if task == "regression":
        return {"n": len(y), "mae": mean_absolute_error(y, score),
                "rmse": np.sqrt(mean_squared_error(y, score)),
                "r2": r2_score(y, score) if len(y) > 1 else None,
                "negative_predictions": int((score < 0).sum())}
    if task != "classification" or not set(np.unique(y)).issubset({0, 1}):
        raise ValueError("Invalid task/class labels")
    if (score < 0).any() or (score > 1).any():
        raise ValueError("Probability outside [0,1]")
    pred = (score >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    both = len(np.unique(y)) == 2
    positives, negatives = int((y == 1).sum()), int((y == 0).sum())
    return {"n": len(y), "positives": positives, "negatives": negatives,
            "prevalence": float(y.mean()), "threshold": threshold,
            "average_precision": average_precision_score(y, score) if both else None,
            "roc_auc": roc_auc_score(y, score) if both else None,
            "brier": brier_score_loss(y, score, pos_label=1), "mean_probability": float(score.mean()),
            "accuracy": accuracy_score(y, pred), "precision_1": precision_score(y, pred, zero_division=0),
            "recall_1": recall_score(y, pred, zero_division=0) if positives else None,
            "f1_1": f1_score(y, pred, zero_division=0) if positives else None,
            "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
            "fpr": float(fp / negatives) if negatives else None,
            "fnr": float(fn / positives) if positives else None,
            "specificity": float(tn / negatives) if negatives else None,
            "precision_defined": bool(tp + fp), "ranking_metrics_defined": both}


def capacity_metrics(y, scores, ids, fraction):
    # Fixed diagnostic capacity; deterministic order_id tie-break, not a tuned
    # deployment threshold or a claimed service budget.
    k = max(1, int(np.ceil(len(y) * fraction)))
    ranked = np.lexsort((np.asarray(ids).astype(str), -np.asarray(scores)))[:k]
    positives = int(np.asarray(y).sum())
    captured = int(np.asarray(y)[ranked].sum())
    return {"capacity_fraction": fraction, "selected_n": k, "captured_positives": captured,
            "precision_at_capacity": captured / k,
            "recall_at_capacity": captured / positives if positives else None}
