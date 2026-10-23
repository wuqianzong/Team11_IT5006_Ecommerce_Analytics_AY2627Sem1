# B2 › classification — evidence cards

Round 2 (B-G-03, B-G-04; built, not yet committed) · run `20261023T153744Z` on uncommitted code (working tree on aed9cfa) · 6 checks, all PASS. Coverage and review dropdowns are on the parent tab "B2 Population and features"; comment on any card here.

## B2.1 Population (B-C1 to B-C5)

**Approved solution (B2 blueprint):** Population (B-C1 to B-C5), applied to A's task-eligible rows, each removal with a reason code in `exclusions\_B.csv`: - B\_STATE: customer or primary seller state outside SP, MG, RJ, PR, RS, BA, SC, or missing; - B\_DISTANCE: distance\_km\_max missing; - B\_LEAD\_CAP (regression): lead\_days > mean + 8 × SD of lead\_days on B's own development rows after B\_STATE and B\_DISTANCE (B-G-03; computed each run, recorded in feature\_build\_log.json; no floor); - B\_NO\_HANDOVER (classification): no carrier handover date; - B\_REVIEW\_BEFORE\_HANDOVER (classification): review answered at or before handover; - B\_WARMUP: purchased before 2017-02-12 (first six weeks), removed after the features are built.

**What was done:** From 77,736 A development rows (s02, eligible, before the cutoff) to 61,258 B rows. Removed: B\_STATE 13,983; B\_DISTANCE 618; B\_NO\_HANDOVER 461; B\_REVIEW\_BEFORE\_HANDOVER 146; B\_WARMUP 1,270.

**Rows by step** (exclusion\_counts\_B.csv):

| step | rows |
| --- | --- |
| A development rows (s02, pre-cutoff, eligible) | 77,736 |
| removed: B\_STATE | 13,983 |
| removed: B\_DISTANCE | 618 |
| removed: B\_NO\_HANDOVER | 461 |
| removed: B\_REVIEW\_BEFORE\_HANDOVER | 146 |
| removed: B\_WARMUP | 1,270 |
| B development rows | 61,258 |

**Check** B development rows are a subset of A's eligible pre-cutoff rows: PASS (61,258 of 77,736) **Check** removal counts add up: A rows = B rows + removed: PASS (77,736 = 61,258 + 16,478)

**Files** (pipeline\_b/stages/b02/classification/outputs/, run 20261023T153744Z): exclusion\_counts\_B.csv, exclusions\_B.csv, records\_B.csv.gz

## B2.2 Prediction time

**Approved solution (B2 blueprint):** Prediction time. Regression: purchase time. Classification: carrier handover time.

**What was done:** Prediction time: carrier handover time.

**Prediction time span** (records\_B.csv.gz): 2017-02-13 08:58:08 to 2018-06-20 12:20:00; 71 prediction weeks.

**Files** (pipeline\_b/stages/b02/classification/outputs/, run 20261023T153744Z): records\_B.csv.gz

## B2.3 Events

**Approved solution (B2 blueprint):** Events. One row per raw order purchased before the task's test cutoff: primary seller (highest price, then lowest item id, A's rule), last shipping limit, carrier date, delivery date, route = seller\_state + "->" + customer\_state. The estimated delivery date column is dropped on load.

**What was done:** 79,046 raw orders purchased before the cutoff 2018-05-26 12:16:34; primary seller by A's rule (highest price, then lowest item id); the estimated delivery date column is not read.

**Events** (feature\_build\_log.json): 79,046 raw orders purchased before the cutoff 2018-05-26 12:16:34.

**Check** no column from the estimated delivery date: PASS **Check** seller state from the raw tables equals A's primary\_seller\_state: PASS

**Files** (pipeline\_b/stages/b02/classification/outputs/, run 20261023T153744Z): feature\_build\_log.json

## B2.4 Weeks and leakage rule

