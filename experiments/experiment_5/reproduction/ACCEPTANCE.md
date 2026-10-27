# Reproduction acceptance (CR-062)

- **Release:** `e5-release-2` (commit 1516800). Rerun on a clean clone of the tag on the reference machine
  (the experiment lead's Mac, Python 3.13.9), 2026-10-27, with `reproduce.py run`. All 34 nodes (A s01–s08,
  B B2–B12) exit 0. The log is `run_log.txt`.
- **Comparison:** `reproduce.py compare --machine reference` → `reproduction_check.json`. 622 of 629 output
  files are byte-identical, covering every A stage and B2–B9 and B12.
- **The 7 files that differ** are all in B10: `parity.json`, `drift_profile.json`, `router_check.json` for
  both tasks, and regression `top_routes_categories.csv`. B10's release run (20261027T044744Z and
  20261027T044819Z) was produced on Henry's Windows machine (Python 3.13.7). The differences are float noise
  of at most 2.1e-14 and the recorded interpreter version.
- **Decision (experiment lead, 2026-10-27):** those 7 files are judged by the CR-056 tolerance rule, because
  their release copy came from another machine. They pass: every number is within 1e-9, and no count or label
  differs. **Reproduction accepted**; tag `e5-reproduced`.
- **T1:** not rerun (single read, `e5-T1-tested`). Its saved predictions and bundles are as committed.
