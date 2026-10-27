# B10 › regression (round 3)

**Built for review · run `20261027T044744Z` on commit 906fe39 (clean, dirty: false) · 13 checks, 13 PASS.** Blueprint spec/blueprints/b10\_release.md (AGREED). Nothing is refitted and the test is not read again (B-G-08, B10-D10). Every number below is read from pipeline\_b/stages/b10/regression/outputs/.

## B10.1 Reload parity

**What was done:** Bundles reloaded from disk re-predict T1's saved test predictions on rows rebuilt with every label column empty (B-G-08): A frozen on A test rows max difference 2.1e-14 over 18,788 rows; A frozen on B test rows max difference 1.8e-14 over 15,422 rows; B frozen on B test rows max difference 1.4e-14 over 15,422 rows. Python 3.13.7.

| model | rows | n\_rows | n\_t1\_rows | max\_abs\_diff | within\_tolerance |
| --- | --- | --- | --- | --- | --- |
| A frozen | A test rows | 18788 | 18788 | 2.1e-14 | True |
| A frozen | B test rows | 15422 | 15422 | 1.8e-14 | True |
| B frozen | B test rows | 15422 | 15422 | 1.4e-14 | True |

## B10.2 Release manifest

**What was done:** Release manifest: sha256 of every bundle file (equal to tag e5-T1-tested), frozen recipes equal to their tags (A e5-A-frozen, B e5-B-frozen), training digests recomputed. Version differences: {"A": {}, "B": {}}

| bundle | model | calibration | training rows | files equal T1 tag | recipe equals its tag | digest recomputes | version differences |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | reg.sel.log.linear |  | 74834 | True | True | True | {} |
| B | reg.sel.log.linear |  | 59683 | True | True | True | {} |

## B10.3 Serving configuration

**What was done:** Serving: B inside its scope, A outside (B-G-06), both at checkout. Test rows inside 15,422, outside 3,366.

## B10.4 Router

**What was done:** Router (e5b/serving.py) on every A test row: reproduces T1 within 2.1e-14. Routes: in scope / B frozen / scored: 15,422; outside: customer state / A frozen / scored: 2,790; outside: distance missing / A frozen / scored: 144; outside: seller state / A frozen / scored: 432

| scope\_reason | model | status | orders |
| --- | --- | --- | --- |
| in scope | B frozen | scored | 15422 |
| outside: customer state | A frozen | scored | 2790 |
| outside: distance missing | A frozen | scored | 144 |
| outside: seller state | A frozen | scored | 432 |

B rows outside T1's kept set (regression: above the lead cap; classification: review answered before handover) are scored by B at serving time but have no T1 prediction to compare with.

## B10.5 Input checks

**What was done:** 10 input rules; 13 of 13 test cases give the expected outcome (input\_validation.json).

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

## B10.6 Drift profile

**What was done:** Training ranges per feature from T1's final-fit rows; shares of test rows beyond 3, 4 and 5 SD in out\_of\_profile\_shares.csv. The app warns beyond 4 SD (B10-D11); warning only.

Largest shares of test rows beyond 3 SD of the training mean (all features in out\_of\_profile\_shares.csv):

| pipeline | feature | rows | n\_rows | share\_beyond\_3sd | share\_beyond\_4sd | share\_beyond\_5sd |
| --- | --- | --- | --- | --- | --- | --- |
| B | n\_products | B test rows | 15422 | 0.0329 | 0.0329 | 0.0038 |
| A | n\_products | A test rows | 18788 | 0.0325 | 0.0325 | 0.0041 |
| A | total\_freight | A test rows | 18788 | 0.0263 | 0.0134 | 0.0086 |
| B | total\_freight | B test rows | 15422 | 0.0244 | 0.0128 | 0.0080 |
| B | n\_items | B test rows | 15422 | 0.0226 | 0.0089 | 0.0089 |
| A | n\_items | A test rows | 18788 | 0.0217 | 0.0087 | 0.0087 |
| A | total\_price | A test rows | 18788 | 0.0192 | 0.0111 | 0.0084 |
| A | freight\_ratio | A test rows | 18788 | 0.0188 | 0.0076 | 0.0041 |

## B10.7 App sources and R-14

**What was done:** 17 app elements mapped to files and evidence IDs (app\_sources.json); R-14 top 5 routes and categories per quarter with at least 100 orders, observed outcomes on development rows, coefficient beside (top\_routes\_categories.csv).