**Approved solution (B2 blueprint):** Weeks. Calendar weeks, Monday to Sunday. A handover event counts in its carrier-date week; a delivery event in its delivery week. A row uses only complete weeks before its prediction week.

**What was done:** Calendar weeks from Monday 2016-01-04; handover events in their carrier-date week, delivery events in their delivery week; a row uses only weeks before its prediction week.

**Settings** (feature\_build\_log.json): weights 0.5, 0.3, 0.2 for weeks w−1, w−2, w−3; at least 10 route events over 3 weeks; state mix 0.7 / 0.3 (seller state / customer state).

**Check** leakage re-check: features recomputed by brute force from events in weeks before the prediction week match: PASS (300 rows, max difference 0.00e+00)

**Files** (pipeline\_b/stages/b02/classification/outputs/, run 20261023T153744Z): feature\_build\_log.json

## B2.5 History features (B-C6 to B-C9)

**Approved solution (B2 blueprint):** Features (B-C6 to B-C9), all candidates for both tasks unless stated: Feature names (B-G-04) are in brackets. - route (categorical) \[route\_seller\_to\_customer\_state\]; - prior seller late-handover rate, prior seller late-handover days, prior seller dispatch days (B-C7) \[seller\_prior\_late\_handover\_rate, seller\_prior\_late\_handover\_days, seller\_prior\_dispatch\_days\]: mean over all of the seller's earlier handover weeks; a seller with no history takes the weighted 3-week mean of sellers in the same seller state; - recent route delivery days (B-C8) and recent route carrier transit days (B-C8b) \[route\_recent\_delivery\_days, route\_recent\_carrier\_transit\_days\]: weighted 3-week mean (0.5, 0.3, 0.2 for weeks w−1, w−2, w−3) of the route's weekly median, the weights renormalised over the weeks that have events; fewer than 10 route events in the 3 weeks → 0.7 × seller state's + 0.3 × customer state's weighted 3-week mean, then the overall one; - classification only (B-C9): this order's handover late flag, late days and dispatch days \[order\_handed\_over\_late, order\_handover\_late\_days, order\_dispatch\_days\].

**What was done:** Features built: route\_seller\_to\_customer\_state, seller\_prior\_late\_handover\_rate, seller\_prior\_late\_handover\_days, seller\_prior\_dispatch\_days, route\_recent\_delivery\_days, route\_recent\_carrier\_transit\_days, order\_handed\_over\_late, order\_handover\_late\_days, order\_dispatch\_days. History sources: seller\_prior: own seller history 96.7%, seller-state fallback 3.3%; route\_recent\_delivery\_days: own route history 96.0%, state-mix fallback 4.0%; route\_recent\_carrier\_transit\_days: own route history 96.0%, state-mix fallback 4.0%.

**Feature distributions** (computed from records\_B.csv.gz):

| feature | count | mean | 10% | 50% | 90% | missing\_share |
| --- | --- | --- | --- | --- | --- | --- |
| seller\_prior\_late\_handover\_rate | 61,258 | 0.0844 | 0.0000 | 0.0390 | 0.2381 | 0.0000 |
| seller\_prior\_late\_handover\_days | 61,258 | 0.2825 | 0.0000 | 0.0579 | 0.6604 | 0.0000 |
| seller\_prior\_dispatch\_days | 61,258 | 3.2425 | 1.5990 | 2.8724 | 5.1887 | 0.0000 |
| route\_recent\_delivery\_days | 61,258 | 10.8028 | 6.4834 | 9.8733 | 16.8225 | 0.0000 |
| route\_recent\_carrier\_transit\_days | 61,258 | 7.6315 | 3.4855 | 6.9579 | 13.3071 | 0.0000 |
| order\_handed\_over\_late | 61,258 | 0.0872 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| order\_handover\_late\_days | 61,258 | 0.2205 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| order\_dispatch\_days | 61,233 | 3.2651 | 0.8043 | 2.3141 | 6.4257 | 0.0004 |

**History source by quarter** (history\_coverage.csv; share of rows using own history vs a fallback):

