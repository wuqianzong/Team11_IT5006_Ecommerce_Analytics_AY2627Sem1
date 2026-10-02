# IT5006 Group 11 — Milestone 2 Proposed Direction

**Project Title**: The E-Commerce Conversion Engine: Balancing Physical Delivery Constraints with Review Sentiment Optimization  
**Framework**: Interconnected Two-Stage Predictive Architecture (Regression + Classification)  
**Applies to**: Milestone 2 (Deadline: Sunday, 11 October 2026, 23:59 | Weight: 40%)  
**Target Report Length**: 6–8 Pages (Excluding cover, references, and appendices)  

---

## 1. Executive Problem Scoping & System Architecture

Following the official guidance in **Page 3 (Example 2 + Example 3) and Pages 4–5 of the IT5006 Project Description**, we formulate a single, cohesive business problem centered on **Marketplace Conversion Optimization**. 

E-commerce conversion operates as an interconnected, two-stage flywheel:
1. **Front-Funnel Conversion (Storefront Checkout)**: Driven by sharp, competitive, and realistic Estimated Delivery Dates (EDDs) that prevent cart abandonment.
2. **Back-Funnel Conversion & Retention (Marketplace Reputation)**: Protected by preventing negative customer reviews (1–2 stars) that destroy seller ratings and depress future product page conversion.

The solution deploys **two complementary, interconnected machine learning models**:

```
                       ┌────────────────────────────────────────────────────────┐
                       │          Point-of-Checkout Order Metadata              │
                       │     (Known at order_purchase_timestamp — Zero Leakage) │
                       └───────────────────────────┬────────────────────────────┘
                                                   │
                                                   ▼
                       ┌────────────────────────────────────────────────────────┐
                       │          STAGE 1: PHYSICAL LOGISTICS CONSTRAINT        │
                       │             Task 1: Delivery Lead-Time Model           │
                       │                  (Continuous Regression)               │
                       └───────────────────────────┬────────────────────────────┘
                                                   │
                                                   ├──────────────────────────────────────────────┐
                                                   ▼                                              ▼
                                    ┌──────────────────────────────┐              ┌──────────────────────────────┐
                                    │ Storefront Dynamic EDD       │              │ Out-of-Fold Predicted Lead   │
                                    │ • Quoted to buyer at checkout│              │ Time Feature: T_pred         │
                                    │ • Wins upfront conversion!   │              │ (Zero-leakage stacking input)│
                                    └──────────────────────────────┘              └──────────────┬───────────────┘
                                                                                                 │
                                                   ┌─────────────────────────────────────────────┘
                                                   ▼
                       ┌────────────────────────────────────────────────────────┐
                       │          STAGE 2: CUSTOMER SENTIMENT OPTIMIZATION      │
                       │            Task 2: Review Detractor Risk Model         │
                       │                  (Binary Classification)               │
                       │       Inputs: T_pred + Freight Ratio + Price +         │
                       │               Product Category + Seller Rating Track   │
                       └───────────────────────────┬────────────────────────────┘
                                                   │
                                                   ▼
                                    ┌──────────────────────────────┐
                                    │ CX & Seller Operations       │
                                    │ • Pre-dispatch packaging QC  │
                                    │ • Priority courier rerouting │
                                    │ • Proactive unboxing VIP care│
                                    │ • Protects seller conversion!│
                                    └──────────────────────────────┘
```

### Problem Statement 1 (Regression Task — Logistics Constraint)
* **Question**: *At checkout, how many calendar days will it physically take for this parcel to travel from seller to customer?*
* **Target Variable**: Continuous delivery lead time in calendar days:
  $$\Delta t_{\text{lead\_days}} = \frac{\text{order\_delivered\_customer\_date} - \text{order\_purchase\_timestamp}}{86400}$$
* **Primary Stakeholder**: **Storefront Product, Fulfillment Planning & Growth Teams**.
* **Business Action**: Replacing Olist's static, over-padded 25-day delivery estimates with calibrated dynamic delivery windows, winning checkout conversion without setting unrealistic expectations (Cui et al., 2024).

### Problem Statement 2 (Classification Task — Sentiment Optimization)
* **Question**: *At order creation, will this transaction result in a negative customer review (1–2 stars / Detractor)?*
* **Target Variable**: Binary customer dissatisfaction / detractor indicator:
  $$y_{\text{detractor}} = \begin{cases} 1, & \text{if } \text{review\_score} \le 2 \\ 0, & \text{if } \text{review\_score} \ge 3 \end{cases}$$
