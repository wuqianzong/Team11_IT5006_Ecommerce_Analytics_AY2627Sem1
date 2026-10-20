# EDA review pack: s03_eda/classification

Human gate before s04 (G-31). Every table and figure of this node is listed below; the team records its decisions in `spec/human_decisions.yaml` (section `s03_to_s04.classification`), logged in CHANGELOG.md. s04 does not run until both are recorded.

Rows: 77,736 eligible classification orders purchased before the test cutoff 2018-05-26 12:16:34 (latest purchase used 2018-05-26 12:12:15).

## Target: is_detractor (3.2)

| class | orders | share |
| --- | --- | --- |
| low review (score <= 2), is_detractor = 1 | 11493 | 0.1478 |
| normal review (score >= 3), is_detractor = 0 | 66243 | 0.8522 |
| total | 77736 | 1.0000 |

![bar](figures/target_is_detractor_bar.png)

## Outcome trends (3.3)

| month | orders | orders_with_lead_time | median_lead_days | late_vs_promised_rate | orders_with_review | detractor_rate |
| --- | --- | --- | --- | --- | --- | --- |
| 2017-01 | 777 | 741 | 10.7145 | 0.0297 | 777 | 0.1480 |
| 2017-02 | 1708 | 1643 | 10.9498 | 0.0280 | 1708 | 0.1382 |
| 2017-03 | 2597 | 2526 | 10.1247 | 0.0550 | 2597 | 0.1275 |
| 2017-04 | 2360 | 2290 | 12.7430 | 0.0773 | 2360 | 0.1483 |
| 2017-05 | 3606 | 3517 | 9.7826 | 0.0344 | 3606 | 0.1179 |
| 2017-06 | 3181 | 3111 | 10.8020 | 0.0379 | 3181 | 0.1201 |
| 2017-07 | 3911 | 3842 | 10.1524 | 0.0336 | 3911 | 0.1102 |
| 2017-08 | 4241 | 4165 | 9.7698 | 0.0331 | 4241 | 0.1068 |
| 2017-09 | 4194 | 4118 | 10.3136 | 0.0512 | 4194 | 0.1159 |
| 2017-10 | 4510 | 4446 | 10.2492 | 0.0515 | 4510 | 0.1188 |
| 2017-11 | 7360 | 7237 | 12.6274 | 0.1415 | 7360 | 0.1773 |
| 2017-12 | 5561 | 5461 | 13.1226 | 0.0826 | 5561 | 0.1577 |
| 2018-01 | 7126 | 7013 | 11.8047 | 0.0649 | 7126 | 0.1485 |
| 2018-02 | 6573 | 6507 | 14.2617 | 0.1589 | 6573 | 0.2004 |
| 2018-03 | 7106 | 6948 | 13.3387 | 0.2106 | 7106 | 0.2250 |
| 2018-04 | 6859 | 6748 | 9.3033 | 0.0520 | 6859 | 0.1276 |
| 2018-05 | 6066 | 5992 | 8.9830 | 0.0915 | 6066 | 0.1182 |

![trends](figures/outcome_trends.png)

## Numeric features vs is_detractor (3.6)

| feature | n | overlap_coefficient | overlap_method | roc_auc | mutual_information |
| --- | --- | --- | --- | --- | --- |
| total_freight | 77736 | 0.8660 | KDE (log1p scale) | 0.5871 | 0.0102 |
| purchase_month | 77736 | 0.8876 | discrete frequencies | 0.4748 | 0.0040 |
| n_items | 77736 | 0.8913 | discrete frequencies | 0.5548 | 0.0073 |
| interstate_share | 77736 | 0.9143 | discrete frequencies | 0.5412 | 0.0026 |
| total_price | 77736 | 0.9322 | KDE (log1p scale) | 0.5442 | 0.0075 |
| distance_km_max | 76826 | 0.9335 | KDE (log1p scale) | 0.5474 | 0.0035 |
| n_products | 77736 | 0.9467 | discrete frequencies | 0.5267 | 0.0044 |
| total_weight_g | 77720 | 0.9473 | KDE (log1p scale) | 0.5289 | 0.0050 |
| total_volume_cm3 | 77720 | 0.9476 | KDE (log1p scale) | 0.5289 | 0.0085 |
| payment_installments_max | 77736 | 0.9568 | discrete frequencies | 0.5258 | 0.0008 |
| freight_ratio | 77736 | 0.9611 | KDE | 0.5128 | 0.0088 |
| n_sellers | 77736 | 0.9671 | discrete frequencies | 0.5165 | 0.0041 |
| purchase_hour | 77736 | 0.9754 | discrete frequencies | 0.5012 | 0.0003 |
| n_categories | 77736 | 0.9804 | discrete frequencies | 0.5047 | 0.0016 |
| purchase_dayofweek | 77736 | 0.9832 | discrete frequencies | 0.5019 | 0.0001 |
| category_missing_fraction | 77736 | 0.9928 | discrete frequencies | 0.5036 | 0.0004 |
| distance_missing_fraction | 77736 | 0.9980 | discrete frequencies | 0.4991 | 0.0000 |
| n_payment_methods | 77736 | 0.9994 | discrete frequencies | 0.4997 | 0.0000 |
| volume_missing_fraction | 77736 | 0.9999 | discrete frequencies | 0.5000 | 0.0000 |
| weight_missing_fraction | 77736 | 0.9999 | discrete frequencies | 0.5000 | 0.0000 |

