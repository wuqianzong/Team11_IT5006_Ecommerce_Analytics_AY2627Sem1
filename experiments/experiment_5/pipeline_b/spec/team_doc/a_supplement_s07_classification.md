# s07 Tuning › classification — evidence cards

## Supplement for decisions and the report (added 2026-10-24; DOC\_GAPS D-04)

Added after the pipeline ran, from accepted outputs only; nothing above is changed. Source: A's s07 grid\_results.csv and plain\_vs\_tuned.csv at e5-A-frozen (run 20261023T084930Z); same layout as the B7 tabs.

### Full grid — linear/logistic (18 configurations)

Best mean clf.sel.log.logistic.C=0.01.class\_weight=none = 0.2553 (SE 0.0294); one-SE bound 0.2259; one-SE choice clf.sel.log.logistic.C=0.01.class\_weight=none = 0.2553. Against the plain s06 model: tuned paired gain +0.0118 (paired SE 0.0045), better in 5 of 5 folds; carried: plain (G-55). Grid edge: the one-SE choice sits at the edge of the grid for C = 0.01 (lowest value in the grid) (the simpler end, where the one-SE rule moves the choice by design).

Effect of each parameter:

| parameter | value | configurations | best validation mean | mean over its configurations |
| --- | --- | --- | --- | --- |
| C | 0.01 | 2 | 0.2553 | 0.2542 |
| C | 0.1 | 2 | 0.2506 | 0.2499 |
| C | 0.5 | 2 | 0.2481 | 0.2474 |
| C | 1.0 | 2 | 0.2470 | 0.2463 |
| C | 10.0 | 2 | 0.2443 | 0.2438 |
| C | 100.0 | 2 | 0.2437 | 0.2433 |
| C | 20.0 | 2 | 0.2442 | 0.2437 |
| C | 5.0 | 2 | 0.2446 | 0.2442 |
| C | 50.0 | 2 | 0.2434 | 0.2432 |
| class\_weight | balanced | 9 | 0.2532 | 0.2457 |
| class\_weight | none | 9 | 0.2553 | 0.2468 |

Every configuration, ranked (per-fold validation, mean, SE, training mean, gap):

| C | class\_weight | val f1 | val f2 | val f3 | val f4 | val f5 | validation\_mean | validation\_se | train\_mean | train\_validation\_gap | rank | flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.01 | none | 0.1746 | 0.2629 | 0.2543 | 0.3554 | 0.2292 | 0.2553 | 0.0294 | 0.2113 | -0.0440 | 1 | best mean; one-SE choice; within one SE |
| 0.01 | balanced | 0.1713 | 0.2605 | 0.2522 | 0.3537 | 0.2282 | 0.2532 | 0.0296 | 0.2122 | -0.0410 | 2 | within one SE |
| 0.1 | none | 0.1647 | 0.2543 | 0.2512 | 0.3541 | 0.2289 | 0.2506 | 0.0305 | 0.2167 | -0.0339 | 3 | within one SE |
| 0.1 | balanced | 0.1636 | 0.2534 | 0.2494 | 0.3516 | 0.2278 | 0.2492 | 0.0302 | 0.2162 | -0.0330 | 4 | within one SE |
| 0.5 | none | 0.1605 | 0.2497 | 0.2490 | 0.3527 | 0.2288 | 0.2481 | 0.0308 | 0.2190 | -0.0292 | 5 | within one SE |
| 1.0 | none | 0.1587 | 0.2471 | 0.2483 | 0.3522 | 0.2284 | 0.2470 | 0.0310 | 0.2196 | -0.0273 | 6 | within one SE |
| 0.5 | balanced | 0.1602 | 0.2486 | 0.2472 | 0.3496 | 0.2273 | 0.2466 | 0.0304 | 0.2177 | -0.0288 | 7 | within one SE |
| 1.0 | balanced | 0.1588 | 0.2473 | 0.2462 | 0.3487 | 0.2270 | 0.2456 | 0.0304 | 0.2182 | -0.0274 | 8 | within one SE |
| 5.0 | none | 0.1552 | 0.2427 | 0.2464 | 0.3504 | 0.2282 | 0.2446 | 0.0312 | 0.2210 | -0.0236 | 9 | within one SE |
| 10.0 | none | 0.1548 | 0.2418 | 0.2457 | 0.3505 | 0.2285 | 0.2443 | 0.0313 | 0.2211 | -0.0231 | 10 | within one SE |
| 20.0 | none | 0.1544 | 0.2416 | 0.2458 | 0.3508 | 0.2283 | 0.2442 | 0.0314 | 0.2212 | -0.0230 | 11 | within one SE |
| 5.0 | balanced | 0.1571 | 0.2432 | 0.2455 | 0.3467 | 0.2268 | 0.2439 | 0.0303 | 0.2190 | -0.0249 | 12 | within one SE |
| 100.0 | none | 0.1535 | 0.2390 | 0.2465 | 0.3508 | 0.2286 | 0.2437 | 0.0315 | 0.2213 | -0.0224 | 13 | within one SE |
| 10.0 | balanced | 0.1560 | 0.2429 | 0.2450 | 0.3464 | 0.2267 | 0.2434 | 0.0304 | 0.2192 | -0.0242 | 14 | within one SE |
| 50.0 | none | 0.1536 | 0.2396 | 0.2456 | 0.3500 | 0.2279 | 0.2434 | 0.0314 | 0.2212 | -0.0221 | 15 | within one SE |
| 20.0 | balanced | 0.1561 | 0.2415 | 0.2447 | 0.3472 | 0.2268 | 0.2433 | 0.0306 | 0.2193 | -0.0239 | 16 | within one SE |
| 50.0 | balanced | 0.1558 | 0.2417 | 0.2444 | 0.3471 | 0.2266 | 0.2431 | 0.0306 | 0.2194 | -0.0237 | 17 | within one SE |
| 100.0 | balanced | 0.1552 | 0.2413 | 0.2443 | 0.3470 | 0.2267 | 0.2429 | 0.0306 | 0.2194 | -0.0235 | 18 | within one SE |

### Full grid — single tree (72 configurations)

Best mean clf.sel.log.tree\_clf.class\_weight=none.max\_depth=10.min\_samples\_leaf=200 = 0.2216 (SE 0.0230); one-SE bound 0.1986; one-SE choice clf.sel.log.tree\_clf.class\_weight=none.max\_depth=4.min\_samples\_leaf=200 = 0.2134. Against the plain s06 model: tuned paired gain -0.0024 (paired SE 0.0022), better in 2 of 5 folds; carried: plain (G-55). Grid edge: the one-SE choice sits at the edge of the grid for max\_depth = 4 (lowest value in the grid); min\_samples\_leaf = 200 (highest value in the grid) (the simpler end, where the one-SE rule moves the choice by design).

