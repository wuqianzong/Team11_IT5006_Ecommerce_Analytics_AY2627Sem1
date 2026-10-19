# s03 EDA › regression

> **How to read this tab.** Part A is the final, accepted result (run `20261019T163336Z`, CR-042; every value identical to the round 3 acceptance). Part B keeps the review record of rounds 1–3 for the discussion and comment threads.

# Part A — Final result (accepted, cite this)

Run `20261019T163336Z` on commit aca98ac (clean tree) · 6 solution steps IMPLEMENTED · 6 checks, all PASS. Regression pool = the 24 contract predictors (`e5lib.contract.pool("regression")`); threshold 99%; no collinearity drop (G-70).

## 3.1 Regression target

**Approved solution:** `lead_days` KDE; count, mean, SD, min, 1/5/25/50/75/95/99%, max, skewness, kurtosis

**What was done:** lead\_days profile on 77,139 pre-cutoff orders: median 11.18, mean 13.44, SD 9.46, p99 47.38, max 133.24 days; skewness 2.40, excess kurtosis 11.55.

**Conclusion:** Right-skewed target: supports the pre-registered log1p target (G-36).

| statistic | value |
| --- | --- |
| count | 77,139.0000 |
| missing\_share | 0.0000 |
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

&#91;image: lead\_days KDE\]

**Check** no order on or after the test cutoff loaded: PASS (latest purchase 2018-05-26 18:16:57, cutoff 2018-05-26 18:18:03)

**Files** (stages/s03\_eda/regression/outputs/, run 20261019T163336Z): target\_regression\_lead\_days.csv, figures/target\_lead\_days\_kde.png, figures/target\_lead\_days\_kde.csv, figures/target\_lead\_days\_kde.json, eda\_summary.json

## 3.3 Outcome trends

**Approved solution:** By purchase month: median lead time, late-vs-promised rate, detractor rate, with counts (not volume only)

**What was done:** 19 purchase months; over the 18 months with at least 100 orders: median lead time 9.0 to 17.9 days, late-vs-promised rate 1.1% to 21.4%, detractor rate 9.5% to 21.2%; every month is in the table with its counts.

**Reasoning:** Late is delivery after order\_estimated\_delivery\_date, used here only as a description (G-35).

| month | orders | orders\_with\_lead\_time | median\_lead\_days | late\_vs\_promised\_rate | orders\_with\_review | detractor\_rate |
| --- | --- | --- | --- | --- | --- | --- |
| 2016-10 | 265 | 265 | 17.944 | 0.011 | 262 | 0.164 |
| 2016-12 | 1 | 1 | 4.693 | 0.000 | 1 | 0.000 |
| 2017-01 | 750 | 750 | 10.734 | 0.031 | 741 | 0.120 |
| 2017-02 | 1,651 | 1,651 | 10.964 | 0.031 | 1,642 | 0.110 |
| 2017-03 | 2,535 | 2,535 | 10.108 | 0.052 | 2,516 | 0.113 |
| 2017-04 | 2,296 | 2,296 | 12.721 | 0.076 | 2,284 | 0.128 |
| 2017-05 | 3,543 | 3,543 | 9.789 | 0.036 | 3,515 | 0.101 |
| 2017-06 | 3,133 | 3,133 | 10.802 | 0.038 | 3,109 | 0.108 |
| 2017-07 | 3,872 | 3,872 | 10.158 | 0.034 | 3,842 | 0.101 |
| 2017-08 | 4,193 | 4,193 | 9.770 | 0.033 | 4,165 | 0.095 |
| 2017-09 | 4,150 | 4,150 | 10.314 | 0.052 | 4,118 | 0.103 |
| 2017-10 | 4,478 | 4,478 | 10.263 | 0.053 | 4,446 | 0.111 |
| 2017-11 | 7,284 | 7,284 | 12.692 | 0.143 | 7,233 | 0.166 |
| 2017-12 | 5,512 | 5,512 | 13.142 | 0.084 | 5,460 | 0.145 |
| 2018-01 | 7,068 | 7,068 | 11.829 | 0.066 | 7,012 | 0.137 |
| 2018-02 | 6,552 | 6,552 | 14.263 | 0.159 | 6,504 | 0.194 |
| 2018-03 | 7,003 | 7,003 | 13.368 | 0.214 | 6,948 | 0.212 |
| 2018-04 | 6,797 | 6,797 | 9.315 | 0.053 | 6,751 | 0.118 |
| 2018-05 | 6,056 | 6,056 | 9.010 | 0.091 | 6,031 | 0.111 |

&#91;image: Outcome trends\]

**Check** no order on or after the test cutoff loaded: PASS (latest purchase 2018-05-26 18:16:57, cutoff 2018-05-26 18:18:03) **Check** outcome trends show outcomes, not volume only: PASS

**Files** (stages/s03\_eda/regression/outputs/, run 20261019T163336Z): outcome\_trends.csv, figures/outcome\_trends.png, figures/outcome\_trends.csv, figures/outcome\_trends.json, eda\_summary.json

## 3.4 Numeric features vs lead\_days

**Approved solution:** Scatter plot per feature; Pearson **and** Spearman (skewed features); full percentile profile; sorted by absolute correlation

**What was done:** 20 numeric predictors: Pearson and Spearman with lead\_days on the rows where the feature is present, plus each feature's percentile profile; strongest |Spearman|: distance\_km\_max (0.539). Scatter panels use 2,000 random orders each (seed 42); log1p x-axis for the five log1p candidates (plot only).

| feature | n | pearson | spearman | feature\_missing\_share | feature\_p50 | feature\_p99 | feature\_skewness |
| --- | --- | --- | --- | --- | --- | --- | --- |
| distance\_km\_max | 76,249 | 0.4088 | 0.5393 | 0.0115 | 443.8695 | 2,484.1965 | 1.6442 |
| interstate\_share | 77,139 | 0.3828 | 0.4982 | 0.0000 | 1.0000 | 1.0000 | -0.6348 |
| total\_freight | 77,139 | 0.1912 | 0.4048 | 0.0000 | 16.7900 | 100.9344 | 8.1219 |
| freight\_ratio | 77,139 | 0.0904 | 0.1317 | 0.0000 | 0.2223 | 1.4412 | 10.9982 |
| total\_price | 77,139 | 0.0574 | 0.0935 | 0.0000 | 86.9000 | 989.9962 | 10.1167 |
| total\_weight\_g | 77,123 | 0.0678 | 0.0774 | 0.0002 | 800.0000 | 22,644.5000 | 6.6201 |
| total\_volume\_cm3 | 77,123 | 0.0571 | 0.0579 | 0.0002 | 7,632.0000 | 140,000.0000 | 7.3868 |
| n\_sellers | 77,139 | -0.0423 | -0.0487 | 0.0000 | 1.0000 | 2.0000 | 10.1057 |
| payment\_installments\_max | 77,139 | 0.0530 | 0.0476 | 0.0000 | 2.0000 | 10.0000 | 1.5904 |
| purchase\_dayofweek | 77,139 | 0.0290 | 0.0437 | 0.0000 | 3.0000 | 6.0000 | 0.1589 |
| n\_products | 77,139 | -0.0343 | -0.0395 | 0.0000 | 1.0000 | 2.0000 | 7.7036 |
| purchase\_month | 77,139 | -0.0225 | -0.0311 | 0.0000 | 5.0000 | 12.0000 | 0.3731 |
| n\_items | 77,139 | -0.0213 | -0.0275 | 0.0000 | 1.0000 | 3.0000 | 7.8378 |
| n\_categories | 77,139 | -0.0116 | -0.0130 | 0.0000 | 1.0000 | 1.0000 | -2.1460 |
| distance\_missing\_fraction | 77,139 | 0.0053 | 0.0098 | 0.0000 | 0.0000 | 1.0000 | 9.1802 |
| category\_missing\_fraction | 77,139 | -0.0056 | -0.0060 | 0.0000 | 0.0000 | 1.0000 | 7.5937 |
| n\_payment\_methods | 77,139 | -0.0010 | 0.0029 | 0.0000 | 1.0000 | 2.0000 | 6.3189 |
| volume\_missing\_fraction | 77,139 | -0.0019 | -0.0022 | 0.0000 | 0.0000 | 0.0000 | 69.4145 |
| weight\_missing\_fraction | 77,139 | -0.0019 | -0.0022 | 0.0000 | 0.0000 | 0.0000 | 69.4145 |
| purchase\_hour | 77,139 | 0.0013 | 0.0016 | 0.0000 | 15.0000 | 23.0000 | -0.6059 |

