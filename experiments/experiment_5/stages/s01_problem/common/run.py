"""s01_problem/common: problem statement and pre-registration (blueprint spec/blueprints/s01_problem.md).

Writes the pre-registered layer of spec/protocol.yaml (README section 5.2) before any data is
read, plus the task contract. Every value below comes from an AGREED blueprint or decision-log
entry, named in its `source`. No Olist file is read here.
"""
from __future__ import annotations

import json
import re

import pandas as pd
import yaml

from e5lib import STAGE_ORDER, contract, protocol
from e5lib.outputs import Writer
from e5lib.paths import E5, assert_inside_e5, outputs_dir, spec_path

STAGE, TASK = "s01_problem", "common"

CITATIONS = {  # verified against their sources (s01 1.4, 1.5, 1.7; s07 7.4)
    "willmott2005": "Willmott, C. J. & Matsuura, K. (2005). Advantages of the mean absolute error (MAE) over the root mean square error (RMSE) in assessing average model performance. Climate Research 30:79-82.",
    "saito2015": "Saito, T. & Rehmsmeier, M. (2015). The precision-recall plot is more informative than the ROC plot when evaluating binary classifiers on imbalanced datasets. PLoS ONE 10(3):e0118432.",
    "brier1950": "Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. Monthly Weather Review 78:1-3.",
    "elkan2001": "Elkan, C. (2001). The foundations of cost-sensitive learning. IJCAI 2001.",
    "breiman1984": "Breiman, L., Friedman, J., Olshen, R. & Stone, C. (1984). Classification and Regression Trees.",
    "hastie2009": "Hastie, T., Tibshirani, R. & Friedman, J. (2009). The Elements of Statistical Learning, 2nd ed., section 7.10.",
    "friedman2010": "Friedman, J., Hastie, T. & Tibshirani, R. (2010). Regularization paths for generalized linear models via coordinate descent. Journal of Statistical Software 33(1).",
    "breiman2001": "Breiman, L. (2001). Random forests. Machine Learning 45:5-32.",
}

EXCLUSION_REASONS = {  # s02 removal rules (G-63); the task column of exclusions.csv says which population lost the order
    "BEFORE_DATA_START": "purchased before the data start 2017-01-01 00:00:00; the 2016 months are too thin to be representative (s02 2.8; G-72)",
    "INVALID_LEAD_TIME": "not delivered, or delivery time missing or not after purchase (s02 2.6, 2.8)",
    "ZERO_ITEMS": "order has no items (s02 2.8)",
    "CANCELLED_OR_UNAVAILABLE": "order cancelled or unavailable (s02 2.8)",
    "NO_VALID_REVIEW": "no valid review score (s02 2.8)",
    "INVALID_REVIEW_TIME": "a valid review answered at or before the purchase time, a data error (s02 2.8; G-71)",
    "LEAD_DAYS_OUTLIER": "lead_days above max(100, mean + 12 SD) of pre-cutoff orders (s02 2.9)",
    "DISTANCE_OUTLIER": "distance_km_max above 4,397.53 km (s02 2.9)",
    "MISSING_INSTALLMENTS": "payment_installments_max missing (s02 2.10)",
    "NO_USABLE_PAYMENT": "no payment rows, or only the not_defined payment type (s02 2.11)",
    "NEGATIVE_VALUE": "negative value in a log1p candidate (s02 2.13)",
}
GRID_C = [0.01, 0.1, 0.5, 1, 5, 10, 20, 50, 100]


