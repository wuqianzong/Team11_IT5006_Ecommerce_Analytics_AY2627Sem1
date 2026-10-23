# B7 › regression — evidence cards

Round 1 · ACCEPTED by the experiment lead (tag e5-B-s07-accepted) · run `20261023T163311Z` on code commit e358f81 (clean tree) · 6 checks, all PASS. Coverage and review dropdowns are on the parent tab "B7 Tuning"; comment on any card here.

*Card text is written by A's code, so its stage words refer to B's inputs: "s04 recipe" = B4 recipes\_B.json, "s05 folds" = B5 folds\_B.csv, "s06" = B6, "s08 decides" = B8 decides.*

**Approved solution for every card (B6–B7 blueprint):** B7 = A's s07 on B's inputs: A's grids per family; one-SE choice inside each grid and against the plain B6 model (G-55). Same code, other inputs (no copy).

## B7.1

**What was done:** linear/logistic: 9 configurations; best mean 5.0191 days ({'alpha': 20.0}); one-SE choice {"alpha": 100.0} with 5.0205 ± 0.5946 days.

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 9 configurations; single tree 36 configurations; forest 24 configurations)

**Files** (pipeline\_b/stages/b07/regression/outputs/, run 20261023T163311Z): grid\_results.csv

### B7.1 full grid — linear/logistic (9 configurations)

**How the decision was made** (grid\_results.csv, plain\_vs\_tuned.csv; metric: MAE in days, lower is better):

1. Best mean in the grid: reg.sel.log.ridge.alpha=20 = 5.0191 days (fold SE 0.6056).
2. One-SE bound: 5.0191 + 0.6056 = 5.6247 days. Configurations inside the bound are marked "within one SE".
3. One-SE choice: the simplest configuration inside the bound (protocol order: higher alpha) = reg.sel.log.ridge.alpha=100, 5.0205 days.
4. Against the plain B6 model: plain B6 model reg.sel.log.linear: 5.0247 days; tuned one-SE choice reg.sel.log.ridge.alpha=100: 5.0205 days (SE 0.5946); paired gain of tuned +0.0041 (paired SE 0.0270), better in 3 of 5 folds → carried: **plain** (G-55).

**Grid edge:** the one-SE choice sits at the edge of the pre-registered grid for alpha = 100.0 (highest value in the grid). This is the simpler end of the grid (protocol order: higher alpha, lower C, shallower depth, larger leaf), which is where the one-SE rule moves the choice by design; it means the grid may not extend far enough on that side. A's code reviews grid edges at the B8 gate (grid\_edge\_action in human\_decisions\_B.yaml b08), not here.

**Effect of each parameter** (best and average validation mean over the configurations with that value):

| parameter | value | configurations | best validation mean | mean over its configurations |
| --- | --- | --- | --- | --- |
| alpha | 0.0100 | 1 | 5.0246 | 5.0246 |
| alpha | 0.1000 | 1 | 5.0244 | 5.0244 |
| alpha | 0.5000 | 1 | 5.0235 | 5.0235 |
| alpha | 1.0000 | 1 | 5.0229 | 5.0229 |
| alpha | 5.0000 | 1 | 5.0205 | 5.0205 |
| alpha | 10.0000 | 1 | 5.0195 | 5.0195 |
| alpha | 20.0000 | 1 | 5.0191 | 5.0191 |
| alpha | 50.0000 | 1 | 5.0198 | 5.0198 |
| alpha | 100.0000 | 1 | 5.0205 | 5.0205 |

