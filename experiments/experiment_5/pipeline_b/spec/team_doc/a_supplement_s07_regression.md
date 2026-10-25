# s07 Tuning › regression — evidence cards

## Supplement for decisions and the report (added 2026-10-24; DOC\_GAPS D-04)

Added after the pipeline ran, from accepted outputs only; nothing above is changed. Source: A's s07 grid\_results.csv and plain\_vs\_tuned.csv at e5-A-frozen (run 20261023T084131Z); same layout as the B7 tabs.

### Full grid — linear/logistic (9 configurations)

Best mean reg.sel.log.ridge.alpha=20 = 5.4620 days (SE 0.6728); one-SE bound 6.1348 days; one-SE choice reg.sel.log.ridge.alpha=100 = 5.4642 days. Against the plain s06 model: tuned paired gain +0.0059 (paired SE 0.0056), better in 4 of 5 folds; carried: plain (G-55). Grid edge: the one-SE choice sits at the edge of the grid for alpha = 100.0 (highest value in the grid) (the simpler end, where the one-SE rule moves the choice by design).

Effect of each parameter:

| parameter | value | configurations | best validation mean | mean over its configurations |
| --- | --- | --- | --- | --- |
| alpha | 0.0100 | 1 | 5.4697 | 5.4697 |
| alpha | 0.1000 | 1 | 5.4679 | 5.4679 |
| alpha | 0.5000 | 1 | 5.4663 | 5.4663 |
| alpha | 1.0000 | 1 | 5.4656 | 5.4656 |
| alpha | 10.0000 | 1 | 5.4627 | 5.4627 |
| alpha | 100.0000 | 1 | 5.4642 | 5.4642 |
| alpha | 20.0000 | 1 | 5.4620 | 5.4620 |
| alpha | 5.0000 | 1 | 5.4637 | 5.4637 |
| alpha | 50.0000 | 1 | 5.4621 | 5.4621 |

Every configuration, ranked (per-fold validation, mean, SE, training mean, gap):

| alpha | val f1 | val f2 | val f3 | val f4 | val f5 | validation\_mean | validation\_se | train\_mean | train\_validation\_gap | rank | flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20.0 | 4.1198 | 5.8606 | 6.0124 | 7.4905 | 3.8265 | 5.4620 | 0.6728 | 4.2917 | 1.1703 | 1 | best mean; within one SE |
| 50.0 | 4.1187 | 5.8591 | 6.0113 | 7.4897 | 3.8318 | 5.4621 | 0.6720 | 4.2954 | 1.1667 | 2 | within one SE |
| 10.0 | 4.1217 | 5.8627 | 6.0136 | 7.4912 | 3.8245 | 5.4627 | 0.6731 | 4.2903 | 1.1725 | 3 | within one SE |
| 5.0 | 4.1237 | 5.8645 | 6.0147 | 7.4917 | 3.8237 | 5.4637 | 0.6731 | 4.2894 | 1.1743 | 4 | within one SE |
| 100.0 | 4.1206 | 5.8600 | 6.0123 | 7.4896 | 3.8385 | 5.4642 | 0.6711 | 4.3009 | 1.1633 | 5 | one-SE choice; within one SE |
| 1.0 | 4.1287 | 5.8672 | 6.0164 | 7.4923 | 3.8235 | 5.4656 | 0.6729 | 4.2882 | 1.1774 | 6 | within one SE |
| 0.5 | 4.1305 | 5.8678 | 6.0167 | 7.4928 | 3.8235 | 5.4663 | 0.6728 | 4.2878 | 1.1785 | 7 | within one SE |
| 0.1 | 4.1335 | 5.8682 | 6.0200 | 7.4942 | 3.8234 | 5.4679 | 0.6729 | 4.2866 | 1.1813 | 8 | within one SE |
| 0.01 | 4.1349 | 5.8682 | 6.0267 | 7.4954 | 3.8233 | 5.4697 | 0.6732 | 4.2862 | 1.1835 | 9 | within one SE |

### Full grid — single tree (36 configurations)

Best mean reg.sel.log.tree\_reg.max\_depth=8.min\_samples\_leaf=200 = 5.3760 days (SE 0.7055); one-SE bound 6.0815 days; one-SE choice reg.sel.log.tree\_reg.max\_depth=4.min\_samples\_leaf=200 = 5.4332 days. Against the plain s06 model: tuned paired gain -0.0088 (paired SE 0.0359), better in 1 of 5 folds; carried: plain (G-55). Grid edge: the one-SE choice sits at the edge of the grid for max\_depth = 4 (lowest value in the grid); min\_samples\_leaf = 200 (highest value in the grid) (the simpler end, where the one-SE rule moves the choice by design).

