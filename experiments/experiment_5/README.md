# Experiment 5 — Milestone 3 clean baseline (textbook-sequence replay of Milestone 2)

Status: **PROTOCOL v1.0 — pipeline design frozen 2026-10-17 (CR-001). No implementation yet.**
Branch: `milestone-3`. Owner of this protocol: team (changes follow §9).

---

## 0. Read this first (humans and AI agents)

Experiment 5 is **not a new study**. It replays the Milestone 2 direction
(Olist, two checkout-time tasks, leakage exclusions, the feature candidate set (24 predictors here),
log transforms, linear and tree families) but executes it as **one
ten-stage pass in the textbook order taught in Tutorials 1–8**, with **one validation
protocol, one pipeline factory and one evidence registry** from start to finish.

Its purpose is a baseline whose pipeline, code, data and evidence are
**clear, accurate and logically connected**, so the Milestone 3 report, deck and
app can all be regenerated from one command after any change.

**If you are an AI agent:** before editing anything, read in this order:

1. this README (the rules — binding);
2. [`spec/pipeline_design.md`](spec/pipeline_design.md) (what each stage must do — frozen v1.0, binding);
3. [`spec/sources.md`](spec/sources.md) (teacher expectations, TA feedback, tutorial mapping);
4. the `STAGE.md` of the stage/task folder you were assigned;
5. §13 (how to use the technical foundation) before writing any stage code.

Then follow §8 (agent rules). If a rule here conflicts with an instruction you
received, stop and ask the human; do not resolve the conflict yourself.

### 0.1 Containment rule (applies to everyone, for the whole experiment)

**Everything Experiment 5 produces stays inside `experiments/experiment_5/`** — code,
configs, outputs, models, figures, evidence, app code, report and deck drafts — until the
**whole experiment is approved** and the **experiment lead explicitly instructs a
migration** (§12). Until then:

- nothing is written to the working folders (`src/`, `artifacts/`, `deployment/`,
  `notebooks/`, `data/`, `docs/`, root `app.py`, `requirements*.txt`, root `README.md`);
- files outside this folder may be **read** (raw data, Milestone 2 code for reference,
  tutorials), never written, moved or deleted;
- Experiment 5 code never imports from `src/` or other experiments; reused logic is copied
  into `e5lib/` with a provenance comment.

What an agent works on may change during a conversation; this rule does not.

---

## 1. Why this protocol exists (lessons from Milestone 2)

Milestone 2 changed its pipeline mid-way (random-group → chronological split,
27 → 9 → 11/12 features, several preprocessing builders, competing threshold
stories) and reran pieces independently. Report numbers then came from runs with
different cohorts, folds and encodings. Experiment 5 prevents that with five
mechanisms:

| Problem in M2 | Mechanism in Experiment 5 |
| --- | --- |
| Numbers from different runs/protocols mixed in one report | Every output carries a **run manifest** with input/code/config hashes; the report is built only from a **release** where every stage is fresh (§6, §7) |
| Several preprocessing builders, untested switches after search | **One pipeline factory** in `e5lib/`; a candidate is a full spec (features + preprocessing + target treatment + estimator) with a stable `candidate_id` (§5.3) |
| Grouped screening compared with chronological confirmation | **One frozen protocol** in `spec/protocol.yaml`, written in s01_problem, used by every stage (§5.2) |
| Pipeline changed but downstream evidence not rerun | **DAG orchestrator** marks downstream stages **STALE** and reruns them; decisions that flip are sent back to review (§6) |
| Hand-copied numbers in report/deck | **Evidence registry** maps every table/figure/number to a stage output; report/deck/app read only `evidence/build/` (§7) |

---

## 2. Authority order

When documents disagree, the higher item wins:

1. Project brief (`docs/Project/IT5006 Project Description …pdf`) — requirements.
2. Teacher expectations ([`spec/teacher_expectation_m2.md`](spec/teacher_expectation_m2.md)) and TA feedback (summarised in `spec/sources.md`).
3. Tutorials 1–8 sequence (mapped per stage in `spec/pipeline_design.md` and `spec/sources.md`).
4. [`spec/pipeline_design.md`](spec/pipeline_design.md) — the agreed Milestone 3 pipeline (the authoritative copy; supersedes the `docs/` original).
5. `spec/protocol.yaml` — the frozen numeric contract (seeds, folds, grids, decision rules). Created in s01_problem.
6. This README — process and collaboration rules.
7. `STAGE.md` of each stage — local details only; may not contradict 1–6.

Milestone 2 code/artifacts (`src/`, `artifacts/`, `experiments/experiment_3/`,
`notebooks/`) are **reference only**. Reuse logic by copying it into `e5lib/`
with a provenance comment; never import from or write to them.

---

## 3. Folder structure

