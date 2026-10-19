# EDA review pack: s03_eda/regression

Human gate before s04 (G-31). Every table and figure of this node is listed below; the team records its decisions in `spec/human_decisions.yaml` (section `s03_to_s04.regression`), logged in CHANGELOG.md. s04 does not run until both are recorded.

Rows: 77,139 eligible regression orders purchased before the test cutoff 2018-05-26 18:18:03 (latest purchase used 2018-05-26 18:16:57).

## Target: lead_days (3.1)

| statistic | value |
| --- | --- |
| count | 77,139.0000 |
| missing_share | 0.0000 |
| mean | 13.4391 |
| sd | 9.4646 |
| min | 0.5334 |
| p1 | 1.8989 |
| p5 | 3.2295 |
| p25 | 7.2151 |
| p50 | 11.1820 |
| p75 | 16.9642 |
| p95 | 31.1236 |
| p99 | 47.3791 |
| max | 133.2411 |
| skewness | 2.3996 |
| kurtosis | 11.5469 |

![lead_days KDE](figures/target_lead_days_kde.png)

## Outcome trends (3.3)

| month | orders | orders_with_lead_time | median_lead_days | late_vs_promised_rate | orders_with_review | detractor_rate |
| --- | --- | --- | --- | --- | --- | --- |
| 2016-10 | 265 | 265 | 17.9443 | 0.0113 | 262 | 0.1641 |
| 2016-12 | 1 | 1 | 4.6930 | 0.0000 | 1 | 0.0000 |
| 2017-01 | 750 | 750 | 10.7336 | 0.0307 | 741 | 0.1201 |
| 2017-02 | 1651 | 1651 | 10.9644 | 0.0309 | 1642 | 0.1102 |
| 2017-03 | 2535 | 2535 | 10.1083 | 0.0517 | 2516 | 0.1129 |
| 2017-04 | 2296 | 2296 | 12.7210 | 0.0758 | 2284 | 0.1283 |
| 2017-05 | 3543 | 3543 | 9.7894 | 0.0356 | 3515 | 0.1010 |
| 2017-06 | 3133 | 3133 | 10.8020 | 0.0380 | 3109 | 0.1081 |
| 2017-07 | 3872 | 3872 | 10.1581 | 0.0343 | 3842 | 0.1010 |
| 2017-08 | 4193 | 4193 | 9.7698 | 0.0332 | 4165 | 0.0951 |
| 2017-09 | 4150 | 4150 | 10.3144 | 0.0520 | 4118 | 0.1032 |
| 2017-10 | 4478 | 4478 | 10.2634 | 0.0529 | 4446 | 0.1109 |
| 2017-11 | 7284 | 7284 | 12.6920 | 0.1426 | 7233 | 0.1660 |
| 2017-12 | 5512 | 5512 | 13.1420 | 0.0836 | 5460 | 0.1445 |
| 2018-01 | 7068 | 7068 | 11.8293 | 0.0655 | 7012 | 0.1375 |
| 2018-02 | 6552 | 6552 | 14.2628 | 0.1595 | 6504 | 0.1943 |
| 2018-03 | 7003 | 7003 | 13.3677 | 0.2136 | 6948 | 0.2119 |
| 2018-04 | 6797 | 6797 | 9.3153 | 0.0531 | 6751 | 0.1181 |
| 2018-05 | 6056 | 6056 | 9.0096 | 0.0913 | 6031 | 0.1108 |

![trends](figures/outcome_trends.png)

## Numeric features vs lead_days (3.4)

| feature | n | pearson | spearman | feature_missing_share | feature_skewness |
| --- | --- | --- | --- | --- | --- |
| distance_km_max | 76249 | 0.4088 | 0.5393 | 0.0115 | 1.6442 |
| interstate_share | 77139 | 0.3828 | 0.4982 | 0.0000 | -0.6348 |
| total_freight | 77139 | 0.1912 | 0.4048 | 0.0000 | 8.1219 |
| freight_ratio | 77139 | 0.0904 | 0.1317 | 0.0000 | 10.9982 |
| total_price | 77139 | 0.0574 | 0.0935 | 0.0000 | 10.1167 |
| total_weight_g | 77123 | 0.0678 | 0.0774 | 0.0002 | 6.6201 |
| total_volume_cm3 | 77123 | 0.0571 | 0.0579 | 0.0002 | 7.3868 |
| n_sellers | 77139 | -0.0423 | -0.0487 | 0.0000 | 10.1057 |
| payment_installments_max | 77139 | 0.0530 | 0.0476 | 0.0000 | 1.5904 |
| purchase_dayofweek | 77139 | 0.0290 | 0.0437 | 0.0000 | 0.1589 |
| n_products | 77139 | -0.0343 | -0.0395 | 0.0000 | 7.7036 |
| purchase_month | 77139 | -0.0225 | -0.0311 | 0.0000 | 0.3731 |
| n_items | 77139 | -0.0213 | -0.0275 | 0.0000 | 7.8378 |
| n_categories | 77139 | -0.0116 | -0.0130 | 0.0000 | -2.1460 |
| distance_missing_fraction | 77139 | 0.0053 | 0.0098 | 0.0000 | 9.1802 |
| category_missing_fraction | 77139 | -0.0056 | -0.0060 | 0.0000 | 7.5937 |
| n_payment_methods | 77139 | -0.0010 | 0.0029 | 0.0000 | 6.3189 |
| volume_missing_fraction | 77139 | -0.0019 | -0.0022 | 0.0000 | 69.4145 |
| weight_missing_fraction | 77139 | -0.0019 | -0.0022 | 0.0000 | 69.4145 |
| purchase_hour | 77139 | 0.0013 | 0.0016 | 0.0000 | -0.6059 |

