# s03 EDA — implementation review

> **How to read this tab.** Part A is the final, accepted state of s03 (CR-043, 2026-10-20); the report, slides and s04 use only Part A and the Part A sections of the two sub-tabs. Part B is the review record of rounds 1–3 (review table, decisions, comments), kept unchanged; its run IDs and numbers are superseded.

# Part A — Final result (accepted, cite this)

**ACCEPTED** · regression run `20261020T053125Z` · classification run `20261020T053142Z` (round 5) · both on commit 4999811, clean tree · coverage 6 of 6 and 10 of 10 IMPLEMENTED · 6 + 11 checks, all PASS · tag e5-s03-accepted · data from 2017-01-01 (G-72).

## Gate decisions (spec/human\_decisions.yaml, G-70)

| Decision | Regression | Classification |
| --- | --- | --- |
| Feature pool (`e5lib.contract.pool(task)`) | 24 contract predictors | 27 = 24 contract predictors + product\_photos\_qty, product\_description\_lenght, seller\_prior\_review\_mean (plus its derived missing indicator, kept with it) |
| Ranking measure | absolute Spearman (rank correlation ratio for the 4 categorical) | mutual information |
| Cumulative-importance threshold | 99% | 99% |
| Features inside 99% (s04 computes this officially) | 18 of 24 | 19 of 27 |
| Collinearity drops | none (identical missing-fraction pair: s04 duplicate rule) | none (same) |
| Screening candidates not adopted | — | product\_name\_lenght, est\_delivery\_days (G-35 holds), customer\_region, seller\_region, region\_pair, seller\_prior\_review\_count, seller\_prior\_detractor\_share, seller\_prior\_delivered\_count, seller\_prior\_late\_share |

**Regression, inside 99%:** distance\_km\_max, customer\_state, interstate\_share, total\_freight, primary\_category, freight\_ratio, total\_price, primary\_seller\_state, total\_weight\_g, primary\_payment\_type, total\_volume\_cm3, n\_sellers, payment\_installments\_max, purchase\_dayofweek, n\_products, purchase\_month, n\_items, n\_categories.

**Classification, inside 99% of the pool:** seller\_prior\_review\_mean, total\_freight, freight\_ratio, total\_volume\_cm3, total\_price, n\_items, product\_description\_lenght, customer\_state, total\_weight\_g, n\_products, n\_sellers, purchase\_month, distance\_km\_max, interstate\_share, primary\_category, n\_categories, primary\_seller\_state, payment\_installments\_max, product\_photos\_qty.

Evidence: the Part A sections of the sub-tabs “s03 › regression” and “s03 › classification”; files under stages/s03\_eda/\<task>/outputs/.

## Changes since the round 3 acceptance (2026-10-20)

- **CR-042 (G-71, external audit H-03).** Reviews answered at or before their own order's purchase are a data error: such orders leave classification and such reviews never count in seller history.
- **CR-043 (G-72).** Data start 2017-01-01: orders bought earlier leave both tasks and seller history, because the 2016 months are too thin to be representative.
- **Effect.** Pre-cutoff orders: regression 77,139 → 76,925, classification 77,971 → 77,736. seller\_prior\_review\_mean is now rank 1 of 36. Every 95% and 99% cut keeps the same features as in round 3; only the order of near-tied features changed. Regression stays accepted; classification was re-accepted as rounds 4 and 5 by the experiment lead (README 9.2).
- **s04 ranking specified (audit H-02).** s04 walks the pool ranking (the extended ranking filtered to the pool, re-normalised) and checks that the ranked set equals `contract.pool(task)`.

## Checks (final runs)