Effect of each parameter:

| parameter | value | configurations | best validation mean | mean over its configurations |
| --- | --- | --- | --- | --- |
| class\_weight | balanced | 36 | 0.2193 | 0.2096 |
| class\_weight | none | 36 | 0.2216 | 0.2104 |
| max\_depth | 10 | 8 | 0.2216 | 0.2106 |
| max\_depth | 12 | 8 | 0.2206 | 0.2088 |
| max\_depth | 14 | 8 | 0.2203 | 0.2067 |
| max\_depth | 16 | 8 | 0.2201 | 0.2057 |
| max\_depth | 18 | 8 | 0.2202 | 0.2047 |
| max\_depth | 4 | 8 | 0.2140 | 0.2118 |
| max\_depth | 5 | 8 | 0.2187 | 0.2146 |
| max\_depth | 6 | 8 | 0.2193 | 0.2144 |
| max\_depth | 8 | 8 | 0.2211 | 0.2129 |
| min\_samples\_leaf | 100 | 18 | 0.2158 | 0.2112 |
| min\_samples\_leaf | 20 | 18 | 0.2129 | 0.2019 |
| min\_samples\_leaf | 200 | 18 | 0.2216 | 0.2182 |
| min\_samples\_leaf | 50 | 18 | 0.2148 | 0.2088 |

Every configuration, ranked (per-fold validation, mean, SE, training mean, gap):