![scatter](figures/numeric_vs_lead_days.png)

## Categorical features vs lead_days (3.5)

Rank correlation ratio per categorical feature: customer_state 0.5045, primary_seller_state 0.0910, primary_category 0.1454, primary_payment_type 0.0716. Per-level medians, IQR and drop-first dummy correlations: categorical_feature_target_lead_days.csv.

![violins](figures/categorical_vs_lead_days.png)

## Missingness and outliers (3.8)

| feature | type | missing_share | share_outside_1_5_iqr | share_outside_3_iqr | vif | vif_note |
| --- | --- | --- | --- | --- | --- | --- |
| n_items | numeric | 0.0000 | 0.1011 | 0.1011 | 1.6587 |  |
| n_products | numeric | 0.0000 | 0.0331 | 0.0331 | 1.7987 |  |
| n_sellers | numeric | 0.0000 | 0.0123 | 0.0123 | 1.8544 |  |
| n_categories | numeric | 0.0000 | 0.0232 | 0.0232 | 4.8112 |  |
| total_price | numeric | 0.0000 | 0.0794 | 0.0406 | 1.4761 |  |
| total_freight | numeric | 0.0000 | 0.0963 | 0.0485 | 3.3380 |  |
| freight_ratio | numeric | 0.0000 | 0.0680 | 0.0229 | 1.2601 |  |
| total_weight_g | numeric | 0.0002 | 0.1410 | 0.0829 | 3.6120 |  |
| total_volume_cm3 | numeric | 0.0002 | 0.0977 | 0.0432 | 3.4731 |  |
| weight_missing_fraction | numeric | 0.0000 | 0.0002 | 0.0002 |  | constant on the complete rows |
| volume_missing_fraction | numeric | 0.0000 | 0.0002 | 0.0002 |  | constant on the complete rows |
| primary_category | categorical | 0.0000 |  |  |  |  |
| category_missing_fraction | numeric | 0.0000 | 0.0169 | 0.0169 | 4.2629 |  |
| customer_state | categorical | 0.0000 |  |  |  |  |
| primary_seller_state | categorical | 0.0000 |  |  |  |  |
| distance_km_max | numeric | 0.0115 | 0.0796 | 0.0069 | 1.6851 |  |
| distance_missing_fraction | numeric | 0.0000 | 0.0115 | 0.0115 |  | constant on the complete rows |
| interstate_share | numeric | 0.0000 | 0.0000 | 0.0000 | 1.5004 |  |
| purchase_month | numeric | 0.0000 | 0.0000 | 0.0000 | 1.0031 |  |
| purchase_dayofweek | numeric | 0.0000 | 0.0000 | 0.0000 | 1.0020 |  |
| purchase_hour | numeric | 0.0000 | 0.0000 | 0.0000 | 1.0007 |  |
| primary_payment_type | categorical | 0.0000 |  |  |  |  |
| payment_installments_max | numeric | 0.0000 | 0.0667 | 0.0017 | 1.1552 |  |
| n_payment_methods | numeric | 0.0000 | 0.0233 | 0.0233 | 1.0023 |  |

## Skewness of the log1p candidates (3.8, for s04 4.2)

| feature | skewness | threshold | log1p |
| --- | --- | --- | --- |
| total_price | 10.1167 | 1.0000 | True |
| total_freight | 8.1219 | 1.0000 | True |
| total_weight_g | 6.6201 | 1.0000 | True |
| total_volume_cm3 | 7.3868 | 1.0000 | True |
| distance_km_max | 1.6442 | 1.0000 | True |