* **Primary Stakeholder**: **Customer Experience (CX), Seller Quality, & Logistics Operations Teams**.
* **Business Action**: Flagging high-risk orders at order placement to trigger pre-dispatch merchant quality checks, express courier upgrades, and proactive customer tracking support, preventing 1-star reviews from destroying seller sales conversion (Deshpande & Pendem, 2023).

---

### 1.1 Formal Verification Against Problem Scoping Checklist (Syllabus Page 4)

| Checklist Criterion | Specific Project Compliance in Proposal | Status |
| :--- | :--- | :---: |
| **1. Derivable Target**<br>*(Can target be computed directly from provided tables without external data?)* | • **Regression**: $\Delta t_{\text{lead\_days}} = (\text{delivered\_date} - \text{purchase\_timestamp}) / 86400$ from `olist_orders_dataset.csv`.<br>• **Classification**: $y_{\text{detractor}} = \mathbb{I}(\text{review\_score} \le 2)$ from `olist_order_reviews_dataset.csv`.<br>Both derived 100% from provided tables across **95,832 complete records** (99.3% join coverage). Zero external data required. | **PASS** |
| **2. Realistic Features**<br>*(Are all predictors known before the outcome occurs — zero leakage?)* | • **Strict Cutoff**: Frozen at `order_purchase_timestamp`.<br>• **Quarantined**: Review comment text, review creation dates, review answer timestamps, actual delivered dates, and carrier handover dates are strictly excluded.<br>• **Interconnection**: Task 1 predicted lead times feed into Task 2 via **Out-of-Fold (OOF) cross-validation stacking**, guaranteeing zero leakage across folds (Kapoor & Narayanan, 2023). | **PASS** |
| **3. Sufficient Signal**<br>*(Does Phase 1 EDA show relationship between features and target?)* | • **Logistics Signal**: Interstate transit averages ~15.2 days vs. ~7.5 days for intrastate routes; distance and parcel weight heavily drive lead days.<br>• **Review Signal**: Empirical audit of 95,832 orders reveals that delivery lead time >17 days **quadruples the low-review rate from 7.31% to 29.20%**.<br>• Non-delivery drivers: Freight-to-price ratio, fragile categories, and seller rating histories strongly differentiate detractors. | **PASS** |
| **4. Manageable Imbalance**<br>*(Do you have a plan for appropriate metrics/handling for imbalanced target?)* | • Low reviews (1–2 stars) represent **12.85% (12,311 orders)**.<br>• Evaluated strictly via **Precision, Recall, F1-Score, and PR-AUC** (Accuracy rejected).<br>• Applying cost-sensitive loss weighting (`scale_pos_weight ≈ 6.78` and `class_weight='balanced'`) and decision threshold tuning ($\tau$) (van den Goorbergh et al., 2022). | **PASS** |
| **5. Clear Stakeholder**<br>*(Can you name a real business role who would use this, and how?)* | • **Storefront Product & Growth**: Uses Task 1 continuous lead-time predictions to display dynamic, calibrated Estimated Delivery Dates (EDDs) at checkout, lifting purchase conversion (Cui et al., 2024).<br>• **CX & Seller Quality Ops**: Uses Task 2 detractor risk scoring to trigger pre-dispatch merchant inspection, courier upgrades, and proactive unboxing support to prevent 1-star reviews and protect seller conversion (Deshpande & Pendem, 2023). | **PASS** |

---

## 2. Business Narrative & The Conversion Flywheel

### 2.1 The Two Pillars of E-Commerce Conversion
In digital marketplace platforms like Olist, gross merchandise value (GMV) is governed by two sequential conversion hurdles:
1. **Front-Funnel Acquisition Conversion (Day 0)**: When prospective buyers evaluate an item at checkout, delivery speed is a decisive conversion factor. Quoting bloated, over-conservative delivery dates causes immediate cart abandonment. As established by **Cui et al. (2024)**, every 1-day reduction in promised delivery time increases sales by **+0.73%** and profits by **+2.0%**.
2. **Back-Funnel Reputation & Retention Conversion (Day 30+)**: Post-purchase satisfaction dictates future platform viability. In online marketplaces, over 90% of prospective buyers read customer reviews before purchasing. When an order delivers a poor experience, the customer posts a 1-star or 2-star review. As proven by **Deshpande & Pendem (2023)**, negative ratings shocks degrade third-party merchant sales by **13.3% per day of delay**, permanently suppressing seller conversion and driving customer churn.