Effect of each parameter:

| parameter | value | configurations | best validation mean | mean over its configurations |
| --- | --- | --- | --- | --- |
| max\_depth | 10 | 4 | 5.3834 | 5.4129 |
| max\_depth | 12 | 4 | 5.3855 | 5.4268 |
| max\_depth | 14 | 4 | 5.3823 | 5.4355 |
| max\_depth | 16 | 4 | 5.3826 | 5.4464 |
| max\_depth | 18 | 4 | 5.3820 | 5.4537 |
| max\_depth | 4 | 4 | 5.4218 | 5.4271 |
| max\_depth | 5 | 4 | 5.3998 | 5.4198 |
| max\_depth | 6 | 4 | 5.3913 | 5.4114 |
| max\_depth | 8 | 4 | 5.3760 | 5.4042 |
| min\_samples\_leaf | 100 | 9 | 5.3827 | 5.3991 |
| min\_samples\_leaf | 20 | 9 | 5.4302 | 5.5012 |
| min\_samples\_leaf | 200 | 9 | 5.3760 | 5.3912 |
| min\_samples\_leaf | 50 | 9 | 5.3974 | 5.4143 |

Every configuration, ranked (per-fold validation, mean, SE, training mean, gap):

| max\_depth | min\_samples\_leaf | val f1 | val f2 | val f3 | val f4 | val f5 | validation\_mean | validation\_se | train\_mean | train\_validation\_gap | rank | flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 8 | 200 | 4.0905 | 5.5711 | 6.1742 | 7.4695 | 3.5748 | 5.3760 | 0.7055 | 4.2917 | 1.0843 | 1 | best mean; within one SE |
| 18 | 200 | 4.0905 | 5.5593 | 6.1702 | 7.5050 | 3.5850 | 5.3820 | 0.7091 | 4.2607 | 1.1213 | 2 | within one SE |
| 14 | 200 | 4.0905 | 5.5589 | 6.1702 | 7.5057 | 3.5865 | 5.3823 | 0.7090 | 4.2613 | 1.1211 | 3 | within one SE |
| 16 | 200 | 4.0905 | 5.5593 | 6.1702 | 7.5040 | 3.5889 | 5.3826 | 0.7085 | 4.2608 | 1.1218 | 4 | within one SE |
| 8 | 100 | 4.0953 | 5.6749 | 6.1381 | 7.4660 | 3.5393 | 5.3827 | 0.7089 | 4.2564 | 1.1263 | 5 | within one SE |
| 10 | 200 | 4.0905 | 5.5628 | 6.1867 | 7.4756 | 3.6014 | 5.3834 | 0.7036 | 4.2744 | 1.1090 | 6 | within one SE |
| 12 | 200 | 4.0905 | 5.5666 | 6.1700 | 7.4944 | 3.6063 | 5.3855 | 0.7049 | 4.2652 | 1.1204 | 7 | within one SE |
| 10 | 100 | 4.0950 | 5.6885 | 6.1720 | 7.4439 | 3.5530 | 5.3905 | 0.7061 | 4.2192 | 1.1713 | 8 | within one SE |
| 6 | 200 | 4.0915 | 5.5828 | 6.1720 | 7.5336 | 3.5765 | 5.3913 | 0.7148 | 4.3282 | 1.0631 | 9 | within one SE |
| 18 | 100 | 4.0950 | 5.6791 | 6.1502 | 7.4595 | 3.5834 | 5.3934 | 0.7030 | 4.1775 | 1.2160 | 10 | within one SE |
| 14 | 100 | 4.0950 | 5.6903 | 6.1509 | 7.4627 | 3.5700 | 5.3938 | 0.7055 | 4.1832 | 1.2106 | 11 | within one SE |
| 16 | 100 | 4.0950 | 5.6860 | 6.1507 | 7.4588 | 3.5818 | 5.3945 | 0.7033 | 4.1790 | 1.2155 | 12 | within one SE |
| 6 | 100 | 4.0860 | 5.6820 | 6.1246 | 7.5178 | 3.5655 | 5.3952 | 0.7135 | 4.3092 | 1.0860 | 13 | within one SE |
| 12 | 100 | 4.0950 | 5.6957 | 6.1544 | 7.4378 | 3.5945 | 5.3955 | 0.6990 | 4.1953 | 1.2002 | 14 | within one SE |
| 8 | 50 | 4.1281 | 5.6898 | 6.1480 | 7.4760 | 3.5450 | 5.3974 | 0.7075 | 4.2284 | 1.1690 | 15 | within one SE |
| 5 | 50 | 4.1198 | 5.5474 | 6.1686 | 7.5604 | 3.6030 | 5.3998 | 0.7123 | 4.3511 | 1.0487 | 16 | within one SE |
| 6 | 50 | 4.1078 | 5.6657 | 6.1378 | 7.5324 | 3.5708 | 5.4029 | 0.7134 | 4.2991 | 1.1038 | 17 | within one SE |
| 5 | 200 | 4.1198 | 5.5598 | 6.1662 | 7.5750 | 3.5997 | 5.4041 | 0.7150 | 4.3653 | 1.0388 | 18 | within one SE |
| 10 | 50 | 4.1188 | 5.7095 | 6.1810 | 7.4546 | 3.5683 | 5.4065 | 0.7044 | 4.1700 | 1.2365 | 19 | within one SE |
| 12 | 50 | 4.1224 | 5.7245 | 6.1695 | 7.4564 | 3.6059 | 5.4157 | 0.6992 | 4.1264 | 1.2893 | 20 | within one SE |
| 14 | 50 | 4.1160 | 5.7254 | 6.1755 | 7.4592 | 3.6124 | 5.4177 | 0.6996 | 4.0969 | 1.3208 | 21 | within one SE |
| 4 | 100 | 4.1377 | 5.5306 | 6.1917 | 7.5972 | 3.6521 | 5.4218 | 0.7113 | 4.4061 | 1.0157 | 22 | within one SE |
| 4 | 50 | 4.1364 | 5.5386 | 6.1925 | 7.5972 | 3.6521 | 5.4233 | 0.7115 | 4.4032 | 1.0202 | 23 | within one SE |
| 5 | 100 | 4.1141 | 5.6875 | 6.1600 | 7.5600 | 3.6002 | 5.4244 | 0.7147 | 4.3533 | 1.0711 | 24 | within one SE |
| 16 | 50 | 4.1188 | 5.7217 | 6.1786 | 7.4834 | 3.6466 | 5.4298 | 0.6986 | 4.0816 | 1.3482 | 25 | within one SE |
| 4 | 20 | 4.1528 | 5.5416 | 6.2051 | 7.5972 | 3.6543 | 5.4302 | 0.7104 | 4.4016 | 1.0286 | 26 | within one SE |
| 4 | 200 | 4.1386 | 5.5550 | 6.1989 | 7.6108 | 3.6628 | 5.4332 | 0.7125 | 4.4140 | 1.0192 | 27 | one-SE choice; within one SE |
| 18 | 50 | 4.1188 | 5.7158 | 6.1853 | 7.5046 | 3.6542 | 5.4357 | 0.7010 | 4.0750 | 1.3608 | 28 | within one SE |
| 5 | 20 | 4.3868 | 5.5277 | 6.1757 | 7.5602 | 3.6047 | 5.4510 | 0.6900 | 4.3450 | 1.1060 | 29 | within one SE |
| 6 | 20 | 4.3678 | 5.6691 | 6.1535 | 7.5314 | 3.5603 | 5.4564 | 0.6934 | 4.2903 | 1.1662 | 30 | within one SE |
| 8 | 20 | 4.3913 | 5.7115 | 6.1564 | 7.5036 | 3.5401 | 5.4606 | 0.6911 | 4.2026 | 1.2579 | 31 | within one SE |
| 10 | 20 | 4.4182 | 5.7209 | 6.1818 | 7.4544 | 3.5815 | 5.4714 | 0.6775 | 4.1075 | 1.3638 | 32 | within one SE |
| 12 | 20 | 4.4391 | 5.7454 | 6.2239 | 7.5035 | 3.6399 | 5.5103 | 0.6776 | 4.0258 | 1.4845 | 33 | within one SE |
| 14 | 20 | 4.4570 | 5.7791 | 6.2631 | 7.5488 | 3.6921 | 5.5480 | 0.6783 | 3.9514 | 1.5966 | 34 | within one SE |
| 16 | 20 | 4.4564 | 5.7964 | 6.2738 | 7.6025 | 3.7649 | 5.5788 | 0.6773 | 3.8995 | 1.6793 | 35 | within one SE |
| 18 | 20 | 4.4608 | 5.8002 | 6.2751 | 7.6671 | 3.8152 | 5.6037 | 0.6801 | 3.8643 | 1.7394 | 36 | within one SE |

