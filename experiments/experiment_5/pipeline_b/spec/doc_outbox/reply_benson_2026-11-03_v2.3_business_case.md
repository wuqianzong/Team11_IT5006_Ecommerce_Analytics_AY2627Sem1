# Reply to Benson: report v2.3 and deck v2.3, the business case (2026-11-03)

Hi Benson, your revision brief is done as one change set, B-CR-50, on `e5/validation-fixes-henry` (not merged into
milestone-3 or main; waiting for your approval). Henry's choices and the rules from your brief are recorded as
B-G-19 to B-G-23, all `Proposed` until you approve them (`spec/decision_log_B.md`).

## What was computed, and where

No stage output or run record was changed. Every new number comes from one new read-only producer,
`deliverables/business_case/make_business_case.py` (dashboard venv), with `_manifest.json` (input, code and output
sha256) and `_evidence_index.json`. The register reads it as `BCASE/<file>` (new root in
`build_evidence_B.MANIFEST_ROOTS`, the same manifest check as BIZ, M2A, DECK and SHOT). It refits nothing: it reads
T1's stored test predictions, b08's out-of-fold predictions, b12's buffer choice, b10's thresholds, b09's
missed-dispatch rule, the s02 records and the raw order events, and it scores the scenarios with the frozen bundles
through the dashboard's own scenario code (it asserts the bundles reproduce T1's stored risk and that b12's 12.0
days is reproduced).

| Evidence | Output | What it holds | Label in the report |
| --- | --- | --- | --- |
| BC.1 | `promise_compare.csv`, `figures/promise_compare.png` | On B's 15,422 test orders: median promise, MAE and late share for Olist's estimate, Dummy, A, B, B + 3/5/6/12 days and B + 10 days | Observation, post-test analysis |
| BC.2 | `buffer_recent.csv` | Buffer chosen on b08's last validation fold (1 Apr to 24 May 2018): 10.0 days at Olist's late share there (2.1%), 3.5 days at 10%; b12's 12.0 on all folds | Operational rule (no test data); test late share a post-test view |
| BC.3 | `expedite.csv` | Late orders handed over late, and how many would be on time with transit 10% faster | Scenario, unmeasured mechanism |
| BC.4 | `discount.csv` | Still-late orders flagged by B at 4/15, and how many alerts stop under each dashboard freight scenario (with out-of-range counts) | Association, not an effect |
| BC.5 | `reach.csv` | Alerts a day, precision and detractors reached a day for B 4/15, A 1/6, A 4/15 and the missed-dispatch rule | Observation (post-test view) |

New register ids: `BC.promise.*`, `BC.buffer.*`, `BC.expedite.*`, `BC.discount.*`, `BC.reach.*`, `BC.test_orders`,
`BC.promise_table`, `F.BC.promise_compare` and `F.BC.promise_compare.deck` (register 504 items). The deck render was
added to `make_deck_renders.py`; the 18 earlier renders are byte-identical after the rerun.

## Decisions

| ID | Decision |
| --- | --- |
| B-G-19 | Buffers shown: B + 3, 5, 6 and 12 days and the recent-weeks buffer; Olist, Dummy, A and B without buffer (Henry) |
| B-G-20 | Transit scenario: the actual transit 10% shorter, for late orders handed over late, as the dashboard's "Logistics −10%" (Henry) |
| B-G-21 | Recommended rule: each month, the smallest buffer whose late share on recent weeks is at or below Olist's own; 10.0 days on the last fold; b12's 12.0 stays the unbiased result (your brief) |
| B-G-22 | Rescue = alert risk below threshold under the freight scenarios; alert options A 1/6, A 4/15 (post-test view, not tuned on the test) and the rule; reach = precision × alerts a day; break-even as a condition without values; hold-back pilot (Henry and your brief) |
| B-G-23 | Deck: slide 2 'business'; 'use_reg' and 'use_clf' replace 'use' (18 slides); cover note 0:15 and app note 0:10, notes total 9:55; literature checked by the session (Henry) |

## Report v2.3 (sources first, then review doc rev 51)

- Executive summary "Use": Olist's estimate MAE (12.62 days), the recent-weeks buffer (10.0 days, 2.1% late against
  Olist's 5.5%), missed dispatch and the alert.
- §1: "grew fast, then stalled"; new "Problem statement" paragraph linking the lead-time model to sales
  (literature-supported hypothesis) and the alert to retention (unmeasured mechanism, pilot).
- §2: Fisher et al. (2019) and Salari et al. (2022), each limited to its abstract.
- §9 rewritten as one chain: 1 promise (Table 5, figure 24 replaces the buffer curve, recent-weeks rule),
  2 dispatch, 3 transit (scenario), 4 service recovery (Table 6), workflow through tabs 3, 4.1, 4.2 and 4.3
  (operational rule), freight discount (association), cost and break-even (assumption).
- §10: business-case limit, missing operational data (live handover feed, action log), hold-back pilot as next step.
- References: the two new sources. Table K16 rebuilt for the four steps.
- Literature register rows 13 and 14: metadata and claims from the Crossref record of each DOI
  (10.1177/0022243719849940, 10.1287/msom.2022.1081). Please recheck both rows.

## Deck v2.3 (version 48)

Cover: "Olist's own estimate: 12.62" under the regression MAE. Slide 2: growth stalled, service broke, retention low,
the problem statement and how each model helps. Slide 16: the buffer as a dial (promise chart, Olist today, monthly
rule, B + 6 days, why recent weeks, dispatch is the lever). Slide 17: the alert options table, the workflow through
the dashboard tabs, the freight discount as an association, the hold-back pilot. Footers n/18.

## Other

- `deliverables/dashboard/app/README.md` now says the app is hosted at https://it5006grp11ecommerce.streamlit.app/.

## Checks

Placeholders resolve; audit 9/9 on the committed inputs (`report_export_rev51.md`, deck version 48, 29 doc and 22 deck
charts); `pytest pipeline_b/tests tests/test_guards.py` 36 passed, 5 skipped; dashboard tests 21 passed.

## Open

- The .docx and .pptx exports need Henry's Chrome; they follow in a later commit under `deliverables/exports/2026-11-03/`.
- The review doc's file name still reads v2.2 (its heading and note say v2.3).
- The 4/15 threshold, the A 4/15 option and all test numbers in §9 remain post-test views, as labelled.

## Addendum: page budget (B-CR-51, B-G-24)

Henry capped the body growth at 2/3 page. The new body text is now 338 words (it was about 1,245), with no new body
table: §9 is compact, and the promise comparison (Table 5), the alert options (Table 6) and the freight scenarios
are appendix tables K18, K19 and K20. No number changed. Review doc rev 52; audit 9/9. On the same local
pipeline, v2.3's body is 0.3 text-pages longer than v2.2's (about +0.25 page at the official format's scale); the
real .docx export will confirm that the body ends on or before page 20.