### 2.2 Physical Logistics as the Primary Constraint
Olist operates as an e-commerce gateway in Brazil, connecting small merchants to major national storefronts. Milestone 1 exploratory data analysis uncovered Brazil's extreme geographical asymmetry:
* **Seller Concentration**: Over 70% of active merchants reside in the industrialized Southeast (São Paulo State, `SP`).
* **Customer Dispersion**: Buyers span all 27 Brazilian states, frequently requiring shipments to traverse 3,000+ kilometers over federal road networks.

Because delivery is constrained by physical geography, parcel weight, and road infrastructure, an e-commerce platform cannot arbitrarily promise 2-day delivery across continental routes without triggering catastrophic service failures. **Task 1 (Regression)** estimates this physical constraint with statistical rigor.

### 2.3 The Empirical Delivery-Review Nexus (Data Reality)
An empirical audit across all **95,832 completed and reviewed orders** in the Olist dataset demonstrates how physical logistics directly governs review outcomes:

| Delivery Lead Time Quintile | Delivery Days Range | Low Review Rate (1–2 Stars) | Commercial Takeaway |
| :--- | :---: | :---: | :--- |
| **Quintile 1 (Fastest 20%)** | 0.5 to 6.0 days | **7.31%** | Baseline product dissatisfaction rate. |
| **Quintile 2 (20%–40%)** | 6.0 to 8.7 days | **8.03%** | Healthy satisfaction band. |
| **Quintile 3 (40%–60%)** | 8.7 to 12.1 days | **9.31%** | Moderate satisfaction band. |
| **Quintile 4 (60%–80%)** | 12.1 to 17.4 days | **10.38%** | Slight increase in friction. |
| **Quintile 5 (Slowest 20%)** | **17.4 to 208.4 days** | **29.20%** | **🚨 4X SURGE in negative reviews!** |

Crucially, **66.3% of all low reviews (8,190 / 12,350) occur on orders that arrived on-time**, driven by:
* Disproportionate freight-to-price ratios (paying R\$35 freight on an R\$20 item induces severe buyer remorse).
* Inherently fragile or complex categories (electronics, furniture, audio equipment).
* Sub-par merchant packaging or seller reliability track records.

### 2.4 The Interconnected Solution: How the Models Work Together
Rather than operating in isolation, the two models form a cascaded intelligence engine:
1. **At Checkout**: Task 1 calculates the true physical delivery capability ($\hat{T}_{\text{lead\_days}}$) based on spatial distance, parcel dimensions, and seasonal factors. The storefront uses this to display a calibrated, competitive dynamic delivery window (e.g. 7–9 days for local corridors), winning the checkout conversion.
2. **At Order Creation**: Task 2 takes the order metadata **and incorporates Task 1's predicted lead time ($\hat{T}_{\text{lead\_days}}$)** to evaluate the overall probability of customer dissatisfaction ($y_{\text{detractor}} \in \{0, 1\}$).
3. **Proactive Intervention**: When an order is flagged as high-risk ($P \ge \tau$):
   * *Logistics Ops*: Issues a priority dispatch alert to the merchant and upgrades the parcel from standard road freight (Correios PAC) to express courier (Correios Sedex / Private Air).
   * *Customer Experience (CX)*: Initiates proactive tracking notifications, pre-emptive unboxing guides, and VIP support check-ins, resolving issues before the customer ever writes a 1-star review.

### 2.5 Literature-Calibrated Economic & ROI Simulation
While raw pre-purchase clickstream impressions are unobserved in Olist's post-purchase transactional tables, we quantify business impact by combining our model's empirical metrics with causal elasticities established in peer-reviewed literature:

1. **Top-Line Sales Lift from Task 1 (Cui et al., 2024)**:
   * Olist's legacy delivery estimates averaged **23.8 days** vs. actual delivery of **12.5 days** (+11.2-day over-pad; +9.4 days for SP $\rightarrow$ SP).
   * Compressing stated delivery promises by a safe **4 to 6 days** on predictable routes yields:
     $$\text{Estimated Sales Lift} = 4 \text{ to } 6 \text{ days} \times 0.73\%/\text{day} = \mathbf{+2.92\% \text{ to } +4.38\%}$$
   * On Olist's total GMV of **R\$ 13,591,643 (~R\$ 13.6M)**, this generates **~R\$ 397,000 to R\$ 595,000 in incremental top-line revenue**.
