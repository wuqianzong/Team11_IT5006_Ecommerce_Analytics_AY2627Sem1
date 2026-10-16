# Experiment 5 — Milestone 3 clean baseline (textbook-sequence replay of Milestone 2)

Status: **PROTOCOL DRAFT v0.1 (2026-10-16) — for team discussion. No implementation yet.**
Branch: `milestone-3`. Owner of this protocol: team (changes follow §9).

---

## 0. Read this first (humans and AI agents)

Experiment 5 is **not a new study**. It replays the Milestone 2 direction
(Olist, two checkout-time tasks, leakage exclusions, 9-feature core,
task-specific 11/12-feature expansions, linear and tree families) but executes it
in the **textbook order taught in Tutorials 1–8**, with **one validation protocol,
one pipeline factory and one evidence registry** from start to finish.

Its purpose is a baseline whose pipeline, code, data and evidence are
**clear, accurate and logically connected**, so the Milestone 3 report, deck and
app can all be regenerated from one command after any change.

**If you are an AI agent:** before editing anything, read in this order:

1. this README (the rules — binding);
2. [`spec/pipeline_design.md`](spec/pipeline_design.md) (what each stage must do — binding once frozen);
3. [`spec/sources.md`](spec/sources.md) (teacher expectations, TA feedback, tutorial mapping);
4. the `STAGE.md` of the stage/task folder you were assigned.

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
| Grouped screening compared with chronological confirmation | **One frozen protocol** in `spec/protocol.yaml`, written in Stage 0, used by every stage (§5.2) |
| Pipeline changed but downstream evidence not rerun | **DAG orchestrator** marks downstream stages **STALE** and reruns them; decisions that flip are sent back to review (§6) |
| Hand-copied numbers in report/deck | **Evidence registry** maps every table/figure/number to a stage output; report/deck/app read only `evidence/build/` (§7) |

---

## 2. Authority order

When documents disagree, the higher item wins:

1. Project brief (`docs/Project/IT5006 Project Description …pdf`) — requirements.
2. Teacher expectations ([`spec/teacher_expectation_m2.md`](spec/teacher_expectation_m2.md)) and TA feedback (summarised in `spec/sources.md`).
3. Tutorials 1–8 sequence (mapped per stage in `spec/pipeline_design.md` and `spec/sources.md`).
4. [`spec/pipeline_design.md`](spec/pipeline_design.md) — the agreed Milestone 3 pipeline (the authoritative copy; supersedes the `docs/` original).
5. `spec/protocol.yaml` — the frozen numeric contract (seeds, folds, grids, decision rules). Created in Stage 0.
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
│   ├── pipeline_design.md     # THE Milestone 3 pipeline design (authoritative copy; edited until frozen)
│   ├── stages.json            # machine-readable stage list derived from the design (§3.1)
│   ├── sources.md             # teacher/TA/tutorial requirements → stage mapping
│   ├── teacher_expectation_m2.md
│   └── protocol.yaml          # frozen numbers & rules, written by Stage 0
├── e5lib/                     # SHARED code (platform owner; change via PR + review)
│   ├── paths.py               # all paths; no stage hard-codes a path
│   ├── data.py                # loaders with population guard (§5.4)
│   ├── factory.py             # the ONE pipeline factory: spec → sklearn Pipeline
│   ├── candidates.py          # candidate spec → candidate_id
│   ├── metrics.py             # metric definitions (MAE, RMSE, R2, AP, ROC-AUC, Brier, cost)
│   ├── cv.py                  # fold iteration, customer purge, label-maturity filter
│   └── manifest.py            # run manifest write/read, hashing, staleness check
├── stages/                    # HOW it ran — one folder per node, GENERATED from spec/stages.json
│   ├── s00_contract/common/   #   (current draft list; see §10 for the live index)
│   ├── s01_records/common/
│   ├── s02_partitions/{regression,classification}/
│   ├── …                      #   s03_eda … s10_benchmark, each {regression,classification}
│   ├── s11_deployment/common/
│   └── s12_package/common/
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

The structure is **not hard-wired** to the current 13 stages. The design flows one way:

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
   in a reviewed PR.
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
| Platform lead | `e5lib/`, `run_pipeline.py`, `build_evidence.py`, `tests/`, S00–S02 | 0, 1, 2 | _TBD_ |
| Regression lead | `stages/*/regression/` | 3–10 (regression) | _TBD_ |
| Classification lead | `stages/*/classification/` | 3–10 (classification) | _TBD_ |
| Product / report lead | `s11_deployment/` (incl. the app), `s12_package/`, `evidence/registry.yaml`, `deliverables/` | 11, 12 | _TBD_ |
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
node: s04_baselines/regression
owner: <name>
reviewer: <name>
status: TODO            # TODO | IN_PROGRESS | READY_FOR_REVIEW | ACCEPTED | REOPENED
depends_on:             # upstream NODES; may only read their outputs/
  - s02_partitions/regression
  - s03_eda/regression
