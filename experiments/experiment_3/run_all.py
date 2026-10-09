#!/usr/bin/env python3
"""Experiment 3: Master End-to-End Execution & Reproduction Runner.

Executes all 6 phases of Experiment 3 sequentially:
  Phase 1: Distribution Tail Audit & Outlier Treatment (run_eda_outliers.py)
  Phase 2: Multicollinearity Diagnostics & Feature Reduction (run_collinearity_reduction.py)
  Phase 3: Base-to-Complex Hierarchy & Task Expansion (run_feature_expansion_importance.py)
  Phase 4: Transforms & GridSearchCV Tuning (run_phase4_transforms_and_tuning.py)
  Phase 5: Probability Calibration & Cost Curves (run_phase5_threshold_calibration.py)
  Phase 6: Final Master Synthesis & Unified Benchmark (run_phase6_final_synthesis.py)

Usage:
  python experiments/experiment_3/run_all.py
"""

import sys
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXP3_DIR = REPO_ROOT / "experiments" / "experiment_3"

PHASES = [
    ("Phase 1: Tail Audit & Outlier Ablation", EXP3_DIR / "run_eda_outliers.py"),
    ("Phase 2: Multicollinearity Audit & Feature Reduction", EXP3_DIR / "run_collinearity_reduction.py"),
    ("Phase 3: Base-to-Complex Hierarchy & Feature Expansion", EXP3_DIR / "run_feature_expansion_importance.py"),
    ("Phase 4: Transforms & GridSearchCV Model Tuning", EXP3_DIR / "run_phase4_transforms_and_tuning.py"),
    ("Phase 5: Probability Calibration & Cost-Curve Optimization", EXP3_DIR / "run_phase5_threshold_calibration.py"),
    ("Phase 6: Final Master Synthesis & Unified Benchmark", EXP3_DIR / "run_phase6_final_synthesis.py")
]


def main():
    print("=" * 80)
    print("EXPERIMENT 3: MASTER END-TO-END REPRODUCTION SUITE")
    print("NUS IT5006 AY2026/2027 Semester 1 — Team 11")
    print("=" * 80)

    start_total = time.time()

    for idx, (name, script_path) in enumerate(PHASES, 1):
        print("\n" + "#" * 80)
        print(f"STARTING [{idx}/6]: {name}")
        print(f"Script: {script_path.relative_to(REPO_ROOT)}")
        print("#" * 80 + "\n")

        phase_start = time.time()
        res = subprocess.run([sys.executable, str(script_path)], cwd=str(REPO_ROOT))

        if res.returncode != 0:
            print(f"\n[ERROR] {name} failed with return code {res.returncode}!")
            sys.exit(res.returncode)

        elapsed = time.time() - phase_start
        print(f"\n[SUCCESS] Completed {name} in {elapsed:.1f} seconds.")

    total_elapsed = time.time() - start_total
    print("\n" + "=" * 80)
    print(f"ALL 6 PHASES OF EXPERIMENT 3 COMPLETED SUCCESSFULLY IN {total_elapsed / 60.0:.1f} MINUTES!")
    print("All metric tables and visual diagnostic figures are generated under:")
    print("  artifacts/metrics/experiment-3/")
    print("=" * 80)


if __name__ == "__main__":
    main()