2. **Reputation Protection from Task 2 (Deshpande & Pendem, 2023)**:
   * An empirical intercept of ~50% of detractor orders (~6,150 orders) shields marketplace sellers from negative rating shocks, protecting an estimated **~R\$ 1.8M in annualized seller sales volume** from conversion decay and customer churn.

---

## 3. Direct Application of Week 06 Machine Learning Implementation Lab

Our end-to-end architecture directly incorporates the modeling, pipeline design, and deployment workflows taught in the **Week 06 ML Implementation Lab (`L6.1_Fraud_Detection_Training` & `L6.2_Bulk_Scoring_Demo`)**:

### 3.1 Haversine Geospatial Feature Engineering (Week 6 Lab Pattern)
Following the exact location-delta formulation taught in Week 6:
* We convert customer and seller latitude/longitude coordinates from degrees to radians:
  $$\text{radians} = \text{degrees} \times \left(\frac{\pi}{180}\right)$$
* We apply the **Haversine formula** to calculate exact spherical distance in kilometers between customer and seller zip-code centroids:
  $$d = 2R \arcsin \left( \sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)} \right)$$
  where $R = 6,371\text{ km}$. This produces an uncompromised physical transit distance feature (`distance_km`) for every transaction.

### 3.2 Preprocessing Pipelines with `ColumnTransformer` (Anti-Leakage Standard)
Mirroring the Week 6 pipeline architecture, we separate feature types and bundle them into Scikit-Learn `Pipeline` workflows:
* **Categorical Features**: `CATEGORICAL_COLS = ['customer_state', 'seller_state', 'product_category_name_english', 'payment_type']` processed with `OneHotEncoder(handle_unknown='ignore', sparse_output=False)` (or `OrdinalEncoder`).
* **Numerical Features**: `NUMERIC_COLS = ['price', 'freight_value', 'freight_ratio', 'product_weight_g', 'product_volume_cm3', 'distance_km', 'seller_historical_review_score']` processed with `RobustScaler()` / `StandardScaler()`.
* **Zero Leakage Rule**: As emphasized in Week 6 Step 4, train-test splitting occurs **before** preprocessor fitting so encoders and scalers only ever learn from the training fold.

### 3.3 Out-of-Fold (OOF) Stacking & Cascading Architecture
To pass Task 1's predicted lead time ($\hat{T}_{\text{lead\_days}}$) into Task 2 without data leakage:
* Within each cross-validation fold, the Task 1 regression model is trained on the training partition and generates Out-of-Fold predictions for the validation partition.
* These out-of-fold predictions serve as the input feature for training Task 2.
* At runtime inference, a unified Scikit-Learn pipeline chains the Task 1 regressor output into the Task 2 classifier feature vector.

### 3.4 Ensemble Workflows & Soft Voting (Week 6 Lab Architecture)
Adopting the exact ensemble model training taught in Week 6 Step 5:
* **Pipeline 1 (XGBoost)**: Preprocessor chained directly to `xgb.XGBClassifier` (with `scale_pos_weight ≈ 6.78` tuned for 12.85% imbalance) and `xgb.XGBRegressor`.
* **Pipeline 2 (Random Forest)**: Preprocessor chained to `RandomForestClassifier` (with `class_weight='balanced'`) and `RandomForestRegressor`.
* **Soft Voting Ensemble**: Averaging predicted probabilities across diverse models:
  $$\hat{P}_{\text{ensemble}} = \frac{\hat{P}_{\text{XGB}} + \hat{P}_{\text{RF}}}{2}$$
  and classifying via decision threshold tuning $\hat{y} = (\hat{P}_{\text{ensemble}} \ge \tau)$.

### 3.5 Artifact Serialization & Metadata Packaging (Week 6 Lab Step 7)
Following the production-readiness standards taught in Week 6 Step 7:
* **Full Pipeline Pickling**: Serializing complete pipelines using `joblib.dump(pipeline, '..._pipeline.pkl')` so downstream inference requires zero manual preprocessing.
* **`model_metadata.json`**: Tracking model version, training timestamp, Scikit-Learn/XGBoost hyperparameters, and cross-validation scores (MAE, RMSE, F1, PR-AUC).
* **`feature_stats.json`**: Exporting training distribution parameters (min, max, mean, median, standard deviation) for runtime data validation and outlier checking during live inference.