reads:                  # exact upstream files used (hashed into the manifest)
  - stages/s02_partitions/regression/outputs/selection_folds.csv
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
Milestone 2 artifact directly (Stage 1/2 import M2 inputs once, explicitly, and
record their hashes).

### 5.2 `spec/protocol.yaml` — the frozen contract (written in Stage 0)

Holds every number that otherwise tends to drift: tasks, positive class, eligibility,
predictor lists (core 9, regression 11, classification 12), excluded columns, seed
`42`, fold boundaries, purge and label-maturity rules, metric definitions, decision
rules and tie-breaks ("simpler wins within 1 SD", etc.), the cost assumption
(FN:FP = 5:1, illustrative), search grids and budgets. Code reads values from here;
**no stage hard-codes these numbers**.

### 5.3 Candidates and the pipeline factory

- A **candidate** is a full recipe: `task, feature_set, numeric/categorical
  representation, imputation, scaling/encoding, input transforms, target treatment,
  estimator + params, calibration`. Nothing outside the spec may influence the fit.
- `candidate_id` is a readable, stable slug from the spec, e.g.
  `reg.f9.raw.linreg`, `clf.f12.raw.logit-none`, `reg.f11.log1p-cap60.rf.d10-l20`.
  The same id in two stages means the identical pipeline.
- All stages build models only via `e5lib.factory.build(spec)`. The winner of
  Stage 7/8 is exactly the pipeline confirmed in S09, refitted in S10 and deployed in S11.

### 5.4 Population guard (leakage control)

`e5lib.data.load(task, population, caller)` is the only data loader.

| population | Who may load it |
| --- | --- |
| `selection` (four earlier expanding windows) | S03–S08 |
| `confirmation` (last pre-terminal window, ≈2018-03-08 → 2018-05-25) | S09 onward only |
| `benchmark` (M2 terminal cohort) | S10 onward only |

The loader raises if a stage loads a population it is not allowed to see. Do not
bypass it. Confirmation and benchmark labels must not influence any choice in S03–S08.

### 5.5 Standard output files

So that one master table and the report can be built mechanically, nodes use these
shapes whenever the content applies:

| File | Columns / content |
| --- | --- |
| `metrics_long.csv` | `node, task, population, phase(train/validation/confirmation/benchmark), fold, candidate_id, metric, value, n_rows, n_pos` |
| `predictions.csv.gz` | `order_id, task, population, fold, candidate_id, y_true, y_pred` (classification adds `p_raw`, `p_final`) |
| `decision.json` | `question, rule (from protocol.yaml), candidates_compared, chosen, evidence_files, notes` |
| `counts.json` | rows, customers, positives per population/fold |
| `figures/*.png` | each figure has a sidecar `*.json` with the data/coordinates used |
| `_manifest.json` | written by `e5lib.manifest` (§6.1) |

Units are fixed: lead time in **days**, probabilities in **[0,1]**, rates as fractions
in data and percentages only in rendered text.

---

## 6. Run, rerun and staleness

### 6.1 Run manifest

Each `run.py` ends by calling `e5lib.manifest.write(...)`, which records: node,
`run_id` (UTC timestamp), git commit + dirty flag, sha256 of the node's code,
`spec/protocol.yaml` and every file in `reads`, sha256 of every output, Python and
package versions, seed, runtime.

A run made from a **dirty** working tree is allowed for development but is
**never** eligible for a release.

### 6.2 Orchestrator

```bash
python experiments/experiment_5/run_pipeline.py status
```

