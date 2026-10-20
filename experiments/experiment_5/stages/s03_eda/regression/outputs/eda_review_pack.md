# EDA review pack: s03_eda/regression

Human gate before s04 (G-31). Every table and figure of this node is listed below; the team records its decisions in `spec/human_decisions.yaml` (section `s03_to_s04.regression`), logged in CHANGELOG.md. s04 does not run until both are recorded.

Rows: 76,925 eligible regression orders purchased before the test cutoff 2018-05-27 12:30:34 (latest purchase used 2018-05-27 12:20:21).

## Target: lead_days (3.1)

| statistic | value |
| --- | --- |
| count | 76,925.0000 |
| missing_share | 0.0000 |
| mean | 13.4173 |
| sd | 9.4467 |
| min | 0.5334 |
| p1 | 1.8980 |
| p5 | 3.2248 |
| p25 | 7.2119 |
| p50 | 11.1721 |
| p75 | 16.9355 |
| p95 | 31.0790 |
| p99 | 47.2877 |
| max | 133.2411 |
| skewness | 2.4060 |
| kurtosis | 11.6358 |

![lead_days KDE](figures/target_lead_days_kde.png)

## Outcome trends (3.3)

| month | orders | orders_with_lead_time | median_lead_days | late_vs_promised_rate | orders_with_review | detractor_rate |
| --- | --- | --- | --- | --- | --- | --- |
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
| 2018-05 | 6108 | 6108 | 9.0224 | 0.0907 | 6082 | 0.1107 |

![trends](figures/outcome_trends.png)

## Numeric features vs lead_days (3.4)

| feature | n | pearson | spearman | feature_missing_share | feature_skewness |
| --- | --- | --- | --- | --- | --- |
| distance_km_max | 76035 | 0.4102 | 0.5411 | 0.0116 | 1.6439 |
| interstate_share | 76925 | 0.3843 | 0.4996 | 0.0000 | -0.6343 |
| total_freight | 76925 | 0.1913 | 0.4057 | 0.0000 | 8.1328 |
| freight_ratio | 76925 | 0.0908 | 0.1321 | 0.0000 | 11.0080 |
| total_price | 76925 | 0.0573 | 0.0935 | 0.0000 | 10.1346 |
| total_weight_g | 76909 | 0.0672 | 0.0768 | 0.0002 | 6.6257 |
| total_volume_cm3 | 76909 | 0.0565 | 0.0573 | 0.0002 | 7.3965 |
| n_sellers | 76925 | -0.0421 | -0.0484 | 0.0000 | 10.1107 |
| payment_installments_max | 76925 | 0.0532 | 0.0475 | 0.0000 | 1.5928 |
| purchase_dayofweek | 76925 | 0.0303 | 0.0446 | 0.0000 | 0.1576 |
| n_products | 76925 | -0.0345 | -0.0397 | 0.0000 | 7.6784 |
| purchase_month | 76925 | -0.0252 | -0.0338 | 0.0000 | 0.3823 |
| n_items | 76925 | -0.0216 | -0.0278 | 0.0000 | 7.8507 |
| n_categories | 76925 | -0.0116 | -0.0130 | 0.0000 | -2.1501 |
| distance_missing_fraction | 76925 | 0.0055 | 0.0101 | 0.0000 | 9.1670 |
| category_missing_fraction | 76925 | -0.0054 | -0.0060 | 0.0000 | 7.5889 |
| n_payment_methods | 76925 | -0.0010 | 0.0031 | 0.0000 | 6.3189 |
| volume_missing_fraction | 76925 | -0.0019 | -0.0022 | 0.0000 | 69.3181 |
| weight_missing_fraction | 76925 | -0.0019 | -0.0022 | 0.0000 | 69.3181 |
| purchase_hour | 76925 | 0.0017 | 0.0019 | 0.0000 | -0.6069 |

![scatter](figures/numeric_vs_lead_days.png)

## Categorical features vs lead_days (3.5)

Rank correlation ratio per categorical feature: customer_state 0.5059, primary_seller_state 0.0913, primary_category 0.1459, primary_payment_type 0.0718. Per-level medians, IQR and drop-first dummy correlations: categorical_feature_target_lead_days.csv.

![violins](figures/categorical_vs_lead_days.png)

## Missingness and outliers (3.8)

| feature | type | missing_share | share_outside_1_5_iqr | share_outside_3_iqr | vif | vif_note |
| --- | --- | --- | --- | --- | --- | --- |
| n_items | numeric | 0.0000 | 0.1010 | 0.1010 | 1.6561 |  |
| n_products | numeric | 0.0000 | 0.0331 | 0.0331 | 1.7986 |  |
| n_sellers | numeric | 0.0000 | 0.0123 | 0.0123 | 1.8567 |  |
| n_categories | numeric | 0.0000 | 0.0232 | 0.0232 | 4.8207 |  |
| total_price | numeric | 0.0000 | 0.0792 | 0.0405 | 1.4757 |  |
| total_freight | numeric | 0.0000 | 0.0963 | 0.0484 | 3.3341 |  |
| freight_ratio | numeric | 0.0000 | 0.0681 | 0.0229 | 1.2601 |  |
| total_weight_g | numeric | 0.0002 | 0.1409 | 0.0829 | 3.6094 |  |
| total_volume_cm3 | numeric | 0.0002 | 0.0976 | 0.0431 | 3.4727 |  |
| weight_missing_fraction | numeric | 0.0000 | 0.0002 | 0.0002 |  | constant on the complete rows |
| volume_missing_fraction | numeric | 0.0000 | 0.0002 | 0.0002 |  | constant on the complete rows |
| primary_category | categorical | 0.0000 |  |  |  |  |
| category_missing_fraction | numeric | 0.0000 | 0.0169 | 0.0169 | 4.2713 |  |
| customer_state | categorical | 0.0000 |  |  |  |  |
| primary_seller_state | categorical | 0.0000 |  |  |  |  |
| distance_km_max | numeric | 0.0116 | 0.0795 | 0.0069 | 1.6848 |  |
| distance_missing_fraction | numeric | 0.0000 | 0.0116 | 0.0116 |  | constant on the complete rows |
| interstate_share | numeric | 0.0000 | 0.0000 | 0.0000 | 1.5008 |  |
| purchase_month | numeric | 0.0000 | 0.0000 | 0.0000 | 1.0030 |  |
| purchase_dayofweek | numeric | 0.0000 | 0.0000 | 0.0000 | 1.0020 |  |
| purchase_hour | numeric | 0.0000 | 0.0000 | 0.0000 | 1.0007 |  |
| primary_payment_type | categorical | 0.0000 |  |  |  |  |
| payment_installments_max | numeric | 0.0000 | 0.0664 | 0.0017 | 1.1550 |  |
| n_payment_methods | numeric | 0.0000 | 0.0233 | 0.0233 | 1.0023 |  |