| class\_weight | max\_depth | min\_samples\_leaf | val f1 | val f2 | val f3 | val f4 | val f5 | validation\_mean | validation\_se | train\_mean | train\_validation\_gap | rank | flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| none | 10 | 200 | 0.1402 | 0.2344 | 0.2366 | 0.2811 | 0.2157 | 0.2216 | 0.0230 | 0.2293 | 0.0077 | 1 | best mean; within one SE |
| none | 8 | 200 | 0.1417 | 0.2354 | 0.2340 | 0.2806 | 0.2136 | 0.2211 | 0.0227 | 0.2224 | 0.0013 | 2 | within one SE |
| none | 12 | 200 | 0.1400 | 0.2343 | 0.2340 | 0.2804 | 0.2143 | 0.2206 | 0.0229 | 0.2325 | 0.0119 | 3 | within one SE |
| none | 14 | 200 | 0.1400 | 0.2346 | 0.2341 | 0.2793 | 0.2136 | 0.2203 | 0.0228 | 0.2340 | 0.0136 | 4 | within one SE |
| none | 18 | 200 | 0.1400 | 0.2347 | 0.2342 | 0.2789 | 0.2134 | 0.2202 | 0.0227 | 0.2350 | 0.0148 | 5 | within one SE |
| none | 16 | 200 | 0.1400 | 0.2347 | 0.2339 | 0.2787 | 0.2134 | 0.2201 | 0.0227 | 0.2345 | 0.0144 | 6 | within one SE |
| balanced | 6 | 200 | 0.1412 | 0.2286 | 0.2326 | 0.2826 | 0.2117 | 0.2193 | 0.0228 | 0.2110 | -0.0084 | 7 | within one SE |
| balanced | 10 | 200 | 0.1401 | 0.2225 | 0.2285 | 0.2830 | 0.2221 | 0.2192 | 0.0228 | 0.2288 | 0.0096 | 8 | within one SE |
| balanced | 8 | 200 | 0.1417 | 0.2236 | 0.2322 | 0.2846 | 0.2136 | 0.2191 | 0.0229 | 0.2224 | 0.0032 | 9 | within one SE |
| none | 5 | 200 | 0.1416 | 0.2367 | 0.2308 | 0.2816 | 0.2028 | 0.2187 | 0.0230 | 0.2038 | -0.0149 | 10 | within one SE |
| none | 6 | 200 | 0.1412 | 0.2379 | 0.2270 | 0.2795 | 0.2076 | 0.2186 | 0.0227 | 0.2113 | -0.0073 | 11 | within one SE |
| balanced | 12 | 200 | 0.1401 | 0.2240 | 0.2285 | 0.2809 | 0.2159 | 0.2179 | 0.0226 | 0.2327 | 0.0148 | 12 | within one SE |
| balanced | 18 | 200 | 0.1401 | 0.2240 | 0.2291 | 0.2793 | 0.2143 | 0.2174 | 0.0224 | 0.2354 | 0.0181 | 13 | within one SE |
| balanced | 14 | 200 | 0.1401 | 0.2240 | 0.2285 | 0.2791 | 0.2145 | 0.2172 | 0.0223 | 0.2345 | 0.0173 | 14 | within one SE |
| balanced | 16 | 200 | 0.1401 | 0.2240 | 0.2284 | 0.2794 | 0.2142 | 0.2172 | 0.0224 | 0.2351 | 0.0178 | 15 | within one SE |
| none | 5 | 100 | 0.1393 | 0.2325 | 0.2318 | 0.2798 | 0.1956 | 0.2158 | 0.0233 | 0.2078 | -0.0080 | 16 | within one SE |
| balanced | 6 | 100 | 0.1413 | 0.2275 | 0.2225 | 0.2830 | 0.2047 | 0.2158 | 0.0228 | 0.2171 | 0.0013 | 17 | within one SE |
| balanced | 5 | 100 | 0.1404 | 0.2293 | 0.2231 | 0.2786 | 0.2030 | 0.2149 | 0.0224 | 0.2070 | -0.0079 | 18 | within one SE |
| balanced | 6 | 50 | 0.1408 | 0.2264 | 0.2184 | 0.2875 | 0.2006 | 0.2148 | 0.0236 | 0.2222 | 0.0074 | 19 | within one SE |
| balanced | 5 | 200 | 0.1416 | 0.2199 | 0.2269 | 0.2773 | 0.2075 | 0.2146 | 0.0218 | 0.2035 | -0.0111 | 20 | within one SE |
| balanced | 5 | 50 | 0.1423 | 0.2289 | 0.2198 | 0.2802 | 0.2003 | 0.2143 | 0.0223 | 0.2099 | -0.0043 | 21 | within one SE |
| none | 4 | 100 | 0.1389 | 0.2294 | 0.2331 | 0.2720 | 0.1963 | 0.2140 | 0.0223 | 0.1960 | -0.0180 | 22 | within one SE |
| none | 10 | 100 | 0.1367 | 0.2210 | 0.2301 | 0.2851 | 0.1963 | 0.2138 | 0.0241 | 0.2478 | 0.0340 | 23 | within one SE |
| balanced | 8 | 50 | 0.1386 | 0.2256 | 0.2115 | 0.2900 | 0.2015 | 0.2134 | 0.0243 | 0.2487 | 0.0353 | 24 | within one SE |
| none | 4 | 200 | 0.1428 | 0.2334 | 0.2239 | 0.2728 | 0.1942 | 0.2134 | 0.0217 | 0.1934 | -0.0200 | 25 | one-SE choice; within one SE |
| none | 6 | 100 | 0.1354 | 0.2250 | 0.2288 | 0.2815 | 0.1954 | 0.2132 | 0.0239 | 0.2184 | 0.0052 | 26 | within one SE |
| none | 5 | 20 | 0.1401 | 0.2246 | 0.2286 | 0.2788 | 0.1923 | 0.2129 | 0.0229 | 0.2134 | 0.0005 | 27 | within one SE |
| none | 5 | 50 | 0.1403 | 0.2279 | 0.2212 | 0.2786 | 0.1960 | 0.2128 | 0.0226 | 0.2100 | -0.0028 | 28 | within one SE |
| balanced | 5 | 20 | 0.1391 | 0.2230 | 0.2201 | 0.2812 | 0.2004 | 0.2128 | 0.0228 | 0.2109 | -0.0019 | 29 | within one SE |
| none | 8 | 100 | 0.1388 | 0.2221 | 0.2307 | 0.2796 | 0.1923 | 0.2127 | 0.0232 | 0.2361 | 0.0234 | 30 | within one SE |
| balanced | 4 | 100 | 0.1398 | 0.2299 | 0.2224 | 0.2740 | 0.1971 | 0.2127 | 0.0220 | 0.1965 | -0.0161 | 31 | within one SE |
| balanced | 8 | 100 | 0.1384 | 0.2302 | 0.2148 | 0.2758 | 0.2024 | 0.2123 | 0.0223 | 0.2363 | 0.0240 | 32 | within one SE |
| none | 6 | 50 | 0.1402 | 0.2274 | 0.2206 | 0.2787 | 0.1943 | 0.2122 | 0.0226 | 0.2228 | 0.0106 | 33 | within one SE |
| balanced | 4 | 50 | 0.1401 | 0.2291 | 0.2213 | 0.2737 | 0.1966 | 0.2122 | 0.0219 | 0.1971 | -0.0151 | 34 | within one SE |
| balanced | 4 | 200 | 0.1428 | 0.2193 | 0.2235 | 0.2745 | 0.1984 | 0.2117 | 0.0213 | 0.1938 | -0.0179 | 35 | within one SE |
| none | 12 | 100 | 0.1353 | 0.2224 | 0.2266 | 0.2868 | 0.1870 | 0.2116 | 0.0249 | 0.2559 | 0.0443 | 36 | within one SE |
| balanced | 6 | 20 | 0.1372 | 0.2188 | 0.2139 | 0.2841 | 0.2002 | 0.2108 | 0.0234 | 0.2252 | 0.0144 | 37 | within one SE |
| none | 4 | 50 | 0.1405 | 0.2212 | 0.2263 | 0.2713 | 0.1943 | 0.2107 | 0.0215 | 0.1971 | -0.0136 | 38 | within one SE |
| none | 6 | 20 | 0.1406 | 0.2199 | 0.2190 | 0.2767 | 0.1968 | 0.2106 | 0.0219 | 0.2300 | 0.0194 | 39 | within one SE |
| balanced | 4 | 20 | 0.1372 | 0.2249 | 0.2220 | 0.2756 | 0.1933 | 0.2106 | 0.0226 | 0.1969 | -0.0137 | 40 | within one SE |
| balanced | 10 | 50 | 0.1367 | 0.2213 | 0.2071 | 0.2885 | 0.1970 | 0.2101 | 0.0243 | 0.2698 | 0.0596 | 41 | within one SE |
| none | 8 | 50 | 0.1421 | 0.2225 | 0.2140 | 0.2766 | 0.1935 | 0.2097 | 0.0218 | 0.2479 | 0.0382 | 42 | within one SE |
| none | 14 | 100 | 0.1353 | 0.2229 | 0.2225 | 0.2827 | 0.1839 | 0.2094 | 0.0244 | 0.2605 | 0.0511 | 43 | within one SE |
| none | 4 | 20 | 0.1405 | 0.2192 | 0.2275 | 0.2669 | 0.1927 | 0.2094 | 0.0209 | 0.1983 | -0.0111 | 44 | within one SE |
| balanced | 10 | 100 | 0.1376 | 0.2274 | 0.2065 | 0.2723 | 0.2028 | 0.2093 | 0.0218 | 0.2485 | 0.0392 | 45 | within one SE |
| balanced | 12 | 50 | 0.1362 | 0.2191 | 0.2057 | 0.2864 | 0.1985 | 0.2092 | 0.0240 | 0.2851 | 0.0760 | 46 | within one SE |
| none | 16 | 100 | 0.1353 | 0.2216 | 0.2221 | 0.2848 | 0.1818 | 0.2091 | 0.0248 | 0.2627 | 0.0535 | 47 | within one SE |
| none | 8 | 20 | 0.1453 | 0.2152 | 0.2085 | 0.2775 | 0.1960 | 0.2085 | 0.0212 | 0.2637 | 0.0552 | 48 | within one SE |
| none | 18 | 100 | 0.1353 | 0.2216 | 0.2226 | 0.2813 | 0.1811 | 0.2084 | 0.0243 | 0.2639 | 0.0555 | 49 | within one SE |
| balanced | 12 | 100 | 0.1374 | 0.2281 | 0.2077 | 0.2730 | 0.1957 | 0.2084 | 0.0221 | 0.2563 | 0.0479 | 50 | within one SE |
| balanced | 14 | 100 | 0.1368 | 0.2286 | 0.2045 | 0.2731 | 0.1939 | 0.2074 | 0.0223 | 0.2611 | 0.0537 | 51 | within one SE |
| balanced | 14 | 50 | 0.1364 | 0.2200 | 0.2045 | 0.2825 | 0.1908 | 0.2068 | 0.0236 | 0.2970 | 0.0902 | 52 | within one SE |
| balanced | 8 | 20 | 0.1355 | 0.2150 | 0.2044 | 0.2855 | 0.1930 | 0.2067 | 0.0240 | 0.2581 | 0.0514 | 53 | within one SE |
| none | 10 | 50 | 0.1422 | 0.2105 | 0.2141 | 0.2721 | 0.1941 | 0.2066 | 0.0208 | 0.2679 | 0.0613 | 54 | within one SE |
| balanced | 18 | 100 | 0.1368 | 0.2280 | 0.2045 | 0.2715 | 0.1917 | 0.2065 | 0.0221 | 0.2654 | 0.0589 | 55 | within one SE |
| none | 12 | 50 | 0.1407 | 0.2124 | 0.2135 | 0.2736 | 0.1920 | 0.2064 | 0.0214 | 0.2820 | 0.0756 | 56 | within one SE |
| balanced | 16 | 100 | 0.1368 | 0.2285 | 0.2042 | 0.2717 | 0.1908 | 0.2064 | 0.0222 | 0.2639 | 0.0575 | 57 | within one SE |
| balanced | 16 | 50 | 0.1364 | 0.2177 | 0.2027 | 0.2812 | 0.1915 | 0.2059 | 0.0233 | 0.3050 | 0.0991 | 58 | within one SE |
| balanced | 18 | 50 | 0.1365 | 0.2171 | 0.2043 | 0.2770 | 0.1887 | 0.2047 | 0.0227 | 0.3098 | 0.1051 | 59 | within one SE |
| none | 14 | 50 | 0.1406 | 0.2125 | 0.2040 | 0.2712 | 0.1936 | 0.2044 | 0.0209 | 0.2927 | 0.0883 | 60 | within one SE |
| none | 16 | 50 | 0.1407 | 0.2110 | 0.2033 | 0.2665 | 0.1938 | 0.2030 | 0.0201 | 0.2995 | 0.0965 | 61 | within one SE |
| none | 10 | 20 | 0.1418 | 0.2095 | 0.2041 | 0.2692 | 0.1873 | 0.2024 | 0.0205 | 0.2987 | 0.0963 | 62 | within one SE |
| balanced | 10 | 20 | 0.1380 | 0.2081 | 0.1959 | 0.2823 | 0.1847 | 0.2018 | 0.0234 | 0.2945 | 0.0927 | 63 | within one SE |
| none | 18 | 50 | 0.1408 | 0.2115 | 0.1983 | 0.2654 | 0.1897 | 0.2011 | 0.0200 | 0.3041 | 0.1030 | 64 | within one SE |
| none | 12 | 20 | 0.1409 | 0.1992 | 0.2053 | 0.2695 | 0.1847 | 0.1999 | 0.0207 | 0.3306 | 0.1307 | 65 | within one SE |
| balanced | 12 | 20 | 0.1318 | 0.1924 | 0.1964 | 0.2772 | 0.1859 | 0.1968 | 0.0233 | 0.3298 | 0.1331 | 66 |  |
| none | 14 | 20 | 0.1381 | 0.1915 | 0.2044 | 0.2658 | 0.1765 | 0.1953 | 0.0208 | 0.3560 | 0.1608 | 67 |  |
| none | 16 | 20 | 0.1372 | 0.1934 | 0.2034 | 0.2632 | 0.1734 | 0.1941 | 0.0206 | 0.3767 | 0.1826 | 68 |  |
| none | 18 | 20 | 0.1369 | 0.1921 | 0.2042 | 0.2614 | 0.1717 | 0.1933 | 0.0205 | 0.3909 | 0.1976 | 69 |  |
| balanced | 14 | 20 | 0.1319 | 0.1892 | 0.1954 | 0.2653 | 0.1804 | 0.1924 | 0.0214 | 0.3590 | 0.1665 | 70 |  |
| balanced | 16 | 20 | 0.1302 | 0.1883 | 0.1903 | 0.2674 | 0.1718 | 0.1896 | 0.0222 | 0.3824 | 0.1928 | 71 |  |
| balanced | 18 | 20 | 0.1304 | 0.1832 | 0.1879 | 0.2590 | 0.1679 | 0.1857 | 0.0209 | 0.4017 | 0.2160 | 72 |  |

