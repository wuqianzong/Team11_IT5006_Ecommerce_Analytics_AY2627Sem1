"""SmartCommerce — deployment launcher for the Milestone 3 dashboard.

The final dashboard lives in
experiments/experiment_5/pipeline_b/deliverables/dashboard/app/app.py and reads
its frozen model bundles and stored outputs relative to that location, so it is
run in place rather than copied here. This launcher puts the dashboard folder
on the import path (for its ``dashboard_core`` package) and runs it.

The Milestone 1 dashboard that used to be this file is kept as
deployment/app_milestone1.py.
"""
from pathlib import Path
import runpy
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = (
    REPO_ROOT / "experiments" / "experiment_5" / "pipeline_b" / "deliverables" / "dashboard" / "app"
)
TARGET_APP = DASHBOARD_DIR / "app.py"

if str(DASHBOARD_DIR) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_DIR))

runpy.run_path(str(TARGET_APP), run_name="__main__")