&#91;image: Numeric features vs lead\_days\]

**Check** all 24 contract predictors diagnosed against lead\_days: PASS

**Files** (stages/s03\_eda/regression/outputs/, run 20261019T163336Z): numeric\_feature\_target\_lead\_days.csv, figures/numeric\_vs\_lead\_days.png, figures/numeric\_vs\_lead\_days.csv, figures/numeric\_vs\_lead\_days.json

## 3.5 Categorical features vs lead\_days

**Approved solution:** Violin plots (median, IQR, outliers); one-hot (drop-first) correlations; calendar fields treated as categorical for plots only

**What was done:** Four categorical predictors: per-level median, IQR and mean of lead\_days, drop-first dummy correlations (reference level = first in sorted order), and one rank correlation ratio per feature; the three calendar fields are shown per level for the plots only and stay numeric.

**Reasoning:** Spearman needs an ordered feature, so a nominal feature gets the rank correlation ratio (square root of the Kruskal-Wallis epsilon-squared): the same 0-1 scale as |Spearman| on the ranked target. Flagged for the team to confirm (decision 1).

| feature | levels | rank\_correlation\_ratio | lowest\_median | highest\_median |
| --- | --- | --- | --- | --- |
| customer\_state | 27 | 0.5045 | 7.8524 | 27.0878 |
| primary\_category | 72 | 0.1454 | 5.0995 | 18.8395 |
| primary\_seller\_state | 22 | 0.0910 | 9.0058 | 29.5235 |
| primary\_payment\_type | 4 | 0.0716 | 10.1591 | 12.2566 |

**customer\_state** (top 15 of 27 levels by count; all levels in categorical\_feature\_target\_lead\_days.csv)

| level | n | share | target\_median | target\_q1 | target\_q3 | dummy | dummy\_correlation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SP | 31,566 | 0.409 | 7.852 | 5.126 | 11.775 | kept | -0.358 |
| RJ | 10,135 | 0.131 | 13.105 | 9.038 | 20.001 | kept | 0.126 |
| MG | 9,220 | 0.120 | 11.245 | 8.141 | 15.582 | kept | -0.023 |
| RS | 4,403 | 0.057 | 14.118 | 10.134 | 19.889 | kept | 0.071 |
| PR | 3,945 | 0.051 | 11.203 | 8.091 | 15.434 | kept | -0.015 |
| SC | 2,926 | 0.038 | 14.157 | 10.081 | 19.942 | kept | 0.055 |
| BA | 2,611 | 0.034 | 18.052 | 13.369 | 24.225 | kept | 0.133 |
| ES | 1,632 | 0.021 | 14.255 | 10.341 | 19.908 | kept | 0.044 |
| DF | 1,613 | 0.021 | 12.379 | 9.046 | 17.239 | kept | 0.009 |
| GO | 1,609 | 0.021 | 14.691 | 11.107 | 19.555 | kept | 0.044 |
| PE | 1,270 | 0.016 | 17.210 | 13.051 | 23.714 | kept | 0.086 |
| CE | 1,062 | 0.014 | 19.670 | 14.944 | 26.790 | kept | 0.114 |
| PA | 786 | 0.010 | 22.661 | 16.867 | 30.601 | kept | 0.125 |
| MT | 734 | 0.010 | 17.189 | 13.359 | 22.084 | kept | 0.058 |
| MA | 601 | 0.008 | 19.787 | 15.269 | 25.361 | kept | 0.081 |

**primary\_seller\_state** (top 15 of 22 levels by count; all levels in categorical\_feature\_target\_lead\_days.csv)

| level | n | share | target\_median | target\_q1 | target\_q3 | dummy | dummy\_correlation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SP | 54,904 | 0.712 | 10.978 | 6.973 | 16.971 | kept | -0.029 |
| MG | 6,294 | 0.082 | 11.579 | 7.773 | 16.578 | kept | 0.004 |
| PR | 5,996 | 0.078 | 12.164 | 8.357 | 17.278 | kept | 0.028 |
| RJ | 3,146 | 0.041 | 10.998 | 7.185 | 16.369 | kept | -0.006 |
| SC | 2,867 | 0.037 | 12.453 | 8.970 | 17.566 | kept | 0.026 |
| RS | 1,459 | 0.019 | 10.242 | 7.014 | 14.766 | kept | -0.018 |
| DF | 657 | 0.009 | 11.063 | 7.875 | 15.760 | kept | -0.005 |
| BA | 426 | 0.006 | 12.070 | 9.117 | 17.249 | kept | 0.006 |
| GO | 344 | 0.004 | 12.075 | 8.364 | 16.925 | kept | 0.003 |
| PE | 294 | 0.004 | 12.142 | 9.049 | 16.816 | kept | 0.002 |
| ES | 266 | 0.003 | 11.549 | 8.604 | 15.602 | kept | 0.000 |
| MA | 163 | 0.002 | 19.386 | 15.579 | 29.139 | kept | 0.044 |
| MT | 115 | 0.001 | 13.094 | 10.747 | 17.295 | kept | 0.007 |
| CE | 59 | 0.001 | 15.243 | 11.381 | 21.653 | kept | 0.012 |
| RN | 45 | 0.001 | 9.006 | 5.052 | 21.913 | kept | 0.001 |

**primary\_payment\_type**

| level | n | share | target\_median | target\_q1 | target\_q3 | dummy | dummy\_correlation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| credit\_card | 58,205 | 0.755 | 10.973 | 7.058 | 16.760 | kept | -0.038 |
| boleto | 15,658 | 0.203 | 12.257 | 8.135 | 17.848 | dropped (reference) | — |
| voucher | 2,484 | 0.032 | 11.066 | 7.190 | 16.391 | kept | -0.006 |
| debit\_card | 792 | 0.010 | 10.159 | 6.521 | 16.205 | kept | -0.009 |