**Every configuration, ranked** (per-fold validation scores, mean, fold SE, training mean, train–validation gap; positive gap = worse on validation than on the training folds, in both tasks, as in A's s07):

| alpha | val f1 | val f2 | val f3 | val f4 | val f5 | validation\_mean | validation\_se | train\_mean | train\_validation\_gap | rank | convergence\_warnings | flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20.0 | 3.7460 | 5.4485 | 5.5849 | 6.7660 | 3.5499 | 5.0191 | 0.6056 | 3.8663 | 1.1527 | 1 | 0 | best mean; within one SE |
| 10.0 | 3.7318 | 5.4550 | 5.5947 | 6.7680 | 3.5482 | 5.0195 | 0.6083 | 3.8637 | 1.1558 | 2 | 0 | within one SE |
| 50.0 | 3.7801 | 5.4365 | 5.5664 | 6.7628 | 3.5529 | 5.0198 | 0.6000 | 3.8721 | 1.1476 | 3 | 0 | within one SE |
| 5.0 | 3.7249 | 5.4592 | 5.6016 | 6.7696 | 3.5471 | 5.0205 | 0.6099 | 3.8623 | 1.1581 | 4 | 0 | within one SE |
| 100.0 | 3.8134 | 5.4253 | 5.5480 | 6.7603 | 3.5557 | 5.0205 | 0.5946 | 3.8784 | 1.1421 | 5 | 0 | one-SE choice; within one SE |
| 1.0 | 3.7218 | 5.4643 | 5.6100 | 6.7717 | 3.5465 | 5.0229 | 0.6112 | 3.8612 | 1.1617 | 6 | 0 | within one SE |
| 0.5 | 3.7222 | 5.4654 | 5.6116 | 6.7721 | 3.5465 | 5.0235 | 0.6113 | 3.8610 | 1.1626 | 7 | 0 | within one SE |
| 0.1 | 3.7228 | 5.4667 | 5.6132 | 6.7723 | 3.5467 | 5.0244 | 0.6114 | 3.8608 | 1.1636 | 8 | 0 | within one SE |
| 0.01 | 3.7225 | 5.4677 | 5.6139 | 6.7724 | 3.5469 | 5.0246 | 0.6115 | 3.8607 | 1.1640 | 9 | 0 | within one SE |

Source: pipeline\_b/stages/b07/regression/outputs/grid\_results.csv (run 20261023T163311Z); validation curves: figures/validation\_curve\_linear.png and curves/validation\_curve\_linear.csv.

## B7.3

**What was done:** single tree: 36 configurations; best mean 4.9735 days ({'max\_depth': 8, 'min\_samples\_leaf': 100}); one-SE choice {"max\_depth": 4, "min\_samples\_leaf": 200} with 5.0841 ± 0.6443 days.

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 9 configurations; single tree 36 configurations; forest 24 configurations) **Check** the grid point with the s06 plain settings reproduces the s06 fold scores (tree, forest): PASS (2 of 2 reproduced)

**Files** (pipeline\_b/stages/b07/regression/outputs/, run 20261023T163311Z): grid\_results.csv

### B7.3 full grid — single tree (36 configurations)

**How the decision was made** (grid\_results.csv, plain\_vs\_tuned.csv; metric: MAE in days, lower is better):

1. Best mean in the grid: reg.sel.log.tree\_reg.max\_depth=8.min\_samples\_leaf=100 = 4.9735 days (fold SE 0.6603).
2. One-SE bound: 4.9735 + 0.6603 = 5.6338 days. Configurations inside the bound are marked "within one SE".
3. One-SE choice: the simplest configuration inside the bound (protocol order: shallower depth, then larger leaf) = reg.sel.log.tree\_reg.max\_depth=4.min\_samples\_leaf=200, 5.0841 days.
4. Against the plain B6 model: plain B6 model reg.sel.log.tree\_reg.max\_depth=5.min\_samples\_leaf=100: 5.0532 days; tuned one-SE choice reg.sel.log.tree\_reg.max\_depth=4.min\_samples\_leaf=200: 5.0841 days (SE 0.6443); paired gain of tuned -0.0309 (paired SE 0.0269), better in 1 of 5 folds → carried: **plain** (G-55).

**Grid edge:** the one-SE choice sits at the edge of the pre-registered grid for max\_depth = 4 (lowest value in the grid); min\_samples\_leaf = 200 (highest value in the grid). This is the simpler end of the grid (protocol order: higher alpha, lower C, shallower depth, larger leaf), which is where the one-SE rule moves the choice by design; it means the grid may not extend far enough on that side. A's code reviews grid edges at the B8 gate (grid\_edge\_action in human\_decisions\_B.yaml b08), not here.

**Effect of each parameter** (best and average validation mean over the configurations with that value):

