# B9 Conclusion — for team review

## ACCEPTED 2026-10-25 (tag e5-B-s09-accepted)

Confirmed by Henry and the experiment lead: B is the delivered model inside the seven states, and A stays valid outside them (B-G-06). The operating threshold is 4/15 (B-G-07). No slice or limitation is open. Accepted clean reruns on b09c396 are byte-identical to the build runs cited in this tab and its sub-tabs (EVIDENCE.md).

Added at confirmation:

- B9.14 time windows on the validation-and-test chart (R-17).
- B9.16 residual distribution (R-16): 4.7% of B's test orders arrive more than 6 days after its prediction (11.1% more than 3 days); see the regression sub-tab.
- Report notes: R-15 (importance vs B4 ranking) and R-18 (report and deck layout).

The four thin classification states have 53 to 81 test detractors each (subgroups.csv), above Henry's 50, so no extra note is needed.

Next: B10, then the report, deck, dashboard and reproduction, when the lead starts them.

**Built · runs `20261024T052445Z` (regression) and `20261024T052644Z` (classification) on uncommitted code · 6 + 6 checks, all PASS.** Blueprint spec/blueprints/b09\_conclusion.md (AGREED; B9-D1 to B9-D4). B9 reads T1's frozen predictions only: B's and A's bundles re-predict T1's test rows (within 1e-9, CSV rounding), nothing is refitted and the threshold is unchanged (G-79). Scope (lead, 2026-10-24): implementation and conclusion only; B10 release, report, deck, dashboard and reproduction start after the team confirms this conclusion.

## Round 2 — Henry's B9 review (added 2026-10-25)

Runs `20261025T091027Z` (regression) and `20261025T090945Z` (classification), uncommitted, 6 + 7 checks, all PASS. Read only; the frozen models and the T1 test read are unchanged.

**Decisions recorded (experiment lead, 2026-10-25):**

- **B-G-07** Operating threshold for classification **4/15**, a post-test business change. The frozen 1/6 stays in the frozen recipe and its T1 result stays the unbiased test result.
- **B-G-06** Orders inside B's scope are predicted by B; orders outside it fall back to A's frozen model.

**What round 2 adds** (details in the sub-tabs):

- Operating threshold 4/15 (B-G-07, post-test) vs frozen 1/6 on B's rows. Validation: 4.0 alerts/day, FP per TP 1.35, recall 0.084 (1/6: 17.0/day, 2.35, 0.250). Test: 5.6/day, FP per TP 1.89, precision 0.346, recall 0.121 (1/6: 23.2/day, 3.81). Cost 5:1 at 4/15 7,123 vs 7,156 at 1/6; cost 1:1 1,707 vs 2,844.
- Payment type (regression): Lead time starts at purchase; Olist approves an order when payment clears. Development rows: median purchase-to-approval boleto 1.21 days vs credit card 0.01; mean lead time 13.24 vs 12.04 days; lead time after approval 11.87 vs 11.87. Payment type stands for payment-clearance delay, not delivery quality (observation).
- A outside B's scope, regression: A's frozen model by B's scope (B-G-06 fallback). Validation MAE mean over 5 folds: inside 5.1827, outside 6.7480. Test: inside 4.0280 (15,422 orders), outside 5.7491 \[5.5929, 5.8946\] (3,366 orders).
- A outside B's scope, classification: A's frozen model by B's scope (B-G-06 fallback). Validation AP mean over 5 folds: inside 0.2356, outside 0.2257. Test: inside 0.1798 (15,570 orders), outside 0.1614 \[0.1350, 0.1964\] (3,396 orders).
- Drift by fold (A and B, for the appendix): Training vs validation drift per fold for A and B, plus final fit vs test (SMD for numeric features and the target, TVD for categorical). Numeric features with |SMD| >= 0.2 in at least 3 of the 6 periods: A purchase\_month (6), B purchase\_month (6), B route\_recent\_carrier\_transit\_days (4), B route\_recent\_delivery\_days (4).
- Business summary by route: regression — Routes judged (at least 100 orders): 20 of 48 on B's test rows; B has the lower MAE on 20 of them. A on all of A's test routes is listed too (in or out of B's scope). Classification — Routes judged (more than 100 detractors): 3 of 48 on B's test rows; A on all of A's test routes is listed too (in or out of B's scope).
- Validation folds and test together: tables and charts in both sub-tabs (B9.14).

**Updates to the conclusion below:** the scope limitation is now covered by B-G-06 (B9.15), and the classification threshold question is decided (B-G-07). Report notes: ratio\_per\_unit = e^coefficient, odds\_ratio = e^coefficient and the bootstrap wording are added to the Report notes tab (§8).

## Regression — delivery lead time

Every number below is read from this folder's files or T1's metrics\_test.csv. Validation scores are selection scores (G-10); only test numbers are unbiased.

### Answer