### Full grid — forest (24 configurations)

Best mean reg.sel.log.forest\_reg.max\_depth=18.max\_features=sqrt.min\_samples\_leaf=20 = 5.3541 days (SE 0.6936); one-SE bound 6.0477 days; one-SE choice reg.sel.log.forest\_reg.max\_depth=8.max\_features=sqrt.min\_samples\_leaf=200 = 5.5772 days. Against the plain s06 model: tuned paired gain -0.1338 (paired SE 0.0150), better in 0 of 5 folds; carried: plain (G-55). Grid edge: the one-SE choice sits at the edge of the grid for max\_depth = 8 (lowest value in the grid); min\_samples\_leaf = 200 (highest value in the grid) (the simpler end, where the one-SE rule moves the choice by design).

Effect of each parameter:

| parameter | value | configurations | best validation mean | mean over its configurations |
| --- | --- | --- | --- | --- |
| max\_depth | 10 | 4 | 5.4240 | 5.4761 |
| max\_depth | 12 | 4 | 5.3871 | 5.4524 |
| max\_depth | 14 | 4 | 5.3777 | 5.4478 |
| max\_depth | 16 | 4 | 5.3629 | 5.4396 |
| max\_depth | 18 | 4 | 5.3541 | 5.4362 |
| max\_depth | 8 | 4 | 5.4770 | 5.5169 |
| max\_features | sqrt | 24 | 5.3541 | 5.4615 |
| min\_samples\_leaf | 100 | 6 | 5.4503 | 5.4702 |
| min\_samples\_leaf | 20 | 6 | 5.3541 | 5.3971 |
| min\_samples\_leaf | 200 | 6 | 5.5378 | 5.5486 |
| min\_samples\_leaf | 50 | 6 | 5.4025 | 5.4301 |

