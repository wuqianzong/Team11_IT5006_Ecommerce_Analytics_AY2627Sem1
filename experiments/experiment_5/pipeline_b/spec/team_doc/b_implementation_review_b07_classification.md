# B7 › classification — evidence cards

Round 1 · ACCEPTED by the experiment lead (tag e5-B-s07-accepted) · run `20261023T164241Z` on code commit e358f81 (clean tree) · 6 checks, all PASS. Coverage and review dropdowns are on the parent tab "B7 Tuning"; comment on any card here.

*Card text is written by A's code, so its stage words refer to B's inputs: "s04 recipe" = B4 recipes\_B.json, "s05 folds" = B5 folds\_B.csv, "s06" = B6, "s08 decides" = B8 decides.*

**Approved solution for every card (B6–B7 blueprint):** B7 = A's s07 on B's inputs: A's grids per family; one-SE choice inside each grid and against the plain B6 model (G-55). Same code, other inputs (no copy).

## B7.2

**What was done:** linear/logistic: 18 configurations; best mean 0.2734 ({'C': 0.01, 'class\_weight': None}); one-SE choice {"C": 0.01, "class\_weight": null} with 0.2734 ± 0.0318.

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 18 configurations; single tree 72 configurations; forest 48 configurations)

**Files** (pipeline\_b/stages/b07/classification/outputs/, run 20261023T164241Z): grid\_results.csv

### B7.2 full grid — linear/logistic (18 configurations)

**How the decision was made** (grid\_results.csv, plain\_vs\_tuned.csv; metric: average precision, higher is better):

1. Best mean in the grid: clf.sel.log.logistic.C=0.01.class\_weight=none = 0.2734 (fold SE 0.0318).
2. One-SE bound: 0.2734 − 0.0318 = 0.2416. Configurations inside the bound are marked "within one SE".
3. One-SE choice: the simplest configuration inside the bound (protocol order: lower C) = clf.sel.log.logistic.C=0.01.class\_weight=none, 0.2734.
4. Against the plain B6 model: plain B6 model clf.sel.log.logistic: 0.2616; tuned one-SE choice clf.sel.log.logistic.C=0.01.class\_weight=none: 0.2734 (SE 0.0318); paired gain of tuned +0.0118 (paired SE 0.0051), better in 4 of 5 folds → carried: **plain** (G-55).

**Grid edge:** the one-SE choice sits at the edge of the pre-registered grid for C = 0.01 (lowest value in the grid). This is the simpler end of the grid (protocol order: higher alpha, lower C, shallower depth, larger leaf), which is where the one-SE rule moves the choice by design; it means the grid may not extend far enough on that side. A's code reviews grid edges at the B8 gate (grid\_edge\_action in human\_decisions\_B.yaml b08), not here.

**Effect of each parameter** (best and average validation mean over the configurations with that value):

| parameter | value | configurations | best validation mean | mean over its configurations |
| --- | --- | --- | --- | --- |
| C | 0.01 | 2 | 0.2734 | 0.2727 |
| C | 0.1 | 2 | 0.2717 | 0.2708 |
| C | 0.5 | 2 | 0.2692 | 0.2682 |
| C | 1.0 | 2 | 0.2678 | 0.2668 |
| C | 5.0 | 2 | 0.2646 | 0.2639 |
| C | 10.0 | 2 | 0.2633 | 0.2627 |
| C | 20.0 | 2 | 0.2626 | 0.2622 |
| C | 50.0 | 2 | 0.2616 | 0.2616 |
| C | 100.0 | 2 | 0.2616 | 0.2609 |
| class\_weight | balanced | 9 | 0.2721 | 0.2649 |
| class\_weight | none | 9 | 0.2734 | 0.2662 |

