"""Development-only threshold scenarios, with exact ties and explicit assumptions."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .evaluate import metrics


def threshold_curve(y, probability):
    y = np.asarray(y)
    probability = np.asarray(probability, dtype=float)
    if len(y) == 0 or len(y) != len(probability) or not set(np.unique(y)) <= {0, 1}:
        raise ValueError("Invalid threshold population")
    if not np.isfinite(probability).all() or ((probability < 0) | (probability > 1)).any():
        raise ValueError("Invalid probabilities")
    grouped = pd.DataFrame({"threshold": probability, "positive": y}).groupby(
        "threshold", sort=True).positive.agg(["size", "sum"]).sort_index(ascending=False)
    tp = grouped["sum"].cumsum().to_numpy(dtype=int)
    fp = grouped["size"].cumsum().to_numpy(dtype=int) - tp
    positives, negatives = int(y.sum()), len(y) - int(y.sum())
    curve = pd.DataFrame({"threshold": grouped.index, "tp": tp, "fp": fp,
                          "fn": positives - tp, "tn": negatives - fp})
    none = pd.DataFrame({"threshold": [np.nextafter(1., np.inf)], "tp": [0], "fp": [0],
                         "fn": [positives], "tn": [negatives]})
    return pd.concat([none, curve], ignore_index=True)


def select_cost_threshold(y, probability, ratio):
    if not isinstance(ratio, int) or isinstance(ratio, bool) or ratio <= 0:
        raise ValueError("Cost ratio must be a positive integer")
    curve = threshold_curve(y, probability)
    costs = curve.fp + ratio * curve.fn
    # Curve is descending in threshold; first minimum gives highest threshold.
    winner = curve.loc[costs.idxmin()]
    threshold = float(winner.threshold)
    report = metrics("classification", y, probability, threshold)
    report.update(cost_ratio_fn_to_fp=ratio, illustrative_cost=int(costs.min()),
                  mean_illustrative_cost=float(costs.min() / len(y)),
                  alerts=int(report["tp"] + report["fp"]),
                  tie_break="highest threshold among equal integer costs",
                  assumption="hypothetical FP=1, FN=ratio; not measured intervention benefit")
    return threshold, report


def apply_threshold(probability, policy):
    if policy.get("kind") != "fixed_threshold" or policy.get("positive_class") != 1:
        raise ValueError("Unsupported policy or positive class")
    threshold = policy["threshold"]
    if not np.isfinite(threshold) or not 0 <= threshold <= np.nextafter(1., np.inf):
        raise ValueError("Invalid saved threshold")
    scores = np.asarray(probability, dtype=float)
    if not np.isfinite(scores).all() or ((scores < 0) | (scores > 1)).any():
        raise ValueError("Invalid scoring probability")
    return (scores >= threshold).astype(int)