def preregistered() -> dict:
    return {
        "version": "1.0",
        "seed": 42,
        "prediction_time": {"column": "order_purchase_timestamp", "source": "s01 1.1"},
        "tasks": {
            "regression": {
                "target": "lead_days", "unit": "days",
                "definition": "order_delivered_customer_date - order_purchase_timestamp, fractional days; delivered orders with a valid lead time > 0",
                "label_available_at": "delivery",
                "stakeholder": "logistics / fulfilment planning: expected lead time per order at checkout, to flag long-haul orders and set realistic delivery promises",
                "source": "s01 1.1-1.3; s02 2.6",
            },
            "classification": {
                "target": "is_detractor", "positive_class": 1,
                "definition": "minimum valid review score <= 2 for an eligible order (not cancelled or unavailable, and reviewed)",
                "sensitivity_label": "is_detractor_first (first review only)",
                "label_available_at": "last review answer",
                "score_meaning": "risk of a 1-2 star review if the customer reviews (scope limit)",
                "stakeholder": "customer-experience team: daily list of at-risk orders for proactive contact (status update, check with the seller)",
                "source": "s01 1.1-1.3; s02 2.6; G-34",
            },
        },
        "populations": {
            "data_start": "2017-01-01 00:00:00",
            "data_start_rule": ("orders purchased before data_start leave both tasks and never count in seller history: "
                                "the 2016 months are too thin to be representative (G-72)"),
            "both": ["orders purchased before data_start excluded (G-72)",
                     "zero-item orders excluded", "orders with missing payment_installments_max removed",
                     "orders without a usable payment removed (no payment rows, or only not_defined)",
                     "orders with a negative value in a log1p candidate removed (zero kept)"],
            "regression": "delivered orders with a valid lead time",
            "classification": "orders not cancelled or unavailable, with a valid review; targets never imputed",
            "outliers": {"lead_days_rule": "lead_days > max(100, mean + 12 * SD), mean and SD from pre-cutoff orders",
                         "lead_days_floor_days": 100, "lead_days_sd_multiplier": 12,
                         "distance_km_max_limit": 4397.53, "applies_to": "development and test (G-21, audit 2 A1 kept)"},
            "exclusions": {
                "file": "s02 exclusions.csv: order_id, task, step, reason_code, reason_description; one row per removed order and reason, every removal rule included",
                "reason_codes": EXCLUSION_REASONS,
                "rule": "one description per reason code; s02 uses only these codes",
                "source": "s02 2.6-2.11, 2.13; G-63",
            },
            "source": "s02 2.8-2.11, 2.13; G-20, G-21, G-51, G-62",
        },
        "features": {
            "contract": "e5lib/contract.py (G-61)",
            "predictors": list(contract.PREDICTORS),
            "not_in_contract": contract.NOT_IN_CONTRACT,
            "categorical": list(contract.CATEGORICAL),
            "calendar_numeric": list(contract.CALENDAR_NUMERIC),
            "counts": list(contract.COUNTS),
            "shares": list(contract.SHARES),
            "never_predictors": ["order_status", "order_approved_at", "order_delivered_carrier_date",
                                 "order_delivered_customer_date", "shipping_limit_date", "review fields",
                                 "order_estimated_delivery_date"],
            "log1p": {"skewness_threshold": 1.0, "skewness_on": "pre-cutoff development orders",
                      "candidates": list(contract.LOG_CANDIDATES),
                      "never": contract.NEVER_LOGGED,
                      "missing_values": "stay missing through log1p; imputed afterwards in the fold pipeline",
                      "negative_values": "orders removed in s02 2.13 (reason NEGATIVE_VALUE)",
                      "regression_target": True, "source": "s04 4.2; G-36, G-47, G-62"},
            "collinearity": {"abs_correlation_above": 0.9, "vif_above": 10, "decided_by": "team (human_decisions.yaml)",
                             "source": "s04 4.3; G-26"},
            "selection": {"ranking": {"regression": "absolute Spearman", "classification": "mutual information"},
                          "cumulative_threshold_options": [0.95, 0.99], "decided_by": "team after s03 (G-31)",
                          "source": "s03 3.8, s04 4.4; G-19, G-42"},
            "screening_candidates": {"columns": contract.SCREENING_CANDIDATES,
                                     "order_level_rule": "value of the primary item (highest price, then lowest "
                                                         "order_item_id), as for primary_category",
                                     "role": "screened in s03 for the named task only; enter that task's selection "
                                             "pool only if adopted at the s03 gate (human_decisions.yaml)",
                                     "assumption": "catalogue fields fixed at checkout (stated limitation)",
                                     "added_after_eda": "s03 round 1 and 2 reviews; disclosed as a post-hoc addition",
                                     "promise_note": "est_delivery_days is screened for classification only (G-35 "
                                                     "reopened for this screen); if adopted, training uses out-of-fold "
                                                     "task 1 predictions, as production would",
                                     "seller_history_rule": "events of the primary seller strictly before purchase_ts "
                                                            "(to the second), own order excluded by order_id; reviews "
                                                            "at their answer time, deliveries at delivery time",
                                     "source": "G-68, G-69"},
            "route_median": {"column": "distance_km_max",
                             "keys": [["customer_state", "primary_seller_state"], ["customer_state"]],
                             "source": "s04 4.8; G-27"},
        },
        "split": {
            "test_share": 0.20, "rule": "newest 20% of each task's eligible orders by purchase time; cutoff computed in s02",
            "test_side_customer_purge": True,
            "size_checks": {"regression": {"min_share_of_eligible_delivered": 0.15},
                            "classification": {"min_share_of_eligible_reviewed": 0.15, "min_share_of_detractors": 0.15}},
            "random_fallback": False,
            "name": "new-customer time-ordered holdout",
            "source": "s05 5.2-5.4; G-18, G-28, G-46, G-48",
        },
        "cv": {"n_folds": 5, "scheme": "expanding, time-ordered, equal-sized validation blocks by order count",
               "fold_customer_purge": "training side", "label_maturity": True,
               "data_dependent_in_s05": ["fold_boundaries", "class_support", "min_training_rows"],
               "source": "s05 5.5-5.8; G-23, G-53"},
        "metrics": {
            "regression": {"primary": "mae", "secondary": ["rmse", "r2", "within_3d"]},
            "classification": {"primary": "ap", "secondary": ["roc_auc", "brier", "precision", "recall", "f1", "confusion_matrix"],
                               "never_alone": "accuracy"},
            "charts": "precision-recall and ROC curves out-of-fold (s06 6.6) and on test (s09), with curve data",
            "citations": ["willmott2005", "saito2015", "brier1950"],
            "source": "s01 1.4; G-24",
        },
        "cost": {"fn": 5, "fp": 1, "nature": "illustrative assumption, never measured ROI",
                 "citations": ["elkan2001"], "source": "s01 1.5"},
        "families": {
            "regression": ["dummy_median", "linear", "ridge", "tree_reg", "forest_reg"],
            "classification": ["dummy_prior", "logistic", "tree_clf", "forest_clf"],
            "excluded": "boosting, voting, stacking",
            "s06_settings": {"logistic": "unregularised (C = inf), lbfgs, max_iter 5000",
                             "tree": {"max_depth": 5, "min_samples_leaf": 100},
                             "forest": {"n_estimators": 200, "max_depth": 10, "min_samples_leaf": 50, "max_features": "sqrt"}},
            "source": "s01 1.6; s06 6.2",
        },
        "decision_rule": {
            "name": "one-standard-error rule",
            "statement": "keep the simplest candidate whose fold-mean primary metric is within one standard error of the best mean; SE = fold SD / sqrt(5); ties go to the simpler",
            "simplicity_order": ["dummy", "linear/logistic", "single tree", "forest"],
            "within_family_simpler": "higher alpha, lower C, shallower depth, then larger leaf",
            "plain_vs_tuned": "the plain s06 model is kept if it is within one SE of the tuned configuration (G-55)",
            "fallback": "if no complex variant passes, the best simple model goes forward; if nothing beats the dummy, the dummy is the result",
            "s08_gate": "the rule recommends; the team confirms; an override is a logged protocol deviation (G-39, G-44)",
            "paired_differences": "reported as description only",
            "citations": ["breiman1984", "hastie2009", "friedman2010"],
            "source": "s01 1.7; G-33, G-44, G-55",
        },
        "grids": {
            "ridge_alpha": GRID_C,
            "logistic_C": GRID_C,
            "logistic_penalty": "l2",
            "tree": {"max_depth": [4, 5, 6, 8, 10, 12, 14, 16, 18], "min_samples_leaf": [20, 50, 100, 200]},
            "forest": {"max_depth": [8, 10, 12, 14, 16, 18], "min_samples_leaf": [20, 50, 100, 200],
                       "n_estimators": 200, "max_features": "sqrt"},
            "class_weight": [None, "balanced"],
            "rule": "fixed before any tuning result; no grid points added after results are seen",
            "citations": ["breiman2001"],
            "source": "s01 1.8; s07 7.1-7.4; G-37, G-43",
        },
        "calibration": {"method": "sigmoid", "always_scored": True,
                        "keep_if": "mean Brier improves and mean AP stays within one fold SE of the raw model",
                        "source": "s08 8.3; G-16, G-45, G-52"},
        "threshold": {"candidates": ["no alerts", 0.5, "1/6 (cost cutoff)", "empirical minimum of 5*FN + FP"],
                      "ties": "higher threshold (fewer alerts)", "chosen_by": "team at the s08 hard stop",
                      "default_recommendation": "minimise the illustrative cost subject to the daily alert cap",
                      "source": "s08 8.4; G-39, G-56"},
        "evaluation": {"bootstrap_resamples": 1000, "confidence": 0.95, "resample_unit": "test order (G-50, C3 rejected)",
                       "classification_slice_min_detractors": 100, "regression_slice_min_orders": 100,
                       "eda_consistency_alert": {"spearman_below": 0.5, "top10_overlap_below": 5},
                       "source": "s09 9.1-9.5; G-40, G-54"},
    }


