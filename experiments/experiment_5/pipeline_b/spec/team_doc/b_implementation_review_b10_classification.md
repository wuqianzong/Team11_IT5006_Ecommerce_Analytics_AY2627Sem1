# B10 › classification

**ACCEPTED round 3** by the experiment lead (Wu Qianzong), 2026-10-27 · tag `e5-B-s10-accepted-r3` · B-G-10 and B-G-11 ratified (B-CR-34). Built by Henry and his Claude on branch e5/b10-henry; merged into milestone-3 at 46d68a4. Verified on the lead's machine: tests 25 of 25, deliverables audit 9 of 9; B10 rerun reproduces threshold\_results.csv and serving\_config.json exactly, other outputs differ only in the last float digit (reproduction policy CR-056). Published from pipeline\_b/spec/doc\_outbox/; round 2 is kept below for the record (superseded).

## Round 3 (current)

**Built for review · run `20261027T044819Z` on commit 906fe39 (clean, dirty: false) · 16 checks, 16 PASS.** Blueprint spec/blueprints/b10\_release.md (AGREED). Nothing is refitted and the test is not read again (B-G-08, B10-D10). Every number below is read from pipeline\_b/stages/b10/classification/outputs/.

### B10.1 Reload parity

**What was done:** Bundles reloaded from disk re-predict T1's saved test predictions on rows rebuilt with every label column empty (B-G-08): A frozen on A test rows max difference 2.2e-16 over 18,966 rows; A frozen on B test rows max difference 2.2e-16 over 15,492 rows; B frozen on B test rows max difference 2.2e-16 over 15,492 rows. Python 3.13.7.

| model | rows | n\_rows | n\_t1\_rows | max\_abs\_diff | within\_tolerance |
| --- | --- | --- | --- | --- | --- |
| A frozen | A test rows | 18966 | 18966 | 2.2e-16 | True |
| A frozen | B test rows | 15492 | 15492 | 2.2e-16 | True |
| B frozen | B test rows | 15492 | 15492 | 2.2e-16 | True |

### B10.2 Release manifest

**What was done:** Release manifest: sha256 of every bundle file (equal to tag e5-T1-tested), frozen recipes equal to their tags (A e5-A-frozen, B e5-B-frozen), training digests recomputed. Version differences: {"A": {}, "B": {}}

| bundle | model | calibration | training rows | files equal T1 tag | recipe equals its tag | digest recomputes | version differences |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | clf.sel.log.logistic | sigmoid | 74970 | True | True | True | {} |
| B | clf.sel.log.logistic | sigmoid | 59188 | True | True | True | {} |

### B10.3 Serving configuration

**What was done:** Serving: B inside its scope at 4/15 (B-G-07), frozen 1/6 kept beside it; A outside at 1/6 (B10-D2). Expected alerts/day, validation: B 4.0 + A 6.5 = 10.5; test (post-test view): B 5.6 + A 14.9 = 20.5, combined test cost 9,211 at 5:1 and 3,115 at 1:1 (round 3, B-G-10). Volumes accepted by the team (Henry, 2026-10-26; threshold\_results.csv).

