# s03 EDA › classification

> **How to read this tab.** Part A is the final, accepted result (round 5, CR-043, run `20261020T053142Z`); the report, slides and s04 use only Part A. Part B keeps the review record of rounds 1–3: its numbers come from earlier runs (before CR-042 and CR-043) and are superseded, kept only so the discussion and comment threads still make sense.

# Part A — Final result (accepted, cite this)

Run `20261020T053142Z` on commit 4999811 (clean tree) · data from s02 run `20261020T053117Z` · 10 solution steps IMPLEMENTED · 11 checks, all PASS · gate decisions in spec/human\_decisions.yaml (G-70, unchanged by CR-042 and CR-043).

## Final classification feature pool (27 features)

The 24 contract predictors + **product\_photos\_qty**, **product\_description\_lenght** (3.10) and **seller\_prior\_review\_mean** (3.13, the seller rating customers see at checkout). In code the only source is `e5lib.contract.pool("classification")`, which reads spec/human\_decisions.yaml and is pinned by a test. Not adopted: product\_name\_lenght, est\_delivery\_days (G-35 holds), customer\_region, seller\_region, region\_pair and the other four seller-history columns. Threshold 99%; no collinearity drop.

**Missing indicator for the seller rating (derived, goes with its parent).** A 0/1 column that is 1 when the seller had no review answered before the purchase, so `seller_prior_review_mean` is missing (6.8% of pre-cutoff orders, card 3.13 missing\_share). The s04 recipe (4.8, median imputation + missing indicators) creates it next to the imputed value, fitted per training fold, and keeps it whenever `seller_prior_review_mean` is kept. It is not ranked on its own, unlike the contract's missing-fraction predictors (weight, volume, category, distance), which s02 builds and s03 ranks. Its column name is fixed in s04 `feature_dictionary.csv`.

**Pool ranking** — the ranking s04 walks (s04 blueprint 4.4): the extended ranking filtered to the 27 pool features, shares re-normalised. At 99% it keeps 19 features; at 95%, 15. s04 computes this officially; this table is the same rule on the same values.

| rank | feature | source | inside 99% | value | share | cumulative\_share |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | seller\_prior\_review\_mean | adopted candidate (G-70) | yes | 0.0110 | 0.1159 | 0.1159 |
| 2 | total\_freight | contract predictor | yes | 0.0102 | 0.1079 | 0.2238 |
| 3 | freight\_ratio | contract predictor | yes | 0.0088 | 0.0932 | 0.3169 |
| 4 | total\_volume\_cm3 | contract predictor | yes | 0.0085 | 0.0899 | 0.4068 |
| 5 | total\_price | contract predictor | yes | 0.0075 | 0.0795 | 0.4863 |
| 6 | n\_items | contract predictor | yes | 0.0073 | 0.0769 | 0.5632 |
| 7 | product\_description\_lenght | adopted candidate (G-70) | yes | 0.0054 | 0.0566 | 0.6198 |
| 8 | customer\_state | contract predictor | yes | 0.0051 | 0.0538 | 0.6737 |
| 9 | total\_weight\_g | contract predictor | yes | 0.0050 | 0.0530 | 0.7266 |
| 10 | n\_products | contract predictor | yes | 0.0044 | 0.0468 | 0.7734 |
| 11 | n\_sellers | contract predictor | yes | 0.0041 | 0.0432 | 0.8166 |
| 12 | purchase\_month | contract predictor | yes | 0.0040 | 0.0421 | 0.8587 |
| 13 | distance\_km\_max | contract predictor | yes | 0.0035 | 0.0368 | 0.8955 |
| 14 | interstate\_share | contract predictor | yes | 0.0026 | 0.0277 | 0.9232 |
| 15 | primary\_category | contract predictor | yes | 0.0026 | 0.0275 | 0.9507 |
| 16 | n\_categories | contract predictor | yes | 0.0016 | 0.0164 | 0.9671 |
| 17 | primary\_seller\_state | contract predictor | yes | 0.0009 | 0.0094 | 0.9764 |
| 18 | payment\_installments\_max | contract predictor | yes | 0.0008 | 0.0084 | 0.9849 |
| 19 | product\_photos\_qty | adopted candidate (G-70) | yes | 0.0005 | 0.0057 | 0.9906 |
| 20 | category\_missing\_fraction | contract predictor | no | 0.0004 | 0.0045 | 0.9951 |
| 21 | purchase\_hour | contract predictor | no | 0.0003 | 0.0034 | 0.9985 |
| 22 | purchase\_dayofweek | contract predictor | no | 0.0001 | 0.0011 | 0.9996 |
| 23 | distance\_missing\_fraction | contract predictor | no | 0.0000 | 0.0003 | 0.9999 |
| 24 | primary\_payment\_type | contract predictor | no | 0.0000 | 0.0001 | 1.0000 |
| 25 | volume\_missing\_fraction | contract predictor | no | 0.0000 | 0.0000 | 1.0000 |
| 26 | weight\_missing\_fraction | contract predictor | no | 0.0000 | 0.0000 | 1.0000 |
| 27 | n\_payment\_methods | contract predictor | no | 0.0000 | 0.0000 | 1.0000 |

**Changes since the round 3 acceptance.** CR-042 (G-71): orders with a review answered at or before purchase leave classification and such reviews never count in seller history. CR-043 (G-72): orders bought before 2017-01-01 leave both tasks and seller history, because the 2016 months are too thin to be representative. Pre-cutoff orders 77,971 (round 3) → 77,736; seller\_prior\_review\_mean is now rank 1 of 36. The 99% cut of the pool keeps the same 19 features as in round 3; only the order of near-tied features changed. Gate decisions unchanged.

## 3.2 Classification target

**Approved solution:** `is_detractor` bar chart; counts, share of low reviews (≤ 2) and normal reviews (≥ 3)

**What was done:** 77,736 pre-cutoff orders: 11,493 low reviews (score <= 2, 14.78%) and 66,243 normal reviews (score >= 3, 85.22%).

**Conclusion:** Imbalanced target: average precision is read against the prevalence baseline.

| class | orders | share |
| --- | --- | --- |
| low review (score <= 2), is\_detractor = 1 | 11,493 | 0.1478 |
| normal review (score >= 3), is\_detractor = 0 | 66,243 | 0.8522 |
| total | 77,736 | 1.0000 |

&#91;image: is\_detractor counts\]

**Check** no order on or after the test cutoff loaded: PASS (latest purchase 2018-05-26 12:12:15, cutoff 2018-05-26 12:16:34)

**Files** (stages/s03\_eda/classification/outputs/, run 20261020T053142Z): target\_classification\_is\_detractor.csv, figures/target\_is\_detractor\_bar.png, figures/target\_is\_detractor\_bar.csv, figures/target\_is\_detractor\_bar.json, eda\_summary.json

## 3.3 Outcome trends

**Approved solution:** By purchase month: median lead time, late-vs-promised rate, detractor rate, with counts (not volume only)

**What was done:** 17 purchase months; over the 17 months with at least 100 orders: detractor rate 10.7% to 22.5%, late-vs-promised rate 2.8% to 21.1%, median lead time 9.0 to 14.3 days; every month is in the table with its counts.

**Reasoning:** Late is delivery after order\_estimated\_delivery\_date, used here only as a description (G-35).

| month | orders | orders\_with\_lead\_time | median\_lead\_days | late\_vs\_promised\_rate | orders\_with\_review | detractor\_rate |
| --- | --- | --- | --- | --- | --- | --- |
| 2017-01 | 777 | 741 | 10.715 | 0.030 | 777 | 0.148 |
| 2017-02 | 1,708 | 1,643 | 10.950 | 0.028 | 1,708 | 0.138 |
| 2017-03 | 2,597 | 2,526 | 10.125 | 0.055 | 2,597 | 0.127 |
| 2017-04 | 2,360 | 2,290 | 12.743 | 0.077 | 2,360 | 0.148 |
| 2017-05 | 3,606 | 3,517 | 9.783 | 0.034 | 3,606 | 0.118 |
| 2017-06 | 3,181 | 3,111 | 10.802 | 0.038 | 3,181 | 0.120 |
| 2017-07 | 3,911 | 3,842 | 10.152 | 0.034 | 3,911 | 0.110 |
| 2017-08 | 4,241 | 4,165 | 9.770 | 0.033 | 4,241 | 0.107 |
| 2017-09 | 4,194 | 4,118 | 10.314 | 0.051 | 4,194 | 0.116 |
| 2017-10 | 4,510 | 4,446 | 10.249 | 0.052 | 4,510 | 0.119 |
| 2017-11 | 7,360 | 7,237 | 12.627 | 0.141 | 7,360 | 0.177 |
| 2017-12 | 5,561 | 5,461 | 13.123 | 0.083 | 5,561 | 0.158 |
| 2018-01 | 7,126 | 7,013 | 11.805 | 0.065 | 7,126 | 0.148 |
| 2018-02 | 6,573 | 6,507 | 14.262 | 0.159 | 6,573 | 0.200 |
| 2018-03 | 7,106 | 6,948 | 13.339 | 0.211 | 7,106 | 0.225 |
| 2018-04 | 6,859 | 6,748 | 9.303 | 0.052 | 6,859 | 0.128 |
| 2018-05 | 6,066 | 5,992 | 8.983 | 0.091 | 6,066 | 0.118 |

&#91;image: Outcome trends\]

**Check** no order on or after the test cutoff loaded: PASS (latest purchase 2018-05-26 12:12:15, cutoff 2018-05-26 12:16:34) **Check** outcome trends show outcomes, not volume only: PASS

**Files** (stages/s03\_eda/classification/outputs/, run 20261020T053142Z): outcome\_trends.csv, figures/outcome\_trends.png, figures/outcome\_trends.csv, figures/outcome\_trends.json, eda\_summary.json

## 3.6 Numeric features vs is\_detractor

**Approved solution:** KDE per class with overlap coefficient (0% = perfect separation, 100% = no signal) and per-feature ROC-AUC on the same rows

**What was done:** 20 numeric predictors: class-conditional distributions with the overlap coefficient (KDE for continuous features, class frequencies for features with at most 30 values), per-feature ROC-AUC and mutual information on the same rows; lowest overlap: total\_freight (86.6%, ROC-AUC 0.587).

**Reasoning:** A KDE smears an integer count into values that cannot occur, so features with few values use the class frequencies; the five log1p candidates use the KDE on the log1p scale (the coefficient does not change under a monotone transform). Flagged for the team (decision 2).

| feature | n | overlap\_coefficient | overlap\_method | roc\_auc | direction | mutual\_information | mean\_class\_0 | mean\_class\_1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| total\_freight | 77,736 | 0.8660 | KDE (log1p scale) | 0.5871 | higher value, more detractors | 0.0102 | 21.4422 | 27.2716 |
| purchase\_month | 77,736 | 0.8876 | discrete frequencies | 0.4748 | lower value, more detractors | 0.0040 | 5.8197 | 5.5882 |
| n\_items | 77,736 | 0.8913 | discrete frequencies | 0.5548 | higher value, more detractors | 0.0073 | 1.1160 | 1.2937 |
| interstate\_share | 77,736 | 0.9143 | discrete frequencies | 0.5412 | higher value, more detractors | 0.0026 | 0.6399 | 0.7229 |
| total\_price | 77,736 | 0.9322 | KDE (log1p scale) | 0.5442 | higher value, more detractors | 0.0075 | 132.8165 | 159.9416 |
| distance\_km\_max | 76,826 | 0.9335 | KDE (log1p scale) | 0.5474 | higher value, more detractors | 0.0035 | 596.3162 | 692.5733 |
| n\_products | 77,736 | 0.9467 | discrete frequencies | 0.5267 | higher value, more detractors | 0.0044 | 1.0284 | 1.0912 |
| total\_weight\_g | 77,720 | 0.9473 | KDE (log1p scale) | 0.5289 | higher value, more detractors | 0.0050 | 2,359.7742 | 3,054.1240 |
| total\_volume\_cm3 | 77,720 | 0.9476 | KDE (log1p scale) | 0.5289 | higher value, more detractors | 0.0085 | 17,268.9553 | 22,096.2165 |
| payment\_installments\_max | 77,736 | 0.9568 | discrete frequencies | 0.5258 | higher value, more detractors | 0.0008 | 2.9116 | 3.1969 |
| freight\_ratio | 77,736 | 0.9611 | KDE | 0.5128 | higher value, more detractors | 0.0088 | 0.3029 | 0.3203 |
| n\_sellers | 77,736 | 0.9671 | discrete frequencies | 0.5165 | higher value, more detractors | 0.0041 | 1.0073 | 1.0429 |
| purchase\_hour | 77,736 | 0.9754 | discrete frequencies | 0.5012 | higher value, more detractors | 0.0003 | 14.7767 | 14.7568 |
| n\_categories | 77,736 | 0.9804 | discrete frequencies | 0.5047 | higher value, more detractors | 0.0016 | 0.9891 | 0.9991 |
| purchase\_dayofweek | 77,736 | 0.9832 | discrete frequencies | 0.5019 | higher value, more detractors | 0.0001 | 2.7638 | 2.7761 |
| category\_missing\_fraction | 77,736 | 0.9928 | discrete frequencies | 0.5036 | higher value, more detractors | 0.0004 | 0.0159 | 0.0219 |
| distance\_missing\_fraction | 77,736 | 0.9980 | discrete frequencies | 0.4991 | lower value, more detractors | 0.0000 | 0.0119 | 0.0100 |
| n\_payment\_methods | 77,736 | 0.9994 | discrete frequencies | 0.4997 | lower value, more detractors | 0.0000 | 1.0233 | 1.0227 |
| volume\_missing\_fraction | 77,736 | 0.9999 | discrete frequencies | 0.5000 | higher value, more detractors | 0.0000 | 0.0002 | 0.0003 |
| weight\_missing\_fraction | 77,736 | 0.9999 | discrete frequencies | 0.5000 | higher value, more detractors | 0.0000 | 0.0002 | 0.0003 |