- B predicts delivery lead time better than A on the same test orders: MAE 3.299 vs 4.028 days, difference -0.729 \[-0.754, -0.703\] (paired bootstrap, paired\_test\_differences.csv).
- B is within 3 days of the actual lead time for 57.6% of its test orders (A on the same orders 44.3%).
- B beats its dummy reference (MAE 4.385); the frozen model is the plain linear recipe, so the plain reference equals it.

### Limitations

- Scope: seven states (B-C1); orders outside them are not covered by B. How they are served (A's model or no prediction) is open for the team, for B10.
- Prediction moments differ: checkout for regression, carrier handover for classification; the classifier cannot act before handover.
- Fold 1 is below A's training-row minimum (B-G-01); the 5-fold comparison keeps it.
- B's history features for test rows use earlier test weeks (J-1 (a)), as in deployment; the test gain may partly reflect that recency.
- The test period is the newest and differs from development (G-77); A's classification test cohort is below the 15% detractor share (G-75).
- No causal claims: features describe association, not the effect of an intervention.

### Questions for the team

1. Confirm B as the delivered model for this task (G-79), on the test evidence above.
2. Any slice or limitation that must be resolved before B10 and the report?

## Classification — detractor alert at handover

Every number below is read from this folder's files or T1's metrics\_test.csv. Validation scores are selection scores (G-10); only test numbers are unbiased.

### Answer

- B ranks detractors better than A on the same test orders: AP 0.1972 vs 0.1785, difference +0.0187 \[+0.0089, +0.0291\] (paired bootstrap).
- At the frozen threshold 1/6, B sends 23.2 alerts/day (cap 25) with precision 0.208 and recall 0.300; A sends 51.1/day on its own rows, above the cap.
- Illustrative cost (5 per missed detractor, 1 per false alert): B 7,156 vs 7,705 with no alerts.

### Limitations

- Scope: seven states (B-C1); orders outside them are not covered by B. How they are served (A's model or no prediction) is open for the team, for B10.
- Prediction moments differ: checkout for regression, carrier handover for classification; the classifier cannot act before handover.
- Fold 1 is below A's training-row minimum (B-G-01); the 5-fold comparison keeps it.
- B's history features for test rows use earlier test weeks (J-1 (a)), as in deployment; the test gain may partly reflect that recency.
- The test period is the newest and differs from development (G-77); A's classification test cohort is below the 15% detractor share (G-75).
- No causal claims: features describe association, not the effect of an intervention.
- B classification uses sigmoid calibration by decision (B-G-05), a deviation from the 8.3 rule.
- Cost is illustrative (5 per missed detractor, 1 per false alert).

### Questions for the team

1. Confirm B as the delivered model for this task (G-79), on the test evidence above.
2. Any slice or limitation that must be resolved before B10 and the report?
3. Keep the frozen threshold 1/6 for delivery, or revisit after the test? A change is reported as a post-test change, with this frozen-threshold result kept as the unbiased one (G-79).

## Alerts for the team

1. **Importance vs B4 ranking diverges for both tasks** (regression Spearman 0.16, top-10 overlap 7; classification 0.31, 6). By the agreed rule this alerts the team; the model is not changed. B4 ranks features one at a time on development rows; permutation importance measures the fitted model on the test period. Decide whether this needs more than a note in the report.
2. **Regression late tail.** B is closer on average, but 11.1% of B's test orders arrive more than 3 days after B's prediction, against 9.3% for A on the same orders (business\_summary.csv). B predicts shorter times in a faster test period; promises built on B would need a buffer.
3. **Classification slices are thin.** Only 3 customer states have more than 100 test detractors (4 too few to judge); slice results are indicative.
4. **Drift (G-77).** The test period is faster and happier than development; route history features moved most (B9.4). Validation scores (selection) and test scores are not on the same footing.

## Coverage

| Task | Evidence | Status | Review |
| --- | --- | --- | --- |
| regression | B9.1 | IMPLEMENTED | Approved |
| regression | B9.2 | IMPLEMENTED | Approved |
| regression | B9.3 | IMPLEMENTED | Approved |
| regression | B9.4 | IMPLEMENTED | Approved |
| regression | B9.5 | IMPLEMENTED | Approved |
| regression | B9.7 | IMPLEMENTED | Approved |
| regression | B9.8 | IMPLEMENTED | Approved |
| regression | B9.9 | IMPLEMENTED | Approved |
| classification | B9.1 | IMPLEMENTED | Approved |
| classification | B9.2 | IMPLEMENTED | Approved |
| classification | B9.3 | IMPLEMENTED | Approved |
| classification | B9.4 | IMPLEMENTED | Approved |
| classification | B9.5 | IMPLEMENTED | Approved |
| classification | B9.6 | IMPLEMENTED | Approved |
| classification | B9.7 | IMPLEMENTED | Approved |
| classification | B9.8 | IMPLEMENTED | Approved |
| classification | B9.9 | IMPLEMENTED | Approved |

## Next

On the team's confirmation: commit B9, then B10 (release from B's bundle), the report, deck, dashboard, reproduction and the DOC\_GAPS.md pass.