| Task | Check | Result | Detail | IDs |
| --- | --- | --- | --- | --- |
| regression | no order on or after the test cutoff loaded | PASS | latest purchase 2018-05-27 12:20:21, cutoff 2018-05-27 12:30:34 | 3.1, 3.3, 3.8 |
| regression | all 24 contract predictors diagnosed against lead\_days | PASS | — | 3.4, 3.5 |
| regression | importance\_ranking has the 24 contract predictors and ends at cumulative share 1.0 | PASS | 24 rows | 3.8 |
| regression | ranking measure is the pre-registered one | PASS | — | 3.8 |
| regression | outcome trends show outcomes, not volume only | PASS | — | 3.3 |
| regression | review pack lists both cut points and every flagged group | PASS | — | 3.9 |
| classification | no order on or after the test cutoff loaded | PASS | latest purchase 2018-05-26 12:12:15, cutoff 2018-05-26 12:16:34 | 3.2, 3.3, 3.8 |
| classification | all 24 contract predictors diagnosed against is\_detractor | PASS | — | 3.6, 3.7 |
| classification | importance\_ranking has the 24 contract predictors and ends at cumulative share 1.0 | PASS | 24 rows | 3.8 |
| classification | ranking measure is the pre-registered one | PASS | — | 3.8 |
| classification | outcome trends show outcomes, not volume only | PASS | — | 3.3 |
| classification | review pack lists both cut points and every flagged group | PASS | — | 3.9 |
| classification | candidate screen 3.10 covers every product candidate | PASS | 3 candidates | 3.10 |
| classification | candidate screen 3.11 covers every promise candidate | PASS | 1 candidates | 3.11 |
| classification | candidate screen 3.12 covers every region candidate | PASS | 3 candidates | 3.12 |
| classification | candidate screen 3.13 covers every seller\_history candidate | PASS | 5 candidates | 3.13 |
| classification | extended ranking holds the 24 predictors and every candidate, ends at 1.0; official ranking unchanged at 24 | PASS | 36 rows | 3.10 |

# Part B — Review record (history: rounds 1–3, do not cite)

## Round 3 review (as accepted 2026-10-19; values superseded by Part A)

### Coverage

| Task | ID | Solution step | Coverage | Checks | Review |
| --- | --- | --- | --- | --- | --- |
| regression | 3.1 | Regression target | IMPLEMENTED | PASS | Approved |
| regression | 3.3 | Outcome trends | IMPLEMENTED | PASS | Approved |
| regression | 3.4 | Numeric features vs lead\_days | IMPLEMENTED | PASS | Approved |
| regression | 3.5 | Categorical features vs lead\_days | IMPLEMENTED | PASS | Approved |
| regression | 3.8 | Importance ranking | IMPLEMENTED | PASS | Approved |
| regression | 3.9 | Human gate (review pack for s04 decisions) | IMPLEMENTED | PASS | Approved |
| classification | 3.2 | Classification target | IMPLEMENTED | PASS | Approved |
| classification | 3.3 | Outcome trends | IMPLEMENTED | PASS | Approved |
| classification | 3.6 | Numeric features vs is\_detractor | IMPLEMENTED | PASS | Approved |
| classification | 3.7 | Categorical features vs is\_detractor | IMPLEMENTED | PASS | Approved |
| classification | 3.8 | Importance ranking | IMPLEMENTED | PASS | Approved |
| classification | 3.9 | Human gate (review pack for s04 decisions) | IMPLEMENTED | PASS | Approved |
| classification | 3.10 | Candidate screen: product fields and extended ranking (G-68; extended in round 3) | IMPLEMENTED | PASS | Approved |
| classification | 3.11 | Candidate screen: promised delivery days (G-69, new in round 3) | IMPLEMENTED | PASS | Approved |
| classification | 3.12 | Candidate screen: regions (G-69, new in round 3) | IMPLEMENTED | PASS | Approved |
| classification | 3.13 | Candidate screen: seller history at checkout (G-69, new in round 3) | IMPLEMENTED | PASS | Approved |

### Human gate: decisions the team records (spec/human\_decisions.yaml)