&#91;image: Class-conditional distributions\]

**Check** all 24 contract predictors diagnosed against is\_detractor: PASS

**Files** (stages/s03\_eda/classification/outputs/, run 20261020T053142Z): numeric\_feature\_target\_is\_detractor.csv, figures/numeric\_vs\_is\_detractor.png, figures/numeric\_vs\_is\_detractor.csv, figures/numeric\_vs\_is\_detractor.json

## 3.7 Categorical features vs is\_detractor

**Approved solution:** Mutual information (`mutual_info_classif`, discrete, seed 42)

**What was done:** Four categorical predictors: mutual\_info\_classif (discrete, seed 42) and per-level detractor rates; calendar fields shown per level for the plots only. MI: customer\_state 0.0051, primary\_seller\_state 0.0009, primary\_category 0.0026, primary\_payment\_type 0.0000 nats.

| feature | levels | mutual\_information | lowest\_rate | highest\_rate |
| --- | --- | --- | --- | --- |
| customer\_state | 27 | 0.0051 | 0.0893 | 0.2596 |
| primary\_category | 72 | 0.0026 | 0.0000 | 0.5000 |
| primary\_seller\_state | 22 | 0.0009 | 0.0000 | 0.6667 |
| primary\_payment\_type | 4 | 0.0000 | 0.1411 | 0.1494 |

**customer\_state** (top 15 of 27 levels by count; all levels in categorical\_feature\_target\_is\_detractor.csv)

| level | n | share | detractors | detractor\_rate |
| --- | --- | --- | --- | --- |
| SP | 31,767 | 0.409 | 3,820 | 0.120 |
| RJ | 10,261 | 0.132 | 2,225 | 0.217 |
| MG | 9,248 | 0.119 | 1,217 | 0.132 |
| RS | 4,432 | 0.057 | 603 | 0.136 |
| PR | 3,959 | 0.051 | 491 | 0.124 |
| SC | 2,937 | 0.038 | 439 | 0.149 |
| BA | 2,653 | 0.034 | 528 | 0.199 |
| DF | 1,633 | 0.021 | 256 | 0.157 |
| GO | 1,629 | 0.021 | 244 | 0.150 |
| ES | 1,625 | 0.021 | 249 | 0.153 |
| PE | 1,292 | 0.017 | 234 | 0.181 |
| CE | 1,088 | 0.014 | 231 | 0.212 |
| PA | 792 | 0.010 | 174 | 0.220 |
| MT | 741 | 0.010 | 108 | 0.146 |
| MA | 610 | 0.008 | 134 | 0.220 |

**primary\_seller\_state** (top 15 of 22 levels by count; all levels in categorical\_feature\_target\_is\_detractor.csv)

| level | n | share | detractors | detractor\_rate |
| --- | --- | --- | --- | --- |
| SP | 55,348 | 0.712 | 8,531 | 0.154 |
| MG | 6,356 | 0.082 | 792 | 0.125 |
| PR | 6,034 | 0.078 | 869 | 0.144 |
| RJ | 3,162 | 0.041 | 472 | 0.149 |
| SC | 2,880 | 0.037 | 360 | 0.125 |
| RS | 1,457 | 0.019 | 143 | 0.098 |
| DF | 663 | 0.009 | 96 | 0.145 |
| BA | 437 | 0.006 | 48 | 0.110 |
| GO | 350 | 0.005 | 34 | 0.097 |
| PE | 293 | 0.004 | 30 | 0.102 |
| ES | 269 | 0.003 | 42 | 0.156 |
| MA | 163 | 0.002 | 37 | 0.227 |
| MT | 116 | 0.001 | 9 | 0.078 |
| CE | 62 | 0.001 | 7 | 0.113 |
| RN | 45 | 0.001 | 5 | 0.111 |

**primary\_payment\_type**

| level | n | share | detractors | detractor\_rate |
| --- | --- | --- | --- | --- |
| credit\_card | 58,644 | 0.754 | 8,709 | 0.149 |
| boleto | 15,788 | 0.203 | 2,297 | 0.145 |
| voucher | 2,503 | 0.032 | 374 | 0.149 |
| debit\_card | 801 | 0.010 | 113 | 0.141 |

**primary\_category** (top 15 of 72 levels by count; all levels in categorical\_feature\_target\_is\_detractor.csv)

| level | n | share | detractors | detractor\_rate |
| --- | --- | --- | --- | --- |
| bed\_bath\_table | 7,417 | 0.095 | 1,298 | 0.175 |
| health\_beauty | 6,339 | 0.082 | 861 | 0.136 |
| sports\_leisure | 6,304 | 0.081 | 832 | 0.132 |
| computers\_accessories | 5,425 | 0.070 | 907 | 0.167 |
| furniture\_decor | 5,202 | 0.067 | 894 | 0.172 |
| housewares | 4,209 | 0.054 | 564 | 0.134 |
| watches\_gifts | 4,137 | 0.053 | 634 | 0.153 |
| telephony | 3,443 | 0.044 | 531 | 0.154 |
| toys | 3,289 | 0.042 | 411 | 0.125 |
| cool\_stuff | 3,205 | 0.041 | 385 | 0.120 |
| garden\_tools | 2,990 | 0.038 | 400 | 0.134 |
| auto | 2,868 | 0.037 | 432 | 0.151 |
| perfumery | 2,538 | 0.033 | 344 | 0.136 |
| baby | 2,146 | 0.028 | 353 | 0.164 |
| electronics | 2,062 | 0.027 | 303 | 0.147 |

&#91;image: Detractor rate by level\]

**Check** all 24 contract predictors diagnosed against is\_detractor: PASS

**Files** (stages/s03\_eda/classification/outputs/, run 20261020T053142Z): categorical\_feature\_target\_is\_detractor.csv, figures/categorical\_vs\_is\_detractor.png, figures/categorical\_vs\_is\_detractor.csv, figures/categorical\_vs\_is\_detractor.json

## 3.8 Importance ranking

**Approved solution:** One ranking per task feeding s04 selection, over all 24 contract predictors (the ranking file has exactly 24 rows; G-42, G-61): absolute Spearman for regression, mutual information for classification (one measure per task, so cumulative shares are meaningful). Missingness, outliers and correlation/VIF among raw numeric features also reported here

**What was done:** Ranking over the 24 contract predictors by mutual information (discrete estimator for categorical features and features with at most 30 values, k-NN estimator for the rest): top 5 \['total\_freight', 'freight\_ratio', 'total\_volume\_cm3', 'total\_price', 'n\_items'\]; cut points {'0.95': 14, '0.99': 17}. Missingness, IQR outliers, Pearson/Spearman matrix and VIF on 76,810 complete rows; flagged groups: \[\]; identical columns: \[('weight\_missing\_fraction', 'volume\_missing\_fraction')\].

**Ranking** (mutual information):

| rank | feature | type | method | value | share | cumulative\_share |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | total\_freight | numeric | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0102 | 0.1313 | 0.1313 |
| 2 | freight\_ratio | numeric | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0088 | 0.1133 | 0.2447 |
| 3 | total\_volume\_cm3 | numeric | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0085 | 0.1094 | 0.3541 |
| 4 | total\_price | numeric | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0075 | 0.0967 | 0.4508 |
| 5 | n\_items | numeric | mutual\_info\_classif, discrete (contingency) | 0.0073 | 0.0936 | 0.5444 |
| 6 | customer\_state | categorical | mutual\_info\_classif, discrete (contingency) | 0.0051 | 0.0655 | 0.6098 |
| 7 | total\_weight\_g | numeric | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0050 | 0.0645 | 0.6743 |
| 8 | n\_products | numeric | mutual\_info\_classif, discrete (contingency) | 0.0044 | 0.0570 | 0.7313 |
| 9 | n\_sellers | numeric | mutual\_info\_classif, discrete (contingency) | 0.0041 | 0.0525 | 0.7838 |
| 10 | purchase\_month | numeric | mutual\_info\_classif, discrete (contingency) | 0.0040 | 0.0512 | 0.8350 |
| 11 | distance\_km\_max | numeric | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0035 | 0.0448 | 0.8798 |
| 12 | interstate\_share | numeric | mutual\_info\_classif, discrete (contingency) | 0.0026 | 0.0337 | 0.9135 |
| 13 | primary\_category | categorical | mutual\_info\_classif, discrete (contingency) | 0.0026 | 0.0335 | 0.9470 |
| 14 | n\_categories | numeric | mutual\_info\_classif, discrete (contingency) | 0.0016 | 0.0199 | 0.9669 |
| 15 | primary\_seller\_state | categorical | mutual\_info\_classif, discrete (contingency) | 0.0009 | 0.0114 | 0.9783 |
| 16 | payment\_installments\_max | numeric | mutual\_info\_classif, discrete (contingency) | 0.0008 | 0.0102 | 0.9885 |
| 17 | category\_missing\_fraction | numeric | mutual\_info\_classif, discrete (contingency) | 0.0004 | 0.0055 | 0.9940 |
| 18 | purchase\_hour | numeric | mutual\_info\_classif, discrete (contingency) | 0.0003 | 0.0041 | 0.9981 |
| 19 | purchase\_dayofweek | numeric | mutual\_info\_classif, discrete (contingency) | 0.0001 | 0.0014 | 0.9995 |
| 20 | distance\_missing\_fraction | numeric | mutual\_info\_classif, discrete (contingency) | 0.0000 | 0.0004 | 0.9999 |
| 21 | primary\_payment\_type | categorical | mutual\_info\_classif, discrete (contingency) | 0.0000 | 0.0001 | 1.0000 |
| 22 | volume\_missing\_fraction | numeric | mutual\_info\_classif, discrete (contingency) | 0.0000 | 0.0000 | 1.0000 |
| 23 | weight\_missing\_fraction | numeric | mutual\_info\_classif, discrete (contingency) | 0.0000 | 0.0000 | 1.0000 |
| 24 | n\_payment\_methods | numeric | mutual\_info\_classif, discrete (contingency) | 0.0000 | 0.0000 | 1.0000 |

&#91;image: Cumulative importance\]

**Missingness, outliers and VIF** (raw features, pre-cutoff orders):

| feature | type | missing\_share | distinct\_values | share\_outside\_1\_5\_iqr | share\_outside\_3\_iqr | vif | vif\_note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| n\_items | numeric | 0.0000 | 17 | 0.1001 | 0.1001 | 1.6467 |  |
| n\_products | numeric | 0.0000 | 7 | 0.0327 | 0.0327 | 1.8025 |  |
| n\_sellers | numeric | 0.0000 | 5 | 0.0120 | 0.0120 | 1.8561 |  |
| n\_categories | numeric | 0.0000 | 4 | 0.0234 | 0.0234 | 4.9191 |  |
| total\_price | numeric | 0.0000 | 6,423 | 0.0797 | 0.0408 | 1.4752 |  |
| total\_freight | numeric | 0.0000 | 6,782 | 0.0969 | 0.0488 | 3.3220 |  |
| freight\_ratio | numeric | 0.0000 | 33,482 | 0.0683 | 0.0230 | 1.2595 |  |
| total\_weight\_g | numeric | 0.0002 | 2,592 | 0.1408 | 0.0828 | 3.4977 |  |
| total\_volume\_cm3 | numeric | 0.0002 | 5,547 | 0.0978 | 0.0434 | 3.4242 |  |
| weight\_missing\_fraction | numeric | 0.0000 | 2 | 0.0002 | 0.0002 | — | constant on the complete rows |
| volume\_missing\_fraction | numeric | 0.0000 | 2 | 0.0002 | 0.0002 | — | constant on the complete rows |
| primary\_category | categorical | 0.0000 | 72 | — | — | — |  |
| category\_missing\_fraction | numeric | 0.0000 | 10 | 0.0171 | 0.0171 | 4.3683 |  |
| customer\_state | categorical | 0.0000 | 27 | — | — | — |  |
| primary\_seller\_state | categorical | 0.0000 | 22 | — | — | — |  |
| distance\_km\_max | numeric | 0.0117 | 72,614 | 0.0800 | 0.0068 | 1.6817 |  |
| distance\_missing\_fraction | numeric | 0.0000 | 3 | 0.0117 | 0.0117 | — | constant on the complete rows |
| interstate\_share | numeric | 0.0000 | 5 | 0.0000 | 0.0000 | 1.4985 |  |
| purchase\_month | numeric | 0.0000 | 12 | 0.0000 | 0.0000 | 1.0030 |  |
| purchase\_dayofweek | numeric | 0.0000 | 7 | 0.0000 | 0.0000 | 1.0021 |  |
| purchase\_hour | numeric | 0.0000 | 24 | 0.0000 | 0.0000 | 1.0006 |  |
| primary\_payment\_type | categorical | 0.0000 | 4 | — | — | — |  |
| payment\_installments\_max | numeric | 0.0000 | 22 | 0.0662 | 0.0016 | 1.1541 |  |
| n\_payment\_methods | numeric | 0.0000 | 2 | 0.0232 | 0.0232 | 1.0023 |  |

