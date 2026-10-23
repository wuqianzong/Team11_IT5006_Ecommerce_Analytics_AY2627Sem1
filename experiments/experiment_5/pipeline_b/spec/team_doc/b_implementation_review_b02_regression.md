# B2 › regression — evidence cards

Round 2 (B-G-03, B-G-04; built, not yet committed) · run `20261023T153736Z` on uncommitted code (working tree on aed9cfa) · 7 checks, all PASS. Coverage and review dropdowns are on the parent tab "B2 Population and features"; comment on any card here.

## B2.1 Population (B-C1 to B-C5)

**Approved solution (B2 blueprint):** Population (B-C1 to B-C5), applied to A's task-eligible rows, each removal with a reason code in `exclusions\_B.csv`: - B\_STATE: customer or primary seller state outside SP, MG, RJ, PR, RS, BA, SC, or missing; - B\_DISTANCE: distance\_km\_max missing; - B\_LEAD\_CAP (regression): lead\_days > mean + 8 × SD of lead\_days on B's own development rows after B\_STATE and B\_DISTANCE (B-G-03; computed each run, recorded in feature\_build\_log.json; no floor); - B\_NO\_HANDOVER (classification): no carrier handover date; - B\_REVIEW\_BEFORE\_HANDOVER (classification): review answered at or before handover; - B\_WARMUP: purchased before 2017-02-12 (first six weeks), removed after the features are built.

**What was done:** From 76,925 A development rows (s02, eligible, before the cutoff) to 61,233 B rows. Removed: B\_STATE 13,777; B\_DISTANCE 606; B\_LEAD\_CAP 45; B\_WARMUP 1,264.

**Rows by step** (exclusion\_counts\_B.csv):

| step | rows |
| --- | --- |
| A development rows (s02, pre-cutoff, eligible) | 76,925 |
| removed: B\_STATE | 13,777 |
| removed: B\_DISTANCE | 606 |
| removed: B\_LEAD\_CAP | 45 |
| removed: B\_WARMUP | 1,264 |
| B development rows | 61,233 |

**Check** B development rows are a subset of A's eligible pre-cutoff rows: PASS (61,233 of 76,925) **Check** removal counts add up: A rows = B rows + removed: PASS (76,925 = 61,233 + 15,692) **Check** lead-time cap applied: no B row above mean + 8 SD of B's own rows after the scope and distance rules: PASS (cap 83.66 days; longest B lead time 83.63)

**Files** (pipeline\_b/stages/b02/regression/outputs/, run 20261023T153736Z): exclusion\_counts\_B.csv, exclusions\_B.csv, records\_B.csv.gz

## B2.2 Prediction time

**Approved solution (B2 blueprint):** Prediction time. Regression: purchase time. Classification: carrier handover time.

**What was done:** Prediction time: purchase time (checkout).

**Prediction time span** (records\_B.csv.gz): 2017-02-12 00:20:45 to 2018-05-27 12:20:21; 68 prediction weeks.

**Files** (pipeline\_b/stages/b02/regression/outputs/, run 20261023T153736Z): records\_B.csv.gz

## B2.3 Events

**Approved solution (B2 blueprint):** Events. One row per raw order purchased before the task's test cutoff: primary seller (highest price, then lowest item id, A's rule), last shipping limit, carrier date, delivery date, route = seller\_state + "->" + customer\_state. The estimated delivery date column is dropped on load.

**What was done:** 79,137 raw orders purchased before the cutoff 2018-05-27 12:30:34; primary seller by A's rule (highest price, then lowest item id); the estimated delivery date column is not read.

**Events** (feature\_build\_log.json): 79,137 raw orders purchased before the cutoff 2018-05-27 12:30:34.

**Check** no column from the estimated delivery date: PASS **Check** seller state from the raw tables equals A's primary\_seller\_state: PASS

**Files** (pipeline\_b/stages/b02/regression/outputs/, run 20261023T153736Z): feature\_build\_log.json

## B2.4 Weeks and leakage rule

**Approved solution (B2 blueprint):** Weeks. Calendar weeks, Monday to Sunday. A handover event counts in its carrier-date week; a delivery event in its delivery week. A row uses only complete weeks before its prediction week.

**What was done:** Calendar weeks from Monday 2016-01-04; handover events in their carrier-date week, delivery events in their delivery week; a row uses only weeks before its prediction week.

**Settings** (feature\_build\_log.json): weights 0.5, 0.3, 0.2 for weeks w−1, w−2, w−3; at least 10 route events over 3 weeks; state mix 0.7 / 0.3 (seller state / customer state).