Every configuration, ranked (per-fold validation, mean, SE, training mean, gap):

| max\_depth | max\_features | min\_samples\_leaf | val f1 | val f2 | val f3 | val f4 | val f5 | validation\_mean | validation\_se | train\_mean | train\_validation\_gap | rank | flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 18 | sqrt | 20 | 4.0216 | 5.6063 | 6.0962 | 7.4171 | 3.6294 | 5.3541 | 0.6936 | 4.1778 | 1.1763 | 1 | best mean; within one SE |
| 16 | sqrt | 20 | 4.0277 | 5.5937 | 6.0979 | 7.4329 | 3.6622 | 5.3629 | 0.6912 | 4.1988 | 1.1641 | 2 | within one SE |
| 14 | sqrt | 20 | 4.0234 | 5.6124 | 6.1121 | 7.4488 | 3.6915 | 5.3777 | 0.6914 | 4.2257 | 1.1520 | 3 | within one SE |
| 12 | sqrt | 20 | 4.0377 | 5.6012 | 6.1332 | 7.4521 | 3.7114 | 5.3871 | 0.6890 | 4.2677 | 1.1194 | 4 | within one SE |
| 18 | sqrt | 50 | 4.0989 | 5.6540 | 6.1376 | 7.4514 | 3.6708 | 5.4025 | 0.6892 | 4.2776 | 1.1249 | 5 | within one SE |
| 16 | sqrt | 50 | 4.1002 | 5.6408 | 6.1363 | 7.4589 | 3.6856 | 5.4044 | 0.6880 | 4.2859 | 1.1185 | 6 | within one SE |
| 14 | sqrt | 50 | 4.1137 | 5.6437 | 6.1456 | 7.4596 | 3.7066 | 5.4138 | 0.6848 | 4.2995 | 1.1144 | 7 | within one SE |
| 12 | sqrt | 50 | 4.1025 | 5.6395 | 6.1545 | 7.4743 | 3.7310 | 5.4204 | 0.6854 | 4.3217 | 1.0987 | 8 | within one SE |
| 10 | sqrt | 20 | 4.0692 | 5.6276 | 6.1665 | 7.4833 | 3.7735 | 5.4240 | 0.6853 | 4.3175 | 1.1065 | 9 | within one SE |
| 10 | sqrt | 50 | 4.1162 | 5.6428 | 6.1800 | 7.4963 | 3.7815 | 5.4434 | 0.6826 | 4.3597 | 1.0837 | 10 | within one SE |
| 18 | sqrt | 100 | 4.1778 | 5.6745 | 6.1797 | 7.4976 | 3.7217 | 5.4503 | 0.6849 | 4.3612 | 1.0890 | 11 | within one SE |
| 16 | sqrt | 100 | 4.1776 | 5.6793 | 6.1826 | 7.4938 | 3.7217 | 5.4510 | 0.6846 | 4.3646 | 1.0864 | 12 | within one SE |
| 14 | sqrt | 100 | 4.1818 | 5.6801 | 6.1839 | 7.5067 | 3.7445 | 5.4594 | 0.6833 | 4.3716 | 1.0878 | 13 | within one SE |
| 12 | sqrt | 100 | 4.1805 | 5.6607 | 6.1875 | 7.5084 | 3.7632 | 5.4600 | 0.6813 | 4.3839 | 1.0761 | 14 | within one SE |
| 8 | sqrt | 20 | 4.1051 | 5.6482 | 6.2256 | 7.5607 | 3.8455 | 5.4770 | 0.6883 | 4.3929 | 1.0841 | 15 | within one SE |
| 10 | sqrt | 100 | 4.1884 | 5.6784 | 6.2178 | 7.5305 | 3.8022 | 5.4835 | 0.6809 | 4.4047 | 1.0787 | 16 | within one SE |
| 8 | sqrt | 50 | 4.1309 | 5.6837 | 6.2330 | 7.5711 | 3.8617 | 5.4961 | 0.6863 | 4.4144 | 1.0817 | 17 | within one SE |
| 8 | sqrt | 100 | 4.1939 | 5.7012 | 6.2591 | 7.5738 | 3.8581 | 5.5172 | 0.6826 | 4.4480 | 1.0693 | 18 | within one SE |
| 18 | sqrt | 200 | 4.3141 | 5.7534 | 6.2681 | 7.5612 | 3.7923 | 5.5378 | 0.6789 | 4.4556 | 1.0823 | 19 | within one SE |
| 16 | sqrt | 200 | 4.3141 | 5.7531 | 6.2697 | 7.5644 | 3.7996 | 5.5402 | 0.6785 | 4.4568 | 1.0834 | 20 | within one SE |
| 14 | sqrt | 200 | 4.3141 | 5.7533 | 6.2708 | 7.5681 | 3.7961 | 5.5405 | 0.6796 | 4.4580 | 1.0825 | 21 | within one SE |
| 12 | sqrt | 200 | 4.3147 | 5.7521 | 6.2707 | 7.5601 | 3.8136 | 5.5422 | 0.6761 | 4.4629 | 1.0793 | 22 | within one SE |
| 10 | sqrt | 200 | 4.3148 | 5.7558 | 6.2742 | 7.5739 | 3.8495 | 5.5536 | 0.6738 | 4.4754 | 1.0782 | 23 | within one SE |
| 8 | sqrt | 200 | 4.3099 | 5.7596 | 6.2981 | 7.6178 | 3.9004 | 5.5772 | 0.6758 | 4.5009 | 1.0763 | 24 | one-SE choice; within one SE |