The pipeline stops here. For each task the team picks the cumulative-importance threshold (95% or 99%) and, for each flagged collinear group, which feature to drop with its rationale. The values below are the computed options; nothing is chosen by code.

**Regression** (ranking by absolute Spearman):

- 95% keeps the top 14: distance\_km\_max, customer\_state, interstate\_share, total\_freight, primary\_category, freight\_ratio, total\_price, primary\_seller\_state, total\_weight\_g, primary\_payment\_type, total\_volume\_cm3, n\_sellers, payment\_installments\_max, purchase\_dayofweek; drops n\_products, purchase\_month, n\_items, n\_categories, distance\_missing\_fraction, category\_missing\_fraction, n\_payment\_methods, volume\_missing\_fraction, weight\_missing\_fraction, purchase\_hour
- 99% keeps the top 18: distance\_km\_max, customer\_state, interstate\_share, total\_freight, primary\_category, freight\_ratio, total\_price, primary\_seller\_state, total\_weight\_g, primary\_payment\_type, total\_volume\_cm3, n\_sellers, payment\_installments\_max, purchase\_dayofweek, n\_products, purchase\_month, n\_items, n\_categories; drops distance\_missing\_fraction, category\_missing\_fraction, n\_payment\_methods, volume\_missing\_fraction, weight\_missing\_fraction, purchase\_hour
- Collinear groups needing a decision: none. Identical columns (automatic s04 drop): weight\_missing\_fraction = volume\_missing\_fraction.

**Classification** (ranking by mutual information):

- 95% keeps the top 14: total\_freight, freight\_ratio, total\_volume\_cm3, total\_price, n\_items, total\_weight\_g, customer\_state, n\_products, n\_sellers, purchase\_month, distance\_km\_max, primary\_category, interstate\_share, n\_categories; drops primary\_seller\_state, payment\_installments\_max, category\_missing\_fraction, purchase\_hour, purchase\_dayofweek, distance\_missing\_fraction, primary\_payment\_type, volume\_missing\_fraction, weight\_missing\_fraction, n\_payment\_methods
- 99% keeps the top 17: total\_freight, freight\_ratio, total\_volume\_cm3, total\_price, n\_items, total\_weight\_g, customer\_state, n\_products, n\_sellers, purchase\_month, distance\_km\_max, primary\_category, interstate\_share, n\_categories, primary\_seller\_state, payment\_installments\_max, category\_missing\_fraction; drops purchase\_hour, purchase\_dayofweek, distance\_missing\_fraction, primary\_payment\_type, volume\_missing\_fraction, weight\_missing\_fraction, n\_payment\_methods
- Collinear groups needing a decision: none. Identical columns (automatic s04 drop): weight\_missing\_fraction = volume\_missing\_fraction.

**Classification, round 3 (3.10–3.13, G-68, G-69):** the official 24-predictor ranking above is unchanged. Adopted so far: product\_photos\_qty and product\_description\_lenght (Henry and the lead, recorded in human\_decisions.yaml); product\_name\_lenght not adopted. Still to decide per candidate: est\_delivery\_days (3.11), customer\_region, seller\_region, region\_pair (3.12) and the five seller\_prior\_\* columns (3.13), plus one collinear group: seller\_prior\_review\_count and seller\_prior\_delivered\_count (Spearman 0.999, VIF about 1,440): keep one. The threshold is 99% for both tasks (Henry, as a share, not a feature count); s04 applies it to the agreed pool (24 + adopted), so the number of features follows from the adoption. For reference, the extended ranking over 24 + all 12 candidates gives 95% → top 22, 99% → top 27; seller\_prior\_review\_mean ranks 2nd of 36.

Recommendation from the Feature solution tab: 95%, with 99% only if 95% drops a feature the EDA shows to be clearly useful. Please reply in a comment with the threshold per task; I record it in human\_decisions.yaml and the CHANGELOG.

### Method decisions for the team

