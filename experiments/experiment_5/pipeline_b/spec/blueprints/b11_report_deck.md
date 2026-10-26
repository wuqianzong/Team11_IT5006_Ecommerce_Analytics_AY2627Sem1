# B11 — final report and deck drafts, from B's evidence (blueprint)

| Field | Value |
| --- | --- |
| Stage | B11 deliverables: report and deck drafts (A's s10 10.7 adapted to B; G-79: B delivered, A baseline) |
| Nodes | common (one report, one deck, both tasks) |
| Status | AGREED 2026-10-26 (Henry: B11-D1 to D9; D6 changed to Claude Slides). Drafted by Henry's Claude |
| Inputs frozen | Every B run listed Current in `../../EVIDENCE.md` (B2 to B10, T1, doc support); B10 at tag e5-B-s10-accepted |
| Doc copy | `../doc_outbox/b11_blueprint_tab.md` |

## 0. Scope and order (decisions of 2026-10-26)

Henry's decisions on the deliverables (B11-D1 to D4):

1. **Draft now, before migration and the reproduction check** (a deviation from s10-D3's order, because the
   slides lock on 4 Nov). Drafts live in `pipeline_b/deliverables/`. Before submission every number is
   re-checked against the reproduced outputs (s10 10.4), or against the same Current runs if the team
   submits without migration.
2. **Blueprint first**, as every B stage.
3. **B's own number register**, `pipeline_b/build_evidence_B.py`, separate from A's `build_evidence.py`.
4. **Report as a Claude Doc** for the team to review and comment (not the Milestone 2 Word route); **deck
   as a Claude Slides deck** (no team template): text and tables stay editable, charts are images.

Not in B11: migration, the reproduction check, the Streamlit app and its live URL (each only when
ordered). Report and deck keep marked placeholders for the app (deployment section, screenshots) until then.

## 1. Goal and gate

Goal: a 15–20 page report and a 10-minute deck that follow the brief's Phase 3 section list, tell one
story (B delivered, A as baseline), and carry no hand-typed number. Gate: every number and table in both
resolves to `numbers_B.json` (built from Current runs only); the team reviews the report in the Claude Doc
and the deck file; open placeholders are listed.

## 2. Number register (B11.1, `build_evidence_B.py`)

- `pipeline_b/evidence/registry_B.yaml` lists every number, table and figure the report and deck use
  (A's registry format: `id`, `kind` number/table/figure, `source` file, `select`, `used_in`), with B
  evidence IDs. A's baseline numbers come from B's T1 and B9 files, which already score A (A on A's rows,
  A on B's rows); A's own tree is not read for the register and never written.
- The builder refuses to run unless each source file belongs to a run listed Current in EVIDENCE.md (its
  `_manifest.json` run_id and sha256 match), then writes `pipeline_b/evidence/build/numbers_B.json`,
  table CSVs and figure copies, each with its source file, run_id and evidence ID.
- Report and deck text uses placeholders such as `{{B9.2.reg.mae_diff}}`; a filler replaces them from
  `numbers_B.json` with the registry's format. A placeholder that does not resolve fails the build.
- Test: every placeholder in the report and deck sources is in the registry; every registry item resolves.

## 3. Report (B11.2)

Source: `pipeline_b/deliverables/report/*.md`, one file per section, with placeholders. Filled output is
published as a Claude Doc in Henry's account for the team (B11-D5); the doc is the review copy, the repo
holds the source. Exported to PDF at the end (12 pt, captions, labelled tables; `TeamX_...` naming).

| § | Section (brief Phase 3) | Pages | Content and sources |
| --- | --- | --- | --- |
| — | Cover, executive summary | 1 | Problem, delivered model, headline test results with intervals (B9.1, B9.2), business answer |
| 1 | Problem definition and stakeholder | 1.5 | Two tasks, prediction moments (checkout; handover for classification), stakeholders and actions, 5:1 cost (s01; CR-054) |
| 2 | Dataset and preprocessing | 2 | Tables and joins, `customer_unique_id`, leakage audit (s02); B's population rules and history features (B2); why carrier dates are allowed as *past* events and at handover only (brief leakage warning) |
| 3 | Exploratory analysis highlights | 1.5 | Target shape, trends over time, late delivery vs detractors (s03); route lateness (B2 lateness summary) |
| 4 | Modelling approach | 3 | Pipeline A, then B = A + CR-054; features and 99% rule (B4; Report notes §6 citations); time-ordered folds and why not stratified (Report notes §2); model ladder dummy → linear/logistic → tree → forest, one-SE rule (B6–B8); calibration and threshold (B8, B-G-05); ensemble decision (§3, wording per B11-D7) |
| 5 | Results and evaluation | 4 | Train–validation–test table with intervals, A vs B on the same rows (B9.1, B9.2, B9.14); where B's gain comes from (Report notes §1); error analysis by state and route (B9.3, B9.13); residual buffers (B9.16); classification at 1/6 (unbiased) and 5/14 (post-test, B-G-09) (B10.3); interpretation: coefficients, odds ratios, permutation importance and its divergence from B4 (B9.5, R-15); drift (B9.4, B9.11) |
| 6 | Model deployment and application | 1.5 | Release package and serving rule (B10): parity, router, A fallback, input checks, out-of-profile warning; app URL and screenshots **placeholder** |
| 7 | Business recommendations and impact | 2 | Delivery promises with buffers, alert volumes and costs, missed-dispatch rule, route actions (B9.7, B9.13, B10.3, R-14); observation / hypothesis / unmeasured-mechanism labels |
| 8 | Limitations and next steps | 1 | Scope, prediction moments, fold-1 deviation, drift, post-test threshold, refit reproducibility (B10-D10), no causal claims |
| — | References; appendices | (excluded) | Full rank (R-01), metric glossary, fold boundaries, recipes, full tables, AI-use declaration |

Report requests R-01 to R-18 and DOC_GAPS T-01 to T-10 are each mapped to a section in the registry
(`used_in`); the build lists any request without a home.

## 4. Deck (B11.3)

- A Claude Slides deck (artifact type "Slides") in Henry's account, shared with the team like the report
  doc (B11-D6). Slide text comes from `pipeline_b/deliverables/deck/slides.md` (one block per slide, with
  placeholders), filled from `numbers_B.json`. One house style for the deck (palette, fonts, title,
  content, two-column, table and chart layouts). **Every title, bullet and table is editable deck text or
  table; only charts are images** (the stage PNGs, uploaded as assets). Speaker notes carry the talk track
  and the source of each number.
- About 12 slides for 10 minutes: title; problem and stakeholders; data and leakage control; A → B (what
  changed and why); model ladder and selection; results A vs B (both tasks); where B errs; threshold and
  alert volumes; business actions; deployment (app screenshots placeholder); limitations; summary.
- Downloaded as .pptx and PDF for Canvas and the ZIP (B11-D6).

## 5. Outputs

`pipeline_b/build_evidence_B.py`, `evidence/registry_B.yaml`, `evidence/build/` (numbers_B.json, tables,
figures, build manifest); `deliverables/report/*.md` and the filled report; `deliverables/deck/slides.md`
and the Slides deck; `deliverables/placeholders.md` (open items: app URL, screenshots, reproduction re-check).

## 6. Checks

- Every number, table and figure in report and deck resolves to `numbers_B.json`; none is typed.
- Every register source is a Current run in EVIDENCE.md (run_id and sha256).
- Superseded evidence (e.g. 4/15, B2 round 1) is never cited.
- Validation scores are labelled selection scores (G-10); test numbers come from T1 or B9/B10 post-test views,
  and 1/6 is called the unbiased result.
- The deck has no text or table inside a picture (every image asset is a chart PNG from the register).
- Report body 15–20 pages after export; deck about 12 slides.
- Brief compliance list (Phase 3 sections, leakage, imbalance, 2–3 families, baselines, CV, seeds) ticked
  with the section that satisfies each.

## 7. Decisions

| ID | Question | Recommendation | Status |
| --- | --- | --- | --- |
| B11-D1 | Draft before migration and reproduction | Yes, in `pipeline_b/deliverables/`; re-check before submission | Agreed (Henry, 2026-10-26) |
| B11-D2 | Blueprint first | This blueprint | Agreed (Henry, 2026-10-26) |
| B11-D3 | Number register | `build_evidence_B.py`, separate from A's | Agreed (Henry, 2026-10-26) |
| B11-D4 | Formats | Report as a Claude Doc for review; deck generated, editable text and tables, charts as images | Agreed (Henry, 2026-10-26) |
| B11-D5 | Whose account holds the report doc. A doc in Henry's account can be read and edited by Henry's Claude (comments included); Benson's Claude cannot reach it, as Henry's Claude cannot reach Benson's doc | Henry's account, shared with the team by link for browser review; the repo Markdown stays the source | Agreed (Henry, 2026-10-26) |
| B11-D6 | Deck format | Claude Slides deck in Henry's account; editable text and tables, charts as images; download .pptx and PDF | Agreed (Henry, 2026-10-26; replaces the python-pptx proposal) |
| B11-D7 | Ensemble wording. Report notes §3 says the course "rules out" a more complex family; the brief lists voting/stacking as an optional third family built from the chosen ones, and Benson says the professor forbids more complex families | Write "ensembles were optional; within the course's limit on model families the team kept linear and tree families, with the random forest as the bagged ensemble; stacking was not added", and cite the brief accurately | Agreed (Henry, 2026-10-26) |
| B11-D8 | Team name and numbers in file names (`TeamX_…`) | Team 11, from the Milestone 2 report name | Agreed (Henry, 2026-10-26) |
| B11-D9 | Report authorship: Claude drafts every section from the register, the team edits in the doc; AI use declared (brief policy) | As stated | Agreed (Henry, 2026-10-26) |

## 8. Timeline (slides lock 4 Nov 23:59, report 8 Nov 23:59)

| Date | Step |
| --- | --- |
| 27 Oct | Register and builder; report outline in the doc |
| 28–30 Oct | Report sections 1–8 drafted; deck v1 |
| 31 Oct – 2 Nov | Team review of doc and deck; app placeholders filled if migration and app are done |
| 3 Nov | Deck final check (numbers, compliance list); 4 Nov submit |
| 5–7 Nov | Report final edits, PDF export, re-check numbers; 8 Nov submit ZIP |
