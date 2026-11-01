# Reproducing Milestone 3 (Experiment 5)

The full guide, including how to check the dashboard, is
[Appendix A of the root README](README.md#appendix-a-reproducing-milestone-3-experiment-5-and-checking-its-dashboard).
This card gives the commands only.

Milestone 3 lives entirely in [`experiments/experiment_5/`](experiments/experiment_5/) and reads only the raw
Olist tables in `data/raw/`. Earlier milestones' folders (`src/`, `artifacts/`, `notebooks/01`–`09`,
`docs/milestone2_*`) are not used by it. Its outputs are frozen evidence: rerun in a separate clone and do not
commit the rerun's outputs.

## Already done: the recorded reproduction

The team's rerun of release `e5-release-2` (2026-10-27) and its acceptance are in
[`experiments/experiment_5/reproduction/ACCEPTANCE.md`](experiments/experiment_5/reproduction/ACCEPTANCE.md)
(tag `e5-reproduced`). The `FAIL` verdict in its `reproduction_check.json` comes from the strict identical-files
rule; the 7 differing B10 files are float noise (at most 2.1e-14) and pass the tolerance rule, as recorded there.

## Rerun it yourself (any machine)

```bash
# 1. Clone (keep LF line endings, also on Windows)
git clone -c core.autocrlf=false https://github.com/wuqianzong/Team11_IT5006_Ecommerce_Analytics_AY2627Sem1.git
cd Team11_IT5006_Ecommerce_Analytics_AY2627Sem1

# 2. Experiment 5 environment (Python 3.13)
python3.13 -m venv experiments/experiment_5/.venv
experiments/experiment_5/.venv/bin/pip install -r experiments/experiment_5/requirements.txt

# 3. Rerun all 34 nodes at tag e5-reproduced in a separate worktree (../e5-reproduce-check), then check
experiments/experiment_5/.venv/bin/python scripts/reproduce_experiment5.py
```

On Windows the interpreter is `experiments\experiment_5\.venv\Scripts\python.exe`.

[`scripts/reproduce_experiment5.py`](scripts/reproduce_experiment5.py) reruns Pipeline A s01–s08 and Pipeline
B B2–B12 with the same commands as `experiments/experiment_5/reproduce.py run`, then runs two checks:

- **decision check** (`decision_check.json`): every model choice, hyperparameter, feature, transform,
  calibration, row count and alert threshold equals the release, and the frozen T1 models re-predict the stored
  test predictions within 1e-9. Expected: `PASS` on any machine.
- **file-by-file check** (`reproduction_check.json`, `reproduce.py compare --machine other`, rule CR-056).
  Expected: identical files on the reference Mac; on other machines `FAIL` on refitted scores and counts.

The held-out test (T1) is **not** rerun: the test cohort was read exactly once (tag `e5-T1-tested`). Its saved
predictions and model bundles stay as committed.

**Machine differences.** Experiment 5 is deterministic on one machine, but floating-point arithmetic differs
slightly across machines, and refitted scores move in the fourth decimal (largest in the unregularised
logistic regression). The team documented this on Windows on 2026-10-26 (CR-056), and a full Linux rerun on
2026-11-01 confirmed it: every decision equal; at the operating thresholds, validation alert counts within
1.8%. Two exact-match safeguards built for the reference Mac would stop `reproduce.py run` after s06 on another
machine; the script passes over those two only. Full explanation and sizes:
[README Appendix A.2.1](README.md#a21-machine-differences-what-to-expect-and-why).

The team's original procedure, for the reference Mac: in a fresh clone, `git checkout e5-reproduced`, then
`reproduce.py run` and `reproduce.py compare --machine reference` (use `e5-reproduced`, not `e5-release-2`:
`reproduce.py` was added after the release commit).

## Where to look

| What | Where |
| --- | --- |
| Walkthrough of every stage's results, no rerun | [`notebooks/10_milestone3_experiment5.ipynb`](notebooks/10_milestone3_experiment5.ipynb) |
| Protocol and rules | `experiments/experiment_5/README.md` |
| Decisions | `experiments/experiment_5/spec/blueprints/decision_log.md`, `experiments/experiment_5/pipeline_b/spec/decision_log_B.md` |
| Which runs are current | `experiments/experiment_5/pipeline_b/EVIDENCE.md` |
| Release record | `experiments/experiment_5/pipeline_b/release/e5-release-2.json` |
| Every number in the report and slides | `experiments/experiment_5/pipeline_b/evidence/registry_B.yaml`, built into `evidence/build/` |
| Dashboard | `experiments/experiment_5/pipeline_b/deliverables/dashboard/app/` (run with `streamlit run app.py` from the root) |