### Full grid — forest (48 configurations)

Best mean clf.sel.log.forest\_clf.class\_weight=none.max\_depth=10.max\_features=sqrt.min\_samples\_leaf=20 = 0.2563 (SE 0.0267); one-SE bound 0.2295; one-SE choice clf.sel.log.forest\_clf.class\_weight=none.max\_depth=8.max\_features=sqrt.min\_samples\_leaf=200 = 0.2533. Against the plain s06 model: tuned paired gain -0.0012 (paired SE 0.0005), better in 1 of 5 folds; carried: plain (G-55). Grid edge: the one-SE choice sits at the edge of the grid for max\_depth = 8 (lowest value in the grid); min\_samples\_leaf = 200 (highest value in the grid) (the simpler end, where the one-SE rule moves the choice by design).

Effect of each parameter:

| parameter | value | configurations | best validation mean | mean over its configurations |
| --- | --- | --- | --- | --- |
| class\_weight | balanced | 24 | 0.2556 | 0.2540 |
| class\_weight | none | 24 | 0.2563 | 0.2548 |
| max\_depth | 10 | 8 | 0.2563 | 0.2543 |
| max\_depth | 12 | 8 | 0.2561 | 0.2542 |
| max\_depth | 14 | 8 | 0.2562 | 0.2546 |
| max\_depth | 16 | 8 | 0.2558 | 0.2546 |
| max\_depth | 18 | 8 | 0.2561 | 0.2546 |
| max\_depth | 8 | 8 | 0.2551 | 0.2539 |
| max\_features | sqrt | 48 | 0.2563 | 0.2544 |
| min\_samples\_leaf | 100 | 12 | 0.2562 | 0.2548 |
| min\_samples\_leaf | 20 | 12 | 0.2563 | 0.2554 |
| min\_samples\_leaf | 200 | 12 | 0.2535 | 0.2525 |
| min\_samples\_leaf | 50 | 12 | 0.2557 | 0.2547 |

Every configuration, ranked (per-fold validation, mean, SE, training mean, gap):