![class-conditional](figures/numeric_vs_is_detractor.png)

## Categorical features vs is_detractor (3.7)

| feature | mutual_information |
| --- | --- |
| customer_state | 0.0051 |
| primary_category | 0.0026 |
| primary_payment_type | 0.0000 |
| primary_seller_state | 0.0009 |

Per-level detractor rates: categorical_feature_target_is_detractor.csv.

![detractor rate by level](figures/categorical_vs_is_detractor.png)

## Missingness and outliers (3.8)

| feature | type | missing_share | share_outside_1_5_iqr | share_outside_3_iqr | vif | vif_note |
| --- | --- | --- | --- | --- | --- | --- |
| n_items | numeric | 0.0000 | 0.1001 | 0.1001 | 1.6467 |  |
| n_products | numeric | 0.0000 | 0.0327 | 0.0327 | 1.8025 |  |
| n_sellers | numeric | 0.0000 | 0.0120 | 0.0120 | 1.8561 |  |
| n_categories | numeric | 0.0000 | 0.0234 | 0.0234 | 4.9191 |  |
| total_price | numeric | 0.0000 | 0.0797 | 0.0408 | 1.4752 |  |
| total_freight | numeric | 0.0000 | 0.0969 | 0.0488 | 3.3220 |  |
| freight_ratio | numeric | 0.0000 | 0.0683 | 0.0230 | 1.2595 |  |
| total_weight_g | numeric | 0.0002 | 0.1408 | 0.0828 | 3.4977 |  |
| total_volume_cm3 | numeric | 0.0002 | 0.0978 | 0.0434 | 3.4242 |  |
| weight_missing_fraction | numeric | 0.0000 | 0.0002 | 0.0002 |  | constant on the complete rows |
| volume_missing_fraction | numeric | 0.0000 | 0.0002 | 0.0002 |  | constant on the complete rows |
| primary_category | categorical | 0.0000 |  |  |  |  |
| category_missing_fraction | numeric | 0.0000 | 0.0171 | 0.0171 | 4.3683 |  |
| customer_state | categorical | 0.0000 |  |  |  |  |
| primary_seller_state | categorical | 0.0000 |  |  |  |  |
| distance_km_max | numeric | 0.0117 | 0.0800 | 0.0068 | 1.6817 |  |
| distance_missing_fraction | numeric | 0.0000 | 0.0117 | 0.0117 |  | constant on the complete rows |
| interstate_share | numeric | 0.0000 | 0.0000 | 0.0000 | 1.4985 |  |
| purchase_month | numeric | 0.0000 | 0.0000 | 0.0000 | 1.0030 |  |
| purchase_dayofweek | numeric | 0.0000 | 0.0000 | 0.0000 | 1.0021 |  |
| purchase_hour | numeric | 0.0000 | 0.0000 | 0.0000 | 1.0006 |  |
| primary_payment_type | categorical | 0.0000 |  |  |  |  |
| payment_installments_max | numeric | 0.0000 | 0.0662 | 0.0016 | 1.1541 |  |
| n_payment_methods | numeric | 0.0000 | 0.0232 | 0.0232 | 1.0023 |  |

## Skewness of the log1p candidates (3.8, for s04 4.2)