**Every configuration, ranked** (per-fold validation scores, mean, fold SE, training mean, train–validation gap; positive gap = worse on validation than on the training folds, in both tasks, as in A's s07):

| C | class\_weight | val f1 | val f2 | val f3 | val f4 | val f5 | validation\_mean | validation\_se | train\_mean | train\_validation\_gap | rank | convergence\_warnings | flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.01 | none | 0.1821 | 0.2939 | 0.2888 | 0.3706 | 0.2315 | 0.2734 | 0.0318 | 0.2271 | -0.0463 | 1 | 0 | best mean; one-SE choice; within one SE |
| 0.01 | balanced | 0.1801 | 0.2947 | 0.2845 | 0.3705 | 0.2306 | 0.2721 | 0.0320 | 0.2265 | -0.0456 | 2 | 0 | within one SE |
| 0.1 | none | 0.1733 | 0.2943 | 0.2863 | 0.3734 | 0.2310 | 0.2717 | 0.0335 | 0.2328 | -0.0388 | 3 | 0 | within one SE |
| 0.1 | balanced | 0.1743 | 0.2919 | 0.2817 | 0.3717 | 0.2301 | 0.2699 | 0.0330 | 0.2304 | -0.0396 | 4 | 0 | within one SE |
| 0.5 | none | 0.1688 | 0.2908 | 0.2829 | 0.3729 | 0.2307 | 0.2692 | 0.0339 | 0.2353 | -0.0339 | 5 | 0 | within one SE |
| 1.0 | none | 0.1677 | 0.2875 | 0.2813 | 0.3724 | 0.2302 | 0.2678 | 0.0339 | 0.2357 | -0.0321 | 6 | 0 | within one SE |
| 0.5 | balanced | 0.1717 | 0.2858 | 0.2778 | 0.3707 | 0.2296 | 0.2671 | 0.0329 | 0.2312 | -0.0359 | 7 | 0 | within one SE |
| 1.0 | balanced | 0.1702 | 0.2829 | 0.2763 | 0.3702 | 0.2293 | 0.2658 | 0.0330 | 0.2313 | -0.0345 | 8 | 0 | within one SE |
| 5.0 | none | 0.1633 | 0.2813 | 0.2764 | 0.3718 | 0.2303 | 0.2646 | 0.0342 | 0.2366 | -0.0280 | 9 | 0 | within one SE |
| 10.0 | none | 0.1601 | 0.2779 | 0.2765 | 0.3716 | 0.2302 | 0.2633 | 0.0345 | 0.2370 | -0.0262 | 10 | 0 | within one SE |
| 5.0 | balanced | 0.1666 | 0.2771 | 0.2734 | 0.3697 | 0.2287 | 0.2631 | 0.0333 | 0.2316 | -0.0315 | 11 | 0 | within one SE |
| 20.0 | none | 0.1598 | 0.2759 | 0.2754 | 0.3711 | 0.2305 | 0.2626 | 0.0344 | 0.2370 | -0.0256 | 12 | 0 | within one SE |
| 10.0 | balanced | 0.1650 | 0.2753 | 0.2724 | 0.3693 | 0.2287 | 0.2621 | 0.0334 | 0.2317 | -0.0304 | 13 | 0 | within one SE |
| 20.0 | balanced | 0.1642 | 0.2732 | 0.2730 | 0.3697 | 0.2291 | 0.2618 | 0.0335 | 0.2318 | -0.0300 | 14 | 0 | within one SE |
| 100.0 | none | 0.1566 | 0.2754 | 0.2752 | 0.3707 | 0.2301 | 0.2616 | 0.0349 | 0.2370 | -0.0246 | 15 | 0 | within one SE |
| 50.0 | balanced | 0.1631 | 0.2738 | 0.2726 | 0.3697 | 0.2287 | 0.2616 | 0.0337 | 0.2319 | -0.0297 | 16 | 0 | within one SE |
| 50.0 | none | 0.1572 | 0.2740 | 0.2746 | 0.3716 | 0.2303 | 0.2616 | 0.0349 | 0.2371 | -0.0244 | 17 | 0 | within one SE |
| 100.0 | balanced | 0.1580 | 0.2724 | 0.2729 | 0.3694 | 0.2283 | 0.2602 | 0.0344 | 0.2319 | -0.0283 | 18 | 0 | within one SE |

Source: pipeline\_b/stages/b07/classification/outputs/grid\_results.csv (run 20261023T164241Z); validation curves: figures/validation\_curve\_linear.png and curves/validation\_curve\_linear.csv.

## B7.3

**What was done:** single tree: 72 configurations; best mean 0.2394 ({'class\_weight': None, 'max\_depth': 5, 'min\_samples\_leaf': 100}); one-SE choice {"class\_weight": null, "max\_depth": 4, "min\_samples\_leaf": 200} with 0.2298 ± 0.0297.

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 18 configurations; single tree 72 configurations; forest 48 configurations) **Check** the grid point with the s06 plain settings reproduces the s06 fold scores (tree, forest): PASS (2 of 2 reproduced)

**Files** (pipeline\_b/stages/b07/classification/outputs/, run 20261023T164241Z): grid\_results.csv

### B7.3 full grid — single tree (72 configurations)

**How the decision was made** (grid\_results.csv, plain\_vs\_tuned.csv; metric: average precision, higher is better):

1. Best mean in the grid: clf.sel.log.tree\_clf.class\_weight=none.max\_depth=5.min\_samples\_leaf=100 = 0.2394 (fold SE 0.0354).
2. One-SE bound: 0.2394 − 0.0354 = 0.2040. Configurations inside the bound are marked "within one SE".
3. One-SE choice: the simplest configuration inside the bound (protocol order: shallower depth, then larger leaf) = clf.sel.log.tree\_clf.class\_weight=none.max\_depth=4.min\_samples\_leaf=200, 0.2298.
4. Against the plain B6 model: plain B6 model clf.sel.log.tree\_clf.max\_depth=5.min\_samples\_leaf=100: 0.2394; tuned one-SE choice clf.sel.log.tree\_clf.class\_weight=none.max\_depth=4.min\_samples\_leaf=200: 0.2298 (SE 0.0297); paired gain of tuned -0.0096 (paired SE 0.0076), better in 1 of 5 folds → carried: **plain** (G-55).

**Grid edge:** the one-SE choice sits at the edge of the pre-registered grid for max\_depth = 4 (lowest value in the grid); min\_samples\_leaf = 200 (highest value in the grid). This is the simpler end of the grid (protocol order: higher alpha, lower C, shallower depth, larger leaf), which is where the one-SE rule moves the choice by design; it means the grid may not extend far enough on that side. A's code reviews grid edges at the B8 gate (grid\_edge\_action in human\_decisions\_B.yaml b08), not here.

**Effect of each parameter** (best and average validation mean over the configurations with that value):

| parameter | value | configurations | best validation mean | mean over its configurations |
| --- | --- | --- | --- | --- |
| class\_weight | balanced | 36 | 0.2304 | 0.2186 |
| class\_weight | none | 36 | 0.2394 | 0.2245 |
| max\_depth | 4 | 8 | 0.2298 | 0.2255 |
| max\_depth | 5 | 8 | 0.2394 | 0.2324 |
| max\_depth | 6 | 8 | 0.2293 | 0.2253 |
| max\_depth | 8 | 8 | 0.2323 | 0.2241 |
| max\_depth | 10 | 8 | 0.2345 | 0.2211 |
| max\_depth | 12 | 8 | 0.2325 | 0.2192 |
| max\_depth | 14 | 8 | 0.2294 | 0.2159 |
| max\_depth | 16 | 8 | 0.2327 | 0.2155 |
| max\_depth | 18 | 8 | 0.2327 | 0.2151 |
| min\_samples\_leaf | 20 | 18 | 0.2386 | 0.2097 |
| min\_samples\_leaf | 50 | 18 | 0.2379 | 0.2198 |
| min\_samples\_leaf | 100 | 18 | 0.2394 | 0.2269 |
| min\_samples\_leaf | 200 | 18 | 0.2387 | 0.2299 |