1. **Categorical predictors in the regression ranking (3.5, 3.8).** Spearman needs an ordered feature, so the four categorical predictors are scored by the rank correlation ratio: the target is ranked, each level is replaced by its mean rank, and the correlation of the two is taken (the square root of the Kruskal–Wallis epsilon-squared). It is 0 when every level has the same distribution and lies on the same 0–1 scale as |Spearman|, so the cumulative share stays meaningful. The blueprint says "absolute Spearman" without saying how a nominal feature gets one. Please confirm.
2. **Features with few values in the classification diagnostics (3.6, 3.8).** A KDE smears an integer count into impossible values, so numeric features with at most 30 distinct values use the class frequencies for the overlap coefficient and the contingency (discrete) estimator for mutual information; continuous features use the KDE (on the log1p scale for the five log1p candidates; the coefficient does not change under a monotone transform) and the k-NN estimator. Please confirm.
3. **Identical columns are not a team decision (3.8).** weight\_missing\_fraction and volume\_missing\_fraction are identical on every pre-cutoff order in both tasks, so the s04 duplicate rule (4.3) drops one automatically; they are listed, not offered as a collinear group. Please confirm.
4. **Trend ranges quoted over months with at least 100 orders (3.3).** The first months hold 1 to 285 orders (2016-09 has one order), so the min–max ranges in the cards use months with at least 100 orders; the table and figure keep every month. Please confirm.

**Note for the adoption decision (3.10).** product\_description\_lenght ranks 8th by mutual information but its ROC-AUC is 0.492 (close to no ranking signal). The two measures disagree because mutual information also counts a non-monotonic pattern, and the k-NN estimator on a continuous feature tends to give larger values than the contingency estimator on a count. Tree models could use such a pattern; linear and logistic models mostly cannot. All three candidates are weak on their own (ROC-AUC 0.480 to 0.504, overlap above 96%).

### Checks

| Task | Check | Result | Detail | IDs |
| --- | --- | --- | --- | --- |
| regression | no order on or after the test cutoff loaded | PASS | latest purchase 2018-05-26 18:16:57, cutoff 2018-05-26 18:18:03 | 3.1, 3.3, 3.8 |
| regression | all 24 contract predictors diagnosed against lead\_days | PASS | — | 3.4, 3.5 |
| regression | importance\_ranking has the 24 contract predictors and ends at cumulative share 1.0 | PASS | 24 rows | 3.8 |
| regression | ranking measure is the pre-registered one | PASS | — | 3.8 |
| regression | outcome trends show outcomes, not volume only | PASS | — | 3.3 |
| regression | review pack lists both cut points and every flagged group | PASS | — | 3.9 |
| classification | no order on or after the test cutoff loaded | PASS | latest purchase 2018-05-25 18:43:19, cutoff 2018-05-25 18:44:28 | 3.2, 3.3, 3.8 |
| classification | all 24 contract predictors diagnosed against is\_detractor | PASS | — | 3.6, 3.7 |
| classification | importance\_ranking has the 24 contract predictors and ends at cumulative share 1.0 | PASS | 24 rows | 3.8 |
| classification | ranking measure is the pre-registered one | PASS | — | 3.8 |
| classification | outcome trends show outcomes, not volume only | PASS | — | 3.3 |
| classification | review pack lists both cut points and every flagged group | PASS | — | 3.9 |
| classification | candidate screen 3.10 / 3.11 / 3.12 / 3.13 covers every product / promise / region / seller\_history candidate | PASS | 3 / 1 / 3 / 5 candidates | 3.10–3.13 |
| classification | extended ranking holds the 24 predictors and every candidate, ends at 1.0; official ranking unchanged at 24 | PASS | 36 rows | 3.10 |

## Round history

### Round 1 — 2026-10-19

