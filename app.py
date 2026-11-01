"""SmartCommerce — Root Streamlit Application Launcher.

Delegates to deployment/app.py, which runs the Milestone 3 dashboard in
experiments/experiment_5/pipeline_b/deliverables/dashboard/app/app.py.
Either `streamlit run app.py` or `streamlit run deployment/app.py` opens it.
"""
from pathlib import Path
import runpy

TARGET_APP = Path(__file__).resolve().parent / "deployment" / "app.py"

runpy.run_path(str(TARGET_APP), run_name="__main__")