**Collinearity** (|Pearson| or |Spearman| > 0.9, VIF > 10.0; VIF on 76,810 complete rows):

| feature\_a | feature\_b | pearson | spearman | identical |
| --- | --- | --- | --- | --- |
| weight\_missing\_fraction | volume\_missing\_fraction | 1.0000 | 1.0000 | yes |

&#91;image: Correlation heatmap\]

**Skewness of the log1p candidates** (for s04 4.2):

| feature | skewness | threshold | log1p |
| --- | --- | --- | --- |
| total\_price | 10.0561 | 1.0000 | yes |
| total\_freight | 8.0991 | 1.0000 | yes |
| total\_weight\_g | 6.5946 | 1.0000 | yes |
| total\_volume\_cm3 | 7.4804 | 1.0000 | yes |
| distance\_km\_max | 1.6391 | 1.0000 | yes |

**Candidate rationale** (finding → change → stage that tests it):

| finding | evidence | change\_it\_motivates | stage\_that\_tests\_it |
| --- | --- | --- | --- |
| total\_price pre-cutoff skewness 10.06 (above 1) | eda\_summary.json:log1p\_candidates | log1p on total\_price | s04 4.2 (applied), s06 (fitted inside folds) |
| total\_freight pre-cutoff skewness 8.10 (above 1) | eda\_summary.json:log1p\_candidates | log1p on total\_freight | s04 4.2 (applied), s06 (fitted inside folds) |
| total\_weight\_g pre-cutoff skewness 6.59 (above 1) | eda\_summary.json:log1p\_candidates | log1p on total\_weight\_g | s04 4.2 (applied), s06 (fitted inside folds) |
| total\_volume\_cm3 pre-cutoff skewness 7.48 (above 1) | eda\_summary.json:log1p\_candidates | log1p on total\_volume\_cm3 | s04 4.2 (applied), s06 (fitted inside folds) |
| distance\_km\_max pre-cutoff skewness 1.64 (above 1) | eda\_summary.json:log1p\_candidates | log1p on distance\_km\_max | s04 4.2 (applied), s06 (fitted inside folds) |
| weight\_missing\_fraction and volume\_missing\_fraction are identical on every pre-cutoff order | collinear\_pairs.csv | drop one of weight\_missing\_fraction, volume\_missing\_fraction automatically (duplicate rule) | s04 4.3 |
| top 14 of 24 features reach 95% of total mutual information | importance\_ranking.csv:cumulative\_share | selected set = top 14 if the team picks 95% | s04 4.4 (threshold fixed before fitting), s06 |
| top 17 of 24 features reach 99% of total mutual information | importance\_ranking.csv:cumulative\_share | selected set = top 17 if the team picks 99% | s04 4.4 (threshold fixed before fitting), s06 |
| detractor prevalence 14.78% (11,493 of 77,736 pre-cutoff orders) | target\_classification\_is\_detractor.csv | average precision with the prevalence baseline as the primary metric (s01) | s06, s08 |
| detractor rate ranges 10.7% to 22.5% across purchase months with at least 100 orders | outcome\_trends.csv | time-ordered expanding folds; class support per fold | s05 5.5, 5.8 |
| detractor rate 57.2% for orders delivered after the promised date vs 9.5% on time (description only, G-35) | eda\_summary.json:detractor\_rate\_by\_late | none: lateness is known only after delivery and is never a predictor; it explains why checkout-time signal is limited | s09 (discussion) |
| candidate product\_photos\_qty: ROC-AUC 0.480, overlap 96.3%, MI rank 26 of 36 in the extended ranking | candidate\_screen\_3\_10.csv, candidate\_ranking\_extended.csv | team adopts or drops it at the s03 gate (G-68); if adopted it joins the classification selection pool with its planned transform | s04 4.4 (pool), s06 |
| candidate product\_description\_lenght: ROC-AUC 0.492, overlap 97.8%, MI rank 9 of 36 in the extended ranking | candidate\_screen\_3\_10.csv, candidate\_ranking\_extended.csv | team adopts or drops it at the s03 gate (G-68); if adopted it joins the classification selection pool with its planned transform | s04 4.4 (pool), s06 |
| candidate product\_name\_lenght: ROC-AUC 0.504, overlap 97.2%, MI rank 36 of 36 in the extended ranking | candidate\_screen\_3\_10.csv, candidate\_ranking\_extended.csv | team adopts or drops it at the s03 gate (G-68); if adopted it joins the classification selection pool with its planned transform | s04 4.4 (pool), s06 |
| candidate est\_delivery\_days: ROC-AUC 0.538, overlap 95.0%, MI rank 16 of 36 in the extended ranking | candidate\_screen\_3\_11.csv, candidate\_ranking\_extended.csv | team adopts or drops it at the s03 gate (G-68); if adopted it joins the classification selection pool with its planned transform | s04 4.4 (pool), s06 |
| candidate customer\_region: overlap 95.4%, MI rank 23 of 36 in the extended ranking | candidate\_screen\_3\_12.csv, candidate\_ranking\_extended.csv | team adopts or drops it at the s03 gate (G-68); if adopted it joins the classification selection pool with its planned transform | s04 4.4 (pool), s06 |
| candidate seller\_region: overlap 97.9%, MI rank 29 of 36 in the extended ranking | candidate\_screen\_3\_12.csv, candidate\_ranking\_extended.csv | team adopts or drops it at the s03 gate (G-68); if adopted it joins the classification selection pool with its planned transform | s04 4.4 (pool), s06 |
| candidate region\_pair: overlap 94.9%, MI rank 20 of 36 in the extended ranking | candidate\_screen\_3\_12.csv, candidate\_ranking\_extended.csv | team adopts or drops it at the s03 gate (G-68); if adopted it joins the classification selection pool with its planned transform | s04 4.4 (pool), s06 |
| candidate seller\_prior\_review\_mean: ROC-AUC 0.441, overlap 90.5%, MI rank 1 of 36 in the extended ranking | candidate\_screen\_3\_13.csv, candidate\_ranking\_extended.csv | team adopts or drops it at the s03 gate (G-68); if adopted it joins the classification selection pool with its planned transform | s04 4.4 (pool), s06 |
| candidate seller\_prior\_review\_count: ROC-AUC 0.508, overlap 96.3%, MI rank 22 of 36 in the extended ranking | candidate\_screen\_3\_13.csv, candidate\_ranking\_extended.csv | team adopts or drops it at the s03 gate (G-68); if adopted it joins the classification selection pool with its planned transform | s04 4.4 (pool), s06 |
| candidate seller\_prior\_detractor\_share: ROC-AUC 0.557, overlap 90.6%, MI rank 5 of 36 in the extended ranking | candidate\_screen\_3\_13.csv, candidate\_ranking\_extended.csv | team adopts or drops it at the s03 gate (G-68); if adopted it joins the classification selection pool with its planned transform | s04 4.4 (pool), s06 |
| candidate seller\_prior\_delivered\_count: ROC-AUC 0.507, overlap 96.3%, MI rank 19 of 36 in the extended ranking | candidate\_screen\_3\_13.csv, candidate\_ranking\_extended.csv | team adopts or drops it at the s03 gate (G-68); if adopted it joins the classification selection pool with its planned transform | s04 4.4 (pool), s06 |
| candidate seller\_prior\_late\_share: ROC-AUC 0.536, overlap 90.2%, MI rank 8 of 36 in the extended ranking | candidate\_screen\_3\_13.csv, candidate\_ranking\_extended.csv | team adopts or drops it at the s03 gate (G-68); if adopted it joins the classification selection pool with its planned transform | s04 4.4 (pool), s06 |

**Check** no order on or after the test cutoff loaded: PASS (latest purchase 2018-05-26 12:12:15, cutoff 2018-05-26 12:16:34) **Check** importance\_ranking has the 24 contract predictors and ends at cumulative share 1.0: PASS (24 rows) **Check** ranking measure is the pre-registered one: PASS

**Files** (stages/s03\_eda/classification/outputs/, run 20261020T053142Z): feature\_quality.csv, collinear\_pairs.csv, numeric\_correlations.csv, figures/numeric\_correlation\_heatmap.png, figures/numeric\_correlation\_heatmap.csv, figures/numeric\_correlation\_heatmap.json, importance\_ranking.csv, figures/cumulative\_importance.png, figures/cumulative\_importance.csv, figures/cumulative\_importance.json, candidate\_rationale.csv, eda\_summary.json, decision.json

## 3.9 Human gate (review pack for s04 decisions)

**Approved solution:** Human gate (G-31): implementation stops after s03. All EDA results are presented to the team, and s04 runs only after the team records its decisions (threshold, collinearity drops)

**What was done:** eda\_review\_pack.md lists every table and figure above, the ranking with both cut points, the flagged collinear groups and the YAML block the team fills in spec/human\_decisions.yaml.

**Conclusion:** Stop: s04 waits for the team's threshold and collinearity decisions (G-31).

Threshold options over the 24 contract predictors (the team chose 99%, G-70):

| Threshold | Features kept | Features (in ranking order) |
| --- | --- | --- |
| 95% | 14 | total\_freight, freight\_ratio, total\_volume\_cm3, total\_price, n\_items, customer\_state, total\_weight\_g, n\_products, n\_sellers, purchase\_month, distance\_km\_max, interstate\_share, primary\_category, n\_categories |
| 99% | 17 | total\_freight, freight\_ratio, total\_volume\_cm3, total\_price, n\_items, customer\_state, total\_weight\_g, n\_products, n\_sellers, purchase\_month, distance\_km\_max, interstate\_share, primary\_category, n\_categories, primary\_seller\_state, payment\_installments\_max, category\_missing\_fraction |

Flagged collinear groups needing a team decision: none. Identical columns, dropped automatically by the s04 duplicate rule: weight\_missing\_fraction = volume\_missing\_fraction.

**Check** review pack lists both cut points and every flagged group: PASS

**Files** (stages/s03\_eda/classification/outputs/, run 20261020T053142Z): figures/cumulative\_importance.png, figures/cumulative\_importance.csv, figures/cumulative\_importance.json, eda\_review\_pack.md

## 3.10 Candidate screen: product fields and extended ranking (G-68)

**Approved solution:** Screen product\_photos\_qty, product\_description\_lenght and product\_name\_lenght (value of the primary item) for classification only; not predictors unless adopted at the gate (G-68). The extended ranking covers every screening candidate.

**What was done:** Screening columns (not predictors) diagnosed against is\_detractor with the 3.6 measures; numeric ones also with skewness, correlation with the 20 numeric predictors and VIF in the extended numeric set. Product fields (primary item): product\_photos\_qty: rank 26, MI 0.0005, ROC-AUC 0.480, overlap 96.3%; product\_description\_lenght: rank 9, MI 0.0054, ROC-AUC 0.492, overlap 97.8%; product\_name\_lenght: rank 36, MI 0.0000, ROC-AUC 0.504, overlap 97.2%. Extended ranking over 24 + 12 candidates; cut points {'0.95': 22, '0.99': 26} (official 3.8 ranking unchanged at 24).

**Reasoning:** The extended ranking shows where each candidate would enter; s04 recomputes the cumulative share over the agreed pool (24 + adopted candidates). Screening on pre-cutoff orders and then choosing is a post-hoc addition; the report says so.

**Conclusion:** Team decision at the gate: adopt or drop each candidate (human\_decisions.yaml).

| feature | adopted (G-70) | kind | n | missing\_share | overlap\_coefficient | roc\_auc | direction | mutual\_information | rank\_in\_extended | inside\_95\_cut | inside\_99\_cut | skewness | vif\_in\_extended\_set | planned\_transform |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| product\_photos\_qty | yes | numeric | 76,441 | 0.0167 | 0.9631 | 0.4796 | lower value, more detractors | 0.0005 | 26 | no | yes | 1.8939 | 1.0451 | scaled, never logged (count) |
| product\_description\_lenght | yes | numeric | 76,441 | 0.0167 | 0.9776 | 0.4923 | lower value, more detractors | 0.0054 | 9 | yes | yes | 2.0451 | 1.0911 | log1p if pre-cutoff skewness > 1, then scaled |
| product\_name\_lenght | no | numeric | 76,441 | 0.0167 | 0.9719 | 0.5040 | higher value, more detractors | 0.0000 | 36 | no | no | -0.8842 | 1.0594 | log1p if pre-cutoff skewness > 1, then scaled |

&#91;image: Product fields\]

**Extended ranking** (24 contract predictors + 12 screening candidates, mutual information; cut points {'0.95': 22, '0.99': 26}). The official 3.8 ranking stays at 24; s04 ranks the pool from these values (section below).