**primary\_category** (top 15 of 72 levels by count; all levels in categorical\_feature\_target\_lead\_days.csv)

| level | n | share | target\_median | target\_q1 | target\_q3 | dummy | dummy\_correlation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bed\_bath\_table | 7,405 | 0.096 | 11.919 | 8.018 | 17.524 | kept | 0.022 |
| health\_beauty | 6,310 | 0.082 | 10.505 | 6.824 | 16.499 | kept | -0.009 |
| sports\_leisure | 6,233 | 0.081 | 11.038 | 7.140 | 16.130 | kept | -0.013 |
| computers\_accessories | 5,367 | 0.070 | 11.966 | 7.879 | 17.406 | kept | 0.015 |
| furniture\_decor | 5,183 | 0.067 | 11.471 | 7.661 | 17.439 | kept | 0.011 |
| housewares | 4,160 | 0.054 | 10.154 | 6.522 | 15.332 | kept | -0.031 |
| watches\_gifts | 4,089 | 0.053 | 11.343 | 7.654 | 17.531 | kept | 0.011 |
| telephony | 3,397 | 0.044 | 11.449 | 7.300 | 17.251 | kept | 0.003 |
| toys | 3,290 | 0.043 | 10.002 | 6.578 | 15.114 | kept | -0.025 |
| cool\_stuff | 3,190 | 0.041 | 10.861 | 7.001 | 15.365 | kept | -0.020 |
| garden\_tools | 2,964 | 0.038 | 12.328 | 8.472 | 17.755 | kept | 0.020 |
| auto | 2,838 | 0.037 | 10.814 | 6.970 | 16.737 | kept | 0.000 |
| perfumery | 2,521 | 0.033 | 10.402 | 6.420 | 15.951 | kept | -0.014 |
| baby | 2,125 | 0.028 | 11.105 | 7.050 | 17.268 | kept | 0.006 |
| electronics | 2,058 | 0.027 | 12.054 | 7.816 | 17.953 | kept | 0.009 |

&#91;image: Categorical features vs lead\_days\]

**Check** all 24 contract predictors diagnosed against lead\_days: PASS

**Files** (stages/s03\_eda/regression/outputs/, run 20261019T163336Z): categorical\_feature\_target\_lead\_days.csv, figures/categorical\_vs\_lead\_days.png, figures/categorical\_vs\_lead\_days.csv, figures/categorical\_vs\_lead\_days.json

## 3.8 Importance ranking

**Approved solution:** One ranking per task feeding s04 selection, over all 24 contract predictors (the ranking file has exactly 24 rows; G-42, G-61): absolute Spearman for regression, mutual information for classification (one measure per task, so cumulative shares are meaningful). Missingness, outliers and correlation/VIF among raw numeric features also reported here

**What was done:** Ranking over the 24 contract predictors by absolute Spearman (rank correlation ratio for the four categorical ones): top 5 \['distance\_km\_max', 'customer\_state', 'interstate\_share', 'total\_freight', 'primary\_category'\]; cut points {'0.95': 14, '0.99': 18} (features needed for each cumulative share). Missingness, IQR outliers, Pearson/Spearman matrix and VIF on 76,233 complete rows; flagged groups: \[\]; identical columns: \[('weight\_missing\_fraction', 'volume\_missing\_fraction')\].

**Ranking** (absolute Spearman):

| rank | feature | type | method | value | share | cumulative\_share |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | distance\_km\_max | numeric | /Spearman/ | 0.5393 | 0.1865 | 0.1865 |
| 2 | customer\_state | categorical | rank correlation ratio (Spearman scale) | 0.5045 | 0.1745 | 0.3610 |
| 3 | interstate\_share | numeric | /Spearman/ | 0.4982 | 0.1723 | 0.5333 |
| 4 | total\_freight | numeric | /Spearman/ | 0.4048 | 0.1400 | 0.6734 |
| 5 | primary\_category | categorical | rank correlation ratio (Spearman scale) | 0.1454 | 0.0503 | 0.7237 |
| 6 | freight\_ratio | numeric | /Spearman/ | 0.1317 | 0.0455 | 0.7692 |
| 7 | total\_price | numeric | /Spearman/ | 0.0935 | 0.0323 | 0.8015 |
| 8 | primary\_seller\_state | categorical | rank correlation ratio (Spearman scale) | 0.0910 | 0.0315 | 0.8330 |
| 9 | total\_weight\_g | numeric | /Spearman/ | 0.0774 | 0.0268 | 0.8598 |
| 10 | primary\_payment\_type | categorical | rank correlation ratio (Spearman scale) | 0.0716 | 0.0248 | 0.8846 |
| 11 | total\_volume\_cm3 | numeric | /Spearman/ | 0.0579 | 0.0200 | 0.9046 |
| 12 | n\_sellers | numeric | /Spearman/ | 0.0487 | 0.0168 | 0.9214 |
| 13 | payment\_installments\_max | numeric | /Spearman/ | 0.0476 | 0.0165 | 0.9379 |
| 14 | purchase\_dayofweek | numeric | /Spearman/ | 0.0437 | 0.0151 | 0.9530 |
| 15 | n\_products | numeric | /Spearman/ | 0.0395 | 0.0137 | 0.9667 |
| 16 | purchase\_month | numeric | /Spearman/ | 0.0311 | 0.0108 | 0.9774 |
| 17 | n\_items | numeric | /Spearman/ | 0.0275 | 0.0095 | 0.9869 |
| 18 | n\_categories | numeric | /Spearman/ | 0.0130 | 0.0045 | 0.9914 |
| 19 | distance\_missing\_fraction | numeric | /Spearman/ | 0.0098 | 0.0034 | 0.9948 |
| 20 | category\_missing\_fraction | numeric | /Spearman/ | 0.0060 | 0.0021 | 0.9969 |
| 21 | n\_payment\_methods | numeric | /Spearman/ | 0.0029 | 0.0010 | 0.9979 |
| 22 | volume\_missing\_fraction | numeric | /Spearman/ | 0.0022 | 0.0008 | 0.9987 |
| 23 | weight\_missing\_fraction | numeric | /Spearman/ | 0.0022 | 0.0008 | 0.9994 |
| 24 | purchase\_hour | numeric | /Spearman/ | 0.0016 | 0.0006 | 1.0000 |

&#91;image: Cumulative importance\]

**Missingness, outliers and VIF** (raw features, pre-cutoff orders):

