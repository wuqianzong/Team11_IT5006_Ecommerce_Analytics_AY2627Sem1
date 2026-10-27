# Deliverable ideas from the team-doc comments (report, deck, dashboard)

Built 2026-10-27 from the comment threads of all 56 tabs of the team doc (Claude Docs `21432fd4-…`), for the
report/deck owner (Henry) and the dashboard implementer (Solomon), who cannot read the doc's comments. Only
comments about **building the report, deck or dashboard** are kept; comments that settled a pipeline choice are
left out (their outcome is in the decision logs). Quotes are the commenter's words, shortened with "…".

- **Links** point to the sentence the comment sits on, in the read-only mirrors:
  `../../spec/team_doc/` (Pipeline A tabs) and `../spec/team_doc/` (Pipeline B tabs). Line numbers are those
  of the mirror at this commit.
- **Already logged:** Henry's B-phase requests R-01 to R-18 (24–25 Oct) are in
  [`../REPORT_REQUESTS.md`](../REPORT_REQUESTS.md) with their citable evidence; they are referenced, not repeated.
  Pipeline A's report hooks (section 8 of each `../../spec/blueprints/s0N_*.md`) record the A-phase appendix
  requests. Comments after 25 Oct are only resolve marks.
- **Numbers** in the old replies are from their day; the report cites only register IDs (`../evidence/registry_B.yaml`).
- **Status:** *Open* = still to build; *Check* = conflicts with a later decision or the TA feedback, the lead
  decides (see section 4).

## 1. Dashboard (Solomon; Henry owns the content)