| rank | feature | candidate | card | value | share | cumulative\_share |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | seller\_prior\_review\_mean | yes | 3.1300 | 0.0110 | 0.0923 | 0.0923 |
| 2 | total\_freight | no | 3.8000 | 0.0102 | 0.0860 | 0.1783 |
| 3 | freight\_ratio | no | 3.8000 | 0.0088 | 0.0742 | 0.2525 |
| 4 | total\_volume\_cm3 | no | 3.8000 | 0.0085 | 0.0716 | 0.3242 |
| 5 | seller\_prior\_detractor\_share | yes | 3.1300 | 0.0080 | 0.0671 | 0.3913 |
| 6 | total\_price | no | 3.8000 | 0.0075 | 0.0633 | 0.4546 |
| 7 | n\_items | no | 3.8000 | 0.0073 | 0.0613 | 0.5159 |
| 8 | seller\_prior\_late\_share | yes | 3.1300 | 0.0062 | 0.0524 | 0.5683 |
| 9 | product\_description\_lenght | yes | 3.1000 | 0.0054 | 0.0451 | 0.6134 |
| 10 | customer\_state | no | 3.8000 | 0.0051 | 0.0429 | 0.6563 |
| 11 | total\_weight\_g | no | 3.8000 | 0.0050 | 0.0422 | 0.6985 |
| 12 | n\_products | no | 3.8000 | 0.0044 | 0.0373 | 0.7358 |
| 13 | n\_sellers | no | 3.8000 | 0.0041 | 0.0344 | 0.7702 |
| 14 | purchase\_month | no | 3.8000 | 0.0040 | 0.0335 | 0.8037 |
| 15 | distance\_km\_max | no | 3.8000 | 0.0035 | 0.0293 | 0.8330 |
| 16 | est\_delivery\_days | yes | 3.1100 | 0.0030 | 0.0249 | 0.8579 |
| 17 | interstate\_share | no | 3.8000 | 0.0026 | 0.0221 | 0.8800 |
| 18 | primary\_category | no | 3.8000 | 0.0026 | 0.0219 | 0.9019 |
| 19 | seller\_prior\_delivered\_count | yes | 3.1300 | 0.0022 | 0.0184 | 0.9203 |
| 20 | region\_pair | yes | 3.1200 | 0.0019 | 0.0157 | 0.9360 |
| 21 | n\_categories | no | 3.8000 | 0.0016 | 0.0130 | 0.9491 |
| 22 | seller\_prior\_review\_count | yes | 3.1300 | 0.0015 | 0.0126 | 0.9617 |
| 23 | customer\_region | yes | 3.1200 | 0.0012 | 0.0101 | 0.9718 |
| 24 | primary\_seller\_state | no | 3.8000 | 0.0009 | 0.0075 | 0.9793 |
| 25 | payment\_installments\_max | no | 3.8000 | 0.0008 | 0.0067 | 0.9860 |
| 26 | product\_photos\_qty | yes | 3.1000 | 0.0005 | 0.0045 | 0.9905 |
| 27 | category\_missing\_fraction | no | 3.8000 | 0.0004 | 0.0036 | 0.9941 |
| 28 | purchase\_hour | no | 3.8000 | 0.0003 | 0.0027 | 0.9968 |
| 29 | seller\_region | yes | 3.1200 | 0.0002 | 0.0020 | 0.9988 |
| 30 | purchase\_dayofweek | no | 3.8000 | 0.0001 | 0.0009 | 0.9997 |
| 31 | distance\_missing\_fraction | no | 3.8000 | 0.0000 | 0.0002 | 0.9999 |
| 32 | primary\_payment\_type | no | 3.8000 | 0.0000 | 0.0001 | 1.0000 |
| 33 | volume\_missing\_fraction | no | 3.8000 | 0.0000 | 0.0000 | 1.0000 |
| 34 | weight\_missing\_fraction | no | 3.8000 | 0.0000 | 0.0000 | 1.0000 |
| 35 | n\_payment\_methods | no | 3.8000 | 0.0000 | 0.0000 | 1.0000 |
| 36 | product\_name\_lenght | yes | 3.1000 | 0.0000 | 0.0000 | 1.0000 |

&#91;image: Extended ranking\]

**Check** candidate screen 3.10 covers every product candidate: PASS (3 candidates) **Check** extended ranking holds the 24 predictors and every candidate, ends at 1.0; official ranking unchanged at 24: PASS (36 rows)

**Files** (stages/s03\_eda/classification/outputs/, run 20261020T053142Z): figures/candidate\_screen.png, figures/candidate\_screen.csv, figures/candidate\_screen.json, candidate\_screen\_3\_10.csv, candidate\_ranking\_extended.csv, candidate\_collinear\_pairs.csv, figures/candidate\_ranking\_extended.png, figures/candidate\_ranking\_extended.csv, figures/candidate\_ranking\_extended.json, eda\_summary.json

## 3.11 Candidate screen: promised delivery days (G-69)

**Approved solution:** Screen est\_delivery\_days = estimated delivery date minus purchase, classification only; G-35 reopened for this screen only (G-69).

**What was done:** Screening columns (not predictors) diagnosed against is\_detractor with the 3.6 measures; numeric ones also with skewness, correlation with the 20 numeric predictors and VIF in the extended numeric set. Promised delivery days: est\_delivery\_days: rank 16, MI 0.0030, ROC-AUC 0.538, overlap 95.0%.

**Reasoning:** G-35 is reopened for this screen only. Olist's own promise is measured here; in production the promise would come from the task 1 prediction, so if adopted the classifier trains on out-of-fold task 1 predictions, which makes classification s06 depend on regression s06.

| feature | adopted (G-70) | kind | n | missing\_share | overlap\_coefficient | roc\_auc | direction | mutual\_information | rank\_in\_extended | inside\_95\_cut | inside\_99\_cut | skewness | vif\_in\_extended\_set | planned\_transform |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| est\_delivery\_days | no | numeric | 77,736 | 0.0000 | 0.9501 | 0.5378 | higher value, more detractors | 0.0030 | 16 | yes | yes | 1.2476 | 1.7468 | log1p if pre-cutoff skewness > 1, then scaled; in production fed by the task 1 prediction, so if adopted the classifier trains on out-of-fold task 1 predictions (G-69) |

&#91;image: Promised delivery days\]

**Check** candidate screen 3.11 covers every promise candidate: PASS (1 candidates)

**Files** (stages/s03\_eda/classification/outputs/, run 20261020T053142Z): figures/candidate\_screen\_promise.png, figures/candidate\_screen\_promise.csv, figures/candidate\_screen\_promise.json, candidate\_screen\_3\_11.csv, eda\_summary.json

## 3.12 Candidate screen: regions (G-69)

**Approved solution:** Screen customer\_region, seller\_region (IBGE macro-regions) and region\_pair (customer>seller), classification only (G-69).

**What was done:** Screening columns (not predictors) diagnosed against is\_detractor with the 3.6 measures; numeric ones also with skewness, correlation with the 20 numeric predictors and VIF in the extended numeric set. Regions (IBGE macro-regions; pair = customer>seller): customer\_region: rank 23, MI 0.0012, overlap 95.4%; seller\_region: rank 29, MI 0.0002, overlap 97.9%; region\_pair: rank 20, MI 0.0019, overlap 94.9%. Per-level detractor rates in candidate\_screen\_levels.csv.

**Reasoning:** A region has 5 levels instead of 27 states, so each level holds more orders; the pair captures logistics corridors. Mutual information with many levels is biased upward, so compare the region and state values with that in mind.

| feature | adopted (G-70) | kind | n | missing\_share | overlap\_coefficient | roc\_auc | direction | mutual\_information | rank\_in\_extended | inside\_95\_cut | inside\_99\_cut | skewness | vif\_in\_extended\_set | planned\_transform |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| customer\_region | no | categorical | 77,736 | 0.0000 | 0.9538 | — | — | 0.0012 | 23 | no | yes | — | — | one-hot (drop-first for linear/logistic), unknown level handled |
| seller\_region | no | categorical | 77,736 | 0.0000 | 0.9786 | — | — | 0.0002 | 29 | no | no | — | — | one-hot (drop-first for linear/logistic), unknown level handled |
| region\_pair | no | categorical | 77,736 | 0.0000 | 0.9494 | — | — | 0.0019 | 20 | yes | yes | — | — | one-hot (drop-first for linear/logistic), unknown level handled |

Per-level detractor rates:

| feature | level | n | share | detractors | detractor\_rate |
| --- | --- | --- | --- | --- | --- |
| customer\_region | Center-West | 4,573 | 0.0588 | 691 | 0.1511 |
| customer\_region | North | 1,496 | 0.0192 | 278 | 0.1858 |
| customer\_region | Northeast | 7,438 | 0.0957 | 1,480 | 0.1990 |
| customer\_region | South | 11,328 | 0.1457 | 1,533 | 0.1353 |
| customer\_region | Southeast | 52,901 | 0.6805 | 7,511 | 0.1420 |
| seller\_region | Center-West | 1,166 | 0.0150 | 141 | 0.1209 |
| seller\_region | North | 25 | 0.0003 | 6 | 0.2400 |
| seller\_region | Northeast | 1,039 | 0.0134 | 137 | 0.1319 |
| seller\_region | South | 10,371 | 0.1334 | 1,372 | 0.1323 |
| seller\_region | Southeast | 65,135 | 0.8379 | 9,837 | 0.1510 |

region\_pair, top 15 levels by count:

| feature | level | n | share | detractors | detractor\_rate |
| --- | --- | --- | --- | --- | --- |
| region\_pair | Southeast>Southeast | 45,086 | 0.5800 | 6,460 | 0.1433 |
| region\_pair | South>Southeast | 8,689 | 0.1118 | 1,277 | 0.1470 |
| region\_pair | Southeast>South | 6,525 | 0.0839 | 890 | 0.1364 |
| region\_pair | Northeast>Southeast | 6,283 | 0.0808 | 1,263 | 0.2010 |
| region\_pair | Center-West>Southeast | 3,819 | 0.0491 | 603 | 0.1579 |
| region\_pair | South>South | 2,427 | 0.0312 | 226 | 0.0931 |
| region\_pair | North>Southeast | 1,258 | 0.0162 | 234 | 0.1860 |
| region\_pair | Southeast>Center-West | 721 | 0.0093 | 87 | 0.1207 |
| region\_pair | Northeast>South | 720 | 0.0093 | 159 | 0.2208 |
| region\_pair | Southeast>Northeast | 551 | 0.0071 | 71 | 0.1289 |
| region\_pair | Center-West>South | 528 | 0.0068 | 67 | 0.1269 |
| region\_pair | Northeast>Northeast | 289 | 0.0037 | 30 | 0.1038 |
| region\_pair | North>South | 171 | 0.0022 | 30 | 0.1754 |
| region\_pair | Center-West>Center-West | 154 | 0.0020 | 13 | 0.0844 |
| region\_pair | Northeast>Center-West | 142 | 0.0018 | 27 | 0.1901 |

&#91;image: Regions\]

**Check** candidate screen 3.12 covers every region candidate: PASS (3 candidates)

**Files** (stages/s03\_eda/classification/outputs/, run 20261020T053142Z): figures/candidate\_screen\_region.png, figures/candidate\_screen\_region.csv, figures/candidate\_screen\_region.json, candidate\_screen\_3\_12.csv, candidate\_screen\_levels.csv, eda\_summary.json

## 3.13 Candidate screen: seller history at checkout (G-69)

**Approved solution:** Screen the primary seller's history at checkout: prior review mean, review count, detractor share, delivered count and late share, counting only events strictly before the purchase second, never the order's own, and never a review answered before its own order's purchase (G-69, G-71).

**What was done:** Screening columns (not predictors) diagnosed against is\_detractor with the 3.6 measures; numeric ones also with skewness, correlation with the 20 numeric predictors and VIF in the extended numeric set. Seller history at checkout: seller\_prior\_review\_mean: rank 1, MI 0.0110, ROC-AUC 0.441, overlap 90.5%; seller\_prior\_review\_count: rank 22, MI 0.0015, ROC-AUC 0.508, overlap 96.3%; seller\_prior\_detractor\_share: rank 5, MI 0.0080, ROC-AUC 0.557, overlap 90.6%; seller\_prior\_delivered\_count: rank 19, MI 0.0022, ROC-AUC 0.507, overlap 96.3%; seller\_prior\_late\_share: rank 8, MI 0.0062, ROC-AUC 0.536, overlap 90.2%.

**Reasoning:** Only the primary seller's events strictly before the purchase second count (reviews at their answer time, deliveries at delivery time) and the order's own events never count; s02 checks this against a direct recomputation on 2,000 orders. Sellers without history are missing, with the counts at 0.

| feature | adopted (G-70) | kind | n | missing\_share | overlap\_coefficient | roc\_auc | direction | mutual\_information | rank\_in\_extended | inside\_95\_cut | inside\_99\_cut | skewness | vif\_in\_extended\_set | planned\_transform |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| seller\_prior\_review\_mean | yes | numeric | 72,429 | 0.0683 | 0.9054 | 0.4405 | lower value, more detractors | 0.0110 | 1 | yes | yes | -1.8287 | 5.1024 | scaled; missing for sellers without an earlier review (imputed in folds with a missing indicator) |
| seller\_prior\_review\_count | no | numeric | 77,736 | 0.0000 | 0.9625 | 0.5076 | higher value, more detractors | 0.0015 | 22 | yes | yes | 2.6682 | 1,445.1021 | log1p if pre-cutoff skewness > 1, then scaled |
| seller\_prior\_detractor\_share | no | numeric | 72,429 | 0.0683 | 0.9057 | 0.5573 | higher value, more detractors | 0.0080 | 5 | yes | yes | 3.0601 | 5.0489 | scaled, never logged (share); missing as for the mean |
| seller\_prior\_delivered\_count | no | numeric | 77,736 | 0.0000 | 0.9629 | 0.5069 | higher value, more detractors | 0.0022 | 19 | yes | yes | 2.6105 | 1,446.0587 | log1p if pre-cutoff skewness > 1, then scaled |
| seller\_prior\_late\_share | no | numeric | 73,017 | 0.0607 | 0.9017 | 0.5359 | higher value, more detractors | 0.0062 | 8 | yes | yes | 5.6150 | 1.2132 | scaled, never logged (share); missing when no earlier delivery |

**Collinear pair among the candidates:**

