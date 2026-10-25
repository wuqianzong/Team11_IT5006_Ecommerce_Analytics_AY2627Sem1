# B9 › regression

## Accepted (2026-10-25) — confirmation additions; accepted run 20261025T132406Z on b09c396 (tag e5-B-s09-accepted)

B9 is confirmed by Henry and the experiment lead. The accepted clean rerun is byte-identical to the build runs cited below, so every number in this tab is unchanged. Added at confirmation:

### B9.14 Validation and test with time windows (R-17)

**What was done:** Each series: five validation folds, their mean ± SE, and the test with its 95% bootstrap interval; each period's time window is in validation\_and\_test\_windows.csv and on the chart. B on B rows: folds mean 5.0247 ± 0.6115, test 3.2992 \[3.2449, 3.3533\]; A on B rows: folds mean 5.1423 ± 0.6616, test 4.0280 \[3.9701, 4.0834\]; A on A rows: folds mean 5.4701 ± 0.6733, test 4.3364 \[4.2813, 4.3900\]. Test window 2018-05-27 to 2018-08-29.

&#91;image: validation and test with windows\]

| period | kind | start | end | festival\_days |
| --- | --- | --- | --- | --- |
| fold 1 | validation (selection score, G-10) | 2017-06-19 | 2017-09-27 |  |
| fold 2 | validation (selection score, G-10) | 2017-09-27 | 2017-12-03 | 2017-11-24 |
| fold 3 | validation (selection score, G-10) | 2017-12-03 | 2018-02-05 | 2017-12-25 |
| fold 4 | validation (selection score, G-10) | 2018-02-05 | 2018-04-01 |  |
| fold 5 | validation (selection score, G-10) | 2018-04-01 | 2018-05-24 |  |
| test | test (unbiased, read once) | 2018-05-27 | 2018-08-29 |  |

### B9.16 Residual distribution: 3- and 6-day buffers (R-16)

**What was done:** Residual = actual minus predicted lead time. On B's test rows, B's orders arrive more than 3 days after its prediction in 11.1% of cases and more than 6 days after in 4.7% (A on the same rows 9.3% and 4.3%); median residual B -1.64 days, A -2.72; 95th percentile B +5.77, A +5.33. With a 6-day buffer on B's prediction, 95.3% of test orders arrive in time.

&#91;image: residuals\]

Why it matters: the business promises a delivery range, not a date. The share of orders arriving more than 6 days after B's prediction is the share that would miss even a 6-day buffer (residuals\_summary.csv; residual = actual minus predicted; validation rows shown for contrast).

| series | orders | mean\_days | p05 | p25 | median | p75 | p95 | share\_later\_than\_predicted | share\_more\_than\_3d\_late | share\_more\_than\_6d\_late | share\_more\_than\_3d\_early | share\_within\_3d | share\_within\_6d |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B on B's test rows | 15,422 | -1.143 | -6.931 | -3.570 | -1.637 | 0.504 | 5.772 | 0.295 | 0.111 | 0.047 | 0.314 | 0.576 | 0.870 |
| A on B's test rows | 15,422 | -2.221 | -8.341 | -4.880 | -2.724 | -0.471 | 5.329 | 0.218 | 0.093 | 0.043 | 0.464 | 0.443 | 0.792 |
| A on A's test rows | 18,788 | -2.483 | -9.033 | -5.339 | -2.942 | -0.599 | 5.510 | 0.212 | 0.094 | 0.045 | 0.493 | 0.414 | 0.754 |
| B on B's validation rows (out-of-fold) | 50,618 | 2.918 | -5.014 | -1.633 | 1.100 | 5.176 | 17.428 | 0.597 | 0.361 | 0.220 | 0.139 | 0.500 | 0.750 |
| A on A's validation rows (out-of-fold) | 62,009 | 3.319 | -5.159 | -1.724 | 1.276 | 5.871 | 18.937 | 0.603 | 0.385 | 0.245 | 0.151 | 0.465 | 0.723 |

## Round 2 — Henry's B9 review (added 2026-10-25; run 20261025T091027Z, uncommitted)

