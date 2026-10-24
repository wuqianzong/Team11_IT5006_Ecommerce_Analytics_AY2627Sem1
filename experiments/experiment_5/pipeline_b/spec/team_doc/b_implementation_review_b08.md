# B8 Selection — implementation review (gate)

**Round 1 · AT THE GATE · not frozen, test not read · team review of B6–B8 now (G-78).** Runs `20261024T032040Z` (regression) and `20261024T032112Z` (classification) on uncommitted code (working tree on 171f23d). 7 + 9 checks, all PASS. B8.1–B8.4 run A's own s08 code on B's inputs through the adapter; tests/test\_adapter.py shows that the same adapter fed A's inputs and A's decisions reproduces A's frozen recipes with the same sha256 (both tasks). B8.A and B8.M are new B code. Evidence is in the two sub-tabs.

## FROZEN 2026-10-24 (B8.5) · tag e5-B-frozen · test not read

The team's decisions (Henry and the experiment lead; human\_decisions\_B.yaml b08) are applied. Clean reruns `20261024T042516Z` (regression) and `20261024T042619Z` (classification) on code commit a4a0ded give 9 + 14 checks, all PASS, and are byte-identical to the first freeze run. The tables further down this tab were written at the gate on raw probabilities; for classification the frozen figures below replace them (B-G-05).

| Task | Frozen model | Calibration | Threshold and cap | Out-of-fold at the threshold | sha256 (frozen\_recipe.json) |
| --- | --- | --- | --- | --- | --- |
| regression | reg.sel.log.linear | — | — | — | 8f1241b5bc5fdc27… |
| classification | clf.sel.log.logistic | sigmoid (B-G-05, deviation from the 8.3 rule) | 1/6, cap 25/day | 17.0 alerts/day, precision 0.298, recall 0.250 | da056ab74eff0957… |

**A vs B on B's validation rows, both sigmoid as deployed** (metrics\_by\_population.csv): AP A 0.2302 vs B 0.2482; ROC-AUC A 0.626 vs B 0.637; Brier A 0.1162 vs B 0.1146.

**Confusion matrices at 1/6, all five folds pooled** (confusion\_comparison.csv; per fold in the file): A: 1,517 TP, 4,410 FP, 5,483 FN (precision 0.256, recall 0.217). B: 1,749 TP, 4,116 FP, 5,251 FN (precision 0.298, recall 0.250). B catches 232 more detractors with 62 fewer alerts.

Next: the joint test run (A and B, one read), then B9/B10. Fuller documentation (charts, sigmoid tables in the sub-tabs) is on the post-pipeline list (DOC\_GAPS.md).

## Decisions needed from the team (human\_decisions\_B.yaml b08)

| Task | Field | Recommendation from the evidence | Your decision |
| --- | --- | --- | --- |
| regression | model | reg.sel.log.linear (one-SE recommendation; forest best mean, within one SE) |  |
| classification | model | clf.sel.log.logistic (one-SE recommendation; forest best mean, within one SE) |  |
| classification | calibration | by the agreed rule (8.3): raw probabilities. | confirm |
| classification | threshold and daily alert cap | decided again for B (B's scope and prediction time differ from A's); candidates below |  |

**Threshold candidates, B classification** (threshold\_table.csv, out-of-fold, raw recommended model):

| candidate | threshold | alerts\_per\_day | alert\_rate | error\_rate | precision | recall | f1 | cost | extra\_false\_alarms\_per\_extra\_detractor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| no alerts | inf | 0.0000 | 0.0000 | 0.1394 | 0.0000 | 0.0000 | 0.0000 | 35000.0000 |  |
| 0.50 | 0.5000 | 1.0087 | 0.0069 | 0.1386 | 0.5603 | 0.0279 | 0.0531 | 34178.0000 | 0.7846 |
| 1/6 (cost cutoff) | 0.1667 | 19.1652 | 0.1317 | 0.1936 | 0.2943 | 0.2780 | 0.2859 | 29936.0000 | 2.5774 |
| empirical minimum of 5\*FN + FP | 0.1306 | 33.9507 | 0.2333 | 0.2549 | 0.2524 | 0.4223 | 0.3159 | 28977.0000 | 4.0505 |

**Side by side with A's gate decisions:**

| Item | A (frozen, e5-A-frozen; frozen\_recipe.json) | B (options at this gate) |
| --- | --- | --- |
| regression model | reg.sel.log.linear | recommended reg.sel.log.linear |
| classification model | clf.sel.log.logistic | recommended clf.sel.log.logistic |
| calibration | sigmoid | by the rule (8.3): raw probabilities |
| threshold | 0.1667 (1/6) | to decide; 1/6 shown below |
| daily alert cap | 25 | to decide (threshold\_by\_cap.csv in the classification sub-tab) |
| out-of-fold alerts/day, precision, recall at 1/6 | 23.9, 0.252, 0.223 (A's population, at checkout) | 19.2, 0.294, 0.278 (B's population, at handover) |