| feature\_a | feature\_b | pearson | spearman | identical |
| --- | --- | --- | --- | --- |
| seller\_prior\_review\_count | seller\_prior\_delivered\_count | 0.9997 | 0.9990 | no |

&#91;image: Seller history\]

**Check** candidate screen 3.13 covers every seller\_history candidate: PASS (5 candidates)

**Files** (stages/s03\_eda/classification/outputs/, run 20261020T053142Z): figures/candidate\_screen\_seller\_history.png, figures/candidate\_screen\_seller\_history.csv, figures/candidate\_screen\_seller\_history.json, candidate\_screen\_3\_13.csv, candidate\_collinear\_pairs.csv, eda\_summary.json

# Part B — Review record (history: rounds 1–3, do not cite)

The cards below are kept exactly as the team reviewed them in rounds 1–3 (classification runs 20261019T081206Z, 20261019T140130Z, 20261019T151336Z), so the comments and the decision trail stay readable. Their numbers are superseded by Part A above (CR-042).

## 3.2 Classification target

**Approved solution:** `is_detractor` bar chart; counts, share of low reviews (≤ 2) and normal reviews (≥ 3)

**What was done:** 77,971 pre-cutoff orders: 11,554 low reviews (score <= 2, 14.82%) and 66,417 normal reviews (score >= 3, 85.18%).

**Conclusion:** Imbalanced target: average precision is read against the prevalence baseline.

| class | orders | share |
| --- | --- | --- |
| low review (score <= 2), is\_detractor = 1 | 11,554 | 0.1482 |
| normal review (score >= 3), is\_detractor = 0 | 66,417 | 0.8518 |
| total | 77,971 | 1.0000 |

&#91;image: is\_detractor counts\]

**Files** (local, run 20261019T081206Z): target\_classification\_is\_detractor.csv, figures/target\_is\_detractor\_bar.png, figures/target\_is\_detractor\_bar.csv, figures/target\_is\_detractor\_bar.json, eda\_summary.json

## 3.3 Outcome trends

**Approved solution:** By purchase month: median lead time, late-vs-promised rate, detractor rate, with counts (not volume only)

**What was done:** 20 purchase months; over the 18 months with at least 100 orders: detractor rate 10.7% to 22.5%, late-vs-promised rate 0.8% to 21.1%, median lead time 8.9 to 17.9 days; every month is in the table with its counts.

**Reasoning:** Late is delivery after order\_estimated\_delivery\_date, used here only as a description (G-35).

| month | orders | orders\_with\_lead\_time | median\_lead\_days | late\_vs\_promised\_rate | orders\_with\_review | detractor\_rate |
| --- | --- | --- | --- | --- | --- | --- |
| 2016-09 | 1 | 0 | — | — | 1 | 1.000 |
| 2016-10 | 285 | 262 | 17.882 | 0.008 | 285 | 0.218 |
| 2016-12 | 1 | 1 | 4.693 | 0.000 | 1 | 0.000 |
| 2017-01 | 777 | 741 | 10.715 | 0.030 | 777 | 0.148 |
| 2017-02 | 1,708 | 1,643 | 10.950 | 0.028 | 1,708 | 0.138 |
| 2017-03 | 2,598 | 2,527 | 10.123 | 0.055 | 2,598 | 0.128 |
| 2017-04 | 2,360 | 2,290 | 12.743 | 0.077 | 2,360 | 0.148 |
| 2017-05 | 3,606 | 3,517 | 9.783 | 0.034 | 3,606 | 0.118 |
| 2017-06 | 3,181 | 3,111 | 10.802 | 0.038 | 3,181 | 0.120 |
| 2017-07 | 3,911 | 3,842 | 10.152 | 0.034 | 3,911 | 0.110 |
| 2017-08 | 4,241 | 4,165 | 9.770 | 0.033 | 4,241 | 0.107 |
| 2017-09 | 4,194 | 4,118 | 10.314 | 0.051 | 4,194 | 0.116 |
| 2017-10 | 4,510 | 4,446 | 10.249 | 0.052 | 4,510 | 0.119 |
| 2017-11 | 7,360 | 7,237 | 12.627 | 0.141 | 7,360 | 0.177 |
| 2017-12 | 5,561 | 5,461 | 13.123 | 0.083 | 5,561 | 0.158 |
| 2018-01 | 7,126 | 7,013 | 11.805 | 0.065 | 7,126 | 0.148 |
| 2018-02 | 6,573 | 6,507 | 14.262 | 0.159 | 6,573 | 0.200 |
| 2018-03 | 7,106 | 6,948 | 13.339 | 0.211 | 7,106 | 0.225 |
| 2018-04 | 6,862 | 6,751 | 9.305 | 0.052 | 6,862 | 0.128 |
| 2018-05 | 6,010 | 5,936 | 8.902 | 0.092 | 6,010 | 0.118 |

&#91;image: Outcome trends\]

**Files** (local, run 20261019T081206Z): outcome\_trends.csv, figures/outcome\_trends.png, figures/outcome\_trends.csv, figures/outcome\_trends.json, eda\_summary.json

## 3.6 Numeric features vs is\_detractor

**Approved solution:** KDE per class with overlap coefficient (0% = perfect separation, 100% = no signal) and per-feature ROC-AUC on the same rows

**What was done:** 20 numeric predictors: class-conditional distributions with the overlap coefficient (KDE for continuous features, class frequencies for features with at most 30 values), per-feature ROC-AUC and mutual information on the same rows; lowest overlap: total\_freight (86.6%, ROC-AUC 0.587).

**Reasoning:** A KDE smears an integer count into values that cannot occur, so features with few values use the class frequencies; the five log1p candidates use the KDE on the log1p scale (the coefficient does not change under a monotone transform). Flagged for the team (decision 2).

| feature | n | overlap\_coefficient | overlap\_method | roc\_auc | direction | mutual\_information | mean\_class\_0 | mean\_class\_1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| total\_freight | 77,971 | 0.8660 | KDE (log1p scale) | 0.5870 | higher value, more detractors | 0.0108 | 21.4452 | 27.2690 |
| purchase\_month | 77,971 | 0.8895 | discrete frequencies | 0.4757 | lower value, more detractors | 0.0039 | 5.8344 | 5.6118 |
| n\_items | 77,971 | 0.8914 | discrete frequencies | 0.5548 | higher value, more detractors | 0.0073 | 1.1160 | 1.2939 |
| interstate\_share | 77,971 | 0.9150 | discrete frequencies | 0.5408 | higher value, more detractors | 0.0026 | 0.6401 | 0.7223 |
| total\_price | 77,971 | 0.9324 | KDE (log1p scale) | 0.5441 | higher value, more detractors | 0.0083 | 132.9082 | 159.7593 |
| distance\_km\_max | 77,062 | 0.9343 | KDE (log1p scale) | 0.5470 | higher value, more detractors | 0.0037 | 596.4906 | 691.9794 |
| total\_weight\_g | 77,955 | 0.9467 | KDE (log1p scale) | 0.5294 | higher value, more detractors | 0.0058 | 2,359.7311 | 3,058.1228 |
| n\_products | 77,971 | 0.9468 | discrete frequencies | 0.5266 | higher value, more detractors | 0.0044 | 1.0284 | 1.0914 |
| total\_volume\_cm3 | 77,955 | 0.9474 | KDE (log1p scale) | 0.5292 | higher value, more detractors | 0.0092 | 17,272.8921 | 22,112.5668 |
| payment\_installments\_max | 77,971 | 0.9567 | discrete frequencies | 0.5257 | higher value, more detractors | 0.0008 | 2.9138 | 3.1992 |
| freight\_ratio | 77,971 | 0.9611 | KDE | 0.5128 | higher value, more detractors | 0.0100 | 0.3029 | 0.3201 |
| n\_sellers | 77,971 | 0.9672 | discrete frequencies | 0.5164 | higher value, more detractors | 0.0041 | 1.0073 | 1.0428 |
| purchase\_hour | 77,971 | 0.9757 | discrete frequencies | 0.5008 | higher value, more detractors | 0.0003 | 14.7781 | 14.7486 |
| n\_categories | 77,971 | 0.9806 | discrete frequencies | 0.5047 | higher value, more detractors | 0.0015 | 0.9891 | 0.9991 |
| purchase\_dayofweek | 77,971 | 0.9835 | discrete frequencies | 0.5018 | higher value, more detractors | 0.0001 | 2.7622 | 2.7738 |
| category\_missing\_fraction | 77,971 | 0.9929 | discrete frequencies | 0.5035 | higher value, more detractors | 0.0004 | 0.0159 | 0.0218 |
| distance\_missing\_fraction | 77,971 | 0.9980 | discrete frequencies | 0.4990 | lower value, more detractors | 0.0000 | 0.0119 | 0.0099 |
| n\_payment\_methods | 77,971 | 0.9994 | discrete frequencies | 0.4997 | lower value, more detractors | 0.0000 | 1.0233 | 1.0227 |
| volume\_missing\_fraction | 77,971 | 0.9999 | discrete frequencies | 0.5000 | higher value, more detractors | 0.0000 | 0.0002 | 0.0003 |
| weight\_missing\_fraction | 77,971 | 0.9999 | discrete frequencies | 0.5000 | higher value, more detractors | 0.0000 | 0.0002 | 0.0003 |

&#91;image: Class-conditional distributions\]

**w****Files** (local, run 20261019T081206Z): numeric\_feature\_target\_is\_detractor.csv, figures/numeric\_vs\_is\_detractor.png, figures/numeric\_vs\_is\_detractor.csv, figures/numeric\_vs\_is\_detractor.json

## 3.7 Categorical features vs is\_detractor

**Approved solution:** Mutual information (`mutual_info_classif`, discrete, seed 42)

**What was done:** Four categorical predictors: mutual\_info\_classif (discrete, seed 42) and per-level detractor rates; calendar fields shown per level for the plots only. MI: customer\_state 0.0050, primary\_seller\_state 0.0009, primary\_category 0.0026, primary\_payment\_type 0.0000 nats.

| feature | levels | mutual\_information | lowest\_rate | highest\_rate |
| --- | --- | --- | --- | --- |
| customer\_state | 27 | 0.0050 | 0.0893 | 0.2610 |
| primary\_category | 72 | 0.0026 | 0.0000 | 0.5000 |
| primary\_seller\_state | 23 | 0.0009 | 0.0000 | 1.0000 |
| primary\_payment\_type | 4 | 0.0000 | 0.1409 | 0.1511 |

**customer\_state** (top 15 of 27 levels by count; all levels in categorical\_feature\_target\_is\_detractor.csv)

| level | n | share | detractors | detractor\_rate |
| --- | --- | --- | --- | --- |
| SP | 31,849 | 0.408 | 3,843 | 0.121 |
| RJ | 10,295 | 0.132 | 2,233 | 0.217 |
| MG | 9,281 | 0.119 | 1,231 | 0.133 |
| RS | 4,450 | 0.057 | 607 | 0.136 |
| PR | 3,978 | 0.051 | 494 | 0.124 |
| SC | 2,943 | 0.038 | 441 | 0.150 |
| BA | 2,655 | 0.034 | 529 | 0.199 |
| DF | 1,638 | 0.021 | 258 | 0.158 |
| GO | 1,636 | 0.021 | 244 | 0.149 |
| ES | 1,627 | 0.021 | 249 | 0.153 |
| PE | 1,297 | 0.017 | 235 | 0.181 |
| CE | 1,093 | 0.014 | 231 | 0.211 |
| PA | 795 | 0.010 | 174 | 0.219 |
| MT | 743 | 0.010 | 109 | 0.147 |
| MA | 613 | 0.008 | 134 | 0.219 |

**primary\_seller\_state** (top 15 of 23 levels by count; all levels in categorical\_feature\_target\_is\_detractor.csv)

| level | n | share | detractors | detractor\_rate |
| --- | --- | --- | --- | --- |
| SP | 55,468 | 0.711 | 8,566 | 0.154 |
| MG | 6,375 | 0.082 | 799 | 0.125 |
| PR | 6,068 | 0.078 | 879 | 0.145 |
| RJ | 3,197 | 0.041 | 475 | 0.149 |
| SC | 2,892 | 0.037 | 363 | 0.126 |
| RS | 1,462 | 0.019 | 144 | 0.098 |
| DF | 667 | 0.009 | 97 | 0.145 |
| BA | 438 | 0.006 | 48 | 0.110 |
| GO | 350 | 0.004 | 34 | 0.097 |
| PE | 293 | 0.004 | 30 | 0.102 |
| ES | 270 | 0.003 | 42 | 0.156 |
| MA | 163 | 0.002 | 37 | 0.227 |
| MT | 116 | 0.001 | 9 | 0.078 |
| CE | 62 | 0.001 | 7 | 0.113 |
| RN | 45 | 0.001 | 5 | 0.111 |

**primary\_payment\_type**

| level | n | share | detractors | detractor\_rate |
| --- | --- | --- | --- | --- |
| credit\_card | 58,816 | 0.754 | 8,750 | 0.149 |
| boleto | 15,838 | 0.203 | 2,311 | 0.146 |
| voucher | 2,515 | 0.032 | 380 | 0.151 |
| debit\_card | 802 | 0.010 | 113 | 0.141 |

**primary\_category** (top 15 of 72 levels by count; all levels in categorical\_feature\_target\_is\_detractor.csv)

