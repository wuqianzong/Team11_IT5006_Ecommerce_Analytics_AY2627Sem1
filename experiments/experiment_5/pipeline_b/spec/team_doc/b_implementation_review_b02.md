# B2 Population and features — implementation review

**Round 2 · ACCEPTED by the experiment lead (2026-10-23, tag e5-B-s02-accepted-r2; built from Henry's review: B-G-03, B-G-04) · team review open.** Clean reruns `20261023T154814Z` (regression) and `20261023T154822Z` (classification) on code commit e960870, clean tree. They are byte-identical to the round-2 build runs 20261023T153736Z and 20261023T153744Z, whose figures appear below. Coverage 6 of 6 per task, 0 MISSING; 7 + 6 checks, all PASS. In each sub-tab, the round-2 cards come first and the round-1 cards follow below.

## Current (round 2)

### Coverage

| Task | ID | Solution step | Coverage | Checks | Review |
| --- | --- | --- | --- | --- | --- |
| regression | B2.1 | Population (B-C1 to B-C5) | IMPLEMENTED | PASS | Open |
| regression | B2.2 | Prediction time | IMPLEMENTED | — | Open |
| regression | B2.3 | Events | IMPLEMENTED | PASS | Open |
| regression | B2.4 | Weeks and leakage rule | IMPLEMENTED | PASS | Open |
| regression | B2.5 | History features (B-C6 to B-C9) | IMPLEMENTED | PASS | Open |
| regression | B2.6 | Test rows | IMPLEMENTED | PASS | Open |
| classification | B2.1 | Population (B-C1 to B-C5) | IMPLEMENTED | PASS | Open |
| classification | B2.2 | Prediction time | IMPLEMENTED | — | Open |
| classification | B2.3 | Events | IMPLEMENTED | PASS | Open |
| classification | B2.4 | Weeks and leakage rule | IMPLEMENTED | PASS | Open |
| classification | B2.5 | History features (B-C6 to B-C9) | IMPLEMENTED | PASS | Open |
| classification | B2.6 | Test rows | IMPLEMENTED | PASS | Open |

### Summary

B2 applies B's population rules to A's eligible development rows and builds the history features, using only events from complete weeks before each row's prediction week (checkout for regression, carrier handover for classification). The estimated delivery date is never read.

| Task | A development rows | B rows (share) | Features built | Rows on own seller history | Rows on own route history |
| --- | --- | --- | --- | --- | --- |
| regression | 76,925 | 61,233 (79.6%) | 6 | 95.9% | 95.9% |
| classification | 77,736 | 61,258 (78.8%) | 9 | 96.7% | 96.0% |

### Round 2 changes (from Henry's review)

1. **The cap now uses B's own rows (B-G-03).** Cap = mean 12.33 + 8 × SD 8.92 = 83.66 days, from lead\_days on B's regression rows after the scope and distance rules (feature\_build\_log.json, lead\_cap\_basis). Round 1 used A's all-state orders and got 93.63 days. The cap now removes 45 regression rows instead of 32, which leaves 61,233 B rows instead of 61,245 (exclusion\_counts\_B.csv). Classification has no cap and is unchanged.
2. **The lateness summary covers the seven states only (B-G-03).** lateness\_summary\_B.csv.gz now holds the 49 routes where both states are among the seven. Any comparison with A filters A to the same states first. The history features still use events from all states: a seller's earlier handovers count whatever the customer's state.
3. **Readable names (B-G-04).** route → route\_seller\_to\_customer\_state, now written seller state → customer state (SP->RJ means shipped from SP to RJ). The other renames:
   - b\_seller\_late\_rate, b\_seller\_late\_days and b\_seller\_dispatch\_days → seller\_prior\_late\_handover\_rate, seller\_prior\_late\_handover\_days and seller\_prior\_dispatch\_days;
   - b\_route\_lead\_days → route\_recent\_delivery\_days;
   - b\_route\_transit\_days → route\_recent\_carrier\_transit\_days;
   - b\_own\_handover\_late, b\_own\_late\_days and b\_own\_dispatch\_days → order\_handed\_over\_late, order\_handover\_late\_days and order\_dispatch\_days.

   The history sources now read: own seller history, seller-state fallback, own route history, state-mix fallback. Values are unchanged; the shares of rows on their own history match round 1.

### Points for review (round 1; Henry's answers are in the comments)

1. **Where the rows go (B2.1).** Regression: 13,777 leave on the seven-state scope, 606 on missing distance, 32 on the lead-time cap and 1,265 in the six-week warm-up. Classification: 13,983 scope, 618 distance, 461 never handed over, 146 reviewed before handover, 1,270 warm-up (exclusion\_counts\_B.csv). The orders never handed over are the missed-dispatch cases that B8 reports with the rule (B-C10).
2. **Cap value corrected.** The B-C3 cap is mean + 8 × SD of A's s02 pre-cutoff orders = 93.63 days (feature\_build\_log.json). CR-054, G-79 and the blueprint first said 93.65, from rounded inputs; they are corrected. The rule itself is unchanged.
3. **Fallbacks are used for about 4% of rows** (history\_coverage.csv): sellers with no earlier handover and routes with fewer than 10 deliveries in the last three weeks. The share is highest in 2017 Q1, right after the warm-up.
4. **Leakage re-check.** For 300 rows per task, the seller and route values were recomputed by brute force from events in weeks before the prediction week and matched exactly (check B2.4/B2.5).
5. **Events cover all states.** History features use deliveries from every state (the environment), while the rows are limited to the seven states. The lateness summary is therefore all-state and descriptive only.
6. **Rows reach B5 before A's fold filter.** B2 starts from A's eligible pre-cutoff rows; B5 keeps only rows that are in A's folds (A's label-maturity and customer rules), so B5's counts will be a little lower.

## Round history

### Round 2 — 2026-10-23

- B-G-03 and B-G-04 applied (B-CR-04) in e5b/history.py, e5b/b02.py and tests/test\_history.py; the 3 tests pass. Runs 20261023T153736Z and 20261023T153744Z; not committed.
- Comments: Henry made 6 comments on the round-1 points, all answered in their threads. This round makes his three changes: the cap base, the seven-state summary and the naming comment on the classification sub-tab.

### Round 1 — 2026-10-23

- First build of B2 for both tasks (B-CR-03): e5b/env.py, e5b/history.py, e5b/b02.py and tests/test\_history.py; the 3 tests pass. Accepted by the experiment lead after a clean rerun (tag e5-B-s02-accepted).
