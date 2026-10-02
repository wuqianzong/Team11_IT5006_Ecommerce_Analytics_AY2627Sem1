# Machine Learning Datasets (`data/business/ml/`)

**Status**: Layer 3B Specification (Milestones 2 & 3)  
**Applies to**: Machine learning modeling, feature engineering, and cross-validation splits.

---

## 1. Purpose & Architectural Role

This directory hosts point-in-time feature tables, target variables, and train/validation/test partitions for predictive modeling (Task 1: Delivery Lead Time Regression, and Task 2: Review Detractor Classification).

Per [`docs/data_architecture.md §4.4`](../../docs/data_architecture.md), this layer is **strictly isolated** from `data/business/dashboard/` to prevent data leakage and operational date-filtering bias.

---

## 2. Lineage Contract

```
data/preprocessed/*.csv ──> notebooks/04_ml_feature_engineering.ipynb ──> data/business/ml/orders_ml_features.csv
                                    (src/features/)
```

* **Upstream Source**: Reads exclusively from **`data/preprocessed/*.csv`** (the clean, lossless, typed baseline).
* **Prohibited Upstreams**:
  * **`data/raw/`**: ML scripts must never read directly from raw.
  * **`data/business/dashboard/`**: Contains dashboard-specific date clipping (Rule G: 2017-01 to 2018-08) and review collapsing that must not bias ML models.

---

## 3. Standard Artifacts

| Filename | Description | Required Columns / Notes |
| :--- | :--- | :--- |
| `orders_ml_features.csv` | Master consolidated feature matrix & targets | Point-in-time predictors + targets (`lead_days`, `is_detractor`, `review_score`). Grain = 1 row per order (`order_id`). |
| `train.csv` *(optional)* | Training partition | Derived via `GroupKFold` on `customer_unique_id`. |
| `test.csv` *(optional)* | Holdout test partition | Derived via `GroupKFold` on `customer_unique_id`. |

---

## 4. Mandatory Anti-Leakage Constraints (Kapoor & Narayanan, 2023)

All AI agents and contributors generating or modifying datasets in this folder must enforce:

1. **Strict Point-in-Time Cutoff**:
   Features must strictly represent information available at or before **`order_purchase_timestamp`**.
2. **Quarantined Fields**:
   * Post-purchase timestamps (`order_approved_at`, `order_delivered_carrier_date`, `order_delivered_customer_date`).
   * Actual delivery outcomes (`delivery_days`, `is_on_time`, `delivery_delay_days`).
   * Review text and review metadata (`review_comment_message`, `review_comment_title`, `review_creation_date`, `review_answer_timestamp`).
3. **Partition Independence**:
   Splits must always be grouped by **`customer_unique_id`** (never random order-level splits) to ensure repeat-purchaser behavior cannot leak across training and test partitions.