| level | n | share | detractors | detractor\_rate |
| --- | --- | --- | --- | --- |
| bed\_bath\_table | 7,412 | 0.095 | 1,299 | 0.175 |
| health\_beauty | 6,373 | 0.082 | 871 | 0.137 |
| sports\_leisure | 6,318 | 0.081 | 833 | 0.132 |
| computers\_accessories | 5,441 | 0.070 | 914 | 0.168 |
| furniture\_decor | 5,247 | 0.067 | 906 | 0.173 |
| housewares | 4,214 | 0.054 | 566 | 0.134 |
| watches\_gifts | 4,139 | 0.053 | 634 | 0.153 |
| telephony | 3,449 | 0.044 | 532 | 0.154 |
| toys | 3,307 | 0.042 | 414 | 0.125 |
| cool\_stuff | 3,212 | 0.041 | 386 | 0.120 |
| garden\_tools | 2,994 | 0.038 | 401 | 0.134 |
| auto | 2,875 | 0.037 | 435 | 0.151 |
| perfumery | 2,564 | 0.033 | 346 | 0.135 |
| baby | 2,153 | 0.028 | 354 | 0.164 |
| electronics | 2,060 | 0.026 | 303 | 0.147 |

&#91;image: Detractor rate by level\]

**Files** (local, run 20261019T081206Z): categorical\_feature\_target\_is\_detractor.csv, figures/categorical\_vs\_is\_detractor.png, figures/categorical\_vs\_is\_detractor.csv, figures/categorical\_vs\_is\_detractor.json

## 3.8 Importance ranking

**Approved solution:** One ranking per task feeding s04 selection, over all 24 contract predictors (the ranking file has exactly 24 rows; G-42, G-61): absolute Spearman for regression, mutual information for classification (one measure per task, so cumulative shares are meaningful). Missingness, outliers and correlation/VIF among raw numeric features also reported here

**What was done:** Ranking over the 24 contract predictors by mutual information (discrete estimator for categorical features and features with at most 30 values, k-NN estimator for the rest): top 5 \['total\_freight', 'freight\_ratio', 'total\_volume\_cm3', 'total\_price', 'n\_items'\]; cut points {'0.95': 14, '0.99': 17}. Missingness, IQR outliers, Pearson/Spearman matrix and VIF on 77,046 complete rows; flagged groups: \[\]; identical columns: \[('weight\_missing\_fraction', 'volume\_missing\_fraction')\].

**Ranking** (mutual information):

| rank | feature | type | method | value | share | cumulative\_share |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | total\_freight | numeric | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0108 | 0.1316 | 0.1316 |
| 2 | freight\_ratio | numeric | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0100 | 0.1217 | 0.2533 |
| 3 | total\_volume\_cm3 | numeric | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0092 | 0.1120 | 0.3653 |
| 4 | total\_price | numeric | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0083 | 0.1011 | 0.4664 |
| 5 | n\_items | numeric | mutual\_info\_classif, discrete (contingency) | 0.0073 | 0.0893 | 0.5557 |
| 6 | total\_weight\_g | numeric | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0058 | 0.0713 | 0.6270 |
| 7 | customer\_state | categorical | mutual\_info\_classif, discrete (contingency) | 0.0050 | 0.0617 | 0.6887 |
| 8 | n\_products | numeric | mutual\_info\_classif, discrete (contingency) | 0.0044 | 0.0542 | 0.7430 |
| 9 | n\_sellers | numeric | mutual\_info\_classif, discrete (contingency) | 0.0041 | 0.0500 | 0.7929 |
| 10 | purchase\_month | numeric | mutual\_info\_classif, discrete (contingency) | 0.0039 | 0.0477 | 0.8407 |
| 11 | distance\_km\_max | numeric | mutual\_info\_classif, continuous (k-NN, k=3) | 0.0037 | 0.0447 | 0.8853 |
| 12 | primary\_category | categorical | mutual\_info\_classif, discrete (contingency) | 0.0026 | 0.0323 | 0.9176 |
| 13 | interstate\_share | numeric | mutual\_info\_classif, discrete (contingency) | 0.0026 | 0.0320 | 0.9496 |
| 14 | n\_categories | numeric | mutual\_info\_classif, discrete (contingency) | 0.0015 | 0.0188 | 0.9684 |
| 15 | primary\_seller\_state | categorical | mutual\_info\_classif, discrete (contingency) | 0.0009 | 0.0111 | 0.9795 |
| 16 | payment\_installments\_max | numeric | mutual\_info\_classif, discrete (contingency) | 0.0008 | 0.0097 | 0.9892 |
| 17 | category\_missing\_fraction | numeric | mutual\_info\_classif, discrete (contingency) | 0.0004 | 0.0052 | 0.9944 |
| 18 | purchase\_hour | numeric | mutual\_info\_classif, discrete (contingency) | 0.0003 | 0.0038 | 0.9982 |
| 19 | purchase\_dayofweek | numeric | mutual\_info\_classif, discrete (contingency) | 0.0001 | 0.0013 | 0.9995 |
| 20 | distance\_missing\_fraction | numeric | mutual\_info\_classif, discrete (contingency) | 0.0000 | 0.0004 | 0.9999 |
| 21 | primary\_payment\_type | categorical | mutual\_info\_classif, discrete (contingency) | 0.0000 | 0.0001 | 1.0000 |
| 22 | volume\_missing\_fraction | numeric | mutual\_info\_classif, discrete (contingency) | 0.0000 | 0.0000 | 1.0000 |
| 23 | weight\_missing\_fraction | numeric | mutual\_info\_classif, discrete (contingency) | 0.0000 | 0.0000 | 1.0000 |
| 24 | n\_payment\_methods | numeric | mutual\_info\_classif, discrete (contingency) | 0.0000 | 0.0000 | 1.0000 |

&#91;image: Cumulative importance\]

**Missingness, outliers and VIF** (raw features, pre-cutoff orders):

| feature | type | missing\_share | distinct\_values | share\_outside\_1\_5\_iqr | share\_outside\_3\_iqr | vif | vif\_note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| n\_items | numeric | 0.0000 | 17 | 0.1001 | 0.1001 | 1.6499 |  |
| n\_products | numeric | 0.0000 | 7 | 0.0327 | 0.0327 | 1.7994 |  |
| n\_sellers | numeric | 0.0000 | 5 | 0.0120 | 0.0120 | 1.8523 |  |
| n\_categories | numeric | 0.0000 | 4 | 0.0233 | 0.0233 | 4.9226 |  |
| total\_price | numeric | 0.0000 | 6,428 | 0.0799 | 0.0410 | 1.4759 |  |
| total\_freight | numeric | 0.0000 | 6,795 | 0.0969 | 0.0489 | 3.3271 |  |
| freight\_ratio | numeric | 0.0000 | 33,649 | 0.0683 | 0.0229 | 1.2596 |  |
| total\_weight\_g | numeric | 0.0002 | 2,602 | 0.1409 | 0.0828 | 3.5012 |  |
| total\_volume\_cm3 | numeric | 0.0002 | 5,563 | 0.0979 | 0.0435 | 3.4255 |  |
| weight\_missing\_fraction | numeric | 0.0000 | 2 | 0.0002 | 0.0002 | — | constant on the complete rows |
| volume\_missing\_fraction | numeric | 0.0000 | 2 | 0.0002 | 0.0002 | — | constant on the complete rows |
| primary\_category | categorical | 0.0000 | 72 | — | — | — |  |
| category\_missing\_fraction | numeric | 0.0000 | 10 | 0.0171 | 0.0171 | 4.3724 |  |
| customer\_state | categorical | 0.0000 | 27 | — | — | — |  |
| primary\_seller\_state | categorical | 0.0000 | 23 | — | — | — |  |
| distance\_km\_max | numeric | 0.0117 | 72,829 | 0.0801 | 0.0069 | 1.6819 |  |
| distance\_missing\_fraction | numeric | 0.0000 | 3 | 0.0117 | 0.0117 | — | constant on the complete rows |
| interstate\_share | numeric | 0.0000 | 5 | 0.0000 | 0.0000 | 1.4980 |  |
| purchase\_month | numeric | 0.0000 | 12 | 0.0000 | 0.0000 | 1.0031 |  |
| purchase\_dayofweek | numeric | 0.0000 | 7 | 0.0000 | 0.0000 | 1.0021 |  |
| purchase\_hour | numeric | 0.0000 | 24 | 0.0000 | 0.0000 | 1.0007 |  |
| primary\_payment\_type | categorical | 0.0000 | 4 | — | — | — |  |
| payment\_installments\_max | numeric | 0.0000 | 22 | 0.0665 | 0.0016 | 1.1543 |  |
| n\_payment\_methods | numeric | 0.0000 | 2 | 0.0232 | 0.0232 | 1.0023 |  |

**Collinearity** (|Pearson| or |Spearman| > 0.9, VIF > 10.0; VIF on 77,046 complete rows):

| feature\_a | feature\_b | pearson | spearman | identical |
| --- | --- | --- | --- | --- |
| weight\_missing\_fraction | volume\_missing\_fraction | 1.0000 | 1.0000 | yes |

&#91;image: Correlation heatmap\]

**Skewness of the log1p candidates** (for s04 4.2):

| feature | skewness | threshold | log1p |
| --- | --- | --- | --- |
| total\_price | 10.0401 | 1.0000 | yes |
| total\_freight | 8.0876 | 1.0000 | yes |
| total\_weight\_g | 6.5865 | 1.0000 | yes |
| total\_volume\_cm3 | 7.4701 | 1.0000 | yes |
| distance\_km\_max | 1.6402 | 1.0000 | yes |

**Candidate rationale** (finding → change → stage that tests it):

| finding | evidence | change\_it\_motivates | stage\_that\_tests\_it |
| --- | --- | --- | --- |
| total\_price pre-cutoff skewness 10.04 (above 1) | eda\_summary.json:log1p\_candidates | log1p on total\_price | s04 4.2 (applied), s06 (fitted inside folds) |
| total\_freight pre-cutoff skewness 8.09 (above 1) | eda\_summary.json:log1p\_candidates | log1p on total\_freight | s04 4.2 (applied), s06 (fitted inside folds) |
| total\_weight\_g pre-cutoff skewness 6.59 (above 1) | eda\_summary.json:log1p\_candidates | log1p on total\_weight\_g | s04 4.2 (applied), s06 (fitted inside folds) |
| total\_volume\_cm3 pre-cutoff skewness 7.47 (above 1) | eda\_summary.json:log1p\_candidates | log1p on total\_volume\_cm3 | s04 4.2 (applied), s06 (fitted inside folds) |
| distance\_km\_max pre-cutoff skewness 1.64 (above 1) | eda\_summary.json:log1p\_candidates | log1p on distance\_km\_max | s04 4.2 (applied), s06 (fitted inside folds) |
| weight\_missing\_fraction and volume\_missing\_fraction are identical on every pre-cutoff order | collinear\_pairs.csv | drop one of weight\_missing\_fraction, volume\_missing\_fraction automatically (duplicate rule) | s04 4.3 |
| top 14 of 24 features reach 95% of total mutual information | importance\_ranking.csv:cumulative\_share | selected set = top 14 if the team picks 95% | s04 4.4 (threshold fixed before fitting), s06 |
| top 17 of 24 features reach 99% of total mutual information | importance\_ranking.csv:cumulative\_share | selected set = top 17 if the team picks 99% | s04 4.4 (threshold fixed before fitting), s06 |
| detractor prevalence 14.82% (11,554 of 77,971 pre-cutoff orders) | target\_classification\_is\_detractor.csv | average precision with the prevalence baseline as the primary metric (s01) | s06, s08 |
| detractor rate ranges 10.7% to 22.5% across purchase months with at least 100 orders | outcome\_trends.csv | time-ordered expanding folds; class support per fold | s05 5.5, 5.8 |
| detractor rate 57.2% for orders delivered after the promised date vs 9.5% on time (description only, G-35) | eda\_summary.json:detractor\_rate\_by\_late | none: lateness is known only after delivery and is never a predictor; it explains why checkout-time signal is limited | s09 (discussion) |

**Files** (local, run 20261019T081206Z): feature\_quality.csv, collinear\_pairs.csv, numeric\_correlations.csv, figures/numeric\_correlation\_heatmap.png, figures/numeric\_correlation\_heatmap.csv, figures/numeric\_correlation\_heatmap.json, importance\_ranking.csv, figures/cumulative\_importance.png, figures/cumulative\_importance.csv, figures/cumulative\_importance.json, candidate\_rationale.csv, eda\_summary.json, decision.json

## 3.10 Candidate screen: product fields and extended ranking (G-68) — round 3

**Approved solution:** Screen product\_photos\_qty, product\_description\_lenght and product\_name\_lenght (value of the primary item) for classification only; not predictors unless adopted at the gate (G-68, CR-037). Round 3: the extended ranking covers every screening candidate.

**What was done:** Screening columns (not predictors) diagnosed against is\_detractor with the 3.6 measures; numeric ones also with skewness, correlation with the 20 numeric predictors and VIF in the extended numeric set. Product fields (primary item): product\_photos\_qty: rank 27, MI 0.0006, ROC-AUC 0.480, overlap 96.3%; product\_description\_lenght: rank 11, MI 0.0047, ROC-AUC 0.492, overlap 97.8%; product\_name\_lenght: rank 26, MI 0.0007, ROC-AUC 0.504, overlap 97.2%. Extended ranking over 24 + 12 candidates; cut points {'0.95': 22, '0.99': 27} (official 3.8 ranking unchanged at 24).

**Reasoning:** The extended ranking shows where each candidate would enter; s04 recomputes the cumulative share over the agreed pool (24 + adopted candidates). Screening on pre-cutoff orders and then choosing is a post-hoc addition; the report says so.