**Check** leakage re-check: features recomputed by brute force from events in weeks before the prediction week match: PASS (300 rows, max difference 0.00e+00)

**Files** (pipeline\_b/stages/b02/regression/outputs/, run 20261023T153736Z): feature\_build\_log.json

## B2.5 History features (B-C6 to B-C9)

**Approved solution (B2 blueprint):** Features (B-C6 to B-C9), all candidates for both tasks unless stated: Feature names (B-G-04) are in brackets. - route (categorical) \[route\_seller\_to\_customer\_state\]; - prior seller late-handover rate, prior seller late-handover days, prior seller dispatch days (B-C7) \[seller\_prior\_late\_handover\_rate, seller\_prior\_late\_handover\_days, seller\_prior\_dispatch\_days\]: mean over all of the seller's earlier handover weeks; a seller with no history takes the weighted 3-week mean of sellers in the same seller state; - recent route delivery days (B-C8) and recent route carrier transit days (B-C8b) \[route\_recent\_delivery\_days, route\_recent\_carrier\_transit\_days\]: weighted 3-week mean (0.5, 0.3, 0.2 for weeks w−1, w−2, w−3) of the route's weekly median, the weights renormalised over the weeks that have events; fewer than 10 route events in the 3 weeks → 0.7 × seller state's + 0.3 × customer state's weighted 3-week mean, then the overall one; - classification only (B-C9): this order's handover late flag, late days and dispatch days \[order\_handed\_over\_late, order\_handover\_late\_days, order\_dispatch\_days\].

**What was done:** Features built: route\_seller\_to\_customer\_state, seller\_prior\_late\_handover\_rate, seller\_prior\_late\_handover\_days, seller\_prior\_dispatch\_days, route\_recent\_delivery\_days, route\_recent\_carrier\_transit\_days. History sources: seller\_prior: own seller history 95.9%, seller-state fallback 4.1%; route\_recent\_delivery\_days: own route history 95.9%, state-mix fallback 4.1%; route\_recent\_carrier\_transit\_days: own route history 95.9%, state-mix fallback 4.1%.

**Feature distributions** (computed from records\_B.csv.gz):

| feature | count | mean | 10% | 50% | 90% | missing\_share |
| --- | --- | --- | --- | --- | --- | --- |
| seller\_prior\_late\_handover\_rate | 61,233 | 0.0845 | 0.0000 | 0.0394 | 0.2353 | 0.0000 |
| seller\_prior\_late\_handover\_days | 61,233 | 0.2913 | 0.0000 | 0.0588 | 0.6718 | 0.0000 |
| seller\_prior\_dispatch\_days | 61,233 | 3.2439 | 1.5955 | 2.8761 | 5.1947 | 0.0000 |
| route\_recent\_delivery\_days | 61,233 | 10.7892 | 6.5083 | 9.8434 | 16.8036 | 0.0000 |
| route\_recent\_carrier\_transit\_days | 61,233 | 7.6229 | 3.4855 | 6.9579 | 13.3071 | 0.0000 |

**History source by quarter** (history\_coverage.csv; share of rows using own history vs a fallback):

| feature | quarter | own route history | own seller history | seller-state fallback | state-mix fallback |
| --- | --- | --- | --- | --- | --- |
| route\_recent\_carrier\_transit\_days | 2017Q1 | 0.859 | 0.000 | 0.000 | 0.141 |
| route\_recent\_carrier\_transit\_days | 2017Q2 | 0.929 | 0.000 | 0.000 | 0.071 |
| route\_recent\_carrier\_transit\_days | 2017Q3 | 0.948 | 0.000 | 0.000 | 0.052 |
| route\_recent\_carrier\_transit\_days | 2017Q4 | 0.960 | 0.000 | 0.000 | 0.040 |
| route\_recent\_carrier\_transit\_days | 2018Q1 | 0.979 | 0.000 | 0.000 | 0.021 |
| route\_recent\_carrier\_transit\_days | 2018Q2 | 0.982 | 0.000 | 0.000 | 0.018 |
| route\_recent\_delivery\_days | 2017Q1 | 0.859 | 0.000 | 0.000 | 0.141 |
| route\_recent\_delivery\_days | 2017Q2 | 0.929 | 0.000 | 0.000 | 0.071 |
| route\_recent\_delivery\_days | 2017Q3 | 0.948 | 0.000 | 0.000 | 0.052 |
| route\_recent\_delivery\_days | 2017Q4 | 0.960 | 0.000 | 0.000 | 0.040 |
| route\_recent\_delivery\_days | 2018Q1 | 0.979 | 0.000 | 0.000 | 0.021 |
| route\_recent\_delivery\_days | 2018Q2 | 0.982 | 0.000 | 0.000 | 0.018 |
| seller\_prior | 2017Q1 | 0.000 | 0.891 | 0.109 | 0.000 |
| seller\_prior | 2017Q2 | 0.000 | 0.956 | 0.044 | 0.000 |
| seller\_prior | 2017Q3 | 0.000 | 0.957 | 0.043 | 0.000 |
| seller\_prior | 2017Q4 | 0.000 | 0.964 | 0.036 | 0.000 |
| seller\_prior | 2018Q1 | 0.000 | 0.970 | 0.030 | 0.000 |
| seller\_prior | 2018Q2 | 0.000 | 0.959 | 0.041 | 0.000 |