| feature | type | missing\_share | distinct\_values | share\_outside\_1\_5\_iqr | share\_outside\_3\_iqr | vif | vif\_note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| n\_items | numeric | 0.0000 | 17 | 0.1011 | 0.1011 | 1.6587 |  |
| n\_products | numeric | 0.0000 | 7 | 0.0331 | 0.0331 | 1.7987 |  |
| n\_sellers | numeric | 0.0000 | 5 | 0.0123 | 0.0123 | 1.8544 |  |
| n\_categories | numeric | 0.0000 | 4 | 0.0232 | 0.0232 | 4.8112 |  |
| total\_price | numeric | 0.0000 | 6,383 | 0.0794 | 0.0406 | 1.4761 |  |
| total\_freight | numeric | 0.0000 | 6,763 | 0.0963 | 0.0485 | 3.3380 |  |
| freight\_ratio | numeric | 0.0000 | 33,286 | 0.0680 | 0.0229 | 1.2601 |  |
| total\_weight\_g | numeric | 0.0002 | 2,577 | 0.1410 | 0.0829 | 3.6120 |  |
| total\_volume\_cm3 | numeric | 0.0002 | 5,526 | 0.0977 | 0.0432 | 3.4731 |  |
| weight\_missing\_fraction | numeric | 0.0000 | 2 | 0.0002 | 0.0002 | — | constant on the complete rows |
| volume\_missing\_fraction | numeric | 0.0000 | 2 | 0.0002 | 0.0002 | — | constant on the complete rows |
| primary\_category | categorical | 0.0000 | 72 | — | — | — |  |
| category\_missing\_fraction | numeric | 0.0000 | 10 | 0.0169 | 0.0169 | 4.2629 |  |
| customer\_state | categorical | 0.0000 | 27 | — | — | — |  |
| primary\_seller\_state | categorical | 0.0000 | 22 | — | — | — |  |
| distance\_km\_max | numeric | 0.0115 | 72,050 | 0.0796 | 0.0069 | 1.6851 |  |
| distance\_missing\_fraction | numeric | 0.0000 | 3 | 0.0115 | 0.0115 | — | constant on the complete rows |
| interstate\_share | numeric | 0.0000 | 5 | 0.0000 | 0.0000 | 1.5004 |  |
| purchase\_month | numeric | 0.0000 | 12 | 0.0000 | 0.0000 | 1.0031 |  |
| purchase\_dayofweek | numeric | 0.0000 | 7 | 0.0000 | 0.0000 | 1.0020 |  |
| purchase\_hour | numeric | 0.0000 | 24 | 0.0000 | 0.0000 | 1.0007 |  |
| primary\_payment\_type | categorical | 0.0000 | 4 | — | — | — |  |
| payment\_installments\_max | numeric | 0.0000 | 22 | 0.0667 | 0.0017 | 1.1552 |  |
| n\_payment\_methods | numeric | 0.0000 | 2 | 0.0233 | 0.0233 | 1.0023 |  |

**Collinearity** (|Pearson| or |Spearman| > 0.9, VIF > 10.0; VIF on 76,233 complete rows):

| feature\_a | feature\_b | pearson | spearman | identical |
| --- | --- | --- | --- | --- |
| weight\_missing\_fraction | volume\_missing\_fraction | 1.0000 | 1.0000 | yes |

&#91;image: Correlation heatmap\]

**Skewness of the log1p candidates** (for s04 4.2):

| feature | skewness | threshold | log1p |
| --- | --- | --- | --- |
| total\_price | 10.1167 | 1.0000 | yes |
| total\_freight | 8.1219 | 1.0000 | yes |
| total\_weight\_g | 6.6201 | 1.0000 | yes |
| total\_volume\_cm3 | 7.3868 | 1.0000 | yes |
| distance\_km\_max | 1.6442 | 1.0000 | yes |

**Candidate rationale** (finding → change → stage that tests it):

| finding | evidence | change\_it\_motivates | stage\_that\_tests\_it |
| --- | --- | --- | --- |
| total\_price pre-cutoff skewness 10.12 (above 1) | eda\_summary.json:log1p\_candidates | log1p on total\_price | s04 4.2 (applied), s06 (fitted inside folds) |
| total\_freight pre-cutoff skewness 8.12 (above 1) | eda\_summary.json:log1p\_candidates | log1p on total\_freight | s04 4.2 (applied), s06 (fitted inside folds) |
| total\_weight\_g pre-cutoff skewness 6.62 (above 1) | eda\_summary.json:log1p\_candidates | log1p on total\_weight\_g | s04 4.2 (applied), s06 (fitted inside folds) |
| total\_volume\_cm3 pre-cutoff skewness 7.39 (above 1) | eda\_summary.json:log1p\_candidates | log1p on total\_volume\_cm3 | s04 4.2 (applied), s06 (fitted inside folds) |
| distance\_km\_max pre-cutoff skewness 1.64 (above 1) | eda\_summary.json:log1p\_candidates | log1p on distance\_km\_max | s04 4.2 (applied), s06 (fitted inside folds) |
| weight\_missing\_fraction and volume\_missing\_fraction are identical on every pre-cutoff order | collinear\_pairs.csv | drop one of weight\_missing\_fraction, volume\_missing\_fraction automatically (duplicate rule) | s04 4.3 |
| top 14 of 24 features reach 95% of total absolute Spearman | importance\_ranking.csv:cumulative\_share | selected set = top 14 if the team picks 95% | s04 4.4 (threshold fixed before fitting), s06 |
| top 18 of 24 features reach 99% of total absolute Spearman | importance\_ranking.csv:cumulative\_share | selected set = top 18 if the team picks 99% | s04 4.4 (threshold fixed before fitting), s06 |
| lead\_days skewness 2.40, p99 47.4 vs median 11.2 days | target\_regression\_lead\_days.csv | log1p regression target (G-36) | s04 4.2, s06 |
| median lead time ranges 9.0 to 17.9 days across purchase months with at least 100 orders | outcome\_trends.csv | time-ordered expanding folds, not random folds | s05 5.5 |
| distance\_km\_max missing on 1.15% of orders | feature\_quality.csv:missing\_share | route-median fill (customer x seller state) with the missing indicator, fitted in folds (G-27) | s04 4.8, s06 |

**Check** no order on or after the test cutoff loaded: PASS (latest purchase 2018-05-26 18:16:57, cutoff 2018-05-26 18:18:03) **Check** importance\_ranking has the 24 contract predictors and ends at cumulative share 1.0: PASS (24 rows) **Check** ranking measure is the pre-registered one: PASS

**Files** (stages/s03\_eda/regression/outputs/, run 20261019T163336Z): feature\_quality.csv, collinear\_pairs.csv, numeric\_correlations.csv, figures/numeric\_correlation\_heatmap.png, figures/numeric\_correlation\_heatmap.csv, figures/numeric\_correlation\_heatmap.json, importance\_ranking.csv, figures/cumulative\_importance.png, figures/cumulative\_importance.csv, figures/cumulative\_importance.json, candidate\_rationale.csv, eda\_summary.json, decision.json

## 3.9 Human gate (review pack for s04 decisions)

**Approved solution:** Human gate (G-31): implementation stops after s03. All EDA results are presented to the team, and s04 runs only after the team records its decisions (threshold, collinearity drops)

**What was done:** eda\_review\_pack.md lists every table and figure above, the ranking with both cut points, the flagged collinear groups and the YAML block the team fills in spec/human\_decisions.yaml.

**Conclusion:** Stop: s04 waits for the team's threshold and collinearity decisions (G-31).

Threshold options over the 24 contract predictors (the team chose 99%, G-70):

| Threshold | Features kept | Features (in ranking order) |
| --- | --- | --- |
| 95% | 14 | distance\_km\_max, customer\_state, interstate\_share, total\_freight, primary\_category, freight\_ratio, total\_price, primary\_seller\_state, total\_weight\_g, primary\_payment\_type, total\_volume\_cm3, n\_sellers, payment\_installments\_max, purchase\_dayofweek |
| 99% | 18 | distance\_km\_max, customer\_state, interstate\_share, total\_freight, primary\_category, freight\_ratio, total\_price, primary\_seller\_state, total\_weight\_g, primary\_payment\_type, total\_volume\_cm3, n\_sellers, payment\_installments\_max, purchase\_dayofweek, n\_products, purchase\_month, n\_items, n\_categories |

