# Reproducing Milestone 3 (Experiment 5)

Milestone 3 lives entirely in [`experiments/experiment_5/`](experiments/experiment_5/): code, specification,
stage outputs, models, evidence registers, report and deck sources. It reads only the raw Olist tables in
`data/raw/`. Earlier milestones' folders (`src/`, `deployment/`, `artifacts/`, `notebooks/01`–`09`,
`docs/milestone2_*`) are not used by it.

- **Pipeline A** (`experiments/experiment_5/stages/`): all states, prediction at checkout.
- **Pipeline B** (`experiments/experiment_5/pipeline_b/`): seven states, seller and route history,
  classification at carrier handover. B reuses A's frozen code read-only.
- **Walkthrough:** [`notebooks/10_milestone3_experiment5.ipynb`](notebooks/10_milestone3_experiment5.ipynb)
  shows every stage's results from the stored outputs and can trigger the rerun.

## 1. Environment (Python 3.13)

```bash
python3 -m venv experiments/experiment_5/.venv
experiments/experiment_5/.venv/bin/pip install -r experiments/experiment_5/requirements.txt
```

On Windows the interpreter is `experiments\experiment_5\.venv\Scripts\python.exe`. To open the notebook, also
install Jupyter into the same environment (`pip install jupyter`). Jupyter is not part of the pinned set and
does not affect any result.

## 2. Rerun from a clean checkout of the release

```bash
git checkout e5-release-2
experiments/experiment_5/.venv/bin/python experiments/experiment_5/reproduce.py run
```

This reruns Pipeline A's stages s01–s08 and Pipeline B's B2–B12 in order, from the raw data. It takes about
25 minutes; the log is `experiments/experiment_5/reproduction/run_log.txt`.

The held-out test (T1) is **not** rerun. The test cohort was read exactly once (tag `e5-T1-tested`); rereading
it would make the test a selection step. Its saved predictions and model bundles stay as committed, and B10's
parity check re-predicts them from the bundles without labels.

## 3. Compare with the release

```bash
experiments/experiment_5/.venv/bin/python experiments/experiment_5/reproduce.py compare --machine other
```

This writes `experiments/experiment_5/reproduction/reproduction_check.json`, which compares every output file
with the hash recorded at the release.

- **The team's reference machine** used `--machine reference`, which requires identical files.
- **Any other machine** is judged by tolerance, because floating-point results differ slightly across operating
  systems and maths libraries (CR-056):
  - predictions within 1e-9;
  - refitted scores within 2e-3;
  - counts and labels equal.

## 4. Where to look

| What | Where |
| --- | --- |
| Protocol and rules | `experiments/experiment_5/README.md` |
| Decisions | `experiments/experiment_5/spec/blueprints/decision_log.md`, `experiments/experiment_5/pipeline_b/spec/decision_log_B.md` |
| Which runs are current | `experiments/experiment_5/pipeline_b/EVIDENCE.md` |
| Release record | `experiments/experiment_5/pipeline_b/release/e5-release-2.json` |
| Every number in the report and slides | `experiments/experiment_5/pipeline_b/evidence/registry_B.yaml`, built into `evidence/build/` |
