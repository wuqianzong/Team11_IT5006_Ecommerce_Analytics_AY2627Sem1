# Handover: dashboard plan, report and deck (from Benson's Claude, 2026-10-27)

You are Henry's Claude. Henry now owns the report, the deck and the dashboard plan. Solomon will
build the dashboard from your plan. The pipeline is finished and frozen. Your work is to turn the
frozen evidence into the deliverables. You do not change the evidence.

## 0. Sync first

1. `git fetch origin --tags`, check out `milestone-3` and pull. You should be at or after the commit
   that added this file, and see tag `e5-release-2`.
2. Cut your branch from that point: `git switch -c e5/deliverables-henry`.
3. Read `experiments/experiment_5/CLAUDE.md`, `README.md` §0.1, §7, §8 (rule 15 is the branch rule)
   and §12, then `pipeline_b/README.md`.

## 1. Where everything is (read in this order)

Paths are under `experiments/experiment_5/pipeline_b/` unless they start with `docs/`.

| What | Where |
| --- | --- |
| Ideas the team left in doc comments (dashboard, report, deck), with links to the sentence each one sits on | `deliverables/DELIVERABLE_IDEAS.md` (section 4 holds the lead's decisions) |
| What the TA feedback still needs from the report | `deliverables/M2_FEEDBACK_GAPS.md`; Milestone 1 TA feedback `docs/Project/Milestone1/TA Feedback.txt` (Windows encoding) |
| Earlier reports, for the sections the final report must cover (read for structure; never cite or reuse their numbers) | `docs/reports/Report submitted/` (Phase 1 PDF, Phase 2 docx); teacher's expectation `docs/Project/Milestone2/Teacher expectation for milestone 2.md`; brief `docs/Project/IT5006 Project Description - AY 2026_27 Semester 1.pdf` |
| Henry's earlier report requests R-01 to R-18, each with its evidence | `REPORT_REQUESTS.md` |
| Report and deck sources, audit, the review doc and deck links | `deliverables/README.md`, `deliverables/report/`, `deliverables/deck/project/`, `deliverables/audit/` |
| Every number you may use (register IDs and the built figures) | `evidence/registry_B.yaml`, `evidence/build/` |
| Which runs are Current (the only valid source of numbers) | `EVIDENCE.md` |
| Decisions | `spec/decision_log_B.md`, `spec/human_decisions_B.yaml`; Pipeline A: `../spec/blueprints/decision_log.md` |
| What the app may read, panel by panel | `stages/b10/<task>/outputs/app_sources.json`, `serving_config.json`, `input_validation.json`, `drift_profile.json` |
| Frozen model bundles (A and B) | `stages/t1_joint_test/<task>/outputs/bundles/{A,B}/` |
| B12 analyses added for the TA feedback (ranking stability, promise buffer) | `stages/b12/`, register items `B12.*`, `F.reg.buffer_curve` |
| Read-only mirrors of the team doc | `spec/team_doc/` (B tabs), `../spec/team_doc/` (A tabs) |
| A's original app design (three tabs, seven panels per model tab) | `../spec/team_doc/model_solution_s01_s06-s10.md` lines 100–120 |
| A's appendix requests | `../spec/blueprints/s0N_*.md`, §8 "Report hooks" |
| Release and reproduction record | `release/e5-release-2.json`, `../reproduction/ACCEPTANCE.md` (no migration, CR-061) |

## 2. Your three tasks

1. **Dashboard plan** → `deliverables/dashboard/DASHBOARD_PLAN.md`. Design it from `DELIVERABLE_IDEAS.md`
   §1, A's seven-panel design and `app_sources.json`. List each tab and panel with what it shows,
   the decision it supports, the file and evidence ID it reads, and its chart type. The app computes no
   statistic; every number comes from a stored output (G-41, A's s10 rule 10.5). Henry decides two things
   in the plan:
   - **The scope message.** B-G-06 is binding: B scores orders inside the seven states, A's frozen model
     the rest. The CR-054 "not served" wording is superseded. The app shows which model scored each order.
   - **The panel choice.** The suggestions in D-6a and D-6b were never confirmed; take, drop or change them.

   Also:
   - The Phase 1 business dashboard tab keeps its own data and labels it as a separate scope.
   - B12 files the app needs but `app_sources.json` doesn't list go into the plan as "new sources", with
     their evidence IDs.
2. **Report: the one complete final report.**
   - It replaces every earlier milestone report and never mentions Milestone 1 or 2. There is no
     "response to feedback" section.
   - It covers every section the earlier reports had: problem statement and stakeholders, literature
     review, data and preprocessing, EDA, features, validation design, models, results, business
     recommendations, deployment, limitations.
   - Every section is written from this experiment's evidence, fixing silently each mistake the two TAs
     pointed out (`M2_FEEDBACK_GAPS.md`, the Milestone 1 TA feedback).
   - Literature: only sources verified against the publisher's record (G-76). No reference or number is
     carried over from earlier reports.
   - Also close the open items in `DELIVERABLE_IDEAS.md` §2 and `REPORT_REQUESTS.md`, then proofread the
     whole report once.
3. **Deck:** apply `DELIVERABLE_IDEAS.md` §3. The deck follows the same rule as the report: it never
   mentions earlier milestones, and it stays consistent with the report.

Plan before you write. Show Henry the plan for each task and wait for his OK.

## 3. Timing: reproduction

**Update 2026-10-27: reproduction passed** (tag `e5-reproduced`, `experiments/experiment_5/reproduction/ACCEPTANCE.md`). The
outputs are unchanged and stay where they are (no migration, CR-061), so the register IDs and paths you use are final.
The text below is kept for the record.

Benson starts the migration and reproduction in a later session. Final numbers, figures and app paths come
from the reproduced outputs. That doesn't block you: write everything with register IDs (`{{id}}`), which
stay the same after migration. Only these wait for the reproduction:
- the final fill and freeze of the report and deck;
- the re-uploaded figures;
- the app screenshots and URL.

List them in your handover as "waits for reproduction".

## 4. Collaboration rules (binding for you, and for Solomon's AI)

Updated 2026-10-27 (lead): Henry and Solomon share one branch and talk directly about the dashboard.

1. **One shared branch.** Henry and Solomon both work on `e5/deliverables-henry`, cut from `milestone-3`.
   - Before you start and before every push, run `git pull --rebase origin e5/deliverables-henry`.
   - Never force-push. Never rewrite commits already pushed.
   - Push when your human says so.
   - Only Benson merges the branch into `milestone-3`. Never push to `milestone-3` or `main`, never tag.
2. **Containment.** Write only inside `experiments/experiment_5/pipeline_b/`. Read anything. Experiment 5 is
   not migrated (CR-061): nothing is copied into `src/`, `deployment/`, `artifacts/` or other working folders,
   and the root `app.py` is not touched. How the app is launched and hosted is a later step; ask Benson then.
3. **The evidence is frozen.** Never rerun a stage, T1 or a model; never refit; never change `e5b/`,
   `stages/*/outputs/`, the tags or the release record. T1 was read once (`e5-T1-tested`).
4. **Numbers.**
   - Never type a metric. Every number is a `{{id}}` register placeholder, filled with
     `build_evidence_B.py fill` and checked with `build_evidence_B.py check`.
   - Before each push that touches the report or deck, rerun the audit: `audit_deliverables_B.py`.
   - If a number has no register item: Henry adds the item to `registry_B.yaml`, built only from a Current
     run in `EVIDENCE.md`, and logs it in the worklog. Only Henry edits the register; Solomon asks Henry.
5. **Who owns which files.** Each person touches only their own files, so the shared branch never conflicts:
   - Henry (report and deck; no code): `deliverables/report/`, `deliverables/deck/`,
     `deliverables/dashboard/DASHBOARD_PLAN.md`, `evidence/registry_B.yaml`, `WORKLOG.md`, `HANDOVER.md`,
     `spec/doc_outbox/`.
   - Solomon (dashboard code): `deliverables/dashboard/app/` (code, tests, its own `requirements` and README),
     `deliverables/dashboard/WORKLOG_solomon.md`.
   - Any other file: ask Benson first.
6. **Logs.** Each session appends a dated entry to its own worklog: what was done, commits, open questions.
   Doc text for tabs you can't edit goes to `spec/doc_outbox/` with a `sync_for_benson_<topic>.md` summary.
7. **Talking.** Henry and Solomon settle the dashboard plan between themselves; `DASHBOARD_PLAN.md` is the
   contract, and a change to it is Henry's commit. If a spec rule is unclear or conflicts with a request,
   quote the text (file and section), stop and ask your human; only rule conflicts go to Benson.
8. **Commit and review.** Commit small, one topic per commit, ending with a co-author line. When the work is
   ready, Henry asks Benson to merge; Benson's Claude reviews the branch (diff, audit, tests) first.

## 5. Working with Solomon on the dashboard

1. Solomon's AI has its own starting prompt (from Benson). It joins `e5/deliverables-henry` and waits for
   `deliverables/dashboard/DASHBOARD_PLAN.md`.
2. When Henry approves the plan, commit and push it, and tell Henry to tell Solomon it is ready. Questions
   about the plan go between Henry and Solomon directly.
3. The plan must give Solomon, for every tab and panel, what it shows, the decision it supports, the exact
   file and evidence ID it reads (from `stages/b10/<task>/outputs/app_sources.json` or a listed new
   source), and the chart type.
4. The app never computes a statistic, never retrains, and never scores the test cohort with labels.
   Re-predicting without labels for parity is allowed (B-G-08).

## 6. First reply to Henry

Before writing anything, reply with:
- the commit you are on;
- what you read;
- your plan for each of the three tasks;
- your questions.