Round 2 (accepted) · run `20261021T042137Z` · 6 checks, all PASS. Round 2 differs from round 1 only in the validation-curve figures (dashed training lines now in their series colour); every table and value is unchanged. Coverage and review dropdowns are on the parent tab "s07 Tuning"; comment on any card here.

## 7.1 Linear (regression)

**Approved solution:** Ridge(alpha): 0.01, 0.1, 0.5, 1, 5, 10, 20, 50, 100

**What was done:** linear/logistic: 9 configurations; best mean 5.4620 days ({'alpha': 20.0}); one-SE choice {"alpha": 100.0} with 5.4642 ± 0.6711 days.

**Observation:** Against the plain s06 model (5.4701 days): paired gain of the tuned model +0.0059 days (paired SE 0.0056), better in 4 of 5 folds; carried: plain model. For description only, the best-mean grid point against the plain model: paired gain +0.0081 days (paired SE 0.0035), better in 4 of 5 folds.

**Reasoning:** The tuned configuration replaces the plain s06 model only if it beats it by more than one standard error of the fold means (G-55); otherwise the simpler plain model stays.

**Top 8 configurations by validation MAE, plus the one-SE choice** (grid\_results.csv; 9 configurations (days)):

| params | train\_mean | validation\_mean | validation\_se | train\_validation\_gap | rank | chosen\_in\_family |
| --- | --- | --- | --- | --- | --- | --- |
| {"alpha": 20.0} | 4.2917 | 5.4620 | 0.6728 | 1.1703 | 1 | False |
| {"alpha": 50.0} | 4.2954 | 5.4621 | 0.6720 | 1.1667 | 2 | False |
| {"alpha": 10.0} | 4.2903 | 5.4627 | 0.6731 | 1.1725 | 3 | False |
| {"alpha": 5.0} | 4.2894 | 5.4637 | 0.6731 | 1.1743 | 4 | False |
| {"alpha": 100.0} | 4.3009 | 5.4642 | 0.6711 | 1.1633 | 5 | True |
| {"alpha": 1.0} | 4.2882 | 5.4656 | 0.6729 | 1.1774 | 6 | False |
| {"alpha": 0.5} | 4.2878 | 5.4663 | 0.6728 | 1.1785 | 7 | False |
| {"alpha": 0.1} | 4.2866 | 5.4679 | 0.6729 | 1.1813 | 8 | False |