**Conclusion:** Team decision at the gate: adopt or drop each candidate (human\_decisions.yaml).

| feature | kind | n | missing\_share | overlap\_coefficient | roc\_auc | direction | mutual\_information | rank\_in\_extended | inside\_95\_cut | inside\_99\_cut | skewness | vif\_in\_extended\_set | planned\_transform |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| product\_photos\_qty | numeric | 76,674 | 0.0166 | 0.9628 | 0.4796 | lower value, more detractors | 0.0006 | 27 | no | yes | 1.8945 | 1.0450 | scaled, never logged (count) |
| product\_description\_lenght | numeric | 76,674 | 0.0166 | 0.9777 | 0.4921 | lower value, more detractors | 0.0047 | 11 | yes | yes | 2.0435 | 1.0910 | log1p if pre-cutoff skewness > 1, then scaled |
| product\_name\_lenght | numeric | 76,674 | 0.0166 | 0.9718 | 0.5038 | higher value, more detractors | 0.0007 | 26 | no | yes | -0.8821 | 1.0588 | log1p if pre-cutoff skewness > 1, then scaled |

&#91;image: Product fields\]

**Extended ranking** (24 contract predictors + 12 screening candidates, mutual information; cut points {'0.95': 22, '0.99': 27}; the official 3.8 ranking stays at 24, and s04 recomputes the shares over the agreed pool):

| rank | feature | candidate | card | value | share | cumulative\_share |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | total\_freight | no | 3.8000 | 0.0108 | 0.0861 | 0.0861 |
| 2 | seller\_prior\_review\_mean | yes | 3.1300 | 0.0104 | 0.0830 | 0.1691 |
| 3 | freight\_ratio | no | 3.8000 | 0.0100 | 0.0796 | 0.2486 |
| 4 | total\_volume\_cm3 | no | 3.8000 | 0.0092 | 0.0732 | 0.3219 |
| 5 | total\_price | no | 3.8000 | 0.0083 | 0.0661 | 0.3880 |
| 6 | seller\_prior\_detractor\_share | yes | 3.1300 | 0.0081 | 0.0646 | 0.4526 |
| 7 | n\_items | no | 3.8000 | 0.0073 | 0.0584 | 0.5110 |
| 8 | seller\_prior\_late\_share | yes | 3.1300 | 0.0067 | 0.0537 | 0.5647 |
| 9 | total\_weight\_g | no | 3.8000 | 0.0058 | 0.0466 | 0.6114 |
| 10 | customer\_state | no | 3.8000 | 0.0050 | 0.0403 | 0.6517 |
| 11 | product\_description\_lenght | yes | 3.1000 | 0.0047 | 0.0378 | 0.6895 |
| 12 | n\_products | no | 3.8000 | 0.0044 | 0.0354 | 0.7249 |
| 13 | n\_sellers | no | 3.8000 | 0.0041 | 0.0327 | 0.7576 |
| 14 | purchase\_month | no | 3.8000 | 0.0039 | 0.0312 | 0.7888 |
| 15 | distance\_km\_max | no | 3.8000 | 0.0037 | 0.0292 | 0.8180 |
| 16 | est\_delivery\_days | yes | 3.1100 | 0.0031 | 0.0248 | 0.8428 |
| 17 | seller\_prior\_delivered\_count | yes | 3.1300 | 0.0029 | 0.0235 | 0.8663 |
| 18 | seller\_prior\_review\_count | yes | 3.1300 | 0.0028 | 0.0223 | 0.8886 |
| 19 | primary\_category | no | 3.8000 | 0.0026 | 0.0211 | 0.9097 |
| 20 | interstate\_share | no | 3.8000 | 0.0026 | 0.0209 | 0.9306 |
| 21 | region\_pair | yes | 3.1200 | 0.0018 | 0.0147 | 0.9453 |
| 22 | n\_categories | no | 3.8000 | 0.0015 | 0.0123 | 0.9576 |
| 23 | customer\_region | yes | 3.1200 | 0.0012 | 0.0094 | 0.9670 |
| 24 | primary\_seller\_state | no | 3.8000 | 0.0009 | 0.0073 | 0.9743 |
| 25 | payment\_installments\_max | no | 3.8000 | 0.0008 | 0.0064 | 0.9807 |
| 26 | product\_name\_lenght | yes | 3.1000 | 0.0007 | 0.0060 | 0.9866 |
| 27 | product\_photos\_qty | yes | 3.1000 | 0.0006 | 0.0044 | 0.9911 |
| 28 | category\_missing\_fraction | no | 3.8000 | 0.0004 | 0.0034 | 0.9944 |
| 29 | purchase\_hour | no | 3.8000 | 0.0003 | 0.0025 | 0.9969 |
| 30 | seller\_region | yes | 3.1200 | 0.0002 | 0.0019 | 0.9988 |
| 31 | purchase\_dayofweek | no | 3.8000 | 0.0001 | 0.0008 | 0.9997 |
| 32 | distance\_missing\_fraction | no | 3.8000 | 0.0000 | 0.0002 | 0.9999 |
| 33 | primary\_payment\_type | no | 3.8000 | 0.0000 | 0.0001 | 1.0000 |
| 34 | volume\_missing\_fraction | no | 3.8000 | 0.0000 | 0.0000 | 1.0000 |
| 35 | weight\_missing\_fraction | no | 3.8000 | 0.0000 | 0.0000 | 1.0000 |
| 36 | n\_payment\_methods | no | 3.8000 | 0.0000 | 0.0000 | 1.0000 |

&#91;image: Extended ranking\]

**Check** candidate screen 3.10 covers every product candidate: PASS (3 candidates) **Check** extended ranking holds the 24 predictors and every candidate, ends at 1.0; official ranking unchanged at 24: PASS (36 rows)

**Files** (local, run 20261019T151336Z): figures/candidate\_screen.png, figures/candidate\_screen.csv, candidate\_screen\_3\_10.csv, candidate\_ranking\_extended.csv, candidate\_collinear\_pairs.csv, figures/candidate\_ranking\_extended.png, figures/candidate\_ranking\_extended.csv

## 3.11 Candidate screen: promised delivery days (G-69) — new in round 3

**Approved solution:** Screen est\_delivery\_days = estimated delivery date minus purchase, classification only; G-35 reopened for this screen; if adopted, train on out-of-fold task 1 predictions (G-69, CR-038).

**What was done:** Screening columns (not predictors) diagnosed against is\_detractor with the 3.6 measures; numeric ones also with skewness, correlation with the 20 numeric predictors and VIF in the extended numeric set. Promised delivery days: est\_delivery\_days: rank 16, MI 0.0031, ROC-AUC 0.539, overlap 95.0%.

**Reasoning:** G-35 is reopened for this screen only. Olist's own promise is measured here; in production the promise would come from the task 1 prediction, so if adopted the classifier trains on out-of-fold task 1 predictions, which makes classification s06 depend on regression s06.

| feature | kind | n | missing\_share | overlap\_coefficient | roc\_auc | direction | mutual\_information | rank\_in\_extended | inside\_95\_cut | inside\_99\_cut | skewness | vif\_in\_extended\_set | planned\_transform |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| est\_delivery\_days | numeric | 77,971 | 0.0000 | 0.9495 | 0.5386 | higher value, more detractors | 0.0031 | 16 | yes | yes | 1.3482 | 1.7261 | log1p if pre-cutoff skewness > 1, then scaled; in production fed by the task 1 prediction, so if adopted the classifier trains on out-of-fold task 1 predictions (G-69) |

&#91;image: Promised delivery days\]

**Check** candidate screen 3.11 covers every promise candidate: PASS (1 candidates)

**Files** (local, run 20261019T151336Z): figures/candidate\_screen\_promise.png, figures/candidate\_screen\_promise.csv, candidate\_screen\_3\_11.csv

## 3.12 Candidate screen: regions (G-69) — new in round 3

**Approved solution:** Screen customer\_region, seller\_region (IBGE macro-regions) and region\_pair (customer>seller), classification only (G-69, CR-038; the lead chose regions over numeric state codes).

**What was done:** Screening columns (not predictors) diagnosed against is\_detractor with the 3.6 measures; numeric ones also with skewness, correlation with the 20 numeric predictors and VIF in the extended numeric set. Regions (IBGE macro-regions; pair = customer>seller): customer\_region: rank 23, MI 0.0012, overlap 95.4%; seller\_region: rank 30, MI 0.0002, overlap 97.9%; region\_pair: rank 21, MI 0.0018, overlap 95.0%. Per-level detractor rates in candidate\_screen\_levels.csv.

**Reasoning:** A region has 5 levels instead of 27 states, so each level holds more orders; the pair captures logistics corridors. Mutual information with many levels is biased upward, so compare the region and state values with that in mind.

| feature | kind | n | missing\_share | overlap\_coefficient | roc\_auc | direction | mutual\_information | rank\_in\_extended | inside\_95\_cut | inside\_99\_cut | skewness | vif\_in\_extended\_set | planned\_transform |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| customer\_region | categorical | 77,971 | 0.0000 | 0.9544 | — | — | 0.0012 | 23 | no | yes | — | — | one-hot (drop-first for linear/logistic), unknown level handled |
| seller\_region | categorical | 77,971 | 0.0000 | 0.9789 | — | — | 0.0002 | 30 | no | no | — | — | one-hot (drop-first for linear/logistic), unknown level handled |
| region\_pair | categorical | 77,971 | 0.0000 | 0.9499 | — | — | 0.0018 | 21 | yes | yes | — | — | one-hot (drop-first for linear/logistic), unknown level handled |

Per-level detractor rates:

| feature | level | n | share | detractors | detractor\_rate |
| --- | --- | --- | --- | --- | --- |
| customer\_region | Center-West | 4,585 | 0.0588 | 694 | 0.1514 |
| customer\_region | North | 1,501 | 0.0193 | 279 | 0.1859 |
| customer\_region | Northeast | 7,462 | 0.0957 | 1,483 | 0.1987 |
| customer\_region | South | 11,371 | 0.1458 | 1,542 | 0.1356 |
| customer\_region | Southeast | 53,052 | 0.6804 | 7,556 | 0.1424 |
| seller\_region | Center-West | 1,173 | 0.0150 | 142 | 0.1211 |
| seller\_region | North | 26 | 0.0003 | 7 | 0.2692 |
| seller\_region | Northeast | 1,040 | 0.0133 | 137 | 0.1317 |
| seller\_region | South | 10,422 | 0.1337 | 1,386 | 0.1330 |
| seller\_region | Southeast | 65,310 | 0.8376 | 9,882 | 0.1513 |

region\_pair, top 15 levels by count:

| feature | level | n | share | detractors | detractor\_rate |
| --- | --- | --- | --- | --- | --- |
| region\_pair | Southeast>Southeast | 45,204 | 0.5798 | 6,493 | 0.1436 |
| region\_pair | South>Southeast | 8,716 | 0.1118 | 1,283 | 0.1472 |
| region\_pair | Southeast>South | 6,551 | 0.0840 | 900 | 0.1374 |
| region\_pair | Northeast>Southeast | 6,301 | 0.0808 | 1,265 | 0.2008 |
| region\_pair | Center-West>Southeast | 3,827 | 0.0491 | 606 | 0.1583 |
| region\_pair | South>South | 2,443 | 0.0313 | 229 | 0.0937 |
| region\_pair | North>Southeast | 1,262 | 0.0162 | 235 | 0.1862 |
| region\_pair | Southeast>Center-West | 727 | 0.0093 | 88 | 0.1210 |
| region\_pair | Northeast>South | 725 | 0.0093 | 160 | 0.2207 |
| region\_pair | Southeast>Northeast | 551 | 0.0071 | 71 | 0.1289 |
| region\_pair | Center-West>South | 531 | 0.0068 | 67 | 0.1262 |
| region\_pair | Northeast>Northeast | 290 | 0.0037 | 30 | 0.1034 |
| region\_pair | North>South | 172 | 0.0022 | 30 | 0.1744 |
| region\_pair | Center-West>Center-West | 155 | 0.0020 | 13 | 0.0839 |
| region\_pair | Northeast>Center-West | 142 | 0.0018 | 27 | 0.1901 |

&#91;image: Regions\]

**Check** candidate screen 3.12 covers every region candidate: PASS (3 candidates)

**Files** (local, run 20261019T151336Z): figures/candidate\_screen\_region.png, figures/candidate\_screen\_region.csv, candidate\_screen\_3\_12.csv, candidate\_screen\_levels.csv

## 3.13 Candidate screen: seller history at checkout (G-69) — new in round 3

**Approved solution:** Screen the primary seller's history at checkout: prior review mean, review count, detractor share, delivered count and late share, counting only events strictly before the purchase second and never the order's own (G-69, CR-038).

**What was done:** Screening columns (not predictors) diagnosed against is\_detractor with the 3.6 measures; numeric ones also with skewness, correlation with the 20 numeric predictors and VIF in the extended numeric set. Seller history at checkout: seller\_prior\_review\_mean: rank 2, MI 0.0104, ROC-AUC 0.441, overlap 90.5%; seller\_prior\_review\_count: rank 18, MI 0.0028, ROC-AUC 0.507, overlap 96.2%; seller\_prior\_detractor\_share: rank 6, MI 0.0081, ROC-AUC 0.557, overlap 90.5%; seller\_prior\_delivered\_count: rank 17, MI 0.0029, ROC-AUC 0.506, overlap 96.2%; seller\_prior\_late\_share: rank 8, MI 0.0067, ROC-AUC 0.536, overlap 90.0%.

