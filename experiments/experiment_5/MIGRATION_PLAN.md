# Migration plan — Experiment 5 into the working folders (README §12 step 2; CR-059)

**Status: PROPOSED, for the experiment lead's approval. Nothing here has been done.** No file outside
`experiments/experiment_5/` is written until the lead approves this plan and explicitly orders the
migration (§12 step 1). The migration runs on branch `e5/migration`, cut from `milestone-3` at release
`e5-release-1` (2f2e3c1; record `pipeline_b/release/e5-release-1.json`), and changes paths only (§12
step 3), with the one exception listed in §3. Reproduction (§12 step 4) is a separate step and is not
part of this plan's execution.

## 1. Preconditions (§12 step 1, CR-058)

| Precondition | State |
| --- | --- |
| Every node ACCEPTED or replaced under G-79 | A s01–s07 ACCEPTED; A s08 gate part ACCEPTED at e5-A-frozen, 8.6–8.8 replaced by T1; A s09 by B9; A s10 by B10; B2–B10 accepted (EVIDENCE.md) |
| A's check passes; B passes its own checks and tests | yes, with the recorded pipeline\_b/ guard finding (CR-058); release record checks 1–3 |
| Release tag exists, cut before migration | `e5-release-1` on 2f2e3c1 (local until pushed) |
| Team approved the whole experiment | B9 conclusion confirmed by Henry and the lead (2026-10-25); B10 round 3 accepted by the lead (2026-10-27) |
| Lead explicitly orders the migration | **open** |

## 2. File-by-file map

Source paths are relative to `experiments/experiment_5/`; targets to the repository root.

| Source | Target | Note |
| --- | --- | --- |
| `e5lib/` | `src/e5lib/` | A's foundation, imported read-only by B |
| `pipeline_b/e5b/` | `src/e5b/` | B's package (population, history features, stage runners, router `serving.py`) |
| `stages/sNN_*/<task>/run.py` | `pipelines/a/sNN_<name>/<task>/run.py` | A's stage runners (code only) |
| `run_pipeline.py`, `pipeline_b/b_run.py` | `pipelines/run_pipeline.py`, `pipelines/b_run.py` | orchestrators |
| `spec/protocol.yaml`, `spec/*.yaml` | `config/` | frozen contracts read by the code |
| `spec/` (Markdown), `pipeline_b/spec/` (blueprints, decision logs, team-doc mirror) | `docs/experiment5/spec/`, `docs/experiment5/pipeline_b_spec/` | design record, read-only |
| Current stage outputs at the release (A: `stages/*/*/outputs/`; B: `pipeline_b/stages/*/*/outputs/`) | `artifacts/e5-release-1/{A,B}/<stage>/<task>/outputs/` | release evidence, byte-for-byte copies; the run IDs are those in the release record |
| T1 bundles `pipeline_b/stages/t1_joint_test/<task>/outputs/bundles/{A,B}/` | `artifacts/models/e5-release-1/<task>/{A,B}/` | B serves inside its scope, A outside (B-G-06) |
| `evidence/`, `pipeline_b/evidence/` (registry, build) | `artifacts/e5-release-1/evidence/` | number registers for report and deck |
| `pipeline_b/deliverables/` (report and deck sources, audit and its inputs) | `docs/reports/milestone3/` | report and deck sources; the live report doc and deck stay where they are |
| B10 app sources (`pipeline_b/stages/b10/*/outputs/app_sources.json`, `serving_config.json`, `input_validation.json`, `drift_profile.json`) | read by the new app in `deployment/` | the app itself is built after the migration (it reads only these files and the bundles; A's s10 10.5 rule) |
| `tests/`, `pipeline_b/tests/` | `tests/e5/a/`, `tests/e5/b/` | |
| `requirements.txt` | root `requirements.txt` | the Milestone 2 root file moves to `archive/milestone2/requirements.txt` (a pinned copy also exists as `requirements-milestone2.txt`) |
| (new) | `REPRODUCE.md` at the root | how to rerun from a clean checkout; the CR-056 tolerance rule; T1 handling (M-3) |

**Archived, not overwritten** (moved under `archive/milestone2/`, git history kept): `src/reporting/`,
`src/features/`, `src/models/`, `src/common/`, root `app.py`, `deployment/` (the Milestone 2 app).
**Left as they are:** `data/` (Experiment 5 reads `data/raw` in place), `notebooks/`, `docs/milestone2_*`,
the Milestone 2 `artifacts/` folders, `experiments/` (Experiment 5 stays in the repo, frozen, §12 step 5).

## 3. Allowed changes on `e5/migration`

- Path constants only: `e5lib/paths.py` (`E5`, `REPO`), `pipeline_b/e5b/env.py`, the import roots of the
  orchestrators and tests.
- One non-path change, decided in CR-058: every `read_text` / `write_text` names `encoding="utf-8"`
  (and `newline="\n"` on write), so the migrated code passes A's text-IO guard. It does not change any
  output on the reference machine; the reproduction (step 4) confirms that.
- Nothing else: no logic, parameter, threshold, model or data change. A code diff on the branch other
  than the two kinds above blocks the merge.

## 4. Decisions for the lead (before execution)

| ID | Question | Recommendation |
| --- | --- | --- |
| M-1 | Package layout: `src/e5lib/` and `src/e5b/` beside the archived Milestone 2 packages, or one package `src/e5/` | `src/e5lib/` and `src/e5b/` (same import names as now, so the diff stays paths-only) |
| M-2 | Milestone 2 `src/` and `deployment/`: archive (move) or keep side by side | archive under `archive/milestone2/`, as §12 step 2 asks |
| M-3 | T1 in the reproduction (step 4): T1 was read once and is never rerun (joint\_test.md §1). Proposed: the reproduction reruns every stage except T1's test read; T1's saved predictions and bundles are copied, and B-G-08 parity (re-predict without labels) proves the bundles reproduce them | as proposed; recorded as a CR before step 4 |
| M-4 | Who runs it | the lead's machine (reference machine, CR-056) |
| M-5 | App location | `deployment/app.py` reading `artifacts/e5-release-1/` only |

## 5. After approval

1. The lead orders the migration (§12 step 1); push `e5-release-1`.
2. Cut `e5/migration` from `milestone-3` at the release; copy per §2; adjust paths per §3; one commit
   per row group, each listing its source → target.
3. Stop there: reproduction (§12 step 4) starts only when the lead orders it.