**If the team chose another finalist, would B still be adopted?** (adoption\_by\_finalist\_summary.csv; gain > 0 = B better than A's frozen model on the same rows; fold-by-fold in the sub-tabs)

| Task | Finalist | B mean | Mean gain over A | Paired SE | Folds B better | B adopted if chosen |
| --- | --- | --- | --- | --- | --- | --- |
| regression | reg.sel.log.dummy\_median | 5.9689 | -0.8266 | 0.1137 | 0 of 5 | no |
| regression | reg.sel.log.linear | 5.0247 | +0.1176 | 0.0594 | 5 of 5 | yes |
| regression | reg.sel.log.tree\_reg.max\_depth=5.min\_samples\_leaf=100 | 5.0532 | +0.0891 | 0.0791 | 3 of 5 | yes |
| regression | reg.sel.log.forest\_reg.max\_depth=10.max\_features=sqrt.min\_samples\_leaf=50 | 4.9627 | +0.1796 | 0.0445 | 5 of 5 | yes |
| classification | clf.sel.log.dummy\_prior | 0.1380 | -0.1039 | 0.0175 | 0 of 5 | no |
| classification | clf.sel.log.logistic | 0.2616 | +0.0197 | 0.0050 | 5 of 5 | yes |
| classification | clf.sel.log.tree\_clf.max\_depth=5.min\_samples\_leaf=100 | 0.2394 | -0.0025 | 0.0052 | 3 of 5 | no |
| classification | clf.sel.log.forest\_clf.max\_depth=10.max\_features=sqrt.min\_samples\_leaf=50 | 0.2739 | +0.0320 | 0.0077 | 5 of 5 | yes |

## Current (round 1)

### Coverage

| Task | ID | Coverage | Review |
| --- | --- | --- | --- |
| regression | B8.1 | IMPLEMENTED | Approved |
| regression | B8.2 | IMPLEMENTED | Approved |
| regression | B8.A | IMPLEMENTED | Approved |
| classification | B8.1 | IMPLEMENTED | Approved |
| classification | B8.2 | IMPLEMENTED | Approved |
| classification | B8.3 | IMPLEMENTED | Approved |
| classification | B8.4 | IMPLEMENTED | Approved |
| classification | B8.A | IMPLEMENTED | Approved |
| classification | B8.M | IMPLEMENTED | Approved |
| regression | B8.5 Freeze | MISSING (after the team's decisions, by design) | Approved |
| classification | B8.5 Freeze | MISSING (after the team's decisions, by design) | Approved |

### Points for review

1. **B beats A on the same rows in both tasks (G-79 fold rule).** Regression: mean paired gain +0.1176 days MAE (paired SE 0.0594), B better in 5 of 5 folds. Classification: +0.0197 AP (paired SE 0.0050), better in 5 of 5 folds. By the agreed rule B is adopted for both tasks. A and B both go to the joint test run, and the test does not re-choose (adoption\_decision.json).
2. **Classification compares different prediction moments.** A scores at checkout, B at carrier handover, as the CR-054 limitations state. The gain includes the value of the later moment.
3. **Where B's advantage comes from (R-02).** Regression MAE: A on A's rows 5.470 → A on B's rows 5.142 (scope) → B on B's rows 5.025 days (B's features). Classification AP: 0.2435 → 0.2419 → 0.2616. So on regression most of the drop comes from the scope; on classification the scope changes little and the gain comes from B's features and prediction time. Mean ± SE by population and the per-fold decomposition are in each sub-tab (population\_summary.csv, se\_decomposition.csv).
4. **Calibration differs from A.** For B the agreed rule keeps raw probabilities: mean Brier raw 0.11414 vs sigmoid 0.11461; mean AP raw 0.2616 vs sigmoid 0.2482 (one fold SE 0.0349). A kept sigmoid. The team confirms.
5. **Threshold and cap are B's own decision.** At 1/6 on B's out-of-fold probabilities the table above gives the alerts per day; A's cap of 25 per day was set for A's population and prediction time.
6. **Missed-dispatch rule (B-C10).** On B's development population the rule flags 5,904 orders, with 1,805 detractors (precision 0.306, 20.3% of all detractors). Orders never handed over are mostly detractors (missed\_dispatch\_rule.csv). It is a rule reported beside the classifier, not part of it.
7. **Grid edges.** Both recommendations are plain B6 models, not grid configurations. The B7 grid-edge note matters only if the team picks a tuned configuration.
8. **Finalist choice and adoption.** The forest has the best mean in both tasks and beats A by more than the recommended model does (table above), but stays within one SE of it, so the agreed one-SE rule recommends the simpler model. Choosing the forest would be an override of the agreed rule (G-44). The table shows B is adopted either way.

## Round history

### Round 1 — 2026-10-24

- First build: e5b/b08.py, e5b/adoption.py, the adapter's s08 inputs, and the s08 equivalence test (both tasks pass). Run to the gate; not frozen, not committed.
- Added at the lead's request: fold-by-fold results of every finalist, adoption for every finalist, the full threshold curve, the best threshold under each daily cap, threshold results by fold, the reliability curve, and A's gate decisions side by side.
- Henry: no comments on B8 yet.