| class\_weight | max\_depth | max\_features | min\_samples\_leaf | val f1 | val f2 | val f3 | val f4 | val f5 | validation\_mean | validation\_se | train\_mean | train\_validation\_gap | rank | flags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| none | 10 | sqrt | 20 | 0.1755 | 0.2646 | 0.2628 | 0.3417 | 0.2368 | 0.2563 | 0.0267 | 0.2853 | 0.0290 | 1 | best mean; within one SE |
| none | 14 | sqrt | 100 | 0.1731 | 0.2677 | 0.2606 | 0.3393 | 0.2400 | 0.2562 | 0.0267 | 0.2457 | -0.0105 | 2 | within one SE |
| none | 12 | sqrt | 20 | 0.1757 | 0.2647 | 0.2640 | 0.3389 | 0.2372 | 0.2561 | 0.0263 | 0.3040 | 0.0479 | 3 | within one SE |
| none | 18 | sqrt | 20 | 0.1764 | 0.2655 | 0.2608 | 0.3373 | 0.2404 | 0.2561 | 0.0258 | 0.3491 | 0.0930 | 4 | within one SE |
| none | 16 | sqrt | 20 | 0.1749 | 0.2658 | 0.2616 | 0.3376 | 0.2392 | 0.2558 | 0.0261 | 0.3374 | 0.0816 | 5 | within one SE |
| none | 14 | sqrt | 20 | 0.1770 | 0.2652 | 0.2622 | 0.3363 | 0.2382 | 0.2558 | 0.0256 | 0.3217 | 0.0659 | 6 | within one SE |
| none | 14 | sqrt | 50 | 0.1733 | 0.2669 | 0.2602 | 0.3378 | 0.2402 | 0.2557 | 0.0264 | 0.2732 | 0.0176 | 7 | within one SE |
| balanced | 16 | sqrt | 20 | 0.1740 | 0.2654 | 0.2597 | 0.3379 | 0.2410 | 0.2556 | 0.0262 | 0.3414 | 0.0858 | 8 | within one SE |
| none | 18 | sqrt | 50 | 0.1746 | 0.2654 | 0.2604 | 0.3363 | 0.2408 | 0.2555 | 0.0259 | 0.2804 | 0.0249 | 9 | within one SE |
| none | 10 | sqrt | 100 | 0.1741 | 0.2682 | 0.2605 | 0.3361 | 0.2369 | 0.2552 | 0.0261 | 0.2399 | -0.0153 | 10 | within one SE |
| none | 16 | sqrt | 100 | 0.1724 | 0.2670 | 0.2607 | 0.3369 | 0.2385 | 0.2551 | 0.0264 | 0.2475 | -0.0076 | 11 | within one SE |
| none | 8 | sqrt | 20 | 0.1778 | 0.2653 | 0.2600 | 0.3371 | 0.2351 | 0.2551 | 0.0257 | 0.2626 | 0.0075 | 12 | within one SE |
| balanced | 12 | sqrt | 20 | 0.1726 | 0.2649 | 0.2594 | 0.3402 | 0.2381 | 0.2550 | 0.0269 | 0.3075 | 0.0524 | 13 | within one SE |
| none | 8 | sqrt | 50 | 0.1757 | 0.2656 | 0.2605 | 0.3384 | 0.2350 | 0.2550 | 0.0262 | 0.2459 | -0.0091 | 14 | within one SE |
| none | 18 | sqrt | 100 | 0.1723 | 0.2673 | 0.2606 | 0.3372 | 0.2376 | 0.2550 | 0.0265 | 0.2483 | -0.0067 | 15 | within one SE |
| balanced | 10 | sqrt | 20 | 0.1729 | 0.2653 | 0.2590 | 0.3388 | 0.2390 | 0.2550 | 0.0266 | 0.2854 | 0.0304 | 16 | within one SE |
| balanced | 16 | sqrt | 100 | 0.1731 | 0.2667 | 0.2567 | 0.3400 | 0.2383 | 0.2550 | 0.0268 | 0.2431 | -0.0118 | 17 | within one SE |
| none | 12 | sqrt | 50 | 0.1733 | 0.2658 | 0.2613 | 0.3378 | 0.2365 | 0.2549 | 0.0265 | 0.2649 | 0.0099 | 18 | within one SE |
| balanced | 18 | sqrt | 100 | 0.1730 | 0.2669 | 0.2581 | 0.3406 | 0.2360 | 0.2549 | 0.0270 | 0.2440 | -0.0109 | 19 | within one SE |
| balanced | 18 | sqrt | 20 | 0.1729 | 0.2650 | 0.2588 | 0.3382 | 0.2398 | 0.2549 | 0.0265 | 0.3536 | 0.0987 | 20 | within one SE |
| none | 16 | sqrt | 50 | 0.1718 | 0.2646 | 0.2614 | 0.3382 | 0.2384 | 0.2549 | 0.0267 | 0.2772 | 0.0223 | 21 | within one SE |
| balanced | 14 | sqrt | 100 | 0.1731 | 0.2673 | 0.2567 | 0.3395 | 0.2375 | 0.2548 | 0.0267 | 0.2415 | -0.0133 | 22 | within one SE |
| balanced | 10 | sqrt | 100 | 0.1732 | 0.2683 | 0.2565 | 0.3394 | 0.2366 | 0.2548 | 0.0268 | 0.2368 | -0.0180 | 23 | within one SE |
| none | 12 | sqrt | 100 | 0.1720 | 0.2682 | 0.2592 | 0.3370 | 0.2371 | 0.2547 | 0.0266 | 0.2425 | -0.0122 | 24 | within one SE |
| balanced | 16 | sqrt | 50 | 0.1723 | 0.2677 | 0.2579 | 0.3373 | 0.2382 | 0.2547 | 0.0265 | 0.2723 | 0.0176 | 25 | within one SE |
| balanced | 10 | sqrt | 50 | 0.1743 | 0.2657 | 0.2584 | 0.3383 | 0.2361 | 0.2545 | 0.0264 | 0.2539 | -0.0007 | 26 | within one SE |
| balanced | 18 | sqrt | 50 | 0.1723 | 0.2663 | 0.2577 | 0.3371 | 0.2392 | 0.2545 | 0.0264 | 0.2743 | 0.0198 | 27 | within one SE |
| balanced | 8 | sqrt | 20 | 0.1721 | 0.2656 | 0.2587 | 0.3393 | 0.2366 | 0.2545 | 0.0269 | 0.2636 | 0.0091 | 28 | within one SE |
| none | 10 | sqrt | 50 | 0.1724 | 0.2650 | 0.2596 | 0.3386 | 0.2365 | 0.2544 | 0.0267 | 0.2570 | 0.0025 | 29 | within one SE |
| balanced | 14 | sqrt | 20 | 0.1708 | 0.2649 | 0.2583 | 0.3380 | 0.2401 | 0.2544 | 0.0268 | 0.3259 | 0.0715 | 30 | within one SE |
| balanced | 8 | sqrt | 50 | 0.1770 | 0.2663 | 0.2579 | 0.3377 | 0.2329 | 0.2544 | 0.0260 | 0.2442 | -0.0102 | 31 | within one SE |
| balanced | 14 | sqrt | 50 | 0.1718 | 0.2663 | 0.2576 | 0.3373 | 0.2379 | 0.2542 | 0.0266 | 0.2680 | 0.0138 | 32 | within one SE |
| balanced | 12 | sqrt | 100 | 0.1715 | 0.2670 | 0.2558 | 0.3384 | 0.2379 | 0.2541 | 0.0268 | 0.2398 | -0.0143 | 33 | within one SE |
| balanced | 12 | sqrt | 50 | 0.1720 | 0.2651 | 0.2584 | 0.3373 | 0.2379 | 0.2541 | 0.0265 | 0.2640 | 0.0099 | 34 | within one SE |
| none | 8 | sqrt | 100 | 0.1707 | 0.2663 | 0.2591 | 0.3385 | 0.2342 | 0.2538 | 0.0271 | 0.2337 | -0.0201 | 35 | within one SE |
| balanced | 8 | sqrt | 100 | 0.1732 | 0.2665 | 0.2582 | 0.3377 | 0.2327 | 0.2537 | 0.0266 | 0.2319 | -0.0218 | 36 | within one SE |
| none | 18 | sqrt | 200 | 0.1702 | 0.2635 | 0.2574 | 0.3353 | 0.2409 | 0.2535 | 0.0264 | 0.2275 | -0.0259 | 37 | within one SE |
| none | 16 | sqrt | 200 | 0.1702 | 0.2637 | 0.2572 | 0.3355 | 0.2405 | 0.2534 | 0.0264 | 0.2275 | -0.0259 | 38 | within one SE |
| none | 8 | sqrt | 200 | 0.1711 | 0.2629 | 0.2575 | 0.3383 | 0.2366 | 0.2533 | 0.0268 | 0.2228 | -0.0305 | 39 | one-SE choice; within one SE |
| none | 14 | sqrt | 200 | 0.1702 | 0.2635 | 0.2568 | 0.3359 | 0.2394 | 0.2532 | 0.0265 | 0.2273 | -0.0258 | 40 | within one SE |
| none | 12 | sqrt | 200 | 0.1701 | 0.2634 | 0.2572 | 0.3356 | 0.2378 | 0.2528 | 0.0265 | 0.2265 | -0.0263 | 41 | within one SE |
| balanced | 14 | sqrt | 200 | 0.1696 | 0.2606 | 0.2561 | 0.3383 | 0.2383 | 0.2526 | 0.0269 | 0.2244 | -0.0281 | 42 | within one SE |
| none | 10 | sqrt | 200 | 0.1702 | 0.2630 | 0.2571 | 0.3352 | 0.2366 | 0.2524 | 0.0264 | 0.2255 | -0.0269 | 43 | within one SE |
| balanced | 16 | sqrt | 200 | 0.1695 | 0.2602 | 0.2554 | 0.3383 | 0.2378 | 0.2522 | 0.0270 | 0.2250 | -0.0273 | 44 | within one SE |
| balanced | 18 | sqrt | 200 | 0.1695 | 0.2601 | 0.2554 | 0.3382 | 0.2373 | 0.2521 | 0.0269 | 0.2249 | -0.0272 | 45 | within one SE |
| balanced | 12 | sqrt | 200 | 0.1696 | 0.2596 | 0.2556 | 0.3384 | 0.2364 | 0.2519 | 0.0270 | 0.2243 | -0.0277 | 46 | within one SE |
| balanced | 8 | sqrt | 200 | 0.1690 | 0.2604 | 0.2564 | 0.3369 | 0.2350 | 0.2515 | 0.0269 | 0.2209 | -0.0307 | 47 | within one SE |
| balanced | 10 | sqrt | 200 | 0.1688 | 0.2604 | 0.2553 | 0.3370 | 0.2357 | 0.2514 | 0.0269 | 0.2232 | -0.0283 | 48 | within one SE |

