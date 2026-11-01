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

## Rerun it yourself

```bash
# 1. A fresh clone at the reproduced release (keep LF line endings, also on Windows)
git clone -c core.autocrlf=false https://github.com/wuqianzong/Team11_IT5006_Ecommerce_Analytics_AY2627Sem1.git e5-check
cd e5-check
git checkout e5-reproduced      # not e5-release-2: reproduce.py was added after the release commit

# 2. Environment (Python 3.13)
python3.13 -m venv experiments/experiment_5/.venv
experiments/experiment_5/.venv/bin/pip install -r experiments/experiment_5/requirements.txt

# 3. Rerun Pipeline A s01-s08 and Pipeline B B2-B12 from data/raw (about 25 minutes)
experiments/experiment_5/.venv/bin/python experiments/experiment_5/reproduce.py run

# 4. Compare every output with the release (writes experiments/experiment_5/reproduction/reproduction_check.json)
experiments/experiment_5/.venv/bin/python experiments/experiment_5/reproduce.py compare --machine other
```

On Windows the interpreter is `experiments\experiment_5\.venv\Scripts\python.exe`.

The held-out test (T1) is **not** rerun: the test cohort was read exactly once (tag `e5-T1-tested`). Its saved
predictions and model bundles stay as committed, and B10's parity check re-predicts them without labels.

On a machine other than the team's reference machine, numbers are judged by tolerance (CR-056): predictions
within 1e-9, refitted scores within 2e-3, counts and labels equal. Model pickles and PNGs are reported but not
judged.

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