Read only: no frozen model refitted on new data, no second test read. Decisions: B-G-06 (orders outside B's scope fall back to A) and B-G-07 (classification only). Henry's requests: REPORT\_REQUESTS R-07 to R-13.

### B9.11 Drift by fold, training vs validation, A and B (R-07; for the report appendix)

**What was done:** Training vs validation drift per fold for A and B, plus final fit vs test (SMD for numeric features and the target, TVD for categorical). Numeric features with |SMD| >= 0.2 in at least 3 of the 6 periods: A purchase\_month (6), B purchase\_month (6), B route\_recent\_carrier\_transit\_days (4), B route\_recent\_delivery\_days (4).

&#91;image: drift\_by\_fold\]

**B: numeric features and target, SMD (validation or test minus training rows)**:

| feature | fold 1 | fold 2 | fold 3 | fold 4 | fold 5 | test |
| --- | --- | --- | --- | --- | --- | --- |
| purchase\_month | 3.59 | 3.14 | -0.47 | -1.92 | -0.72 | 0.41 |
| route\_recent\_delivery\_days | -0.31 | -0.03 | 0.58 | 0.50 | 0.11 | -0.73 |
| lead\_days | -0.10 | 0.28 | 0.37 | 0.40 | -0.50 | -0.59 |
| route\_recent\_carrier\_transit\_days | -0.27 | -0.06 | 0.48 | 0.48 | 0.13 | -0.56 |
| seller\_prior\_late\_handover\_rate | -0.23 | -0.14 | -0.03 | 0.12 | -0.02 | -0.09 |
| seller\_prior\_late\_handover\_days | -0.19 | -0.17 | -0.13 | -0.00 | -0.04 | -0.07 |
| seller\_prior\_dispatch\_days | -0.11 | -0.04 | 0.01 | 0.10 | -0.07 | -0.19 |
| interstate\_share | -0.04 | 0.00 | -0.03 | -0.01 | -0.15 | -0.12 |
| distance\_km\_max | 0.02 | 0.02 | -0.05 | -0.02 | -0.14 | -0.09 |
| purchase\_dayofweek | -0.01 | 0.13 | -0.01 | -0.02 | -0.08 | -0.03 |
| payment\_installments\_max | 0.01 | -0.05 | -0.11 | -0.10 | -0.09 | -0.06 |
| total\_freight | 0.03 | 0.04 | -0.01 | 0.04 | 0.03 | 0.11 |
| total\_volume\_cm3 | 0.02 | -0.03 | -0.06 | -0.05 | -0.03 | -0.10 |
| total\_weight\_g | 0.03 | -0.03 | -0.02 | -0.02 | 0.00 | -0.08 |
| freight\_ratio | -0.04 | -0.03 | -0.03 | 0.01 | -0.01 | 0.06 |
| n\_sellers | 0.06 | 0.03 | 0.02 | -0.01 | 0.06 | 0.03 |
| n\_items | 0.01 | 0.06 | -0.01 | 0.01 | 0.03 | -0.02 |
| n\_products | 0.00 | 0.03 | -0.00 | -0.05 | 0.02 | -0.00 |
| total\_price | -0.04 | 0.01 | -0.03 | -0.02 | 0.03 | -0.00 |

**B: categorical features, total variation distance**:

| feature | fold 1 | fold 2 | fold 3 | fold 4 | fold 5 | test |
| --- | --- | --- | --- | --- | --- | --- |
| primary\_category | 0.093 | 0.104 | 0.107 | 0.134 | 0.143 | 0.162 |
| primary\_payment\_type | 0.006 | 0.014 | 0.008 | 0.022 | 0.029 | 0.026 |
| route\_seller\_to\_customer\_state | 0.055 | 0.047 | 0.059 | 0.053 | 0.081 | 0.079 |

**A: numeric features and target, SMD (validation or test minus training rows)**:

| feature | fold 1 | fold 2 | fold 3 | fold 4 | fold 5 | test |
| --- | --- | --- | --- | --- | --- | --- |
| purchase\_month | 3.49 | 3.04 | -0.40 | -1.82 | -0.68 | 0.44 |
| lead\_days | -0.07 | 0.25 | 0.33 | 0.40 | -0.46 | -0.58 |
| interstate\_share | -0.03 | 0.00 | -0.04 | -0.01 | -0.16 | -0.11 |
| distance\_km\_max | -0.01 | -0.00 | -0.04 | -0.01 | -0.15 | -0.05 |
| purchase\_dayofweek | -0.03 | 0.12 | -0.01 | -0.02 | -0.09 | -0.03 |
| payment\_installments\_max | 0.02 | -0.04 | -0.12 | -0.10 | -0.08 | -0.05 |
| total\_freight | 0.04 | 0.05 | -0.02 | 0.04 | 0.02 | 0.12 |
| total\_volume\_cm3 | 0.01 | -0.03 | -0.07 | -0.06 | -0.03 | -0.11 |
| n\_categories | 0.08 | 0.04 | -0.05 | -0.00 | 0.09 | 0.10 |
| total\_weight\_g | 0.01 | -0.03 | -0.03 | -0.03 | -0.00 | -0.08 |
| n\_sellers | 0.06 | 0.03 | 0.02 | -0.01 | 0.06 | 0.04 |
| freight\_ratio | -0.04 | -0.04 | -0.02 | 0.02 | -0.03 | 0.06 |
| n\_items | 0.01 | 0.05 | -0.02 | 0.01 | 0.02 | -0.02 |
| n\_products | 0.02 | 0.03 | -0.00 | -0.05 | 0.02 | 0.00 |
| total\_price | -0.03 | 0.01 | -0.04 | -0.02 | 0.03 | 0.01 |

**A: categorical features, total variation distance**:

| feature | fold 1 | fold 2 | fold 3 | fold 4 | fold 5 | test |
| --- | --- | --- | --- | --- | --- | --- |
| customer\_state | 0.033 | 0.023 | 0.031 | 0.018 | 0.067 | 0.057 |
| primary\_category | 0.099 | 0.098 | 0.114 | 0.136 | 0.144 | 0.165 |
| primary\_payment\_type | 0.004 | 0.019 | 0.009 | 0.022 | 0.032 | 0.026 |
| primary\_seller\_state | 0.065 | 0.042 | 0.051 | 0.054 | 0.052 | 0.034 |

### B9.12 Payment type and payment clearance (R-09)

**What was done:** Lead time starts at purchase; Olist approves an order when payment clears. Development rows: median purchase-to-approval boleto 1.21 days vs credit card 0.01; mean lead time 13.24 vs 12.04 days; lead time after approval 11.87 vs 11.87. Payment type stands for payment-clearance delay, not delivery quality (observation).

(payment\_type.csv; approval time from the raw orders table; lead time after approval = lead days minus approval days)

| period | primary\_payment\_type | orders | approval\_days\_median | approval\_days\_mean | lead\_days\_mean | lead\_days\_median | lead\_minus\_approval\_days\_mean |
| --- | --- | --- | --- | --- | --- | --- | --- |
| development (B rows) | boleto | 12,332 | 1.21 | 1.36 | 13.24 | 11.28 | 11.87 |
| development (B rows) | credit\_card | 46,239 | 0.01 | 0.17 | 12.04 | 9.96 | 11.87 |
| development (B rows) | debit\_card | 669 | 0.04 | 0.33 | 11.53 | 9.36 | 11.20 |
| development (B rows) | voucher | 1,993 | 0.01 | 0.32 | 12.09 | 10.11 | 11.77 |
| test (B rows) | boleto | 2,841 | 1.18 | 1.39 | 8.91 | 7.76 | 7.51 |
| test (B rows) | credit\_card | 11,584 | 0.01 | 0.18 | 7.66 | 6.74 | 7.47 |
| test (B rows) | debit\_card | 572 | 0.02 | 0.42 | 7.89 | 6.89 | 7.47 |
| test (B rows) | voucher | 425 | 0.02 | 0.25 | 7.99 | 7.05 | 7.74 |

### B9.13 Business summary by route (R-10)

**What was done:** Routes judged (at least 100 orders): 20 of 48 on B's test rows; B has the lower MAE on 20 of them. A on all of A's test routes is listed too (in or out of B's scope).

A and B on B's test rows, judged routes (20 of 48; the rest are in business\_by\_route.csv as too small to judge):

| route | orders | mae\_A | mae\_B | within\_3d\_A | within\_3d\_B | more\_than\_3d\_late\_A | more\_than\_3d\_late\_B |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SP->SP | 6,615 | 2.859 | 2.433 | 0.624 | 0.739 | 0.103 | 0.123 |
| SP->RJ | 1,277 | 6.112 | 4.798 | 0.190 | 0.324 | 0.082 | 0.089 |
| SP->MG | 1,233 | 4.819 | 3.655 | 0.258 | 0.470 | 0.074 | 0.087 |
| SP->RS | 585 | 5.410 | 4.031 | 0.277 | 0.431 | 0.060 | 0.087 |
| PR->SP | 584 | 4.330 | 3.335 | 0.301 | 0.527 | 0.103 | 0.123 |
| SP->PR | 562 | 4.227 | 3.464 | 0.340 | 0.472 | 0.066 | 0.096 |
| SP->BA | 434 | 7.269 | 6.116 | 0.187 | 0.242 | 0.164 | 0.161 |
| MG->SP | 428 | 4.312 | 3.223 | 0.355 | 0.565 | 0.075 | 0.098 |
| SP->SC | 356 | 5.721 | 4.249 | 0.191 | 0.354 | 0.065 | 0.076 |
| RJ->SP | 321 | 3.692 | 3.095 | 0.417 | 0.561 | 0.062 | 0.093 |
| MG->MG | 320 | 2.778 | 2.539 | 0.550 | 0.634 | 0.091 | 0.059 |
| SC->SP | 275 | 4.504 | 3.614 | 0.291 | 0.473 | 0.091 | 0.102 |
| RJ->RJ | 242 | 3.228 | 2.726 | 0.570 | 0.736 | 0.116 | 0.202 |
| PR->RJ | 186 | 6.067 | 5.508 | 0.226 | 0.290 | 0.086 | 0.065 |
| MG->RJ | 174 | 5.995 | 4.691 | 0.213 | 0.362 | 0.080 | 0.098 |
| RS->SP | 171 | 3.031 | 2.518 | 0.591 | 0.678 | 0.099 | 0.129 |
| PR->PR | 163 | 3.050 | 2.695 | 0.595 | 0.669 | 0.117 | 0.141 |
| PR->MG | 146 | 5.431 | 4.812 | 0.260 | 0.377 | 0.089 | 0.103 |
| RJ->MG | 135 | 3.833 | 3.341 | 0.415 | 0.511 | 0.044 | 0.037 |
| PR->RS | 110 | 4.385 | 3.901 | 0.336 | 0.418 | 0.091 | 0.073 |

A on all of A's test rows, judged routes (27 of 301; in\_b\_scope = False marks routes served by A under B-G-06):

| route | orders | mae\_A | within\_3d\_A | more\_than\_3d\_late\_A | in\_b\_scope |
| --- | --- | --- | --- | --- | --- |
| SP->SP | 6,664 | 2.854 | 0.625 | 0.103 | False |
| SP->RJ | 1,300 | 6.132 | 0.189 | 0.082 | False |
| SP->MG | 1,263 | 4.846 | 0.257 | 0.072 | False |
| SP->RS | 590 | 5.403 | 0.280 | 0.059 | False |
| PR->SP | 584 | 4.330 | 0.301 | 0.103 | True |
| SP->PR | 572 | 4.237 | 0.341 | 0.066 | False |
| SP->BA | 442 | 7.317 | 0.183 | 0.163 | False |
| MG->SP | 428 | 4.312 | 0.355 | 0.075 | True |
| SP->SC | 365 | 5.730 | 0.189 | 0.063 | False |
| MG->MG | 322 | 2.783 | 0.547 | 0.090 | False |
| RJ->SP | 322 | 3.681 | 0.419 | 0.062 | False |
| SP->DF | 282 | 5.477 | 0.199 | 0.082 | False |
| SC->SP | 275 | 4.504 | 0.291 | 0.091 | True |
| SP->ES | 260 | 4.744 | 0.300 | 0.085 | False |
| RJ->RJ | 242 | 3.228 | 0.570 | 0.116 | True |
| SP->GO | 229 | 5.229 | 0.284 | 0.083 | False |
| SP->PE | 217 | 7.607 | 0.157 | 0.074 | False |
| PR->RJ | 186 | 6.067 | 0.226 | 0.086 | True |
| MG->RJ | 175 | 5.983 | 0.211 | 0.080 | False |
| RS->SP | 171 | 3.031 | 0.591 | 0.099 | True |
| PR->PR | 163 | 3.050 | 0.595 | 0.117 | True |
| SP->CE | 157 | 7.251 | 0.204 | 0.032 | False |
| PR->MG | 147 | 5.501 | 0.259 | 0.095 | False |
| RJ->MG | 135 | 3.833 | 0.415 | 0.044 | True |
| SP->MT | 113 | 6.471 | 0.186 | 0.044 | False |
| PR->RS | 110 | 4.385 | 0.336 | 0.091 | True |
| SP->PA | 109 | 8.479 | 0.156 | 0.046 | False |

### B9.14 Validation folds and test together (R-11)

**What was done:** Each series: five validation folds, their mean ± SE, and the test with its 95% bootstrap interval. B on B rows: folds mean 5.0247 ± 0.6115, test 3.2992 \[3.2449, 3.3533\]; A on B rows: folds mean 5.1423 ± 0.6616, test 4.0280 \[3.9701, 4.0834\]; A on A rows: folds mean 5.4701 ± 0.6733, test 4.3364 \[4.2813, 4.3900\].

&#91;image: validation\_and\_test\]

(validation\_and\_test.csv; folds are selection scores across seasons, the test is one recent window read once)

| series | fold\_1 | fold\_2 | fold\_3 | fold\_4 | fold\_5 | mean\_5\_folds | se\_5\_folds | test | test\_ci\_low | test\_ci\_high | metric |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B on B rows | 3.7223 | 5.4678 | 5.6140 | 6.7724 | 3.5469 | 5.0247 | 0.6115 | 3.2992 | 3.2449 | 3.3533 | mae |
| A on B rows | 3.7238 | 5.5158 | 5.7551 | 7.1098 | 3.6070 | 5.1423 | 0.6616 | 4.0280 | 3.9701 | 4.0834 | mae |
| A on A rows | 4.1351 | 5.8682 | 6.0283 | 7.4957 | 3.8233 | 5.4701 | 0.6733 | 4.3364 | 4.2813 | 4.3900 | mae |

### B9.15 A's model outside B's scope (R-12; B-G-06)

**What was done:** A's frozen model by B's scope (B-G-06 fallback). Validation MAE mean over 5 folds: inside 5.1827, outside 6.7480. Test: inside 4.0280 (15,422 orders), outside 5.7491 \[5.5929, 5.8946\] (3,366 orders).

Fold by fold and test (a\_fallback\_by\_scope.csv; out of scope = customer or seller state outside the seven, or distance missing):

| period | scope | orders | mae | rmse | within\_3d | mae\_ci\_low | mae\_ci\_high |
| --- | --- | --- | --- | --- | --- | --- | --- |
| fold 1 | outside B's scope | 2,495 | 5.7469 | 9.2477 | 0.4341 |  |  |
| fold 1 | inside B's scope | 10,325 | 3.7456 | 6.0978 | 0.5796 |  |  |
| fold 2 | outside B's scope | 2,448 | 7.0581 | 10.5909 | 0.3766 |  |  |
| fold 2 | inside B's scope | 10,372 | 5.5874 | 9.3896 | 0.4890 |  |  |
| fold 3 | outside B's scope | 2,365 | 6.8690 | 10.3495 | 0.3315 |  |  |
| fold 3 | inside B's scope | 10,453 | 5.8381 | 9.5759 | 0.4497 |  |  |
| fold 4 | outside B's scope | 2,378 | 9.0770 | 13.0824 | 0.2990 |  |  |
| fold 4 | inside B's scope | 10,433 | 7.1352 | 11.3453 | 0.4241 |  |  |
| fold 5 | outside B's scope | 1,681 | 4.9890 | 6.4844 | 0.3783 |  |  |
| fold 5 | inside B's scope | 9,059 | 3.6070 | 4.7054 | 0.4981 |  |  |
| test | outside B's scope | 3,366 | 5.7491 | 7.1854 | 0.2802 | 5.5929 | 5.8946 |
| test | inside B's scope | 15,422 | 4.0280 | 5.3586 | 0.4429 | 3.9750 | 4.0858 |

Five-fold summary (a\_fallback\_summary.csv):

| scope | mean\_5\_folds | se\_5\_folds |
| --- | --- | --- |
| inside B's scope | 5.1827 | 0.6691 |
| outside B's scope | 6.7480 | 0.6940 |

Run `20261024T052445Z` on uncommitted code (working tree on 7e6941f) · 6 checks, all PASS · reads T1's frozen predictions; no refit, no threshold change. Coverage and review dropdowns are on the parent tab "B9 Conclusion".

## B9.1 Train, validation and test

**What was done:** Train, validation (selection scores, G-10) and test with 95% bootstrap intervals (1000 resamples, seed 42) for B, A and references. B's test MAE 3.2992 \[3.2449, 3.3533\], width 0.1084.

Validation means are selection scores (G-10), mean over 5 folds ± SE; test = T1's single read with a 95% bootstrap interval (train\_val\_test.csv). Train means exist only where the model was fitted per fold in B6/s06 (plain and dummy; the frozen regression model is the plain linear recipe).

| model | rows | metric | train\_mean | validation\_mean | validation\_se | test | test\_ci\_low | test\_ci\_high | ci\_width | test\_rows |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B frozen | B test rows | mae | 3.8607 | 5.0247 | 0.6115 | 3.2992 | 3.2449 | 3.3533 | 0.1084 | 15,422 |
| B frozen | B test rows | rmse | 6.0443 | 7.8367 | 1.1084 | 4.7750 | 4.5934 | 4.9515 | 0.3581 | 15,422 |
| B frozen | B test rows | r2 | 0.2437 | 0.0873 | 0.0530 | 0.1849 | 0.1616 | 0.2074 | 0.0458 | 15,422 |
| B frozen | B test rows | within\_3d | 0.5563 | 0.5010 | 0.0269 | 0.5755 | 0.5676 | 0.5838 | 0.0162 | 15,422 |
| A frozen | B test rows | mae |  | 5.1423 | 0.6616 | 4.0280 | 3.9701 | 4.0834 | 0.1134 | 15,422 |
| A frozen | B test rows | rmse |  | 7.9896 | 1.1872 | 5.3586 | 5.1971 | 5.5110 | 0.3139 | 15,422 |
| A frozen | B test rows | r2 |  | 0.0574 | 0.0619 | -0.0265 | -0.0614 | 0.0067 | 0.0681 | 15,422 |
| A frozen | B test rows | within\_3d |  | 0.4883 | 0.0265 | 0.4429 | 0.4352 | 0.4510 | 0.0158 | 15,422 |
| B plain | B test rows | mae | 3.8607 | 5.0247 | 0.6115 | 3.2992 | 3.2449 | 3.3533 | 0.1084 | 15,422 |
| B plain | B test rows | rmse | 6.0443 | 7.8367 | 1.1084 | 4.7750 | 4.5934 | 4.9515 | 0.3581 | 15,422 |
| B plain | B test rows | r2 | 0.2437 | 0.0873 | 0.0530 | 0.1849 | 0.1616 | 0.2074 | 0.0458 | 15,422 |
| B plain | B test rows | within\_3d | 0.5563 | 0.5010 | 0.0269 | 0.5755 | 0.5676 | 0.5838 | 0.0162 | 15,422 |
| B dummy | B test rows | mae | 4.7937 | 5.9689 | 0.7107 | 4.3849 | 4.3273 | 4.4414 | 0.1141 | 15,422 |
| B dummy | B test rows | rmse | 7.1055 | 8.7467 | 1.2172 | 5.7088 | 5.5400 | 5.8764 | 0.3364 | 15,422 |
| B dummy | B test rows | r2 | -0.0435 | -0.1398 | 0.0414 | -0.1651 | -0.1900 | -0.1428 | 0.0471 | 15,422 |
| B dummy | B test rows | within\_3d | 0.4394 | 0.3752 | 0.0259 | 0.3710 | 0.3636 | 0.3784 | 0.0148 | 15,422 |
| A frozen | A test rows | mae | 4.2862 | 5.4701 | 0.6733 | 4.3364 | 4.2813 | 4.3900 | 0.1087 | 18,788 |
| A frozen | A test rows | rmse | 6.8815 | 8.5785 | 1.1785 | 5.7289 | 5.5944 | 5.8754 | 0.2810 | 18,788 |
| A frozen | A test rows | r2 | 0.2382 | 0.0911 | 0.0729 | 0.0340 | 0.0045 | 0.0593 | 0.0548 | 18,788 |
| A frozen | A test rows | within\_3d | 0.5132 | 0.4654 | 0.0256 | 0.4138 | 0.4066 | 0.4204 | 0.0138 | 18,788 |
| A plain | A test rows | mae | 4.2862 | 5.4701 | 0.6733 | 4.3364 | 4.2813 | 4.3900 | 0.1087 | 18,788 |
| A plain | A test rows | rmse | 6.8815 | 8.5785 | 1.1785 | 5.7289 | 5.5944 | 5.8754 | 0.2810 | 18,788 |
| A plain | A test rows | r2 | 0.2382 | 0.0911 | 0.0729 | 0.0340 | 0.0045 | 0.0593 | 0.0548 | 18,788 |
| A plain | A test rows | within\_3d | 0.5132 | 0.4654 | 0.0256 | 0.4138 | 0.4066 | 0.4204 | 0.0138 | 18,788 |
| A dummy | A test rows | mae | 5.3118 | 6.4946 | 0.6889 | 4.8755 | 4.8192 | 4.9337 | 0.1145 | 18,788 |
| A dummy | A test rows | rmse | 8.0528 | 9.5348 | 1.1572 | 6.2614 | 6.1152 | 6.4200 | 0.3047 | 18,788 |
| A dummy | A test rows | r2 | -0.0432 | -0.1355 | 0.0415 | -0.1540 | -0.1735 | -0.1361 | 0.0374 | 18,788 |
| A dummy | A test rows | within\_3d | 0.4001 | 0.3390 | 0.0229 | 0.3213 | 0.3140 | 0.3283 | 0.0144 | 18,788 |

Where the validation numbers come from:

| model | rows | validation\_source |
| --- | --- | --- |
| B frozen | B test rows | b08 metrics\_by\_population.csv |
| A frozen | B test rows | b08 metrics\_by\_population.csv |
| B plain | B test rows | b06 metrics\_long.csv (raw) |
| B dummy | B test rows | b06 metrics\_long.csv (raw) |
| A frozen | A test rows | b08 metrics\_by\_population.csv |
| A plain | A test rows | s06 metrics\_long.csv (raw) |
| A dummy | A test rows | s06 metrics\_long.csv (raw) |

- PASS: no refit: B's and A's bundles re-predict T1's test predictions on the rebuilt rows (within 1e-9) (B 15,422 rows (max difference 3.6e-15), A 18,788 rows (max difference 3.6e-15); CSV round-trip only)
- PASS: every restated test number equals T1's metrics\_test.csv
- PASS: bootstrap intervals contain the T1 point estimate (1000 resamples, seed 42)
- PASS: validation scores are labelled selection scores (source column filled wherever a value is shown)
- PASS: A's tree untouched: A's code matches e5-A-frozen

## B9.2 B versus A, and B versus its references, on B's test rows

**What was done:** B minus A on B's test rows: MAE -0.7288 \[-0.7537, -0.7030\] (excludes zero).

&#91;embedded content: paired\_test\_differences.csv · B9 run, B frozen minus A frozen on B's test rows\]

(paired\_test\_differences.csv; 1,000 paired resamples of test orders, seed 42)

| comparison | rows | metric | difference | ci\_low | ci\_high | b\_better | interval\_excludes\_zero |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B frozen minus A frozen | B test rows | mae | -0.7288 | -0.7537 | -0.7030 | True | True |
| B frozen minus A frozen | B test rows | rmse | -0.5836 | -0.6257 | -0.5447 | True | True |
| B frozen minus A frozen | B test rows | r2 | 0.2114 | 0.1904 | 0.2342 | True | True |
| B frozen minus A frozen | B test rows | within\_3d | 0.1326 | 0.1255 | 0.1394 | True | True |
| B frozen minus B plain | B test rows | mae | 0.0000 | 0.0000 | 0.0000 | False | False |
| B frozen minus B plain | B test rows | rmse | 0.0000 | 0.0000 | 0.0000 | False | False |
| B frozen minus B plain | B test rows | r2 | 0.0000 | 0.0000 | 0.0000 | False | False |
| B frozen minus B plain | B test rows | within\_3d | 0.0000 | 0.0000 | 0.0000 | False | False |
| B frozen minus B dummy | B test rows | mae | -1.0858 | -1.1381 | -1.0342 | True | True |
| B frozen minus B dummy | B test rows | rmse | -0.9338 | -0.9994 | -0.8621 | True | True |
| B frozen minus B dummy | B test rows | r2 | 0.3500 | 0.3205 | 0.3802 | True | True |
| B frozen minus B dummy | B test rows | within\_3d | 0.2045 | 0.1940 | 0.2161 | True | True |

- PASS: bootstrap intervals contain the T1 point estimate (1000 resamples, seed 42)

## B9.3 Error analysis by slice

**What was done:** Slices judged with at least 100 orders. Customer state: 7 judged, B better in 7; mean gain -0.930 days (SD 0.275).

A slice is judged with at least 100 test orders; smaller ones are descriptive only (G-40).

Aggregate over judged slices (subgroups\_aggregate.csv):

| slice | judged\_slices | too\_few | pooled\_mae\_A | pooled\_mae\_B | mean\_gain | sd\_gain | slices\_B\_better |
| --- | --- | --- | --- | --- | --- | --- | --- |
| customer\_state | 7 | 0 | 4.028 | 3.299 | -0.930 | 0.275 | 7 |
| route\_seller\_to\_customer\_state | 20 | 28 | 3.970 | 3.233 | -0.816 | 0.387 | 20 |
| distance\_band | 5 | 0 | 4.028 | 3.299 | -0.744 | 0.313 | 5 |
| basket | 3 | 0 | 4.028 | 3.299 | -0.639 | 0.095 | 3 |
| month | 4 | 0 | 4.028 | 3.299 | -0.546 | 0.549 | 3 |

&#91;image: by\_customer\_state\]

**customer\_state**:

| value | orders | mae\_A | mae\_B | gain\_B\_minus\_A | judged |
| --- | --- | --- | --- | --- | --- |
| SP | 8,419 | 3.126 | 2.610 | -0.516 | True |
| RJ | 2,033 | 5.727 | 4.611 | -1.116 | True |
| MG | 1,979 | 4.437 | 3.546 | -0.891 | True |
| PR | 925 | 3.917 | 3.260 | -0.657 | True |
| RS | 891 | 5.013 | 4.012 | -1.001 | True |
| BA | 604 | 7.003 | 6.010 | -0.992 | True |
| SC | 571 | 5.354 | 4.021 | -1.334 | True |

**route\_seller\_to\_customer\_state** — judged routes only (20 of 48; the other 28 are too small to judge; full list in subgroups.csv):

| value | orders | mae\_A | mae\_B | gain\_B\_minus\_A | judged |
| --- | --- | --- | --- | --- | --- |
| SP->SP | 6,615 | 2.859 | 2.433 | -0.425 | True |
| SP->RJ | 1,277 | 6.112 | 4.798 | -1.315 | True |
| SP->MG | 1,233 | 4.819 | 3.655 | -1.164 | True |
| SP->RS | 585 | 5.410 | 4.031 | -1.379 | True |
| PR->SP | 584 | 4.330 | 3.335 | -0.995 | True |
| SP->PR | 562 | 4.227 | 3.464 | -0.763 | True |
| SP->BA | 434 | 7.269 | 6.116 | -1.153 | True |
| MG->SP | 428 | 4.312 | 3.223 | -1.089 | True |
| SP->SC | 356 | 5.721 | 4.249 | -1.472 | True |
| RJ->SP | 321 | 3.692 | 3.095 | -0.597 | True |
| MG->MG | 320 | 2.778 | 2.539 | -0.239 | True |
| SC->SP | 275 | 4.504 | 3.614 | -0.890 | True |
| RJ->RJ | 242 | 3.228 | 2.726 | -0.503 | True |
| PR->RJ | 186 | 6.067 | 5.508 | -0.559 | True |
| MG->RJ | 174 | 5.995 | 4.691 | -1.305 | True |
| RS->SP | 171 | 3.031 | 2.518 | -0.513 | True |
| PR->PR | 163 | 3.050 | 2.695 | -0.355 | True |
| PR->MG | 146 | 5.431 | 4.812 | -0.620 | True |
| RJ->MG | 135 | 3.833 | 3.341 | -0.491 | True |
| PR->RS | 110 | 4.385 | 3.901 | -0.484 | True |

**distance\_band**:

| value | orders | mae\_A | mae\_B | gain\_B\_minus\_A | judged |
| --- | --- | --- | --- | --- | --- |
| 300-600 km | 5,568 | 4.529 | 3.567 | -0.962 | True |
| <100 km | 4,106 | 2.797 | 2.457 | -0.340 | True |
| 100-300 km | 2,586 | 3.157 | 2.647 | -0.510 | True |
| 600-1000 km | 2,127 | 5.128 | 4.037 | -1.091 | True |
| >=1000 km | 1,035 | 6.131 | 5.312 | -0.819 | True |

**basket**:

| value | orders | mae\_A | mae\_B | gain\_B\_minus\_A | judged |
| --- | --- | --- | --- | --- | --- |
| 1 item | 13,902 | 4.072 | 3.329 | -0.743 | True |
| 2 items | 1,172 | 3.648 | 3.031 | -0.617 | True |
| 3+ items | 348 | 3.564 | 3.007 | -0.557 | True |

**month**:

| value | orders | mae\_A | mae\_B | gain\_B\_minus\_A | judged |
| --- | --- | --- | --- | --- | --- |
| 2018-08 | 5,272 | 3.869 | 2.789 | -1.080 | True |
| 2018-07 | 4,822 | 4.318 | 3.382 | -0.936 | True |
| 2018-06 | 4,821 | 3.986 | 3.766 | -0.220 | True |
| 2018-05 | 507 | 3.330 | 3.383 | 0.054 | True |

- PASS: slice rule: a slice is judged only above the minimum

## B9.4 Drift: final-fit rows vs test rows (G-77)

**What was done:** 3 numeric features moved by |SMD| >= 0.2 between final-fit and test rows: route\_recent\_delivery\_days -0.73, route\_recent\_carrier\_transit\_days -0.56, purchase\_month +0.41. Target: mean 12.111 -> 7.904; median 10.053 -> 6.957 (G-77).

&#91;image: drift\_numeric\]

Numeric features (standardised mean difference, test minus final-fit; |0.2| or more is a notable move):

| feature | development | test | change |
| --- | --- | --- | --- |
| route\_recent\_delivery\_days | 10.805 | 7.935 | -0.734 |
| route\_recent\_carrier\_transit\_days | 7.628 | 5.515 | -0.561 |
| purchase\_month | 5.889 | 6.963 | 0.413 |
| seller\_prior\_dispatch\_days | 3.235 | 2.870 | -0.192 |
| interstate\_share | 0.573 | 0.514 | -0.119 |
| total\_freight | 20.178 | 22.210 | 0.106 |
| total\_volume\_cm3 | 18231.049 | 15223.400 | -0.105 |
| distance\_km\_max | 423.634 | 392.036 | -0.089 |
| seller\_prior\_late\_handover\_rate | 0.084 | 0.074 | -0.087 |
| total\_weight\_g | 2474.436 | 2123.513 | -0.077 |
| seller\_prior\_late\_handover\_days | 0.288 | 0.220 | -0.075 |
| freight\_ratio | 0.284 | 0.302 | 0.063 |
| payment\_installments\_max | 2.888 | 2.735 | -0.058 |
| n\_sellers | 1.013 | 1.018 | 0.033 |
| purchase\_dayofweek | 2.761 | 2.708 | -0.027 |
| n\_items | 1.147 | 1.138 | -0.017 |
| n\_products | 1.039 | 1.039 | -0.002 |
| total\_price | 131.879 | 131.555 | -0.002 |

Categorical features and history sources (total variation distance per feature; share changes of the levels that moved most):

| kind | feature | level | development | test | change |
| --- | --- | --- | --- | --- | --- |
| categorical | route\_seller\_to\_customer\_state | SP->SP | 0.381 | 0.429 | 0.047 |
| categorical | route\_seller\_to\_customer\_state | SP->RJ | 0.107 | 0.083 | -0.024 |
| categorical | route\_seller\_to\_customer\_state | SP->MG | 0.096 | 0.080 | -0.017 |
| categorical | route\_seller\_to\_customer\_state | SP->RS | 0.047 | 0.038 | -0.009 |
| categorical | route\_seller\_to\_customer\_state | SP->SC | 0.030 | 0.023 | -0.007 |
| categorical | route\_seller\_to\_customer\_state | RJ->SP | 0.015 | 0.021 | 0.006 |
| categorical | route\_seller\_to\_customer\_state | MG->SP | 0.033 | 0.028 | -0.005 |
| categorical | route\_seller\_to\_customer\_state | RJ->RJ | 0.011 | 0.016 | 0.005 |
| categorical | route\_seller\_to\_customer\_state | MG->RJ | 0.015 | 0.011 | -0.004 |
| categorical | route\_seller\_to\_customer\_state | RS->SP | 0.008 | 0.011 | 0.003 |
| categorical total | route\_seller\_to\_customer\_state | (all levels) |  |  | 0.079 |
| categorical | primary\_category | health\_beauty | 0.076 | 0.107 | 0.031 |
| categorical | primary\_category | housewares | 0.057 | 0.083 | 0.026 |
| categorical | primary\_category | cool\_stuff | 0.040 | 0.017 | -0.022 |
| categorical | primary\_category | sports\_leisure | 0.083 | 0.065 | -0.018 |
| categorical | primary\_category | watches\_gifts | 0.052 | 0.068 | 0.017 |
| categorical | primary\_category | toys | 0.043 | 0.027 | -0.016 |
| categorical | primary\_category | garden\_tools | 0.037 | 0.023 | -0.015 |
| categorical | primary\_category | construction\_tools\_construction | 0.005 | 0.019 | 0.014 |
| categorical | primary\_category | furniture\_decor | 0.069 | 0.055 | -0.013 |
| categorical | primary\_category | computers\_accessories | 0.069 | 0.056 | -0.013 |
| categorical | primary\_category | auto | 0.036 | 0.048 | 0.012 |
| categorical | primary\_category | Unknown | 0.017 | 0.006 | -0.011 |
| categorical | primary\_category | pet\_shop | 0.016 | 0.027 | 0.010 |
| categorical | primary\_category | telephony | 0.042 | 0.033 | -0.009 |
| categorical | primary\_category | food | 0.003 | 0.010 | 0.007 |
| categorical | primary\_category | perfumery | 0.031 | 0.024 | -0.007 |
| categorical | primary\_category | baby | 0.027 | 0.034 | 0.007 |
| categorical | primary\_category | fashion\_bags\_accessories | 0.020 | 0.014 | -0.006 |
| categorical | primary\_category | office\_furniture | 0.014 | 0.008 | -0.006 |
| categorical | primary\_category | construction\_tools\_lights | 0.001 | 0.007 | 0.006 |
| categorical | primary\_category | electronics | 0.026 | 0.021 | -0.005 |
| categorical | primary\_category | home\_appliances | 0.007 | 0.012 | 0.005 |
| categorical | primary\_category | home\_construction | 0.004 | 0.008 | 0.004 |
| categorical | primary\_category | consoles\_games | 0.011 | 0.008 | -0.003 |
| categorical | primary\_category | furniture\_living\_room | 0.003 | 0.006 | 0.003 |
| categorical | primary\_category | luggage\_accessories | 0.012 | 0.009 | -0.003 |
| categorical | primary\_category | books\_technical | 0.002 | 0.005 | 0.003 |
| categorical | primary\_category | art | 0.002 | 0.004 | 0.002 |
| categorical | primary\_category | market\_place | 0.003 | 0.001 | -0.002 |
| categorical | primary\_category | fashion\_shoes | 0.003 | 0.001 | -0.002 |
| categorical | primary\_category | small\_appliances\_home\_oven\_and\_coffee | 0.000 | 0.002 | 0.002 |
| categorical | primary\_category | bed\_bath\_table | 0.103 | 0.102 | -0.002 |
| categorical | primary\_category | home\_confort | 0.005 | 0.003 | -0.002 |
| categorical | primary\_category | signaling\_and\_security | 0.001 | 0.003 | 0.002 |
| categorical | primary\_category | small\_appliances | 0.007 | 0.005 | -0.001 |
| categorical | primary\_category | construction\_tools\_safety | 0.001 | 0.002 | 0.001 |
| categorical | primary\_category | agro\_industry\_and\_commerce | 0.002 | 0.003 | 0.001 |
| categorical | primary\_category | fashion\_underwear\_beach | 0.001 | 0.000 | -0.001 |
| categorical | primary\_category | stationery | 0.024 | 0.025 | 0.001 |
| categorical | primary\_category | arts\_and\_craftmanship | 0.000 | 0.001 | 0.001 |
| categorical | primary\_category | cine\_photo | 0.000 | 0.001 | 0.001 |
| categorical | primary\_category | furniture\_bedroom | 0.001 | 0.002 | 0.001 |
| categorical | primary\_category | tablets\_printing\_image | 0.001 | 0.000 | -0.001 |
| categorical | primary\_category | kitchen\_dining\_laundry\_garden\_furniture | 0.003 | 0.004 | 0.001 |
| categorical | primary\_category | drinks | 0.003 | 0.004 | 0.001 |
| categorical | primary\_category | home\_appliances\_2 | 0.002 | 0.003 | 0.001 |
| categorical | primary\_category | party\_supplies | 0.000 | 0.001 | 0.001 |
| categorical | primary\_category | computers | 0.002 | 0.001 | -0.001 |
| categorical | primary\_category | diapers\_and\_hygiene | 0.000 | 0.001 | 0.001 |
| categorical | primary\_category | furniture\_mattress\_and\_upholstery | 0.001 | 0.000 | -0.000 |
| categorical | primary\_category | fashion\_male\_clothing | 0.001 | 0.001 | -0.000 |
| categorical | primary\_category | costruction\_tools\_garden | 0.002 | 0.002 | 0.000 |
| categorical | primary\_category | air\_conditioning | 0.003 | 0.002 | -0.000 |
| categorical | primary\_category | fashio\_female\_clothing | 0.000 | 0.000 | -0.000 |
| categorical | primary\_category | music | 0.000 | 0.001 | 0.000 |
| categorical | primary\_category | fashion\_sport | 0.000 | 0.000 | -0.000 |
| categorical | primary\_category | costruction\_tools\_tools | 0.001 | 0.001 | 0.000 |
| categorical | primary\_category | food\_drink | 0.002 | 0.002 | -0.000 |
| categorical | primary\_category | flowers | 0.000 | 0.000 | -0.000 |
| categorical | primary\_category | fixed\_telephony | 0.002 | 0.002 | -0.000 |
| categorical | primary\_category | books\_imported | 0.001 | 0.001 | 0.000 |
| categorical | primary\_category | la\_cuisine | 0.000 | 0.000 | -0.000 |
| categorical | primary\_category | cds\_dvds\_musicals | 0.000 | 0.000 | -0.000 |
| categorical | primary\_category | industry\_commerce\_and\_business | 0.003 | 0.002 | -0.000 |
| categorical | primary\_category | dvds\_blu\_ray | 0.000 | 0.000 | 0.000 |
| categorical | primary\_category | christmas\_supplies | 0.001 | 0.001 | 0.000 |
| categorical | primary\_category | home\_comfort\_2 | 0.000 | 0.000 | -0.000 |
| categorical | primary\_category | books\_general\_interest | 0.005 | 0.005 | -0.000 |
| categorical | primary\_category | musical\_instruments | 0.006 | 0.006 | 0.000 |
| categorical | primary\_category | fashion\_childrens\_clothes | 0.000 | 0.000 | -0.000 |
| categorical | primary\_category | audio | 0.003 | 0.003 | -0.000 |
| categorical total | primary\_category | (all levels) |  |  | 0.162 |
| categorical | primary\_payment\_type | debit\_card | 0.011 | 0.037 | 0.026 |
| categorical | primary\_payment\_type | boleto | 0.201 | 0.184 | -0.017 |
| categorical | primary\_payment\_type | voucher | 0.033 | 0.028 | -0.005 |
| categorical | primary\_payment\_type | credit\_card | 0.755 | 0.751 | -0.004 |
| categorical total | primary\_payment\_type | (all levels) |  |  | 0.026 |
| source share | seller\_prior\_source | seller-state fallback | 0.041 | 0.042 | 0.002 |
| source share | seller\_prior\_source | own seller history | 0.959 | 0.958 | -0.002 |
| categorical total | seller\_prior\_source | (all levels) |  |  | 0.002 |
| source share | route\_recent\_delivery\_days\_source | own route history | 0.958 | 0.972 | 0.014 |
| source share | route\_recent\_delivery\_days\_source | state-mix fallback | 0.042 | 0.028 | -0.014 |
| categorical total | route\_recent\_delivery\_days\_source | (all levels) |  |  | 0.014 |
| source share | route\_recent\_carrier\_transit\_days\_source | own route history | 0.958 | 0.972 | 0.014 |
| source share | route\_recent\_carrier\_transit\_days\_source | state-mix fallback | 0.042 | 0.028 | -0.014 |
| categorical total | route\_recent\_carrier\_transit\_days\_source | (all levels) |  |  | 0.014 |

Target:

| feature | level | development | test | change | measure |
| --- | --- | --- | --- | --- | --- |
| lead\_days | mean | 12.111 | 7.904 | -4.208 | difference |
| lead\_days | median | 10.053 | 6.957 | -3.096 | difference |

## B9.5 Interpretation

**What was done:** Largest term: primary\_category\_arts\_and\_craftmanship. Top permutation feature: seller\_prior\_dispatch\_days. Against B4's ranking: Spearman 0.16, top-10 overlap 7; DIVERGES: team alerted, model unchanged.

**Coefficients of B's frozen model** (coefficients.csv; multiplies predicted lead time by ratio\_per\_unit per +1 unit of the transformed term (log1p target)). The largest terms are mostly single levels of categorical features (one-hot); the numeric terms are listed separately below because they carry the business levers.

&#91;image: coefficients\]

Largest 15 terms overall:

| term | coefficient | ratio\_per\_unit |
| --- | --- | --- |
| primary\_category\_arts\_and\_craftmanship | -0.530 | 0.588 |
| route\_seller\_to\_customer\_state\_RS->SP | -0.409 | 0.665 |
| route\_seller\_to\_customer\_state\_RS->PR | -0.400 | 0.670 |
| route\_seller\_to\_customer\_state\_BA->MG | -0.386 | 0.680 |
| route\_seller\_to\_customer\_state\_BA->SP | -0.344 | 0.709 |
| route\_seller\_to\_customer\_state\_RS->SC | -0.334 | 0.716 |
| route\_seller\_to\_customer\_state\_RS->MG | -0.334 | 0.716 |
| primary\_category\_la\_cuisine | -0.287 | 0.750 |
| route\_seller\_to\_customer\_state\_BA->RJ | -0.279 | 0.756 |
| primary\_category\_music | -0.246 | 0.782 |
| route\_seller\_to\_customer\_state\_MG->PR | -0.231 | 0.794 |
| route\_seller\_to\_customer\_state\_PR->SP | -0.230 | 0.794 |
| route\_seller\_to\_customer\_state\_MG->SP | -0.218 | 0.804 |
| route\_seller\_to\_customer\_state\_RJ->PR | -0.210 | 0.811 |
| primary\_category\_books\_imported | -0.205 | 0.814 |

Numeric terms (all):

| term | coefficient | ratio\_per\_unit |
| --- | --- | --- |
| distance\_km\_max | 0.182 | 1.199 |
| route\_recent\_delivery\_days | 0.129 | 1.138 |
| seller\_prior\_dispatch\_days | 0.115 | 1.122 |
| interstate\_share | 0.097 | 1.102 |
| seller\_prior\_late\_handover\_days | -0.045 | 0.956 |
| total\_freight | 0.045 | 1.046 |
| n\_sellers | -0.033 | 0.967 |
| n\_items | -0.030 | 0.970 |
| seller\_prior\_late\_handover\_rate | 0.029 | 1.030 |
| purchase\_dayofweek | 0.029 | 1.029 |
| purchase\_month | 0.017 | 1.017 |
| total\_price | 0.011 | 1.011 |
| n\_products | -0.006 | 0.994 |
| payment\_installments\_max | 0.005 | 1.005 |
| total\_volume\_cm3 | 0.005 | 1.005 |
| freight\_ratio | 0.003 | 1.003 |
| route\_recent\_carrier\_transit\_days | -0.003 | 0.997 |
| missingindicator\_total\_weight\_g | -0.002 | 0.998 |
| total\_weight\_g | 0.001 | 1.001 |

**Permutation importance on B's test rows** (permutation\_importance.csv; description only, B9-D2):

&#91;image: permutation\_importance\]

| feature | importance\_mean | importance\_sd | rank |
| --- | --- | --- | --- |
| seller\_prior\_dispatch\_days | 0.2932 | 0.0072 | 1 |
| route\_seller\_to\_customer\_state | 0.2638 | 0.0067 | 2 |
| distance\_km\_max | 0.1977 | 0.0081 | 3 |
| primary\_payment\_type | 0.0423 | 0.0031 | 4 |
| seller\_prior\_late\_handover\_days | 0.0297 | 0.0034 | 5 |
| seller\_prior\_late\_handover\_rate | 0.0245 | 0.0024 | 6 |
| n\_sellers | 0.0133 | 0.0021 | 7 |
| primary\_category | 0.0114 | 0.0044 | 8 |
| purchase\_dayofweek | 0.0108 | 0.0031 | 9 |
| route\_recent\_carrier\_transit\_days | 0.0085 | 0.0001 | 10 |
| n\_items | 0.0081 | 0.0019 | 11 |
| purchase\_month | 0.0014 | 0.0004 | 12 |
| total\_weight\_g | 0.0001 | 0.0002 | 13 |
| total\_volume\_cm3 | -0.0005 | 0.0003 | 14 |
| total\_price | -0.0011 | 0.0007 | 15 |
| payment\_installments\_max | -0.0013 | 0.0002 | 16 |
| freight\_ratio | -0.0015 | 0.0002 | 17 |
| n\_products | -0.0017 | 0.0002 | 18 |
| route\_recent\_delivery\_days | -0.0067 | 0.0081 | 19 |
| total\_freight | -0.0325 | 0.0026 | 20 |
| interstate\_share | -0.0549 | 0.0040 | 21 |

**Against B4's development ranking** (ranking\_consistency.json): 21 features compared, Spearman 0.16, top-10 overlap 7. Rule: diverges when Spearman < 0.5 or fewer than 5 of the top 10 shared (as A's s09 9.5). Result: **DIVERGES**. Action: alert the team: the test-row importance differs from B4's development ranking; describe, do not change the frozen model. Note: B4 ranks each feature alone (Spearman or mutual information with the target); permutation importance measures what the fitted model loses without the feature, given the others, on the test period, so the two answer different questions.

## B9.7 Business summary

**What was done:** B on its test rows: within 3 days 57.6%; delivered more than 3 days later than predicted 11.1% (A on the same rows 9.3%).

By customer state (business\_summary.csv). "Later than predicted" = actual lead time above the prediction; "more than 3 days later" is the promise-breaking case.

| customer\_state | orders | mae\_B | within\_3d\_B | share\_later\_than\_predicted\_B | share\_more\_than\_3d\_later\_B | mae\_A | share\_more\_than\_3d\_later\_A |
| --- | --- | --- | --- | --- | --- | --- | --- |
| BA | 604 | 6.010 | 0.270 | 0.263 | 0.161 | 7.003 | 0.156 |
| MG | 1,979 | 3.546 | 0.490 | 0.227 | 0.081 | 4.437 | 0.077 |
| PR | 925 | 3.260 | 0.523 | 0.284 | 0.114 | 3.917 | 0.080 |
| RJ | 2,033 | 4.611 | 0.376 | 0.230 | 0.103 | 5.727 | 0.086 |
| RS | 891 | 4.012 | 0.441 | 0.269 | 0.102 | 5.013 | 0.080 |
| SC | 571 | 4.021 | 0.406 | 0.194 | 0.072 | 5.354 | 0.054 |
| SP | 8,419 | 2.610 | 0.697 | 0.340 | 0.120 | 3.126 | 0.099 |
| all | 15,422 | 3.299 | 0.576 | 0.295 | 0.111 | 4.028 | 0.093 |

**Files**: pipeline\_b/stages/b09/regression/outputs/ (run 20261024T052445Z): business\_summary.csv, coefficients.csv, conclusion.md, drift.csv, paired\_test\_differences.csv, permutation\_importance.csv, ranking\_consistency.json, subgroups.csv, subgroups\_aggregate.csv, train\_val\_test.csv; plus figures/.