| feature | skewness | threshold | log1p |
| --- | --- | --- | --- |
| total_price | 10.0561 | 1.0000 | True |
| total_freight | 8.0991 | 1.0000 | True |
| total_weight_g | 6.5946 | 1.0000 | True |
| total_volume_cm3 | 7.4804 | 1.0000 | True |
| distance_km_max | 1.6391 | 1.0000 | True |

## Candidate screen (3.10-3.13, G-68, G-69; not predictors unless adopted)

| card | feature | kind | n | missing_share | overlap_coefficient | roc_auc | mutual_information | rank_in_extended | inside_95_cut | inside_99_cut | skewness | vif_in_extended_set |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3.10 | product_photos_qty | numeric | 76441 | 0.0167 | 0.9631 | 0.4796 | 0.0005 | 26 | False | True | 1.8939 | 1.0451 |
| 3.10 | product_description_lenght | numeric | 76441 | 0.0167 | 0.9776 | 0.4923 | 0.0054 | 9 | True | True | 2.0451 | 1.0911 |
| 3.10 | product_name_lenght | numeric | 76441 | 0.0167 | 0.9719 | 0.5040 | 0.0000 | 36 | False | False | -0.8842 | 1.0594 |
| 3.11 | est_delivery_days | numeric | 77736 | 0.0000 | 0.9501 | 0.5378 | 0.0030 | 16 | True | True | 1.2476 | 1.7468 |
| 3.12 | customer_region | categorical | 77736 | 0.0000 | 0.9538 |  | 0.0012 | 23 | False | True |  |  |
| 3.12 | seller_region | categorical | 77736 | 0.0000 | 0.9786 |  | 0.0002 | 29 | False | False |  |  |
| 3.12 | region_pair | categorical | 77736 | 0.0000 | 0.9494 |  | 0.0019 | 20 | True | True |  |  |
| 3.13 | seller_prior_review_mean | numeric | 72429 | 0.0683 | 0.9054 | 0.4405 | 0.0110 | 1 | True | True | -1.8287 | 5.1024 |
| 3.13 | seller_prior_review_count | numeric | 77736 | 0.0000 | 0.9625 | 0.5076 | 0.0015 | 22 | True | True | 2.6682 | 1445.1021 |
| 3.13 | seller_prior_detractor_share | numeric | 72429 | 0.0683 | 0.9057 | 0.5573 | 0.0080 | 5 | True | True | 3.0601 | 5.0489 |
| 3.13 | seller_prior_delivered_count | numeric | 77736 | 0.0000 | 0.9629 | 0.5069 | 0.0022 | 19 | True | True | 2.6105 | 1446.0587 |
| 3.13 | seller_prior_late_share | numeric | 73017 | 0.0607 | 0.9017 | 0.5359 | 0.0062 | 8 | True | True | 5.6150 | 1.2132 |

Extended cut points (24 + 12): {'0.95': 22, '0.99': 26}. Collinear groups involving a candidate: ['seller_prior_review_count', 'seller_prior_delivered_count']. Record adopted candidates under `adopted_candidates` in human_decisions.yaml.

![extended ranking](figures/candidate_ranking_extended.png)

## Importance ranking (3.8)

Measure: mutual information. All 24 contract predictors.