Round 2 (accepted) · run `20261021T042900Z` · 6 checks, all PASS. Round 2 differs from round 1 only in the validation-curve figures (dashed training lines now in their series colour); every table and value is unchanged. Coverage and review dropdowns are on the parent tab "s07 Tuning"; comment on any card here.

## 7.2 Logistic (classification)

**Approved solution:** LogisticRegression(C) with L2: 0.01, 0.1, 0.5, 1, 5, 10, 20, 50, 100; class\_weight: None, balanced

**What was done:** linear/logistic: 18 configurations; best mean 0.2553 ({'C': 0.01, 'class\_weight': None}); one-SE choice {"C": 0.01, "class\_weight": null} with 0.2553 ± 0.0294.

**Observation:** Against the plain s06 model (0.2435): paired gain of the tuned model +0.0118 (paired SE 0.0045), better in 5 of 5 folds; carried: plain model. For description only, the best-mean grid point against the plain model: paired gain +0.0118 (paired SE 0.0045), better in 5 of 5 folds.

**Reasoning:** The tuned configuration replaces the plain s06 model only if it beats it by more than one standard error of the fold means (G-55); otherwise the simpler plain model stays.

**Top 8 configurations by validation AP, plus the one-SE choice** (grid\_results.csv; 18 configurations):

| params | train\_mean | validation\_mean | validation\_se | train\_validation\_gap | rank | chosen\_in\_family |
| --- | --- | --- | --- | --- | --- | --- |
| {"C": 0.01, "class\_weight": null} | 0.2113 | 0.2553 | 0.0294 | -0.0440 | 1 | True |
| {"C": 0.01, "class\_weight": "balanced"} | 0.2122 | 0.2532 | 0.0296 | -0.0410 | 2 | False |
| {"C": 0.1, "class\_weight": null} | 0.2167 | 0.2506 | 0.0305 | -0.0339 | 3 | False |
| {"C": 0.1, "class\_weight": "balanced"} | 0.2162 | 0.2492 | 0.0302 | -0.0330 | 4 | False |
| {"C": 0.5, "class\_weight": null} | 0.2190 | 0.2481 | 0.0308 | -0.0292 | 5 | False |
| {"C": 1.0, "class\_weight": null} | 0.2196 | 0.2470 | 0.0310 | -0.0273 | 6 | False |
| {"C": 0.5, "class\_weight": "balanced"} | 0.2177 | 0.2466 | 0.0304 | -0.0288 | 7 | False |
| {"C": 1.0, "class\_weight": "balanced"} | 0.2182 | 0.2456 | 0.0304 | -0.0274 | 8 | False |

**Against the plain s06 model** (plain\_vs\_tuned.csv; paired figures are description only):

| plain\_mean | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | paired\_se | tuned\_better\_folds | carried | best\_mean | paired\_gain\_of\_best\_mean | best\_mean\_paired\_se | best\_mean\_better\_folds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.2435 | 0.2553 | 0.0294 | 0.0118 | 0.0045 | 5 | plain | 0.2553 | 0.0118 | 0.0045 | 5 |

&#91;image: Validation curve, linear/logistic, classification\]

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 18 configurations; single tree 72 configurations; forest 48 configurations)