## Skewness of the log1p candidates (3.8, for s04 4.2)

| feature | skewness | threshold | log1p |
| --- | --- | --- | --- |
| total_price | 10.1346 | 1.0000 | True |
| total_freight | 8.1328 | 1.0000 | True |
| total_weight_g | 6.6257 | 1.0000 | True |
| total_volume_cm3 | 7.3965 | 1.0000 | True |
| distance_km_max | 1.6439 | 1.0000 | True |

## Importance ranking (3.8)

Measure: absolute Spearman. All 24 contract predictors.

| rank | feature | type | method | value | share | cumulative_share |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | distance_km_max | numeric | |Spearman| | 0.5411 | 0.1865 | 0.1865 |
| 2 | customer_state | categorical | rank correlation ratio (Spearman scale) | 0.5059 | 0.1744 | 0.3609 |
| 3 | interstate_share | numeric | |Spearman| | 0.4996 | 0.1722 | 0.5331 |
| 4 | total_freight | numeric | |Spearman| | 0.4057 | 0.1398 | 0.6729 |
| 5 | primary_category | categorical | rank correlation ratio (Spearman scale) | 0.1459 | 0.0503 | 0.7232 |
| 6 | freight_ratio | numeric | |Spearman| | 0.1321 | 0.0455 | 0.7688 |
| 7 | total_price | numeric | |Spearman| | 0.0935 | 0.0322 | 0.8010 |
| 8 | primary_seller_state | categorical | rank correlation ratio (Spearman scale) | 0.0913 | 0.0315 | 0.8325 |
| 9 | total_weight_g | numeric | |Spearman| | 0.0768 | 0.0265 | 0.8589 |
| 10 | primary_payment_type | categorical | rank correlation ratio (Spearman scale) | 0.0718 | 0.0248 | 0.8837 |
| 11 | total_volume_cm3 | numeric | |Spearman| | 0.0573 | 0.0197 | 0.9035 |
| 12 | n_sellers | numeric | |Spearman| | 0.0484 | 0.0167 | 0.9202 |
| 13 | payment_installments_max | numeric | |Spearman| | 0.0475 | 0.0164 | 0.9365 |
| 14 | purchase_dayofweek | numeric | |Spearman| | 0.0446 | 0.0154 | 0.9519 |
| 15 | n_products | numeric | |Spearman| | 0.0397 | 0.0137 | 0.9656 |
| 16 | purchase_month | numeric | |Spearman| | 0.0338 | 0.0116 | 0.9772 |
| 17 | n_items | numeric | |Spearman| | 0.0278 | 0.0096 | 0.9868 |
| 18 | n_categories | numeric | |Spearman| | 0.0130 | 0.0045 | 0.9913 |
| 19 | distance_missing_fraction | numeric | |Spearman| | 0.0101 | 0.0035 | 0.9947 |
| 20 | category_missing_fraction | numeric | |Spearman| | 0.0060 | 0.0021 | 0.9968 |
| 21 | n_payment_methods | numeric | |Spearman| | 0.0031 | 0.0011 | 0.9979 |
| 22 | volume_missing_fraction | numeric | |Spearman| | 0.0022 | 0.0007 | 0.9986 |
| 23 | weight_missing_fraction | numeric | |Spearman| | 0.0022 | 0.0007 | 0.9994 |
| 24 | purchase_hour | numeric | |Spearman| | 0.0019 | 0.0006 | 1.0000 |

![cumulative importance](figures/cumulative_importance.png)

| Threshold option | Features kept (top k) | Features kept |
| --- | --- | --- |
| 95% | 14 | distance_km_max, customer_state, interstate_share, total_freight, primary_category, freight_ratio, total_price, primary_seller_state, total_weight_g, primary_payment_type, total_volume_cm3, n_sellers, payment_installments_max, purchase_dayofweek |
| 99% | 18 | distance_km_max, customer_state, interstate_share, total_freight, primary_category, freight_ratio, total_price, primary_seller_state, total_weight_g, primary_payment_type, total_volume_cm3, n_sellers, payment_installments_max, purchase_dayofweek, n_products, purchase_month, n_items, n_categories |

## Collinearity among raw numeric features (3.8)

Cut-offs from protocol.yaml: |correlation| > 0.9 (Pearson or Spearman) or VIF > 10; VIF on 76,019 complete rows (a column constant on those rows has no VIF). Nothing is dropped in s03.

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