Flagged collinear groups needing a team decision: none. Identical columns, dropped automatically by the s04 duplicate rule: weight\_missing\_fraction = volume\_missing\_fraction.

**Check** review pack lists both cut points and every flagged group: PASS

**Files** (stages/s03\_eda/regression/outputs/, run 20261019T163336Z): figures/cumulative\_importance.png, figures/cumulative\_importance.csv, figures/cumulative\_importance.json, eda\_review\_pack.md

# Part B — Review record (history: rounds 1–3, do not cite)

The cards below are kept exactly as the team reviewed them (regression runs 20261019T081153Z, 20261019T140119Z, 20261019T151309Z), so the comments and the decision trail stay readable. Every regression value is identical in Part A; cite Part A.

## 3.1 Regression target

**Approved solution:** `lead_days` KDE; count, mean, SD, min, 1/5/25/50/75/95/99%, max, skewness, kurtosis

**What was done:** lead\_days profile on 77,139 pre-cutoff orders: median 11.18, mean 13.44, SD 9.46, p99 47.38, max 133.24 days; skewness 2.40, excess kurtosis 11.55.

**Conclusion:** Right-skewed target: supports the pre-registered log1p target (G-36).

| statistic | value |
| --- | --- |
| count | 77,139.0000 |
| missing\_share | 0.0000 |
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

&#91;image: lead\_days KDE\]

**Files** (local, run 20261019T081153Z): target\_regression\_lead\_days.csv, figures/target\_lead\_days\_kde.png, figures/target\_lead\_days\_kde.csv, figures/target\_lead\_days\_kde.json, eda\_summary.json

## 3.3 Outcome trends

**Approved solution:** By purchase month: median lead time, late-vs-promised rate, detractor rate, with counts (not volume only)

**What was done:** 19 purchase months; over the 18 months with at least 100 orders: median lead time 9.0 to 17.9 days, late-vs-promised rate 1.1% to 21.4%, detractor rate 9.5% to 21.2%; every month is in the table with its counts.

**Reasoning:** Late is delivery after order\_estimated\_delivery\_date, used here only as a description (G-35).

| month | orders | orders\_with\_lead\_time | median\_lead\_days | late\_vs\_promised\_rate | orders\_with\_review | detractor\_rate |
| --- | --- | --- | --- | --- | --- | --- |
| 2016-10 | 265 | 265 | 17.944 | 0.011 | 262 | 0.164 |
| 2016-12 | 1 | 1 | 4.693 | 0.000 | 1 | 0.000 |
| 2017-01 | 750 | 750 | 10.734 | 0.031 | 741 | 0.120 |
| 2017-02 | 1,651 | 1,651 | 10.964 | 0.031 | 1,642 | 0.110 |
| 2017-03 | 2,535 | 2,535 | 10.108 | 0.052 | 2,516 | 0.113 |
| 2017-04 | 2,296 | 2,296 | 12.721 | 0.076 | 2,284 | 0.128 |
| 2017-05 | 3,543 | 3,543 | 9.789 | 0.036 | 3,515 | 0.101 |
| 2017-06 | 3,133 | 3,133 | 10.802 | 0.038 | 3,109 | 0.108 |
| 2017-07 | 3,872 | 3,872 | 10.158 | 0.034 | 3,842 | 0.101 |
| 2017-08 | 4,193 | 4,193 | 9.770 | 0.033 | 4,165 | 0.095 |
| 2017-09 | 4,150 | 4,150 | 10.314 | 0.052 | 4,118 | 0.103 |
| 2017-10 | 4,478 | 4,478 | 10.263 | 0.053 | 4,446 | 0.111 |
| 2017-11 | 7,284 | 7,284 | 12.692 | 0.143 | 7,233 | 0.166 |
| 2017-12 | 5,512 | 5,512 | 13.142 | 0.084 | 5,460 | 0.145 |
| 2018-01 | 7,068 | 7,068 | 11.829 | 0.066 | 7,012 | 0.137 |
| 2018-02 | 6,552 | 6,552 | 14.263 | 0.159 | 6,504 | 0.194 |
| 2018-03 | 7,003 | 7,003 | 13.368 | 0.214 | 6,948 | 0.212 |
| 2018-04 | 6,797 | 6,797 | 9.315 | 0.053 | 6,751 | 0.118 |
| 2018-05 | 6,056 | 6,056 | 9.010 | 0.091 | 6,031 | 0.111 |

&#91;image: Outcome trends\]

**Files** (local, run 20261019T081153Z): outcome\_trends.csv, figures/outcome\_trends.png, figures/outcome\_trends.csv, figures/outcome\_trends.json, eda\_summary.json

## 3.4 Numeric features vs lead\_days

**Approved solution:** Scatter plot per feature; Pearson **and** Spearman (skewed features); full percentile profile; sorted by absolute correlation

**What was done:** 20 numeric predictors: Pearson and Spearman with lead\_days on the rows where the feature is present, plus each feature's percentile profile; strongest |Spearman|: distance\_km\_max (0.539). Scatter panels use 2,000 random orders each (seed 42); log1p x-axis for the five log1p candidates (plot only).

| feature | n | pearson | spearman | feature\_missing\_share | feature\_p50 | feature\_p99 | feature\_skewness |
| --- | --- | --- | --- | --- | --- | --- | --- |
| distance\_km\_max | 76,249 | 0.4088 | 0.5393 | 0.0115 | 443.8695 | 2,484.1965 | 1.6442 |
| interstate\_share | 77,139 | 0.3828 | 0.4982 | 0.0000 | 1.0000 | 1.0000 | -0.6348 |
| total\_freight | 77,139 | 0.1912 | 0.4048 | 0.0000 | 16.7900 | 100.9344 | 8.1219 |
| freight\_ratio | 77,139 | 0.0904 | 0.1317 | 0.0000 | 0.2223 | 1.4412 | 10.9982 |
| total\_price | 77,139 | 0.0574 | 0.0935 | 0.0000 | 86.9000 | 989.9962 | 10.1167 |
| total\_weight\_g | 77,123 | 0.0678 | 0.0774 | 0.0002 | 800.0000 | 22,644.5000 | 6.6201 |
| total\_volume\_cm3 | 77,123 | 0.0571 | 0.0579 | 0.0002 | 7,632.0000 | 140,000.0000 | 7.3868 |
| n\_sellers | 77,139 | -0.0423 | -0.0487 | 0.0000 | 1.0000 | 2.0000 | 10.1057 |
| payment\_installments\_max | 77,139 | 0.0530 | 0.0476 | 0.0000 | 2.0000 | 10.0000 | 1.5904 |
| purchase\_dayofweek | 77,139 | 0.0290 | 0.0437 | 0.0000 | 3.0000 | 6.0000 | 0.1589 |
| n\_products | 77,139 | -0.0343 | -0.0395 | 0.0000 | 1.0000 | 2.0000 | 7.7036 |
| purchase\_month | 77,139 | -0.0225 | -0.0311 | 0.0000 | 5.0000 | 12.0000 | 0.3731 |
| n\_items | 77,139 | -0.0213 | -0.0275 | 0.0000 | 1.0000 | 3.0000 | 7.8378 |
| n\_categories | 77,139 | -0.0116 | -0.0130 | 0.0000 | 1.0000 | 1.0000 | -2.1460 |
| distance\_missing\_fraction | 77,139 | 0.0053 | 0.0098 | 0.0000 | 0.0000 | 1.0000 | 9.1802 |
| category\_missing\_fraction | 77,139 | -0.0056 | -0.0060 | 0.0000 | 0.0000 | 1.0000 | 7.5937 |
| n\_payment\_methods | 77,139 | -0.0010 | 0.0029 | 0.0000 | 1.0000 | 2.0000 | 6.3189 |
| volume\_missing\_fraction | 77,139 | -0.0019 | -0.0022 | 0.0000 | 0.0000 | 0.0000 | 69.4145 |
| weight\_missing\_fraction | 77,139 | -0.0019 | -0.0022 | 0.0000 | 0.0000 | 0.0000 | 69.4145 |
| purchase\_hour | 77,139 | 0.0013 | 0.0016 | 0.0000 | 15.0000 | 23.0000 | -0.6059 |