**Files** (stages/s07\_tuning/classification/outputs/, run 20261021T040619Z): grid\_results.csv

## 7.3 Decision tree

**Approved solution:** max\_depth: 4, 5, 6, 8, 10, 12, 14, 16, 18 (includes the s06 depth 5; G-43); min\_samples\_leaf: 20, 50, 100, 200; classifier also class\_weight: None, balanced

**What was done:** single tree: 72 configurations; best mean 0.2216 ({'class\_weight': None, 'max\_depth': 10, 'min\_samples\_leaf': 200}); one-SE choice {"class\_weight": null, "max\_depth": 4, "min\_samples\_leaf": 200} with 0.2134 ± 0.0217.

**Observation:** Against the plain s06 model (0.2158): paired gain of the tuned model -0.0024 (paired SE 0.0022), better in 2 of 5 folds; carried: plain model. For description only, the best-mean grid point against the plain model: paired gain +0.0058 (paired SE 0.0037), better in 5 of 5 folds.

**Reasoning:** The tuned configuration replaces the plain s06 model only if it beats it by more than one standard error of the fold means (G-55); otherwise the simpler plain model stays.

**Top 8 configurations by validation AP, plus the one-SE choice** (grid\_results.csv; 72 configurations):

| params | train\_mean | validation\_mean | validation\_se | train\_validation\_gap | rank | chosen\_in\_family |
| --- | --- | --- | --- | --- | --- | --- |
| {"class\_weight": null, "max\_depth": 10, "min\_samples\_leaf": 200} | 0.2293 | 0.2216 | 0.0230 | 0.0077 | 1 | False |
| {"class\_weight": null, "max\_depth": 8, "min\_samples\_leaf": 200} | 0.2224 | 0.2211 | 0.0227 | 0.0013 | 2 | False |
| {"class\_weight": null, "max\_depth": 12, "min\_samples\_leaf": 200} | 0.2325 | 0.2206 | 0.0229 | 0.0119 | 3 | False |
| {"class\_weight": null, "max\_depth": 14, "min\_samples\_leaf": 200} | 0.2340 | 0.2203 | 0.0228 | 0.0136 | 4 | False |
| {"class\_weight": null, "max\_depth": 18, "min\_samples\_leaf": 200} | 0.2350 | 0.2202 | 0.0227 | 0.0148 | 5 | False |
| {"class\_weight": null, "max\_depth": 16, "min\_samples\_leaf": 200} | 0.2345 | 0.2201 | 0.0227 | 0.0144 | 6 | False |
| {"class\_weight": "balanced", "max\_depth": 6, "min\_samples\_leaf": 200} | 0.2110 | 0.2193 | 0.0228 | -0.0084 | 7 | False |
| {"class\_weight": "balanced", "max\_depth": 10, "min\_samples\_leaf": 200} | 0.2288 | 0.2192 | 0.0228 | 0.0096 | 8 | False |
| {"class\_weight": null, "max\_depth": 4, "min\_samples\_leaf": 200} | 0.1934 | 0.2134 | 0.0217 | -0.0200 | 25 | True |

**Against the plain s06 model** (plain\_vs\_tuned.csv; paired figures are description only):

| plain\_mean | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | paired\_se | tuned\_better\_folds | carried | best\_mean | paired\_gain\_of\_best\_mean | best\_mean\_paired\_se | best\_mean\_better\_folds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.2158 | 0.2134 | 0.0217 | -0.0024 | 0.0022 | 2 | plain | 0.2216 | 0.0058 | 0.0037 | 5 |

&#91;image: Validation curve, single tree, classification\]

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 18 configurations; single tree 72 configurations; forest 48 configurations) **Check** the grid point with the s06 plain settings reproduces the s06 fold scores (tree, forest): PASS (2 of 2 reproduced)

**Files** (stages/s07\_tuning/classification/outputs/, run 20261021T040619Z): grid\_results.csv

## 7.4 Random forest

**Approved solution:** 200 trees; max\_depth: 8, 10, 12, 14, 16, 18; min\_samples\_leaf: 20, 50, 100, 200 (forest grid unchanged by G-43); max\_features: sqrt; classifier also class\_weight: None, balanced