**Against the plain s06 model** (plain\_vs\_tuned.csv; paired figures are description only):

| plain\_mean | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | paired\_se | tuned\_better\_folds | carried | best\_mean | paired\_gain\_of\_best\_mean | best\_mean\_paired\_se | best\_mean\_better\_folds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5.4701 | 5.4642 | 0.6711 | 0.0059 | 0.0056 | 4 | plain | 5.4620 | 0.0081 | 0.0035 | 4 |

&#91;image: Validation curve, linear/logistic, regression\]

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 9 configurations; single tree 36 configurations; forest 24 configurations)

**Files** (stages/s07\_tuning/regression/outputs/, run 20261021T035843Z): grid\_results.csv

## 7.3 Decision tree

**Approved solution:** max\_depth: 4, 5, 6, 8, 10, 12, 14, 16, 18 (includes the s06 depth 5; G-43); min\_samples\_leaf: 20, 50, 100, 200; classifier also class\_weight: None, balanced

**What was done:** single tree: 36 configurations; best mean 5.3760 days ({'max\_depth': 8, 'min\_samples\_leaf': 200}); one-SE choice {"max\_depth": 4, "min\_samples\_leaf": 200} with 5.4332 ± 0.7125 days.

**Observation:** Against the plain s06 model (5.4244 days): paired gain of the tuned model -0.0088 days (paired SE 0.0359), better in 1 of 5 folds; carried: plain model. For description only, the best-mean grid point against the plain model: paired gain +0.0483 days (paired SE 0.0239), better in 4 of 5 folds.

**Reasoning:** The tuned configuration replaces the plain s06 model only if it beats it by more than one standard error of the fold means (G-55); otherwise the simpler plain model stays.

**Top 8 configurations by validation MAE, plus the one-SE choice** (grid\_results.csv; 36 configurations (days)):

| params | train\_mean | validation\_mean | validation\_se | train\_validation\_gap | rank | chosen\_in\_family |
| --- | --- | --- | --- | --- | --- | --- |
| {"max\_depth": 8, "min\_samples\_leaf": 200} | 4.2917 | 5.3760 | 0.7055 | 1.0843 | 1 | False |
| {"max\_depth": 18, "min\_samples\_leaf": 200} | 4.2607 | 5.3820 | 0.7091 | 1.1213 | 2 | False |
| {"max\_depth": 14, "min\_samples\_leaf": 200} | 4.2613 | 5.3823 | 0.7090 | 1.1211 | 3 | False |
| {"max\_depth": 16, "min\_samples\_leaf": 200} | 4.2608 | 5.3826 | 0.7085 | 1.1218 | 4 | False |
| {"max\_depth": 8, "min\_samples\_leaf": 100} | 4.2564 | 5.3827 | 0.7089 | 1.1263 | 5 | False |
| {"max\_depth": 10, "min\_samples\_leaf": 200} | 4.2744 | 5.3834 | 0.7036 | 1.1090 | 6 | False |
| {"max\_depth": 12, "min\_samples\_leaf": 200} | 4.2652 | 5.3855 | 0.7049 | 1.1204 | 7 | False |
| {"max\_depth": 10, "min\_samples\_leaf": 100} | 4.2192 | 5.3905 | 0.7061 | 1.1713 | 8 | False |
| {"max\_depth": 4, "min\_samples\_leaf": 200} | 4.4140 | 5.4332 | 0.7125 | 1.0192 | 27 | True |

**Against the plain s06 model** (plain\_vs\_tuned.csv; paired figures are description only):

| plain\_mean | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | paired\_se | tuned\_better\_folds | carried | best\_mean | paired\_gain\_of\_best\_mean | best\_mean\_paired\_se | best\_mean\_better\_folds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5.4244 | 5.4332 | 0.7125 | -0.0088 | 0.0359 | 1 | plain | 5.3760 | 0.0483 | 0.0239 | 4 |