| feature | quarter | own route history | own seller history | seller-state fallback | state-mix fallback |
| --- | --- | --- | --- | --- | --- |
| route\_recent\_carrier\_transit\_days | 2017Q1 | 0.863 | 0.000 | 0.000 | 0.137 |
| route\_recent\_carrier\_transit\_days | 2017Q2 | 0.928 | 0.000 | 0.000 | 0.072 |
| route\_recent\_carrier\_transit\_days | 2017Q3 | 0.948 | 0.000 | 0.000 | 0.052 |
| route\_recent\_carrier\_transit\_days | 2017Q4 | 0.963 | 0.000 | 0.000 | 0.037 |
| route\_recent\_carrier\_transit\_days | 2018Q1 | 0.978 | 0.000 | 0.000 | 0.022 |
| route\_recent\_carrier\_transit\_days | 2018Q2 | 0.983 | 0.000 | 0.000 | 0.017 |
| route\_recent\_delivery\_days | 2017Q1 | 0.863 | 0.000 | 0.000 | 0.137 |
| route\_recent\_delivery\_days | 2017Q2 | 0.928 | 0.000 | 0.000 | 0.072 |
| route\_recent\_delivery\_days | 2017Q3 | 0.948 | 0.000 | 0.000 | 0.052 |
| route\_recent\_delivery\_days | 2017Q4 | 0.963 | 0.000 | 0.000 | 0.037 |
| route\_recent\_delivery\_days | 2018Q1 | 0.978 | 0.000 | 0.000 | 0.022 |
| route\_recent\_delivery\_days | 2018Q2 | 0.983 | 0.000 | 0.000 | 0.017 |
| seller\_prior | 2017Q1 | 0.000 | 0.910 | 0.090 | 0.000 |
| seller\_prior | 2017Q2 | 0.000 | 0.962 | 0.038 | 0.000 |
| seller\_prior | 2017Q3 | 0.000 | 0.964 | 0.036 | 0.000 |
| seller\_prior | 2017Q4 | 0.000 | 0.971 | 0.029 | 0.000 |
| seller\_prior | 2018Q1 | 0.000 | 0.979 | 0.021 | 0.000 |
| seller\_prior | 2018Q2 | 0.000 | 0.965 | 0.035 | 0.000 |

**Lateness summary, ten busiest routes** (aggregated from lateness\_summary\_B.csv.gz, which holds every route × week × seller; seven-state routes only (B-G-03), events before the cutoff; descriptive only, for Henry's lateness page):

| route (seller state -> customer state) | handovers | late\_handover\_rate | late\_handover\_days | median\_of\_weekly\_carrier\_transit\_medians |
| --- | --- | --- | --- | --- |
| SP->SP | 24,087 | 0.092 | 0.267 | 3.945 |
| SP->RJ | 6,994 | 0.103 | 0.336 | 10.050 |
| SP->MG | 6,185 | 0.098 | 0.245 | 8.008 |
| SP->RS | 3,008 | 0.078 | 0.219 | 11.740 |
| SP->PR | 2,546 | 0.088 | 0.294 | 8.181 |
| PR->SP | 2,341 | 0.113 | 0.613 | 6.863 |
| MG->SP | 2,125 | 0.082 | 0.362 | 7.026 |
| SP->SC | 1,968 | 0.091 | 0.279 | 11.338 |
| SP->BA | 1,906 | 0.085 | 0.203 | 15.106 |
| MG->MG | 1,205 | 0.080 | 0.341 | 5.145 |

**Check** leakage re-check: features recomputed by brute force from events in weeks before the prediction week match: PASS (300 rows, max difference 0.00e+00)

**Files** (pipeline\_b/stages/b02/classification/outputs/, run 20261023T153744Z): feature\_build\_log.json, history\_coverage.csv, lateness\_summary\_B.csv.gz, records\_B.csv.gz

## B2.6 Test rows

**Approved solution (B2 blueprint):** Test rows. B2 builds features for development rows only. Test-row features are built in the joint test run, from events known before each test row's prediction week.

**What was done:** Development rows only; test-row features are built in the joint test run.

**Latest purchase in B rows** (records\_B.csv.gz): 2018-05-26 12:12:15; test cutoff 2018-05-26 12:16:34.

**Check** no test row: every B row purchased before the test cutoff: PASS (latest purchase 2018-05-26 12:12:15, cutoff 2018-05-26 12:16:34)

**Files** (pipeline\_b/stages/b02/classification/outputs/, run 20261023T153744Z):

# Round 1 cards (superseded by round 2, kept for the record)

Run 20261023T134750Z on commit 2991253 (tag e5-B-s02-accepted). Old feature names; Henry's naming comment is on B2.5 below.

## B2.1 Population (B-C1 to B-C5)

**Approved solution (B2 blueprint):** Population (B-C1 to B-C5), applied to A's task-eligible rows, each removal with a reason code in `exclusions\_B.csv`: - B\_STATE: customer or primary seller state outside SP, MG, RJ, PR, RS, BA, SC, or missing; - B\_DISTANCE: distance\_km\_max missing; - B\_LEAD\_CAP (regression): lead\_days > 93.63 (mean + 8 × SD of A's s02 pre-cutoff orders, audit.json; no floor); - B\_NO\_HANDOVER (classification): no carrier handover date; - B\_REVIEW\_BEFORE\_HANDOVER (classification): review answered at or before handover; - B\_WARMUP: purchased before 2017-02-12 (first six weeks), removed after the features are built.