```bash
python experiments/experiment_5/run_pipeline.py run --from s05_features
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
- Files > 50 MB are not committed; they are gitignored, regenerated by `run`, and
  their hash is still recorded in the manifest. Prefer `.csv.gz`.
- Raw Olist CSVs are not in git; Stage 1 records their hashes so a teammate with a
  different copy gets a mismatch instead of silently different numbers.
- All paths are resolved through `e5lib/paths.py` relative to the Experiment 5 root (and
  the repo root for read-only inputs). No absolute paths, no paths into working folders
  as outputs. This keeps the later migration (§12) a path change, not a rewrite.

---

## 7. Evidence registry → report, deck, app

- `evidence/registry.yaml` lists every item the report/deck/app uses:

  ```yaml
  - id: T5.1-reg-baselines
    kind: table            # table | figure | number
    source: stages/s04_baselines/regression/outputs/metrics_long.csv
    select: {phase: validation, metric: [mae, rmse, r2]}
    aggregate: mean_sd_by_candidate
    used_in: [report §5.1, deck slide 6]
  ```

- `python experiments/experiment_5/build_evidence.py` writes `evidence/build/`
  (`tables/*.csv|.md`, `figures/*.png`, `numbers.json`, `_release.json`) and refuses to
  build if `run_pipeline.py check` fails.
- The report and deck cite evidence IDs; they never contain a number typed by hand.
  A small `verify` step in S12 checks every number in the report text against
  `numbers.json`.
- Report and deck drafts live in `deliverables/`; the S11 app lives in
  `stages/s11_deployment/common/` and loads bundles from S10 `outputs/`. None of them
  is placed in `docs/reports/` or `deployment/` before migration (§0.1, §12).
- A **release** is a git tag `e5-release-N` on a commit where `check` passes and
  `evidence/build/_release.json` lists every node's `run_id`. The report states which
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

3. Load data only through `e5lib.data.load`; never bypass the population guard.
4. Learned preprocessing (imputation, encoding, scaling, caps from percentiles,
   feature selection, calibration) is fit **inside** training folds via the factory.
   Only deterministic, row-local formulas may run before the split.
5. Never use confirmation or benchmark labels for any choice made in S03–S08.
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

15. Work on branch `e5/<node-id>` (e.g. `e5/s04-regression`) from `milestone-3`; open a
    PR into `milestone-3`. One gate per PR.
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

### 9.1 Gate (end of every stage)

1. Owner runs the node(s), fills `STAGE.md` → *Review summary* (what was done, the
   decision, key numbers **with file references**, deviations, limitations, open
   questions) and sets `READY_FOR_REVIEW`.
2. Team checkpoint (short meeting or async): check logic and reasoning against
   `spec/pipeline_design.md`, the teacher/TA items mapped to this stage in
   `spec/sources.md`, and the stage's gate checklist.
3. Reviewer records `Accepted by <name>, <date>, commit <sha>` and sets `ACCEPTED`.
4. Downstream nodes start from ACCEPTED upstream outputs. (Prototyping earlier in
   `sandbox/` is fine; it is never evidence.)

### 9.2 Changing something after acceptance

1. Add an entry to `CHANGELOG.md`: what, why, which file(s), expected affected nodes.
2. Team (at least one other member) approves it in the PR.
3. Make the change; `run_pipeline.py run --from <earliest affected node>`.
4. Nodes whose decisions changed go `REOPENED` → re-review. Others stay ACCEPTED but
   with the new run_id.
5. Changes to `spec/` or `e5lib/factory.py` almost always require `--from s04` or earlier.

### 9.3 Special rule for confirmation (S09) and benchmark (S10)

Once S09 results have been looked at, any change to S03–S08 means the confirmation
window has been used for selection. Record this in `CHANGELOG.md` as a **reopened
selection** and say so in the report; do not keep claiming an untouched confirmation.
The M2 terminal benchmark is a historical benchmark, not a fresh test (see design §C,
Stage 2), and is scored once per release.

---

## 10. Stage index

Detailed requirements: [`spec/pipeline_design.md`](spec/pipeline_design.md). Each
node's `STAGE.md` repeats its purpose, outputs and gate criteria.

<!-- BEGIN STAGE INDEX from spec/stages.json -->
_Generated from `spec/stages.json` v0.1-draft (pipeline_design.md 2026-10-13 (pre-freeze)). Do not edit by hand._

| Stage | Nodes | Depends on | Key outputs | Gate question |
| --- | --- | --- | --- | --- |
| s00_contract Contract | common | - | spec/protocol.yaml v1.0; task_contract.md | Are targets, populations, metrics, decision rules and budget frozen before any result? |
| s01_records Records | common | s00_contract | records.csv.gz; exclusions.csv; data_hashes.json | Are joins, grains, units, eligibility and leakage exclusions verified? |
| s02_partitions Partitions | regression, classification | s01_records | selection_folds.csv; confirmation_manifest.csv; benchmark_manifest.csv | Are windows chronological, customers purged, labels mature and both classes supported? |
| s03_eda EDA | regression, classification | s02_partitions | figures/*.png + sidecar json; candidate_rationale.csv; eda_summary.json | Does every planned change follow from an observed, selection-only finding? |
| s04_baselines Baselines | regression, classification | s02_partitions, s03_eda | metrics_long.csv; predictions.csv.gz; decision.json | Do simplest matched baselines exist on identical rows and folds? |
| s05_features Features | regression, classification | s04_baselines | metrics_long.csv; paired_deltas.csv; figures/ | Do expansions help with estimator and preprocessing fixed? |
| s06_interventions Interventions | regression, classification | s05_features | ablation.csv; metrics_long.csv; decision.json | Is each added complexity justified one change at a time? |
| s07_tuning Tuning | regression, classification | s06_interventions | grid_results.csv; predictions.csv.gz; selected_spec.json | Is the winner a complete pipeline, compared with dummy and simplest family? |
| s08_policy Policy | regression, classification | s07_tuning | learning_curve.csv + figures; calibration.csv; threshold_table.csv | Is the recipe (and probability/threshold policy) frozen before confirmation? |
| s09_confirmation Confirmation | regression, classification | s08_policy | metrics_long.csv; predictions.csv.gz; figures/ | Does the frozen method hold up without being changed? |
| s10_benchmark Benchmark | regression, classification | s09_confirmation | bundle/; metrics_long.csv; predictions.csv.gz | Is the confirmed recipe refitted unchanged and scored once? |
| s11_deployment Deployment | common | s10_benchmark | app/; parity.json; input_validation.json | Does the app load the same artifact and reproduce its predictions? |
| s12_package Package | common | s11_deployment | evidence/build/**; deliverables/ report & deck drafts that cite evidence IDs; report_number_check.json | Does every number in report, deck and app trace to one release? |
<!-- END STAGE INDEX -->

---

## 11. Getting started (after the kickoff meeting)

0. Freeze the design: edit `spec/pipeline_design.md` and `spec/stages.json`, run
   `tools/scaffold_stages.py`, set `stages.json` `version` to `1.0`, commit.
1. Fill roles in §4 and `owner`/`reviewer` in each `STAGE.md`.
2. Platform lead builds `e5lib/` skeleton, `run_pipeline.py`, `build_evidence.py`
   and the contract tests (this is "Stage −1": infrastructure, no modelling).
3. Team completes S00 together and freezes `spec/protocol.yaml` (v1.0).
4. Proceed stage by stage through the gates in §9. Start each teammate's agent with
   [`AGENT_INIT_PROMPT.md`](AGENT_INIT_PROMPT.md).

Open items for the kickoff:

- [ ] Team size and role assignment (§4).
- [ ] Milestone 2 TA comments: only Milestone 1 TA feedback is in the repo
      (`docs/milestone1_feedback_response.md`). Add the Milestone 2 TA comments to
      `spec/sources.md` §3 before S00 is accepted.
- [ ] Agree the decision rule wording (e.g. "complex model must beat its family
      baseline by > 1 fold-SD on the primary metric, else keep simpler").
- [ ] Confirm outputs-in-git policy (§6.3) and the 50 MB limit.
- [ ] Confirm each member has the Olist raw CSVs and the tutorials locally
      (`docs/` and `data/raw/` are not in git).

---

## 12. Migration to the working folders (only after full approval)

Experiment 5 is the staging area. Its results become the project's working version only
through one deliberate migration:

1. **Preconditions:** every node `ACCEPTED`; `run_pipeline.py check` passes; a release tag
   `e5-release-N` exists; the team has approved the whole experiment; the **experiment lead
   explicitly instructs** the migration. No agent starts it on its own initiative, and
   nobody migrates individual stages early.
2. **Migration plan first** (written into `CHANGELOG.md` and approved): a file-by-file map,
   e.g. `e5lib/` → `src/…`, stage `run.py` files → `src/…` or `pipelines/…`, release
   evidence → `artifacts/…`, S11 app → `deployment/`, `deliverables/` → `docs/reports/`,
   pinned requirements → root `requirements*.txt`, plus which Milestone 2 files are archived
   rather than overwritten.
3. **Migrate on a dedicated branch** (`e5/migration`), changing paths only — no logic,
   parameter or data change.
4. **Prove reproducibility in the working folder:** run the full pipeline from the migrated
   code on a clean checkout; every output hash (models excepted only if documented
   non-determinism) and every number in `evidence/build/numbers.json` must match release
   `e5-release-N`. Record the comparison as `migration_check.json`.
5. Merge only after that check passes. `experiments/experiment_5/` stays in the repo,
   frozen, as the record of how the evidence was produced.