&#91;image: Numeric features vs lead\_days\]

**Files** (local, run 20261019T081153Z): numeric\_feature\_target\_lead\_days.csv, figures/numeric\_vs\_lead\_days.png, figures/numeric\_vs\_lead\_days.csv, figures/numeric\_vs\_lead\_days.json

## 3.5 Categorical features vs lead\_days

**Approved solution:** Violin plots (median, IQR, outliers); one-hot (drop-first) correlations; calendar fields treated as categorical for plots only

**What was done:** Four categorical predictors: per-level median, IQR and mean of lead\_days, drop-first dummy correlations (reference level = first in sorted order), and one rank correlation ratio per feature; the three calendar fields are shown per level for the plots only and stay numeric.

**Reasoning:** Spearman needs an ordered feature, so a nominal feature gets the rank correlation ratio (square root of the Kruskal-Wallis epsilon-squared): the same 0-1 scale as |Spearman| on the ranked target. Flagged for the team to confirm (decision 1).

| feature | levels | rank\_correlation\_ratio | lowest\_median | highest\_median |
| --- | --- | --- | --- | --- |
| customer\_state | 27 | 0.5045 | 7.8524 | 27.0878 |
| primary\_category | 72 | 0.1454 | 5.0995 | 18.8395 |
| primary\_seller\_state | 22 | 0.0910 | 9.0058 | 29.5235 |
| primary\_payment\_type | 4 | 0.0716 | 10.1591 | 12.2566 |

**customer\_state** (top 15 of 27 levels by count; all levels in categorical\_feature\_target\_lead\_days.csv)

| level | n | share | target\_median | target\_q1 | target\_q3 | dummy | dummy\_correlation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SP | 31,566 | 0.409 | 7.852 | 5.126 | 11.775 | kept | -0.358 |
| RJ | 10,135 | 0.131 | 13.105 | 9.038 | 20.001 | kept | 0.126 |
| MG | 9,220 | 0.120 | 11.245 | 8.141 | 15.582 | kept | -0.023 |
| RS | 4,403 | 0.057 | 14.118 | 10.134 | 19.889 | kept | 0.071 |
| PR | 3,945 | 0.051 | 11.203 | 8.091 | 15.434 | kept | -0.015 |
| SC | 2,926 | 0.038 | 14.157 | 10.081 | 19.942 | kept | 0.055 |
| BA | 2,611 | 0.034 | 18.052 | 13.369 | 24.225 | kept | 0.133 |
| ES | 1,632 | 0.021 | 14.255 | 10.341 | 19.908 | kept | 0.044 |
| DF | 1,613 | 0.021 | 12.379 | 9.046 | 17.239 | kept | 0.009 |
| GO | 1,609 | 0.021 | 14.691 | 11.107 | 19.555 | kept | 0.044 |
| PE | 1,270 | 0.016 | 17.210 | 13.051 | 23.714 | kept | 0.086 |
| CE | 1,062 | 0.014 | 19.670 | 14.944 | 26.790 | kept | 0.114 |
| PA | 786 | 0.010 | 22.661 | 16.867 | 30.601 | kept | 0.125 |
| MT | 734 | 0.010 | 17.189 | 13.359 | 22.084 | kept | 0.058 |
| MA | 601 | 0.008 | 19.787 | 15.269 | 25.361 | kept | 0.081 |

**primary\_seller\_state** (top 15 of 22 levels by count; all levels in categorical\_feature\_target\_lead\_days.csv)

| level | n | share | target\_median | target\_q1 | target\_q3 | dummy | dummy\_correlation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SP | 54,904 | 0.712 | 10.978 | 6.973 | 16.971 | kept | -0.029 |
| MG | 6,294 | 0.082 | 11.579 | 7.773 | 16.578 | kept | 0.004 |
| PR | 5,996 | 0.078 | 12.164 | 8.357 | 17.278 | kept | 0.028 |
| RJ | 3,146 | 0.041 | 10.998 | 7.185 | 16.369 | kept | -0.006 |
| SC | 2,867 | 0.037 | 12.453 | 8.970 | 17.566 | kept | 0.026 |
| RS | 1,459 | 0.019 | 10.242 | 7.014 | 14.766 | kept | -0.018 |
| DF | 657 | 0.009 | 11.063 | 7.875 | 15.760 | kept | -0.005 |
| BA | 426 | 0.006 | 12.070 | 9.117 | 17.249 | kept | 0.006 |
| GO | 344 | 0.004 | 12.075 | 8.364 | 16.925 | kept | 0.003 |
| PE | 294 | 0.004 | 12.142 | 9.049 | 16.816 | kept | 0.002 |
| ES | 266 | 0.003 | 11.549 | 8.604 | 15.602 | kept | 0.000 |
| MA | 163 | 0.002 | 19.386 | 15.579 | 29.139 | kept | 0.044 |
| MT | 115 | 0.001 | 13.094 | 10.747 | 17.295 | kept | 0.007 |
| CE | 59 | 0.001 | 15.243 | 11.381 | 21.653 | kept | 0.012 |
| RN | 45 | 0.001 | 9.006 | 5.052 | 21.913 | kept | 0.001 |

**primary\_payment\_type**

| level | n | share | target\_median | target\_q1 | target\_q3 | dummy | dummy\_correlation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| credit\_card | 58,205 | 0.755 | 10.973 | 7.058 | 16.760 | kept | -0.038 |
| boleto | 15,658 | 0.203 | 12.257 | 8.135 | 17.848 | dropped (reference) | — |
| voucher | 2,484 | 0.032 | 11.066 | 7.190 | 16.391 | kept | -0.006 |
| debit\_card | 792 | 0.010 | 10.159 | 6.521 | 16.205 | kept | -0.009 |

**primary\_category** (top 15 of 72 levels by count; all levels in categorical\_feature\_target\_lead\_days.csv)