| panel | element | file | evidence\_id |
| --- | --- | --- | --- |
| headline | test metrics of A and B | pipeline\_b/stages/t1\_joint\_test/regression/outputs/metrics\_test.csv | T1.3 |
| headline | train, validation and test with 95% intervals | pipeline\_b/stages/b09/regression/outputs/train\_val\_test.csv | B9.1 |
| headline | B minus A on the same test orders | pipeline\_b/stages/b09/regression/outputs/paired\_test\_differences.csv | B9.2 |
| fit | validation folds and test together | pipeline\_b/stages/b09/regression/outputs/validation\_and\_test.csv | B9.14 |
| fit | fold-by-fold and test table | pipeline\_b/stages/t1\_joint\_test/regression/outputs/fold\_and\_test\_table.csv | T1.6 |
| where it errs | slices by state, route and more | pipeline\_b/stages/b09/regression/outputs/subgroups.csv | B9.3 |
| where it errs | business summary by route | pipeline\_b/stages/b09/regression/outputs/business\_by\_route.csv | B9.13 |
| why | coefficients | pipeline\_b/stages/b09/regression/outputs/coefficients.csv | B9.5 |
| why | permutation importance | pipeline\_b/stages/b09/regression/outputs/permutation\_importance.csv | B9.5 |
| data health | drift, development vs test | pipeline\_b/stages/b09/regression/outputs/drift.csv | B9.4 |
| data health | training profile and out-of-profile shares | pipeline\_b/stages/b10/regression/outputs/drift\_profile.json | B10.6 |
| score | serving rule and thresholds | pipeline\_b/stages/b10/regression/outputs/serving\_config.json | B10.3 |
| score | input checks | pipeline\_b/stages/b10/regression/outputs/input\_validation.json | B10.5 |
| fallback | A inside and outside B's scope | pipeline\_b/stages/b09/regression/outputs/a\_fallback\_by\_scope.csv | B9.15 |
| fit | residual distribution and promise buffers | pipeline\_b/stages/b09/regression/outputs/residuals\_summary.csv | B9.16 |
| fit | errors on B's test rows | pipeline\_b/stages/t1\_joint\_test/regression/outputs/figures/test\_errors.png | T1.3 |
| dashboard (R-14) | top 5 routes and categories by quarter | pipeline\_b/stages/b10/regression/outputs/top\_routes\_categories.csv | B10.7 |

R-14, latest development quarter (2018Q2); every quarter is in top\_routes\_categories.csv:

| window | dimension | rank | level | orders | outcome | outcome\_name | coefficient |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2018Q2 | route\_seller\_to\_customer\_state | 1 | SP->BA | 208 | 19.5387 | mean lead\_days (observed) | -0.0743 |
| 2018Q2 | route\_seller\_to\_customer\_state | 2 | SP->RJ | 853 | 12.6044 | mean lead\_days (observed) | -0.0373 |
| 2018Q2 | route\_seller\_to\_customer\_state | 3 | SP->RS | 383 | 12.4151 | mean lead\_days (observed) | -0.1294 |
| 2018Q2 | route\_seller\_to\_customer\_state | 4 | SP->SC | 253 | 11.5780 | mean lead\_days (observed) | -0.0549 |
| 2018Q2 | route\_seller\_to\_customer\_state | 5 | SP->MG | 796 | 10.4333 | mean lead\_days (observed) | -0.1753 |
| 2018Q2 | primary\_category | 1 | watches\_gifts | 666 | 10.1687 | mean lead\_days (observed) | 0.0149 |
| 2018Q2 | primary\_category | 2 | cool\_stuff | 250 | 9.9743 | mean lead\_days (observed) | -0.0551 |
| 2018Q2 | primary\_category | 3 | garden\_tools | 301 | 9.4341 | mean lead\_days (observed) | -0.0036 |
| 2018Q2 | primary\_category | 4 | pet\_shop | 214 | 9.2208 | mean lead\_days (observed) | -0.0766 |
| 2018Q2 | primary\_category | 5 | furniture\_decor | 624 | 9.1464 | mean lead\_days (observed) | -0.0004 |

## Checks

| check | passed | detail |
| --- | --- | --- |
| with labels blanked, only the label-free rules remove test rows (B\_DISTANCE, B\_STATE) | True | B\_STATE 3,222; B\_DISTANCE 144 |
| no test label is read: every label column of the rebuilt test rows is empty (B-G-08) | True | lead\_days, lead\_label\_ts, is\_detractor, is\_detractor\_first, review\_label\_ts |
| the rebuilt rows contain exactly T1's kept B test rows | True | 15,422 of 15,422 |
| every bundle reloads from disk and re-predicts T1's saved test predictions within 1e-9 | True | A frozen on A test rows: max 2.1e-14 (18,788 rows); A frozen on B test rows: max 1.8e-14 (15,422 rows); B frozen on B test rows: max 1.4e-14 (15,422 rows) |
| bundle files equal T1's tagged files; frozen recipes recompute their sha256, equal their tagged files and match the schemas; training rows and digests recompute | True |  |
| the frozen thresholds in the bundles are unchanged (1/6 for classification) | True |  |
| the training profile in each bundle recomputes from T1's final-fit rows (mean and SD within 1e-9) | True |  |
| the router reproduces T1's predictions: B on B's test rows and A on the out-of-scope rows (within 1e-9) | True | B 1.4e-14, A 2.1e-14 |
| no test row is rejected by the input checks | True | 0 rejected |
| every scope reason and route occurs (in scope; customer state; seller state) | True | ['in scope', 'outside: customer state', 'outside: distance missing', 'outside: seller state'] |
| every input-check case gives the expected outcome | True | 13 cases |
| every app element names an existing file tagged with its evidence ID | True | 17 elements |
| A's tree untouched: A's code matches e5-A-frozen | True |  |