| # | Who, date | Idea | On the sentence | Status |
| --- | --- | --- | --- | --- |
| D-1 | Henry, 18 Oct | "The updated streamlit app will have existing business dashboard tab, lead time tab and detractor risk tab. The EDA analysis table and charts should also be added in to two newly added machine learning tabs." | [model_solution:100](../../spec/team_doc/model_solution_s01_s06-s10.md#L100) (10.5 Streamlit app) | Open: three tabs |
| D-2 | Henry, 18 Oct | "Every data and charts presented in the streamlit App should come from the data saved from the overall pipeline. If we have not yet added it in the output, add it in the outputs. if it changes any of previous frozen stages, ask us to review." | [model_solution:104](../../spec/team_doc/model_solution_s01_s06-s10.md#L104) (10.9 outputs) | Open: the app reads only `app_sources.json` files (B10) and computes nothing |
| D-3 | Lead, 18 Oct | Business dashboard tab keeps the original Phase 1 data: "it is for general data view, it contains all the order status … should still use the original dataset in the dashboard folder. For the new two tabs … use the machine learning dataset"; design the two model tabs "using the industry practice". Henry (reply recorded): keep dropping incomplete months from the monthly charts. | [model_solution:101](../../spec/team_doc/model_solution_s01_s06-s10.md#L101) (10.6 Dashboard) | Open: tab 1 = Phase 1 dashboard, own scope, labelled as such |
| D-4 | Lead, 18 Oct | "Yes, extend, not build a new one. check data source, make sure it is correct" (the Phase 1 dashboard in `deployment/app.py`). | [model_solution:129](../../spec/team_doc/model_solution_s01_s06-s10.md#L129) (open item 10.6) | Open: extend after migration (MIGRATION_PLAN M-5) |
| D-5 | Claude, 18 Oct (agreed) | Seven panels per model tab: headline, fit, policy, where it errs, why, score, data health, each mapped to a stored output. | [model_solution:106](../../spec/team_doc/model_solution_s01_s06-s10.md#L106) (Model tab design) | Open: B10 adapted it to B in `stages/b10/<task>/outputs/app_sources.json` |
| D-6 | Henry, 25 Oct (R-14) | "When we adjust the time window, the model should provide the top 5 routes and top 5 categories in charts, and all routes and all categories in table below the charts, to let business set their operational priorities." Then: "Please think and suggest what are important for business in the dashboard creation." | [b09_classification:498](../spec/team_doc/b_implementation_review_b09_classification.md#L498) (odds ratio table) | Open: see the two replies below |
| D-6a | Claude reply (not yet confirmed by the team) | Rank by **observed** outcomes in the chosen window (late-handover rate, MAE or share > 3 days late; detractor rate, alerts), with a minimum volume and intervals; the model's coefficient or odds ratio as a second column ("risk the model attributes, holding other factors fixed"). Coefficients are one frozen fit, do not change with the window, and rare levels are unstable. | same thread | Open |
| D-6b | Claude reply (not yet confirmed) | Business panels: (1) work queue of alerted orders, capped per day, exportable; (2) promise view with residual-quantile band and share > 3 days late; (3) operational priorities (routes, sellers, categories); (4) seller watchlist (rising late handover); (5) threshold and cost panel; (6) model health (weekly MAE/AP, calibration, drift, fallback share, scope coverage); (7) transparency (model version, window, definitions, limits). | same thread | Open: Henry to choose which panels |
| D-7 | Henry, 25 Oct (R-16) | Promise ranges in the dashboard: share of orders more than 3 and 6 days after B's prediction. | [REPORT_REQUESTS R-16](../REPORT_REQUESTS.md) | Open: now also the buffer curve and per-state late shares (B12.2, `F.reg.buffer_curve`, `B12.reg.buffer_by_state`); add them to `app_sources.json` |
| D-8 | Lead, 23 Oct | Out-of-scope orders "not served; the dashboard states the scope". | [cr054:84](../../spec/team_doc/pipeline_b_cr054_change_request.md#L84) area (decision 3) | **Check:** superseded by B-G-06, B serves its seven states and A serves the rest; the dashboard shows which model scored each order |
| D-9 | Lead, 17 Oct | App input checks refuse orders the model was never trained on (e.g. missing installments) "with a clear message … instead of returning a prediction". | [feature_solution](../../spec/team_doc/feature_solution_s02-s05.md) (2.10, "the app rejects the same input") | Open: B10 `input_validation.json` |

## 2. Report (Henry)

| # | Who, date | Idea | On the sentence | Status |
| --- | --- | --- | --- | --- |
| P-1 | Henry, 22 Oct | Why the bonus round exists: "Narrow down the business problem … when the scope is too wide, the data is too noisy" and "another try of feature engineering … when the score is poor, we can study it as a computing project, but it can't contribute anything to business." | [scratch_check_plan:246](../../spec/team_doc/pipeline_b_scratch_check_plan.md#L246) | Open: the A → B story (with R-18: highlight the new ideas and their impact) |
| P-2 | Henry, 22 Oct | "Since we are working on two types of lateness, in the report, please also summarize what is the dominant factor and what can business do." | [scratch_check_plan:277](../../spec/team_doc/pipeline_b_scratch_check_plan.md#L277) | Open: seller handover vs route transit; cite B9.5 importance, B9.13 by route |
| P-3 | Lead, 22 Oct | Why classification moved to carrier handover: seller dispatch efficiency is observable then, there is "no rush to predict rating at checkout", and orders never handed over are caught by a simple rule ("limit passed, no handover"), not the model. | [scratch_check_plan:145](../../spec/team_doc/pipeline_b_scratch_check_plan.md#L145) | Open: method and business sections; B-C10 missed-dispatch counts |
| P-4 | Henry, 23 Oct | Fold-by-fold validation and test in one table, "because each fold is in fact one of the test period". | [cr054:73](../../spec/team_doc/pipeline_b_cr054_change_request.md#L73) | Built (B-C13, B9.14, T1.6); fold rows are labelled selection scores |
| P-5 | Henry, 23 Oct | Adoption of B is a business decision: B is used if its 5-fold mean beats A, "even by a thin margin"; both go to the test regardless. | [cr054:84](../../spec/team_doc/pipeline_b_cr054_change_request.md#L84) | Open: explain the rule and that the test did not re-choose |
| P-6 | Henry, 23 Oct | B's summaries cover its seven states; any A–B comparison filters A to the same seven states. | [b02:51](../spec/team_doc/b_implementation_review_b02.md#L51) | Open: wording rule for every A–B table |
| P-7 | Henry, 23 Oct | Readable names for the history features (applied as B-G-04, e.g. `seller_prior_late_handover_rate`), and every derived B feature documented with name, scope, definition, formula, reason. | [b02_classification:235](../spec/team_doc/b_implementation_review_b02_classification.md#L235); [cr054:21](../../spec/team_doc/pipeline_b_cr054_change_request.md#L21) | Open: use the B-G-04 names; table from `feature_dictionary_B.csv` |
| P-8 | Henry, 23 Oct | Probe 1 is never cited; B must stand on its own definitions. | [pipeline_b_overview:40](../../spec/team_doc/pipeline_b_overview.md#L40) | Rule: background only |
| P-9 | Henry, 20 Oct | Appendix: the recipe table per family ("I like this table"), the derived-feature formulas, and the CV fold boundary tables and charts for both tasks. | [s04_classification:243](../../spec/team_doc/implementation_review_s04_features_classification.md#L243); [s05_regression:80](../../spec/team_doc/implementation_review_s05_partition_regression.md#L80) | Open: A's s04/s05/s10 report hooks; B's equivalents are `recipes_B`, `feature_dictionary_B.csv`, B5 `folds_B.csv` |
| P-10 | Henry, 19 Oct | A side-by-side view of which feature is in which model, for both tasks. | [s02_data:281](../../spec/team_doc/implementation_review_s02_data.md#L281) (2.12) | Open: feature × task table from the two selected-feature files (A and B) |
| P-11 | Henry, 20 Oct | "we should disconnect any reference from milestone 2. We should review those papers again and redo the citations in Milestone 3." | [s04_features:105](../../spec/team_doc/implementation_review_s04_features.md#L105) | Open: G-76; also TA point 4 (M2_FEEDBACK_GAPS.md) |
| P-12 | Henry, 18 Oct | Check the frozen model's importance against the EDA ranking, "Add the analysis into the report"; the business conclusions need literature and e-commerce sense (lead, 17 Oct). | [model_solution:85](../../spec/team_doc/model_solution_s01_s06-s10.md#L85); [model_solution:87](../../spec/team_doc/model_solution_s01_s06-s10.md#L87) | Open: B9.5 and R-15 (importance vs B4 ranking differ by design) |
| P-13 | Henry, 18 Oct | Classification slices by customer state only where the test has more than 100 detractors, plus a pooled result over those states. | [model_solution:83](../../spec/team_doc/model_solution_s01_s06-s10.md#L83) | Open: B9.3 subgroups |
| P-14 | Henry, 18 Oct | The best model at a grid edge means the search or the features need a relook, so a human decides. | [model_solution:67](../../spec/team_doc/model_solution_s01_s06-s10.md#L67) (8.2) | Open: grid-edge paragraph (TA point 7) |
| P-15 | Henry, 18 Oct | Threshold: how many false alarms per detractor caught, and whether customer service can handle the volume. | [model_solution](../../spec/team_doc/model_solution_s01_s06-s10.md) (8.4) | Built (B9.10, B-G-07 4/15); explain alerts per day and cost |
| P-16 | Lead, 17–18 Oct | Document the literature for the one-SE rule; record each collinear-feature drop and its rationale in the report. | [model_solution:67](../../spec/team_doc/model_solution_s01_s06-s10.md#L67); [feature_solution:65](../../spec/team_doc/feature_solution_s02-s05.md#L65) | Open: Hastie et al. §7.10 etc. (verify); `reduction_rationale*.csv` |
| P-17 | Toh Sim, 21 Oct | Plain-language reading of the one-SE choice (the tree's gain is far below the fold SE; the forest's AP gain is within noise and drift). | [s08_selection:45](../../spec/team_doc/implementation_review_s08_selection.md#L45) | Open: reuse the wording with register numbers; the reply notes the paired check (forest wins 4 of 5 folds) |
| P-18 | Lead, 20 Oct | Test-period limitation: the slowest August deliveries may be missing from the data, which can make the test MAE look slightly better. | [s03_classification](../../spec/team_doc/implementation_review_s03_eda_classification.md) (monthly trend chart) | Open: §8 limitations |
| P-19 | Lead, 17 Oct | "Do not refer previous milestone using the same data as limitation. No decision in this pipeline is influenced by the result of previous milestones." | [model_solution:88](../../spec/team_doc/model_solution_s01_s06-s10.md#L88) | **Check** against TA points 10 and 11 (section 4) |
| P-20 | Lead, 17 Oct | Cite the reproduced data: deliverables are built from the migrated outputs after the reproduction check passes. | [pipeline_v2:50](../../spec/team_doc/pipeline_v2.md#L50) (step 10); A 10.7 | **Check** (section 4) |
| — | Henry, 24–25 Oct | R-01 to R-18 (glossary, drift by fold, payment type, routes, threshold options, residuals, time windows on charts, charts in the body with tables in the appendix). | [`../REPORT_REQUESTS.md`](../REPORT_REQUESTS.md) | As listed there |

## 3. Deck (Henry)

| # | Who, date | Idea | On the sentence | Status |
| --- | --- | --- | --- | --- |
| K-1 | Henry, 25 Oct (R-18) | Charts of the key metrics and the fold-by-fold validation and test results; highlight the engineered features and their impact, and how the bonus-round ideas improved the model. | [report_notes:7](../spec/team_doc/report_notes_a_and_b.md#L7) | Open |
| K-2 | Henry, 24 Oct (R-05, R-06) | Mean ± SE by population with a comparison chart; ROC-AUC and Brier beside AP; confusion-matrix comparison, for report and slides. | [`../REPORT_REQUESTS.md`](../REPORT_REQUESTS.md) | Partly built (B8 outputs); charts to make |
| K-3 | Henry, 18 Oct | PR-AUC and ROC-AUC charts. | [model_solution:23](../../spec/team_doc/model_solution_s01_s06-s10.md#L23) | Built (s06, T1 curves) |
| K-4 | Lead, 17 Oct | Deadline: the reproduction check has to pass before 4 Nov so the slides can use it. | [pipeline_v2:50](../../spec/team_doc/pipeline_v2.md#L50) | **Check** (section 4) |

## 4. Decisions (lead, 2026-10-27)

1. **No earlier milestone in the report (P-19).** The final report replaces all earlier milestone reports. It
   never mentions Milestone 1 or 2 and has no response-to-feedback appendix. It covers every section the
   earlier reports had (problem statement, literature, data, EDA, models, business), rewritten from this
   experiment's evidence and free of the mistakes both TAs pointed out.
2. **Numbers from the reproduced outputs (P-20, K-4).** Final numbers and app paths come from the migrated,
   reproduced outputs; the lead starts migration and reproduction next. Drafting continues meanwhile on
   register IDs, which do not change; the final fill, figures and screenshots wait for the reproduction.
3. **Scope message (D-8)** and 4. **panel choice (D-6a/D-6b)**: handed to Henry for the dashboard plan
   (B-G-06 routing is the binding constraint for 3).