&#91;image: Validation curve, single tree, regression\]

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 9 configurations; single tree 36 configurations; forest 24 configurations) **Check** the grid point with the s06 plain settings reproduces the s06 fold scores (tree, forest): PASS (2 of 2 reproduced)

**Files** (stages/s07\_tuning/regression/outputs/, run 20261021T035843Z): grid\_results.csv

## 7.4 Random forest

**Approved solution:** 200 trees; max\_depth: 8, 10, 12, 14, 16, 18; min\_samples\_leaf: 20, 50, 100, 200 (forest grid unchanged by G-43); max\_features: sqrt; classifier also class\_weight: None, balanced

**What was done:** forest: 24 configurations; best mean 5.3541 days ({'max\_depth': 18, 'max\_features': 'sqrt', 'min\_samples\_leaf': 20}); one-SE choice {"max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 200} with 5.5772 ± 0.6758 days.

**Observation:** Against the plain s06 model (5.4434 days): paired gain of the tuned model -0.1338 days (paired SE 0.0150), better in 0 of 5 folds; carried: plain model. For description only, the best-mean grid point against the plain model: paired gain +0.0893 days (paired SE 0.0186), better in 5 of 5 folds.

**Reasoning:** The tuned configuration replaces the plain s06 model only if it beats it by more than one standard error of the fold means (G-55); otherwise the simpler plain model stays.

**Top 8 configurations by validation MAE, plus the one-SE choice** (grid\_results.csv; 24 configurations (days)):

| params | train\_mean | validation\_mean | validation\_se | train\_validation\_gap | rank | chosen\_in\_family |
| --- | --- | --- | --- | --- | --- | --- |
| {"max\_depth": 18, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 4.1778 | 5.3541 | 0.6936 | 1.1763 | 1 | False |
| {"max\_depth": 16, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 4.1988 | 5.3629 | 0.6912 | 1.1641 | 2 | False |
| {"max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 4.2257 | 5.3777 | 0.6914 | 1.1520 | 3 | False |
| {"max\_depth": 12, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 4.2677 | 5.3871 | 0.6890 | 1.1194 | 4 | False |
| {"max\_depth": 18, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 4.2776 | 5.4025 | 0.6892 | 1.1249 | 5 | False |
| {"max\_depth": 16, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 4.2859 | 5.4044 | 0.6880 | 1.1185 | 6 | False |
| {"max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 4.2995 | 5.4138 | 0.6848 | 1.1144 | 7 | False |
| {"max\_depth": 12, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 4.3217 | 5.4204 | 0.6854 | 1.0987 | 8 | False |
| {"max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 4.5009 | 5.5772 | 0.6758 | 1.0763 | 24 | True |

**Against the plain s06 model** (plain\_vs\_tuned.csv; paired figures are description only):

| plain\_mean | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | paired\_se | tuned\_better\_folds | carried | best\_mean | paired\_gain\_of\_best\_mean | best\_mean\_paired\_se | best\_mean\_better\_folds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5.4434 | 5.5772 | 0.6758 | -0.1338 | 0.0150 | 0 | plain | 5.3541 | 0.0893 | 0.0186 | 5 |

&#91;image: Validation curve, forest, regression\]

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 9 configurations; single tree 36 configurations; forest 24 configurations) **Check** the grid point with the s06 plain settings reproduces the s06 fold scores (tree, forest): PASS (2 of 2 reproduced)

**Files** (stages/s07\_tuning/regression/outputs/, run 20261021T035843Z): grid\_results.csv

## 7.5 Search method

**Approved solution:** GridSearchCV over the full Pipeline with cv = the s05 fold iterator, scoring = the primary metric (neg MAE, average precision), refit=False, return\_train\_score=True, seed 42. Best per family = the simplest configuration within one standard error of the best mean (s01 1.7). Simpler means higher alpha, lower C, shallower depth, then larger leaf. It is then compared with the family's plain s06 model by the same one-SE rule: if the plain model's mean is within one SE of the tuned configuration's mean, the plain model is kept (G-55)

**What was done:** GridSearchCV over the whole s04 pipeline on the s05 folds, scoring neg\_mean\_absolute\_error, refit=False, return\_train\_score=True, seed 42; 69 configurations in total. Carried per family: linear/logistic plain s06; single tree plain s06; forest plain s06. Ladder over the carried families (description only; s08 decides): linear/logistic kept over dummy (paired gain +1.0245 days, better in 5 of 5 folds); single tree not kept over linear/logistic (paired gain +0.0458 days, better in 3 of 5 folds); forest not kept over linear/logistic (paired gain +0.0267 days, better in 3 of 5 folds); result linear/logistic.

**Conclusion:** Selection scores on the folds, not generalisation estimates (G-10). The finalists and the final choice are made in s08 at its gate (G-39).

**Plain vs tuned per family** (plain\_vs\_tuned.csv):

| family | plain\_mean | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | tuned\_better\_folds | carried |
| --- | --- | --- | --- | --- | --- | --- |
| linear/logistic | 5.4701 | 5.4642 | 0.6711 | 0.0059 | 4 | plain |
| single tree | 5.4244 | 5.4332 | 0.7125 | -0.0088 | 1 | plain |
| forest | 5.4434 | 5.5772 | 0.6758 | -0.1338 | 0 | plain |

**Ladder over the carried families** (ladder\_preview.csv; description only, s08 chooses):

| comparison | mean\_gain | paired\_se | folds\_better | kept\_by\_one\_se\_rule |
| --- | --- | --- | --- | --- |
| linear/logistic vs dummy | 1.0245 | 0.1262 | 5 | True |
| single tree vs linear/logistic | 0.0458 | 0.0685 | 3 | False |
| forest vs linear/logistic | 0.0267 | 0.0601 | 3 | False |

**Check** same folds as s06 (rows per fold equal): PASS **Check** every configuration scored on all five folds, whole pipeline refitted per fold: PASS **Check** no test row read: every row used was purchased before the test cutoff: PASS (latest purchase 2018-05-27 12:20:21, cutoff 2018-05-27 12:30:34)

**Files** (stages/s07\_tuning/regression/outputs/, run 20261021T035843Z): candidates.csv, counts.json, decision.json, grid\_results.csv, ladder\_preview.csv, plain\_vs\_tuned.csv

## 7.6 Overfitting check

**Approved solution:** For each configuration report the train–validation gap; flag the best configuration if the gap is large and a simpler one is within the decision rule

**What was done:** train\_validation\_gap for every configuration in grid\_results.csv (positive = worse on validation). Gap of each family's one-SE choice: linear/logistic +1.1633 days; single tree +1.0192 days; forest +1.0763 days.

**Reasoning:** The one-SE choice is already the simplest configuration within the rule, so no simpler configuration within the rule exists to flag; the gaps are reported for the review.

**Gap of each family's one-SE choice** (grid\_results.csv):

| family | params | train\_mean | validation\_mean | train\_validation\_gap |
| --- | --- | --- | --- | --- |
| linear | {"alpha": 100.0} | 4.3009 | 5.4642 | 1.1633 |
| tree | {"max\_depth": 4, "min\_samples\_leaf": 200} | 4.4140 | 5.4332 | 1.0192 |
| forest | {"max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 4.5009 | 5.5772 | 1.0763 |

**Files** (stages/s07\_tuning/regression/outputs/, run 20261021T035843Z): curves/validation\_curve\_forest.csv, curves/validation\_curve\_linear.csv, curves/validation\_curve\_tree.csv, figures/validation\_curve\_forest.csv, figures/validation\_curve\_forest.png, figures/validation\_curve\_linear.csv, figures/validation\_curve\_linear.png, figures/validation\_curve\_tree.csv, figures/validation\_curve\_tree.png, grid\_results.csv

## 7.7 Outputs

**Approved solution:** grid\_results.csv (every configuration: parameters, per-fold train and validation scores, mean, SD, rank, fit time, convergence), out-of-fold predictions of each family's best, kept separate as pooled OOF vs mean-fold scores

**What was done:** grid\_results.csv, plain\_vs\_tuned.csv, ladder\_preview.csv, candidates.csv, decision.json, out-of-fold predictions of each family's best (predictions.csv.gz) with pooled vs mean-fold scores (oof\_scores.csv), validation curves (curves/, figures/); fit times in \_manifest.json.

**Out-of-fold scores of each family's one-SE choice, pooled vs mean-fold** (oof\_scores.csv):

| family | mean\_fold\_mae | pooled\_oof\_mae | pooled\_oof\_rmse | pooled\_oof\_r2 |
| --- | --- | --- | --- | --- |
| linear/logistic | 5.4642 | 5.5184 | 9.0018 | 0.0958 |
| single tree | 5.4332 | 5.4922 | 8.9775 | 0.1007 |
| forest | 5.5772 | 5.6331 | 9.1207 | 0.0717 |

**Check** refitting each family's best per fold gives the grid's validation scores: PASS (15 refits)

**Files** (stages/s07\_tuning/regression/outputs/, run 20261021T035843Z): counts.json, oof\_scores.csv, predictions.csv.gz