**What was done:** From 77,736 A development rows (s02, eligible, before the cutoff) to 61,258 B rows. Removed: B\_STATE 13,983; B\_DISTANCE 618; B\_NO\_HANDOVER 461; B\_REVIEW\_BEFORE\_HANDOVER 146; B\_WARMUP 1,270.

**Rows by step** (exclusion\_counts\_B.csv):

| step | rows |
| --- | --- |
| A development rows (s02, pre-cutoff, eligible) | 77,736 |
| removed: B\_STATE | 13,983 |
| removed: B\_DISTANCE | 618 |
| removed: B\_NO\_HANDOVER | 461 |
| removed: B\_REVIEW\_BEFORE\_HANDOVER | 146 |
| removed: B\_WARMUP | 1,270 |
| B development rows | 61,258 |

**Check** B development rows are a subset of A's eligible pre-cutoff rows: PASS (61,258 of 77,736) **Check** removal counts add up: A rows = B rows + removed: PASS (77,736 = 61,258 + 16,478)

**Files** (pipeline\_b/stages/b02/classification/outputs/, run 20261023T134750Z): exclusion\_counts\_B.csv, exclusions\_B.csv, records\_B.csv.gz

## B2.2 Prediction time

**Approved solution (B2 blueprint):** Prediction time. Regression: purchase time. Classification: carrier handover time.

**What was done:** Prediction time: carrier handover time.

**Prediction time span** (records\_B.csv.gz): 2017-02-13 08:58:08 to 2018-06-20 12:20:00; 71 prediction weeks.

**Files** (pipeline\_b/stages/b02/classification/outputs/, run 20261023T134750Z): records\_B.csv.gz

## B2.3 Events

**Approved solution (B2 blueprint):** Events. One row per raw order purchased before the task's test cutoff: primary seller (highest price, then lowest item id, A's rule), last shipping limit, carrier date, delivery date, route = customer\_state + "->" + seller\_state. The estimated delivery date column is dropped on load.

**What was done:** 79,046 raw orders purchased before the cutoff 2018-05-26 12:16:34; primary seller by A's rule (highest price, then lowest item id); the estimated delivery date column is not read.

**Events** (feature\_build\_log.json): 79,046 raw orders purchased before the cutoff 2018-05-26 12:16:34.

**Check** no column from the estimated delivery date: PASS **Check** seller state from the raw tables equals A's primary\_seller\_state: PASS