**Reasoning:** Only the primary seller's events strictly before the purchase second count (reviews at their answer time, deliveries at delivery time) and the order's own events never count; s02 checks this against a direct recomputation on 2,000 orders. Sellers without history are missing, with the counts at 0.

| feature | kind | n | missing\_share | overlap\_coefficient | roc\_auc | direction | mutual\_information | rank\_in\_extended | inside\_95\_cut | inside\_99\_cut | skewness | vif\_in\_extended\_set | planned\_transform |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| seller\_prior\_review\_mean | numeric | 72,862 | 0.0655 | 0.9051 | 0.4408 | lower value, more detractors | 0.0104 | 2 | yes | yes | -1.8616 | 5.1144 | scaled; missing for sellers without an earlier review (imputed in folds with a missing indicator) |
| seller\_prior\_review\_count | numeric | 77,971 | 0.0000 | 0.9622 | 0.5066 | higher value, more detractors | 0.0028 | 18 | yes | yes | 2.6656 | 1,443.3614 | log1p if pre-cutoff skewness > 1, then scaled |
| seller\_prior\_detractor\_share | numeric | 72,862 | 0.0655 | 0.9048 | 0.5566 | higher value, more detractors | 0.0081 | 6 | yes | yes | 3.0728 | 5.0672 | scaled, never logged (share); missing as for the mean |
| seller\_prior\_delivered\_count | numeric | 77,971 | 0.0000 | 0.9622 | 0.5058 | higher value, more detractors | 0.0029 | 17 | yes | yes | 2.6083 | 1,444.4322 | log1p if pre-cutoff skewness > 1, then scaled |
| seller\_prior\_late\_share | numeric | 73,355 | 0.0592 | 0.8999 | 0.5360 | higher value, more detractors | 0.0067 | 8 | yes | yes | 5.7004 | 1.2042 | scaled, never logged (share); missing when no earlier delivery |

**Collinear pair (team decision at the gate):**

| feature\_a | feature\_b | pearson | spearman | identical |
| --- | --- | --- | --- | --- |
| seller\_prior\_review\_count | seller\_prior\_delivered\_count | 0.9997 | 0.9990 | no |

&#91;image: Seller history\]

**Check** candidate screen 3.13 covers every seller\_history candidate: PASS (5 candidates)

**Files** (local, run 20261019T151336Z): figures/candidate\_screen\_seller\_history.png, figures/candidate\_screen\_seller\_history.csv, candidate\_screen\_3\_13.csv, candidate\_collinear\_pairs.csv

## 3.9 Human gate (review pack for s04 decisions)

**Approved solution:** Human gate (G-31): implementation stops after s03. All EDA results are presented to the team, and s04 runs only after the team records its decisions (threshold, collinearity drops)

**What was done:** eda\_review\_pack.md lists every table and figure above, the ranking with both cut points, the flagged collinear groups and the YAML block the team fills in spec/human\_decisions.yaml.

**Conclusion:** Stop: s04 waits for the team's threshold and collinearity decisions (G-31).

eda\_review\_pack.md holds every table and figure of this tab. Threshold options:

| Threshold | Features kept | Features (in ranking order) |
| --- | --- | --- |
| 95% | 14 | total\_freight, freight\_ratio, total\_volume\_cm3, total\_price, n\_items, total\_weight\_g, customer\_state, n\_products, n\_sellers, purchase\_month, distance\_km\_max, primary\_category, interstate\_share, n\_categories |
| 99% | 17 | total\_freight, freight\_ratio, total\_volume\_cm3, total\_price, n\_items, total\_weight\_g, customer\_state, n\_products, n\_sellers, purchase\_month, distance\_km\_max, primary\_category, interstate\_share, n\_categories, primary\_seller\_state, payment\_installments\_max, category\_missing\_fraction |

Flagged collinear groups needing a team decision: none. Identical columns, dropped automatically by the s04 duplicate rule: weight\_missing\_fraction = volume\_missing\_fraction.

**Files** (local, run 20261019T081206Z): figures/cumulative\_importance.png, figures/cumulative\_importance.csv, figures/cumulative\_importance.json, eda\_review\_pack.md

# Round history: card 3.10 as of round 2 (superseded by round 3)

Kept unchanged as the record; the current 3.10 card is above.

> **Superseded. Not the feature set.** This round 2 table predates the seller history (round 3) and the adoption decision. The final pool is in the box at the top of this tab.

## 3.10 Candidate screen (G-68) — new in round 2

**Approved solution:** The experiment lead's decisions on the round 1 comments (CR-037, G-68): screen product\_photos\_qty, product\_description\_lenght and product\_name\_lenght for classification only, each the value of the primary item (the primary\_category rule); not predictors unless the team adopts them at the gate; est\_delivery\_days not added (G-35 stays); untranslated categories stay Unknown.

**What was done:** Screening candidates \['product\_photos\_qty', 'product\_description\_lenght', 'product\_name\_lenght'\] (G-68: value of the primary item; not predictors) diagnosed against is\_detractor with the 3.6 measures (overlap, ROC-AUC, mutual information), skewness for the planned transform, correlation with the 20 numeric predictors and VIF in the extended numeric set. Extended ranking over 24 + 3: candidate ranks product\_photos\_qty 19, product\_description\_lenght 8, product\_name\_lenght 18 of 27; extended cut points {'0.95': 15, '0.99': 20} (official ranking unchanged at 24). ROC-AUC: product\_photos\_qty 0.480, product\_description\_lenght 0.492, product\_name\_lenght 0.504.

**Reasoning:** The official 3.8 ranking stays over the 24 contract predictors so the agreed selection pool is unchanged; the extended ranking shows where each candidate would enter if adopted. Screening on pre-cutoff orders and then choosing is a post-hoc addition; the report says so.

**Conclusion:** Team decision at the gate: adopt or drop each candidate (human\_decisions.yaml).

| feature | n | missing\_share | overlap\_coefficient | overlap\_method | roc\_auc | direction | mutual\_information | mi\_estimator | rank\_in\_extended | inside\_95\_cut | inside\_99\_cut | skewness | planned\_transform | most\_correlated\_predictor | spearman\_with\_it | vif\_in\_extended\_set |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| product\_photos\_qty | 76,674 | 0.0166 | 0.9628 | discrete frequencies | 0.4796 | lower value, more detractors | 0.0006 | discrete (contingency) | 19 | no | yes | 1.8945 | scaled, never logged (count) | n\_items | -0.0547 | 1.0346 |
| product\_description\_lenght | 76,674 | 0.0166 | 0.9777 | KDE (log1p scale) | 0.4921 | lower value, more detractors | 0.0047 | continuous (k-NN, k=3) | 8 | yes | yes | 2.0435 | log1p if pre-cutoff skewness > 1, then scaled | total\_price | 0.2039 | 1.0766 |
| product\_name\_lenght | 76,674 | 0.0166 | 0.9718 | KDE (log1p scale) | 0.5038 | higher value, more detractors | 0.0007 | continuous (k-NN, k=3) | 18 | no | yes | -0.8821 | log1p if pre-cutoff skewness > 1, then scaled | total\_weight\_g | 0.0853 | 1.0284 |

**Extended ranking** (24 contract predictors + 3 candidates, mutual information; the official 3.8 ranking stays at 24):

| rank | feature | candidate | value | share | cumulative\_share |
| --- | --- | --- | --- | --- | --- |
| 1 | total\_freight | no | 0.0108 | 0.1226 | 0.1226 |
| 2 | freight\_ratio | no | 0.0100 | 0.1134 | 0.2359 |
| 3 | total\_volume\_cm3 | no | 0.0092 | 0.1043 | 0.3402 |
| 4 | total\_price | no | 0.0083 | 0.0942 | 0.4344 |
| 5 | n\_items | no | 0.0073 | 0.0832 | 0.5176 |
| 6 | total\_weight\_g | no | 0.0058 | 0.0664 | 0.5840 |
| 7 | customer\_state | no | 0.0050 | 0.0575 | 0.6415 |
| 8 | product\_description\_lenght | yes | 0.0047 | 0.0538 | 0.6953 |
| 9 | n\_products | no | 0.0044 | 0.0505 | 0.7458 |
| 10 | n\_sellers | no | 0.0041 | 0.0466 | 0.7923 |
| 11 | purchase\_month | no | 0.0039 | 0.0445 | 0.8368 |
| 12 | distance\_km\_max | no | 0.0037 | 0.0416 | 0.8784 |
| 13 | primary\_category | no | 0.0026 | 0.0300 | 0.9084 |
| 14 | interstate\_share | no | 0.0026 | 0.0298 | 0.9382 |
| 15 | n\_categories | no | 0.0015 | 0.0175 | 0.9557 |
| 16 | primary\_seller\_state | no | 0.0009 | 0.0103 | 0.9661 |
| 17 | payment\_installments\_max | no | 0.0008 | 0.0091 | 0.9751 |
| 18 | product\_name\_lenght | yes | 0.0007 | 0.0085 | 0.9836 |
| 19 | product\_photos\_qty | yes | 0.0006 | 0.0063 | 0.9899 |
| 20 | category\_missing\_fraction | no | 0.0004 | 0.0048 | 0.9948 |
| 21 | purchase\_hour | no | 0.0003 | 0.0036 | 0.9983 |
| 22 | purchase\_dayofweek | no | 0.0001 | 0.0012 | 0.9995 |
| 23 | distance\_missing\_fraction | no | 0.0000 | 0.0003 | 0.9999 |
| 24 | primary\_payment\_type | no | 0.0000 | 0.0001 | 1.0000 |
| 25 | volume\_missing\_fraction | no | 0.0000 | 0.0000 | 1.0000 |
| 26 | weight\_missing\_fraction | no | 0.0000 | 0.0000 | 1.0000 |
| 27 | n\_payment\_methods | no | 0.0000 | 0.0000 | 1.0000 |

Collinear pairs involving a candidate: none.

&#91;image: Candidate screen\]

**Check** candidate screen covers every classification candidate; extended ranking ends at 1.0; official ranking unchanged at 24: PASS (3 candidates, 27 rows in the extended ranking)

**Files** (local, run 20261019T140130Z): candidate\_screen\_is\_detractor.csv, candidate\_ranking\_extended.csv, candidate\_collinear\_pairs.csv, figures/candidate\_screen.png

## Pool ranking as of CR-042 (superseded by Part A; kept for its comment thread)

| rank | feature | source | inside 99% | value | share | cumulative\_share |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | total\_volume\_cm3 | contract predictor | yes | 0.0104 | 0.1109 | 0.1109 |
| 2 | seller\_prior\_review\_mean | adopted candidate (G-70) | yes | 0.0094 | 0.1001 | 0.2110 |
| 3 | total\_freight | contract predictor | yes | 0.0093 | 0.0995 | 0.3105 |
| 4 | freight\_ratio | contract predictor | yes | 0.0082 | 0.0875 | 0.3979 |
| 5 | total\_price | contract predictor | yes | 0.0079 | 0.0840 | 0.4820 |
| 6 | n\_items | contract predictor | yes | 0.0073 | 0.0780 | 0.5600 |
| 7 | product\_description\_lenght | adopted candidate (G-70) | yes | 0.0052 | 0.0559 | 0.6159 |
| 8 | customer\_state | contract predictor | yes | 0.0050 | 0.0538 | 0.6697 |
| 9 | total\_weight\_g | contract predictor | yes | 0.0048 | 0.0517 | 0.7214 |
| 10 | n\_products | contract predictor | yes | 0.0044 | 0.0473 | 0.7687 |
| 11 | n\_sellers | contract predictor | yes | 0.0041 | 0.0436 | 0.8124 |
| 12 | purchase\_month | contract predictor | yes | 0.0039 | 0.0417 | 0.8540 |
| 13 | distance\_km\_max | contract predictor | yes | 0.0037 | 0.0399 | 0.8940 |
| 14 | primary\_category | contract predictor | yes | 0.0026 | 0.0281 | 0.9221 |
| 15 | interstate\_share | contract predictor | yes | 0.0026 | 0.0279 | 0.9500 |
| 16 | n\_categories | contract predictor | yes | 0.0015 | 0.0164 | 0.9664 |
| 17 | primary\_seller\_state | contract predictor | yes | 0.0009 | 0.0097 | 0.9761 |
| 18 | payment\_installments\_max | contract predictor | yes | 0.0008 | 0.0085 | 0.9846 |
| 19 | product\_photos\_qty | adopted candidate (G-70) | yes | 0.0006 | 0.0059 | 0.9905 |
| 20 | category\_missing\_fraction | contract predictor | no | 0.0004 | 0.0045 | 0.9951 |
| 21 | purchase\_hour | contract predictor | no | 0.0003 | 0.0034 | 0.9984 |
| 22 | purchase\_dayofweek | contract predictor | no | 0.0001 | 0.0011 | 0.9996 |
| 23 | distance\_missing\_fraction | contract predictor | no | 0.0000 | 0.0003 | 0.9999 |
| 24 | primary\_payment\_type | contract predictor | no | 0.0000 | 0.0001 | 1.0000 |
| 25 | volume\_missing\_fraction | contract predictor | no | 0.0000 | 0.0000 | 1.0000 |
| 26 | weight\_missing\_fraction | contract predictor | no | 0.0000 | 0.0000 | 1.0000 |
| 27 | n\_payment\_methods | contract predictor | no | 0.0000 | 0.0000 | 1.0000 |
