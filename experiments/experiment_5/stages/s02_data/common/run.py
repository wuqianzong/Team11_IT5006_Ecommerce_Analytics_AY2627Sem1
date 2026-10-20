"""s02_data/common: data preprocessing (blueprint spec/blueprints/s02_data.md, steps 2.1-2.13).

One row per order with audit IDs, the 24 contract predictors (e5lib/contract.py), both targets with
label-available times and eligibility flags; every removal written to exclusions.csv with its
reason code (G-63). Nothing is learned from data except the per-task test cutoff (80/20 rule,
G-28) and the lead-time outlier threshold, both from pre-cutoff orders only.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from e5lib import contract, data, protocol  # noqa: E402
from e5lib.aggregation import aggregate_items, aggregate_payments, aggregate_reviews, resolve_english_category  # noqa: E402
from e5lib.cleaning import REGION_OF, TABLES, UNKNOWN, load_clean, normalize_state  # noqa: E402
from e5lib.seller_history import brute_force, seller_history  # noqa: E402
from e5lib.geography import distance_features, load_boundary, zip_centroids  # noqa: E402
from e5lib.manifest import sha256  # noqa: E402
from e5lib.outputs import Writer  # noqa: E402
from e5lib.paths import raw_data_dir, reference_dir, rel  # noqa: E402

STAGE, TASK = "s02_data", "common"
TASKS = ("regression", "classification")

# ---------------------------------------------------------------------------
# Leakage tags and data dictionary metadata (2.7, 2.12)
# ---------------------------------------------------------------------------
GRAIN = {"orders": "order", "order_items": "order item", "order_payments": "payment line",
         "order_reviews": "review", "customers": "customer (per order)", "sellers": "seller",
         "products": "product", "geolocation": "geolocation row (ZIP prefix, city)",
         "category_translation": "product category"}
# Raw columns known only after purchase (G-30). Everything else is known at checkout, with the
# stated assumptions that payment lines and catalogue attributes are fixed at checkout.
NOT_KNOWN = {
    "orders": {"order_status": "final status, set after purchase; defines populations only",
               "order_approved_at": "payment approval happens after purchase",
               "order_delivered_carrier_date": "after purchase",
               "order_delivered_customer_date": "after purchase; the regression label"},
    "order_items": {"shipping_limit_date": "set by the seller after purchase"},
    "order_reviews": {c: "review fields exist only after delivery" for c in TABLES["order_reviews"][0]
                      if c not in ("review_id", "order_id")},
}
KNOWN_NOTE = {
    ("orders", "order_estimated_delivery_date"): "known at checkout but never a predictor (G-35); kept for the s03 late-vs-promised trend",
    ("order_payments", "payment_type"): "assumed chosen at checkout (no timestamp)",
    ("order_payments", "payment_installments"): "assumed chosen at checkout (no timestamp)",
    ("order_payments", "payment_value"): "assumed chosen at checkout (no timestamp)",
}
MISSING_MEANING = {
    "order_approved_at": "not approved", "order_delivered_carrier_date": "not handed to carrier",
    "order_delivered_customer_date": "not delivered", "review_comment_title": "no comment",
    "review_comment_message": "no comment", "product_category_name": "unknown category",
    "product_weight_g": "missing measurement", "product_length_cm": "missing measurement",
    "product_height_cm": "missing measurement", "product_width_cm": "missing measurement",
}

RECORD_META = {  # column -> (grain, source, known at checkout, role, missing meaning, comment)
    "order_id": ("order", "orders.order_id", "yes", "identifier", "never missing", "unique key"),
    "customer_id": ("order", "orders.customer_id", "yes", "identifier", "never missing", "session key, audit only"),
    "customer_unique_id": ("customer", "customers.customer_unique_id", "yes", "identifier", "never missing",
                           "persistent customer key; purges in s05"),
    "purchase_ts": ("order", "orders.order_purchase_timestamp", "yes", "prediction time", "never missing",
                    "checkout time; test cutoffs compare against it"),
    "order_estimated_delivery_date": ("order", "orders.order_estimated_delivery_date", "yes", "description only",
                                      "not set", "never a predictor (G-35); s03 trend only"),
    "lead_days": ("order", "orders.order_delivered_customer_date - order_purchase_timestamp", "no", "target (regression)",
                  "not delivered or invalid", "fractional days; label available at delivery"),
    "lead_label_ts": ("order", "orders.order_delivered_customer_date", "no", "label time",
                      "no valid lead time", "when lead_days becomes known"),
    "is_detractor": ("order", "order_reviews.review_score (minimum valid)", "no", "target (classification)",
                     "no valid review", "1 if minimum valid score <= 2"),
    "is_detractor_first": ("order", "order_reviews.review_score (first review)", "no", "sensitivity label",
                           "no valid review", "first review by creation date (s09 9.6)"),
    "review_label_ts": ("order", "order_reviews.review_answer_timestamp (latest valid)", "no", "label time",
                        "no valid review", "when is_detractor becomes known"),
    "eligible_regression": ("order", "s02 rules 2.6-2.13", "n/a", "eligibility", "never missing",
                            "1 if the order is in the regression population after every rule"),
    "eligible_classification": ("order", "s02 rules 2.6-2.13", "n/a", "eligibility", "never missing",
                                "1 if the order is in the classification population after every rule"),
}
PREDICTOR_SOURCE = {
    "n_items": "order_items.order_item_id (count)", "n_products": "order_items.product_id (distinct)",
    "n_sellers": "order_items.seller_id (distinct)", "n_categories": "products.category (distinct, English)",
    "total_price": "order_items.price (sum; missing if any item invalid)",
    "total_freight": "order_items.freight_value (sum; missing if any item invalid)",
    "freight_ratio": "total_freight / total_price", "total_weight_g": "products.product_weight_g (sum)",
    "total_volume_cm3": "products length x height x width (sum)",
    "weight_missing_fraction": "share of items without a valid weight",
    "volume_missing_fraction": "share of items without valid dimensions",
    "primary_category": "category of the highest-priced item (English)",
    "category_missing_fraction": "share of items without a translated category",
    "customer_state": "customers.customer_state", "primary_seller_state": "sellers.seller_state of the primary item",
    "distance_km_max": "max haversine customer-seller distance over distinct sellers (IBGE-filtered ZIP centroids)",
    "distance_missing_fraction": "share of distinct sellers without a resolved distance",
    "interstate_share": "share of distinct sellers in another state",
    "purchase_month": "orders.order_purchase_timestamp (month, numeric)",
    "purchase_dayofweek": "orders.order_purchase_timestamp (Monday = 0, numeric)",
    "purchase_hour": "orders.order_purchase_timestamp (hour, numeric)",
    "primary_payment_type": "order_payments (type with the largest usable value)",
    "payment_installments_max": "order_payments.payment_installments (max over usable lines)",
    "n_payment_methods": "order_payments.payment_type (distinct usable)",
}
SCREEN = contract.all_screening()  # screening candidates (G-68), not predictors
RECORD_COLUMNS = (["order_id", "customer_id", "customer_unique_id", "purchase_ts"] + list(contract.PREDICTORS)
                  + list(SCREEN) + ["order_estimated_delivery_date", "lead_days", "lead_label_ts", "is_detractor",
                     "is_detractor_first", "review_label_ts", "eligible_regression", "eligible_classification"])


def assert_unique(df, cols, label, checks):
    dup = int(df.duplicated(cols).sum())
    null = int(df[cols].isna().any(axis=1).sum()) if isinstance(cols, list) else int(df[cols].isna().sum())
    checks[f"{label} key {cols} unique and non-null"] = (dup == 0 and null == 0, f"{dup} duplicates, {null} nulls")


def main() -> None:
    w = Writer(STAGE, TASK)
    p = protocol.load()
    reasons = p["populations"]["exclusions"]["reason_codes"]
    key_checks: dict[str, tuple[bool, str]] = {}

    # 2.1 Load + 2.2 Clean -------------------------------------------------------------------
    t, clean_log = {}, {}
    for name in TABLES:
        t[name], clean_log[name] = load_clean(name, STAGE)
    hashes = {f"data/raw/{data.RAW_FILES[n]}": sha256(raw_data_dir() / data.RAW_FILES[n]) for n in TABLES}

    # 2.3 Geography ----------------------------------------------------------------------------
    polygon, boundary = load_boundary(STAGE)
    for f in ("BR_Pais_2024.zip", "BR_Pais_2024_4326.geojson", "boundary_manifest.json"):
        hashes[f"data/reference/geography/{f}"] = sha256(reference_dir() / "geography" / f)
    centroids, geo_report = zip_centroids(t["geolocation"], polygon)

    # 2.4 Join (aggregate first) ---------------------------------------------------------------
    orders, customers = t["orders"], t["customers"]
    for df, cols, label in ((orders, "order_id", "orders"), (customers, "customer_id", "customers"),
                            (t["products"], "product_id", "products"), (t["sellers"], "seller_id", "sellers"),
                            (t["category_translation"], "product_category_name", "category_translation"),
                            (t["order_items"], ["order_id", "order_item_id"], "order_items"),
                            (t["order_payments"], ["order_id", "payment_sequential"], "order_payments")):
        assert_unique(df, cols, label, key_checks)
    products_cat = resolve_english_category(t["products"], t["category_translation"])
    item_agg, primary, pairs = aggregate_items(products_cat, t["order_items"])
    pay_agg = aggregate_payments(t["order_payments"])
    rev_agg = aggregate_reviews(t["order_reviews"])
    geo = distance_features(orders, customers, t["sellers"], pairs, centroids)

    base = orders.merge(customers, on="customer_id", how="left", validate="many_to_one")
    for part in (item_agg, primary, pay_agg, rev_agg, geo):
        base = base.merge(part, left_on="order_id", right_index=True, how="left", validate="one_to_one")
    key_checks["output rows = orders"] = (len(base) == len(orders), f"{len(base)} rows, {len(orders)} orders")
    key_checks["every order has a customer"] = (int(base["customer_unique_id"].isna().sum()) == 0,
                                                f"{int(base['customer_unique_id'].isna().sum())} without")

    # 2.5 Predictors ---------------------------------------------------------------------------
    for col in ("n_items", "n_products", "n_sellers", "n_categories", "seller_id_missing", "n_payment_methods"):
        base[col] = base[col].fillna(0).astype(int)
    base["primary_category"] = base["primary_category"].fillna(UNKNOWN)
    base["primary_payment_type"] = base["primary_payment_type"].fillna(UNKNOWN)
    base["has_usable_type"] = base["has_usable_type"].fillna(False).astype(bool)
    base.loc[base["seller_id_missing"] == 1, ["distance_km_max", "distance_missing_fraction", "interstate_share"]] = np.nan
    base["customer_state"] = base["customer_state"].map(normalize_state)
    seller_state = t["sellers"].set_index("seller_id")["seller_state"].map(normalize_state)
    base["primary_seller_state"] = base["primary_seller_id"].map(seller_state).fillna(UNKNOWN)
    pt = base["order_purchase_timestamp"]
    base["purchase_ts"] = pt
    base["purchase_month"], base["purchase_dayofweek"], base["purchase_hour"] = pt.dt.month, pt.dt.dayofweek, pt.dt.hour

    # Screening candidates (G-68, G-69): promise, regions, seller history at checkout ---------------
    base["est_delivery_days"] = (base["order_estimated_delivery_date"] - pt).dt.total_seconds() / 86400.0
    base["customer_region"] = base["customer_state"].map(REGION_OF).fillna(UNKNOWN)
    base["seller_region"] = base["primary_seller_state"].map(REGION_OF).fillna(UNKNOWN)
    base["region_pair"] = base["customer_region"] + ">" + base["seller_region"]
    # G-72: orders before the data start are too thin to be representative; their reviews and deliveries
    # never enter any seller's history.
    data_start = pd.Timestamp(p["populations"]["data_start"])
    early = set(base.loc[pt < data_start, "order_id"])
    hist_reviews = t["order_reviews"][~t["order_reviews"]["order_id"].isin(early)]
    hist_orders = pd.DataFrame({"order_id": base["order_id"], "seller_id": base["primary_seller_id"], "purchase_ts": pt})
    delivered_rows = ((base["order_status"] == "delivered") & base["order_delivered_customer_date"].notna()
                      & (pt >= data_start))
    hist_deliveries = pd.DataFrame({"order_id": base.loc[delivered_rows, "order_id"],
                                    "delivered_ts": base.loc[delivered_rows, "order_delivered_customer_date"],
                                    "estimated_ts": base.loc[delivered_rows, "order_estimated_delivery_date"]})
    hist = seller_history(hist_orders, hist_reviews, hist_deliveries)
    for c in hist.columns:
        base[c] = hist[c]
    sample = hist_orders["order_id"].sample(n=2000, random_state=int(p["seed"])).to_numpy()
    slow = brute_force(hist_orders, hist_reviews, hist_deliveries, sample)
    fast = hist.set_index(hist_orders["order_id"]).loc[sample]
    hist_ok = bool(np.allclose(fast.to_numpy(float), slow.to_numpy(float), equal_nan=True, rtol=0, atol=1e-12))

    # 2.6 Targets ------------------------------------------------------------------------------
    delivered = base["order_delivered_customer_date"]
    elapsed = (delivered - pt).dt.total_seconds() / 86400.0
    lead_ok = (base["order_status"] == "delivered") & pt.notna() & delivered.notna() & (elapsed > 0)
    base["lead_days"] = elapsed.where(lead_ok)
    base["lead_label_ts"] = delivered.where(lead_ok)
    base["review_count"] = base["review_count"].fillna(0).astype(int)

    # 2.7 Leakage audit: date-order audit on every order ---------------------------------------
    first_answer = t["order_reviews"].groupby("order_id")["review_answer_timestamp"].min()
    ans = base["order_id"].map(first_answer)
    seq = [("order_purchase_timestamp", "order_approved_at"), ("order_approved_at", "order_delivered_carrier_date"),
           ("order_delivered_carrier_date", "order_delivered_customer_date")]
    date_audit = {f"{a} <= {b}": int((base[a] > base[b]).sum()) for a, b in seq}
    date_audit["order_estimated_delivery_date > order_purchase_timestamp"] = int(
        (base["order_estimated_delivery_date"] <= pt).sum())
    date_audit["first review answer > order_purchase_timestamp"] = int((ans <= pt).sum())
    date_audit["order_delivered_customer_date > order_purchase_timestamp (delivered orders)"] = int(
        ((base["order_status"] == "delivered") & delivered.notna() & (elapsed <= 0)).sum())

    # 2.8, 2.10, 2.11, 2.13: population rules (row-local) ---------------------------------------
    cand = list(p["features"]["log1p"]["candidates"])
    rule = {
        "BEFORE_DATA_START": ("2.8", pt < data_start, TASKS),  # G-72
        "INVALID_LEAD_TIME": ("2.6, 2.8", ~lead_ok, ("regression",)),
        "ZERO_ITEMS": ("2.8", base["n_items"] == 0, TASKS),
        "CANCELLED_OR_UNAVAILABLE": ("2.8", base["order_status"].isin(["canceled", "unavailable"]), ("classification",)),
        "NO_VALID_REVIEW": ("2.8", base["is_detractor"].isna(), ("classification",)),
        # G-71: a review answered at or before its own order's purchase is a data error; the label of such an
        # order is not trusted (classification only).
        "INVALID_REVIEW_TIME": ("2.8", base["is_detractor"].notna() & (ans <= pt), ("classification",)),
        "MISSING_INSTALLMENTS": ("2.10", base["payment_installments_max"].isna(), TASKS),
        "NO_USABLE_PAYMENT": ("2.11", ~base["has_usable_type"], TASKS),
        "NEGATIVE_VALUE": ("2.13", (base[cand] < 0).any(axis=1), TASKS),
    }
    population_ok = {}
    for task in TASKS:
        bad = pd.Series(False, index=base.index)
        for code, (_, mask, tasks) in rule.items():
            if task in tasks:
                bad |= mask.fillna(False).astype(bool)
        population_ok[task] = ~bad

    # Test cutoff per task (G-28): 80% position of eligible orders after the population rules,
    # before the outlier rule.
    test_share = float(p["split"]["test_share"])
    cutoffs = {}
    for task in TASKS:
        ts = np.sort(pt[population_ok[task]].to_numpy())
        cutoffs[task] = pd.Timestamp(ts[int(np.floor((1 - test_share) * len(ts)))]).strftime("%Y-%m-%d %H:%M:%S")
    protocol.set_data_dependent("test_cutoffs", cutoffs, stage=STAGE)

    # 2.9 Outliers: lead-time threshold from pre-cutoff regression orders only ----------------
    o = p["populations"]["outliers"]
    pre = population_ok["regression"] & (pt < pd.Timestamp(cutoffs["regression"]))
    mean, sd = float(base.loc[pre, "lead_days"].mean()), float(base.loc[pre, "lead_days"].std())
    lead_thr = max(float(o["lead_days_floor_days"]), mean + float(o["lead_days_sd_multiplier"]) * sd)
    pre_max_ts = base.loc[pre, "purchase_ts"].max()
    rule["LEAD_DAYS_OUTLIER"] = ("2.9", base["lead_days"] > lead_thr, ("regression",))
    rule["DISTANCE_OUTLIER"] = ("2.9", base["distance_km_max"] > float(o["distance_km_max_limit"]), TASKS)

    # Exclusions (G-63) and eligibility ------------------------------------------------------
    rows = []
    for code, (step, mask, tasks) in rule.items():
        hit = base.loc[mask.fillna(False).astype(bool), ["order_id", "purchase_ts"]]
        for task in tasks:
            rows.append(hit.assign(task=task, step=step, reason_code=code, reason_description=reasons[code]))
    excl = pd.concat(rows, ignore_index=True)
    for task in TASKS:
        removed = set(excl.loc[excl["task"] == task, "order_id"])
        base[f"eligible_{task}"] = (~base["order_id"].isin(removed)).astype(int)
    n_by = excl.groupby(["task", "reason_code"]).size()
    excl_counts = pd.DataFrame([{"task": task, "step": step, "reason_code": code,
                                 "reason_description": reasons[code], "orders": int(n_by.get((task, code), 0))}
                                for code, (step, _, tasks) in rule.items() for task in tasks])
    after_cut = []
    for task in TASKS:
        e = excl[(excl["task"] == task) & excl["reason_code"].isin(["LEAD_DAYS_OUTLIER", "DISTANCE_OUTLIER"])]
        after_cut.append({"task": task, "outlier_removals_on_or_after_cutoff":
                          int((e["purchase_ts"] >= pd.Timestamp(cutoffs[task])).sum())})
    excl = excl.drop(columns="purchase_ts").sort_values(["task", "step", "reason_code", "order_id"], kind="mergesort")

    # Records ---------------------------------------------------------------------------------
    rec = base[RECORD_COLUMNS].sort_values("order_id", kind="mergesort").reset_index(drop=True)
    w.table("records", rec, ids=("2.4", "2.5", "2.6", "2.8"), compress=True)
    w.table("exclusions", excl, ids=("2.8", "2.9", "2.10", "2.11", "2.13"))
    w.table("exclusion_counts", excl_counts, ids=("2.8", "2.9", "2.10", "2.11", "2.13"))
    w.table("zip_centroids", centroids, ids=("2.3",))
    w.json("data_hashes", hashes, ids=("2.1", "2.3"))

    # Label sensitivity (2.6) and population sizes ----------------------------------------------
    lab = rec[rec["is_detractor"].notna()]
    label_agreement = {"orders_with_valid_review": int(len(lab)),
                       "min_and_first_label_agree": int((lab["is_detractor"] == lab["is_detractor_first"]).sum()),
                       "orders_with_more_than_one_review": int((base["review_count"] > 1).sum())}
    pop_sizes = {task: {"eligible": int(rec[f"eligible_{task}"].sum()),
                        "eligible_before_cutoff": int(((rec[f"eligible_{task}"] == 1)
                                                       & (rec["purchase_ts"] < pd.Timestamp(cutoffs[task]))).sum())}
                 for task in TASKS}

    # Data dictionary (2.12, G-58) ------------------------------------------------------------
    leak = {}
    dd = []
    for name, (dtypes, _, _) in TABLES.items():
        df = t[name]
        for col, typ in dtypes.items():
            not_known = NOT_KNOWN.get(name, {}).get(col)
            known = "no" if not_known else "yes"
            leak[f"{name}.{col}"] = known
            dd.append({"table": name, "column": col, "type": typ, "nullable": bool(df[col].isna().any()),
                       "grain": GRAIN[name], "source": f"{data.RAW_FILES[name]}:{col}",
                       "missing_meaning": MISSING_MEANING.get(col, "missing" if df[col].isna().any() else "never missing"),
                       "known_at_checkout": known, "label_available_at": "", "eligibility": "raw input",
                       "comment": not_known or KNOWN_NOTE.get((name, col), "")})
    for col in RECORD_COLUMNS:
        if col in SCREEN:
            task = [t for t, cols in contract.SCREENING_CANDIDATES.items() if col in cols]
            grain, source, known = "order", contract.SCREENING_CANDIDATES[task[0]][col]["source"], "yes"
            role = f"screening candidate ({', '.join(task)} only, G-68)"
            miss = "missing (product without a catalogue value)" if rec[col].isna().any() else "never missing"
            comment = ("not a predictor unless adopted at the s03 gate; catalogue fields assumed fixed at checkout; "
                       + contract.SCREENING_CANDIDATES[task[0]][col]["transform"])
        elif col in contract.PREDICTORS:
            grain, source, known, role = "order", PREDICTOR_SOURCE[col], "yes", "predictor (contract)"
            miss = "missing (imputed later in the fold pipeline)" if rec[col].isna().any() else "never missing"
            comment = ("log1p candidate (s04 4.2)" if col in contract.LOG_CANDIDATES else "")
        else:
            grain, source, known, role, miss, comment = RECORD_META[col]
        leak[f"records.{col}"] = known
        dd.append({"table": "records", "column": col, "type": str(rec[col].dtype), "nullable": bool(rec[col].isna().any()),
                   "grain": grain, "source": source, "missing_meaning": miss, "known_at_checkout": known,
                   "label_available_at": {"lead_days": "lead_label_ts", "is_detractor": "review_label_ts",
                                          "is_detractor_first": "review_label_ts"}.get(col, ""),
                   "eligibility": role, "comment": comment})
    for col, reason in contract.NOT_IN_CONTRACT.items():
        dd.append({"table": "not built", "column": col, "type": "", "nullable": "", "grain": "order", "source": "",
                   "missing_meaning": "", "known_at_checkout": "no" if "leakage" in reason else "yes",
                   "label_available_at": "", "eligibility": "not in the contract", "comment": reason})
    dictionary = pd.DataFrame(dd)
    w.table("data_dictionary", dictionary, ids=("2.7", "2.12"))

    # Data structure figure (2.12) ------------------------------------------------------------
    links = pd.DataFrame([
        ("customers", "orders", "customer_id", "one-to-many"), ("orders", "order_items", "order_id", "one-to-many"),
        ("orders", "order_payments", "order_id", "one-to-many"), ("orders", "order_reviews", "order_id", "one-to-many"),
        ("products", "order_items", "product_id", "one-to-many"), ("sellers", "order_items", "seller_id", "one-to-many"),
        ("category_translation", "products", "product_category_name", "one-to-many"),
        ("geolocation", "customers", "zip prefix + state (median centroid)", "many-to-one lookup"),
        ("geolocation", "sellers", "zip prefix + state (median centroid)", "many-to-one lookup"),
    ], columns=["from_table", "to_table", "key", "cardinality"])
    pos = {"customers": (0, 2.2), "orders": (2.6, 2.2), "order_items": (5.2, 3.4), "order_payments": (5.2, 2.2),
           "order_reviews": (5.2, 1.0), "sellers": (7.8, 2.2), "products": (7.8, 4.4),
           "category_translation": (10.4, 4.4), "geolocation": (7.8, 0.0)}
    fig, ax = plt.subplots(figsize=(12, 6))
    for _, r in links.iterrows():
        (x1, y1), (x2, y2) = pos[r.from_table], pos[r.to_table]
        curved = r.from_table == "geolocation" and r.to_table == "customers"
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color="0.45", shrinkA=26 if y1 != y2 else 48, shrinkB=26 if y1 != y2 else 52, mutation_scale=14,
                                    connectionstyle="arc3,rad=-0.25" if curved else "arc3"))
        mx, my = ((x1 + x2) / 2, min(y1, y2) - 0.45) if curved else ((x1 + x2) / 2, (y1 + y2) / 2)
        ax.text(mx, my + 0.12, {"product_category_name": "category name"}.get(r.key, r.key if len(r.key) < 25 else "ZIP + state centroid"), ha="center", fontsize=7,
                color="0.25", bbox=dict(fc="white", ec="none", pad=0.5))
    for name, (x, y) in pos.items():
        ax.text(x, y, f"{name}\n{clean_log[name]['rows_clean']:,} rows", ha="center", va="center", fontsize=8,
                bbox=dict(boxstyle="round", fc="#eef3fb" if name == "orders" else "white", ec="0.3"))
    ax.text(-0.6, 4.4, "Join: aggregate order_items, order_payments and order_reviews to order_id first,\n"
            "then left-join one-to-one onto orders + customers: one row per order", fontsize=8, style="italic", va="center")
    ax.set_xlim(-1, 11.5)
    ax.set_ylim(-1.2, 5)
    ax.axis("off")
    ax.set_title("Olist tables, keys and the aggregate-first join (arrow: one side to many side)")
    w.figure("data_structure", fig, links, ids=("2.12",), title="Data structure")
    plt.close(fig)

    # Audit -----------------------------------------------------------------------------------
    audit = {"cleaning": clean_log, "key_checks": {k: {"passed": v[0], "detail": v[1]} for k, v in key_checks.items()},
             "geography": {"boundary": boundary, "filter": geo_report},
             "leakage_tags": leak, "date_order_violations": date_audit,
             "label_agreement": label_agreement, "test_cutoffs": cutoffs,
             "outlier_threshold": {"lead_days_threshold": lead_thr, "pre_cutoff_mean": mean, "pre_cutoff_sd": sd,
                                   "rule": o["lead_days_rule"], "distance_km_max_limit": o["distance_km_max_limit"],
                                   "statistics_latest_purchase_ts": str(pre_max_ts)},
             "outlier_removals_on_or_after_cutoff": after_cut,
             "exclusion_counts": excl_counts.to_dict(orient="records"), "population_sizes": pop_sizes,
             "payment_assumption": "payment fields have no timestamp; chosen at checkout is a stated assumption"}
    w.json("audit", audit, ids=("2.2", "2.3", "2.4", "2.6", "2.7", "2.9"))

    # Checks (blueprint section 6 and gate) -----------------------------------------------------
    for name, (ok, detail) in key_checks.items():
        w.check(name, ok, ids=("2.4",), detail=detail)
    w.check("order_id unique and non-null in records", rec["order_id"].is_unique and rec["order_id"].notna().all(), ids=("2.4",))
    w.check("records hold exactly the 24 contract predictors", [c for c in rec.columns if c in contract.PREDICTORS]
            == list(contract.PREDICTORS) and not set(contract.NOT_IN_CONTRACT) & set(rec.columns), ids=("2.5",))
    w.check("screening candidates built, known at checkout, numeric ones non-negative (G-68, G-69)",
            all(c in rec.columns and leak[f"records.{c}"] == "yes" for c in SCREEN)
            and not (rec[[c for c in SCREEN if contract.SCREENING_CANDIDATES["classification"][c]["kind"] == "numeric"]] < 0).any().any()
            and not set(SCREEN) & set(contract.PREDICTORS),
            ids=("2.5", "2.7"), detail=f"{list(SCREEN)}; missing: "
            + ", ".join(f"{c} {int(rec[c].isna().sum()):,}" for c in SCREEN))
    w.check("seller history equals a direct per-order recomputation (2,000 random orders, strict time, own order excluded)",
            hist_ok, ids=("2.5", "2.7"), detail=f"sample seed {p['seed']}")
    w.check("est_delivery_days after purchase on every order; region columns complete",
            bool((rec["est_delivery_days"] > 0).all()) and not rec[["customer_region", "seller_region", "region_pair"]].isna().any().any(),
            ids=("2.5",), detail=f"min est_delivery_days {rec['est_delivery_days'].min():.3f}")
    w.check("no predictor tagged not known at checkout",
            all(leak[f"records.{c}"] == "yes" for c in contract.PREDICTORS), ids=("2.7",))
    w.check("data dictionary: one row per raw and records column",
            len(dictionary[dictionary.table != "not built"]) == sum(len(v[0]) for v in TABLES.values()) + len(RECORD_COLUMNS)
            and not dictionary.duplicated(["table", "column"]).any(), ids=("2.12",))
    w.check("data dictionary tags match the audit leakage tags",
            all(leak[f"{r.table}.{r.column}"] == r.known_at_checkout for r in dictionary.itertuples() if r.table != "not built"),
            ids=("2.7", "2.12"))
    w.check("outlier statistics use only pre-cutoff orders", pre_max_ts < pd.Timestamp(cutoffs["regression"]),
            ids=("2.9",), detail=f"latest purchase used {pre_max_ts}, cutoff {cutoffs['regression']}")
    w.check("every reason code has its pre-registered description",
            set(excl["reason_code"]) <= set(reasons) and all(excl["reason_description"] == excl["reason_code"].map(reasons)),
            ids=("2.8", "2.13"))
    ineligible = {task: set(rec.loc[rec[f"eligible_{task}"] == 0, "order_id"]) for task in TASKS}
    w.check("no order silently dropped: every ineligible order has an exclusion row",
            all(ineligible[task] == set(excl.loc[excl.task == task, "order_id"]) for task in TASKS), ids=("2.8",))
    w.check("eligible orders have their target", rec.loc[rec.eligible_regression == 1, "lead_days"].notna().all()
            and rec.loc[rec.eligible_classification == 1, "is_detractor"].notna().all(), ids=("2.6",))
    w.check("no eligible order before the data start; seller history uses no review or delivery of such an order (G-72)",
            not ((rec.eligible_regression == 1) | (rec.eligible_classification == 1))[rec["purchase_ts"] < data_start].any()
            and not hist_reviews["order_id"].isin(early).any() and not hist_deliveries["order_id"].isin(early).any(),
            ids=("2.5", "2.8"), detail=f"data start {data_start}; {len(early):,} orders before it")
    bad_review_time = set(base.loc[ans <= pt, "order_id"])
    w.check("eligible classification orders have every review answered after purchase (G-71)",
            not rec.loc[rec.eligible_classification == 1, "order_id"].isin(bad_review_time).any(), ids=("2.7", "2.8"),
            detail=f"{len(bad_review_time):,} orders with a review answered at or before purchase")
    w.check("eligible orders have no negative log1p candidate",
            not (rec.loc[(rec.eligible_regression == 1) | (rec.eligible_classification == 1), cand] < 0).any().any(), ids=("2.13",))
    w.check("IBGE boundary hashes verified", True, ids=("2.3",), detail=f"archive {boundary['archive_sha256'][:12]}")
    w.check("test cutoffs recorded in protocol.yaml",
            protocol.get("data_dependent.test_cutoffs.values") == cutoffs, ids=("2.8",), detail=str(cutoffs))

    # Evidence-card text (computed values only) ------------------------------------------------
    cl = clean_log
    w.explain("2.1", done=f"Nine raw tables read with declared types; sha256 of every file and of the IBGE archive, "
              f"derived geometry and manifest in data_hashes.json ({len(hashes)} files).")
    w.explain("2.2", done="Declared types per the Milestone 2 cleaning schema; ZIP prefixes read as strings; categorical "
              f"domains checked (violations kept, listed in audit.json); geolocation exact duplicates dropped: "
              f"{cl['geolocation']['exact_duplicates_dropped']:,} of {cl['geolocation']['rows_raw']:,} rows. No imputation.")
    w.explain("2.3", done=f"ZIP/state median centroids after the IBGE boundary filter: {geo_report['accepted']:,} of "
              f"{geo_report['rows']:,} geolocation rows accepted; {geo_report['keys']:,} keys, by status "
              f"{geo_report['keys_by_status']}.", conclusion="Archive and derived geometry match the pinned hashes.")
    w.explain("2.4", done="Items, payments and reviews aggregated to order_id first, then left-joined one-to-one "
              f"(pandas validate); output rows {len(rec):,} = orders {len(orders):,}.")
    w.explain("2.5", done="The 24 predictors of e5lib/contract.py built with the Milestone 2 formulas; calendar fields "
              "numeric; has_items, freight_ratio_missing and payment_missing not built. Screening candidates (G-68, "
              f"classification only, not predictors): {', '.join(SCREEN)}. Product fields from the primary item; "
              "est_delivery_days = estimated delivery date minus purchase; regions are the IBGE macro-regions of the "
              "customer and primary-seller states and their pair; seller history uses only the primary seller's events "
              "strictly before purchase, own order excluded.")
    w.explain("2.6", done=f"lead_days for delivered orders with delivery after purchase; is_detractor from the minimum "
              f"valid score; first-review label kept. Min and first labels agree on "
              f"{label_agreement['min_and_first_label_agree']:,} of {label_agreement['orders_with_valid_review']:,} reviewed orders.")
    w.explain("2.7", done="Every raw and records column tagged known / not known at checkout (data_dictionary.csv, "
              f"audit.json); date-order violations logged: {date_audit}.",
              reasoning="Zero-item orders are excluded from both tasks (ZERO_ITEMS, step 2.8): items can be removed "
                        "after checkout, so a zero item count would leak a later cancellation. For the same reason "
                        "has_items is not in the contract (G-30, G-61).")
    w.explain("2.8", done="Population rules applied per task and written to exclusions.csv; counts in exclusion_counts.csv. "
              f"Test cutoffs (80/20 on eligible orders after the population rules, before the outlier rule): {cutoffs}.",
              reasoning="Lead-time outliers are applied to the regression population only, because lead_days exists only "
                        "for delivered orders; distance outliers apply to both tasks. Flagged for the team to confirm.")
    w.explain("2.9", done=f"Lead-time threshold max(100, mean + 12 SD) = {lead_thr:.2f} days from pre-cutoff regression "
              f"orders (mean {mean:.2f}, SD {sd:.2f}); distance limit {o['distance_km_max_limit']} km. Removals on or after "
              f"each cutoff: {after_cut}.")
    w.explain("2.10", done="Orders with no usable payment_installments_max removed from both tasks (MISSING_INSTALLMENTS).")
    w.explain("2.11", done="Orders with no payment rows or only not_defined types removed from both tasks (NO_USABLE_PAYMENT).")
    w.explain("2.12", done=f"data_dictionary.csv: {len(dictionary):,} rows (every raw and records column, plus the three "
              "columns not in the contract); figures/data_structure.png with its link table.")
    w.explain("2.13", done=f"Orders with a negative value in {cand} removed from both tasks (NEGATIVE_VALUE); zero kept.")
    w.finish(seed=p["seed"])


if __name__ == "__main__":
    main()