**Files** (pipeline\_b/stages/b02/classification/outputs/, run 20261023T134750Z): feature\_build\_log.json

## B2.4 Weeks and leakage rule

**Approved solution (B2 blueprint):** Weeks. Calendar weeks, Monday to Sunday. A handover event counts in its carrier-date week; a delivery event in its delivery week. A row uses only complete weeks before its prediction week.

**What was done:** Calendar weeks from Monday 2016-01-04; handover events in their carrier-date week, delivery events in their delivery week; a row uses only weeks before its prediction week.

**Settings** (feature\_build\_log.json): weights 0.5, 0.3, 0.2 for weeks w−1, w−2, w−3; at least 10 route events over 3 weeks; state mix 0.7 / 0.3 (seller state / customer state).

**Check** leakage re-check: features recomputed by brute force from events in weeks before the prediction week match: PASS (300 rows, max difference 0.00e+00)

**Files** (pipeline\_b/stages/b02/classification/outputs/, run 20261023T134750Z): feature\_build\_log.json

## B2.5 History features (B-C6 to B-C9)

**Approved solution (B2 blueprint):** Features (B-C6 to B-C9), all candidates for both tasks unless stated: - route (categorical); - prior seller late rate, prior seller late days, prior seller dispatch days (B-C7): mean over all of the seller's earlier handover weeks; a seller with no history takes the weighted 3-week mean of sellers in the same seller state; - route lead days (B-C8) and route transit days (B-C8b): weighted 3-week mean (0.5, 0.3, 0.2 for weeks w−1, w−2, w−3) of the route's weekly median, the weights renormalised over the weeks that have events; fewer than 10 route events in the 3 weeks → 0.7 × seller state's + 0.3 × customer state's weighted 3-week mean, then the overall one; - classification only (B-C9): this order's handover late flag, late days and dispatch days.

**What was done:** Features built: b\_seller\_late\_rate, b\_seller\_late\_days, b\_seller\_dispatch\_days, b\_route\_lead\_days, b\_route\_transit\_days, b\_own\_handover\_late, b\_own\_late\_days, b\_own\_dispatch\_days, route. History sources: b\_seller: seller 96.7%, seller\_state 3.3%; b\_route\_lead\_days: route 96.0%, state\_mix 4.0%; b\_route\_transit\_days: route 96.0%, state\_mix 4.0%.

**Feature distributions** (computed from records\_B.csv.gz):

| feature | count | mean | 10% | 50% | 90% | missing\_share |
| --- | --- | --- | --- | --- | --- | --- |
| b\_seller\_late\_rate | 61,258 | 0.0844 | 0.0000 | 0.0390 | 0.2381 | 0.0000 |
| b\_seller\_late\_days | 61,258 | 0.2825 | 0.0000 | 0.0579 | 0.6604 | 0.0000 |
| b\_seller\_dispatch\_days | 61,258 | 3.2425 | 1.5990 | 2.8724 | 5.1887 | 0.0000 |
| b\_route\_lead\_days | 61,258 | 10.8028 | 6.4834 | 9.8733 | 16.8225 | 0.0000 |
| b\_route\_transit\_days | 61,258 | 7.6315 | 3.4855 | 6.9579 | 13.3071 | 0.0000 |
| b\_own\_handover\_late | 61,258 | 0.0872 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| b\_own\_late\_days | 61,258 | 0.2205 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| b\_own\_dispatch\_days | 61,233 | 3.2651 | 0.8043 | 2.3141 | 6.4257 | 0.0004 |

**History source by quarter** (history\_coverage.csv; share of rows using own history vs a fallback):