**Lateness summary, ten busiest routes** (aggregated from lateness\_summary\_B.csv.gz, which holds every route × week × seller; seven-state routes only (B-G-03), events before the cutoff; descriptive only, for Henry's lateness page):

| route (seller state -> customer state) | handovers | late\_handover\_rate | late\_handover\_days | median\_of\_weekly\_carrier\_transit\_medians |
| --- | --- | --- | --- | --- |
| SP->SP | 24,123 | 0.092 | 0.267 | 3.944 |
| SP->RJ | 7,000 | 0.103 | 0.336 | 10.050 |
| SP->MG | 6,194 | 0.098 | 0.245 | 8.009 |
| SP->RS | 3,010 | 0.078 | 0.219 | 11.740 |
| SP->PR | 2,549 | 0.088 | 0.294 | 8.181 |
| PR->SP | 2,343 | 0.113 | 0.612 | 6.864 |
| MG->SP | 2,130 | 0.082 | 0.361 | 7.027 |
| SP->SC | 1,970 | 0.091 | 0.279 | 11.356 |
| SP->BA | 1,907 | 0.085 | 0.203 | 15.106 |
| MG->MG | 1,205 | 0.080 | 0.341 | 5.145 |

**Check** leakage re-check: features recomputed by brute force from events in weeks before the prediction week match: PASS (300 rows, max difference 0.00e+00)

**Files** (pipeline\_b/stages/b02/regression/outputs/, run 20261023T153736Z): feature\_build\_log.json, history\_coverage.csv, lateness\_summary\_B.csv.gz, records\_B.csv.gz

## B2.6 Test rows

**Approved solution (B2 blueprint):** Test rows. B2 builds features for development rows only. Test-row features are built in the joint test run, from events known before each test row's prediction week.

**What was done:** Development rows only; test-row features are built in the joint test run.

**Latest purchase in B rows** (records\_B.csv.gz): 2018-05-27 12:20:21; test cutoff 2018-05-27 12:30:34.

**Check** no test row: every B row purchased before the test cutoff: PASS (latest purchase 2018-05-27 12:20:21, cutoff 2018-05-27 12:30:34)

**Files** (pipeline\_b/stages/b02/regression/outputs/, run 20261023T153736Z):

# Round 1 cards (superseded by round 2, kept for the record)

Run 20261023T134738Z on commit 2991253 (tag e5-B-s02-accepted). Old feature names and the cap from A's orders.

## B2.1 Population (B-C1 to B-C5)

**Approved solution (B2 blueprint):** Population (B-C1 to B-C5), applied to A's task-eligible rows, each removal with a reason code in `exclusions\_B.csv`: - B\_STATE: customer or primary seller state outside SP, MG, RJ, PR, RS, BA, SC, or missing; - B\_DISTANCE: distance\_km\_max missing; - B\_LEAD\_CAP (regression): lead\_days > 93.63 (mean + 8 × SD of A's s02 pre-cutoff orders, audit.json; no floor); - B\_NO\_HANDOVER (classification): no carrier handover date; - B\_REVIEW\_BEFORE\_HANDOVER (classification): review answered at or before handover; - B\_WARMUP: purchased before 2017-02-12 (first six weeks), removed after the features are built.

**What was done:** From 76,925 A development rows (s02, eligible, before the cutoff) to 61,245 B rows. Removed: B\_STATE 13,777; B\_DISTANCE 606; B\_LEAD\_CAP 32; B\_WARMUP 1,265.

**Rows by step** (exclusion\_counts\_B.csv):

| step | rows |
| --- | --- |
| A development rows (s02, pre-cutoff, eligible) | 76,925 |
| removed: B\_STATE | 13,777 |
| removed: B\_DISTANCE | 606 |
| removed: B\_LEAD\_CAP | 32 |
| removed: B\_WARMUP | 1,265 |
| B development rows | 61,245 |