| model | threshold\_name | rows | threshold | alerts | alerts\_per\_day | tp | fp | fn | precision | recall | fp\_per\_tp | cost\_5\_to\_1 | cost\_1\_to\_1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B frozen | B frozen 1/6 | validation (out-of-fold), B rows | 0.1667 | 5865 | 17 | 1749 | 4116 | 5251 | 0.2982 | 0.2499 | 2.3533 | 30,371 | 9367 |
| B frozen | B operating 4/15 (B-G-07) | validation (out-of-fold), B rows | 0.2667 | 1381 | 4.0029 | 588 | 793 | 6412 | 0.4258 | 0.0840 | 1.3486 | 32,853 | 7205 |
| B frozen | B frozen 1/6 | test, B rows (post-test view) | 0.1667 | 2229 | 23.2188 | 463 | 1766 | 1078 | 0.2077 | 0.3005 | 3.8143 | 7,156 | 2844 |
| B frozen | B operating 4/15 (B-G-07) | test, B rows (post-test view) | 0.2667 | 540 | 5.6250 | 187 | 353 | 1354 | 0.3463 | 0.1213 | 1.8877 | 7,123 | 1707 |
| A frozen | A frozen 1/6 (B10-D2) | validation (out-of-fold), A rows outside B's scope | 0.1667 | 2253 | 6.5304 | 519 | 1734 | 1431 | 0.2304 | 0.2662 | 3.3410 | 8,889 | 3165 |
| A frozen | A frozen 1/6 (B10-D2) | test, A rows outside B's scope | 0.1667 | 1428 | 14.8750 | 190 | 1238 | 170 | 0.1331 | 0.5278 | 6.5158 | 2,088 | 1408 |
| B frozen + A frozen | B 4/15 + A 1/6 (serving rule) | validation (out-of-fold), all rows |  | 3634 | 10.5333 | 1107 | 2527 | 7843 | 0.3046 | 0.1237 | 2.2827 | 41,742 | 10370 |
| B frozen + A frozen | B 4/15 + A 1/6 (serving rule) | test, all rows (post-test view) |  | 1968 | 20.5000 | 377 | 1591 | 1524 | 0.1916 | 0.1983 | 4.2202 | 9,211 | 3115 |

Validation rows are selection scores (G-10); test rows are a post-test view of T1's saved predictions. The frozen 1/6 test result stays the unbiased one (G-79). Sources per row in threshold\_results.csv.

### B10.4 Router

**What was done:** Router (e5b/serving.py) on every A test row: reproduces T1 within 2.2e-16. Routes: in scope / - / no score: in scope, not yet handed over (B10-D9; missed-dispatch rule applies): 36; in scope / B frozen / scored: 15,534; outside: customer state / A frozen / scored: 2,821; outside: distance missing / A frozen / scored: 144; outside: seller state / A frozen / scored: 431

| scope\_reason | model | status | orders |
| --- | --- | --- | --- |
| in scope |  | no score: in scope, not yet handed over (B10-D9; missed-dispatch rule applies) | 36 |
| in scope | B frozen | scored | 15534 |
| outside: customer state | A frozen | scored | 2821 |
| outside: distance missing | A frozen | scored | 144 |
| outside: seller state | A frozen | scored | 431 |

B rows outside T1's kept set (regression: above the lead cap; classification: review answered before handover) are scored by B at serving time but have no T1 prediction to compare with.

### B10.5 Input checks

**What was done:** 10 input rules; 14 of 14 test cases give the expected outcome (input\_validation.json).