- First build of s03 for both tasks on pre-cutoff development orders (data.load population guard). New foundation modules e5lib/eda.py and eda\_sections.py with unit tests (CR-036).
- The foundation change made s01 and s02 stale; both rerun with identical value outputs and stay ACCEPTED.
- Comments and resolutions: Henry agreed 3.1–3.4 and 3.2; proposed thresholds regression 99% (top 18, keeps purchase\_month) and classification 99% (top 17), recorded at the gate. B asked about untranslated categories: kept as the Unknown level (answered in thread; lead: keep them as Unknown). Henry asked for a product-field screen and est\_delivery\_days: the lead approved the screen of product\_photos\_qty, product\_description\_lenght and product\_name\_lenght and kept G-35 (no est\_delivery\_days) → round 2.

### Round 2 — 2026-10-19

- CR-037 (G-68): s01 registers the three screening candidates (classification only, not predictors); s02 builds them as the primary item's value (populations, exclusions and test cutoffs unchanged); s01 and s02 stay ACCEPTED, with a dated addendum on their tabs for review.
- Classification: new card 3.10 (candidate screen); cards 3.2–3.9 unchanged in value (shared files eda\_summary.json and candidate\_rationale.csv gained the 3.10 rows). Regression: rerun only because records gained columns; every evidence hash equals round 1.
- Runs 20261019T140119Z (regression) and 20261019T140130Z (classification); 38 tests pass.

### Round 3 — 2026-10-19

- Round 2 review: 3.10 Approved; 3.6 marked Change (Henry's request for more classification features) and answered by the candidate screen 3.10–3.13 (3.6 itself is unchanged). Adopted: product\_photos\_qty, product\_description\_lenght. Thresholds: Henry, 99% for both tasks (as a share).
- CR-038 (G-69), lead's decisions: est\_delivery\_days screened (G-35 reopened for this screen only); regions as IBGE macro-regions plus the customer>seller pair (not numeric state codes); seller history at checkout with the late share. Built in s02 (populations and cutoffs unchanged; seller history checked against a direct recomputation on 2,000 orders); s01 and s02 stay ACCEPTED with a dated addendum.
- Classification cards 3.11–3.13 new; 3.10 extended to every candidate (the round 2 card is kept at the end of the classification sub-tab). Regression unchanged (every evidence hash equals round 2). Runs 20261019T151309Z and 20261019T151336Z; 40 tests pass.

* Outcome: accepted by the experiment lead on 2026-10-19 (CR-039, G-70). Adopted after the round 3 advice: seller\_prior\_review\_mean only of the seller history (the rating customers see; detractor share is near-duplicate of the mean, Spearman −0.87, and late share is not shown to customers). Committed and tagged e5-s03-accepted together with the s01 and s02 changes of CR-037 and CR-038.

### Round 4 — 2026-10-20 (CR-042, classification only)

- External audit of s01–s03 validated; the experiment lead asked to rectify what was not correct and decided the result (“decide for me”).
- Fix G-71: reviews answered at or before their own order's purchase are a data error; such orders leave classification and such reviews no longer count in seller history. s01–s03 rerun on a clean tree (commit aca98ac).
- Classification decision.json changed only in the order of near-tied features (REOPENED by the orchestrator); the 99% pool selection, adopted candidates and every gate decision are unchanged, so round 4 was accepted. Regression values byte-identical, stays accepted.
- The tabs were restructured: Part A (final result) on top, Part B (this review record) below.

### Round 5 — 2026-10-20 (CR-043, classification; regression stays accepted)

- Team comment on the s02 tab: the 2016 purchase months are too thin to be representative (4, 324, 0 and 1 orders). The experiment lead set the data start to 2017-01-01 for both tasks and seller history (G-72).
- s01–s03 rerun on a clean tree (commit 4999811). Regression: values shift slightly, the 95% and 99% cuts keep the same features, decision unchanged. Classification: decision.json changed only in the order of near-tied features (REOPENED by the orchestrator); every cut keeps the same features and the gate decisions stand, so round 5 was accepted.
- Part A at the top of this tab and its sub-tabs now shows the CR-043 result.