**Check** B development rows are a subset of A's eligible pre-cutoff rows: PASS (61,245 of 76,925) **Check** removal counts add up: A rows = B rows + removed: PASS (76,925 = 61,245 + 15,680) **Check** lead-time cap applied: no B row above mean + 8 SD of A's s02 pre-cutoff orders (audit.json): PASS (cap 93.63 days; longest B lead time 88.24)

**Files** (pipeline\_b/stages/b02/regression/outputs/, run 20261023T134738Z): exclusion\_counts\_B.csv, exclusions\_B.csv, records\_B.csv.gz

## B2.2 Prediction time

**Approved solution (B2 blueprint):** Prediction time. Regression: purchase time. Classification: carrier handover time.

**What was done:** Prediction time: purchase time (checkout).

**Prediction time span** (records\_B.csv.gz): 2017-02-12 00:20:45 to 2018-05-27 12:20:21; 68 prediction weeks.

**Files** (pipeline\_b/stages/b02/regression/outputs/, run 20261023T134738Z): records\_B.csv.gz

## B2.3 Events

**Approved solution (B2 blueprint):** Events. One row per raw order purchased before the task's test cutoff: primary seller (highest price, then lowest item id, A's rule), last shipping limit, carrier date, delivery date, route = customer\_state + "->" + seller\_state. The estimated delivery date column is dropped on load.

**What was done:** 79,137 raw orders purchased before the cutoff 2018-05-27 12:30:34; primary seller by A's rule (highest price, then lowest item id); the estimated delivery date column is not read.

**Events** (feature\_build\_log.json): 79,137 raw orders purchased before the cutoff 2018-05-27 12:30:34.

**Check** no column from the estimated delivery date: PASS **Check** seller state from the raw tables equals A's primary\_seller\_state: PASS

**Files** (pipeline\_b/stages/b02/regression/outputs/, run 20261023T134738Z): feature\_build\_log.json

## B2.4 Weeks and leakage rule

**Approved solution (B2 blueprint):** Weeks. Calendar weeks, Monday to Sunday. A handover event counts in its carrier-date week; a delivery event in its delivery week. A row uses only complete weeks before its prediction week.

**What was done:** Calendar weeks from Monday 2016-01-04; handover events in their carrier-date week, delivery events in their delivery week; a row uses only weeks before its prediction week.

**Settings** (feature\_build\_log.json): weights 0.5, 0.3, 0.2 for weeks w−1, w−2, w−3; at least 10 route events over 3 weeks; state mix 0.7 / 0.3 (seller state / customer state).

**Check** leakage re-check: features recomputed by brute force from events in weeks before the prediction week match: PASS (300 rows, max difference 0.00e+00)

**Files** (pipeline\_b/stages/b02/regression/outputs/, run 20261023T134738Z): feature\_build\_log.json

## B2.5 History features (B-C6 to B-C9)

**Approved solution (B2 blueprint):** Features (B-C6 to B-C9), all candidates for both tasks unless stated: - route (categorical); - prior seller late rate, prior seller late days, prior seller dispatch days (B-C7): mean over all of the seller's earlier handover weeks; a seller with no history takes the weighted 3-week mean of sellers in the same seller state; - route lead days (B-C8) and route transit days (B-C8b): weighted 3-week mean (0.5, 0.3, 0.2 for weeks w−1, w−2, w−3) of the route's weekly median, the weights renormalised over the weeks that have events; fewer than 10 route events in the 3 weeks → 0.7 × seller state's + 0.3 × customer state's weighted 3-week mean, then the overall one; - classification only (B-C9): this order's handover late flag, late days and dispatch days.

**What was done:** Features built: b\_seller\_late\_rate, b\_seller\_late\_days, b\_seller\_dispatch\_days, b\_route\_lead\_days, b\_route\_transit\_days, route. History sources: b\_seller: seller 95.9%, seller\_state 4.1%; b\_route\_lead\_days: route 95.9%, state\_mix 4.1%; b\_route\_transit\_days: route 95.9%, state\_mix 4.1%.

**Feature distributions** (computed from records\_B.csv.gz):

| feature | count | mean | 10% | 50% | 90% | missing\_share |
| --- | --- | --- | --- | --- | --- | --- |
| b\_seller\_late\_rate | 61,245 | 0.0845 | 0.0000 | 0.0394 | 0.2353 | 0.0000 |
| b\_seller\_late\_days | 61,245 | 0.2913 | 0.0000 | 0.0588 | 0.6718 | 0.0000 |
| b\_seller\_dispatch\_days | 61,245 | 3.2440 | 1.5955 | 2.8761 | 5.1947 | 0.0000 |
| b\_route\_lead\_days | 61,245 | 10.7902 | 6.5083 | 9.8434 | 16.8036 | 0.0000 |
| b\_route\_transit\_days | 61,245 | 7.6238 | 3.4855 | 6.9579 | 13.3071 | 0.0000 |