| parameter | value | configurations | best validation mean | mean over its configurations |
| --- | --- | --- | --- | --- |
| max\_depth | 4 | 4 | 5.0835 | 5.0848 |
| max\_depth | 5 | 4 | 5.0521 | 5.0559 |
| max\_depth | 6 | 4 | 5.0077 | 5.0148 |
| max\_depth | 8 | 4 | 4.9735 | 4.9814 |
| max\_depth | 10 | 4 | 4.9798 | 5.0118 |
| max\_depth | 12 | 4 | 4.9756 | 5.0301 |
| max\_depth | 14 | 4 | 4.9756 | 5.0395 |
| max\_depth | 16 | 4 | 4.9756 | 5.0453 |
| max\_depth | 18 | 4 | 4.9756 | 5.0466 |
| min\_samples\_leaf | 20 | 9 | 5.0005 | 5.0862 |
| min\_samples\_leaf | 50 | 9 | 4.9762 | 5.0389 |
| min\_samples\_leaf | 100 | 9 | 4.9735 | 5.0109 |
| min\_samples\_leaf | 200 | 9 | 4.9755 | 5.0018 |

**Every configuration, ranked** (per-fold validation scores, mean, fold SE, training mean, train–validation gap; positive gap = worse on validation than on the training folds, in both tasks, as in A's s07):

| max\_depth | min\_samples\_leaf | val f1 | val f2 | val f3 | val f4 | val f5 | validation\_mean | validation\_se | train\_mean | train\_validation\_gap | rank | convergence\_warnings | flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 8 | 100 | 3.6349 | 5.1810 | 5.7167 | 6.9362 | 3.3987 | 4.9735 | 0.6603 | 3.8244 | 1.1491 | 1 | 0 | best mean; within one SE |
| 8 | 200 | 3.5996 | 5.1945 | 5.7559 | 6.9376 | 3.3901 | 4.9755 | 0.6676 | 3.8724 | 1.1032 | 2 | 0 | within one SE |
| 12 | 200 | 3.5958 | 5.1898 | 5.7474 | 6.9030 | 3.4419 | 4.9756 | 0.6562 | 3.8556 | 1.1200 | 3 | 0 | within one SE |
| 18 | 200 | 3.5958 | 5.1898 | 5.7474 | 6.9031 | 3.4419 | 4.9756 | 0.6562 | 3.8556 | 1.1200 | 4 | 0 | within one SE |
| 16 | 200 | 3.5958 | 5.1898 | 5.7474 | 6.9031 | 3.4419 | 4.9756 | 0.6562 | 3.8556 | 1.1200 | 4 | 0 | within one SE |
| 14 | 200 | 3.5958 | 5.1898 | 5.7474 | 6.9031 | 3.4419 | 4.9756 | 0.6562 | 3.8556 | 1.1200 | 4 | 0 | within one SE |
| 8 | 50 | 3.6611 | 5.1687 | 5.7161 | 6.9477 | 3.3873 | 4.9762 | 0.6605 | 3.7885 | 1.1876 | 7 | 0 | within one SE |
| 10 | 200 | 3.5958 | 5.1898 | 5.7486 | 6.9213 | 3.4437 | 4.9798 | 0.6588 | 3.8592 | 1.1207 | 8 | 0 | within one SE |
| 14 | 100 | 3.6298 | 5.2040 | 5.7372 | 6.9092 | 3.4854 | 4.9931 | 0.6481 | 3.7720 | 1.2212 | 9 | 0 | within one SE |
| 18 | 100 | 3.6298 | 5.2040 | 5.7389 | 6.9092 | 3.4854 | 4.9935 | 0.6482 | 3.7709 | 1.2226 | 10 | 0 | within one SE |
| 16 | 100 | 3.6298 | 5.2040 | 5.7389 | 6.9110 | 3.4854 | 4.9938 | 0.6485 | 3.7710 | 1.2229 | 11 | 0 | within one SE |
| 10 | 100 | 3.6298 | 5.2023 | 5.7375 | 6.9366 | 3.4681 | 4.9949 | 0.6542 | 3.7894 | 1.2055 | 12 | 0 | within one SE |
| 12 | 100 | 3.6298 | 5.2040 | 5.7396 | 6.9301 | 3.4771 | 4.9961 | 0.6523 | 3.7753 | 1.2208 | 13 | 0 | within one SE |
| 8 | 20 | 3.7203 | 5.2132 | 5.7119 | 6.9679 | 3.3892 | 5.0005 | 0.6579 | 3.7492 | 1.2513 | 14 | 0 | within one SE |
| 6 | 50 | 3.6560 | 5.1209 | 5.7530 | 6.9932 | 3.5153 | 5.0077 | 0.6544 | 3.8826 | 1.1251 | 15 | 0 | within one SE |
| 6 | 200 | 3.6035 | 5.1866 | 5.7639 | 7.0020 | 3.5264 | 5.0165 | 0.6613 | 3.9177 | 1.0987 | 16 | 0 | within one SE |
| 6 | 100 | 3.6293 | 5.1710 | 5.7601 | 6.9993 | 3.5244 | 5.0168 | 0.6580 | 3.8974 | 1.1194 | 17 | 0 | within one SE |
| 6 | 20 | 3.6954 | 5.1244 | 5.7617 | 6.9991 | 3.5103 | 5.0182 | 0.6524 | 3.8751 | 1.1431 | 18 | 0 | within one SE |
| 10 | 50 | 3.6724 | 5.2325 | 5.7610 | 6.9529 | 3.4803 | 5.0198 | 0.6526 | 3.7179 | 1.3019 | 19 | 0 | within one SE |
| 12 | 50 | 3.6756 | 5.2546 | 5.7818 | 6.9809 | 3.5371 | 5.0460 | 0.6513 | 3.6821 | 1.3639 | 20 | 0 | within one SE |
| 16 | 50 | 3.6756 | 5.2512 | 5.7925 | 6.9560 | 3.5701 | 5.0491 | 0.6443 | 3.6620 | 1.3871 | 21 | 0 | within one SE |
| 14 | 50 | 3.6756 | 5.2512 | 5.7921 | 6.9757 | 3.5593 | 5.0508 | 0.6485 | 3.6663 | 1.3845 | 22 | 0 | within one SE |
| 18 | 50 | 3.6756 | 5.2512 | 5.7958 | 6.9632 | 3.5732 | 5.0518 | 0.6453 | 3.6607 | 1.3911 | 23 | 0 | within one SE |
| 5 | 20 | 3.6559 | 5.1306 | 5.7954 | 7.0127 | 3.6659 | 5.0521 | 0.6432 | 3.9439 | 1.1083 | 24 | 0 | within one SE |
| 10 | 20 | 3.7564 | 5.2520 | 5.7795 | 7.0035 | 3.4725 | 5.0528 | 0.6539 | 3.6286 | 1.4242 | 25 | 0 | within one SE |
| 5 | 100 | 3.6808 | 5.1292 | 5.7792 | 7.0115 | 3.6654 | 5.0532 | 0.6394 | 3.9489 | 1.1043 | 26 | 0 | = plain B6 setting; within one SE |
| 5 | 200 | 3.6650 | 5.1394 | 5.8021 | 7.0177 | 3.6635 | 5.0575 | 0.6437 | 3.9619 | 1.0956 | 27 | 0 | within one SE |
| 5 | 50 | 3.6994 | 5.1288 | 5.7959 | 7.0127 | 3.6672 | 5.0608 | 0.6384 | 3.9444 | 1.1164 | 28 | 0 | within one SE |
| 4 | 100 | 3.6338 | 5.1450 | 5.8379 | 7.0408 | 3.7599 | 5.0835 | 0.6426 | 4.0181 | 1.0654 | 29 | 0 | within one SE |
| 4 | 20 | 3.6316 | 5.1473 | 5.8379 | 7.0408 | 3.7599 | 5.0835 | 0.6428 | 4.0182 | 1.0653 | 30 | 0 | within one SE |
| 4 | 200 | 3.6202 | 5.1483 | 5.8477 | 7.0408 | 3.7634 | 5.0841 | 0.6443 | 4.0233 | 1.0608 | 31 | 0 | one-SE choice; within one SE |
| 4 | 50 | 3.6544 | 5.1473 | 5.8379 | 7.0408 | 3.7599 | 5.0881 | 0.6403 | 4.0162 | 1.0719 | 32 | 0 | within one SE |
| 12 | 20 | 3.7928 | 5.2693 | 5.8249 | 7.0288 | 3.5973 | 5.1026 | 0.6419 | 3.5288 | 1.5738 | 33 | 0 | within one SE |
| 14 | 20 | 3.7881 | 5.2969 | 5.8796 | 7.0272 | 3.7007 | 5.1385 | 0.6337 | 3.4601 | 1.6784 | 34 | 0 | within one SE |
| 16 | 20 | 3.8023 | 5.3179 | 5.9037 | 7.0274 | 3.7614 | 5.1625 | 0.6271 | 3.4220 | 1.7405 | 35 | 0 | within one SE |
| 18 | 20 | 3.8036 | 5.3252 | 5.9054 | 7.0237 | 3.7692 | 5.1654 | 0.6257 | 3.4062 | 1.7592 | 36 | 0 | within one SE |

Source: pipeline\_b/stages/b07/regression/outputs/grid\_results.csv (run 20261023T163311Z); validation curves: figures/validation\_curve\_tree.png and curves/validation\_curve\_tree.csv.

## B7.4

**What was done:** forest: 24 configurations; best mean 4.8867 days ({'max\_depth': 18, 'max\_features': 'sqrt', 'min\_samples\_leaf': 20}); one-SE choice {"max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 200} with 5.0821 ± 0.6490 days.

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 9 configurations; single tree 36 configurations; forest 24 configurations) **Check** the grid point with the s06 plain settings reproduces the s06 fold scores (tree, forest): PASS (2 of 2 reproduced)

**Files** (pipeline\_b/stages/b07/regression/outputs/, run 20261023T163311Z): grid\_results.csv

### B7.4 full grid — forest (24 configurations)

**How the decision was made** (grid\_results.csv, plain\_vs\_tuned.csv; metric: MAE in days, lower is better):

1. Best mean in the grid: reg.sel.log.forest\_reg.max\_depth=18.max\_features=sqrt.min\_samples\_leaf=20 = 4.8867 days (fold SE 0.6462).
2. One-SE bound: 4.8867 + 0.6462 = 5.5330 days. Configurations inside the bound are marked "within one SE".
3. One-SE choice: the simplest configuration inside the bound (protocol order: shallower depth, then larger leaf) = reg.sel.log.forest\_reg.max\_depth=8.max\_features=sqrt.min\_samples\_leaf=200, 5.0821 days.
4. Against the plain B6 model: plain B6 model reg.sel.log.forest\_reg.max\_depth=10.max\_features=sqrt.min\_samples\_leaf=50: 4.9627 days; tuned one-SE choice reg.sel.log.forest\_reg.max\_depth=8.max\_features=sqrt.min\_samples\_leaf=200: 5.0821 days (SE 0.6490); paired gain of tuned -0.1193 (paired SE 0.0260), better in 0 of 5 folds → carried: **plain** (G-55).

**Grid edge:** the one-SE choice sits at the edge of the pre-registered grid for max\_depth = 8 (lowest value in the grid); min\_samples\_leaf = 200 (highest value in the grid). This is the simpler end of the grid (protocol order: higher alpha, lower C, shallower depth, larger leaf), which is where the one-SE rule moves the choice by design; it means the grid may not extend far enough on that side. A's code reviews grid edges at the B8 gate (grid\_edge\_action in human\_decisions\_B.yaml b08), not here.

**Effect of each parameter** (best and average validation mean over the configurations with that value):

| parameter | value | configurations | best validation mean | mean over its configurations |
| --- | --- | --- | --- | --- |
| max\_depth | 8 | 4 | 4.9728 | 5.0156 |
| max\_depth | 10 | 4 | 4.9352 | 4.9931 |
| max\_depth | 12 | 4 | 4.9087 | 4.9759 |
| max\_depth | 14 | 4 | 4.8940 | 4.9713 |
| max\_depth | 16 | 4 | 4.8890 | 4.9684 |
| max\_depth | 18 | 4 | 4.8867 | 4.9679 |
| max\_features | sqrt | 24 | 4.8867 | 4.9820 |
| min\_samples\_leaf | 20 | 6 | 4.8867 | 4.9144 |
| min\_samples\_leaf | 50 | 6 | 4.9318 | 4.9473 |
| min\_samples\_leaf | 100 | 6 | 4.9866 | 4.9962 |
| min\_samples\_leaf | 200 | 6 | 5.0654 | 5.0702 |

**Every configuration, ranked** (per-fold validation scores, mean, fold SE, training mean, train–validation gap; positive gap = worse on validation than on the training folds, in both tasks, as in A's s07):

| max\_depth | max\_features | min\_samples\_leaf | val f1 | val f2 | val f3 | val f4 | val f5 | validation\_mean | validation\_se | train\_mean | train\_validation\_gap | rank | convergence\_warnings | flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 18 | sqrt | 20 | 3.5173 | 5.1347 | 5.6183 | 6.7853 | 3.3781 | 4.8867 | 0.6462 | 3.7301 | 1.1566 | 1 | 0 | best mean; within one SE |
| 16 | sqrt | 20 | 3.5176 | 5.1410 | 5.6202 | 6.7842 | 3.3818 | 4.8890 | 0.6458 | 3.7442 | 1.1448 | 2 | 0 | within one SE |
| 14 | sqrt | 20 | 3.5142 | 5.1426 | 5.6233 | 6.7934 | 3.3966 | 4.8940 | 0.6460 | 3.7658 | 1.1282 | 3 | 0 | within one SE |
| 12 | sqrt | 20 | 3.5225 | 5.1565 | 5.6496 | 6.8164 | 3.3987 | 4.9087 | 0.6501 | 3.7998 | 1.1089 | 4 | 0 | within one SE |
| 14 | sqrt | 50 | 3.5693 | 5.1791 | 5.6705 | 6.8167 | 3.4235 | 4.9318 | 0.6439 | 3.8730 | 1.0589 | 5 | 0 | within one SE |
| 18 | sqrt | 50 | 3.5648 | 5.1824 | 5.6628 | 6.8216 | 3.4281 | 4.9319 | 0.6441 | 3.8624 | 1.0695 | 6 | 0 | within one SE |
| 16 | sqrt | 50 | 3.5665 | 5.1803 | 5.6649 | 6.8229 | 3.4293 | 4.9328 | 0.6441 | 3.8656 | 1.0671 | 7 | 0 | within one SE |
| 10 | sqrt | 20 | 3.5351 | 5.1727 | 5.6694 | 6.8537 | 3.4449 | 4.9352 | 0.6503 | 3.8509 | 1.0843 | 8 | 0 | within one SE |
| 12 | sqrt | 50 | 3.5712 | 5.1766 | 5.6713 | 6.8367 | 3.4371 | 4.9386 | 0.6450 | 3.8851 | 1.0535 | 9 | 0 | within one SE |
| 10 | sqrt | 50 | 3.5846 | 5.2012 | 5.6926 | 6.8655 | 3.4698 | 4.9627 | 0.6457 | 3.9108 | 1.0520 | 10 | 0 | = plain B6 setting; within one SE |
| 8 | sqrt | 20 | 3.5512 | 5.2184 | 5.7222 | 6.8973 | 3.4748 | 4.9728 | 0.6554 | 3.9189 | 1.0539 | 11 | 0 | within one SE |
| 8 | sqrt | 50 | 3.5898 | 5.2128 | 5.7311 | 6.9083 | 3.4863 | 4.9857 | 0.6519 | 3.9528 | 1.0329 | 12 | 0 | within one SE |
| 16 | sqrt | 100 | 3.6655 | 5.2238 | 5.7210 | 6.8636 | 3.4590 | 4.9866 | 0.6402 | 3.9497 | 1.0368 | 13 | 0 | within one SE |
| 18 | sqrt | 100 | 3.6655 | 5.2221 | 5.7207 | 6.8657 | 3.4605 | 4.9869 | 0.6403 | 3.9492 | 1.0377 | 14 | 0 | within one SE |
| 12 | sqrt | 100 | 3.6639 | 5.2203 | 5.7231 | 6.8697 | 3.4615 | 4.9877 | 0.6410 | 3.9576 | 1.0302 | 15 | 0 | within one SE |
| 14 | sqrt | 100 | 3.6654 | 5.2313 | 5.7277 | 6.8664 | 3.4685 | 4.9919 | 0.6400 | 3.9524 | 1.0395 | 16 | 0 | within one SE |
| 10 | sqrt | 100 | 3.6649 | 5.2274 | 5.7413 | 6.8917 | 3.4875 | 5.0026 | 0.6423 | 3.9696 | 1.0330 | 17 | 0 | within one SE |
| 8 | sqrt | 100 | 3.6743 | 5.2469 | 5.7606 | 6.9342 | 3.4926 | 5.0217 | 0.6484 | 3.9942 | 1.0275 | 18 | 0 | within one SE |
| 16 | sqrt | 200 | 3.7766 | 5.2799 | 5.8218 | 6.9469 | 3.5020 | 5.0654 | 0.6428 | 4.0308 | 1.0347 | 19 | 0 | within one SE |
| 18 | sqrt | 200 | 3.7766 | 5.2799 | 5.8225 | 6.9484 | 3.5019 | 5.0659 | 0.6431 | 4.0309 | 1.0350 | 20 | 0 | within one SE |
| 14 | sqrt | 200 | 3.7766 | 5.2798 | 5.8227 | 6.9521 | 3.5069 | 5.0676 | 0.6430 | 4.0316 | 1.0360 | 21 | 0 | within one SE |
| 12 | sqrt | 200 | 3.7766 | 5.2779 | 5.8268 | 6.9531 | 3.5086 | 5.0686 | 0.6431 | 4.0325 | 1.0361 | 22 | 0 | within one SE |
| 10 | sqrt | 200 | 3.7766 | 5.2814 | 5.8296 | 6.9609 | 3.5108 | 5.0719 | 0.6443 | 4.0380 | 1.0339 | 23 | 0 | within one SE |
| 8 | sqrt | 200 | 3.7772 | 5.2871 | 5.8457 | 6.9877 | 3.5125 | 5.0821 | 0.6490 | 4.0500 | 1.0320 | 24 | 0 | one-SE choice; within one SE |

Source: pipeline\_b/stages/b07/regression/outputs/grid\_results.csv (run 20261023T163311Z); validation curves: figures/validation\_curve\_forest.png and curves/validation\_curve\_forest.csv.

## B7.5

**What was done:** GridSearchCV over the whole s04 pipeline on the s05 folds, scoring neg\_mean\_absolute\_error, refit=False, return\_train\_score=True, seed 42; 69 configurations in total. Carried per family: linear/logistic plain s06; single tree plain s06; forest plain s06. Ladder over the carried families (description only; s08 decides): linear/logistic kept over dummy (paired gain +0.9442 days, better in 5 of 5 folds); single tree not kept over linear/logistic (paired gain -0.0285 days, better in 2 of 5 folds); forest not kept over linear/logistic (paired gain +0.0619 days, better in 3 of 5 folds); result linear/logistic.

**Plain B6 model against the family's tuned one-SE choice** (plain\_vs\_tuned.csv):

| family | plain\_mean | tuned\_best | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | paired\_se | tuned\_better\_folds | carried |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear/logistic | 5.0247 | reg.sel.log.ridge.alpha=100 | 5.0205 | 0.5946 | 0.0041 | 0.0270 | 3 | plain |
| single tree | 5.0532 | reg.sel.log.tree\_reg.max\_depth=4.min\_samples\_leaf=200 | 5.0841 | 0.6443 | -0.0309 | 0.0269 | 1 | plain |
| forest | 4.9627 | reg.sel.log.forest\_reg.max\_depth=8.max\_features=sqrt.min\_samples\_leaf=200 | 5.0821 | 0.6490 | -0.1193 | 0.0260 | 0 | plain |

**Check** same folds as s06 (rows per fold equal): PASS **Check** every configuration scored on all five folds, whole pipeline refitted per fold: PASS **Check** no test row read: every row used was purchased before the test cutoff: PASS (latest purchase 2018-05-24 18:56:59, cutoff 2018-05-27 12:30:34)

**Files** (pipeline\_b/stages/b07/regression/outputs/, run 20261023T163311Z): candidates.csv, counts.json, decision.json, grid\_results.csv, ladder\_preview.csv, plain\_vs\_tuned.csv

## B7.6

**What was done:** train\_validation\_gap for every configuration in grid\_results.csv (positive = worse on validation). Gap of each family's one-SE choice: linear/logistic +1.1421 days; single tree +1.0608 days; forest +1.0320 days.

**Files** (pipeline\_b/stages/b07/regression/outputs/, run 20261023T163311Z): grid\_results.csv; plus 12 figure/curve files

## B7.7

**What was done:** grid\_results.csv, plain\_vs\_tuned.csv, ladder\_preview.csv, candidates.csv, decision.json, out-of-fold predictions of each family's best (predictions.csv.gz) with pooled vs mean-fold scores (oof\_scores.csv), validation curves (curves/, figures/); fit times in \_manifest.json.

**Check** refitting each family's best per fold gives the grid's validation scores: PASS (15 refits)

**Files** (pipeline\_b/stages/b07/regression/outputs/, run 20261023T163311Z): counts.json, oof\_scores.csv, predictions.csv.gz