```text
experiments/experiment_5/
├── README.md                  # this protocol (binding)
├── AGENTS.md / CLAUDE.md      # 5-line pointers so coding agents auto-load this README
├── AGENT_INIT_PROMPT.md       # general copy-paste prompt to start any teammate's agent
├── CHANGELOG.md               # every change request to spec/, e5lib/ or an ACCEPTED stage
├── spec/                      # WHAT we do (team-owned, change via §9)
│   ├── pipeline_design.md     # THE Milestone 3 pipeline design (authoritative; frozen v1.0)
│   ├── stages.json            # machine-readable stage list derived from the design (§3.1)
│   ├── sources.md             # teacher/TA/tutorial requirements → stage mapping
│   ├── team_doc/              # read-only mirror of the team doc tabs, refreshed at each acceptance (G-65)
│   ├── teacher_expectation_m2.md
│   └── protocol.yaml          # frozen numbers & rules, written by s01_problem
├── e5lib/                     # SHARED technical foundation (see §9.1; changes logged in CHANGELOG)
│   ├── paths.py               # all paths; no stage hard-codes a path
│   ├── data.py                # loaders with population guard (§5.4)
│   ├── factory.py             # the ONE pipeline factory: spec → sklearn Pipeline
│   ├── candidates.py          # candidate spec → candidate_id
│   ├── metrics.py             # metric definitions (MAE, RMSE, R2, AP, ROC-AUC, Brier, cost)
│   ├── cv.py                  # fold iteration, customer purge, label-maturity filter
│   ├── protocol.py            # read protocol.yaml; owning stages write data-dependent sections
│   ├── contract.py            # the 24-predictor contract, feature groups, log1p candidates (G-61), screening candidates (G-68, G-69)
│   ├── cleaning.py            # s02: typed loading and cleaning of the nine tables; states, regions
│   ├── aggregation.py         # s02: order-grain aggregation of items, payments, reviews
│   ├── geography.py           # s02: IBGE boundary, ZIP centroids, distances
│   ├── seller_history.py      # s02: seller history strictly before checkout (G-69)
│   ├── eda.py, eda_sections.py  # s03: EDA statistics and shared output sections
│   ├── features.py            # s04: pool ranking, transforms, reduction, selection, recipes, runner
│   ├── outputs.py             # standard output writers; every output tagged with solution IDs
│   ├── review.py              # review pack + coverage table generator (§9.1)
│   └── manifest.py            # run manifest write/read, hashing, staleness check
├── stages/                    # HOW it ran — one folder per node, GENERATED from spec/stages.json
│   ├── s01_problem/common/    #   (see §10 for the live index)
│   ├── s02_data/common/
│   ├── s03_eda/{regression,classification}/
│   ├── …                      #   s04_features … s09_conclusion, each {regression,classification}
│   └── s10_release/common/
│       # every node folder has the SAME layout:
│       #   STAGE.md     stage card: owner, status, inputs, outputs, decision rule, review
│       #   run.py       single entry point: python -m ... run.py  (no arguments needed)
│       #   *.py         node-local helpers (never imported by other nodes)
│       #   outputs/     GENERATED ONLY — never hand-edited
│       #     _manifest.json   run identity (§6.1)
│       #     metrics_long.csv / predictions.csv.gz / decision.json / figures/*.png …
├── deliverables/              # report & deck drafts built from evidence/build (product lead)
├── evidence/
│   ├── registry.yaml          # evidence ID → stage output + selector + where used
│   └── build/                 # GENERATED: tables, figures, numbers.json for report/deck/app
├── sandbox/<member>/          # personal scratch (gitignored); never read by stages, never cited
├── tools/scaffold_stages.py    # spec/stages.json → node folders, STAGE.md cards, §10 index (§3.1)
├── run_pipeline.py            # orchestrator: run / status / check (§6)
├── build_evidence.py          # registry → evidence/build (§7)
└── tests/                     # e5lib unit tests + cross-stage contract tests
```

Why **stage × task** folders: the pipeline is sequential, so a one-folder-per-person
layout would make people wait or copy each other's code. Splitting each stage into
`regression/` and `classification/` nodes lets two people work in parallel on the
same stage without touching the same files, while the stage order stays the textbook
order. `common/` is used where the two tasks genuinely share one node.

---

### 3.1 When the pipeline design changes (including the design-freeze meeting)

The structure is **not hard-wired** to the current 10 stages. The design flows one way:

`spec/pipeline_design.md` (prose, for humans) → `spec/stages.json` (stage list, for tools)
→ `tools/scaffold_stages.py` → `stages/*/*/STAGE.md` + the §10 index.

To change the pipeline:

1. Edit `spec/pipeline_design.md` — the only authoritative design. The original
   `docs/milestone3_baseline_pipeline_design_2026-10-13.txt` is superseded and not updated.
2. Mirror the change in `spec/stages.json`: add, remove, rename, merge or split stages; change
   `tasks` (`common` or `regression`/`classification`), `depends_on`, purpose, outputs, gate.
3. Run:

   ```bash
   python experiments/experiment_5/tools/scaffold_stages.py
   ```

   It creates new node folders, refreshes generated parts of existing cards (owner, status and
   human-written sections are kept), rebuilds the §10 index, and lists **orphan** folders that
   are no longer in the spec. It never deletes anything; move useful work, then remove orphans
   after review (CHANGELOG entry).
4. Before the design is frozen, just do this freely. After freeze (`stages.json` version
   `1.0`), each change also needs a `CHANGELOG.md` entry (§9.2); cards already
   `READY_FOR_REVIEW`/`ACCEPTED` are only refreshed with `--force`.

`scaffold_stages.py --check` exits non-zero if cards or the index are out of date with the
spec; it becomes one of the `run_pipeline.py check` conditions.

What stays fixed whatever the stages are: one node = one owner folder; nodes read only
upstream `outputs/`; one factory, one population guard, one manifest format, one evidence
registry. Only the list of nodes changes.

## 4. Roles and ownership (fill in at the kickoff meeting)

| Role | Owns (may edit) | Main stages | Person |
| --- | --- | --- | --- |
| Platform lead | `e5lib/`, `run_pipeline.py`, `build_evidence.py`, `tests/`, s01–s02 | 1, 2 | _TBD_ |
| Regression lead | `stages/*/regression/` | 3–9 (regression) | _TBD_ |
| Classification lead | `stages/*/classification/` | 3–9 (classification) | _TBD_ |
| Product / report lead | `s10_release/` (app, dashboard, deliverables), `evidence/registry.yaml`, `deliverables/` | 10 | _TBD_ |
| Experiment lead | `spec/` (with team approval), `CHANGELOG.md`, release tags; the only person who can order the migration (§12) | all | _TBD_ |
| Reviewer of the week | — (reads, signs off) | each gate | rotates |

Rules:

- One **owner** per node folder. Only the owner (or their agent) edits it.
- Every node has a **reviewer** who is not its owner. Regression and classification
  leads review each other — this also keeps both tasks methodologically aligned.
- `spec/` belongs to the whole team; edits need the change process in §9.
- With fewer people, merge roles (e.g. platform + product); with more, split a task
  lead into "modelling" and "diagnostics". Ownership stays one person per folder.

---

## 5. Shared contracts

### 5.1 Node contract (`STAGE.md` front matter)

Every node declares its interface in YAML front matter. The orchestrator reads it.

```yaml
---
node: s06_training/regression
owner: <name>
reviewer: <name>
status: TODO            # TODO | IN_PROGRESS | READY_FOR_REVIEW | CHANGES_REQUESTED | ACCEPTED | REOPENED
depends_on:             # upstream NODES; may only read their outputs/
  - s05_partition/regression
reads:                  # exact upstream files used (hashed into the manifest)
  - stages/s05_partition/regression/outputs/folds.csv
  - stages/s04_features/regression/outputs/recipes.json
  - spec/protocol.yaml
writes:                 # every file run.py produces, relative to outputs/
  - metrics_long.csv
  - predictions.csv.gz
  - decision.json
  - figures/
---
```

A node may read **only** files listed in `reads` that belong to `spec/` or to an
upstream node's `outputs/`. Never read another node's code, sandbox, or any
Milestone 2 artifact directly (s02_data and s05_partition import M2 inputs once,
explicitly, and record their hashes).