| level | n | share | target\_median | target\_q1 | target\_q3 | dummy | dummy\_correlation |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bed\_bath\_table | 7,405 | 0.096 | 11.919 | 8.018 | 17.524 | kept | 0.022 |
| health\_beauty | 6,310 | 0.082 | 10.505 | 6.824 | 16.499 | kept | -0.009 |
| sports\_leisure | 6,233 | 0.081 | 11.038 | 7.140 | 16.130 | kept | -0.013 |
| computers\_accessories | 5,367 | 0.070 | 11.966 | 7.879 | 17.406 | kept | 0.015 |
| furniture\_decor | 5,183 | 0.067 | 11.471 | 7.661 | 17.439 | kept | 0.011 |
| housewares | 4,160 | 0.054 | 10.154 | 6.522 | 15.332 | kept | -0.031 |
| watches\_gifts | 4,089 | 0.053 | 11.343 | 7.654 | 17.531 | kept | 0.011 |
| telephony | 3,397 | 0.044 | 11.449 | 7.300 | 17.251 | kept | 0.003 |
| toys | 3,290 | 0.043 | 10.002 | 6.578 | 15.114 | kept | -0.025 |
| cool\_stuff | 3,190 | 0.041 | 10.861 | 7.001 | 15.365 | kept | -0.020 |
| garden\_tools | 2,964 | 0.038 | 12.328 | 8.472 | 17.755 | kept | 0.020 |
| auto | 2,838 | 0.037 | 10.814 | 6.970 | 16.737 | kept | 0.000 |
| perfumery | 2,521 | 0.033 | 10.402 | 6.420 | 15.951 | kept | -0.014 |
| baby | 2,125 | 0.028 | 11.105 | 7.050 | 17.268 | kept | 0.006 |
| electronics | 2,058 | 0.027 | 12.054 | 7.816 | 17.953 | kept | 0.009 |

&#91;image: Categorical features vs lead\_days\]

**Files** (local, run 20261019T081153Z): categorical\_feature\_target\_lead\_days.csv, figures/categorical\_vs\_lead\_days.png, figures/categorical\_vs\_lead\_days.csv, figures/categorical\_vs\_lead\_days.json

## 3.8 Importance ranking

**Approved solution:** One ranking per task feeding s04 selection, over all 24 contract predictors (the ranking file has exactly 24 rows; G-42, G-61): absolute Spearman for regression, mutual information for classification (one measure per task, so cumulative shares are meaningful). Missingness, outliers and correlation/VIF among raw numeric features also reported here

**What was done:** Ranking over the 24 contract predictors by absolute Spearman (rank correlation ratio for the four categorical ones): top 5 \['distance\_km\_max', 'customer\_state', 'interstate\_share', 'total\_freight', 'primary\_category'\]; cut points {'0.95': 14, '0.99': 18} (features needed for each cumulative share). Missingness, IQR outliers, Pearson/Spearman matrix and VIF on 76,233 complete rows; flagged groups: \[\]; identical columns: \[('weight\_missing\_fraction', 'volume\_missing\_fraction')\].

**Ranking** (absolute Spearman):

| rank | feature | type | method | value | share | cumulative\_share |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | distance\_km\_max | numeric | /Spearman/ | 0.5393 | 0.1865 | 0.1865 |
| 2 | customer\_state | categorical | rank correlation ratio (Spearman scale) | 0.5045 | 0.1745 | 0.3610 |
| 3 | interstate\_share | numeric | /Spearman/ | 0.4982 | 0.1723 | 0.5333 |
| 4 | total\_freight | numeric | /Spearman/ | 0.4048 | 0.1400 | 0.6734 |
| 5 | primary\_category | categorical | rank correlation ratio (Spearman scale) | 0.1454 | 0.0503 | 0.7237 |
| 6 | freight\_ratio | numeric | /Spearman/ | 0.1317 | 0.0455 | 0.7692 |
| 7 | total\_price | numeric | /Spearman/ | 0.0935 | 0.0323 | 0.8015 |
| 8 | primary\_seller\_state | categorical | rank correlation ratio (Spearman scale) | 0.0910 | 0.0315 | 0.8330 |
| 9 | total\_weight\_g | numeric | /Spearman/ | 0.0774 | 0.0268 | 0.8598 |
| 10 | primary\_payment\_type | categorical | rank correlation ratio (Spearman scale) | 0.0716 | 0.0248 | 0.8846 |
| 11 | total\_volume\_cm3 | numeric | /Spearman/ | 0.0579 | 0.0200 | 0.9046 |
| 12 | n\_sellers | numeric | /Spearman/ | 0.0487 | 0.0168 | 0.9214 |
| 13 | payment\_installments\_max | numeric | /Spearman/ | 0.0476 | 0.0165 | 0.9379 |
| 14 | purchase\_dayofweek | numeric | /Spearman/ | 0.0437 | 0.0151 | 0.9530 |
| 15 | n\_products | numeric | /Spearman/ | 0.0395 | 0.0137 | 0.9667 |
| 16 | purchase\_month | numeric | /Spearman/ | 0.0311 | 0.0108 | 0.9774 |
| 17 | n\_items | numeric | /Spearman/ | 0.0275 | 0.0095 | 0.9869 |
| 18 | n\_categories | numeric | /Spearman/ | 0.0130 | 0.0045 | 0.9914 |
| 19 | distance\_missing\_fraction | numeric | /Spearman/ | 0.0098 | 0.0034 | 0.9948 |
| 20 | category\_missing\_fraction | numeric | /Spearman/ | 0.0060 | 0.0021 | 0.9969 |
| 21 | n\_payment\_methods | numeric | /Spearman/ | 0.0029 | 0.0010 | 0.9979 |
| 22 | volume\_missing\_fraction | numeric | /Spearman/ | 0.0022 | 0.0008 | 0.9987 |
| 23 | weight\_missing\_fraction | numeric | /Spearman/ | 0.0022 | 0.0008 | 0.9994 |
| 24 | purchase\_hour | numeric | /Spearman/ | 0.0016 | 0.0006 | 1.0000 |

&#91;image: Cumulative importance\]

**Missingness, outliers and VIF** (raw features, pre-cutoff orders):