**Every configuration, ranked** (per-fold validation scores, mean, fold SE, training mean, train–validation gap; positive gap = worse on validation than on the training folds, in both tasks, as in A's s07):

| class\_weight | max\_depth | min\_samples\_leaf | val f1 | val f2 | val f3 | val f4 | val f5 | validation\_mean | validation\_se | train\_mean | train\_validation\_gap | rank | convergence\_warnings | flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| none | 5 | 100 | 0.1430 | 0.2338 | 0.2599 | 0.3575 | 0.2028 | 0.2394 | 0.0354 | 0.2195 | -0.0199 | 1 | 0 | best mean; within one SE |
| none | 5 | 200 | 0.1398 | 0.2393 | 0.2648 | 0.3503 | 0.1991 | 0.2387 | 0.0350 | 0.2112 | -0.0275 | 2 | 0 | within one SE |
| none | 5 | 20 | 0.1491 | 0.2334 | 0.2590 | 0.3559 | 0.1955 | 0.2386 | 0.0347 | 0.2310 | -0.0076 | 3 | 0 | within one SE |
| none | 5 | 50 | 0.1374 | 0.2381 | 0.2598 | 0.3586 | 0.1954 | 0.2379 | 0.0367 | 0.2227 | -0.0152 | 4 | 0 | within one SE |
| none | 10 | 200 | 0.1387 | 0.2491 | 0.2586 | 0.3112 | 0.2146 | 0.2345 | 0.0285 | 0.2379 | 0.0035 | 5 | 0 | within one SE |
| none | 10 | 100 | 0.1438 | 0.2447 | 0.2543 | 0.3224 | 0.2013 | 0.2333 | 0.0296 | 0.2622 | 0.0289 | 6 | 0 | within one SE |
| none | 16 | 200 | 0.1384 | 0.2476 | 0.2570 | 0.3088 | 0.2119 | 0.2327 | 0.0282 | 0.2431 | 0.0104 | 7 | 0 | within one SE |
| none | 18 | 200 | 0.1384 | 0.2476 | 0.2569 | 0.3089 | 0.2117 | 0.2327 | 0.0282 | 0.2433 | 0.0106 | 8 | 0 | within one SE |
| none | 12 | 100 | 0.1417 | 0.2413 | 0.2563 | 0.3196 | 0.2034 | 0.2325 | 0.0294 | 0.2696 | 0.0371 | 9 | 0 | within one SE |
| none | 8 | 200 | 0.1380 | 0.2479 | 0.2591 | 0.3044 | 0.2122 | 0.2323 | 0.0278 | 0.2313 | -0.0010 | 10 | 0 | within one SE |
| balanced | 8 | 200 | 0.1393 | 0.2320 | 0.2608 | 0.3135 | 0.2062 | 0.2304 | 0.0289 | 0.2333 | 0.0030 | 11 | 0 | within one SE |
| balanced | 12 | 200 | 0.1396 | 0.2305 | 0.2590 | 0.3146 | 0.2060 | 0.2299 | 0.0289 | 0.2413 | 0.0114 | 12 | 0 | within one SE |
| none | 4 | 200 | 0.1394 | 0.2345 | 0.2576 | 0.3177 | 0.1996 | 0.2298 | 0.0297 | 0.1994 | -0.0304 | 13 | 0 | one-SE choice; within one SE |
| none | 12 | 200 | 0.1384 | 0.2480 | 0.2572 | 0.3096 | 0.1953 | 0.2297 | 0.0291 | 0.2415 | 0.0118 | 14 | 0 | within one SE |
| none | 14 | 200 | 0.1384 | 0.2476 | 0.2569 | 0.3095 | 0.1945 | 0.2294 | 0.0292 | 0.2427 | 0.0133 | 15 | 0 | within one SE |
| balanced | 6 | 200 | 0.1407 | 0.2280 | 0.2584 | 0.3124 | 0.2068 | 0.2293 | 0.0284 | 0.2228 | -0.0064 | 16 | 0 | within one SE |
| balanced | 16 | 200 | 0.1388 | 0.2305 | 0.2586 | 0.3127 | 0.2056 | 0.2292 | 0.0288 | 0.2433 | 0.0141 | 17 | 0 | within one SE |
| balanced | 18 | 200 | 0.1388 | 0.2305 | 0.2585 | 0.3126 | 0.2056 | 0.2292 | 0.0288 | 0.2435 | 0.0143 | 18 | 0 | within one SE |
| none | 8 | 100 | 0.1411 | 0.2406 | 0.2513 | 0.3200 | 0.1930 | 0.2292 | 0.0299 | 0.2498 | 0.0206 | 19 | 0 | within one SE |
| none | 14 | 100 | 0.1417 | 0.2432 | 0.2541 | 0.3168 | 0.1879 | 0.2287 | 0.0299 | 0.2739 | 0.0451 | 20 | 0 | within one SE |
| balanced | 6 | 100 | 0.1468 | 0.2274 | 0.2566 | 0.3098 | 0.2017 | 0.2284 | 0.0272 | 0.2360 | 0.0076 | 21 | 0 | within one SE |
| none | 18 | 100 | 0.1417 | 0.2433 | 0.2540 | 0.3155 | 0.1873 | 0.2284 | 0.0297 | 0.2765 | 0.0481 | 22 | 0 | within one SE |
| none | 6 | 100 | 0.1448 | 0.2406 | 0.2548 | 0.3094 | 0.1920 | 0.2283 | 0.0280 | 0.2318 | 0.0034 | 23 | 0 | within one SE |
| none | 16 | 100 | 0.1417 | 0.2425 | 0.2537 | 0.3159 | 0.1868 | 0.2281 | 0.0298 | 0.2757 | 0.0476 | 24 | 0 | within one SE |
| none | 4 | 100 | 0.1426 | 0.2311 | 0.2524 | 0.3167 | 0.1967 | 0.2279 | 0.0289 | 0.2053 | -0.0225 | 25 | 0 | within one SE |
| balanced | 5 | 50 | 0.1381 | 0.2339 | 0.2600 | 0.3114 | 0.1928 | 0.2272 | 0.0295 | 0.2293 | 0.0021 | 26 | 0 | within one SE |
| none | 4 | 20 | 0.1442 | 0.2238 | 0.2529 | 0.3183 | 0.1967 | 0.2272 | 0.0290 | 0.2096 | -0.0175 | 27 | 0 | within one SE |
| balanced | 10 | 200 | 0.1397 | 0.2309 | 0.2599 | 0.3153 | 0.1891 | 0.2270 | 0.0300 | 0.2384 | 0.0114 | 28 | 0 | within one SE |
| balanced | 5 | 200 | 0.1398 | 0.2284 | 0.2579 | 0.3092 | 0.1991 | 0.2269 | 0.0284 | 0.2148 | -0.0121 | 29 | 0 | within one SE |
| none | 6 | 200 | 0.1390 | 0.2417 | 0.2610 | 0.2995 | 0.1923 | 0.2267 | 0.0279 | 0.2196 | -0.0071 | 30 | 0 | within one SE |
| balanced | 5 | 100 | 0.1383 | 0.2316 | 0.2567 | 0.3091 | 0.1966 | 0.2264 | 0.0287 | 0.2243 | -0.0021 | 31 | 0 | within one SE |
| none | 8 | 50 | 0.1414 | 0.2315 | 0.2370 | 0.3197 | 0.2015 | 0.2262 | 0.0289 | 0.2626 | 0.0364 | 32 | 0 | within one SE |
| balanced | 8 | 100 | 0.1338 | 0.2320 | 0.2567 | 0.3094 | 0.1981 | 0.2260 | 0.0293 | 0.2540 | 0.0280 | 33 | 0 | within one SE |
| balanced | 14 | 200 | 0.1388 | 0.2305 | 0.2587 | 0.3136 | 0.1883 | 0.2260 | 0.0298 | 0.2429 | 0.0170 | 34 | 0 | within one SE |
| none | 4 | 50 | 0.1364 | 0.2244 | 0.2527 | 0.3176 | 0.1964 | 0.2255 | 0.0300 | 0.2056 | -0.0199 | 35 | 0 | within one SE |
| balanced | 4 | 100 | 0.1395 | 0.2229 | 0.2572 | 0.3053 | 0.1970 | 0.2244 | 0.0279 | 0.2100 | -0.0144 | 36 | 0 | within one SE |
| balanced | 10 | 100 | 0.1372 | 0.2268 | 0.2533 | 0.3094 | 0.1952 | 0.2244 | 0.0287 | 0.2661 | 0.0417 | 37 | 0 | within one SE |
| none | 10 | 50 | 0.1379 | 0.2302 | 0.2410 | 0.3181 | 0.1945 | 0.2243 | 0.0295 | 0.2859 | 0.0615 | 38 | 0 | within one SE |
| balanced | 5 | 20 | 0.1346 | 0.2272 | 0.2570 | 0.3080 | 0.1941 | 0.2242 | 0.0292 | 0.2334 | 0.0092 | 39 | 0 | within one SE |
| none | 6 | 50 | 0.1338 | 0.2414 | 0.2504 | 0.3076 | 0.1877 | 0.2242 | 0.0295 | 0.2370 | 0.0128 | 40 | 0 | within one SE |
| balanced | 6 | 50 | 0.1394 | 0.2256 | 0.2587 | 0.3100 | 0.1857 | 0.2239 | 0.0293 | 0.2447 | 0.0208 | 41 | 0 | within one SE |
| balanced | 4 | 50 | 0.1381 | 0.2274 | 0.2552 | 0.3028 | 0.1947 | 0.2236 | 0.0278 | 0.2112 | -0.0124 | 42 | 0 | within one SE |
| balanced | 4 | 200 | 0.1394 | 0.2200 | 0.2518 | 0.3055 | 0.1993 | 0.2232 | 0.0276 | 0.2040 | -0.0192 | 43 | 0 | within one SE |
| balanced | 4 | 20 | 0.1348 | 0.2204 | 0.2555 | 0.3036 | 0.1973 | 0.2223 | 0.0283 | 0.2138 | -0.0085 | 44 | 0 | within one SE |
| balanced | 6 | 20 | 0.1341 | 0.2215 | 0.2611 | 0.3079 | 0.1843 | 0.2218 | 0.0300 | 0.2526 | 0.0308 | 45 | 0 | within one SE |
| balanced | 8 | 50 | 0.1379 | 0.2225 | 0.2516 | 0.3020 | 0.1939 | 0.2216 | 0.0275 | 0.2709 | 0.0494 | 46 | 0 | within one SE |
| balanced | 16 | 100 | 0.1353 | 0.2239 | 0.2491 | 0.3036 | 0.1945 | 0.2213 | 0.0280 | 0.2788 | 0.0575 | 47 | 0 | within one SE |
| balanced | 12 | 100 | 0.1356 | 0.2249 | 0.2514 | 0.3103 | 0.1820 | 0.2208 | 0.0298 | 0.2731 | 0.0523 | 48 | 0 | within one SE |
| none | 6 | 20 | 0.1445 | 0.2320 | 0.2373 | 0.2962 | 0.1912 | 0.2202 | 0.0253 | 0.2518 | 0.0316 | 49 | 0 | within one SE |
| none | 12 | 50 | 0.1376 | 0.2265 | 0.2379 | 0.3112 | 0.1850 | 0.2197 | 0.0289 | 0.3023 | 0.0826 | 50 | 0 | within one SE |
| balanced | 14 | 100 | 0.1353 | 0.2240 | 0.2497 | 0.3049 | 0.1826 | 0.2193 | 0.0289 | 0.2768 | 0.0575 | 51 | 0 | within one SE |
| balanced | 18 | 100 | 0.1353 | 0.2239 | 0.2487 | 0.3016 | 0.1813 | 0.2182 | 0.0284 | 0.2795 | 0.0614 | 52 | 0 | within one SE |
| none | 14 | 50 | 0.1371 | 0.2273 | 0.2338 | 0.3093 | 0.1802 | 0.2175 | 0.0289 | 0.3134 | 0.0959 | 53 | 0 | within one SE |
| none | 16 | 50 | 0.1374 | 0.2225 | 0.2346 | 0.3047 | 0.1781 | 0.2154 | 0.0282 | 0.3209 | 0.1055 | 54 | 0 | within one SE |
| none | 18 | 50 | 0.1377 | 0.2234 | 0.2317 | 0.3005 | 0.1796 | 0.2146 | 0.0273 | 0.3238 | 0.1092 | 55 | 0 | within one SE |
| balanced | 8 | 20 | 0.1253 | 0.2256 | 0.2380 | 0.3041 | 0.1792 | 0.2144 | 0.0299 | 0.2914 | 0.0770 | 56 | 0 | within one SE |
| balanced | 10 | 50 | 0.1365 | 0.2146 | 0.2473 | 0.2957 | 0.1715 | 0.2131 | 0.0279 | 0.2918 | 0.0787 | 57 | 0 | within one SE |
| balanced | 12 | 50 | 0.1359 | 0.2132 | 0.2418 | 0.2907 | 0.1825 | 0.2128 | 0.0262 | 0.3107 | 0.0979 | 58 | 0 | within one SE |
| none | 8 | 20 | 0.1423 | 0.2222 | 0.2229 | 0.2969 | 0.1783 | 0.2125 | 0.0259 | 0.2907 | 0.0781 | 59 | 0 | within one SE |
| balanced | 14 | 50 | 0.1353 | 0.2118 | 0.2390 | 0.2870 | 0.1803 | 0.2107 | 0.0257 | 0.3251 | 0.1144 | 60 | 0 | within one SE |
| balanced | 18 | 50 | 0.1349 | 0.2115 | 0.2375 | 0.2866 | 0.1784 | 0.2098 | 0.0258 | 0.3330 | 0.1232 | 61 | 0 | within one SE |
| none | 12 | 20 | 0.1418 | 0.2142 | 0.2121 | 0.2901 | 0.1847 | 0.2086 | 0.0242 | 0.3594 | 0.1508 | 62 | 0 | within one SE |
| balanced | 16 | 50 | 0.1353 | 0.2113 | 0.2378 | 0.2887 | 0.1663 | 0.2079 | 0.0269 | 0.3300 | 0.1221 | 63 | 0 | within one SE |
| none | 10 | 20 | 0.1408 | 0.2171 | 0.2134 | 0.2944 | 0.1697 | 0.2071 | 0.0260 | 0.3279 | 0.1208 | 64 | 0 | within one SE |
| balanced | 10 | 20 | 0.1279 | 0.2107 | 0.2159 | 0.2900 | 0.1806 | 0.2050 | 0.0264 | 0.3295 | 0.1245 | 65 | 0 | within one SE |
| none | 14 | 20 | 0.1410 | 0.2096 | 0.2102 | 0.2846 | 0.1636 | 0.2018 | 0.0246 | 0.3835 | 0.1816 | 66 | 0 |  |
| none | 16 | 20 | 0.1392 | 0.2056 | 0.2094 | 0.2815 | 0.1626 | 0.1997 | 0.0244 | 0.4036 | 0.2039 | 67 | 0 |  |
| balanced | 12 | 20 | 0.1278 | 0.2022 | 0.2132 | 0.2843 | 0.1694 | 0.1994 | 0.0259 | 0.3639 | 0.1646 | 68 | 0 |  |
| none | 18 | 20 | 0.1383 | 0.2046 | 0.2091 | 0.2757 | 0.1618 | 0.1979 | 0.0235 | 0.4182 | 0.2203 | 69 | 0 |  |
| balanced | 14 | 20 | 0.1288 | 0.1966 | 0.2110 | 0.2773 | 0.1553 | 0.1938 | 0.0255 | 0.3953 | 0.2015 | 70 | 0 |  |
| balanced | 18 | 20 | 0.1264 | 0.1925 | 0.2079 | 0.2712 | 0.1506 | 0.1897 | 0.0250 | 0.4385 | 0.2488 | 71 | 0 |  |
| balanced | 16 | 20 | 0.1288 | 0.1935 | 0.2041 | 0.2747 | 0.1470 | 0.1896 | 0.0255 | 0.4202 | 0.2306 | 72 | 0 |  |

Source: pipeline\_b/stages/b07/classification/outputs/grid\_results.csv (run 20261023T164241Z); validation curves: figures/validation\_curve\_tree.png and curves/validation\_curve\_tree.csv.

## B7.4

**What was done:** forest: 48 configurations; best mean 0.2761 ({'class\_weight': None, 'max\_depth': 8, 'max\_features': 'sqrt', 'min\_samples\_leaf': 20}); one-SE choice {"class\_weight": null, "max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 200} with 0.2625 ± 0.0297.

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 18 configurations; single tree 72 configurations; forest 48 configurations) **Check** the grid point with the s06 plain settings reproduces the s06 fold scores (tree, forest): PASS (2 of 2 reproduced)

**Files** (pipeline\_b/stages/b07/classification/outputs/, run 20261023T164241Z): grid\_results.csv

### B7.4 full grid — forest (48 configurations)

**How the decision was made** (grid\_results.csv, plain\_vs\_tuned.csv; metric: average precision, higher is better):

1. Best mean in the grid: clf.sel.log.forest\_clf.class\_weight=none.max\_depth=8.max\_features=sqrt.min\_samples\_leaf=20 = 0.2761 (fold SE 0.0304).
2. One-SE bound: 0.2761 − 0.0304 = 0.2457. Configurations inside the bound are marked "within one SE".
3. One-SE choice: the simplest configuration inside the bound (protocol order: shallower depth, then larger leaf) = clf.sel.log.forest\_clf.class\_weight=none.max\_depth=8.max\_features=sqrt.min\_samples\_leaf=200, 0.2625.
4. Against the plain B6 model: plain B6 model clf.sel.log.forest\_clf.max\_depth=10.max\_features=sqrt.min\_samples\_leaf=50: 0.2739; tuned one-SE choice clf.sel.log.forest\_clf.class\_weight=none.max\_depth=8.max\_features=sqrt.min\_samples\_leaf=200: 0.2625 (SE 0.0297); paired gain of tuned -0.0114 (paired SE 0.0026), better in 0 of 5 folds → carried: **plain** (G-55).

**Grid edge:** the one-SE choice sits at the edge of the pre-registered grid for max\_depth = 8 (lowest value in the grid); min\_samples\_leaf = 200 (highest value in the grid). This is the simpler end of the grid (protocol order: higher alpha, lower C, shallower depth, larger leaf), which is where the one-SE rule moves the choice by design; it means the grid may not extend far enough on that side. A's code reviews grid edges at the B8 gate (grid\_edge\_action in human\_decisions\_B.yaml b08), not here.

**Effect of each parameter** (best and average validation mean over the configurations with that value):

| parameter | value | configurations | best validation mean | mean over its configurations |
| --- | --- | --- | --- | --- |
| class\_weight | balanced | 24 | 0.2695 | 0.2654 |
| class\_weight | none | 24 | 0.2761 | 0.2705 |
| max\_depth | 8 | 8 | 0.2761 | 0.2682 |
| max\_depth | 10 | 8 | 0.2745 | 0.2681 |
| max\_depth | 12 | 8 | 0.2739 | 0.2677 |
| max\_depth | 14 | 8 | 0.2745 | 0.2679 |
| max\_depth | 16 | 8 | 0.2754 | 0.2679 |
| max\_depth | 18 | 8 | 0.2740 | 0.2680 |
| max\_features | sqrt | 48 | 0.2761 | 0.2680 |
| min\_samples\_leaf | 20 | 12 | 0.2761 | 0.2716 |
| min\_samples\_leaf | 50 | 12 | 0.2746 | 0.2710 |
| min\_samples\_leaf | 100 | 12 | 0.2708 | 0.2678 |
| min\_samples\_leaf | 200 | 12 | 0.2645 | 0.2615 |

**Every configuration, ranked** (per-fold validation scores, mean, fold SE, training mean, train–validation gap; positive gap = worse on validation than on the training folds, in both tasks, as in A's s07):

| class\_weight | max\_depth | max\_features | min\_samples\_leaf | val f1 | val f2 | val f3 | val f4 | val f5 | validation\_mean | validation\_se | train\_mean | train\_validation\_gap | rank | convergence\_warnings | flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| none | 8 | sqrt | 20 | 0.1848 | 0.2884 | 0.2967 | 0.3680 | 0.2425 | 0.2761 | 0.0304 | 0.3018 | 0.0257 | 1 | 0 | best mean; within one SE |
| none | 16 | sqrt | 20 | 0.1844 | 0.2886 | 0.2943 | 0.3661 | 0.2434 | 0.2754 | 0.0301 | 0.3906 | 0.1152 | 2 | 0 | within one SE |
| none | 8 | sqrt | 50 | 0.1794 | 0.2870 | 0.2962 | 0.3647 | 0.2454 | 0.2746 | 0.0305 | 0.2748 | 0.0002 | 3 | 0 | within one SE |
| none | 14 | sqrt | 20 | 0.1844 | 0.2873 | 0.2915 | 0.3628 | 0.2466 | 0.2745 | 0.0293 | 0.3756 | 0.1011 | 4 | 0 | within one SE |
| none | 10 | sqrt | 20 | 0.1817 | 0.2865 | 0.2958 | 0.3665 | 0.2417 | 0.2745 | 0.0306 | 0.3261 | 0.0516 | 5 | 0 | within one SE |
| none | 18 | sqrt | 20 | 0.1839 | 0.2862 | 0.2932 | 0.3626 | 0.2444 | 0.2740 | 0.0295 | 0.4064 | 0.1324 | 6 | 0 | within one SE |
| none | 10 | sqrt | 50 | 0.1810 | 0.2859 | 0.2952 | 0.3652 | 0.2421 | 0.2739 | 0.0305 | 0.2868 | 0.0129 | 7 | 0 | within one SE |
| none | 12 | sqrt | 20 | 0.1839 | 0.2864 | 0.2931 | 0.3646 | 0.2414 | 0.2739 | 0.0299 | 0.3508 | 0.0769 | 8 | 0 | within one SE |
| none | 18 | sqrt | 50 | 0.1778 | 0.2866 | 0.2959 | 0.3657 | 0.2430 | 0.2738 | 0.0310 | 0.3136 | 0.0398 | 9 | 0 | within one SE |
| none | 16 | sqrt | 50 | 0.1782 | 0.2861 | 0.2959 | 0.3628 | 0.2459 | 0.2738 | 0.0304 | 0.3102 | 0.0364 | 10 | 0 | within one SE |
| none | 12 | sqrt | 50 | 0.1784 | 0.2862 | 0.2967 | 0.3631 | 0.2420 | 0.2733 | 0.0306 | 0.2975 | 0.0242 | 11 | 0 | within one SE |
| none | 14 | sqrt | 50 | 0.1769 | 0.2842 | 0.2934 | 0.3664 | 0.2419 | 0.2726 | 0.0312 | 0.3054 | 0.0329 | 12 | 0 | within one SE |
| none | 10 | sqrt | 100 | 0.1786 | 0.2763 | 0.2919 | 0.3640 | 0.2433 | 0.2708 | 0.0303 | 0.2620 | -0.0088 | 13 | 0 | within one SE |
| none | 8 | sqrt | 100 | 0.1776 | 0.2763 | 0.2915 | 0.3637 | 0.2425 | 0.2703 | 0.0305 | 0.2550 | -0.0153 | 14 | 0 | within one SE |
| none | 18 | sqrt | 100 | 0.1769 | 0.2752 | 0.2939 | 0.3610 | 0.2425 | 0.2699 | 0.0303 | 0.2708 | 0.0010 | 15 | 0 | within one SE |
| balanced | 8 | sqrt | 20 | 0.1785 | 0.2813 | 0.2886 | 0.3616 | 0.2374 | 0.2695 | 0.0303 | 0.3099 | 0.0404 | 16 | 0 | within one SE |
| none | 16 | sqrt | 100 | 0.1769 | 0.2751 | 0.2886 | 0.3637 | 0.2427 | 0.2694 | 0.0305 | 0.2699 | 0.0005 | 17 | 0 | within one SE |
| balanced | 10 | sqrt | 20 | 0.1751 | 0.2852 | 0.2863 | 0.3587 | 0.2414 | 0.2693 | 0.0302 | 0.3434 | 0.0741 | 18 | 0 | within one SE |
| none | 14 | sqrt | 100 | 0.1771 | 0.2741 | 0.2886 | 0.3634 | 0.2429 | 0.2692 | 0.0304 | 0.2683 | -0.0009 | 19 | 0 | within one SE |
| none | 12 | sqrt | 100 | 0.1766 | 0.2760 | 0.2906 | 0.3612 | 0.2414 | 0.2692 | 0.0303 | 0.2659 | -0.0032 | 20 | 0 | within one SE |
| balanced | 18 | sqrt | 50 | 0.1771 | 0.2817 | 0.2901 | 0.3609 | 0.2347 | 0.2689 | 0.0306 | 0.3120 | 0.0431 | 21 | 0 | within one SE |
| balanced | 12 | sqrt | 50 | 0.1769 | 0.2824 | 0.2857 | 0.3599 | 0.2394 | 0.2689 | 0.0301 | 0.2985 | 0.0296 | 22 | 0 | within one SE |
| balanced | 14 | sqrt | 20 | 0.1745 | 0.2822 | 0.2871 | 0.3592 | 0.2408 | 0.2687 | 0.0303 | 0.3969 | 0.1282 | 23 | 0 | within one SE |
| balanced | 16 | sqrt | 50 | 0.1763 | 0.2831 | 0.2870 | 0.3611 | 0.2362 | 0.2687 | 0.0306 | 0.3098 | 0.0411 | 24 | 0 | within one SE |
| balanced | 18 | sqrt | 20 | 0.1738 | 0.2841 | 0.2868 | 0.3577 | 0.2403 | 0.2685 | 0.0302 | 0.4294 | 0.1609 | 25 | 0 | within one SE |
| balanced | 14 | sqrt | 50 | 0.1763 | 0.2824 | 0.2849 | 0.3585 | 0.2383 | 0.2681 | 0.0300 | 0.3051 | 0.0371 | 26 | 0 | within one SE |
| balanced | 8 | sqrt | 50 | 0.1755 | 0.2795 | 0.2875 | 0.3626 | 0.2346 | 0.2679 | 0.0309 | 0.2723 | 0.0043 | 27 | 0 | within one SE |
| balanced | 12 | sqrt | 20 | 0.1748 | 0.2800 | 0.2906 | 0.3587 | 0.2355 | 0.2679 | 0.0305 | 0.3727 | 0.1048 | 28 | 0 | within one SE |
| balanced | 10 | sqrt | 50 | 0.1761 | 0.2817 | 0.2870 | 0.3589 | 0.2339 | 0.2675 | 0.0304 | 0.2874 | 0.0198 | 29 | 0 | within one SE |
| balanced | 16 | sqrt | 20 | 0.1735 | 0.2815 | 0.2854 | 0.3576 | 0.2367 | 0.2669 | 0.0303 | 0.4163 | 0.1494 | 30 | 0 | within one SE |
| balanced | 14 | sqrt | 100 | 0.1772 | 0.2750 | 0.2862 | 0.3585 | 0.2342 | 0.2662 | 0.0300 | 0.2651 | -0.0012 | 31 | 0 | within one SE |
| balanced | 8 | sqrt | 100 | 0.1766 | 0.2734 | 0.2872 | 0.3578 | 0.2353 | 0.2661 | 0.0299 | 0.2530 | -0.0131 | 32 | 0 | within one SE |
| balanced | 12 | sqrt | 100 | 0.1774 | 0.2740 | 0.2848 | 0.3571 | 0.2358 | 0.2658 | 0.0296 | 0.2628 | -0.0030 | 33 | 0 | within one SE |
| balanced | 16 | sqrt | 100 | 0.1774 | 0.2734 | 0.2858 | 0.3570 | 0.2340 | 0.2655 | 0.0297 | 0.2650 | -0.0005 | 34 | 0 | within one SE |
| balanced | 10 | sqrt | 100 | 0.1769 | 0.2747 | 0.2833 | 0.3589 | 0.2337 | 0.2655 | 0.0300 | 0.2590 | -0.0065 | 35 | 0 | within one SE |
| balanced | 18 | sqrt | 100 | 0.1774 | 0.2734 | 0.2858 | 0.3587 | 0.2319 | 0.2655 | 0.0300 | 0.2660 | 0.0005 | 36 | 0 | within one SE |
| none | 16 | sqrt | 200 | 0.1743 | 0.2699 | 0.2778 | 0.3628 | 0.2376 | 0.2645 | 0.0306 | 0.2444 | -0.0200 | 37 | 0 | within one SE |
| none | 18 | sqrt | 200 | 0.1743 | 0.2701 | 0.2777 | 0.3623 | 0.2380 | 0.2645 | 0.0305 | 0.2443 | -0.0202 | 38 | 0 | within one SE |
| none | 14 | sqrt | 200 | 0.1743 | 0.2697 | 0.2771 | 0.3616 | 0.2395 | 0.2644 | 0.0303 | 0.2439 | -0.0206 | 39 | 0 | within one SE |
| none | 10 | sqrt | 200 | 0.1741 | 0.2691 | 0.2771 | 0.3617 | 0.2393 | 0.2642 | 0.0304 | 0.2421 | -0.0221 | 40 | 0 | within one SE |
| none | 12 | sqrt | 200 | 0.1744 | 0.2693 | 0.2772 | 0.3576 | 0.2383 | 0.2634 | 0.0297 | 0.2429 | -0.0205 | 41 | 0 | within one SE |
| none | 8 | sqrt | 200 | 0.1739 | 0.2684 | 0.2773 | 0.3566 | 0.2361 | 0.2625 | 0.0297 | 0.2394 | -0.0230 | 42 | 0 | one-SE choice; within one SE |
| balanced | 12 | sqrt | 200 | 0.1695 | 0.2697 | 0.2749 | 0.3556 | 0.2285 | 0.2596 | 0.0305 | 0.2384 | -0.0212 | 43 | 0 | within one SE |
| balanced | 10 | sqrt | 200 | 0.1695 | 0.2700 | 0.2748 | 0.3531 | 0.2289 | 0.2593 | 0.0301 | 0.2372 | -0.0221 | 44 | 0 | within one SE |
| balanced | 16 | sqrt | 200 | 0.1695 | 0.2706 | 0.2727 | 0.3529 | 0.2303 | 0.2592 | 0.0300 | 0.2385 | -0.0207 | 45 | 0 | within one SE |
| balanced | 14 | sqrt | 200 | 0.1695 | 0.2702 | 0.2740 | 0.3535 | 0.2287 | 0.2592 | 0.0302 | 0.2383 | -0.0208 | 46 | 0 | within one SE |
| balanced | 18 | sqrt | 200 | 0.1695 | 0.2702 | 0.2729 | 0.3524 | 0.2297 | 0.2589 | 0.0299 | 0.2385 | -0.0204 | 47 | 0 | within one SE |
| balanced | 8 | sqrt | 200 | 0.1696 | 0.2676 | 0.2742 | 0.3547 | 0.2280 | 0.2588 | 0.0303 | 0.2349 | -0.0239 | 48 | 0 | within one SE |

Source: pipeline\_b/stages/b07/classification/outputs/grid\_results.csv (run 20261023T164241Z); validation curves: figures/validation\_curve\_forest.png and curves/validation\_curve\_forest.csv.

## B7.5

**What was done:** GridSearchCV over the whole s04 pipeline on the s05 folds, scoring average\_precision, refit=False, return\_train\_score=True, seed 42; 138 configurations in total. Carried per family: linear/logistic plain s06; single tree plain s06; forest plain s06. Ladder over the carried families (description only; s08 decides): linear/logistic kept over dummy (paired gain +0.1236, better in 5 of 5 folds); single tree not kept over linear/logistic (paired gain -0.0222, better in 0 of 5 folds); forest not kept over linear/logistic (paired gain +0.0123, better in 4 of 5 folds); result linear/logistic.

**Plain B6 model against the family's tuned one-SE choice** (plain\_vs\_tuned.csv):

| family | plain\_mean | tuned\_best | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | paired\_se | tuned\_better\_folds | carried |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| linear/logistic | 0.2616 | clf.sel.log.logistic.C=0.01.class\_weight=none | 0.2734 | 0.0318 | 0.0118 | 0.0051 | 4 | plain |
| single tree | 0.2394 | clf.sel.log.tree\_clf.class\_weight=none.max\_depth=4.min\_samples\_leaf=200 | 0.2298 | 0.0297 | -0.0096 | 0.0076 | 1 | plain |
| forest | 0.2739 | clf.sel.log.forest\_clf.class\_weight=none.max\_depth=8.max\_features=sqrt.min\_samples\_leaf=200 | 0.2625 | 0.0297 | -0.0114 | 0.0026 | 0 | plain |

**Check** same folds as s06 (rows per fold equal): PASS **Check** every configuration scored on all five folds, whole pipeline refitted per fold: PASS **Check** no test row read: every row used was purchased before the test cutoff: PASS (latest purchase 2018-05-23 11:29:51, cutoff 2018-05-26 12:16:34)

**Files** (pipeline\_b/stages/b07/classification/outputs/, run 20261023T164241Z): candidates.csv, counts.json, decision.json, grid\_results.csv, ladder\_preview.csv, plain\_vs\_tuned.csv

## B7.6

**What was done:** train\_validation\_gap for every configuration in grid\_results.csv (positive = worse on validation). Gap of each family's one-SE choice: linear/logistic -0.0463; single tree -0.0304; forest -0.0230.

**Files** (pipeline\_b/stages/b07/classification/outputs/, run 20261023T164241Z): grid\_results.csv; plus 12 figure/curve files

## B7.7

**What was done:** grid\_results.csv, plain\_vs\_tuned.csv, ladder\_preview.csv, candidates.csv, decision.json, out-of-fold predictions of each family's best (predictions.csv.gz) with pooled vs mean-fold scores (oof\_scores.csv), validation curves (curves/, figures/); fit times in \_manifest.json.

**Check** refitting each family's best per fold gives the grid's validation scores: PASS (15 refits)

**Files** (pipeline\_b/stages/b07/classification/outputs/, run 20261023T164241Z): counts.json, oof\_scores.csv, predictions.csv.gz