| feature | quarter | route | seller | seller\_state | state\_mix |
| --- | --- | --- | --- | --- | --- |
| b\_route\_lead\_days | 2017Q1 | 0.863 | 0.000 | 0.000 | 0.137 |
| b\_route\_lead\_days | 2017Q2 | 0.928 | 0.000 | 0.000 | 0.072 |
| b\_route\_lead\_days | 2017Q3 | 0.948 | 0.000 | 0.000 | 0.052 |
| b\_route\_lead\_days | 2017Q4 | 0.963 | 0.000 | 0.000 | 0.037 |
| b\_route\_lead\_days | 2018Q1 | 0.978 | 0.000 | 0.000 | 0.022 |
| b\_route\_lead\_days | 2018Q2 | 0.983 | 0.000 | 0.000 | 0.017 |
| b\_route\_transit\_days | 2017Q1 | 0.863 | 0.000 | 0.000 | 0.137 |
| b\_route\_transit\_days | 2017Q2 | 0.928 | 0.000 | 0.000 | 0.072 |
| b\_route\_transit\_days | 2017Q3 | 0.948 | 0.000 | 0.000 | 0.052 |
| b\_route\_transit\_days | 2017Q4 | 0.963 | 0.000 | 0.000 | 0.037 |
| b\_route\_transit\_days | 2018Q1 | 0.978 | 0.000 | 0.000 | 0.022 |
| b\_route\_transit\_days | 2018Q2 | 0.983 | 0.000 | 0.000 | 0.017 |
| b\_seller | 2017Q1 | 0.000 | 0.910 | 0.090 | 0.000 |
| b\_seller | 2017Q2 | 0.000 | 0.962 | 0.038 | 0.000 |
| b\_seller | 2017Q3 | 0.000 | 0.964 | 0.036 | 0.000 |
| b\_seller | 2017Q4 | 0.000 | 0.971 | 0.029 | 0.000 |
| b\_seller | 2018Q1 | 0.000 | 0.979 | 0.021 | 0.000 |
| b\_seller | 2018Q2 | 0.000 | 0.965 | 0.035 | 0.000 |

**Lateness summary, ten busiest routes** (aggregated from lateness\_summary\_B.csv.gz, which holds every route × week × seller; all states, events before the cutoff; descriptive only, for Henry's lateness page):

| route | handovers | seller\_late\_rate | seller\_late\_days | median\_of\_weekly\_transit\_medians |
| --- | --- | --- | --- | --- |
| SP->SP | 24,087 | 0.092 | 0.267 | 3.945 |
| RJ->SP | 6,994 | 0.103 | 0.336 | 10.050 |
| MG->SP | 6,185 | 0.098 | 0.245 | 8.008 |
| RS->SP | 3,008 | 0.078 | 0.219 | 11.740 |
| PR->SP | 2,546 | 0.088 | 0.294 | 8.181 |
| SP->PR | 2,341 | 0.113 | 0.613 | 6.863 |
| SP->MG | 2,125 | 0.082 | 0.362 | 7.026 |
| SC->SP | 1,968 | 0.091 | 0.279 | 11.338 |
| BA->SP | 1,906 | 0.085 | 0.203 | 15.106 |
| GO->SP | 1,206 | 0.080 | 0.233 | 11.986 |

**Check** leakage re-check: features recomputed by brute force from events in weeks before the prediction week match: PASS (300 rows, max difference 0.00e+00)

**Files** (pipeline\_b/stages/b02/classification/outputs/, run 20261023T134750Z): feature\_build\_log.json, history\_coverage.csv, lateness\_summary\_B.csv.gz, records\_B.csv.gz

## B2.6 Test rows

**Approved solution (B2 blueprint):** Test rows. B2 builds features for development rows only. Test-row features are built in the joint test run, from events known before each test row's prediction week.

**What was done:** Development rows only; test-row features are built in the joint test run.

**Latest purchase in B rows** (records\_B.csv.gz): 2018-05-26 12:12:15; test cutoff 2018-05-26 12:16:34.

**Check** no test row: every B row purchased before the test cutoff: PASS (latest purchase 2018-05-26 12:12:15, cutoff 2018-05-26 12:16:34)

**Files** (pipeline\_b/stages/b02/classification/outputs/, run 20261023T134750Z):