def flatten(d: dict, prefix: str = "") -> list[tuple[str, str]]:
    rows = []
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            rows += flatten(v, key + ".")
        else:
            rows.append((key, ", ".join(map(str, v)) if isinstance(v, list) else str(v)))
    return rows


def task_contract(p: dict) -> str:
    t, m, c, d = p["tasks"], p["metrics"], p["cost"], p["decision_rule"]
    cite = lambda keys: "; ".join(CITATIONS[k] for k in keys)  # noqa: E731
    return "\n".join([
        "# Task contract (generated by s01_problem from spec/protocol.yaml)", "",
        "## Tasks and prediction time (1.1)",
        f"- Prediction time: `{p['prediction_time']['column']}` (checkout).",
        f"- Regression: `{t['regression']['target']}` ({t['regression']['unit']}): {t['regression']['definition']}.",
        f"- Classification: `{t['classification']['target']}` (positive class {t['classification']['positive_class']}): "
        f"{t['classification']['definition']}. The score means the {t['classification']['score_meaning']}.", "",
        "## Stakeholders and action (1.2)",
        f"- Regression: {t['regression']['stakeholder']}.",
        f"- Classification: {t['classification']['stakeholder']}.", "",
        "## Targets and populations (1.3)",
        f"- Both tasks: {'; '.join(p['populations']['both'])}.",
        f"- Regression: {p['populations']['regression']}. Classification: {p['populations']['classification']}.",
        f"- Label sensitivity: {t['classification']['sensitivity_label']}.", "",
        "## Metrics (1.4)",
        f"- Regression: primary {m['regression']['primary'].upper()}; also {', '.join(m['regression']['secondary'])}.",
        f"- Classification: primary {m['classification']['primary'].upper()}; also {', '.join(m['classification']['secondary'])}; "
        f"{m['classification']['never_alone']} is never reported alone.",
        f"- Charts: {m['charts']}.",
        f"- Sources: {cite(m['citations'])}", "",
        "## Cost assumption (1.5)",
        f"- FN:FP = {c['fn']}:{c['fp']}, an {c['nature']}. Source: {cite(c['citations'])}", "",
        "## Model families (1.6)",
        f"- Regression: {', '.join(p['families']['regression'])}. Classification: {', '.join(p['families']['classification'])}. "
        f"Not used: {p['families']['excluded']}.", "",
        "## Decision rule (1.7)",
        f"- {d['name']}: {d['statement']}.", f"- Simplicity order: {' < '.join(d['simplicity_order'])}; within a family: {d['within_family_simpler']}.",
        f"- {d['plain_vs_tuned']}. Fallback: {d['fallback']}. {d['s08_gate']}.",
        f"- Alert threshold: {p['threshold']['default_recommendation']}, chosen by the {p['threshold']['chosen_by']}.",
        f"- Sources: {cite(d['citations'])}", "",
        "## Search budget (1.8)",
        f"- Grids fixed in advance (see protocol.yaml `grids`); forest {p['grids']['forest']['n_estimators']} trees; seed {p['seed']}. "
        f"Source: {cite(p['grids']['citations'])}", "",
        "## Scope limits",
        "- Checkout-time information only; populations are fulfilled (regression) and reviewed (classification) orders.",
        "- The cost ratio is illustrative; no causal claims.",
    ]) + "\n"


