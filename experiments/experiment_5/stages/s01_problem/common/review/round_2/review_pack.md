# Review pack: s01_problem/common, round 2

| Field | Value |
| --- | --- |
| Run ID | `20261018T150315Z` |
| Base commit | `0e8741832f5722ba94d42d5bc6d3f159c6f4be68` plus uncommitted changes (committed at acceptance) |
| Outputs | FRESH |
| Coverage | 9 implemented, 0 deviation, 0 missing |
| Failed checks | 0 |
| Ready for acceptance | yes |

## Coverage

| ID | Solution step | Coverage | Checks | Changed since last round | Evidence |
| --- | --- | --- | --- | --- | --- |
| [1.1](#card-1-1) | Tasks and prediction time | IMPLEMENTED | — | yes | [protocol_preregistered.yaml](../../outputs/protocol_preregistered.yaml), [preregistered_values.csv](../../outputs/preregistered_values.csv), [task_contract.md](../../outputs/task_contract.md) |
| [1.2](#card-1-2) | Stakeholders and action | IMPLEMENTED | — | yes | [protocol_preregistered.yaml](../../outputs/protocol_preregistered.yaml), [preregistered_values.csv](../../outputs/preregistered_values.csv), [task_contract.md](../../outputs/task_contract.md) |
| [1.3](#card-1-3) | Targets and populations | IMPLEMENTED | PASS | yes | [protocol_preregistered.yaml](../../outputs/protocol_preregistered.yaml), [preregistered_values.csv](../../outputs/preregistered_values.csv), [task_contract.md](../../outputs/task_contract.md) |
| [1.4](#card-1-4) | Metrics | IMPLEMENTED | PASS | yes | [protocol_preregistered.yaml](../../outputs/protocol_preregistered.yaml), [preregistered_values.csv](../../outputs/preregistered_values.csv), [task_contract.md](../../outputs/task_contract.md) |
| [1.5](#card-1-5) | Cost assumption | IMPLEMENTED | PASS | yes | [protocol_preregistered.yaml](../../outputs/protocol_preregistered.yaml), [preregistered_values.csv](../../outputs/preregistered_values.csv), [task_contract.md](../../outputs/task_contract.md) |
| [1.6](#card-1-6) | Model families | IMPLEMENTED | — | yes | [protocol_preregistered.yaml](../../outputs/protocol_preregistered.yaml), [preregistered_values.csv](../../outputs/preregistered_values.csv), [task_contract.md](../../outputs/task_contract.md) |
| [1.7](#card-1-7) | Decision rule | IMPLEMENTED | PASS | yes | [protocol_preregistered.yaml](../../outputs/protocol_preregistered.yaml), [preregistered_values.csv](../../outputs/preregistered_values.csv), [task_contract.md](../../outputs/task_contract.md) |
| [1.8](#card-1-8) | Search budget | IMPLEMENTED | PASS | yes | [protocol_preregistered.yaml](../../outputs/protocol_preregistered.yaml), [preregistered_values.csv](../../outputs/preregistered_values.csv), [task_contract.md](../../outputs/task_contract.md) |
| [1.9](#card-1-9) | Outputs | IMPLEMENTED | PASS | yes | [protocol_preregistered.yaml](../../outputs/protocol_preregistered.yaml), [preregistered_values.csv](../../outputs/preregistered_values.csv) |

## Evidence cards

### 1.1 Tasks and prediction time {#card-1-1}

Coverage: **IMPLEMENTED**; checks: **—**.

- **What was done:** Two tasks pre-registered: lead_days (regression) and is_detractor (classification, positive class 1), both predicted at order_purchase_timestamp.
- **Conclusion:** Matches s01 1.1 and G-34 (eligible-order wording and scope limit).
- **Claim type:** observation
- **Files:** [protocol_preregistered.yaml](../../outputs/protocol_preregistered.yaml), [preregistered_values.csv](../../outputs/preregistered_values.csv), [task_contract.md](../../outputs/task_contract.md)

### 1.2 Stakeholders and action {#card-1-2}

Coverage: **IMPLEMENTED**; checks: **—**.

- **What was done:** Stakeholder and action recorded per task in protocol.yaml and task_contract.md.
- **Conclusion:** Regression: logistics / fulfilment planning: expected lead time per order at checkout, to flag long-haul orders and set realistic delivery promises. Classification: customer-experience team: daily list of at-risk orders for proactive contact (status update, check with the seller).
- **Claim type:** observation
- **Files:** [protocol_preregistered.yaml](../../outputs/protocol_preregistered.yaml), [preregistered_values.csv](../../outputs/preregistered_values.csv), [task_contract.md](../../outputs/task_contract.md)

### 1.3 Targets and populations {#card-1-3}

Coverage: **IMPLEMENTED**; checks: **PASS**.

- **What was done:** Populations, label rule and the predictor contract recorded from e5lib/contract.py: 24 predictors (4 categorical, calendar fields numeric); 3 columns listed as not in the contract with their reason; 9 exclusion reason codes for s02.
- **Reasoning:** Round 2 applies the round 1 review: the contract is defined directly as the 24 predictors (G-61); log1p candidates are total_price, total_freight, total_weight_g, total_volume_cm3 and distance_km_max, while freight_ratio and counts are never logged; missing values stay missing through log1p; orders with a negative candidate value are removed in s02 (G-62); every s02 removal is written to exclusions.csv with a reason code and description (G-63).
- **Conclusion:** Feeds s02 (populations, exclusion codes, the 24 predictors to build) and s03-s04 (feature groups, log1p candidates).
- **Claim type:** observation
- **Check contract: 24 distinct predictors, groups and log1p candidates consistent:** PASS
- **Check not-in-contract columns have a reason and are not predictors:** PASS
- **Check one description per exclusion reason code:** PASS 9 codes
- **Files:** [protocol_preregistered.yaml](../../outputs/protocol_preregistered.yaml), [preregistered_values.csv](../../outputs/preregistered_values.csv), [task_contract.md](../../outputs/task_contract.md)

### 1.4 Metrics {#card-1-4}

Coverage: **IMPLEMENTED**; checks: **PASS**.

- **What was done:** Primary metrics: MAE (regression), AP (classification), with secondary metrics and charts; evaluation settings for s09 pre-registered.
- **Conclusion:** 3 verified citations in the task contract.
- **Claim type:** observation
- **Check every citation is in the verified list:** PASS 8 citations
- **Files:** [protocol_preregistered.yaml](../../outputs/protocol_preregistered.yaml), [preregistered_values.csv](../../outputs/preregistered_values.csv), [task_contract.md](../../outputs/task_contract.md)

### 1.5 Cost assumption {#card-1-5}

Coverage: **IMPLEMENTED**; checks: **PASS**.

- **What was done:** Illustrative cost FN:FP = 5:1.
- **Conclusion:** Stated as an assumption; drives the s08 threshold table (cost cutoff 1/6).
- **Claim type:** observation
- **Check every citation is in the verified list:** PASS 8 citations
- **Files:** [protocol_preregistered.yaml](../../outputs/protocol_preregistered.yaml), [preregistered_values.csv](../../outputs/preregistered_values.csv), [task_contract.md](../../outputs/task_contract.md)

### 1.6 Model families {#card-1-6}

Coverage: **IMPLEMENTED**; checks: **—**.

- **What was done:** 5 regression and 4 classification estimators, with the s06 plain settings.
- **Conclusion:** No boosting, voting or stacking.
- **Claim type:** observation
- **Files:** [protocol_preregistered.yaml](../../outputs/protocol_preregistered.yaml), [preregistered_values.csv](../../outputs/preregistered_values.csv), [task_contract.md](../../outputs/task_contract.md)

### 1.7 Decision rule {#card-1-7}

Coverage: **IMPLEMENTED**; checks: **PASS**.

- **What was done:** One-standard-error rule, simplicity order, plain-vs-tuned comparison, fallback, s08 gate, calibration keep rule and threshold candidates pre-registered.
- **Conclusion:** e5lib.metrics.one_se_select implements the rule; its contract tests cover the simpler-within-one-SE case.
- **Claim type:** observation
- **Check every citation is in the verified list:** PASS 8 citations
- **Files:** [protocol_preregistered.yaml](../../outputs/protocol_preregistered.yaml), [preregistered_values.csv](../../outputs/preregistered_values.csv), [task_contract.md](../../outputs/task_contract.md)

### 1.8 Search budget {#card-1-8}

Coverage: **IMPLEMENTED**; checks: **PASS**.

- **What was done:** Grids fixed: tree depths [4, 5, 6, 8, 10, 12, 14, 16, 18], forest depths [8, 10, 12, 14, 16, 18], leaves [20, 50, 100, 200], alpha and C [0.01, 0.1, 0.5, 1, 5, 10, 20, 50, 100]; forest 200 trees; seed 42.
- **Conclusion:** Checked against the AGREED s07 blueprint (see check).
- **Claim type:** observation
- **Check grids match the AGREED s07 blueprint:** PASS
- **Files:** [protocol_preregistered.yaml](../../outputs/protocol_preregistered.yaml), [preregistered_values.csv](../../outputs/preregistered_values.csv), [task_contract.md](../../outputs/task_contract.md)

### 1.9 Outputs {#card-1-9}

Coverage: **IMPLEMENTED**; checks: **PASS**.

- **What was done:** spec/protocol.yaml (pre-registered layer) and task_contract.md written; the values are also listed in preregistered_values.csv for review.
- **Conclusion:** Later stages read these values through e5lib.protocol; none hard-codes them.
- **Claim type:** observation
- **Check pre-registered before any later stage has outputs:** PASS stages with outputs: none
- **Check all ten blueprints AGREED:** PASS
- **Files:** [protocol_preregistered.yaml](../../outputs/protocol_preregistered.yaml), [preregistered_values.csv](../../outputs/preregistered_values.csv)