**History source by quarter** (history\_coverage.csv; share of rows using own history vs a fallback):

| feature | quarter | route | seller | seller\_state | state\_mix |
| --- | --- | --- | --- | --- | --- |
| b\_route\_lead\_days | 2017Q1 | 0.859 | 0.000 | 0.000 | 0.141 |
| b\_route\_lead\_days | 2017Q2 | 0.929 | 0.000 | 0.000 | 0.071 |
| b\_route\_lead\_days | 2017Q3 | 0.948 | 0.000 | 0.000 | 0.052 |
| b\_route\_lead\_days | 2017Q4 | 0.960 | 0.000 | 0.000 | 0.040 |
| b\_route\_lead\_days | 2018Q1 | 0.979 | 0.000 | 0.000 | 0.021 |
| b\_route\_lead\_days | 2018Q2 | 0.982 | 0.000 | 0.000 | 0.018 |
| b\_route\_transit\_days | 2017Q1 | 0.859 | 0.000 | 0.000 | 0.141 |
| b\_route\_transit\_days | 2017Q2 | 0.929 | 0.000 | 0.000 | 0.071 |
| b\_route\_transit\_days | 2017Q3 | 0.948 | 0.000 | 0.000 | 0.052 |
| b\_route\_transit\_days | 2017Q4 | 0.960 | 0.000 | 0.000 | 0.040 |
| b\_route\_transit\_days | 2018Q1 | 0.979 | 0.000 | 0.000 | 0.021 |
| b\_route\_transit\_days | 2018Q2 | 0.982 | 0.000 | 0.000 | 0.018 |
| b\_seller | 2017Q1 | 0.000 | 0.891 | 0.109 | 0.000 |
| b\_seller | 2017Q2 | 0.000 | 0.956 | 0.044 | 0.000 |
| b\_seller | 2017Q3 | 0.000 | 0.957 | 0.043 | 0.000 |
| b\_seller | 2017Q4 | 0.000 | 0.964 | 0.036 | 0.000 |
| b\_seller | 2018Q1 | 0.000 | 0.971 | 0.029 | 0.000 |
| b\_seller | 2018Q2 | 0.000 | 0.958 | 0.042 | 0.000 |

**Lateness summary, ten busiest routes** (aggregated from lateness\_summary\_B.csv.gz, which holds every route × week × seller; all states, events before the cutoff; descriptive only, for Henry's lateness page):

| route | handovers | seller\_late\_rate | seller\_late\_days | median\_of\_weekly\_transit\_medians |
| --- | --- | --- | --- | --- |
| SP->SP | 24,123 | 0.092 | 0.267 | 3.944 |
| RJ->SP | 7,000 | 0.103 | 0.336 | 10.050 |
| MG->SP | 6,194 | 0.098 | 0.245 | 8.009 |
| RS->SP | 3,010 | 0.078 | 0.219 | 11.740 |
| PR->SP | 2,549 | 0.088 | 0.294 | 8.181 |
| SP->PR | 2,343 | 0.113 | 0.612 | 6.864 |
| SP->MG | 2,130 | 0.082 | 0.361 | 7.027 |
| SC->SP | 1,970 | 0.091 | 0.279 | 11.356 |
| BA->SP | 1,907 | 0.085 | 0.203 | 15.106 |
| GO->SP | 1,206 | 0.080 | 0.233 | 11.986 |

**Check** leakage re-check: features recomputed by brute force from events in weeks before the prediction week match: PASS (300 rows, max difference 0.00e+00)

**Files** (pipeline\_b/stages/b02/regression/outputs/, run 20261023T134738Z): feature\_build\_log.json, history\_coverage.csv, lateness\_summary\_B.csv.gz, records\_B.csv.gz

## B2.6 Test rows

**Approved solution (B2 blueprint):** Test rows. B2 builds features for development rows only. Test-row features are built in the joint test run, from events known before each test row's prediction week.

**What was done:** Development rows only; test-row features are built in the joint test run.

**Latest purchase in B rows** (records\_B.csv.gz): 2018-05-27 12:20:21; test cutoff 2018-05-27 12:30:34.

**Check** no test row: every B row purchased before the test cutoff: PASS (latest purchase 2018-05-27 12:20:21, cutoff 2018-05-27 12:30:34)

**Files** (pipeline\_b/stages/b02/regression/outputs/, run 20261023T134738Z):