### 3.6 Diagnostic Evaluations (Week 6 Lab Step 6)
* Visualizing confusion matrices via `seaborn.heatmap`.
* Extracting feature importances from `pipeline.named_steps['classifier'].feature_importances_`.
* Logging multi-metric evaluation tables (Accuracy, Precision, Recall, F1-Score, ROC-AUC, PR-AUC).

---

## 4. Grounding in the 6 Literature Review Papers

Our implementation directly translates findings from our Milestone 1 literature review into technical design decisions:

1. **Promising Delivery Speed in Online Retail (Cui et al., 2024)**:  
   Establishes that delivery speed promises fundamentally govern purchase conversion (+0.73% sales per day faster), while over-promising inflates returns. Our regression model provides calibrated expected lead times to capture sales lift without overpromising.
2. **Ratings Impact on Sales and Purchasing Behavior (Deshpande & Pendem, 2023)**:  
   Demonstrates that fulfillment delays trigger negative reviews that reduce seller sales by 13.3% per day of delay. Task 2 directly predicts low review risk (1–2 stars) to enable proactive intervention before negative ratings materialize.
3. **Macro-Level Ground Truth (Kandula et al., 2021)**:  
   Unlike Kandula’s unobserved hourly presence assumptions, our delivery lead times and customer review scores are fully recorded in observational logs across 95,832 orders, providing solid ground truth.
4. **Tree Ensembles for Tabular Data (Grinsztajn et al., 2022)**:  
   Tree-based models (XGBoost / Random Forest) handle tabular coordinate-axis splits and uninformative features significantly better than neural networks without requiring complex scaling.
5. **Strict Point-in-Time Anti-Leakage Discipline (Kapoor & Narayanan, 2023)**:  
   We enforce a strict cutoff at `order_purchase_timestamp`. Post-purchase dates (`order_delivered_carrier_date`, review text, review creation dates) are quarantined to ensure zero data leakage.
6. **Cost-Sensitive Imbalance Handling (van den Goorbergh et al., 2022)**:  
   Low reviews represent 12.85% of transactions. We reject synthetic resampling (SMOTE) to preserve natural probability calibration, using cost-sensitive weighted losses (`class_weight='balanced'`, `scale_pos_weight`) and precision-recall threshold optimization.

---

## 5. Point-in-Time Feature Engineering Strategy

All features are extracted strictly from data available at or before `order_purchase_timestamp`:

| Feature Family | Candidate Variables | Domain Justification & Task Allocation |
| :--- | :--- | :--- |
| **Geospatial & Spatial Corridors** | • Geodesic distance (km) via Haversine formula<br>• `is_interstate` boolean flag<br>• Origin & destination state clusters (e.g. SE $\rightarrow$ NE) | Direct physical proxy for transportation transit time across Brazil's diverse geography (Primary in Task 1 & Task 2). |
| **Financial Scale & Freight Burden** | • Total order price & freight value<br>• Freight-to-price ratio (`freight / price`)<br>• Number of items in basket | High freight ratios on low-value items directly cause buyer remorse and drive low review scores (Primary in Task 2). |
| **Physical Parcel Specifications** | • Total parcel weight (grams)<br>• Cubic volume ($L \times W \times H \text{ in } \text{cm}^3$)<br>• Packaging density ratio ($\text{weight} / \text{volume}$) | Heavy/oversized freight requires specialized road freight carriers with lower departure frequencies (Primary in Task 1). |
| **Product Category Risk** | • English product category name<br>• High-defect category indicator (Electronics, Furniture, Audio vs. Books, Apparel) | Complex and fragile product categories exhibit structurally higher customer return and dissatisfaction rates (Primary in Task 2). |
| **Seller Historical Track Record** | • Historical seller review score prior to order timestamp<br>• Historical seller dispatch SLA compliance rate | Seller operational diligence is the strongest early leading indicator of parcel quality and fulfillment speed (Task 1 & Task 2). |
| **Temporal & Seasonality Context** | • Day of week of purchase<br>• Purchase hour of day<br>• Month of year / Black Friday high-volume quarter flag | Captures weekend dispatch bottlenecks and nationwide logistics congestion during peak promotional surges (Task 1). |
| **Cascaded Predictive Feature** | • $\hat{T}_{\text{lead\_days}}$: Predicted delivery lead time generated by Task 1 (via Out-of-Fold cross-validation) | Bridges physical logistics constraint into customer sentiment prediction with zero data leakage (Unique to Task 2). |