| rule | level | source |
| --- | --- | --- |
| missing column | error | bundle schema.json (numeric, categorical) and the scope columns |
| unknown state | error | Brazil's 27 state codes |
| type | error | numeric features in schema.json |
| impossible distance | error | 0 to 5,000 km |
| no items | error | n\_items >= 1 (A's s10 10.5) |
| missing installments | error | A's s10 10.5 |
| negative value | error | numeric features whose training minimum is >= 0 (drift\_profile.json) |
| missing value | warning | the bundle imputes the training median |
| unseen category | warning | levels of the bundle's one-hot encoder (ignored when unseen) |
| out of profile | warning | drift\_profile.json; more than 4 SD from the training mean (B10-D11) |

| case | expected | status | model | rules | passed |
| --- | --- | --- | --- | --- | --- |
| valid in-scope order | scored (B frozen) | scored | B frozen |  | True |
| valid out-of-scope order | scored (A frozen) | scored | A frozen |  | True |
| unknown customer state | rejected (unknown state) | rejected: input error |  | unknown state, unseen category | True |
| negative distance | rejected (impossible distance) | rejected: input error |  | impossible distance, negative value | True |
| distance beyond Brazil | rejected (impossible distance) | rejected: input error |  | impossible distance, out of profile | True |
| no items | rejected (no items) | rejected: input error |  | no items | True |
| missing installments | rejected (missing installments) | rejected: input error |  | missing installments, missing value | True |
| text in a numeric feature | rejected (type) | rejected: input error |  | type | True |
| negative value where training has none | rejected (negative value) | rejected: input error |  | negative value | True |
| missing numeric value (imputed) | scored (missing value) | scored | B frozen | missing value | True |
| unseen category (ignored) | scored (unseen category) | scored | B frozen | unseen category | True |
| distance missing: out of scope | scored (A frozen) | scored | A frozen | missing value | True |
| far from the training profile (warning) | scored (out of profile) | scored | B frozen | out of profile | True |
| in scope, not yet handed over | no score: in scope, not yet handed over (B10-D9; missed-dispatch rule applies) | no score: in scope, not yet handed over (B10-D9; missed-dispatch rule applies) |  | missing value | True |

### B10.6 Drift profile

**What was done:** Training ranges per feature from T1's final-fit rows; shares of test rows beyond 3, 4 and 5 SD in out\_of\_profile\_shares.csv. The app warns beyond 4 SD (B10-D11); warning only.

Largest shares of test rows beyond 3 SD of the training mean (all features in out\_of\_profile\_shares.csv):

| pipeline | feature | rows | n\_rows | share\_beyond\_3sd | share\_beyond\_4sd | share\_beyond\_5sd |
| --- | --- | --- | --- | --- | --- | --- |
| B | order\_handed\_over\_late | B test rows | 15492 | 0.0773 | 0.0000 | 0.0000 |
| B | n\_products | B test rows | 15492 | 0.0327 | 0.0327 | 0.0038 |
| A | n\_products | A test rows | 18966 | 0.0323 | 0.0323 | 0.0041 |
| A | total\_freight | A test rows | 18966 | 0.0252 | 0.0131 | 0.0085 |
| B | total\_freight | B test rows | 15492 | 0.0243 | 0.0127 | 0.0079 |
| A | product\_description\_lenght | A test rows | 18966 | 0.0241 | 0.0080 | 0.0000 |
| B | product\_description\_lenght | B test rows | 15492 | 0.0225 | 0.0081 | 0.0000 |
| B | n\_items | B test rows | 15492 | 0.0221 | 0.0086 | 0.0086 |

### B10.7 App sources and R-14

**What was done:** 20 app elements mapped to files and evidence IDs (app\_sources.json); R-14 top 5 routes and categories per quarter with at least 100 orders, observed outcomes on development rows, coefficient beside (top\_routes\_categories.csv).

| panel | element | file | evidence\_id |
| --- | --- | --- | --- |
| headline | test metrics of A and B | pipeline\_b/stages/t1\_joint\_test/classification/outputs/metrics\_test.csv | T1.3 |
| headline | train, validation and test with 95% intervals | pipeline\_b/stages/b09/classification/outputs/train\_val\_test.csv | B9.1 |
| headline | B minus A on the same test orders | pipeline\_b/stages/b09/classification/outputs/paired\_test\_differences.csv | B9.2 |
| fit | validation folds and test together | pipeline\_b/stages/b09/classification/outputs/validation\_and\_test.csv | B9.14 |
| fit | fold-by-fold and test table | pipeline\_b/stages/t1\_joint\_test/classification/outputs/fold\_and\_test\_table.csv | T1.6 |
| where it errs | slices by state, route and more | pipeline\_b/stages/b09/classification/outputs/subgroups.csv | B9.3 |
| where it errs | business summary by route | pipeline\_b/stages/b09/classification/outputs/business\_by\_route.csv | B9.13 |
| why | coefficients | pipeline\_b/stages/b09/classification/outputs/coefficients.csv | B9.5 |
| why | permutation importance | pipeline\_b/stages/b09/classification/outputs/permutation\_importance.csv | B9.5 |
| data health | drift, development vs test | pipeline\_b/stages/b09/classification/outputs/drift.csv | B9.4 |
| data health | training profile and out-of-profile shares | pipeline\_b/stages/b10/classification/outputs/drift\_profile.json | B10.6 |
| score | serving rule and thresholds | pipeline\_b/stages/b10/classification/outputs/serving\_config.json | B10.3 |
| score | input checks | pipeline\_b/stages/b10/classification/outputs/input\_validation.json | B10.5 |
| fallback | A inside and outside B's scope | pipeline\_b/stages/b09/classification/outputs/a\_fallback\_by\_scope.csv | B9.15 |
| policy | B at 1/6 and 4/15, A out of scope at 1/6 | pipeline\_b/stages/b10/classification/outputs/threshold\_results.csv | B10.3 |
| fit | PR, ROC and reliability on B's test rows | pipeline\_b/stages/t1\_joint\_test/classification/outputs/figures/test\_curves.png | T1.4 |
| fit | confusion matrices at 1/6 | pipeline\_b/stages/t1\_joint\_test/classification/outputs/confusion\_test.csv | T1.4 |
| policy | missed-dispatch rule on the test period | pipeline\_b/stages/b09/classification/outputs/missed\_dispatch\_rule\_test.csv | B9.7 |
| why | label sensitivity | pipeline\_b/stages/b09/classification/outputs/label\_sensitivity.csv | B9.6 |
| dashboard (R-14) | top 5 routes and categories by quarter | pipeline\_b/stages/b10/classification/outputs/top\_routes\_categories.csv | B10.7 |

R-14, latest development quarter (2018Q2); every quarter is in top\_routes\_categories.csv:

| window | dimension | rank | level | orders | outcome | outcome\_name | coefficient |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2018Q2 | route\_seller\_to\_customer\_state | 1 | SP->RJ | 798 | 0.1679 | detractor share (observed) | 0.4974 |
| 2018Q2 | route\_seller\_to\_customer\_state | 2 | SP->BA | 185 | 0.1514 | detractor share (observed) | 0.4329 |
| 2018Q2 | route\_seller\_to\_customer\_state | 3 | RJ->SP | 166 | 0.1205 | detractor share (observed) | -0.0256 |
| 2018Q2 | route\_seller\_to\_customer\_state | 4 | SP->RS | 360 | 0.1000 | detractor share (observed) | 0.0431 |
| 2018Q2 | route\_seller\_to\_customer\_state | 5 | SP->MG | 771 | 0.0999 | detractor share (observed) | 0.1112 |
| 2018Q2 | primary\_category | 1 | home\_appliances | 114 | 0.1491 | detractor share (observed) | 0.2201 |
| 2018Q2 | primary\_category | 2 | bed\_bath\_table | 761 | 0.1380 | detractor share (observed) | 0.2193 |
| 2018Q2 | primary\_category | 3 | computers\_accessories | 504 | 0.1349 | detractor share (observed) | 0.2045 |
| 2018Q2 | primary\_category | 4 | construction\_tools\_construction | 103 | 0.1262 | detractor share (observed) | -0.4290 |
| 2018Q2 | primary\_category | 5 | baby | 266 | 0.1165 | detractor share (observed) | 0.1906 |

### Checks

| check | passed | detail |
| --- | --- | --- |
| with labels blanked, only the label-free rules remove test rows (B\_DISTANCE, B\_NO\_HANDOVER, B\_STATE) | True | B\_STATE 3,252; B\_DISTANCE 144; B\_NO\_HANDOVER 36 |
| no test label is read: every label column of the rebuilt test rows is empty (B-G-08) | True | lead\_days, lead\_label\_ts, is\_detractor, is\_detractor\_first, review\_label\_ts |
| the rebuilt rows contain exactly T1's kept B test rows | True | 15,492 of 15,492 |
| every bundle reloads from disk and re-predicts T1's saved test predictions within 1e-9 | True | A frozen on A test rows: max 2.2e-16 (18,966 rows); A frozen on B test rows: max 2.2e-16 (15,492 rows); B frozen on B test rows: max 2.2e-16 (15,492 rows) |
| bundle files equal T1's tagged files; frozen recipes recompute their sha256, equal their tagged files and match the schemas; training rows and digests recompute | True |  |
| the frozen thresholds in the bundles are unchanged (1/6 for classification) | True |  |
| B's 1/6 and 4/15 test results from T1's saved predictions equal B9 threshold\_options.csv (alerts, TP, FP, FN) | True |  |
| A's out-of-scope fold counts derive exactly from B9.15 (TP and alerts are whole numbers) | True | 2,253 alerts, 519 TP over 345 validation days |
| A's out-of-scope test precision and recall from T1's saved predictions equal B9.15's test row (within 1e-12) | True | precision 0.1331, recall 0.5278 |
| the training profile in each bundle recomputes from T1's final-fit rows (mean and SD within 1e-9) | True |  |
| the router reproduces T1's predictions: B on B's test rows and A on the out-of-scope rows (within 1e-9) | True | B 2.2e-16, A 2.2e-16 |
| no test row is rejected by the input checks | True | 0 rejected |
| every scope reason and route occurs (in scope; customer state; seller state; before handover) | True | \['in scope', 'outside: customer state', 'outside: distance missing', 'outside: seller state'\] |
| every input-check case gives the expected outcome | True | 14 cases |
| every app element names an existing file tagged with its evidence ID | True | 20 elements |
| A's tree untouched: A's code matches e5-A-frozen | True |  |

## Round 2 (superseded by round 3)

**Built for review · run `20261026T024858Z` on commit 1e36f0a (clean, dirty: false) · 15 checks, 15 PASS.** Blueprint spec/blueprints/b10\_release.md (AGREED). Nothing is refitted and the test is not read again (B-G-08, B10-D10). Every number below is read from pipeline\_b/stages/b10/classification/outputs/.

### B10.1 Reload parity

**What was done:** Bundles reloaded from disk re-predict T1's saved test predictions on rows rebuilt with every label column empty (B-G-08): A frozen on A test rows max difference 2.2e-16 over 18,966 rows; A frozen on B test rows max difference 2.2e-16 over 15,492 rows; B frozen on B test rows max difference 2.2e-16 over 15,492 rows. Python 3.13.7.

| model | rows | n\_rows | n\_t1\_rows | max\_abs\_diff | within\_tolerance |
| --- | --- | --- | --- | --- | --- |
| A frozen | A test rows | 18966 | 18966 | 2.2e-16 | True |
| A frozen | B test rows | 15492 | 15492 | 2.2e-16 | True |
| B frozen | B test rows | 15492 | 15492 | 2.2e-16 | True |

### B10.2 Release manifest

**What was done:** Release manifest: sha256 of every bundle file (equal to tag e5-T1-tested), frozen recipes equal to their tags (A e5-A-frozen, B e5-B-frozen), training digests recomputed. Version differences: {"A": {}, "B": {}}

| bundle | model | calibration | training rows | files equal T1 tag | recipe equals its tag | digest recomputes | version differences |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | clf.sel.log.logistic | sigmoid | 74970 | True | True | True | {} |
| B | clf.sel.log.logistic | sigmoid | 59188 | True | True | True | {} |

### B10.3 Serving configuration

**What was done:** Serving: B inside its scope at 4/15 (B-G-07), frozen 1/6 kept beside it; A outside at 1/6 (B10-D2). Expected alerts/day, validation: B 4.0 + A 6.5 = 10.5; test (post-test view): B 5.6 + A 14.9 = 20.5. Volumes accepted by the team (Henry, 2026-10-26; threshold\_results.csv).

| model | threshold\_name | rows | threshold | alerts | alerts\_per\_day | tp | fp | fn | precision | recall | fp\_per\_tp | cost\_5\_to\_1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B frozen | B frozen 1/6 | validation (out-of-fold), B rows | 0.1667 | 5865 | 17 | 1,749 | 4,116 | 5,251 | 0.2982 | 0.2499 | 2.3533 | 30,371 |
| B frozen | B operating 4/15 (B-G-07) | validation (out-of-fold), B rows | 0.2667 | 1381 | 4.0029 | 588 | 793 | 6,412 | 0.4258 | 0.0840 | 1.3486 | 32,853 |
| B frozen | B frozen 1/6 | test, B rows (post-test view) | 0.1667 | 2229 | 23.2188 | 463 | 1,766 | 1,078 | 0.2077 | 0.3005 | 3.8143 | 7,156 |
| B frozen | B operating 4/15 (B-G-07) | test, B rows (post-test view) | 0.2667 | 540 | 5.6250 | 187 | 353 | 1,354 | 0.3463 | 0.1213 | 1.8877 | 7,123 |
| A frozen | A frozen 1/6 (B10-D2) | validation (out-of-fold), A rows outside B's scope | 0.1667 | 2253 | 6.5304 | 519 | 1,734 | 1,431 | 0.2304 | 0.2662 | 3.3410 | 8,889 |
| A frozen | A frozen 1/6 (B10-D2) | test, A rows outside B's scope | 0.1667 | 1428 | 14.8750 |  |  |  | 0.1331 | 0.5278 |  |  |

Validation rows are selection scores (G-10); test rows are a post-test view of T1's saved predictions. The frozen 1/6 test result stays the unbiased one (G-79). Sources per row in threshold\_results.csv.

### B10.4 Router

**What was done:** Router (e5b/serving.py) on every A test row: reproduces T1 within 2.2e-16. Routes: in scope / - / no score: in scope, not yet handed over (B10-D9; missed-dispatch rule applies): 36; in scope / B frozen / scored: 15,534; outside: customer state / A frozen / scored: 2,821; outside: distance missing / A frozen / scored: 144; outside: seller state / A frozen / scored: 431

| scope\_reason | model | status | orders |
| --- | --- | --- | --- |
| in scope |  | no score: in scope, not yet handed over (B10-D9; missed-dispatch rule applies) | 36 |
| in scope | B frozen | scored | 15534 |
| outside: customer state | A frozen | scored | 2821 |
| outside: distance missing | A frozen | scored | 144 |
| outside: seller state | A frozen | scored | 431 |

B rows outside T1's kept set (regression: above the lead cap; classification: review answered before handover) are scored by B at serving time but have no T1 prediction to compare with.

### B10.5 Input checks

**What was done:** 10 input rules; 14 of 14 test cases give the expected outcome (input\_validation.json).

| rule | level | source |
| --- | --- | --- |
| missing column | error | bundle schema.json (numeric, categorical) and the scope columns |
| unknown state | error | Brazil's 27 state codes |
| type | error | numeric features in schema.json |
| impossible distance | error | 0 to 5,000 km |
| no items | error | n\_items >= 1 (A's s10 10.5) |
| missing installments | error | A's s10 10.5 |
| negative value | error | numeric features whose training minimum is >= 0 (drift\_profile.json) |
| missing value | warning | the bundle imputes the training median |
| unseen category | warning | levels of the bundle's one-hot encoder (ignored when unseen) |
| out of profile | warning | drift\_profile.json; more than 4 SD from the training mean (B10-D11) |

| case | expected | status | model | rules | passed |
| --- | --- | --- | --- | --- | --- |
| valid in-scope order | scored (B frozen) | scored | B frozen |  | True |
| valid out-of-scope order | scored (A frozen) | scored | A frozen |  | True |
| unknown customer state | rejected (unknown state) | rejected: input error |  | unknown state, unseen category | True |
| negative distance | rejected (impossible distance) | rejected: input error |  | impossible distance, negative value | True |
| distance beyond Brazil | rejected (impossible distance) | rejected: input error |  | impossible distance, out of profile | True |
| no items | rejected (no items) | rejected: input error |  | no items | True |
| missing installments | rejected (missing installments) | rejected: input error |  | missing installments, missing value | True |
| text in a numeric feature | rejected (type) | rejected: input error |  | type | True |
| negative value where training has none | rejected (negative value) | rejected: input error |  | negative value | True |
| missing numeric value (imputed) | scored (missing value) | scored | B frozen | missing value | True |
| unseen category (ignored) | scored (unseen category) | scored | B frozen | unseen category | True |
| distance missing: out of scope | scored (A frozen) | scored | A frozen | missing value | True |
| far from the training profile (warning) | scored (out of profile) | scored | B frozen | out of profile | True |
| in scope, not yet handed over | no score: in scope, not yet handed over (B10-D9; missed-dispatch rule applies) | no score: in scope, not yet handed over (B10-D9; missed-dispatch rule applies) |  | missing value | True |

### B10.6 Drift profile

**What was done:** Training ranges per feature from T1's final-fit rows; shares of test rows beyond 3, 4 and 5 SD in out\_of\_profile\_shares.csv. The app warns beyond 4 SD (B10-D11); warning only.

Largest shares of test rows beyond 3 SD of the training mean (all features in out\_of\_profile\_shares.csv):

| pipeline | feature | rows | n\_rows | share\_beyond\_3sd | share\_beyond\_4sd | share\_beyond\_5sd |
| --- | --- | --- | --- | --- | --- | --- |
| B | order\_handed\_over\_late | B test rows | 15492 | 0.0773 | 0.0000 | 0.0000 |
| B | n\_products | B test rows | 15492 | 0.0327 | 0.0327 | 0.0038 |
| A | n\_products | A test rows | 18966 | 0.0323 | 0.0323 | 0.0041 |
| A | total\_freight | A test rows | 18966 | 0.0252 | 0.0131 | 0.0085 |
| B | total\_freight | B test rows | 15492 | 0.0243 | 0.0127 | 0.0079 |
| A | product\_description\_lenght | A test rows | 18966 | 0.0241 | 0.0080 | 0.0000 |
| B | product\_description\_lenght | B test rows | 15492 | 0.0225 | 0.0081 | 0.0000 |
| B | n\_items | B test rows | 15492 | 0.0221 | 0.0086 | 0.0086 |

### B10.7 App sources and R-14

**What was done:** 20 app elements mapped to files and evidence IDs (app\_sources.json); R-14 top 5 routes and categories per quarter with at least 100 orders, observed outcomes on development rows, coefficient beside (top\_routes\_categories.csv).

| panel | element | file | evidence\_id |
| --- | --- | --- | --- |
| headline | test metrics of A and B | pipeline\_b/stages/t1\_joint\_test/classification/outputs/metrics\_test.csv | T1.3 |
| headline | train, validation and test with 95% intervals | pipeline\_b/stages/b09/classification/outputs/train\_val\_test.csv | B9.1 |
| headline | B minus A on the same test orders | pipeline\_b/stages/b09/classification/outputs/paired\_test\_differences.csv | B9.2 |
| fit | validation folds and test together | pipeline\_b/stages/b09/classification/outputs/validation\_and\_test.csv | B9.14 |
| fit | fold-by-fold and test table | pipeline\_b/stages/t1\_joint\_test/classification/outputs/fold\_and\_test\_table.csv | T1.6 |
| where it errs | slices by state, route and more | pipeline\_b/stages/b09/classification/outputs/subgroups.csv | B9.3 |
| where it errs | business summary by route | pipeline\_b/stages/b09/classification/outputs/business\_by\_route.csv | B9.13 |
| why | coefficients | pipeline\_b/stages/b09/classification/outputs/coefficients.csv | B9.5 |
| why | permutation importance | pipeline\_b/stages/b09/classification/outputs/permutation\_importance.csv | B9.5 |
| data health | drift, development vs test | pipeline\_b/stages/b09/classification/outputs/drift.csv | B9.4 |
| data health | training profile and out-of-profile shares | pipeline\_b/stages/b10/classification/outputs/drift\_profile.json | B10.6 |
| score | serving rule and thresholds | pipeline\_b/stages/b10/classification/outputs/serving\_config.json | B10.3 |
| score | input checks | pipeline\_b/stages/b10/classification/outputs/input\_validation.json | B10.5 |
| fallback | A inside and outside B's scope | pipeline\_b/stages/b09/classification/outputs/a\_fallback\_by\_scope.csv | B9.15 |
| policy | B at 1/6 and 4/15, A out of scope at 1/6 | pipeline\_b/stages/b10/classification/outputs/threshold\_results.csv | B10.3 |
| fit | PR, ROC and reliability on B's test rows | pipeline\_b/stages/t1\_joint\_test/classification/outputs/figures/test\_curves.png | T1.4 |
| fit | confusion matrices at 1/6 | pipeline\_b/stages/t1\_joint\_test/classification/outputs/confusion\_test.csv | T1.4 |
| policy | missed-dispatch rule on the test period | pipeline\_b/stages/b09/classification/outputs/missed\_dispatch\_rule\_test.csv | B9.7 |
| why | label sensitivity | pipeline\_b/stages/b09/classification/outputs/label\_sensitivity.csv | B9.6 |
| dashboard (R-14) | top 5 routes and categories by quarter | pipeline\_b/stages/b10/classification/outputs/top\_routes\_categories.csv | B10.7 |

R-14, latest development quarter (2018Q2); every quarter is in top\_routes\_categories.csv:

| window | dimension | rank | level | orders | outcome | outcome\_name | coefficient |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2018Q2 | route\_seller\_to\_customer\_state | 1 | SP->RJ | 798 | 0.1679 | detractor share (observed) | 0.4974 |
| 2018Q2 | route\_seller\_to\_customer\_state | 2 | SP->BA | 185 | 0.1514 | detractor share (observed) | 0.4329 |
| 2018Q2 | route\_seller\_to\_customer\_state | 3 | RJ->SP | 166 | 0.1205 | detractor share (observed) | -0.0256 |
| 2018Q2 | route\_seller\_to\_customer\_state | 4 | SP->RS | 360 | 0.1000 | detractor share (observed) | 0.0431 |
| 2018Q2 | route\_seller\_to\_customer\_state | 5 | SP->MG | 771 | 0.0999 | detractor share (observed) | 0.1112 |
| 2018Q2 | primary\_category | 1 | home\_appliances | 114 | 0.1491 | detractor share (observed) | 0.2201 |
| 2018Q2 | primary\_category | 2 | bed\_bath\_table | 761 | 0.1380 | detractor share (observed) | 0.2193 |
| 2018Q2 | primary\_category | 3 | computers\_accessories | 504 | 0.1349 | detractor share (observed) | 0.2045 |
| 2018Q2 | primary\_category | 4 | construction\_tools\_construction | 103 | 0.1262 | detractor share (observed) | -0.4290 |
| 2018Q2 | primary\_category | 5 | baby | 266 | 0.1165 | detractor share (observed) | 0.1906 |

### Checks

| check | passed | detail |
| --- | --- | --- |
| with labels blanked, only the label-free rules remove test rows (B\_DISTANCE, B\_NO\_HANDOVER, B\_STATE) | True | B\_STATE 3,252; B\_DISTANCE 144; B\_NO\_HANDOVER 36 |
| no test label is read: every label column of the rebuilt test rows is empty (B-G-08) | True | lead\_days, lead\_label\_ts, is\_detractor, is\_detractor\_first, review\_label\_ts |
| the rebuilt rows contain exactly T1's kept B test rows | True | 15,492 of 15,492 |
| every bundle reloads from disk and re-predicts T1's saved test predictions within 1e-9 | True | A frozen on A test rows: max 2.2e-16 (18,966 rows); A frozen on B test rows: max 2.2e-16 (15,492 rows); B frozen on B test rows: max 2.2e-16 (15,492 rows) |
| bundle files equal T1's tagged files; frozen recipes recompute their sha256, equal their tagged files and match the schemas; training rows and digests recompute | True |  |
| the frozen thresholds in the bundles are unchanged (1/6 for classification) | True |  |
| B's 1/6 and 4/15 test results from T1's saved predictions equal B9 threshold\_options.csv (alerts, TP, FP, FN) | True |  |
| A's out-of-scope fold counts derive exactly from B9.15 (TP and alerts are whole numbers) | True | 2,253 alerts, 519 TP over 345 validation days |
| the training profile in each bundle recomputes from T1's final-fit rows (mean and SD within 1e-9) | True |  |
| the router reproduces T1's predictions: B on B's test rows and A on the out-of-scope rows (within 1e-9) | True | B 2.2e-16, A 2.2e-16 |
| no test row is rejected by the input checks | True | 0 rejected |
| every scope reason and route occurs (in scope; customer state; seller state; before handover) | True | \['in scope', 'outside: customer state', 'outside: distance missing', 'outside: seller state'\] |
| every input-check case gives the expected outcome | True | 14 cases |
| every app element names an existing file tagged with its evidence ID | True | 20 elements |
| A's tree untouched: A's code matches e5-A-frozen | True |  |