| feature | type | missing\_share | distinct\_values | share\_outside\_1\_5\_iqr | share\_outside\_3\_iqr | vif | vif\_note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| n\_items | numeric | 0.0000 | 17 | 0.1011 | 0.1011 | 1.6587 |  |
| n\_products | numeric | 0.0000 | 7 | 0.0331 | 0.0331 | 1.7987 |  |
| n\_sellers | numeric | 0.0000 | 5 | 0.0123 | 0.0123 | 1.8544 |  |
| n\_categories | numeric | 0.0000 | 4 | 0.0232 | 0.0232 | 4.8112 |  |
| total\_price | numeric | 0.0000 | 6,383 | 0.0794 | 0.0406 | 1.4761 |  |
| total\_freight | numeric | 0.0000 | 6,763 | 0.0963 | 0.0485 | 3.3380 |  |
| freight\_ratio | numeric | 0.0000 | 33,286 | 0.0680 | 0.0229 | 1.2601 |  |
| total\_weight\_g | numeric | 0.0002 | 2,577 | 0.1410 | 0.0829 | 3.6120 |  |
| total\_volume\_cm3 | numeric | 0.0002 | 5,526 | 0.0977 | 0.0432 | 3.4731 |  |
| weight\_missing\_fraction | numeric | 0.0000 | 2 | 0.0002 | 0.0002 | — | constant on the complete rows |
| volume\_missing\_fraction | numeric | 0.0000 | 2 | 0.0002 | 0.0002 | — | constant on the complete rows |
| primary\_category | categorical | 0.0000 | 72 | — | — | — |  |
| category\_missing\_fraction | numeric | 0.0000 | 10 | 0.0169 | 0.0169 | 4.2629 |  |
| customer\_state | categorical | 0.0000 | 27 | — | — | — |  |
| primary\_seller\_state | categorical | 0.0000 | 22 | — | — | — |  |
| distance\_km\_max | numeric | 0.0115 | 72,050 | 0.0796 | 0.0069 | 1.6851 |  |
| distance\_missing\_fraction | numeric | 0.0000 | 3 | 0.0115 | 0.0115 | — | constant on the complete rows |
| interstate\_share | numeric | 0.0000 | 5 | 0.0000 | 0.0000 | 1.5004 |  |
| purchase\_month | numeric | 0.0000 | 12 | 0.0000 | 0.0000 | 1.0031 |  |
| purchase\_dayofweek | numeric | 0.0000 | 7 | 0.0000 | 0.0000 | 1.0020 |  |
| purchase\_hour | numeric | 0.0000 | 24 | 0.0000 | 0.0000 | 1.0007 |  |
| primary\_payment\_type | categorical | 0.0000 | 4 | — | — | — |  |
| payment\_installments\_max | numeric | 0.0000 | 22 | 0.0667 | 0.0017 | 1.1552 |  |
| n\_payment\_methods | numeric | 0.0000 | 2 | 0.0233 | 0.0233 | 1.0023 |  |

**Collinearity** (|Pearson| or |Spearman| > 0.9, VIF > 10.0; VIF on 76,233 complete rows):

| feature\_a | feature\_b | pearson | spearman | identical |
| --- | --- | --- | --- | --- |
| weight\_missing\_fraction | volume\_missing\_fraction | 1.0000 | 1.0000 | yes |

&#91;image: Correlation heatmap\]

**Skewness of the log1p candidates** (for s04 4.2):

| feature | skewness | threshold | log1p |
| --- | --- | --- | --- |
| total\_price | 10.1167 | 1.0000 | yes |
| total\_freight | 8.1219 | 1.0000 | yes |
| total\_weight\_g | 6.6201 | 1.0000 | yes |
| total\_volume\_cm3 | 7.3868 | 1.0000 | yes |
| distance\_km\_max | 1.6442 | 1.0000 | yes |

**Candidate rationale** (finding → change → stage that tests it):

| finding | evidence | change\_it\_motivates | stage\_that\_tests\_it |
| --- | --- | --- | --- |
| total\_price pre-cutoff skewness 10.12 (above 1) | eda\_summary.json:log1p\_candidates | log1p on total\_price | s04 4.2 (applied), s06 (fitted inside folds) |
| total\_freight pre-cutoff skewness 8.12 (above 1) | eda\_summary.json:log1p\_candidates | log1p on total\_freight | s04 4.2 (applied), s06 (fitted inside folds) |
| total\_weight\_g pre-cutoff skewness 6.62 (above 1) | eda\_summary.json:log1p\_candidates | log1p on total\_weight\_g | s04 4.2 (applied), s06 (fitted inside folds) |
| total\_volume\_cm3 pre-cutoff skewness 7.39 (above 1) | eda\_summary.json:log1p\_candidates | log1p on total\_volume\_cm3 | s04 4.2 (applied), s06 (fitted inside folds) |
| distance\_km\_max pre-cutoff skewness 1.64 (above 1) | eda\_summary.json:log1p\_candidates | log1p on distance\_km\_max | s04 4.2 (applied), s06 (fitted inside folds) |
| weight\_missing\_fraction and volume\_missing\_fraction are identical on every pre-cutoff order | collinear\_pairs.csv | drop one of weight\_missing\_fraction, volume\_missing\_fraction automatically (duplicate rule) | s04 4.3 |
| top 14 of 24 features reach 95% of total absolute Spearman | importance\_ranking.csv:cumulative\_share | selected set = top 14 if the team picks 95% | s04 4.4 (threshold fixed before fitting), s06 |
| top 18 of 24 features reach 99% of total absolute Spearman | importance\_ranking.csv:cumulative\_share | selected set = top 18 if the team picks 99% | s04 4.4 (threshold fixed before fitting), s06 |
| lead\_days skewness 2.40, p99 47.4 vs median 11.2 days | target\_regression\_lead\_days.csv | log1p regression target (G-36) | s04 4.2, s06 |
| median lead time ranges 9.0 to 17.9 days across purchase months with at least 100 orders | outcome\_trends.csv | time-ordered expanding folds, not random folds | s05 5.5 |
| distance\_km\_max missing on 1.15% of orders | feature\_quality.csv:missing\_share | route-median fill (customer x seller state) with the missing indicator, fitted in folds (G-27) | s04 4.8, s06 |

**Files** (local, run 20261019T081153Z): feature\_quality.csv, collinear\_pairs.csv, numeric\_correlations.csv, figures/numeric\_correlation\_heatmap.png, figures/numeric\_correlation\_heatmap.csv, figures/numeric\_correlation\_heatmap.json, importance\_ranking.csv, figures/cumulative\_importance.png, figures/cumulative\_importance.csv, figures/cumulative\_importance.json, candidate\_rationale.csv, eda\_summary.json, decision.json

## 3.9 Human gate (review pack for s04 decisions)

**Approved solution:** Human gate (G-31): implementation stops after s03. All EDA results are presented to the team, and s04 runs only after the team records its decisions (threshold, collinearity drops)

**What was done:** eda\_review\_pack.md lists every table and figure above, the ranking with both cut points, the flagged collinear groups and the YAML block the team fills in spec/human\_decisions.yaml.

**Conclusion:** Stop: s04 waits for the team's threshold and collinearity decisions (G-31).

eda\_review\_pack.md holds every table and figure of this tab. Threshold options:

| Threshold | Features kept | Features (in ranking order) |
| --- | --- | --- |
| 95% | 14 | distance\_km\_max, customer\_state, interstate\_share, total\_freight, primary\_category, freight\_ratio, total\_price, primary\_seller\_state, total\_weight\_g, primary\_payment\_type, total\_volume\_cm3, n\_sellers, payment\_installments\_max, purchase\_dayofweek |
| 99% | 18 | distance\_km\_max, customer\_state, interstate\_share, total\_freight, primary\_category, freight\_ratio, total\_price, primary\_seller\_state, total\_weight\_g, primary\_payment\_type, total\_volume\_cm3, n\_sellers, payment\_installments\_max, purchase\_dayofweek, n\_products, purchase\_month, n\_items, n\_categories |

Flagged collinear groups needing a team decision: none. Identical columns, dropped automatically by the s04 duplicate rule: weight\_missing\_fraction = volume\_missing\_fraction.

**Files** (local, run 20261019T081153Z): figures/cumulative\_importance.png, figures/cumulative\_importance.csv, figures/cumulative\_importance.json, eda\_review\_pack.md