---

## 6. Modeling Strategy Within the 2–3 Family Budget

To adhere to the **"Quality over Quantity"** rule (Page 5 of Project Description), we implement matching algorithms across 2 core families plus an interconnected stacking ensemble:

```
  ┌────────────────────────────────────────────────────────────────────────┐
  │                        MODEL FAMILY BUDGET                             │
  ├────────────────────────────────────┬───────────────────────────────────┤
  │ Family A: Linear Models            │ Family B: Tree-Based Ensembles    │
  │ • Task 1 Baseline: OLS Linear      │ • Task 1 Baseline: Decision Tree  │
  │ • Task 1 Tuned: Ridge / Lasso      │ • Task 1 Tuned: RF & XGBoost      │
  │ • Task 2: Logistic Regression (Bal)│ • Task 2: RF & XGBoost (Weighted) │
  └─────────────────┬──────────────────┴───────────────────┬───────────────┘
                    └───────────────────┬──────────────────┘
                                        ▼
                   ┌────────────────────────────────────────┐
                   │ Family C: Two-Stage Stacking Ensemble  │
                   │ Task 1 OOF predictions feed Task 2     │
                   │ Soft Voting (XGBoost + Random Forest)  │
                   └────────────────────────────────────────┘
```

1. **Family A (Linear Models)**:
   * *Task 1 (Regression)*: `LinearRegression` (Baseline) $\rightarrow$ `Ridge` / `Lasso` (Tuned Regularization).
   * *Task 2 (Classification)*: `LogisticRegression(class_weight='balanced', penalty='l2')`.
2. **Family B (Tree-Based Models)**:
   * *Task 1 (Regression)*: `DecisionTreeRegressor` (Baseline) $\rightarrow$ `RandomForestRegressor` $\rightarrow$ `XGBoostRegressor`.
   * *Task 2 (Classification)*: `DecisionTreeClassifier` (Baseline) $\rightarrow$ `RandomForestClassifier(class_weight='balanced')` $\rightarrow$ `XGBoostClassifier(scale_pos_weight≈6.78)`.
3. **Family C (Two-Stage Stacking & Soft Voting Ensemble)**:
   * Interconnected pipeline where Task 1 regression outputs feed into Task 2, combined with soft voting probabilities:
     $$\hat{P}_{\text{ensemble}} = 0.5 \cdot \hat{P}_{\text{XGB}} + 0.5 \cdot \hat{P}_{\text{RF}}$$

---

## 7. Validation Protocol & Evaluation Discipline

1. **Split Protocol**:
   * **5-Fold `GroupKFold` grouped by `customer_unique_id`**: Prevents multi-order customer patterns from leaking across training and validation splits.
2. **Evaluation Metrics**:
   * **Task 1 (Regression)**: Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and Coefficient of Determination ($R^2$).
   * **Task 2 (Classification)**: Precision, Recall, F1-Score, and Precision-Recall AUC (PR-AUC). Accuracy is explicitly rejected due to class imbalance.
3. **Operational Threshold Tuning**:
   * For the classification task, optimize the probability decision threshold $\tau$ using an asymmetric business cost matrix where missing a detractor review (False Negative) is penalized $5\times$ more heavily than a false alarm (False Positive).

---

## 8. Implementation Deliverables & Execution Timeline

* **Phase 2 Deadline**: Sunday, 11 October 2026, 23:59.
* **Architecture Storage**:
  * Feature table: `data/business/ml/orders_ml_features.csv`
  * Feature Pipeline: `src/features/build_features.py`
  * Model Training Scripts: `src/models/train_regression.py` & `src/models/train_classification.py`
  * Analysis Notebooks: `notebooks/04_feature_engineering.ipynb` & `notebooks/05_model_training_and_evaluation.ipynb`
  * Serialized Pipelines: `artifacts/models/lead_time_pipeline.pkl` & `artifacts/models/review_sentiment_pipeline.pkl`
  * Model Metadata: `artifacts/models/model_metadata.json` & `artifacts/models/feature_stats.json`
* **Report Deliverable**: 6–8 page PDF technical report detailing problem context, anti-leakage lineage, CV metric comparisons, residual plots, SHAP feature importance, and concrete stakeholder deployment recommendations including the literature-calibrated ROI simulation.