**What was done:** forest: 48 configurations; best mean 0.2563 ({'class\_weight': None, 'max\_depth': 10, 'max\_features': 'sqrt', 'min\_samples\_leaf': 20}); one-SE choice {"class\_weight": null, "max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 200} with 0.2533 ± 0.0268.

**Observation:** Against the plain s06 model (0.2544): paired gain of the tuned model -0.0012 (paired SE 0.0005), better in 1 of 5 folds; carried: plain model. For description only, the best-mean grid point against the plain model: paired gain +0.0019 (paired SE 0.0008), better in 4 of 5 folds.

**Reasoning:** The tuned configuration replaces the plain s06 model only if it beats it by more than one standard error of the fold means (G-55); otherwise the simpler plain model stays.

**Top 8 configurations by validation AP, plus the one-SE choice** (grid\_results.csv; 48 configurations):

| params | train\_mean | validation\_mean | validation\_se | train\_validation\_gap | rank | chosen\_in\_family |
| --- | --- | --- | --- | --- | --- | --- |
| {"class\_weight": null, "max\_depth": 10, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.2853 | 0.2563 | 0.0267 | 0.0290 | 1 | False |
| {"class\_weight": null, "max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 100} | 0.2457 | 0.2562 | 0.0267 | -0.0105 | 2 | False |
| {"class\_weight": null, "max\_depth": 12, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.3040 | 0.2561 | 0.0263 | 0.0479 | 3 | False |
| {"class\_weight": null, "max\_depth": 18, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.3491 | 0.2561 | 0.0258 | 0.0930 | 4 | False |
| {"class\_weight": null, "max\_depth": 16, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.3374 | 0.2558 | 0.0261 | 0.0816 | 5 | False |
| {"class\_weight": null, "max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.3217 | 0.2558 | 0.0256 | 0.0659 | 6 | False |
| {"class\_weight": null, "max\_depth": 14, "max\_features": "sqrt", "min\_samples\_leaf": 50} | 0.2732 | 0.2557 | 0.0264 | 0.0176 | 7 | False |
| {"class\_weight": "balanced", "max\_depth": 16, "max\_features": "sqrt", "min\_samples\_leaf": 20} | 0.3414 | 0.2556 | 0.0262 | 0.0858 | 8 | False |
| {"class\_weight": null, "max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 0.2228 | 0.2533 | 0.0268 | -0.0305 | 39 | True |

**Against the plain s06 model** (plain\_vs\_tuned.csv; paired figures are description only):

| plain\_mean | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | paired\_se | tuned\_better\_folds | carried | best\_mean | paired\_gain\_of\_best\_mean | best\_mean\_paired\_se | best\_mean\_better\_folds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0.2544 | 0.2533 | 0.0268 | -0.0012 | 0.0005 | 1 | plain | 0.2563 | 0.0019 | 0.0008 | 4 |

&#91;image: Validation curve, forest, classification\]

**Check** every configuration comes from the pre-registered protocol.yaml grids (s01, before any s07 output): PASS (linear/logistic 18 configurations; single tree 72 configurations; forest 48 configurations) **Check** the grid point with the s06 plain settings reproduces the s06 fold scores (tree, forest): PASS (2 of 2 reproduced)

**Files** (stages/s07\_tuning/classification/outputs/, run 20261021T040619Z): grid\_results.csv

## 7.5 Search method

**Approved solution:** GridSearchCV over the full Pipeline with cv = the s05 fold iterator, scoring = the primary metric (neg MAE, average precision), refit=False, return\_train\_score=True, seed 42. Best per family = the simplest configuration within one standard error of the best mean (s01 1.7). Simpler means higher alpha, lower C, shallower depth, then larger leaf. It is then compared with the family's plain s06 model by the same one-SE rule: if the plain model's mean is within one SE of the tuned configuration's mean, the plain model is kept (G-55)

**What was done:** GridSearchCV over the whole s04 pipeline on the s05 folds, scoring average\_precision, refit=False, return\_train\_score=True, seed 42; 138 configurations in total. Carried per family: linear/logistic plain s06; single tree plain s06; forest plain s06. Ladder over the carried families (description only; s08 decides): linear/logistic kept over dummy (paired gain +0.0953, better in 5 of 5 folds); single tree not kept over linear/logistic (paired gain -0.0277, better in 0 of 5 folds); forest not kept over linear/logistic (paired gain +0.0109, better in 4 of 5 folds); result linear/logistic.

**Conclusion:** Selection scores on the folds, not generalisation estimates (G-10). The finalists and the final choice are made in s08 at its gate (G-39).

**Plain vs tuned per family** (plain\_vs\_tuned.csv):

| family | plain\_mean | tuned\_mean | tuned\_se | paired\_gain\_of\_tuned | tuned\_better\_folds | carried |
| --- | --- | --- | --- | --- | --- | --- |
| linear/logistic | 0.2435 | 0.2553 | 0.0294 | 0.0118 | 5 | plain |
| single tree | 0.2158 | 0.2134 | 0.0217 | -0.0024 | 2 | plain |
| forest | 0.2544 | 0.2533 | 0.0268 | -0.0012 | 1 | plain |

**Ladder over the carried families** (ladder\_preview.csv; description only, s08 chooses):

| comparison | mean\_gain | paired\_se | folds\_better | kept\_by\_one\_se\_rule |
| --- | --- | --- | --- | --- |
| linear/logistic vs dummy | 0.0953 | 0.0157 | 5 | True |
| single tree vs linear/logistic | -0.0277 | 0.0115 | 0 | False |
| forest vs linear/logistic | 0.0109 | 0.0063 | 4 | False |

**Check** same folds as s06 (rows per fold equal): PASS **Check** every configuration scored on all five folds, whole pipeline refitted per fold: PASS **Check** no test row read: every row used was purchased before the test cutoff: PASS (latest purchase 2018-05-26 12:12:15, cutoff 2018-05-26 12:16:34)

**Files** (stages/s07\_tuning/classification/outputs/, run 20261021T040619Z): candidates.csv, counts.json, decision.json, grid\_results.csv, ladder\_preview.csv, plain\_vs\_tuned.csv

## 7.6 Overfitting check

**Approved solution:** For each configuration report the train–validation gap; flag the best configuration if the gap is large and a simpler one is within the decision rule

**What was done:** train\_validation\_gap for every configuration in grid\_results.csv (positive = worse on validation). Gap of each family's one-SE choice: linear/logistic -0.0440; single tree -0.0200; forest -0.0305.

**Reasoning:** The one-SE choice is already the simplest configuration within the rule, so no simpler configuration within the rule exists to flag; the gaps are reported for the review.

**Gap of each family's one-SE choice** (grid\_results.csv):

| family | params | train\_mean | validation\_mean | train\_validation\_gap |
| --- | --- | --- | --- | --- |
| linear | {"C": 0.01, "class\_weight": null} | 0.2113 | 0.2553 | -0.0440 |
| tree | {"class\_weight": null, "max\_depth": 4, "min\_samples\_leaf": 200} | 0.1934 | 0.2134 | -0.0200 |
| forest | {"class\_weight": null, "max\_depth": 8, "max\_features": "sqrt", "min\_samples\_leaf": 200} | 0.2228 | 0.2533 | -0.0305 |

**Files** (stages/s07\_tuning/classification/outputs/, run 20261021T040619Z): curves/validation\_curve\_forest.csv, curves/validation\_curve\_linear.csv, curves/validation\_curve\_tree.csv, figures/validation\_curve\_forest.csv, figures/validation\_curve\_forest.png, figures/validation\_curve\_linear.csv, figures/validation\_curve\_linear.png, figures/validation\_curve\_tree.csv, figures/validation\_curve\_tree.png, grid\_results.csv

## 7.7 Outputs

**Approved solution:** grid\_results.csv (every configuration: parameters, per-fold train and validation scores, mean, SD, rank, fit time, convergence), out-of-fold predictions of each family's best, kept separate as pooled OOF vs mean-fold scores

**What was done:** grid\_results.csv, plain\_vs\_tuned.csv, ladder\_preview.csv, candidates.csv, decision.json, out-of-fold predictions of each family's best (predictions.csv.gz) with pooled vs mean-fold scores (oof\_scores.csv), validation curves (curves/, figures/); fit times in \_manifest.json.

**Out-of-fold scores of each family's one-SE choice, pooled vs mean-fold** (oof\_scores.csv):

| family | mean\_fold\_ap | pooled\_oof\_ap | pooled\_oof\_roc\_auc | pooled\_oof\_brier |
| --- | --- | --- | --- | --- |
| linear/logistic | 0.2553 | 0.2394 | 0.6132 | 0.1249 |
| single tree | 0.2134 | 0.2182 | 0.5772 | 0.1253 |
| forest | 0.2533 | 0.2396 | 0.6174 | 0.1253 |

**Check** refitting each family's best per fold gives the grid's validation scores: PASS (15 refits)

**Files** (stages/s07\_tuning/classification/outputs/, run 20261021T040619Z): counts.json, oof\_scores.csv, predictions.csv.gz