def main() -> None:
    w = Writer(STAGE, TASK)
    p = preregistered()

    # 1.9 Outputs: write the pre-registered layer, keeping any data-dependent sections.
    path = assert_inside_e5(spec_path("protocol.yaml"))
    existing = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
    doc = {**p, **({"data_dependent": existing["data_dependent"]} if existing and "data_dependent" in existing else {})}
    header = "# Experiment 5 protocol. Pre-registered layer written by stages/s01_problem/common/run.py (README section 5.2).\n" \
             "# Data-dependent sections are written only by their owning stage (e5lib.protocol.set_data_dependent).\n"
    path.write_text(header + yaml.safe_dump(doc, sort_keys=False, allow_unicode=True, width=110), encoding="utf-8", newline="\n")
    protocol.load()  # parse back: fails loudly if the YAML is malformed

    all_ids = tuple(f"1.{i}" for i in range(1, 10))
    w.text("protocol_preregistered.yaml", yaml.safe_dump(p, sort_keys=False, allow_unicode=True, width=110), ids=all_ids)
    table = pd.DataFrame(flatten(p), columns=["key", "value"])
    id_by_prefix = {"prediction_time": "1.1", "tasks": "1.1", "populations": "1.3", "features": "1.3", "split": "1.3",
                    "cv": "1.7", "metrics": "1.4", "cost": "1.5", "families": "1.6", "decision_rule": "1.7",
                    "grids": "1.8", "calibration": "1.7", "threshold": "1.7", "evaluation": "1.4",
                    "seed": "1.8", "version": "1.9"}
    table["solution_id"] = table["key"].str.split(".").str[0].map(id_by_prefix)
    w.table("preregistered_values", table, ids=all_ids)
    w.text("task_contract.md", task_contract(p), ids=("1.1", "1.2", "1.3", "1.4", "1.5", "1.6", "1.7", "1.8"))

    # Checks (s01 section 6 and gate).
    # Pre-registration holds if every later stage that has run used this exact pre-registered layer
    # (rerun-safe: s01 may be rerun after later stages exist, e.g. after a foundation change).
    current = protocol.layer_hashes()["pre_registered"]
    used = {m.parent.parent.parent.name + "/" + m.parent.parent.name:
            json.loads(m.read_text(encoding="utf-8")).get("protocol", {}).get("pre_registered")
            for s in STAGE_ORDER[1:] for m in (E5 / "stages" / s).glob("*/outputs/_manifest.json")}
    differ = sorted(n for n, h in used.items() if h != current)
    w.check("later stages used this pre-registered layer", not differ, ids=("1.9",),
            detail=f"later nodes with outputs: {len(used)}; using a different layer: {differ or 'none'}")
    problems = contract.validate()
    w.check("contract: 24 distinct predictors, groups and log1p candidates consistent", not problems, ids=("1.3",),
            detail="; ".join(problems))
    w.check("screening candidates are task-scoped and outside the 24 predictors",
            set(contract.SCREENING_CANDIDATES) <= {"classification"} and not set(contract.all_screening()) & set(contract.PREDICTORS),
            ids=("1.3",), detail=f"{list(contract.all_screening())}")
    w.check("not-in-contract columns have a reason and are not predictors",
            set(contract.NOT_IN_CONTRACT) == {"has_items", "freight_ratio_missing", "payment_missing"}
            and not set(contract.NOT_IN_CONTRACT) & set(contract.PREDICTORS), ids=("1.3",))
    w.check("one description per exclusion reason code",
            len(EXCLUSION_REASONS) == len(set(EXCLUSION_REASONS)) and all(EXCLUSION_REASONS.values()), ids=("1.3",),
            detail=f"{len(EXCLUSION_REASONS)} codes")
    cited = set(p["metrics"]["citations"] + p["cost"]["citations"] + p["decision_rule"]["citations"] + p["grids"]["citations"])
    w.check("every citation is in the verified list", cited <= set(CITATIONS), ids=("1.4", "1.5", "1.7"),
            detail=f"{len(cited)} citations")
    s07 = (E5 / "spec" / "blueprints" / "s07_tuning.md").read_text(encoding="utf-8")
    grid_text = lambda xs: ", ".join(f"{x:g}" if isinstance(x, float) else str(x) for x in xs)  # noqa: E731
    in_blueprint = all(grid_text(g) in s07 for g in (GRID_C, p["grids"]["tree"]["max_depth"],
                                                     p["grids"]["forest"]["max_depth"], p["grids"]["tree"]["min_samples_leaf"]))
    w.check("grids match the AGREED s07 blueprint", in_blueprint, ids=("1.8",))
    index = (E5 / "spec" / "blueprints" / "README.md").read_text(encoding="utf-8")
    agreed = all(re.search(rf"\| {s[:3]} [^|]+\| \[[^\]]+\]\([^)]+\) \| AGREED", index) for s in STAGE_ORDER)
    w.check("all ten blueprints AGREED", agreed, ids=("1.9",))

    # Evidence-card text (computed from the values above).
    tk = p["tasks"]
    w.explain("1.1", done=f"Two tasks pre-registered: {tk['regression']['target']} (regression) and "
              f"{tk['classification']['target']} (classification, positive class {tk['classification']['positive_class']}), "
              f"both predicted at {p['prediction_time']['column']}.",
              conclusion="Matches s01 1.1 and G-34 (eligible-order wording and scope limit).")
    w.explain("1.2", done="Stakeholder and action recorded per task in protocol.yaml and task_contract.md.",
              conclusion=f"Regression: {tk['regression']['stakeholder']}. Classification: {tk['classification']['stakeholder']}.")
    w.explain("1.3", done=f"Populations, label rule and the predictor contract recorded from e5lib/contract.py: "
              f"{len(contract.PREDICTORS)} predictors ({len(contract.CATEGORICAL)} categorical, calendar fields numeric); "
              f"{len(contract.NOT_IN_CONTRACT)} columns listed as not in the contract with their reason; "
              f"{len(EXCLUSION_REASONS)} exclusion reason codes for s02.",
              reasoning="Round 2 applies the round 1 review: the contract is defined directly as the 24 predictors (G-61); "
                        "log1p candidates are total_price, total_freight, total_weight_g, total_volume_cm3 and "
                        "distance_km_max, while freight_ratio and counts are never logged; missing values stay missing "
                        "through log1p; orders with a negative candidate value are removed in s02 (G-62); every s02 "
                        "removal is written to exclusions.csv with a reason code and description (G-63).",
              conclusion="Feeds s02 (populations, exclusion codes, the 24 predictors to build) and s03-s04 (feature groups, "
                         "log1p candidates).")
    w.explain("1.4", done=f"Primary metrics: {p['metrics']['regression']['primary'].upper()} (regression), "
              f"{p['metrics']['classification']['primary'].upper()} (classification), with secondary metrics and charts; "
              "evaluation settings for s09 pre-registered.",
              conclusion=f"{len(p['metrics']['citations'])} verified citations in the task contract.")
    w.explain("1.5", done=f"Illustrative cost FN:FP = {p['cost']['fn']}:{p['cost']['fp']}.",
              conclusion="Stated as an assumption; drives the s08 threshold table (cost cutoff 1/6).")
    w.explain("1.6", done=f"{len(p['families']['regression'])} regression and {len(p['families']['classification'])} "
              "classification estimators, with the s06 plain settings.", conclusion="No boosting, voting or stacking.")
    w.explain("1.7", done="One-standard-error rule, simplicity order, plain-vs-tuned comparison, fallback, s08 gate, "
              "calibration keep rule and threshold candidates pre-registered.",
              conclusion="e5lib.metrics.one_se_select implements the rule; its contract tests cover the simpler-within-one-SE case.")
    w.explain("1.8", done=f"Grids fixed: tree depths {p['grids']['tree']['max_depth']}, forest depths "
              f"{p['grids']['forest']['max_depth']}, leaves {p['grids']['tree']['min_samples_leaf']}, alpha and C "
              f"{GRID_C}; forest {p['grids']['forest']['n_estimators']} trees; seed {p['seed']}.",
              conclusion="Checked against the AGREED s07 blueprint (see check).")
    w.explain("1.9", done="spec/protocol.yaml (pre-registered layer) and task_contract.md written; the values are also "
              "listed in preregistered_values.csv for review.",
              conclusion="Later stages read these values through e5lib.protocol; none hard-codes them.")

    w.finish(seed=p["seed"])


if __name__ == "__main__":
    main()