### 5.2 `spec/protocol.yaml` — the frozen contract (written in s01_problem)

Holds every number that otherwise tends to drift, in two layers:

- **Pre-registered** (fixed in s01, before any data is seen): tasks, positive class,
  eligibility, the 24-predictor contract (`e5lib/contract.py`) and the columns left out of it, seed `42`, test cutoff,
  purge and label-maturity rules, metric definitions, decision rules and tie-breaks, the
  cost assumption (FN:FP = 5:1, illustrative), search grids and budgets.
- **Data-dependent** (each section owned by one stage, added via CHANGELOG and frozen at
  that stage's gate, before any model result): core set and the selected set per task (s04); exact fold boundaries, class-support threshold and minimum training rows per fold (s05).

Code reads values from here; **no stage hard-codes these numbers**.

### 5.3 Candidates and the pipeline factory

- A **candidate** is a full recipe: `task, feature_set, numeric/categorical
  representation, imputation, scaling/encoding, input transforms, target treatment,
  estimator + params, calibration`. Nothing outside the spec may influence the fit.
- `candidate_id` is a readable, stable slug from the spec, e.g.
  `reg.core.raw.linreg`, `clf.core.raw.logit-none`, `reg.core.log1p.rf.d10-l20`.
  The same id in two stages means the identical pipeline.
- All stages build models only via `e5lib.factory.build(spec)`. The candidate selected in
  s08 is exactly the pipeline refitted and tested once in s08 and deployed in s10.

### 5.4 Population guard (leakage control)

`e5lib.data.load(task, population, caller)` is the only data loader.

| population | Who may load it |
| --- | --- |
| `development` (orders before the task's test cutoff, computed in s02 by the 80/20 rule; CV folds built in s05) | s02 onward |
| `test` (per task: newest 20% by the s02 cutoff; IDs frozen in s05; orders of customers also in development are removed from it) | s08 final evaluation onward only |

The loader raises if a stage loads a population it is not allowed to see. Do not
bypass it. Test labels must not influence any choice; s08 reads them only after the
recipe and threshold are frozen to `frozen_recipe.json`.

### 5.5 Standard output files

So that one master table and the report can be built mechanically, nodes use these
shapes whenever the content applies:

| File | Columns / content |
| --- | --- |
| `metrics_long.csv` | `node, task, population, phase(train/validation/test), fold, candidate_id, metric, value, n_rows, n_pos` |
| `predictions.csv.gz` | `order_id, task, population, fold, candidate_id, y_true, y_pred` (classification adds `p_raw`, `p_final`) |
| `decision.json` | `question, rule (from protocol.yaml), candidates_compared, chosen, evidence_files, notes` |
| `counts.json` | rows, customers, positives per population/fold |
| `figures/*.png` | each figure has a sidecar `*.json` with the data/coordinates used |
| `_manifest.json` | written by `e5lib.manifest` (§6.1) |
| `_evidence_index.json` | written by `Writer.finish`: solution-ID tags per file, checks, deviations and evidence-card text (§13) |
| `candidates.csv` | every option considered for a decision: `candidate_id, description, kept (yes/no), reason, evidence_files` (design rule 8) |
| `curves/*.csv` | data behind threshold, calibration, learning and validation curves, one row per point |

Design rule 8 (evidence kept, not recomputed): a stage records the intermediate results that led
to its decision, not only the final choice, so the report and deck can retrieve any table, figure
or number without rerunning a model. The s10 reproduction run writes the same files under its own
outputs plus a parity diff against the experiment run.

Units are fixed: lead time in **days**, probabilities in **[0,1]**, rates as fractions
in data and percentages only in rendered text.

---

## 6. Run, rerun and staleness

### 6.1 Run manifest

Each `run.py` ends by calling `e5lib.manifest.write(...)`, which records: node,
`run_id` (UTC timestamp), git commit + dirty flag, sha256 of the node's code,
`spec/protocol.yaml` and every file in `reads`, sha256 of every output, Python and
package versions, seed, runtime.

Review rounds run from the uncommitted working tree (G-64), so their manifests are marked dirty;
the sha256 hashes of code, foundation, protocol, inputs and outputs identify the run. At
acceptance the stage is committed and its manifest must still be FRESH against the committed
files; a release (`check`) needs a clean tree and every manifest FRESH. Since CR-042 an acceptance
is two steps, so the cited run has `dirty: false`: commit the code and spec, rerun the changed nodes
on that clean tree, then commit their outputs, review pack and stage card.

### 6.2 Orchestrator

```bash
python experiments/experiment_5/run_pipeline.py status
```

```bash
python experiments/experiment_5/run_pipeline.py run --from s04_features
```

```bash
python experiments/experiment_5/run_pipeline.py run --all
```

```bash
python experiments/experiment_5/run_pipeline.py check
```

- `status` prints every node: status, last run_id, **FRESH / STALE / MISSING**.
  A node is STALE if its code, `protocol.yaml`, or any upstream output hash differs
  from what its manifest recorded.
- `run` executes nodes in DAG order (regression and classification branches may run
  independently). `--node`, `--from`, `--task` narrow the run.
- After a rerun, `run` **diffs every `decision.json`** against the previous one. If a
  decision changed, that node's status is set to `REOPENED` and must go through
  review again; numbers that merely shift without changing a decision are reported
  but do not reopen the node.
- `check` = all nodes FRESH + clean tree + contract tests pass. It is the gate for a release.

This is the mechanism behind "anyone can change their part, and we can still rerun
everything": change your node → run `--from` your node → the orchestrator tells you
which downstream decisions moved → those owners review.

### 6.3 What is committed to git

- Commit `outputs/` (CSV/JSON/PNG, model bundles) so teammates can start downstream
  work without rerunning, and so evidence is versioned with the code that made it.
- Files > 50 MB are not committed; they are gitignored and their hash is still recorded in the
  manifest. Prefer `.csv.gz`. Such a file is still kept: the node owner copies it to the team's
  shared drive (path recorded in the manifest), so it can be retrieved without a rerun (design
  rule 8).
- Raw Olist CSVs are not in git; s02_data records their hashes so a teammate with a
  different copy gets a mismatch instead of silently different numbers.
- All paths are resolved through `e5lib/paths.py` relative to the Experiment 5 root (and
  the repo root for read-only inputs). No absolute paths, no paths into working folders
  as outputs. This keeps the later migration (§12) a path change, not a rewrite.

---

## 7. Evidence registry → report, deck, app

- `evidence/registry.yaml` lists every item the report/deck/app uses:

  ```yaml
  - id: T6.1-reg-training
    kind: table            # table | figure | number
    source: stages/s06_training/regression/outputs/metrics_long.csv
    select: {phase: validation, metric: [mae, rmse, r2]}
    aggregate: mean_sd_by_candidate
    used_in: [report §5.1, deck slide 6]
  ```

- `python experiments/experiment_5/build_evidence.py` writes `evidence/build/`
  (`tables/*.csv|.md`, `figures/*.png`, `numbers.json`, `_release.json`) and refuses to
  build if `run_pipeline.py check` fails.
- The report and deck cite evidence IDs; they never contain a number typed by hand.
  A small `verify` step in s10_release checks every number in the report text against
  `numbers.json`.
- Report and deck drafts live in `deliverables/`; the app and dashboard live in
  `stages/s10_release/common/` and load bundles from s08 `outputs/`. None of them
  is placed in `docs/reports/` or `deployment/` before migration (§0.1, §12).
- A **release** is a git tag `e5-release-N` on a commit where `check` passes and
  `evidence/build/_release.json` lists every node's `run_id`. With Pipeline B (G-79, CR-058) the
  release is the commit where A's frozen evidence and B's register (`pipeline_b/build_evidence_B.py`)
  both build from Current runs only, B's tests pass and the deliverables audit passes; its record is
  `pipeline_b/release/e5-release-N.json` (every A node's and every B stage's run ID, commit and tag). The report states which
  release it was built from. If anything changes later, cut `e5-release-N+1`; do not
  patch old evidence.

---

## 8. Rules for every teammate's AI agent (binding)

**Scope**

1. **Containment (§0.1):** write only inside `experiments/experiment_5/`. Never write,
   move or delete anything outside it — not Milestone 2 files, not `src/`, `artifacts/`,
   `deployment/`, `data/`, `docs/`, `notebooks/`, root files. Read-only access outside is fine.
   Do not migrate, copy or "promote" Experiment 5 work into working folders unless the
   experiment lead explicitly orders the migration (§12).
2. **Scope:** your working scope is whatever the human sets in the conversation, and it may
   change. Before editing a node, confirm it is one the human owns (`STAGE.md` `owner`) or
   was explicitly asked to work on. Inside Experiment 5 you edit only those node folders and
   `sandbox/<member>/`; `spec/`, `e5lib/`, tools and other members' nodes need a change
   request (§9.2) — propose it, do not do it.

**Data and leakage**

3. Load data only through `e5lib.data.load`; never bypass the population guard. Use the
   technical foundation exactly as §13 describes (paths, protocol, cv, factory, metrics,
   outputs with solution-ID tags, manifest, review packs).
4. Learned preprocessing (imputation, encoding, scaling, caps from percentiles,
   model-based feature selection, calibration) is fit **inside** training folds via the
   factory. Two declared exceptions (design rule 2): the s04 label-free reduction and the s04
   selection by the s03 importance ranking, both on pre-cutoff orders only.
   Only deterministic, row-local formulas may run before the split.
5. Never use test-cohort labels for any choice; s08 reads them once, after the recipe and
   threshold are frozen.
6. IDs (`order_id`, `customer_unique_id`) are for audit, never predictors.

**Modelling**

7. Build every model with `e5lib.factory.build(spec)`; identify it by `candidate_id`.
8. Families are dummy, linear/logistic and tree/forest only. Start with the simplest
   variant (dummy → plain LinearRegression / unregularised LogisticRegression →
   single tree) before regularisation, forests or tuning.
9. Compare one change at a time on the same rows and folds; a more complex variant is
   accepted only if it passes the decision rule in `protocol.yaml`. Keep the simpler
   one otherwise. Do not assume the Milestone 2 winner wins again.
10. Seeds, grids, fold boundaries, thresholds and costs come from `protocol.yaml`.
    Do not hard-code them and do not add new grid points silently.

**Outputs and evidence**

11. `run.py` must regenerate **all** of `outputs/` from scratch, deterministically, with
    no manual step and no notebook state. Never hand-edit anything in `outputs/`.
12. Use the standard output shapes (§5.5) and write the manifest.
13. Every decision is written to `decision.json` by code, using the rule from
    `protocol.yaml`; the human rationale goes into `STAGE.md` → *Review summary*.
14. Never type a metric into `STAGE.md`, the report or slides from memory; cite the
    output file or evidence ID.

**Process**

15. **Branches (CR-057, replaces the "work directly on milestone-3" rule of CR-002).**
    `milestone-3` is the one base everyone starts from and the only branch that holds
    accepted work. When more than one person (or their agent) works at the same time, each
    piece of work goes on its own short branch cut from the current `milestone-3`, named
    `e5/<topic>-<member>` (for example `e5/b11-henry`); the experiment lead reviews it and
    merges it back (fast-forward when possible), then the branch is deleted or left idle.
    Only the experiment lead commits directly on `milestone-3`, and only records (decision
    log, change log, evidence register, handover notes, the team-doc mirror). The migration
    runs on its own branch `e5/migration` (§12 step 3). Never push to `main`; never move or
    re-create a tag. Anyone who cannot edit the team doc writes doc-ready text to
    `pipeline_b/spec/doc_outbox/` and logs each session in `pipeline_b/WORKLOG.md`
    (with "Questions for Benson") and `pipeline_b/HANDOVER.md`; the lead verifies the
    branch, publishes the outbox and refreshes the mirror when merging.
    Pull before you start and before you push; never force-push. Commit only your own node folder and
    `sandbox/<you>/`; shared files (`spec/`, `e5lib/`, `tools/`, `CHANGELOG.md`) change only
    through the experiment lead. Build only on upstream outputs marked `ACCEPTED`. At a
    gate, record the commit hash in `STAGE.md` → Sign-off so the reviewer checks exactly
    that commit.
16. Before asking for review: `run_pipeline.py run --node <yours>` then
    `run_pipeline.py check`; fill *Review summary* and *Deviations* in `STAGE.md`;
    set status `READY_FOR_REVIEW`.
17. **Stop at the gate.** Do not start the next stage, change upstream nodes, or "fix"
    results to look better. Report what you found, including weak or negative results.
18. If the spec is unclear or seems wrong, write the question under *Open questions* in
    `STAGE.md` and stop; do not invent a new method or interpretation.
19. Do not delete or overwrite another node's outputs, manifests or git history.

---

## 9. Stage gates and change control

### 9.1 Implementation review loop (every stage; CR-024, G-59)

Stages are built one at a time in pipeline order, s01 to s10. A stage starts
only when every upstream stage is `ACCEPTED` and unchanged since acceptance; `run_pipeline.py`
enforces this. Prototyping in `sandbox/` is allowed but is never evidence.

**Technical foundation** (not a pipeline stage, no stage review; G-60): `e5lib/` (paths, data
loader and population guard, factory, cv, manifest), `run_pipeline.py`, the review-pack
generator, `build_evidence.py` and `tests/`. It is built first and changed whenever a stage
review needs it. Every foundation change is logged in `CHANGELOG.md` and must keep the contract
tests passing; if it changes the outputs of an ACCEPTED stage, that stage is rerun and reopened
(§9.2). Each stage review shows the foundation commit its run used.

**Statuses** (`STAGE.md` front matter): `TODO → IN_PROGRESS → READY_FOR_REVIEW →
CHANGES_REQUESTED → … → ACCEPTED`, and `REOPENED` when an upstream change (§9.2) sends an accepted
stage back for review.

**One round of the loop**
1. *Build*: code exactly as the AGREED blueprint says. Every code change names the solution ID
   it serves (2.1, 3.4, …) and fills that row of the stage card's working log. A difference
   from the blueprint is written as a deviation, never made silently.
2. *Run*: `run_pipeline.py run --node sNN`. All outputs, including process evidence (design rule 8),
   go under `stages/sNN/<task>/outputs/` with `_manifest.json`.
3. *Pack*: code generates `stages/sNN/<task>/review/round_N/review_pack.md` with the coverage
   table: every solution ID of the stage, each marked IMPLEMENTED, DEVIATION or MISSING. Nothing is
   committed or pushed for a round (G-64); status `READY_FOR_REVIEW`.
4. *Review*: the stage's tab under "Implementation reviews" in the team doc (below). Reviewers
   approve or comment per row there; the tab carries every value they need, so nobody opens the
   repository.
5. *Fix*: each comment is answered in its thread; fixes become round N+1 (new run and pack).
   Rows whose evidence hashes did not change keep their approval; changed rows are reviewed
   again. Status `CHANGES_REQUESTED` until the next pack.
6. *Accept*: every row Approved, no MISSING row, every check PASS. The experiment lead approves;
   the stage is then committed on `milestone-3` (one commit, "sNN accepted", local; pushed only on
   the lead's instruction), its manifest checked FRESH against that commit, and the card records
   the accepted round, commit, run ID, approver and date; the commit is tagged `e5-sNN-accepted`;
   the next stage unlocks. The same commit refreshes `spec/team_doc/`, a read-only Markdown mirror of every
   tab of the team doc (pipeline, solutions, implementation reviews), so an auditing agent can
   check the repository against it (G-65). The team keeps working in the commented doc; the
   mirror is never edited or reviewed.

**s06–s08: one team review for three stages (G-78).** s06, s07 and s08 are still built one at a
time, each with its own rounds, pack and doc tab. The experiment lead reviews each stage briefly
and accepts it (step 6 above: commit, tag, next stage unlocks); the team does not review them one
by one. s08 runs only up to its gate (8.1–8.4: model choice, calibration, threshold table) and
stops there; nothing reads the test cohort. The team then reviews s06, s07 and s08 together in one
combined round, together with the two s08 decisions (G-39). A change that comes out of that review
is a change request that reopens the earliest stage it affects (§9.2); `run_pipeline.py` marks every
later stage STALE and they are rerun in order, each with a new round. Only after the team signs off
the combined round do 8.5–8.7 (freeze, final fit, test once) run, so no review comment can follow a
look at test results.

**Evidence card** (one per solution ID, generated from output files, never typed): approved
solution (quoted); what was done and inputs; process data (intermediate tables); results (small
tables inline, large ones as top rows plus link; charts shown inline); expectation vs
observation; reasoning and conclusion, each claim labelled observation / literature-supported
hypothesis / unmeasured mechanism; deviation; checks (PASS/FAIL); file paths with the run ID and
output hashes, evidence IDs and figure sidecars.

**Team doc layout** ("Implementation reviews" tab): one tab per stage; stages that run per task
(s03–s09) get one sub-tab per task for the evidence cards, while the stage tab holds the status
banner, the coverage table for both tasks, the decisions for the team (s03 and s08 human gates)
and the round history. A stage tab is created when the stage starts. Each tab has a *Current*
layer (latest round only; the only place to read the result) and an append-only *Round history*
(what changed, which rows were rerun, every comment and its resolution). Before a card is
replaced, its previous version is copied into the round history. Tabs are never deleted: once
accepted they are frozen as the record, and later changes are added as dated sections.

**Records in the repo**: `review/round_N/` keeps each round's pack, coverage table and exported
comment threads; the stage card's working log, round table and accepted result point to them.
The report, slides, app and dashboard cite only the accepted round.

**Progress view**: the Pipeline v2 chart in the team doc carries two tags per stage, design
(APPROVED) and build (NOT STARTED, BUILDING, IN REVIEW, CHANGES, ACCEPTED, REOPENED), and a ✓ on
each step box whose solution IDs are all approved; the chip-to-ID map sits under the chart. The
progress table in `spec/blueprints/README.md` mirrors it.

### 9.2 Changing something after acceptance

1. Add an entry to `CHANGELOG.md`: what, why, which file(s), expected affected nodes.
2. Team (at least one other member) approves it; the approver is named in the CHANGELOG row.
3. Make the change; `run_pipeline.py run --from <earliest affected node>`.
4. Nodes whose decisions changed go `REOPENED` → re-review. Others stay ACCEPTED but
   with the new run_id.
5. Changes to `spec/` or `e5lib/factory.py` almost always require `--from s04_features` or earlier.

### 9.3 Special rule for the test cohort (s08)

The test cohort is scored once per release, at the end of s08. Once its results have been
looked at, any change to s03–s08 means the test has been used for selection: record it in
`CHANGELOG.md` as a **reopened selection** and say so in the report. Experiment 5 is
independent of earlier milestones (G-29): its test cohort is defined and scored only here, so it
is described as a new-customer time-ordered holdout with its actual share, unseen by every
Experiment 5 decision (G-38, G-48).

---

## 10. Stage index

Detailed requirements: [`spec/pipeline_design.md`](spec/pipeline_design.md) (frozen v1.0). Each
node's `STAGE.md` repeats its purpose, outputs and gate criteria.

<!-- BEGIN STAGE INDEX from spec/stages.json -->
_Generated from `spec/stages.json` v1.0 (pipeline_design.md v1.2 (frozen 2026-10-17; CR-003 audit, CR-004 feature solution)). Do not edit by hand._

| Stage | Nodes | Depends on | Key outputs | Gate question |
| --- | --- | --- | --- | --- |
| s01_problem Problem statement | common | - | spec/protocol.yaml v1.0; task_contract.md | Are tasks, targets, metrics, cost, decision rule and budget fixed before any result? |
| s02_data Data preprocessing | common | s01_problem | records.csv.gz; exclusions.csv; data_hashes.json | Are joins, grains, targets and leakage exclusions verified? |
| s03_eda EDA | regression, classification | s02_data | figures/*.png + sidecar json; target and per-feature diagnostic tables; importance_ranking.csv | Does every planned change follow from a pre-cutoff observation? |
| s04_features Features | regression, classification | s03_eda | feature_dictionary.csv; selected_features.json; recipes.json | Are features and recipes defined without fitting or using labels? |
| s05_partition Partition | regression, classification | s02_data | folds.csv; test_manifest.csv; counts.json | Are folds chronological, customers purged, labels mature and classes supported? |
| s06_training Training | regression, classification | s04_features, s05_partition | metrics_long.csv; predictions.csv.gz; figures/ | Do the models run basic to complex on identical folds, with each choice justified? |
| s07_tuning Tuning | regression, classification | s06_training | grid_results.csv; predictions.csv.gz | Is every tuned candidate a complete pipeline scored on the same folds? |
| s08_selection Selection | regression, classification | s07_tuning | selected_spec.json; threshold_table.csv; frozen_recipe.json | Was the recipe frozen before the test cohort was scored once? |
| s09_conclusion Conclusion | regression, classification | s08_selection | master_metrics.csv; subgroups.csv; drift.csv | Does every conclusion follow from the test results and their limits? |
| s10_release Release | common | s09_conclusion | parity.json; input_validation.json; migration_check.json | Do the app, dashboard, report and slides all trace to one reproduced release? |
<!-- END STAGE INDEX -->

---

## 11. Getting started (after the kickoff meeting)

0. ~~Freeze the design~~ — done 2026-10-17 (CR-001): `pipeline_design.md` and
   `stages.json` v1.0, cards regenerated.
1. Fill roles in §4 and `owner`/`reviewer` in each `STAGE.md`.
2. ~~Build the technical foundation~~ — done 2026-10-18 (CR-026): `e5lib/`, `run_pipeline.py`,
   `build_evidence.py`, review-pack generator and contract tests, as §13 documents. It is not a
   stage and has no stage review (G-60).
3. Team completes s01_problem together and freezes `spec/protocol.yaml` (v1.0).
4. Proceed stage by stage through the gates in §9. Start each teammate's agent with
   [`AGENT_INIT_PROMPT.md`](AGENT_INIT_PROMPT.md).

Open items for the kickoff:

- [ ] Team size and role assignment (§4).
- [x] Milestone 2 TA comments: not waited for (Milestone 2 still being graded); the
      teacher's Milestone 2 expectation note is the rubric (team decision 2026-10-17).
- [x] Decision rule agreed in s01: one-standard-error rule (G-33, CR-014).
- [ ] Confirm outputs-in-git policy (§6.3) and the 50 MB limit.
- [ ] Confirm each member has the Olist raw CSVs and the tutorials locally
      (`docs/` and `data/raw/` are not in git).

---

## 12. Migration to the working folders (only after full approval)

Experiment 5 is the staging area. Its results become the project's working version only
through one deliberate migration:

1. **Preconditions:** every node `ACCEPTED`, or replaced under G-79 (A's s08.6–8.8 by T1,
   A's s09 by B9, A's s10 by B10; CR-058); `run_pipeline.py check` passes on Pipeline A, and
   Pipeline B passes its own checks and tests (B relies on A's frozen code read-only, not on A's
   check; a guard finding that lists only `pipeline_b/` files is a recorded deviation, fixed in
   the migrated code at step 3; CR-058); a release tag `e5-release-N` exists, cut before the
   migration starts; the team has approved the whole experiment; the **experiment lead
   explicitly instructs** the migration. No agent starts it on its own initiative, and
   nobody migrates individual stages early.
2. **Migration plan first** (written into `CHANGELOG.md` and approved): a file-by-file map,
   e.g. `e5lib/` → `src/…`, stage `run.py` files → `src/…` or `pipelines/…`, release
   evidence → `artifacts/…`, s10 app and dashboard → `deployment/`, `deliverables/` →
   `docs/reports/`, a reproduction README at the repo root,
   pinned requirements → root `requirements*.txt`, plus which Milestone 2 files are archived
   rather than overwritten.
3. **Migrate on a dedicated branch** (`e5/migration`), changing paths only — no logic,
   parameter or data change.
4. **Prove reproducibility in the working folder:** run the full pipeline from the migrated
   code on a clean checkout; every output hash (models excepted only if documented
   non-determinism) and every number in `evidence/build/numbers.json` must match release
   `e5-release-N`. Record the comparison as `migration_check.json`.
   **Reference machine and tolerance (CR-056).** The hash check above is run on the experiment
   lead's machine (the machine that produced the release), and it is the gate for step 5. A rerun
   on any other machine (other OS, BLAS or CPU) is judged by tolerance, not hashes: predictions
   within 1e-9 (absolute); scores of stages that refit (fold and test metrics, calibration,
   threshold tables) within 2e-3 absolute; counts (rows, alerts, TP/FP/FN) equal; every number
   the report and slides show equal at the precision shown. `migration_check.json` records which
   machine ran it and which rule applied.
5. Merge only after that check passes. `experiments/experiment_5/` stays in the repo,
   frozen, as the record of how the evidence was produced.

---

## 13. Technical foundation: how to use it (for humans and AI agents)

The foundation is the shared code every stage runs on (G-60). It is not a pipeline stage and
has no stage review. **This section is the contract:** the code must match it, and any change to
a function name, argument or behaviour updates this section in the same commit and adds a
CHANGELOG row. If the code and this section disagree, stop and ask the human.

### 13.1 What it gives you

Status: built and covered by `tests/` (CR-026). The signatures below are the ones in the code.

| Module / tool | Use it for | Never do instead |
| --- | --- | --- |
| `e5lib/__init__.py` | `STAGE_ORDER`, `TASKS`, `stage_rank(stage)` | Comparing stage names as strings |
| `e5lib/paths.py` | Every path: `E5`, `REPO`, `stage_dir(stage, task)`, `outputs_dir(stage, task)`, `review_dir(stage, task, round)`, `raw_data_dir()` (Canvas CSVs, read-only), `reference_dir()` (`data/reference/`, staged IBGE geography, read-only), `spec_path(name)`, `evidence_dir()`, `assert_inside_e5(path)`, `rel(path)` | Hard-coded or absolute paths; writing outside `experiments/experiment_5/` |
| `e5lib/cleaning.py` | s02 only: `load_clean(table, stage)` reads one raw table with the declared Milestone 2 cleaning schema (`TABLES`), returns `(frame, log)`; `normalize_state`; `BR_STATES`, `USABLE_PAYMENT_TYPES`, `UNKNOWN` | Reading raw CSVs with pandas directly |
| `e5lib/aggregation.py` | s02 only: `resolve_english_category`, `aggregate_items`, `aggregate_payments`, `aggregate_reviews` (order grain, Milestone 2 formulas; first-review label and label timestamps) | Joining fact tables before aggregating |
| `e5lib/seller_history.py` | s02 only: `seller_history(orders, reviews, deliveries)`: the primary seller's review and delivery history strictly before each purchase, own order excluded (G-69); `brute_force(...)` for the s02 check | Rolling means over purchase time (leaks reviews answered after checkout) |
| `e5lib/features.py` | s04 both nodes: `pool_ranking`, `transforms`, `reduction`, `selection`, `recipes`/`factory_spec`, `design_matrix` and the node runner `run(task)`; the pool only through `contract.pool(task)`, decisions only from human_decisions.yaml | Hand-written feature lists; fitting anything in s04 |
| `e5lib/eda.py`, `e5lib/eda_sections.py` | s03: statistics (`profile`, `correlations`, `rank_correlation_ratio`, `overlap`, `auc`, `mutual_information`, `vif`, `collinear_groups`, `cumulative_ranking`, `cut_point`) and the shared output sections (trends, quality and collinearity, ranking, rationale, `eda_review_pack.md`, `screen_group` for candidates) | Re-implementing a statistic inside a stage |
| `e5lib/geography.py` | s02 only: `load_boundary()` (verified IBGE polygon), `zip_centroids`, `distance_features`, `haversine_km`, `normalize_zip` | Bounding boxes or unverified boundaries |
| `e5lib/contract.py` | The predictor contract (s01 1.3; G-61, G-62): `PREDICTORS` (24), `pool(task)` (the selection pool s04 uses: the 24 + the candidates adopted at the s03 gate, read from `spec/human_decisions.yaml`; G-70), `SCREENING_CANDIDATES` (classification screen, G-68, G-69; adoption in `spec/human_decisions.yaml`, G-70), `CATEGORICAL`, `CALENDAR_NUMERIC`, `COUNTS`, `SHARES`, `LOG_CANDIDATES`, `NEVER_LOGGED`, `NOT_IN_CONTRACT` (column → reason), `numeric()`, `validate()`. s01 copies these lists into `protocol.yaml`; later stages read them from there | Typing feature lists into a stage |
| `e5lib/protocol.py` | Reading `spec/protocol.yaml` (created by s01): `load()`, `get("dotted.key", default)`. Data-dependent sections are written only by their owner via `set_data_dependent(section, values, stage)`: `test_cutoffs` (s02); `core_set`, `selected_set` (s04); `fold_boundaries`, `class_support`, `min_training_rows` (s05). An existing value is never overwritten unless `replace=True` after a CHANGELOG entry | Typing a number that lives in protocol.yaml |
| `e5lib/data.py` | All data access, through the population guard:<br>`reference(relpath, stage)`: a staged reference file under `data/reference/` (IBGE geography), s02 only;<br>`load_raw(table, stage)`: raw tables, s02 only (`orders`, `order_items`, `order_payments`, `order_reviews`, `customers`, `sellers`, `products`, `geolocation`, `category_translation`);<br>`load("records", task, population, stage)`: s02 records for one task, `population` = `development` (before the task's cutoff), `test` (s08 after `frozen_recipe.json`, and later) or `all` (s05 only);<br>`upstream(source_stage, source_task, filename, stage)`: path of an earlier stage's output.<br>Breaking a rule raises `PopulationError`; every read is recorded for the manifest (`reads()`) | `pandas.read_csv` on data files; filtering test rows yourself |
| `e5lib/cv.py` | The s05 folds: `folds(task, stage)` yields `(fold, train_order_ids, val_order_ids)`; `sklearn_splits(order_ids, task, stage)` gives positional splits for `cv=`; `check_fold_rules(folds_df, records)` asserts training-before-validation and no shared customer | `KFold`, `TimeSeriesSplit` or any split of your own |
| `e5lib/candidates.py` | `make_id(spec)`: stable, readable `candidate_id`, e.g. `reg.sel.log.ridge.alpha=10` (§5.3) | Hand-written IDs |
| `e5lib/factory.py` | `build(spec)` returns one unfitted sklearn estimator; `feature_columns(spec)` lists the columns it reads. Spec keys: `task`, `numeric`, `categorical`, `log_inputs`, `estimator` (`dummy_median`, `linear`, `ridge`, `tree_reg`, `forest_reg`, `dummy_prior`, `logistic`, `tree_clf`, `forest_clf`), `params`, `route_median`, `log_target`, `calibration` (`"sigmoid"`; rows sorted by purchase time), `random_state`. Imputation with missing indicators, one-hot (drop-first and scaling for linear/logistic only), route-median imputer, log target and calibration are all fitted inside `.fit()` | Building estimators or preprocessing outside the factory |
| `e5lib/metrics.py` | `score(task, y_true, y_pred=None, proba=None, threshold=None)` returns every s01 metric (MAE, RMSE, R², within ±3 days; AP, ROC-AUC, Brier, confusion counts, precision, recall, F1, alert rate, error rate, 5:1 cost); `fold_summary(results, metric)`; `one_se_select(results, metric, higher_is_better, simplicity)` applies the s01 rule (G-33, G-55); `PRIMARY` gives each task's primary metric | Re-implementing metrics or the selection rule |
| `e5lib/outputs.py` | The only way to write outputs: `Writer(stage, task)` empties `outputs/` and offers `.metrics_long(df, ids)`, `.predictions(df, ids)`, `.candidates(df, ids)`, `.table(name, df, ids)`, `.curve(name, df, ids)`, `.figure(name, fig, data, ids)` (PNG plus sidecar data), `.json(name, obj, ids)`, `.text(name, content, ids)`, `.decision(question, rule, candidates, chosen, files, ids)`; review support: `.check(name, passed, ids, detail)`, `.deviation(id, text)`, `.explain(id, done=, inputs=, expectation=, observation=, reasoning=, conclusion=, label=)` (evidence-card text built from computed values); end of run: `.finish(seed)` writes `_evidence_index.json`, `decision.json` and the manifest. **Every output takes `ids=(...)`, the solution IDs it serves** | `df.to_csv`/`plt.savefig` straight into `outputs/`; outputs without solution IDs; typed numbers in card text |
| `e5lib/manifest.py` | Called by `Writer.finish`: `write(stage, task, reads, seed)` (§6.1); `read(stage, task)`; `status(stage, task)` returns FRESH / STALE / MISSING with reasons (stage code, foundation code, protocol, inputs or outputs changed) | Skipping the manifest |
| `e5lib/review.py` | `build_pack(stage, task, round)` (via `run_pipeline.py pack`): writes `review/round_N/review_pack.md` and `pack.json` with the coverage table over `spec/solution_ids.json` (IMPLEMENTED / DEVIATION / MISSING, PASS / FAIL checks, changed since last round), evidence cards, inline figures and relative links to the round's output files; the pack header shows the run ID, the base commit and whether the outputs are FRESH. Rounds are packed from the uncommitted working tree (G-64); `coverage(stage, task)` | Writing review packs by hand |
| `spec/solution_ids.json` | The approved solution IDs per stage (and per task where an ID applies to one task); the coverage table is checked against it | Coverage lists kept by hand |
| `run_pipeline.py` | `status`; `run --node <stage/task>` or `run --from <stage> [--task]` (refuses unless every upstream node is ACCEPTED and FRESH; TODO becomes IN_PROGRESS; an ACCEPTED node whose `decision.json` changes becomes REOPENED); `pack --node <stage/task> --round N` (append-only rounds; sets READY_FOR_REVIEW); `check` (all FRESH, clean tree, tests pass) | Running `run.py` files directly for evidence |
| `build_evidence.py` | `--draft` writes `evidence/build_draft/` (not committed); without it, builds `evidence/build/` only when `check` passes, from `evidence/registry.yaml` | Copying numbers into documents |
| `tests/` | Contract tests on a throwaway copy of the folder: guards, protocol ownership, folds, factory, metrics and the one-SE rule, writer tags, manifests, review packs and the run gate | Committing with failing tests |

### 13.2 The shape of every stage's `run.py`

```python
"""s02_data/common: data preprocessing (blueprint spec/blueprints/s02_data.md)."""
from e5lib import data, protocol
from e5lib.outputs import Writer

STAGE, TASK = "s02_data", "common"


def main() -> None:
    p = protocol.load()
    w = Writer(STAGE, TASK)                               # starts from an empty outputs/
    orders = data.load_raw("orders", stage=STAGE)         # s02 only; later stages use data.load
    # ... one function per solution ID, each tagging its outputs ...
    w.table("exclusions", exclusions_df, ids=("2.8", "2.9", "2.10", "2.11"))
    w.figure("data_structure", fig, data=edges_df, ids=("2.12",))
    w.check("rows equal orders", n_rows == n_orders, ids=("2.4",), detail=f"{n_rows} rows")
    w.explain("2.9", expectation="...", observation=f"{n_removed} orders removed", conclusion="...")
    w.decision(question="...", rule=p["..."], candidates=[...], chosen=..., files=[...], ids=("2.9",))
    w.finish(seed=p["seed"])                              # evidence index + manifest


if __name__ == "__main__":
    main()
```

Rules: one function per solution ID (or a clearly named group), no hard-coded numbers, no
direct file reads or writes, every output tagged with the solution IDs it serves, and card text
built from computed values. The tags are what make the coverage table and the working log
complete.

### 13.3 Day-to-day commands

One-time setup (the environment lives inside the Experiment 5 folder and is not committed):

```bash
python3 -m venv experiments/experiment_5/.venv
```

```bash
experiments/experiment_5/.venv/bin/pip install -r experiments/experiment_5/requirements.txt
```

Then, with `PY=experiments/experiment_5/.venv/bin/python`:

```bash
$PY experiments/experiment_5/run_pipeline.py status
$PY experiments/experiment_5/run_pipeline.py run --node s02_data/common
$PY experiments/experiment_5/run_pipeline.py pack --node s02_data/common --round 1
$PY experiments/experiment_5/run_pipeline.py check
$PY -m pytest experiments/experiment_5/tests
```

**Windows** (PowerShell, from the repository root): the interpreter is
`experiments\experiment_5\.venv\Scripts\python.exe`; the commands are otherwise the same.
Outputs and manifests are byte-identical across operating systems (CR-031):
`experiments/experiment_5/.gitattributes` checks every text file out with LF, and every writer
in the foundation writes UTF-8 with LF line endings. A clone made before CR-031 still has CRLF
files in the working tree; refresh the folder once (this discards uncommitted changes inside
`experiments/experiment_5/` only; the local `.venv` is not tracked and is kept):

```powershell
git rm -r -q --cached experiments/experiment_5
git checkout HEAD -- experiments/experiment_5
```

To audit an accepted stage without changing anything, run `status`: it must show the stage
`FRESH`. A rerun (`run --node`) must leave every output byte-identical; only `_manifest.json`
changes (new run ID); an auditor discards it rather than committing it.

The raw CSVs in `data/raw/` are outside this folder and its `.gitattributes`, so git may check them
out with CRLF on Windows (or with `core.autocrlf`). The accepted input hashes were taken on LF bytes, so such a
checkout makes every stage `STALE` (input changed) although the data are the same (CR-042, audit
H-01, L-01). Check out `data/raw/` with LF (for example `git -c core.autocrlf=false checkout -- data/raw`)
before running `status`; this folder never writes there.

### 13.4 When the foundation must change

1. A stage review (or a bug) shows the foundation needs to change: change it, keep or extend the
   tests, and update §13 in the same commit.
2. Add a CHANGELOG row naming the change and the stages it can affect.
3. Run `run_pipeline.py status`: any ACCEPTED stage whose outputs would change goes to
   REOPENED and is rerun and re-reviewed (§9.2). Each stage review shows the foundation commit
   its run used.