| rank | feature | type | method | value | share | cumulative_share |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | total_freight | numeric | mutual_info_classif, continuous (k-NN, k=3) | 0.0102 | 0.1313 | 0.1313 |
| 2 | freight_ratio | numeric | mutual_info_classif, continuous (k-NN, k=3) | 0.0088 | 0.1133 | 0.2447 |
| 3 | total_volume_cm3 | numeric | mutual_info_classif, continuous (k-NN, k=3) | 0.0085 | 0.1094 | 0.3541 |
| 4 | total_price | numeric | mutual_info_classif, continuous (k-NN, k=3) | 0.0075 | 0.0967 | 0.4508 |
| 5 | n_items | numeric | mutual_info_classif, discrete (contingency) | 0.0073 | 0.0936 | 0.5444 |
| 6 | customer_state | categorical | mutual_info_classif, discrete (contingency) | 0.0051 | 0.0655 | 0.6098 |
| 7 | total_weight_g | numeric | mutual_info_classif, continuous (k-NN, k=3) | 0.0050 | 0.0645 | 0.6743 |
| 8 | n_products | numeric | mutual_info_classif, discrete (contingency) | 0.0044 | 0.0570 | 0.7313 |
| 9 | n_sellers | numeric | mutual_info_classif, discrete (contingency) | 0.0041 | 0.0525 | 0.7838 |
| 10 | purchase_month | numeric | mutual_info_classif, discrete (contingency) | 0.0040 | 0.0512 | 0.8350 |
| 11 | distance_km_max | numeric | mutual_info_classif, continuous (k-NN, k=3) | 0.0035 | 0.0448 | 0.8798 |
| 12 | interstate_share | numeric | mutual_info_classif, discrete (contingency) | 0.0026 | 0.0337 | 0.9135 |
| 13 | primary_category | categorical | mutual_info_classif, discrete (contingency) | 0.0026 | 0.0335 | 0.9470 |
| 14 | n_categories | numeric | mutual_info_classif, discrete (contingency) | 0.0016 | 0.0199 | 0.9669 |
| 15 | primary_seller_state | categorical | mutual_info_classif, discrete (contingency) | 0.0009 | 0.0114 | 0.9783 |
| 16 | payment_installments_max | numeric | mutual_info_classif, discrete (contingency) | 0.0008 | 0.0102 | 0.9885 |
| 17 | category_missing_fraction | numeric | mutual_info_classif, discrete (contingency) | 0.0004 | 0.0055 | 0.9940 |
| 18 | purchase_hour | numeric | mutual_info_classif, discrete (contingency) | 0.0003 | 0.0041 | 0.9981 |
| 19 | purchase_dayofweek | numeric | mutual_info_classif, discrete (contingency) | 0.0001 | 0.0014 | 0.9995 |
| 20 | distance_missing_fraction | numeric | mutual_info_classif, discrete (contingency) | 0.0000 | 0.0004 | 0.9999 |
| 21 | primary_payment_type | categorical | mutual_info_classif, discrete (contingency) | 0.0000 | 0.0001 | 1.0000 |
| 22 | volume_missing_fraction | numeric | mutual_info_classif, discrete (contingency) | 0.0000 | 0.0000 | 1.0000 |
| 23 | weight_missing_fraction | numeric | mutual_info_classif, discrete (contingency) | 0.0000 | 0.0000 | 1.0000 |
| 24 | n_payment_methods | numeric | mutual_info_classif, discrete (contingency) | 0.0000 | 0.0000 | 1.0000 |

![cumulative importance](figures/cumulative_importance.png)

| Threshold option | Features kept (top k) | Features kept |
| --- | --- | --- |
| 95% | 14 | total_freight, freight_ratio, total_volume_cm3, total_price, n_items, customer_state, total_weight_g, n_products, n_sellers, purchase_month, distance_km_max, interstate_share, primary_category, n_categories |
| 99% | 17 | total_freight, freight_ratio, total_volume_cm3, total_price, n_items, customer_state, total_weight_g, n_products, n_sellers, purchase_month, distance_km_max, interstate_share, primary_category, n_categories, primary_seller_state, payment_installments_max, category_missing_fraction |

## Collinearity among raw numeric features (3.8)

Cut-offs from protocol.yaml: |correlation| > 0.9 (Pearson or Spearman) or VIF > 10; VIF on 76,810 complete rows (a column constant on those rows has no VIF). Nothing is dropped in s03.

Identical columns (dropped automatically in s04 4.3, no team decision needed): weight_missing_fraction = volume_missing_fraction.

No group needs a team decision: no pair of distinct columns above the correlation cut-off and no VIF above the VIF cut-off.

| feature_a | feature_b | pearson | spearman | identical |
| --- | --- | --- | --- | --- |
| weight_missing_fraction | volume_missing_fraction | 1.0000 | 1.0000 | True |

![correlation heatmap](figures/numeric_correlation_heatmap.png)

## Decisions for the team (record in spec/human_decisions.yaml)

```yaml
s03_to_s04:
  classification:
    cumulative_importance_threshold: 0.95   # or 0.99
    collinearity_drops:
    adopted_candidates: []   # any of ['product_photos_qty', 'product_description_lenght', 'product_name_lenght', 'est_delivery_days', 'customer_region', 'seller_region', 'region_pair', 'seller_prior_review_mean', 'seller_prior_review_count', 'seller_prior_detractor_share', 'seller_prior_delivered_count', 'seller_prior_late_share'] (G-68), with rationale
```