## Importance ranking (3.8)

Measure: absolute Spearman. All 24 contract predictors.

| rank | feature | type | method | value | share | cumulative_share |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | distance_km_max | numeric | |Spearman| | 0.5393 | 0.1865 | 0.1865 |
| 2 | customer_state | categorical | rank correlation ratio (Spearman scale) | 0.5045 | 0.1745 | 0.3610 |
| 3 | interstate_share | numeric | |Spearman| | 0.4982 | 0.1723 | 0.5333 |
| 4 | total_freight | numeric | |Spearman| | 0.4048 | 0.1400 | 0.6734 |
| 5 | primary_category | categorical | rank correlation ratio (Spearman scale) | 0.1454 | 0.0503 | 0.7237 |
| 6 | freight_ratio | numeric | |Spearman| | 0.1317 | 0.0455 | 0.7692 |
| 7 | total_price | numeric | |Spearman| | 0.0935 | 0.0323 | 0.8015 |
| 8 | primary_seller_state | categorical | rank correlation ratio (Spearman scale) | 0.0910 | 0.0315 | 0.8330 |
| 9 | total_weight_g | numeric | |Spearman| | 0.0774 | 0.0268 | 0.8598 |
| 10 | primary_payment_type | categorical | rank correlation ratio (Spearman scale) | 0.0716 | 0.0248 | 0.8846 |
| 11 | total_volume_cm3 | numeric | |Spearman| | 0.0579 | 0.0200 | 0.9046 |
| 12 | n_sellers | numeric | |Spearman| | 0.0487 | 0.0168 | 0.9214 |
| 13 | payment_installments_max | numeric | |Spearman| | 0.0476 | 0.0165 | 0.9379 |
| 14 | purchase_dayofweek | numeric | |Spearman| | 0.0437 | 0.0151 | 0.9530 |
| 15 | n_products | numeric | |Spearman| | 0.0395 | 0.0137 | 0.9667 |
| 16 | purchase_month | numeric | |Spearman| | 0.0311 | 0.0108 | 0.9774 |
| 17 | n_items | numeric | |Spearman| | 0.0275 | 0.0095 | 0.9869 |
| 18 | n_categories | numeric | |Spearman| | 0.0130 | 0.0045 | 0.9914 |
| 19 | distance_missing_fraction | numeric | |Spearman| | 0.0098 | 0.0034 | 0.9948 |
| 20 | category_missing_fraction | numeric | |Spearman| | 0.0060 | 0.0021 | 0.9969 |
| 21 | n_payment_methods | numeric | |Spearman| | 0.0029 | 0.0010 | 0.9979 |
| 22 | volume_missing_fraction | numeric | |Spearman| | 0.0022 | 0.0008 | 0.9987 |
| 23 | weight_missing_fraction | numeric | |Spearman| | 0.0022 | 0.0008 | 0.9994 |
| 24 | purchase_hour | numeric | |Spearman| | 0.0016 | 0.0006 | 1.0000 |

![cumulative importance](figures/cumulative_importance.png)

| Threshold option | Features kept (top k) | Features kept |
| --- | --- | --- |
| 95% | 14 | distance_km_max, customer_state, interstate_share, total_freight, primary_category, freight_ratio, total_price, primary_seller_state, total_weight_g, primary_payment_type, total_volume_cm3, n_sellers, payment_installments_max, purchase_dayofweek |
| 99% | 18 | distance_km_max, customer_state, interstate_share, total_freight, primary_category, freight_ratio, total_price, primary_seller_state, total_weight_g, primary_payment_type, total_volume_cm3, n_sellers, payment_installments_max, purchase_dayofweek, n_products, purchase_month, n_items, n_categories |

## Collinearity among raw numeric features (3.8)

Cut-offs from protocol.yaml: |correlation| > 0.9 (Pearson or Spearman) or VIF > 10; VIF on 76,233 complete rows (a column constant on those rows has no VIF). Nothing is dropped in s03.

Identical columns (dropped automatically in s04 4.3, no team decision needed): weight_missing_fraction = volume_missing_fraction.

No group needs a team decision: no pair of distinct columns above the correlation cut-off and no VIF above the VIF cut-off.

| feature_a | feature_b | pearson | spearman | identical |
| --- | --- | --- | --- | --- |
| weight_missing_fraction | volume_missing_fraction | 1.0000 | 1.0000 | True |

![correlation heatmap](figures/numeric_correlation_heatmap.png)

## Decisions for the team (record in spec/human_decisions.yaml)

```yaml
s03_to_s04:
  regression:
    cumulative_importance_threshold: 0.95   # or 0.99
    collinearity_drops:
```
